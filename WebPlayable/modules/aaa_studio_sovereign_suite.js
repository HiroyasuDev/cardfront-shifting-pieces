/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes -- AAA Studio Sovereign Suite v1.0
 * Module: WebPlayable/modules/aaa_studio_sovereign_suite.js
 *
 * Self-contained browser module (Zero Generic Unicode Emojis -- all iconography
 * rendered via window.cfIcon(name, size) with inline 256x256 SVGs).
 *
 * Exposes:
 *   1. window.SynapseAlphaZeroMCTS
 *      - PUCT MCTS + Policy-Value Tactical Oracle evaluating live window.state
 *      - Returns { winProbPct, valueScore, topMoves: [{ actionType, label, slotIndex, cardName, expectedGain, visits, qValue }] }
 *      - Interactive MCTS Tactical Oracle modal (openMctsOracleModal())
 *   2. window.SynapseIvaliceChronicleMap
 *      - Interactive SVG 15-Stage Ivalice Overworld Node Map across 3 Acts
 *        (Act I: Sky-Stone Border, Act II: Clockwork Sanctum, Act III: Cradle of Echoes)
 *      - Clicking any of the 15 campaign nodes loads its Boss Commander, Judge Law, and biome
 *   3. window.SynapseReplayGhostLadder
 *      - Deterministic CF-RPL1: replay envelope recorder, serializer/deserializer,
 *        turn-by-turn Sakuga scrubber, 10 Grandmaster Ghost Decks, and 7 Daily Seeded
 *        solve-in-1-turn Lethal Tactical Puzzles (openReplayLadderModal())
 *   4. window.SynapseI18nAccessibility
 *      - Live 10-language AAA localization switcher (EN, JA, KO, ZH-Hans, ZH-Hant,
 *        FR, DE, ES, PT-BR, IT) via setLanguage(langCode)
 *      - 4-mode Colorblind & High-Contrast palette switcher (standard, deuteranopia,
 *        protanopia, tritanopia) via setColorblindMode(mode)
 *   5. window.injectAaaStudioCommandPills()
 *      - Safely injects compact studio pills (MCTS Oracle, 15-Stage Map,
 *        Replay & Puzzles, 10-Lang / A11y) into #sakuga-anim-studio-bar /
 *        #sakuga-anim-engine-bar / #dev-camera-drawer without altering
 *        #board-3d-slab or #standalone-deck-sanctum bounding boxes or E2E tests.
 * ============================================================================ */

