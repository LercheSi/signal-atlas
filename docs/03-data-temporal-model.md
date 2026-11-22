# 03 · Datenarchitektur und zeitliches Modell

[Zur Übersicht](../README.md)

## 1. Datenebenen und Identitäten

**Raw:** unveränderte Quelldateien beziehungsweise Originalantworten einschließlich Abrufmetadaten und Prüfsummen. Geheimnisse werden nicht als Teil von HTTP-Headern archiviert. **Normalized:** kanonische, geprüfte Fakten ohne Verlust der Referenz zur Rohquelle. **Derived:** Transformationen, Features und Ergebnisse mit vollständiger Lineage.

Assets erhalten stabile interne IDs. Instrumente beschreiben zusätzlich Venue, Marktart, Base-/Quote-Asset, Settlement-Asset, Kontraktmultiplikator und Gültigkeitszeitraum. Symbole sind zeitlich gültige Aliase. `BTC/USDT` auf Binance und `BTC/USD` auf Kraken sind verschiedene Instrumente. Spot, Perpetual und Futures dürfen nicht allein über das Tickersymbol zusammengeführt werden.

**Vorschlag:** UUIDs oder gleichwertige stabile IDs für interne Identitäten; Quell-IDs bleiben separat erhalten. Jede Tabelle trägt eine Schemaversion. Einheiten sind explizit: Basisvolumen, Quotevolumen, Funding pro Periode, Preis in Quote pro Basiseinheit. Decimal-Skalierung beziehungsweise Integer-Ticks bewahren Quellpräzision; statistische Arrays dürfen nach dokumentierter Konvertierung Float64 verwenden.

| Identität | Bedeutung | Beispiel |
|---|---|---|
| `provider_id` | Organisation oder System, das Daten bereitstellt | Statistikamt |
| `source_id` | Konkreter Ursprung oder Importkanal | Veröffentlichungsfeed oder Dateiarchiv |
| `venue_id` | Handelsplatz des Instruments, soweit fachlich vorhanden | Binance, Kraken |
| `instrument_id` | Konkretes handelbares Instrument | BTC/USDT Spot auf Binance |
| `entity_id` | Fachlicher Bezug eines Datensatzes | Bitcoin, Zentralbank oder US-Leitzins |
| `dataset_id` | Logische Reihe oder Sammlung | BTC-Candles oder Makro-Veröffentlichungen |
| `snapshot_id` | Unveränderlicher Stand eines Datensatzes | Versionierter Importstand |

Makroereignisse können über eine Entity referenziert werden. Venue, Instrument, Base-/Quote-Asset, Candle-Intervall und Preis sind nur Pflichtfelder der jeweils passenden Datentypen. Historische Abfragen binden die Mapping-Version für Quell- und Instrumenten-Aliase, damit eine spätere Katalogänderung eingefrorene Läufe nicht rückwirkend verändert.

## 2. Gemeinsame Ereignishülle

Die folgenden Felder sind ein Zielvertrag, keine Forderung nach einer einzigen universellen physischen Tabelle. Typspezifische Tabellen teilen diese Semantik.

| Feld | Bedeutung und Regel |
|---|---|
| `record_id` | Identität einer unveränderlichen Revision |
| `logical_id` | Identität des fachlichen Fakts über Revisionen hinweg |
| `source_id`, `source_record_id` | Herkunft und optionale Quellidentität |
| `dataset_id` | Logische Reihe oder Sammlung im Katalog |
| `instrument_id` / `entity_id` | Fachliche Zuordnung; typabhängig |
| `event_time` | Zeitpunkt des Ereignisses bzw. fachlicher Referenzzeitpunkt |
| `published_at` | Zeitpunkt der Veröffentlichung dieser Revision; nullable |
| `observed_at` | Tatsächlicher Empfang durch unseren Collector; niemals rückdatieren |
| `available_at` | Frühester nutzbarer Zeitpunkt nach expliziter Verfügbarkeitspolicy; nullable, wenn unbekannt |
| `availability_basis` | `observed`, `source_vintage`, `estimated` oder `unknown` |
| `availability_policy_id` | Version und Annahmen der Ableitung |
| `revision`, `supersedes_record_id` | Reihenfolge/Verweis für Änderungen |
| `ingest_batch_id`, `raw_ref` | Aufnahme und Referenz zur Rohquelle |
| `schema_version`, `quality_flags` | Struktur und maschinenlesbare Qualitätskennzeichen |

