# 08 · AP01-Vertrag und Übergabe

[Zur Übersicht](../README.md)

## 1. Status und Zuständigkeiten

Stand: 22. November 2026. Dieser Vertrag konkretisiert AP01; er beschreibt keine implementierten Funktionen. Lokalbetrieb für eine Person wurde im Projektgespräch bestätigt. Die folgenden technischen Festlegungen sind der zur Prüfung vorgelegte AP01-Entwurf; die ADRs kennzeichnen sie als `proposed`.

Die Rollen Produkt, Research, Daten, Architektur und Betrieb sind Verantwortungsbereiche, keine behaupteten Personalzuweisungen. Die namentliche Besetzung bleibt vor Beginn von AP02/03 offen. AP01 ist bis zu dieser Zuordnung und der Annahme der vorgeschlagenen ADRs **zur Abnahme vorbereitet**, nicht abgeschlossen.

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

**Referenzfall:** Ein Ereignis hat `event_time = published_at = 10:00 UTC`, `available_at = 10:02 UTC`; seine Revision wird erst um 10:07 verfügbar. Die konkrete UTC-Datumsangabe ist Teil der versionierten Fixture. Am Cutoff 10:01 ist kein Ereignis sichtbar, um 10:02 die erste Revision und um 10:07 deren Nachfolger. Ein zweites Ereignis ohne belegte Verfügbarkeit dient als Negativfall. Die synthetischen Zeitangaben sind Testwahrheit und keine Evidenz realer Marktverfügbarkeit.

**Alignment:** Vor dem Join wird der bekannte Revisionsstand am jeweiligen Cutoff rekonstruiert. Standard für diesen Referenzfall ist rückwärtsgerichtete Zuordnung eines finalen Candle-Close zum Ereignisanker `available_at`, Alter höchstens 60 Sekunden inklusive Grenze. Entity/Instrument-Zuordnung ist expliziter Parameter; keine automatische fachliche Gleichsetzung. Mehrdeutige gleiche Zeitpunkte werden ohne belegte Sequenz abgewiesen. Fehlende Zuordnung bleibt als Ausschluss erhalten.

**Ergebnisfenster:** Logarithmische Rendite vom zugeordneten Baseline-Close zum Close exakt fünf Minuten später. Beide Endpunkte müssen vorliegen; keine Approximation des Horizonts oder Auffüllung. Das ist eine zukünftige Ergebnisgröße, kein zum Ereignisanker bekanntes Feature. Ein Auswertungs-Cutoff muss auch die Verfügbarkeit des Endpunkts einschließen. Ereignis- und Ergebnisberechtigung werden getrennt ausgewiesen. Revisionen werden niemals mehrfach als unabhängige Ereignisse gezählt.

**Outputs:** Zahl berechtigter Ereignisse, Zahl vollständiger Fenster, Einzelrenditen, Mittelwert, Median, Minimum/Maximum sowie Überlappungen und Ausschlüsse. Bei leerer Stichprobe sind Kennzahlen nicht definiert. Marker zeigen in dieser Referenzsicht `available_at`, Revision und abweichende Ereignis-/Publikationszeit im Detail. Andere Sichten sind explizit beschriftet. Export enthält Ergebnisdaten und Manifest einschließlich synthetischer Herkunft und Zeitannahmen; kein allgemeiner Exporteditor ist erforderlich.

**Abnahme:** Event ohne Venue/Instrument durchläuft Import, Snapshot, Query, Workspace und Export. Verspätete Ereignisse und Revisionen sind vor ihrer Verfügbarkeit unsichtbar; nach dem Cutoff geänderte Daten verändern frühere Features nicht. Fehlende Endpunkte, zu alte Baselines und überlappende Fenster werden ausgewiesen. Speichern/Laden und erneutes Ausführen erhält fachliche Manifestangaben und Ergebnisse.

## 4. Gemeinsame Verträge

### Connector, Normalisierung und Registry

Registrierung bindet `connector_id`, Vertrags- und Implementierungsversion, unterstützte `data_kinds`, Schemaversionen und Fähigkeiten `historical_backfill`, `live_stream`, `point_in_time`, `replay`. Punkt-in-Zeit-Fähigkeit nennt zusätzlich belegte Reihen/Zeiträume und Grundlage; ein globales Boolean ersetzt keinen Verfügbarkeitsnachweis.

Ein Abruf-/Importauftrag erhält Quell-ID, erlaubte Eingabereferenzen, optionalen Cursor, Bereich und Secret-Referenzen. Er liefert unveränderte Raw-Payloads/Dateireferenzen, Hashes, tatsächlichen Empfang und Fortsetzungscursor oder einen klassifizierten Fehler. Der Normalizer liefert versionierte Candle- oder Veröffentlichungsevent-Records, Raw-Referenzen und Qualitätsbericht. Abbruch/Teilfehler lassen keinen unvollständigen Snapshot sichtbar werden. Wiederholung desselben Inputs ist fachlich idempotent.

Das MVP unterstützt `candle` und `publication_event`. Beide verwenden die Ereignishülle aus dem Datenmodell; Events ergänzen `event_type` und `entity_id`, optional Attribute mit Einheit. Instrument- und Candle-Felder sind keine Event-Pflichtfelder. Unbekannte Schemaversionen und widersprüchliche Revisionen scheitern ausdrücklich. Physische Tabellen dürfen je Datenart getrennt sein.

