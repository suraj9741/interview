#!/usr/bin/env python3
"""log_report.py: count log levels, ERROR lines per hour, and the top users in an app log.

Usage: python3 log_report.py app.log [--top 3]
Line format: 2026-11-12 09:01:23 ERROR [txn-0001] user=john Connection refused db:5432
"""
import argparse
import re
import sys
from collections import Counter

LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}):\d{2}:\d{2} (\w+)\s+\[[^\]]+\] user=(\w+)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarise an application log")
    parser.add_argument("logfile")
    parser.add_argument("--top", type=int, default=3, help="how many users to show")
    args = parser.parse_args()

    levels, errors_per_hour, users = Counter(), Counter(), Counter()
    skipped = 0
    try:
        with open(args.logfile) as f:
            for line in f:
                m = LINE.match(line)
                if not m:
                    skipped += 1
                    continue
                _date, hour, level, user = m.groups()
                levels[level] += 1
                users[user] += 1
                if level == "ERROR":
                    errors_per_hour[hour] += 1
    except FileNotFoundError:
        print(f"error: {args.logfile} not found", file=sys.stderr)
        return 2

    print("Lines per level:")
    for level, n in levels.most_common():
        print(f"  {level:<5} {n}")
    print("ERROR lines per hour:")
    for hour in sorted(errors_per_hour):
        print(f"  {hour}:00  {errors_per_hour[hour]}")
    print(f"Top {args.top} users:")
    for user, n in users.most_common(args.top):
        print(f"  {user:<6} {n}")
    if skipped:
        print(f"({skipped} lines did not match the format)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
