// Shared Playwright helpers for the rules_audit repro scripts (headless Chromium, per BRIEF.md).
// Convention: every repro asserts the *buggy* behaviour. "REPRODUCED" = all bug assertions held.
const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");

const EXE = "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const BASE = process.env.GAME_URL || "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const OUT = path.join(__dirname, "..", "out");
fs.mkdirSync(OUT, { recursive: true });

// Deterministic Math.random (mulberry32) injected before page scripts run.
function seedScript(seed) {
  return `(() => { let a = ${seed >>> 0}; Math.random = function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })();`;
}

async function open({ seed = 12345, query = "", viewport = { width: 1408, height: 800 } } = {}) {
  const browser = await chromium.launch({ headless: true, executablePath: EXE });
  const page = await browser.newPage({ viewport });
  const errors = [];
  const requests = [];
  page.on("pageerror", (e) => errors.push(String(e && e.message ? e.message : e)));
  page.on("request", (r) => requests.push({ url: r.url(), method: r.method() }));
  if (seed !== null) await page.addInitScript(seedScript(seed));
  const q = query ? `?${query}&pw=${Date.now()}` : `?pw=${Date.now()}`;
  await page.goto(BASE + q);
  await page.waitForFunction(() => typeof state !== "undefined" && state.grid.length === 3 && state.hand.length > 0);
  await page.waitForTimeout(400);
  return { browser, page, errors, requests };
}

const snap = (page) => page.evaluate(() => {
  const s = getScores();
  return {
    stageIndex: state.stageIndex,
    isPlayerTurn: state.isPlayerTurn,
    gameOver: state.gameOver,
    nudgesLeft: state.nudgesLeft,
    rerollsLeft: state.rerollsLeft,
    usedSlide: state.usedSlideThisTurn,
    colDice: state.colDice.slice(),
    hand: state.hand.slice(),
    aiPool: state.aiPool.slice(),
    selectedHandIdx: state.selectedHandIdx,
    selectedBoardSlot: state.selectedBoardSlot,
    grid: state.grid.map((row) => row.map((c) => (c.cardId || c.owner) ? { id: c.cardId === undefined ? "<undefined>" : c.cardId, owner: c.owner, nesw: c.nesw.slice() } : null)),
    scores: s,
    domScore: { you: document.getElementById("player-score").textContent, boss: document.getElementById("ai-score").textContent },
    turnBadge: document.getElementById("turn-badge").textContent,
    modalShown: document.getElementById("result-modal").style.display === "flex",
    modalTitle: document.getElementById("modal-title").textContent,
    ghost: !!document.querySelector(".drag-ghost"),
  };
});

const slotSel = (r, c) => `#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`;
async function center(page, sel) {
  const b = await page.locator(sel).boundingBox();
  return [b.x + b.width / 2, b.y + b.height / 2];
}
const slotCenter = (page, r, c) => center(page, slotSel(r, c));
const handCenter = (page, i) => center(page, `#hand-bar .hand-card-wrap >> nth=${i}`);

async function clickSlot(page, r, c) {
  // Hover first and let the 0.3 s parallax slab transition settle, then click the settled centre.
  let [x, y] = await slotCenter(page, r, c);
  await page.mouse.move(x, y);
  await page.waitForTimeout(380);
  [x, y] = await slotCenter(page, r, c);
  await page.mouse.click(x, y);
}
async function clickHand(page, i) {
  const [x, y] = await handCenter(page, i);
  await page.mouse.click(x, y);
}

// Build a deterministic board. grid cells: null | "P:<id>" | "A:<id>" | {id, owner, nesw}
async function setup(page, spec) {
  await page.evaluate((spec) => {
    if (spec.stage !== undefined) startStage(spec.stage);
    if (spec.dice) state.colDice = spec.dice.slice();
    if (spec.grid) {
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        const v = spec.grid[r][c];
        cell.cardId = null; cell.owner = null; cell.nesw = [0, 0, 0, 0];
        if (!v) continue;
        if (typeof v === "string") {
          const [o, id] = v.split(":");
          cell.cardId = id;
          cell.owner = o === "P" ? "player" : "ai";
          cell.nesw = getCardEffectiveStats(id, c, o === "A");
        } else {
          cell.cardId = v.id; cell.owner = v.owner; cell.nesw = v.nesw.slice();
        }
      }
    }
    if (spec.hand) state.hand = spec.hand.slice();
    if (spec.aiPool) state.aiPool = spec.aiPool.slice();
    if (spec.nudges !== undefined) state.nudgesLeft = spec.nudges;
    if (spec.rerolls !== undefined) state.rerollsLeft = spec.rerolls;
    if (spec.focus !== undefined) state.focusedSlotIndex = spec.focus;
    state.selectedHandIdx = 0;
    state.selectedBoardSlot = null;
    state.usedSlideThisTurn = false;
    state.isPlayerTurn = true;
    state.gameOver = false;
    renderAll();
  }, spec);
  await page.waitForTimeout(150);
}

function reporter(id, title) {
  const checks = [];
  const notes = {};
  return {
    check(name, cond, detail) {
      checks.push({ name, ok: !!cond, detail });
      console.log(`${cond ? "  PASS" : "  FAIL"}  ${name}${detail !== undefined ? "  :: " + JSON.stringify(detail) : ""}`);
    },
    note(k, v) { notes[k] = v; },
    async finish(ctx, extra = {}) {
      const reproduced = checks.length > 0 && checks.every((c) => c.ok);
      const res = { id, title, reproduced, checks, notes, pageErrors: ctx ? ctx.errors : [], ...extra, ranAt: new Date().toISOString() };
      fs.writeFileSync(path.join(OUT, `${id}.json`), JSON.stringify(res, null, 2));
      console.log(`${id}: ${reproduced ? "REPRODUCED" : "NOT REPRODUCED"} (${checks.filter((c) => c.ok).length}/${checks.length} assertions) -> out/${id}.json`);
      if (ctx && ctx.browser) await ctx.browser.close();
      return res;
    },
  };
}

module.exports = { open, snap, setup, slotSel, slotCenter, handCenter, clickSlot, clickHand, reporter, OUT, BASE };
