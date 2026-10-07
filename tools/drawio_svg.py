#!/usr/bin/env python3
"""drawio_svg: build editable draw.io diagrams as .drawio.svg files, using only the standard library.

A .drawio.svg file is a normal SVG picture (so it renders inside Markdown in the VS Code
preview and on GitHub) that also carries the draw.io diagram XML in its `content`
attribute (so draw.io desktop, app.diagrams.net and the VS Code "Draw.io Integration"
extension open it for editing, and re-render the picture when you save).

Use this only to CREATE a diagram. After that, edit the .drawio.svg in draw.io directly;
the per-topic generator scripts refuse to overwrite an existing file unless --force is given.
"""
from __future__ import annotations

import html
import math
import xml.etree.ElementTree as ET
from pathlib import Path

PALETTE = {  # name: (fill, stroke), the draw.io default colour set
    "blue": ("#dae8fc", "#6c8ebf"),
    "green": ("#d5e8d4", "#82b366"),
    "yellow": ("#fff2cc", "#d6b656"),
    "orange": ("#ffe6cc", "#d79b00"),
    "red": ("#f8cecc", "#b85450"),
    "purple": ("#e1d5e7", "#9673a6"),
    "gray": ("#f5f5f5", "#666666"),
    "white": ("#ffffff", "#666666"),
    "outline": ("none", "#666666"),
    "none": ("none", "none"),
}
INK = "#1a1a1a"
LINE = "#555555"
FONT = "Helvetica, Arial, sans-serif"
CHAR_W = 0.56  # rough average glyph width, as a fraction of font size (fit warnings only)
LINE_H = 1.3   # line height, as a fraction of font size


def _q(s: str) -> str:
    return html.escape(str(s), quote=True)


def _center(v: dict) -> tuple[float, float]:
    return v["x"] + v["w"] / 2, v["y"] + v["h"] / 2


def _perimeter(v: dict, tx: float, ty: float) -> tuple[float, float]:
    """Point where the ray from v's centre towards (tx, ty) leaves v's outline."""
    cx, cy = _center(v)
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    hw, hh = v["w"] / 2, v["h"] / 2
    if v["shape"] == "ellipse":
        s = 1 / math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
    else:
        s = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
    return cx + dx * s, cy + dy * s


def _midpoint(pts: list[tuple[float, float]]) -> tuple[float, float]:
    segs = [(a, b, math.dist(a, b)) for a, b in zip(pts, pts[1:])]
    half = sum(length for _, _, length in segs) / 2
    for a, b, length in segs:
        if length > 0 and half <= length:
            f = half / length
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        half -= length
    return pts[-1]


def _svg_text(lines, x, y, w, h, size, valign, align, bold, bold_first, italic, top_inset=0.0):
    lh = size * LINE_H
    n = len(lines)
    if valign == "top":
        first_c = y + 6 + lh / 2
    elif valign == "bottom":
        first_c = y + h - 6 - lh * (n - 0.5)
    else:
        first_c = y + top_inset + (h - top_inset - lh * n) / 2 + lh / 2
    ax, anchor = (x + 8, "start") if align == "left" else (x + w / 2, "middle")
    italic_attr = ' font-style="italic"' if italic else ""
    out = [f'<text font-family="{FONT}" font-size="{size}" fill="{INK}" text-anchor="{anchor}"{italic_attr}>']
    for i, line in enumerate(lines):
        weight = ' font-weight="bold"' if bold or (bold_first and i == 0 and n > 1) else ""
        out.append(f'<tspan x="{ax:.1f}" y="{first_c + i * lh + size * 0.35:.1f}"{weight}>'
                   f'{html.escape(line, quote=False)}</tspan>')
    out.append("</text>")
    return "".join(out)


