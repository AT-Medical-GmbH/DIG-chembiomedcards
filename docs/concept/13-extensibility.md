# 13 — Erweiterbarkeit auf weitere Fachgebiete

ChemBioMed Cards startet mit Chemie/Biochemie/Molekularbiologie, ist aber als **generisches
Lernkarten-System** ausgelegt. Erweiterung darf **keine** Code-/Layout-Änderung erzwingen.

## 1. Was Erweiterbarkeit konkret bedeutet

| Baustein | Mechanismus der Erweiterung |
|----------|------------------------------|
| **Kategorien/Tabs** | Eintrag in `data/categories.yaml` — kein Layout-Code (Kap. 03) |
| **Tags** | Eintrag in `data/tags.yaml` |
| **Kartentypen (Front)** | neuer `front_type` + Template-Block; `front_content` ist JSONB |
| **Rückseiten-Typen** | zusätzliche Sektions-Bausteine im Back-Template |
| **Fachgebiet/Modul** | neuer Modulcode + Paket in `package-registry.yaml` |
| **Import** | gleiche Pipeline (YAML/JSON/CSV) |
| **Export** | gleiche Moodle-/PDF-/PNG-Generatoren |
| **Review/Rollen** | identischer Workflow & Rollenmodell |

## 2. Front-Typen (erweiterbarer Katalog)

`structure` · `term` · `image` · `diagram` · `case` (Fallvignette) · `labvalue` (Laborwert) ·
`ecg` (EKG-Streifen) · `xray` (Röntgen) · `micro` (Mikroskopie) · `algorithm` · `calc`
(Rechenaufgabe).

## 3. Rückseiten-Typen (Sektions-Bausteine)

`explanation` · `diagnosis` · `differential` (Differentialdiagnose) · `consequence`
(klinische Konsequenz) · `therapy` · `mnemonic` · `references`.

Die festen Sektionen aus Kap. 05 sind der **Chemie/Biochemie-Standard**; weitere Fachgebiete
aktivieren zusätzliche Bausteine, ohne die Grundstruktur (Titel → Klassifikation → Relevanzen →
Merke) zu brechen.

## 4. Beispiel-Erweiterungen (Zielbild, nicht MVP)

- **Pharmakologie** (Modul PH): Wirkstoff · Mechanismus · Nebenwirkungen · Interaktionen.
- **Mikrobiologie**: Erreger · Gramverhalten · Therapie.
- **Immunologie**: Zelltyp · Marker · Funktion.
- **Intensivmedizin**: Beatmungsmodus · Indikation · Fallstrick.
- **Notfallmedizin**: Algorithmus · Medikamentendosis · Kontraindikationen.
- **Labormedizin**: Parameter · Referenzbereich · Interpretation.

Perspektivisch ebenso: Physiologie, Pathophysiologie, Genetik, Anästhesie, Hämatologie,
Infektiologie, Ernährungsmedizin, Medizintechnik, Anatomie, Histologie.

## 5. Leitplanke: kontrolliertes Wachstum

Erweiterung erfolgt **didaktisch begründet**, nicht beliebig. Neue Fachgebiete durchlaufen
denselben Review-Workflow (Kap. 14). Die Soll-Listen (Kap. 14 §2) verhindern „unendliche“
Ausdehnung der Stoffliste im Startbereich.

## 6. Mehr-Fachgebiet-Betrieb

Das Datenmodell trägt `module` + `primary_category`; das Online-System kann Fachgebiete als
getrennte Sammlungen / Lizenzpakete führen. Eine spätere **Mandanten-/Produktlinien-Trennung**
(z. B. eigenes Branding je Fachgebiet) ist über Design-Tokens + Kategorie-Konfiguration möglich,
ohne die Pipeline zu verzweigen.
