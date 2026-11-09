// R08 — End-of-stage flow:
//  (a) "Next Stage ▶" is offered and works after a DEFEAT (no progression gate);
//  (b) from Stage 4 it wraps to Stage 1 (no campaign end);
//  (c) the turn badge reads "YOUR TURN" on the final board (isPlayerTurn set true before checkGameOver);
//  (d) the game always ends on the BOSS's move with 1 hero card still in hand.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R08_next_stage_after_defeat_wraps", "Next Stage after defeat, 4->1 wrap, end-state badge");
  const ctx = await L.open({ seed: 808 });
  const { page } = ctx;
  await L.setup(page, {
    stage: 3, dice: [4, 2, 5],
    grid: [
      ["A:e_eclipse", "A:e_cryo", "A:e_archon"],
      ["A:e_reaper", null, "P:h_kai"],
      ["A:e_titan", null, "P:h_seraph"],
    ],
    hand: ["h_oracle", "h_chronos"], aiPool: ["e_shinobi"],
  });
  await page.evaluate(() => { document.getElementById("stage-select").value = "3"; });
  await L.clickSlot(page, 1, 1);                       // player's last deploy (8th card)
  const p = await L.snap(page);
  rep.check("player deploy did not end the game (board 8/9)", !p.gameOver && p.scores.empty === 1, p.scores);
  await page.waitForSelector("#result-modal", { state: "visible", timeout: 4000 });
  const end = await L.snap(page);
  rep.check("(d) game ended on the boss's 9th card with 1 hero left unused in hand", end.gameOver && end.scores.empty === 0 && end.hand.length === 1, { hand: end.hand, scores: end.scores });
  rep.check("result is a DEFEAT", /DEFEAT/.test(end.modalTitle), end.modalTitle);
  rep.check("(c) turn badge says YOUR TURN on the finished board", end.turnBadge === "YOUR TURN", end.turnBadge);
  const nextVisible = await page.getByRole("button", { name: "Next Stage ▶" }).isVisible();
  rep.check("(a) 'Next Stage ▶' button is visible on the DEFEAT modal", nextVisible);
  await page.screenshot({ path: L.OUT + "/R08_defeat_modal_next_stage.png" });
  if (nextVisible) await page.getByRole("button", { name: "Next Stage ▶" }).click();
  else await page.evaluate(() => closeModal(false));
  await page.waitForTimeout(250);
  const n = await L.snap(page);
  const sel = await page.$eval("#stage-select", (e) => e.value);
  rep.check("(a)+(b) after losing Stage 4, Next Stage starts Stage 1 (index 0)", n.stageIndex === 0 && sel === "0" && !n.modalShown, { stageIndex: n.stageIndex, select: sel });
  // (a) also from a mid stage: lose stage 1 -> next goes to stage 2
  await L.setup(page, {
    stage: 0, dice: [1, 2, 1],
    grid: [["A:e_eclipse", "A:e_cryo", "A:e_archon"], ["A:e_reaper", null, "P:h_kai"], ["A:e_titan", null, "P:h_seraph"]],
    hand: ["h_valkyrie", "h_chronos"], aiPool: ["e_shinobi"],
  });
  await L.clickSlot(page, 1, 1);
  await page.waitForSelector("#result-modal", { state: "visible", timeout: 4000 });
  const e2 = await L.snap(page);
  const nextVisible2 = await page.getByRole("button", { name: "Next Stage ▶" }).isVisible();
  if (nextVisible2) await page.getByRole("button", { name: "Next Stage ▶" }).click();
  else await page.evaluate(() => closeModal(false));
  await page.waitForTimeout(250);
  const n2 = await L.snap(page);
  rep.check("(a) losing Stage 1 still advances to Stage 2", /DEFEAT/.test(e2.modalTitle) && n2.stageIndex === 1, { title: e2.modalTitle, stageIndex: n2.stageIndex });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
