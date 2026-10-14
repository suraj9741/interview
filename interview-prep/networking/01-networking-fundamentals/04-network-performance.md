# 1.4 · Network Performance: Bandwidth, Throughput, Latency, Jitter, Loss

> **Level 1 · Networking fundamentals** · Lesson 4 of 5 · ⏱️ about 60 minutes (estimate)
> ⬅️ [1.3 Addresses, ports and protocols](03-addresses-ports-and-protocols.md) · ➡️ [1.5 The OSI and TCP/IP models](05-osi-and-tcp-ip-models.md)

## What you'll learn

- 🔥 **Bits vs bytes**, and how to convert link speeds (Mbit/s) into download speeds (MB/s) without mistakes.
- The difference between **bandwidth**, **throughput** and **goodput**.
- The four parts of **latency**, and what **RTT** means.
- What **jitter** and **packet loss** are, and who suffers from them.
- The **bandwidth-delay product**, and why a fast link can still be slow.
- How to measure all of these with `ping`, `mtr`, `curl` and `iperf3`.

## Before you start

- [1.3](03-addresses-ports-and-protocols.md): packets and frames.
- Basic arithmetic. A calculator is fine here (subnetting in Level 2 is on paper).

---

## The idea in plain words

Think of the network as a **motorway**:

| Measure | On the motorway | On the network |
|---|---|---|
| **Bandwidth** | How many lanes: the most cars per minute the road **could** carry | The link's maximum rate, e.g. 1 Gbit/s |
| **Throughput** | How many cars **actually** got through per minute | The rate you really achieved, e.g. 940 Mbit/s |
| **Latency** | How long one car takes to drive from A to B | How long one packet takes to arrive, e.g. 20 ms |
| **Jitter** | How much that journey time **varies** from car to car | Variation in latency, e.g. ±5 ms |
| **Packet loss** | Cars that never arrive | Packets dropped on the way, e.g. 1% |

A wide motorway (high bandwidth) can still give a slow trip if it's long (high latency) or blocked by accidents (loss).

## Why it matters

- "The app is slow" is a performance question. You need to know **which** of these numbers is bad before you can fix it.
- Bandwidth problems are fixed by **bigger pipes**. Latency problems are fixed by **moving things closer** (CDNs, regions) or **making fewer round trips**. You can't buy your way out of latency with bandwidth.
- Cloud costs, video calls, database replication across regions and Kubernetes cross-zone traffic all depend on these numbers.

## 🔥 Bits and bytes: get this right first

| Unit | Symbol | Size |
|---|---|---|
| **bit** | lowercase **b** | One 0 or 1 |
| **byte** | uppercase **B** | **8 bits** |

- **Network speeds** are almost always in **bits per second**: Mbit/s, Mbps, Gbps.
- **File sizes and download counters** are almost always in **bytes**: MB, GB.
- So: **divide by 8** to go from a link speed to the most bytes per second you can download.

| Link speed | ÷ 8 = maximum download rate |
|---|---|
| 100 Mbit/s | 12.5 MB/s |
| 1 Gbit/s | 125 MB/s |
| 10 Gbit/s | 1.25 GB/s |

**Worked example:** how long does a 5 GB download take on a 100 Mbit/s link, at best?

1. 5 GB = 5 × 1,000,000,000 bytes × 8 = **40,000,000,000 bits**.
2. 40,000,000,000 ÷ 100,000,000 bit/s = **400 seconds** ≈ 6.7 minutes.

Real downloads take a bit longer because headers and acknowledgements use some of the capacity (see goodput, below).

> **Two more traps:**
> - Networking prefixes are **decimal**: 1 Mbit = 1,000,000 bits. Some tools show sizes in **binary** units: 1 MiB = 1,048,576 bytes. `iperf3` prints transfer in binary "MBytes" and rate in decimal "Mbits/sec". The difference is about 5% at mega, 7% at giga.
> - This was the exact point an interviewer flagged ("bit and byte are very different"). The same 8× confusion breaks subnetting maths too, which is why [2.1](../02-ip-addressing-and-subnetting/01-binary-decimal-and-hex.md) starts with it.

## Bandwidth, throughput and goodput

