# 15 · Kubernetes Security ⭐🔥

![7 security layers](diagrams/15-security-layers.drawio.svg)

## 1. API access: 3 gates

![API request pipeline](diagrams/02-api-request-pipeline.drawio.svg)

- **EKS:** IAM users or roles map in through **access entries** (old way: `aws-auth` ConfigMap).
- Validating admission options: **Pod Security Admission**, ResourceQuota, **ValidatingAdmissionPolicy** (CEL, stable 1.30), Kyverno, OPA Gatekeeper.

## RBAC ⭐

![RBAC: subjects, bindings and roles](diagrams/15-rbac.drawio.svg)

| Object | Scope | Meaning |
|---|---|---|
| **Role** | Namespace | `apiGroups` + `resources` + `verbs` |
| **ClusterRole** | Cluster | Same, for cluster resources or reuse |
| **RoleBinding** | Namespace | Grants a Role **or ClusterRole** in one namespace |
| **ClusterRoleBinding** | Cluster | Grants a ClusterRole everywhere |

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-reader
  namespace: shop
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: shop
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-reader-pods
  namespace: shop
subjects:
- kind: ServiceAccount
  name: app-reader
  namespace: shop
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## 2. ServiceAccounts

- The identity pods use for the API. Each namespace has `default`.
- Pods get a **projected token**: short-lived, auto-refreshed, one audience. No auto long-lived token Secrets since 1.24.
- App never calls the API → `automountServiceAccountToken: false`.
- **IRSA / Pod Identity** → AWS IAM role, no stored keys ([20](20-eks.md)).

## 3. Pod Security Standards ⭐

| Level | Allows |
|---|---|
| `privileged` | Everything (system components) |
| `baseline` | No privileged, hostNetwork, hostPID, hostPath… |
| `restricted` | Baseline + non-root, drop ALL caps, no privilege escalation, seccomp |

- Enforced **per namespace** by label: `kubectl label ns shop pod-security.kubernetes.io/enforce=restricted` (modes `enforce`, `audit`, `warn`).
- Replaced **PodSecurityPolicy** (removed in 1.25).

```yaml
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapi:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
```

## 5. Supply chain (🔥 model answer Q55)

- **CI:** scan images (Trivy), scan manifests / charts (Checkov, kube-linter, `trivy config`), sign (cosign).
- **Admission:** trusted registries only, **verify signatures** (Kyverno `verifyImages`), block `:latest`, root, missing limits.

## 7. Detection

- EKS `audit` logs → CloudWatch · Falco / GuardDuty Runtime Monitoring · `kube-bench` (CIS).

> **Docker link:** `securityContext` = `--user`, `--read-only`, `--cap-drop ALL`, `no-new-privileges` ([Docker 10](../docker/10-security.md)).

## Interview angle

| Question | Answer |
|---|---|
| ⭐🔥 Secure a cluster? | Walk the 7 layers in order; don't just list tools. |
| ⭐ Role vs ClusterRole, bindings? | Namespace vs cluster. A RoleBinding can grant a ClusterRole in one namespace. |
| ⭐ Dangerous RBAC? | secrets get/list, create pods, exec, escalate/bind/impersonate, wildcards. |
| ⭐ Pod → AWS without keys? | IRSA or Pod Identity ([20](20-eks.md)). |
| What replaced PSP? | Pod Security Admission + Kyverno / Gatekeeper for custom rules. |
| 🔥 Security in the pipeline? | Scan in CI, verify at admission, detect at runtime (Q55–Q56). |

## Practice 🖥️

```bash
kubectl auth can-i create deployments -n shop
kubectl auth can-i list secrets -n shop --as=system:serviceaccount:shop:app-reader
kubectl apply -f practice/rbac.yaml
kubectl auth can-i list pods -n shop --as=system:serviceaccount:shop:app-reader
kubectl label ns shop pod-security.kubernetes.io/enforce=restricted
kubectl -n shop run bad --image=nginx:1.27 --privileged   # rejected by Pod Security Admission
```
