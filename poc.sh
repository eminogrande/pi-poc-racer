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
V=$(grep '"version"' "$DIR/package.json" | head -1 | cut -d'"' -f4)
H=$(git -C "$DIR" rev-parse --short HEAD 2>/dev/null)
echo "🏁 poc v$V ($H)"

[ -f .pi/settings.json ] || { mkdir -p .pi && printf '{ "quietStartup": true }\n' > .pi/settings.json; }
export PI_OFFLINE=1
if [ -t 1 ]; then
  W=$(( $(tput cols) - 2 ))
  python3 "$DIR/scripts/banner.py" "$W" /tmp/poc-banner.ansi >/dev/null 2>&1 && cat /tmp/poc-banner.ansi
fi
exec pi \
  --model "${POC_CLERK_MODEL:-kimi-coding/k3:medium}" \
  --no-skills --no-extensions --no-context-files --no-prompt-templates --no-themes \
  --theme "$DIR/themes/racer.json" \
  --use-theme racer \
  --append-system-prompt "$DIR/prompts/clerk.md" \
  "$@"
