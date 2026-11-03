# Online Platform

Online-Lernsystem für ChemBioMed Cards, zuerst für das Modul PH (Pharma Cards).

| Verzeichnis / Datei | Inhalt |
|---|---|
| `backend/` | FastAPI-API: Karten, Lernen (SM-2/Leitner), Notizen, Review-Protokoll, Downloads; Alembic-Migrationen; Tests |
| `frontend/` | SvelteKit-Oberfläche (statisch, nginx): Übersicht, Lernmodus, Kartensuche, Antidot-Übersicht, Notizen |
| `e2e/smoke.py` | Browser-Smoke-Test (Playwright) gegen eine laufende Instanz |
| `docker-compose.yml`, `docker-compose.traefik.yml`, `.env.example` | Betrieb lokal/Staging bzw. hinter Traefik |
| `architecture/`, `database/` | frühere Konzeptnotizen (ChemBioMed allgemein) |

Betrieb, Sicherheit, Backup und bekannte Grenzen: **`README_DEPLOYMENT.md`**.
