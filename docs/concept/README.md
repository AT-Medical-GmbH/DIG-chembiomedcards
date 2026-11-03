# ChemBioMed Cards — Gesamtkonzept

Dieses Verzeichnis enthält das **vollständige, verbindliche Umsetzungskonzept** für das Projekt
**ChemBioMed Cards** der AT Medical GmbH. Es übersetzt die Projektidee und das Handover in eine
konkrete, reproduzierbare und produktionsreife Architektur über alle drei Projektebenen hinweg:

1. **Content-Ebene** — strukturierte, versionierbare, fachlich geprüfte Kartendaten.
2. **Export-Ebene** — Einzelbilder, Moodle-Importe, druckfertige PDFs, Kategorie-Gesamtexporte.
3. **Online-Lernsystem** — eine moderne, interaktive, Moodle-integrierbare Lernplattform.

Leitprinzip des gesamten Konzepts: **Das Datenmodell ist die einzige Quelle der Wahrheit.**
Alle Bilder, PDFs, Moodle-Pakete und Online-Ansichten sind *generierte Artefakte* aus
strukturierten Kartendaten — niemals umgekehrt.

---

## Lesereihenfolge

| # | Dokument | Inhalt |
|---|----------|--------|
| 00 | [Executive Summary](00-executive-summary.md) | Zielbild, Scope, Kernentscheidungen auf einer Seite |
| 01 | [Systemarchitektur](01-system-architecture.md) | Drei-Ebenen-Architektur, Datenfluss, Repository-Struktur |
| 02 | [Content-Modell](02-content-model.md) | Kanonisches Kartenschema, Felder, Versionierung |
| 03 | [Taxonomie & Tabs](03-taxonomy-and-tabs.md) | Kategorien, Register-Tabs, Tag-System, Modul-Mapping |
| 04 | [Import- & Audit-Pipeline](04-import-audit-pipeline.md) | Einlesen, Paaren, Auditieren, Bereinigen der Upload-Karten |
| 05 | [Kartenlayout](05-card-layout.md) | Einheitliches Layout, Farblogik, Vorder-/Rückseiten-Regeln |
| 06 | [Generierungs-Pipeline](06-generation-pipeline.md) | Reproduzierbare PNG-/SVG-/PDF-Erzeugung aus Daten |
| 07 | [Print-Export](07-print-export.md) | Einzelkarten, A4/A3-Bögen, Schnittmarken, Druckpakete |
| 08 | [Moodle-Integration](08-moodle-integration.md) | Entscheidung LTI 1.3 + Importpakete, Begründung, Pfade |
| 09 | [Online-Lernsystem](09-online-learning-system.md) | Funktionsumfang: Lernen, SRS, Notizen, Annotationen, Admin |
| 10 | [Online-Architektur](10-online-architecture.md) | Technologie-Stack-Entscheidung, Komponenten, API |
| 11 | [Online-Datenmodell](11-online-data-model.md) | Relationales Schema, Entitäten, Migrationen |
| 12 | [UI/UX](12-ui-ux.md) | Designprinzipien, Ansichten, Interaktion, Barrierefreiheit |
| 13 | [Erweiterbarkeit](13-extensibility.md) | Weitere Fachgebiete, Kartentypen, generisches Modell |
| 14 | [Qualitätssicherung](14-quality-assurance.md) | Fachreview-Workflow, QS-Kriterien, Berichte |
| 15 | [Deployment](15-deployment.md) | Container, Compose, Traefik, OIDC, Backup, Betrieb |
| 16 | [Roadmap & Akzeptanz](16-roadmap-and-acceptance.md) | Phasenplan, Meilensteine, 20 Akzeptanzkriterien |

Querschnittsdokumente:

- [Decision Log](decision-log.md) — alle begründeten Architekturentscheidungen (ADR-Kurzform).
- [Offene Fragen](open-questions.md) — Punkte, die eine Freigabe durch Andreas / AT Medical brauchen.

---

## Verhältnis zum bestehenden Repository

Das Repository enthält bereits eine Verzeichnisstruktur und Platzhalterdokumente
(`card-system/`, `online-platform/`, `print-production/`, `lms-content/`, `cards/registry/` …).
Dieses Konzept **baut auf diesen vorhandenen Konventionen auf** und vertieft sie, statt sie zu
ersetzen. Wo das Handover und der bestehende Stand voneinander abweichen (z. B. Register-Tabs vs.
Modul-Codes), ist die Abweichung im [Decision Log](decision-log.md) bzw. in den
[offenen Fragen](open-questions.md) ausdrücklich dokumentiert — es wird nichts stillschweigend
überschrieben.

## Status

**Konzeptphase — abgeschlossen und freigabebereit.**
Die eigentlichen Karten werden laut Handover separat hochgeladen. Die
[Import- & Audit-Pipeline](04-import-audit-pipeline.md) ist so entworfen, dass sie nach dem
Upload automatisiert greift. Die Umsetzung der Pipeline, der Generierung und des Online-Systems
folgt dem [Phasenplan](16-roadmap-and-acceptance.md).
