"""Level 3 diagrams, part b: the Level 3 map and lessons 3.7 to 3.11."""
from drawio_svg import Diagram


def anchor(d, id, x, y):
    """An invisible point that edges can start or end on (for sequence-style arrows)."""
    return d.box(id, x, y, 0, 0, "", "none", shape="text", valign="top")


def msg(d, id, x1, x2, y, label=None, *, dashed=False, size=11):
    """A horizontal arrow from x1 to x2 at height y, with an optional label in the middle."""
    anchor(d, f"{id}a", x1, y)
    anchor(d, f"{id}b", x2, y)
    d.edge(f"{id}a", f"{id}b", label, dashed=dashed, size=size)


# ---- Level 3 README -----------------------------------------------------------------

def level_3_map():
    d = Diagram("level-3-map", 860, 560, "Level 3 · Core protocols: the order to read the lessons")
    xs = [20, 188, 356, 524, 692]
    w, h = 148, 62
    r = [50, 140, 230, 320, 410]

    def lesson(id, col, row, label, color):
        d.box(id, xs[col], r[row], w, h, label, color, size=11)

    lesson("l1", 1, 0, "3.1 Ethernet\nframes, MACs, switch\nlearning, broadcasts", "green")
    lesson("l2", 2, 1, "3.2 TCP and UDP ★\nrefused vs timeout\nvs silence", "blue")
    lesson("l7", 0, 2, "3.7 ICMP\nping, traceroute,\nMTU black holes", "green")
    lesson("l4", 1, 2, "3.4 DNS ★\nroot → TLD →\nauthoritative", "purple")
    lesson("l8", 2, 2, "3.8 NAT ★\nSNAT, PAT, DNAT,\nIGW vs NAT gateway", "orange")
    lesson("l9", 3, 2, "3.9 Ports\ncommon ports, SSH\ntunnels, NTP", "purple")
    lesson("l3", 4, 2, "3.3 TCP in depth ★\nhandshake capture,\nTIME_WAIT, windows", "blue")
    lesson("l5", 4, 3, "3.5 HTTP and HTTPS\nrequests, 502/503/504,\nHTTP/1.1, 2 and 3", "purple")
    lesson("l6", 3, 3, "3.6 TLS ★\nTLS 1.3 handshake,\nchain of trust", "purple")
    d.box("l10", 20, r[4], 652, h,
          "3.10 Packet flow end to end ★\n\"What happens when you type a URL\": DNS → route → ARP → TCP → NAT → TLS → HTTP",
          "gray", size=11)
    lesson("l11", 4, 4, "3.11 Troubleshooting\n★ the 6-step method,\nerror → broken step", "gray")
    for a, b in [("l1", "l2"), ("l1", "l7"), ("l2", "l4"), ("l2", "l8"), ("l2", "l9"),
                 ("l3", "l5"), ("l5", "l6"), ("l10", "l11")]:
        d.edge(a, b)
    d.edge("l2", "l3", points=[(xs[4] + w / 2, r[1] + h / 2)])
    for src in ("l7", "l4", "l8", "l6"):
        x = d._by_id[src]["x"] + w / 2
        anchor(d, f"in-{src}", x, r[4])
        d.edge(src, f"in-{src}")
    d.box("note", 20, 494, 820, 48,
          "Practise as you go: Labs 3.1 to 3.5 (TCP handshake · DNS · TLS · NAT · troubleshooting challenge)\n"
          "★ = very likely interview topic (⭐ in the lessons table)",
          "yellow", size=11, bold_first=False)
    return d


# ---- 3.7 ICMP, ping and traceroute -------------------------------------------------------

def traceroute_ttl():
    d = Diagram("3.7-traceroute-ttl", 860, 520,
                "Traceroute: probes with TTL 1, 2, 3 · the router where TTL hits 0 reports back")
    cols = [20 + i * 176 for i in range(4)]
    cw, bh = 156, 50
    heads = [("h1", "h1 · the sender\n10.0.1.10", "blue"), ("r1", "r1 (router 1)\n10.0.1.1", "green"),
             ("r2", "r2 (router 2)\n10.0.12.2", "green"), ("h2", "h2 · destination\n10.0.2.10", "blue")]
    for (hid, label, color), x in zip(heads, cols):
        d.box(hid, x, 46, cw, 46, label, color)
    d.box("back", 724, 46, 116, 46, "Comes back\nto h1 (ICMP)", "white", dashed=True)
    rows = [
        [("Probe 1 · UDP\nTTL 1", "white"), ("TTL 1 → 0\ndrop, report back", "red")],
        [("Probe 2 · UDP\nTTL 2", "white"), ("TTL 2 → 1\nforward", "green"), ("TTL 1 → 0\ndrop, report back", "red")],
        [("Probe 3 · UDP\nTTL 3", "white"), ("TTL 3 → 2\nforward", "green"), ("TTL 2 → 1\nforward", "green"),
         ("arrived: no app on\nUDP port 33436", "purple")],
    ]
    replies = ["Time Exceeded\n(type 11)\nfrom 10.0.1.1",
               "Time Exceeded\n(type 11)\nfrom 10.0.12.2",
               "Port unreachable\n(type 3 code 3)\n= arrived"]
    for i, (row, reply) in enumerate(zip(rows, replies)):
        y = 112 + i * 92
        ids = []
        for j, (label, color) in enumerate(row):
            bid = f"p{i}{j}"
            d.box(bid, cols[j], y, cw, bh, label, color, size=11 if j == 3 else 12)
            ids.append(bid)
        for a, b in zip(ids, ids[1:]):
            d.edge(a, b)
        yb = y + bh + 14
        last = cols[len(row) - 1] + cw / 2
        d.edge(ids[-1], ids[0], dashed=True, points=[(last, yb), (cols[0] + cw / 2, yb)])
        d.box(f"rep{i}", 724, y, 116, bh, reply, "white", dashed=True, size=11, bold_first=False)
    d.box("out", 20, 400, 400, 104,
          "What it prints (tested)\n$ traceroute -n -q 1 10.0.2.10\n 1  10.0.1.1  0.240 ms\n 2  10.0.12.2  0.197 ms\n 3  10.0.2.10  0.177 ms",
          "white", align="left", size=12)
    d.box("arr", 440, 400, 400, 104,
          "How it knows it has arrived\nUDP probe (Linux, macOS default) → port unreachable\n"
          "-I ICMP echo (Windows tracert) → echo reply\n-T -p 443 TCP SYN → SYN-ACK\n"
          "By hand: ping -t 1 → From 10.0.1.1 Time to live exceeded",
          "yellow", align="left", size=11)
    return d

