# 08 · AP01-Vertrag und Übergabe

[Zur Übersicht](../README.md)

## 1. Status und Zuständigkeiten

Stand: 22. November 2026. Dieser Vertrag konkretisiert AP01; er beschreibt keine implementierten Funktionen. Lokalbetrieb für eine Person wurde im Projektgespräch bestätigt. Die folgenden technischen Festlegungen sind der zur Prüfung vorgelegte AP01-Entwurf; die ADRs kennzeichnen sie als `proposed`.

Die Rollen Produkt, Research, Daten, Architektur und Betrieb sind Verantwortungsbereiche, keine behaupteten Personalzuweisungen. Die namentliche Besetzung bleibt vor Beginn von AP02/03 offen. AP01 ist bis zu dieser Zuordnung und der Annahme der vorgeschlagenen ADRs sowie der ausdrücklichen D-08-Entscheidung **zur Abnahme vorbereitet**, nicht abgeschlossen.

## 2. Research-Ablauf A: OHLCV-Vergleich und Lead-Lag

**Frage:** Laufen Renditebewegungen auf Markt A denen auf Markt B voraus?

**Eingaben:** Zwei finalisierte Spot-Candle-Reihen des gleichen Basisassets aus getrennten Pilotadaptern, feste Snapshot- und Mapping-Versionen, Qualitätsberichte, UTC-Bereich und eine explizite Zeitpolicy. Reale Instrumente, Intervalle und Zeitraum legt AP02 anhand der verfügbaren Binance-/Kraken-Dateien fest. Der synthetische Referenzfall verwendet Minuten-Candles, 256 aufeinanderfolgende Schlusszeitpunkte, positive Preise und nichtkonstante Renditen mit bekanntem Shift von drei Minuten.

**Graph:** Katalog → zwei Candle-Quellen → logarithmische Close-Renditen → gemeinsames Zeitraster → Pearson-Korrelation/Kreuzkorrelation → Bericht und zwei synchronisierte Charts.

**Regeln:** `r[t] = log(close[t] / close[t-1])` nur bei positiven Preisen und unmittelbar benachbarten vollständigen Intervallen. Lücken erzeugen fehlende Renditen; kein implizites Fill. Verglichen werden exakte gemeinsame Schlusszeitpunkte. Pro Lag werden gültige Paare gezählt; unter 30 Paaren oder bei Nullvarianz wird kein Koeffizient ausgegeben. Raster `k = -10 … +10` Minuten; `corr(x[t], y[t+k])` bedeutet bei positivem k, dass x vorausläuft. Der unverunreinigte Referenzfall hat `y[t+3] = x[t]` und einen eindeutigen Peak bei +3. Fehlende Überlappung wird nicht durch Randauffüllung ersetzt.

Finale Candle-Werte sind frühestens ab `bar_end` und gegebenenfalls später verfügbar. Unterschiedliche Quote-Assets bleiben im Bericht sichtbar. Ein absoluter Spread verlangt eine eigene, zeitlich verfügbare Umrechnung; ohne diese wird er abgewiesen. Explorative Renditekorrelation ist auch bei verschiedenen Quotes möglich, trägt aber einen Quote-Risikohinweis.

**Outputs:** Koeffizienten und Paarzahlen je Lag, getesteter Suchumfang, Lag-Konvention, Datenlücken/Ausschlüsse, Qualitäts- und Zeitannahmen, Chartdaten sowie Run-Manifest. Der Befund wird explorativ gekennzeichnet; keine kausale oder handelbare Aussage und keine unbegründeten IID-p-Werte.

**Abnahme:** Referenzlag exakt +3 Rastereinheiten; ein separater verunreinigter Fall enthält Lücke, identisches Duplikat und spätere Korrektur. Duplikate werden nicht doppelt gezählt, Lücken nicht gefüllt und die Korrektur erscheint erst ab ihrer Verfügbarkeit. Nullvarianz, nichtpositive Preise, fehlende Paare und Quote-Konflikte ergeben nachvollziehbare Meldungen. Der reale AP02-Ausschnitt muss den Ablauf reproduzierbar durchlaufen, aber keinen bestimmten empirischen Lag ergeben.

