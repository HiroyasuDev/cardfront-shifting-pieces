// Pure rules model mirroring the game's inline <script> (code wins; see line refs in REPORT.md).
// Used ONLY for persona decision-making / lookahead and for prediction-vs-actual fidelity checks.
// The game itself is always driven through real mouse input; outcomes are read back from `state`.
"use strict";

const DIRS = [ // dr, dc, myEdge, theirEdge  (NESW = top,right,bottom,left) — mirrors findCaptures()
  [-1, 0, 0, 2],
  [0, 1, 1, 3],
  [1, 0, 2, 0],
  [0, -1, 3, 1],
];

function makeSim(CARDS, aiBonus) {
  const eff = (id, c, dice) => CARDS[id].map((v) => Math.min(9, v + (dice[c] >= 4 ? 1 : 0)));
  const aiEff = (id) => CARDS[id].map((v) => Math.min(9, v + aiBonus));
  const clone = (g) => g.map((row) => row.map((x) => ({ cardId: x.cardId, owner: x.owner, nesw: x.nesw.slice() })));

  function captures(g, r, c, nesw, owner) {
    const out = [];
    for (const [dr, dc, me, them] of DIRS) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr > 2 || nc < 0 || nc > 2) continue;
      const nb = g[nr][nc];
      if (nb.cardId && nb.owner !== owner && nesw[me] > nb.nesw[them]) out.push([nr, nc]);
    }
    return out;
  }
  // recalcBoardStats(): every player-owned cell (incl. captured enemy cards) re-derives from base + column boost
  function recalc(g, dice) {
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      const x = g[r][c];
      if (x.cardId && x.owner === "player") x.nesw = eff(x.cardId, c, dice);
    }
  }
  function nudge(g, dice, col) {
    const d = dice.slice();
    d[col] = (d[col] % 6) + 1;
    const g2 = clone(g);
    recalc(g2, d);
    return { g: g2, dice: d };
  }
  function place(g, dice, id, r, c) {
    const g2 = clone(g);
    g2[r][c] = { cardId: id, owner: "player", nesw: eff(id, c, dice) };
    const f = captures(g2, r, c, g2[r][c].nesw, "player");
    f.forEach(([a, b]) => { g2[a][b].owner = "player"; });
    return { g: g2, flips: f.length, flipCells: f };
  }
  function slide(g, dice, sr, sc, r, c) {
    const g2 = clone(g);
    const id = g2[sr][sc].cardId;
    g2[r][c] = { cardId: id, owner: "player", nesw: eff(id, c, dice) };
    g2[sr][sc] = { cardId: null, owner: null, nesw: [0, 0, 0, 0] };
    const f = captures(g2, r, c, g2[r][c].nesw, "player");
    f.forEach(([a, b]) => { g2[a][b].owner = "player"; });
    return { g: g2, flips: f.length, flipCells: f };
  }
  // executeBossTurn(): bestSlot is overwritten by the first open slot in row-major order (f > -1),
  // so ties resolve to the FIRST max-flip slot — the random initial pick never survives.
  function boss(g, aiId) {
    const open = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!g[r][c].cardId) open.push([r, c]);
    if (!open.length) return { g, flips: 0, slot: null };
    const st = aiEff(aiId);
    let best = null, bc = -1;
    for (const [r, c] of open) {
      const f = captures(g, r, c, st, "ai").length;
      if (f > bc) { bc = f; best = [r, c]; }
    }
    const g2 = clone(g);
    g2[best[0]][best[1]] = { cardId: aiId, owner: "ai", nesw: st };
    const f = captures(g2, best[0], best[1], st, "ai");
    f.forEach(([a, b]) => { g2[a][b].owner = "ai"; });
    return { g: g2, flips: f.length, slot: best, flipCells: f };
  }
  function score(g) {
    let b = 0, rd = 0;
    for (const row of g) for (const x of row) { if (x.owner === "player") b++; else if (x.owner === "ai") rd++; }
    return { blue: b, red: rd, diff: b - rd };
  }
  const empties = (g) => {
    const o = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!g[r][c].cardId) o.push([r, c]);
    return o;
  };
  function legalSlides(g) {
    const o = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      if (!(g[r][c].cardId && g[r][c].owner === "player")) continue;
      for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !g[nr][nc].cardId) o.push([r, c, nr, nc]);
      }
    }
    return o;
  }
  return { eff, aiEff, clone, captures, recalc, nudge, place, slide, boss, score, empties, legalSlides };
}

module.exports = { makeSim, DIRS };
