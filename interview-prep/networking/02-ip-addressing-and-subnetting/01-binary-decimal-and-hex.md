# 2.1 · Binary, Decimal and Hexadecimal for Networking 🔥

> **Level 2 · IP addressing and subnetting** · Lesson 1 of 8 · ⏱️ about 60 minutes + daily practice (estimate)
> ⬅️ [Level 2 overview](README.md) · ➡️ [2.2 IPv4 addresses and ranges](02-ipv4-addresses-and-ranges.md)

## What you'll learn

- Why computers and networks count in **binary**.
- The difference between a **bit**, an **octet** and a **byte**, for good.
- How to convert **decimal ↔ binary** for numbers 0–255 **on paper, in seconds**.
- The handful of **powers of 2** that do all the work in subnetting.
- How to read **hexadecimal**, enough for MAC addresses and IPv6.

## Before you start

- [1.4](../01-networking-fundamentals/04-network-performance.md#-bits-and-bytes-get-this-right-first): bits vs bytes.
- No calculator. This lesson is about doing it **by hand**, because that's what makes subnetting click (and what interviewers test).

> 🔥 **Why this lesson exists:** the feedback from the 9 Oct interview was "calculation is totally wrong, conceptually totally wrong. Bit and byte are very different. Calculate on pen and paper, not with a website." Every subnetting mistake traces back to the ideas on this page. Spend the time here.

---

## The idea in plain words

We count in **decimal** (base 10) because we have ten fingers: each digit is worth 10× the one to its right (1, 10, 100…).

Computers store everything as **switches that are on or off**. So they count in **binary** (base 2): each digit is a **bit** (**bi**nary digi**t**), 0 or 1, and each one is worth **2×** the one to its right (1, 2, 4, 8…).

An **IP address is just a 32-bit binary number**. `192.168.1.10` is a human-friendly way of writing it. Subnet masks, CIDR prefixes and "which subnet is this address in?" are all questions about **bits**. Once you can see the bits, subnetting is counting.

## Bits, octets and bytes

| Word | Means | Where you see it |
|---|---|---|
| **bit** | One binary digit: 0 or 1 | "a /24 has 8 host **bits**" |
| **octet** | A group of **8 bits** | Each of the 4 numbers in an IPv4 address |
| **byte** | 8 bits (on every system you'll use, a byte *is* an octet) | File sizes; "an IPv4 address is 4 bytes" |
| **nibble** | 4 bits = one hex digit | Hex in IPv6 and MAC addresses |

So:

- **IPv4 address** = 4 octets = **4 bytes = 32 bits**.
- **IPv6 address** = **16 bytes = 128 bits**.
- **MAC address** = **6 bytes = 48 bits**.
- A `/24` means the first **24 bits** (not bytes!) are the network part. 24 bits = 3 octets, so the first 3 numbers are the network.

> **The mistake to never make again:** the `/N` in CIDR counts **bits**. `/24` is 24 bits = 3 octets. `/20` is 20 bits = 2 octets **plus 4 bits** of the third octet. If you treat `/20` as "20 bytes" or as "the first 2 octets", every answer after that is wrong.

## The 8 bit values of an octet

Learn this line by heart. It is the whole of subnetting maths:

| Bit position (left → right) | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th |
|---|---|---|---|---|---|---|---|---|
| **Value** | **128** | **64** | **32** | **16** | **8** | **4** | **2** | **1** |
| Power of 2 | 2⁷ | 2⁶ | 2⁵ | 2⁴ | 2³ | 2² | 2¹ | 2⁰ |

- Each value is **double** the one to its right.
- All 8 bits on: 128+64+32+16+8+4+2+1 = **255**. That's why every octet is between **0 and 255**.

## Binary → decimal: add the values where the bit is 1

**Example:** `10101100`

| Value | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|
| Bit | **1** | 0 | **1** | 0 | **1** | **1** | 0 | 0 |
| Take | 128 | | 32 | | 8 | 4 | | |

128 + 32 + 8 + 4 = **172**.

## Decimal → binary: subtract from the left

Walk along 128, 64, 32 … 1. At each value: **if it fits** into what's left, write **1** and subtract it; if not, write **0**.

**Example:** 168

| Value | Fits into what's left? | Bit | Left |
|---|---|---|---|
| 128 | 168 ≥ 128 ✅ | **1** | 40 |
| 64 | 40 < 64 | 0 | 40 |
| 32 | 40 ≥ 32 ✅ | **1** | 8 |
| 16 | 8 < 16 | 0 | 8 |
| 8 | 8 ≥ 8 ✅ | **1** | 0 |
| 4 | | 0 | 0 |
| 2 | | 0 | 0 |
| 1 | | 0 | 0 |

168 = **`10101000`**.

**Check it with Python (tested in the lab container):**

```bash
python3 -c "print(format(168, '08b'), int('10101100', 2))"
```

```
10101000 172
```

`format(n, '08b')` = "write n in binary, 8 digits, padded with zeros". `int(text, 2)` = "read this text as base 2".

## The numbers you'll see constantly

These come up in every subnet mask. Notice they are all **1s filling from the left**:

| Binary | Decimal | Why it matters |
|---|---|---|
| `00000000` | 0 | |
| `10000000` | 128 | Mask octet for one network bit |
| `11000000` | 192 | 2 bits |
| `11100000` | 224 | 3 bits |
| `11110000` | 240 | 4 bits (a `/20` mask has 240 in the 3rd octet) |
| `11111000` | 248 | 5 bits |
| `11111100` | 252 | 6 bits (a `/30` mask ends in 252) |
| `11111110` | 254 | 7 bits |
| `11111111` | 255 | 8 bits: a whole octet |

**Shortcut:** each one is the previous one **plus half of what was added last**: 128, +64 = 192, +32 = 224, +16 = 240, +8 = 248, +4 = 252, +2 = 254, +1 = 255.

And the other direction, **block sizes**: 256 minus each mask value.

| Mask octet | 128 | 192 | 224 | 240 | 248 | 252 | 254 | 255 |
|---|---|---|---|---|---|---|---|---|
| **256 − mask = block size** | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

You'll use the block size in [2.4](04-subnetting-step-by-step.md): it's the gap between one subnet and the next.

## Powers of 2: how many addresses

With **n** bits you can make **2ⁿ** different combinations. In subnetting, **n = the number of host bits**, so 2ⁿ = how many addresses a subnet has.

| n | 2ⁿ | | n | 2ⁿ |
|---|---|---|---|---|
| 1 | 2 | | 9 | 512 |
| 2 | 4 | | 10 | 1,024 |
| 3 | 8 | | 11 | 2,048 |
| 4 | 16 | | 12 | 4,096 |
| 5 | 32 | | 13 | 8,192 |
| 6 | 64 | | 14 | 16,384 |
| 7 | 128 | | 15 | 32,768 |
| 8 | 256 | | 16 | 65,536 |

Anchor points to memorise: **2⁸ = 256, 2¹⁰ = 1,024, 2¹² = 4,096, 2¹⁶ = 65,536, 2³² ≈ 4.3 billion.** Everything else is a doubling or halving away.

## A whole IP address in binary

`10.0.1.25` is four octets. Convert each one separately and join them:

```bash
python3 -c "import ipaddress; print('.'.join(format(o, '08b') for o in ipaddress.ip_address('10.0.1.25').packed))"
```

**Expected output (tested in the lab container):**

```
00001010.00000000.00000001.00011001
```

10 = 8+2, 0 = nothing, 1 = 1, 25 = 16+8+1. All 32 bits, written out. When you see `/24`, draw a line after the 24th bit (the end of the third octet): to the left is the **network**, to the right the **host**.

## Hexadecimal (base 16)

Writing 128-bit IPv6 addresses or 48-bit MAC addresses in binary would be unreadable. **Hexadecimal** (hex) packs **4 bits into one digit**:

| Decimal | 0–9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|
| **Hex** | 0–9 | **a** | **b** | **c** | **d** | **e** | **f** |
| Binary | `0000`–`1001` | `1010` | `1011` | `1100` | `1101` | `1110` | `1111` |

- **One hex digit = 4 bits** (a nibble). **Two hex digits = 8 bits = one byte.** `ff` = `11111111` = 255.
- A MAC address `d6:15:f1:59:b2:a3` is 6 bytes, each written as 2 hex digits.
- An IPv6 group like `2405` is 4 hex digits = 16 bits.
- `0x` in front of a number means "this is hex": `0xff` = 255.

**Hex → decimal:** each digit is worth 16× the one to its right. `c0` = 12 × 16 + 0 = **192**. `a8` = 10 × 16 + 8 = **168**.

**Worked example from your own network (tested on the Mac, Oct 2026):** your router's IPv6 address ends in `c0a8:1d01`. Split into bytes: `c0` `a8` `1d` `01` = 192, 168, 29, 1 = **192.168.29.1**, the router's IPv4 address. The same 4 bytes, written in hex. Checked with Python (tested in the lab container):

```bash
python3 -c "import ipaddress; print(ipaddress.ip_address('192.168.29.1').packed.hex())"
```

```
c0a81d01
```

## In the real world

- **Subnet masks, CIDR, route tables, security group rules, Kubernetes pod CIDRs**: all are bit patterns written in decimal.
- **Wireshark and `tcpdump -X`** show raw packets in hex.
- **IPv6 and MAC addresses** are always hex.
- **Linux file permissions** (`chmod 755`) use octal, the same idea with 3 bits per digit.

## Common mistakes

| Mistake | Fix |
|---|---|
| Treating `/24` as bytes | `/N` is always **bits**. 8 bits per octet. |
| Writing fewer than 8 bits for an octet (`101` for 5) | Pad to 8: `00000101`. The position of each bit matters. |
| Starting the bit values from the left with 1 | The **leftmost** bit is worth **128**; the rightmost is worth 1. |
| Forgetting that 256 values means 0–255 | 8 bits make 256 combinations, from 0 **to 255**. |
| Mixing up hex `10` and decimal 10 | Hex `10` = 16. Write `0x10` when it could be confused. |

## Practice (do it every day this week, on paper)

Convert, then check with `python3 -c "print(format(N, '08b'))"`:

1. 10, 172, 192, 224, 240, 248, 252, 255
2. 37, 100, 127, 129, 200
3. Binary → decimal: `11100000`, `01111111`, `10000001`, `00110010`
4. Hex → decimal: `ff`, `80`, `0a`, `fe`, `1d`
5. How many addresses do 5, 7, 11 and 14 host bits give?

More drills, with worked solutions: [Level 2 subnetting drills](../14-practice-exercises/02-level-2-subnetting-drills.md), set A.

## Check yourself

1. How many bits are in an IPv4 address? In a byte? In an IPv6 address?
2. Convert 200 to binary.
3. What's the decimal value of `11111000`?
4. A subnet has 6 host bits. How many addresses does it have?
5. What decimal number is the hex byte `a8`?

<details>
<summary><b>Answers</b> (try first)</summary>

1. 32 · 8 · 128.
2. 200 = 128 + 64 + 8 = **`11001000`**.
3. 128+64+32+16+8 = **248**.
4. 2⁶ = **64**.
5. 10 × 16 + 8 = **168**.

</details>

## Summary

- **Bit** = one 0/1. **Octet / byte** = 8 bits. IPv4 = **32 bits**, IPv6 = **128**, MAC = **48**.
- The octet values **128 64 32 16 8 4 2 1** convert anything from 0 to 255.
- Mask octets fill with 1s from the left: **128, 192, 224, 240, 248, 252, 254, 255**. Block size = **256 − mask octet**.
- **n bits → 2ⁿ values.** Anchor on 2⁸ = 256, 2¹⁰ = 1,024, 2¹² = 4,096, 2¹⁶ = 65,536.
- **Hex** = 4 bits per digit, 2 digits per byte.

## Next

➡️ [2.2 · IPv4 addresses and ranges](02-ipv4-addresses-and-ranges.md): what the 32 bits of an IPv4 address mean, the network and host parts, the old address classes, and which ranges are private, public or special.
