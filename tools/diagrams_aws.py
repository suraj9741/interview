#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/aws-troubleshooting-playbook.md (a*).

Run once:  python3 tools/diagrams_aws.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def connectivity_path():
    d = Diagram("a1-aws-connectivity-check-order", 900, 520, "\"It can't connect\": check the path in this order, every time")
    steps = [
        ("dns", "1. DNS\nresolves to the right IP?\ndig / nslookup, Route 53 record", "blue"),
        ("rt", "2. Route table\n0.0.0.0/0 → IGW (public)\nor → NAT GW (private)", "purple"),
        ("sg", "3. Security group (stateful)\ninbound port + source allowed?\nreturn traffic automatic", "green"),
        ("nacl", "4. NACL (stateless)\ninbound AND outbound rules\nincl. ephemeral 1024–65535", "orange"),
        ("os", "5. Instance / OS\nfirewall (iptables, firewalld)\napp listening? ss -tlnp", "yellow"),
        ("app", "6. Application\nhealth endpoint, logs,\ndependencies (DB, API)", "red"),
    ]
    y = 55
    for i, (sid, label, col) in enumerate(steps):
        x = 20 if i % 2 == 0 else 470
        d.box(sid, x, y + (i // 2) * 110, 410, 80, label, col, size=11)
    for a, b in [("dns", "rt"), ("rt", "sg"), ("sg", "nacl"), ("nacl", "os"), ("os", "app")]:
        d.edge(a, b)
    d.box("tools", 20, 395, 860, 105,
          "Evidence that proves which layer is broken\n"
          "VPC Flow Logs: REJECT = SG/NACL blocked it · ACCEPT but no reply = OS/app problem · no record = routing/DNS\n"
          "Reachability Analyzer: tests the path between two resources without sending traffic\n"
          "ELB target health reason · CloudTrail: who changed the SG/route/NACL and when · CloudWatch metrics/logs",
          "white", size=11, align="left")
    return d


ALL = [connectivity_path]

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