def reading_traceroute():
    d = Diagram("3.7-reading-traceroute", 860, 420, "Reading traceroute: what the hops are telling you")
    d.text("hl", 20, 40, 430, 22, "You see (one box per hop · row 1 tested, rows 2–4 examples)", bold=True)
    d.text("hr", 460, 40, 380, 22, "It means", bold=True)
    ok, star, slow = "green", "gray", "orange"
    rows = [
        ([("1\n10.0.1.1", ok), ("2\n*", star), ("3\n10.0.2.10", ok)],
         "Fine (tested): hop 2 doesn't send Time Exceeded,\nbut hop 3 answers, so the path works.\nStars only in the middle are normal.", "green"),
        ([("1", ok), ("2", ok), ("3\n*", star), ("4\n*", star), ("5\n*", star)],
         "Traffic stops after hop 2 (or ICMP is filtered\nfrom there on). Try traceroute -T -p <port>,\nthen check that network's firewall.", "red"),
        ([("3\nfast", ok), ("4\nslow", slow), ("5\nfast", ok), ("6\nfast", ok)],
         "Hop 4 is slow to generate ICMP (low priority on\nits control plane), not to forward: no problem.\nOnly latency that lasts to the destination is real.", "green"),
        ([("1", ok), None, ("3", ok)],
         "Different addresses on the same hop across\nprobes: load balancing (ECMP) over parallel paths.", "gray"),
    ]
    for i, (hops, meaning, color) in enumerate(rows):
        y = 70 + i * 74
        prev = None
        for j, hop in enumerate(hops):
            hid = f"h{i}{j}"
            x = 20 + j * 86
            if hop is None:  # one hop, two addresses (ECMP)
                d.box(f"{hid}a", x, y, 68, 26, "2 · A", ok, size=11)
                d.box(f"{hid}b", x, y + 32, 68, 26, "2 · B", ok, size=11)
                d.edge(prev, f"{hid}a")
                d.edge(prev, f"{hid}b")
                prev = (f"{hid}a", f"{hid}b")
                continue
            label, c = hop
            d.box(hid, x, y, 68, 58, label, c, dashed=(c == star), size=11, bold="\n" not in label)
            for p in (prev if isinstance(prev, tuple) else [prev] if prev else []):
                d.edge(p, hid)
            prev = hid
        d.box(f"m{i}", 460, y, 380, 58, meaning, color, size=11, bold_first=False, align="left")
    d.box("note", 20, 370, 820, 40,
          "Traceroute shows only the forward path: the way back can differ (asymmetric routing).\n"
          "In AWS, VPC routers don't decrement the TTL or appear: you see instances and gateways, not the fabric.",
          "yellow", size=11, bold_first=False)
    return d


