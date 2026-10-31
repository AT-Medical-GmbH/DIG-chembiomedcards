# 16 — Phasenplan, Meilensteine & Akzeptanzkriterien

## 0. Aktueller Stand (2026-10-31)

Wegen der korrigierten Ausgangslage (nur Muster + Planungsliste, ADR-014) wurde die Reihenfolge
angepasst: **Produktion aus Daten startet sofort**, der Import entfällt weitgehend.

| Schritt | Stand |
|---|---|
| Konzept (Phase 1) | ✅ abgeschlossen |
| Template (Vorder-/Rückseite), Design-Tokens, Kategorien/Tags, Kartenschema | ✅ umgesetzt (`templates/`, `data/`) |
| Generator + Validierung + Berichte (`make build`) | ✅ umgesetzt (`scripts/`) |
| **Pilotserie: 20 proteinogene Aminosäuren** (`bc_098`–`bc_117`) | ✅ gerendert · ⏳ **Fachreview offen** (`reports/cards_review_needed.md`) |
| Abgleich mit den Musterkarten | ⏳ wartet auf Upload der Muster |
| Serienproduktion Handover-Soll-Liste (~170 Karten), danach Masterverzeichnis (1.452) | ⏳ nach Pilot-Freigabe |
| Print-/Moodle-Pakete, Online-MVP | ⏳ wie unten geplant |

## 1. Phasenplan (umsetzungsreihenfolge)

| Phase | Inhalt | Ergebnis / Gate |
|------:|--------|-----------------|
| **1 ✅** | Analyse, Architektur, Struktur, Datenmodell, Import-/Audit-Plan, Entscheidungen | **dieses Konzept** |
| **2** | *(nach Upload)* Import & Audit der vorhandenen Karten | Inventar + `reports/*` |
| **3** | Normalisierung → kanonisches `cards_master.json` | validierte Datenebene |
| **4** | Vollständigkeits-/Qualitätsprüfung gegen Soll-Listen | `missing_cards.md`, `content_review.md` |
| **5** | Einheitliche Neugenerierung aller Karten (Kap. 06) | `generated/individual/**` |
| **6** | Print-Export + Druckpakete (Kap. 07) | `dist/print/*.zip` |
| **7** | Moodle-Importpakete (Kap. 08) | `dist/moodle/*.zip` |
| **8** | Online-MVP (Backend + Frontend, Lernmodus, SRS, Notizen) | lauffähige App (Staging) |
| **9** | Annotationen, Exportcenter, Admin-/Review-UI | Feature-Vollausbau |
| **10** | Moodle LTI 1.3, OIDC/Authentik, WooCommerce-Lizenz | Integrationen live |
| **11** | Deployment ATMED-core → später dediziert | produktiver Betrieb |

Diese Reihenfolge respektiert „Datenmodell zuerst, Bilder daraus generieren“ und entkoppelt die
Print-/Moodle-Linie (Phasen 5–7) vom Online-System (Phasen 8–10), sodass beide unabhängig
Fortschritt zeigen können. Sie ist kompatibel zur bestehenden `docs/roadmap.md` (Phasen 0–8).

## 2. Definition of Done je Artefaktklasse

- **Karte (Daten):** Schema-valide, Kategorie/Tags gültig, `review_status` gesetzt, versioniert.
- **Karte (Bild):** Front+Back generiert, kein Overflow, Kontrast AA, Tabs korrekt, kein Rand.
- **Druckpaket:** Bogen-PDF duplexpassend + Einzel-PDFs + PNGs + `README_PRINT.md`.
- **Moodle-Paket:** Importvarianten + `images/` + `README_IMPORT.md`, auf Testinstanz importiert.
- **Online-Feature:** Tests grün, barrierearm, in Staging verifiziert.

## 3. Akzeptanzkriterien (die 20 aus dem Handover)

Das Projekt gilt als abgeschlossen, wenn:

1. alle hochgeladenen vorhandenen Karten erfasst wurden — *Pipeline Kap. 04, `final_inventory.md`*;
2. falsche Sammelbilder ausgeschlossen wurden — *Audit Kap. 04 §3.2, `rejected_files.md`*;
3. alle Karten ein einheitliches Layout besitzen — *Generierung Kap. 05/06*;
4. die Tabs am oberen Rand konsistent umgesetzt sind — *Kap. 03/05, erzwungen durch Template*;
5. Vorder- und Rückseiten korrekt gepaart sind — *Kap. 04 §3.1*;
6. fehlende Karten ergänzt **oder** begründet als nicht erforderlich dokumentiert sind — *Kap. 14 §2*;
7. alle Karten inhaltlich geprüft wurden — *Review-Workflow Kap. 14*;
8. alle Karten optisch geprüft wurden — *`layout_review.md` Kap. 06 §7*;
9. Moodle-Importpakete vorhanden sind — *Kap. 08, `dist/moodle/`*;
10. druckfertige PDFs vorhanden sind — *Kap. 07, `dist/print/`*;
11. Einzelkarten als PNG **und** PDF vorhanden sind — *Kap. 06 §3*;
12. ein Online-Lernsystem implementiert ist — *Kap. 09/10*;
13. Karten online angezeigt/gelernt/markiert/wiederholt werden können — *Kap. 09*;
14. Nutzer Notizen unter Karten speichern können — *Kap. 09 §3 / 11*;
15. Annotationen auf Karten vorbereitet/implementiert sind — *Kap. 09 §4 (Overlay/JSON)*;
16. einzelne Karten online als PNG/PDF heruntergeladen werden können — *Kap. 09 §5 / 10*;
17. Kategorien, Tags und Review-Status bearbeitbar sind — *Kap. 09 §6*;
18. das System auf weitere Fachgebiete erweiterbar ist — *Kap. 13*;
19. Deployment-Dokumentation vorhanden ist — *Kap. 15*;
20. Abschlussbericht vorhanden ist — *`dist/ChemBioMed_Cards_Final_Report.md/.pdf`*.

Dieses Konzept erfüllt Kriterium-Vorbedingungen (Design/Pläne) für **alle 20** und erfüllt die
planungsseitigen Kriterien vollständig; die inhalts-/codeseitige Erfüllung folgt in Phasen 2–11
nach dem Karten-Upload.

## 4. Distributions-Endstand (`dist/`)

```
dist/
  ChemBioMed_Cards_Moodle_*.zip      (6 Pakete)
  ChemBioMed_Cards_Print_*.zip       (6 Pakete)
  ChemBioMed_Cards_Online_App.zip
  ChemBioMed_Cards_Source_Project.zip
  ChemBioMed_Cards_Final_Report.md / .pdf
```

## 5. Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|--------|----------------|
| Upload enthält viele Sammelbilder | Audit lehnt automatisch ab, listet in `rejected_files.md` |
| Uneinheitliche Alt-Layouts | Neugenerierung aus Daten (nicht Alt-Bilder weiterverwenden) |
| Fachliche Fehler | Review-Gate; nur `approved` geht live |
| Moodle-Plugin-Format unklar | mehrere Importvarianten + LTI als strategischer Pfad |
| Scope-Ausweitung (Stoffliste) | Soll-Listen + didaktisches Erweiterungsgate (Kap. 13 §5) |
| Live-Betrieb-Eingriffe | Staging-first, Freigabe durch Andreas, Backups vor Änderung |
