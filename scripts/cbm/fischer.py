"""Fischer-Projektion für Aminosäuren als SVG.

Feste Konvention (docs/concept/05-card-layout.md §5.1):
  - Carboxylgruppe oben, vollständig gezeichnet: C mit Doppelbindung zu O und Bindung zu OH
  - α-C-Atom in der Mitte (explizit als "C")
  - Aminogruppe links, Wasserstoff rechts (L-Konfiguration)
  - Seitenkette (Rest) unten
  - kein Name der Aminosäure

Die Seitenkette wird datengetrieben aus `front_content.side_chain` gezeichnet
(Knoten mit Beschriftung, optionalen Links-/Rechts-Substituenten, Gabeln für
C(=O)X-Gruppen und Endringen). Prolin ist ein Sonderfall (`special: proline`).
"""
from __future__ import annotations

import math
import re
from html import escape

L = 46.0          # Bindungslänge (Abstand zwischen Atommittelpunkten)
FONT = 17.0       # Schriftgröße Atombeschriftung
STROKE = 1.9      # Strichstärke Bindungen
DOUBLE_GAP = 3.4  # Abstand der Linien einer Doppelbindung
LABEL_PAD = 2.6   # Abstand zwischen Bindungsende und Beschriftung
SCALE_MM = 0.27   # fester Maßstab: 1 Einheit = 0,27 mm (gleiche Atomgröße auf allen Karten)
COS30 = math.cos(math.radians(30))


class Drawing:
    def __init__(self) -> None:
        self.segments: list[tuple[float, float, float, float]] = []
        self.boxes: list[tuple[float, float, float, float]] = []  # cx, cy, halbe Breite, halbe Höhe
        self.labels: list[str] = []
        self.xs: list[float] = []
        self.ys: list[float] = []

    def _track(self, x: float, y: float, pad: float = 0.0) -> None:
        self.xs += [x - pad, x + pad]
        self.ys += [y - pad, y + pad]

    def line(self, x1, y1, x2, y2) -> None:
        self.segments.append((x1, y1, x2, y2))
        self._track(x1, y1)
        self._track(x2, y2)

    def bond(self, a, b, order: int = 1, inner: tuple[float, float] | None = None) -> None:
        """Bindung a→b. Doppelbindung symmetrisch oder (mit `inner`) als
        Innenlinie zum Ringmittelpunkt hin."""
        (x1, y1), (x2, y2) = a, b
        if order == 1:
            self.line(x1, y1, x2, y2)
            return
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        nx, ny = -dy / n, dx / n
        if inner is None:
            g = DOUBLE_GAP / 2
            self.line(x1 + nx * g, y1 + ny * g, x2 + nx * g, y2 + ny * g)
            self.line(x1 - nx * g, y1 - ny * g, x2 - nx * g, y2 - ny * g)
            return
        # Ring-Doppelbindung: Außenlinie + verkürzte Innenlinie
        self.line(x1, y1, x2, y2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if (inner[0] - mx) * nx + (inner[1] - my) * ny < 0:
            nx, ny = -nx, -ny
        g = DOUBLE_GAP * 1.9
        s = 0.16
        self.line(
            x1 + dx * s + nx * g, y1 + dy * s + ny * g,
            x2 - dx * s + nx * g, y2 - dy * s + ny * g,
        )

    def label(self, x: float, y: float, text: str, anchor: str = "middle") -> None:
        self.labels.append(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
            f'dominant-baseline="central">{_formula_tspans(text)}</text>'
        )
        width = _text_width(text)
        self.boxes.append((x, y, width / 2, FONT * 0.42))
        if anchor == "middle":
            self.xs += [x - width / 2, x + width / 2]
        elif anchor == "end":
            self.xs += [x - width, x]
        else:
            self.xs += [x, x + width]
        self.ys += [y - FONT * 0.6, y + FONT * 0.6]

    def _trim(self, x, y, dx, dy):
        """Verkürzt ein Bindungsende, das in einer Beschriftung liegt, bis zu deren Rand."""
        for cx, cy, hw, hh in self.boxes:
            if abs(x - cx) <= hw + 1 and abs(y - cy) <= hh + 1:
                tx = (hw + LABEL_PAD) / abs(dx) if dx else math.inf
                ty = (hh + LABEL_PAD) / abs(dy) if dy else math.inf
                t = min(tx, ty)
                # vom Beschriftungszentrum aus messen (versetzte Doppelbindungslinien)
                proj = (x - cx) * dx + (y - cy) * dy
                return x + dx * (t - proj), y + dy * (t - proj)
        return x, y

    def _bond_lines(self) -> str:
        out = []
        for x1, y1, x2, y2 in self.segments:
            n = math.hypot(x2 - x1, y2 - y1)
            dx, dy = (x2 - x1) / n, (y2 - y1) / n
            ax, ay = self._trim(x1, y1, dx, dy)
            bx, by = self._trim(x2, y2, -dx, -dy)
            out.append(f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}"/>')
        return "".join(out)

    def svg(self, margin: float = 10.0) -> str:
        x0, x1 = min(self.xs) - margin, max(self.xs) + margin
        y0, y1 = min(self.ys) - margin, max(self.ys) + margin
        w, h = x1 - x0, y1 - y0
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="fischer" '
            f'viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" '
            f'width="{w * SCALE_MM:.2f}mm" height="{h * SCALE_MM:.2f}mm" '
            f'data-aspect="{w / h:.4f}" role="img" aria-label="Strukturformel">'
            f'<g class="bonds" stroke="currentColor" stroke-width="{STROKE}" '
            f'stroke-linecap="round" fill="none">{self._bond_lines()}</g>'
            f'<g class="atoms" font-size="{FONT}" fill="currentColor">{"".join(self.labels)}</g>'
            f"</svg>"
        )


