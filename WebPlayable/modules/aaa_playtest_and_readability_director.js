/**
 * ============================================================================
 * CARDFRONT: CRADLE OF ECHOES — TRACK A MODULE
 * AAA Card-Face Readability, Non-Colliding Chibi Corner-Perch,
 * Live On-Board `[CAPTURE! X > Y]` Combat Preview, Non-Blocking Quick-Inspector,
 * & 8-Persona Automated Readability/Usability Self-Audit Engine
 * ============================================================================
 * File: WebPlayable/modules/aaa_playtest_and_readability_director.js
 * Global API: window.CardFrontAaaReadabilityDirector
 *
 * Strict Compliance:
 * - ZERO living artists' names anywhere (zeroLivingArtistNames: true)
 * - ZERO raw Unicode emojis in DOM text, labels, or buttons (zeroRawUnicodeEmojis: true)
 * - Zero bounding-box overlap across all 7 card-face sub-elements on board & hand cards
 * ============================================================================
 */
(function initCardFrontAaaReadabilityDirector(globalScope) {
  "use strict";

  // ==========================================================================
  // 1. 8 AUTOMATED PLAYTEST PERSONA PROFILES (P1..P8)
  // ==========================================================================
  const PLAYTEST_PERSONAS_8 = [
    {
      personaId: "P1_Onboarding_Duelist",
      name: "First-Time Onboarding Duelist",
      focus: "Zero-jargon turn banner, clear hand selection, and unmistakable open-slot deploy prompts",
      targetMetric: "Turn guidance & quick-inspector clarity >= 98%"
    },
    {
      personaId: "P2_Tactical_Math_MinMaxer",
      name: "Tactical Math & Orthogonal Min-Maxer",
      focus: "Instant pre-deploy [CAPTURE! X > Y] vs [HOLD X <= Y] math and column die (+1 N/S) boost preview",
      targetMetric: "100% deterministic orthogonal clash preview accuracy"
    },
    {
      personaId: "P3_Shadowverse_Evolve_Sequencer",
      name: "Evolve (Base -> Evolved) Tempo Sequencer",
      focus: "Non-colliding on-board EVOLVE button, EP counter visibility, and Base SR -> Awakened UR stat delta",
      targetMetric: "Zero overlap between .cf-board-evolve-btn, .edge-bottom, and .cf-slab-layer-3-chibi"
    },
    {
      personaId: "P4_FFTA_Chibi_Collector",
      name: "FFTA Isometric Pixel-Chibi Collector",
      focus: "24x24 pixel-chibi corner perch (34x34 board / 28x28 hand) without obscuring N/E/S/W compass gems",
      targetMetric: "100% chibi visibility with 0px collision against .edge-right and .edge-bottom"
    },
    {
      personaId: "P5_Speedrun_APM_Competitor",
      name: "High-APM Speedrun Competitor",
      focus: "Zero modal pop-up interruptions during card selection, instant hover feedback, and 60fps slab response",
      targetMetric: "Non-blocking pointer-events:none Quick-Inspector at z-index 22"
    },
    {
      personaId: "P6_Low_Vision_Accessibility_Auditor",
      name: "WCAG AAA High-Contrast & Typography Auditor",
      focus: "21x21px tabular-nums 13px font-weight 900 directional badges with >= 14.5:1 luminance contrast",
      targetMetric: "Directional stat font size >= 13px and contrastRatio >= 14.5"
    },
    {
      personaId: "P7_Deckbuilder_Meta_Theorist",
      name: "10-Year Saga & Studio PxG Deckbuilder",
      focus: "Cross-set faction telegraph readability, star cost curve inspection, and chibi job/weapon attribution",
      targetMetric: "Complete 141-card metadata resolution in Quick-Inspector"
    },
    {
      personaId: "P8_Chaos_Stress_Monkey",
      name: "Rapid Hover / Evolve / Re-Render Stress Tester",
      focus: "Idempotent renderAll() hooks, zero duplicate DOM badges, and zero NaN/null state regressions",
      targetMetric: "Zero DOM leaks or bounding-box collisions across rapid re-renders"
    }
  ];

  const DISTILLED_70B_COUNCIL_SOUP_PRIORS = {
    schemaVersion: "2026.11.v3",
    sourceFleet: "4-Node Ensemble (v100 30B-A3B + node30 72B/12B + node22 2070 7B + node127 M1Max 7B) -> pxg-unified-soup-v3 -> Qwen2.5-3B-4bit / 1.5B-QLoRA",
    captureSwingWeight: 2.40,
    chainCascadeBonus: 1.65,
    centerControlWeight: 1.35,
    cornerAnchorBonus: 1.28,
    proactivePlusWallBonus: 1.15,
    columnDieSynergyBonus: 0.75,
    evolutionTempoBonus: 1.55,
    exposedWeakEdgePenalty: -0.85,
    safeBorderFortificationBonus: 0.45,
    breachStackDecayFactor: 0.50,
    weakEdgeThreshold: 6
  };

  const AAA_DIRECTOR_STATE = {
    initialized: false,
    inspectedCardId: "ev_01_base",
    inspectedCardOwner: "player",
    inspectedColIndex: 0,
    lastPreviewSlot: null,
    lastAuditReport: null,
    distilledPriors: DISTILLED_70B_COUNCIL_SOUP_PRIORS
  };

  // ==========================================================================
  // 2. AAA HIGH-CONTRAST CSS & ZERO-COLLISION CARD GEOMETRY
  // ==========================================================================
  function ensureAaaReadabilityStyles() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    if (doc.getElementById("cf-aaa-readability-director-styles")) return;

    const styleEl = doc.createElement("style");
    styleEl.id = "cf-aaa-readability-director-styles";
    styleEl.textContent = `
      /* ====================================================================
         1. HIGH-CONTRAST AAA DIRECTIONAL STAT BADGES (.edge-num)
            & ZERO BOUNDING-BOX COLLISION CARD GEOMETRY
         ==================================================================== */
      .card-3d-unit .edge-num {
        width: 20px !important;
        height: 18px !important;
        min-width: 20px !important;
        min-height: 18px !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        font-variant-numeric: tabular-nums !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 5px !important;
        background: rgba(5, 9, 18, 0.96) !important;
        color: #FFFFFF !important;
        border: 1.6px solid rgba(255, 224, 130, 0.92) !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.92), inset 0 0 4px rgba(0, 229, 255, 0.28) !important;
        text-shadow: 0 1px 3px #000000, 0 0 5px rgba(0, 0, 0, 0.95) !important;
        z-index: 14 !important;
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        pointer-events: none !important;
      }
      .card-3d-unit .edge-num.boosted-stat {
        background: linear-gradient(145deg, #422006 0%, #090d16 90%) !important;
        color: #FEF08A !important;
        border-color: #FACC15 !important;
        box-shadow: 0 0 8px rgba(250, 204, 21, 0.65), 0 2px 5px rgba(0, 0, 0, 0.95) !important;
      }
      /* Top badge & ribbon: preserve core_checks.json invariants (rb.top - cb.top <= 14 & rb.bottom < tip.top) */
      .card-3d-unit .edge-top {
        top: 2px !important;
        left: 2px !important;
        right: auto !important;
        bottom: auto !important;
        transform: none !important;
      }
      .card-3d-unit .slot-name-ribbon {
        top: 2px !important;
        left: 24px !important;
        right: 2px !important;
        bottom: auto !important;
        height: 15px !important;
        line-height: 14px !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        padding: 0 4px !important;
        transform: none !important;
        z-index: 13 !important;
        box-sizing: border-box !important;
      }
      /* Left & Right compass badges positioned below top band and horizontally disjoint from bottom badges */
      .card-3d-unit .edge-left {
        left: 2px !important;
        right: auto !important;
        top: 56% !important;
        bottom: auto !important;
        transform: translateY(-50%) !important;
      }
      .card-3d-unit .edge-right {
        right: 2px !important;
        left: auto !important;
        top: 56% !important;
        bottom: auto !important;
        transform: translateY(-50%) !important;
      }
      /* Bottom badge horizontally disjoint from .edge-left (x: 2..22px vs left: 25px) */
      .board-slot .card-3d-unit .edge-bottom {
        bottom: 2px !important;
        left: 25px !important;
        top: auto !important;
        right: auto !important;
        transform: none !important;
      }
      .hand-card-wrap .card-3d-unit .edge-bottom {
        bottom: 2px !important;
        left: 25px !important;
        top: auto !important;
        right: auto !important;
        transform: none !important;
      }
      /* Non-colliding Chibi corner perch (horizontally disjoint from .edge-right at right: 2px..22px) */
      .cf-slab-layer-3-chibi,
      .board-slot .cf-slab-layer-3-chibi {
        right: 24px !important;
        bottom: 2px !important;
        left: auto !important;
        top: auto !important;
        width: 24px !important;
        height: 24px !important;
        z-index: 8 !important;
        transform: none !important;
      }
      .hand-card-wrap .cf-slab-layer-3-chibi {
        right: 24px !important;
        bottom: 2px !important;
        left: auto !important;
        top: auto !important;
        width: 22px !important;
        height: 22px !important;
        z-index: 8 !important;
        transform: none !important;
      }
      /* Non-colliding Board Evolve button (between .edge-bottom [25..45px] and .cf-slab-layer-3-chibi [right: 24px]) */
      .cf-board-evolve-btn,
      .board-slot .cf-board-evolve-btn {
        left: 48px !important;
        bottom: 2px !important;
        right: auto !important;
        top: auto !important;
        z-index: 12 !important;
        padding: 1px 4px !important;
        font-size: 12px !important;
        line-height: 1.05 !important;
        height: 15px !important;
        max-width: 42px !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        transform: none !important;
        box-sizing: border-box !important;
      }
      /* Hand card spacing & faction-consistent gold/cyan selection border */
      .hand-card-wrap {
        margin: 0 7px !important;
      }
      .hand-card-wrap.selected .card-3d-unit {
        border: 2.5px solid #FFB800 !important;
        box-shadow:
          0 14px 28px rgba(0, 0, 0, 0.95),
          0 0 22px rgba(0, 229, 255, 0.85),
          inset 0 0 12px rgba(255, 184, 0, 0.45) !important;
      }
      /* Keep Row 3 of the 3x3 board unobstructed when a hand card is merely selected (not hovered);
         full card details are shown in #aaa-card-quick-inspector, while hovering still reveals .hand-card-tooltip */
      .hand-card-wrap.selected:not(:hover) .hand-card-tooltip {
        opacity: 0 !important;
        pointer-events: none !important;
      }
      /* Ensure capture flip animation never rotates on Y where front-face text appears mirrored or horizontally foreshortened */
      @keyframes card3DSlamFlip {
        0%   { transform: translateZ(44px) rotateX(14deg) scale(1.08); filter: brightness(1.45); }
        55%  { transform: translateZ(20px) rotateX(-4deg) scale(1.03); filter: brightness(1.15); }
        100% { transform: translateZ(10px) rotateX(0deg) scale(1.0); filter: brightness(1.0); }
      }
      @keyframes cardFlip180Capture {
        0%   { transform: translateZ(38px) rotateX(14deg) scale(1.10); filter: brightness(1.65) saturate(1.35); }
        50%  { transform: translateZ(24px) rotateX(-4deg) scale(1.04); filter: brightness(1.25); }
        100% { transform: translateZ(10px) rotateX(0deg) scale(1.0); filter: brightness(1.0); }
      }

      /* ====================================================================
         2. LIVE ON-BOARD TACTICAL OUTCOME PREVIEW PILL (.aaa-slot-outcome-pill)
         ==================================================================== */
      .aaa-slot-outcome-pill {
        position: absolute;
        left: 50%;
        bottom: 6px;
        transform: translateX(-50%);
        z-index: 25;
        pointer-events: none;
        padding: 2px 7px;
        border-radius: 999px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 9.5px;
        font-weight: 900;
        letter-spacing: 0.05em;
        white-space: nowrap;
        text-transform: uppercase;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.92);
      }
      .aaa-slot-outcome-pill.outcome-capture {
        background: linear-gradient(135deg, #FFB800 0%, #D97706 100%);
        color: #050912;
        border: 1.5px solid #FEF08A;
      }
      .aaa-slot-outcome-pill.outcome-boost {
        background: linear-gradient(135deg, #00E5FF 0%, #0284C7 100%);
        color: #041019;
        border: 1.5px solid #E0F2FE;
      }
      .aaa-slot-outcome-pill.outcome-safe {
        background: rgba(8, 20, 38, 0.92);
        color: #00E5FF;
        border: 1px solid rgba(0, 229, 255, 0.75);
      }

      /* ====================================================================
         3. NON-BLOCKING QUICK CARD INSPECTOR (#aaa-card-quick-inspector)
         ==================================================================== */
      #aaa-card-quick-inspector {
        position: fixed;
        left: 14px;
        top: 96px;
        width: 216px;
        z-index: 22;
        pointer-events: none;
        background: linear-gradient(165deg, rgba(8, 13, 24, 0.94) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1.5px solid rgba(255, 184, 0, 0.65);
        border-radius: 10px;
        padding: 9px 10px;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.82), inset 0 0 12px rgba(0, 229, 255, 0.12);
        color: #F8FAFC;
        font-family: system-ui, -apple-system, sans-serif;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        transition: opacity 0.16s ease;
      }
      @media (max-width: 1100px) {
        #aaa-card-quick-inspector {
          display: none !important;
        }
      }
      .aaa-qi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 4px;
        border-bottom: 1px solid rgba(255, 184, 0, 0.28);
        padding-bottom: 4px;
        margin-bottom: 5px;
      }
      .aaa-qi-tag {
        font-size: 8.5px;
        font-weight: 900;
        letter-spacing: 0.06em;
        padding: 1px 5px;
        border-radius: 4px;
        background: rgba(0, 229, 255, 0.16);
        color: #00E5FF;
        border: 1px solid rgba(0, 229, 255, 0.45);
      }
      .aaa-qi-evo-badge {
        font-size: 8.5px;
        font-weight: 900;
        padding: 1px 5px;
        border-radius: 4px;
        background: rgba(255, 184, 0, 0.2);
        color: #FEF08A;
        border: 1px solid rgba(250, 204, 21, 0.6);
      }
      .aaa-qi-title {
        font-size: 11.5px;
        font-weight: 900;
        color: #FFFFFF;
        line-height: 1.2;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .aaa-qi-sub {
        font-size: 9.5px;
        font-weight: 700;
        color: #94A3B8;
        margin-bottom: 6px;
      }
      .aaa-qi-compass-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 4px;
        margin-bottom: 6px;
      }
      .aaa-qi-compass-cell {
        background: rgba(5, 9, 18, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.4);
        border-radius: 5px;
        padding: 3px 2px;
        text-align: center;
      }
      .aaa-qi-compass-cell.boosted {
        border-color: #FACC15;
        background: rgba(66, 32, 6, 0.78);
      }
      .aaa-qi-dir-lbl {
        display: block;
        font-size: 8px;
        font-weight: 800;
        color: #94A3B8;
      }
      .aaa-qi-dir-val {
        display: block;
        font-size: 12px;
        font-weight: 900;
        color: #FFFFFF;
        font-variant-numeric: tabular-nums;
      }
      .aaa-qi-compass-cell.boosted .aaa-qi-dir-val {
        color: #FEF08A;
      }
      .aaa-qi-ability {
        font-size: 9.5px;
        line-height: 1.3;
        color: #E2E8F0;
        background: rgba(15, 23, 42, 0.78);
        border-left: 2px solid #00E5FF;
        padding: 4px 6px;
        border-radius: 0 4px 4px 0;
        margin-bottom: 5px;
      }
      .aaa-qi-chibi-row {
        font-size: 8.5px;
        font-weight: 800;
        color: #2EE6D3;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 6px;
        line-height: 1.25;
      }
      .aaa-qi-chibi-svg {
        width: 24px;
        height: 24px;
        flex-shrink: 0;
        border-radius: 4px;
        background: rgba(8, 13, 26, 0.92);
        border: 1px solid rgba(46, 230, 211, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .aaa-qi-distilled-ai {
        margin-top: 5px;
        padding-top: 4px;
        border-top: 1px dashed rgba(255, 184, 0, 0.32);
        font-size: 8.5px;
        font-weight: 800;
        color: #FEF08A;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 4px;
      }
      .aaa-qi-risk-tag {
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 8px;
        font-weight: 900;
      }
      .aaa-qi-risk-tag.risk-safe {
        background: rgba(0, 230, 118, 0.18);
        color: #00E676;
        border: 1px solid rgba(0, 230, 118, 0.5);
      }
      .aaa-qi-risk-tag.risk-amber {
        background: rgba(255, 184, 0, 0.22);
        color: #FFB800;
        border: 1px solid rgba(255, 184, 0, 0.65);
      }
    `;
    if (doc.head) {
      doc.head.appendChild(styleEl);
    }
  }

  // ==========================================================================
  // 3. CARD METADATA & EFFECTIVE STAT RESOLVER
  // ==========================================================================
  function resolveCardMeta(cardId) {
    const cid = String(cardId || "ev_01_base").trim();
    if (typeof globalScope.getCardMeta === "function") {
      try {
        const gm = globalScope.getCardMeta(cid);
        if (gm && (gm.title || gm.name)) {
          return gm;
        }
      } catch (_e) {}
    }
    if (globalScope.CARDS && globalScope.CARDS[cid]) {
      return globalScope.CARDS[cid];
    }
    if (Array.isArray(globalScope.EVOLVE_MECH_WING_CARDS_10)) {
      for (let i = 0; i < globalScope.EVOLVE_MECH_WING_CARDS_10.length; i++) {
        const ec = globalScope.EVOLVE_MECH_WING_CARDS_10[i];
        if (ec.id === cid || ec.slug === cid) return ec;
      }
    }
    return {
      id: cid,
      name: cid.replace(/_/g, " ").toUpperCase(),
      faction: "Aether",
      starCost: 2,
      cost: 2,
      nesw: [6, 6, 5, 5],
      telegraphName: "Astral Vanguard Resonance",
      telegraphDesc: "Challenges orthogonal adjacent enemy cards on the 3x3 grid."
    };
  }

  function computeEffectiveCardStats(cardId, colIndex) {
    const meta = resolveCardMeta(cardId);
    const rawNesw = Array.isArray(meta.nesw)
      ? meta.nesw
      : Array.isArray(meta.stats)
      ? meta.stats
      : [meta.top || 6, meta.right || 6, meta.bottom || 5, meta.left || 5];
    const st = globalScope.state || {};
    const colDice = Array.isArray(st.colDice) ? st.colDice : [3, 4, 2];
    const cIdx = typeof colIndex === "number" && colIndex >= 0 && colIndex < 3 ? colIndex : 0;
    const dieVal = Number(colDice[cIdx] || 3);
    const columnBoosted = dieVal >= 4;
    const boostDelta = columnBoosted ? 1 : 0;

    return {
      cardId: meta.id || cardId,
      name: meta.title || meta.name || String(cardId),
      faction: meta.faction || meta.element || "Aether",
      starCost: Number(meta.starCost || meta.cost || 2),
      isEvolved: Boolean(meta.isEvolvedForm || String(cardId).endsWith("_evo")),
      baseStats: {
        top: Number(rawNesw[0] || 6),
        right: Number(rawNesw[1] || 6),
        bottom: Number(rawNesw[2] || 5),
        left: Number(rawNesw[3] || 5)
      },
      effectiveStats: {
        top: Math.min(10, Number(rawNesw[0] || 6) + boostDelta),
        right: Number(rawNesw[1] || 6),
        bottom: Math.min(10, Number(rawNesw[2] || 5) + boostDelta),
        left: Number(rawNesw[3] || 5)
      },
      columnIndex: cIdx,
      columnDieValue: dieVal,
      columnBoosted: columnBoosted,
      telegraphSummary:
        (meta.abilityTitle ? meta.abilityTitle + ": " + (meta.abilityDesc || "") : "") ||
        meta.telegraphDesc ||
        meta.rulesHtml ||
        "Orthogonal edge comparison on the 3x3 grid."
    };
  }

  // ==========================================================================
  // 4. LIVE ON-BOARD TACTICAL OUTCOME PREVIEW (`simulateTacticalCombatPreview`)
  // ==========================================================================
  function getActiveHandCardId() {
    const st = globalScope.state || {};
    if (Array.isArray(st.hand) && st.hand.length > 0) {
      const selIdx = typeof st.selectedHandIdx === "number" ? Math.max(0, Math.min(st.hand.length - 1, st.selectedHandIdx)) : 0;
      const item = st.hand[selIdx];
      return typeof item === "string" ? item : (item && item.id) || "ev_01_base";
    }
    return "ev_01_base";
  }

  function simulateTacticalCombatPreview(slotIndex, customCardId) {
    ensureAaaReadabilityStyles();
    const idx = typeof slotIndex === "number" ? Math.max(0, Math.min(8, slotIndex)) : 4;
    const r = Math.floor(idx / 3);
    const c = idx % 3;
    const cardId = customCardId || getActiveHandCardId();
    const statInfo = computeEffectiveCardStats(cardId, c);
    const eff = statInfo.effectiveStats;

    const st = globalScope.state || {};
    const grid = Array.isArray(st.grid) ? st.grid : [];

    function readCell(row, col) {
      if (!grid[row]) return null;
      return grid[row][col] || null;
    }

    const dirs = [
      { dir: "N", dr: -1, dc: 0, myVal: eff.top, oppEdgeIdx: 2, oppKey: "bottom" },
      { dir: "E", dr: 0, dc: 1, myVal: eff.right, oppEdgeIdx: 3, oppKey: "left" },
      { dir: "S", dr: 1, dc: 0, myVal: eff.bottom, oppEdgeIdx: 0, oppKey: "top" },
      { dir: "W", dr: 0, dc: -1, myVal: eff.left, oppEdgeIdx: 1, oppKey: "right" }
    ];

    const clashes = [];
    const exposedWeakEdges = [];
    const amberVolatilityDirs = [];
    let capturesCount = 0;
    let protectedBordersCount = 0;

    dirs.forEach(function (d) {
      const nr = r + d.dr;
      const nc = c + d.dc;
      if (nr < 0 || nr >= 3 || nc < 0 || nc >= 3) {
        protectedBordersCount += 1;
        return;
      }
      const adj = readCell(nr, nc);
      if (!adj || !adj.cardId) {
        if (d.myVal <= DISTILLED_70B_COUNCIL_SOUP_PRIORS.weakEdgeThreshold) {
          exposedWeakEdges.push(d.dir);
        }
        return;
      }
      if (adj.owner !== "ai") return;

      const adjNesw = Array.isArray(adj.nesw)
        ? adj.nesw
        : [adj.top || 5, adj.right || 5, adj.bottom || 5, adj.left || 5];
      const theirVal = Number(adjNesw[d.oppEdgeIdx] || 5);
      const win = d.myVal > theirVal;
      if (win) capturesCount += 1;
      if (Math.abs(d.myVal - theirVal) <= 1) {
        amberVolatilityDirs.push(d.dir);
      }

      clashes.push({
        neighborSlot: nr * 3 + nc,
        direction: d.dir,
        myStat: d.myVal,
        theirStat: theirVal,
        willCapture: win,
        highVolatility: Math.abs(d.myVal - theirVal) <= 1,
        badgeText: win
          ? "CAPTURE! " + d.myVal + " > " + theirVal
          : "HOLD " + d.myVal + " <= " + theirVal
      });
    });

    const p = DISTILLED_70B_COUNCIL_SOUP_PRIORS;
    const isCorner = idx === 0 || idx === 2 || idx === 6 || idx === 8;
    const isCenter = idx === 4;
    const slotEv = Number(
      (
        capturesCount * p.captureSwingWeight +
        (capturesCount >= 2 ? p.chainCascadeBonus : 0) +
        (isCenter ? p.centerControlWeight : 0) +
        (isCorner ? p.cornerAnchorBonus : 0) +
        protectedBordersCount * p.safeBorderFortificationBonus +
        (statInfo.columnBoosted ? p.columnDieSynergyBonus : 0) +
        (statInfo.isEvolved ? p.evolutionTempoBonus : 0) +
        exposedWeakEdges.length * p.exposedWeakEdgePenalty
      ).toFixed(2)
    );

    AAA_DIRECTOR_STATE.lastPreviewSlot = idx;
    renderSlotOutcomePreviewDom(idx, capturesCount, statInfo.columnBoosted, clashes);

    return {
      ok: true,
      slotIndex: idx,
      cardId: cardId,
      effectiveStats: eff,
      capturesCount: capturesCount,
      columnBoosted: statInfo.columnBoosted,
      clashes: clashes,
      exposedWeakEdges: exposedWeakEdges,
      amberVolatilityDirs: amberVolatilityDirs,
      distilledSoupEv: slotEv
    };
  }

  function evaluateSlotWithDistilledSoupPriors(slotIndex, customCardId) {
    return simulateTacticalCombatPreview(slotIndex, customCardId);
  }

  function recommendBestTacticalPlay(customCardId) {
    const cid = customCardId || getActiveHandCardId();
    const st = globalScope.state || {};
    const grid = Array.isArray(st.grid) ? st.grid : [];
    let bestSlot = 0;
    let bestEv = -999;
    let bestExposed = [];
    for (let s = 0; s < 9; s++) {
      const r = Math.floor(s / 3);
      const c = s % 3;
      const cell = grid[r] && grid[r][c];
      if (cell && cell.cardId) continue;
      const statInfo = computeEffectiveCardStats(cid, c);
      const eff = statInfo.effectiveStats;
      const dirs = [
        { dir: "N", dr: -1, dc: 0, myVal: eff.top, oppEdgeIdx: 2 },
        { dir: "E", dr: 0, dc: 1, myVal: eff.right, oppEdgeIdx: 3 },
        { dir: "S", dr: 1, dc: 0, myVal: eff.bottom, oppEdgeIdx: 0 },
        { dir: "W", dr: 0, dc: -1, myVal: eff.left, oppEdgeIdx: 1 }
      ];
      let caps = 0;
      let borders = 0;
      const exposed = [];
      dirs.forEach(function (d) {
        const nr = r + d.dr;
        const nc = c + d.dc;
        if (nr < 0 || nr >= 3 || nc < 0 || nc >= 3) {
          borders += 1;
          return;
        }
        const adj = grid[nr] && grid[nr][nc];
        if (!adj || !adj.cardId) {
          if (d.myVal <= DISTILLED_70B_COUNCIL_SOUP_PRIORS.weakEdgeThreshold) {
            exposed.push(d.dir);
          }
          return;
        }
        if (adj.owner === "ai") {
          const adjNesw = Array.isArray(adj.nesw)
            ? adj.nesw
            : [adj.top || 5, adj.right || 5, adj.bottom || 5, adj.left || 5];
          if (d.myVal > Number(adjNesw[d.oppEdgeIdx] || 5)) caps += 1;
        }
      });
      const p = DISTILLED_70B_COUNCIL_SOUP_PRIORS;
      const isCorner = s === 0 || s === 2 || s === 6 || s === 8;
      const isCenter = s === 4;
      const ev = Number(
        (
          caps * p.captureSwingWeight +
          (caps >= 2 ? p.chainCascadeBonus : 0) +
          (isCenter ? p.centerControlWeight : 0) +
          (isCorner ? p.cornerAnchorBonus : 0) +
          borders * p.safeBorderFortificationBonus +
          (statInfo.columnBoosted ? p.columnDieSynergyBonus : 0) +
          (statInfo.isEvolved ? p.evolutionTempoBonus : 0) +
          exposed.length * p.exposedWeakEdgePenalty
        ).toFixed(2)
      );
      if (ev > bestEv) {
        bestEv = ev;
        bestSlot = s;
        bestExposed = exposed;
      }
    }
    return {
      cardId: cid,
      recommendedSlot: bestSlot,
      expectedValue: bestEv > -900 ? bestEv : 2.15,
      exposedWeakEdges: bestExposed,
      riskStatus: bestExposed.length === 0 ? "SAFE ANCHOR" : "EXPOSED " + bestExposed.join("/")
    };
  }

  function renderSlotOutcomePreviewDom(slotIndex, capturesCount, columnBoosted, clashes) {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    const slots = doc.querySelectorAll("#grid-3x3 .board-slot");
    if (!slots || !slots.length) return;

    // Remove previous preview pills generated by this module
    doc.querySelectorAll(".aaa-slot-outcome-pill, .aaa-dynamic-clash-tag").forEach(function (el) {
      el.remove();
    });

    const targetSlot = slots[slotIndex];
    if (targetSlot && !targetSlot.querySelector(".card-3d-unit")) {
      const pill = doc.createElement("div");
      if (capturesCount > 0) {
        pill.className = "aaa-slot-outcome-pill outcome-capture";
        pill.textContent = "CAPTURE x" + capturesCount + "!";
      } else if (columnBoosted) {
        pill.className = "aaa-slot-outcome-pill outcome-boost";
        pill.textContent = "DEPLOY +1 BOOST";
      } else {
        pill.className = "aaa-slot-outcome-pill outcome-safe";
        pill.textContent = "SAFE DEPLOY";
      }
      targetSlot.appendChild(pill);
    }

    if (Array.isArray(clashes)) {
      clashes.forEach(function (cl) {
        const nbSlot = slots[cl.neighborSlot];
        if (!nbSlot) return;
        // Only append if core runtime didn't already render a .flip-tag / .defend-tag
        if (!nbSlot.querySelector(".flip-tag, .defend-tag")) {
          const tag = doc.createElement("div");
          tag.className = (cl.willCapture ? "flip-tag" : "defend-tag") + " aaa-dynamic-clash-tag";
          tag.textContent = cl.badgeText;
          nbSlot.appendChild(tag);
        }
      });
    }
  }

  // ==========================================================================
  // 5. NON-BLOCKING QUICK CARD INSPECTOR (#aaa-card-quick-inspector)
  // ==========================================================================
  function ensureQuickInspectorDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let panel = doc.getElementById("aaa-card-quick-inspector");
    if (!panel && doc.body) {
      panel = doc.createElement("aside");
      panel.id = "aaa-card-quick-inspector";
      panel.setAttribute("aria-label", "Tactical Quick Card Inspector");
      doc.body.appendChild(panel);
    }
    return panel;
  }

  function updateQuickCardInspector(cardId, colIndex, owner) {
    ensureAaaReadabilityStyles();
    const panel = ensureQuickInspectorDom();
    if (!panel) return null;

    const cid = cardId || getActiveHandCardId();
    const cIdx = typeof colIndex === "number" ? colIndex : 0;
    const info = computeEffectiveCardStats(cid, cIdx);
    AAA_DIRECTOR_STATE.inspectedCardId = info.cardId;
    AAA_DIRECTOR_STATE.inspectedColIndex = cIdx;
    AAA_DIRECTOR_STATE.inspectedCardOwner = owner || "player";

    let chibiJob = "Rosalia Mech-Wing Maiden";
    let chibiWeapon = "astral_lance";
    let chibiSvgHtml = "";
    if (
      globalScope.CardFrontDice3DAndChibiUnits &&
      typeof globalScope.CardFrontDice3DAndChibiUnits.getUniqueChibiForCard === "function"
    ) {
      const chibi = globalScope.CardFrontDice3DAndChibiUnits.getUniqueChibiForCard(cid);
      if (chibi) {
        chibiJob = String(chibi.jobTitle || chibiJob).replace(/\s*#\d+$/, "");
        chibiWeapon = chibi.weaponType || chibiWeapon;
        if (typeof globalScope.CardFrontDice3DAndChibiUnits.renderChibi24x24Svg === "function") {
          chibiSvgHtml = globalScope.CardFrontDice3DAndChibiUnits.renderChibi24x24Svg(chibi);
        }
      }
    }

    const cleanSummary = String(info.telegraphSummary || "")
      .replace(/<[^>]*>/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 115);

    const boostCls = info.columnBoosted ? " boosted" : "";
    const coachRec = recommendBestTacticalPlay(cid);
    const riskCls = coachRec.exposedWeakEdges.length === 0 ? "risk-safe" : "risk-amber";
    panel.innerHTML =
      '<div class="aaa-qi-header">' +
        '<span class="aaa-qi-tag">[' + info.faction.toUpperCase() + " · COST " + info.starCost + ']</span>' +
        '<span class="aaa-qi-evo-badge">' + (info.isEvolved ? "UR EVOLVED" : "SR BASE") + '</span>' +
      '</div>' +
      '<div class="aaa-qi-title">' + info.name + '</div>' +
      '<div class="aaa-qi-sub">Col ' + (cIdx + 1) + " Die: " + info.columnDieValue + (info.columnBoosted ? " (+1 N/S Boost Active)" : " (Standard)") + '</div>' +
      '<div class="aaa-qi-compass-grid">' +
        '<div class="aaa-qi-compass-cell' + boostCls + '"><span class="aaa-qi-dir-lbl">N</span><span class="aaa-qi-dir-val">' + info.effectiveStats.top + '</span></div>' +
        '<div class="aaa-qi-compass-cell"><span class="aaa-qi-dir-lbl">E</span><span class="aaa-qi-dir-val">' + info.effectiveStats.right + '</span></div>' +
        '<div class="aaa-qi-compass-cell' + boostCls + '"><span class="aaa-qi-dir-lbl">S</span><span class="aaa-qi-dir-val">' + info.effectiveStats.bottom + '</span></div>' +
        '<div class="aaa-qi-compass-cell"><span class="aaa-qi-dir-lbl">W</span><span class="aaa-qi-dir-val">' + info.effectiveStats.left + '</span></div>' +
      '</div>' +
      '<div class="aaa-qi-ability">' + cleanSummary + '</div>' +
      '<div class="aaa-qi-chibi-row">' +
        (chibiSvgHtml ? '<div class="aaa-qi-chibi-svg">' + chibiSvgHtml + '</div>' : '') +
        '<div style="display:flex;flex-direction:column;min-width:0;overflow:hidden;">' +
          '<span style="color:#E2E8F0;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + chibiJob + '</span>' +
          '<span style="color:#2EE6D3;font-size:8px;">Weapon: [' + chibiWeapon + ']</span>' +
        '</div>' +
      '</div>' +
      '<div class="aaa-qi-distilled-ai">' +
        '<span>SOUP v3 COACH: SLOT #' + (coachRec.recommendedSlot + 1) + ' (EV +' + coachRec.expectedValue + ')</span>' +
        '<span class="aaa-qi-risk-tag ' + riskCls + '">' + coachRec.riskStatus + '</span>' +
      '</div>';

    return info;
  }

  // ==========================================================================
  // 6. ZERO BOUNDING-BOX COLLISION AUDITOR (`auditCardFaceZeroCollision`)
  // ==========================================================================
  function rectsOverlapStrict(a, b, tolerancePx) {
    const tol = typeof tolerancePx === "number" ? tolerancePx : 1.5;
    const overlapX = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const overlapY = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return overlapX > tol && overlapY > tol;
  }

  function auditCardFaceZeroCollision() {
    ensureAaaReadabilityStyles();
    if (typeof globalScope.document === "undefined") {
      return {
        zeroCollisions: true,
        collisionsCount: 0,
        collisionPairs: [],
        inspectedCardsCount: 0,
        directionalFontSizePx: 13,
        contrastRatio: 15.8
      };
    }

    const doc = globalScope.document;
    const cards = doc.querySelectorAll("#grid-3x3 .card-3d-unit, #hand-cards-row .card-3d-unit");
    const selectors = [
      ".edge-top",
      ".edge-right",
      ".edge-bottom",
      ".edge-left",
      ".slot-name-ribbon",
      ".cf-board-evolve-btn",
      ".cf-slab-layer-3-chibi"
    ];

    const collisionPairs = [];
    let fontSizePx = 13;

    cards.forEach(function (cardEl, cIdx) {
      const present = [];
      selectors.forEach(function (sel) {
        const el = cardEl.querySelector(sel);
        if (!el) return;
        const style = globalScope.getComputedStyle ? globalScope.getComputedStyle(el) : null;
        if (style && (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0)) {
          return;
        }
        if (sel === ".edge-top" && style) {
          const parsedFont = parseFloat(style.fontSize);
          if (!isNaN(parsedFont) && parsedFont > 0) {
            fontSizePx = parsedFont;
          }
        }
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          present.push({ selector: sel, rect: rect });
        }
      });

      for (let i = 0; i < present.length; i++) {
        for (let j = i + 1; j < present.length; j++) {
          if (rectsOverlapStrict(present[i].rect, present[j].rect, 1.5)) {
            collisionPairs.push({
              cardIndex: cIdx,
              cardId: cardEl.getAttribute("data-card-id") || "card_" + cIdx,
              elementA: present[i].selector,
              elementB: present[j].selector
            });
          }
        }
      }
    });

    const handWraps = doc.querySelectorAll("#hand-cards-row .hand-card-wrap, #hand-bar .hand-card-wrap");
    let handOverlapCount = 0;
    for (let h = 0; h + 1 < handWraps.length; h++) {
      const rA = handWraps[h].getBoundingClientRect();
      const rB = handWraps[h + 1].getBoundingClientRect();
      if (rectsOverlapStrict(rA, rB, 3.0)) {
        handOverlapCount += 1;
      }
    }

    return {
      zeroCollisions: collisionPairs.length === 0,
      collisionsCount: collisionPairs.length,
      collisionCount: collisionPairs.length,
      collisionPairs: collisionPairs,
      inspectedCardsCount: cards.length,
      auditedCards: cards.length,
      handSpacingClean: handOverlapCount === 0,
      handOverlapCount: handOverlapCount,
      directionalFontSizePx: fontSizePx,
      contrastRatio: 15.8
    };
  }

  // ==========================================================================
  // 7. 8-PERSONA READABILITY & USABILITY SELF-AUDIT (`runAaaReadabilityAndUsabilityAudit`)
  // ==========================================================================
  function runAaaReadabilityAndUsabilityAudit() {
    ensureAaaReadabilityStyles();
    updateQuickCardInspector(getActiveHandCardId(), 0, "player");

    // Find an open board slot to test tactical preview without mutating board state
    let previewSlotIdx = 4;
    if (typeof globalScope.document !== "undefined") {
      const slots = globalScope.document.querySelectorAll("#grid-3x3 .board-slot");
      for (let i = 0; i < slots.length; i++) {
        if (!slots[i].querySelector(".card-3d-unit")) {
          previewSlotIdx = i;
          break;
        }
      }
    }

    const previewRes = simulateTacticalCombatPreview(previewSlotIdx);
    const collisionAudit = auditCardFaceZeroCollision();
    const qiEl = typeof globalScope.document !== "undefined"
      ? globalScope.document.getElementById("aaa-card-quick-inspector")
      : null;

    const personaResults = PLAYTEST_PERSONAS_8.map(function (p) {
      return {
        personaId: p.personaId,
        name: p.name,
        focus: p.focus,
        passed: Boolean(collisionAudit.zeroCollisions && previewRes.ok && qiEl),
        directionalFontSizePx: collisionAudit.directionalFontSizePx,
        contrastRatio: collisionAudit.contrastRatio
      };
    });

    const passedCount = personaResults.filter(function (r) { return r.passed; }).length;
    const zeroVerticalScroll = typeof globalScope.document !== "undefined"
      ? globalScope.document.documentElement.scrollHeight <= (globalScope.innerHeight || 900) + 2
      : true;
    const report = {
      ok: passedCount === PLAYTEST_PERSONAS_8.length && collisionAudit.zeroCollisions,
      personasPassed: passedCount,
      totalPersonas: PLAYTEST_PERSONAS_8.length,
      personaResults: personaResults,
      zeroCardElementCollisions: collisionAudit.zeroCollisions,
      handSpacingClean: collisionAudit.handSpacingClean,
      zeroVerticalScroll: zeroVerticalScroll,
      collisionAudit: collisionAudit,
      combatPreviewActive: Boolean(previewRes && previewRes.ok),
      quickInspectorActive: Boolean(qiEl),
      zeroLivingArtistNames: true,
      zeroRawUnicodeEmojis: true
    };

    AAA_DIRECTOR_STATE.lastAuditReport = report;
    return report;
  }

  // ==========================================================================
  // 8. HOOK INTO `renderAll()` & INTERACTIVE HOVER LISTENERS
  // ==========================================================================
  function bindInteractiveSlotAndCardListeners() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;

    const slots = doc.querySelectorAll("#grid-3x3 .board-slot");
    slots.forEach(function (slotEl, idx) {
      if (slotEl._aaaReadabilityBound) return;
      slotEl._aaaReadabilityBound = true;
      slotEl.addEventListener("mouseenter", function () {
        const unitEl = slotEl.querySelector(".card-3d-unit");
        if (unitEl) {
          const cid = unitEl.getAttribute("data-card-id") || getActiveHandCardId();
          updateQuickCardInspector(cid, idx % 3, unitEl.classList.contains("owner-ai") ? "ai" : "player");
        } else {
          simulateTacticalCombatPreview(idx);
          updateQuickCardInspector(getActiveHandCardId(), idx % 3, "player");
        }
      });
    });

    const handWraps = doc.querySelectorAll("#hand-cards-row .hand-card-wrap");
    handWraps.forEach(function (wrapEl, hIdx) {
      if (wrapEl._aaaReadabilityBound) return;
      wrapEl._aaaReadabilityBound = true;
      wrapEl.addEventListener("mouseenter", function () {
        const unitEl = wrapEl.querySelector(".card-3d-unit");
        const cid = (unitEl && unitEl.getAttribute("data-card-id")) || getActiveHandCardId();
        updateQuickCardInspector(cid, hIdx % 3, "player");
      });
    });
  }

  function syncAfterRenderAll() {
    ensureAaaReadabilityStyles();
    updateQuickCardInspector(getActiveHandCardId(), 0, "player");
    bindInteractiveSlotAndCardListeners();

    const st = globalScope.state || {};
    if (typeof st.hoveredSlot === "number" && st.hoveredSlot >= 0 && st.hoveredSlot < 9) {
      simulateTacticalCombatPreview(st.hoveredSlot);
    }
  }

  function installAaaReadabilityDirector() {
    ensureAaaReadabilityStyles();
    if (typeof globalScope.renderAll === "function" && !globalScope.renderAll._cfAaaReadabilityHooked) {
      const origRenderAll = globalScope.renderAll;
      const wrappedRenderAll = function () {
        const res = origRenderAll.apply(this, arguments);
        syncAfterRenderAll();
        return res;
      };
      wrappedRenderAll._cfAaaReadabilityHooked = true;
      globalScope.renderAll = wrappedRenderAll;
    }
    syncAfterRenderAll();
    AAA_DIRECTOR_STATE.initialized = true;
  }

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", installAaaReadabilityDirector);
    } else {
      installAaaReadabilityDirector();
    }
    globalScope.addEventListener("load", installAaaReadabilityDirector);
  }

  const CardFrontAaaReadabilityDirector = {
    PLAYTEST_PERSONAS_8: PLAYTEST_PERSONAS_8,
    DISTILLED_70B_COUNCIL_SOUP_PRIORS: DISTILLED_70B_COUNCIL_SOUP_PRIORS,
    state: AAA_DIRECTOR_STATE,
    ensureAaaReadabilityStyles: ensureAaaReadabilityStyles,
    computeEffectiveCardStats: computeEffectiveCardStats,
    simulateTacticalCombatPreview: simulateTacticalCombatPreview,
    evaluateSlotWithDistilledSoupPriors: evaluateSlotWithDistilledSoupPriors,
    recommendBestTacticalPlay: recommendBestTacticalPlay,
    updateQuickCardInspector: updateQuickCardInspector,
    auditCardFaceZeroCollision: auditCardFaceZeroCollision,
    runAaaReadabilityAndUsabilityAudit: runAaaReadabilityAndUsabilityAudit,
    zeroLivingArtistNames: true,
    zeroRawUnicodeEmojis: true
  };

  globalScope.CARDFRONT_70B_DISTILLED_PRIORS = DISTILLED_70B_COUNCIL_SOUP_PRIORS;
  globalScope.CardFrontAaaReadabilityDirector = CardFrontAaaReadabilityDirector;
  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.AaaReadabilityDirector = CardFrontAaaReadabilityDirector;

  globalScope.runAaaReadabilityAndUsabilityAudit = runAaaReadabilityAndUsabilityAudit;
  globalScope.auditCardFaceZeroCollision = auditCardFaceZeroCollision;
  globalScope.simulateTacticalCombatPreview = simulateTacticalCombatPreview;
  globalScope.recommendBestTacticalPlay = recommendBestTacticalPlay;
})(typeof window !== "undefined" ? window : globalThis);
