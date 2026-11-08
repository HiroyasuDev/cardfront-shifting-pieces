// Player policies. Each policy plays one full player turn on an engine state `s`
// (dice actions -> optional slide -> deploy; deploy triggers the synchronous boss turn).
// Policies draw their own randomness from `prng` (never from the game rng), so the game RNG
// stream is identical to the page's Math.random stream.
"use strict";
const E = require("./engine");
const { Searcher } = require("./search");

function emptyCells(s) { const o = []; for (let i = 0; i < 9; i++) if (s.card[i] < 0) o.push(i); return o; }
function pick(arr, prng) { return arr[Math.floor(prng() * arr.length)]; }

function statsWithDice(s, card, cell, dice) {
  const b = dice[cell % 3] >= s.opts.boostThreshold ? 1 : 0;
  return E.BASE[card].map(v => Math.min(9, v + b));
}
function flipsAt(s, card, cell, dice) {
  return E.findCaptures(s, cell, statsWithDice(s, card, cell, dice || s.colDice), E.PLAYER).length;
}
// all (handIdx, cell, flips) placements
function placements(s, dice) {
  const out = [];
  const em = emptyCells(s);
  s.hand.forEach((card, hi) => { for (const cell of em) out.push({ hi, card, cell, f: flipsAt(s, card, cell, dice) }); });
  return out;
}
function bestFlips(s, dice) { let m = 0; for (const p of placements(s, dice)) if (p.f > m) m = p.f; return m; }

function doPlace(s, hi, cell, log) {
  const card = s.hand[hi];
  const r = E.place(s, hi, cell);
  if (!r) throw new Error("illegal place");
  log.push({ t: "place", card, cell, flips: r.flips.length, boss: r.boss ? { card: r.boss.card, slot: r.boss.slot, flips: r.boss.flips.length } : null });
}
function doSlide(s, from, to, log) {
  const f = E.slide(s, from, to);
  if (!f) throw new Error("illegal slide");
  log.push({ t: "slide", from, to, flips: f.length, card: s.card[to] });
}
function doNudge(s, col, log) { if (!E.nudge(s, col)) throw new Error("illegal nudge"); log.push({ t: "nudge", col }); }
function doReroll(s, log) { if (!E.reroll(s)) throw new Error("illegal reroll"); log.push({ t: "reroll", dice: s.colDice.slice() }); }

function greedyPlace(s, prng, log) {
  const ps = placements(s);
  const m = Math.max(...ps.map(p => p.f));
  const best = ps.filter(p => p.f === m);
  const p = pick(best, prng);
  doPlace(s, p.hi, p.cell, log);
}

// ---------------------------------------------------------------- policies
const POLICIES = {};

POLICIES.random = { name: "Random", turn(s, prng, log) {
  const hi = Math.floor(prng() * s.hand.length);
  doPlace(s, hi, pick(emptyCells(s), prng), log);
} };

POLICIES.greedy = { name: "Greedy", turn(s, prng, log) { greedyPlace(s, prng, log); } };

function nudgeCombos(n) {   // multisets of columns of size 1..n
  const out = [];
  const rec = (start, cur) => {
    if (cur.length) out.push(cur.slice());
    if (cur.length === n) return;
    for (let c = start; c < 3; c++) { cur.push(c); rec(c, cur); cur.pop(); }
  };
  rec(0, []);
  return out.sort((a, b) => a.length - b.length);
}
function applyNudgesToDice(d, combo) { const x = d.slice(); for (const c of combo) x[c] = (x[c] % 6) + 1; return x; }

function greedyDiceStep(s, log) {
  // spend nudges only if they increase the best immediate flip count (fewest nudges first)
  const cur = bestFlips(s);
  let bestCombo = null, bestVal = cur;
  for (const combo of nudgeCombos(s.nudgesLeft)) {
    const v = bestFlips(s, applyNudgesToDice(s.colDice, combo));
    if (v > bestVal) { bestVal = v; bestCombo = combo; }
  }
  if (bestCombo) for (const c of bestCombo) doNudge(s, c, log);
}
let DICE216 = null;
function allDice() {
  if (!DICE216) { DICE216 = []; for (let a = 1; a <= 6; a++) for (let b = 1; b <= 6; b++) for (let c = 1; c <= 6; c++) DICE216.push([a, b, c]); }
  return DICE216;
}
function greedyDiceTurnTools(s, log) {
  greedyDiceStep(s, log);
  while (s.rerollsLeft > 0) {
    const cur = bestFlips(s);
    let exp = 0; for (const d of allDice()) exp += bestFlips(s, d) / 216;
    if (exp > cur + 1e-9) { doReroll(s, log); greedyDiceStep(s, log); } else break;
  }
}
POLICIES.greedy_dice = { name: "Greedy+Dice", turn(s, prng, log) { greedyDiceTurnTools(s, log); greedyPlace(s, prng, log); } };

function greedySlideTurn(s, prng, log) {
  // evaluate: no slide, or each legal slide followed by the best placement; maximise total flips
  let best = [{ slide: null, f: bestFlips(s) }];
  if (s.opts.slideEnabled && !s.usedSlideThisTurn) {
    for (let i = 0; i < 9; i++) if (s.card[i] >= 0 && s.owner[i] === E.PLAYER) {
      for (const [j] of E.NEIGH[i]) if (s.card[j] < 0) {
        const c = E.cloneState(s);
        const sf = E.slide(c, i, j);
        const tot = sf.length + bestFlips(c);
        if (tot > best[0].f) best = [{ slide: [i, j], f: tot }];
        else if (tot === best[0].f && best[0].slide !== null) best.push({ slide: [i, j], f: tot });
      }
    }
  }
  const ch = best[0].slide === null ? best[0] : pick(best, prng);
  if (ch.slide) doSlide(s, ch.slide[0], ch.slide[1], log);
  greedyPlace(s, prng, log);
}
POLICIES.greedy_slide = { name: "Greedy+Slide", turn: greedySlideTurn };
POLICIES.greedy_all = { name: "Greedy+Dice+Slide", turn(s, prng, log) { greedyDiceTurnTools(s, log); greedySlideTurn(s, prng, log); } };

