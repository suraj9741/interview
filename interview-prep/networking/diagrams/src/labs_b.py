"""Lab diagrams, part B: the lab index, Labs 3.1 to 3.5, and the Level 1 solutions."""
from drawio_svg import Diagram


# ---- Lab index -------------------------------------------------------------------------------

def labs_map():
    d = Diagram("labs-map", 860, 610, "The labs in order: do each one right after its lesson")
    col = [20, 300, 580]
    bw, bh = 260, 58

    def row(group_y, items, y_off=30):
        ids = []
        for (bid, label, color), x in zip(items, col):
            d.box(bid, x, group_y + y_off, bw, bh, label, color, size=11)
            ids.append(bid)
        for a, b in zip(ids, ids[1:]):
            d.edge(a, b)
        return ids

    d.group("g1", 10, 46, 840, 98, "Start here · Level 1 · Fundamentals")
    row(46, [("s00", "00 · Environment setup\nbuild and start the lab container\nMac + Docker · 20 min", "yellow"),
             ("l11", "1.1 · Inspect your own network\nyour IP, MAC, gateway, DNS and ports\nMac · 20 min", "blue"),
             ("l12", "1.2 · Build a tiny network\nnamespaces, a cable, a switch, ARP\nlab container · 45 min", "blue")])

    d.group("g2", 10, 168, 840, 98, "Level 2 · IP addressing and subnetting")
    row(168, [("l21", "2.1 · Subnetting by hand\n10 subnets on paper, VLSM, summaries\npaper + Python · 60 min", "blue"),
              ("l22", "2.2 · Routing between two subnets\nfix routing step by step; TTL, MTU\nlab container · 65 min", "blue"),
              ("l23", "2.3 · DHCP: capture DORA\nDiscover, Offer, Request, Ack, release\nlab container · 30 min", "blue")])

    d.group("g3", 10, 290, 840, 176, "Level 3 · Core protocols")
    row(290, [("l31", "3.1 · Capture a TCP handshake\nclose, TIME_WAIT, DROP vs REJECT, UDP\nlab container · 60 min", "blue"),
              ("l32", "3.2 · Trace DNS resolution\nyour own root, TLD and auth servers\nlab container · 60 min", "blue"),
              ("l33", "3.3 · TLS certificates, handshake\nbe a CA; untrusted, mismatch, expired\nlab container · 60 min", "blue")])
    row(290, [("l34", "3.4 · NAT and port forwarding\nMASQUERADE, conntrack, DNAT\nlab container · 45 min", "blue"),
              ("l35", "3.5 · Troubleshooting challenge\nfind and fix eight hidden faults\nlab container · 2 h · the capstone", "orange")],
        y_off=108)
    d.box("hrs", 580, 398, 260, 58, "Levels 1–3: about 9 hours\nof lab time (an estimate)", "yellow", size=11,
          bold_first=False)
    d.edge("l33", "l34", points=[(710, 388), (150, 388)])

    d.group("g4", 10, 490, 280, 98, "Level 10 · Containers")
    d.box("l101", 20, 520, 260, 58, "10.1 · Docker bridge, NAT and DNS\ninside Docker Desktop's VM\nMac + Docker · 20 min", "blue",
          size=11)
    d.group("g5", 300, 490, 550, 98, "Planned (not written yet)", dashed=True)
    d.text("plan", 310, 520, 530, 58,
           "VLANs and 802.1Q · OSPF and BGP with FRR · a load balancer · nftables\n"
           "WireGuard · an AWS VPC with a NAT gateway (may cost money)\nkind · Prometheus", size=11)

    d.edge("g1", "g2")
    d.edge("g2", "g3")
    d.edge("g3", "g4", points=[(150, 466)])
    return d


# ---- Lab 3.1 ---------------------------------------------------------------------------------

