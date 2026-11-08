// Fast search core used by Lookahead / Expert / Oracle policies.
// Operates on a compact Int8Array snapshot of an engine state and models exactly the same rules
// as engine.js (boss = first open cell, row-major, with max flips; ties never random in the shipped game).
"use strict";
const E = require("./engine");

const S = 60;
const OC = 0, OO = 9, ON = 18, OD = 54, ONU = 57, OPL = 58, OSL = 59;
const NEIGH = E.NEIGH;
const MAXLEVEL = 64;

function popcount(x) { let n = 0; while (x) { x &= x - 1; n++; } return n; }

class Searcher {
  constructor(cfg) {
    this.aiBonus = cfg.aiBonus;
    this.thr = cfg.boostThreshold ?? 4;
    this.cap = cfg.nudgeCap ?? 3;
    this.refill = cfg.nudgeRefill ?? 1;
    this.useDice = cfg.useDice ?? true;
    this.useSlide = cfg.useSlide ?? true;
    this.slideCanCapture = cfg.slideCanCapture ?? true;
    this.bossTieRandom = cfg.bossTieRandom ?? false;
    this.oracleSeq = null;   // array of upcoming boss cards (perfect information) or null
    // utility: "win" = P(win); "lex" = 0.99*win + 0.01*blue/9 (P(win) first, then final Blue count)
    this.utility = cfg.utility || "win";
    this.horizon = cfg.horizon || 99;   // number of boss replies searched before static evaluation
    this.nodes = 0;
    // player stats table [card][boost] -> 4 values; ai stats [card]
    this.pst = [];
    this.ast = [];
    for (let c = 0; c < 16; c++) {
      const b = E.BASE[c];
      this.pst.push([b.map(v => Math.min(9, v)), b.map(v => Math.min(9, v + 1))]);
      this.ast.push(b.map(v => Math.min(9, v + this.aiBonus)));
    }
    this.bufs = [];
    for (let i = 0; i < MAXLEVEL; i++) this.bufs.push(new Int8Array(S));
    this.sbufs = []; this.slideList = []; this.cardLists = [];
    for (let i = 0; i < MAXLEVEL; i++) { this.sbufs.push(new Int8Array(S)); this.slideList.push(new Int8Array(64)); this.cardLists.push(new Int8Array(8)); }
  }

  // Build compact state from an engine state
  fromEngine(s) {
    const b = new Int8Array(S);
    for (let i = 0; i < 9; i++) { b[OC + i] = s.card[i]; b[OO + i] = s.owner[i]; }
    for (let k = 0; k < 36; k++) b[ON + k] = s.nesw[k];
    b[OD] = s.colDice[0]; b[OD + 1] = s.colDice[1]; b[OD + 2] = s.colDice[2];
    b[ONU] = s.nudgesLeft; b[OPL] = s.aiPool.length; b[OSL] = s.usedSlideThisTurn ? 1 : 0;
    let hand = 0; for (const h of s.hand) hand |= 1 << h;
    let seen = 0; for (let i = 0; i < 9; i++) if (s.card[i] >= 8) seen |= 1 << s.card[i];
    const unseen = 0xFF00 & ~seen;
    return { b, hand, unseen };
  }

  // Auto-boost rule (identical to the Expert's real dice behaviour). Returns list of columns nudged.
  autoBoostPlan(dice, nudges) {
    const thr = this.thr;
    const d = [dice[0], dice[1], dice[2]];
    const plan = [];
    let n = nudges;
    const cols = [0, 1, 2].filter(c => d[c] < thr).sort((a, b) => (thr - d[a]) - (thr - d[b]) || a - b);
    for (const c of cols) {           // complete affordable boosts, cheapest first
      const cost = thr - d[c];
      if (cost <= n) { for (let k = 0; k < cost; k++) plan.push(c); n -= cost; d[c] = thr; }
    }
    for (const c of cols) {           // spend leftovers as partial progress (never hurts: v+1 <= thr)
      while (n > 0 && d[c] < thr) { d[c]++; plan.push(c); n--; }
    }
    return plan;
  }

  applyAutoBoost(b) {
    if (!this.useDice || b[ONU] <= 0) return;
    const plan = this.autoBoostPlan([b[OD], b[OD + 1], b[OD + 2]], b[ONU]);
    if (!plan.length) return;
    for (const c of plan) { b[OD + c] = (b[OD + c] % 6) + 1; b[ONU]--; }
    this.recalc(b);
  }

