"""Level 3 diagrams, part A: lessons 3.1 to 3.6 (Ethernet, TCP and UDP, TCP in depth, DNS, HTTP, TLS)."""
from drawio_svg import Diagram


# ---- helpers for sequence (lifeline) diagrams ---------------------------------------
def lifeline(d, id, x, y0, y1):
    """A thin vertical bar under a participant; x is its centre."""
    d.box(id, x - 6, y0, 12, y1 - y0, "", "gray")


def anchor(d, id, x, y):
    """An invisible point that an arrow can start or end at."""
    d.text(id, x - 1, y - 8, 2, 16, "", size=11)


def msg(d, id, x1, x2, y, label=None, *, dashed=False, size=11):
    """A horizontal message arrow from x1 to x2 at height y (label sits on the arrow)."""
    anchor(d, id + "_s", x1, y)
    anchor(d, id + "_t", x2, y)
    d.edge(id + "_s", id + "_t", label, dashed=dashed, size=size)


# ---- 3.1 Ethernet and switching ---------------------------------------------------------
def switch_learning():
    d = Diagram("3.1-switch-learning", 860, 480, "What a switch does with every frame")
    d.box("in", 290, 50, 280, 40, "Frame arrives on port P", "white", bold=True)
    d.box("learn", 250, 120, 360, 50, "1 · Learn\nsource MAC → port P (refresh its timer)", "green")
    d.box("look", 250, 200, 360, 50, "2 · Look up the destination MAC\nin the MAC table (FDB / CAM table)", "gray")
    outs = [("fwd", "Known unicast on port Q ≠ P\n→ forward out of Q only", "green"),
            ("unk", "Unknown unicast\n(MAC not in the table)\n→ flood: all ports but P", "orange"),
            ("bc", "Broadcast ff:ff:ff:ff:ff:ff\nor multicast → flood\n(multicast: unless the\nswitch does IGMP snooping)", "orange"),
            ("same", "Known, on port P itself\n→ filter (drop)", "gray")]
    for i, (oid, label, color) in enumerate(outs):
        d.box(oid, 20 + i * 207, 300, 195, 74, label, color, size=11)
        d.edge("look", oid)
    d.edge("in", "learn")
    d.edge("learn", "look")
    d.box("age", 20, 400, 402, 62, "3 · Age out\nforget entries not seen for 300 s (Cisco and\nLinux bridge default), so moved devices are relearned",
          "gray", size=11)
    d.box("tip", 438, 400, 402, 62, "Learns from the SOURCE MAC,\nforwards on the DESTINATION MAC",
          "yellow", bold_first=False)
    return d


def ethernet_frame():
    d = Diagram("3.1-ethernet-frame", 860, 360, "An Ethernet frame, field by field (sizes in bytes)")
    fields = [("dst", 20, 120, "Dest MAC\n6", "blue", False),
              ("src", 145, 120, "Source MAC\n6", "blue", False),
              ("vlan", 270, 110, "802.1Q tag\n4 (optional)", "white", True),
              ("et", 385, 100, "EtherType\n2", "white", False),
              ("pay", 490, 250, "Payload (the IP packet)\n46 – 1500", "green", False),
              ("fcs", 745, 95, "FCS\n4", "white", False)]
    for fid, x, w, label, color, dashed in fields:
        d.box(fid, x, 50, w, 56, label, color, dashed=dashed)
    d.box("n_mac", 20, 146, 245, 82, "Switch FORWARDS on the destination\n(it comes first, so it can decide\nearly) and LEARNS from the source",
          "gray", size=11, bold_first=False)
    d.box("n_et", 270, 146, 215, 82, "802.1Q: which VLAN\nEtherType 0x0800 IPv4,\n0x0806 ARP, 0x86DD IPv6,\n0x8100 = VLAN tag follows",
          "gray", size=11, bold_first=False)
    d.box("n_pay", 490, 146, 250, 82, "At most 1500 bytes = the MTU\nJumbo frames: 9000 (AWS VPC: 9001)\nTunnels (VPN, VXLAN) leave less,\ne.g. 1450", "gray", size=11)
    d.box("n_fcs", 745, 146, 95, 82, "CRC-32\nbad FCS =\ndropped\nsilently", "gray", size=11, bold_first=False)
    for a, b in [("dst", "n_mac"), ("src", "n_mac"), ("vlan", "n_et"), ("et", "n_et"), ("pay", "n_pay"), ("fcs", "n_fcs")]:
        d.edge(a, b)
    d.box("tcpdump", 20, 254, 820, 88,
          "What tcpdump shows: the 14-byte header + payload (never the 8-byte preamble or the FCS)\n"
          "a ping: 14 + 84 = 98 bytes · a full 1500-byte IP packet: 1514 bytes\n"
          "On the wire the frame is 1518 bytes (1522 with a VLAN tag), plus the preamble and a gap",
          "yellow", size=12)
    return d


