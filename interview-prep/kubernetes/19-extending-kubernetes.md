# 19 · Extending Kubernetes: CRDs, Operators, Webhooks

ArgoCD, Karpenter, cert-manager, External Secrets and Gateway API are all built with these mechanisms.

![The operator pattern](diagrams/19-operator-pattern.drawio.svg)

- **CRD:** adds a new type (`kind: Backup`); stored in etcd, `kubectl get backups` works. On its own it **only stores data**.
- **Operator** = CRDs + a controller running the same loop as built-ins ([02](02-architecture.md)), encoding ops know-how (install, upgrade, failover, backup).
- Build one with **kubebuilder** or **Operator SDK** (Go, controller-runtime).

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.example.com
spec:
  group: example.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              schedule:
                type: string
              database:
                type: string
---
apiVersion: example.com/v1
kind: Backup
metadata:
  name: nightly
spec:
  schedule: "0 2 * * *"
  database: orders
```

| Operator | Custom resources |
|---|---|
| Prometheus Operator | `Prometheus`, `ServiceMonitor`, `PrometheusRule` |
| cert-manager | `Certificate`, `Issuer` |
| ArgoCD | `Application`, `ApplicationSet` |
| Karpenter | `NodePool`, `EC2NodeClass` |
| External Secrets | `ExternalSecret`, `SecretStore` |
| CloudNativePG / Strimzi | `Cluster` / `Kafka` |

## Admission control

- **Mutating webhooks** change objects (Istio sidecar injection). **Validating webhooks** accept or reject (Kyverno, Gatekeeper: "no `:latest`", "only our ECR").
- **ValidatingAdmissionPolicy** (stable 1.30): CEL rules inside the API server, no webhook to run.
- ⚠️ A webhook that's down with `failurePolicy: Fail` blocks every matching request. Run it HA.

## Other extension points

| Interface | Extends | Examples |
|---|---|---|
| **CRI** | Runtime | containerd, CRI-O |
| **CNI** | Pod networking | Calico, Cilium, VPC CNI ([14](14-cluster-networking.md)) |
| **CSI** | Volumes | EBS CSI, EFS CSI ([11](11-storage.md)) |
| Device plugins | Hardware | NVIDIA GPUs |
| Scheduler plugins | Placement | Custom scoring |
| **API aggregation** | Whole APIs | metrics-server → `metrics.k8s.io` |
| kubectl plugins | CLI | **krew** |

## Interview angle

| Question | Answer |
|---|---|
| ⭐ CRD vs operator? | New API type vs a controller that reconciles it with ops knowledge. |
| Block Docker Hub images cluster-wide? | Admission policy (Kyverno, Gatekeeper, ValidatingAdmissionPolicy) on every pod's image. |
| CRI, CNI, CSI? | Plug-in interfaces for runtime, network, storage: why Kubernetes runs anywhere. |

## Practice 🖥️

```bash
kubectl get crds
kubectl apply -f practice/backup-crd.yaml
kubectl wait --for=condition=Established crd/backups.example.com
kubectl apply -f practice/backup.yaml
kubectl get backups          # stored, but nothing acts on it: no controller
kubectl explain backup.spec
kubectl get apiservices | grep metrics
```
