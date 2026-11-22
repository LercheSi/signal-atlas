# ADR-0004 · Verfügbarkeit und fachliche Zeit trennen

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Daten / Research

## Kontext

Ereigniszeit oder heutiger Download allein belegen keine historische Bekanntheit. Latest-Sichten würden spätere Revisionen rückwirkend sichtbar machen.

## Entscheidung

event_time, published_at, observed_at und available_at bleiben getrennt. Historische Marktsicht, System-Replay und explorative Sicht sind explizit. Strikte Analyse verlangt belegte Verfügbarkeit; estimated benötigt ausdrücklichen Annahmemodus. Vor Alignment wird der am Cutoff bekannte Revisionsstand rekonstruiert. Finale Candles sind nie vor bar_end nutzbar.

## Alternativen und Folgen

Gegen pauschale Verfügbarkeit ab Ereigniszeit. Zusätzliche Metadaten begrenzen die belegbare Stichprobe. Lag-Konvention: corr(x[t], y[t+k]); positives k bedeutet x führt. Zukünftige Renditen bleiben Ergebnisgrößen.

## Nachweis und Überprüfung

Candle-Ende, Cutoff, Revisionen, Unknown/Estimated, Mappingwechsel und Zukunftsänderungen; AP03/04/08. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Neue Quellenzeitsemantik oder Replayperspektive.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
