# Übergabe: ChemBioMed Cards – Cloud-Session an Server-Session

**Projekt 16 · ChemBioMed Cards (AT Medical GmbH)** · Stand 18.11.2026

- **Von:** Claude-Code-Cloud-Session `session_01QNnLUe6QEgJguzuLT6k77J`; sie wird nach dieser
  Übergabe archiviert.
- **An:** die Server-Session, die das Projekt im eigenen Git auf ATMED-core betreut, laut Auftrag
  vom 03.11.2026 `claude-code-atmed-core`.
- **Hintergrund:** Andreas betreibt das Projekt nicht mehr auf GitHub, sondern im eigenen Git
  (Forgejo) auf dem Server.
- **Inhalt:** Diese Datei fasst den gesamten Inhalt der Cloud-Session zusammen und ist ab jetzt der
  Einstieg für alle weiteren Arbeiten.

---

## 1. Auftrag und Ziel

- **Ziel:** ein datengetriebenes Lernkartensystem mit drei Ebenen:
  1. **Content:** eine YAML-Datei je Karte als einzige Quelle der Wahrheit;
  2. **Export:** PNG mit 300 dpi, PDF im Format DIN A6 quer (148 × 105 mm), Druckbögen,
     Moodle-Pakete;
  3. **Online-Lernsystem.**
- **Grundlage:** das Handover mit 17 Phasen und 20 Akzeptanzkriterien.
- **Leitplanken aus dem Handover, weiterhin gültig:**
  - keine spontanen Layoutwechsel;
  - keine Sammelbilder als Einzelkarten;
  - keine unkontrollierte Erweiterung der Stoffliste;
  - keine endgültigen fachlichen Behauptungen ohne Prüfung; bei Unsicherheit den Prüfstatus
    `needs_review` setzen;
  - das Datenmodell kommt zuerst, die Bilder werden daraus erzeugt;
  - Reproduzierbarkeit ist Pflicht.

## 2. Wo alles liegt

- **Quellstand:** Branch `claude/chembio-cards-planning-c5l2ub`, letzter Commit dieser Session
  `95c3729` (plus diese Übergabedatei). Im eigenen Git wird er über einen PR nach `main` gebracht,
  siehe Runbook Phase 4, Schritt 1.
- **Einstiegsdateien:**

  | Thema | Datei |
  |---|---|
  | Gesamtkonzept (Kapitel 00–16) | `docs/concept/README.md` |
  | Architekturentscheidungen ADR-001–024 | `docs/concept/decision-log.md` |
  | Offene Punkte | `docs/concept/open-questions.md` |
  | Layout ändern / Inhalte einzeln austauschen | `templates/README.md` |
  | Betrieb auf ATMED-core (Phasen 0–7, Gates, Rollback) | `deploy/README_MIGRATION.md` |
  | ATLAS-Verkehr dieser Session | `docs/communication/` |
  | Änderungsverlauf | `CHANGELOG.md` |

## 3. Was produziert ist

- **116 Karten** (die vollständige Soll-Liste aus dem Handover) liegen unter
  `data/cards/<card_id>.yaml`. Alle haben `review_status: needs_review` und `id_status: confirmed`.
  Alle sind im Modul BC; die Second Messenger tragen die Hauptkategorie Molekularbio.

  | Gruppe | Karten-IDs |
  |---|---|
  | Zentraler Stoffwechsel | `bc_061`–`bc_065`, `bc_073`–`bc_081` |
  | Proteinogene Aminosäuren | `bc_098`–`bc_117` |
  | Derivate | `bc_118`–`bc_131` |
  | Stickstoffstoffwechsel | `bc_132`–`bc_135` |
  | Lipide | `bc_140`–`bc_151` |
  | Neurotransmitter | `bc_160`–`bc_169` |
  | Hormone | `bc_170`–`bc_184` |
  | Nukleotide, Coenzyme, Second Messenger | `bc_200`–`bc_212` |
  | Vitamine | `bc_256`–`bc_269` |

  Sonderfälle: Bei `bc_129` und `bc_204` ist `layout: rdkit` gesetzt. `bc_063`
  (Fructose-6-phosphat) verwendet die Ringform aus PubChem-CID 440641.
- **Layout aus einer zentralen Vorlage:** `templates/card_template.html` (Jinja2) enthält CSS,
  Kopfzone, Vorder- und Rückseite.
  - Farben, Format und Schrift kommen aus `brand/design-tokens/chembiomed.tokens.json` → `card`.
  - Die Tabs stehen in `data/categories.yaml`, das kontrollierte Vokabular in `data/tags.yaml`.
  - Eine Änderung an der Vorlage rendert alle Karten neu, eine Änderung an einer Kartendatei nur
    diese Karte. Der Generator merkt sich dafür je Karte einen Fingerabdruck.
- **Vorderseitentypen:**
  - `fischer_projection`: Aminosäuren ohne Namen, als eigenes SVG aus `scripts/cbm/fischer.py`;
  - `molecule`: Strukturformel per RDKit aus PubChem-SMILES (`scripts/cbm/molecule.py`).
    Optionen: `form: physiological` deprotoniert die Gruppen; Platzhalteratome `[*:n]` erhalten
    `labels`; `layout` ist `auto`, `rdkit` oder `coordgen`;
  - `term`: Vitamine und Peptidhormone, nur die Bezeichnung;
  - `formula`: Ionen.