def pmtud():
    d = Diagram("3.7-pmtud", 860, 528, "Path MTU discovery: a too-big packet with DF set, and the ICMP that fixes it")
    xs = [20, 250, 480, 710]
    nodes = [("h1", "h1\n10.0.1.10", "blue"), ("r1", "r1\n10.0.1.1", "green"),
             ("r2", "r2\n10.0.12.2", "green"), ("h2", "h2\n10.0.2.10", "blue")]
    for (nid, label, color), x in zip(nodes, xs):
        d.box(nid, x, 46, 130, 44, label, color)
    d.edge("h1", "r1", "MTU 1500", both=True, size=11)
    d.edge("r1", "r2", "MTU 1400", both=True, size=11)
    d.edge("r2", "h2", "unchanged", both=True, size=11)
    # 1: the too-big packet
    d.box("s1", 20, 116, 380, 50, "① h1 sends 1500 bytes with DF (Don't Fragment) set\nping -M do -s 1472: 1472 data + 8 ICMP + 20 IP", "white", size=11)
    d.box("s1r", 480, 116, 360, 50, "r1: 1500 > next link's 1400 and DF is set\n→ drop it (can't fragment) and tell the sender", "red", size=11)
    d.edge("s1", "s1r")
    # 2: the ICMP back
    d.box("s2", 20, 190, 820, 44,
          "② r1 → h1: ICMP type 3 code 4 · From 10.0.1.1 icmp_seq=1 Frag needed and DF set (mtu = 1400)",
          "white", dashed=True, size=11, bold=True)
    anchor(d, "s2in", 660, 190)
    d.edge("s1r", "s2in")
    # 3 and 4: cached, then it fits
    d.box("s3", 20, 258, 400, 50, "③ h1 caches path MTU 1400 for this destination\nnext 1500-byte try: local error: message too long, mtu=1400", "blue", size=11)
    d.box("s4", 440, 258, 400, 50, "④ h1 sends 1400 bytes (1372 + 28): fits\n1380 bytes from 10.0.2.10 ✓", "green", size=11)
    d.edge("s3", "s4")
    anchor(d, "s2out", 220, 234)
    d.edge("s2out", "s3")
    # black hole
    d.box("bh", 20, 334, 820, 60,
          "PMTUD black hole: a firewall drops the ICMP in ②\n"
          "h1 never learns and keeps sending 1500-byte packets, which vanish. TCP handshake and small requests work,\n"
          "large responses hang (Lab 3.5 fault 8: headers, then 0 bytes, then a timeout)", "red", size=11)
    d.box("fix", 20, 412, 400, 100,
          "Fixes (both verified in Lab 3.5)\nFix 1: allow ICMP type 3 code 4 (ICMPv6: type 2).\nNever block all ICMP.\n"
          "Fix 2: clamp the TCP MSS on the router:\niptables … -j TCPMSS --clamp-mss-to-pmtu", "green", size=11, align="left")
    d.box("where", 440, 412, 400, 100,
          "Where it bites\nVPNs and tunnels: extra headers\nVXLAN overlays in Kubernetes: MTU 1450 inside\n"
          "AWS: MTU 9001 inside a VPC, but 1500 across the\ninternet, VPN and some peering paths", "yellow", size=11, align="left")
    return d


# ---- 3.8 NAT, PAT and port forwarding ----------------------------------------------------

def snat_pat_flow():
    d = Diagram("3.8-snat-pat-flow", 860, 640, "PAT (source NAT) in action: what each hop sees, and how the reply finds its way back")
    lanes = [("laptop", 20, 200, "Laptop\n192.168.1.10", "blue"),
             ("router", 290, 280, "Router (NAT)\nLAN 192.168.1.1 · WAN 203.0.113.1", "orange"),
             ("web", 660, 180, "Web server\n203.0.113.50", "purple")]
    for lid, x, w, label, color in lanes:
        d.group(lid, x, 46, w, 424, label, color, size=12)
    L, R, W = 110, 430, 750
    msg(d, "m1", L, R, 120, "① 192.168.1.10:56500\n→ 203.0.113.50:80")
    d.box("n1", 310, 150, 240, 58, "SNAT (MASQUERADE)\nrecord it in conntrack, rewrite\nsource → 203.0.113.1:56500", "white", size=11)
    msg(d, "m2", R, W, 240, "② 203.0.113.1:56500\n→ 203.0.113.50:80")
    d.box("n2", 670, 270, 160, 58, "sees the router's\nIP, not the laptop's\n(its log: 203.0.113.1)", "white", size=11, bold_first=False)
    msg(d, "m3", W, R, 350, "③ 203.0.113.50:80\n→ 203.0.113.1:56500", dashed=True)
    d.box("n3", 310, 378, 240, 44, "look up conntrack, rewrite\ndestination → 192.168.1.10:56500", "white", size=11, bold_first=False)
    msg(d, "m4", R, L, 446, "④ 203.0.113.50:80\n→ 192.168.1.10:56500", dashed=True)
    d.text("cth", 20, 482, 820, 20, "The router's conntrack entry (tested): one line, both directions", bold=True)
    d.box("ct1", 20, 506, 405, 50, "original direction (as the laptop sent it)\nsrc=192.168.1.10 dst=203.0.113.50 sport=56500 dport=80", "blue", size=11)
    d.box("ct2", 435, 506, 405, 50, "reply direction (what the router expects back)\nsrc=203.0.113.50 dst=203.0.113.1 sport=80 dport=56500", "orange", size=11)
    d.box("nonat", 20, 572, 820, 52,
          "Without the MASQUERADE rule (tested): the SYNs still reach the web server, but from 192.168.1.10,\n"
          "a private address it has no route to. The laptop sees curl: (28) … Timeout was reached",
          "red", size=11, bold_first=False)
    return d


