# 02 — Content-Modell (Kanonisches Kartenschema)

Dieses Kapitel definiert die **einzige Quelle der Wahrheit**: das Kartenschema. Es führt das
Handover-Schema mit dem bereits vorhandenen `cards/registry/cards.master.schema.json` und
`card-metadata-example.yaml` zusammen. Das bestehende Schema (`module`, `card_id`, `front_asset`
…) bleibt gültig und wird als **Teilmenge** dieses reicheren Modells verstanden.

## 1. Autoren-Quelle: eine YAML je Karte

Jede Karte lebt als eigene Datei unter `data/cards/<card_id>.yaml`. Vorteile: minimale Merge-
Konflikte, saubere Diffs im Review, Datei = Einheit der Versionierung.

```yaml
# data/cards/bc_014.yaml
card_id: bc_014                      # <lowercase-modul>_<3-stellig>  (Pattern: ^[a-z]{2,4}_[0-9]{3}$)
slug: alanin                         # URL-stabil, eindeutig, kebab-case
title: Alanin                        # Anzeigename
subtitle: Proteinogene Aminosäure    # kurze Einordnung (optional)

# --- Einordnung -----------------------------------------------------------
module: BC                           # Distributions-/Paketcode (AC|OC|BC|MB|APC|PH)
primary_category: biochemie          # steuert den aktiven Register-Tab (siehe Kap. 03)
secondary_categories: [organik, klinik]
topic_group: aminosaeuren            # thematische Gruppe (für Vollständigkeitsprüfung)
chapter: biochemie/aminosaeuren      # hierarchischer Pfad (kompatibel zum Bestand)
tags: [aminosaeure, proteinogen, unpolar, glukogen]
difficulty: beginner                 # beginner | intermediate | advanced

# --- Vorderseite ----------------------------------------------------------
front_type: structure                # structure | term | image | diagram | case | labvalue | …
front_content:
  render: fischer_projection         # Rendering-Hinweis für die Generierung
  smiles: "C[C@@H](N)C(=O)O"         # strukturierte Struktur-Repräsentation (wenn vorhanden)
  caption: ""                        # KEIN Name auf AS-Vorderseite (siehe Kap. 05)

# --- Rückseite (feste Sektionen, siehe Kap. 05) ---------------------------
back_sections:
  classification: "α-Aminosäure, unpolar/aliphatisch, proteinogen, glukogen"
  general_properties:
    - "Seitenkette: Methylgruppe (−CH3)"
    - "Nicht essenziell; zentrales Glied im Alanin-Zyklus"
  biochemical_relevance:
    - "Transaminierung Pyruvat ⇄ Alanin (ALT/GPT)"
    - "Alanin-Zyklus: Stickstofftransport Muskel → Leber"
  clinical_relevance:
    - "ALT (GPT) als Leberwert diagnostisch zentral"
  molecular_relevance: []            # nur wenn zutreffend
  mnemonic: "Alanin = 'A' wie einfach – kleinste chirale AS nach Glycin"
  fun_fact: "Entsteht im Muskel beim Abbau, 'tarnt' Stickstoff für den Transport."

# --- Referenzen & Governance ---------------------------------------------
references:
  - "Löffler/Petrides, Biochemie & Pathobiochemie"
biochemical_relevance: true          # schnelle Facet-Flags (für Filter/Farblogik)
clinical_relevance: true
molecular_relevance: false

review_status: draft                 # draft|needs_review|reviewed|approved|deprecated|archived
version: "0.1.0"
author: "AT Medical GmbH"
reviewer: ""
created_at: "2026-01-01"
updated_at: "2026-01-01"

# --- Ausgabe-Status (kompatibel zum Bestand) ------------------------------
print_status: draft
web_status: draft

# --- Verweise -------------------------------------------------------------
related_cards: [bc_013, bc_015]
qr_url: https://chembiomed-cards.de/c/bc014
lms_url: ""                          # optional, LMS-Lernpfad
```

## 2. Feldreferenz

