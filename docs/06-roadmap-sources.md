# 06 · Roadmap, Arbeitspakete und Datenquellen

[Zur Übersicht](../README.md)

## 1. Planungsgrundlage

**Kontextfestlegung:** Vier Phasen mit 14 Arbeitspaketen, jeweils mit nutzbarem Ergebnis. Keine festen Kalendertermine vor Dateninventur und Hardwarebenchmark. Versionen bezeichnen Zielmeilensteine und keine bereits veröffentlichten Releases. Querschnittlich gelten Tests, Dokumentation, Reproduzierbarkeit und sichere Zugangsdaten.

| Phase | Pakete | Zielmeilenstein |
|---|---|---|
| 1 · Foundation | AP 01–04 | M1 / v0.0.1 · Data Foundation |
| 2 · Interactive Research Workspace | AP 05–08 | M2 / v0.1 · Research MVP |
| 3 · Market Intelligence | AP 09–11 | M3 / v0.2 · Intelligence Platform |
| 4 · Advanced Research | AP 12–14 | M4 / v0.3 · Advanced Research Platform |

Die Namen und Reihenfolge stammen aus dem Gespräch; Liefergegenstände, Abnahmekriterien und Detailabhängigkeiten sind hier konkretisierte Vorschläge. Frontend und Statistik können nach Stabilisierung der Verträge parallel entwickelt werden, ohne die Meilensteinabnahme vorwegzunehmen.

## 2. Phase 1 · Foundation

### AP 01 · Anforderungen und Systemdesign

**Ziel:** tragfähige Verträge und MVP-Grenzen. **Abhängigkeit:** keine.

Lieferumfang: bestätigter Scope, ADRs zu Anbieter- und Handelsplatzunabhängigkeit sowie Connector- und Modalitätsgrenzen, Komponenten- und Datenmodell, Zeitpolicy, Plugin-/API-Entwurf, Repository-Struktur und erste ADRs. Entscheidungen zu Lizenz, Laufzeitversionen und lokaler Betriebsform werden vorbereitet.

**Abnahme:** Der börsenübergreifende OHLCV-Vergleich und der heterogene OHLCV-/Event-Ablauf sind mit Eingaben, Ergebnissen und Zeitannahmen beschrieben; offene Entscheidungen besitzen Owner/Rolle und Entscheidungskriterium; kein autonomes Trading im Scope. Verantwortliche Personen müssen noch benannt werden.

**Arbeitsstand:** [AP01-Vertrag](08-ap01-contract.md) und sechs ADRs liegen vor. Lokalbetrieb ist bestätigt; die Rollen sind besetzt. Die technische ADR-Annahme und die ausdrückliche Entscheidung über D-08 stehen aus. Vertragsfreigabe erfolgt vor formaler AP01-Abnahme; Software-/Recovery-Nachweise folgen erst in den Umsetzungspaketen. AP01 ist zur Abnahme vorbereitet, noch nicht abgenommen.

### AP 02 · Dateninventur und Qualitätsanalyse

**Ziel:** belegter Ausgangsbestand statt angenommener Datenqualität. **Abhängigkeit:** Inventurvertrag aus AP 01.

Lieferumfang: schreibgeschützter Scan aller bereitgestellten Binance-/Kraken-OHLCV-Dateien, Hashes, Größen, Formate, Märkte, Auflösungen, Zeiträume, Duplikate, Lücken und Konflikte. Physische Speicherorte und Zugriffsrechte werden erfasst, bevor irgendetwas verschoben wird.

**Abnahme:** Inventar und reproduzierbarer Qualitätsbericht decken alle bereitgestellten Dateien ab; nicht lesbare Dateien sind separat ausgewiesen; Originalhashes bleiben unverändert. Repräsentative Benchmarkausschnitte sind festgelegt.

### AP 03 · Data Lake und Datenintegration

**Ziel:** Raw-/Normalized-/Derived-Modell mit historischer Verfügbarkeit. **Abhängigkeit:** AP 01, AP 02.

Lieferumfang: Versionierte Connector- und Normalizer-Verträge für Raw, Normalized und Derived, Instrument- und Entitykatalog, Zeit- und Qualitätsmodell, Quarantäne, versionierte Parquet-Snapshots und Commit-Protokoll. Zwei Pilotadapter importieren die bestätigten Binance-/Kraken-Formate. Ein separat registrierter synthetischer Event-Adapter verwendet denselben Importpfad.

**Abnahme:** Wiederholter Import erzeugt keine fachlichen Duplikate; Korrekturen bleiben nachvollziehbar; ein Snapshot ist vollständig oder unsichtbar; unbekannte Verfügbarkeit wird nicht verschleiert; alle Werte verweisen auf Raw-Daten. Der Event-Adapter erfüllt F-11 und die Connector-Vertragstests.