  recalc(b) {
    for (let i = 0; i < 9; i++) if (b[OC + i] >= 0 && b[OO + i] === 1) {
      const st = this.pst[b[OC + i]][b[OD + (i % 3)] >= this.thr ? 1 : 0];
      const o = ON + i * 4; b[o] = st[0]; b[o + 1] = st[1]; b[o + 2] = st[2]; b[o + 3] = st[3];
    }
  }

  // place card with stats st at cell i for owner, flip captures; returns #flips
  put(b, i, card, owner, st, capture) {
    b[OC + i] = card; b[OO + i] = owner;
    const o = ON + i * 4; b[o] = st[0]; b[o + 1] = st[1]; b[o + 2] = st[2]; b[o + 3] = st[3];
    if (!capture) return 0;
    let f = 0; const nb = NEIGH[i];
    for (let k = 0; k < nb.length; k++) {
      const t = nb[k]; const j = t[0];
      if (b[OC + j] >= 0 && b[OO + j] !== owner && st[t[1]] > b[ON + j * 4 + t[2]]) { b[OO + j] = owner; f++; }
    }
    return f;
  }
  countFlips(b, i, owner, st) {
    let f = 0; const nb = NEIGH[i];
    for (let k = 0; k < nb.length; k++) {
      const t = nb[k]; const j = t[0];
      if (b[OC + j] >= 0 && b[OO + j] !== owner && st[t[1]] > b[ON + j * 4 + t[2]]) f++;
    }
    return f;
  }
  pStats(b, card, cell) { return this.pst[card][b[OD + (cell % 3)] >= this.thr ? 1 : 0]; }

  doSlide(b, from, to) {
    const card = b[OC + from];
    b[OC + from] = -1; b[OO + from] = 0; const o = ON + from * 4; b[o] = b[o + 1] = b[o + 2] = b[o + 3] = 0;
    const f = this.put(b, to, card, 1, this.pStats(b, card, to), this.slideCanCapture);
    b[OSL] = 1;
    return f;
  }

  // Boss placement candidates for card e: returns array of cells (1 entry unless bossTieRandom)
  bossSlots(b, e) {
    const st = this.ast[e];
    let best = -1, bestSlot = -1, ties = null;
    for (let i = 0; i < 9; i++) if (b[OC + i] < 0) {
      const f = this.countFlips(b, i, 2, st);
      if (f > best) { best = f; bestSlot = i; if (this.bossTieRandom) ties = [i]; }
      else if (this.bossTieRandom && f === best) ties.push(i);
    }
    return this.bossTieRandom ? ties : (bestSlot < 0 ? [] : [bestSlot]);
  }
  bossApply(b, e, slot) {
    this.put(b, slot, e, 2, this.ast[e], true);
    b[ONU] = Math.min(this.cap, b[ONU] + this.refill);
    b[OPL]--; b[OSL] = 0;
  }

  static emptyCount(b) { let n = 0; for (let i = 0; i < 9; i++) if (b[OC + i] < 0) n++; return n; }
  static terminalValue(b) {
    let blue = 0, red = 0;
    for (let i = 0; i < 9; i++) { if (b[OO + i] === 1) blue++; else if (b[OO + i] === 2) red++; }
    return blue > red ? 1 : 0;
  }
  static lexValue(b) {
    let blue = 0, red = 0;
    for (let i = 0; i < 9; i++) { if (b[OO + i] === 1) blue++; else if (b[OO + i] === 2) red++; }
    return (blue > red ? 0.99 : 0) + 0.01 * blue / 9;
  }
  static diff(b) {
    let d = 0; for (let i = 0; i < 9; i++) { if (b[OO + i] === 1) d++; else if (b[OO + i] === 2) d--; }
    return d;
  }