- **Taxonomie:** fünf Tabs – Allg./Anorganik · Organik · Molekularbio · Biochemie · Klinik
  (ADR-022). Die Modulcodes AC/OC/BC/MB/APC/PH bleiben als eigene Dimension.
- **Logo:** Das offizielle Logo liegt unter `brand/logo/source/`. Die Varianten werden mit
  `scripts/derive_logo_assets.py` abgeleitet. Im Kartenkopf steht die Kompaktfassung (ADR-021).
- **Farben aus dem Logo:**

  | Farbe | Wert | Verwendung |
  |---|---|---|
  | Navy | `#03204c` | Grundinformation, Chemie-Tabs |
  | Petrol | `#06807d` | Biochemie |
  | Rot | `#a90411` | Klinik |
  | Blau | `#2563eb` | Molekularbiologie |
  | Violett | `#7c3aed` | Merke |

  Die Vektorfassung `brand/logo/chembiomed-cards-logo-full.svg` ist eine automatische
  Nachzeichnung; die Abnahme steht noch aus.
- **Automatische Prüfungen:**
  - **Generator:** Überlauf der Rückseite; fünf Tabs mit genau einem aktiven; Schrift Inter
    geladen; Atombeschriftungen mit mindestens etwa 1 mm Abstand; Logo geladen und ohne
    Überdeckung von Inhalten.
  - **Validierung:** JSON-Schema plus Projektregeln:
    - ID-Präfix passt zum Modul;
    - Tags und Tabs sind gültig;
    - kein Name auf Aminosäure-Vorderseiten;
    - Platzhalter und `labels` passen zusammen;
    - Formeln enthalten nur `<sub>` und `<sup>`;
    - `approved` erfordert `reviewer` und `references`.
- **Befehle:**
  - `make build PY=python3.13` – entspricht `validate`, `cards` und `reports` nacheinander.
  - Im Build-Image genügt `make build PY=python`.
  - Ergebnis: `generated/individual/...`, `generated/preview/contact_sheet_<gruppe>.png`,
    `generated/manifest.json`, `reports/layout_review.md`, `reports/cards_review_needed.md`.
    Das Masterverzeichnis `cards/registry/MASTER_DIRECTORY.md` wird automatisch gepflegt.

## 4. Betrieb auf ATMED-core (ADR-024)

- **Entscheidungen von Andreas (03.11.2026):**
  - eigenes Forgejo v15 LTS auf ATMED-core;
  - Staging bei jeder Änderung auf `main` automatisch;
  - Produktion nur per manuellem Start mit der Bestätigung „FREIGABE“ und nur mit Karten im
    Status `approved`;
  - GitHub nicht weiterbetreiben: archivieren, sobald Staging aus Forgejo läuft (Gate G4).
- **Bausteine im Repository:**

  | Datei | Inhalt |
  |---|---|
  | `deploy/builder/Dockerfile` | Build- und Runner-Image: Playwright 1.56, Forgejo-Runner 13.2.1 mit Prüfsumme, Schrift Inter, RDKit |
  | `deploy/atmed-core/forgejo/` | Forgejo-Stack (`compose.yaml`, `.env.example`) und Sicherung (`forgejo dump` per systemd-Timer nach `/srv/atmed/stacks/forgejo/sicherung`) |
  | `deploy/atmed-core/chembiomed-cards/` | Runner im Host-Modus (kein Docker-Socket, ohne Root, `mem_limit` 3 GB, Kapazität 1) und nginx für Staging und Produktion mit Kennwortschutz (htpasswd, apr1) |
  | `.forgejo/workflows/cards.yml` | CI: PR → prüfen und rendern; Push auf `main` → Staging; manueller Start mit `production` + `FREIGABE` → Produktion |
  | `scripts/release_cards.py` | Paket je Kanal; Produktion bricht mit Code 3 ab, wenn keine Karte `approved` ist |
  | `deploy/scripts/publish-release.sh`, `rollback-release.sh` | Veröffentlichung atomar per Symlink; 5 Stände bleiben für ein Rollback |
  | `deploy/scripts/00-preflight-readonly.sh` | Read-only-Vorabprüfung |
  | `deploy/scripts/10-migrate-from-github.sh` | Übernahme von GitHub mit Issues und PRs |

- **Lokal getestet (03.11.2026, Docker):**
  - Alle 116 Karten im Build-Image, 0 Layoutfehler, etwa 75 Sekunden.
  - Forgejo 15.0.11 mit Runner: Ein Push auf `main` hat Staging veröffentlicht.
  - Die Produktion hat einen Lauf ohne „FREIGABE“ und einen ohne freigegebene Karten abgelehnt.
    Mit einer Testkarte auf `approved` ging genau diese eine Karte live.
  - Rollback vor und zurück, `forgejo dump` mit Prüfsumme und der Kennwortschutz von nginx
    (401 ohne bzw. mit falschem Kennwort, 200 mit richtigem) funktionierten.
