"""Level 1 diagrams: networking fundamentals."""
from drawio_svg import Diagram


def level_map():
    d = Diagram("level-1-map", 860, 400, "Level 1 · Networking fundamentals: 5 lessons, about 6 hours")
    xs = [20, 300, 580]
    lessons = [
        ("l11", "1.1 · What is a network?\nLAN · WLAN · WAN · the internet\nclient–server vs peer-to-peer\n45 min"),
        ("l12", "1.2 · Network devices\nhub · switch · router · modem · AP\nfirewall · load balancer\n60 min"),
        ("l13", "1.3 · Addresses, ports, protocols\nMAC · IP · port · 5-tuple\n127.0.0.1 vs 0.0.0.0\n60 min"),
        ("l14", "1.4 · Network performance\nbits vs bytes: divide by 8\nbandwidth · latency · jitter · loss\n60 min"),
        ("l15", "1.5 · OSI and TCP/IP models\n7 layers · encapsulation\nL4 vs L7 · debug bottom up\n90 min"),
    ]
    for i, (lid, label) in enumerate(lessons):
        d.box(lid, xs[i % 3], 50 if i < 3 else 190, 260, 92, label, "blue")
    d.box("ms", 580, 190, 260, 92, "Milestone → Level 2\nIP addressing and subnetting\n(checklist below)", "green")
    d.edge("l11", "l12")
    d.edge("l12", "l13")
    d.edge("l13", "l14", points=[(710, 166), (150, 166)])
    d.edge("l14", "l15")
    d.edge("l15", "ms")
    d.box("lab1", 20, 310, 260, 56, "Lab 1.1 · Inspect your network\nafter 1.1 · Mac + Linux · 20 min", "white")
    d.box("lab2", 300, 310, 260, 56, "Lab 1.2 · Build a tiny network\nafter 1.2 · lab container · 45 min", "white")
    d.box("ex", 580, 310, 260, 56, "Level 1 exercises\nscore 80% or more", "white")
    d.edge("ex", "ms", dashed=True)
    return d


def home_network():
    d = Diagram("1.1-home-network", 860, 420, "Inside one network vs between networks")
    d.group("home", 20, 50, 360, 250, "Your home network (LAN)")
    d.box("laptop", 40, 90, 120, 40, "Laptop", "blue")
    d.box("phone", 40, 150, 120, 40, "Phone", "blue")
    d.box("tv", 40, 210, 120, 40, "Smart TV", "blue")
    d.box("hr", 220, 125, 140, 90, "Home router\nswitch + Wi-Fi\n+ router", "green")
    d.text("inside", 30, 262, 340, 30, "laptop ↔ phone: direct, never leaves home", italic=True, size=11)
    for n in ("laptop", "phone", "tv"):
        d.edge(n, "hr", both=True)
    d.box("isp", 440, 140, 130, 60, "ISP routers\nyour provider", "green")
    d.box("net", 610, 55, 230, 100, "The internet\nthousands of networks\n(autonomous systems)", "gray",
          shape="ellipse")
    d.box("google", 610, 220, 105, 50, "Google's\nnetwork", "purple")
    d.box("aws", 735, 220, 105, 50, "An AWS\nVPC", "purple")
    d.edge("hr", "isp", "link to\nprovider", both=True)
    d.edge("isp", "net", both=True)
    d.edge("net", "google", both=True)
    d.edge("net", "aws", both=True)
    d.box("in", 20, 318, 400, 52, "Inside one network (home, office floor, VPC subnet)\ndevices talk directly, through a switch or Wi-Fi AP",
          "yellow")
    d.box("out", 440, 318, 400, 52, "Between networks (home → Google)\nrouters pass each packet on, hop by hop", "yellow")
    d.text("foot", 20, 382, 820, 24,
           "The internet = independent networks that all speak IP and swap routes with BGP · the web (HTTP) is one app on it",
           size=12)
    return d


