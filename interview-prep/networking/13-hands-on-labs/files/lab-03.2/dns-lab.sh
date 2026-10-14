#!/usr/bin/env bash
# Builds a tiny, offline copy of the DNS hierarchy in Linux network namespaces:
#   root server (.) -> TLD server (lab.) -> authoritative server (example.lab.)
#   plus a recursive resolver and a client.
# Usage:  sudo ./dns-lab.sh up          # build and start everything
#         sudo ./dns-lab.sh flush       # restart the resolver = empty its cache
#         sudo ./dns-lab.sh stop-auth   # stop the authoritative server (to see failures)
#         sudo ./dns-lab.sh start-auth  # start it again
#         sudo ./dns-lab.sh stop-resolver / start-resolver
#         sudo ./dns-lab.sh down        # stop everything and delete it
set -euo pipefail
LAB=/tmp/dnslab
NODES="root tld auth resolver client"
declare -A IP=([root]=10.53.0.10 [tld]=10.53.0.20 [auth]=10.53.0.30 [resolver]=10.53.0.53 [client]=10.53.0.100)

down() {
  for n in $NODES; do
    [ -f "$LAB/$n/named.pid" ] && kill "$(cat "$LAB/$n/named.pid")" 2>/dev/null || true
    ip netns del "$n" 2>/dev/null || true
  done
  ip netns del sw 2>/dev/null || true
  rm -rf "$LAB" /etc/netns/client
  echo "DNS lab removed."
}

server_conf() {   # $1 = node name, $2 = extra options, $3 = zone stanzas
  cat > "$LAB/$1/named.conf" <<EOF
options {
  directory "$LAB/$1";
  pid-file "$LAB/$1/named.pid";
  listen-on { ${IP[$1]}; };
  listen-on-v6 { none; };
  dnssec-validation no;
  $2
};
controls { };
$3
EOF
}

up() {
  mkdir -p "$LAB"/{root,tld,auth,resolver}
  # --- the "internet": one switch (Linux bridge) that every node plugs into
  ip netns add sw
  ip -n sw link add br0 type bridge && ip -n sw link set br0 up
  for n in $NODES; do
    ip netns add "$n"
    ip link add eth0 netns "$n" type veth peer name "p-$n" netns sw
    ip -n sw link set "p-$n" master br0 && ip -n sw link set "p-$n" up
    ip -n "$n" addr add "${IP[$n]}/24" dev eth0
    ip -n "$n" link set eth0 up && ip -n "$n" link set lo up
  done

  # --- root zone: knows only who runs each TLD (here: lab.)
  cat > "$LAB/root/root.zone" <<'EOF'
$TTL 86400
.                    IN SOA  a.root-servers.net. admin.lab. 1 3600 600 86400 300
.                    IN NS   a.root-servers.net.
a.root-servers.net.  IN A    10.53.0.10
; delegation: "lab." is run by ns1.nic.lab (the A record is "glue")
lab.                 IN NS   ns1.nic.lab.
ns1.nic.lab.         IN A    10.53.0.20
; delegation for reverse lookups of 10.53.0.x
0.53.10.in-addr.arpa. IN NS  ns1.example.lab.
ns1.example.lab.     IN A    10.53.0.30
EOF
  server_conf root 'recursion no;' 'zone "." { type primary; file "root.zone"; };'

  # --- TLD zone: knows only who runs each domain inside lab.
  cat > "$LAB/tld/lab.zone" <<'EOF'
$TTL 86400
lab.                 IN SOA  ns1.nic.lab. admin.nic.lab. 1 3600 600 86400 300
lab.                 IN NS   ns1.nic.lab.
ns1.nic.lab.         IN A    10.53.0.20
; delegation: "example.lab." is run by ns1.example.lab (glue below)
example.lab.         IN NS   ns1.example.lab.
ns1.example.lab.     IN A    10.53.0.30
EOF
  server_conf tld 'recursion no;' 'zone "lab." { type primary; file "lab.zone"; };'

  # --- authoritative zone: the real answers for example.lab.
  cat > "$LAB/auth/example.lab.zone" <<'EOF'
$TTL 300
@        IN SOA   ns1.example.lab. admin.example.lab. 2026101401 3600 600 86400 60
@        IN NS    ns1.example.lab.
ns1      IN A     10.53.0.30
@        IN A     10.53.0.80
@        IN AAAA  fd00:53::80
www      IN CNAME example.lab.
api      IN A     10.53.0.81
api      IN A     10.53.0.82
@        IN MX    10 mail.example.lab.
mail     IN A     10.53.0.25
@        IN TXT   "v=spf1 mx -all"
EOF
  cat > "$LAB/auth/10.53.0.rev" <<'EOF'
$TTL 300
@        IN SOA   ns1.example.lab. admin.example.lab. 2026101401 3600 600 86400 60
@        IN NS    ns1.example.lab.
80       IN PTR   example.lab.
81       IN PTR   api.example.lab.
EOF
  server_conf auth 'recursion no;' 'zone "example.lab." { type primary; file "example.lab.zone"; };
zone "0.53.10.in-addr.arpa." { type primary; file "10.53.0.rev"; };'

  # --- recursive resolver: starts from the root "hints", follows referrals, caches
  cat > "$LAB/resolver/root.hints" <<'EOF'
.                    3600000 IN NS a.root-servers.net.
a.root-servers.net.  3600000 IN A  10.53.0.10
EOF
  server_conf resolver 'recursion yes; allow-recursion { 10.53.0.0/24; }; empty-zones-enable no;' 'zone "." { type hint; file "root.hints"; };'

  for n in root tld auth resolver; do
    ip netns exec "$n" named -c "$LAB/$n/named.conf" -n 1 -L "$LAB/$n/named.log"
  done

  # --- the client uses the resolver (ip netns exec bind-mounts this file over /etc/resolv.conf)
  mkdir -p /etc/netns/client
  printf 'nameserver 10.53.0.53\nsearch example.lab\n' > /etc/netns/client/resolv.conf
  sleep 2
  echo "DNS lab is up. Try:  sudo ip netns exec client dig www.example.lab"
}

stop() { kill "$(cat "$LAB/$1/named.pid")" 2>/dev/null || true; sleep 1; }
start() { ip netns exec "$1" named -c "$LAB/$1/named.conf" -n 1 -L "$LAB/$1/named.log"; sleep 1; }

case "${1:-}" in
  up) up ;;
  down) down ;;
  flush) stop resolver; start resolver; echo "Resolver restarted: its cache is empty." ;;
  stop-auth) stop auth; echo "Authoritative server for example.lab stopped." ;;
  start-auth) start auth; echo "Authoritative server for example.lab started." ;;
  stop-resolver) stop resolver; echo "Recursive resolver stopped." ;;
  start-resolver) start resolver; echo "Recursive resolver started (empty cache)." ;;
  *) echo "usage: $0 up|flush|stop-auth|start-auth|stop-resolver|start-resolver|down"; exit 1 ;;
esac
