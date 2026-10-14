# 3.2 · TCP and UDP: The Two Transport Protocols

> **Level 3 · Core networking protocols** · Lesson 2 of 11 · ⏱️ about 60 minutes (estimate)
> ⬅️ [3.1 Ethernet and switching basics](01-ethernet-and-switching-basics.md) · ➡️ [3.3 TCP in depth](03-tcp-in-depth.md)

## What you'll learn

- What the **transport layer** adds on top of IP: **ports**, and (for TCP) **reliability**.
- The differences between **TCP** and **UDP**, and how to pick one.
- What each looks like on the wire, and what happens when the **port is closed**, for each (tested).
- Port ranges: well-known, registered, ephemeral.
- Why UDP is harder to test and to firewall.

## Before you start

- [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md): ports, sockets and the 5-tuple.
- [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md): the transport layer (L4).

---

## The idea in plain words

IP gets a packet to the right **machine**. It promises nothing else: packets can be lost, duplicated or arrive out of order. The transport layer adds the **port** (which program) and decides how much care to take.

| | TCP | UDP |
|---|---|---|
| Like | A **phone call**: dial, both sides say hello, talk, hang up | A **postcard**: write the address and drop it in the box |
| Setup | 3-way handshake: **SYN → SYN-ACK → ACK** | None |
| Reliable? | **Yes**: lost data is re-sent, order is kept, duplicates removed | **No**: each datagram arrives once, or not at all, in any order |
| Data shape | A **byte stream** (no message boundaries) | **Messages** (each `send` = one datagram) |
| Flow and congestion control | Yes: it slows down for a slow receiver or a busy network | No: the application must be careful |
| Header | 20 bytes minimum (32 with common options) | **8 bytes** |
| Used by | HTTP/1.1 and HTTP/2, SSH, TLS, databases, the Kubernetes API, SMTP | DNS (mostly), DHCP, NTP, video and voice calls, games, **QUIC/HTTP/3**, VXLAN, WireGuard |

## Why it matters

- Firewalls, security groups and Kubernetes NetworkPolicies are written **per protocol and port**. "Allow 53" isn't enough: DNS needs **UDP 53 and TCP 53**.
- The **failure signals** are different: a closed TCP port answers at once with a reset; a closed UDP port may just stay silent. Knowing this saves hours.
- "Why is DNS on UDP?" and "why is HTTP/3 on UDP?" are classic interview questions.

---

## How it works

### Ports

A port is a 16-bit number (0–65535). The **same number** can be used by TCP and UDP independently: `53/udp` and `53/tcp` are different sockets.

| Range | Name (IANA) | Used for |
|---|---|---|
| 0–1023 | **Well-known** (system) ports | Standard services: 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS. On Linux, binding to them needs root (or a capability) |
| 1024–49151 | **Registered** ports | Applications: 3306 MySQL, 5432 PostgreSQL, 6443 Kubernetes API |
| 49152–65535 | **Dynamic / private** ports | Temporary client ports, in IANA's recommendation |

**Ephemeral ports:** your side of an outgoing connection gets a temporary port chosen by the operating system. Linux uses **32768–60999** by default, not IANA's range **(tested in the lab container: `net.ipv4.ip_local_port_range = 32768 60999`)**. A full list of common ports is in [references/common-ports.md](../references/common-ports.md).

### UDP on the wire (tested)

A single UDP message between two namespaces (`client` `10.10.0.1` → `server` `10.10.0.2`, with `nc -u -l -p 5000` listening on the server) **(tested in the lab container)**:

```console
$ echo "hello over udp" | nc -u -w 1 10.10.0.2 5000
```

```text
IP 10.10.0.1.50171 > 10.10.0.2.5000: UDP, length 15
```

That's the **whole conversation**: one packet, no handshake, no acknowledgement. The sender has no idea whether it arrived (it did: the server printed `hello over udp`).

### TCP on the wire (tested)

The same kind of request over TCP (`curl` to a web server on port 8080) takes **12 packets** for a 22-byte answer: 3 to open, data and acknowledgements, and 4 to close. Those 12 packets are dissected line by line in [3.3](03-tcp-in-depth.md). The first three **(tested in the lab container)**:

