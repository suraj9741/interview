# Level 12 · Expert Architecture and Troubleshooting

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** design networks that survive failures and growth, defend those designs in a review, and lead the investigation of hard, intermittent problems.

**Start here if:** you've finished Levels 1–11, or have several years of production networking experience.

⏱️ **Estimated time when written:** about 20 hours (an estimate), plus ongoing practice.

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 12.1 | Data-centre design | Leaf–spine, layer 3 to the rack, EVPN-VXLAN; why layer 2 domains stay small |
| 12.2 | Multi-region and hybrid cloud | Address plans, transit designs, DNS and failover across regions and on-premises |
| 12.3 | Designing for failure | Failure domains, redundancy that actually fails over, testing it |
| 12.4 | Performance engineering | BDP, congestion control (CUBIC vs BBR), buffers, long-haul transfers |
| 12.5 | Capacity planning | Bandwidth, connection counts, NAT ports, conntrack tables, IP addresses |
| 12.6 | Intermittent problems | Packet loss that comes and goes, microbursts, asymmetric routing, duplicate IPs |
| 12.7 | Incident case studies | Public post-mortems (BGP leaks, DNS outages, certificate expiry) and what they teach |
| 12.8 | Design reviews | How to present and challenge a network design; the questions reviewers ask |

## Related material that already exists

- [Troubleshooting scenarios](../14-practice-exercises/04-troubleshooting-scenarios.md), expert section: NAT exhaustion, idle timeouts, long-haul throughput, asymmetric routing.
- [Level 2 drills](../14-practice-exercises/02-level-2-subnetting-drills.md), E8: a multi-region IP plan.
- [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md): the method under time pressure.

➡️ **Then:** [Interview preparation](../15-interview-preparation/README.md)
