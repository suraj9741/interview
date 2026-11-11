#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/terraform/*.md.

Run once:  python3 tools/diagrams_terraform.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "terraform" / "diagrams"


def three_worlds():
    d = Diagram("00-three-worlds", 1100, 470, "Terraform compares three things: code, state and the real cloud")
    d.box("code", 30, 70, 300, 110, "1 · Configuration (.tf in Git)\nwhat you WANT\nresource \"aws_s3_bucket\" \"logs\" {…}", "blue", size=11)
    d.box("state", 400, 70, 300, 110, "2 · State (terraform.tfstate)\nwhat Terraform THINKS exists\naddress → real ID + attributes", "orange", size=11)
    d.box("real", 770, 70, 300, 110, "3 · Real infrastructure\nwhat REALLY exists\nAWS API: S3, EKS, RDS, IAM…", "green", size=11)
    d.edge("code", "state", "plan compares")
    d.edge("real", "state", "refresh reads")
    d.box("c1", 30, 240, 250, 90, "terraform import / import {}\nreal object → state\n(adopt, nothing created)", "purple", size=11)
    d.box("c2", 300, 240, 250, 90, "-replace (old: taint)\nforce destroy + create\nof one object", "red", size=11)
    d.box("c3", 570, 240, 250, 90, "plan / apply -refresh-only\nreal → state\n(drift, no infra change)", "yellow", size=11)
    d.box("c4", 840, 240, 230, 90, "plan → apply\nchange real infra\nto match the code", "white", size=11)
    d.text("cap", 20, 360, 1060, 90,
           "Every question in these notes is about one of these arrows.\n"
           "Drift = real ≠ state.  Pending change = code ≠ state.  Import = real object not yet in state.\n"
           "The state file is the heart: protect it (remote backend + lock + encryption + versioning).", size=12)
    return d


def import_vs_taint():
    d = Diagram("01-import-vs-taint", 1100, 500, "import brings an object IN; taint / -replace REBUILDS an object already in")
    d.group("gi", 20, 50, 520, 330, "terraform import: adopt something that already exists", "purple")
    d.box("i1", 50, 100, 200, 70, "EC2 / S3 / IAM role\ncreated by hand in console\n(not in state)", "green", size=11)
    d.box("i2", 300, 100, 210, 70, "import {\n  to = aws_s3_bucket.logs\n  id = \"acme-prod-logs\" }", "white", size=11, align="left")
    d.box("i3", 50, 230, 200, 70, "state now has it\nnothing created\nnothing destroyed", "orange", size=11)
    d.box("i4", 300, 230, 210, 70, "write / generate the HCL\nplan must say\n0 to add, 0 to change", "blue", size=11)
    d.edge("i1", "i3", "read by ID")
    d.edge("i2", "i3")
    d.edge("i3", "i4")
    d.group("gt", 560, 50, 520, 330, "terraform taint (deprecated) → apply -replace", "red")
    d.box("t1", 590, 100, 200, 70, "EC2 already in state\nbut broken / bad boot\n(config unchanged)", "orange", size=11)
    d.box("t2", 840, 100, 210, 70, "terraform apply\n-replace=\"aws_instance.web\"", "white", size=11)
    d.box("t3", 590, 230, 200, 70, "plan: will be replaced,\nas requested\n1 to add, 1 to destroy", "yellow", size=11)
    d.box("t4", 840, 230, 210, 70, "old destroyed, new created\n(new ID, new IP,\nunless create_before_destroy)", "red", size=11)
    d.edge("t1", "t3")
    d.edge("t2", "t3")
    d.edge("t3", "t4")
    d.text("cap", 20, 400, 1060, 80,
           "import = add to state, no infra change.  taint = mark in state, rebuild on the NEXT apply (hidden, affects everyone).\n"
           "-replace = rebuild in THIS plan only, shown in the plan, state untouched until apply.  "
           "taint deprecated since v0.15.2; still works in 1.13.", size=11)
    return d


