# 06 · Troubleshooting Helm

![Debugging a Helm release, in order](diagrams/06-debug-order.drawio.svg)

```bash
helm status web -n shop ; helm history web -n shop
helm list -n shop --failed ; helm list -n shop --pending
helm get manifest web -n shop ; helm get values web -n shop --all ; helm get hooks web -n shop
helm get manifest web -n shop | kubectl diff -n shop -f -
kubectl get deploy web -n shop -o yaml --show-managed-fields
```

- Step 5: Helm says `deployed` but the app is broken → debug pods like any Kubernetes problem ([Kubernetes 17](../kubernetes/17-troubleshooting.md)).

## Release states

![Release revision states](diagrams/06-release-states.drawio.svg)

## Error messages

| Error | Cause | Fix |
|---|---|---|
| `UPGRADE FAILED: … conflict with "kubectl-edit" … .spec.replicas` 🧪 | SSA: someone changed a field Helm sets | `--force-conflicts`, value in Git, or stop setting it ([03](03-server-side-apply.md)) |
| `… cannot be imported into the current release: invalid ownership metadata` 🧪 | Object made outside Helm | `--take-ownership` (+ `--force-conflicts` if hand-edited) |
| `another operation (install/upgrade/rollback) is in progress` | Killed run left `pending-*` | `helm history`, `helm rollback web <last deployed>`; CI concurrency group |
| `has no deployed releases` | First install failed | `helm uninstall` and reinstall, or `--rollback-on-failure` on install |
| `cannot re-use a name that is still in use` | `install` on an existing name | `helm upgrade --install` |
| `no matches for kind "PodDisruptionBudget" in version "policy/v1beta1"` | **Stored** manifest uses a removed API | `helm mapkubeapis` plugin ([B8](../hemant-scenario-deep-dives.md)) |
| Timeout with `--wait` | Pods never ready (pull, probes, resources) | Debug pods; `--rollback-on-failure` |
| `Flag --atomic has been deprecated, use --rollback-on-failure instead` 🧪 | Old Helm 3 flag | Rename in CI |

## Scenarios

| Scenario | Answer |
|---|---|
| `deployed`, but pods crash-loop | Without `--wait` Helm 4 waits for **hooks only** (`hookOnly`): `deployed` = applied, not healthy. `--wait --rollback-on-failure`. |
| Fix pushed with the same image tag; half the pods run old code | Mutable tags + cached images (`IfNotPresent`). Unique tag (git SHA) or digest, ECR tag immutability ([B3](../hemant-scenario-deep-dives.md)). |
| ConfigMap changed via Helm, app has old config | Pod template unchanged → no rollout. `checksum/config` annotation ([05](05-flags-annotations-hooks.md)) or `rollout restart`. |
| Teammate ran `kubectl rollout undo` in prod | Git, Helm and cluster now disagree; next deploy brings the bad version back. Roll back with the deploying tool: `helm rollback`, or `git revert` with GitOps. |
| Argo CD + Helm charts: does `helm list` show them? | No. Argo CD **renders** (like `helm template`) and applies itself. Self-heal fixes drift; `ignoreDifferences` on `/spec/replicas` for HPAs. |

## Interview angle

| Question | Answer |
|---|---|
| ⭐ CI fails: another operation is in progress | A killed upgrade left `pending-upgrade`. `helm history`, roll back to the last deployed revision, stop concurrent deploys. |
| What did Helm actually apply? | `helm get manifest` (+ `values --all`, `hooks`), then diff against the cluster with `-n`. |
| Helm says deployed but the app is down | Helm doesn't wait for pods unless asked: `--wait`. |
