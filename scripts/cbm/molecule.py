"""Strukturformeln (Skelettformel) mit RDKit als SVG.

Quelle der Struktur ist `front_content.smiles` – bei Molekülen aus PubChem
unverändert übernommen (`pubchem_cid` dokumentiert die Herkunft). Darstellung:

  - `form: physiological` deprotoniert Carbonsäuren, Phosphat- und Sulfonsäure-
    gruppen (Form bei pH 7,4; für Namen auf „-at“). `form: as_is` zeichnet die
    Struktur wie angegeben.
  - Platzhalteratome `[*:n]` werden über `labels: {n: "CoA"}` beschriftet
    (z. B. Acyl-CoA, Reste R₁–R₃). `<sub>`/`<sup>` sind erlaubt.
  - Fester Maßstab (Bindungslänge) für alle Karten; sehr große Moleküle
    werden im Template nur verkleinert, nie vergrößert.
"""
from __future__ import annotations

import math
import os
import re

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

BOND_PX = 34.0          # Bindungslänge in SVG-Einheiten
PX_TO_MM = 0.26         # → 8,8 mm Bindungslänge auf der Karte
MIN_W_MM, MIN_H_MM = 62.0, 44.0   # Zielgröße kleiner Moleküle
MAX_UPSCALE = 1.7                 # höchstens 1,7-fach vergrößern
FONT_FILE = os.environ.get("CBM_FONT_FILE", "/usr/share/fonts/opentype/inter/Inter-Medium.otf")

_IONIZE = [
    # Carbonsäure, Phosphat-/Phosphonat-OH, Sulfonsäure → Anion
    Chem.MolFromSmarts("[CX3](=O)[OX2H1]"),
    Chem.MolFromSmarts("[PX4][OX2H1]"),
    Chem.MolFromSmarts("[SX4](=O)(=O)[OX2H1]"),
]


def _ionize(mol: Chem.Mol) -> Chem.Mol:
    rw = Chem.RWMol(mol)
    for patt in _IONIZE:
        for match in rw.GetSubstructMatches(patt):
            o = rw.GetAtomWithIdx(match[-1])
            if o.GetSymbol() == "O" and o.GetTotalNumHs() == 1 and o.GetFormalCharge() == 0:
                o.SetFormalCharge(-1)
                o.SetNoImplicit(True)
                o.SetNumExplicitHs(0)
    mol = rw.GetMol()
    Chem.SanitizeMol(mol)
    return mol


def prepare(front_content: dict) -> Chem.Mol:
    mol = Chem.MolFromSmiles(front_content["smiles"])
    if mol is None:
        raise ValueError(f"Ungültiges SMILES: {front_content['smiles']}")
    if front_content.get("form", "as_is") == "physiological":
        mol = _ionize(mol)
    labels = {str(k): v for k, v in (front_content.get("labels") or {}).items()}
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 0:
            label = labels.get(str(atom.GetAtomMapNum()))
            if label is None:
                raise ValueError("Platzhalteratom ohne Beschriftung in labels")
            atom.SetAtomMapNum(0)
            atom.SetProp("atomLabel", label)
    return mol


def _min_nonbonded_distance(mol: Chem.Mol) -> float:
    conf = mol.GetConformer()
    pos = [conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms())]
    best = math.inf
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            if mol.GetBondBetweenAtoms(i, j) is None:
                best = min(best, (pos[i] - pos[j]).Length())
    return best


def _layout(mol: Chem.Mol, mode: str = "auto") -> None:
    """2D-Koordinaten: CoordGen bevorzugt; bei Atomüberlappung (Abstand < 0,5
    Bindungslängen) RDKit-eigenes Layout, sonst das bessere von beiden.
    `mode` ("auto" | "coordgen" | "rdkit") erzwingt bei Bedarf ein Verfahren
    (Kartenfeld front_content.layout, z. B. wenn sich Beschriftungen berühren)."""
    if mode in ("coordgen", "rdkit"):
        rdDepictor.SetPreferCoordGen(mode == "coordgen")
        rdDepictor.Compute2DCoords(mol)
        rdDepictor.SetPreferCoordGen(True)
        return
    candidates = []
    for prefer in (True, False):
        rdDepictor.SetPreferCoordGen(prefer)
        rdDepictor.Compute2DCoords(mol)
        candidates.append((_min_nonbonded_distance(mol), prefer))
        if candidates[-1][0] >= 0.5:
            break
    best_prefer = max(candidates)[1]
    if best_prefer != candidates[-1][1]:
        rdDepictor.SetPreferCoordGen(best_prefer)
        rdDepictor.Compute2DCoords(mol)
    rdDepictor.SetPreferCoordGen(True)


def molecule_svg(front_content: dict) -> str:
    mol = prepare(front_content)
    _layout(mol, front_content.get("layout", "auto"))
    if front_content.get("rotate"):
        conf = mol.GetConformer()
        a = math.radians(float(front_content["rotate"]))
        for i in range(mol.GetNumAtoms()):
            p = conf.GetAtomPosition(i)
            conf.SetAtomPosition(i, (p.x * math.cos(a) - p.y * math.sin(a),
                                     p.x * math.sin(a) + p.y * math.cos(a), 0.0))

    drawer = rdMolDraw2D.MolDraw2DSVG(-1, -1)
    opts = drawer.drawOptions()
    opts.useBWAtomPalette()
    opts.fixedBondLength = BOND_PX
    opts.bondLineWidth = 1.6
    opts.scaleBondWidth = False
    opts.clearBackground = False
    opts.padding = 0.06
    opts.addStereoAnnotation = False
    opts.flagCloseContactsDist = -1   # keine roten Prüfkästen auf Karten
    opts.minFontSize = 13
    opts.maxFontSize = 13
    opts.multipleBondOffset = 0.18
    opts.additionalAtomLabelPadding = 0.08
    if os.path.exists(FONT_FILE):
        opts.fontFile = FONT_FILE
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    svg = svg[svg.index("<svg"):]
    w = float(re.search(r"width='([\d.]+)px'", svg).group(1))
    h = float(re.search(r"height='([\d.]+)px'", svg).group(1))
    # Kleine Moleküle bis max. MAX_UPSCALE vergrößern, damit sie die Karte füllen;
    # große behalten den festen Maßstab (das Template verkleinert nur bei Bedarf).
    k = PX_TO_MM * max(1.0, min(MIN_W_MM / (w * PX_TO_MM), MIN_H_MM / (h * PX_TO_MM), MAX_UPSCALE))
    svg = re.sub(r"width='[\d.]+px' height='[\d.]+px'",
                 f"width='{w * k:.2f}mm' height='{h * k:.2f}mm' "
                 f"class='molecule' role='img' aria-label='Strukturformel'", svg, count=1)
    # Schwarz → Kartentextfarbe (currentColor), damit Tokens gelten
    svg = re.sub(r"#000000", "currentColor", svg)
    return svg
