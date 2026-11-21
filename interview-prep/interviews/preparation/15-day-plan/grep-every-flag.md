# grep: one example per flag (Day 1 practice)

**Learn the ⭐ flags by heart.** These are the ones interviews and real incidents use: `-i -v -c -n -E -w -o -l -r -A -B -C -q -e -F`. Type the rest once so you know they exist, but don't try to memorise them.

Every example was run against the lab files (GNU grep on Ubuntu). Run everything inside your Day 1 lab folder (`lab/`, created by `make-logs.sh`). Before you press Enter, **say out loud what you expect to see**.

## 1. Program information

| Flag | Example | What you'll see |
|---|---|---|
| `-V` | `grep -V` | grep version (GNU grep 3.x) |
| `--help` | `grep --help \| head -20` | usage summary |

## 2. Pattern syntax: how the pattern is read

| Flag | Example | What it shows |
|---|---|---|
| ⭐ `-E` | `grep -E 'ERROR\|WARN' app.log` | `\|` means OR in extended regex |
| | `grep -E 'txn-0[0-9]{3}' app.log \| head -3` | `{3}` = exactly 3 digits (ERE) |
| `-G` (default) | `grep -G 'ERROR' app.log \| head -3` | basic regex, the default. Here OR needs a backslash before the pipe (`ERROR\` + pipe + `WARN`), which is why `-E` is easier |
| ⭐ `-F` | `grep -F 'db.url=http://' configs/app.properties` | **fixed string**: `.` means a literal dot, not "any character". Fast and safe for text with special characters |
| | `grep -F '[txn-0001]' app.log` | without `-F`, `[...]` would be read as a character class |
| `-P` | `grep -P '\d{4}-\d{2}-\d{2} 1[0-2]:' app.log \| head -3` | Perl regex: `\d` = digit (not on macOS's BSD grep) |
| | `grep -oP 'user=\K\w+' app.log \| sort \| uniq -c` | `\K` drops `user=` from the output, leaving only the name |

## 3. Matching control: what counts as a match

| Flag | Example | What it shows |
|---|---|---|
| ⭐ `-e` | `grep -e ERROR -e WARN app.log \| wc -l` | several patterns, OR (an alternative to `-E 'A\|B'`) |
| | `grep -e '-v' file.txt` | search for text that **starts with a hyphen** |
| `-f` | `printf 'Timeout\nOutOfMemoryError\n' > patterns.txt; grep -f patterns.txt app.log` | patterns read from a file, one per line (e.g. a list of known errors or IPs) |
| ⭐ `-i` | `grep -i 'error' app.log \| wc -l` | ignore case: error, Error, ERROR |
| ⭐ `-v` | `grep -v -e INFO -e DEBUG app.log \| head` | invert: lines **without** INFO or DEBUG |
| | `grep -v '^#' configs/app.properties \| grep -v '^$'` | config without comments and blank lines |
| ⭐ `-w` | `echo -e "INFO\nINFORMATION" \| grep -w INFO` | only the whole word `INFO`, not `INFORMATION` |
| `-x` | `grep -x 'log.level=DEBUG' configs/app.properties` | the whole line must match exactly |
| `-y` | `grep -y error app.log \| head -2` | old name for `-i`; you'll never need it |
| `--no-ignore-case` | `grep -i --no-ignore-case ERROR app.log \| head -2` | cancels an earlier `-i` (useful in aliases) |

## 4. General output control: what gets printed

| Flag | Example | What it shows |
|---|---|---|
| ⭐ `-c` | `grep -c ERROR app.log` | count of matching **lines** |
| | `grep -c ERROR app.log access.log` | count per file |
| `-L` | `grep -L ERROR configs/* app.log` | files that do **not** contain ERROR |
| ⭐ `-l` | `grep -l "db.url" -r .` | only the names of files that contain a match |
| `-m` | `grep -m 3 ERROR app.log` | stop after the first 3 matches (fast on huge logs) |
| ⭐ `-o` | `grep -o 'user=[a-z]*' app.log \| sort \| uniq -c \| sort -rn` | only the matched part, so you can count values |
| | `grep -oE '" [0-9]{3} ' access.log \| sort \| uniq -c` | HTTP status code counts |
| ⭐ `-q` | `grep -q OutOfMemoryError app.log && echo "OOM found, alert!"` | no output, only the exit code. Use it in scripts: `if grep -q …; then` |
| `-s` | `grep -s ERROR nofile.log app.log \| head -2` | hide the "No such file" error |
| `--color` | `grep --color=always ERROR app.log \| head -3` | highlight matches (`auto` is the default in most terminals) |

## 5. Output line prefix control

| Flag | Example | What it shows |
|---|---|---|
| `-b` | `grep -b ERROR app.log \| head -2` | byte offset of each matching line |
| `-H` | `grep -H ERROR app.log \| head -2` | file name in front, even with one file |
| `-h` | `grep -h ERROR app.log access.log \| head -2` | no file names, even with many files |
| ⭐ `-n` | `grep -n OutOfMemoryError app.log` | line numbers, so you can then do `sed -n '120,130p' app.log` |
| `-T` | `grep -nT ERROR app.log \| head -2` | aligns output on a tab |
| `-u` | `grep -bu ERROR app.log \| head -2` | Unix byte offsets. **Obsolete**: newer GNU grep prints a warning and ignores it |
| `-Z` | `grep -lZ ERROR *.log \| xargs -0 ls -l` | NUL after file names, safe with spaces in names |
| `--label` | `cat app.log \| grep -H --label=from-stdin ERROR \| head -2` | name to show for stdin |

## 6. Context lines: what happened around the error

| Flag | Example | What it shows |
|---|---|---|
| ⭐ `-A` | `grep -A 3 OutOfMemoryError app.log` | 3 lines **after** (the stack trace usually follows the error) |
| ⭐ `-B` | `grep -B 2 "Connection refused" app.log` | 2 lines **before** (what led up to it) |
| ⭐ `-C` | `grep -C 2 Timeout app.log \| head -20` | 2 lines before **and** after |
| `-NUM` | `grep -2 Timeout app.log \| head -10` | same as `-C 2` |
| `--group-separator` | `grep -A1 --group-separator='=====' ERROR app.log \| head -10` | custom line between groups instead of `--` |
| `--no-group-separator` | `grep -A1 --no-group-separator ERROR app.log \| head -6` | no separator line |

## 7. Files and directories

| Flag | Example | What it shows |
|---|---|---|
| `-a` | `printf 'ERROR in core\0\0' > core.bin; grep ERROR core.bin; grep -a ERROR core.bin` | first prints only "binary file matches"; with `-a` it treats the file as text and prints the line |
| `-D` | `grep -D skip -r ERROR /dev 2>/dev/null` | skip devices, FIFOs and sockets |
| `-d` | `grep -d skip ERROR *` | skip directories instead of printing "Is a directory" |
| `-I` | `grep -rI ERROR .` | ignore binary files during a recursive search |
| ⭐ `-r` | `grep -r "db.url" configs/` | search every file in a folder |
| `-R` | `grep -R "db.url" /etc/myapp/` | same as `-r`, but follows **all** symlinks |
| `--binary-files` | `grep --binary-files=without-match -r ERROR .` | long form of `-I` |
| ⭐ `--include` | `grep -r --include='*.log' ERROR .` | search only `.log` files |
| ⭐ `--exclude` | `grep -r --exclude='*.bak' "http" configs/` | skip backup files |
| `--exclude-from` | `echo '*.bin' > skip.txt; grep -r --exclude-from=skip.txt ERROR .` | skip patterns listed in a file |
| ⭐ `--exclude-dir` | `grep -r --exclude-dir=old --exclude-dir=.git ERROR .` | skip whole folders (`.git`, `node_modules`) |

## 8. Other options

| Flag | Example | What it shows |
|---|---|---|
| `-U` | `grep -U $'\r' file.txt` | keeps Windows CR characters (spot "file has CRLF line endings" problems) |
| `-z` | `find . -name '*.log' -print0 \| grep -z app` | input lines end with NUL, which pairs with `find -print0` |
| ⭐ `--line-buffered` | `tail -f app.log \| grep --line-buffered ERROR \| tee errors-live.txt` | print each match immediately when piping a live log; without it, output waits in a buffer |

## Combined, the way you'll use them at work

```bash
grep -rniE 'error|exception' --include='*.log' --exclude-dir=old .      # every error, any case, with file and line
grep -c "Connection refused" app.log                                    # how often?
grep -B2 -A5 OutOfMemoryError app.log                                   # what happened around the OOM?
grep -oE '" [0-9]{3} ' access.log | sort | uniq -c | sort -rn           # status code breakdown
grep -v -e INFO -e DEBUG app.log | grep -o 'user=[a-z]*' | sort | uniq -c   # problems per user
tail -f app.log | grep --line-buffered -E 'ERROR|WARN'                  # watch live
if grep -q OutOfMemoryError app.log; then echo "page on-call"; fi       # in a script
```

## 10-minute self-test (no notes, then check)

1. Count lines containing "timeout" in any case.
2. Show every line that has neither INFO nor DEBUG.
3. Show 5 lines after each "OutOfMemoryError", with line numbers.
4. List only the names of files under `/etc/myapp` that contain `password`, skipping `.bak` files.
5. Print only the IP address (first field) of requests that got a 502, then count the IPs.
6. Search for the literal text `1.2.3.4` so that the dots aren't treated as "any character".
7. In a script, print "found" if app.log contains "FATAL", without printing the matching lines.
8. Watch a live log and save only ERROR lines to a file as they arrive.

<details><summary>Answers</summary>

1. `grep -ic timeout app.log`
2. `grep -v -e INFO -e DEBUG app.log`
3. `grep -n -A5 OutOfMemoryError app.log`
4. `grep -rl --exclude='*.bak' password /etc/myapp`
5. `grep '" 502 ' access.log | awk '{print $1}' | sort | uniq -c | sort -rn`
6. `grep -F '1.2.3.4' file`
7. `grep -q FATAL app.log && echo found`
8. `tail -f app.log | grep --line-buffered ERROR > errors.txt`
</details>