def bridge_proof():
    d = Diagram("3.1-bridge-flood", 860, 378, "Proof on a Linux bridge: pc1 pings pc2, and pc3 sees only the broadcast")
    d.box("bcast", 20, 50, 400, 62, "① ARP request \"who-has 192.168.20.2\"\nto ff:ff:ff:ff:ff:ff (broadcast)\n→ flooded out of port2 AND port3", "orange", size=11)
    d.box("ucast", 440, 50, 400, 62, "② ARP reply and the pings\nunicast to MACs the bridge has just learned\n→ port1 and port2 only", "green", size=11)
    d.box("pc1", 20, 160, 210, 56, "pc1 · 192.168.20.1\n76:32:69:66:e4:b9", "blue")
    d.box("br0", 330, 150, 200, 76, "br0\nLinux bridge (a software\nswitch) in namespace sw", "green")
    d.box("pc2", 630, 160, 210, 56, "pc2 · 192.168.20.2\naa:94:ac:4b:59:f0", "blue")
    d.box("pc3", 330, 290, 200, 56, "pc3 · 192.168.20.3\n9a:fa:c5:4e:c9:ac", "blue")
    d.edge("pc1", "br0", "port1", both=True, size=11)
    d.edge("br0", "pc2", "port2", both=True, size=11)
    d.edge("br0", "pc3", "port3", both=True, size=11)
    d.box("fdb", 20, 262, 290, 96,
          "bridge fdb show (dynamic entries)\n76:32:69:66:e4:b9 → port1\naa:94:ac:4b:59:f0 → port2\npc3: not learned (it never sent a frame)\nageing_time 30000 = 300 s",
          "white", size=11, align="left")
    d.box("cap", 550, 262, 290, 96,
          "tcpdump on pc3\nexactly ONE frame: the ARP request\n(the broadcast); none of the ARP reply\nor the pings, which were unicast",
          "white", size=11, align="left")
    return d


# ---- 3.2 TCP and UDP ------------------------------------------------------------------------
def tcp_vs_udp():
    d = Diagram("3.2-tcp-vs-udp", 860, 490, "Same small request, two transports")
    d.group("gt", 20, 44, 400, 300, "TCP · curl to a web server on port 8080", "gray")
    d.group("gu", 440, 44, 400, 300, "UDP · nc -u to port 5000", "gray")
    # TCP lifelines
    d.box("tc", 40, 76, 130, 40, "client\n10.10.0.1", "blue", size=11)
    d.box("ts", 270, 76, 130, 40, "server\n10.10.0.2", "purple", size=11)
    lifeline(d, "tcl", 105, 116, 300)
    lifeline(d, "tsl", 335, 116, 300)
    msg(d, "t1", 111, 329, 140, "1 · SYN")
    msg(d, "t2", 329, 111, 172, "2 · SYN-ACK")
    msg(d, "t3", 111, 329, 204, "3 · ACK")
    d.box("tdata", 60, 222, 320, 42, "4 – 9 · request, response, ACKs", "white", size=11, bold=False)
    d.box("tclose", 60, 270, 320, 36, "10 – 12 · close: 4 steps in 3 packets\nFIN, then ACK + FIN in one packet, then ACK",
          "white", size=11, bold_first=False)
    d.text("tsum", 40, 314, 360, 20, "12 packets for a 22-byte answer", size=12, bold=True)
    # UDP lifelines
    d.box("uc", 460, 76, 130, 40, "client\n10.10.0.1", "blue", size=11)
    d.box("us", 690, 76, 130, 40, "server\n10.10.0.2", "purple", size=11)
    lifeline(d, "ucl", 525, 116, 300)
    lifeline(d, "usl", 755, 116, 300)
    msg(d, "u1", 531, 749, 140, "UDP, length 15")
    d.box("unote", 560, 190, 160, 74, "That's all:\nno handshake,\nno ACK, no close", "yellow", size=11)
    d.text("usum", 460, 314, 360, 20, "1 packet: the sender can't tell if it arrived", size=12, bold=True)
    # properties
    d.box("tp", 20, 358, 400, 116,
          "TCP: a phone call\nReliable: lost data re-sent, order kept, no duplicates\nA byte stream (no message boundaries)\n"
          "Flow and congestion control\nHeader 20 bytes (32 with common options)\n"
          "HTTP/1.1, HTTP/2, SSH, TLS, databases,\nthe Kubernetes API, SMTP",
          "blue", size=11, align="left")
    d.box("up", 440, 358, 400, 116,
          "UDP: a postcard\nNo guarantees: arrives once or not at all, any order\nMessages (each send = one datagram)\n"
          "No flow control: the app must be careful\nHeader 8 bytes\n"
          "DNS (mostly), DHCP, NTP, voice and video calls,\ngames, QUIC/HTTP/3, VXLAN, WireGuard",
          "purple", size=11, align="left")
    return d


