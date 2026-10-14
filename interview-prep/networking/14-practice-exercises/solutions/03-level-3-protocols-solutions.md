# Solutions · Level 3 Exercises

> ⚠️ Spoilers for the [Level 3 exercises](../03-level-3-protocols.md). Where an answer depends on a measured value, it points to the lesson or lab where it was **tested in the lab container** (Ubuntu 24.04, kernel 6.18, Oct 2026). Calculations were checked with Python. Statements about AWS behaviour are from AWS documentation and are marked as vendor-specific.

## A · Ethernet and switching

**A1.** a) **Forwards** it out of that one port only. b) **Floods** it out of every port except the one it came in on (unknown unicast). c) **Floods** it: a broadcast goes to every port in the VLAN. In every case it also **learns** the source MAC on the incoming port.

**A2.** **1,500 bytes** (the standard MTU). EtherTypes: IPv4 `0x0800`, ARP `0x0806`, IPv6 `0x86DD`, 802.1Q tag `0x8100`.

**A3.** The printer's entry has aged out, so the first frame is **flooded** to every port (unknown unicast). It's harmless: other hosts see a destination MAC that isn't theirs and drop it, and as soon as the printer replies, the bridge **learns** its port again and stops flooding. (The ageing time was read from a Linux bridge in [Lab 1.2](../../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md).)

**A4.** **No.** A VLAN is a separate **broadcast domain**: the ARP request from VLAN 10 never reaches VLAN 20, so the PCs can't even find each other's MAC, whatever their IPs say. To talk they need a **router** (or a layer 3 switch, or a "router on a stick" on a trunk port), and in a sane design **different subnets**, one per VLAN.

## B · Ports and everyday protocols

**B1.**

| Service | Port |
|---|---|
| SSH | 22/tcp |
| DNS | 53/udp and 53/tcp |
| HTTPS | 443/tcp (HTTP/3: 443/udp) |
| PostgreSQL | 5432/tcp |
| MySQL | 3306/tcp |
| Redis | 6379/tcp |
| NTP | 123/udp |
| DHCP server | 67/udp (client: 68/udp) |
| kube-apiserver | 6443/tcp |
| etcd client | 2379/tcp (peers: 2380/tcp) |
| kubelet API | 10250/tcp |
| SMTP submission | 587/tcp (STARTTLS) or 465/tcp (implicit TLS) |
| LDAPS | 636/tcp |
| RDP | 3389/tcp (and udp) |
| NodePort range | 30000–32767 (tcp/udp), the default |

**B2.** UDP: DNS queries, NTP, DHCP, SNMP, WireGuard, VXLAN, **HTTP/3** (it runs over QUIC, which runs over UDP), traditional syslog. TCP: SSH, BGP.

**B3.** Ordinary DNS queries go over **UDP** 53. With only TCP allowed, every UDP query is dropped and times out. A client only switches to TCP when it's told to (`dig +tcp`), or when a UDP answer comes back **truncated** (`TC` flag) because it's too big, which can't happen here because no UDP answer ever arrives. Allow **both** UDP and TCP 53 for a DNS server.

