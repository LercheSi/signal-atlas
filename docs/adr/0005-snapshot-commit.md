# ADR-0005 · Unveränderliche Snapshots mit Manifest-Commit

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Betrieb

## Kontext

Dateien und PostgreSQL teilen keine atomare Transaktion. In-place-Updates und wandernde Globs gefährden reproduzierbare Datensichten.

## Entscheidung

Dateien und Manifest müssen vor dem PostgreSQL-Commit vollständig validiert und gemäß dem dokumentierten Haltbarkeitsvertrag des Speichers dauerhaft gesichert sein. Validierung umfasst die vollständige Dateiliste, Prüfsummen, Schemata, Zeilenzahlen und Qualitätsbericht; das Manifest bindet genau diese Inhalte. Ein bloß erfolgreicher Schreibaufruf oder Rename genügt nicht als Dauerhaftigkeitsnachweis. Erst danach darf PostgreSQL den Snapshot als `committed` sichtbar machen. Leser verwenden ausschließlich solche Snapshots und keine Staging-Pfade oder Dateiglobs. Bei fehlenden oder beschädigten referenzierten Inhalten wird die Abfrage ausdrücklich abgewiesen statt einen Teilbestand zu liefern.

Vom Beginn der Veröffentlichung bis zum abgeschlossenen Commit oder zur gesicherten Aufgabe schützt eine zwischen Publisher, Recovery und Garbage Collection koordinierte Veröffentlichungsreservierung sämtliche Dateien und das Manifest vor Löschung. Die konkrete Sperr-/Reservierungstechnik bleibt AP03 überlassen; sie muss exklusives Aufräumen gegen erneuten Commit absichern. Eine Schonfrist allein genügt nicht. Nach Ablauf einer Reservierung darf ein alter Publisher nicht mehr committen, ohne den Schutz erneut zu erwerben und Bestand, Dauerhaftigkeit und Validierung erneut zu prüfen. Bei Übernahme durch Recovery darf nur der aktuelle berechtigte Publisher abschließen.

Ein Absturz vor dem Commit lässt den Snapshot unsichtbar. Recovery setzt denselben Auftrag nur mit gültigem Schutz und erneut bestätigter Vollständigkeit fort oder gibt ihn koordiniert auf. Wiederholung nach unbekanntem Commit-Ausgang prüft zuerst den Katalog: derselbe Auftrag mit demselben Manifest liefert den bereits committed Snapshot, widersprechende Inhalte scheitern. Ein Absturz nach dem Commit hebt den Schutz durch die dauerhafte Katalogreferenz nicht auf. Verwaiste Dateien dürfen erst nach gesicherter Aufgabe, Ausschluss eines noch berechtigten Publishers und erneuter Referenzprüfung gelöscht werden; Retention und Backup gelten zusätzlich. Prüfung und Löschung sind mit Publishern koordiniert, sodass dazwischen kein Commit die Dateien referenzieren kann. Gemeinsam referenzierte Dateien bleiben erhalten.

## Alternativen und Folgen

Gegen In-place-Dateien und vollständige Massendatenhaltung in PostgreSQL. Ein Fehler vor DB-Commit kann verwaiste Dateien, aber keine halben sichtbaren Snapshots erzeugen. Wiederholung ist idempotent; Aufräumen respektiert Referenzen, Backup und Retention.

## Vertragsfreigabe

Freigabekriterium für D-12 ist die dokumentierte Commit-Reihenfolge mit vollständiger Lesersicht und Verhalten an den Fehlergrenzen. Die Vertragsfreigabe ist vor formaler AP01-Abnahme und AP03-Persistenzcode erforderlich. Crash-/Wiederholungs- und Restore-Nachweise folgen erst in AP03/04 vor M1. Der Status bleibt `proposed`; diese Überarbeitung enthält keine Freigabe.

## Nachweis und Überprüfung

AP03/04 prüfen fehlende Dauerhaftigkeitsbestätigung, unvollständiges Manifest, Hashfehler, Crash vor/nach Commit mit unbekanntem Ausgang, Wiederholung, paralleles Aufräumen sowie Wiederanlauf eines Publishers mit abgelaufenem Schutz. Erwartung: nie ein lesbarer Teilbestand, keine Löschung geschützter/referenzierter Dateien, kein Commit durch einen überholten Publisher. Verwaiste Dateien werden erst nach sicherer Aufgabe bereinigt. Restore bleibt erforderlich. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Storagewechsel oder geänderte atomare Grenzen.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