def closed_port():
    d = Diagram("3.2-open-closed-filtered", 860, 330, "Open, closed or filtered: what the client gets back")
    cols = ["Port open", "Port closed (nothing listening)", "Firewall drops it"]
    for i, c in enumerate(cols):
        d.text(f"h{i}", 140 + i * 235, 44, 225, 22, c, bold=True)
    d.box("tcp", 20, 74, 110, 92, "TCP", "blue", bold=True, size=14)
    d.box("udp", 20, 180, 110, 92, "UDP", "purple", bold=True, size=14)
    cells = [
        ("to", 0, 74, "SYN → SYN-ACK → ACK\nhandshake completes", "green"),
        ("tc", 1, 74, "SYN → RST at once\n\"Connection refused\"\ncurl: (7) … after 0 ms", "orange"),
        ("td", 2, 74, "SYN … SYN … SYN …\nno answer: retries\nthen a timeout, curl: (28)", "red"),
        ("uo", 0, 180, "datagram → silence,\nor an application reply", "green"),
        ("uc", 1, 180, "datagram → ICMP port\nunreachable (if not filtered)\nnc doesn't notice: exit 0", "orange"),
        ("ud", 2, 180, "datagram → silence", "red"),
    ]
    for cid, col, y, label, color in cells:
        d.box(cid, 140 + col * 235, y, 225, 92, label, color, bold_first=False)
    d.box("note", 20, 286, 820, 32,
          "For UDP, \"no answer\" proves nothing: test with the protocol's own client (dig for DNS, ntpdate -q / chronyc for NTP)",
          "yellow", size=11)
    return d


def port_ranges():
    d = Diagram("3.2-port-ranges", 860, 290, "Port numbers: 16 bits, 0 – 65535 (TCP and UDP each have their own)")
    d.box("wk", 20, 60, 200, 56, "0 – 1023\nwell-known (system)", "green")
    d.box("reg", 220, 60, 380, 56, "1024 – 49151\nregistered", "blue")
    d.box("dyn", 600, 60, 240, 56, "49152 – 65535\ndynamic / private (IANA)", "gray")
    d.box("eph", 470, 136, 303, 46, "Linux ephemeral ports: 32768 – 60999\nnet.ipv4.ip_local_port_range", "orange",
          dashed=True, size=11)
    d.box("ewk", 20, 200, 200, 74, "22 SSH · 53 DNS\n80 HTTP · 443 HTTPS\nLinux: binding needs root\n(or a capability)",
          "white", size=11, bold_first=False)
    d.box("ereg", 320, 200, 180, 74, "3306 MySQL\n5432 PostgreSQL\n6443 Kubernetes API", "white", size=11, bold_first=False)
    d.box("edyn", 540, 200, 300, 74,
          "Your side of an outgoing connection gets\na temporary port chosen by the OS.\n53/udp and 53/tcp are different sockets.",
          "yellow", size=11, bold_first=False)
    d.edge("wk", "ewk")
    d.edge("reg", "ereg")
    return d


# ---- 3.3 TCP in depth ---------------------------------------------------------------------------
def tcp_connection():
    d = Diagram("3.3-tcp-connection", 860, 612, "One HTTP request over TCP: all 12 packets of the tested capture")
    cx, sx = 200, 640
    d.box("c", cx - 80, 44, 160, 44, "client 10.10.0.1:54370\ncurl", "blue", size=11)
    d.box("s", sx - 80, 44, 160, 44, "server 10.10.0.2:8080\nPython http.server", "purple", size=11)
    lifeline(d, "cl", cx, 88, 512)
    lifeline(d, "sl", sx, 88, 512)
    rows = [(">", "1 · SYN  seq 4014836867 (ISN)  mss 1460, sackOK, TS, wscale 10"),
            ("<", "2 · SYN-ACK  seq 3219876447  ack 4014836868 (client ISN + 1)"),
            (">", "3 · ACK  ack 1  (tcpdump shows relative numbers from here)"),
            (">", "4 · PSH  seq 1:88  87 bytes: GET /index.html HTTP/1.1"),
            ("<", "5 · ACK  ack 88  (the next byte expected)"),
            ("<", "6 · PSH  seq 1:187  186 bytes: HTTP/1.0 200 OK + headers"),
            (">", "7 · ACK  ack 187"),
            ("<", "8 · PSH  seq 187:209  the 22-byte body"),
            (">", "9 · ACK  ack 209"),
            (">", "10 · FIN  seq 88  (close step 1)"),
            ("<", "11 · ACK 89 + FIN seq 209  (steps 2 + 3 in one packet)"),
            (">", "12 · ACK  ack 210  (step 4)")]
    for i, (way, label) in enumerate(rows):
        y = 120 + i * 34
        a, b = (cx + 6, sx - 6) if way == ">" else (sx - 6, cx + 6)
        msg(d, f"m{i}", a, b, y, label)
    d.box("ph1", 20, 104, 80, 100, "Handshake\n1 – 3", "green", size=11)
    d.box("ph2", 20, 208, 80, 200, "Data\n4 – 9", "blue", size=11)
    d.box("ph3", 20, 412, 80, 98, "Close\n10 – 12\n4 steps,\n3 packets", "orange", size=11)
    d.box("st3", 720, 166, 120, 44, "ESTABLISHED\non both sides", "green", size=11)
    d.box("st12", 720, 456, 120, 58, "client now in\nTIME-WAIT\n(it closed first)", "yellow", size=11, bold_first=False)
    d.box("note", 20, 530, 820, 62,
          "Close = 4 steps (FIN, ACK, FIN, ACK), one FIN + ACK per direction; packet 11 combines two of them\n"
          "SYN and FIN each use one sequence number · an ACK names the next byte expected\n"
          "win 63 with wscale 10 = 63 × 1024 = 64,512 bytes the sender may have in flight",
          "yellow", size=11, bold_first=False)
    return d


