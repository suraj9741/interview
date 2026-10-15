"""Lab diagrams, part A: lab environment setup and labs 1.1 to 2.3."""
from drawio_svg import Diagram


# ---- shared helpers ------------------------------------------------------------------
def _lifeline(d, id, cx, y0, y1):
    """A thin vertical bar for a sequence diagram."""
    d.box(id, cx - 6, y0, 12, y1 - y0, "", "gray", bold_first=False)


def _anchor(d, id, cx, y):
    """An invisible point on a lifeline, for a horizontal message arrow."""
    d.text(id, cx - 1, y - 8, 2, 16, "")


def _msg(d, id, x1, x2, y, *, dashed=False):
    """A horizontal arrow from x1 to x2 at height y (no label: labels are placed as text)."""
    _anchor(d, f"{id}-a", x1, y)
    _anchor(d, f"{id}-b", x2, y)
    d.edge(f"{id}-a", f"{id}-b", dashed=dashed)


# ---- 00 · lab environment setup --------------------------------------------------------
def lab_setup_layers():
    d = Diagram("lab-setup-layers", 860, 460, "Where the labs run: small networks inside one Linux container")
    d.group("mac", 20, 50, 540, 310, "Option A · your Mac (macOS)", "gray")
    d.group("vm", 40, 82, 500, 262, "Docker Desktop's Linux VM: --privileged applies here, not to macOS", "white", size=12)
    d.group("ctr", 60, 114, 460, 214, "netlab container: docker run --rm -it --privileged\nthe files/ folder appears as /labs\n"
            "--privileged: never on a shared or production Linux server", "outline", dashed=True, size=12)
    d.box("h1", 80, 186, 110, 50, "namespace\nh1", "blue")
    d.box("r1", 240, 186, 110, 50, "namespace\nr1", "green")
    d.box("h2", 400, 186, 110, 50, "namespace\nh2", "blue")
    d.edge("h1", "r1", "veth", both=True)
    d.edge("r1", "h2", "veth", both=True)
    d.text("ns", 70, 252, 440, 56, "Each lab creates its own namespaces and deletes them in cleanup.\n"
           "Exiting the container (--rm) throws everything away.\nNothing touches your real network.", size=11)

    d.box("optb", 580, 50, 260, 100, "Option B · any Ubuntu 24.04 machine\nUTM · Multipass · VirtualBox VM\nor a spare Linux box\n"
          "apt-get install the lab packages\nthen run lab commands with sudo", "blue", size=11)
    d.box("cloud", 580, 162, 260, 128, "A cloud VM (EC2) costs money\nbilled by the hour, plus storage\nand public IPv4 address charges\n"
          "free tier depends on your account\nstop or terminate it when done\nsecurity group: your own IP only", "yellow", size=11)
    d.box("free", 580, 302, 260, 58, "Free\nno lab in Levels 1–3 creates\ncloud resources", "green", size=11)

    d.box("lns", 20, 380, 266, 60, "network namespace\na separate computer: its own interfaces,\nIP addresses, routing table, firewall",
          "blue", size=11)
    d.box("lveth", 297, 380, 266, 60, "veth pair\na virtual cable between two namespaces", "white", size=11)
    d.box("lbr", 574, 380, 266, 60, "Linux bridge\na virtual switch (Lab 1.2 part B)", "green", size=11)
    return d


