#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/kubernetes/*.md.

Run once:  python3 tools/diagrams_kubernetes.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "kubernetes" / "diagrams"


def reconciliation_loop():
    d = Diagram("01-reconciliation-loop", 760, 360, "The reconciliation loop (every controller runs this)")
    d.box("desired", 40, 70, 200, 60, "Desired state\n(spec, from your YAML)", "blue")
    d.box("actual", 40, 230, 200, 60, "Actual state\n(what is really running)", "yellow")
    d.box("compare", 300, 150, 160, 60, "Compare\n(controller)", "purple")
    d.box("act", 540, 150, 180, 60, "Act\ncreate / delete / update", "green")
    d.edge("desired", "compare", "watch")
    d.edge("actual", "compare", "observe")
    d.edge("compare", "act", "difference found")
    d.edge("act", "actual", "changes the cluster", points=[(630, 260)])
    d.text("example", 0, 310, 760, 40,
           "Example: want 3 pods, 1 crashes → actual 2 → controller creates 1 → actual 3 again (self-healing)", size=12)
    return d


def architecture():
    d = Diagram("02-architecture", 900, 600, "Kubernetes architecture")
    d.box("kubectl", 130, 46, 180, 40, "kubectl / CI / you", "white")
    d.group("cp", 20, 100, 400, 440, "Control plane", "blue", align="left")
    d.box("api", 60, 145, 320, 54, "kube-apiserver\nthe front door: auth, RBAC, admission", "purple")
    d.box("etcd", 60, 240, 140, 80, "etcd\nall cluster state", "yellow", shape="cylinder")
    d.box("sched", 240, 240, 140, 54, "kube-scheduler\npicks a node", "green")
    d.box("cm", 60, 345, 320, 54, "kube-controller-manager\nDeployment, ReplicaSet, Node… controllers", "green")
    d.box("ccm", 60, 425, 320, 54, "cloud-controller-manager\ncloud LBs, routes, nodes", "gray")
    d.group("n1", 480, 100, 400, 210, "Worker node 1", "gray")
    d.box("kubelet1", 500, 140, 170, 50, "kubelet\nruns pods, probes", "orange")
    d.box("proxy1", 690, 140, 170, 50, "kube-proxy\nService rules", "orange")
    d.box("rt1", 500, 220, 170, 54, "containerd (CRI)\n+ CNI plugin", "white")
    d.box("p1a", 690, 225, 80, 40, "Pod", "green")
    d.box("p1b", 780, 225, 80, 40, "Pod", "green")
    d.group("n2", 480, 330, 400, 210, "Worker node 2", "gray")
    d.box("kubelet2", 500, 370, 170, 50, "kubelet\nruns pods, probes", "orange")
    d.box("proxy2", 690, 370, 170, 50, "kube-proxy\nService rules", "orange")
    d.box("rt2", 500, 450, 170, 54, "containerd (CRI)\n+ CNI plugin", "white")
    d.box("p2a", 690, 455, 80, 40, "Pod", "green")
    d.box("p2b", 780, 455, 80, 40, "Pod", "green")
    d.edge("kubectl", "api", "HTTPS")
    d.edge("api", "etcd", "only the API server\ntalks to etcd", both=True)
    d.edge("api", "sched", "watch", both=True)
    d.edge("cm", "api", "watch", both=True)
    d.edge("api", "kubelet1", "watch /\nstatus", both=True)
    d.edge("api", "kubelet2", both=True, points=[(450, 185), (450, 395)])
    d.edge("kubelet1", "rt1", "CRI")
    d.edge("kubelet2", "rt2", "CRI")
    d.text("addons", 0, 560, 900, 30,
           "Add-ons (run as pods): CoreDNS (DNS) · CNI plugin (pod networking) · metrics-server · ingress / gateway controller",
           size=11)
    return d