def company_network():
    d = Diagram("1.1-lan-wan-internet", 860, 470, "LAN, WLAN, WAN and the internet in one small company")
    d.group("office", 20, 50, 300, 300, "Office LAN + WLAN")
    d.box("desk", 40, 90, 120, 44, "Desktops\n(cables)", "blue")
    d.box("sw", 190, 90, 110, 44, "Switch", "green")
    d.box("ap", 40, 175, 120, 44, "Wi-Fi\naccess point", "green")
    d.box("lap", 40, 270, 120, 44, "Laptops,\nphones", "blue")
    d.box("fw", 190, 255, 110, 60, "Firewall /\nrouter", "orange")
    d.edge("desk", "sw", both=True)
    d.edge("ap", "sw", both=True)
    d.edge("lap", "ap", "Wi-Fi", dashed=True, both=True)
    d.edge("sw", "fw", both=True)
    d.box("net", 380, 60, 170, 70, "Internet", "gray", shape="ellipse", bold=True)
    d.box("cust", 610, 70, 180, 50, "Customers\n(browsers)", "blue")
    d.group("vpc", 560, 160, 280, 230, "AWS VPC", align="left")
    d.box("lb", 590, 200, 220, 40, "Load balancer", "orange")
    d.box("app", 590, 260, 220, 40, "App servers", "purple")
    d.box("db", 640, 315, 120, 60, "Database", "purple", shape="cylinder")
    d.edge("fw", "net", "internet\nlink", both=True, points=[(300, 266), (360, 266), (360, 95)])
    d.edge("net", "cust", both=True)
    d.edge("cust", "lb")
    d.edge("lb", "app")
    d.edge("app", "db")
    d.edge("fw", "vpc", "site-to-site VPN\n= a WAN link", both=True, points=[(300, 302), (560, 302)])
    d.box("note", 20, 405, 820, 52,
          "LAN / WLAN: desks on cables, laptops on Wi-Fi, all through the switch · Internet: customers reach the load balancer\n"
          "WAN: the office reaches the database privately over the VPN · Client–server everywhere: browser → LB → app → DB",
          "yellow", size=11, bold_first=False)
    return d


def client_server_p2p():
    d = Diagram("1.1-client-server-p2p", 860, 400, "Two ways programs talk: client–server and peer-to-peer")
    d.group("cs", 20, 50, 410, 275, "Client–server")
    d.box("cli", 40, 85, 140, 60, "Client\ne.g. your browser\nSTARTS the talk", "blue", size=11)
    d.box("srv", 270, 85, 140, 60, "Server\ne.g. a web server\nWAITS and answers", "purple", size=11)
    d.edge("cli", "srv", "1 · request", points=[(180, 100), (270, 100)])
    d.edge("srv", "cli", "2 · response", points=[(270, 130), (180, 130)], dashed=True)
    d.text("ex", 40, 152, 370, 34, "browser → web server · kubectl → API server\napp → PostgreSQL · dig → DNS server",
           size=11)
    d.box("csp", 40, 194, 370, 120,
          "The server holds the data: one place to manage,\nupdate, back up and secure\n"
          "Single point of failure, unless several servers\nsit behind a load balancer · scales by adding servers\n"
          "Roles, not machines: nginx is a server to browsers\nand a client to the app behind it",
          "white", size=11, align="left", bold_first=False)
    d.group("p2p", 450, 50, 390, 275, "Peer-to-peer (P2P)")
    peers = [("pa", 480, 85), ("pb", 690, 85), ("pc", 480, 150), ("pd", 690, 150)]
    for pid, x, y in peers:
        d.box(pid, x, y, 120, 40, "Peer " + pid[1].upper(), "blue")
    for a, b in (("pa", "pb"), ("pb", "pd"), ("pd", "pc"), ("pc", "pa")):
        d.edge(a, b, both=True)
    d.box("p2pp", 470, 206, 350, 108,
          "Each peer is both client and server\nPeers talk directly; no central server holds data\n"
          "No single point of failure; new peers add capacity\nHarder to control and secure\n"
          "e.g. BitTorrent, WebRTC media, blockchains",
          "white", size=11, align="left", bold_first=False)
    d.box("hyb", 20, 340, 820, 46,
          "Real systems mix them: a video call finds the other person through a server (signalling), sends audio and video\n"
          "directly peer to peer, and falls back to a relay server when NAT blocks the direct path.",
          "yellow", size=11, bold_first=False)
    return d


