# Level 6 · Network Security

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** understand how networks are attacked and defended, from layer 2 tricks to DDoS, and design segmentation and firewall rules you can defend in a review.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md).

⏱️ **Estimated time when written:** about 15 hours (an estimate).

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 6.1 | Firewalls | Stateless vs stateful, NGFW, WAF; write and review a rule set; default deny |
| 6.2 | Segmentation and zero trust | Zones, DMZs, micro-segmentation; why "inside the network" isn't trust |
| 6.3 | Layer 2 attacks and defences | ARP spoofing and Dynamic ARP Inspection, rogue DHCP and DHCP snooping, port security, 802.1X |
| 6.4 | Denial of service | SYN floods and SYN cookies, amplification attacks, rate limiting, scrubbing |
| 6.5 | Securing DNS | DNSSEC, cache poisoning, DNS over TLS/HTTPS, DNS as an exfiltration channel |
| 6.6 | TLS in practice | Hardening, certificate lifecycle and automation, mTLS for services |
| 6.7 | Detection | IDS/IPS, flow logs and what an anomaly looks like |
| 6.8 | VPN and remote-access security | Choosing and hardening VPNs; bastions vs session managers |

## Planned labs (free, in the lab container)

- Stateful firewall rules with nftables: build, test and log a default-deny policy.
- ARP spoofing between namespaces, then detect it.
- A SYN flood against a namespace, with and without SYN cookies.

## Related material that already exists

- [3.2 · TCP and UDP](../03-core-networking-protocols/02-tcp-and-udp.md) and [Lab 3.1](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md), part D: DROP vs REJECT.
- [3.6 · TLS and certificates](../03-core-networking-protocols/06-tls-and-certificates.md) and [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md), including mutual TLS.
- [8.6 · Netfilter, NAT and conntrack](../08-linux-networking/06-netfilter-nat-and-conntrack.md): the ufw bypass with Docker.

➡️ **Next level:** [Level 7 · Advanced networking](../07-advanced-networking/README.md)
