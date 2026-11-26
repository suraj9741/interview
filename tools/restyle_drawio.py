#!/usr/bin/env python3
"""restyle_drawio: redraw existing .drawio.svg diagrams in the current drawio_svg THEME (the AWS look).

Every diagram in this repo was made by tools/drawio_svg.py, so its embedded draw.io model can be read back
into the same Diagram calls (box / group / text / icon / edge) that built it. This script does that and saves
the diagram again, so the picture gets the new style while every label, position and arrow stays the same.

Safety checks, per file:
  1. Round trip: read back with THEME = "classic" and re-render; the result must be byte-identical to the
     file, which proves the reader understood every shape. A file that fails is left untouched.
  2. Words: every word of every label in the old model must still be in the new model (no fact dropped).

Usage:
  python3 tools/restyle_drawio.py FILE_OR_DIR...        restyle in place (only files that pass both checks)
  python3 tools/restyle_drawio.py --check FILE_OR_DIR... report only, write nothing
"""
from __future__ import annotations

import collections
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import drawio_svg  # noqa: E402
from drawio_svg import (DRAWIO_AWS, DRAWIO_AWS_GROUP, DRAWIO_K8S, PALETTE, PALETTE_AWS, PALETTE_CLASSIC,  # noqa: E402
                        Diagram, drawio_aws_style)

ICON_BY_STYLE = {}
for _name in list(DRAWIO_AWS) + list(DRAWIO_K8S):
    ICON_BY_STYLE[drawio_aws_style(_name)] = _name
GROUP_BY_STENCIL = {(shape, color.lower()): name for name, (shape, color) in DRAWIO_AWS_GROUP.items()}
COLOR_BY_PAINT = {}
for _table in (PALETTE, PALETTE_CLASSIC, PALETTE_AWS):
    for _name, (_fill, _stroke) in _table.items():
        COLOR_BY_PAINT.setdefault((_fill.lower(), _stroke.lower()), _name)


def _style(s: str) -> dict:
    out = {}
    for part in s.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
        elif part:
            out[part] = True
    return out


def _lines(value: str):
    """(lines, bold_first, italic) from a cell value written by Diagram._mx_value."""
    italic = value.startswith("<i>") and value.endswith("</i>")
    if italic:
        value = value[3:-4]
    parts = value.split("<br>") if value else []
    bold_first = bool(parts) and parts[0].startswith("<b>") and parts[0].endswith("</b>")
    if bold_first:
        parts[0] = parts[0][3:-4]
    return [html.unescape(p) for p in parts], bold_first, italic


def _num(v: str):
    return float(v) if "." in v or "e" in v else int(v)


def read(path: Path) -> Diagram:
    """Rebuild the Diagram (with the current THEME) from a .drawio.svg made by drawio_svg.py."""
    svg = ET.fromstring(path.read_text(encoding="utf-8"))
    mx = ET.fromstring(svg.get("content"))
    dia = mx.find("diagram")
    model = dia.find("mxGraphModel")
    d = Diagram(dia.get("name"), _num(model.get("pageWidth")), _num(model.get("pageHeight")))
    cells = [c for c in model.find("root") if c.get("id") not in ("0", "1")]
    by_id = {c.get("id"): c for c in cells}
    squares = []
    for c in cells:
        if c.get("vertex") != "1":
            continue
        cid = c.get("id")[2:]
        g = c.find("mxGeometry")
        x, y, w, h = (_num(g.get(k)) for k in ("x", "y", "width", "height"))
        st = _style(c.get("style", ""))
        lines, bold_first, italic = _lines(c.get("value", ""))
        label = "\n".join(lines)
        if "shape" in st and st["shape"].startswith("mxgraph.") and "grIcon" not in st or (
                st.get("shape") == "mxgraph.aws4.group" and st.get("fillColor") == "none" and "grIconSize" in st):
            if cid.endswith("-icon") and f"v-{cid[:-5]}" in by_id:
                continue  # drawn by its box
            if st.get("shape") == "mxgraph.aws4.group":
                name = GROUP_BY_STENCIL[(st["grIcon"].split(".")[-1], st["strokeColor"].lower())]
            else:
                name = ICON_BY_STYLE[c.get("style")]
            d.icon(cid, x, y, name, w)
            continue
        size = _num(st.get("fontSize", 12))
        align, valign = st.get("align", "center"), st.get("verticalAlign", "middle")
        bold = st.get("fontStyle") == "1"
        if "text" in st:
            d.box(cid, x, y, w, h, label, "none", shape="text", size=size, bold=bold, italic=italic, align=align,
                  valign=valign, bold_first=bold_first, auto_icon=False)
            continue
        dashed = st.get("dashed") == "1"
        if st.get("shape") == "mxgraph.aws4.group":
            color = _fill_name(st.get("fillColor", ""))
        else:
            color = COLOR_BY_PAINT[(st.get("fillColor", "").lower(), st.get("strokeColor", "").lower())]
        icon_cell = by_id.get(f"v-{cid}-icon")
        icon = icon_size = None
        if icon_cell is not None:
            ist = _style(icon_cell.get("style", ""))
            if ist.get("shape") == "mxgraph.aws4.group":
                icon = GROUP_BY_STENCIL[(ist["grIcon"].split(".")[-1], ist["strokeColor"].lower())]
            else:
                icon = ICON_BY_STYLE[icon_cell.get("style")]
            icon_size = _num(icon_cell.find("mxGeometry").get("width"))
        if st.get("shape") == "mxgraph.aws4.group":  # draw.io AWS container
            name = GROUP_BY_STENCIL[(st["grIcon"].split(".")[-1], st["strokeColor"].lower())]
            d.group(cid, x, y, w, h, label, color, dashed=dashed, size=size, align=align, icon=name)
            continue
        shape = "ellipse" if "ellipse" in st else "cylinder" if st.get("shape") == "cylinder3" else "rect"
        square = st.get("rounded") == "0"
        if square and bold and valign == "top" and align == "left" and (
                icon is None or (icon_size == drawio_svg.GROUP_ICON and _num(icon_cell.find("mxGeometry").get("x")) == x)):
            d.group(cid, x, y, w, h, label, color, dashed=dashed, size=size, icon=icon, aws=True)  # aws=True group
            continue
        kids, texts = _children(c, cells)
        leaf = not kids
        if shape == "rect" and not square and bold and valign == "top" and not italic and not leaf:
            d.group(cid, x, y, w, h, label, color, dashed=dashed, size=size, valign=valign, align=align,
                    icon=icon, icon_size=icon_size or 24)  # a container: AWS container look in the new theme
            continue
        d.box(cid, x, y, w, h, label, color, shape=shape, size=size, bold=bold, italic=italic, dashed=dashed,
              valign=valign, align=align, bold_first=bold_first, icon=icon, icon_size=icon_size or 32,
              auto_icon=leaf and _icon_room(c, texts))
        if square:
            squares.append(cid)
    for cid in squares:
        d._by_id[cid]["square"] = True
    for c in cells:
        if c.get("edge") != "1":
            continue
        st = _style(c.get("style", ""))
        lines, _, _ = _lines(c.get("value", ""))
        pts = [(_num(p.get("x")), _num(p.get("y"))) for p in c.iter("mxPoint")]
        d.edge(c.get("source")[2:], c.get("target")[2:], "\n".join(lines) or None, dashed=st.get("dashed") == "1",
               both=st.get("startArrow") == "classic", points=pts, size=_num(st.get("fontSize", 10)))
    return d


