// R03 — Drag state survives a turn: start a real-mouse drag of hand card #5, press Enter (keyboard
// deploy ends the turn), wait for the boss, then release on an empty tile. onDragPointerUp restores
// the stale handIdx (4) into a 4-card hand -> handleSlotClick writes cardId=undefined/owner="player"
// into the cell, then throws a TypeError. The phantom cell counts as a Blue point.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R03_stale_hand_drag_undefined_card", "Stale hand-drag drop after keyboard deploy corrupts board");
  const ctx = await L.open({ seed: 303 });
  const { page } = ctx;
  const s0 = await L.snap(page);
  rep.note("startHand", s0.hand);

  const [hx, hy] = await L.handCenter(page, 4);
  const [mx, my] = await L.slotCenter(page, 2, 0);
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move((hx + mx) / 2, (hy + my) / 2, { steps: 12 }); // past 6px threshold, ghost active
  const dragging = await L.snap(page);
  rep.check("drag ghost is active with hand card #5", dragging.ghost && dragging.selectedHandIdx === 4);

  await page.keyboard.press("Enter");          // keyboard deploys selected card at focused slot (1,1)
  const afterEnter = await L.snap(page);
  rep.check("Enter deployed a card mid-drag and ended the turn", afterEnter.hand.length === 4 && !afterEnter.isPlayerTurn,
    { hand: afterEnter.hand.length, centre: afterEnter.grid[1][1] });
  await page.waitForTimeout(1100);             // boss turn resolves while mouse is still held
  const afterBoss = await L.snap(page);
  rep.check("boss moved; player turn again; ghost still alive", afterBoss.isPlayerTurn && afterBoss.ghost);

  // pick an empty tile and release on it
  const empty = await page.evaluate(() => { for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) return [r, c]; });
  const [ex, ey] = await L.slotCenter(page, empty[0], empty[1]);
  await page.mouse.move(ex, ey, { steps: 15 });
  await page.waitForTimeout(150);
  await page.mouse.up();
  await page.waitForTimeout(500);
  const end = await L.snap(page);
  const cell = end.grid[empty[0]][empty[1]];
  rep.check("TypeError thrown by getCardEffectiveStats(undefined)", ctx.errors.some((e) => /nesw|undefined/i.test(e)), ctx.errors);
  rep.check("target cell now has cardId=undefined but owner='player' (phantom)", cell && cell.id === "<undefined>" && cell.owner === "player", cell);
  const realBlue = end.grid.flat().filter((c) => c && c.owner === "player" && c.id !== "<undefined>").length;
  rep.check("getScores counts the phantom as an extra Blue point", end.scores.blue === realBlue + 1, { scoresBlue: end.scores.blue, realBlueCards: realBlue });
  rep.check("player still holds the turn after the exception (turn never ended)", end.isPlayerTurn === true);
  // Scoreboard DOM was not re-rendered by the throwing call; force a render to show the inflated score
  await page.evaluate(() => renderAll());
  const end2 = await L.snap(page);
  rep.check("after the next render the scoreboard shows the inflated Blue score", Number(end2.domScore.you) === realBlue + 1, end2.domScore);
  await page.screenshot({ path: L.OUT + "/R03_phantom_cell.png" });
  rep.note("endSnapshot", end2);
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
