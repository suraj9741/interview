# 05 · Hands-On Lab: See It With Your Own Eyes 🖥️

**About 20 minutes.** Every command and output here was tested on this Mac (Docker Desktop 29.6.2). Your interface numbers and IPs may differ: use yours.

## Setup: 2 terminal windows

| Terminal | What it is |
|---|---|
| **💻 Mac** | Your normal terminal |
| **🏢 Building** | A special shell **inside Docker Desktop's hidden Linux VM**, where the bridge, doors and NAT rules live |

**Why the Building terminal?** On a Mac, Docker runs in a hidden Linux VM. This special container lets you look inside it:
- `--network=host` means it sees the VM's network;
- `--privileged` means it's allowed to read the NAT rules.

Use it **only to look**. On a Linux server (EC2) you don't need it: run the 🏢 commands directly, with `sudo` for `iptables`.

### Step 0 · 💻 Mac: start two "flats"

Remove any old copies first (if they don't exist, you'll just see an error):

```bash
docker rm -f flat-a flat-b
```

Flat A, **with** an instruction at reception (`-p`):

```bash
docker run -d --name flat-a -p 8080:80 nginx:alpine
```

Flat B, **without** `-p`:

```bash
docker run -d --name flat-b nginx:alpine
```

### Step 0 · 🏢 Building: open the shell

```bash
docker run -it --rm --network=host --privileged alpine sh
```

Inside it, install the tools once:

```
apk add iptables iproute2
```

From here on, a 🏢 block means **type it in the Building terminal**.

---

## Test 1 · Bridge = the corridor

🏢 See the corridor:

```
ip addr show docker0
```
```
16: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> ... state UP
    inet 172.17.0.1/16
```

🏢 See what's plugged into it:

```
ip link show master docker0
```
```
17: veth14a2cac@if11: ... master docker0
18: veth35e954d@if11: ... master docker0
```

👉 **2 lines = 2 doors**, one for each flat.

💻 Flat B talks to flat A **through the corridor** (no NAT):

```bash
docker exec flat-b wget -qO- http://172.17.0.2 | grep title
```
```
<title>Welcome to nginx!</title>
```

💻 By **name** on the default bridge:

```bash
docker exec flat-b wget -qO- http://flat-a
```
```
wget: bad address 'flat-a'
```

👉 The default bridge has **no name lookup**.

## Test 2 · veth pair = one door, two sides

💻 The inside side:

```bash
docker exec flat-a ip addr show eth0
```
```
11: eth0@if17: ...
    inet 172.17.0.2/16
```

💻 The number of the other side:

```bash
docker exec flat-a cat /sys/class/net/eth0/iflink
```
```
17
```

🏢 The outside side (use **your** number):

```
ip link | grep "^17:"
```
```
17: veth14a2cac@if11: ... master docker0
```

👉 #11 points at #17, and #17 points at #11: **one cable**.

**Watch a door disappear:**

1. 💻 Stop flat B:
   ```bash
   docker stop flat-b
   ```
2. 🏢 Run `ip link show master docker0` again. 👉 **1 line.**
3. 💻 Start it again:
   ```bash
   docker start flat-b
   ```
4. 🏢 Run it once more. 👉 2 lines, with a **new** door number.

## Test 3 · MASQUERADE = mask the FROM (going out)

🏢 The rule:

```
iptables -t nat -S POSTROUTING | grep 172.17
```
```
-A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE
```

🏢 Note the first number (packets) on this line:

```
iptables -t nat -L POSTROUTING -v -n | grep 172.17.0.0
```
```
    1    52 MASQUERADE  all  --  *  !docker0  172.17.0.0/16  0.0.0.0/0
```

💻 Send a letter out:

```bash
docker exec flat-a wget -q --spider http://example.com
```

🏢 Run the counter command again:

```
    3   169 MASQUERADE  ...
```

👉 It went up by 2: one for looking up example.com's address, one for the web request.