def _fill_name(fill: str) -> str:
    for table in (PALETTE, PALETTE_CLASSIC, PALETTE_AWS):
        for name, (f, _) in table.items():
            if f.lower() == fill.lower():
                return name
    raise KeyError(fill)


def _children(cell, cells):
    """(shapes, texts) drawn inside this cell's rectangle (a box that holds shapes is a container)."""
    g = cell.find("mxGeometry")
    x, y, w, h = (float(g.get(k)) for k in ("x", "y", "width", "height"))
    shapes, texts = [], []
    for o in cells:
        if o is cell or o.get("vertex") != "1" or o.get("id", "").endswith("-icon"):
            continue
        og = o.find("mxGeometry")
        ox, oy, ow, oh = (float(og.get(k)) for k in ("x", "y", "width", "height"))
        if ox >= x and oy >= y and ox + ow <= x + w and oy + oh <= y + h and (ow * oh) < w * h * 0.9:
            (texts if o.get("style", "").startswith("text;") else shapes).append((ox, oy, ow, oh))
    return shapes, texts


def _icon_room(cell, texts) -> bool:
    """False when a text label inside the box sits where the auto icon would go (left 46 px)."""
    x = float(cell.find("mxGeometry").get("x"))
    return all(tx >= x + 46 for tx, _, _, _ in texts)


WORD = re.compile(r"[^\s]+")


def words(svg_text: str) -> collections.Counter:
    mx = ET.fromstring(ET.fromstring(svg_text).get("content"))
    c = collections.Counter()
    for cell in mx.iter("mxCell"):
        lines, _, _ = _lines(cell.get("value", ""))
        for line in lines:
            c.update(WORD.findall(line))
    return c


def restyle(path: Path, write: bool) -> str:
    old = path.read_text(encoding="utf-8")
    empty = re.compile(r'<text [^>]*>(<tspan [^>]*></tspan>)?</text>')  # empty-label text, invisible either way
    ok, err = False, ""
    for theme in ("classic", "aws"):  # an old-look file, or one already in the new look
        drawio_svg.THEME = theme
        try:
            ok = empty.sub("", read(path).to_svg()) == empty.sub("", old)
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
        finally:
            drawio_svg.THEME = "aws"
        if ok:
            break
    if not ok:
        return f"SKIP (round trip differs{'; ' + err if err else ''})"
    d = read(path)
    new = d.to_svg()
    missing = words(old) - words(new)
    if missing:
        return f"SKIP (words missing: {dict(missing)})"
    if new == old:
        return "unchanged"
    if write:
        ET.fromstring(new)
        path.write_text(new, encoding="utf-8")
    return "restyled" + (f" ({len(d.warnings)} fit warnings)" if d.warnings else "")


def main(argv):
    write = "--check" not in argv
    targets = [Path(a) for a in argv if not a.startswith("--")]
    files = []
    for t in targets:
        files += sorted(t.rglob("*.drawio.svg")) if t.is_dir() else [t]
    stats = collections.Counter()
    for f in files:
        r = restyle(f, write)
        stats[r.split(" ")[0]] += 1
        if not r.startswith(("restyled", "unchanged")) or "warn" in r:
            print(f"{r:40.200s}  {f}")
    print(dict(stats))


if __name__ == "__main__":
    main(sys.argv[1:])
