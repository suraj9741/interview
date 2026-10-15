# 02 · How `helm upgrade` Changes Objects ⭐

![How each Helm version updates an object that someone edited by hand](diagrams/02-helm-versions.drawio.svg)

## Helm 2 vs 3 vs 4

| Version | How it updates objects | Inputs | A hand edit on a chart field… |
|---|---|---|---|
| **Helm 2** | 2-way merge (computed by Tiller in the cluster) | OLD vs NEW | …is **never fixed**: LIVE is ignored |
| **Helm 3** | 3-way strategic merge, computed by Helm = **CSA** | OLD + LIVE + NEW | …is **silently overwritten** |
| **Helm 4** | **Server-side apply (SSA)** for new installs | NEW, merged by the API server | …causes a **conflict** that you must resolve |

## CSA and SSA

**CSA = Client-Side Apply.** The merge happens in the **client**: the `helm` program on your laptop or CI runner.
1. Helm reads OLD (the manifest in the release Secret), LIVE (from the cluster) and NEW (the rendered chart).
2. Helm computes the 3-way patch **itself**.
3. Helm sends it as a normal **Update**.
4. The API server applies it **without checking who owns each field**.

**SSA = Server-Side Apply.** Helm sends the whole desired object as an **Apply**. The **API server** merges it and checks the owner of every field (`managedFields`). Details in [03](03-server-side-apply.md).

**How to tell them apart (tested 🧪):**
- The release Secret stores `apply_method: csa` or `ssa`.
- In `managedFields`, CSA Helm shows `helm / Update`, and SSA Helm shows `helm / Apply`.

**Not the same as `kubectl apply`:** client-side `kubectl apply` keeps its OLD in the `kubectl.kubernetes.io/last-applied-configuration` annotation. Helm doesn't use that annotation (the tested object had none); it keeps OLD in its release Secret.

**Helm 4 still uses CSA when:**
- you pass `--server-side=false`;
- you upgrade with `--server-side=auto` (the default) a release that was created with CSA, e.g. by Helm 3. It stays CSA until one upgrade with `--server-side=true`.

## What "3-way merge" really means

![3-way merge: two questions, so three inputs](diagrams/02-three-way-rules.drawio.svg)

**The job:** turn LIVE into what the chart wants, **without destroying changes made by other people and controllers**. Helm must answer **two questions**, and each needs a different pair of inputs:

| Question | Compare | Why this pair |
|---|---|---|
| What should I **set**? | **NEW vs LIVE** | Whatever the chart wants that the cluster doesn't have now |
| What should I **delete**? | **OLD vs NEW** | Only what **Helm** set last time and has now dropped. LIVE alone can't tell "mine, removed on purpose" from "someone else's" |

**Two questions → three inputs.** OLD is Helm's memory of what it set.

### The rules

1. **NEW ≠ LIVE → set it to NEW.** If NEW = LIVE, **nothing happens** (the field is left out of the patch).
2. **In OLD but not in NEW → delete it.** If it's already gone from LIVE, nothing happens.
3. **Only in LIVE → leave it alone.**

If NEW and LIVE match for the whole object, no change is sent and no pods restart, but Helm still records a new revision.

### Why "strategic"

For built-in types, Kubernetes knows how to merge **lists by a key**: containers by `name`, env vars by `name`, ports by `containerPort`. So an env var added with `kubectl set env` is **merged into** the list, not wiped out by replacing the whole list.

**Custom resources** (Karpenter NodePool, Argo CD Application, ServiceMonitor…) have no such information. Helm's source code (`pkg/kube/client.go`, `createPatch`) uses `CreateThreeWayMergePatch(old, new, live)` for built-in types, but a **2-way JSON merge (OLD vs NEW)** for custom resources. So a hand edit on a custom resource **survives** an upgrade, unless the chart changed that same field.

### Why not compare only two things?

| Approach | What goes wrong | Proof |
|---|---|---|
| **OLD vs NEW** (Helm 2) | Drift is never fixed: a Deployment scaled to 0 by hand stays at 0 | Helm's "Changes since Helm 2" page |
| **NEW vs LIVE** (make the cluster exactly the chart) | Everything others added is destroyed | 🧪 `--force-replace` wiped a hand-added annotation, an env var and `kubectl rollout restart`'s annotation in one go |

## Tested: one upgrade, five kinds of field 🧪

![Deletion works on whole blocks](diagrams/02-block-deletion.drawio.svg)

1. The chart set `replicas: 3` and a pod annotation `owner: helm-team`.
2. By hand: `kubectl edit` (replicas → 5), `kubectl annotate deploy … team=x`, `kubectl rollout restart` (adds a `restartedAt` pod annotation), `kubectl set env … DEBUG=true`.
3. `helm upgrade` with the same replicas, and `owner` **removed** from the chart.

![Tested: what happens to each field on helm upgrade](../diagrams/s5-helm-merge-cases.drawio.svg)

### ⚠️ The surprise: deletion works on whole blocks

`restartedAt` was **lost** with the 3-way merge, although Helm never set it.

- `owner` was the chart's **only** pod annotation. Removing it made the whole `annotations:` block disappear from NEW.
- The 3-way merge deletes **at the level where OLD and NEW differ**, so it deleted the **whole block**, `restartedAt` included. That also started a new rollout.
- I ran it again with the chart keeping one other annotation (`tier: web`). Then only `owner` was deleted, and `restartedAt` survived.
- Server-side apply kept `restartedAt` either way, because it tracks each field's owner (`kubectl-rollout`).

## Interview angle

- ⭐ **"What does a 3-way merge mean?"** → "Three inputs because there are two questions. NEW vs LIVE decides what to set, which fixes drift. OLD vs NEW decides what to delete, so Helm only removes what it set itself. Anything only in the cluster, like an injected sidecar or a hand-added annotation, is left alone."
  - **He'll push: "Any edge cases?"** → "Deletion happens at the level where OLD and NEW differ: dropping a whole annotations block also deletes annotations others added there. I saw `rollout restart`'s `restartedAt` disappear. And custom resources only get a 2-way merge."
- ⭐ **"Helm 2 vs 3 vs 4?"** → "Helm 2 compared old and new manifests only. Helm 3 added the live state and computes the patch itself: client-side apply, so the server never checks field ownership. Helm 4 uses server-side apply: the API server merges and enforces per-field owners. Existing releases keep their old method until you switch them."
- **"NEW and LIVE are the same: what happens?"** → Nothing for that field. With SSA, the same value means no conflict: the field gets two owners.