def tcp_header():
    d = Diagram("3.3-tcp-header", 860, 480, "The TCP header: 20 bytes, plus up to 40 bytes of options")
    x0 = 30
    d.text("b0", x0, 40, 400, 18, "bits 0 – 15", size=11)
    d.text("b1", x0 + 400, 40, 400, 18, "bits 16 – 31", size=11)
    d.box("sp", x0, 60, 400, 36, "Source port (16)", "white")
    d.box("dp", x0 + 400, 60, 400, 36, "Destination port (16)", "white")
    d.box("seq", x0, 96, 800, 36, "Sequence number (32): which byte this segment starts with", "blue")
    d.box("ack", x0, 132, 800, 36, "Acknowledgement number (32): the next byte I expect from you", "blue")
    d.box("hl", x0, 168, 100, 36, "Hdr len", "white")
    d.box("fl", x0 + 100, 168, 300, 36, "Flags (see below)", "orange", bold=True)
    d.box("win", x0 + 400, 168, 400, 36, "Window (16): room left in my receive buffer", "green")
    d.box("ck", x0, 204, 400, 36, "Checksum (16)", "white")
    d.box("up", x0 + 400, 204, 400, 36, "Urgent pointer (16)", "white")
    d.box("opt", x0, 240, 800, 36, "Options (0 – 40 bytes): MSS, window scale, SACK, timestamps …", "gray", dashed=True)
    d.group("flags", x0, 300, 800, 112, "Flags, with the letter tcpdump prints", "outline", size=12)
    flags = [("CWR · W", "ECN"), ("ECE · E", "ECN"), ("URG", "urgent\npointer"), ("ACK · .", "ack field\nis valid"),
             ("PSH · P", "deliver to\nthe app now"), ("RST · R", "abort"), ("SYN · S", "start: my\nISN is X"),
             ("FIN · F", "done\nsending")]
    for i, (name, meaning) in enumerate(flags):
        color = "orange" if name.split()[0] in ("SYN", "ACK", "FIN", "RST", "PSH") else "white"
        d.box(f"f{i}", x0 + 8 + i * 99, 330, 91, 72, f"{name}\n{meaning}", color, size=11)
    d.box("note", x0, 426, 800, 36,
          "tcpdump combines them: [S.] = SYN+ACK · [P.] = PSH+ACK · [F.] = FIN+ACK · [R.] = RST+ACK",
          "yellow", size=12)
    return d


def tcp_states():
    d = Diagram("3.3-tcp-states", 860, 720, "TCP connection states (the names ss shows)")
    L, R, W = 20, 580, 260
    d.group("g_open", 10, 44, 840, 190, "Opening: client on the left, server on the right", "gray", dashed=True, size=12)
    d.box("synsent", L, 76, W, 62, "SYN-SENT · client\ncalled connect(), sent SYN\nmany = server or firewall not answering", "blue", size=11)
    d.box("listen", R, 76, W, 48, "LISTEN · server\ncalled listen(): waiting (ss -tln)", "purple", size=11)
    d.box("synrecv", R, 160, W, 62, "SYN-RECV · server\nsent SYN-ACK, waits for the final ACK\nvery many = possible SYN flood", "purple", size=11)
    d.box("est", 300, 250, 260, 50, "ESTABLISHED · both sides\nopen connection", "green")
    d.group("g_close", 10, 336, 840, 370, "Closing: the side that closes first takes the left path", "gray", dashed=True, size=12)
    d.box("fw1", L, 372, W, 48, "FIN-WAIT-1\napp closed first, sent FIN", "gray", size=11)
    d.box("fw2", L, 470, W, 48, "FIN-WAIT-2\nits FIN was acknowledged", "gray", size=11)
    d.box("tw", L, 568, W, 62, "TIME-WAIT · closed first\nnormal: kept 2 × MSL (60 s on Linux) so\nlate packets die out", "yellow", size=11)
    d.box("cw", R, 372, W, 76, "CLOSE-WAIT\npeer closed, but this app hasn't\ncalled close() yet. Many that never\ngo away = application bug (a leak)", "red", size=11)
    d.box("la", R, 488, W, 48, "LAST-ACK\napp called close(), sent FIN", "gray", size=11)
    d.box("closed", 330, 646, 200, 40, "CLOSED", "white", bold=True)
    d.edge("listen", "synrecv", "receives SYN · sends SYN-ACK", size=11)
    d.edge("synsent", "est", "receives SYN-ACK · sends ACK", points=[(150, 275)], size=11)
    d.edge("synrecv", "est", "receives ACK", points=[(710, 275)], size=11)
    d.edge("est", "fw1", "app closes first · sends FIN", points=[(430, 318), (150, 318)], size=11)
    d.edge("est", "cw", "receives FIN first · sends ACK", points=[(430, 318), (710, 318)], size=11)
    d.edge("fw1", "fw2", "receives ACK", size=11)
    d.edge("fw2", "tw", "receives FIN · sends ACK", size=11)
    d.edge("cw", "la", "app calls close() · sends FIN", size=11)
    d.edge("tw", "closed", "after 60 s", points=[(150, 666)], size=11)
    d.edge("la", "closed", "receives ACK", points=[(710, 666)], size=11)
    return d