def _formula_tspans(text: str) -> str:
    """'CH3' → CH<tspan sub>3</tspan>; Ziffern hinter Buchstaben/Klammern tiefgestellt."""
    out = []
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else ""
        if ch.isdigit() and (prev.isalpha() or prev in ")]" or prev.isdigit()):
            out.append(
                f'<tspan font-size="{FONT * 0.68:.1f}" dy="{FONT * 0.28:.1f}">{ch}</tspan>'
                f'<tspan dy="{-FONT * 0.28:.1f}">​</tspan>'
            )
        else:
            out.append(escape(ch))
    return "".join(out)


def _text_width(text: str) -> float:
    plain = re.sub(r"\d", "", text)
    digits = len(text) - len(plain)
    return FONT * 0.62 * len(plain) + FONT * 0.45 * digits


def _carboxyl_head(d: Drawing) -> None:
    c = (0.0, -L)
    d.bond(c, (0.0, 0.0))
    o = (-L * COS30, -L * 1.5)
    oh = (L * COS30, -L * 1.5)
    d.bond(c, o, 2)
    d.bond(c, oh)
    d.label(*c, "C")
    d.label(*o, "O")
    d.label(*oh, "OH")


def _alpha_center(d: Drawing, amino: str = "H2N") -> None:
    d.bond((0.0, 0.0), (-L, 0.0))
    d.bond((0.0, 0.0), (L, 0.0))
    d.label(0.0, 0.0, "C")
    d.label(-L, 0.0, amino)
    d.label(L, 0.0, "H")


