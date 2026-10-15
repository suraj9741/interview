# Level 2 Drills · Binary, Subnetting, VLSM and Summarisation 🔥

> Covers [Level 2](../02-ip-addressing-and-subnetting/README.md), lessons 2.1–2.5.
> ⏱️ Set A 20 min · B 40 min · C 30 min · D 40 min · E 45 min (estimates for a first attempt) · Solutions: [solutions/02-level-2-subnetting-drills-solutions.md](solutions/02-level-2-subnetting-drills-solutions.md)
> Difficulty: 🟢 beginner · 🟡 intermediate · 🟠 advanced · 🔴 expert

**How to use this:** pen and paper only. Redraw the block-size chart at the top of the page from memory ([2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md#the-method-block-size)). Time yourself; the interview target is **under a minute** for a set B question. Then check with the solutions, or with the checker from Lab 2.1:

```bash
python3 ../13-hands-on-labs/files/lab-02.1/subnet_check.py 10.4.19.200/22       # run from this folder
```

Repeat the sets you score below 90% on another day. Subnetting is a skill, not knowledge: speed comes from repetition.

---

## Set A · Binary, decimal and hex 🟢

**A1.** Convert to 8-bit binary: `192` · `172` · `10` · `255` · `128` · `224` · `248` · `63`

**A2.** Convert to decimal: `11000000` · `10101000` · `11111100` · `00001111` · `11110000` · `01111111`

**A3.** Convert to hex: `255` · `172` · `16` · `192`. Then to decimal: `0xFE` · `0x80` · `0xA9` · `0x1F`

**A4.** Write `192.168.10.77` in binary, octet by octet.

**A5.** Write each prefix as a dotted-decimal mask: `/20` · `/27` · `/13` · `/30` · `/9`

**A6.** Write each mask as a prefix length: `255.255.248.0` · `255.255.255.252` · `255.224.0.0` · `255.255.255.128` · `255.255.192.0`

**A7.** Which of these is **not** a valid subnet mask, and why? `255.255.240.0` · `255.255.0.255` · `255.254.0.0` · `255.255.255.200`

---

## Set B · Network, broadcast and hosts 🟢🟡

For each address, write: **network address**, **broadcast address**, **first** and **last usable host**, and the number of **usable hosts**.

| # | Address |
|---|---|
| B1 | `192.168.10.77/24` |
| B2 | `10.4.19.200/22` |
| B3 | `172.16.45.14/27` |
| B4 | `192.168.1.130/25` |
| B5 | `10.0.255.255/15` |
| B6 | `172.31.64.1/18` |
| B7 | `192.168.200.63/26` |
| B8 | `10.10.10.10/29` |
| B9 | `100.70.17.250/10` |
| B10 | `198.51.100.97/28` |
| B11 | `10.123.45.67/20` |
| B12 | `172.20.0.4/30` |

**B13.** Two of the twelve addresses above are traps: they **can't** be assigned to a host. Which ones, and why? Which one **looks** like a trap but isn't?

---

## Set C · Sizing and splitting 🟡

**C1.** What's the smallest subnet (the longest prefix) that gives at least: a) 500 hosts · b) 60 hosts · c) 2 hosts · d) 1,000 hosts?

**C2.** The same four needs, but in an **AWS VPC subnet** (AWS reserves 5 addresses in every subnet; allowed sizes are `/16` to `/28`).

**C3.** Split `10.0.0.0/16` into **6** equal subnets, each as large as possible. Give the prefix and list all the subnets you get. How many are spare?

**C4.** How many `/27` subnets fit in a `/24`? In a `/20`? How many `/24`s fit in a `/16`?

**C5.** List every `/24` inside `172.16.0.0/22`.

**C6.** What is the **5th** `/26` subnet of `10.20.0.0/23`? (The first is `10.20.0.0/26`.)

**C7.** What comes **next** after each of these, at the same size? a) `10.0.48.0/20` · b) `192.168.1.224/27` · c) `172.16.252.0/22` · d) `10.255.255.248/29`

