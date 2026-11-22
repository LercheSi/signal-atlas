# ADR-0002 · Quellen- und Handelsplatzunabhängigkeit

Status: **accepted** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Daten

Annahme durch Simon Lerche mit der AP01-Abnahme am 22. November 2026.

## Kontext

Ein börsenspezifischer Kern vereinfacht die Pilotimporte, erschwert aber Ereignisse und andere Märkte.

## Entscheidung

Provider, Quelle, Venue, Instrument, Entity, Dataset und Snapshot erhalten getrennte stabile Identitäten. Providerformate und Sonderregeln liegen in Connectoren/Normalizern. Query, Research und Executor verwenden kanonische Verträge und deklarierte Fähigkeiten. Mapping-Versionen werden gebunden.

## Alternativen und Folgen

Gegen einen providerabhängigen Kern und eine universelle Tabelle mit Candle-Pflichtfeldern für Events. Zusätzlicher Katalogaufwand schützt fachliche Grenzen.

## Nachweis und Überprüfung

Event ohne Venue/Instrument, zusätzliche Quell-IDs und Quote-Währungen; AP03/04. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Neue fachliche Identitäten oder Modalitäten.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
