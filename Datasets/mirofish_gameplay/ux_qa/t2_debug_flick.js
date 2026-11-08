// T2-debug: why does a 1-step flick never place? Log pointer events + drag state with real mouse input.
const L = require("./lib");
(async () => {
  const browser = await L.launch();
  const { page } = await L.openGame(browser);
  await page.evaluate(() => {
    window.__ev = [];
    ["pointerdown", "pointermove", "pointerup", "click"].forEach((t) => window.addEventListener(t, (e) => window.__ev.push({ t, x: Math.round(e.clientX), y: Math.round(e.clientY), active: drag.active, pending: !!drag.pending, target: drag.target ? [drag.target.r, drag.target.c] : null, ts: Math.round(performance.now()) }), true));
  });
  const out = {};
  for (const steps of [1, 2]) {
    await page.evaluate(() => { startStage(0); window.__ev = []; });
    await page.waitForTimeout(300);
    const s0 = await L.snap(page);
    const [hx, hy] = await L.center(page, L.handSel(2));
    const [tx, ty] = await L.center(page, L.slotSel(1, 1));
    await page.mouse.move(hx, hy);
    await page.mouse.down();
    await page.mouse.move(tx, ty, { steps });
    const mid = await page.evaluate(() => ({ active: drag.active, target: drag.target ? [drag.target.r, drag.target.c] : null, ghost: !!drag.ghost }));
    await page.mouse.up();
    await page.waitForTimeout(400);
    const s1 = await L.snap(page);
    // bubble-phase window listener (game's) ran after our capture listener: log state after events too
    out["steps" + steps] = { mid, placed: s0.hand.length - s1.hand.length, events: await page.evaluate(() => window.__ev) };
  }
  L.writeJSON("t2_debug_flick.json", out);
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
