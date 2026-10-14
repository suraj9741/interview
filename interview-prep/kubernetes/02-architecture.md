# 02 · Kubernetes Architecture ⭐

![Kubernetes architecture](diagrams/02-architecture.drawio.svg)

A cluster has two halves:

- The **control plane** decides what *should* run and stores it. It never runs your app.
- The **worker nodes** actually run your containers, and keep reporting what *is* running.

The two halves only ever meet through one place: the **API server**. Read the summary tables first, then the deep dive for each component below them.

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

---

## Component deep dive ⭐

Each component below follows the same shape: **what it is**, **what it does step by step**, **what to remember**, and **what you see when it breaks**.

### kube-apiserver: the front door

**What it is.** A stateless REST (HTTPS) server, listening on port **6443**. It is the only way to read or change cluster state. kubectl, the scheduler, every controller, every kubelet and every operator are all just clients of it.

**What it does with every request:**

1. **Authentication:** who are you? Client certificate, bearer token (ServiceAccount token), or OIDC. On EKS, your IAM identity.
2. **Authorization:** may you do this verb on this resource in this namespace? Usually **RBAC**; the kubelet's own requests go through the **Node** authorizer, which only lets a kubelet touch its own node's pods ([15](15-security.md)).
3. **Mutating admission:** may change the object (set defaults, inject a sidecar).
4. **Schema validation:** is the object well formed?
5. **Validating admission:** may reject it (Pod Security, ResourceQuota, Kyverno, OPA Gatekeeper).
6. **Persist to etcd**, then tell every **watcher** that the object changed.

**Other jobs worth knowing:**

- **Watch:** clients open a long-lived `watch` and get a stream of changes (ADDED, MODIFIED, DELETED). This is how every component learns about work **without polling**. The API server keeps a **watch cache** in memory so thousands of watchers don't all hit etcd.
- **Optimistic concurrency:** every object has a `resourceVersion`. If two clients update the same old version, the second gets `409 Conflict` and must re-read and retry. No locks.
- **API groups and versions:** `/api/v1` (core: pods, services), `/apis/apps/v1` (deployments) and so on. CRDs add new groups ([19](19-extending-kubernetes.md)).
- **Aggregation layer:** forwards some API groups to another server. `metrics.k8s.io` (used by `kubectl top`) is served by metrics-server this way.
- **API Priority and Fairness:** queues requests by priority so one noisy client (a buggy controller) can't starve kubelets and the scheduler.
- **Proxy to kubelets:** `kubectl logs`, `exec`, `port-forward` and `attach` go kubectl → API server → **kubelet on port 10250**.

**Remember:** stateless, so scale it **horizontally** behind a load balancer. It is the only thing allowed to talk to etcd.

**When it breaks:** `kubectl` fails with `connection refused` or timeouts. Running pods keep running, because the kubelet and kernel rules don't need it to serve traffic, but nothing can change and nothing self-heals.

### etcd: the cluster's memory

**What it is.** A distributed, strongly consistent key-value store. Every Kubernetes object is stored as a key such as `/registry/pods/default/web-abc`. Clients use port **2379**; members talk to each other on port **2380**.

**How it works:**

- Uses the **Raft** consensus algorithm. One member is the **leader**; all writes go through it and are committed only when a **majority (quorum)** has them on disk.
- That gives **strong consistency**: once a write succeeds, every later read sees it.
- Every change gets a new **revision** number. Kubernetes' `resourceVersion` comes from it, and watches are built on it.
- Old revisions are **compacted** (the API server asks for this every 5 minutes by default), and the database file needs an occasional **defrag** to give the space back.

**Remember:**

- It is sensitive to **disk latency**. Slow disks cause leader elections and a slow, flaky API. Use SSDs.
- It has a size quota (**2 GiB by default**, commonly raised up to **8 GiB**). Hit it and the cluster goes read-only (`mvcc: database space exceeded`).
- **Backup** = `etcdctl snapshot save`. **Restore** = `etcdctl snapshot restore` (newer versions move this to `etcdutl`) to a new data directory, then restart etcd and the API server pointing at it.
- Secrets are stored here, so turn on **encryption at rest** ([10](10-configmaps-and-secrets.md)).

