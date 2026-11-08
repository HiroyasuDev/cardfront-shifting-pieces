// T3b: Probe (a) what element is actually hit at tile centre/corners per viewport (3D-transform hit-testing),
// (b) real-mouse click-to-place on every empty tile centre, (c) layout shift of the right panel as the
// telegraph HUD text changes when hovering different hand cards.
const L = require("./lib");
const VPS = [[1024, 768], [1280, 720], [1280, 800], [1440, 900], [1920, 1080], [1180, 820]];

(async () => {
  const browser = await L.launch();
  const out = [];
  for (const [w, h] of VPS) {
    const { page, context } = await L.openGame(browser, { viewport: { width: w, height: h } });
    await page.mouse.move(2, h - 2);
    await page.waitForTimeout(300);
    const hits = await page.evaluate(() => {
      const desc = (el) => { if (!el) return "null"; const s = el.closest(".board-slot"); return (el.className && typeof el.className === "string" ? el.tagName + "." + el.className.split(" ").join(".") : el.tagName) + (s ? ` in slot(${s.dataset.r},${s.dataset.c})` : ""); };
      return [...document.querySelectorAll("#grid-3x3 .board-slot")].map((el) => {
        const r = el.getBoundingClientRect();
        const res = { tile: [+el.dataset.r, +el.dataset.c] };
        for (const [k, fx, fy] of [["center", 0.5, 0.5], ["tl", 0.2, 0.2], ["br", 0.8, 0.8]]) {
          const hit = document.elementFromPoint(r.left + r.width * fx, r.top + r.height * fy);
          res[k] = (hit === el || el.contains(hit)) ? "OK" : desc(hit);
        }
        return res;
      });
    });
    // real click-to-place on each empty tile centre (Reset between trials)
    const clicks = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      const rb = await page.locator("header button", { hasText: "Reset" }).boundingBox();
      let s0;
      if (rb && rb.x + rb.width / 2 < w) { await page.mouse.click(rb.x + rb.width / 2, rb.y + rb.height / 2); }
      else { await page.evaluate(() => startStage(state.stageIndex)); }
      await page.waitForTimeout(250);
      s0 = await L.snap(page);
      if (s0.grid[r][c]) continue;
      const [hx, hy] = await L.center(page, L.handSel(0));
      await page.mouse.click(hx, hy);
      await page.waitForTimeout(80);
      const [, , tb] = await L.center(page, L.slotSel(r, c));
      await page.mouse.click(tb.x + tb.width / 2, tb.y + tb.height / 2);
      await page.waitForTimeout(250);
      const s1 = await L.snap(page);
      const placedAt = []; s1.grid.forEach((row, rr) => row.forEach((v, cc) => { if (v && v.startsWith("p:") && !s0.grid[rr][cc]) placedAt.push([rr, cc]); }));
      clicks.push({ tile: [r, c], ok: s1.grid[r][c] === "p:" + s0.hand[0], placedAt });
      await page.waitForTimeout(800);
    }
    // layout shift: hover each hand card -> HUD text changes -> measure right aside x / visible width
    const shifts = [];
    const n = await page.locator("#hand-bar .hand-card-wrap").count();
    for (let i = 0; i < n; i++) {
      const [hx, hy] = await L.center(page, L.handSel(i));
      await page.mouse.move(hx, hy);
      await page.waitForTimeout(120);
      shifts.push(await page.evaluate(() => {
        const a = document.querySelector("main > aside:nth-of-type(2)").getBoundingClientRect();
        const g = document.querySelector("#grid-3x3").getBoundingClientRect();
        return { hud: document.getElementById("telegraph-hud-desc").textContent.length, hudPx: Math.round(document.getElementById("telegraph-hud-pill").scrollWidth), asideLeft: Math.round(a.left), asideVisiblePx: Math.max(0, Math.round(Math.min(innerWidth, a.right) - a.left)), gridLeft: Math.round(g.left) };
      }));
    }
    const shot = L.path.join(L.SCREENS, `t3b_${w}x${h}_hover_last_card.png`);
    await page.screenshot({ path: shot });
    out.push({ viewport: `${w}x${h}`, hits, clicks, clickToPlaceOk: clicks.filter((c) => c.ok).length + "/" + clicks.length, layoutShiftOnHover: shifts, gridLeftRangePx: Math.max(...shifts.map((s) => s.gridLeft)) - Math.min(...shifts.map((s) => s.gridLeft)), asideLeftRangePx: Math.max(...shifts.map((s) => s.asideLeft)) - Math.min(...shifts.map((s) => s.asideLeft)) });
    await context.close();
  }
  L.writeJSON("t3b_hit_and_shift.json", out);
  console.log(JSON.stringify(out.map((o) => ({ vp: o.viewport, clickToPlace: o.clickToPlaceOk, failedClicks: o.clicks.filter((c) => !c.ok), badHits: o.hits.filter((x) => x.center !== "OK" || x.tl !== "OK" || x.br !== "OK"), gridShift: o.gridLeftRangePx, asideShift: o.asideLeftRangePx, shifts: o.layoutShiftOnHover })), null, 1));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
