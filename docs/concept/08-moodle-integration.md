# 08 — Moodle-Integration

AT Medical betreibt Moodle (vgl. `ATMED-docs/moodle/theme/atmedical` — Boost-Child-Theme,
Authentik-/WooCommerce-/BigBlueButton-Integration). ChemBioMed Cards soll dort nutzbar sein.

## 1. Entscheidung

> **Strategisch: LTI 1.3 Tool** (ChemBioMed Cards als externes Lerntool).
> **Interim/ergänzend: Importpakete** (Bilder + CSV/GIFT/XML, optional H5P) und **iframe/
> Webcomponent**-Einbettung.

### Begründung (Optionen abgewogen)

| Option | Pro | Contra | Rolle |
|--------|-----|--------|------|
| **LTI 1.3** (Tool Provider) | SSO via Launch, Deep Linking, Noten-Rückgabe (AGS), **keine Plugin-Pflege** bei Moodle-Upgrades, nutzt dasselbe Online-System | Setup (Keys/Deployment-ID) nötig | **primär** |
| **Moodle-Plugin (Aktivität)** | tief integriert, Fortschritt in Moodle | Pflege/Review bei jedem Moodle-Release, PHP-Codebasis zusätzlich | später, nur falls nötig |
| **iframe / Webcomponent** | sofort, trivial | kein SSO/Grading out-of-the-box | **interim** / Einbettung einzelner Sets |
| **CSV/GIFT/XML-Import** | nutzt Moodle-Fragenpool/Karten-Plugins, offline-tauglich | statisch, kein Fortschritt im Online-System | **ergänzend** (Fragenpool, Quiz) |
| **H5P/SCORM-Export** | portabel, in vielen LMS | Autoren-Overhead, begrenzte Interaktivität | optional für Austausch |

LTI 1.3 vermeidet die Hauptlast (Plugin-Wartung über Moodle-Versionen) und bringt SSO + Grading
„umsonst“, weil das **eine** Online-System (Kap. 09/10) der Tool Provider ist.

## 2. LTI-1.3-Architektur

```
Moodle (Platform) ──Launch (OIDC)──▶ ChemBioMed Cards /lti/launch
   ▲  Deep Linking (Set/Kategorie wählen)        │ validiert JWT, mappt lti_user → user
   │  AGS (Scores zurück)  ◀───────────────────── │ zeigt Lernmodus im Moodle-Kontext
```

- **Login/Launch:** OIDC-basierter LTI-Launch; `lti_deployment_id`/`client_id` je Moodle-Instanz.
- **Deep Linking:** Dozent wählt beim Einbetten Kategorie/Set/Modus (z. B. „Biochemie –
  Aminosäuren – Lernmodus“).
- **AGS (Grading):** optionale Rückgabe von Lernfortschritt/Quiz-Ergebnis als Moodle-Note.
- **NRPS (Namensliste):** optional für Kurszuordnung.
- Kontextdaten (Kurs, Rolle) landen in `moodle_contexts` (Kap. 11, optional).

## 3. Importpakete (interim/ergänzend)

Pro Kategorie unter `generated/moodle/` bzw. `dist/moodle/`:

```
generated/moodle/<kategorie>/
  images/                       # Vorder-/Rückseiten-PNGs
  import.csv                    # Grundfelder
  import_html.csv               # HTML-Varianten (formatierte Vorder-/Rückseite)
  manifest.json
  DIRECT_IMPORT_TAB_CRLF.txt    # Tab-getrennt, CRLF (robuste Direktimport-Variante)
  DIRECT_IMPORT_SEMICOLON_CRLF.txt
  README_IMPORT.md              # Schritt-für-Schritt je Zielplugin + Annahmen
```

**Importfelder:** `title, category, card_id, front_image, back_image, front_html, back_html,
tags, difficulty, primary_category, secondary_categories`.

**Kategorien:** Allgemeine Chemie · Anorganische Chemie · Organische Chemie · Molekularbiologie ·
Biochemie · Gesamtset.

**Robustheit:** Da das konkrete Moodle-Flashcard-Plugin ein spezifisches Format erwarten kann,
werden **mehrere Varianten** erzeugt (CSV, Tab/CRLF, Semikolon/CRLF, HTML-Felder) und die
**Annahmen** je Variante in `README_IMPORT.md` dokumentiert. Zusätzlich kann ein
GIFT-/Moodle-XML-Export für den Fragenpool erzeugt werden (Name↔Struktur als Frage-Antwort).

## 4. Distribution (`dist/moodle/`)

```
ChemBioMed_Cards_Moodle_Allgemeine_Chemie.zip
ChemBioMed_Cards_Moodle_Anorganische_Chemie.zip
ChemBioMed_Cards_Moodle_Organische_Chemie.zip
ChemBioMed_Cards_Moodle_Molekularbiologie.zip
ChemBioMed_Cards_Moodle_Biochemie.zip
ChemBioMed_Cards_Moodle_Gesamtset.zip
```

## 5. Abstimmung mit dem ATMED-Moodle

- Theme/Design: Karten-Einbettung soll zum `theme_atmedical` passen (dunkel-glasig vs. helle
  Kartenfläche — Kontrast beachten).
- SSO: LTI-Launch nutzt dieselbe Identität wie Authentik-SSO (Kap. 15), damit Lernende nicht
  doppelt anmelden.
- Rollen-Mapping Moodle→ChemBioMed: `instructor`→Dozent, `learner`→Lernender (Kap. 09 §Rollen).

→ Konkrete Moodle-Version, aktives Flashcard-/H5P-Plugin und AGS-Nutzung sind in
[offenen Fragen](open-questions.md) zur Klärung mit dem Moodle-Betrieb vermerkt.