### AP 04 · Backend und Performance-Grundlage

**Ziel:** einheitliche Abfrage und isolierte Berechnung. **Abhängigkeit:** AP 01, funktionsfähiger Importpfad aus AP 03.

Lieferumfang: Query-/Job-API, DuckDB-/Polars-Pfade, Worker, Limits, Cache, Benchmarkreport und erste Wiederherstellung. Schwergewichtige Analyse darf asynchron sein.

**Abnahme:** OHLCV-Zeitreihen beider Pilotquellen und unregelmäßige Ereignisse sind über dieselbe Query- und Job-API nutzbar; Referenzbenchmarks dokumentiert; Jobabbruch und Crash-Recovery geprüft; Cache unterscheidet Daten-/Code-/Zeitpolicy-Versionen.

**M1:** Daten aus zwei getrennt implementierten Handelsplatzadaptern und einem synthetischen Event-Adapter sind über den gemeinsamen Katalog und dieselbe Abfrageschnittstelle nutzbar. Für beide Datentypen sind versionierte Parquet-Snapshots, Raw-Herkunft, Qualitätsberichte und Zeitsemantik nachvollziehbar.

## 3. Phase 2 · Interactive Research Workspace

### AP 05 · Frontend-Grundgerüst

**Ziel:** nutzbare React-/TypeScript-Anwendung. **Abhängigkeit:** API-Vertrag AP 01/04.

Lieferumfang: Navigation, Layout, Datenbrowser, Einstellungen, Fehler-/Ladezustände und Metadatenanzeige. **Abnahme:** Candles und Ereignisse nach Datentyp, Quelle, Entity/Instrument, Zeitbereich, Qualität und Verfügbarkeit auswählbar; nicht verfügbare Daten werden verständlich ausgewiesen.

### AP 06 · Interaktive Arbeitsfläche

**Ziel:** speicherbarer Analysegraph. **Abhängigkeit:** AP 05 sowie Plugin-/Jobvertrag AP 04/08.

Lieferumfang: Nodes und Ports, Kantenprüfung, Parameterformulare, Graph-/Layoutversionen, Laden und Speichern. **Abnahme:** Quelle → Analyse → Output sowie Ereignisse + OHLCV → Alignment → Analyse → Chart ausführbar; Zyklen und Typfehler blockiert; Reload rekonstruiert Graph; verspätete Ergebnisse überschreiben keinen neueren Parameterstand.

### AP 07 · Visualisierungsengine

**Ziel:** interpretierbare Ergebnisse und synchronisierte Zeitachsen. **Abhängigkeit:** AP 05, Queryvertrag AP 04; Integration mit AP 06.

Lieferumfang: Zeitreihencharts, Heatmaps, synchroner Zoom/Cursor, Ereignismarker mit Zeitbezug, Datenlückenanzeige, begrenzter Transfer und Darstellungsaggregation. **Abnahme:** mindestens zwei Reihen teilen denselben sichtbaren UTC-Bereich; Display-Downsampling verändert keine Analysewerte; Einheiten und Lag-Konvention sind erkennbar.

### AP 08 · Statistical Research Engine

**Ziel:** versionierte statistische Analyseplugins. **Abhängigkeit:** Daten-/Zeitvertrag AP 03, Worker AP 04.

Lieferumfang: MVP-Verfahren gemäß Scope einschließlich deskriptiver Renditezusammenfassung zu Ereignissen und Cutoff-Prüfung; danach Stationarität/Cointegration, Regression/Faktoren, Anomalien/Strukturbrüche und Signifikanzverfahren. **Abnahme:** synthetische Referenzen, bekanntes Lag, Nullfälle und Fehlereingaben geprüft; Ergebnisse tragen Methode, Parameter, Stichprobe, Unsicherheit und Lineage. Erweiterter Releaseumfang bleibt D-08.

**M2:** Beide [MVP-Abnahmeläufe](01-product-scope.md) sind erfolgreich. Der Workspace unterstützt den Vergleich zweier OHLCV-Reihen sowie einen OHLCV-/Event-Graphen mit explizitem Alignment, Verfügbarkeitsprüfung und gemeinsamer Darstellung. Beide Arbeitsflächen lassen sich speichern, laden und mit denselben Eingaben reproduzierbar ausführen. Der Event-Referenzfall prüft das an Erstverfügbarkeit gebundene Fünf-Minuten-Fenster, den Ausschluss älterer Baselines, verzögerte Endkursverfügbarkeit und revisionsstabile Anker gemäß AP01-Vertrag.

## 4. Phase 3 · Market Intelligence

