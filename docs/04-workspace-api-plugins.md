# 04 · Research Workspace, API und Plugins

[Zur Übersicht](../README.md)

## 1. Node-basierter Workspace

**Kontextfestlegung:** Quellen, Filter, Resampling, mathematische Transformationen, statistische Methoden und Visualisierungen werden visuell verbunden. Das Frontend beschreibt die Berechnung, das Backend führt sie aus.

**Vorschlag:** Die Berechnung bildet einen gerichteten azyklischen Graphen (DAG). Ein Node enthält stabile ID, Node-Typ, Plugin-Version, deklarierte Parameter und Eingangs-/Ausgangsports. Kanten verbinden benannte Ports; Layout, Farben und Zoom sind getrennte Präsentationsdaten.

Beispiel für zwei Pilot-Zeitreihen:

```text
Binance BTC/USDT ─→ Renditen ─┐
                             ├─→ Alignment ─→ Lead-Lag ─→ Ergebnis-Chart
Kraken BTC/USD ───→ Renditen ─┘
              FX-/Quote-Kontext und Verfügbarkeit explizit prüfen
```

Ähnliche Renditen können bei unterschiedlichen Quote-Assets verglichen werden; das beseitigt das Quote-Risiko nicht. Ein absoluter Preis-Spread erfordert eine zeitlich korrekte Umrechnung. Ein Lead-Lag-Befund aus Minutencandles belegt keine in Millisekunden ausführbare Arbitrage.

Porttypen umfassen beispielsweise `CandleFrame`, `TimeSeries`, `EventFrame`, `FeatureFrame`, `StatisticalResult` und `ChartSpec`. Zusätzlich zum Strukturtyp werden Zeitbasis, Einheit, Instrumentgruppe, Sortierung, Sampling, Verfügbarkeitspolicy und Qualitätsstatus geprüft. Eine Float-Spalte allein ist kein ausreichender fachlicher Typ.

Zweiter Graph für den MVP-Abnahmelauf:

```text
Makro-Veröffentlichungen (EventFrame) ─┐
                                      ├─→ Zeitliches Alignment ─→ Renditezusammenfassung ─→ Chart + Bericht
OHLCV → Renditen (TimeSeries) ──────────┘
```

Der Alignment-Node deklariert Richtung, maximales Datenalter, Zeitbasis und Verfügbarkeitspolicy. Marker nennen ihren Zeitbezug und die verwendete Revision. Eine Auswertung späterer Renditen verwendet diese als Ergebnisgrößen; als historische Features sind sie erst nach Ablauf und Verfügbarkeit des Renditefensters zulässig. Die Zusammenfassung weist Stichprobe, überlappende Fenster und Ausschlüsse aus. Weitergehende Event Studies berichten zusätzlich Unsicherheit. Ereignismarker zeigen zeitliche Zusammenhänge.

