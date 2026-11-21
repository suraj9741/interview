#!/usr/bin/env bash
# disk_alert.sh: warn when any filesystem is above a usage threshold.
# Usage: ./disk_alert.sh [threshold_percent]   (default 80)
set -euo pipefail

THRESHOLD="${1:-80}"
status=0

# -P = one line per filesystem (POSIX format); skip the header and pseudo filesystems
while read -r fs size used avail pct mount; do
  usage="${pct%\%}"                      # "83%" -> "83"
  if (( usage >= THRESHOLD )); then
    echo "ALERT: ${mount} is at ${usage}% (${fs})"
    status=1
  fi
done < <(df -P -x tmpfs -x devtmpfs -x overlay 2>/dev/null | tail -n +2)

if (( status == 0 )); then
  echo "OK: all filesystems below ${THRESHOLD}%"
fi
exit "$status"                            # non-zero exit lets cron/monitoring detect the alert
