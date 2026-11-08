// R01 — Reset / stage-select while the boss setTimeout(650) is pending: the stale boss turn
// executes on the NEW board (free extra boss card, nudges bumped to 3), and two stale timers
// give the boss two consecutive moves.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R01_stale_boss_turn_after_reset", "Pending boss turn survives Reset/stage-select");
  const ctx = await L.open({ seed: 101 });
  const { page } = ctx;

  // --- A: Reset button ---
  await L.clickSlot(page, 1, 1);                  // real click: deploy hand[0] to centre
  const afterPlace = await L.snap(page);
  rep.check("A: placement ended the player turn", afterPlace.isPlayerTurn === false);
  await page.getByRole("button", { name: "↻ Reset" }).click();  // within the 650 ms window
  const afterReset = await L.snap(page);
  const fresh = afterReset.grid.flat().filter(Boolean).length;
  rep.check("A: fresh board right after Reset has 1 card (boss pre-place)", fresh === 1, { cards: fresh });
  await page.waitForTimeout(1000);
  const later = await L.snap(page);
  const redCount = later.scores.red;
  rep.check("A: stale boss turn placed an extra red card on the NEW board with no player move", redCount === 2 && later.hand.length === 5, { red: redCount, hand: later.hand.length });
  rep.check("A: nudges bumped above the stage-start value of 2", later.nudgesLeft === 3, { nudgesLeft: later.nudgesLeft });
  rep.check("A: aiPool shrank on new board (5 -> 4)", later.aiPool.length === 4, { aiPool: later.aiPool.length });

  // --- B: stage-select dropdown, then double stale timers => boss double move ---
  await page.evaluate(() => startStage(0));
  await page.waitForTimeout(200);
  await L.clickSlot(page, 2, 0);
  await page.selectOption("#stage-select", "2");  // stale timer #1 pending, board replaced by stage 3
  await page.waitForTimeout(60);
  await L.clickSlot(page, 2, 2);                  // player moves on the new stage -> timer #2 pending
  const mid = await L.snap(page);
  await page.waitForTimeout(1200);
  const end = await L.snap(page);
  rep.check("B: stage changed to index 2", end.stageIndex === 2);
  rep.check("B: after ONE player move the boss has placed TWO cards (1 pre-place + 2 = 3 red-placed cards)",
    end.aiPool.length === 3, { aiPoolAfter: end.aiPool.length, gridAfter: end.grid });
  rep.check("B: it is the player's turn and slide reset, i.e. the double move was silent", end.isPlayerTurn === true);
  rep.note("midSnapshot", mid);
  rep.note("endSnapshot", end);
  await page.screenshot({ path: L.OUT + "/R01_after_double_boss_move.png" });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
