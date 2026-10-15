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


def values_order():
    d = Diagram("01-values-order", 1000, 400, "Values: which one wins? (the higher layer wins)")
    d.box("hi", 20, 60, 90, 50, "highest\n(wins)", "none", size=11)
    d.box("lo", 20, 255, 90, 50, "lowest", "none", size=11)
    d.edge("lo", "hi")
    d.box("l4", 120, 60, 420, 50, "4 · --set, --set-string, --set-json, --set-file, --set-literal", "orange", size=11)
    d.box("l3", 120, 125, 420, 50, "3 · -f files, in the order given\n-f values.yaml -f values-prod.yaml (later wins)", "yellow", size=11,
          bold_first=False)
    d.box("l2", 120, 190, 420, 50, "2 · A parent chart's values for its subchart", "blue", size=11)
    d.box("l1", 120, 255, 420, 50, "1 · The chart's own values.yaml (defaults)", "gray", size=11)
    d.text("ex", 600, 40, 380, 24, "Example: image.tag", size=12, bold=True)
    d.box("e1", 600, 70, 380, 44, "values.yaml → tag: latest", "gray", size=11)
    d.box("e2", 600, 140, 380, 44, "-f values-prod.yaml → tag: 1.4", "yellow", size=11)
    d.box("e3", 600, 210, 380, 44, "--set image.tag=4f2a9c1", "orange", size=11)
    d.box("e4", 600, 280, 380, 44, "Result: 4f2a9c1", "green", size=12, bold=True)
    d.edge("e1", "e2")
    d.edge("e2", "e3")
    d.edge("e3", "e4")
    d.text("cap", 20, 345, 960, 40,
           "helm get values web -n shop = only what YOU passed.  Add --all to see the merged result.", size=11)
    return d


def release_secret():
    d = Diagram("01-release-secret", 1100, 400, "Where Helm keeps a release: one Secret per revision")
    d.box("s1", 20, 60, 240, 76, "Secret per revision\nsh.helm.release.v1.web.v3\nlabel status=deployed", "orange", size=11)
    d.box("s2", 340, 66, 160, 64, "base64 -d\n(Kubernetes' encoding)", "white", size=11)
    d.box("s3", 540, 66, 140, 64, "base64 -d\n(Helm's encoding)", "white", size=11)
    d.box("s4", 720, 66, 100, 64, "gunzip", "white", size=11)
    d.box("s5", 860, 60, 220, 76, "JSON release record", "green", size=12)
    d.edge("s1", "s2", ".data.release")
    d.edge("s2", "s3")
    d.edge("s3", "s4")
    d.edge("s4", "s5")
    d.group("keys", 20, 180, 1060, 140,
            "Inside (tested keys): apply_method, chart, config, hooks, info, manifest, name, namespace, version", "gray", size=12)
    d.box("k1", 40, 220, 320, 80, "manifest\nthe OLD input of the next\n3-way merge (02)", "blue", size=11)
    d.box("k2", 390, 220, 320, 80, "apply_method: csa or ssa\ndecides how the next upgrade\nis applied (03)", "purple", size=11)
    d.box("k3", 740, 220, 320, 80, "config = your values\nanyone who can read Secrets\nhere can read them", "red", size=11)
    d.edge("s5", "keys")
    d.text("cap", 20, 335, 1060, 50,
           "No Tiller since Helm 3: the cluster itself holds the history.  --history-max (default 10) = how many revision Secrets are kept.\n"
           "Never put passwords in values: use External Secrets or Sealed Secrets.", size=11)
    return d