## 3. Research-Ablauf B: OHLCV und Veröffentlichungsereignisse

**Frage:** Welche deskriptiven Renditen folgen auf bekannte Veröffentlichungsereignisse?

**Eingaben:** Ein Candle-Snapshot sowie offline importierbare synthetische Veröffentlichungsereignisse mit Entity, Ereignistyp, Originalzeitpunkten, Revision und Verfügbarkeitsgrundlage. Der separate Event-Adapter wird über die Registry konfiguriert. Kein externer API-Zugang ist erforderlich.

**Graph:** EventFrame + CandleFrame → Renditen/Alignment → deskriptive Ereigniszusammenfassung → Markerchart, Bericht und Vertragsexport.

**Ereignisanker und Revisionen:** `anchor_at` ist die Verfügbarkeit der ersten belegten Veröffentlichung eines `logical_id` in der gebundenen Zeitpolicy, nicht die Verfügbarkeit der jeweils neuesten Revision. Die anfängliche `record_id`, `anchor_at` und Policy werden im Run gebunden. Spätere Ereignisrevisionen sind erst ab ihrer eigenen Verfügbarkeit sichtbar, aktualisieren dann die angezeigten Attribute und bleiben demselben Ereignis zugeordnet. Sie ändern weder den ursprünglichen Anker noch die gewählten Kursreferenzen und erzeugen kein zweites unabhängiges Ereignis. Am Anker verwendete Ereignisattribute bleiben in ihrer damaligen Revision gebunden; spätere Attribute sind als Revision zu kennzeichnen und keine damals bekannten Features. Ist die Erstverfügbarkeit nicht belegt, scheidet das Ereignis aus der strikten Auswertung aus; sie wird nicht aus der frühesten zufällig vorhandenen Revision geraten. Ein expliziter Wechsel von Snapshot oder Policy erzeugt einen neuen Run mit ausgewiesenen Änderungen.

**Alignment und Startkurs:** Für die Kennzahl „fünf Minuten nach Verfügbarkeit“ ist ausschließlich ein finaler Candle-Close mit `bar_end = anchor_at` und `available_at <= anchor_at` zulässig. Die am Anker bekannte Kursrevision wird gebunden. Eine rückwärtsgerichtete Suche darf einen höchstens 60 Sekunden alten Close als Diagnosekandidaten liefern; bei `bar_end < anchor_at` wird dieser mit `baseline_age_seconds` und Ausschlussgrund `BASELINE_BEFORE_ANCHOR` ausgewiesen, aber nicht als Startkurs verwendet. Kein Forward-Fill, keine Interpolation und keine ersatzweise Verschiebung des Fensters. Bei nicht rastergenauem Anker oder verspätet verfügbarem Start-Close entfällt die Kennzahl ebenfalls mit ausgewiesenem Grund. Entity/Instrument-Zuordnung ist expliziter Parameter. Mehrdeutige gleiche Zeitpunkte werden ohne belegte Sequenz abgewiesen.

**Ergebnisfenster und Cutoff:** `window_start = anchor_at`, `window_end = anchor_at + 5 Minuten`; `r_5m = log(close(window_end) / close(window_start))` für positive Kurse derselben Reihe und Einheit. Der End-Close muss exakt `bar_end = window_end` haben. Seine erste finale Revision ist erst ab ihrer eigenen Verfügbarkeit auswertbar und wird dann gebunden; spätere Kurskorrekturen verschieben oder überschreiben dieses Referenzergebnis nicht stillschweigend. Ein neuer explizit korrigierter Run weist geänderte Kursreferenzen aus. Bei Auswertungs-Cutoff `C` gilt zusätzlich `window_end <= C` und `available_at(end_close) <= C`. Fehlende oder unbekannt verfügbare Endpunkte liefern keine Rendite. Das Ereignis kann vorher sichtbar sein, während sein Ergebnis noch aussteht. Ergebnisgrößen sind keine am Anker bekannten Features. Gleichheit am Cutoff ist bei eindeutigen Zeit-/Revisionsangaben zulässig; bei ungeklärter Reihenfolge gilt der konservative Ausschluss.

