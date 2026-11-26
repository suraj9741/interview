#!/usr/bin/env python3
"""drawio_aws4: draw.io's own AWS library (mxgraph.aws4 stencils) as SVG vectors, standard library only.

The diagrams use draw.io's AWS shapes in the draw.io model (shape=mxgraph.aws4.<name>), so draw.io shows
them as normal library shapes. GitHub can't run draw.io, so the SVG preview needs the same shapes as plain
vector paths. This module turns a stencil from draw.io's aws4 stencil set into an SVG <g> element.

No icon files live in this repository. The stencil set is downloaded once into a local cache
(~/.cache/drawio-aws4/aws4.json, not committed): draw.io's aws4 stencils, taken from the npm package
@markdown-viewer/drawio2svg 1.5.5 (resources/stencils/aws4.json), because draw.io's own stencil file is not
published on its own. Set DRAWIO_AWS4_STENCILS to a local aws4.json to skip the download.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import tarfile
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

TARBALL = "https://registry.npmjs.org/@markdown-viewer/drawio2svg/-/drawio2svg-1.5.5.tgz"
TARBALL_SHA256 = "852288d9b3cd7b7566275eaf3602da418ac1e4d06de923cbad1b138a7db9ff21"
CACHE = Path(os.environ.get("DRAWIO_AWS4_STENCILS", Path.home() / ".cache" / "drawio-aws4" / "aws4.json"))

def _decode(bundle: dict) -> dict:
    raw = zlib.decompress(base64.b64decode(bundle["data"])).decode("utf-8")  # zlib-wrapped deflate
    if raw.startswith("%"):
        raw = urllib.parse.unquote(raw)
    return json.loads(raw)


def _download(sets=("aws4", "kubernetes")) -> None:
    """Fetch the pinned package once and cache the stencil sets this repo uses (aws4, kubernetes)."""
    data = urllib.request.urlopen(TARBALL, timeout=60).read()
    if hashlib.sha256(data).hexdigest() != TARBALL_SHA256:
        raise RuntimeError("drawio_aws4: stencil package checksum mismatch, refusing to use it")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for name in sets:
            bundle = json.load(tar.extractfile(f"package/resources/stencils/{name}.json"))
            out = CACHE if name == "aws4" else CACHE.parent / f"{name}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(_decode(bundle)), encoding="utf-8")


_sets: dict[str, dict] = {}


def stencil_set(name: str = "aws4") -> dict:
    """One draw.io stencil set by name: aws4 (AWS library) or kubernetes (Kubernetes icons)."""
    if name not in _sets:
        path = CACHE if name == "aws4" else CACHE.parent / f"{name}.json"
        if not path.exists():
            _download()
        _sets[name] = json.loads(path.read_text(encoding="utf-8"))
    return _sets[name]


def stencils() -> dict:
    return stencil_set("aws4")


def has(name: str) -> bool:
    return f"aws4.{name}" in stencils()


def _num(v: float, digits: int = 3) -> str:
    t = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return "0" if t in ("", "-0") else t


def _cmd(cmd: list) -> str:
    """One path command, 1 decimal (stencils are ~44 units wide, so 0.1 unit is far below a pixel)."""
    out = cmd[0]
    for v in cmd[1:]:
        t = _num(v, 1)
        out += t if (out[-1].isalpha() or t.startswith("-")) else " " + t
    return out


def stencil_symbol(name: str, fill: str, family: str = "aws4") -> tuple[str, str]:
    """(id, <symbol>) for stencil mxgraph.aws4.<name> painted in `fill`, in the stencil's own units.

    Use it as <use href="#id" x= y= width= height=/>: the viewBox keeps the aspect and centres the shape,
    like draw.io does. One symbol per shape and colour, so repeated icons cost a few bytes each."""
    st = stencil_set(family)[f"{family}.{name}"]
    sid = f"{family}-{name}-{fill.lstrip('#').lower()}"
    out, d, color, alpha = [], [], fill, None
    for item in st.get("background", []) + st.get("foreground", []):
        if isinstance(item, dict) and "path" in item:
            d += [_cmd(cmd) for cmd in item["path"]]
        elif isinstance(item, dict) and "fillColor" in item:
            color = item["fillColor"]
        elif isinstance(item, dict) and "alpha" in item:
            alpha = item["alpha"]
        elif item in ("fill", "fillStroke", "stroke") and d:
            paint = f'fill="{color}"' if item != "stroke" else f'fill="none" stroke="{color}"'
            op = f' fill-opacity="{alpha}"' if alpha not in (None, 1) else ""
            out.append(f'<path d="{"".join(d)}" {paint}{op}/>')
            d = []
    return sid, f'<symbol id="{sid}" viewBox="0 0 {_num(st["width"])} {_num(st["height"])}">{"".join(out)}</symbol>'
