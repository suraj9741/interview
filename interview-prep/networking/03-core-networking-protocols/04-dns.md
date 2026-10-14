# 04 · DNS ⭐

**Computers connect using numbers (IP addresses). Humans remember names.** DNS is the **phonebook** that turns a name into a number. It works like the contacts on your phone: you tap "Mom", and the phone dials the number.

## `nslookup`, line by line (your real output)

`nslookup` = **n**ame **s**erver **lookup**. It asks a DNS server: "what is the IP for this name?"

```
nslookup google.com
Server:		2405:201:1006:e906::c0a8:1d01
Address:	2405:201:1006:e906::c0a8:1d01#53

Non-authoritative answer:
Name:	google.com
Address: 142.250.146.100
Name:	google.com
Address: 142.250.146.113
...
```

| Line | Meaning |
|---|---|
| `Server: 2405:201:…::c0a8:1d01` | **Who you asked:** your home router. `c0a8:1d01` is hex for `192.168.29.1`, the router's IPv4 address. Your Mac has both addresses set as DNS servers **(tested: `scutil --dns`)**. |
| `#53` | **Port 53**, the DNS port |
| `Non-authoritative answer` | The answer is **second-hand**: it came from a cache (the router's or your provider's), not from Google's own DNS server |
| Several `Address:` lines | google.com is thousands of servers. DNS returns a **list**: your Mac uses the first one and tries the next if it fails, which also spreads the load. A minute later the answer was a single, different address (`172.217.160.78`). Google picks addresses near you and changes them. |
| The **order** of the addresses changes between runs | **Round robin:** DNS servers shuffle the list on purpose, so clients (which mostly take the first address) spread across the servers |

**The addresses change over time too.** On 7 Oct the answers were `142.250.146.x`; on 8 Oct they were `192.178.193.x`. Both belong to Google: a reverse lookup of `192.178.193.101` gives `ly-in-f101.1e100.net`, and `1e100.net` is Google's own domain **(tested)**.

**IPv6 question, IPv4 answer:** the server's address is IPv6, but the answers are IPv4. The first is **how your question travelled**; the second is **what you asked for** (an `A` record, the default).

## Authoritative vs non-authoritative