**Synthetische Abnahmefälle (2026-01-15, alle Zeiten UTC):** Ein Ereignis hat `event_time = published_at = 10:00:00`, Erstverfügbarkeit/Anker `10:02:00`; seine Korrektur wird `10:07:00` verfügbar. Vor 10:02 ist das Ereignis unsichtbar; ab 10:07 sind die Korrekturattribute sichtbar, aber Anker und Fenster bleiben 10:02 bis 10:07. Ein zweites Ereignis ohne belegte Erstverfügbarkeit ist ein strikter Negativfall. Die Zeiten sind synthetische Testwahrheit, kein Beleg realer Marktverfügbarkeit.

| Fall | Finale Closes mit eigener Verfügbarkeit | Erwartung |
|---|---|---|
| Ältere Baseline | 10:01:00: 100, verfügbar 10:01:00; kein Close um 10:02; 10:06:00: 104, verfügbar 10:06:00; 10:07:00: 110, verfügbar 10:07:30 | Diagnosealter 60 s, `BASELINE_BEFORE_ANCHOR`; auch ab Cutoff 10:07:30 keine Rendite. Weder 10:01→10:06 noch 10:01→10:07 gilt als fünf Minuten nach Verfügbarkeit. |
| Exakter Start, verzögertes Ende | Wie oben, zusätzlich 10:02:00: 100, verfügbar 10:02:00 | Start 10:02, Ende 10:07. Bei Cutoff 10:07:00 und 10:07:29 bleibt das Ergebnis ausstehend; erst bei 10:07:30 gilt `log(110/100) = 0,09531017980432493` (Logrendite, keine einfache Prozentzahl). Der Close 104 um 10:06 ist kein Endkurs. |
| Verspäteter Start | Close 10:02:00: 100 erst verfügbar 10:02:01; Ende wie oben | Kein am Anker verfügbarer Startkurs, Ausschluss auch nach 10:07:30; kein nachträgliches Auffüllen. |
| Spätere Ereignisrevision | Korrektur desselben `logical_id` verfügbar 10:07:00; Kurse wie im exakten Startfall | Ein Ereignis, Anker 10:02, Ende 10:07; keine Verschiebung auf 10:07→10:12 und keine zweite Rendite. Ein früherer eingefrorener Run sieht die Korrektur nicht. |

**Outputs:** Zahl berechtigter Ereignisse, Zahl vollständiger Fenster, Einzelrenditen, Mittelwert, Median, Minimum/Maximum sowie Überlappungen und Ausschlüsse. Bei leerer Stichprobe sind Kennzahlen nicht definiert. Marker zeigen in dieser Referenzsicht den festen `anchor_at` sowie die ursprüngliche und die am Cutoff sichtbare Revision und abweichende Ereignis-/Publikationszeit im Detail. Andere Sichten sind explizit beschriftet. Export enthält Ergebnisdaten und Manifest einschließlich synthetischer Herkunft und Zeitannahmen; kein allgemeiner Exporteditor ist erforderlich.

**Abnahme:** Event ohne Venue/Instrument durchläuft Import, Snapshot, Query, Workspace und Export. Verspätete Ereignisse und Revisionen sind vor ihrer Verfügbarkeit unsichtbar; nach dem Cutoff geänderte Daten verändern frühere Features nicht. Die obigen Referenzfälle, fehlende Endpunkte, ausgeschlossene ältere Baselines und überlappende Fenster werden ausgewiesen. Speichern/Laden und erneutes Ausführen erhält fachliche Manifestangaben und Ergebnisse.

## 4. Gemeinsame Verträge

### Connector, Normalisierung und Registry

Registrierung bindet `connector_id`, Vertrags- und Implementierungsversion, unterstützte `data_kinds`, Schemaversionen und Fähigkeiten `historical_backfill`, `live_stream`, `point_in_time`, `replay`. Punkt-in-Zeit-Fähigkeit nennt zusätzlich belegte Reihen/Zeiträume und Grundlage; ein globales Boolean ersetzt keinen Verfügbarkeitsnachweis.