def lab31_topology():
    d = Diagram("lab-3.1-topology", 860, 400, "Lab 3.1: a client and a server joined by one veth pair")
    d.group("cg", 20, 50, 300, 210, "client namespace")
    d.box("ce", 40, 84, 260, 46, "eth0\n10.10.0.1/24", "blue")
    d.box("ct", 40, 146, 260, 96, "Runs the tests\ncurl · nc · tcpdump · tshark\nss -tan: who is in TIME-WAIT?\ncaptures in /tmp/lab31/", "white",
          size=11)
    d.box("parts", 20, 280, 300, 104,
          "Parts\nA build it · B a complete connection\nC a closed TCP port · D DROP vs REJECT\n"
          "E UDP: closed vs open · F HTTP by hand\nG decode a packet, read ss -ti", "yellow", size=11)

    d.group("sg", 470, 50, 370, 334, "server namespace")
    d.box("se", 490, 84, 330, 46, "eth0\n10.10.0.2/24", "blue")
    d.box("p8080", 490, 146, 330, 44, ":8080/tcp · python3 -m http.server (HTTP/1.0)\nserves /tmp/lab31/www (Parts B, D, F, G)",
          "purple", size=11)
    d.box("p8081", 490, 198, 330, 34, ":8081/tcp · an HTTP/1.1 server (Part F)", "purple", size=11)
    d.box("p5000", 490, 240, 330, 34, ":5000/udp · nc -u -l (Part E)", "purple", size=11)
    d.box("closed", 490, 282, 330, 34, ":9999/tcp and :5353/udp · closed (Parts C, E)", "red", size=11)
    d.box("fw", 490, 324, 330, 44, "iptables INPUT, tcp 8080: DROP, then REJECT (D)\ntc tbf rate 20mbit on eth0 (Part G)",
          "orange", size=11)
    d.edge("ce", "se", "veth pair", both=True, size=11)
    return d


def lab31_what_comes_back():
    d = Diagram("lab-3.1-what-comes-back", 860, 530, "What comes back: the six cases in this lab")
    d.text("hc", 20, 44, 190, 22, "Case", bold=True)
    d.text("hr", 615, 44, 225, 22, "What the client sees", bold=True)
    d.box("cl", 220, 44, 80, 420, "client\n10.10.0.1", "blue", size=11, valign="top")
    d.box("sv", 530, 44, 70, 420, "server\n10.10.0.2", "purple", size=11, valign="top")
    rows = [
        ("Open TCP port\n:8080, web server", "SYN · ACK · request · FIN", "SYN-ACK · response · FIN",
         "Data\nhello from the server", "green"),
        ("Closed TCP port\n:9999, nothing listens", "SYN", "RST  (Flags [R.])",
         "Refused, instantly\ncurl: (7) · nc: Connection refused", "red"),
        ("DROP rule\niptables -j DROP on :8080", "SYN ×4, same seq, about 1 s apart", None,
         "Timeout\ncurl: (28) after 4002 ms", "red"),
        ("REJECT rule\niptables -j REJECT on :8080", "SYN", "ICMP port unreachable",
         "Fails instantly\ncurl: (7) after 0 ms", "red"),
        ("Closed UDP port\n:5353", "datagram  (hi)", "ICMP port unreachable",
         "Nothing: nc exit=0\nit never noticed the ICMP", "red"),
        ("Open UDP port\n:5000, nc -u -l", "one datagram  (hello over udp)", None,
         "Nothing (no reply needed)\nthe server got the data", "green"),
    ]
    for i, (case, out, back, sees, color) in enumerate(rows):
        y = 80 + i * 64
        c = y + 26
        d.box(f"case{i}", 20, y, 190, 52, case, "gray", size=11)
        d.box(f"see{i}", 615, y, 225, 52, sees, color, size=11)
        oy = c - 11 if back else c
        d.edge("cl", "sv", out, points=[(300, oy), (530, oy)], size=11)
        if back:
            d.edge("sv", "cl", back, points=[(530, c + 11), (300, c + 11)], size=11)
    d.box("note", 20, 478, 820, 40,
          "Refused = something answered, so the network works.   Timed out = something dropped the packet.",
          "yellow", size=12)
    return d


