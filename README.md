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

**Soll-Liste vollständig produziert – Fachreview offen.** 116 Karten (Handover-Soll-Liste) liegen als
Datensätze in `data/cards/` und werden aus **einer zentralen Vorlage** erzeugt
([`templates/card_template.html`](templates/card_template.html), Bedienung:
[`templates/README.md`](templates/README.md)). Vorschauen je Themengruppe unter
[`generated/preview/`](generated/preview/), offene Reviews in
[`reports/cards_review_needed.md`](reports/cards_review_needed.md).

Bisher existieren nur einige Musterkarten und die Planungsliste
(`cards/registry/MASTER_DIRECTORY.md`); die Karten werden deshalb direkt aus Daten produziert
(`data/cards/*.yaml` → `make build`). Startumfang: Handover-Soll-Liste (~170 Karten), danach das
Masterverzeichnis. Nächste Schritte und offene Punkte:
[Roadmap](docs/concept/16-roadmap-and-acceptance.md) · [Offene Fragen](docs/concept/open-questions.md).