def devices_by_layer():
    d = Diagram("1.2-devices-by-layer", 860, 524, "How deep each device reads: from L1 (signals) up to L7 (the request)")
    gx, cw, top, step = 150, 64, 80, 46
    rows = [
        ("nic", "NIC", "blue", [(1, 2)], "Signals ↔ data for one device\nhas its own MAC address"),
        ("hub", "Hub", "green", [(1, 1)], "Nothing: repeats every bit\nout of every port (historical)"),
        ("modem", "Modem / ONT", "green", [(1, 1)], "Nothing: converts signals\nprovider's line ↔ your network"),
        ("ap", "Access point", "green", [(1, 2)], "MACs: bridges Wi-Fi radio\nand Ethernet (same LAN)"),
        ("switch", "Switch", "green", [(2, 2)], "MACs: sends each frame only\nto the destination's port"),
        ("router", "Router", "green", [(3, 3)], "IPs: routing table picks the\nnext network · stops broadcasts"),
        ("fw", "Firewall", "orange", [(3, 7)], "IPs, ports, connection state,\ncontent → allow or block"),
        ("lb", "Load balancer", "orange", [(4, 4), (7, 7)], "L4: IP + port (NLB, kube-proxy)\nL7: HTTP host, path (ALB, nginx)"),
    ]
    for i in range(7):
        d.box(f"col{i}", gx + i * cw + 2, top - 6, cw - 4, len(rows) * step + 4, "", "gray")
        d.text(f"h{i}", gx + i * cw, 50, cw, 20, f"L{i + 1}", bold=True)
    d.text("hdev", 20, 50, 120, 20, "Device", bold=True)
    d.text("hwhat", 608, 50, 232, 20, "Reads → does", bold=True)
    for j, (rid, name, color, spans, what) in enumerate(rows):
        y = top + j * step
        d.box(f"n{rid}", 20, y, 120, 38, name, color, bold=True)
        for k, (a, b) in enumerate(spans):
            label = f"L{a}" if a == b else f"L{a}–L{b}"
            d.box(f"b{rid}{k}", gx + (a - 1) * cw + 6, y + 4, (b - a + 1) * cw - 12, 30, label, color, size=11)
        d.box(f"w{rid}", 608, y, 232, 38, what, "white", size=11, align="left", bold_first=False)
    d.text("or", gx + 4 * cw + 8, top + 7 * step + 4, cw - 16, 30, "or", italic=True, size=11)
    d.box("note", 20, top + 8 * step + 10, 820, 52,
          "Higher = reads deeper = smarter decisions, but more work per packet. The layer numbers come from the OSI model (1.5).\n"
          "Cloud has them all in software: route table = router, security group = firewall, ALB = load balancer, Linux bridge = switch.",
          "yellow", size=11, bold_first=False)
    return d


def switch_learning():
    d = Diagram("1.2-switch-learning", 860, 470, "How a switch learns MAC addresses, then forwards or floods")
    panels = [(20, "Known destination: forward to ONE port", "MAC table\naa:aa → port 1\nbb:bb → port 2", False),
              (440, "Unknown destination: flood", "MAC table\naa:aa → port 1\n(bb:bb not learnt yet)", True)]
    for p, (x0, title, table, flood) in enumerate(panels):
        d.group(f"g{p}", x0, 50, 400, 260, title)
        d.box(f"sw{p}", x0 + 100, 84, 200, 72, "Switch · " + table, "green")
        d.box(f"a{p}", x0 + 15, 230, 110, 56, "PC A · aa:aa\nsends a frame\nto bb:bb", "blue", size=11)
        d.box(f"b{p}", x0 + 145, 230, 110, 56, "PC B · bb:bb\ngets it" if not flood else "PC B · bb:bb\ngets a copy",
              "blue", size=11)
        if flood:
            d.box(f"c{p}", x0 + 275, 230, 110, 56, "PC C · cc:cc\ngets a copy", "blue", size=11)
        else:
            d.box(f"c{p}", x0 + 275, 230, 110, 56, "PC C · cc:cc\nnever sees it", "gray", size=11)
        d.edge(f"a{p}", f"sw{p}", "port 1")
        d.edge(f"sw{p}", f"b{p}", "port 2")
        if flood:
            d.edge(f"sw{p}", f"c{p}", "port 3")
    steps = [("s1", "1 · Learn\nnote the SOURCE MAC of every\nframe and the port it came in on"),
             ("s2", "2 · Forward\ndestination MAC is in the table:\nsend out of that port only"),
             ("s3", "3 · Flood\nunknown MAC, or ff:ff:ff:ff:ff:ff:\nevery port except the one it came in on")]
    for i, (sid, label) in enumerate(steps):
        d.box(sid, 20 + i * 277, 324, 266, 58, label, "white", size=11)
    d.box("note", 20, 396, 820, 58,
          "Hub = repeats everything to every port: one collision domain, no privacy. Switch = each port its own collision domain\n"
          "(full duplex), but ALL ports are one broadcast domain; a router stops broadcasts. Linux bridge (docker0) = a software switch.",
          "yellow", size=11, bold_first=False)
    return d