```text
10.10.0.1.54370 > 10.10.0.2.8080: Flags [S], seq 4014836867, win 64240, options [mss 1460,sackOK,TS val 598057074 ecr 0,nop,wscale 10], length 0
10.10.0.2.8080 > 10.10.0.1.54370: Flags [S.], seq 3219876447, ack 4014836868, win 65160, options [mss 1460,...], length 0
10.10.0.1.54370 > 10.10.0.2.8080: Flags [.], ack 1, win 63, options [nop,nop,TS val 598057075 ecr 3005015560], length 0
```

The first packet, the **SYN**, is how a firewall or NAT rule recognises a **new connection**. In [Lab 3.4](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md) a port-forwarding rule's counter showed exactly **1 packet, 60 bytes**: one SYN (20-byte IP header + 40-byte TCP header with options). Only the first packet of a connection hits a NAT rule; conntrack handles the rest.

### When the port is closed

This is the most useful practical difference **(tested in the lab container)**.

**TCP, nothing listening on port 9999:** the server's kernel answers the SYN with a **reset** (`R`) immediately.

```text
10.10.0.1.51358 > 10.10.0.2.9999: Flags [S], seq 2750311665, win 64240, ...
10.10.0.2.9999 > 10.10.0.1.51358: Flags [R.], seq 0, ack 2750311666, win 0, length 0
```

```console
$ curl http://10.10.0.2:9999/
curl: (7) Failed to connect to 10.10.0.2 port 9999 after 0 ms: Couldn't connect to server
$ nc -zv -w 2 10.10.0.2 9999
nc: connect to 10.10.0.2 port 9999 (tcp) failed: Connection refused
```

**UDP, nothing listening on port 5353:** the server's kernel answers with an **ICMP "port unreachable"**…

```text
10.10.0.1.45927 > 10.10.0.2.5353: domain [length 3 < 12] (invalid)
10.10.0.2 > 10.10.0.1: ICMP 10.10.0.2 udp port 5353 unreachable, length 39
```

…but `nc` **didn't notice** and exited with status 0, because it sent its one datagram and stopped. And if a firewall drops the ICMP message (very common), the sender gets **nothing at all**.

| | Port open | Port closed | Firewall drops it |
|---|---|---|---|
| **TCP** | Handshake completes | **RST** at once → "Connection refused" | Silence → retries → **timeout** |
| **UDP** | Silence, or an application reply | ICMP port unreachable (if not filtered) | **Silence** |

So for UDP, **"no answer" proves nothing**. Test UDP services with a real client for that protocol (`dig` for DNS, `ntpdate -q` / `chronyc` for NTP), not with a port scanner.

### Choosing between them

Use **TCP** when every byte must arrive, in order, and you'd rather wait than lose data: web pages, APIs, file transfers, databases, SSH.

Use **UDP** when:

