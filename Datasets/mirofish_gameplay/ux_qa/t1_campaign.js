// T1: Full 4-stage campaign via real-mouse drag & drop only (greedy), through result modal -> Next Stage.
// Also samples DOM counters (CDP Memory.getDOMCounters after forced GC) every turn for leak analysis.
const L = require("./lib");

(async () => {
  const browser = await L.launch();
  const { page, log } = await L.openGame(browser, { viewport: { width: 1408, height: 800 } });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("HeapProfiler.enable");
  const domCounters = async (label) => {
    await cdp.send("HeapProfiler.collectGarbage");
    const c = await cdp.send("Memory.getDOMCounters");
    const live = await page.evaluate(() => ({ liveNodes: document.getElementsByTagName("*").length, heap: performance.memory ? performance.memory.usedJSHeapSize : null }));
    return { label, ...c, ...live };
  };

  const out = { stages: [], domSeries: [], misdrops: [], log };
  out.domSeries.push(await domCounters("initial"));
  const campaignT0 = Date.now();

  for (let s = 0; s < 4; s++) {
    const st0 = await L.snap(page);
    const stage = { stage: s, stageIndexInGame: st0.stage, turns: [], startedAt: Date.now() };
    await page.mouse.move(5, 790); // park the mouse off-board for a neutral screenshot
    await page.waitForTimeout(250);
    await page.screenshot({ path: L.path.join(L.SCREENS, `t1_stage${s + 1}_start.png`) });
    let turn = 0, capShots = 0;
    while (true) {
      await L.waitPlayerTurn(page, 8000);
      const pre = await L.snap(page);
      if (pre.gameOver) break;
      const mv = await L.greedyMove(page);
      if (!mv) break;
      const midShot = turn === 0 ? L.path.join(L.SCREENS, `t1_stage${s + 1}_middrag.png`) : null;
      const tStart = Date.now();
      await L.dragHandToSlot(page, mv.idx, mv.r, mv.c, { midShot, after: 0 });
      // wait for the 120 ms snap animation to commit the placement (or give up after 1.5 s = misdrop)
      const committed = await page.waitForFunction((n) => state.hand.length < n, pre.hand.length, { timeout: 1500 }).then(() => true, () => false);
      const commitMs = Date.now() - tStart;
      const post = await L.snap(page);
      const landed = post.grid[mv.r][mv.c] === "p:" + mv.cid && post.hand.length === pre.hand.length - 1;
      if (!landed) out.misdrops.push({ stage: s, turn, mv, gridAfter: post.grid, hand: post.hand });
      const capturesObserved = L.countCards(post.grid).p - L.countCards(pre.grid).p - (landed ? 1 : 0);
      if (mv.caps > 0) {
        capShots++;
        await page.waitForTimeout(140);
        await page.screenshot({ path: L.path.join(L.SCREENS, `t1_stage${s + 1}_capture${capShots}.png`) });
      }
      // wait boss reply (or game over)
      await page.waitForFunction(() => state.isPlayerTurn || state.gameOver, null, { timeout: 5000 });
      await page.waitForTimeout(150);
      const afterBoss = await L.snap(page);
      stage.turns.push({
        turn, card: mv.cid, tile: [mv.r, mv.c], predictedCaptures: mv.caps, capturesObserved, landed,
        committed, gestureToCommitMs: commitMs,
        bossFlipsAgainstPlayer: Math.max(0, L.countCards(post.grid).p - L.countCards(afterBoss.grid).p),
        scoreAfterBoss: afterBoss.scores,
      });
      out.domSeries.push(await domCounters(`s${s + 1}t${turn}`));
      turn++;
      if (afterBoss.gameOver) break;
      if (turn > 9) break;
    }
    await page.waitForFunction(() => getComputedStyle(document.getElementById("result-modal")).display !== "none", null, { timeout: 4000 });
    await page.waitForTimeout(300);
    const fin = await L.snap(page);
    stage.timeToCompleteMs = Date.now() - stage.startedAt;
    stage.outcome = /VICTORY/.test(fin.modalTitle) ? "WIN" : "LOSS";
    stage.modalTitle = fin.modalTitle;
    stage.finalScores = fin.scores;
    stage.handLeft = fin.hand.length;
    await page.screenshot({ path: L.path.join(L.SCREENS, `t1_stage${s + 1}_result.png`) });
    // Real mouse click on "Next Stage"
    const nb = await page.locator("#result-modal button", { hasText: "Next Stage" }).boundingBox();
    await page.mouse.click(nb.x + nb.width / 2, nb.y + nb.height / 2);
    await page.waitForTimeout(600);
    const nxt = await L.snap(page);
    stage.nextStageLoaded = nxt.stage === (s + 1) % 4 && !nxt.modal && nxt.hand.length === 5;
    stage.stageSelectValueAfter = await page.$eval("#stage-select", (e) => e.value);
    delete stage.startedAt;
    out.stages.push(stage);
    out.domSeries.push(await domCounters(`after_stage${s + 1}`));
  }
  out.campaignMs = Date.now() - campaignT0;
  const d = out.domSeries;
  out.domSummary = {
    nodesFirst: d[0].nodes, nodesLast: d[d.length - 1].nodes,
    liveNodesFirst: d[0].liveNodes, liveNodesLast: d[d.length - 1].liveNodes,
    listenersFirst: d[0].jsEventListeners, listenersLast: d[d.length - 1].jsEventListeners,
    maxNodes: Math.max(...d.map((x) => x.nodes)), maxListeners: Math.max(...d.map((x) => x.jsEventListeners)),
    heapFirst: d[0].heap, heapLast: d[d.length - 1].heap,
  };
  out.imgCheck = await page.evaluate(() => [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.src));
  const p = L.writeJSON("t1_campaign.json", out);
  console.log(JSON.stringify({ file: p, stages: out.stages.map((s) => ({ s: s.stage + 1, outcome: s.outcome, title: s.modalTitle, ms: s.timeToCompleteMs, next: s.nextStageLoaded })), misdrops: out.misdrops.length, dom: out.domSummary, errs: log.pageErrors.length, console: log.console.length, failed: log.failedRequests.length + log.badResponses.length }, null, 1));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
