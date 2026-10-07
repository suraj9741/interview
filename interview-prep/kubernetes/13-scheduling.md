# 13 · Scheduling: Where Pods Run

## How the scheduler decides

For every pod with no node:
1. **Filter.** Drop nodes that can't run it:
   - not enough **unrequested** CPU or memory;
   - doesn't match `nodeSelector` or required affinity;
   - has a **taint** the pod doesn't tolerate;
   - the pod's **volume is in another zone**;
   - a port conflict.
2. **Score.** Rank the remaining nodes: spread pods out, balance resources, prefer nodes that already have the image, honour preferred affinity.
3. **Bind.** Write `spec.nodeName`. From then on, the kubelet on that node takes over ([04](04-kubectl-apply-flow.md)).

If no node passes the filter, the pod stays **Pending**, and `kubectl describe pod` shows why: for example, `0/3 nodes are available: 3 Insufficient cpu`.

## Choosing nodes: attract

| Tool | What it does |
|---|---|
| `nodeSelector` | Simple: only nodes with these labels (`disktype: ssd`) |
| **Node affinity** | Expressive rules (`In`, `NotIn`, `Exists`…). **Required** (`requiredDuringSchedulingIgnoredDuringExecution`) or **preferred** (with weights) |
| **Pod affinity** | "Put me **near** pods with label X" (same node or zone), for low latency |
| **Pod anti-affinity** | "Keep me **away** from pods with label X", for example spreading replicas across nodes |
| **Topology spread constraints** | Spread pods **evenly** across zones or nodes (`maxSkew`) |

"…IgnoredDuringExecution" means the rule is only checked **when the pod is scheduled**. Already-running pods aren't moved if labels change later.

## Keeping pods away: taints and tolerations

- A **taint on a node** repels pods: `key=value:Effect`.
- A **toleration on a pod** lets it **ignore** that taint. A toleration **allows** the pod onto the node; it doesn't **attract** it there.

| Effect | Meaning |
|---|---|
| `NoSchedule` | New pods without the toleration aren't scheduled here |
| `PreferNoSchedule` | Avoid if possible |
| `NoExecute` | Also **evicts** running pods that don't tolerate it |

- Built-in examples:
  - control plane nodes carry `node-role.kubernetes.io/control-plane:NoSchedule`;
  - unhealthy nodes get `node.kubernetes.io/not-ready:NoExecute` (pods tolerate it for **300 s** by default, then they're evicted).
- ⭐ **Dedicated nodes** (GPUs, a specific team): **taint** the nodes so others stay off, **and** add **node affinity** to the right pods so they go there. You need both.

```yaml
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: gpu
    effect: NoSchedule
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/arch
            operator: In
            values: ["amd64"]
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: api
          topologyKey: kubernetes.io/hostname
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: api
```

## Priority, preemption and eviction

- **PriorityClass:** pods with a higher `value` are scheduled first. If there's no room, the scheduler **preempts** (evicts) lower-priority pods. Built-in classes: `system-cluster-critical` and `system-node-critical`.
- **Node-pressure eviction:** when a node runs low on memory, disk or PIDs, the **kubelet** evicts pods, BestEffort first and Guaranteed last ([12](12-resources-and-autoscaling.md)). Evicted pods show `Evicted`.
- **API-initiated eviction:** `kubectl drain` evicts pods politely, **respecting PodDisruptionBudgets** ([07](07-workloads.md), [18](18-cluster-operations.md)).
- `kubectl cordon` marks a node unschedulable (existing pods stay). `spec.nodeName` set by hand skips the scheduler completely.

## Why a pod is Pending (from the `describe` events)

| Message | Fix |
|---|---|
| `Insufficient cpu` / `Insufficient memory` | Lower requests, add nodes (Cluster Autoscaler / Karpenter) |
| `node(s) had untolerated taint` | Add a toleration, or use other nodes |
| `didn't match Pod's node affinity/selector` | Fix the labels or the affinity |
| `volume node affinity conflict` | The volume is in another AZ: use `WaitForFirstConsumer` ([11](11-storage.md)) |
| `pod has unbound immediate PersistentVolumeClaims` | Fix the PVC or StorageClass |
| `didn't match pod anti-affinity rules` | Not enough nodes for "one per node": add nodes, or use *preferred* instead of *required* |

## Interview angle

- ⭐ "Taints vs affinity?" → taints repel pods from nodes (the node decides); affinity attracts pods to nodes (the pod decides). Use both for dedicated nodes.
- ⭐ "How do you spread replicas across availability zones?" → topology spread constraints on `topology.kubernetes.io/zone`, or pod anti-affinity.
- ⭐ "Why is a pod Pending?" → read the `describe` events, then use the table above.
- "What's preemption?" → evicting lower-priority pods to make room for higher-priority ones.

## Practice 🖥️

```bash
kubectl get nodes --show-labels
kubectl label node kind-control-plane disktype=ssd
kubectl taint nodes kind-control-plane dedicated=gpu:NoSchedule
kubectl taint nodes kind-control-plane dedicated=gpu:NoSchedule-
kubectl create priorityclass high --value=1000 --description="critical apps"
kubectl describe pod <pending-pod>
```

The `-` at the end of the second taint command removes the taint.
