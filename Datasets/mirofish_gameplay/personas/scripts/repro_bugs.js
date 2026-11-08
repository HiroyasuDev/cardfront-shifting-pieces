// Deterministic repros for issues surfaced by the persona swarm (read-only against the game; no HTML edits).
// Output: raw/repro_bugs.json
"use strict";
const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");
const EXE = "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const URL = process.env.GAME_URL || "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const OUT = path.resolve(__dirname, "..", "raw", "repro_bugs.json");

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: EXE });
  const res = {};

  // 1) Viewport clipping of the right panel at common sizes
  res.viewport_clipping = {};
  for (const [w, h] of [[1280, 720], [1408, 800], [1920, 1080]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto(URL + "?repro=" + Date.now());
    await page.waitForTimeout(800);
    res.viewport_clipping[`${w}x${h}`] = await page.evaluate(() => {
      const W = window.innerWidth, H = window.innerHeight;
      const probe = {
        reroll_button: [...document.querySelectorAll("button")].find((b) => b.textContent.includes("Roll All")),
        nudge_counter: document.getElementById("nudge-left"),
        turn_badge: document.getElementById("turn-badge"),
        last_move_banner: document.getElementById("last-move-banner"),
        right_panel: document.querySelectorAll("aside.side-box")[1],
        grid: document.getElementById("grid-3x3"),
        hand: document.getElementById("hand-bar"),
      };
      const o = { innerWidth: W, innerHeight: H, docScrollWidth: document.documentElement.scrollWidth };
      for (const [k, el] of Object.entries(probe)) {
        if (!el) { o[k] = null; continue; }
        const r = el.getBoundingClientRect();
        o[k] = { right: Math.round(r.right), bottom: Math.round(r.bottom), clipped_x: r.right > W + 0.5, clipped_y: r.bottom > H + 0.5 };
      }
      return o;
    });
    await page.screenshot({ path: path.resolve(__dirname, "..", "screenshots", `viewport_${w}x${h}.jpg`), type: "jpeg", quality: 70 });
    await page.close();
  }

  const page = await browser.newPage({ viewport: { width: 1408, height: 800 } });
  await page.goto(URL + "?repro2=" + Date.now());
  await page.waitForTimeout(800);

  // 2) Boss tie-break: the random initial pick in executeBossTurn never survives (bestCount starts at -1)
  res.boss_tiebreak = await page.evaluate(() => {
    const counts = {};
    for (let trial = 0; trial < 200; trial++) {
      startStage(0);
      // empty board except boss opener; give boss a card; no captures possible → every open slot ties at 0 flips
      state.grid.forEach((row) => row.forEach((c) => { c.cardId = null; c.owner = null; c.nesw = [0, 0, 0, 0]; }));
      state.aiPool = ["e_eclipse"];
      state.isPlayerTurn = false;
      executeBossTurn();
      let pos = null;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (state.grid[r][c].cardId) pos = `${r},${c}`;
      counts[pos] = (counts[pos] || 0) + 1;
    }
    return { trials: 200, placement_counts_on_all_tie_board: counts };
  });

  // 3) Captured-card stat drift: captured enemy card re-derived from base on any dice change (loses aiBonus)
  res.captured_card_stat_drift = await page.evaluate(() => {
    startStage(2); // Stage 3: aiBonus = 1
    state.grid.forEach((row) => row.forEach((c) => { c.cardId = null; c.owner = null; c.nesw = [0, 0, 0, 0]; }));
    // enemy card at (0,1) with boss stats, then the player captures it
    state.grid[0][1].cardId = "e_titan"; state.grid[0][1].owner = "ai"; state.grid[0][1].nesw = getCardEffectiveStats("e_titan", 1, true);
    const before_capture = state.grid[0][1].nesw.slice();
    state.grid[0][1].owner = "player"; // as findCaptures→flip does: owner changes, nesw untouched
    const after_capture = state.grid[0][1].nesw.slice();
    state.isPlayerTurn = true; state.nudgesLeft = 2;
    nudgeColDie(0); // nudge an UNRELATED column (col 1)
    const after_unrelated_nudge = state.grid[0][1].nesw.slice();
    return { card: "e_titan", base: ALL_CARDS.e_titan.nesw, col2_die: state.colDice[1], before_capture, after_capture, after_unrelated_nudge,
      changed: JSON.stringify(after_capture) !== JSON.stringify(after_unrelated_nudge) };
  });

  // 4) Stage boss identity is cosmetic: how often is the stage's bossId among the 6 enemies used?
  res.stage_boss_presence = await page.evaluate(() => {
    const o = {};
    STAGES.forEach((st, i) => {
      let present = 0;
      for (let t = 0; t < 300; t++) {
        startStage(i);
        const used = [state.grid[0][1].cardId, ...state.aiPool];
        if (used.includes(st.bossId)) present++;
      }
      o[st.name] = { bossId: st.bossId, trials: 300, boss_card_in_enemy_lineup_pct: +(100 * present / 300).toFixed(1) };
    });
    return o;
  });

  // 5) Card power budget (edge sums) — balance context
  res.edge_sums = await page.evaluate(() => ({
    heroes: Object.fromEntries(PLAYER_HEROES.map((h) => [h.id, h.nesw.reduce((a, b) => a + b, 0)])),
    enemies: Object.fromEntries(ENEMY_MECHS.map((e) => [e.id, e.nesw.reduce((a, b) => a + b, 0)])),
  }));
  const hs = Object.values(res.edge_sums.heroes), es = Object.values(res.edge_sums.enemies);
  res.edge_sums.hero_mean = +(hs.reduce((a, b) => a + b, 0) / hs.length).toFixed(2);
  res.edge_sums.enemy_mean = +(es.reduce((a, b) => a + b, 0) / es.length).toFixed(2);
  res.edge_sums.enemy_mean_with_aiBonus1 = +(res.edge_sums.enemy_mean + 4).toFixed(2);

  // 6) Max edge per card side — how often can a hero edge beat an enemy edge at all
  res.edge_win_prob = await page.evaluate(() => {
    let win = 0, tot = 0, winB = 0;
    for (const h of PLAYER_HEROES) for (const e of ENEMY_MECHS) for (let s = 0; s < 4; s++) {
      const opp = (s + 2) % 4; tot++;
      if (h.nesw[s] > e.nesw[opp]) win++;
      if (h.nesw[s] > Math.min(9, e.nesw[opp] + 1)) winB++;
    }
    return { pct_hero_edge_beats_facing_enemy_edge_stage12: +(100 * win / tot).toFixed(1), pct_stage34: +(100 * winB / tot).toFixed(1) };
  });
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(res, null, 2));
  console.log(JSON.stringify(res, null, 2));
})().catch((e) => { console.error(e); process.exit(1); });
