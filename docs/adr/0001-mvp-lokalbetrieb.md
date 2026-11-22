# ADR-0001 · MVP und lokaler Einzelbetrieb

Status: **accepted** · Datum: 22. November 2026 · Verantwortliche Rolle: Produkt / Research

## Kontext

Lokaler Betrieb für eine Person wurde im Projektgespräch bestätigt. Ein Mehrnutzerdienst würde zusätzliche Rechte- und Betriebsanforderungen vorziehen.

## Entscheidung

Zwei Abnahmeläufe: OHLCV-Vergleich mit Lead-Lag sowie OHLCV plus synthetische Veröffentlichungsereignisse. Binance und Kraken sind Pilotquellen. Lokale Dienste binden an Loopback. Autonome Echtgeld-Ausführung, öffentliche Mehrnutzerfunktionen und verpflichtende reale Makro-APIs sind ausgeschlossen.

## Alternativen und Folgen

Ein reiner OHLCV-Start prüft Heterogenität nicht; reale APIs als Pflicht würden externe Abhängigkeiten zum MVP-Gate machen.

## Nachweis und Überprüfung

Beide Abläufe im AP01-Vertrag; Softwareabnahme AP03–08. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Remotezugriff, Mehrnutzerbedarf oder geänderter Referenzumfang.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
