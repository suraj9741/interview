# Level 3 Exercises · Core Networking Protocols

> Covers [Level 3](../03-core-networking-protocols/README.md): Ethernet, TCP and UDP, DNS, HTTP, TLS, ICMP, NAT, ports and packet flow.
> ⏱️ about 2–3 hours for all sections (estimate) · Solutions: [solutions/03-level-3-protocols-solutions.md](solutions/03-level-3-protocols-solutions.md)
> Difficulty: 🟢 beginner · 🟡 intermediate · 🟠 advanced · 🔴 expert

**How to use this:** each section matches one or two lessons, so you can do a section right after its lesson. Explain your reasoning in a sentence or two; in an interview, "why" is worth more than the bare answer. For troubleshooting practice, see the [troubleshooting scenarios](04-troubleshooting-scenarios.md) and [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md).

---

## A · Ethernet and switching ([3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md))

**A1.** 🟢 What does a switch do with a frame whose destination MAC is: a) in its MAC table; b) not in its MAC table; c) `ff:ff:ff:ff:ff:ff`?

**A2.** 🟢 What's the largest payload a standard Ethernet frame carries? What EtherType values mean IPv4, ARP, IPv6 and an 802.1Q VLAN tag?

**A3.** 🟡 A Linux bridge forgets a MAC address after 300 seconds of silence (its default ageing time). A printer sends nothing for 10 minutes, then a laptop sends it a job. What does the bridge do with the first frame, and why is that harmless?

**A4.** 🟡 Two PCs plug into the same switch, one in VLAN 10 and one in VLAN 20, with addresses in the same subnet. Can they ping each other? What would you need for them to talk?

---

## B · Ports and everyday protocols ([3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md))

**B1.** 🟢 Give the default port and transport (TCP/UDP) for: SSH · DNS · HTTPS · PostgreSQL · MySQL · Redis · NTP · DHCP (server side) · kube-apiserver · etcd (client) · kubelet API · SMTP submission · LDAPS · RDP · the Kubernetes NodePort range.

**B2.** 🟡 Which of these use UDP (only or mainly)? DNS queries · NTP · DHCP · SSH · SNMP · WireGuard · VXLAN · HTTP/3 · BGP · syslog (traditional)

**B3.** 🟡 A security group allows inbound **TCP 53** to a DNS server, nothing else. Normal lookups from clients time out, yet `dig +tcp` against the same server works. Explain.

**B4.** 🟠 You're opening a firewall for an **IPsec site-to-site VPN**. What must you allow, and why can't one of the items be written as a port?

**B5.** 🟠 `ss -tulpn` on a Kubernetes control-plane node shows these listeners. For each, say which program it probably is and whether **another machine** can connect to it:

```text
udp  UNCONN  127.0.0.53%lo:53
tcp  LISTEN  0.0.0.0:22
tcp  LISTEN  127.0.0.1:2379
tcp  LISTEN  10.0.1.15:2379
tcp  LISTEN  *:6443
tcp  LISTEN  *:10250
```

---

## C · TCP and UDP ([3.2](../03-core-networking-protocols/02-tcp-and-udp.md), [3.3](../03-core-networking-protocols/03-tcp-in-depth.md))

**C1.** 🟢 Write the three packets of the TCP handshake, with their flags, in order.

**C2.** 🟡 What does a client receive when it sends to: a) a closed **TCP** port; b) a closed **UDP** port; c) a port where a firewall **drops** packets?

**C3.** 🟡 From the client's point of view, how does a firewall `DROP` differ from a `REJECT`? Which one makes troubleshooting faster, and which one hides more from an attacker?

**C4.** 🟡 A busy web server shows 5,000 sockets in `TIME_WAIT` and 300 in `CLOSE_WAIT`. Which side closed first in each case? Which number worries you more, and why?

**C5.** 🟠 On a 1500-byte MTU link, a Linux client advertises MSS 1460, but the capture shows data segments of 1448 bytes. Why the difference? If traffic must cross a tunnel with a 1400-byte MTU, what MSS should a router clamp to (assume 20-byte IPv4 and 20-byte TCP headers)?

**C6.** 🟠 A SYN carries `wscale 7`. Later, the same host advertises `win 502`. How many bytes may the other side send before waiting for an ACK?

**C7.** 🟠 The client's initial sequence number is 1000 and the server's is 5000. After the handshake, the client sends 100 bytes of data. What are the `seq` and `ack` numbers on that data segment, and on the server's ACK for it?

**C8.** 🔴 A service connects to a database through an AWS NAT gateway. Connections that sit idle for about 6 minutes fail with a reset the next time the app uses them. Explain the mechanism, and give two fixes (one in the app, one in the OS).

---

## D · DNS ([3.4](../03-core-networking-protocols/04-dns.md))

**D1.** 🟢 Match the record type to its purpose: `A` · `AAAA` · `CNAME` · `MX` · `NS` · `TXT` · `PTR` · `SOA`

1. Which servers are authoritative for a zone
2. IPv6 address
3. An alias to another name
4. Zone metadata, including the negative-caching TTL
5. IPv4 address
6. Reverse lookup: address to name
7. Mail servers for the domain
8. Free text: domain verification, SPF

**D2.** 🟡 Explain the difference between a **recursive** and an **iterative** query. Which kind does your laptop send? Which kind does a resolver send to the root?