def home_router_box():
    d = Diagram("1.2-home-router-box", 860, 480, "The \"home router\" from your provider: seven parts in one box")
    d.box("line", 20, 175, 100, 56, "Provider\nline", "gray", shape="ellipse")
    d.group("box", 140, 50, 560, 320, "The \"home router\" box")
    d.box("modem", 160, 170, 130, 66, "Modem / ONT\ntalks to the\nprovider's line", "green", size=11)
    d.box("router", 325, 170, 140, 66, "Router\nhome network\n↔ internet", "green", size=11)
    d.box("nat", 325, 80, 140, 56, "NAT\nshares one public IP", "orange", size=11)
    d.box("fw", 505, 80, 180, 56, "Firewall\nblocks unsolicited inbound", "orange", size=11)
    d.box("sw", 505, 175, 180, 56, "Switch\nthe LAN ports", "green", size=11)
    d.box("ap", 505, 280, 180, 56, "Wi-Fi access point", "green", size=11)
    d.box("dhcp", 325, 280, 140, 66, "DHCP + DNS\nforwarder\nhands out addresses", "purple", size=11)
    d.box("pc", 730, 175, 110, 56, "Wired PC", "blue")
    d.box("phone", 730, 280, 110, 56, "Phone\n(Wi-Fi)", "blue")
    d.edge("line", "modem", both=True)
    d.edge("modem", "router", both=True)
    d.edge("router", "nat", both=True)
    d.edge("nat", "fw", both=True)
    d.edge("router", "sw", both=True)
    d.edge("sw", "pc", both=True)
    d.edge("router", "ap", both=True)
    d.edge("ap", "phone", dashed=True, both=True)
    d.edge("dhcp", "router", dashed=True, both=True)
    d.text("sh", 20, 380, 820, 20, "Symptom → the part that's probably failing", bold=True, align="left")
    syms = ["Wi-Fi network not visible\n→ access point",
            "Laptop got a 169.254.x.x\naddress → DHCP",
            "Router's page works but\nnothing outside → modem\nlink or the provider",
            "Outgoing works, a console\ncan't accept incoming\n→ NAT / firewall"]
    for i, s in enumerate(syms):
        d.box(f"sym{i}", 20 + i * 207, 404, 199, 60, s, "red", size=11, bold_first=False)
    return d


def ip_mac_port():
    d = Diagram("1.3-ip-mac-port", 860, 430, "Three labels on every packet: MAC, IP and port")
    d.text("pk", 20, 42, 820, 22, "One packet on the wire, outermost header first:", bold=True, align="left")
    segs = [("smac", 20, 230, "Ethernet header: dst MAC", "yellow"),
            ("sip", 270, 230, "IP header: dst IP", "green"),
            ("sport", 520, 230, "TCP / UDP header: dst port", "blue"),
            ("sdata", 770, 70, "data", "purple")]
    for sid, x, w, label, color in segs:
        d.box(sid, x, 68, w, 36, label, color, bold=True)
    cards = [("cmac", 20, "MAC address · layer 2\n= which DOOR on this street\ne.g. 02:42:ac:11:00:02 (48 bits)\n"
                          "read by switches: next hop only\nchanges at every router", "yellow"),
             ("cip", 270, "IP address · layer 3\n= which BUILDING, anywhere\ne.g. 142.250.183.4 (IPv4, 32 bits)\n"
                         "read by routers: final destination\nsame end to end (unless NAT)", "green"),
             ("cport", 520, "Port · layer 4\n= which PERSON (program) inside\ne.g. 443 (from 0 to 65535)\n"
                           "read by the OS to pick the program\n22 SSH + 443 HTTPS on one IP", "blue")]
    for (cid, x, label, color), (sid, *_rest) in zip(cards, segs):
        d.box(cid, x, 136, 230, 90, label, color, size=11)
        d.edge(sid, cid)
    hops = [("h0", "Laptop", "blue"), ("h1", "Router 1", "green"), ("h2", "Router 2", "green"),
            ("h3", "Server\n142.250.183.4 : 443", "purple")]
    for i, (hid, label, color) in enumerate(hops):
        d.box(hid, 20 + i * 223, 256, 150, 50, label, color)
    for a, b in zip(hops, hops[1:]):
        d.edge(a[0], b[0], "new MACs")
    d.box("same", 20, 330, 400, 52, "Stays the same on every link\ndestination IP and port (unless NAT, 3.8)", "green")
    d.box("chg", 440, 330, 400, 52, "Rewritten on every link\nboth MAC addresses (found with ARP, 2.7)", "orange")
    d.text("foot", 20, 394, 820, 24,
           "Why both? IPs are hierarchical (a router stores networks, not every device); MACs are flat and only local.",
           size=12)
    return d


