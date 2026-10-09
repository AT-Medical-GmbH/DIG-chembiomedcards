# 05 — Einheitliches Kartenlayout

Dieses Kapitel ist die **gestalterische Verfassung** des Projekts. Es konkretisiert den
bestehenden `card-system/layout-standard/` und macht ihn für die automatische Generierung
(Kap. 06) verbindlich. Leitplanke: **keine spontanen Layoutwechsel zwischen Karten.**

## 1. Format & Grundraster

- **Kartenformat:** DIN A6 quer, **148 × 105 mm** (bestehender Standard).
- **Beschnittzugabe:** 3 mm umlaufend (Endformat 154 × 111 mm im Druck).
- **Sicherheitsabstand:** 4 mm von der Endformatkante für Inhalte.
- **Auflösung Export:** 300 dpi für Druck (≈ 1819 × 1240 px inkl. Beschnitt), 2× für Online-PNG.
- Vorder- und Rückseite bilden **eine zusammenhängende Inhaltseinheit** (gleiche Karte).

## 2. Feste Bildschirm-/Druck-Zonen (beide Seiten)

```
┌───────────────────────────────────────────────┐
│ [Inward-Tabs oben links]              [Logo]   │  ← Kopfzone
│                                                │
│                 INHALTSZONE                     │
│                                                │
│ [Karten-ID unten links]   [QR] [© unten rechts]│  ← Fußzone
└───────────────────────────────────────────────┘
```

Verbindlich aus dem Bestand:
- **Logo** rechts oben, auf **beiden** Seiten.
- **Inward-Tabs** oben links, vom oberen Rand in die Karte laufend.
- **Karten-ID** dezent links unten.
- **Copyright** rechts unten; **QR-Code** rechts unten, **ohne** Footer zu überlagern.
- Inhalte dicht, klar, ohne unnötige Leerräume; **keine schwarzen Außenränder**.

## 3. Register-Tabs

- Immer **sechs Tabs** in fester Reihenfolge (Kap. 03): Allgemein · Anorganik · Organik ·
  Molekularbio · Biochemie · Klinik.
- **Aktiver Haupttab** (= `primary_category`) deutlich hervorgehoben (volle Akzentfarbe, Füllton).
- **Nebentabs** (= `secondary_categories`) dezent markiert (Punkt/feine Linie in Akzentfarbe).
- Inaktive Tabs: ruhiges Grau. Struktur **über alle Karten identisch**.

## 4. Farblogik (verbindlich)

| Bedeutung | Farbe | Einsatz |
|-----------|-------|---------|
| Grundinfo, Struktur, Stoffklasse | Dunkelgrau/Schwarz | Titel, Klassifikation, Eigenschaften |
| Biochemische Relevanz | **Grün** | Box „Biochemie“, Biochemie-Tab |
| Klinische Relevanz | **Rot** | Box „Klinik“, Klinik-Tab |
| Molekularbio / Signalwege / Regulation | **Blau** | Box „Molekularbio“, Molekularbio-Tab |
| Merkhilfen / Besonderheiten / Fun Fact | **Orange/Violett** | Box „Merke / Fun Fact“ |

Die Farben sind als **Design-Tokens** in `brand/design-tokens/chembiomed.tokens.json` zentral
definiert (bestehend) und werden von Print-Templates **und** Online-UI gemeinsam genutzt — eine
Farbquelle für alles. Akzente bleiben dezent und medizinisch-sachlich (AT-Medical-Linie).

## 5. Vorderseiten-Regeln

### 5.1 Aminosäuren — Fischer-Projektion (strikte Konvention)
- **Säuregruppe oben**, α-C-Atom mittig, **Aminogruppe links**, **Wasserstoff rechts**,
  **Rest unten**.
- Säurekopfgruppe **vollständig** zeichnen: C mit Doppelbindung zu O **und** Bindung zu OH —
  **nicht** nur „COOH“ schreiben.
- **Kein Aminosäurename** auf der Vorderseite (trainiert Wiedererkennung). → Lint-Regel (Kap. 02 §5).

### 5.2 Vitamine
- Vorderseite **nur mit Bezeichnung**, z. B. „Vitamin C“, „Vitamin B6“.

### 5.3 Andere Moleküle
- Saubere Strukturformel **oder** didaktisch geeignete schematische Darstellung.

**Grundsatz:** Vorderseiten sind **bewusst reduziert** und trainieren Wiedererkennung.

## 6. Rückseiten-Aufbau (feste Sektionen)

Jede Rückseite ist **gleich** aufgebaut (Reihenfolge verbindlich; leere Sektionen entfallen
sichtbar, nicht die Struktur):

1. **Titel / Name**
2. **Kurzklassifikation** (`back_sections.classification`)
3. **Eigenschaften** (breite Box, `general_properties`)
4. **Biochemische Relevanz** (grün) | **Klinische Relevanz** (rot) — nebeneinander
5. **Molekularbio / Signalweg** (blau) — nur wenn zutreffend
6. **Merke / Fun Fact / Besonderheit** (orange/violett) — kompakt unten

```
┌──────────────── Tab-Leiste ────────────────┐
│ Titel · Kurzklassifikation          [Logo] │
│ ┌─────────────── Eigenschaften ──────────┐ │
│ └────────────────────────────────────────┘ │
│ ┌── Biochemie (grün) ──┐ ┌── Klinik (rot) ─┐│
│ └──────────────────────┘ └─────────────────┘│
│ ┌──── Molekularbio / Signalweg (blau) ─────┐│  (optional)
│ └──────────────────────────────────────────┘│
│ ┌──── Merke / Fun Fact (orange) ───────────┐│
│ [ID]                        [QR]        [©] │
└──────────────────────────────────────────────┘
```

Regeln: dezente Icons, **nicht überladen**, konsistente Abstände und Schriftgrößen, klare
visuelle Hierarchie, keine überlangen Rückseiten (Lesbarkeit > Vollständigkeit).

## 7. Typografie

Aus `brand/typography/typography-system.md`: eine klare, gut lesbare Schriftfamilie,
definierte Stufen für Titel / Section-Header / Fließtext / Fußnote. Mindestgröße im Druck so,
dass A6-Inhalte bei normalem Leseabstand lesbar bleiben; dieselben Stufen als CSS-Variablen im
Online-System.

## 8. Konsistenz-Garantie durch Generierung

Weil **alle** Karten aus **einem** HTML/SVG-Template + Tokens gerendert werden (Kap. 06), ist die
Einheitlichkeit technisch erzwungen — nicht per Handarbeit erhofft. Abweichungen sind nur über
Template-/Token-Änderungen möglich und wirken dann auf **alle** Karten gleichzeitig.
