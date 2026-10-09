# 09 — Eigenes Online-Lernkartensystem (Funktionskonzept)

Das Online-System ist **kein Bildergalerie-Viewer**, sondern eine datengetriebene Lernplattform.
Es nutzt die Kartendaten (Kap. 02) strukturiert; Bilder sind Darstellungs-/Exportartefakte.
Bestehende Notizen: `online-platform/user-features/*`, `online-platform/frontend/*`.

## 1. Lernende — Kernfunktionen

### Auswahl & Navigation
- Karten nach **Kategorie/Modul** auswählen, nach **Tags filtern**, **Volltextsuche**.
- **Lernmodus** starten; Karte **umdrehen** per Klick/Tap/Swipe/Leertaste.
- **Tastatursteuerung** und **Touch-/Swipe-Gesten**; **Vollbild-** und **Präsentationsmodus**.

### Markierung & Status
Pro Karte setzbar: **neu · gelernt · unsicher · noch einmal wiederholen · beherrscht ·
später wiederholen**. Diese Status speisen die Wiederholungslogik.

### Spaced Repetition (SRS)
- **Algorithmus: SM-2** (ease factor, interval, repetitions) **mit Leitner-Box-Overlay** als
  erklärbare, sichtbare Darstellung (Box 1–5).
- Begründung: SM-2 ist bewährt und gibt feinkörnige Intervalle; die Leitner-Box macht den
  Zustand für Lernende **sichtbar/verständlich**. Beides teilt sich dieselben Felder in
  `user_progress` (Kap. 11).
- Abgeleitete Stapel: **„Heute fällige Karten“**, **„Neue Karten lernen“**,
  **„Nur falsche/unsichere Karten“**, **Wiederholungsstapel**.

### Lernsteuerung & Statistik
- **Tagesziel / Lernsession**, **Favoriten**, **schwierige Karten separat üben**.
- **Lernhistorie pro Karte**, **Fortschritt pro Kategorie**, **Statistik-Dashboard**
  (Serie/Streak, Fälligkeiten, Beherrschungsgrad).

## 2. Modi

- **Lernmodus** (Flip + Status), **Wiederholungsmodus** (SRS-gesteuert), **Zufallsmodus**,
  **Prüfungsmodus**, **Fokusmodus** (ohne Ablenkung), optional **Timer**.
- **Quizmodus**: Freitextantwort · Multiple Choice (optional) · Struktur erkennen ·
  Name nennen · Kategorie zuordnen.

## 3. Notizen

- **Notizenfeld unter jeder Karte** (einklappbar), private Nutzer-Notizen.
- Optional **Dozenten-/Kursnotizen** (Sichtbarkeit `private | course | shared`).
- Rich-Text-light / Markdown, **Autospeicherung**, Zeitstempel, editier-/löschbar, **pro Nutzer**.
- Optional **Export der eigenen Notizen** als PDF/Markdown.

## 4. Annotationen auf Karten

- Zunächst als **Overlay** implementiert, **nicht destruktiv** ins Originalbild.
- Werkzeuge: Textnotiz · Pfeil · Markierung · Kreis/Rechteck · freie Hervorhebung.
- Speicherung als **JSON-Koordinaten** (`user_notes.annotation_data`, Kap. 11).
- Export kann Annotationen **optional einrendern** (über denselben Playwright-Export, Kap. 10).

## 5. Download / Export (für Lernende)

- Angezeigte Karte als **PNG** oder **PDF**; **Vorderseite** / **Rückseite** einzeln;
  **Vorder+Rückseite zusammen** als PDF.
- **Ausgewählte Karten** als Druckpaket; **ganze Kategorie** als PDF; **persönliches Lernset**
  exportieren. Alle Downloads laufen über den serverseitigen Export-Service (Kap. 10), damit das
  Ergebnis identisch zum Print-Layout ist.

## 6. Administration

- Karten **erstellen/bearbeiten/deaktivieren/versionieren**; **Layout-Vorschau**;
  **Export neu generieren**.
- **Kategorien & Tags verwalten**; **Review-Status setzen**; **fachliche Prüfung markieren**.
- **Import** aus CSV/YAML/JSON; **Änderungsverlauf pro Karte** (`card_versions`).

## 7. Rollenmodell

| Rolle | Rechte |
|-------|--------|
| **Admin** | Vollzugriff, Nutzer-/Rollenverwaltung, Deployment-nahe Aktionen |
| **Editor** | Karten/Kategorien/Tags erstellen & bearbeiten |
| **Fachreviewer** | Review-Status setzen, fachliche Freigabe, Kommentare |
| **Dozent** | Sets/Kurse kuratieren, Kursnotizen, Fortschritt der Lerngruppe (via LTI) |
| **Lernender** | Lernen, eigener Fortschritt, eigene Notizen/Annotationen, Downloads |

## 8. Fachreview-Workflow (Status-Automat)

```
draft → needs_review → reviewed → approved → (deprecated) → (archived)
```
Jede inhaltliche Änderung wird **versioniert** (`card_versions`). Nur `approved`-Karten sind für
Lernende/Print/Moodle „live“; `draft/needs_review` nur für Editor/Reviewer sichtbar. Details &
QS-Kriterien in [14 — Qualitätssicherung](14-quality-assurance.md).

## 9. Abgrenzung zum Bestand

Die vorhandenen `online-platform/user-features/`-Dokumente (learning-status, spaced-repetition,
user-notes, custom-card-sets, user-media-uploads, storage-quotas) beschreiben Teilaspekte; dieses
Kapitel ist die **konsolidierte, verbindliche** Funktionsreferenz, auf die sie künftig verweisen.
