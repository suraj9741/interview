#!/usr/bin/env bash
# A small network with one hidden fault, for practising troubleshooting.
#
#   client ──────── r1 ────── 10.0.0.0/30 ────── r2 ──────── server
#   10.1.1.10   10.1.1.1  10.0.0.1      10.0.0.2  10.2.2.1   10.2.2.20
#                                                          (web :8080, DNS :53)
#
# Usage:  sudo ./broken-network.sh up <1-8>    build it with fault number N (no spoilers)
#         sudo ./broken-network.sh up random   a random fault
#         sudo ./broken-network.sh up 0        no fault: everything works
#         sudo ./broken-network.sh test        the user's complaint, as a command
#         sudo ./broken-network.sh down        remove everything
# Investigate with:  sudo ip netns exec <client|r1|r2|server> <command>
set -euo pipefail
WORK=/tmp/broken-network
NODES="client r1 r2 server"

down() {
  for n in $NODES; do
    { ip netns pids "$n" | xargs -r kill; } >/dev/null 2>&1 || true
    ip netns del "$n" 2>/dev/null || true
  done
  rm -rf "$WORK" /etc/netns/client
}

up() {
  local fault="$1"
  [ "$fault" = random ] && fault=$(( (RANDOM % 8) + 1 ))
  down
  mkdir -p "$WORK/www"
  echo "$fault" > "$WORK/.fault"    # the answer, if you give up: cat /tmp/broken-network/.fault

  for n in $NODES; do ip netns add "$n"; ip -n "$n" link set lo up; done
  ip link add eth0 netns client type veth peer name eth0 netns r1
  ip link add eth1 netns r1 type veth peer name eth1 netns r2
  ip link add eth0 netns r2 type veth peer name eth0 netns server
  ip -n client addr add 10.1.1.10/24 dev eth0
  ip -n r1 addr add 10.1.1.1/24 dev eth0
  ip -n r1 addr add 10.0.0.1/30 dev eth1
  ip -n r2 addr add 10.0.0.2/30 dev eth1
  ip -n r2 addr add 10.2.2.1/24 dev eth0
  ip -n server addr add 10.2.2.20/24 dev eth0
  for n in $NODES; do
    for i in eth0 eth1; do ip -n "$n" link set "$i" up 2>/dev/null || true; done
  done
  ip netns exec r1 sysctl -qw net.ipv4.ip_forward=1
  ip netns exec r2 sysctl -qw net.ipv4.ip_forward=1
  ip -n client route add default via 10.1.1.1
  ip -n r1 route add 10.2.2.0/24 via 10.0.0.2
  ip -n r2 route add 10.1.1.0/24 via 10.0.0.1
  ip -n server route add default via 10.2.2.1
  # The link between the routers is narrower, like a VPN or tunnel in real life.
  ip -n r1 link set eth1 mtu 1400
  ip -n r2 link set eth1 mtu 1400

  # DNS: the server answers for app.lab, and the client uses it as its resolver.
  mkdir -p /etc/netns/client
  echo "nameserver 10.2.2.20" > /etc/netns/client/resolv.conf
  ip netns exec server dnsmasq --conf-file=/dev/null --no-resolv --no-hosts \
    --listen-address=10.2.2.20 --bind-interfaces --address=/app.lab/10.2.2.20 \
    --pid-file="$WORK/dnsmasq.pid"

  # Web: a small page and a big file.
  echo "OK: the app answered" > "$WORK/www/index.html"
  head -c 200000 /dev/zero | tr '\0' 'x' > "$WORK/www/big.txt"
  local bind=0.0.0.0

  case "$fault" in
    0) ;;
    1) echo "nameserver 10.2.2.99" > /etc/netns/client/resolv.conf ;;
    2) ip -n client route replace default via 10.1.1.254 ;;
    3) ip netns exec r1 sysctl -qw net.ipv4.ip_forward=0 ;;
    4) ip -n server route del default ;;
    5) ip netns exec server iptables -A INPUT -p tcp --dport 8080 -j DROP ;;
    6) bind=none ;;
    7) bind=127.0.0.1 ;;
    8) ip netns exec r2 iptables -A OUTPUT -p icmp --icmp-type fragmentation-needed -j DROP ;;
    *) echo "unknown fault: $fault (use 0-8 or random)"; exit 1 ;;
  esac
  if [ "$bind" != none ]; then
    ip netns exec server nohup python3 -m http.server 8080 --bind "$bind" \
      --directory "$WORK/www" >"$WORK/web.log" 2>&1 &
  fi
  sleep 1
  echo "Network is up. A user on 'client' says: \"I can't download http://app.lab:8080/big.txt\""
  echo "See the complaint with:  sudo $0 test"
}

complaint() {
  echo "\$ curl -sS -m 5 -o /dev/null -w '%{http_code} %{size_download} bytes\\n' http://app.lab:8080/big.txt"
  ip netns exec client curl -sS -m 5 -o /dev/null -w '%{http_code} %{size_download} bytes\n' \
    http://app.lab:8080/big.txt || true
}

case "${1:-}" in
  up) up "${2:?give a fault number 0-8, or random}" ;;
  test) complaint ;;
  down) down; echo "Removed." ;;
  *) echo "usage: $0 up <0-8|random> | test | down"; exit 1 ;;
esac
