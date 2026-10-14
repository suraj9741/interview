# Prerequisites: What You Need Before Level 1

**No networking knowledge is needed.** Level 1 starts from "what is a network?". You do need a little comfort with a computer's terminal, a machine that can run the labs, and about an hour to set it up.

## Skills

| Skill | Needed for | How much | If you don't have it yet |
|---|---|---|---|
| Using a terminal | Every "Try it" section and lab | Open a terminal; run a command; `cd`, `ls`, `cat`, `less`; copy and paste; stop a command with Ctrl+C | Spend an hour with any "Linux command line basics" tutorial first |
| Editing a text file in the terminal | A few labs | Open, change and save a file with `nano` or `vim` (`vim-tiny` is in the lab container) | `nano` is the easiest; its shortcuts are shown at the bottom of the screen |
| `sudo` and root | Linux labs on a VM | Know that `sudo` runs one command as root, and that root can break things | In the lab container you are already root, safely isolated |
| Basic Docker | Lab setup, Lab 10.1, Level 10 | `docker build`, `docker run`, `docker exec`, `docker ps` | The [Docker notes](../../docker/README.md) in this repository |
| Arithmetic | Level 2 | Add, multiply, and know powers of 2 up to 256 (Level 2.1 teaches the rest) | Nothing more: subnetting is practice, not talent |
| Reading English technical docs | References, RFCs | Slowly is fine | The lessons explain every term; the [glossary](../references/glossary.md) has the rest |

**Self-check.** If you can run these three commands and say roughly what each printed, you're ready:

```bash
pwd
```

```bash
ls -l /etc | head -5
```

```bash
docker run --rm alpine echo hello
```

## A machine for the labs

| Option | Works for | Notes |
|---|---|---|
| **A Mac with Docker Desktop** (what these notes were written on) | Every lab | Lab 1.1 runs on macOS itself; the Linux labs run in the lab container; Lab 10.1 looks inside Docker Desktop's VM |
| **A Linux machine or VM** (Ubuntu 24.04 recommended) | Every lab except the macOS parts of Lab 1.1 and Lab 10.1's Docker Desktop details | Install the packages listed in [option B of the setup guide](../13-hands-on-labs/00-lab-environment-setup.md#option-b-any-ubuntu-2404-machine) |
| **Windows** | The Linux labs, through WSL 2 with Docker Desktop or an Ubuntu VM | Not tested with these notes. Use the Linux commands, not the macOS ones |
| **A cloud VM** | The Linux labs | 💸 **Costs money** while it runs (compute, storage, public IPv4). Stop it when you finish. Only needed if you have no other option |

**Hardware (estimate):** any laptop from the last few years that runs Docker Desktop comfortably. The lab container is small; the namespaces it creates use almost no memory.

Set up the lab environment once, before [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md): [00 · Lab environment setup](../13-hands-on-labs/00-lab-environment-setup.md) (about 20 minutes, estimate).

## Tools, by level

You don't need to install everything now. The lab container already has every Linux tool listed here; on a Mac, the built-in tools cover Lab 1.1.

| Level | Tools | Where |
|---|---|---|
| 1 | `ifconfig`, `ipconfig getifaddr`, `route`, `netstat`, `arp`, `scutil --dns`, `lsof`, `ping`, `curl` | macOS built-ins |
| 1–3 | `ip`, `ping`, `tracepath`, `traceroute`, `mtr`, `ss`, `tcpdump`, `tshark`, `curl`, `nc`, `iperf3`, `tc` | Lab container |
| 2 | `python3` (for the subnet checker), `ipcalc` (optional) | Lab container or your Mac |
| 2 | `dnsmasq`, `dhclient` (DHCP lab) | Lab container |
| 3 | `dig`, `nslookup`, `host`, BIND (`named`) | Lab container; `dig`, `nslookup` and `host` also ship with macOS |
| 3 | `openssl`, `faketime` (TLS lab) | Lab container |
| 3, 8 | `iptables`, `nft`, `conntrack` | Lab container |
| 10 | Docker Desktop; later `kind` and `kubectl` (planned labs) | Your Mac |
| 9 | A cloud account and its CLI (planned labs) | 💸 **may cost money**: each lab will say what and how much |

**Optional but recommended:** [Wireshark](https://www.wireshark.org/) on your Mac, to open packet captures (Lab 3.1 saves one as a `.pcap` file; copy it into `/labs` to reach it from your Mac) and see the same packets in a graphical view.

## Accounts and costs

- **Levels 1–8, 10, 11 and the interview module: free.** Everything runs on your machine.
- **Level 9 (cloud networking): may cost money.** Some cloud resources, such as NAT gateways, load balancers and public IPv4 addresses, are billed for every hour they exist, even when idle. Each lab will list what it creates, the expected cost and a cleanup step. Use a personal sandbox account with a budget alert, never a shared or production account.

## Before you start Level 1

- [ ] You can run the three self-check commands above.
- [ ] You've read [how to study](how-to-study.md) (10 minutes).
- [ ] You've picked a [path](learning-roadmap.md#choose-a-path) and blocked study time in your calendar.
- [ ] You have a paper notebook for drills and diagrams.

➡️ **Start:** [Level 1 · Networking fundamentals](../01-networking-fundamentals/README.md)