# ---- Lab 1.1 · inspect your own network ---------------------------------------------
def lab11_home_network():
    d = Diagram("lab-1.1-home-network", 860, 470, "Your home network, and the step that finds each value")
    d.box("mac", 20, 50, 200, 66, "Your Mac\nen0 (Wi-Fi)\n192.168.29.x/24", "blue")
    d.box("rtr", 290, 50, 220, 66, "Home router\n192.168.29.1\ngateway · DHCP · DNS · NAT", "orange")
    d.box("isp", 600, 50, 100, 66, "Provider", "gray")
    d.box("net", 740, 50, 100, 66, "Internet", "gray", shape="ellipse")
    d.edge("mac", "rtr", "Wi-Fi")
    d.edge("rtr", "isp", "WAN / fibre")
    d.edge("isp", "net")

    d.text("h1", 20, 128, 250, 22, "About your Mac", bold=True)
    d.text("h2", 285, 128, 270, 22, "About the router", bold=True)
    d.text("h3", 570, 128, 270, 22, "From the internet", bold=True)

    d.box("s1", 20, 156, 250, 64, "1 · ifconfig en0\nether: MAC · inet: IPv4 · inet6: IPv6\nipconfig getifaddr en0: IPv4 only",
          "white", size=11)
    d.box("s6", 20, 234, 250, 78, "6 · lsof -nP -iTCP -sTCP:LISTEN\nprograms waiting for connections\n"
          "127.0.0.1 = only this Mac can connect\n* or 0.0.0.0 = anyone who reaches you", "white", size=11)
    d.box("s2", 285, 156, 270, 64, "2 · route -n get default\nyour gateway: 192.168.29.1\n(and the interface used)", "white", size=11)
    d.box("s3", 285, 234, 270, 50, "3 · ping the gateway, then arp -a\nthe gateway's MAC address", "white", size=11)
    d.box("s4", 285, 298, 270, 78, "4 · scutil --dns\nDNS server = the router: 192.168.29.1\nand an IPv6 address ending c0a8:1d01\n"
          "(c0a8:1d01 = 192.168.29.1 in hex)", "white", size=11)
    d.box("s5", 570, 156, 270, 64, "5 · curl -s https://ifconfig.me\nyour public IP: not 192.168.x.x\nthe difference is NAT at the router",
          "white", size=11)
    d.box("s7", 570, 234, 270, 78, "7 · ping gateway, 8.8.8.8, google.com\ngateway: a few ms over Wi-Fi\n"
          "internet: tens of ms\ngoogle.com needs DNS as well", "white", size=11)
    d.box("lin", 570, 326, 270, 50, "On Linux\nip -br addr · ip route · ip neigh\n/etc/resolv.conf · ss -tlnp", "gray", size=11)

    d.box("note", 20, 396, 820, 56, "Addresses are from the author's Mac (Oct 2026); yours may differ.\n"
          "Check: your IP and gateway share a subnet · public IP ≠ private IP · 8.8.8.8 works but google.com fails → DNS",
          "yellow", size=12, bold_first=False)
    return d


# ---- Lab 1.2 · a tiny network with namespaces ---------------------------------------
def lab12_topology():
    d = Diagram("lab-1.2-topology", 860, 400, "What you build: a cable (parts A, C, D), then a switch (part B)")
    d.group("ga", 20, 50, 400, 300, "Parts A, C, D · two PCs and a cable", "gray")
    d.box("a1", 40, 90, 130, 62, "pc1\nveth-pc1\n192.168.10.1/24", "blue")
    d.box("a2", 270, 90, 130, 62, "pc2\nveth-pc2\n192.168.10.2/24", "blue")
    d.edge("a1", "a2", "veth pair", both=True)
    d.box("na", 40, 170, 360, 46, "A · ping pc2: ARP first (0.232 ms), then ~0.04 ms\nttl=64: no router crossed", "white", size=11)
    d.box("nc", 40, 226, 360, 46, "C · ping 8.8.8.8 → Network is unreachable\nthe only route is 192.168.10.0/24: no gateway", "red",
          size=11)
    d.box("nd", 40, 282, 360, 56, "D · tc tbf rate 10mbit on veth-pc1\niperf3 pc1 → pc2: 9.41 Mbit/s received\n"
          "pings slow down while the link is full", "white", size=11)

    d.group("gb", 440, 50, 400, 300, "Part B · three PCs and a switch", "gray")
    d.group("sw", 452, 84, 376, 112, "namespace sw", "outline", dashed=True, size=12)
    d.box("br0", 462, 114, 356, 34, "br0 · a Linux bridge (the switch)", "green", bold=True)
    for i, x in enumerate((462, 586, 710), start=1):
        d.box(f"p{i}", x, 148, 108, 30, f"port{i}", "green")
        d.box(f"pc{i}", x, 238, 108, 62, f"pc{i}\neth0\n192.168.20.{i}/24", "blue", size=11)
        d.edge(f"p{i}", f"pc{i}", "veth", both=True)
    d.text("bdel", 452, 310, 376, 30, "First delete Part A's pc1 and pc2: the names are reused", size=11)

    d.text("order", 20, 362, 820, 24, "Order in this lab:  A → C → D (same two PCs)  →  delete them  →  B  →  cleanup", bold=True)
    return d


