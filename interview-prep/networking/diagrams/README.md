# Diagrams

Every diagram in these notes is an editable **draw.io** file (`.drawio.svg`): GitHub shows it as a picture, and draw.io opens it for editing ([app.diagrams.net](https://app.diagrams.net), draw.io desktop, or the VS Code "Draw.io Integration" extension). There are no Mermaid diagrams.

- **Edit a diagram:** open the `.drawio.svg` in draw.io and save. The picture updates with it.
- **Generated diagrams:** most were created by the scripts in [`src/`](src/), one module per part (`l1.py`, `l2.py`, `l3a.py`, `l3b.py`, `labs_a.py`, `labs_b.py`, `guides.py`), using the helper in `tools/drawio_svg.py`. `python3 src/build.py` only creates missing files; `--force` regenerates them and overwrites edits made in draw.io.
- **Older diagrams** keep their original names (`00-` to `08-`) because the Docker notes and `tools/diagrams_networking.py` refer to them.
- **To redraw on a whiteboard in an interview:** [the URL journey](3.10-url-journey.drawio.svg), [the debug ladder](06-debug-ladder.drawio.svg), [the OSI layers](08-osi-layers.drawio.svg) and [what a host does for every packet](2.7-routing-decision.drawio.svg).

Two diagrams in the Docker notes are used here too: [the bridge network](../../docker/diagrams/08-bridge-network.drawio.svg) and [the packet's journey](../../docker/diagrams/08-packet-flow.drawio.svg) (both in [10.1](../10-container-and-kubernetes-networking/01-docker-bridge-networking-inside-out.md)).

## Guides and roadmap

| Diagram | Shows | Used in |
|---|---|---|
| [interview-answer-steps](interview-answer-steps.drawio.svg) | How to answer a networking question: five steps | [Interview prep](../15-interview-preparation/README.md) |
| [interview-prep-plan](interview-prep-plan.drawio.svg) | Interview preparation: a first pass of about 10 hours (estimate) | [Interview prep](../15-interview-preparation/README.md) |
| [labs-map](labs-map.drawio.svg) | The labs in order: do each one right after its lesson | [Lab index](../13-hands-on-labs/README.md) |
| [lesson-layout](lesson-layout.drawio.svg) | A lesson page, top to bottom | [How to study](../00-learning-roadmap/how-to-study.md) |
| [prerequisites-setup](prerequisites-setup.drawio.svg) | What you need, and where each lab runs | [Prerequisites](../00-learning-roadmap/prerequisites.md) |
| [roadmap-levels](roadmap-levels.drawio.svg) | The 12 levels in four stages (an arrow means: finish this level first) | [Roadmap](../00-learning-roadmap/learning-roadmap.md), [Main README](../README.md) |
| [roadmap-paths](roadmap-paths.drawio.svg) | Choose a path: all three start with Levels 1–3 | [Roadmap](../00-learning-roadmap/learning-roadmap.md) |
| [roadmap-reading-order](roadmap-reading-order.drawio.svg) | Read this module in this order: about 30 minutes | [Roadmap index](../00-learning-roadmap/README.md) |
| [study-loop](study-loop.drawio.svg) | The loop for every lesson | [How to study](../00-learning-roadmap/how-to-study.md) |

## Level 1 · Networking fundamentals

| Diagram | Shows | Used in |
|---|---|---|
| [level-1-map](level-1-map.drawio.svg) | Level 1 · Networking fundamentals: 5 lessons, about 6 hours | [Level 1](../01-networking-fundamentals/README.md) |
| [1.1-client-server-p2p](1.1-client-server-p2p.drawio.svg) | Two ways programs talk: client–server and peer-to-peer | [1.1](../01-networking-fundamentals/01-what-is-a-network.md) |
| [1.1-home-network](1.1-home-network.drawio.svg) | Inside one network vs between networks | [1.1](../01-networking-fundamentals/01-what-is-a-network.md) |
| [1.1-lan-wan-internet](1.1-lan-wan-internet.drawio.svg) | LAN, WLAN, WAN and the internet in one small company | [1.1](../01-networking-fundamentals/01-what-is-a-network.md) |
| [1.2-devices-by-layer](1.2-devices-by-layer.drawio.svg) | How deep each device reads: from L1 (signals) up to L7 (the request) | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| [1.2-home-router-box](1.2-home-router-box.drawio.svg) | The "home router" from your provider: seven parts in one box | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| [1.2-switch-learning](1.2-switch-learning.drawio.svg) | How a switch learns MAC addresses, then forwards or floods | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| [1.3-ephemeral-ports](1.3-ephemeral-ports.drawio.svg) | A client connects: an ephemeral source port to the server's listening port | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| [1.3-ip-mac-port](1.3-ip-mac-port.drawio.svg) | Three labels on every packet: MAC, IP and port | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| [1.3-localhost-vs-all](1.3-localhost-vs-all.drawio.svg) | 127.0.0.1 vs 0.0.0.0: the listening address decides who can connect | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| [1.4-bits-and-bytes](1.4-bits-and-bytes.drawio.svg) | Bits and bytes: link speeds are in bits, file sizes in bytes, so divide by 8 | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| [1.4-five-measures](1.4-five-measures.drawio.svg) | Five numbers that describe a link: the motorway picture | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| [1.4-latency-parts](1.4-latency-parts.drawio.svg) | Where latency comes from: four delays, added on every hop | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| [1.5-l4-vs-l7](1.5-l4-vs-l7.drawio.svg) | L4 vs L7 load balancer: what it can read decides what it can do | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| [1.5-osi-vs-tcpip](1.5-osi-vs-tcpip.drawio.svg) | OSI (7 layers, the teaching model) vs TCP/IP (4 layers, what runs) | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |

## Level 2 · IP addressing and subnetting

| Diagram | Shows | Used in |
|---|---|---|
| [level-2-map](level-2-map.drawio.svg) | Level 2 path: an arrow means "this lesson builds on that one" | [Level 2](../02-ip-addressing-and-subnetting/README.md) |
| [2.1-hex-bytes](2.1-hex-bytes.drawio.svg) | Hex: 1 digit = 4 bits (a nibble), 2 digits = 1 byte | [2.1](../02-ip-addressing-and-subnetting/01-binary-decimal-and-hex.md) |
| [2.1-mask-octets](2.1-mask-octets.drawio.svg) | Mask octets fill with 1s from the left · block size = 256 − mask | [2.1](../02-ip-addressing-and-subnetting/01-binary-decimal-and-hex.md) |
| [2.1-octet-place-values](2.1-octet-place-values.drawio.svg) | One octet = 8 bits, worth 128 64 32 16 8 4 2 1 | [2.1](../02-ip-addressing-and-subnetting/01-binary-decimal-and-hex.md) |
| [2.2-address-map](2.2-address-map.drawio.svg) | Every IPv4 address is private, special-purpose or public | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| [2.2-cast-types](2.2-cast-types.drawio.svg) | Unicast, broadcast, multicast, anycast: who receives one packet | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| [2.2-real-addresses](2.2-real-addresses.drawio.svg) | Classify every address in a real setup: only public ones cross the internet | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| [2.3-aws-reserved](2.3-aws-reserved.drawio.svg) | AWS reserves 5 addresses in every subnet: a /24 gives 251, not 254 | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| [2.3-block-size](2.3-block-size.drawio.svg) | By hand: block size = 256 − mask octet; the network is the multiple at or below | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| [2.3-mask-and](2.3-mask-and.drawio.svg) | The mask's 1s mark the network bits: address AND mask = network address | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| [2.4-borrow-bits](2.4-borrow-bits.drawio.svg) | Subnetting = borrowing host bits: each bit doubles the subnets, halves their size | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| [2.4-six-questions](2.4-six-questions.drawio.svg) | Six questions, one tool: block size = 256 − mask octet | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| [2.4-vpc-plan](2.4-vpc-plan.drawio.svg) | Question 6: 10.0.0.0/16 across 3 AZs, laid out in /20 slots, biggest first | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| [2.5-hierarchical-plan](2.5-hierarchical-plan.drawio.svg) | A hierarchical plan summarises itself: company → region → VPC → tier | [2.5](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) |
| [2.5-over-summarising](2.5-over-summarising.drawio.svg) | Summarise only what you own: a lazy /22 black-holes 10.1.3.0/24 | [2.5](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) |
| [2.5-vlsm-and-summary](2.5-vlsm-and-summary.drawio.svg) | VLSM cuts one block unevenly · summarisation announces many blocks as one | [2.5](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) |
| [2.6-address-anatomy](2.6-address-anatomy.drawio.svg) | IPv6: 128 bits = 8 groups of 4 hex digits (16 bits each) | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| [2.6-slaac-ndp](2.6-slaac-ndp.drawio.svg) | On the LAN: NDP (ICMPv6, multicast) replaces ARP; SLAAC builds the address | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| [2.7-hop-by-hop](2.7-hop-by-hop.drawio.svg) | One ping from h1 to h2: what changes on each link | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| [2.7-longest-prefix-match](2.7-longest-prefix-match.drawio.svg) | Longest prefix match: the most specific matching route wins | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| [2.7-routing-decision](2.7-routing-decision.drawio.svg) | What a host does for every packet it sends | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| [2.8-dhcp-relay](2.8-dhcp-relay.drawio.svg) | A DHCP relay: one central server for many subnets | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| [2.8-dora](2.8-dora.drawio.svg) | DHCP DORA: how a client with no address gets one (tested in the lab container) | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| [2.8-lease-timeline](2.8-lease-timeline.drawio.svg) | A lease is borrowed time: renew at T1, rebind at T2, stop at expiry | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |

## Level 3 · Core networking protocols

| Diagram | Shows | Used in |
|---|---|---|
| [level-3-map](level-3-map.drawio.svg) | Level 3 · Core protocols: the order to read the lessons | [Level 3](../03-core-networking-protocols/README.md) |
| [3.1-bridge-flood](3.1-bridge-flood.drawio.svg) | Proof on a Linux bridge: pc1 pings pc2, and pc3 sees only the broadcast | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| [3.1-ethernet-frame](3.1-ethernet-frame.drawio.svg) | An Ethernet frame, field by field (sizes in bytes) | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| [3.1-switch-learning](3.1-switch-learning.drawio.svg) | What a switch does with every frame | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| [3.2-open-closed-filtered](3.2-open-closed-filtered.drawio.svg) | Open, closed or filtered: what the client gets back | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| [3.2-port-ranges](3.2-port-ranges.drawio.svg) | Port numbers: 16 bits, 0 – 65535 (TCP and UDP each have their own) | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| [3.2-tcp-vs-udp](3.2-tcp-vs-udp.drawio.svg) | Same small request, two transports | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| [3.3-tcp-connection](3.3-tcp-connection.drawio.svg) | One HTTP request over TCP: all 12 packets of the tested capture | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| [3.3-tcp-header](3.3-tcp-header.drawio.svg) | The TCP header: 20 bytes, plus up to 40 bytes of options | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| [3.3-tcp-states](3.3-tcp-states.drawio.svg) | TCP connection states (the names ss shows) | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| [3.4-dns-tree](3.4-dns-tree.drawio.svg) | DNS is a delegated tree: each parent publishes NS records (plus glue) for its children | [3.4](../03-core-networking-protocols/04-dns.md) |
| [3.4-ndots-trap](3.4-ndots-trap.drawio.svg) | In a pod (ndots:5), one lookup of google.com sends 4 questions | [3.4](../03-core-networking-protocols/04-dns.md) |
| [3.4-resolver-at-work](3.4-resolver-at-work.drawio.svg) | Lab 3.2: one question from the client, five from the resolver (tested capture) | [3.4](../03-core-networking-protocols/04-dns.md) |
| [3.5-http-anatomy](3.5-http-anatomy.drawio.svg) | A URL, and the plain-text request and response it turns into | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| [3.5-http-versions](3.5-http-versions.drawio.svg) | HTTP versions: how requests share connections (A → A = request A, then its response) | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| [3.5-lb-5xx](3.5-lb-5xx.drawio.svg) | 502, 503, 504: usually generated by the load balancer, not by your app | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| [3.6-cert-chain](3.6-cert-chain.drawio.svg) | Chain of trust: the client checks each signature up to a root it already has | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| [3.6-tls-termination](3.6-tls-termination.drawio.svg) | Where TLS ends: three options at the load balancer | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| [3.6-tls13-handshake](3.6-tls13-handshake.drawio.svg) | The TLS 1.3 handshake: one round trip, then encrypted data | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| [3.7-pmtud](3.7-pmtud.drawio.svg) | Path MTU discovery: a too-big packet with DF set, and the ICMP that fixes it | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| [3.7-reading-traceroute](3.7-reading-traceroute.drawio.svg) | Reading traceroute: what the hops are telling you | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| [3.7-traceroute-ttl](3.7-traceroute-ttl.drawio.svg) | Traceroute: probes with TTL 1, 2, 3 · the router where TTL hits 0 reports back | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| [3.8-aws-nat](3.8-aws-nat.drawio.svg) | AWS: internet gateway (1:1 NAT) vs NAT gateway (outbound PAT) | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| [3.8-snat-pat-flow](3.8-snat-pat-flow.drawio.svg) | PAT (source NAT) in action: what each hop sees, and how the reply finds its way back | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| [3.8-translation-table](3.8-translation-table.drawio.svg) | One public IP, many inside hosts: outbound SNAT/PAT and inbound DNAT | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| [3.9-ports-map](3.9-ports-map.drawio.svg) | Common ports (1): access, infrastructure, email and the web | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| [3.9-ports-platform](3.9-ports-platform.drawio.svg) | Common ports (2): data stores, VPNs and overlays, Kubernetes and monitoring | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| [3.9-ssh-keys-tunnels](3.9-ssh-keys-tunnels.drawio.svg) | SSH: two kinds of keys, and four ways to tunnel | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| [3.10-container-pod-journey](3.10-container-pod-journey.drawio.svg) | The same journey from a Docker container and from a pod in EKS | [3.10](../03-core-networking-protocols/10-packet-flow-end-to-end.md) |
| [3.10-request-layers](3.10-request-layers.drawio.svg) | What wraps the encrypted GET /cart as it leaves the laptop's Wi-Fi card | [3.10](../03-core-networking-protocols/10-packet-flow-end-to-end.md) |
| [3.10-url-journey](3.10-url-journey.drawio.svg) | What happens when you open https://shop.example.com/cart | [3.10](../03-core-networking-protocols/10-packet-flow-end-to-end.md) |
| [3.11-capture-verdicts](3.11-capture-verdicts.drawio.svg) | When you're stuck, capture: sudo tcpdump -i any -nn port 5432 | [3.11](../03-core-networking-protocols/11-troubleshooting-connectivity.md) |
| [3.11-error-to-step](3.11-error-to-step.drawio.svg) | Read the error first: it names the broken step | [3.11](../03-core-networking-protocols/11-troubleshooting-connectivity.md) |

## Labs

| Diagram | Shows | Used in |
|---|---|---|
| [lab-setup-layers](lab-setup-layers.drawio.svg) | Where the labs run: small networks inside one Linux container | [Lab setup](../13-hands-on-labs/00-lab-environment-setup.md) |
| [lab-1.1-home-network](lab-1.1-home-network.drawio.svg) | Your home network, and the step that finds each value | [Lab 1.1](../13-hands-on-labs/lab-01.1-inspect-your-own-network.md) |
| [lab-1.2-switch-flooding](lab-1.2-switch-flooding.drawio.svg) | Part B: pc1 pings pc2 while pc3 listens | [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) |
| [lab-1.2-topology](lab-1.2-topology.drawio.svg) | What you build: a cable (parts A, C, D), then a switch (part B) | [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) |
| [lab-2.1-lab-map](lab-2.1-lab-map.drawio.svg) | Paper first, then check: the three parts of this lab | [Lab 2.1](../13-hands-on-labs/lab-02.1-subnetting-by-hand-then-verify.md) |
| [lab-2.1-local-or-remote](lab-2.1-local-or-remote.drawio.svg) | Part B: local or remote? The kernel decides from 10.20.37.140/26 | [Lab 2.1](../13-hands-on-labs/lab-02.1-subnetting-by-hand-then-verify.md) |
| [lab-2.1-vlsm-summaries](lab-2.1-vlsm-summaries.drawio.svg) | Part C: the VLSM plan and the two summaries | [Lab 2.1](../13-hands-on-labs/lab-02.1-subnetting-by-hand-then-verify.md) |
| [lab-2.2-fix-ladder](lab-2.2-fix-ladder.drawio.svg) | Part B: add one piece at a time; each missing piece fails differently | [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md) |
| [lab-2.2-topology](lab-2.2-topology.drawio.svg) | Two subnets joined by two routers: what each part adds | [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md) |
| [lab-2.2-traceroute-mtu](lab-2.2-traceroute-mtu.drawio.svg) | Part C: what traceroute and a "don't fragment" ping really do | [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md) |
| [lab-2.3-dora](lab-2.3-dora.drawio.svg) | DORA: four messages, one transaction ID (xid), then a release | [Lab 2.3](../13-hands-on-labs/lab-02.3-dhcp-dora-capture.md) |
| [lab-2.3-topology](lab-2.3-topology.drawio.svg) | A DHCP server and a client on one virtual cable | [Lab 2.3](../13-hands-on-labs/lab-02.3-dhcp-dora-capture.md) |
| [lab-3.1-topology](lab-3.1-topology.drawio.svg) | Lab 3.1: a client and a server joined by one veth pair | [Lab 3.1](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md) |
| [lab-3.1-what-comes-back](lab-3.1-what-comes-back.drawio.svg) | What comes back: the six cases in this lab | [Lab 3.1](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md) |
| [lab-3.2-referral-chain](lab-3.2-referral-chain.drawio.svg) | One question, four servers: the resolver follows the referrals | [Lab 3.2](../13-hands-on-labs/lab-03.2-trace-dns-resolution.md) |
| [lab-3.2-topology](lab-3.2-topology.drawio.svg) | Lab 3.2: five namespaces on one bridge, fully offline | [Lab 3.2](../13-hands-on-labs/lab-03.2-trace-dns-resolution.md) |
| [lab-3.3-certificates](lab-3.3-certificates.drawio.svg) | Be your own CA: who makes which key, and what the CA signs | [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md) |
| [lab-3.3-tls-errors](lab-3.3-tls-errors.drawio.svg) | Each TLS failure, as you reproduced it, and what the client prints | [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md) |
| [lab-3.3-topology](lab-3.3-topology.drawio.svg) | Lab 3.3: a TLS client and server, with a hosts file instead of DNS | [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md) |
| [lab-3.4-nat-rewrites](lab-3.4-nat-rewrites.drawio.svg) | What the router rewrites (ports from the tested run) | [Lab 3.4](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md) |
| [lab-3.4-topology](lab-3.4-topology.drawio.svg) | Lab 3.4: a home network in miniature | [Lab 3.4](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md) |
| [lab-3.5-method](lab-3.5-method.drawio.svg) | The 6-step method in this lab: stop at the first step that fails | [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) |
| [lab-3.5-topology](lab-3.5-topology.drawio.svg) | Lab 3.5: the network the script builds (one fault hidden in it) | [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) |

## Exercise solutions

| Diagram | Shows | Used in |
|---|---|---|
| [sol-1-home-network](sol-1-home-network.drawio.svg) | Exercise 19: an example home network (yours will differ) | [Level 1 solutions](../14-practice-exercises/solutions/01-level-1-fundamentals-solutions.md) |

## Older diagrams (kept from the original notes)

| Diagram | Shows | Used in |
|---|---|---|
| [00-building-story](00-building-story.drawio.svg) | Docker networking explained as an apartment building | [Level 10](../10-container-and-kubernetes-networking/README.md) |
| [02-netfilter-chains](02-netfilter-chains.drawio.svg) | The 5 checkpoints a packet passes on a Linux host (netfilter hooks) | [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md), [Interview prep](../15-interview-preparation/README.md) |
| [04-dns-journey](04-dns-journey.drawio.svg) | The journey of a DNS question: who is google.com? | [3.4](../03-core-networking-protocols/04-dns.md), [Interview prep](../15-interview-preparation/README.md) |
| [06-debug-ladder](06-debug-ladder.drawio.svg) | Debug a connection step by step: stop at the first step that fails | [3.11](../03-core-networking-protocols/11-troubleshooting-connectivity.md), [Interview prep](../15-interview-preparation/README.md) |
| [08-osi-encapsulation](08-osi-encapsulation.drawio.svg) | Encapsulation: how curl http://10.0.2.15/health is wrapped before it leaves | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md), [Interview prep](../15-interview-preparation/README.md) |
| [08-osi-layers](08-osi-layers.drawio.svg) | The 7 OSI layers: what each one adds, and what works there | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md), [Interview prep](../15-interview-preparation/README.md) |