- **Authoritative** = the **owner** of the name answers (for google.com, that's `ns1.google.com`).
- **Non-authoritative** = someone answers **from memory** (a cache). This is normal, and it's what you get almost every time.

**Proof (tested):** ask the owner directly, and the "Non-authoritative answer" line disappears.

```bash
nslookup google.com ns1.google.com
```

## Record types

| Record | Meaning | Example |
|---|---|---|
| **A** | Name → **IPv4** | `google.com → 142.250.146.100` |
| **AAAA** | Name → **IPv6** | `google.com → 2404:6800:4000:100e::65` **(tested)** |
| **CNAME** | Name → **another name** (a nickname) | `www.shop.com → shop.com` |
| **MX** | Where to deliver **email** | `gmail.com → gmail-smtp-in.l.google.com` |
| **NS** | Which servers are **authoritative** for a domain | `google.com → ns1.google.com` |
| **TXT** | Free text: domain verification, SPF for email | `"v=spf1 include:_spf.google.com ~all"` |
| **PTR** | **Reverse:** IP → name | `dig -x 8.8.8.8 +short` → `dns.google.` **(tested)** |
| **Alias** (Route 53 only) | Like a CNAME, but allowed at the **zone apex** (`shop.com` itself), pointing at an ALB, CloudFront, etc. | `shop.com → my-alb-123.us-west-1.elb.amazonaws.com` |

A CNAME **can't** be used at the zone apex. That's why Route 53 has Alias records.

## TTL: how long an answer is remembered

```
dig google.com +noall +answer
google.com.   161   IN   A   172.217.160.78
               │
               └─ TTL: this answer may be cached for 161 more seconds
```

🎯 **"I changed a DNS record, but some users still reach the old server."** → Their resolvers cached the old answer, and it stays until its **TTL** runs out. Before a planned migration, **lower the TTL** (say to 60 seconds) a day ahead.

## The journey of a DNS question

![The journey of a DNS question](diagrams/04-dns-journey.drawio.svg)

1. **Your Mac** checks its own cache.
2. **Your router** checks its cache.
3. **Your provider's resolver** (Jio) does the real work when nobody has it cached:
   - asks the **root servers**: "who handles `.com`?";
   - asks the **`.com` servers**: "who handles google.com?";
   - asks **`ns1.google.com`**, the owner, which gives the authoritative answer.
4. The answer travels back, and **every step caches it** for the TTL.

`dig +trace google.com` shows steps 4–6 for real **(tested)**.

## `/etc/hosts` and the difference between DNS tools

| Tool | Uses `/etc/hosts` and search domains? | Use it to |
|---|---|---|
| `getent hosts db` (Linux) | ✅ Yes, like a real app does | See what **your app** will get |
| `nslookup` / `dig` | ❌ No, they ask a DNS server directly | Test **the DNS server** itself |

So if `dig` works but the app fails (or the other way round), compare with `getent hosts`.

## DNS inside Docker (tested)

| Where the container runs | DNS server in `/etc/resolv.conf` | Finds other containers by name? |
|---|---|---|
| **Default bridge** | `192.168.65.7` on Docker Desktop (the host's DNS servers on Linux) | ❌ No |
| **User-defined network** | **`127.0.0.11`**: Docker's built-in DNS server, which knows container names and forwards everything else | ✅ Yes |

A failed lookup inside a container **(tested)**:

```
** server can't find doesnotexist.invalid: NXDOMAIN
```

## DNS inside Kubernetes ⭐

- **CoreDNS** runs in `kube-system` behind a Service called **`kube-dns`**. Every pod's `/etc/resolv.conf` points at that Service's ClusterIP.
- **Service names:** `<service>.<namespace>.svc.cluster.local` → the ClusterIP. In the same namespace, just `<service>` works, thanks to the **search domains**.
- **A headless Service** (`clusterIP: None`) returns the **pod IPs** instead. StatefulSet pods get stable names: `<pod>.<service>.<namespace>.svc.cluster.local`.

A pod's `/etc/resolv.conf` looks like this:

```
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

### The trailing dot and the `ndots:5` trap ⭐

**What the trailing dot means:** `google.com.` (with a dot at the end) is a **fully qualified domain name (FQDN)**. The final dot stands for the root of the DNS tree, and it tells the resolver: **"this is the complete name, don't add anything."** Without the dot, the resolver may first try adding the **search domains**.

It works like a phone number: `+91 98xxxxxxxx` is complete, while `98xxxxxxxx` may get a prefix added by the phone.

**On your Mac there is no difference.** `nslookup google.com` and `nslookup google.com.` returned the same 6 addresses (only the order changed). Your Mac has **no search domains** (`scutil --dns` shows none), so there is nothing to add.

**In a pod there is a big difference.** `ndots:5` means: "if the name has **fewer than 5 dots**, try every search domain **first**." `google.com` has only 1 dot.

**Proof (tested):** a container with the same `search` and `ndots:5` settings as a pod, recording every DNS question it sent for **one** lookup.

| Without the dot: `google.com` | With the dot: `google.com.` |
|---|---|
| 1 · `google.com.default.svc.cluster.local.` → NXDomain | 1 · `google.com.` → ✅ the answer |
| 2 · `google.com.svc.cluster.local.` → NXDomain | |
| 3 · `google.com.cluster.local.` → NXDomain | |
| 4 · `google.com.` → ✅ the answer | |
| **4 questions, 3 wasted** | **1 question** |

Real apps ask for both IPv4 (A) and IPv6 (AAAA), so the waste doubles, and it happens on **every external call**. At scale this:
- slows down calls to external services;
- overloads CoreDNS;
- on EKS, can hit the VPC resolver's packet limit (below).

**Fixes:**
1. Write external names with a **trailing dot** in config, e.g. `api.stripe.com.`
2. Lower `ndots` for the pod with `dnsConfig`:
   ```yaml
   spec:
     dnsConfig:
       options:
         - name: ndots
           value: "2"
   ```
3. Run **NodeLocal DNSCache**, a DNS cache on every node, so repeated questions never leave the node.

**Try it yourself:**

```bash
docker run --rm --dns 8.8.8.8 --dns-search default.svc.cluster.local --dns-search svc.cluster.local --dns-search cluster.local --dns-option ndots:5 nicolaka/netshoot sh -c 'timeout 5 tcpdump -i eth0 -nn -l udp port 53 2>/dev/null > /tmp/q.txt & sleep 1; getent hosts google.com; sleep 3; grep -oE " A{1,4}\? [^ ]+" /tmp/q.txt'
```

- It lists the questions sent for `google.com`. Change it to `google.com.` and only `google.com.` is asked.
- `--dns 8.8.8.8` is needed on a Mac because Docker Desktop's DNS server (`192.168.65.7`) **never answers** `.cluster.local` questions, so the lookup just hangs **(tested)**. CoreDNS in a real cluster answers NXDomain straight away.
- The list may appear twice: `getent` repeats the lookup. Count one round.

**On EKS:** each network interface can send at most **1024 packets per second** to the VPC DNS resolver. Very chatty clusters can hit this limit and see random DNS failures. NodeLocal DNSCache helps here too.

## DNS on AWS

- **Route 53** is AWS's DNS service, and the **authoritative** owner of your domains:
  - a **public hosted zone** answers the internet;
  - a **private hosted zone** answers only inside the VPCs you attach it to.
- **Inside a VPC**, the resolver is at the **VPC base address + 2** (e.g. `10.0.0.2`), and also at `169.254.169.253`.
  - It needs `enableDnsSupport`.
  - Private hosted zones also need `enableDnsHostnames`.
- **VPC interface endpoints** (e.g. for ECR) rely on **private DNS**, so the normal service name resolves to the endpoint's private IP ([scenario deep dives](../hemant-scenario-deep-dives.md), B10).
- **Route 53 Resolver endpoints** (inbound and outbound) connect VPC DNS with on-premises DNS.

## Common DNS failures

| You see | It means | Check |
|---|---|---|
| `Could not resolve host` / `bad address` | The name didn't resolve | `nslookup`, `/etc/resolv.conf` |
| `NXDOMAIN` | The name **doesn't exist** (typo, wrong namespace, record missing) | Spelling, the FQDN, the record in Route 53 |
| `SERVFAIL` | The DNS server **failed** to get an answer | The resolver is broken or can't reach upstream |
| Timeout on port 53 | DNS packets are dropped | Kubernetes NetworkPolicy blocking egress to kube-dns on **UDP and TCP 53**; a security group or NACL |
| Old IP returned | Caching | The TTL; flush your Mac's cache: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` |

## Interview angle

- ⭐ **"What happens when you type google.com in the browser?"** → The browser/OS cache, then the resolver (router → provider), then root → `.com` → Google's authoritative server. The IP comes back and is cached for the TTL. Then a TCP connection to port 443, TLS, and the HTTP request.
- **"What does 'non-authoritative' mean?"** → The answer came from a cache, not from the domain's own name server.
- ⭐ **"Pods can't resolve anything. How do you debug?"** →
  1. `kubectl exec <pod> -- cat /etc/resolv.conf`
  2. Test from a debug pod: `nslookup kubernetes.default`
  3. Check the CoreDNS pods and logs
  4. Look for a NetworkPolicy that blocks port 53
  - **He'll push: "Only external names fail?"** → CoreDNS can't reach its upstream (the VPC resolver), or the `ndots` search list is slowing things down.
- **"Why can't my containers find each other by name?"** → They're on the **default bridge**, which doesn't use Docker's DNS at `127.0.0.11`. Use a user-defined network (Compose creates one).
- **"CNAME at the zone apex?"** → Not allowed. Use a Route 53 **Alias** record.
- ⭐ **"What's the difference between `google.com` and `google.com.`?"** → The trailing dot makes the name fully qualified, so no search domains are added. On a laptop with no search domains they behave the same. In a pod, `ndots:5` turns `google.com` into 3 wrong lookups before the real one: I measured 4 questions instead of 1.
  - **He'll push: "How do you fix it cluster-wide?"** → NodeLocal DNSCache on every node, plus a lower `ndots` (via `dnsConfig`) for chatty workloads.

## Practice 🖥️ (on your Mac)

```bash
nslookup google.com
```

```bash
nslookup -type=AAAA google.com
```

```bash
nslookup google.com ns1.google.com
```

Run these one after the other: the same addresses, in a different order:

```bash
nslookup google.com
```

```bash
nslookup google.com.
```

Who owns an address (a reverse lookup):

```bash
dig -x 192.178.193.101 +short
```

```bash
dig google.com +noall +answer
```

```bash
dig +trace google.com
```

```bash
scutil --dns | grep nameserver
```

```bash
docker run --rm alpine cat /etc/resolv.conf
```
