# PH Beispielkarten

> **Hinweis:** Die ursprünglichen Beispiel-YAML (`ph_006_agonist.yaml`, `ph_020_naloxon.yaml`)
> sind in den produktiven Bestand übergegangen. Produktive Karten liegen jetzt in
> `cards/PH/metadata/` und werden durch die Pipeline (`scripts/pharma/`) validiert, in die Registry
> übernommen und gerendert.

Die erste produktive Tranche (Release R1) umfasst die Blöcke **Allgemeine Pharmakologie**
(`ph_001`–`ph_019`) und **Pharmakokinetik/Pharmakodynamik-Mechanismen** (`ph_020`–`ph_030`) als
`needs_review`, ohne finale Dosierungen.

Die klinisch kritischen Blöcke (**Notfallmedikamente, Toxidrome, Antidote**) werden bewusst erst nach
dem Fachreview-Workflow (siehe `docs/pharma-cards/10_review-sicherheit-und-governance.md`) als
`approved` ausgespielt. Die Antidot-Karte **Naloxon** (Warnlevel `critical`,
`toxicology_review_needed`) wird mit diesem Block im Antidot-ID-Bereich (`ph_1xx`) angelegt.

Als Schema-Referenz dient `docs/pharma-cards/02_datenmodell.md` sowie jede Datei in
`cards/PH/metadata/`.
