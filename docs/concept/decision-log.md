# Decision Log (ADR-Kurzform)

Jede Entscheidung: Kontext → Entscheidung → Begründung → Konsequenz. Status `accepted` = im
Konzept umgesetzt; `proposed` = wartet auf Bestätigung (siehe [offene Fragen](open-questions.md)).

---

### ADR-001 — Datenmodell als Single Source of Truth · *accepted*
**Kontext:** Karten existieren heute teils als Bilder/CSV. **Entscheidung:** YAML je Karte →
kanonisches `cards_master.json`; alle Bilder/PDFs/Moodle-Pakete sind generierte Artefakte.
**Begründung:** Reproduzierbarkeit, Review, Einheitlichkeit. **Konsequenz:** Alt-Bilder sind
Inhaltsquelle, nicht finales Artefakt; Neugenerierung erzwingt einheitliches Layout.

### ADR-002 — Rendering via HTML/CSS → Playwright · *accepted*
**Entscheidung:** HTML/CSS + Jinja2, gerendert mit Playwright (Chromium) zu PNG/PDF; SVG als
editierbare Zweitquelle. **Begründung:** Playwright vorinstalliert; eine Engine für Build **und**
Online-Export → pixelgleiche Ergebnisse. **Konsequenz:** gemeinsame Template-/Token-Basis.

### ADR-003 — Kartenformat DIN A6 quer · *accepted*
**Entscheidung:** 148 × 105 mm + 3 mm Beschnitt, auf A4/A3-Bögen montiert. **Begründung:**
bestehender Repo-Standard, druck- und online-tauglich. **Konsequenz:** Print-Montagelogik Kap. 07.

### ADR-004 — Tab-Taxonomie folgt Handover, Modulcodes bleiben · *proposed*
**Kontext:** Handover-Tabs (6) vs. bestehende Modulcodes (AC/OC/BC/MB/APC/PH). **Entscheidung:**
sichtbare Tabs = Handover (Allgemein/Anorganik/Organik/Molekularbio/Biochemie/Klinik);
Modul-/Paketcodes unverändert; Mapping in Kap. 03 §4. **Begründung:** erfüllt Handover **und**
hält IDs/Registry stabil. **Konsequenz:** zwei getrennte Dimensionen; Bestätigung ausstehend
(APC/PH als eigene Tabs?).

### ADR-005 — Spaced Repetition: SM-2 + Leitner-Overlay · *accepted*
**Entscheidung:** SM-2-Felder (ease/interval/repetitions) plus sichtbare Leitner-Box.
**Begründung:** bewährt + erklärbar. **Konsequenz:** `user_progress`-Felder Kap. 11.

### ADR-006 — Online-Frontend React/TS/Vite · *accepted*
**Begründung:** größtes Ökosystem, Webcomponent-Einbettung (WordPress/Moodle), ATMED-Weblinie.

### ADR-007 — Online-Backend FastAPI/PostgreSQL · *accepted*
**Begründung:** gleiche Sprache wie Pipeline → geteilter Code (Schema/Export); OpenAPI-nativ.
**Konsequenz:** ein Python-Monorepo-Teil für Pipeline + API.

### ADR-008 — Moodle: LTI 1.3 strategisch, Importpakete interim · *proposed*
**Entscheidung:** LTI-1.3-Tool (SSO, Deep Linking, AGS) als Hauptpfad; CSV/H5P/iframe ergänzend.
**Begründung:** vermeidet Plugin-Pflege über Moodle-Versionen. **Konsequenz:** Abstimmung mit
Moodle-Betrieb nötig (Version/Plugin/AGS).

### ADR-009 — Auth: lokal (Dev) / OIDC-Authentik (Prod) · *accepted*
**Begründung:** `ATMED-authentik` existiert; zentrale Identität/SSO; dev-freundlich lokal.

### ADR-010 — Storage S3-kompatibel · *accepted*
**Begründung:** Trennung App/DB/Storage; portabel (MinIO → dediziert/Nextcloud-kompatibel).

### ADR-011 — Annotationen als nicht-destruktives Overlay · *accepted*
**Entscheidung:** JSON-Koordinaten über dem Bild; Original unverändert; Export rendert optional ein.
**Begründung:** Original bleibt intakt; mehrere Nutzer-Overlays pro Karte.

### ADR-012 — Deployment Docker Compose + Traefik, Staging-first · *accepted*
**Begründung:** ATMED-Betriebsmuster (`ATMED-traefik`), saubere Produktion.

### ADR-013 — `app/` (Code) neben `online-platform/` (Notizen) · *proposed*
**Entscheidung:** Implementierung in `app/`, bestehende Notizen in `online-platform/` verweisen
darauf. **Begründung:** nichts stillschweigend löschen. **Konsequenz:** spätere Konsolidierung
offen (siehe offene Fragen).

### ADR-014 — Produktion aus Daten statt Altbestand-Übernahme · *accepted*
**Kontext:** Es gibt nur Musterkarten und eine Planungsliste, keinen großen Altbestand (Klärung
2026-10-31). **Entscheidung:** Karten werden direkt als Datensätze angelegt und generiert; die
Import-/Audit-Pipeline (Kap. 04) dient nur noch für Muster und Fremdzulieferungen.
**Konsequenz:** Serienproduktion kann ohne Upload beginnen; Muster werden zum Layout-Abgleich genutzt.