def _ring(d: Drawing, kind: str, top: tuple[float, float], subs: dict | None = None) -> None:
    """Endring, dessen oberer Eckpunkt `top` an der Kette hängt. `subs` setzt
    Substituenten nach Ringposition (Phenyl: 2–6, Indol: 4–7)."""
    subs = {str(k): v for k, v in (subs or {}).items()}
    tx, ty = top
    s = L * 0.82  # Ringkante
    if kind in ("phenyl", "4-hydroxyphenyl"):
        cx, cy = tx, ty + s
        v = [(cx + s * math.cos(math.radians(-90 + 60 * k)),
              cy + s * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
        for k in range(6):
            d.bond(v[k], v[(k + 1) % 6], 2 if k % 2 == 1 else 1, inner=(cx, cy))
        if kind == "4-hydroxyphenyl":
            subs.setdefault("4", "OH")
        # Phenyl-Nummerierung: v[0] = C1 (Anknüpfung), im Uhrzeigersinn C2 … C6
        for pos, label in subs.items():
            _substituent(d, v[int(pos) - 1], (cx, cy), label)
        return

    r5 = s / (2 * math.sin(math.radians(36)))
    cx, cy = tx, ty + r5
    p = [(cx + r5 * math.cos(math.radians(-90 + 72 * k)),
          cy + r5 * math.sin(math.radians(-90 + 72 * k))) for k in range(5)]

    if kind == "imidazol-4-yl":
        # p0 C4 · p1 C5 · p2 N1(H) · p3 C2 · p4 N3 ; Doppelbindungen C4=C5, C2=N3
        orders = [2, 1, 1, 2, 1]
        for k in range(5):
            d.bond(p[k], p[(k + 1) % 5], orders[k], inner=(cx, cy))
        _ring_nh(d, p[2], (cx, cy))
        d.label(*p[4], "N")
        return

    if kind == "indol-3-yl":
        # p0 C3 · p1 C3a · p2 C7a · p3 N1(H) · p4 C2 ; C2=C3 im Fünfring
        d.bond(p[4], p[0], 2, inner=(cx, cy))
        d.bond(p[0], p[1])
        d.bond(p[2], p[3])
        d.bond(p[3], p[4])
        a, b = p[1], p[2]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ex, ey = b[0] - a[0], b[1] - a[1]
        n = math.hypot(ex, ey)
        nx, ny = -ey / n, ex / n
        if (mx - cx) * nx + (my - cy) * ny < 0:
            nx, ny = -nx, -ny
        hx, hy = mx + nx * s * COS30, my + ny * s * COS30
        # Sechsring-Ecken ab C3a, von C7a weg: C3a, C4, C5, C6, C7, C7a
        ang_a = math.atan2(a[1] - hy, a[0] - hx)
        ang_b = math.atan2(b[1] - hy, b[0] - hx)
        step = math.radians(60) if _angle_diff(ang_b, ang_a) < 0 else -math.radians(60)
        hexv = [(hx + s * math.cos(ang_a + step * k), hy + s * math.sin(ang_a + step * k))
                for k in range(6)]
        hex_orders = [1, 2, 1, 2, 1, 2]  # C3a-C4, C4=C5, C5-C6, C6=C7, C7-C7a, C7a=C3a
        for k in range(6):
            d.bond(hexv[k], hexv[(k + 1) % 6], hex_orders[k], inner=(hx, hy))
        _ring_nh(d, p[3], (cx, cy))
        # Indol-Benzolteil: hexv = C3a, C4, C5, C6, C7, C7a
        for pos, label in subs.items():
            _substituent(d, hexv[int(pos) - 3], (hx, hy), label)
        return

    raise ValueError(f"Unbekannter Ringtyp: {kind}")


def _substituent(d: Drawing, atom, center, label: str) -> None:
    """Substituent radial nach außen an einem Ringatom."""
    vx, vy = atom[0] - center[0], atom[1] - center[1]
    n = math.hypot(vx, vy)
    pos = (atom[0] + vx / n * L * 0.8, atom[1] + vy / n * L * 0.8)
    d.bond(atom, pos)
    d.label(*pos, label)


def _angle_diff(a: float, b: float) -> float:
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def _ring_nh(d: Drawing, pos, center) -> None:
    """Ring-N mit H, das H radial nach außen versetzt."""
    d.label(*pos, "N")
    vx, vy = pos[0] - center[0], pos[1] - center[1]
    n = math.hypot(vx, vy)
    d.label(pos[0] + vx / n * FONT * 1.05, pos[1] + vy / n * FONT * 1.05, "H")


def _side_chain(d: Drawing, chain: list[dict]) -> None:
    prev = (0.0, 0.0)
    y = 0.0
    for node in chain:
        if "ring" in node:
            top = (0.0, y + L * 0.92)
            d.bond(prev, top)
            _ring(d, node["ring"], top, node.get("subs"))
            return
        y += L
        cur = (0.0, y)
        d.bond(prev, cur)
        if "left" in node:
            d.bond(cur, (-L, y))
            d.label(-L, y, node["left"])
        if "right" in node:
            d.bond(cur, (L, y))
            d.label(L, y, node["right"])
        if "fork" in node:
            left, right = node["fork"]
            lp = (-L * COS30, y + L * 0.5)
            rp = (L * COS30, y + L * 0.5)
            d.bond(cur, lp, left["bond"])
            d.bond(cur, rp, right["bond"])
            d.label(*lp, left["label"])
            d.label(*rp, right["label"])
        d.label(*cur, node.get("label", "C"))
        prev = cur


def _proline(d: Drawing, hydroxy: bool = False) -> None:
    # Pyrrolidinring: Cα – N – Cδ – Cγ – Cβ – Cα ; N trägt H (sekundäre Aminogruppe).
    # hydroxy=True: 4-Hydroxyprolin, OH am Cγ (Stereochemie am C4 nicht dargestellt).
    ca, n = (0.0, 0.0), (-L, 0.0)
    cd, cg, cb = (-L * 1.3, L * 1.05), (-L * 0.62, L * 1.85), (0.0, L)
    d.bond(ca, (L, 0.0))
    for a, b in ((ca, n), (n, cd), (cd, cg), (cg, cb), (cb, ca)):
        d.bond(a, b)
    d.label(*ca, "C")
    d.label(L, 0.0, "H")
    d.label(*n, "HN")
    d.label(*cd, "H2C")
    d.label(*cb, "CH2")
    if hydroxy:
        oh = (cg[0], cg[1] + L * 0.8)
        d.bond(cg, oh)
        d.label(*cg, "CH")
        d.label(*oh, "OH")
    else:
        d.label(*cg, "CH2")


def fischer_svg(front_content: dict) -> str:
    d = Drawing()
    _carboxyl_head(d)
    if front_content.get("special") in ("proline", "hydroxyproline"):
        _proline(d, hydroxy=front_content["special"] == "hydroxyproline")
    else:
        _alpha_center(d)
        _side_chain(d, front_content.get("side_chain", []))
    return d.svg()
