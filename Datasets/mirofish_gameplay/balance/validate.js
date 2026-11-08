// Cross-validation: the REAL page plays (its own startStage / nudgeColDie / rerollAllDice /
// handleSlotClick / executeBossTurn), with Math.random replaced by the same seeded PRNG the
// headless engine uses. Each action is applied to the page and to a replay engine in lockstep,
// and full state snapshots are compared after every action.
"use strict";
const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");
const E = require("./engine");
const P = require("./policies");

const EXE = "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const PORT = process.env.PORT || 8096;
const URL = `http://127.0.0.1:${PORT}/WebPlayable/cardfront_cradle_of_echoes_playable.html?balance=${Date.now()}`;
const N = +(process.env.N || 160);
const REALTIME = +(process.env.REALTIME || 6);   // matches played with the genuine 650 ms setTimeout path
const OUT = path.join(__dirname, "results");
fs.mkdirSync(OUT, { recursive: true });

const POLS = ["chaos", "greedy_all", "random", "greedy_slide", "greedy_dice", "expert", "lookahead", "greedy", "expert_noslide", "chaos"];

function cellFromRC(i) { return [(i / 3) | 0, i % 3]; }

function diff(a, b, pfx = "") {
  const out = [];
  if (typeof a !== "object" || a === null || typeof b !== "object" || b === null) {
    if (a !== b) out.push(`${pfx}: page=${JSON.stringify(a)} engine=${JSON.stringify(b)}`);
    return out;
  }
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of keys) out.push(...diff(a[k], b[k], pfx ? pfx + "." + k : k));
  return out;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: EXE });
  const page = await browser.newPage({ viewport: { width: 1408, height: 800 } });
  const pageErrors = [];
  page.on("pageerror", e => pageErrors.push(String(e)));
  await page.goto(URL);
  await page.waitForTimeout(800);
  await page.evaluate((src) => {
    window.__mulberry32 = eval("(" + src + ")");
    window.__snap = () => {
      const grid = [];
      let blue = 0, red = 0;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        grid.push(cell.cardId ? [cell.cardId, cell.owner, cell.nesw.slice()] : null);
        if (cell.owner === "player") blue++; else if (cell.owner === "ai") red++;
      }
      return { grid, hand: state.hand.slice(), aiPool: state.aiPool.slice(), colDice: state.colDice.slice(),
        nudgesLeft: state.nudgesLeft, rerollsLeft: state.rerollsLeft, usedSlide: state.usedSlideThisTurn,
        isPlayerTurn: state.isPlayerTurn, gameOver: state.gameOver, blue, red };
    };
    window.__init = (seed, stage) => {
      document.getElementById("result-modal").style.display = "none";
      window.__rngCalls = 0;
      const g = window.__mulberry32(seed);
      Math.random = () => { window.__rngCalls++; return g(); };
      startStage(stage);
      return window.__snap();
    };
    // Apply one action through the page's own handlers. Boss turn: the 650 ms setTimeout is captured
    // and executeBossTurn is invoked synchronously; other timers are re-scheduled normally.
    window.__act = (a, realtime) => {
      if (a.t === "nudge") nudgeColDie(a.col);
      else if (a.t === "reroll") rerollAllDice();
      else if (a.t === "slide") {
        state.selectedBoardSlot = null;
        handleSlotClick(a.fr, a.fc);
        handleSlotClick(a.tr, a.tc);
      } else if (a.t === "place") {
        state.selectedBoardSlot = null;
        state.selectedHandIdx = a.hi;
        if (realtime) { handleSlotClick(a.r, a.c); return null; }
        const orig = window.setTimeout, q = [];
        window.setTimeout = (fn, ms) => { q.push([fn, ms]); return 0; };
        try { handleSlotClick(a.r, a.c); } finally { window.setTimeout = orig; }
        for (const [fn, ms] of q) { if (fn === executeBossTurn) executeBossTurn(); else orig(fn, ms); }
      }
      return window.__snap();
    };
  }, E.MULBERRY_SRC);

  const results = [];
  let totalActions = 0, agreeActions = 0;
  const t0 = Date.now();
  for (let m = 0; m < N + REALTIME; m++) {
    const realtime = m >= N;
    const stage = m % 4;
    const seed = 777000 + m * 7919;
    const pk = POLS[m % POLS.length];
    // decision engine (policy runs here) and replay engine (lockstep with page)
    const s = E.newGame(stage, E.mulberry32(seed));
    const r = E.newGame(stage, E.mulberry32(seed));
    const prng = E.mulberry32((seed ^ 0x9E3779B9) >>> 0);
    const rec = { match: m, seed, stage, policy: pk, realtime, actions: 0, mismatches: [], final: null };
    const p0 = await page.evaluate(([sd, st]) => window.__init(sd, st), [seed, stage]);
    const d0 = diff(p0, E.snapshot(r));
    if (d0.length) rec.mismatches.push({ step: "init", diffs: d0 });
    let guard = 0;
    while (!s.gameOver && guard++ < 10) {
      const log = [];
      P.POLICIES[pk].turn(s, prng, log);
      for (const a of log) {
        let pa;
        if (a.t === "nudge") { E.nudge(r, a.col); pa = { t: "nudge", col: a.col }; }
        else if (a.t === "reroll") { E.reroll(r); pa = { t: "reroll" }; }
        else if (a.t === "slide") { E.slide(r, a.from, a.to); const [fr, fc] = cellFromRC(a.from), [tr, tc] = cellFromRC(a.to); pa = { t: "slide", fr, fc, tr, tc }; }
        else if (a.t === "place") { const hi = r.hand.indexOf(a.card); E.place(r, hi, a.cell); const [rr, cc] = cellFromRC(a.cell); pa = { t: "place", hi, r: rr, c: cc }; }
        let ps = await page.evaluate(([x, rt]) => window.__act(x, rt), [pa, realtime]);
        if (realtime && a.t === "place") {
          // wait for the genuine 650 ms boss timer
          await page.waitForFunction(() => state.isPlayerTurn || state.gameOver, null, { timeout: 5000 });
          await page.waitForTimeout(50);
          ps = await page.evaluate(() => window.__snap());
        }
        const es = E.snapshot(r);
        const d = diff(ps, es);
        totalActions++; rec.actions++;
        if (d.length) rec.mismatches.push({ step: rec.actions, action: a, diffs: d.slice(0, 12) });
        else agreeActions++;
      }
    }
    const es = E.snapshot(r), ss = E.snapshot(s);
    rec.final = { blue: es.blue, red: es.red, win: r.win };
    rec.policyEngineAgrees = JSON.stringify(es) === JSON.stringify(ss);
    if (realtime) {
      await page.waitForTimeout(700);
      rec.modalTitle = await page.evaluate(() => document.getElementById("modal-title").textContent);
      const expect = r.win ? `VICTORY (${es.blue} – ${es.red})` : `DEFEAT (${es.blue} – ${es.red})`;
      rec.modalMatches = rec.modalTitle.includes(expect);
    }
    rec.rngCallsPage = await page.evaluate(() => window.__rngCalls);
    rec.ok = rec.mismatches.length === 0 && rec.policyEngineAgrees && (rec.modalMatches !== false);
    results.push(rec);
    if (m % 20 === 0) console.log(`match ${m} stage ${stage} ${pk} ok=${rec.ok} ${es.blue}-${es.red}`);
  }
  const okMatches = results.filter(x => x.ok).length;
  const summary = {
    url: URL, matches: results.length, syncMatches: N, realtimeMatches: REALTIME,
    matchAgreementPct: +(100 * okMatches / results.length).toFixed(3),
    actionsCompared: totalActions, actionAgreementPct: +(100 * agreeActions / totalActions).toFixed(3),
    finalScoreAgreementPct: +(100 * results.filter(x => !x.mismatches.some(mm => mm.step === x.actions)).length / results.length).toFixed(3),
    byPolicy: {}, byStage: {}, pageErrors, divergent: results.filter(x => !x.ok).slice(0, 20),
    actionTypeCounts: {}, seconds: (Date.now() - t0) / 1000,
  };
  for (const x of results) {
    summary.byPolicy[x.policy] = summary.byPolicy[x.policy] || { n: 0, ok: 0 };
    summary.byPolicy[x.policy].n++; if (x.ok) summary.byPolicy[x.policy].ok++;
    summary.byStage[x.stage] = summary.byStage[x.stage] || { n: 0, ok: 0, wins: 0 };
    summary.byStage[x.stage].n++; if (x.ok) summary.byStage[x.stage].ok++; if (x.final.win) summary.byStage[x.stage].wins++;
  }
  fs.writeFileSync(path.join(OUT, "validation_summary.json"), JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(OUT, "validation_matches.json"), JSON.stringify(results, null, 1));
  console.log(JSON.stringify({ matches: summary.matches, matchAgreementPct: summary.matchAgreementPct, actionsCompared: totalActions,
    actionAgreementPct: summary.actionAgreementPct, pageErrors: pageErrors.length, seconds: summary.seconds, byPolicy: summary.byPolicy }, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
