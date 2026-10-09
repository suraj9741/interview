# Hemant's Scenario Deep Dives ⭐🔥

**Why this file exists:** while talking to Hemant on 7 Oct, he said the interview will be **scenario-based**. He named three examples:
1. **Helm drift:** a release was installed with Helm, then someone edited the objects in the cluster. What happens on the next `helm upgrade`?
2. **Overlapping VPC CIDRs:** two clusters in two VPCs with the same IP range. How do you connect them, and what options are there?
3. **Node CIDR ≠ pod CIDR:** nodes have IPs from one range and pods from another. Which technique is that, and how does it work? He pointed to One2N's blog post [Why Your EKS Auto Mode NodeClass Keeps Reverting to Default](https://one2n.io/blog/eks-auto-mode-nodeclass-reverting-to-default) (21 Sep 2026).

Part A goes deep on these three. Part B has 20 more scenarios **in the same style** across Docker, Kubernetes, AWS, CI/CD and security.

---

## How he asks, and how to answer ⭐

He gives a situation, then keeps pushing: **"What happens?" → "Why?" → "What else could you do?" → "Which would you pick?" → "How would you check?"**

Answer every scenario in **5 steps**:

| Step | What you say | Example (overlapping CIDRs) |
|---|---|---|
| 1. **Clarify** | 1–2 short questions | "Which way does traffic go, and is it a few HTTP services or everything?" |
| 2. **Mechanism** | What really happens underneath | "In each VPC, the local route always wins, so 10.0.x.x never leaves the VPC." |
| 3. **Options** | 2–4 options, each with its trade-off | Lattice · PrivateLink · private NAT + TGW · re-IP |
| 4. **Pick one** | Your choice and **why** | "A few HTTP APIs → VPC Lattice: no network changes." |
| 5. **Verify / prevent** | How you'd prove it works, and stop it happening again | "Test from a pod; use IPAM so new VPCs never overlap." |

### The one idea behind all three of his scenarios: *who owns this?*

- **Helm drift:** Helm and a human (`kubectl edit`) both claim the same field.
- **One2N's NodeClass bug:** Argo CD and EKS Auto Mode both claim the same object.
- **Overlapping CIDRs:** VPC A and VPC B both claim the same IP addresses.
- **Node vs pod CIDR:** you deliberately give nodes and pods **separate** address space, so they don't compete for IPs.

When something "keeps changing back" or "can't be reached," ask: **who else owns this?** There's a full table of these fights at the [end of Part A](#the-two-owners-pattern-).

---

# Part A: the three scenarios he named

## A1 · Helm drift: someone edited the cluster, then we run `helm upgrade` again ⭐🔥

> Everything about Helm, in study order, is also in the [Helm notes](helm-chart/README.md). The short practise-out-loud version of this scenario is [Helm 04](helm-chart/04-drift-scenario.md).

![Helm 3-way merge](diagrams/s1-helm-three-way-merge.drawio.svg)

**The scenario:**
- Release `web` was installed with `helm upgrade --install web ./chart -n shop`. It's on revision 3, with `replicas: 3` in the chart.
- During an incident, someone ran `kubectl edit deploy web`: replicas 3 → 5, and they added an annotation `team=x`.
- Next day, CI runs `helm upgrade` again with the **same** chart and values. What happens?

### Say this first (30 seconds)

> "It depends on what was edited and how Helm applies changes.
>
> With **Helm 3** (client-side apply), `helm upgrade` builds a **3-way merge patch** from three things: the **old manifest** stored in the release, the **live object** in the cluster, and the **new manifest** from the chart.
> - Any field the **chart sets** goes back to the chart's value. So replicas goes 5 → 3, **even though the chart didn't change**.
> - Anything the chart **doesn't set**, like that annotation or a sidecar injected by Istio, is **left alone**.
>
> Helm doesn't watch the cluster, so the drift stays until someone runs Helm again.
>
> On **Helm 4**, new releases use **server-side apply**. `kubectl edit` makes kubectl the owner of that field, so the upgrade **fails with a conflict** unless you pass `--force-conflicts`.
>
> The real fix is to make Git the only way to change prod: GitOps with self-heal, and no edit rights for people."

### What each kind of edit leads to (Helm 3, client-side)

| What was changed by hand | Next `helm upgrade` (same chart) | Why |
|---|---|---|
| A field the **chart sets** (replicas, image, env value, limits) | **Reverted** to the chart's value | NEW ≠ LIVE, so the patch sets it |
| Something the chart **never set** (an extra annotation or label, an injected sidecar, an extra env var) | **Kept** | It's only in LIVE, and the patch leaves LIVE-only fields alone |
| **Deleted** a field the chart sets | **Added back** | It's in NEW but missing from LIVE |
| The **chart removed** a field it used to set | **Deleted** from the cluster | It's in OLD but not in NEW. ⚠️ If a whole block disappears from the chart (e.g. all pod annotations), the whole block is deleted, **including entries others added** (tested, see below) |
| **Deleted the whole object** (`kubectl delete deploy web`) | **Recreated** (Helm logs "Created a new Deployment") | Helm finds it missing and creates it. Until then it's gone, and so are its pods. |
| Edited a **custom resource** (a Karpenter NodePool, ServiceMonitor, Argo CD Application…) | ⚠️ **The edit survives**, unless the chart changed that same field | Strategic merge doesn't work on custom resources, so Helm falls back to a **2-way JSON merge (OLD vs NEW only)** and never looks at LIVE |
| **HPA** changed replicas (not a person), and the chart sets `replicas:` | **Every deploy resets replicas** to the chart value, then the HPA scales back up | Two owners for one field. Don't template `replicas` when autoscaling is on; `helm create` already wraps it in `{{- if not .Values.autoscaling.enabled }}`. |

> I checked the custom-resource row in Helm's source code (`pkg/kube/client.go`, `createPatch`). Built-in types use `CreateThreeWayMergePatch(old, new, live)`. Custom resources use `CreateMergePatch(old, new)` during an upgrade. Few candidates know this; mention it as "one subtle thing…".

### Why the 3-way merge exists (the deep "why")

