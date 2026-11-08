// R06 — Real-mouse clicks on an EMPTY slide-target tile can be swallowed by #grid-3x3.
// Observed first while writing R05: with a Blue unit selected, hovering the adjacent "⇄ SLIDE HERE"
// tile makes renderAll() rebuild the grid on every mouseenter/mouseleave; in the preserve-3d board
// the stationary pointer then alternately hit-tests the new .board-slot and its coplanar parent
// #grid-3x3 (mouseover flicker loop) and the click can land on #grid-3x3 (no handler).
// Method: phase 1 = plain deploy hover on fresh boards (control); phase 2 = select unit, hover each
// adjacent slide-target, settle 400 ms, record flicker/elementFromPoint, click, check whether the slide happened.
const L = require("./_lib");
(async () => {
  const rep = L.reporter("R06_empty_tile_click_swallowed", "Clicks on slide-target tiles swallowed by hover re-render / 3D hit-test");
  const ctx = await L.open({ seed: 606 });
  const { page } = ctx;
  await page.evaluate(() => {
    window.__ev = [];
    document.addEventListener("mouseover", (e) => { const s = e.target.closest && e.target.closest(".board-slot"); window.__ev.push(s ? "slot" + s.dataset.r + s.dataset.c : (e.target.id || "other")); }, true);
  });
  const hitAt = (x, y) => page.evaluate(([x, y]) => { const e = document.elementFromPoint(x, y); const s = e && e.closest && e.closest(".board-slot"); return s ? "slot" + s.dataset.r + s.dataset.c : (e && (e.id || e.className)); }, [x, y]);

  async function trial(kind, cam, unit, target, fromPrev) {
    // fresh deterministic board: unit at `unit`, boss card at (0,1) unless unit/target collide
    await L.setup(page, {
      stage: 0, dice: [4, 2, 5],
      grid: [0, 1, 2].map((r) => [0, 1, 2].map((c) => (r === unit[0] && c === unit[1]) ? "P:h_kai" : (r === 0 && c === 1 && !(target[0] === 0 && target[1] === 1)) ? "A:e_eclipse" : null)),
      hand: ["h_oracle", "h_seraph", "h_arbiter", "h_chronos"], aiPool: ["e_cryo", "e_titan", "e_reaper"],
    });
    if (fromPrev) { await page.mouse.move(fromPrev[0], fromPrev[1]); await page.waitForTimeout(300); }
    if (kind === "slide") { await L.clickSlot(page, unit[0], unit[1]); }
    let [x, y] = await L.slotCenter(page, target[0], target[1]);
    await page.mouse.move(x, y, { steps: 6 });
    await page.waitForTimeout(400);
    [x, y] = await L.slotCenter(page, target[0], target[1]);
    await page.evaluate(() => { window.__ev = []; });
    await page.waitForTimeout(250);
    const flicker = await page.evaluate(() => window.__ev.length);
    const hit = await hitAt(x, y);
    const before = await L.snap(page);
    await page.mouse.click(x, y);
    await page.waitForTimeout(60);
    const after = await L.snap(page);
    const ok = kind === "slide"
      ? (after.usedSlide && after.grid[target[0]][target[1]] && after.grid[target[0]][target[1]].id === "h_kai")
      : (after.hand.length === before.hand.length - 1);
    if (!after.isPlayerTurn) await page.waitForFunction(() => state.isPlayerTurn || state.gameOver, null, { timeout: 4000 });
    return { kind, cam, unit, target, selected: before.selectedBoardSlot, hit, flickerEventsIn250ms: flicker, actionHappened: !!ok };
  }

  const trials = [];
  const units = [[2, 0], [1, 1], [2, 2], [1, 0]];
  const adj = (u) => [[-1, 0], [1, 0], [0, -1], [0, 1]].map(([dr, dc]) => [u[0] + dr, u[1] + dc]).filter(([r, c]) => r >= 0 && r < 3 && c >= 0 && c < 3 && !(r === 0 && c === 1));
  for (const cam of ["5,0", "0,0", "14,0"]) {
    await page.selectOption("#camera-select", cam);
    for (const u of units) for (const t of adj(u)) trials.push(await trial("slide", cam, u, t, null));
    for (const u of units) for (const t of adj(u)) trials.push(await trial("deploy", cam, u, t, null));
  }
  const s = (k) => trials.filter((t) => t.kind === k);
  const lost = (k) => s(k).filter((t) => !t.actionHappened);
  const summary = {
    slide: { total: s("slide").length, lost: lost("slide").length, flickering: s("slide").filter((t) => t.flickerEventsIn250ms > 2).length, hitGrid: s("slide").filter((t) => t.hit === "grid-3x3").length },
    deploy: { total: s("deploy").length, lost: lost("deploy").length, flickering: s("deploy").filter((t) => t.flickerEventsIn250ms > 2).length, hitGrid: s("deploy").filter((t) => t.hit === "grid-3x3").length },
  };
  console.log(JSON.stringify(summary));
  rep.note("summary", summary);
  rep.note("trials", trials);
  rep.check("at least one centred real-mouse click on a slide-target tile was swallowed", summary.slide.lost > 0, summary.slide);
  rep.check("every swallowed click hit-tested to #grid-3x3 or sat in a flicker loop", lost("slide").every((t) => t.hit === "grid-3x3" || t.flickerEventsIn250ms > 2), lost("slide").slice(0, 4));
  await rep.finish(ctx);
})().catch((e) => { console.error(e); process.exit(1); });
