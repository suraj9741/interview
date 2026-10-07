# 16 · Observability: Logs, Metrics, Events

The full stack design is in the model answers (Q45–Q49), with a [diagram](../diagrams/46-observability-stack.drawio.svg). This file covers what's **specific to Kubernetes**.

## Logs

- Apps write to **stdout and stderr**. The container runtime saves that to files **on the node** (`/var/log/pods/...`). `kubectl logs` reads them **through the kubelet**.
- The kubelet **rotates** these files (by default about 10 MiB × 5 files per container).
- ⚠️ When a pod is **deleted** or its node disappears, those logs are **gone**. That's why you **ship** logs: a **DaemonSet** (Fluent Bit, Grafana Alloy) tails every node's log files and sends them to Loki, CloudWatch or Elasticsearch.
- `kubectl logs <pod> --previous` shows the logs of the **crashed** container. This is the most important CrashLoopBackOff command.
- **Control plane logs on EKS:** turn on `api`, `audit`, `authenticator`, `controllerManager` and `scheduler` logs (they go to CloudWatch).

## Metrics

| Tool | Gives you | Used for |
|---|---|---|
| **metrics-server** | Current CPU and memory per pod and node (no history) | `kubectl top`, **HPA** |
| **cAdvisor** (built into the kubelet) | Container CPU, memory, network and disk | Scraped by Prometheus |
| **kube-state-metrics** | The **state of objects**: desired vs available replicas, pod phase, restart counts | Alerts like "Deployment has fewer pods than wanted" |
| **node_exporter** | Node OS metrics | Disk full, load, network |
| **Prometheus + Grafana** (`kube-prometheus-stack`) | Collection, storage, alerting, dashboards | Long-term monitoring |

## Events

- Objects record **events**: `Scheduled`, `Pulling`, `Failed`, `BackOff`, `Unhealthy`, `FailedScheduling`, `OOMKilling`…
- `kubectl describe` shows them at the bottom; `kubectl get events --sort-by=.lastTimestamp` lists them all.
- ⚠️ Events are kept for only about **1 hour** by default. Export them (for example with an event exporter) if you need history.

## What to alert on (Kubernetes-specific)

- Pods in **CrashLoopBackOff**, or restart count rising
- **Deployment replicas unavailable** (from kube-state-metrics)
- Pods **Pending** too long
- Nodes **NotReady**, or under memory/disk pressure
- **PVCs nearly full**
- **API server** errors and latency
- Certificates about to expire
- HPA stuck at `maxReplicas`

## Traces

Instrument apps with **OpenTelemetry**. Run an OTel Collector (a DaemonSet or a Deployment) → Tempo or X-Ray. Connect logs, metrics and traces with **trace IDs** and shared labels (`namespace`, `pod`, `app`).

## Interview angle

- ⭐ "Where do pod logs go, and why might `kubectl logs` show nothing?" → the node's files read through the kubelet. If the pod was deleted or its node is gone, the logs are lost unless you ship them.
- ⭐ "metrics-server vs Prometheus?" → current CPU/memory for `top` and the HPA vs full metrics history, queries and alerts.
- "How do you see why a pod restarted?" → `describe` (last state, exit code, events), `logs --previous`, and the restart-count metric.

## Practice 🖥️

```bash
kubectl logs deploy/web --tail=50 -f
kubectl logs <pod> -c <container> --previous
kubectl get events -A --sort-by=.lastTimestamp
kubectl top pods -A --sort-by=memory
```
