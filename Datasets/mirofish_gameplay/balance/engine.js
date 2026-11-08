// Headless rules engine for CARDFRONT: Cradle of Echoes.
// Ported line-by-line from the inline <script> of
//   WebPlayable/cardfront_cradle_of_echoes_playable.html
// (startStage L1545, shuffle L1498, isColBoosted L1507, getCardEffectiveStats L1511,
//  nudgeColDie L1591, rerollAllDice L1604, recalcBoardStats L1613, findCaptures L1624,
//  handleSlotClick L1670 (slide + deploy), executeBossTurn L1756, getScores L1807,
//  checkGameOver L1819).  Presentation code (audio, DOM, banners) is omitted.
//
// Every call to rng() happens in exactly the same order as the page's Math.random() calls
// so a seeded PRNG installed as Math.random in the page reproduces the same game.
//
// `opts` lets what-if variants change rules; defaults == the shipped game.
"use strict";

const PLAYER_HEROES = [
  { id: "h_archangel", name: "Solar Archangel",   nesw: [8, 7, 6, 7] },
  { id: "h_phoenix",   name: "Phoenix Valkyrie",  nesw: [9, 8, 5, 6] },
  { id: "h_oracle",    name: "Lunar Oracle",      nesw: [7, 7, 8, 7] },
  { id: "h_chronos",   name: "Chronos Weaver",    nesw: [6, 8, 7, 7] },
  { id: "h_seraph",    name: "Astral Seraph",     nesw: [8, 6, 7, 8] },
  { id: "h_kai",       name: "Kai Crimson Visor", nesw: [7, 8, 6, 7] },
  { id: "h_valkyrie",  name: "Sky-Wing Striker",  nesw: [8, 8, 5, 6] },
  { id: "h_arbiter",   name: "Sun Arbiter",       nesw: [7, 7, 8, 8] },
];
const ENEMY_MECHS = [
  { id: "e_eclipse",  name: "Eclipse Void Blade",  nesw: [6, 6, 5, 6] },
  { id: "e_archon",   name: "Prism Core Archon",   nesw: [7, 6, 6, 5] },
  { id: "e_inferno",  name: "Inferno Seraph",      nesw: [7, 7, 5, 6] },
  { id: "e_reaper",   name: "Sigil Wraith",        nesw: [6, 7, 7, 5] },
  { id: "e_titan",    name: "Bastion Dreadnought", nesw: [7, 5, 7, 6] },
  { id: "e_colossus", name: "Emerald Colossus",    nesw: [6, 8, 5, 6] },
  { id: "e_cryo",     name: "Cryo Interceptor",    nesw: [5, 7, 6, 7] },
  { id: "e_shinobi",  name: "Cyber Shinobi",       nesw: [7, 6, 6, 5] },
];
const STAGES = [
  { name: "Eclipse Void Blade",  bossId: "e_eclipse",  aiBonus: 0 },
  { name: "Prism Core Archon",   bossId: "e_archon",   aiBonus: 0 },
  { name: "Emerald Colossus",    bossId: "e_colossus", aiBonus: 1 },
  { name: "Inferno Core Seraph", bossId: "e_inferno",  aiBonus: 1 },
];
// Card indices: 0..7 heroes, 8..15 enemies (same order as the page arrays).
const CARDS = [...PLAYER_HEROES, ...ENEMY_MECHS];
const ID2IDX = {}; CARDS.forEach((c, i) => { ID2IDX[c.id] = i; });
const BASE = CARDS.map(c => c.nesw);

const NONE = 0, PLAYER = 1, AI = 2;
// Neighbour table: for cell i, list of [neighbourCell, myEdge, theirEdge] in page order N,E,S,W.
const NEIGH = [];
for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
  const l = [];
  const dirs = [[-1, 0, 0, 2], [0, 1, 1, 3], [1, 0, 2, 0], [0, -1, 3, 1]];
  for (const [dr, dc, me, them] of dirs) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) l.push([nr * 3 + nc, me, them]);
  }
  NEIGH.push(l);
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// Same generator as a source string, for injection into the page.
const MULBERRY_SRC = mulberry32.toString();

const DEFAULT_OPTS = {
  aiBonus: null,          // null -> STAGES[stage].aiBonus
  startDice: [4, 2, 5],
  startNudges: 2,
  startRerolls: 2,
  nudgeRefill: 1,
  nudgeCap: 3,
  boostThreshold: 4,
  slideEnabled: true,
  slideCanCapture: true,
  bossOpener: true,       // boss pre-places one card at (0,1)
  bossTieRandom: false,   // false = shipped behaviour (random start is always overwritten)
  handSize: 5,
  poolSize: 5,
};

