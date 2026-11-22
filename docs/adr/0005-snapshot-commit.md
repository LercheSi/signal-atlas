# ADR-0005 · Unveränderliche Snapshots mit Manifest-Commit

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Betrieb

## Kontext

Dateien und PostgreSQL teilen keine atomare Transaktion. In-place-Updates und wandernde Globs gefährden reproduzierbare Datensichten.

## Entscheidung

Staging schreiben, Schema/Hashes/Bericht prüfen, unveränderliche Dateien und Manifest veröffentlichen, danach vollständigen Snapshot in PostgreSQL als committed registrieren. Leser verwenden ausschließlich committed Snapshots. Ergebnisse werden ebenfalls erst vollständig erfolgreich veröffentlicht.

## Alternativen und Folgen

Gegen In-place-Dateien und vollständige Massendatenhaltung in PostgreSQL. Ein Fehler vor DB-Commit kann verwaiste Dateien, aber keine halben sichtbaren Snapshots erzeugen. Wiederholung ist idempotent; Aufräumen respektiert Referenzen, Backup und Retention.

## Nachweis und Überprüfung

Crash vor/nach Datei- und DB-Veröffentlichung, Wiederholung und Restore; AP03/04. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Storagewechsel oder geänderte atomare Grenzen.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