def secrets():
    d = Diagram("02-secrets-flow", 1100, 520, "Secrets: where they come from, and where they can leak")
    d.box("sm", 20, 70, 230, 80, "AWS Secrets Manager / SSM\nHashiCorp Vault\nSOPS-encrypted file", "green", size=11)
    d.box("ci", 20, 190, 230, 80, "GitLab CI masked +\nprotected variable\n→ TF_VAR_db_password", "blue", size=11)
    d.box("oidc", 20, 310, 230, 80, "GitLab OIDC id_token\n→ AssumeRoleWithWebIdentity\n(no static AWS keys)", "purple", size=11)
    d.box("tf", 330, 170, 260, 120, "terraform plan / apply\nvariable { sensitive = true }\nephemeral = true (1.10+)\ndata / ephemeral blocks", "yellow", size=11)
    d.edge("sm", "tf", "read at run time")
    d.edge("ci", "tf")
    d.edge("oidc", "tf", "AWS creds")
    d.box("out", 680, 60, 400, 70, "CLI output / plan: shows (sensitive value)\nsensitive = true hides it HERE only", "white", size=11)
    d.box("state", 680, 170, 400, 90, "State file: value stored in PLAIN TEXT\neven when sensitive = true (tested)\n→ S3 SSE-KMS + tight IAM + versioning", "red", size=11)
    d.box("eph", 680, 300, 400, 90, "Never stored: ephemeral values,\nwrite-only args (password_wo, 1.11+),\nRDS manage_master_user_password = true", "green", size=11)
    d.edge("tf", "out")
    d.edge("tf", "state")
    d.edge("tf", "eph")
    d.text("cap", 20, 420, 1060, 80,
           "Never: secrets in .tf, in committed .tfvars, or as plain outputs.  Leak points: Git, CI logs, plan files, state.\n"
           "Best: Terraform never sees the secret at all (AWS generates it in Secrets Manager); next best: ephemeral / write-only.", size=11)
    return d


def count_vs_foreach():
    d = Diagram("03-count-vs-for-each", 1100, 520, "Remove \"bob\" from the list: count shifts, for_each doesn't (tested)")
    d.group("gc", 20, 50, 520, 340, "count = length(var.names)  → keyed by POSITION", "orange")
    for i, (n, after, col) in enumerate([("alice", "alice  (no change)", "white"), ("bob", "carol  ~ update in place!", "yellow"),
                                         ("carol", "destroyed (index 2 out of range)", "red")]):
        d.box(f"cb{i}", 40, 100 + i * 90, 170, 60, f"[{i}] = \"{n}\"", "gray", size=12)
        d.box(f"ca{i}", 270, 100 + i * 90, 250, 60, f"[{i}] → {after}", col, size=11)
        d.edge(f"cb{i}", f"ca{i}")
    d.group("gf", 560, 50, 520, 340, "for_each = toset(var.names)  → keyed by NAME", "green")
    for i, (n, after, col) in enumerate([("alice", "no change", "white"), ("bob", "destroyed (key not in map)", "red"),
                                         ("carol", "no change", "white")]):
        d.box(f"fb{i}", 580, 100 + i * 90, 170, 60, f"[\"{n}\"]", "gray", size=12)
        d.box(f"fa{i}", 810, 100 + i * 90, 250, 60, f"[\"{n}\"] → {after}", col, size=11)
        d.edge(f"fb{i}", f"fa{i}")
    d.text("cap", 20, 405, 1060, 100,
           "count: [1] changes bob → carol, [2] is destroyed (for a real aws_iam_user the name change = destroy + create).   for_each: only bob goes.\n"
           "count: N identical copies or on/off switch (count = var.enabled ? 1 : 0).\n"
           "for_each: a set/map of DIFFERENT things (IAM users, subnets per AZ, EKS node groups). Migrate with moved {} blocks.", size=11)
    return d


