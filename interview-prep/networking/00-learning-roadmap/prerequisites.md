# Prerequisites: What You Need Before Level 1

![Your Mac runs Lab 1.1 with its built-in tools; Docker Desktop's Linux VM holds the lab container, where the Linux labs run in network namespaces; a Linux machine, Windows or a cloud VM are the alternatives; then self-check, set up the lab environment and start Level 1](../diagrams/prerequisites-setup.drawio.svg)

- **No networking knowledge needed:** Level 1 starts from "what is a network?".
- You need a little terminal comfort, a machine that runs the labs, and about an hour to set it up.

## Skills

| Skill | Needed for | How much | If you don't have it yet |
|---|---|---|---|
| Using a terminal | Every "Try it" section and lab | Open a terminal; run a command; `cd`, `ls`, `cat`, `less`; copy and paste; stop a command with Ctrl+C | An hour with any "Linux command line basics" tutorial |
| Editing a text file in the terminal | A few labs | Open, change and save a file with `nano` or `vim` (`vim-tiny` is in the lab container) | `nano` is the easiest; its shortcuts are at the bottom of the screen |
| `sudo` and root | Linux labs on a VM | `sudo` runs one command as root, and root can break things | In the lab container you are already root, safely isolated |
| Basic Docker | Lab setup, Lab 10.1, Level 10 | `docker build`, `docker run`, `docker exec`, `docker ps` | The [Docker notes](../../docker/README.md) in this repository |
| Arithmetic | Level 2 | Add, multiply, know powers of 2 up to 256 (2.1 teaches the rest) | Nothing more: subnetting is practice, not talent |
| Reading English technical docs | References, RFCs | Slowly is fine | Lessons explain every term; the [glossary](../references/glossary.md) has the rest |

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

- **Linux machine or VM:** install the packages in [option B of the setup guide](../13-hands-on-labs/00-lab-environment-setup.md#option-b-any-ubuntu-2404-machine). It misses only the macOS parts of Lab 1.1 and Lab 10.1's Docker Desktop details.
- **Hardware (estimate):** any laptop from the last few years that runs Docker Desktop comfortably.
- Set up the lab environment once, before [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md): [00 · Lab environment setup](../13-hands-on-labs/00-lab-environment-setup.md) (about 20 minutes, estimate).

## Tools, by level

Nothing to install now: the lab container has every Linux tool here, and the Mac's built-ins cover Lab 1.1.

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

**Optional but recommended:** [Wireshark](https://www.wireshark.org/) on your Mac, to see packet captures graphically (Lab 3.1 saves a `.pcap` file; copy it into `/labs` to reach it from your Mac).

## Accounts and costs

- **Levels 1–8, 10, 11 and the interview module: free.** Everything runs on your machine.
- **Level 9 (cloud networking): may cost money.** Some cloud resources (NAT gateways, load balancers, public IPv4 addresses) are billed every hour they exist, even idle. Each lab will list what it creates, the expected cost and a cleanup step. Use a personal sandbox account with a budget alert, never a shared or production account.

## Before you start Level 1

- [ ] You can run the three self-check commands above.
- [ ] You've read [how to study](how-to-study.md) (10 minutes).
- [ ] You've picked a [path](learning-roadmap.md#choose-a-path) and blocked study time in your calendar.
- [ ] You have a paper notebook for drills and diagrams.

➡️ **Start:** [Level 1 · Networking fundamentals](../01-networking-fundamentals/README.md)
