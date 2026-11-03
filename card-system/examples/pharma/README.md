# Pharma Cards — Beispiel-Renders

Committete, direkt im Browser ansehbare Beispielausgaben der Render-Pipeline
(`scripts/pharma/render_cards.py`). Sie zeigen das einheitliche Layout (DIN A6 quer, Tab-Leiste oben,
farbrollen-codierte Boxen, Footer mit ID/QR/Copyright) für Fachreview und Abnahme.

| Datei | Karte | Typ |
|---|---|---|
| `ph_006_front.html` / `ph_006_back.html` | Agonist | Prinzip/Übersicht |
| `ph_020_front.html` / `ph_020_back.html` | LADME-Prinzip | Prinzip/Übersicht |
| `ph_040_front.html` / `ph_040_back.html` | Adrenalin | Wirkstoffkarte, `critical` (Entwurf) |
| `ph_100_front.html` / `ph_100_back.html` | Naloxon | Antidotkarte, `critical` (Entwurf) |

Die klinischen Beispiele sind **Entwürfe vor dem Fachreview** und dienen nur der Layoutabnahme.

Der vollständige Satz wird reproduzierbar erzeugt und ist nicht eingecheckt:

```bash
make ph-render          # exports/web/ph/html/ (HTML)
make ph-render-png      # zusätzlich PNG/PDF via Chromium (CI/Deployment)
```

Diese Beispiele werden bei Layoutänderungen manuell aktualisiert (`cp` aus `exports/web/ph/html/`).
