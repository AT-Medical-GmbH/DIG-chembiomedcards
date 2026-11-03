# 11 — Import- & Audit-Pipeline

**Dokument:** Automatisiertes Einlesen, Prüfen, Bereinigen, Vereinheitlichen späterer Uploads
**Handover-Phasen:** 1 (Pipeline), 4 (Vollständigkeits-/Review-Reports)

---

## 1. Zweck

Wenn später vorhandene Karten, Tabellen, Skripte, PDFs oder Listen hochgeladen werden, sollen sie
**automatisiert** eingelesen, geprüft, bereinigt, vereinheitlicht und in das System überführt werden —
nicht manuell zusammengebaut. Diese Pipeline definiert den reproduzierbaren Weg vom Upload zur
validierten Karte im Repo.

---

## 2. Verzeichniskonvention (erweitert bestehende `imports/`)

```
imports/
  csv/              # bestehend — CSV-Importe
  yaml/             # bestehend — YAML-Importe
  source-material/  # bestehend — Quellmaterial
  pharma/           # NEU bei erstem Upload:
    uploaded_raw/   # unveränderte Originale (untrusted, read-only behandeln)
    extracted/      # extrahierte, strukturierte Zwischenform
    rejected/       # aussortierte/fehlerhafte Einträge + Grund
```

**Sicherheit:** Hochgeladenes ist **untrusted data**. Jeder Upload in ein eigenes, leeres Verzeichnis;
Extraktionsskripte liegen getrennt und erhalten Pfade als Argument (keine Interpreterausführung aus dem
Upload-Verzeichnis; Python mit `-I`). Keine Secrets einlesen/ausgeben.

---

## 3. Pipeline-Stufen

```
(1) extract_uploaded_files.py   uploaded_raw/*  →  extracted/*.yaml (+ Herkunftslog)
(2) normalize_cards.py          extracted/      →  vereinheitlichte Felder, Slugs, Enums
(3) audit_cards.py              normalize-Ausg. →  data/audit_report.json + reports/*.md
(4) (manuell) Review/Freigabe   audit-Ergebnis  →  cards/PH/metadata/*.yaml (übernommen)
(5) generate_* / validate_*     wie Dok. 06     →  Registry/Exporte/Seed
```

### 3.1 `extract_uploaded_files.py`
- Liest CSV/XLSX/YAML/JSON und — soweit möglich — PDFs/Listen; erzeugt pro Kandidat einen
  strukturierten Zwischen-Datensatz in `extracted/`.
- Protokolliert Herkunft (Quelle, Zeile/Seite), damit jede Aussage rückverfolgbar bleibt.

### 3.2 `normalize_cards.py`
- Feldnamen auf das PH-Content-Schema abbilden (Synonyme/Aliasse auflösen).
- Slugs erzeugen (`ph_###_<slug>`), Kategorien/Wirkstoffgruppen/Tags gegen `scope/*.yaml` normalisieren.
- Einheitliche Schreibweisen (Wirkstoffnamen, INN), Markdown-Bereinigung, Längen kürzen/markieren.
- Unbekannte Kategorien/Tags → Vorschlag für `scope/*.yaml`, **nicht** automatisch anlegen.

### 3.3 `audit_cards.py` → `audit_report.json` + Reports
Prüft und berichtet:
- **Pflichtfelder & Enums** (Scope-Validierung).
- **Dubletten** (gleicher Wirkstoff/Slug/sehr ähnlicher Inhalt) → `reports/duplicate_cards.md`.
- **Fehlende Karten** vs. kuratierter Startliste → `reports/missing_cards.md`.
- **Inhaltlicher Prüfstatus** → `reports/content_review.md`.
- **Dosierungs-Flag-Konsistenz** (Zahlendosis ohne Quelle/Review → Fund).
- **Rückseitenlänge/Layout-Tauglichkeit** → `reports/layout_review.md`.
- **Warnlevel-Plausibilität** (Antidot/Katecholamin/Antikoagulans → mind. high/critical).
- **Review-Bedarf** → `reports/cards_review_needed.md`.

### 3.4 Übernahme
Nur **nach menschlicher Freigabe** werden normalisierte, auditierte Datensätze als
`cards/PH/metadata/*.yaml` übernommen (mit passendem `review_status`). Nichts wird blind importiert;
`rejected/` dokumentiert Aussortiertes mit Grund.

---

## 4. Audit-Report-Struktur (`data/audit_report.json`, Soll)

```json
{
  "run_at": "YYYY-MM-DDThh:mm:ssZ",
  "input": "imports/pharma/extracted",
  "summary": { "candidates": 0, "valid": 0, "rejected": 0, "duplicates": 0, "review_needed": 0 },
  "findings": [
    { "card_ref": "ph_xxx|slug", "severity": "error|warning|info",
      "type": "missing_field|enum|duplicate|dose_without_source|too_long|warning_level",
      "message": "…", "source": "datei:zeile|pdf:seite", "suggestion": "…" }
  ],
  "reports": ["reports/missing_cards.md", "reports/duplicate_cards.md", "reports/content_review.md"]
}
```

---

## 5. Reproduzierbarkeit & CI

- Jede Stufe idempotent, über `scripts/` und `make` aufrufbar; CI kann Audit als PR-Gate laufen lassen.
- Der Audit-Report ist das Bindeglied zwischen Upload und Review — er macht Qualität messbar und
  Fortschritt sichtbar, bevor Karten in den produktiven Bestand gelangen.