**B4.** **UDP 500** (IKE, the key exchange), **UDP 4500** (NAT traversal: IKE and ESP wrapped in UDP when there's NAT on the path), and **IP protocol 50 (ESP)**, which carries the encrypted traffic when there's no NAT. ESP is its own IP protocol, alongside TCP (6) and UDP (17), so it has **no ports**: the firewall rule must match the protocol number.

**B5.**

| Listener | Probably | Reachable from another machine? |
|---|---|---|
| `127.0.0.53%lo:53` (udp) | `systemd-resolved`'s local DNS stub | **No**: loopback only |
| `0.0.0.0:22` | `sshd` | **Yes**, on every IPv4 address (firewall permitting) |
| `127.0.0.1:2379` | etcd, client port, for local clients | **No** |
| `10.0.1.15:2379` | etcd, client port, on the node's own IP | **Yes**, via `10.0.1.15` (the API servers use it) |
| `*:6443` | kube-apiserver | **Yes**, every address, IPv4 and IPv6 |
| `*:10250` | kubelet API | **Yes**. It should be firewalled to the control plane |

The listening address decides who can connect; the firewall decides who is **allowed** to. Check both.

## C · TCP and UDP

**C1.** `SYN` (client → server) · `SYN, ACK` (server → client) · `ACK` (client → server). In `tcpdump`: `[S]`, `[S.]`, `[.]` ([Lab 3.1](../../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md)).

**C2.** a) A TCP **RST**: curl reports `(7) Couldn't connect to server`, `nc` reports "Connection refused". b) An ICMP **port unreachable** (type 3, code 3). c) **Nothing**: the client retransmits and eventually times out. All three were reproduced in Lab 3.1.

**C3.** `DROP`: no answer at all; the client **retransmits the SYN** with growing gaps and gives up only after its timeout (`curl: (28)`). `REJECT`: the firewall answers at once (a RST or an ICMP error), so the client fails **immediately** with a "refused"-style error. REJECT makes troubleshooting faster (the error is instant and clear). DROP reveals less to a scanner (a dropped port looks like no host at all), which is why internet-facing defaults usually drop.

**C4.**
- `TIME_WAIT` is on the side that **closed first** (the active closer), so here the **server** closed those connections. It's normal and short-lived (60 seconds on Linux), so 5,000 on a busy server is usually fine.
- `CLOSE_WAIT` is on the side that **received** a close but hasn't closed its own socket yet: the **peer** closed first, and **this application hasn't called `close()`**. It doesn't expire on its own.
- **`CLOSE_WAIT` is the worry**: it's almost always an application bug (a leaked connection), and it grows until the process runs out of file descriptors.

**C5.** MSS 1460 = 1500 − 20 (IP) − 20 (TCP). But Linux adds the **TCP timestamps** option (12 bytes with padding) to every data segment, so 1460 − 12 = **1448** bytes of data fit ([3.3](../../03-core-networking-protocols/03-tcp-in-depth.md), seen in Lab 3.1). For a 1400-byte tunnel MTU: 1400 − 20 − 20 = **1360** (Linux's `--clamp-mss-to-pmtu` works this out from the route's MTU, as in [Lab 3.5](../../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md)'s fault 8).

**C6.** Window scaling multiplies the advertised window by 2^scale: 502 × 2⁷ = 502 × 128 = **64,256 bytes**. Without scaling, the 16-bit window field could never exceed 65,535 bytes.

**C7.** The SYN consumes one sequence number on each side.
- Client's data segment: **`seq 1001`, `ack 5001`** (100 bytes: sequence numbers 1001–1100).
- Server's ACK: **`seq 5001`, `ack 1101`** ("I've received everything up to 1100; send 1101 next").

**C8.** **Vendor-specific (AWS):** a NAT gateway removes a connection's entry after **350 seconds** of inactivity. The app and the database each still believe the connection is open. When the app sends on it again, the NAT gateway has no matching entry and answers with a **reset** (AWS documents that it sends a RST to the client in this case), so the app sees "connection reset". Fixes:
- **App:** make the connection pool discard or validate connections idle longer than about 5 minutes (a max-idle setting, or a test query before use).
- **OS:** enable TCP keepalive on the socket and lower `net.ipv4.tcp_keepalive_time` below 350 s (the Linux default is **7,200 s**, two hours, far too long). Keepalive probes keep the NAT entry alive. The app must turn on `SO_KEEPALIVE` for the sysctl to have any effect.

## D · DNS

**D1.** `A` → 5 · `AAAA` → 2 · `CNAME` → 3 · `MX` → 7 · `NS` → 1 · `TXT` → 8 · `PTR` → 6 · `SOA` → 4.

**D2.** A **recursive** query says "give me the final answer, do the work for me" (the `rd` flag): your laptop sends it to its **resolver**. An **iterative** query accepts "here's who to ask next" (a **referral**): the resolver sends these to the root, then the TLD server, then the authoritative server ([Lab 3.2](../../13-hands-on-labs/lab-03.2-trace-dns-resolution.md), step 2, shows the whole chain).

**D3.** `aa` = **authoritative answer**, set only by a server authoritative for the zone. `rd` = **recursion desired**, set by the client. `ra` = **recursion available**, set by a resolver willing to recurse. A resolver's answer from its cache has `rd ra` but **no** `aa`.

**D4.** Cached at 09:58:00 with TTL 300 → valid until **10:03:00**, so its clients may get the old IP for up to 3 minutes after your change (and up to 5 minutes in general, for a resolver that cached it just before 10:00). Negative answers are cached too (RFC 2308): the NXDOMAIN may be served for up to **3,600 seconds** (the lower of the SOA record's own TTL and its minimum field), so a newly created name can stay "missing" for up to an hour for anyone who looked it up just before. Lab 3.2, step 7, shows the negative TTL counting down.

**D5.** a) **The name doesn't exist**: an authoritative server said so. Check the spelling and the zone. b) **The resolver tried and couldn't get an answer**: the authoritative servers are down or unreachable, a delegation is broken, or DNSSEC validation failed. c) The host answered, but **nothing listens on port 53** there. d) **No answer at all**: packets dropped by a firewall, a wrong IP, or the server is down. (All four reproduced in Lab 3.2, step 10.)

