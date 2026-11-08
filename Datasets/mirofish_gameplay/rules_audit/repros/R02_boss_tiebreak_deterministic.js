// R02 — Boss tie-break is NOT random: `bestSlot` is seeded randomly but `bestCount = -1`, so the
// first open slot always overwrites it and ties resolve to the first row-major slot.
// Method: play many games in the real page (player = random legal deploys via handleSlotClick),
// predict the boss choice right before each boss turn, compare with what the boss actually did.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R02_boss_tiebreak_deterministic", "Boss tie-break always picks first row-major slot");
  const ctx = await L.open({ seed: 202 });
  const { page } = ctx;
  const res = await page.evaluate(async () => {
    // time-compress timers (harness only; game logic untouched)
    const _st = window.setTimeout.bind(window);
    window.setTimeout = (fn, ms, ...a) => _st(fn, Math.max(0, (ms || 0) / 50), ...a);
    const sleep = (ms) => new Promise((r) => _st(r, ms));
    const out = { bossTurns: 0, tieTurns: 0, chosenFirstAmongTies: 0, chosenMatchesFirstArgmax: 0, mismatches: [], firstMoveSlots: {} };
    for (let g = 0; g < 120; g++) {
      startStage(g % 4);
      let turn = 0;
      while (!state.gameOver) {
        while (!state.isPlayerTurn && !state.gameOver) await sleep(2);
        if (state.gameOver) break;
        const open = [];
        for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) open.push([r, c]);
        state.selectedHandIdx = Math.floor(Math.random() * state.hand.length);
        state.selectedBoardSlot = null;
        const [pr, pc] = open[Math.floor(Math.random() * open.length)];
        handleSlotClick(pr, pc);
        if (state.gameOver) break;
        // predict boss move now (boss timer has not fired yet)
        const aiId = state.aiPool[state.aiPool.length - 1];
        const cand = [];
        for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) {
          cand.push({ r, c, f: findCaptures(r, c, getCardEffectiveStats(aiId, c, true), "ai").length });
        }
        const max = Math.max(...cand.map((x) => x.f));
        const tied = cand.filter((x) => x.f === max);
        const before = state.grid.map((row) => row.map((x) => x.cardId));
        while (!state.isPlayerTurn && !state.gameOver) await sleep(2);
        let placed = null;
        for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!before[r][c] && state.grid[r][c].cardId === aiId) placed = { r, c };
        if (!placed) continue;
        out.bossTurns++;
        if (turn === 0) { const k = `${placed.r},${placed.c}`; out.firstMoveSlots[k] = (out.firstMoveSlots[k] || 0) + 1; }
        if (placed.r === tied[0].r && placed.c === tied[0].c) out.chosenMatchesFirstArgmax++;
        else out.mismatches.push({ placed, tied });
        if (tied.length > 1) { out.tieTurns++; if (placed.r === tied[0].r && placed.c === tied[0].c) out.chosenFirstAmongTies++; }
        turn++;
      }
    }
    window.setTimeout = _st;
    return out;
  });
  rep.note("result", res);
  rep.check("collected a meaningful sample of boss turns", res.bossTurns >= 300, { bossTurns: res.bossTurns });
  rep.check("ties occurred in a large share of boss turns", res.tieTurns >= 100, { tieTurns: res.tieTurns });
  rep.check("boss ALWAYS chose the first row-major slot among tied best slots (no randomness)",
    res.chosenFirstAmongTies === res.tieTurns, { chosenFirst: res.chosenFirstAmongTies, ties: res.tieTurns });
  rep.check("boss choice == first argmax in 100% of turns", res.chosenMatchesFirstArgmax === res.bossTurns, { mismatches: res.mismatches.slice(0, 3) });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
