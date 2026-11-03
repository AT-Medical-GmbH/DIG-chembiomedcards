# 12 — Akzeptanzkriterien & Roadmap

**Dokument:** Abnahmekriterien (20 Punkte), Umsetzungs-Roadmap, offene Punkte/Backlog
**Handover-Phase:** 18

---

## 1. Akzeptanzkriterien — Status

Legende: ✅ erfüllt (Konzeptphase) · 🟡 spezifiziert, Umsetzung in Folgephase · ⬜ offen

| # | Kriterium | Status | Nachweis |
|---|---|---|---|
| 1 | Projektstruktur vollständig angelegt | ✅ | Dossier + `cards/PH/scope/` + Mapping (README §4) |
| 2 | Datenmodell Pharmakologie **und** Toxikologie steht | ✅ | `02_datenmodell.md`, Scope-Konfig |
| 3 | Startliste kuratiert & priorisiert | ✅ | `04_startliste-kuratiert.md` |
| 4 | Einheitliches Layout für alle Karten | 🟡 | `05_kartenlayout.md` (Templates folgen) |
| 5 | Tabs oben konsistent | 🟡 | `05` §2 (fixes Tab-Set, aus `card_types.yaml`) |
| 6 | Vorder-/Rückseiten korrekt erzeugt | 🟡 | `06_generierung-und-print.md` (Pipeline spezifiziert) |
| 7 | Alle Karten geprüft oder mit Review-Status | ✅ | Review-Statusmodell + Example-Karten `needs_review` |
| 8 | Klinisch kritische Karten gesondert markiert | ✅ | `warning_levels.yaml`, `antidotes.yaml` (critical) |
| 9 | Moodle-Importpakete | 🟡 | `07_moodle-integration.md` §2 (Generator spezifiziert) |
| 10 | Druckfertige PDFs | 🟡 | `06` §2 (Print-Spec vorhanden) |
| 11 | Einzelkarten als PNG & PDF | 🟡 | `06` §1.2 |
| 12 | Online-Lernsystem implementiert | 🟡 | `08_online-lernsystem.md` + `01`/`02` (Architektur/DB) |
| 13 | Online lernen/markieren/wiederholen | 🟡 | `08` §2 (SR, Markierungen) |
| 14 | Notizen unter Karten | 🟡 | `08` §3.1, Tabelle `user_notes` |
| 15 | Annotationen technisch vorbereitet | ✅ | `08` §3.2 + `annotation_data` JSONB (Overlay-Prinzip) |
| 16 | Einzelne Karten online als PNG/PDF | 🟡 | `08` §4 |
| 17 | Kategorien/Tags/Gruppen/Review bearbeitbar | ✅/🟡 | Konfig editierbar (✅); Admin-UI (🟡) `08` §5 |
| 18 | Erweiterbar auf weitere Fachgebiete | ✅ | `03_fachliche-zielstruktur.md` §3, Konfig-getrieben |
| 19 | Deployment-Dokumentation | ✅ | `09_deployment.md` |
| 20 | Abschlussbericht | 🟡 | dieses Dokument (Konzept); Release-Report bei Produktion |

**Fazit:** Die **Konzept-/Setup-Ebene** aller 20 Kriterien ist erbracht; die mit 🟡 markierten Punkte
sind vollständig spezifiziert und in den Folgephasen (Code/Content) umzusetzen.

---

## 2. Umsetzungs-Roadmap (nach Konzeptfreigabe)

Eingebettet in die bestehende ChemBioMed-Roadmap (dort Phase 8 = „PH-Erweiterungsmodul“).