def translation_table():
    d = Diagram("3.8-translation-table", 860, 426, "One public IP, many inside hosts: outbound SNAT/PAT and inbound DNAT")
    d.text("hin", 20, 42, 180, 20, "Inside (private)", bold=True)
    d.text("hnat", 240, 42, 360, 20, "Router 203.0.113.1: translation table", bold=True)
    d.text("hout", 680, 42, 160, 20, "Outside (public)", bold=True)
    rows = [("in0", "Laptop\n192.168.1.10", "SNAT · 192.168.1.10:40000 ↔ 203.0.113.1:40000\nfirst host: port kept"),
            ("in1", "Second host\n192.168.1.11", "SNAT · 192.168.1.11:40000 ↔ 203.0.113.1:34851\nsame source port: port rewritten (the P in PAT)"),
            ("in2", "Laptop app\n192.168.1.10:8000", "DNAT · 203.0.113.1:8080 → 192.168.1.10:8000\nport forward: only the destination changes")]
    for i, (iid, host, entry) in enumerate(rows):
        y = 70 + i * 74
        d.box(iid, 20, y, 180, 52, host, "blue")
        d.box(f"t{i}", 240, y, 360, 52, entry, "orange" if i < 2 else "white", size=11)
    d.box("web", 680, 70, 160, 126, "Web server\n203.0.113.50:80", "purple")
    d.box("cli", 680, 218, 160, 52, "Client on the internet\n203.0.113.50", "purple", size=11)
    d.edge("in0", "t0")
    d.edge("in1", "t1")
    d.edge("t0", "web")
    d.edge("t1", "web")
    d.edge("cli", "t2")
    d.edge("t2", "in2")
    d.box("rule", 20, 296, 820, 40,
          "Before the DNAT rule (tested): curl http://203.0.113.1:8080/laptop.html → curl: (7) … Couldn't connect to server",
          "red", size=11)
    d.box("notes", 20, 350, 820, 62,
          "Only a connection's first packet (the SYN) goes through the NAT rules: the DNAT counter shows 1 packet, 60 bytes.\n"
          "conntrack translates every later packet, both ways. DNAT keeps the source: the laptop's app logged 203.0.113.50.\n"
          "PAT limit: about 64,000 ports per public IP, for each destination IP, port and protocol.",
          "yellow", size=11, bold_first=False, align="left")
    return d


def aws_nat():
    d = Diagram("3.8-aws-nat", 860, 600, "AWS: internet gateway (1:1 NAT) vs NAT gateway (outbound PAT)")
    d.group("vpc", 20, 46, 590, 424, "VPC", "gray")
    d.group("pub", 40, 76, 550, 176, "Public subnet (route to the internet gateway)", "outline", size=12)
    d.group("priv", 40, 270, 550, 184, "Private subnet (route to the NAT gateway)", "outline", size=12)
    d.box("ec2", 60, 110, 240, 52, "EC2 instance\npublic or Elastic IP", "blue")
    d.box("natgw", 330, 184, 240, 52, "NAT gateway\nPAT, outbound only", "orange")
    d.box("app", 60, 314, 240, 52, "Instance or pod\nprivate IP only", "blue")
    d.box("vpce", 330, 386, 240, 52, "VPC endpoint\nS3 · DynamoDB · ECR", "gray")
    d.box("inet", 660, 46, 180, 44, "Internet", "white", bold=True)
    d.box("igw", 660, 110, 180, 52, "Internet gateway\n1:1 static NAT", "orange")
    d.box("s3", 660, 386, 180, 52, "S3 / DynamoDB", "purple", bold=True)
    d.edge("ec2", "igw", "two-way", both=True, size=11)
    d.edge("igw", "inet", both=True)
    anchor(d, "natin", 520, 236)
    d.edge("app", "natin", "outbound", size=11, points=[(520, 340)])
    d.edge("natgw", "igw")
    d.edge("app", "vpce", "off the NAT gateway", size=11, points=[(180, 412)])
    d.edge("vpce", "s3")
    d.box("igwn", 20, 486, 410, 100,
          "Internet gateway\nTwo-way 1:1 static NAT between an instance's\nprivate IP and its public / Elastic IP.\n"
          "The instance never sees the public address\non its own interface.", "blue", size=11, align="left")
    d.box("natn", 440, 486, 400, 100,
          "NAT gateway\nLives in a public subnet: its own traffic uses the IGW.\nCharged per hour and per GB processed.\n"
          "Up to 55,000 connections to each unique destination,\nthen ErrorPortAllocation. Idle 350 s → reset.",
          "orange", size=11, align="left")
    return d


# ---- 3.9 Everyday protocols and ports -----------------------------------------------------

ENC, CLEAR, PLAIN = "green", "red", "white"


def port_group(d, gid, x, y, w, title, chips, cols=3, ch=40):
    """A titled group of port 'chips' laid out in a grid. Returns the group's bottom y."""
    gap, pad, top = 8, 12, 28
    cw = (w - 2 * pad - (cols - 1) * gap) / cols
    rows = (len(chips) + cols - 1) // cols
    h = top + rows * ch + (rows - 1) * gap + pad
    d.group(gid, x, y, w, h, title, "gray", size=12)
    for i, (label, color, *span) in enumerate(chips):
        r, c = divmod(i, cols)
        n = span[0] if span else 1
        d.box(f"{gid}{i}", x + pad + c * (cw + gap), y + top + r * (ch + gap), cw * n + gap * (n - 1), ch, label,
              color, size=11)
    return y + h