- **Helm 2** compared only **OLD vs NEW**. If someone scaled a Deployment to 0 by hand, a rollback did **nothing**: old and new manifests were the same, so Helm saw "no change."
- **Helm 3** added the **live state** as a third input. Now that rollback notices replicas is 0 and fixes it.
- The **sidecar case** goes the other way. A service mesh injects a container into the live pod spec. Helm 3 keeps it, because the chart never owned it.
- (Both examples are from Helm's own ["Changes since Helm 2"](https://helm.sh/docs/faq/changes_since_helm2/) page.)

### Helm 2 vs 3 vs 4, and what CSA and SSA mean ⭐

| Version | How it updates objects | Inputs |
|---|---|---|
| **Helm 2** | 2-way merge | OLD vs NEW. It ignores the cluster, so live drift is never fixed |
| **Helm 3** | 3-way strategic merge patch, computed by Helm (**CSA**) | OLD + LIVE + NEW. Custom resources get a 2-way JSON merge (OLD vs NEW) |
| **Helm 4** | **Server-side apply (SSA)** for new installs | The API server merges, using an owner per field (`managedFields`) |

**CSA = Client-Side Apply.** The merge happens in the **client**: the `helm` program on your laptop or CI runner.
1. Helm reads OLD (the manifest in the release Secret), LIVE (fetched from the cluster) and NEW (the rendered chart).
2. Helm computes the 3-way strategic merge patch **itself**.
3. Helm sends it to the API server as a normal **Update**.
4. The API server applies it **without checking who owns each field**. So hand edits on fields the chart sets are **silently overwritten**.

**SSA = Server-Side Apply.** Helm sends the whole desired object as an **Apply**. The **API server** does the merge and checks `managedFields`. A different value on a field another owner holds gives a **conflict**.

**How to tell them apart (tested):**
- The release Secret stores `apply_method: csa` or `ssa`.
- In `managedFields`, CSA Helm shows `helm / Update`, and SSA Helm shows `helm / Apply`.

**Not the same as `kubectl apply`:**
- Client-side `kubectl apply` keeps its OLD in the `kubectl.kubernetes.io/last-applied-configuration` annotation.
- Helm CSA doesn't use that annotation (the lab object had none). Helm keeps OLD in its release Secret.

**When Helm 4 still uses CSA:**
- `--server-side=false`;
- `--server-side=auto` (the upgrade default) on a release that was created with CSA, e.g. by Helm 3.
- It stays CSA until one upgrade with `--server-side=true`.

> **Say it:** "Helm 2 compared the old and new manifests. Helm 3 added the live state: a 3-way merge that Helm computes itself and sends as a plain update. That's client-side apply, so the server never checks field ownership. Helm 4 uses server-side apply: the API server merges and enforces per-field owners. Existing releases keep their old method until you switch them."

### What "3-way merge" actually means ⭐ (tested)

**The job:** turn the live object into what the chart wants, **without destroying changes made by other people and controllers**. To do that, Helm must answer **two questions**, and each one needs a different pair of inputs:

| Question | Compare | Why this pair |
|---|---|---|
| What should I **set**? | **NEW vs LIVE** | Whatever the chart wants that the cluster doesn't have right now |
| What should I **delete**? | **OLD vs NEW** | Only what **Helm itself** set last time and has now removed. LIVE alone can't tell "mine, removed on purpose" from "someone else's" |

**Three inputs, because there are two questions.** OLD is Helm's memory of what it set, kept in the release Secret.

- **The patch** = the "set" part (NEW vs LIVE) + the "delete" part (OLD vs NEW), sent as **one** patch.
- **The 3 rules:**
  1. NEW ≠ LIVE → set it to NEW. (NEW = LIVE → **nothing**: the field is left out of the patch.)
  2. In OLD but not in NEW → delete it.
  3. Only in LIVE → leave it alone.
- **If NEW and LIVE match for the whole object:** no change is sent and no pods restart, but Helm still records a new revision.
- **Why "strategic":** for built-in types, Kubernetes knows how to merge **lists by a key**: containers by `name`, env vars by `name`, ports by `containerPort`. So an env var added with `kubectl set env` is **merged into** the list, not wiped by replacing the whole list. Custom resources have no such information, so Helm falls back to a plain JSON merge (the custom-resource row in the table above).

**Why not a 2-way comparison?**
- **OLD vs NEW only** (Helm 2): live drift is never fixed. A Deployment scaled to 0 by hand stays at 0.
- **NEW vs LIVE only** ("make the cluster exactly match the chart"): everything others added is destroyed. That's what `--force-replace` does. Tested: it wiped the hand-added annotation, the env var and `kubectl rollout restart`'s annotation in one go.

**Tested: one upgrade, five kinds of field** (Helm 4.2.3, Kubernetes 1.34, k3s in Docker, 8 Oct 2026):

1. The chart set `replicas: 3` and a pod annotation `owner: helm-team`.
2. Then, by hand: `kubectl edit` (replicas → 5), `kubectl annotate deploy … team=x`, `kubectl rollout restart` (it adds a `restartedAt` pod annotation), and `kubectl set env … DEBUG=true`.
3. Then `helm upgrade` with the same replicas and the `owner` annotation **removed** from the chart.

![Tested: what happens to each field on helm upgrade](diagrams/s5-helm-merge-cases.drawio.svg)

**The surprise ⚠️:** `restartedAt` was **lost** with the 3-way merge, even though Helm never set it.
- The chart's **only** pod annotation was `owner`. Removing it made the whole `annotations:` block vanish from NEW.
- The 3-way merge deletes **at the level where OLD and NEW differ**, so it deleted the **whole block**, `restartedAt` included. That also triggers a new rollout.
- I ran it again with the chart keeping one other pod annotation (`tier: web`). Then only `owner` was deleted, and `restartedAt` survived.
- Server-side apply kept it either way, because it tracks each field's owner (`kubectl-rollout`) instead of comparing blocks.

> **Say it in one line:** "A 3-way merge sets whatever NEW wants that LIVE lacks, deletes only what OLD had and NEW dropped, and leaves fields that exist only in LIVE alone. That's how it fixes drift without destroying sidecars or other people's annotations."

### Helm 4: server-side apply, tested ⭐ (current: 4.3; your laptop has **v4.2.3**)

![Helm 4 server-side apply: every field has an owner](diagrams/s6-ssa-field-owners.drawio.svg)

**The idea: every field carries a name tag.** The API server records **who owns each field** in `metadata.managedFields`.
- **Helm 3** never looks at the tags: it builds the patch itself and sends a normal **Update**, which the server doesn't check.
- **Helm 4** sends an **Apply**, and the server **checks the tags**. If another owner holds a field Helm wants to change, the server refuses.

**The tags, for real**, after `helm install`, then `kubectl edit` (replicas 3 → 5) and `kubectl annotate team=x`. `kubectl` hides them unless you add `--show-managed-fields`.

| manager | operation | subresource | owns `replicas` | owns `team` |
|---|---|---|---|---|
| `helm` | **Apply** | – | **no** (lost it) | no |
| `kubectl-edit` | Update | – | **yes** | no |
| `kubectl-annotate` | Update | – | no | yes |
| `k3s` (the controllers) | Update | status | no | no |

**The rules, each one seen in the lab:**

| # | Rule | Seen |
|---|---|---|
| 1 | You own **only the fields you send**. Others' fields are never touched. | `team=x` survived every upgrade, even `--force-conflicts` |
| 2 | A normal write that **changes** a value **takes the tag** silently | After `kubectl edit`, Helm no longer owned `replicas` |
| 3 | Applying a **different value** to someone else's field = **conflict** | `conflict with "kubectl-edit"`, `conflict with "kubectl" with subresource "scale"`, and, from an HPA, `conflict with "k3s" with subresource "scale"` |
| 4 | If the **only owner stops sending** a field, it is **deleted** | `replicas` 3 → 1 (below) |
| 5 | The **same value** = no conflict; the tag becomes shared | (Kubernetes docs) |

**Helm 3 way vs Helm 4 way, same story** (install replicas 3 → `kubectl edit` to 5 → `helm upgrade` with the same values):

| | `--server-side=false` (the Helm 3 way) | Default for new installs (server-side) |
|---|---|---|
| Helm's tag | `helm` / Update | `helm` / **Apply** |
| `helm upgrade` | ✅ `deployed`; replicas **silently 5 → 3** | ❌ `Error: UPGRADE FAILED: conflict occurred while applying object shop/web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-edit" using apps/v1: .spec.replicas`; replicas **stay 5** |
| `helm history` | A normal new revision | The revision is marked **`failed`**, with that message |

**How `--server-side=auto` decides:** each release Secret stores **`apply_method`**. I decoded them: `ssa` for the server-side release and `csa` for the client-side one. `auto` (the default for upgrades) reuses the previous revision's method. That's why releases created by Helm 3 keep the 3-way merge until one upgrade with `--server-side=true`.

**When it conflicts, choose; don't just force:**

| Choice | Do | When |
|---|---|---|
| Take it back | `--force-conflicts` | The edit was a mistake, or an emergency that's over. Tested: replicas → 3, and the `kubectl-edit` entry disappeared. |
| Keep it | Put the value in the values file | The edit was right. Same value = no conflict. |
| Give it away | Stop setting the field in the chart | Something else owns it (an HPA). ⚠️ Hand it over first (rule 4). |

🎯 If CI **always** passes `--force-conflicts`, the protection is switched off and you're back to Helm 3's silent overwrite. Better: let CI fail, and have a person decide.

**The HPA case, end to end (tested):**

1. An HPA (`minReplicas: 4`) scaled the Deployment from 3 to 4 and took the tag (`k3s / Update / scale`; on EKS it's the controller manager). The next `helm upgrade` failed with a conflict on `.spec.replicas`.
2. **Fix:** set `autoscaling.enabled=true` in the chart. `helm create` charts then **stop templating `replicas`** and create the HPA themselves. But an HPA made with `kubectl autoscale` already existed:
   - with no flags: `HorizontalPodAutoscaler "web" … exists and cannot be imported into the current release: invalid ownership metadata`;
   - with `--take-ownership`: that check passed, then `conflict with "kubectl-autoscale" … .spec.maxReplicas`;
   - with **`--take-ownership --force-conflicts`**: ✅ adopted. Later upgrades worked with no flags, and replicas stayed 4.
   - 👉 **`--take-ownership` skips only Helm's label check. The server's field tags still apply.**
3. **⚠️ The trap.** On a release where **Helm alone** owned `replicas`, switching to autoscaling deleted the field (rule 4). Events: `Scaled down replica set … from 3 to 1`, then about 15 seconds later `New size: 4; reason: Current number of replicas below Spec.MinReplicas`. In step 2 the HPA **already** owned the field, so nothing dropped. **Let the HPA own `replicas` first, then remove it from the chart.** The Kubernetes docs call this "transferring ownership".

**Renamed flags** (checked in `helm upgrade --help`, v4.2.3):
- `--force` → `--force-replace` (overwrites the object with NEW; every hand-made change is lost, as in the s5 diagram);
- `--atomic` → `--rollback-on-failure`;
- new: `--server-side true|false|auto`, `--force-conflicts`, and `--take-ownership` (adopts objects that lack Helm's labels).

### How to *see* the drift

```bash
# Diff what Helm thinks it deployed against what is live (exit code 1 = there is drift).
# -n is required: the manifest has no namespace, so without it the diff is made against "default".
helm get manifest web -n shop | kubectl diff -n shop -f -

# Helm 4 (server-side apply) preview: shows the exact conflict the next upgrade will hit
helm get manifest web -n shop | kubectl diff -n shop --server-side --field-manager=helm -f -

# Who changed it, and when? Look for manager "kubectl-edit" with operation "Update"
kubectl get deploy web -n shop -o yaml --show-managed-fields

# Preview an upgrade against the LIVE objects (needs the helm-diff plugin)
helm diff upgrade web ./chart -n shop -f values-prod.yaml --three-way-merge
```

The **person** behind the change is in the EKS control plane **audit logs** (CloudWatch).

### Follow-ups he's likely to ask

- **"How do you stop this happening?"**
  - **GitOps:** Argo CD with `selfHeal: true` reverts drift within minutes, not just at the next deploy.
  - **RBAC:** people get **view** only in prod; changes go through PRs.
  - A **break-glass** role for emergencies, time-limited and audited.
- **"Where does Helm keep the OLD manifest?"**
  - In a **Secret** in the release namespace, named `sh.helm.release.v1.<release>.v<revision>`.
  - It holds the chart, values and rendered manifest, gzipped and base64-encoded.
  - `--history-max` (default 10) limits how many revisions are kept.
  - Anyone who can read Secrets there can read your values.
- **"CI says: `another operation (install/upgrade/rollback) is in progress`."**
  - The previous `helm upgrade` was killed half-way (a cancelled CI job), so the release is stuck in `pending-upgrade`.
  - Fix: `helm history web` → `helm rollback web <last good revision>`.
  - Prevent: a CI **concurrency group** for deploys, and don't cancel running deploy jobs.
- **"`helm install` fails: resource already exists… invalid ownership metadata."**
  - The object was created outside Helm.
  - Adopt it: add the label `app.kubernetes.io/managed-by=Helm` and the annotations `meta.helm.sh/release-name` and `meta.helm.sh/release-namespace`, or use `--take-ownership`.
- **"After an EKS upgrade, `helm upgrade` fails with `no matches for kind PodDisruptionBudget in version policy/v1beta1`."**
  - The **OLD manifest stored in the release** uses an API the cluster removed, so Helm can't build the patch.
  - Fix: the `helm mapkubeapis` plugin rewrites the stored manifest.
  - Prevent: check for deprecated APIs **before** upgrading (pluto, kubent, EKS upgrade insights).
- **"Argo CD + Helm: same behaviour?"**
  - No. Argo CD **renders** the chart (like `helm template`) and applies it itself, so `helm list` shows nothing.
  - Drift is fixed **continuously** by self-heal.
  - For the HPA problem, use `ignoreDifferences` on `/spec/replicas`, or don't set replicas.
- **"`kubectl rollout undo` in prod, is that OK?"**
  - It works, but now **Git, Helm and the cluster all disagree**: the next deploy brings the bad version back.
  - Roll back through the same tool that deployed: `git revert` (GitOps) or `helm rollback`.

### Try it yourself (5 minutes, on a **local** cluster only) 🖥️

```bash
# 1. Make sure you are NOT on your work EKS cluster
kubectl config current-context

# 2. Install a release, then change it by hand two ways
helm create demo
helm install demo ./demo --set replicaCount=2
kubectl scale deploy demo --replicas=5
kubectl annotate deploy demo team=x

# 3. Upgrade with the SAME values, then check replicas and the annotation
helm upgrade demo ./demo --set replicaCount=2
kubectl get deploy demo -o jsonpath='{.spec.replicas} {.metadata.annotations.team}{"\n"}'
```

- **Step 1** must print `kind-…` or `docker-desktop`.
- **What you should see in step 3:**
  - With Helm 3 behaviour you get `2 x`: replicas reverted, annotation kept.
  - Your Helm is v4, so this new install uses server-side apply, and the upgrade **stops with a conflict** instead (tested on 8 Oct with Helm 4.2.3: `conflict with "kubectl" with subresource "scale" … .spec.replicas`). Re-run it with `--force-conflicts` and you'll see replicas go back to 2.
  - Seeing both behaviours yourself is the best preparation for this question.

---

## A2 · Two clusters, two VPCs, overlapping CIDRs: how do you connect them? ⭐🔥

![Overlapping CIDR with private NAT and Transit Gateway](diagrams/s2-overlapping-cidr-private-nat.drawio.svg)

**The scenario:** cluster A runs in VPC A (`10.0.0.0/16`) and cluster B in VPC B, **also `10.0.0.0/16`** (both made from the same template). A service in A must call an API in B.

### Clarify first (this alone impresses)

1. **What exactly overlaps?**
   - With the **VPC CNI**, pod IPs come from the VPC, so a VPC overlap means **node and pod IPs overlap**.
   - Overlapping **Service CIDRs** (ClusterIPs) **don't matter**: ClusterIPs never leave their cluster.
2. **Which direction, and how much?** A few HTTP APIs from A → B, or full two-way connectivity on many ports?
3. **Same account? Same region? Is this temporary** (a merger, a migration) **or permanent?**

### Why the normal tools fail (the mechanism)

- **VPC peering:** AWS **refuses** to create peering between VPCs whose CIDRs overlap.
- **Transit Gateway:** it lets you attach both VPCs, but it **can't route** between them.
  - Its route table can't send `10.0.0.0/16` to two places; the overlapping VPC's routes aren't propagated.
  - And even if it could: inside VPC A, the route table says **`10.0.0.0/16 → local`**, and the local route always wins. A packet to `10.0.5.10` **never leaves VPC A**, because that address *means* "here."
- **The rule:** only **unique** addresses can cross between networks. Every working option either **translates** addresses or **avoids routing IPs** altogether.

### What a Transit Gateway is (and why it can't route an overlap) ⭐

![AWS Transit Gateway](diagrams/s14-transit-gateway.drawio.svg)

**A Transit Gateway (TGW) is a regional network hub.** Every VPC, VPN and Direct Connect connects **once** to the hub, instead of every VPC peering with every other one.

| Word | Meaning |
|---|---|
| **Attachment** | One connection to the hub: a VPC, a Site-to-Site VPN, a Direct Connect gateway, or another TGW (peering, e.g. another region). A **VPC attachment** puts an ENI in **one subnet per AZ** you choose (best: a small dedicated subnet in each AZ) |
| **TGW route table** | The hub's own routing: "destination prefix → which attachment" |
| **Association** | Each attachment uses **exactly one** TGW route table for traffic **coming from** it |
| **Propagation** | An attachment can **add its CIDRs automatically** to one or more route tables. VPNs and Direct Connect bring routes learned by BGP. You can also add **static** routes, and **blackhole** routes to drop traffic |
| **Segmentation** | Several route tables, e.g. prod attachments can't reach dev, while both reach a shared-services VPC |

**One packet from VPC A to VPC B checks three route tables:**
1. VPC A's subnet route table: `10.2.0.0/16 → tgw-…`
2. The TGW route table associated with A: `10.2.0.0/16 → VPC B attachment`
3. VPC B's subnet route table, **for the reply**: `10.1.0.0/16 → tgw-…`

Forgetting step 3 is the classic "traffic goes out but never comes back" mistake.

**TGW vs VPC peering:**

| | VPC peering | Transit Gateway |
|---|---|---|
| Shape | 1-to-1 links; 10 VPCs need 45 peerings | **Hub**: 10 VPCs need 10 attachments |
| Transitive? | **No**: A–B and B–C doesn't give A–C | **Yes**: everything attached can reach everything its route tables allow |
| VPN, Direct Connect, on-prem | No | Yes |
| Cost | No hourly charge; data charges only across AZs and regions | Per attachment per hour + **per GB processed** |
| Overlapping CIDRs | **Refused** | Can attach, but **can't route** them |
| Across accounts | Accept a request | Share the TGW with **AWS RAM** |

**Why it can't route an overlap:**
- A route table holds **one** route per prefix, so `10.0.0.0/16` can't point to two VPCs.
- And even if it could, VPC A's own `10.0.0.0/16 → local` route wins first, so the packet never reaches the TGW.

That's why option 3 sends **only unique ranges** (`10.100.x.x`) through the TGW, with **static** routes and no propagation of the overlapping CIDRs.

> **Say it:** "A Transit Gateway is a regional hub: VPCs, VPNs and Direct Connect attach once, and TGW route tables decide who reaches whom, with association, propagation and separate tables for segmentation. Unlike peering it's transitive and scales, but it charges per GB. It still routes by IP, so two VPCs with the same CIDR can't both be reached through it."

### Your options

| Option | How it works | Best when | Trade-offs |
|---|---|---|---|
| **1. Amazon VPC Lattice** (on EKS: the AWS Gateway API Controller) | Services join a **service network**. Clients call a Lattice DNS name; traffic goes through the link-local range **169.254.171.0/24**, so VPC IPs never matter. | Several **HTTP/gRPC** services, many teams or accounts, **IAM auth policies** between services | Cost per service-hour, GB and request. Mostly layer 7. Security groups must allow 169.254.171.0/24. |
| **2. AWS PrivateLink** | In B: Service `type: LoadBalancer` → internal **NLB** → **endpoint service**. In A: an **interface endpoint**, an ENI with an IP from **A's own subnet**. | **1–2 TCP services**, one direction, strong isolation, cross-account | One endpoint per service, per direction. The provider sees the NLB's IP, not the client's (use proxy protocol v2 if needed). |
| **3. Routable secondary CIDR + private NAT gateway + Transit Gateway** (the diagram) | Add a **small unique CIDR** to each VPC. A **private NAT** hides A's pods behind one unique IP. TGW carries **only** the unique ranges (static routes, no propagation). An **internal NLB** in B's unique subnet receives the traffic. | **Network-level** access to many services and ports; on-prem joins in too | The most moving parts. NAT and TGW charge per GB. One direction per NAT: B → A needs the mirror image. |
| **4. Remove the overlap (re-IP)** | Build a new cluster in a new VPC with a CIDR from **AWS VPC IPAM**, move the apps (blue/green, shifting DNS weights), then retire the old one | It's permanent, or the options above get messy | Takes time. But it is the **real** fix. |
| 5. **IPv6** clusters | Pods get **globally unique** IPv6 addresses, so pod IPs can't overlap | New clusters | An EKS cluster's IP family is fixed at creation: you can't convert an IPv4 cluster |

**Not options (say why):**
- VPC peering: refused for overlapping CIDRs.
- Plain TGW: can't route them.
- "Change the Service CIDR": irrelevant.
- Cilium Cluster Mesh: needs **unique** pod CIDRs.
- Outside AWS, Submariner's "Globalnet" solves overlap with NAT; mention only if he asks about non-AWS clusters.

### Each option as a picture

All five pictures use the same setup: VPC A (blue) and VPC B (green), **both `10.0.0.0/16`**, and a pod in A that must call `orders` in B.

#### Option 1 · Amazon VPC Lattice

![Option 1: Amazon VPC Lattice](diagrams/s7-option1-vpc-lattice.drawio.svg)

- The client calls a **name**. It resolves to the link-local range `169.254.171.x`, not to anything in either VPC.
- The **service network** (in the middle, run by AWS) decides where the request goes, by service, never by VPC IP. So the overlap simply doesn't matter.
- On EKS, the **AWS Gateway API Controller** turns an `HTTPRoute` into the Lattice service and its targets. An **IAM auth policy** controls who may call it.

#### Option 2 · AWS PrivateLink

![Option 2: AWS PrivateLink](diagrams/s8-option2-privatelink.drawio.svg)

- B **publishes** one service: pods → internal NLB → **endpoint service**.
- A **consumes** it through an **interface endpoint**, an ENI with an IP from **A's own subnet** (`10.0.5.20`). A only ever talks to its own address.
- One service, one direction. B sees the NLB's IP as the source.

#### Option 3 · Unique CIDR + private NAT + Transit Gateway

![Option 3: private NAT gateway and Transit Gateway](diagrams/s2-overlapping-cidr-private-nat.drawio.svg)

- Only **unique** addresses (`10.100.x.x`) ever cross the TGW.
- The private NAT hides pod A behind `10.100.0.5`, and B's internal NLB (`10.100.1.10`) is the only address A can reach in B.
- The packet walk is in [Walk the packet](#walk-the-packet-option-3-as-in-the-diagram) below.

#### Option 4 · Remove the overlap (re-IP)

![Option 4: re-IP with a new VPC and blue/green](diagrams/s9-option4-re-ip.drawio.svg)

- Build **VPC B2** with a unique CIDR from **IPAM**, deploy the same code there, and shift traffic with **Route 53 weights**.
- Once the old VPC B is retired, normal **peering or TGW** works, because nothing overlaps any more.
- It's the only option that **removes** the problem; the others work around it.

#### Option 5 · IPv6 clusters

![Option 5: IPv6 clusters](diagrams/s10-option5-ipv6.drawio.svg)

- Pods get **IPv6** addresses from each VPC's own unique `/56`, so pod-to-pod traffic routes over TGW or peering with **no NAT**.
- IPv4 still overlaps, so anything IPv4-only still needs options 1–3.
- The IP family is fixed when the cluster is created, so this is a **new-cluster** option (usually together with option 4).

### What I'd pick (say a choice, then the reason)

- **A few HTTP APIs, A → B:** VPC Lattice, or **PrivateLink** for one or two TCP services. No network redesign, it works despite the overlap, and access is controlled by IAM or security groups.
- **Broad two-way connectivity** (many ports, old protocols, on-prem too): a unique routable CIDR + **private NAT** + **TGW**, with internal NLBs for inbound traffic.
- **And in parallel, fix the root cause:** take every new VPC's CIDR from **IPAM** pools, and never use the default `10.0.0.0/16` again.

### Walk the packet (option 3, as in the diagram)

1. Pod A (`10.0.1.25`) calls `api.b.internal`. That name is a Route 53 private-zone record pointing at **B's internal NLB, `10.100.1.10`**.
2. A's pod subnet route table: `10.100.1.0/24 → private NAT gateway`.
3. The private NAT does **source NAT**: `10.0.1.25 → 10.100.0.5` (its own unique IP), then sends the packet on: `10.100.1.0/24 → TGW`.
4. The TGW has **static routes only for the unique ranges**: `10.100.1.0/24 → VPC B`.
5. The NLB (`10.100.1.10`) forwards to the target pods. Their `10.0.x.x` IPs are **local inside VPC B**, so that's fine.
6. The reply goes to `10.100.0.5` (B's routable subnet route: `10.100.0.0/24 → TGW`). The NAT **remembers the connection** and translates the reply back to `10.0.1.25`.

### Option 3: which load balancer receives the traffic? ⭐

![Option 3, the way in to VPC B: four load balancer set-ups](diagrams/s15-option3-inbound-load-balancers.drawio.svg)

The way IN to B must be a load balancer with an IP in B's **unique** routable subnet. Many services can **share** one.

**Does every service need its own NLB?** No. One NLB per service (Service `type: LoadBalancer`) is only the simplest set-up. Fewer load balancers means:
- lower cost: each one has an hourly charge plus usage;
- fewer IPs used: each one takes an IP in every AZ subnet it uses, and the routable CIDR is small on purpose;
- fewer IPs to open in security groups and to point DNS at.

**ALB vs NLB: what each can route on**

| Rule | ALB (layer 7) | NLB (layer 4) |
|---|---|---|
| Host (`orders.b.internal`), path (`/orders`), headers | ✅ | ❌ |
| Listener port | ✅ | ✅, **its only rule** |
| TLS with several certificates (SNI) | ✅ | Only **picks the certificate**; can't send different names to different target groups |

**An NLB can't route like an ALB Ingress.** Host and path routing always happens in a **layer-7 hop**: an ALB, or an ingress / gateway controller.

**The four set-ups (A–D in the diagram):**

| | Set-up | Who does the host / path routing | Use it for |
|---|---|---|---|
| **A** | Internal **ALB** | The ALB itself | HTTP / gRPC only; simplest. Ingresses share one ALB through `alb.ingress.kubernetes.io/group.name` |
| **B** | **NLB → controller pods** (e.g. Envoy Gateway) | The **controller**: the NLB only passes TCP on port 443 | HTTP **plus** fixed IPs or TLS passthrough; one NLB for many services |
| **C** | **NLB, one listener per port** | Nobody: routing is by port (`5432` → DB, `9092` → Kafka) | Non-HTTP services. Bind each target group to its Service with `TargetGroupBinding` |
| **D** | **NLB → ALB** (the ALB is the NLB's target) | The ALB | Firewall rules that need **fixed IPs**, plus ALB routing |

**Set-up B in one request:**
1. A pod in A calls `https://orders.b.internal`. DNS returns the NLB's IP, `10.100.1.10`.
2. Private NAT A → TGW → **NLB, port 443**. The NLB forwards the TCP connection to one controller pod, **without reading any name**.
3. The controller reads `orders.b.internal` (the HTTP `Host` header, or the TLS SNI) and sends the request to the **orders** Service.
4. `payments.b.internal` reaches the **same** NLB and controller, then goes to **payments**.

The NLB is the front door; the controller is the receptionist who reads the name on each envelope. The routes live in the controller, as `HTTPRoute`s or Ingresses.

**Why an NLB in option 3 at all:**
1. **Fixed IPs:** you can choose an internal NLB's private IP in each subnet, and it never changes. That's good for firewall rules; ALB IPs change as it scales.
2. **Any protocol:** TCP, UDP, TLS, not just HTTP.
3. **One subnet is enough:** an NLB can live in one AZ subnet; an **ALB needs subnets in two AZs**, so the unique CIDR must then be split, e.g. `10.100.1.0/24` into two `/25`s.
4. **TLS passthrough:** the NLB doesn't decrypt, so the controller or the app handles TLS.

**Using an ALB in option 3 (set-up A):**
- Clients use its **DNS name**, never its IPs.
- Its security group allows the **NAT range** (`10.100.0.0/24`), not pod IPs.
- Targets are the pods in the non-routable `10.0.x.x` subnets (target type `ip`), reached through the VPC's local route.
- B sees the **NAT's IP** (`10.100.0.5`) as the client, in `X-Forwarded-For` too. The pod's real IP is lost at the private NAT.

> **Say it:** "Not one NLB per service. An NLB is layer 4 and routes only by listener port, so host or path routing needs a layer-7 hop: an internal ALB for plain HTTP, or an NLB in front of an ingress or gateway controller when I need fixed IPs or TLS passthrough. Non-HTTP services share an NLB with a listener per port. That keeps cost down and saves IPs in the small routable CIDR."

### Two-way traffic ⭐

![Two-way traffic with option 3](diagrams/s11-two-way-private-nat.drawio.svg)

**"Two-way" means both sides can START a connection.** Replies on an existing connection always come back by themselves (step 6 above). What needs extra work is B **starting** a call to A.

**Why one NAT can't carry both directions:**
- A NAT only translates connections that **start inside it**. It remembers each one (like conntrack on a Linux host), and that memory is how replies find their way back.
- A packet that arrives at `10.100.0.5` from B with **no matching connection** has no pod to go to, so it's dropped.
- It's your home Wi-Fi: you can open any website, but nobody on the internet can start a connection to your laptop.
- AWS NAT gateways never forward ports inward. **The way in is always a load balancer.**

**So with option 3, each VPC needs both:**

| | Way OUT (it starts calls) | Way IN (it receives calls) |
|---|---|---|
| VPC A | Private NAT A · `10.100.0.5` | Internal NLB A · `10.100.0.10` |
| VPC B | Private NAT B · `10.100.1.5` | Internal NLB B · `10.100.1.10` |

The TGW routes (`10.100.0.0/24 → A`, `10.100.1.0/24 → B`) already work in both directions; only the NATs and NLBs are per direction.

#### Can the other options do two-way? Yes, all of them

![Two-way traffic: what each option needs](diagrams/s13-two-way-per-option.drawio.svg)

| Option | Two-way? | What B → A needs |
|---|---|---|
| **1 · Lattice** | Yes, **built in**, per service | Nothing new on the network. A also publishes its services in the **same** service network |
| **2 · PrivateLink** | Yes, but as **two separate one-way setups**, per service | A builds its own NLB + endpoint service; B creates an interface endpoint in B |
| **3 · Private NAT + TGW** | Yes, at **network level**, with NAT | A NAT and an NLB on **each** side (the 4 desks above) |
| **4 · Re-IP** | Yes, **full**: any port, any protocol, no NAT | Normal TGW or peering routes both ways; security groups decide |
| **5 · IPv6** | Yes, for **IPv6** traffic | Same as re-IP; IPv4-only traffic still overlaps |

- **Lattice:**
  - Both VPCs are associated with one service network.
  - Each cluster runs the AWS Gateway API Controller, which turns its `HTTPRoute`s into Lattice services, so either side calls the other by Lattice name.
  - Each service has its own **auth policy**, so each direction is controlled separately.
  - Limit: it's **service-to-service only**, not any IP on any port.
- **PrivateLink:**
  - Everything is per service **and** per direction: A → B needs NLB B + an endpoint service in B + an interface endpoint in A, and B → A is the mirror image.
  - With **5 services both ways**, that's 10 endpoint services and 10 endpoints. At that size the cost and the work point to Lattice.
- **Re-IP and IPv6:** the only options with full **network-level** two-way traffic and **no NAT**.

> **Say it:** "Lattice gives two-way per service with almost no extra setup. PrivateLink needs a mirrored setup for each direction and each service. Only re-IP or IPv6 give full network-level two-way without NAT."

### Why not a bastion host or a VPN? ⭐

![Why a bastion or a VPN doesn't fix overlapping CIDRs](diagrams/s12-why-not-bastion-or-vpn.drawio.svg)

**The overlap is an addressing problem, and neither of these changes addresses.**

**Why not a bastion host:**
- A bastion is a **door for people**: an admin logs in with SSH (or better, SSM Session Manager) to reach private machines. It's not a path for application traffic.
- It sits in **one** VPC, so it has the **same routing problem**: its route table also says `10.0.0.0/16 → local`. Even a box with a network card in **both** VPCs sees `10.0.0.0/16` on both cards, and can't tell which side `10.0.1.25` means.
- Making it carry app traffic means hand-made SSH tunnels or a proxy you run yourself. That's one box with no high availability, a throughput limit, manual work when pods change, and an extra way in for attackers.

**Why not a VPN:**
- A VPN is a **pipe between networks**. It doesn't change any address.
- Pod A sends to `10.0.1.25`, and VPC A's route table picks **`10.0.0.0/16 → local`**. A VPN route for that range can never win, so **nothing ever enters the tunnel**. It fails for the same reason peering and a plain TGW fail.
- It only works if you add **NAT on both ends**, mapping the other side to a fake unique range (e.g. B appears as `10.200.0.0/16`). AWS's managed Site-to-Site VPN doesn't do that, so you'd run VPN appliances yourself. That is **option 3, self-managed**, with about **1.25 Gbps per AWS VPN tunnel**.
- VPNs are the right tool for connecting **on-premises or another cloud**, not two overlapping VPCs.

> **Say it:** "A bastion is a door for people and a VPN is a pipe. Neither changes addresses, and with an overlap the problem *is* the addresses: VPC A's local route always wins, so the traffic never reaches the bastion or the tunnel. Only three things work: translate the addresses (private NAT), avoid IP routing (Lattice, PrivateLink), or change the addresses (re-IP, IPv6)."

### Follow-ups he's likely to ask

- **"Can B start a connection to A this way?"** No. NAT only allows connections started **from inside**. For B → A, you need a private NAT in B and an NLB in A.
- **"Does B's service see pod A's IP?"**
  - No. It sees the NAT's IP, or the NLB's.
  - For identity, use **mTLS / service identity or headers**, not source IPs.
  - The NLB can pass the client IP with proxy protocol v2; an ALB uses `X-Forwarded-For`.
- **"DNS?"**
  - A Route 53 **private hosted zone** associated with VPC A, or the generated DNS names that Lattice and PrivateLink give you.
  - ExternalDNS can create the records from Kubernetes.
- **"What does it cost?"**
  - NAT: per hour and per GB. TGW: per attachment-hour and per GB. PrivateLink: per endpoint per AZ, and per GB. Lattice: per service-hour, GB and request.
  - Say "I'd model it for our traffic"; don't guess numbers.
- **"How do you prevent this next time?"**
  - **AWS VPC IPAM** pools per environment and region.
  - Terraform modules take CIDRs **from IPAM**, never typed by hand.
  - A shared CIDR register that includes on-prem ranges.

---

## A3 · Nodes in one CIDR, pods in another: how is that done? ⭐🔥

![Node vs pod CIDR](diagrams/s3-node-vs-pod-cidr.drawio.svg)

**The scenario:**
- `kubectl get nodes -o wide` shows node IPs like `10.0.12.201`;
- `kubectl get pods -o wide` shows pod IPs like `100.64.1.23`.

"Which technique is this, and how does it work?"

### Say this first (30 seconds)

> "On EKS with the VPC CNI, pods normally get IPs from the **same subnet as their node**. Different ranges means one of three things:
> 1. **VPC CNI custom networking:** a **secondary CIDR**, usually from `100.64.0.0/10`, is added to the VPC, with pod subnets in each AZ. An **ENIConfig** per AZ tells the CNI to put the node's **secondary ENIs** in those subnets. The **primary ENI keeps the node IP**.
> 2. **EKS Auto Mode:** the same idea, set up with `podSubnetSelectorTerms` and `podSecurityGroupSelectorTerms` in a **custom NodeClass**.
> 3. An **overlay CNI** (Calico or Cilium in overlay mode), where the pod CIDR isn't in the VPC at all.
>
> I'd check which one it is by looking at the ENIConfigs, the aws-node settings, the NodeClass, and the ENIs on the instance."

### Why teams do this

![VPC CNI custom networking, before and after](diagrams/s16-custom-networking-before-after.drawio.svg)

**Before:** every pod takes an IP from the node's own small subnet, through the node's ENIs (Elastic Network Interfaces). **After:** the primary ENI keeps only the node IP, and the secondary ENIs sit in a pod subnet from the secondary CIDR (Classless Inter-Domain Routing range) `100.64.0.0/16`.

1. **IP exhaustion** (the most common reason). Node subnets are often a small `/24`, and every node reserves extra IPs for future pods. The `100.64.0.0/10` range (RFC 6598, "carrier-grade NAT" space) gives lots of room.
2. **Different security groups** for pod traffic and node traffic.
3. **Pods stay non-routable** while nodes keep routable, corporate (RFC 1918) IPs. On-prem and the TGW only ever see node IPs, which saves scarce corporate address space.

### How VPC CNI custom networking works, step by step

![Set up VPC CNI custom networking in 5 steps](diagrams/s17-custom-networking-steps.drawio.svg)

The VPC CNI (Virtual Private Cloud Container Network Interface) runs as the `aws-node` pods. The right side of the diagram shows how a new node finds **its** ENIConfig: its AZ (Availability Zone) label `topology.kubernetes.io/zone=us-west-1a` picks the ENIConfig named `us-west-1a`.

```bash
# 1. Add a secondary CIDR to the VPC, then create a pod subnet in EACH AZ your nodes use
aws ec2 associate-vpc-cidr-block --vpc-id vpc-0abc --cidr-block 100.64.0.0/16

# 2. Turn on custom networking, and pick each node's ENIConfig by its AZ label
kubectl set env daemonset aws-node -n kube-system AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true
kubectl set env daemonset aws-node -n kube-system ENI_CONFIG_LABEL_DEF=topology.kubernetes.io/zone
```

3. Create one ENIConfig **named after each AZ**:

```yaml
apiVersion: crd.k8s.amazonaws.com/v1alpha1
kind: ENIConfig
metadata:
  name: us-west-1a            # = the AZ name
spec:
  subnet: subnet-0pod1a       # the pod subnet from 100.64.0.0/16 in us-west-1a
  securityGroups:
  - sg-0podtraffic
```

4. **Replace the nodes.** Existing nodes don't change: create new nodes, then cordon and drain the old ones.
5. **Fix max pods.** The primary ENI no longer hosts pods, so the formula becomes **(ENIs − 1) × (IPs per ENI − 1) + 2**. An m5.large goes **29 → 20**. Add **prefix delegation** to get far more (AWS suggests capping at 110 on small instances).

> ⚠️ On the **EKS managed add-on**, put these settings in the add-on's **configuration values**. `kubectl set env` changes can be **overwritten by the next add-on update**: two owners again.

### What happens to a packet

| Traffic | Source IP seen | Security group used |
|---|---|---|
| Pod → pod or service **inside the VPC** | The **pod IP** (`100.64.1.23`) | The ENIConfig's (pod) SG |
| Pod → **outside the VPC** (internet through NAT, on-prem through TGW) | **SNAT to the node's primary IP** (`10.0.12.201`), because `AWS_VPC_K8S_CNI_EXTERNALSNAT=false` by default | The **node's** SG and the node subnet's route table |
| On-prem → a pod | ❌ Not directly: `100.64.x` isn't advertised | Put an **internal ALB or NLB** in routable subnets; the ALB with `target-type: ip` reaches pod IPs inside the VPC |
| `hostNetwork` pods (aws-node, kube-proxy) | The **node IP** | Node SG |

### The EKS Auto Mode version (what One2N did)

```yaml
apiVersion: eks.amazonaws.com/v1
kind: NodeClass
metadata:
  name: prod-nodeclass           # ⚠️ NOT "default"
spec:
  role: MyNodeRole
  subnetSelectorTerms:           # node primary ENI
  - tags: { Name: node-subnet }
  securityGroupSelectorTerms:
  - tags: { Name: eks-node-sg }
  podSubnetSelectorTerms:        # pod ENIs: must be set TOGETHER with the next field
  - tags: { kubernetes.io/role/pod: "1" }
  podSecurityGroupSelectorTerms:
  - tags: { Name: eks-pod-sg }
```

- **NodePool:** point the NodePool's `nodeClassRef.name` at your NodeClass.
- **Access entry:** a custom NodeClass needs an **access entry of type EC2**, with `AmazonEKSAutoNodePolicy`, so its nodes can join the cluster. The built-in NodeClass gets one automatically.
- **Pod IPs:**
  - come in **/28 prefixes** by default, falling back to single IPs;
  - `advancedNetworking.ipv4PrefixSize: "32"` uses single IPs only.
- **`snatPolicy`:**
  - `Random` (the default) SNATs traffic leaving the VPC to the node IP;
  - `Disabled` keeps pod IPs everywhere, so routing and SGs must allow them.
- **Pod SGs:**
  - apply **only inside the VPC**;
  - are per **NodeClass** (every pod on those nodes shares them).
- **Pod subnet AZ:** each pod subnet must be in the **same AZ** as its node subnet.
- **Pods per node:** fewer, because the primary ENI only carries the node IP.

### The One2N incident (expect this as a follow-up) ⭐

![Two controllers fight over NodeClass default](diagrams/s4-two-controllers-fight.drawio.svg)

- **What happened:**
  - They added a `100.64.0.0/16` pod CIDR through **Argo CD**, by editing a NodeClass named **`default`**.
  - Pods got `100.64.x.x` IPs, then **flipped back to `10.0.x.x` within about five minutes**, again and again.
  - Argo CD showed **OutOfSync** right after "successful" syncs.
- **Root cause:**
  - EKS Auto Mode **creates and owns a NodeClass called `default`** as soon as you enable a built-in NodePool.
  - Its controller kept resetting it, removing `podSubnetSelectorTerms` and `podSecurityGroupSelectorTerms`.
  - Two controllers, one object.
- **Fix:**
  - Rename to `<env>-nodeclass` and update the NodePool's `nodeClassRef`.
  - AWS's docs say it plainly: *don't name your custom NodeClass `default`*.
- **How to debug a "keeps reverting" problem:**
  - `kubectl get nodeclass default -o yaml --show-managed-fields` (two managers);
  - Argo CD's sync history;
  - `kubectl get nodes -L karpenter.sh/nodepool`;
  - pod IPs over time with `kubectl get pods -o wide`.

### Follow-ups he's likely to ask

- **"Pods are stuck in ContainerCreating: `failed to assign an IP address to container`."** Check, in this order:
  1. Is the pod subnet full?
  2. Is there an ENIConfig for **this node's AZ**?
  3. Is the subnet in the wrong AZ?
  4. Is the CNI missing IAM permissions?
  - Look in `kubectl describe pod` and the node's ipamd log (`/var/log/aws-routed-eni/ipamd.log`).
- **"We enabled it, but new pods still get `10.0.x.x`."**
  - The pods landed on **old nodes**;
  - the ENIConfig name doesn't match the AZ (and the nodes have no label or annotation);
  - or an add-on update **wiped the env vars**.
- **"Custom networking vs prefix delegation vs IPv6?"**
  - **Prefix delegation:** more IPs per ENI, but still from the **node's** subnet.
  - **Custom networking:** a **separate** pod range.
  - **IPv6:** solves exhaustion completely, but only for new clusters (AWS recommends IPv6 when you can).
  - They can be combined: custom networking + prefix delegation.
- **"And in plain Kubernetes, not EKS?"** There are three ranges:
  - **nodes** (the machine network);
  - **pods** (`--cluster-cidr`, split into one `podCIDR` per node, for example a /24);
  - **Services** (`--service-cluster-ip-range`, virtual only).
  - An overlay CNI routes pod traffic between nodes with encapsulation (VXLAN) or BGP.
- **"Overlay CNI on EKS: any catch?"** Yes. The **EKS control plane can't reach overlay pod IPs**, so admission webhooks and metrics-server need `hostNetwork: true`. ALB `target-type: ip` doesn't work either; use instance targets.

---

## The "two owners" pattern ⭐

The most important lesson across his three scenarios. Learn this table; it answers a whole family of "why does it keep changing back?" questions.

| Owner 1 | Owner 2 | Symptom | Fix |
|---|---|---|---|
| A person (`kubectl edit`) | Helm | The edit is reverted on the next deploy (Helm 3), or the deploy fails with a conflict (Helm 4 SSA) | Change prod through Git only |
| HPA | Helm or Argo CD setting `replicas` | Replicas drop on every deploy / app shows OutOfSync | Don't template `replicas`; use `ignoreDifferences` |
| A person (`kubectl edit`) | Argo CD with `selfHeal` | The edit is undone within minutes | That's the point of GitOps; make the change in Git |
| Argo CD | EKS Auto Mode (NodeClass `default`) | Fields stripped, pods flip IPs, OutOfSync forever | Use your own NodeClass name |
| `kubectl set env aws-node` | EKS managed add-on update | Settings lost after an add-on update | Use the add-on's configuration values |
| Two CI pipelines | The same Helm release | `another operation … is in progress` | CI concurrency group, or GitOps |
| VPC A | VPC B (same CIDR) | No route between them | Translate (NAT, Lattice, PrivateLink) or re-IP |

**Tools to see owners:**
- `kubectl get <obj> -o yaml --show-managed-fields` shows each manager, the operation and the time;
- the Argo CD diff;
- the EKS audit logs.

---

# Part B: more scenarios, Hemant style

Each one: **Say** (the core answer) and **He'll push** (the follow-up). ⭐ = most likely.

## 🐳 Docker

**B1 ⭐ "The container is distroless: no shell, no curl. How do you check whether it can reach the database?"**
- **Say:**
  - Don't add tools to the image. Attach a **debug container** that shares the pod's network: `kubectl debug -it <pod> --image=nicolaka/netshoot --target=app`, then `nc -zv db 5432`.
  - In plain Docker: `docker run --rm -it --network container:<name> nicolaka/netshoot`.
  - On a locked-down VM that has bash but no curl: `timeout 5 bash -c '</dev/tcp/db/5432' && echo open`. This is from One2N's blog, [1 Oct 2026](https://one2n.io/blog/test-tcp-connectivity-without-curl-bash-dev-tcp).
- **He'll push: "Limits of `/dev/tcp`?"**
  - It's **bash only**: not `sh`, not zsh, and it's off in POSIX mode.
  - It has no TLS and no built-in timeout.
  - The error tells you a lot: *refused* means the port is closed; a *timeout* means a firewall or SG is dropping packets.

**B2 "The image works on my Mac but crashes on EKS with `exec format error`."**
- **Say:** the image was built for **arm64** (Apple silicon), but the nodes are **amd64**. Build for both:
  - `docker buildx build --platform linux/amd64,linux/arm64 -t <repo>:<sha> --push .`
  - Check the result with `docker buildx imagetools inspect`.
- **He'll push: "Why build arm64 at all?"** Graviton nodes are cheaper; a multi-arch image runs on both.

**B3 ⭐ "We pushed a fix with the same tag `v1`. Half the pods still run the old code."**
- **Say:**
  - Tags are **mutable**.
  - For non-`latest` tags, `imagePullPolicy` defaults to `IfNotPresent`, so nodes that already cached `v1` keep the old image.
  - Fix: a **unique tag per build** (the git SHA) or a **digest** (`image@sha256:…`), plus **ECR tag immutability**.
- **He'll push: "Why not `imagePullPolicy: Always`?"** It pulls on every container start (more registry load and rate limits), and running pods **still** don't change. Immutable tags are the real fix.

**B4 "`docker stop` takes 10 seconds and the container exits with 137."**
- **Say:**
  - The app never got SIGTERM, or ignored it: a shell-form `CMD` makes `sh` PID 1, and sh doesn't pass signals on.
  - After 10 seconds Docker sends SIGKILL, which gives exit code 128 + 9 = **137**.
  - Fix: exec-form `CMD`, `exec "$@"` in entrypoint scripts, `--init` (tini), and handle SIGTERM in the app.
- **He'll push:** "And in Kubernetes?" → the same, with a 30-second `terminationGracePeriodSeconds` (see [05 Pods](kubernetes/05-pods.md)).

## ☸️ Kubernetes

**B5 ⭐ "You updated a ConfigMap, but the app still uses the old values."**
- **Say:**
  - **Env vars** are read only when the container starts.
  - **Mounted files** update after a delay (the kubelet sync, about a minute), **except `subPath` mounts, which never update**. Even then, the app must re-read the file.
  - Fix: `kubectl rollout restart`, Helm's `checksum/config` annotation, or Kustomize's `configMapGenerator` hash suffix.
- **He'll push: "Secrets too?"** Yes, the same rules.

**B6 ⭐ "A node goes NotReady. What happens to its pods, and when?"**
- **Say:**
  1. After **50 seconds** without heartbeats (`node-monitor-grace-period`), the node becomes NotReady/Unknown and gets the `node.kubernetes.io/unreachable:NoExecute` taint.
  2. Pods have a default toleration of **300 seconds**, so after about **5 minutes** they're evicted and their controllers recreate them elsewhere.
  3. **StatefulSet pods are not replaced** until the node is confirmed gone: two pods with the same identity would be worse.
- **He'll push: "How do you speed that up?"**
  - A shorter `tolerationSeconds` for critical pods.
  - On EKS, a terminated instance's Node object is deleted automatically.
  - For a node that's dead but not deleted, add the `node.kubernetes.io/out-of-service` taint (non-graceful node shutdown).
  - A PDB **doesn't help** here: this is an involuntary disruption.

**B7 "The new pods fail readiness and the rollout is stuck. Does Kubernetes roll back?"**
- **Say:**
  - **No.** The old pods keep serving (thanks to `maxUnavailable`).
  - After `progressDeadlineSeconds` (600 s), the Deployment shows `Progressing=False, ProgressDeadlineExceeded`, and that's all.
  - You roll back yourself (`kubectl rollout undo`), or let a tool do it: Helm `--rollback-on-failure` (Helm 4; `--atomic` in Helm 3), or Argo Rollouts analysis.

**B8 ⭐ "After the EKS upgrade, `helm upgrade` fails with `no matches for kind … policy/v1beta1`."**
- **Say:** the release Secret still stores the **old API version** → the `helm mapkubeapis` plugin fixes it. Before upgrades, run pluto or kubent and check **EKS upgrade insights** ([A1](#follow-ups-hes-likely-to-ask)).

**B9 "Karpenter / Auto Mode keeps moving our pods during business hours."**
- **Say:** that's **consolidation** (repacking pods onto fewer, cheaper nodes). Ways to control it:
  - **PDBs**;
  - the pod annotation `karpenter.sh/do-not-disrupt: "true"`;
  - NodePool **disruption budgets** with a schedule (for example, `nodes: "0"` during business hours);
  - or `consolidationPolicy: WhenEmpty`.

## ☁️ AWS

**B10 ⭐ "Pods in private subnets can't pull from ECR: `i/o timeout`."**
- **Say:** a **timeout means network**; **401/403 means permissions**.
  - **Network:** there's no route out. Add a NAT gateway, or **VPC endpoints**: `ecr.api` and `ecr.dkr` (interface), plus an **S3 gateway endpoint**, because image layers come from S3.
    - For a private cluster, add `sts` and `logs` too.
    - The endpoint's SG must allow 443 from the nodes, and private DNS must be on.
  - **Permissions:** the node role needs ECR read permission (`AmazonEC2ContainerRegistryReadOnly`), and a repository in another account needs a repository policy.
- **He'll push:** "Why does an ECR pull need S3?" → ECR stores image layers in S3.

**B11 "The NAT gateway bill jumped."**
- **Say:**
  1. **Find it:** Cost Explorer (usage type `NatGateway-Bytes`) plus **VPC Flow Logs**: which source IPs send the most bytes, and to where.
  2. **Common causes:** S3 or ECR traffic going through the NAT (fix: the S3 gateway endpoint is free; add ECR endpoints); pods in AZ-b using the NAT in AZ-a (one NAT **per AZ** with per-AZ routes); chatty logging to an external SaaS.

**B12 "Intermittent 502s from the ALB during every deploy on EKS."**
- **Say:**
  - The ALB still sends requests to pods that are shutting down, or to new pods before they're ready.
  - Fixes: **pod readiness gates** from the AWS Load Balancer Controller (label the namespace `elbv2.k8s.aws/pod-readiness-gate-inject=enabled`), a `preStop` sleep longer than the deregistration delay, SIGTERM handling, and `target-type: ip`.

**B13 "We made the EKS API endpoint private. Now kubectl times out from laptops and GitHub Actions."**
- **Say:** the endpoint now resolves to **private IPs inside the VPC**. You need a way in:
  - VPN or Direct Connect, or a bastion / SSM tunnel;
  - or keep the public endpoint but restrict `publicAccessCidrs`;
  - for CI: **self-hosted runners in the VPC**, or GitOps, where Argo CD pulls from inside so CI never needs the API.

## 🔄 CI/CD

**B14 ⭐ "Two merges land a minute apart. The second pipeline fails: `another operation (install/upgrade/rollback) is in progress`."**
- **Say:**
  - Helm marks the release `pending-upgrade` while it works.
  - Fix: serialize deploys with a GitHub Actions `concurrency: { group: deploy-prod, cancel-in-progress: false }`.
  - If a job was killed half-way: `helm rollback` to the last good revision.
  - GitOps avoids this entirely: one controller applies everything.

**B15 "`helm upgrade` was green in CI, but the app is down."**
- **Say:**
  - Without `--wait`, Helm returns as soon as the API **accepts** the objects, not when the pods are healthy.
  - Use `--wait --timeout 5m` with `--rollback-on-failure` (Helm 4) or `--atomic` (Helm 3), plus a smoke test.
  - Better still: Argo CD health checks with Argo Rollouts analysis.

**B16 "Roll back production now. How?"**
- **Say:** roll back **through the tool that deployed**:
  - GitOps: `git revert`, and Argo CD syncs the old version back;
  - Helm: `helm rollback web <rev>` (this creates a new revision).
- `kubectl rollout undo` creates **drift** ([A1](#a1--helm-drift-someone-edited-the-cluster-then-we-run-helm-upgrade-again-)).
- **He'll push: "And the database?"** Rolling back code only works if schema changes are **backward compatible**: expand first, contract later.

## 🔥 Security

**B17 ⭐ "A developer asks for cluster-admin on prod to debug something."**
- **Say:**
  - No. Give least privilege: namespace **view** plus `pods/log`, and `pods/exec` only if truly needed.
  - For emergencies: a **time-limited break-glass role** through access entries, with approval and audit (CloudTrail and EKS audit logs).
- **He'll push: "What's risky about `create pods` or `list secrets`?"**
  - Creating pods lets someone run a privileged pod or mount the host, which means **taking over the node**, unless Pod Security Admission blocks it.
  - `list secrets` = **read every secret**.

**B18 "A pod is compromised and running a crypto miner. First steps?"**
- **Say:** **contain, keep the evidence, then clean up:**
  1. Isolate it with a deny-all NetworkPolicy on its labels, and cordon the node.
  2. Capture the pod YAML, its logs and a node snapshot.
  3. Revoke its AWS access (remove the Pod Identity association, or the IRSA role's trust).
  4. Rotate the secrets it could read.
  5. Only then delete it.
- Then find how they got in (an image CVE, an exposed dashboard, a leaked token).
- Detect the next one with **GuardDuty EKS protection and runtime monitoring**.

**B19 "A critical CVE is found in the base image used by 40 running services."**
- **Find:** **ECR enhanced scanning** (Amazon Inspector) rescans images continuously and lists the affected images.
- **Fix:** rebuild from the patched base image (Renovate or Dependabot can bump it) and deploy through the normal pipeline.
- **Prevent:** an admission policy (Kyverno or ValidatingAdmissionPolicy) that blocks images that are **unsigned or have critical CVEs**.

**B20 "Database passwords were committed in `values.yaml`."**
- **Say:**
  1. **Rotate first**: assume they leaked.
  2. Then clean the history (`git filter-repo`) and force-push.
  3. Going forward: **External Secrets Operator** with AWS Secrets Manager (and Pod Identity), or SOPS-encrypted values; **gitleaks** in pre-commit and CI.
- See [model answer Q57](hemant-model-answers.md).

---

## Videos for these scenarios (all checked: link, title, channel, length)

| | Video | Channel | Length | For |
|---|---|---|---|---|
| ⭐ | [How Amazon VPC CNI for k8s works](https://www.youtube.com/watch?v=RBE3yk2UlYA) | Containers from the Couch (AWS) | 9 min | A3: how pods get VPC IPs from ENIs; prefixes; custom networking |
| ⭐ | [Running Out of IPs on EKS? Use Secondary CIDR + VPC CNI Plugin](https://www.youtube.com/watch?v=69OE4LwzdJE) | DevOps World | 10 min | A3: the secondary CIDR setup, step by step |
| ⭐ | [How to Solve for Overlapping IP Addresses](https://www.youtube.com/watch?v=vM1sO_huJvw) | F5 DevCentral | 4 min | A2: what overlap is and the general ways out |
| ⭐ | [Fix Overlapping Network Addresses in AWS: How to Use Private NAT Gateway](https://www.youtube.com/watch?v=fIcKD8jASyQ) | Lepczynski | 15 min | A2: option 3, with a demo |
| ⭐ | [What Problem AWS VPC Lattice Actually Solves](https://www.youtube.com/watch?v=EpuVruSutAM) | TheBlueprintInfra | 2 min | A2: option 1 in two minutes |
| 🔁 | [Amazon VPC Lattice: EKS](https://www.youtube.com/watch?v=jtfvD1kytSE) | Amazon Web Services | 5 min | A2: Lattice with EKS (demo) |
| 🔁 | [Helm 2 vs Helm 3](https://www.youtube.com/watch?v=dqMSOtWZRws) | KodeKloud | 8 min | A1 background: what changed in Helm 3. The 3-way details are in the notes above. |
| 🔁 | [Kubernetes managedFields explained](https://www.youtube.com/watch?v=P12z8X-qhis) | Aqua Security Open Source | 14 min | A1/Helm 4: field managers, the base of server-side apply |

No good video exists yet for Helm 4's server-side apply or for Auto Mode pod subnets. For those, read A1 and A3 above and the One2N post.

## Sources

- **One2N blog:**
  - [EKS Auto Mode NodeClass reverting to default](https://one2n.io/blog/eks-auto-mode-nodeclass-reverting-to-default)
  - [Test TCP connectivity without curl](https://one2n.io/blog/test-tcp-connectivity-without-curl-bash-dev-tcp)
- **Helm:**
  - [Changes since Helm 2 (3-way merge)](https://helm.sh/docs/faq/changes_since_helm2/)
  - [helm upgrade flags (Helm 4)](https://helm.sh/docs/helm/helm_upgrade/)
  - [HIP-0023: server-side apply](https://helm.sh/community/hips/hip-0023)
- **Kubernetes:** [Server-side apply and conflicts](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- **AWS EKS:**
  - [Custom networking tutorial](https://docs.aws.amazon.com/eks/latest/userguide/cni-custom-network-tutorial.html)
  - [Custom networking best practices](https://docs.aws.amazon.com/eks/latest/best-practices/custom-networking.html)
  - [Auto Mode NodeClass](https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html)
- **AWS networking:**
  - [Private NAT gateways for overlapping CIDRs](https://aws.amazon.com/blogs/containers/addressing-ipv4-address-exhaustion-in-amazon-eks-clusters-using-private-nat-gateways)
  - [VPC Lattice with EKS](https://aws.amazon.com/blogs/containers/application-networking-with-amazon-vpc-lattice-and-amazon-eks/)
