# Fachreview: Ablauf und Rollen

**Gilt für:** alle PH-Karten mit `warning_level` `high` oder `critical` sowie alle Karten mit
`review_status` `clinical_review_needed` oder `toxicology_review_needed`.
**Grundlage:** `../10_review-sicherheit-und-governance.md`, `cards/PH/scope/review_status.yaml`.

---

## 1. Zweck

Klinisch relevante Lernkarten werden erst nach einer dokumentierten fachlichen Prüfung freigegeben.
Dieses Verzeichnis macht die Prüfung praktisch durchführbar. Es legt Rollen, Reihenfolge,
Checklisten und das Protokoll fest.

Die Karten selbst bleiben Ausbildungsmaterial und sind keine Therapieanweisung. Die Prüfung stellt
sicher, dass sie fachlich korrekt, aktuell und didaktisch nicht irreführend sind.

---

## 2. Rollen

| Rolle | Kürzel in den Daten | Aufgabe | Benannt |
|---|---|---|---|
| Redaktion | `editor` | Entwurf, Formulierung, Umsetzung der Korrekturen | AT Medical GmbH |
| Fachreviewer Pharmakologie | `reviewer_pharm` | Wirkmechanismus, Indikation, NW, KI, Interaktionen, Dosierungsprinzip | Andreas Tremml (seit 2026-10-31) |
| Fachreviewer Toxikologie | `reviewer_tox` | Toxidrome, Antidote, Akuttherapie, Red Flags | Andreas Tremml (seit 2026-10-31) |
| Freigabe | `admin` | Setzt `approved`, wenn alle nötigen Prüfungen vorliegen | Andreas Tremml |

Eine Person darf nicht ihren eigenen Entwurf fachlich freigeben (Vier-Augen-Prinzip). Die Entwürfe
stammen von der Redaktion; Andreas Tremml prüft und gibt frei.

> **Empfehlung:** Weil Fachprüfung und Freigabe derzeit bei derselben Person liegen, sollte für
> `critical`-Karten (Antidote, Katecholamine) zusätzlich eine zweite fachkundige Person gegenlesen.
> Das zweite Lesen wird im Protokoll vermerkt.

Wer eine Karte prüft, trägt sich erst bei der tatsächlichen Prüfung im Feld `reviewer` der Karte ein.

---

## 3. Welche Prüfung braucht welche Karte?

| Kartentyp | Pharmakologie | Toxikologie | Klinische Sicherheit |
|---|:---:|:---:|:---:|
| Wirkstoffkarte (`substance`) | ✓ | – | ✓ |
| Toxidromkarte (`toxidrome`) | – | ✓ | ✓ |
| Antidotkarte (`antidote`) | ✓ | ✓ | ✓ |
| Interaktionskarte (`interaction`) | ✓ | bei Tox-Bezug | ✓ |
| Prinzipkarte `low`/`moderate` | ✓ | – | – |

Die klinische Sicherheitsprüfung (`checkliste_klinische_sicherheit.md`) wird vom jeweils
zuständigen Fachreviewer mit erledigt. Sie ist keine eigene Person, aber ein eigener Prüfschritt.

---

## 4. Ablauf je Karte

```
Entwurf (editor)
  └─ review_status: clinical_review_needed / toxicology_review_needed
       │
       ▼
Fachprüfung (reviewer_pharm / reviewer_tox)
  ├─ Checkliste abarbeiten
  ├─ review_focus der Karte gezielt prüfen
  ├─ Quelle(n) mit Jahr in references eintragen
  └─ Protokoll ausfüllen (review_protokoll_vorlage.md)
       │
       ├─ Korrektur nötig → zurück an editor → erneute Prüfung
       └─ fachlich korrekt → review_status: reviewed
              │
              ▼
Freigabe (admin)
  └─ alle nötigen Prüfungen nach Abschnitt 3 dokumentiert → review_status: approved
```

Wer prüft, trägt sich in `reviewer` ein. Bei jeder inhaltlichen Änderung wird `version` erhöht und
`updated_at` gesetzt.

---

## 5. Regeln, die das Review nicht aufweichen darf

- **Dosierungen:** Konkrete Zahlen kommen nur mit Quelle (Leitlinie/Fachinformation mit Jahr) auf die
  Karte. Dann wird `dose_contains_numeric: true` gesetzt. Im Zweifel bleibt es beim
  Dosierungsprinzip.
- **Unsicherheit:** Nicht raten. Karte auf `*_review_needed` lassen und den offenen Punkt in
  `review_focus` festhalten.
- **Export-Gating:** `critical`-Karten werden nur mit `approved` exportiert. Die Pipeline erzwingt das
  (`make ph-release-check`).
- **Aktualität:** Bei Leitlinien- oder Zulassungsänderungen wird `update_needed` gesetzt und die Karte
  erneut geprüft.

---

## 6. Dateien

| Datei | Inhalt |
|---|---|
| `checkliste_pharmakologie.md` | Prüfpunkte für Wirkstoff- und Antidotkarten |
| `checkliste_toxikologie.md` | Prüfpunkte für Toxidrom- und Antidotkarten |
| `checkliste_klinische_sicherheit.md` | Querschnittsprüfung Sicherheit und Didaktik |
| `review_protokoll_vorlage.md` | Protokoll je Karte bzw. je Prüfrunde |
| `../reports/cards_review_needed.md` | automatisch erzeugte Liste aller offenen Karten mit Prüfschwerpunkten (`make ph-review-report`) |
| `dist/review/Pharma_Cards_Review.pdf` | Review-Paket: eine A4-Seite je offener Karte (Vorder-/Rückseite mit ENTWURF-Wasserzeichen, Prüfschwerpunkte, Ergebnisfeld, Quelle, Anmerkungen), Inhaltsverzeichnis nach Prüfrolle (`make ph-review-packet`, nicht versioniert) |
