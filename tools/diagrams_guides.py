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


def call_flow():
    d = Diagram("c1-call-flow", 1100, 300, "How a CTO-level SRE call usually flows")
    steps = [("1 · Intro\n2–3 min\nyour 60–90 s intro", "blue"),
             ("2 · Your experience\n10–15 min\n\"why?\" on your CV", "purple"),
             ("3 · Open scenarios\n10–15 min\n\"the site is slow…\"", "orange"),
             ("4 · Culture\n5–10 min\nconflict, mistakes", "yellow"),
             ("5 · Your questions\n5 min\npick 2–3", "green")]
    for i, (label, c) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 215, 60, 195, 90, label, c, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.group("mind", 20, 180, 1060, 100, "Mindset: a conversation between two engineers, not an exam", "gray", size=12)
    for i, t in enumerate(["Think out loud", "Pausing is fine", "1–2 min answer,\nthen offer depth",
                           "Say \"I\" for your work", "Only say what\nyou can defend"]):
        d.box(f"m{i}", 35 + i * 210, 215, 195, 50, t, "white", size=11, bold_first=False)
    return d


def answer_frameworks():
    d = Diagram("c2-answer-frameworks", 1100, 330, "Two shapes for any open question")
    d.text("t1", 20, 45, 700, 24, "Scenario or design: \"How would you…\", \"The system is down…\"",
           size=13, bold=True, align="left")
    rows = [("Clarify\nusers? down or slow?\nwhat changed?", "Impact first\nbig? MITIGATE first:\nrollback, scale", "Options\nA vs B, with\ntrade-offs",
             "Decide\npick one and\nsay why", "Measure\nalert or SLO +\nblameless postmortem"),
            ("Situation\n1–2 lines\nof context", "Task\nwhat YOU\nowned", "Action\nwhat YOU did,\nstep by step",
             "Result\na number if\npossible", "Learning\n\"what I changed\nafter this\"")]
    colours = [["purple", "red", "orange", "blue", "green"], ["gray", "gray", "blue", "green", "yellow"]]
    for r, row in enumerate(rows):
        y = 75 + r * 140
        for i, label in enumerate(row):
            d.box(f"r{r}{i}", 20 + i * 215, y, 195, 80, label, colours[r][i], size=11)
            if i:
                d.edge(f"r{r}{i - 1}", f"r{r}{i}")
    d.text("t2", 20, 185, 700, 24, "Experience: \"Tell me about a time…\" (STAR + Learning)", size=13, bold=True, align="left")
    return d


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


ALL = [call_flow, answer_frameworks, slo_error_budget]

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
