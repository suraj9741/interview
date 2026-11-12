#!/usr/bin/env bash
# make-logs.sh: create practice log files for the 15-day plan labs.
# Usage:  bash make-logs.sh            (creates ./lab/ with app.log, access.log, old files)
set -euo pipefail

mkdir -p lab/old lab/configs
cd lab

# ---- app.log: an application log with INFO/WARN/ERROR/DEBUG lines ----------------
levels=(INFO INFO INFO INFO DEBUG WARN ERROR)
msgs_INFO=("User login success" "Payment processed" "Batch job started" "Batch job finished" "Health check OK")
msgs_DEBUG=("Cache lookup key=txn" "SQL took 12ms")
msgs_WARN=("Slow response 2300ms" "Connection pool 85% used" "Retrying request")
msgs_ERROR=("Connection refused db:5432" "Timeout calling fraud-service" "NullPointerException in TxnValidator" "OutOfMemoryError: Java heap space")
users=(asha ravi suraj meera john)

: > app.log
for i in $(seq 1 600); do
  h=$(( (i / 60) + 9 )); m=$(( i % 60 ))
  lvl=${levels[$((RANDOM % ${#levels[@]}))]}
  arr="msgs_${lvl}[@]"; list=("${!arr}")
  msg=${list[$((RANDOM % ${#list[@]}))]}
  user=${users[$((RANDOM % ${#users[@]}))]}
  printf '2026-11-12 %02d:%02d:%02d %-5s [txn-%04d] user=%s %s\n' "$h" "$m" $((RANDOM % 60)) "$lvl" "$i" "$user" "$msg" >> app.log
done

# ---- access.log: Nginx combined format + request time as last field ----------------
ips=(10.0.1.15 10.0.1.22 10.0.2.8 192.168.1.50 172.16.0.9 10.0.1.15 10.0.1.15)
paths=("/api/login" "/api/payments" "/api/alerts" "/health" "/api/payments" "/static/app.js")
codes=(200 200 200 200 200 201 301 404 500 502 503)
: > access.log
for i in $(seq 1 1000); do
  h=$(( (i / 100) + 9 ))
  ip=${ips[$((RANDOM % ${#ips[@]}))]}
  p=${paths[$((RANDOM % ${#paths[@]}))]}
  c=${codes[$((RANDOM % ${#codes[@]}))]}
  t=$(awk -v r=$RANDOM 'BEGIN{printf "%.3f", (r%2000)/1000}')
  printf '%s - - [12/Nov/2026:%02d:%02d:%02d +0530] "GET %s HTTP/1.1" %s %d "-" "curl/8.5" %s\n' \
    "$ip" "$h" $((RANDOM % 60)) $((RANDOM % 60)) "$p" "$c" $((RANDOM % 5000 + 200)) "$t" >> access.log
done

# ---- config files for sed practice ----------------------------------------------------
cat > configs/app.properties <<'EOF'
# application config
db.url=http://db.internal:5432/payments
db.user=app_user
log.level=DEBUG
feature.newui=false

api.endpoint=http://api.internal/v1
EOF

# ---- old files for find practice (touch -d works on Linux; on macOS use touch -t) -----
for n in 10 45 70 90 120; do
  f="old/report-${n}days.log"
  echo "report $n" > "$f"
  touch -d "$n days ago" "$f" 2>/dev/null || touch -t "$(date -v-"${n}"d +%Y%m%d%H%M)" "$f"
done
dd if=/dev/zero of=old/big-dump.bin bs=1M count=20 status=none 2>/dev/null || dd if=/dev/zero of=old/big-dump.bin bs=1m count=20 2>/dev/null

echo "Created: $(pwd)"
ls -la . old configs
