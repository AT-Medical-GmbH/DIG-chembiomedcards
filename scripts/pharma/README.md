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

## Schnellstart

```bash
make ph-validate        # Daten prüfen
make ph-registry        # Registry aktualisieren
make ph-render          # HTML erzeugen (exports/web/ph/html/)
make ph-output-check    # Ausgabe + Gating prüfen
make ph-all             # alles nacheinander
```

## Abhängigkeiten

- Pflicht: Python 3.11+, PyYAML.
- Optional (nur `ph-render-png`): Playwright + das vorinstallierte Chromium
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). Ohne Playwright bleibt die
  HTML-Ausgabe maßgeblich; PNG/PDF werden übersprungen.

## Hinweise

- Generierte Binärdateien (PNG/PDF) sind per `.gitignore` ausgeschlossen und werden
  in CI/Deployment erzeugt. HTML-Previews unter `exports/web/ph/html/` sind Text und
  werden versioniert, um die Pipeline nachvollziehbar zu machen.
- Export-/Release-Läufe nutzen `make ph-release-check` und spielen nur `approved`
  (bzw. `reviewed`, je Warnlevel) Karten aus.
