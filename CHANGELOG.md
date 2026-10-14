# Changelog

Newest first. Every SHA is a commit on `master`.

## 2026-10-14 — [RELEASE] v0.5.0 — hermes-agent for emino

State at `master` HEAD `e55292fe` (package.json `0.5.0`, set in that commit):

- `poc` opens a clean-room pi TUI with the Clerk of the Course prompt, racer theme and width-scaled banner; self-updates via `git pull --ff-only`.
- `pi-poc-racer run` races `.racer/PLAN.md` with parallel pi workers, token ceiling and silence kill, split and redispatch, live standings, per-task commits, one push at READY TO TEST.
- `pi-poc-racer smoke` checks the worker harness before every race.
- `pi-poc-racer viz [--mermaid]` prints the plan as a tree or Mermaid graph.
- Steering mid-race via `.racer/STEER.md`: `kill`, `drop`, `note`, `pause`, `resume`.
- Docs: README rewritten with Logs, Status, Architecture, User flow, Components, CLI reference, Run; CHANGELOG and PROMPTLOG added. No code changed.

## 2026-09-16

- `e55292fe` feat: `viz` command prints an ASCII tree per task with Test lines, `--mermaid` prints a Mermaid graph. Version 0.5.0.
- `e30f95fe` fix: planning is one round with max 3 open points and defaults; Clerk thinking level lowered from max to medium. Version 0.4.1.
- `be189f7d` feat: one-screen plan checklist (decide, present, GO); dead questionnaire code removed. Version 0.4.0.
- `e45c426d` feat: pit-radio voice without fillers, every task must carry Goal and Test, rules card at session start. Version 0.3.0.
- `489ac3e9` fix: banner scales to terminal width at startup; `poc` prints version and commit hash at launch. Version 0.2.0.
- `e18c99fa` feat: natural-language steering; the Clerk translates plain text into steer commands.
- `b5914f2b` feat: live steer channel via `.racer/STEER.md` (kill, drop, note, pause, resume); Clerk no longer polls; readable worker status.
- `2fa2c222` feat: Clerk must pass the smoke test before every race.
- `a5487182` fix: real push status with rebase retry, `.racer` excluded from commits, pre-race smoke test added.
- `116c8320` feat: planning proposes one item at a time with a recommendation instead of batch lists.
- `7092dfd3` feat: Clerk voice changed to a playful race-queen persona with truthful data (later replaced by pit-radio voice in `e45c426d`).
- `e7ff15fa` feat: Clerk gets a champion character: radio style, ruthless kills.
- `a2cfd88a` feat: pixelated race-queen image composited above the logotype in the banner.
- `ef0a874e` refactor: banner reduced to pixel logotype in two-tone race red.
- `ded18bcc` feat: pixel banner header rendered as half-block ANSI.
- `8bbbd753` fix: `poc` resolves the npm symlink to find its directory, auto-updates via `git pull`, sets `PI_OFFLINE` to hide update banners.
- `30c310aa` feat: separate thinking levels for Clerk and workers, tunable via env.
- `8b48edde` feat: clean-room TUI (quiet startup, no skills, extensions or context files), commit per task, push only at finish; skill files dropped.
- `51df039c` feat: Clerk of the Course with live standings, lap times and race commentary.

## 2026-09-15

- `6a577464` feat: racer color theme (race red, nitro, gold) and racing persona.
- `a8ac7608` feat: `poc` command opens the pi TUI with the planning persona.
- `826b254e` feat: initial pi-poc-racer: race-to-PoC orchestrator with planning, kill-split-redispatch. Version 0.1.0.
