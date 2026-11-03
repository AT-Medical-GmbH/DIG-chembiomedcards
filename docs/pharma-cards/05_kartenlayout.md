# 05 — Kartenlayout

**Dokument:** Einheitliches Kartenlayout, Tab-System, Farblogik, Front-/Back-Typen
**Handover-Phase:** 5

---

## 1. Grundlage: bestehender Layoutstandard

Pharma Cards übernimmt **vollständig** den ChemBioMed-Cards-Layoutstandard
(`card-system/layout-standard/`) und präzisiert ihn für pharmakologisch-toxikologische Inhalte:

- **Format:** DIN A6 quer (148×105 mm), Beschnitt 3 mm, Safe Zone 5 mm, CMYK/300 dpi, PDF/X (Print-Spec).
- **Logo** rechts oben, **Karten-ID** links unten, **Copyright** rechts unten, **QR** rechts unten.
- **Inward-Tabs** oben links, laufen nach innen (keine Stanzproblematik), farbiger oberer Kartenrand
  erzeugt den Registereffekt.
- Ein Layout für **Print und Online** (dieselbe HTML/CSS-Quelle, zwei Rendering-Ziele).
- Keine unnötigen schwarzen Außenränder, helle ruhige Oberfläche, dichte klare Typografie.

**Regel:** Keine spontanen Layoutwechsel zwischen Karten. Das Layout wird aus Daten + Konfiguration
gesteuert, nie pro Karte frei gestaltet.

---

## 2. Tab-System (oben)

Konsistente Registerstruktur über **alle** PH-Karten. Die Tabs entsprechen den inhaltlichen Achsen der
Rückseite und machen den Kartentyp sofort erkennbar.

**Tab-Set (fix, über alle Karten identisch):**

`Allgemein` · `PK/PD` · `Wirkstoff` · `Klinik` · `Tox` · `Antidot` · `Interaktion`

- Der **aktive Haupttab** (zum Kartentyp passend) wird kräftig hervorgehoben (volle Akzentfarbe).
- **Nebentabs**, zu denen die Karte Inhalt hat, werden dezent markiert (gedämpfte Farbe).
- Tabs ohne Inhalt bleiben neutral/ausgegraut, bleiben aber sichtbar (Konsistenz).
- Die Tab-Zuordnung je Kartentyp steht in `card_types.yaml` (kein Hardcoding im Template).

| Kartentyp | aktiver Haupttab |
|---|---|
| Wirkstoffkarte | `Wirkstoff` |
| Wirkmechanismuskarte | `PK/PD` |
| Toxidromkarte | `Tox` |
| Antidotkarte | `Antidot` |
| Interaktionskarte | `Interaktion` |
| Fallkarte | `Klinik` |
| Prinzip/Übersicht | `Allgemein` |

---

## 3. Farblogik

Die Farbrollen sind in `card_types.yaml` (Back-Sections) und `categories.yaml`/`warning_levels.yaml`
verankert — Templates lesen sie, verdrahten sie nicht.

| Rolle | Farbe | Verwendung |
|---|---|---|
| `base` | Dunkelgrau/Schwarz `#37474F` | Grundinformation, Stoffklasse, Definition |
| `pkpd` | Blau `#1E88E5` | PK/PD, Wirkmechanismus, Signalweg |
| `clinic` | Grün `#43A047` | klinische Anwendung, Indikation |
| `risk` | Rot `#E53935` / kritisch `#B71C1C` | Warnungen, KI, schwere NW, Toxikologie |
| `interaction` | Orange `#FB8C00` | Interaktionen, Monitoring |
| `antidote` | Violett `#8E24AA` | Antidot, Spezialwissen, Merkhilfen |

Akzente bleiben dezent und AT-Medical-konform. Warnlevel wird zusätzlich als Badge dargestellt
(sichtbar bei `high`/`critical`).

---

## 4. Vorderseiten (nach `front_type`)

Je Kartentyp eine feste, aber knappe Vorderseite — **keine vollständige Lösung vorn**:

1. **Wirkstoffkarte** (`substance`/`structure`): Wirkstoffname (ggf. Strukturformel), Wirkstoffgruppe,
   optional Kategorie-Icon. Keine Lösung.
2. **Wirkmechanismuskarte** (`mechanism`): Frage oder Schema („Wie wirkt Naloxon?“), optional einfaches
   Rezeptor-/Pathway-Schema.
3. **Toxidromkarte** (`toxidrome`): Name des Toxidroms oder Leitsymptom-Cluster, optional Warnsymbol.
4. **Antidotkarte** (`antidote`): **Giftstoff/Intoxikation** vorn, Antidot auf der Rückseite.
5. **Interaktionskarte** (`interaction`): Kombination/Problem vorn, Mechanismus+Konsequenz hinten.
6. **Fallkarte** (`case`): kurze Fallvignette vorn, Lösung+Begründung+Fallstricke hinten.

