# PH Beispielkarten

Vollständig ausmodellierte Beispielkarten nach dem erweiterten PH-Content-Schema
(`docs/pharma-cards/02_datenmodell.md`). Sie demonstrieren das **data-first**-Prinzip: Karten werden
aus strukturierten Daten erzeugt, nicht als Bilder gepflegt.

| Datei | Typ | Zweck |
|---|---|---|
| `ph_006_agonist.yaml` | overview/principle | Didaktische Prinzipkarte (low risk), Status `needs_review` |
| `ph_020_naloxon.yaml` | antidote | Hochrisiko-/Antidotkarte (critical), Status `toxicology_review_needed` |

**Wichtig:** Dies sind **Beispiele**, kein freigegebener medizinischer Inhalt. Beide stehen bewusst auf
einem Review-Status < `approved` und enthalten **keine finalen Dosierungsangaben**. Vor einer
Produktion/Freigabe müssen sie den Fachreview-Workflow (Dok. 10) durchlaufen.

Beim Start der Produktion (Roadmap P2) werden Karten als `cards/PH/metadata/ph_###_<slug>.yaml`
angelegt; diese Beispiele dienen als Vorlage.