- **Late data is useless** (a voice call can't wait for a re-sent packet from 300 ms ago; skip it).
- The exchange is **one small question and one small answer** (DNS, NTP, DHCP): a handshake would triple the time.
- You need **broadcast or multicast** (DHCP Discover): TCP is always one-to-one.
- You want to build your **own reliability** in user space: **QUIC** (the transport under **HTTP/3**) runs over UDP so it can avoid TCP's head-of-line blocking and be upgraded without changing operating systems ([3.5](05-http-and-https.md)).

**DNS uses both:** UDP for normal queries; **TCP** when the answer is too big for one UDP message (the server sets the "truncated" flag and the client retries over TCP), and for zone transfers.

---

## Try it

**On your Mac:**

```bash
lsof -nP -iTCP -sTCP:LISTEN     # TCP listening sockets
lsof -nP -iUDP                  # UDP sockets
nc -zv -G 3 google.com 443      # does a TCP port answer?
dig +tcp google.com             # force DNS over TCP
```

**On Linux:**

```bash
ss -tlnp                        # TCP listening sockets (t=TCP, l=listening, n=numeric, p=process)
ss -ulnp                        # UDP sockets
ss -tan                         # all TCP sockets and their states
sudo tcpdump -i any -nn 'udp port 53'   # watch DNS queries
```

## In the real world

- **AWS security groups and NACLs** have separate rules per protocol. A NACL is **stateless**, so it must also allow the **return traffic** to the client's **ephemeral ports** (AWS suggests 1024–65535); a security group is stateful and doesn't need this. Forgetting it gives **timeouts**.
- **Kubernetes:** a Service port has a `protocol` (TCP by default). CoreDNS needs **both** UDP and TCP 53 allowed in NetworkPolicies.
- **Load balancers:** AWS NLB supports TCP, UDP and TLS listeners; ALB is HTTP/HTTPS only (and therefore TCP only).
- **NAT and firewalls** track UDP "connections" with a **timeout** (there's no FIN), so long-idle UDP flows (VPNs, VoIP) send keepalives.

## Common mistakes

| Mistake | Fix |
|---|---|
| Opening only UDP 53 for DNS | Open **UDP and TCP** 53 |
| Treating "no reply" from a UDP port as "closed" | Use a protocol-specific client (`dig`, `chronyc`) |
| Assuming TCP preserves message boundaries | It's a byte stream; applications add their own framing (HTTP headers, length prefixes) |
| "UDP is unreliable, so never use it" | Reliability can be built on top (QUIC); for real-time media, retransmission is the wrong trade-off |

## Troubleshooting

| What you see | Meaning | Next step |
|---|---|---|
| `Connection refused` (instant) | Reached the host; **nothing is listening** on that TCP port (or a firewall sent a reject) | `ss -tlnp` on the server: right port? Listening on `0.0.0.0` or only `127.0.0.1`? |
| `Connection timed out` / curl `(28)` | SYNs got **no answer**: a firewall drop, wrong IP, or routing | Capture on the server: do SYNs arrive? ([3.3](03-tcp-in-depth.md), [3.11](11-troubleshooting-connectivity.md)) |
| UDP app gets no reply | Could be anything: closed port, filtered ICMP, firewall | Capture on both ends; test with the protocol's own client |
| DNS works for small names, fails for some big answers | TCP 53 blocked | `dig +tcp name @server` |

## Hands-on lab

[Lab 3.1 · Capture a TCP handshake](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md): parts C and E compare a closed TCP port, a closed UDP port and an open UDP port.

## Interview angle

- ⭐ **"TCP vs UDP?"** → TCP: connection-oriented, reliable, ordered byte stream with flow and congestion control. UDP: connectionless datagrams, no guarantees, 8-byte header, lower latency. Give an example of each and why.
- ⭐ **"Why does DNS use UDP?"** → One small question, one small answer: no handshake needed. Falls back to TCP for large responses and zone transfers, so allow both.
- **"Why is HTTP/3 on UDP?"** → QUIC implements reliability per stream in user space, avoiding TCP head-of-line blocking and allowing faster handshakes combined with TLS 1.3.
- **"How do you know a port is closed vs filtered?"** → TCP closed = RST ("refused"); filtered = timeout. UDP closed = ICMP port unreachable, if not itself filtered.
- **"NACL timeouts but security group looks fine?"** → NACLs are stateless: allow the ephemeral return ports.

## Check yourself

1. Which of these use UDP: DHCP, SSH, NTP, HTTP/3, PostgreSQL, a VXLAN overlay?
2. A client connects to `10.0.0.5:5432` and gets `Connection refused` at once. Is the network path working?
3. Why can't TCP be used for DHCP Discover?
4. A firewall allows TCP 53 only. What breaks?
5. What range does Linux use for ephemeral ports by default, and where do you check it?

<details>
<summary><b>Answers</b> (try first)</summary>

1. **UDP:** DHCP, NTP, HTTP/3 (QUIC), VXLAN. **TCP:** SSH, PostgreSQL.
2. **Yes**: the SYN reached the host and its kernel sent a reset back. The problem is on the host: nothing listens on 5432 there (or it listens on another address), or a local firewall rejects it.
3. The client has no IP address and doesn't know the server, so it must **broadcast**; TCP only works between two known endpoints.
4. Normal DNS queries (UDP) fail, so almost all name resolution breaks.
5. **32768–60999**; `cat /proc/sys/net/ipv4/ip_local_port_range` or `sysctl net.ipv4.ip_local_port_range`.

</details>

## Summary

- **TCP** = reliable, ordered byte stream with a handshake. **UDP** = fire-and-forget datagrams, 8-byte header.
- Closed TCP port → **RST** ("refused"); filtered → **timeout**. Closed UDP port → ICMP port unreachable, **often silent**.
- Ports: well-known 0–1023, registered 1024–49151, dynamic 49152–65535; Linux ephemeral **32768–60999**.
- DNS needs **UDP and TCP 53**. HTTP/3 runs over **UDP** (QUIC).

## Next

➡️ [3.3 · TCP in depth](03-tcp-in-depth.md): the handshake, sequence numbers, windows, retransmission and connection states, packet by packet.