Für den AP01-Ereignisablauf bleibt der Anker die belegte Erstverfügbarkeit des fachlichen Ereignisses unter der gebundenen Policy. Eine spätere Ereignisrevision ändert nur die ab ihrem Cutoff sichtbaren Attribute, nicht diesen Anker oder die Anzahl unabhängiger Ereignisse. Die Fünf-Minuten-Rendite verlangt einen am Anker verfügbaren finalen Close exakt am Anker und einen finalen Close exakt bei Anker plus fünf Minuten. Ältere Baseline-Kandidaten werden mit Alter und Ausschlussgrund ausgewiesen; keine Auffüllung. Der Endkurs ist erst ab eigener Verfügbarkeit auswertbar. Gebundene Kursrevisionen werden nicht still überschrieben; korrigierte Kursauswertungen benötigen einen expliziten neuen Run. Siehe [AP01-Referenzfälle](08-ap01-contract.md#3-research-ablauf-b-ohlcv-und-veröffentlichungsereignisse).

Datenbrowser und Nodes verwenden Datentyp, fachlichen Bezug, Quelle und Zeitbereich. Analyseplugins deklarieren akzeptierte Eingangsmodalitäten. Für inkompatible Ports ist eine explizite, fachlich zulässige Transformation erforderlich.

## 2. Planung und Ausführung

1. Workspace-Version und angefragte Output-Nodes fixieren.
2. DAG auf Zyklen, fehlende Ports, unbekannte Plugins und Parameter prüfen.
3. Datenreferenzen auf konkrete Snapshots auflösen; keine wandernden „latest“-Referenzen während des Laufs.
4. Zeit- und Einheitenverträge validieren; Datenmenge und Kosten abschätzen.
5. Plan kanonisieren, Cache-Schlüssel bilden, benötigte Teilgraphen bestimmen.
6. Nodes in topologischer Reihenfolge mit begrenzter Parallelität ausführen.
7. Ergebnisartefakte und Manifest atomar veröffentlichen; UI über Status informieren.

Ein neuer Parameterstand erhält eine neue Graphrevision. Die UI zeigt Ergebnisse nur für die passende Revision an und markiert ältere Ergebnisse als veraltet. Unabhängige Teilgraphen können wiederverwendet werden. Ein Chart darf für die Darstellung Daten reduzieren; statistische Nodes bekommen die unveränderte, explizit gewählte Analyseeingabe.

## 3. Statistische Verträge

| Methode | Mindestvertrag |
|---|---|
| Deskriptive Statistik | Anzahl gültiger/fehlender Werte, Zeitraum, Einheiten, verwendete Ausschlüsse |
| Renditen | einfach oder logarithmisch, Preisfeld, Intervall, Behandlung von Lücken und nichtpositiven Preisen |
| Korrelation | Pearson/Spearman, Alignment, Mindeststichprobe, Pairwise/Listwise-Missing-Regel |
| Lead-Lag | Lag-Raster, Vorzeichen, Normalisierung, Überlappung je Lag, Unsicherheit und Zahl getesteter Kombinationen |
| Stationarität | Testtyp, Nullhypothese, Trend-/Konstantenwahl, Lag-/Bandbreitenwahl |
| Cointegration | Integrationsannahmen, Testvariante, Beziehung zu Stationarität, Stabilitätsprüfung |
| Regression | Ziel, Features, Training/Test, robuste Fehlerannahmen und Diagnose |
| Anomalien/Brüche | Fit-Zeitraum, Schwelle, Referenzregime, Alarmrate und zeitliche Evaluationsregel |

**AP01-Vertragsvorschlag für Lag-Konvention:** `corr(x[t], y[t+k])`; positives `k` bedeutet, dass x gegenüber y vorausläuft. Ein synthetischer Test mit bekanntem Shift fixiert diese Konvention. Die UI zeigt sie im Ergebnis, statt allein „Lag +5“ anzugeben.

Zeitreihen besitzen Autokorrelation und sich überlappende Beobachtungen. Einfache IID-p-Werte dürfen daher nicht als allgemeine Evidenz dargestellt werden. Vorgesehen sind passende Block-Bootstraps oder andere explizit begründete Unsicherheitsverfahren. Auswahl des „besten“ Lags zählt als Mehrfachsuche. Methoden, Parameter und Korrekturfamilien werden dokumentiert; explorative Ergebnisse bleiben entsprechend markiert.

## 4. API-Entwurf

**Vorschlag, nicht implementiert:** versionierte HTTP-/JSON-Steuerung unter `/api/v1`; große Tabellenergebnisse als begrenzte Batches oder Artefaktdownload. Arrow IPC/Parquet sind zu evaluierende Datenformate. Ein API-Schema wird später maschinenlesbar versioniert.

| Endpoint | Zweck |
|---|---|
| `GET /datasets` | paginierter Katalog mit Filtern für Quelle, Datenart, Entity/Instrument, Zeitraum, Qualität und Verfügbarkeit sowie Rechtehinweisen |
| `GET /datasets/{id}/snapshots` | verfügbare unveränderliche Stände |
| `POST /queries` | begrenzte Datenauswahl/Preview oder asynchroner Query-Job |
| `GET /plugins` | freigegebene Typen, Parameter- und Portschemata |
| `POST /workspaces` | Arbeitsfläche anlegen |
| `GET /workspaces/{id}` | aktuelle oder angeforderte Version lesen |
| `PUT /workspaces/{id}` | neue Version mit erwarteter Vorgängerversion speichern |
| `POST /runs` | Graphversion, Snapshots, Zeitpolicy und Outputs ausführen |
| `GET /runs/{id}` | Zustand, Fortschritt, Fehler und Artefaktverweise |
| `POST /runs/{id}/cancel` | idempotente Abbruchanforderung |
| `GET /artifacts/{id}` | Metadaten und erlaubten Download beziehen |

Beispiel eines schematischen Auftrags:

```json
{
  "workspace_id": "example-workspace",
  "workspace_version": 3,
  "snapshot_ids": ["example-binance", "example-kraken"],
  "outputs": ["lead_lag_result"],
  "temporal_policy": {"mode": "historical_market", "policy_id": "estimated-v1"},
  "resource_profile": "interactive"
}
```

`POST /runs` liefert `202` mit `run_id` und Status-URL. Beispiele sind Zielverträge; die konkreten Objektformen werden in AP 01/04 abgestimmt. Für Wiederholungen wird ein Idempotency-Key vorgeschlagen: gleicher Key und gleicher Payload liefern denselben Auftrag; anderer Payload unter gleichem Key führt zu Konflikt.

Jobzustände: `queued → validating → running → succeeded | failed | cancelled`; ein aktiver Abbruch darf über `cancelling` führen. Ein Cachetreffer ist ein erfolgreicher Run mit `cache_hit=true` und Referenz auf das geprüfte Artefakt. Versuchszustände werden getrennt vom fachlichen Run gespeichert.

Fehler enthalten stabilen Code, verständliche Nachricht, Request-ID, Retry-Eignung und begrenzte Details. Beispiele: `INVALID_GRAPH`, `UNKNOWN_AVAILABILITY`, `SNAPSHOT_NOT_FOUND`, `RESOURCE_LIMIT`, `PLUGIN_FAILURE`, `VERSION_CONFLICT`. HTTP-Status unterscheiden Validierung, Konflikt, Berechtigung, Quoten und interne Fehler. Keine Stacktraces oder Zugangsdaten an den Browser.

Pagination benötigt stabile Sortierung und Cursor; Zeitfilter sind `[start,end)`. Optimistic Locking verhindert verlorene Workspace-Änderungen. Der Client darf keine Serverdateipfade oder beliebige SQL-Fragmente vorgeben. SSE oder WebSocket für Fortschritt ist eine spätere Option; Polling reicht zunächst.

## 5. Plugin-Konzept

Zwei Vertragstypen:

- **Connector:** deklariert Datenarten, Quellrechte, Authentifizierungsbedarf, Rate-Limits, Cursor-/Replay-Fähigkeit, Zeitsemantik und Normalizer-Schema. Die Metadaten enthalten `data_kinds`, Schemaversionen sowie Zeit-, Revisions- und Abruffähigkeiten gemäß [Architektur](02-architecture.md). Historischer Abruf und Live-Aufnahme sind separat deklarierbar.
- **Analyse:** deklariert Plugin-ID, API-Version, Implementierungsversion, Port- und Parameterschemata, Einheiten-/Zeitbedingungen, deterministisches Verhalten, benötigte Ressourcen und Ausgabetypen.

Schematische Analyseschnittstelle:

```python
class AnalysisPlugin:
    def validate(self, input_metadata, parameters): ...
    def estimate_cost(self, input_metadata, parameters): ...
    def execute(self, inputs, parameters, context): ...
```

`context` stellt aufgelöste Snapshots, Seed, Zeitpolicy, Ressourcenbudget, Logger und Abbruchsignal bereit. Ein Analyseplugin darf diese Inputs nicht durch unversionierte spontane Netzwerkabrufe ergänzen. Ein Connector besitzt einen gesonderten Abrufkontext mit Secret-Referenzen; Secrets werden nie im Workspace serialisiert.

Vertragskonforme Connectoren und Analyseplugins werden über die Registry eingebunden. Die Ausführung verwendet die deklarierten Schnittstellen und benötigt dafür keine providerspezifischen Verzweigungen im zentralen Executor.

Parameter verwenden deklarative Schemas mit Defaults, Grenzen, Enum-Werten und verständlichen Labels. Dadurch kann die UI Standardformulare für neue Methoden erzeugen. Neue Spezialvisualisierungen können zusätzliche Frontend-Arbeit benötigen; „Plugin“ garantiert keine beliebige UI-Erweiterung ohne Codeänderung.

**Vertrauensmodell:** MVP lädt nur geprüfte, lokal installierte Plugins aus einer Allowlist. Ein separater Worker-Prozess ist keine Sicherheitsisolation gegen bösartigen Code. Fremde Plugins erfordern Container-/Berechtigungsisolation, Netzwerk- und Dateisystemregeln sowie einen signierten oder anderweitig geprüften Distributionsweg. Ein offener Plugin-Marktplatz ist kein MVP-Ziel.

Eine Allowlist-Freigabe bindet das Tupel aus Plugin-ID, Implementierungsversion und unveränderlichem Code-/Paketnachweis (beispielsweise Inhaltsdigest des ausführbaren Pakets). Die tatsächlich geladenen Inhalte müssen diesem geprüften Nachweis entsprechen; eine Versionszeichenfolge oder ein veränderlicher Installationspfad reicht nicht. Änderungen an Code/Paket oder Version erfordern erneute Prüfung und eine neue Freigabe. Registry, Run-Manifest und Cacheidentität binden dieses Tupel; Environment-/Dependency-Nachweise bleiben zusätzlich erforderlich.

Fehlt für einen alten Run genau die gebundene Version mit passendem Nachweis oder ihre gültige Freigabe, scheitert die angeforderte Ausführung ausdrücklich vor dem Laden des Plugins. Gleichnamige, neuere oder unter gleicher Versionsnummer veränderte Pakete sind kein Ersatz. Bereits archivierte Ergebnisse dürfen mit Herkunft gelesen werden, gelten aber nicht als erneute Ausführung. Ein ausdrücklich gewähltes Upgrade erzeugt einen neuen Run und erhält die Bindungen des alten Runs.

Plugin-API und Implementierung sind separat versioniert. Breaking Changes benötigen neue Hauptversion und Migration; alte Runs benötigen weiterhin ein ausführbares Environment oder einen ausdrücklich dokumentierten Reproduzierbarkeitsverlust. Veraltete Versionen dürfen nicht still gegen neue ausgetauscht werden.

## 6. Run-Manifest und Cache

Ein erfolgreicher Run speichert mindestens:

- Run-ID, Workspace- und Graphversion, kanonische Parameter und ausgewählte Outputs.
- Snapshot-/Dateihashes, Qualitätsbericht, Zeitpolicy, Einheiten- und Instrument-Mapping-Version.
- Code-Commit, Plugin-Versionen, Dependency-Lock/Environment-ID, relevante Engine-Einstellungen.
- Seed, Laufzeit, Ressourcenprofil, Warnungen, Ausschlüsse, Artefakthashes und Ausgabeschema.
- Start-/Endzeit, Nutzer-/Projektkontext sofern vorhanden, Hardware-/Plattformklasse für numerische Vergleichbarkeit.

Ein Cache-Key umfasst semantischen Teilgraphen, Daten-/Schema-/Mappingversionen, Plugin und Code, Parameter, Zeitpolicy, Seed und relevante Engine-Konfiguration. Ein neuer Import oder eine geänderte Verfügbarkeitsannahme darf keinen alten Treffer wiederverwenden. Cache ist löschbar; archivierte Forschungsergebnisse sind unabhängig davon aufzubewahren.

Deterministische Ergebnisse sollen identisch oder innerhalb ausgewiesener numerischer Toleranzen reproduzierbar sein. Parallelreduktionen und native Bibliotheken können Rundungsunterschiede erzeugen; ein Hash allein ist kein allgemeiner Nachweis numerischer Äquivalenz.

## 7. AP01-Konkretisierung

Der [AP01-Vertrag](08-ap01-contract.md) konkretisiert beide Research-Abläufe, Schnittstellen, Modulgrenzen, numerische Toleranzen und die Übergabe. Technische ADRs sind Vorschläge zur Abnahme. Softwaretests und Benchmarks werden erst in den nachfolgenden Arbeitspaketen ausgeführt.
