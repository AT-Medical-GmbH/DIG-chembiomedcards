# 01 — Analyse und Architektur

**Dokument:** Technische Analyse, Systemarchitektur, Technologieentscheidung
**Handover-Phasen:** 1 (Analyse/Struktur), 10 (Architektur Online-System)

---

## 1. Ausgangslage (Analyse)

### 1.1 Was bereits existiert

Das Repository `DIG-chembiomedcards` ist in der Konzept-/Prototypenphase und enthält eine reife,
konsistente Basis, auf der Pharma Cards aufsetzt:

- **Modulstruktur** AC/OC/BC/MB/APC/**PH** mit eindeutiger ID-Systematik (`ph_###`).
- **Registry** als Quelle der Wahrheit: `cards.master.csv` + JSON-Schema (`cards.master.schema.json`)
  + menschenlesbares `MASTER_DIRECTORY.md` + `package-registry.yaml`.
- **Layoutstandard** DIN A6 quer (148×105 mm), Inward-Tabs oben links, Logo rechts oben,
  Karten-ID links unten, QR + Copyright rechts unten.
- **Print-Spezifikation**: Beschnitt 3 mm, Safe Zone 5 mm, CMYK/ISO Coated v2, 300 dpi (QR 600 dpi),
  PDF/X-1a / X-4.
- **QR-Redirect-Service**: stabile, unveränderliche URLs `https://chembiomed-cards.de/c/<card-id>`,
  entkoppelt vom CMS.
- **Plattform-Betriebsmodell**: Initialbetrieb auf ATMED-core (WordPress/WooCommerce), Migrationspfad
  zu dediziertem Server; Zielbild zentrale Gateway/SSO-Authentifizierung.
- **Moodle/LMS-Anbindung**: `lms_url` je Karte, Modul = Kurs, Karte = URL-Aktivität; tiefere
  Integration (Plugin/OAuth2/SCORM/xAPI) als spätere Phase vorgesehen.
- **Skript-Scaffolds** (Python): `generate_card_registry.py`, `validate_card_metadata.py`,
  `generate_qr_codes.py`, `export_print_batch.py`.
- **PH ist vorbereitet, aber leer**: 242 Karten Zielumfang, 5 Beispielanker (`ph_001`–`ph_005`),
  Status `planned`.

### 1.2 Was Pharma Cards ergänzt

Der Handover fordert über die bestehende Basis hinaus:

1. **Fachliche Tiefe** in Pharmakologie **und Toxikologie** (Toxidrome, Antidote, Notfall, Interaktionen).
2. **Erweitertes, pharmaspezifisches Datenmodell** (Wirkmechanismus, PK/PD, Kontraindikationen,
   Interaktionen, Antidot/Toxidrom, Warnlevel, differenzierter Review-Status).
3. **Vollständiges Online-Lernsystem** mit Spaced Repetition, Notizen, Annotationen, Downloads,
   Editor, Rollen- und Review-Workflow.
4. **Robuste Moodle-Importpakete** und eine klare Moodle-Architekturentscheidung.
5. **Import-/Audit-Pipeline** für später hochgeladene Karten/Listen/PDFs.
6. **Medizinische Sicherheits-Governance** (Warnlevel, Dosierungspolitik, Freigabezwang für Export).

### 1.3 Konsequenz

Pharma Cards = **inhaltlicher und technischer Ausbau des Moduls PH**. Die drei Ebenen des Handovers
(Content / Export / Online) sind im Repo bereits angelegt und werden erweitert. Kein Parallel-Repo.

---

## 2. Architektur in drei Ebenen

```
                ┌───────────────────────────────────────────────────────────┐
                │  EBENE 1 — CONTENT (Single Source of Truth)                │
                │                                                           │
                │  cards/PH/metadata/*.yaml        ← Kartendatensätze        │
                │  cards/PH/scope/*.yaml           ← Kategorien/Tags/Config  │
                │  cards/registry/cards.master.csv ← abgeleitete Registry    │
                │  cards/registry/*.schema.json    ← Validierung             │
                └───────────────┬───────────────────────────┬───────────────┘
                                │                           │
             generate_* / validate_*                        │ API-Seed / DB-Import
                                │                           │
         ┌──────────────────────▼───────────┐   ┌───────────▼───────────────────────┐
         │  EBENE 2 — EXPORT (Artefakte)      │   │  EBENE 3 — ONLINE-LERNSYSTEM        │
         │                                    │   │                                    │
         │  PNG Front/Back (exports/web)      │   │  Backend-API (online-platform/     │
         │  SVG-Quellen                       │   │    backend) + PostgreSQL           │
         │  Einzelkarten-PDF                  │   │  Frontend-SPA (online-platform/    │
         │  A4/A3-Druckbögen (print-prod.)    │   │    frontend)                       │
         │  Moodle-Pakete (exports/...)       │   │  Spaced Repetition, Notizen,       │
         │  QR-Codes (exports/qr)             │   │  Annotationen, Downloads, Editor   │
         └────────────────────────────────────┘   └───────────────┬────────────────────┘
                                                                   │
                                   ┌───────────────────────────────┼───────────────────┐
                                   │ QR-Redirect  │ WooCommerce→SSO │ Moodle (LTI/iframe)│
                                   │ /c/<card-id> │ Lizenz/Auth     │ Kurs-Einbettung    │
                                   └──────────────┴─────────────────┴───────────────────┘
```

**Zentrale Eigenschaft:** Ebene 2 und Ebene 3 konsumieren **dieselben** Kartendaten aus Ebene 1.
Bilder werden generiert (nicht gepflegt); die Online-App rendert aus strukturierten Feldern und zeigt
generierte Bilder nur als optionale Download-/Print-Artefakte.

---

## 3. Reproduzierbarkeits-Pipeline

Deterministische Kette (jeder Schritt idempotent, skriptgesteuert, CI-fähig):

```
  (0) imports/pharma/*  ──extract──▶  (1) cards/PH/metadata/*.yaml  ──validate──▶  OK/Fehlerbericht
                                                   │
                                                   ├─ generate_card_registry.py ─▶ cards.master.csv
                                                   ├─ generate_cards (HTML/SVG→PNG/PDF) ─▶ exports/
                                                   ├─ generate_qr_codes.py ─▶ exports/qr/
                                                   ├─ generate_print_sheets ─▶ print-production/exports/
                                                   ├─ generate_moodle_import ─▶ exports/moodle/
                                                   └─ seed_online_db ─▶ PostgreSQL (online-platform)
```

Vorgaben:

- **Ein Kommando pro Stufe**, alle über `make`/`scripts/` orchestrierbar; CI (GitHub Actions) ruft
  dieselben Kommandos auf, die lokal laufen.
- **Validierung ist Gate**: Kein Export/Seed ohne bestandene Schema-Validierung (siehe Dok. 10 zur
  Review-/Export-Gating-Politik).
- **Determinismus**: gleiche Eingabe → gleiche Ausgabe (fixe Schriftversionen, fixe Template-Version,
  keine Netzwerkabhängigkeit beim Rendern).

---

## 4. Technologieentscheidung Online-System

### 4.1 Randbedingungen (aus der AT-Medical-Systemlandschaft)

- Initialbetrieb WordPress/WooCommerce auf ATMED-core; Migration zu dediziertem Server vorgesehen.
- Zielbild **zentrale SSO-Authentifizierung** (Authentik ist in der AT-Medical-Landschaft vorhanden:
  Repos `ATMED-authentik`, `ATMED-auth`).
- Reverse Proxy **Traefik** vorhanden (`ATMED-traefik`).
- Moodle-Lernplattform ist Referenz-LMS.
- Datenbank soll migrierbar und schema-sauber sein (bestehende Entkopplungsanforderung).

### 4.2 Entscheidung (begründet)

| Schicht | Entscheidung | Begründung |
|---|---|---|
| **Backend** | **FastAPI (Python 3.11+)** | Die gesamte Content-/Export-Pipeline ist bereits Python. Ein Stack vermeidet Doppel-Toolchains; FastAPI liefert OpenAPI automatisch (Moodle/LTI-Integration), ist schlank, async-fähig, Container-freundlich. |
| **Datenbank** | **PostgreSQL 16** | Vom Handover vorgegeben; JSONB für `annotation_data`/`content_snapshot`, robuste Constraints, saubere Migrationen (Alembic). |
| **Frontend** | **Svelte/SvelteKit (TypeScript)** | Kleinstes JS-Bundle, exzellente Lade-/Animationsperformance (Kartenflip, Tablet-first), einfache Web-Component-Auslieferung für WordPress-/Moodle-iframe-Einbettung. React/Vue bleiben valide Alternativen; die Entscheidung ist in `online-platform/architecture/` als ADR zu fixieren. |
| **Auth** | **lokal (dev) → OIDC/Authentik (prod)** | Deckt sich mit dem dokumentierten Gateway/SSO-Zielbild. JWT-Access + Refresh, Paket-Claims im Token (bestehende `gateway-authentication.md`). |
| **Lizenz/Commerce** | **WooCommerce-Webhook → eigene Lizenztabelle** | Bestehende Entscheidung; Lizenzlogik hinter eigener API, WooCommerce nur als Trigger. |
| **Rendering/Export** | **Playwright (Chromium, vorinstalliert)** | HTML/CSS-Templates → PNG/PDF. Chromium ist in der Umgebung vorhanden (`PLAYWRIGHT_BROWSERS_PATH`), keine Zusatzinstallation. |
| **Deployment** | **Docker Compose, Traefik-kompatibel** | App + DB + Storage sauber getrennt; siehe Dok. 09. |
| **API-Stil** | **REST (OpenAPI 3)** | Breite Kompatibilität (Moodle, WordPress, LTI-Tools); GraphQL nicht erforderlich für den Funktionsumfang. |

### 4.3 Komponentenschnitt (Deployable Units)

1. **`pharma-api`** — FastAPI-Service: Karten, Fortschritt, Notizen, Review, Export-Trigger, LTI-Endpoints.
2. **`pharma-web`** — SvelteKit-SPA/SSR: Lern-, Wiederholungs-, Editor-, Statistik-Ansichten.
3. **`qr-redirect`** — bestehender leichtgewichtiger Redirect (unverändert, stabilisiert), separat
   deploybar; **darf nie die stabile URL ändern**.
4. **`postgres`** — Datenbank.
5. **`object-storage`** — S3-kompatibel/lokal/Nextcloud-kompatibel für generierte Bilder & Exporte.
6. **Reverse Proxy** — Traefik (vorhanden), terminiert TLS, routet auf interne Ports.

Jede Unit ist unabhängig migrierbar (Blue/Green-Strategie der bestehenden Migrationsdoku bleibt gültig).

---

## 5. Datenfluss Content → Online (kein Bildgalerie-Antipattern)

1. Redaktion pflegt `cards/PH/metadata/ph_###_<slug>.yaml` (strukturierte Felder).
2. CI validiert, generiert Registry + Bilder + QR + Moodle-Pakete.
3. `seed_online_db` überführt **die strukturierten Felder** (nicht nur Bildpfade) in PostgreSQL.
4. Die Online-App rendert Vorder-/Rückseite **aus den Feldern** (HTML-Template im Browser) und bietet
   das generierte PNG/PDF nur als Download/Print an.
5. Nutzer-spezifische Daten (Fortschritt, Notizen, Annotationen) liegen getrennt von den Kartendaten
   und werden nie in Bilder geschrieben (Annotationen als JSON-Overlay, siehe Dok. 08).

---

## 6. Nicht-funktionale Anforderungen

- **Performance:** Kartenansicht < 1,5 s initial, Flip-Animation 60 fps, QR-Redirect < 50 ms.
- **Barrierearmut:** WCAG-AA-Kontraste, Tastatursteuerung, große Schrift, Fokusmodus.
- **Responsiv:** Tablet-first, Smartphone und Desktop vollwertig.
- **Datenschutz:** Lernstatus/Notizen personenbezogen → DSGVO-konform, Scan-Logs anonym (bestehende Vorgabe).
- **Wartbarkeit:** Ein Datenmodell, eine Template-Quelle, konfigurierbare Kategorien.
- **Migrierbarkeit:** DB-Dump + Storage + Redirect-Tabelle als geschlossene Einheit umziehbar.
