#!/usr/bin/env python3
"""Check your paper subnetting answers.

Usage:
  python3 subnet_check.py 10.20.37.140/26 192.168.5.77/27 ...   # describe each address/prefix
  python3 subnet_check.py --classify 10.1.2.3 172.32.0.1 ...     # private / public / special?
  python3 subnet_check.py --overlap 10.0.0.0/16 10.0.128.0/17 ...# any overlaps in a plan?
  python3 subnet_check.py --summarise 172.16.8.0/24 172.16.9.0/24 ...
Only the Python standard library is used.
"""
import ipaddress
import itertools
import sys


def describe(arg):
    iface = ipaddress.ip_interface(arg)
    net = iface.network
    total = net.num_addresses
    if net.version == 4 and net.prefixlen <= 30:
        first, last = net.network_address + 1, net.broadcast_address - 1
        usable = total - 2
    else:  # /31 and /32 (RFC 3021) have no network/broadcast addresses
        first, last, usable = net.network_address, net[-1], total
    aws = total - 5 if 16 <= net.prefixlen <= 28 else "n/a (AWS allows /16 to /28)"
    print(f"{arg}")
    print(f"  network    {net.network_address}/{net.prefixlen}   mask {net.netmask}   wildcard {net.hostmask}")
    if net.version == 4 and net.prefixlen <= 30:
        print(f"  broadcast  {net.broadcast_address}")
    else:
        print("  broadcast  none (a /31 or /32 has no network or broadcast address)")
    print(f"  hosts      {first} - {last}   usable {usable}   (in an AWS subnet: {aws})")


def classify(arg):
    ip = ipaddress.ip_address(arg)
    labels = []
    for name in ("is_loopback", "is_link_local", "is_multicast", "is_reserved", "is_unspecified"):
        if getattr(ip, name):
            labels.append(name[3:])
    if ip.version == 4 and ip in ipaddress.ip_network("100.64.0.0/10"):
        labels.append("shared/CGNAT (RFC 6598)")
    rfc1918 = any(ip in ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
    if rfc1918:
        labels.append("private (RFC 1918)")
    print(f"{arg:<18} global={ip.is_global!s:<5}  {', '.join(labels) or 'public'}")


def overlap(args):
    nets = [ipaddress.ip_network(a) for a in args]
    found = [(a, b) for a, b in itertools.combinations(nets, 2) if a.overlaps(b)]
    print("overlaps:", [f"{a} ~ {b}" for a, b in found] or "none")


def summarise(args):
    nets = [ipaddress.ip_network(a) for a in args]
    print("exact summary:", [str(n) for n in ipaddress.collapse_addresses(nets)])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    mode, rest = sys.argv[1], sys.argv[2:]
    if mode == "--classify":
        for a in rest:
            classify(a)
    elif mode == "--overlap":
        overlap(rest)
    elif mode == "--summarise":
        summarise(rest)
    else:
        for a in sys.argv[1:]:
            describe(a)
