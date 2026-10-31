# PH Beispielkarten

> **Hinweis:** Die ursprünglichen Beispiel-YAML (`ph_006_agonist.yaml`, `ph_020_naloxon.yaml`)
> sind in den produktiven Bestand übergegangen. Produktive Karten liegen jetzt in
> `cards/PH/metadata/` und werden durch die Pipeline (`scripts/pharma/`) validiert, in die Registry
> übernommen und gerendert.

Die erste produktive Tranche (Release R1) umfasst die Blöcke **Allgemeine Pharmakologie**
(`ph_001`–`ph_019`) und **Pharmakokinetik/Pharmakodynamik-Mechanismen** (`ph_020`–`ph_030`) als
`needs_review`, ohne finale Dosierungen.

Die klinisch kritischen Blöcke (**Notfallmedikamente `ph_040`–`ph_049`, Toxidrome `ph_080`–`ph_086`,
Antidote `ph_100`–`ph_112`**) liegen als Entwürfe vor. Sie werden erst nach dem Fachreview-Workflow
(`docs/pharma-cards/review/`) als `approved` ausgespielt. Die frühere Beispielkarte Naloxon ist jetzt
`ph_100`.

Als Schema-Referenz dient `docs/pharma-cards/02_datenmodell.md` sowie jede Datei in
`cards/PH/metadata/`.