# ---- Lab 3.2 ---------------------------------------------------------------------------------

def lab32_topology():
    d = Diagram("lab-3.2-topology", 860, 370, "Lab 3.2: five namespaces on one bridge, fully offline")
    nodes = [("client", "client\neth0 10.53.0.100/24\nruns dig, getent, curl", "blue"),
             ("resolver", "resolver\neth0 10.53.0.53/24\nrecursive, caching", "purple"),
             ("root", "root\neth0 10.53.0.10/24\nzone '.'", "purple"),
             ("tld", "tld\neth0 10.53.0.20/24\nzone 'lab.'", "purple"),
             ("auth", "auth\neth0 10.53.0.30/24\nzone 'example.lab.'", "purple")]
    d.box("br", 20, 196, 820, 44, "sw namespace · Linux bridge br0 · one subnet: 10.53.0.0/24", "green", bold=True)
    for i, (nid, label, color) in enumerate(nodes):
        x = 20 + i * 166
        d.box(nid, x, 50, 156, 72, label, color, size=11)
        d.edge(nid, "br", f"eth0 ↔ p-{nid}", both=True, points=[(x + 78, 196)], size=11)
    d.box("rc", 20, 262, 400, 92,
          "The client's resolver\n/etc/netns/client/resolv.conf (ip netns exec\nmounts it over /etc/resolv.conf):\n"
          "nameserver 10.53.0.53 · search example.lab", "yellow", size=11)
    d.box("bind", 440, 262, 400, 92,
          "BIND 9 (named) runs in root, tld, auth, resolver\nconfig, zones, pid and log: /tmp/dnslab/<node>/\n"
          "./dns-lab.sh up · flush · down\nstop-auth · start-auth · stop-resolver · start-resolver", "yellow", size=11)
    return d


def lab32_referral_chain():
    d = Diagram("lab-3.2-referral-chain", 860, 460, "One question, four servers: the resolver follows the referrals")
    d.box("client", 20, 56, 280, 56, "client · 10.53.0.100\ndig www.example.lab", "blue")
    d.box("res", 20, 196, 280, 84,
          "resolver · 10.53.0.53\nrecursive and caching; at start it knows\nonly the root hints:\na.root-servers.net = 10.53.0.10",
          "purple", size=11)
    d.edge("client", "res", "1 · A? www.example.lab (recursive query)\n5 · CNAME example.lab., A 10.53.0.80",
           both=True, size=11)
    d.box("root", 540, 46, 300, 86,
          "root '.' · 10.53.0.10 · a.root-servers.net\nreferral: lab. NS ns1.nic.lab.\n+ glue A 10.53.0.20\n"
          "(and 0.53.10.in-addr.arpa. → ns1.example.lab)", "purple", size=11)
    d.box("tld", 540, 150, 300, 72,
          "TLD 'lab.' · 10.53.0.20 · ns1.nic.lab\nreferral: example.lab. NS ns1.example.lab.\n+ glue A 10.53.0.30",
          "purple", size=11)
    d.box("auth", 540, 240, 300, 146,
          "auth 'example.lab.' · 10.53.0.30\nns1.example.lab · answers with aa\nTTL 300 · negative TTL 60\n"
          "@ A 10.53.0.80 · AAAA fd00:53::80\nwww CNAME example.lab.\napi A 10.53.0.81 and 10.53.0.82\n"
          "MX 10 mail · mail A 10.53.0.25\nTXT \"v=spf1 mx -all\"\nPTR .80 and .81 (zone 0.53.10.in-addr.arpa.)",
          "purple", size=11, align="left")
    d.edge("res", "root", "2 · NS? lab.", both=True, size=11)
    d.edge("res", "tld", "3 · NS? example.lab.", both=True, size=11)
    d.edge("res", "auth", "4 · A? www.example.lab.", both=True, size=11)
    d.box("note", 20, 404, 820, 44,
          "Ask again within 300 s: the answer comes from the resolver's cache (TTL counting down), and 2–4 don't happen.\n"
          "A name that doesn't exist (NXDOMAIN) is cached too, for the SOA's 60 s.", "yellow", size=11, bold_first=False)
    return d


