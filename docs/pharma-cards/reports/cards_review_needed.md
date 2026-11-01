# Report — Karten mit offenem Review (PH / Pharma Cards)

> Automatisch erzeugt durch `scripts/pharma/review_report.py` (`make ph-review-report`).
> Nicht von Hand bearbeiten; Änderungen in den Kartendaten vornehmen.

## Übersicht

- Karten gesamt: **110**
- davon offen (nicht `approved`): **110**
- nach Review-Status: `clinical_review_needed` 57, `needs_review` 30, `toxicology_review_needed` 23
- offene nach Warnlevel: `critical` 24, `high` 43, `moderate` 24, `low` 19

Prüfablauf und Checklisten: `docs/pharma-cards/review/`.

## Toxikologische Prüfung nötig (`reviewer_tox`) — 23

| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |
|---|---|---|---|---|
| `ph_087` | Betablocker-Intoxikation | toxidrome | critical | • Stufentherapie und Stellenwert der Insulin-Euglykämie-Therapie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_088` | Calciumkanalblocker-Intoxikation | toxidrome | critical | • Beobachtungsdauer bei Retardpräparaten nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_089` | Digitalisintoxikation | toxidrome | critical | • Indikationskriterien für Digoxin-Fab mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
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

## Klinisch-pharmakologische Prüfung nötig (`reviewer_pharm`) — 57

| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |
|---|---|---|---|---|
| `ph_040` | Adrenalin | substance | critical | • Indikationsspezifische Applikationswege gegen aktuelle ERC-/Anaphylaxie-Leitlinie prüfen<br>• Verwechslungsgefahr der Konzentrationen eindeutig formulieren<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_041` | Noradrenalin | substance | critical | • Aktuelle Empfehlung zur peripheren vs. zentralen Gabe prüfen<br>• Stellenwert im septischen Schock gegen aktuelle Sepsis-Leitlinie abgleichen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_062` | Dobutamin | substance | critical | • Stellenwert im kardiogenen Schock gegen aktuelle Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_064` | Vasopressin | substance | critical | • Stellenwert gegen aktuelle Sepsis-Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_146` | Heparin (unfraktioniert) | substance | critical | • HIT-Diagnostik und Monitoringwerte nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_147` | Niedermolekulare Heparine | substance | critical | • Anpassung bei Niereninsuffizienz nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_148` | Direkte orale Antikoagulanzien (DOAK) | substance | critical | • Antidot-Zulassungsstand (Andexanet) prüfen<br>• Nierenfunktionsgrenzen je Substanz nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_149` | Phenprocoumon | substance | critical | • INR-Zielbereiche nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_219` | Maligne Hyperthermie | overview | critical | • Notfallablauf gegen aktuelle MH-Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_220` | Arzneimittel-Anaphylaxie | overview | critical | • Ablauf gegen aktuelle Anaphylaxie-Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_042` | Amiodaron | substance | high | • Position im aktuellen Reanimationsalgorithmus prüfen<br>• Interaktionsliste auf Vollständigkeit/Relevanz prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_043` | Adenosin | substance | high | • Kontraindikation Asthma: absolute vs. relative Einstufung nach aktueller Fachinformation prüfen<br>• Vorgehen bei Präexzitation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_044` | Nitroglycerin (Glyceroltrinitrat) | substance | high | • Zeitfenster der PDE-5-Hemmer-Kontraindikation je Substanz nach Fachinformation prüfen<br>• Blutdruckgrenzen nicht ohne Quelle angeben<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_046` | Midazolam | substance | high | • Applikationswege beim Status epilepticus (z. B. bukkal/intranasal/i.m.) gegen aktuelle Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_047` | Ketamin | substance | high | • Aussage zum Hirndruck nach aktuellem Stand prüfen (frühere KI gilt als relativiert)<br>• Potenzverhältnis Ketamin/Esketamin mit Quelle belegen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_050` | Propofol | substance | high | • Allergie-Aussage (Ei/Soja) nach aktueller Fachinformation prüfen<br>• Risikofaktoren des Infusionssyndroms mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_051` | Etomidat | substance | high | • Stellenwert bei Sepsis nach aktueller Evidenz prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_052` | Sevofluran | substance | high | • MH-Kontraindikation und Monitoring nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_053` | Fentanyl | substance | high | • Pflaster-Indikation und -Kontraindikationen nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_054` | Sufentanil | substance | high | • Potenzverhältnis zu Fentanyl nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_055` | Remifentanil | substance | high | • Kontraindikation epidural/intrathekal nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_056` | Rocuronium | substance | high | • Einsatz zur RSI gegen aktuelle Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_057` | Succinylcholin (Suxamethonium) | substance | high | • Zeitfenster der Hyperkaliämie-Kontraindikation (Verbrennung, Immobilisation) nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_058` | Cisatracurium | substance | high | • Aussage zur Histaminfreisetzung mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_059` | Sugammadex | substance | high | • Hinweis zur hormonellen Kontrazeption nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_060` | Neostigmin | substance | high | • Indikationsgrenzen (Blockadetiefe) nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_061` | Dexmedetomidin | substance | high | • Zulassungsumfang (Sedierungstiefe) nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_063` | Levosimendan | substance | high | • Indikation und Kontraindikationen nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_133` | Metamizol | substance | high | • Indikationsformulierung und Monitoring gegen aktuelle Fachinformation/Rote-Hand-Briefe prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_134` | Acetylsalicylsäure (ASS) | substance | high | • Reye-Syndrom-Altersgrenze und Schwangerschaftshinweis nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_135` | Morphin | substance | high | • Anwendung bei Niereninsuffizienz mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_136` | Oxycodon | substance | high | • Aussage zur Naloxon-Fixkombination mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_137` | Tramadol | substance | high | • Krampfschwelle und CYP2D6-Aussagen mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_138` | Buprenorphin | substance | high | • Aussage zur Naloxon-Antagonisierbarkeit mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_140` | Betablocker | substance | high | • Asthma-Kontraindikation (kardioselektiv vs. nichtselektiv) nach Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_145` | Digoxin | substance | high | • Stellenwert bei Herzinsuffizienz nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_150` | Clopidogrel | substance | high | • PPI-Interaktion (Omeprazol vs. Pantoprazol) nach aktuellem Stand prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_151` | Ticagrelor | substance | high | • Hinweis zur ASS-Begleitdosis nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_210` | QT-Zeit-Verlängerung | interaction | high | • Beispielsubstanzen gegen aktuelle Referenzliste (z. B. CredibleMeds) prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_212` | CYP-Inhibition | interaction | high | • Beispiel Statin-Interaktion (betroffene Statine) prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_213` | Serotonerge Interaktionen | interaction | high | • Auswaschzeiten nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_214` | Blutungsrisiko unter Antikoagulanzien | interaction | high | • Empfehlung zum Magenschutz nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_215` | Nephrotoxische Kombinationen | interaction | high | • Sick-Day-Rules nach aktueller Empfehlung formulieren<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_217` | Hyperkaliämie-Risiko | interaction | high | • Notfalltherapie der Hyperkaliämie nach aktueller Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_045` | Furosemid | substance | moderate | • Stellenwert beim akuten Lungenödem gegen aktuelle Herzinsuffizienz-Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_048` | Glucose | substance | moderate | • Reihenfolge Thiamin/Glucose nach aktuellem Stand formulieren<br>• Konzentrationsangaben nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_049` | Magnesium (Magnesiumsulfat) | substance | moderate | • Indikation Eklampsie gegen aktuelle geburtshilfliche Leitlinie prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_130` | Paracetamol | substance | moderate | • Tageshöchstdosen und Risikogruppen nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_131` | Ibuprofen | substance | moderate | • ASS-Interaktion nach aktuellem Stand formulieren<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_132` | Diclofenac | substance | moderate | • Kardiovaskuläre Kontraindikationen nach aktueller Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_141` | ACE-Hemmer | substance | moderate | • Kontraindikationen nach aktueller Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_142` | AT1-Blocker (Sartane) | substance | moderate | • Kombinationsverbote (ACE-Hemmer, Aliskiren) nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_143` | Calciumkanalblocker | substance | moderate | • Kontraindikationen je Substanzgruppe nach Fachinformation prüfen<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_144` | Thiaziddiuretika | substance | moderate | • Wirkverlust bei Niereninsuffizienz (Grenze) nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_211` | CYP-Induktion | interaction | moderate | • Zeitverlauf der Induktion mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_216` | Hepatotoxische Kombinationen | interaction | moderate | • Beispielsubstanzen mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |
| `ph_218` | Hyponatriämie-Risiko | interaction | moderate | • Korrekturgrenzen nur mit Quelle<br>• Aktuelle Quelle (Leitlinie/Fachinformation) mit Jahr in references eintragen |

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
