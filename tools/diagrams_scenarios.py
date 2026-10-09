#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/hemant-scenario-deep-dives.md.

Run once:  python3 tools/diagrams_scenarios.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def helm_three_way():
    d = Diagram("s1-helm-three-way-merge", 1000, 560,
                "helm upgrade (Helm 3, client-side): one patch built from three inputs")
    d.box("old", 30, 70, 270, 110,
          "1. OLD manifest\nwhat Helm applied last time\n(stored in the release Secret\nsh.helm.release.v1.web.v3)\nreplicas: 3", "gray")
    d.box("live", 365, 70, 270, 110,
          "2. LIVE object\nwhat is in the cluster now\n(someone ran kubectl edit)\nreplicas: 5\n+ annotation team=x", "red")
    d.box("new", 700, 70, 270, 110,
          "3. NEW manifest\nhelm template output\nof the chart + values\nreplicas: 3", "blue")
    d.box("patch", 300, 240, 400, 92,
          "3-way strategic merge patch\n• field in NEW differs from LIVE → set it to NEW\n• field in OLD but removed from NEW → delete it\n• field only in LIVE → leave it alone",
          "yellow", align="left")
    d.edge("old", "patch", "what did\nHelm own?")
    d.edge("live", "patch", "what is\nthere now?")
    d.edge("new", "patch", "what do\nwe want?")
    d.box("r1", 30, 400, 300, 92,
          "replicas 5 → 3\nreverted: the chart sets this field,\neven if the chart did not change", "green")
    d.box("r2", 350, 400, 300, 92,
          "annotation team=x\nkept: the chart never set it\n(same for injected sidecars)", "green")
    d.box("r3", 670, 400, 300, 92,
          "⚠️ custom resources (CRDs)\nplain 2-way JSON merge (OLD vs NEW)\nlive edits survive if values unchanged", "orange")
    d.edge("patch", "r1")
    d.edge("patch", "r2")
    d.edge("patch", "r3")
    d.text("caption", 0, 510, 1000, 40,
           "Helm only compares when you run it: it never watches the cluster. Helm 4 new releases use server-side apply\n"
           "instead, so a field changed by kubectl edit gives a conflict error unless you pass --force-conflicts.",
           size=12, italic=True)
    return d


def overlapping_cidr():
    d = Diagram("s2-overlapping-cidr-private-nat", 1200, 640,
                "Two clusters, both VPCs are 10.0.0.0/16: private NAT gateway + Transit Gateway")
    # VPC A
    d.group("vpcA", 20, 50, 470, 470, "VPC A (cluster A)\nprimary 10.0.0.0/16 (overlaps with B)\nsecondary 10.100.0.0/24 (unique, routable)", "blue", size=12)
    d.group("aPriv", 40, 115, 430, 170, "Node and pod subnets (10.0.x.x, NOT routable outside)", "white", size=11)
    d.box("podA", 70, 155, 170, 60, "Pod in cluster A\n10.0.1.25", "blue")
    d.box("rtA", 260, 150, 190, 120,
          "Route table\n10.0.0.0/16 → local\n10.100.1.0/24 → private NAT", "white", align="left", size=11)
    d.group("aRout", 40, 310, 430, 190, "Routable subnet (10.100.0.0/24)", "white", size=11)
    d.box("pnat", 70, 350, 190, 70, "Private NAT gateway\n10.100.0.5\nSNAT: 10.0.1.25 → 10.100.0.5", "orange", size=11)
    d.box("rtA2", 280, 430, 170, 56,
          "Route table\n10.100.1.0/24 → TGW", "white", align="left", size=11)
    # TGW
    d.box("tgw", 515, 280, 170, 130,
          "Transit Gateway\nstatic routes only:\n10.100.0.0/24 → A\n10.100.1.0/24 → B\n(no 10.0.0.0/16!)", "purple", size=11)
    # VPC B
    d.group("vpcB", 710, 50, 470, 470, "VPC B (cluster B)\nprimary 10.0.0.0/16 (overlaps with A)\nsecondary 10.100.1.0/24 (unique, routable)", "green", size=12)
    d.group("bRout", 730, 310, 430, 190, "Routable subnet (10.100.1.0/24)", "white", size=11)
    d.box("nlb", 760, 350, 200, 70, "Internal NLB\n10.100.1.10\n(Service type LoadBalancer)", "orange", size=11)
    d.box("rtB2", 975, 350, 170, 70,
          "Route table\n10.100.0.0/24 → TGW\n(for the replies)", "white", align="left", size=11)
    d.group("bPriv", 730, 115, 430, 170, "Node and pod subnets (10.0.x.x, NOT routable outside)", "white", size=11)
    d.box("podB", 820, 160, 230, 60, "Pods of the target service\n10.0.1.25 too! (same IPs)", "green")
    d.edge("podA", "pnat", "1. dst 10.100.1.10")
    d.edge("pnat", "tgw", "2. src now 10.100.0.5", points=[(600, 385)])
    d.edge("tgw", "nlb", "3.")
    d.edge("nlb", "podB", "4. NLB → pod IP\n(local route in VPC B)")
    d.text("caption", 0, 540, 1200, 90,
           "Why plain peering / TGW fail: in each VPC the local route (10.0.0.0/16 → local) always wins, so 10.0.x.x can never mean 'the other VPC'.\n"
           "Fix: only unique, routable addresses cross the TGW. Outbound, the private NAT hides pod A behind 10.100.0.5.\n"
           "Inbound, the NLB in the routable subnet is the only address A can reach in B. Replies retrace the same path (NAT keeps connection state).\n"
           "B → A needs the mirror image (private NAT in B, NLB in A). Easier per-service options: VPC Lattice or PrivateLink.",
           size=12, italic=True)
    return d