**C8.** Is `192.168.4.255` a valid host address in `192.168.4.0/23`? Is `192.168.5.255`?

**C9.** Are these two hosts in the same subnet? a) `10.1.2.3/24` and `10.1.3.4/24` · b) `10.1.2.3/23` and `10.1.3.4/23` · c) `172.16.31.200/20` and `172.16.32.5/20`

**C10.** How many usable addresses do a `/31` and a `/32` have? Give a real use for each.

---

## Set D · VLSM and overlaps 🟠

**D1.** Allocate from `10.50.0.0/24`, **largest first**, with no wasted gaps: Sales **100** hosts, Engineering **50**, HR **25**, Management **10**, and **3** point-to-point router links. List each subnet. What's left over?

**D2.** Allocate from `192.168.8.0/22`: Building A **400** hosts, Building B **200**, Building C **100**, Wi-Fi guests **100**, servers **20**. List each subnet, or, if it can't be done, prove it and say what you'd change.

**D3.** Find **every overlapping pair** in this list:

```text
10.1.0.0/16   10.1.64.0/18   10.2.0.0/16   10.1.255.0/24
172.16.0.0/12   172.31.0.0/16   192.168.0.0/16   192.169.0.0/16
```

**D4.** VPC A is `10.0.0.0/16`. VPC B is `10.0.128.0/20`. Can you peer them? If not, what would you change, and why is changing it later so painful?

**D5.** A developer's **Linux** laptop connects to the office VPN, which adds the route `172.16.0.0/12`. The laptop can reach office servers in `172.20.5.0/24`, but not those in `172.17.5.0/24`, as long as Docker is running (its default bridge is `172.17.0.0/16`). Explain why, using longest prefix match, and give two fixes.

---

## Set E · Summarisation and real-world design 🟠🔴

**E1.** Summarise into **one** route: `10.8.0.0/16` through `10.15.0.0/16` (eight networks).

**E2.** Summarise into one route: `192.168.16.0/24` through `192.168.23.0/24`.

**E3.** Networks `172.16.4.0/24`, `172.16.5.0/24`, `172.16.6.0/24`, `172.16.7.0/24` and `172.16.8.0/24`:
a) What's the **exact** summary (the fewest prefixes covering exactly these)?
b) What's the smallest **single** prefix that covers them all, and what extra space does it include?

**E4.** What's the smallest single prefix that contains both `10.1.1.0/24` and `10.1.6.0/24`?

**E5.** A router has these routes. Where does each packet go?

```text
0.0.0.0/0        → internet gateway
10.0.0.0/8       → VPN
10.20.0.0/16     → peering to VPC B
10.20.30.0/24    → firewall appliance
```

Packets to: a) `10.20.30.40` · b) `10.20.31.1` · c) `10.21.0.1` · d) `11.0.0.1`

**E6.** 🔴 A Kubernetes cluster uses the Service CIDR `10.96.0.0/12` and the Pod CIDR `10.244.0.0/16`, with a `/24` per node. The company VPC is `10.100.0.0/16`.
a) How many addresses does the Service CIDR contain? Which range does it cover?
b) Does anything overlap? What breaks if it does?
c) With a `/24` per node, how many nodes can the Pod CIDR support?

**E7.** 🔴 An AWS VPC gets the IPv6 block `2001:db8:1234:5600::/56`. AWS subnets are `/64`. How many subnets can you make? Write the first two and the last one.

**E8.** 🔴 **Interview design question.** Plan addresses for a company with an on-premises network in `10.0.0.0/12` (keep it), and AWS in **two regions**, each with **four VPCs** (prod, staging, dev, shared services). Requirements: no overlaps anywhere, each region reachable from on-premises with **one summary route**, and room to add more VPCs and a third region. Write your plan as a table, with your reasoning. (There's more than one good answer; the solutions show one.)
