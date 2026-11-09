#!/usr/bin/env node
/**
 * MiroFish 100-Iteration Full-Game & TCG Deckbuilder Persona UI/UX + Intuitiveness Playtest Swarm
 * Executes 100 full matches (10 TCG deckbuilder personas x 10 iterations across Stages 1-15)
 * while auditing tabletop UI/UX, Deckbuilder workflows, Column-Header 3D Dice, Boss Crest Telegraphs,
 * Tactical Slides, and zero-clipping / zero-overflow guarantees.
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const L = require("../../ux_qa/lib");

const URL = process.env.GAME_URL || "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const OUT_DIR = path.resolve(__dirname, "../raw");
const JSONL_OUT = path.join(OUT_DIR, "deckbuilder_100_iterations.jsonl");
const SUMMARY_OUT = path.join(OUT_DIR, "deckbuilder_100_ux_summary.json");

const PERSONAS = [
  {
    id: "P01_Spike_MinMax_Optimizer",
    archetype: "Competitive Min-Max Deckbuilder",
    focus: "Auto-Build Best 5, CardCraft +1 evolution, multi-flip optimization, Column-Header 3D Dice nudges",
    deckStrategy: "autobuild",
    movePolicy: "greedy_flips_plus_corners"
  },
  {
    id: "P02_Johnny_Synergy_Architect",
    archetype: "Faction Synergy & Combo Deckbuilder",
    focus: "Faction filter pills (Aether/Solaris/Valkyria/Chronos/Abyss), 3D Pawn Inspector, Tactical Slide combos",
    deckStrategy: "faction_filter",
    movePolicy: "slide_and_synergy"
  },
  {
    id: "P03_Timmy_Pack_Collector",
    archetype: "Booster Pack Opener & High-Stat Collector",
    focus: "Booster Pack opening (100 coins), locked-card UX feedback, Pulse board-wide telegraph preview",
    deckStrategy: "booster_and_swap",
    movePolicy: "high_stat_center"
  },
  {
    id: "P04_QueenBlood_Lane_Controller",
    archetype: "Column-Header 3D Dice & Lane Buff Tactician",
    focus: "Direct Column-Header 3D Dice clicking (.col-header-pill), column energy surge (.col-surge-active), boosted lane stacking",
    deckStrategy: "autobuild",
    movePolicy: "boosted_lane_priority"
  },
  {
    id: "P05_TripleTriad_Corner_Grandmaster",
    archetype: "Corner Anchor & Directional Edge Mathematician",
    focus: "Octagonal N/E/S/W badges (.edge-num, .boost-pop-badge), flip preview parity (FLIP! vs DEFEND), corner defense",
    deckStrategy: "manual_toggle",
    movePolicy: "corner_fortress"
  },
  {
    id: "P06_IntoTheBreach_Telegraph_Counter",
    archetype: "Boss Telegraph & Target Reticle Counter-Player",
    focus: "Top-of-Board Boss Commander Crest (#boss-tabletop-crest) & Direct Tile Reticle (.boss-target-slot / ⚠️ TARGET)",
    deckStrategy: "autobuild",
    movePolicy: "counter_boss_target"
  },
  {
    id: "P07_Tactical_Slider_Specialist",
    archetype: "Orthogonal Mobility & Board Repositioner",
    focus: "1x/Turn Free Tactical Slide (⇄ SLIDE) into boosted columns and surprise flank captures",
    deckStrategy: "faction_filter",
    movePolicy: "aggressive_slide"
  },
  {
    id: "P08_DragDrop_Tabletop_Purist",
    archetype: "Tactile Tabletop Drag-and-Drop & Physical Deck Stack User",
    focus: "Fanned bottom Hero Hand hover/drag, physical 3D Deck (60) stack (.tabletop-deck-stack), recessed socket drop feel",
    deckStrategy: "tabletop_stack_click",
    movePolicy: "greedy_flips_plus_corners"
  },
  {
    id: "P09_Keyboard_Gamepad_Speedrunner",
    archetype: "Keyboard Shortcut & Fast-Input TCG Player",
    focus: "1-5 hand hotkeys, WASD/Arrow grid navigation, Q/E column dice nudges, Enter/Space deploy",
    deckStrategy: "autobuild",
    movePolicy: "keyboard_fast"
  },
  {
    id: "P10_FirstTime_TCG_Intuitiveness_Auditor",
    archetype: "First-Impression UX, Readability & Accessibility Auditor",
    focus: "Zero text truncation, zero viewport overflow, ◆ ALLY / ▲ FOE ownership clarity, Squad Directional Avg radar",
    deckStrategy: "full_ux_audit",
    movePolicy: "greedy_flips_plus_corners"
  }
];

function launchVisibleMacOSBrowserWithOsascript() {
  try {
    const targetUrl = `${URL}?autotest=1`;
    execSync(
      `osascript -e 'tell application "Safari" to activate' -e 'tell application "Safari" to open location "${targetUrl}"'`,
      { stdio: "ignore", timeout: 5000 }
    );
    return { launched: true, method: "osascript Safari", url: targetUrl };
  } catch (e) {
    try {
      const targetUrl = `${URL}?autotest=1`;
      execSync(`open "${targetUrl}"`, { stdio: "ignore", timeout: 5000 });
      return { launched: true, method: "macOS open", url: targetUrl };
    } catch (e2) {
      return { launched: false, error: String(e2.message || e2) };
    }
  }
}

async function run100Iterations() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  if (fs.existsSync(JSONL_OUT)) fs.unlinkSync(JSONL_OUT);

  const osaLaunch = launchVisibleMacOSBrowserWithOsascript();
  console.log("[osascript] Live game window launch:", JSON.stringify(osaLaunch));

  const browser = await L.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  const consoleErrors = [];
  page.on("pageerror", (err) => consoleErrors.push(String(err)));

  await page.goto(`${URL}?seed=20261108`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#grid-3x3 .board-slot");

  // Speed up AI turn timer during 100-iteration sweep while preserving all state & DOM transitions
  await page.evaluate(() => {
    const origSetTimeout = window.setTimeout;
    window.setTimeout = function (fn, ms, ...args) {
      const capped = typeof ms === "number" && ms > 25 ? 8 : ms;
      return origSetTimeout.call(window, fn, capped, ...args);
    };
  });

  const records = [];
  let totalWins = 0;
  let totalLosses = 0;
  let totalDraws = 0;
  let totalFlips = 0;
  let totalSlidesUsed = 0;
  let totalColHeaderNudges = 0;
  let totalPacksOpened = 0;
  let totalCardCraftEvolutions = 0;
  let totalDeckSwaps = 0;
  let totalPawnInspections = 0;

  const uxAuditTotals = {
    iterationsChecked: 0,
    bossCrestVisible: 0,
    colHeaderDiceInteractive: 0,
    tabletopDeckStackInteractive: 0,
    bossTargetReticleRendered: 0,
    ownershipBadgesRendered: 0,
    octagonalStatMedallionsRendered: 0,
    deckbuilderSquadSummaryRendered: 0,
    deckbuilderFilterPillsWorking: 0,
    lockedCardFeedbackWorking: 0,
    customDeckEquippedToHand: 0,
    zeroNameplateClipping: 0,
    zeroViewportOverflow: 0,
    stageBossInLineup: 0,
    uxIssuesFound: []
  };

  for (let iter = 0; iter < 100; iter++) {
    const persona = PERSONAS[Math.floor(iter / 10)];
    const stageIdx = iter % 15;

    const iterResult = await page.evaluate(
      async ({ iter, persona, stageIdx }) => {
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

        // Grant coins periodically so personas can test Booster Packs & CardCraft in later iterations
        if (state.coins < 260) {
          state.coins += 250;
          saveProgressionV3();
        }

        // Start stage
        const stageSel = document.getElementById("stage-select");
        if (stageSel) stageSel.value = String(stageIdx);
        startStage(stageIdx);
        await sleep(10);

        const campSt = CAMPAIGN_STAGES[stageIdx] || STAGES[stageIdx % STAGES.length];
        const st = STAGES[stageIdx % STAGES.length];
        const firstEnemyId = state.grid[0][1].cardId;
        const allEnemiesInMatch = [firstEnemyId, ...state.aiPool];
        const bossInLineup =
          allEnemiesInMatch.includes(campSt.bossId) && allEnemiesInMatch.includes(st.bossId);

        // 1. Exercise TCG Deckbuilder & 3D Pawn workflows according to persona strategy
        let deckSwaps = 0;
        let packsOpened = 0;
        let evolutions = 0;
        let pawnInspected = false;
        let lockedCardFeedbackOk = true;
        let filterPillsOk = true;
        let squadSummaryOk = true;
        let customDeckInHandOk = true;

        if (persona.deckStrategy === "tabletop_stack_click") {
          const stackEl = document.querySelector(".tabletop-deck-stack");
          if (stackEl) stackEl.click();
        } else {
          openDeckbuilderModal();
        }
        await sleep(6);

        const sqSum = document.getElementById("deckbuilder-squad-summary");
        squadSummaryOk = Boolean(sqSum && sqSum.textContent.includes("SQUAD (") && sqSum.textContent.includes("Avg Stats:"));

        if (persona.deckStrategy === "faction_filter" || persona.deckStrategy === "full_ux_audit") {
          const factions = ["Aether", "Solaris", "Valkyria", "Chronos", "Abyss"];
          const chosenFaction = factions[iter % factions.length];
          setDeckFilter(chosenFaction);
          const filteredCount = document.querySelectorAll("#deckbuilder-grid > div").length;
          setDeckFilter("OWNED");
          const ownedCount = document.querySelectorAll("#deckbuilder-grid > div").length;
          setDeckFilter("ALL");
          const allCount = document.querySelectorAll("#deckbuilder-grid > div").length;
          filterPillsOk = filteredCount === 12 && ownedCount >= 5 && allCount === 60;
        }

        // Test clicking a locked card for UX feedback
        const lockedCard = SET1_60_CATALOG.find((c) => !state.unlockedCards.includes(c.id));
        if (lockedCard) {
          toggleDeckCard(lockedCard.id);
          const statusTxt = document.getElementById("deckbuilder-status")?.textContent || "";
          lockedCardFeedbackOk = statusTxt.includes("locked") || statusTxt.includes("Open Pack");
        }

        // Open booster pack if Timmy or every 4th iteration
        if ((persona.deckStrategy === "booster_and_swap" || iter % 4 === 0) && state.coins >= 100) {
          openBoosterPackUI();
          packsOpened++;
        }

        // Evolve card via CardCraft if Spike or every 5th iteration
        if ((persona.deckStrategy === "autobuild" || iter % 5 === 0) && state.coins >= 150) {
          evolveCardCraftUI();
          evolutions++;
        }

        // Customize active 5-card squad
        if (persona.deckStrategy === "autobuild" || persona.deckStrategy === "full_ux_audit") {
          autoBuildBestSquad();
          deckSwaps++;
        } else {
          const ownedCandidates = state.unlockedCards.filter((cid) => !state.activeDeck.includes(cid));
          if (ownedCandidates.length > 0) {
            const pickCid = ownedCandidates[iter % ownedCandidates.length];
            toggleDeckCard(pickCid);
            deckSwaps++;
          }
        }

        customDeckInHandOk =
          state.hand.length === 5 &&
          state.activeDeck.length === 5 &&
          state.hand.every((cid, idx) => cid === state.activeDeck[idx]);

        closeDeckbuilderModal();

        // Inspect 3D Pawn Hologram if Johnny
        if (persona.id === "P02_Johnny_Synergy_Architect" || iter % 10 === 0) {
          open3DPawnInspectorModal();
          await sleep(5);
          const pTitle = document.getElementById("pawn3d-title")?.textContent || "";
          pawnInspected = pTitle.includes("Watertight 3D");
          close3DPawnInspectorModal();
        }

        // 2. Audit Tabletop UI/UX & Intuitiveness before match play
        const bossCrest = document.getElementById("boss-tabletop-crest");
        const bossCrestRect = bossCrest ? bossCrest.getBoundingClientRect() : null;
        const bossCrestVisible = Boolean(bossCrestRect && bossCrestRect.width > 120 && bossCrestRect.height > 24);

        const colHeaderPills = document.querySelectorAll("#col-headers .col-header-pill");
        const colHeaderDiceBadges = document.querySelectorAll("#col-headers .col-header-die-badge");
        const colHeaderDiceInteractive = colHeaderPills.length === 3 && colHeaderDiceBadges.length === 3;

        const deckStack = document.querySelector(".tabletop-deck-stack");
        const deckStackRect = deckStack ? deckStack.getBoundingClientRect() : null;
        const tabletopDeckStackInteractive = Boolean(deckStackRect && deckStackRect.width >= 40 && deckStackRect.height >= 50);

        const bossTargetSlots = document.querySelectorAll(".board-slot.boss-target-slot");
        const bossTargetReticleRendered = bossTargetSlots.length >= 1;

        const ownershipBadges = document.querySelectorAll(".owner-faction-tag");
        const ownershipBadgesRendered = ownershipBadges.length >= 1;

        const edgeMedallions = document.querySelectorAll(".edge-num");
        const octagonalStatMedallionsRendered = edgeMedallions.length >= 24;

        // Check zero nameplate clipping & zero viewport overflow
        let clippedNames = 0;
        document.querySelectorAll(".slot-name-ribbon").forEach((el) => {
          if (el.scrollWidth > el.clientWidth + 2) clippedNames++;
        });
        const zeroViewportOverflow = document.documentElement.scrollWidth <= window.innerWidth + 1;

        // 3. Play Full 3x3 Match according to Persona Move Policy
        let matchFlips = 0;
        let slidesUsed = 0;
        let colHeaderNudges = 0;
        let turnsTaken = 0;

        for (let turn = 0; turn < 5; turn++) {
          let waitGuard = 0;
          while (!state.isPlayerTurn && !state.gameOver && waitGuard < 60) {
            await sleep(8);
            waitGuard++;
          }
          if (state.gameOver || state.hand.length === 0) break;

          // Step A: Column-Header 3D Die Nudge if beneficial (e.g. bumping Pip 2 or 3 up to 4+ for +1 All Sides)
          while (state.nudgesLeft > 0) {
            let nudged = false;
            for (let c = 0; c < 3; c++) {
              if (state.colDice[c] === 3 || (state.colDice[c] === 2 && state.nudgesLeft >= 2)) {
                const headerPill = document.querySelectorAll("#col-headers .col-header-pill")[c];
                if (headerPill) {
                  headerPill.click();
                  colHeaderNudges++;
                  nudged = true;
                  break;
                }
              }
            }
            if (!nudged) break;
          }

          // Step B: Tactical Slide (1x Free/Turn) if available and persona uses slides
          if (!state.usedSlideThisTurn) {
            let bestSlide = null;
            let bestSlideScore = -1;
            for (let r = 0; r < 3; r++) {
              for (let c = 0; c < 3; c++) {
                if (state.grid[r][c]?.cardId && state.grid[r][c]?.owner === "player") {
                  const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]];
                  for (const [dr, dc] of dirs) {
                    const nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !state.grid[nr][nc].cardId) {
                      const statsAtDest = getCardEffectiveStats(state.grid[r][c].cardId, nc, false);
                      const clashes = findClashes(nr, nc, statsAtDest, "player");
                      const flips = clashes.filter((cl) => cl.willFlip).length;
                      const colBoost = isColBoosted(nc) && !isColBoosted(c) ? 0.5 : 0;
                      const score = flips + colBoost;
                      if (
                        score > bestSlideScore &&
                        (score > 0 || persona.movePolicy === "aggressive_slide" || persona.movePolicy === "slide_and_synergy")
                      ) {
                        bestSlideScore = score;
                        bestSlide = { from: [r, c], to: [nr, nc], flips };
                      }
                    }
                  }
                }
              }
            }
            if (bestSlide) {
              handleSlotClick(bestSlide.from[0], bestSlide.from[1]);
              handleSlotClick(bestSlide.to[0], bestSlide.to[1]);
              slidesUsed++;
              matchFlips += bestSlide.flips;
            }
          }

          // Step C: Choose best (handIdx, r, c) according to persona policy
          let bestMove = null;
          let bestScore = -999;
          const bossTarget = state.bossTargetSlot;

          for (let hIdx = 0; hIdx < state.hand.length; hIdx++) {
            const cid = state.hand[hIdx];
            for (let r = 0; r < 3; r++) {
              for (let c = 0; c < 3; c++) {
                if (state.grid[r][c].cardId) continue;
                const effStats = getCardEffectiveStats(cid, c, false);
                const clashes = findClashes(r, c, effStats, "player");
                const flips = clashes.filter((cl) => cl.willFlip).length;
                const isCorner = (r === 0 || r === 2) && (c === 0 || c === 2);
                const isCenter = r === 1 && c === 1;
                const isBossTarget = bossTarget && bossTarget.r === r && bossTarget.c === c;
                const inBoostedCol = isColBoosted(c);

                let score = flips * 10;
                if (persona.movePolicy === "corner_fortress" && isCorner) score += 4;
                else if (persona.movePolicy === "high_stat_center" && isCenter) score += 3;
                else if (persona.movePolicy === "boosted_lane_priority" && inBoostedCol) score += 4;
                else if (persona.movePolicy === "counter_boss_target" && isBossTarget) score += 5;
                else if (isCorner) score += 1.5;
                if (inBoostedCol) score += 1.2;

                if (score > bestScore) {
                  bestScore = score;
                  bestMove = { hIdx, r, c, flips };
                }
              }
            }
          }

          if (!bestMove) break;
          state.selectedHandIdx = bestMove.hIdx;
          state.selectedBoardSlot = null;
          state.hoveredSlot = { r: bestMove.r, c: bestMove.c };
          renderAll();

          handleSlotClick(bestMove.r, bestMove.c);
          matchFlips += bestMove.flips;
          turnsTaken++;
          await sleep(18);
        }

        let endWait = 0;
        while (!state.gameOver && endWait < 80) {
          await sleep(10);
          endWait++;
        }

        const scores = getScores();
        const outcome = scores.blue > scores.red ? "WIN" : scores.blue < scores.red ? "LOSS" : "DRAW";
        const squadStars = typeof getSquadTotalStars === "function" ? getSquadTotalStars(state.activeDeck) : 10;

        return {
          iter: iter + 1,
          personaId: persona.id,
          archetype: persona.archetype,
          stageIdx,
          stageName: campSt.name,
          outcome,
          playerScore: scores.blue,
          bossScore: scores.red,
          turnsTaken,
          matchFlips,
          slidesUsed,
          colHeaderNudges,
          deckSwaps,
          packsOpened,
          evolutions,
          pawnInspected,
          squadStars,
          uxChecks: {
            bossInLineup,
            bossCrestVisible,
            colHeaderDiceInteractive,
            tabletopDeckStackInteractive,
            bossTargetReticleRendered,
            ownershipBadgesRendered,
            octagonalStatMedallionsRendered,
            squadSummaryOk,
            filterPillsOk,
            lockedCardFeedbackOk,
            customDeckInHandOk,
            zeroNameplateClipping: clippedNames === 0,
            zeroViewportOverflow,
            squadStarCostCapOk: squadStars <= 12
          }
        };
      },
      { iter, persona, stageIdx }
    );

    records.push(iterResult);
    fs.appendFileSync(JSONL_OUT, JSON.stringify(iterResult) + "\n");

    if (iterResult.outcome === "WIN") totalWins++;
    else if (iterResult.outcome === "LOSS") totalLosses++;
    else totalDraws++;

    totalFlips += iterResult.matchFlips;
    totalSlidesUsed += iterResult.slidesUsed;
    totalColHeaderNudges += iterResult.colHeaderNudges;
    totalPacksOpened += iterResult.packsOpened;
    totalCardCraftEvolutions += iterResult.evolutions;
    totalDeckSwaps += iterResult.deckSwaps;
    if (iterResult.pawnInspected) totalPawnInspections++;

    uxAuditTotals.iterationsChecked++;
    const u = iterResult.uxChecks;
    if (u.bossCrestVisible) uxAuditTotals.bossCrestVisible++;
    if (u.colHeaderDiceInteractive) uxAuditTotals.colHeaderDiceInteractive++;
    if (u.tabletopDeckStackInteractive) uxAuditTotals.tabletopDeckStackInteractive++;
    if (u.bossTargetReticleRendered) uxAuditTotals.bossTargetReticleRendered++;
    if (u.ownershipBadgesRendered) uxAuditTotals.ownershipBadgesRendered++;
    if (u.octagonalStatMedallionsRendered) uxAuditTotals.octagonalStatMedallionsRendered++;
    if (u.squadSummaryOk) uxAuditTotals.deckbuilderSquadSummaryRendered++;
    if (u.filterPillsOk) uxAuditTotals.deckbuilderFilterPillsWorking++;
    if (u.lockedCardFeedbackOk) uxAuditTotals.lockedCardFeedbackWorking++;
    if (u.customDeckInHandOk) uxAuditTotals.customDeckEquippedToHand++;
    if (u.zeroNameplateClipping) uxAuditTotals.zeroNameplateClipping++;
    if (u.zeroViewportOverflow) uxAuditTotals.zeroViewportOverflow++;
    if (u.bossInLineup) uxAuditTotals.stageBossInLineup++;

    for (const [k, v] of Object.entries(u)) {
      if (!v) {
        uxAuditTotals.uxIssuesFound.push({ iter: iter + 1, persona: persona.id, check: k });
      }
    }
  }

  const gameTheoryCounters = await page.evaluate(() => ({
    telegraphPowersTriggered: state.telegraphPowersTriggered || 0,
    factionLinksTriggered: state.factionLinksTriggered || 0,
    telegraphDisruptedCount: state.telegraphDisruptedCount || 0,
    bossDiceDrains: state.bossDiceDrains || 0
  }));

  await browser.close();

  const perPersonaSummary = {};
  for (const p of PERSONAS) {
    const pRecs = records.filter((r) => r.personaId === p.id);
    const wins = pRecs.filter((r) => r.outcome === "WIN").length;
    const losses = pRecs.filter((r) => r.outcome === "LOSS").length;
    const draws = pRecs.filter((r) => r.outcome === "DRAW").length;
    perPersonaSummary[p.id] = {
      archetype: p.archetype,
      iterations: pRecs.length,
      wins,
      losses,
      draws,
      winRatePct: Number(((wins / Math.max(1, pRecs.length)) * 100).toFixed(1)),
      avgPlayerScore: Number((pRecs.reduce((s, r) => s + r.playerScore, 0) / Math.max(1, pRecs.length)).toFixed(2)),
      totalFlips: pRecs.reduce((s, r) => s + r.matchFlips, 0),
      totalSlides: pRecs.reduce((s, r) => s + r.slidesUsed, 0),
      totalColHeaderNudges: pRecs.reduce((s, r) => s + r.colHeaderNudges, 0)
    };
  }

  const summary = {
    suite: "MiroFish 100-Iteration TCG Deckbuilder Persona & Tabletop UI/UX Intuitiveness Swarm",
    timestamp: new Date().toISOString(),
    osascriptLaunch: osaLaunch,
    totalIterations: records.length,
    matchOutcomes: {
      wins: totalWins,
      losses: totalLosses,
      draws: totalDraws,
      winRatePct: Number(((totalWins / Math.max(1, records.length)) * 100).toFixed(1))
    },
    gameplayTelemetry: {
      totalFlips,
      totalSlidesUsed,
      totalColHeaderNudges,
      totalDeckSwaps,
      totalPacksOpened,
      totalCardCraftEvolutions,
      totalPawnInspections,
      ...gameTheoryCounters,
      consoleErrorsCount: consoleErrors.length
    },
    uxAuditTotals,
    perPersonaSummary
  };

  fs.writeFileSync(SUMMARY_OUT, JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

run100Iterations().catch((err) => {
  console.error(err);
  process.exit(1);
});