# ---- Lab 3.3 ---------------------------------------------------------------------------------

def lab33_topology():
    d = Diagram("lab-3.3-topology", 860, 396, "Lab 3.3: a TLS client and server, with a hosts file instead of DNS")
    d.group("cg", 20, 50, 330, 262, "tls-client namespace")
    d.box("ce", 40, 84, 290, 44, "eth0\n10.20.0.1/24", "blue")
    d.box("hosts", 40, 144, 290, 64,
          "/etc/netns/tls-client/hosts\n10.20.0.2 web.example.lab\n(ip netns exec uses it as /etc/hosts)", "yellow", size=11)
    d.box("trust", 40, 224, 290, 64,
          "Trusts Lab Root CA only when told\ncurl --cacert ca.crt\nopenssl s_client -CAfile ca.crt", "white", size=11)
    d.group("sg", 510, 50, 330, 262, "tls-server namespace")
    d.box("se", 530, 84, 290, 44, "eth0\n10.20.0.2/24", "blue")
    d.box("p8443", 530, 144, 290, 44, ":8443 · s_server, server.crt (valid)\nsteps 4 to 8", "purple", size=11)
    d.box("p9443", 530, 194, 290, 44, ":9443 · s_server, old.crt (expired)\nstep 9", "red", size=11)
    d.box("p10443", 530, 244, 290, 44, ":10443 · s_server -Verify 1 (mutual TLS)\nstep 10", "orange", size=11)
    d.edge("ce", "se", "veth pair", both=True, size=11)
    d.box("files", 20, 330, 820, 50,
          "Files in /tmp/lab33\nca.key, ca.crt (the CA) · server.key, server.csr, server.crt · old.crt · client.key, client.csr, client.crt",
          "white", size=11)
    return d


def lab33_certificates():
    d = Diagram("lab-3.3-certificates", 860, 410, "Be your own CA: who makes which key, and what the CA signs")
    d.box("scsr", 20, 56, 260, 86,
          "Server: openssl req -newkey\nserver.key never leaves the server\nserver.csr: CN=web.example.lab\nSAN DNS:web.example.lab",
          "blue", size=11)
    d.box("ca", 320, 56, 220, 86,
          "Lab Root CA\nca.crt: self-signed, CA:TRUE\nsubject = issuer · 30 days\nca.key signs: keep it offline",
          "orange", size=11)
    d.box("ccsr", 580, 56, 260, 86, "Client: openssl req -newkey\nclient.key stays with the client\nclient.csr: CN=lab-client",
          "blue", size=11)
    d.edge("scsr", "ca", "CSR", size=11)
    d.edge("ccsr", "ca", "CSR", size=11)
    d.box("scrt", 20, 222, 260, 86,
          "server.crt · 7 days\nissuer CN = Lab Root CA\nOct 14 → Oct 21 2026 in the tested run\nSAN copied by -copy_extensions copy",
          "green", size=11)
    d.box("old", 300, 222, 260, 86,
          "old.crt · the same server.csr\nsigned under faketime 2026-09-01\nvalid Sep 1 → Sep 8 2026\nalready expired", "red", size=11)
    d.box("ccrt", 580, 222, 260, 86, "client.crt · 7 days\nCN=lab-client\nfor mutual TLS on :10443", "green", size=11)
    d.edge("ca", "scrt", "signs", size=11)
    d.edge("ca", "old", "signs", size=11)
    d.edge("ca", "ccrt", "signs", size=11)
    d.box("note", 20, 330, 820, 64,
          "A client checks: who issued it (issuer) · when it's valid (notBefore / notAfter) · "
          "which names it covers (the SAN, not the CN).\nWithout -copy_extensions copy the certificate has no SAN, "
          "and every name check fails.", "yellow", size=11, bold_first=False)
    return d