def three_way_rules():
    d = Diagram("02-three-way-rules", 1100, 460, "3-way merge: two questions, so three inputs")
    d.box("old", 20, 55, 300, 80, "OLD\nmanifest stored in the release Secret\n(what Helm set last time)", "gray", size=11)
    d.box("new", 400, 55, 300, 80, "NEW\nthe chart rendered with\ntoday's values", "blue", size=11)
    d.box("live", 780, 55, 300, 80, "LIVE\nthe object in the cluster now", "red", size=11)
    d.box("qdel", 170, 190, 320, 64, "What should I DELETE?\ncompare OLD vs NEW", "orange", size=12)
    d.box("qset", 610, 190, 320, 64, "What should I SET?\ncompare NEW vs LIVE", "green", size=12)
    d.edge("old", "qdel")
    d.edge("new", "qdel")
    d.edge("new", "qset")
    d.edge("live", "qset")
    d.box("r1", 20, 310, 340, 76, "In OLD, not in NEW → delete it\nonly what Helm set itself", "orange", size=11)
    d.box("r2", 380, 310, 340, 76, "NEW ≠ LIVE → set it to NEW\nNEW = LIVE → left out of the patch", "green", size=11)
    d.box("r3", 740, 310, 340, 76, "Only in LIVE → left alone\nsidecars, hand-added annotations", "gray", size=11)
    d.edge("qdel", "r1")
    d.edge("qset", "r2")
    d.edge("qset", "r3", dashed=True)
    d.text("cap", 20, 400, 1060, 50,
           "\"Strategic\": built-in lists merge by key (containers and env by name), so kubectl set env survives.\n"
           "Custom resources have no merge keys: Helm uses a 2-way merge (OLD vs NEW), so a hand edit survives unless the chart changed it.",
           size=11)
    return d


def block_deletion():
    d = Diagram("02-block-deletion", 1100, 400, "Tested surprise: deletion works on whole blocks")
    for gx, title, gc, old, new, live, res, rc in [
        (20, "Chart drops its ONLY pod annotation", "red",
         "OLD\nowner", "NEW\n(no annotations\nblock at all)", "LIVE\nowner, restartedAt",
         "Patch deletes the WHOLE block\nrestartedAt lost + a new rollout", "red"),
        (560, "Chart keeps another annotation (tier: web)", "green",
         "OLD\nowner, tier", "NEW\ntier", "LIVE\nowner, tier,\nrestartedAt",
         "Patch deletes only owner\nrestartedAt kept", "green"),
    ]:
        p = f"g{gx}"
        d.group(p, gx, 45, 520, 280, title, gc, size=12)
        d.box(p + "o", gx + 20, 90, 150, 80, old, "gray", size=11)
        d.box(p + "n", gx + 185, 90, 150, 80, new, "blue", size=11)
        d.box(p + "l", gx + 350, 90, 150, 80, live, "white", size=11)
        d.box(p + "r", gx + 20, 230, 480, 70, res, rc, size=12)
        for k in "onl":
            d.edge(p + k, p + "r")
    d.text("cap", 20, 340, 1060, 50,
           "The 3-way merge deletes at the level where OLD and NEW differ.\n"
           "Server-side apply kept restartedAt in both cases: it has its own owner (kubectl-rollout).", size=11)
    return d


def csa_or_ssa():
    d = Diagram("03-csa-or-ssa", 1000, 380, "How Helm 4 picks server-side or client-side apply")
    d.box("inst", 20, 60, 200, 60, "helm install", "blue", size=12)
    d.box("upg", 20, 210, 200, 60, "helm upgrade\nhelm rollback", "blue", size=12)
    d.box("auto", 280, 195, 300, 90, "--server-side=auto (default)\nreads apply_method from the\nprevious release Secret", "yellow", size=11)
    d.box("ssa", 680, 50, 300, 80, "SSA: the API server merges\nchecks field owners → conflicts", "green", size=11)
    d.box("csa", 680, 230, 300, 80, "CSA: Helm's 3-way merge\nhand edits silently overwritten", "orange", size=11)
    d.edge("inst", "ssa", "default true")
    d.edge("upg", "auto")
    d.edge("auto", "ssa", "ssa")
    d.edge("auto", "csa", "csa")
    d.edge("csa", "ssa", "one upgrade with\n--server-side=true", dashed=True)
    d.text("cap", 20, 325, 960, 40,
           "Releases created by Helm 3 stored csa, so they keep the 3-way merge after you move to Helm 4 until that one switch.", size=11)
    return d


