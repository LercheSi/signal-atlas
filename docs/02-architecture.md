# 02 · Systemarchitektur

[Zur Übersicht](../README.md)

## 1. Architekturprinzipien

**Kontextfestlegung:** Historische Forschung zuerst; modularer Ausbau zur Live-Plattform. Speicherung, Berechnung und Darstellung bleiben getrennt. Raw-Daten werden durch Normalisierung nicht ersetzt. Große Analysen laufen außerhalb des Browsers.

**Vorschlag:** Ein modularer Python-Backendkern mit getrennten Prozessen für API, Import und Analyse ist der Ausgangspunkt. Modulgrenzen werden zunächst als Bibliotheksverträge umgesetzt. Eigene Netzwerkdienste entstehen erst, wenn Betrieb, Ausfallschutz oder Last dies rechtfertigen.

```mermaid
flowchart LR
  S[Dateien und externe Quellen] --> I[Import / Connector]
  I --> R[Raw-Archiv]
  R --> N[Normalisierung und Qualität]
  N --> P[Parquet-Snapshots]
  N --> M[(PostgreSQL-Metadaten)]
  UI[React / TypeScript Workspace] --> API[Query- und Job-API]
  API --> M
  API --> W[Analyse-Worker]
  W --> P
  W --> D[DuckDB / Polars]
  D --> A[Ergebnisartefakte]
  A --> API
  API --> UI
```

Das Diagramm zeigt logische Datenflüsse, keine abgeschlossenen verteilten Transaktionen. Das Commit-Protokoll für Dateien und Metadaten ist unten definiert.

## 2. Komponenten und Zuständigkeit

| Komponente | Zuständigkeit | Grenze |
|---|---|---|
| Connector | Abruf, Quellcursor, Rohpayload, Empfangszeit | Keine ungeprüfte fachliche Bereinigung |
| Normalizer | Einheiten, Instrumente, Zeiten, Schema, Qualitätsflags | Keine versteckte Ersetzung fehlender Werte |
| Catalog | Datensätze, Instrumente, Rechte, Schemata, Snapshots | Keine Vollablage aller historischen Candles in Metadatentabellen |
| Query Service | autorisierte und begrenzte Datensicht, Projektion, Filter | Kein beliebiges SQL aus dem Browser |
| Graph Planner | Typprüfung, DAG, Ressourcenabschätzung, Ausführungsplan | Keine Ausführung unvalidierter Plugins |
| Worker | reproduzierbare Berechnung, Fortschritt, Abbruch | Kein blockierender Job im API-Prozess |
| Artifact Store | Ergebnisse, Manifeste und referenzierte Dateien | Unveränderliche Inhalte unter versionierten IDs |
| Workspace Service | Graphversionen, Layout, Parameter, Run-Verweise | Layout ist keine Datenversion |
| Frontend | Datenbrowser, Canvas, Charts, Fehler und Provenienz | Keine autoritative Statistik auf heruntergesampelten Charts |

## 3. Technologieeinsatz

Python steuert Import, Geschäftslogik und statistische Module. Polars übernimmt tabellarische Transformationen; DuckDB dient SQL-Abfragen über den historischen Bestand. Verantwortlichkeiten pro Pipeline werden explizit gewählt, statt Daten bei jedem Node zwischen beiden Engines zu kopieren.

Parquet ist das geplante spaltenorientierte Austausch- und Archivformat für normalisierte Massendaten. PostgreSQL verwaltet Katalog, Arbeitsflächen, Jobstatus und Entscheidungen; es ist nicht automatisch das primäre Archiv für sämtliche historischen Datenpunkte.

