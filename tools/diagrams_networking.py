#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/networking/*.md.

Run once:  python3 tools/diagrams_networking.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "networking" / "diagrams"


def building_story():
    d = Diagram("00-building-story", 940, 610, "Docker networking explained as an apartment building")
    d.box("inet", 300, 44, 340, 46, "Outside world (internet, your browser)\nletters come in and go out through reception",
          "gray", shape="ellipse", size=11)
    d.group("host", 20, 112, 600, 478, "Building = your computer (host) · address 10.0.1.25", "gray", align="left")
    d.box("rec", 170, 150, 300, 56, "Reception = iptables NAT\nchanges the FROM / TO address on letters", "red", size=11)
    d.box("cor", 60, 262, 530, 50, "Corridor = bridge (docker0)\nconnects every flat · 172.17.0.1", "green", size=11)
    d.box("doorA", 88, 352, 200, 50, "Door = veth pair\ncorridor side ↔ flat side (eth0)", "orange", size=10)
    d.box("doorB", 363, 352, 200, 50, "Door = veth pair\ncorridor side ↔ flat side (eth0)", "orange", size=10)
    d.group("flatA", 60, 436, 255, 118, "Flat = container A", "yellow", dashed=True, size=12, valign="bottom")
    d.box("inA", 88, 452, 200, 48, "flat number 172.17.0.2\nnginx at counter 80", "white", size=11)
    d.group("flatB", 335, 436, 255, 118, "Flat = container B", "yellow", dashed=True, size=12, valign="bottom")
    d.box("inB", 363, 452, 200, 48, "flat number 172.17.0.3\napi at counter 8000", "white", size=11)
    d.edge("inet", "rec", both=True)
    d.edge("rec", "cor", both=True)
    d.edge("cor", "doorA", both=True)
    d.edge("cor", "doorB", both=True)
    d.edge("doorA", "inA", both=True)
    d.edge("doorB", "inB", both=True)
    d.box("out", 645, 150, 275, 160,
          "Letter going OUT = MASQUERADE\n(container → internet)\n\nFROM was: 172.17.0.2 (flat)\n"
          "FROM now: 10.0.1.25 (building)\nTO: google.com\n\nReception writes it in its register,\n"
          "so the reply finds flat A again",
          "blue", size=11, align="left")
    d.box("in", 645, 340, 275, 150,
          "Letter coming IN = DNAT\n(your browser → container)\n\nTO was: 10.0.1.25 : 8080\nTO now: 172.17.0.2 : 80\n\n"
          "Reception does this only because\nyou ran  docker run -p 8080:80",
          "purple", size=11, align="left")
    d.text("tip", 640, 505, 285, 70,
           "Remember:\nMASQUERADE changes FROM (going out)\nDNAT changes TO (coming in)", size=12)
    return d


def netfilter_chains():
    d = Diagram("02-netfilter-chains", 960, 560, "The 5 checkpoints a packet passes on a Linux host (netfilter hooks)")
    d.box("arrive", 20, 230, 130, 56, "Packet arrives\non eth0 or docker0", "gray", size=11)
    d.box("pre", 170, 230, 160, 56, "PREROUTING\nnat: DNAT for -p", "red", size=11)
    d.box("route", 350, 230, 150, 56, "Routing decision\nfor me, or pass it on?", "gray", size=11)
    d.box("fwd", 570, 230, 170, 56, "FORWARD\nDOCKER-USER, then Docker", "orange", size=11)
    d.box("post", 770, 230, 170, 56, "POSTROUTING\nnat: MASQUERADE / SNAT", "red", size=11)
    d.box("leave", 770, 350, 170, 50, "Packet leaves\non eth0 or docker0", "gray", size=11)
    d.box("input", 350, 80, 150, 56, "INPUT\nufw rules live here", "blue", size=11)
    d.box("proc", 570, 80, 170, 56, "Process on the host\nsshd, nginx on the host", "white", size=11)
    d.box("out", 770, 80, 170, 56, "OUTPUT\npackets the host creates", "blue", size=11)
    d.edge("arrive", "pre")
    d.edge("pre", "route")
    d.edge("route", "fwd", "pass on")
    d.edge("fwd", "post")
    d.edge("post", "leave")
    d.edge("route", "input", "for me")
    d.edge("input", "proc")
    d.edge("proc", "out")
    d.edge("out", "post")
    d.box("n-docker", 20, 430, 450, 110,
          "Container traffic never touches INPUT\nA request for -p 8080:80 goes PREROUTING → FORWARD → POSTROUTING.\n"
          "ufw only filters INPUT, so it can't block a published port.\n"
          "Fix: add your own rules to the DOCKER-USER chain,\nor publish on localhost only: -p 127.0.0.1:8080:80",
          "yellow", size=11, align="left")
    d.box("n-order", 490, 430, 450, 110,
          "Why DNAT sits in PREROUTING\nThe TO address must change before the routing decision.\n"
          "If it changed later, the kernel would already have decided\n\"this is for me\" and looked for a host process on 8080.\n"
          "MASQUERADE sits in POSTROUTING: the last step before leaving.",
          "yellow", size=11, align="left")
    return d