Ein Abruf-/Importauftrag erhält Quell-ID, erlaubte Eingabereferenzen, optionalen Cursor, Bereich und Secret-Referenzen. Er liefert unveränderte Raw-Payloads/Dateireferenzen, Hashes, tatsächlichen Empfang und Fortsetzungscursor oder einen klassifizierten Fehler. Der Normalizer liefert versionierte Candle- oder Veröffentlichungsevent-Records, Raw-Referenzen und Qualitätsbericht. Abbruch/Teilfehler lassen keinen unvollständigen Snapshot sichtbar werden. Wiederholung desselben Inputs ist fachlich idempotent.

Das MVP unterstützt `candle` und `publication_event`. Beide verwenden die Ereignishülle aus dem Datenmodell; Events ergänzen `event_type` und `entity_id`, optional Attribute mit Einheit. Instrument- und Candle-Felder sind keine Event-Pflichtfelder. Unbekannte Schemaversionen und widersprüchliche Revisionen scheitern ausdrücklich. Physische Tabellen dürfen je Datenart getrennt sein.

Für Snapshots gilt der [Veröffentlichungsvertrag aus ADR-0005](adr/0005-snapshot-commit.md): vollständige Validierung und dauerhafte Sicherung aller Dateien und des Manifests vor dem PostgreSQL-Commit sowie koordinierter Schutz gegen paralleles Aufräumen. Recovery und Wiederholung dürfen nie einen unvollständigen Snapshot lesbar machen.

Registry-Einträge deklarieren normalisierte Porttypen und Versionen. Ein zusätzlicher vertragskonformer Adapter erfordert Registrierung/Konfiguration, aber keine Änderung an Query-/Research-Kern oder Executor. Neue Datenmodalitäten außerhalb der zwei vereinbarten Typen können neue Schemata und Plugins erfordern.

### Query, Analyse und Runs

Die Endpoints aus dem API-Entwurf bleiben maßgeblich. Katalogfilter umfassen Quelle, Datenart, Entity/Instrument, Zeitbereich, Qualität und Verfügbarkeitsstatus, bei Candles zusätzlich Intervall. Die Query bindet Dataset/Snapshot, Mapping-Version, Projektion, Bereich `[start,end)`, Zeitfeld des Filters, Perspektive, versionierte Verfügbarkeitspolicy und Cutoff. Vorschau und vollständige Analyse unterscheiden sich durch explizite Limits; eine begrenzte Vorschau ist keine vollständige Statistikeingabe.

Antworten tragen Datenart/Schemaversion, Einheiten, Qualitätsstatus, Zeit-/Revisionsmetadaten und Herkunft. Gleiche Semantik verschiedener Provider ergibt dasselbe Schema je Datenart. CandleFrame und EventFrame werden nicht auf eine universelle Pflichtstruktur reduziert. Bestehende Fehlercodes werden um `UNSUPPORTED_SCHEMA`, `AMBIGUOUS_REVISION`, `INCOMPATIBLE_UNITS` und `INSUFFICIENT_SAMPLE` ergänzt; fachlich leere Auswertungen werden als solche ausgewiesen, nicht als berechnete Nullwerte.

Analysen deklarieren Porttypen, Parameter, Zeit-/Einheitenbedingungen, Ressourcen und Ausgabeschema. Alignment verwendet `direction`, `max_age_seconds`, Gruppen-/Entity-Mapping, Zeitbasis und Policy; künftige Ergebnisgrößen erhalten einen vom historischen Feature unterscheidbaren Portvertrag. Der Planner weist unzulässige Verbindungen zurück.

Strikte historische Marktsicht erfordert belegte Vintages; System-Replay verwendet tatsächlichen Empfang und Verarbeitung. Geschätzte Verfügbarkeit ist nur im ausdrücklich gewählten Annahmemodus zulässig, unbekannte Verfügbarkeit nie durch Ereigniszeit zu ersetzen. Explorative Sichten ohne Nachweis tragen keinen Punkt-in-Zeit-sicher-Status. Diese Dimensionen gehören in Manifest und Cacheidentität.

Die [Plugin-Freigabe aus ADR-0006](adr/0006-plugin-vertrauen.md) bindet Plugin-ID, Implementierungsversion und unveränderlichen Code-/Paketnachweis. Registry, Manifest und Cache übernehmen diese Identität; Änderungen brauchen erneute Prüfung. Fehlt die gebundene alte Version, der passende Nachweis oder ihre Freigabe, scheitert die Ausführung ausdrücklich ohne Versionsfallback.

