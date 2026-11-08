// T5: Accessibility basics — keyboard-only play, tab order & focus visibility, Enter hijack, color-only
// ownership (grayscale + CVD emulation screenshots, computed-style diff), contrast ratios, small fonts,
// prefers-reduced-motion.
const L = require("./lib");
const S = (n) => L.path.join(L.SCREENS, n);
const empties = (g) => { const e = []; g.forEach((row, r) => row.forEach((v, c) => { if (!v) e.push([r, c]); })); return e; };

(async () => {
  const browser = await L.launch();
  const R = {};

  // 1. Keyboard-only full game (no mouse events at all)
  {
    const { page, context } = await L.openGame(browser);
    let focus = 4; // state.focusedSlotIndex initial value (line 1359); tracked from our own key presses
    const turns = [];
    let guard = 0;
    while (guard++ < 8) {
      await L.waitPlayerTurn(page, 8000);
      const s = await L.snap(page);
      if (s.gameOver) break;
      const mv = await L.greedyMove(page);
      await page.keyboard.press(String(mv.idx + 1));
      let fr = Math.floor(focus / 3), fc = focus % 3;
      while (fr < mv.r) { await page.keyboard.press("ArrowDown"); fr++; }
      while (fr > mv.r) { await page.keyboard.press("ArrowUp"); fr--; }
      while (fc < mv.c) { await page.keyboard.press("ArrowRight"); fc++; }
      while (fc > mv.c) { await page.keyboard.press("ArrowLeft"); fc--; }
      focus = fr * 3 + fc;
      if (guard === 1) await page.screenshot({ path: S("t5_keyboard_focus_before_enter.png") });
      await page.keyboard.press("Enter");
      await page.waitForTimeout(250);
      const s2 = await L.snap(page);
      turns.push({ card: mv.cid, tile: [mv.r, mv.c], placed: s2.grid[mv.r][mv.c] === "p:" + mv.cid });
      await page.waitForFunction(() => state.isPlayerTurn || state.gameOver, null, { timeout: 5000 });
    }
    await page.waitForFunction(() => getComputedStyle(document.getElementById("result-modal")).display !== "none", null, { timeout: 4000 }).catch(() => {});
    await page.waitForTimeout(300);
    const end = await L.snap(page);
    // reach "Next Stage" with Tab only
    const tabStops = [];
    let reached = -1;
    for (let i = 1; i <= 15; i++) {
      await page.keyboard.press("Tab");
      const a = await page.evaluate(() => { const e = document.activeElement; return { tag: e.tagName, text: (e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40), id: e.id, inModal: !!e.closest("#result-modal") }; });
      tabStops.push(a);
      if (/Next Stage/.test(a.text)) { reached = i; break; }
    }
    await page.screenshot({ path: S("t5_keyboard_modal_focus.png") });
    if (reached > 0) await page.keyboard.press("Enter");
    await page.waitForTimeout(500);
    const nxt = await L.snap(page);
    R.keyboardOnlyGame = {
      turns, allPlacedByKeyboard: turns.every((t) => t.placed), gameCompleted: end.gameOver, modalTitle: end.modalTitle,
      tabPressesToReachNextStage: reached, tabStopsFromBodyInModal: tabStops, modalAutoFocused: false,
      nextStageLoadedByKeyboard: nxt.stage === 1 && !nxt.modal,
      notes: "Keys: 1-5 select hand card, arrows/WASD move board focus, Enter/Space place, R reroll, P pulse (handleHarnessKeyDown L1409-1445). No key for column-die nudge; Tactical Slide via Enter on own card then Enter on adjacent tile.",
    };
    await context.close();
  }

  // 2. Tab order + focus visibility from a fresh load; nudge reachability
  {
    const { page, context } = await L.openGame(browser);
    const stops = [];
    for (let i = 0; i < 14; i++) {
      await page.keyboard.press("Tab");
      stops.push(await page.evaluate(() => {
        const e = document.activeElement; const cs = getComputedStyle(e);
        return { tag: e.tagName, text: (e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 36), outlineStyle: cs.outlineStyle, outlineWidth: cs.outlineWidth, outlineColor: cs.outlineColor, focusVisible: e.matches(":focus-visible"), boxShadow: cs.boxShadow.slice(0, 60) };
      }));
      if (i === 2) await page.screenshot({ path: S("t5_tab_focus_stop3.png") });
    }
    const reach = await page.evaluate(() => ({
      focusableDiceRows: [...document.querySelectorAll(".col-die-row")].filter((e) => e.tabIndex >= 0).length,
      focusableHandCards: [...document.querySelectorAll(".hand-card-wrap")].filter((e) => e.tabIndex >= 0).length,
      focusableSlots: [...document.querySelectorAll(".board-slot")].filter((e) => e.tabIndex >= 0).length,
      ariaLiveRegions: document.querySelectorAll("[aria-live]").length,
      rolesOnBoard: document.querySelectorAll("#grid-3x3 [role]").length,
      modalRoleDialog: !!document.querySelector("#result-modal[role=dialog], #result-modal [role=dialog]"),
      imgAltSample: [...document.querySelectorAll("#grid-3x3 img, #hand-bar img")].slice(0, 3).map((i) => i.alt),
      htmlLang: document.documentElement.lang || null,
    }));
    const uniq = []; stops.forEach((s) => { if (!uniq.find((u) => u.tag === s.tag && u.text === s.text)) uniq.push(s); });
    R.tabOrder = { stops: uniq, ...reach, stopsWithVisibleOutline: uniq.filter((s) => s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0).length, totalStops: uniq.length };
    await context.close();
  }

  // 3. Board keyboard focus indicator on an occupied tile; Enter hijack on focused header button; arrows on <select>
  {
    const { page, context } = await L.openGame(browser);
    const grid = page.locator("#board-3d-slab");
    // focus starts at (1,1). Move to (0,1) (boss card) and compare screenshots before/after
    await page.keyboard.press("ArrowRight"); await page.keyboard.press("ArrowLeft"); // stay at (1,1), now hoveredSlot set
    await page.waitForTimeout(250);
    await grid.screenshot({ path: S("t5_focus_at_1_1_empty.png") });
    await page.keyboard.press("ArrowUp");
    await page.waitForTimeout(250);
    await grid.screenshot({ path: S("t5_focus_at_0_1_occupied.png") });
    await page.keyboard.press("ArrowLeft");
    await page.waitForTimeout(250);
    await grid.screenshot({ path: S("t5_focus_at_0_0_empty.png") });
    const focusClasses = await page.evaluate(() => [...document.querySelectorAll("#grid-3x3 .board-slot")].map((s) => s.className));
    R.boardFocusIndicator = { note: "pixel diff of these screenshots computed in a11y_analyze.py", slotClassesAfterNav: focusClasses, hasDedicatedFocusClass: focusClasses.some((c) => /focus/.test(c)) };

    // Enter on a Tab-focused "Reset" button
    await page.evaluate(() => startStage(0));
    await page.waitForTimeout(300);
    const s0 = await L.snap(page);
    await page.focus("header button:has-text('Reset')");
    await page.keyboard.press("Enter");
    await page.waitForTimeout(300);
    const s1 = await L.snap(page);
    R.enterOnFocusedResetButton = { activeElement: "Reset button", cardPlacedInstead: s0.hand.length - s1.hand.length === 1, handBefore: s0.hand, handAfter: s1.hand, pass: s1.hand.length === 5 && JSON.stringify(s1.hand) !== JSON.stringify(s0.hand) };
    await page.waitForTimeout(1200);
    // Space on focused "Roll All" button
    await page.evaluate(() => startStage(0));
    await page.waitForTimeout(300);
    const s2 = await L.snap(page);
    await page.focus("button:has-text('Roll All')");
    await page.keyboard.press(" ");
    await page.waitForTimeout(300);
    const s3 = await L.snap(page);
    R.spaceOnFocusedRerollButton = { rerollsBefore: s2.rerolls, rerollsAfter: s3.rerolls, cardPlaced: s2.hand.length - s3.hand.length === 1, pass: s3.rerolls === s2.rerolls - 1 && s3.hand.length === s2.hand.length };
    await page.waitForTimeout(1200);
    // Arrow keys while the stage <select> has focus
    await page.evaluate(() => startStage(0));
    await page.waitForTimeout(300);
    await page.focus("#stage-select");
    const f0 = await page.evaluate(() => state.focusedSlotIndex);
    await page.keyboard.press("ArrowDown");
    await page.waitForTimeout(300);
    R.arrowOnFocusedStageSelect = { stageAfter: await page.evaluate(() => state.stageIndex), selectValue: await page.$eval("#stage-select", (e) => e.value), boardFocusMoved: (await page.evaluate(() => state.focusedSlotIndex)) !== f0 };
    await context.close();
  }

  // 4. Color-only ownership: mid-game screenshot (normal, grayscale via CSS filter on a clone screenshot is not allowed -> use CDP vision emulation)
  {
    const { page, context } = await L.openGame(browser);
    // play one turn so both colours are present plus a capture if possible
    const mv = await L.greedyMove(page);
    await L.dragHandToSlot(page, mv.idx, mv.r, mv.c, { after: 300 });
    await L.waitPlayerTurn(page);
    const mv2 = await L.greedyMove(page);
    await L.dragHandToSlot(page, mv2.idx, mv2.r, mv2.c, { after: 300 });
    await L.waitPlayerTurn(page);
    await page.mouse.move(3, 790);
    await page.waitForTimeout(500);
    const cdp = await context.newCDPSession(page);
    const shots = {};
    for (const t of ["none", "achromatopsia", "protanopia", "deuteranopia", "tritanopia"]) {
      await cdp.send("Emulation.setEmulatedVisionDeficiency", { type: t });
      await page.waitForTimeout(200);
      const p = S(`t5_cvd_${t}.png`);
      await page.locator("#board-3d-slab").screenshot({ path: p });
      shots[t] = p;
    }
    await cdp.send("Emulation.setEmulatedVisionDeficiency", { type: "none" });
    const owners = await page.evaluate(() => {
      const p = document.querySelector("#grid-3x3 .card-3d-unit.owner-player");
      const a = document.querySelector("#grid-3x3 .card-3d-unit.owner-ai");
      if (!p || !a) return null;
      const props = ["borderTopColor", "borderTopStyle", "borderTopWidth", "boxShadow", "opacity", "filter", "borderRadius", "outlineStyle"];
      const diff = {};
      const cp = getComputedStyle(p), ca = getComputedStyle(a);
      props.forEach((k) => { if (cp[k] !== ca[k]) diff[k] = [cp[k], ca[k]]; });
      const ep = getComputedStyle(p.querySelector(".edge-num")), ea = getComputedStyle(a.querySelector(".edge-num"));
      ["borderTopColor", "color", "fontWeight", "borderTopStyle"].forEach((k) => { if (ep[k] !== ea[k]) diff["edge." + k] = [ep[k], ea[k]]; });
      const txt = (el) => el.innerText.replace(/\d/g, "").replace(/\s+/g, " ").trim();
      const rect = (el) => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
      const slab = document.querySelector("#board-3d-slab").getBoundingClientRect();
      return { differingProps: diff, playerTextNoDigits: txt(p), aiTextNoDigits: txt(a), playerRect: rect(p), aiRect: rect(a), slabOrigin: [slab.x, slab.y], dpr: devicePixelRatio, hasNonColorOwnerCue: false };
    });
    R.colorOnlyOwnership = { screenshots: shots, owners };
    await context.close();
  }

  // 5. Contrast ratios for key labels (computed-style compositing over ancestors) + 6. small fonts
  {
    const { page, context } = await L.openGame(browser);
    // hover an empty tile so preview/flip tags exist; select state is default
    const res = await page.evaluate(() => {
      const parse = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
      const over = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
      const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
      const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
      const bgOf = (el) => {
        const layers = []; let approx = false; let e = el;
        while (e) {
          const cs = getComputedStyle(e);
          const c = parse(cs.backgroundColor);
          if (cs.backgroundImage && cs.backgroundImage !== "none") { approx = true; const m = cs.backgroundImage.match(/(#[0-9a-f]{6}|rgba?\([^)]+\))/i); if (m) { const col = m[1].startsWith("#") ? { r: parseInt(m[1].slice(1, 3), 16), g: parseInt(m[1].slice(3, 5), 16), b: parseInt(m[1].slice(5, 7), 16), a: 1 } : parse(m[1]); if (col) layers.push(col); if (col && col.a >= 1) break; } }
          if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
          e = e.parentElement;
        }
        let base = { r: 4, g: 7, b: 15, a: 1 }; // body gradient dark stop rgba(4,7,15,.97)
        for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
        return { bg: base, approx };
      };
      const items = {
        "brand badge": ".brand-badge", "harness pill": ".brand span:nth-child(3)", "YOU score": ".score-side:first-child", "VS": ".scoreboard > span", "BOSS score": ".score-side:last-child",
        "box-title (Hero Hand)": ".box-title span", "hand-count badge (gold)": "#hand-count-badge", "telegraph HUD desc": "#telegraph-hud-desc", "telegraph HUD badge": "#telegraph-hud-badge",
        "col header (not boosted)": ".col-header-pill:not(.boosted)", "col header (boosted)": ".col-header-pill.boosted", "OPEN tile label": "#grid-3x3 .board-slot:not(.occupied) > div",
        "edge number (AI card)": "#grid-3x3 .owner-ai .edge-num", "name ribbon (board)": "#grid-3x3 .slot-name-ribbon", "name ribbon (hand)": "#hand-bar .slot-name-ribbon", "edge number (hand)": "#hand-bar .edge-num",
        "slide card title": ".tactical-slide-card > div:nth-child(1)", "slide card type": ".tactical-slide-card > div:nth-child(2)", "slide status": ".tactical-slide-card > div:nth-child(3)",
        "dice help text": "main > aside:nth-of-type(2) > div > div:nth-child(2)", "die row label": ".col-die-row > div > div:first-child", "die row hint (uncharged)": ".col-die-row:not(.charged) > div > div:nth-child(2)", "die row hint (charged)": ".col-die-row.charged > div > div:nth-child(2)",
        "NUDGES label": "main > aside:nth-of-type(2) .box-title span:nth-child(2)", "turn badge": "#turn-badge", "boss name": "#boss-name", "boss telegraph label": "#boss-telegraph-label", "'Counters after each move.'": ".boss-profile > div > div:nth-child(3)",
        "last-move banner": "#last-move-banner", "Reset button": "header button:last-child", "Roll dice button": "main > aside:nth-of-type(2) button",
      };
      const out = [];
      for (const [name, sel] of Object.entries(items)) {
        const el = document.querySelector(sel);
        if (!el) { out.push({ name, missing: sel }); continue; }
        const cs = getComputedStyle(el);
        const fg = parse(cs.color);
        const { bg, approx } = bgOf(el);
        const fgc = fg.a < 1 ? over(fg, bg) : fg;
        const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight, 10);
        const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
        const cr = ratio(fgc, bg);
        out.push({ name, text: el.textContent.trim().replace(/\s+/g, " ").slice(0, 40), color: cs.color, bg: `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})`, bgApprox: approx, fontSize: fs, fontWeight: fw, ratio: +cr.toFixed(2), AA: cr >= (large ? 3 : 4.5) });
      }
      // small fonts census
      const small = {}; let textEls = 0;
      document.querySelectorAll("body *").forEach((el) => {
        if (el.closest("svg") || el.closest("#result-modal")) return;
        const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
        if (!own) return;
        const cs = getComputedStyle(el);
        if (cs.display === "none") return;
        textEls++;
        const fs = parseFloat(cs.fontSize);
        if (fs < 11) { const k = fs.toFixed(1) + "px"; small[k] = small[k] || { count: 0, samples: [] }; small[k].count++; if (small[k].samples.length < 6) small[k].samples.push(el.textContent.trim().replace(/\s+/g, " ").slice(0, 30)); }
      });
      return { contrast: out, smallFonts: small, textElements: textEls, smallFontElements: Object.values(small).reduce((a, b) => a + b.count, 0) };
    });
    R.contrast = res.contrast;
    R.smallFonts = { census: res.smallFonts, textElements: res.textElements, under11px: res.smallFontElements };
    await context.close();
  }

  // 7. prefers-reduced-motion
  {
    const out = {};
    for (const rm of ["no-preference", "reduce"]) {
      const { page, context } = await L.openGame(browser, { reducedMotion: rm });
      const before = await page.evaluate(() => ({ anims: document.getAnimations().length, infinite: document.getAnimations().filter((a) => a.effect && a.effect.getTiming().iterations === Infinity).length, mq: matchMedia("(prefers-reduced-motion: reduce)").matches }));
      const mv = await L.greedyMove(page);
      // sample the screen-shake transform every ~25 ms for 600 ms after the drop commits
      await page.evaluate(() => { window.__shake = []; const t0 = performance.now(); const f = () => { const m = (document.getElementById("arena-viewport").style.transform || "").match(/-?[\d.]+px/g); window.__shake.push(m ? Math.max(...m.map((v) => Math.abs(parseFloat(v)))) : 0); if (performance.now() - t0 < 1400) requestAnimationFrame(f); }; requestAnimationFrame(f); });
      await L.dragHandToSlot(page, mv.idx, mv.r, mv.c, { after: 900 });
      const shake = await page.evaluate(() => ({ maxShakeOffsetPx: Math.max(...window.__shake), framesWithShake: window.__shake.filter((v) => v > 0).length }));
      const after = await page.evaluate(() => ({ infiniteAfterPlacement: document.getAnimations().filter((a) => a.effect && a.effect.getTiming().iterations === Infinity && a.playState === "running").length }));
      out[rm] = { ...before, ...after, capturesThisMove: mv.caps, shakeDuringPlacement: shake };
      await context.close();
    }
    out.cssHasReducedMotionMedia = false; // grep of the HTML: no 'prefers-reduced-motion' occurrence (see REPORT)
    out.pass = out.reduce.infinite === 0 && out.reduce.shakeDuringPlacement.maxShakeOffsetPx === 0;
    R.reducedMotion = out;
  }

  L.writeJSON("t5_a11y.json", R);
  console.log(JSON.stringify(R, null, 1).slice(0, 12000));
  await browser.close();
})().catch((e) => { console.error("FAILED:", e); process.exit(1); });
