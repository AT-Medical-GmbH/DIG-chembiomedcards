# Changelog

## 2026-10-31 (CI: eigener Runner)
- CI läuft auf einem eigenen Runner, weil die GitHub-Runner wegen Billing gesperrt sind:
  `runs-on: [self-hosted, linux, chembiomed]`, jeder Job im Container, nie für Fork-PRs, nur
  Leserechte.
- Neu `.github/workflows/pharma-ci.yml` mit den Jobs pipeline, api und web. Schritte ohne passende
  Dateien überspringen sich selbst.
- `docs/ci/self-hosted-runner.md`: Sicherheitsmodell, GitHub-Einstellungen (zuerst Repo privat),
  VM-Einrichtung, Wartung, Rückweg.

## 2026-10-09
- Pharma Cards (Modul PH) — vollständiges Konzeptdossier unter `docs/pharma-cards/` (18 Phasen:
  Analyse/Architektur, Datenmodell, fachliche Zielstruktur, kuratierte Startliste, Layout, Generierung
  & Print, Moodle-Integration, Online-Lernsystem, Deployment, Review/Sicherheit, Import/Audit,
  Akzeptanzkriterien & Roadmap)
- PH-Scope-Konfiguration angelegt (`cards/PH/scope/`): Kategorien, Wirkstoffgruppen, Tags, Warnlevel,
  Review-Status, Kartentypen, Toxidrome, Antidote — Kategorien kommen aus Konfiguration, nicht aus
  Layout-Code
- Erweitertes PH-Content-Datenmodell + zwei Beispielkarten (`cards/PH/examples/`), konservativ, mit
  Review-Status, ohne finale Dosierungen
- Phase-4-Reports angelegt (`docs/pharma-cards/reports/`: content_scope, missing_cards, content_review)
- PH als Ausbau-Vertikal von ChemBioMed Cards verankert (kein Parallel-Repo)

## 2026-05-15
- Initiale Repository-Struktur für ChemBioMed Cards angelegt
- Bereiche für Dokumentation, Card-System, Registry, Print-Produktion und Onlineplattform vorbereitet
