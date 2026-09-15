#!/usr/bin/env node
// pi-poc-racer — race-to-PoC orchestrator. General plans with you (tinder y/n),
// then spawns pi workers, kills over-budget ones, splits, redispatches. YOLO.
import { spawn, execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, appendFileSync, mkdirSync } from "node:fs";
import { createInterface } from "node:readline";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const CWD = process.cwd();
const STATE = join(CWD, ".racer");
mkdirSync(join(STATE, "logs"), { recursive: true });

const TOKEN_CEILING = +(process.env.POC_TOKEN_CEILING || 100_000);
const SILENCE_MS = +(process.env.POC_SILENCE_MS || 180_000);
const PI_MODEL = process.env.POC_PI_MODEL || "kimi-coding/k3";
const WORKER_THINKING = process.env.POC_WORKER_THINKING || "low";

const git = (...a) => { try { return execFileSync("git", a, { cwd: CWD, stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { return ""; } };
const gitTry = (...a) => { try { return { ok: true, out: execFileSync("git", a, { cwd: CWD }).toString().trim() }; } catch (e) { return { ok: false, out: (e.stderr || "").toString().trim() }; } };
const inGit = () => git("rev-parse", "--is-inside-work-tree") === "true";
const commit = msg => { if (inGit() && git("status", "--porcelain")) { git("add", "-A", "--", ".", ":!.racer"); git("commit", "-qm", msg); } };
const deliver = () => {
  if (!inGit() || !git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")) return console.log("no upstream — nothing pushed.");
  if (gitTry("push", "-q").ok) return console.log("pushed to origin.");
  console.log("push rejected — pull --rebase, retry...");
  gitTry("pull", "--rebase", "--autostash", "-q");
  const again = gitTry("push", "-q");
  console.log(again.ok ? "pushed to origin (after rebase)." : `PUSH FAILED — fix manually: ${again.out.slice(-200)}`);
};

const sh = (args, input) => new Promise((res, rej) => {
  const p = spawn("pi", ["-p", "--model", PI_MODEL, ...args], { cwd: CWD });
  let out = "";
  p.stdout.on("data", d => (out += d));
  p.on("close", c => (c === 0 ? res(out) : rej(new Error(`pi exited ${c}: ${out.slice(-300)}`))));
  if (input) p.stdin.write(input);
  p.stdin.end();
});

const prompt = (f, extra) => sh(["--append-system-prompt", join(ROOT, "prompts", f), "--"], String(extra ?? ""));
const jsonBlock = s => JSON.parse(s.match(/```json\s*([\s\S]*?)```/)?.[1] || s.match(/\[[\s\S]*\]|\{[\s\S]*\}/)?.[0]);

const rl = createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(r => rl.question(q, r));

async function plan(goal) {
  console.log(`\n🃏 TINDER PLANNING — y / n / ? + free text\n`);
  const qs = jsonBlock(await prompt("plan-questions.md", goal));
  const answers = [];
  for (const q of qs) {
    const a = (await ask(`  ${q}  [y/n/?] `)).trim();
    if (a.startsWith("?")) answers.push({ q, a: await ask("     clarify: ") });
    else answers.push({ q, a: a.toLowerCase().startsWith("y") ? "y" : "n" });
  }
  const planMd = await prompt("plan-final.md", `GOAL: ${goal}\nANSWERS: ${JSON.stringify(answers)}`);
  writeFileSync(join(STATE, "PLAN.md"), planMd);
  console.log(`\n${planMd}\n`);
  return (await ask(`PLAN OK? [y/n] `)).trim().toLowerCase().startsWith("y");
}

const incident = (task, reason, note) => {
  appendFileSync(join(STATE, "INCIDENTS.md"),
    `\n## ${new Date().toISOString()} ${task.id} — ${reason}\n- task: ${task.title}\n- est: ${task.estTokens}\n- note: ${note}\n- lesson: split smaller next plan\n`);
  console.log(`💥 ${task.id} killed (${reason}) — incident logged, splitting`);
};

function meter(child, task) {
  // ponytail: token field shape of `pi --mode json` not fixed; we grep any
  // totalTokens-ish key. Silence timer is the always-on guard regardless.
  let tokens = 0, lastOut = Date.now(), tail = "";
  child.stdout.on("data", d => {
    lastOut = Date.now();
    const s = d.toString();
    tail = (tail + s).slice(-800);
    task.tokens = tokens;
    task.last = tail.replace(/\s+/g, " ").slice(-120);
    for (const m of s.matchAll(/"totalTokens":(\d+)|"total_tokens":(\d+)/g))
      tokens = Math.max(tokens, +(m[1] || m[2]));
  });
  return { tokens: () => tokens, silentFor: () => Date.now() - lastOut, tail: () => tail };
}

const raceStart = Date.now();
const writeStandings = tasks => writeFileSync(join(STATE, "standings.json"),
  JSON.stringify({ raceElapsedSec: ((Date.now() - raceStart) / 1000) | 0,
    done: [...tasks.values()].filter(t => t.status === "done").length,
    total: tasks.size,
    tasks: Object.fromEntries([...tasks.values()].map(t => [t.id,
      { title: t.title, status: t.status, tokens: t.tokens || 0, last: t.last || "",
        lapSec: t.startedAt ? (((t.endedAt || Date.now()) - t.startedAt) / 1000) | 0 : 0 }])) }, null, 1));

function runWorker(task) {
  return new Promise(resolve => {
    const args = ["-p", "--mode", "json", "--model", `${PI_MODEL}:${WORKER_THINKING}`, "--no-skills", "--no-extensions", "--no-context-files", "--",
      `TASK ${task.id}: ${task.title}\nFILES YOU OWN: ${(task.files || []).join(", ")}\nDONE WHEN: ${task.doneWhen}\nRULES: touch only your files. Smallest change that works, delete over add, no new abstractions, no new dependencies. No questions, decide yourself, YOLO. End with one line: RESULT: <what works now + demo URL or CLI command>.`];
    const child = spawn("pi", args, { cwd: CWD });
    child.stdin.end(); // close stdin: pi waits for EOF before starting — open pipe = worker hangs silent
    const m = meter(child, task);
    const log = join(STATE, "logs", `${task.id}.jsonl`);
    child.stdout.on("data", d => appendFileSync(log, d));
    const tick = setInterval(() => {
      if (m.tokens() > TOKEN_CEILING) return kill("token-ceiling");
      if (m.silentFor() > SILENCE_MS) return kill("silence-timeout");
    }, 5000);
    const kill = reason => { clearInterval(tick); child.kill("SIGKILL"); resolve({ ok: false, reason, tail: m.tail() }); };
    child.on("close", code => { clearInterval(tick); resolve({ ok: code === 0, reason: code === 0 ? null : "crash", tail: m.tail() }); });
    console.log(`🏁 ${task.id} started: ${task.title}`);
  });
}

async function race() {
  const plan = jsonBlock(readFileSync(join(STATE, "PLAN.md"), "utf8"));
  const tasks = new Map(plan.tasks.map(t => [t.id, { ...t, status: "pending" }]));
  const running = new Set();
  while ([...tasks.values()].some(t => t.status === "pending" || t.status === "running")) {
    for (const t of tasks.values()) {
      if (t.status !== "pending" || running.size >= (plan.maxParallel || 3)) continue;
      if (t.dependsOn?.some(d => tasks.get(d)?.status !== "done")) continue;
      t.status = "running"; running.add(t.id); t.startedAt = Date.now(); writeStandings(tasks);
      runWorker(t).then(async r => {
        running.delete(t.id);
        if (r.ok) { t.status = "done"; t.endedAt = Date.now(); commit(`racer(${t.id}): ${t.title}`); console.log(`✅ ${t.id} done`); writeStandings(tasks); return; }
        incident(t, r.reason, r.tail.slice(-200).replace(/\n/g, " "));
        const split = jsonBlock(await prompt("split.md",
          `TASK: ${JSON.stringify(t)}\nREASON: ${r.reason}\nLAST OUTPUT: ${r.tail.slice(-500)}`));
        t.status = "split";
        for (const nt of split) tasks.set(nt.id, { ...nt, status: "pending",
          dependsOn: (nt.dependsOn || []).map(d => (d === t.id ? null : d)).filter(Boolean)
            .concat(t.dependsOn?.filter(d => tasks.get(d)?.status !== "done") || []) });
      });
    }
    await new Promise(r => setTimeout(r, 2000));
    writeStandings(tasks);
    if (!running.size && ![...tasks.values()].some(t => t.status === "pending")) break;
  }
  const total = ((Date.now() - raceStart) / 1000) | 0;
  const laps = [...tasks.values()].filter(t => t.status === "done")
    .map(t => `${t.id}: ${(((t.endedAt - t.startedAt) / 1000) | 0)}s`).join(" | ");
  console.log(`\n🏆 READY TO TEST. RACE TIME: ${(total / 60) | 0}m${total % 60}s. LAPS: ${laps}`);
  deliver();
  console.log(`Logs: .racer/logs/ Incidents: .racer/INCIDENTS.md Standings: .racer/standings.json`);
  rl.close();
}

async function smoke() {
  // pre-race harness check: one tiny worker must exit 0 with parseable tokens.
  const t = { id: "smoke", title: "Reply with exactly: OK. Create no files.", files: [], doneWhen: "worker prints OK", estTokens: 1000 };
  const r = await runWorker(t);
  const tokens = t.tokens || 0;
  if (r.ok && tokens > 0) { console.log(`SMOKE OK — worker alive, metering works (${tokens} tokens)`); process.exit(0); }
  console.error(`SMOKE FAILED — ok=${r.ok} reason=${r.reason} tokens=${tokens}. Do NOT race. Last output: ${r.tail.slice(-200)}`);
  process.exit(1);
}

const [cmd, ...rest] = process.argv.slice(2);
if (cmd === "plan") (await plan(rest.join(" "))) && console.log("run: pi-poc-racer run"), rl.close();
else if (cmd === "smoke") await smoke();
else if (cmd === "run") await race();
else if (cmd) { if (await plan([cmd, ...rest].join(" "))) await race(); else rl.close(); }
else console.log("usage: pi-poc-racer \"<goal>\" | plan \"<goal>\" | run | smoke");
