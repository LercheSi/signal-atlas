# ADR-0003 · Connectoren mit versionierten Modalitäten

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Daten

## Kontext

Candle-only verhindert heterogene Daten; untypisierte Payloads verschieben Fehler in den Executor.

## Entscheidung

Gemeinsame versionierte Metadaten und Fähigkeiten; getrennte Schemata candle/1 und publication_event/1 mit gemeinsamer Herkunfts-, Zeit- und Revisionshülle. Registry und Konfiguration binden Adapter ein. Punkt-in-Zeit-Abdeckung wird je Reihe/Zeitraum belegt.

## Alternativen und Folgen

Gegen ein einziges Pflichtschema und gegen beliebige Payloads. Neue Adapter bekannter Typen benötigen keine Kernänderung; neue Modalitäten können neue Verträge benötigen.

## Nachweis und Überprüfung

Gemeinsame Vertragssuite, äquivalente Provider-Fixtures mit erhaltener Herkunft und Eventregistrierung ohne Kernänderung; AP03/04. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Neue Datenart oder inkompatible Fähigkeit/Schemaversion.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