def ephemeral_ports():
    d = Diagram("1.3-ephemeral-ports", 860, 480, "A client connects: an ephemeral source port to the server's listening port")
    d.text("rt", 20, 42, 820, 22, "Port numbers 0 to 65535 (TCP and UDP)", bold=True, align="left")
    d.box("wk", 20, 68, 218, 44, "0–1023 well-known\nroot or a capability to listen", "gray", size=11)
    d.box("reg", 242, 68, 316, 44, "1024–49151 registered\ne.g. 3306 MySQL · 5432 PostgreSQL", "gray", size=11)
    d.box("dyn", 562, 68, 278, 44, "49152–65535 dynamic / private\nIANA's range for client ports", "gray", size=11)
    d.text("eph", 20, 124, 400, 76,
           "Ephemeral (client) ports: the OS picks one\nfor every outgoing connection, from a fixed range\n"
           "(about 28,000 ports on Linux: busy clients\nand NAT devices can run out)",
           size=11, align="left")
    d.box("linux", 450, 122, 312, 24, "Linux default: 32768–60999", "yellow", size=11, bold=True)
    d.box("winmac", 562, 150, 278, 24, "Windows, macOS: 49152–65535", "yellow", size=11)
    d.box("dock", 660, 178, 180, 24, "Docker Desktop: 55000–65535", "yellow", size=11)
    d.box("cli", 20, 228, 240, 76, "Client · 10.10.0.1\nsocket 10.10.0.1:48766\n48766 = ephemeral port,\npicked by the OS",
          "blue", size=11)
    d.box("srv", 600, 228, 240, 76, "Server · 10.10.0.2\nLISTEN 10.10.0.2:8080\nthe listening socket\nwaits for connections",
          "purple", size=11)
    d.edge("cli", "srv", "1 · to 10.10.0.2 port 8080", points=[(260, 248), (600, 248)])
    d.edge("srv", "cli", "2 · reply to 10.10.0.1 port 48766", points=[(600, 286), (260, 286)])
    d.box("tuple", 140, 322, 580, 48, "5-tuple = one connection\nTCP · 10.10.0.1 · 48766 · 10.10.0.2 · 8080", "white")
    d.box("two", 20, 388, 400, 76,
          "A second connection from the same client gets a\ndifferent source port: that's how one browser\n"
          "holds 10 connections to one website at once.\nFirewalls, NAT and conntrack all track the 5-tuple.",
          "yellow", size=11, bold_first=False)
    d.box("nacl", 440, 388, 400, 76,
          "AWS: a NACL is stateless, so it must allow the\nreturn traffic to ephemeral ports (AWS suggests\n"
          "1024–65535). Forget it and you get timeouts.\nA security group is stateful and doesn't need this.",
          "orange", size=11, bold_first=False)
    return d


