// Externalized E2E / Synthetic Drag & Automated Playtest Harness
// Loaded when ?autotest=1 or ?dragtest=1 is present in the query string.

async function runDragDropTest() {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const res = { suite: "CARDFRONT drag & drop (synthetic pointer events)", checks: {} };
  const prog = (step) => { document.title = "DT:" + step; };
  prog("start");
  const fire = (target, type, x, y) => target.dispatchEvent(new PointerEvent(type, {
    bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, buttons: type === "pointerup" ? 0 : 1,
    pointerId: 1, pointerType: "mouse", isPrimary: true
  }));
  const center = (el) => { const r = el.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
  async function glide(x0, y0, x1, y1, steps, holdMs) {
    for (let i = 1; i <= steps; i++) {
      const t = i / steps, e = t * t * (3 - 2 * t);
      fire(document, "pointermove", x0 + (x1 - x0) * e, y0 + (y1 - y0) * e);
      await sleep(16);
    }
    if (holdMs) await sleep(holdMs);
  }
  const slotEl = (r, c) => document.querySelector(`#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`);
  const firstEmpty = () => { for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!state.grid[r][c].cardId) return [r, c]; return null; };

  let handBefore = state.hand.length;
  let wrap = document.querySelectorAll("#hand-bar .hand-card-wrap")[0];
  let [hx, hy] = center(wrap);
  fire(wrap, "pointerdown", hx, hy);
  await glide(hx, hy, hx + 40, 20, 14, 200);
  prog("glide1-done");
  res.checks.ghostCreated = !!document.querySelector(".drag-ghost");
  fire(document, "pointerup", hx + 40, 20);
  await sleep(380);
  prog("invalid-done");
  res.checks.invalidDropReturned = state.hand.length === handBefore && !document.querySelector(".drag-ghost");

  handBefore = state.hand.length;
  const [tr, tc] = firstEmpty();
  wrap = document.querySelectorAll("#hand-bar .hand-card-wrap")[1];
  const cardId = state.hand[1];
  [hx, hy] = center(wrap);
  const [sx, sy] = center(slotEl(tr, tc));
  fire(wrap, "pointerdown", hx, hy);
  await glide(hx, hy, sx + 18, sy - 10, 30, 0);
  res.checks.dropHoverHighlighted = !!document.querySelector(".board-slot.drop-hover");
  res.checks.landingPreviewShown = !!document.querySelector(".board-slot.landing-preview");
  res.checks.validTargetsPulsing = document.querySelectorAll(".board-slot.drop-valid").length;
  document.title = "DRAG_HOLD";
  await sleep(2200);
  fire(document, "pointerup", sx + 18, sy - 10);
  await sleep(500);
  prog("drop-done");
  res.checks.validDropPlaced = state.grid[tr][tc].cardId === cardId && state.hand.length === handBefore - 1;
  res.checks.ghostRemoved = !document.querySelector(".drag-ghost");

  while (!state.isPlayerTurn && !state.gameOver) await sleep(100);
  await sleep(300);
  wrap = document.querySelectorAll("#hand-bar .hand-card-wrap")[2];
  if (wrap) {
    [hx, hy] = center(wrap);
    fire(wrap, "pointerdown", hx, hy);
    fire(document, "pointerup", hx, hy);
    wrap.click();
    await sleep(100);
    res.checks.clickSelectStillWorks = state.selectedHandIdx === 2 && !document.querySelector(".drag-ghost");
  }

  res.pass = Object.values(res.checks).every(v => v === true || (typeof v === "number" && v > 0));
  window.__DRAG_TEST__ = res;
  try {
    await fetch("/__osascript_report__?name=dragdrop", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(res, null, 2) });
  } catch (e) {}
  document.title = `DRAGTEST_COMPLETE:PASS=${res.pass}`;
}