Alle Zeitpunkte sind UTC-Instants. Vorschlag: Mikrosekundenpräzision als Mindestvertrag, bei Tickquellen erweiterbar; Originalwert, Einheit und Genauigkeit bleiben erhalten. UTC-Zeit und lokale Anzeigezone sind getrennt. Fehlende Quellpräzision darf nicht durch erfundene Nachkommastellen als Messgenauigkeit erscheinen. Zeitintervalle verwenden `[start, end)`.

## 3. Vier Zeiten und zwei historische Perspektiven

Beispiel: Ein Makrowert bezieht sich auf Januar (`event_time`), wird am 5. Februar um 13:30 veröffentlicht (`published_at`) und um 13:30:02 vom laufenden Collector empfangen (`observed_at`). Bei einer angenommenen internen Nutzbarkeitsverzögerung von einer Sekunde liegt `available_at` für den eigenen historischen Systembetrieb frühestens bei 13:30:03. Eine Revision im März wird als neuer Record gespeichert und darf einen Februar-Lauf nicht rückwirkend verändern.

Es gibt keine pauschale Gleichheit der Zeitfelder:

- **System-Replay:** Was hätte unser tatsächlich laufendes System gewusst? Frühestens Empfang, relevante Veröffentlichung und abgeschlossene Verarbeitung berücksichtigen. Nachträglich importierte Daten waren diesem System damals nicht bekannt.
- **Historische Marktsicht:** Was war einem Marktteilnehmer nachweislich zugänglich? Source-Vintages/Archivstände plus dokumentierte Latenzannahme verwenden. Der heutige Downloadzeitpunkt ist nicht die damalige Marktverfügbarkeit.
- **Explorative Sicht ohne Verfügbarkeitsnachweis:** Daten sind analysierbar, aber nicht als Punkt-in-Zeit-sicher zu kennzeichnen.

`observed_at` eines heutigen historischen Downloads bleibt heute. Historische Verfügbarkeit wird separat als `source_vintage` oder `estimated` beschrieben. Unknown wird nicht durch `event_time` ersetzt. Die gewählte Sicht ist Teil von Query, Run-Manifest und Cache-Key. Strikte Läufe lehnen unbekannte Verfügbarkeit ab; ein Annahmemodus muss ausdrücklich gewählt und im Export sichtbar sein.

## 4. Kanonische Candles

| Feldgruppe | Zielfelder |
|---|---|
| Identität | `source_id`, `instrument_id`, `interval`, `bar_start`, `bar_end` |
| Werte | `open`, `high`, `low`, `close`, `base_volume`, optional `quote_volume`, `trade_count` |
| Zustand | `is_final`, `quality_flags`, gemeinsame Ereignishülle |

Vorschlag: `event_time = bar_end`; `bar_start` bleibt separat erhalten. Eine Candle für `[10:00, 10:01)` ist erst ab ihrem Schluss plus Veröffentlichung/Nutzbarkeit vollständig bekannt. Close, High, Low und Gesamtvolumen dürfen keinem Entscheidungszeitpunkt innerhalb dieser Minute zugeordnet werden. Laufende Candles sind eigene vorläufige Revisionen; sie werden nicht stillschweigend mit finalen Candles vermischt.

Fachlicher Schlüssel: Quelle, Instrument, Intervall, Bar-Start und Datenvariante. Identische Wiederholungen sind Duplikate, unterschiedliche Werte unter demselben Schlüssel Korrekturen oder Konflikte. Regeln wie `low <= open/close <= high`, nichtnegative Volumina, korrekte Intervalllänge und monotone Zeitbereiche werden geprüft. Ein Ausreißer ist zunächst ein Qualitätsflag, keine automatische Löschung.

## 5. Weitere Datentypen

