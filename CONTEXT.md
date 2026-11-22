# SignalAtlas

SignalAtlas ist ein Arbeitsplatz für explorative Finanzmarkt- und Ereignisforschung. Kryptowährungen bilden den ersten fachlichen Schwerpunkt.

## Sprache

**Provider**: Organisation oder System, das Daten bereitstellt. Ein Provider ist nicht automatisch ein Handelsplatz.

**Quelle**: Konkreter Ursprung oder Importkanal eines Datenbestands, etwa ein Dateiarchiv oder Veröffentlichungsfeed.

**Handelsplatz (Venue)**: Ort, an dem ein Instrument gehandelt wird. Veröffentlichungsereignisse benötigen keinen Handelsplatz.

**Instrument**: Konkretes handelbares Produkt einschließlich Handelsplatz, Marktart und Einheiten. BTC/USD und BTC/USDT sind verschiedene Instrumente.

**Entity**: Fachlicher Bezug eines Datensatzes, beispielsweise ein Asset, eine Zentralbank oder eine makroökonomische Größe.

**Datensatz (Dataset)**: Logische Reihe oder Sammlung von Fakten einer Datenart.

**Snapshot**: Unveränderlicher, vollständig veröffentlichter Stand eines Datensatzes.

**Revision**: Unveränderliche Fassung eines fachlichen Fakts. Eine spätere Revision ersetzt frühere Fassungen erst ab ihrer jeweiligen Verfügbarkeit.

**Verfügbarkeit**: Frühester Nutzungszeitpunkt eines Fakts in der gewählten historischen Perspektive; Herkunft und Annahmen dieses Zeitpunkts gehören zur Aussage.
_Avoid_: Ereigniszeit als Synonym für Verfügbarkeit

**Alignment**: Explizite zeitliche Zuordnung zwischen Eingaben unter festgelegten Gruppen-, Richtungs-, Alters- und Verfügbarkeitsregeln.

**Run**: Ausführung eines festgelegten Analysegraphen mit gebundenen Datenständen, Parametern und Zeitannahmen.
_Avoid_: Workspace als Synonym für Ausführung

**Workspace**: Speicherbare Arbeitsfläche mit Analysegraph, Parametern und Darstellung. Eine Arbeitsfläche kann mehrere Runs besitzen.
