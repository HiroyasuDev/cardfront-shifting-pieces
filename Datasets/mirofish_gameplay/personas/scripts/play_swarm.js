// MiroFish grounded persona playtest swarm for Cardfront: Cradle of Echoes.
// Each persona plays MATCHES_PER_STAGE full matches on each of the 4 stages in headless Chromium,
// using REAL mouse drags (hand→tile deploys, board→tile Tactical Slides) and real clicks (dice nudge/reroll).
// Decisions come from the persona policy (personas.js) evaluated on the live `state` read via page.evaluate;
// outcomes (flips, scores, boss replies) are always read back from the real game, never from the model.
//
// Usage: node play_swarm.js            (env: MATCHES_PER_STAGE=3 CONCURRENCY=5 ONLY=p01,p02 THINK_SCALE=1)
"use strict";
const path = require("path");
const fs = require("fs");
const { chromium } = require(process.env.PLAYWRIGHT_CORE || "/Users/frederickamina/.local/node_modules/playwright-core");
const PERSONAS = require("./personas");
const { makeSim } = require("./sim");

const ROOT = path.resolve(__dirname, "..");
const RAW = path.join(ROOT, "raw");
const SHOTS = path.join(ROOT, "screenshots");
const EXE = process.env.CHROMIUM_EXE ||
  "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const URL = process.env.GAME_URL || "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const MATCHES = +(process.env.MATCHES_PER_STAGE || 3);
const CONC = +(process.env.CONCURRENCY || 5);
const THINK_SCALE = +(process.env.THINK_SCALE || 1);
const ONLY = process.env.ONLY ? process.env.ONLY.split(",") : null;
const TAG = process.env.RUN_TAG || "";

fs.mkdirSync(RAW, { recursive: true });
fs.mkdirSync(SHOTS, { recursive: true });
const MOVES = path.join(RAW, `moves${TAG}.jsonl`);
const MATCHF = path.join(RAW, `matches${TAG}.jsonl`);
const EVENTS = path.join(RAW, `events${TAG}.jsonl`);
const append = (f, o) => fs.appendFileSync(f, JSON.stringify(o) + "\n");