| Typ | Zusätzliche Semantik |
|---|---|
| Trades | Trade-ID, Preis, Menge, Aggressorseite soweit bekannt; nicht aus Empfangsreihenfolge auf Ereignisreihenfolge schließen |
| Funding | Rate, Bezugsperiode, Settlement-Zeit; vorhergesagte und realisierte Rate getrennt |
| Open Interest | Kontrakte oder Nominalwert samt Einheit und Multiplikator |
| Makro | Referenzperiode, Release, Vintage und Revisionshistorie |
| On-Chain | Chain-ID, Blockhöhe/-hash, Logindex, Finalitätszustand; Reorg als Revision/Rücknahme |
| Nachrichten | Erstveröffentlichung, Update, Empfang, Entity-Zuordnung und Quellrecht; keine erfundene Originalverfügbarkeit |
| Beziehungen | Subjekt, Relation, Objekt, fachliche Gültigkeit, Bekanntheitszeit und Zuordnungskonfidenz |

Eine Beziehung wie „Wallet gehört zu Exchange X“ darf in historischen Analysen erst ab ihrer damaligen Bekanntheit verwendet werden. Das gilt auch für später erkannte Token-Aliase und rückwirkende Entity-Labels.

Für den synthetischen Event-Adapter sieht der MVP einen Datentyp für Veröffentlichungsereignisse vor. Er kombiniert die gemeinsame Ereignishülle mit Ereignistyp und Entity-Bezug sowie optionalen strukturierten Attributen mit deklarierter Einheit. Ereignisse können unregelmäßig auftreten. Die Abfrage erhält Originalzeitpunkte und Revisionsinformationen.

## 6. Punkt-in-Zeit-Abfragen und Revisionen

Für den Entscheidungszeitpunkt `t` sind nur Revisionen zulässig, deren `available_at <= t` gilt. Je fachlichem Fakt ist die letzte damals bekannte Revision auszuwählen; eine spätere Korrektur darf die frühere Revision erst ab ihrem eigenen Verfügbarkeitszeitpunkt ersetzen. Fachliche Gültigkeit und Bekanntheitszeit sind getrennte Dimensionen.

Ein As-of-Join allein löst das Revisionsproblem nicht. Bei revidierbaren Ereignisreihen wird zuerst der bekannte Zustand je `logical_id` rekonstruiert und danach nach fachlichem Zeitpunkt und zulässigem Alter verknüpft. Ein heutiger „latest“-Datensatz ist kein gültiger Ersatz für Vintages.

Für einfache, nicht revidierte Zustandsupdates eignet sich folgende schematische DuckDB-Abfrage:

```sql
SELECT d.decision_at, d.instrument_id,
       CASE WHEN d.decision_at - f.available_at <= INTERVAL '8 hours'
            THEN f.rate ELSE NULL END AS funding_rate
FROM decisions d
ASOF LEFT JOIN funding_state_updates f
  ON d.instrument_id = f.instrument_id
 AND d.decision_at >= f.available_at;
```