**When it breaks:** lose quorum and the API server can't write (and soon can't read) anything. Lose all members with no backup and the cluster's state is gone for good.

### kube-scheduler: picks a node for each pod

**What it is.** A controller that watches for pods with an empty `spec.nodeName`. It **only decides**; it never starts anything. It writes its decision back to the API server, and the kubelet does the rest.

**What it does for each pod:**

1. **Queue:** unscheduled pods wait in a priority queue (higher `priorityClassName` first).
2. **Filter:** drop nodes that can't run the pod. Checks include:
   - enough free **requested** CPU and memory (requests, not real usage);
   - **taints** the pod doesn't tolerate;
   - **node affinity** or `nodeSelector` not matching;
   - host ports already taken;
   - volume in another zone;
   - node marked unschedulable (cordoned).
3. **Score:** rank the remaining nodes from 0 to 100 with plugins such as least-allocated resources, balanced allocation, image already on the node, pod (anti-)affinity and topology spread.
4. **Bind:** pick the top-scoring node and write a **Binding**, which sets `spec.nodeName`.
5. **No node fits?** The pod stays `Pending` with a `FailedScheduling` event that says why, such as `0/3 nodes are available: 3 Insufficient cpu`. If the pod has a higher priority, the scheduler may **preempt** (evict) lower-priority pods to make room.

**Remember:**

- Every one of those steps is a **plugin** in the *scheduling framework*, so you can tune the scheduler or run a second scheduler (`spec.schedulerName`) ([13](13-scheduling.md)).
- Runs as several copies for HA, but only one is active at a time, chosen by **leader election** (a `Lease` object in `kube-system`).

**When it breaks:** new pods stay `Pending` with no `FailedScheduling` events at all, which is the giveaway. Pods already running are unaffected.

### kube-controller-manager: the self-healing engine

**What it is.** One binary that runs dozens of **controllers**. Each controller is a reconciliation loop: watch objects → compare desired with actual → act → repeat ([01](01-fundamentals.md)).

**The controllers interviewers ask about:**

| Controller | Watches | Does |
|---|---|---|
| Deployment | Deployments | Creates and scales ReplicaSets for rollouts and rollbacks |
| ReplicaSet | ReplicaSets, Pods | Keeps exactly N pods matching the selector |
| StatefulSet, DaemonSet, Job, CronJob | their objects | Ordered pods, one pod per node, run-to-completion, scheduled Jobs |
| Node lifecycle | Node heartbeats (Leases) | Marks silent nodes `NotReady`, taints them, which triggers eviction of their pods |
| EndpointSlice | Services, Pods | Keeps each Service's list of **ready** pod IPs up to date |
| Namespace | Namespaces | Deletes everything inside a namespace being deleted |
| ServiceAccount, token | Namespaces | Creates the `default` ServiceAccount in each namespace |
| Garbage collector | `ownerReferences` | Deletes children when the owner is deleted (ReplicaSet → its pods) |
| HPA | HPAs, metrics | Changes `replicas` based on CPU, memory or custom metrics ([12](12-resources-and-autoscaling.md)) |
| PersistentVolume | PVCs, PVs | Binds claims to volumes ([11](11-storage.md)) |

**How a controller works inside:** an **informer** lists and then watches the objects it cares about, keeps a local cache, and pushes changed keys onto a **work queue**. Workers pop a key, read the current state from the cache, and fix the difference. Failed keys are retried with backoff. The same pattern powers every operator you'll write ([19](19-extending-kubernetes.md)).

**Remember:** controllers **never call each other**. The Deployment controller doesn't tell the ReplicaSet controller anything; it just writes a ReplicaSet object, and the ReplicaSet controller notices. Leader election works the same way as the scheduler's.

**When it breaks:** nothing heals. Deleted pods aren't replaced, rollouts freeze, Services don't get new endpoints, dead nodes' pods are never moved.

### cloud-controller-manager: the bridge to the cloud

**What it is.** The cloud-specific controllers, split out of the controller manager so cloud vendors can ship their own code without changing Kubernetes.

