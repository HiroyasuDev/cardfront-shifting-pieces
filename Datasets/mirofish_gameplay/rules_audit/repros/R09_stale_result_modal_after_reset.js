// R09 — Game-over modal timer (460 ms) is not cancelled by Reset: pressing Reset right after the final
// boss move shows the PREVIOUS game's result modal on top of a fresh, un-finished board.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R09_stale_result_modal_after_reset", "Old result modal pops over a new game after Reset");
  const ctx = await L.open({ seed: 909 });
  const { page } = ctx;
  await L.setup(page, {
    stage: 0, dice: [4, 2, 5],
    grid: [["A:e_eclipse", "A:e_cryo", "A:e_archon"], ["A:e_reaper", null, "P:h_kai"], ["A:e_titan", null, "P:h_seraph"]],
    hand: ["h_oracle", "h_chronos"], aiPool: ["e_shinobi"],
  });
  await L.clickSlot(page, 1, 1);
  await page.waitForFunction(() => state.gameOver === true, null, { timeout: 3000 }); // boss final move done
  const resetBtn = page.getByRole("button", { name: "↻ Reset" });
  const [bx, by] = await (async () => { const b = await resetBtn.boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; })();
  await page.mouse.click(bx, by);                 // within the 460 ms window
  const r0 = await L.snap(page);
  rep.check("Reset started a fresh game (1 card, gameOver=false, hand 5)", !r0.gameOver && r0.grid.flat().filter(Boolean).length === 1 && r0.hand.length === 5, { gameOver: r0.gameOver, hand: r0.hand.length });
  await page.waitForTimeout(700);
  const r1 = await L.snap(page);
  rep.check("old result modal is now displayed over the fresh board", r1.modalShown && !r1.gameOver, { modalShown: r1.modalShown, title: r1.modalTitle, gameOver: r1.gameOver });
  await page.screenshot({ path: L.OUT + "/R09_stale_modal.png" });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
