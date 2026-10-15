#!/usr/bin/env python3
"""Build the networking diagrams from the modules in this folder.

    python3 build.py                 # create any diagram that doesn't exist yet
    python3 build.py --force         # regenerate all of them (overwrites edits made in draw.io)
    python3 build.py --module l2     # only the diagrams in l2.py
    python3 build.py --only 2.7-routing-decision --force

Each module (l1.py, l2.py, ...) defines one function per diagram and lists them in ALL.
The drawing helpers come from tools/drawio_svg.py at the repository root.
Once a diagram exists, you can edit the .drawio.svg in draw.io directly instead.
"""
import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))  # repo/tools, for drawio_svg


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing .drawio.svg files")
    ap.add_argument("--module", action="append", help="build only this module (repeatable)")
    ap.add_argument("--only", action="append", help="build only this diagram name (repeatable)")
    args = ap.parse_args()

    paths = sorted(p for p in HERE.glob("*.py") if p.name != "build.py")
    if args.module:
        paths = [p for p in paths if p.stem in args.module]
    names, warnings, written, skipped = set(), [], 0, 0
    for path in paths:
        for make in load(path).ALL:
            d = make()
            if d.name in names:
                sys.exit(f"duplicate diagram name {d.name!r} in {path.name}")
            names.add(d.name)
            if args.only and d.name not in args.only:
                continue
            warnings += d.warnings
            if d.save(OUT, force=args.force):
                written += 1
            else:
                skipped += 1
    for w in warnings:
        print("WARNING", w)
    print(f"{written} written, {skipped} skipped (already exist; use --force), {len(warnings)} warnings")
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
