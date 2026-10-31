# Offene Fragen (Freigabe durch Andreas / AT Medical)

Am **2026-10-31** wurden alle bis dahin offenen Fragen in einer strukturierten Abfrage beantwortet.
Die Entscheidungen stehen unten; die Begründungen im [Decision Log](decision-log.md) (ADR-022/023).

## Noch offen

| # | Punkt | Was fehlt | Blockiert |
|---|---|---|---|
| 1 | **Read-only-Prüfung der Server** (freigegeben) | Aus der Cloud-Session gibt es keinen SSH-Zugang (keine Schlüssel/Aliase, kein Rechner per Remote Control). Ausgabe der Befehle aus dem Abschnitt „Befehle für die Read-only-Prüfung“ liefern **oder** einen Rechner per Remote Control freigeben. | Moodle-Importformat (Plugin), Deployment-Planung (DNS/Traefik, Backup-Kette) |
| 2 | **Fachreview der 116 Karten** durch Andreas | Arbeitsliste: [`reports/cards_review_needed.md`](../../reports/cards_review_needed.md) | Freigabe für Druck, Moodle, Online |
| 3 | **Abnahme der Logo-Vektorfassung** | `brand/logo/chembiomed-cards-logo-full.svg` ist eine automatische Nachzeichnung (Abweichungen im Detail möglich) | Verwendung im Druck (Boxen, Verpackung) |
| 4 | **APC/PH als eigene Tabs?** | Neu entscheiden, sobald Inhalte in diesen Modulen entstehen | – |

### Befehle für die Read-only-Prüfung

Auf dem lokalen Rechner (PowerShell oder Bash) ausführen, Ausgabe zurückgeben. Alle Befehle lesen
nur, nichts wird geändert.

```text
ssh -n -T -o BatchMode=yes -o ConnectTimeout=8 ATMED-core "docker ps --format '{{.Names}}' | grep -i moodle"
ssh -n -T -o BatchMode=yes -o ConnectTimeout=8 ATMED-core "ls /srv/atmed/moodle-src/mod /srv/atmed/moodle-src/question/type /srv/atmed/moodle-src/blocks 2>/dev/null"
ssh -n -T -o BatchMode=yes -o ConnectTimeout=8 ATINFRA-gateway "getent hosts chembiomed-cards.de; grep -rl chembiomed /etc/traefik /srv 2>/dev/null | head"
ssh -n -T -o BatchMode=yes -o ConnectTimeout=8 ATMED-core "systemctl list-timers --all | grep -iE 'restic|backup'"
```

## Entschieden am 2026-10-31

| Thema | Entscheidung |
|---|---|
| Kartenfarben | Logofarben behalten (Navy/Petrol/Rot) – ADR-021 |
| Logo im Kartenkopf | Kompaktfassung (Bildmarke + Wortmarke ohne Unterzeilen) freigegeben – ADR-021 |
| Logo als Vektor | Claude vektorisiert das PNG (umgesetzt, Abnahme offen – s. o.) |
| Strukturdarstellung | „-at“-Stoffe deprotoniert, Peptidhormone vorne nur mit Namen – ADR-019 |
| Tab-Leiste | Handover-Tabs; **„Allgemein“ und „Anorganik“ als ein gemeinsamer Tab** „Allg./Anorganik“ (5 Tabs); APC/PH vorerst unter Klinik – ADR-004, ADR-022 |
| Karten-IDs | alle 116 IDs bestätigt und ins Masterverzeichnis eingetragen – ADR-016, ADR-020 |
| Vitamin S | behalten |
| Fachreview | Andreas prüft selbst |
| Musterkarten | nicht mehr nötig |
| Pharma-PR #8 | läuft getrennt weiter |
| Nächste Schritte | Druck-/Moodle-Pakete **und** Online-MVP parallel |
| Moodle-Plugin | Claude prüft read-only (blockiert – s. o.) |
| LTI 1.3 | zunächst ohne Notenrückgabe (Login + Deep Linking) – ADR-008 |
| Druck-Farbprofil | RGB jetzt, CMYK final mit der Druckerei |
| Druckbögen | 4 × A6 pro A4, Duplex über die lange Kante (Standard); 2/8 pro Seite und ohne Schnittmarken zusätzlich |
| Lizenzmodell | pro Modul über WooCommerce |
| Nutzer-Uploads | ja, mit Speicherkontingent (Virenprüfung, Löschkonzept nötig) |
| Authentik | Application `chembiomed-cards`, Gruppen `chembiomed-admins/-editors/-reviewers/-dozenten` |
| Server-Prüfung | read-only freigegeben |
| Code-Verzeichnis | `app/` für die Implementierung (ADR-013, unverändert) |

> Es werden weiterhin **keine** Live-Systeme verändert; produktive Schritte erst nach gesonderter
> Freigabe und nach den ATMED-Betriebsregeln.
