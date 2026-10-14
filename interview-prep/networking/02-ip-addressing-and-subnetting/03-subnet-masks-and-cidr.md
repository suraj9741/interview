# 2.3 · Subnet Masks and CIDR ⭐

> **Level 2 · IP addressing and subnetting** · Lesson 3 of 8 · ⏱️ about 75 minutes (estimate)
> ⬅️ [2.2 IPv4 addresses and ranges](02-ipv4-addresses-and-ranges.md) · ➡️ [2.4 Subnetting step by step](04-subnetting-step-by-step.md)

## What you'll learn

- What a **subnet** is and why networks are split into them.
- How a **subnet mask** (`255.255.255.0`) and a **prefix length** (`/24`) say the same thing.
- How a device uses the mask (a bitwise **AND**) to decide "local or remote?".
- How to calculate, **by hand**, the **network address, broadcast address, first and last host, and host count** of any address.
- The special cases: **`/31`, `/32`, `/0`**, and the **5 addresses AWS reserves** in every subnet.
- What **wildcard masks** are, so they don't surprise you in firewall and router configs.

## Before you start

- [2.1](01-binary-decimal-and-hex.md): octet bit values (128…1), mask values (128, 192, 224, 240, 248, 252, 254, 255), powers of 2.
- [2.2](02-ipv4-addresses-and-ranges.md): network part vs host part; network and broadcast addresses.

---

## The idea in plain words

A **subnet** (sub-network) is a slice of an address range that forms **one local network**: devices in it reach each other directly, and reach everything else through a router.

The **mask** is a 32-bit pattern of **1s followed by 0s**:

- the **1s** cover the **network part**;
- the **0s** cover the **host part**.

**CIDR notation** (Classless Inter-Domain Routing) just **counts the 1s**: `/24` = 24 ones = `255.255.255.0`.

```
Address  192.168.10.70   11000000.10101000.00001010.01|000110
Mask     /26             11111111.11111111.11111111.11|000000
                          ←────── 26 network bits ──────→|← 6 host bits →
```

## Why it matters

- Every interface, route table entry, security group rule, VPC, subnet and Kubernetes CIDR is written this way.
- A wrong mask causes the strangest bugs: two machines on the same cable that can't talk, or a machine sending local traffic to the router (or vice versa).
- 🔥 This is the topic interviewers test on paper.

## How it works

### Mask and prefix: two ways to write the same thing

| Prefix | Mask | Mask in binary (last non-zero octet) | Addresses | Usable hosts* | Block size |
|---|---|---|---|---|---|
| `/8` | `255.0.0.0` | `11111111` | 16,777,216 | 16,777,214 | 1 in the 1st octet |
| `/12` | `255.240.0.0` | `11110000` | 1,048,576 | 1,048,574 | 16 in the 2nd octet |
| `/16` | `255.255.0.0` | `11111111` | 65,536 | 65,534 | 1 in the 2nd octet |
| `/19` | `255.255.224.0` | `11100000` | 8,192 | 8,190 | 32 in the 3rd octet |
| `/20` | `255.255.240.0` | `11110000` | 4,096 | 4,094 | 16 in the 3rd octet |
| `/21` | `255.255.248.0` | `11111000` | 2,048 | 2,046 | 8 in the 3rd octet |
| `/22` | `255.255.252.0` | `11111100` | 1,024 | 1,022 | 4 in the 3rd octet |
| `/23` | `255.255.254.0` | `11111110` | 512 | 510 | 2 in the 3rd octet |
| `/24` | `255.255.255.0` | `11111111` | 256 | 254 | 1 in the 3rd octet |
| `/25` | `255.255.255.128` | `10000000` | 128 | 126 | 128 in the 4th octet |
| `/26` | `255.255.255.192` | `11000000` | 64 | 62 | 64 |
| `/27` | `255.255.255.224` | `11100000` | 32 | 30 | 32 |
| `/28` | `255.255.255.240` | `11110000` | 16 | 14 | 16 |
| `/29` | `255.255.255.248` | `11111000` | 8 | 6 | 8 |
| `/30` | `255.255.255.252` | `11111100` | 4 | 2 | 4 |
| `/31` | `255.255.255.254` | `11111110` | 2 | 2 (point-to-point, below) | 2 |
| `/32` | `255.255.255.255` | `11111111` | 1 | 1 (one host) | 1 |

\* Usable = addresses − 2 (network and broadcast), in a normal subnet. AWS uses 5, below.

**Two formulas:**

> **Addresses = 2^(32 − N)** · **Usable hosts = 2^(32 − N) − 2**