def drift():
    d = Diagram("04-drift-loop", 1100, 500, "Drift detection: a scheduled plan that fails loudly")
    d.box("hand", 20, 70, 220, 90, "Someone changes AWS\nconsole hotfix, script,\nautoscaler, AWS itself", "red", size=11)
    d.box("sched", 300, 70, 240, 90, "GitLab scheduled pipeline\n(e.g. every morning)\nterraform plan\n-detailed-exitcode", "blue", size=11)
    d.box("code", 580, 40, 200, 60, "exit 0 = no changes", "green", size=11)
    d.box("code2", 580, 115, 200, 60, "exit 2 = drift / changes", "orange", size=11)
    d.box("code1", 580, 190, 200, 60, "exit 1 = error", "gray", size=11)
    d.box("alert", 815, 100, 210, 90, "Alert: Slack / MR /\nissue with plan output\n(-refresh-only shows\nwhat changed)", "yellow", size=11)
    d.edge("hand", "sched", "real ≠ state")
    d.edge("sched", "code")
    d.edge("sched", "code2")
    d.edge("sched", "code1")
    d.edge("code2", "alert")
    d.box("keep", 120, 300, 400, 90, "Change is WANTED → keep it\nupdate the .tf code to match\n(apply -refresh-only accepts it into state)", "green", size=11)
    d.box("revert", 760, 300, 320, 90, "Change is NOT wanted → revert it\nterraform apply (code wins)\nthen find who did it (CloudTrail)", "red", size=11)
    d.edge("alert", "keep", "decide", points=[(880, 265), (320, 265)])
    d.edge("alert", "revert", "decide")
    d.text("cap", 20, 410, 1060, 70,
           "Prevent: read-only console roles / SCPs, all changes via MR + pipeline, ignore_changes only for fields\n"
           "owned by something else (EKS node group desired_size owned by Cluster Autoscaler).  "
           "plan can't see resources that were never in state.", size=11)
    return d


def remote_backend():
    d = Diagram("05-remote-backend", 1100, 500, "Remote backend: one shared, locked, encrypted, versioned state")
    d.box("dev1", 20, 70, 200, 60, "Suraj's laptop\nterraform plan", "blue", size=11)
    d.box("dev2", 20, 160, 200, 60, "Teammate's laptop\nterraform apply", "blue", size=11)
    d.box("ci", 20, 250, 200, 60, "GitLab CI runner\nplan on MR, apply on main", "purple", size=11)
    d.box("lock", 330, 150, 230, 90, "Lock (one writer at a time)\nS3 use_lockfile = true (1.10+)\nold: DynamoDB table", "yellow", size=11)
    d.box("s3", 650, 60, 420, 120, "S3 bucket: acme-tfstate\nkey = prod/eks/terraform.tfstate\nencrypt = true (SSE-KMS) · versioning on\nblock public access · bucket policy = CI role only", "orange", size=11)
    d.box("lk", 650, 220, 420, 60, "prod/eks/terraform.tfstate.tflock\n(exists only while someone holds the lock)", "white", size=11)
    d.edge("dev1", "lock")
    d.edge("dev2", "lock")
    d.edge("ci", "lock")
    d.edge("lock", "s3", "read / write state", points=[(605, 170), (605, 120)])
    d.edge("lock", "lk", "create / delete", points=[(605, 220), (605, 250)])
    d.box("ro", 650, 310, 420, 60, "Other stacks read outputs:\ndata \"terraform_remote_state\" (or SSM parameters)", "green", size=11)
    d.edge("s3", "ro", points=[(1090, 120), (1090, 340)])
    d.text("cap", 20, 395, 1060, 90,
           "Local state problems: lost laptop = lost state, two applies at once = corrupt state, secrets on disk, no history.\n"
           "Remote: shared truth + locking + encryption + versions to recover from.  "
           "GitLab also offers GitLab-managed Terraform state (http backend).", size=11)
    return d