def lab33_tls_errors():
    d = Diagram("lab-3.3-tls-errors", 860, 450, "Each TLS failure, as you reproduced it, and what the client prints")
    rows = [
        ("All checks pass\ntrusted CA, name in the SAN, valid dates", "gray",
         "HTTP 200\nVerify return code: 0 (ok)", "green"),
        ("CA not trusted\nno --cacert (step 5a)", "gray",
         "curl: (60) SSL certificate problem: unable to get local issuer certificate\n"
         "s_client: Verify return code: 21, and it still completes the handshake", "red"),
        ("Name not in the SAN\nby IP (step 5b) or by another name (step 8)", "gray",
         "curl: (60) SSL: no alternative certificate subject name matches\ntarget host name '10.20.0.2' (or 'other.example.lab')", "red"),
        ("Expired certificate\nold.crt on :9443 (step 9)", "gray",
         "curl: (60) SSL certificate problem: certificate has expired\nVerify return code: 10 (certificate has expired)",
         "red"),
        ("Plain HTTP to a TLS port\nhttp://web.example.lab:8443/ (step 8)", "gray",
         "curl: (52) Empty reply from server\nnot a ClientHello, so the server closes the connection", "red"),
        ("Mutual TLS, no client certificate\n:10443 with -Verify 1 (step 10)", "gray",
         "curl: (56) … tlsv13 alert certificate required\nserver log: peer did not return a certificate", "red"),
        ("-k (insecure)\nuntrusted CA and the wrong name", "gray",
         "HTTP 200, with no protection at all\nskips every check: diagnose with it, never use it in scripts", "orange"),
    ]
    for i, (cause, cc, seen, sc) in enumerate(rows):
        y = 50 + i * 56
        d.box(f"c{i}", 20, y, 290, 46, cause, cc, size=11)
        d.box(f"s{i}", 340, y, 500, 46, seen, sc, size=11, bold_first=False)
        d.edge(f"c{i}", f"s{i}")
    return d


# ---- Lab 3.4 ---------------------------------------------------------------------------------

def lab34_topology():
    d = Diagram("lab-3.4-topology", 860, 380, "Lab 3.4: a home network in miniature")
    d.text("lan", 105, 46, 330, 22, "LAN 192.168.1.0/24 (private)", bold=True, size=11)
    d.text("wan", 430, 46, 330, 22, "Public side 203.0.113.0/24 (TEST-NET-3)", bold=True, size=11)
    d.box("laptop", 20, 74, 210, 96,
          "laptop\neth0 192.168.1.10/24\n+ 192.168.1.11 (step 5)\ndefault via 192.168.1.1\napp :8000 (python3 http.server)",
          "blue", size=11)
    d.box("router", 325, 74, 210, 96, "router\nlan 192.168.1.1/24\nwan 203.0.113.1/24\nnet.ipv4.ip_forward=1", "orange",
          size=11)
    d.box("web", 630, 74, 210, 96, "web (\"the internet\")\neth0 203.0.113.50/24\nweb server :80\nno route to 192.168.1.0/24",
          "purple", size=11)
    d.edge("laptop", "router", "eth0 ↔ lan", both=True, size=10)
    d.edge("router", "web", "wan ↔ eth0", both=True, size=10)
    d.group("nat", 150, 206, 560, 156, "router · iptables -t nat (rules you add)", size=12)
    d.box("snat", 170, 236, 520, 50,
          "step 3 · POSTROUTING (after the routing decision)\n-s 192.168.1.0/24 -o wan -j MASQUERADE", "white", size=11)
    d.box("dnat", 170, 296, 520, 50,
          "step 6 · PREROUTING (before the routing decision)\n-i wan -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.10:8000",
          "white", size=11)
    d.edge("router", "nat", dashed=True)
    return d


