# ☸️ Kubernetes Notes: Interview Edition

My own Kubernetes notes for the interview with Hemant (One2N), in the same format as the [Docker notes](../docker/README.md). They cover **all the core Kubernetes concepts**, checked against two complete lists: the official Kubernetes "Concepts" documentation and the CKA exam syllabus. They also fix the mistakes in the Instagram "Kubernetes Handbook" and add the depth Hemant asks about.

## How to use these notes

- **Before Friday:** read the ⭐ files in order (about 4–5 hours). Read the others after the interview, or when a topic comes up.
- For each file: read it, do its **Practice** section, then answer its **Interview angle** questions **out loud**.
- 🖥️ = he may ask you to show it live · 🔥 = Hemant's feedback topics
- **Docker link** boxes connect each idea back to the [Docker notes](../docker/README.md).

## ⚠️ Practise only on a local cluster

Your `kubectl` is currently set to a **real EKS cluster**. Before any practice command, check where kubectl points:

```bash
kubectl config current-context
```

It must say `kind-kind`. Set up a local cluster once:

```bash
brew install kind
kind create cluster
kubectl config use-context kind-kind
```

(Docker Desktop must be running.)

## Contents

| # | File | What's inside |
|---|---|---|
| 01 ⭐ | [Fundamentals](01-fundamentals.md) | Why Kubernetes, desired state, the reconciliation loop |
| 02 ⭐ | [Architecture](02-architecture.md) | Control plane, node components, add-ons, high availability |
| 03 ⭐ | [Objects and the API](03-objects-and-api.md) | YAML structure, API groups, labels, selectors, namespaces, garbage collection, finalizers |
| 04 ⭐ | [What happens on `kubectl apply`](04-kubectl-apply-flow.md) | The full flow, and where it can get stuck |
| 05 ⭐ | [Pods](05-pods.md) | Phases, init and sidecar containers, graceful shutdown |
| 06 ⭐ | [Probes](06-probes.md) | Liveness, readiness, startup |
| 07 ⭐ | [Workloads](07-workloads.md) | Deployment, StatefulSet, DaemonSet, Job, CronJob, rollouts, PodDisruptionBudgets |
| 08 ⭐ | [Services and DNS](08-services-and-dns.md) | Service types, kube-proxy, EndpointSlices, CoreDNS |
| 09 | [Ingress and Gateway API](09-ingress-and-gateway-api.md) | Ingress controllers, AWS ALB, Gateway API |
| 10 | [ConfigMaps and Secrets](10-configmaps-and-secrets.md) | Configuration, why base64 isn't encryption, external secrets |
| 11 | [Storage](11-storage.md) | Volumes, PV, PVC, StorageClass, CSI |
| 12 ⭐ | [Resources and Autoscaling](12-resources-and-autoscaling.md) | Requests and limits, QoS, quotas, HPA, VPA, Karpenter |
| 13 | [Scheduling](13-scheduling.md) | Affinity, taints and tolerations, topology spread, priority, eviction |
| 14 ⭐ | [Cluster Networking](14-cluster-networking.md) | The networking model, CNI, NetworkPolicy |
| 15 ⭐🔥 | [Security](15-security.md) | Authentication, RBAC, ServiceAccounts, Pod Security, securityContext, policies |
| 16 | [Observability](16-observability.md) | Logs, metrics, events |
| 17 ⭐ | [Troubleshooting](17-troubleshooting.md) | Flowchart, every common error, `kubectl debug` |
| 18 | [Cluster Operations](18-cluster-operations.md) | Drain, upgrades, version skew, etcd backup, certificates |
| 19 | [Extending Kubernetes](19-extending-kubernetes.md) | CRDs, operators, admission webhooks |
| 20 ⭐ | [EKS on AWS](20-eks.md) | VPC CNI, IRSA and Pod Identity, AWS Load Balancer Controller, upgrades |
| 21 | [Helm, Kustomize and GitOps](21-helm-kustomize-gitops.md) | Packaging, ArgoCD, canary and blue/green |
| 22 ⭐ | [Interview Questions](22-interview-questions.md) | 30 questions in Hemant's style |
| 23 | [kubectl Command List](23-kubectl-commands.md) | Every command by task, checked against kubectl v1.36 |

## Diagrams

All diagrams are in [diagrams/](diagrams/) as editable **`.drawio.svg`** files. They appear inside the notes. To edit one, open it in VS Code (Draw.io Integration) or [app.diagrams.net](https://app.diagrams.net).

## Mistakes in the Instagram handbook (fixed here)

- It says Secrets are "encrypted". They're only **base64-encoded**, unless encryption at rest is turned on. See [10](10-configmaps-and-secrets.md).
- Its `kubectl apply` flow skips etcd, the controllers and the network setup. See [04](04-kubectl-apply-flow.md) for the full flow.
- Its caption promises a kubectl cheat sheet, but there isn't one. [23](23-kubectl-commands.md) is a real, checked list.
