# Pharma Cards — Konzeptdossier

**Projekt:** Pharma Cards (Modul **PH** innerhalb von ChemBioMed Cards)
**Betreiber:** AT Medical GmbH
**Status:** Konzept- und Setup-Phase (Branch `claude/pharma-cards-project-setup-apbnpz`)
**Stand:** 2026-10-09

---

## 1. Was ist dieses Dossier?

Dieses Verzeichnis ist das **vollständige technische und fachliche Konzept** für *Pharma Cards* — ein
didaktisch hochwertiges Lernkarten-System für Pharmakologie, klinische Pharmakologie,
Arzneimittellehre, Toxikologie, Notfalltoxikologie, Pharmakokinetik/-dynamik und angrenzende
Fachgebiete.

Es setzt den Projektauftrag („Handover Pharma Cards“, 18 Phasen) um, **ohne das bestehende
Repository zu duplizieren**. Pharma Cards ist **kein neues, konkurrierendes Repository**, sondern der
inhaltliche und technische **Ausbau des bereits vorbereiteten Moduls `PH`** von
ChemBioMed Cards (siehe `cards/registry/MASTER_DIRECTORY.md`, Roadmap-Phase 8).

> **Leitentscheidung:** Der Handover schlägt eine eigene `pharma-cards/`-Struktur vor, sagt aber
> ausdrücklich: *„Falls bereits ein Repository vorhanden ist, arbeite darin.“* Das ist hier der Fall.
> Alle etablierten Standards von ChemBioMed Cards (DIN-A6-Layout, Inward-Tabs, Registry-Schema,
> QR-Redirect-Service, WooCommerce→SSO-Migrationspfad, Moodle-Anbindung) gelten und werden
> erweitert — nicht ersetzt. Die Mapping-Tabelle in Abschnitt 4 zeigt, wo jede vorgeschlagene
> Handover-Struktur im bestehenden Repo lebt.

---

## 2. Das Zielbild in drei Ebenen

Pharma Cards wird auf drei Ebenen gebaut (identisch zur Handover-Vorgabe, eingebettet in ChemBioMed Cards):

| Ebene | Inhalt | Primärer Ort im Repo |
|---|---|---|
| **1 — Content** | Versionierbare, fachlich geprüfte Kartendaten; einheitliche Kategorien/Tags; Quellen & Review-Status; reproduzierbare Generierung | `cards/PH/` (Daten), `cards/PH/scope/` (Konfiguration), `cards/registry/` (Registry) |
| **2 — Export** | Einzelbilder Front/Back, Moodle-Pakete, druckfertige PDFs, Einzelkarten-Downloads, Gesamtexporte | `exports/`, `print-production/`, `scripts/` |
| **3 — Online-Lernsystem** | Interaktive Lernoberfläche, Lernstatus, Spaced Repetition, Notizen/Annotationen, Editor, Moodle-Integration | `online-platform/` |

**Grundprinzip (nicht verhandelbar):** Die Bilddateien sind **Export-Artefakte**, nicht die Quelle der
Wahrheit. Quelle der Wahrheit ist der strukturierte Kartendatensatz. Jede Karte wird aus Daten +
Template reproduzierbar erzeugt.

---

## 3. Leseführung — Dokumente dieses Dossiers

| # | Dokument | Inhalt | Handover-Phase |
|---|---|---|---|
| 00 | `README.md` *(dieses Dokument)* | Überblick, Einordnung, Mapping, Akzeptanz | 1, 18 |
| 01 | `01_analyse-und-architektur.md` | Technische Analyse, 3-Ebenen-Architektur, Tech-Stack-Entscheidung, Reproduzierbarkeit | 1, 10 |
| 02 | `02_datenmodell.md` | Kartendatenmodell (erweitert), relationales Online-Datenmodell | 3, 11 |
| 03 | `03_fachliche-zielstruktur.md` | Fachbereiche Pharmakologie + Toxikologie, erweiterbares Kategorienmodell | 2, 13 |
| 04 | `04_startliste-kuratiert.md` | Kuratierte, priorisierte Startliste mit Release-Wellen | 4 |
| 05 | `05_kartenlayout.md` | Tab-System, Farblogik, Front-/Back-Kartentypen, Online-Template | 5 |
| 06 | `06_generierung-und-print.md` | Generierungs-Pipeline, Druckbögen, Druckpakete | 6, 7 |
| 07 | `07_moodle-integration.md` | Moodle: Plugin vs. LTI vs. iframe vs. H5P — Entscheidung | 8 |
| 08 | `08_online-lernsystem.md` | Funktionen, Spaced Repetition, Notizen, Annotationen, Rollen, UI/UX | 9, 12 |
| 09 | `09_deployment.md` | Container, Docker Compose, Traefik, OIDC/Authentik, Backup/Update | 16 |
| 10 | `10_review-sicherheit-und-governance.md` | Review-Workflow, Warnlevel, medizinische Sicherheit, Dosierungspolitik | 14, 17 |
| 11 | `11_import-audit-pipeline.md` | Einlese-/Audit-/Normalisierungs-Pipeline für spätere Uploads | 1, 4 |
| 12 | `12_akzeptanzkriterien-und-roadmap.md` | Akzeptanzkriterien (20 Punkte), Release-Roadmap, Backlog | 18 |

