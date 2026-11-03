# 04 — Kuratierte Startliste

**Dokument:** Priorisierte, kuratierte erste Kartenversion mit Release-Wellen
**Handover-Phase:** 4

---

## 1. Kuratierungsprinzip

Der Handover listet ~200 mögliche Themen (Blöcke A–L). Diese werden **nicht alle sofort** produziert.
Stattdessen eine kuratierte, didaktisch tragfähige **Pilot- und Aufbaustruktur** in Release-Wellen.
Leitlinien:

- **Didaktisch hochwertig statt ausufernd.** Lieber 60 exzellente Karten als 242 mittelmäßige.
- **Hoher klinischer Hebel zuerst:** Grundprinzipien, Notfallmedikamente, Antidote, Kerntoxidrome.
- **Sicherheit vor Vollständigkeit:** kritische Karten (Antidote, Katecholamine) nur mit Review-Zwang.
- **Dubletten vermeiden:** Wirkstoffe, die in mehreren Blöcken vorkommen (z. B. Fentanyl in C/D/E),
  werden **einmal** als Wirkstoffkarte angelegt und über Kategorien/Tags mehrfach zugeordnet.

Release-Wellen (Spalte `release` in `categories.yaml`):

| Welle | Fokus | Kartenzahl (Richtwert) |
|---|---|---:|
| **R1 — Pilot** | Grundlagen, PK/PD-Kernbegriffe, Notfallmedikamente-Kern, Kerntoxidrome, Top-Antidote | ~60 |
| **R2 — Aufbau** | Anästhesie/Intensiv, Analgetika, Herz-Kreislauf, Interaktionen, Arzneimittelsicherheit | ~80 |
| **R3 — Breite** | Antibiotika, Psychopharmaka/Neurologie, Endokrinologie, Präklinik, Drogen/Intox | ~70 |
| **R4 — Spezial** | Onkologie, Pädiatrie, Geriatrie, Schwangerschaft, Niere/Leber, CBRN | später |

Gesamt R1–R3 ≈ 210 Karten → passt in den PH-Zielraum (242), R4 füllt auf/erweitert über 242 hinaus
(ID-Raum reicht bis `ph_999`).

---

## 2. Release 1 — Pilot (kuratiert, ~60 Karten)

### 2.1 Allgemeine Pharmakologie (Block A) — Prinzipkarten (`overview`/`principle`)

ID-Block `ph_001`–`ph_017` (Anker `ph_001`–`ph_005` bereits reserviert):

Agonist · Antagonist · Partialagonist · inverser Agonist · kompetitive Hemmung · nichtkompetitive
Hemmung · therapeutische Breite · Bioverfügbarkeit · First-Pass-Effekt · Verteilungsvolumen ·
Halbwertszeit · Clearance · Steady State · Loading/Erhaltungsdosis · Rezeptor-Down-/Upregulation.

→ `warning_level: low`, `review_status: needs_review`, keine konkreten Dosen.

### 2.2 Pharmakokinetik / Pharmakodynamik (Block B) — `ph_020`–`ph_030`

LADME-Prinzip · CYP450-System · CYP3A4 · CYP2D6 · CYP2C9 · P-Glykoprotein · renale Elimination ·
hepatische Metabolisierung · Proteinbindung · aktive Metaboliten · Prodrugs.

→ `warning_level: low–moderate`, `review_status: needs_review`.

### 2.3 Notfallmedikamente-Kern (Block C, Auswahl) — Wirkstoffkarten (`substance`) — `ph_040`–`ph_060`

Adrenalin · Noradrenalin · Atropin · Amiodaron · Adenosin · Nitroglycerin · Furosemid · Midazolam ·
Ketamin · Naloxon · Flumazenil · Glucose · Glucagon · Calcium · Magnesium · Natriumbicarbonat.

→ `warning_level: high`, viele `critical` (Katecholamine). `review_status: clinical_review_needed`.
Dosierungen **nur als Prinzip**, konkrete Zahlen nur mit Quelle + Review.

### 2.4 Kerntoxidrome (Block J, Auswahl) — Toxidromkarten (`toxidrome`) — `ph_080`–`ph_086`

Cholinerges · anticholinerges · sympathomimetisches · Opioid- · sedativ-hypnotisches · serotonerges ·
malignes neuroleptisches Syndrom.

→ `warning_level: high`, `review_status: toxicology_review_needed`.

### 2.5 Top-Antidote (Block K, Auswahl) — Antidotkarten (`antidote`) — `ph_100`–`ph_112`

Naloxon · Flumazenil · N-Acetylcystein · Atropin · Hydroxocobalamin · Sauerstoff · Fomepizol ·
Digoxin-Fab · Glucagon · Calcium · Natriumbicarbonat · Lipidemulsion · Vitamin K.

→ `warning_level: critical`, `review_status: toxicology_review_needed`, Export erst nach `approved`.

---

## 3. Release 2 — Aufbau (~80 Karten, Blöcke D, E, G, L)