def pod_cidr_separate():
    d = Diagram("s3-node-vs-pod-cidr", 1100, 620,
                "Nodes and pods in different CIDRs: VPC CNI custom networking / Auto Mode pod subnets")
    d.group("vpc", 20, 50, 700, 500, "VPC: primary 10.0.0.0/16 + secondary 100.64.0.0/16 (same AZ: us-west-1a)", "gray", size=12)
    d.group("nsub", 40, 90, 300, 440, "Node subnet 10.0.12.0/24\n(primary CIDR, small, routable)", "blue", size=11)
    d.group("psub", 400, 90, 300, 440, "Pod subnet 100.64.1.0/24\n(secondary CIDR, big, non-routable)", "green", size=11)
    d.group("node", 60, 160, 620, 300, "EC2 node (one instance, network interfaces in both subnets)", "white", size=11)
    d.box("eth0", 80, 200, 240, 90, "eth0 = primary ENI\nnode IP 10.0.12.201\nnode security group\nno pod IPs on it", "blue", size=11)
    d.box("hostpods", 80, 320, 240, 110, "hostNetwork pods use the node IP\naws-node, kube-proxy\n10.0.12.201", "white", size=11)
    d.box("eth1", 420, 200, 240, 90, "eth1, eth2 = secondary ENIs\nin the pod subnet\npod security group", "green", size=11)
    d.box("pods", 420, 320, 240, 110, "Normal pods\n100.64.1.23\n100.64.1.24 …\n(/28 prefixes or single IPs)", "green", size=11)
    d.edge("eth1", "pods", "pod IPs come from here")
    d.edge("pods", "eth0", "leaving VPC:\nSNAT to\nnode IP", dashed=True, points=[(370, 400), (370, 260)])
    d.box("cfg1", 760, 70, 320, 140,
          "VPC CNI (managed node groups)\naws-node env:\nAWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true\nENI_CONFIG_LABEL_DEF=\n  topology.kubernetes.io/zone\nENIConfig per AZ → pod subnet + SG",
          "yellow", align="left", size=11)
    d.box("cfg2", 760, 240, 320, 140,
          "EKS Auto Mode (your own NodeClass)\nsubnetSelectorTerms → node subnet\nsecurityGroupSelectorTerms → node SG\npodSubnetSelectorTerms → pod subnet\npodSecurityGroupSelectorTerms → pod SG\n(both pod fields together)",
          "yellow", align="left", size=11)
    d.box("cost", 760, 410, 320, 120,
          "The price you pay\n• fewer pods per node (eth0 not used)\n  m5.large: 29 → 20 without prefixes\n• only NEW nodes use it: replace old ones\n• outside VPC sees the node IP, not pod IP",
          "red", align="left", size=11)
    d.text("caption", 0, 565, 1100, 44,
           "Why do it: subnets ran out of IPs, pods need different security groups, or pods must stay non-routable\n"
           "while nodes keep routable IPs for on-prem / Transit Gateway. Debug with: kubectl get nodes -o wide vs kubectl get pods -o wide.",
           size=12, italic=True)
    return d


def controllers_fight():
    d = Diagram("s4-two-controllers-fight", 1000, 430,
                "One2N incident: two controllers own the same object (the built-in NodeClass `default`)")
    d.box("git", 30, 70, 210, 80, "Git repo\nNodeClass name: default\n+ podSubnetSelectorTerms", "gray", size=11)
    d.box("argo", 30, 220, 210, 80, "Argo CD\nsync: write Git's version", "blue")
    d.box("obj", 395, 140, 210, 100, "NodeClass `default`\n(live object)\nthe same name, two owners", "yellow")
    d.box("auto", 760, 140, 210, 100, "EKS Auto Mode controller\nreconcile: reset `default`\nto AWS's spec", "orange")
    d.box("pods", 345, 300, 300, 80, "Pods flip between 100.64.x.x and 10.0.x.x\nrestarts every few minutes\nArgo CD: OutOfSync forever", "red", size=11)
    d.edge("git", "argo", "desired")
    d.edge("argo", "obj", "adds pod subnet fields", points=[(330, 260)])
    d.edge("auto", "obj", "removes them again")
    d.edge("obj", "pods", "nodes drift → replaced")
    d.text("fix", 640, 290, 350, 100,
           "Fix: give yours its own name\n(e.g. prod-nodeclass) and point the\nNodePool's nodeClassRef.name at it.\nOne object = one owner.",
           size=12, bold=False, align="left")
    return d


