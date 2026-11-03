# 07 — Druckfertige Dateien & Print-Export

Aufbauend auf `print-production/` (Specs, Packaging) und `scripts/export_print_batch.py`.

## 1. Ausgabeformen

### 1.1 Einzelkarten-PDFs
- Jede Karte einzeln als `generated/individual/pdf/<card_id>.pdf`.
- Vorder- und Rückseite **paarweise** (2 Seiten), mit Beschnitt, CMYK-tauglich vorbereitet.

### 1.2 A4-Druckbögen (`generate_print_pdfs.py`)
- Mehrere Karten pro Bogen; Vorder- und Rückseiten korrekt für **Duplexdruck** angeordnet
  (schnitt- und spiegelpassend — Rückseiten so gespiegelt/positioniert, dass sie nach dem
  Wenden deckungsgleich auf den Vorderseiten liegen).
- **Schneidemarken**, ausreichende Ränder, optional Beschnittzugabe.

### 1.3 A3-Druckbögen (optional)
- Gleiche Logik, höhere Nutzenzahl pro Bogen für Auflagendruck.

### 1.4 Varianten (je Kategorie/Paket)
- mit Schnittmarken / ohne Schnittmarken
- 2 Karten pro Seite / 4 pro Seite / 8 pro Seite (letzteres nur, wenn lesbar — Lesbarkeits-Gate)

## 2. Montagelogik (Duplex)

```
A4 quer, 4 Karten (2×2):     Vorderseiten-Bogen        Rückseiten-Bogen (horizontal gespiegelt)
                              ┌────┬────┐               ┌────┬────┐
                              │ C1 │ C2 │               │ C2 │ C1 │
                              ├────┼────┤   ⟶ wenden ⟶  ├────┼────┤
                              │ C3 │ C4 │               │ C4 │ C3 │
                              └────┴────┘               └────┴────┘
```
Die Spiegelachse (lange/kurze Kante) ist konfigurierbar und in `print-production/specs`
dokumentiert; Standard ist Wenden über die lange Kante.

## 3. Druckpakete (`dist/print/`)

Pro Fachbereich/Modul ein ZIP, plus Gesamtset:

```
dist/print/
  ChemBioMed_Cards_Print_Allgemeine_Chemie.zip     (AC → allgemein/anorganik)
  ChemBioMed_Cards_Print_Anorganische_Chemie.zip
  ChemBioMed_Cards_Print_Organische_Chemie.zip      (OC)
  ChemBioMed_Cards_Print_Molekularbiologie.zip      (MB)
  ChemBioMed_Cards_Print_Biochemie.zip              (BC)
  ChemBioMed_Cards_Print_Gesamtset.zip
```

**Inhalt je Paket:**
- druckfertige Bogen-PDF (gewählte Variante[n]),
- Einzelkarten-PDFs,
- PNGs (Vorder-/Rückseite),
- `README_PRINT.md` (Druckhinweise: Papier, Grammatur, Duplex-Einstellung, Beschnitt,
  Farbprofil, empfohlene Dienstleister-Settings).

## 4. Druckvorstufe / Qualität

- **Farbraum:** Layout in sRGB; für professionellen Druck CMYK-Konvertierung mit dokumentiertem
  ICC-Profil (im `README_PRINT.md`). Entscheidung je Druckdienstleister final abstimmen
  ([offene Fragen](open-questions.md)).
- **Mindestabstände/Beschnitt** laut `print-production/specs` und Kap. 05 §1.
- **Prüfbogen-PDF** (Imposition-Vorschau) als Teil des Validierungslaufs.

## 5. Reproduzierbarkeit

Alle Druckartefakte entstehen aus `cards_master.json` + Templates (Kap. 06). Ein Paket ist
jederzeit aus einem Git-Stand neu baubar; Paketinhalte werden über `package-registry.yaml`
(bestehend) gesteuert, damit Zusammenstellung und Reihenfolge nachvollziehbar sind.
