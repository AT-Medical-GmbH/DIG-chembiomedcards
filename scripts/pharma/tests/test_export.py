"""Tests für die Export-Pipeline von Pharma Cards (Modul PH).

Ausführen:  python3 -m pytest scripts/pharma/tests -q
Rendering-Tests mit Chromium werden übersprungen, wenn Playwright fehlt.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
REPO = HERE.parents[2]

import generate_moodle_import as gm  # noqa: E402
import generate_print_sheets as gp  # noqa: E402
import render_cards  # noqa: E402
from validate_output import is_exportable  # noqa: E402


def card(cid="ph_900", wl="low", rs="approved", cat="allgemeine_pharmakologie", sec=None):
    return {
        "card_id": cid, "slug": f"{cid}_test", "title": f"Test {cid}", "module": "PH",
        "primary_category": cat, "secondary_categories": sec or [], "card_type": "overview",
        "front_type": "principle", "warning_level": wl, "review_status": rs,
        "front_content": {"question": "Frage?"}, "updated_at": "2026-10-31", "version": "0.1.0",
        "qr_url": f"https://chembiomed-cards.de/c/{cid.replace('_', '')}",
        "back_sections": [
            {"key": "kernaussage", "label": "Kern", "color_role": "base", "text": "Zeile\tmit Tab"},
            {"key": "merke", "label": "Merke", "color_role": "antidote", "text": "- a\n- b"},
        ],
    }


# ---------------- Export-Gating ----------------

@pytest.mark.parametrize("wl,rs,expected", [
    ("critical", "approved", True),
    ("critical", "reviewed", False),          # critical nur mit approved
    ("high", "reviewed", True),
    ("moderate", "reviewed", True),
    ("low", "needs_review", False),
    ("high", "toxicology_review_needed", False),
    ("high", "clinical_review_needed", False),
    ("low", "draft", False),
])
def test_is_exportable(wl, rs, expected):
    assert is_exportable(card(wl=wl, rs=rs)) is expected


def test_release_selection_excludes_unreviewed_and_preview_includes_them():
    cards = [card("ph_901", "critical", "approved"), card("ph_902", "critical", "reviewed"),
             card("ph_903", "low", "needs_review"), card("ph_904", "low", "archived")]
    assert [c["card_id"] for c in gm.select_cards(cards, preview=False)] == ["ph_901"]
    assert [c["card_id"] for c in gm.select_cards(cards, preview=True)] == ["ph_901", "ph_902", "ph_903"]


def test_package_membership_uses_primary_and_secondary_categories():
    pkg = {"categories": ["notfallmedikamente"]}
    assert gm.in_package(card(cat="notfallmedikamente"), pkg)
    assert gm.in_package(card(cat="antidote", sec=["notfallmedikamente"]), pkg)
    assert not gm.in_package(card(cat="antidote"), pkg)
    assert gm.in_package(card(cat="antidote"), {"categories": ["*"]})


def test_every_scope_package_has_unique_label():
    pkgs = gm.load_packages(REPO / "cards/PH/scope")
    labels = [p["label"] for p in pkgs]
    assert len(labels) == len(set(labels))
    assert any("*" in p["categories"] for p in pkgs), "Gesamtset fehlt"


# ---------------- Moodle-Formate ----------------

def test_one_line_strips_tabs_and_newlines():
    assert gm.one_line("a\tb\r\nc\nd") == "a b c d"


def test_moodle_package_formats(tmp_path):
    scope = render_cards.load_scope(REPO / "cards/PH/scope")
    css = (REPO / "card-system/templates/pharma/card.css").read_text(encoding="utf-8")
    pkg = {"slug": "t", "name": "Test", "label": "Test", "categories": ["*"]}
    gm.build_package(pkg, [card("ph_901"), card("ph_902")], scope, css, tmp_path / "out",
                     tmp_path / "dist", preview=False, images=False)
    d = tmp_path / "out" / "Pharma_Cards_Moodle_Test"
    tab = (d / "DIRECT_IMPORT_TAB_CRLF.txt").read_bytes()
    assert tab.count(b"\r\n") == 2
    assert b"\n" not in tab.replace(b"\r\n", b"")
    assert all(line.count(b"\t") == 1 for line in tab.split(b"\r\n") if line)
    assert (d / "DIRECT_IMPORT_SEMICOLON_CRLF.txt").read_bytes().startswith(b"\xef\xbb\xbf")
    rows = list(csv.DictReader(open(d / "import.csv", encoding="utf-8", newline="")))
    assert list(rows[0].keys()) == gm.FIELDS
    assert {r["card_id"] for r in rows} == {"ph_901", "ph_902"}
    assert "keine Therapieanweisung" in rows[0]["back_html"]
    assert (tmp_path / "dist" / "Pharma_Cards_Moodle_Test.zip").exists()


def test_zip_is_deterministic(tmp_path):
    src = tmp_path / "pkg"
    (src / "sub").mkdir(parents=True)
    (src / "a.txt").write_text("A")
    (src / "sub" / "b.txt").write_text("B")
    gm.write_zip(src, tmp_path / "1.zip")
    gm.write_zip(src, tmp_path / "2.zip")
    assert (tmp_path / "1.zip").read_bytes() == (tmp_path / "2.zip").read_bytes()


# ---------------- Ausschießen / Duplex ----------------

@pytest.mark.parametrize("name", list(gp.VARIANTS))
def test_layout_fits_on_paper(name):
    paper, n, marks = gp.VARIANTS[name]
    lay = gp.compute_layout(paper, n, marks)
    margin = gp.MARGIN_MARKS if marks else gp.MARGIN_PLAIN
    assert lay.cols * lay.rows == n
    assert 0 < lay.scale <= 1.0
    for slot in range(n):
        x, y = lay.trim_origin(slot)
        assert x - lay.bleed >= margin - lay.bleed - 1e-6
        assert y - lay.bleed >= margin - lay.bleed - 1e-6
        assert x + lay.card_w + lay.bleed <= lay.width - margin + lay.bleed + 1e-6
        assert y + lay.card_h + lay.bleed <= lay.height - margin + lay.bleed + 1e-6
    if marks:  # Schnittmarken müssen auf das Papier passen
        x0, y0 = lay.trim_origin(0)
        assert y0 - lay.bleed - gp.MARK_OFFSET - gp.MARK_LEN >= 0
        assert x0 - lay.bleed - gp.MARK_OFFSET - gp.MARK_LEN >= 0


def test_a4_two_up_is_full_size():
    assert gp.compute_layout("A4", 2, True).scale == 1.0
    assert gp.compute_layout("A4", 2, False).scale == 1.0


@pytest.mark.parametrize("name", list(gp.VARIANTS))
@pytest.mark.parametrize("flip", ["long", "short"])
def test_back_slot_is_a_permutation_and_involution(name, flip):
    lay = gp.compute_layout(*gp.VARIANTS[name])
    n = lay.cols * lay.rows
    mapped = [gp.back_slot(lay, s, flip) for s in range(n)]
    assert sorted(mapped) == list(range(n))
    assert all(gp.back_slot(lay, m, flip) == s for s, m in enumerate(mapped))


def test_back_slot_direction():
    portrait = gp.compute_layout("A4", 2, True)            # 1×2 hoch
    assert (portrait.orientation, portrait.cols, portrait.rows) == ("hoch", 1, 2)
    assert gp.back_slot(portrait, 0, "long") == 0           # Spalten spiegeln: 1 Spalte -> gleich
    assert gp.back_slot(portrait, 0, "short") == 1          # Zeilen spiegeln
    landscape = gp.compute_layout("A4", 4, True)           # 2×2 quer
    assert landscape.orientation == "quer"
    assert gp.back_slot(landscape, 0, "long") == 2          # quer + lange Kante: Zeilen spiegeln
    assert gp.back_slot(landscape, 0, "short") == 1         # quer + kurze Kante: Spalten spiegeln


# ---------------- QR ----------------

def test_qr_svg_is_real_code_or_placeholder():
    svg = render_cards.qr_svg("https://chembiomed-cards.de/c/ph100")
    try:
        import qrcode  # noqa: F401
    except ImportError:
        assert svg is None
        assert "placeholder" in render_cards.footer_html(card(), with_qr=True)
        return
    assert svg.startswith("<svg") and "viewBox" in svg and 'fill="#000"' in svg
    assert 'class="qr"' in render_cards.footer_html(card(), with_qr=True)
    assert 'class="qr' not in render_cards.footer_html(card(), with_qr=False)


# ---------------- Rendering (Chromium) ----------------

def test_rendered_sample_has_no_overflow():
    pytest.importorskip("playwright")
    import check_layout
    scope = render_cards.load_scope(REPO / "cards/PH/scope")
    css = (REPO / "card-system/templates/pharma/card.css").read_text(encoding="utf-8")
    assert check_layout.measure([card("ph_901")], scope, css) == []
    long = card("ph_902")
    long["back_sections"] = [{"key": f"k{i}", "label": f"Box {i}", "color_role": "risk",
                              "text": "Sehr langer Text. " * 25} for i in range(8)]
    kinds = {f["kind"] for f in check_layout.measure([long], scope, css)}
    assert "Überlauf" in kinds, "Überlauf muss erkannt werden"
