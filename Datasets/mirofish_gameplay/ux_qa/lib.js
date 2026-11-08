// Shared helpers for the ux_qa workstream (real-input Playwright QA). Read-only w.r.t. the game.
const path = require("path");
const fs = require("fs");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");

const EXE = "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const ROOT = __dirname;
const SCREENS = path.join(ROOT, "screens");
const RAW = path.join(ROOT, "raw");
fs.mkdirSync(SCREENS, { recursive: true });
fs.mkdirSync(RAW, { recursive: true });

const BASE = process.env.GAME_BASE || "http://127.0.0.1:8096";
const gameUrl = (extra = "") => `${BASE}/WebPlayable/cardfront_cradle_of_echoes_playable.html?uxqa=${Date.now()}${extra}`;

async function launch(extraArgs = []) {
  return chromium.launch({ headless: true, executablePath: EXE, args: ["--enable-precise-memory-info", ...extraArgs] });
}

// Attach console / error / network collectors to a page
function attachCollectors(page) {
  const log = { console: [], pageErrors: [], failedRequests: [], badResponses: [] };
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") log.console.push({ type: m.type(), text: m.text() }); });
  page.on("pageerror", (e) => log.pageErrors.push(String(e)));
  page.on("requestfailed", (r) => log.failedRequests.push({ url: r.url(), err: r.failure() && r.failure().errorText }));
  page.on("response", (r) => { if (r.status() >= 400) log.badResponses.push({ url: r.url(), status: r.status() }); });
  return log;
}

async function openGame(browser, ctxOpts = {}, extra = "") {
  const context = await browser.newContext({ viewport: { width: 1408, height: 800 }, ...ctxOpts });
  const page = await context.newPage();
  const log = attachCollectors(page);
  await page.goto(gameUrl(extra));
  await page.waitForFunction(() => typeof state !== "undefined" && state.grid.length === 3 && document.querySelectorAll("#grid-3x3 .board-slot").length === 9);
  await page.waitForTimeout(700);
  return { context, page, log };
}

const slotSel = (r, c) => `#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`;
const handSel = (i) => `#hand-bar .hand-card-wrap >> nth=${i}`;

async function center(page, sel) {
  const b = await page.locator(sel).first().boundingBox();
  if (!b) return null;
  return [b.x + b.width / 2, b.y + b.height / 2, b];
}

// Observation-only snapshot of game state
const snap = (page) => page.evaluate(() => ({
  stage: state.stageIndex,
  hand: state.hand.slice(),
  aiPool: state.aiPool.slice(),
  grid: state.grid.map((row) => row.map((c) => (c.cardId ? c.owner[0] + ":" + c.cardId : null))),
  isPlayerTurn: state.isPlayerTurn,
  gameOver: state.gameOver,
  used: state.usedSlideThisTurn,
  nudges: state.nudgesLeft,
  rerolls: state.rerollsLeft,
  dice: state.colDice.slice(),
  sel: state.selectedHandIdx,
  selBoard: state.selectedBoardSlot,
  ghost: document.querySelectorAll(".drag-ghost").length,
  dragActive: drag.active,
  modal: getComputedStyle(document.getElementById("result-modal")).display !== "none",
  modalTitle: document.getElementById("modal-title").textContent,
  scores: getScores(),
}));

const countCards = (grid) => {
  let p = 0, a = 0, e = 0;
  grid.flat().forEach((v) => { if (!v) e++; else if (v[0] === "p") p++; else a++; });
  return { p, a, e };
};

// Real-mouse drag of hand card idx to tile (r,c). Starts the drag first (6px threshold) so the
// parallax freezes, then measures the target tile and glides there.
async function dragHandToSlot(page, idx, r, c, opts = {}) {
  const steps = opts.steps ?? 22;
  const [hx, hy] = await center(page, handSel(idx));
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move(hx + 12, hy - 4, { steps: 2 });
  const [, , tb] = await center(page, slotSel(r, c));
  const fx = opts.fx ?? 0.5, fy = opts.fy ?? 0.5;
  const tx = tb.x + tb.width * fx, ty = tb.y + tb.height * fy;
  await page.mouse.move(tx, ty, { steps });
  if (opts.midShot) { await page.waitForTimeout(220); await page.screenshot({ path: opts.midShot }); }
  if (opts.beforeUp) await opts.beforeUp();
  await page.waitForTimeout(opts.hold ?? 120);
  await page.mouse.up();
  await page.waitForTimeout(opts.after ?? 260);
}

// Raw "flick": no pre-threshold move, N steps total from hand center straight to target
async function flickHandToSlot(page, idx, r, c, steps, fx = 0.5, fy = 0.5, holdMs = 0) {
  const [hx, hy] = await center(page, handSel(idx));
  const [, , tb] = await center(page, slotSel(r, c));
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move(tb.x + tb.width * fx, tb.y + tb.height * fy, { steps });
  if (holdMs) await page.waitForTimeout(holdMs);
  await page.mouse.up();
  await page.waitForTimeout(300);
}

async function waitPlayerTurn(page, timeout = 6000) {
  await page.waitForFunction(() => (state.isPlayerTurn && !state.gameOver) || state.gameOver, null, { timeout });
  await page.waitForTimeout(250);
}

// Greedy chooser (observation only): maximise immediate captures, tiebreak by edge sum
const greedyMove = (page) => page.evaluate(() => {
  let best = null;
  state.hand.forEach((cid, idx) => {
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      if (state.grid[r][c].cardId) continue;
      const st = getCardEffectiveStats(cid, c, false);
      const caps = findCaptures(r, c, st, "player").length;
      const score = caps * 100 + st.reduce((a, b) => a + b, 0) + (r === 1 && c === 1 ? 0.5 : 0);
      if (!best || score > best.score) best = { idx, r, c, caps, score, cid };
    }
  });
  return best;
});

// CDP touch helpers (real input pipeline -> pointerType "touch")
async function touchDrag(page, x0, y0, x1, y1, steps = 20, holdMs = 120) {
  const cdp = await page.context().newCDPSession(page);
  const pt = (x, y) => [{ x, y, id: 1, radiusX: 4, radiusY: 4, force: 1 }];
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: pt(x0, y0) });
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: pt(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) });
    await page.waitForTimeout(16);
  }
  await page.waitForTimeout(holdMs);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await cdp.detach();
}
async function touchTap(page, x, y, id = 7) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y, id }] });
  await page.waitForTimeout(40);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await cdp.detach();
}

function writeJSON(name, obj) {
  const p = path.join(RAW, name);
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
  return p;
}

module.exports = {
  launch, openGame, attachCollectors, gameUrl, slotSel, handSel, center, snap, countCards,
  dragHandToSlot, flickHandToSlot, waitPlayerTurn, greedyMove, touchDrag, touchTap, writeJSON,
  SCREENS, RAW, ROOT, path, fs,
};