def ports_map():
    d = Diagram("3.9-ports-map", 860, 470, "Common ports (1): access, infrastructure, email and the web")
    y = port_group(d, "ra", 20, 46, 400, "Remote access and file transfer", [
        ("22/tcp\nSSH · SFTP · scp", ENC), ("23/tcp\nTelnet", CLEAR), ("21 + 20/tcp\nFTP ctrl + data", CLEAR),
        ("69/udp\nTFTP (PXE boot)", CLEAR), ("3389/tcp+udp\nRDP", ENC), ("873/tcp\nrsync daemon", CLEAR)])
    y = port_group(d, "em", 20, y + 12, 400, "Email", [
        ("25/tcp\nSMTP relay", PLAIN), ("587/tcp\nsubmit, STARTTLS", ENC), ("465/tcp\nsubmit, TLS", ENC),
        ("143 / 993 tcp\nIMAP / IMAPS", PLAIN), ("110 / 995 tcp\nPOP3 / POP3S", PLAIN)])
    port_group(d, "web", 20, y + 12, 400, "Web and APIs", [
        ("80/tcp\nHTTP", PLAIN), ("443/tcp\nHTTPS · gRPC", ENC), ("443/udp\nHTTP/3", ENC),
        ("8080 · 8443 · 8000 · 3000 · 5000\ndev servers and app containers", PLAIN, 3)], cols=3)
    y2 = port_group(d, "inf", 440, 46, 400, "Infrastructure services", [
        ("53/udp + tcp\nDNS", PLAIN), ("853/tcp\nDNS over TLS", ENC), ("67 / 68 udp\nDHCP srv / client", PLAIN),
        ("547 / 546 udp\nDHCPv6 srv/client", PLAIN), ("123/udp\nNTP (time)", PLAIN), ("514/udp\nSyslog", PLAIN), ("6514/tcp\nSyslog over TLS", ENC),
        ("161 / 162 udp\nSNMP query / trap", PLAIN), ("389 / 636 tcp\nLDAP / LDAPS", PLAIN), ("3268/tcp\nAD Global Catalog", PLAIN),
        ("88/tcp+udp\nKerberos", PLAIN), ("445/tcp\nSMB file shares", PLAIN), ("2049/tcp\nNFS (AWS EFS)", PLAIN),
        ("179/tcp\nBGP", PLAIN)])
    d.box("legend", 440, y2 + 12, 400, 452 - y2 - 12,
          "How to read it\ngreen = encrypted · red = clear text, passwords readable\n"
          "(also clear: SNMP v1/v2c, plain LDAP; SNMPv3 encrypts)\n"
          "A port is a convention (IANA, /etc/services), not a law:\nSSH can run on 2222, and allowing 443 allows anything on 443.",
          "yellow", size=11, align="left")
    return d


def ports_platform():
    d = Diagram("3.9-ports-platform", 860, 476, "Common ports (2): data stores, VPNs and overlays, Kubernetes and monitoring")
    y = port_group(d, "db", 20, 46, 400, "Databases, caches and queues (all tcp)", [
        ("3306\nMySQL / MariaDB", PLAIN), ("5432\nPostgreSQL", PLAIN), ("1433\nSQL Server", PLAIN),
        ("1521\nOracle", PLAIN), ("27017\nMongoDB", PLAIN), ("6379\nRedis", PLAIN),
        ("11211\nMemcached", PLAIN), ("5672 / 15672\nRabbitMQ AMQP/UI", PLAIN), ("9092\nKafka", PLAIN),
        ("9200\nElasticsearch / OpenSearch", PLAIN, 3)])
    port_group(d, "vpn", 20, y + 12, 400, "VPNs and overlays", [
        ("500/udp\nIPsec IKE", ENC), ("4500/udp\nIPsec NAT-T", ENC), ("IP protocol 50\nESP (not tcp/udp)", ENC),
        ("51820/udp\nWireGuard", ENC), ("1194/udp\nOpenVPN", ENC), ("4789/udp\nVXLAN (IANA)", PLAIN), ("8472/udp\nVXLAN, flannel", PLAIN),
        ("6081/udp\nGeneve (AWS GWLB)", PLAIN)])
    y2 = port_group(d, "k8s", 440, 46, 400, "Kubernetes (tcp unless shown)", [
        ("6443\nkube-apiserver", PLAIN), ("2379 / 2380\netcd client/peer", PLAIN), ("10250\nkubelet API", PLAIN),
        ("10257\ncontroller-mgr", PLAIN), ("10259\nkube-scheduler", PLAIN), ("30000–32767\nNodePorts tcp/udp", PLAIN), ("53/udp + tcp\nto CoreDNS", PLAIN)])
    y3 = port_group(d, "obs", 440, y2 + 12, 400, "Monitoring and secrets (tcp unless shown)", [
        ("9090\nPrometheus", PLAIN), ("9093\nAlertmanager", PLAIN), ("9100\nnode exporter", PLAIN),
        ("3000\nGrafana", PLAIN), ("4317 / 4318\nOTLP gRPC / HTTP", PLAIN), ("8125/udp\nStatsD", PLAIN),
        ("8200\nHashiCorp Vault", PLAIN)])
    d.box("note", 440, y3 + 12, 400, 458 - y3 - 12,
          "green = encrypted VPN traffic. ESP isn't TCP or UDP:\nfirewall rules need the protocol number (50).",
          "yellow", size=11, bold_first=False)
    return d


