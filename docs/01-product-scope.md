# 01 · Produktziel und Anforderungen

[Zur Übersicht](../README.md)

## 1. Status und Sprache der Anforderungen

**Kontextfestlegung** bezeichnet Ziele aus dem referenzierten Gespräch und der aktuellen Beauftragung. **Vorschlag** bezeichnet technisch konkretisierte Anforderungen, die vor der Implementierung bestätigt oder angepasst werden sollen. **Annahme** bezeichnet unbestätigte Rahmenbedingungen. **Offen** kennzeichnet Entscheidungen ohne Festlegung. In diesem Konzept beschreiben „muss“ und „darf nicht“ Zielanforderungen, keinen nachgewiesenen Implementierungsstand.

## 2. Vision und Nutzer

**Kontextfestlegung:** SignalAtlas ist ein modularer Arbeitsplatz für explorative Finanzmarkt- und Ereignisforschung. Die Architektur ist unabhängig von einzelnen Anbietern, Handelsplätzen, Instrumenten und Asset-Klassen. Kryptowährungen sind der erste fachliche Schwerpunkt. Binance und Kraken dienen als Pilotquellen. Börsenübergreifende Arbitrage ist ein möglicher Forschungsfall.

**Bestätigt A-01 / ADR-0001:** Zunächst arbeitet eine technisch versierte Person lokal mit vorhandenen historischen Daten. Ein öffentlich erreichbarer Mehrmandantendienst ist kein MVP-Ziel.

Primäre Arbeitsabläufe:

1. Eine Marktbeobachtung als Frage formulieren: „Gehen Renditebewegungen auf Markt A denen auf Markt B voraus?“
2. Geeignete Daten auswählen, Qualität, Einheiten und Zeitverfügbarkeit prüfen.
3. Transformationen und Analysen verbinden, Zeitfenster und Parameter variieren.
4. Befunde einschließlich Unsicherheit, Alternativerklärungen und Datenmängeln festhalten.
5. Den exakten Lauf reproduzieren und später mit neuen Daten erneut prüfen.

Der Workspace soll Exploration erleichtern, zugleich aber die Grenze zwischen explorativer Entdeckung und bestätigender Prüfung sichtbar machen.

## 3. MVP-Vertrag v0.1

| ID | Zielanforderung | Überprüfbare Abnahme |
|---|---|---|
| F-01 | Quellenübergreifender Katalog für unterstützte Datentypen | Binance-/Kraken-OHLCV und synthetische Ereignisse sind nach Quelle, Datentyp, Entity oder Instrument, Zeitbereich, Qualität und Verfügbarkeitsstatus auffindbar. Das Intervall ist für Candles filterbar |
| F-02 | Einheitliche Abfrage | Dieselben Filter liefern unabhängig vom Ursprungsformat dasselbe kanonische Schema je Datenart; Candle- und Event-Payloads bleiben getrennt |
| F-03 | Mehrere Charts | Mindestens zwei Quellen gemeinsam sichtbar; Zoom und Cursor besitzen dieselbe UTC-Zeitbasis |
| F-04 | Node-Arbeitsfläche | Quelle → Transformation → Analyse → Chart ist verbindbar; unzulässige Typen und Zyklen werden abgewiesen |
| F-05 | Mindestanalysen | Deskriptive Statistik, Renditetransformation, Korrelation und Kreuzkorrelation/Lead-Lag mit explizitem Lag-Vorzeichen |
| F-06 | Parameterinteraktion | Änderungen erzeugen neuen Lauf oder validen Cachetreffer; ältere Ergebnisse überschreiben keine neueren |
| F-07 | Persistenz | Speichern, Schließen, Laden rekonstruiert Graph, Parameter, Datenreferenzen und Layout |
| F-08 | Herkunft | Jedes Ergebnis verweist auf Snapshot, Code-/Plugin-Version, Parameter und zeitliche Policy |
| F-09 | Zeitliche Sicherheit | Historischer Punkt-in-Zeit-Modus weist unbekannte Verfügbarkeit zurück oder markiert einen ausdrücklich gewählten Annahmemodus |
| F-10 | Export | Im Event-Vertragstest lassen sich Ergebnisdaten und Run-Manifest unter Beachtung der Datenrechte exportieren. Der Umfang einer allgemeinen Exportfunktion bleibt ein Vorschlag |
| F-11 | Erweiterbarkeit der Datenquellen | Ein separater synthetischer Event-Adapter ergänzt die Pilotadapter per Konfiguration und Registrierung. Er verwendet die vereinbarten Schemata und benötigt keine Änderung am Query-/Research-Kern, Executor oder kanonischen Modell |
| F-12 | Heterogener Analysegraph | Unregelmäßige Ereignisse und OHLCV werden auf einer Zeitachse dargestellt und über einen expliziten Alignment-Node mit Richtung, Altersgrenze und Zeitpolicy für die Analyse verbunden |

Die unterstützten OHLCV-Formate und Instrumenttypen werden in AP 02 ermittelt. Das kanonische Event-Schema und der synthetische Adapter gehören zum Referenzumfang. Die produktive Anbindung weiterer Anbieter folgt in AP 09.

