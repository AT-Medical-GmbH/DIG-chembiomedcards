# 14 — Inhaltliche Qualitätssicherung

Leitplanke: **Keine endgültigen fachlichen Behauptungen ohne Prüfung. Bei Unsicherheit
`review_needed` setzen — nicht raten.**

## 1. Prüfkriterien je Karte

- korrekter Name & korrekte Schreibweise,
- fachlich plausible Aussage, korrekte Stoffklasse,
- korrekte biochemische / klinische / (ggf.) molekularbiologische Relevanz,
- keine veralteten/missverständlichen Aussagen,
- keine unnötigen Dubletten, keine überlangen Rückseiten,
- konsistente Begriffe, passende Kategorie, passende Tags.

Automatisierbare Teile laufen als **Lints** im Build (Kap. 06 §7): Namen gegen `substances.yaml`,
Tags gegen `tags.yaml`, Kategorie gültig, Rückseitenlänge/Overflow, AS-Vorderseite ohne Name,
Kontrast. Fachliche Korrektheit bleibt **menschlicher Review**.

## 2. Vollständigkeitsprüfung (Soll-Listen)

`audit_cards`/`validate_output` prüfen die vorhandenen Karten gegen definierte Soll-Gruppen und
listen Fehlendes in `reports/missing_cards.md`. Soll-Gruppen (aus dem Handover):

- **Proteinogene Aminosäuren** (20): Gly, Ala, Val, Leu, Ile, Ser, Thr, Cys, Met, Pro, Phe, Tyr,
  Trp, His, Lys, Arg, Asp, Glu, Asn, Gln.
- **Derivate/Spezialfälle**: Kreatin, Kreatinin, Homocystein, Taurin, β-Alanin, Hydroxyprolin,
  Hydroxylysin, Selenocystein, Selenomethionin, Ornithin, Citrullin, Argininosuccinat,
  N-Acetylglutamat, N-Acetylaspartat.
- **Neurotransmitter/biogene Amine**: Dopamin, Adrenalin, Noradrenalin, Serotonin, Melatonin,
  Histamin, Acetylcholin, GABA, Glutamat, 5-HTP, L-DOPA.
- **Hormone/Signalstoffe**: Insulin, Glukagon, GLP-1, GIP, Ghrelin, Leptin, Adiponektin, Cortisol,
  Aldosteron, Calcitriol, T3, T4, Testosteron, Östradiol, Progesteron.
- **Stoffwechsel**: Glucose, G6P, F6P, Pyruvat, Laktat, Acetyl-CoA, CoA, Citrat, Oxalacetat,
  α-Ketoglutarat, Succinyl-CoA, Succinat, Fumarat, Malat.
- **Stickstoffstoffwechsel**: Ammoniak/Ammonium, Carbamoylphosphat, Ornithin, Citrullin,
  Argininosuccinat, Arginin, Harnstoff, Orotat.
- **Lipide/Eicosanoide**: Ölsäure, Linolsäure, Arachidonsäure, Triacylglycerid, DAG, PGE2, TXA2,
  LTB4, β-Hydroxybutyrat, Malonyl-CoA, HMG-CoA, Mevalonat.
- **Nukleotide/Coenzyme/Second Messenger**: ATP, cAMP, cGMP, GTP, IP3, NAD⁺, NADH, FAD, CoQ10,
  Ubichinol, SAM, Calcium/Ca²⁺, NO.
- **Vitamine**: A, B1, B2, B3, B5, B6, B7, B9, B12, C, D, E, K + „Vitamin S/Schokolade“
  (humorvolle Sonderkarte).

Die maschinenlesbare Form dieser Listen liegt in `data/substances.yaml` (mit Synonymen), damit
die Prüfung reproduzierbar ist. **Fehlende Karten werden nur ergänzt, wenn sie didaktisch ins
Zielsystem passen** — sonst als „nicht erforderlich, begründet“ dokumentiert.

## 3. Review-Workflow (Status-Automat)

```
draft → needs_review → reviewed → approved → (deprecated) → (archived)
```
- Übergänge nur durch berechtigte Rollen (Reviewer/Editor/Admin, Kap. 09 §7).
- Jede inhaltliche Änderung → `card_versions`-Snapshot + `version`-Erhöhung.
- Nur `approved` ist „live“ für Lernende/Print/Moodle.
- Ereignisse werden (optional) in `review_events` protokolliert.

## 4. Umgang mit Unsicherheit

Bei fachlicher Unsicherheit: **nicht raten** → `review_status: needs_review`, **knappe
Begründung** im Feld/Report, **Korrekturvorschlag** notieren. Das gilt auch für unsichere
Importe (Kap. 04 §8).

## 5. Berichte

| Datei | Inhalt |
|-------|--------|
| `reports/content_review.md` | fachliche Prüfung je Karte, Auffälligkeiten |
| `reports/cards_review_needed.md` | alle `needs_review`-Karten mit Begründung & Vorschlag |
| `reports/final_quality_report.md` | Gesamtbild: Abdeckung, Review-Stand, offene Punkte |
| `reports/missing_cards.md` | fehlende Soll-Karten + Begründungen |
| `reports/duplicate_cards.md` | Dubletten-Entscheidungen |
| `reports/layout_review.md` | Layout-/Lesbarkeitsbefunde |

## 6. Medizinische Sorgfalt

Klinische Aussagen (Box „Klinik“, rot) sind besonders sensibel. Sie müssen von einem
Fachreviewer freigegeben sein (`approved` + `reviewer` gesetzt), bevor sie live gehen. Das
Konzept trifft **keine** eigenständigen medizinischen Festlegungen; es stellt den Prozess bereit,
in dem Fachpersonal sie verantwortet.