**D3.** 🟡 In `dig` output, what do the flags `aa`, `rd` and `ra` mean? Which server sets `aa`?

**D4.** 🟡 A record has a TTL of 300. You change its IP at 10:00:00. A resolver cached the old answer at 09:58:00. Until when might its clients still get the old IP? And if the name **didn't exist** before (it returned NXDOMAIN, with an SOA minimum of 3600), how long could clients keep failing after you create it?

**D5.** 🟠 What does each tell you? a) `status: NXDOMAIN` · b) `status: SERVFAIL` · c) `communications error … connection refused` · d) `communications error … timed out`

**D6.** 🟠 On a server with `search corp.example` in `/etc/resolv.conf`, `getent hosts api` returns an address but `dig api` returns NXDOMAIN. Why?

**D7.** 🔴 A pod (with the standard `search` list of three cluster domains and `ndots:5`) looks up `api.partner.com`. How many names does the resolver try **before** `api.partner.com.` itself, and what are they? Give two ways to cut those wasted queries.

---

## E · HTTP and TLS ([3.5](../03-core-networking-protocols/05-http-and-https.md), [3.6](../03-core-networking-protocols/06-tls-and-certificates.md))

**E1.** 🟢 What does each status mean? `200` · `301` · `304` · `401` · `403` · `404` · `429` · `500` · `502` · `503` · `504`

**E2.** 🟡 Which HTTP methods are **idempotent**: GET, POST, PUT, DELETE, PATCH? Why does it matter for a load balancer or client that retries?

**E3.** 🟡 `curl -w` reports, for one HTTPS request (all times in seconds from the start):

```text
time_namelookup=0.012  time_connect=0.045  time_appconnect=0.120  time_starttransfer=0.480  time_total=0.495
```

How long did the DNS lookup, the TCP handshake, the TLS handshake, the server's processing and the transfer each take? Where would you look first?

**E4.** 🟡 Match each curl error to its cause:

1. `curl: (60) SSL certificate problem: unable to get local issuer certificate`
2. `curl: (60) SSL: no alternative certificate subject name matches target host name 'db.internal'`
3. `curl: (60) SSL certificate problem: certificate has expired`
4. `curl: (52) Empty reply from server`

Causes: a) plain HTTP sent to a TLS port · b) the client doesn't trust the CA · c) the name isn't in the certificate's SAN · d) the clock passed `notAfter`

**E5.** 🟠 An attacker on the Wi-Fi watches your TLS 1.3 connection to `https://bank.example/accounts/123`. Which of these can they see? The server's IP · the port · `bank.example` · `/accounts/123` · the certificate · the cookies · the amount of data and timing.

**E6.** 🟠 A certificate's SAN is `*.example.com`. Does it match: `api.example.com` · `example.com` · `v2.api.example.com`?

**E7.** 🔴 Compare TLS **termination at the load balancer**, **re-encryption** and **passthrough**: for each, where is the certificate installed, can the load balancer route by URL path, and is traffic encrypted between the load balancer and the backend?

---

## F · ICMP, traceroute and MTU ([3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md))

**F1.** 🟢 Give the ICMP type numbers for echo request, echo reply, destination unreachable and time exceeded.

**F2.** 🟡 Traceroute shows `* * *` at hop 4, but hops 5 to 8 answer normally and the destination is reached. Is there a problem at hop 4?

**F3.** 🟡 Explain the difference between `ping: connect: Network is unreachable` and `From 10.0.1.1 icmp_seq=1 Destination Net Unreachable`.

**F4.** 🟠 What's the largest `ping -s` payload that fits through a 1500-byte MTU with "don't fragment" set? Through a 9001-byte MTU?

**F5.** 🟠 Describe the symptoms of a **path MTU black hole**, and two ways to fix it.

---

## G · NAT ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md))

**G1.** 🟡 Which is source NAT and which is destination NAT: a) a home router letting laptops reach the internet; b) `docker run -p 8080:80`; c) an AWS NAT gateway; d) a Kubernetes Service ClusterIP handled by kube-proxy? In which netfilter chain does Linux apply SNAT, and in which DNAT?

**G2.** 🟠 Read this conntrack entry from a NAT router. What were the original source and destination? What will the router rewrite a reply packet's destination to?

```text
tcp 6 431999 ESTABLISHED src=192.168.1.10 dst=93.184.216.34 sport=51514 dport=443 src=93.184.216.34 dst=203.0.113.1 sport=443 dport=51514 [ASSURED]
```

**G3.** 🟠 A fleet of 400 instances behind one NAT gateway calls a single third-party API endpoint. Under load, new connections start failing while existing ones work. What's the likely cause, and three ways to fix it?

**G4.** 🟠 A home-lab user adds a port forward for `public-IP:8080 → 192.168.1.10:8000`. It works from their phone on mobile data, but not from a laptop on the same home Wi-Fi using the public IP. Why?

---

## H · Putting it together ([3.10](../03-core-networking-protocols/10-packet-flow-end-to-end.md)) 🔴

**H1.** A pod in a private EKS subnet calls `https://api.partner.com`. Trace the request from the pod to the partner's server and back: every DNS lookup, every routing decision, every address translation and every TLS check. Name the component that does each step.

**H2.** In one paragraph for a non-network colleague: why can a site load its homepage but hang on a large download, and why is ping no help in finding out?
