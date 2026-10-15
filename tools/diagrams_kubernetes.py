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


def api_request_pipeline():
    d = Diagram("02-api-request-pipeline", 1000, 430, "kube-apiserver: what happens to every request")
    d.box("client", 20, 60, 220, 70, "Any client, HTTPS :6443\nkubectl · controllers ·\nscheduler · kubelets", "white")
    d.box("authn", 265, 60, 220, 70, "1 · Authentication\nwho are you?\ncert · token · OIDC · IAM", "purple")
    d.box("authz", 510, 60, 220, 70, "2 · Authorization\nmay you do this verb here?\nRBAC · Node authorizer", "purple")
    d.box("mutate", 755, 60, 225, 70, "3 · Mutating admission\nmay change the object\ndefaults · inject sidecar", "purple")
    d.box("schema", 755, 190, 225, 70, "4 · Schema validation\nis the object well formed?", "purple")
    d.box("validate", 510, 190, 220, 70, "5 · Validating admission\nmay reject it\nPod Security · Kyverno · OPA", "purple")
    d.box("etcd", 300, 180, 160, 90, "6 · etcd\nobject saved", "yellow", shape="cylinder")
    d.box("watch", 20, 190, 230, 70, "7 · Watchers notified\nADDED · MODIFIED · DELETED\n(no polling)", "green")
    d.edge("client", "authn")
    d.edge("authn", "authz")
    d.edge("authz", "mutate")
    d.edge("mutate", "schema")
    d.edge("schema", "validate")
    d.edge("validate", "etcd")
    d.edge("etcd", "watch")
    d.text("fail", 0, 280, 1000, 24,
           "Fails at 1 → 401 Unauthorized  ·  fails at 2 → 403 Forbidden  ·  fails at 3–5 → request denied, nothing saved",
           size=12, bold=True)
    d.box("f1", 20, 320, 230, 86, "Watch cache\nthousands of watchers are\nserved from memory,\nnot from etcd", "gray", size=11)
    d.box("f2", 265, 320, 230, 86, "resourceVersion\nupdate an old version →\n409 Conflict → re-read\nand retry (no locks)", "gray", size=11)
    d.box("f3", 510, 320, 220, 86, "logs · exec · port-forward\nkubectl → API server →\nkubelet :10250", "gray", size=11)
    d.box("f4", 755, 320, 225, 86, "Stateless\nrun several copies behind\na load balancer; the only\ncomponent that talks to etcd", "gray", size=11)
    return d


def scheduler_steps():
    d = Diagram("02-scheduler-steps", 1000, 340, "kube-scheduler: filter → score → bind (it only decides)")
    steps = [("pod", "New Pod\nnodeName empty", "yellow"), ("queue", "1 · Queue\nby priority", "gray"),
             ("filter", "2 · Filter\ncan it run here?", "blue"), ("score", "3 · Score\nwhich is best?", "blue"),
             ("bind", "4 · Bind\nsets nodeName", "purple"), ("kubelet", "kubelet\nstarts the pod", "orange")]
    for i, (sid, label, color) in enumerate(steps):
        d.box(sid, 20 + i * 164, 56, 140, 56, label, color)
    for (a, *_), (b, *_) in zip(steps, steps[1:]):
        d.edge(a, b)
    d.box("fd", 230, 150, 260, 120, "Filter drops a node if:\n• not enough requested CPU / memory\n"
          "• a taint the pod doesn't tolerate\n• nodeSelector / affinity mismatch\n• host port already taken\n"
          "• volume is in another zone\n• node is cordoned", "white", size=11, valign="top", align="left")
    d.box("sd", 510, 150, 220, 120, "Score ranks nodes 0–100:\n• least allocated\n• balanced CPU / memory\n"
          "• image already on the node\n• pod (anti-)affinity\n• topology spread", "white", size=11,
          valign="top", align="left")
    d.box("fail", 750, 150, 230, 120, "No node passes Filter?\npod stays Pending\nevent FailedScheduling:\n"
          "\"0/3 nodes are available:\n3 Insufficient cpu\"\nhigher priority → may preempt", "red", size=11)
    d.edge("filter", "fd", dashed=True)
    d.edge("score", "sd", dashed=True)
    d.text("caption", 0, 282, 1000, 50,
           "Filter uses requests, not real usage. Scheduler down → new pods Pending with NO FailedScheduling events.\n"
           "HA: several copies, one active leader (Lease). Every step is a plugin; a 2nd scheduler via spec.schedulerName.",
           size=11)
    return d


