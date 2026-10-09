# 07 · Helm Command List

Every command checked against **Helm 4.2.3** (`--help`, with an empty kubeconfig, so no cluster was contacted). `helm diff` is the helm-diff plugin (v3.15.11 on your laptop).

## Charts

| Command | Purpose |
|---|---|
| `helm create demo` | A starter chart |
| `helm lint ./demo` | Check the chart for mistakes |
| `helm template web ./demo -f values-prod.yaml` | Render the final YAML locally (nothing is sent) |
| `helm template web ./demo -s templates/deployment.yaml` | Render only one template |
| `helm show values ./demo` | The chart's default values |
| `helm package ./demo` | Build `demo-0.1.0.tgz` |
| `helm dependency update ./demo` | Download the dependencies listed in `Chart.yaml` |

## Repositories and OCI registries

| Command | Purpose |
|---|---|
| `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts` | Add a classic repository |
| `helm repo update` | Refresh repository indexes |
| `helm search repo prometheus` | Search the added repositories |
| `helm pull prometheus-community/prometheus --version 27.0.0` | Download a chart `.tgz` |
| `helm push demo-0.1.0.tgz oci://123456789012.dkr.ecr.us-west-1.amazonaws.com/charts` | Push to an OCI registry (e.g. ECR) |
| `helm registry login 123456789012.dkr.ecr.us-west-1.amazonaws.com` | Log in to an OCI registry |

## Deploy

| Command | Purpose |
|---|---|
| `helm upgrade --install web ./demo -n shop --create-namespace -f values-prod.yaml --set image.tag=4f2a9c1` | Install or upgrade (what CI runs) |
| `helm upgrade --install web ./demo -n shop -f values-prod.yaml --wait --rollback-on-failure --timeout 10m` | The safe CI version |
| `helm upgrade web ./demo -n shop -f values-prod.yaml --dry-run=server` | Validate against the real API, save nothing |
| `helm upgrade web ./demo -n shop -f values-prod.yaml --force-conflicts` | Take back fields someone edited by hand (SSA) |
| `helm upgrade web ./demo -n shop -f values-prod.yaml --server-side=true` | Move an old CSA release to server-side apply |

## Inspect a release

| Command | Purpose |
|---|---|
| `helm list -n shop` | Releases in a namespace (`-A` for all namespaces) |
| `helm list -A --failed` | Failed releases everywhere (`--pending` for stuck ones) |
| `helm status web -n shop` | The current state and notes |
| `helm history web -n shop` | Every revision, its state and description |
| `helm get values web -n shop --all` | The values in use (without `--all`: only the ones you supplied) |
| `helm get manifest web -n shop` | The rendered YAML Helm applied |
| `helm get hooks web -n shop` | The hooks of the release |
| `helm get metadata web -n shop` | Chart, version, status, dates |

## Drift and diffs

| Command | Purpose |
|---|---|
| `helm get manifest web -n shop \| kubectl diff -n shop -f -` | What drifted (keep `-n`!) |
| `helm get manifest web -n shop \| kubectl diff -n shop --server-side --field-manager=helm -f -` | The conflict Helm 4 will hit |
| `helm diff upgrade web ./demo -n shop -f values-prod.yaml --three-way-merge` | Preview the upgrade, **including live drift** |
| `helm diff upgrade web ./demo -n shop -f values-prod.yaml --three-way-merge --detailed-exitcode` | Same; exit code 2 = changes (for CI) |
| `kubectl get deploy web -n shop -o yaml --show-managed-fields` | Who owns each field |

## Roll back, test, remove

| Command | Purpose |
|---|---|
| `helm rollback web 3 -n shop` | Apply revision 3 again (as a new revision) |
| `helm rollback web 3 -n shop --wait` | The same, waiting until it's ready |
| `helm test web -n shop` | Run the chart's test pods |
| `helm uninstall web -n shop` | Remove the release |
| `helm uninstall web -n shop --keep-history` | Remove it, but keep its history (so it can be rolled back) |

## Plugins

| Command | Purpose |
|---|---|
| `helm plugin list` | Installed plugins (you have `diff`) |
| `helm diff version` | The helm-diff version |