def helm_merge_cases():
    d = Diagram("s5-helm-merge-cases", 1200, 560,
                "Tested: what happens to each field on helm upgrade (Helm 4.2.3, Kubernetes 1.34)")
    cols = [  # (x, width, header)
        (20, 170, "Field"), (200, 130, "OLD\nlast Helm apply"), (340, 160, "LIVE\ncluster now"),
        (510, 130, "NEW\nchart now"), (650, 190, "3-way merge\n(Helm 3 way, csa)"),
        (850, 170, "Server-side apply\n(Helm 4, ssa)"), (1030, 150, "--force-replace\n(LIVE becomes NEW)"),
    ]
    for c, (x, w, label) in enumerate(cols):
        d.box(f"h{c}", x, 50, w, 50, label, "gray", size=11)
    rows = [  # field, OLD, LIVE, NEW, then (text, colour) for the three results
        ("spec.replicas", "3", "5\n(kubectl edit)", "3",
         ("3: reverted\nNEW ≠ LIVE → set", "blue"), ("conflict, then 3\nwith --force-conflicts", "yellow"), ("3", "blue")),
        ("annotation team", "–", "x\n(kubectl annotate)", "–",
         ("x: kept\nonly in LIVE", "green"), ("x: kept\nowner: kubectl-annotate", "green"), ("lost", "red")),
        ("env DEBUG=true", "–", "true\n(kubectl set env)", "–",
         ("kept\nlist merged by name", "green"), ("kept\nowner: kubectl-set", "green"), ("lost", "red")),
        ("pod annotation\nowner", "helm-team", "helm-team", "removed\nfrom the chart",
         ("deleted\nin OLD, not in NEW", "blue"), ("deleted\nHelm was the only owner", "blue"), ("deleted", "blue")),
        ("pod annotation\nrestartedAt", "–", "set\n(rollout restart)", "–",
         ("LOST if the chart dropped\nthe whole annotations block;\nkept if the block remains", "orange"),
         ("kept\nowner: kubectl-rollout", "green"), ("lost", "red")),
    ]
    for r, (field, old, live, new, *results) in enumerate(rows):
        y = 110 + r * 66
        d.box(f"f{r}", 20, y, 170, 58, field, "gray", size=11, bold=True)
        for c, text in ((1, old), (2, live), (3, new)):
            x, w, _ = cols[c]
            d.box(f"c{r}{c}", x, y, w, 58, text, "white", size=11, bold_first=False)
        for c, (text, colour) in zip((4, 5, 6), results):
            x, w, _ = cols[c]
            d.box(f"c{r}{c}", x, y, w, 58, text, colour, size=11)
    d.text("rules", 20, 448, 1160, 90,
           "The 3 rules of the 3-way merge: (1) NEW ≠ LIVE → set it to NEW.  (2) In OLD but not in NEW → delete it, "
           "at the level where OLD and NEW differ.  (3) Only in LIVE → leave it alone.\n"
           "Server-side apply uses per-field owners instead of OLD, so it deletes only fields Helm alone owned.  "
           "--force-replace overwrites the object with NEW, so every hand-made change is lost.\n"
           "Green = someone else's change survived · Blue = the chart's intent applied · "
           "Orange / red = someone else's change was lost",
           size=11)
    return d


def ssa_field_owners():
    d = Diagram("s6-ssa-field-owners", 1100, 580,
                "Helm 4 server-side apply: every field has an owner (metadata.managedFields)")
    d.group("obj", 20, 50, 470, 320, "Deployment web · its name tags (managedFields)", "gray", size=12)
    d.box("t1", 40, 100, 430, 54, "spec.replicas\nowner: kubectl-edit · Update (taken from helm)", "red", size=11)
    d.box("t2", 40, 166, 430, 54, "spec.template (image, labels, pod annotations…)\nowner: helm · Apply", "blue", size=11)
    d.box("t3", 40, 232, 430, 54, "metadata.annotations.team\nowner: kubectl-annotate · Update", "green", size=11)
    d.box("t4", 40, 298, 430, 54, "status\nowner: controllers · subresource status", "white", size=11)
    d.box("s1", 540, 60, 540, 54, "1 · helm install\nHelm (Apply) owns every field it sends", "blue", size=11)
    d.box("s2", 540, 140, 540, 54, "2 · kubectl edit: replicas 3 → 5\nA normal write that changes a value takes the name tag",
          "orange", size=11)
    d.box("s3", 540, 220, 540, 54, "3 · helm upgrade with the same values\nThe API server checks the tags → conflict, the upgrade fails",
          "red", size=11)
    d.box("c1", 540, 320, 175, 72, "--force-conflicts\nHelm takes the tag back:\nreplicas = 3", "white", size=11)
    d.box("c2", 723, 320, 175, 72, "Put 5 in the values\nsame value = shared tag,\nno conflict", "white", size=11)
    d.box("c3", 905, 320, 175, 72, "Stop setting replicas\nsafe only if another\nowner (HPA) has it first", "white", size=11)
    d.edge("s1", "s2")
    d.edge("s2", "s3")
    d.edge("s3", "c1")
    d.edge("s3", "c2")
    d.edge("s3", "c3")
    d.box("n1", 20, 420, 520, 130,
          "Rule: the only owner stops sending a field → it is DELETED\nTested: the chart stopped setting replicas while Helm was the\n"
          "only owner → replicas 3 → 1, and the HPA restored 4 about\n15 seconds later. Let the HPA own the field first, then remove it.",
          "yellow", size=11, align="left")
    d.box("n2", 560, 420, 520, 130,
          "Helm 3 way (apply_method = csa) never checks the tags\nIt sends a normal Update, so replicas silently goes back to 3.\n"
          "Each release Secret stores apply_method (ssa or csa), and\n--server-side=auto reuses it on the next upgrade.",
          "gray", size=11, align="left")
    return d


def option_lattice():
    d = Diagram("s7-option1-vpc-lattice", 1200, 560,
                "Option 1 · Amazon VPC Lattice: call services by name, so VPC IPs never matter")
    d.group("vpcA", 20, 50, 360, 390, "VPC A (cluster A)\n10.0.0.0/16", "blue", size=12)
    d.box("podA", 50, 125, 300, 56, "Client pod\n10.0.1.25", "blue", size=11)
    d.box("dns", 50, 215, 300, 76,
          "DNS name of the Lattice service\norders-0abc….vpc-lattice-svcs.us-west-1.on.aws\n→ 169.254.171.x (link-local, not a VPC IP)",
          "white", size=10)
    d.box("assoc", 50, 330, 300, 80, "VPC association with the\nservice network (its security\ngroup allows the clients)", "white", size=11)
    d.group("sn", 420, 50, 360, 390, "VPC Lattice service network\n(AWS-managed, outside both VPCs)", "purple", size=12)
    d.box("svc", 450, 125, 300, 70, "Lattice service: orders\nlistener HTTPS 443 → target group", "white", size=11)
    d.box("auth", 450, 230, 300, 70, "Auth policy (IAM)\nonly cluster A's role may call orders", "yellow", size=11)
    d.text("why", 450, 330, 300, 80,
           "Routes by service name,\nnever by VPC IP:\nthe overlap doesn't matter", size=12, bold=True)
    d.group("vpcB", 820, 50, 360, 390, "VPC B (cluster B)\n10.0.0.0/16 (the same range!)", "green", size=12)
    d.box("ctrl", 850, 125, 300, 70, "AWS Gateway API Controller\nturns an HTTPRoute into the\nLattice service + its targets", "white", size=11)
    d.box("podsB", 850, 230, 300, 56, "orders pods\n10.0.1.25 too", "green", size=11)
    d.box("sgB", 850, 320, 300, 80, "Pod security group: allow\n169.254.171.0/24 (the Lattice\nmanaged prefix list)", "white", size=11)
    d.edge("podA", "dns", "1 · look up the name")
    d.edge("podA", "svc", "2 · HTTPS")
    d.edge("svc", "podsB", "3 · to the targets")
    d.edge("ctrl", "svc", "creates", dashed=True)
    d.text("cap", 20, 460, 1160, 80,
           "Best for many HTTP/gRPC services across teams and accounts, with IAM auth between them. Any associated VPC can call\n"
           "any service in the network (if the auth policy allows). Costs: per service-hour, per GB and per request. Mostly layer 7.",
           size=12, italic=True)
    return d


