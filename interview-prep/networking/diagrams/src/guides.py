"""Guide diagrams: the master README, the learning roadmap module and interview preparation."""
from drawio_svg import Diagram

# Level status colours, used the same way in every roadmap diagram:
# written = green, partly written = orange, planned = white with a dashed outline.
WRITTEN, PARTLY, PLANNED = "green", "orange", "white"


def _level(d, id, x, y, w, label, status, h=52):
    color = {"w": WRITTEN, "p": PARTLY, "n": PLANNED}[status]
    d.box(id, x, y, w, h, label, color, size=11, dashed=(status == "n"))


def roadmap_levels():
    d = Diagram("roadmap-levels", 860, 540, "The 12 levels in four stages (an arrow means: finish this level first)")
    # Stage bands, drawn first so they sit behind the levels. The label sits in a strip on the left.
    for sid, y, w, label in [("s1", 46, 530, "Stage 1\nBeginner"), ("s2", 156, 830, "Stage 2\nIntermediate"),
                             ("s3", 266, 830, "Stage 3\nAdvanced"), ("s4", 376, 830, "Stage 4\nExpert")]:
        d.group(sid, 16, y, w, 80, label, "gray", size=11, valign="middle", align="left")
    # Stage 1
    _level(d, "l1", 112, 60, 110, "1 · Networking\nfundamentals\n✅ 6 h · M1", "w")
    _level(d, "l2", 240, 60, 136, "2 · IP addressing\nand subnetting 🔥\n✅ 12 h + drills · M2", "w")
    _level(d, "l3", 394, 60, 136, "3 · Core protocols\n✅ 20 h · M3 ⭐", "w")
    _level(d, "l15", 690, 60, 146, "15 · Interview\npreparation 🎤\n✅ 10 h", "w")
    # Stage 2
    _level(d, "l4", 112, 170, 128, "4 · Switching\nand routing\n📝 20 h · M4", "n")
    _level(d, "l5", 255, 170, 128, "5 · Network\nservices\n📝 15 h · M4", "n")
    _level(d, "l6", 398, 170, 128, "6 · Network\nsecurity\n📝 15 h · M4", "n")
    _level(d, "l8", 542, 170, 150, "8 · Linux\nnetworking\n🚧 1 of 9 · 15 h · M5", "p")
    # Stage 3
    _level(d, "l7", 184, 280, 128, "7 · Advanced\nnetworking\n📝 15 h · M6", "n")
    _level(d, "l10", 542, 280, 150, "10 · Containers\nand Kubernetes\n🚧 1 of 9 · 20 h · M5", "p")
    _level(d, "l9", 722, 280, 114, "9 · Cloud\nnetworking 💸\n📝 20 h · M5", "n")
    # Stage 4
    _level(d, "l12", 370, 390, 184, "12 · Architecture and\ntroubleshooting\n📝 20 h + ongoing · M6", "n")
    _level(d, "l11", 607, 390, 200, "11 · Automation and\nobservability\n📝 12 h · M6", "n")

    ch12, ch23, ch34 = 141, 251, 361  # the gaps between the stage bands, where the arrows run
    d.edge("l1", "l2")
    d.edge("l2", "l3")
    d.edge("l3", "l15", "once the Level 3\nmilestone is met", dashed=True)
    d.edge("l3", "l4", points=[(462, ch12), (176, ch12)])
    d.edge("l3", "l5", points=[(462, ch12), (319, ch12)])
    d.edge("l3", "l6")
    d.edge("l3", "l8", points=[(462, ch12), (617, ch12)])
    d.edge("l3", "l9", points=[(462, ch12), (779, ch12)])
    d.edge("l4", "l7", points=[(176, ch23), (248, ch23)])
    d.edge("l5", "l7", points=[(319, ch23), (248, ch23)])
    d.edge("l8", "l10")
    d.edge("l8", "l11", points=[(707, 196)])
    d.edge("l10", "l11", points=[(617, ch34), (707, ch34)])
    d.edge("l9", "l11", points=[(779, ch34), (707, ch34)])
    d.edge("l6", "l12")
    d.edge("l7", "l12", points=[(248, ch34), (462, ch34)])
    d.edge("l11", "l12")

    d.box("legend", 16, 470, 830, 58,
          "✅ written (green) · 🚧 partly written, 1 of 9 lessons (orange) · 📝 planned (dashed) · Mx = the milestone the level counts towards\n"
          "No arrow between two levels: study them in any order. 💸 = the only level whose labs will use a paid cloud account.\n"
          "Times are estimates: Levels 1–3 about 38 h · all 12 levels about 190 h · with interview preparation about 200 h",
          "yellow", size=11, bold_first=False)
    return d


