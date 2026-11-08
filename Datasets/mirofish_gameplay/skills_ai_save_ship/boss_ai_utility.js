#!/usr/bin/env node
/**
 * boss_ai_utility.js
 * Clean-room Utility AI & Hybrid Behavior-Tree Boss Evaluator for CARDFRONT: Cradle of Echoes
 * Adapted for the Gemini 4 Argon (`gemini-4-argon`) + Antigravity Subagent Skill Harness
 *
 * Implements patterns from:
 * - `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md`
 *   (lines 45-57, 75-83, 126-135, 154-158: normalized 0..1 response curves, consideration product with
 *    n-th root compensation `Curves.Compensate(prod, count)`, softmax/argmax selection, hysteresis)
 * - `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md`
 *   (lines 36-41: separation of decision intent from execution)
 *
 * Can be imported in the browser/Playwright or run directly via `/Users/frederickamina/.local/bin/node`
 * to execute a deterministic 4,000-match Monte Carlo benchmark against the current `executeBossTurn` greedy AI.
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ============================================================================
// 1. NORMALIZED 0..1 RESPONSE CURVES (ai-behavior-trees-utility-ai/SKILL.md:126-139)
// ============================================================================
const Curves = {
  clamp01(x) {
    return x < 0 ? 0 : x > 1 ? 1 : x;
  },
  linear(x, min = 0, max = 1) {
    if (Math.abs(max - min) < 1e-9) return 0;
    return Curves.clamp01((x - min) / (max - min));
  },
  quadratic(x, k = 2.0) {
    return Math.pow(Curves.clamp01(x), k);
  },
  exponential(x, k = 3.0) {
    const c = Curves.clamp01(x);
    return (Math.exp(k * c) - 1) / (Math.exp(k) - 1);
  },
  sigmoid(x, k = 8.0, mid = 0.5) {
    const c = Curves.clamp01(x);
    return 1.0 / (1.0 + Math.exp(-k * (c - mid)));
  },
  smoothstep(x) {
    const c = Curves.clamp01(x);
    return c * c * (3 - 2 * c);
  },
  /**
   * Dave Mark / Infinite Axis Utility System (IAUS) geometric mean / makeup compensation
   * Prevents multiplying N considerations in [0,1] from dragging valid multi-factor scores toward 0.
   * Ref: `ai-behavior-trees-utility-ai/SKILL.md:133`
   */
  compensate(product, count) {
    if (count <= 1 || product <= 0) return Curves.clamp01(product);
    const modFactor = 1.0 - 1.0 / count;
    const makeUp = (1.0 - product) * modFactor;
    return Curves.clamp01(product + product * makeUp);
  }
};

// ============================================================================
// 2. DIFFICULTY TIER PRESETS (Apprentice / Tactician / Grandmaster)
// ============================================================================
const DIFFICULTY_TIERS = {
  apprentice: {
    name: "Apprentice (Stage 1 Intro)",
    selectionMode: "softmax",
    temperature: 0.28,
    evaluateFullPool: false, // Draws top card from aiPool like baseline, scores slots via curves
    weights: {
      immediateFlips: 1.0,
      edgeExposureSafety: 0.35,
      cornerCenterControl: 0.25,
      denyBoostedColumn: 0.20,
      counterFlipResistance: 0.15
    }
  },
  tactician: {
    name: "Tactician (Stage 2-3 Midgame)",
    selectionMode: "softmax",
    temperature: 0.08,
    evaluateFullPool: true, // Evaluates all (cardIndex, slot) pairs in aiPool × openSlots
    weights: {
      immediateFlips: 1.25,
      edgeExposureSafety: 0.75,
      cornerCenterControl: 0.55,
      denyBoostedColumn: 0.65,
      counterFlipResistance: 0.70
    }
  },
  grandmaster: {
    name: "Grandmaster (Stage 4 Apex Boss)",
    selectionMode: "argmax",
    temperature: 0.01,
    evaluateFullPool: true,
    weights: {
      immediateFlips: 1.45,
      edgeExposureSafety: 0.95,
      cornerCenterControl: 0.70,
      denyBoostedColumn: 0.85,
      counterFlipResistance: 1.10
    }
  }
};

