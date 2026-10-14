# 08 · The OSI Model, Layer by Layer ⭐

The OSI model splits "sending data over a network" into **7 layers**. Each layer does one job and only talks to the layer just above and just below it. Real networks run **TCP/IP**, not OSI, but everyone (interviewers, AWS docs, load balancer names) still uses the OSI numbers: "an L4 load balancer", "an L7 rule", "it's an L2 problem".

Keep the story in mind: **a packet is a letter**. The OSI model is the list of envelopes the letter goes into before it leaves the building, and which person in the building reads which envelope.

![The 7 OSI layers](diagrams/08-osi-layers.drawio.svg)

## The 7 layers on one page ⭐

| # | Layer | Its one job | Data is called | Address it uses | Examples | Devices that work here |
|---|---|---|---|---|---|---|
| 7 | **Application** | What the program wants to say | data | URL, hostname | HTTP, HTTPS, DNS, SSH, SMTP, gRPC | ALB, API gateway, ingress-nginx, WAF |
| 6 | **Presentation** | How the data is written: format, encryption, compression | data | – | TLS, JSON, UTF-8, gzip, JPEG | (in software) |
| 5 | **Session** | Open, keep and close a conversation | data | session ID | TLS session resume, RPC sessions, NetBIOS | (in software) |
| 4 | **Transport** | Program to program: ports, reliability, order | **segment** (TCP) / **datagram** (UDP) | **port** | TCP, UDP, QUIC | NLB, security group, kube-proxy, L4 firewall |
| 3 | **Network** | Machine to machine, across networks | **packet** | **IP address** | IPv4, IPv6, ICMP, IPsec, BGP / OSPF (routing) | Router, route table, NAT gateway, iptables |
| 2 | **Data link** | Next hop on the **same** network | **frame** | **MAC address** | Ethernet, Wi-Fi (802.11), ARP, VLAN (802.1Q) | Switch, bridge (`docker0`), veth, NIC |
| 1 | **Physical** | Bits as electricity, light or radio | **bits** | – | Ethernet cables, fibre, Wi-Fi radio | Cable, hub, repeater, NIC |

**Remember the order:**
- 7 → 1 (top down): **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing
- 1 → 7 (bottom up): **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way

## How the layers work together: encapsulation ⭐

When you **send**, data starts at layer 7 and goes **down**. Each layer puts the data from above inside its own envelope (it adds a **header**) and hands it down. This is **encapsulation**.

When you **receive**, it goes **up**. Each layer opens its own envelope, reads its header, and hands what's inside to the layer above. This is **decapsulation**.

![Encapsulation of an HTTP request](diagrams/08-osi-encapsulation.drawio.svg)

Example: `curl http://10.0.2.15/health` from `10.0.1.25`.

| Step | Layer | What gets added |
|---|---|---|
| 1 | L7 | curl writes `GET /health HTTP/1.1` and `Host: 10.0.2.15` |
| 2 | L6 / L5 | Nothing here, because it's plain HTTP. For HTTPS, TLS encrypts the request here. |
| 3 | L4 | TCP header: source port `45000` (ephemeral), destination port `80`, sequence numbers |
| 4 | L3 | IP header: source `10.0.1.25`, destination `10.0.2.15`, TTL `64` |
| 5 | L2 | Ethernet header: source MAC (my card), destination MAC (**the next hop**: the gateway if `10.0.2.15` is in another subnet), plus a checksum at the end (FCS) |
| 6 | L1 | The NIC turns the frame into signals on the wire or radio |

**The key idea:** IP addresses (L3) say **where the letter finally goes**. MAC addresses (L2) say **who carries it on this one hop**. At every router, the old L2 envelope is thrown away and a new one is written. The IPs stay the same end to end, unless NAT changes them ([02](02-nat.md)).

**Same layer talks to same layer.** The TCP on my machine "talks" to the TCP on the server (sequence numbers, ACKs), even though the bytes really travel down my stack and up theirs. This is called **peer-to-peer communication between layers**.

## Layer 1 · Physical

**Job:** move **bits** (0s and 1s) from one card to the next, as electricity (copper), light (fibre) or radio (Wi-Fi).

**How it works:**
- It decides **voltage, light pulses or radio frequencies**, the connector type, the cable length, and the speed (1 Gbit/s, 10 Gbit/s).
- It has **no addresses** and doesn't understand frames. It just sends bits to whoever is on the other end of the wire.
- **Duplex:** full duplex = send and receive at the same time (modern Ethernet). Half duplex = one at a time (old hubs, Wi-Fi radio).