function shuffle(arr, rng) {           // L1498
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function aiBonusOf(s) { return s.opts.aiBonus == null ? STAGES[s.stageIndex].aiBonus : s.opts.aiBonus; }
function isColBoosted(s, c) { return s.colDice[c] >= s.opts.boostThreshold; }   // L1507

// L1511: returns a fresh 4-array
function effStats(s, card, col, isAi) {
  const base = BASE[card];
  const b = isAi ? s.aiBonus : (isColBoosted(s, col) ? 1 : 0);
  return [Math.min(9, base[0] + b), Math.min(9, base[1] + b), Math.min(9, base[2] + b), Math.min(9, base[3] + b)];
}

// L1545
function newGame(stageIndex, rng, opts) {
  const o = Object.assign({}, DEFAULT_OPTS, opts || {});
  const s = {
    stageIndex, opts: o, rng,
    aiBonus: 0,
    isPlayerTurn: true, gameOver: false,
    colDice: o.startDice.slice(),
    nudgesLeft: o.startNudges, rerollsLeft: o.startRerolls,
    usedSlideThisTurn: false,
    card: new Int8Array(9).fill(-1), owner: new Int8Array(9), nesw: new Int8Array(36),
    hand: [], aiPool: [], opener: -1,
    log: [],
  };
  s.aiBonus = aiBonusOf(s);
  const heroes = shuffle([0, 1, 2, 3, 4, 5, 6, 7], rng);
  const enemies = shuffle([8, 9, 10, 11, 12, 13, 14, 15], rng);
  if (o.bossOpener) {
    const first = enemies.pop();
    setCell(s, 1, first, AI, effStats(s, first, 1, true));
    s.opener = first;
  }
  s.hand = heroes.slice(0, o.handSize);
  s.aiPool = enemies.slice(0, o.poolSize);
  return s;
}

function setCell(s, i, card, owner, st) {
  s.card[i] = card; s.owner[i] = owner;
  s.nesw[i * 4] = st[0]; s.nesw[i * 4 + 1] = st[1]; s.nesw[i * 4 + 2] = st[2]; s.nesw[i * 4 + 3] = st[3];
}
function clearCell(s, i) { s.card[i] = -1; s.owner[i] = NONE; s.nesw.fill(0, i * 4, i * 4 + 4); }

// L1624 – returns array of captured cell indices (page order N,E,S,W)
function findCaptures(s, i, st, owner) {
  const out = [];
  const nb = NEIGH[i];
  for (let k = 0; k < nb.length; k++) {
    const [j, me, them] = nb[k];
    if (s.card[j] >= 0 && s.owner[j] !== owner && st[me] > s.nesw[j * 4 + them]) out.push(j);
  }
  return out;
}

// L1613
function recalc(s) {
  for (let i = 0; i < 9; i++) if (s.card[i] >= 0 && s.owner[i] === PLAYER) {
    const st = effStats(s, s.card[i], i % 3, false);
    for (let k = 0; k < 4; k++) s.nesw[i * 4 + k] = st[k];
  }
}

// L1591
function nudge(s, col) {
  if (!s.isPlayerTurn || s.gameOver) return false;
  if (s.nudgesLeft <= 0) return false;
  s.nudgesLeft--;
  s.colDice[col] = (s.colDice[col] % 6) + 1;
  recalc(s);
  return true;
}

// L1604
function reroll(s) {
  if (!s.isPlayerTurn || s.gameOver || s.rerollsLeft <= 0) return false;
  s.rerollsLeft--;
  s.colDice = s.colDice.map(() => Math.floor(s.rng() * 6) + 1);
  recalc(s);
  return true;
}

function adjacent(a, b) {
  const ar = (a / 3) | 0, ac = a % 3, br = (b / 3) | 0, bc = b % 3;
  return Math.abs(ar - br) + Math.abs(ac - bc) === 1;
}

// L1686-1713 (Tactical Slide branch of handleSlotClick). Returns flips array or null if illegal.
function slide(s, from, to) {
  if (!s.isPlayerTurn || s.gameOver || !s.opts.slideEnabled) return null;
  if (!(s.card[from] >= 0 && s.owner[from] === PLAYER)) return null;
  if (s.card[to] >= 0 || !adjacent(from, to) || s.usedSlideThisTurn) return null;
  s.usedSlideThisTurn = true;
  const card = s.card[from];
  setCell(s, to, card, PLAYER, effStats(s, card, to % 3, false));
  clearCell(s, from);
  const st = [s.nesw[to * 4], s.nesw[to * 4 + 1], s.nesw[to * 4 + 2], s.nesw[to * 4 + 3]];
  const flips = s.opts.slideCanCapture ? findCaptures(s, to, st, PLAYER) : [];
  for (const j of flips) s.owner[j] = PLAYER;
  return flips;
}

// L1716-1753 (deploy branch of handleSlotClick) + synchronous boss turn.
// Returns { flips, boss } or null if illegal.
function place(s, handIdx, cell) {
  if (!s.isPlayerTurn || s.gameOver) return null;
  if (s.card[cell] >= 0 || s.hand.length === 0) return null;
  const card = s.hand[handIdx];
  s.hand.splice(handIdx, 1);
  setCell(s, cell, card, PLAYER, effStats(s, card, cell % 3, false));
  const st = effStats(s, card, cell % 3, false);
  const flips = findCaptures(s, cell, st, PLAYER);
  for (const j of flips) s.owner[j] = PLAYER;
  s.isPlayerTurn = false;
  if (checkGameOver(s)) return { flips, boss: null };
  const boss = bossTurn(s);
  return { flips, boss };
}

// L1756
function bossTurn(s) {
  if (s.gameOver) return null;
  const open = [];
  for (let i = 0; i < 9; i++) if (s.card[i] < 0) open.push(i);
  if (open.length === 0 || s.aiPool.length === 0) {
    s.isPlayerTurn = true;
    checkGameOver(s);
    return null;
  }
  const aiCard = s.aiPool.pop();
  let bestSlot = open[Math.floor(s.rng() * open.length)];
  let bestCount = -1;
  if (!s.opts.bossTieRandom) {
    for (const slot of open) {
      const st = effStats(s, aiCard, slot % 3, true);
      const f = findCaptures(s, slot, st, AI).length;
      if (f > bestCount) { bestCount = f; bestSlot = slot; }
    }
  } else {
    // what-if: genuine random tie-break (the presumably intended behaviour)
    let ties = [];
    for (const slot of open) {
      const f = findCaptures(s, slot, effStats(s, aiCard, slot % 3, true), AI).length;
      if (f > bestCount) { bestCount = f; ties = [slot]; } else if (f === bestCount) ties.push(slot);
    }
    bestSlot = ties[Math.floor(s.rng() * ties.length)];
  }
  const st = effStats(s, aiCard, bestSlot % 3, true);
  setCell(s, bestSlot, aiCard, AI, st);
  const flips = findCaptures(s, bestSlot, st, AI);
  for (const j of flips) s.owner[j] = AI;
  s.isPlayerTurn = true;
  s.usedSlideThisTurn = false;
  s.nudgesLeft = Math.min(s.opts.nudgeCap, s.nudgesLeft + s.opts.nudgeRefill);
  checkGameOver(s);
  return { card: aiCard, slot: bestSlot, flips };
}

// L1807
function getScores(s) {
  let blue = 0, red = 0, empty = 0;
  for (let i = 0; i < 9; i++) {
    if (s.owner[i] === PLAYER) blue++; else if (s.owner[i] === AI) red++; else empty++;
  }
  return { blue, red, empty };
}

// L1819
function checkGameOver(s) {
  const { blue, red, empty } = getScores(s);
  if (empty > 0 && s.hand.length > 0) return false;
  s.gameOver = true;
  s.win = blue > red;
  s.final = { blue, red };
  return true;
}

// Snapshot in the same shape as the page-side snapshot used by validate.js
function snapshot(s) {
  const grid = [];
  for (let i = 0; i < 9; i++) grid.push(s.card[i] >= 0
    ? [CARDS[s.card[i]].id, s.owner[i] === PLAYER ? "player" : "ai", [s.nesw[i * 4], s.nesw[i * 4 + 1], s.nesw[i * 4 + 2], s.nesw[i * 4 + 3]]]
    : null);
  const sc = getScores(s);
  return {
    grid, hand: s.hand.map(i => CARDS[i].id), aiPool: s.aiPool.map(i => CARDS[i].id),
    colDice: s.colDice.slice(), nudgesLeft: s.nudgesLeft, rerollsLeft: s.rerollsLeft,
    usedSlide: s.usedSlideThisTurn, isPlayerTurn: s.isPlayerTurn, gameOver: s.gameOver,
    blue: sc.blue, red: sc.red,
  };
}

function cloneState(s) {
  return {
    stageIndex: s.stageIndex, opts: s.opts, rng: s.rng, aiBonus: s.aiBonus,
    isPlayerTurn: s.isPlayerTurn, gameOver: s.gameOver, colDice: s.colDice.slice(),
    nudgesLeft: s.nudgesLeft, rerollsLeft: s.rerollsLeft, usedSlideThisTurn: s.usedSlideThisTurn,
    card: s.card.slice(), owner: s.owner.slice(), nesw: s.nesw.slice(),
    hand: s.hand.slice(), aiPool: s.aiPool.slice(), opener: s.opener, log: [],
  };
}

module.exports = {
  PLAYER_HEROES, ENEMY_MECHS, STAGES, CARDS, ID2IDX, BASE, NEIGH, NONE, PLAYER, AI,
  DEFAULT_OPTS, mulberry32, MULBERRY_SRC, shuffle, isColBoosted, effStats, newGame,
  findCaptures, recalc, nudge, reroll, adjacent, slide, place, bossTurn, getScores,
  checkGameOver, snapshot, cloneState, setCell, clearCell,
};
