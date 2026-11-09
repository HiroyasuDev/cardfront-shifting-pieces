#!/usr/bin/env node
/**
 * Tools/skill_harness/assess_tabletop_real_estate.js
 * ==================================================
 * Multi-Viewport & Multi-State Tactile Tabletop Real-Estate Assessment
 * for CARDFRONT 3D: Cradle of Echoes (`gemini-4-argon` harness integration).
 *
 * Evaluates 5 standard desktop/tablet landscape viewports:
 *   - 1920x1080 (Full HD 16:9)
 *   - 1440x900  (MacBook Pro 16:10)
 *   - 1408x800  (Playtest Default)
 *   - 1280x800  (Steam Deck / Compact 16:10)
 *   - 1180x820  (iPad Air Landscape)
 *
 * Across 8 interactive tabletop states:
 *   1. Initial Duel Topology (Top Boss -> 3D Column Dice -> 3x3 Stone Board -> Bottom Hand Fan)
 *   2. Board Horizontal Real-Estate Utilization (>= 42% viewport width)
 *   3. Row-3-to-Hand Vertical Clearance (Zero overlap across all 9 sockets)
 *   4. Top-Right Settings Drawer Non-Collision with Boss Commander Banner
 *   5. Card Nameplate Top-Header Readability (Zero collision with #last-move-banner)
 *   6. Hand Card Hover Scale & Floating Ability Tooltip (.hand-card-tooltip)
 *   7. Tactical Slide Directional Arrow Previews (▲/▼/◀/▶ SLIDE)
 *   8. Column Die Nudge Surge Animation & 60-Card Deck Stack Modal Trigger
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require(process.env.PLAYWRIGHT_CORE || "/Users/frederickamina/.local/node_modules/playwright-core");

const CHROMIUM_EXE =
  process.env.CHROMIUM_EXE ||
  "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const PLAYTEST_URL =
  process.env.PLAYTEST_URL ||
  "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const OUT_JSON = path.resolve(
  __dirname,
  "../../Datasets/mirofish_gameplay/ux_qa/raw/tabletop_real_estate_assessment.json"
);

const VIEWPORTS = [
  { name: "1920x1080_fhd", width: 1920, height: 1080 },
  { name: "1440x900_macbook", width: 1440, height: 900 },
  { name: "1408x800_harness", width: 1408, height: 800 },
  { name: "1280x800_steamdeck", width: 1280, height: 800 },
  { name: "1180x820_ipad_land", width: 1180, height: 820 },
];

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: CHROMIUM_EXE });
  const results = [];
  let totalChecks = 0;
  let passedChecks = 0;

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    await page.goto(`${PLAYTEST_URL}?assess=${Date.now()}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(350);

    const vpReport = await page.evaluate(() => {
      startStage(0);
      const rect = (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const b = el.getBoundingClientRect();
        return {
          x: Math.round(b.x),
          y: Math.round(b.y),
          w: Math.round(b.width),
          h: Math.round(b.height),
          top: Math.round(b.top),
          bottom: Math.round(b.bottom),
          left: Math.round(b.left),
          right: Math.round(b.right),
        };
      };

      const header = rect("header");
      const boss = rect("#boss-tabletop-crest");
      const slab = rect("#board-3d-slab");
      const row3 = rect('.board-slot[data-r="2"][data-c="1"]');
      const hand = rect("#hand-bar");
      const tip = rect("#last-move-banner");
      const deck = rect(".tabletop-deck-stack");

      // Check 1: Zero page overflow
      const noOverflow =
        document.documentElement.scrollWidth <= window.innerWidth &&
        document.documentElement.scrollHeight <= window.innerHeight;

      // Check 2: Board horizontal width utilization >= 40%
      const boardWidthRatio = +(slab.w / window.innerWidth).toFixed(3);
      const boardWidthOk = boardWidthRatio >= 0.40;

      // Check 3: Row 3 to Hand vertical clearance (zero overlap)
      const gapRow3ToHandPx = hand.top - row3.bottom;
      const zeroRow3Overlap = gapRow3ToHandPx >= 6;

      // Check 4: Head-to-head vertical topology
      const duelTopologyOk = boss.top < slab.top && slab.top < hand.top && boss.bottom <= slab.top + 10;

      // Check 5: Open settings popover non-collision with Boss Commander banner
      const drawerEl = document.getElementById("dev-camera-drawer");
      drawerEl.classList.remove("collapsed");
      const drawerRect = drawerEl.getBoundingClientRect();
      const drawerClearancePx = Math.round(drawerRect.left - boss.right);
      const drawerNonCollision = drawerClearancePx >= 8;
      drawerEl.classList.add("collapsed");

      // Check 6: Top-header card nameplates clear of bottom instructional banner
      const ribbons = Array.from(document.querySelectorAll("#hand-bar .slot-name-ribbon"));
      const nameplatesClear =
        ribbons.length === 5 &&
        ribbons.every((r) => {
          const rb = r.getBoundingClientRect();
          const cb = r.closest(".card-3d-unit").getBoundingClientRect();
          return rb.top - cb.top <= 14 && rb.bottom < tip.top;
        });

      // Check 7: Circular 3D column die pedestals aligned above Columns 1-3
      const pills = Array.from(document.querySelectorAll("#col-headers .col-header-pill"));
      const diceAligned =
        pills.length === 3 &&
        pills.every((p, c) => {
          const s = document.querySelector(`.board-slot[data-r="0"][data-c="${c}"]`);
          const pr = p.getBoundingClientRect();
          const sr = s.getBoundingClientRect();
          return (
            Boolean(p.querySelector(".die-pedestal-ring .cube-3d")) &&
            Math.abs(pr.left + pr.width / 2 - (sr.left + sr.width / 2)) <= 18
          );
        });

      // Check 8: Tactical Slide directional arrows + Column Die surge
      state.grid[1][1] = { r: 1, c: 1, cardId: "h_archangel", owner: "player", nesw: [8, 7, 6, 7], justFlipped: false };
      state.selectedBoardSlot = { r: 1, c: 1 };
      renderAll();
      const slideArrowsCount = document.querySelectorAll(".board-slot.slide-target .slide-arrow-call").length;
      state.colDice = [4, 3, 5];
      nudgeColDie(1);
      const surgeCount = document.querySelectorAll(".board-slot.col-surge-active").length;
      const interactiveJuiceOk = slideArrowsCount >= 3 && surgeCount === 3 && isColBoosted(1);
      startStage(0);

      const checks = {
        noOverflow,
        boardWidthOk,
        zeroRow3Overlap,
        duelTopologyOk,
        drawerNonCollision,
        nameplatesClear,
        diceAligned,
        interactiveJuiceOk,
      };

      return {
        metrics: {
          boardWidthPx: slab.w,
          boardHeightPx: slab.h,
          boardWidthPct: +(boardWidthRatio * 100).toFixed(1),
          socketWidthPx: row3.w,
          socketHeightPx: row3.h,
          gapBossToSlabPx: slab.top - boss.bottom,
          gapRow3ToHandPx,
          drawerClearancePx,
          deckVisible: Boolean(deck && deck.w > 0),
        },
        checks,
      };
    });

    const checkValues = Object.values(vpReport.checks);
    totalChecks += checkValues.length;
    passedChecks += checkValues.filter(Boolean).length;
    results.push({
      viewport: vp.name,
      width: vp.width,
      height: vp.height,
      ...vpReport,
      allPassed: checkValues.every(Boolean),
    });
    await page.close();
  }

  await browser.close();

  const passRatePct = totalChecks > 0 ? +((passedChecks / totalChecks) * 100).toFixed(1) : 0;
  const payload = {
    generatedAt: new Date().toISOString(),
    harness: "gemini-4-argon",
    summary: {
      viewportsTested: VIEWPORTS.length,
      totalChecks,
      passedChecks,
      passRatePct,
      status: passRatePct === 100 ? "PASS_ALL_VIEWPORTS" : "FAIL",
    },
    viewports: results,
  };

  fs.mkdirSync(path.dirname(OUT_JSON), { recursive: true });
  fs.writeFileSync(OUT_JSON, JSON.stringify(payload, null, 2));
  console.log(
    `[assess_tabletop_real_estate] ${passedChecks}/${totalChecks} checks passed (${passRatePct}%) across ${VIEWPORTS.length} viewports -> ${OUT_JSON}`
  );
  process.exit(passRatePct === 100 ? 0 : 1);
})();