def localhost_vs_all():
    d = Diagram("1.3-localhost-vs-all", 860, 480, "127.0.0.1 vs 0.0.0.0: the listening address decides who can connect")
    panels = [(20, "127.0.0.1", "App listens on 127.0.0.1:8000 (same machine only)", False),
              (440, "0.0.0.0", "App listens on 0.0.0.0:8000 (all interfaces)", True)]
    for p, (x0, bind, head, ok) in enumerate(panels):
        d.text(f"hd{p}", x0, 44, 400, 22, head, bold=True)
        d.box(f"mac{p}", x0 + 30, 72, 170, 48, "curl from the Mac\n-p 8081:8000", "blue")
        d.text(f"dl{p}", x0 + 128, 126, 270, 34, "Docker delivers the request\nto the container's eth0",
               size=11, align="left")
        d.group(f"c{p}", x0, 166, 400, 190, "Container", align="left")
        d.box(f"eth{p}", x0 + 40, 196, 150, 44, "eth0\n172.17.0.x", "green")
        d.box(f"lo{p}", x0 + 230, 196, 150, 44, "lo (loopback)\n127.0.0.1", "green")
        d.box(f"app{p}", x0 + 100, 288, 200, 52, f"Python app\nLISTEN {bind}:8000", "purple")
        d.edge(f"mac{p}", f"eth{p}")
        d.edge(f"lo{p}", f"app{p}")
        if ok:
            d.edge(f"eth{p}", f"app{p}")
        else:
            d.box(f"no{p}", x0 + 30, 248, 170, 26, "✗ nothing listens on eth0", "red", size=11)
    d.box("bad", 20, 370, 400, 50, "✗ From the Mac: Connection reset by peer\ninside the container: 200 (through lo)", "red")
    d.box("good", 440, 370, 400, 50, "✓ From the Mac: 200\nboth eth0 and lo reach the app", "green")
    d.box("note", 20, 432, 820, 36,
          "0.0.0.0 (listening) = all my IPv4 addresses · :: = all IPv6 · Flask listens on 127.0.0.1 by default: use --host=0.0.0.0",
          "yellow", size=11)
    return d


def five_measures():
    d = Diagram("1.4-five-measures", 860, 420, "Five numbers that describe a link: the motorway picture")
    d.box("a", 20, 100, 90, 130, "Host A\nsender", "blue")
    d.box("b", 750, 100, 90, 130, "Host B\nreceiver", "blue")
    d.group("link", 130, 90, 600, 150, "The link = a motorway · lanes = bandwidth")
    lanes = [[170, 250, 330, 410, 490, 570, 650], [190, 300, 380, 560, 640], [160, 230, 345, 420, 520, 600]]
    for i, xs in enumerate(lanes):
        y = 118 + i * 38
        d.box(f"lane{i}", 150, y, 560, 30, "", "outline", dashed=True)
        for k, x in enumerate(xs):
            lost = i == 1 and k == 3
            d.box(f"p{i}{k}", x, y + 4, 50, 22, "lost" if lost else "pkt", "red" if lost else "white",
                  size=11, dashed=lost)
    d.edge("a", "b", "latency: how long ONE packet takes from A to B", points=[(65, 70), (795, 70)])
    cards = [("Bandwidth", "how many lanes: the\nmost the link CAN carry\ne.g. 1 Gbit/s", "white"),
             ("Throughput", "packets that actually\nget through per second\ne.g. ~990 Mbit/s", "white"),
             ("Latency", "time for ONE packet\nto get from A to B\ne.g. 20 ms", "white"),
             ("Jitter", "how much that time\nvaries packet to packet\ne.g. ±5 ms", "white"),
             ("Packet loss", "packets that never\narrive\ne.g. 1%", "red")]
    for i, (name, body, color) in enumerate(cards):
        d.box(f"c{i}", 20 + i * 166, 262, 156, 76, f"{name}\n{body}", color, size=11)
    d.box("note", 20, 352, 820, 52,
          "A wide motorway (high bandwidth) is still a slow trip if it is long (latency) or blocked (loss).\n"
          "Bandwidth problems: a bigger pipe. Latency problems: move closer (CDN, region) or make fewer round trips.",
          "yellow", size=11, bold_first=False)
    return d


