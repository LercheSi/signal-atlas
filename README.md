# SignalAtlas

**Explore Data. Discover Connections.**

Modularer Research Workspace für explorative Finanzmarkt- und Ereignisforschung mit Kryptowährungen als erstem fachlichen Schwerpunkt.
SignalAtlas verbindet historische Marktdaten mit später hinzukommenden Derivate-, Makro-, On-Chain- und Ereignisdaten. Forschende stellen Datenquellen, Transformationen, statistische Verfahren und Visualisierungen auf einer gemeinsamen Arbeitsfläche zusammen und untersuchen überprüfbare Hypothesen.

> **Projektstatus: Foundation / AP02 in Umsetzung, Stand 22. November 2026.** Die Forschungsanwendung ist noch nicht implementiert. Ein eigenständiges [AP02-Inventurwerkzeug](docs/09-ap02-inventory.md) ist ausführbar; der reale Vollscan und seine Abnahme stehen noch aus. Die Technologien und Detailverträge sind teilweise Architekturvorschläge; ihr Status steht im [Entscheidungsregister](docs/07-decisions-risks.md).

## Ziel und Abgrenzung

Der Plattformkern ist unabhängig von Datenanbietern, Handelsplätzen, Instrumenten und Asset-Klassen konzipiert. Versionierte Connector-Verträge ermöglichen die Integration weiterer Quellen. Vorhandene Binance- und Kraken-Zeitreihen dienen als Pilotdaten für reproduzierbare Analysen. Der Mensch formuliert Fragen, variiert Parameter, vergleicht Ergebnisse und beurteilt deren Aussagekraft. Auffällige Korrelationen sind Forschungsbefunde und noch keine profitablen Handelssignale.

Automatische Mustererkennung und die Übergabe an Strategieforschung folgen später. Autonomes Echtgeld-Trading gehört ausdrücklich nicht zu den vier geplanten Phasen. Eine Ausführungsengine wäre ein getrenntes Modul mit eigenem Risikomodell.

## Research MVP v0.1

- Unterstützte Datensätze über einen gemeinsamen Katalog auswählen. Binance und Kraken liefern die OHLCV-Referenzdaten. Synthetische, unregelmäßige Ereignisse bilden den zweiten Referenzdatentyp.
- Mindestens zwei Zeitreihen anzeigen und ihre Zeitachsen synchron zoomen.
- Quellen, Transformationen, Analysen und Charts als Nodes verbinden.
- Korrelation und Lead-Lag untersuchen, Parameter ändern und Ergebnisse neu berechnen.
- Ereignisse mit Kurszeitreihen über eine explizite Zeitregel verknüpfen und als Marker anzeigen.
- Arbeitsflächen speichern und wiederherstellen.
- Datenherkunft, Datenversion, Zeitannahmen und Analyseparameter nachvollziehen.

Das MVP erfordert weder vollständige On-Chain-Integration noch KI-Agenten, Tick-Orderbücher oder Live-Ausführung. Vollständige statistische Verfahren aus AP 08 können nach dem ersten MVP schrittweise folgen; die genaue Mindestmenge ist in [Scope und Anforderungen](docs/01-product-scope.md) abgegrenzt.

| Architekturziel | Referenzumfang v0.1 |
|---|---|
| Mehrere Handelsplätze und Anbieter | Binance- und Kraken-Importadapter und ein separater synthetischer Event-Adapter |
| Heterogene Daten | OHLCV-Zeitreihen und unregelmäßige Ereignisse |
| Erweiterbare Analysen | Versionierter Plugin-Vertrag und geprüfte Basisanalysen |
| Weitere Finanzmärkte | Marktübergreifendes Datenmodell, erster fachlicher Schwerpunkt Krypto |

## Technische Richtung

