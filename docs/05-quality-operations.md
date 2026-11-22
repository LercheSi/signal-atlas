# 05 · Qualität, Performance und Betrieb

[Zur Übersicht](../README.md)

## 1. Durchgängige Qualitätssicherung

Qualität ist Bestandteil jedes Arbeitspakets. Import, Zeitverträge, Statistik und Wiederherstellung werden vor Funktionsausbau abgesichert. Ein Chart, der plausibel aussieht, ist kein Korrektheitsnachweis.

| Ebene | Prüfungen | Fehlerwirkung |
|---|---|---|
| Datenvertrag | Schema, Einheit, Schlüssel, Präzision, Intervall | Quarantäne oder explizit markierter Teilimport |
| Datenbestand | Lücken, Duplikate, Revisionen, Plausibilität | Bericht statt stiller Bereinigung |
| Zeitsemantik | Candle-Abschluss, Releases, Revisionen, Altersgrenzen | Strikter Lauf stoppt bei Vertragsverletzung |
| Statistik | synthetische Referenzen, bekannte Nullfälle, Lag-Vorzeichen | Fehlerhafte Module nicht freigeben |
| API/Workspace | Validierung, Versionen, Idempotenz, veraltete Ergebnisse | Kein erfolgreicher Lauf mit unklarer Eingabe |
| Betrieb | Crash-Recovery, Backup, Abbruch, Quoten | Keine halbfertigen Artefakte veröffentlichen |

## 2. Teststrategie

**Unit- und Property-Tests:** OHLC-Invarianten, UTC-/Epoch-Konvertierung, Join-Gruppierung, Lückenregeln, Einheiten, Revisionstiefe und kanonische Parameter. Importieren derselben unveränderten Daten ist idempotent. Verschiedene Chunk-Grenzen ergeben dieselbe fachliche Ausgabe.

**Integrationsprüfungen:** Raw → Normalized → Manifest → Query → Plugin → Artefakt; API plus PostgreSQL; Workspace speichern und laden; Jobclaim/Lease; Cache-Invaliderung bei Daten- oder Codeänderung. Ein Crash zwischen Dateischreiben und Katalog-Commit darf keinen halben Snapshot lesbar machen.

**Connector-Vertragstests:** Eine gemeinsame Testsuite prüft deklarierte Fähigkeiten, Schemata, Herkunft, Zeitsemantik und Wiederholung für Candle- und Event-Adapter. Unterschiedlich strukturierte Provider-Fixtures mit gleicher fachlicher Semantik ergeben äquivalente kanonische Werte; die jeweilige Herkunft bleibt erhalten. Ein Makroereignis durchläuft Raw → Normalized → Snapshot → Query → Workspace → Export mit Entity-Bezug ohne Instrument oder Venue. Fixtures mit weiteren Quell-IDs und Quote-Währungen decken fest codierte Annahmen im Kern auf. Für Candle-Instrumente werden Venue, Marktart, Base/Quote und Gültigkeitszeitraum geprüft.

**Zeitliche Regressionstests:**

1. Ein Fakt wird erst nach dem Analysezeitpunkt veröffentlicht: er darf nicht erscheinen.
2. Eine finale Candle darf vor `bar_end` nicht bekannt sein.
3. Eine Revision von morgen ändert das Ergebnis eines eingefrorenen gestrigen Laufs nicht.
4. Ein historischer Download mit unbekannter Verfügbarkeit scheitert im strikten Modus.
5. Ein Wert außerhalb der Staleness-Grenze bleibt fehlend, nicht unendlich fortgeschrieben.
6. Gleichzeitige, widersprüchliche Revisionen benötigen Tie-Breaker oder werden abgewiesen.
7. Verändert man ausschließlich Daten nach dem Cutoff, bleiben frühere Features unverändert.
8. Ein rückwirkend erkanntes Entity-Label ist vor seiner Bekanntheit unsichtbar.
9. Geänderte Quell- und Instrumenten-Aliase beeinflussen eingefrorene Läufe erst bei einem expliziten Wechsel der Mapping-Version.
10. Geschätzte Veröffentlichungszeiten bleiben in Query, Workspace und Export als Annahmen gekennzeichnet.

