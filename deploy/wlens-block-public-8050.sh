#!/usr/bin/env bash
set -euo pipefail

RULE=(
  -p tcp
  --dport 8050
  !
  -i lo
  !
  -s 172.16.0.0/12
  -j REJECT
  --reject-with tcp-reset
)

if ! iptables -C INPUT "${RULE[@]}" 2>/dev/null; then
  iptables -I INPUT 1 "${RULE[@]}"
fi
