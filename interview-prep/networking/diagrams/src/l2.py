"""Level 2 diagrams: IP addressing and subnetting."""
from drawio_svg import Diagram


def routing_decision():
    d = Diagram("2.7-routing-decision", 860, 600, "What a host does for every packet it sends")
    d.box("app", 300, 50, 260, 40, "App sends a packet to IP D", "white", bold=True)
    d.box("lookup", 280, 120, 300, 56, "Route lookup\nlongest prefix match wins", "blue")
    d.box("noroute", 20, 220, 230, 56, "No route at all\n✗ Network is unreachable", "red")
    d.box("conn", 290, 220, 240, 56, "Connected route (D is local)\nnext hop = D itself", "green")
    d.box("gw", 570, 220, 270, 56, "Route via a gateway (or default)\nnext hop = gateway's IP", "orange")
    d.box("arp", 300, 320, 260, 56, "Next hop's MAC already in\nthe neighbour (ARP) table?", "gray")
    d.box("arpreq", 570, 420, 270, 56, "ARP broadcast\n\"Who has <next-hop IP>?\"", "purple")
    d.box("send", 250, 420, 260, 72, "Send the frame\ndst MAC = next hop's MAC\ndst IP = D (never changes)", "green")
    d.box("fail", 570, 520, 270, 56, "No reply after ~3 s\n✗ Destination Host Unreachable", "red")
    d.box("tip", 20, 520, 490, 56, "IP address = where the packet is going\nMAC address = who picks it up next (changes every hop)",
          "yellow", bold_first=False)
    d.edge("app", "lookup")
    d.edge("lookup", "noroute")
    d.edge("lookup", "conn")
    d.edge("lookup", "gw")
    d.edge("conn", "arp")
    d.edge("gw", "arp")
    d.edge("arp", "send", "yes")
    d.edge("arp", "arpreq", "no")
    d.edge("arpreq", "send", "reply")
    d.edge("arpreq", "fail", "no reply")
    return d


def longest_prefix_match():
    d = Diagram("2.7-longest-prefix-match", 860, 380, "Longest prefix match: the most specific matching route wins")
    d.text("hl", 20, 44, 330, 22, "Routing table on h1 (4 routes overlap)", bold=True)
    d.text("hr", 560, 44, 280, 22, "Destination → route the kernel uses", bold=True)
    rows = [("r0", "default (0.0.0.0/0) via 10.0.1.1\n0 bits fixed: matches everything", "gray"),
            ("r8", "10.0.0.0/8 via 172.31.0.8\n8 bits fixed", "blue"),
            ("r24", "10.0.2.0/24 via 10.0.1.1\n24 bits fixed", "green"),
            ("r25", "10.0.2.128/25 via 172.31.0.25\n25 bits fixed: 10.0.2.128 – .255", "orange")]
    dests = [("d0", "8.8.8.8", "only /0 matches"),
             ("d8", "10.9.9.9", "/0 and /8 match"),
             ("d24", "10.0.2.10", "/0, /8, /24 match\n(.10 is below .128)"),
             ("d25", "10.0.2.200", "/0, /8, /24, /25 match")]
    for i, ((rid, label, color), (did, ip, why)) in enumerate(zip(rows, dests)):
        y = 74 + i * 62
        d.box(rid, 20, y, 330, 48, label, color)
        d.box(did, 600, y, 200, 48, ip, "white", bold=True, size=13)
        d.edge(did, rid, why)
    d.box("note", 20, 324, 820, 44,
          "Length first. The metric (Linux) or administrative distance (Cisco) only breaks ties between routes of the SAME length.",
          "yellow", size=12)
    return d


def hop_by_hop():
    d = Diagram("2.7-hop-by-hop", 860, 370, "One ping from h1 to h2: what changes on each link")
    nodes = [("h1", "h1\n10.0.1.10\ndefault via 10.0.1.1", "blue"),
             ("r1", "r1\n10.0.1.1 | 10.0.12.1\n10.0.2.0/24 via 10.0.12.2", "green"),
             ("r2", "r2\n10.0.12.2 | 10.0.2.1\n10.0.1.0/24 via 10.0.12.1", "green"),
             ("h2", "h2\n10.0.2.10\ndefault via 10.0.2.1", "blue")]
    for i, (nid, label, color) in enumerate(nodes):
        d.box(nid, 20 + i * 213, 50, 170, 66, label, color, size=11)
    for a, b in zip(nodes, nodes[1:]):
        d.edge(a[0], b[0], both=True)
    links = [("Link 1: h1 → r1", "MAC  h1 → r1's eth0", "64"),
             ("Link 2: r1 → r2", "MAC  r1's eth1 → r2's eth1", "63"),
             ("Link 3: r2 → h2", "MAC  r2's eth0 → h2", "62")]
    for i, (name, mac, ttl) in enumerate(links):
        d.box(f"l{i}", 107 + i * 213, 146, 206, 84, f"{name}\n{mac}\nIP  10.0.1.10 → 10.0.2.10\nTTL {ttl}",
              "white", size=11, align="left")
    d.box("same", 20, 256, 260, 96, "Never changes\nsource and destination IP\n(unless NAT is in the path)", "green", size=11)
    d.box("chg", 300, 256, 260, 96, "Rewritten by every router\nboth MAC addresses (a new ARP\non each link) and TTL − 1", "orange", size=11)
    d.box("back", 580, 256, 260, 96, "The way back needs routes too\nh2 and r2 must know 10.0.1.0/24,\nelse: timeout and no error", "red", size=11)
    return d


# ---- helpers for the diagrams below --------------------------------------------------------

def _pt(d, id, x, y):
    """An invisible anchor point at (x, y), so an arrow can start or end exactly there."""
    d.text(id, x, y - 8, 0, 16, "")
    return id


def _arrow(d, id, x1, y1, x2, y2, label=None, **kw):
    """A straight arrow from (x1, y1) to (x2, y2), e.g. a message between two lifelines."""
    d.edge(_pt(d, id + "_a", x1, y1), _pt(d, id + "_b", x2, y2), label, size=11, **kw)


def _lifeline(d, id, cx, y_top, y_bottom, label, color):
    """A sequence-diagram participant: a head box and a dashed line down from it."""
    d.box(id, cx - 110, y_top, 220, 48, label, color)
    d.box(id + "_line", cx - 6, y_top + 48, 12, y_bottom - y_top - 48, "", "gray", dashed=True)


# ---- Level 2 map (README) ------------------------------------------------------------------

