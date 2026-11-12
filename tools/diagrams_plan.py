#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/15-day-plan/ (d*).

Run once:  python3 tools/diagrams_plan.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "15-day-plan" / "diagrams"


def d1_pipeline():
    d = Diagram("d1-pipeline-and-permissions", 900, 470, "Day 1: how a pipeline flows, and how to read permissions")
    d.box("file", 20, 60, 150, 70, "app.log\n10,000 lines", "gray", size=11)
    d.box("grep", 200, 60, 150, 70, "grep -i error\nkeep matching lines", "blue", size=11)
    d.box("awk", 380, 60, 150, 70, "awk '{print $3}'\npick column 3", "purple", size=11)
    d.box("sort", 560, 60, 140, 70, "sort | uniq -c\ncount each value", "yellow", size=11)
    d.box("out", 730, 60, 150, 70, "> report.txt\nsave to a file", "green", size=11)
    d.edge("file", "grep", "stdin")
    d.edge("grep", "awk", "|")
    d.edge("awk", "sort", "|")
    d.edge("sort", "out")
    d.text("note", 20, 138, 860, 50,
           "Each | sends the output (stdout) of the left command into the input (stdin) of the right one.\n"
           "> overwrites a file, >> appends, 2> redirects errors.", size=11)
    d.group("perm", 20, 200, 860, 250, "ls -l output:   -rwxr-x---  1  suraj  dev  2048  Nov 12  deploy.sh", "white")
    d.box("type", 40, 250, 120, 80, "-\ntype\n- file / d dir", "gray", size=10)
    d.box("u", 180, 250, 150, 80, "rwx\nuser (owner)\n4+2+1 = 7", "blue", size=11)
    d.box("g", 350, 250, 150, 80, "r-x\ngroup\n4+0+1 = 5", "green", size=11)
    d.box("o", 520, 250, 150, 80, "---\nothers\n0+0+0 = 0", "red", size=11)
    d.box("cmd", 690, 250, 170, 80, "chmod 750 deploy.sh\nchown suraj:dev deploy.sh", "yellow", size=10)
    d.text("rwx", 40, 350, 820, 80,
           "r = 4 (read)   w = 2 (write)   x = 1 (execute)\n"
           "On a directory: r = list files, w = create/delete files, x = enter it (cd)\n"
           "Common: 644 files, 755 scripts/dirs, 600 private keys, 640 config with secrets", size=11)
    return d


ALL = [d1_pipeline]

if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in ALL:
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"{'wrote  ' if path else 'skipped'} {diagram.name}.drawio.svg"
              f"{'' if path else '  (exists; use --force to overwrite)'}")
    for w in warnings:
        print("WARN", w)
