# 07 · Annahmen, Entscheidungen und Risiken

[Zur Übersicht](../README.md)

## 1. Herkunft und Vollständigkeit

Entwurfsgrundlage sind die Projektanforderungen und Architekturgespräche vom November 2026. Die Dokumentation beschreibt das Zielsystem. Der Status jeder Architekturentscheidung steht im folgenden Register.

Der reale Datenbestand, die konkreten Providerverträge und die Hardwareleistung sind zu prüfen. Dateiformate, Benchmarkbudgets sowie API-, Plugin-, Commit- und Jobverträge werden bei Inventur, Implementierung und Prototyping validiert.

## 2. Statusmodell

- **K – Kontextfestlegung:** aus Beauftragung oder Referenzgespräch übernommen; keine Behauptung vorhandener Umsetzung.
- **V – Vorschlag:** technisch begründete Konkretisierung; vor Implementierung als ADR bestätigen oder ändern.
- **A – Annahme:** unbestätigte Rahmenbedingung; durch Inventur/Prototyp prüfen.
- **O – Offen:** Alternativen oder Freigabe fehlen; Entscheidungskriterium ist benannt.

## 3. Architekturentscheidungen

| ID | Status | Entscheidung / Frage | Begründung oder nächster Nachweis |
|---|---|---|---|
| D-01 | K | Exploration und Crypto Intelligence zuerst | MVP-Ziel; keine autonome Ausführung |
| D-02 | K | Parquet / DuckDB / Polars als Forschungsgrundlage | Gesprächsrichtung; Lastprofil in AP 04 validieren |
| D-03 | K | PostgreSQL für Katalog und Arbeitsflächen | Transaktionale Metadaten getrennt von historischem Lake |
| D-04 | O/V | Konkreter Jobrunner; Vorschlag DB-Queue mit Leases | Restart, Claim, Abbruch, Fairness und Idempotenz prototypisieren |
| D-05 | K/V | Python, React/TypeScript; modularer Kern | Stack vorgegeben; Frameworks und Versionspins offen |
| D-06 | K/O | Live modular; NATS/TimescaleDB/ClickHouse optional | Auswahl erst nach Last-/Recoverynachweis |
| D-07 | K/V | Vier Zeitstempel; zwei Replayperspektiven | Grundmodell aus Kontext, Detailpolicy hier konkretisiert |
| D-08 | O | Vollständiger AP-08-Umfang für M2 | MVP-Minimum vorgeschlagen; weitere Statistik priorisieren |
| D-09 | O | Lizenz, Governance, Contribution und Security-Kontakt | Vor öffentlicher Veröffentlichung klären |
| D-10 | O | Chart-/Canvasbibliothek, Python-Webframework | Lizenz, Wartbarkeit, große Graphen/Daten, Accessibility testen |
| D-11 | O | Backup, RPO/RTO, Retention und Speicherbudget | AP 02 ermittelt Größe; Restore vor M1 nachweisen |
| D-12 | V | Unveränderliche Snapshots plus Manifest-Commit | Verhindert halbe Imports und wandernde Datenstände |
| D-13 | O | Verfügbarkeitsannahmen je historischer Quelle | Ohne belegte Vintages kein striktes Markt-Replay behaupten |
| D-14 | O | Authentifizierung und Mehrnutzerbetrieb | Lokaler Start angenommen; Hosting ändert Bedrohungsmodell |
| D-15 | O | Native Module und zusätzliche Stores | Erst nach reproduzierbarem Profiling entscheiden |
| D-16 | O | Backtesting-Integrationsziel | AP 14 anhand Zeitmodell, Kosten und Exportvertrag auswählen |
| D-17 | O | Name/Repository/Markenverfügbarkeit | SignalAtlas ist Arbeitsname; keine Verfügbarkeitsprüfung erfolgt |
| D-18 | V | Anbieter- und Handelsplatzunabhängigkeit | Binance und Kraken sind Pilotadapter. Der Kern verwendet kanonische Typen, stabile IDs und deklarierte Fähigkeiten |
| D-19 | O | Heterogener MVP-Demonstrator | Synthetische unregelmäßige Ereignisse als Referenzfall vorgesehen. Eine reale Makro- oder Funding-Reihe ist optional und hängt von Aufwand und Nutzungsrechten ab |
| D-20 | O/V | Granularität des Connector-Vertrags | Gemeinsame Metadaten und deklarierte Fähigkeiten mit datenartspezifischen Payloads. Die Vertragstests konkretisieren den Umfang |