AP 08 hat einen größeren Zielumfang als F-05: Stationarität, Cointegration, Regression, Faktoren, Anomalien und Strukturbrüche sind geplante Module. **AP01-Vorschlag D-08:** M2 umfasst F-05 und die deskriptive Event-Renditezusammenfassung mit Cutoff-Prüfung aus F-12. Weitere Verfahren blockieren M2 nicht und erhalten getrennte Issues.

## 4. Nichtfunktionale Anforderungen

| ID | Anforderung | Nachweis |
|---|---|---|
| N-01 | Reproduzierbare Datensicht | Unveränderliches Manifest mit Hashes; Ergebnis verweist auf Manifest-ID |
| N-02 | Begrenzte Ressourcen | Größen-, Zeit- und Speicherlimits; Jobabbruch; keine vollständigen Massendaten im Browser |
| N-03 | Erklärbare Datenqualität | Lücken, Revisionen, Ausschlüsse und Imputation im Ergebnis sichtbar |
| N-04 | Erweiterbarkeit | Neue geprüfte Analyse über Registry und deklarierte Ports integrierbar |
| N-05 | Betriebssicherheit | Importwiederholung ohne Doppelzählung; Wiederherstellung aus Backup getestet |
| N-06 | Portabilität | Start mit Dateispeicher und wenigen Diensten; keine verpflichtende Cloud |
| N-07 | Interaktivität | Messbare Latenzbudgets auf definierter Referenzhardware; siehe Qualitätskonzept |

## 5. Konkreter MVP-Abnahmelauf

Ein versionierter synthetischer Datensatz enthält zwei Märkte mit absichtlich eingebautem Lag, einer Datenlücke, einem Duplikat und einer nachträglichen Korrektur. Der Import weist alle Besonderheiten aus. Die Arbeitsfläche berechnet Renditen und findet den erwarteten Lag innerhalb der festgelegten Testtoleranz. Ein ungültiger Join wird abgewiesen. Ein Lauf vor der Korrektur sieht deren neuen Wert nicht. Nach Speichern, Wiederladen und erneutem Ausführen stimmen die fachlichen Manifestangaben überein. Ergebniswerte stimmen innerhalb dokumentierter numerischer Toleranzen überein. Lauf-ID und Ausführungszeiten können sich unterscheiden. Eine Parameteränderung löst einen getrennten Lauf aus.

Zusätzlich wird derselbe Ablauf mit einem nach AP 02 ausgewählten realen Binance-/Kraken-Ausschnitt ausgeführt. Ein unbereinigter USD-/USDT-Preisvergleich darf keinen als Arbitrage interpretierbaren Spread ausgeben.

Ein zweiter Abnahmelauf kombiniert vorhandene Candles einer Pilotquelle mit synthetischen, unregelmäßig eintreffenden Makro-Veröffentlichungen. Der Adapter importiert sie ohne externen API-Zugang. Die Ereignisse tragen `event_time`, gegebenenfalls `published_at`, `observed_at`, `available_at` und die Grundlage der Verfügbarkeit. Die Arbeitsfläche zeigt Marker auf der gemeinsamen UTC-Achse und berechnet über einen expliziten Alignment-Node eine deskriptive Renditezusammenfassung zu den Ereignissen. Ein verspätet verfügbarer Datensatz und eine spätere Revision bleiben vor ihrem jeweiligen Cutoff aus der Analyse ausgeschlossen. Marker folgen der gewählten Sicht und geben ihren Zeitbezug an. Speichern, Laden und erneutes Ausführen reproduziert Datenstand, Zeitpolicy und Ergebnis innerhalb dokumentierter Toleranzen. Die Fünf-Minuten-Kennzahl verlangt einen am ersten Verfügbarkeitsanker bereits verfügbaren Close exakt am Anker und einen Close exakt fünf Minuten danach; ältere Baselines werden gekennzeichnet ausgeschlossen. Der Endkurs zählt erst ab eigener Verfügbarkeit. Spätere Ereignisrevisionen verschieben den ursprünglichen Anker nicht und zählen nicht erneut. Die konkreten Negativ- und Rechenfälle stehen im [AP01-Vertrag](08-ap01-contract.md#3-research-ablauf-b-ohlcv-und-veröffentlichungsereignisse). Eine reale Makro- oder Funding-Reihe kann den Vertragstest ergänzen.

## 6. Spätere Funktionen und Nichtziele

Phase 3 ergänzt Datenvielfalt, Beziehungen und Live-Beobachtung. Phase 4 ergänzt Hypothesenverwaltung, systematische Suche und Übergabe an Backtests. Ein einfacher Run-Nachweis gehört bereits ins MVP; ein vollständiger Experiment Manager erst in AP 12.

Nicht Teil der ersten vier Phasen: autonome Echtgeldorders, Verwahrung von Vermögen, garantierte Handelsrenditen, vollständige globale Blockchain-Indexierung, verteiltes High-Frequency-Trading und die Behauptung von Kausalität allein aus Korrelation.

## 7. AP01-Konkretisierung

Der [AP01-Vertrag](08-ap01-contract.md) konkretisiert beide Research-Abläufe, Schnittstellen, Modulgrenzen, numerische Toleranzen und die Übergabe. Technische ADRs sind Vorschläge zur Abnahme. Softwaretests und Benchmarks werden erst in den nachfolgenden Arbeitspaketen ausgeführt.
