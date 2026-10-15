# ⎈ Helm Notes: Interview Edition

Everything we've learned about Helm while preparing for the interview with Hemant (One2N), in the same format as the [Docker](../docker/README.md), [Kubernetes](../kubernetes/README.md) and [Networking](../networking/README.md) notes.

Helm drift is one of the **three scenarios Hemant named** ([A1](../hemant-scenario-deep-dives.md)), so these notes go deep on **how `helm upgrade` really changes objects**. Almost everything here was **run for real** with **your Helm v4.2.3** on a throwaway Kubernetes 1.34 cluster (k3s in Docker) on 8–9 Oct 2026.

## How to use these notes

- Read one file at a time, then answer its **Interview angle** questions **out loud**.
- ⭐ = very likely interview topic · 🔥 = Hemant's named scenario · 🖥️ = you can show it live · 🧪 = tested, real output
- **Before the interview:** read 02, 03 and 04 (about 40 minutes).

## The one idea: every field has an owner

![Helm 4 server-side apply: every field has an owner](../diagrams/s6-ssa-field-owners.drawio.svg)

Think of a Kubernetes object as a **shared document where every line carries a name tag**: who wrote it last.

- **Helm 3** rewrites its lines without looking at the tags → **silent overwrite**.
- **Helm 4** sends its lines to the API server, which **checks the tags** → **conflict** if someone else owns a line Helm wants to change.

When something "keeps changing back" or "won't update", ask: **who else owns this field?**

## Contents

| # | File | What's inside |
|---|---|---|
| 01 | [Basics](01-basics.md) | Chart, release, revision, chart layout, values order, rendering, where releases are stored 🧪 |
| 02 ⭐ | [How upgrades work](02-how-upgrades-work.md) | Helm 2 vs 3 vs 4, CSA vs SSA, what "3-way merge" really means, 5 fields tested 🧪 |
| 03 ⭐ | [Server-side apply](03-server-side-apply.md) | `managedFields`, the rules, conflicts and how to choose, the HPA case 🧪 |
| 04 ⭐🔥 | [The drift scenario](04-drift-scenario.md) | Hemant's A1 question: what to say, how to see drift, follow-ups 🧪 |
| 05 | [Flags, annotations and hooks](05-flags-annotations-hooks.md) | Every important Helm 4 flag, every Helm annotation, the upgrade order 🧪 |
| 06 | [Troubleshooting](06-troubleshooting.md) | Release states, real error messages, debug commands, scenarios |
| 07 | [Command list](07-helm-commands.md) | Every command by task, checked against Helm 4.2.3 |

## Diagrams

The diagrams are in [diagrams/](diagrams/) as editable **`.drawio.svg`** files; open one in VS Code (Draw.io Integration) or [app.diagrams.net](https://app.diagrams.net) to edit it. Two more come from the scenario notes: [s5, tested field results](../diagrams/s5-helm-merge-cases.drawio.svg) and [s6, field owners](../diagrams/s6-ssa-field-owners.drawio.svg).

**To draw on a whiteboard:** the three Helm versions (02) and the field owners (s6).

## Your own practice cluster (no kind needed) 🖥️

This is how every 🧪 test here was run. It uses **its own kubeconfig file**, so your work EKS cluster is never touched.

Start the cluster (takes about 20 seconds):

```bash
docker run -d --rm --name helm-lab --privileged -p 127.0.0.1:16443:6443 rancher/k3s:latest server --disable traefik --disable servicelb
```

Save its kubeconfig, pointed at the published port:

```bash
docker exec helm-lab cat /etc/rancher/k3s/k3s.yaml | sed 's#127.0.0.1:6443#127.0.0.1:16443#' > ~/helm-lab.yaml
```

Use it **in this terminal only**:

```bash
export KUBECONFIG=~/helm-lab.yaml
```

**Check before every session:** it must print `https://127.0.0.1:16443`.

```bash
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
```

Stop it. `--rm` deletes the container and everything in it:

```bash
docker stop helm-lab
```

## Related files

- [Kubernetes 21: Helm, Kustomize and GitOps](../kubernetes/21-helm-kustomize-gitops.md): the short Helm overview, Kustomize, Argo CD.
- [Scenario deep dives](../hemant-scenario-deep-dives.md): A1 (Helm drift) in Hemant's format, plus B3 (mutable tags), B5 (ConfigMap changes), B7 (stuck rollout) and B8 (removed APIs after an EKS upgrade).