// ---------- deterministic RNG (persona noise in Node; game Math.random seeded via init script) ----------
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hash = (s) => { let h = 2166136261; for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
const gauss = (rng) => { const u = 1 - rng(), v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const INIT_SCRIPT = `
(() => {
  const orig = Math.random; let s = 0, on = false;
  function m() { s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  Math.random = () => (on ? m() : orig());
  window.__reseed = (n) => { s = n >>> 0; on = true; };
})();`;

// ---------- planning ----------
function buildPlanner(P, CARDS, ENEMY_IDS, aiBonus, rng) {
  const sim = makeSim(Object.fromEntries(Object.entries(CARDS).map(([k, v]) => [k, v.nesw])), aiBonus);
  const unseen = (g) => {
    const on = new Set(); g.forEach((row) => row.forEach((x) => x.cardId && on.add(x.cardId)));
    return ENEMY_IDS.filter((e) => !on.has(e));
  };
  function reply(g) { // boss reply distribution over unseen enemy cards (uniform: pool order hidden from the player)
    const es = unseen(g);
    if (!es.length || !sim.empties(g).length) { const d = sim.score(g).diff; return { exp: d, worst: d, boards: [g] }; }
    let sum = 0, worst = Infinity; const boards = [];
    for (const e of es) { const b = sim.boss(g, e); const d = sim.score(b.g).diff; sum += d; worst = Math.min(worst, d); boards.push(b.g); }
    return { exp: sum / es.length, worst, boards };
  }
  function ply3(g, dice, hand) {
    const r = reply(g); let tot = 0;
    for (const b of r.boards) {
      let best = sim.score(b).diff;
      const em = sim.empties(b);
      if (em.length && hand.length) {
        best = -Infinity;
        for (const id of hand) for (const [rr, cc] of em) {
          const p = sim.place(b, dice, id, rr, cc); best = Math.max(best, reply(p.g).exp);
        }
      }
      tot += best;
    }
    return tot / r.boards.length;
  }
  // colour-vision noise: misperceive ownership of some occupied cells that touch an empty tile
  function perceive(grid) {
    if (!P.ownerMisread) return { g: grid, misreads: 0 };
    const g = sim.clone(grid); let n = 0;
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
      const x = g[r][c];
      if (!x.cardId) continue;
      const touchesEmpty = [[-1, 0], [1, 0], [0, -1], [0, 1]].some(([a, b]) => {
        const nr = r + a, nc = c + b; return nr >= 0 && nr < 3 && nc >= 0 && nc < 3 && !g[nr][nc].cardId;
      });
      if (touchesEmpty && rng() < P.ownerMisread) { x.owner = x.owner === "player" ? "ai" : "player"; n++; }
    }
    return { g, misreads: n };
  }

  function neutralAgency(S, chosen) { // persona-neutral: E[diff after boss] over all hand×tile placements
    const vals = [];
    let chosenVal = null;
    S.hand.forEach((id, i) => sim.empties(S.grid).forEach(([r, c]) => {
      const v = reply(sim.place(S.grid, S.dice, id, r, c).g).exp;
      vals.push(v);
      if (chosen && id === chosen.cardId && r === chosen.r && c === chosen.c) chosenVal = v;
    }));
    const mx = Math.max(...vals), mn = Math.min(...vals);
    return {
      decision_space: +(mx - mn).toFixed(3), regret: chosenVal == null ? null : +(mx - chosenVal).toFixed(3),
      agency: chosenVal == null || mx === mn ? null : +((chosenVal - mn) / (mx - mn)).toFixed(3),
      n_options: vals.length,
    };
  }

  function plan(S, mem, allowReroll) {
    const t0 = Date.now();
    const per = perceive(S.grid);
    const G = per.g;
    const out = { reroll: false, nudges: [], slide: null, place: null, misreads: per.misreads, random: false, candidates: 0 };
    const boosted = S.dice.filter((d) => d >= 4).length;
    if (allowReroll && S.rerollsLeft > 0) {
      if (P.reroll === "low_boost" && boosted <= 1) out.reroll = true;
      if (P.reroll === "drama" && boosted < 2 && rng() < 0.5) out.reroll = true;
      if (out.reroll) { out.compute_ms = Date.now() - t0; return out; } // re-plan after seeing the new dice
    }
    const allPlacements = [];
    S.hand.forEach((id, idx) => sim.empties(S.grid).forEach(([r, c]) => allPlacements.push({ idx, cardId: id, r, c })));

    if (P.policy === "random_biased") {
      let pick;
      const scored = allPlacements.map((p) => ({ p, f: sim.place(G, S.dice, p.cardId, p.r, p.c).flips }));
      const mxf = Math.max(...scored.map((s) => s.f));
      if (mxf > 0 && rng() < P.flipBias) { const best = scored.filter((s) => s.f === mxf); pick = best[Math.floor(rng() * best.length)].p; }
      else pick = allPlacements[Math.floor(rng() * allPlacements.length)];
      out.place = pick; out.candidates = allPlacements.length; out.compute_ms = Date.now() - t0;
      return out;
    }

    const nudgeSets = [[]];
    if (P.nudge !== "never" && S.nudgesLeft > 0) {
      for (let c = 0; c < 3; c++) nudgeSets.push([c]);
      if (P.nudge === "eval" && S.nudgesLeft >= 2) for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) nudgeSets.push([a, b]);
    }
    const nudgePen = P.nudge === "eval" ? 0.05 : 0.3;
    const slidePen = P.slide === "eval" ? 0.02 : P.slide === "spectacle" ? 0 : 0.3;
    const cands = [];
    for (const ns of nudgeSets) {
      let g0 = G, d0 = S.dice;
      for (const c of ns) { const r = sim.nudge(g0, d0, c); g0 = r.g; d0 = r.dice; }
      const slides = [null];
      if (P.slide !== "never" && !S.used) sim.legalSlides(S.grid).forEach((s) => slides.push(s)); // draggable cards are visually distinct
      for (const sl of slides) {
        let g1 = g0, sf = 0;
        if (sl) { const r = sim.slide(g0, d0, ...sl); g1 = r.g; sf = r.flips; }
        S.hand.forEach((id, idx) => sim.empties(g1).forEach(([r, c]) => {
          const p = sim.place(g1, d0, id, r, c);
          cands.push({ ns, sl, sf, idx, cardId: id, r, c, pf: p.flips, g2: p.g, d0 });
        }));
      }
    }
    for (const k of cands) {
      const rp = reply(k.g2);
      k.imm = sim.score(k.g2).diff; k.e2 = rp.exp; k.w2 = rp.worst;
      const pen = k.ns.length * nudgePen + (k.sl ? slidePen : 0);
      let v;
      switch (P.policy) {
        case "greedy": v = k.imm + 0.01 * k.e2; break;
        case "lane": {
          let colCount = 0; for (let r = 0; r < 3; r++) if (k.g2[r][k.c].owner === "player") colCount++;
          v = k.e2 + 0.4 * (k.d0[k.c] >= 4 ? 1 : 0) + 0.2 * colCount; break;
        }
        case "minimax": v = k.w2 + 0.3 * k.e2; break;
        case "spectacle": v = k.sf + k.pf + 0.15 * k.e2; break;
        case "coverage": {
          v = k.e2 + (mem.cardsPlayed.has(k.cardId) ? 0 : 0.35);
          if (P.forceTryMechanics) { if (k.sl && !mem.matchUsedSlide) v += 0.35; if (k.ns.length && !mem.matchUsedNudge) v += 0.35; }
          break;
        }
        default: v = k.e2; // expectimax, minmax3 (pre-score)
      }
      k.v = v - pen + rng() * 1e-6;
    }
    cands.sort((a, b) => b.v - a.v);
    if (P.policy === "minmax3") {
      const top = cands.slice(0, 12);
      for (const k of top) k.v = ply3(k.g2, k.d0, S.hand.filter((_, i) => i !== k.idx)) - k.ns.length * nudgePen - (k.sl ? slidePen : 0);
      top.sort((a, b) => b.v - a.v);
      cands.splice(0, 12, ...top);
    }
    const best = cands[0];
    out.candidates = cands.length;
    if (rng() < P.epsilon) { // persona error: random legal placement, no dice/slide this turn
      out.random = true;
      out.place = allPlacements[Math.floor(rng() * allPlacements.length)];
    } else {
      out.nudges = best.ns; out.slide = best.sl;
      out.place = { idx: best.idx, cardId: best.cardId, r: best.r, c: best.c };
      out.pred = { slide_flips: best.sf, place_flips: best.pf, value: +best.v.toFixed(3), e2: +best.e2.toFixed(3) };
    }
    out.compute_ms = Date.now() - t0;
    return out;
  }
  return { sim, plan, neutralAgency, reply };
}