- **Anästhesie/Intensiv (D):** Propofol, Etomidat, Sevofluran, Fentanyl/Sufentanil/Remifentanil,
  Rocuronium/Succinylcholin/Cisatracurium, Sugammadex, Neostigmin, Dexmedetomidin, Noradrenalin*,
  Dobutamin, Levosimendan. (*bereits in R1 als Wirkstoffkarte, nur Kategorie-Zuordnung ergänzen.)
- **Analgetika (E):** Paracetamol, Ibuprofen, Diclofenac, Metamizol, ASS, Morphin, Oxycodon, Tramadol,
  Buprenorphin (+ Naloxon-Querverweis).
- **Herz-Kreislauf (G):** Betablocker, ACE-Hemmer, AT1-Blocker, Calciumkanalblocker, Diuretika,
  Nitrate, Digoxin, Heparin/NMH, DOAK, Phenprocoumon, ASS, Clopidogrel, Ticagrelor + Intoxikationskarten
  (Betablocker-, Calciumkanalblocker-, Digitalisintoxikation).
- **Arzneimittelsicherheit/Interaktionen (L):** QT-Verlängerung, CYP-Induktion/-Inhibition, serotonerge
  Interaktionen, Blutungsrisiko, nephro-/hepatotoxische Kombinationen, Hyperkaliämie-/Hyponatriämie-Risiko,
  maligne Hyperthermie, Anaphylaxie.

→ Mischung Wirkstoff-/Interaktions-/Fallkarten; `warning_level` je Stoff; Review je nach Aussage.

---

## 4. Release 3 — Breite (~70 Karten, Blöcke F, H, I + Rest J)

- **Antibiotika/Antiinfektiva (F):** Penicilline, Pip/Tazo, Cephalosporine (Ceftriaxon, Cefuroxim),
  Carbapeneme (Meropenem), Makrolide (Azithromycin), Fluorchinolone (Cipro-/Levofloxacin), Vancomycin,
  Linezolid, Daptomycin, Aminoglykoside (Gentamicin), Cotrimoxazol, Metronidazol, Aciclovir, Oseltamivir,
  Fluconazol, Amphotericin B.
- **Endokrinologie/Stoffwechsel (H):** Insulin, Glucagon*, Metformin, Sulfonylharnstoffe, GLP-1-RA,
  SGLT2-Hemmer, Levothyroxin, Thiamazol, Glucocorticoide (Hydrocortison, Dexamethason).
- **Psychopharmaka/Neurologie (I):** Benzodiazepine, SSRI, SNRI, TZA, Neuroleptika (Haloperidol,
  Quetiapin), Lithium, Valproat, Levetiracetam, Carbamazepin, Phenytoin + Syndromkarten
  (Propofol-Infusionssyndrom, Serotoninsyndrom, MNS).
- **Rest-Toxikologie (J):** Salicylat-, Paracetamol-, CO-, Methanol-, Ethylenglykol-, Organophosphat-,
  LAST-Intoxikation.

---

## 5. Release 4 — Spezial (später, über 242 hinaus zulässig)

Onkologische Pharmakologie, Pädiatrie, Geriatrie, Schwangerschaft/Stillzeit, Niere-/Leberinsuffizienz,
CBRN/Gefahrstoffe. Diese Blöcke sind klinisch sensibel und erfordern umfangreiches Fachreview →
bewusst nach hinten priorisiert.

---

## 6. ID-Vergabeplan (Blockreservierung innerhalb PH)

| ID-Block | Kategorie | Welle |
|---|---|---|
| `ph_001`–`ph_019` | Allgemeine Pharmakologie | R1 |
| `ph_020`–`ph_039` | PK/PD | R1 |
| `ph_040`–`ph_079` | Notfall-/Intensiv-/Anästhesie-Medikamente | R1/R2 |
| `ph_080`–`ph_099` | Toxidrome | R1/R3 |
| `ph_100`–`ph_129` | Antidote | R1/R2 |
| `ph_130`–`ph_169` | Herz-Kreislauf, Analgetika | R2 |
| `ph_170`–`ph_209` | Antibiotika, Endokrinologie, Psychopharmaka | R3 |
| `ph_210`–`ph_249` | Interaktionen/Sicherheit, Intoxikationen | R2/R3 |
| `ph_250`+ | Spezialgebiete | R4 |

---

## 7. In spätere Releases verschoben (mit Begründung)

| Thema | Grund |
|---|---|
| Onkologische Pharmakologie | Hohe fachliche Varianz, Protokoll-/Dosisabhängigkeit → intensives Review |
| Pädiatrische Dosierungen | Gewichtsadaptierte Dosen = `critical`, Fehlerrisiko → nur mit Fachfreigabe |
| CBRN/Gefahrstoffe | Spezialwissen, geringere Breitenrelevanz für Erstrelease |
| Schwangerschaft/Stillzeit | Hohe Haftungssensibilität, leitlinienabhängig |
| Vollständige Handelsnamenlisten | Nur illustrativ, pflegeintensiv → optional, nicht primär |

> Diese Priorisierung ist ein Vorschlag zur Freigabe durch Andreas / das Fachreview-Team. Die
> maschinenlesbare Umsetzung erfolgt über `release`-Felder in `categories.yaml` und die Registry.
