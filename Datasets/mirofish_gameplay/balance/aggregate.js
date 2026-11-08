// Aggregator for CARDFRONT: Cradle of Echoes balance simulations.
// Reads Datasets/mirofish_gameplay/balance/results/raw/*.csv (main_* and var_*)
// and writes Datasets/mirofish_gameplay/balance/results/summary.json.
"use strict";
const fs = require("fs");
const path = require("path");
const E = require("./engine");

const RAW_DIR = path.join(__dirname, "results", "raw");
const OUT_FILE = path.join(__dirname, "results", "summary.json");

function round(v, d = 2) {
  if (v == null || Number.isNaN(v)) return null;
  const f = Math.pow(10, d);
  return Math.round(v * f) / f;
}

function ci95Pct(wins, n) {
  if (!n) return 0;
  const p = wins / n;
  return round(1.96 * Math.sqrt((p * (1 - p)) / n) * 100, 2);
}

function parseActions(actStr) {
  const res = {
    nudges: 0,
    rerolls: 0,
    slides: [],
    places: [],
    bossMoves: [],
    playerFlips: 0,
    slideFlips: 0,
    bossFlips: 0,
  };
  if (!actStr) return res;
  const toks = actStr.split(" ");
  for (let i = 0; i < toks.length; i++) {
    const t = toks[i];
    if (!t) continue;
    const ch = t[0];
    if (ch === "N") {
      res.nudges++;
    } else if (ch === "R") {
      res.rerolls++;
    } else if (ch === "S") {
      // S<card>:<from>><to>:<flips>
      const m = /^S(\d+):(\d+)>(\d+):(\d+)$/.exec(t);
      if (m) {
        const card = +m[1], from = +m[2], to = +m[3], flips = +m[4];
        res.slides.push({ card, from, to, flips });
        res.slideFlips += flips;
      }
    } else if (ch === "P") {
      // P<card>@<cell>:<flips>
      const m = /^P(\d+)@(\d+):(\d+)$/.exec(t);
      if (m) {
        const card = +m[1], cell = +m[2], flips = +m[3];
        res.places.push({ card, cell, flips, turn: res.places.length });
        res.playerFlips += flips;
      }
    } else if (ch === "B") {
      // B<card>@<slot>:<flips>
      const m = /^B(\d+)@(\d+):(\d+)$/.exec(t);
      if (m) {
        const card = +m[1], slot = +m[2], flips = +m[3];
        res.bossMoves.push({ card, slot, flips, turn: res.bossMoves.length });
        res.bossFlips += flips;
      }
    }
  }
  return res;
}

function loadCsvFiles(prefixFilter) {
  const files = fs.readdirSync(RAW_DIR).filter(f => f.endsWith(".csv") && f.startsWith(prefixFilter)).sort();
  const rows = [];
  for (const f of files) {
    const text = fs.readFileSync(path.join(RAW_DIR, f), "utf8").trim();
    if (!text) continue;
    const lines = text.split("\n");
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      const [label, policy, stageStr, seedStr, handStr, openerStr, poolStr, blueStr, redStr, winStr, actionsStr, unusedStr, rootValStr] = line.split(",");
      const hand = handStr ? handStr.split("-").map(Number) : [];
      const pool = poolStr ? poolStr.split("-").map(Number) : [];
      const unused = unusedStr ? unusedStr.split("-").map(Number) : [];
      const acts = parseActions(actionsStr);
      rows.push({
        label,
        policy,
        stage: +stageStr,
        seed: +seedStr,
        hand,
        opener: +openerStr,
        pool,
        blue: +blueStr,
        red: +redStr,
        win: +winStr === 1,
        unused,
        rootValue: rootValStr !== "" && rootValStr != null ? +rootValStr : null,
        acts,
      });
    }
  }
  return rows;
}