| Term | Meaning | Example on a 1 Gbit/s link |
|---|---|---|
| **Bandwidth** (capacity) | The maximum rate the link can carry | 1 Gbit/s |
| **Throughput** | The rate actually achieved, including headers | ~990 Mbit/s |
| **Goodput** | The **useful** data rate the application gets, after headers, retransmissions and protocol overhead | ~940 Mbit/s of file data |

Why goodput is lower: every 1500-byte packet carries about 40–60 bytes of IP and TCP headers, the receiver sends acknowledgements, lost packets are sent again, and the slowest link on the path sets the limit.

**Proof (tested in the lab container):** a 5,000,000-byte file over a link limited to **20 Mbit/s**:

```
connect=0.000330s first_byte=0.001749s total=2.099752s size=5000000B speed=2381233B/s
```

- Theory: 5,000,000 × 8 ÷ 20,000,000 = **2.0 s**. Measured: **2.1 s**.
- 2,381,233 bytes/s × 8 = **19.05 Mbit/s** of goodput on a 20 Mbit/s link: about 95%.

## Latency: where the time goes

**Latency** is the time for one piece of data to get from sender to receiver. It has four parts:

| Part | What it is | How big | Depends on |
|---|---|---|---|
| **Propagation delay** | The signal travelling down the cable or through the air | About **5 µs per km** in fibre (light in glass covers ~200,000 km/s) | **Distance** only |
| **Transmission (serialisation) delay** | Pushing all the bits of the packet onto the wire | Packet size ÷ link speed | **Link speed** |
| **Queuing delay** | Waiting in a router's or switch's buffer behind other packets | 0 to hundreds of ms | **Congestion** |
| **Processing delay** | A device reading headers and deciding where to send the packet | Microseconds | Device speed |

**RTT** (round-trip time) = the time to get there **and back**. `ping` measures RTT. Most protocols need several round trips before useful data flows (TCP handshake, TLS handshake), so **RTT multiplies**.

**Worked examples:**

1. **Transmission delay** of one 1500-byte packet:
   - on a 10 Mbit/s link: 1500 × 8 ÷ 10,000,000 = **1.2 ms**;
   - on a 1 Gbit/s link: 1500 × 8 ÷ 1,000,000,000 = **12 µs**.
   Faster links shrink this part, but not propagation.
2. **Propagation delay**, Mumbai to the US east coast. The great-circle distance is roughly 13,000 km **(estimate)**:
   - one way ≥ 13,000 × 5 µs = **65 ms**, so RTT ≥ **130 ms**, from physics alone;
   - real RTTs are noticeably higher, because cables don't follow the shortest path and every router adds a little.
   No amount of bandwidth reduces this. Only moving the server closer does.
3. **Why a "fast" site feels slow from far away:** opening an HTTPS connection needs about 2 round trips (TCP + TLS 1.3) before the first byte of the request. At 200 ms RTT that's 400 ms before the server even sees the request. A CDN edge 10 ms away does the same in 20 ms.

## Jitter

**Jitter** is the **variation** in latency from packet to packet.

- File downloads barely care: TCP smooths it out.
- **Voice and video calls care a lot.** Audio packets must be played at a steady rate. If some arrive late, the app must either wait (adding delay) or skip them (glitches). Apps use a **jitter buffer** to absorb it.
- `ping` shows a rough jitter figure as **`mdev`** (mean deviation) in its summary.

## Packet loss

**Packet loss** = the percentage of packets that never arrive.

| Cause | Example |
|---|---|
| **Congestion** | A router's queue is full, so new packets are dropped |
| Bad links | Weak Wi-Fi, a damaged cable, a faulty transceiver |
| **Policing / rate limits** | A provider or cloud limit drops packets above a rate |
| Firewalls | Rules that drop some traffic (this looks like 100% loss for that traffic) |

Effects:

- **TCP** resends lost data, so files still arrive complete, but **throughput falls sharply**: TCP treats loss as a sign of congestion and slows down ([3.3](../03-core-networking-protocols/03-tcp-in-depth.md)). Even 1% loss can cut a long-distance transfer to a fraction of the link speed.
- **Real-time UDP traffic** (calls, games) doesn't resend; you hear a gap or see a frozen frame.

## The bandwidth-delay product (BDP)

