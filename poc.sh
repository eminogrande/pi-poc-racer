#!/bin/sh
# poc — one command. Opens the pi-poc-racer TUI (pi + Clerk of the Course, racer theme).
# Clean room: no user skills/extensions/context files, quiet startup, no update banners.
# Auto-updates itself from origin before launch.
LINK="$0"
while [ -L "$LINK" ]; do
  NEXT="$(readlink "$LINK")"
  case "$NEXT" in /*) LINK="$NEXT" ;; *) LINK="$(dirname "$LINK")/$NEXT" ;; esac
done
DIR="$(cd "$(dirname "$LINK")" && pwd)"

git -C "$DIR" pull -q --ff-only >/dev/null 2>&1 || true

[ -f .pi/settings.json ] || { mkdir -p .pi && printf '{ "quietStartup": true }\n' > .pi/settings.json; }
export PI_OFFLINE=1
[ -t 1 ] && cat "$DIR/themes/banner.ansi"
exec pi \
  --model "${POC_CLERK_MODEL:-kimi-coding/k3:max}" \
  --no-skills --no-extensions --no-context-files --no-prompt-templates --no-themes \
  --theme "$DIR/themes/racer.json" \
  --use-theme racer \
  --append-system-prompt "$DIR/prompts/clerk.md" \
  "$@"
