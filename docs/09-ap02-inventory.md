# 09 · AP02 · Dateninventur und Qualitätsanalyse

[Zur Übersicht](../README.md)

## Stand und Abnahme

AP02 ergänzt ein eigenständiges Python-Inventurwerkzeug. Die Forschungsanwendung,
Importadapter und Snapshots aus AP03 sind weiterhin nicht implementiert. Der
vollständige reale Bestand ist erst nach beendetem Scan und Review nachgewiesen;
die formale Abnahme bleibt bei Simon Lerche. Private Pfade, Originaldaten und
reale Ergebnisdateien werden nicht eingecheckt.

## Ausführung

Voraussetzung: Python >= 3.12 auf Linux; zur Ausführung nur Standardbibliothek.
Die Backend-Laufzeitwahl für AP03 wird dadurch nicht vorweggenommen.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
mkdir -p .local/ap02
cp config/ap02.example.json .local/ap02/config.json
# Absolute Quell-, Ausgabe- und Arbeitspfade lokal anpassen.
.venv/bin/python -m tools.ap02 --config .local/ap02/config.json
make check
```

Die Konfiguration ist versioniert (`schema_version: 1`). Pro Quelle werden Muster
in der Reihenfolge `original`, `derived`, `support` geprüft; nicht zugeordnete
Dateien bleiben `unknown`. Muster gelten für relative POSIX-Pfade; `*` kann auch
Unterverzeichnisse umfassen. Nur `original` durchläuft die OHLCV-Vollprüfung.
Alle Dateien erhalten eine Hash-/Lesbarkeitsprüfung. Symlinks werden erfasst,
aber nicht verfolgt; unzugängliche Verzeichnisse bleiben als Fehler sichtbar.

Ausgabe und Arbeitspfad müssen außerhalb sämtlicher Quellverzeichnisse liegen
und voneinander getrennt sein. Für große Bestände ein ausreichend großes
Laufwerk verwenden: Der SQLite-Arbeitsindex kann deutlich größer als die
komprimierten Quelldaten werden. `min_free_bytes` reserviert freien Platz auf dem
Arbeitslaufwerk; Unterschreitung stoppt den Lauf. Arbeitsindizes bleiben für die
Nachprüfung erhalten. Ein neuer Aufruf startet einen neuen Scan, ohne einen
unterbrochenen Index wiederzuverwenden.

## Ergebnisse und Schnittstellen

Jeder Lauf erstellt zunächst `<run_id>.partial/`; erst `status: complete` entfernt
per Umbenennung den Suffix. Ein abgeschlossener Scan kann Qualitätsbefunde haben.
Parse-/Lesefehler, unbekannte Originalformate oder Quelländerungen ergeben
`incomplete`. Unterbrechung durch SIGINT/SIGTERM ergibt `interrupted`; ein interner
Fehler `failed`. Bei hartem Prozess-/Rechnerabbruch bleibt der laufende Status im
`.partial`-Verzeichnis als unvollständiger Nachweis erhalten. CLI-Exitcodes: 0
vollständig verarbeitet, 2 unvollständig oder Konfigurationsfehler, 130 Abbruch.

| Datei | Vertrag |
|---|---|
| `selection.jsonl` | Vor der Inhaltsprüfung festgehaltene Dateiauswahl mit Quelle, relativer Referenz, Klassifikation und Bytes |
| `files.jsonl` | Physische Dateien, Rechte, Besitzer, SHA-256 vor/nach Verarbeitung, Bytes und Lesestatus |
| `members.jsonl` | CSV-/Archivmitglieder, gebundene Archivhashes, Schemaidentität, Zeilenzahlen, Zeitabdeckung in UTC-Mikrosekunden und Befunde |
| `findings.jsonl` | Einzelbefunde mit Datei, ggf. Archivmitglied, Zeilennummer und vergleichbaren Fundstellen |
| `manifest.json` | Scan-/Ergebnisschema-Version, vollständige lokale Konfiguration samt Hash, Zeitpunkte, Hardware, Zähler, Formatmatrix und Benchmarkbereiche |
| `report.md` | Lesbare lokale Zusammenfassung mit Verweisen auf Detailnachweise |

Die Zeilennummer bezeichnet bei mehrzeiligen CSV-Records die letzte physische
Zeile des Records. Identische numerische Werte werden unabhängig von dezimaler
Schreibweise verglichen; keine Float-Rundung oder Datenkorrektur. Konflikte
bleiben separate Varianten, ohne erfundene Revisionsreihenfolge. Lücken werden
auf der Vereinigung der Originalbeobachtungen je Quelle/Instrument/Intervall
innerhalb belegter Abdeckung gezählt; doppelte Lieferungen erzeugen keine
zusätzlichen Rasterpunkte. Ungeordnete Datensätze werden gesondert gemeldet.

Benchmark-Mappings müssen explizit konfiguriert sein; Asset-/Quote-Zuordnung wird
nicht aus beliebigen Symbolsuffixen geraten. Kandidaten verwenden tatsächlich
auf beiden Quellen vorhandene Zeitpunkte, einen kleinen Bereich bis sieben Tage
und die gesamte gemeinsame Abdeckung; mindestens zwei Jahre werden separat
gekennzeichnet. Ein Kandidat ersetzt keine Qualitätsfreigabe. Fehlende gemeinsame
Zeitpunkte oder fehlende mehrjährige Abdeckung bleiben sichtbar. Historische
Verfügbarkeit ist aus diesen Archiven nicht belegt; kein Ergebnis erhält einen
Punkt-in-Zeit-sicheren Status.

## Belegte Formatregeln und offene Quellangaben

Geprüft am 22. November 2026:

- [Binance Public Data](https://github.com/binance/binance-public-data/):
  zwölfspaltige Spot-Klines; Open-/Close-Zeit, Basis-/Quote-Volumen und Tradezahl.
  Spot-Zeitstempel wechseln ab Januar 2025 von Millisekunden auf Mikrosekunden.
  Der Parser erkennt beide Einheiten, prüft den inklusiven Quellschluss gegen
  das exklusive Intervallende und unterstützt auch kalendarisches `1M`.
- [Kraken OHLCVT](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data):
  sieben Spalten für Zeit, OHLC, Volumen, Tradezahl; Symbol und Minutenintervall
  aus dem Mitgliedsnamen. Die CSV-Stichprobe besitzt Unix-Sekunden. Der Anbieter
  beschreibt ausgelassene Intervalle ohne Trades. Rasterlücken allein sind
  deshalb kein Nachweis beschädigter Lieferung.

Normale ZIPs werden streamend gelesen und CRC-geprüft. Byteweise geteilte ZIPs
(`.part00`, `.part01`, …) werden als seekbarer Gesamtstrom gelesen; fehlende Teile
oder ein ungültiges Gesamt-ZIP scheitern ausdrücklich. PKZIP-Multi-Disk-Archive
sind kein unterstütztes Format. Es wird nicht in Quellverzeichnisse entpackt.

Nutzungs-/Weiterverteilungsrechte, historische Erstverfügbarkeit, lokale
Empfangszeiten und Revisionen bleiben ungeklärt, soweit keine separaten Belege
vorliegen. Downloadpläne und Prüfdateien werden als Begleitdateien gehasht;
vorhandene Hashbehauptungen ersetzen nicht die neu berechneten Hashes. D-13
bleibt für Importfreigabe und strikte historische Realanalysen offen.

## Prüfungen

`make check` führt die Vertragstests über Parser, ZIP-Leser und CLI, Ruff-Lint,
Ruff-Formatprüfung, strikte Mypy-Typprüfung und `git diff --check` aus. Testfälle
umfassen Zeiteinheiten/Kalendermonate, exakte Dezimalwerte, Lücken, Reihenfolge,
Duplikate/Konflikte, Parsefehler, Archivteile, unbekannte Mitglieder, beschädigte
und unlesbare Dateien, Quelländerung, Abbruch, Speicherreserve sowie tatsächlich
überlappende Benchmarkzeitpunkte. Eine Wiederholung prüft identische fachliche
Befunde bei abweichenden Laufmetadaten.

Reale Vollscan-Ergebnisse und die abschließende Benchmarkfreigabe stehen noch aus.
