# Network Command Cheatsheet

> **Reference** · Every command by task, for Mac, Linux, Docker, Kubernetes and AWS. Written before the curriculum was reorganised; the content is unchanged. The lessons explain each command; [Lab 1.1](../13-hands-on-labs/lab-01.1-inspect-your-own-network.md) and the Linux labs use most of them. See also: [common ports](common-ports.md), [glossary](glossary.md).

Every command by task. **All of them were tested:**
- Linux commands in `nicolaka/netshoot` inside Docker Desktop's VM;
- Mac commands on this Mac;
- `docker` commands against Docker 29.6.2;
- `kubectl` commands against the kubectl `--help` (with an empty kubeconfig, so no cluster was touched);
- `aws` commands offline, for valid parameters only, with no AWS account used.

Not run: the two `sudo` Mac commands (packet capture and DNS flush) and `resolvectl`, which needs a systemd Linux host.

Use `sudo` for `iptables`, `conntrack`, `tcpdump` and `ss -p` on a real Linux server.

## Mac vs Linux: the same job, different tools

| Task | Mac | Linux |
|---|---|---|
| My IP addresses | `ipconfig getifaddr en0` · `ifconfig en0` | `ip -br addr` |
| Routes and the default gateway | `route -n get default` · `netstat -rn` | `ip route` · `ip route get 8.8.8.8` |
| Which programs are listening | `lsof -nP -iTCP -sTCP:LISTEN` | `ss -lntp` |
| Who is using port 8080 | `lsof -nP -iTCP:8080 -sTCP:LISTEN` | `ss -lntp \| grep 8080` |
| My DNS servers | `scutil --dns \| grep nameserver` | `cat /etc/resolv.conf` |
| Test a TCP port (3-second limit) | `nc -zv -G 3 google.com 443` | `nc -zv -w 3 google.com 443` |
| Capture packets | `sudo tcpdump -i en0 -nn port 53` | `sudo tcpdump -i any -nn port 53` |
| Flush the DNS cache | `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` | `resolvectl flush-caches` (systemd-resolved) |

## Linux: addresses and routes

| Command | What it shows |
|---|---|
| `ip addr` (short: `ip a`) | Every interface and its IPs |
| `ip -br addr` | The same, one line per interface |
| `ip route` | The routing table, including `default via …` (the gateway) |
| `ip route get 8.8.8.8` | **Which route and interface** a packet to that IP would really use |
| `ip link show master docker0` | What is plugged into the docker0 bridge (the veth doors) |
| `ip neigh` | The ARP table: IP → MAC address of neighbours on the local network |

## Linux: ports and connections

| Command | What it shows |
|---|---|
| `ss -lntp` | **TCP ports listening**, on which address (`127.0.0.1` vs `0.0.0.0`), and by which program |
| `ss -lnup` | The same for UDP |
| `ss -tnp` | Open TCP connections, with programs |
| `ss -s` | A summary count of sockets |

## Linux: connectivity

| Command | What it shows |
|---|---|
| `ping -c 3 8.8.8.8` | ICMP reachability (often blocked, so a failure proves little) |
| `traceroute 8.8.8.8` | Each router hop on the way |
| `mtr -r -c 10 8.8.8.8` | traceroute plus packet loss per hop, as a report |
| `nc -zv -w 3 db 5432` | **Is this TCP port reachable?** succeeded / refused / timed out |
| `curl -v http://host:8080/health` | The full conversation: DNS, connect, TLS, HTTP headers |
| `curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://example.com` | Just the status code and the total time |
| `timeout 3 bash -c '</dev/tcp/db/5432' && echo open` | A port test with only bash (no curl or nc needed) |

## Linux: DNS

| Command | What it shows |
|---|---|
| `nslookup google.com` | The answer and which server gave it |
| `nslookup google.com 8.8.8.8` | Ask a **specific** DNS server |
| `dig google.com` | The full answer, with TTLs |
| `dig +short google.com` | Just the IPs |
| `dig google.com @8.8.8.8` | Ask a specific server |
| `dig +trace google.com` | The whole chain: root → `.com` → the owner |
| `dig -x 8.8.8.8 +short` | Reverse lookup: IP → name |
| `getent hosts db` | What **an app** gets (uses `/etc/hosts` and search domains) |
| `cat /etc/resolv.conf` | Which DNS server, search domains, `ndots` |

## Linux: firewall, NAT and conntrack

| Command | What it shows |
|---|---|
| `iptables -t nat -S` | All NAT rules, in the same form they were written |
| `iptables -t nat -L -n -v` | NAT rules with **packet counters** |
| `iptables -L DOCKER-USER -n -v` | Your own rules for container traffic |
| `iptables -S FORWARD` | The rules for traffic passing through (to containers) |
| `nft list ruleset` | Everything in nftables, the system underneath |
| `conntrack -L` | The connection table (every NAT change) |
| `conntrack -L -p tcp --dport 8080` | Only connections to port 8080 |
| `conntrack -C` | How many entries the table has (compare with `sysctl net.netfilter.nf_conntrack_max`) |
| `sysctl net.ipv4.ip_forward` | `1` = the host forwards packets (Docker needs this) |
| `cat /proc/sys/net/ipv4/ip_local_port_range` | The ephemeral port range |

