#!/bin/bash
set -euo pipefail

LOG_DIR="/ws/vishwsh2-sjc/dsaTelegram/logs"
MAX_BYTES="${MAX_BYTES:-10485760}" # 10 MB
KEEP="${KEEP:-5}"

rotate_file() {
  local file="$1"

  if [ ! -f "$file" ]; then
    return
  fi

  local size
  size="$(stat -c%s "$file")"
  if [ "$size" -lt "$MAX_BYTES" ]; then
    return
  fi

  local ts
  ts="$(date +%Y%m%d%H%M%S)"
  mv "$file" "$file.$ts"
  : > "$file"

  ls -1t "$file".* 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f
}

mkdir -p "$LOG_DIR"
rotate_file "$LOG_DIR/bot.log"
rotate_file "$LOG_DIR/bot.err"

