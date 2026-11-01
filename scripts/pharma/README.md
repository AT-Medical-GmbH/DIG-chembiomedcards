# Pharma Cards Pipeline (Modul PH)

Reproduzierbare Pipeline für das Modul PH. Quelle der Wahrheit sind die Kartendaten
(`cards/PH/metadata/*.yaml`) und die Scope-Konfiguration (`cards/PH/scope/*.yaml`);
Bilder/HTML sind **Export-Artefakte**.

| Skript | Aufgabe |
|---|---|
| `validate_ph_cards.py` | PH-Content-Schema + Scope-Enums + Governance-Regeln prüfen |
| `build_registry.py` | ph_*-Zeilen in `cards/registry/cards.master.csv` aus YAML erzeugen (Nicht-PH unangetastet) |
| `render_cards.py` | Vorder-/Rückseiten als self-contained HTML; optional PNG/PDF via Chromium |
| `validate_output.py` | erzeugte Ausgabe + Export-Gating (critical → nur approved) |
| `review_report.py` | Liste offener Reviews mit Prüfschwerpunkten → `docs/pharma-cards/reports/cards_review_needed.md` |
| `check_layout.py` | misst in Chromium Überlauf und 5-mm-Sicherheitszone je Kartenseite → `reports/layout_review.md` |
| `generate_moodle_import.py` | Moodle-Pakete je Paket aus `scope/packages.yaml` (CSV, HTML-CSV, TAB, Semikolon, Bilder, Manifest, ZIP) |
| `generate_print_sheets.py` | Druckpakete: A4/A3-Bögen 2/4/8-up, Duplex-Spiegelung, Schnittmarken, Beschnitt, Einzel-PDF, PNG |
| `tests/` | pytest: Gating, Paketzuordnung, Formate, Ausschießen, Duplex, QR, Überlauferkennung |

## Schnellstart

```bash
make ph-validate        # Daten prüfen
make ph-registry        # Registry aktualisieren
make ph-render          # HTML erzeugen (exports/web/ph/html/)
make ph-output-check    # Ausgabe + Gating prüfen
make ph-all             # alles nacheinander
```

## Export (Moodle / Druck)

```bash
make ph-moodle-preview PYR=/pfad/zu/venv/bin/python   # Vorschau inkl. Karten im Review
make ph-print-preview  PYR=/pfad/zu/venv/bin/python
make ph-moodle && make ph-print                        # Release: nur freigegebene Karten
```

Release-Läufe nehmen nur exportierbare Karten auf (`critical` nur `approved`). Pakete ohne
freigegebene Karten werden übersprungen. `ph-print` läuft erst nach bestandener
Layout-Prüfung (`ph-layout-check --strict`): Abgeschnittener Text wird nie gedruckt.
Vorschaupakete liegen getrennt unter `dist/preview/` und tragen ein ENTWURF-Wasserzeichen.

## Abhängigkeiten

- Pflicht: Python 3.11+, PyYAML.
- Für Rendering, Druck, Moodle-Bilder und Layoutprüfung: `playwright==1.56.0` (nutzt das
  vorinstallierte Chromium, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) und `qrcode` für echte
  QR-Codes. Ohne Playwright bleibt die HTML-Ausgabe maßgeblich; ohne `qrcode` erscheint ein
  QR-Platzhalter, und das Druck-README warnt davor.
- Tests: `pytest`.

## Hinweise

- Generierte Binärdateien (PNG/PDF) sind per `.gitignore` ausgeschlossen und werden
  in CI/Deployment erzeugt. HTML-Previews unter `exports/web/ph/html/` sind Text und
  werden versioniert, um die Pipeline nachvollziehbar zu machen.
- Export-/Release-Läufe nutzen `make ph-release-check` und spielen nur `approved`
  (bzw. `reviewed`, je Warnlevel) Karten aus.
