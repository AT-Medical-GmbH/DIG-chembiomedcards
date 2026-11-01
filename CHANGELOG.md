# Changelog

## 2026-10-31 (Fachreview-Vorlauf)
- Pharma Cards – Fachreview-Prozess unter `docs/pharma-cards/review/`: Ablauf und Rollen,
  Checklisten Pharmakologie, Toxikologie und klinische Sicherheit, Protokollvorlage.
- Klinische R1-Entwürfe (30 Karten) in `cards/PH/metadata/`: Notfallmedikamente `ph_040`–`ph_049`
  (`clinical_review_needed`), Toxidrome `ph_080`–`ph_086` und Antidote `ph_100`–`ph_112`
  (`toxicology_review_needed`). Keine Zahlendosen; konkrete Prüfpunkte je Karte in `review_focus`.
- `scripts/pharma/review_report.py` + `make ph-review-report` erzeugen
  `docs/pharma-cards/reports/cards_review_needed.md`.
- Render: Vorderseite zeigt Namen der Wirkstoffgruppe statt Slug.
- Scope: Intoxikationsbild `cyanid` ergänzt (Zielgift des Antidots Hydroxocobalamin).
- Reports `missing_cards`, `content_review`, `content_scope` auf Stand R1 (60 Entwürfe) gebracht.

## 2026-10-31
- Pharma Cards (Modul PH) – P1 Pipeline: reproduzierbare Erzeugung unter `scripts/pharma/`
  (`validate_ph_cards.py`, `build_registry.py`, `render_cards.py`, `validate_output.py`) + `Makefile`
  und gemeinsames Kartenlayout `card-system/templates/pharma/card.css` (DIN A6 quer, Tab-Leiste,
  Farbrollen, Warnlevel-Badge). Rendering optional via vorinstalliertem Chromium.
- Pharma Cards – P2 Pilot-Content R1: 30 Karten in `cards/PH/metadata/` (Allgemeine Pharmakologie
  `ph_001`–`ph_019`, PK/PD-Mechanismen `ph_020`–`ph_030`), warning_level low/moderate,
  review_status needs_review, keine Dosierungen; Registry `cards.master.csv` um PH-Zeilen ergänzt
  (Nicht-PH-Zeilen unverändert).
- Export-Gating implementiert (critical nur approved; moderate/high nur reviewed/approved);
  Pilot-Karten korrekt als "im Review / nicht exportierbar" erkannt.
- Beispiel-Renders unter `card-system/examples/pharma/`; generierte Massen-Artefakte via `.gitignore`
  ausgeschlossen (reproduzierbar). Superseded Beispiel-YAML aus `cards/PH/examples/` entfernt.

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