**See the mask:** ask the internet what address it sees, from the container and from your Mac. You should see **the same public IP** both times; nobody outside ever sees `172.17.0.2`.

```bash
docker exec flat-a wget -qO- http://checkip.amazonaws.com
```

```bash
curl http://checkip.amazonaws.com
```

## Test 4 · DNAT = change the TO (coming in)

💻 Which flats have an instruction at reception?

```bash
docker port flat-a
```
```
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
```

```bash
docker port flat-b
```

👉 Nothing for flat B: no `-p`, so no instruction.

🏢 The instruction itself:

```
iptables -t nat -S DOCKER
```
```
-N DOCKER
-A DOCKER -p tcp -m tcp --dport 8080 -j DNAT --to-destination 172.17.0.2:80
```

💻 Use it:

```bash
curl -s localhost:8080 | grep title
```
```
<title>Welcome to nginx!</title>
```

**Watch the counter.** 🏢 Before:

```
iptables -t nat -L DOCKER -v -n
```
```
    0     0 DNAT  tcp  ...  tcp dpt:8080 to:172.17.0.2:80
```

💻 Send a letter to the **building's address**, counter 8080:

```bash
docker exec flat-b wget -qO- http://172.17.0.1:8080 | grep title
```

🏢 After:

```
    1    60 DNAT  tcp  ...  tcp dpt:8080 to:172.17.0.2:80
```

👉 **1 packet, 60 bytes**: the TCP SYN. Reception changes only the first packet of a connection; conntrack handles the rest.

(The counter does **not** move for `curl localhost:8080` from your Mac: Docker Desktop delivers Mac traffic by a shortcut. On a Linux server it would.)

**Watch the rule disappear:**

1. 💻 Stop flat A:
   ```bash
   docker stop flat-a
   ```
2. 🏢 Run `iptables -t nat -S DOCKER` again. 👉 Only `-N DOCKER` is left.
3. 💻 Start it again:
   ```bash
   docker start flat-a
   ```
4. 🏢 The DNAT line is back.

## Test 5 · DNS: default bridge vs user-defined network

💻 On the default bridge:

```bash
docker run --rm alpine cat /etc/resolv.conf
```
```
nameserver 192.168.65.7
```

💻 On a user-defined network:

```bash
docker network create dnsdemo
```

```bash
docker run --rm --network dnsdemo alpine cat /etc/resolv.conf
```
```
nameserver 127.0.0.11
```

```bash
docker network rm dnsdemo
```

## Test 6 · The `127.0.0.1` trap

💻 An app that listens on `127.0.0.1` inside the container:

```bash
docker run -d --rm --name bindtest -p 8081:8000 python:3.12-alpine python -m http.server 8000 --bind 127.0.0.1
```

```bash
curl -sS http://localhost:8081
```
```
curl: (56) Recv failure: Connection reset by peer
```

💻 See where it listens, using netshoot inside the container's network:

```bash
docker run --rm --network container:bindtest nicolaka/netshoot ss -lntp
```
```
LISTEN 0  5   127.0.0.1:8000   0.0.0.0:*
```

```bash
docker stop bindtest
```

Now run it again with `--bind 0.0.0.0`: `curl` returns the page. ✅

## Clean up

🏢 Leave the Building terminal (`--rm` deletes the special container):

```
exit
```

💻 Remove the flats:

```bash
docker rm -f flat-a flat-b
```

## Cheat sheet

| Word | See it with | What proves it |
|---|---|---|
| **Bridge** | 🏢 `ip addr show docker0` | `172.17.0.1/16` |
| **veth pair** | 💻 `docker exec flat-a ip addr show eth0` + 🏢 `ip link \| grep "^17:"` | `@if17` ↔ `@if11` point at each other |
| **MASQUERADE** | 🏢 `iptables -t nat -L POSTROUTING -v -n` | The counter rises when a container goes out |
| **DNAT** | 🏢 `iptables -t nat -S DOCKER` | A rule exists only for containers with `-p` |
| **conntrack** | 🏢 the DNAT counter | 1 packet for a whole web page |
