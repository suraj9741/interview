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


def d2_slow_server():
    d = Diagram("d2-slow-server-triage", 900, 600, "Day 2: \"the server is slow\": check in this order, then signals and systemd")
    steps = [
        ("load", "1 · Load\nuptime · nproc\nload > CPU count = queueing", "gray"),
        ("cpu", "2 · CPU\ntop: us sy wa st\nps --sort=-%cpu", "blue"),
        ("mem", "3 · Memory\nfree -h → available\ndmesg -T | grep -i oom", "purple"),
        ("disk", "4 · Disk space\ndf -h · df -i (inodes)\ndu -sh · lsof +L1", "yellow"),
        ("io", "5 · Disk I/O\ntop wa · vmstat 1\niostat -xz 1 (%util, await)", "orange"),
        ("logs", "6 · Logs + network\njournalctl -u app --since\nss -tulpn · ss -s", "green"),
    ]
    for i, (sid, label, col) in enumerate(steps):
        x = 20 + (i % 3) * 293
        y = 55 + (i // 3) * 105
        d.box(sid, x, y, 275, 85, label, col, size=11)
    for a, b in [("load", "cpu"), ("cpu", "mem"), ("disk", "io"), ("io", "logs")]:
        d.edge(a, b)
    d.edge("mem", "disk", points=[(744, 150), (157, 150)])
    d.text("hint", 20, 250, 860, 40,
           "High load + low CPU + high wa = waiting on disk (D state). df full but du small = deleted file still open.\n"
           "\"No space left\" but df shows space = inodes full (df -i). Process vanished, no app log = OOM killer (dmesg).", size=11)
    d.group("sig", 20, 305, 420, 275, "Signals: kill -<n> PID", "white", size=12)
    d.box("s15", 35, 340, 390, 50, "15 SIGTERM (default kill): ask to stop, app cleans up\nexit code 128+15 = 143", "green", size=10)
    d.box("s9", 35, 398, 390, 50, "9 SIGKILL: kernel kills at once, can't be caught\nexit code 128+9 = 137 (also OOMKilled)", "red", size=10)
    d.box("s1", 35, 456, 390, 50, "1 SIGHUP: reload config (nginx, rsyslog)\n2 SIGINT = Ctrl+C · Ctrl+Z = SIGTSTP (stop)", "yellow", size=10)
    d.text("srule", 35, 515, 390, 55, "Always 15 first, wait, then 9.\nA zombie (Z) can't be killed: fix or restart its parent.", size=11)
    d.group("sysd", 460, 305, 420, 275, "systemd: run and watch a service", "white", size=12)
    d.box("unit", 475, 340, 390, 50, "/etc/systemd/system/myapp.service\n[Unit] · [Service] ExecStart, Restart · [Install]", "blue", size=10)
    d.box("reload", 475, 410, 390, 40, "systemctl daemon-reload  (after every edit)", "gray", size=11, bold_first=False)
    d.box("start", 475, 470, 390, 40, "systemctl enable --now myapp · status · restart", "purple", size=11, bold_first=False)
    d.box("jctl", 475, 530, 390, 40, "journalctl -u myapp -f --since \"10 min ago\" -p err", "green", size=11, bold_first=False)
    d.edge("unit", "reload")
    d.edge("reload", "start")
    d.edge("start", "jctl")
    return d


ALL = [d1_pipeline, d2_slow_server]

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
