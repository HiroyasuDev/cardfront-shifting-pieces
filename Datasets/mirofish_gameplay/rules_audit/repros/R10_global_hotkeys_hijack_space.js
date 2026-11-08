// R10 — Global keydown handler hijacks Space/Enter (and 'r') regardless of focus:
//  (a) after clicking the "Roll All 3D Dice" button, pressing Space (native button activation) instead
//      deploys a hand card at the keyboard-focus tile and ENDS THE TURN (preventDefault blocks the button);
//  (b) pressing 'r' anywhere silently spends a reroll.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R10_global_hotkeys_hijack_space", "Space/Enter/r global hotkeys override focused controls");
  const ctx = await L.open({ seed: 1010 });
  const { page } = ctx;
  const rollBtn = page.locator("button", { hasText: "Roll All 3D Dice" });
  await rollBtn.click();
  const a0 = await L.snap(page);
  const focused = await page.evaluate(() => document.activeElement && document.activeElement.textContent.trim().slice(0, 20));
  rep.check("Roll button clicked: rerolls 2 -> 1 and button has focus", a0.rerollsLeft === 1 && /Roll All/.test(focused), { rerolls: a0.rerollsLeft, focused });
  await page.keyboard.press(" ");
  const a1 = await L.snap(page);
  rep.check("(a) Space did NOT activate the focused button (rerolls still 1)", a1.rerollsLeft === 1, { rerolls: a1.rerollsLeft });
  rep.check("(a) Space deployed hand[0] at focus tile (1,1) and ended the turn", a1.grid[1][1] && a1.grid[1][1].owner === "player" && a1.hand.length === 4 && !a1.isPlayerTurn, { centre: a1.grid[1][1], hand: a1.hand.length });
  await page.waitForFunction(() => state.isPlayerTurn, null, { timeout: 3000 });
  const b0 = await L.snap(page);
  await page.keyboard.press("r");
  const b1 = await L.snap(page);
  rep.check("(b) bare 'r' keypress spent the last reroll and re-rolled all dice", b0.rerollsLeft === 1 && b1.rerollsLeft === 0, { before: b0.rerollsLeft, after: b1.rerollsLeft, dice: [b0.colDice, b1.colDice] });
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
