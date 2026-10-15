# 05 · Pods ⭐

![Pod anatomy](diagrams/05-pod-anatomy.drawio.svg)

- Smallest unit you deploy: one or more containers, **always on one node together**.
- They share the **network** (one IP, `localhost`), IPC and **volumes**; each keeps its own filesystem and processes.
- The hidden **pause** container holds the network namespace, so restarts keep the IP.
- Don't create bare pods: nothing recreates them. Use a controller ([07](07-workloads.md)).

## Phase vs container state ⭐

![Pod phase vs container state](diagrams/05-pod-lifecycle.drawio.svg)

| restartPolicy | Used by |
|---|---|
| `Always` (default) | Deployments, StatefulSets, DaemonSets |
| `OnFailure` | Jobs that retry |
| `Never` | Jobs that shouldn't restart a failed container |

## Multi-container patterns

| Pattern | Example |
|---|---|
| **Sidecar** (helps all the time) | Log shipper, Envoy proxy, config reloader |
| **Ambassador** (outgoing proxy) | Local proxy to a DB cluster |
| **Adapter** (converts output) | App metrics → Prometheus format |

- **Init containers:** run one by one to completion before the app (wait for DB, migrations).
- **Native sidecar** (stable 1.33): an init container with `restartPolicy: Always`. Starts before the app, stops after it, so Job pods can finish.
- **Ephemeral containers:** added to a running pod with `kubectl debug` ([17](17-troubleshooting.md)).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
spec:
  terminationGracePeriodSeconds: 30
  volumes:
  - name: logs
    emptyDir: {}
  initContainers:
  - name: wait-for-db            # runs first, must finish
    image: busybox:1.36
    command: ["sh", "-c", "until nslookup db; do echo waiting for db; sleep 2; done"]
  - name: log-shipper            # native sidecar: keeps running
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "touch /logs/app.log; tail -F /logs/app.log"]
    volumeMounts:
    - name: logs
      mountPath: /logs
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /logs/app.log; sleep 5; done"]
    volumeMounts:
    - name: logs
      mountPath: /logs
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 5"]
```

## Graceful shutdown ⭐

![Graceful shutdown and the race](diagrams/05-graceful-shutdown.drawio.svg)

## Other pod features

- **Hooks:** `postStart`, `preStop`. **Downward API:** pod name, namespace, IP, limits as env or files.
- **QoS class** from requests and limits ([12](12-resources-and-autoscaling.md)). **Static pods** from `/etc/kubernetes/manifests` ([02](02-architecture.md)).

> **Docker link:** PID 1, SIGTERM and exit code 137 work as in [Docker 04](../docker/04-containers.md).

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Why pods, not containers? | Some containers must share network and storage and be scheduled together (app + sidecar). |
| ⭐ What do they share? | Network namespace (IP, localhost), IPC, volumes. Not the filesystem or process tree. |
| ⭐ Init container vs sidecar? | Finishes before the app vs runs alongside it for the pod's life. |
| ⭐ Errors on every deploy? | The endpoint/SIGTERM race: `preStop` sleep, SIGTERM handling, readiness, `maxUnavailable: 0`. |
| CrashLoopBackOff? | Container keeps exiting; restarts back off. `logs --previous` + exit code. |

## Practice 🖥️

```bash
kubectl apply -f practice/pod.yaml
kubectl get pod web -w
kubectl logs web -c log-shipper -f
kubectl exec -it web -c app -- sh
kubectl get pod web -o jsonpath='{.status.containerStatuses[*].state}'
kubectl delete pod web          # takes ~5 s: the preStop sleep
```