def bits_and_bytes():
    d = Diagram("1.4-bits-and-bytes", 860, 410, "Bits and bytes: link speeds are in bits, file sizes in bytes, so divide by 8")
    d.group("byte", 20, 50, 420, 88, "1 byte (capital B) = 8 bits (small b)", color="yellow")
    for i in range(8):
        d.box(f"bit{i}", 36 + i * 50, 86, 42, 36, "bit", "white", size=11)
    d.box("net", 460, 50, 380, 40, "Network speeds → bits per second\nMbit/s · Mbps · Gbps", "green")
    d.box("files", 460, 98, 380, 40, "File sizes, download counters → bytes\nMB · GB", "blue")
    d.text("hl", 20, 152, 150, 20, "Link speed", bold=True)
    d.text("hr", 270, 152, 160, 20, "Most you can download", bold=True)
    conv = [("100 Mbit/s", "12.5 MB/s"), ("1 Gbit/s", "125 MB/s"), ("10 Gbit/s", "1.25 GB/s")]
    for i, (a, b) in enumerate(conv):
        y = 178 + i * 46
        d.box(f"l{i}", 20, y, 150, 36, a, "green", bold=True)
        d.box(f"r{i}", 270, y, 160, 36, b, "blue", bold=True)
        d.edge(f"l{i}", f"r{i}", "÷ 8")
    d.box("ex", 460, 152, 380, 162,
          "Worked example: 5 GB on 100 Mbit/s\n5 GB = 5 × 1,000,000,000 bytes\n× 8 = 40,000,000,000 bits\n"
          "÷ 100,000,000 bit/s = 400 s\n≈ 6.7 minutes at best\n(headers and ACKs make it a bit slower)",
          "white", align="left")
    d.box("trap", 20, 330, 820, 64,
          "Trap: network prefixes are decimal (1 Mbit = 1,000,000 bits); some tools use binary units (1 MiB = 1,048,576 bytes).\n"
          "iperf3 prints transfer in binary MBytes and rate in decimal Mbits/sec: about 5% apart at mega, 7% at giga.\n"
          "The same 8× bit / byte confusion breaks subnetting maths too (2.1).",
          "red", size=11, bold_first=False)
    return d


def latency_parts():
    d = Diagram("1.4-latency-parts", 860, 390, "Where latency comes from: four delays, added on every hop")
    d.box("snd", 20, 56, 150, 60, "Sender\n(1) transmission", "blue")
    d.box("rtr", 335, 56, 190, 60, "Router\n(3) queuing + (4) processing", "green", size=11)
    d.box("rcv", 690, 56, 150, 60, "Receiver", "blue")
    d.edge("snd", "rtr", "(2) propagation")
    d.edge("rtr", "rcv", "(2) propagation")
    cards = [("1 · Transmission", "push the bits onto the wire\n= packet size ÷ link speed\n1500 B @ 10 Mbit/s = 1.2 ms\n"
                                  "1500 B @ 1 Gbit/s = 12 µs", "white"),
             ("2 · Propagation", "the signal crossing the cable\n~5 µs per km in fibre\nlight: ~200,000 km/s in glass\n"
                                 "depends on distance only", "white"),
             ("3 · Queuing", "waiting in a buffer behind\nother packets\n0 to hundreds of ms\ndepends on congestion", "white"),
             ("4 · Processing", "reading headers, choosing\nwhere to send the packet\nmicroseconds\ndepends on the device",
              "white")]
    for i, (name, body, color) in enumerate(cards):
        d.box(f"c{i}", 20 + i * 208, 140, 196, 88, f"{name}\n{body}", color, size=11)
    d.box("rtt", 20, 246, 400, 84,
          "RTT = round-trip time: there AND back (ping shows it)\nHTTPS needs about 2 round trips (TCP + TLS 1.3)\n"
          "before the request: at 200 ms RTT that's 400 ms;\na CDN edge 10 ms away does it in 20 ms.",
          "blue", size=11)
    d.box("phys", 440, 246, 400, 84,
          "Distance sets a floor no bandwidth can beat\nMumbai → US east coast ≈ 13,000 km (estimate)\n"
          "one way ≥ 13,000 × 5 µs = 65 ms, so RTT ≥ 130 ms\nreal RTTs are higher: cables don't run straight",
          "yellow", size=11)
    d.text("foot", 20, 344, 820, 24,
           "A faster link shrinks (1) transmission but never (2) propagation: only moving closer does that.", size=12)
    return d


