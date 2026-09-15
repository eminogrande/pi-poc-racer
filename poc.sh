#!/bin/sh
# poc — one command. Opens the pi-poc-racer TUI (pi + general persona + skills).
DIR="$(cd "$(dirname "$0")" && pwd)"
exec pi \
  --append-system-prompt "$DIR/prompts/general.md" \
  --append-system-prompt "$DIR/skills/ponytail.md" \
  --append-system-prompt "$DIR/skills/caveman.md" \
  --append-system-prompt "$DIR/skills/adhd.md" \
  "$@"