def level_2_map():
    d = Diagram("level-2-map", 860, 390, "Level 2 path: an arrow means \"this lesson builds on that one\"")
    xs, w, h = [15, 228, 441, 655], 190, 62
    y1, y2, y3 = 52, 166, 280
    d.box("l21", xs[0], y1, w, h, "2.1 Binary, decimal, hex\n128 64 32 16 8 4 2 1", "blue")
    d.box("l22", xs[1], y1, w, h, "2.2 IPv4 ranges ★\nprivate, public, special", "blue")
    d.box("l23", xs[2], y1, w, h, "2.3 Masks and CIDR ★\n/N = mask, AND, block size", "blue")
    d.box("l24", xs[3], y1, w, h, "2.4 Subnetting ★\nmost asked: six questions", "orange")
    d.box("l26", xs[1], y2, w, h, "2.6 IPv6\n128 bits, /64, SLAAC, NDP", "blue")
    d.box("l27", xs[2], y2, w, h, "2.7 Routes and ARP ★\ngateway, longest prefix", "green")
    d.box("l25", xs[3], y2, w, h, "2.5 VLSM, summarisation\nlargest first · /24s → /22", "blue")
    d.box("l28", xs[2], y3, w, h, "2.8 DHCP\nDORA, leases, 169.254.x.x", "green")
    d.box("l3", xs[3], y3, w, h, "Level 3\ncore networking protocols", "white")
    d.text("how", xs[0], y2, w, h, "Read 2.1 → 2.8 in order.\nTimes and goals: table below.",
           size=11, italic=True)
    d.box("drill", xs[0], y3, 400, h,
          "Practice alongside\nLabs 2.1 (subnetting) · 2.2 (routing) · 2.3 (DHCP)\ndrill sets A–E: 15 minutes on paper, every day",
          "yellow", size=11)
    for a, b in [("l21", "l22"), ("l22", "l23"), ("l23", "l24"), ("l23", "l26"), ("l24", "l27"),
                 ("l24", "l25"), ("l27", "l28"), ("l28", "l3")]:
        d.edge(a, b)
    return d


# ---- 2.1 Binary, decimal and hex -------------------------------------------------------------

def octet_place_values():
    d = Diagram("2.1-octet-place-values", 860, 420, "One octet = 8 bits, worth 128 64 32 16 8 4 2 1")
    vals = [128, 64, 32, 16, 8, 4, 2, 1]
    sup = ["2⁷", "2⁶", "2⁵", "2⁴", "2³", "2²", "2¹", "2⁰"]
    cx = [200 + i * 66 for i in range(8)]
    cw = 60
    d.text("h0", 15, 48, 175, 46, "Place value\n(each is double the\none to its right)", size=11, align="left")
    for i, v in enumerate(vals):
        d.box(f"pv{i}", cx[i], 50, cw, 40, f"{v}\n{sup[i]}", "gray", size=12)
    d.text("hres", 735, 50, 110, 40, "Result", bold=True)
    # binary -> decimal
    d.box("la", 15, 104, 175, 48, "Binary → decimal\nadd the values of the 1s", "white", size=11)
    for i, b in enumerate("10101100"):
        lab = f"1\n+{vals[i]}" if b == "1" else "0\n·"
        d.box(f"a{i}", cx[i], 104, cw, 48, lab, "green" if b == "1" else "white", size=11)
    d.box("ra", 735, 104, 110, 48, "128+32+8+4\n= 172", "green", size=12)
    # decimal -> binary
    d.box("lb", 15, 166, 175, 48, "Decimal → binary: 168\nfits? write 1 and subtract", "white", size=11)
    left = 168
    for i, v in enumerate(vals):
        bit = "1" if left >= v else "0"
        left = left - v if bit == "1" else left
        d.box(f"b{i}", cx[i], 166, cw, 48, f"{bit}\n{left} left", "green" if bit == "1" else "white", size=11)
    d.box("rb", 735, 166, 110, 48, "168 =\n10101000", "green", size=12)
    # a whole address
    d.text("lc", 15, 240, 175, 48, "10.0.1.25 is four octets:\nall 32 bits", size=11, align="left")
    octs = [("10 = 8 + 2", "00001010"), ("0", "00000000"), ("1", "00000001"), ("25 = 16 + 8 + 1", "00011001")]
    for i, (dec, bits) in enumerate(octs):
        d.box(f"o{i}", 200 + i * 162, 240, 154, 48, f"{dec}\n{bits}", "white", size=12)
    d.box("net", 200, 296, 478, 30, "network part: /24 = the first 24 bits = 3 octets", "blue", size=11)
    d.box("host", 686, 296, 159, 30, "host: last 8 bits", "orange", size=11)
    d.box("note", 15, 344, 830, 62,
          "All 8 bits on: 128+64+32+16+8+4+2+1 = 255, so an octet is 0–255 (256 values).\n"
          "/N counts BITS, never bytes: /24 = 3 octets · /20 = 2 octets + 4 bits of the 3rd.",
          "yellow", bold_first=False)
    return d


def mask_octets():
    d = Diagram("2.1-mask-octets", 860, 420, "Mask octets fill with 1s from the left · block size = 256 − mask")
    heads = [(15, 60, "1s"), (90, 280, "Bits"), (384, 90, "Decimal"), (488, 120, "Shortcut"),
             (622, 100, "Block size"), (736, 109, "Prefix\n3rd · 4th octet")]
    for i, (x, w, t) in enumerate(heads):
        d.text(f"h{i}", x, 42, w, 32, t, bold=True, size=11)
    dec = [128, 192, 224, 240, 248, 252, 254, 255]
    for r in range(8):
        y = 78 + r * 36
        n = r + 1
        d.text(f"n{r}", 15, y, 60, 30, f"{n}", bold=True)
        for j in range(8):
            one = j < n
            d.box(f"c{r}_{j}", 90 + j * 35, y, 31, 30, "1" if one else "0", "green" if one else "white", size=12)
        d.box(f"d{r}", 384, y, 90, 30, f"{dec[r]}", "blue", bold=True, size=13)
        short = "start" if r == 0 else f"{dec[r - 1]} + {dec[r] - dec[r - 1]}"
        d.text(f"s{r}", 488, y, 120, 30, short, size=12)
        d.box(f"k{r}", 622, y, 100, 30, f"{256 - dec[r]}", "orange", size=12)
        d.text(f"p{r}", 736, y, 109, 30, f"/{16 + n} · /{24 + n}", size=12)
    d.box("note", 15, 374, 830, 36,
          "Each mask value = the previous one + half of what was added last.  Block size = the gap between one subnet and the next (2.4).",
          "yellow", size=11)
    return d