def dns_journey():
    d = Diagram("04-dns-journey", 940, 560, "The journey of a DNS question: who is google.com?")
    d.box("mac", 20, 60, 230, 56, "1 · Your Mac (or a container)\nchecks its own cache first", "blue", size=11)
    d.box("router", 20, 200, 230, 56, "2 · Home router 192.168.29.1\nchecks its cache", "gray", size=11)
    d.box("isp", 20, 340, 230, 56, "3 · Provider's resolver (Jio)\nasks the servers on the right", "green", size=11)
    d.box("root", 540, 60, 300, 56, "4 · Root servers\n\"I don't know. Ask the .com servers\"", "yellow", size=11)
    d.box("tld", 540, 200, 300, 56, "5 · .com servers\n\"I don't know. Ask ns1.google.com\"", "yellow", size=11)
    d.box("auth", 540, 340, 300, 56, "6 · ns1.google.com (authoritative)\n\"google.com = 142.250.146.100\"",
          "orange", size=11)
    d.edge("mac", "router", "question ↓  answer ↑", both=True)
    d.edge("router", "isp", "question ↓  answer ↑", both=True)
    d.edge("isp", "root", both=True)
    d.edge("isp", "tld", both=True)
    d.edge("isp", "auth", both=True)
    d.box("n-cache", 20, 420, 440, 120,
          "Every step remembers the answer for its TTL\n(for example 161 seconds), so the next question is fast.\n\n"
          "\"Non-authoritative answer\" = it came from a cache.\n"
          "Only step 6, the owner, gives an authoritative answer.",
          "white", size=11, align="left")
    d.box("n-where", 480, 420, 440, 120,
          "Who answers the question first?\nDocker default bridge: the host's DNS (192.168.65.7 on Desktop)\n"
          "Docker user-defined network: 127.0.0.11 (knows container names)\n"
          "Kubernetes pod: CoreDNS (its Service IP is in /etc/resolv.conf)\n"
          "AWS VPC: the VPC base address + 2, for example 10.0.0.2",
          "purple", size=11, align="left")
    return d


def debug_ladder():
    d = Diagram("06-debug-ladder", 960, 560, "Debug a connection step by step: stop at the first step that fails")
    d.text("h1", 20, 44, 240, 22, "Question to answer", size=12, bold=True)
    d.text("h2", 280, 44, 300, 22, "Command", size=12, bold=True)
    d.text("h3", 600, 44, 340, 22, "If it fails, you'll see", size=12, bold=True)
    steps = [
        ("1 · DNS\nDoes the name resolve?", "nslookup db.example.com\ngetent hosts db",
         "could not resolve host · bad address · NXDOMAIN\n→ DNS problem, not the network"),
        ("2 · Route\nIs there a path to the IP?", "ip route get 10.0.2.15\ntraceroute 10.0.2.15",
         "No route to host · Network unreachable\n→ route table, gateway, subnet"),
        ("3 · Port\nCan I reach the port?", "nc -zv 10.0.2.15 5432",
         "timed out → packets DROPPED (SG, NACL, firewall)\nrefused → reached the machine, nothing listening"),
        ("4 · Listener\nIs the app listening, and where?", "ss -lntp",
         "127.0.0.1:5432 → reachable only from inside\nport missing → the app isn't running there"),
        ("5 · Rules\nDo NAT / firewall rules allow it?", "iptables -t nat -L -n -v\nSG · NACL · NetworkPolicy",
         "rule missing, or a DROP / REJECT\n→ fix the rule, then retest step 3"),
        ("6 · App\nDoes the app answer correctly?", "curl -v http://10.0.2.15:8080/health",
         "502 · 503 · 504 → the network is fine\n→ check the backend, its health and its logs"),
    ]
    for i, (q, cmd, err) in enumerate(steps):
        y = 72 + i * 74
        d.box(f"q{i}", 20, y, 240, 58, q, "blue", size=11)
        d.box(f"c{i}", 280, y, 300, 58, cmd, "white", size=11, bold_first=False)
        d.box(f"e{i}", 600, y, 340, 58, err, "red", size=11, align="left", bold_first=False)
    for i in range(len(steps) - 1):
        d.edge(f"q{i}", f"q{i + 1}")
    d.text("footer", 20, 520, 920, 24,
           "Read the error word first: it tells you which step failed. A timeout is a DROP somewhere; refused means nobody is listening.",
           size=11)
    return d