// ============================================================================
// 3. UTILITY AI CONSIDERATIONS FOR 3x3 DIRECTIONAL CARD BATTLER
// ============================================================================
const DIRS = [
  { dr: -1, dc: 0, myEdge: 0, theirEdge: 2, dirName: "N" },
  { dr: 0,  dc: 1, myEdge: 1, theirEdge: 3, dirName: "E" },
  { dr: 1,  dc: 0, myEdge: 2, theirEdge: 0, dirName: "S" },
  { dr: 0,  dc: -1, myEdge: 3, theirEdge: 1, dirName: "W" }
];

function getEffectiveStats(cardObj, colIdx, isAi, stageAiBonus, colDice) {
  const base = cardObj.nesw;
  if (isAi) {
    return base.map(v => Math.min(9, v + stageAiBonus));
  }
  const boost = colDice[colIdx] >= 4 ? 1 : 0;
  return base.map(v => Math.min(9, v + boost));
}

function findCapturesOnGrid(grid, r, c, nesw, owner) {
  const captured = [];
  for (let i = 0; i < DIRS.length; i++) {
    const d = DIRS[i];
    const nr = r + d.dr, nc = c + d.dc;
    if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) {
      const nb = grid[nr][nc];
      if (nb.cardId && nb.owner !== owner && nesw[d.myEdge] > nb.nesw[d.theirEdge]) {
        captured.push({ nr, nc, myVal: nesw[d.myEdge], theirVal: nb.nesw[d.theirEdge] });
      }
    }
  }
  return captured;
}

/**
 * Computes 5 normalized [0..1] considerations for placing `cardObj` at `(r, c)`:
 * 1. `cFlips`: Quadratic/exponential reward for capturing 1..4 adjacent player cards (`0.22` base if 0 flips so non-flip moves still compete on positioning).
 * 2. `cEdgeSafety`: Sigmoid curve evaluating how strong our outward edges facing EMPTY neighbor sockets are (avoid exposing weak edges to open tiles).
 * 3. `cTopology`: Smoothstep positional value (corners have only 2 exposed sides; center projects 4-way pressure when high-stat).
 * 4. `cColumnDenial`: Linear bonus for occupying a column where the player's die is boosted (>= 4), denying the player a +1 All Sides socket.
 * 5. `cCounterResistance`: 1-ply worst-case lookahead against remaining player hand cards (probability that the placed card + flipped neighbors survive the player's next turn).
 */
