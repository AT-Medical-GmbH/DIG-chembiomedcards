# 00 — Executive Summary

## Was ChemBioMed Cards ist

ChemBioMed Cards ist ein **professionelles, datengetriebenes Lernkarten-System** für Chemie,
Biochemie, Molekularbiologie und Medizin, das aus **einer** gepflegten Datenquelle drei
Ausgabeebenen bedient:

- **Print** — druckfertige DIN-A6-Karten und A4/A3-Bögen für Lernkartenboxen.
- **Moodle / LMS** — importfähige Pakete und eine tiefe LTI-1.3-Integration.
- **Online** — eine eigenständige, interaktive Lernplattform mit Spaced Repetition,
  Notizen, Annotationen und Nutzerfortschritt.

Das System ist von Beginn an **mandantenfähig für weitere Fachgebiete** (Pharmakologie,
Mikrobiologie, Immunologie, Notfallmedizin …) ausgelegt: Kategorien, Tags und Kartentypen
kommen aus Konfiguration, nicht aus hartem Layout-Code.

## Die eine Regel

> **Datenmodell zuerst. Bilder, PDFs und Moodle-Pakete sind generierte Artefakte.**

Keine Karte existiert nur als Bild. Jede Karte ist ein strukturierter, versionierter Datensatz
(YAML als Autoren-Quelle, kanonisches JSON + Datenbank als Laufzeitquelle). Jedes sichtbare
Artefakt entsteht reproduzierbar daraus.

## Kernentscheidungen (Details im [Decision Log](decision-log.md))

| Thema | Entscheidung | Kurzbegründung |
|-------|--------------|----------------|
| Autoren-Datenformat | **YAML pro Karte** → kanonisches `cards_master.json` | Diff-freundlich, review-fähig, maschinell validierbar |
| Rendering | **HTML/CSS → Playwright (Chromium)** für PNG & PDF; SVG als editierbare Zweitquelle | Ein Layout, alle Formate; Playwright ist in der Umgebung vorinstalliert |
| Kartenformat | **DIN A6 quer (148 × 105 mm)** mit Beschnitt, auf A4/A3-Bögen montiert | Bestehender Repo-Standard, druck- und online-tauglich |
| Register-Tabs | **6 feste Tabs**: Allgemein · Anorganik · Organik · Molekularbio · Biochemie · Klinik | Handover-Vorgabe; über alle Karten identisch |
| Online-Frontend | **React + TypeScript (Vite) + Tailwind** | Größtes Ökosystem, Web-Component-Einbettung, passt zur ATMED-Weblinie |
| Online-Backend | **FastAPI (Python) + PostgreSQL + SQLAlchemy/Alembic** | Gleiche Sprache wie die Generierungs-Pipeline; OpenAPI-nativ |
| Export-Service | **Playwright** serverseitig für On-Demand-PNG/PDF | Identische Render-Engine wie der Build |
| Spaced Repetition | **SM-2 mit Leitner-Box-Overlay** | Bewährt, erklärbar, erweiterbar |
| Moodle | **LTI 1.3 (strategisch)** + **Import-/H5P-Pakete (interim)** | SSO, Deep Linking, Noten-Rückgabe ohne Plugin-Pflege |
| Auth | Dev: lokales JWT · Prod: **OIDC via Authentik (SSO)** | `ATMED-authentik` existiert; zentrale Identität |
| Storage | **S3-kompatibel** (MinIO lokal, später dediziert/Nextcloud-kompatibel) | Trennung App/DB/Storage, cloud-portabel |
| Deployment | **Docker Compose + Traefik-Labels**, GitHub Actions CI/CD | `ATMED-traefik` existiert; ATMED-Betriebsmuster |
| Annotationen | **Overlay als JSON-Koordinaten**, nicht destruktiv ins Bild | Original bleibt unberührt; Export kann einrendern |

## Scope dieses Dokumentensatzes

Dieser Konzeptsatz liefert **Phase 1 vollständig** (Analyse, Architektur, Projektstruktur,
Datenmodell, Import-/Audit-Plan, Online-/Moodle-Entscheidung) und entwirft die Phasen 2–17 so
detailliert, dass sie nach dem Karten-Upload direkt umgesetzt werden können.

## Nicht in diesem Dokument

- Die tatsächlichen Kartendaten (werden laut Handover separat hochgeladen).
- Produktionssecrets, Live-Serveränderungen, echte Lizenz-/Preislogik.
- Endgültige fachliche Festlegungen ohne Review — strittige Inhalte werden `review_needed`.

## Nächster Schritt

Nach Freigabe dieses Konzepts und **Upload der vorhandenen Karten**:
1. Import- & Audit-Pipeline laufen lassen → Inventar + Auditberichte.
2. Vollständigkeitsprüfung gegen die Soll-Liste (Aminosäuren, Vitamine, Stoffwechsel …).
3. Einheitliche Neugenerierung aller Karten aus dem Datenmodell.
4. Moodle-Pakete + Druckpakete erzeugen.
5. Online-MVP aufsetzen.