**Frontend-End-to-End:** beide MVP-Abnahmeläufe einschließlich Ereignismarkern, Alignment und Cutoff-Prüfung, Fehlermeldungen, Abbruch, Reload, synchrone Zeitachsen und Schutz gegen verspätete Resultate. Tastaturbedienbarkeit, lesbare Kontraste und sichtbare Zeitzone sind UI-Qualitätsziele.

## 3. Forschungsqualität

Explorative Suche und bestätigende Auswertung werden getrennt protokolliert. Der Experiment Manager in AP 12 erweitert diese Nachweise, aber Suchhistorie und Parameter gehören bereits in MVP-Manifeste.

- Zeitlich getrennte Trainings-, Validierungs- und Testfenster; kein zufälliger Split als Standard für abhängige Zeitreihen.
- Walk-forward-Analysen; bei überlappenden Zielhorizonten Purging und zeitlicher Abstand gemäß Labelkonstruktion.
- Skalierer, Featureauswahl und Hyperparameter nur im Trainings-/Validierungsprozess fitten.
- Anzahl getesteter Assets, Lags, Fenster und Methoden erfassen. Korrektur für multiples Testen mit benannter Testfamilie und Annahmen; ein korrigierter p-Wert löst schlechte Datenauswahl nicht.
- Stabilität über Zeitregime, Quellen und Parameter prüfen; Negativkontrollen und geeignete Permutations-/Blocktests vorsehen.
- Survivorship Bias, Delistings, Quellabdeckung und nachträgliche Asset-Mappings prüfen.
- Effektgröße, Stichprobe, Konfidenz/Unsicherheit und fehlende Werte neben Signifikanz ausgeben.

Für AP 14 kommen Kosten, Spread, Slippage, Finanzierung, FX-/Stablecoin-Risiko, Latenz und Liquiditätsgrenzen hinzu. Historische Preisunterschiede allein belegen keine realisierbare Strategie. Ein nicht unangetastetes Testfenster wird als solches markiert; wiederholtes Nachoptimieren verbraucht dessen bestätigenden Wert.

## 4. Performanceplan

**Annahme:** Datenumfang, Hardware und Parallelität sind noch nicht gemessen. Folgende Zahlen sind vorgeschlagene Startbudgets für AP 04 und keine erreichten Werte oder SLA.

| Profil | Vorgeschlagenes Messziel |
|---|---|
| Katalog/Workspace auf Referenzbestand | p95 unter 300 ms serverseitig bei geringer lokaler Parallelität |
| Warmer Chart-Request | p95 unter 1 s für höchstens 10.000 dargestellte Punkte je Serie |
| Jobannahme | p95 unter 500 ms ohne eigentliche Berechnung |
| Interaktiver Beispielgraph | Ziel unter 3 s auf festgelegtem MVP-Ausschnitt; sonst asynchron |
| Große Scans | kein pauschales Latenzziel; Durchsatz, Peak-RAM und temporärer Speicher werden gemessen |

AP 02 definiert reale Größenklassen: kleiner Interaktionsausschnitt, repräsentativer Mehrjahresvergleich und großer Gesamtscan. Ein synthetischer Über-RAM-Test prüft Spill/Fehlerverhalten. Jeder Bericht erfasst CPU, RAM, Datenträger, Dateianzahl/-größe, Datenvolumen, Zeilen, Schema, Versionsstände, Parallelität und Cachezustand.

Candle-Scans, unregelmäßige Ereignisse, zeitliche Joins und Abfragen über viele Assets erhalten eigene Benchmarkprofile. Getrennt messen: Import MB/s und Zeilen/s, Speicherbedarf, Scan/Filter/Aggregation, As-of-Join, Resampling, Lead-Lag, Artefakttransfer und UI-Renderzeit. Kalte und warme Läufe getrennt berichten; p50/p95 nur aus ausreichend wiederholten Läufen ableiten. Ein Einzelwert ist kein Perzentil.