def lab12_switch_flooding():
    d = Diagram("lab-1.2-switch-flooding", 860, 420, "Part B: pc1 pings pc2 while pc3 listens")
    panels = [
        ("1 · ARP request (broadcast)\nflooded out of every port", [("pc1", "br0"), ("br0", "pc2"), ("br0", "pc3")], True,
         "broadcast: who-has 192.168.20.2?\nbr0 learns pc1's MAC on port1"),
        ("2 · ARP reply (unicast)\nsent only to pc1's port", [("pc2", "br0"), ("br0", "pc1")], False,
         "to pc1's MAC, learned in 1\nbr0 learns pc2's MAC on port2"),
        ("3 · ping request and reply\nunicast, pc1 ↔ pc2 only", [("pc1", "br0"), ("br0", "pc2")], False,
         "both MACs are known now\nno flooding, so pc3 sees nothing"),
    ]
    for n, (label, path, pc3_sees, learn) in enumerate(panels):
        px = 20 + n * 280
        d.group(f"g{n}", px, 50, 260, 264, label, "gray", size=12)
        d.box(f"br{n}", px + 80, 106, 100, 34, "br0", "green", bold=True)
        for i, ox in enumerate((10, 93, 176), start=1):
            if i == 3:
                lbl, col = ("pc3\nsees it" if pc3_sees else "pc3\n(nothing)"), ("blue" if pc3_sees else "gray")
            else:
                lbl, col = f"pc{i}", "blue"
            d.box(f"pc{i}-{n}", px + ox, 186, 74, 44, lbl, col, bold=(i != 3), size=11 if i == 3 else 12)
        for a, b in path:
            src = f"br{n}" if a == "br0" else f"{a}-{n}"
            tgt = f"br{n}" if b == "br0" else f"{b}-{n}"
            d.edge(src, tgt, both=(n == 2))
        d.box(f"l{n}", px + 10, 250, 240, 50, learn, "green", size=11, bold_first=False)
    d.box("fdb", 20, 330, 820, 72, "The switch's table (FDB) at the end\n"
          "pc1's MAC → port1 · pc2's MAC → port2 · pc3 is missing: it never sent a frame\n"
          "Entries age out after ageing_time 30000 = 300 seconds", "yellow")
    return d


# ---- Lab 2.1 · subnetting by hand ----------------------------------------------------
def lab21_map():
    d = Diagram("lab-2.1-lab-map", 860, 380, "Paper first, then check: the three parts of this lab")
    cols = [
        ("Part A · classify",
         "On paper\n9 addresses: private (RFC 1918),\npublic, or special?",
         "Check\nsubnet_check.py --classify …",
         "Target: 9/9"),
        ("Part B · ten subnets",
         "On paper, for each subnet\nnetwork · broadcast · host range\nusable · usable in AWS (5 reserved)",
         "Check\nsubnet_check.py <10 subnets>\nipcalc -n: the same in binary\nip route get: local or remote?",
         "Target: 10/10\nbelow 100% → more drills"),
        ("Part C · VLSM + summaries",
         "On paper\nsplit 192.168.1.0/24 for 100, 50,\n20 hosts + 2 point-to-point links;\ncan two sets of /24s be summarised?",
         "Check\nsubnet_check.py --overlap …\nsubnet_check.py --summarise …",
         "Target: no overlaps and\nthe right summary / non-summary"),
    ]
    for i, (head, paper, check, target) in enumerate(cols):
        x = 20 + i * 280
        d.text(f"h{i}", x, 46, 260, 24, head, bold=True, size=13)
        d.box(f"p{i}", x, 76, 260, 76, paper, "blue", size=11)
        d.box(f"c{i}", x, 176, 260, 76, check, "white", size=11)
        d.box(f"t{i}", x, 276, 260, 46, target, "green", size=11, bold="\n" not in target)
        d.edge(f"p{i}", f"c{i}")
        d.edge(f"c{i}", f"t{i}")
    d.text("note", 20, 336, 820, 34, "subnet_check.py (in files/lab-02.1) uses only Python's standard ipaddress module · "
           "ipcalc is optional (brew install ipcalc on a Mac)", size=11)
    return d


