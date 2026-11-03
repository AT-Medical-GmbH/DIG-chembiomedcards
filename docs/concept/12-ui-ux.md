# 12 — UI/UX-Konzept (Online-System)

Aufbauend auf `online-platform/frontend/*` (tablet-/desktop-/smartphone-layout, ux-requirements).

## 1. Designprinzipien

- Klare **medizinisch-wissenschaftliche** Optik; ruhige, **helle** Oberfläche; professionelles
  CME-/Medizin-Lernsystem — **kein verspieltes Lernspielzeug-Design**.
- Hochwertige, **dezente** Kartenanimationen (3D-Flip), schnelle Ladezeiten.
- **Responsive**: Desktop, Tablet (Tablet-first gemäß Repo), Smartphone; touch-freundlich.
- **Barrierearm**: große, gut lesbare Schrift, hohe Kontraste (WCAG AA+), sichtbarer Fokus,
  vollständige Tastaturbedienung, `prefers-reduced-motion` respektiert.
- Gestaltung zieht Farben/Typo aus denselben **Design-Tokens** wie die Karten (Kap. 05) → eine
  visuelle Sprache für Print und Online; passend zur AT-Medical-Webseite.

## 2. Hauptansichten

1. **Dashboard** — heute fällig, Streak, Fortschritt je Kategorie, Schnellstart.
2. **Kategorienübersicht** — die 6 Tabs als Einstieg, Kartenzahlen/Beherrschung.
3. **Kartenset-Übersicht** — Liste/Grid mit Filter (Tags), Suche, Status-Badges.
4. **Lernmodus** — zentrale Lernkartenansicht (siehe §3).
5. **Wiederholungsmodus** — SRS-gesteuert, „nur fällige/unsichere“.
6. **Karteneditor** (Editor/Admin) — Formular + Live-Layout-Vorschau.
7. **Notizenansicht** — alle eigenen Notizen, durchsuchbar, exportierbar.
8. **Fortschrittsstatistik** — Diagramme (Fälligkeiten, Beherrschungsgrad, Aktivität).
9. **Exportcenter** — Karte/Set/Kategorie als PNG/PDF, Druckpaket.
10. **Admin-/Review-Bereich** — Review-Queue, Statuswechsel, Import, Sync.

## 3. Lernkartenansicht (Detail)

```
┌──────── Register-Tabs (aktiv hervorgehoben) ────────┐
│                                                     │
│                 ┌───────────────┐                    │
│                 │    KARTE       │  ← Flip (Front/Back)│
│                 └───────────────┘                    │
│   [Gelernt] [Wiederholen] [Unsicher] [Beherrscht]    │
│   [Notiz]   [Download]     [Drucken]                  │
│   ▓▓▓▓▓▓▓▓░░░░ Fortschrittsbalken   ⏱ (optional)      │
├─────────────────────────────────────────────────────┤
│ ▸ Notizen (einklappbar, Autospeicherung)             │
└─────────────────────────────────────────────────────┘
```

- **Flip** per Klick/Tap/Swipe/**Leertaste**; **Vollbild** und **Fokusmodus**.
- **Tastaturkürzel**: `Space` flip · `←/→` zurück/weiter · `1–4` Status · `n` Notiz · `f` Fokus.
- **Swipe-Gesten** auf Touch: links/rechts = navigieren, hoch = Notiz, Doppeltipp = flip.

## 4. Notizenbereich

Unterhalb der Karte, einklappbar; Rich-Text-light/Markdown; **Autospeicherung** mit
Zeitstempel; optionaler Export. Dozenten-/Kursnotizen deutlich getrennt von privaten Notizen.

## 5. Annotationen (Overlay)

Werkzeugleiste über der Karte: Text · Pfeil · Markierung · Kreis/Rechteck · Freihand.
Annotationen liegen als Overlay über dem Kartenbild (nicht destruktiv, Kap. 09 §4); Ein-/Ausblenden
per Toggle; Export bindet sie optional ein.

## 6. Interaktion & States

- Klare Lade-/Leer-/Fehlerzustände; optimistische Status-Updates mit Server-Bestätigung.
- Offline-tolerant im Lernmodus (Set vorab geladen; Reviews werden nachsynchronisiert) — Ausbau,
  nicht MVP-Pflicht.

## 7. Einbettung

- **Webcomponent** `<chembiomed-cards set="biochemie-aminosaeuren">` für WordPress-Shortcode.
- **iframe** für Moodle (interim), vollwertig via **LTI-Launch** (Kap. 08).
- Eingebettete Ansicht respektiert das Host-Theme (heller Kartenkern auch auf dunklem Moodle-Theme).
