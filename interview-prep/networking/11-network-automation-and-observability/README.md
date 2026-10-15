# Level 11 · Network Automation and Observability

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** manage networks as code, and see what they're doing: configuration automation, infrastructure as code for cloud networks, and the metrics, flows and packets that tell you what's wrong before users do.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md) and at least one of Levels [8](../08-linux-networking/README.md), [9](../09-cloud-networking/README.md) or [10](../10-container-and-kubernetes-networking/README.md).

⏱️ **Estimated time when written:** about 12 hours (an estimate).

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 11.1 | Infrastructure as code for networks | Define VPCs, subnets, routes and security groups in Terraform; review a network change safely |
| 11.2 | Configuring network devices automatically | Ansible and Python (Netmiko, NAPALM) concepts; idempotent changes; config backups |
| 11.3 | Network APIs | NETCONF/YANG, RESTCONF, gNMI streaming telemetry, at a practical level |
| 11.4 | What to monitor | Interface counters, errors and drops, latency, loss, saturation; SNMP vs streaming telemetry |
| 11.5 | Flow data | NetFlow/IPFIX/sFlow and cloud flow logs: who talked to whom, how much |
| 11.6 | Synthetic monitoring | Probing from the user's side: blackbox exporter, DNS and TLS expiry checks |
| 11.7 | Packet capture at scale | When and how to capture in production, ring buffers, and privacy |

## Planned labs (free)

- Prometheus with the blackbox exporter probing HTTP, DNS and TLS expiry in the lab container.
- A Terraform plan for a VPC, reviewed without applying it (no cloud cost).

## Related material that already exists

- [Network command cheatsheet](../references/network-commands-cheatsheet.md).
- [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md), step 9: checking certificate expiry with `openssl x509 -checkend`, the basis of an expiry alert.

➡️ **Next level:** [Level 12 · Expert architecture and troubleshooting](../12-expert-architecture-and-troubleshooting/README.md)
