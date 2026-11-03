# 03 — Fachliche Zielstruktur

**Dokument:** Fachbereiche, Kategorienmodell, Erweiterbarkeit
**Handover-Phasen:** 2 (Zielstruktur), 13 (Erweiterbarkeit)

---

## 1. Startumfang und Ausbaustrategie

Pharma Cards startet mit **Pharmakologie und Toxikologie** und ist so modelliert, dass weitere
medizinisch-pharmakologische Fachgebiete additiv ergänzt werden können — ohne Layout- oder App-Code zu
ändern. Die gesamte Fachstruktur lebt in `cards/PH/scope/` (siehe Dok. 02).

### 1.1 Aktuelle Hauptbereiche (15)

Gemäß Handover, abgebildet in `categories.yaml`:

1. Allgemeine Pharmakologie
2. Pharmakokinetik
3. Pharmakodynamik
4. Klinische Pharmakologie
5. Arzneimittelgruppen
6. Notfallmedikamente
7. Intensivmedizinische Pharmakologie
8. Anästhesiologische Pharmakologie
9. Toxikologie
10. Notfalltoxikologie
11. Antidote
12. Arzneimittelinteraktionen
13. Nebenwirkungen und Kontraindikationen
14. Arzneimittelsicherheit
15. Pharmakogenetik / individualisierte Pharmakotherapie

### 1.2 Perspektivische Erweiterungen

In `categories.yaml` als `future_categories` bereits angelegt (Release R2–R4): Antibiotika/Antiinfektiva,
Analgetika, Sedativa/Hypnotika, Katecholamine/Vasopressoren, Antiarrhythmika, Antihypertensiva,
Antikoagulanzien, Antiepileptika, Psychopharmaka, Endokrinologie, Diabetologie, Onkologische
Pharmakologie, Pädiatrie, Geriatrie, Schwangerschaft/Stillzeit, Nieren-/Leberinsuffizienz, Präklinische
Notfallmedizin, CBRN/Gefahrstoffe, Drogen/Alkohol/Intoxikationen.

---

## 2. Verhältnis Kategorie ↔ Wirkstoffgruppe ↔ Tag

Drei orthogonale Achsen, bewusst getrennt, damit eine Karte mehrdimensional auffindbar ist:

| Achse | Zweck | Beispiel (Karte „Naloxon“) |
|---|---|---|
| **Kategorie** (`primary_category`, `secondary_categories`) | fachliche Hauptzuordnung / Produktgliederung | `antidote`, sekundär `notfallmedikamente` |
| **Wirkstoffgruppe** (`drug_class`) | pharmakologische Klassifikation | `antidote` (bzw. `opioid`-Antagonist) |
| **Tag** (`tags`) | querschnittliche Filter | `notfall`, `antidot`, `antagonist`, `pruefungsrelevant` |

Die Online-Suche (Dok. 08) durchsucht alle drei Achsen plus Volltext (Wirkstoff, Indikation,
Nebenwirkung, Antidot, Toxidrom).

---

## 3. Erweiterbarkeit auf weitere Fachgebiete

Damit Pharma Cards später wachsen kann (Handover Phase 13), sind folgende Mechanismen verankert:

- **Generisches Kategorienmodell:** Kategorien hierarchisierbar (`parent`), aus Konfig, mit Farbe/Icon.
- **Generisches Tagging:** kontrolliertes Vokabular, additiv erweiterbar.
- **Flexible Kartentypen:** `card_types.yaml` definiert Typen + Default-Rückseitenstruktur.
- **Flexible Front-Typen:** von `substance`/`structure`/`mechanism` bis `ecg`/`lab`/`algorithm`
  (perspektivisch) — bereits als Enum vorbereitet.
- **Flexible Rückseiten-Typen:** Box-Bausteine mit Farbrolle, frei kombinierbar je Kartentyp.
- **Import aus YAML/JSON/CSV** (Dok. 11), **Export nach Moodle/PDF/PNG** (Dok. 06/07).
- **Review-Workflow & Rollenmodell** greifen für jedes neue Fachgebiet unverändert.

### 3.1 Muster für künftige Fachgebiete

| Fachgebiet | Typische Front | Typische Back-Boxen |
|---|---|---|
| Pharmakologie | Wirkstoff/Mechanismus | Mechanismus, Indikation, NW, KI |
| Toxikologie | Giftstoff/Toxidrom | Leitsymptome, Pathophysiologie, Antidot |
| Intensivmedizin | Medikament | Indikation, Monitoring, Cave |
| Notfallmedizin | Algorithmus/Dosierungsprinzip | Algorithmus, Prinzip, KI |
| Antibiotika | Wirkstoff/Gruppe | Spektrum, Resistenz, NW |
| Pädiatrie | Wirkstoff | altersabhängige Besonderheiten |
| Geriatrie | Wirkstoff/Situation | Polypharmazie, Delirrisiko |
| Pharmakogenetik | CYP-Variante | klinische Konsequenz |

---

## 4. ID- und Kapitelsystematik innerhalb PH

- **ID-Raum:** `ph_001`–`ph_999` (3-stellig), kompatibel zum bestehenden Schema. Zielumfang PH laut
  Masterverzeichnis: 242 Karten. Pharma Cards nutzt diesen Raum; die Vergabe erfolgt blockweise je
  Kategorie (siehe `04_startliste-kuratiert.md`).
- **Kapitel (`chapter`):** `pharmakologie/<kategorie-slug>` bzw. `toxikologie/<thema>`, passend zur
  bestehenden `chapter`-Logik (`module/thema`).
- **Reservierte Anker:** `ph_001`–`ph_005` bleiben wie im Masterverzeichnis vergeben (Allgemeine
  Pharmakologie, PK-Überblick, PD-Überblick, Rezeptorbindung, Dosis-Wirkungs-Kurve).

---

## 5. Abgrenzung zu anderen ChemBioMed-Modulen

- **Arzneistoffchemie** ist die Brücke zu OC/APC (Strukturformeln) — Querverweise via `related_cards`,
  keine Dopplung. Pharmakologische Mechanismen gehören zu PH, reine Strukturchemie zu OC.
- **Ernährung/Stoffwechselmedizin** überschneidet sich mit APC — Zuordnung über `primary_category`
  (PH, wenn der pharmakologische/toxikologische Aspekt führt).
