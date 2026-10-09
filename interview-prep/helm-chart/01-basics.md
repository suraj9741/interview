# 01 · Helm Basics

![How Helm turns a chart into a running release](diagrams/01-helm-flow.drawio.svg)

## Three words

| Word | Meaning | Example |
|---|---|---|
| **Chart** | A package: templated Kubernetes YAML + default values | `./demo`, or `oci://…/demo --version 0.1.0` |
| **Release** | One installed copy of a chart, with a name, in a namespace | `web` in `shop` |
| **Revision** | One version of a release. Every install, upgrade or rollback adds one | `helm history web -n shop` → 1, 2, 3… |

**A rollback doesn't go back in time.** `helm rollback web 3` applies revision 3's manifest again and saves it as a **new** revision (e.g. 6).

## The chart folder

What `helm create demo` makes in Helm 4.2.3 🧪:

```text
demo/
├── Chart.yaml          # apiVersion: v2, name, version (the chart's), appVersion (the app's)
├── values.yaml         # default settings
├── charts/             # dependency charts (filled by helm dependency update)
└── templates/
    ├── _helpers.tpl    # named templates (names, labels), reused with include
    ├── deployment.yaml # replicas only if autoscaling is off (see 03)
    ├── hpa.yaml
    ├── httproute.yaml  # Gateway API
    ├── ingress.yaml
    ├── service.yaml
    ├── serviceaccount.yaml
    ├── NOTES.txt       # printed after install
    └── tests/          # helm test pods
```

- **`version` vs `appVersion`:** `version` is the **chart's** version (bump it when the chart changes). `appVersion` is the **app's** version (often the image tag). They're independent.
- **`crds/` folder (optional):** CRDs placed here are installed **only on the first install**. They're **never upgraded or deleted** by Helm, and they aren't templated.

## Values: which one wins?

From lowest to highest priority (the last one wins):

1. The chart's own `values.yaml`
2. A parent chart's values for its subchart
3. `-f` files, in the order given (`-f values.yaml -f values-prod.yaml`)
4. `--set`, `--set-string`, `--set-json`, `--set-file`, `--set-literal`

`helm get values web -n shop` shows only what **you** supplied. Add `--all` to see the merged result.

## Rendering: templates become YAML

Templates are **Go templates** with extra functions (from the Sprig library):

| You write | It becomes |
|---|---|
| `{{ .Values.image.tag }}` | A value from the values |
| `{{ .Release.Name }}`, `{{ .Release.Namespace }}` | The release name and namespace |
| `{{ include "demo.labels" . \| nindent 4 }}` | A named template from `_helpers.tpl`, indented |
| `{{ toYaml .Values.resources \| nindent 12 }}` | A whole block of YAML from the values |
| `{{ required "image.tag is required" .Values.image.tag }}` | Fails the render if the value is missing |
| `{{ lookup "v1" "Secret" "shop" "db" }}` | Reads a **live** object. Returns empty with `helm template` or `--dry-run=client` |

Three ways to check what will be applied:

| Command | Contacts the cluster? | Use it for |
|---|---|---|
| `helm template web ./demo -f values-prod.yaml` | No | See the final YAML; CI checks |
| `helm lint ./demo` | No | Chart mistakes |
| `helm upgrade web ./demo --dry-run=server` | Yes, but saves nothing | Real API validation and admission policies |

## Where a release is stored 🧪

There is **no Tiller** since Helm 3. The release lives in the cluster as **one Secret per revision**:

```bash
kubectl get secrets -n shop --field-selector type=helm.sh/release.v1 -o custom-columns=NAME:.metadata.name,STATUS:.metadata.labels.status --no-headers
```

```
sh.helm.release.v1.web.v1    superseded
sh.helm.release.v1.web.v2    failed
sh.helm.release.v1.web.v3    deployed
```

Decode one (base64 twice, because Helm encodes it and Kubernetes encodes it again, then gunzip):

```bash
kubectl get secret sh.helm.release.v1.web.v3 -n shop -o jsonpath='{.data.release}' | base64 -d | base64 -d | gunzip
```

It's JSON with these keys **(tested)**: `apply_method`, `chart`, `config` (your values), `hooks`, `info` (status), `manifest`, `name`, `namespace`, `version`.

- **`manifest`** is the **OLD** input of the next 3-way merge ([02](02-how-upgrades-work.md)).
- **`apply_method`** (`csa` or `ssa`) decides how the next upgrade is applied ([03](03-server-side-apply.md)).
- `--history-max` (default **10**) limits how many revision Secrets are kept.
- ⚠️ **Anyone who can read Secrets in that namespace can read your values.** Never put passwords in values; use External Secrets or Sealed Secrets.

## Repositories, OCI and dependencies

| Task | Command |
|---|---|
| Add a classic chart repository | `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`, then `helm repo update` |
| Package a chart | `helm package ./demo` → `demo-0.1.0.tgz` |
| Push to an **OCI** registry (e.g. ECR) | `helm push demo-0.1.0.tgz oci://123456789012.dkr.ecr.us-west-1.amazonaws.com/charts` |
| Install from OCI | `helm install web oci://123456789012.dkr.ecr.us-west-1.amazonaws.com/charts/demo --version 0.1.0` |
| Fetch dependencies listed in `Chart.yaml` | `helm dependency update ./demo` (writes `charts/` and `Chart.lock`) |

## Interview angle

- **"Chart vs release vs revision?"** → The package, one installed copy of it, and one version of that copy.
- **"Where does Helm 3/4 keep state?"** → In Secrets in the release's namespace, one per revision, holding the chart, values, rendered manifest and apply method. Tiller is gone.
  - **He'll push: "Security?"** → Values are readable by anyone who can read Secrets there, so never keep passwords in values.
- **"How do you see exactly what Helm will apply?"** → `helm template` locally, or `--dry-run=server` for real API validation.
- **"`version` vs `appVersion`?"** → The chart's own version vs the application's version.
- **"Why aren't my CRD changes applied on upgrade?"** → CRDs in `crds/` are installed only once and never upgraded. Upgrade them separately, or ship them as templates on purpose.
