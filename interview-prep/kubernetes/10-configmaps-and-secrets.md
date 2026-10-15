# 10 · ConfigMaps and Secrets

![Two ways config reaches a container](diagrams/10-config-to-pod.drawio.svg)

Keep configuration **out of the image**: the same image then runs in dev, QA and prod, and only its config changes ("build once, promote everywhere", model answer Q38).

## ConfigMap

- Non-sensitive key-value pairs or whole files (feature flags, URLs, `app.properties`). Maximum **1 MiB**.
- Use it as **environment variables** (`env`, `envFrom`) or as **files** (a volume).
- `immutable: true` protects it from accidental edits and reduces load on the API server.

## Secret

- For passwords, tokens, keys and certificates. Types:
  - `Opaque`: generic;
  - `kubernetes.io/tls`: a certificate and key;
  - `kubernetes.io/dockerconfigjson`: registry login, used through `imagePullSecrets`;
  - `basic-auth` and `ssh-auth`.
- ⚠️ **Secrets are base64-ENCODED, not encrypted.** Anyone who can read the Secret can decode it in one command (the Instagram handbook gets this wrong). By default they're stored in etcd **unencrypted**, unless **encryption at rest** is configured (an `EncryptionConfiguration` with a KMS provider).

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: info
  FEATURE_X: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:                  # plain text here; the API server stores it base64-encoded
  DB_PASSWORD: change-me
---
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "env; ls /etc/app; sleep 3600"]
    envFrom:
    - configMapRef:
        name: app-config            # every key becomes an env var
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: DB_PASSWORD
    volumeMounts:
    - name: config
      mountPath: /etc/app            # every key becomes a file
      readOnly: true
  volumes:
  - name: config
    configMap:
      name: app-config
```

## Env var vs mounted file

| | Environment variable | Mounted file |
|---|---|---|
| Updates when the ConfigMap or Secret changes | ❌ Only after the pod **restarts** | ✅ After a short delay (the kubelet syncs it), **but** the app must re-read the file. Not for `subPath` mounts. |
| Leak risk | Higher: shows up in crash dumps and debug output | Lower |
| Recommended for secrets | Acceptable | ✅ Better |

To roll pods when the config changes: `kubectl rollout restart deployment/x`. Or use Helm's checksum annotation, or Kustomize's `configMapGenerator`, which adds a hash to the name ([21](21-helm-kustomize-gitops.md)).

## Managing secrets properly in production ⭐ 🔥

![Secrets: from AWS Secrets Manager to the pod](diagrams/10-secrets-flow.drawio.svg)

1. **Don't put Secret YAML in Git.** base64 isn't protection.
2. Keep secrets in a **secret manager** (AWS Secrets Manager, SSM Parameter Store, Vault), and sync them in with:
   - **External Secrets Operator:** creates and refreshes a Kubernetes Secret from Secrets Manager. It authenticates with **IRSA or Pod Identity**, so no keys are stored ([20](20-eks.md)).
   - **Secrets Store CSI Driver:** mounts the secret straight into the pod as a file.
   - For GitOps without a manager: **Sealed Secrets** or **SOPS** (encrypted files that are safe to commit).
3. **Encrypt Secrets at rest** in etcd with **KMS**. On EKS, turn on (or confirm) KMS envelope encryption for the cluster.
4. **RBAC:** `get` or `list` on secrets means **reading the values**. Even `list` returns them. Grant it rarely ([15](15-security.md)).
5. **Rotate** secrets; prefer short-lived credentials (IAM roles) over static keys.

> **Docker link:** this is `-e` / `--env-file` / mounted secret files from [Docker 10](../docker/10-security.md), managed centrally for the whole cluster.

## Interview angle

- ⭐ "ConfigMap vs Secret?" → non-sensitive vs sensitive. **Secrets are only base64-encoded**; real protection comes from RBAC, encryption at rest and external managers.
- ⭐ "Are Kubernetes Secrets secure?" → not by default. Explain encoding vs encryption, etcd encryption with KMS, RBAC on `get`/`list`, and External Secrets with Secrets Manager.
- "I changed a ConfigMap. Why didn't the app change?" → env vars need a pod restart; mounted files update but the app must reload them; `subPath` mounts never update.
- "How do pods pull from a private registry?" → an `imagePullSecrets` entry with a `dockerconfigjson` Secret. On EKS, nodes pull from ECR using their IAM role.

## Practice 🖥️

```bash
kubectl apply -f practice/config.yaml
kubectl logs config-demo
kubectl get secret db-credentials -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
kubectl create secret generic demo --from-literal=k=v --dry-run=client -o yaml
```

The second command prints the pod's env vars and the files from the ConfigMap. The third proves base64 isn't security. The last one shows the YAML a command would create, without creating anything.
