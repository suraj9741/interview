# 3.7 · ICMP, Ping and Traceroute

> **Level 3 · Core networking protocols** · Lesson 7 of 11 · ⏱️ about 75 minutes (estimate)
> ⬅️ [3.6 TLS and certificates](06-tls-and-certificates.md) · ➡️ [3.8 NAT, PAT and port forwarding](08-nat-pat-and-port-forwarding.md)

## What you'll learn

- What **ICMP** is, and the message types you'll actually meet.
- How to read `ping` output, and why **"ping fails" doesn't mean "host down"**.
- How **traceroute** uses the **TTL** to reveal each router, and how to read `*` and odd latencies.
- **MTU** and **Path MTU discovery**, and why blocking all ICMP breaks big transfers.

## Before you start

- [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md): routing, TTL, and the "unreachable" messages you've already met.
- [3.1](01-ethernet-and-switching-basics.md): MTU.

---

## The idea in plain words

IP has no way to report problems by itself. **ICMP** (Internet Control Message Protocol) is the network's **error-report and test channel**: "I couldn't deliver this", "this packet ran out of hops", "this is too big for my link", and "are you there?" / "yes, I'm here".

`ping` and `traceroute` are just clever uses of those messages.

## Why it matters

- `ping` and `traceroute` are the first two tools anyone reaches for. Reading them correctly (and knowing their limits) separates good troubleshooting from guessing.
- Over-zealous firewalls that drop **all** ICMP cause one of the nastiest bugs in networking: connections that open fine but **hang on large transfers**.

---

## How it works

### ICMP messages

ICMP sits **inside IP** (IP protocol number **1**; ICMPv6 is **58**). It has **no ports**: each message has a **type** and a **code**.

| Type | Code | Name | You see it as |
|---|---|---|---|
| 8 / 0 | 0 | **Echo request / echo reply** | `ping` |
| 3 | 0 | Destination unreachable: **net** | `Destination Net Unreachable` (a router has no route) |
| 3 | 1 | Destination unreachable: **host** | `Destination Host Unreachable` (ARP for the last hop failed) |
| 3 | 3 | Destination unreachable: **port** | A closed **UDP** port ([3.2](02-tcp-and-udp.md)); also how traceroute knows it arrived |
| 3 | 4 | **Fragmentation needed and DF set** | `Frag needed … (mtu = 1400)`: the heart of Path MTU discovery |
| 3 | 13 | Communication administratively prohibited | A firewall rejected it |
| 5 | | Redirect | "Use another gateway" (usually ignored or disabled) |
| 11 | 0 | **Time exceeded** in transit | `Time to live exceeded`: what traceroute relies on |

In **IPv6**, ICMPv6 is even more essential: type **2 "Packet Too Big"** replaces "fragmentation needed", and Neighbor Discovery (types 133–137) replaces ARP ([2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md)). Blocking ICMPv6 breaks IPv6.

### Ping

`ping` sends **echo requests** and times the **echo replies**. From [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md) (`h1` → `h2`, two routers apart) **(tested in the lab container)**:

```console
$ ping -c 2 10.0.2.10
PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
64 bytes from 10.0.2.10: icmp_seq=1 ttl=62 time=0.039 ms
64 bytes from 10.0.2.10: icmp_seq=2 ttl=62 time=0.056 ms

--- 10.0.2.10 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1008ms
rtt min/avg/max/mdev = 0.039/0.047/0.056/0.008 ms
```

| Part | Meaning |
|---|---|
| `56(84) bytes` | 56 bytes of data; 84 with the ICMP (8) and IP (20) headers |
| `icmp_seq` | Sequence number. **Gaps** = lost packets; **out of order** = reordering |
| `ttl=62` | The reply's remaining TTL. Linux starts at 64, so the reply crossed **2 routers** (Windows starts at 128, many routers at 255) |
| `time` | Round-trip time |
| `mdev` | Variation in RTT: a rough **jitter** figure ([1.4](../01-networking-fundamentals/04-network-performance.md)) |
| `+2 errors` | ICMP errors came back instead of replies (e.g. unreachable) |