function scoreCandidateAction(stateSnapshot, cardMap, cardId, r, c, tierConfig, lastChosenKey = null) {
  const cardObj = cardMap[cardId];
  const aiBonus = stateSnapshot.stageAiBonus || 0;
  const stats = getEffectiveStats(cardObj, c, true, aiBonus, stateSnapshot.colDice);
  const grid = stateSnapshot.grid;

  // Consideration 1: Immediate Captures (0..3+ flips mapped via smooth response curve)
  const flips = findCapturesOnGrid(grid, r, c, stats, "ai");
  const rawFlipRatio = Curves.linear(flips.length, 0, 3);
  const cFlips = 0.22 + 0.78 * Curves.quadratic(rawFlipRatio, 0.75);

  // Consideration 2: Outward Edge Exposure Safety (edges facing empty sockets)
  let exposedEdgeSum = 0;
  let exposedCount = 0;
  let wastedWallSum = 0;
  let wallCount = 0;
  for (let i = 0; i < DIRS.length; i++) {
    const d = DIRS[i];
    const nr = r + d.dr, nc = c + d.dc;
    if (nr < 0 || nr >= 3 || nc < 0 || nc >= 3) {
      wastedWallSum += stats[d.myEdge];
      wallCount++;
    } else if (!grid[nr][nc].cardId) {
      exposedEdgeSum += stats[d.myEdge];
      exposedCount++;
    }
  }
  const meanExposedEdge = exposedCount > 0 ? exposedEdgeSum / (exposedCount * 9.0) : 0.85;
  const meanWallEdge = wallCount > 0 ? wastedWallSum / (wallCount * 9.0) : 0.5;
  // Reward high edges facing open sockets and low edges tucked against board walls
  const safetyRaw = Curves.clamp01(meanExposedEdge * 0.75 + (1.0 - meanWallEdge) * 0.25);
  const cEdgeSafety = Curves.sigmoid(safetyRaw, 6.5, 0.48);

  // Consideration 3: Board Topology (Corner fortresses vs Center crossroads)
  const isCorner = (r === 0 || r === 2) && (c === 0 || c === 2);
  const isCenter = r === 1 && c === 1;
  const avgStat = (stats[0] + stats[1] + stats[2] + stats[3]) / 36.0;
  let topoRaw = 0.5;
  if (isCorner) topoRaw = 0.82; // Only 2 neighbors can ever attack a corner
  else if (isCenter) topoRaw = avgStat >= 0.72 ? 0.88 : 0.35; // Center only good for high-stat cards
  else topoRaw = 0.58;
  const cTopology = Curves.smoothstep(topoRaw);

  // Consideration 4: Deny Player Boosted Column (colDice[c] >= 4 grants player +1 all sides)
  const colPip = stateSnapshot.colDice[c] || 1;
  const cColumnDenial = colPip >= 4 ? Curves.linear(colPip, 3, 6) : 0.35;

  // Consideration 5: 1-Ply Counter-Flip Resistance against Player Hand
  let worstNetLoss = 0;
  if (stateSnapshot.hand && stateSnapshot.hand.length > 0 && exposedCount > 0) {
    // Check adjacent open sockets where player could immediately reply
    for (let i = 0; i < DIRS.length; i++) {
      const d = DIRS[i];
      const nr = r + d.dr, nc = c + d.dc;
      if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !grid[nr][nc].cardId) {
        for (let h = 0; h < stateSnapshot.hand.length; h++) {
          const pCard = cardMap[stateSnapshot.hand[h]];
          if (!pCard) continue;
          const pStats = getEffectiveStats(pCard, nc, false, aiBonus, stateSnapshot.colDice);
          // Opposite edge of d.myEdge is d.theirEdge
          if (pStats[d.theirEdge] > stats[d.myEdge]) {
            worstNetLoss = Math.max(worstNetLoss, 1);
          }
        }
      }
    }
  }
  const cCounterResistance = worstNetLoss > 0 ? 0.38 : 0.95;

  // Combine considerations using weighted geometric/compensatory score
  const w = tierConfig.weights;
  const weightedFactors = [
    Math.pow(cFlips, w.immediateFlips),
    Math.pow(cEdgeSafety, w.edgeExposureSafety),
    Math.pow(cTopology, w.cornerCenterControl),
    Math.pow(cColumnDenial, w.denyBoostedColumn),
    Math.pow(cCounterResistance, w.counterFlipResistance)
  ];
  const prod = weightedFactors.reduce((acc, v) => acc * v, 1.0);
  let utility = Curves.compensate(prod, weightedFactors.length);

  // Hysteresis bonus (+0.035) to prevent tie jitter (`ai-behavior-trees-utility-ai/SKILL.md:155-157`)
  const actionKey = `${cardId}@${r},${c}`;
  if (lastChosenKey && lastChosenKey === actionKey) {
    utility = Curves.clamp01(utility + 0.035);
  }

  return {
    cardId,
    r,
    c,
    flipsCount: flips.length,
    utility,
    considerations: {
      cFlips: Number(cFlips.toFixed(4)),
      cEdgeSafety: Number(cEdgeSafety.toFixed(4)),
      cTopology: Number(cTopology.toFixed(4)),
      cColumnDenial: Number(cColumnDenial.toFixed(4)),
      cCounterResistance: Number(cCounterResistance.toFixed(4))
    }
  };
}

/**
 * Selects the best Boss action `(cardId, poolIdx, r, c)` using the specified difficulty tier.
 */