  // Enumerate player actions from buffer b (after auto-boost). Action = {from,to,card,cell,h}
  genActions(b, hand, order) {
    const acts = [];
    const tmp = this.bufs[MAXLEVEL - 1];
    const slides = [[-1, -1]];
    if (this.useSlide && !b[OSL]) {
      for (let i = 0; i < 9; i++) if (b[OC + i] >= 0 && b[OO + i] === 1) {
        for (const t of NEIGH[i]) if (b[OC + t[0]] < 0) slides.push([i, t[0]]);
      }
    }
    for (const [from, to] of slides) {
      tmp.set(b);
      let sf = 0;
      if (from >= 0) sf = this.doSlide(tmp, from, to);
      for (let c = 0; c < 8; c++) if (hand & (1 << c)) {
        for (let i = 0; i < 9; i++) if (tmp[OC + i] < 0) {
          const h = order ? sf + this.countFlips(tmp, i, 1, this.pStats(tmp, c, i)) : 0;
          acts.push({ from, to, card: c, cell: i, h });
        }
      }
    }
    if (order) acts.sort((x, y) => y.h - x.h);
    return acts;
  }

  applyAction(dst, src, a) {
    dst.set(src);
    if (a.from >= 0) this.doSlide(dst, a.from, a.to);
    this.put(dst, a.cell, a.card, 1, this.pStats(dst, a.card, a.cell), true);
  }

  // ---------- Expectimax with Star1-style pruning ----------
  // utility "win": P(win); "lex": 0.99*win + 0.01*blue/9; "blue": E[final Blue]/9 (allows a horizon).
  // Returns v: if v > alpha then v is exact; else true value <= alpha.
  valueCounts(blue, red) {
    if (this.utility === "win") return blue > red ? 1 : 0;
    if (this.utility === "lex") return (blue > red ? 0.99 : 0) + 0.01 * blue / 9;
    return blue / 9;
  }
  value(b) {
    let blue = 0, red = 0;
    for (let i = 0; i < 9; i++) { const o = b[OO + i]; if (o === 1) blue++; else if (o === 2) red++; }
    return this.valueCounts(blue, red);
  }

  maxNode(b0, hand, unseen, alpha, lvl, depth) {
    this.nodes++;
    const b = this.bufs[lvl]; b.set(b0);
    this.applyAutoBoost(b);
    const child = this.bufs[lvl + 1];
    let best = -1;
    if (depth <= 1) {   // shallow: ordered move list
      const acts = this.genActions(b, hand, true);
      for (let k = 0; k < acts.length; k++) {
        const a = acts[k];
        this.applyAction(child, b, a);
        const v = this.afterPlayer(child, hand & ~(1 << a.card), unseen, Math.max(alpha, best), lvl + 2, depth);
        if (v > best) { best = v; if (best >= 1 - 1e-9) return 1; }
      }
      return best;
    }
    const sb = this.sbufs[lvl];
    const sl = this.slideList[lvl];
    let nS = 0;
    if (this.useSlide && !b[OSL]) {
      for (let i = 0; i < 9; i++) if (b[OC + i] >= 0 && b[OO + i] === 1) {
        const nb = NEIGH[i];
        for (let k = 0; k < nb.length; k++) if (b[OC + nb[k][0]] < 0) { sl[nS * 2] = i; sl[nS * 2 + 1] = nb[k][0]; nS++; }
      }
    }
    for (let si = -1; si < nS; si++) {
      let src = b;
      if (si >= 0) { sb.set(b); this.doSlide(sb, sl[si * 2], sl[si * 2 + 1]); src = sb; }
      for (let c = 0; c < 8; c++) if (hand & (1 << c)) {
        const h2 = hand & ~(1 << c);
        for (let i = 0; i < 9; i++) if (src[OC + i] < 0) {
          child.set(src);
          this.put(child, i, c, 1, this.pStats(child, c, i), true);
          const v = this.afterPlayer(child, h2, unseen, alpha > best ? alpha : best, lvl + 2, depth);
          if (v > best) { best = v; if (best >= 1 - 1e-9) return 1; }
        }
      }
    }
    return best;
  }

  afterPlayer(child, h2, unseen, alpha, lvl, depth) {
    let empty = 0; for (let i = 0; i < 9; i++) if (child[OC + i] < 0) empty++;
    if (empty === 0 || h2 === 0) return this.value(child);
    return this.chanceNode(child, h2, unseen, alpha, lvl, depth, empty);
  }