**Ping failing doesn't mean the host is down.** With `h2` dropping echo requests, ping shows 100% loss, while the web server on the same host answers normally **(tested in the lab container)**:

```console
$ ping -c 2 -W 1 10.0.2.10
2 packets transmitted, 0 received, 100% packet loss, time 1014ms
$ curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://10.0.2.10:8080/
HTTP 200
```

Windows Firewall blocks ping by default; **AWS security groups** don't allow ICMP unless you add a rule. And **ping working doesn't mean the service works** either: test the real port (`nc -zv`, `curl`).

### TTL and traceroute

Every router decrements the IP **TTL** by one; a router that brings it to **zero** drops the packet and sends back **ICMP time exceeded**. Ping with a deliberately small TTL **(tested in the lab container)**:

```console
$ ping -c 1 -t 1 10.0.2.10
From 10.0.1.1 icmp_seq=1 Time to live exceeded
$ ping -c 1 -t 2 10.0.2.10
From 10.0.12.2 icmp_seq=1 Time to live exceeded
```

TTL 1 died at the first router, TTL 2 at the second. **Traceroute is exactly this, automated**: send probes with TTL 1, 2, 3 … and list who reports back.

```console
$ traceroute -n -q 1 10.0.2.10
traceroute to 10.0.2.10 (10.0.2.10), 30 hops max, 60 byte packets
 1  10.0.1.1  0.240 ms
 2  10.0.12.2  0.197 ms
 3  10.0.2.10  0.177 ms
```

What actually travelled (Linux `traceroute` sends **UDP** probes to high ports by default) **(tested in the lab container, trimmed)**:

```text
IP (ttl 1, proto UDP (17), length 60)                                  ← probe 1
    10.0.1.1 > 10.0.1.10: ICMP time exceeded in-transit, length 68      ← router 1 answers
IP (ttl 2, proto UDP (17), length 60)                                  ← probe 2
    10.0.12.2 > 10.0.1.10: ICMP time exceeded in-transit, length 68     ← router 2 answers
IP (ttl 3, proto UDP (17), length 60)                                  ← probe 3 reaches the host
    10.0.2.10 > 10.0.1.10: ICMP 10.0.2.10 udp port 33436 unreachable    ← "port unreachable" = arrived
```

The destination answers with **port unreachable** (nothing listens on that high UDP port), which tells traceroute it has arrived. (Linux traceroute also sends later probes in parallel, so the capture shows more probes than hops.)

Probe types:

| Tool / option | Probe | Use when |
|---|---|---|
| `traceroute` (Linux, macOS default) | UDP to high ports | Default |
| `traceroute -I` / Windows `tracert` | ICMP echo | UDP is filtered |
| `traceroute -T -p 443` (Linux, needs root) | TCP SYN to a real port | Firewalls only allow the service port; the best match for "can my app's traffic get there?" |
| `mtr` | Repeated traceroute with loss and latency **per hop** | Intermittent loss |

All three gave the same 3 hops in the lab **(tested in the lab container)**.

### Reading traceroute correctly

- **`*`** = no reply for that probe. With `r2` configured to drop its own time-exceeded messages **(tested in the lab container)**:

  ```text
   1  10.0.1.1  0.025 ms
   2  *
   3  10.0.2.10  0.011 ms
  ```

  The path **works** (hop 3 answers); router 2 just doesn't talk. Stars only in the **middle** are normal. Stars from some hop **to the end** mean traffic stops somewhere after the last answering hop.
- **High latency at one middle hop but not after it** is usually that router answering ICMP slowly (low priority on its control plane), **not** a problem. Only latency that **continues** to the destination is real.
- **The return path can differ** (asymmetric routing): traceroute only shows the forward path.
- **Different addresses on the same hop** across probes = load balancing (ECMP) between parallel paths.
- In **AWS**, VPC routers don't decrement the TTL or appear in traceroute; you see the instances and gateways, not the fabric.

### MTU and Path MTU discovery

