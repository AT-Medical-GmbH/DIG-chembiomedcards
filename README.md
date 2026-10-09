# DIG-chembiomedcards

DIG-chembiomedcards ist die strukturierte Projektbasis für **ChemBioMed Cards** – ein skalierbares Lernkarten-Referenzsystem der AT Medical GmbH für Druck und Online-Nutzung.

## Projektziele

- **Druckziel:** DIN A6 quer, hochwertige Front-/Back-Karten, stabile QR-Links, modulare Kartenpakete.
- **Onlineziel:** responsive Lernkartenplattform (Tablet-first) mit Lernstatus, eigenen Kartensammlungen, Notizen, Medien und Lizenzlogik.

## Hauptbereiche

- **AC** – Allgemeine und anorganische Chemie
- **OC** – Organische Chemie
- **BC** – Biochemie
- **MB** – Molekularbiologie der Zelle
- **APC** – Angewandte Chemie, Ernährung & Medizin
- **PH** – Pharmakologie (strukturell vorbereitet, inhaltlich später ausgebaut)

## Gesamtkonzept

Das vollständige, verbindliche Umsetzungskonzept über alle drei Projektebenen (Content, Export,
Online-Lernsystem) liegt in **[`docs/concept/`](docs/concept/README.md)**. Einstieg:

- [Executive Summary](docs/concept/00-executive-summary.md) – Zielbild & Kernentscheidungen
- [Systemarchitektur](docs/concept/01-system-architecture.md)
- [Content-Modell](docs/concept/02-content-model.md) & [Import-/Audit-Pipeline](docs/concept/04-import-audit-pipeline.md)
- [Online-Lernsystem](docs/concept/09-online-learning-system.md) & [Online-Architektur](docs/concept/10-online-architecture.md)
- [Decision Log](docs/concept/decision-log.md) & [Offene Fragen](docs/concept/open-questions.md)

## Projektstatus

**Konzeptphase – abgeschlossen und freigabebereit.**

Das Gesamtkonzept (`docs/concept/`) ist ausgearbeitet. Die vorhandenen Karten werden laut Handover
separat hochgeladen; die Import-/Audit-Pipeline ist so entworfen, dass sie danach automatisiert
greift. Layoutstandards, Kartenmetadaten, Registry-Prozesse sowie Print-/Online-Schnittstellen
sind konzeptionell festgelegt.