function summarizeGroup(rows) {
  const n = rows.length;
  if (!n) return null;
  let wins = 0, draws = 0, losses = 0;
  let sumBlue = 0, sumSqBlue = 0, sumRed = 0;
  let sumPFlips = 0, sumSFlips = 0, sumBFlips = 0;
  let sumNudges = 0, sumRerolls = 0, sumSlides = 0, gamesWithSlide = 0;
  let sumRootVal = 0, nRootVal = 0, rootValOne = 0, rootValZero = 0;
  const blueHist = new Array(10).fill(0);

  for (const r of rows) {
    if (r.blue > r.red) wins++;
    else if (r.blue === r.red) draws++;
    else losses++;
    sumBlue += r.blue;
    sumSqBlue += r.blue * r.blue;
    sumRed += r.red;
    blueHist[r.blue] = (blueHist[r.blue] || 0) + 1;

    sumPFlips += r.acts.playerFlips;
    sumSFlips += r.acts.slideFlips;
    sumBFlips += r.acts.bossFlips;
    sumNudges += r.acts.nudges;
    sumRerolls += r.acts.rerolls;
    sumSlides += r.acts.slides.length;
    if (r.acts.slides.length > 0) gamesWithSlide++;

    if (r.rootValue != null) {
      sumRootVal += r.rootValue;
      nRootVal++;
      if (r.rootValue >= 1 - 1e-6) rootValOne++;
      if (r.rootValue <= 1e-6) rootValZero++;
    }
  }
  const meanBlue = sumBlue / n;
  const varBlue = Math.max(0, sumSqBlue / n - meanBlue * meanBlue);
  return {
    n,
    wins,
    draws,
    losses,
    winRatePct: round((100 * wins) / n, 2),
    drawRatePct: round((100 * draws) / n, 2),
    lossRatePct: round((100 * losses) / n, 2),
    winRateCI95Pct: ci95Pct(wins, n),
    meanBlue: round(meanBlue, 3),
    sdBlue: round(Math.sqrt(varBlue), 3),
    meanRed: round(sumRed / n, 3),
    meanMargin: round((sumBlue - sumRed) / n, 3),
    meanPlayerDeployFlips: round(sumPFlips / n, 3),
    meanSlideFlips: round(sumSFlips / n, 3),
    meanTotalPlayerFlips: round((sumPFlips + sumSFlips) / n, 3),
    meanBossFlips: round(sumBFlips / n, 3),
    meanNudges: round(sumNudges / n, 3),
    meanRerolls: round(sumRerolls / n, 3),
    meanSlides: round(sumSlides / n, 3),
    slideGamePct: round((100 * gamesWithSlide) / n, 2),
    meanRootValue: nRootVal ? round(sumRootVal / nRootVal, 4) : null,
    sureWinAtRootPct: nRootVal ? round((100 * rootValOne) / nRootVal, 2) : null,
    unwinnableAtRootPct: nRootVal ? round((100 * rootValZero) / nRootVal, 2) : null,
    blueScoreDistPct: blueHist.map(c => round((100 * c) / n, 2)),
  };
}

