import re, shlex, subprocess, sys
from functools import lru_cache

md = open(sys.argv[1], encoding="utf-8").read()
STOP_AT_POSITIONAL = {("run",), ("create",), ("exec",), ("compose", "run"), ("compose", "exec"),
                      ("container", "run"), ("container", "create"), ("container", "exec")}

@lru_cache(None)
def helpinfo(prefix):
    out = subprocess.run(["docker", *prefix, "--help"], capture_output=True, text=True).stdout
    flags, subs, in_cmds = {}, set(), False
    for line in out.splitlines():
        if re.match(r"^(\S.*)?Commands:\s*$", line):
            in_cmds = True; continue
        if in_cmds:
            m = re.match(r"^\s{2,}([a-z][\w-]*)\*?\s", line)
            if m: subs.add(m.group(1)); continue
            if line.strip() == "" or not line.startswith(" "): in_cmds = False
        m = re.match(r"^\s+(?:-(\w), )?--([\w-]+)(?: (\w+))?\s{2,}", line) or re.match(r"^\s+(?:-(\w), )?--([\w-]+)(?: (\w+))?$", line)
        if m:
            short, long_, typ = m.groups()
            takes = typ is not None
            flags["--" + long_] = takes
            if short: flags["-" + short] = takes
    return out, flags, subs

def check(cmd):
    errs = []
    try:
        toks = shlex.split(cmd)
    except ValueError as e:
        return [f"cannot parse: {e}"]
    assert toks[0] == "docker"
    prefix, i, consumed_pos = (), 1, False
    help_ok = helpinfo(prefix)
    while i < len(toks):
        t = toks[i]
        _, flags, subs = helpinfo(prefix)
        if t.startswith("--"):
            name = t.split("=", 1)[0]
            if name not in flags: errs.append(f"unknown flag {name} for 'docker {' '.join(prefix)}'")
            elif flags[name] and "=" not in t: i += 1
        elif t.startswith("-") and len(t) > 1 and not t[1].isdigit():
            letters = t[1:]
            for j, ch in enumerate(letters):
                f = "-" + ch
                if f not in flags:
                    errs.append(f"unknown flag {f} for 'docker {' '.join(prefix)}'"); break
                if flags[f]:
                    if j == len(letters) - 1: i += 1
                    break
        else:
            if not consumed_pos and t in subs:
                prefix = prefix + (t,)
            else:
                if not consumed_pos and subs:
                    errs.append(f"unknown subcommand {t!r} for 'docker {' '.join(prefix)}'")
                consumed_pos = True
                if prefix in STOP_AT_POSITIONAL: break
        i += 1
    if not prefix:
        errs.append("no subcommand recognised")
    return errs

# collect commands: inline code + fenced bash lines
cands = []
section = ""
for line in md.splitlines():
    if line.startswith("## "): section = line
    for code in re.findall(r"`([^`]+)`", line):
        code = code.replace("\\|", "|")
        if section.startswith("## 4.") and code.startswith("-") and line.strip().startswith("|"):
            code = "docker run " + code + " IMG"
        cands.append(code)
in_bash = False
for line in md.splitlines():
    if line.startswith("```"): in_bash = line.strip() == "```bash"; continue
    if in_bash and line.strip(): cands.append(line.strip())

cmds = []
for c in cands:
    nested = re.findall(r"\$\((docker [^)]*)\)", c)
    outer = re.sub(r"\$\(docker [^)]*\)", "X", c)
    for seg in re.split(r"\|\||&&|\||;", outer) + nested:
        k = seg.find("docker ")
        if k >= 0 and (k == 0 or seg[k-1] in " ("):
            s = seg[k:].strip()
            if s.split()[1:2] and not s.split()[1].startswith("→"):
                cmds.append(s)
seen, bad = set(), 0
for c in cmds:
    if c in seen: continue
    seen.add(c)
    e = check(c)
    if e:
        bad += 1; print("✗", c, "\n   ", "; ".join(e))
print(f"checked {len(seen)} unique docker commands, {bad} with problems")
