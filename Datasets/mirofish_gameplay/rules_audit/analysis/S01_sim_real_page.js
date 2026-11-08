// S01 — Monte-Carlo playthroughs inside the REAL game page (real game functions: startStage,
// handleSlotClick, executeBossTurn, nudgeColDie, findCaptures, getScores). Only the harness clock is
// changed: the 650 ms boss timeout is executed synchronously, other timers are compressed to 0 ms.
// Player policies: random | greedy | greedy+slide | greedy+slide+nudge.  Output: analysis/sim.json
const fs = require("fs");
const path = require("path");
const L = require("../repros/_lib");
const N = Number(process.env.N || 300);
(async () => {
  const ctx = await L.open({ seed: 4242 });
  const { page } = ctx;
  const res = await page.evaluate(async (N) => {
    const _st = window.setTimeout.bind(window);
    window.setTimeout = (fn, ms, ...a) => { if (fn === executeBossTurn) { fn(); return 0; } return _st(fn, 0, ...a); };
    const rnd = (a) => a[Math.floor(Math.random() * a.length)];
    const owners = () => state.grid.map((row) => row.map((c) => c.owner));
    const empties = () => { const o = []; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) o.push([r, c]); return o; };
    function bestDeploy() {
      let best = [], bc = -1;
      state.hand.forEach((cid, i) => empties().forEach(([r, c]) => {
        const f = findCaptures(r, c, getCardEffectiveStats(cid, c, false), "player").length;
        if (f > bc) { bc = f; best = [[i, r, c]]; } else if (f === bc) best.push([i, r, c]);
      }));
      return { count: bc, pick: rnd(best) };
    }
    function bestSlide() {
      let best = null, bc = 0;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        if (!(cell.cardId && cell.owner === "player")) continue;
        for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
          const nr = r + dr, nc = c + dc;
          if (nr < 0 || nr > 2 || nc < 0 || nc > 2 || state.grid[nr][nc].cardId) continue;
          const f = findCaptures(nr, nc, getCardEffectiveStats(cell.cardId, nc, false), "player").length;
          if (f > bc) { bc = f; best = { r, c, nr, nc, captured: cell.cardId.startsWith("e_") }; }
        }
      }
      return best ? { ...best, count: bc } : null;
    }
    function tryNudge() {
      // spend nudges to boost one column if it raises the best immediate capture count
      const base = bestDeploy().count;
      let plan = null;
      for (let c = 0; c < 3; c++) {
        if (state.colDice[c] >= 4) continue;
        const need = 4 - state.colDice[c];
        if (need > state.nudgesLeft) continue;
        let bc = -1;
        state.hand.forEach((cid) => empties().filter(([, cc]) => cc === c).forEach(([r]) => {
          const st = ALL_CARDS[cid].nesw.map((v) => Math.min(9, v + 1));
          bc = Math.max(bc, findCaptures(r, c, st, "player").length);
        }));
        if (bc > base && (!plan || bc > plan.bc)) plan = { c, need, bc };
      }
      if (plan) { for (let k = 0; k < plan.need; k++) nudgeColDie(plan.c); return plan.need; }
      return 0;
    }
    const games = [];
    for (const policy of ["random", "greedy", "greedy+slide", "greedy+slide+nudge"]) {
      for (let stage = 0; stage < 4; stage++) {
        for (let g = 0; g < N; g++) {
          startStage(stage);
          const bossId = STAGES[stage].bossId;
          const bossCardInPlay = state.grid[0][1].cardId === bossId || state.aiPool.includes(bossId);
          const rec = { policy, stage, bossCardInPlay, playerDeploys: 0, bossDeploys: 0, playerFlips: 0, slideFlips: 0, bossFlips: 0, slidesUsed: 0, capturedEnemySlid: 0, nudgesSpent: 0, slideAvailableTurns: 0, turns: 0, lastMover: null };
          let guard = 0;
          while (!state.gameOver && guard++ < 20) {
            rec.turns++;
            if (policy !== "random" && policy !== "greedy") {
              const s = bestSlide();
              if (s) rec.slideAvailableTurns++;
              if (s && s.count > 0) {
                state.selectedBoardSlot = { r: s.r, c: s.c };
                handleSlotClick(s.nr, s.nc);
                rec.slidesUsed++; rec.slideFlips += s.count; if (s.captured) rec.capturedEnemySlid++;
              }
            }
            if (policy === "greedy+slide+nudge") rec.nudgesSpent += tryNudge();
            let i, r, c, pf;
            if (policy === "random") { i = Math.floor(Math.random() * state.hand.length); [r, c] = rnd(empties()); pf = findCaptures(r, c, getCardEffectiveStats(state.hand[i], c, false), "player").length; }
            else { const b = bestDeploy(); [i, r, c] = b.pick; pf = b.count; }
            state.selectedHandIdx = i; state.selectedBoardSlot = null;
            const before = owners();
            const aiBefore = state.aiPool.length;
            handleSlotClick(r, c);
            rec.playerDeploys++; rec.playerFlips += pf;
            if (state.aiPool.length < aiBefore) { rec.bossDeploys++; rec.lastMover = "boss"; } else rec.lastMover = "player";
            const after = owners();
            for (let rr = 0; rr < 3; rr++) for (let cc = 0; cc < 3; cc++) if (before[rr][cc] === "player" && after[rr][cc] === "ai") rec.bossFlips++;
            // player flips that were then re-flipped by the boss in the same call are not double-counted here
          }
          const sc = getScores();
          Object.assign(rec, { blue: sc.blue, red: sc.red, empty: sc.empty, win: sc.blue > sc.red, tie: sc.blue === sc.red, handLeft: state.hand.length, aiPoolLeft: state.aiPool.length });
          games.push(rec);
        }
      }
    }
    window.setTimeout = _st;
    return games;
  }, N);
  const agg = {};
  for (const g of res) {
    const k = `${g.policy}|S${g.stage + 1}`;
    const a = agg[k] || (agg[k] = { policy: g.policy, stage: g.stage + 1, n: 0, wins: 0, ties: 0, blue: 0, red: 0, playerFlips: 0, bossFlips: 0, slideFlips: 0, slidesUsed: 0, capturedEnemySlid: 0, nudgesSpent: 0, bossCardInPlay: 0, handLeft1: 0, lastBoss: 0, playerDeploys: 0, bossDeploys: 0, empty0: 0 });
    a.n++; a.wins += g.win; a.ties += g.tie; a.blue += g.blue; a.red += g.red; a.playerFlips += g.playerFlips; a.bossFlips += g.bossFlips; a.slideFlips += g.slideFlips; a.slidesUsed += g.slidesUsed; a.capturedEnemySlid += g.capturedEnemySlid; a.nudgesSpent += g.nudgesSpent;
    a.bossCardInPlay += g.bossCardInPlay; a.handLeft1 += g.handLeft === 1; a.lastBoss += g.lastMover === "boss"; a.playerDeploys += g.playerDeploys; a.bossDeploys += g.bossDeploys; a.empty0 += g.empty === 0;
  }
  const rows = Object.values(agg).map((a) => ({
    policy: a.policy, stage: a.stage, n: a.n, winPct: +(100 * a.wins / a.n).toFixed(1), ties: a.ties,
    meanBlue: +(a.blue / a.n).toFixed(2), meanRed: +(a.red / a.n).toFixed(2),
    playerFlipsPerGame: +(a.playerFlips / a.n).toFixed(2), slideFlipsPerGame: +(a.slideFlips / a.n).toFixed(2), bossFlipsPerGame: +(a.bossFlips / a.n).toFixed(2),
    slidesPerGame: +(a.slidesUsed / a.n).toFixed(2), capturedEnemySlidPct: a.slidesUsed ? +(100 * a.capturedEnemySlid / a.slidesUsed).toFixed(1) : 0, nudgesPerGame: +(a.nudgesSpent / a.n).toFixed(2),
    bossCardInPlayPct: +(100 * a.bossCardInPlay / a.n).toFixed(1), handLeftOnePct: +(100 * a.handLeft1 / a.n).toFixed(1), bossMovedLastPct: +(100 * a.lastBoss / a.n).toFixed(1),
    playerDeploysPerGame: +(a.playerDeploys / a.n).toFixed(2), bossDeploysPerGame: +(a.bossDeploys / a.n).toFixed(2), boardFullPct: +(100 * a.empty0 / a.n).toFixed(1),
  }));
  const out = { generatedAt: new Date().toISOString(), gamesPerCell: N, totalGames: res.length, pageErrors: ctx.errors, rows };
  fs.writeFileSync(path.join(__dirname, "sim.json"), JSON.stringify(out, null, 2));
  console.table(rows.map((r) => ({ policy: r.policy, S: r.stage, win: r.winPct, ties: r.ties, blue: r.meanBlue, pF: r.playerFlipsPerGame, sF: r.slideFlipsPerGame, bF: r.bossFlipsPerGame, nud: r.nudgesPerGame, bossIn: r.bossCardInPlayPct, hand1: r.handLeftOnePct, bossLast: r.bossMovedLastPct })));
  console.log("pageErrors:", ctx.errors.length, "totalGames:", res.length);
  await ctx.browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