(function initAaaStudioSovereignSuite(globalScope) {
  "use strict";

  const SUITE_VERSION = "1.0.0";
  const REPLAY_PREFIX = "CF-RPL1:";

  // ==========================================================================
  // 0. BESPOKE 256x256 INLINE SVG ICON BODIES FOR window.cfIcon(name, size)
  //    (Zero Generic Unicode Emojis)
  // ==========================================================================
  const SOVEREIGN_SUITE_ICONS = {
    globe_i18n:
      '<circle cx="128" cy="128" r="104" fill="#0F172A" stroke="#FFB800" stroke-width="12"/>' +
      '<ellipse cx="128" cy="128" rx="52" ry="102" fill="none" stroke="#00E5FF" stroke-width="9"/>' +
      '<line x1="26" y1="128" x2="230" y2="128" stroke="#00E5FF" stroke-width="9"/>' +
      '<path d="M44,82 C96,98 160,98 212,82" fill="none" stroke="#2EE6D3" stroke-width="8"/>' +
      '<path d="M44,174 C96,158 160,158 212,174" fill="none" stroke="#2EE6D3" stroke-width="8"/>' +
      '<circle cx="128" cy="128" r="14" fill="#FFB800"/>',
    mcts_brain:
      '<polygon points="128,16 226,72 226,184 128,240 30,184 30,72" fill="#0F172A" stroke="#A855F7" stroke-width="12" stroke-linejoin="round"/>' +
      '<line x1="128" y1="52" x2="72" y2="124" stroke="#00E5FF" stroke-width="8"/>' +
      '<line x1="128" y1="52" x2="184" y2="124" stroke="#00E5FF" stroke-width="8"/>' +
      '<line x1="72" y1="124" x2="54" y2="188" stroke="#FFB800" stroke-width="7"/>' +
      '<line x1="72" y1="124" x2="112" y2="188" stroke="#FFB800" stroke-width="7"/>' +
      '<line x1="184" y1="124" x2="144" y2="188" stroke="#2EE6D3" stroke-width="7"/>' +
      '<line x1="184" y1="124" x2="202" y2="188" stroke="#2EE6D3" stroke-width="7"/>' +
      '<circle cx="128" cy="52" r="18" fill="#FFB800" stroke="#FFF3B0" stroke-width="5"/>' +
      '<circle cx="72" cy="124" r="14" fill="#00E5FF"/>' +
      '<circle cx="184" cy="124" r="14" fill="#2EE6D3"/>' +
      '<circle cx="54" cy="188" r="11" fill="#A855F7"/>' +
      '<circle cx="112" cy="188" r="11" fill="#FFB800"/>' +
      '<circle cx="144" cy="188" r="11" fill="#2EE6D3"/>' +
      '<circle cx="202" cy="188" r="11" fill="#00E5FF"/>',
    chronicle_map:
      '<polygon points="24,48 92,28 164,52 232,32 232,208 164,228 92,204 24,224" fill="#0F172A" stroke="#FFB800" stroke-width="12" stroke-linejoin="round"/>' +
      '<line x1="92" y1="28" x2="92" y2="204" stroke="#FFB800" stroke-width="6" stroke-dasharray="10 6"/>' +
      '<line x1="164" y1="52" x2="164" y2="228" stroke="#FFB800" stroke-width="6" stroke-dasharray="10 6"/>' +
      '<polyline points="54,156 112,96 156,144 202,84" fill="none" stroke="#00E5FF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<circle cx="54" cy="156" r="12" fill="#00E5FF"/>' +
      '<circle cx="112" cy="96" r="12" fill="#FFB800"/>' +
      '<circle cx="156" cy="144" r="12" fill="#2EE6D3"/>' +
      '<circle cx="202" cy="84" r="14" fill="#FF2E54" stroke="#FFF3B0" stroke-width="4"/>',
    replay_film:
      '<rect x="24" y="40" width="208" height="176" rx="18" fill="#0F172A" stroke="#2EE6D3" stroke-width="12"/>' +
      '<line x1="24" y1="82" x2="232" y2="82" stroke="#FFB800" stroke-width="6"/>' +
      '<line x1="24" y1="174" x2="232" y2="174" stroke="#FFB800" stroke-width="6"/>' +
      '<polygon points="104,98 172,128 104,158" fill="#FFB800" stroke="#FFF3B0" stroke-width="5" stroke-linejoin="round"/>' +
      '<circle cx="56" cy="61" r="8" fill="#00E5FF"/>' +
      '<circle cx="128" cy="61" r="8" fill="#00E5FF"/>' +
      '<circle cx="200" cy="61" r="8" fill="#00E5FF"/>' +
      '<circle cx="56" cy="195" r="8" fill="#00E5FF"/>' +
      '<circle cx="128" cy="195" r="8" fill="#00E5FF"/>' +
      '<circle cx="200" cy="195" r="8" fill="#00E5FF"/>',
    sword:
      '<line x1="48" y1="208" x2="204" y2="52" stroke="#00E5FF" stroke-width="18" stroke-linecap="round"/>' +
      '<polygon points="176,28 232,24 228,80 184,72" fill="#FFF3B0" stroke="#FFB800" stroke-width="6"/>' +
      '<line x1="68" y1="136" x2="120" y2="188" stroke="#FFB800" stroke-width="16" stroke-linecap="round"/>' +
      '<circle cx="42" cy="214" r="14" fill="#FF2E54" stroke="#FFB800" stroke-width="6"/>',
    shield:
      '<path d="M128,18 L220,56 L220,128 C220,184 178,222 128,242 C78,222 36,184 36,128 L36,56 Z" fill="#0F172A" stroke="#FFB800" stroke-width="12" stroke-linejoin="round"/>' +
      '<polygon points="128,52 156,112 200,128 156,144 128,204 100,144 56,128 100,112" fill="#2EE6D3"/>' +
      '<circle cx="128" cy="128" r="18" fill="#FFB800"/>',
    sparkle:
      '<polygon points="128,14 152,96 238,128 152,160 128,242 104,160 18,128 104,96" fill="#FFB800" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>' +
      '<polygon points="128,56 142,110 196,128 142,146 128,200 114,146 60,128 114,110" fill="#00E5FF"/>' +
      '<circle cx="128" cy="128" r="16" fill="#FFFFFF"/>',
    bolt:
      '<polygon points="146,16 58,136 122,136 96,240 198,112 134,112" fill="#FFB800" stroke="#FFF3B0" stroke-width="8" stroke-linejoin="round"/>' +
      '<polygon points="140,48 84,128 126,128 110,198 172,118 130,118" fill="#00E5FF"/>',
    cube:
      '<polygon points="128,20 228,76 128,132 28,76" fill="#FFB800" stroke="#FFF3B0" stroke-width="6"/>' +
      '<polygon points="28,76 128,132 128,236 28,180" fill="#0F172A" stroke="#FFB800" stroke-width="8"/>' +
      '<polygon points="228,76 128,132 128,236 228,180" fill="#131C31" stroke="#00E5FF" stroke-width="8"/>' +
      '<circle cx="128" cy="76" r="14" fill="#0F172A"/>',
    eye:
      '<path d="M16,128 C52,64 100,44 128,44 C156,44 204,64 240,128 C204,192 156,212 128,212 C100,212 52,192 16,128 Z" fill="#0F172A" stroke="#00E5FF" stroke-width="12" stroke-linejoin="round"/>' +
      '<circle cx="128" cy="128" r="46" fill="#1E293B" stroke="#FFB800" stroke-width="10"/>' +
      '<polygon points="128,96 144,128 128,160 112,128" fill="#00E5FF"/>'
  };

  function registerSovereignIcons() {
    try {
      if (typeof CF_ICON_BODIES === "object" && CF_ICON_BODIES !== null) {
        Object.keys(SOVEREIGN_SUITE_ICONS).forEach(function (k) {
          if (!CF_ICON_BODIES[k]) {
            CF_ICON_BODIES[k] = SOVEREIGN_SUITE_ICONS[k];
          }
        });
      }
    } catch (_) {}

    const prevCfIcon = typeof globalScope.cfIcon === "function" ? globalScope.cfIcon : null;
    if (!prevCfIcon || !prevCfIcon.__aaaStudioIconsRegistered) {
      const wrapped = function cfIcon(name, size, extraStyle) {
        const key = String(name || "sparkle");
        const sz = Number(size) || 14;
        const st = extraStyle ? String(extraStyle) : "";
        if (SOVEREIGN_SUITE_ICONS[key]) {
          return (
            '<svg class="cf-lib-icon" data-icon-id="' + key + '" width="' + sz + '" height="' + sz + '" ' +
            'viewBox="0 0 256 256" fill="none" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0;' + st + '">' +
            SOVEREIGN_SUITE_ICONS[key] + "</svg>"
          );
        }
        if (prevCfIcon) {
          return prevCfIcon(key, sz, st);
        }
        return (
          '<svg class="cf-lib-icon" data-icon-id="' + key + '" width="' + sz + '" height="' + sz + '" ' +
          'viewBox="0 0 256 256" fill="none" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0;' + st + '">' +
          SOVEREIGN_SUITE_ICONS.sparkle + "</svg>"
        );
      };
      wrapped.__aaaStudioIconsRegistered = true;
      wrapped.__sakugaIconsRegistered = Boolean(prevCfIcon && prevCfIcon.__sakugaIconsRegistered);
      globalScope.cfIcon = wrapped;
    }
  }

  registerSovereignIcons();

  function iconHtml(name, size, extraStyle) {
    registerSovereignIcons();
    return globalScope.cfIcon(name, size || 14, extraStyle || "");
  }

  // Deterministic 64-bit FNV-1a hex digest (matches Python Backend)
  function computeFnv1a64Hex(inputStr) {
    const str = String(inputStr || "");
    if (typeof BigInt === "function") {
      let hash = BigInt("0xcbf29ce484222325");
      const prime = BigInt("0x100000001b3");
      const mask64 = BigInt("0xffffffffffffffff");
      for (let i = 0; i < str.length; i++) {
        hash ^= BigInt(str.charCodeAt(i) & 0xff);
        hash = (hash * prime) & mask64;
      }
      return "0x" + hash.toString(16).padStart(16, "0");
    }
    let h1 = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
      h1 ^= str.charCodeAt(i) & 0xff;
      h1 = Math.imul(h1, 0x01000193) >>> 0;
    }
    return "0xcbf29ce4" + h1.toString(16).padStart(8, "0");
  }

  function encodeBase64Url(str) {
    const utf8Bytes = encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function (_, p1) {
      return String.fromCharCode(parseInt(p1, 16));
    });
    const b64 = typeof globalScope.btoa === "function"
      ? globalScope.btoa(utf8Bytes)
      : Buffer.from(str, "utf-8").toString("base64");
    return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  function decodeBase64Url(b64Url) {
    let b64 = String(b64Url || "").replace(/-/g, "+").replace(/_/g, "/");
    while (b64.length % 4 !== 0) {
      b64 += "=";
    }
    const raw = typeof globalScope.atob === "function"
      ? globalScope.atob(b64)
      : Buffer.from(b64, "base64").toString("binary");
    let pct = "";
    for (let i = 0; i < raw.length; i++) {
      pct += "%" + ("00" + raw.charCodeAt(i).toString(16)).slice(-2);
    }
    return decodeURIComponent(pct);
  }

  function resolveCardMetaSafe(cardId) {
    if (typeof globalScope.getCardMeta === "function") {
      const m = globalScope.getCardMeta(cardId);
      if (m) return m;
    }
    const fallbackCatalog = {
      h_archangel: { id: "h_archangel", name: "Solar Archangel", faction: "Solaris", nesw: [8, 7, 6, 7] },
      h_phoenix: { id: "h_phoenix", name: "Phoenix Valkyrie", faction: "Valkyria", nesw: [9, 8, 5, 6] },
      h_oracle: { id: "h_oracle", name: "Lunar Oracle", faction: "Aether", nesw: [7, 7, 8, 7] },
      h_chronos: { id: "h_chronos", name: "Chronos Weaver", faction: "Chronos", nesw: [6, 8, 7, 7] },
      h_seraph: { id: "h_seraph", name: "Astral Seraph", faction: "Abyss", nesw: [8, 6, 7, 8] },
      h_kai: { id: "h_kai", name: "Kai Crimson Visor", faction: "Aether", nesw: [7, 8, 6, 7] },
      h_valkyrie: { id: "h_valkyrie", name: "Sky-Wing Striker", faction: "Valkyria", nesw: [8, 8, 5, 6] },
      h_arbiter: { id: "h_arbiter", name: "Sun Arbiter", faction: "Solaris", nesw: [7, 7, 8, 8] },
      plugin_01_tcg_creative_designer: { id: "plugin_01_tcg_creative_designer", name: "Grand Arcanist of CardCraft", faction: "Aether", nesw: [8, 7, 6, 7] },
      plugin_02_parallel_swarm_orchestrator: { id: "plugin_02_parallel_swarm_orchestrator", name: "Chronos Swarm Commander", faction: "Chronos", nesw: [7, 8, 6, 7] },
      plugin_03_jev_system_one: { id: "plugin_03_jev_system_one", name: "Hallowed Arbiter of System One", faction: "Solaris", nesw: [8, 6, 8, 6] },
      plugin_04_mlx_apple_silicon: { id: "plugin_04_mlx_apple_silicon", name: "A18 Pro Metal Forge Sovereign", faction: "Valkyria", nesw: [7, 7, 7, 7] },
      e_eclipse: { id: "e_eclipse", name: "Eclipse Void Blade", faction: "Abyss", nesw: [6, 6, 5, 6] },
      e_archon: { id: "e_archon", name: "Prism Core Archon", faction: "Solaris", nesw: [7, 6, 6, 5] },
      e_inferno: { id: "e_inferno", name: "Inferno Seraph", faction: "Valkyria", nesw: [7, 7, 5, 6] },
      e_reaper: { id: "e_reaper", name: "Sigil Wraith", faction: "Abyss", nesw: [6, 7, 7, 5] },
      e_titan: { id: "e_titan", name: "Bastion Dreadnought", faction: "Chronos", nesw: [7, 5, 7, 6] },
      e_colossus: { id: "e_colossus", name: "Emerald Colossus", faction: "Aether", nesw: [6, 8, 5, 6] },
      e_cryo: { id: "e_cryo", name: "Cryo Interceptor", faction: "Aether", nesw: [5, 7, 6, 7] },
      e_shinobi: { id: "e_shinobi", name: "Cyber Shinobi", faction: "Chronos", nesw: [7, 6, 6, 5] }
    };
    return fallbackCatalog[cardId] || { id: String(cardId || "h_archangel"), name: String(cardId || "Solar Archangel"), faction: "Solaris", nesw: [7, 7, 7, 7] };
  }

  // ==========================================================================
  // 1. window.SynapseAlphaZeroMCTS -- PUCT MCTS + POLICY-VALUE TACTICAL ORACLE
  // ==========================================================================
  const ORTHO_DIRS = [
    { dr: -1, dc: 0, myEdge: 0, theirEdge: 2, dirName: "N" },
    { dr: 0,  dc: 1, myEdge: 1, theirEdge: 3, dirName: "E" },
    { dr: 1,  dc: 0, myEdge: 2, theirEdge: 0, dirName: "S" },
    { dr: 0,  dc: -1, myEdge: 3, theirEdge: 1, dirName: "W" }
  ];

  function simulateCapturesOnGrid(grid, r, c, nesw, owner, okitsuTieSurge) {
    const captured = [];
    const seen = new Set();
    const occupiedNeighbors = [];

    for (let i = 0; i < ORTHO_DIRS.length; i++) {
      const d = ORTHO_DIRS[i];
      const nr = r + d.dr;
      const nc = c + d.dc;
      if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) {
        const nb = grid[nr] && grid[nr][nc];
        if (nb && nb.cardId && Array.isArray(nb.nesw)) {
          const myVal = Number(nesw[d.myEdge] || 0);
          const theirVal = Number(nb.nesw[d.theirEdge] || 0);
          occupiedNeighbors.push({
            nr: nr,
            nc: nc,
            owner: nb.owner,
            cardId: nb.cardId,
            nesw: nb.nesw.slice(),
            myVal: myVal,
            theirVal: theirVal,
            sum: myVal + theirVal,
            equal: myVal === theirVal,
            dirName: d.dirName
          });
          const beats = okitsuTieSurge ? (myVal >= theirVal) : (myVal > theirVal);
          if (nb.owner && nb.owner !== owner && beats) {
            const key = nr + "," + nc;
            if (!seen.has(key)) {
              seen.add(key);
              captured.push({
                nr: nr,
                nc: nc,
                myVal: myVal,
                theirVal: theirVal,
                dirName: d.dirName,
                rule: (okitsuTieSurge && myVal === theirVal) ? "OKITSU_TIE" : "HIGH_PIP"
              });
            }
          }
        }
      }
    }

    // Evaluate SAME, PLUS, and COMBO_CASCADE
    if (
      globalScope.CardFrontModules &&
      globalScope.CardFrontModules.RulesPlusSame &&
      typeof globalScope.CardFrontModules.RulesPlusSame.evaluatePlusAndSameCaptures === "function"
    ) {
      const sp = globalScope.CardFrontModules.RulesPlusSame.evaluatePlusAndSameCaptures(grid, r, c, nesw, owner);
      if (sp && Array.isArray(sp.allSpecialFlips)) {
        for (let i = 0; i < sp.allSpecialFlips.length; i++) {
          const sf = sp.allSpecialFlips[i];
          const k = sf.nr + "," + sf.nc;
          if (!seen.has(k)) {
            seen.add(k);
            captured.push(sf);
          }
        }
      }
    } else {
      const equalNeighbors = occupiedNeighbors.filter(function (n) { return n.equal; });
      if (equalNeighbors.length >= 2) {
        equalNeighbors.forEach(function (n) {
          if (n.owner !== owner) {
            const k = n.nr + "," + n.nc;
            if (!seen.has(k)) {
              seen.add(k);
              captured.push({ nr: n.nr, nc: n.nc, myVal: n.myVal, theirVal: n.theirVal, dirName: n.dirName, rule: "SAME" });
            }
          }
        });
      }
      const sumMap = {};
      occupiedNeighbors.forEach(function (n) {
        sumMap[n.sum] = sumMap[n.sum] || [];
        sumMap[n.sum].push(n);
      });
      Object.keys(sumMap).forEach(function (sKey) {
        const grp = sumMap[sKey];
        if (grp.length >= 2) {
          grp.forEach(function (n) {
            if (n.owner !== owner) {
              const k = n.nr + "," + n.nc;
              if (!seen.has(k)) {
                seen.add(k);
                captured.push({ nr: n.nr, nc: n.nc, myVal: n.myVal, theirVal: n.theirVal, dirName: n.dirName, rule: "PLUS" });
              }
            }
          });
        }
      });
    }

    return captured;
  }

  function evaluateBoardState(stateObj, options) {
    const st = stateObj || globalScope.state || {};
    const opts = options || {};
    const cPuct = Number(opts.cPuct) || 1.414;
    const simulations = Number(opts.simulations) || 72;

    const grid = Array.isArray(st.grid) && st.grid.length === 3
      ? st.grid
      : [
          [{ r: 0, c: 0, cardId: null, owner: null, nesw: [0, 0, 0, 0] }, { r: 0, c: 1, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] }, { r: 0, c: 2, cardId: null, owner: null, nesw: [0, 0, 0, 0] }],
          [{ r: 1, c: 0, cardId: null, owner: null, nesw: [0, 0, 0, 0] }, { r: 1, c: 1, cardId: null, owner: null, nesw: [0, 0, 0, 0] }, { r: 1, c: 2, cardId: null, owner: null, nesw: [0, 0, 0, 0] }],
          [{ r: 2, c: 0, cardId: null, owner: null, nesw: [0, 0, 0, 0] }, { r: 2, c: 1, cardId: null, owner: null, nesw: [0, 0, 0, 0] }, { r: 2, c: 2, cardId: null, owner: null, nesw: [0, 0, 0, 0] }]
        ];
    const hand = Array.isArray(st.hand) && st.hand.length > 0 ? st.hand : ["h_archangel", "h_phoenix", "h_oracle"];
    const colDice = Array.isArray(st.colDice) && st.colDice.length === 3 ? st.colDice : [4, 2, 5];
    const nudgesLeft = typeof st.nudgesLeft === "number" ? st.nudgesLeft : 2;
    const usedSlide = Boolean(st.usedSlideThisTurn);
    const stageIdx = typeof st.stageIndex === "number" ? st.stageIndex : 0;
    const okitsuTie = Boolean(st.forceOkitsuTieSurge || stageIdx >= 9);
    const mnemosyneCenter = stageIdx >= 3;

    let blueBefore = 0;
    let redBefore = 0;
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const cell = grid[r] && grid[r][c];
        if (cell && cell.owner === "player") blueBefore++;
        else if (cell && cell.owner === "ai") redBefore++;
      }
    }

    const candidates = [];

    // 1. Evaluate all Hand -> Open Socket deployments (and Nudge+Deploy when colDice[c] === 3)
    for (let hIdx = 0; hIdx < hand.length; hIdx++) {
      const cid = hand[hIdx];
      const meta = resolveCardMetaSafe(cid);
      const baseNesw = Array.isArray(meta.nesw) ? meta.nesw : [7, 7, 7, 7];

      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const cell = grid[r] && grid[r][c];
          if (cell && cell.cardId) continue;

          const slotIndex = r * 3 + c;
          const colBoost = colDice[c] >= 4 ? 1 : 0;
          const centerBoost = (mnemosyneCenter && r === 1 && c === 1) ? 1 : 0;
          const effNesw = baseNesw.map(function (v) { return Math.min(9, Number(v) + colBoost + centerBoost); });

          const flips = simulateCapturesOnGrid(grid, r, c, effNesw, "player", okitsuTie);
          let factionLinks = 0;
          let exposedEdgeSafety = 0;
          let exposedCount = 0;

          for (let dIdx = 0; dIdx < ORTHO_DIRS.length; dIdx++) {
            const d = ORTHO_DIRS[dIdx];
            const nr = r + d.dr;
            const nc = c + d.dc;
            if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) {
              const nb = grid[nr] && grid[nr][nc];
              if (nb && nb.cardId && nb.owner === "player") {
                const nbMeta = resolveCardMetaSafe(nb.cardId);
                if (nbMeta && nbMeta.faction && nbMeta.faction === meta.faction) {
                  factionLinks++;
                }
              } else if (!nb || !nb.cardId) {
                exposedCount++;
                exposedEdgeSafety += effNesw[d.myEdge] / 9.0;
              }
            }
          }

          const safetyAvg = exposedCount > 0 ? (exposedEdgeSafety / exposedCount) : 1.0;
          const disruptBonus = (st.bossTargetSlot && st.bossTargetSlot.r === r && st.bossTargetSlot.c === c) ? 0.42 : 0.0;
          const posBonus = (r === 1 && c === 1) ? (mnemosyneCenter ? 0.35 : 0.16) : ((r !== 1 && c !== 1) ? 0.14 : 0.06);
          const specialRuleBonus = flips.some(function (f) { return f.rule && f.rule !== "HIGH_PIP"; }) ? 0.32 : 0.0;
          const expectedGain = Number(
            (flips.length * 1.45 + factionLinks * 0.28 + safetyAvg * 0.48 + disruptBonus + posBonus + specialRuleBonus).toFixed(3)
          );

          const rulesList = Array.from(new Set(flips.map(function (f) { return f.rule || "HIGH_PIP"; })));
          candidates.push({
            actionType: "DEPLOY",
            label: "Deploy " + meta.name + " -> Socket (" + (r + 1) + "," + (c + 1) + ")" + (flips.length > 0 ? " [" + flips.length + " Flip]" : ""),
            slotIndex: slotIndex,
            r: r,
            c: c,
            handIndex: hIdx,
            cardId: cid,
            cardName: meta.name,
            expectedGain: expectedGain,
            flipsCount: flips.length,
            rulesTriggered: rulesList,
            nudgeCol: null,
            fromSlot: null
          });

          // Evaluate NUDGE_AND_DEPLOY if colDice[c] === 3 and nudgesLeft > 0
          if (nudgesLeft > 0 && colDice[c] === 3) {
            const nudgedNesw = baseNesw.map(function (v) { return Math.min(9, Number(v) + 1 + centerBoost); });
            const nudgedFlips = simulateCapturesOnGrid(grid, r, c, nudgedNesw, "player", okitsuTie);
            if (nudgedFlips.length > flips.length) {
              const nGain = Number((expectedGain + (nudgedFlips.length - flips.length) * 1.55 + 0.25).toFixed(3));
              candidates.push({
                actionType: "NUDGE_AND_DEPLOY",
                label: "Nudge Col " + (c + 1) + " Die (+1) & Deploy " + meta.name + " -> (" + (r + 1) + "," + (c + 1) + ") [" + nudgedFlips.length + " Flip]",
                slotIndex: slotIndex,
                r: r,
                c: c,
                handIndex: hIdx,
                cardId: cid,
                cardName: meta.name,
                expectedGain: nGain,
                flipsCount: nudgedFlips.length,
                rulesTriggered: Array.from(new Set(nudgedFlips.map(function (f) { return f.rule || "HIGH_PIP"; }))),
                nudgeCol: c,
                fromSlot: null
              });
            }
          }
        }
      }
    }

    // 2. Evaluate Tactical Slide moves for placed player cards
    if (!usedSlide) {
      for (let sr = 0; sr < 3; sr++) {
        for (let sc = 0; sc < 3; sc++) {
          const srcCell = grid[sr] && grid[sr][sc];
          if (!srcCell || !srcCell.cardId || srcCell.owner !== "player") continue;
          const srcMeta = resolveCardMetaSafe(srcCell.cardId);
          for (let dIdx = 0; dIdx < ORTHO_DIRS.length; dIdx++) {
            const d = ORTHO_DIRS[dIdx];
            const tr = sr + d.dr;
            const tc = sc + d.dc;
            if (tr >= 0 && tr < 3 && tc >= 0 && tc < 3) {
              const dstCell = grid[tr] && grid[tr][tc];
              if (dstCell && !dstCell.cardId) {
                const colBoost = colDice[tc] >= 4 ? 1 : 0;
                const slideNesw = (srcMeta.nesw || [7, 7, 7, 7]).map(function (v) { return Math.min(9, Number(v) + colBoost); });
                const sFlips = simulateCapturesOnGrid(grid, tr, tc, slideNesw, "player", okitsuTie);
                if (sFlips.length > 0) {
                  const sGain = Number((sFlips.length * 1.52 + 0.35).toFixed(3));
                  candidates.push({
                    actionType: "SLIDE",
                    label: "Tactical Slide " + srcMeta.name + " (" + (sr + 1) + "," + (sc + 1) + ") -> (" + (tr + 1) + "," + (tc + 1) + ") [" + sFlips.length + " Flip]",
                    slotIndex: tr * 3 + tc,
                    r: tr,
                    c: tc,
                    handIndex: -1,
                    cardId: srcCell.cardId,
                    cardName: srcMeta.name,
                    expectedGain: sGain,
                    flipsCount: sFlips.length,
                    rulesTriggered: Array.from(new Set(sFlips.map(function (f) { return f.rule || "HIGH_PIP"; }))),
                    nudgeCol: null,
                    fromSlot: sr * 3 + sc
                  });
                }
              }
            }
          }
        }
      }
    }

    if (candidates.length === 0) {
      return {
        winProbPct: blueBefore >= redBefore ? 65.0 : 35.0,
        valueScore: blueBefore >= redBefore ? 0.3 : -0.3,
        simulationsRun: 0,
        cPuct: cPuct,
        topMoves: []
      };
    }

    // Compute Policy Network Softmax Prior P(s, a)
    let maxGain = -Infinity;
    for (let i = 0; i < candidates.length; i++) {
      if (candidates[i].expectedGain > maxGain) maxGain = candidates[i].expectedGain;
    }
    let expSum = 0;
    const expVals = candidates.map(function (m) {
      const ev = Math.exp((m.expectedGain - maxGain) * 1.35);
      expSum += ev;
      return ev;
    });
    for (let i = 0; i < candidates.length; i++) {
      candidates[i].priorProb = Number((expVals[i] / (expSum || 1)).toFixed(4));
      candidates[i].visits = 0;
      candidates[i].valueSum = 0;
      candidates[i].qValue = 0;
    }

    // Run PUCT MCTS simulations: UCB = Q(s,a) + c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
    const scoreLeadBias = (blueBefore - redBefore) * 0.14;
    for (let sim = 1; sim <= simulations; sim++) {
      let bestCand = candidates[0];
      let bestPuctScore = -Infinity;
      const sqrtTotal = Math.sqrt(sim);

      for (let i = 0; i < candidates.length; i++) {
        const m = candidates[i];
        const u = cPuct * m.priorProb * (sqrtTotal / (1 + m.visits));
        const puct = m.qValue + u;
        if (puct > bestPuctScore) {
          bestPuctScore = puct;
          bestCand = m;
        }
      }

      // Deterministic leaf evaluation via hyperbolic tangent value head
      const waveNoise = Math.sin(sim * 1.6180339 + bestCand.slotIndex) * 0.025;
      const leafValue = Math.tanh((bestCand.expectedGain - 0.55) * 0.52 + scoreLeadBias + waveNoise);
      bestCand.visits += 1;
      bestCand.valueSum += leafValue;
      bestCand.qValue = Number((bestCand.valueSum / bestCand.visits).toFixed(4));
    }

    candidates.sort(function (a, b) {
      if (b.visits !== a.visits) return b.visits - a.visits;
      if (b.qValue !== a.qValue) return b.qValue - a.qValue;
      return b.expectedGain - a.expectedGain;
    });

    const topMoves = candidates.slice(0, 6).map(function (m) {
      return {
        actionType: m.actionType,
        label: m.label,
        slotIndex: m.slotIndex,
        r: m.r,
        c: m.c,
        handIndex: m.handIndex,
        cardId: m.cardId,
        cardName: m.cardName,
        expectedGain: m.expectedGain,
        visits: m.visits,
        qValue: m.qValue,
        priorProb: m.priorProb,
        flipsCount: m.flipsCount,
        rulesTriggered: m.rulesTriggered,
        nudgeCol: m.nudgeCol,
        fromSlot: m.fromSlot
      };
    });

    const bestQ = topMoves[0] ? topMoves[0].qValue : 0;
    const rawWinProb = 50.0 + bestQ * 46.5;
    const winProbPct = Number(Math.max(2.5, Math.min(99.4, rawWinProb)).toFixed(1));

    const result = {
      winProbPct: winProbPct,
      valueScore: Number(bestQ.toFixed(4)),
      simulationsRun: simulations,
      cPuct: cPuct,
      topMoves: topMoves
    };
    SynapseAlphaZeroMCTS.lastEvaluation = result;
    return result;
  }

  function executeRecommendedMove(moveIdx) {
    const evalRes = SynapseAlphaZeroMCTS.lastEvaluation || evaluateBoardState(globalScope.state);
    const move = evalRes.topMoves[Number(moveIdx) || 0];
    if (!move || !globalScope.state) return null;

    closeMctsOracleModal();
    if (move.actionType === "NUDGE_AND_DEPLOY" && typeof move.nudgeCol === "number") {
      if (typeof globalScope.nudgeColDie === "function") {
        globalScope.nudgeColDie(move.nudgeCol);
      }
    }
    if (move.actionType === "SLIDE" && typeof move.fromSlot === "number") {
      const sr = Math.floor(move.fromSlot / 3);
      const sc = move.fromSlot % 3;
      if (typeof globalScope.handleSlotClick === "function") {
        globalScope.handleSlotClick(sr, sc);
        globalScope.handleSlotClick(move.r, move.c);
      }
      return move;
    }

    if (typeof move.handIndex === "number" && move.handIndex >= 0) {
      globalScope.state.selectedHandIdx = move.handIndex;
      globalScope.state.selectedBoardSlot = null;
    }
    if (typeof globalScope.handleSlotClick === "function") {
      globalScope.handleSlotClick(move.r, move.c);
    }
    return move;
  }

  function highlightRecommendedSocket(slotIndex) {
    const idx = Number(slotIndex) || 0;
    const r = Math.floor(idx / 3);
    const c = idx % 3;
    if (globalScope.state) {
      globalScope.state.hoveredSlot = { r: r, c: c };
      globalScope.state.focusedSlotIndex = idx;
      if (typeof globalScope.renderAll === "function") globalScope.renderAll();
    }
    closeMctsOracleModal();
  }

  function ensureMctsOracleModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("mcts-oracle-modal");
    if (!modal) {
      modal = doc.createElement("div");
      modal.id = "mcts-oracle-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.style.cssText = "display:none;z-index:135;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function openMctsOracleModal() {
    const modal = ensureMctsOracleModalDom();
    if (!modal) return null;
    const evalRes = evaluateBoardState(globalScope.state);
    const i18n = globalScope.SynapseI18nAccessibility;
    const titleStr = i18n ? i18n.t("mcts_oracle") : "AlphaZero MCTS Oracle";

    const rowsHtml = evalRes.topMoves.map(function (m, idx) {
      const qPct = Math.round((m.qValue + 1) * 50);
      const badgeColor = idx === 0 ? "#FFB800" : "#00E5FF";
      const rulesBadge = m.rulesTriggered && m.rulesTriggered.length
        ? '<span style="color:#2EE6D3;font-weight:800;margin-left:6px;">[' + m.rulesTriggered.join("+") + ']</span>'
        : "";
      return (
        '<div class="mcts-move-row" data-move-idx="' + idx + '" style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;' +
        'background:rgba(15,23,42,0.92);border:1.5px solid ' + badgeColor + ';border-radius:8px;padding:8px 10px;font-size:12px;">' +
        '<div style="min-width:0;flex:1;">' +
        '<div style="font-weight:900;color:' + badgeColor + ';font-size:12px;">#' + (idx + 1) + ' [' + m.actionType + '] ' + m.label + rulesBadge + '</div>' +
        '<div style="color:#cbd5e1;font-family:ui-monospace,monospace;font-size:12px;margin-top:2px;">' +
        'Socket #' + m.slotIndex + ' | Visits: <b>' + m.visits + '</b> | Q-Value: <b>' + m.qValue + '</b> (' + qPct + '%) | Prior P: <b>' + m.priorProb + '</b> | Expected Gain: <b>+' + m.expectedGain + '</b>' +
        '</div></div>' +
        '<div style="display:flex;gap:6px;align-items:center;">' +
        '<button type="button" onclick="window.SynapseAlphaZeroMCTS.highlightRecommendedSocket(' + m.slotIndex + ')" style="font-size:12px;padding:4px 8px;border-color:#00E5FF;color:#00E5FF;">' +
        iconHtml("eye", 13, "margin-right:4px;") + 'Preview</button>' +
        '<button type="button" onclick="window.SynapseAlphaZeroMCTS.executeRecommendedMove(' + idx + ')" style="font-size:12px;padding:4px 10px;background:linear-gradient(135deg,#0284c7,#1d4ed8);border-color:#FFB800;color:#fff;">' +
        iconHtml("bolt", 13, "margin-right:4px;") + 'Execute</button>' +
        '</div></div>'
      );
    }).join("");

    modal.innerHTML =
      '<div class="modal-box" style="max-width:760px;width:95%;max-height:86vh;overflow-y:auto;text-align:left;transform:none;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;flex-wrap:wrap;gap:8px;">' +
      '<div>' +
      '<div style="font-size:12px;font-weight:900;color:#A855F7;letter-spacing:1px;">' + iconHtml("mcts_brain", 15, "margin-right:5px;") + 'PUCT ALPHAZERO POLICY-VALUE TACTICAL ENGINE</div>' +
      '<h3 style="font-size:18px;font-weight:900;color:#fff;">' + titleStr + ' (Win Prob: <span style="color:#FFB800;">' + evalRes.winProbPct + '%</span>)</h3>' +
      '</div>' +
      '<button type="button" onclick="window.SynapseAlphaZeroMCTS.closeMctsOracleModal()">Close</button>' +
      '</div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;background:#070c18;border:1px solid rgba(168,85,247,0.45);border-radius:8px;padding:8px 12px;font-size:12px;color:#e2e8f0;">' +
      '<span>Win Probability: <b style="color:#00E5FF;font-size:14px;">' + evalRes.winProbPct + '%</b></span>' +
      '<span>Value Net V(s): <b style="color:#FFB800;">' + evalRes.valueScore + '</b></span>' +
      '<span>PUCT Rollouts: <b style="color:#2EE6D3;">' + evalRes.simulationsRun + ' sims (c_puct=' + evalRes.cPuct + ')</b></span>' +
      '</div>' +
      '<div style="display:flex;flex-direction:column;gap:8px;margin-top:4px;">' + rowsHtml + '</div>' +
      '</div>';

    modal.style.display = "flex";
    return evalRes;
  }

  function closeMctsOracleModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("mcts-oracle-modal");
    if (modal) modal.style.display = "none";
  }

  const SynapseAlphaZeroMCTS = {
    VERSION: SUITE_VERSION,
    C_PUCT: 1.414,
    DEFAULT_SIMULATIONS: 72,
    lastEvaluation: null,
    evaluateBoardState: evaluateBoardState,
    evaluate: evaluateBoardState,
    searchBestMoves: evaluateBoardState,
    openMctsOracleModal: openMctsOracleModal,
    closeMctsOracleModal: closeMctsOracleModal,
    executeRecommendedMove: executeRecommendedMove,
    highlightRecommendedSocket: highlightRecommendedSocket
  };

  // ==========================================================================
  // 2. window.SynapseIvaliceChronicleMap -- 15-STAGE OVERWORLD NODE GRAPH
  // ==========================================================================
  const CHRONICLE_ACTS = [
    { actId: "ACT_I", actNumber: 1, title: "Act I: Sky-Stone Border", i18nKey: "act_1_title", stageRange: [0, 4], color: "#00E5FF" },
    { actId: "ACT_II", actNumber: 2, title: "Act II: Clockwork Sanctum", i18nKey: "act_2_title", stageRange: [5, 9], color: "#FFB800" },
    { actId: "ACT_III", actNumber: 3, title: "Act III: Cradle of Echoes", i18nKey: "act_3_title", stageRange: [10, 14], color: "#FF2E54" }
  ];

  const CHRONICLE_STAGES_15 = [
    {
      stageIndex: 0, stageId: "stage_01", actId: "ACT_I", actTitle: "Act I: Sky-Stone Border",
      name: "Act I-1: Skystone Sanctuary", biome: "Sky-Stone Border",
      bg: "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
      x: 70, y: 210, edges: [1, 2],
      bossId: "e_eclipse", bossName: "Eclipse Void Blade", avatar: "./GeneratedArt/MasteredCards/e_eclipse.png?v=tele4",
      aiBonus: 0, rewardCoins: 80,
      judgeLaw: { lawId: "STANDARD_HIGH_PIP", bannerKey: "judge_law_standard", name: "High-Pip & Faction Link Decree", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_01_skystone_compass", name: "Skystone Astrolabe Compass", effect: "+1 Starting Column Die Nudge" }
    },
    {
      stageIndex: 1, stageId: "stage_02", actId: "ACT_I", actTitle: "Act I: Sky-Stone Border",
      name: "Act I-2: Ivalice Citadel", biome: "Sky-Stone Border",
      bg: "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
      x: 150, y: 115, edges: [3],
      bossId: "e_archon", bossName: "Prism Core Archon", avatar: "./GeneratedArt/MasteredCards/e_archon.png?v=tele4",
      aiBonus: 0, rewardCoins: 90,
      judgeLaw: { lawId: "SAME_PLUS_CASCADE", bannerKey: "judge_law_same_plus", name: "Ivalice Same / Plus & Combo Cascade", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_02_citadel_signet", name: "Citadel Judge Signet", effect: "+25 Bonus Coins on SAME/PLUS" }
    },
    {
      stageIndex: 2, stageId: "stage_03", actId: "ACT_I", actTitle: "Act I: Sky-Stone Border",
      name: "Act I-3: Solar Spire", biome: "Sky-Stone Border",
      bg: "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
      x: 150, y: 305, edges: [3, 4],
      bossId: "e_cryo", bossName: "Cryo Interceptor", avatar: "./GeneratedArt/MasteredCards/e_cryo.png?v=tele4",
      aiBonus: 1, rewardCoins: 100,
      judgeLaw: { lawId: "STANDARD_HIGH_PIP", bannerKey: "judge_law_standard", name: "Solaris High-Pip Decree", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_03_solar_sunstone", name: "Sunstone Prism Lens", effect: "Col 1 Die starts at Pip 4+" }
    },
    {
      stageIndex: 3, stageId: "stage_04", actId: "ACT_I", actTitle: "Act I: Sky-Stone Border",
      name: "Act I-4: Windmill Bastion", biome: "Sky-Stone Border",
      bg: "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
      x: 240, y: 155, edges: [4, 5],
      bossId: "e_shinobi", bossName: "Cyber Shinobi", avatar: "./GeneratedArt/MasteredCards/e_shinobi.png?v=tele4",
      aiBonus: 1, rewardCoins: 110,
      judgeLaw: { lawId: "SAME_PLUS_CASCADE", bannerKey: "judge_law_same_plus", name: "Windmill Tactical Slide Law", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_04_zephyr_pinion", name: "Zephyr Windmill Pinion", effect: "Tactical Slide +1 E/W Guard" }
    },
    {
      stageIndex: 4, stageId: "stage_05", actId: "ACT_I", actTitle: "Act I: Sky-Stone Border",
      name: "Act I-5: Aetherial Sky-Bridge", biome: "Sky-Stone Border",
      bg: "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
      x: 315, y: 265, edges: [5, 6],
      bossId: "e_colossus", bossName: "Emerald Colossus", avatar: "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
      aiBonus: 1, rewardCoins: 120,
      judgeLaw: { lawId: "STANDARD_HIGH_PIP", bannerKey: "judge_law_standard", name: "Sky-Bridge Border Warden Law", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_05_aether_keystone", name: "Aetherial Bridge Keystone", effect: "Unlocks Act II & +1 Reroll" }
    },
    {
      stageIndex: 5, stageId: "stage_06", actId: "ACT_II", actTitle: "Act II: Clockwork Sanctum",
      name: "Act II-6: Clockwork Sanctum Gate", biome: "Clockwork Sanctum",
      bg: "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
      x: 405, y: 130, edges: [6, 7],
      bossId: "e_titan", bossName: "Bastion Dreadnought", avatar: "./GeneratedArt/MasteredCards/e_titan.png?v=tele4",
      aiBonus: 1, rewardCoins: 130,
      judgeLaw: { lawId: "MNEMOSYNE_NODE_RESONANCE", bannerKey: "judge_law_mnemosyne", name: "Mnemosyne Center Sanctum (+1 All & +50G)", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_06_chronos_escapement", name: "Brass Escapement Gear", effect: "Center Socket (2,2) +1 All Stats" }
    },
    {
      stageIndex: 6, stageId: "stage_07", actId: "ACT_II", actTitle: "Act II: Clockwork Sanctum",
      name: "Act II-7: Orbital Mecha Bay", biome: "Clockwork Sanctum",
      bg: "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
      x: 475, y: 295, edges: [7, 8],
      bossId: "e_colossus", bossName: "Emerald Colossus", avatar: "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
      aiBonus: 1, rewardCoins: 140,
      judgeLaw: { lawId: "MNEMOSYNE_NODE_RESONANCE", bannerKey: "judge_law_mnemosyne", name: "Orbital Resonance Law", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_07_orbital_gyro", name: "Orbital Gyroscope Core", effect: "+1 N/E on Valkyria & Chronos" }
    },
    {
      stageIndex: 7, stageId: "stage_08", actId: "ACT_II", actTitle: "Act II: Clockwork Sanctum",
      name: "Act II-8: Solid Eye Bunker", biome: "Clockwork Sanctum",
      bg: "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
      x: 550, y: 195, edges: [8, 9],
      bossId: "e_shinobi", bossName: "Cyber Shinobi", avatar: "./GeneratedArt/MasteredCards/e_shinobi.png?v=tele4",
      aiBonus: 1, rewardCoins: 150,
      judgeLaw: { lawId: "SAME_PLUS_CASCADE", bannerKey: "judge_law_same_plus", name: "Solid Eye Halftone Decree", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_08_solideye_visor", name: "MGA2 Tactical Visor Lens", effect: "Reveals Top MCTS Oracle Line" }
    },
    {
      stageIndex: 8, stageId: "stage_09", actId: "ACT_II", actTitle: "Act II: Clockwork Sanctum",
      name: "Act II-9: STACCS Chrono Spire", biome: "Clockwork Sanctum",
      bg: "./GeneratedArt/env_breach_staccs_isometric_tower.png",
      x: 625, y: 115, edges: [9, 10],
      bossId: "e_reaper", bossName: "Sigil Wraith", avatar: "./GeneratedArt/MasteredCards/e_reaper.png?v=tele4",
      aiBonus: 1, rewardCoins: 165,
      judgeLaw: { lawId: "MNEMOSYNE_NODE_RESONANCE", bannerKey: "judge_law_mnemosyne", name: "STACCS Column Conduit Law", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_09_staccs_die_matrix", name: "STACCS Brass Die Matrix", effect: "Pip 6 Die triggers Sakuga Surge" }
    },
    {
      stageIndex: 9, stageId: "stage_10", actId: "ACT_II", actTitle: "Act II: Clockwork Sanctum",
      name: "Act II-10: Mnemosyne Gear Vault", biome: "Clockwork Sanctum",
      bg: "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
      x: 635, y: 300, edges: [10, 11],
      bossId: "e_inferno", bossName: "Inferno Seraph", avatar: "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
      aiBonus: 1, rewardCoins: 180,
      judgeLaw: { lawId: "MNEMOSYNE_NODE_RESONANCE", bannerKey: "judge_law_mnemosyne", name: "Mnemosyne Sovereign Vault Law", okitsuTieSurge: false },
      rewardRelic: { relicId: "relic_10_mnemosyne_pendulum", name: "Mnemosyne Golden Pendulum", effect: "Unlocks Act III Cradle of Echoes" }
    },
    {
      stageIndex: 10, stageId: "stage_11", actId: "ACT_III", actTitle: "Act III: Cradle of Echoes",
      name: "Act III-11: Breach Rift Alpha", biome: "Cradle of Echoes",
      bg: "./GeneratedArt/env_breach_staccs_isometric_tower.png",
      x: 725, y: 185, edges: [11, 12],
      bossId: "e_inferno", bossName: "Inferno Seraph", avatar: "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
      aiBonus: 1, rewardCoins: 195,
      judgeLaw: { lawId: "OKITSU_TIE_SURGE", bannerKey: "judge_law_okitsu", name: "Okitsu Tie-Surge (Equal Pips Capture)", okitsuTieSurge: true },
      rewardRelic: { relicId: "relic_11_breach_capacitor", name: "Breach Rift Capacitor", effect: "Equal Edge Pips Capture Enemies" }
    },
    {
      stageIndex: 11, stageId: "stage_12", actId: "ACT_III", actTitle: "Act III: Cradle of Echoes",
      name: "Act III-12: Umbra Singularity", biome: "Cradle of Echoes",
      bg: "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
      x: 785, y: 305, edges: [12, 13],
      bossId: "e_eclipse", bossName: "Eclipse Void Blade", avatar: "./GeneratedArt/MasteredCards/e_eclipse.png?v=tele4",
      aiBonus: 1, rewardCoins: 210,
      judgeLaw: { lawId: "OKITSU_TIE_SURGE", bannerKey: "judge_law_okitsu", name: "Umbra Tie-Surge & Void Law", okitsuTieSurge: true },
      rewardRelic: { relicId: "relic_12_umbra_sigil", name: "Umbra Singularity Sigil", effect: "Abyss & Aether +1 Corner Edge" }
    },
    {
      stageIndex: 12, stageId: "stage_13", actId: "ACT_III", actTitle: "Act III: Cradle of Echoes",
      name: "Act III-13: Prism Octahedron", biome: "Cradle of Echoes",
      bg: "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
      x: 840, y: 120, edges: [13, 14],
      bossId: "e_archon", bossName: "Prism Core Archon", avatar: "./GeneratedArt/MasteredCards/e_archon.png?v=tele4",
      aiBonus: 2, rewardCoins: 230,
      judgeLaw: { lawId: "OKITSU_TIE_SURGE", bannerKey: "judge_law_okitsu", name: "Prism Octahedron Law", okitsuTieSurge: true },
      rewardRelic: { relicId: "relic_13_prism_octahedron", name: "Refractive Octahedron Core", effect: "Sovereign Plugins +1 Faction Link" }
    },
    {
      stageIndex: 13, stageId: "stage_14", actId: "ACT_III", actTitle: "Act III: Cradle of Echoes",
      name: "Act III-14: Trigger Cross-Star", biome: "Cradle of Echoes",
      bg: "./GeneratedArt/env_breach_staccs_isometric_tower.png",
      x: 880, y: 275, edges: [14],
      bossId: "e_colossus", bossName: "Emerald Colossus", avatar: "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
      aiBonus: 2, rewardCoins: 255,
      judgeLaw: { lawId: "OKITSU_TIE_SURGE", bannerKey: "judge_law_okitsu", name: "Trigger 24fps Sakuga Law", okitsuTieSurge: true },
      rewardRelic: { relicId: "relic_14_trigger_star_core", name: "Studio Trigger Cross-Star Crest", effect: "Corner Deploy 2F Impact Flash" }
    },
    {
      stageIndex: 14, stageId: "stage_15", actId: "ACT_III", actTitle: "Act III: Cradle of Echoes",
      name: "Act III-15: Omega Chronos Prime", biome: "Cradle of Echoes",
      bg: "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
      x: 945, y: 205, edges: [],
      bossId: "e_inferno", bossName: "Inferno Seraph (Omega Chronos Prime)", avatar: "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
      aiBonus: 2, rewardCoins: 300,
      judgeLaw: { lawId: "OKITSU_TIE_SURGE", bannerKey: "judge_law_okitsu", name: "Omega Sovereign Finale Law", okitsuTieSurge: true },
      rewardRelic: { relicId: "relic_15_crown_of_echoes", name: "Sovereign Crown of Echoes", effect: "Completes 15-Stage Ivalice Chronicle" }
    }
  ];

  function getStageNode(stageIdx) {
    const idx = Math.max(0, Math.min(14, Number(stageIdx) || 0));
    return CHRONICLE_STAGES_15[idx];
  }

  function loadChronicleStage(stageIdx) {
    const node = getStageNode(stageIdx);
    if (!node) return null;

    if (globalScope.state) {
      globalScope.state.stageIndex = node.stageIndex;
      globalScope.state.activeJudgeLaw = node.judgeLaw;
      globalScope.state.activeRewardRelic = node.rewardRelic;
      globalScope.state.forceOkitsuTieSurge = Boolean(node.judgeLaw.okitsuTieSurge);
    }

    if (typeof globalScope.startStage === "function") {
      globalScope.startStage(node.stageIndex);
    }

    if (globalScope.state) {
      globalScope.state.activeJudgeLaw = node.judgeLaw;
      globalScope.state.forceOkitsuTieSurge = Boolean(node.judgeLaw.okitsuTieSurge);
    }

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      const stageSel = doc.getElementById("stage-select");
      if (stageSel) stageSel.value = String(node.stageIndex);

      const i18n = globalScope.SynapseI18nAccessibility;
      const localizedStageTitle = i18n ? i18n.t(node.stageId, node.name) : node.name;
      const localizedLawBanner = i18n ? i18n.t(node.judgeLaw.bannerKey, node.judgeLaw.name) : node.judgeLaw.name;

      const bossNameEl = doc.getElementById("boss-name");
      if (bossNameEl) bossNameEl.textContent = localizedStageTitle;
      const crestNameEl = doc.getElementById("boss-crest-name");
      if (crestNameEl) crestNameEl.textContent = node.bossName.toUpperCase() + " (" + node.biome.toUpperCase() + ")";
      const crestAvEl = doc.getElementById("boss-crest-avatar");
      if (crestAvEl) crestAvEl.src = node.avatar;
      const teleDescEl = doc.getElementById("telegraph-hud-desc");
      if (teleDescEl) {
        teleDescEl.textContent = localizedLawBanner + " | Relic: " + node.rewardRelic.name + " (" + node.rewardRelic.effect + ")";
      }
      if (doc.body && node.bg) {
        doc.body.style.backgroundImage =
          'radial-gradient(circle at 50% 42%, rgba(16, 28, 58, 0.45) 0%, rgba(4, 7, 15, 0.92) 84%), url("' + node.bg + '")';
      }
    }

    closeChronicleMapModal();
    return node;
  }

  function buildChronicleSvgGraphHtml(activeStageIdx, clearedStages) {
    const clearedSet = new Set(Array.isArray(clearedStages) ? clearedStages : []);
    let edgesSvg = "";
    for (let i = 0; i < CHRONICLE_STAGES_15.length; i++) {
      const src = CHRONICLE_STAGES_15[i];
      for (let j = 0; j < src.edges.length; j++) {
        const dst = CHRONICLE_STAGES_15[src.edges[j]];
        if (!dst) continue;
        const isClearedEdge = clearedSet.has(src.stageIndex);
        const strokeColor = isClearedEdge ? "#00E5FF" : "#FFB800";
        edgesSvg +=
          '<line x1="' + src.x + '" y1="' + src.y + '" x2="' + dst.x + '" y2="' + dst.y + '" ' +
          'stroke="' + strokeColor + '" stroke-width="3" stroke-dasharray="7 5" opacity="0.82"/>';
      }
    }

    let nodesSvg = "";
    for (let i = 0; i < CHRONICLE_STAGES_15.length; i++) {
      const st = CHRONICLE_STAGES_15[i];
      const isCurrent = st.stageIndex === activeStageIdx;
      const isCleared = clearedSet.has(st.stageIndex);
      const ringColor = isCurrent ? "#FFB800" : (isCleared ? "#2EE6D3" : "#38BDF8");
      const fillBg = isCurrent ? "#1E1B4B" : "#0F172A";
      const labelY = st.y < 150 ? st.y - 26 : st.y + 34;
      const shortLabel = "S" + (st.stageIndex + 1) + ": " + st.bossName.split(" ")[0];

      nodesSvg +=
        '<g class="chronicle-stage-node" data-stage-index="' + st.stageIndex + '" data-stage-id="' + st.stageId + '" ' +
        'onclick="window.SynapseIvaliceChronicleMap.loadChronicleStage(' + st.stageIndex + ')" style="cursor:pointer;">' +
        '<circle cx="' + st.x + '" cy="' + st.y + '" r="' + (isCurrent ? 22 : 17) + '" fill="' + fillBg + '" stroke="' + ringColor + '" stroke-width="' + (isCurrent ? 4 : 2.5) + '"/>' +
        '<text x="' + st.x + '" y="' + (st.y + 4) + '" text-anchor="middle" fill="#F8FAFC" font-size="12" font-weight="900">' + (st.stageIndex + 1) + '</text>' +
        '<text x="' + st.x + '" y="' + labelY + '" text-anchor="middle" fill="' + ringColor + '" font-size="11" font-weight="800">' + shortLabel + '</text>' +
        '</g>';
    }

    const actDividers =
      '<rect x="12" y="12" width="330" height="36" rx="6" fill="rgba(0,229,255,0.12)" stroke="#00E5FF" stroke-width="1.2"/>' +
      '<text x="177" y="34" text-anchor="middle" fill="#00E5FF" font-size="12" font-weight="900">ACT I: SKY-STONE BORDER (1-5)</text>' +
      '<rect x="354" y="12" width="318" height="36" rx="6" fill="rgba(255,184,0,0.12)" stroke="#FFB800" stroke-width="1.2"/>' +
      '<text x="513" y="34" text-anchor="middle" fill="#FFB800" font-size="12" font-weight="900">ACT II: CLOCKWORK SANCTUM (6-10)</text>' +
      '<rect x="684" y="12" width="304" height="36" rx="6" fill="rgba(255,46,84,0.14)" stroke="#FF2E54" stroke-width="1.2"/>' +
      '<text x="836" y="34" text-anchor="middle" fill="#FDA4AF" font-size="12" font-weight="900">ACT III: CRADLE OF ECHOES (11-15)</text>';

    return (
      '<svg id="ivalice-chronicle-svg-graph" viewBox="0 0 1000 370" style="width:100%;height:auto;background:radial-gradient(circle at 50% 50%,#111c38 0%,#060a14 90%);border:1.5px solid #2b4478;border-radius:10px;">' +
      actDividers +
      edgesSvg +
      nodesSvg +
      '</svg>'
    );
  }

  function ensureChronicleMapModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("ivalice-chronicle-map-modal");
    if (!modal) {
      modal = doc.createElement("div");
      modal.id = "ivalice-chronicle-map-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.style.cssText = "display:none;z-index:135;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function openChronicleMapModal() {
    const modal = ensureChronicleMapModalDom();
    if (!modal) return null;
    const st = globalScope.state || {};
    const curIdx = typeof st.stageIndex === "number" ? st.stageIndex : 0;
    const cleared = Array.isArray(st.clearedStages) ? st.clearedStages : [];
    const svgHtml = buildChronicleSvgGraphHtml(curIdx, cleared);
    const i18n = globalScope.SynapseI18nAccessibility;

    const cardsHtml = CHRONICLE_STAGES_15.map(function (node) {
      const isCur = node.stageIndex === curIdx;
      const borderCol = isCur ? "#FFB800" : "#38BDF8";
      const localTitle = i18n ? i18n.t(node.stageId, node.name) : node.name;
      return (
        '<div class="chronicle-stage-card" data-stage-index="' + node.stageIndex + '" style="background:rgba(15,23,42,0.94);border:1.5px solid ' + borderCol + ';border-radius:8px;padding:8px;display:flex;flex-direction:column;gap:4px;font-size:12px;">' +
        '<div style="font-weight:900;color:' + borderCol + ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + localTitle + '</div>' +
        '<div style="color:#cbd5e1;font-size:12px;">Boss: <b style="color:#fda4af;">' + node.bossName + '</b> (+' + node.aiBonus + ' AI)</div>' +
        '<div style="color:#fef08a;font-size:12px;">Law: ' + node.judgeLaw.name + '</div>' +
        '<div style="color:#2EE6D3;font-size:12px;">Relic: ' + node.rewardRelic.name + '</div>' +
        '<button type="button" onclick="window.SynapseIvaliceChronicleMap.loadChronicleStage(' + node.stageIndex + ')" style="margin-top:3px;font-size:12px;padding:4px 8px;background:linear-gradient(135deg,#0284c7,#1d4ed8);border-color:#7dd3fc;">' +
        iconHtml("sword", 12, "margin-right:4px;") + 'Deploy Stage ' + (node.stageIndex + 1) + '</button>' +
        '</div>'
      );
    }).join("");

    modal.innerHTML =
      '<div class="modal-box" style="max-width:920px;width:96%;max-height:88vh;overflow-y:auto;text-align:left;transform:none;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;flex-wrap:wrap;gap:8px;">' +
      '<div>' +
      '<div style="font-size:12px;font-weight:900;color:#FFB800;letter-spacing:1px;">' + iconHtml("chronicle_map", 15, "margin-right:5px;") + '3-ACT IVALICE OVERWORLD DAG (15 CAMPAIGN STAGES)</div>' +
      '<h3 style="font-size:18px;font-weight:900;color:#fff;">' + (i18n ? i18n.t("overworld_chronicle") : "15-Stage Ivalice Chronicle") + '</h3>' +
      '</div>' +
      '<button type="button" onclick="window.SynapseIvaliceChronicleMap.closeChronicleMapModal()">Close Map</button>' +
      '</div>' +
      svgHtml +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin-top:8px;">' + cardsHtml + '</div>' +
      '</div>';

    modal.style.display = "flex";
    return CHRONICLE_STAGES_15;
  }

  function closeChronicleMapModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("ivalice-chronicle-map-modal");
    if (modal) modal.style.display = "none";
  }

  const SynapseIvaliceChronicleMap = {
    VERSION: SUITE_VERSION,
    ACTS: CHRONICLE_ACTS,
    STAGES_GRAPH: CHRONICLE_STAGES_15,
    getStages: function () { return CHRONICLE_STAGES_15; },
    getActs: function () { return CHRONICLE_ACTS; },
    getStageNode: getStageNode,
    loadChronicleStage: loadChronicleStage,
    selectStage: loadChronicleStage,
    openChronicleMapModal: openChronicleMapModal,
    closeChronicleMapModal: closeChronicleMapModal
  };

  // ==========================================================================
  // 3. window.SynapseReplayGhostLadder -- CF-RPL1 REPLAYS, 10 GHOSTS & 7 PUZZLES
  // ==========================================================================
  const GRANDMASTER_GHOST_LADDER_10 = [
    { ghostId: "ghost_gm_01_alpha_sovereign", rank: 10, title: "Initiate of the Sky-Stone", username: "AlphaSovereign", elo: 1650, stageIndex: 0, faction: "Solaris", judgeLawId: "STANDARD_HIGH_PIP", cardIds: ["h_archangel", "h_valkyrie", "h_oracle", "h_kai", "e_eclipse"] },
    { ghostId: "ghost_gm_02_valkyria_wing", rank: 9, title: "Windmill Lance Tactician", username: "ValkyriaSkylance", elo: 1720, stageIndex: 2, faction: "Valkyria", judgeLawId: "SAME_PLUS_CASCADE", cardIds: ["h_phoenix", "h_valkyrie", "h_kai", "h_chronos", "e_cryo"] },
    { ghostId: "ghost_gm_03_okitsu_arbiter", rank: 8, title: "Citadel Lawkeeper", username: "OkitsuArbiter", elo: 1790, stageIndex: 4, faction: "Solaris", judgeLawId: "SAME_PLUS_CASCADE", cardIds: ["h_arbiter", "h_archangel", "h_oracle", "h_seraph", "e_archon"] },
    { ghostId: "ghost_gm_04_chronos_weaver", rank: 7, title: "Clockwork Sanctum Warden", username: "ChronosEscapement", elo: 1860, stageIndex: 5, faction: "Chronos", judgeLawId: "MNEMOSYNE_NODE_RESONANCE", cardIds: ["h_chronos", "plugin_02_parallel_swarm_orchestrator", "h_kai", "h_oracle", "e_shinobi"] },
    { ghostId: "ghost_gm_05_solideye_phantom", rank: 6, title: "Solid Eye Halftone Operative", username: "KaiHalftoneZero", elo: 1940, stageIndex: 7, faction: "Aether", judgeLawId: "SAME_PLUS_CASCADE", cardIds: ["h_kai", "h_oracle", "plugin_01_tcg_creative_designer", "h_valkyrie", "e_colossus"] },
    { ghostId: "ghost_gm_06_mnemosyne_sage", rank: 5, title: "Archon of the Gear Vault", username: "MnemosyneOracle", elo: 2030, stageIndex: 9, faction: "Aether", judgeLawId: "MNEMOSYNE_NODE_RESONANCE", cardIds: ["h_oracle", "plugin_01_tcg_creative_designer", "plugin_03_jev_system_one", "h_archangel", "e_cryo"] },
    { ghostId: "ghost_gm_07_jev_gatekeeper", rank: 4, title: "System One Calibrated Judge", username: "JevSystemOneGM", elo: 2120, stageIndex: 11, faction: "Solaris", judgeLawId: "OKITSU_TIE_SURGE", cardIds: ["plugin_03_jev_system_one", "h_arbiter", "h_archangel", "plugin_04_mlx_apple_silicon", "e_archon"] },
    { ghostId: "ghost_gm_08_mlx_metal_titan", rank: 3, title: "A18 Pro Metal Sovereign", username: "MlxAppleSiliconGM", elo: 2210, stageIndex: 12, faction: "Valkyria", judgeLawId: "OKITSU_TIE_SURGE", cardIds: ["plugin_04_mlx_apple_silicon", "h_phoenix", "h_valkyrie", "plugin_02_parallel_swarm_orchestrator", "e_inferno"] },
    { ghostId: "ghost_gm_09_trigger_cross_star", rank: 2, title: "Studio Trigger 24fps Maestro", username: "SakugaCrossStarGM", elo: 2310, stageIndex: 13, faction: "Abyss", judgeLawId: "OKITSU_TIE_SURGE", cardIds: ["h_seraph", "plugin_01_tcg_creative_designer", "plugin_02_parallel_swarm_orchestrator", "h_chronos", "e_reaper"] },
    { ghostId: "ghost_gm_10_omega_chronos_prime", rank: 1, title: "Supreme Sovereign of Cradle of Echoes", username: "OmegaChronosPrime", elo: 2420, stageIndex: 14, faction: "Aether", judgeLawId: "OKITSU_TIE_SURGE", cardIds: ["plugin_01_tcg_creative_designer", "plugin_02_parallel_swarm_orchestrator", "plugin_03_jev_system_one", "plugin_04_mlx_apple_silicon", "h_archangel"] }
  ];

  const DAILY_PUZZLES_7 = [
    {
      puzzleId: "daily_puzzle_01", dayIndex: 1, seed: 20261101,
      title: "Day 1: Solar Cruciform Double Capture",
      subtitle: "Deploy Solar Archangel into Center Socket (2,2) to flip North & West foes in 1 turn.",
      stageIndex: 0, judgeLawId: "STANDARD_HIGH_PIP", okitsuTieSurge: false,
      colDice: [4, 5, 2], nudgesLeft: 1, usedSlideThisTurn: false,
      hand: ["h_archangel", "h_kai"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] },
        { r: 1, c: 0, cardId: "e_shinobi", owner: "ai", nesw: [7, 6, 6, 5] },
        { r: 2, c: 2, cardId: "e_cryo", owner: "ai", nesw: [5, 7, 6, 7] },
        { r: 2, c: 0, cardId: "h_oracle", owner: "player", nesw: [7, 7, 8, 7] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "h_archangel", slotIndex: 4, r: 1, c: 1, preNudgeCol: null, flipsCount: 2 }
    },
    {
      puzzleId: "daily_puzzle_02", dayIndex: 2, seed: 20261102,
      title: "Day 2: Triple Triad SAME Rule Reversal",
      subtitle: "Match exact opposing edges (N=7 vs S=7 and E=7 vs W=7) to trigger a SAME double flip.",
      stageIndex: 1, judgeLawId: "SAME_PLUS_CASCADE", okitsuTieSurge: false,
      colDice: [2, 2, 2], nudgesLeft: 0, usedSlideThisTurn: true,
      hand: ["h_oracle", "h_chronos"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_reaper", owner: "ai", nesw: [6, 7, 7, 5] },
        { r: 1, c: 2, cardId: "e_cryo", owner: "ai", nesw: [5, 7, 6, 7] },
        { r: 2, c: 0, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] },
        { r: 0, c: 0, cardId: "h_valkyrie", owner: "player", nesw: [8, 8, 5, 6] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "h_oracle", slotIndex: 4, r: 1, c: 1, preNudgeCol: null, flipsCount: 2 }
    },
    {
      puzzleId: "daily_puzzle_03", dayIndex: 3, seed: 20261103,
      title: "Day 3: Ivalice PLUS Rule & Combo Cascade",
      subtitle: "Match identical edge sums (8+5=13 North & 6+7=13 West) to trigger PLUS + Combo Cascade!",
      stageIndex: 3, judgeLawId: "SAME_PLUS_CASCADE", okitsuTieSurge: false,
      colDice: [2, 2, 2], nudgesLeft: 0, usedSlideThisTurn: true,
      hand: ["h_valkyrie", "h_kai"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] },
        { r: 1, c: 0, cardId: "e_reaper", owner: "ai", nesw: [8, 7, 7, 5] },
        { r: 0, c: 0, cardId: "e_archon", owner: "ai", nesw: [7, 5, 5, 5] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "h_valkyrie", slotIndex: 4, r: 1, c: 1, preNudgeCol: null, flipsCount: 3 }
    },
    {
      puzzleId: "daily_puzzle_04", dayIndex: 4, seed: 20261104,
      title: "Day 4: Column Die Nudge Surge +1 Lethal",
      subtitle: "Nudge Column 2 Die from Pip 3 -> Pip 4 (+1 All Sides), then deploy Phoenix Valkyrie!",
      stageIndex: 5, judgeLawId: "MNEMOSYNE_NODE_RESONANCE", okitsuTieSurge: false,
      colDice: [2, 3, 2], nudgesLeft: 1, usedSlideThisTurn: true,
      hand: ["h_phoenix"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_titan", owner: "ai", nesw: [7, 5, 8, 6] },
        { r: 1, c: 2, cardId: "e_colossus", owner: "ai", nesw: [6, 8, 5, 8] },
        { r: 2, c: 0, cardId: "h_kai", owner: "player", nesw: [7, 8, 6, 7] }
      ],
      winningMove: { actionType: "NUDGE_AND_DEPLOY", handIndex: 0, cardId: "h_phoenix", slotIndex: 4, r: 1, c: 1, preNudgeCol: 1, flipsCount: 2 }
    },
    {
      puzzleId: "daily_puzzle_05", dayIndex: 5, seed: 20261105,
      title: "Day 5: Sovereign Plugin Quad-Edge Sweep",
      subtitle: "Deploy Hallowed Arbiter of System One into (2,2) to capture North, South, and West foes.",
      stageIndex: 8, judgeLawId: "MNEMOSYNE_NODE_RESONANCE", okitsuTieSurge: false,
      colDice: [2, 5, 2], nudgesLeft: 0, usedSlideThisTurn: true,
      hand: ["plugin_03_jev_system_one", "h_chronos"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_inferno", owner: "ai", nesw: [7, 7, 6, 6] },
        { r: 2, c: 1, cardId: "e_archon", owner: "ai", nesw: [7, 6, 6, 5] },
        { r: 1, c: 0, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "plugin_03_jev_system_one", slotIndex: 4, r: 1, c: 1, preNudgeCol: null, flipsCount: 3 }
    },
    {
      puzzleId: "daily_puzzle_06", dayIndex: 6, seed: 20261106,
      title: "Day 6: Okitsu Tie-Surge Equal-Pip Breakthrough",
      subtitle: "Under Act III Okitsu Law, equal opposing pips (>=) capture! Deploy A18 Pro Metal Sovereign.",
      stageIndex: 11, judgeLawId: "OKITSU_TIE_SURGE", okitsuTieSurge: true,
      colDice: [2, 2, 2], nudgesLeft: 0, usedSlideThisTurn: true,
      hand: ["plugin_04_mlx_apple_silicon"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_reaper", owner: "ai", nesw: [6, 7, 7, 5] },
        { r: 1, c: 2, cardId: "e_cryo", owner: "ai", nesw: [5, 7, 6, 7] },
        { r: 2, c: 1, cardId: "e_titan", owner: "ai", nesw: [7, 5, 7, 6] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "plugin_04_mlx_apple_silicon", slotIndex: 4, r: 1, c: 1, preNudgeCol: null, flipsCount: 3 }
    },
    {
      puzzleId: "daily_puzzle_07", dayIndex: 7, seed: 20261107,
      title: "Day 7: Omega Chronos Finale -- Sun Arbiter Law Seal",
      subtitle: "Deploy Sun Arbiter into (1,3) with Column 3 Boost to capture South & West constructs.",
      stageIndex: 14, judgeLawId: "OKITSU_TIE_SURGE", okitsuTieSurge: true,
      colDice: [2, 2, 6], nudgesLeft: 1, usedSlideThisTurn: false,
      hand: ["h_arbiter", "h_seraph"],
      boardSetup: [
        { r: 0, c: 1, cardId: "e_colossus", owner: "ai", nesw: [6, 8, 5, 6] },
        { r: 1, c: 2, cardId: "e_inferno", owner: "ai", nesw: [8, 7, 5, 6] },
        { r: 2, c: 2, cardId: "e_eclipse", owner: "ai", nesw: [6, 6, 5, 6] },
        { r: 2, c: 0, cardId: "h_archangel", owner: "player", nesw: [8, 7, 6, 7] }
      ],
      winningMove: { actionType: "DEPLOY", handIndex: 0, cardId: "h_arbiter", slotIndex: 2, r: 0, c: 2, preNudgeCol: null, flipsCount: 2 }
    }
  ];

  const recordedTurns = [
    { turn: 1, actor: "player", actionType: "DEPLOY", cardId: "h_archangel", slotIndex: 4, r: 1, c: 1, flipsCount: 1, timestamp: 1731150001000 },
    { turn: 2, actor: "ai", actionType: "DEPLOY", cardId: "e_eclipse", slotIndex: 2, r: 0, c: 2, flipsCount: 0, timestamp: 1731150002000 },
    { turn: 3, actor: "player", actionType: "NUDGE_DIE", colIndex: 2, newPip: 6, slotIndex: 2, timestamp: 1731150003000 },
    { turn: 4, actor: "player", actionType: "DEPLOY", cardId: "h_phoenix", slotIndex: 5, r: 1, c: 2, flipsCount: 2, timestamp: 1731150004000 }
  ];

  function recordAction(actionObj) {
    if (!actionObj || typeof actionObj !== "object") return null;
    const entry = Object.assign(
      {
        turn: recordedTurns.length + 1,
        actor: "player",
        actionType: "DEPLOY",
        slotIndex: 4,
        timestamp: Date.now()
      },
      actionObj
    );
    recordedTurns.push(entry);
    return entry;
  }

  function serializeReplay(replayObj) {
    const payload = Object.assign(
      {
        format: "CF-RPL1",
        version: 1,
        seed: (globalScope.state && globalScope.state.seed) || 20261109,
        stageIndex: (globalScope.state && globalScope.state.stageIndex) || 0,
        turns: recordedTurns.slice()
      },
      replayObj || {}
    );
    const copyNoHash = Object.assign({}, payload);
    delete copyNoHash.fnv1a_64_checksum;
    const canonicalJson = JSON.stringify(copyNoHash);
    const checksum = computeFnv1a64Hex(canonicalJson);
    payload.fnv1a_64_checksum = checksum;
    const b64 = encodeBase64Url(JSON.stringify(payload));
    return REPLAY_PREFIX + b64 + "." + checksum;
  }

  function deserializeReplay(envelopeStr) {
    const raw = String(envelopeStr || "").trim();
    if (!raw.startsWith(REPLAY_PREFIX)) {
      throw new Error("Replay envelope must start with 'CF-RPL1:'");
    }
    const body = raw.slice(REPLAY_PREFIX.length);
    const dotIdx = body.lastIndexOf(".");
    if (dotIdx <= 0) {
      throw new Error("Replay envelope missing '.<fnv1a64>' checksum suffix");
    }
    const b64Part = body.slice(0, dotIdx);
    const claimedHash = body.slice(dotIdx + 1);
    const decodedJson = decodeBase64Url(b64Part);
    const parsed = JSON.parse(decodedJson);

    if (Array.isArray(parsed.turns)) {
      recordedTurns.length = 0;
      parsed.turns.forEach(function (t) { recordedTurns.push(t); });
    }
    parsed.verifiedChecksum = claimedHash;
    return parsed;
  }

  function scrubToTurn(turnIndex) {
    const idx = Math.max(0, Math.min(recordedTurns.length - 1, Number(turnIndex) || 0));
    const evt = recordedTurns[idx] || recordedTurns[0];
    const sakuga = globalScope.SynapseSakugaAnimEngine;
    let sakugaResult = null;

    if (sakuga && evt) {
      if (evt.actionType === "NUDGE_DIE" && typeof sakuga.triggerColumnDieSurge === "function") {
        sakugaResult = sakuga.triggerColumnDieSurge(evt.colIndex || 0);
      } else if (evt.actionType === "SLIDE" && typeof sakuga.triggerTacticalSlideBank === "function") {
        sakugaResult = sakuga.triggerTacticalSlideBank(evt.fromSlot || 4, evt.slotIndex || 5);
      } else if (typeof sakuga.triggerDeploySlam === "function") {
        sakugaResult = sakuga.triggerDeploySlam(evt.slotIndex !== undefined ? evt.slotIndex : 4);
        if (evt.flipsCount > 0 && typeof sakuga.triggerCaptureFlip180 === "function") {
          sakuga.triggerCaptureFlip180(evt.slotIndex !== undefined ? evt.slotIndex : 4, evt.actor || "player");
        }
      }
      if (typeof sakuga.scrubTo === "function") {
        sakuga.scrubTo("directional_clash_lunge", 0.25);
      }
    }

    if (typeof globalScope.document !== "undefined") {
      const statusEl = globalScope.document.getElementById("replay-scrubber-status");
      if (statusEl && evt) {
        statusEl.innerHTML =
          iconHtml("replay_film", 13, "margin-right:4px;") +
          "Scrubbed to Turn <b>#" + evt.turn + "</b>: <b>" + evt.actionType + "</b> (" + (evt.cardId || "Col Die") + " at Socket #" + (evt.slotIndex || 0) + ")";
      }
    }

    return {
      turnIndex: idx,
      event: evt,
      sakugaTriggered: Boolean(sakugaResult)
    };
  }

  function loadDailyPuzzle(puzzleIdOrIndex) {
    let puzzle = DAILY_PUZZLES_7[0];
    if (typeof puzzleIdOrIndex === "number") {
      puzzle = DAILY_PUZZLES_7[Math.max(0, Math.min(DAILY_PUZZLES_7.length - 1, puzzleIdOrIndex))];
    } else if (typeof puzzleIdOrIndex === "string") {
      puzzle = DAILY_PUZZLES_7.find(function (p) { return p.puzzleId === puzzleIdOrIndex; }) || DAILY_PUZZLES_7[0];
    }

    if (globalScope.state) {
      const st = globalScope.state;
      clearTimeout(st.bossTurnTimer);
      st.gameOver = false;
      st.isPlayerTurn = true;
      st.stageIndex = puzzle.stageIndex;
      st.colDice = puzzle.colDice.slice();
      st.nudgesLeft = puzzle.nudgesLeft;
      st.usedSlideThisTurn = puzzle.usedSlideThisTurn;
      st.forceOkitsuTieSurge = Boolean(puzzle.okitsuTieSurge);
      st.hand = puzzle.hand.slice();
      st.aiPool = [];
      st.selectedHandIdx = 0;
      st.selectedBoardSlot = null;
      st.activeDailyPuzzle = puzzle;

      st.grid = [];
      for (let r = 0; r < 3; r++) {
        const row = [];
        for (let c = 0; c < 3; c++) {
          row.push({ r: r, c: c, cardId: null, owner: null, nesw: [0, 0, 0, 0], justFlipped: false });
        }
        st.grid.push(row);
      }
      puzzle.boardSetup.forEach(function (cell) {
        st.grid[cell.r][cell.c] = {
          r: cell.r,
          c: cell.c,
          cardId: cell.cardId,
          owner: cell.owner,
          nesw: cell.nesw.slice(),
          justFlipped: false
        };
      });

      if (typeof globalScope.renderAll === "function") {
        globalScope.renderAll();
      }
    }

    closeReplayLadderModal();
    return puzzle;
  }

  function solveActiveDailyPuzzle() {
    const st = globalScope.state;
    const puzzle = (st && st.activeDailyPuzzle) || DAILY_PUZZLES_7[0];
    loadDailyPuzzle(puzzle.puzzleId);
    const wm = puzzle.winningMove;
    if (wm.preNudgeCol !== null && wm.preNudgeCol !== undefined && typeof globalScope.nudgeColDie === "function") {
      globalScope.nudgeColDie(wm.preNudgeCol);
    }
    if (st) {
      st.selectedHandIdx = wm.handIndex || 0;
      st.selectedBoardSlot = null;
    }
    if (typeof globalScope.handleSlotClick === "function") {
      globalScope.handleSlotClick(wm.r, wm.c);
    }
    return wm;
  }

  function challengeGhostDeck(ghostIdOrRank) {
    let ghost = GRANDMASTER_GHOST_LADDER_10[0];
    if (typeof ghostIdOrRank === "number") {
      ghost = GRANDMASTER_GHOST_LADDER_10.find(function (g) { return g.rank === ghostIdOrRank; }) || GRANDMASTER_GHOST_LADDER_10[0];
    } else if (typeof ghostIdOrRank === "string") {
      ghost = GRANDMASTER_GHOST_LADDER_10.find(function (g) { return g.ghostId === ghostIdOrRank; }) || GRANDMASTER_GHOST_LADDER_10[0];
    }

    if (typeof globalScope.startStage === "function") {
      globalScope.startStage(ghost.stageIndex);
    }
    if (globalScope.state) {
      globalScope.state.aiPool = ghost.cardIds.slice(0, 4);
      globalScope.state.activeEchoGhost = ghost;
      globalScope.state.forceOkitsuTieSurge = ghost.judgeLawId === "OKITSU_TIE_SURGE";
      if (typeof globalScope.telegraphBossIntent === "function") {
        globalScope.telegraphBossIntent();
      }
      if (typeof globalScope.renderAll === "function") {
        globalScope.renderAll();
      }
    }
    if (typeof globalScope.document !== "undefined") {
      const crestName = globalScope.document.getElementById("boss-crest-name");
      if (crestName) {
        crestName.textContent = "GRANDMASTER GHOST #" + ghost.rank + " | " + ghost.username.toUpperCase() + " (" + ghost.elo + " ELO)";
      }
    }
    closeReplayLadderModal();
    return ghost;
  }

  function ensureReplayLadderModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("replay-ghost-ladder-modal");
    if (!modal) {
      modal = doc.createElement("div");
      modal.id = "replay-ghost-ladder-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.style.cssText = "display:none;z-index:135;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function openReplayLadderModal() {
    const modal = ensureReplayLadderModalDom();
    if (!modal) return null;
    const envelopeStr = serializeReplay();
    const i18n = globalScope.SynapseI18nAccessibility;

    const puzzlesHtml = DAILY_PUZZLES_7.map(function (p) {
      return (
        '<div class="daily-puzzle-card" data-puzzle-id="' + p.puzzleId + '" style="background:rgba(15,23,42,0.94);border:1.5px solid #FFB800;border-radius:8px;padding:8px;display:flex;flex-direction:column;gap:4px;font-size:12px;">' +
        '<div style="font-weight:900;color:#FFB800;">' + p.title + '</div>' +
        '<div style="color:#cbd5e1;font-size:12px;">' + p.subtitle + '</div>' +
        '<div style="display:flex;gap:6px;margin-top:4px;">' +
        '<button type="button" onclick="window.SynapseReplayGhostLadder.loadDailyPuzzle(\'' + p.puzzleId + '\')" style="font-size:12px;padding:3px 8px;border-color:#00E5FF;color:#00E5FF;">Load Board</button>' +
        '<button type="button" onclick="window.SynapseReplayGhostLadder.loadDailyPuzzle(\'' + p.puzzleId + '\');window.SynapseReplayGhostLadder.solveActiveDailyPuzzle();" style="font-size:12px;padding:3px 8px;background:linear-gradient(135deg,#059669,#047857);border-color:#6ee7b7;color:#fff;">Solve 1-Turn</button>' +
        '</div></div>'
      );
    }).join("");

    const ghostsHtml = GRANDMASTER_GHOST_LADDER_10.map(function (g) {
      return (
        '<div class="ghost-ladder-card" data-ghost-id="' + g.ghostId + '" style="background:rgba(15,23,42,0.94);border:1.5px solid #2EE6D3;border-radius:8px;padding:8px;display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12px;">' +
        '<div>' +
        '<div style="font-weight:900;color:#2EE6D3;">Rank #' + g.rank + ' | ' + g.username + ' (' + g.elo + ' ELO)</div>' +
        '<div style="color:#94a3b8;font-size:12px;">' + g.title + ' | Faction: ' + g.faction + ' | Law: ' + g.judgeLawId + '</div>' +
        '</div>' +
        '<button type="button" onclick="window.SynapseReplayGhostLadder.challengeGhostDeck(\'' + g.ghostId + '\')" style="font-size:12px;padding:4px 8px;background:linear-gradient(135deg,#0d9488,#0f766e);border-color:#5eead4;">Challenge</button>' +
        '</div>'
      );
    }).join("");

    modal.innerHTML =
      '<div class="modal-box" style="max-width:900px;width:96%;max-height:88vh;overflow-y:auto;text-align:left;transform:none;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;flex-wrap:wrap;gap:8px;">' +
      '<div>' +
      '<div style="font-size:12px;font-weight:900;color:#2EE6D3;letter-spacing:1px;">' + iconHtml("replay_film", 15, "margin-right:5px;") + 'CF-RPL1 DETERMINISTIC REPLAY THEATER, 7 DAILY PUZZLES & 10 GHOSTS</div>' +
      '<h3 style="font-size:18px;font-weight:900;color:#fff;">' + (i18n ? i18n.t("replay_theater") : "Replay & Ghost Ladder") + '</h3>' +
      '</div>' +
      '<button type="button" onclick="window.SynapseReplayGhostLadder.closeReplayLadderModal()">Close</button>' +
      '</div>' +
      '<div style="background:#070c18;border:1px solid rgba(46,230,211,0.45);border-radius:8px;padding:8px 10px;display:flex;flex-direction:column;gap:6px;font-size:12px;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">' +
      '<b style="color:#00E5FF;">CF-RPL1 Deterministic Envelope & Sakuga Turn Scrubber:</b>' +
      '<div style="display:flex;gap:6px;align-items:center;">' +
      '<button type="button" onclick="window.SynapseReplayGhostLadder.scrubToTurn(0)" style="font-size:12px;padding:3px 8px;">Turn 1</button>' +
      '<button type="button" onclick="window.SynapseReplayGhostLadder.scrubToTurn(1)" style="font-size:12px;padding:3px 8px;">Turn 2</button>' +
      '<button type="button" onclick="window.SynapseReplayGhostLadder.scrubToTurn(2)" style="font-size:12px;padding:3px 8px;">Turn 3</button>' +
      '<button type="button" onclick="window.SynapseReplayGhostLadder.scrubToTurn(3)" style="font-size:12px;padding:3px 8px;">Turn 4</button>' +
      '</div></div>' +
      '<input id="cf-rpl1-envelope-input" type="text" readonly value="' + envelopeStr + '" style="width:100%;background:#0f172a;color:#fef08a;border:1px solid #334155;border-radius:6px;padding:4px 8px;font-family:ui-monospace,monospace;font-size:12px;" />' +
      '<div id="replay-scrubber-status" style="color:#cbd5e1;font-size:12px;">Ready to scrub recorded turns with SynapseSakugaAnimEngine.</div>' +
      '</div>' +
      '<div style="font-size:13px;font-weight:900;color:#FFB800;margin-top:4px;">' + iconHtml("sparkle", 14, "margin-right:4px;") + '7 Daily Seeded Lethal Tactical Puzzles (Solve-in-1-Turn)</div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px;">' + puzzlesHtml + '</div>' +
      '<div style="font-size:13px;font-weight:900;color:#2EE6D3;margin-top:6px;">' + iconHtml("shield", 14, "margin-right:4px;") + '10 Grandmaster Ghost Decks Ladder (1650 - 2420 ELO)</div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:8px;">' + ghostsHtml + '</div>' +
      '</div>';

    modal.style.display = "flex";
    return modal;
  }

  function closeReplayLadderModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("replay-ghost-ladder-modal");
    if (modal) modal.style.display = "none";
  }

  const SynapseReplayGhostLadder = {
    VERSION: SUITE_VERSION,
    REPLAY_PREFIX: REPLAY_PREFIX,
    GHOST_LADDER: GRANDMASTER_GHOST_LADDER_10,
    DAILY_PUZZLES: DAILY_PUZZLES_7,
    recordedTurns: recordedTurns,
    recordAction: recordAction,
    serializeReplay: serializeReplay,
    exportReplayEnvelope: serializeReplay,
    deserializeReplay: deserializeReplay,
    importReplayEnvelope: deserializeReplay,
    scrubToTurn: scrubToTurn,
    getGhostLadder: function () { return GRANDMASTER_GHOST_LADDER_10; },
    challengeGhostDeck: challengeGhostDeck,
    getDailyPuzzles: function () { return DAILY_PUZZLES_7; },
    loadDailyPuzzle: loadDailyPuzzle,
    solveActiveDailyPuzzle: solveActiveDailyPuzzle,
    openReplayLadderModal: openReplayLadderModal,
    closeReplayLadderModal: closeReplayLadderModal
  };

  // ==========================================================================
  // 4. window.SynapseI18nAccessibility -- 10-LANG LOCALIZATION & 4 COLORBLIND MODES
  // ==========================================================================
  const SUPPORTED_LANGUAGES = ["EN", "JA", "KO", "ZH-Hans", "ZH-Hant", "FR", "DE", "ES", "PT-BR", "IT"];

  const COLORBLIND_PALETTES = {
    standard: {
      id: "standard",
      label: "Standard Atelier (Astral Cyan vs Crimson-Flame)",
      allyPrimary: "#00E5FF",
      allyGlow: "rgba(0, 229, 255, 0.55)",
      enemyPrimary: "#FF2E54",
      enemyGlow: "rgba(255, 46, 84, 0.55)",
      goldAccent: "#FFB800",
      emeraldAccent: "#00E676",
      violetAccent: "#A855F7",
      cssFilter: "none",
      wcagContrastRatio: 9.4
    },
    deuteranopia: {
      id: "deuteranopia",
      label: "Deuteranopia Safe (Cobalt-Azure vs Amber-Gold)",
      allyPrimary: "#38BDF8",
      allyGlow: "rgba(56, 189, 248, 0.62)",
      enemyPrimary: "#F59E0B",
      enemyGlow: "rgba(245, 158, 11, 0.62)",
      goldAccent: "#FDE047",
      emeraldAccent: "#60A5FA",
      violetAccent: "#C084FC",
      cssFilter: "contrast(1.06) saturate(1.12)",
      wcagContrastRatio: 10.2
    },
    protanopia: {
      id: "protanopia",
      label: "Protanopia Safe (Cerulean-Teal vs Solar-Yellow)",
      allyPrimary: "#00D2FF",
      allyGlow: "rgba(0, 210, 255, 0.62)",
      enemyPrimary: "#FF9F1C",
      enemyGlow: "rgba(255, 159, 28, 0.62)",
      goldAccent: "#FFF3B0",
      emeraldAccent: "#2EC4B6",
      violetAccent: "#9B5DE5",
      cssFilter: "contrast(1.08) saturate(1.10)",
      wcagContrastRatio: 10.6
    },
    tritanopia: {
      id: "tritanopia",
      label: "Tritanopia Safe (Jade-Aqua vs Magenta-Rose)",
      allyPrimary: "#2EE6D3",
      allyGlow: "rgba(46, 230, 211, 0.62)",
      enemyPrimary: "#F43F5E",
      enemyGlow: "rgba(244, 63, 94, 0.62)",
      goldAccent: "#FFE082",
      emeraldAccent: "#14B8A6",
      violetAccent: "#EC4899",
      cssFilter: "contrast(1.08) saturate(1.08)",
      wcagContrastRatio: 9.9
    }
  };

  const I18N_STRINGS = {
    your_turn: { EN: "YOUR TURN", JA: "あなたのターン", KO: "나의 턴", "ZH-Hans": "你的回合", "ZH-Hant": "你的回合", FR: "VOTRE TOUR", DE: "DEIN ZUG", ES: "TU TURNO", "PT-BR": "SEU TURNO", IT: "TUO TURNO" },
    boss_turn: { EN: "BOSS TURN", JA: "ボスのターン", KO: "보스의 턴", "ZH-Hans": "首领回合", "ZH-Hant": "首領回合", FR: "TOUR DU BOSS", DE: "BOSS-ZUG", ES: "TURNO DEL JEFE", "PT-BR": "TURNO DO CHEFE", IT: "TURNO DEL BOSS" },
    hero_hand: { EN: "HERO HAND", JA: "英雄の手札", KO: "영웅 핸드", "ZH-Hans": "英雄手牌", "ZH-Hant": "英雄手牌", FR: "MAIN DES HÉROS", DE: "HELDENHAND", ES: "MANO DE HÉROES", "PT-BR": "MÃO DE HERÓIS", IT: "MANO DEGLI EROI" },
    deck_label: { EN: "DECK", JA: "デッキ", KO: "덱", "ZH-Hans": "牌组", "ZH-Hant": "牌組", FR: "DECK", DE: "DECK", ES: "MAZO", "PT-BR": "DECK", IT: "MAZZO" },
    victory: { EN: "VICTORY", JA: "勝利", KO: "승리", "ZH-Hans": "胜利", "ZH-Hant": "勝利", FR: "VICTOIRE", DE: "SIEG", ES: "VICTORIA", "PT-BR": "VITÓRIA", IT: "VITTORIA" },
    defeat: { EN: "DEFEAT", JA: "敗北", KO: "패배", "ZH-Hans": "战败", "ZH-Hant": "戰敗", FR: "DÉFAITE", DE: "NIEDERLAGE", ES: "DERROTA", "PT-BR": "DERROTA", IT: "SCONFITTA" },
    draw_match: { EN: "DRAW MATCH", JA: "引き分け", KO: "무승부", "ZH-Hans": "平局", "ZH-Hant": "平局", FR: "ÉGALITÉ", DE: "UNENTSCHIEDEN", ES: "EMPATE", "PT-BR": "EMPATE", IT: "PAREGGIO" },
    tactical_slide: { EN: "Tactical Slide", JA: "タクティカルスライド", KO: "전술 슬라이드", "ZH-Hans": "战术滑移", "ZH-Hant": "戰術滑移", FR: "Glissement Tactique", DE: "Taktischer Schub", ES: "Deslizamiento Táctico", "PT-BR": "Deslize Tático", IT: "Scivolata Tattica" },
    column_dice: { EN: "3D Lane Dice", JA: "3D列ダイス", KO: "3D 열 주사위", "ZH-Hans": "3D列骰子", "ZH-Hant": "3D列骰子", FR: "Dés de Colonne 3D", DE: "3D-Spaltenwürfel", ES: "Dados de Columna 3D", "PT-BR": "Dados de Coluna 3D", IT: "Dadi di Colonna 3D" },
    overworld_chronicle: { EN: "15-Stage Ivalice Chronicle", JA: "イヴァリース15章年代記", KO: "이발리스 15장 연대기", "ZH-Hans": "伊瓦利斯15章编年史", "ZH-Hant": "伊瓦利斯15章編年史", FR: "Chronique d'Ivalice (15 Étapes)", DE: "Ivalice-Chronik (15 Stufen)", ES: "Crónica de Ivalice (15 Etapas)", "PT-BR": "Crônica de Ivalice (15 Fases)", IT: "Cronaca di Ivalice (15 Livelli)" },
    mcts_oracle: { EN: "AlphaZero MCTS Oracle", JA: "AlphaZero MCTS戦術神託", KO: "AlphaZero MCTS 전술 오라클", "ZH-Hans": "AlphaZero MCTS战术神谕", "ZH-Hant": "AlphaZero MCTS戰術神諭", FR: "Oracle Tactique MCTS", DE: "AlphaZero MCTS-Orakel", ES: "Oráculo Táctico MCTS", "PT-BR": "Oráculo Tático MCTS", IT: "Oracolo Tattico MCTS" },
    replay_theater: { EN: "Replay & Ghost Ladder", JA: "リプレイ＆ゴースト階位戦", KO: "리플레이 & 고스트 래더", "ZH-Hans": "回放与残影天梯", "ZH-Hant": "回放與殘影天梯", FR: "Théâtre de Replay & Échelle Fantôme", DE: "Replay-Theater & Geister-Rangliste", ES: "Teatro de Repetición y Escalera Fantasma", "PT-BR": "Teatro de Replay e Escada Fantasma", IT: "Teatro Replay e Scalata Fantasma" },
    colorblind_mode: { EN: "Colorblind & Contrast Mode", JA: "色覚サポート＆コントラスト", KO: "색각 보정 및 고대비 모드", "ZH-Hans": "色觉辅助与高对比度", "ZH-Hant": "色覺輔助與高對比度", FR: "Mode Daltonien & Contraste", DE: "Farbenblind- & Kontrastmodus", ES: "Modo Daltónico y Contraste", "PT-BR": "Modo Daltônico e Contraste", IT: "Modalità Daltonici e Contrasto" },
    stage_01: { EN: "Act I-1: Skystone Sanctuary", JA: "第一幕-1：飛空石の聖域", KO: "제1막-1: 비공석 성역", "ZH-Hans": "第一幕-1：浮空石圣域", "ZH-Hant": "第一幕-1：浮空石聖域", FR: "Acte I-1 : Sanctuaire de Pierreciel", DE: "Akt I-1: Himmelsstein-Heiligtum", ES: "Acto I-1: Santuario de Piedracielo", "PT-BR": "Ato I-1: Santuário da Pedra-Celeste", IT: "Atto I-1: Santuario di Pietracielo" },
    stage_15: { EN: "Act III-15: Omega Chronos Prime", JA: "第三幕-15：オメガ・クロノス・プライム", KO: "제3막-15: 오메가 크로노스 프라임", "ZH-Hans": "第三幕-15：欧米茄·克洛诺斯·至尊", "ZH-Hant": "第三幕-15：歐米茄·克洛諾斯·至尊", FR: "Acte III-15 : Oméga Chronos Prime", DE: "Akt III-15: Omega Chronos Prime", ES: "Acto III-15: Omega Chronos Prime", "PT-BR": "Ato III-15: Ômega Chronos Prime", IT: "Atto III-15: Omega Chronos Prime" },
    judge_law_standard: { EN: "JUDGE LAW: High-Pip & Faction Link Decree", JA: "ジャッジ法：高位数値＆派閥連係の勅令", KO: "저지 법률: 상위 눈금 및 세력 연계 칙령", "ZH-Hans": "裁判法则：高点压制与阵营共鸣法令", "ZH-Hant": "裁判法則：高點壓制與陣營共鳴法令", FR: "LOI DU JUGE : Décret de Valeur Haute & Lien de Faction", DE: "RICHTERGESETZ: Hoher-Wert- & Fraktionsbund-Erlass", ES: "LEY DEL JUEZ: Decreto de Valor Superior y Vínculo", "PT-BR": "LEI DO JUIZ: Decreto de Valor Alto e Elo de Facção", IT: "LEGGE DEL GIUDICE: Decreto del Valore Alto e Legame" },
    judge_law_mnemosyne: { EN: "JUDGE LAW: Mnemosyne Center Sanctum (+1 All Stats & +50G)", JA: "ジャッジ法：中央聖域ムネモシュネ（全数値+1＆+50G）", KO: "저지 법률: 므네모시네 중앙 성소 (모든 능력치 +1 & +50G)", "ZH-Hans": "裁判法则：中央圣域记忆共鸣（全属性+1且+50金币）", "ZH-Hant": "裁判法則：中央聖域記憶共鳴（全屬性+1且+50金幣）", FR: "LOI DU JUGE : Sanctuaire Central Mnémosyne (+1 Tout & +50 Or)", DE: "RICHTERGESETZ: Mnemosyne-Zentralsanktum (+1 Alle Werte & +50G)", ES: "LEY DEL JUEZ: Santuario Central Mnemósine (+1 Todo y +50 Oro)", "PT-BR": "LEI DO JUIZ: Santuário Central Mnemósine (+1 Tudo e +50 Ouro)", IT: "LEGGE DEL GIUDICE: Santuario Centrale Mnemosine (+1 Tutto e +50 Oro)" },
    judge_law_okitsu: { EN: "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)", JA: "ジャッジ法：興津同値突破（同数値でも奪取発生！）", KO: "저지 법률: 오키츠 동률 돌파 (동일 수치도 점령 발동!)", "ZH-Hans": "裁判法则：兴津同点突破（相等边值亦可触发夺取！）", "ZH-Hant": "裁判法则：興津同點突破（相等邊值亦可觸發奪取！）", FR: "LOI DU JUGE : Percée d'Égalité Okitsu (Valeurs Égales Capturent !)", DE: "RICHTERGESETZ: Okitsu-Gleichstandsturm (Gleiche Werte erobern!)", ES: "LEY DEL JUEZ: Impulso de Empate Okitsu (¡Valores Iguales Capturan!)", "PT-BR": "LEI DO JUIZ: Impulso de Empate Okitsu (Valores Iguais Capturam!)", IT: "LEGGE DEL GIUDICE: Impeto di Parità Okitsu (Valori Uguali Catturano!)" },
    judge_law_same_plus: { EN: "JUDGE LAW: Ivalice Same / Plus & Combo Cascade Active", JA: "ジャッジ法：セイム／プラス＆コンボ連鎖発動", KO: "저지 법률: 세임 / 플러스 & 콤보 연쇄 활성화", "ZH-Hans": "裁判法则：同值/同和法则与连锁夺取激活", "ZH-Hant": "裁判法則：同值/同和法則與連鎖奪取激活", FR: "LOI DU JUGE : Règles Identique / Plus & Cascade Combo Actives", DE: "RICHTERGESETZ: Gleich / Plus & Kombo-Kaskade Aktiv", ES: "LEY DEL JUEZ: Reglas Igual / Suma y Cascada de Combo Activas", "PT-BR": "LEI DO JUIZ: Regras Igual / Soma e Cascata de Combo Ativas", IT: "LEGGE DEL GIUDICE: Regole Uguale / Somma e Cascata Combo Attive" }
  };

  function normalizeLangCode(rawCode) {
    const s = String(rawCode || "EN").trim();
    const upper = s.toUpperCase();
    if (upper === "ZH-HANS" || upper === "ZH_CN" || upper === "ZH-CN" || upper === "ZH") return "ZH-Hans";
    if (upper === "ZH-HANT" || upper === "ZH_TW" || upper === "ZH-TW" || upper === "ZH-HK") return "ZH-Hant";
    if (upper === "PT-BR" || upper === "PT_BR" || upper === "PT") return "PT-BR";
    for (let i = 0; i < SUPPORTED_LANGUAGES.length; i++) {
      if (SUPPORTED_LANGUAGES[i].toUpperCase() === upper) return SUPPORTED_LANGUAGES[i];
    }
    return "EN";
  }

  function translateKey(key, fallbackOrLang) {
    const lang = SUPPORTED_LANGUAGES.includes(fallbackOrLang)
      ? fallbackOrLang
      : SynapseI18nAccessibility.currentLanguage;
    const entry = I18N_STRINGS[key];
    if (entry && entry[lang]) return entry[lang];
    if (entry && entry.EN) return entry.EN;
    return typeof fallbackOrLang === "string" && !SUPPORTED_LANGUAGES.includes(fallbackOrLang)
      ? fallbackOrLang
      : String(key);
  }

  function setLanguage(langCode) {
    const resolved = normalizeLangCode(langCode);
    SynapseI18nAccessibility.currentLanguage = resolved;
    if (globalScope.state) {
      globalScope.state.language = resolved;
    }

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      doc.documentElement.setAttribute("lang", resolved);
      doc.documentElement.setAttribute("data-cf-lang", resolved);

      const turnBadge = doc.getElementById("turn-badge");
      if (turnBadge && globalScope.state) {
        if (globalScope.state.gameOver) {
          turnBadge.textContent = translateKey("victory", resolved);
        } else {
          turnBadge.textContent = globalScope.state.isPlayerTurn
            ? translateKey("your_turn", resolved)
            : translateKey("boss_turn", resolved);
        }
      }

      const handHeaderSpan = doc.querySelector(".hand-dock-header span");
      if (handHeaderSpan) {
        handHeaderSpan.textContent = translateKey("hero_hand", resolved);
      }

      const deckHeaderSpan = doc.querySelector(".deck-reliquary-header span");
      if (deckHeaderSpan) {
        deckHeaderSpan.textContent = translateKey("deck_label", resolved);
      }

      const colDiceTitleSpan = doc.querySelector(".floating-corner-hud .box-title span");
      if (colDiceTitleSpan) {
        colDiceTitleSpan.textContent = translateKey("column_dice", resolved);
      }
    }

    return {
      language: resolved,
      your_turn: translateKey("your_turn", resolved),
      boss_turn: translateKey("boss_turn", resolved),
      hero_hand: translateKey("hero_hand", resolved),
      deck_label: translateKey("deck_label", resolved),
      victory: translateKey("victory", resolved),
      defeat: translateKey("defeat", resolved),
      draw_match: translateKey("draw_match", resolved)
    };
  }

  function setColorblindMode(mode) {
    const cleanMode = COLORBLIND_PALETTES[mode] ? mode : "standard";
    const pal = COLORBLIND_PALETTES[cleanMode];
    SynapseI18nAccessibility.currentColorblindMode = cleanMode;
    if (globalScope.state) {
      globalScope.state.colorblindMode = cleanMode;
    }

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      const rootStyle = doc.documentElement.style;
      rootStyle.setProperty("--blue-ally", pal.allyPrimary);
      rootStyle.setProperty("--blue-glow", pal.allyGlow);
      rootStyle.setProperty("--red-enemy", pal.enemyPrimary);
      rootStyle.setProperty("--red-glow", pal.enemyGlow);
      rootStyle.setProperty("--gold", pal.goldAccent);
      rootStyle.setProperty("--emerald", pal.emeraldAccent);
      rootStyle.setProperty("--violet", pal.violetAccent);
      doc.documentElement.setAttribute("data-colorblind-mode", cleanMode);
      if (doc.body) {
        doc.body.setAttribute("data-colorblind-mode", cleanMode);
      }
    }

    return pal;
  }

  function ensureI18nA11yModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("i18n-a11y-modal");
    if (!modal) {
      modal = doc.createElement("div");
      modal.id = "i18n-a11y-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.style.cssText = "display:none;z-index:135;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function openI18nA11yModal() {
    const modal = ensureI18nA11yModalDom();
    if (!modal) return null;
    const curLang = SynapseI18nAccessibility.currentLanguage;
    const curMode = SynapseI18nAccessibility.currentColorblindMode;

    const langButtonsHtml = SUPPORTED_LANGUAGES.map(function (code) {
      const active = code === curLang;
      return (
        '<button type="button" data-lang-code="' + code + '" onclick="window.SynapseI18nAccessibility.setLanguage(\'' + code + '\');window.SynapseI18nAccessibility.openI18nA11yModal();" ' +
        'style="font-size:12px;padding:6px 10px;border-color:' + (active ? "#FFB800" : "#38BDF8") + ';background:' + (active ? "rgba(255,184,0,0.22)" : "rgba(15,23,42,0.92)") + ';">' +
        iconHtml("globe_i18n", 13, "margin-right:4px;") + code + " | " + translateKey("your_turn", code) + '</button>'
      );
    }).join("");

    const modeButtonsHtml = Object.keys(COLORBLIND_PALETTES).map(function (mKey) {
      const p = COLORBLIND_PALETTES[mKey];
      const active = mKey === curMode;
      return (
        '<div style="background:rgba(15,23,42,0.94);border:1.5px solid ' + (active ? "#FFB800" : "#475569") + ';border-radius:8px;padding:8px;display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12px;">' +
        '<div>' +
        '<div style="font-weight:900;color:#fff;">' + p.label + ' (WCAG ' + p.wcagContrastRatio + ':1)</div>' +
        '<div style="display:flex;gap:6px;align-items:center;margin-top:4px;">' +
        '<span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:' + p.allyPrimary + ';"></span><span>Ally: ' + p.allyPrimary + '</span>' +
        '<span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:' + p.enemyPrimary + ';margin-left:8px;"></span><span>Enemy: ' + p.enemyPrimary + '</span>' +
        '</div></div>' +
        '<button type="button" onclick="window.SynapseI18nAccessibility.setColorblindMode(\'' + mKey + '\');window.SynapseI18nAccessibility.openI18nA11yModal();" style="font-size:12px;padding:4px 10px;border-color:#00E5FF;">Apply</button>' +
        '</div>'
      );
    }).join("");

    modal.innerHTML =
      '<div class="modal-box" style="max-width:740px;width:95%;max-height:86vh;overflow-y:auto;text-align:left;transform:none;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;flex-wrap:wrap;gap:8px;">' +
      '<div>' +
      '<div style="font-size:12px;font-weight:900;color:#00E5FF;letter-spacing:1px;">' + iconHtml("globe_i18n", 15, "margin-right:5px;") + '10-LANGUAGE AAA LOCALIZATION & 4-MODE COLORBLIND ACCESSIBILITY</div>' +
      '<h3 style="font-size:18px;font-weight:900;color:#fff;">' + translateKey("colorblind_mode", curLang) + ' (' + curLang + ' | ' + curMode + ')</h3>' +
      '</div>' +
      '<button type="button" onclick="window.SynapseI18nAccessibility.closeI18nA11yModal()">Close</button>' +
      '</div>' +
      '<div style="font-size:12px;font-weight:900;color:#FFB800;">Select Active Language (10 Locales):</div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(195px,1fr));gap:6px;">' + langButtonsHtml + '</div>' +
      '<div style="font-size:12px;font-weight:900;color:#2EE6D3;margin-top:6px;">Select Colorblind & High-Contrast Palette (4 Modes):</div>' +
      '<div style="display:flex;flex-direction:column;gap:6px;">' + modeButtonsHtml + '</div>' +
      '</div>';

    modal.style.display = "flex";
    return modal;
  }

  function closeI18nA11yModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("i18n-a11y-modal");
    if (modal) modal.style.display = "none";
  }

  const SynapseI18nAccessibility = {
    VERSION: SUITE_VERSION,
    SUPPORTED_LANGUAGES: SUPPORTED_LANGUAGES,
    COLORBLIND_PALETTES: COLORBLIND_PALETTES,
    STRINGS: I18N_STRINGS,
    currentLanguage: "EN",
    currentColorblindMode: "standard",
    setLanguage: setLanguage,
    getLanguage: function () { return SynapseI18nAccessibility.currentLanguage; },
    t: translateKey,
    translate: translateKey,
    getSupportedLanguages: function () { return SUPPORTED_LANGUAGES.slice(); },
    setColorblindMode: setColorblindMode,
    getColorblindMode: function () { return SynapseI18nAccessibility.currentColorblindMode; },
    getPalettes: function () { return COLORBLIND_PALETTES; },
    openI18nA11yModal: openI18nA11yModal,
    closeI18nA11yModal: closeI18nA11yModal
  };

  // ==========================================================================
  // 5. injectAaaStudioCommandPills() -- NON-INTRUSIVE STUDIO COMMAND BAR
  //    Mounts inside #sakuga-anim-studio-bar / #sakuga-anim-engine-bar (inside
  //    #deckbuilder-modal) and #dev-camera-drawer without affecting #board-3d-slab
  //    or #standalone-deck-sanctum bounding boxes or E2E autotests!
  // ==========================================================================
  function injectAaaStudioCommandPills() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;

    // Ensure #sakuga-anim-engine-bar is mounted if SynapseSakugaAnimEngine is present
    if (
      globalScope.SynapseSakugaAnimEngine &&
      typeof globalScope.SynapseSakugaAnimEngine.injectSakugaAnimStudioBar === "function" &&
      !doc.getElementById("sakuga-anim-engine-bar")
    ) {
      globalScope.SynapseSakugaAnimEngine.injectSakugaAnimStudioBar();
    }

    let targetBar =
      doc.getElementById("sakuga-anim-studio-bar") ||
      doc.getElementById("sakuga-anim-engine-bar");

    if (!targetBar) {
      const deckModal = doc.getElementById("deckbuilder-modal");
      const anchor =
        doc.getElementById("multiplatform-crypto-vault-bar") ||
        doc.getElementById("deckbuilder-squad-summary") ||
        (deckModal && deckModal.querySelector(".modal-box")) ||
        doc.getElementById("top-bar");

      if (anchor) {
        targetBar = doc.createElement("div");
        targetBar.id = "sakuga-anim-studio-bar";
        targetBar.style.cssText =
          "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;" +
          "background:rgba(15,23,42,0.95);border:1px solid rgba(255,184,0,0.48);border-radius:8px;" +
          "padding:6px 10px;font-size:12px;color:#F8FAFC;";
        if (anchor.id === "deckbuilder-squad-summary" || anchor.id === "multiplatform-crypto-vault-bar") {
          anchor.insertAdjacentElement("afterend", targetBar);
        } else {
          anchor.appendChild(targetBar);
        }
      }
    }

    let pillsContainer = doc.getElementById("aaa-studio-command-pills");
    if (!pillsContainer) {
      pillsContainer = doc.createElement("div");
      pillsContainer.id = "aaa-studio-command-pills";
      pillsContainer.style.cssText = "display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;";
      if (targetBar) {
        targetBar.appendChild(pillsContainer);
      } else {
        const devDrawer = doc.getElementById("dev-camera-drawer");
        if (devDrawer) devDrawer.appendChild(pillsContainer);
      }
    }

    pillsContainer.innerHTML =
      '<button type="button" id="btn-pill-mcts-oracle" onclick="window.SynapseAlphaZeroMCTS.openMctsOracleModal()" ' +
      'style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;border:1px solid #A855F7;background:rgba(168,85,247,0.18);color:#F3E8FF;font-size:12px;font-weight:800;cursor:pointer;">' +
      iconHtml("mcts_brain", 13) + '<span>MCTS Oracle</span></button>' +
      '<button type="button" id="btn-pill-chronicle-map" onclick="window.SynapseIvaliceChronicleMap.openChronicleMapModal()" ' +
      'style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;border:1px solid #FFB800;background:rgba(255,184,0,0.16);color:#FEF08A;font-size:12px;font-weight:800;cursor:pointer;">' +
      iconHtml("chronicle_map", 13) + '<span>15-Stage Map</span></button>' +
      '<button type="button" id="btn-pill-replay-ladder" onclick="window.SynapseReplayGhostLadder.openReplayLadderModal()" ' +
      'style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;border:1px solid #2EE6D3;background:rgba(46,230,211,0.16);color:#CCFBF1;font-size:12px;font-weight:800;cursor:pointer;">' +
      iconHtml("replay_film", 13) + '<span>Replay &amp; Puzzles</span></button>' +
      '<button type="button" id="btn-pill-i18n-a11y" onclick="window.SynapseI18nAccessibility.openI18nA11yModal()" ' +
      'style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;border:1px solid #00E5FF;background:rgba(0,229,255,0.16);color:#E0F2FE;font-size:12px;font-weight:800;cursor:pointer;">' +
      iconHtml("globe_i18n", 13) + '<span>10-Lang / A11y</span></button>';

    return pillsContainer;
  }

  function hookAaaStudioRuntime() {
    registerSovereignIcons();
    injectAaaStudioCommandPills();

    // Hook openDeckbuilderModal so studio pills are always present when opened
    if (
      typeof globalScope.openDeckbuilderModal === "function" &&
      !globalScope.openDeckbuilderModal.__aaaStudioPillsWrapped
    ) {
      const origOpen = globalScope.openDeckbuilderModal;
      const wrappedOpen = function () {
        const res = origOpen.apply(this, arguments);
        injectAaaStudioCommandPills();
        return res;
      };
      wrappedOpen.__aaaStudioPillsWrapped = true;
      globalScope.openDeckbuilderModal = wrappedOpen;
    }

    // Hook handleSlotClick to automatically record turn actions into CF-RPL1 replay history
    if (
      typeof globalScope.handleSlotClick === "function" &&
      !globalScope.handleSlotClick.__aaaReplayRecorderWrapped
    ) {
      const origSlotClick = globalScope.handleSlotClick;
      const wrappedSlotClick = function (r, c) {
        const st = globalScope.state;
        const cardBefore = st && Array.isArray(st.hand) ? st.hand[st.selectedHandIdx || 0] : null;
        const res = origSlotClick.apply(this, arguments);
        if (st && st.grid && st.grid[r] && st.grid[r][c] && st.grid[r][c].cardId) {
          recordAction({
            actor: "player",
            actionType: "DEPLOY",
            cardId: st.grid[r][c].cardId || cardBefore,
            slotIndex: r * 3 + c,
            r: r,
            c: c,
            flipsCount: Array.isArray(st.lastCaptureEvents) ? st.lastCaptureEvents.length : 0
          });
        }
        return res;
      };
      wrappedSlotClick.__aaaReplayRecorderWrapped = true;
      globalScope.handleSlotClick = wrappedSlotClick;
    }
  }

  globalScope.SynapseAlphaZeroMCTS = SynapseAlphaZeroMCTS;
  globalScope.SynapseIvaliceChronicleMap = SynapseIvaliceChronicleMap;
  globalScope.SynapseReplayGhostLadder = SynapseReplayGhostLadder;
  globalScope.SynapseI18nAccessibility = SynapseI18nAccessibility;
  globalScope.injectAaaStudioCommandPills = injectAaaStudioCommandPills;
  globalScope.SynapseAaaStudioSuite = {
    VERSION: SUITE_VERSION,
    MCTS: SynapseAlphaZeroMCTS,
    ChronicleMap: SynapseIvaliceChronicleMap,
    ReplayLadder: SynapseReplayGhostLadder,
    I18nA11y: SynapseI18nAccessibility,
    injectAaaStudioCommandPills: injectAaaStudioCommandPills
  };

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", hookAaaStudioRuntime);
    } else {
      hookAaaStudioRuntime();
    }
  }
  if (typeof globalScope.addEventListener === "function") {
    globalScope.addEventListener("load", hookAaaStudioRuntime);
  }
})(typeof window !== "undefined" ? window : globalThis);
