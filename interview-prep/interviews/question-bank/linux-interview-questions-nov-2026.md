# Linux and shell scripting interview questions with answers (real rounds, Nov 2026)

These Linux and shell scripting questions came from real DevOps / SRE interview rounds in November 2026 (4–8 years of experience). Each answer is short enough to say in about 30 to 60 seconds.

**How to use it:** cover the answer, type the command from memory, run it on a Linux box, then check.

---

**1.1 Name some Linux commands you use daily.**
Group them so it sounds organised:
- **files:** `ls cd cp mv rm find`
- **text:** `cat less grep sed awk sort uniq wc head tail`
- **processes:** `ps top kill systemctl journalctl`
- **disk:** `df du lsof`
- **network:** `ss curl dig ping traceroute`
- **permissions:** `chmod chown`

**1.2 Find lines containing "error" or "info" in a log file.**
```bash
grep -Ei 'error|info' app.log
```
`-E` is needed for `|` (alternation), and `-i` ignores case. Useful extras: `-c` counts, `-n` shows line numbers, `-v` excludes.

**1.3 Replace "error" with "success" in a file.**
```bash
sed -i 's/error/success/g' app.log      # -i.bak keeps a backup
```
`s` = substitute, `g` = every match on the line. Run it without `-i` first to preview the result.

**1.4 Find files in a folder older than 60 days (and delete them).**
```bash
find /var/log/app -type f -mtime +60            # list
find /var/log/app -type f -mtime +60 -delete    # delete
```
`-mtime +60` = modified more than 60 days ago; `-mtime -1` = within the last day.

**1.5 How do you list all processes running on the system?**
`ps aux` or `ps -ef` for everything; `top` / `htop` for a live view sorted by CPU or memory; `pgrep -a nginx` to find one by name.

**1.6 Run a script, but if someone already ran it within the last hour, it must not run again.**
Use a timestamp file for "less than an hour ago" and `flock` so two copies can't run at the same time:
```bash
#!/usr/bin/env bash
set -euo pipefail
STAMP=/var/tmp/myjob.last_run
LOCK=/var/tmp/myjob.lock

exec 9>"$LOCK"
flock -n 9 || { echo "Already running"; exit 0; }

if [[ -f "$STAMP" ]] && (( $(date +%s) - $(stat -c %Y "$STAMP") < 3600 )); then
  echo "Ran less than an hour ago, exiting"; exit 0
fi

echo "Running the job..."     # real work here
touch "$STAMP"                # record success only at the end
```

**1.7 A shell script fails at line 10 but keeps running. How do you make it stop there?**
```bash
set -euo pipefail
trap 'echo "Error on line $LINENO: $BASH_COMMAND" >&2' ERR
```
- `-e`: exit on the first failing command.
- `-u`: an unset variable is an error.
- `pipefail`: a pipeline fails if any part of it fails.

For a single command: `cmd || exit 1`. Note that `set -e` doesn't trigger inside `if` conditions or on the left side of `&&` / `||`.

**1.8 Write a script that alerts when any filesystem is above 80% full.** *(practice question, not asked in these rounds)*
```bash
#!/usr/bin/env bash
set -euo pipefail
THRESHOLD="${1:-80}"; status=0
while read -r fs size used avail pct mount; do
  usage="${pct%\%}"
  if (( usage >= THRESHOLD )); then echo "ALERT: $mount at ${usage}%"; status=1; fi
done < <(df -P -x tmpfs -x devtmpfs | tail -n +2)
exit $status
```
`< <(...)` feeds the loop without a pipe. With a pipe, the loop runs in a subshell and `status=1` would be lost.

**1.9 Describe a shell automation you've written.**
Example answer: "A daily RDS backup script, run from Jenkins, that uses the AWS CLI to take a snapshot (`aws rds create-db-snapshot`) and deletes snapshots older than 7 days." Mention scheduling, logging and alerting on failure.