def lab21_local_or_remote():
    d = Diagram("lab-2.1-local-or-remote", 860, 420, "Part B: local or remote? The kernel decides from 10.20.37.140/26")
    d.group("ns", 20, 48, 430, 104, "namespace host · default via 10.20.37.129", "gray", size=12)
    d.box("v0", 40, 84, 160, 52, "veth0\n10.20.37.140/26", "blue")
    d.box("v1", 300, 84, 130, 52, "veth1\nup, no address", "white")
    d.edge("v0", "v1", "veth pair", both=True)
    d.box("tip", 470, 48, 370, 104, "ip route get <destination>\nasks the kernel how it would reach it:\n"
          "send directly (dev veth0), or via the gateway?\nNothing else is attached to the cable.", "yellow", size=11)

    dests = [("d150", "10.20.37.150", 252), ("d190", "10.20.37.190", 384), ("d191", "10.20.37.191", 501),
             ("d200", "10.20.37.200", 642), ("d38", "10.20.38.1", 772)]
    for did, ip, cx in dests:
        d.box(did, cx - 47, 178, 94, 32, ip, "white", size=11, bold=True)

    d.group("loc", 20, 236, 540, 104, "10.20.37.128/26 · connected route: sent directly", "green", size=12,
            valign="bottom")
    segs = [("s128", 28, 72, ".128\nnetwork", "gray"), ("s129", 104, 78, ".129\ngateway", "orange"),
            ("shost", 186, 132, ".130 – .189\nhosts (you: .140)", "blue"), ("s190", 322, 124, ".190\nlast host", "blue"),
            ("s191", 450, 102, ".191\nbroadcast", "gray")]
    for sid, x, w, lbl, col in segs:
        d.box(sid, x, 246, w, 56, lbl, col, size=11)
    d.group("rem", 570, 236, 270, 104, "outside the /26: via 10.20.37.129", "orange", size=12, valign="bottom")
    d.box("snext", 580, 246, 124, 56, ".192 – .255\nthe next /26", "white", size=11)
    d.box("sother", 714, 246, 116, 56, "10.20.38.0 …\nother subnets", "white", size=11)
    for did, sid in [("d150", "shost"), ("d190", "s190"), ("d191", "s191"), ("d200", "snext"), ("d38", "sother")]:
        d.edge(did, sid)

    d.box("note", 20, 356, 820, 48, "A /26 is a block of 64: boundaries at .0 · .64 · .128 · .192.\n"
          ".200 looks close to .140, but it is in the next block, so it goes via the gateway.", "yellow", bold_first=False)
    return d