---

## 5. Rückseiten (konsistent, Box-Struktur aus `card_types.yaml`)

**Layout-Raster (alle Rückseiten):**

```
┌─ Tab-Leiste ───────────────────────────────────────────┐
│ Titelbereich (Titel · Wirkstoffgruppe · Warnlevel-Badge)│
├─────────────────────────────────────────────────────────┤
│ breite Box: KERNMECHANISMUS / Leitaussage  (pkpd/base)  │
├───────────────────────────┬─────────────────────────────┤
│ Box: KLINIK (clinic)      │ Box: RISIKEN/TOX (risk)     │
├───────────────────────────┴─────────────────────────────┤
│ (optional) Box: INTERAKTION/MONITORING (interaction)    │
├─────────────────────────────────────────────────────────┤
│ kompakte Box: MERKE / FALLSTRICK (antidote)             │
└─────────────────────────────────────────────────────────┘
  ID (links unten) · QR + © (rechts unten)
```

**Standard-Boxfolgen je Typ** (Defaults, in `card_types.yaml`):

- **Wirkstoffkarte:** Wirkstoffgruppe · Wirkmechanismus · Indikationen · Nebenwirkungen ·
  Kontraindikationen/Warnhinweise · Interaktionen/Monitoring · Merke.
- **Toxikologie-/Toxidromkarte:** Leitsymptome · Pathophysiologie · Diagnostik/Monitoring ·
  Akuttherapie · Antidot · Red Flags · Merke.
- **Antidotkarte:** Zielintoxikation · Wirkprinzip · Anwendungskontext · Risiken/Cave · Merke.

Gestaltungsregeln: dezente Icons, konsistente Abstände/Schriftgrößen, klare visuelle Hierarchie,
nicht überladen. Rückseiten nicht überlang (harte Längenprüfung im Audit, Dok. 11).

---

## 6. Online-Kartentemplate

Dieselbe HTML/CSS-Struktur wird für die Online-Ansicht wiederverwendet (responsives Flip-Layout):

- Vorder-/Rückseite als CSS-Flip (Klick/Tap/Swipe/Leertaste).
- Tabs bleiben oben sichtbar; aktiver Tab hervorgehoben.
- Warnlevel-Badge bei `high`/`critical` prominent.
- Rendern **aus strukturierten Feldern** (`front_content`/`back_content` JSONB), nicht aus Bild.
- Print/Download erzeugen aus derselben Quelle PNG/PDF (Playwright).

---

## 7. Template-Artefakte (Folgephase, Ort)

- `card-system/templates/card-template-front.html` / `card-template-back.html` — bestehende Ablage,
  wird um PH-Varianten (Box-Slots, Tab-Leiste, Farbrollen) erweitert.
- `card-system/card-types/` — je Kartentyp eine Konfigurations-/Beispielansicht.
- CSS-Design-Tokens (`brand/design-tokens/`, `brand/colors/`) liefern Farben/Typografie — Templates
  referenzieren Tokens, keine Inline-Farben.

---

## 8. Umsetzung und Messung (Stand 2026-10-31)

Festlegungen, die bei der Umsetzung der Druckpipeline getroffen und gemessen wurden:

| Punkt | Festlegung | Begründung |
|---|---|---|
| Sicherheitszone | Alle Inhalte (Tabs, Titel, Badge, Boxen, ID, ©, QR) ≥ 5 mm von der Schnittkante | `print-production/specs/bleed-and-safe-zone.md`; frühere 4-mm-Ränder waren zu knapp |
| QR-Code | echter Code, 15 × 15 mm, Fehlerkorrektur Q, Ruhezone 4 Module, **nur Vorderseite** rechts unten | Spezifikation verlangt ≥ 15 mm; auf der dichten Rückseite fehlte dafür der Platz. Der Standard fordert „rechts unten“, nicht „beidseitig“. |
| Rückseite | Kern- und Merke-Box über volle Breite, dazwischen **Zweispaltenfluss** | Starre Paarzeilen verschenkten Höhe; der Fluss senkte den gemessenen Überlauf von 16 auf 4 Karten, ohne die Schrift zu verkleinern |
| Schriftgröße Boxtext | 2,75 mm (≈ 7,8 pt) | Untergrenze für Lesbarkeit im Druck nicht unterschritten |
| Toxidrom ohne klassisches Antidot | Antidot-Hinweis in die Akuttherapie-Box statt eigener Box | hielt die Rückseite druckfähig, ohne Sicherheitsaussagen zu streichen |
| Überlaufschutz | `scripts/pharma/check_layout.py` misst jede Kartenseite in Chromium; `make ph-print` läuft nur ohne Befund | Karte hat `overflow: hidden` – abgeschnittener Text wäre sonst unbemerkt gedruckt worden |

Aktueller Messstand: `reports/layout_review.md`.