| Bereich | Geplante Grundlage |
|---|---|
| Analyse und Import | Python, Polars, DuckDB |
| Historische Massendaten | versionierte Parquet-Dateien, Raw / Normalized / Derived |
| Metadaten und Arbeitsflächen | PostgreSQL |
| Weboberfläche | React / TypeScript |
| Ausführung | API und getrennte Analyse-Worker |
| Erweiterbarkeit | versionierte Connector- und Analyseverträge |
| Spätere Optionen | Rust/C++, persistenter Event-Stream, TimescaleDB, ClickHouse |

Browser-Nodes beschreiben den Analysegraphen. Große Berechnungen laufen auf dem Backend. „Node-basiert“ bezeichnet die visuelle Arbeitsfläche, keine Entscheidung für Node.js als Analyse-Backend.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [Scope und Anforderungen](docs/01-product-scope.md) | Zielgruppen, Anwendungsfälle, MVP, Nichtziele, Abnahme |
| [Systemarchitektur](docs/02-architecture.md) | Komponenten, Abläufe, Speicher, Deployment und Skalierung |
| [Daten- und Zeitmodell](docs/03-data-temporal-model.md) | Schemas, Revisionen, Verfügbarkeit, As-of-Joins, Look-ahead-Schutz |
| [Workspace, API und Plugins](docs/04-workspace-api-plugins.md) | DAG, Jobs, Schnittstellen, Erweiterungen, Reproduzierbarkeit |
| [Qualität, Performance und Betrieb](docs/05-quality-operations.md) | Teststrategie, Forschungsqualität, Benchmarks und Wiederherstellung |
| [Roadmap und Datenquellen](docs/06-roadmap-sources.md) | 14 Arbeitspakete, vier Phasen, Abhängigkeiten und Connector-Roadmap |
| [Entscheidungen und Risiken](docs/07-decisions-risks.md) | Herkunft, Annahmen, offene Entscheidungen, Risiko- und ADR-Register |

Für AP01: [Vertrag und Übergabe](docs/08-ap01-contract.md), [Domänenbegriffe](CONTEXT.md) und [Entscheidungsregister](docs/07-decisions-risks.md). AP01 wurde am 22. November 2026 abgenommen.

Empfohlener Einstieg: Scope → Architektur → Datenmodell → Roadmap. Für die Umsetzung sind zusätzlich die API-Verträge und das Entscheidungsregister maßgeblich.

## Entwicklungsstart

1. AP 01: MVP-Scope, Quellenunabhängigkeit, Connector-Grenzen und Zeitsemantik als ADRs bestätigen.
2. AP 02: Originaldaten unverändert inventarisieren; Formate, Größen und Qualität messen.
3. AP 03: Den reproduzierbaren Import- und Snapshot-Pfad mit OHLCV und synthetischen Ereignissen umsetzen.
4. AP 04: Einen vertikalen Pfad von der Datenabfrage bis zur Lead-Lag-Analyse benchmarken.
5. AP 05–08: Diesen Pfad über die speicherbare Arbeitsfläche zugänglich machen.

Installation, CLI-Aufruf und Projektprüfungen des Inventurwerkzeugs stehen in der [AP02-Anleitung](docs/09-ap02-inventory.md). Startbefehle für die Forschungsanwendung folgen mit deren Umsetzung.

## Mitarbeit und Lizenz

Beiträge sollen kleine, überprüfbare Schritte mit dokumentiertem Datenvertrag, nachvollziehbaren Ergebnissen und passenden Tests liefern. Architekturänderungen erhalten ein ADR. Synthetische Testdaten gehören ins Repository; private, große oder nicht weiterverteilbare Quelldaten nicht.

**Offen:** Open-Source-Lizenz, Governance, Contribution-Prozess und Security-Kontakt. Dieses Dokument vergibt selbst keine Softwarelizenz. Nutzungsrechte an Marktdaten sind gesondert zu prüfen; eine offene Softwarelizenz erlaubt nicht automatisch deren Weiterverteilung.
