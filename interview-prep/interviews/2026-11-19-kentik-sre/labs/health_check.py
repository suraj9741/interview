#!/usr/bin/env python3
"""health_check.py: check URLs, report status code and latency, exit non-zero if any fail.

Usage: python3 health_check.py https://example.com/health https://example.org
Uses only the standard library (no pip install needed).
"""
import sys
import time
import urllib.error
import urllib.request


def check(url: str, timeout: float = 5.0) -> bool:
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            ms = (time.monotonic() - start) * 1000
            print(f"OK    {resp.status}  {ms:7.1f} ms  {url}")
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as e:          # server answered with 4xx/5xx
        print(f"FAIL  {e.code}  {url}")
    except (urllib.error.URLError, TimeoutError) as e:   # DNS failure, refused, timeout
        print(f"FAIL  ---  {url}  ({e})")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: health_check.py URL [URL ...]")
    results = [check(u) for u in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
