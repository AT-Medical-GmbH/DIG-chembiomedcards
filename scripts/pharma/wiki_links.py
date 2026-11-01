"""Verknüpfungsstandard QR → WikiMedica (v0.2, Entscheidung Andreas Tremml 2026-10-31).

- Wirkstoffkarten (Feld ``substance_name`` gesetzt) erhalten ``wirkstoff_slug`` und zeigen auf
  ``https://at-medical.de/w/wirkstoff/<slug>``.
- Alle übrigen Karten (Übersicht, Toxidrom) erhalten ``begriff_slug`` und zeigen auf
  ``https://at-medical.de/w/begriff/<slug>``.
- ``qr_url`` wird ausschließlich daraus erzeugt (``scripts/pharma/sync_qr_urls.py``) und vom
  Validator auf Übereinstimmung geprüft. Maßgeblich ist das zentrale Linkregister; die tägliche
  Konsistenzprüfung auf ATMED-core meldet Abweichungen.
"""
from __future__ import annotations

import re

WIKI_BASE = "https://at-medical.de/w"
SLUG_FORMAT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_UMLAUTE = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
_GRIECHISCH = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "κ": "kappa",
    "λ": "lambda", "µ": "my", "μ": "my", "ω": "omega",
}


def slugify(name: str) -> str:
    """Slug-Regel des Standards: Kleinschreibung, Umlaute/ß ersetzt, Klammerzusätze entfernt,
    griechische Buchstaben ausgeschrieben, alles andere zu Bindestrich."""
    s = re.sub(r"\([^)]*\)", " ", name).lower()
    for src, dst in {**_UMLAUTE, **_GRIECHISCH}.items():
        s = s.replace(src, dst)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def link_kind(card: dict) -> str:
    """'wirkstoff' für Karten mit Wirkstoff, sonst 'begriff'."""
    return "wirkstoff" if card.get("substance_name") else "begriff"


def slug_field(card: dict) -> str:
    return "wirkstoff_slug" if link_kind(card) == "wirkstoff" else "begriff_slug"


def expected_slug(card: dict) -> str:
    """Slug, der sich nach der Regel aus Wirkstoffname bzw. Titel ergibt."""
    return slugify(card.get("substance_name") or card.get("title", ""))


def wiki_url(card: dict) -> str:
    """Ziel-URL aus dem gepflegten Slug-Feld (nicht aus dem Titel)."""
    return f"{WIKI_BASE}/{link_kind(card)}/{card.get(slug_field(card), '')}"


def short_url(url: str) -> str:
    """Kurzform für den Klartext unter dem QR-Code (ohne Schema)."""
    return re.sub(r"^https?://", "", url)


def check(card: dict) -> tuple[list[str], list[str]]:
    """Fehler und Warnungen zur Verknüpfung einer Karte."""
    cid = card.get("card_id", "?")
    errors, warnings = [], []
    field = slug_field(card)
    other = "begriff_slug" if field == "wirkstoff_slug" else "wirkstoff_slug"
    slug = card.get(field)
    if not slug:
        errors.append(f"{cid}: {field} fehlt (Verknüpfungsstandard v0.2)")
        return errors, warnings
    if card.get(other):
        errors.append(f"{cid}: {other} gesetzt, für diesen Kartentyp ist {field} vorgesehen")
    if not SLUG_FORMAT.match(str(slug)):
        errors.append(f"{cid}: {field} '{slug}' verletzt das Slug-Format")
    if card.get("qr_url") != wiki_url(card):
        errors.append(f"{cid}: qr_url '{card.get('qr_url')}' ≠ {wiki_url(card)} "
                      "(make ph-qr-sync ausführen)")
    exp = expected_slug(card)
    if slug != exp:
        warnings.append(f"{cid}: {field} '{slug}' weicht von der Slug-Regel ab ('{exp}') "
                        "— nur zulässig, wenn das Linkregister es so führt")
    return errors, warnings