**Devices:** cables (Cat6, fibre), **hub** (repeats every bit to every port), **repeater**, the physical part of the **NIC**, Wi-Fi radio.

**What breaks here:** a loose cable, a bad transceiver, the link is down, a speed / duplex mismatch (slow, many errors).

**On Linux:**

```bash
ip link show eth0          # "state UP" and "LOWER_UP" = the cable / link is up
ethtool eth0               # speed, duplex, "Link detected: yes"
```

> **In the cloud:** AWS owns layer 1. You never see a cable. The closest thing you control is the **instance type**, which sets the network bandwidth ("up to 10 Gbit").

## Layer 2 · Data link

**Job:** deliver a **frame** to the **next device on the same local network** (the same subnet, the same Wi-Fi, the same bridge).

**How it works:**
- Every network card has a **MAC address**: 48 bits, like `02:42:ac:11:00:02`. It only matters on the local network.
- **A switch learns** which MAC is behind which port by reading the **source MAC** of every frame. It then sends each frame **only** to the port of the destination MAC. If it doesn't know the MAC yet, it **floods** the frame to every port.
- **Broadcast:** destination `ff:ff:ff:ff:ff:ff` = everyone on the local network. A **broadcast domain** is everyone who hears it; a router stops it.
- **ARP** (Address Resolution Protocol) connects L3 to L2: "Who has `172.17.0.3`? Tell `172.17.0.2`." The owner answers with its MAC, and the answer is cached in the **ARP table**.
- **VLAN** (802.1Q) puts a tag in the frame so one physical switch can act as several separate networks.
- The frame ends with an **FCS** (a checksum). A frame with a bad checksum is dropped.
- Two sub-layers you may hear: **LLC** (talks to L3) and **MAC** (talks to the wire).

**Devices:** **switch**, **bridge**, the NIC, Wi-Fi access point. Virtual ones: **`docker0`** and `br-xxxx` (Linux bridges = virtual switches), **veth pairs**, **VXLAN** (L2 frames carried inside UDP, used by Flannel and Docker overlay networks).

**Docker link:** containers on the **same bridge** talk at **layer 2**: container A ARPs for container B's MAC, and the bridge forwards the frame. No router, no NAT ([03](03-docker-bridge.md)).

**What breaks here:** a wrong VLAN, a duplicate MAC, a stale ARP entry, an MTU mismatch (big packets disappear, small ones work: common with VXLAN overlays, which add 50 bytes of headers).

**On Linux:**

```bash
ip link show                       # MAC address of every interface ("link/ether ...")
ip neigh                           # the ARP table: IP → MAC
bridge link                        # which veths are plugged into which bridge
```

