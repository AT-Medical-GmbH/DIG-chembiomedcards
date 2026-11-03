# 08 — Online-Lernkartensystem

**Dokument:** Funktionen, Spaced Repetition, Notizen/Annotationen, Downloads, Rollen, UI/UX
**Handover-Phasen:** 9 (Funktionen/Admin/Review), 12 (UI/UX)

---

## 1. Zielbild

Ein modernes, interaktives Lernkartensystem, optisch zur AT-Medical-Webseite passend — **kein**
Lernspielzeug, sondern ein professionelles CME-/Medizin-Lernsystem. Es arbeitet auf den strukturierten
Kartendaten (Dok. 02), nicht auf einer Bildergalerie.

---

## 2. Funktionen für Lernende

### 2.1 Navigation & Auswahl
- Karten nach Kategorie, Wirkstoffgruppe und Tags filtern.
- Volltextsuche über Wirkstoff, Klasse, Indikation, Nebenwirkung, Antidot, Toxidrom.
- Kuratierte Sets: „Notfallmedikamente“, „Antidote“, „Toxidrome“, „Heute fällige Karten“,
  „Nur falsche/unsichere“, „Neue Karten“.

### 2.2 Lernmodus
- Karte umdrehen per Klick/Tap/Swipe/Leertaste; Vollbild; Präsentationsmodus; Fokusmodus.
- Tastatursteuerung (← → zum Blättern, Leertaste Flip, 1–5 Bewertung) und Touch-/Swipe-Gesten.
- Fortschrittsbalken, optionaler Timer.
- Sichtbares Warnlevel-Badge bei `high`/`critical`.

### 2.3 Markierungssystem (Status je Karte/Nutzer)
`neu · gelernt · unsicher · noch einmal wiederholen · beherrscht · später wiederholen ·
klinisch wichtig · prüfungsrelevant` → Feld `user_progress.status`.

### 2.4 Spaced Repetition
- **Zwei wählbare Verfahren:** Leitner-Box (5 Fächer) und **SM-2** (ease_factor/interval/repetitions).
- Felder in `user_progress`: `leitner_box, ease_factor, interval_days, repetitions, next_due_at,
  last_reviewed_at`.
- Tagesziel/Lernsession, Wiederholungsstapel, Favoriten, „schwierige Karten separat üben“,
  Lernhistorie pro Karte, Fortschritt pro Kategorie, Statistik-Dashboard.

### 2.5 Quiz-/Prüfungsmodi
Wirkstoff erkennen · Wirkmechanismus nennen · Antidot nennen · Nebenwirkung zuordnen · Toxidrom
erkennen · Interaktion bewerten · Fallvignette lösen · Multiple Choice (optional) · Freitext (optional).
Zufalls-, Prüfungs- und Wiederholungsmodus.

---

## 3. Notizen & Annotationen

### 3.1 Notizen (`user_notes`)
- Notizfeld **unterhalb** jeder Karte, einklappbar.
- Rich-Text-light/Markdown, Autospeicherung, Zeitstempel.
- Sichtbarkeit `private | course | public` (Dozenten-/Kursnotizen möglich).
- Export der eigenen Notizen als PDF/Markdown.

### 3.2 Annotationen auf Karten (`annotation_data` JSONB)
- Overlay-Prinzip: Text, Pfeil, Markierung, Kreis/Rechteck, freie Hervorhebung.
- **Nicht destruktiv** — Annotationen werden als JSON-Koordinaten gespeichert, nie ins Originalbild
  geschrieben. Export kann Annotationen optional einrendern.
- Pro Nutzer gespeichert; editierbar/löschbar.

---

## 4. Download-Funktionen
- Angezeigte Karte als PNG oder PDF (Front, Back, oder Front+Back gemeinsam).
- Ausgewählte Karten als Druckpaket; ganze Kategorie als PDF; persönliches Lernset exportieren.
- Serverseitig über dieselbe Playwright-Pipeline (Dok. 06); Export-Gating gilt (Dok. 10).
- Exporte werden in `exports`-Tabelle protokolliert.

---

## 5. Administrations- & Redaktionsfunktionen
- Karten erstellen/bearbeiten/deaktivieren/versionieren.
- Kategorien, Tags, Wirkstoffgruppen verwalten (schreibt zurück in bzw. synchron mit `scope/*.yaml`).
- Warnlevel und Review-Status setzen; fachliche/klinische Prüfung markieren.
- Layout-Vorschau, Export neu generieren, Import aus CSV/YAML/JSON (Dok. 11).
- Änderungsverlauf pro Karte (`card_versions`, Pflicht für klinisch relevante Karten).

### 5.1 Rollenmodell (`users.role`)
`admin · editor · reviewer_pharm (Fachreviewer Pharmakologie) · reviewer_tox (Fachreviewer
Toxikologie) · teacher (Dozent) · learner (Lernender)`.

### 5.2 Fachreview-Workflow (verbindlich)
`draft → needs_review → clinical_review_needed / toxicology_review_needed → reviewed → approved`
(+ `deprecated`, `archived`). Jede inhaltliche Änderung wird versioniert (`card_versions`), jede
Reviewentscheidung in `review_events` protokolliert. Details in Dok. 10.

---

## 6. UI/UX — Ansichten

Designprinzipien: ruhige helle Oberfläche, hochwertige Kartenanimationen, responsiv (Tablet-first),
touch-freundlich, schnelle Ladezeiten, barrierearm (WCAG-AA), große lesbare Schrift, gute Kontraste,
dezente Animationen, professionelle Medizin-Optik.

**Hauptansichten:** Dashboard · Kategorienübersicht · Wirkstoffgruppenübersicht · Kartenset-Übersicht ·
Lernmodus · Wiederholungsmodus · Karteneditor · Notizenansicht · Fortschrittsstatistik · Exportcenter ·
Admin-/Review-Bereich · Toxikologie-/Antidot-Schnellübersicht.

**Lernkartenansicht:** Karte mittig, Tabs oben, Front/Back-Flip; Buttons *Gelernt · Wiederholen ·
Unsicher · Beherrscht · Klinisch wichtig · Notiz · Download · Drucken*; Fortschrittsbalken;
Tastaturkürzel; Swipe; optional Timer/Fokusmodus; Warnlevel sichtbar.

---

## 7. API-Oberfläche (Auszug, REST/OpenAPI)

| Endpoint | Zweck |
|---|---|
| `GET /cards` (Filter: category, drug_class, tag, q) | Kartenliste/Suche |
| `GET /cards/{card_id}` | Einzelkarte (strukturierte Felder) |
| `GET/PUT /progress/{card_id}` | Lernstatus/SR-Update |
| `GET/POST/PUT/DELETE /notes` | Notizen + Annotationen |
| `GET /due`, `GET /sets/{name}` | fällige Karten, kuratierte Sets |
| `POST /export` | Download/PDF-Erzeugung |
| `POST /cards`, `PUT /cards/{id}` (Editor+) | Redaktion |
| `POST /reviews` (Reviewer+) | Reviewentscheidung |
| `GET /stats` | Fortschritt/Statistik |
| LTI 1.3: `/lti/login`, `/lti/launch`, `/lti/jwks`, `/lti/deeplink` | Moodle |

Zugriffskontrolle über Rolle + Lizenz-/Paket-Claims (JWT). Nur `approved`-Inhalte sind für Lernende
sichtbar, außer Review-Rollen in der Vorschau.