def lab21_vlsm_summaries():
    d = Diagram("lab-2.1-vlsm-summaries", 860, 440, "Part C: the VLSM plan and the two summaries")
    d.text("h1", 20, 42, 820, 22, "192.168.1.0/24, largest subnet first (the plan checked with --overlap)", bold=True, align="left")
    px = 820 / 256  # pixels per address

    def seg(id, start, size, label, color, dashed=False):
        d.box(id, 20 + start * px, 70, size * px, 56, label, color, size=11, dashed=dashed)

    seg("p25", 0, 128, "192.168.1.0/25 · .0 – .127\n100 hosts (126 usable)", "blue")
    seg("p26", 128, 64, "192.168.1.128/26\n50 hosts (62 usable)", "blue")
    seg("p27", 192, 32, ".192/27\n20 hosts (30)", "blue")
    seg("tail", 224, 32, ".224 – .255\nzoom ↓", "white", dashed=True)
    zx, zpx = 328, 16  # zoomed: 16 px per address
    d.text("zl", 20, 152, 300, 52, "The last 32 addresses, zoomed:\n2 point-to-point links (/30)\nand the free space left over",
           size=11, align="left")
    d.box("zgrp", zx, 152, 32 * zpx, 52, "", "none")
    zsegs = [("z1", 0, 4, ".224/30\nlink", "green", False), ("z2", 4, 4, ".228/30\nlink", "green", False),
             ("z3", 8, 8, ".232/29\nfree", "white", True), ("z4", 16, 16, ".240/28\nfree", "white", True)]
    for zid, start, size, label, col, dashed in zsegs:
        d.box(zid, zx + start * zpx, 152, size * zpx, 52, label, col, size=11, dashed=dashed)
    d.edge("tail", "zgrp", dashed=True)

    d.text("h2", 20, 226, 820, 22, "Summaries: can one route cover them?  (the third octet is shown in each box)", bold=True,
           align="left")
    cw, x0 = 50, 180
    d.text("r1l", 20, 266, 150, 40, "172.16.X.0/24", size=12, bold=True)
    d.group("b21", x0 - 6, 256, 8 * cw + 6, 60, "", "outline", dashed=True)
    for i, octet in enumerate(range(8, 16)):
        d.box(f"a{octet}", x0 + i * cw, 266, cw - 6, 40, str(octet), "blue", bold=True)
    d.box("r1r", 620, 256, 220, 60, "✓ one route: 172.16.8.0/21\n8 networks starting at 8,\na multiple of 8", "green", size=11)

    d.text("r2l", 20, 348, 150, 40, "192.168.X.0/24", size=12, bold=True)
    for i, octet in enumerate(range(4, 12)):
        if i in (0, 4):
            bx = x0 + i * cw + (16 if i else 0)
            d.group(f"blk{i}", bx - 6, 338, 4 * cw + 6, 60, "", "outline", dashed=True)
            d.text(f"w{i}", bx - 6, 400, 4 * cw + 6, 20, f"192.168.{octet}.0/22", size=11)
        x = x0 + i * cw + (16 if i >= 4 else 0)
        d.box(f"b{octet}", x, 348, cw - 6, 40, str(octet), "blue" if 5 <= octet <= 8 else "white", bold=True)
    d.box("r2r", 620, 338, 220, 60, "✗ no single route: 5 is not\na multiple of 4, so the set spans\ntwo /22 blocks: /24 + /23 + /24",
          "red", size=11)
    return d


