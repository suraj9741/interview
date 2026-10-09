#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/helm-chart/*.md.

Run once:  python3 tools/diagrams_helm.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "helm-chart" / "diagrams"


def helm_flow():
    d = Diagram("01-helm-flow", 1100, 470, "How Helm turns a chart into a running release")
    d.box("chart", 20, 60, 250, 100, "Chart (a folder or .tgz)\nChart.yaml · values.yaml\ntemplates/ · charts/ · crds/", "blue", size=11)
    d.box("vals", 20, 200, 250, 80, "Your values\n-f values-prod.yaml\n--set image.tag=4f2a9c1 (last wins)", "yellow", size=11)
    d.box("render", 320, 120, 220, 70, "Render\nGo templates + values\n(helm template stops here)", "purple", size=11)
    d.box("mani", 590, 120, 160, 70, "Manifests\nplain Kubernetes YAML", "white", size=11)
    d.box("apply", 790, 100, 290, 110, "Apply to the cluster\nHelm 4 new installs: server-side apply\nHelm 3 way: 3-way merge (CSA)\n+ hooks, + --wait if asked", "green", size=11)
    d.box("cluster", 820, 270, 230, 60, "Cluster objects\nDeployment, Service, HPA…", "gray", size=11)
    d.box("rel", 380, 260, 380, 100,
          "Release record = one Secret per revision\nsh.helm.release.v1.web.v4 (type helm.sh/release.v1)\n"
          "chart + values + rendered manifest + apply_method\n(gzip, then base64)", "orange", size=11)
    d.edge("chart", "render")
    d.edge("vals", "render")
    d.edge("render", "mani")
    d.edge("mani", "apply")
    d.edge("apply", "cluster")
    d.edge("apply", "rel", "stores revision N")
    d.text("cap", 20, 390, 1060, 60,
           "helm template = render only, nothing is sent.  helm upgrade = render + apply + a new revision.\n"
           "helm rollback 3 = apply revision 3's stored manifest again, saved as a NEW revision.  "
           "The stored manifest is the OLD input of the next 3-way merge.", size=11)
    return d


def helm_versions():
    d = Diagram("02-helm-versions", 1100, 470, "How each Helm version updates an object that someone edited by hand")
    cols = [(20, "Helm 2: 2-way merge"), (380, "Helm 3: 3-way merge (CSA)"), (740, "Helm 4: server-side apply (SSA)")]
    for i, (x, title) in enumerate(cols):
        d.text(f"t{i}", x, 44, 340, 24, title, size=14, bold=True)
    d.box("h2old", 20, 80, 165, 50, "OLD manifest", "gray", size=11)
    d.box("h2new", 195, 80, 165, 50, "NEW manifest", "blue", size=11)
    d.box("h2do", 20, 180, 340, 70, "Patch = OLD vs NEW only\n(Tiller computed it inside the cluster)", "white", size=11)
    d.box("h2res", 20, 300, 340, 70, "LIVE is ignored\nscaled to 0 by hand → stays 0", "red", size=11)
    d.edge("h2old", "h2do")
    d.edge("h2new", "h2do")
    d.edge("h2do", "h2res")
    d.box("h3old", 380, 80, 105, 50, "OLD", "gray", size=11)
    d.box("h3live", 497, 80, 105, 50, "LIVE", "red", size=11)
    d.box("h3new", 615, 80, 105, 50, "NEW", "blue", size=11)
    d.box("h3do", 380, 180, 340, 70, "helm computes the 3-way patch\non your laptop or CI runner = CSA", "white", size=11)
    d.box("h3res", 380, 300, 340, 70, "Sent as a plain Update: no owner check\n→ hand edits silently overwritten", "orange", size=11)
    d.edge("h3old", "h3do")
    d.edge("h3live", "h3do")
    d.edge("h3new", "h3do")
    d.edge("h3do", "h3res")
    d.box("h4new", 740, 80, 340, 50, "NEW = the whole desired object (Apply)", "blue", size=11)
    d.box("h4do", 740, 180, 340, 70, "The API server merges it\nusing an owner per field (managedFields)", "white", size=11)
    d.box("h4res", 740, 300, 340, 70, "Another owner + a different value → conflict\n(fix: values, or --force-conflicts)", "green", size=11)
    d.edge("h4new", "h4do")
    d.edge("h4do", "h4res")
    d.text("cap", 20, 395, 1060, 60,
           "Helm 4: new installs use SSA. Upgrades use --server-side=auto, which reuses the apply_method stored in the release\n"
           "(csa or ssa). So a release created by Helm 3 keeps the 3-way merge until one upgrade with --server-side=true.", size=11)
    return d