def hex_bytes():
    d = Diagram("2.1-hex-bytes", 860, 430, "Hex: 1 digit = 4 bits (a nibble), 2 digits = 1 byte")
    for i, (h, n, b) in enumerate([("a", 10, "1010"), ("b", 11, "1011"), ("c", 12, "1100"),
                                   ("d", 13, "1101"), ("e", 14, "1110"), ("f", 15, "1111")]):
        d.box(f"x{i}", 15 + i * 140, 46, 130, 40, f"{h} = {n}\n{b}", "gray", size=12)
    d.text("ex", 15, 98, 640, 24, "Worked example: the last 4 bytes of your router's IPv6 address, c0a8:1d01",
           bold=True, size=12, align="left")
    cols = [("c0", "1100 0000", "12 × 16 + 0", "192"), ("a8", "1010 1000", "10 × 16 + 8", "168"),
            ("1d", "0001 1101", "1 × 16 + 13", "29"), ("01", "0000 0001", "0 × 16 + 1", "1")]
    for i, (hx, bits, calc, dec) in enumerate(cols):
        x = 15 + i * 162
        d.box(f"hx{i}", x, 130, 150, 36, hx, "white", bold=True, size=15)
        d.box(f"bi{i}", x, 186, 150, 32, bits, "gray", size=12)
        d.box(f"ca{i}", x, 238, 150, 32, calc, "white", size=12)
        d.box(f"de{i}", x, 290, 150, 36, dec, "blue", bold=True, size=15)
        d.edge(f"hx{i}", f"bi{i}")
        d.edge(f"bi{i}", f"ca{i}")
        d.edge(f"ca{i}", f"de{i}")
    d.box("res", 665, 186, 180, 140,
          "= 192.168.29.1\nthe router's IPv4\naddress, in hex inside\nits IPv6 address\n(tested on the Mac,\nOct 2026)",
          "green", size=12)
    d.box("rule", 665, 130, 180, 36, "digit × 16 + digit", "yellow", size=12)
    d.box("mac", 15, 350, 270, 60, "MAC d6:15:f1:59:b2:a3\n6 bytes = 12 hex digits = 48 bits", "white", size=11)
    d.box("v6", 295, 350, 270, 60, "IPv6 group 2405\n4 hex digits = 16 bits", "white", size=11)
    d.box("ox", 575, 350, 270, 60, "0x means \"this is hex\"\n0xff = 255 · hex 10 = 16, not 10", "white", size=11)
    return d


# ---- 2.2 IPv4 addresses and ranges -----------------------------------------------------------

def address_map():
    d = Diagram("2.2-address-map", 860, 520, "Every IPv4 address is private, special-purpose or public")
    gx, gw, bw = [15, 295, 575], 270, 250
    d.group("gpriv", gx[0], 44, gw, 386, "Private · RFC 1918\nfree to reuse · not routed",
            "gray", size=12)
    d.group("gspec", gx[1], 44, gw, 466, "Special-purpose\nreserved (IANA registry)",
            "gray", size=12)
    d.group("gpub", gx[2], 44, gw, 386, "Public: everything else\nunique · routed on the internet",
            "gray", size=12)
    priv = [("10.0.0.0/8\n10.0.0.0 – 10.255.255.255\n16,777,216 · AWS VPCs", 58),
            ("172.16.0.0/12\n172.16.0.0 – 172.31.255.255\n1,048,576 · Docker 172.17.0.0/16", 58),
            ("192.168.0.0/16\n192.168.0.0 – 192.168.255.255\n65,536 · home Wi-Fi 192.168.29.x", 58)]
    y = 96
    for i, (lab, h) in enumerate(priv):
        d.box(f"p{i}", gx[0] + 10, y, bw, h, lab, "blue")
        y += h + 8
    d.box("nat", gx[0] + 10, y, bw, 44, "Going out to the internet?\nNAT swaps in a public IP (3.8)", "orange")
    y += 52
    d.box("plan", gx[0] + 10, y, bw, 82,
          "Plan so ranges never overlap\nother VPCs, offices, VPNs and\nDocker's 172.17.0.0/16: overlaps\ncan't be routed without NAT",
          "yellow", size=11)
    spec = [("127.0.0.0/8 · loopback\nlocalhost · never leaves the machine", 40),
            ("169.254.0.0/16 · link-local\nself-assigned when DHCP fails (APIPA)\nAWS: IMDS .169.254 · VPC DNS .169.253", 52),
            ("100.64.0.0/10 · shared (CGNAT)\nISPs, mobile · EKS secondary pod CIDR", 40),
            ("224.0.0.0/4 · multicast (class D)\ne.g. 224.0.0.5 = all OSPF routers", 40),
            ("0.0.0.0/8 · \"this network\"\nsource 0.0.0.0: no address yet (DHCP)\nlistening on 0.0.0.0: all interfaces", 52),
            ("255.255.255.255 · limited broadcast\neveryone on this LAN (DHCP Discover)", 40),
            ("Documentation (TEST-NET-1/2/3)\n192.0.2.0/24 · 198.51.100.0/24\n203.0.113.0/24 (\"a public IP\" in labs)", 52),
            ("240.0.0.0/4 · reserved (class E)\n198.18.0.0/15 · benchmarking", 40)]
    y = 96
    for i, (lab, h) in enumerate(spec):
        d.box(f"s{i}", gx[1] + 10, y, bw, h, lab, "white", size=11)
        y += h + 6
    pub = [("8.8.8.8 · Google DNS\nreachable from anywhere", 44, "purple"),
           ("49.36.x.x · your router's WAN side\nwhat websites see (after NAT)", 44, "purple"),
           ("Trap: 172.32.0.1 is PUBLIC\n172.16.0.0/12 = 172.16 – 172.31 only", 44, "red"),
           ("Who hands them out\nIANA → 5 regional registries\n(APNIC for India) → ISPs → you.\nIPv4 has run out: addresses are\nnow re-used, transferred, bought", 86, "yellow"),
           ("Classes A–E: history only\nalways state the prefix length", 44, "white")]
    y = 96
    for i, (lab, h, c) in enumerate(pub):
        d.box(f"u{i}", gx[2] + 10, y, bw, h, lab, c, size=11)
        y += h + 8
    return d


