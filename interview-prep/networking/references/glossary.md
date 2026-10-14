# Glossary

> **Reference.** Short, plain definitions, each linked to the lesson that explains it properly. Terms marked *(vendor)* are specific to one company's products; everything else is a general networking term.

Jump to: [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J–K](#jk) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q–R](#qr) · [S](#s) · [T](#t) · [U–V](#uv) · [W–Z](#wz)

## A

| Term | Meaning | Lesson |
|---|---|---|
| **ACK** | TCP flag and number meaning "I've received everything up to here". | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **ALPN** | TLS extension where client and server agree on the application protocol (`h2`, `http/1.1`) during the handshake. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **Anycast** | One IP address announced from many places; routing delivers each packet to the nearest. Used by DNS root servers and CDNs. | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| **APIPA / link-local** | A `169.254.x.x` address a host gives itself when DHCP fails. | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| **ARP** | Address Resolution Protocol: finds the MAC address for an IPv4 address on the local link. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **Authoritative server** | A DNS server that holds a zone's records and answers with the `aa` flag. | [3.4](../03-core-networking-protocols/04-dns.md) |

## B

| Term | Meaning | Lesson |
|---|---|---|
| **Bandwidth** | The maximum rate a link can carry, in bits per second. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **BDP (bandwidth-delay product)** | Bandwidth × RTT: how much data must be in flight to keep a path full. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **BGP** | Border Gateway Protocol: how networks (autonomous systems) exchange routes on the internet and in large private networks. | Level 4 (planned) |
| **Block size** | 256 minus the mask value in the interesting octet: the step between subnets of one size. | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| **Bridge** | A software switch, e.g. Linux `br0` or Docker's `docker0`. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| **Broadcast address** | The last address of an IPv4 subnet (all host bits 1): "everyone on this subnet". | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| **Broadcast domain** | The set of devices that receive each other's broadcasts; a router or VLAN boundary ends it. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |

## C

| Term | Meaning | Lesson |
|---|---|---|
| **CA (certificate authority)** | An organisation (or system) that signs certificates; clients trust a set of root CAs. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **CGNAT** | Carrier-grade NAT: a provider NATs many customers, using `100.64.0.0/10` between them. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **CIDR** | Classless notation `address/prefix-length`, e.g. `10.0.0.0/16`. | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| **CNAME** | A DNS alias pointing one name at another. | [3.4](../03-core-networking-protocols/04-dns.md) |
| **CNI** | Container Network Interface: the plugin that gives Kubernetes pods their network (e.g. AWS VPC CNI, Calico, Cilium). | [Level 10](../10-container-and-kubernetes-networking/README.md) |
| **Collision domain** | Devices sharing one half-duplex medium; every switch port is its own. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| **Congestion window (cwnd)** | How much unacknowledged data the TCP sender allows itself, adjusted to network conditions. | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **conntrack** | Linux's connection-tracking table, which stateful firewalls and NAT depend on. | [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md) |

## D

| Term | Meaning | Lesson |
|---|---|---|
| **Default gateway** | The router a host sends traffic to when the destination isn't on its own subnet. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **Default route** | `0.0.0.0/0` (IPv4) or `::/0` (IPv6): matches everything, used when nothing more specific does. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **DHCP** | Hands out IP address, mask, gateway and DNS servers automatically (Discover, Offer, Request, Ack). | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| **DNAT** | Destination NAT: rewrites the destination address/port, e.g. port forwarding. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **DNS** | The system that turns names into addresses (and more). | [3.4](../03-core-networking-protocols/04-dns.md) |
| **DROP vs REJECT** | Firewall actions: drop silently (client times out) or refuse with an error (client fails at once). | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |

## E

| Term | Meaning | Lesson |
|---|---|---|
| **Encapsulation** | Each layer wraps the data from the layer above in its own header. | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| **Ephemeral port** | A temporary source port the OS picks for an outgoing connection (Linux default 32768–60999). | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **Ethernet** | The standard for wired local networks (IEEE 802.3): frames, MAC addresses. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| **EtherType** | Field in an Ethernet header naming the payload: `0x0800` IPv4, `0x0806` ARP, `0x86DD` IPv6. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |

## F

| Term | Meaning | Lesson |
|---|---|---|
| **FIN** | TCP flag meaning "I've finished sending". | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **Flooding** | A switch sending a frame out of every port because it doesn't know (or can't know) where the destination is. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| **FQDN** | A fully qualified domain name, ending with the root dot: `api.example.com.` | [3.4](../03-core-networking-protocols/04-dns.md) |
| **Frame** | The layer 2 unit (Ethernet header + payload + FCS). | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |

## G

