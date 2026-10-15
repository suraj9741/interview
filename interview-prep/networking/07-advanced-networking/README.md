# Level 7 · Advanced Networking

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** understand the techniques large networks use on top of the basics: tunnels and overlays, traffic engineering, quality of service, multicast and IPv6 transition.

**Start here if:** you've finished [Level 4](../04-switching-and-routing/README.md) and [Level 5](../05-network-services-and-infrastructure/README.md).

⏱️ **Estimated time when written:** about 15 hours (an estimate).

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 7.1 | Tunnels | GRE, IP-in-IP, IPsec tunnels; the MTU cost of every encapsulation |
| 7.2 | Overlays: VXLAN and Geneve | How a VTEP works; why Kubernetes and clouds use overlays; EVPN at a high level |
| 7.3 | MPLS and SD-WAN | Label switching and why enterprises replaced private WANs with SD-WAN |
| 7.4 | Quality of service | DSCP marking, queues, policing vs shaping, bufferbloat |
| 7.5 | Multicast | IGMP, multicast routing, and where multicast still matters |
| 7.6 | IPv6 in production | Dual stack, NAT64/DNS64, IPv6-only clusters |
| 7.7 | Anycast and global traffic | Anycast routing, BGP-based failover, global load balancing |

## Planned labs (free, in the lab container)

- A VXLAN overlay between two namespaces on different "hosts", captured and decoded.
- QoS with `tc`: shape a link, mark traffic, and measure the effect on latency.

## Related material that already exists

- [3.7 · ICMP, ping and traceroute](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md): MTU and the PMTUD black hole.
- [2.6 · IPv6 fundamentals](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md).
- [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md), part D: shaping a link with `tc` and bufferbloat.

➡️ **Next level:** [Level 8 · Linux networking](../08-linux-networking/README.md)
