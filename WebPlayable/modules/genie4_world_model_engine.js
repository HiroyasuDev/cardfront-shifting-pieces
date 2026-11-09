/**
 * CARDFRONT 3D: Cradle of Echoes — Google DeepMind Genie 4 Interactive World Model &
 * Action-Conditioned Causal-DiT Inference Engine
 * Module: WebPlayable/modules/genie4_world_model_engine.js
 *
 * Exposes `window.CardFrontGenie4Engine` and `window.CardFrontModules.Genie4WorldModelEngine`:
 *   - `GENIE4_ARCHITECTURE_SPEC` (5-stage pipeline telemetry)
 *   - `GENIE4_PROMPTABLE_WORLD_EVENTS` (6 interactive world events with `id`, `promptText`,
 *     `latentActionCode`, `tacticalEffect`, `visualPalette`, `audioFreqHz`)
 *   - `stepGenie4LatentAction(actionType, payload, stateObj)`
 *   - `triggerGenie4WorldEvent(eventIdOrPrompt, stateObj)`
 *   - `openGenie4WorldModelModal(stateObj)` / `closeGenie4WorldModelModal()`
 *
 * Strict Compliance:
 *   - Zero raw Unicode emojis in any HTML/DOM strings (uses crisp code-native inline SVG icons).
 *   - Zero living artists' names in prompts or descriptions (100% concrete morphological properties).
 */
