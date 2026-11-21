#!/usr/bin/env python3
"""python_drills.py: 12 small problems that SRE/DevOps Python rounds often ask.

Try each one from a blank file first. Then compare with the solution here.
Run all the self-tests:  python3 python_drills.py
"""
import json
from collections import Counter


# 1. Reverse a string (two ways)
def reverse(s: str) -> str:
    return s[::-1]                      # slicing: start:stop:step, step -1 walks backwards


def reverse_loop(s: str) -> str:
    out = ""
    for ch in s:
        out = ch + out
    return out


# 2. Is it a palindrome? Ignore case and non-letters.
def is_palindrome(s: str) -> bool:
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]


# 3. Count how often each word appears; return the top n
def top_words(text: str, n: int = 3) -> list:
    words = text.lower().split()
    return Counter(words).most_common(n)


def word_count_dict(text: str) -> dict:   # same without Counter (they may ask this)
    counts = {}
    for w in text.lower().split():
        counts[w] = counts.get(w, 0) + 1
    return counts


# 4. FizzBuzz 1..n
def fizzbuzz(n: int) -> list:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out


# 5. Find duplicates in a list
def duplicates(items: list) -> list:
    seen, dups = set(), set()
    for x in items:
        if x in seen:
            dups.add(x)
        seen.add(x)
    return sorted(dups)


# 6. Two-sum: indexes of two numbers that add up to target (O(n) with a dict)
def two_sum(nums: list, target: int):
    index_of = {}
    for i, n in enumerate(nums):
        if target - n in index_of:
            return index_of[target - n], i
        index_of[n] = i
    return None


# 7. Second-largest unique number
def second_largest(nums: list):
    uniq = sorted(set(nums), reverse=True)
    return uniq[1] if len(uniq) > 1 else None


# 8. Flatten a nested list one level, then fully (recursion)
def flatten_once(lst: list) -> list:
    return [x for sub in lst for x in sub]


def flatten(lst: list) -> list:
    out = []
    for x in lst:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out


# 9. Parse JSON: names of pods that are not Running
def not_running(pods_json: str) -> list:
    data = json.loads(pods_json)
    return [p["name"] for p in data["pods"] if p["status"] != "Running"]


# 10. Group IPs by status code from access-log-like lines
def ips_by_status(lines: list) -> dict:
    groups = {}
    for line in lines:
        parts = line.split()
        ip, status = parts[0], parts[8]
        groups.setdefault(status, set()).add(ip)
    return {k: sorted(v) for k, v in sorted(groups.items())}


# 11. Count vowels; check if two strings are anagrams
def vowels(s: str) -> int:
    return sum(1 for c in s.lower() if c in "aeiou")


def anagrams(a: str, b: str) -> bool:
    return sorted(a.replace(" ", "").lower()) == sorted(b.replace(" ", "").lower())


# 12. A small class: a service with a health check and restart counter
class Service:
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.restarts = 0
        self.healthy = True

    def restart(self) -> None:
        self.restarts += 1
        self.healthy = True

    def __repr__(self) -> str:
        return f"Service({self.name!r}, port={self.port}, restarts={self.restarts})"


if __name__ == "__main__":
    assert reverse("devops") == "spoved" == reverse_loop("devops")
    assert is_palindrome("A man, a plan, a canal: Panama") and not is_palindrome("sre")
    assert top_words("the pod the node the pod", 2) == [("the", 3), ("pod", 2)]
    assert word_count_dict("a b a") == {"a": 2, "b": 1}
    assert fizzbuzz(15)[-1] == "FizzBuzz" and fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
    assert duplicates([1, 2, 3, 2, 1, 5]) == [1, 2]
    assert two_sum([2, 7, 11, 15], 9) == (0, 1) and two_sum([1, 2], 10) is None
    assert second_largest([5, 1, 5, 3]) == 3 and second_largest([4, 4]) is None
    assert flatten_once([[1, 2], [3]]) == [1, 2, 3] and flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]
    pods = '{"pods": [{"name": "web-1", "status": "Running"}, {"name": "db-0", "status": "CrashLoopBackOff"}]}'
    assert not_running(pods) == ["db-0"]
    log = ['10.0.0.1 - - [x +0530] "GET / HTTP/1.1" 200 10',
           '10.0.0.2 - - [x +0530] "GET / HTTP/1.1" 502 10',
           '10.0.0.1 - - [x +0530] "GET / HTTP/1.1" 502 10']
    assert ips_by_status(log) == {"200": ["10.0.0.1"], "502": ["10.0.0.1", "10.0.0.2"]}
    assert vowels("Kubernetes") == 4 and anagrams("listen", "silent")
    s = Service("api", 8080)
    s.restart()
    assert s.restarts == 1 and repr(s) == "Service('api', port=8080, restarts=1)"
    print("all 12 drills pass")