class Diagram:
    def __init__(self, name: str, width: int, height: int, title: str | None = None):
        self.name, self.width, self.height = name, width, height
        self.vertices: list[dict] = []
        self.edges: list[dict] = []
        self.warnings: list[str] = []
        self._by_id: dict[str, dict] = {}
        if title:
            self.text("title", 0, 8, width, 28, title, size=16, bold=True)

    # ---- building ---------------------------------------------------------------
    def box(self, id, x, y, w, h, label, color="blue", *, shape="rect", size=12, bold=False,
            italic=False, dashed=False, valign="middle", align="center", bold_first=True):
        if id in self._by_id:
            raise ValueError(f"{self.name}: duplicate id {id!r}")
        v = dict(id=id, x=x, y=y, w=w, h=h, lines=label.split("\n"), color=color, shape=shape,
                 size=size, bold=bold, italic=italic, dashed=dashed, valign=valign, align=align,
                 bold_first=bold_first)
        self.vertices.append(v)
        self._by_id[id] = v
        self._check_fit(v)
        return id

    def group(self, id, x, y, w, h, label, color="gray", *, dashed=False, size=13,
              valign="top", align="center"):
        """A labelled region. Add it BEFORE the boxes inside it, so it is drawn behind them."""
        return self.box(id, x, y, w, h, label, color, size=size, bold=True, dashed=dashed,
                        valign=valign, align=align)

    def text(self, id, x, y, w, h, label, *, size=12, bold=False, italic=False, align="center"):
        return self.box(id, x, y, w, h, label, "none", shape="text", size=size, bold=bold,
                        italic=italic, align=align, bold_first=False)

    def edge(self, src, tgt, label=None, *, dashed=False, both=False, points=None, size=10):
        for end in (src, tgt):
            if end not in self._by_id:
                raise KeyError(f"{self.name}: edge end {end!r} is not a vertex")
        self.edges.append(dict(id=f"e{len(self.edges)}", src=src, tgt=tgt,
                               lines=label.split("\n") if label else [], dashed=dashed,
                               both=both, points=list(points or []), size=size))

    def _check_fit(self, v):
        pad = 0 if v["shape"] == "text" else 12
        for i, line in enumerate(v["lines"]):
            bold = v["bold"] or (v["bold_first"] and i == 0 and len(v["lines"]) > 1)
            est = len(line) * v["size"] * CHAR_W * (1.08 if bold else 1.0)
            if est > v["w"] - pad:
                self.warnings.append(f"{self.name}/{v['id']}: {line!r} needs ~{est:.0f}px, has {v['w'] - pad}px")
        if v["valign"] == "middle":
            need = len(v["lines"]) * v["size"] * LINE_H + (0 if v["shape"] == "text" else 6)
            need += 16 if v["shape"] == "cylinder" else 0
            if need > v["h"]:
                self.warnings.append(f"{self.name}/{v['id']}: {len(v['lines'])} lines need ~{need:.0f}px, has {v['h']}px")

    # ---- SVG rendering ------------------------------------------------------------
    def _route(self, e) -> list[tuple[float, float]]:
        s, t = self._by_id[e["src"]], self._by_id[e["tgt"]]
        first = e["points"][0] if e["points"] else _center(t)
        last = e["points"][-1] if e["points"] else _center(s)
        return [_perimeter(s, *first), *e["points"], _perimeter(t, *last)]

    @staticmethod
    def _svg_vertex(v) -> str:
        fill, stroke = PALETTE[v["color"]]
        x, y, w, h = v["x"], v["y"], v["w"], v["h"]
        dash = ' stroke-dasharray="6 4"' if v["dashed"] else ""
        paint = f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}'
        out, inset = [], 0.0
        if v["shape"] == "rect":
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" {paint}/>')
        elif v["shape"] == "ellipse":
            out.append(f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" {paint}/>')
        elif v["shape"] == "cylinder":
            r, ry = w / 2, 8
            out.append(f'<path d="M{x},{y + ry} L{x},{y + h - ry} A{r},{ry} 0 0 0 {x + w},{y + h - ry} '
                       f'L{x + w},{y + ry}" {paint}/>')
            out.append(f'<ellipse cx="{x + r}" cy="{y + ry}" rx="{r}" ry="{ry}" {paint}/>')
            inset = 2 * ry
        out.append(_svg_text(v["lines"], x, y, w, h, v["size"], v["valign"], v["align"], v["bold"],
                             v["bold_first"], v["italic"], top_inset=inset))
        return "".join(out)

    @staticmethod
    def _svg_edge(e, pts) -> str:
        d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        dash = ' stroke-dasharray="6 4"' if e["dashed"] else ""
        start = ' marker-start="url(#arrow)"' if e["both"] else ""
        return (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"{dash}{start} '
                f'marker-end="url(#arrow)"/>')

    @staticmethod
    def _svg_edge_label(e, pts) -> str:
        if not e["lines"]:
            return ""
        mx, my = _midpoint(pts)
        size = e["size"]
        w = max(len(line) for line in e["lines"]) * size * CHAR_W + 8
        h = size * LINE_H * len(e["lines"]) + 4
        x, y = mx - w / 2, my - h / 2
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff"/>'
                + _svg_text(e["lines"], x, y, w, h, size, "middle", "center", False, False, False))

    # ---- draw.io XML ----------------------------------------------------------------
    @staticmethod
    def _mx_value(lines, bold_first, italic) -> str:
        parts = [html.escape(line, quote=False) for line in lines]
        if bold_first and len(parts) > 1:
            parts[0] = f"<b>{parts[0]}</b>"
        value = "<br>".join(parts)
        return f"<i>{value}</i>" if italic else value

    @staticmethod
    def _mx_vertex_style(v) -> str:
        fill, stroke = PALETTE[v["color"]]
        common = (f"whiteSpace=wrap;html=1;fontSize={v['size']};fontColor={INK};fontFamily=Helvetica;"
                  f"align={v['align']};verticalAlign={v['valign']};")
        if v["shape"] == "text":
            style = "text;strokeColor=none;fillColor=none;" + common
        else:
            shape = {"rect": "rounded=1;absoluteArcSize=1;arcSize=16;",
                     "ellipse": "ellipse;",
                     "cylinder": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;"}[v["shape"]]
            style = shape + f"fillColor={fill};strokeColor={stroke};strokeWidth=1.5;" + common
        if v["dashed"]:
            style += "dashed=1;dashPattern=6 4;"
        if v["bold"]:
            style += "fontStyle=1;"
        if v["align"] == "left":
            style += "spacingLeft=6;"
        if v["valign"] in ("top", "bottom"):
            style += "spacingTop=2;spacingBottom=2;"
        return style

    @staticmethod
    def _mx_edge_style(e) -> str:
        style = (f"html=1;rounded=0;endArrow=classic;endFill=1;strokeColor={LINE};strokeWidth=1.5;"
                 f"fontSize={e['size']};fontColor={INK};labelBackgroundColor=#ffffff;")
        style += "startArrow=classic;startFill=1;" if e["both"] else "startArrow=none;"
        if e["dashed"]:
            style += "dashed=1;dashPattern=6 4;"
        return style

    def to_mxfile(self) -> str:
        cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
        for v in self.vertices:
            value = self._mx_value(v["lines"], v["bold_first"] and not v["bold"], v["italic"])
            cells.append(f'<mxCell id="v-{_q(v["id"])}" value="{_q(value)}" style="{_q(self._mx_vertex_style(v))}" '
                         f'vertex="1" parent="1"><mxGeometry x="{v["x"]}" y="{v["y"]}" width="{v["w"]}" '
                         f'height="{v["h"]}" as="geometry"/></mxCell>')
        for e in self.edges:
            pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in e["points"])
            geometry = (f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
                        if pts else '<mxGeometry relative="1" as="geometry"/>')
            value = self._mx_value(e["lines"], False, False)
            cells.append(f'<mxCell id="{e["id"]}" value="{_q(value)}" style="{_q(self._mx_edge_style(e))}" '
                         f'edge="1" parent="1" source="v-{_q(e["src"])}" target="v-{_q(e["tgt"])}">'
                         f'{geometry}</mxCell>')
        model = (f'<mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                 f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.width}" '
                 f'pageHeight="{self.height}" math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel>')
        return (f'<mxfile host="drawio_svg.py" agent="drawio_svg.py" version="24.7.17" type="device">'
                f'<diagram id="{_q(self.name)}" name="{_q(self.name)}">{model}</diagram></mxfile>')

    def to_svg(self) -> str:
        routes = [(e, self._route(e)) for e in self.edges]
        body = ("".join(self._svg_vertex(v) for v in self.vertices)
                + "".join(self._svg_edge(e, pts) for e, pts in routes)
                + "".join(self._svg_edge_label(e, pts) for e, pts in routes))
        w, h = self.width, self.height
        return (f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}" content="{_q(self.to_mxfile())}">'
                f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                f'markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/>'
                f'</marker></defs><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>')

    # ---- output ---------------------------------------------------------------------
    def save(self, out_dir: Path, force: bool = False) -> Path | None:
        out = Path(out_dir) / f"{self.name}.drawio.svg"
        if out.exists() and not force:
            return None  # never overwrite a diagram that may have been edited in draw.io
        svg = self.to_svg()
        root = ET.fromstring(svg)               # the SVG must be well-formed
        model = ET.fromstring(root.get("content"))  # and so must the embedded draw.io XML
        assert model.find("./diagram/mxGraphModel/root") is not None, "draw.io model missing"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        return out
