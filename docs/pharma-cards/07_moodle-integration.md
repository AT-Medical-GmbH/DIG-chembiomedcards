# 07 — Moodle-Integration

**Dokument:** Moodle-Importpakete + Architekturentscheidung (Plugin vs. LTI vs. iframe vs. H5P)
**Handover-Phase:** 8

---

## 1. Zwei Integrationsstufen

Pharma Cards braucht Moodle auf zwei Ebenen, die unabhängig ausgeliefert werden:

- **Stufe A — Importpakete (sofort nutzbar):** statische Karteninhalte als Moodle-importierbare Dateien
  (Bilder + CSV/HTML). Funktioniert ohne das Online-System.
- **Stufe B — Live-Integration (mit Online-System):** die interaktive Lernkartenoberfläche in Moodle,
  mit Lernfortschritt. Baut auf dem Online-System (Dok. 08) auf.

---

## 2. Stufe A — Moodle-Importpakete

Generiert durch `generate_moodle_import.py`, je Kategorie ein Paket:

```
exports/moodle/ph/<kategorie>/
  images/                       # Front-/Back-PNGs
  import.csv                    # Grundfelder (Trennzeichen Komma)
  import_html.csv               # HTML-Variante (Front/Back als HTML-Blöcke)
  manifest.json                 # Paketbeschreibung, Kartenliste, Versionen
  DIRECT_IMPORT_TAB_CRLF.txt    # Tab-separiert, CRLF (robuste Variante)
  DIRECT_IMPORT_SEMICOLON_CRLF.txt  # Semikolon-separiert, CRLF (DE-Excel-freundlich)
  README_IMPORT.md              # Importanleitung + Annahmen
```

**Importfelder** (je Zeile = eine Karte):
`title, category, card_id, front_image, back_image, front_html, back_html, tags, difficulty,
primary_category, secondary_categories, warning_level, review_status`.

**Kategorienpakete:** Allgemeine Pharmakologie · PK/PD · Notfallmedikamente · Anästhesie/Intensiv ·
Analgetika · Antibiotika/Antiinfektiva · Herz-Kreislauf · Endokrinologie/Stoffwechsel ·
Psychopharmaka/Neurologie · Toxikologie · Antidote · Arzneimittelsicherheit/Interaktionen · Gesamtset.

**Robustheit:** Da das konkrete Moodle-Flashcard-Plugin ein spezifisches Format erwarten kann, werden
**mehrere Varianten** erzeugt (CSV Komma/Semikolon, Tab, HTML) und die Annahmen in `README_IMPORT.md`
dokumentiert. Nur Karten, die das Export-Gate erfüllen (Dok. 10), werden aufgenommen.

---

**Umsetzungsstand (2026-10-31):** Stufe A ist implementiert (`scripts/pharma/generate_moodle_import.py`,
`make ph-moodle` / `make ph-moodle-preview`). Die Paketzuschnitte kommen aus
`cards/PH/scope/packages.yaml`. ZIPs sind byte-reproduzierbar (feste Zeitstempel). Getestet sind
CRLF, BOM und Spaltenstruktur.

## 3. Stufe B — Architekturentscheidung Live-Integration

### 3.1 Optionen und Bewertung

| Option | Aufwand | Nutzerfortschritt | SSO | Wartung | Bewertung |
|---|---|---|---|---|---|
| 1. Moodle-Plugin (Aktivität) | hoch | ja (Moodle-nativ) | Moodle-nativ | PHP-Plugin, Moodle-Versionspflege | mächtig, aber teuer & versionsgebunden |
| 2. **LTI 1.3 External Tool** | **mittel** | **ja (AGS/NRPS)** | **OIDC-basiert** | entkoppelt vom Moodle-Core | **empfohlen** |
| 3. iframe/Webcomponent | gering | nur via eigene Auth | separat | gering | schneller Einstieg, schwache Kopplung |
| 4. H5P/SCORM-Export | mittel | eingeschränkt (SCORM-Tracking) | n/a | Content-Export statisch | gut für Offline/Paketkurse, kein Live-Edit |
| 5. Moodle-Block | gering | nein | n/a | gering | nur Verweis/Navigation |

### 3.2 Entscheidung

**Primär: LTI 1.3 External Tool** — begründet:

- Pharma Cards ist ohnehin eine eigenständige Web-App mit eigener API (Dok. 01/08); LTI 1.3 bettet sie
  sauber als „External Tool“ ein, ohne Moodle-Core-Eingriffe oder Versionskopplung.
- **OIDC-basierter Launch** passt exakt zum SSO-/Authentik-Zielbild (Dok. 01/09).
- **Assignment & Grade Services (AGS)** und **Names & Role Provisioning (NRPS)** erlauben Fortschritt/
  Bewertung und Rollen (Dozent/Lernende) zurück an Moodle, ohne Daten doppelt zu halten.
- Mehrere Moodle-Instanzen/Kurse können dieselbe Tool-Instanz nutzen (`moodle_contexts`-Tabelle).

**Übergang/Fallback: iframe/Webcomponent** für einen schnellen ersten Rollout, bevor LTI steht; und
**H5P/SCORM-Export** als Zusatzkanal für Kurse, die gekapselte, offline-fähige Pakete brauchen.

**Nicht primär:** ein vollständiges PHP-Moodle-Plugin (Option 1) — zu hoher Wartungsaufwand gegenüber
LTI, ohne Mehrwert für diesen Funktionsumfang.

### 3.3 Umsetzungsschritte (Folgephase)

1. LTI-1.3-Endpoints in `pharma-api` (OIDC-Login-Initiation, Launch, JWKS, Deep Linking).
2. Tool-Registrierung in Moodle (Client-ID, Deployment-ID, Keys).
3. Deep Linking: Dozent wählt Kategorie/Lernset → eingebettete Aktivität.
4. AGS-Rückmeldung von Lernfortschritt/Quizergebnis (optional, datensparsam).
5. `lms_url`-Felder der Karten weiterhin für einfache URL-Aktivitäten (Stufe-A-kompatibel).

Die Entscheidung und ihre Konsequenzen werden zusätzlich als ADR in
`online-platform/architecture/lms-integration.md` (bestehend) fortgeschrieben und in
`lms-content/moodle-integration.md` operativ konkretisiert.