def option_privatelink():
    d = Diagram("s8-option2-privatelink", 1200, 560,
                "Option 2 · AWS PrivateLink: B publishes one service, A reaches it through an IP of its own")
    d.group("vpcA", 20, 50, 420, 390, "VPC A, the consumer\n10.0.0.0/16", "blue", size=12)
    d.box("podA", 50, 125, 360, 56, "Client pod\n10.0.1.25", "blue", size=11)
    d.box("ep", 50, 225, 360, 80,
          "Interface VPC endpoint\nan ENI in A's own subnet: 10.0.5.20\n(private DNS: orders.b.internal → 10.0.5.20)", "orange", size=11)
    d.text("noteA", 50, 330, 360, 90, "A only talks to an IP inside A.\nNothing is routed between the VPCs,\nso the overlap doesn't matter.",
           size=12, bold=True)
    d.box("pl", 470, 225, 240, 80, "AWS PrivateLink\none direction: A → B", "purple", size=12)
    d.group("vpcB", 740, 50, 440, 390, "VPC B, the provider\n10.0.0.0/16 (the same range)", "green", size=12)
    d.box("es", 770, 125, 380, 56, "Endpoint service\nallowed principals: account A", "white", size=11)
    d.box("nlb", 770, 225, 380, 80,
          "Internal NLB\n(Service type: LoadBalancer, made by\nthe AWS Load Balancer Controller)", "orange", size=11)
    d.box("podsB", 770, 340, 380, 56, "orders pods\n10.0.1.25 too", "green", size=11)
    d.edge("podA", "ep", "1 · TCP to 10.0.5.20:443")
    d.edge("ep", "pl", "2")
    d.edge("pl", "es", "3")
    d.edge("es", "nlb", "4")
    d.edge("nlb", "podsB", "5")
    d.text("cap", 20, 460, 1160, 80,
           "Best for 1–2 TCP services, one direction, strong isolation, cross-account. B sees the NLB's IP as the source, not 10.0.1.25\n"
           "(turn on proxy protocol v2 if the app needs the client IP). One endpoint per service and per direction: B → A needs its own setup.",
           size=12, italic=True)
    return d


def option_reip():
    d = Diagram("s9-option4-re-ip", 1200, 640,
                "Option 4 · Remove the overlap: a new VPC with a unique CIDR, then move the apps blue/green")
    d.box("ipam", 20, 50, 1160, 56,
          "AWS VPC IPAM pool (e.g. 10.0.0.0/8 split per region and team)\nhands out a unique CIDR to every new VPC, so this can never happen again",
          "yellow", size=12)
    d.group("vpcA", 20, 140, 330, 190, "VPC A (stays)\n10.0.0.0/16", "blue", size=12)
    d.box("podA", 50, 220, 270, 56, "Client pods in cluster A", "blue", size=11)
    d.group("vpcOld", 430, 140, 330, 190, "VPC B, OLD\n10.0.0.0/16 (overlaps A)", "red", size=12)
    d.box("old", 460, 220, 270, 56, "orders, old cluster\n(retired at the end)", "white", size=11)
    d.group("vpcNew", 850, 140, 330, 190, "VPC B2, NEW\n10.20.0.0/16 (from IPAM)", "green", size=12)
    d.box("new", 880, 220, 270, 56, "orders, new cluster\n(same Terraform + GitOps)", "green", size=11)
    d.box("r53", 400, 370, 400, 70,
          "Route 53 weighted records for api.b.example\nold: 90 → 50 → 0 %    new: 10 → 50 → 100 %", "blue", size=11)
    d.edge("r53", "old", "weight goes down", dashed=True)
    d.edge("r53", "new", "weight goes up")
    d.edge("vpcA", "vpcNew", "peering or TGW now works: no overlap", points=[(185, 470), (1015, 470)])
    d.text("steps", 20, 500, 1160, 120,
           "1 · Get a unique CIDR from IPAM.\n2 · Build VPC B2 and the new cluster from the same Terraform and GitOps code.\n"
           "3 · Shift traffic with DNS weights, watching error rates at each step.\n"
           "4 · Retire the old VPC B. Slow, but it's the real fix: every other option only works around the overlap.",
           size=12, italic=True)
    return d