def node_internals():
    d = Diagram("02-node-internals", 900, 520, "Inside a worker node: who calls whom")
    d.box("api", 300, 46, 300, 46, "kube-apiserver (control plane)", "purple")
    d.group("node", 20, 120, 860, 350, "Worker node", "gray")
    d.box("kubelet", 50, 165, 230, 56, "kubelet\nnode agent, port 10250", "orange")
    d.box("proxy", 620, 165, 230, 56, "kube-proxy\nwatches Services, EndpointSlices", "orange")
    d.box("containerd", 50, 265, 230, 56, "containerd\nCRI server: images, sandboxes", "white")
    d.box("cni", 335, 265, 230, 56, "CNI plugin\npod IP + routes", "white")
    d.box("rules", 620, 265, 230, 56, "iptables / nftables rules\nService IP → pod IPs", "white")
    d.box("shim", 50, 360, 230, 46, "containerd-shim (one per pod)", "white")
    d.box("runc", 50, 420, 230, 36, "runc: namespaces + cgroups", "gray")
    d.group("pod", 335, 355, 230, 100, "Pod", "green")
    d.box("pause", 350, 390, 95, 50, "pause\nholds netns", "green", size=11)
    d.box("app", 455, 390, 95, 50, "app\ncontainer", "green", size=11)
    d.edge("api", "kubelet", "watch my pods /\nreport status", both=True)
    d.edge("api", "proxy", "watch")
    d.edge("kubelet", "containerd", "CRI (gRPC)")
    d.edge("containerd", "cni", "CNI")
    d.edge("containerd", "shim")
    d.edge("shim", "runc")
    d.edge("runc", "pause", points=[(320, 438), (320, 415)])
    d.edge("cni", "pause", "assign IP")
    d.edge("proxy", "rules", "program")
    d.text("caption", 0, 480, 900, 30,
           "kubelet never runs containers itself: it asks containerd over CRI. kube-proxy never forwards packets: the kernel rules do.",
           size=11)
    return d


def labels_selectors():
    d = Diagram("03-labels-selectors", 860, 340, "Labels and selectors connect objects")
    d.box("deploy", 30, 70, 230, 60, "Deployment web\nselector: app=web", "blue")
    d.box("rs", 30, 170, 230, 54, "ReplicaSet\nselector: app=web + hash", "blue")
    d.box("p1", 330, 60, 190, 54, "Pod web-a\nlabels: app=web", "green")
    d.box("p2", 330, 140, 190, 54, "Pod web-b\nlabels: app=web", "green")
    d.box("p3", 330, 220, 190, 54, "Pod web-c\nlabels: app=web", "green")
    d.box("svc", 600, 70, 220, 60, "Service web\nselector: app=web", "orange")
    d.box("other", 600, 220, 220, 54, "Pod api-x\nlabels: app=api (not selected)", "gray")
    d.edge("deploy", "rs", "owns")
    d.edge("rs", "p1")
    d.edge("rs", "p2", "creates\n& counts")
    d.edge("rs", "p3")
    d.edge("svc", "p1")
    d.edge("svc", "p2", "sends\ntraffic")
    d.edge("svc", "p3")
    d.text("caption", 0, 296, 860, 36,
           "Change a pod's label and it leaves both the ReplicaSet (which replaces it) and the Service (which stops sending it traffic).",
           size=11)
    return d


