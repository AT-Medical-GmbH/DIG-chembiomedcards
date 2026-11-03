# PH Scope-Konfiguration

Dieses Verzeichnis ist die **maschinenlesbare Konfiguration** für das Modul Pharmakologie (PH) von
Pharma Cards. Sie ist die einzige Quelle für Kategorien, Wirkstoffgruppen, Tags, Warnlevel,
Review-Status, Kartentypen, Toxidrome und Antidote.

**Prinzip:** Kategorien und Vokabulare sind **nicht** im Layout- oder App-Code hart verdrahtet. Sowohl
die Export-Pipeline (Layout/Templates) als auch die Online-Datenbank (Seed) lesen diese Dateien. Eine
neue Kategorie/Wirkstoffgruppe/ein neuer Tag = ein neuer Eintrag hier, kein Code-Change.

| Datei | Inhalt |
|---|---|
| `categories.yaml` | Haupt- und perspektivische Kategorien (Farbe, Icon, Release-Welle) |
| `drug_classes.yaml` | Wirkstoffgruppen, hierarchisch (parent) |
| `tags.yaml` | Kontrolliertes Tag-Vokabular |
| `warning_levels.yaml` | Warnlevel low/moderate/high/critical + Export-Gate |
| `review_status.yaml` | Fachreview-Workflow-Status + Pflegestatus |
| `card_types.yaml` | Kartentypen, Front-Typen, Back-Section-Bausteine + Farbrolle |
| `toxidromes.yaml` | Toxidrome + Intoxikationsbilder |
| `antidotes.yaml` | Antidote + Zielintoxikation + Warnlevel |

Validierung: `scripts/validate_card_metadata.py` (erweitert) prüft Karten gegen diese Enums. Seed:
`scripts/seed_online_db` (Folgephase) überführt die Konfig in die Tabellen `categories`,
`drug_classes`, `tags`, `antidotes`, `toxidromes`.

Siehe `docs/pharma-cards/03_fachliche-zielstruktur.md` und `02_datenmodell.md`.