**D6.** `getent` uses the system resolver library (like every application), which applies the **search domains**: it tries `api.corp.example` and finds it. `dig` is a DNS debugging tool and by default asks for **exactly** the name you typed (`api.`), which doesn't exist. `dig +search api` behaves like the application.

**D7.** `api.partner.com` has 2 dots, fewer than 5, so the search domains come **first**. In namespace `default`:
1. `api.partner.com.default.svc.cluster.local.`
2. `api.partner.com.svc.cluster.local.`
3. `api.partner.com.cluster.local.`

That's **3** wasted names, usually each asked for both `A` and `AAAA`. If the node's own `resolv.conf` adds search domains (on AWS, typically one like `<region>.compute.internal`), there are more. Fixes: use the FQDN with a **trailing dot** (`api.partner.com.`); or lower `ndots` for the pod (`dnsConfig: options: [{name: ndots, value: "2"}]`). A node-local DNS cache makes the wasted queries cheaper, but doesn't remove them. ([3.4](../../03-core-networking-protocols/04-dns.md#the-trailing-dot-and-the-ndots5-trap-) shows a tested capture.)

## E · HTTP and TLS

**E1.** `200` OK · `301` moved permanently (redirect) · `304` not modified (use your cached copy) · `401` not authenticated (who are you?) · `403` authenticated but **forbidden** · `404` not found · `429` too many requests (rate limited) · `500` the server's own error · `502` bad gateway: the proxy got an **invalid response** (or none) from the backend · `503` service unavailable: overloaded or **no healthy backend** · `504` gateway timeout: the proxy **waited too long** for the backend.

**E2.** Idempotent: **GET, PUT, DELETE** (and HEAD, OPTIONS): doing them twice has the same effect as once. **POST** isn't (two POSTs can create two orders), and **PATCH** isn't guaranteed to be. It matters because networks fail mid-request: a client or proxy may **retry** safely only if the request is idempotent. Retrying a POST can double-charge a customer; that's why payment APIs use **idempotency keys**.

**E3.** The values are cumulative, so subtract:

| Phase | Calculation | Time |
|---|---|---|
| DNS | 0.012 | **12 ms** |
| TCP handshake | 0.045 − 0.012 | **33 ms** (≈ one round trip) |
| TLS handshake | 0.120 − 0.045 | **75 ms** |
| Server processing (to first byte) | 0.480 − 0.120 | **360 ms** |
| Transfer | 0.495 − 0.480 | **15 ms** |

