# 03 · Objects and the API ⭐

## The shape of every manifest

```yaml
apiVersion: apps/v1          # API group/version
kind: Deployment             # object type
metadata:                    # identity
  name: web
  namespace: shop
  labels:
    app: web
  annotations:
    team: payments
spec:                        # DESIRED state: you write this
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
# status:                    # ACTUAL state: controllers write this, you never do
```

⭐ **`spec` vs `status`:** `spec` is what you want; `status` is what exists right now. Controllers keep working until `status` matches `spec`.

## API groups and versions

| apiVersion | Kinds |
|---|---|
| `v1` (the "core" group) | Pod, Service, ConfigMap, Secret, Namespace, ServiceAccount, PersistentVolume, PersistentVolumeClaim, Node |
| `apps/v1` | Deployment, ReplicaSet, StatefulSet, DaemonSet |
| `batch/v1` | Job, CronJob |
| `networking.k8s.io/v1` | Ingress, IngressClass, NetworkPolicy |
| `rbac.authorization.k8s.io/v1` | Role, ClusterRole, RoleBinding, ClusterRoleBinding |
| `storage.k8s.io/v1` | StorageClass |
| `autoscaling/v2` | HorizontalPodAutoscaler |
| `policy/v1` | PodDisruptionBudget |
| `gateway.networking.k8s.io/v1` | Gateway, HTTPRoute (installed as CRDs, see [09](09-ingress-and-gateway-api.md)) |

- Maturity goes **alpha → beta → stable (v1)**. Old beta APIs get **removed** in later versions, so check for deprecated APIs before every upgrade ([18](18-cluster-operations.md)).
- `kubectl api-resources` lists every type. `kubectl explain deployment.spec.strategy` documents any field, straight from the cluster.

## Namespaces

- A way to **group and isolate** objects in one cluster, by team, app or environment.
- Names only need to be unique **within** a namespace. RBAC, quotas and NetworkPolicies are usually set **per namespace**.
- Built-in namespaces:
  - `default`: where objects go if you don't choose;
  - `kube-system`: cluster components;
  - `kube-public`: readable by everyone;
  - `kube-node-lease`: node heartbeats.
- **Cluster-scoped** (no namespace): Nodes, PersistentVolumes, Namespaces, ClusterRoles, StorageClasses, CRDs.
- ⚠️ Namespaces are **not** a network or security boundary on their own. Add NetworkPolicy ([14](14-cluster-networking.md)) and RBAC ([15](15-security.md)).

## Labels and selectors ⭐ (the glue)

![Labels and selectors connect objects](diagrams/03-labels-selectors.drawio.svg)

- **Labels:** key-value pairs on any object (`app: web`, `env: prod`, `tier: backend`).
- **Selectors:** queries over labels.
  - **Equality-based:** `app=web`, `env!=dev`
  - **Set-based:** `env in (prod,staging)`
- **Who uses them:**
  - **Deployments and ReplicaSets** count the pods matching `selector.matchLabels`.
  - **Services** send traffic to the pods matching `selector`.
  - **NetworkPolicies** pick pods by label.
  - `kubectl get pods -l app=web`
- ⚠️ A Deployment's `selector` **can't be changed** after creation, and it must match the pod template's labels.
- Recommended labels: `app.kubernetes.io/name`, `app.kubernetes.io/version`, `app.kubernetes.io/part-of`.

## Annotations

- Also key-value pairs, but **not for selecting**. They store information **for tools and people**: an ingress controller's settings, a build commit, `prometheus.io/scrape`, a team contact.
- Rule of thumb: if you'd **filter by it**, make it a label; otherwise, an annotation.

## Owners, garbage collection and finalizers

![Owners and finalizers](diagrams/03-ownership-finalizers.drawio.svg)

- **Owner references:** a Deployment owns its ReplicaSets, which own their Pods (see `metadata.ownerReferences`).
- **Garbage collection:** delete the owner and its dependants are deleted too ("cascading"). Modes:
  - **background** (the default);
  - **foreground** (dependants first);
  - **orphan** (keep the dependants: `--cascade=orphan`).
- **Finalizers:** keys in `metadata.finalizers` that **block deletion** until a controller has cleaned up. Examples:
  - `kubernetes.io/pvc-protection` stops a PVC that's still in use from being deleted;
  - a load balancer controller removes the cloud load balancer first.
  - ⚠️ A namespace or object stuck in **`Terminating`** usually has a finalizer whose controller is gone.

## `kubectl apply` vs `create`, client-side vs server-side

- `create` fails if the object exists. `apply` creates **or** updates, by comparing with the last applied version.
- **Server-side apply** (`kubectl apply --server-side`): the API server tracks which tool owns which field (field managers), so tools can't silently overwrite each other's fields.

## Interview angle

- ⭐ "spec vs status?" → desired vs actual; controllers reconcile `status` towards `spec`.
- ⭐ "How does a Service know which pods to send traffic to?" → its label selector, which the EndpointSlice controller turns into a list of ready pod IPs ([08](08-services-and-dns.md)).
- "Labels vs annotations?" → labels are for selecting and grouping; annotations are non-identifying data for tools.
- ⭐ "A namespace is stuck in Terminating. Why?" → finalizers on it or on objects inside it, often a controller or CRD that has been removed. Find them with `kubectl get ns <ns> -o yaml`.
- "What happens when you delete a Deployment?" → garbage collection deletes its ReplicaSets and Pods, unless you use `--cascade=orphan`.

## Practice 🖥️

```bash
kubectl api-resources --namespaced=false
kubectl explain deployment.spec.strategy.rollingUpdate
kubectl get pods --show-labels
kubectl label pod <pod> tier=frontend
kubectl get pods -l 'app=web,tier in (frontend)'
kubectl annotate deployment web owner=team-a
kubectl get rs -o yaml | grep -A5 ownerReferences
```
