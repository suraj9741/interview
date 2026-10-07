# 23 · kubectl Command List

Every kubectl command you're likely to need, grouped by task. Each command and flag was checked against the `--help` output of **kubectl v1.36** on your Mac.

**Placeholders:** `<pod>` · `<deploy>` · `<svc>` · `<node>` · `<ns>`

⚠️ **First, always:** `kubectl config current-context`. Practise only on `kind-kind`, never on a work cluster by accident.

---

## ⭐ The 20 to know by heart

| Command | What it does |
|---|---|
| `kubectl get pods -o wide` | Pods with node, IP and status |
| `kubectl get pods -A` | Pods in every namespace |
| `kubectl describe pod <pod>` | Details and **events** (the first stop for any problem) |
| `kubectl logs <pod> --previous` | Logs of the **crashed** container |
| `kubectl logs -f deploy/<deploy>` | Follow a deployment's logs |
| `kubectl exec -it <pod> -- sh` | Shell inside a pod |
| `kubectl apply -f app.yaml` | Create or update from YAML |
| `kubectl delete -f app.yaml` | Delete what the file created |
| `kubectl get events --sort-by=.lastTimestamp` | What just happened in the namespace |
| `kubectl rollout status deployment/<deploy>` | Watch a rollout finish |
| `kubectl rollout undo deployment/<deploy>` | Roll back |
| `kubectl scale deployment/<deploy> --replicas=5` | Change the replica count |
| `kubectl set image deployment/<deploy> app=myapi:1.5` | Deploy a new image |
| `kubectl get svc,endpointslices` | Services and the pod IPs behind them |
| `kubectl port-forward svc/<svc> 8080:80` | Reach a Service from your laptop |
| `kubectl top pods` | CPU and memory use (needs metrics-server) |
| `kubectl auth can-i create pods -n <ns>` | Check RBAC permissions |
| `kubectl explain deployment.spec.strategy` | Documentation for any field |
| `kubectl create deployment web --image=nginx:1.27 --dry-run=client -o yaml` | **Generate YAML** without creating anything |
| `kubectl debug -it <pod> --image=busybox:1.36 --target=<container>` | Debug a pod that has no shell |

---

## 1. Context and cluster info

| Command | What it does |
|---|---|
| `kubectl config get-contexts` | List the clusters and contexts you can use |
| `kubectl config current-context` | Which cluster you're pointed at |
| `kubectl config use-context kind-kind` | Switch cluster |
| `kubectl config set-context --current --namespace=shop` | Set the default namespace |
| `kubectl cluster-info` | API server and CoreDNS addresses |
| `kubectl version` | Client and server versions |
| `kubectl api-resources` | Every resource type (short names, namespaced or not) |
| `kubectl api-versions` | Every API group and version |
| `kubectl explain pod.spec.containers.resources` | Field documentation |

## 2. Get and inspect

| Command | What it does |
|---|---|
| `kubectl get pods -n shop` | Pods in one namespace |
| `kubectl get pods -l app=web --show-labels` | Filter by label and show labels |
| `kubectl get pods --field-selector=status.phase!=Running -A` | Every pod that isn't Running |
| `kubectl get pods -w` | Watch changes live |
| `kubectl get deploy,rs,pods,svc` | Several types at once |
| `kubectl get pod <pod> -o yaml` | The full object, including `status` |
| `kubectl get pods -o jsonpath='{.items[*].status.podIP}'` | Pull out exact fields |
| `kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName` | Choose your own columns |
| `kubectl get pods --sort-by=.status.startTime` | Sort the output |
| `kubectl describe deployment <deploy>` | Details, conditions, events |
| `kubectl get events -A --sort-by=.lastTimestamp` | Events across the cluster |

## 3. Create, apply, delete