def apply_flow():
    d = Diagram("04-kubectl-apply-flow", 1000, 480, "What happens on kubectl apply (steps match the notes)")
    d.box("n1", 20, 60, 170, 64, "1 · kubectl\nsends HTTPS request", "white")
    d.box("n2", 230, 60, 230, 64, "2–4 · API server\nauthN → RBAC → admission", "purple")
    d.box("n3", 500, 52, 150, 80, "5 · etcd\nobject saved", "yellow", shape="cylinder")
    d.box("n4", 690, 60, 290, 64, "6 · Deployment controller\ncreates a ReplicaSet", "green")
    d.box("n5", 690, 190, 290, 64, "7 · ReplicaSet controller\ncreates 3 Pods (Pending, no node)", "green")
    d.box("n6", 380, 190, 270, 64, "8 · Scheduler\nfilter → score → bind to a node", "green")
    d.box("n7", 20, 190, 320, 64, "9 · kubelet on that node\nsandbox → CNI gives IP → pull → start", "orange")
    d.box("n8", 20, 320, 320, 64, "10 · Probes\nstartup → liveness / readiness", "orange")
    d.box("n9", 380, 320, 600, 64,
          "11 · Ready → EndpointSlice updated → kube-proxy rules on every node\ntraffic now reaches the pod", "blue")
    d.edge("n1", "n2")
    d.edge("n2", "n3")
    d.edge("n3", "n4", "watch")
    d.edge("n4", "n5")
    d.edge("n5", "n6")
    d.edge("n6", "n7", "nodeName set")
    d.edge("n7", "n8")
    d.edge("n8", "n9")
    d.text("caption", 0, 410, 1000, 50,
           "kubectl apply returns as soon as step 5 is done. Steps 6–11 happen afterwards, asynchronously.\n"
           "Watch them live: kubectl get events --sort-by=.lastTimestamp -w", size=12)
    return d


def pod_anatomy():
    d = Diagram("05-pod-anatomy", 820, 380, "Inside a pod")
    d.group("pod", 30, 50, 560, 300, "Pod  ·  one IP: 10.0.1.23  ·  scheduled as one unit", "blue")
    d.box("init", 60, 100, 230, 54, "init container\nruns first, must finish", "yellow")
    d.box("side", 330, 100, 230, 54, "native sidecar\nrestartPolicy: Always", "purple")
    d.box("app", 60, 180, 500, 54, "app container\nyour process, PID 1 of its container", "green")
    d.box("net", 60, 260, 240, 54, "shared network namespace\nlocalhost between containers", "white")
    d.box("vol", 320, 260, 240, 54, "shared volume (emptyDir)\nfiles between containers", "white")
    d.edge("init", "app", "then")
    d.text("order", 610, 60, 190, 280,
           "Start order:\n1. init containers (in order)\n2. sidecars start\n3. app containers start\n\n"
           "Stop order:\n1. app gets SIGTERM\n2. sidecars stop last", size=11, align="left")
    return d


def deployment_rollout():
    d = Diagram("07-deployment-rollout", 880, 400, "Rolling update: v1 → v2 (maxSurge 1, maxUnavailable 0)")
    d.box("deploy", 330, 50, 220, 56, "Deployment api\nimage: v1 → v2", "blue")
    d.box("rs1", 90, 150, 250, 56, "ReplicaSet v1 (old)\nscaling down: 3 → 0", "gray")
    d.box("rs2", 540, 150, 250, 56, "ReplicaSet v2 (new)\nscaling up: 0 → 3", "green")
    for i, x in enumerate((70, 175, 280)):
        d.box(f"o{i}", x, 250, 90, 40, "v1 pod", "gray")
    for i, x in enumerate((515, 620, 725)):
        d.box(f"n{i}", x, 250, 90, 40, "v2 pod", "green")
    d.edge("deploy", "rs1", "kept for rollback")
    d.edge("deploy", "rs2", "creates")
    for i in range(3):
        d.edge("rs1", f"o{i}")
        d.edge("rs2", f"n{i}")
    d.text("caption", 0, 320, 880, 60,
           "New pods must pass readiness before old ones are removed.\n"
           "kubectl rollout undo = scale the old ReplicaSet back up.", size=12)
    return d