### AP 09 · Externe Datenkonnektoren

**Ziel:** heterogene Daten schrittweise integrieren. **Abhängigkeit:** AP 03/04, Connector-Vertrag.

Lieferumfang: zuerst Derivate, dann Makro, Blockchain-/Stablecoin-Flüsse, anschließend Nachrichten. Jeder Connector erhält Quellenblatt, Rechteprüfung, Zeitmodell, Rate-Limit- und Backfill-Verhalten.

**Abnahme:** Mehrere produktive Connectoren erweitern den Bestand. Mindestens ein priorisierter Connector durchläuft Import, Qualität und zeitlich sicheren Join; weitere Connectoren haben jeweils eigene Akzeptanzkriterien. „Alle Anbieter angebunden“ ist kein realistisches Sammelkriterium.

### AP 10 · Event- und Relationship-Engine

**Ziel:** Assets, Börsen, Wallets und Informationen zeitlich nachvollziehbar verknüpfen. **Abhängigkeit:** AP 09 und Entitymodell AP 03.

Lieferumfang: Eventtypen, zeitlich gültige Relationen, Quellenbelege und Konfidenz, Abfrage und Darstellung. **Abnahme:** Relation vor ihrer Bekanntheit nicht im historischen Lauf sichtbar; mehrdeutige Zuordnungen bleiben erkennbar; Ereigniskette wird nicht automatisch als Kausalität bezeichnet. Eine Graphdatenbank ist keine Vorbedingung.

### AP 11 · Echtzeit-Infrastruktur

**Ziel:** zuverlässige kontinuierliche Aufnahme und Live-Beobachtung. **Abhängigkeit:** mindestens ein AP-09-Connector, vorhandene Zeit-/Persistenzverträge.

Lieferumfang: persistenter Replaypfad, Reconnect/Backfill, Deduplikation, Lag-Monitoring, Live-/History-Cutover und Benachrichtigungen. **Abnahme:** Neustart verliert keine bestätigten Ereignisse im getesteten Fehlerprofil; Doppellieferung zählt nicht doppelt; Lücken werden erkannt und markiert; Orderbuchsequenzen nur bei tatsächlich unterstützter Quelle.

**M3:** Mehrere Informationsarten lassen sich gemeinsam auf Zeitachsen und in Beziehungen untersuchen. Live-Funktionen erfüllen ein explizit gemessenes Forschungs-Latenzprofil, kein HFT-Versprechen.

## 5. Phase 4 · Advanced Research

### AP 12 · Hypothesis & Experiment Manager

**Ziel:** aus Exploration nachvollziehbare Experimente machen. **Abhängigkeit:** MVP-Manifeste AP 06/08; Beziehungen optional.

Lieferumfang: Hypothesentext, erwartete Richtung/Horizont, Datenversionen, Suchhistorie, Ergebnisvergleich, Out-of-sample-Plan und Status. **Abnahme:** Hypothese vor bestätigendem Test fixierbar; wiederholter Lauf reproduzierbar; spätere Änderungen versioniert statt überschrieben.

### AP 13 · Automated Pattern Discovery

**Ziel:** statistisch auffällige Kandidaten systematisch finden. **Abhängigkeit:** AP 08, AP 12 und passende Quellen.

Lieferumfang: begrenzte Suchräume, Anzahl getesteter Kombinationen, Ressourcenbudgets, Mehrfachtestkontrolle und Kandidatenberichte. **Abnahme:** Nullkontrollen quantifizieren Zufallsfunde; Bericht zeigt Effektgröße, Stabilität, Unsicherheit, Suchumfang und ungesehene Prüfbereiche. Kein automatisches „Alpha“-Label aufgrund des besten In-sample-Scores.

### AP 14 · Strategy Research Integration

**Ziel:** Befunde in überprüfbare Strategieforschung überführen. **Abhängigkeit:** AP 12, Analyse-/Zeitverträge AP 08; AP 13 liefert optional Kandidaten.

Lieferumfang: Exportvertrag für Features, Ereignisse, Entscheidungen und Labels; Integration zu einer noch auszuwählenden Backtesting-Schnittstelle; Kosten-/Latenz-/Liquiditätsannahmen. **Abnahme:** Referenzhypothese wird mit Punkt-in-Zeit-Daten und realistischen Annahmen evaluiert; keine Echtgeldorder und keine Ausführungsrechte notwendig.

**M4:** SignalAtlas erzeugt überprüfbare Hypothesen, dokumentiert ihre Evidenz und übergibt sie reproduzierbar an Strategieforschung.

## 6. Abhängigkeiten und Umsetzungsschnitt

