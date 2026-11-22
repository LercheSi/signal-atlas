# AGENTS.md

## Geltungsbereich

Diese Regeln gelten für sämtlichen neu geschriebenen oder geänderten Code in
SignalAtlas, einschließlich Frontend, Backend, Datenimporten, Analyse-Plugins,
Skripten und Tests.

## Lesbarkeit und Aufbau

- Verwende aussagekräftige Namen, die den fachlichen Zweck ausdrücken.
  Mache Einheiten, Zeitbezüge und Bedeutungen explizit, etwa `bar_end_utc`,
  `max_age_seconds` oder `base_volume`.
- Gib Funktionen und Modulen eine klar erkennbare Aufgabe. Halte den
  Kontrollfluss übersichtlich und bevorzuge einfache, direkte Lösungen.
- Nutze vorhandene Funktionen und Konventionen, sofern sie zum fachlichen
  Vertrag passen. Führe Abstraktionen ein, wenn sie wiederkehrende Logik
  bündeln oder eine klare Modulgrenze schaffen.
- Definiere an Modulgrenzen, welche Eingaben, Ausgaben und Fehlerfälle
  Aufrufer erwarten können. Nutze dafür Typen, Validierung und bei Bedarf
  Docstrings oder Schnittstellendokumentation.

## Kommentare und Docstrings

- Dokumentiere neue oder fachlich geänderte öffentliche Schnittstellen mit
  einem kurzen Docstring oder der im Modul üblichen Schnittstellendokumentation.
  Beschreibe den Zweck und relevante Annahmen, Einheiten, Seiteneffekte oder
  Fehlerfälle.
- Kommentiere komplexe Algorithmen, fachliche Regeln und überraschende
  Randfälle dort, wo sie im Code umgesetzt werden. Erkläre, warum eine Regel
  gilt oder welche Bedingung der Code sicherstellt.
- Erkläre bei Zeitreihenanalysen insbesondere die Zeitbasis, die
  Verfügbarkeitsgrenze, die Behandlung von Lücken und Revisionen sowie
  die Vorzeichenkonvention von Lags, soweit sie für den Abschnitt relevant
  sind. Eine finale Candle darf beispielsweise frühestens ab ihrem Ende in
  die Analyse eingehen. Der Verfügbarkeitszeitpunkt kann später liegen.
- Halte Kommentare knapp und aktuell. Für selbsterklärende Anweisungen
  genügen klare Namen und eine verständliche Struktur.

## Fachliche Korrektheit

- Behandle fehlende Werte, Datenlücken, Duplikate und unbekannte Einheiten
  oder Zeitangaben nach einer expliziten Regel. Kennzeichne Ausschlüsse,
  Schätzungen und Ersetzungen nachvollziehbar.
- Verwende für historische Analysen die gewählte Verfügbarkeitspolicy und
  berücksichtige spätere Revisionen erst ab ihrer jeweiligen Verfügbarkeit.
- Halte anbieterspezifische Formate und Sonderregeln in den Connectoren
  und Normalizern. Der gemeinsame Forschungs- und Abfragekern arbeitet
  mit kanonischen Datentypen und stabilen IDs.
- Berücksichtige bei Importen und Jobs auch Wiederholungen, Abbrüche
  und Teilausfälle. Ergebnisse gelten erst nach vollständiger,
  erfolgreicher Verarbeitung als veröffentlicht.

## Prüfung vor Abschluss

- Prüfe die Änderung über ihren regulären Einstiegspunkt und führe die
  relevanten Projektprüfungen für Tests, Formatierung, Linting und Typen aus.
- Ergänze gezielte Tests für neue fachliche Regeln und Fehlerfälle, wenn die
  vorhandenen Tests das geänderte Verhalten nicht abdecken.
- Prüfe, ob Namen, Kommentare und Dokumentation mit dem tatsächlichen
  Verhalten übereinstimmen. Halte Formatierungsänderungen außerhalb der
  betroffenen Stellen aus dem Diff heraus.
- Gib bei der Übergabe an, welche Prüfungen durchgeführt wurden und welche
  relevanten Prüfungen noch ausstehen.

## Git-Workflow

- Arbeite für jedes Feature und jedes Arbeitspaket auf einem eigenen Git-Branch.
  Lege den Branch vor der ersten Änderung an oder verwende den bereits für
  diese Aufgabe angelegten Branch. Halte die Änderungen auf den jeweiligen
  Aufgabenbereich begrenzt. Direkte Entwicklungsarbeit auf `main` ist
  ausgeschlossen.
- Erstelle während der Arbeit einen Commit, sobald ein fachlich zusammenhängender,
  überprüfbarer Teilschritt abgeschlossen ist. Jeder Commit bündelt die zu
  diesem Schritt gehörenden Änderungen und hat eine aussagekräftige Nachricht,
  die Zweck oder Wirkung der Änderung beschreibt.