// Chaos: random use of every tool (used for rules cross-validation coverage)
POLICIES.chaos = { name: "Chaos", turn(s, prng, log) {
  let guard = 0;
  while (guard++ < 6) {
    const r = prng();
    if (r < 0.25 && s.nudgesLeft > 0) doNudge(s, Math.floor(prng() * 3), log);
    else if (r < 0.35 && s.rerollsLeft > 0) doReroll(s, log);
    else if (r < 0.6 && !s.usedSlideThisTurn) {
      const opts = [];
      for (let i = 0; i < 9; i++) if (s.card[i] >= 0 && s.owner[i] === E.PLAYER) for (const [j] of E.NEIGH[i]) if (s.card[j] < 0) opts.push([i, j]);
      if (opts.length) { const o = pick(opts, prng); doSlide(s, o[0], o[1], log); }
    } else break;
  }
  if (prng() < 0.5) greedyPlace(s, prng, log);
  else doPlace(s, Math.floor(prng() * s.hand.length), pick(emptyCells(s), prng), log);
} };

// ---- search-based policies
const searchers = new Map();
function getSearcher(s, flavour) {
  const key = flavour.key + "|" + s.aiBonus + "|" + JSON.stringify(s.opts);
  let x = searchers.get(key);
  if (!x) {
    x = { sr: new Searcher({ aiBonus: s.aiBonus, boostThreshold: s.opts.boostThreshold, nudgeCap: s.opts.nudgeCap,
      nudgeRefill: s.opts.nudgeRefill, useDice: flavour.dice, useSlide: flavour.slide && s.opts.slideEnabled,
      slideCanCapture: s.opts.slideCanCapture, bossTieRandom: s.opts.bossTieRandom, utility: flavour.utility, horizon: flavour.horizon }), cache: new Map() };
    searchers.set(key, x);
  }
  return x;
}
function execSearchDecision(s, d, log) {
  for (const c of d.plan) doNudge(s, c, log);
  const a = d.action;
  if (a.from >= 0) doSlide(s, a.from, a.to, log);
  const hi = s.hand.indexOf(a.card);
  doPlace(s, hi, a.cell, log);
}
function makeSearchPolicy(name, flavour, mode) {
  return { name, flavour, mode, turn(s, prng, log, ctx) {
    const X = getSearcher(s, flavour);
    const { b, hand, unseen } = X.sr.fromEngine(s);
    let d;
    if (mode === "oracle") {
      X.sr.oracleSeq = s.aiPool.slice().reverse();  // pool pops from the end
      d = X.sr.decide(b, hand, unseen);
      X.sr.oracleSeq = null;
    } else {
      const key = Buffer.from(b.buffer).toString("base64") + ":" + hand + ":" + unseen;
      d = X.cache.get(key);
      if (!d) {
        d = mode === "lookahead" ? X.sr.lookahead(b, hand, unseen) : X.sr.decide(b, hand, unseen);
        d = { action: d.action, value: d.value, plan: d.plan };
        X.cache.set(key, d);
      }
    }
    if (ctx) { ctx.values = ctx.values || []; ctx.values.push(d.value); }
    execSearchDecision(s, d, log);
  } };
}
POLICIES.lookahead = makeSearchPolicy("Lookahead (depth-2 minimax)", { key: "LA", dice: true, slide: true }, "lookahead");
POLICIES.expert = makeSearchPolicy("Expert (expectimax)", { key: "EX", dice: true, slide: true }, "expert");
POLICIES.expert_nodice = makeSearchPolicy("Expert, no dice", { key: "EXnd", dice: false, slide: true }, "expert");
POLICIES.expert_noslide = makeSearchPolicy("Expert, no slide", { key: "EXns", dice: true, slide: false }, "expert");
POLICIES.expert_notools = makeSearchPolicy("Expert, no tools", { key: "EXnt", dice: false, slide: false }, "expert");
POLICIES.expert_margin = makeSearchPolicy("Expert-Margin (expectimax on E[Blue], 2-turn horizon)", { key: "EXM", dice: true, slide: true, utility: "blue", horizon: 2 }, "expert");
POLICIES.oracle = makeSearchPolicy("Oracle (sees boss pool)", { key: "OR", dice: true, slide: true }, "oracle");

// Play one full game. Returns a record.
function playGame(stage, seed, policyKey, opts) {
  const rng = E.mulberry32(seed);
  const prng = E.mulberry32((seed ^ 0x9E3779B9) >>> 0);
  const s = E.newGame(stage, rng, opts);
  const startHand = s.hand.slice(), opener = s.opener, pool = s.aiPool.slice();
  const pol = POLICIES[policyKey];
  const log = [], ctx = {};
  let turns = 0;
  while (!s.gameOver) {
    if (!s.isPlayerTurn) throw new Error("not player turn");
    pol.turn(s, prng, log, ctx);
    if (++turns > 20) throw new Error("runaway");
  }
  return { stage, seed, policy: policyKey, startHand, opener, pool, log, blue: s.final.blue, red: s.final.red, win: s.win,
    unused: s.hand.slice(), values: ctx.values || [] };
}

module.exports = { POLICIES, playGame, placements, bestFlips, nudgeCombos };
