# ADR-0004 · Verfügbarkeit und fachliche Zeit trennen

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Daten / Research

## Kontext

Ereigniszeit oder heutiger Download allein belegen keine historische Bekanntheit. Latest-Sichten würden spätere Revisionen rückwirkend sichtbar machen.

## Entscheidung

event_time, published_at, observed_at und available_at bleiben getrennt. Historische Marktsicht, System-Replay und explorative Sicht sind explizit. Strikte Analyse verlangt belegte Verfügbarkeit; estimated benötigt ausdrücklichen Annahmemodus. Vor Alignment wird der am Cutoff bekannte Revisionsstand rekonstruiert. Finale Candles sind nie vor bar_end nutzbar.

Für den AP01-Ereignisablauf bleibt der Anker die belegte Erstverfügbarkeit des fachlichen Ereignisses unter der gebundenen Policy. Eine spätere Ereignisrevision ändert nur die ab ihrem Cutoff sichtbaren Attribute, nicht diesen Anker oder die Anzahl unabhängiger Ereignisse. Die Fünf-Minuten-Rendite verlangt einen am Anker verfügbaren finalen Close exakt am Anker und einen finalen Close exakt bei Anker plus fünf Minuten. Ältere Baseline-Kandidaten werden mit Alter und Ausschlussgrund ausgewiesen; keine Auffüllung. Der Endkurs ist erst ab eigener Verfügbarkeit auswertbar. Gebundene Kursrevisionen werden nicht still überschrieben; korrigierte Kursauswertungen benötigen einen expliziten neuen Run. Siehe [AP01-Referenzfälle](../08-ap01-contract.md#3-research-ablauf-b-ohlcv-und-veröffentlichungsereignisse).

## Alternativen und Folgen

Gegen pauschale Verfügbarkeit ab Ereigniszeit. Zusätzliche Metadaten begrenzen die belegbare Stichprobe. Lag-Konvention: corr(x[t], y[t+k]); positives k bedeutet x führt. Zukünftige Renditen bleiben Ergebnisgrößen.

## Vertragsfreigabe

Freigabekriterium für D-07 ist der widerspruchsfreie Zeitvertrag einschließlich des an Erstverfügbarkeit gebundenen Ereignisfensters und seiner Referenzfälle. Die Freigabe ist vor formaler AP01-Abnahme und AP03-Vertragsimplementierung erforderlich; quellenspezifische Verfügbarkeitsbelege D-13 folgen separat vor strikter Realanalyse. Der Status bleibt `proposed`; diese Überarbeitung enthält keine Freigabe.

## Nachweis und Überprüfung

Candle-Ende, Cutoff, Revisionen, Unknown/Estimated, Mappingwechsel und Zukunftsänderungen; AP03/04/08. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Neue Quellenzeitsemantik oder Replayperspektive.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
