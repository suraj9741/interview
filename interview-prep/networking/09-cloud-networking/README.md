# Level 9 · Cloud Networking

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them. Cloud-specific details are **vendor-specific**: the general ideas (subnets, routing, NAT, stateful vs stateless filtering) come from Levels 1–3.

**Goal:** design, build and troubleshoot cloud networks: address plans, public and private subnets, routing to the internet and between networks, filtering, private access to services, DNS, load balancing and hybrid connectivity.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md) and can do the [Level 2 drills](../14-practice-exercises/02-level-2-subnetting-drills.md) set E.

⏱️ **Estimated time when written:** about 20 hours (an estimate).

> 💸 **Cost warning.** Labs in this level will use real cloud accounts. Some resources cost money **every hour they exist**, even when idle: NAT gateways, load balancers, Transit Gateway attachments, VPN connections, and public IPv4 addresses. Each lab will say what it creates, what it may cost, and how to delete everything. Nothing here should be run in a shared or production account.

## Structure

| Folder | Provider | Status |
|---|---|---|
| [aws/](aws/README.md) | Amazon Web Services | planned (main focus, matching the rest of these notes) |
| [azure/](azure/README.md) | Microsoft Azure | planned (shorter: the same ideas, mapped to Azure names) |

## Planned lessons (provider-neutral concepts first, then AWS)

| # | Lesson | You'll be able to… |
|---|---|---|
| 9.1 | Cloud networking concepts | Map VPC/VNet, subnet, route table, gateway and firewall to what you know from Levels 1–3 |
| 9.2 | Designing a VPC | Plan CIDRs for multiple accounts and regions without overlaps; public, private and isolated subnets per AZ |
| 9.3 | Internet access | Internet gateway vs NAT gateway; egress-only gateways for IPv6; NAT costs and limits |
| 9.4 | Filtering | Security groups (stateful) vs network ACLs (stateless), with the ephemeral-port trap |
| 9.5 | Private access to services | Gateway and interface endpoints, PrivateLink |
| 9.6 | Connecting networks | Peering vs Transit Gateway; site-to-site VPN; Direct Connect |
| 9.7 | Cloud DNS | Route 53 public and private zones, the VPC resolver, resolver endpoints for hybrid DNS |
| 9.8 | Cloud load balancers | ALB vs NLB vs GWLB; target types; TLS termination options |
| 9.9 | Observability | VPC flow logs, Reachability Analyzer, Traffic Mirroring |
| 9.10 | Troubleshooting cloud connectivity | A method for "it times out", from route tables to security groups to the OS |

## Planned labs

| Lab | Cost |
|---|---|
| Design-only: a multi-account IP plan on paper (no cloud account) | 💰 free |
| A VPC with public and private subnets, an internet gateway and a NAT gateway | 💸 **may cost money** (NAT gateway hourly + data processing) |
| Break and fix a security group / NACL pair | 💸 small cost if instances are left running |

## Related material that already exists

- [Level 2](../02-ip-addressing-and-subnetting/README.md): AWS's 5 reserved addresses, subnet sizing, VPC IP plans ([2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md)).
- [3.8 · NAT](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md): IGW vs NAT gateway, port exhaustion, idle timeouts.
- [3.10 · Packet flow end to end](../03-core-networking-protocols/10-packet-flow-end-to-end.md#the-same-journey-from-a-kubernetes-pod-in-aws-eks): a pod's request through a VPC.
- [Interview scenarios N10–N13](../15-interview-preparation/troubleshooting-scenarios-docker-kubernetes-aws.md#️-aws): EKS IP exhaustion, timeouts to EC2 and RDS, private subnets without internet.
- [Scenario deep dives](../../hemant-scenario-deep-dives.md) (A2 overlapping CIDRs, A3 node vs pod CIDR) and the VPC diagrams in the [Oct 9 interview review](../../interview-transcript-review-oct-9.md).

➡️ **Next level:** [Level 10 · Container and Kubernetes networking](../10-container-and-kubernetes-networking/README.md)