**Begleitende, maschinenlesbare Artefakte** (Teil des Konzepts, bereits angelegt):

- `cards/PH/scope/*.yaml` — Konfiguration für Kategorien, Wirkstoffgruppen, Tags, Warnlevel,
  Review-Status, Kartentypen, Toxidrome, Antidote. **Hier kommen Kategorien aus Konfiguration, nicht
  aus Layout-Code** (Handover-Vorgabe Phase 2/13).
- `cards/PH/examples/*.yaml` — Vollständig ausmodellierte Beispielkarten nach erweitertem Schema
  (konservativ, mit Review-Status, ohne finale Dosierungsbehauptungen).
- `docs/pharma-cards/reports/` — `content_scope.md`, `missing_cards.md`, `content_review.md`
  (Handover-Vorgabe Phase 4/14).

---

## 4. Mapping: Handover-Struktur → bestehendes Repository

Die vom Handover vorgeschlagene `pharma-cards/`-Struktur wird wie folgt auf das bestehende Repo abgebildet:

| Handover-Vorschlag | Ziel im Repo | Hinweis |
|---|---|---|
| `pharma-cards/docs/` | `docs/pharma-cards/` | dieses Dossier |
| `pharma-cards/data/*.yaml` | `cards/PH/scope/*.yaml` + `cards/registry/` | Scope-Konfig + bestehende Registry |
| `pharma-cards/input/` | `imports/{csv,yaml,source-material}` + `imports/pharma/` (neu, bei Upload) | bestehende Import-Struktur |
| `pharma-cards/templates/` | `card-system/templates/` + `card-system/card-types/` | bestehende Template-Ablage |
| `pharma-cards/assets/` | `brand/` + `cards/PH/assets/` (bei Bedarf) | gemeinsame Marke + modul­spezifisch |
| `pharma-cards/generated/` | `exports/{web,pdf,...}` + `cards/PH/{front,back,print}` | bestehende Export-Ablage |
| `pharma-cards/app/{backend,frontend}` | `online-platform/{backend,frontend,database}` | bestehende Plattform-Ablage |
| `pharma-cards/scripts/` | `scripts/` | bestehende Skripte erweitern, nicht duplizieren |
| `pharma-cards/reports/` | `docs/pharma-cards/reports/` | modul­scoped, hält das Repo-Root sauber |
| `pharma-cards/dist/` | `exports/publisher/` / Release-Artefakte (CI) | Distribution über CI |

---

## 5. Abgrenzung dieses Arbeitsstandes

**Dieser Branch liefert das Konzept und das Setup, nicht die fertige Produktion.** Konkret erbracht:

- vollständiges, umsetzungsreifes Konzept über alle 18 Phasen;
- erweitertes, data-first Datenmodell für PH (Pharmakologie **und** Toxikologie/Antidote);
- kuratierte, priorisierte Startliste mit Release-Wellen und ID-Vergabeplan;
- maschinenlesbare Scope-Konfiguration (Kategorien/Tags/Warnlevel/Review-Status aus Konfig);
- begründete Architektur- und Integrationsentscheidungen (Online-System + Moodle);
- Import-/Audit-Pipeline-Konzept für spätere Uploads;
- Beispielkarten und Qualitäts-/Sicherheits-Governance.

**Bewusst noch nicht erbracht** (Folgephasen, nach Konzeptfreigabe durch Andreas):

- massenhafte inhaltliche Kartenproduktion (nur Beispielanker);
- lauffähiger Backend-/Frontend-Code der Online-App (Architektur + Datenmodell + Schnittstellen sind spezifiziert);
- finale, fachlich freigegebene medizinische Inhalte (alle Beispielinhalte stehen auf `needs_review`/`*_review_needed`).

---

## 6. Wichtige Leitplanken (gelten für alle Folgearbeiten)

- Keine spontanen Layoutwechsel zwischen Karten. Ein Layoutstandard, aus Konfiguration gesteuert.
- Keine Sammelbilder als Einzelkarten. Jede Vorder- und jede Rückseite ist eine eigene Datei.
- Keine unkontrollierte Erweiterung der Stoffliste. Neue Karten laufen über die Scope-Konfig + Review.
- Keine endgültigen medizinischen Behauptungen ohne Prüfung. Dosierungen nur mit Review-Status + Quelle.
- Bei Unsicherheit `clinical_review_needed` oder `toxicology_review_needed` setzen.
- Datenmodell zuerst, Karten daraus generieren. Reproduzierbarkeit ist Pflicht.
- Das Online-System ist **keine** Bildergalerie — es arbeitet auf den strukturierten Kartendaten.

---

## 7. Verantwortung (medizinische Inhalte)

Pharma Cards ist **Ausbildungs- und Lernmaterial**, keine verbindliche Therapieanweisung. Die
klinische/toxikologische Freigabe von Inhalten ist ein verpflichtender, dokumentierter Workflow
(siehe `10_review-sicherheit-und-governance.md`). Verantwortlich für fachliche Freigabe: AT Medical GmbH.