# ---- 3.4 DNS ---------------------------------------------------------------------------------------
def dns_tree():
    d = Diagram("3.4-dns-tree", 860, 400, "DNS is a delegated tree: each parent publishes NS records (plus glue) for its children")
    d.box("root", 200, 50, 280, 66, "Root zone \".\"\nNS records for each TLD\nlab: a.root-servers.net 10.53.0.10", "purple", size=11)
    d.box("com", 30, 170, 260, 56, ".com zone\nNS records for google.com", "purple", size=11)
    d.box("lab", 390, 170, 260, 56, ".lab zone (our lab)\nns1.nic.lab 10.53.0.20", "purple", size=11)
    d.box("goo", 30, 290, 260, 66, "google.com zone\nns1.google.com\nA, AAAA, MX … records", "purple", size=11)
    d.box("ex", 390, 290, 260, 66, "example.lab zone\nns1.example.lab 10.53.0.30\nA, AAAA, CNAME, MX, TXT", "purple", size=11)
    d.edge("root", "com", "delegates (NS)", size=11)
    d.edge("root", "lab", "delegates (NS + glue)", size=11)
    d.edge("com", "goo", "delegates (NS)", size=11)
    d.edge("lab", "ex", "NS + glue A record", size=11)
    d.box("l1", 690, 50, 150, 66, "Root servers\n13 names (a – m),\nhundreds of anycast\ninstances", "gray", size=11)
    d.box("l2", 690, 170, 150, 56, "TLD servers\n.com, .org, .in, .lab", "gray", size=11)
    d.box("l3", 690, 290, 150, 66, "Authoritative\nservers\nhold the real records", "gray", size=11)
    d.text("glue", 30, 366, 800, 22,
           "Glue = an A record for a name server that lives inside the zone it serves (ns1.example.lab inside example.lab)",
           size=11, italic=True)
    return d


def dns_resolver():
    d = Diagram("3.4-resolver-at-work", 860, 640, "Lab 3.2: one question from the client, five from the resolver (tested capture)")
    xs = {"cl": 70, "rs": 240, "rt": 420, "tld": 610, "au": 790}
    heads = [("cl", "client\n10.53.0.100", "blue"), ("rs", "resolver\n10.53.0.53", "green"),
             ("rt", "root\n10.53.0.10", "purple"), ("tld", "TLD lab.\n10.53.0.20", "purple"),
             ("au", "example.lab.\n10.53.0.30", "purple")]
    for hid, label, color in heads:
        d.box(hid, xs[hid] - 55, 44, 110, 40, label, color, size=11)
        lifeline(d, hid + "_l", xs[hid], 84, 520)
    rows = [("cl", "rs", "1 · A? www.example.lab", "cl"),
            ("rs", "rt", "2 · NS? .", "rs"),
            ("rs", "rt", "3 · NS? lab.", "rs"),
            ("rt", "rs", "4 · NS a.root-servers.net", "rs"),
            ("rt", "rs", "5 · referral 0/1/2", "rs"),
            ("rs", "tld", "6 · NS? example.lab.", "rt"),
            ("tld", "rs", "7 · referral 0/1/2", "rt"),
            ("rs", "au", "8 · A? www.example.lab.", "tld"),
            ("au", "rs", "9 · * CNAME + A 10.53.0.80", "tld"),
            ("rs", "au", "10 · A? example.lab.", "tld"),
            ("au", "rs", "11 · * A 10.53.0.80", "tld"),
            ("rs", "cl", "12 · CNAME + A 10.53.0.80", "cl")]
    for i, (a, b, label, gap) in enumerate(rows):
        y = 124 + i * 34
        x1 = xs[a] + (6 if xs[b] > xs[a] else -6)
        x2 = xs[b] + (-6 if xs[b] > xs[a] else 6)
        msg(d, f"q{i}", x1, x2, y)
        gx = xs[gap]
        nxt = {"cl": "rs", "rs": "rt", "rt": "tld", "tld": "au"}[gap]
        d.text(f"ql{i}", gx + 6, y - 19, xs[nxt] - xs[gap] - 12, 16, label, size=11)
    d.box("n1", 20, 540, 410, 84,
          "Reading the capture\n+ on the client's query = recursion desired\n* on a reply = authoritative answer\n0/1/2 = 0 answers, 1 authority (NS), 2 additional (glue)",
          "yellow", size=11, align="left")
    d.box("n2", 450, 540, 390, 84,
          "What to notice\nThe root only heard \"who runs lab.?\": QNAME\nminimisation (RFC 9156), better for privacy\nwww is a CNAME, so the resolver asked again (10)",
          "yellow", size=11, align="left")
    return d