def roadmap_paths():
    d = Diagram("roadmap-paths", 860, 520, "Choose a path: all three start with Levels 1–3")

    def lane(prefix, y, title, chips, note):
        d.group(f"{prefix}-lane", 16, y, 828, 112, title, "gray", size=12, align="left")
        for i, (label, status) in enumerate(chips):
            _level(d, f"{prefix}{i}", 30 + i * 102, y + 32, 86, label, status, h=40)
            if i:
                d.edge(f"{prefix}{i - 1}", f"{prefix}{i}")
        d.text(f"{prefix}-note", 30, y + 80, 800, 24, note, size=11, italic=True, align="left")

    lane("a", 46, "Path A · DevOps, SRE and cloud engineers (the main path for these notes)",
         [("1\nFundamentals", "w"), ("2\nSubnetting 🔥", "w"), ("3\nProtocols ⭐", "w"), ("8\nLinux", "p"),
          ("10\nContainers", "p"), ("9\nCloud 💸", "n"), ("11\nAutomation", "n"), ("12\nExpert", "n")],
         "Skip or skim 4–7 until you need them: you meet VLANs, BGP and QoS mostly through cloud abstractions.")
    lane("b", 168, "Path B · Network engineers",
         [("1\nFundamentals", "w"), ("2\nSubnetting 🔥", "w"), ("3\nProtocols ⭐", "w"), ("4\nSwitching", "n"),
          ("5\nServices", "n"), ("6\nSecurity", "n"), ("7\nAdvanced", "n"), ("then\n8 · 9 · 12", "n")],
         "Vendor-neutral fundamentals prepare you for vendor certifications, but don't replace their device-specific material.")

    d.group("c-lane", 16, 290, 828, 220,
            "Path C · Interview fast track: about 35–40 h (estimate), about two weeks at 2–3 hours a day",
            "gray", size=12, align="left")
    steps = ["1 · Level 1: 1.3 and 1.5\naddresses and ports, OSI and TCP/IP\n2.5 h",
             "2 · All of Level 2 🔥\n+ 15 min of drills a day, from day 1\n10 h + drills",
             "3 · Level 3: six lessons\n3.2 · 3.4 · 3.6 · 3.8 · 3.10 · 3.11\n9 h",
             "4 · Two written deep notes\n8.6 Netfilter and NAT · 10.1 Docker\n1.5 h",
             "5 · Four labs\n2.1 · 3.1 · 3.5 · 10.1\n4.5 h",
             "6 · Interview preparation\nquestions · scenarios · drills · mock\n10 h"]
    for i, label in enumerate(steps):
        row, col = divmod(i, 3)
        d.box(f"c{i}", 28 + col * 280, 322 + row * 92, 244, 56, label, "blue", size=11)
        if i:
            pts = [(150 + 2 * 280, 397), (150, 397)] if i == 3 else None
            d.edge(f"c{i - 1}", f"c{i}", points=pts)
    d.text("c-note", 30, 478, 800, 24,
           "A shortcut, not a substitute: go back and fill in the skipped lessons afterwards.",
           size=11, italic=True, align="left")
    return d


def roadmap_reading_order():
    d = Diagram("roadmap-reading-order", 860, 230, "Read this module in this order: about 30 minutes")
    boxes = [("p", "1 · Prerequisites\nskills, a machine, tools\nand a self-check\n5 min", "blue"),
             ("h", "2 · How to study\nthe study loop, the lesson\nlayout, symbols, labels\n10 min", "blue"),
             ("r", "3 · Learning roadmap ⭐\n12 levels, milestones,\nthree paths, pacing\n15 min", "blue"),
             ("l1", "Then Level 1\nset up the lab environment\nbefore its second lab\n(Lab 1.2)", "green")]
    for i, (bid, label, color) in enumerate(boxes):
        d.box(bid, 17 + i * 214, 52, 184, 72, label, color, size=11)
        if i:
            d.edge(boxes[i - 1][0], bid)
    d.box("audit", 231, 156, 398, 56,
          "Content audit (reference, any time)\nwhat exists, where every piece went, what remains",
          "gray", size=11, dashed=True)
    return d


