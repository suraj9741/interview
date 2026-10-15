# 14 · Practice Exercises ✍️

Exercises turn reading into skill. Every set has **solutions in a separate file** in [solutions/](solutions/), so you can't see the answers by accident.

## How to use them

1. Do a set **after** its module's lessons and lab.
2. Write every answer down before checking. For calculations, show the method.
3. Score yourself honestly. Below the target score: re-read the lesson sections you missed, then retry the set **another day**.
4. For troubleshooting, answer the four questions (step, cause, confirming command, fix) out loud: it's how interviews test it.

Difficulty labels: 🟢 beginner · 🟡 intermediate · 🟠 advanced · 🔴 expert.

## Index

| Set | Covers | Difficulty | Time (estimate) | Target | Solutions |
|---|---|---|---|---|---|
| [01 · Level 1 fundamentals](01-level-1-fundamentals.md) | Networks, devices, addresses, performance, OSI/TCP-IP (19 questions) | 🟢 → 🔴 | 60–90 min | 80% | [solutions](solutions/01-level-1-fundamentals-solutions.md) |
| [02 · Level 2 subnetting drills](02-level-2-subnetting-drills.md) 🔥 | Binary, network/broadcast, sizing, VLSM, overlaps, summarisation, IP plans (sets A–E, 43 questions) | 🟢 → 🔴 | about 3 h, repeat until fast | 90%, under 1 min per set B question | [solutions](solutions/02-level-2-subnetting-drills-solutions.md) |
| [03 · Level 3 protocols](03-level-3-protocols.md) | Ethernet, ports, TCP/UDP, DNS, HTTP, TLS, ICMP/MTU, NAT, end-to-end flow (sections A–H) | 🟢 → 🔴 | 2–3 h | 80% | [solutions](solutions/03-level-3-protocols-solutions.md) |
| [04 · Troubleshooting scenarios](04-troubleshooting-scenarios.md) ⭐ | 14 symptom-and-evidence cases: DNS, DHCP, firewalls, listeners, return routes, duplicate IPs, 502s, MTU, asymmetric routing, TLS chains, NAT exhaustion, idle timeouts, long-haul throughput | 🟢 → 🔴 | 5–10 min each | The right step and cause for 12/14 | [solutions](solutions/04-troubleshooting-scenarios-solutions.md) |
| [Lab 3.5 · Troubleshooting challenge](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) | Eight hidden faults in a live network | 🟡 → 🟠 | 2 h | 8/8 with evidence | [solutions](solutions/lab-03.5-troubleshooting-challenge-solutions.md) |

More scenario practice, specific to Docker, Kubernetes and AWS: [interview scenarios N1–N13](../15-interview-preparation/troubleshooting-scenarios-docker-kubernetes-aws.md).

## Checking your subnetting answers with a tool

After you've written your answers on paper, check them with the script from Lab 2.1 (only Python 3 needed):

```bash
python3 ../13-hands-on-labs/files/lab-02.1/subnet_check.py 10.123.45.67/20            # network, broadcast, hosts
python3 ../13-hands-on-labs/files/lab-02.1/subnet_check.py --overlap 10.1.0.0/16 10.1.64.0/18
python3 ../13-hands-on-labs/files/lab-02.1/subnet_check.py --summarise 10.8.0.0/16 10.9.0.0/16
```

(Run from this folder.) `ipcalc` shows the same in binary, if you have it.

## Planned exercise sets (not written yet)

Levels 4–12 are still outlines, so their exercises don't exist yet: switching and routing (VLANs, STP, OSPF, BGP path selection), network services (load balancing, proxies), security (firewall rule review, VPN design), Linux networking, cloud networking design reviews, and Kubernetes networking. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.