Manifestvergleich umfasst Graph, Parameter, Snapshots/Hashes, Mapping, Code-/Plugin-/Environment-Versionen, Seed und Zeitpolicy. Run-ID, Ausführungszeiten, Laufzeitmessungen und davon abgeleitete Manifestdateihashes dürfen abweichen. Für Float64-Referenzergebnisse gilt zunächst `abs(actual-expected) <= 1e-12 + 1e-9*abs(expected)`; Zählwerte, IDs und erwartete Zeitpunkte stimmen exakt. Abweichende Engine-Toleranzen benötigen begründete, versionierte Referenztests in AP08.

### Repository-Grenzen

Geplante Struktur, noch keine angelegten Anwendungsmodule:

| Bereich | Aufgabe |
|---|---|
| `packages/backend/` | Kanonische Verträge, Katalog, Query, Planner, Workspace, API und Worker; getrennte Module und Prozesse, gemeinsamer versionierter Kern |
| `plugins/connectors/` | Pilotadapter und quellenspezifische Normalizer; keine Providerverzweigungen im Kern |
| `plugins/analyses/` | Geprüfte Transformationen, Alignment und Statistik |
| `apps/web/` | React-/TypeScript-Katalog, Canvas und Visualisierung |
| `tests/fixtures/` | Kleine synthetische Candle-/Event-Eingaben und erwartete Ergebnisse, keine privaten Originaldaten |
| `docs/` | Verträge, ADRs, Abnahme- und Benchmarknachweise |

## 5. Anforderungs- und Prüfübergabe

Alle folgenden Tests sind **spezifiziert, noch nicht ausgeführt**. AP01 prüft Dokumentationskonsistenz; Software- und End-to-End-Nachweise entstehen erst mit den genannten Paketen.

| Anforderungen | Nachweis | Verantwortliche Rolle | Umsetzung |
|---|---|---|---|
| F-01, F-02 | Beide Datentypen katalogisieren und im jeweiligen kanonischen Schema abfragen | Daten/Architektur | AP03–05 |
| F-03, F-04 | Gemeinsame UTC-Achse; gültiger Graph ausführbar, Typfehler und Zyklen blockiert | Architektur | AP05–07 |
| F-05, F-06 | Ablauf A mit bekanntem Lag; Parameterwechsel und Schutz vor alten Resultaten | Research/Architektur | AP04/06/08 |
| F-07, F-08 | Beide Graphen nach Reload reproduzierbar; gebundene Herkunft und Versionen | Architektur | AP03/04/06 |
| F-09 | Candle-Ende, Cutoffs, Revisionen, Unknown/Estimated, Mappingwechsel und Zukunftsänderung prüfen | Daten/Research | AP03/04/08 |
| F-10 | Ergebnis und Manifest des Event-Vertragstests exportieren | Architektur | AP04/06 |
| F-11 | Separaten Event-Adapter nur per Registrierung ergänzen; zusätzliche Quell-IDs/Quotes und äquivalente Provider-Fixtures testen | Daten/Architektur | AP03/04 |
| F-12 | Ablauf B mit explizitem Alignment, Markern und Ergebnisfenster | Research/Architektur | AP06–08 |
| N-01–N-07 | Manifest, Limits/Abbruch, Qualitätsbericht, Registry, Importwiederholung/Restore, lokaler Start und gemessene Budgets | Architektur/Betrieb | AP02–08 |

## 6. Inventurvertrag für AP02

AP02 erhält konfigurierte, erlaubte Quellpfade; ein Scan ist schreibgeschützt. Er verschiebt, normalisiert oder repariert keine Originaldateien. Jede bereitgestellte Datei erhält Pfadreferenz, SHA-256, Bytes, Lesestatus, Format-/Schemahinweise, Quelle, Instrument/Quote soweit belegt, Zeit-/Intervalldefinition, Zeilenzahl und Zeitabdeckung. Unbekannte Angaben bleiben unbekannt. Lücken, identische Duplikate, Wertkonflikte und Parsefehler werden mit Zählung und Fundstellen gemeldet; unlesbare Dateien bleiben im Gesamtinventar.