  chanceNode(b, hand, unseen, alpha, lvl, depth, empty) {
    if (b[OPL] <= 0) return this.maxNode(b, hand, unseen, alpha, lvl, depth + 1);
    let cards = this.cardLists[lvl], nC = 0;
    if (this.oracleSeq) { cards[0] = this.oracleSeq[depth]; nC = 1; }
    else for (let e = 8; e < 16; e++) if (unseen & (1 << e)) cards[nC++] = e;
    const p = 1 / nC;
    // Fast path: boss fills the last empty cell -> terminal, no copying
    if (empty === 1 && !this.bossTieRandom) {
      let slot = 0; while (b[OC + slot] >= 0) slot++;
      let blue = 0, red = 0;
      for (let i = 0; i < 9; i++) { const o = b[OO + i]; if (o === 1) blue++; else if (o === 2) red++; }
      let sum = 0;
      for (let k = 0; k < nC; k++) {
        const f = this.countFlips(b, slot, 2, this.ast[cards[k]]);
        sum += this.valueCounts(blue - f, red + 1 + f);
      }
      return sum * p;
    }
    // Horizon reached (depth-limited search): evaluate after the boss reply
    const atHorizon = depth + 1 >= this.horizon;
    let sum = 0, rem = 1;
    const child = this.bufs[lvl];
    for (let k = 0; k < nC; k++) {
      const e = cards[k];
      rem -= p;
      const slots = this.bossSlots(b, e);
      const q = p / slots.length;
      for (let si = 0; si < slots.length; si++) {
        const remQ = rem + (slots.length - 1 - si) * q;
        const need = (alpha - sum - remQ) / q;
        if (need >= 1) return alpha;            // cannot exceed alpha any more
        child.set(b);
        this.bossApply(child, e, slots[si]);
        let v;
        if (empty - 1 === 0 || hand === 0 || atHorizon) v = this.value(child);
        else v = this.maxNode(child, hand, unseen & ~(1 << e), need, lvl + 1, depth + 1);
        if (v <= need) return alpha;
        sum += q * v;
      }
    }
    return sum;
  }

  // Root decision for the player at turn start. Returns {action, value, plan}
  decide(b0, hand, unseen) {
    const b = new Int8Array(S); b.set(b0);
    const plan = this.useDice && b[ONU] > 0 ? this.autoBoostPlan([b[OD], b[OD + 1], b[OD + 2]], b[ONU]) : [];
    this.applyAutoBoost(b);
    const acts = this.genActions(b, hand, true);
    const child = new Int8Array(S);
    let best = -1, bestA = null;
    for (const a of acts) {
      this.applyAction(child, b, a);
      const v = this.afterPlayer(child, hand & ~(1 << a.card), unseen, best, 1, 0);
      if (v > best) { best = v; bestA = a; if (best >= 1 - 1e-9) break; }
    }
    return { action: bestA, value: best, plan };
  }

  // Depth-2 minimax lookahead (player action, then worst-case boss card reply). Eval = blue - red.
  lookahead(b0, hand, unseen) {
    const b = new Int8Array(S); b.set(b0);
    const plan = this.useDice && b[ONU] > 0 ? this.autoBoostPlan([b[OD], b[OD + 1], b[OD + 2]], b[ONU]) : [];
    this.applyAutoBoost(b);
    const acts = this.genActions(b, hand, true);
    const child = new Int8Array(S), g = new Int8Array(S);
    let bestA = null, bestMin = -99, bestMean = -99;
    const cards = []; for (let e = 8; e < 16; e++) if (unseen & (1 << e)) cards.push(e);
    for (const a of acts) {
      this.applyAction(child, b, a);
      const h2 = hand & ~(1 << a.card);
      let mn, mean;
      if (Searcher.emptyCount(child) === 0 || h2 === 0 || child[OPL] <= 0) { mn = mean = Searcher.diff(child); }
      else {
        mn = 99; mean = 0;
        for (const e of cards) {
          const slots = this.bossSlots(child, e);
          for (const sl of slots) {
            g.set(child); this.bossApply(g, e, sl);
            const d = Searcher.diff(g);
            if (d < mn) mn = d; mean += d / cards.length / slots.length;
          }
        }
      }
      if (mn > bestMin || (mn === bestMin && mean > bestMean + 1e-9)) { bestMin = mn; bestMean = mean; bestA = a; }
    }
    return { action: bestA, value: bestMin, mean: bestMean, plan };
  }
}

module.exports = { Searcher, S, OC, OO, ON, OD, ONU, OPL, OSL, popcount };