Kein Eintrag mit Status V oder O wird durch Erwähnung in einem Diagramm zu einer endgültigen Festlegung. Ansprechpartner sind derzeit Rollen, keine erfundenen Personen: Architekturverantwortung, Datenverantwortung, Research-Verantwortung und Betrieb. Ihre tatsächliche Besetzung ist vor der Umsetzung zu dokumentieren.

## 4. Annahmenregister

| ID | Annahme | Prüfung und Konsequenz |
|---|---|---|
| A-01 | Einzelner lokaler/private-server Research-Nutzer zuerst | In AP 01 bestätigen; sonst Auth, Rechte und Parallelität neu planen |
| A-02 | Binance-/Kraken-OHLCV-Bestand ist verfügbar | AP 02 prüft Zugriffsorte/Formate; fehlender Bestand erfordert Beschaffung |
| A-03 | Einzelner Rechner reicht für erstes Profil | AP 04 misst RAM/Scan/Join; bei Nichterfüllung Datenlayout/Scope anpassen |
| A-04 | Historische Verfügbarkeit ist teilweise unbekannt | Quellenblatt und Zeitpolicy; Ergebnisse entsprechend kennzeichnen |
| A-05 | Datenrechte erlauben lokale Forschung | Je Quelle prüfen; Öffentlichkeit/Weiterverteilung separat bewerten |
| A-06 | Fachliche Plugins werden anfangs geprüft installiert | Fremdcodebetrieb braucht Isolation und neuen Freigabeprozess |

## 5. Risikoregister

Bewertungen sind qualitative Planungseinschätzungen ohne empirische Eintrittswahrscheinlichkeit.

| Risiko | Auswirkung | Frühes Signal | Maßnahme / Verantwortung |
|---|---|---|---|
| Look-ahead durch Candle-/Release-/Revisionszeiten | unbrauchbare Forschung | Ergebnisse ändern sich rückwirkend | Zeitvertrag, Cutoff-Tests, Vintages; Daten/Research |
| USD/USDT oder Kontrakte verwechselt | falsche Spreads/Beziehungen | große venueabhängige Abweichung | Instrument-/Einheitenmodell, explizite Umrechnung; Daten |
| Data Snooping / multiples Testen | Zufallsfunde als Entdeckung | nur bestes In-sample-Ergebnis berichtet | Suchregister, Nulltests, getrennte Bestätigung; Research |
| Unvollständiger Raw-Bestand | Ergebnisse nicht reproduzierbar | fehlende Hashreferenzen | unveränderte Originale, Snapshotprüfung, Backup; Daten/Betrieb |
| Provider-Ausfälle, Limits, wechselnde Formate | Lücken oder Kosten | steigender Aufnahmeverzug/Schemafehler | versionierte Connectoren, Backoff, Quarantäne; Daten |
| Lizenz- oder Weiterverteilungsproblem | eingeschränkte Veröffentlichung | unklare Nutzungsbedingungen | Quellenblatt, keine automatische Rohdatenpublikation; Projektleitung |
| Börsenspezifische Annahmen im Plattformkern | Neue Quellen erfordern Kernänderungen | Event-Import verlangt Candle-Felder oder einen Venue | Vertrags- und Provider-Wechseltests; Architektur/Daten |
| Zu viele Dateien oder zu breite Scans | schlechte Interaktivität | Metadaten-/IO-Zeit dominiert | Partitionbenchmark, Compaction, Projektion; Architektur |
| Worker-Überlast / RAM-Spitzen | Abstürze, blockierte UI | Queuealter und OOM | Quoten, getrennte Kapazität, Spill/Abbruch; Betrieb |
| Cache mit falscher Identität | veraltete oder falsche Resultate | trotz Datenänderung gleiche Ergebnisse | vollständiger semantischer Key, Invalidationtests; Architektur |
| Überladener Technologie-Stack | hoher Wartungsaufwand | mehrere Stores ohne Messgrund | wenige Basiskomponenten, Erweiterung nur mit ADR; Architektur |
| Fremdplugin mit Dateisystem-/Netzzugriff | Geheimnisverlust oder Manipulation | unkontrollierte Seiteneffekte | geprüfte Allowlist, später echte Isolation; Betrieb |
| Chain-Reorg / nachträgliche Entity-Labels | historische Fehlinterpretation | wechselnde Zuordnung/Finalität | Revisionen, Bekanntheitszeit, Konfidenz; Daten |
| Canvas wird vor Datenpfad optimiert | schönes UI ohne belastbaren Nutzen | Graph ausführbar nur mit Mocks | früher vertikaler Researchpfad; Produkt/Architektur |
| Reproduzierbarkeit alter Environments | Ergebnisse später nicht mehr ausführbar | fehlende Locks/Artefakte | Environment-ID, archivierte Manifeste, Referenzruns; Betrieb |