def service_traffic():
    d = Diagram("08-service-traffic", 920, 420, "How Service traffic reaches a pod")
    d.box("client", 30, 80, 170, 56, "Client pod\ncurl http://web", "white")
    d.box("dns", 30, 220, 170, 56, "CoreDNS\nweb → 10.96.12.34", "purple")
    d.group("node", 240, 50, 300, 300, "Client's node", "gray")
    d.box("kp", 270, 110, 240, 70, "kube-proxy rules\n(iptables / nftables)\nDNAT 10.96.12.34:80 → pod IP:8080",
          "orange", size=11)
    d.box("es", 270, 220, 240, 70, "EndpointSlice web\n10.0.1.5 · 10.0.2.7 · 10.0.3.9\n(ready pods only)", "blue", size=11)
    d.box("p1", 620, 70, 250, 50, "Pod 10.0.1.5:8080 (node 1)", "green")
    d.box("p2", 620, 150, 250, 50, "Pod 10.0.2.7:8080 (node 2)", "green")
    d.box("p3", 620, 230, 250, 50, "Pod 10.0.3.9:8080 (node 3)", "green")
    d.box("bad", 620, 310, 250, 50, "Pod not Ready → not in the list", "red")
    d.edge("client", "dns", "1. resolve name")
    d.edge("client", "kp", "2. connect to\nClusterIP")
    d.edge("es", "kp", "watched", dashed=True)
    d.edge("kp", "p1")
    d.edge("kp", "p2", "3. DNAT to one\nready pod")
    d.edge("kp", "p3")
    d.text("caption", 0, 372, 920, 36,
           "The ClusterIP is not a machine: no process listens on it and you can't ping it. "
           "The client node's kernel rewrites the packet.", size=11)
    return d


def ingress_paths():
    d = Diagram("09-ingress-paths", 960, 470, "Getting internet traffic to pods")
    d.text("ha", 20, 46, 440, 24, "A · AWS Load Balancer Controller (Ingress → ALB)", size=13, bold=True)
    d.box("au", 150, 80, 180, 44, "Users", "gray", shape="ellipse")
    d.box("alb", 130, 160, 220, 54, "ALB (layer 7)\nhost/path rules, TLS via ACM", "orange")
    d.box("ap", 130, 260, 220, 54, "Pod IPs directly\n(target-type: ip)", "green")
    d.edge("au", "alb", "HTTPS")
    d.edge("alb", "ap", "routes to pods")
    d.text("hb", 500, 46, 440, 24, "B · In-cluster controller (NGINX / Envoy / Traefik)", size=13, bold=True)
    d.box("bu", 630, 80, 180, 44, "Users", "gray", shape="ellipse")
    d.box("nlb", 610, 150, 220, 44, "NLB (layer 4)", "orange")
    d.box("ctrl", 610, 220, 220, 54, "Controller pods\nread Ingress / Gateway rules", "purple")
    d.box("bs", 610, 300, 220, 44, "Service → Pods", "green")
    d.edge("bu", "nlb")
    d.edge("nlb", "ctrl")
    d.edge("ctrl", "bs")
    d.group("gw", 20, 370, 920, 80, "Gateway API (the successor to Ingress)", "blue", size=12)
    d.box("gc", 60, 405, 250, 36, "GatewayClass · infra provider", "white", size=11)
    d.box("g", 350, 405, 250, 36, "Gateway · platform team", "white", size=11)
    d.box("hr", 640, 405, 260, 36, "HTTPRoute · app teams", "white", size=11)
    d.edge("g", "gc", "uses")
    d.edge("hr", "g", "attaches to")
    return d


def secrets_flow():
    d = Diagram("10-secrets-flow", 900, 330, "Secrets from AWS Secrets Manager to the pod (no values in Git)")
    d.box("sm", 20, 90, 200, 60, "AWS Secrets Manager\nthe real secret", "orange")
    d.box("eso", 290, 90, 220, 60, "External Secrets Operator\nreads + refreshes", "purple")
    d.box("ks", 570, 85, 160, 70, "K8s Secret\n(base64 in etcd,\nKMS-encrypted)", "blue")
    d.box("pod", 770, 90, 110, 60, "Pod\nfile or env", "green")
    d.box("iam", 290, 210, 220, 54, "IAM role\nvia IRSA / Pod Identity", "yellow")
    d.box("git", 570, 210, 310, 54, "Git holds only the ExternalSecret\n(which secret to fetch), never values",
          "white", size=11)
    d.edge("sm", "eso", "1. fetch")
    d.edge("eso", "ks", "2. create /\nupdate")
    d.edge("ks", "pod", "3. mount")
    d.edge("iam", "eso", "credentials,\nno keys", dashed=True)
    return d


