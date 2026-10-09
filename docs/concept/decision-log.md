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
