// T2: Input edge cases with real mouse / keyboard / CDP touch input.
const L = require("./lib");
const S = (n) => L.path.join(L.SCREENS, n);

async function fresh(browser, opts = {}) {
  const g = await L.openGame(browser, { viewport: { width: 1408, height: 800 }, ...opts });
  return g;
}
const firstEmpty = (page, skip = []) => page.evaluate((skip) => {
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId && !skip.some(([a, b]) => a === r && b === c)) return [r, c];
  return null;
}, skip);

(async () => {
  const browser = await L.launch();
  const R = {};

  // 1. Drag during boss turn
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 0, r, c, { after: 40 });
    const s1 = await L.snap(page);
    const [r2, c2] = await firstEmpty(page);
    // immediately try another drag while boss is "thinking" (650 ms window)
    const [hx, hy] = await L.center(page, L.handSel(0));
    const [tx, ty] = await L.center(page, L.slotSel(r2, c2));
    await page.mouse.move(hx, hy); await page.mouse.down();
    await page.mouse.move(tx, ty, { steps: 10 });
    const mid = await L.snap(page);
    await page.screenshot({ path: S("t2_drag_during_boss_turn.png") });
    await page.mouse.up();
    await page.waitForTimeout(1000);
    const s2 = await L.snap(page);
    R.dragDuringBossTurn = {
      bossTurnActiveAtAttempt: s1.isPlayerTurn === false,
      ghostCreated: mid.ghost > 0, dragActive: mid.dragActive,
      handAfterBoss: s2.hand.length, expectedHand: s0.hand.length - 1,
      pass: mid.ghost === 0 && s2.hand.length === s0.hand.length - 1,
      note: "No feedback cursor/tooltip explains why the card cannot be grabbed (cursor stays 'grab').",
      cursorDuringBossTurn: await page.evaluate(() => getComputedStyle(document.querySelector("#hand-bar .hand-card-wrap")).cursor),
    };
    await context.close();
  }

  // 2. Rapid double-click placement (click-select, then dblclick an empty tile; then two tiles 30ms apart)
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const [hx, hy] = await L.center(page, L.handSel(1));
    await page.mouse.click(hx, hy);
    const [r, c] = await firstEmpty(page);
    const [tx, ty] = await L.center(page, L.slotSel(r, c));
    await page.mouse.dblclick(tx, ty);
    await page.waitForTimeout(150);
    const s1 = await L.snap(page);
    await page.waitForTimeout(1000);
    // two different tiles in quick succession
    const [ax, ay] = await L.center(page, L.slotSel(...(await firstEmpty(page))));
    const e1 = await firstEmpty(page);
    const e2 = await firstEmpty(page, [e1]);
    const [bx, by] = await L.center(page, L.slotSel(...e2));
    const s2pre = await L.snap(page);
    await page.mouse.click(ax, ay); await page.waitForTimeout(30); await page.mouse.click(bx, by);
    await page.waitForTimeout(150);
    const s2 = await L.snap(page);
    R.rapidDoubleClick = {
      dblclickPlacedCount: s0.hand.length - s1.hand.length,
      twoTileRapidPlacedCount: s2pre.hand.length - s2.hand.length,
      pass: s0.hand.length - s1.hand.length === 1 && s2pre.hand.length - s2.hand.length === 1,
    };
    await context.close();
  }

  // 3. Drop on occupied tile (boss card at 0,1) dead-centre, and 4. drop outside board (right panel, header, bottom gap)
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    await L.dragHandToSlot(page, 0, 0, 1, { midShot: S("t2_drop_on_occupied_mid.png"), after: 400 });
    const s1 = await L.snap(page);
    R.dropOnOccupied = { placed: s0.hand.length - s1.hand.length, ghostLeft: s1.ghost, occupiedUnchanged: s1.grid[0][1] === s0.grid[0][1], pass: s1.hand.length === s0.hand.length && s1.ghost === 0 && s1.grid[0][1] === s0.grid[0][1] };
    // off-centre drop on occupied tile, 20% from its left edge (toward empty 0,0)
    await L.dragHandToSlot(page, 0, 0, 1, { fx: 0.12, fy: 0.5, after: 400 });
    const s1b = await L.snap(page);
    R.dropOnOccupiedNearEdge = { placedSomewhere: s1.hand.length - s1b.hand.length, whereChanged: s1b.grid.flat().map((v, i) => (v !== s1.grid.flat()[i] ? i : -1)).filter((i) => i >= 0), note: "magnet may redirect a sloppy drop to the nearest valid neighbour (by design)" };
    await context.close();
  }
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const targets = {};
    const dice = await page.locator("#dice-column-list").boundingBox();
    targets.rightPanel = [dice.x + dice.width / 2, dice.y + dice.height / 2];
    targets.header = [700, 20];
    const gb = await page.locator("#grid-3x3").boundingBox();
    targets.belowBoard = [gb.x + gb.width / 2, Math.min(795, gb.y + gb.height + 30)];
    targets.handPanel = (await L.center(page, L.handSel(3))).slice(0, 2);
    const res = {};
    for (const [name, [x, y]] of Object.entries(targets)) {
      const [hx, hy] = await L.center(page, L.handSel(0));
      await page.mouse.move(hx, hy); await page.mouse.down();
      await page.mouse.move(x, y, { steps: 15 });
      await page.waitForTimeout(120);
      const mid = await L.snap(page);
      await page.mouse.up();
      await page.waitForTimeout(400);
      const s = await L.snap(page);
      res[name] = { at: [Math.round(x), Math.round(y)], ghostDuring: mid.ghost, placed: s0.hand.length - s.hand.length, ghostAfter: s.ghost };
    }
    R.dropOutsideBoard = { ...res, pass: Object.values(res).every((v) => v.placed === 0 && v.ghostAfter === 0) };
    await context.close();
  }

  // 5. Esc mid-drag, 6. window blur mid-drag
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const [r, c] = await firstEmpty(page);
    let midEsc;
    await L.dragHandToSlot(page, 0, r, c, {
      beforeUp: async () => { await page.keyboard.press("Escape"); await page.waitForTimeout(350); midEsc = await L.snap(page); },
      after: 300,
    });
    const s1 = await L.snap(page);
    R.escMidDrag = { ghostAfterEsc: midEsc.ghost, dragActiveAfterEsc: midEsc.dragActive, placedAfterRelease: s0.hand.length - s1.hand.length, pass: midEsc.ghost === 0 && s1.hand.length === s0.hand.length };
    // can still drag afterwards
    await L.dragHandToSlot(page, 0, r, c, { after: 200 });
    R.escMidDrag.dragWorksAfterEsc = (await L.snap(page)).hand.length === s0.hand.length - 1;
    await context.close();
  }
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const [r, c] = await firstEmpty(page);
    let mid;
    // (a) real focus change: open a second tab and bring it to front mid-drag
    const other = await context.newPage();
    await page.bringToFront();
    await L.dragHandToSlot(page, 0, r, c, {
      beforeUp: async () => { await other.bringToFront(); await page.waitForTimeout(350); mid = await L.snap(page); await page.bringToFront(); },
      after: 300,
    });
    const s1 = await L.snap(page);
    const realBlur = { ghostAfterBlur: mid.ghost, placed: s0.hand.length - s1.hand.length, ghostAfter: s1.ghost };
    // (b) dispatched window 'blur' event (headless focus emulation may not deliver a real blur)
    let mid2;
    const s1b = await L.snap(page);
    await L.dragHandToSlot(page, 0, r, c, {
      beforeUp: async () => { await page.evaluate(() => window.dispatchEvent(new Event("blur"))); await page.waitForTimeout(350); mid2 = await L.snap(page); },
      after: 300,
    });
    const s2 = await L.snap(page);
    R.windowBlurMidDrag = {
      realTabSwitch: realBlur,
      dispatchedBlur: { ghostAfterBlur: mid2.ghost, placed: s1b.hand.length - s2.hand.length, ghostAfter: s2.ghost },
      pass: mid2.ghost === 0 && s2.hand.length === s1b.hand.length,
    };
    await context.close();
  }

  // 7. Drag a board card when slide already used
  {
    const { page, context } = await fresh(browser);
    // place a card at (1,1) via drag, wait boss
    let s = await L.snap(page);
    const target = s.grid[1][1] ? await firstEmpty(page) : [1, 1];
    await L.dragHandToSlot(page, 0, target[0], target[1]);
    await L.waitPlayerTurn(page);
    // find a blue card with an empty neighbour
    const findSlide = () => page.evaluate(() => {
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        if (cell.cardId && cell.owner === "player") for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
          const nr = r + dr, nc = c + dc;
          if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !state.grid[nr][nc].cardId) return { r, c, nr, nc };
        }
      }
      return null;
    });
    const sl = await findSlide();
    const res = { slideFound: !!sl };
    if (sl) {
      const [ax, ay] = await L.center(page, L.slotSel(sl.r, sl.c));
      await page.mouse.move(ax, ay); await page.mouse.down();
      await page.mouse.move(ax + 10, ay, { steps: 2 });
      const [bx, by] = await L.center(page, L.slotSel(sl.nr, sl.nc));
      await page.mouse.move(bx, by, { steps: 15 }); await page.waitForTimeout(120);
      await page.mouse.up(); await page.waitForTimeout(400);
      const s1 = await L.snap(page);
      res.firstSlideOk = s1.used === true && !!s1.grid[sl.nr][sl.nc];
      const sl2 = await findSlide();
      if (sl2) {
        const before = await L.snap(page);
        const [cx, cy] = await L.center(page, L.slotSel(sl2.r, sl2.c));
        await page.mouse.move(cx, cy); await page.mouse.down();
        await page.mouse.move(cx + 10, cy, { steps: 2 });
        const [dx, dy] = await L.center(page, L.slotSel(sl2.nr, sl2.nc));
        await page.mouse.move(dx, dy, { steps: 15 }); await page.waitForTimeout(120);
        const mid = await L.snap(page);
        await page.mouse.up(); await page.waitForTimeout(400);
        const after = await L.snap(page);
        res.secondDrag = { ghost: mid.ghost, boardChanged: JSON.stringify(after.grid) !== JSON.stringify(before.grid), selectedBoardAfter: after.selBoard };
        res.cursorOnUsedBoardCard = await page.evaluate(([r, c]) => getComputedStyle(document.querySelector(`#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`)).cursor, [sl2.nr, sl2.nc]);
        res.pass = mid.ghost === 0 && !res.secondDrag.boardChanged;
        await page.screenshot({ path: S("t2_slide_used_second_drag.png") });
      } else res.pass = res.firstSlideOk;
    }
    R.dragBoardCardSlideUsed = res;
    await context.close();
  }

  // 8. Click-select one card then drag another
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const [hx, hy] = await L.center(page, L.handSel(0));
    await page.mouse.click(hx, hy);
    await page.waitForTimeout(120);
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 2, r, c);
    const s1 = await L.snap(page);
    R.clickSelectThenDragOther = { expected: s0.hand[2], placed: s1.grid[r][c], pass: s1.grid[r][c] === "p:" + s0.hand[2] };
    await context.close();
  }

  // 9. Reset & stage-select mid-drag (second input = CDP touch tap on Reset while mouse button held)
  {
    const { page, context } = await fresh(browser, { hasTouch: true });
    const s0 = await L.snap(page);
    const [r, c] = [1, 1];
    let afterReset;
    const resetBtn = page.locator("header button", { hasText: "Reset" });
    const rb = await resetBtn.boundingBox();
    await L.dragHandToSlot(page, 1, r, c, {
      beforeUp: async () => {
        await L.touchTap(page, rb.x + rb.width / 2, rb.y + rb.height / 2);
        await page.waitForTimeout(300);
        afterReset = await L.snap(page);
        await page.screenshot({ path: S("t2_reset_mid_drag.png") });
      },
      after: 400,
    });
    const s1 = await L.snap(page);
    R.resetMidDrag = {
      draggedCard: s0.hand[1],
      resetHappened: JSON.stringify(afterReset.hand) !== JSON.stringify(s0.hand),
      ghostStillShownAfterReset: afterReset.ghost, dragStillActive: afterReset.dragActive,
      newHandAtIdx1: afterReset.hand[1],
      placedAfterRelease: s1.grid[r][c],
      placedCardMatchesGhost: s1.grid[r][c] === "p:" + s0.hand[1],
      placedCardIsFromNewHand: afterReset.hand.includes((s1.grid[r][c] || "").slice(2)),
    };
    // stage-select mid-drag: selectOption fires 'change' (programmatic stand-in for a 2nd input device)
    await page.waitForTimeout(1200);
    await page.locator("header button", { hasText: "Reset" }).click();
    await page.waitForTimeout(500);
    const s2 = await L.snap(page);
    let afterSel;
    await L.dragHandToSlot(page, 1, 1, 1, {
      beforeUp: async () => { await page.selectOption("#stage-select", "2"); await page.waitForTimeout(300); afterSel = await L.snap(page); },
      after: 400,
    });
    const s3 = await L.snap(page);
    R.stageSelectMidDrag = {
      draggedCard: s2.hand[1], stageAfter: afterSel.stage, ghostStillShown: afterSel.ghost,
      placedAfterRelease: s3.grid[1][1], placedCardMatchesGhost: s3.grid[1][1] === "p:" + s2.hand[1],
    };
    await context.close();
  }

  // 10. Reset / stage-select mid-boss-turn (real mouse click on Reset within the 650 ms boss delay)
  {
    const { page, context } = await fresh(browser);
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 0, r, c, { after: 60 });
    const pre = await L.snap(page);
    const rb = await page.locator("header button", { hasText: "Reset" }).boundingBox();
    await page.mouse.click(rb.x + rb.width / 2, rb.y + rb.height / 2);
    await page.waitForTimeout(50);
    const justAfter = await L.snap(page);
    await page.waitForTimeout(1200);
    const later = await L.snap(page);
    await page.screenshot({ path: S("t2_reset_mid_boss_turn.png") });
    R.resetMidBossTurn = {
      bossTurnPendingWhenReset: pre.isPlayerTurn === false,
      cardsRightAfterReset: L.countCards(justAfter.grid),
      cardsAfter1200ms: L.countCards(later.grid),
      nudgesAfter: later.nudges, handAfter: later.hand.length, aiPoolAfter: later.aiPool.length,
      bannerAfter: await page.$eval("#last-move-banner", (e) => e.textContent.trim()),
      pass: L.countCards(later.grid).a === 1 && later.nudges === 2,
    };
    await context.close();
  }
  {
    const { page, context } = await fresh(browser);
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 0, r, c, { after: 60 });
    await page.selectOption("#stage-select", "3");
    const justAfter = await L.snap(page);
    await page.waitForTimeout(1200);
    const later = await L.snap(page);
    R.stageSelectMidBossTurn = {
      stageAfter: later.stage, cardsRightAfter: L.countCards(justAfter.grid), cardsAfter1200ms: L.countCards(later.grid), nudgesAfter: later.nudges,
      pass: L.countCards(later.grid).a === 1 && later.nudges === 2,
    };
    await context.close();
  }
  // 10b. Reset during the 460 ms window between game end and modal → stale modal on fresh board?
  {
    const { page, context } = await fresh(browser);
    let guard = 0, ended = false, result = null;
    while (guard++ < 8) {
      await L.waitPlayerTurn(page);
      let s = await L.snap(page);
      if (s.gameOver) break;
      const mv = await L.greedyMove(page);
      if (s.grid.flat().filter((v) => !v).length === 1) {
        // last tile: place and immediately click Reset
        await L.dragHandToSlot(page, mv.idx, mv.r, mv.c, { after: 130 });
        const rb = await page.locator("header button", { hasText: "Reset" }).boundingBox();
        await page.mouse.click(rb.x + rb.width / 2, rb.y + rb.height / 2);
        await page.waitForTimeout(800);
        const after = await L.snap(page);
        result = { modalVisibleOnFreshBoard: after.modal, freshBoardCards: L.countCards(after.grid), gameOverFlag: after.gameOver };
        await page.screenshot({ path: S("t2_reset_during_gameover_delay.png") });
        ended = true; break;
      }
      await L.dragHandToSlot(page, mv.idx, mv.r, mv.c);
    }
    R.resetDuringGameOverDelay = result ? { ...result, pass: !result.modalVisibleOnFreshBoard } : { skipped: "board never reached 1 empty on player turn" };
    await context.close();
  }

  // 11. Nudge / reroll spam
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    const rows = page.locator("#dice-column-list .col-die-row");
    const b1 = await rows.nth(1).boundingBox();
    for (let i = 0; i < 10; i++) await page.mouse.click(b1.x + b1.width / 2, b1.y + b1.height / 2, { delay: 5 });
    await page.waitForTimeout(150);
    const s1 = await L.snap(page);
    const rr = await page.locator("button", { hasText: "Roll All" }).boundingBox();
    for (let i = 0; i < 10; i++) await page.mouse.click(rr.x + rr.width / 2, rr.y + rr.height / 2, { delay: 5 });
    await page.waitForTimeout(150);
    const s2 = await L.snap(page);
    const rerollBtnState = await page.evaluate(() => { const b = [...document.querySelectorAll("button")].find((x) => x.textContent.includes("Roll All")); const cs = getComputedStyle(b); return { disabled: b.disabled, opacity: cs.opacity, cursor: cs.cursor, text: b.textContent.trim().replace(/\s+/g, " ") }; });
    const dieRowState = await page.evaluate(() => { const r = document.querySelector("#dice-column-list .col-die-row"); const cs = getComputedStyle(r); return { opacity: cs.opacity, cursor: cs.cursor, hint: r.textContent.trim().replace(/\s+/g, " ") }; });
    await page.screenshot({ path: S("t2_nudge_reroll_spam.png") });
    // nudge during boss turn
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 0, r, c, { after: 40 });
    const sb = await L.snap(page);
    await page.mouse.click(b1.x + b1.width / 2, b1.y + b1.height / 2);
    const sb2 = await L.snap(page);
    R.nudgeRerollSpam = {
      nudgesStart: s0.nudges, nudgesAfter10Clicks: s1.nudges, die1Start: s0.dice[1], die1After: s1.dice[1],
      rerollsAfter10Clicks: s2.rerolls, rerollBtnWhenExhausted: rerollBtnState, dieRowWhenNoNudges: dieRowState,
      nudgeDuringBossTurnChangedDice: JSON.stringify(sb.dice) !== JSON.stringify(sb2.dice),
      pass: s1.nudges === 0 && s1.dice[1] === ((s0.dice[1] + 1) % 6) + 1 && s2.rerolls === 0,
    };
    await context.close();
  }

  // 12. Fast flick drags: N mouse steps total (no pre-move), release immediately. Also sloppy release.
  {
    const { page, context } = await fresh(browser);
    const trials = [];
    const configs = [
      { steps: 1, fx: 0.5, fy: 0.5 }, { steps: 2, fx: 0.5, fy: 0.5 }, { steps: 3, fx: 0.5, fy: 0.5 }, { steps: 5, fx: 0.5, fy: 0.5 },
      { steps: 1, fx: 0.08, fy: 0.9 }, { steps: 2, fx: 0.92, fy: 0.1 }, { steps: 3, fx: 1.06, fy: 0.5 }, { steps: 2, fx: 0.5, fy: -0.05 },
    ];
    const tiles = [[1, 1], [2, 0], [2, 2], [1, 0], [1, 2], [2, 1], [0, 0], [0, 2]];
    for (const cfg of configs) {
      for (const [r, c] of tiles) {
        const rb = await page.locator("header button", { hasText: "Reset" }).boundingBox();
        await page.mouse.click(rb.x + rb.width / 2, rb.y + rb.height / 2);
        await page.waitForTimeout(350);
        const s0 = await L.snap(page);
        if (s0.grid[r][c]) continue;
        await L.flickHandToSlot(page, 2, r, c, cfg.steps, cfg.fx, cfg.fy, 0);
        await page.waitForTimeout(150);
        const s1 = await L.snap(page);
        const changed = s1.grid.flat().map((v, i) => (v !== s0.grid.flat()[i] && v && v.startsWith("p:" + s0.hand[2]) ? i : -1)).filter((i) => i >= 0);
        trials.push({ ...cfg, tile: [r, c], landedOnIntended: s1.grid[r][c] === "p:" + s0.hand[2], landedIdx: changed.map((i) => [Math.floor(i / 3), i % 3]), placed: s0.hand.length - s1.hand.length, ghostLeft: s1.ghost });
      }
    }
    const byCfg = {};
    trials.forEach((t) => { const k = `steps${t.steps}_fx${t.fx}_fy${t.fy}`; byCfg[k] = byCfg[k] || { n: 0, intended: 0, wrongTile: 0, noPlace: 0 }; byCfg[k].n++; if (t.landedOnIntended) byCfg[k].intended++; else if (t.placed) byCfg[k].wrongTile++; else byCfg[k].noPlace++; });
    R.fastFlick = { byConfig: byCfg, trials, pass: Object.entries(byCfg).filter(([k]) => /fx0.5_fy0.5/.test(k)).every(([, v]) => v.intended === v.n) };
    await context.close();
  }

  // 13. Keyboard during an active drag (Enter / digits while mouse drag held)
  {
    const { page, context } = await fresh(browser);
    const s0 = await L.snap(page);
    let mid;
    const [r, c] = await firstEmpty(page);
    await L.dragHandToSlot(page, 3, r, c, {
      beforeUp: async () => { await page.keyboard.press("Enter"); await page.waitForTimeout(200); mid = await L.snap(page); },
      after: 500,
    });
    const s1 = await L.snap(page);
    R.enterKeyMidDrag = {
      focusedSlotIndex: 4, placedDuringDrag: s0.hand.length - mid.hand.length, ghostStillUp: mid.ghost,
      placedTotal: s0.hand.length - s1.hand.length, gridAfter: s1.grid, ghostAfter: s1.ghost,
      pass: s0.hand.length - mid.hand.length === 0,
    };
    await context.close();
  }

  const pass = Object.fromEntries(Object.entries(R).map(([k, v]) => [k, v && v.pass]));
  L.writeJSON("t2_edge_cases.json", R);
  console.log(JSON.stringify(pass, null, 1));
  console.log(JSON.stringify(R, null, 1).slice(0, 9000));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