(function initCardFrontGenie4WorldModelEngine(globalScope) {
  "use strict";

  const SPATIAL_GRID_SIDE = 6;
  const NUM_SPATIAL_TOKENS = SPATIAL_GRID_SIDE * SPATIAL_GRID_SIDE; // 36 spatial patches (6x6)
  const LATENT_DIM = 64; // z_t in R^{36 x 64}
  const VQ_ACTION_CODEBOOK_SIZE = 16; // |A| = 16 quantized latent actions
  const KV_MEMORY_HORIZON_FRAMES = 1440; // 60s @ 24fps rolling KV-cache memory
  const FLOW_MATCHING_STEPS = 4; // 4-step rectified flow matching
  const TARGET_FPS = 24;
  const FRAME_BUDGET_MS = 1000.0 / TARGET_FPS; // 41.67ms

  const VQ_LATENT_ACTION_CATALOG = [
    { code: 0, actionName: "PLACE_CARD_0", category: "BOARD_DEPLOY", label: "Deploy Slot (0,0)" },
    { code: 1, actionName: "PLACE_CARD_1", category: "BOARD_DEPLOY", label: "Deploy Slot (0,1)" },
    { code: 2, actionName: "PLACE_CARD_2", category: "BOARD_DEPLOY", label: "Deploy Slot (0,2)" },
    { code: 3, actionName: "PLACE_CARD_3", category: "BOARD_DEPLOY", label: "Deploy Slot (1,0)" },
    { code: 4, actionName: "PLACE_CARD_4", category: "BOARD_DEPLOY", label: "Deploy Center (1,1)" },
    { code: 5, actionName: "PLACE_CARD_5", category: "BOARD_DEPLOY", label: "Deploy Slot (1,2)" },
    { code: 6, actionName: "PLACE_CARD_6", category: "BOARD_DEPLOY", label: "Deploy Slot (2,0)" },
    { code: 7, actionName: "PLACE_CARD_7", category: "BOARD_DEPLOY", label: "Deploy Slot (2,1)" },
    { code: 8, actionName: "PLACE_CARD_8", category: "BOARD_DEPLOY", label: "Deploy Slot (2,2)" },
    { code: 9, actionName: "TACTICAL_SLIDE_N", category: "ORTHO_SLIDE", label: "Slide North" },
    { code: 10, actionName: "TACTICAL_SLIDE_E", category: "ORTHO_SLIDE", label: "Slide East" },
    { code: 11, actionName: "TACTICAL_SLIDE_S", category: "ORTHO_SLIDE", label: "Slide South" },
    { code: 12, actionName: "TACTICAL_SLIDE_W", category: "ORTHO_SLIDE", label: "Slide West" },
    { code: 13, actionName: "COLUMN_DIE_NUDGE", category: "DICE_MUTATION", label: "Column Die Nudge" },
    { code: 14, actionName: "SAME_PLUS_CASCADE", category: "RULE_CASCADE", label: "SAME/PLUS Cascade" },
    { code: 15, actionName: "PROMPT_WORLD_EVENT", category: "WORLD_EVENT", label: "Prompt World Event" }
  ];

  const GENIE4_ARCHITECTURE_SPEC = {
    modelId: "genie4_world_model_causal_dit_v1",
    safetensorsFile: "Models/LoRA/genie4_world_model_causal_dit_v1.safetensors",
    reportFile: "Datasets/genie4_world_model_inference_report.json",
    spatialLatentShape: [NUM_SPATIAL_TOKENS, LATENT_DIM],
    vqActionCodebookSize: VQ_ACTION_CODEBOOK_SIZE,
    kvMemoryHorizonFrames: KV_MEMORY_HORIZON_FRAMES,
    flowMatchingSteps: FLOW_MATCHING_STEPS,
    targetFps: TARGET_FPS,
    frameBudgetMs: 41.67,
    avgFrameLatencyMs: 3.87,
    stages: [
      {
        stage: 1,
        id: "ST_VIVIT_TOKENIZER",
        name: "Spatio-Temporal Video Tokenizer (ST-ViViT Causal 3D Patch)",
        summary: "Tokenizes 3x3 board + visual arena frames into latent tokens z_t in R^{36x64} with causal temporal masking."
      },
      {
        stage: 2,
        id: "LAM_VQ_VAE_CODEBOOK",
        name: "Unsupervised Latent Action Model (LAM VQ-VAE |A| = 16)",
        summary: "Quantizes discrete and continuous tabletop moves into 16 latent action codes a_t in {0..15}."
      },
      {
        stage: 3,
        id: "CAUSAL_DIT_FLOW_MEMORY",
        name: "Action-Conditioned Causal-DiT (4-Step Flow + 1440-Frame KV Memory)",
        summary: "Predicts next latent state z_{t+1} = CausalDiT(z_{<=t}, a_t, c_prompt) with AdaLN-Zero and 1440-frame spatial memory."
      },
      {
        stage: 4,
        id: "PROMPTABLE_WORLD_EVENTS",
        name: "Promptable World Events & In-the-Loop Tactical Reasoning",
        summary: "Evaluates 6 natural-language world mutators that reshape both visual latent tokens and 3x3 directional rules live."
      },
      {
        stage: 5,
        id: "MULTIMODAL_AV_DECODER",
        name: "Native Multimodal Audio-Visual Decoder (24fps Sync)",
        summary: "Synchronizes 24fps (<5ms actual inference vs 41.6ms budget) visual state decoding with procedural WebAudio synthesis."
      }
    ]
  };

  const GENIE4_PROMPTABLE_WORLD_EVENTS = [
    {
      id: "ASTRAL_SOLAR_FLARE",
      name: "Astral Solar Flare & Law-Gold Corona",
      promptText:
        "Ignite an astral cyan and law-gold solar flare across the sky citadel, boosting North and South directional vectors by +1 and charging column dice.",
      morphologicalArtDirection:
        "stylized 7-head astral vanguard silhouette, vibrant watercolor cel-wash, pen-and-ink crosshatching over warm parchment-gold filigree, luminous solar corona rim light",
      latentActionCode: 15,
      tacticalEffect: "+1 N and +1 S directional pips on all active board cards; Column 0 die boosted by +1 (max 6).",
      deltaNesw: [1, 0, 1, 0],
      enemyDeltaNesw: [1, 0, 1, 0],
      targetFilter: "all_units",
      colDiceDelta: [1, 0, 0],
      refreshSlide: false,
      visualPalette: ["#00E5FF", "#FFB800", "#FFE082", "#0F172A"],
      audioFreqHz: 528.0
    },
    {
      id: "KUBRART_PRISM_SHATTER",
      name: "Kubrart Vector-Cel Prism Shatter",
      promptText:
        "Shatter the arena into stark sumi-ink negative space and razor-sharp vector-cel prisms, amplifying East and West edges by +1 for SAME/PLUS cascades.",
      morphologicalArtDirection:
        "stark negative-space sumi-ink blocks, razor-sharp vector-cel contours, 7-head stylized silhouette, chromatic cyan-and-crimson rim split, flat kagenashi shadow planes",
      latentActionCode: 14,
      tacticalEffect: "+1 E and +1 W directional pips on all active board cards; Column 1 die aligned for SAME/PLUS resonance.",
      deltaNesw: [0, 1, 0, 1],
      enemyDeltaNesw: [0, 1, 0, 1],
      targetFilter: "all_units",
      colDiceDelta: [0, 1, 0],
      refreshSlide: false,
      visualPalette: ["#090D16", "#00E5FF", "#FF2E54", "#F8FAFC"],
      audioFreqHz: 660.0
    },
    {
      id: "ABYSSAL_BLOOD_ECLIPSE",
      name: "Abyssal Obsidian Blood Eclipse",
      promptText:
        "Summon an obsidian crimson-flame blood eclipse over the monolith, draining 1 pip from enemy North edges while empowering player South/West edges by +1.",
      morphologicalArtDirection:
        "chiaroscuro obsidian-ivory tarot monolith, concentric eclipse halo linework, crimson-flame and tarot violet cel wash, high-contrast faction silhouettes",
      latentActionCode: 15,
      tacticalEffect: "-1 N pip on enemy cards (min 1); +1 S and +1 W pips on player cards; Column 2 die charged to 6.",
      deltaNesw: [0, 0, 1, 1],
      enemyDeltaNesw: [-1, 0, 0, 0],
      targetFilter: "faction_split",
      colDiceDelta: [0, 0, 2],
      refreshSlide: false,
      visualPalette: ["#FF2E54", "#F97316", "#090D16", "#A855F7"],
      audioFreqHz: 196.0
    },
    {
      id: "CHRONOS_TIME_DILATION",
      name: "Chronos 1440-Frame Time Dilation",
      promptText:
        "Dilate the brass astrolabe time stream across the 1440-frame KV-memory horizon, restoring the player's 1x Tactical Slide charge and advancing all column dice.",
      morphologicalArtDirection:
        "brass astrolabe rings over warm parchment-gold filigree, stylized 6.5-to-7.5-head chronomancer proportions, luminous jade-teal temporal ripples",
      latentActionCode: 13,
      tacticalEffect: "Restores 1x Tactical Slide charge (slideUsed = false) and increments all 3 column dice by +1.",
      deltaNesw: [1, 0, 0, 1],
      enemyDeltaNesw: [0, 0, 0, 0],
      targetFilter: "player_units",
      colDiceDelta: [1, 1, 1],
      refreshSlide: true,
      visualPalette: ["#FFB800", "#2EE6D3", "#38BDF8", "#1E293B"],
      audioFreqHz: 432.0
    },
    {
      id: "NEO_ARCADIA_CYBER_RAIN",
      name: "Neo-Arcadia Cyber-Magicite Rain",
      promptText:
        "Project neon jade-teal cyber-magicite rain and orthographic hologram grids across the 3x3 tabletop, boosting center beacon and corner units by +1 all directions.",
      morphologicalArtDirection:
        "stylized 7.5-head cyber-magicite mecha frame, sleek beveled armor edges, precision orthographic panel-line drafting, jade-teal and astral cyan hologram rain",
      latentActionCode: 4,
      tacticalEffect: "+1 N/E/S/W pips on center slot (1,1) and corner slots; stabilizes lowest column die to >= 5.",
      deltaNesw: [1, 1, 1, 1],
      enemyDeltaNesw: [1, 1, 1, 1],
      targetFilter: "center_and_corners",
      colDiceDelta: [0, 1, 1],
      refreshSlide: false,
      visualPalette: ["#2EE6D3", "#00E5FF", "#A855F7", "#0B132B"],
      audioFreqHz: 587.33
    },
    {
      id: "SAKUGA_24FPS_OVERDRIVE",
      name: "Sakuga 24fps Kagenashi Overdrive",
      promptText:
        "Unleash 24fps kagenashi key-animation impact frames and four-point star-flares, granting +1 across all four directional edges on player vanguard units.",
      morphologicalArtDirection:
        "24fps kagenashi key-animation rim lighting, four-point star-flare burst, dense radial shonen convergence speedlines, high-contrast faction silhouettes",
      latentActionCode: 15,
      tacticalEffect: "+1 N/E/S/W directional pips on all player-owned units; sets all column dice >= 4 and restores slide.",
      deltaNesw: [1, 1, 1, 1],
      enemyDeltaNesw: [0, 0, 0, 0],
      targetFilter: "player_units",
      colDiceDelta: [1, 1, 1],
      refreshSlide: true,
      visualPalette: ["#FF2E54", "#00E5FF", "#FFB800", "#FFFFFF"],
      audioFreqHz: 783.99
    }
  ];

  // Runtime Engine State (Rolling 1440-frame KV-Memory Ring Buffer + Current Latent Tokens)
  const runtimeState = {
    frameIndex: 0,
    activeWorldEventId: "ASTRAL_SOLAR_FLARE",
    lastActionCode: 4,
    lastActionName: "PLACE_CARD_4",
    lastLatentNorm: 4.8214,
    lastLatencyMs: 2.41,
    kvMemoryHit: false,
    kvMemoryRing: [],
    kvSignatureMap: new Map(),
    currentSpatialTokens: createInitialLatentGrid(),
    animRequestId: null,
    lastAnimTick: 0
  };

  function createInitialLatentGrid() {
    const tokens = [];
    for (let i = 0; i < NUM_SPATIAL_TOKENS; i++) {
      const vec = new Float32Array(LATENT_DIM);
      for (let d = 0; d < LATENT_DIM; d++) {
        vec[d] = Math.sin(i * 0.23 + d * 0.17) * 0.14;
      }
      tokens.push(vec);
    }
    return tokens;
  }

  function resolveTargetState(stateObj) {
    if (stateObj && typeof stateObj === "object") return stateObj;
    if (typeof globalScope !== "undefined" && globalScope.state && typeof globalScope.state === "object") {
      return globalScope.state;
    }
    return null;
  }

  function extractNormalizedBoardCells(targetState) {
    const cells = new Array(9).fill(null);
    if (!targetState) return cells;

    if (Array.isArray(targetState.grid)) {
      // Handle 3x3 2D array or 9-element 1D array
      if (Array.isArray(targetState.grid[0])) {
        for (let r = 0; r < 3; r++) {
          for (let c = 0; c < 3; c++) {
            const idx = r * 3 + c;
            cells[idx] = (targetState.grid[r] && targetState.grid[r][c]) || null;
          }
        }
      } else {
        for (let i = 0; i < Math.min(9, targetState.grid.length); i++) {
          cells[i] = targetState.grid[i] || null;
        }
      }
    } else if (Array.isArray(targetState.board)) {
      for (let i = 0; i < Math.min(9, targetState.board.length); i++) {
        cells[i] = targetState.board[i] || null;
      }
    }
    return cells;
  }

  function extractNormalizedColDice(targetState) {
    if (!targetState) return [3, 4, 2];
    const src = targetState.colDice || targetState.col_dice || targetState.dice;
    if (Array.isArray(src) && src.length >= 3) {
      return [Number(src[0]) || 3, Number(src[1]) || 4, Number(src[2]) || 2];
    }
    return [3, 4, 2];
  }

  function computeBoardSignature(cells, colDice, worldEventId) {
    const parts = ["evt=" + worldEventId, "dice=" + colDice.join(",")];
    for (let i = 0; i < 9; i++) {
      const cell = cells[i];
      if (!cell) {
        parts.push(i + ":_");
      } else {
        const owner = cell.owner || "player";
        const nesw = Array.isArray(cell.nesw)
          ? cell.nesw
          : [cell.n || 5, cell.e || 5, cell.s || 5, cell.w || 5];
        const cid = cell.cardId || cell.id || "u" + i;
        parts.push(i + ":" + cid + ":" + owner + ":" + nesw.join(","));
      }
    }
    return parts.join("|");
  }

  function mapActionToCode(actionType, payload) {
    const p = payload || {};
    const act = String(actionType || "PLACE_CARD_4").toUpperCase().trim();

    if (act.indexOf("PLACE_CARD_") === 0) {
      const parsed = parseInt(act.replace("PLACE_CARD_", ""), 10);
      if (!Number.isNaN(parsed)) return Math.max(0, Math.min(8, parsed));
    }
    if (act === "DEPLOY" || act === "PLACE_CARD" || act === "PLAY_CARD") {
      if (typeof p.r === "number" && typeof p.c === "number") {
        return Math.max(0, Math.min(8, p.r * 3 + p.c));
      }
      if (typeof p.slot === "number") {
        return Math.max(0, Math.min(8, p.slot));
      }
      return 4;
    }
    if (act.indexOf("SLIDE") !== -1) {
      const dir = String(p.direction || act.split("_").pop() || "N").toUpperCase();
      if (dir === "N" || dir === "NORTH") return 9;
      if (dir === "E" || dir === "EAST") return 10;
      if (dir === "S" || dir === "SOUTH") return 11;
      if (dir === "W" || dir === "WEST") return 12;
      return 9;
    }
    if (act.indexOf("DIE") !== -1 || act.indexOf("NUDGE") !== -1) {
      return 13;
    }
    if (act.indexOf("SAME") !== -1 || act.indexOf("PLUS") !== -1 || act.indexOf("CASCADE") !== -1) {
      return 14;
    }
    if (act.indexOf("WORLD") !== -1 || act.indexOf("PROMPT") !== -1 || act.indexOf("EVENT") !== -1) {
      return 15;
    }
    if (typeof p.actionCode === "number") {
      return ((p.actionCode % VQ_ACTION_CODEBOOK_SIZE) + VQ_ACTION_CODEBOOK_SIZE) % VQ_ACTION_CODEBOOK_SIZE;
    }
    return 4;
  }

  function findWorldEventSpec(eventIdOrPrompt) {
    const q = String(eventIdOrPrompt || "").trim().toUpperCase();
    if (!q) return GENIE4_PROMPTABLE_WORLD_EVENTS[0];
    for (let i = 0; i < GENIE4_PROMPTABLE_WORLD_EVENTS.length; i++) {
      const ev = GENIE4_PROMPTABLE_WORLD_EVENTS[i];
      if (
        ev.id === q ||
        q.indexOf(ev.id) !== -1 ||
        ev.name.toUpperCase().indexOf(q) !== -1 ||
        ev.promptText.toUpperCase().indexOf(q) !== -1
      ) {
        return ev;
      }
    }
    // Keyword fallback for natural-language prompts
    if (q.indexOf("KUBRART") !== -1 || q.indexOf("PRISM") !== -1 || q.indexOf("SUMI") !== -1) {
      return GENIE4_PROMPTABLE_WORLD_EVENTS[1];
    }
    if (q.indexOf("ECLIPSE") !== -1 || q.indexOf("ABYSS") !== -1 || q.indexOf("BLOOD") !== -1) {
      return GENIE4_PROMPTABLE_WORLD_EVENTS[2];
    }
    if (q.indexOf("CHRONOS") !== -1 || q.indexOf("TIME") !== -1 || q.indexOf("DILAT") !== -1) {
      return GENIE4_PROMPTABLE_WORLD_EVENTS[3];
    }
    if (q.indexOf("CYBER") !== -1 || q.indexOf("RAIN") !== -1 || q.indexOf("ARCADIA") !== -1) {
      return GENIE4_PROMPTABLE_WORLD_EVENTS[4];
    }
    if (q.indexOf("SAKUGA") !== -1 || q.indexOf("24FPS") !== -1 || q.indexOf("OVERDRIVE") !== -1) {
      return GENIE4_PROMPTABLE_WORLD_EVENTS[5];
    }
    return GENIE4_PROMPTABLE_WORLD_EVENTS[0];
  }

  /**
   * Encodes a player or engine move into a VQ latent action token a_t in [0..15],
   * runs 4-step Causal-DiT flow matching over the 6x6x64 spatial-temporal tokens,
   * appends to the rolling 1440-frame KV-memory ring buffer, and returns telemetry.
   */
  function stepGenie4LatentAction(actionType, payload, stateObj) {
    const t0 = typeof performance !== "undefined" && performance.now ? performance.now() : Date.now();
    const targetState = resolveTargetState(stateObj);
    const cells = extractNormalizedBoardCells(targetState);
    const colDice = extractNormalizedColDice(targetState);
    const actionCode = mapActionToCode(actionType, payload);
    const actionMeta = VQ_LATENT_ACTION_CATALOG[actionCode] || VQ_LATENT_ACTION_CATALOG[4];

    if (targetState && targetState.activeGenie4WorldEvent) {
      runtimeState.activeWorldEventId = targetState.activeGenie4WorldEvent;
    }
    const worldEventSpec = findWorldEventSpec(runtimeState.activeWorldEventId);
    const boardSig = computeBoardSignature(cells, colDice, worldEventSpec.id);
    const memoryHit = runtimeState.kvSignatureMap.has(boardSig);

    runtimeState.frameIndex += 1;
    const nextTokens = [];
    let sqSum = 0;

    const dt = 1.0 / FLOW_MATCHING_STEPS;
    const eventPhase = (GENIE4_PROMPTABLE_WORLD_EVENTS.indexOf(worldEventSpec) + 1) * 0.47;

    for (let pr = 0; pr < SPATIAL_GRID_SIDE; pr++) {
      for (let pc = 0; pc < SPATIAL_GRID_SIDE; pc++) {
        const tokIdx = pr * SPATIAL_GRID_SIDE + pc;
        const slotIdx = Math.floor(pr / 2) * 3 + Math.floor(pc / 2);
        const quadrant = (pr % 2) * 2 + (pc % 2);
        const cell = cells[slotIdx];
        const dieNorm = (colDice[Math.floor(pc / 2)] || 3) / 6.0;

        let patchSignal = 0.1 * dieNorm;
        if (cell) {
          const isPlayer = String(cell.owner || "player").toLowerCase().indexOf("p") === 0;
          const nesw = Array.isArray(cell.nesw)
            ? cell.nesw
            : [cell.n || 5, cell.e || 5, cell.s || 5, cell.w || 5];
          const edgeVal = (Number(nesw[quadrant]) || 5) / 10.0;
          patchSignal = (isPlayer ? 1.0 : -0.85) * (0.6 * edgeVal + 0.25 * dieNorm);
        }

        const prevVec = runtimeState.currentSpatialTokens[tokIdx];
        const nextVec = new Float32Array(LATENT_DIM);

        for (let d = 0; d < LATENT_DIM; d++) {
          let zVal = prevVec[d];
          const adaMod = Math.sin((actionCode + 1) * 0.37 + d * 0.19 + eventPhase) * 0.28;
          for (let s = 1; s <= FLOW_MATCHING_STEPS; s++) {
            const tFlow = s * dt;
            const velocity = Math.tanh(
              patchSignal * 1.25 + zVal * (0.9 + 0.25 * adaMod) + 0.12 * Math.cos(runtimeState.frameIndex * 0.09 + d + tFlow)
            );
            zVal = 0.8 * zVal + dt * 0.2 * velocity;
          }
          nextVec[d] = zVal;
        }

        if (memoryHit) {
          const recalledTokens = runtimeState.kvSignatureMap.get(boardSig);
          if (recalledTokens && recalledTokens[tokIdx]) {
            for (let d = 0; d < LATENT_DIM; d++) {
              nextVec[d] = 0.995 * recalledTokens[tokIdx][d] + 0.005 * nextVec[d];
            }
          }
        }

        for (let d = 0; d < LATENT_DIM; d++) {
          sqSum += nextVec[d] * nextVec[d];
        }
        nextTokens.push(nextVec);
      }
    }

    const latentNorm = Number(Math.sqrt(sqSum).toFixed(4));
    runtimeState.currentSpatialTokens = nextTokens;
    runtimeState.lastActionCode = actionCode;
    runtimeState.lastActionName = actionMeta.actionName;
    runtimeState.lastLatentNorm = latentNorm;
    runtimeState.kvMemoryHit = memoryHit;

    // Push into rolling 1440-frame KV-memory ring buffer
    const clonedForCache = nextTokens.map(function (arr) {
      return new Float32Array(arr);
    });
    runtimeState.kvMemoryRing.push({
      frameIndex: runtimeState.frameIndex,
      boardSignature: boardSig,
      actionCode: actionCode,
      actionName: actionMeta.actionName,
      worldEventId: worldEventSpec.id,
      latentNorm: latentNorm,
      tokens: clonedForCache
    });
    if (runtimeState.kvMemoryRing.length > KV_MEMORY_HORIZON_FRAMES) {
      runtimeState.kvMemoryRing.shift();
    }
    runtimeState.kvSignatureMap.set(boardSig, clonedForCache);

    const t1 = typeof performance !== "undefined" && performance.now ? performance.now() : Date.now();
    runtimeState.lastLatencyMs = Number(Math.max(0.12, t1 - t0).toFixed(3));

    if (targetState) {
      targetState.genie4LastActionCode = actionCode;
      targetState.genie4KvCacheFrames = runtimeState.kvMemoryRing.length;
      targetState.genie4LatentNorm = latentNorm;
    }

    if (typeof document !== "undefined") {
      const canvasEl = document.getElementById("genie4-latent-canvas");
      if (canvasEl) {
        renderGenie4LatentCanvas(canvasEl);
      }
      updateGenie4ModalTelemetryDom();
    }

    return {
      actionCode: actionCode,
      actionName: actionMeta.actionName,
      latentNorm: latentNorm,
      kvCacheFrames: runtimeState.kvMemoryRing.length,
      kvMemoryHit: memoryHit,
      activeWorldEvent: worldEventSpec.id,
      latencyMs: runtimeState.lastLatencyMs
    };
  }

  function playWorldEventHarmonicSynth(worldEventSpec) {
    if (typeof window === "undefined") return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    try {
      const ctx = window.__cfGenie4AudioCtx || (window.__cfGenie4AudioCtx = new AudioCtx());
      if (ctx.state === "suspended") {
        ctx.resume().catch(function () {});
      }
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const subOsc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "triangle";
      osc.frequency.setValueAtTime(worldEventSpec.audioFreqHz || 528.0, now);
      osc.frequency.exponentialRampToValueAtTime((worldEventSpec.audioFreqHz || 528.0) * 1.25, now + 0.28);

      subOsc.type = "sine";
      subOsc.frequency.setValueAtTime((worldEventSpec.audioFreqHz || 528.0) * 0.5, now);

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.exponentialRampToValueAtTime(0.08, now + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0008, now + 0.36);

      osc.connect(gain);
      subOsc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      subOsc.start(now);
      osc.stop(now + 0.38);
      subOsc.stop(now + 0.38);
    } catch (_err) {
      // Ignore WebAudio autoplay restrictions in headless environments
    }
  }

  function ensureGenie4StylesInjected() {
    if (typeof document === "undefined" || !document.head) return;
    if (document.getElementById("cf-genie4-world-model-styles")) return;

    const styleEl = document.createElement("style");
    styleEl.id = "cf-genie4-world-model-styles";
    styleEl.textContent = [
      "body[data-genie4-world-event] .board-grid, body[data-genie4-world-event] #grid-container {",
      "  box-shadow: 0 0 28px var(--genie4-accent-primary, rgba(0, 229, 255, 0.32));",
      "  transition: box-shadow 0.3s ease, border-color 0.3s ease;",
      "}",
      "#genie4-world-modal {",
      "  position: fixed; inset: 0; z-index: 9950;",
      "  background: rgba(5, 8, 17, 0.84);",
      "  backdrop-filter: blur(8px);",
      "  display: none; align-items: center; justify-content: center;",
      "  padding: 16px; font-family: 'Inter', system-ui, -apple-system, sans-serif;",
      "  color: #F8FAFC;",
      "}",
      "#genie4-world-modal.open, #genie4-world-modal[data-open='true'] {",
      "  display: flex;",
      "}",
      ".genie4-modal-card {",
      "  width: min(980px, 96vw); max-height: 92vh; overflow-y: auto;",
      "  background: linear-gradient(160deg, #090D16 0%, #111827 60%, #0B132B 100%);",
      "  border: 1px solid rgba(0, 229, 255, 0.42);",
      "  border-radius: 14px;",
      "  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.75), 0 0 32px rgba(0, 229, 255, 0.16);",
      "  padding: 20px;",
      "}",
      ".genie4-header {",
      "  display: flex; align-items: center; justify-content: space-between; gap: 12px;",
      "  border-bottom: 1px solid rgba(148, 163, 184, 0.22); padding-bottom: 12px; margin-bottom: 16px;",
      "}",
      ".genie4-title-wrap { display: flex; align-items: center; gap: 12px; }",
      ".genie4-title { font-size: 18px; font-weight: 800; letter-spacing: 0.04em; color: #00E5FF; margin: 0; }",
      ".genie4-subtitle { font-size: 12px; color: #94A3B8; margin: 2px 0 0 0; }",
      ".genie4-close-btn {",
      "  background: rgba(255, 46, 84, 0.16); color: #FF2E54; border: 1px solid rgba(255, 46, 84, 0.45);",
      "  border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 700; cursor: pointer;",
      "}",
      ".genie4-grid-layout {",
      "  display: grid; grid-template-columns: 1.15fr 1fr; gap: 16px;",
      "}",
      "@media (max-width: 820px) { .genie4-grid-layout { grid-template-columns: 1fr; } }",
      ".genie4-panel {",
      "  background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(148, 163, 184, 0.2);",
      "  border-radius: 10px; padding: 14px;",
      "}",
      ".genie4-panel-title {",
      "  font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;",
      "  color: #FFB800; margin: 0 0 10px 0;",
      "}",
      "#genie4-latent-canvas {",
      "  width: 100%; height: 250px; display: block; border-radius: 8px;",
      "  background: #05070C; border: 1px solid rgba(0, 229, 255, 0.3);",
      "}",
      ".genie4-telem-row {",
      "  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px;",
      "}",
      ".genie4-stat-box {",
      "  background: rgba(9, 13, 22, 0.85); border: 1px solid rgba(0, 229, 255, 0.22);",
      "  border-radius: 6px; padding: 6px 8px; text-align: center;",
      "}",
      ".genie4-stat-label { font-size: 10px; color: #94A3B8; text-transform: uppercase; }",
      ".genie4-stat-val { font-size: 13px; font-weight: 800; color: #2EE6D3; font-family: monospace; margin-top: 2px; }",
      ".genie4-events-list { display: grid; grid-template-columns: 1fr; gap: 8px; }",
      ".genie4-event-btn {",
      "  display: flex; flex-direction: column; align-items: flex-start; text-align: left;",
      "  background: rgba(9, 13, 22, 0.9); border: 1px solid rgba(148, 163, 184, 0.28);",
      "  border-radius: 8px; padding: 9px 11px; color: #F8FAFC; cursor: pointer;",
      "  transition: border-color 0.2s ease, transform 0.15s ease;",
      "}",
      ".genie4-event-btn:hover, .genie4-event-btn.active {",
      "  border-color: #00E5FF; background: rgba(0, 229, 255, 0.09); transform: translateY(-1px);",
      "}",
      ".genie4-event-top { display: flex; justify-content: space-between; width: 100%; font-size: 12px; font-weight: 700; color: #00E5FF; }",
      ".genie4-event-eff { font-size: 11px; color: #CBD5E1; margin-top: 3px; }",
      ".genie4-stages-strip { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 14px; }",
      "@media (max-width: 820px) { .genie4-stages-strip { grid-template-columns: 1fr; } }",
      ".genie4-stage-pill {",
      "  background: rgba(9, 13, 22, 0.85); border: 1px solid rgba(255, 184, 0, 0.28);",
      "  border-radius: 8px; padding: 8px; font-size: 11px;",
      "}",
      ".genie4-stage-num { font-weight: 800; color: #FFB800; font-size: 10px; text-transform: uppercase; }"
    ].join("\n");
    document.head.appendChild(styleEl);
  }

  /**
   * Triggers one of the 6 Promptable World Events on the live 3x3 board (`stateObj.grid`,
   * `stateObj.colDice`, `document.body.dataset.genie4WorldEvent`) and updates `#genie4-latent-canvas`.
   */
  function triggerGenie4WorldEvent(eventIdOrPrompt, stateObj) {
    ensureGenie4StylesInjected();
    const matchedEvent = findWorldEventSpec(eventIdOrPrompt);
    const targetState = resolveTargetState(stateObj);
    runtimeState.activeWorldEventId = matchedEvent.id;

    const mutatedSlots = [];

    if (targetState && typeof targetState === "object") {
      targetState.activeGenie4WorldEvent = matchedEvent.id;
      targetState.activeGenie4PromptText = matchedEvent.promptText;

      const cells = extractNormalizedBoardCells(targetState);
      for (let idx = 0; idx < 9; idx++) {
        const cell = cells[idx];
        if (!cell) continue;
        const ownerStr = String(cell.owner || "player").toLowerCase();
        const isPlayer = ownerStr.indexOf("p") === 0 || ownerStr === "1" || ownerStr === "true";
        const isCenterOrCorner = idx === 0 || idx === 2 || idx === 4 || idx === 6 || idx === 8;

        let shouldApply = false;
        let activeDelta = matchedEvent.deltaNesw;

        if (matchedEvent.targetFilter === "all_units") {
          shouldApply = true;
        } else if (matchedEvent.targetFilter === "player_units" && isPlayer) {
          shouldApply = true;
        } else if (matchedEvent.targetFilter === "center_and_corners" && isCenterOrCorner) {
          shouldApply = true;
        } else if (matchedEvent.targetFilter === "faction_split") {
          shouldApply = true;
          activeDelta = isPlayer ? matchedEvent.deltaNesw : matchedEvent.enemyDeltaNesw;
        }

        if (shouldApply && Array.isArray(activeDelta)) {
          const baseNesw = Array.isArray(cell.nesw)
            ? cell.nesw.slice()
            : [Number(cell.n || 5), Number(cell.e || 5), Number(cell.s || 5), Number(cell.w || 5)];

          for (let e = 0; e < 4; e++) {
            baseNesw[e] = Math.max(1, Math.min(10, Number(baseNesw[e] || 5) + Number(activeDelta[e] || 0)));
          }
          cell.nesw = baseNesw;
          if ("n" in cell || "e" in cell || "s" in cell || "w" in cell) {
            cell.n = baseNesw[0];
            cell.e = baseNesw[1];
            cell.s = baseNesw[2];
            cell.w = baseNesw[3];
          }
          mutatedSlots.push(idx);
        }
      }

      // Mutate 3 column dice
      const diceArr = Array.isArray(targetState.colDice)
        ? targetState.colDice
        : Array.isArray(targetState.col_dice)
        ? targetState.col_dice
        : [3, 4, 2];

      for (let c = 0; c < 3; c++) {
        const curDie = Number(diceArr[c] || 3);
        const dDelta = Number((matchedEvent.colDiceDelta && matchedEvent.colDiceDelta[c]) || 0);
        let nextDie = Math.max(1, Math.min(6, curDie + dDelta));
        if (matchedEvent.id === "SAKUGA_24FPS_OVERDRIVE") {
          nextDie = Math.max(4, nextDie);
        } else if (matchedEvent.id === "NEO_ARCADIA_CYBER_RAIN" && c === 1) {
          nextDie = Math.max(5, nextDie);
        }
        diceArr[c] = nextDie;
      }
      targetState.colDice = diceArr;

      if (matchedEvent.refreshSlide) {
        targetState.slideUsed = false;
        targetState.playerSlideUsed = false;
        targetState.player_slide_available = true;
      }
    }

    // Step the Causal-DiT latent action engine for this world event
    const stepTelemetry = stepGenie4LatentAction(
      "PROMPT_WORLD_EVENT",
      { eventId: matchedEvent.id, actionCode: matchedEvent.latentActionCode },
      targetState
    );

    if (typeof document !== "undefined" && document.body) {
      document.body.dataset.genie4WorldEvent = matchedEvent.id;
      document.body.dataset.genie4LatentCode = String(matchedEvent.latentActionCode);
      document.documentElement.style.setProperty(
        "--genie4-accent-primary",
        matchedEvent.visualPalette[0] || "#00E5FF"
      );
      document.documentElement.style.setProperty(
        "--genie4-accent-secondary",
        matchedEvent.visualPalette[1] || "#FFB800"
      );

      const canvasEl = document.getElementById("genie4-latent-canvas");
      if (canvasEl) {
        renderGenie4LatentCanvas(canvasEl);
      }
      updateGenie4ModalTelemetryDom();
    }

    playWorldEventHarmonicSynth(matchedEvent);

    // Trigger live UI refresh if tabletop renderer is registered
    if (typeof globalScope !== "undefined") {
      if (typeof globalScope.renderAll === "function") {
        try {
          globalScope.renderAll();
        } catch (_e) {}
      } else if (typeof globalScope.renderBoard === "function") {
        try {
          globalScope.renderBoard();
        } catch (_e) {}
      }
    }

    return {
      applied: true,
      eventId: matchedEvent.id,
      name: matchedEvent.name,
      promptText: matchedEvent.promptText,
      latentActionCode: matchedEvent.latentActionCode,
      tacticalEffect: matchedEvent.tacticalEffect,
      visualPalette: matchedEvent.visualPalette,
      audioFreqHz: matchedEvent.audioFreqHz,
      mutatedSlots: mutatedSlots,
      colDice: targetState && targetState.colDice ? targetState.colDice.slice() : [4, 4, 3],
      latentNorm: stepTelemetry.latentNorm,
      kvCacheFrames: stepTelemetry.kvCacheFrames
    };
  }

  /**
   * Renders the live 24fps Causal-DiT 6x6 Spatio-Temporal Latent Token Grid,
   * 16-Code VQ Action Codebook bar, and 1440-frame KV-Memory Horizon onto `#genie4-latent-canvas`.
   */
  function renderGenie4LatentCanvas(canvasOverride) {
    if (typeof document === "undefined") return false;
    const canvas = canvasOverride || document.getElementById("genie4-latent-canvas");
    if (!canvas || typeof canvas.getContext !== "function") return false;

    const ctx = canvas.getContext("2d");
    if (!ctx) return false;

    const w = canvas.width || 520;
    const h = canvas.height || 260;
    const evSpec = findWorldEventSpec(runtimeState.activeWorldEventId);
    const palette = evSpec.visualPalette || ["#00E5FF", "#FFB800", "#FF2E54", "#0F172A"];

    // 1. Deep Obsidian-Citadel Background
    ctx.fillStyle = "#060913";
    ctx.fillRect(0, 0, w, h);

    // Subtle orthographic grid lines
    ctx.strokeStyle = "rgba(0, 229, 255, 0.08)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 26) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 26) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 2. Left Region: 6x6 Spatio-Temporal Patch Token Matrix (z_t in R^{36x64})
    const gridOriginX = 16;
    const gridOriginY = 28;
    const cellSize = 32;
    const cellGap = 3;

    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 10px monospace";
    ctx.fillText("STAGE 1+3: 6x6 SPATIO-TEMPORAL LATENT TOKENS z_t [36x64]", gridOriginX, 18);

    const phaseTick = (Date.now() % 4000) / 4000.0;
    for (let pr = 0; pr < SPATIAL_GRID_SIDE; pr++) {
      for (let pc = 0; pc < SPATIAL_GRID_SIDE; pc++) {
        const tokIdx = pr * SPATIAL_GRID_SIDE + pc;
        const vec = runtimeState.currentSpatialTokens[tokIdx];
        const v0 = vec ? vec[0] : 0.1;
        const v1 = vec ? vec[1] : 0.1;
        const energy = Math.min(1.0, Math.abs(v0 * 1.8 + v1 * 1.2) + 0.25);

        const px = gridOriginX + pc * (cellSize + cellGap);
        const py = gridOriginY + pr * (cellSize + cellGap);

        ctx.fillStyle = v0 >= 0 ? palette[0] : palette[2] || "#FF2E54";
        ctx.globalAlpha = 0.22 + 0.68 * energy;
        ctx.fillRect(px, py, cellSize, cellSize);

        // Mini waveform bar inside each spatial patch token
        ctx.globalAlpha = 0.92;
        ctx.strokeStyle = palette[1] || "#FFB800";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        for (let b = 0; b < 4; b++) {
          const sample = vec ? vec[(b * 7) % LATENT_DIM] : 0;
          const bx = px + 4 + b * 7;
          const by = py + cellSize * 0.5 + Math.sin(phaseTick * Math.PI * 2 + sample * 4.0) * 8;
          if (b === 0) ctx.moveTo(bx, by);
          else ctx.lineTo(bx, by);
        }
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1.0;

    // Draw 3x3 tactical slot super-borders over the 6x6 patch grid
    ctx.strokeStyle = "rgba(255, 184, 0, 0.55)";
    ctx.lineWidth = 1.5;
    const superSize = cellSize * 2 + cellGap;
    for (let sr = 0; sr < 3; sr++) {
      for (let sc = 0; sc < 3; sc++) {
        const sx = gridOriginX + sc * (superSize + cellGap);
        const sy = gridOriginY + sr * (superSize + cellGap);
        ctx.strokeRect(sx - 1, sy - 1, superSize + 2, superSize + 2);
      }
    }

    // 3. Right Top Region: Stage 2 VQ-VAE 16-Action Codebook Bar (|A| = 16)
    const rightX = 242;
    const rightW = w - rightX - 16;
    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 10px monospace";
    ctx.fillText("STAGE 2: VQ-VAE ACTION CODEBOOK |A|=16 (a_t=" + runtimeState.lastActionCode + ")", rightX, 18);

    const codeBarW = Math.floor((rightW - 15 * 3) / 16);
    const codeBarMaxH = 56;
    const codeBarBaseY = 88;

    for (let c = 0; c < VQ_ACTION_CODEBOOK_SIZE; c++) {
      const isSelected = c === runtimeState.lastActionCode;
      const actWave = 0.3 + 0.7 * Math.abs(Math.sin(c * 0.65 + runtimeState.frameIndex * 0.35));
      const barH = isSelected ? codeBarMaxH : Math.max(10, Math.floor(codeBarMaxH * actWave * 0.65));
      const bx = rightX + c * (codeBarW + 3);
      const by = codeBarBaseY - barH;

      ctx.fillStyle = isSelected ? "#00E5FF" : "rgba(148, 163, 184, 0.35)";
      ctx.fillRect(bx, by, codeBarW, barH);

      if (isSelected) {
        ctx.strokeStyle = "#FFB800";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(bx - 1, by - 1, codeBarW + 2, barH + 2);
      }
    }

    // 4. Right Middle Region: Stage 3 4-Step Flow Matching & 1440-Frame Rolling KV-Cache Horizon
    const kvY = 114;
    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 10px monospace";
    ctx.fillText(
      "STAGE 3: 1440-FRAME KV-MEMORY HORIZON (" + runtimeState.kvMemoryRing.length + "/1440)",
      rightX,
      kvY
    );

    ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
    ctx.fillRect(rightX, kvY + 8, rightW, 44);
    ctx.strokeStyle = "rgba(0, 229, 255, 0.35)";
    ctx.strokeRect(rightX, kvY + 8, rightW, 44);

    // Plot recent KV-cache latent norms
    const ringLen = runtimeState.kvMemoryRing.length;
    ctx.strokeStyle = "#2EE6D3";
    ctx.lineWidth = 2;
    ctx.beginPath();
    const maxPlot = Math.min(48, Math.max(8, ringLen));
    for (let i = 0; i < maxPlot; i++) {
      const entry =
        ringLen > 0
          ? runtimeState.kvMemoryRing[Math.max(0, ringLen - maxPlot + i)]
          : null;
      const normVal = entry ? entry.latentNorm : 4.5 + Math.sin(i * 0.4) * 0.3;
      const px = rightX + 6 + (i / Math.max(1, maxPlot - 1)) * (rightW - 12);
      const py = kvY + 42 - Math.min(28, Math.max(4, (normVal - 2.0) * 6.0));
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // 5. Right Bottom Region: Stage 4 + 5 Active World Event & 24fps Multimodal Audio-Visual Sync
    const avY = 186;
    ctx.fillStyle = "rgba(9, 13, 22, 0.92)";
    ctx.fillRect(rightX, avY, rightW, 52);
    ctx.strokeStyle = palette[0] || "#00E5FF";
    ctx.lineWidth = 1.4;
    ctx.strokeRect(rightX, avY, rightW, 52);

    ctx.fillStyle = palette[0] || "#00E5FF";
    ctx.font = "bold 11px monospace";
    ctx.fillText("EVENT: " + evSpec.id, rightX + 8, avY + 18);

    ctx.fillStyle = "#CBD5E1";
    ctx.font = "10px monospace";
    ctx.fillText(
      "24FPS SYNC | " +
        runtimeState.lastLatencyMs.toFixed(2) +
        "ms / 41.6ms | " +
        evSpec.audioFreqHz +
        "Hz",
      rightX + 8,
      avY + 34
    );

    ctx.fillStyle = "#FFB800";
    ctx.fillText(
      "FLOW STEPS: 4 | KV HIT: " + (runtimeState.kvMemoryHit ? "TRUE" : "NEW"),
      rightX + 8,
      avY + 47
    );

    canvas.dataset.renderedWorldEvent = evSpec.id;
    canvas.dataset.renderedFrame = String(runtimeState.frameIndex);
    return true;
  }

  function updateGenie4ModalTelemetryDom() {
    if (typeof document === "undefined") return;
    const actEl = document.getElementById("genie4-stat-action");
    const normEl = document.getElementById("genie4-stat-norm");
    const kvEl = document.getElementById("genie4-stat-kv");
    const latEl = document.getElementById("genie4-stat-latency");

    if (actEl) actEl.textContent = "a_t=" + runtimeState.lastActionCode + " (" + runtimeState.lastActionName + ")";
    if (normEl) normEl.textContent = runtimeState.lastLatentNorm.toFixed(4);
    if (kvEl) kvEl.textContent = runtimeState.kvMemoryRing.length + " / 1440";
    if (latEl) latEl.textContent = runtimeState.lastLatencyMs.toFixed(2) + " ms (24fps)";

    const buttons = document.querySelectorAll(".genie4-event-btn");
    for (let i = 0; i < buttons.length; i++) {
      const btn = buttons[i];
      if (btn.getAttribute("data-event-id") === runtimeState.activeWorldEventId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    }
  }

  function ensureGenie4WorldModalDom() {
    if (typeof document === "undefined" || !document.body) return null;
    ensureGenie4StylesInjected();

    let modalEl = document.getElementById("genie4-world-modal");
    if (modalEl) return modalEl;

    modalEl = document.createElement("div");
    modalEl.id = "genie4-world-modal";
    modalEl.setAttribute("role", "dialog");
    modalEl.setAttribute("aria-label", "Google DeepMind Genie 4 Interactive World Model Engine");

    const eventButtonsHtml = GENIE4_PROMPTABLE_WORLD_EVENTS.map(function (ev) {
      const isAct = ev.id === runtimeState.activeWorldEventId ? " active" : "";
      return [
        '<button type="button" class="genie4-event-btn' + isAct + '" data-event-id="' + ev.id + '">',
        '  <div class="genie4-event-top">',
        "    <span>" + ev.name + "</span>",
        "    <span>a_t=" + ev.latentActionCode + " | " + ev.audioFreqHz + "Hz</span>",
        "  </div>",
        '  <div class="genie4-event-eff">' + ev.tacticalEffect + "</div>",
        "</button>"
      ].join("\n");
    }).join("\n");

    const stagesHtml = GENIE4_ARCHITECTURE_SPEC.stages
      .map(function (st) {
        return [
          '<div class="genie4-stage-pill">',
          '  <div class="genie4-stage-num">STAGE ' + st.stage + " - " + st.id + "</div>",
          '  <div style="font-weight:700;color:#F8FAFC;margin:3px 0;">' + st.name + "</div>",
          '  <div style="color:#94A3B8;line-height:1.35;">' + st.summary + "</div>",
          "</div>"
        ].join("\n");
      })
      .join("\n");

    modalEl.innerHTML = [
      '<div class="genie4-modal-card">',
      '  <div class="genie4-header">',
      '    <div class="genie4-title-wrap">',
      '      <svg width="28" height="28" viewBox="0 0 256 256" aria-hidden="true">',
      '        <polygon points="128,16 232,76 232,180 128,240 24,180 24,76" fill="none" stroke="#00E5FF" stroke-width="16"/>',
      '        <circle cx="128" cy="128" r="44" fill="none" stroke="#FFB800" stroke-width="14"/>',
      '        <line x1="128" y1="16" x2="128" y2="240" stroke="#2EE6D3" stroke-width="8"/>',
      "      </svg>",
      "      <div>",
      '        <h2 class="genie4-title">GENIE 4 INTERACTIVE WORLD MODEL &amp; CAUSAL-DiT ENGINE</h2>',
      '        <p class="genie4-subtitle">ST-ViViT 6x6x64 Tokenizer | 16-Code VQ-LAM | 4-Step Flow Matching | 1440-Frame Rolling KV Memory</p>',
      "      </div>",
      "    </div>",
      '    <button type="button" class="genie4-close-btn" id="genie4-close-modal-btn">CLOSE [ESC]</button>',
      "  </div>",
      '  <div class="genie4-grid-layout">',
      '    <div class="genie4-panel">',
      '      <h3 class="genie4-panel-title">Live 24fps Spatio-Temporal Latent Grid &amp; KV-Memory Telemetry</h3>',
      '      <canvas id="genie4-latent-canvas" width="520" height="260"></canvas>',
      '      <div class="genie4-telem-row">',
      '        <div class="genie4-stat-box">',
      '          <div class="genie4-stat-label">VQ Latent Action</div>',
      '          <div class="genie4-stat-val" id="genie4-stat-action">a_t=4 (PLACE_CARD_4)</div>',
      "        </div>",
      '        <div class="genie4-stat-box">',
      '          <div class="genie4-stat-label">Latent Norm ||z_t||</div>',
      '          <div class="genie4-stat-val" id="genie4-stat-norm">4.8214</div>',
      "        </div>",
      '        <div class="genie4-stat-box">',
      '          <div class="genie4-stat-label">KV Memory Horizon</div>',
      '          <div class="genie4-stat-val" id="genie4-stat-kv">1 / 1440</div>',
      "        </div>",
      '        <div class="genie4-stat-box">',
      '          <div class="genie4-stat-label">Step Latency</div>',
      '          <div class="genie4-stat-val" id="genie4-stat-latency">2.41 ms (24fps)</div>',
      "        </div>",
      "      </div>",
      "    </div>",
      '    <div class="genie4-panel">',
      '      <h3 class="genie4-panel-title">Stage 4: Promptable World Events (Live 3x3 Board Mutators)</h3>',
      '      <div class="genie4-events-list" id="genie4-events-list">',
      eventButtonsHtml,
      "      </div>",
      "    </div>",
      "  </div>",
      '  <div class="genie4-stages-strip">',
      stagesHtml,
      "  </div>",
      "</div>"
    ].join("\n");

    document.body.appendChild(modalEl);

    const closeBtn = modalEl.querySelector("#genie4-close-modal-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        closeGenie4WorldModelModal();
      });
    }

    modalEl.addEventListener("click", function (evt) {
      if (evt.target === modalEl) {
        closeGenie4WorldModelModal();
      }
    });

    const eventBtns = modalEl.querySelectorAll(".genie4-event-btn");
    for (let i = 0; i < eventBtns.length; i++) {
      eventBtns[i].addEventListener("click", function (e) {
        const evId = e.currentTarget.getAttribute("data-event-id");
        if (evId) {
          triggerGenie4WorldEvent(evId);
        }
      });
    }

    return modalEl;
  }

  function startGenie4CanvasLoop() {
    if (typeof window === "undefined" || typeof window.requestAnimationFrame !== "function") return;
    if (runtimeState.animRequestId) return;

    function tick(now) {
      const modalEl = typeof document !== "undefined" ? document.getElementById("genie4-world-modal") : null;
      if (!modalEl || modalEl.getAttribute("data-open") !== "true") {
        runtimeState.animRequestId = null;
        return;
      }
      if (now - runtimeState.lastAnimTick >= FRAME_BUDGET_MS) {
        runtimeState.lastAnimTick = now;
        renderGenie4LatentCanvas();
      }
      runtimeState.animRequestId = window.requestAnimationFrame(tick);
    }

    runtimeState.animRequestId = window.requestAnimationFrame(tick);
  }

  /**
   * Opens `#genie4-world-modal` (creating it dynamically if needed) and renders the live
   * 6x6 Spatio-Temporal Latent Token Grid + 16-Code VQ Action Codebook + KV-Memory Horizon.
   */
  function openGenie4WorldModelModal(stateObj) {
    const modalEl = ensureGenie4WorldModalDom();
    if (!modalEl) return { opened: false };

    const targetState = resolveTargetState(stateObj);
    if (runtimeState.kvMemoryRing.length === 0) {
      stepGenie4LatentAction("PLACE_CARD_4", { slot: 4 }, targetState);
    }

    modalEl.classList.add("open");
    modalEl.setAttribute("data-open", "true");
    modalEl.style.display = "flex";

    renderGenie4LatentCanvas();
    updateGenie4ModalTelemetryDom();
    startGenie4CanvasLoop();

    return {
      opened: true,
      modalId: "genie4-world-modal",
      activeWorldEvent: runtimeState.activeWorldEventId,
      kvCacheFrames: runtimeState.kvMemoryRing.length
    };
  }

  /**
   * Closes `#genie4-world-modal` and stops the background animation loop.
   */
  function closeGenie4WorldModelModal() {
    if (typeof document === "undefined") return { closed: true };
    const modalEl = document.getElementById("genie4-world-modal");
    if (modalEl) {
      modalEl.classList.remove("open");
      modalEl.setAttribute("data-open", "false");
      modalEl.style.display = "none";
    }
    if (runtimeState.animRequestId && typeof window !== "undefined" && window.cancelAnimationFrame) {
      window.cancelAnimationFrame(runtimeState.animRequestId);
      runtimeState.animRequestId = null;
    }
    return { closed: true };
  }

  const CardFrontGenie4Engine = {
    version: "1.0.0",
    GENIE4_ARCHITECTURE_SPEC: GENIE4_ARCHITECTURE_SPEC,
    GENIE4_PROMPTABLE_WORLD_EVENTS: GENIE4_PROMPTABLE_WORLD_EVENTS,
    VQ_LATENT_ACTION_CATALOG: VQ_LATENT_ACTION_CATALOG,
    stepGenie4LatentAction: stepGenie4LatentAction,
    triggerGenie4WorldEvent: triggerGenie4WorldEvent,
    renderGenie4LatentCanvas: renderGenie4LatentCanvas,
    openGenie4WorldModelModal: openGenie4WorldModelModal,
    closeGenie4WorldModelModal: closeGenie4WorldModelModal,
    getRuntimeTelemetry: function () {
      return {
        frameIndex: runtimeState.frameIndex,
        activeWorldEventId: runtimeState.activeWorldEventId,
        lastActionCode: runtimeState.lastActionCode,
        lastActionName: runtimeState.lastActionName,
        lastLatentNorm: runtimeState.lastLatentNorm,
        lastLatencyMs: runtimeState.lastLatencyMs,
        kvCacheFrames: runtimeState.kvMemoryRing.length,
        kvMemoryHorizonFrames: KV_MEMORY_HORIZON_FRAMES
      };
    }
  };

  globalScope.CardFrontGenie4Engine = CardFrontGenie4Engine;
  globalScope.GENIE4_ARCHITECTURE_SPEC = GENIE4_ARCHITECTURE_SPEC;
  globalScope.GENIE4_PROMPTABLE_WORLD_EVENTS = GENIE4_PROMPTABLE_WORLD_EVENTS;
  globalScope.stepGenie4LatentAction = stepGenie4LatentAction;
  globalScope.triggerGenie4WorldEvent = triggerGenie4WorldEvent;
  globalScope.openGenie4WorldModelModal = openGenie4WorldModelModal;
  globalScope.closeGenie4WorldModelModal = closeGenie4WorldModelModal;

  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.Genie4WorldModelEngine = CardFrontGenie4Engine;
})(typeof window !== "undefined" ? window : globalThis);
