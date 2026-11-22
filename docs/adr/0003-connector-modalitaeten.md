# ADR-0003 · Connectoren mit versionierten Modalitäten

Status: **accepted** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Daten

Annahme durch Simon Lerche mit der AP01-Abnahme am 22. November 2026.

## Kontext

Candle-only verhindert heterogene Daten; untypisierte Payloads verschieben Fehler in den Executor.

## Entscheidung

Gemeinsame versionierte Metadaten und Fähigkeiten; getrennte Schemata candle/1 und publication_event/1 mit gemeinsamer Herkunfts-, Zeit- und Revisionshülle. Verbindliche Schema-ID für Candles ist `candle/1`; der Datenartbezeichner bleibt `candle`. Registry, Normalizer, Query und Manifest verwenden dieselbe Schema-ID. Registry und Konfiguration binden Adapter ein. Punkt-in-Zeit-Abdeckung wird je Reihe/Zeitraum belegt.

## Alternativen und Folgen

Gegen ein einziges Pflichtschema und gegen beliebige Payloads. Neue Adapter bekannter Typen benötigen keine Kernänderung; neue Modalitäten können neue Verträge benötigen.

## Nachweis und Überprüfung

Gemeinsame Vertragssuite, äquivalente Provider-Fixtures mit erhaltener Herkunft und Eventregistrierung ohne Kernänderung; AP03/04. Zusätzlicher Prüffall AP03/04: Registry, Normalizer, Query und Manifest akzeptieren dieselbe Schema-ID `candle/1`; abweichende IDs werden als unbekannt zurückgewiesen. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Neue Datenart oder inkompatible Fähigkeit/Schemaversion.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