def prerequisites_setup():
    d = Diagram("prerequisites-setup", 860, 480, "What you need, and where each lab runs")
    d.group("mac", 16, 46, 540, 330, "💻 Your Mac with Docker Desktop: every lab (the notes were written on it)",
            "blue", size=12, align="left")
    d.box("builtins", 32, 78, 250, 80,
          "macOS built-ins: Lab 1.1\nifconfig · route · netstat · arp\nscutil --dns · lsof · ping · curl",
          "white", size=11)
    d.box("wireshark", 298, 78, 242, 80,
          "Wireshark (optional)\nopens the .pcap file Lab 3.1 saves\n(copy it into /labs first)",
          "white", size=11)
    d.group("vm", 32, 172, 508, 190, "Docker Desktop's Linux VM (Lab 10.1 looks inside it)",
            "gray", size=11, align="left")
    d.group("lab", 48, 200, 476, 148, "🐧 Lab container: the Linux labs run here, as root, safely isolated",
            "green", size=11, align="left")
    d.box("tools", 64, 226, 444, 62,
          "Every Linux tool the labs use\nip · tcpdump · tshark · dig · BIND · dnsmasq\nopenssl · iptables · conntrack · iperf3 · tc",
          "white", size=11)
    d.box("ns", 64, 296, 444, 44,
          "Network namespaces\neach a separate small \"computer\", using almost no memory",
          "blue", size=11)

    d.text("or", 576, 46, 268, 22, "No Mac? Other options", bold=True, size=12)
    d.box("linux", 576, 72, 268, 70,
          "A Linux machine or VM\nUbuntu 24.04 recommended\nevery lab except the macOS parts\ninstall the packages: setup option B",
          "blue", size=11)
    d.box("win", 576, 152, 268, 64,
          "Windows (not tested): the Linux labs\nWSL 2 with Docker Desktop, or an\nUbuntu VM; Linux commands, not macOS",
          "gray", size=11)
    d.box("cloudvm", 576, 226, 268, 64,
          "A cloud VM 💸: Linux labs, last resort\ncompute, storage, public IPv4 billed\nwhile it runs: stop it when done",
          "orange", size=11)
    d.box("level9", 576, 300, 268, 76,
          "Level 9 cloud account 💸 (planned)\na personal sandbox with a budget\nalert, never shared or production;\neach lab lists its cost and cleanup",
          "orange", size=11)

    d.box("check", 17, 400, 250, 64,
          "Self-check: 3 commands\npwd · ls -l /etc | head -5\ndocker run --rm alpine echo hello",
          "white", size=11)
    d.box("setup", 305, 400, 250, 64,
          "Lab environment setup\nonce, before Lab 1.2\nabout 20 minutes (estimate)",
          "blue", size=11)
    d.box("go", 593, 400, 250, 64,
          "Start Level 1\nno networking knowledge needed",
          "green", size=11)
    d.edge("check", "setup")
    d.edge("setup", "go")
    return d


def study_loop():
    d = Diagram("study-loop", 860, 260, "The loop for every lesson")
    steps = [("read", "1 · Read the lesson\nin one sitting; type\nevery command in\nTry it, don't paste"),
             ("lab", "2 · Do its lab\npredict before each\nstep: being wrong is\nwhere you learn"),
             ("check", "3 · Check yourself\nanswer on paper,\nwithout notes, then\nopen the answers"),
             ("explain", "4 · Explain out loud\n60 s, to a colleague,\nusing the lesson's\nInterview angle"),
             ("revisit", "5 · Revisit\nCheck yourself again\nafter 1, 3 and 7 days\n(spaced recall)")]
    for i, (sid, label) in enumerate(steps):
        d.box(sid, 16 + i * 168, 52, 150, 80, label, "blue", size=11)
        if i:
            d.edge(steps[i - 1][0], sid)
    d.edge("revisit", "read", "forgot something, or stumbled while explaining: re-read that part",
           dashed=True, points=[(16 + 4 * 168 + 75, 166), (91, 166)])
    d.box("tip", 16, 196, 822, 50,
          "Reading feels like learning, but most of what you only read is gone within a week.\n"
          "What sticks is what you predict, do, explain and recall later. Spaced recall is the cheapest way to make it permanent.",
          "yellow", size=11, bold_first=False)
    return d


