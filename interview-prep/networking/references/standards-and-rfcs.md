# Standards and RFCs

> **Reference.** The documents that define what the lessons describe. You don't need to read them to pass an interview, but quoting the right one ("`/31` links are fine, RFC 3021") shows depth, and when two blog posts disagree, the RFC decides.

RFCs are free at [rfc-editor.org](https://www.rfc-editor.org/) (for example `https://www.rfc-editor.org/rfc/rfc1918`). Many old RFCs have been updated or replaced ("obsoleted"); each RFC's page says so at the top. This list names the **current** document where one replaced another.

**Fundamentals vs vendor details.** Everything here is a vendor-neutral standard. Cloud and product behaviour (AWS reserved addresses, NAT gateway limits, Kubernetes port defaults) comes from vendor documentation, not RFCs; the lessons mark those as vendor-specific.

## Addressing

| Document | Topic | Lesson |
|---|---|---|
| RFC 791 | IPv4 | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| RFC 1918 | Private IPv4 address ranges | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| RFC 6598 | Shared address space `100.64.0.0/10` (CGNAT) | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| RFC 3927 | IPv4 link-local addresses `169.254.0.0/16` | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| RFC 5737 | IPv4 documentation ranges (TEST-NET-1/2/3: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) | used throughout the labs |
| RFC 6890 | Registry of special-purpose IP address blocks | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| RFC 4632 | CIDR | [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) |
| RFC 3021 | `/31` prefixes on point-to-point links | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| RFC 8200 | IPv6 | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| RFC 4291 | IPv6 addressing architecture | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| RFC 4193 | IPv6 unique local addresses (`fc00::/7`) | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| RFC 3849 | IPv6 documentation prefix `2001:db8::/32` | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| RFC 4861, RFC 4862 | IPv6 neighbour discovery, stateless address autoconfiguration (SLAAC) | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |

## Link layer and local network

| Document | Topic | Lesson |
|---|---|---|
| IEEE 802.3 | Ethernet | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| IEEE 802.1Q | VLAN tagging (and bridging, which now includes spanning tree) | [3.1](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) |
| IEEE 802.11 | Wi-Fi | [1.2](../01-networking-fundamentals/02-network-devices.md) |
| IEEE 802.1X | Port-based network access control | Level 6 (planned) |
| RFC 826 | ARP | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md) |
| RFC 2131, RFC 2132 | DHCP, and its options | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |
| RFC 8415 | DHCPv6 | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md) |

## Transport

| Document | Topic | Lesson |
|---|---|---|
| RFC 9293 | TCP (the current specification; replaced RFC 793) | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md), [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| RFC 768 | UDP | [3.2](../03-core-networking-protocols/02-tcp-and-udp.md) |
| RFC 7323 | TCP window scaling and timestamps | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| RFC 2018 | TCP selective acknowledgements (SACK) | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| RFC 5681 | TCP congestion control | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| RFC 6298 | TCP retransmission timer | [3.3](../03-core-networking-protocols/03-tcp-in-depth.md) |
| RFC 9000 | QUIC | [3.5](../03-core-networking-protocols/05-http-and-https.md) |

## ICMP and MTU

| Document | Topic | Lesson |
|---|---|---|
| RFC 792 | ICMP (IPv4) | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| RFC 4443 | ICMPv6 | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| RFC 1191 | Path MTU discovery (IPv4) | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| RFC 8201 | Path MTU discovery (IPv6) | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |
| RFC 4821 | Packetization-layer path MTU discovery (works without ICMP) | [3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md) |

## DNS

| Document | Topic | Lesson |
|---|---|---|
| RFC 1034, RFC 1035 | DNS concepts, and the protocol | [3.4](../03-core-networking-protocols/04-dns.md) |
| RFC 2308 | Negative caching (NXDOMAIN TTLs) | [3.4](../03-core-networking-protocols/04-dns.md) |
| RFC 9156 | QNAME minimisation | [3.4](../03-core-networking-protocols/04-dns.md) |
| RFC 7858, RFC 8484 | DNS over TLS, DNS over HTTPS | [3.4](../03-core-networking-protocols/04-dns.md) |

## HTTP and TLS

| Document | Topic | Lesson |
|---|---|---|
| RFC 9110 | HTTP semantics (methods, status codes, headers) | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| RFC 9112 | HTTP/1.1 | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| RFC 9113 | HTTP/2 | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| RFC 9114 | HTTP/3 | [3.5](../03-core-networking-protocols/05-http-and-https.md) |
| RFC 8446 | TLS 1.3 | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| RFC 5280 | X.509 certificates and revocation lists for the internet | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| RFC 6066 | TLS extensions, including SNI | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| RFC 7301 | ALPN | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |
| CA/Browser Forum Baseline Requirements | Rules public CAs follow, including maximum certificate lifetimes | [3.6](../03-core-networking-protocols/06-tls-and-certificates.md) |

## NAT, tunnels and routing

| Document | Topic | Lesson |
|---|---|---|
| RFC 3022 | Traditional NAT and NAPT (PAT) | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| RFC 4787, RFC 5382 | How NATs should behave for UDP and TCP | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| RFC 6146 | NAT64 | [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) |
| RFC 7348 | VXLAN | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 8926 | Geneve | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 4271 | BGP-4 | Level 4 (planned) |
| RFC 2328 | OSPF version 2 | Level 4 (planned) |

## Everyday protocols

| Document | Topic | Lesson |
|---|---|---|
| RFC 4253 | SSH transport layer | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 5905 | NTP version 4 | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 5424 | Syslog | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 5321 | SMTP | [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) |
| RFC 1122 | Requirements for internet hosts (how a host's stack should behave) | background |
| IANA service name and port number registry | Official port assignments (the source of `/etc/services`) | [common ports](common-ports.md) |