The network parts total 120 ms; **the server took 360 ms** to start answering. Look at the application or its backends (database, upstream API) first, not the network.

**E4.** 1 → **b** · 2 → **c** · 3 → **d** · 4 → **a**. All four were reproduced in [Lab 3.3](../../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md).

**E5.** Visible: the server's **IP**, the **port** (443), **`bank.example`** (in the SNI, in clear text, unless Encrypted Client Hello is used; also in the DNS query if DNS isn't encrypted), and the **amount of data and timing**. Not visible: **`/accounts/123`**, the **cookies** and every other header and body byte (all inside TLS), and in TLS 1.3 the **certificate** too (it's encrypted; Lab 3.3, step 7).

**E6.** `api.example.com` → **yes**. `example.com` → **no** (the wildcard needs exactly one label in its place; certificates usually list `example.com` as a second SAN). `v2.api.example.com` → **no** (a wildcard covers one label only, not several).

**E7.**

| Option | Certificate on | Route by path? | LB → backend encrypted? |
|---|---|---|---|
| Termination at the LB | the load balancer | **Yes** | **No** (plain HTTP inside the network) |
| Re-encryption | the LB **and** the backends | **Yes** | **Yes** (a second TLS connection) |
| Passthrough | the backends only | **No**: the LB sees only encrypted bytes (it can still route on SNI) | **Yes**, end to end |

Typical in AWS: an **ALB** terminates or re-encrypts; an **NLB** with a TCP listener passes through (vendor-specific examples).

## F · ICMP, traceroute and MTU

**F1.** Echo request **8** · echo reply **0** · destination unreachable **3** · time exceeded **11**.

**F2.** **No.** The router at hop 4 forwards traffic fine (later hops answer); it just doesn't send ICMP time-exceeded messages, or rate-limits them. Stars in the middle of a trace that then continues are normal. Only stars from some hop **to the end** suggest a problem, and even then, test the real service (TCP) before blaming the path. Reproduced in [Lab 2.2](../../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md), part C, step 4.

**F3.** `Network is unreachable` is **local**: your own host has no route, so nothing is sent (check `ip route`). `From 10.0.1.1 … Destination Net Unreachable` comes from a **router** (`10.0.1.1`): your packet got that far, and that router has no route onwards. Both reproduced in Lab 2.2.

**F4.** 1500 − 20 (IP header) − 8 (ICMP header) = **1,472** bytes. For 9001: **8,973** bytes.

**F5.** Symptoms: the TCP handshake and **small** requests work; **large** responses (downloads, big pages, `git clone`, SSH after login with lots of output) **hang** and time out; ping with small packets works. Cause: a router can't forward the large packets (smaller MTU ahead) and its ICMP "fragmentation needed" message is dropped by a firewall, so the sender never learns to send smaller packets. Fixes: **allow ICMP type 3 code 4** (and ICMPv6 "packet too big") through firewalls; or **clamp the TCP MSS** on the router at the narrow link; or lower the MTU on the endpoints. All reproduced in Lab 3.5, fault 8.

## G · NAT

**G1.** a) **SNAT** (PAT/masquerade). b) **DNAT** (host port 8080 → container port 80). c) **SNAT**. d) **DNAT** (ClusterIP → a pod IP). Linux applies **DNAT in PREROUTING** (and OUTPUT, for locally generated packets), before the routing decision, so the packet is routed to the new destination; and **SNAT in POSTROUTING**, after routing, when the outgoing interface is known ([8.6](../../08-linux-networking/06-netfilter-nat-and-conntrack.md)).