// ---------- browser helpers ----------
async function readState(page) {
  return page.evaluate(() => ({
    stageIndex: state.stageIndex, isPlayerTurn: state.isPlayerTurn, gameOver: state.gameOver,
    grid: state.grid.map((row) => row.map((c) => ({ cardId: c.cardId, owner: c.owner, nesw: c.nesw.slice() }))),
    hand: state.hand.slice(), dice: state.colDice.slice(), nudgesLeft: state.nudgesLeft, rerollsLeft: state.rerollsLeft,
    used: state.usedSlideThisTurn, dragBusy: drag.active || drag.dropping,
    modal: getComputedStyle(document.getElementById("result-modal")).display,
  }));
}
const slotSel = (r, c) => `#grid-3x3 .board-slot[data-r="${r}"][data-c="${c}"]`;
async function box(page, sel) { const b = await page.locator(sel).first().boundingBox(); return b; }
async function center(page, sel) { const b = await box(page, sel); return [b.x + b.width / 2, b.y + b.height / 2, b]; }
async function clickSel(page, sel) { const [x, y] = await center(page, sel); await page.mouse.move(x, y, { steps: 5 }); await page.mouse.click(x, y); }
const scores = (g) => { let b = 0, r = 0; g.forEach((row) => row.forEach((x) => { if (x.owner === "player") b++; else if (x.owner === "ai") r++; })); return { blue: b, red: r }; };
const ownerDiff = (a, b) => { const o = []; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (a[r][c].cardId && b[r][c].cardId && a[r][c].owner !== b[r][c].owner) o.push([r, c]); return o; };