Kritischer erster Pfad: AP 01 → AP 02 → AP 03 → AP 04 → integrierte AP 05–08 → M2. AP 05 kann mit stabilen API-Mocks früher beginnen; ein vollständig vorgezogener Canvas ohne echten Datenpfad birgt Integrationsrisiko.

AP 09 versorgt AP 10/11; AP 12 baut auf Run-Manifesten auf; AP 13 benötigt AP 12, während AP 14 auch manuell formulierte Hypothesen aufnehmen kann. Dokumentation und Tests laufen in allen Phasen mit. Aufwandsschätzung erst nach AP 02/04 in kleinen, unabhängig abnehmbaren Issues; keine ausgedachten Personentage.

## 7. Datenquellen-Roadmap

Die folgenden Namen sind Kandidaten beziehungsweise Quellklassen, keine Zusage aktueller API-Verfügbarkeit, kostenloser Nutzung oder vollständiger historischer Abdeckung. Vor Auswahl werden offizielle Vertrags-/API-Dokumentation und tatsächliche Daten getestet. Dieser Plan enthält bewusst keine unbestätigten Preise oder Rate-Limits.

| Stufe | Daten | Mögliche Herkunft | Zentrale Prüfung |
|---|---|---|---|
| MVP | vorhandene OHLCV-Daten | lokaler Binance-/Kraken-Bestand | Herkunft, Format, Quote-Asset, Lücken, Candle-Ende |
| MVP | unregelmäßige Veröffentlichungsereignisse | synthetische Fixtures über separat registrierten Adapter | Entity-Bezug, Verfügbarkeit, Revisionen, Alignment und Darstellung |
| 1 | Funding, Open Interest, Basis | Börsen-APIs / lizenzierte Archive | predicted vs. realized, Einheit, Historientiefe |
| 2 | Makro und Releases | öffentliche Statistik-/Zentralbankquellen; Vintage-Archive | Referenzperiode, Releasekalender, Revisionen |
| 3 | Blockchain und Stablecoin-Flüsse | Nodes, Explorer oder Indexer | Chain-Reorgs, Finalität, Entity-Labels, Token-Decimals |
| 4 | DeFi | Protokollereignisse / geprüfte Aggregatoren | Protokollversion, Preisableitung, Duplikate |
| 5 | Nachrichten und Informationen | lizenzierte Feeds / erlaubte öffentliche Metadaten | Erstveröffentlichung, Updates, Nutzungsrechte, Zuordnung |
| später | Trades / Orderbücher | Venue-Streams und historische Archive | Sequenzlücken, Volumen, Replay, Netzwerklatenz |

### Quellenblatt pro Connector

Pflichtangaben: Anbieter/Quell-ID, Dokumentations-URL, Nutzungs-/Weiterverteilungsrechte mit Prüfdatum, Authentifizierung und Secret-Referenz, Datenarten, Instrumentabdeckung, historischer Zeitraum, Pagination, Limits, Cursor, Ausfallstrategie, Quellzeitdefinition, Revisionen, Präzision, Einheit, Qualitätsprüfung und verantwortliche Rolle. Fehlen historische Vintages, ist diese Einschränkung maschinenlesbar zu speichern.

Eine neue Quelle wird bevorzugt, wenn sie eine konkrete Forschungsfrage verbessert, historische Verfügbarkeit nachvollziehbar ist und Import/Betrieb finanziell wie technisch tragbar bleiben. Datenmenge allein ist kein Prioritätskriterium.

### Vorgeschlagene Umsetzungstickets

| Priorität | Ticket | Nachweis |
|---|---|---|
| P0 | ADR zu Quellen- und Handelsplatzunabhängigkeit | Plattformgrenzen und Pilotumfang sind dokumentiert |
| P0 | Connector-Fähigkeiten und Schemata | Metadaten, Zeitsemantik und Import-/Replay-Fähigkeiten sind versioniert |
| P0 | Kanonische Ereignisdaten | Synthetische Ereignisse durchlaufen Import, Snapshot und Abfrage mit Revisionen |
| P0 | Connector-Vertragstests | Gemeinsame Suite prüft Candle- und Event-Adapter |
| P1 | Heterogener Workspace-Abnahmelauf | Ereignisse und Kurszeitreihe sind zeitlich korrekt verknüpft und visualisiert |
| P1 | Katalog- und Abfragefilter | Datentyp, Quelle, Entity/Instrument, Zeitbereich, Qualität und Verfügbarkeit sind filterbar |
| P1 | Konsistenz der Release-Dokumentation | README, Scope und Roadmap beschreiben dieselbe Abnahme |
| P2 | Dokumentation für Veröffentlichung | Öffentliche Texte beschreiben die Projektgrundlage ohne interne Erstellungsmetadaten |
