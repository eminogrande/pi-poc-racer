# pi-poc-racer

Race-to-proof-of-concept orchestrator for the [pi](https://github.com/earendil-works/pi-coding-agent) coding agent.

You give it a goal. The **general** plans with you tinder-style — rapid yes/no questions, `?` when something needs clarification — then dispatches parallel **workers** (pi subprocesses), watches their token spend and output silence, **kills** anything that thinks too long, splits the task smaller, and redispatches. Unlimited rounds, zero questions mid-run, until the goal is ready to test.

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
| `.racer/INCIDENTS.md` | kill log + lesson per kill |
| `.racer/logs/<task>.jsonl` | raw worker output |

## Knobs (env vars)

| var | default | meaning |
|---|---|---|
| `POC_TOKEN_CEILING` | `100000` | kill a worker past this many total tokens |
| `POC_SILENCE_MS` | `180000` | kill a worker silent this long |

## Built-in skills

Every worker spawns with three system prompts appended, so machine-to-machine and human-to-machine throughput stays maximal:

- **ponytail** — laziest solution that works, deletion over addition
- **caveman** — ultra-compressed output, no filler tokens
- **adhd** — action-first output shaped for fast human decisions

## Rules of the race

1. Only the general spawns agents. Workers report up, never spawn.
2. One shared checkout. Tasks own disjoint files (set in `PLAN.md`).
3. YOLO: workers never ask questions. They decide and move.
4. Unlimited kill-split-redispatch rounds until ready to test.