def storage_flow():
    d = Diagram("11-storage-flow", 900, 300, "Dynamic provisioning: from PVC to a real disk")
    d.box("pod", 20, 100, 150, 60, "Pod\nmounts /data", "green")
    d.box("pvc", 220, 100, 190, 60, "PVC data\n10Gi · ReadWriteOnce", "blue")
    d.box("sc", 460, 40, 190, 60, "StorageClass gp3\nprovisioner: ebs.csi.aws.com", "purple", size=11)
    d.box("pv", 460, 160, 190, 60, "PV\nbound to the PVC", "yellow")
    d.box("ebs", 720, 95, 160, 80, "EBS volume\none AZ", "orange", shape="cylinder")
    d.edge("pod", "pvc", "uses")
    d.edge("pvc", "sc", "names the class", dashed=True)
    d.edge("sc", "ebs", "CSI driver\ncreates")
    d.edge("pv", "ebs", "represents")
    d.edge("pvc", "pv", "bound", both=True)
    d.text("caption", 0, 248, 900, 40,
           "WaitForFirstConsumer: the disk is created only after the pod is scheduled, in the pod's AZ.\n"
           "reclaimPolicy (Delete / Retain) decides what happens to the disk when the PVC is deleted.", size=11)
    return d


def autoscaling():
    d = Diagram("12-autoscaling", 940, 320, "Pod and node autoscaling working together")
    d.box("traffic", 20, 110, 140, 56, "Traffic rises", "gray", shape="ellipse")
    d.box("metrics", 200, 40, 190, 56, "metrics-server\nCPU % of requests", "white")
    d.box("hpa", 200, 170, 190, 56, "HPA\nadds pods (2 → 6)", "blue")
    d.box("pending", 440, 170, 190, 56, "New pods Pending\nno room on nodes", "yellow")
    d.box("karp", 670, 170, 250, 56, "Cluster Autoscaler / Karpenter\nadds nodes", "green")
    d.box("done", 670, 40, 250, 56, "Pods scheduled\ncapacity matches load", "green")
    d.edge("traffic", "hpa", "load")
    d.edge("metrics", "hpa", "reads")
    d.edge("hpa", "pending")
    d.edge("pending", "karp")
    d.edge("karp", "done")
    d.text("caption", 0, 260, 940, 40,
           "Scale-down works in reverse: the HPA removes pods, then Karpenter / Cluster Autoscaler removes or "
           "consolidates empty nodes.", size=11)
    return d


def networkpolicy():
    d = Diagram("14-networkpolicy", 900, 400, "NetworkPolicy: default deny, then allow only what's needed")
    d.group("ns", 20, 50, 600, 280, "namespace shop  ·  default-deny-all applied", "gray", dashed=True)
    d.box("fe", 60, 110, 200, 56, "frontend\napp=frontend", "blue")
    d.box("be", 360, 110, 200, 56, "backend :8080\napp=backend", "green")
    d.box("other", 60, 230, 200, 56, "other pod\napp=batch", "gray")
    d.box("dns", 660, 110, 220, 56, "CoreDNS (kube-system)\nport 53 UDP + TCP", "purple")
    d.edge("fe", "be", "allowed: TCP 8080")
    d.edge("other", "be", "blocked ✗", dashed=True)
    d.edge("be", "dns", "allowed: DNS")
    d.text("caption", 0, 345, 900, 44,
           "Policies only add permissions. Without the allow-DNS policy, nothing in the namespace can resolve names.\n"
           "Policies need a network plugin (CNI) that enforces them.", size=11)
    return d