| Feld | Pflicht | Typ | Zweck |
|------|:------:|-----|-------|
| `card_id` | ✓ | string `^[a-z]{2,4}_[0-9]{3}$` | Stabile ID, Dateiname, Primärschlüssel |
| `slug` | ✓ | string (kebab) | URL-stabil, eindeutig je Fachbereich |
| `title` | ✓ | string | Anzeigename |
| `subtitle` | – | string | Kurzeinordnung |
| `module` | ✓ | enum | Distributions-/Paketcode (Print/Moodle-Bündelung) |
| `primary_category` | ✓ | enum | Aktiver Register-Tab (Kap. 03) |
| `secondary_categories` | – | enum[] | Dezente Nebentabs |
| `topic_group` | – | string | Gruppe für Vollständigkeitsprüfung (Kap. 14) |
| `tags` | – | string[] | Freies, kontrolliertes Vokabular (`tags.yaml`) |
| `difficulty` | – | enum | beginner/intermediate/advanced |
| `front_type` | ✓ | enum | Kartentyp vorne (Kap. 13) |
| `front_content` | ✓ | object | Typabhängiger Inhalt (Struktur/Begriff/Bild …) |
| `back_sections` | ✓ | object | Feste Rückseiten-Sektionen (Kap. 05) |
| `biochemical/clinical/molecular_relevance` | – | bool | Facetten-Flags für Filter & Farblogik |
| `references` | – | string[] | Quellenangaben |
| `review_status` | ✓ | enum | Fachreview-Status (Kap. 14) |
| `version` | ✓ | semver | Inhaltsversion der Karte |
| `created_at`/`updated_at` | ✓ | date | Lebenszyklus |
| `related_cards` | – | card_id[] | Querverweise |
| `qr_url`/`lms_url` | ✓/– | uri | Print→Online-Brücke, LMS-Ziel |

**Abwärtskompatibilität:** `front_asset`/`back_asset` aus dem bestehenden CSV-Schema werden
beim Build *abgeleitet* (`generated/individual/front/<card_id>_front.png` …) und müssen nicht
mehr manuell gepflegt werden.

## 3. Kanonische Gesamtdatei

`normalize_cards` erzeugt aus allen `data/cards/*.yaml` eine validierte
`data/cards_master.json` (Array von Kartenobjekten + Metadaten-Header: Schemaversion, Build-Zeit,
Kartenanzahl je Kategorie). Diese Datei ist die Eingabe für **alle** Generatoren und den
Online-Seed. Die bestehende `cards/registry/cards.master.csv` wird als flache,
tabellen-/Moodle-freundliche Projektion daraus erzeugt (nicht mehr von Hand gepflegt).

## 4. Versionierung

- **Git** versioniert die YAML-Quelle (wer/was/wann über Commits).
- **`version` (semver)** je Karte: Patch = Korrektur, Minor = inhaltliche Ergänzung,
  Major = didaktische Neukonzeption.
- Im Online-System spiegelt die Tabelle `card_versions` jede inhaltliche Änderung als Snapshot
  (Kap. 11), sodass Änderungen auch außerhalb von Git (Editor im Admin-UI) nachvollziehbar sind.
- **Grundsatz:** Jede inhaltliche Änderung erhöht `version` **und** `updated_at`.

## 5. Validierungsregeln (hart)

1. `card_id`-Präfix == lowercase(`module`) (bestehende `oneOf`-Regel bleibt).
2. `slug` eindeutig je Fachbereich; `card_id` global eindeutig.
3. `primary_category` ∈ Tab-Taxonomie (Kap. 03); alle `tags` ∈ `tags.yaml`.
4. `front_type` passt zu `front_content` (z. B. `structure` ⇒ `smiles` oder `svg` vorhanden).
5. Aminosäuren-Vorderseiten dürfen **keinen Namen** tragen (Lint-Regel, Kap. 05).
6. `back_sections.classification` und mindestens eine Relevanz-Sektion vorhanden.
7. Bei `review_status: approved` müssen `reviewer` und `references` gesetzt sein.

Verstöße gegen 1–4/6 sind **Build-Fehler**; 5/7 sind **Warnungen mit `review_needed`-Flag**.
