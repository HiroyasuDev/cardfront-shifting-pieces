// T4: Performance — frame intervals during a 3 s continuous real-mouse drag (and baselines), long tasks,
// renderAll call counts/durations (runtime wrapper, game file untouched), resource/image errors.
// Runs at CPU throttle 1x and 4x (CDP Emulation.setCPUThrottlingRate) to approximate a low-end device.
const L = require("./lib");

const INIT = () => {
  window.__lt = [];
  try {
    new PerformanceObserver((list) => list.getEntries().forEach((e) => window.__lt.push({ start: +e.startTime.toFixed(1), dur: +e.duration.toFixed(1) }))).observe({ type: "longtask", buffered: true });
  } catch (e) { window.__ltErr = String(e); }
};

const startRec = (page) => page.evaluate(() => {
  window.__frames = []; window.__rec = true; window.__ltMark = performance.now();
  window.__ra = { n: 0, total: 0, max: 0 };
  if (!window.__wrapped) {
    const orig = window.renderAll;
    window.renderAll = function () { const t = performance.now(); const r = orig.apply(this, arguments); const d = performance.now() - t; if (window.__rec) { window.__ra.n++; window.__ra.total += d; window.__ra.max = Math.max(window.__ra.max, d); } return r; };
    window.__wrapped = true;
  }
  const loop = (ts) => { if (!window.__rec) return; window.__frames.push(ts); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
});
const stopRec = (page) => page.evaluate(() => {
  window.__rec = false;
  const f = window.__frames; const iv = [];
  for (let i = 1; i < f.length; i++) iv.push(f[i] - f[i - 1]);
  const s = [...iv].sort((a, b) => a - b);
  const pct = (p) => s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : null;
  const lts = window.__lt.filter((x) => x.start >= window.__ltMark);
  return {
    frames: f.length, durationMs: f.length ? +(f[f.length - 1] - f[0]).toFixed(0) : 0,
    avgMs: +(iv.reduce((a, b) => a + b, 0) / (iv.length || 1)).toFixed(2), p95Ms: +(pct(0.95) || 0).toFixed(2), p99Ms: +(pct(0.99) || 0).toFixed(2), maxMs: +(s[s.length - 1] || 0).toFixed(2),
    over20ms: iv.filter((x) => x > 20).length, over33ms: iv.filter((x) => x > 33.4).length, over50ms: iv.filter((x) => x > 50).length,
    longTasks: lts.length, longTaskTotalMs: +lts.reduce((a, b) => a + b.dur, 0).toFixed(1), longTaskMaxMs: lts.length ? Math.max(...lts.map((x) => x.dur)) : 0,
    renderAll: { calls: window.__ra.n, avgMs: +(window.__ra.total / (window.__ra.n || 1)).toFixed(2), maxMs: +window.__ra.max.toFixed(2) },
    ltObserverError: window.__ltErr || null,
  };
});

async function scenario(page, kind) {
  const gb = await page.locator("#grid-3x3").boundingBox();
  const cx = gb.x + gb.width / 2, cy = gb.y + gb.height / 2;
  if (kind === "idle") { await startRec(page); await page.waitForTimeout(3000); return stopRec(page); }
  if (kind === "hoverSweep") {
    await startRec(page);
    const t0 = Date.now(); let i = 0;
    while (Date.now() - t0 < 3000) { const a = i++ * 0.09; await page.mouse.move(cx + Math.cos(a) * gb.width * 0.42, cy + Math.sin(a * 1.3) * gb.height * 0.42); await page.waitForTimeout(8); }
    return stopRec(page);
  }
  // continuous drag: pick hand card 0, wander over the board (crossing many tiles) for 3 s, then Esc
  const [hx, hy] = await L.center(page, L.handSel(0));
  await page.mouse.move(hx, hy); await page.mouse.down();
  await page.mouse.move(hx + 15, hy, { steps: 3 });
  await startRec(page);
  const t0 = Date.now(); let i = 0, moves = 0;
  while (Date.now() - t0 < 3000) { const a = i++ * 0.09; await page.mouse.move(cx + Math.cos(a) * gb.width * 0.45, cy + Math.sin(a * 1.3) * gb.height * 0.45); moves++; await page.waitForTimeout(8); }
  const r = await stopRec(page);
  r.pointerMovesSent = moves;
  r.ghostPresentDuringDrag = await page.evaluate(() => !!document.querySelector(".drag-ghost"));
  await page.keyboard.press("Escape");
  await page.mouse.up();
  await page.waitForTimeout(400);
  return r;
}

(async () => {
  const browser = await L.launch();
  const out = { note: "Headless Chromium (chrome-headless-shell) on Apple A18 Pro; rAF cadence ~60 Hz in headless. Numbers are relative indicators, not device-accurate.", runs: {} };
  for (const throttle of [1, 4]) {
    const context = await browser.newContext({ viewport: { width: 1408, height: 800 } });
    await context.addInitScript(INIT);
    const page = await context.newPage();
    const log = L.attachCollectors(page);
    let imgReq = 0; page.on("request", (r) => { if (r.resourceType() === "image") imgReq++; });
    await page.goto(L.gameUrl());
    await page.waitForFunction(() => document.querySelectorAll("#grid-3x3 .board-slot").length === 9);
    await page.waitForTimeout(800);
    const cdp = await context.newCDPSession(page);
    if (throttle > 1) await cdp.send("Emulation.setCPUThrottlingRate", { rate: throttle });
    const loadLT = await page.evaluate(() => window.__lt.slice());
    const run = { loadLongTasks: loadLT, imageRequestsAtLoad: imgReq };
    run.idle = await scenario(page, "idle");
    run.hoverSweep = await scenario(page, "hoverSweep");
    const imgBefore = imgReq;
    run.drag = await scenario(page, "drag");
    run.imageRequestsDuringDrag = imgReq - imgBefore;
    run.domNodesAfter = await page.evaluate(() => document.getElementsByTagName("*").length);
    run.brokenImages = await page.evaluate(() => [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src));
    run.resourceErrors = { failed: log.failedRequests, bad: log.badResponses };
    run.console = log.console; run.pageErrors = log.pageErrors;
    out.runs[`cpu${throttle}x`] = run;
    await context.close();
  }
  const p = L.writeJSON("t4_perf.json", out);
  const brief = {};
  for (const [k, v] of Object.entries(out.runs)) brief[k] = { idle: v.idle, hover: v.hoverSweep, drag: v.drag, imgReqDrag: v.imageRequestsDuringDrag, loadLT: v.loadLongTasks.length, broken: v.brokenImages.length, errs: v.pageErrors.length + v.console.length };
  console.log(p); console.log(JSON.stringify(brief, null, 1));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