# ---- Lab 2.2 · routing between two subnets ------------------------------------------
def lab22_topology():
    d = Diagram("lab-2.2-topology", 860, 330, "Two subnets joined by two routers: what each part adds")
    pw, pgap, dw = 196, 12, 150
    pxs = [20 + i * (pw + pgap) for i in range(4)]
    centres = [x + pw / 2 for x in pxs]
    devs = [("h1", "h1\neth0 10.0.1.10/24", "blue"),
            ("r1", "r1\neth0 10.0.1.1/24\neth1 10.0.12.1/30", "green"),
            ("r2", "r2\neth1 10.0.12.2/30\neth0 10.0.2.1/24", "green"),
            ("h2", "h2\neth0 10.0.2.10/24", "blue")]
    for (nid, label, col), c in zip(devs, centres):
        d.box(nid, c - dw / 2, 50, dw, 62, label, col)
    for a, b in zip(devs, devs[1:]):
        d.edge(a[0], b[0], both=True)
    for i, net in enumerate(["10.0.1.0/24", "10.0.12.0/30", "10.0.2.0/24"]):
        gc = (centres[i] + centres[i + 1]) / 2
        d.text(f"n{i}", gc - 60, 116, 120, 20, net, size=11, bold=True)
    d.text("lb", 20, 146, 820, 20, "Part B adds (one step at a time; the numbers are the steps)", bold=True, size=11)
    partb = ["2 · default via 10.0.1.1",
             "3 · ip_forward=1\n4 · 10.0.2.0/24 via 10.0.12.2",
             "3 · ip_forward=1\n6 · 10.0.1.0/24 via 10.0.12.1",
             "5 · default via 10.0.2.1"]
    for i, (txt, x) in enumerate(zip(partb, pxs)):
        d.box(f"b{i}", x, 168, pw, 46, txt, "white", size=11, bold_first=False)
    d.text("lc", 20, 226, 820, 20, "Part C adds", bold=True, size=11)
    partc = ["sends ping -t, traceroute,\ntracepath, curl",
             "eth1 mtu 1400",
             "eth1 mtu 1400\nOUTPUT: drop time-exceeded",
             "web server on port 8080\nINPUT: drop echo-request"]
    for i, (txt, x) in enumerate(zip(partc, pxs)):
        d.box(f"c{i}", x, 248, pw, 46, txt, "white", size=11, dashed=True, bold_first=False)
    d.text("foot", 20, 302, 820, 20, "Each link is a veth pair; r1 and r2 each sit in two subnets", size=11, italic=True)
    return d


def lab22_fix_ladder():
    d = Diagram("lab-2.2-fix-ladder", 860, 500, "Part B: add one piece at a time; each missing piece fails differently")
    d.text("h1", 20, 44, 230, 22, "You add", bold=True)
    d.text("h2", 270, 44, 270, 22, "h1's ping shows (tested)", bold=True)
    d.text("h3", 560, 44, 280, 22, "Why: where the packet stops", bold=True)
    rows = [
        ("1 · nothing yet", "ping: connect: Network is unreachable\ninstant: nothing is sent", "red",
         "h1 has no route to 10.0.2.0/24\nand no default route"),
        ("2 · h1: default via 10.0.1.1", "100% packet loss, no error", "gray",
         "r1 gets the packets but isn't\nforwarding: ip_forward = 0"),
        ("3 · r1, r2: ip_forward=1", "From 10.0.1.1 …\nDestination Net Unreachable", "red",
         "r1 forwards, but has no route\nto 10.0.2.0/24, and says so"),
        ("4 · r1: 10.0.2.0/24\nvia 10.0.12.2", "100% packet loss, no error", "gray",
         "the request reaches h2, but\nh2 has no route back to 10.0.1.0/24"),
        ("5 · h2: default via 10.0.2.1", "100% packet loss, no error", "gray",
         "h2 replies via r2, but r2 has no\nroute back; r2 tells h2, not h1"),
        ("6 · r2: 10.0.1.0/24\nvia 10.0.12.1", "✓ 64 bytes from 10.0.2.10\nttl=62", "green",
         "routes in both directions\nttl 62 = 64 − 2 routers"),
    ]
    for i, (add, seen, col, why) in enumerate(rows):
        y = 72 + i * 64
        d.box(f"a{i}", 20, y, 230, 50, add, "blue", size=11, bold_first=False)
        d.box(f"s{i}", 270, y, 270, 50, seen, col, size=11)
        d.box(f"w{i}", 560, y, 280, 50, why, "white", size=11, bold_first=False)
        if i:
            d.edge(f"a{i - 1}", f"a{i}")
    d.box("tip", 20, 460, 820, 30, "No error at all = a silent drop or a missing route back: capture on the far end "
          "and ask \"does it know how to get back to me?\"", "yellow", size=11)
    return d


