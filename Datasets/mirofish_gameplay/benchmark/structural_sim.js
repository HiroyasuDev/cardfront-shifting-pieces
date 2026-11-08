// Structural benchmark sim for CARDFRONT (read-only extraction of card data from the playable HTML).
// Replicates findCaptures / executeBossTurn / checkGameOver logic (no slides, no nudges/rerolls unless noted).
const fs = require('fs');
const HTML = '/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html';
const src = fs.readFileSync(HTML, 'utf8');
function grab(name) {
  const i = src.indexOf(`const ${name} = [`);
  const j = src.indexOf('\n];', i);
  return eval(src.slice(i + `const ${name} = `.length, j + 3).replace(/;$/, ''));
}
const H = grab('PLAYER_HEROES'), E = grab('ENEMY_MECHS');
const sum = a => a.reduce((x, y) => x + y, 0);
const out = { cards: {}, sims: {} };
out.cards.heroes = H.map(c => ({ id: c.id, nesw: c.nesw, total: sum(c.nesw) }));
out.cards.enemies = E.map(c => ({ id: c.id, nesw: c.nesw, total: sum(c.nesw) }));
out.cards.heroMeanTotal = sum(H.map(c => sum(c.nesw))) / H.length;
out.cards.enemyMeanTotal = sum(E.map(c => sum(c.nesw))) / E.length;
// pairwise edge-win probability (strictly greater)
function edgeP(boostH, bonusE) {
  let w = 0, t = 0, ties = 0;
  for (const h of H) for (const a of h.nesw) for (const e of E) for (const b of e.nesw) {
    const x = Math.min(9, a + boostH), y = Math.min(9, b + bonusE); t++; if (x > y) w++; else if (x === y) ties++;
  }
  return { pHeroEdgeBeats: +(w / t).toFixed(4), pTie: +(ties / t).toFixed(4) };
}
out.cards.edgeVsEdge = { noBoost_bonus0: edgeP(0, 0), boost_bonus0: edgeP(1, 0), noBoost_bonus1: edgeP(0, 1), boost_bonus1: edgeP(1, 1),
  enemyAttacksHero_bonus0: (() => { let w=0,t=0; for (const e of E) for (const b of e.nesw) for (const h of H) for (const a of h.nesw) { t++; if (b > a) w++; } return +(w/t).toFixed(4); })(),
  enemyAttacksHero_bonus1_vsUnboosted: (() => { let w=0,t=0; for (const e of E) for (const b of e.nesw) for (const h of H) for (const a of h.nesw) { t++; if (Math.min(9,b+1) > a) w++; } return +(w/t).toFixed(4); })() };