| Phase | Inhalt | Ergebnis |
|---|---|---|
| **P1 Pipeline** | `generate_cards.py`, Registry-Mapping, `validate_output.py`, Templates (Tabs/Boxen/Farbrollen) | reproduzierbare Erzeugung |
| **P2 Pilot-Content R1** | ~60 Karten R1 (Grundlagen, PK/PD, Notfall, Toxidrome, Top-Antidote) als `needs_review`/`*_review_needed` | Pilotbestand |
| **P3 Review R1** | Fachreview pharm/tox, `clinical_safety_review.md`, Freigabe approved | geprüfter Pilot |
| **P4 Export R1** | Moodle-Pakete + Druckpakete + Einzel-PNG/PDF (Gating) | distribuierbare Artefakte |
| **P5 Online-MVP** | `pharma-api` + `pharma-web` (Lernmodus, SR, Notizen, Download), DB-Seed | lauffähiges Lernsystem |
| **P6 Moodle LTI** | LTI-1.3-Integration + Deep Linking | Moodle-Live-Einbettung |
| **P7 Content R2/R3** | Aufbau-/Breiten-Wellen + Review | wachsender Bestand |
| **P8 Deploy/Hardening** | Compose/Traefik/OIDC-Authentik, Backups, CI | produktiver Betrieb |

---

## 3. Offene Punkte / Backlog (für Issues)

- [ ] ADR fixieren: Frontend-Framework (Svelte vs. React/Vue) in `online-platform/architecture/`.
- [ ] PH-Content-JSON-Schema (`cards/registry/ph.content.schema.json`) formal ergänzen.
- [ ] `validate_card_metadata.py` um PH-Content-/Scope-Validierung erweitern.
- [ ] Templates (Front/Back) um Tab-Leiste, Box-Slots, Farbrollen, Warnlevel-Badge erweitern.
- [ ] Fachreviewer benennen (Pharmakologie, Toxikologie) und Verantwortlichkeiten dokumentieren.
- [ ] Preis-/Paketlogik für PH in `package-registry.yaml` ergänzen (derzeit TBD).
- [ ] Moodle-Zielinstanz + LTI-Registrierungsdaten klären.
- [ ] Authentik-Application/Client für Pharma Cards anlegen (Prod-Auth).
- [ ] EAN/Verpackung für PH-Druckboxen (falls kommerzieller Vertrieb) klären.
- [ ] Rechtliche Freigabe/Haftungshinweis mit `docs/legal-rights-notes.md` abgleichen.

---

## 4. Nächster konkreter Schritt

Freigabe dieses Konzepts durch Andreas / Fachreview-Team. Danach Start mit **P1 (Pipeline)** und
**P2 (Pilot-Content R1)** — datenmodell-getrieben, Karten aus Daten generiert, nichts manuell gebaut.

---

## 5. Stand nach Umsetzung (2026-10-31)

| # | Kriterium | Stand | Nachweis |
|---|---|---|---|
| 4–6 | Einheitliches Layout, Tabs, Front/Back | ✅ | `card.css`, `render_cards.py`; Layoutprüfung 110/110 ohne Überlauf |
| 7–8 | Review-Status, kritische Karten markiert | ✅ | 110 Karten mit Status, Warnlevel, `review_focus`; Prozess in `review/` |
| 9 | Moodle-Importpakete | ✅ Generator | `generate_moodle_import.py`; Release leer, bis Karten freigegeben sind |
| 10–11 | Druck-PDFs, Einzel-PNG/PDF | ✅ Generator | `generate_print_sheets.py`; Vorschau visuell geprüft |
| 12–13 | Online-Lernsystem: lernen, markieren, wiederholen | ✅ MVP | API + SvelteKit; SM-2/Leitner; Browser-E2E 8/8 (auch gegen den Docker-Stack) |
| 14 | Notizen unter Karten | ✅ | Autospeicherung, Kursnotizen, Markdown-Export |
| 15 | Annotationen | ✅ vorbereitet | `annotation_data` in DB/API; Zeichenwerkzeuge offen |
| 16 | Download PNG/PDF online | ✅ | `/api/cards/{id}/download`, getestet (auch im Container) |
| 17 | Kategorien/Tags/Gruppen/Review bearbeitbar | 🟡 | über Scope-Konfiguration + Pull Request; Admin-UI offen |
| 19 | Deployment | ✅ | Dockerfiles, Compose, Traefik-Overlay, `online-platform/README_DEPLOYMENT.md` |

**Offen für den Produktivbetrieb:** SPA-Login über Authentik (OIDC/PKCE), Freigabe der ersten Karten
durch das Fachreview, LTI-1.3-Endpunkte für Moodle, Annotationswerkzeuge, Admin-UI.