def environments():
    d = Diagram("06-environments", 1100, 540, "Dev, staging, prod: same modules, separate state, separate accounts")
    d.box("mod", 400, 50, 300, 80, "modules/ (versioned, e.g. git tag v1.4.0)\nvpc · eks · rds", "purple", size=11)
    envs = [("dev", "dev.tfvars-style inputs\nt3.medium, 1 NAT", "green"), ("staging", "copy of prod, smaller\nsame module version first", "yellow"),
            ("prod", "m6i.xlarge, 3 NAT,\nmanual apply in CI", "red")]
    for i, (e, txt, c) in enumerate(envs):
        x = 40 + i * 360
        d.box(f"e{i}", x, 190, 300, 80, f"envs/{e}/main.tf + backend\n{txt}", c, size=11)
        d.box(f"s{i}", x, 310, 300, 60, f"state: s3://acme-tfstate/{e}/…\nAWS account: acme-{e}", "orange", size=11)
        d.edge("mod", f"e{i}")
        d.edge(f"e{i}", f"s{i}")
    d.text("cap", 20, 390, 1060, 130,
           "Option A (recommended): a directory per environment calling shared modules → different code version per env is possible,\n"
           "a broken dev plan can never touch prod, each env has its own backend + IAM role.\n"
           "Option B: workspaces (terraform workspace new prod) → one code path, state per workspace (env:/prod/… in S3);\n"
           "easy to apply to the wrong workspace, same backend credentials for all. Fine for short-lived copies (feature envs).\n"
           "Option C: Terragrunt to keep backend / provider blocks DRY across many envs and accounts.", size=11, align="left")
    return d


def provisioners():
    d = Diagram("07-provisioners", 1100, 480, "local-exec runs where Terraform runs; remote-exec runs on the new machine")
    d.box("runner", 30, 90, 280, 110, "Machine running Terraform\n(laptop / GitLab runner)\nlocal-exec: command = \"aws eks\nupdate-kubeconfig …\"", "blue", size=11)
    d.box("aws", 400, 90, 260, 110, "AWS API\ncreates aws_instance.web\n(public IP / private IP)", "green", size=11)
    d.box("vm", 760, 90, 310, 110, "The new EC2 instance\nremote-exec: inline = [\n\"sudo apt-get install -y nginx\" ]\nneeds connection { ssh / winrm }", "orange", size=11)
    d.edge("runner", "aws", "1 · create")
    d.edge("runner", "vm", "2 · SSH (port 22 must be open)", points=[(170, 240), (915, 240)])
    d.box("fail", 30, 290, 500, 80, "If a creation-time provisioner fails, the resource is\nmarked TAINTED → destroyed + recreated on the next apply\n(on_failure = continue to ignore)", "red", size=11)
    d.box("alt", 560, 290, 510, 80, "Last resort (HashiCorp docs). Prefer: user_data / cloud-init,\nPacker-baked AMIs, Ansible after apply, EKS add-ons / Helm,\nterraform_data + triggers_replace instead of null_resource", "yellow", size=11)
    d.text("cap", 20, 390, 1060, 70,
           "Both run only at CREATE (or at destroy with when = destroy), not on every apply, and Terraform can't plan or\n"
           "track what they did.  Changing the command later does nothing to existing resources.", size=11)
    return d


def rollback():
    d = Diagram("08-rollback", 1100, 520, "There is no terraform rollback: roll FORWARD to the last good code")
    steps = [("1 · Failed apply\nstate = what DID succeed\n(not transactional)", "red"),
             ("2 · Stop the bleeding\nread the error + plan\nterraform force-unlock\nif the run was killed", "orange"),
             ("3 · git revert the MR\n→ last known good code\n(same pipeline)", "blue"),
             ("4 · plan, review, apply\nplan -out=tfplan\napply tfplan", "green"),
             ("5 · Verify + postmortem\nhealth checks, alarms\nwhy didn't plan catch it?", "purple")]
    for i, (label, c) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 215, 60, 195, 110, label, c, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.box("no", 20, 210, 520, 90, "Restoring an OLD state file (S3 version) ≠ rollback\nit changes Terraform's memory, not AWS → next plan is wrong.\nOnly for a corrupted / deleted state.", "red", size=11)
    d.box("cant", 560, 210, 520, 90, "Some changes can't be undone at all:\ndeleted RDS / S3 data, EKS version upgrade (no downgrade),\nKMS key deletion → backups + guards BEFORE the change", "orange", size=11)
    d.box("guard", 20, 330, 1060, 90, "Guards: small states (small blast radius), saved plan files, pinned module/provider versions + .terraform.lock.hcl,\n"
          "lifecycle { prevent_destroy, create_before_destroy }, deletion_protection, final snapshots, S3 versioning,\n"
          "dev → staging → prod promotion, blue/green (new node group / new ASG, then switch traffic)", "green", size=11, align="left")
    d.text("cap", 20, 440, 1060, 60,
           "Interview line: \"I don't roll back the state, I roll forward the code: revert the commit, plan, apply. Data is protected\n"
           "by snapshots and deletion protection, because Terraform can't bring deleted data back.\"", size=11)
    return d


