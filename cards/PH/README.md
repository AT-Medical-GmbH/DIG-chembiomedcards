# PH — Pharmakologie (Pharma Cards)

Bereich Pharmakologie und Toxikologie. Dieses Modul wird unter dem Produktnamen **Pharma Cards**
inhaltlich und technisch ausgebaut.

## Konzept & Struktur

- **Konzeptdossier:** `docs/pharma-cards/` (Architektur, Datenmodell, Startliste, Layout, Generierung,
  Moodle, Online-System, Deployment, Review/Sicherheit, Import/Audit, Akzeptanzkriterien).
- **Scope-Konfiguration:** `cards/PH/scope/` (Kategorien, Wirkstoffgruppen, Tags, Warnlevel,
  Review-Status, Kartentypen, Toxidrome, Antidote) — Single Source of Truth, aus Konfiguration
  gesteuert, nicht im Layout-Code verdrahtet.
- **Beispielkarten:** `cards/PH/examples/` (erweitertes Content-Schema, Status < `approved`).

## Grundsatz

Ausbildungs-/Lernmaterial, keine Therapieanweisung. Dosierungen nur mit Review-Status und Quelle; bei
Unsicherheit `clinical_review_needed` / `toxicology_review_needed`. Datenmodell zuerst, Karten daraus
generieren.