def lab22_traceroute_mtu():
    d = Diagram("lab-2.2-traceroute-mtu", 860, 600, "Part C: what traceroute and a \"don't fragment\" ping really do")
    cols = [("h1", 100, "h1\n10.0.1.10", "blue"), ("r1", 320, "r1\n10.0.1.1 | 10.0.12.1", "green"),
            ("r2", 540, "r2\n10.0.12.2 | 10.0.2.1", "green"), ("h2", 760, "h2\n10.0.2.10", "blue")]
    for cid, cx, label, col in cols:
        d.box(cid, cx - 80, 46, 160, 46, label, col, size=11)
        _lifeline(d, f"ll-{cid}", cx, 92, 440)
    x = {cid: cx for cid, cx, _, _ in cols}

    d.text("sec1", 112, 96, 200, 18, "traceroute -n 10.0.2.10", bold=True, size=11, align="left")
    rows = [  # (id, from, to, y, label, label column, dashed)
        ("t1", "h1", "r1", 136, "UDP probe · TTL 1", "h1", False),
        ("t1r", "r1", "h1", 168, "time exceeded from 10.0.1.1", "h1", True),
        ("t2", "h1", "r2", 208, "UDP probe · TTL 2", "h1", False),
        ("t2r", "r2", "h1", 240, "time exceeded from 10.0.12.2", "r1", True),
        ("t3", "h1", "h2", 280, "UDP probe · TTL 3", "h1", False),
        ("t3r", "h2", "h1", 312, "ICMP port 33436 unreachable", "r2", True),
    ]
    for rid, a, b, y, label, lcol, dashed in rows:
        _msg(d, rid, x[a], x[b], y, dashed=dashed)
        d.text(f"{rid}-t", x[lcol] + 8, y - 20, 204, 18, label, size=11)

    d.text("sec2", 112, 336, 200, 18, "ping -M do (don't fragment)", bold=True, size=11, align="left")
    _msg(d, "m1", x["h1"], x["r1"], 376)
    d.text("m1-t", x["h1"] + 8, 356, 204, 18, "1500-byte packet, DF set", size=11)
    d.box("mtu", 342, 359, 176, 34, "r1 → r2 link: MTU 1400", "red", size=11, bold=True)
    _msg(d, "m1r", x["r1"], x["h1"], 420, dashed=True)
    d.text("m1r-t", x["h1"] + 8, 386, 204, 30, "Frag needed and DF set\n(mtu = 1400)", size=11)

    d.box("n1", 20, 456, 400, 52, "traceroute -I (ICMP echo) and -T -p 8080 (TCP SYN)\nuse other probes: the same three hops", "yellow",
          size=11)
    d.box("n2", 440, 456, 400, 52, "r2 drops its time-exceeded messages → hop 2 shows *\nbut hop 3 still answers: the path works",
          "yellow", size=11)
    d.box("n3", 20, 520, 400, 62, "h2 drops echo-request\nping: 100% packet loss · curl :8080 → HTTP 200\n"
          "ping blocked does not mean the service is down", "yellow", size=11)
    d.box("pmtu", 440, 520, 400, 62, "h1 remembers path MTU 1400\nthe next 1500-byte ping fails locally: message too long\n"
          "a 1400-byte packet fits", "white", size=11)
    return d


# ---- Lab 2.3 · DHCP DORA ----------------------------------------------------------------
def lab23_topology():
    d = Diagram("lab-2.3-topology", 860, 370, "A DHCP server and a client on one virtual cable")
    d.group("srv", 20, 48, 390, 228, "namespace dhcp-server", "gray")
    d.box("se", 40, 88, 350, 50, "eth0\n192.168.50.1/24", "white")
    d.box("dm", 40, 150, 350, 110, "dnsmasq: DHCP only (--port=0 turns DNS off)\npool 192.168.50.100 – .150, /24, 1 h leases\n"
          "router = 192.168.50.1\ndns-server = 192.168.50.1\nlog /tmp/dnsmasq.log · leases /tmp/dnsmasq.leases",
          "purple", size=11)
    d.group("lap", 450, 48, 390, 228, "namespace laptop", "gray")
    d.box("le", 470, 88, 350, 50, "eth0\nno address yet", "white")
    d.box("dc", 470, 150, 350, 110, "dhclient -v -1 eth0\nafter DORA (tested): 192.168.50.108/24\n"
          "default via 192.168.50.1\nDNS → /etc/netns/laptop/resolv.conf\ntcpdump udp 67/68 → /tmp/dora.txt",
          "blue", size=11)
    d.edge("se", "le", "veth", both=True)
    d.box("warn", 20, 292, 820, 62, "Step 2 first: dhclient writes the DNS server it receives into resolv.conf.\n"
          "ip netns exec laptop uses /etc/netns/laptop/resolv.conf only if that file exists;\n"
          "otherwise dhclient overwrites the container's own /etc/resolv.conf.", "yellow", size=12)
    return d


