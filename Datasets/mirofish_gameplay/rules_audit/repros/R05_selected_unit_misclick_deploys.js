// R05 — With a Blue board card selected for a slide, clicking an empty tile that is NOT a legal slide
// target (non-adjacent, or slide already used) silently deploys a hand card and ends the turn,
// even though the hand UI shows no card selected (isSel requires !selectedBoardSlot).
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R05_selected_unit_misclick_deploys", "Mis-click while a board unit is selected deploys from hand");
  const ctx = await L.open({ seed: 505 });
  const { page } = ctx;
  const base = {
    stage: 0, dice: [4, 2, 5],
    grid: [[null, "A:e_eclipse", null], [null, null, null], ["P:h_kai", null, null]],
    hand: ["h_oracle", "h_seraph", "h_arbiter", "h_chronos"],
    aiPool: ["e_cryo", "e_titan", "e_reaper"],
  };
  // A: non-adjacent click
  await L.setup(page, base);
  await L.clickSlot(page, 2, 0);                 // select Kai for a slide
  const a1 = await L.snap(page);
  const selectedHandUi = await page.locator("#hand-bar .hand-card-wrap.selected").count();
  rep.check("A: Kai selected as slide unit; no hand card shows as selected", a1.selectedBoardSlot && selectedHandUi === 0, { sel: a1.selectedBoardSlot, selectedHandUi });
  await L.clickSlot(page, 0, 2);                 // far tile: not a slide target
  const a2 = await L.snap(page);
  rep.check("A: a hand card (oracle) was deployed at (0,2) and the turn ended", a2.grid[0][2] && a2.grid[0][2].id === "h_oracle" && a2.hand.length === 3 && !a2.isPlayerTurn, { cell: a2.grid[0][2], hand: a2.hand.length });
  rep.check("A: Kai did not move", a2.grid[2][0] && a2.grid[2][0].id === "h_kai");
  await page.waitForTimeout(1000);

  // B: slide already used, select a unit, click an adjacent tile
  await L.setup(page, base);
  await L.clickSlot(page, 2, 0);
  // NOTE: clicking the exact tile centre here is intermittently swallowed by #grid-3x3 (see R06),
  // so the *legal* first slide is performed with the keyboard path: focus (1,0) and press Enter.
  await page.evaluate(() => { state.focusedSlotIndex = 6; });
  await page.keyboard.press("ArrowUp");   // focus (1,0)
  await page.keyboard.press("Enter");     // slide Kai (selected by the click above) to (1,0)
  const b1 = await L.snap(page);
  rep.check("B: first slide worked, usedSlide=true", b1.usedSlide && b1.grid[1][0] && b1.grid[1][0].id === "h_kai", { usedSlide: b1.usedSlide, sel: b1.selectedBoardSlot, grid: b1.grid, turn: b1.isPlayerTurn });
  await L.clickSlot(page, 1, 0);                 // select Kai again
  const bSel = await L.snap(page);
  rep.check("B: Kai re-selected as unit (selectedBoardSlot=(1,0)) although slide is spent", bSel.selectedBoardSlot && bSel.selectedBoardSlot.r === 1 && bSel.selectedBoardSlot.c === 0, bSel.selectedBoardSlot);
  await L.clickSlot(page, 1, 1);                 // adjacent tile; slide spent
  const b2 = await L.snap(page);
  rep.check("B: instead of rejecting the 2nd slide, a hand card was deployed at (1,1) and turn ended",
    b2.grid[1][1] && b2.grid[1][1].id === "h_oracle" && !b2.isPlayerTurn, { cell: b2.grid[1][1] });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