def lesson_layout():
    d = Diagram("lesson-layout", 860, 616, "A lesson page, top to bottom")
    d.group("page", 16, 46, 330, 558, "", "gray")
    d.text("hdr-what", 370, 46, 470, 22, "What it gives you, and what to do with it", bold=True, align="left")
    rows = [  # id, height, block label, colour, what it gives you
        ("head", 50, "# n.m · Title\nLevel · lesson m of k · ⏱️ · 🧪 Lab · ⬅️ ➡️", "white",
         "Where you are, how long it takes (estimate), which lab practises it"),
        ("diag", 78, "Diagram (draw.io)\nthe whole idea in one picture", "blue",
         "Read it first. Later, cover it and redraw it from memory"),
        ("bullets", 50, "3–6 key points\n⭐ on the most-asked one", "white",
         "The facts to remember: numbers, ports, rules"),
        ("topics", 62, "2–5 topic sections\na diagram, short bullets, tested output", "white",
         "One main idea each, with the console output that proves it"),
        ("where", 34, "Where you meet it (optional)", "white", "Docker, Kubernetes, AWS and your Mac: one table row each"),
        ("try", 34, "Try it", "white", "Commands to type yourself (don't paste)"),
        ("trouble", 34, "Troubleshooting", "white", "A table: You see | It means | Next step"),
        ("iv", 34, "Interview angle", "white", "Likely questions → short model answers: say them out loud"),
        ("check", 34, "Check yourself", "white", "Questions, answers hidden until you open them"),
        ("next", 34, "➡️ Next", "white", "The next lesson, with one line on what it adds"),
    ]
    y = 58
    for rid, h, label, color, what in rows:
        d.box(rid, 32, y, 298, h, label, color, size=11)
        d.text(f"{rid}-what", 370, y, 470, h, what, size=11, align="left")
        y += h + 10
    return d


def interview_prep_plan():
    d = Diagram("interview-prep-plan", 860, 300, "Interview preparation: a first pass of about 10 hours (estimate)")
    boxes = [("gate", "Start: Level 3 milestone ✓\nrehearsing answers you don't\nunderstand yet only builds\nconfident mistakes", "green"),
             ("bank", "1 · Question bank · ~3 h\nanswer each one out loud\nbefore you open its link", "blue"),
             ("scen", "2 · Scenarios N1–N13 · ~3 h\nSay · Check · He'll push", "blue"),
             ("drill", "3 · Drills and whiteboard · ~2 h\nset a timer, record yourself,\nlisten back; draw from memory", "blue"),
             ("mock", "4 · One mock interview · ~1 h\na friend picks the questions", "blue"),
             ("review", "5 · Review · ~1 h\npractise what was vague,\nout of order or unproved", "blue")]
    for i, (bid, label, color) in enumerate(boxes):
        row, col = divmod(i, 3)
        d.box(bid, 16 + col * 284, 50 + row * 116, 256, 84, label, color, size=11)
        if i:
            pts = [(144 + 2 * 284, 150), (144, 150)] if i == 3 else None
            d.edge(boxes[i - 1][0], bid, points=pts)
    d.box("daily", 16, 262 - 0, 824, 30,
          "Then, before an interview: 20 minutes a day", "yellow", size=12, bold=True)
    return d


def interview_answer_steps():
    d = Diagram("interview-answer-steps", 860, 290, "How to answer a networking question: five steps")
    steps = [("c", "1 · Clarify\nthe question", "\"Not reachable from\nwhere: the same VPC,\nthe internet, another\npod?\""),
             ("a", "2 · One-sentence\nanswer first", "\"It's listening on\n127.0.0.1, so only\nthe same machine can\nconnect.\""),
             ("m", "3 · Mechanism,\nin order", "the packet's path, the\nlayers, or DNS → route\n→ port → listener →\nrules → app"),
             ("p", "4 · Proof:\ncommand + output", "name the command and\nwhat it would show:\nss -ltnp shows\n127.0.0.1:8000"),
             ("s", "5 · Their stack\nconnect it", "the same idea in\nDocker, Kubernetes\nor AWS")]
    for i, (sid, title, example) in enumerate(steps):
        x = 16 + i * 168
        d.box(sid, x, 50, 150, 44, title, "blue", size=11, bold=True)
        d.box(f"{sid}-ex", x, 106, 150, 70, example, "white", size=11, bold_first=False)
        if i:
            d.edge(steps[i - 1][0], sid)
    d.box("unsure", 16, 198, 822, 76,
          "When you don't know\n"
          "Say what you do know, how you'd find out (the command or the document) and what you'd expect to see.\n"
          "\"I'm not sure of the exact default, but I'd check sysctl net.ipv4.tcp_keepalive_time\" is a good answer;\n"
          "a confident guess is a bad one.",
          "yellow", size=11)
    return d


ALL = [roadmap_levels, roadmap_paths, roadmap_reading_order, prerequisites_setup, study_loop,
       lesson_layout, interview_prep_plan, interview_answer_steps]