def rbac():
    d = Diagram("15-rbac", 900, 360, "RBAC: who can do what, where")
    d.group("subj", 20, 60, 230, 230, "Subjects", "gray")
    d.box("user", 40, 100, 190, 44, "User: alice", "white")
    d.box("grp", 40, 160, 190, 44, "Group: dev-team", "white")
    d.box("sa", 40, 220, 190, 44, "ServiceAccount: app", "white")
    d.box("rb", 320, 140, 220, 70, "RoleBinding\n(namespace shop)\nconnects subject → role", "orange")
    d.box("role", 610, 70, 270, 70, "Role pod-reader (shop)\nresources: pods, pods/log\nverbs: get, list, watch", "blue")
    d.box("cr", 610, 190, 270, 70,
          "or a ClusterRole\nreused in many namespaces,\nor cluster-wide with a ClusterRoleBinding", "purple", size=11)
    d.edge("user", "rb")
    d.edge("grp", "rb")
    d.edge("sa", "rb")
    d.edge("rb", "role", "grants")
    d.edge("rb", "cr", "can also\nreference", dashed=True)
    d.text("caption", 0, 306, 900, 36,
           "RBAC only allows; there is no deny. Check with: kubectl auth can-i <verb> <resource> --as=<subject>", size=11)
    return d


def troubleshooting():
    d = Diagram("17-troubleshooting-flowchart", 1000, 530, "Pod troubleshooting flowchart")
    d.box("start", 400, 50, 200, 44, "Pod not working", "red", shape="ellipse")
    qs = [("q1", 120, "Status Pending?", "a1", "Scheduling: describe → events\nresources, taints, affinity, PVC"),
          ("q2", 200, "ContainerCreating / ImagePull?", "a2", "describe → events\nimage name / creds, volume, CNI / IPs"),
          ("q3", 280, "CrashLoopBackOff / Error?", "a3", "logs --previous, exit code\n137 = OOM · config · liveness"),
          ("q4", 360, "Running but 0/1 Ready?", "a4", "Readiness probe failing\ndescribe → probe path / port"),
          ("q5", 440, "Ready but no traffic?", "a5", "endpointslices → selector, targetPort\n→ NetworkPolicy → DNS → Ingress")]
    for qid, y, q, aid, a in qs:
        d.box(qid, 370, y, 260, 50, q, "yellow")
        d.box(aid, 690, y - 5, 290, 60, a, "white")
    d.edge("start", "q1")
    for i, (qid, _y, _q, aid, _a) in enumerate(qs):
        d.edge(qid, aid, "yes")
        if i + 1 < len(qs):
            d.edge(qid, qs[i + 1][0], "no")
    d.text("first", 20, 120, 320, 370,
           "Always start with:\n1. kubectl get pods -o wide\n2. kubectl describe pod <pod>\n"
           "3. kubectl logs <pod> --previous\n4. kubectl get events\n    --sort-by=.lastTimestamp", size=11, align="left")
    return d


def operator_pattern():
    d = Diagram("19-operator-pattern", 880, 320, "The operator pattern")
    d.box("you", 20, 110, 170, 56, "You / GitOps\napply a Backup", "white")
    d.box("api", 240, 110, 190, 56, "API server + etcd\nstores the custom resource", "purple")
    d.box("ctrl", 500, 110, 200, 56, "Your operator\n(custom controller)", "green")
    d.box("pods", 740, 60, 130, 56, "Pods / Jobs\nin the cluster", "blue")
    d.box("ext", 740, 170, 130, 56, "External\nAWS, DBs…", "orange")
    d.edge("you", "api", "1. apply")
    d.edge("ctrl", "api", "2. watch\n4. status", both=True)
    d.edge("ctrl", "pods", "3. act")
    d.edge("ctrl", "ext", "3. act")
    d.text("caption", 0, 240, 880, 50,
           "A CRD adds the type; the operator adds the behaviour, using the same reconciliation loop as built-in controllers.\n"
           "Examples: cert-manager, ArgoCD, Karpenter, External Secrets, Prometheus Operator.", size=11)
    return d