Ein reproduzierbarer Bericht bindet Scanversion, Konfiguration, Zeitpunkt und Dateihashes. Originalhashes werden auf unverändert geprüft. AP02 liefert die Formatmatrix für zwei Pilotadapter, kleine und mehrjährige Benchmarkausschnitte, Gesamtvolumen und Hardwareprofil. Der synthetische Eventbestand entsteht separat als Fixture in AP03; er wird nicht als vorgefundener Realbestand inventarisiert. Private Speicherorte gehören in lokale Konfiguration statt öffentliche Dokumentation.

## 7. Offene Entscheidungen mit Gates

Die Tabelle deckt D-01 bis D-20 sowie das Plugin-Vertrauen A-06 ab. **Vertragsfreigabe** bedeutet eine dokumentierte Entscheidung durch die zuständige Rolle; **Implementierungsnachweis** bedeutet erst den später ausgeführten Test oder Benchmark. Vorschläge werden durch diesen Review nicht freigegeben. Die technische Freigabe der vorgeschlagenen AP01-ADRs und die Entscheidung über D-08 sind Voraussetzungen der formalen AP01-Abnahme; spätere Softwaretests sind keine vorgezogenen AP01-Gates.

| Entscheidung / aktueller Status | Verantwortliche Rolle | Überprüfbares Entscheidungskriterium und spätester Entscheidungspunkt | Späterer Implementierungsnachweis |
|---|---|---|---|
| Rollenbesetzung | Produkt | Tatsächliche Verantwortliche benennen; vor formaler AP01-Abnahme und Beginn AP02/03 | Keine erfundenen Personalzuweisungen |
| D-01 K; D-14/D-19 B · MVP/Lokalbetrieb, ADR-0001 accepted | Produkt/Research | Bereits festgelegte zwei Referenzabläufe und lokalen Einzelbetrieb beibehalten; Änderungen vor Scope-/Betriebserweiterung neu entscheiden | Beide Abläufe AP03–08; kein Nachweis durch accepted-Status |
| D-02/D-03 K · Speicherrollen | Architektur | Bestehende Parquet-/DuckDB-/Polars- und PostgreSQL-Rollen sind Kontext; Abweichungen vor Umsetzung gesondert entscheiden | Lastprofil AP04, Persistenz AP03/04 |
| D-04 O/V · Jobrunner | Architektur/Betrieb | Runner anhand Claim-, Lease-, Retry- und Abbruchkonzept auswählen; vor produktiver Jobintegration in AP04 | Recovery und Idempotenz AP04 vor M1 |
| D-05 K/V; D-10 O · Laufzeiten, Frameworks, Bibliotheken | Architektur | Kompatible unterstützte Versionen und Lizenzen dokumentieren; Backend vor AP03-Code, UI vor AP05-Code | Vertikaler Prototyp und Kompatibilitätsprüfungen AP03–05 |
| D-07 K/V · Zeit-/Verfügbarkeitspolicy, ADR-0004 proposed | Daten/Research | Perspektiven, Erstverfügbarkeitsanker, Revisionen, Start-/Endkurs, Unknown/Estimated und Cutoffs anhand der Referenzfälle widerspruchsfrei freigeben; vor formaler AP01-Abnahme, spätestens vor AP03-Vertragsimplementierung | Zeit-/Revisions- und Fensterregressionen AP03/04/08 |
| D-08 V · Statistikumfang M2 | Research/Produkt | Mindestumfang F-05 plus deskriptive Event-Zusammenfassung/Cutoff-Prüfung und Ausschluss weitergehender Statistik als M2-Blocker ausdrücklich entscheiden; vor formaler AP01-Abnahme und AP08-Planung | Beide MVP-Abnahmeläufe AP06–08 vor M2 |
| D-09 O · Lizenz/Governance/Contribution/Security | Produkt | Lizenzwahl, Beitragsregeln und Security-Verantwortung anhand gewünschter Nutzung und Abhängigkeiten dokumentieren; vor öffentlicher Codefreigabe | Einhaltung und Kontakt-/Prozessprüfung bei Veröffentlichung |
| D-11 O · Backup/Retention/Budgets | Betrieb | AP02-Volumen und Änderungsrate in Backupplan, Speicherbudget, RPO/RTO und Retention überführen; vor Betriebsfreigabe M1 | Vollständiger Restore vor M1 |
| D-12 V · Snapshot-Commit, ADR-0005 proposed | Architektur/Betrieb | Dauerhaftigkeit vor Commit, vollständige Validierung, koordinierte Veröffentlichungs-/Aufräumrechte, Lesersicht und Recovery gemäß ADR-0005 freigeben; vor formaler AP01-Abnahme, spätestens vor AP03-Persistenzcode | Crashpunkte, Wiederholung und Hash-/Restoreprüfung AP03/04 vor M1 |
| D-13 O · Quellenverfügbarkeit | Daten | Pro Quelle belegte Vintages oder ausdrücklich gekennzeichnete Annahmen und Rechte im Quellenblatt entscheiden; vor Importfreigabe bzw. strikter Realanalyse | Quellfixtures, Cutoffs und Rechteprüfung AP02–04; ADR-0004-Freigabe ersetzt keine Quellbelege |
| D-18 V; D-20 O/V · Kern-/Connectorgrenzen, ADR-0002/0003 proposed | Architektur/Daten | Zwei Modalitäten, stabile Identitäten, Fähigkeiten und Registrierung ohne Providerzweige im Kern anhand F-11 freigeben; vor formaler AP01-Abnahme und AP03-Code | Provider-Wechsel-, Schema- und Connector-Vertragstests AP03/04 |
| A-06 Annahme · Plugin-Vertrauen, ADR-0006 proposed | Architektur/Betrieb | Allowlist-Tupel aus ID/Version/Code-Nachweis, erneute Prüfung bei Änderungen, Scheitern bei fehlenden Altversionen, Secret-Grenzen und fehlende Fremdcodeisolation ausdrücklich freigeben; vor formaler AP01-Abnahme und Pluginladung AP04 | Registry-, Versions-, Secret- und Portprüfungen AP04/06 |
| D-06 K/O; D-15 O · Live/Stores/native Module | Architektur | Last-/Recovery-/Profilingbefund und Betriebsaufwand rechtfertigen die jeweilige Auswahl; vor entsprechendem Ausbau, kein MVP-Gate | Benchmark und Recovery/Referenzvergleich beim Ausbau |
| D-16 O · Backtesting-Ziel | Research | Zeit-, Kosten- und Exportvertrag mit gewähltem Integrationsziel abgleichen; vor Integration AP14 | Punkt-in-Zeit-Referenzhypothese AP14 |
| D-17 O · Name/Marke | Produkt | Verfügbarkeit gesondert prüfen und Arbeitsnamen bestätigen/ersetzen; vor öffentlicher Namensfestlegung | Dokumentierter Prüfbeleg, keine ungeprüfte Verfügbarkeitsaussage |