def option_ipv6():
    d = Diagram("s10-option5-ipv6", 1200, 500,
                "Option 5 · IPv6 clusters: pod addresses are globally unique, so they can't overlap")
    d.group("vpcA", 20, 50, 460, 300,
            "VPC A (dual-stack)\nIPv4 10.0.0.0/16 (still overlaps)\nIPv6 e.g. 2600:1f14:a::/56 (unique)", "blue", size=12)
    d.box("clA", 50, 150, 400, 60, "EKS cluster A, IP family IPv6\nchosen at creation, can't be changed later", "white", size=11)
    d.box("podA", 50, 250, 400, 60, "Pod 2600:1f14:a:1::5\n(each node gets a /80 prefix from the subnet)", "blue", size=11)
    d.box("tgw", 505, 170, 190, 150, "Transit Gateway\nor peering\nIPv6 routes:\n…a::/56 → A\n…b::/56 → B\npod to pod, no NAT", "purple", size=11)
    d.group("vpcB", 720, 50, 460, 300,
            "VPC B (dual-stack)\nIPv4 10.0.0.0/16 (still overlaps)\nIPv6 e.g. 2600:1f14:b::/56 (unique)", "green", size=12)
    d.box("clB", 750, 150, 400, 60, "EKS cluster B, IP family IPv6", "white", size=11)
    d.box("podB", 750, 250, 400, 60, "orders pod 2600:1f14:b:2::9", "green", size=11)
    d.edge("podA", "tgw")
    d.edge("tgw", "podB")
    d.box("why", 20, 370, 560, 110,
          "Why it works\nEvery IPv6 address is globally unique, so pod IPs\ncan never overlap. Security groups and NetworkPolicy\nstill control who may connect.",
          "yellow", size=11, align="left")
    d.box("limits", 600, 370, 580, 110,
          "Limits\nIPv4 still overlaps: a pod calling an IPv4-only address\nuses its node's IPv4 (SNAT), so IPv4-only services still need\n"
          "options 1–3. An IPv4 cluster can't be converted: build a new one.",
          "gray", size=11, align="left")
    return d


def two_way():
    d = Diagram("s11-two-way-private-nat", 1200, 600,
                "Two-way traffic with option 3: each side needs its OWN way out (private NAT) and its OWN way in (NLB)")
    d.group("vpcA", 20, 50, 470, 380, "VPC A · 10.0.0.0/16 + unique 10.100.0.0/24", "blue", size=12)
    d.box("podA", 40, 200, 150, 80, "Pods in A\n10.0.x.x", "blue", size=11)
    d.box("natA", 240, 100, 230, 76, "Private NAT A · 10.100.0.5\nway OUT for A → B\n(hides A's pods)", "orange", size=11)
    d.box("nlbA", 240, 320, 230, 76, "Internal NLB A · 10.100.0.10\nway IN for B → A", "orange", size=11)
    d.box("tgw", 520, 190, 160, 100, "Transit Gateway\n10.100.0.0/24 → A\n10.100.1.0/24 → B", "purple", size=11)
    d.group("vpcB", 710, 50, 470, 380, "VPC B · 10.0.0.0/16 + unique 10.100.1.0/24", "green", size=12)
    d.box("nlbB", 730, 100, 230, 76, "Internal NLB B · 10.100.1.10\nway IN for A → B", "orange", size=11)
    d.box("natB", 730, 320, 230, 76, "Private NAT B · 10.100.1.5\nway OUT for B → A\n(hides B's pods)", "orange", size=11)
    d.box("podB", 1010, 200, 150, 80, "Pods in B\n10.0.x.x too", "green", size=11)
    d.edge("podA", "natA", "A starts")
    d.edge("natA", "tgw")
    d.edge("tgw", "nlbB")
    d.edge("nlbB", "podB")
    d.edge("podB", "natB", "B starts")
    d.edge("natB", "tgw")
    d.edge("tgw", "nlbA")
    d.edge("nlbA", "podA")
    d.box("why", 20, 450, 570, 130,
          "Why one NAT can't carry both directions\nA NAT translates only connections that START inside it (it\nremembers them, like conntrack). A packet that arrives at 10.100.0.5\n"
          "with no matching connection has no pod to go to, so it's dropped.\nAWS NAT gateways never forward ports inward: the way in is an NLB.",
          "yellow", size=11, align="left")
    d.box("others", 610, 450, 570, 130,
          "Two-way with the other options\nLattice: built in. Each side publishes services in the same service network.\n"
          "PrivateLink: one endpoint service per direction (mirror the setup).\nRe-IP or IPv6: normal routing both ways; security groups decide.\n"
          "Replies never need extra setup: they follow the existing connection.",
          "gray", size=11, align="left")
    return d


def why_not_bastion_vpn():
    d = Diagram("s12-why-not-bastion-or-vpn", 1200, 580,
                "Why a bastion or a VPN doesn't fix overlapping CIDRs: neither changes the addresses")
    d.group("vpcA", 20, 50, 570, 380, "VPC A · 10.0.0.0/16", "blue", size=12)
    d.box("podA", 50, 110, 220, 70, "Pod A wants orders in B\ndst 10.0.1.25", "blue", size=11)
    d.box("rt", 330, 100, 230, 96, "VPC A route table\n10.0.0.0/16 → local\n(always wins; a VPN route\nfor it can never win)", "white", size=11)
    d.box("local", 50, 250, 220, 80, "Delivered inside A\nto A's own 10.0.1.25,\nor to nobody", "red", size=11)
    d.box("box", 330, 250, 230, 80, "Bastion host / VPN gateway\nup and running, but no packet\nis ever routed to it", "gray", size=11)
    d.group("vpcB", 650, 50, 530, 380, "VPC B · 10.0.0.0/16 (the same range)", "green", size=12)
    d.box("podB", 760, 150, 300, 70, "orders pod\n10.0.1.25", "green", size=11)
    d.box("bB", 760, 270, 300, 60, "The other end of the tunnel / SSH", "white", size=11)
    d.edge("podA", "rt", "1 · send to 10.0.1.25")
    d.edge("rt", "local", "2 · local route wins")
    d.edge("box", "bB", "tunnel or SSH: up, but unused", dashed=True)
    d.box("bastion", 20, 450, 570, 110,
          "Bastion = a door for PEOPLE (SSH or SSM), not a path for app traffic\nIt sits in one VPC, so it has the same routing problem. Making it carry\n"
          "app traffic means hand-made SSH tunnels or a proxy: one box, no high\navailability, manual, and an extra way in for attackers.",
          "yellow", size=11, align="left")
    d.box("vpn", 610, 450, 570, 110,
          "VPN = a pipe between networks; it doesn't change addresses\nRouting still picks the local route, so nothing enters the pipe.\n"
          "It works only with NAT added on both ends: that is option 3,\nself-managed on VPN boxes (and about 1.25 Gbps per AWS VPN tunnel).",
          "gray", size=11, align="left")
    return d