`/26`: 32 − 26 = 6 host bits → 2⁶ = 64 addresses → 62 usable.

**Build any mask without the table:** `/N` = N ones. Fill whole octets of 255 first (8 bits each), then the remaining bits make one partial octet from [2.1](01-binary-decimal-and-hex.md#the-numbers-youll-see-constantly), then zeros.

- `/20` = 8 + 8 + **4** → `255.255.` + 4 ones (`11110000` = 240) + `.0` → `255.255.240.0`.
- `/27` = 8 + 8 + 8 + **3** → `255.255.255.` + 3 ones (224) → `255.255.255.224`.

### How a device uses the mask: the AND operation

To find the **network address**, the device does a bitwise **AND** of the address and the mask: each result bit is **1 only if both bits are 1**. Where the mask is 1, the address bit is kept; where the mask is 0, it becomes 0.

**Worked example: `192.168.10.70/26`.** Only the 4th octet is "interesting" (the mask is 255 in the first three, so they're copied as-is):

```
70   = 0 1 0 0 0 1 1 0
192  = 1 1 0 0 0 0 0 0      (the /26 mask's last octet)
AND  = 0 1 0 0 0 0 0 0  = 64
```

Network address = **192.168.10.64**.

**Then "local or remote?"** When the host at `192.168.10.70/26` wants to send to `192.168.10.130`:

1. It ANDs the destination with **its own** mask: 130 AND 192 = `10000010` AND `11000000` = `10000000` = **128** → network `192.168.10.128`.
2. Compare with its own network, `192.168.10.64`. **Different** → the destination is **remote** → send it to the **default gateway** ([2.7](07-default-gateway-routing-table-and-arp.md)).

Even though both addresses start with `192.168.10.`, they're in **different subnets** under `/26`. This is exactly the kind of bug a wrong mask causes.

### Calculating everything about a subnet, by hand

Four answers for any `address/N`. Use the **block size** (256 − the interesting mask octet):

1. **Find the interesting octet**: the one where the mask isn't 255 or 0.
2. **Block size** = 256 − mask value in that octet.
3. **Network address** = the largest **multiple of the block size** ≤ the address's value in that octet. Octets to the right become 0.
4. **Broadcast** = next network − 1. Octets to the right become 255.
5. **First host** = network + 1; **last host** = broadcast − 1.

**Example 1: `192.168.10.70/26`**

| Step | Work | Result |
|---|---|---|
| Interesting octet | /26 → the 4th octet (24 < 26 < 32) | 4th |
| Block size | 256 − 192 | **64** → subnets start at 0, 64, 128, 192 |
| Network | Largest multiple of 64 ≤ 70 | **192.168.10.64** |
| Broadcast | Next network (128) − 1 | **192.168.10.127** |
| Host range | .65 – .126 | **62 hosts** |

**Example 2: `10.0.37.5/20`**

| Step | Work | Result |
|---|---|---|
| Interesting octet | /20 → the 3rd octet (16 < 20 < 24) | 3rd |
| Block size | 256 − 240 | **16** → 0, 16, 32, 48, 64… |
| Network | Largest multiple of 16 ≤ 37 → 32; 4th octet → 0 | **10.0.32.0** |
| Broadcast | Next network is 10.0.48.0, minus 1 → 3rd octet 47, 4th octet 255 | **10.0.47.255** |
| Host range | 10.0.32.1 – 10.0.47.254 | 2¹² − 2 = **4,094 hosts** |

**Check both with `ipcalc` (tested in the lab container, ipcalc 0.51):**

```bash
ipcalc 192.168.10.70/26
```

```
Address:   192.168.10.70        11000000.10101000.00001010.01 000110
Netmask:   255.255.255.192 = 26 11111111.11111111.11111111.11 000000
Wildcard:  0.0.0.63             00000000.00000000.00000000.00 111111
=>
Network:   192.168.10.64/26     11000000.10101000.00001010.01 000000
HostMin:   192.168.10.65        11000000.10101000.00001010.01 000001
HostMax:   192.168.10.126       11000000.10101000.00001010.01 111110
Broadcast: 192.168.10.127       11000000.10101000.00001010.01 111111
Hosts/Net: 62                    Class C, Private Internet
```

`ipcalc` draws the line between network and host bits (the space in the binary column). Ignore "Class C": classes are historical ([2.2](02-ipv4-addresses-and-ranges.md#address-classes-historical-context)).

```bash
ipcalc 10.0.37.5/20
```

```
Network:   10.0.32.0/20         00001010.00000000.0010 0000.00000000
HostMin:   10.0.32.1            00001010.00000000.0010 0000.00000001
HostMax:   10.0.47.254          00001010.00000000.0010 1111.11111110
Broadcast: 10.0.47.255          00001010.00000000.0010 1111.11111111
Hosts/Net: 4094                  Class A, Private Internet
```

(Shortened to the result lines.) No `ipcalc`? Python's standard library does the same:

```bash
python3 -c "import ipaddress as i; n=i.ip_interface('192.168.10.70/26').network; print(n, n.netmask, n.broadcast_address, n.num_addresses)"
```

```
192.168.10.64/26 255.255.255.192 192.168.10.127 64
```

> 🔥 **Do it on paper first, then check.** The tools are for *checking*. In an interview you'll have a whiteboard.

### Special prefix lengths

| Prefix | What it is | Where you see it |
|---|---|---|
| **`/0`** | `0.0.0.0/0`: **every** address | The **default route**; "allow from anywhere" in a security group |
| **`/32`** | Exactly **one** address | A security group rule for one host; a loopback or a load balancer's single IP; routes to one host |
| **`/31`** | **Two** addresses, **both usable**, no network or broadcast address (**RFC 3021**) | **Point-to-point links** between two routers: saves addresses compared with `/30` |
| **`/30`** | 4 addresses, **2 usable** | The traditional point-to-point link (used between the routers in [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md)) |

Python agrees `/31` has two usable hosts **(tested in the lab container)**:

```bash
python3 -c "import ipaddress as i; print(list(i.ip_network('10.0.0.0/31').hosts()))"
```

```
[IPv4Address('10.0.0.0'), IPv4Address('10.0.0.1')]
```

### ⭐ AWS reserves 5 addresses in every subnet

In an AWS VPC subnet, these are not usable by you:

| Address (in `10.0.1.0/24`) | Reserved for |
|---|---|
| `10.0.1.0` | Network address |
| `10.0.1.1` | The **VPC router** |
| `10.0.1.2` | The **DNS resolver** (strictly: the VPC base + 2; AWS reserves +2 in every subnet) |
| `10.0.1.3` | Reserved for future use |
| `10.0.1.255` | Broadcast (the VPC doesn't support broadcast, but the address is reserved) |

| CIDR | Addresses | Usable in AWS | Example |
|---|---|---|---|
| `/28` | 16 | **11** | The **smallest** AWS subnet |
| `/24` | 256 | **251** | A typical subnet: `10.0.1.0/24` |
| `/20` | 4,096 | **4,091** | The default subnet size in a default VPC |
| `/16` | 65,536 | n/a | The **largest** VPC CIDR block (and Docker's default bridge) |

(Azure also reserves 5 addresses per subnet; GCP reserves 4 **(from each provider's documentation)**.)

### Wildcard masks (inverse masks)

Some systems (Cisco ACLs, OSPF configs) use a **wildcard mask**: the mask with the bits **flipped**. 0 = "must match", 1 = "don't care".

> **Wildcard = 255.255.255.255 − mask.** `/26` → mask `255.255.255.192` → wildcard `0.0.0.63`.

`ipcalc` prints it on the `Wildcard:` line above. You'll use these in [Level 4](../04-switching-and-routing/README.md); for now, recognise them.

## Worked example: why the mask must match on both ends

Two servers on the same switch:

| Server | Configured as |
|---|---|
| A | `10.0.1.10/24` |
| B | `10.0.1.200/25` ← a typo: should be `/24` |

- A → B: A computes "`10.0.1.200` is in my `/24`" → **local** → ARP for B directly. ✅ B receives it.
- B → A: B's `/25` network is `10.0.1.128/25` (`.128`–`.255`). `10.0.1.10` is **outside** it → **remote** → B sends the reply to its default gateway. If there's no gateway, or the router doesn't route it back, **the reply is lost**.

Result: A's connections to B hang, and B's logs show requests arriving. A **mismatched mask** looks like a firewall problem. Always check **both** ends' masks.

## In the real world

- **VPC and subnet design** is choosing prefix lengths: a `/16` VPC split into `/24` or `/20` subnets ([2.4](04-subnetting-step-by-step.md)).
- **Security groups and firewall rules** use CIDRs: `10.0.0.0/16` = the whole VPC; `203.0.113.7/32` = one office IP; `0.0.0.0/0` = anyone (dangerous for SSH).
- **Kubernetes:** `--pod-network-cidr=10.244.0.0/16` and a Service CIDR like `10.96.0.0/12` are prefix choices, and must not overlap the node network.
- **EKS IP exhaustion:** with the VPC CNI, every pod takes an IP from the subnet. A `/24` subnet (251 usable) runs out fast; that's why bigger subnets, prefix delegation or a secondary CIDR are used ([scenario deep dives](../../hemant-scenario-deep-dives.md), A3).

## Common mistakes

| Mistake | Reality |
|---|---|
| "`/24` means the 24th address." | It's the number of **network bits**. |
| Using 2^(host bits) as usable hosts | Subtract 2 (network, broadcast); on AWS subtract 5. |
| Bigger prefix = bigger network | **Opposite.** `/16` (65,536) is far bigger than `/28` (16). A bigger number means **fewer** host bits. |
| Choosing a network address that isn't on a block boundary, e.g. `10.0.5.0/22` | A `/22` must start at a multiple of 4 in the 3rd octet: `10.0.4.0/22`. Tools reject the wrong one **(tested in the lab container)**: `ip route add 10.0.5.0/22 …` → `Error: Invalid prefix for given prefix length.`; Python → `ValueError: 10.0.5.0/22 has host bits set`. |
| Assuming addresses that "look similar" are in the same subnet | `192.168.10.70` and `192.168.10.130` are in **different** `/26`s. Do the AND. |

## Troubleshooting

| Symptom | Mask-related cause | Check |
|---|---|---|
| Two hosts on the same switch can't talk | One has the wrong mask (or they're in different subnets) | `ip -br addr` on both; compute both network addresses |
| Replies go to the router instead of straight back | A mask mismatch, as in the worked example | `ip route get <peer IP>` on each side: `via` means "through a router" |
| A route, VPC or subnet CIDR is rejected as invalid | Not aligned to the block size (host bits set) | Use the correct network address (`10.0.4.0/22`, not `10.0.5.0/22`) |
| A new subnet can't be created in a VPC | It **overlaps** an existing subnet, or is outside the VPC CIDR | List subnets and compare ranges ([2.4](04-subnetting-step-by-step.md)) |

## Hands-on lab

[Lab 2.1 · Subnetting by hand, then verify](../13-hands-on-labs/lab-02.1-subnetting-by-hand-then-verify.md): calculate 10 subnets on paper, then check yourself with `ipcalc` and Python, and see the "local or remote" decision live with `ip route get`.

## Interview angle

- 🔥 **"How many usable IPs in a `/24` subnet on AWS?"** → 251: 256 minus 5 reserved.
- 🔥 **"What range does `10.0.16.0/20` cover?"** → Block size 16 in the 3rd octet → `10.0.16.0`–`10.0.31.255`, 4,096 addresses.
- **"Mask for `/27`?"** → `255.255.255.224`, 32 addresses, 30 usable.
- **"What's a `/31` for?"** → Point-to-point links: two usable addresses, no broadcast (RFC 3021).
- **"How does a host know if a destination is local?"** → It ANDs the destination with its own mask and compares the result with its own network address.

## Check yourself

1. Write the mask for `/22` and `/29`.
2. `172.16.45.200/21`: network, broadcast, first and last host, usable count.
3. Are `10.1.1.5/23` and `10.1.0.200/23` in the same subnet?
4. How many usable addresses does a `/26` have in AWS?
5. What's the wildcard mask for `/20`?

<details>
<summary><b>Answers</b> (try first)</summary>

1. `/22` = `255.255.252.0`; `/29` = `255.255.255.248`.
2. Block size 8 in the 3rd octet → multiples of 8 ≤ 45 → **40**. Network `172.16.40.0`, broadcast `172.16.47.255`, hosts `172.16.40.1`–`172.16.47.254`, **2,046** usable.
3. **Yes.** `/23` → block size 2 in the 3rd octet → `10.1.0.0`–`10.1.1.255` contains both.
4. 64 − 5 = **59**.
5. `255.255.255.255 − 255.255.240.0` = **`0.0.15.255`**.

</details>

## Summary

- **Mask** = 1s for network bits, 0s for host bits. **`/N`** counts the 1s.
- **Addresses = 2^(32−N)**; usable = −2 normally, **−5 in AWS**.
- Network address = address **AND** mask. By hand: **block size = 256 − interesting mask octet**; network = the multiple of the block size at or below the address.
- Broadcast = next network − 1. Hosts = everything in between.
- `/32` = one host, `/31` = point-to-point, `/0` = everything.
- **A mask mismatch** between two hosts breaks one direction of traffic.

## Next

➡️ [2.4 · Subnetting step by step](04-subnetting-step-by-step.md): splitting a network into many subnets, sizing subnets for a number of hosts, and planning a real VPC without overlaps.