> **AWS link:** a VPC does **not** do real broadcast or ARP flooding. AWS answers ARP for you (from the VPC's own mapping table). That's why you can't run your own "floating IP" with ARP tricks in a VPC.

## Layer 3 · Network ⭐

**Job:** get a **packet** from the source **machine** to the destination **machine**, even across many networks.

**How it works:**
- Every machine has an **IP address** and a **subnet** (CIDR, see [01](01-basics.md)). The subnet says what's "local".
- **Routing decision:** for every packet, the kernel asks: "Is the destination in my subnet?"
  - **Yes:** send it directly (ARP for the destination's MAC).
  - **No:** send it to the **gateway** (ARP for the **gateway's** MAC), and let the router decide the next hop.
- The **route table** picks the most specific match (**longest prefix match**): `10.0.2.0/24` wins over `10.0.0.0/16`, which wins over `0.0.0.0/0` (default).
- **TTL** (Time To Live): every router subtracts 1. At 0, the packet is dropped and an ICMP "time exceeded" goes back. This stops loops, and it's how `traceroute` works.
- **Fragmentation:** if a packet is bigger than the next link's **MTU** (usually 1500 bytes), it's split, or dropped if "Don't Fragment" is set (ICMP "fragmentation needed" goes back).
- **ICMP** is L3's helper for errors and tests: `ping` (echo request / reply), "destination unreachable", "time exceeded".
- **NAT** changes IP addresses (and usually ports) at this layer ([02](02-nat.md)).

**Devices:** **router**, **L3 switch**, the Linux kernel itself (`net.ipv4.ip_forward=1` makes Linux a router: Docker turns it on). In AWS: the **VPC router**, **route tables**, **internet gateway**, **NAT gateway**, **Transit Gateway**, **VPC peering**. **NACLs** filter by IP (and port), so they sit at L3–L4.

**Kubernetes link:** each pod gets its own IP, and the CNI (AWS VPC CNI, Calico, Cilium) makes sure every pod can reach every other pod's IP without NAT. That's a layer-3 promise.

**What breaks here:** no route, a wrong gateway, overlapping CIDRs (two VPCs both `10.0.0.0/16` can't be peered), a blocked ICMP that breaks MTU discovery.

**On Linux:**

```bash
ip addr                    # my IP addresses and subnets
ip route                   # the route table ("default via ..." = gateway)
ip route get 8.8.8.8       # which route and interface this one packet would use
ping -c 3 10.0.2.15        # L3 reachability (only if ICMP is allowed)
traceroute 10.0.2.15       # every router on the way (uses TTL)
```

## Layer 4 · Transport ⭐

**Job:** get data from a **program** on one machine to a **program** on the other. L3 finds the machine; **L4 finds the program**, using **ports**.

**How it works:**
- A connection is identified by the **5-tuple**: protocol, source IP, source port, destination IP, destination port. conntrack ([02](02-nat.md)) tracks exactly this.
- **TCP** (reliable, like a phone call):
  - **3-way handshake:** `SYN` → `SYN-ACK` → `ACK`. Only then does data flow.
  - **Sequence numbers + ACKs:** every byte is numbered. Lost data is **resent**; data arriving out of order is **put back in order**.
  - **Flow control** (the receive window): the receiver says how much it can take, so a fast sender doesn't drown a slow receiver.
  - **Congestion control** (slow start, CUBIC, BBR): the sender slows down when the network is full.
  - **Closing:** `FIN` → `ACK`, both ways (4 steps). The side that closes first waits in **TIME_WAIT** for a while.
  - **RST** = "no, go away": sent when nothing listens on that port (**connection refused**).
- **UDP** (like a postcard): no handshake, no order, no resend. Just a small header with ports, length and checksum. Fast and simple: DNS, video, VXLAN, WireGuard.
- **QUIC** (HTTP/3) runs on UDP but adds TCP-like reliability and built-in TLS in user space.

**Devices and tools:** **L4 load balancer** (AWS **NLB**: forwards TCP/UDP by IP and port, doesn't read HTTP), **security groups** (stateful, allow by protocol + port), stateful firewalls, **kube-proxy** (Service IP:port → pod IP:port with iptables or IPVS), Kubernetes **Services** (`ClusterIP`, `NodePort`).

**What breaks here:**

| Symptom | What it means at L4 |
|---|---|
| `Connection refused` | The packet reached the machine, and it answered **RST**: nothing listens on that port |
| `Connection timed out` | No answer at all: a firewall, SG or NACL **dropped** the SYN |
| Many `TIME_WAIT` / port exhaustion | Too many short connections from one IP: use keep-alive / connection pooling |
| Slow transfers, retransmits | Packet loss or a small window: check `ss -ti` |

**On Linux:**

```bash
ss -lntp                   # which programs listen on which TCP ports
ss -tan                    # all TCP connections and their states (ESTAB, TIME_WAIT, ...)
nc -zv 10.0.2.15 5432      # can I open a TCP connection to this port?
sudo tcpdump -ni any 'tcp port 80'   # watch SYN, SYN-ACK, ACK, FIN on the wire
```

## Layer 5 · Session

**Job:** **open, keep and close** a conversation between two programs, and resume it if it breaks.

**How it works:**
- It decides who talks when, adds **checkpoints** so a long transfer can continue after a failure instead of starting again, and tears the dialog down at the end.
- In TCP/IP there's **no separate session layer**. Its work is done by the app or a library: **TLS session resumption** (skip the full handshake on reconnect), **HTTP keep-alive** (reuse one TCP connection for many requests), RPC sessions, **sticky sessions** on a load balancer (cookies).

**Examples you may be asked about:** NetBIOS, RPC, PPTP, SOCKS (often called L5), SQL sessions, SMB sessions.

**What breaks here:** sessions dropped by an idle timeout (ALB default **60 s**, NLB TCP idle timeout **350 s**), so long-lived connections need keep-alives.

## Layer 6 · Presentation

**Job:** make sure the receiver can **understand** the data: the **format**, the **encryption** and the **compression**.

**How it works:**
- **Translation / encoding:** characters (ASCII, UTF-8), data formats (JSON, XML, Protobuf), media formats (JPEG, MP4).
- **Encryption:** TLS / SSL is usually placed here (some put it at L5 or "between L4 and L7"; say that the OSI model doesn't fit TLS perfectly).
- **Compression:** gzip, brotli (`Content-Encoding: gzip`).
- In TCP/IP, this is also part of the application or its libraries (OpenSSL, the JSON parser).

**What breaks here:** a TLS certificate error (expired, wrong name), a TLS version or cipher mismatch, wrong character encoding (garbled text).

```bash
openssl s_client -connect example.com:443 -servername example.com   # see the cert and the TLS version
curl -v https://example.com                                          # shows the TLS handshake, then HTTP
```

## Layer 7 · Application ⭐

**Job:** the protocol **the program itself speaks**. It's not the app (Chrome, nginx); it's the language the app uses on the network.

**How it works:**
- **HTTP/HTTPS:** method, path, host, headers, status codes (`200`, `404`, `502`). An L7 device can read all of these.
- **DNS:** turns names into IPs ([04](04-dns.md)). DNS is an L7 protocol, even though it's usually carried in UDP.
- Others: SSH, FTP, SMTP/IMAP (email), DHCP (gets your IP address, carried in UDP), gRPC (HTTP/2), MQTT, SNMP.

**Devices and tools:** **L7 load balancer** (AWS **ALB**: routes by host, path or header, terminates TLS), **reverse proxy** (nginx, Envoy, HAProxy in HTTP mode), Kubernetes **Ingress** and **Gateway API**, **API gateway**, **WAF**, a service mesh sidecar (Istio / Linkerd).

**What breaks here:** `502` (the proxy got a bad answer from the backend), `503` (no healthy backend), `504` (the backend was too slow), a wrong `Host` header, a wrong path rule, DNS returning the wrong IP.

```bash
curl -v http://10.0.2.15/health      # the full L7 request and response
dig +short google.com                # L7 DNS query
```

## OSI vs TCP/IP ⭐

The OSI model is the **teaching model** (from ISO, 1984). The internet actually runs the **TCP/IP model**, which has 4 layers (some books say 5, keeping Physical separate).

| OSI (7 layers) | TCP/IP (4 layers) | Protocols |
|---|---|---|
| 7 Application · 6 Presentation · 5 Session | **Application** | HTTP, DNS, SSH, TLS |
| 4 Transport | **Transport** | TCP, UDP |
| 3 Network | **Internet** | IP, ICMP |
| 2 Data link · 1 Physical | **Link** (Network access) | Ethernet, Wi-Fi, ARP |

**What to say:** "OSI is a reference model for talking about networks; TCP/IP is what's implemented. We still use OSI numbers, like L4 vs L7 load balancers."

## Where common things sit (quick reference)

| Thing | Layer | Why |
|---|---|---|
| Hub | L1 | Repeats bits to every port |
| Switch, Linux bridge, `docker0` | L2 | Forwards by MAC |
| ARP | L2 / L3 | Finds the MAC for an IP (it's carried in L2 frames, and it serves L3) |
| Router, route table, VPC router | L3 | Forwards by IP |
| `ping`, `traceroute` (ICMP) | L3 | ICMP has no ports |
| NAT, MASQUERADE, DNAT | L3 / L4 | Changes IPs, and usually ports too |
| NACL | L3 / L4 | Stateless, filters IP + port |
| Security group, stateful firewall | L4 | Stateful, filters protocol + port |
| NLB, kube-proxy, `NodePort` | L4 | Forwards TCP/UDP by IP + port |
| TLS | L6 (or L5 / "4.5") | Encryption; the OSI fit isn't perfect |
| ALB, Ingress, nginx proxy, API gateway, WAF | L7 | Reads HTTP host, path, headers |
| Kubernetes NetworkPolicy | L3 / L4 | Pod IPs / labels + ports (Cilium can also do L7) |
| DNS, DHCP | L7 | Application protocols (carried in UDP) |

## Debugging bottom up ⭐🔥

When "it doesn't work", walk the layers from the bottom. The [6-step debugging method](06-debugging.md) is this idea in practice.

| Layer | Question | Command |
|---|---|---|
| L1 | Is the link up? | `ip link show eth0` |
| L2 | Do I know the next hop's MAC? | `ip neigh` |
| L3 | Is there a route, and can I reach the IP? | `ip route get <ip>`, `ping`, `traceroute` |
| L4 | Can I open the port? Is anyone listening? | `nc -zv <ip> <port>`, `ss -lntp` |
| L6 | Does TLS work? | `openssl s_client -connect <host>:443` |
| L7 | Does the app answer correctly? | `curl -v`, `dig` |

**The fastest shortcut:** read the error. `could not resolve host` = DNS (L7). `No route to host` = L3. `timed out` = something dropped it (L3/L4 firewall). `refused` = L4, nothing listening. `502 / 503 / 504` = L7, the network is fine.

## Interview angle

- ⭐ **"Explain the OSI model."** → 7 layers, each with one job. Go top down with one line each and one example: HTTP, TLS, sessions, TCP/UDP, IP, Ethernet/MAC, cables. Then say "real networks use TCP/IP's 4 layers; OSI is how we talk about them".
- ⭐ **"What happens when you type `google.com` in the browser?"** → Walk the layers: DNS (L7) gets the IP → TCP handshake to port 443 (L4) → TLS handshake (L6) → HTTP GET (L7). On the way down, the IP header (L3) gets the destination IP, the Ethernet frame (L2) gets the **gateway's MAC** (found by ARP), and the NIC sends bits (L1). Every router swaps the L2 frame; NAT at the home router changes the source IP.
- ⭐ **"L4 vs L7 load balancer?"** → L4 (NLB) sees only IP + port, forwards TCP/UDP, very fast, keeps the client IP, can't route by path. L7 (ALB) reads HTTP, routes by host / path / headers, terminates TLS, adds `X-Forwarded-For`, can do auth and WAF.
- **"Switch vs router?"** → A switch forwards **frames by MAC** inside one network (L2). A router forwards **packets by IP** between networks (L3), and it stops broadcasts.
- **"MAC vs IP address?"** → MAC = who carries it on **this hop** (changes at every router). IP = the **final destination** (stays the same end to end, unless NAT).
- **"What is encapsulation?"** → Each layer wraps the data from above in its own header on the way down; the receiver unwraps it on the way up. Segment → packet → frame → bits.
- **"At which layer does ping work? Does it use a port?"** → L3, ICMP. No ports, so `ping` working doesn't prove a TCP port is open, and a blocked ICMP doesn't mean the host is down.
- **"Where does TLS sit?"** → Usually L6 (presentation, encryption). Say that it really runs on top of TCP, inside the app, so it doesn't fit OSI exactly.
- **"Security group vs NACL in OSI terms?"** → Both filter at L3/L4 (IP + port). The SG is **stateful** (returns are allowed automatically), the NACL is **stateless** (allow the ephemeral return ports, see [01](01-basics.md)).
- **"Where do Docker containers on the same bridge talk?"** → L2: ARP and frames through the bridge, no NAT. Going to the internet, they cross L3 (routing + MASQUERADE).
- **"Big requests hang, small ones work. Which layer?"** → An **MTU** problem (L2/L3): often an overlay (VXLAN adds 50 bytes) or a VPN, with ICMP "fragmentation needed" blocked.
- **"Is ARP L2 or L3?"** → It works between them: it's carried in L2 frames and its job is to find the MAC for an L3 address. Most people call it L2.

## Practice 🖥️

See each layer on your own machine.

L1 / L2: the interfaces, their state and their MAC addresses (on the Mac: `ifconfig en0`):

```bash
docker run --rm alpine ip link show
```

L2: the ARP table (IP → MAC):

```bash
arp -a
```

L3: routes and the gateway:

```bash
docker run --rm alpine ip route
```

```bash
traceroute -m 5 8.8.8.8
```

L4: who is listening, and a TCP handshake to a port:

```bash
lsof -nP -iTCP -sTCP:LISTEN
```

```bash
nc -zv google.com 443
```

L6 / L7: the TLS handshake, then the HTTP request and response:

```bash
curl -v https://example.com -o /dev/null
```

All layers at once: watch the handshake, the request and the close in one capture (Linux or inside a container with `NET_ADMIN`):

```bash
docker run --rm --cap-add NET_ADMIN nicolaka/netshoot \
  sh -c "tcpdump -ni eth0 -c 12 'tcp port 80' & sleep 1; curl -s http://example.com -o /dev/null; sleep 2"
```