def ssh_keys_tunnels():
    d = Diagram("3.9-ssh-keys-tunnels", 860, 520, "SSH: two kinds of keys, and four ways to tunnel")
    d.box("hk", 20, 46, 400, 92,
          "Host key: the SERVER proves who it is\nfirst connect: confirm the fingerprint → saved in\n~/.ssh/known_hosts. Key changed (rebuilt server or\na man-in-the-middle) → REMOTE HOST IDENTIFICATION HAS CHANGED!",
          "purple", size=11, align="left")
    d.box("uk", 440, 46, 400, 92,
          "User key: YOU prove you may log in\nprivate key ~/.ssh/id_ed25519 stays on your laptop;\nthe public key goes in the server's ~/.ssh/authorized_keys\n(ssh-keygen -t ed25519, then ssh-copy-id user@server)",
          "blue", size=11, align="left")
    d.text("hc", 20, 152, 290, 20, "Command", bold=True)
    d.text("hl", 320, 152, 130, 20, "Your laptop", bold=True)
    d.text("hm", 540, 152, 130, 20, "SSH server", bold=True)
    d.text("ht", 710, 152, 130, 20, "Reaches", bold=True)
    rows = [
        ("-J jump host (ProxyJump)", "ssh -J user@bastion user@10.0.2.15", "laptop", "bastion", "10.0.2.15\n(private host)", False),
        ("-L local forward", "ssh -L 5432:db.internal:5432 user@bastion", "localhost:5432", "bastion", "db.internal:5432", False),
        ("-R remote forward", "ssh -R 8080:localhost:3000 user@server", "localhost:3000", "server :8080", "people who\nopen server:8080", True),
        ("-D dynamic SOCKS proxy", "ssh -D 1080 user@server", "SOCKS on :1080", "server", "any host the\nserver can reach", False),
    ]
    for i, (name, cmd, lap, mid, tgt, rev) in enumerate(rows):
        y = 178 + i * 72
        d.box(f"c{i}", 20, y, 290, 56, f"{name}\n{cmd}", "white", size=11, align="left")
        d.box(f"l{i}", 320, y, 130, 56, lap, "blue", size=11, bold=True)
        d.box(f"m{i}", 540, y, 130, 56, mid, "orange", size=11, bold=True)
        d.box(f"t{i}", 710, y, 130, 56, tgt, "purple", size=11, bold_first=False)
        if rev:
            d.edge(f"m{i}", f"l{i}", "tunnel", size=11)
            d.edge(f"t{i}", f"m{i}")
        else:
            d.edge(f"l{i}", f"m{i}", "tunnel", size=11)
            d.edge(f"m{i}", f"t{i}")
    d.box("aws", 20, 470, 820, 38,
          "In AWS, prefer Systems Manager Session Manager or EC2 Instance Connect: no inbound port 22, no long-lived keys, sessions logged.",
          "yellow", size=11)
    return d


# ---- 3.10 Packet flow end to end ------------------------------------------------------------

def url_journey():
    d = Diagram("3.10-url-journey", 860, 1010, "What happens when you open https://shop.example.com/cart")
    lanes = [("lb", 20, 190, "Browser / OS\nlaptop 192.168.29.42", "blue"),
             ("lr", 222, 150, "Home router (NAT)\n192.168.29.1", "orange"),
             ("ld", 384, 140, "DNS resolvers\nroot · TLD · auth", "purple"),
             ("la", 536, 160, "Load balancer (ALB)\n203.0.113.80", "orange"),
             ("lp", 708, 132, "App container", "purple")]
    for lid, x, w, label, color in lanes:
        d.group(lid, x, 44, w, 952, label, color, size=12)
    B, R, D, A, P = 115, 297, 454, 616, 774

    def note(id, x, y, w, h, label, color="white", bf=True):
        d.box(id, x, y, w, h, label, color, size=11, bold_first=bf)

    note("n1", 30, 100, 170, 58, "① parse the URL\nhttps → port 443, TLS\ncheck HSTS and caches")
    msg(d, "d1", B, R, 182, "② DNS: A/AAAA for\nshop.example.com? UDP 53")
    msg(d, "d2", R, D, 222, "recursive lookup")
    note("n2", 394, 240, 120, 44, "root → .com →\nexample.com", bf=False)
    msg(d, "d3", D, R, 304, "A 203.0.113.80\nTTL 60", dashed=True)
    msg(d, "d4", R, B, 346, "answer, cached\nfor the TTL", dashed=True)
    note("n3", 30, 372, 170, 58, "③ not on my /24 →\ndefault via 192.168.29.1\nneed the router's MAC")
    msg(d, "a1", B, R, 452, "ARP who-has\n(broadcast)")
    msg(d, "a2", R, B, 492, "ARP reply\n(unicast)", dashed=True)
    msg(d, "t1", B, R, 534, "④ TCP SYN\n:54370 → :443")
    note("n4", 230, 556, 134, 72, "⑤ NAT (PAT)\nsource → public\nIP:port, saved\nin its table", "white")
    msg(d, "t2", R, A, 654, "⑥ internet: routers,\nBGP, AWS IGW")
    msg(d, "t3", A, B, 694, "SYN-ACK", dashed=True)
    msg(d, "t4", B, A, 726, "ACK  (TCP: one round trip)")
    msg(d, "s1", B, A, 762, "⑦ TLS 1.3 ClientHello: SNI shop.example.com, ALPN h2")
    msg(d, "s2", A, B, 796, "ServerHello, certificate (ACM), Finished · browser checks chain, SAN, dates", dashed=True)
    msg(d, "h1", B, A, 830, "⑧ Finished + GET /cart (HTTP/2, encrypted)")
    msg(d, "h2", A, P, 866, "GET /cart\n+ X-Forwarded-For")
    msg(d, "h3", P, A, 906, "200 OK + HTML", dashed=True)
    msg(d, "h4", A, B, 940, "⑨ 200 OK (encrypted)", dashed=True)
    note("n5", 30, 956, 170, 30, "render the page", bf=False)
    d.box("n6", 232, 956, 598, 30, "CSS, JS, images reuse the connection (HTTP/2) · idle ones close later: FIN, then TIME_WAIT",
          "yellow", size=11)
    return d


