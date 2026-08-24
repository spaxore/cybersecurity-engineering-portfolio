# Keycloak configuration

This directory contains the local Keycloak realm configuration used by Project 07.

The committed file `cloudsec-realm.example.json` is safe for public sharing because its password values are placeholders. The live file `cloudsec-realm.json` is intentionally ignored by Git because it contains local disposable credentials.

## Local setup

From the Project 07 root directory, create a local realm file:

```powershell
Copy-Item .\keycloak\cloudsec-realm.example.json .\keycloak\cloudsec-realm.json