def osi_layers():
    d = Diagram("08-osi-layers", 960, 640, "The 7 OSI layers: what each one adds, and what works there")
    d.text("h1", 20, 44, 250, 22, "Layer", size=12, bold=True)
    d.text("h2", 290, 44, 210, 22, "Data is called", size=12, bold=True)
    d.text("h3", 520, 44, 420, 22, "Examples (protocols · devices · tools)", size=12, bold=True)
    layers = [
        ("7 · Application\nwhat the program says", "data\nGET /health", "HTTP · DNS · SSH · gRPC\nALB, API gateway, ingress-nginx", "purple"),
        ("6 · Presentation\nformat, encrypt, compress", "data\nJSON · TLS records", "TLS, UTF-8, gzip, JPEG\n(in TCP/IP: part of the app)", "purple"),
        ("5 · Session\nopen, keep, close a dialog", "data", "TLS session resume, RPC sessions\n(in TCP/IP: part of the app)", "purple"),
        ("4 · Transport\nport to port, reliable or not", "segment (TCP)\ndatagram (UDP)", "TCP · UDP · QUIC\nNLB, security group, kube-proxy", "blue"),
        ("3 · Network\nhost to host, across networks", "packet\nsrc IP → dst IP", "IP · ICMP · routing · NAT\nrouter, route table, iptables", "green"),
        ("2 · Data link\nnext hop on the same network", "frame\nsrc MAC → dst MAC", "Ethernet · Wi-Fi · ARP · VLAN\nswitch, bridge (docker0), veth", "yellow"),
        ("1 · Physical\nbits on a wire or radio", "bits", "cable, fibre, radio, NIC\nhub, repeater", "orange"),
    ]
    for i, (name, unit, ex, color) in enumerate(layers):
        y = 72 + i * 68
        d.box(f"l{i}", 20, y, 250, 56, name, color, size=11)
        d.box(f"u{i}", 290, y, 210, 56, unit, "white", size=11)
        d.box(f"x{i}", 520, y, 420, 56, ex, "white", size=11, align="left")
    d.box("n-send", 20, 556, 450, 66,
          "Sending: each layer wraps the data from the layer above\n(adds its header) and passes it DOWN: encapsulation.\n"
          "Receiving: each layer reads its header and passes it UP.",
          "gray", size=11, align="left")
    d.box("n-mnemonic", 490, 556, 450, 66,
          "Remember 7 → 1: All People Seem To Need Data Processing\n"
          "TCP/IP folds 7 + 6 + 5 into one Application layer,\nand 2 + 1 into one Link layer.",
          "gray", size=11, align="left")
    return d


def osi_encapsulation():
    d = Diagram("08-osi-encapsulation", 960, 470, "Encapsulation: how curl http://10.0.2.15/health is wrapped before it leaves")
    http = ("HTTP: GET /health", "purple", 260)
    tcp = ("TCP header\nports 45000 → 80", "blue", 150)
    ip = ("IP header\n10.0.1.25 → 10.0.2.15", "green", 170)
    rows = [
        ("L7 data", [http]),
        ("L4 segment", [tcp, http]),
        ("L3 packet", [ip, tcp, http]),
        ("L2 frame", [("Eth header\nMACs of next hop", "yellow", 140), ip, tcp, http, ("FCS", "yellow", 60)]),
    ]
    for r, (label, parts) in enumerate(rows):
        y = 50 + r * 72
        d.text(f"lab{r}", 20, y, 100, 56, label, size=12, bold=True)
        x = 940 - sum(w for _, _, w in parts)
        for c, (text, color, w) in enumerate(parts):
            d.box(f"r{r}c{c}", x, y, w, 56, text, color, size=11, bold_first=False)
            x += w
    d.box("n-hop", 20, 350, 450, 104,
          "At every router hop\nThe L2 frame is thrown away and rebuilt with new MACs.\n"
          "The IP addresses stay the same end to end\n(unless NAT changes them, see 02).",
          "white", size=11, align="left")
    d.box("n-read", 490, 350, 450, 104,
          "Which device reads how deep?\nSwitch / bridge: up to L2 (MAC)\n"
          "Router / NAT / security group: up to L3–L4 (IP, port)\n"
          "ALB / ingress / proxy: up to L7 (host, path, headers)",
          "white", size=11, align="left")
    return d


ALL = [building_story, netfilter_chains, dns_journey, debug_ladder, osi_layers, osi_encapsulation]

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
