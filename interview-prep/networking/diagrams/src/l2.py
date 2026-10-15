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


ALL = [routing_decision, longest_prefix_match, hop_by_hop]
