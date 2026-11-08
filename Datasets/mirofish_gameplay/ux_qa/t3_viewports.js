// T3: Viewport matrix — visibility/clipping of key regions, text overflow, tile hittability, touch drag on iPad.
const L = require("./lib");

const VIEWPORTS = [
  { name: "1024x768", width: 1024, height: 768 },
  { name: "1280x720", width: 1280, height: 720 },
  { name: "1280x800", width: 1280, height: 800 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
  { name: "ipad_portrait_820x1180", width: 820, height: 1180, touch: true },
  { name: "ipad_landscape_1180x820", width: 1180, height: 820, touch: true },
];

// In-page audit: for each region, compute its rect, the visible rect after intersecting with the viewport
// and every overflow-clipping ancestor, and the % hidden.
const AUDIT = () => {
  const vw = innerWidth, vh = innerHeight;
  const clipRect = (el) => {
    let r = el.getBoundingClientRect();
    let vis = { l: Math.max(0, r.left), t: Math.max(0, r.top), r: Math.min(vw, r.right), b: Math.min(vh, r.bottom) };
    let p = el.parentElement;
    while (p && p !== document.documentElement) {
      const cs = getComputedStyle(p);
      if (/(hidden|clip|auto|scroll)/.test(cs.overflow + cs.overflowX + cs.overflowY)) {
        const pr = p.getBoundingClientRect();
        vis = { l: Math.max(vis.l, pr.left), t: Math.max(vis.t, pr.top), r: Math.min(vis.r, pr.right), b: Math.min(vis.b, pr.bottom) };
      }
      p = p.parentElement;
    }
    const area = Math.max(0, r.width) * Math.max(0, r.height);
    const visArea = Math.max(0, vis.r - vis.l) * Math.max(0, vis.b - vis.t);
    return { rect: [r.left, r.top, r.width, r.height].map(Math.round), hiddenPct: area ? +(100 * (1 - visArea / area)).toFixed(1) : 100 };
  };
  const regions = {
    header: "header", headerRight: ".header-right", scoreboard: ".scoreboard",
    handPanel: "main > aside:nth-of-type(1)", bossPanelAside: "main > aside:nth-of-type(2)",
    board: "#board-3d-slab", grid: "#grid-3x3", telegraphHud: "#telegraph-hud-pill",
    dicePanel: "#dice-column-list", rerollBtn: "main > aside:nth-of-type(2) button",
    bossProfile: ".boss-profile", lastMoveBanner: "#last-move-banner",
  };
  const out = { regions: {}, handCards: [], tiles: [], textOverflow: [], docScroll: { sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, vw, vh } };
  for (const [k, sel] of Object.entries(regions)) { const el = document.querySelector(sel); out.regions[k] = el ? clipRect(el) : { missing: true }; }
  document.querySelectorAll("#hand-bar .hand-card-wrap, #hand-bar .tactical-slide-card").forEach((el, i) => out.handCards.push({ i, ...clipRect(el) }));
  document.querySelectorAll("#grid-3x3 .board-slot").forEach((el) => {
    const r = el.getBoundingClientRect();
    const pts = [[0.5, 0.5], [0.2, 0.2], [0.8, 0.8]].map(([fx, fy]) => {
      const x = r.left + r.width * fx, y = r.top + r.height * fy;
      const hit = document.elementFromPoint(x, y);
      return !!(hit && (hit === el || el.contains(hit)));
    });
    out.tiles.push({ r: +el.dataset.r, c: +el.dataset.c, ...clipRect(el), centerHittable: pts[0], cornersHittable: pts.slice(1).every(Boolean) });
  });
  // text overflow: any element with own text whose content is wider/taller than its box and clipped
  document.querySelectorAll("body *").forEach((el) => {
    if (el.closest("svg") || el.closest(".modal-backdrop")) return;
    const ownText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!ownText) return;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return;
    const ox = el.scrollWidth - el.clientWidth, oy = el.scrollHeight - el.clientHeight;
    const clipped = /(hidden|clip)/.test(cs.overflow + cs.overflowX + cs.overflowY);
    if ((ox > 1 || oy > 1) && clipped) {
      out.textOverflow.push({ text: el.textContent.trim().replace(/\s+/g, " ").slice(0, 60), cls: el.className && el.className.baseVal === undefined ? el.className : el.tagName, id: el.id, ox, oy, ellipsis: cs.textOverflow === "ellipsis" });
    }
  });
  return out;
};