def request_layers():
    d = Diagram("3.10-request-layers", 860, 344, "What wraps the encrypted GET /cart as it leaves the laptop's Wi-Fi card")
    layers = [
        ("L2 · 802.11 Wi-Fi frame (Ethernet on wired hops)", "dst MAC = the router's · src MAC = the laptop's", "green"),
        ("L3 · IPv4 header (20 bytes)", "src 192.168.29.42 → dst 203.0.113.80 · TTL 64", "blue"),
        ("L4 · TCP header (20–60 bytes)", "src port 54370 → dst port 443 · seq/ack · flags PSH, ACK", "blue"),
        ("TLS record (5 bytes + auth tag), between L4 and L7", "encrypted application data", "orange"),
    ]
    for i, (name, fields, color) in enumerate(layers):
        x, y = 20 + i * 24, 44 + i * 44
        d.box(f"g{i}", x, y, 820 - 2 * i * 24, 252 - i * 52, f"{name}\n{fields}", color, size=11,
              valign="top", align="left")
    d.box("l7", 116, 222, 628, 36, "L7 · HTTP/2 frames:  :method GET  ·  :path /cart  ·  :authority shop.example.com",
          "purple", size=11, bold=True)
    d.box("lab", 20, 308, 820, 26,
          "Measured in the lab for plain HTTP: 153 bytes = 14 (Ethernet) + 20 (IP) + 32 (TCP) + 87 (HTTP)",
          "yellow", size=11)
    return d


def container_pod_journey():
    d = Diagram("3.10-container-pod-journey", 860, 400, "The same journey from a Docker container and from a pod in EKS")
    d.group("gd", 20, 44, 820, 100, "Docker container on the default bridge, calling an external API", "gray", size=12, align="left")
    steps = [("dc", "Container\nDNS: host's resolv.conf\n(127.0.0.11 user-defined)", "blue"),
             ("db", "docker0 bridge\ndefault via 172.17.0.1", "green"),
             ("dh", "Host\nforwards + MASQUERADE\nto the host's IP", "orange"),
             ("dn", "Home router or AWS\nNAT gateway, then\nsteps 6–9 as above", "gray")]
    for i, (sid, label, color) in enumerate(steps):
        d.box(sid, 36 + i * 202, 74, 184, 58, label, color, size=11)
    for a, b in zip(steps, steps[1:]):
        d.edge(a[0], b[0])
    d.group("gk", 20, 160, 820, 226, "Kubernetes pod in AWS (EKS), calling a Service and then an external API",
            "gray", size=12, align="left")
    d.box("pod", 36, 190, 150, 180, "Pod\nresolv.conf →\nCoreDNS", "blue", size=11)
    d.box("dns", 216, 190, 184, 52, "① CoreDNS (kube-dns)\nndots:5 search list", "purple", size=11)
    d.box("cip", 430, 190, 184, 52, "② ClusterIP: kube-proxy\nDNATs to a healthy pod", "orange", size=11)
    d.box("bpod", 644, 190, 180, 52, "③ pod IP = a real VPC\naddress: plain routing", "blue", size=11)
    d.box("snat", 216, 290, 184, 64, "④ leaving the VPC:\nSNAT to the node IP\n(VPC CNI default)", "orange", size=11)
    d.box("ngw", 430, 290, 184, 64, "NAT gateway\n(used by the\nprivate subnet)", "orange", size=11)
    d.box("igw", 644, 290, 180, 64, "Internet gateway\n→ external API", "orange", size=11)
    anchor(d, "podname", 186, 216)
    d.edge("podname", "dns")
    d.edge("dns", "cip")
    d.edge("cip", "bpod")
    anchor(d, "podout", 186, 322)
    d.edge("podout", "snat")
    d.edge("snat", "ngw")
    d.edge("ngw", "igw")
    return d


# ---- 3.11 Troubleshooting connectivity ------------------------------------------------------