def two_way_options():
    d = Diagram("s13-two-way-per-option", 1200, 620,
                "Two-way traffic (both sides START calls): what each option needs")
    panels = [  # (x, y, colour, title, footer, middle boxes: one shared box, or (top A→B, bottom B→A))
        (20, 50, "purple", "1 · VPC Lattice", "Two-way built in, per service.\nBoth VPCs join one service network.", ["service\nnetwork"]),
        (415, 50, "orange", "2 · PrivateLink", "Two separate setups, per service:\nNLB + endpoint service on each side.",
         ["setup 1 (A → B)\nendpoint svc in B", "setup 2 (B → A)\nendpoint svc in A"]),
        (810, 50, "yellow", "3 · Private NAT + TGW", "Network level, with NAT:\nNAT + NLB on EACH side (4 desks).",
         ["NAT A → NLB B", "NAT B → NLB A"]),
        (217, 320, "green", "4 · Re-IP (unique CIDRs)", "Full two-way: any port, any protocol,\nno NAT. Security groups decide.", ["TGW or\npeering"]),
        (612, 320, "blue", "5 · IPv6 clusters", "Full two-way for IPv6 traffic.\nIPv4-only traffic still overlaps.", ["TGW or\npeering\n(IPv6)"]),
    ]
    for i, (x, y, colour, title, footer, mids) in enumerate(panels):
        d.group(f"p{i}", x, y, 370, 250, title, colour, size=12)
        d.box(f"a{i}", x + 15, y + 80, 80, 60, "VPC A", "blue", size=11)
        d.box(f"b{i}", x + 275, y + 80, 80, 60, "VPC B", "green", size=11)
        if len(mids) == 1:
            d.box(f"m{i}", x + 125, y + 75, 120, 70, mids[0], "white", size=11, bold_first=False)
            d.edge(f"a{i}", f"m{i}", both=True)
            d.edge(f"m{i}", f"b{i}", both=True)
        else:
            d.box(f"t{i}", x + 112, y + 45, 146, 48, mids[0], "white", size=10, bold_first=False)
            d.box(f"u{i}", x + 112, y + 127, 146, 48, mids[1], "white", size=10, bold_first=False)
            d.edge(f"a{i}", f"t{i}")
            d.edge(f"t{i}", f"b{i}")
            d.edge(f"b{i}", f"u{i}")
            d.edge(f"u{i}", f"a{i}")
        d.text(f"f{i}", x + 10, y + 190, 350, 50, footer, size=11)
    d.text("cap", 20, 585, 1160, 24,
           "Replies never need extra setup: they follow the existing connection. Only STARTING a call from the other side does.",
           size=12, italic=True)
    return d


def transit_gateway():
    d = Diagram("s14-transit-gateway", 1200, 700, "AWS Transit Gateway: one regional hub instead of a mesh of peerings")
    d.box("vpcA", 20, 70, 280, 80, "VPC A · 10.1.0.0/16\n(attachment: an ENI in one\nsmall subnet per AZ)", "blue", size=11)
    d.box("vpcB", 20, 230, 280, 80, "VPC B · 10.2.0.0/16", "green", size=11)
    d.box("shared", 900, 70, 280, 80, "Shared-services VPC · 10.3.0.0/16\n(DNS, CI runners, monitoring)", "gray", size=11)
    d.box("vpn", 900, 230, 280, 80, "On-premises · 192.168.0.0/16\nvia Site-to-Site VPN or\nDirect Connect gateway", "orange", size=11)
    d.box("tgw", 470, 130, 260, 120, "Transit Gateway\nregional hub · transitive\nshared across accounts with RAM", "purple", size=12)
    d.edge("vpcA", "tgw", "attachment", both=True)
    d.edge("vpcB", "tgw", "attachment", both=True)
    d.edge("shared", "tgw", "attachment", both=True)
    d.edge("vpn", "tgw", "attachment", both=True)
    d.box("rt", 400, 290, 400, 130,
          "TGW route table\n10.1.0.0/16 → VPC A attachment (propagated)\n10.2.0.0/16 → VPC B attachment (propagated)\n"
          "10.3.0.0/16 → shared attachment (propagated)\n192.168.0.0/16 → VPN attachment (learned by BGP)",
          "white", size=11, align="left")
    d.edge("tgw", "rt", "looks up", dashed=True)
    d.text("path-h", 20, 450, 1160, 24, "One packet from VPC A to VPC B checks THREE route tables:", size=13, bold=True, align="left")
    d.box("p1", 20, 485, 360, 76, "1 · VPC A subnet route table\n10.2.0.0/16 → tgw-0abc", "blue", size=11)
    d.box("p2", 420, 485, 360, 76, "2 · TGW route table (associated with A)\n10.2.0.0/16 → VPC B attachment", "purple", size=11)
    d.box("p3", 820, 485, 360, 76, "3 · VPC B subnet route table (for the reply)\n10.1.0.0/16 → tgw-0abc", "green", size=11)
    d.edge("p1", "p2")
    d.edge("p2", "p3")
    d.text("cap", 20, 585, 1160, 100,
           "Association: each attachment uses exactly ONE TGW route table for traffic coming from it.  "
           "Propagation: an attachment can add its CIDRs to route tables automatically.\n"
           "Several route tables = segmentation (e.g. prod can't reach dev).  A route table can't hold two routes for the same prefix,\n"
           "so two VPCs with the same CIDR can't both be reached: that's why overlapping CIDRs need NAT or unique ranges (A2).",
           size=12, italic=True)
    return d


