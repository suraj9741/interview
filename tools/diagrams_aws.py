#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/aws/*.md.

Run once:  python3 tools/diagrams_aws.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "aws" / "diagrams"


def iam_big_picture():
    d = Diagram("iam-01-big-picture", 960, 600, "IAM in one picture: WHO (identities) gets WHAT (policies)")
    d.group("acct", 20, 44, 920, 540, "One AWS account · IAM is GLOBAL (no region to pick)", "gray", align="left")
    d.box("root", 40, 84, 270, 92,
          "Root user\nemail + password used to create the account\nall power, cannot be limited by IAM\n"
          "MFA on, NO access keys, lock it away", "red", size=11)
    d.box("why", 330, 84, 590, 92,
          "IAM = Identity and Access Management\nAuthentication: who are you? (password + MFA, or access keys)\n"
          "Authorization: what may you do? (policies; everything is DENIED by default)\n"
          "Free service · least privilege: give only the permissions a job needs", "white", size=11, align="left")
    d.text("h-id", 40, 192, 520, 24, "IDENTITIES (principals)", size=13, bold=True)
    d.group("g-dev", 40, 220, 250, 150, "Group: Developers", "green", dashed=True, size=12)
    d.box("u-alice", 60, 252, 100, 40, "User: alice", "white", size=11)
    d.box("u-bob", 172, 252, 100, 40, "User: bob", "white", size=11)
    d.text("g-note", 50, 300, 230, 64, "users only, no nested groups\na user can be in many groups\n(max 10)", size=10)
    d.group("g-ops", 310, 220, 250, 150, "Group: Operations", "green", dashed=True, size=12)
    d.box("u-bob2", 330, 252, 100, 40, "User: bob", "white", size=11)
    d.box("u-carl", 442, 252, 100, 40, "User: carl", "white", size=11)
    d.text("g-note2", 320, 300, 230, 64, "bob is in BOTH groups:\nhe gets the union of both\ngroups' permissions", size=10)
    d.box("u-dave", 40, 392, 250, 56, "User: dave (in no group)\nallowed, but not best practice", "white", size=11)
    d.box("role", 310, 392, 250, 56, "Role: ec2-s3-read\nassumed by EC2 / Lambda / another account", "purple", size=11)
    d.text("h-pol", 600, 192, 320, 24, "POLICIES (JSON permission documents)", size=13, bold=True)
    d.box("p-aws", 600, 222, 320, 52, "AWS managed policy\ne.g. AdministratorAccess, ReadOnlyAccess", "blue", size=11)
    d.box("p-cust", 600, 286, 320, 52, "Customer managed policy\nyou write it, reuse it on many identities", "blue", size=11)
    d.box("p-inline", 600, 350, 320, 52, "Inline policy\nembedded in ONE user/group/role, deleted with it", "yellow", size=11)
    d.box("p-res", 600, 414, 320, 52, "Resource-based policy (has \"Principal\")\non the resource: S3 bucket policy, role trust policy", "orange", size=11)
    d.edge("p-aws", "g-dev", "attach", points=[(580, 248), (580, 184), (165, 184)])
    d.edge("p-cust", "role", "attach", points=[(580, 312), (580, 420)])
    d.box("rule", 40, 474, 880, 94,
          "How permissions add up\nEffective permissions = user's own policies + every group's policies (union).\n"
          "No policy that allows it = implicit DENY.   Any policy that says \"Effect\": \"Deny\" = explicit DENY, and it ALWAYS wins.\n"
          "Best practice: attach policies to GROUPS (not users), give each person their own user, use ROLES for AWS services.",
          "yellow", size=11, align="left")
    return d