### ADR-015 — Startumfang: Handover-Soll-Liste vor Masterverzeichnis · *accepted*
**Entscheidung:** Zuerst die ~170 Karten der Handover-Soll-Liste (Kap. 14 §2), danach schrittweise die
1.452 Karten aus `MASTER_DIRECTORY.md`. Pilot: 20 proteinogene Aminosäuren.
**Begründung:** Testet die strengste Darstellungsregel (Fischer-Projektion) und ein vollständiges
Rückseitenschema, bevor die Serie skaliert.

### ADR-016 — Vorläufige IDs (Aminosäuren `bc_098`–`bc_117`, siehe auch ADR-020) · *proposed*
**Kontext:** Das Masterverzeichnis vergibt im BC-Kapitel „Aminosäuren, Proteine und Stickstoff“ nur den
Anker `bc_097` (Aminosäure-Grundstruktur). **Entscheidung:** fortlaufend direkt danach, als
`id_status: provisional` markiert. **Konsequenz:** Bestätigung oder Umnummerierung vor der
Freigabe nötig; die Validierung warnt, solange IDs vorläufig sind.

### ADR-017 — QR-Code nur auf der Rückseite; Wortmarke als Logo-Platzhalter · *QR accepted, Logo-Teil abgelöst durch ADR-021*
**Entscheidung:** Die Vorderseite bleibt ohne QR-Code, damit sie die Antwort nicht verrät (bewusst
reduzierte Vorderseite). Bis ein freigegebenes Logo unter `brand/logo/` liegt, steht oben rechts eine
Text-Wortmarke „ChemBioMed Cards · AT Medical“. **Konsequenz:** Logo-Datei nachliefern; der Austausch
betrifft nur die Kopfzone in `templates/card_template.html`.

### ADR-018 — Eine zentrale Kartenvorlage · *accepted*
**Kontext:** Vorgabe: Layout muss auf einer zentralen Datei beruhen und jederzeit änderbar sein,
Inhalte einzeln austauschbar. **Entscheidung:** `templates/card_template.html` enthält das gesamte
Kartenlayout (CSS, Kopfzone, Vorder- und Rückseite); Farben/Format bleiben als Tokens getrennt, weil
das Online-System sie mitnutzt. Inhalte liegen je Karte in `data/cards/<card_id>.yaml`.
**Konsequenz:** Der Generator bildet einen Hash über Vorlage, Tokens und Renderer – ändert sich
davon etwas, werden alle Karten neu erzeugt; ändert sich nur eine Kartendatei, nur diese Karte.

### ADR-019 — Strukturformeln aus PubChem + RDKit, physiologische Form bei „-at“ · *accepted*
**Entscheidung:** Für Moleküle außer α-Aminosäuren wird die Struktur aus PubChem übernommen
(`pubchem_cid` in der Kartendatei) und mit RDKit als Skelettformel gezeichnet. Carbon-, Phosphat- und
Sulfonsäuregruppen werden bei Namen auf „-at“ deprotoniert (`form: physiological`), Säuren mit
„-säure“-Namen bleiben neutral. α-Aminosäuren (auch Derivate wie Homocystein, L-DOPA) folgen der
Fischer-Konvention. Vitamine und Peptidhormone zeigen vorne nur die Bezeichnung, Ionen die Formel.
**Begründung:** geprüfte Quelle statt abgetippter Strukturen; ein Layoutverfahren für alle.
**Konsequenz:** Abkürzungen wie „CoA“ oder Reste R₁–R₃ über Platzhalteratome; der Generator prüft
Atombeschriftungen auf Mindestabstand und meldet Problemfälle (`front_content.layout` als Ausweg).

### ADR-020 — ID-Blöcke für die Handover-Soll-Liste · *proposed*
**Entscheidung (vorläufig, `id_status: provisional`):** Stoffwechsel `bc_061`–`bc_081` um den Anker
`bc_073` Acetyl-CoA (bestätigt), Derivate `bc_118`–`bc_131`, Stickstoffstoffwechsel `bc_132`–`bc_135`,
Lipide `bc_140`–`bc_151`, Neurotransmitter `bc_160`–`bc_169`, Hormone `bc_170`–`bc_184` (vor dem Anker
`bc_188`), Nukleotide/Coenzyme `bc_200`–`bc_212`, Vitamine `bc_256`–`bc_269` ab dem Anker `bc_256`
Vitamin A (bestätigt). Alle Karten im Modul BC; Second Messenger mit Hauptkategorie Molekularbio.
**Konsequenz:** Bestätigung oder Umnummerierung vor der Freigabe; Ankernummern sind unverändert.

### ADR-021 — Offizielles Logo im Kartenkopf; Kartenfarben aus dem Logo · *accepted*
**Kontext:** AT Medical hat das Logo „ChemBioMed Cards – by AT Medical GmbH®“ für die Karten
bereitgestellt. **Entscheidung:** Rechts oben steht auf beiden Seiten die Kompaktfassung (Bildmarke +
Wortmarke, ohne Unterzeilen, 9,6 mm hoch) statt der Text-Wortmarke. Die Kartenfarben übernehmen die
Logofarben, die der Farblogik bereits entsprechen: Navy `#03204c` für Grundinformation/Chemie-Tabs,
Petrol `#06807d` für Biochemie, Rot `#a90411` für Klinik; Molekularbio (Blau) und Merke (Violett)
bleiben. **Begründung:** Das Logo kodiert Chem/Bio/Med farbig – Karten und Logo sprechen dieselbe
Sprache. **Konsequenz:** Varianten werden reproduzierbar aus dem Original abgeleitet
(`scripts/derive_logo_assets.py`); der Generator prüft, dass das Logo geladen ist und keine Inhalte
überdeckt. Rückgängig/anpassbar allein über die Tokens.