def refresh_vs_plan():
    d = Diagram("09-refresh-vs-plan", 1100, 500, "refresh updates the STATE; plan proposes changes to the INFRA")
    d.group("gr", 20, 50, 520, 320, "terraform refresh (deprecated since v0.15.4)", "yellow")
    d.box("r1", 50, 100, 200, 60, "Read real objects\nfrom AWS", "green", size=11)
    d.box("r2", 300, 100, 210, 60, "OVERWRITE state\nimmediately, no review", "red", size=11)
    d.box("r3", 50, 220, 460, 110, "= terraform apply -refresh-only -auto-approve\nRisk: wrong region / creds → objects look gone\n→ state silently loses them.\nUse: terraform plan -refresh-only (review) then\napply -refresh-only (approve).", "white", size=11)
    d.edge("r1", "r2")
    d.edge("r2", "r3")
    d.group("gp", 560, 50, 520, 320, "terraform plan", "blue")
    d.box("p1", 590, 100, 200, 60, "1 · Refresh in memory\n(state file untouched)", "green", size=11)
    d.box("p2", 840, 100, 210, 60, "2 · Compare code vs\nrefreshed state", "yellow", size=11)
    d.box("p3", 590, 220, 460, 110, "3 · Print the action list: + create, ~ update,\n-/+ replace, - destroy.  Changes NOTHING.\n-out=tfplan saves it for apply.\n-refresh=false skips step 1 (faster, big states).\n-detailed-exitcode: 0 none, 1 error, 2 changes.", "white", size=11)
    d.edge("p1", "p2")
    d.edge("p2", "p3")
    d.text("cap", 20, 390, 1060, 80,
           "refresh answers \"what does the cloud look like now?\" and writes it down.\n"
           "plan answers \"what would apply do?\" and writes nothing.  Since 0.15.4, plan and apply refresh automatically.", size=12)
    return d


def modules():
    d = Diagram("10-module-structure", 1100, 540, "A reusable module: inputs in, resources inside, outputs out")
    d.box("in", 20, 80, 270, 200, "variables.tf (the API)\ntype = object({…})\noptional(…, default) (1.3+)\nvalidation { … }\nsensible defaults\nno hard-coded env / region", "blue", size=11)
    d.box("mid", 330, 60, 440, 240, "modules/eks-nodegroup/\nmain.tf · versions.tf (required_providers,\nno provider block) · locals.tf\nfor_each over var.node_groups\ntags = merge(var.tags, local.default_tags)\nREADME.md (terraform-docs)\nexamples/basic/ · tests/*.tftest.hcl", "purple", size=11)
    d.box("out", 810, 80, 270, 200, "outputs.tf\nIDs / ARNs / names\nthe caller needs\n(node_role_arn,\nsecurity_group_id)\nnot whole objects", "green", size=11)
    d.edge("in", "mid")
    d.edge("mid", "out")
    d.box("c1", 20, 340, 340, 80, "Caller (envs/prod/main.tf)\nsource = \"git::https://gitlab…/\neks-nodegroup.git?ref=v1.4.0\"", "yellow", size=11)
    d.box("c2", 380, 340, 340, 80, "Release: semantic version tags\nv1.4.0 → v1.5.0 (feature) → v2.0.0 (breaking)\nCHANGELOG + moved {} for refactors", "orange", size=11)
    d.box("c3", 740, 340, 340, 80, "CI on the module repo:\nfmt -check · validate · tflint\ntrivy/checkov · terraform test", "white", size=11)
    d.edge("c1", "mid", "pins a version")
    d.text("cap", 20, 440, 1060, 80,
           "Rules: one job per module (not a \"god module\"), callers configure providers, version-pin everything,\n"
           "test with terraform test, document inputs/outputs, and keep modules no more than 1–2 levels deep.", size=11)
    return d


ALL = [three_worlds, import_vs_taint, secrets, count_vs_foreach, drift, remote_backend, environments,
       provisioners, rollback, refresh_vs_plan, modules]

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