async function runVisualAutomatedPlaytest() {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const report = {
    suite: "CARDFRONT 3D Tabletop, 16 Unique Telegraphs & 3:4 Mastered Portrait E2E Playtest (osascript)",
    timestamp: new Date().toISOString(),
    steps: [],
    imagesChecked: 0,
    allImagesLoaded: true,
    imageDimensionsVerified: true,
    singletonVerified: true,
    duplicateCardsFound: 0,
    telegraphSVGsRendered: 0,
    cameraModesTested: [],
    diceActionsTested: [],
    turnsPlayed: 0,
    capturesTriggered: 0,
    tacticalSlideTested: false,
    modalDisplayed: false,
    finalScore: { player: 0, boss: 0 },
    outcome: ""
  };

  async function checkSingletonAndImages() {
    const seen = new Set();
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        if (cell && cell.cardId) {
          if (seen.has(cell.cardId)) {
            report.singletonVerified = false;
            report.duplicateCardsFound++;
          }
          seen.add(cell.cardId);
        }
      }
    }
    for (const cid of state.hand) {
      if (seen.has(cid)) {
        report.singletonVerified = false;
        report.duplicateCardsFound++;
      }
      seen.add(cid);
    }
    const imgs = Array.from(document.querySelectorAll(".slot-art"));
    await Promise.all(imgs.filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 400); })));
    report.imagesChecked = Math.max(report.imagesChecked, imgs.length);
    for (const img of imgs) {
      if (!img.complete || img.naturalWidth === 0) {
        report.allImagesLoaded = false;
      } else if (img.naturalWidth !== 600 || img.naturalHeight !== 800) {
        report.imageDimensionsVerified = false;
      }
    }
    const telegraphs = document.querySelectorAll(".card-telegraph-fx");
    report.telegraphSVGsRendered = Math.max(report.telegraphSVGsRendered, telegraphs.length);
  }

  await sleep(400);
  await checkSingletonAndImages();
  report.steps.push({
    step: "Initial Stage Load",
    stage: STAGES[state.stageIndex % STAGES.length].name,
    handCount: state.hand.length,
    imagesChecked: report.imagesChecked,
    telegraphSVGsRendered: report.telegraphSVGsRendered
  });

  for (const camVal of ["14,0", "0,0", "5,0"]) {
    const camSel = document.getElementById("camera-select");
    if (camSel) camSel.value = camVal;
    setBoardCamera(camVal);
    report.cameraModesTested.push(camVal);
    await sleep(220);
  }

  nudgeColDie(0);
  report.diceActionsTested.push("nudgeColDie(0)");
  await sleep(300);
  rerollAllDice();
  report.diceActionsTested.push("rerollAllDice()");
  await sleep(380);

  for (let turn = 0; turn < 4; turn++) {
    while (!state.isPlayerTurn && !state.gameOver) {
      await sleep(100);
    }
    if (state.hand.length === 0 || state.gameOver) break;

    if (!report.tacticalSlideTested && !state.usedSlideThisTurn) {
      outerSlide: for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          if (state.grid[r][c] && state.grid[r][c].cardId && state.grid[r][c].owner === "player") {
            const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
            for (const [dr, dc] of dirs) {
              const nr = r + dr, nc = c + dc;
              if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !state.grid[nr][nc].cardId) {
                handleSlotClick(r, c);
                await sleep(160);
                handleSlotClick(nr, nc);
                report.tacticalSlideTested = true;
                report.steps.push({ step: "Tactical Slide (1x Free/Turn)", from: [r, c], to: [nr, nc] });
                await sleep(220);
                break outerSlide;
              }
            }
          }
        }
      }
    }

    state.selectedHandIdx = 0;
    state.selectedBoardSlot = null;
    updateTelegraphHud(state.hand[0]);
    renderAll();
    await sleep(150);

    let bestRC = null;
    let bestFlips = -1;
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        if (!state.grid[r][c].cardId) {
          const effStats = getCardEffectiveStats(state.hand[0], c, false);
          const clashes = findClashes(r, c, effStats, "player");
          const flips = clashes.filter(cl => cl.willFlip).length;
          if (flips > bestFlips) {
            bestFlips = flips;
            bestRC = [r, c];
          }
        }
      }
    }
    if (!bestRC) break;
    const [tr, tc] = bestRC;
    state.hoveredSlot = { r: tr, c: tc };
    renderAll();
    await sleep(180);

    const cardPlayed = state.hand[0];
    report.capturesTriggered += Math.max(0, bestFlips);
    handleSlotClick(tr, tc);
    report.turnsPlayed++;
    await sleep(800);
    await checkSingletonAndImages();
    const sc = getScores();
    report.steps.push({
      step: `Turn ${turn + 1} Deploy`,
      cardPlayed,
      telegraph: ALL_CARDS[cardPlayed] ? ALL_CARDS[cardPlayed].telegraphName : "",
      socket: [tr, tc],
      immediateCaptures: bestFlips,
      scoreAfterTurn: { player: sc.blue, boss: sc.red }
    });
  }

  await sleep(650);
  await checkSingletonAndImages();
  const finalScores = getScores();
  report.finalScore = { player: finalScores.blue, boss: finalScores.red };
  const modalEl = document.getElementById("result-modal");
  report.modalDisplayed = modalEl ? (modalEl.style.display === "flex" || modalEl.classList.contains("show")) : false;
  report.outcome = finalScores.blue > finalScores.red ? "VICTORY" : (finalScores.blue < finalScores.red ? "DEFEAT" : "DRAW");

  window.__OSASCRIPT_TEST_REPORT__ = report;
  try {
    await fetch("/__osascript_report__", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(report, null, 2)
    });
  } catch (e) {}

  document.title = `TEST_COMPLETE:${report.finalScore.player}-${report.finalScore.boss}:SINGLETON=${report.singletonVerified}:IMG=${report.allImagesLoaded && report.imageDimensionsVerified}`;
  return JSON.stringify(report);
}