def hpa_handover():
    d = Diagram("03-hpa-handover", 1100, 400, "Moving replicas from Helm to an HPA (tested)")
    d.text("t1", 20, 42, 600, 24, "Trap: Helm alone owns replicas", size=13, bold=True, align="left")
    d.box("a1", 20, 72, 240, 70, "Helm is the only owner\nof replicas (3)", "gray", size=11)
    d.box("a2", 300, 72, 240, 70, "Chart stops sending replicas\n(autoscaling.enabled=true)", "blue", size=11)
    d.box("a3", 580, 72, 240, 70, "Rule 4: only owner stopped\n→ field deleted → 1 replica", "red", size=11)
    d.box("a4", 860, 72, 220, 70, "~15 s later the HPA\nscales to minReplicas 4", "yellow", size=11)
    d.edge("a1", "a2")
    d.edge("a2", "a3")
    d.edge("a3", "a4")
    d.text("t2", 20, 172, 600, 24, "Safe order: hand the field over first", size=13, bold=True, align="left")
    d.box("b1", 20, 202, 240, 70, "HPA scales first\n→ now owns replicas", "gray", size=11)
    d.box("b2", 300, 202, 240, 70, "Chart stops sending replicas", "blue", size=11)
    d.box("b3", 580, 202, 500, 70, "The field still has an owner (the HPA)\nnothing drops", "green", size=11)
    d.edge("b1", "b2")
    d.edge("b2", "b3")
    d.text("cap", 20, 300, 1060, 80,
           "Adopting an HPA made with kubectl autoscale:\n"
           "--take-ownership passes Helm's own label check (invalid ownership metadata)\n"
           "--force-conflicts takes the fields kubectl-autoscale owns.  You may need both.", size=11)
    return d


def values_flags():
    d = Diagram("05-values-flags", 1100, 400, "--reuse-values vs --reset-values vs --reset-then-reuse-values")
    cols = [
        (20, "--reuse-values", [("Your -f / --set", "orange", False), ("Last release's values", "yellow", False),
                               ("New chart defaults: IGNORED", "white", True)],
         "New defaults in a newer chart\nare missing (the classic bug)", "red"),
        (390, "--reset-values", [("Your -f / --set", "orange", False), ("Last release's values: DROPPED", "white", True),
                                ("New chart's values.yaml", "gray", False)],
         "Clean, but settings passed only\nin the last release are lost", "yellow"),
        (760, "--reset-then-reuse-values", [("Your -f / --set", "orange", False), ("Last release's values", "yellow", False),
                                           ("New chart's values.yaml", "gray", False)],
         "New defaults + kept settings\nfixes the --reuse-values gotcha", "green"),
    ]
    for x, title, layers, res, rc in cols:
        d.text(f"t{x}", x, 45, 320, 24, title, size=13, bold=True)
        for i, (label, c, dash) in enumerate(layers):
            d.box(f"l{x}{i}", x, 80 + i * 56, 320, 48, label, c, size=11, dashed=dash)
        d.box(f"r{x}", x, 270, 320, 64, res, rc, size=11)
        d.edge(f"l{x}2", f"r{x}")
    d.text("cap", 20, 350, 1060, 40,
           "Top layer wins.  Safest in CI: pass full values files every time, so none of these flags matter.", size=11)
    return d


def debug_order():
    d = Diagram("06-debug-order", 1100, 290, "Debugging a Helm release, in order")
    steps = [
        ("1 · What does Helm think?\nhelm status\nhelm history\n(failed revision = the error)", "purple"),
        ("2 · What did Helm apply?\nhelm get manifest\nget values --all\nget hooks", "blue"),
        ("3 · What's in the cluster?\nhelm get manifest |\nkubectl diff -n shop -f -", "yellow"),
        ("4 · Who changed it?\n--show-managed-fields\n+ EKS audit logs\n(the person)", "orange"),
        ("5 · Helm or Kubernetes?\ndeployed but broken\n= debug the pods", "green"),
    ]
    for i, (label, c) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 215, 55, 195, 110, label, c, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.box("w1", 20, 200, 520, 64, "deployed ≠ healthy\nwithout --wait Helm waits for hooks only, not pods", "red", size=11)
    d.box("w2", 560, 200, 520, 64, "pending-* = a killed run (\"another operation in progress\")\nhelm rollback to the last deployed revision", "orange", size=11)
    return d


ALL = [helm_flow, helm_versions, upgrade_lifecycle, release_states, values_order, release_secret,
       three_way_rules, block_deletion, csa_or_ssa, hpa_handover, values_flags, debug_order]

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
