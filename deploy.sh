#!/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="dsa-bot.service"

cd "$REPO_DIR"

echo "→ Pulling latest code"
git pull --ff-only

if [ ! -x "$REPO_DIR/.venv/bin/python" ]; then
  echo "→ Creating virtualenv"
  python3 -m venv "$REPO_DIR/.venv"
fi

echo "→ Installing dependencies"
"$REPO_DIR/.venv/bin/pip" install -r "$REPO_DIR/requirements.txt"

echo "→ Restarting user service"
systemctl --user restart "$SERVICE_NAME"

echo "✓ Deploy complete"