def etcd_quorum():
    d = Diagram("02-etcd-quorum", 1000, 380, "etcd: one leader, a majority must agree (Raft)")
    d.box("api", 20, 65, 170, 60, "kube-apiserver\nthe only etcd client", "purple")
    d.box("leader", 300, 50, 170, 90, "etcd leader\nall writes go here", "yellow", shape="cylinder")
    d.box("f1", 220, 210, 160, 90, "etcd follower", "yellow", shape="cylinder")
    d.box("f2", 400, 210, 160, 90, "etcd follower", "yellow", shape="cylinder")
    d.edge("api", "leader", "read / write\n:2379")
    d.edge("leader", "f1", "Raft :2380", both=True)
    d.edge("leader", "f2", "Raft :2380", both=True)
    d.box("q", 620, 50, 360, 100, "Quorum = majority of members\n3 members → survives 1 failure\n"
          "4 members → survives 1 (no gain)\n5 members → survives 2\n→ always run an odd number", "blue",
          valign="top", align="left")
    d.box("rem", 620, 170, 360, 120, "Remember\n• slow disk → leader elections → flaky API (use SSD)\n"
          "• quota 2 GiB default (up to 8 GiB); full → read-only\n  \"mvcc: database space exceeded\"\n"
          "• backup: etcdctl snapshot save\n• restore: etcdutl snapshot restore → new data dir\n"
          "• Secrets live here → encryption at rest", "white", size=11, valign="top", align="left")
    d.text("caption", 0, 330, 1000, 40,
           "A write is committed only when a majority has it on disk → strong consistency.\n"
           "Every change gets a revision number → that is Kubernetes' resourceVersion, and watches are built on it.",
           size=11)
    return d


def controller_internals():
    d = Diagram("02-controller-internals", 1000, 400, "Inside every controller: informer → work queue → worker")
    d.box("api", 20, 150, 170, 60, "kube-apiserver", "purple")
    d.box("inf", 260, 70, 190, 60, "Informer\nlist once, then watch", "blue")
    d.box("cache", 260, 200, 190, 60, "Local cache\nreads cost no API calls", "yellow")
    d.box("q", 520, 70, 190, 60, "Work queue\nkeys of changed objects", "gray")
    d.box("w", 780, 70, 200, 60, "Worker\ncompare desired vs actual", "green")
    d.edge("api", "inf", "watch")
    d.edge("inf", "cache", "update")
    d.edge("inf", "q", "key changed")
    d.edge("q", "w", "pop key")
    d.edge("w", "q", "error → retry with backoff", dashed=True, points=[(880, 165), (615, 165)])
    d.edge("w", "cache", "read state", dashed=True, points=[(880, 230)])
    d.edge("w", "api", "write the fix (create / update / delete objects)", points=[(880, 300), (105, 300)])
    d.text("caption", 0, 320, 1000, 70,
           "Controllers never call each other: the Deployment controller just writes a ReplicaSet;\n"
           "the ReplicaSet controller sees it on its own watch and creates Pods.\n"
           "One active copy at a time via leader election (a Lease). Every operator you write uses this same pattern.",
           size=11)
    return d