function main() {
  const mainRows = loadCsvFiles("main_");
  const varRows = loadCsvFiles("var_");

  // 1. By Policy & Stage
  const byPolicyStage = {};
  const policies = [...new Set(mainRows.map(r => r.policy))];
  for (const pol of policies) {
    byPolicyStage[pol] = {};
    for (const st of [0, 1, 2, 3]) {
      const sub = mainRows.filter(r => r.policy === pol && r.stage === st);
      if (sub.length) byPolicyStage[pol][`stage${st + 1}`] = summarizeGroup(sub);
    }
    byPolicyStage[pol].stages1_2 = summarizeGroup(mainRows.filter(r => r.policy === pol && (r.stage === 0 || r.stage === 1)));
    byPolicyStage[pol].stages3_4 = summarizeGroup(mainRows.filter(r => r.policy === pol && (r.stage === 2 || r.stage === 3)));
    byPolicyStage[pol].overall = summarizeGroup(mainRows.filter(r => r.policy === pol));
  }

  // 2. Skill Gap & Information Value
  const skillGap = {};
  for (const key of ["stage1", "stage2", "stage3", "stage4", "stages1_2", "stages3_4", "overall"]) {
    const rnd = byPolicyStage.random?.[key];
    const grd = byPolicyStage.greedy?.[key];
    const gal = byPolicyStage.greedy_all?.[key];
    const lka = byPolicyStage.lookahead?.[key];
    const exp = byPolicyStage.expert?.[key];
    const exm = byPolicyStage.expert_margin?.[key];
    const orc = byPolicyStage.oracle?.[key];
    if (!rnd || !exp) continue;
    skillGap[key] = {
      randomWinPct: rnd.winRatePct,
      greedyWinPct: grd?.winRatePct,
      greedyAllWinPct: gal?.winRatePct,
      lookaheadWinPct: lka?.winRatePct,
      expertWinPct: exp.winRatePct,
      expertMarginWinPct: exm?.winRatePct,
      oracleWinPct: orc?.winRatePct,
      expertMinusRandomWinPct: round(exp.winRatePct - rnd.winRatePct, 2),
      expertMinusGreedyWinPct: grd ? round(exp.winRatePct - grd.winRatePct, 2) : null,
      greedyMinusRandomWinPct: grd ? round(grd.winRatePct - rnd.winRatePct, 2) : null,
      greedyAllMinusGreedyWinPct: (gal && grd) ? round(gal.winRatePct - grd.winRatePct, 2) : null,
      oracleMinusExpertWinPct: orc ? round(orc.winRatePct - exp.winRatePct, 2) : null,
      expertMinusRandomBlue: round(exp.meanBlue - rnd.meanBlue, 3),
      expertMarginMinusExpertBlue: exm ? round(exm.meanBlue - exp.meanBlue, 3) : null,
    };
  }

  // 3. Dice & Slide Marginal Value (Greedy & Expert Ablations)
  const diceAndSlideValue = {};
  for (const key of ["stage1", "stage2", "stage3", "stage4", "stages1_2", "stages3_4", "overall"]) {
    const g0 = byPolicyStage.greedy?.[key];
    const gd = byPolicyStage.greedy_dice?.[key];
    const gs = byPolicyStage.greedy_slide?.[key];
    const ga = byPolicyStage.greedy_all?.[key];

    const e0 = byPolicyStage.expert_notools?.[key];
    const ed = byPolicyStage.expert_noslide?.[key]; // has dice, no slide
    const es = byPolicyStage.expert_nodice?.[key];  // has slide, no dice
    const ea = byPolicyStage.expert?.[key];          // has both

    diceAndSlideValue[key] = {
      greedyLadder: {
        none: { winPct: g0?.winRatePct, meanBlue: g0?.meanBlue },
        diceOnly: { winPct: gd?.winRatePct, meanBlue: gd?.meanBlue, deltaWinPct: round(gd.winRatePct - g0.winRatePct, 2), deltaBlue: round(gd.meanBlue - g0.meanBlue, 3) },
        slideOnly: { winPct: gs?.winRatePct, meanBlue: gs?.meanBlue, deltaWinPct: round(gs.winRatePct - g0.winRatePct, 2), deltaBlue: round(gs.meanBlue - g0.meanBlue, 3) },
        both: { winPct: ga?.winRatePct, meanBlue: ga?.meanBlue, deltaWinPct: round(ga.winRatePct - g0.winRatePct, 2), deltaBlue: round(ga.meanBlue - g0.meanBlue, 3) },
      },
      expertAblation: {
        none: { winPct: e0?.winRatePct, meanBlue: e0?.meanBlue },
        diceOnly: { winPct: ed?.winRatePct, meanBlue: ed?.meanBlue, deltaWinPct: round(ed.winRatePct - e0.winRatePct, 2), deltaBlue: round(ed.meanBlue - e0.meanBlue, 3) },
        slideOnly: { winPct: es?.winRatePct, meanBlue: es?.meanBlue, deltaWinPct: round(es.winRatePct - e0.winRatePct, 2), deltaBlue: round(es.meanBlue - e0.meanBlue, 3) },
        both: { winPct: ea?.winRatePct, meanBlue: ea?.meanBlue, deltaWinPct: round(ea.winRatePct - e0.winRatePct, 2), deltaBlue: round(ea.meanBlue - e0.meanBlue, 3) },
        marginalDiceGivenSlideWinPct: round(ea.winRatePct - es.winRatePct, 2),
        marginalSlideGivenDiceWinPct: round(ea.winRatePct - ed.winRatePct, 2),
        marginalDiceGivenSlideBlue: round(ea.meanBlue - es.meanBlue, 3),
        marginalSlideGivenDiceBlue: round(ea.meanBlue - ed.meanBlue, 3),
      },
    };
  }

  // 4. Per-Card Win/Capture/Usage Rates
  function computeCardStats(filterPolicies) {
    const sub = mainRows.filter(r => filterPolicies.includes(r.policy));
    const overallWinPct = (100 * sub.filter(r => r.win).length) / sub.length;
    const heroes = {};
    for (let c = 0; c < 8; c++) {
      const info = E.CARDS[c];
      heroes[info.id] = {
        idx: c, id: info.id, name: info.name, nesw: info.nesw, edgeSum: info.nesw.reduce((a, b) => a + b, 0),
        dealt: 0, winsWhenDealt: 0, blueWhenDealt: 0,
        played: 0, winsWhenPlayed: 0, blueWhenPlayed: 0,
        unused: 0, winsWhenUnused: 0,
        deployFlips: 0, slides: 0, slideFlips: 0,
        dealtS34: 0, winsWhenDealtS34: 0, playedS34: 0, unusedS34: 0,
      };
    }
    const enemies = {};
    for (let c = 8; c < 16; c++) {
      const info = E.CARDS[c];
      enemies[info.id] = {
        idx: c, id: info.id, name: info.name, nesw: info.nesw, edgeSum: info.nesw.reduce((a, b) => a + b, 0),
        openerGames: 0, playerWinsWhenOpener: 0, playerBlueWhenOpener: 0,
        openerGamesS34: 0, playerWinsWhenOpenerS34: 0,
        inPoolGames: 0, playerWinsWhenInPool: 0,
        bossDeployed: 0, bossFlips: 0, bossDeployedS34: 0, bossFlipsS34: 0,
      };
    }

    for (const r of sub) {
      const isS34 = r.stage >= 2;
      for (const h of r.hand) {
        const hs = heroes[E.CARDS[h].id];
        hs.dealt++;
        if (r.win) hs.winsWhenDealt++;
        hs.blueWhenDealt += r.blue;
        if (isS34) {
          hs.dealtS34++;
          if (r.win) hs.winsWhenDealtS34++;
        }
      }
      for (const u of r.unused) {
        const hs = heroes[E.CARDS[u].id];
        hs.unused++;
        if (r.win) hs.winsWhenUnused++;
        if (isS34) hs.unusedS34++;
      }
      for (const p of r.acts.places) {
        const hs = heroes[E.CARDS[p.card].id];
        if (!hs) continue;
        hs.played++;
        if (r.win) hs.winsWhenPlayed++;
        hs.blueWhenPlayed += r.blue;
        hs.deployFlips += p.flips;
        if (isS34) hs.playedS34++;
      }
      for (const s of r.acts.slides) {
        const cardInfo = E.CARDS[s.card];
        if (cardInfo && s.card < 8) {
          const hs = heroes[cardInfo.id];
          hs.slides++;
          hs.slideFlips += s.flips;
        }
      }

      if (r.opener >= 8) {
        const es = enemies[E.CARDS[r.opener].id];
        es.openerGames++;
        if (r.win) es.playerWinsWhenOpener++;
        es.playerBlueWhenOpener += r.blue;
        if (isS34) {
          es.openerGamesS34++;
          if (r.win) es.playerWinsWhenOpenerS34++;
        }
      }
      for (const e of r.pool) {
        const es = enemies[E.CARDS[e].id];
        es.inPoolGames++;
        if (r.win) es.playerWinsWhenInPool++;
      }
      for (const bm of r.acts.bossMoves) {
        const es = enemies[E.CARDS[bm.card].id];
        if (!es) continue;
        es.bossDeployed++;
        es.bossFlips += bm.flips;
        if (isS34) {
          es.bossDeployedS34++;
          es.bossFlipsS34 += bm.flips;
        }
      }
    }

    const heroOut = Object.values(heroes).map(h => ({
      id: h.id, name: h.name, nesw: h.nesw, edgeSum: h.edgeSum,
      dealt: h.dealt,
      winRateWhenDealtPct: round((100 * h.winsWhenDealt) / h.dealt, 2),
      winDeltaVsMeanPct: round((100 * h.winsWhenDealt) / h.dealt - overallWinPct, 2),
      meanBlueWhenDealt: round(h.blueWhenDealt / h.dealt, 3),
      played: h.played,
      playedRateWhenDealtPct: round((100 * h.played) / h.dealt, 2),
      unusedRateWhenDealtPct: round((100 * h.unused) / h.dealt, 2),
      winRateWhenPlayedPct: round((100 * h.winsWhenPlayed) / h.played, 2),
      meanDeployFlipsPerPlay: round(h.deployFlips / h.played, 3),
      slidesPerPlay: round(h.slides / h.played, 3),
      meanSlideFlipsPerSlide: h.slides ? round(h.slideFlips / h.slides, 3) : 0,
      winRateWhenDealtS34Pct: round((100 * h.winsWhenDealtS34) / h.dealtS34, 2),
      unusedRateS34Pct: round((100 * h.unusedS34) / h.dealtS34, 2),
    })).sort((a, b) => b.winRateWhenDealtPct - a.winRateWhenDealtPct);

    const enemyOut = Object.values(enemies).map(e => ({
      id: e.id, name: e.name, nesw: e.nesw, edgeSum: e.edgeSum,
      openerGames: e.openerGames,
      playerWinRateWhenOpenerPct: round((100 * e.playerWinsWhenOpener) / e.openerGames, 2),
      playerMeanBlueWhenOpener: round(e.playerBlueWhenOpener / e.openerGames, 3),
      playerWinRateWhenOpenerS34Pct: round((100 * e.playerWinsWhenOpenerS34) / e.openerGamesS34, 2),
      playerWinRateWhenInPoolPct: round((100 * e.playerWinsWhenInPool) / e.inPoolGames, 2),
      bossDeployed: e.bossDeployed,
      meanBossFlipsPerDeploy: round(e.bossFlips / e.bossDeployed, 3),
      meanBossFlipsPerDeployS34: round(e.bossFlipsS34 / e.bossDeployedS34, 3),
    })).sort((a, b) => a.playerWinRateWhenOpenerPct - b.playerWinRateWhenOpenerPct);

    return { heroes: heroOut, enemies: enemyOut };
  }

  const perCard = {
    byExpert: computeCardStats(["expert"]),
    byGreedyAll: computeCardStats(["greedy_all"]),
    byGreedy: computeCardStats(["greedy"]),
    byRandom: computeCardStats(["random"]),
  };

  // 5. First-Move Heatmap (Player 1st placement + Boss 1st reply)
  const firstMoveHeatmap = {};
  for (const pol of ["random", "greedy", "greedy_all", "lookahead", "expert"]) {
    const sub = mainRows.filter(r => r.policy === pol);
    const cells = Array.from({ length: 9 }, (_, i) => ({
      cell: i, row: (i / 3) | 0, col: i % 3,
      count: 0, wins: 0, blueSum: 0, flipsSum: 0,
      countS34: 0, winsS34: 0,
    }));
    const bossCells = Array.from({ length: 9 }, (_, i) => ({
      cell: i, row: (i / 3) | 0, col: i % 3, count: 0, flipsSum: 0,
    }));
    for (const r of sub) {
      const p0 = r.acts.places[0];
      if (p0) {
        const c = cells[p0.cell];
        c.count++;
        if (r.win) c.wins++;
        c.blueSum += r.blue;
        c.flipsSum += p0.flips;
        if (r.stage >= 2) {
          c.countS34++;
          if (r.win) c.winsS34++;
        }
      }
      const b0 = r.acts.bossMoves[0];
      if (b0) {
        const bc = bossCells[b0.slot];
        bc.count++;
        bc.flipsSum += b0.flips;
      }
    }
    firstMoveHeatmap[pol] = {
      playerFirstDeploy: cells.map(c => ({
        cell: c.cell,
        rc: `(${c.row},${c.col})`,
        count: c.count,
        sharePct: round((100 * c.count) / sub.length, 2),
        winRatePct: c.count ? round((100 * c.wins) / c.count, 2) : null,
        meanBlue: c.count ? round(c.blueSum / c.count, 3) : null,
        meanImmediateFlips: c.count ? round(c.flipsSum / c.count, 3) : null,
        shareS34Pct: round((100 * c.countS34) / (sub.length / 2), 2),
        winRateS34Pct: c.countS34 ? round((100 * c.winsS34) / c.countS34, 2) : null,
      })),
      bossFirstReply: bossCells.map(bc => ({
        cell: bc.cell,
        rc: `(${bc.row},${bc.col})`,
        count: bc.count,
        sharePct: round((100 * bc.count) / sub.length, 2),
        meanFlips: bc.count ? round(bc.flipsSum / bc.count, 3) : null,
      })),
    };
  }

  // 6. Hand Deal Variance (across C(8,5)=56 unique 5-card hero subsets)
  function computeHandVariance(pol, stageFilter) {
    const sub = mainRows.filter(r => r.policy === pol && stageFilter(r.stage));
    const byHandKey = new Map();
    for (const r of sub) {
      const sorted = r.hand.slice().sort((a, b) => a - b);
      const key = sorted.join("-");
      let h = byHandKey.get(key);
      if (!h) {
        const edgeSum = sorted.reduce((acc, c) => acc + E.CARDS[c].nesw.reduce((x, y) => x + y, 0), 0);
        h = {
          handIds: sorted.map(c => E.CARDS[c].id),
          edgeSum,
          n: 0, wins: 0, blueSum: 0,
        };
        byHandKey.set(key, h);
      }
      h.n++;
      if (r.win) h.wins++;
      h.blueSum += r.blue;
    }
    const list = [...byHandKey.values()].map(h => ({
      handIds: h.handIds,
      edgeSum: h.edgeSum,
      n: h.n,
      winRatePct: round((100 * h.wins) / h.n, 2),
      meanBlue: round(h.blueSum / h.n, 3),
    })).sort((a, b) => b.winRatePct - a.winRatePct || b.meanBlue - a.meanBlue);

    const winRates = list.map(x => x.winRatePct).sort((a, b) => a - b);
    const meanWR = winRates.reduce((a, b) => a + b, 0) / winRates.length;
    const sdWR = Math.sqrt(winRates.reduce((a, b) => a + (b - meanWR) ** 2, 0) / winRates.length);
    const q = p => winRates[Math.min(winRates.length - 1, Math.floor(p * winRates.length))];

    // Group by hand edgeSum (range 138..144)
    const byEdgeSum = {};
    for (const h of list) {
      const b = byEdgeSum[h.edgeSum] || (byEdgeSum[h.edgeSum] = { hands: 0, games: 0, wins: 0, blueSum: 0 });
      b.hands++;
      b.games += h.n;
      b.wins += Math.round((h.winRatePct / 100) * h.n);
      b.blueSum += h.meanBlue * h.n;
    }
    const edgeSumTable = Object.entries(byEdgeSum).sort((a, b) => +a[0] - +b[0]).map(([es, b]) => ({
      handEdgeSum: +es,
      distinctHands: b.hands,
      games: b.games,
      winRatePct: round((100 * b.wins) / b.games, 2),
      meanBlue: round(b.blueSum / b.games, 3),
    }));

    return {
      distinctHands: list.length,
      minWinRatePct: winRates[0],
      p25WinRatePct: q(0.25),
      medianWinRatePct: q(0.5),
      p75WinRatePct: q(0.75),
      maxWinRatePct: winRates[winRates.length - 1],
      iqrWinRatePct: round(q(0.75) - q(0.25), 2),
      sdAcrossHandsPct: round(sdWR, 2),
      byHandEdgeSum: edgeSumTable,
      top5Hands: list.slice(0, 5),
      bottom5Hands: list.slice(-5).reverse(),
    };
  }

  const handDealVariance = {
    expertOverall: computeHandVariance("expert", () => true),
    expertStages3_4: computeHandVariance("expert", st => st >= 2),
    greedyAllStages3_4: computeHandVariance("greedy_all", st => st >= 2),
    greedyStages3_4: computeHandVariance("greedy", st => st >= 2),
    randomOverall: computeHandVariance("random", () => true),
    randomStages3_4: computeHandVariance("random", st => st >= 2),
  };

  // 7. What-If Tuning Variants (var_*.csv vs baseline on matching stages)
  const varNames = [...new Set(varRows.map(r => {
    // label is var_<variant>_<policy>_s<stage>
    const m = /^var_([^_]+)_/.exec(r.label);
    return m ? m[1] : null;
  }).filter(Boolean))];

  const variants = {};
  const varPols = ["random", "greedy", "greedy_slide", "greedy_all", "lookahead", "expert"];
  for (const v of varNames) {
    variants[v] = { byStage: {} };
    for (const st of [0, 2]) {
      const stRows = varRows.filter(r => r.label.startsWith(`var_${v}_`) && r.stage === st);
      if (!stRows.length) continue;
      const stKey = `stage${st + 1}`;
      variants[v].byStage[stKey] = {};
      for (const pol of varPols) {
        const sub = stRows.filter(r => r.policy === pol);
        if (!sub.length) continue;
        const g = summarizeGroup(sub);
        const baseG = byPolicyStage[pol]?.[stKey];
        variants[v].byStage[stKey][pol] = {
          n: g.n,
          winRatePct: g.winRatePct,
          deltaWinRateVsBasePct: baseG ? round(g.winRatePct - baseG.winRatePct, 2) : null,
          meanBlue: g.meanBlue,
          deltaBlueVsBase: baseG ? round(g.meanBlue - baseG.meanBlue, 3) : null,
          meanMargin: g.meanMargin,
          meanPlayerDeployFlips: g.meanPlayerDeployFlips,
          meanSlideFlips: g.meanSlideFlips,
          meanBossFlips: g.meanBossFlips,
        };
      }
      const expV = variants[v].byStage[stKey].expert;
      const rndV = variants[v].byStage[stKey].random;
      const grdV = variants[v].byStage[stKey].greedy;
      if (expV && rndV) {
        variants[v].byStage[stKey].skillGap = {
          expertMinusRandomWinPct: round(expV.winRatePct - rndV.winRatePct, 2),
          expertMinusGreedyWinPct: grdV ? round(expV.winRatePct - grdV.winRatePct, 2) : null,
          expertMinusRandomBlue: round(expV.meanBlue - rndV.meanBlue, 3),
        };
      }
    }
  }

  const summary = {
    generatedAt: new Date().toISOString(),
    totalMainGames: mainRows.length,
    totalVariantGames: varRows.length,
    totalSimulatedGames: mainRows.length + varRows.length,
    byPolicyStage,
    skillGap,
    diceAndSlideValue,
    perCard,
    firstMoveHeatmap,
    handDealVariance,
    variants,
  };

  fs.writeFileSync(OUT_FILE, JSON.stringify(summary, null, 2));
  console.log(`Wrote ${OUT_FILE} (${mainRows.length} main games + ${varRows.length} variant games = ${mainRows.length + varRows.length} total)`);
}

main();