## 6. ADR-Verfahren

Vorschlag: Entscheidungen unter `docs/adr/NNNN-kurztitel.md` ablegen. Ein ADR beschreibt Kontext, Status, Alternativen, Entscheidung, Konsequenzen, Evidenz und Überprüfungsauslöser. Änderungen ersetzen alte ADRs durch Nachfolger statt ihre Historie zu löschen.

Erste ADRs: MVP-Grenzen; Anbieter- und Handelsplatzunabhängigkeit; Connector-Fähigkeiten und Datenmodalitäten; Zeit-/Verfügbarkeitspolicies; Snapshot-Commit; Prozess-/Jobmodell; Plugin-Vertrauen; Bibliotheks-/Laufzeitversionen; Lizenz. Das vorliegende Register ersetzt noch keine bestätigten ADRs.

```text
Titel / ID:
Status: proposed | accepted | superseded
Datum und verantwortliche Rolle:
Kontext und konkrete Frage:
Alternativen:
Entscheidung und Gründe:
Folgen und Grenzen:
Mess-/Testnachweis:
Überprüfungsauslöser / Nachfolge-ADR:
```

## 7. Quellen und Pflege

Projektgrundlage sind die Anforderungen und Architekturgespräche vom November 2026. Externe technische Referenzen wurden zur Erstellung am 22. November 2026 eingesehen:

- [DuckDB: FROM und As-of-Joins](https://duckdb.org/docs/stable/sql/query_syntax/from) – grundlegende zeitliche Join-Syntax.
- [Polars: Joins](https://docs.pola.rs/user-guide/transformations/joins/) – Gruppierung und As-of-Verknüpfung.
- [Polars: Lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/) – Planbildung und Optimierung als Grundlage für den Prototyp.
- [PostgreSQL: SET TRANSACTION](https://www.postgresql.org/docs/current/sql-set-transaction.html) – Transaktionssicht für Metadaten; keine Garantie für externe Dateien.

Die Links unter `stable`/`current` können sich ändern. Die Implementierung muss tatsächliche Versionen pinnen, API-Kompatibilität testen und Quellenblatt/ADRs mit Prüfdatum fortführen. Dieser Entwurf setzt keine unüberprüften Mindestversionen voraus.

Pflegeanlässe: veränderte Zeitsemantik, neue Datenquelle, neue Plugin-API, öffentliches Hosting, nachgewiesener Performanceengpass und Scopeänderung. README und Scope werden gemeinsam aktualisiert, damit geplante und bereits ausgelieferte Funktionen später klar unterscheidbar bleiben.
