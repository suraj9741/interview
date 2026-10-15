#!/usr/bin/env python3
"""Create the draw.io diagrams used by the interview guides and plans in interview-prep/:
cto-sre-discussion-guide.md (c*), devops-interview-prep-plan.md and study-plan-oct-5-9.md (p*).

Run once:  python3 tools/diagrams_guides.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def slo_error_budget():
    d = Diagram("c3-slo-error-budget", 1100, 330, "SLI → SLO → error budget: speed vs stability as data")
    d.box("sli", 20, 60, 260, 80, "SLI: what you measure\n% of requests that succeed\n(fast enough)", "blue", size=11)
    d.box("slo", 330, 60, 260, 80, "SLO: the target\n99.9% over 30 days\n(not 100%: too expensive)", "purple", size=11)
    d.box("eb", 640, 60, 440, 80, "Error budget: the 0.1% you may fail\n30 days × 24 h × 60 min × 0.001 ≈ 43 minutes",
          "yellow", size=11)
    d.edge("sli", "slo")
    d.edge("slo", "eb")
    d.box("left", 400, 190, 330, 70, "Budget left\n→ ship faster, run experiments", "green", size=11)
    d.box("burnt", 750, 190, 330, 70, "Budget burnt\n→ slow releases, fix reliability first", "red", size=11)
    d.edge("eb", "left")
    d.edge("eb", "burnt")
    d.box("words", 20, 180, 340, 130, "Words to use (only if you can explain them)\nGolden signals: latency, traffic, errors, saturation\n"
          "Toil · blast radius · graceful degradation\nMTTD / MTTR · DORA metrics", "white", size=11, align="left")
    return d


ALL = [slo_error_budget]

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