def ndots_trap():
    d = Diagram("3.4-ndots-trap", 860, 400, "In a pod (ndots:5), one lookup of google.com sends 4 questions")
    d.box("conf", 20, 44, 820, 44,
          "Pod /etc/resolv.conf:  search default.svc.cluster.local svc.cluster.local cluster.local  ·  options ndots:5\n"
          "Fewer than 5 dots in the name → try every search domain FIRST", "white", size=11)
    d.group("gl", 20, 104, 500, 216, "Without the dot: google.com (1 dot)", "gray")
    d.group("gr", 540, 104, 300, 216, "With the dot: google.com.", "gray")
    left = [("a1", "1 · google.com.default.svc.cluster.local. → NXDOMAIN", "red"),
            ("a2", "2 · google.com.svc.cluster.local. → NXDOMAIN", "red"),
            ("a3", "3 · google.com.cluster.local. → NXDOMAIN", "red"),
            ("a4", "4 · google.com. → the answer ✓", "green")]
    for i, (aid, label, color) in enumerate(left):
        d.box(aid, 36, 136 + i * 44, 468, 36, label, color, size=12)
    d.box("b1", 556, 136, 268, 36, "1 · google.com. → the answer ✓", "green")
    d.box("b2", 556, 192, 268, 112, "A trailing dot = a fully\nqualified name (FQDN):\n\"complete, add nothing\".\nOn a Mac with no search\ndomains both forms behave\nthe same.", "yellow", size=11, bold_first=False)
    d.box("cost", 20, 336, 410, 50, "4 questions, 3 wasted · ×2 for A and AAAA\non every external call → slow calls, busy CoreDNS",
          "red", size=11, bold_first=False)
    d.box("fix", 450, 336, 390, 50, "Fixes: trailing dot in config (api.stripe.com.) ·\nlower ndots via dnsConfig · NodeLocal DNSCache",
          "green", size=11, bold_first=False)
    return d


# ---- 3.5 HTTP and HTTPS -----------------------------------------------------------------------
def http_anatomy():
    d = Diagram("3.5-http-anatomy", 860, 520, "A URL, and the plain-text request and response it turns into")
    parts = [("u1", 20, 90, "https://", "scheme", "http = 80,\nhttps = 443"),
             ("u2", 110, 160, "api.shop.com", "host", "resolved by DNS;\nsent as Host"),
             ("u3", 270, 80, ":8443", "port", "optional if\nthe default"),
             ("u4", 350, 150, "/v1/orders", "path", "what to fetch"),
             ("u5", 500, 170, "?status=open", "query", "parameters"),
             ("u6", 670, 170, "#top", "fragment", "browser only:\nNEVER sent")]
    for pid, x, w, val, name, note in parts:
        color = "red" if name == "fragment" else "white"
        d.box(pid, x, 46, w, 36, val, color, bold=True, size=13)
        d.box(pid + "n", x, 88, w, 50, f"{name}\n{note}", "gray", size=11)
    d.group("req", 20, 160, 390, 300, "Request · client → server", "blue")
    d.group("resp", 450, 160, 390, 300, "Response · server → client", "purple")
    d.box("r1", 34, 192, 362, 44, "Start line: method · path · version\nGET /index.html HTTP/1.1", "white", size=11)
    d.box("r2", 34, 244, 362, 86, "Headers (Name: value)\nHost: 10.10.0.2:8080  (required in HTTP/1.1)\nUser-Agent: curl/8.5.0\nAccept: */*", "white", size=11, align="left")
    d.box("r3", 34, 338, 362, 30, "Blank line (\\r\\n\\r\\n) ends the headers", "gray", size=11)
    d.box("r4", 34, 376, 362, 44, "Body (optional)\ne.g. a POST's JSON", "white", size=11)
    d.text("r5", 34, 430, 362, 20, "87 bytes in the 3.3 capture (packet 4)", size=11, italic=True)
    d.box("s1", 464, 192, 362, 44, "Status line: version · code · reason\nHTTP/1.0 200 OK", "white", size=11)
    d.box("s2", 464, 244, 362, 86, "Headers\nServer: SimpleHTTP/0.6 Python/3.13.16\nContent-type: text/html\nContent-Length: 22", "white", size=11, align="left")
    d.box("s3", 464, 338, 362, 30, "Blank line ends the headers", "gray", size=11)
    d.box("s4", 464, 376, 362, 44, "Body: Content-Length bytes\nhello from the server", "white", size=11)
    d.text("s5", 464, 430, 362, 20, "headers 186 bytes + 22-byte body in the capture", size=11, italic=True)
    d.edge("req", "resp")
    d.box("tls", 20, 474, 820, 32, "HTTPS = exactly the same conversation inside an encrypted TLS tunnel, normally on port 443 instead of 80 (3.6)",
          "yellow", size=11)
    return d


def lb_5xx():
    d = Diagram("3.5-lb-5xx", 860, 396, "502, 503, 504: usually generated by the load balancer, not by your app")
    lanes = [("502", "502 Bad Gateway", "backend answered BADLY\nclosed, reset, or sent garbage",
              "app crashed mid-request · backend\nkeepalive timeout shorter than the\nLB's · HTTPS to an HTTP port"),
             ("503", "503 Service Unavailable", "NO HEALTHY backend: nothing\nto forward to (or deliberately\noverloaded)",
              "all targets failing health checks ·\nKubernetes Service with no ready\nendpoints"),
             ("504", "504 Gateway Timeout", "backend didn't answer\nIN TIME",
              "slow app or database · security\ngroup blocking LB → target (the\nconnect times out)")]
    d.text("h1", 20, 44, 190, 20, "The client gets", bold=True)
    d.text("h2", 250, 44, 100, 20, "Proxy / LB", bold=True)
    d.text("h3", 390, 44, 200, 20, "What happened behind it", bold=True)
    d.text("h4", 610, 44, 230, 20, "Typical cause", bold=True)
    for i, (cid, code, what, cause) in enumerate(lanes):
        y = 72 + i * 96
        d.box(f"c{cid}", 20, y, 190, 70, code, "red", bold=True)
        d.box(f"lb{cid}", 250, y + 8, 100, 54, "load\nbalancer", "orange", size=11)
        d.box(f"b{cid}", 390, y, 200, 70, what, "purple", size=11, bold_first=False)
        d.box(f"k{cid}", 610, y, 230, 70, cause, "white", size=11, bold_first=False)
        d.edge(f"lb{cid}", f"c{cid}")
        d.edge(f"lb{cid}", f"b{cid}", dashed=(cid == "503"))
    d.box("note", 20, 350, 820, 30, "Check the LB's logs and target health first · 4xx = fix the request (401 who are you? · 403 I know you, and no)",
          "yellow", size=11)
    return d