Each link has an **MTU** (1500 on Ethernet). When a packet is bigger than the next link's MTU, the router either **fragments** it or, if the **Don't Fragment (DF)** bit is set (TCP sets it on Linux and most systems), **drops** it and sends back **ICMP "fragmentation needed"** with the smaller MTU. The sender then lowers its packet size for that destination: **Path MTU discovery (PMTUD)**.

In the lab, the link between the two routers was set to MTU 1400. A 1500-byte packet with DF set **(tested in the lab container)**:

```console
$ ping -c 1 -M do -s 1472 10.0.2.10        # 1472 data + 8 ICMP + 20 IP = 1500
From 10.0.1.1 icmp_seq=1 Frag needed and DF set (mtu = 1400)
$ ping -c 1 -M do -s 1472 10.0.2.10        # again: the host has now cached the path MTU
ping: local error: message too long, mtu=1400
$ ping -c 1 -M do -s 1372 10.0.2.10        # 1372 + 28 = 1400: fits
1380 bytes from 10.0.2.10: icmp_seq=1 ttl=62 time=0.038 ms
```

`tracepath` finds the path MTU hop by hop **(tested in the lab container)**:

```text
 1?: [LOCALHOST]                      pmtu 1500
 1:  10.0.1.1                                              0.036ms
 2:  10.0.1.1                                              0.005ms pmtu 1400
 2:  10.0.12.2                                             0.013ms
 3:  10.0.2.10                                             0.013ms reached
     Resume: pmtu 1400 hops 3 back 3
```

**The PMTUD black hole.** If a firewall drops that ICMP "fragmentation needed" message, the sender never learns, keeps sending full-size packets, and they vanish. The symptom is distinctive: **the TCP handshake and small requests work, large responses hang**. [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) fault 8 reproduces it exactly (a 200 KB download returns headers, then 0 bytes, then times out) **(tested in the lab container)**. Two fixes, both verified there:

1. **Allow ICMP type 3 code 4** (and ICMPv6 type 2) through firewalls. Never block all ICMP.
2. **Clamp the TCP MSS** on the router so TCP never sends segments too big for the path:

   ```bash
   iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
   ```

Where it bites: **VPNs and tunnels** (extra headers), **VXLAN overlays** in Kubernetes (MTU 1450 inside), **AWS** (instances use MTU 9001 inside a VPC, but 1500 across the internet, VPN and some peering paths).

---

## Try it

**On your Mac:**

```bash
ping -c 4 8.8.8.8
ping -c 2 -D -s 1472 8.8.8.8       # DF set (-D); does a 1500-byte packet get through?
traceroute -n 8.8.8.8              # UDP probes
traceroute -n -I 8.8.8.8           # ICMP probes
```

**On Linux:**

```bash
ping -c 4 8.8.8.8
ping -c 2 -M do -s 1472 8.8.8.8    # DF set (-M do)
traceroute -n 8.8.8.8
sudo traceroute -n -T -p 443 example.com   # TCP SYN probes to port 443
tracepath -n example.com           # path MTU
mtr -rwc 20 8.8.8.8                # per-hop loss and latency (install mtr)
```

## In the real world