def real_addresses():
    d = Diagram("2.2-real-addresses", 860, 470, "Classify every address in a real setup: only public ones cross the internet")
    d.box("inet", 300, 46, 260, 64, "Internet\nonly public addresses are routed", "gray", shape="ellipse")
    d.group("home", 15, 130, 400, 270, "Home", "gray", dashed=True)
    d.group("aws", 445, 130, 400, 270, "AWS VPC", "gray", dashed=True)
    d.box("rtr", 75, 160, 280, 58, "Home router (NAT)\nWAN 49.36.x.x · public (from your ISP)\nLAN 192.168.29.1 · private", "orange", size=11)
    d.box("lap", 75, 248, 280, 52, "Your laptop\n192.168.29.10 · private (192.168.0.0/16)", "blue", size=11)
    d.box("ctr", 75, 330, 280, 52, "Docker container on the laptop\n172.17.0.2 · private (172.16.0.0/12)", "blue", size=11)
    d.box("igw", 505, 160, 280, 58, "Internet gateway\nmaps public 54.x.x.x ↔ 10.0.1.25\n54.x.x.x never appears on the instance", "orange", size=11)
    d.box("ec2", 505, 248, 280, 52, "EC2 instance\neth0 10.0.1.25 · private (10.0.0.0/8)", "blue", size=11)
    d.box("imds", 505, 330, 280, 52, "Instance metadata 169.254.169.254\nlink-local: only from the instance", "purple", size=11)
    d.edge("inet", "rtr", both=True)
    d.edge("inet", "igw", both=True)
    d.edge("rtr", "lap", both=True)
    d.edge("lap", "ctr", both=True)
    d.edge("igw", "ec2", both=True)
    d.edge("ec2", "imds")
    d.box("note", 15, 414, 830, 44,
          "Docker lab, test 3: the container and the Mac got the SAME public IP back from checkip.amazonaws.com\n"
          "(tested on the Mac, Oct 2026): neither private address ever reached the internet.",
          "yellow", size=11, bold_first=False)
    return d


def cast_types():
    d = Diagram("2.2-cast-types", 860, 304, "Unicast, broadcast, multicast, anycast: who receives one packet")
    panels = [("Unicast: one → one", ["host", "host", "host"], [1], "Almost all traffic\nbrowser → web server", "white"),
              ("Broadcast: one → all", ["host", "host", "host"], [0, 1, 2],
               "255.255.255.255 or a subnet's\nbroadcast · ARP, DHCP\nnever crosses a router", "white"),
              ("Multicast: one → group", ["joined", "not", "joined"], [0, 2],
               "224.0.0.5 = all OSPF routers\nIPv6 has no broadcast:\nit uses multicast", "white"),
              ("Anycast: one → nearest", ["1.1.1.1\nfar", "1.1.1.1\nnearest", "1.1.1.1\nfar"], [1],
               "1.1.1.1, 8.8.8.8: many servers\nannounce one address;\nrouting picks the closest", "white")]
    for i, (title, recv, hit, ex, _) in enumerate(panels):
        x = 15 + i * 210
        d.group(f"g{i}", x, 46, 200, 244, title, "gray", size=12)
        d.box(f"snd{i}", x + 60, 82, 80, 32, "sender", "blue", size=11)
        for j, r in enumerate(recv):
            on = j in hit
            color = "purple" if (i == 3 and on) else ("green" if on else "white")
            d.box(f"r{i}_{j}", x + 8 + j * 64, 156, 56, 38, r, color, size=11, bold_first=False)
            if on:
                d.edge(f"snd{i}", f"r{i}_{j}")
        d.text(f"ex{i}", x + 5, 206, 190, 76, ex, size=11)
    return d


# ---- 2.3 Subnet masks and CIDR ---------------------------------------------------------------

