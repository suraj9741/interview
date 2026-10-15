# 04 · The Drift Scenario (Hemant's A1) ⭐🔥

**The question:** `web` installed with `replicas: 3`. In an incident someone ran `kubectl edit deploy web` (replicas → 5) and added `team=x`. Next day CI runs `helm upgrade` with the **same** chart and values. What happens?

![How each Helm version updates an object that someone edited by hand](diagrams/02-helm-versions.drawio.svg)

Full version with every follow-up: [scenario deep dives, A1](../hemant-scenario-deep-dives.md).

## Answer in Hemant's 5 steps

| Step | Say |
|---|---|
| 1 · **Clarify** | "Which Helm version, and was the release created with 3 or 4? That decides client-side vs server-side apply." |
| 2 · **Mechanism** | "CSA: 3-way merge of OLD, LIVE, NEW. Replicas back to 3 (NEW ≠ LIVE); annotation stays (only in LIVE). SSA: `kubectl edit` took ownership of `replicas`, so the upgrade fails with a conflict." |
| 3 · **Options** | "`--force-conflicts` to take it back; put 5 in Git if it was right; stop templating replicas if an HPA should own it." |
| 4 · **Pick** | "If the incident showed we need 5, put 5 in values: no conflict, Git matches reality." |
| 5 · **Verify / prevent** | "Diff first, `managedFields` for the tool, audit logs for the person; prevent with GitOps self-heal and read-only prod access." |

## Each kind of hand edit (CSA, Helm 3 way)

| Changed by hand | Next upgrade, same chart | Why |
|---|---|---|
| Field the **chart sets** (replicas, image, limits) | **Reverted** | NEW ≠ LIVE |
| Something the chart **never set** (annotation, sidecar, env) | **Kept** | Only in LIVE |
| **Deleted** a field the chart sets | **Added back** | In NEW, not LIVE |
| **Chart removed** a field it used to set | **Deleted** | In OLD, not NEW. ⚠️ A whole removed block takes others' entries 🧪 |
| **Deleted the whole object** | **Recreated** | Missing |
| A **custom resource** | ⚠️ **Survives** unless the chart changed that field | 2-way merge (OLD vs NEW) |
| **HPA** changed replicas, chart sets `replicas:` | Reset every deploy, HPA scales back | Two owners. SSA: conflict 🧪 |

- **SSA (Helm 4)** differs only for fields someone else now owns: **conflict** instead of revert ([03](03-server-side-apply.md)).

## How to see the drift 🧪

| Check | What it shows |
|---|---|
| `helm get manifest web -n shop \| kubectl diff -n shop -f -` | Stored manifest vs LIVE: `- replicas: 5` / `+ replicas: 3`. Exit 0 = none, 1 = drift. ⚠️ `-n` required (manifest has no namespace) |
| `… \| kubectl diff -n shop --server-side --field-manager=helm -f -` | The SSA conflict Helm 4 will hit |
| `helm diff upgrade web ./demo -n shop -f values.yaml` | ⚠️ **Nothing**: OLD vs NEW only, blind to drift |
| `helm diff upgrade … --three-way-merge --detailed-exitcode` | Sees drift; exit **2** = changes → fail/flag CI |
| `--show-managed-fields` · EKS audit logs (CloudWatch) | **Who**: the tool (`kubectl-edit`, `Update`) · the person |

- helm-diff plugin on your laptop: v3.15.11.

## Prevent it

- **GitOps:** Argo CD `selfHeal: true` reverts drift in minutes.
- **RBAC:** view-only in prod; changes through PRs · **Break-glass:** time-limited, audited role.
- **After an incident:** put the emergency change in Git the same day.

## Practise it (10 minutes) 🖥️

Use the [practice cluster](README.md#your-own-practice-cluster-no-kind-needed-), never your work EKS.

```bash
helm create demo
helm install web ./demo -n shop --create-namespace --set fullnameOverride=web --set replicaCount=3
kubectl scale deploy web -n shop --replicas=5                                          # hand edit
helm upgrade web ./demo -n shop --set fullnameOverride=web --set replicaCount=3        # conflict
helm upgrade web ./demo -n shop --set fullnameOverride=web --set replicaCount=3 --force-conflicts   # back to 3
```
