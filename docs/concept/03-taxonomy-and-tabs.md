# 03 — Taxonomie, Register-Tabs & Tags

## 1. Zwei Dimensionen, nicht vermischen

ChemBioMed Cards hat **zwei unabhängige Ordnungsdimensionen**. Sie werden bewusst getrennt,
weil sie unterschiedliche Zwecke erfüllen:

| Dimension | Feld | Zweck | Sichtbar als |
|-----------|------|-------|--------------|
| **Register-Tab** (fachliche Zuordnung) | `primary_category` + `secondary_categories` | Fachliche Verortung, Farblogik, Filter, konsistente Tab-Leiste | Tab-Leiste oben auf jeder Karte |
| **Modul / Paket** (Distribution) | `module` | Bündelung für Druck-/Moodle-/Kaufpakete | Paketname, Kartennummernkreis |

Eine Karte liegt z. B. im **Modul BC** (Biochemie-Paket), hat aber `primary_category: biochemie`
und `secondary_categories: [organik, klinik]` — sie erscheint also im Biochemie-Tab aktiv und in
Organik/Klinik dezent markiert.

## 2. Register-Tabs (fest, über alle Karten identisch)

> **Stand 2026-10-31 (ADR-022):** „Allgemein“ und „Anorganik“ sind zu einem Tab zusammengelegt – die
> Leiste hat fünf Tabs. Maßgeblich ist `data/categories.yaml`; die Tabelle unten ist entsprechend angepasst.

Gemäß Handover sind die **sechs festen Tabs** (Reihenfolge verbindlich):

| Reihenfolge | Tab-Label | `primary_category`-Wert | Farbe (Akzent) |
|:-:|-----------|-------------------------|----------------|
| 1 | **Allg./Anorganik** | `allgemein_anorganik` | Logo-Navy (ADR-022: ein gemeinsamer Tab) |
| 3 | **Organik** | `organik` | Dunkelgrau/Schwarz |
| 4 | **Molekularbio** | `molekularbio` | Blau |
| 5 | **Biochemie** | `biochemie` | Grün |
| 6 | **Klinik** | `klinik` | Rot |

Regeln (aus dem Layoutstandard, Kap. 05):
- Die **Tab-Struktur ist auf jeder Karte identisch** — nie spontan ändern.
- Der **aktive Haupttab** (= `primary_category`) wird deutlich hervorgehoben.
- **Nebentabs** (= `secondary_categories`) werden dezent markiert.
- Tabs sind **Inward-Tabs oben links** (bestehender Repo-Standard
  `card-system/layout-standard/inward-tabs-system.md`).

Die Tab-Definition liegt in `data/categories.yaml` — **nicht** im Layout-Code. So lässt sich die
Taxonomie später erweitern (Kap. 13), ohne Templates anzufassen.

```yaml
# data/categories.yaml
tabs:
  - key: allgemein     ; label: "Allgemein"    ; color: "#2b2f36" ; icon: atom
  - key: anorganik     ; label: "Anorganik"    ; color: "#2b2f36" ; icon: flask
  - key: organik       ; label: "Organik"      ; color: "#2b2f36" ; icon: hexagon
  - key: molekularbio  ; label: "Molekularbio" ; color: "#2563eb" ; icon: dna
  - key: biochemie     ; label: "Biochemie"    ; color: "#059669" ; icon: cycle
  - key: klinik        ; label: "Klinik"       ; color: "#dc2626" ; icon: stethoscope
```

> Hinweis: YAML-Syntax oben schematisch; die reale Datei nutzt Standard-Listen-Objekte.

## 3. Modul-/Paket-Codes (Distribution)

Bestehender Repo-Stand (`cards.master.schema.json`) — bleibt unverändert gültig:

| Modul | Bedeutung |
|-------|-----------|
| **AC** | Allgemeine und anorganische Chemie |
| **OC** | Organische Chemie |
| **BC** | Biochemie |
| **MB** | Molekularbiologie der Zelle |
| **APC** | Angewandte Chemie, Ernährung & Medizin |
| **PH** | Pharmakologie (strukturell vorbereitet) |

## 4. Mapping Modul → Register-Tab

Das Mapping ist **nicht 1:1** — und genau deshalb sind beide Dimensionen getrennt:

| Modul | Typischer `primary_category`-Tab | Häufige Nebentabs |
|-------|----------------------------------|-------------------|
| AC | `allgemein` oder `anorganik` | — |
| OC | `organik` | `biochemie` |
| BC | `biochemie` | `organik`, `klinik`, `molekularbio` |
| MB | `molekularbio` | `biochemie` |
| APC | `klinik` | `biochemie` |
| PH | `klinik` | `biochemie`, `molekularbio` |

## 5. Offener Abstimmungspunkt (kein stilles Überschreiben)

Das Handover nennt als Hauptbereiche sechs Kategorien (inkl. getrennt „Allgemeine Chemie“ und
„Anorganische Chemie“) und listet als Tabs: *Allgemein, Anorganik, Organik, Molekularbio,
Biochemie, Klinik*. Der Bestand fasst **AC = Allgemeine + Anorganische Chemie** in **einem**
Modul zusammen und hat zusätzlich **APC** (Ernährung/Medizin) und **PH** (Pharma).

**Vorschlag (umgesetzt in diesem Konzept):** Die sichtbare **Tab-Taxonomie folgt dem Handover**
(6 feste Tabs), die **Modul-/Paketcodes bleiben wie im Bestand**. Das Mapping (Abschnitt 4)
verbindet beide. Dadurch bleiben vorhandene IDs/Registry/Schema stabil **und** die Handover-
Vorgabe zur konsistenten Tab-Leiste ist erfüllt.

→ Dieser Punkt ist in den [offenen Fragen](open-questions.md) zur ausdrücklichen Bestätigung
durch Andreas vermerkt (insb. ob APC/PH eigene Tabs bekommen sollen, sobald Inhalte wachsen).

## 6. Tag-System

Tags sind ein **kontrolliertes Vokabular** in `data/tags.yaml` (Build-Validierung verhindert
Tippfehler/Wildwuchs). Tag-Gruppen:

- **Stoffklasse**: `aminosaeure`, `kohlenhydrat`, `lipid`, `nukleotid`, `vitamin`, `hormon`,
  `neurotransmitter`, `coenzym`, `second-messenger` …
- **Eigenschaft**: `polar`, `unpolar`, `essenziell`, `glukogen`, `ketogen`, `sauer`, `basisch` …
- **Pathway/Funktion**: `citratzyklus`, `harnstoffzyklus`, `glykolyse`, `signaltransduktion` …
- **Klinik**: `laborwert`, `leberwert`, `mangelerkrankung`, `diagnostik` …

Tags sind die Grundlage für **Filter, Suche und „schwierige Karten separat üben“** im
Online-System (Kap. 09) und für thematische Teilexporte.

## 7. Substanz-Register

`data/substances.yaml` ist ein fachliches Hilfsregister: kanonische Stoffnamen,
Synonyme/Schreibweisen (z. B. „Aspartat/Asparaginsäure“), optional SMILES/Strukturreferenz.
Es dient (a) der **Vollständigkeitsprüfung** (Kap. 14 / [04](04-import-audit-pipeline.md)) gegen
die Soll-Liste und (b) der **Dubletten-/Synonym-Erkennung** beim Import.
