// Real-mouse drag & drop E2E for cardfront_cradle_of_echoes_playable.html (Playwright Chromium)
const { chromium } = require(process.env.PLAYWRIGHT_CORE || "playwright-core");
const OUT = process.env.OUT_DIR || require("os").tmpdir();
const URL = "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html?pw=" + Date.now();

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROMIUM_EXE || undefined });
  const page = await browser.newPage({ viewport: { width: 1408, height: 800 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(URL);
  await page.waitForTimeout(900);

  const res = {};
  const center = async (sel) => {
    const b = await page.locator(sel).boundingBox();
    return [b.x + b.width / 2, b.y + b.height / 2];
  };
  const state = () => page.evaluate(() => ({
    hand: state.hand.slice(),
    grid: state.grid.map((row) => row.map((c) => c.cardId ? c.owner[0] + ":" + c.cardId : null)),
    isPlayerTurn: state.isPlayerTurn,
    used: state.usedSlideThisTurn,
    ghost: !!document.querySelector(".drag-ghost"),
  }));
  const firstEmpty = async () => page.evaluate(() => {
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) return [r, c];
  });
  const slotSel = (r, c) => `#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`;

  // 1. Invalid drop: release over the header → card springs home, nothing placed
  let s0 = await state();
  let [hx, hy] = await center("#hand-bar .hand-card-wrap >> nth=0");
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move(hx + 60, 20, { steps: 15 });
  res.ghostCreatedOnDrag = (await state()).ghost;
  await page.mouse.up();
  await page.waitForTimeout(400);
  let s1 = await state();
  res.invalidDropSpringsBack = s1.hand.length === s0.hand.length && !s1.ghost;

  // 2. Valid drop with a deliberately sloppy release (off-center, inside the magnet radius)
  const [tr, tc] = await firstEmpty();
  const cardId = s1.hand[1];
  [hx, hy] = await center("#hand-bar .hand-card-wrap >> nth=1");
  const tb = await page.locator(slotSel(tr, tc)).boundingBox();
  await page.mouse.move(hx, hy);
  await page.mouse.down();
  await page.mouse.move(tb.x + tb.width * 0.5, tb.y + tb.height * 0.5, { steps: 25 });
  await page.waitForTimeout(250);
  res.dropHoverHighlighted = await page.locator(".board-slot.drop-hover").count() === 1;
  res.landingPreviewShown = await page.locator(".board-slot.landing-preview").count() === 1;
  res.validTargetsPulsing = await page.locator(".board-slot.drop-valid").count();
  res.sourceCardDimmed = await page.locator(".hand-card-wrap.drag-source").count() === 1;
  await page.screenshot({ path: `${OUT}/drag_midair.png` });
  // drift to the gap just outside the tile edge: magnet should keep the same target
  await page.mouse.move(tb.x + tb.width + 4, tb.y + tb.height * 0.5, { steps: 6 });
  await page.waitForTimeout(120);
  res.magnetHoldsNearEdge = await page.locator(`${slotSel(tr, tc)}.drop-hover`).count() === 1;
  await page.mouse.up();
  await page.waitForTimeout(250);
  await page.screenshot({ path: `${OUT}/drag_landed.png` });
  let s2 = await state();
  res.validDropPlaced = s2.grid[tr][tc] === "p:" + cardId && s2.hand.length === s1.hand.length - 1 && !s2.ghost;

  // 3. Wait for boss, then Tactical Slide by dragging a blue board card 1 tile
  await page.waitForFunction(() => state.isPlayerTurn && !state.gameOver, null, { timeout: 5000 });
  await page.waitForTimeout(300);
  const slide = await page.evaluate(() => {
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      const cell = state.grid[r][c];
      if (cell.cardId && cell.owner === "player") {
        for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
          const nr = r + dr, nc = c + dc;
          if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !state.grid[nr][nc].cardId) return { r, c, nr, nc, id: cell.cardId };
        }
      }
    }
    return null;
  });
  if (slide) {
    const [ax, ay] = await center(slotSel(slide.r, slide.c));
    const [bx, by] = await center(slotSel(slide.nr, slide.nc));
    await page.mouse.move(ax, ay);
    await page.mouse.down();
    await page.mouse.move(bx, by, { steps: 20 });
    await page.waitForTimeout(150);
    res.slideSourceDimmed = await page.locator(".board-slot.drag-source").count() === 1;
    await page.mouse.up();
    await page.waitForTimeout(300);
    const s3 = await state();
    res.tacticalSlideByDrag = s3.grid[slide.nr][slide.nc] && s3.grid[slide.nr][slide.nc].endsWith(slide.id) && s3.used === true;
  }

  // 4. Plain click still selects a hand card (no ghost)
  await page.locator("#hand-bar .hand-card-wrap >> nth=1").click();
  await page.waitForTimeout(100);
  res.clickSelectStillWorks = (await page.evaluate(() => state.selectedHandIdx)) === 1 && !(await state()).ghost;

  // 5. Click-to-place fallback still works
  const [er, ec] = await firstEmpty();
  const before = (await state()).hand.length;
  await page.locator(slotSel(er, ec)).click();
  await page.waitForTimeout(300);
  res.clickToPlaceStillWorks = (await state()).hand.length === before - 1;

  res.pageErrors = errors;
  res.pass = Object.entries(res).every(([k, v]) => k === "pageErrors" ? v.length === 0 : (v === true || (typeof v === "number" && v > 0)));
  console.log(JSON.stringify(res, null, 2));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