function selectBossUtilityAction(stateSnapshot, cardMap, tierKey = "grandmaster", rngFn = Math.random) {
  const tier = DIFFICULTY_TIERS[tierKey] || DIFFICULTY_TIERS.grandmaster;
  const openSlots = [];
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      if (!stateSnapshot.grid[r][c].cardId) openSlots.push({ r, c });
    }
  }
  if (openSlots.length === 0 || stateSnapshot.aiPool.length === 0) return null;

  const candidatePoolIndices = tier.evaluateFullPool
    ? stateSnapshot.aiPool.map((_, idx) => idx)
    : [stateSnapshot.aiPool.length - 1];

  const scored = [];
  for (const poolIdx of candidatePoolIndices) {
    const cardId = stateSnapshot.aiPool[poolIdx];
    for (const slot of openSlots) {
      const evalRes = scoreCandidateAction(stateSnapshot, cardMap, cardId, slot.r, slot.c, tier);
      evalRes.poolIdx = poolIdx;
      scored.push(evalRes);
    }
  }

  scored.sort((a, b) => b.utility - a.utility);

  if (tier.selectionMode === "argmax" || scored.length === 1) {
    return { chosen: scored[0], topCandidates: scored.slice(0, 5) };
  }

  // Softmax selection for controlled variety on lower/mid tiers
  const maxU = scored[0].utility;
  const temp = Math.max(0.01, tier.temperature);
  const exps = scored.map(s => Math.exp((s.utility - maxU) / temp));
  const sumExp = exps.reduce((a, b) => a + b, 0);
  let pick = rngFn() * sumExp;
  for (let i = 0; i < scored.length; i++) {
    pick -= exps[i];
    if (pick <= 0) {
      return { chosen: scored[i], topCandidates: scored.slice(0, 5) };
    }
  }
  return { chosen: scored[0], topCandidates: scored.slice(0, 5) };
}

// ============================================================================
// 4. HEADLESS BENCHMARK HARNESS (Greedy Baseline vs Utility AI Tiers)
// ============================================================================
const PLAYER_HEROES = [
  { id: "h_archangel", name: "Solar Archangel", nesw: [8, 7, 6, 7] },
  { id: "h_phoenix",   name: "Phoenix Valkyrie", nesw: [9, 8, 5, 6] },
  { id: "h_oracle",    name: "Lunar Oracle", nesw: [7, 7, 8, 7] },
  { id: "h_chronos",   name: "Chronos Weaver", nesw: [6, 8, 7, 7] },
  { id: "h_seraph",    name: "Astral Seraph", nesw: [8, 6, 7, 8] },
  { id: "h_kai",       name: "Kai Crimson Visor", nesw: [7, 8, 6, 7] },
  { id: "h_valkyrie",  name: "Sky-Wing Striker", nesw: [8, 8, 5, 6] },
  { id: "h_arbiter",   name: "Sun Arbiter", nesw: [7, 7, 8, 8] }
];

const ENEMY_MECHS = [
  { id: "e_eclipse",  name: "Eclipse Void Blade", nesw: [6, 6, 5, 6] },
  { id: "e_archon",   name: "Prism Core Archon", nesw: [7, 6, 6, 5] },
  { id: "e_inferno",  name: "Inferno Seraph", nesw: [7, 7, 5, 6] },
  { id: "e_reaper",   name: "Sigil Wraith", nesw: [6, 7, 7, 5] },
  { id: "e_titan",    name: "Bastion Dreadnought", nesw: [7, 5, 7, 6] },
  { id: "e_colossus", name: "Emerald Colossus", nesw: [6, 8, 5, 6] },
  { id: "e_cryo",     name: "Cryo Interceptor", nesw: [5, 7, 6, 7] },
  { id: "e_shinobi",  name: "Cyber Shinobi", nesw: [7, 6, 6, 5] }
];

const STAGES = [
  { stageIndex: 0, name: "Stage 1: Skystone Sanctuary", aiBonus: 0 },
  { stageIndex: 1, name: "Stage 2: Ivalice Citadel",    aiBonus: 0 },
  { stageIndex: 2, name: "Stage 3: Orbital Mecha Bay",  aiBonus: 1 },
  { stageIndex: 3, name: "Stage 4: Apex Neural Core",   aiBonus: 1 }
];

const CARD_MAP = {};
[...PLAYER_HEROES, ...ENEMY_MECHS].forEach(c => { CARD_MAP[c.id] = c; });

