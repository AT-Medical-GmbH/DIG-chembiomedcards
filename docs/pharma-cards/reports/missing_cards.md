# Report — Missing Cards (PH / Pharma Cards)

**Stand:** 2026-10-31 (R1 + R2) · **Bedeutung:** Geplante Karten, die noch fehlen, und Karten, die zwar angelegt,
aber noch nicht freigegeben sind.

## Release R1 — als Entwurf vollständig angelegt

| Block | IDs | Anzahl | Status |
|---|---|---:|---|
| Allgemeine Pharmakologie | `ph_001`–`ph_019` | 19 | `needs_review` |
| PK/PD-Mechanismen | `ph_020`–`ph_030` | 11 | `needs_review` |
| Notfallmedikamente (Wirkstoffkarten) | `ph_040`–`ph_049` | 10 | `clinical_review_needed` |
| Toxidrome | `ph_080`–`ph_086` | 7 | `toxicology_review_needed` |
| Antidote | `ph_100`–`ph_112` | 13 | `toxicology_review_needed` |
| **Summe R1** | | **60** | **0 freigegeben** |

Die Notfallmedikamente Naloxon, Flumazenil, Atropin, Glucagon, Calcium und Natriumbicarbonat sind
nicht doppelt angelegt. Es gibt sie nur als Antidotkarte; über die Nebenkategorie
`notfallmedikamente` erscheinen sie auch im Notfallset.

**Was in R1 fehlt, ist die Freigabe, nicht der Inhalt.** Offene Prüfungen mit Schwerpunkten:
`cards_review_needed.md`.

## Release R2 — als Entwurf angelegt (50 Karten)

| Block | IDs | Anzahl | Status |
|---|---|---:|---|
| Anästhesie / Intensiv | `ph_050`–`ph_064` | 15 | `clinical_review_needed` |
| Analgetika | `ph_130`–`ph_138` | 9 | `clinical_review_needed` |
| Herz-Kreislauf | `ph_140`–`ph_151` | 12 | `clinical_review_needed` |
| Intoxikationen (Betablocker, Calciumkanalblocker, Digitalis) | `ph_087`–`ph_089` | 3 | `toxicology_review_needed` |
| Interaktionen / Arzneimittelsicherheit | `ph_210`–`ph_220` | 11 | `clinical_review_needed` |

Aus der Startliste noch offen (bewusst nicht im ersten R2-Schnitt): Esketamin (als Hinweis auf der
Ketamin-Karte), Vecuronium, Desfluran, Isofluran, Clonidin. Wirkstoffe, die mehreren Blöcken
angehören (Noradrenalin, ASS, Naloxon), gibt es nur einmal; die Mehrfachzuordnung läuft über
Nebenkategorien.

## Release R3 / R4 — fehlt noch

Siehe `../04_startliste-kuratiert.md` §4–§5.