def osi_vs_tcpip():
    d = Diagram("1.5-osi-vs-tcpip", 860, 480, "OSI (7 layers, the teaching model) vs TCP/IP (4 layers, what runs)")
    y0, rh, gap = 74, 42, 6
    d.text("ho", 20, 46, 230, 22, "OSI (ISO, 1984)", bold=True)
    d.text("ht", 300, 46, 230, 22, "TCP/IP", bold=True)
    d.text("hp", 580, 46, 260, 22, "Protocols", bold=True)
    osi = [("7 · Application", "purple"), ("6 · Presentation", "purple"), ("5 · Session", "purple"),
           ("4 · Transport", "blue"), ("3 · Network", "green"), ("2 · Data link", "yellow"), ("1 · Physical", "orange")]
    for i, (name, color) in enumerate(osi):
        d.box(f"o{i}", 20, y0 + i * (rh + gap), 230, rh, name, color, bold=True)
    tcp = [("Application", "purple", 0, 3, "HTTP · DNS · SSH · TLS\nformat, encryption and sessions\nlive inside the app"),
           ("Transport", "blue", 3, 1, "TCP · UDP"),
           ("Internet", "green", 4, 1, "IP · ICMP"),
           ("Link (network access)", "yellow", 5, 2, "Ethernet · Wi-Fi · ARP")]
    for i, (name, color, start, n, protos) in enumerate(tcp):
        y, h = y0 + start * (rh + gap), n * rh + (n - 1) * gap
        d.box(f"t{i}", 300, y, 230, h, name, color, bold=True)
        d.box(f"p{i}", 580, y, 260, h, protos, "white", bold_first=False)
        d.edge(f"t{i}", f"p{i}")
    d.box("say", 20, 418, 820, 50,
          "Say: \"OSI is a reference model for talking about networks; TCP/IP is what's implemented. We still use OSI numbers,\n"
          "like L4 vs L7 load balancers.\" Some books give TCP/IP 5 layers, keeping Physical separate.",
          "yellow", size=11, bold_first=False)
    return d


def l4_vs_l7():
    d = Diagram("1.5-l4-vs-l7", 860, 450, "L4 vs L7 load balancer: what it can read decides what it can do")
    d.group("g4", 20, 50, 400, 380, "L4 load balancer: AWS NLB, kube-proxy")
    d.box("c4", 130, 88, 180, 40, "Client", "blue")
    d.box("lb4", 100, 172, 240, 56, "L4 load balancer\nreads IP + port only", "orange")
    for i in range(3):
        d.box(f"s4{i}", 40 + i * 120, 276, 100, 40, f"server {i + 1}", "purple")
        d.edge("lb4", f"s4{i}")
    d.edge("c4", "lb4", "TCP / UDP connection")
    d.box("n4", 40, 334, 360, 82,
          "Forwards whole TCP / UDP connections\nVery fast · keeps the client's IP\n"
          "Can't route by path: it never reads HTTP\nAny TCP / UDP: databases, DNS, game servers",
          "white", size=11, align="left", bold_first=False)
    d.group("g7", 440, 50, 400, 380, "L7 load balancer: ALB, nginx, Envoy, Ingress")
    d.box("c7", 550, 88, 180, 40, "Client", "blue")
    d.box("lb7", 500, 172, 280, 56, "L7 load balancer\nreads HTTP: host, path, headers", "orange")
    d.box("api", 460, 276, 170, 40, "API servers", "purple")
    d.box("web", 650, 276, 170, 40, "web servers", "purple")
    d.edge("c7", "lb7", "HTTPS request")
    d.edge("lb7", "api", "e.g. path /api")
    d.edge("lb7", "web", "e.g. other paths")
    d.box("n7", 460, 334, 360, 82,
          "Routes by host name, path or header\nTerminates TLS · adds X-Forwarded-For\n"
          "Can do auth and WAF rules\nAlso: HAProxy, Kubernetes Gateway API",
          "white", size=11, align="left", bold_first=False)
    return d


ALL = [level_map, home_network, company_network, client_server_p2p, devices_by_layer, switch_learning,
       home_router_box, ip_mac_port, ephemeral_ports, localhost_vs_all, five_measures, bits_and_bytes,
       latency_parts, osi_vs_tcpip, l4_vs_l7]