Optimierungsreihenfolge: Queryplan und Filter/Projektion → Dateilayout → vektorisierte/Lazy-Verarbeitung → geeignete Algorithmen → Cache/Voraggregation → native Beschleunigung oder zusätzliche Stores. Chart-Downsampling muss Extremwerte beziehungsweise Datenlücken nach klarer Regel erhalten und darf keine Statistik beeinflussen.

**Vorschlag für Performance-Regressionen:** Auf einem stabilen Benchmarkrunner Veränderungen über 20 % untersuchen, mit Streuung und mindestens einer Wiederholung vor Blockierung. Schwelle und Datensätze werden in AP 04 bestätigt. Shared-CI-Timing allein ist kein stabiler Hard-Gate.

## 5. Sicherheit und Betrieb

MVP-Bindung an Loopback/localhost gemäß ADR-0001. Öffentliche Erreichbarkeit erfordert vor Freigabe Authentifizierung, Autorisierung, TLS und Quoten. Dateizugriffe folgen erlaubten Dataset-IDs; Query-Parameter werden validiert, SQL-Werte gebunden. Unkontrollierte Pfadwahl, SQL-Ausführung und Plugin-Installation durch API-Nutzer sind ausgeschlossen.

API-Schlüssel liegen in einem Secret Store beziehungsweise einer lokalen, nicht versionierten Konfiguration; keine Trade-/Withdrawal-Rechte für reine Datenaufnahme. Logs und Raw-Captures dürfen keine Tokens enthalten. Netzwerkfehler, Limits und Sperrantworten führen zu begrenzten Retries mit Backoff und nachvollziehbarem Cursor, nicht zu unendlichen Schleifen.

Strukturierte Logs enthalten Request-, Run-, Batch- und Snapshot-IDs. Metriken: Importverzug, fehlerhafte Zeilen, Queuealter, aktive Jobs, Fehlerrate, Laufzeit, Peak-RAM, Disk-Füllstand und Cachetreffer. Eine Live-Verbindung ohne Datenfluss gilt nicht automatisch als gesund.

## 6. Backup, Wiederherstellung und Retention

Zu sichern sind Raw-Bestand, referenzierte Parquet-Dateien, Manifeste, PostgreSQL, Workspace-Exporte sowie Code und reproduzierbare Environments. Cache und temporäre Dateien sind getrennt und grundsätzlich rekonstruierbar.

Wiederherstellungsablauf: Dienste anhalten oder konsistenten Stand wählen → PostgreSQL und zugehörige Dateien zurückspielen → referenzierte Hashes/Existenz prüfen → Katalog freigeben → festgelegten Referenzrun wiederholen. PostgreSQL-Isolation allein schützt keine externe Dateisammlung; Transaktionssicht siehe [offizielle PostgreSQL-Dokumentation](https://www.postgresql.org/docs/current/sql-set-transaction.html).

**Offen D-11:** Backupintervall, Retention, RPO/RTO und zweiter Speicherort nach Bestandsgröße und Änderungsrate. Vor M1 muss wenigstens ein vollständiger Restore-Test mit dem Referenzbestand erfolgreich sein. Daten mit ungeklärten Weiterverteilungsrechten werden nicht in öffentliche Backups oder Git-Artefakte übernommen.

## 7. Gemeinsame Definition of Done

Ein Arbeitspaket ist abgeschlossen, wenn seine Akzeptanzkriterien nachgewiesen, Schnittstellen dokumentiert, relevante Korrektheits-/Fehlertests erfolgreich, Daten-/Lizenzannahmen benannt und nötige ADRs aktualisiert sind. Performanceaussagen enthalten Messumgebung und Grenzen. Unfertige Optionen erscheinen nicht als implementierte Features.

## 8. AP01-Konkretisierung

Der [AP01-Vertrag](08-ap01-contract.md) konkretisiert beide Research-Abläufe, Schnittstellen, Modulgrenzen, numerische Toleranzen und die Übergabe. Technische ADRs sind Vorschläge zur Abnahme. Softwaretests und Benchmarks werden erst in den nachfolgenden Arbeitspaketen ausgeführt.
