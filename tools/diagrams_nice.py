#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/nice-actimize-sre-cheatsheet.md (n*).

Run once:  python3 tools/diagrams_nice.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def incident_lifecycle():
    d = Diagram("n1-incident-lifecycle", 1180, 420, "Production incident: from alert to permanent fix (ITIL)")
    d.box("detect", 20, 60, 170, 80, "1. Detect\nalert / user ticket\nmonitoring", "blue", size=11)
    d.box("triage", 220, 60, 170, 80, "2. Triage\nimpact + urgency\n= priority P1–P4", "purple", size=11)
    d.box("mitigate", 420, 60, 170, 80, "3. Mitigate\nrestore service first\nrestart / rollback", "orange", size=11)
    d.box("comms", 620, 60, 170, 80, "4. Communicate\nbridge call, updates\nevery 30 min (P1)", "yellow", size=11)
    d.box("resolve", 820, 60, 170, 80, "5. Resolve + verify\nmetrics normal\nuser confirms", "green", size=11)
    d.box("close", 1010, 60, 150, 80, "Close incident\nticket updated", "gray", size=11)
    for a, b in [("detect", "triage"), ("triage", "mitigate"), ("mitigate", "comms"),
                 ("comms", "resolve"), ("resolve", "close")]:
        d.edge(a, b)
    d.group("itil", 20, 190, 1140, 210, "ITIL: incident ≠ problem ≠ change", "white", dashed=True)
    d.box("inc", 50, 230, 330, 140, "Incident management\nGoal: restore service fast\nOne outage = one incident\nMeasured by MTTR, SLA", "orange", size=11)
    d.box("prob", 425, 230, 330, 140, "Problem management\nGoal: find root cause (RCA)\n5 Whys, timeline, fishbone\nKnown error + workaround", "red", size=11)
    d.box("chg", 800, 230, 330, 140, "Change management\nGoal: apply the fix safely\nCR, CAB approval, test,\nrollback plan, change window", "green", size=11)
    d.edge("inc", "prob", "recurring / P1")
    d.edge("prob", "chg", "permanent fix")
    d.edge("close", "chg", "RCA within 24–72 h", dashed=True, points=[(1085, 170), (1085, 210)])
    return d


def linux_triage():
    d = Diagram("n2-linux-triage", 1180, 380, "\"The application is slow / down\": Linux triage order")
    d.box("up", 20, 60, 210, 110, "1. Is it running?\nsystemctl status app\nps -ef | grep java\nss -tlnp | grep 8080", "blue", size=11, align="left")
    d.box("res", 260, 60, 210, 110, "2. Resources?\nuptime (load)\ntop / free -h\ndf -h ; df -i", "purple", size=11, align="left")
    d.box("logs", 500, 60, 210, 110, "3. Logs?\ntail -f catalina.out\ngrep -i error app.log\njournalctl -u app", "yellow", size=11, align="left")
    d.box("net", 740, 60, 210, 110, "4. Dependencies?\ncurl -v localhost:8080\nnc -zv db 1521\nnslookup db-host", "orange", size=11, align="left")
    d.box("fix", 980, 60, 180, 110, "5. Mitigate\nrestart / free disk\nroll back\nthen RCA", "green", size=11, align="left")
    for a, b in [("up", "res"), ("res", "logs"), ("logs", "net"), ("net", "fix")]:
        d.edge(a, b)
    d.box("tip", 20, 210, 1140, 140,
          "Say it out loud while you work\n"
          "\"First I check scope: one user or all, one server or all, since when, any change or deployment in that window?\n"
          "Then: is the process up and listening, are CPU / memory / disk / inodes healthy, what do the logs say at that time,\n"
          "can the app reach its database and downstream services? I restore service first, keep evidence (logs, thread dump),\n"
          "and open a problem ticket for the RCA.\"", "white", size=11, align="left")
    return d


ALL = [incident_lifecycle, linux_triage]

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
