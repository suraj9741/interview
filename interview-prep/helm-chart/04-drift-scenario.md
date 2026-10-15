# 04 · The Drift Scenario (Hemant's A1) ⭐🔥

![How each Helm version updates an object that someone edited by hand](diagrams/02-helm-versions.drawio.svg)

**The question:** release `web` was installed with `replicas: 3`. During an incident someone ran `kubectl edit deploy web` (replicas → 5) and added an annotation `team=x`. Next day CI runs `helm upgrade` with the **same** chart and values. What happens?

The full version, with every follow-up, is in [the scenario deep dives, A1](../hemant-scenario-deep-dives.md). This page is the version to practise out loud.

## Answer in Hemant's 5 steps

| Step | Say |
|---|---|
| 1 · **Clarify** | "Which Helm version, and was the release created with Helm 3 or 4? That decides client-side vs server-side apply." |
| 2 · **Mechanism** | "With client-side apply, Helm builds a 3-way merge from the stored OLD manifest, the LIVE object and the NEW render. Replicas goes back to 3 because NEW ≠ LIVE. The annotation stays because it's only in LIVE. With server-side apply, `kubectl edit` took ownership of `replicas`, so the upgrade fails with a conflict." |
| 3 · **Options** | "`--force-conflicts` to take the field back; put 5 into Git if the change was right; or stop templating replicas if an HPA should own it." |
| 4 · **Pick** | "If the incident showed we need 5, I'd put 5 in the values file. Then the upgrade has no conflict and Git matches reality." |
| 5 · **Verify / prevent** | "Diff before upgrading, check `managedFields` for who changed it, the audit logs for the person, and prevent it with GitOps self-heal and read-only prod access." |

## What each kind of hand edit leads to (Helm 3 way, CSA)

| Changed by hand | Next upgrade, same chart | Why |
|---|---|---|
| A field the **chart sets** (replicas, image, limits) | **Reverted** | NEW ≠ LIVE |
| Something the chart **never set** (annotation, sidecar, extra env var) | **Kept** | Only in LIVE |
| **Deleted** a field the chart sets | **Added back** | In NEW, missing from LIVE |
| The **chart removed** a field it used to set | **Deleted** | In OLD, not in NEW. ⚠️ A whole removed block takes others' entries with it 🧪 |
| **Deleted the whole object** | **Recreated** | Helm finds it missing |
| A **custom resource** | ⚠️ **The edit survives**, unless the chart changed that field | Custom resources get a 2-way merge (OLD vs NEW) |
| An **HPA** changed replicas, and the chart sets `replicas:` | Every deploy resets replicas, then the HPA scales back | Two owners for one field. Under SSA it's a conflict 🧪 |

With **SSA (Helm 4)** the outcome is different only for fields someone else now owns: the upgrade **fails with a conflict** instead of reverting them ([03](03-server-side-apply.md)).

## How to see the drift 🧪

**1 · What drifted** (client-side view). `-n` is **required**: the manifest has no namespace, so without it the diff is made against `default`.

```bash
helm get manifest web -n shop | kubectl diff -n shop -f -
```

```
-  replicas: 5
+  replicas: 3
```

Exit code: 0 = no drift, 1 = drift.

**2 · What Helm 4 will hit** (a server-side dry run as Helm):

```bash
helm get manifest web -n shop | kubectl diff -n shop --server-side --field-manager=helm -f -
```

```
Error from server (Conflict): Apply failed with 1 conflict: conflict with "kubectl-edit" using apps/v1: .spec.replicas
```

**3 · Preview the upgrade with the helm-diff plugin** (installed on your laptop: v3.15.11). ⚠️ **By default it does NOT see drift.** It compares OLD vs NEW, Helm 2-style.

| Command | Result with live replicas = 5 |
|---|---|
| `helm diff upgrade web ./demo -n shop -f values.yaml` | **Nothing**, exit code 0 with `--detailed-exitcode` |
| `helm diff upgrade web ./demo -n shop -f values.yaml --three-way-merge` | `-   replicas: 5` / `+   replicas: 3`, exit code **2** with `--detailed-exitcode` |

So in CI, always use `--three-way-merge`, and `--detailed-exitcode` (2 = changes) to fail or flag a pipeline.

**4 · Who changed it:**
- `kubectl get deploy web -n shop -o yaml --show-managed-fields` shows the **tool** (`kubectl-edit`, operation `Update`).
- The EKS control plane **audit logs** (CloudWatch) show the **person**.

## How to prevent it

- **GitOps:** Argo CD with `selfHeal: true` reverts drift within minutes, not only at the next deploy.
- **RBAC:** people get **view** only in prod; changes go through pull requests.
- **Break-glass:** an emergency role that is time-limited and audited.
- **After an incident:** put the emergency change into Git the same day.

## Practise it (10 minutes) 🖥️

Use the [practice cluster](README.md#your-own-practice-cluster-no-kind-needed-), never your work EKS.

1. Make a chart:
   ```bash
   helm create demo
   ```
2. Install it:
   ```bash
   helm install web ./demo -n shop --create-namespace --set fullnameOverride=web --set replicaCount=3
   ```
3. Change it by hand:
   ```bash
   kubectl scale deploy web -n shop --replicas=5
   ```
4. Upgrade with the same values. You'll see the conflict:
   ```bash
   helm upgrade web ./demo -n shop --set fullnameOverride=web --set replicaCount=3
   ```
5. Take the field back, then check replicas is 3 again:
   ```bash
   helm upgrade web ./demo -n shop --set fullnameOverride=web --set replicaCount=3 --force-conflicts
   ```
