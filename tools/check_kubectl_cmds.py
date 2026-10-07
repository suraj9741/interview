#!/usr/bin/env python3
"""Check every `kubectl …` and `helm …` command in Markdown files against the installed CLIs' --help.

Usage:  python3 tools/check_kubectl_cmds.py file.md [file.md …]

Runs kubectl with an EMPTY kubeconfig (KUBECONFIG=/dev/null), so it can never contact a real cluster.
Checks that each subcommand exists and each flag is valid for it. Prints problems and a summary line.
"""
import os
import re
import shlex
import subprocess
import sys
from functools import lru_cache

ENV = dict(os.environ, KUBECONFIG="/dev/null")


@lru_cache(None)
def kubectl_help(prefix):
    out = subprocess.run(["kubectl", *prefix, "--help"], capture_output=True, text=True, env=ENV).stdout
    flags, subs, in_cmds = {}, set(), False
    for line in out.splitlines():
        if re.match(r"^\S.*:\s*$", line) and not re.match(r"^(Usage|Examples|Options|Aliases):", line):
            in_cmds = "Command" in line
            continue
        if in_cmds:
            m = re.match(r"^\s{2}([a-z][\w-]*)\s", line)
            if m:
                subs.add(m.group(1))
                continue
            if line.strip() == "":
                in_cmds = False
        m = re.match(r"^\s+(?:-(\w), )?--([\w-]+)=(.*):\s*$", line)
        if m:
            short, long_, default = m.groups()
            takes = default not in ("true", "false")
            flags["--" + long_] = takes
            if short:
                flags["-" + short] = takes
    return out, flags, subs


@lru_cache(None)
def kubectl_globals():
    out = subprocess.run(["kubectl", "options"], capture_output=True, text=True, env=ENV).stdout
    flags = {}
    for m in re.finditer(r"^\s+(?:-(\w), )?--([\w-]+)=(.*):\s*$", out, re.M):
        short, long_, default = m.groups()
        takes = default not in ("true", "false")
        flags["--" + long_] = takes
        if short:
            flags["-" + short] = takes
    return flags


@lru_cache(None)
def helm_help(prefix):
    out = subprocess.run(["helm", *prefix, "--help"], capture_output=True, text=True).stdout
    flags, subs, in_cmds = {}, set(), False
    for line in out.splitlines():
        if re.match(r"^(\S.*)?Commands:\s*$", line):
            in_cmds = True
            continue
        if in_cmds:
            m = re.match(r"^\s{2,}([a-z][\w-]*)\s", line)
            if m:
                subs.add(m.group(1))
                continue
            if line.strip() == "" or not line.startswith(" "):
                in_cmds = False
        m = re.match(r"^\s+(?:-(\w), )?--([\w-]+)(?: (\w+))?\s{2,}", line)
        if m:
            short, long_, typ = m.groups()
            flags["--" + long_] = typ is not None
            if short:
                flags["-" + short] = typ is not None
    return out, flags, subs


@lru_cache(None)
def resolves_as_alias(tool, prefix, word):
    """True if `tool prefix word --help` shows a different (child) command's help, i.e. word is an alias."""
    run_env = ENV if tool == "kubectl" else None
    parent = subprocess.run([tool, *prefix, "--help"], capture_output=True, text=True, env=run_env)
    child = subprocess.run([tool, *prefix, word, "--help"], capture_output=True, text=True, env=run_env)
    return child.returncode == 0 and child.stdout.strip() != "" and child.stdout != parent.stdout


def check(cmd):
    try:
        toks = shlex.split(cmd)
    except ValueError as e:
        return [f"cannot parse: {e}"]
    tool = toks[0]
    helpf = kubectl_help if tool == "kubectl" else helm_help
    globals_ = kubectl_globals() if tool == "kubectl" else {}
    errs, prefix, i, consumed_pos = [], (), 1, False
    while i < len(toks):
        t = toks[i]
        _, own, subs = helpf(prefix)
        flags = {**globals_, **own}
        if t == "--":
            break
        if t.startswith("--"):
            name = t.split("=", 1)[0]
            if name not in flags:
                errs.append(f"unknown flag {name} for '{tool} {' '.join(prefix)}'")
            elif flags[name] and "=" not in t:
                i += 1
        elif t.startswith("-") and len(t) > 1 and not t[1].isdigit():
            letters = t[1:]
            for j, ch in enumerate(letters):
                f = "-" + ch
                if f not in flags:
                    errs.append(f"unknown flag {f} for '{tool} {' '.join(prefix)}'")
                    break
                if flags[f]:
                    if j == len(letters) - 1:
                        i += 1
                    break
        else:
            if not consumed_pos and t in subs:
                prefix = prefix + (t,)
            elif not consumed_pos and subs and resolves_as_alias(tool, prefix, t):
                prefix = prefix + (t,)  # an alias such as "pods" for "pod"
            else:
                if not consumed_pos and subs:
                    errs.append(f"unknown subcommand {t!r} for '{tool} {' '.join(prefix)}'")
                consumed_pos = True
        i += 1
    if not prefix:
        errs.append("no subcommand recognised")
    return errs


def commands_in(md):
    found, in_bash = [], False
    for line in md.splitlines():
        if line.startswith("```"):
            in_bash = line.strip() == "```bash"
            continue
        if in_bash:
            found.append(line.strip())
            continue
        for code in re.findall(r"`([^`]+)`", line):
            found.append(code.replace("\\|", "|"))
    cmds = []
    for c in found:
        for seg in re.split(r"\|\||&&|\||;", c):
            m = re.search(r"(?:^|\s)((?:kubectl|helm) \S.*)$", seg.strip())
            if m:
                s = m.group(1).strip()
                if "<" in s.split()[1]:  # e.g. "kubectl <verb>" prose, not a command
                    continue
                cmds.append(s)
    return cmds


if __name__ == "__main__":
    seen, bad = set(), 0
    for path in sys.argv[1:]:
        for c in commands_in(open(path, encoding="utf-8").read()):
            if c in seen:
                continue
            seen.add(c)
            e = check(c)
            if e:
                bad += 1
                print(f"✗ {os.path.basename(path)}: {c}\n    " + "; ".join(e))
    print(f"checked {len(seen)} unique kubectl/helm commands, {bad} with problems")