def _bitx(k, x0=182):
    """x of bit k (0-31) in a 32-bit row: 19 px cells, 1 px apart, 9 px between octets."""
    return x0 + (k // 8) * 168 + (k % 8) * 20


def _bitrow(d, pid, y, bits, colors):
    for k, b in enumerate(bits):
        d.box(f"{pid}{k}", _bitx(k), y, 19, 26, b, colors(k, b), size=11)


def _b32(*octets):
    return "".join(format(o, "08b") for o in octets)


def mask_and():
    d = Diagram("2.3-mask-and", 860, 430, "The mask's 1s mark the network bits: address AND mask = network address")
    n = 26
    d.box("bn", _bitx(0), 46, _bitx(n - 1) + 19 - _bitx(0), 24, "26 network bits (/26): the mask is 1", "blue", size=11)
    d.box("bh", _bitx(n), 46, _bitx(31) + 19 - _bitx(n), 24, "6 host bits", "orange", size=11)
    rows = [("Address 192.168.10.70", _b32(192, 168, 10, 70), lambda k, b: "blue" if k < n else "white"),
            ("Mask 255.255.255.192", _b32(255, 255, 255, 192), lambda k, b: "green" if b == "1" else "gray"),
            ("AND = 192.168.10.64", _b32(192, 168, 10, 64), lambda k, b: "blue" if k < n else "white"),
            ("Broadcast 192.168.10.127", _b32(192, 168, 10, 127), lambda k, b: "blue" if k < n else "orange")]
    for i, (lab, bits, col) in enumerate(rows):
        y = 80 + i * 32
        d.text(f"l{i}", 15, y, 162, 26, lab, size=11, bold=(i == 2), align="left")
        _bitrow(d, f"r{i}_", y, bits, col)
    d.box("net", 15, 218, 270, 44, "Network 192.168.10.64\nhost bits all 0", "blue")
    d.box("hosts", 295, 218, 270, 44, "Hosts .65 – .126\n2⁶ − 2 = 62 usable", "green")
    d.box("bc", 575, 218, 270, 44, "Broadcast 192.168.10.127\nhost bits all 1", "orange")
    d.text("q", 15, 280, 830, 22, "Local or remote? The host ANDs the destination with its OWN mask, then compares",
           bold=True, align="left")
    d.box("dst", 15, 310, 200, 50, "Send to\n192.168.10.130", "white")
    d.box("and", 245, 310, 270, 50, "130 AND 192 = 128\n10000010 AND 11000000 = 10000000", "gray", size=11)
    d.box("rem", 545, 310, 300, 50, "192.168.10.128 ≠ my network .64\n→ remote: send it to the gateway (2.7)", "orange", size=11)
    d.edge("dst", "and")
    d.edge("and", "rem")
    d.box("note", 15, 376, 830, 40,
          "Both addresses start with 192.168.10. but sit in different /26s: do the AND, don't trust how they look.",
          "yellow", size=12)
    return d


def block_size_lines():
    d = Diagram("2.3-block-size", 860, 380, "By hand: block size = 256 − mask octet; the network is the multiple at or below")
    d.text("h1", 15, 42, 830, 24, "192.168.10.70/26 → interesting octet: the 4th · mask 192 · block 256 − 192 = 64",
           bold=True, align="left")
    for i, lab in enumerate([".0 – .63", ".64 – .127\n70 is in here", ".128 – .191", ".192 – .255"]):
        d.box(f"a{i}", 15 + i * 210, 70, 200, 44, lab, "green" if i == 1 else "white", size=12)
    for i, lab in enumerate(["Network .64\nlargest multiple of 64 ≤ 70", "Hosts .65 – .126\n= 62 usable",
                             "Broadcast .127\nnext network (.128) − 1"]):
        d.box(f"ar{i}", 15 + i * 280, 124, 270, 42, lab, ["blue", "green", "orange"][i], size=11)
    d.text("h2", 15, 184, 830, 24, "10.0.37.5/20 → interesting octet: the 3rd · mask 240 · block 256 − 240 = 16",
           bold=True, align="left")
    for i, lab in enumerate(["0 – 15", "16 – 31", "32 – 47\n37 is in here", "48 – 63", "64 – 79", "… 240 – 255"]):
        d.box(f"b{i}", 15 + i * 140, 212, 130, 44, lab, "green" if i == 2 else "white", size=12)
    for i, lab in enumerate(["Network 10.0.32.0\n4th octet → 0", "Hosts 10.0.32.1 – 10.0.47.254\n2¹² − 2 = 4,094 usable",
                             "Broadcast 10.0.47.255\nnext 10.0.48.0 − 1, right → 255"]):
        d.box(f"br{i}", 15 + i * 280, 266, 270, 42, lab, ["blue", "green", "orange"][i], size=11)
    d.box("note", 15, 324, 830, 44,
          "Quick division: 37 ÷ 16 = 2 remainder 5 → 2 × 16 = 32.\n"
          "A network must start on a block boundary: 10.0.5.0/22 is invalid, 10.0.4.0/22 is right.",
          "yellow", size=11, bold_first=False)
    return d


def aws_reserved():
    d = Diagram("2.3-aws-reserved", 860, 270, "AWS reserves 5 addresses in every subnet: a /24 gives 251, not 254")
    cells = [(".0\nnetwork", 110, "gray"), (".1\nVPC router", 110, "green"), (".2\nDNS resolver", 110, "purple"),
             (".3\nfuture use", 110, "gray"), (".4 – .254\nyours: 251 usable", 250, "blue"), (".255\nbroadcast", 110, "gray")]
    x = 15
    for i, (lab, w, c) in enumerate(cells):
        d.box(f"c{i}", x, 50, w, 50, lab, c)
        x += w + 6
    d.text("cap", 15, 104, 830, 22,
           "10.0.1.0/24 in a VPC · .2 is strictly the VPC base + 2 · .255 is reserved although the VPC has no broadcast",
           size=11, italic=True)
    for i, lab in enumerate(["/28 · 16 → 11 usable\nthe smallest AWS subnet", "/24 · 256 → 251 usable\na typical subnet",
                             "/20 · 4,096 → 4,091 usable\ndefault VPC's subnets", "/16 · 65,536 addresses\nthe largest VPC CIDR block"]):
        d.box(f"s{i}", 15 + i * 210, 140, 200, 46, lab, "white", size=11)
    d.box("note", 15, 204, 830, 50,
          "Usable = 2^(32 − N) − 2 in a normal subnet, − 5 on AWS. Azure also reserves 5, GCP 4 (from each provider's docs).\n"
          "/31 = 2 usable (point-to-point, RFC 3021) · /32 = one host · /0 = every address (the default route).",
          "yellow", size=11, bold_first=False)
    return d


# ---- 2.4 Subnetting step by step -------------------------------------------------------------

def borrow_bits():
    d = Diagram("2.4-borrow-bits", 860, 350, "Subnetting = borrowing host bits: each bit doubles the subnets, halves their size")
    rows = [("/24 · nothing borrowed\n1 × 256 addresses", 1, "192.168.10.0/24 · 256 addresses"),
            ("/25 · borrow 1 bit\n2 × 128 (126 usable)", 2, None),
            ("/26 · borrow 2 bits\n4 × 64 (62 usable)", 4, None),
            ("/27 · borrow 3 bits\n8 × 32 (30 usable)", 8, None)]
    X, W = 205, 640
    for r, (lab, n, only) in enumerate(rows):
        y = 50 + r * 62
        d.box(f"l{r}", 15, y, 180, 50, lab, "gray", size=11)
        step = 256 // n
        bw = W / n
        for i in range(n):
            start = i * step
            text = only or (f".{start}/{24 + r}\n{step}" if n == 8 else f".{start}/{24 + r} · {step}")
            d.box(f"b{r}_{i}", round(X + i * bw), y, round(bw) - 6, 50, text,
                  "blue" if i % 2 == 0 else "white", size=12 if n < 8 else 11, bold_first=False)
    d.box("note", 15, 302, 830, 36,
          "Block size = the step between subnet starts: /25 → 128, /26 → 64, /27 → 32. Subnets start at 0, block, 2 × block …",
          "yellow", size=11)
    return d


def six_questions():
    d = Diagram("2.4-six-questions", 860, 440, "Six questions, one tool: block size = 256 − mask octet")
    for i, (x, w, t) in enumerate([(15, 230, "Question"), (255, 300, "Method"), (565, 280, "Example")]):
        d.text(f"h{i}", x, 42, w, 22, t, bold=True)
    rows = [("1 · Which subnet is it in?", "largest multiple of the block\n≤ the value in that octet",
             "10.0.37.5/20: block 16, 37 → 32\n→ 10.0.32.0/20"),
            ("2 · Split into N equal subnets", "borrow b bits where 2^b ≥ N\nnew prefix = old prefix + b",
             "/24 into 6: b = 3 → /27\n8 subnets of 32 (2 spare)"),
            ("3 · Size a subnet for H hosts", "smallest h with 2^h − 2 ≥ H\n(AWS: 2^h − 5) · prefix = 32 − h",
             "50 hosts: h = 6 → /26 (62)\n500 pods on AWS: /23 min, /22 better"),
            ("4 · What's the next subnet?", "add the block size\nin the interesting octet",
             "10.0.16.0/20 → 10.0.32.0/20\n10.0.252.0/22 → 10.1.0.0/22"),
            ("5 · Do two ranges overlap?", "only if one contains the other:\nis the small one's start inside?",
             "10.0.16.0/20 vs 10.0.20.0/24: yes\n10.0.16.0/20 vs 10.0.32.0/24: no"),
            ("6 · Plan a VPC", "size with growth, biggest first,\non block boundaries, leave spare",
             "10.0.0.0/16: /20 app tiers,\n/24 public and data, per AZ")]
    for i, (q, m, e) in enumerate(rows):
        y = 70 + i * 58
        d.box(f"q{i}", 15, y, 230, 50, q, "gray", size=12)
        d.box(f"m{i}", 255, y, 300, 50, m, "white", size=11, bold_first=False)
        d.box(f"e{i}", 565, y, 280, 50, e, "green", size=11, bold_first=False)
    d.text("foot", 15, 414, 830, 20, "Subnets → borrowed bits (2^b ≥ N). Hosts → remaining bits (2^h − 2 ≥ H). Never mix them up.",
           size=11, italic=True)
    return d


def vpc_plan():
    d = Diagram("2.4-vpc-plan", 860, 460, "Question 6: 10.0.0.0/16 across 3 AZs, laid out in /20 slots, biggest first")
    slots = ["10.0.0.0/20\n10.0.0.0 – 10.0.15.255", "10.0.16.0/20\n10.0.16.0 – 10.0.31.255",
             "10.0.32.0/20\n10.0.32.0 – 10.0.47.255", "10.0.48.0/20\n10.0.48.0 – 10.0.63.255",
             "10.0.64.0/20\n10.0.64.0 – 10.0.79.255", "10.0.80.0 – 10.0.255.255\n11 more /20 slots"]
    for i, lab in enumerate(slots):
        d.box(f"s{i}", 15, 48 + i * 58, 190, 50, lab, "gray", size=11)
    X = 215

    def three(prefix, y, base, color, tier):
        for j, az in enumerate("abc"):
            d.box(f"{prefix}{j}", X + j * 152, y, 146, 50, f"{tier} · AZ {az}\n10.0.{base + j}.0/24 · 251", color, size=11)
        d.box(f"{prefix}f", X + 456, y, 174, 50, f"free\n10.0.{base + 3}.0 – 10.0.{base + 15}.255",
              "white", size=11, dashed=True)

    three("pub", 48, 0, "orange", "public")
    for j, az in enumerate("abc"):
        d.box(f"app{j}", X, 106 + j * 58, 630, 50,
              f"private app · AZ {az} · 10.0.{16 * (j + 1)}.0/20\n4,091 usable on AWS: EKS nodes and pods (each pod takes a VPC IP)",
              "blue", size=11)
    three("dat", 280, 64, "purple", "data")
    d.box("spare", X, 338, 630, 50, "spare: room for new tiers or more AZs", "white", dashed=True)
    d.box("note", 15, 400, 830, 46,
          "Used 13,824 of 65,536 (about 21%). Public: load balancers, NAT gateways · data: databases.\n"
          "The next environment gets 10.1.0.0/16: never overlap other VPCs, offices or VPNs.",
          "yellow", size=11, bold_first=False)
    return d


# ---- 2.5 VLSM and route summarisation --------------------------------------------------------

def vlsm_vs_summary():
    d = Diagram("2.5-vlsm-and-summary", 860, 446, "VLSM cuts one block unevenly · summarisation announces many blocks as one")
    d.group("gv", 15, 44, 440, 388, "VLSM: 192.168.1.0/24, largest first", "gray", size=12)
    parts = [("Head office · 100 hosts → /25\n192.168.1.0/25 · .0 – .127 · usable .1 – .126", 62, "blue"),
             ("Branch A · 50 hosts → /26\n192.168.1.128/26 · .128 – .191 · usable .129 – .190", 48, "blue"),
             ("Branch B · 20 hosts → /27\n192.168.1.192/27 · .192 – .223 · usable .193 – .222", 40, "blue"),
             ("WAN link 1 → /30 · 192.168.1.224/30 · .225 – .226", 26, "green"),
             ("WAN link 2 → /30 · 192.168.1.228/30 · .229 – .230", 26, "green"),
             ("WAN link 3 → /30 · 192.168.1.232/30 · .233 – .234", 26, "green"),
             ("Spare: 192.168.1.236/30 + 192.168.1.240/28\n.236 – .255 · 20 addresses, all in one place", 42, "white")]
    y = 76
    for i, (lab, h, c) in enumerate(parts):
        d.box(f"v{i}", 25, y, 420, h, lab, c, size=11, dashed=(i == 6))
        y += h + 6
    d.text("vn", 25, y + 2, 420, 34, "Each start is where the previous one ended, and always\na valid boundary for the smaller size.",
           size=11, italic=True)
    d.group("gs", 470, 44, 375, 388, "Summarisation: 4 routes → 1", "gray", size=12)
    for i in range(4):
        d.box(f"r{i}", 480, 80 + i * 50, 205, 42, f"10.1.{i}.0/24\n3rd octet 000000|{i:02b}", "blue", size=11)
    d.box("sum", 715, 132, 120, 84, "10.1.0.0/22\n16 + 6 common\nbits = /22", "green", size=12)
    for i in range(4):
        d.edge(f"r{i}", "sum")
    d.box("why", 480, 286, 355, 42, "A router in London carries 1 route\ninstead of 4 for the subnets in Pune", "yellow", size=11,
          bold_first=False)
    d.box("rule", 480, 336, 355, 56, "Shortcut: 2^k consecutive /24s = one /(24 − k)\nonly if the first starts on a multiple of 2^k\n4 from 0 → /22 · 8 from 8 → 172.16.8.0/21",
          "white", size=11, bold_first=False)
    return d


def over_summarising():
    d = Diagram("2.5-over-summarising", 860, 318, "Summarise only what you own: a lazy /22 black-holes 10.1.3.0/24")
    X, W = 175, 163
    d.text("l0", 15, 50, 150, 44, "Your subnets", bold=True, align="left")
    for i in range(4):
        own = i < 3
        d.box(f"s{i}", X + i * (W + 5), 50, W, 44, f"10.1.{i}.0/24\n{'yours' if own else 'someone else’s'}",
              "blue" if own else "red", dashed=not own, size=12)
    d.text("l1", 15, 104, 150, 44, "Lazy summary ✗", bold=True, align="left")
    d.box("lazy", X, 104, 4 * W + 15, 44, "10.1.0.0/22 also claims 10.1.3.0/24\n→ its traffic is pulled to you and lost (a black hole)", "red", size=12)
    d.text("l2", 15, 158, 150, 44, "Exact summary ✓\n(collapse_addresses)", size=11, align="left")
    d.box("x23", X, 158, 2 * W + 5, 44, "10.1.0.0/23", "green", bold=True)
    d.box("x24", X + 2 * (W + 5), 158, W, 44, "10.1.2.0/24", "green", bold=True)
    d.box("xno", X + 3 * (W + 5), 158, W, 44, "not announced", "white", dashed=True, size=11)
    d.text("lp", 15, 222, 830, 22, "Summaries and exceptions live side by side: the longest prefix still wins (2.7)",
           bold=True, align="left")
    d.box("pkt", 15, 254, 170, 48, "Packet for\n10.1.2.7", "white")
    d.box("mum", 255, 254, 280, 48, "10.1.2.0/24 → Mumbai ✓\n/24 is the longer match", "green", size=11)
    d.box("lon", 595, 254, 250, 48, "10.1.0.0/22 → London\nalso matches, but shorter", "gray", size=11)
    d.edge("pkt", "mum")
    return d


def hierarchical_plan():
    d = Diagram("2.5-hierarchical-plan", 860, 366, "A hierarchical plan summarises itself: company → region → VPC → tier")
    d.box("org", 230, 46, 220, 44, "Company\n10.0.0.0/8", "gray")
    d.box("in", 90, 130, 220, 44, "Region India\n10.0.0.0/12", "blue")
    d.box("eu", 380, 130, 220, 44, "Region EU\n10.16.0.0/12", "blue")
    d.box("prod", 15, 218, 180, 44, "prod VPC\n10.0.0.0/16", "white")
    d.box("stg", 210, 218, 180, 44, "staging VPC\n10.1.0.0/16", "white")
    d.box("dev", 405, 218, 180, 44, "dev VPC\n10.2.0.0/16", "white")
    d.box("app", 15, 306, 180, 44, "app subnets\n/20", "white", size=11)
    d.box("pd", 210, 306, 180, 44, "public and data\nsubnets /24", "white", size=11)
    for a, b in [("org", "in"), ("org", "eu"), ("in", "prod"), ("in", "stg"), ("in", "dev"), ("prod", "app"), ("prod", "pd")]:
        d.edge(a, b)
    notes = ["An EU router needs ONE route\nfor all of India: 10.0.0.0/12",
             "A new VPC takes the next /16\nin its region: no overlap,\nno renumbering",
             "Firewall rule \"allow from India\"\n= one CIDR",
             "Avoids two VPCs with the\nsame CIDR (scenario A2)"]
    y = 46
    for i, t in enumerate(notes):
        h = 58 if t.count("\n") == 2 else 46
        d.box(f"n{i}", 625, y, 220, h, t, "yellow", size=11, bold_first=False)
        y += h + 22
    return d


# ---- 2.6 IPv6 fundamentals -------------------------------------------------------------------

def ipv6_anatomy():
    d = Diagram("2.6-address-anatomy", 860, 520, "IPv6: 128 bits = 8 groups of 4 hex digits (16 bits each)")
    groups = ["2405", "0201", "1006", "e906", "0000", "0000", "c0a8", "1d01"]
    for i, g in enumerate(groups):
        d.box(f"g{i}", 15 + i * 104, 48, 98, 38, g, "white", bold=True, size=14)
    d.box("pre", 15, 94, 306, 56, "Global routing prefix · 48 bits\ngiven to your site by the ISP\n(homes often get a /56 or /64)", "blue", size=11)
    d.box("sub", 327, 94, 98, 56, "Subnet ID\n16 bits\nyour subnets", "green", size=11)
    d.box("iid", 431, 94, 410, 56, "Interface ID · 64 bits\nthe device (built by SLAAC)\nhere c0a8:1d01 = 192.168.29.1, the router's IPv4", "purple", size=11)
    d.box("p64", 15, 158, 410, 30, "network prefix /64: every LAN is a /64", "gray", size=12, bold=True)
    d.box("sz", 431, 158, 410, 30, "/48 = 65,536 /64s · /56 = 256 · AWS: VPC /56, subnet /64", "gray", size=11)
    d.text("sh", 15, 202, 830, 22, "Shortening (your router's DNS address, tested on the Mac, Oct 2026)", bold=True, align="left")
    steps = [("Full: 8 × 4 hex digits", "2405:0201:1006:e906:0000:0000:c0a8:1d01"),
             ("Rule 1: drop leading zeros", "2405:201:1006:e906:0:0:c0a8:1d01"),
             ("Rule 2: one run of 0 groups → ::\n(only once per address)", "2405:201:1006:e906::c0a8:1d01")]
    for i, (rule, addr) in enumerate(steps):
        y = 230 + i * 58
        d.box(f"r{i}", 15, y, 260, 40, rule, "gray", size=11, bold_first=False)
        d.box(f"a{i}", 300, y, 545, 40, addr, "green" if i == 2 else "white", size=14, bold=(i == 2))
        if i:
            d.edge(f"a{i - 1}", f"a{i}")
    d.box("rfc", 15, 400, 830, 40,
          "RFC 5952: lowercase · shorten the LONGEST zero run (first on a tie) · no :: for a single 0 group · with a port: [2001:db8::1]:443",
          "yellow", size=11)
    types = [("2… or 3…\nglobal unicast\n2000::/3 · public", "blue"), ("fd…\nunique local (ULA)\nfd00::/8 ≈ RFC 1918", "blue"),
             ("fe80…\nlink-local\nalways there · %eth0", "green"), ("ff…\nmulticast\nff02::1 all nodes", "orange"),
             ("::1\nloopback\n= 127.0.0.1", "gray")]
    for i, (t, c) in enumerate(types):
        d.box(f"t{i}", 15 + i * 167, 452, 161, 56, t, c, size=11)
    return d


def slaac_ndp():
    d = Diagram("2.6-slaac-ndp", 860, 590, "On the LAN: NDP (ICMPv6, multicast) replaces ARP; SLAAC builds the address")
    _lifeline(d, "rtr", 140, 46, 486, "Router\nsends Router Advertisements", "green")
    _lifeline(d, "host", 430, 46, 486, "Host (new on the link)\nhas only its fe80:: address", "blue")
    _lifeline(d, "nb", 720, 46, 486, "Neighbour\n2001:db8:abcd:1::20", "blue")
    d.box("m1", 155, 106, 260, 40, "1 · RS (type 133) to all routers\n\"any routers here?\"", "white", size=11)
    _arrow(d, "a1", 424, 156, 146, 156)
    d.box("m2", 155, 170, 260, 54, "2 · RA (type 134) to all nodes\nprefix 2001:db8:abcd:1::/64\n\"use me as your gateway\"", "white", size=11)
    _arrow(d, "a2", 146, 234, 424, 234)
    d.box("m3", 290, 250, 280, 72, "3 · SLAAC: the host builds its address\n/64 prefix + its own 64-bit interface ID\n(random, or EUI-64 from the MAC)\nDAD: is anyone already using it?",
          "blue", size=11)
    d.box("m4", 445, 338, 260, 40, "4 · NS (type 135): who has ::20?\ntell me your MAC (= ARP request)", "white", size=11)
    _arrow(d, "a4", 436, 388, 714, 388)
    d.box("m5", 445, 404, 260, 40, "5 · NA (type 136): that's me,\nhere is my MAC (= ARP reply)", "white", size=11)
    _arrow(d, "a5", 714, 454, 436, 454)
    d.box("eui", 15, 500, 410, 76,
          "EUI-64 (older): MAC 00:1a:2b:3c:4d:5e → flip the 7th bit,\ninsert ff:fe → fe80::21a:2bff:fe3c:4d5e\nThe MAC shows in every address, so the device can be\ntracked. Modern OSes use random interface IDs.",
          "white", size=11, bold_first=False)
    d.box("icmp", 435, 500, 410, 76,
          "Don't block all ICMPv6\nNDP, router discovery, duplicate address detection\nand path MTU discovery (\"packet too big\", type 2)\nall run on it. RFC 4890 lists what to allow.",
          "red", size=11)
    return d


# ---- 2.8 DHCP --------------------------------------------------------------------------------

def dora():
    d = Diagram("2.8-dora", 860, 448, "DHCP DORA: how a client with no address gets one (tested in the lab container)")
    _lifeline(d, "cl", 120, 44, 378, "Client · no IP yet\nMAC fe:25:0f:37:82:a2", "blue")
    _lifeline(d, "sv", 500, 44, 378, "DHCP server (dnsmasq)\n192.168.50.1", "purple")
    msgs = [("1 · DISCOVER · broadcast\n0.0.0.0:68 → 255.255.255.255:67", 40, True),
            ("2 · OFFER\n192.168.50.108, mask /24, gateway .1, DNS .1, lease 1 h", 40, False),
            ("3 · REQUEST · still broadcast\n\"I accept .108 from server 192.168.50.1\"\nso every other server withdraws its offer", 54, True),
            ("4 · ACK\n\"Confirmed: it's yours for 3600 s\" (NAK = start again)", 40, False)]
    y = 104
    for i, (lab, h, up) in enumerate(msgs):
        d.box(f"m{i}", 132, y, 356, h, lab, "white", size=11)
        ay = y + h + 10
        if up:
            _arrow(d, f"a{i}", 126, ay, 494, ay)
        else:
            _arrow(d, f"a{i}", 494, ay, 126, ay)
        y = ay + 16
    d.box("cfg", 15, y + 8, 330, 44, "Client sets IP 192.168.50.108/24, default route\nvia .1 and DNS .1, then ARP-checks the address",
          "green", size=11, bold_first=False)
    notes = [("UDP · RFC 2131\nserver port 67, client port 68\nBOOTP packet format", 58, "gray"),
             ("xid links the 4 messages.\nOffer and Ack: unicast or\nbroadcast (the client's flag)", 58, "white"),
             ("Options the client asks for\n1 mask · 3 router · 6 DNS\n15 domain · 51 lease time\n53 message type · 54 server ID", 72, "yellow"),
             ("No Offer at all?\nDiscovers repeat, gaps grow\nmacOS/Windows: 169.254.x.x\nLinux dhclient: no IPv4 address", 72, "red")]
    y = 44
    for i, (lab, h, c) in enumerate(notes):
        d.box(f"n{i}", 630, y, 215, h, lab, c, size=11)
        y += h + 12
    return d


def lease_timeline():
    d = Diagram("2.8-lease-timeline", 860, 330, "A lease is borrowed time: renew at T1, rebind at T2, stop at expiry")
    d.box("b0", 15, 50, 415, 40, "bound: use the address", "green")
    d.box("b1", 430, 50, 311, 40, "renewing", "orange")
    d.box("b2", 741, 50, 104, 40, "rebinding", "red", size=11)
    for i, (x, t) in enumerate([(40, "start"), (430, "T1 = 50%"), (741, "T2 = 87.5%"), (812, "expiry")]):
        d.text(f"t{i}", x - 50, 94, 100, 20, t, bold=True, size=11)
    d.box("d1", 15, 130, 270, 64, "At T1 (50%): renew\nunicast Request to the server\nthat gave the lease", "orange", size=11)
    d.box("d2", 295, 130, 270, 64, "At T2 (87.5%): rebind\nno answer, so broadcast a\nRequest to ANY server", "orange", size=11)
    d.box("d3", 575, 130, 270, 64, "Lease expires\nstop using the address,\nstart again from Discover", "red", size=11)
    d.box("ex1", 15, 210, 410, 64, "Lab capture: lease 3600 s\nRN (T1) 1800 s · RB (T2) 3150 s\ndhclient: \"renewal in 1503 seconds\" (randomised)", "white", size=11)
    d.box("ex2", 435, 210, 410, 64, "An 8-hour lease\nT1 = 4 hours (renew, unicast)\nT2 = 7 hours (rebind, broadcast)", "white", size=11)
    d.box("res", 15, 286, 830, 34,
          "Reservation (static lease): a fixed IP for one MAC, still managed centrally · dhclient -r sends a unicast Release",
          "yellow", size=11)
    return d


def dhcp_relay():
    d = Diagram("2.8-dhcp-relay", 860, 350, "A DHCP relay: one central server for many subnets")
    d.box("cl", 15, 110, 180, 80, "Client\non 10.1.20.0/24\nno address yet", "blue")
    d.box("rt", 340, 110, 180, 80, "Router / L3 switch\nrelay agent\non 10.1.20.1", "green")
    d.box("sv", 665, 110, 180, 80, "Central DHCP server\n10.9.0.5\none pool per subnet", "purple")
    _arrow(d, "f1", 195, 132, 340, 132)
    _arrow(d, "f2", 520, 132, 665, 132)
    _arrow(d, "r1", 665, 168, 520, 168)
    _arrow(d, "r2", 340, 168, 195, 168)
    d.text("t1", 197, 66, 141, 40, "1 · Discover\n(broadcast)", size=11)
    d.text("t2", 522, 66, 141, 40, "2 · unicast, 10.9.0.5\ngiaddr = 10.1.20.1", size=11)
    d.text("t3", 522, 194, 141, 40, "3 · Offer from the\n10.1.20.0/24 pool", size=11)
    d.text("t4", 197, 194, 141, 40, "4 · Offer passed\nback to the client", size=11)
    d.box("gi", 15, 250, 270, 82, "giaddr = the relay's own\ninterface address: the server\nuses it to pick the right pool", "yellow", size=11,
          bold_first=False)
    d.box("cisco", 295, 250, 270, 82, "Cisco: ip helper-address 10.9.0.5\non the client-facing interface\n(vendor-specific) · Option 82 adds\nthe client's switch port",
          "white", size=11, bold_first=False)
    d.box("none", 575, 250, 270, 82, "No relay on a new subnet?\nIts broadcasts stop at the\nrouter: its clients get no\naddress, other subnets are fine",
          "red", size=11)
    return d


ALL = [routing_decision, longest_prefix_match, hop_by_hop,
       level_2_map, octet_place_values, mask_octets, hex_bytes,
       address_map, real_addresses, cast_types,
       mask_and, block_size_lines, aws_reserved,
       borrow_bits, six_questions, vpc_plan,
       vlsm_vs_summary, over_summarising, hierarchical_plan,
       ipv6_anatomy, slaac_ndp, dora, lease_timeline, dhcp_relay]
