# Report — Karten mit offenem Review (PH / Pharma Cards)

> Automatisch erzeugt durch `scripts/pharma/review_report.py` (`make ph-review-report`).
> Nicht von Hand bearbeiten; Änderungen in den Kartendaten vornehmen.

## Übersicht

- Karten gesamt: **60**
- davon offen (nicht `approved`): **60**
- nach Review-Status: `clinical_review_needed` 10, `needs_review` 30, `toxicology_review_needed` 20
- offene nach Warnlevel: `critical` 13, `high` 14, `moderate` 14, `low` 19

Prüfablauf und Checklisten: `docs/pharma-cards/review/`.

## Toxikologische Prüfung nötig (`reviewer_tox`) — 20

| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |
|---|---|---|---|---|
| `ph_100` | Naloxon | antidote | critical | • Applikationswege (i.v./i.m./intranasal) nach aktueller Leitlinie prüfen<br>• Nachbeobachtung nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_101` | Flumazenil | antidote | critical | • Indikationsgrenzen nach aktueller toxikologischer Empfehlung prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_102` | N-Acetylcystein | antidote | critical | • Aktuelles Behandlungsschema und Nomogramm-Grenzen nur mit Quelle<br>• Vorgehen bei unbekanntem Einnahmezeitpunkt prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_103` | Atropin | antidote | critical | • Titrationsziel nach aktueller Empfehlung prüfen<br>• Bradykardie-Indikation gegen aktuellen Algorithmus abgleichen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_104` | Hydroxocobalamin | antidote | critical | • Verdachtskriterien (z. B. Laktat) nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_106` | Fomepizol | antidote | critical | • Dialyse-Indikationen nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_107` | Digoxin-spezifische Fab-Fragmente | antidote | critical | • Indikationskriterien nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_108` | Glucagon | antidote | critical | • Stellenwert gegenüber hochdosierter Insulin-Euglykämie-Therapie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_109` | Calcium | antidote | critical | • Aussage zu Calcium bei Digitalisintoxikation nach aktuellem Stand prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_110` | Natriumbicarbonat | antidote | critical | • Ziel-pH bzw. Steuerkriterien nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_111` | Lipidemulsion | antidote | critical | • Aktuelle LAST-Leitlinie (Anästhesie-Fachgesellschaft) als Quelle eintragen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_080` | Cholinerges Syndrom | toxidrome | high | • Stellenwert der Oxime nach aktuellem Stand prüfen<br>• Eigenschutz-Hinweise vollständig?<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_081` | Anticholinerges Syndrom | toxidrome | high | • Indikationsgrenzen für Physostigmin nach aktuellem Stand prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_082` | Sympathomimetisches Syndrom | toxidrome | high | • Aussage zu Betablockern bei Kokain-Intoxikation nach aktuellem Stand formulieren<br>• Temperaturgrenzen nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_083` | Opioid-Toxidrom | toxidrome | high | • Nachbeobachtungsdauer nach Naloxon nur mit Quelle angeben<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_084` | Sedativ-hypnotisches Toxidrom | toxidrome | high | • Abgrenzung Benzodiazepine vs. Barbiturate (Atemdepression) prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_085` | Serotonerges Syndrom | toxidrome | high | • Diagnosekriterien und Auslöserliste nach aktuellem Stand prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_086` | Malignes neuroleptisches Syndrom | toxidrome | high | • Stellenwert von Dantrolen/Bromocriptin prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_105` | Sauerstoff | antidote | high | • Indikationen für hyperbare Therapie nach aktuellem Stand prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_112` | Vitamin K (Phytomenadion) | antidote | high | • Kombination mit PPSB und Indikationsgrenzen nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |

## Klinisch-pharmakologische Prüfung nötig (`reviewer_pharm`) — 10

| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |
|---|---|---|---|---|
| `ph_040` | Adrenalin | substance | critical | • Indikationsspezifische Applikationswege gegen aktuelle ERC-/Anaphylaxie-Leitlinie prüfen<br>• Verwechslungsgefahr der Konzentrationen eindeutig formulieren<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_041` | Noradrenalin | substance | critical | • Aktuelle Empfehlung zur peripheren vs. zentralen Gabe prüfen<br>• Stellenwert im septischen Schock gegen aktuelle Sepsis-Leitlinie abgleichen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_042` | Amiodaron | substance | high | • Position im aktuellen Reanimationsalgorithmus prüfen<br>• Interaktionsliste auf Vollständigkeit/Relevanz prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_043` | Adenosin | substance | high | • Kontraindikation Asthma: absolute vs. relative Einstufung nach aktueller Fachinformation prüfen<br>• Vorgehen bei Präexzitation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_044` | Nitroglycerin (Glyceroltrinitrat) | substance | high | • Zeitfenster der PDE-5-Hemmer-Kontraindikation je Substanz nach Fachinformation prüfen<br>• Blutdruckgrenzen nicht ohne Quelle angeben<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_046` | Midazolam | substance | high | • Applikationswege beim Status epilepticus (z. B. bukkal/intranasal/i.m.) gegen aktuelle Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_047` | Ketamin | substance | high | • Aussage zum Hirndruck nach aktuellem Stand prüfen (frühere KI gilt als relativiert)<br>• Potenzverhältnis Ketamin/Esketamin mit Quelle belegen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_045` | Furosemid | substance | moderate | • Stellenwert beim akuten Lungenödem gegen aktuelle Herzinsuffizienz-Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_048` | Glucose | substance | moderate | • Reihenfolge Thiamin/Glucose nach aktuellem Stand formulieren<br>• Konzentrationsangaben nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_049` | Magnesium (Magnesiumsulfat) | substance | moderate | • Indikation Eklampsie gegen aktuelle geburtshilfliche Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |

## Allgemeines Fachreview nötig (`reviewer_pharm`) — 30

| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |
|---|---|---|---|---|
| `ph_012` | Therapeutische Breite | overview | moderate | – |
| `ph_017` | Clearance | overview | moderate | – |
| `ph_019` | Loading Dose / Erhaltungsdosis | overview | moderate | – |
| `ph_021` | CYP450-System | overview | moderate | – |
| `ph_022` | CYP3A4 | overview | moderate | – |
| `ph_023` | CYP2D6 | overview | moderate | – |
| `ph_024` | CYP2C9 | overview | moderate | – |
| `ph_025` | P-Glykoprotein | overview | moderate | – |
| `ph_026` | Renale Elimination | overview | moderate | – |
| `ph_027` | Hepatische Metabolisierung | overview | moderate | – |
| `ph_028` | Proteinbindung | overview | moderate | – |
| `ph_001` | Allgemeine Pharmakologie | overview | low | – |
| `ph_002` | Pharmakokinetik – Überblick | overview | low | – |
| `ph_003` | Pharmakodynamik – Überblick | overview | low | – |
| `ph_004` | Rezeptorbindung | overview | low | – |
| `ph_005` | Dosis-Wirkungs-Kurve | overview | low | – |
| `ph_006` | Agonist | overview | low | – |
| `ph_007` | Antagonist | overview | low | – |
| `ph_008` | Partialagonist | overview | low | – |
| `ph_009` | Inverser Agonist | overview | low | – |
| `ph_010` | Kompetitive Hemmung | overview | low | – |
| `ph_011` | Nichtkompetitive Hemmung | overview | low | – |
| `ph_013` | Bioverfügbarkeit | overview | low | – |
| `ph_014` | First-Pass-Effekt | overview | low | – |
| `ph_015` | Verteilungsvolumen | overview | low | – |
| `ph_016` | Halbwertszeit | overview | low | – |
| `ph_018` | Steady State | overview | low | – |
| `ph_020` | LADME-Prinzip | overview | low | – |
| `ph_029` | Aktive Metaboliten | overview | low | – |
| `ph_030` | Prodrugs | overview | low | – |