def policy_anatomy():
    d = Diagram("iam-02-policy-anatomy", 960, 640, "Anatomy of an IAM policy (JSON)")
    json_lines = [
        "{",
        "  \"Version\": \"2012-10-17\",",
        "  \"Id\": \"S3ReadOnlyPolicy\",",
        "  \"Statement\": [",
        "    {",
        "      \"Sid\": \"ReadReports\",",
        "      \"Effect\": \"Allow\",",
        "      \"Action\": [",
        "        \"s3:GetObject\",",
        "        \"s3:ListBucket\"",
        "      ],",
        "      \"Resource\": [",
        "        \"arn:aws:s3:::reports\",",
        "        \"arn:aws:s3:::reports/*\"",
        "      ],",
        "      \"Condition\": {",
        "        \"IpAddress\": {",
        "          \"aws:SourceIp\": \"203.0.113.0/24\"",
        "        }",
        "      }",
        "    }",
        "  ]",
        "}",
    ]
    # non-breaking spaces keep the indentation (SVG collapses normal spaces)
    body = "\n".join(line.replace("  ", "\u00a0\u00a0") for line in json_lines)
    d.box("json", 20, 50, 360, 520, body, "white", size=12, align="left", bold_first=False)
    rows = [
        ("Version", "policy language version · always \"2012-10-17\"\n(a fixed string, NOT today's date)", "gray"),
        ("Id (optional)", "a name for the whole policy", "gray"),
        ("Statement", "list of one or more statements (required)", "blue"),
        ("Sid (optional)", "a label for one statement", "gray"),
        ("Effect", "Allow or Deny", "green"),
        ("Principal", "WHO · only in resource-based policies (bucket\npolicy, trust policy); never in a policy attached\nto a user, group or role", "orange"),
        ("Action", "WHAT API calls: service:Operation\nwildcards are fine (s3:Get*, s3:*)", "blue"),
        ("Resource", "ON WHAT: ARNs · bucket ARN (reports) is not\nthe object ARN (reports/*)", "blue"),
        ("Condition", "WHEN (optional): source IP, region, MFA present,\ntags, time …", "purple"),
    ]
    y = 50
    for i, (k, v, c) in enumerate(rows):
        n = v.count("\n") + 1
        h = {1: 44, 2: 56, 3: 70}[n]
        d.box(f"k{i}", 400, y, 140, h, k, c, size=12, bold=True)
        d.box(f"v{i}", 546, y, 394, h, v, "white", size=11, align="left", bold_first=False)
        y += h + 6
    d.text("tip", 20, 586, 920, 40, "Memory hook: E-P-A-R-C = Effect, Principal, Action, Resource, Condition", size=14, bold=True)
    return d


def policy_evaluation():
    d = Diagram("iam-03-policy-evaluation", 960, 560, "Allowed or denied? How AWS decides every API call (one account)")
    d.box("req", 360, 46, 240, 50, "Request arrives\nprincipal + action + resource", "gray", size=11)
    d.box("start", 360, 120, 240, 44, "Start: DENY by default", "red", size=12, bold=True)
    d.box("q1", 340, 192, 280, 60, "Is there an explicit \"Deny\" in\nANY applicable policy?", "yellow", size=11)
    d.box("d1", 700, 192, 230, 60, "DENIED (explicit deny)\nnothing can override it", "red", size=11)
    d.box("q2", 340, 290, 280, 60, "Is there an \"Allow\" in an identity\nOR resource-based policy?", "yellow", size=11)
    d.box("d2", 30, 290, 230, 60, "DENIED (implicit deny)\nnobody said Allow", "red", size=11)
    d.box("q3", 340, 388, 280, 60, "SCP, permissions boundary, session\npolicy also allow it? (if any exist)", "yellow", size=11)
    d.box("d3", 700, 388, 230, 60, "DENIED\nthese only LIMIT, never grant", "red", size=11)
    d.box("ok", 380, 478, 200, 50, "ALLOWED", "green", size=14, bold=True)
    d.edge("req", "start")
    d.edge("start", "q1")
    d.edge("q1", "d1", "yes")
    d.edge("q1", "q2", "no")
    d.edge("q2", "d2", "no")
    d.edge("q2", "q3", "yes")
    d.edge("q3", "d3", "no")
    d.edge("q3", "ok", "yes")
    d.box("n1", 30, 388, 290, 140,
          "Exam one-liners\nExplicit DENY > explicit ALLOW > implicit deny.\n"
          "Root user ignores IAM policies\n(but not SCPs in an Organization).\n"
          "Cross-account: BOTH sides must allow\n(identity policy in your account AND\nresource policy in theirs).",
          "white", size=10, align="left")
    d.box("n2", 30, 60, 290, 110,
          "Example\nGroup Developers: Allow s3:*\nalice's inline policy: Deny s3:DeleteBucket\n"
          "→ alice can do everything in S3\n   EXCEPT delete buckets.", "white", size=10, align="left")
    return d


