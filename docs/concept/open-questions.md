# Offene Fragen (Freigabe durch Andreas / AT Medical)

Diese Punkte sind **bewusst nicht einseitig entschieden**, weil sie bestehende Konventionen
berühren, externe Systeme betreffen oder eine fachliche/geschäftliche Festlegung brauchen.

## Neu seit Pilotstart (2026-10-31)
- **A. Vorläufige IDs (ADR-016, ADR-020):** Sind die vergebenen ID-Blöcke (`bc_061`–`bc_269`, siehe ADR-020)
  in Ordnung, oder gibt es eine andere Nummerierung im Masterverzeichnis?
- **F. Darstellungskonventionen (ADR-019):** Metabolite mit „-at“-Namen in deprotonierter Form; Peptidhormone
  vorne nur mit Bezeichnung – so gewünscht?
- **B. Logo (ADR-017):** Freigegebene Logo-Datei (SVG) für die Kopfzone bereitstellen.
- **C. Musterkarten:** Upload nach `input/uploaded_raw/`, um Layout und Inhaltstiefe abzugleichen.
- **D. Fachreviewer:** Wer prüft und gibt die Pilotkarten frei (`reviewer`-Feld)?
- **E. Pharma-Modul:** PR #8 (Modul PH) aus einer anderen Session mit dieser Pipeline und der
  Tab-/Modul-Entscheidung (ADR-004) abstimmen.

## Taxonomie & Inhalt
1. **Tab- vs. Modulstruktur (ADR-004):** Soll die sichtbare Tab-Leiste exakt die 6 Handover-Tabs
   zeigen, während die Modulcodes (AC/OC/BC/MB/APC/PH) als Paketdimension bleiben? Sollen **APC**
   (Ernährung/Medizin) und **PH** (Pharma) perspektivisch **eigene Tabs** erhalten, sobald die
   Inhalte wachsen?
2. **„Allgemein“ vs. „Anorganik“:** Als zwei getrennte Tabs führen (Handover-Tabliste) — auch wenn
   Modul **AC** beide zusammenfasst? (Konzept nimmt „ja, zwei Tabs“ an.)
3. **Vitamin S / Schokolade:** humorvolle Sonderkarte wie im Handover beibehalten? (angenommen: ja)

## Moodle (ADR-008)
4. Welche **Moodle-Version** und welches **Flashcard-/H5P-Plugin** sind im ATMED-Moodle aktiv?
   Davon hängt das konkrete Importformat ab.
5. Soll **LTI 1.3 mit Noten-Rückgabe (AGS)** genutzt werden, oder reicht zunächst Launch + Deep
   Linking ohne Grading?

## Druck (Kap. 07)
6. **Druckdienstleister / Farbprofil:** Zielmaschine/ICC-Profil für CMYK-Konvertierung? Beschnitt-
   und Papiervorgaben (Grammatur, Finish)?
7. **Standard-Nutzenzahl** je Bogen (2/4/8 pro Seite) und Wendeachse (lange/kurze Kante)?

## Online-System
8. **Lizenz-/Kaufmodell:** Wie granular sind Pakete (je Modul? Campus-Lizenz?) und wie genau
   koppelt WooCommerce die Freischaltung (`online-platform/licensing/*` konkretisieren)?
9. **Nutzer-Uploads / Medien:** Dürfen Lernende eigene Medien hochladen (Quoten in
   `storage-quotas.md`)? DSGVO-/Speicherfolgen klären.
10. **`app/` vs. `online-platform/` (ADR-013):** Soll der Code später nach `online-platform/`
    konsolidiert werden, oder bleibt `app/` die Heimat der Implementierung?

## Betrieb (Kap. 15)
11. **Authentik-Application/Gruppen:** Namen der OIDC-Application und Rollengruppen
    (`chembiomed-admins/-editors/-reviewer/-dozenten`) festlegen.
12. **Domain/TLS:** `chembiomed-cards.de` bereits auf ATMED-core/Traefik geroutet? DNS-Stand?
13. **Backup-Einbindung:** Aufnahme von Postgres/Storage in die bestehende Restic-/Backup-Kette
    bestätigen.

## Vorgehen
14. ~~Reihenfolge nach Upload~~ – *entschieden (ADR-014/015): Produktion aus Daten, Pilot Aminosäuren.*
15. **Print-/Moodle-Linie zuerst oder parallel Online-MVP?** (Konzept erlaubt beides unabhängig.)

> Bis zur Klärung bleiben die betroffenen Punkte im Konzept als *proposed* markiert; es werden
> **keine** Live-Systeme verändert und **keine** bestehenden IDs/Registry stillschweigend
> überschrieben.