def lab34_nat_rewrites():
    d = Diagram("lab-3.4-nat-rewrites", 860, 514, "What the router rewrites (ports from the tested run)")
    d.text("h1", 20, 42, 270, 22, "Packet arrives at the router", bold=True)
    d.text("h2", 315, 42, 230, 22, "What the router does", bold=True)
    d.text("h3", 570, 42, 270, 22, "Packet leaves the router", bold=True)
    lanes = [
        ("laptop → web, no NAT yet (step 2)\n192.168.1.10:39970 → 203.0.113.50:80",
         "no rule: forwarded unchanged\n(ip_forward=1)", "gray",
         "192.168.1.10:39970 → 203.0.113.50:80\nweb has no route back: curl (28)"),
        ("laptop → web (step 3)\n192.168.1.10:56196 → 203.0.113.50:80",
         "POSTROUTING · MASQUERADE\nsource → wan's address\nafter the routing decision", "orange",
         "203.0.113.1:56196 → 203.0.113.50:80\nweb logs 203.0.113.1"),
        ("the reply, web → router\n203.0.113.50:80 → 203.0.113.1:56196",
         "conntrack entry\nrewrites the reply back\nno rule needed", "green",
         "203.0.113.50:80 → 192.168.1.10:56196\nback to the laptop"),
        ("a second host, same port (step 5)\n192.168.1.11:40000 → 203.0.113.50:80",
         "MASQUERADE + a port clash\n203.0.113.1:40000 → web:80\nis taken (still TIME_WAIT)", "orange",
         "203.0.113.1:41599 → 203.0.113.50:80\nthe P in PAT: the port changes too"),
        ("web → router:8080 (step 6)\n203.0.113.50:59870 → 203.0.113.1:8080",
         "PREROUTING · DNAT\ndestination → 192.168.1.10:8000\nbefore the routing decision", "orange",
         "203.0.113.50:59870 → 192.168.1.10:8000\nthe laptop logs the real client"),
    ]
    for i, (inp, act, ac, out) in enumerate(lanes):
        y = 72 + i * 74
        d.box(f"in{i}", 20, y, 270, 58, inp, "white", size=11)
        d.box(f"act{i}", 315, y, 230, 58, act, ac, size=11)
        d.box(f"out{i}", 570, y, 270, 58, out, "white", size=11)
        d.edge(f"in{i}", f"act{i}")
        d.edge(f"act{i}", f"out{i}")
    d.box("note", 20, 448, 820, 50,
          "Only the first packet of a connection (the SYN) goes through the nat table: each rule counted 1 packet, 60 bytes.\n"
          "Every later packet is translated from the conntrack entry (conntrack -L shows both directions).",
          "yellow", size=11, bold_first=False)
    return d


# ---- Lab 3.5 ---------------------------------------------------------------------------------

def lab35_topology():
    d = Diagram("lab-3.5-topology", 860, 310, "Lab 3.5: the network the script builds (one fault hidden in it)")
    d.box("client", 20, 56, 150, 104, "client\neth0 10.1.1.10/24\nresolver: see\n/etc/resolv.conf", "blue", size=11)
    d.box("r1", 220, 56, 140, 104, "r1 (router)\neth0 10.1.1.1/24\neth1 10.0.0.1/30", "green", size=11)
    d.box("r2", 480, 56, 140, 104, "r2 (router)\neth1 10.0.0.2/30\neth0 10.2.2.1/24", "green", size=11)
    d.box("server", 670, 56, 170, 104,
          "server\neth0 10.2.2.20/24\nDNS: app.lab → 10.2.2.20\nweb :8080\nbig.txt = 200,000 bytes", "purple", size=11)
    d.edge("client", "r1", both=True)
    d.edge("r1", "r2", "MTU 1400", both=True, size=11)
    d.edge("r2", "server", both=True)
    for i, (x, net) in enumerate([(195, "10.1.1.0/24"), (420, "10.0.0.0/30"), (645, "10.2.2.0/24")]):
        d.text(f"n{i}", x - 60, 164, 120, 20, net, size=11)
    d.box("complaint", 20, 200, 400, 94,
          "The complaint: ./broken-network.sh test\ncurl -sS -m 5 … http://app.lab:8080/big.txt\n"
          "when it works: 200 200000 bytes\nthe router link is narrower (MTU 1400), like a VPN", "yellow", size=11)
    d.box("ok", 440, 200, 400, 94,
          "When nothing is broken\nthe client's default gateway is r1, the server's is r2\n"
          "both routers forward and know routes to both ends\ninvestigate: ip netns exec <client|r1|r2|server> …",
          "gray", size=11)
    return d


