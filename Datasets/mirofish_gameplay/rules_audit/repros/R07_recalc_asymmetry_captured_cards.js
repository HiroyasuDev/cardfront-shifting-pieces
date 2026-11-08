// R07 — Stat recalculation asymmetry after a dice change (recalcBoardStats only touches owner==="player"):
//  (a) a boss card captured by the player is re-statted with the PLAYER formula -> loses its aiBonus
//      (stage 3/4) the moment any die is nudged/rerolled (captured cards also never get stats on flip);
//  (b) a hero captured by the boss keeps its stale column boost forever, even when the column die
//      drops below 4, while the player's own heroes in that column lose it.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R07_recalc_asymmetry_captured_cards", "Captured cards re-statted inconsistently on dice change");
  const ctx = await L.open({ seed: 707 });
  const { page } = ctx;
  await L.setup(page, {
    stage: 2, dice: [6, 2, 5],
    grid: [
      [{ id: "h_oracle", owner: "ai", nesw: [8, 8, 9, 8] }, "A:e_eclipse", null],
      [null, { id: "e_titan", owner: "player", nesw: [8, 6, 8, 7] }, null],
      ["P:h_kai", null, null],
    ],
    hand: ["h_seraph", "h_arbiter", "h_chronos"], aiPool: ["e_cryo", "e_reaper"], nudges: 2,
  });
  const s0 = await L.snap(page);
  rep.check("setup: stage 3 (aiBonus 1), col0 die=6 boosted; boss-held oracle shows boosted [8,8,9,8]", s0.stageIndex === 2 && s0.grid[0][0].nesw.join() === "8,8,9,8");
  rep.check("setup: player-captured titan shows its stage stats [8,6,8,7] (base 7,5,7,6 + aiBonus)", s0.grid[1][1].nesw.join() === "8,6,8,7");
  rep.check("setup: player Kai in col0 boosted [8,9,7,8]", s0.grid[2][0].nesw.join() === "8,9,7,8");

  // real click on the Column 1 die: 6 -> 1 (wraps), drops the boost
  await page.locator("#dice-column-list .col-die-row >> nth=0").click();
  await page.waitForTimeout(150);
  const s1 = await L.snap(page);
  rep.check("nudge wrapped col0 die 6 -> 1 (boost removed) and consumed a nudge", s1.colDice[0] === 1 && s1.nudgesLeft === 1, { dice: s1.colDice, nudges: s1.nudgesLeft });
  rep.check("player's own Kai lost the boost -> [7,8,6,7]", s1.grid[2][0].nesw.join() === "7,8,6,7", s1.grid[2][0].nesw);
  rep.check("(b) boss-held oracle in the SAME column keeps the stale boost [8,8,9,8]", s1.grid[0][0].nesw.join() === "8,8,9,8", s1.grid[0][0].nesw);
  rep.check("(a) player-captured titan (col1, die 2, untouched) silently dropped to base [7,5,7,6] = lost aiBonus", s1.grid[1][1].nesw.join() === "7,5,7,6", s1.grid[1][1].nesw);
  const dom = await page.evaluate(() => [...document.querySelectorAll('#grid-3x3 .board-slot[data-r="1"][data-c="1"] .edge-num')].map((e) => e.textContent).join());
  rep.check("UI edge numbers for titan changed to 7,5,7,6 without any titan-related action", dom === "7,5,7,6", dom);
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
