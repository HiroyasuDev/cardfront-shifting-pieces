// Parallel simulation runner (worker_threads).
// usage: node run.js <suite>   (suites defined below)  -> results/raw/<label>.csv
"use strict";
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const fs = require("fs");
const path = require("path");
const os = require("os");

const RAW = path.join(__dirname, "results", "raw");

function encodeGame(g) {
  // actions: N<col> nudge, R reroll, S<card>:<from>><to>:<flips>, P<card>@<cell>:<flips>, B<card>@<slot>:<flips>
  const parts = [];
  for (const a of g.log) {
    if (a.t === "nudge") parts.push("N" + a.col);
    else if (a.t === "reroll") parts.push("R");
    else if (a.t === "slide") parts.push(`S${a.card}:${a.from}>${a.to}:${a.flips}`);
    else if (a.t === "place") {
      parts.push(`P${a.card}@${a.cell}:${a.flips}`);
      if (a.boss) parts.push(`B${a.boss.card}@${a.boss.slot}:${a.boss.flips}`);
    }
  }
  return [g.label, g.policy, g.stage, g.seed, g.startHand.join("-"), g.opener, g.pool.join("-"), g.blue, g.red, g.win ? 1 : 0,
    parts.join(" "), g.unused.join("-"), g.values.length ? g.values[0].toFixed(6) : ""].join(",");
}
const HEADER = "label,policy,stage,seed,hand,opener,pool,blue,red,win,actions,unused,root_value";

if (!isMainThread) {
  const P = require("./policies");
  parentPort.on("message", (task) => {
    if (task === "exit") process.exit(0);
    const lines = [];
    for (let i = task.from; i < task.to; i++) {
      const seed = task.seedBase + i;
      const g = P.playGame(task.stage, seed, task.policy, task.opts);
      g.label = task.label;
      lines.push(encodeGame(g));
    }
    parentPort.postMessage({ id: task.id, lines });
  });
} else {
  const SUITES = require("./suites");
  const suiteName = process.argv[2] || "main";
  const nWorkers = +(process.env.WORKERS || Math.min(6, os.cpus().length));
  const jobs = SUITES[suiteName]();
  fs.mkdirSync(RAW, { recursive: true });
  const CHUNK = +(process.env.CHUNK || 250);
  const tasks = [];
  const out = {};
  for (const j of jobs) {
    const key = j.label;
    out[key] = out[key] || [];
    for (let f = 0; f < j.n; f += CHUNK) tasks.push({ id: tasks.length, label: j.label, policy: j.policy, stage: j.stage,
      opts: j.opts || {}, seedBase: j.seedBase, from: f, to: Math.min(j.n, f + CHUNK), file: j.file || j.label });
  }
  console.log(`suite ${suiteName}: ${jobs.length} jobs, ${tasks.length} tasks, ${nWorkers} workers`);
  const t0 = Date.now();
  let next = 0, done = 0;
  const files = {};
  const workers = [];
  for (let w = 0; w < nWorkers; w++) {
    const wk = new Worker(__filename);
    workers.push(wk);
    wk.on("message", (msg) => {
      const t = tasks[msg.id];
      (files[t.file] = files[t.file] || []).push(...msg.lines);
      done++;
      if (done % 40 === 0 || done === tasks.length) console.log(`${done}/${tasks.length} tasks  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      if (next < tasks.length) wk.postMessage(tasks[next++]);
      else if (done === tasks.length) finish();
    });
    wk.on("error", (e) => { console.error("worker error", e); process.exit(1); });
  }
  for (const wk of workers) if (next < tasks.length) wk.postMessage(tasks[next++]);
  function finish() {
    for (const [f, lines] of Object.entries(files)) {
      fs.writeFileSync(path.join(RAW, f + ".csv"), HEADER + "\n" + lines.join("\n") + "\n");
    }
    console.log(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${Object.keys(files).length} files`);
    for (const wk of workers) wk.postMessage("exit");
  }
}