def access_methods():
    d = Diagram("iam-04-access-methods", 960, 520, "Three ways to talk to AWS, and which credentials each one uses")
    d.box("you", 20, 200, 150, 70, "You\n(IAM user)", "gray", shape="ellipse", size=12)
    d.box("console", 230, 60, 300, 100,
          "1. AWS Management Console\nbrowser · sign in with\naccount ID/alias + username + password\n+ MFA code", "blue", size=11)
    d.box("cli", 230, 186, 300, 100,
          "2. AWS CLI (terminal) / SDK (code)\nAccess key ID (AKIA…) + Secret access key\nset with: aws configure\nstored in ~/.aws/credentials", "green", size=11)
    d.box("shell", 230, 312, 300, 100,
          "3. AWS CloudShell\nterminal INSIDE the console (>_ icon)\nuses your console login, NO keys needed\nCLI v2 pre-installed, 1 GB $HOME per region", "purple", size=11)
    d.box("api", 620, 186, 140, 100, "AWS APIs\n(HTTPS)\nevery click and\nevery command\nis an API call", "orange", size=11)
    d.box("iam", 800, 186, 140, 100, "IAM checks\nwho? (authN)\nallowed? (authZ)", "red", size=11)
    d.edge("you", "console")
    d.edge("you", "cli")
    d.edge("you", "shell")
    d.edge("console", "api")
    d.edge("cli", "api")
    d.edge("shell", "api")
    d.edge("api", "iam")
    d.box("n", 20, 432, 920, 72,
          "Access keys = a password for the CLI. The secret is shown ONCE at creation; max 2 keys per user (so you can rotate).\n"
          "Never share them, never commit them to Git, never put them on EC2 (use a role). If leaked: deactivate → create new → delete old.\n"
          "CloudShell and EC2 roles give TEMPORARY credentials instead (key IDs start with ASIA, plus a session token).",
          "yellow", size=11, align="left", bold_first=False)
    return d


def role_assume():
    d = Diagram("iam-05-role-assume", 960, 620, "IAM role: temporary permissions for an AWS service (EC2 → S3 example)")
    d.box("ec2", 20, 90, 200, 90, "EC2 instance\napp runs: aws s3 ls\n(no keys on disk!)", "orange", size=11)
    d.box("prof", 20, 220, 200, 70, "Instance profile\ncontainer that attaches\nthe role to EC2", "gray", size=11)
    d.box("imds", 20, 330, 200, 80, "Instance metadata (IMDS)\n169.254.169.254\nSDK/CLI read creds here", "gray", size=10)
    d.group("rolebox", 290, 60, 360, 350, "Role: ec2-s3-read", "purple")
    d.box("trust", 310, 96, 320, 130,
          "Trust policy (WHO may assume)\n\"Effect\": \"Allow\",\n\"Principal\": {\"Service\": \"ec2.amazonaws.com\"},\n"
          "\"Action\": \"sts:AssumeRole\"\n\nresource-based policy on the role", "white", size=10, align="left")
    d.box("perm", 310, 244, 320, 150,
          "Permissions policy (WHAT it may do)\n\"Effect\": \"Allow\",\n\"Action\": [\"s3:GetObject\", \"s3:ListBucket\"],\n"
          "\"Resource\": \"arn:aws:s3:::reports*\"\n\ne.g. AmazonS3ReadOnlyAccess\n(identity-based, managed or inline)", "white", size=10, align="left")
    d.box("sts", 720, 90, 220, 110, "AWS STS\n(Security Token Service)\nsts:AssumeRole returns\ntemporary credentials", "blue", size=11)
    d.box("creds", 720, 230, 220, 120, "Temporary credentials\nAccessKeyId (ASIA…)\nSecretAccessKey\nSessionToken\nexpire (15 min – 12 h;\nEC2 rotates them for you)", "green", size=10)
    d.box("s3", 720, 380, 220, 60, "S3 bucket: reports\nrequest allowed", "orange", size=11)
    d.edge("ec2", "prof", "has")
    d.edge("prof", "rolebox", "points to")
    d.edge("rolebox", "sts", "AssumeRole")
    d.edge("sts", "creds")
    d.edge("creds", "imds", "delivered to the instance", points=[(690, 330), (690, 436), (120, 436)])
    d.edge("imds", "ec2", points=[(8, 370), (8, 135)])
    d.edge("creds", "s3", "sign request")
    d.box("n", 20, 470, 920, 130,
          "User vs role\nUser = one person, long-term credentials (password / access keys).   Role = no long-term credentials, anyone TRUSTED can wear it for a while.\n"
          "Common roles: EC2 instance role · Lambda execution role · ECS task role · cross-account access · federation / SSO (IAM Identity Center).\n"
          "To attach a role to EC2 you need iam:PassRole.  A role has TWO policies: trust (who) + permissions (what).\n"
          "Trap: a role does NOT need access keys, and you never store keys on an instance; you can swap the role on a running instance.",
          "yellow", size=11, align="left")
    return d