// Mulberry32 seeded PRNG for reproducible head-to-head comparisons
function makeSeededRng(seed) {
  let a = seed >>> 0;
  return function() {
    let t = (a += 0x6D2B79F5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function seededShuffle(arr, rng) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function simulateSingleMatch(stageIdx, bossPolicy, playerPolicy, seed) {
  const rng = makeSeededRng(seed);
  const stageAiBonus = STAGES[stageIdx].aiBonus;
  const colDice = [4, 2, 5];

  const heroes = seededShuffle(PLAYER_HEROES, rng);
  const enemies = seededShuffle(ENEMY_MECHS, rng);

  const grid = [];
  for (let r = 0; r < 3; r++) {
    const row = [];
    for (let c = 0; c < 3; c++) {
      row.push({ r, c, cardId: null, owner: null, nesw: [0, 0, 0, 0] });
    }
    grid.push(row);
  }

  const firstEnemy = enemies.pop();
  grid[0][1].cardId = firstEnemy.id;
  grid[0][1].owner = "ai";
  grid[0][1].nesw = getEffectiveStats(firstEnemy, 1, true, stageAiBonus, colDice);

  const hand = heroes.slice(0, 5).map(h => h.id);
  const aiPool = enemies.slice(0, 5).map(e => e.id);

  let bossTotalFlips = 0;
  let playerTotalFlips = 0;

  // 4 turns fill the remaining 8 sockets (player places 4, boss places 4)
  for (let turn = 0; turn < 4; turn++) {
    // --- PLAYER TURN ---
    const openP = [];
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        if (!grid[r][c].cardId) openP.push({ r, c });
      }
    }
    if (openP.length === 0 || hand.length === 0) break;

    let chosenHandIdx = 0;
    let chosenSlotP = openP[0];

    if (playerPolicy === "greedy") {
      let bestF = -1;
      for (let hi = 0; hi < hand.length; hi++) {
        for (const s of openP) {
          const eff = getEffectiveStats(CARD_MAP[hand[hi]], s.c, false, stageAiBonus, colDice);
          const f = findCapturesOnGrid(grid, s.r, s.c, eff, "player").length;
          if (f > bestF) {
            bestF = f;
            chosenHandIdx = hi;
            chosenSlotP = s;
          }
        }
      }
    } else {
      chosenHandIdx = Math.floor(rng() * hand.length);
      chosenSlotP = openP[Math.floor(rng() * openP.length)];
    }

    const pCardId = hand.splice(chosenHandIdx, 1)[0];
    const pCell = grid[chosenSlotP.r][chosenSlotP.c];
    pCell.cardId = pCardId;
    pCell.owner = "player";
    pCell.nesw = getEffectiveStats(CARD_MAP[pCardId], chosenSlotP.c, false, stageAiBonus, colDice);
    const pFlips = findCapturesOnGrid(grid, chosenSlotP.r, chosenSlotP.c, pCell.nesw, "player");
    pFlips.forEach(f => { grid[f.nr][f.nc].owner = "player"; });
    playerTotalFlips += pFlips.length;

    // --- BOSS TURN ---
    const openB = [];
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        if (!grid[r][c].cardId) openB.push({ r, c });
      }
    }
    if (openB.length === 0 || aiPool.length === 0) break;

    let bCardId = null;
    let bSlot = null;

    if (bossPolicy === "greedy_current") {
      // Exact replica of WebPlayable executeBossTurn (lines 1772-1780)
      bCardId = aiPool.pop();
      bSlot = openB[Math.floor(rng() * openB.length)];
      let bestCount = -1;
      for (const slot of openB) {
        const stats = getEffectiveStats(CARD_MAP[bCardId], slot.c, true, stageAiBonus, colDice);
        const f = findCapturesOnGrid(grid, slot.r, slot.c, stats, "ai").length;
        if (f > bestCount) {
          bestCount = f;
          bSlot = slot;
        }
      }
    } else {
      const snap = { grid, aiPool, hand, colDice, stageAiBonus };
      const res = selectBossUtilityAction(snap, CARD_MAP, bossPolicy, rng);
      bCardId = aiPool.splice(res.chosen.poolIdx, 1)[0];
      bSlot = { r: res.chosen.r, c: res.chosen.c };
    }

    const bCell = grid[bSlot.r][bSlot.c];
    bCell.cardId = bCardId;
    bCell.owner = "ai";
    bCell.nesw = getEffectiveStats(CARD_MAP[bCardId], bSlot.c, true, stageAiBonus, colDice);
    const bFlips = findCapturesOnGrid(grid, bSlot.r, bSlot.c, bCell.nesw, "ai");
    bFlips.forEach(f => { grid[f.nr][f.nc].owner = "ai"; });
    bossTotalFlips += bFlips.length;
  }

  let blue = 0, red = 0;
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      if (grid[r][c].owner === "player") blue++;
      else if (grid[r][c].owner === "ai") red++;
    }
  }
  return {
    bossWin: red > blue,
    playerWin: blue > red,
    blue,
    red,
    bossTotalFlips,
    playerTotalFlips
  };
}