**What it does:**

- **Node controller:** labels new nodes with their cloud details (instance type, zone, region) and deletes the Node object when the VM is gone from the cloud.
- **Route controller:** sets up cloud network routes so pods on different nodes can reach each other (only with some network setups).
- **Service controller:** for a `type: LoadBalancer` Service, creates the cloud load balancer and writes its address into the Service's status.

**Remember:** on EKS, AWS runs it inside the managed control plane. In practice most EKS clusters install the **AWS Load Balancer Controller** for ALBs and NLBs instead of the built-in one ([20](20-eks.md)). On bare metal there's no cloud controller, so `LoadBalancer` Services stay `<pending>` until you add something like MetalLB.

**When it breaks:** new `LoadBalancer` Services never get an external IP, and new nodes may stay tainted as uninitialised.

### kubelet: the node agent

![Inside a worker node](diagrams/02-node-internals.drawio.svg)

**What it is.** A process (a systemd service, **not** a pod) on every node, including control plane nodes. It is the only component that actually makes containers exist. It listens on port **10250**.

**What it does:**

1. **Registers the node** with the API server and reports its capacity (CPU, memory, pods, ephemeral storage).
2. **Heartbeats:** renews the node's `Lease` in `kube-node-lease` about every **10 seconds**, and updates the Node's status. Miss enough heartbeats and the node lifecycle controller marks it `NotReady`.
3. **Watches for pods** whose `spec.nodeName` is this node.
4. **Runs each pod** through the container runtime (CRI), in order: create the pod sandbox → CNI gives it an IP → mount volumes → pull images → init containers → app containers and sidecars ([04](04-kubectl-apply-flow.md)).
5. **Runs probes** (startup, liveness, readiness) and restarts containers per `restartPolicy` ([06](06-probes.md)).
6. **Enforces resources:** turns requests and limits into **cgroup** settings. A container over its memory limit is **OOMKilled** by the kernel.
7. **Evicts pods under pressure:** when the node runs low on memory or disk (default hard thresholds include `memory.available<100Mi` and `nodefs.available<10%`), it evicts pods, BestEffort first ([12](12-resources-and-autoscaling.md)).
8. **Reports pod status** (phase, conditions, container states, restart counts) back to the API server.
9. **Serves** logs, exec and port-forward for the API server, and resource metrics for metrics-server.

**Static pods:** the kubelet also runs any pod manifest it finds in a local folder (`/etc/kubernetes/manifests` on kubeadm clusters), even with no API server. That is how kubeadm runs the API server, etcd, scheduler and controller manager themselves. The API server shows a read-only **mirror pod** for each one.

**Remember:** the kubelet does not run containers itself; it asks the runtime to. It only trusts the API server (and its static pod folder).