def mfa_password():
    d = Diagram("iam-06-mfa-password", 960, 470, "Protecting sign-in: password policy + MFA")
    d.box("pw", 20, 50, 440, 260,
          "Password policy (account settings, for IAM users)\n"
          "• minimum length (default 8, can set 6–128)\n"
          "• require uppercase / lowercase / numbers /\n   non-alphanumeric characters (! @ # …)\n"
          "• allow users to change their own password\n"
          "• password expiry (e.g. every 90 days)\n"
          "• prevent password re-use (remember last 1–24)\n"
          "• require admin reset after expiry\n"
          "Does NOT apply to the root user or to access keys", "blue", size=11, align="left")
    d.box("eq", 480, 50, 460, 70, "MFA = something you KNOW (password)\n+ something you HAVE (a device)", "green", size=13)
    d.box("m1", 480, 136, 148, 120, "Virtual MFA\nphone app:\nGoogle Authenticator,\nAuthy, Microsoft\nAuthenticator", "white", size=10)
    d.box("m2", 636, 136, 148, 120, "FIDO2 security key\n/ passkey\nYubiKey, Touch ID,\nWindows Hello\n(phishing-resistant)", "white", size=10)
    d.box("m3", 792, 136, 148, 120, "Hardware TOTP\ntoken\nkey-fob that shows\na 6-digit code\n(third-party, e.g. Thales)", "white", size=10)
    d.box("why", 480, 270, 460, 40, "Password stolen? Attacker still needs your device.", "yellow", size=11)
    d.box("n", 20, 330, 920, 120,
          "Remember for the exam\nTurn on MFA for the ROOT user first, then for every IAM user. Up to 8 MFA devices per user (any mix).\n"
          "MFA protects console sign-in. For the CLI, use sts get-session-token with --serial-number and --token-code, and require it in policies\n"
          "with the condition \"aws:MultiFactorAuthPresent\": \"true\".  S3 MFA Delete can be enabled only by the root user.\n"
          "Lost MFA device: an admin removes (deactivates) it from the user, then the user registers a new one.",
          "yellow", size=11, align="left")
    return d


def security_tools():
    d = Diagram("iam-07-security-tools", 960, 470, "IAM security tools: credential report vs access advisor")
    d.box("cr", 20, 50, 450, 270,
          "IAM Credential Report  (ACCOUNT level)\n"
          "One CSV listing EVERY user in the account and the\nstatus of their credentials:\n"
          "• password enabled? last used? last changed?\n"
          "• MFA active?\n"
          "• access key 1 / 2 active? last rotated? last used?\n"
          "Use it to find: users without MFA, old keys (>90 days),\nunused passwords / keys → audits, compliance\n"
          "Console: IAM → Credential report → Download\n"
          "New report at most every 4 hours", "blue", size=11, align="left")
    d.box("aa", 490, 50, 450, 270,
          "IAM Access Advisor  (USER level)\n"
          "Tab on a user, group, role or policy:\n"
          "• which SERVICES its policies allow\n"
          "• when each service was LAST ACCESSED\n"
          "Use it to find permissions that are never used,\nthen remove them → least privilege\n"
          "Console: IAM → Users → <user> → Last accessed\n"
          "(this tab is what the course calls Access Advisor)\n"
          "History shown for up to 400 days", "green", size=11, align="left")
    d.box("hook", 20, 336, 920, 50,
          "Hook: Credential report = Census of the whole Country (account).   Access Advisor = Audit of one person (user).",
          "yellow", size=12, bold=True)
    d.box("aan", 20, 400, 920, 52,
          "Don't confuse with IAM Access ANALYZER: finds resources shared OUTSIDE your account (public S3 bucket, cross-account role),\n"
          "unused access, and can validate or generate policies from CloudTrail activity.",
          "orange", size=11, align="left", bold_first=False)
    return d


def shared_responsibility():
    d = Diagram("iam-08-shared-responsibility", 960, 400, "Shared responsibility model, applied to IAM")
    d.box("aws", 20, 50, 450, 230,
          "AWS is responsible for (security OF the cloud)\n"
          "• the infrastructure: global network security\n"
          "• the IAM service itself running and secure\n"
          "• configuration and vulnerability analysis\n   of its own systems\n"
          "• compliance validation (audits, certifications)",
          "orange", size=12, align="left")
    d.box("you", 490, 50, 450, 230,
          "YOU are responsible for (security IN the cloud)\n"
          "• users, groups, roles, policies: create, manage, monitor\n"
          "• enable and enforce MFA on all accounts\n"
          "• rotate access keys often\n"
          "• use IAM tools to apply the right permissions\n"
          "• analyse access patterns and review permissions\n   (credential report, access advisor, CloudTrail)",
          "blue", size=12, align="left")
    d.box("n", 20, 296, 920, 84,
          "If your access key leaks on GitHub, or a user has AdministratorAccess they don't need, that is YOUR fault, not AWS's.\n"
          "Exam phrase: \"who is responsible for managing IAM users and MFA?\" → the customer.",
          "yellow", size=12, align="left", bold_first=False)
    return d


ALL = [iam_big_picture, policy_anatomy, policy_evaluation, access_methods, role_assume, mfa_password,
       security_tools, shared_responsibility]

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