Registry-Einträge deklarieren normalisierte Porttypen und Versionen. Ein zusätzlicher vertragskonformer Adapter erfordert Registrierung/Konfiguration, aber keine Änderung an Query-/Research-Kern oder Executor. Neue Datenmodalitäten außerhalb der zwei vereinbarten Typen können neue Schemata und Plugins erfordern.

### Query, Analyse und Runs

Die Endpoints aus dem API-Entwurf bleiben maßgeblich. Katalogfilter umfassen Quelle, Datenart, Entity/Instrument, Zeitbereich, Qualität und Verfügbarkeitsstatus, bei Candles zusätzlich Intervall. Die Query bindet Dataset/Snapshot, Mapping-Version, Projektion, Bereich `[start,end)`, Zeitfeld des Filters, Perspektive, versionierte Verfügbarkeitspolicy und Cutoff. Vorschau und vollständige Analyse unterscheiden sich durch explizite Limits; eine begrenzte Vorschau ist keine vollständige Statistikeingabe.

Antworten tragen Datenart/Schemaversion, Einheiten, Qualitätsstatus, Zeit-/Revisionsmetadaten und Herkunft. Gleiche Semantik verschiedener Provider ergibt dasselbe Schema je Datenart. CandleFrame und EventFrame werden nicht auf eine universelle Pflichtstruktur reduziert. Bestehende Fehlercodes werden um `UNSUPPORTED_SCHEMA`, `AMBIGUOUS_REVISION`, `INCOMPATIBLE_UNITS` und `INSUFFICIENT_SAMPLE` ergänzt; fachlich leere Auswertungen werden als solche ausgewiesen, nicht als berechnete Nullwerte.

Analysen deklarieren Porttypen, Parameter, Zeit-/Einheitenbedingungen, Ressourcen und Ausgabeschema. Alignment verwendet `direction`, `max_age_seconds`, Gruppen-/Entity-Mapping, Zeitbasis und Policy; künftige Ergebnisgrößen erhalten einen vom historischen Feature unterscheidbaren Portvertrag. Der Planner weist unzulässige Verbindungen zurück.

Strikte historische Marktsicht erfordert belegte Vintages; System-Replay verwendet tatsächlichen Empfang und Verarbeitung. Geschätzte Verfügbarkeit ist nur im ausdrücklich gewählten Annahmemodus zulässig, unbekannte Verfügbarkeit nie durch Ereigniszeit zu ersetzen. Explorative Sichten ohne Nachweis tragen keinen Punkt-in-Zeit-sicher-Status. Diese Dimensionen gehören in Manifest und Cacheidentität.

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

| Entscheidung | Owner-Rolle | Kriterium und spätester Entscheidungspunkt |
|---|---|---|
| Rollenbesetzung und ADR-Annahme | Produkt | Tatsächliche Verantwortliche zuordnen und Entwurf prüfen; vor AP02/03 |
| D-04 Jobrunner | Architektur/Betrieb | Claim, Lease, Wiederholung, Abbruch und Recovery nachweisen; AP04 vor M1 |
| D-05/D-10 Laufzeiten, Frameworks, UI-Bibliotheken | Architektur | Unterstützte kompatible Versionen, Lizenzen und vertikaler Prototyp; Backend vor AP03-Code, UI vor AP05 |
| D-09 Lizenz/Governance/Security | Produkt | Gewünschte Nutzung und Abhängigkeiten prüfen; vor öffentlicher Freigabe von Code |
| D-11 Backup/Retention/Budgets | Betrieb | AP02-Volumen und Änderungsrate; Restore sowie RPO/RTO vor M1 |
| D-13 Quellenverfügbarkeit und Datenrechte | Daten | Quellenblatt, belastbare Zeitnachweise und Nutzungsrechte; vor Importfreigabe/strikter Realanalyse |
| D-18/D-20 technische Vertragsgrenzen | Architektur/Research | Beide beschriebenen Abläufe und F-11 abdecken; ADR-Annahme vor AP03 |
| D-06/D-15 zusätzliche Stores/native Module | Architektur | Reproduzierbarer Last-/Profilingnachweis; erst bei Ausbau, kein MVP-Gate |
| D-16 Backtesting-Ziel | Research | Zeit-/Kosten-/Exportvertrag; AP14 |
| D-17 Name/Marke | Produkt | Verfügbarkeit gesondert prüfen; vor öffentlicher Namensfestlegung |

Die Wahl einzelner Bibliotheken oder einer Softwarelizenz wird durch AP01 nicht vorweggenommen. Änderungen an angenommenen ADRs erhalten einen versionierten Nachfolger.

## 8. Dokumentationsprüfung

Am 22. November 2026 geprüft: lokale Markdown-Dateiverweise, Abschnittsanker, geschlossene Codeblöcke, JSON-Beispiele, eindeutige ADR-Nummern/-Status, Abdeckung F-01 bis F-12 in der Übergabematrix und `git diff --check`. README dient als Einstieg zum Vertrag und zum ADR-Register.

Das Repository enthält ausschließlich Dokumentation; Test-, Formatierungs-, Lint- und Typprüfungsbefehle für Anwendungscode sind noch nicht eingerichtet. Entsprechend wurden keine Softwaretests oder Benchmarks ausgeführt. Technische ADR-Annahme, Rollenbesetzung und spätere Implementierungsnachweise bleiben offen.