**When it breaks:** the node goes `NotReady`. Its containers usually **keep running** (containerd doesn't need the kubelet), but nothing on that node is restarted, probed or updated, and after about 5 minutes the pods are evicted and recreated on other nodes.

### Container runtime: containerd and runc

**What it is.** The software that pulls images and runs containers. The kubelet talks to it through the **CRI**, a gRPC API on a local socket (for containerd, `/run/containerd/containerd.sock`). containerd and CRI-O are the common choices.

**The chain:** kubelet → (CRI) → **containerd** → **containerd-shim** (one per pod) → **runc** → Linux **namespaces** and **cgroups**.

- **containerd** manages images, snapshots (container filesystems) and pod sandboxes.
- The **shim** keeps the containers running even if containerd restarts, and holds their exit codes.
- **runc** creates the container process and exits; it is the OCI reference runtime.
- The **pause container** is created first for each pod. It does nothing except hold the pod's network namespace, so app containers can restart without the pod losing its IP.

**Remember:** debug at this level on the node with `crictl ps`, `crictl logs` and `crictl inspect`, not `docker`. Kubernetes removed dockershim in 1.24 (see the Docker link below).

**When it breaks:** pods stick in `ContainerCreating`, or the node goes `NotReady` with a "container runtime is down" condition.

### kube-proxy: makes Service IPs work

**What it is.** A DaemonSet pod on every node. It watches **Services** and **EndpointSlices** and turns them into kernel networking rules.

**What it does:** a Service's ClusterIP is **virtual**: no interface owns it. kube-proxy writes rules that say "a packet to `10.96.12.5:80` → pick one of these ready pod IPs and rewrite the destination (DNAT)". When a pod becomes ready or goes away, the EndpointSlice changes and kube-proxy updates the rules on every node ([08](08-services-and-dns.md)).

**Modes:** `iptables` (the default; one rule chain per Service, random pick of a backend), `nftables` (faster updates on big clusters), and `ipvs` (deprecated). Cilium's eBPF mode can replace kube-proxy entirely.

**Remember:** kube-proxy is **not in the data path**. Packets never pass through the kube-proxy process; the kernel does the work. If kube-proxy dies, existing rules keep working; they just stop being updated.

**When it breaks:** new Services, or pods that changed, don't get traffic on that node, while older ones still work. Classic "works on some nodes, not others".

### CNI plugin: pod networking

**What it is.** A plugin (a binary in `/opt/cni/bin` plus a config in `/etc/cni/net.d`, usually installed by a DaemonSet) that the runtime calls each time a pod sandbox is created or deleted.

**What it does:** gives the pod an IP from the pod range, creates its network interface, and sets up routes (or an overlay such as VXLAN) so **every pod can reach every other pod without NAT**, which is the Kubernetes network model. Many plugins (Calico, Cilium) also enforce **NetworkPolicy** ([14](14-cluster-networking.md)).

**Remember:** on EKS the **AWS VPC CNI** gives pods real VPC IP addresses, so running out of subnet IPs or ENI slots is a common cause of pods stuck in `ContainerCreating`.

**When it breaks:** nodes stay `NotReady` ("network plugin not ready"), or new pods never get an IP.

### CoreDNS and metrics-server

- **CoreDNS:** a Deployment behind the `kube-dns` Service. Every pod's `/etc/resolv.conf` points at that Service's IP. CoreDNS watches Services and answers `<svc>.<ns>.svc.cluster.local` with the ClusterIP, and forwards everything else to the upstream DNS. The pod's `ndots:5` setting is why short names like `my-svc` work, and also why external lookups can be slow ([08](08-services-and-dns.md)).
- **metrics-server:** scrapes CPU and memory from every kubelet (every 15 seconds by default), keeps only the latest values in memory, and serves them through the API server's aggregation layer as `metrics.k8s.io`. It powers `kubectl top` and the HPA. It is **not** a monitoring system: no history; use Prometheus for that ([16](16-observability.md)).

---

## How the parts talk

- Everything goes **through the API server**. Components **watch** for changes instead of polling each other.
- The kubelet watches for pods on its own node. The API server calls the kubelet for `kubectl logs`, `exec` and `port-forward`.
- Controllers never talk to each other; they only read and write objects. That loose coupling is why Kubernetes is easy to extend ([19](19-extending-kubernetes.md)).

**Who connects to whom** (ports are the usual defaults):

| From | To | Why |
|---|---|---|
| kubectl, controllers, scheduler, kubelet, kube-proxy | API server `:6443` | read, write and watch objects |
| API server | etcd `:2379` | store and read state; nothing else talks to etcd |
| etcd member | etcd member `:2380` | Raft replication |
| API server | kubelet `:10250` | logs, exec, port-forward; metrics-server scrapes here too |
| kubelet | containerd (local socket) | CRI: create sandboxes, pull images, run containers |
| containerd | CNI plugin (local binary) | give the pod an IP |

**One loop, start to finish:** you scale a Deployment from 2 to 3. The API server saves it → the Deployment controller updates the ReplicaSet → the ReplicaSet controller creates 1 Pod → the scheduler binds it to a node → that node's kubelet starts it and reports Ready → the EndpointSlice controller adds its IP → kube-proxy on every node updates its rules. Six components cooperated, and **none of them called another directly**. The full version of this story is [04](04-kubectl-apply-flow.md).

## High availability

- Run **3 (or 5) control plane nodes** behind a load balancer.
- etcd needs a **majority (quorum)** to work: 3 members survive 1 failure, 5 members survive 2. Use **odd numbers**, because 4 members still only survive 1 failure.
- The API server is **active-active** (all copies serve requests). The scheduler and controller manager are **active-passive** (one leader at a time, via leader election).
- **On EKS:** AWS runs the API servers and etcd across **3 availability zones**, and you never see them. You manage nodes and workloads ([20](20-eks.md)).

## What breaks when a component is down ⭐

| Down | Effect |
|---|---|
| API server | Running pods **keep running**, but nothing can change: no deploys, no scaling, `kubectl` fails, and failures aren't self-healed |
| etcd | The API server can't read or write state. Effectively the same as the API server being down. **Data loss** if it's gone without a backup. |
| Scheduler | New pods stay `Pending`. Existing pods are fine. |
| Controller manager | No self-healing: deleted pods aren't replaced, rollouts stop |
| Cloud controller manager | New `LoadBalancer` Services get no external IP; new nodes may stay uninitialised |
| kubelet on one node | That node turns `NotReady` within about a minute. After about **5 minutes** (default toleration) its pods are evicted, and controllers recreate them elsewhere. |
| Container runtime on one node | Pods there stick in `ContainerCreating` or fail; the node may go `NotReady` |
| kube-proxy on one node | Existing Service rules keep working, but changes stop reaching that node |
| CNI plugin | New pods get no IP; nodes can go `NotReady` |
| CoreDNS | Service names stop resolving, so most apps break even though the pods are "Running" |

> **Docker link:** the kubelet calls containerd, which calls runc, the same chain as [Docker 02](../docker/02-architecture-internals.md). Kubernetes removed its Docker adapter (dockershim) in **1.24**, but Docker-built images still run because they're OCI images.

## Interview angle

- ⭐ "Explain Kubernetes architecture." → control plane (API server, etcd, scheduler, controller manager, cloud controller), nodes (kubelet, runtime, kube-proxy, CNI), add-ons (CoreDNS, metrics-server). Then say the key idea: **everything talks only to the API server, and every component is a watch-and-reconcile loop**.
- ⭐ "Which component talks to etcd?" → only the API server.
- ⭐ "What does the scheduler actually do?" → filter → score → bind. It only sets `spec.nodeName`; the kubelet starts the pod.
- "What happens if the control plane goes down?" → running workloads continue; nothing new happens.
- "Why an odd number of etcd members?" → quorum is a majority; an even number adds cost without adding fault tolerance.
- "Where does kube-proxy run, and what does it do?" → on every node; it programs the iptables or nftables rules that make Service IPs work. It is not in the packet path.
- "Is the kubelet a pod?" → no, a systemd service on the node. It runs the control plane itself as **static pods** on kubeadm clusters.
- "How do controllers avoid two copies acting at once?" → leader election through a `Lease` object.
- "What is the pause container?" → the pod sandbox; it holds the network namespace so the pod keeps its IP when app containers restart.
- "How does the control plane know a node is dead?" → the kubelet renews a `Lease` about every 10 seconds; when it stops, the node lifecycle controller marks the node `NotReady` and taints it, and pods are evicted after their 5-minute toleration.

## Practice 🖥️

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl describe node kind-control-plane
kubectl get --raw='/readyz?verbose'
kubectl get leases -n kube-system
kubectl get leases -n kube-node-lease
kubectl api-resources
kubectl get apiservices
```

- `/readyz?verbose` shows the API server's own health checks, including etcd.
- The `kube-system` leases show which scheduler and controller manager copy is the current leader; the `kube-node-lease` leases are the node heartbeats.
- `api-resources` lists every resource type the API server serves; `apiservices` shows which API groups are aggregated (look for `metrics.k8s.io`).

On a kind node (`docker exec -it kind-control-plane bash`), look at the layers below Kubernetes:

```bash
ls /etc/kubernetes/manifests   # static pods: the control plane itself
crictl ps                      # containers, as the runtime sees them
crictl pods                    # pod sandboxes
systemctl status kubelet       # the kubelet is a service, not a pod
```
