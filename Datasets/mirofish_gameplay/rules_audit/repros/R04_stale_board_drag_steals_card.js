// R04 — Stale BOARD drag: start a slide-drag of a Blue board card, press Enter to deploy from hand
// (turn ends), let the boss CAPTURE the dragged card, then release next to it. The slide branch of
// handleSlotClick never re-checks that the source is still the player's, so the boss-owned card is
// moved AND converted to Blue ("steal"). Board is set up deterministically via state, actions are
// real mouse + keyboard.
// Part B: same stale-drag pattern with a low hand index -> a DIFFERENT card than the dragged one is placed.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R04_stale_board_drag_steals_card", "Stale slide-drag moves & converts a boss-captured card");
  const ctx = await L.open({ seed: 404 });
  const { page } = ctx;
  await L.setup(page, {
    stage: 0, dice: [1, 2, 5],
    grid: [
      [null, "A:e_eclipse", "A:e_cryo"],
      ["P:h_phoenix", "A:e_archon", "A:e_shinobi"],
      [null, "A:e_reaper", null],
    ],
    hand: ["h_oracle", "h_kai", "h_seraph", "h_chronos"],
    aiPool: ["e_titan"],
    focus: 4,
  });
  const s0 = await L.snap(page);
  rep.check("setup: phoenix (1,0) is Blue with S edge 5", s0.grid[1][0].owner === "player" && s0.grid[1][0].nesw[2] === 5, s0.grid[1][0]);

  const [ax, ay] = await L.slotCenter(page, 1, 0);
  const [bx, by] = await L.slotCenter(page, 0, 0);
  await page.mouse.move(ax, ay);
  await page.mouse.down();
  await page.mouse.move(ax + 4, ay - 30, { steps: 8 });
  const d = await L.snap(page);
  rep.check("slide drag active, selectedBoardSlot=(1,0)", d.ghost && d.selectedBoardSlot && d.selectedBoardSlot.r === 1 && d.selectedBoardSlot.c === 0);
  await page.keyboard.press("ArrowDown");   // focus (2,1)
  await page.keyboard.press("ArrowRight");  // focus (2,2)
  await page.keyboard.press("Enter");       // deploy hand[0] at (2,2) -> boss turn
  const e1 = await L.snap(page);
  rep.check("Enter deployed oracle at (2,2) mid-drag", e1.grid[2][2] && e1.grid[2][2].id === "h_oracle" && !e1.isPlayerTurn, e1.grid[2][2]);
  await page.waitForTimeout(1100);
  const e2 = await L.snap(page);
  rep.check("boss (titan N7 > phoenix S5) captured the dragged phoenix", e2.grid[1][0].owner === "ai" && e2.grid[2][0] && e2.grid[2][0].id === "e_titan", { p: e2.grid[1][0], titan: e2.grid[2][0] });
  const redBefore = e2.scores.red, blueBefore = e2.scores.blue;

  await page.mouse.move(bx, by, { steps: 15 });
  await page.waitForTimeout(150);
  await page.mouse.up();
  await page.waitForTimeout(500);
  const e3 = await L.snap(page);
  rep.check("boss-owned phoenix was slid to (0,0) and is now Blue", e3.grid[0][0] && e3.grid[0][0].id === "h_phoenix" && e3.grid[0][0].owner === "player" && !e3.grid[1][0], { "00": e3.grid[0][0], "10": e3.grid[1][0] });
  rep.check("score swung: stolen phoenix (+1/-1) plus a slide capture it then made", e3.scores.blue >= blueBefore + 1 && e3.scores.red <= redBefore - 1,
    { before: { blueBefore, redBefore }, after: e3.scores });
  rep.note("snapshots", { e2, e3 });
  await page.screenshot({ path: L.OUT + "/R04_stolen_card.png" });

  // ---- Part B: wrong card placed (stale handIdx 0 after a keyboard deploy) ----
  await page.evaluate(() => startStage(0));
  await page.waitForTimeout(200);
  const h = (await L.snap(page)).hand;
  const [hx, hy] = await L.handCenter(page, 0);
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move(hx + 60, hy - 40, { steps: 10 });
  await page.keyboard.press("Enter");       // deploys hand[0] (=dragged card) at (1,1)
  await page.waitForTimeout(1100);
  const empty = await page.evaluate(() => { for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) return [r, c]; });
  const [ex, ey] = await L.slotCenter(page, empty[0], empty[1]);
  await page.mouse.move(ex, ey, { steps: 15 });
  await page.waitForTimeout(120);
  await page.mouse.up();
  await page.waitForTimeout(400);
  const b = await L.snap(page);
  const placedB = b.grid[empty[0]][empty[1]];
  rep.check("B: dropping the (already deployed) dragged card places a different hand card instead", placedB && placedB.id === h[1] && h[0] !== h[1], { dragged: h[0], placed: placedB });
  rep.check("B: hand 5 -> 3 (turn-2 deploy happened, but with a card the player never dragged)", b.hand.length === 3, { hand: b.hand.length });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
