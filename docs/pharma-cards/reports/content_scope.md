# Report — Content Scope (PH / Pharma Cards)

**Stand:** 2026-10-09 · **Quelle:** `cards/PH/scope/categories.yaml`, `04_startliste-kuratiert.md`

## Abdeckung je Release-Welle

| Welle | Kategorien | Kartenzahl (Richtwert) | Status |
|---|---|---:|---|
| R1 — Pilot | Allgemeine Pharmakologie, PK/PD, Notfallmedikamente (Kern), Toxidrome (Kern), Antidote (Top) | ~60 | geplant |
| R2 — Aufbau | Anästhesie/Intensiv, Analgetika, Herz-Kreislauf, Interaktionen, Arzneimittelsicherheit | ~80 | geplant |
| R3 — Breite | Antibiotika/Antiinfektiva, Psychopharmaka/Neurologie, Endokrinologie, Rest-Toxikologie, Präklinik, Drogen/Intox | ~70 | geplant |
| R4 — Spezial | Onkologie, Pädiatrie, Geriatrie, Schwangerschaft/Stillzeit, Niere/Leber, CBRN | später | zurückgestellt |

Gesamt R1–R3 ≈ 210 Karten (PH-Zielraum: 242). R4 über 242 hinaus zulässig (ID-Raum `ph_###` bis 999).

## Abdeckung je Hauptkategorie (Soll)

Alle 15 Hauptkategorien aus `categories.yaml` sind im Scope; `future_categories` (19) sind als
Erweiterung vorgemerkt. Kategorien/Vokabulare stammen aus Konfiguration, nicht aus Code.

## Kartentypen im Scope
Wirkstoff · Wirkmechanismus · Toxidrom · Antidot · Interaktion · Fall · Übersicht/Prinzip
(`card_types.yaml`).

## Produktionsstand (2026-10-31)
R1 ist mit 60 Karten vollständig als Entwurf angelegt (`cards/PH/metadata/`). Freigegeben ist noch
keine Karte. 30 Grundlagen-/PK-PD-Karten warten auf allgemeines Fachreview, 30 klinische Karten auf
pharmakologische bzw. toxikologische Prüfung. Details: `missing_cards.md`, `cards_review_needed.md`.
