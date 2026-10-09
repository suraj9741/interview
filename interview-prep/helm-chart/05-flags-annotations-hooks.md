# 05 · Flags, Annotations and Hooks

Every flag here was checked against **`helm upgrade --help` in Helm 4.2.3**. 🧪 = tested on the practice cluster.

## 🔴 Must know: the 5 server-side apply and safety flags ⭐

| Flag | What it does | Detail |
|---|---|---|
| `--server-side true\|false\|auto` 🧪 | **How** Helm writes changes | `install` default `true` (SSA). `upgrade` and `rollback` default `auto`: reuse the release's stored `apply_method` (`ssa` or `csa`). `false` = the 3-way merge (CSA) |
| `--force-conflicts` 🧪 | Overrides other owners' fields | Without it, a field changed by `kubectl edit` gives `UPGRADE FAILED: … conflict with "kubectl-edit" … .spec.replicas` |
| `--take-ownership` 🧪 | Adopts objects created outside Helm | Skips the `invalid ownership metadata` check. ⚠️ Doesn't override field owners, so you may also need `--force-conflicts` |
| `--force-replace` 🧪 (was `--force`) | **Replaces** the object with NEW | Wipes **every** hand-made change. `--force` still works, with `Flag --force has been deprecated, use --force-replace instead` |
| `--rollback-on-failure` (was `--atomic`) | Automatic undo on failure | Upgrade: back to the last good revision. Install: uninstall. Turns on `--wait=watcher`. `--atomic` still works with a deprecation warning |

## 🟠 Waiting and safety

| Flag | Detail |
|---|---|
| `--wait [watcher\|hookOnly\|legacy]` | ⚠️ **Omitted = `hookOnly`**: Helm waits for **hooks only, not your pods**. `--wait` alone = `watcher`: watches every object until it's ready. `legacy` = the old Helm 3 wait |
| `--timeout 5m0s` | Time limit for each operation (default 5 minutes) |
| `--wait-for-jobs` | With `--wait`, also waits for Jobs to finish |
| `--cleanup-on-fail` | Deletes **new** objects created by a failed upgrade |
| `--dry-run=client\|server\|none` + `--hide-secret` | `client` = render only, no cluster. `server` = the API server validates it (schema and admission policies) but saves nothing. `--hide-secret` keeps Secrets out of the output |

🎯 **In CI:** `--wait --rollback-on-failure --timeout 10m`. Without `--wait`, a release shows `deployed` even while its pods crash-loop.

## 🟡 Values

| Flag | Detail |
|---|---|
| `-f`, `--set`, `--set-string`, `--set-json`, `--set-file`, `--set-literal` | Ways to pass values; the later one wins. `--set-literal` takes the text exactly (no splitting on commas or dots) |
| `--reuse-values` | The last release's values + your overrides. ⚠️ **New defaults in a newer chart version are ignored** |
| `--reset-values` | The chart's defaults + your overrides only |
| `--reset-then-reuse-values` | Chart defaults → the last release's values → your overrides. **Fixes the `--reuse-values` gotcha** |
| `--history-max 10` | How many revision Secrets to keep (`0` = no limit) |

## 🔵 Everything else

| Group | Flags |
|---|---|
| Install from upgrade | `-i/--install`, `--create-namespace` |
| Hooks and CRDs | `--no-hooks`, `--skip-crds` |
| Rendering | `--post-renderer` + `--post-renderer-args` (in Helm 4, the name of a **post-renderer plugin**), `--enable-dns`, `--hide-notes`, `--render-subchart-notes` |
| Chart version | `--version` (a tag, or a range like `^2.0`), `--devel`, `--dependency-update`, `--verify` |
| Validation | `--skip-schema-validation` (values.schema.json), `--disable-openapi-validation` |
| Release record | `-l/--labels`, `--description`, `-o json\|yaml` |

**Other commands:**
- **`helm install` only:** `--generate-name`, `--replace` (reuse a deleted release's name; unsafe in production).
- **`helm rollback`:** also has `--server-side`, `--force-conflicts`, `--force-replace`, `--wait`, `--cleanup-on-fail`, `--no-hooks`.
- **`helm uninstall`:** `--keep-history` (keep the revisions, so you can roll back), `--cascade background|orphan|foreground`, `--ignore-not-found` (good for repeatable CI), `--wait`.

## What happens during `helm upgrade`, in order

![What happens during helm upgrade, in order](diagrams/05-upgrade-lifecycle.drawio.svg)

## Helm annotations (you put these on chart objects) 🧪

| Annotation | Values | Detail |
|---|---|---|
| `helm.sh/hook` | `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-rollback`, `post-rollback`, `pre-delete`, `post-delete`, `test` | Runs the object (usually a Job) at that moment, e.g. a DB migration as `pre-upgrade` |
| `helm.sh/hook-weight` | A number in quotes: `"-5"`, `"0"` | Order: the lowest runs first |
| `helm.sh/hook-delete-policy` | `before-hook-creation` (the default), `hook-succeeded`, `hook-failed` | 🧪 With `hook-succeeded`, the Job was **deleted** right after it finished |
| `helm.sh/hook-output-log-policy` | `hook-succeeded`, `hook-failed` | Helm **prints the hook's logs**. 🧪 `level=INFO msg="running migration v42\ndone"` |
| `helm.sh/resource-policy` | `keep` | Helm never deletes it (uninstall, upgrade, or removed from the chart). 🧪 `These resources were kept due to the resource policy: [ConfigMap] keep-me` |

**Helm adds these itself** (the ownership marks), so don't set them by hand:
- the label `app.kubernetes.io/managed-by: Helm`;
- the annotations `meta.helm.sh/release-name` and `meta.helm.sh/release-namespace`.

If they're missing on an existing object, install or upgrade fails with `invalid ownership metadata` 🧪. Fix it with `--take-ownership`.

**The tested hook** (a `pre-install,pre-upgrade` migration Job):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    helm.sh/hook: pre-install,pre-upgrade
    helm.sh/hook-weight: "0"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
    helm.sh/hook-output-log-policy: hook-succeeded,hook-failed
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: busybox:1.36
          command: ["sh", "-c", "echo running migration v42; echo done"]
```

## Another useful pattern: roll pods when config changes

Pods don't restart when only a ConfigMap changes. Add a checksum of the ConfigMap to the **pod template**:

```yaml
spec:
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

Any change to the ConfigMap changes the pod template, which starts a rollout ([scenario deep dives](../hemant-scenario-deep-dives.md), B5).

## Interview angle

- ⭐ **"How do you deploy with Helm in CI safely?"** → `helm upgrade --install … --wait --rollback-on-failure --timeout 10m`, with an immutable image tag (the git SHA), after `helm lint`, `helm template` and a `helm diff --three-way-merge` preview.
- **"How do you run DB migrations with Helm?"** → A `pre-upgrade` hook Job, with a `hook-delete-policy` of `before-hook-creation,hook-succeeded`. Mind that Helm waits for it, and that a failed hook fails the release.
- **"How do you stop Helm deleting a PVC on uninstall?"** → `helm.sh/resource-policy: keep`. It's then orphaned and must be cleaned up by hand.
- **"`--reuse-values` caused a bug after a chart upgrade. Why?"** → It ignores new defaults in the new chart. Use `--reset-then-reuse-values`, or always pass full values files.