def http_versions():
    d = Diagram("3.5-http-versions", 860, 400, "HTTP versions: how requests share connections (A → A = request A, then its response)")
    lanes = [("v10", "HTTP/1.0 (1996)\nTCP", "One request per connection\nby default"),
             ("v11", "HTTP/1.1 (1997)\nTCP", "Persistent (keep-alive); Host required.\nAnswered IN ORDER: a slow response\nblocks the ones behind it"),
             ("v2", "HTTP/2 (2015)\nTCP (TLS in practice)", "Binary, multiplexed, compressed headers;\nALPN h2. One lost packet still stalls all\nstreams (TCP head-of-line blocking)"),
             ("v3", "HTTP/3 (2022)\nQUIC over UDP", "Independent streams: a loss stalls only its\nown stream; TLS 1.3 built in. Falls back\nto HTTP/2 when UDP 443 is blocked")]
    for i, (vid, name, note) in enumerate(lanes):
        y = 48 + i * 86
        d.box(vid, 20, y, 170, 70, name, "blue", size=11)
        d.box(vid + "n", 560, y, 280, 70, note, "white", size=11, bold_first=False)
    # HTTP/1.0: two connections, one request each
    d.group("c10a", 205, 56, 165, 54, "conn 1", "gray", size=11)
    d.box("a10", 215, 76, 145, 26, "A → A", "white", size=11)
    d.group("c10b", 380, 56, 165, 54, "conn 2", "gray", size=11)
    d.box("b10", 390, 76, 145, 26, "B → B", "white", size=11)
    # HTTP/1.1: one connection, in order
    d.group("c11", 205, 142, 340, 54, "one TCP connection", "gray", size=11)
    d.box("a11", 215, 162, 150, 26, "A → A (slow)", "orange", size=11)
    d.box("b11", 375, 162, 160, 26, "B waits → B", "white", size=11)
    # HTTP/2: one connection, interleaved
    d.group("c2", 205, 228, 340, 54, "one TCP connection, many streams", "gray", size=11)
    for j, lab in enumerate(["A", "B", "C", "A", "B", "C"]):
        d.box(f"s2{j}", 215 + j * 54, 248, 48, 26, lab, "white", size=11)
    # HTTP/3: QUIC streams
    d.group("c3", 205, 314, 340, 54, "one QUIC connection (UDP 443)", "gray", size=11)
    for j, lab in enumerate(["A", "B", "C"]):
        d.box(f"s3{j}", 215 + j * 110, 334, 100, 26, f"stream {lab}", "green", size=11)
    return d


# ---- 3.6 TLS and certificates ---------------------------------------------------------------
def tls13_handshake():
    d = Diagram("3.6-tls13-handshake", 860, 560, "The TLS 1.3 handshake: one round trip, then encrypted data")
    cx, sx = 180, 620
    d.box("c", cx - 80, 44, 160, 40, "Client (curl)", "blue")
    d.box("s", sx - 100, 44, 200, 40, "Server web.example.lab:8443", "purple", size=11)
    d.box("tcp", 100, 96, 620, 26, "TCP handshake already done", "gray", size=11)
    d.group("enc", 100, 222, 620, 252, "Both sides computed the same keys (ECDHE): everything below is encrypted", "yellow", size=11)
    lifeline(d, "cl", cx, 130, 480)
    lifeline(d, "sl", sx, 130, 480)
    msg(d, "m1", cx + 6, sx - 6, 160, "ClientHello: TLS versions, cipher suites, key share (X25519)\nSNI = web.example.lab · ALPN = h2, http/1.1")
    msg(d, "m2", sx - 6, cx + 6, 200, "ServerHello: TLS_AES_256_GCM_SHA384 + its key share")
    rows = [("<", "EncryptedExtensions (e.g. the ALPN choice)"),
            ("<", "Certificate (the chain: leaf + intermediates)"),
            ("<", "CertificateVerify: signed with the server's private key"),
            ("<", "Finished: a hash of the whole handshake"),
            (">", "Finished"),
            (">", "HTTP request (encrypted application data)")]
    for i, (way, label) in enumerate(rows):
        y = 266 + i * 34
        a, b = (cx + 6, sx - 6) if way == ">" else (sx - 6, cx + 6)
        msg(d, f"r{i}", a, b, y, label)
    d.box("see", 730, 140, 110, 92, "Visible to an\nobserver: SNI,\nIPs, ports,\nsizes, timing", "red", size=11, bold_first=False)
    d.box("cert", 730, 280, 110, 92, "Certificate is\nencrypted in\nTLS 1.3 (it was\nvisible in 1.2)", "white", size=11, bold_first=False)
    d.box("rtt", 20, 140, 70, 334, "1 RTT\nbefore\ndata\n\n(TLS 1.2:\n2 RTT)", "green", size=11)
    d.box("note", 20, 490, 820, 52,
          "Asymmetric keys prove identity and agree on fresh symmetric keys; symmetric crypto (AES-GCM, ChaCha20) encrypts the data.\n"
          "Ephemeral (EC)DHE keys give forward secrecy: stealing the private key later doesn't decrypt recorded traffic.",
          "yellow", size=11, bold_first=False)
    return d