def ha_control_plane():
    d = Diagram("02-ha-control-plane", 1000, 400, "HA control plane: 3 nodes behind a load balancer")
    d.box("lb", 390, 46, 220, 44, "Load balancer :6443", "orange")
    roles = [("leader", "leader"), ("standby", "standby"), ("standby", "standby")]
    for i, (sched, cm) in enumerate(roles):
        x = 20 + i * 330
        d.group(f"cp{i}", x, 120, 300, 200, f"Control plane node {i + 1}", "gray")
        d.box(f"api{i}", x + 15, 155, 270, 34, "kube-apiserver · active", "purple", size=11)
        d.box(f"s{i}", x + 15, 197, 270, 34, f"kube-scheduler · {sched}", "green" if sched == "leader" else "white",
              size=11)
        d.box(f"c{i}", x + 15, 239, 270, 34, f"controller-manager · {cm}", "green" if cm == "leader" else "white",
              size=11)
        d.box(f"e{i}", x + 15, 281, 270, 30, "etcd member" + (" (Raft leader)" if i == 1 else ""), "yellow", size=11)
        d.edge("lb", f"api{i}")
    d.text("caption", 0, 335, 1000, 56,
           "API servers are active-active. Scheduler and controller-manager are active-passive: one leader, chosen by a Lease.\n"
           "etcd needs a majority: 3 nodes survive 1 failure. On EKS AWS runs all of this across 3 AZs; you never see it.",
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


def core_ideas():
    d = Diagram("01-core-ideas", 1000, 400, "Kubernetes in one picture: the 5 core ideas")
    d.box("you", 20, 70, 180, 70, "You\nwrite YAML: replicas: 3\n(1) declarative", "white")
    d.box("api", 290, 70, 230, 70, "API server + etcd\nstores every object\n(3) everything is an API object", "purple")
    d.box("ctrl", 600, 70, 230, 70, "Controllers\nobserve → compare → act\n(2) reconciliation loop", "green")
    d.box("svc", 270, 230, 230, 70, "Service web\nselector app=web, stable IP\n(5) labels connect things", "orange")
    d.group("pods", 540, 180, 450, 140, "Pods with label app=web  ·  (4) cattle, not pets", "gray", size=12)
    d.box("p1", 555, 225, 100, 60, "web-a\n10.0.1.5", "green", size=11)
    d.box("p2", 665, 225, 100, 60, "web-b\n10.0.2.7", "green", size=11)
    d.box("p3", 775, 225, 100, 60, "web-c ✗\ncrashed", "red", size=11)
    d.box("p4", 885, 225, 95, 60, "web-d (new)\n10.0.3.9", "green", size=11)
    d.edge("you", "api", "kubectl apply")
    d.edge("api", "ctrl", "watch")
    d.edge("ctrl", "pods", "create / replace")
    d.edge("svc", "pods", "app=web")
    d.text("caption", 0, 335, 1000, 50,
           "A pod crashes → the controller sees 2 ≠ 3 → it creates a new pod with a new name and IP.\n"
           "The Service still finds it by label. Nobody ran a command: that is self-healing.", size=12)
    return d


def ownership_finalizers():
    d = Diagram("03-ownership-finalizers", 1000, 380, "Owners, garbage collection and finalizers")
    d.box("dep", 20, 60, 200, 50, "Deployment web", "blue")
    d.box("rs", 20, 150, 200, 50, "ReplicaSet web-7d9f", "blue")
    d.box("pods", 20, 240, 200, 50, "Pods web-7d9f-xxxxx", "green")
    d.edge("dep", "rs", "owns")
    d.edge("rs", "pods", "owns")
    d.text("gc", 235, 60, 260, 240,
           "Child → owner link:\nmetadata.ownerReferences\n\nDelete the Deployment:\n• background (default):\n  children deleted after it\n"
           "• foreground: children first\n• --cascade=orphan:\n  children are kept", size=11, align="left")
    d.box("del", 530, 60, 200, 50, "kubectl delete pvc data", "white")
    d.box("term", 530, 150, 190, 60, "Terminating\ndeletionTimestamp set", "yellow")
    d.box("ctrl", 800, 150, 180, 60, "Controller cleans up,\nremoves its finalizer", "green")
    d.box("gone", 800, 250, 180, 50, "Object deleted", "gray")
    d.box("stuck", 530, 250, 190, 60, "Controller gone?\nstuck Terminating", "red")
    d.edge("del", "term")
    d.edge("term", "ctrl", "finalizer set")
    d.edge("ctrl", "gone", "finalizers: []")
    d.edge("term", "stuck", "nobody removes it", dashed=True)
    d.text("caption", 0, 325, 1000, 44,
           "Finalizer examples: kubernetes.io/pvc-protection (PVC still mounted) · LB controller deletes the cloud LB first.\n"
           "Find them: kubectl get <kind> <name> -o yaml | grep -A3 finalizers", size=11)
    return d


def pod_lifecycle():
    d = Diagram("05-pod-lifecycle", 1000, 380, "Pod phase (the summary) vs container state (the detail)")
    d.box("pending", 20, 60, 190, 60, "Pending\nnot scheduled / pulling", "yellow")
    d.box("running", 270, 60, 190, 60, "Running\n≥ 1 container running", "green")
    d.box("succ", 520, 42, 190, 44, "Succeeded · all exited 0", "blue", size=11)
    d.box("failed", 520, 96, 190, 44, "Failed · one exited non-zero", "red", size=11)
    d.box("unknown", 770, 60, 210, 60, "Unknown\nnode not reporting", "gray")
    d.edge("pending", "running")
    d.edge("running", "succ")
    d.edge("running", "failed")
    d.group("cs", 20, 170, 960, 150, "Container state", "white", size=12)
    d.box("waiting", 40, 205, 300, 64, "Waiting + reason\nContainerCreating · ImagePullBackOff\nCrashLoopBackOff · ConfigError", "yellow",
          size=11)
    d.box("crun", 380, 205, 170, 64, "Running", "green")
    d.box("cterm", 590, 205, 370, 64, "Terminated + reason + exit code\nCompleted 0 · Error 1 · OOMKilled 137", "red", size=11)
    d.edge("waiting", "crun")
    d.edge("crun", "cterm")
    d.edge("cterm", "waiting", "restartPolicy restarts it → back to Waiting", dashed=True,
           points=[(775, 298), (190, 298)])
    d.text("caption", 0, 330, 1000, 40,
           "CrashLoopBackOff is a Waiting reason, not a phase: each restart waits longer, 10 s → 20 s → 40 s … up to 5 min.",
           size=12)
    return d


def graceful_shutdown():
    d = Diagram("05-graceful-shutdown", 1000, 360, "Deleting a pod: two things start at the same moment (the race)")
    d.box("del", 20, 135, 210, 70, "Pod deleted\nscale-down · rollout · drain", "white")
    d.box("ep", 260, 50, 220, 60, "Removed from\nService endpoints", "orange")
    d.box("kp", 530, 50, 220, 60, "kube-proxy on every node\nupdates rules (takes a moment)", "orange", size=11)
    d.box("race", 790, 50, 190, 60, "Race: requests still\narrive while app stops", "red")
    d.box("pre", 260, 230, 220, 60, "1 · preStop hook\nsleep 5–10 s", "blue")
    d.box("sig", 530, 230, 220, 60, "2 · SIGTERM to PID 1\nfinish in-flight requests", "yellow")
    d.box("kill", 790, 230, 190, 60, "3 · SIGKILL\nafter grace period (30 s)", "red", size=11)
    d.edge("del", "ep")
    d.edge("del", "pre")
    d.edge("ep", "kp")
    d.edge("kp", "race", dashed=True)
    d.edge("pre", "sig")
    d.edge("sig", "kill")
    d.text("caption", 0, 305, 1000, 44,
           "Fix the race: a short preStop sleep (routing updates before SIGTERM) + an app that handles SIGTERM\n"
           "+ readiness probes + maxUnavailable: 0. Kubernetes waits 30 s by default; docker stop waits 10 s.", size=11)
    return d


def probes():
    d = Diagram("06-probes", 1000, 360, "Probes: the kubelet asks three questions")
    d.box("start", 20, 120, 240, 76, "Startup probe\nhas it finished starting?\nthe others wait until it passes", "purple")
    d.box("live", 320, 50, 230, 60, "Liveness probe\nis the process stuck?", "orange")
    d.box("ready", 320, 210, 230, 60, "Readiness probe\ncan it take traffic now?", "blue")
    d.box("restart", 630, 50, 350, 60, "Fails → container is RESTARTED\ncheck only the container, never the DB", "red")
    d.box("unready", 630, 210, 350, 60, "Fails → removed from Service endpoints\nNOT restarted; back when it passes", "yellow")
    d.edge("start", "live", "passes")
    d.edge("start", "ready", "passes")
    d.edge("live", "restart", "fails 3×")
    d.edge("ready", "unready", "fails 3×")
    d.text("caption", 0, 290, 1000, 60,
           "Types: httpGet (200–399) · tcpSocket · exec (exit 0) · grpc.   Defaults: period 10 s · timeout 1 s · failureThreshold 3.\n"
           "Startup budget = failureThreshold × periodSeconds (30 × 10 s = 5 min). Startup keeps failing → restarted.\n"
           "Liveness that checks the database → every pod restarts at once during a DB slowdown.", size=11)
    return d


def workload_types():
    d = Diagram("07-workload-types", 1000, 410, "Which workload controller?")
    cols = [
        ("dep", "Deployment\nstateless: APIs, web", "blue", ["web-7f9c-x2k", "web-7f9c-p8d", "web-7f9c-m4q"],
         "random names, any node;\nrolling update + rollback"),
        ("sts", "StatefulSet\ndatabases, Kafka", "purple", ["db-0 + PVC data-db-0", "db-1 + PVC data-db-1", "db-2 + PVC data-db-2"],
         "stable name + own disk;\nordered 0 → 1 → 2; headless Svc"),
        ("ds", "DaemonSet\nnode agents", "orange", ["node-1: log agent", "node-2: log agent", "node-3: log agent"],
         "one pod per node;\nnew node → gets one"),
        ("job", "Job / CronJob\nrun to completion", "green", ["Job: pod → Completed ✓", "retries: backoffLimit 6", "CronJob: Job at 0 2 * * *"],
         "migrations, batch, backups;\nconcurrencyPolicy: Forbid"),
    ]
    for i, (cid, label, color, items, note) in enumerate(cols):
        x = 20 + i * 245
        d.group(cid, x, 50, 225, 290, label, color, size=12)
        for j, item in enumerate(items):
            d.box(f"{cid}{j}", x + 12, 105 + j * 56, 201, 44, item, "white", size=11)
        d.text(f"{cid}n", x, 275, 225, 56, note, size=11)
    d.text("caption", 0, 355, 1000, 44,
           "ReplicaSet: never create it yourself; the Deployment makes one per version.\n"
           "PodDisruptionBudget (minAvailable / maxUnavailable) limits how many pods a drain may evict at once.", size=11)
    return d


def service_types():
    d = Diagram("08-service-types", 1000, 470, "Service types: who can reach the pods, and how")
    rows = [
        ("ClusterIP (default)", "blue", "Pod in the cluster", "ClusterIP 10.96.12.34:80\nvirtual IP, kube-proxy DNAT", "ready pods :8080"),
        ("NodePort", "yellow", "Outside client", "any-node-IP:30000–32767\nopened on every node", "ready pods :8080"),
        ("LoadBalancer", "orange", "Internet / VPC", "Cloud LB (NLB on EKS)\n→ NodePorts or pod IPs", "ready pods :8080"),
        ("Headless", "green", "Pod in the cluster", "clusterIP: None\nDNS returns every pod IP", "db-0, db-1 directly"),
        ("ExternalName", "gray", "Pod in the cluster", "DNS CNAME → db.example.com\nno proxying at all", "service outside"),
    ]
    for i, (name, color, caller, middle, target) in enumerate(rows):
        y = 55 + i * 70
        d.box(f"t{i}", 20, y, 160, 54, name, color, bold=True)
        d.box(f"c{i}", 210, y, 170, 54, caller, "white")
        d.box(f"m{i}", 430, y, 320, 54, middle, color, bold_first=False)
        d.box(f"p{i}", 800, y, 180, 54, target, "white")
        d.edge(f"c{i}", f"m{i}")
        d.edge(f"m{i}", f"p{i}")
    d.text("caption", 0, 410, 1000, 50,
           "Ports: port = the Service's port · targetPort = the container's port · nodePort = the port on each node.\n"
           "externalTrafficPolicy: Local keeps the client's source IP (only nodes with a local pod get traffic).", size=11)
    return d


def dns_lookup():
    d = Diagram("08-dns-lookup", 1000, 330, "DNS inside a pod: search domains and ndots:5")
    d.box("conf", 20, 55, 270, 120, "/etc/resolv.conf in every pod\nnameserver 10.96.0.10 (CoreDNS)\nsearch shop.svc.cluster.local\n"
          "    svc.cluster.local cluster.local\noptions ndots:5", "white", size=11, valign="top", align="left")
    d.box("short", 340, 50, 330, 56, "web → web.shop.svc.cluster.local\nfound on the 1st try", "green", bold_first=False)
    d.box("ext", 340, 125, 330, 100, "api.stripe.com (2 dots < 5, so search first)\n✗ api.stripe.com.shop.svc.cluster.local\n"
          "✗ api.stripe.com.svc.cluster.local\n✗ api.stripe.com.cluster.local\n✓ api.stripe.com", "yellow", size=11,
          align="left")
    d.box("dns", 730, 90, 250, 70, "CoreDNS\ncluster names → ClusterIPs\neverything else → upstream", "purple")
    d.edge("conf", "short")
    d.edge("conf", "ext")
    d.edge("short", "dns")
    d.edge("ext", "dns")
    d.text("caption", 0, 245, 1000, 70,
           "Names: web (same namespace) · web.shop (any namespace) · db-0.db.shop.svc.cluster.local (one pod, headless).\n"
           "Slow external lookups? Use a trailing dot (api.stripe.com.), lower ndots in dnsConfig, or NodeLocal DNSCache.",
           size=11)
    return d


def ingress_errors():
    d = Diagram("09-ingress-errors", 1000, 340, "Where Ingress errors come from")
    d.box("client", 20, 70, 140, 50, "Client", "gray", shape="ellipse")
    d.box("lb", 210, 60, 210, 70, "ALB / Ingress controller\nmatches host + path", "orange")
    d.box("svc", 470, 60, 210, 70, "Service\nEndpointSlice: ready pods", "blue")
    d.box("pod", 730, 60, 250, 70, "Pod :targetPort\nyour app", "green")
    d.edge("client", "lb")
    d.edge("lb", "svc")
    d.edge("svc", "pod")
    d.box("e404", 210, 180, 210, 80, "404\nno rule matched: host,\npathType, ingressClassName", "red", size=11)
    d.box("e503", 470, 180, 210, 80, "503\nno ready endpoints:\nselector or readiness", "red", size=11)
    d.box("e502", 730, 180, 120, 80, "502\nconn. reset\nwrong targetPort\nkeep-alive < idle", "red", size=11)
    d.box("e504", 860, 180, 120, 80, "504\napp too slow,\nLB timed out", "red", size=11)
    d.edge("lb", "e404", dashed=True)
    d.edge("svc", "e503", dashed=True)
    d.edge("pod", "e502", dashed=True)
    d.edge("pod", "e504", dashed=True)
    d.text("caption", 0, 280, 1000, 50,
           "An Ingress is only rules; a controller implements them. The Ingress API is frozen and ingress-nginx was retired\n"
           "(maintenance ended March 2026). Gateway API is the successor.", size=11)
    return d


def config_to_pod():
    d = Diagram("10-config-to-pod", 1000, 330, "Two ways config reaches a container")
    d.box("cm", 20, 60, 200, 60, "ConfigMap\nplain settings, ≤ 1 MiB", "yellow")
    d.box("sec", 20, 180, 200, 60, "Secret\nbase64, NOT encrypted", "orange")
    d.box("env", 330, 60, 270, 60, "Environment variables\nenv / envFrom", "blue")
    d.box("file", 330, 180, 270, 60, "Mounted files (a volume)\n/etc/app/<key>", "green")
    d.box("envres", 680, 60, 300, 60, "Change → seen only after a pod restart\nleaks more easily (crash dumps)", "red",
          bold_first=False, size=11)
    d.box("fileres", 680, 180, 300, 60, "Change → file updates after a short delay\napp must re-read it · never with subPath",
          "green", bold_first=False, size=11)
    for a in ("cm", "sec"):
        for b in ("env", "file"):
            d.edge(a, b)
    d.edge("env", "envres")
    d.edge("file", "fileres")
    d.text("caption", 0, 260, 1000, 60,
           "Roll pods on a config change: kubectl rollout restart · Helm checksum/config annotation · Kustomize configMapGenerator.\n"
           "Protect Secrets: KMS encryption at rest · RBAC (list = read the values) · External Secrets from Secrets Manager.",
           size=11)
    return d


def requests_limits():
    d = Diagram("12-requests-limits", 1000, 360, "Requests are for the scheduler, limits are for the kernel")
    d.group("node", 20, 50, 440, 220, "Node with 4 CPU", "gray")
    d.text("l1", 30, 85, 420, 20, "Requested (what the scheduler counts)", size=11, align="left")
    d.box("ra", 30, 108, 150, 44, "pod A · 1.5", "blue", size=11)
    d.box("rb", 180, 108, 200, 44, "pod B · 2.0", "blue", size=11)
    d.box("rf", 380, 108, 70, 44, "free 0.5", "white", size=11)
    d.text("l2", 30, 165, 420, 20, "Actually used (what kubectl top shows)", size=11, align="left")
    d.box("use", 30, 190, 420, 60, "pod A uses 0.3 · pod B uses 0.4\nthe node looks idle", "white", size=11, bold_first=False)
    d.box("new", 20, 285, 440, 60, "New pod requests 1 CPU → Pending\n\"Insufficient cpu\" (only 0.5 unrequested)", "red")
    d.box("cpu", 510, 50, 470, 50, "CPU over its limit → THROTTLED (slowed), never killed", "yellow")
    d.box("mem", 510, 115, 470, 50, "Memory over its limit → OOMKilled (exit code 137)", "red")
    d.box("qos", 510, 180, 470, 90, "QoS class = eviction order when the node runs low\n1st  BestEffort: no requests or limits\n"
          "2nd  Burstable: some requests or limits set\nlast  Guaranteed: requests = limits for CPU and memory",
          "blue", valign="top", align="left")
    return d


def taints_affinity():
    d = Diagram("13-taints-affinity", 1000, 450, "Taints repel, affinity attracts: dedicated nodes need both")
    d.box("ml", 20, 60, 300, 76, "ML pod\ntoleration: dedicated=gpu\nnode affinity: gpu=true", "green")
    d.box("web", 20, 190, 300, 60, "Web pod\nno toleration", "white")
    d.box("tol", 20, 300, 300, 60, "Pod with a toleration only\nno affinity", "yellow")
    d.box("gpu", 640, 60, 340, 76, "GPU node\ntaint: dedicated=gpu:NoSchedule\nlabel: gpu=true", "purple")
    d.box("normal", 640, 250, 340, 60, "Normal node\nno taint", "gray")
    d.edge("ml", "gpu", "lands here")
    d.edge("web", "gpu", "blocked by the taint", dashed=True)
    d.edge("web", "normal")
    d.edge("tol", "normal", "may still land here:\na toleration allows, it doesn't attract", dashed=True)
    d.text("caption", 0, 380, 1000, 60,
           "Taint effects: NoSchedule · PreferNoSchedule · NoExecute (also evicts running pods).\n"
           "Not-ready nodes get a NoExecute taint; pods tolerate it for 300 s, then they are evicted.\n"
           "Spread replicas across AZs: topologySpreadConstraints on topology.kubernetes.io/zone, maxSkew 1.", size=11)
    return d


def pod_to_pod():
    d = Diagram("14-pod-to-pod", 1000, 380, "Pod A on node 1 → pod B on node 2")
    for side, x, pod, wrap in (("1", 20, "Pod A · eth0 10.244.1.5", "Overlay: wrap in VXLAN\nnode IPs outside"),
                               ("2", 680, "Pod B · eth0 10.244.2.9", "Overlay: unwrap VXLAN")):
        d.group(f"n{side}", x, 50, 300, 240, f"Node {side}", "gray")
        d.box(f"pod{side}", x + 25, 90, 250, 44, pod, "green")
        d.box(f"veth{side}", x + 25, 155, 250, 40, "veth pair → node network stack", "white", size=11)
        d.box(f"wrap{side}", x + 25, 215, 250, 56, wrap, "orange", size=11)
    d.box("net", 380, 200, 240, 86, "Node network / VPC\nVPC CNI: no wrapping,\nthe VPC routes pod IPs", "blue", size=11)
    d.edge("pod1", "veth1")
    d.edge("veth1", "wrap1")
    d.edge("wrap1", "net")
    d.edge("net", "wrap2")
    d.edge("wrap2", "veth2")
    d.edge("veth2", "pod2")
    d.text("caption", 0, 305, 1000, 64,
           "4 rules: every pod has its own IP · pod → pod without NAT · node agents reach local pods · a pod sees the IP others use.\n"
           "A CNI plugin makes them true. Pod → internet: the node SNATs to its own IP → NAT Gateway.\n"
           "Pod → Service: kube-proxy's DNAT rules on the sending node.", size=11)
    return d


def security_layers():
    d = Diagram("15-security-layers", 1000, 450, "Securing a cluster: 7 layers, say them in this order")
    layers = [
        ("1 · API access", "authentication → RBAC → admission (Pod Security, Kyverno, ValidatingAdmissionPolicy)", "purple"),
        ("2 · Workload identity", "ServiceAccounts, short-lived projected tokens, IRSA / Pod Identity for AWS", "blue"),
        ("3 · Pod hardening", "Pod Security Standards (restricted), securityContext: non-root, drop ALL, read-only FS", "green"),
        ("4 · Network", "default-deny NetworkPolicy, private API endpoint, mTLS with a service mesh", "yellow"),
        ("5 · Supply chain", "scan (Trivy), sign (cosign), verify signatures and trusted registries at admission", "orange"),
        ("6 · Secrets", "KMS encryption at rest, external secret manager, tight RBAC on secrets", "red"),
        ("7 · Detection", "audit logs, Falco / GuardDuty runtime alerts, kube-bench (CIS benchmark)", "gray"),
    ]
    for i, (name, detail, color) in enumerate(layers):
        y = 50 + i * 50
        d.box(f"n{i}", 20, y, 220, 42, name, color, bold=True)
        d.box(f"d{i}", 250, y, 730, 42, detail, color, align="left")
    d.text("caption", 0, 405, 1000, 36,
           "Dangerous RBAC: get/list secrets · create pods · pods/exec · escalate / bind / impersonate · nodes/proxy · wildcards *",
           size=11)
    return d


def k8s_observability():
    d = Diagram("16-k8s-observability", 1000, 400, "Where Kubernetes logs and metrics come from")
    d.group("node", 20, 50, 420, 270, "Node", "gray")
    d.box("app", 40, 90, 170, 56, "App container\nstdout / stderr", "green")
    d.box("files", 40, 200, 160, 60, "/var/log/pods/…\nrotated 10 MiB × 5", "yellow", size=11)
    d.box("kubelet", 260, 90, 165, 56, "kubelet\n+ cAdvisor", "orange")
    d.box("ship", 260, 200, 165, 60, "Fluent Bit / Alloy\n(DaemonSet)", "purple")
    d.edge("app", "files", "runtime writes")
    d.edge("files", "ship", "tails")
    d.edge("files", "kubelet", "reads", dashed=True)
    d.box("kl", 480, 70, 220, 50, "kubectl logs\n--previous after a crash", "white", size=11)
    d.box("ms", 480, 150, 220, 50, "metrics-server\nnow only: top, HPA", "white", size=11)
    d.box("prom", 760, 100, 220, 56, "Prometheus + Grafana\nhistory, alerts", "blue")
    d.box("ksm", 760, 185, 220, 50, "kube-state-metrics\nobject state, restarts", "gray", size=11)
    d.box("loki", 760, 265, 220, 56, "Loki / CloudWatch\nlogs survive the pod", "blue")
    d.edge("kubelet", "kl")
    d.edge("kubelet", "ms")
    d.edge("ksm", "prom")
    d.edge("ship", "loki")
    d.text("caption", 0, 335, 1000, 56,
           "Pod deleted or node gone → its log files are gone too, so ship them. Events last about 1 hour: export them for history.\n"
           "Prometheus scrapes the kubelet (cAdvisor), kube-state-metrics and node_exporter. Traces: OpenTelemetry → Tempo / X-Ray.",
           size=11)
    return d


def upgrade_order():
    d = Diagram("18-upgrade-order", 1000, 300, "Upgrading a cluster: one minor version at a time")
    steps = [("Prepare", "release notes\ndeprecated APIs (pluto,\nkubent, upgrade insights)\nbackup · check PDBs", "white"),
             ("Control plane", "API servers, then\ncontroller-manager\n+ scheduler", "purple"),
             ("Add-ons", "CoreDNS · kube-proxy\nCNI · CSI drivers\n(EKS managed add-ons)", "blue"),
             ("Nodes, rolling", "cordon → drain →\nupgrade / replace →\nuncordon", "orange"),
             ("Verify", "nodes Ready\nworkloads healthy\nno deprecated-API errors", "green")]
    for i, (name, body, color) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 195, 55, 180, 110, f"{i + 1} · {name}\n{body}", color, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.box("skew", 20, 195, 470, 82, "Version skew\n• kubelet: up to 3 minors older than the API server, never newer\n"
          "• scheduler / controller-manager: at most 1 older\n• kubectl: within ±1", "blue", size=11, valign="top",
          align="left")
    d.box("drain", 510, 195, 470, 82, "Drain\n• cordon = no new pods · drain = also evict (respects PDBs)\n"
          "• hangs? a PDB can't be met (minAvailable 1 with 1 replica)\n"
          "• EKS: managed node groups drain for you; Karpenter replaces drifted nodes", "yellow", size=11,
          valign="top", align="left")
    return d


def pod_identity():
    d = Diagram("20-pod-identity", 1000, 360, "A pod reaches AWS with no access keys (IRSA / Pod Identity)")
    d.box("pod", 20, 80, 160, 60, "Pod\nAWS SDK", "green")
    d.box("sa", 250, 80, 190, 60, "ServiceAccount\nshop/app", "blue")
    d.box("role", 530, 80, 200, 60, "IAM role\none per app, least privilege", "yellow", size=11)
    d.box("s3", 800, 65, 180, 90, "S3 / Secrets\nManager", "orange", shape="cylinder")
    d.box("sts", 260, 200, 220, 60, "STS / Pod Identity agent\ntemporary credentials", "purple", size=11)
    d.box("imds", 560, 200, 420, 60, "Node's own IAM role (instance metadata)\nblocked for pods: IMDSv2 with hop limit 1",
          "red")
    d.edge("pod", "sa", "runs as")
    d.edge("sa", "role", "mapped to")
    d.edge("role", "sts", "assume role", dashed=True)
    d.edge("sts", "pod", "temp creds")
    d.edge("pod", "s3", "call AWS with temp creds", points=[(100, 50), (890, 50)])
    d.text("caption", 0, 280, 1000, 64,
           "IRSA: IAM OIDC provider + ServiceAccount annotation eks.amazonaws.com/role-arn → AssumeRoleWithWebIdentity.\n"
           "Pod Identity (newer): agent add-on + association (cluster, namespace, ServiceAccount → role);\n"
           "the role trusts pods.eks.amazonaws.com, so one role works for many clusters.", size=11)
    return d


def helm_vs_kustomize():
    d = Diagram("21-helm-vs-kustomize", 1000, 320, "Helm vs Kustomize: two ways to get final YAML")
    d.group("h", 20, 50, 470, 200, "Helm: templates + values", "blue")
    d.box("tpl", 40, 95, 200, 56, "templates/\n{{ .Values.image.tag }}", "white", size=11)
    d.box("val", 40, 170, 200, 56, "values-prod.yaml\nimage.tag: 4f2a9c1", "yellow", size=11)
    d.box("o1", 290, 130, 180, 60, "Final YAML\n+ release revision", "green")
    d.edge("tpl", "o1")
    d.edge("val", "o1")
    d.group("k", 510, 50, 470, 200, "Kustomize: base + patches", "purple")
    d.box("base", 530, 95, 200, 56, "base/\nplain YAML", "white", size=11)
    d.box("ov", 530, 170, 200, 56, "overlays/prod\nreplicas, image tag", "yellow", size=11)
    d.box("o2", 780, 130, 180, 60, "Final YAML\nkubectl apply -k", "green")
    d.edge("base", "o2")
    d.edge("ov", "o2")
    d.text("caption", 0, 260, 1000, 50,
           "Helm: packages, repositories, helm rollback; good for third-party software.\n"
           "Kustomize: no templating, built into kubectl, rollback = git revert; good for your own apps. Often used together.",
           size=11)
    return d


ALL = [reconciliation_loop, architecture, node_internals, api_request_pipeline, scheduler_steps, etcd_quorum,
       controller_internals, ha_control_plane, labels_selectors, apply_flow, pod_anatomy, deployment_rollout,
       service_traffic, ingress_paths, secrets_flow, storage_flow, autoscaling, networkpolicy, rbac,
       troubleshooting, operator_pattern, eks, gitops, core_ideas, ownership_finalizers, pod_lifecycle,
       graceful_shutdown, probes, workload_types, service_types, dns_lookup, ingress_errors, config_to_pod,
       requests_limits, taints_affinity, pod_to_pod, security_layers, k8s_observability, upgrade_order, pod_identity,
       helm_vs_kustomize]

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