| Term | Meaning | Lesson |
|---|---|---|
| **Geneve** | An overlay encapsulation (UDP 6081), successor to VXLAN in some products. | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| **Glue record** | An address record for a name server, given along with a referral so the resolver can reach it. | [3.4](../03-core-networking-protocols/04-dns.md) |

## H

| Term | Meaning | Lesson |
|---|---|---|
| **Handshake (TCP)** | SYN, SYN-ACK, ACK: how a TCP connection is opened. | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| **Handshake (TLS)** | Agreeing keys and proving the server's identity before encrypted data flows. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **HTTP/2, HTTP/3** | Newer HTTP versions: one multiplexed TCP connection (h2), or QUIC over UDP (h3). | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| **Hub** | An obsolete device that repeats every signal to every port. | [1.2](../01-networking-fundamentals/02-network-devices.md) |

## I

| Term | Meaning | Lesson |
|---|---|---|
| **ICMP** | Internet Control Message Protocol: errors and diagnostics (ping, unreachable, time exceeded). | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **Idempotent** | An HTTP method whose effect is the same whether sent once or several times (GET, PUT, DELETE). | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| **Interface** | A network card, real (`en0`, `eth0`) or virtual (`lo`, `docker0`, `veth…`). | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **IPAM** | IP address management: how addresses are allocated and tracked. | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| **IPsec** | A suite for encrypted IP tunnels (IKE on UDP 500/4500, ESP as IP protocol 50). | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| **IPv4 / IPv6** | Internet Protocol versions: 32-bit and 128-bit addresses. | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md), [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |

## J–K

| Term | Meaning | Lesson |
|---|---|---|
| **Jitter** | Variation in latency between packets; hurts voice and video. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **Jumbo frame** | An Ethernet frame with an MTU above 1500 (commonly 9000; AWS VPC supports 9001 *(vendor)*). | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **Keepalive** | Periodic probes on an idle connection (TCP or HTTP) to keep it, and middlebox state, alive. | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |

## L

| Term | Meaning | Lesson |
|---|---|---|
| **LAN / WAN** | Local area network (one site) / wide area network (connecting sites). | [1.1](../01-networking-fundamentals/01-what-is-a-network.md) |
| **Latency** | The time for data to travel; usually measured as round-trip time. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **Load balancer** | Spreads requests across backends; layer 4 (TCP) or layer 7 (HTTP). | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| **Longest prefix match** | When several routes match, the most specific (longest prefix) wins. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **Loopback** | `127.0.0.1` / `::1`: the host talking to itself. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |

## M

| Term | Meaning | Lesson |
|---|---|---|
| **MAC address** | A 48-bit layer 2 address of a network interface. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **MASQUERADE** | Linux SNAT that uses the outgoing interface's current address. | [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md) |
| **MSS** | Maximum segment size: the largest TCP payload a host wants to receive per segment. | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **mTLS** | Mutual TLS: the client also proves its identity with a certificate. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **MTU** | Maximum transmission unit: the largest packet a link carries (1500 bytes on standard Ethernet). | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **Multicast** | Sending to a group of receivers that joined it (`224.0.0.0/4`). | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |

## N

| Term | Meaning | Lesson |
|---|---|---|
| **NACL** *(vendor)* | AWS network ACL: a **stateless** subnet-level firewall. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **NAT** | Network address translation: rewriting addresses at a boundary. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **NAT gateway** *(vendor)* | AWS managed SNAT for private subnets. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **ndots** | Resolver option: names with fewer dots than this try the search domains first. | [3.4](../03-core-networking-protocols/04-dns.md) |
| **Neighbour (ND / NDP)** | IPv6's replacement for ARP; `ip neigh` shows both. | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| **Network namespace** | A private copy of the Linux network stack; the basis of containers and of these labs. | [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) |
| **Next hop** | The router a packet is sent to next. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **NXDOMAIN** | DNS response: "this name doesn't exist". | [3.4](../03-core-networking-protocols/04-dns.md) |

## O

| Term | Meaning | Lesson |
|---|---|---|
| **OSI model** | A 7-layer reference model for describing networks. | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| **Overlay network** | A virtual network carried inside another (VXLAN, Geneve, IPsec tunnels). | [Level 7](../07-advanced-networking/README.md) |

## P

| Term | Meaning | Lesson |
|---|---|---|
| **Packet** | The layer 3 unit (IP header + payload). | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| **PAT** | Port address translation: many private hosts share one public IP, told apart by port. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **PMTUD** | Path MTU discovery: learning the smallest MTU on a path from ICMP "fragmentation needed" messages. | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **Port** | A 16-bit number identifying an application endpoint on a host. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **Prefix length** | The `/N` in CIDR: how many leading bits are the network part. | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| **Private address** | RFC 1918 ranges (`10/8`, `172.16/12`, `192.168/16`), not routed on the internet. | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| **Propagation delay** | Time for a signal to travel the distance; set by physics, not bandwidth. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **PTR record** | Reverse DNS: address to name. | [3.4](../03-core-networking-protocols/04-dns.md) |

## Q–R

| Term | Meaning | Lesson |
|---|---|---|
| **QUIC** | A transport over UDP with built-in TLS 1.3; carries HTTP/3. | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| **Recursive resolver** | The DNS server that does the lookups on a client's behalf and caches answers. | [3.4](../03-core-networking-protocols/04-dns.md) |
| **Referral** | A DNS answer saying "ask these name servers instead". | [3.4](../03-core-networking-protocols/04-dns.md) |
| **Return path** | The route the reply takes; it must exist, or requests arrive and replies vanish. | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| **Router** | A device that forwards packets between networks by destination IP. | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| **RST** | TCP reset: "this connection doesn't exist / is refused". | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **RTT** | Round-trip time. | [1.4](../01-networking-fundamentals/04-network-performance.md) |

## S

| Term | Meaning | Lesson |
|---|---|---|
| **SAN** | Subject Alternative Name: the list of names a certificate is valid for. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **Security group** *(vendor)* | AWS **stateful** firewall attached to network interfaces. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **Segment** | The layer 4 unit for TCP (datagram for UDP). | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| **Serialisation delay** | Time to put a packet's bits on the wire: size ÷ bandwidth. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **SERVFAIL** | DNS response: "the resolver couldn't get an answer". | [3.4](../03-core-networking-protocols/04-dns.md) |
| **SNAT** | Source NAT: rewrites the source address/port. | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| **SNI** | Server Name Indication: the hostname a TLS client sends in clear text in its ClientHello. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **SOA** | Start of Authority record: zone metadata, including the negative-caching TTL. | [3.4](../03-core-networking-protocols/04-dns.md) |
| **Socket** | An endpoint (IP + port + protocol); a connection is identified by its 5-tuple. | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **Stateful / stateless** | Whether a firewall remembers connections (and lets replies back automatically). | [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) |
| **STP** | Spanning Tree Protocol: prevents layer 2 loops by blocking redundant links. | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md), Level 4 (planned) |
| **Subnet mask** | The dotted-decimal form of the prefix length, e.g. `255.255.255.0` = `/24`. | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| **Summarisation** | Advertising several contiguous networks as one shorter prefix. | [2.5](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) |
| **Switch** | Forwards frames within a LAN using a learned MAC table. | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| **SYN** | TCP flag that opens a connection. | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |

## T

| Term | Meaning | Lesson |
|---|---|---|
| **Throughput** | The data rate actually achieved, always below bandwidth. | [1.4](../01-networking-fundamentals/04-network-performance.md) |
| **TIME_WAIT / CLOSE_WAIT** | TCP states: after closing first (normal, short) / after the peer closed but the app hasn't (often a bug). | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **TLS** | Transport Layer Security: encryption and server authentication for TCP connections. | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| **Traceroute** | Finds the routers on a path by sending probes with increasing TTL. | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **TTL (IP)** | Hop limit, decremented by each router; at 0 the packet is dropped with "time exceeded". | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| **TTL (DNS)** | How long a resolver may cache an answer. | [3.4](../03-core-networking-protocols/04-dns.md) |

## U–V

| Term | Meaning | Lesson |
|---|---|---|
| **UDP** | Connectionless transport: no handshake, no retransmission. | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| **Unicast** | One sender to one receiver. | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| **veth pair** | Two linked virtual interfaces: a "cable" between namespaces. | [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) |
| **VLAN** | A virtual LAN: one switch split into separate broadcast domains (802.1Q tags). | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| **VLSM** | Variable-length subnet masks: subnets of different sizes from one block. | [2.5](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) |
| **VPC** *(vendor term, now generic)* | A private virtual network in a cloud provider. | [Level 9](../09-cloud-networking/README.md) |
| **VPN** | An encrypted tunnel joining networks or a user to a network. | [Level 6](../06-network-security/README.md) |
| **VXLAN** | Ethernet frames carried in UDP (4789 or 8472): the common Kubernetes overlay. | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |

## W–Z

| Term | Meaning | Lesson |
|---|---|---|
| **Wildcard certificate** | Covers one label at one level: `*.example.com` matches `api.example.com`, not `example.com` or `a.b.example.com`. | [Level 3 exercises](../14-practice-exercises/03-level-3-protocols.md), E6 |
| **Window (TCP)** | How much the receiver can accept; scaled by the window-scale option. | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| **Wildcard mask** | The inverse of a subnet mask (`0.0.0.255` for `/24`), used in ACLs and OSPF. | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| **Zone (DNS)** | The part of the DNS tree one set of authoritative servers is responsible for. | [3.4](../03-core-networking-protocols/04-dns.md) |