def cert_chain():
    d = Diagram("3.6-cert-chain", 860, 470, "Chain of trust: the client checks each signature up to a root it already has")
    d.group("sent", 20, 44, 500, 170, "The server sends these", "gray", dashed=True, size=12)
    d.box("leaf", 34, 74, 190, 96, "Leaf certificate\nSubject CN=web.example.lab\nSAN DNS:web.example.lab\nIssuer CN=Lab Root CA\nValid 7 days · RSA 2048 key", "white", size=11)
    d.box("int", 310, 74, 196, 96, "Intermediate CA\noptional, usual in real life\n(in the lab the root\nsigns the leaf directly)", "white", size=11, dashed=True)
    d.group("store", 600, 44, 240, 170, "Client's trust store", "green", size=12)
    d.box("root", 614, 79, 212, 86, "Root CA\nself-signed\nnever sent: the client\nmust already have it", "green", size=11)
    d.text("paths", 614, 170, 212, 40, "/etc/ssl/certs (Linux)\nKeychain (macOS)", size=11)
    d.edge("leaf", "int", "signed by", size=11)
    d.edge("int", "root", "signed by", size=11)
    d.text("ch", 20, 232, 820, 20, "The checks, and the curl error when one fails", bold=True)
    checks = [("k1", "Chain reaches a\ntrusted root?", "e1", "(60) unable to get local\nissuer certificate\nunknown CA or missing\nintermediate"),
              ("k2", "Hostname matches\na SAN entry?", "e2", "(60) no alternative\ncertificate subject name\nmatches target host name"),
              ("k3", "Now inside\nnotBefore … notAfter?", "e3", "(60) certificate has\nexpired (or the client's\nclock is wrong)"),
              ("k4", "CertificateVerify\nsignature valid?", "e4", "handshake fails: the server\ncan't prove it owns the\nprivate key")]
    for i, (kid, q, eid, err) in enumerate(checks):
        x = 20 + i * 207
        d.box(kid, x, 260, 195, 50, q, "blue", size=11, bold_first=False)
        d.box(eid, x, 346, 195, 76, err, "red", size=11, bold_first=False)
        d.edge(kid, eid, "no", size=11)
    d.text("cn", 20, 432, 820, 24, "Browsers ignore the CN: only the SAN counts. -k / --insecure skips every check.", size=11, italic=True)
    return d


def tls_termination():
    d = Diagram("3.6-tls-termination", 860, 400, "Where TLS ends: three options at the load balancer")
    opts = [("t", "1 · Terminate at the load balancer", "ALB / ingress\nholds the certificate", "HTTPS", "plain HTTP", True,
             "Simple; the LB can route on\nHTTP. Traffic inside the VPC\nis unencrypted"),
            ("r", "2 · Re-encrypt", "LB terminates, then\nopens new TLS", "HTTPS", "new TLS", False,
             "Encrypted end to end;\ntwo sets of certificates"),
            ("p", "3 · Passthrough", "NLB (TCP)\nforwards the bytes", "TLS", "same TLS", False,
             "The LB can't see HTTP (no\npath routing); the backend\nmanages certificates")]
    for i, (oid, title, lb, l1, l2, plain, trade) in enumerate(opts):
        y = 44 + i * 116
        d.group(f"g{oid}", 20, y, 820, 104, title, "gray", size=12, align="left")
        d.box(f"c{oid}", 36, y + 34, 100, 54, "client", "blue")
        d.box(f"lb{oid}", 226, y + 34, 170, 54, lb, "orange", size=11, bold_first=False)
        backend = "backend\nterminates TLS" if oid == "p" else "backend"
        d.box(f"b{oid}", 486, y + 34, 130, 54, backend, "purple", size=11, bold_first=False)
        d.box(f"k{oid}", 636, y + 22, 190, 70, trade, "yellow", size=11, bold_first=False)
        d.edge(f"c{oid}", f"lb{oid}", l1, size=11)
        d.edge(f"lb{oid}", f"b{oid}", l2, dashed=plain, size=11)
    return d


ALL = [switch_learning, ethernet_frame, bridge_proof,
       tcp_vs_udp, closed_port, port_ranges,
       tcp_connection, tcp_header, tcp_states,
       dns_tree, dns_resolver, ndots_trap,
       http_anatomy, lb_5xx, http_versions,
       tls13_handshake, cert_chain, tls_termination]
