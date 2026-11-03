# ATMED-core Deployment Notes

## Initiales Deployment

### Zielhost

**ATMED-core** (initial)

Der initiale Betrieb erfolgt auf dem bestehenden ATMED-core-Server. Eine spätere Migration auf einen dedizierten Server ist ausdrücklich vorgesehen und muss architektonisch vorbereitet werden.

### Domain

**Primärdomain:** `chembiomed-cards.de`
**Alternative Domain:** `www.chembiomed-cards.de`

### DNS-Verwaltung

DNS-Verwaltung erfolgt über **Cloudflare**.

## Hosting-Architektur

### Initiale Phase

In der initialen Phase ist die Nutzung von **WordPress/WooCommerce** möglich.

- **Landingpage:** kann statisch oder als WordPress-Content übernommen werden
- **Shop/Lizenzierung:** WooCommerce-Integration für Kartenpakete und Lizenzen

### Perspektivische Subdomain-Struktur

Die Architektur muss die folgenden Subdomains unterstützen:

- **Landingpage:** `chembiomed-cards.de` oder `www.chembiomed-cards.de`
- **Webanwendung:** `app.chembiomed-cards.de`
- **API:** `api.chembiomed-cards.de`

### Authentifizierung

Authentifizierung perspektivisch über **Gateway/SSO**.

Initial kann WordPress-Authentifizierung genutzt werden, langfristig muss eine saubere SSO-/Gateway-Lösung etabliert werden.

## Architektonische Anforderungen

### Keine harte Kopplung an ATMED-core

Die Implementierung muss so erfolgen, dass **keine harte technische Kopplung** an die ATMED-core-Infrastruktur besteht.

Alle Komponenten müssen sich **isoliert deployen und migrieren** lassen.

### QR-Code-Stabilität

**Kritisch:** QR-Links auf den Druckkarten müssen **dauerhaft stabil** bleiben.

- QR-Links müssen auch nach Migration auf einen dedizierten Server ohne Änderung funktionieren.
- Verwendung von permanenten Redirect-URLs (z. B. `chembiomed-cards.de/qr/{card_id}`).
- Backend-seitige Konfiguration der Ziel-URLs, sodass diese bei Infrastrukturwechsel angepasst werden können.

> Umsetzung des Betriebs auf ATMED-core: [`README_MIGRATION.md`](README_MIGRATION.md) (ADR-024).

### Migration auf dedizierten Server

Die spätere Migration auf einen **eigenen dedizierten Server** muss explizit vorbereitet werden:

- **Datenbank:** portabel (MariaDB/PostgreSQL), keine ATMED-core-spezifischen Abhängigkeiten
- **Dateisystem:** strukturiert, migrierbar (Uploads, Medien, Karteninhalte)
- **Authentifizierung:** entkoppelt von ATMED-core-Benutzerverwaltung
- **CI/CD:** unabhängig deploybar

## Technische Empfehlungen

### Backend

- **PHP/WordPress** initial, perspektivisch Trennung von API und CMS
- **Python/Node.js**-Backend für API (wenn Entkopplung von WordPress erfolgt)

### Datenbank

- **MariaDB** oder **PostgreSQL**
- Migrierbar, keine Hardcoding von Hostspezifika

### Deployment

- **Docker**-Container zur Isolation und einfacheren Migration
- **CI/CD** über GitHub Actions

### Monitoring & Logging

- Zentrale Logs (z. B. über ELK-Stack oder Cloudflare Logs)
- Health Checks für API und Webapp

## Zusammenfassung

| Kriterium               | Wert                                   |
|-------------------------|----------------------------------------|
| Zielhost (initial)      | ATMED-core                             |
| Domain                  | chembiomed-cards.de                    |
| DNS                     | Cloudflare                             |
| Initiales CMS           | WordPress/WooCommerce (optional)       |
| Spätere App             | app.chembiomed-cards.de                |
| Spätere API             | api.chembiomed-cards.de                |
| Authentifizierung       | Gateway/SSO (perspektivisch)           |
| QR-Links                | dauerhaft stabil, migrierbar           |
| Entkopplung von ATMED   | ja, zwingend erforderlich              |
| Migration auf dediziert | ausdrücklich vorbereiten               |
