# Troubleshooting Scenarios: Docker, Kubernetes and AWS ⭐🔥

> **Interview preparation** · ⏱️ about 3 hours to work through and practise out loud (estimate)
> Method first: [3.11 · Troubleshooting connectivity](../03-core-networking-protocols/11-troubleshooting-connectivity.md). Moved here from the original `06-debugging.md` without changes to the answers; only the links were updated.

How to use this file:

1. Read the scenario title only.
2. Answer **out loud**, in the order of the [6-step method](../03-core-networking-protocols/11-troubleshooting-connectivity.md#the-method-say-this-in-the-interview): DNS → route → port → listener → rules → app.
3. Then compare with **Say**, run the **Check** commands where you can, and prepare for **He'll push**.

Each one: **Say** (the core answer, in method order), **Check** (the commands), and **He'll push** (the follow-up). ⭐ = most likely. More network scenarios are in the [scenario deep dives](../../hemant-scenario-deep-dives.md): A2 (overlapping CIDRs), A3 (node vs pod CIDR), B1 (distroless), B10 (ECR timeout), B11 (NAT bill), B12 (502s during deploys) and B13 (private EKS endpoint).

## 🐳 Docker

**N1 ⭐ "The app works inside the container, but `curl localhost:8080` from the host fails."**
- **Say:**
  1. Is the port published? `docker port <c>`.
  2. **Where does the app listen?** If it's on `127.0.0.1`, DNAT delivers to the container's `eth0` and nobody is listening there. Make the app listen on `0.0.0.0` (Flask: `--host=0.0.0.0`).
  3. Is the right **container** port used (`-p 8080:80` vs an app on 8000)?
- **Check:**
  ```bash
  docker port myapp
  ```
  ```bash
  docker run --rm --network container:myapp nicolaka/netshoot ss -lntp
  ```
- **He'll push: "What error do you get?"** → On Docker Desktop, `Connection reset by peer` **(tested on the Mac with Docker Desktop, Oct 2026)**. On a Linux server, from outside, it's usually refused, because the container's kernel answers with a reset.

**N2 "Two containers can't reach each other by name."**
- **Say:** they're on the **default bridge**, which has no name lookup (`bad address`). Put both on a **user-defined network** (Compose does this for you); its DNS at `127.0.0.11` knows container names.
- **Check:**
  ```bash
  docker inspect -f '{{json .NetworkSettings.Networks}}' api
  ```
- **He'll push: "And containers on two different user-defined networks?"** → They can't talk until you connect one to the other's network: `docker network connect appnet api`.

**N3 "`docker run -p 8080:80` fails: `port is already allocated`."**
- **Say:** another container, or a host process, already holds host port 8080. Find it, then stop it or choose another host port.
- **Check:**
  ```bash
  docker ps --filter publish=8080
  ```
  ```bash
  lsof -nP -iTCP:8080 -sTCP:LISTEN
  ```
  (On Linux: `sudo ss -lntp | grep 8080`.)

**N4 ⭐ "The container can't reach the internet, or a company server."**
- **Say:** go step by step from inside the container:
  1. **DNS:** `nslookup google.com` inside it. If DNS fails but the IP works, fix DNS (`--dns`, or `"dns"` in `daemon.json`).
  2. **Host forwarding:** `sysctl net.ipv4.ip_forward` must be 1, and the MASQUERADE rule must exist.
  3. **A clash of addresses** (a classic): if the office or VPN network also uses `172.17.x.x`, the host sends that traffic into `docker0` instead of to the office. Change Docker's ranges with `"bip"` and `"default-address-pools"` in `daemon.json`. This is the same problem as [overlapping CIDRs](../../hemant-scenario-deep-dives.md) (A2), at a smaller scale.
  4. **A proxy or VPN** on the laptop that the container doesn't know about.
- **Check:**
  ```bash
  docker exec myapp nslookup google.com
  ```
  ```bash
  sudo iptables -t nat -S POSTROUTING
  ```

**N5 🔥 "ufw blocks port 8080, but the container is reachable from the internet."**
- **Say:** published ports go through **FORWARD**, not INPUT, so ufw never sees them. Use `-p 127.0.0.1:8080:80`, rules in **DOCKER-USER**, or a cloud security group. Details in [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md#-the-ufw-bypass-a-security-question-he-may-ask).

**N6 "The container must reach a database running on the host."**
- **Say:**
  - Use `host.docker.internal` (built into Docker Desktop; on Linux add `--add-host=host.docker.internal:host-gateway`).
  - **And** the host's database must listen on an address the container can reach. If it listens only on `127.0.0.1`, a container can't reach it, for the same reason as N1.

## ☸️ Kubernetes

**N7 ⭐ "The Service doesn't answer, but the pods are Running."**
- **Say:** **split the problem in half.**
  1. **Does the Service have endpoints?**
     - If they're **empty**: the Service's **selector doesn't match the pod labels**, or the pods aren't **Ready** (failing readiness probe).
  2. If there are endpoints, **call one pod IP directly**.
     - The pod IP works but the Service doesn't → a `port` / `targetPort` mismatch, or kube-proxy.
     - The pod IP fails too → the app (listening on `127.0.0.1`? a wrong port?) or a **NetworkPolicy**.
- **Check:**
  ```bash
  kubectl get endpointslices -l kubernetes.io/service-name=my-svc
  ```
  ```bash
  kubectl get pods --show-labels
  ```
  ```bash
  kubectl describe svc my-svc
  ```
  ```bash
  kubectl get pods -o wide
  ```
  ```bash
  kubectl port-forward pod/my-pod 8080:8080
  ```
- **He'll push: "Why is `port-forward` a good test?"** → It goes **straight to the pod** and skips the Service and kube-proxy, so it tells you which half is broken.

**N8 ⭐ "Pods can't resolve DNS."**
- **Say:**
  1. Check the pod's `/etc/resolv.conf`.
  2. Test a cluster name **and** an external name from a debug pod.
  3. Check the CoreDNS pods and logs.
  4. Look for a **NetworkPolicy** that blocks egress to kube-dns on **UDP and TCP 53**.
  - If only external names fail: CoreDNS can't reach its upstream, or `ndots:5` adds slow extra lookups ([3.4](../03-core-networking-protocols/04-dns.md#dns-inside-kubernetes-)).
- **Check:**
  ```bash
  kubectl exec my-pod -- cat /etc/resolv.conf
  ```
  ```bash
  kubectl run tmp --rm -it --image=nicolaka/netshoot -- nslookup kubernetes.default
  ```
  ```bash
  kubectl -n kube-system get pods -l k8s-app=kube-dns
  ```
  ```bash
  kubectl -n kube-system logs -l k8s-app=kube-dns
  ```

**N9 "We added a NetworkPolicy and everything broke."**
- **Say:**
  - A **default-deny** policy that includes **egress** also blocks **DNS**. Add an egress rule allowing UDP and TCP 53 to the kube-dns pods.
  - Policies only **add** permissions, so check every policy that selects the pod.
  - The CNI must support NetworkPolicy. On EKS, the VPC CNI does when network policy is enabled.
- **Check:**
  ```bash
  kubectl get networkpolicy -A
  ```
  ```bash
  kubectl describe networkpolicy -n my-namespace
  ```
- **He'll push:** "Two rules in one `from` entry: AND or OR?" → see [Kubernetes 14](../../kubernetes/14-cluster-networking.md).

**N10 "EKS pods are stuck in `ContainerCreating`: failed to assign an IP address."**
- **Say:** the VPC CNI gives every pod a **real VPC IP**, and either the **subnet has run out of free IPs** or the node has reached its **max pods**. Fixes: **prefix delegation**, bigger subnets, or a **secondary CIDR for pods** ([scenario deep dives](../../hemant-scenario-deep-dives.md), A3).
- **Check:**
  ```bash
  kubectl -n kube-system logs -l k8s-app=aws-node -c aws-node --tail=50
  ```
  ```bash
  aws ec2 describe-subnets --subnet-ids subnet-0123456789abcdef0 --query 'Subnets[].AvailableIpAddressCount'
  ```

**N11 "Calls from pods to an external API time out now and then."**
- **Say:** intermittent timeouts usually mean a **limit** is being hit:
  - **conntrack table full** on the node (`nf_conntrack: table full` in `dmesg`);
  - **NAT gateway port exhaustion**: a NAT gateway supports about **55,000 simultaneous connections to each unique destination**. Watch the **`ErrorPortAllocation`** CloudWatch metric;
  - **DNS throttling**: the 1024 packets-per-second limit per network interface to the VPC resolver; `ndots:5` makes it worse.
- **He'll push: "How do you fix NAT port exhaustion?"** → Reuse connections (keep-alive and connection pools), add more IPs to the NAT gateway, spread across several NAT gateways, or use VPC endpoints for AWS services.

## ☁️ AWS

**N12 ⭐ "I can't connect to an EC2 instance or RDS database: it times out."**
- **Say:** a **timeout means something drops the packets**. Check in this order:
  1. The **security group** on the target: right port, and the source is the client's **SG or CIDR**.
  2. The **NACLs** on both subnets: **stateless**, so allow the return traffic on **ephemeral ports**.
  3. The **route tables**: is there a route between the subnets (or a peering / TGW route)? For internet access, an IGW or NAT.
  4. RDS: is it in private subnets, and is "publicly accessible" what you expect?
  - If it's **refused** instead of a timeout, the network is fine: the database is down, or it's the wrong port.
- **Tools:**
  - **Reachability Analyzer** checks the configuration path between two resources without sending any traffic.
  - **VPC Flow Logs** show `ACCEPT` or `REJECT` for each connection. A `REJECT` tells you where it was dropped.
- **Check:**
  ```bash
  aws ec2 describe-security-groups --group-ids sg-0123456789abcdef0
  ```
  ```bash
  aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=subnet-0123456789abcdef0
  ```
  ```bash
  aws ec2 describe-route-tables --filters Name=association.subnet-id,Values=subnet-0123456789abcdef0
  ```
- **He'll push: "Security group vs NACL?"**

| | Security group | NACL |
|---|---|---|
| Applies to | An ENI / instance | A whole subnet |
| State | **Stateful**: replies are allowed automatically | **Stateless**: allow both directions yourself |
| Rules | Allow only | Allow **and** deny, checked in number order |

A flow log line (default format):

```
2 123456789012 eni-0abc1234 10.0.1.25 10.0.2.15 49152 5432 6 3 180 1696750000 1696750060 REJECT OK
```

The fields are: version, account, ENI, **source**, **destination**, source port, **destination port**, protocol (6 = TCP), packets, bytes, start, end, **action**, log status.

**N13 "An instance in a private subnet can't reach the internet: `apt update` hangs."**
- **Say:**
  1. The private subnet's route table needs `0.0.0.0/0 → nat-xxxx`.
  2. The NAT gateway must sit in a **public** subnet, whose own route is `0.0.0.0/0 → igw-xxxx`.
  3. The NAT gateway needs an Elastic IP.
  4. Check the NACLs.
  - For AWS services, prefer **VPC endpoints**. The S3 gateway endpoint is free and keeps traffic off the NAT ([scenario deep dives](../../hemant-scenario-deep-dives.md), B10 and B11).
- **Check:**
  ```bash
  aws ec2 describe-nat-gateways --filter Name=vpc-id,Values=vpc-0123456789abcdef0
  ```

## Interview angle (practise out loud)

- ⭐ "Something can't connect. Walk me through how you debug it." → The 6 steps, the error-message table, and test from where the client runs.
- ⭐ "What's the difference between connection refused and a timeout?" → Refused: you reached the host and it said no (TCP reset), so nothing is listening. Timeout: no answer at all, so something dropped the packets.
- "Ping fails. Is the server down?" → Not necessarily: ICMP is often blocked. Test the real port with `nc` or `curl`.
- "How do you debug a distroless pod?" → `kubectl debug` with netshoot and `--target`, or the bash `/dev/tcp` trick.

## More practice

- [Lab 3.5 · Troubleshooting challenge](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md): 8 hidden faults to find with the method, on a network you build locally.
- [Troubleshooting exercises](../14-practice-exercises/04-troubleshooting-scenarios.md), beginner to expert, with [solutions](../14-practice-exercises/solutions/04-troubleshooting-scenarios-solutions.md).