How much data must be **"in flight"** (sent but not yet acknowledged) to keep a link full?

> **BDP = bandwidth × RTT**

**Worked example:** a 100 Mbit/s link with 100 ms RTT.

- 100,000,000 bit/s × 0.1 s = 10,000,000 bits = **1.25 MB** must be in flight.
- If the sender only allows 64 KB in flight before waiting for an acknowledgement, the best it can do is 64 KB per 100 ms ≈ **5.2 Mbit/s**, on a 100 Mbit/s link.

This is why TCP has a **window scaling** option ([3.3](../03-core-networking-protocols/03-tcp-in-depth.md)), and why "the link is fast but the transfer is slow" is common on long-distance links.

## Bufferbloat: when queues add latency

When a link is full, routers **queue** packets instead of dropping them. Big queues keep the link busy but make every packet wait.

**Proof (tested in the lab container):** two machines joined by a link limited to 20 Mbit/s.

Idle link, `ping`:

```
rtt min/avg/max/mdev = 0.033/0.048/0.078/0.015 ms
```

The same `ping` **while a download fills the link**:

```
rtt min/avg/max/mdev = 3.939/4.788/6.024/0.771 ms
```

Latency went up **100×**, and jitter (`mdev`) **50×**, with no packet lost: every ping waited in the queue behind the download. On real home links with big buffers this can reach hundreds of ms, which is why a video call stutters while someone uploads a large file.

## Try it: measure your network

**RTT, loss and jitter** to your router, then to a host on the internet:

```bash
ping -c 10 192.168.29.1
```

```bash
ping -c 10 1.1.1.1
```

Read the last two lines:

```
10 packets transmitted, 10 received, 0% packet loss, time 9012ms
rtt min/avg/max/mdev = 3.1/4.0/7.9/1.3 ms
```

**(illustrative)**: `0% packet loss` = loss; `avg` = typical RTT; `max` and `mdev` = how much it varies (jitter).

**Loss per hop** along the path:

```bash
mtr -r -c 20 1.1.1.1
```

`mtr` combines `traceroute` and `ping` ([3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md)). Only loss that **continues to the last hop** is real; loss at one middle hop alone usually means that router just doesn't bother answering pings.

**Where the time goes in a web request:**

```bash
curl -s -o /dev/null -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s first_byte=%{time_starttransfer}s total=%{time_total}s\n' https://example.com
```

| Field | Time until… |
|---|---|
| `time_namelookup` | DNS answered ([3.4](../03-core-networking-protocols/04-dns.md)) |
| `time_connect` | The TCP handshake finished |
| `time_appconnect` | The TLS handshake finished ([3.6](../03-core-networking-protocols/06-tls-and-certificates.md)) |
| `time_starttransfer` | The first byte of the response arrived (**TTFB**, time to first byte) |
| `time_total` | Everything was downloaded |

Large `dns` = slow DNS. Large `connect` = high RTT. A big gap between `tls` and `first_byte` = a slow **server**, not a slow network.

**Throughput** between two machines you control, with `iperf3`. On the server:

```bash
iperf3 -s
```

On the client:

```bash
iperf3 -c <server-ip> -t 10
```

**Expected output (tested in the lab container),** on a link limited to 10 Mbit/s:

```
[  5]   0.00-4.00   sec  6.00 MBytes  12.6 Mbits/sec    0             sender
[  5]   0.00-4.01   sec  4.50 MBytes  9.42 Mbits/sec                  receiver
```

Trust the **receiver** line: that's what arrived. (The sender line is higher because data still sitting in buffers counts as "sent".) Without the limit, the same virtual link measured **9.11 Gbits/sec**.

> **Optional, not tested here:** on Linux you can **add** latency, jitter and loss to an interface to see their effect, with `tc qdisc add dev eth0 root netem delay 50ms 10ms loss 1%`. The kernel in my test container didn't include the `netem` module, so this command is untested in these notes.

## In the real world

- **Cloud regions and zones:** traffic between availability zones adds about a millisecond **(estimate)** and is billed; across regions it adds tens to hundreds of ms. Chatty services belong in the same zone or region as their database.
- **Instance size sets bandwidth in AWS**: "up to 10 Gigabit" instances can burst, then drop to a lower baseline. A "slow network" on a small instance is often this limit.
- **SLOs** are written in these terms: "p99 latency under 300 ms", "error rate under 0.1%".
- **Video calls** are hurt most by jitter and loss, not bandwidth.