def error_to_step():
    groups = [
        ("1 · DNS", [("curl: (6) Could not resolve host: X\nwget: bad address 'X' · NXDOMAIN",
                      "The name didn't turn into an IP")]),
        ("2 · Route", [("connect: Network is unreachable (instant)", "YOUR own host has no route to that network"),
                       ("From <router> … Destination Net Unreachable", "A router on the way has no route"),
                       ("From <your IP> … Destination Host Unreachable\nNo route to host",
                        "ARP for the next hop failed: gateway or local host\nisn't answering (or ICMP host-unreachable came back)"),
                       ("Small requests work, big ones hang", "Path MTU black hole (3.7)")]),
        ("3 · Port\n(or 2)", [("curl: (28) … Timeout was reached\nnc: … Operation timed out",
                               "Dropped silently: SG, NACL, firewall, NetworkPolicy,\nwrong route, no return route, or the host is down")]),
        ("4 · Listener", [("curl: (7) Failed to connect … Couldn't connect to server\nnc: … Connection refused",
                           "Reached the machine, but nothing listens on that port\n(it answered with a TCP reset), or a firewall REJECTs"),
                          ("curl: (56) Recv failure: Connection reset by peer",
                           "Accepted, then reset. Tested: app on 127.0.0.1 behind\na port forward. Also: app crashed, TLS/HTTP mismatch")]),
        ("6 · App", [("curl: (60) SSL certificate problem …",
                      "Network fine: certificate untrusted, wrong name or\nexpired (3.6)"),
                     ("HTTP 502 / 503 / 504",
                      "Network fine: the proxy or LB got a bad reply / has\nno healthy backend / waited too long")]),
        ("Docker", [("Bind for 0.0.0.0:8081 failed: port is already allocated",
                     "Another container already uses that HOST port")]),
    ]
    rows = sum(len(g[1]) for g in groups)
    H = 46 + 26 + rows * 50 + (len(groups) - 1) * 6 + 66
    d = Diagram("3.11-error-to-step", 860, H, "Read the error first: it names the broken step")
    d.text("h1", 20, 44, 100, 22, "Step", bold=True)
    d.text("h2", 130, 44, 360, 22, "You see", bold=True)
    d.text("h3", 500, 44, 340, 22, "It means", bold=True)
    y = 70
    for gi, (step, items) in enumerate(groups):
        gh = len(items) * 50 - 8
        d.box(f"s{gi}", 20, y, 100, gh, step, "blue" if step != "Docker" else "gray", bold=True)
        for ii, (err, meaning) in enumerate(items):
            yy = y + ii * 50
            d.box(f"e{gi}{ii}", 130, yy, 360, 42, err, "red", size=11, bold_first=False, align="left")
            d.box(f"m{gi}{ii}", 500, yy, 340, 42, meaning, "white", size=11, bold_first=False, align="left")
        y += len(items) * 50 + 6
    d.box("note", 20, y + 4, 820, 48,
          "Refused = you reached the host and it said no.   Timeout = no answer at all: something dropped the packets.\n"
          "curl 8.x prints (7) … Couldn't connect to server instead of \"Connection refused\"; nc still says refused.",
          "yellow", size=11, bold_first=False)
    return d


def capture_verdicts():
    d = Diagram("3.11-capture-verdicts", 860, 404, "When you're stuck, capture: sudo tcpdump -i any -nn port 5432")
    panels = [
        (20, 44, "SYN out, nothing back", "drop", "Something on the way drops it (SG, NACL,\nfirewall), or the far end has no route back", "red"),
        (440, 44, "SYN, then RST", "rst", "Nothing listens there:\nconnection refused", "red"),
        (20, 224, "Nothing at all", "none", "Traffic isn't taking this path: DNS gave\na different IP, or a wrong route", "red"),
        (440, 224, "Capture on BOTH ends", "back", "Server sends SYN-ACK, client never gets it:\nthe problem is on the RETURN path", "red"),
    ]
    for i, (x, y, title, kind, verdict, color) in enumerate(panels):
        d.group(f"p{i}", x, y, 400, 166, title, "gray", size=12)
        d.box(f"c{i}", x + 14, y + 30, 90, 70, "client", "blue", bold=True)
        d.box(f"s{i}", x + 296, y + 30, 90, 70, "server\n:5432", "purple")
        cx, sx, mx = x + 104, x + 296, x + 200
        if kind == "drop":
            msg(d, f"a{i}", cx, mx + 30, y + 52, "SYN")
            d.box(f"x{i}", mx + 34, y + 40, 52, 24, "✗", "red", bold=True)
            msg(d, f"b{i}", cx, mx + 30, y + 84, "SYN (retry)")
            d.box(f"y{i}", mx + 34, y + 72, 52, 24, "✗", "red", bold=True)
        elif kind == "rst":
            msg(d, f"a{i}", cx, sx, y + 50, "SYN")
            msg(d, f"b{i}", sx, cx, y + 82, "RST", dashed=True)
        elif kind == "none":
            d.box(f"x{i}", cx + 20, y + 46, 152, 38, "no packets seen\non this interface", "white", dashed=True, size=11, bold_first=False)
        else:
            msg(d, f"a{i}", cx, sx, y + 50, "SYN arrives")
            msg(d, f"b{i}", sx, mx - 30, y + 82, "SYN-ACK", dashed=True)
            d.box(f"x{i}", mx - 84, y + 70, 52, 24, "✗", "red", bold=True)
        d.box(f"v{i}", x + 14, y + 110, 372, 44, verdict, color, size=11, bold_first=False)
    return d


ALL = [level_3_map, traceroute_ttl, reading_traceroute, pmtud, snat_pat_flow, translation_table, aws_nat, ports_map, ports_platform, ssh_keys_tunnels, url_journey, request_layers, container_pod_journey, error_to_step, capture_verdicts]
