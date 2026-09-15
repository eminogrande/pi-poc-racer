#!/bin/sh
# poc — one command. Opens the pi-poc-racer TUI (pi + Clerk of the Course, racer theme).
# Clean room: no user skills/extensions/context files, quiet startup.
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f .pi/settings.json ] || { mkdir -p .pi && printf '{ "quietStartup": true }\n' > .pi/settings.json; }
exec pi \
  --model "${POC_CLERK_MODEL:-kimi-coding/k3:max}" \
  --no-skills --no-extensions --no-context-files --no-prompt-templates --no-themes \
  --theme "$DIR/themes/racer.json" \
  --use-theme racer \
  --append-system-prompt "$DIR/prompts/clerk.md" \
  "$@"
