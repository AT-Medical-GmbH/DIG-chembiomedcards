# Checkliste Fachreview Pharmakologie

**Rolle:** `reviewer_pharm` · **Für:** Wirkstoffkarten, Antidotkarten, Interaktionskarten, Prinzipkarten

Jeder Punkt wird mit **OK**, **Korrektur** (mit Vorschlag) oder **n/a** bewertet und im Protokoll
festgehalten.

## A. Identität
- [ ] Wirkstoffname (INN) korrekt geschrieben, keine Verwechslung mit ähnlich klingenden Stoffen
- [ ] Wirkstoffgruppe (`drug_class`) zutreffend
- [ ] Kategorie und Tags passen zum Inhalt

## B. Wirkmechanismus
- [ ] Zielstruktur (Rezeptor, Enzym, Kanal, Transporter) korrekt benannt
- [ ] Art der Wirkung korrekt (Agonist, Antagonist, Inhibitor, Modulator)
- [ ] Vereinfachungen sind didaktisch vertretbar und nicht falsch

## C. Klinische Anwendung
- [ ] Indikationen entsprechen aktuellem Stand (Leitlinie/Fachinformation)
- [ ] Keine veraltete oder nicht mehr empfohlene Indikation als aktuell dargestellt
- [ ] Off-Label-Anwendungen als solche erkennbar

## D. Risiken
- [ ] Relevante, häufige und schwere Nebenwirkungen enthalten
- [ ] Kontraindikationen und Warnhinweise vollständig für den Lernzweck
- [ ] Relevante Interaktionen genannt (inkl. CYP/Transporter, QT, additive ZNS-Dämpfung)
- [ ] Monitoring-Hinweise angemessen

## E. Dosierung
- [ ] Keine konkreten Zahlen ohne Quelle; `dose_contains_numeric` korrekt gesetzt
- [ ] Dosierungsprinzip korrekt (z. B. titrieren, gewichtsadaptiert, Applikationsweg)
- [ ] Verwechslungsrisiken benannt (Konzentrationen, Enantiomere, Salzformen)
- [ ] Besondere Gruppen (Niere, Leber, Schwangerschaft, Kinder, Ältere) erwähnt, wo relevant

## F. Quellen und Status
- [ ] Mindestens eine aktuelle Quelle mit Jahr in `references`
- [ ] Alle Punkte aus `review_focus` der Karte geprüft
- [ ] `warning_level` angemessen
- [ ] Ergebnis: `reviewed` oder zurück an Redaktion