## Common mistakes

| Mistake | Reality |
|---|---|
| "My 100 Mbps plan should download at 100 MB/s." | 100 Mbit/s ÷ 8 = 12.5 MB/s at most. |
| "More bandwidth fixes slowness." | Only if the link is full. If latency or loss is the problem, more bandwidth changes nothing. |
| "Ping is the speed of my connection." | Ping measures **latency**, not bandwidth. |
| "0% loss means the network is fine." | Latency and jitter can still be terrible (bufferbloat). |
| "Loss at hop 5 in mtr means hop 5 is broken." | Only if the loss continues to every later hop. |

## Troubleshooting slowness

| Symptom | Likely cause | Check |
|---|---|---|
| Everything is slow when a big upload or download is running | Queuing (bufferbloat) on the busy link | `ping` while the transfer runs vs when idle |
| Single transfers are slow over a long distance, but several in parallel are fast | Window / BDP limit, or loss | Compare one `iperf3` stream with `iperf3 -P 4` |
| Slow only to one site; `curl` shows big `connect` time | High RTT on that path | `mtr` to that site |
| `curl` shows a fast connect but a slow `first_byte` | The server is slow, not the network | Server logs and metrics |
| Calls stutter but downloads are fine | Jitter or loss | `ping` `mdev`, `mtr` loss |

## Hands-on lab

[Lab 1.2 · Build a tiny network with namespaces](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md), part D: limit a virtual link to 10 Mbit/s and measure it with `iperf3`, then watch latency rise while it's busy.

## Interview angle

- **"Bandwidth vs latency?"** → Bandwidth is how much data per second the link can carry; latency is how long one packet takes to arrive. A satellite link can have high bandwidth and terrible latency.
- **"Why is my transfer between regions slow on a 10 Gbit/s link?"** → High RTT plus a limited TCP window: throughput ≤ window ÷ RTT. Check loss, tune or parallelise, or move the data closer.
- 🔥 **"A 1 Gbps link: how long to copy 100 GB?"** → 100 GB × 8 = 800 Gbit; ÷ 1 Gbit/s = 800 s ≈ 13–14 minutes at best, realistically a bit more.

## Check yourself

1. A provider sells you "200 Mbps". What's the most MB/s you can download?
2. Which part of latency does a faster link reduce? Which part can it never reduce?
3. A call app stutters, yet `ping` shows 0% loss. What else should you look at?
4. Calculate the BDP for a 1 Gbit/s link with 40 ms RTT.
5. In the bufferbloat test above, what caused the ping time to rise from 0.05 ms to about 5 ms?

<details>
<summary><b>Answers</b> (try first)</summary>

1. 200 ÷ 8 = **25 MB/s**, a little less in practice.
2. A faster link reduces **transmission (serialisation) delay**. It never reduces **propagation delay**, which depends only on distance.
3. **Jitter** (`mdev`, and the `max` time) and latency spikes.
4. 1,000,000,000 × 0.04 = 40,000,000 bits = **5 MB** in flight.
5. **Queuing delay**: pings waited in the shaper's queue behind the download's packets.

</details>

## Summary

- **1 byte = 8 bits.** Link speeds are in bits, file sizes in bytes: divide by 8.
- **Bandwidth** = capacity; **throughput** = achieved; **goodput** = useful data achieved.
- **Latency** = propagation + transmission + queuing + processing. **RTT** = there and back. Distance sets a floor no bandwidth can beat.
- **Jitter** hurts real-time traffic; **loss** cuts TCP throughput and causes gaps in calls.
- **BDP = bandwidth × RTT**: how much data must be in flight to fill the pipe.
- Measure with `ping` (RTT, loss, jitter), `mtr` (per hop), `curl -w` (per phase) and `iperf3` (throughput).

## Next

➡️ [1.5 · The OSI and TCP/IP models](05-osi-and-tcp-ip-models.md): the layers that headers, devices and protocols belong to, and how data is wrapped (encapsulated) on the way out and unwrapped on the way in.