def upgrade_lifecycle():
    d = Diagram("05-upgrade-lifecycle", 1100, 520, "What happens during helm upgrade, in order")
    steps = [
        ("1 · Render\nchart + values", "purple"),
        ("2 · pre-upgrade hooks\nlowest weight first;\nHelm waits for each Job", "yellow"),
        ("3 · Apply objects\nSSA or CSA,\nin a fixed kind order", "green"),
        ("4 · Wait\nonly with --wait\n(default: hooks only)", "blue"),
        ("5 · post-upgrade hooks\ne.g. smoke tests,\nnotifications", "yellow"),
        ("6 · Release saved\nnew revision: deployed\nold one: superseded", "gray"),
    ]
    for i, (label, colour) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 178, 70, 165, 90, label, colour, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.box("fail", 200, 220, 700, 80,
          "Any step fails → the new revision is marked failed\n--rollback-on-failure → apply the last deployed revision again (on install: uninstall)\n"
          "--cleanup-on-fail → delete objects this upgrade created",
          "red", size=11)
    d.edge("s2", "fail", "fails", dashed=True)
    d.box("hooks", 20, 340, 520, 150,
          "Hook annotations (tested)\nhelm.sh/hook: pre-install, pre-upgrade, post-upgrade, pre-delete, test …\n"
          "helm.sh/hook-weight: \"-5\" runs before \"0\"\nhelm.sh/hook-delete-policy: before-hook-creation (default),\n"
          "    hook-succeeded, hook-failed\nhelm.sh/hook-output-log-policy: prints the hook's logs in helm's output",
          "yellow", size=11, align="left")
    d.box("notes", 560, 340, 520, 150,
          "Good to know\n--wait omitted = hookOnly: pods are NOT waited for\n--wait alone = watcher: waits until every object is ready\n"
          "crds/ folder: installed on first install only, never upgraded or deleted\n"
          "helm.sh/resource-policy: keep → never deleted by Helm",
          "gray", size=11, align="left")
    return d


def release_states():
    d = Diagram("06-release-states", 1100, 500, "Release revision states (helm history shows them)")
    d.box("pinst", 20, 80, 190, 56, "pending-install", "yellow", size=12)
    d.box("dep", 300, 80, 190, 56, "deployed\n(only one per release)", "green", size=12)
    d.box("sup", 580, 80, 190, 56, "superseded\nan older good revision", "gray", size=11)
    d.box("pupg", 300, 230, 190, 56, "pending-upgrade", "yellow", size=12)
    d.box("fail", 580, 230, 190, 56, "failed", "red", size=12)
    d.box("prb", 20, 230, 190, 56, "pending-rollback", "yellow", size=12)
    d.text("unin-h", 20, 362, 600, 24, "helm uninstall (from any state):", size=12, bold=True, align="left")
    d.box("unin", 20, 395, 190, 56, "uninstalling", "yellow", size=12)
    d.box("gone", 300, 395, 250, 56, "uninstalled: kept in history only\nwith --keep-history, else deleted", "white", size=11)
    d.edge("pinst", "dep", "install OK")
    d.edge("dep", "sup", "a newer revision\nis deployed")
    d.edge("dep", "pupg", "helm upgrade\n(new revision)")
    d.edge("pupg", "fail", "error")
    d.edge("prb", "dep", "rollback OK (new revision)", points=[(115, 180), (330, 180)])
    d.edge("fail", "prb", "helm rollback", points=[(675, 320), (115, 320)])
    d.edge("unin", "gone")
    d.box("stuck", 810, 80, 270, 300,
          "Stuck in pending-*?\n\nhelm was killed half-way\n(e.g. a cancelled CI job).\n\nNext run fails with:\n\"another operation\n(install/upgrade/rollback)\nis in progress\"\n\n"
          "Fix: helm history web,\nthen helm rollback web <last\ndeployed revision>\n\nPrevent: one deploy at a time\n(CI concurrency group)",
          "orange", size=11)
    d.text("cap", 20, 465, 780, 30,
           "pending-upgrade → deployed on success: the new revision becomes deployed and the old one superseded.", size=11)
    return d


ALL = [helm_flow, helm_versions, upgrade_lifecycle, release_states]

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
