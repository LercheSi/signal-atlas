# ADR-0006 · Geprüfte lokale Plugins im MVP

Status: **proposed** · Datum: 22. November 2026 · Verantwortliche Rolle: Architektur / Betrieb

## Kontext

Ein freier Plugin-Marktplatz verlangt Isolation und einen Distributions-Vertrauensanker. Ein Worker-Prozess schützt nicht vor bösartigem Code.

## Entscheidung

Nur geprüfte, lokal installierte Allowlist-Plugins. Analysen verwenden gebundene Inputs und keine spontanen unversionierten Netzwerkabrufe. Connectoren erhalten Secret-Referenzen; Secrets werden nicht in Workspace/Manifest serialisiert. Plugin-API und Implementierung sind unabhängig versioniert.

## Alternativen und Folgen

Gegen freie Remoteinstallation im MVP. Fremdcode benötigt ein separates Isolationsmodell. Alte Runs wechseln nicht still auf neue Versionen.

## Nachweis und Überprüfung

Registry/Versionen, unbekannte Plugins, Secret-Ausschluss und inkompatible Ports; AP04/06. Noch kein Implementierungsnachweis. Überprüfungsauslöser: Ungeprüfter Fremdcode, Remoteinstallation oder mehrere Nutzer.

[AP01-Vertrag](../08-ap01-contract.md) · [Entscheidungsregister](../07-decisions-risks.md)