| Command | What it does |
|---|---|
| `kubectl apply -f app.yaml` | Create or update (declarative) |
| `kubectl apply -f k8s/` | Apply every file in a folder |
| `kubectl apply -k overlays/prod` | Apply a Kustomize overlay |
| `kubectl diff -f app.yaml` | Show what `apply` **would** change |
| `kubectl create deployment web --image=nginx:1.27 --replicas=3` | Quick Deployment (imperative) |
| `kubectl expose deployment web --port=80 --target-port=8080` | Make a Service for it |
| `kubectl create service clusterip web --tcp=80:8080` | Service only |
| `kubectl run tmp --rm -it --image=busybox:1.36 --restart=Never -- sh` | Throwaway debug pod |
| `kubectl edit deployment <deploy>` | Edit live (avoid in GitOps-managed clusters) |
| `kubectl delete pod <pod>` | Delete (a controller recreates it) |
| `kubectl delete pod <pod> --grace-period=0 --force` | ⚠️ Force delete a stuck pod (last resort) |

**Generate YAML instead of writing it** (`--dry-run=client -o yaml`):

```bash
kubectl create deployment web --image=nginx:1.27 --dry-run=client -o yaml
kubectl create service clusterip web --tcp=80:8080 --dry-run=client -o yaml
kubectl create configmap app-config --from-literal=LOG_LEVEL=info --dry-run=client -o yaml
kubectl create job hello --image=busybox:1.36 --dry-run=client -o yaml -- echo hello
kubectl create cronjob tick --image=busybox:1.36 --schedule="*/5 * * * *" --dry-run=client -o yaml -- date
kubectl create ingress shop --rule="shop.example.com/api*=api:80" --dry-run=client -o yaml
```

## 4. Logs, exec, debug, port-forward

| Command | What it does |
|---|---|
| `kubectl logs <pod> -c <container>` | One container's logs |
| `kubectl logs <pod> --previous` | The crashed container's logs |
| `kubectl logs -f --tail=100 --since=10m <pod>` | Follow, starting from recent lines |
| `kubectl logs -l app=web --all-containers --prefix` | Logs from every matching pod |
| `kubectl exec -it <pod> -c <container> -- sh` | Shell in one container |
| `kubectl exec <pod> -- env` | Run one command |
| `kubectl debug -it <pod> --image=busybox:1.36 --target=<container>` | Add a temporary debug container |
| `kubectl debug <pod> -it --copy-to=<pod>-debug --container=<container> -- sh` | Debug a copy of the pod |
| `kubectl debug node/<node> -it --image=busybox:1.36` | Shell on a node (host files at `/host`) |
| `kubectl port-forward svc/<svc> 8080:80` | Laptop port 8080 → Service |
| `kubectl port-forward pod/<pod> 5432:5432` | Laptop → one pod |
| `kubectl cp <pod>:/etc/nginx/nginx.conf ./nginx.conf` | Copy a file out (needs `tar` in the image) |

## 5. Deployments and rollouts

| Command | What it does |
|---|---|
| `kubectl scale deployment/<deploy> --replicas=5` | Scale |
| `kubectl set image deployment/<deploy> app=myapi:1.5` | New image → rolling update |
| `kubectl rollout status deployment/<deploy>` | Wait for and watch the rollout |
| `kubectl rollout history deployment/<deploy>` | Past revisions |
| `kubectl rollout undo deployment/<deploy> --to-revision=2` | Roll back to a specific revision |
| `kubectl rollout restart deployment/<deploy>` | Recreate the pods (for example after a ConfigMap change) |
| `kubectl rollout pause deployment/<deploy>` / `resume` | Pause or resume a rollout |
| `kubectl autoscale deployment/<deploy> --min=2 --max=10 --cpu=60%` | Create an HPA |
| `kubectl get hpa` | HPA status |

## 6. Labels, annotations, patches

| Command | What it does |
|---|---|
| `kubectl label pod <pod> tier=frontend` | Add a label |
| `kubectl label pod <pod> tier-` | Remove a label |
| `kubectl annotate deployment <deploy> owner=team-a` | Add an annotation |
| `kubectl patch deployment <deploy> -p '{"spec":{"replicas":2}}'` | Patch fields |

## 7. Nodes