def eks():
    d = Diagram("20-eks-architecture", 1000, 600, "EKS: who runs what")
    d.box("users", 420, 44, 180, 36, "Internet users", "gray", shape="ellipse")
    d.group("aws", 20, 95, 300, 200, "AWS-managed control plane", "purple")
    d.box("api", 40, 140, 260, 50, "API servers (multi-AZ)", "white")
    d.box("etcd", 40, 210, 260, 50, "etcd across 3 AZs", "white")
    d.group("vpc", 360, 95, 620, 450, "Your VPC", "gray")
    d.group("pub", 380, 135, 580, 80, "Public subnets", "yellow", size=12)
    d.box("alb", 400, 160, 220, 44, "ALB (from an Ingress)", "orange")
    d.box("nat", 660, 160, 280, 44, "NAT Gateway → internet", "white")
    d.group("priv", 380, 235, 580, 200, "Private subnets (2 AZs)", "blue", size=12)
    d.box("node1", 400, 275, 260, 70, "Node · AZ-a\npods use VPC IPs (VPC CNI)", "green")
    d.box("node2", 680, 275, 260, 70, "Node · AZ-b\npods use VPC IPs (VPC CNI)", "green")
    d.box("agents", 400, 360, 540, 60, "kubelet · VPC CNI (aws-node) · kube-proxy · Pod Identity agent", "white", size=11)
    d.box("sg", 400, 460, 540, 60, "Security Groups: ALB SG → pod/node SG · IMDSv2 hop limit 1 on nodes", "white", size=11)
    d.box("iam", 20, 330, 300, 60, "IAM role per app\n(IRSA / Pod Identity)", "yellow")
    d.box("s3", 20, 430, 140, 70, "S3 / Secrets\nManager", "orange", shape="cylinder")
    d.box("ecr", 180, 430, 140, 70, "ECR\nimages", "orange", shape="cylinder")
    d.edge("users", "alb", "HTTPS")
    d.edge("alb", "node1", "to pod IPs")
    d.edge("api", "node1", "kubelet ↔ API", both=True)
    d.edge("node1", "iam", "temp creds", dashed=True)
    d.edge("iam", "s3", "access")
    d.edge("node1", "ecr", "pull images", dashed=True)
    d.edge("node2", "nat", "egress")
    return d


def gitops():
    d = Diagram("21-gitops-flow", 980, 360, "GitOps delivery with ArgoCD")
    d.box("dev", 20, 90, 140, 56, "Developer\nopens a PR", "white")
    d.box("ci", 200, 90, 200, 56, "CI (GitHub Actions)\ntest → build → scan", "blue")
    d.box("reg", 480, 40, 170, 56, "Registry (ECR)\nimage:4f2a9c1", "orange")
    d.box("repo", 480, 150, 170, 56, "Deploy repo (Git)\ntag → 4f2a9c1", "yellow")
    d.box("argo", 700, 150, 160, 56, "ArgoCD\nin the cluster", "purple")
    d.box("cluster", 880, 140, 90, 76, "Cluster\nsyncs to\nGit state", "green")
    d.edge("dev", "ci", "merge")
    d.edge("ci", "reg", "push image")
    d.edge("ci", "repo", "update tag")
    d.edge("repo", "argo", "detects\nchange")
    d.edge("argo", "cluster", "sync")
    d.edge("cluster", "reg", "pull image", dashed=True)
    d.text("caption", 0, 260, 980, 50,
           "CI never touches the cluster. Rollback = git revert in the deploy repo, and ArgoCD syncs the old version back.\n"
           "selfHeal: true also reverts manual kubectl edits.", size=11)
    return d


ALL = [reconciliation_loop, architecture, node_internals, labels_selectors, apply_flow, pod_anatomy, deployment_rollout,
       service_traffic, ingress_paths, secrets_flow, storage_flow, autoscaling, networkpolicy, rbac,
       troubleshooting, operator_pattern, eks, gitops]

if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in ALL:
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"{'wrote  ' if path else 'skipped'} {diagram.name}.drawio.svg"
              f"{'' if path else '  (exists; use --force to overwrite)'}")
    for w in warnings:
        print("WARN", w)
