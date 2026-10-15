# 03 · Server-Side Apply (Helm 4) ⭐

![Helm 4 server-side apply: every field has an owner](../diagrams/s6-ssa-field-owners.drawio.svg)

- The API server records **who owns each field** in `metadata.managedFields`.
- **Helm 3 (CSA)** sends a plain **Update**: owners not checked. **Helm 4 (SSA)** sends an **Apply**: another owner on a field Helm wants to change = **refused**.

## See the owners 🧪

```bash
kubectl get deploy web -n shop -o yaml --show-managed-fields
# one-line summary
kubectl get deploy web -n shop --show-managed-fields -o jsonpath='{range .metadata.managedFields[*]}{.manager}/{.operation}{"  "}{end}'
```

After `helm install`, `kubectl edit` (replicas 3 → 5), `kubectl annotate team=x`:

| manager | operation | subresource | owns `replicas` | owns `team` |
|---|---|---|---|---|
| `helm` | **Apply** | – | **no** (lost it) | no |
| `kubectl-edit` | Update | – | **yes** | no |
| `kubectl-annotate` | Update | – | no | yes |
| `k3s` (controllers) | Update | status | no | no |

- Manager names: `kubectl-edit`, `kubectl` (`scale`, subresource `scale`), `kubectl-annotate`, `kubectl-rollout`, `kubectl-set`, `kubectl-autoscale`, the controller manager for the HPA (`k3s` here).

## The 5 rules 🧪

| # | Rule | Seen in the lab |
|---|---|---|
| 1 | You own **only fields you send**; others are never touched | `team=x` survived every upgrade, even `--force-conflicts` |
| 2 | A normal write that **changes** a value **takes the owner tag** | After `kubectl edit`, Helm no longer owned `replicas` |
| 3 | Applying a **different value** to another's field = **conflict** | `conflict with "kubectl-edit"`; `"kubectl" with subresource "scale"`; HPA: `"k3s" with subresource "scale"` |
| 4 | **Only owner stops sending** a field → it's **deleted** | `replicas` 3 → 1 (HPA case below) |
| 5 | **Same value** = no conflict, two owners | (Kubernetes docs; not run) |

## The conflict (Helm 4.2.3) 🧪

```
Error: UPGRADE FAILED: conflict occurred while applying object shop/web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-edit" using apps/v1: .spec.replicas
```

- Nothing changes (replicas **stays 5**); `helm history` shows the revision **`failed`** with this message.
- Same test with `--server-side=false`: `deployed`, replicas **silently** 5 → 3.

| Choice | Do | When |
|---|---|---|
| **Take it back** | `--force-conflicts` | The edit was a mistake / emergency over. 🧪 Back to 3, `kubectl-edit` entry gone |
| **Keep it** | Put the value in the values file | The edit was right. Same value = no conflict |
| **Give it away** | Stop setting the field | Something else (an HPA) should own it. ⚠️ Hand over first (rule 4) |

- 🎯 CI that **always** passes `--force-conflicts` = Helm 3's silent overwrite again. Let CI fail; a person decides.
- **Preview 🧪:** `helm get manifest web -n shop | kubectl diff -n shop --server-side --field-manager=helm -f -` → `Error from server (Conflict): … conflict with "kubectl-edit" … .spec.replicas`.

## How Helm picks CSA or SSA 🧪

![How Helm 4 picks server-side or client-side apply](diagrams/03-csa-or-ssa.drawio.svg)

## The HPA case, end to end 🧪

![Moving replicas from Helm to an HPA](diagrams/03-hpa-handover.drawio.svg)

1. **The fight:** an HPA (`minReplicas: 4`) scaled 3 → 4 and took the tag. Next upgrade: `conflict with "k3s" with subresource "scale" using apps/v1: .spec.replicas`.
2. **The fix:** `autoscaling.enabled=true` (`helm create` charts then **stop templating `replicas`** and create the HPA). A `kubectl autoscale` HPA already existed:
   - no flags → `… exists and cannot be imported into the current release: invalid ownership metadata`
   - `--take-ownership` → `conflict with "kubectl-autoscale" using autoscaling/v2: .spec.maxReplicas`
   - **`--take-ownership --force-conflicts`** → ✅ adopted (`managed-by=Helm`), later upgrades need no flags, replicas stayed 4.
3. **The trap:** on a fresh release where Helm **alone** owned `replicas`, enabling autoscaling deleted the field → `Scaled down replica set web4-… from 3 to 1`, then ~15 s later `New size: 4; reason: Current number of replicas below Spec.MinReplicas`.

👉 `--take-ownership` skips only Helm's label check; the server's field owners still apply.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ What changes in Helm 4? | "New releases use SSA. A hand edit makes `kubectl-edit` the owner, so the next upgrade fails with a conflict instead of silently overwriting. Old releases keep CSA via `--server-side=auto`." |
| ↳ What do you do with the conflict? | Take it back, keep it in values, or give it away: the choice table. |
| `--take-ownership` vs `--force-conflicts`? | Adopt objects without Helm labels vs override other owners' fields. A hand-edited object can need both. |
| Moving a Deployment to an HPA: risk? | If Helm alone owns `replicas` and stops sending it, it's deleted → 1 replica until the HPA reacts. Let the HPA own it first. |