| Command | What it does |
|---|---|
| `kubectl get nodes -o wide` | Nodes, IPs, versions, OS |
| `kubectl get nodes -L topology.kubernetes.io/zone` | Show the zone as a column |
| `kubectl describe node <node>` | Conditions, allocated requests, pods |
| `kubectl top nodes` | Node CPU and memory use |
| `kubectl cordon <node>` / `kubectl uncordon <node>` | Stop or allow scheduling |
| `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data` | Evict pods for maintenance (respects PDBs) |
| `kubectl taint nodes <node> dedicated=gpu:NoSchedule` | Add a taint (append `-` to remove it) |

## 8. RBAC and identity

| Command | What it does |
|---|---|
| `kubectl auth can-i delete pods -n shop` | Can **I** do this? |
| `kubectl auth can-i --list -n shop` | Everything I can do |
| `kubectl auth can-i get secrets -n shop --as=system:serviceaccount:shop:app` | Can **that ServiceAccount**? |
| `kubectl auth whoami` | Who the API server thinks you are |
| `kubectl create serviceaccount app -n shop` | Create a ServiceAccount |
| `kubectl create role pod-reader --verb=get,list,watch --resource=pods -n shop` | Create a Role |
| `kubectl create rolebinding app-pods --role=pod-reader --serviceaccount=shop:app -n shop` | Bind it |
| `kubectl create token app -n shop` | Get a short-lived token for a ServiceAccount |

## 9. Config and secrets

| Command | What it does |
|---|---|
| `kubectl create configmap app-config --from-literal=LOG_LEVEL=info --from-file=app.properties` | ConfigMap from values and a file |
| `kubectl create secret generic db --from-literal=DB_PASSWORD=change-me` | Generic Secret |
| `kubectl create secret tls web-tls --cert=tls.crt --key=tls.key` | TLS Secret |
| `kubectl create secret docker-registry regcred --docker-server=ghcr.io --docker-username=<user> --docker-password=<token>` | Registry login for `imagePullSecrets` |
| `kubectl get secret db -o jsonpath='{.data.DB_PASSWORD}' \| base64 -d` | Decode a value (proves base64 isn't encryption) |

## 10. Storage and networking

| Command | What it does |
|---|---|
| `kubectl get storageclass` | Storage classes (the default is marked) |
| `kubectl get pv,pvc -A` | Volumes and claims |
| `kubectl get svc,endpointslices -n shop` | Services and their pod IPs |
| `kubectl get ingress,ingressclass -A` | Ingress rules and controllers |
| `kubectl get networkpolicy -A` | Pod firewall rules |
| `kubectl run tmp --rm -it --image=nicolaka/netshoot --restart=Never -- bash` | Network-debugging pod (dig, curl, tcpdump) |

## 11. Output formats (`-o`)

| Flag | Gives |
|---|---|
| `-o wide` | Extra columns (node, IP) |
| `-o yaml` / `-o json` | The full object |
| `-o name` | `type/name`, for scripts |
| `-o jsonpath='{...}'` | Exact fields |
| `-o custom-columns=A:.path,B:.path` | Your own table |

## 12. Kustomize and Helm (rendering locally)

| Command | What it does |
|---|---|
| `kubectl kustomize overlays/prod` | Print the final YAML of an overlay |
| `helm template web ./chart -f values-prod.yaml` | Print a chart's final YAML |
| `helm upgrade --install web ./chart -n shop -f values-prod.yaml` | Install or upgrade a release |
| `helm rollback web 2 -n shop` | Roll back a release |

## 13. Handy one-liners

| Command | What it does |
|---|---|
| `kubectl get pods -A --field-selector=status.phase=Failed` | Every failed or evicted pod |
| `kubectl delete pods -A --field-selector=status.phase=Failed` | Clean them up |
| `kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' \| sort \| uniq -c` | Which images run in the cluster, and how many of each |
| `kubectl top pods -A --sort-by=memory` | The biggest memory users |
| `kubectl rollout restart deployment -n shop` | Restart every Deployment in a namespace |
| `kubectl get events -A --field-selector type=Warning --sort-by=.lastTimestamp` | Only warnings |

> **Docker → kubectl equivalents** are in [Docker command list §15](../docker/14-docker-commands.md).