def lab23_dora():
    d = Diagram("lab-2.3-dora", 860, 580, "DORA: four messages, one transaction ID (xid), then a release")
    lx, sx = 300, 640
    d.box("lap", lx - 90, 46, 180, 46, "laptop\nclient, port 68", "blue", size=11)
    d.box("srv", sx - 90, 46, 180, 46, "dhcp-server\n192.168.50.1, port 67", "purple", size=11)
    _lifeline(d, "ll-l", lx, 92, 446)
    _lifeline(d, "ll-s", sx, 92, 446)

    msgs = [  # (id, from x, to x, y, label lines, dashed)
        ("m1", lx, sx, 150, "1 · DHCPDISCOVER\n0.0.0.0:68 → 255.255.255.255:67 (broadcast)", False),
        ("m2", sx, lx, 236, "2 · DHCPOFFER · Your-IP 192.168.50.108\nlease 3600 s · RN (T1) 1800 · RB (T2) 3150\n"
                            "mask 255.255.255.0 · router + DNS 192.168.50.1", True),
        ("m3", lx, sx, 316, "3 · DHCPREQUEST (broadcast again)\nRequested-IP + Server-ID 192.168.50.1", False),
        ("m4", sx, lx, 372, "4 · DHCPACK", True),
        ("m5", lx, sx, 424, "later · DHCPRELEASE (unicast to 192.168.50.1:67)", False),
    ]
    for mid, a, b, y, label, dashed in msgs:
        _msg(d, mid, a, b, y, dashed=dashed)
        n = label.count("\n") + 1
        h = n * 11 * 1.3 + 4
        d.text(f"{mid}-t", lx + 10, y - h - 2, sx - lx - 20, h, label, size=11)

    d.box("st0", 20, 110, 260, 46, "no address yet\neth0 DOWN, then sends from 0.0.0.0", "gray", size=11)
    d.box("st1", 20, 350, 260, 64, "bound: 192.168.50.108/24\ndefault via 192.168.50.1\nnameserver 192.168.50.1", "green", size=11)
    d.box("st2", 20, 422, 260, 32, "address removed", "gray", size=11)
    d.box("sv0", 660, 100, 180, 88, "1st Discover unanswered\nin 4 of 10 test runs\n(never with --no-ping):\ndnsmasq likely pings\nthe address first",
          "white", size=11, bold_first=False)
    d.box("sv1", 660, 334, 180, 76, "server side: lease in\n/tmp/dnsmasq.leases,\nevery message in\n/tmp/dnsmasq.log",
          "white", size=11, bold_first=False)

    d.box("none", 20, 466, 400, 96, "No server running (step 4)\nDiscovers repeat with growing gaps\n"
          "(interval 3, 8, 12, 15 s) until timeout stops it\n(a Mac or Windows laptop would take 169.254.x.x)", "red", size=11)
    d.box("xid", 440, 466, 400, 96, "Read the capture (step 8)\nall four packets carry one xid (0x8ca96847)\n"
          "dhclient's log prints the Request's xid bytes reversed\n"
          "Discover and Request go to 255.255.255.255\nRN = T1 (50% of 3600 s) · RB = T2 (87.5%)", "yellow", size=11)
    return d


ALL = [lab_setup_layers, lab11_home_network, lab12_topology, lab12_switch_flooding,
       lab21_map, lab21_local_or_remote, lab21_vlsm_summaries,
       lab22_topology, lab22_fix_ladder, lab22_traceroute_mtu,
       lab23_topology, lab23_dora]