## Linux: packet capture

| Command | What it shows |
|---|---|
| `tcpdump -i any -nn port 8080` | Every packet to or from port 8080, on all interfaces |
| `tcpdump -i docker0 -nn host 172.17.0.2` | Traffic of one container, on the bridge |
| `tcpdump -i any -nn -w /tmp/cap.pcap port 53` | Save DNS traffic to a file to open in Wireshark |

## Linux: get into a container's network

| Command | What it shows |
|---|---|
| `docker inspect -f '{{.State.Pid}}' flat-a` | The container's main process ID on the host |
| `nsenter -t 1493 -n ss -lntp` | Run a **host** tool inside that container's network namespace (use the PID from above) |

## Docker

| Command | What it shows |
|---|---|
| `docker network ls` | All networks |
| `docker network inspect bridge` | Subnet, gateway and connected containers |
| `docker network create appnet` | A user-defined network (with name lookup) |
| `docker network connect appnet api` | Attach a running container to another network |
| `docker port flat-a` | Which host ports map to which container ports |
| `docker ps --filter publish=8080` | Which container holds host port 8080 |
| `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' flat-a` | The container's IP |
| `docker exec flat-a cat /etc/resolv.conf` | The container's DNS server |
| `docker run --rm -it --network container:flat-a nicolaka/netshoot` | A toolbox inside the container's network |
| `docker run -it --rm --network=host --privileged alpine sh` | On a Mac: a shell in Docker Desktop's VM network (the lab's "Building" terminal) |

## Kubernetes

| Command | What it shows |
|---|---|
| `kubectl get pods -o wide` | Pod IPs and their nodes |
| `kubectl get svc -A` | All Services, with their ClusterIPs and ports |
| `kubectl get endpointslices -l kubernetes.io/service-name=my-svc` | Which pod IPs the Service sends to (empty = a problem) |
| `kubectl describe svc my-svc` | Selector, `port` and `targetPort` |
| `kubectl get pods --show-labels` | Pod labels, to compare with the Service selector |
| `kubectl port-forward svc/my-svc 8080:80` | Reach a Service from your laptop |
| `kubectl port-forward pod/my-pod 8080:8080` | Reach one pod directly, skipping the Service |
| `kubectl exec my-pod -- cat /etc/resolv.conf` | The pod's DNS settings |
| `kubectl run tmp --rm -it --image=nicolaka/netshoot -- bash` | A temporary toolbox pod |
| `kubectl debug -it my-pod --image=nicolaka/netshoot --target=app` | A toolbox inside a running pod's network (works for distroless) |
| `kubectl debug node/my-node -it --image=nicolaka/netshoot` | A toolbox in a node's network |
| `kubectl get networkpolicy -A` | Every NetworkPolicy |
| `kubectl -n kube-system get pods -l k8s-app=kube-dns` | The CoreDNS pods |
| `kubectl -n kube-system logs -l k8s-app=kube-dns` | CoreDNS logs |
| `kubectl -n kube-system get configmap coredns -o yaml` | The CoreDNS configuration (the Corefile) |
| `kubectl -n kube-system logs -l k8s-app=aws-node -c aws-node --tail=50` | EKS VPC CNI logs (IP assignment problems) |
| `kubectl get events -A --field-selector type=Warning` | Recent warnings, e.g. failed sandbox or network setup |

## AWS

| Command | What it shows |
|---|---|
| `aws ec2 describe-security-groups --group-ids sg-0123456789abcdef0` | A security group's rules |
| `aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=subnet-0123456789abcdef0` | The NACL on a subnet |
| `aws ec2 describe-route-tables --filters Name=association.subnet-id,Values=subnet-0123456789abcdef0` | The route table of a subnet |
| `aws ec2 describe-subnets --subnet-ids subnet-0123456789abcdef0 --query 'Subnets[].AvailableIpAddressCount'` | How many free IPs a subnet has (EKS pods need them) |
| `aws ec2 describe-nat-gateways --filter Name=vpc-id,Values=vpc-0123456789abcdef0` | NAT gateways in a VPC (note: `--filter`, not `--filters`) |
| `aws ec2 describe-vpc-endpoints --filters Name=vpc-id,Values=vpc-0123456789abcdef0` | VPC endpoints (ECR, S3, STS…) |
| `aws ec2 describe-flow-logs --filter Name=resource-id,Values=vpc-0123456789abcdef0` | Whether VPC Flow Logs are on (again `--filter`) |
| `aws ec2 create-network-insights-path --source i-0123456789abcdef0 --destination i-0fedcba9876543210 --protocol tcp --destination-port 5432` | **Reachability Analyzer**, step 1: define the path |
| `aws ec2 start-network-insights-analysis --network-insights-path-id nip-0123456789abcdef0` | Step 2: analyse it (each analysis is billed) |
| `aws ssm start-session --target i-0123456789abcdef0` | A shell on an instance with no SSH or public IP |
