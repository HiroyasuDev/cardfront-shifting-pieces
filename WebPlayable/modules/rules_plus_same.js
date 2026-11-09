/**
 * CARDFRONT 3D: Cradle of Echoes — Modular 3x3 Tactical Rules Engine
 * Implements:
 * 1. Classic Triple Triad `SAME` Rule (2+ orthogonal neighbors have equal opposing edge values `myVal === theirVal`)
 * 2. Classic Triple Triad `PLUS` Rule (2+ orthogonal neighbors share an identical edge sum `myVal + theirVal === sum`)
 * 3. `COMBO_CASCADE` Chain Captures (any enemy card flipped by SAME or PLUS triggers standard high-pip captures on its neighbors)
 * 4. `drawCardFromDeckPool(stateObj)` Singleton Deck-Draw-on-Turn / Tactical Draw from the 60-card Set 1 pool
 */
(function (root) {
  "use strict";

  const ORTHO_DIRS = [
    { dr: -1, dc: 0, myEdge: 0, theirEdge: 2, dirName: "N" },
    { dr: 0,  dc: 1, myEdge: 1, theirEdge: 3, dirName: "E" },
    { dr: 1,  dc: 0, myEdge: 2, theirEdge: 0, dirName: "S" },
    { dr: 0,  dc: -1, myEdge: 3, theirEdge: 1, dirName: "W" }
  ];

  /**
   * Evaluates Triple Triad SAME and PLUS rules at (r, c) for `nesw` and `owner`,
   * plus recursive COMBO_CASCADE captures on newly flipped enemy cards.
   */
  function evaluatePlusAndSameCaptures(grid, r, c, nesw, owner) {
    if (!grid || !Array.isArray(nesw) || nesw.length < 4) {
      return { sameFlips: [], plusFlips: [], comboFlips: [], allSpecialFlips: [] };
    }

    const occupiedNeighbors = [];
    for (const d of ORTHO_DIRS) {
      const nr = r + d.dr;
      const nc = c + d.dc;
      if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) {
        const nb = grid[nr] && grid[nr][nc];
        if (nb && nb.cardId && Array.isArray(nb.nesw)) {
          const myVal = Number(nesw[d.myEdge] || 0);
          const theirVal = Number(nb.nesw[d.theirEdge] || 0);
          occupiedNeighbors.push({
            nr,
            nc,
            owner: nb.owner,
            cardId: nb.cardId,
            nesw: nb.nesw.slice(),
            myVal,
            theirVal,
            sum: myVal + theirVal,
            equal: myVal === theirVal,
            dirName: d.dirName
          });
        }
      }
    }

    const sameFlips = [];
    const plusFlips = [];
    const flippedCoordSet = new Set();

    // 1. SAME RULE: 2 or more orthogonal neighbors have matching opposing edge values (myVal === theirVal)
    const equalNeighbors = occupiedNeighbors.filter(n => n.equal);
    if (equalNeighbors.length >= 2) {
      for (const n of equalNeighbors) {
        if (n.owner && n.owner !== owner) {
          const key = `${n.nr},${n.nc}`;
          if (!flippedCoordSet.has(key)) {
            flippedCoordSet.add(key);
            sameFlips.push({
              nr: n.nr,
              nc: n.nc,
              myVal: n.myVal,
              theirVal: n.theirVal,
              dirName: n.dirName,
              rule: "SAME"
            });
          }
        }
      }
    }

    // 2. PLUS RULE: 2 or more orthogonal neighbors share the exact same edge sum (myVal + theirVal)
    const sumGroups = new Map();
    for (const n of occupiedNeighbors) {
      if (!sumGroups.has(n.sum)) sumGroups.set(n.sum, []);
      sumGroups.get(n.sum).push(n);
    }
    for (const [sumVal, group] of sumGroups.entries()) {
      if (group.length >= 2) {
        for (const n of group) {
          if (n.owner && n.owner !== owner) {
            const key = `${n.nr},${n.nc}`;
            if (!flippedCoordSet.has(key)) {
              flippedCoordSet.add(key);
              plusFlips.push({
                nr: n.nr,
                nc: n.nc,
                myVal: n.myVal,
                theirVal: n.theirVal,
                edgeSum: sumVal,
                dirName: n.dirName,
                rule: "PLUS"
              });
            }
          }
        }
      }
    }

    // 3. COMBO CASCADE: Each card flipped by SAME or PLUS triggers standard high-pip captures on its neighbors
    const comboFlips = [];
    const queue = [...sameFlips, ...plusFlips];
    while (queue.length > 0) {
      const src = queue.shift();
      const srcCell = grid[src.nr] && grid[src.nr][src.nc];
      if (!srcCell || !Array.isArray(srcCell.nesw)) continue;
      for (const d of ORTHO_DIRS) {
        const ar = src.nr + d.dr;
        const ac = src.nc + d.dc;
        if (ar >= 0 && ar < 3 && ac >= 0 && ac < 3) {
          const adj = grid[ar] && grid[ar][ac];
          const key = `${ar},${ac}`;
          if (adj && adj.cardId && adj.owner !== owner && !flippedCoordSet.has(key)) {
            const srcEdgeVal = Number(srcCell.nesw[d.myEdge] || 0);
            const adjEdgeVal = Number(adj.nesw[d.theirEdge] || 0);
            if (srcEdgeVal > adjEdgeVal) {
              flippedCoordSet.add(key);
              const cascadeEvt = {
                nr: ar,
                nc: ac,
                fromR: src.nr,
                fromC: src.nc,
                myVal: srcEdgeVal,
                theirVal: adjEdgeVal,
                dirName: d.dirName,
                rule: "COMBO_CASCADE"
              };
              comboFlips.push(cascadeEvt);
              queue.push(cascadeEvt);
            }
          }
        }
      }
    }

    return {
      sameFlips,
      plusFlips,
      comboFlips,
      allSpecialFlips: [...sameFlips, ...plusFlips, ...comboFlips]
    };
  }

  /**
   * Builds a singleton draw pool from the player's unlocked Set 1 cards (or full catalog),
   * excluding cards already in `stateObj.hand` or on `stateObj.grid`.
   */
  function initDeckDrawPool(stateObj, catalogIds = []) {
    if (!stateObj) return [];
    const inUse = new Set(stateObj.hand || []);
    if (Array.isArray(stateObj.grid)) {
      for (const row of stateObj.grid) {
        for (const cell of row || []) {
          if (cell && cell.cardId) inUse.add(cell.cardId);
        }
      }
    }
    const sourcePool = [
      ...(Array.isArray(stateObj.unlockedCards) ? stateObj.unlockedCards : []),
      ...(Array.isArray(catalogIds) ? catalogIds : [])
    ];
    const pool = [];
    for (const cid of sourcePool) {
      if (cid && !inUse.has(cid) && !pool.includes(cid)) {
        pool.push(cid);
      }
    }
    stateObj.deckDrawPool = pool;
    return pool;
  }

  /**
   * Draws 1 singleton card from `stateObj.deckDrawPool` into `stateObj.hand` (up to 5 hand slots).
   */
  function drawCardFromDeckPool(stateObj) {
    if (!stateObj || !Array.isArray(stateObj.hand)) return null;
    if (stateObj.hand.length >= 5) return null;
    if (!Array.isArray(stateObj.deckDrawPool) || stateObj.deckDrawPool.length === 0) {
      return null;
    }
    const inUse = new Set(stateObj.hand);
    if (Array.isArray(stateObj.grid)) {
      for (const row of stateObj.grid) {
        for (const cell of row || []) {
          if (cell && cell.cardId) inUse.add(cell.cardId);
        }
      }
    }
    while (stateObj.deckDrawPool.length > 0) {
      const nextCid = stateObj.deckDrawPool.shift();
      if (nextCid && !inUse.has(nextCid)) {
        stateObj.hand.push(nextCid);
        stateObj.cardsDrawnThisMatch = (stateObj.cardsDrawnThisMatch || 0) + 1;
        return nextCid;
      }
    }
    return null;
  }

  const RulesPlusSameModule = {
    evaluatePlusAndSameCaptures,
    initDeckDrawPool,
    drawCardFromDeckPool
  };

  root.CardFrontModules = root.CardFrontModules || {};
  root.CardFrontModules.RulesPlusSame = RulesPlusSameModule;
})(typeof window !== "undefined" ? window : globalThis);
