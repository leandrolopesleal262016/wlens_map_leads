#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/wlens_map_leads}"
BRANCH="${BRANCH:-main}"
REMOTE="${REMOTE:-origin}"
SERVICE_NAME="${SERVICE_NAME:-wlens-map-leads}"

cd "$APP_DIR"

git fetch "$REMOTE"
git checkout "$BRANCH"
git pull --ff-only "$REMOTE" "$BRANCH"

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements-vps.txt"

systemctl restart "$SERVICE_NAME"
systemctl status "$SERVICE_NAME" --no-pager
