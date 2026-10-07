# 02 · Kubernetes Architecture ⭐

![Kubernetes architecture](diagrams/02-architecture.drawio.svg)

## Control plane (the "brain")

| Component | What it does | Remember |
|---|---|---|
| **kube-apiserver** | The front door. Every request (from kubectl, controllers, kubelets) goes through it. Checks **who you are**, **what you may do**, runs **admission** checks, then saves to etcd. | The **only** component that talks to etcd. Stateless, so you can run several. |
| **etcd** | A consistent key-value database holding **all cluster state** (every object). Uses the Raft algorithm to agree. | **Back it up.** Lose etcd and you lose the cluster's state. Run 3 or 5 members. |
| **kube-scheduler** | Watches for pods with no node, then picks a node: **filter** (which nodes fit?) → **score** (which fits best?) → **bind**. | Scheduler down = new pods stay `Pending`. Running pods are fine. |
| **kube-controller-manager** | Runs the built-in controllers: Deployment, ReplicaSet, Node, Job, EndpointSlice, ServiceAccount, Namespace and more. | Every one is a reconciliation loop ([01](01-fundamentals.md)). |
| **cloud-controller-manager** | Talks to the cloud: node lifecycle, routes, creating cloud load balancers for `LoadBalancer` Services. | On EKS, AWS runs it for you. |

## Worker node components

| Component | What it does |
|---|---|
| **kubelet** | The node agent. Registers the node, watches for pods assigned to it, starts them through the **container runtime**, runs **probes**, and reports status back. |
| **Container runtime** | **containerd** (or CRI-O), driven through the **CRI** (container runtime interface). It pulls images and runs containers with runc. |
| **kube-proxy** | Turns Services into network rules on each node (**iptables** by default, or **nftables**, stable since 1.33). IPVS mode was deprecated in 1.35. Some network plugins (Cilium) replace kube-proxy with eBPF. |
| **CNI plugin** | Gives every pod its IP address and connects pods across nodes (Calico, Cilium, Flannel, AWS VPC CNI). See [14](14-cluster-networking.md). |

## Add-ons (run as pods, usually in `kube-system`)

- **CoreDNS:** cluster DNS, so `my-svc.my-ns.svc.cluster.local` resolves ([08](08-services-and-dns.md)).
- **metrics-server:** CPU and memory numbers for `kubectl top` and the HPA ([12](12-resources-and-autoscaling.md)).
- Ingress or Gateway controller, CSI storage drivers, and a log collector DaemonSet.

## How the parts talk

- Everything goes **through the API server**. Components **watch** for changes instead of polling each other.
- The kubelet watches for pods on its own node. The API server calls the kubelet for `kubectl logs`, `exec` and `port-forward`.
- Controllers never talk to each other; they only read and write objects. That loose coupling is why Kubernetes is easy to extend ([19](19-extending-kubernetes.md)).

## High availability

- Run **3 (or 5) control plane nodes** behind a load balancer.
- etcd needs a **majority (quorum)** to work: 3 members survive 1 failure, 5 members survive 2. Use **odd numbers**, because 4 members still only survive 1 failure.
- **On EKS:** AWS runs the API servers and etcd across **3 availability zones**, and you never see them. You manage nodes and workloads ([20](20-eks.md)).

## What breaks when a component is down ⭐

| Down | Effect |
|---|---|
| API server | Running pods **keep running**, but nothing can change: no deploys, no scaling, `kubectl` fails, and failures aren't self-healed |
| etcd | The API server can't read or write state. Effectively the same as the API server being down. **Data loss** if it's gone without a backup. |
| Scheduler | New pods stay `Pending`. Existing pods are fine. |
| Controller manager | No self-healing: deleted pods aren't replaced, rollouts stop |
| kubelet on one node | That node turns `NotReady` within about a minute. After about **5 minutes** (default toleration) its pods are evicted, and controllers recreate them elsewhere. |
| CoreDNS | Service names stop resolving, so most apps break even though the pods are "Running" |

> **Docker link:** the kubelet calls containerd, which calls runc, the same chain as [Docker 02](../docker/02-architecture-internals.md). Kubernetes removed its Docker adapter (dockershim) in **1.24**, but Docker-built images still run because they're OCI images.

## Interview angle

- ⭐ "Explain Kubernetes architecture." → control plane (API server, etcd, scheduler, controller manager, cloud controller), nodes (kubelet, runtime, kube-proxy, CNI), add-ons (CoreDNS, metrics-server).
- ⭐ "Which component talks to etcd?" → only the API server.
- "What happens if the control plane goes down?" → running workloads continue; nothing new happens.
- "Why an odd number of etcd members?" → quorum is a majority; an even number adds cost without adding fault tolerance.
- "Where does kube-proxy run, and what does it do?" → on every node; it programs the iptables or nftables rules that make Service IPs work.

## Practice 🖥️

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl describe node kind-control-plane
kubectl get --raw='/readyz?verbose'
```

The last command shows the API server's own health checks, including etcd.