Voraussetzungen: `funding_state_updates` ist eine bereits validierte Zustandsreihe ohne mehrdeutige gleiche Verfügbarkeitszeiten, nach identischer Policy; NULL-Verfügbarkeit wurde ausgeschlossen und gemeldet. Acht Stunden sind nur ein Beispiel, keine universelle Funding-Regel. Der JOIN erhält nicht zugeordnete linke Zeilen. Alter wird auf dem gefundenen Zustand geprüft; eine nachgeschaltete WHERE-Bedingung könnte unbeabsichtigt linke Zeilen entfernen. Die Grundsyntax entspricht [DuckDB As-of-Joins](https://duckdb.org/docs/stable/sql/query_syntax/from).

Für belastbare Analysen sind häufig zwei Altersgrenzen nötig: seit Bekanntheit und seit fachlichem Ereignis. Ein gerade publizierter alter Referenzwert ist aktuell bekannt, aber fachlich möglicherweise veraltet. Gruppenidentität, Tie-Breaker, Toleranz und Gleichheitsregel (`<=` oder `<`) sind explizit zu versionieren. Bei fehlender gesicherter Reihenfolge am gleichen Zeitpunkt gilt ein konservativer Cutoff oder eine Sequenznummer.

Für den AP01-Ereignisablauf bleibt der Anker die belegte Erstverfügbarkeit des fachlichen Ereignisses unter der gebundenen Policy. Eine spätere Ereignisrevision ändert nur die ab ihrem Cutoff sichtbaren Attribute, nicht diesen Anker oder die Anzahl unabhängiger Ereignisse. Die Fünf-Minuten-Rendite verlangt einen am Anker verfügbaren finalen Close exakt am Anker und einen finalen Close exakt bei Anker plus fünf Minuten. Ältere Baseline-Kandidaten werden mit Alter und Ausschlussgrund ausgewiesen; keine Auffüllung. Der Endkurs ist erst ab eigener Verfügbarkeit auswertbar. Gebundene Kursrevisionen werden nicht still überschrieben; korrigierte Kursauswertungen benötigen einen expliziten neuen Run. Siehe [AP01-Referenzfälle](08-ap01-contract.md#3-research-ablauf-b-ohlcv-und-veröffentlichungsereignisse).

## 7. Resampling und Look-ahead-Schutz

- Zeitraster und Join erst im Analysekontext wählen; Originalzeitpunkte bleiben erhalten.
- OHLCV-Aggregation verwendet Intervallgrenzen: Open zuerst, High Maximum, Low Minimum, Close zuletzt; Volumen nur innerhalb passender Einheiten summieren.
- Forward-Fill nur für zulässige Zustandsgrößen mit Maximalalter und Flag; keine synthetischen Trades oder unbegrenzt fortgeschriebenen Volumina.
- Backward-Fill, zentrierte Rolling Windows und globale Standardisierung sind in strikt kausalen Featurepfaden verboten.
- Rolling Features verwenden nur damalige Eingaben; Skalierer und Modelle werden nur auf Trainingsfenstern gefittet.
- Abgeleitete Werte erhalten die späteste Eingangsverfügbarkeit plus dokumentierte Berechnungs-/Publikationslatenz, soweit der gewählte Modus dies verlangt.
- Labels und zukünftige Renditen dürfen für Evaluation existieren, bleiben aber typisiert von historischen Features getrennt.
- FX-/Stablecoin-Umrechnung verwendet eine eigene zeitlich verfügbare Reihe; USDT wird nicht als garantiert gleich USD behandelt.

## 8. Datenqualität und Manifest

Jeder Import erzeugt Bericht und Manifest: Dateihashes, Bytes, Quellformat, Zeilenzahl, Min-/Max-Zeiten, Instrumente, erwartete Intervalle, Lücken, Duplikate, Konflikte, ausgeschlossene Datensätze und Normalizer-Version. Lücken können Nicht-Handel, Listinggrenzen, Wartung oder Aufnahmefehler bedeuten. Der Grund bleibt unbekannt, wenn er nicht belegt ist.

Ein Snapshot referenziert genaue Dateien und Schemas, keine veränderlichen Globs. Beispiel:

```json
{
  "snapshot_id": "example-snapshot-001",
  "schema_version": "candles/1",
  "files": [{"uri": "normalized/example/part-001.parquet", "sha256": "<computed-at-import>"}],
  "normalizer_version": "example-commit",
  "quality_report_id": "example-report-001",
  "availability_policy_id": "historical-estimated-v1"
}
```

Die Platzhalter sind illustrativ und keine gültigen Produktionshashes. Schemaänderungen sind migrationspflichtig; neue Felder mit gleicher Bedeutung können kompatibel ergänzt werden, geänderte Einheiten oder Zeitsemantik benötigen neue Versionen. Alte Snapshots werden nicht stillschweigend uminterpretiert.

## 9. AP01-Konkretisierung

Der [AP01-Vertrag](08-ap01-contract.md) konkretisiert beide Research-Abläufe, Schnittstellen, Modulgrenzen, numerische Toleranzen und die Übergabe. Technische ADRs sind Vorschläge zur Abnahme. Softwaretests und Benchmarks werden erst in den nachfolgenden Arbeitspaketen ausgeführt.
