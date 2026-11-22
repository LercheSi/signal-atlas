# 01 · Produktziel und Anforderungen

[Zur Übersicht](../README.md)

## 1. Status und Sprache der Anforderungen

**Kontextfestlegung** bezeichnet Ziele aus dem referenzierten Gespräch und der aktuellen Beauftragung. **Vorschlag** bezeichnet technisch konkretisierte Anforderungen, die vor der Implementierung bestätigt oder angepasst werden sollen. **Annahme** bezeichnet unbestätigte Rahmenbedingungen. **Offen** kennzeichnet Entscheidungen ohne Festlegung. In diesem Konzept beschreiben „muss“ und „darf nicht“ Zielanforderungen, keinen nachgewiesenen Implementierungsstand.

## 2. Vision und Nutzer

**Kontextfestlegung:** SignalAtlas ist ein Crypto Intelligence & Research Workspace. Der ursprüngliche Arbitrage-Kontext ist ein möglicher Forschungsfall; das Produkt ist breiter angelegt. Die Architektur soll später weitere Finanzmärkte aufnehmen können, ohne das MVP darauf auszudehnen.

**Annahme A-01:** Zunächst arbeitet eine technisch versierte Person lokal oder auf einem privaten Server mit vorhandenen historischen Daten. Ein öffentlich erreichbarer Mehrmandantendienst ist kein MVP-Ziel.

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
| F-01 | Datenkatalog für vorhandene OHLCV-Bestände | Inventarisierte unterstützte Binance-/Kraken-Reihen sind nach Instrument, Quelle, Intervall und Zeitraum auffindbar |
| F-02 | Einheitliche Abfrage | Dieselben Filter liefern unabhängig vom Ursprungsformat dasselbe kanonische Schema |
| F-03 | Mehrere Charts | Mindestens zwei Quellen gemeinsam sichtbar; Zoom und Cursor besitzen dieselbe UTC-Zeitbasis |
| F-04 | Node-Arbeitsfläche | Quelle → Transformation → Analyse → Chart ist verbindbar; unzulässige Typen und Zyklen werden abgewiesen |
| F-05 | Mindestanalysen | Deskriptive Statistik, Renditetransformation, Korrelation und Kreuzkorrelation/Lead-Lag mit explizitem Lag-Vorzeichen |
| F-06 | Parameterinteraktion | Änderungen erzeugen neuen Lauf oder validen Cachetreffer; ältere Ergebnisse überschreiben keine neueren |
| F-07 | Persistenz | Speichern, Schließen, Laden rekonstruiert Graph, Parameter, Datenreferenzen und Layout |
| F-08 | Herkunft | Jedes Ergebnis verweist auf Snapshot, Code-/Plugin-Version, Parameter und zeitliche Policy |
| F-09 | Zeitliche Sicherheit | Historischer Punkt-in-Zeit-Modus weist unbekannte Verfügbarkeit zurück oder markiert einen ausdrücklich gewählten Annahmemodus |
| F-10 | Export | Vorschlag: Ergebnisdaten plus Run-Manifest exportieren; Rechtebeschränkungen des Datensatzes beachten |

„Beliebige vorhandene Reihe“ bedeutet innerhalb der nach AP 02 bestätigten Formate und Instrumenttypen. Der Import unbekannter Formate wird nicht stillschweigend garantiert.

AP 08 hat einen größeren Zielumfang als F-05: Stationarität, Cointegration, Regression, Faktoren, Anomalien und Strukturbrüche sind geplante Module. **Offen D-08:** Welche davon blockieren M2? Vorschlag: MVP zunächst mit F-05 abnehmen und weitergehende Verfahren als getrennte Issues führen.

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

Ein versionierter synthetischer Datensatz enthält zwei Märkte mit absichtlich eingebautem Lag, einer Datenlücke, einem Duplikat und einer nachträglichen Korrektur. Der Import weist alle Besonderheiten aus. Die Arbeitsfläche berechnet Renditen und findet den erwarteten Lag innerhalb der festgelegten Testtoleranz. Ein ungültiger Join wird abgewiesen. Ein Lauf vor der Korrektur sieht deren neuen Wert nicht. Nach Speichern und Wiederladen ist das Run-Manifest identisch; Zahlen stimmen innerhalb dokumentierter numerischer Toleranzen überein. Eine Parameteränderung löst einen getrennten Lauf aus.

Zusätzlich wird derselbe Ablauf mit einem nach AP 02 ausgewählten realen Binance-/Kraken-Ausschnitt ausgeführt. Ein unbereinigter USD-/USDT-Preisvergleich darf keinen als Arbitrage interpretierbaren Spread ausgeben.

## 6. Spätere Funktionen und Nichtziele

Phase 3 ergänzt Datenvielfalt, Beziehungen und Live-Beobachtung. Phase 4 ergänzt Hypothesenverwaltung, systematische Suche und Übergabe an Backtests. Ein einfacher Run-Nachweis gehört bereits ins MVP; ein vollständiger Experiment Manager erst in AP 12.

Nicht Teil der ersten vier Phasen: autonome Echtgeldorders, Verwahrung von Vermögen, garantierte Handelsrenditen, vollständige globale Blockchain-Indexierung, verteiltes High-Frequency-Trading und die Behauptung von Kausalität allein aus Korrelation.