def option3_inbound_lbs():
    d = Diagram("s15-option3-inbound-load-balancers", 1200, 760,
                "Option 3, the way IN to VPC B: four load balancer set-ups in the unique routable subnet")
    panels = [
        (20, 50, "blue", "A · Internal ALB (layer 7): HTTP only, simplest"),
        (610, 50, "purple", "B · NLB → controller (NLB = door, controller = receptionist)"),
        (20, 380, "orange", "C · NLB, one listener per port (non-HTTP)"),
        (610, 380, "green", "D · NLB → ALB (fixed IPs + layer-7 rules)"),
    ]
    for i, (x, y, colour, title) in enumerate(panels):
        d.group(f"p{i}", x, y, 570, 310, title, colour, size=12)
        d.box(f"in{i}", x + 15, y + 115, 110, 64, "From A via TGW\nsrc 10.100.0.5", "white", size=10)
    x, y = 20, 50
    d.box("alb", x + 165, y + 95, 150, 104, "Internal ALB\nreads host + path\nsubnets in 2 AZs", "blue", size=11)
    d.box("a-o", x + 375, y + 65, 180, 50, "orders pods\nhost orders.b.internal", "green", size=11)
    d.box("a-p", x + 375, y + 175, 180, 50, "payments pods\nhost payments.b.internal", "green", size=10)
    d.edge("in0", "alb")
    d.edge("alb", "a-o")
    d.edge("alb", "a-p")
    d.text("f0", x + 10, y + 245, 550, 55,
           "The ALB routes by host and path itself. Its IPs change as it scales,\nso clients use its DNS name.", size=11)
    x, y = 610, 50
    d.box("nlb1", x + 150, y + 105, 110, 84, "NLB\nport 443 only\nfixed IPs", "orange", size=11)
    d.box("ctl", x + 290, y + 95, 120, 104, "Envoy Gateway\npods\nread host / SNI", "purple", size=11)
    d.box("b-o", x + 440, y + 65, 115, 50, "orders\norders.b.internal", "green", size=10)
    d.box("b-p", x + 440, y + 175, 115, 50, "payments\npayments.b.int…", "green", size=10)
    d.edge("in1", "nlb1")
    d.edge("nlb1", "ctl")
    d.edge("ctl", "b-o")
    d.edge("ctl", "b-p")
    d.text("f1", x + 10, y + 245, 550, 55,
           "One NLB, many services. The NLB never reads names; the routes\n(HTTPRoute or Ingress) live in the controller. TLS passthrough works.", size=11)
    x, y = 20, 380
    d.box("nlb2", x + 165, y + 85, 170, 124, "NLB\nlistener 5432 → TG db\nlistener 9092 → TG kafka", "orange", size=11)
    d.box("c-d", x + 385, y + 65, 170, 50, "postgres pods", "green", size=11)
    d.box("c-k", x + 385, y + 175, 170, 50, "kafka pods", "green", size=11)
    d.edge("in2", "nlb2")
    d.edge("nlb2", "c-d", "port 5432")
    d.edge("nlb2", "c-k", "port 9092")
    d.text("f2", x + 10, y + 245, 550, 55,
           "Routing by port only. Each target group is bound to its Service with\nTargetGroupBinding (AWS Load Balancer Controller).", size=11)
    x, y = 610, 380
    d.box("nlb3", x + 150, y + 105, 110, 84, "NLB\nfixed IPs", "orange", size=11)
    d.box("alb2", x + 290, y + 95, 120, 104, "ALB\n(the NLB's\ntarget)\nhost / path", "blue", size=11)
    d.box("d-o", x + 440, y + 65, 115, 50, "orders", "green", size=11)
    d.box("d-p", x + 440, y + 175, 115, 50, "payments", "green", size=11)
    d.edge("in3", "nlb3")
    d.edge("nlb3", "alb2")
    d.edge("alb2", "d-o")
    d.edge("alb2", "d-p")
    d.text("f3", x + 10, y + 245, 550, 55,
           "For when firewall rules need fixed IPs\nbut you still want ALB routing rules.", size=11)
    d.text("cap", 20, 705, 1160, 45,
           "Rule: an NLB is layer 4 and routes only by listener port. Host or path routing always happens in a layer-7 hop:\n"
           "an ALB, or an ingress / gateway controller. Fewer load balancers = lower cost and fewer IPs used in the small routable CIDR.",
           size=12, italic=True)
    return d


