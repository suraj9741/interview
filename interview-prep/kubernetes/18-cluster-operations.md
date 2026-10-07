# 18 · Cluster Operations: Nodes, Upgrades, Backups

## Node maintenance

| Command | Effect |
|---|---|
| `kubectl cordon <node>` | Mark the node **unschedulable**. Existing pods stay. |
| `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data` | Cordon, then **evict** every pod, **respecting PodDisruptionBudgets** ([07](07-workloads.md)). Controllers recreate the pods on other nodes. |
| `kubectl uncordon <node>` | Allow scheduling again |

- `--ignore-daemonsets`: DaemonSet pods can't move, so leave them.
- `--delete-emptydir-data`: confirms that losing `emptyDir` data is OK.
- A drain that **hangs** is usually waiting on a **PDB** that can't be satisfied (for example `minAvailable: 1` with only 1 replica).

## Kubernetes versions and upgrades ⭐

- About **3 minor releases a year**. Each gets roughly **14 months** of patches upstream.
- **On EKS:**
  - **standard support** is about **14 months** per version;
  - **extended support** gives about 12 more months **at extra cost**.

  Upgrade regularly so you don't fall behind.
- **Version skew rules:**
  - the **kubelet** may be up to **3 minor versions older** than the API server, never newer;
  - the controller manager and scheduler may be at most 1 older;
  - **kubectl** may be within **±1**.
- **Upgrade one minor version at a time** (1.34 → 1.35 → 1.36). You can't skip.

### Upgrade order (the same idea on kubeadm and EKS)

1. **Before you start:**
   - read the release notes;
   - **find deprecated or removed APIs** your manifests and Helm charts still use (`kubectl get --raw /metrics | grep apiserver_requested_deprecated_apis`, `pluto`, `kubent`, EKS upgrade insights);
   - back up (etcd or Velero);
   - check that PDBs exist.
2. **The control plane first:** API servers, then the controller manager and scheduler.
3. **Add-ons:** CoreDNS, kube-proxy, the CNI, CSI drivers (on EKS, the managed add-ons).
4. **The nodes, in a rolling way:**
   - **cordon and drain** each node, upgrade the kubelet (or replace the node with a new image), then uncordon;
   - on EKS: update the managed node group (it drains for you), or let Karpenter replace drifted nodes.
5. **Check:** nodes Ready, workloads healthy, no errors from deprecated APIs.

kubeadm commands: `kubeadm upgrade plan` → `kubeadm upgrade apply v1.x.y` on the first control plane node → `kubeadm upgrade node` on the others → upgrade the kubelet and kubectl packages on each node.

## etcd backup and restore (self-managed clusters)

```bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%F).db
etcdutl snapshot restore /backup/etcd-2026-10-05.db --data-dir /var/lib/etcd-restored
```

After restoring, point the etcd static pod at the new data directory.

- **On EKS you can't reach etcd**; AWS manages it. Back up **what you deploy** instead:
  - manifests in Git (GitOps);
  - **Velero** for Kubernetes objects plus volume snapshots;
  - database backups (RDS snapshots).

## Certificates (kubeadm)

- kubeadm certificates last **1 year**. Check them with `kubeadm certs check-expiration`, and renew with `kubeadm certs renew all` (a kubeadm upgrade also renews them).
- The kubelet rotates its own client certificate automatically.
- Expired certificates = a broken cluster. Alert on certificate expiry ([16](16-observability.md)).

## High-availability control plane

- **3 or more** control plane nodes behind a **load balancer** for the API server.
- etcd either **stacked** (on the control plane nodes) or **external** (separate machines). Always an **odd** number ([02](02-architecture.md)).
- Spread them across **availability zones**.

## kubeconfig and contexts ⚠️

- `~/.kube/config` holds **clusters**, **users** and **contexts** (a cluster + user + default namespace).
- `kubectl config get-contexts`, `kubectl config use-context kind-kind`, `kubectl config current-context`.
- ⚠️ **Always check the context before running a command.** Your Mac is currently pointed at an EKS cluster. Tools like `kubectx` / `kubens`, or showing the context in your shell prompt, prevent "oops, that was production".

## Interview angle

- ⭐ "How do you upgrade EKS with no downtime?" → check deprecated APIs → control plane (one minor) → add-ons → node groups rolling (drain, respecting PDBs), with several replicas and readiness probes in place.
- ⭐ "Cordon vs drain?" → stop new pods vs also evict the existing ones.
- "A drain never finishes. Why?" → a PDB blocks the eviction, or there are standalone pods (use `--force`) or `emptyDir` data.
- "How do you back up a cluster?" → etcd snapshots (self-managed), Velero, GitOps, and database backups.

## Practice 🖥️

```bash
kubectl cordon kind-control-plane
kubectl get nodes
kubectl drain kind-control-plane --ignore-daemonsets --delete-emptydir-data
kubectl uncordon kind-control-plane
kubectl config get-contexts
```

On a single-node kind cluster, the drain evicts your pods and they stay Pending until you uncordon. That shows why you need more than one node.