- **Nicht getestet:** die Live-Übernahme von GitHub sowie Traefik und DNS auf core.
- **Ergebnis Phase 0 (core, 03.11.):**
  - Traefik: Netz `traefik_web`, Entrypoint `websecure`, Certresolver `letsencrypt` per
    DNS-Challenge.
  - Auf core gibt es keine Authentik-Forward-Auth. Staging und Produktion sind deshalb per Kennwort
    geschützt; Forgejo meldet sich über Authentik-OIDC an.
  - Restic schließt `/srv/atmed/backups` aus; die Sicherung liegt deshalb im Stack-Ordner.
  - Cloudflare-Proxy für alle drei Hostnamen an.
  - Live-Zeiten, in denen nicht gearbeitet wird: Mo–Fr 17:45–20:15, Sa/So 07:45–10:00 und
    12:30–14:00.
- **Hostnamen:** `git.at-medical.de`, `staging.chembiomed-cards.de`,
  `releases.chembiomed-cards.de`.
- **Auftrag an core vom 03.11.** (ATLAS-ID `20261103T183819-andreas-mcp-70852`): Phasen 1–5 sind
  freigegeben.

## 5. Offen – bitte übernehmen

1. **Umzug abschließen bzw. prüfen** (Runbook Phasen 1–7):
   - Nach Gate G4 meldet core Andreas, dass die Refs von GitHub und Forgejo übereinstimmen.
   - Andreas archiviert dann GitHub.
   - Danach das Inventar nachziehen: ATMED-infrastructure `service-catalog.json` und ein Runbook
     in ATMED-docs.
2. **Fachreview der 116 Karten** durch Andreas (Arbeitsliste: `reports/cards_review_needed.md`).
   - Korrekturen nur in den YAML-Dateien.
   - Bei Freigabe einer Karte: `approved` mit `reviewer` und `references` setzen.
   - Danach den Produktionslauf mit „FREIGABE“ starten.
3. **Abnahme der Logo-Vektorfassung** durch AT Medical.
4. **Druckpakete** (entschieden):
   - A4 mit 4 Karten pro Seite, Duplex über die lange Kante, mit Schnittmarken;
   - zusätzlich Varianten mit 2 und 8 Karten pro Seite und ohne Schnittmarken;
   - RGB jetzt, CMYK final mit der Druckerei.
5. **Moodle-Importpakete:** Das Plugin ist noch zu klären.
   - Laut Andreas vom 03.11. (an core) soll ein Lernkarten-Plugin für Kurs 40 erst nach dem
     LearningOS-Einbau installiert werden.
   - Bis dahin Importpakete in mehreren Standardformaten erstellen.
   - LTI 1.3 zunächst ohne Notenrückgabe (ADR-008).
6. **Online-MVP auf Staging:**
   - FastAPI, React/TypeScript/Vite, PostgreSQL, S3/MinIO.
   - Authentik-Application `chembiomed-cards` mit den Gruppen
     `chembiomed-admins/-editors/-reviewers/-dozenten`.
   - Lizenzen pro Modul über WooCommerce.
   - Uploads mit Speicherkontingent (Virenprüfung, Löschkonzept).
   - Lernlogik SM-2 mit Leitner-Kästen.
   - Code-Verzeichnis `app/` (ADR-013).
7. **APC/PH als eigene Tabs:** später entscheiden, sobald es Inhalte gibt.
8. **Newsletter-Meldung:** Text von Andreas am 31.10. freigegeben, über ATLAS bisher **nicht**
   versendet (der Empfänger ist offen). Text: `docs/communication/2026-11-newsletter-meldung.md`.
   - Der Hinweis zum Bildmaterial verweist noch auf GitHub und muss vor dem Versand auf den
     Forgejo-Ort angepasst werden.
9. **Pharma-PR #8:** läuft getrennt weiter. Bei einer Spiegelkopie ohne Issues als Issue in
   Forgejo vermerken.
10. **Hinweis:** Auf GitHub meldete Dependabot am 03.11. eine Schwachstelle der Stufe „low“ im
    Default-Branch. Nach dem Umzug die Abhängigkeiten (`requirements.txt`) im eigenen Git prüfen.

## 6. Arbeitsregeln

- **Python:** lokal `python3.13`, im Image `python`.
- **Neue Karte:** eine bestehende Datei als Muster kopieren, `card_id`, `slug` und Inhalte
  anpassen; neue Tags vorher in `data/tags.yaml` eintragen.
- **Korrekturen:** `version` erhöhen (Patch) und `updated_at` setzen.
- **Commits:** Format `<typ>(<bereich>): …`; keine Modell-ID in Commits oder Artefakten.
- **Sicherheit:** keine Secrets und keine Personendaten ins Repository oder in Nachrichten.
- **Server:** read-only zuerst, Staging-first, keine destruktiven Schritte ohne Freigabe von
  Andreas.

## 7. Rückfragen an Andreas, die noch offen sind

- Empfänger für die Newsletter-Meldung.
- GitHub-Lesetoken für eine Übernahme mit Issues und PRs, falls noch nicht geschehen.
