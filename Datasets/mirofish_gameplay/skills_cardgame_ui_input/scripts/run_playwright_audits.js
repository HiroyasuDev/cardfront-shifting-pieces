#!/usr/bin/env node
/**
 * run_playwright_audits.js
 * Executes live headless Chromium Playwright probes across all 4 gamedev-skills audit tracks
 * against `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`.
 * Saves screenshots and raw JSON telemetry into each track's folder.
 */

"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");

const ROOT = "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine";
const URL = "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const CHROMIUM_BIN = "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROMIUM_BIN
  });

  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    await page.goto(URL, { waitUntil: "networkidle" });
    await page.waitForTimeout(400);

    // 1. Capture native 1280x800 screenshot + hover telegraph screenshot for skills_art_direction & skills_cardgame_ui_input
    const artScreensDir = path.join(ROOT, "Datasets/mirofish_gameplay/skills_art_direction/screens");
    const uiScreensDir = path.join(ROOT, "Datasets/mirofish_gameplay/skills_cardgame_ui_input/screens");
    const feelRawDir = path.join(ROOT, "Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/raw");
    const uiRawDir = path.join(ROOT, "Datasets/mirofish_gameplay/skills_cardgame_ui_input/raw");
    fs.mkdirSync(artScreensDir, { recursive: true });
    fs.mkdirSync(uiScreensDir, { recursive: true });
    fs.mkdirSync(feelRawDir, { recursive: true });
    fs.mkdirSync(uiRawDir, { recursive: true });

    await page.screenshot({ path: path.join(artScreensDir, "native_1280x800_stage1.png") });
    await page.screenshot({ path: path.join(uiScreensDir, "viewport_1280x800.png") });

    // Hover slot (1,1) to trigger clash telegraph overlay
    await page.hover('#grid-3x3 .board-slot[data-r="1"][data-c="1"]');
    await page.waitForTimeout(250);
    await page.screenshot({ path: path.join(artScreensDir, "native_1280x800_hover_telegraph.png") });

    // 2. Measure UI/UX metrics across 4 viewports: 1280x800, 1920x1080, 2560x1080 (21:9), 375x667 (mobile portrait)
    const viewports = [
      { name: "1280x800_laptop", width: 1280, height: 800 },
      { name: "1920x1080_desktop", width: 1920, height: 1080 },
      { name: "2560x1080_ultrawide", width: 2560, height: 1080 },
      { name: "375x667_mobile", width: 375, height: 667 }
    ];

    const viewportMetrics = [];
    for (const vp of viewports) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.waitForTimeout(200);
      await page.screenshot({ path: path.join(uiScreensDir, `viewport_${vp.name}.png`) });

      const m = await page.evaluate(() => {
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const checkEl = (sel) => {
          const el = document.querySelector(sel);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {
            left: Math.round(r.left),
            top: Math.round(r.top),
            right: Math.round(r.right),
            bottom: Math.round(r.bottom),
            width: Math.round(r.width),
            height: Math.round(r.height),
            clippedHoriz: r.left < 0 || r.right > vw,
            clippedVert: r.top < 0 || r.bottom > vh,
            overflowX: el.scrollWidth > el.clientWidth + 2,
            overflowY: el.scrollHeight > el.clientHeight + 2
          };
        };

        // Font size census across visible text elements
        const allEls = Array.from(document.querySelectorAll("header *, main *, .modal-box *"));
        const fontSizes = [];
        for (const el of allEls) {
          if (el.children.length === 0 && (el.textContent || "").trim().length > 0) {
            const cs = window.getComputedStyle(el);
            const px = parseFloat(cs.fontSize);
            if (!isNaN(px) && px > 0) {
              fontSizes.push({ tag: el.tagName, className: el.className, text: el.textContent.trim().slice(0, 24), px });
            }
          }
        }
        const minFontPx = fontSizes.length ? Math.min(...fontSizes.map(f => f.px)) : 0;
        const maxFontPx = fontSizes.length ? Math.max(...fontSizes.map(f => f.px)) : 0;
        const below18PxCount = fontSizes.filter(f => f.px < 18).length;
        const below12PxCount = fontSizes.filter(f => f.px < 12).length;

        return {
          viewport: { vw, vh },
          header: checkEl("header"),
          leftPanel: checkEl("main > aside:first-of-type"),
          centerZone: checkEl(".center-zone"),
          boardSlab: checkEl("#board-3d-slab"),
          rightPanel: checkEl("main > aside:last-of-type"),
          fontCensus: {
            totalLeafTextNodes: fontSizes.length,
            minFontPx,
            maxFontPx,
            below18PxCount,
            below12PxCount,
            samplesBelow10Px: fontSizes.filter(f => f.px < 10).slice(0, 8)
          }
        };
      });
      viewportMetrics.push({ name: vp.name, ...m });
    }

    // Restore 1280x800 for functional & performance probes
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.waitForTimeout(200);

    // 3. Card-game, Input, Feel, Audio, Camera, Performance, and AI/Save probes
    const deepProbes = await page.evaluate(async () => {
      const sleep = (ms) => new Promise(r => setTimeout(r, ms));
      startStage(0);
      await sleep(100);

      // Probe A: Single-Zone Invariant & Card Conservation
      const handIds = [...state.hand];
      const boardIds = state.grid.flat().filter(c => c.cardId).map(c => c.cardId);
      const aiPoolIds = [...state.aiPool];
      const allActive = [...handIds, ...boardIds, ...aiPoolIds];
      const uniqueActive = new Set(allActive);
      const singleZoneValidInitial =
        handIds.every(id => !boardIds.includes(id) && !aiPoolIds.includes(id)) &&
        boardIds.every(id => !aiPoolIds.includes(id));

      // Probe B: DOM Churn & Performance during 20 consecutive renderAll() calls (simulating mouse hover across sockets)
      let mutationsCount = 0;
      let addedNodesCount = 0;
      let removedNodesCount = 0;
      const obs = new MutationObserver((list) => {
        for (const m of list) {
          mutationsCount++;
          addedNodesCount += m.addedNodes.length;
          removedNodesCount += m.removedNodes.length;
        }
      });
      obs.observe(document.querySelector("main"), { childList: true, subtree: true });
      const t0 = performance.now();
      for (let i = 0; i < 20; i++) {
        state.hoveredSlot = { r: i % 3, c: (i >> 1) % 3 };
        renderAll();
      }
      const render20Ms = performance.now() - t0;
      await Promise.resolve();
      obs.disconnect();

      // Probe C: Measure 60-frame rAF frame-time budget while trauma shake + 16 SVG animations run
      addTrauma(0.65);
      const frameDeltas = [];
      let lastF = performance.now();
      for (let f = 0; f < 60; f++) {
        await new Promise(r => requestAnimationFrame((now) => {
          frameDeltas.push(now - lastF);
          lastF = now;
          r();
        }));
      }
      frameDeltas.shift(); // drop first partial delta
      const meanFrameMs = frameDeltas.reduce((a, b) => a + b, 0) / frameDeltas.length;
      const p95FrameMs = [...frameDeltas].sort((a, b) => a - b)[Math.floor(frameDeltas.length * 0.95)];
      const maxFrameMs = Math.max(...frameDeltas);

      // Probe D: Game-Feel trauma decay & hit-stop verification
      state.trauma = 0;
      addTrauma(0.5);
      const traumaAfterAdd = state.trauma;
      const expectedQuadraticShake = traumaAfterAdd * traumaAfterAdd;
      triggerHitStop(80);
      const hitStopImmediate = state.hitStopActive;
      const vpFilterDuringHitStop = document.getElementById("arena-viewport").style.filter;
      await sleep(110);
      const hitStopAfter110ms = state.hitStopActive;

      // Probe E: Camera angle presets & parallax transform
      setBoardCamera("14,0");
      const cam14Transform = document.getElementById("board-3d-slab").style.transform;
      setBoardCamera("5,0");

      // Probe F: Keyboard navigation (1..5 hand select + WASD/Arrow focus)
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "3" }));
      const selectedAfterKey3 = state.selectedHandIdx;
      const focusBefore = state.focusedSlotIndex;
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowUp" }));
      const focusAfterUp = state.focusedSlotIndex;

      // Probe G: Check save/persistence usage in localStorage / sessionStorage / IndexedDB
      const localStorageKeys = Object.keys(window.localStorage || {});
      const sessionStorageKeys = Object.keys(window.sessionStorage || {});

      return {
        cardGame: {
          handCount: handIds.length,
          boardCount: boardIds.length,
          aiPoolCount: aiPoolIds.length,
          totalInPlay: allActive.length,
          uniqueInPlay: uniqueActive.size,
          singleZoneDisjoint: singleZoneValidInitial,
          allImagesComplete600x800: Array.from(document.querySelectorAll(".slot-art")).every(
            img => img.complete && img.naturalWidth === 600 && img.naturalHeight === 800
          )
        },
        domChurnAndPerf: {
          render20CallsTotalMs: Number(render20Ms.toFixed(3)),
          avgSingleRenderAllMs: Number((render20Ms / 20).toFixed(3)),
          mutationsPer20Renders: mutationsCount,
          addedNodesPer20Renders: addedNodesCount,
          removedNodesPer20Renders: removedNodesCount,
          addedNodesPerSingleRender: Math.round(addedNodesCount / 20),
          activeSvgAnimationsCount: document.querySelectorAll(".card-telegraph-fx").length,
          meanFrameMs: Number(meanFrameMs.toFixed(2)),
          p95FrameMs: Number(p95FrameMs.toFixed(2)),
          maxFrameMs: Number(maxFrameMs.toFixed(2))
        },
        gameFeel: {
          traumaAfterAdd05: traumaAfterAdd,
          expectedQuadraticShake,
          hitStopImmediate,
          vpFilterDuringHitStop,
          hitStopAfter110ms
        },
        cameraAndInput: {
          cam14Transform,
          selectedAfterKey3,
          focusBefore,
          focusAfterUp,
          dragThresholdPx: typeof DRAG_THRESHOLD_PX !== "undefined" ? DRAG_THRESHOLD_PX : null
        },
        persistence: {
          localStorageKeysCount: localStorageKeys.length,
          sessionStorageKeysCount: sessionStorageKeys.length
        }
      };
    });

    const summary = {
      timestamp: new Date().toISOString(),
      url: URL,
      viewportMetrics,
      deepProbes
    };

    fs.writeFileSync(path.join(uiRawDir, "playwright_ui_input_audit.json"), JSON.stringify(summary, null, 2));
    fs.writeFileSync(path.join(feelRawDir, "playwright_feel_perf_audit.json"), JSON.stringify(summary, null, 2));
    console.log("Saved Playwright audit telemetry:", JSON.stringify(deepProbes, null, 2));
    for (const vm of viewportMetrics) {
      console.log(
        `Viewport ${vm.name}: boardClippedH=${vm.boardSlab.clippedHoriz}, boardClippedV=${vm.boardSlab.clippedVert}, ` +
        `rightPanelClippedH=${vm.rightPanel.clippedHoriz}, minFontPx=${vm.fontCensus.minFontPx}px, below18px=${vm.fontCensus.below18PxCount}/${vm.fontCensus.totalLeafTextNodes}`
      );
    }
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
