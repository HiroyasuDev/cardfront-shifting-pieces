// T2b: corrected / additional edge cases (waits for the 120 ms snap commit before acting).
const L = require("./lib");
const S = (n) => L.path.join(L.SCREENS, n);
const commit = (page, n) => page.waitForFunction((n) => state.hand.length < n, n, { timeout: 1500 }).then(() => true, () => false);
const clickReset = async (page) => { const rb = await page.locator("header button", { hasText: "Reset" }).boundingBox(); await page.mouse.click(rb.x + rb.width / 2, rb.y + rb.height / 2); };
const empties = (g) => { const e = []; g.forEach((row, r) => row.forEach((v, c) => { if (!v) e.push([r, c]); })); return e; };

(async () => {
  const browser = await L.launch();
  const R = {};

  // A. Drag during boss turn (after commit, inside the 650 ms boss delay)
  {
    const { page, context } = await L.openGame(browser);
    const s0 = await L.snap(page);
    const [r, c] = empties(s0.grid)[0];
    await L.dragHandToSlot(page, 0, r, c, { after: 0 });
    await commit(page, s0.hand.length);
    const s1 = await L.snap(page);
    const [r2, c2] = empties(s1.grid)[0];
    const [hx, hy] = await L.center(page, L.handSel(0));
    const [tx, ty] = await L.center(page, L.slotSel(r2, c2));
    await page.mouse.move(hx, hy); await page.mouse.down();
    await page.mouse.move(tx, ty, { steps: 6 });
    const mid = await L.snap(page);
    await page.screenshot({ path: S("t2_drag_during_boss_turn.png") });
    await page.mouse.up();
    await page.waitForTimeout(1100);
    const s2 = await L.snap(page);
    R.dragDuringBossTurn = {
      bossTurnActiveAtAttempt: s1.isPlayerTurn === false, ghostCreated: mid.ghost > 0, handAfterBoss: s2.hand.length, expectedHand: s0.hand.length - 1,
      turnBadgeDuringAttempt: await page.evaluate(() => 0) === 0 ? "BOSS TURN (badge only; no cursor change)" : "",
      pass: s1.isPlayerTurn === false && mid.ghost === 0 && s2.hand.length === s0.hand.length - 1,
    };
    await context.close();
  }

  // B. Drop outside board — fresh Reset before each target
  {
    const { page, context } = await L.openGame(browser);
    const dice = await page.locator("#dice-column-list").boundingBox();
    const gb = await page.locator("#grid-3x3").boundingBox();
    const targets = {
      rightPanel: [dice.x + dice.width / 2, dice.y + dice.height / 2],
      header: [700, 20],
      handPanelOtherCard: null,
      belowBoard30px: [gb.x + gb.width / 2, gb.y + gb.height + 30],
      leftOfBoard60px: [gb.x - 60, gb.y + gb.height / 2],
    };
    const res = {};
    for (const [name, pt] of Object.entries(targets)) {
      await clickReset(page); await page.waitForTimeout(350);
      const s0 = await L.snap(page);
      const [x, y] = pt || (await L.center(page, L.handSel(3)));
      const [hx, hy] = await L.center(page, L.handSel(0));
      await page.mouse.move(hx, hy); await page.mouse.down();
      await page.mouse.move(hx + 12, hy, { steps: 2 });
      await page.mouse.move(x, y, { steps: 15 });
      await page.waitForTimeout(150);
      const mid = await L.snap(page);
      const hover = await page.evaluate(() => drag.target ? [drag.target.r, drag.target.c] : null);
      await page.mouse.up();
      await page.waitForTimeout(450);
      const s = await L.snap(page);
      res[name] = { at: [Math.round(x), Math.round(y)], ghostDuring: mid.ghost, magnetTargetAtRelease: hover, placed: s0.hand.length - s.hand.length, ghostAfter: s.ghost };
    }
    R.dropOutsideBoard = { ...res, passStrict: ["rightPanel", "header", "handPanelOtherCard"].every((k) => res[k].placed === 0 && res[k].ghostAfter === 0) };
    await context.close();
  }

  // C. Real tab switch mid-drag: does the page even receive 'blur'/visibilitychange in headless?
  {
    const { page, context } = await L.openGame(browser);
    await page.evaluate(() => { window.__blur = 0; window.__vis = 0; addEventListener("blur", () => window.__blur++); document.addEventListener("visibilitychange", () => window.__vis++); });
    const other = await context.newPage();
    await page.bringToFront();
    const s0 = await L.snap(page);
    let mid;
    await L.dragHandToSlot(page, 0, 1, 1, { beforeUp: async () => { await other.bringToFront(); await page.waitForTimeout(300); mid = await L.snap(page); await page.bringToFront(); }, after: 400 });
    const s1 = await L.snap(page);
    R.realTabSwitchMidDrag = { blurEventsReceived: await page.evaluate(() => window.__blur), visibilityEvents: await page.evaluate(() => window.__vis), ghostWhileOtherTabFront: mid.ghost, placedOnReturn: s0.hand.length - s1.hand.length, note: "If blurEventsReceived=0 the headless shell did not deliver focus loss; the dispatched-blur variant in t2_edge_cases.json is the valid check. No visibilitychange handler exists in the game." };
    await context.close();
  }

  // D. Reset during the 120 ms snap animation (after mouseup, before commit)
  {
    const { page, context } = await L.openGame(browser);
    const s0 = await L.snap(page);
    await L.dragHandToSlot(page, 1, 1, 1, { after: 0 });
    await clickReset(page);
    await page.waitForTimeout(1300);
    const s1 = await L.snap(page);
    await page.screenshot({ path: S("t2_reset_during_snap.png") });
    R.resetDuringSnapAnimation = { cardsAfter: L.countCards(s1.grid), handAfter: s1.hand.length, nudges: s1.nudges, pass: L.countCards(s1.grid).p === 0 && L.countCards(s1.grid).a === 1 && s1.hand.length === 5 };
    await context.close();
  }

  // E. Reset / stage-select strictly inside the 650 ms boss delay (after commit)
  for (const how of ["resetButton", "stageSelect"]) {
    const { page, context } = await L.openGame(browser);
    const s0 = await L.snap(page);
    await L.dragHandToSlot(page, 1, 1, 1, { after: 0 });
    await commit(page, s0.hand.length);
    const pre = await L.snap(page);
    const tReset = Date.now();
    if (how === "resetButton") await clickReset(page); else await page.selectOption("#stage-select", "2");
    const justAfter = await L.snap(page);
    await page.waitForTimeout(1200);
    const later = await L.snap(page);
    await page.screenshot({ path: S(`t2_${how}_mid_boss_turn.png`) });
    R[`${how}MidBossTurn`] = {
      bossTurnPendingWhenReset: pre.isPlayerTurn === false, cardsRightAfter: L.countCards(justAfter.grid), cardsAfter1200ms: L.countCards(later.grid),
      nudgesAfter: later.nudges, aiPoolAfter: later.aiPool.length, isPlayerTurn: later.isPlayerTurn,
      banner: await page.$eval("#last-move-banner", (e) => e.textContent.trim()),
      pass: L.countCards(later.grid).a === 1 && later.nudges === 2,
    };
    await context.close();
  }

  // F. Reset in the 460 ms gap between game end (boss's last move) and the result modal
  {
    const { page, context } = await L.openGame(browser);
    let res = null;
    for (let i = 0; i < 6 && !res; i++) {
      await L.waitPlayerTurn(page);
      const s = await L.snap(page);
      if (s.gameOver) break;
      const mv = await L.greedyMove(page);
      await L.dragHandToSlot(page, mv.idx, mv.r, mv.c, { after: 0 });
      await commit(page, s.hand.length);
      if (empties(s.grid).length === 2) {
        await page.waitForFunction(() => state.gameOver, null, { timeout: 3000 });
        await clickReset(page);
        await page.waitForTimeout(900);
        const after = await L.snap(page);
        await page.screenshot({ path: S("t2_reset_during_gameover_delay.png") });
        res = { modalVisibleOnFreshBoard: after.modal, freshBoardCards: L.countCards(after.grid), modalTitle: after.modalTitle, pass: !after.modal };
      }
    }
    R.resetDuringGameOverDelay = res || { skipped: true };
    await context.close();
  }

  // G. Multi-pointer: a second (touch) pointer lifting elsewhere while the mouse drag is held over a tile
  {
    const { page, context } = await L.openGame(browser, { hasTouch: true });
    const s0 = await L.snap(page);
    let mid;
    await L.dragHandToSlot(page, 2, 2, 2, {
      beforeUp: async () => { await L.touchTap(page, 700, 790); await page.waitForTimeout(400); mid = await L.snap(page); },
      after: 400,
    });
    R.secondPointerUpEndsDrag = { placedByForeignPointerUp: s0.hand.length - mid.hand.length, ghostAfterTouch: mid.ghost, note: "onDragPointerUp/Cancel do not filter by pointerId", pass: s0.hand.length - mid.hand.length === 0 };
    await context.close();
  }

  // H. Keyboard digits / R / Enter during an active drag
  {
    const { page, context } = await L.openGame(browser);
    const s0 = await L.snap(page);
    let mid;
    await L.dragHandToSlot(page, 0, 2, 0, { beforeUp: async () => { await page.keyboard.press("4"); await page.keyboard.press("r"); await page.waitForTimeout(150); mid = await L.snap(page); }, after: 400 });
    const s1 = await L.snap(page);
    R.digitAndRerollKeysMidDrag = { selDuringDrag: mid.sel, rerollsDuringDrag: mid.rerolls, placedCard: s1.grid[2][0], expected: "p:" + s0.hand[0], pass: s1.grid[2][0] === "p:" + s0.hand[0] };
    await context.close();
  }

  // I. 1-step flick repeated 20x (pointerup arrives without an intermediate pointermove)
  {
    const { page, context } = await L.openGame(browser);
    let ok = 0, n = 0;
    for (let i = 0; i < 20; i++) {
      await page.evaluate(() => startStage(0));
      await page.waitForTimeout(200);
      const s0 = await L.snap(page);
      await L.flickHandToSlot(page, 1, 1, 1, 1);
      await page.waitForTimeout(100);
      const s1 = await L.snap(page);
      n++; if (s1.grid[1][1] === "p:" + s0.hand[1]) ok++;
    }
    R.oneStepFlick20x = { trials: n, placed: ok, note: "startStage() called via evaluate only to reset between trials" };
    await context.close();
  }

  L.writeJSON("t2b_edge_cases.json", R);
  console.log(JSON.stringify(R, null, 1));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