const ALL = {}; [...H, ...E].forEach(c => ALL[c.id] = c);
function shuffle(arr) { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const DIRS = [{ dr: -1, dc: 0, m: 0, t: 2 }, { dr: 0, dc: 1, m: 1, t: 3 }, { dr: 1, dc: 0, m: 2, t: 0 }, { dr: 0, dc: -1, m: 3, t: 1 }];
function stats(id, col, isAi, st) { const b = ALL[id].nesw; if (isAi) return b.map(v => Math.min(9, v + st.bonus)); const k = st.dice[col] >= 4 ? 1 : 0; return b.map(v => Math.min(9, v + k)); }
function caps(g, r, c, nesw, owner) { const o = []; for (const d of DIRS) { const nr = r + d.dr, nc = c + d.dc; if (nr < 0 || nr > 2 || nc < 0 || nc > 2) continue; const nb = g[nr][nc]; if (nb.id && nb.owner !== owner && nesw[d.m] > nb.nesw[d.t]) o.push([nr, nc]); } return o; }
// Same/Plus opportunity detector (FF8 semantics: >=2 adjacent sides, at least one opponent card)
function samePlus(g, r, c, nesw, owner) {
  const adj = []; for (const d of DIRS) { const nr = r + d.dr, nc = c + d.dc; if (nr < 0 || nr > 2 || nc < 0 || nc > 2) continue; const nb = g[nr][nc]; if (nb.id) adj.push({ mine: nesw[d.m], theirs: nb.nesw[d.t], opp: nb.owner !== owner }); }
  let same = adj.filter(a => a.mine === a.theirs); const sameHit = same.length >= 2 && same.some(a => a.opp);
  const sums = {}; adj.forEach(a => { const s = a.mine + a.theirs; (sums[s] = sums[s] || []).push(a); });
  const plusHit = Object.values(sums).some(v => v.length >= 2 && v.some(a => a.opp));
  return { sameHit, plusHit };
}
function empties(g) { const o = []; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!g[r][c].id) o.push([r, c]); return o; }
function play(policy, bonus) {
  const st = { bonus, dice: [4, 2, 5] };
  const heroes = shuffle(H), enemies = shuffle(E);
  const g = [...Array(3)].map(() => [...Array(3)].map(() => ({ id: null, owner: null, nesw: [0, 0, 0, 0] })));
  const first = enemies.pop(); g[0][1] = { id: first.id, owner: 'ai', nesw: stats(first.id, 1, true, st) };
  let hand = heroes.slice(0, 5).map(h => h.id); const pool = enemies.slice(0, 5).map(e => e.id);
  let pPlaced = 0, bPlaced = 1, pFlips = 0, bFlips = 0, spOpp = 0, sameOpp = 0, plusOpp = 0, decisions = [];
  while (true) {
    // player turn
    const em = empties(g); if (!em.length || !hand.length) break;
    let best = null, bestScore = -1, legal = 0, distinctOutcomes = new Set();
    const moves = [];
    for (let hi = 0; hi < hand.length; hi++) for (const [r, c] of em) { legal++; const n = stats(hand[hi], c, false, st); const k = caps(g, r, c, n, 'player').length; distinctOutcomes.add(k); moves.push({ hi, r, c, n, k }); }
    decisions.push({ legal, maxFlip: Math.max(...moves.map(m => m.k)) });
    let mv;
    if (policy === 'random') mv = moves[Math.floor(Math.random() * moves.length)];
    else { const mx = Math.max(...moves.map(m => m.k)); const top = moves.filter(m => m.k === mx); mv = top[Math.floor(Math.random() * top.length)]; }
    const sp = samePlus(g, mv.r, mv.c, mv.n, 'player'); if (sp.sameHit || sp.plusHit) spOpp++; if (sp.sameHit) sameOpp++; if (sp.plusHit) plusOpp++;
    const id = hand[mv.hi]; hand.splice(mv.hi, 1);
    g[mv.r][mv.c] = { id, owner: 'player', nesw: mv.n }; const f = caps(g, mv.r, mv.c, mv.n, 'player'); f.forEach(([a, b]) => g[a][b].owner = 'player'); pFlips += f.length; pPlaced++;
    if (!empties(g).length || !hand.length) break;
    // boss turn (exact code logic: first-in-scan max)
    const open = empties(g); if (!open.length || !pool.length) continue;
    const aid = pool.pop(); let bs = open[Math.floor(Math.random() * open.length)], bc = -1;
    for (const [r, c] of open) { const n = stats(aid, c, true, st); const k = caps(g, r, c, n, 'ai').length; if (k > bc) { bc = k; bs = [r, c]; } }
    const n = stats(aid, bs[1], true, st); g[bs[0]][bs[1]] = { id: aid, owner: 'ai', nesw: n }; const bf = caps(g, bs[0], bs[1], n, 'ai'); bf.forEach(([a, b]) => g[a][b].owner = 'ai'); bFlips += bf.length; bPlaced++;
  }
  let blue = 0, red = 0, empty = 0; for (const row of g) for (const x of row) x.owner === 'player' ? blue++ : x.owner === 'ai' ? red++ : empty++;
  return { blue, red, empty, win: blue > red, pPlaced, bPlaced, pFlips, bFlips, spOpp, sameOpp, plusOpp, decisions, handLeft: hand.length };
}
// Tie-break audit: how often does the boss's random initial slot survive? (code: bestCount=-1 so first-in-scan always overwrites)
const N = 20000;
for (const policy of ['random', 'greedy']) for (const bonus of [0, 1]) {
  let w = 0, blueSum = 0, pP = 0, bP = 0, sp = 0, same = 0, plus = 0, plTurns = 0, legalSum = 0, zeroFlipTurns = 0, handLeft = 0; const dist = {};
  for (let i = 0; i < N; i++) { const r = play(policy, bonus); if (r.win) w++; blueSum += r.blue; pP += r.pPlaced; bP += r.bPlaced; sp += r.spOpp; same += r.sameOpp; plus += r.plusOpp; plTurns += r.pPlaced; handLeft += r.handLeft;
    r.decisions.forEach(d => { legalSum += d.legal; if (d.maxFlip === 0) zeroFlipTurns++; }); dist[r.blue] = (dist[r.blue] || 0) + 1; }
  out.sims[`${policy}_aiBonus${bonus}`] = { N, playerWinRate: +(w / N).toFixed(4), meanBlue: +(blueSum / N).toFixed(3), blueDist: dist,
    meanPlayerPlacements: +(pP / N).toFixed(3), meanBossPlacementsInclPreplaced: +(bP / N).toFixed(3), meanHandLeftAtEnd: +(handLeft / N).toFixed(3),
    meanLegalMovesPerPlayerTurn: +(legalSum / plTurns).toFixed(2), shareTurnsNoCaptureAvailable: +(zeroFlipTurns / plTurns).toFixed(4),
    samePlusWouldTriggerPerPlayerTurn: +(sp / plTurns).toFixed(4), sameOnly: +(same / plTurns).toFixed(4), plusOnly: +(plus / plTurns).toFixed(4) };
}
out.notes = ['No Tactical Slide, no nudges/rerolls; dice fixed at startStage default [4,2,5] (cols 1 and 3 boosted).',
  'Boss logic replicates executeBossTurn: bestCount=-1 init means the random initial slot is always overwritten by the first scanned slot with max flips (reading order).',
  'Same/Plus columns are counterfactual: share of player placements where FF8 Same or Plus WOULD fire if implemented (base values used).'];
const path = __dirname + '/structural_sim_output.json';
fs.writeFileSync(path, JSON.stringify(out, null, 2)); console.log(JSON.stringify(out, null, 1));