def lab35_method():
    d = Diagram("lab-3.5-method", 860, 510, "The 6-step method in this lab: stop at the first step that fails")
    steps = [
        ("1 · DNS\nDoes the name resolve?",
         "client: cat /etc/resolv.conf · getent hosts app.lab · dig app.lab"),
        ("2 · Route\nA path there and back?",
         "client: ip route · ip neigh · ping · traceroute -n 10.2.2.20\n"
         "r1, r2: sysctl net.ipv4.ip_forward · ip route\nserver: ip route"),
        ("3 · Port\nCan I reach the port?",
         "client: curl -m 5 http://10.2.2.20:8080/   (by IP, so DNS is out of the picture)"),
        ("4 · Listener\nListening, and on which address?",
         "server: ss -ltnp"),
        ("5 · Rules\nFirewall dropping or rejecting?",
         "every node: iptables -S   (iptables -L -n -v for the counters)"),
        ("6 · App\nRight answer, small and large?",
         "client: fetch / and /big.txt · tracepath from both ends"),
    ]
    for i, (step, tests) in enumerate(steps):
        y = 50 + i * 72
        d.box(f"s{i}", 20, y, 230, 54, step, "blue", size=11)
        d.box(f"t{i}", 270, y, 570, 54, tests, "white", size=11, align="left", bold_first=False)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.text("foot", 20, 474, 820, 24, "Read the error first: it tells you which step to start at.", italic=True)
    return d


# ---- Solutions, Level 1 ----------------------------------------------------------------------

def sol1_home_network():
    d = Diagram("sol-1-home-network", 860, 340, "Exercise 19: an example home network (yours will differ)")
    d.box("phone", 20, 62, 140, 48, "Phone\n192.168.29.31", "blue")
    d.box("laptop", 20, 142, 140, 48, "Laptop\n192.168.29.20", "blue")
    d.box("tv", 20, 222, 140, 48, "TV\n192.168.29.40", "blue")
    d.group("box", 230, 46, 430, 280, "Home router box")
    d.box("ap", 250, 100, 170, 44, "Wi-Fi access point", "green")
    d.box("sw", 250, 224, 170, 44, "Switch", "green")
    d.box("rt", 460, 100, 180, 78, "Router + NAT + firewall\nLAN 192.168.29.1\nDHCP server · DNS forwarder", "orange",
          size=11)
    d.box("modem", 460, 262, 180, 44, "Modem / ONT", "gray")
    d.box("isp", 690, 254, 150, 60, "Provider\nWAN IP: public, or\n100.64.x.x if CGNAT", "purple", size=11)
    d.edge("phone", "ap", "Wi-Fi", dashed=True, both=True, size=11)
    d.edge("laptop", "ap", "Wi-Fi", dashed=True, both=True, size=11)
    d.edge("tv", "sw", "cable", both=True, size=11)
    d.edge("ap", "sw", both=True)
    d.edge("sw", "rt", both=True)
    d.edge("rt", "modem", both=True)
    d.edge("modem", "isp", both=True)
    return d


ALL = [labs_map, lab31_topology, lab31_what_comes_back, lab32_topology, lab32_referral_chain,
       lab33_topology, lab33_certificates, lab33_tls_errors, lab34_topology, lab34_nat_rewrites,
       lab35_topology, lab35_method, sol1_home_network]