**G2.** The original packet went from **`192.168.1.10:51514` to `93.184.216.34:443`**. The reply half shows the router expects answers addressed to **`203.0.113.1:51514`** (its public side), so it has SNATed the source to `203.0.113.1` and kept the port. A reply arriving for `203.0.113.1:51514` is rewritten back to **`192.168.1.10:51514`**. (The `431999` is the seconds left before the entry expires: the Linux default for an established TCP connection is 432,000 seconds, five days.)

**G3.** **Source-port exhaustion** on the NAT gateway. Each connection to the **same destination IP, port and protocol** needs a unique source port on the NAT's public IP; AWS documents a limit of **55,000 simultaneous connections per unique destination** per NAT gateway IP address (vendor-specific), and reports failures in the `ErrorPortAllocation` CloudWatch metric. Existing connections keep working; new ones fail. Fixes:
- **Reuse connections** (HTTP keep-alive, connection pooling) instead of opening one per request.
- **Add public IP addresses** to the NAT gateway, or split traffic across **more NAT gateways** (for example one per AZ, with subnets routed to different gateways). Each extra IP adds another set of ports.
- If the partner offers it, reach the API **privately** (for example AWS PrivateLink), with no NAT at all.

**G4.** **Hairpin NAT (NAT loopback).** From the laptop, the packet goes to the router's public IP; the router may DNAT it to `192.168.1.10:8000` only if its rule isn't restricted to the WAN interface (in [Lab 3.4](../../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md) the rule had `-i wan`, so it wouldn't). Even when it does DNAT, the server sees the laptop's **private** source address and **replies directly** over the LAN, bypassing the router; the laptop gets a reply from `192.168.1.10` for a connection it opened to the public IP, and drops it. Fixes: enable **NAT loopback** on the router (it also SNATs these packets so replies return through it), or use **split DNS** so LAN clients resolve the name to the private address.

## H · Putting it together

**H1.** A reference answer. The order matters more than the exact component names, which vary by setup ([3.10](../../03-core-networking-protocols/10-packet-flow-end-to-end.md#the-same-journey-from-a-kubernetes-pod-in-aws-eks)).

1. **DNS.** The app asks the resolver in the pod's `/etc/resolv.conf`: the **kube-dns** Service IP. **kube-proxy's DNAT** sends the query to a **CoreDNS** pod. Because of `ndots:5`, the search domains are tried first and return NXDOMAIN (D7). CoreDNS forwards `api.partner.com` to the **VPC resolver** (Route 53 Resolver, vendor-specific), which resolves it on the internet and returns a public IP.
2. **Routing in the pod.** The pod's default route sends the packet out of its `eth0`, a veth whose other end is on the **node**.
3. **On the node.** With the AWS VPC CNI's default settings, pod traffic to addresses **outside the VPC** is **SNATed to the node's primary IP** (vendor-specific). The node's route sends it to the **subnet's router**.
4. **VPC routing.** The private subnet's route table sends `0.0.0.0/0` to the **NAT gateway**. Security groups (outbound) and network ACLs are checked on the way.
5. **NAT gateway.** **SNAT** (PAT) to its public IP; it records the connection.
6. **Internet gateway → internet → the partner.** Ordinary routing, hop by hop.
7. **TCP and TLS.** Handshake to port 443; the ClientHello carries SNI `api.partner.com`; the pod verifies the certificate against the **CA bundle in its container image**, the name against the SAN, and the dates.
8. **The reply** retraces the path: the NAT gateway and then the node use their connection tables to reverse each translation, back to the pod's IP and port. Security groups are **stateful**, so the reply is allowed; network ACLs are **stateless**, so they must allow the return traffic on ephemeral ports.

**H2.** Example: "Every network path has a maximum packet size. Small things, like a page header or a ping, fit through any path, so they work. A large download is sent in full-size packets; if one link on the path only takes smaller ones, a router is supposed to send back a 'too big, make them smaller' message. When a firewall blocks that message, the sender never finds out: it keeps sending big packets that vanish, and the download hangs. Ping uses small packets, so it says everything's fine."
