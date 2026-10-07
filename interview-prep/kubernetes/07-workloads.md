# 07 · Workloads: Deployments, StatefulSets, DaemonSets, Jobs ⭐

## Which controller do I use?

| Controller | Use it for | Key behaviour |
|---|---|---|
| **Deployment** | Stateless apps (APIs, web) | Manages ReplicaSets; rolling updates and rollback |
| **ReplicaSet** | (Don't use directly) | Keeps N identical pods running; Deployments create them for you |
| **StatefulSet** | Databases, Kafka, ZooKeeper | Stable names (`db-0`, `db-1`), its own disk per pod, ordered start and stop |
| **DaemonSet** | One pod per node: log collectors, node exporters, CNI agents, kube-proxy | New nodes get a copy automatically |
| **Job** | Run to completion: migrations, batch work | Retries failures; `completions` and `parallelism` |
| **CronJob** | Scheduled Jobs: backups, reports | Cron schedule; creates a Job each time |

## Deployments and rolling updates ⭐

![Rolling update: Deployment, ReplicaSets, Pods](diagrams/07-deployment-rollout.drawio.svg)

- Changing the pod **template** (for example, the image) creates a **new ReplicaSet**. The Deployment **scales the new one up** and **the old one down**, a few pods at a time.
- `strategy.rollingUpdate` settings:
  - `maxSurge` (default 25%): how many **extra** pods may exist during the update.
  - `maxUnavailable` (default 25%): how many may be **missing**.
  - **For zero downtime:** `maxUnavailable: 0`, `maxSurge: 1`, plus readiness probes.
- `strategy.type: Recreate` kills all old pods first (there's downtime). Use it when two versions can't run together.
- **Rollback:** old ReplicaSets are kept (`revisionHistoryLimit`, default 10). `kubectl rollout undo` scales the previous one back up.
- `minReadySeconds`: a pod must stay Ready this long before it counts as available.
- `progressDeadlineSeconds` (600): after this, the rollout is marked failed. It **doesn't** roll back by itself.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  revisionHistoryLimit: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myapi:1.4.2
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            memory: 256Mi
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
```

## StatefulSets

- **Stable identity:** pods are named `<name>-0`, `<name>-1`… and keep their name and **their own PVC** when rescheduled.
- **Needs a headless Service** (`serviceName`), which gives each pod its own DNS name, for example `db-0.db.default.svc.cluster.local` ([08](08-services-and-dns.md)).
- **Ordered:** pods are created 0 → 1 → 2 and deleted in reverse (`podManagementPolicy: OrderedReady`; use `Parallel` to skip the ordering).
- **`volumeClaimTemplates`:** one PVC per pod. **PVCs are kept** when the StatefulSet is deleted or scaled down, to protect the data ([11](11-storage.md)).
- Rolling updates go from the highest number to the lowest. `partition` lets you update only some pods (a canary).

## DaemonSets

- One pod on every node, or on the nodes matching `nodeSelector` or affinity.
- To run on control plane nodes too, add a **toleration** for their taint ([13](13-scheduling.md)).

## Jobs and CronJobs

| Field | Meaning |
|---|---|
| `completions` | How many successful pods are needed |
| `parallelism` | How many pods run at once |
| `backoffLimit` (6) | Retries before the Job is marked failed |
| `activeDeadlineSeconds` | A time limit for the whole Job |
| `ttlSecondsAfterFinished` | Delete the finished Job automatically after N seconds |
| CronJob `schedule` | Cron format, for example `"0 2 * * *"` = 02:00 every day (use `timeZone` to set the zone) |
| CronJob `concurrencyPolicy` | `Allow` / `Forbid` (skip if the last run is still going) / `Replace` |

## PodDisruptionBudget (PDB)

- Protects availability during **voluntary** disruptions: `kubectl drain`, node upgrades, Karpenter consolidation.
- Set `minAvailable: 2` or `maxUnavailable: 1` for the pods matching a selector. A drain then **waits** instead of evicting too many at once.
- It **doesn't** protect against **involuntary** disruptions, such as a node crash.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api
```

> **Docker link:** `docker run --restart always` only restarts a container on the same host. A Deployment keeps the **count** right **anywhere in the cluster** ([Docker 11](../docker/11-production.md)).

## Interview angle

- ⭐ "Deployment vs StatefulSet?" → interchangeable stateless pods vs stable name, own disk per pod and ordering.
- ⭐ "How does a rolling update work, and how do you roll back?" → a new ReplicaSet scales up and the old one scales down, following `maxSurge`/`maxUnavailable`; `rollout undo` scales the old ReplicaSet back.
- ⭐ "How do you get zero-downtime deploys?" → several replicas, readiness probes, `maxUnavailable: 0`, a `preStop` sleep plus SIGTERM handling ([05](05-pods.md)), and a PDB.
- "When would you use a DaemonSet?" → node-level agents: logs, metrics, networking.
- "What does a PDB do?" → it limits how many pods a drain or upgrade can take down at once.

## Practice 🖥️

```bash
kubectl create deployment web --image=nginx:1.26 --replicas=3
kubectl set image deployment/web nginx=nginx:1.27
kubectl rollout status deployment/web
kubectl rollout history deployment/web
kubectl get rs
kubectl rollout undo deployment/web
kubectl create job hello --image=busybox:1.36 -- echo hello
kubectl create cronjob tick --image=busybox:1.36 --schedule="*/1 * * * *" -- date
```