function runBenchmarkSuite(matchesPerStage = 500) {
  const policies = ["greedy_current", "apprentice", "tactician", "grandmaster"];
  const playerPolicies = ["greedy", "random"];
  const results = {};

  for (const pPol of playerPolicies) {
    results[pPol] = {};
    for (const bPol of policies) {
      let totalBossWins = 0;
      let totalMatches = 0;
      let totalBossCards = 0;
      let totalBossFlips = 0;
      const byStage = [];

      for (let s = 0; s < STAGES.length; s++) {
        let sBossWins = 0;
        let sBossCards = 0;
        let sBossFlips = 0;
        for (let m = 0; m < matchesPerStage; m++) {
          const seed = 100000 + s * 10000 + m;
          const out = simulateSingleMatch(s, bPol, pPol, seed);
          if (out.bossWin) sBossWins++;
          sBossCards += out.red;
          sBossFlips += out.bossTotalFlips;
        }
        totalBossWins += sBossWins;
        totalMatches += matchesPerStage;
        totalBossCards += sBossCards;
        totalBossFlips += sBossFlips;
        byStage.push({
          stage: STAGES[s].name,
          aiBonus: STAGES[s].aiBonus,
          matches: matchesPerStage,
          bossWinRate: Number((sBossWins / matchesPerStage).toFixed(4)),
          playerWinRate: Number((1 - sBossWins / matchesPerStage).toFixed(4)),
          avgBossFinalCards: Number((sBossCards / matchesPerStage).toFixed(3)),
          avgBossCapturesPerMatch: Number((sBossFlips / matchesPerStage).toFixed(3))
        });
      }

      results[pPol][bPol] = {
        bossPolicy: bPol,
        playerPolicy: pPol,
        totalMatches,
        overallBossWinRate: Number((totalBossWins / totalMatches).toFixed(4)),
        overallPlayerWinRate: Number((1 - totalBossWins / totalMatches).toFixed(4)),
        avgBossFinalCards: Number((totalBossCards / totalMatches).toFixed(3)),
        avgBossCapturesPerMatch: Number((totalBossFlips / totalMatches).toFixed(3)),
        byStage
      };
    }
  }
  return results;
}

if (require.main === module) {
  const outDir = path.join(__dirname, "raw");
  fs.mkdirSync(outDir, { recursive: true });
  const bench = runBenchmarkSuite(500);
  const outPath = path.join(outDir, "ai_benchmark.json");
  fs.writeFileSync(outPath, JSON.stringify(bench, null, 2));
  console.log("Wrote Utility AI benchmark to:", outPath);
  for (const pPol of Object.keys(bench)) {
    console.log(`\n=== vs Player Policy: ${pPol.toUpperCase()} ===`);
    for (const bPol of Object.keys(bench[pPol])) {
      const r = bench[pPol][bPol];
      console.log(
        `  ${bPol.padEnd(16)} | Boss WinRate: ${(r.overallBossWinRate * 100).toFixed(1)}% | ` +
        `Avg Boss Cards: ${r.avgBossFinalCards.toFixed(2)} | Avg Flips: ${r.avgBossCapturesPerMatch.toFixed(2)} | ` +
        `S1..S4 Boss WR: ${r.byStage.map(x => (x.bossWinRate * 100).toFixed(1) + "%").join(" / ")}`
      );
    }
  }
}

module.exports = {
  Curves,
  DIFFICULTY_TIERS,
  scoreCandidateAction,
  selectBossUtilityAction,
  runBenchmarkSuite
};