Die Wahl einzelner Bibliotheken oder einer Softwarelizenz wird durch AP01 nicht vorweggenommen. Änderungen an angenommenen ADRs erhalten einen versionierten Nachfolger.

## 8. Dokumentationsprüfung

Am 22. November 2026 geprüft: lokale Markdown-Dateiverweise, Abschnittsanker, geschlossene Codeblöcke, JSON-Beispiele, eindeutige ADR-Nummern/-Status, Abdeckung F-01 bis F-12 in der Übergabematrix und `git diff --check`. README dient als Einstieg zum Vertrag und zum ADR-Register.

Das Repository enthält ausschließlich Dokumentation; Test-, Formatierungs-, Lint- und Typprüfungsbefehle für Anwendungscode sind noch nicht eingerichtet. Der Event-Referenzfall wurde zusätzlich rechnerisch auf Anker/Ende, Baseline-Ausschluss, Logrendite und Endkurs-Cutoff geprüft. Dies ist eine Prüfung der dokumentierten Erwartungswerte, kein Anwendungstest. Entsprechend wurden keine Softwaretests oder Benchmarks ausgeführt. Technische ADR-Annahme, D-08-Entscheidung und Rollenbesetzung bleiben für AP01 offen; spätere Implementierungsnachweise folgen in den benannten Paketen.