async function realDrag(page, from, toBox, P, rng, opts = {}) {
  const jx = opts.precise ? 0 : gauss(rng) * P.dragJitter * toBox.width;
  const jy = opts.precise ? 0 : gauss(rng) * P.dragJitter * toBox.height;
  const tx = toBox.x + toBox.width / 2 + jx, ty = toBox.y + toBox.height / 2 + jy;
  const t0 = Date.now();
  await page.mouse.move(from[0], from[1], { steps: 3 });
  await page.mouse.down();
  await page.mouse.move(from[0] + 12, from[1] - 14, { steps: 3 }); // lift past the 6px threshold
  await page.mouse.move(tx, ty, { steps: P.dragSteps });
  await sleep(110);
  if (opts.beforeUp) await opts.beforeUp();
  await page.mouse.up();
  return { ms: Date.now() - t0, release: [+(jx / toBox.width).toFixed(3), +(jy / toBox.height).toFixed(3)] };
}

async function misdrop(page, from, P) { // release over the header → spring-back
  await page.mouse.move(from[0], from[1], { steps: 3 });
  await page.mouse.down();
  await page.mouse.move(from[0] + 40, 22, { steps: Math.max(4, P.dragSteps >> 1) });
  await sleep(80);
  await page.mouse.up();
  await sleep(420);
}

// ---------- one persona ----------
async function runPersona(browser, P) {
  const ctx = await browser.newContext({ viewport: { width: 1408, height: 800 }, deviceScaleFactor: 1 });
  await ctx.addInitScript(INIT_SCRIPT);
  const page = await ctx.newPage();
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") pageErrors.push("console:" + m.text()); });
  page.on("requestfailed", (r) => pageErrors.push("requestfailed:" + r.url().replace(/^https?:\/\/[^/]+/, "") + " " + (r.failure() || {}).errorText));
  await page.goto(URL + "?persona=" + P.id + "&t=" + Date.now());
  await page.waitForFunction(() => typeof state !== "undefined" && state.grid.length === 3);
  await sleep(600);
  const meta = await page.evaluate(() => ({
    cards: Object.fromEntries(Object.entries(ALL_CARDS).map(([k, v]) => [k, { nesw: v.nesw.slice(), name: v.name }])),
    enemies: ENEMY_MECHS.map((e) => e.id), heroes: PLAYER_HEROES.map((h) => h.id),
    stages: STAGES.map((s) => ({ name: s.name, aiBonus: s.aiBonus, bossId: s.bossId })),
  }));
  const pdir = path.join(SHOTS, P.id + "_" + P.name);
  fs.mkdirSync(pdir, { recursive: true });
  const existing = fs.existsSync(MATCHF)
    ? Object.fromEntries(fs.readFileSync(MATCHF, "utf8").trim().split("\n").filter(Boolean).map((l) => { const o = JSON.parse(l); return [o.match_id, o]; }))
    : {};
  const rng = mulberry32(hash(P.id + "persona"));
  const mem = { cardsPlayed: new Set(), cumFrustration: 0, wouldQuitAt: null, matchIdx: 0 };

  for (let stage = 0; stage < 4; stage++) {
    for (let m = 0; m < MATCHES; m++) {
      mem.matchIdx++;
      const matchId = `${P.id}_s${stage + 1}_m${m + 1}`;
      if (existing[matchId]) {
        const prev = existing[matchId];
        (prev.cards_played || []).forEach((c) => mem.cardsPlayed.add(c));
        mem.cumFrustration = prev.cum_frustration || 0;
        mem.wouldQuitAt = prev.would_quit_at_match || null;
        for (let k = 0; k < 17; k++) rng();
        continue;
      }
      const errBefore = pageErrors.length;
      try {
        await runMatch(page, P, meta, stage, m, matchId, rng, mem, pdir);
      } catch (e) {
        append(EVENTS, { persona: P.id, match_id: matchId, event: "match_error", error: String(e).slice(0, 400) });
        await page.goto(URL + "?persona=" + P.id + "&t=" + Date.now());
        await page.waitForFunction(() => typeof state !== "undefined" && state.grid.length === 3);
        await sleep(600);
      }
      if (pageErrors.length > errBefore) append(EVENTS, { persona: P.id, match_id: matchId, event: "page_errors", errors: pageErrors.slice(errBefore) });
    }
  }
  await ctx.close();
}

