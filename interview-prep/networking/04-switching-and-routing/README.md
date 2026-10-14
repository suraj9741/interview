# Level 4 · Switching and Routing

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them. Until then, use the related material listed at the end.

**Goal:** understand how switches build larger layer 2 networks safely (VLANs, trunks, spanning tree, link aggregation), and how routers learn routes dynamically inside an organisation (OSPF) and between organisations (BGP).

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md), especially [3.1 · Ethernet and switching](../03-core-networking-protocols/01-ethernet-and-switching-basics.md) and [2.7 · Routing tables and ARP](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md).

⏱️ **Estimated time when written:** about 20 hours (an estimate).

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 4.1 | VLANs and 802.1Q trunks | Explain access vs trunk ports, the native VLAN, and read a tagged frame |
| 4.2 | Inter-VLAN routing | Compare router-on-a-stick, layer 3 switches (SVIs) and a firewall between VLANs |
| 4.3 | Spanning tree (STP, RSTP) | Explain why loops melt a network, root bridge election, port roles, and PortFast/BPDU guard |
| 4.4 | Link aggregation (LACP) and redundancy | Bond links; explain hashing and why one flow never exceeds one link |
| 4.5 | Static routing in depth | Use floating static routes, discard (null) routes for summaries, and recursive next hops |
| 4.6 | How dynamic routing works | Compare distance-vector and link-state; administrative distance vs metric; convergence |
| 4.7 | OSPF | Areas, neighbours, LSAs at a practical level; troubleshoot a neighbour that won't come up |
| 4.8 | BGP | Autonomous systems, eBGP vs iBGP, path attributes and selection, why BGP outages make the news |
| 4.9 | First-hop redundancy and ECMP | VRRP/HSRP virtual gateways; equal-cost multipath |

## Planned labs (all free, in the lab container)

- VLANs and 802.1Q trunks on a Linux bridge with VLAN filtering.
- OSPF, then BGP, between namespaces with FRRouting (a free routing suite).
- A broken spanning tree: build a loop, watch the broadcast storm, enable STP.

## Related material that already exists

- [2.5 · VLSM and route summarisation](../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md) and [2.7 · Routing tables, longest prefix match, ARP](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md).
- [3.1 · Ethernet and switching basics](../03-core-networking-protocols/01-ethernet-and-switching-basics.md): MAC learning, flooding, broadcast domains, a first look at STP and VLANs.
- [Lab 2.2 · Routing between two subnets](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md): static routes, return paths, a routing loop.

➡️ **Next level:** [Level 5 · Network services and infrastructure](../05-network-services-and-infrastructure/README.md)
