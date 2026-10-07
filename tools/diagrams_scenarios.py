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


if __name__ == "__main__":
    force = "--force" in sys.argv
    for build in (helm_three_way, overlapping_cidr, pod_cidr_separate, controllers_fight):
        dia = build()
        for w in dia.warnings:
            print("WARN", w)
        path = dia.save(OUT, force=force)
        print("wrote" if path else "skipped (exists)", dia.name)