async function startMatch(page, stage, seed) {
  const s = await readState(page);
  if (s.modal === "flex") { await clickSel(page, '#result-modal button:has-text("Play Again")'); await sleep(250); }
  await page.evaluate((n) => window.__reseed(n), seed);
  const cur = await page.evaluate(() => state.stageIndex);
  if (cur !== stage) await page.selectOption("#stage-select", String(stage));
  else await clickSel(page, 'header button:has-text("Reset")');
  await page.mouse.move(700, 790); // park the pointer off-board
  await sleep(350);
}

async function runMatch(page, P, meta, stage, m, matchId, rng, mem, pdir) {
  const seed = hash(matchId);
  await startMatch(page, stage, seed);
  const aiBonus = meta.stages[stage].aiBonus;
  const planner = buildPlanner(P, meta.cards, meta.enemies, aiBonus, rng);
  const tMatch = Date.now();
  let S = await readState(page);
  const timeline = [{ t: "start", ...scores(S.grid) }];
  const tot = { flips_gained: 0, flips_lost: 0, slide_flips: 0, nudges: 0, rerolls: 0, slides: 0, misdrops: 0, drop_retries: 0, drop_mismatch: 0, random_moves: 0, misreads: 0, invalid_actions: 0 };
  const lostAt = []; const cardsPlayed = [];
  const shots = [];
  mem.matchUsedSlide = false; mem.matchUsedNudge = false;
  let turn = 0;
  while (!S.gameOver && turn < 8) {
    turn++;
    const rec = { persona: P.id, persona_name: P.name, match_id: matchId, stage: stage + 1, match_idx: m + 1, turn,
      dice_start: S.dice.slice(), nudges_left_start: S.nudgesLeft, rerolls_left_start: S.rerollsLeft };
    const think = Math.round((P.thinkMs[0] + rng() * (P.thinkMs[1] - P.thinkMs[0])));
    rec.think_ms_modeled = think;
    const tw = Date.now(); await sleep(think * THINK_SCALE); rec.think_ms_waited = Date.now() - tw;
    let pl = planner.plan(S, mem, true);
    let compute = pl.compute_ms;
    rec.actions = [];
    if (pl.reroll) {
      const before = S.dice.slice();
      await clickSel(page, 'button:has-text("Roll All")'); await sleep(250);
      S = await readState(page); tot.rerolls++;
      rec.reroll = { before, after: S.dice.slice() }; rec.actions.push("reroll");
      pl = planner.plan(S, mem, false); compute += pl.compute_ms;
    }
    rec.policy_compute_ms = compute; rec.candidates = pl.candidates; rec.misreads = pl.misreads; tot.misreads += pl.misreads;
    rec.random_move = pl.random; if (pl.random) tot.random_moves++;
    if (pl.nudges.length) {
      rec.nudges = [];
      for (const c of pl.nudges) {
        const before = (await readState(page)).dice[c];
        await sleep(180 * THINK_SCALE);
        await clickSel(page, `#dice-column-list .col-die-row >> nth=${c}`); await sleep(160);
        const after = (await readState(page)).dice[c];
        rec.nudges.push({ col: c + 1, before, after, applied: after !== before }); tot.nudges++;
        if (after === before) tot.invalid_actions++;
        rec.actions.push("nudge");
      }
      mem.matchUsedNudge = true;
      S = await readState(page);
    }
    if (pl.slide) {
      const [sr, sc, nr, nc] = pl.slide;
      const before = await readState(page);
      const [ax, ay] = await center(page, slotSel(sr, sc));
      const tb = await box(page, slotSel(nr, nc));
      await sleep(200 * THINK_SCALE);
      const d = await realDrag(page, [ax, ay], tb, P, rng);
      await sleep(450);
      S = await readState(page);
      const moved = !S.grid[sr][sc].cardId;
      let landed = null;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!before.grid[r][c].cardId && S.grid[r][c].cardId === before.grid[sr][sc].cardId) landed = [r + 1, c + 1];
      const fl = ownerDiff(before.grid, S.grid).length;
      rec.slide = { from: [sr + 1, sc + 1], to: [nr + 1, nc + 1], landed, card: before.grid[sr][sc].cardId, ok: moved, flips: fl,
        flips_pred: pl.pred ? pl.pred.slide_flips : null, drag_ms: d.ms, release_offset: d.release };
      if (moved) { tot.slides++; tot.slide_flips += fl; mem.matchUsedSlide = true; } else tot.invalid_actions++;
      rec.actions.push("slide");
      timeline.push({ t: `T${turn}-slide`, ...scores(S.grid) });
      if (!moved) { pl = planner.plan(S, mem, false); }
      // card indices may shift? (hand untouched by slide) — but target tile may be taken by the slide; re-plan if so
      if (S.grid[pl.place.r][pl.place.c].cardId) { pl = planner.plan({ ...S, used: true }, mem, false); }
    }
    // ---- deploy: real mouse drag from hand card to tile ----
    const idx = S.hand.indexOf(pl.place.cardId);
    const handSel = `#hand-bar .hand-card-wrap >> nth=${idx}`;
    rec.card = pl.place.cardId; rec.card_name = meta.cards[pl.place.cardId].name; rec.intended_tile = [pl.place.r + 1, pl.place.c + 1];
    rec.flips_pred = pl.pred ? pl.pred.place_flips : planner.sim.place(S.grid, S.dice, pl.place.cardId, pl.place.r, pl.place.c).flips;
    Object.assign(rec, planner.neutralAgency(S, pl.place));
    const preDeploy = await readState(page);
    let misdrops = 0;
    if (rng() < P.misdropProb) { const [hx, hy] = await center(page, handSel); await misdrop(page, [hx, hy], P); misdrops++; tot.misdrops++; }
    let placed = null, retries = 0, dragInfo = null, midShot = null;
    while (!placed && retries < 3) {
      const [hx, hy] = await center(page, handSel);
      const tb = await box(page, slotSel(pl.place.r, pl.place.c));
      const wantMidShot = P.id === "p07" && turn === 2 && !midShot;
      dragInfo = await realDrag(page, [hx, hy], tb, P, rng, {
        precise: retries > 0,
        beforeUp: wantMidShot ? async () => { midShot = path.join(pdir, `${matchId}_dragmid.jpg`); await page.screenshot({ path: midShot, type: "jpeg", quality: 70 }); } : null,
      });
      try {
        await page.waitForFunction((n) => state.hand.length < n, preDeploy.hand.length, { timeout: 1500, polling: "raf" });
      } catch (_) { retries++; tot.drop_retries++; await sleep(300); continue; }
      const post = await readState(page);
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!preDeploy.grid[r][c].cardId && post.grid[r][c].cardId === pl.place.cardId) placed = { r, c, post };
      if (!placed) { retries++; tot.drop_retries++; }
    }
    if (midShot) shots.push(path.relative(ROOT, midShot));
    if (!placed) throw new Error("deploy failed after retries");
    rec.landed_tile = [placed.r + 1, placed.c + 1];
    rec.drop_mismatch = placed.r !== pl.place.r || placed.c !== pl.place.c; if (rec.drop_mismatch) tot.drop_mismatch++;
    rec.misdrops = misdrops; rec.drop_retries = retries; rec.drag_ms = dragInfo.ms; rec.release_offset = dragInfo.release;
    const gained = ownerDiff(preDeploy.grid, placed.post.grid).length;
    rec.flips_gained = gained; tot.flips_gained += gained;
    rec.score_after_place = scores(placed.post.grid);
    rec.decision_latency_ms = rec.think_ms_waited + compute;
    cardsPlayed.push(pl.place.cardId); mem.cardsPlayed.add(pl.place.cardId);
    timeline.push({ t: `T${turn}-place`, ...rec.score_after_place });
    rec.actions.push("place");
    // ---- boss reply ----
    await page.waitForFunction(() => state.isPlayerTurn || state.gameOver, null, { timeout: 6000 });
    await sleep(120);
    S = await readState(page);
    let bossCard = null, bossSlot = null;
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!placed.post.grid[r][c].cardId && S.grid[r][c].cardId) { bossCard = S.grid[r][c].cardId; bossSlot = [r, c]; }
    if (bossCard) {
      const lost = ownerDiff(placed.post.grid, S.grid);
      const pred = planner.sim.boss(placed.post.grid, bossCard);
      rec.boss = { card: bossCard, card_name: meta.cards[bossCard].name, tile: [bossSlot[0] + 1, bossSlot[1] + 1], flips: lost.length,
        lost_tiles: lost.map(([a, b]) => [a + 1, b + 1]), pred_tile: pred.slot && [pred.slot[0] + 1, pred.slot[1] + 1],
        pred_match: !!pred.slot && pred.slot[0] === bossSlot[0] && pred.slot[1] === bossSlot[1], pred_flips: pred.flips };
      tot.flips_lost += lost.length;
      lost.forEach(([a, b]) => lostAt.push({ turn, tile: [a + 1, b + 1], kind: (a === 1 && b === 1) ? "center" : (a !== 1 && b !== 1) ? "corner" : "edge" }));
    }
    rec.score_after_boss = scores(S.grid);
    timeline.push({ t: `T${turn}-boss`, ...rec.score_after_boss });
    append(MOVES, rec);
    if (turn === 2 && P.id !== "p07") {
      const f = path.join(pdir, `${matchId}_mid.jpg`);
      await page.screenshot({ path: f, type: "jpeg", quality: 70 }); shots.push(path.relative(ROOT, f));
    }
  }
  // ---- game over ----
  await page.waitForFunction(() => getComputedStyle(document.getElementById("result-modal")).display === "flex", null, { timeout: 4000 });
  await sleep(250);
  const fin = await readState(page);
  const modalTitle = await page.evaluate(() => document.getElementById("modal-title").textContent);
  const f = path.join(pdir, `${matchId}_final.jpg`);
  await page.screenshot({ path: f, type: "jpeg", quality: 70 }); shots.push(path.relative(ROOT, f));
  const sc = scores(fin.grid);
  const win = sc.blue > sc.red;
  const mf = Math.max(0, (win ? 0 : 0.6) + 0.15 * tot.flips_lost + 0.25 * tot.misdrops + 0.2 * tot.drop_mismatch + 0.1 * (tot.drop_retries + tot.invalid_actions) - 0.1 * tot.flips_gained);
  mem.cumFrustration = mem.cumFrustration * (win ? 0.7 : 1) + mf;
  if (mem.wouldQuitAt == null && mem.cumFrustration > P.patience) mem.wouldQuitAt = mem.matchIdx;
  append(MATCHF, {
    persona: P.id, persona_name: P.name, match_id: matchId, stage: stage + 1, stage_name: meta.stages[stage].name, ai_bonus: aiBonus,
    match_idx: m + 1, seed, outcome: win ? "win" : "loss", blue: sc.blue, red: sc.red, margin: sc.blue - sc.red,
    modal_title: modalTitle, modal_consistent: modalTitle.includes(win ? "VICTORY" : "DEFEAT"), turns: turn,
    score_timeline: timeline, cards_played: cardsPlayed, unused_hand: fin.hand, totals: tot, lost_at: lostAt,
    frustration_match: +mf.toFixed(3), frustration_index: +Math.min(1, mf / 2).toFixed(3),
    cum_frustration: +mem.cumFrustration.toFixed(3), would_quit_at_match: mem.wouldQuitAt,
    duration_ms: Date.now() - tMatch, screenshots: shots,
  });
  console.log(`[${P.id} ${P.name}] ${matchId} ${win ? "WIN " : "LOSS"} ${sc.blue}-${sc.red} flips+${tot.flips_gained}/-${tot.flips_lost} nud${tot.nudges} rr${tot.rerolls} sl${tot.slides} md${tot.misdrops} ${Math.round((Date.now() - tMatch) / 1000)}s`);
}

(async () => {
  const list = PERSONAS.filter((p) => !ONLY || ONLY.includes(p.id));
  const browser = await chromium.launch({ headless: true, executablePath: EXE });
  const queue = list.slice();
  const t0 = Date.now();
  await Promise.all(Array.from({ length: Math.min(CONC, queue.length) }, async () => {
    while (queue.length) {
      const P = queue.shift();
      try { await runPersona(browser, P); }
      catch (e) { console.error(`[${P.id}] persona failed`, e); append(EVENTS, { persona: P.id, event: "persona_error", error: String(e) }); }
    }
  }));
  await browser.close();
  console.log(`done in ${Math.round((Date.now() - t0) / 1000)}s`);
})();