- **AWS security groups** block inbound ICMP by default. To ping an instance, allow "ICMP – echo request" (or All ICMP) from your source. AWS also recommends allowing **"Destination Unreachable: fragmentation required"** so PMTUD works between 9001-MTU instances and 1500-MTU paths.
- **Kubernetes:** pinging a **ClusterIP** usually fails (with kube-proxy in iptables mode, the virtual IP only exists as rules for the Service's TCP/UDP ports). Test Services with `curl`/`nc`, not `ping`.
- **Load balancers** don't answer ping on behalf of backends; an ALB answering doesn't mean targets are healthy.

## Common mistakes

| Mistake | Fix |
|---|---|
| "Ping fails, so the server is down" | Test the actual service port; ICMP is often filtered |
| "Ping works, so the app should work" | Ping proves IP reachability only; test the port and the protocol |
| Blocking all ICMP "for security" | Allow at least fragmentation-needed / packet-too-big, and time-exceeded |
| Panicking over one slow or `*` hop in the middle | Only loss/latency that persists to the destination matters |
| Testing MTU with plain `ping` | Set DF (`-M do` on Linux, `-D` on macOS) and the size, or fragmentation hides the problem |

## Troubleshooting

| What you see | Meaning | Next step |
|---|---|---|
| `Destination Host Unreachable` from your own IP | ARP for the next hop failed | [2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md): gateway/host on the link? |
| `Destination Net Unreachable` from a router | That router has no route | Its routing table |
| `Time to live exceeded` from a router (normal ping) | A **routing loop** | `traceroute`: the same addresses repeating |
| 100% loss, no errors | Dropped silently (firewall, ICMP blocked, return path missing) | Test a TCP port; capture on the far end |
| Small requests work, large downloads hang | **MTU / PMTUD black hole** | `ping -M do -s 1472`, `tracepath`, MSS clamping |
| traceroute stars from hop N to the end | Traffic stops after hop N (or ICMP filtered there) | `traceroute -T -p <port>`; check that network's firewall |

## Hands-on lab

- [Lab 2.2 · Routing between two subnets](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md), part C: TTL, traceroute (UDP, ICMP, TCP), a silent hop, and the MTU tests above.
- [Lab 3.5 · Troubleshooting challenge](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md), fault 8: find and fix a PMTUD black hole.

## Interview angle

- ⭐ **"How does traceroute work?"** → Probes with TTL 1, 2, 3…; each router that drops a probe at TTL 0 sends ICMP time exceeded; the destination answers port unreachable (UDP) or echo reply (ICMP) or SYN-ACK (TCP).
- **"Ping fails but the website loads. How?"** → ICMP is filtered; HTTP isn't. Ping is not a service check.
- ⭐ **"Connections open but large transfers hang."** → MTU mismatch with blocked ICMP (PMTUD black hole). Test with DF pings; fix by allowing ICMP frag-needed or clamping MSS.
- **"What's TTL for?"** → Stops packets looping for ever; each router decrements it; traceroute exploits it. Also hints at the OS (64 Linux/macOS, 128 Windows).
- **"Why `*` in traceroute?"** → That hop doesn't send (or rate-limits, or a firewall drops) time-exceeded messages; not necessarily a problem.

## Check yourself

1. A reply shows `ttl=55`, and the server runs Linux. Roughly how many routers are in the return path?
2. Which ICMP message tells traceroute that a probe reached the destination when using UDP probes?
3. What's the largest `-s` value for which `ping -M do` succeeds on a path with MTU 1500?
4. Traceroute shows hop 4 at 180 ms, and hops 5–9 at 25 ms. Is there a problem at hop 4?
5. Why does an SSH session work over a VPN, but `scp` of a big file stalls immediately?

<details>
<summary><b>Answers</b> (try first)</summary>

1. 64 − 55 = **9 routers** (assuming it started at 64).
2. **Destination unreachable, port unreachable** (type 3 code 3).
3. **1472** (1472 + 8 ICMP + 20 IP = 1500).
4. **No.** Hop 4 is slow to *generate* ICMP; traffic through it is fine, since later hops are fast.
5. A likely **PMTUD black hole**: the VPN lowers the path MTU, the ICMP "fragmentation needed" is blocked, and full-size packets of the big transfer are silently dropped. Fix with MSS clamping or allowing the ICMP.

</details>

## Summary

- **ICMP** = IP's error and test messages: echo, unreachable (net/host/port/frag-needed), time exceeded.
- `ping` tests IP reachability and RTT, **not** services; a blocked ping proves nothing.
- `traceroute` = increasing TTLs + ICMP time exceeded. Mid-path `*` and slow hops are usually harmless.
- **PMTUD** needs ICMP frag-needed / packet-too-big. Block it and big transfers hang; fix with ICMP rules or **MSS clamping**.

## Next

➡️ [3.8 · NAT, PAT and port forwarding](08-nat-pat-and-port-forwarding.md): how many private addresses share one public address, and how inbound port forwarding works.