(async () => {
  const browser = await L.launch();
  const results = [];
  for (const vp of VIEWPORTS) {
    const ctxOpts = { viewport: { width: vp.width, height: vp.height } };
    if (vp.touch) Object.assign(ctxOpts, { hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
    const { page, context, log } = await L.openGame(browser, ctxOpts);
    await page.waitForTimeout(300);
    const shot = L.path.join(L.SCREENS, `t3_vp_${vp.name}.png`);
    await page.screenshot({ path: shot });
    const audit = await page.evaluate(AUDIT);
    // hover a tile to get the preview HUD text (longest strings) then re-audit text overflow
    const res = { viewport: vp.name, screenshot: shot, ...audit };
    const visibleIssues = [];
    for (const [k, v] of Object.entries(audit.regions)) if (v.hiddenPct > 0.5) visibleIssues.push(`${k} ${v.hiddenPct}% hidden`);
    audit.handCards.forEach((h) => { if (h.hiddenPct > 0.5) visibleIssues.push(`hand[${h.i}] ${h.hiddenPct}% hidden`); });
    audit.tiles.forEach((t) => { if (t.hiddenPct > 0.5) visibleIssues.push(`tile(${t.r},${t.c}) ${t.hiddenPct}% hidden`); });
    res.visibleIssues = visibleIssues;
    res.allTilesCenterHittable = audit.tiles.every((t) => t.centerHittable);
    res.allTilesCornersHittable = audit.tiles.every((t) => t.cornersHittable);

    // Real input placement on this viewport: touch drag on touch devices, mouse drag otherwise
    const s0 = await L.snap(page);
    const target = s0.grid[1][1] ? [2, 1] : [1, 1];
    const h = await L.center(page, L.handSel(0));
    const t = await L.center(page, L.slotSel(...target));
    let inputOk = null, mode;
    if (h && t) {
      if (vp.touch) {
        mode = "touch (CDP Input.dispatchTouchEvent)";
        // capture pointer event types the page sees
        await page.evaluate(() => { window.__pt = []; ["pointerdown", "pointermove", "pointerup", "pointercancel"].forEach((ty) => window.addEventListener(ty, (e) => window.__pt.push(ty + ":" + e.pointerType), true)); });
        await L.touchDrag(page, h[0], h[1], t[0], t[1], 24, 150);
        await page.waitForTimeout(400);
        res.touchPointerEvents = await page.evaluate(() => { const c = {}; window.__pt.forEach((k) => (c[k] = (c[k] || 0) + 1)); return c; });
      } else {
        mode = "mouse";
        await L.dragHandToSlot(page, 0, target[0], target[1], { after: 400 });
      }
      const s1 = await L.snap(page);
      inputOk = s1.grid[target[0]][target[1]] === "p:" + s0.hand[0];
      await page.screenshot({ path: L.path.join(L.SCREENS, `t3_vp_${vp.name}_after_drop.png`) });
    }
    res.inputMode = mode;
    res.dragPlacementWorked = inputOk;
    if (vp.touch) {
      // tap-to-select + tap-to-place fallback
      await L.waitPlayerTurn(page);
      const s2 = await L.snap(page);
      const empty = [];
      s2.grid.forEach((row, r) => row.forEach((v, c) => { if (!v) empty.push([r, c]); }));
      const hc = await L.center(page, L.handSel(1));
      await L.touchTap(page, hc[0], hc[1]);
      await page.waitForTimeout(150);
      const tc = await L.center(page, L.slotSel(...empty[0]));
      await L.touchTap(page, tc[0], tc[1]);
      await page.waitForTimeout(400);
      const s3 = await L.snap(page);
      res.tapTapPlacementWorked = s3.grid[empty[0][0]][empty[0][1]] === "p:" + s2.hand[1];
    }
    res.pageErrors = log.pageErrors;
    results.push(res);
    await context.close();
  }
  const p = L.writeJSON("t3_viewports.json", results);
  console.log(p);
  console.log(JSON.stringify(results.map((r) => ({ vp: r.viewport, issues: r.visibleIssues.slice(0, 12), nIssues: r.visibleIssues.length, center: r.allTilesCenterHittable, corners: r.allTilesCornersHittable, drag: r.dragPlacementWorked, tap: r.tapTapPlacementWorked, touchEv: r.touchPointerEvents, overflow: r.textOverflow.length, docScroll: r.docScroll })), null, 1));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
