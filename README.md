# pi-poc-racer

Race-to-proof-of-concept orchestrator for the [pi](https://github.com/earendil-works/pi-coding-agent) coding agent.

You give it a goal. The **Clerk of the Course** 🏁 plans with you tinder-style — rapid yes/no questions, `?` when something needs clarification — then dispatches parallel **workers** (pi subprocesses) onto the track, commentates live from `.racer/standings.json` (excitement rising toward the finish, podium with lap times at the end), **kills** anything that thinks too long, splits the task smaller, and redispatches. Unlimited rounds, zero questions mid-run, until the goal is ready to test.

No tests get written. "Done" means: a demo you can click, or a CLI that prints the result/state.

Spawned from ideas in [pi-messenger-swarm](https://github.com/monotykamary/pi-messenger-swarm) (task board, `pi --mode json` spawning), rebuilt as a standalone zero-dependency CLI so the constraints live in code, not in LLM discipline.

## How it works

```mermaid
flowchart TD
    A[you: pi-poc-racer "goal"] --> B[GENERAL: planning session]
    B --> C{tinder questions}
    C -->|y / n| C
    C -->|? + free text| C
    C --> D[PLAN.md: tasks, deps, estTokens, maxParallel]
    D --> E{you approve plan?}
    E -->|n| B
    E -->|y| F[race loop]

    subgraph RACE[race loop — plain Node code, no LLM]
        F --> G[spawn ready tasks<br/>pi -p --mode json<br/>+ ponytail/caveman/adhd skills]
        G --> H{meter every 5s}
        H -->|tokens > 100k| I[KILL]
        H -->|silent > 3min| I
        H -->|exit 0| J[task done ✅]
        I --> K[INCIDENTS.md entry]
        K --> L[GENERAL splits task smaller]
        L --> F
    end

    J --> M{pending tasks left?}
    M -->|yes| F
    M -->|no| N[🏆 READY TO TEST]
```

## Why tokens and not time

A token ceiling measures **plan granularity**: a task that needs more than ~100k tokens was not split small enough — that is a planning failure, so the general splits it and writes an incident report to plan better next round.

A silence timeout (no output for 3 minutes) measures **stuckness**: a hung process burns zero tokens and would never trip a token budget. You need both meters.

## Install & use

```bash
npm link            # from this repo; requires pi CLI installed + authed
pi-poc-racer "build a generative UI that renders MCP tools as forms"
```

State lives in `.racer/` of the project you run it in:

| file | what |
|---|---|
| `.racer/PLAN.md` | the agreed plan |
| `.racer/standings.json` | live race standings: task status, tokens, lap times |
| `.racer/INCIDENTS.md` | kill log + lesson per kill |
| `.racer/logs/<task>.jsonl` | raw worker output |

## Steering mid-race

Write commands to `.racer/STEER.md` anytime (the Clerk does this when you type `steer …` in the TUI). The race loop consumes them every few seconds:

| command | effect |
|---|---|
| `kill t3` | kill worker, split task smaller, redispatch |
| `drop t3` | kill/cancel task, no replacement |
| `note t3 use radio not dropdown` | team order, reaches (re)spawned worker prompt |
| `pause` / `resume` | stop/start new dispatches (running cars finish) |

The Clerk never polls and never blocks: every message you type is answered in ≤2 lines from `.racer/race.log`.

## Knobs (env vars)

| var | default | meaning |
|---|---|---|
| `POC_TOKEN_CEILING` | `100000` | kill a worker past this many total tokens |
| `POC_SILENCE_MS` | `180000` | kill a worker silent this long |
| `POC_PI_MODEL` | `kimi-coding/k3` | model for workers + planner calls |
| `POC_WORKER_THINKING` | `low` | thinking level for workers (`off`/`minimal`/`low`/`medium`/`high`) |
| `POC_CLERK_MODEL` | `kimi-coding/k3:medium` | model + thinking for the Clerk TUI |

## Clean-room TUI

`poc` starts pi with `--no-skills --no-extensions --no-context-files --no-prompt-templates` and `quietStartup`: no startup dumps, no global config, no surprise context. The only system prompt is the Clerk. Workers run the same clean room — skill personas were measured and cut: ~6k tokens per worker spawn for zero behavioral gain. The two rules that survived live in the worker prompt itself: smallest change that works, no new dependencies.

## Commit policy

The CLI commits after every finished task (`racer(t3): <title>`) and pushes exactly once: at `READY TO TEST`, and only if the branch has an upstream. Many commits, one push, zero noise mid-race.

## Rules of the race

1. Only the general spawns agents. Workers report up, never spawn.
2. One shared checkout. Tasks own disjoint files (set in `PLAN.md`).
3. YOLO: workers never ask questions. They decide and move.
4. Unlimited kill-split-redispatch rounds until ready to test.
