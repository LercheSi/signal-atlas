# ADR-0006 · Geprüfte lokale Plugins im MVP

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Betrieb

## Kontext

Ein freier Plugin-Marktplatz verlangt Isolation und einen Distributions-Vertrauensanker. Ein Worker-Prozess schützt nicht vor bösartigem Code.

## Entscheidung

Nur geprüfte, lokal installierte Allowlist-Plugins. Analysen verwenden gebundene Inputs und keine spontanen unversionierten Netzwerkabrufe. Connectoren erhalten Secret-Referenzen; Secrets werden nicht in Workspace/Manifest serialisiert. Plugin-API und Implementierung sind unabhängig versioniert.

Eine Allowlist-Freigabe bindet das Tupel aus Plugin-ID, Implementierungsversion und unveränderlichem Code-/Paketnachweis (beispielsweise Inhaltsdigest des ausführbaren Pakets). Die tatsächlich geladenen Inhalte müssen diesem geprüften Nachweis entsprechen; eine Versionszeichenfolge oder ein veränderlicher Installationspfad reicht nicht. Änderungen an Code/Paket oder Version erfordern erneute Prüfung und eine neue Freigabe. Registry, Run-Manifest und Cacheidentität binden dieses Tupel; Environment-/Dependency-Nachweise bleiben zusätzlich erforderlich.

Fehlt für einen alten Run genau die gebundene Version mit passendem Nachweis oder ihre gültige Freigabe, scheitert die angeforderte Ausführung ausdrücklich vor dem Laden des Plugins. Gleichnamige, neuere oder unter gleicher Versionsnummer veränderte Pakete sind kein Ersatz. Bereits archivierte Ergebnisse dürfen mit Herkunft gelesen werden, gelten aber nicht als erneute Ausführung. Ein ausdrücklich gewähltes Upgrade erzeugt einen neuen Run und erhält die Bindungen des alten Runs.

## Alternativen und Folgen

Gegen freie Remoteinstallation im MVP. Fremdcode benötigt ein separates Isolationsmodell. Alte Runs wechseln nicht still auf neue Versionen.

## Nachweis und Überprüfung

Registry/Versionen, unbekannte Plugins, Secret-Ausschluss und inkompatible Ports; AP04/06. Zusätzliche Prüffälle AP04/06: verändertes Paket unter gleicher Version, ungeprüfte neue Version, fehlendes altes Paket und Nachweisabweichung werden vor Ausführung abgewiesen; bloße Installation einer neueren Version erlaubt keinen Fallback. Ein unverändert freigegebenes Paket bleibt ausführbar. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Ungeprüfter Fremdcode, Remoteinstallation oder mehrere Nutzer.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