def custom_networking_before_after():
    d = Diagram("s16-custom-networking-before-after", 1200, 690,
                "VPC CNI (Container Network Interface) custom networking: where pod IPs come from, before and after")
    d.group("before", 20, 50, 560, 420, "BEFORE · default VPC CNI", "red", size=13)
    d.group("bsub", 40, 105, 520, 345, "Node subnet 10.0.12.0/24 (us-west-1a) · about 250 IPs", "white", size=11)
    d.box("bnode", 60, 215, 200, 64, "Node (EC2 instance)\nm5.large", "gray", size=11)
    d.box("beni1", 290, 140, 250, 70, "Primary ENI\nnode IP 10.0.12.201\n+ 9 pod IPs from this subnet", "orange", size=11)
    d.box("beni2", 290, 225, 250, 56, "Secondary ENI 2\n9 more pod IPs from this subnet", "orange", size=11)
    d.box("beni3", 290, 296, 250, 56, "Secondary ENI 3\n9 more pod IPs from this subnet", "orange", size=11)
    d.edge("bnode", "beni1")
    d.edge("bnode", "beni2")
    d.edge("bnode", "beni3")
    d.text("bnote", 50, 370, 500, 70,
           "Every pod takes an IP from the SAME small subnet as its node\n→ the subnet runs out: \"failed to assign an IP address to container\"",
           size=11, bold=True)
    d.group("after", 620, 50, 560, 420, "AFTER · custom networking", "green", size=13)
    d.group("asub1", 640, 105, 520, 110, "Node subnet 10.0.12.0/24 (primary CIDR 10.0.0.0/16)", "white", size=11)
    d.box("anode", 660, 140, 180, 60, "Node (EC2 instance)\nm5.large", "gray", size=11)
    d.box("aeni1", 870, 140, 270, 60, "Primary ENI\nnode IP 10.0.12.201 ONLY", "orange", size=11)
    d.group("asub2", 640, 240, 520, 210, "Pod subnet 100.64.1.0/24 (secondary CIDR 100.64.0.0/16)", "white", size=11)
    d.box("aeni2", 660, 300, 230, 70, "Secondary ENI 2\npod IPs 100.64.1.x", "blue", size=11)
    d.box("aeni3", 910, 300, 230, 70, "Secondary ENI 3\npod IPs 100.64.1.x", "blue", size=11)
    d.edge("anode", "aeni1")
    d.edge("anode", "aeni2")
    d.edge("anode", "aeni3")
    d.text("why-h", 20, 490, 1160, 24, "Why teams do this", size=13, bold=True, align="left")
    d.box("w1", 20, 520, 370, 100, "1 · IP exhaustion (most common)\nNode subnets are often a small /24.\n100.64.0.0/10 (RFC 6598) gives lots of room.",
          "yellow", size=11, align="left")
    d.box("w2", 415, 520, 370, 100, "2 · Separate security groups\nPod traffic uses the ENIConfig's security\ngroup; the node keeps its own.",
          "yellow", size=11, align="left")
    d.box("w3", 810, 520, 370, 100, "3 · Save company IP addresses\nPods use 100.64.x, which never leaves the VPC.\nOutside sees only node IPs (SNAT).",
          "yellow", size=11, align="left")
    d.text("legend", 20, 635, 1160, 45,
           "Short terms: ENI = Elastic Network Interface · EC2 = Elastic Compute Cloud · CIDR = Classless Inter-Domain Routing · "
           "VPC = Virtual Private Cloud\nSNAT = Source Network Address Translation · RFC = Request for Comments · "
           "CNI = Container Network Interface", size=11, italic=True)
    return d


def custom_networking_steps():
    d = Diagram("s17-custom-networking-steps", 1200, 720,
                "Set up VPC CNI custom networking in 5 steps")
    steps = [
        ("1 · Add a secondary CIDR to the VPC, and a pod subnet in EACH AZ your nodes use",
         "aws ec2 associate-vpc-cidr-block --vpc-id vpc-0abc --cidr-block 100.64.0.0/16"),
        ("2 · Turn on custom networking in aws-node (the VPC CNI pods)",
         "AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true\nENI_CONFIG_LABEL_DEF=topology.kubernetes.io/zone"),
        ("3 · Create one ENIConfig per AZ, named after the AZ",
         "us-west-1a → subnet: subnet-0pod1a, securityGroups: sg-0podtraffic"),
        ("4 · Replace the nodes (old nodes keep the old set-up)",
         "new node group → cordon and drain the old nodes"),
        ("5 · Fix max pods (the primary ENI no longer hosts pods)",
         "m5.large: 29 → 20 · prefix delegation gives far more"),
    ]
    for i, (title, body) in enumerate(steps):
        d.box(f"s{i}", 20, 50 + i * 100, 580, 80, title + "\n" + body, ["blue", "purple", "green", "orange", "yellow"][i],
              size=11, align="left")
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.text("pick-h", 640, 50, 540, 24, "How a new node picks its ENIConfig", size=13, bold=True, align="left")
    d.box("k1", 640, 85, 540, 50, "The node has the label  topology.kubernetes.io/zone=us-west-1a", "white", size=11)
    d.box("k2", 640, 160, 540, 50, "ENI_CONFIG_LABEL_DEF says: \"use that label's value as the ENIConfig name\"", "white", size=11)
    d.box("k3", 640, 235, 540, 50, "ENIConfig us-west-1a → subnet-0pod1a + sg-0podtraffic", "green", size=11)
    d.box("k4", 640, 310, 540, 50, "The CNI creates the node's secondary ENIs in that pod subnet", "blue", size=11)
    d.edge("k1", "k2")
    d.edge("k2", "k3")
    d.edge("k3", "k4")
    d.box("math", 640, 390, 540, 110,
          "Max pods on an m5.large (3 ENIs, 10 IPs each)\nDefault:  3 × (10 − 1) + 2 = 29\n"
          "Custom networking:  (3 − 1) × (10 − 1) + 2 = 20\nPrefix delegation: far more (AWS suggests a cap of 110 on small instances)",
          "yellow", size=11, align="left")
    d.box("warn", 20, 560, 580, 80,
          "⚠ EKS managed add-on: put these settings in the add-on's configuration values.\n"
          "kubectl set env can be overwritten by the next add-on update (two owners again).", "red", size=11, align="left")
    d.box("legend", 640, 525, 540, 175,
          "Short terms\nVPC = Virtual Private Cloud\nCNI = Container Network Interface\nENI = Elastic Network Interface (a virtual network card)\n"
          "CIDR = Classless Inter-Domain Routing (an IP range)\nAZ = Availability Zone\nEKS = Elastic Kubernetes Service",
          "white", size=11, align="left")
    return d


if __name__ == "__main__":
    force = "--force" in sys.argv
    for build in (helm_three_way, overlapping_cidr, pod_cidr_separate, controllers_fight,
                  helm_merge_cases, ssa_field_owners, option_lattice, option_privatelink, option_reip, option_ipv6):
        dia = build()
        for w in dia.warnings:
            print("WARN", w)
        path = dia.save(OUT, force=force)
        print("wrote" if path else "skipped (exists)", dia.name)