Für DuckDB/Polars sind zeitliche Joins dokumentiert; sie ersetzen keine projektseitige Verfügbarkeitsprüfung. Siehe [DuckDB As-of-Joins](https://duckdb.org/docs/stable/sql/query_syntax/from) und [Polars Joins](https://docs.pola.rs/user-guide/transformations/joins/). Polars bietet eine [Lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/); die tatsächliche Speicherwirkung jedes geplanten Operators wird benchmarkbasiert geprüft.

**Vorschläge, noch offen:** Python-Webframework, konkreter Prozess-/Job-Runner, Chartbibliothek und Canvasbibliothek. React/TypeScript ist die Frontend-Richtung aus der Beauftragung. Eine Node.js-Laufzeit kann für Frontend-Werkzeuge verwendet werden, ist aber keine Voraussetzung für die Forschungsengine.

## 4. Speicherlayout und Veröffentlichung

```text
signal-atlas/                 # vorgeschlagene spätere Repository-Struktur
  apps/web/
  packages/backend/
  plugins/
  tests/fixtures/
  docs/
  data/                       # extern konfigurierbar; nicht in Git
    raw/<source>/<ingest-batch>/
    normalized/<dataset>/<schema-version>/<partition>/
    derived/<analysis>/<run-id>/
    manifests/<snapshot-id>.json
  workspaces/                 # optionale exportierte Arbeitsflächen
```

Partitionierung wird anhand AP 02/04 festgelegt: wahrscheinlich Quelle, Datentyp und Zeitbereich; Instrument nur bei ausreichender Dateigröße. Eine Datei pro Instrument und Minute erzeugt unnötig viele kleine Dateien. Zielgrößen für Dateien und Row Groups sind Benchmarkparameter, keine pauschalen Garantien.

**Vorschlag: atomare Sichtbarkeit über Manifest-Commit.**

1. Import schreibt Dateien in einen isolierten Staging-Bereich.
2. Validator prüft Schema, Hash, Zeilenzahl, Zeitbereiche und Qualitätsbericht.
3. Writer veröffentlicht unveränderliche Dateien und ein Manifest; vorhandene Dateien werden nicht überschrieben.
4. PostgreSQL-Transaktion registriert den vollständigen Snapshot als `committed` und setzt bei Bedarf den Katalogzeiger.
5. Leser verwenden nur committed Manifeste. Verwaiste Staging-Dateien werden nach einer Schonfrist aufgeräumt.

Ein Dateisystem-Rename ist nur innerhalb seiner tatsächlichen atomaren Grenzen verwendbar; Objektablagen benötigen ein entsprechendes Commit-Verfahren. Eine PostgreSQL-Transaktion allein macht externe Dateien nicht atomar. Compaction erzeugt neue Snapshots; alte Runs behalten alte Dateireferenzen. Garbage Collection löscht nur unreferenzierte Daten außerhalb von Retention und Backup-Verpflichtungen.

## 5. Jobausführung und Parallelität

MVP-Vorschlag: PostgreSQL-basierte Jobtabelle mit transaktionalem Claim, Lease, Heartbeat und begrenzten Worker-Prozessen. Ein Prozessabsturz lässt die Lease auslaufen; ein Wiederholungsversuch erhält eine neue Attempt-ID. Kein Exactly-once-Versprechen: Ergebnisveröffentlichung und externe Effekte müssen idempotent sein. Der konkrete Runner ist D-04.

API-Prozesse nehmen Aufträge an und beantworten Statusabfragen. Analyse-Worker erhalten CPU-, RAM-, Laufzeit- und temporäre Speicherbudgets. Parallelität der Worker und Threads pro Engine werden gemeinsam begrenzt, damit mehrere DuckDB-/Polars-Jobs nicht alle Kerne und den Speicher mehrfach belegen.

Interaktive Aufträge bekommen eine getrennte, begrenzte Kapazität. Große Scans laufen als Hintergrundjobs; Abbruchsignale gelten zwischen Operatorschritten und bei unterstützten Engine-Abbrüchen. Ein nicht abbrechbarer Prozess wird nach einer Frist beendet, ohne halbe Ergebnisse als erfolgreich zu markieren.

## 6. Live-Ausbau

```text
Quelle → persistente Aufnahme → Normalisierung → Live-Projektion / Benachrichtigung
                                      └──────→ gebündelter Historical Writer
```

Ein Live-Ereignis wird erst nach dauerhafter Aufnahme bestätigt. Replay und mindestens einmalige Zustellung werden als Normalfall behandelt. Schlüssel, Cursor und Sequenznummern ermöglichen Deduplikation und Wiederaufnahme. Orderbücher benötigen Snapshot plus geordnete Deltas; Sequenzlücken machen den Zustand ungültig bis zum Neuaufbau.

Späte Ereignisse und Korrekturen erzeugen neue Revisionen. Watermarks kennzeichnen erwartete Vollständigkeit, nicht absolute Fehlerfreiheit. Der Übergang zwischen Live-Sicht und historischem Snapshot erfolgt über einen expliziten Cutover-Cursor; nachgelagerte Leser deduplizieren die Überlappungszone.

**Optionen:** NATS JetStream als persistenter Ereignisstrom, TimescaleDB für operative Zeitreihen, ClickHouse bei nachgewiesener Tick-/Orderbuchlast. Keine dieser Optionen ist eine MVP-Abhängigkeit. Auswahl erst mit Lastprofil, Betriebsaufwand und Wiederherstellungstest.

## 7. Native Beschleunigung und Deployment

Rust/C++ sind optionale Beschleuniger nach Profiling. Vorher: Filter früh anwenden, unnötige Kopien entfernen, Algorithmen verbessern, geeignete Partitionierung und Caching prüfen. Native Module bekommen denselben fachlichen Vertrag wie Python-Referenzen, Tests gegen Referenzergebnisse und dokumentierte Build-/ABI-Unterstützung.

**Annahme:** Lokales Deployment mit Weboberfläche, API, PostgreSQL und wenigen Workern. Vorgeschlagen ist ein späteres Compose-Profil; Containerdateien existieren in diesem Dokumentationspaket nicht. Öffentliches Hosting erfordert Authentifizierung, TLS, Rollen, Quoten und ein separates Betriebsmodell. Kubernetes und verteilte Ausführung sind offen und für v0.1 nicht vorgesehen.
