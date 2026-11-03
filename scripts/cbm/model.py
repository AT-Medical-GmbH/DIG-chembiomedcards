"""Laden und Validieren der Kartendaten (docs/concept/02-content-model.md §5)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CARDS_DIR = DATA / "cards"
TOKENS_FILE = ROOT / "brand" / "design-tokens" / "chembiomed.tokens.json"


@dataclass
class Issue:
    card_id: str
    level: str  # "error" | "warning"
    message: str


@dataclass
class Project:
    tokens: dict
    tabs: list[dict]
    modules: dict
    tags: set[str]
    cards: list[dict]
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]


def _load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_project(card_filter: str | None = None) -> Project:
    tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))["tokens"]["card"]
    cats = _load_yaml(DATA / "categories.yaml")
    tabs = [dict(t, color=tokens["categories"][t["key"]]) for t in cats["tabs"]]
    tag_groups = _load_yaml(DATA / "tags.yaml")
    tags = {t for group in tag_groups.values() for t in group}
    cards = []
    for path in sorted(CARDS_DIR.glob("*.yaml")):
        card = _load_yaml(path)
        card["_file"] = path.name
        if card_filter and not path.stem.startswith(card_filter):
            continue
        cards.append(card)
    project = Project(tokens, tabs, cats["modules"], tags, cards)
    validate(project)
    return project


def validate(project: Project) -> None:
    schema = json.loads((DATA / "schema" / "card.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    tab_keys = {t["key"] for t in project.tabs}
    seen_ids: dict[str, str] = {}
    seen_slugs: dict[str, str] = {}

    def add(cid, level, msg):
        project.issues.append(Issue(cid, level, msg))

    for card in project.cards:
        cid = card.get("card_id", card["_file"])
        data = {k: v for k, v in card.items() if not k.startswith("_")}
        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            add(cid, "error", f"Schema: {loc}: {err.message}")

        if card["_file"] != f"{cid}.yaml":
            add(cid, "error", f"Dateiname {card['_file']} passt nicht zu card_id")
        module = card.get("module", "")
        if not cid.startswith(module.lower() + "_"):
            add(cid, "error", f"card_id-Präfix passt nicht zum Modul {module}")
        if not str(card.get("slug", "")).startswith(cid + "_"):
            add(cid, "error", "slug muss mit <card_id>_ beginnen")
        for key, seen, label in ((cid, seen_ids, "card_id"), (card.get("slug"), seen_slugs, "slug")):
            if key in seen:
                add(cid, "error", f"{label} doppelt (auch in {seen[key]})")
            seen[key] = card["_file"]

        primary = card.get("primary_category")
        if primary not in tab_keys:
            add(cid, "error", f"primary_category '{primary}' ist kein Register-Tab")
        for sec in card.get("secondary_categories") or []:
            if sec not in tab_keys:
                add(cid, "error", f"secondary_category '{sec}' ist kein Register-Tab")
            if sec == primary:
                add(cid, "warning", f"secondary_category '{sec}' entspricht der Hauptkategorie")
        for tag in card.get("tags") or []:
            if tag not in project.tags:
                add(cid, "error", f"Tag '{tag}' fehlt in data/tags.yaml")

        fc = card.get("front_content") or {}
        if card.get("front_type") == "structure":
            if fc.get("render") == "fischer_projection" and not (fc.get("side_chain") or fc.get("special")):
                add(cid, "error", "Fischer-Projektion ohne side_chain/special")
            # Lint: kein Name auf Aminosäure-Vorderseiten (Konzept Kap. 05 §5.1)
            if "aminosaeure" in (card.get("tags") or []):
                shown = " ".join(str(fc.get(k, "")) for k in ("caption", "text")).lower()
                names = [card["title"].lower()] + [p.strip().lower() for p in card["title"].split("/")]
                if any(n and n in shown for n in names) or fc.get("caption"):
                    add(cid, "error", "Aminosäure-Vorderseite darf keinen Namen/keine Beschriftung tragen")
        render = fc.get("render")
        if render == "molecule":
            smiles = fc.get("smiles", "")
            if not smiles:
                add(cid, "error", "Strukturformel (render: molecule) ohne smiles")
            placeholders = set(re.findall(r"\[\*:(\d+)\]", smiles))
            labels = {str(k) for k in (fc.get("labels") or {})}
            if placeholders != labels:
                add(cid, "error", f"Platzhalter {sorted(placeholders)} und labels {sorted(labels)} passen nicht zusammen")
            if "pubchem_cid" not in fc and not fc.get("structure_note"):
                add(cid, "warning", "Strukturquelle undokumentiert (pubchem_cid oder structure_note angeben)")
        if render in ("term", "formula") and not fc.get("text"):
            add(cid, "error", f"Vorderseite ({render}) ohne text")
        if render == "formula" and re.sub(r"</?(sub|sup)>", "", fc.get("text", "")).count("<"):
            add(cid, "error", "Formel-Text darf nur <sub>/<sup> enthalten")

        back = card.get("back_sections") or {}
        if not any(back.get(k) for k in ("biochemical_relevance", "clinical_relevance", "molecular_relevance")):
            add(cid, "error", "Rückseite ohne Relevanz-Sektion")
        if card.get("review_status") == "approved" and not (card.get("reviewer") and card.get("references")):
            add(cid, "error", "approved erfordert reviewer und references")
        if card.get("review_status") in ("draft", "needs_review"):
            add(cid, "warning", f"review_status={card.get('review_status')} – nicht für Live-Ausgabe freigegeben")
        if card.get("id_status") == "provisional":
            add(cid, "warning", "card_id ist vorläufig vergeben (Bestätigung im Masterverzeichnis ausstehend)")
