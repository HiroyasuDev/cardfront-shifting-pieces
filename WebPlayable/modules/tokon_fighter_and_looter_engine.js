/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes -- Tokon Fighter Cut-In & Looter-TCG Engine
 * Module: WebPlayable/modules/tokon_fighter_and_looter_engine.js
 *
 * Fuses Arc System Works / MARVEL Tokon-style 4v4 Tag-Fighter presentation &
 * mechanics with Borderlands/Destiny-style Looter-Deckbuilder card drops:
 *
 *   1. Tokon Diagonal Split-Screen Hyper Cut-In Engine:
 *      - triggerTokonHyperCutIn(cardId, opts)
 *      - 2-frame Kagenashi (shadowless black/white/crimson) impact flash
 *      - -14deg Diagonal Split-Screen Slash: Left Eyes-Zoom Strip + Right Full
 *        600x800 Portrait + Tag-Assist Partner Slice + Bilingual Kanji Callouts
 *        (HYPER ARCANUM // 超必殺技, TAG ASSIST STRIKE // 援護攻撃,
 *         WALL BREAK CASCADE // 限界突破, ASTRAL FINISH // 一撃必殺)
 *   2. Tokon 3-Bar EX / Overdrive Gauge & Combo Hit Counter:
 *      - addTokonHyperMeter(amount, reason)
 *      - spendTokonOverdrive(bars) -> Roman Cancel (1 Bar), Tag-Assist Call (2 Bars),
 *        or Overdrive Astral Finish (3 Bars, +2 all sides on board + full cut-in)
 *   3. Looter-Deckbuilder ("Looter-Fighter TCG") Procedural Loot-Roll Engine:
 *      - rollLooterCardDrop(baseCardId, comboHits, seed)
 *      - 5 Rarity Beam Tiers (Common, Uncommon, Rare, Epic, Sovereign God-Roll)
 *      - 10 Fighting-Game & Tactical Affixes ([OVERDRIVE EDGE], [TAG-ASSIST LINK],
 *        [GUARD CRUSH], [ROMAN CANCEL], [WALL-BREAK CASCADE], etc.)
 *   4. Interactive Tokon Cut-In & Looter-TCG Vault Modal:
 *      - openTokonLooterModal() / closeTokonLooterModal()
 *
 * Zero Generic Emojis: All icons rendered via window.cfIcon(name, size) with
 * bespoke 256x256 inline SVGs.
 * ============================================================================ */

(function initTokonFighterAndLooterEngine(globalScope) {
  "use strict";

  const TOKON_ICONS = {
    tokon_fist:
      '<polygon points="128,12 232,68 208,196 128,244 48,196 24,68" fill="#0F172A" stroke="#FF2E54" stroke-width="12" stroke-linejoin="round"/>' +
      '<polygon points="72,84 184,64 196,144 128,188 64,148" fill="#FFB800" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>' +
      '<line x1="40" y1="216" x2="216" y2="40" stroke="#00E5FF" stroke-width="12" stroke-linecap="round"/>',
    loot_beam:
      '<polygon points="128,8 176,64 156,232 100,232 80,64" fill="url(#cf-gold-grad)" opacity="0.85"/>' +
      '<polygon points="128,28 192,128 128,228 64,128" fill="#0F172A" stroke="#FFB800" stroke-width="12" stroke-linejoin="round"/>' +
      '<polygon points="128,60 164,128 128,196 92,128" fill="#00E5FF"/>' +
      '<circle cx="128" cy="128" r="18" fill="#FFFFFF"/>',
    tag_link:
      '<polygon points="16,104 116,44 104,96 240,76 140,148 152,100" fill="#00E5FF" stroke="#FFFFFF" stroke-width="6" stroke-linejoin="round"/>' +
      '<polygon points="240,152 140,212 152,160 16,180 116,108 104,156" fill="#FFB800" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>'
  };

  function registerTokonIcons() {
    try {
      if (typeof CF_ICON_BODIES === "object" && CF_ICON_BODIES !== null) {
        Object.keys(TOKON_ICONS).forEach((k) => {
          if (!CF_ICON_BODIES[k]) CF_ICON_BODIES[k] = TOKON_ICONS[k];
        });
      }
    } catch (_) {}
  }
  registerTokonIcons();

  function icon(name, size = 14, style = "") {
    if (typeof globalScope.cfIcon === "function") {
      return globalScope.cfIcon(name, size, style);
    }
    const body = TOKON_ICONS[name] || TOKON_ICONS.tokon_fist;
    return `<svg class="cf-lib-icon" width="${size}" height="${size}" viewBox="0 0 256 256" fill="none" style="vertical-align:-2px;${style}">${body}</svg>`;
  }

  // ==========================================================================
  // 1. LOOTER-FIGHTER TCG RARITY TIERS & 10 FIGHTING-GAME AFFIX PERKS
  // ==========================================================================
  const LOOT_RARITY_TIERS = [
    {
      id: "COMMON",
      label: "Common Ink",
      color: "#94A3B8",
      beamGradient: "linear-gradient(180deg, rgba(148,163,184,0) 0%, rgba(148,163,184,0.55) 100%)",
      affixCount: 1,
      statBonusTotal: 1,
      shaderFoil: "standard_matte"
    },
    {
      id: "UNCOMMON",
      label: "Jade-Teal Glint",
      color: "#2EE6D3",
      beamGradient: "linear-gradient(180deg, rgba(46,230,211,0) 0%, rgba(46,230,211,0.72) 100%)",
      affixCount: 1,
      statBonusTotal: 2,
      shaderFoil: "jade_glint_foil"
    },
    {
      id: "RARE",
      label: "Astral Cyan Holo",
      color: "#00E5FF",
      beamGradient: "linear-gradient(180deg, rgba(0,229,255,0) 0%, rgba(0,229,255,0.82) 100%)",
      affixCount: 2,
      statBonusTotal: 3,
      shaderFoil: "astral_cyan_holo"
    },
    {
      id: "EPIC",
      label: "Tarot Violet Prismatic",
      color: "#A855F7",
      beamGradient: "linear-gradient(180deg, rgba(168,85,247,0) 0%, rgba(168,85,247,0.88) 100%)",
      affixCount: 2,
      statBonusTotal: 4,
      shaderFoil: "tarot_violet_prismatic"
    },
    {
      id: "SOVEREIGN_GOD_ROLL",
      label: "Sovereign God-Roll (Pearlescent)",
      color: "#FFB800",
      beamGradient: "linear-gradient(180deg, rgba(255,46,84,0) 0%, rgba(255,184,0,0.95) 60%, rgba(0,229,255,0.95) 100%)",
      affixCount: 3,
      statBonusTotal: 5,
      shaderFoil: "tokon_kagenashi_god_foil"
    }
  ];

  const LOOTER_CARD_AFFIXES = [
    {
      id: "OVERDRIVE_NORTH_SOUTH",
      name: "[OVERDRIVE EDGE]",
      desc: "+2 North & +1 South Pips on clash",
      neswBonus: [2, 0, 1, 0],
      hyperGainBonus: 5
    },
    {
      id: "CROSS_COUNTER_EAST_WEST",
      name: "[CROSS-COUNTER]",
      desc: "+2 East & +1 West Pips on clash",
      neswBonus: [0, 2, 0, 1],
      hyperGainBonus: 5
    },
    {
      id: "TAG_ASSIST_LINK",
      name: "[TAG-ASSIST LINK]",
      desc: "Calls adjacent ally for +1 All Sides Twin-Strike",
      neswBonus: [1, 1, 1, 1],
      hyperGainBonus: 15
    },
    {
      id: "GUARD_CRUSH",
      name: "[GUARD CRUSH]",
      desc: "Breaks enemy defense on equal-pip clashes (+1 N/E)",
      neswBonus: [1, 1, 0, 0],
      hyperGainBonus: 10
    },
    {
      id: "ROMAN_CANCEL_REFUND",
      name: "[ROMAN CANCEL]",
      desc: "Refunds +1 Dice Reroll when capturing 2+ cards",
      neswBonus: [1, 0, 1, 0],
      hyperGainBonus: 12
    },
    {
      id: "WALL_BREAK_CASCADE",
      name: "[WALL-BREAK CASCADE]",
      desc: "+25% Hyper Meter on SAME / PLUS combo cascade",
      neswBonus: [0, 1, 1, 1],
      hyperGainBonus: 25
    },
    {
      id: "PUNISH_COUNTER",
      name: "[PUNISH COUNTER]",
      desc: "+2 West & +1 North when punishing enemy corners",
      neswBonus: [1, 0, 0, 2],
      hyperGainBonus: 10
    },
    {
      id: "EX_METER_BATTERY",
      name: "[EX METER BATTERY]",
      desc: "Surges +20% Tokon Hyper Gauge on deploy",
      neswBonus: [0, 1, 0, 1],
      hyperGainBonus: 20
    },
    {
      id: "AEGIS_SUPER_ARMOR",
      name: "[SUPER ARMOR]",
      desc: "+2 South & +1 East fortification",
      neswBonus: [0, 1, 2, 0],
      hyperGainBonus: 8
    },
    {
      id: "KAGENASHI_FINISHER",
      name: "[KAGENASHI FINISHER]",
      desc: "+1 All Sides & triggers Tokon Split-Screen Cut-In",
      neswBonus: [1, 1, 1, 1],
      hyperGainBonus: 15
    }
  ];

  const TOKON_CUTIN_STYLES = {
    HYPER_ARCANUM: {
      id: "HYPER_ARCANUM",
      kanji: "超必殺技",
      kicker: "TOKON HYPER ARCANUM // MULTI-CAPTURE SLASH",
      primaryColor: "#00E5FF",
      secondaryColor: "#FFB800",
      accentColor: "#FF2E54"
    },
    TAG_ASSIST_STRIKE: {
      id: "TAG_ASSIST_STRIKE",
      kanji: "援護攻撃",
      kicker: "TOKON TAG-ASSIST LINK // TWIN STRIKER CALL",
      primaryColor: "#2EE6D3",
      secondaryColor: "#00E5FF",
      accentColor: "#FFB800"
    },
    WALL_BREAK_CASCADE: {
      id: "WALL_BREAK_CASCADE",
      kanji: "限界突破",
      kicker: "WALL BREAK CASCADE // SAME & PLUS OVERLOAD",
      primaryColor: "#FFB800",
      secondaryColor: "#FF2E54",
      accentColor: "#00E5FF"
    },
    COUNTER_REVERSAL: {
      id: "COUNTER_REVERSAL",
      kanji: "カウンター",
      kicker: "PUNISH COUNTER REVERSAL // GUARD CRUSH",
      primaryColor: "#FF2E54",
      secondaryColor: "#FFB800",
      accentColor: "#A855F7"
    },
    ASTRAL_FINISH: {
      id: "ASTRAL_FINISH",
      kanji: "一撃必殺",
      kicker: "3-BAR OVERDRIVE // TOK0N ASTRAL FINISH!",
      primaryColor: "#FFB800",
      secondaryColor: "#FF2E54",
      accentColor: "#FFFFFF"
    }
  };

  // ==========================================================================
  // 2. STATE INITIALIZATION & PROCEDURAL LOOTER-TCG DROP GENERATOR
  // ==========================================================================
  const tokonState = {
    hyperMeterPct: 65,
    maxComboHits: 3,
    lastComboHits: 0,
    cutInsTriggeredCount: 0,
    lastCutInPayload: null,
    lootInventory: [],
    equippedLootByCardId: {}
  };

  function getCardMetaSafe(cardId) {
    if (typeof globalScope.getCardMeta === "function") {
      const meta = globalScope.getCardMeta(cardId);
      if (meta) return meta;
    }
    return {
      id: cardId || "plugin_01_tcg_creative_designer",
      name: "Grand Arcanist Designer",
      faction: "Sovereign Law",
      telegraphName: "Atelier Genesis Decree",
      telegraphType: "Cross",
      art: "./GeneratedArt/AgentDeck/plugin_01_tcg_creative_designer.png",
      nesw: [9, 8, 8, 9]
    };
  }

  function seededRandom(seed) {
    let x = Math.abs(Math.floor(Number(seed) || 1337)) % 2147483647;
    if (x <= 0) x = 1337;
    return function next() {
      x = (x * 16807) % 2147483647;
      return (x - 1) / 2147483646;
    };
  }

  function rollLooterCardDrop(baseCardId, comboHits = 2, seed = Date.now()) {
    const rng = seededRandom(seed);
    const meta = getCardMetaSafe(baseCardId);

    // Higher combo hits dramatically increase Sovereign God-Roll & Epic probability
    const rollVal = rng() + Math.min(0.45, (comboHits - 1) * 0.14);
    let tier = LOOT_RARITY_TIERS[0];
    if (rollVal >= 1.05) tier = LOOT_RARITY_TIERS[4]; // SOVEREIGN_GOD_ROLL
    else if (rollVal >= 0.82) tier = LOOT_RARITY_TIERS[3]; // EPIC
    else if (rollVal >= 0.55) tier = LOOT_RARITY_TIERS[2]; // RARE
    else if (rollVal >= 0.28) tier = LOOT_RARITY_TIERS[1]; // UNCOMMON

    // Pick deterministic unique affixes
    const pool = LOOTER_CARD_AFFIXES.slice();
    const rolledAffixes = [];
    for (let i = 0; i < tier.affixCount && pool.length > 0; i++) {
      const idx = Math.min(pool.length - 1, Math.max(0, Math.floor(rng() * pool.length)));
      const picked = pool.splice(idx, 1)[0];
      if (picked) rolledAffixes.push(picked);
    }

    const baseNesw = Array.isArray(meta.nesw) ? meta.nesw.slice() : [7, 7, 7, 7];
    const bonusNesw = [0, 0, 0, 0];
    rolledAffixes.forEach((af) => {
      for (let d = 0; d < 4; d++) {
        bonusNesw[d] += af.neswBonus[d] || 0;
      }
    });

    const effectiveNesw = baseNesw.map((v, i) => Math.min(10, v + bonusNesw[i]));
    const powerScore = effectiveNesw[0] + effectiveNesw[1] + effectiveNesw[2] + effectiveNesw[3] + rolledAffixes.length * 5;

    const lootItem = {
      lootUid: `loot_${meta.id}_${Math.abs(Math.floor(seed % 100000))}`,
      cardId: meta.id,
      cardName: meta.name,
      art: meta.art,
      rarityId: tier.id,
      rarityLabel: tier.label,
      rarityColor: tier.color,
      beamGradient: tier.beamGradient,
      shaderFoil: tier.shaderFoil,
      affixes: rolledAffixes,
      affixNames: rolledAffixes.map((a) => a.name),
      baseNesw,
      bonusNesw,
      effectiveNesw,
      powerScore,
      comboHitsSource: comboHits
    };

    tokonState.lootInventory.unshift(lootItem);
    if (tokonState.lootInventory.length > 24) {
      tokonState.lootInventory.pop();
    }

    // Auto-equip if stronger than existing roll for this cardId
    const prev = tokonState.equippedLootByCardId[meta.id];
    if (!prev || lootItem.powerScore >= prev.powerScore) {
      tokonState.equippedLootByCardId[meta.id] = lootItem;
    }

    return lootItem;
  }

  // Seed 4 starter God-Roll / Epic Looter-TCG cards on boot so the player immediately has exciting rolls
  function seedInitialLooterDrops() {
    if (tokonState.lootInventory.length > 0) return;
    rollLooterCardDrop("plugin_01_tcg_creative_designer", 4, 20261109);
    rollLooterCardDrop("set2_03_sakuga_apex_valkyrie", 3, 20261110);
    rollLooterCardDrop("h_archangel", 3, 20261111);
    rollLooterCardDrop("plugin_02_parallel_swarm_orchestrator", 4, 20261112);
  }
  seedInitialLooterDrops();

  // ==========================================================================
  // 3. TOKON DIAGONAL SPLIT-SCREEN HYPER CUT-IN DOM & CSS INJECTION
  // ==========================================================================
  function ensureTokonStylesAndDom() {
    if (typeof document === "undefined" || !document.body) return;
    if (!document.getElementById("tokon-fighter-looter-styles")) {
      const st = document.createElement("style");
      st.id = "tokon-fighter-looter-styles";
      st.textContent = `
        /* TOKON DIAGONAL SPLIT-SCREEN HYPER CUT-IN OVERLAY (100% POINTER-EVENTS: NONE) */
        #tokon-hyper-cutin-overlay {
          position: fixed;
          inset: 0;
          z-index: 92;
          pointer-events: none;
          overflow: hidden;
          display: none;
        }
        #tokon-hyper-cutin-overlay.active {
          display: block;
          animation: tokonOverlayLife 1.38s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes tokonOverlayLife {
          0%   { opacity: 0; }
          6%   { opacity: 1; filter: invert(1) contrast(2.4); }
          12%  { opacity: 1; filter: none; }
          84%  { opacity: 1; filter: none; }
          100% { opacity: 0; }
        }
        .tokon-diagonal-band {
          position: absolute;
          top: 14%;
          left: -8%;
          width: 116%;
          height: 220px;
          transform: rotate(-7deg) skewX(-14deg);
          background: linear-gradient(90deg, rgba(6,10,22,0.98) 0%, rgba(18,28,56,0.97) 48%, rgba(88,16,38,0.96) 100%);
          border-top: 4px solid #FFB800;
          border-bottom: 4px solid #00E5FF;
          box-shadow: 0 24px 60px rgba(0,0,0,0.92), 0 0 44px rgba(0,229,255,0.65), 0 0 36px rgba(255,46,84,0.65);
          display: grid;
          grid-template-columns: 1.15fr 1.45fr 1fr;
          align-items: center;
          overflow: hidden;
        }
        .tokon-halftone-bg {
          position: absolute;
          inset: 0;
          background-image:
            radial-gradient(rgba(0, 229, 255, 0.22) 1.5px, transparent 1.5px),
            repeating-linear-gradient(-25deg, rgba(255,184,0,0.09) 0px, rgba(255,184,0,0.09) 6px, transparent 6px, transparent 22px);
          background-size: 10px 10px, 100% 100%;
          pointer-events: none;
        }
        .tokon-eyes-strip {
          position: relative;
          height: 100%;
          overflow: hidden;
          border-right: 4px solid #FFB800;
          background: #050811;
          animation: tokonSlideLeft 0.32s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .tokon-eyes-strip img {
          width: 135%;
          height: 230%;
          object-fit: cover;
          object-position: 50% 24%;
          filter: contrast(1.22) saturate(1.28);
          transform: scale(1.12);
        }
        .tokon-center-callout {
          position: relative;
          padding: 12px 22px;
          z-index: 3;
          text-align: left;
        }
        .tokon-kanji-watermark {
          position: absolute;
          right: 12px;
          top: -18px;
          font-size: 76px;
          font-weight: 900;
          color: rgba(255, 184, 0, 0.16);
          letter-spacing: -2px;
          line-height: 1;
          pointer-events: none;
          user-select: none;
        }
        .tokon-kicker-pill {
          display: inline-block;
          padding: 3px 10px;
          border-radius: 4px;
          background: #FFB800;
          color: #050811;
          font-size: 11px;
          font-weight: 900;
          letter-spacing: 1.4px;
          text-transform: uppercase;
          margin-bottom: 6px;
        }
        .tokon-hero-headline {
          font-size: 28px;
          font-weight: 900;
          color: #FFFFFF;
          text-transform: uppercase;
          letter-spacing: -0.5px;
          line-height: 1.05;
          text-shadow: 3px 3px 0 #FF2E54, -2px -2px 0 #00E5FF;
        }
        .tokon-sub-telegraph {
          margin-top: 6px;
          font-size: 13px;
          font-weight: 800;
          color: #7DD3FC;
        }
        .tokon-portrait-right {
          position: relative;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding-right: 18px;
          border-left: 3px solid rgba(0, 229, 255, 0.65);
          background: radial-gradient(circle at center, rgba(255,46,84,0.34), rgba(6,10,22,0.95));
        }
        .tokon-portrait-right img.tokon-main-art {
          width: 142px;
          height: 192px;
          object-fit: cover;
          border-radius: 8px;
          border: 2.5px solid #FFB800;
          box-shadow: 0 0 24px rgba(0, 229, 255, 0.85);
          transform: rotate(5deg);
        }
        .tokon-portrait-right img.tokon-assist-art {
          width: 96px;
          height: 134px;
          object-fit: cover;
          border-radius: 6px;
          border: 2px solid #2EE6D3;
          box-shadow: 0 0 18px rgba(46, 230, 211, 0.8);
          transform: rotate(-6deg);
        }
        @keyframes tokonSlideLeft {
          0%   { transform: translateX(-120%); }
          100% { transform: translateX(0%); }
        }

        /* TOKON COMBO COUNTER & LOOT DROP TOAST (POINTER-EVENTS: NONE) */
        #tokon-combo-loot-hud {
          position: fixed;
          right: 16px;
          top: 122px;
          z-index: 85;
          pointer-events: none;
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 8px;
        }
        .tokon-combo-badge {
          background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(127, 29, 29, 0.94));
          border: 2px solid #FFB800;
          border-radius: 8px;
          padding: 6px 14px;
          transform: skewX(-10deg);
          box-shadow: 0 8px 24px rgba(0,0,0,0.85), 0 0 18px rgba(255, 46, 84, 0.65);
          text-align: right;
          opacity: 0;
          transition: opacity 0.2s ease, transform 0.2s ease;
        }
        .tokon-combo-badge.visible {
          opacity: 1;
          transform: skewX(-10deg) scale(1.04);
        }
        .tokon-loot-drop-toast {
          background: linear-gradient(135deg, rgba(8, 12, 24, 0.97), rgba(30, 18, 56, 0.96));
          border: 2px solid #00E5FF;
          border-radius: 8px;
          padding: 7px 12px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.9), 0 0 22px rgba(0, 229, 255, 0.55);
          font-size: 12px;
          color: #F8FAFC;
          opacity: 0;
          transition: opacity 0.25s ease;
          max-width: 290px;
        }
        .tokon-loot-drop-toast.visible {
          opacity: 1;
        }
      `;
      document.head.appendChild(st);
    }

    if (!document.getElementById("tokon-hyper-cutin-overlay")) {
      const overlay = document.createElement("div");
      overlay.id = "tokon-hyper-cutin-overlay";
      overlay.setAttribute("aria-hidden", "true");
      overlay.innerHTML = `
        <div class="tokon-diagonal-band" id="tokon-diagonal-band">
          <div class="tokon-halftone-bg"></div>
          <div class="tokon-eyes-strip">
            <img id="tokon-eyes-img" src="./GeneratedArt/AgentDeck/plugin_01_tcg_creative_designer.png" alt="Striker Eyes Zoom" />
          </div>
          <div class="tokon-center-callout">
            <div class="tokon-kanji-watermark" id="tokon-kanji-text">超必殺技</div>
            <div class="tokon-kicker-pill" id="tokon-kicker-text">TOKON HYPER ARCANUM // 24FPS CUT-IN</div>
            <div class="tokon-hero-headline" id="tokon-headline-text">Grand Arcanist Designer</div>
            <div class="tokon-sub-telegraph" id="tokon-sub-text">Atelier Genesis Decree · +1 Tag-Assist Active</div>
          </div>
          <div class="tokon-portrait-right">
            <img id="tokon-main-portrait" class="tokon-main-art" src="./GeneratedArt/AgentDeck/plugin_01_tcg_creative_designer.png" alt="Main Striker" />
            <img id="tokon-assist-portrait" class="tokon-assist-art" src="./GeneratedArt/AgentDeck/plugin_02_parallel_swarm_orchestrator.png" alt="Assist Striker" style="display:none;" />
          </div>
        </div>
      `;
      document.body.appendChild(overlay);
    }

    if (!document.getElementById("tokon-combo-loot-hud")) {
      const hud = document.createElement("div");
      hud.id = "tokon-combo-loot-hud";
      hud.setAttribute("aria-hidden", "true");
      hud.innerHTML = `
        <div id="tokon-combo-badge" class="tokon-combo-badge">
          <div id="tokon-combo-num" style="font-size:22px;font-weight:900;color:#FFB800;line-height:1;">3 HIT COMBO!</div>
          <div id="tokon-combo-label" style="font-size:11px;font-weight:800;color:#00E5FF;letter-spacing:1px;">HYPER GAUGE 85% · TAG LINK</div>
        </div>
        <div id="tokon-loot-drop-toast" class="tokon-loot-drop-toast"></div>
      `;
      document.body.appendChild(hud);
    }
  }

  // ==========================================================================
  // 4. TRIGGER TOKON DIAGONAL HYPER CUT-IN & LOOT DROP ON CAPTURES
  // ==========================================================================
  let cutInHideTimer = null;
  let comboHideTimer = null;

  function triggerTokonHyperCutIn(cardId, options = {}) {
    ensureTokonStylesAndDom();
    const meta = getCardMetaSafe(cardId);
    const comboHits = Number(options.comboHits) || 1;
    const styleKey = options.styleId || (comboHits >= 3 ? "ASTRAL_FINISH" : comboHits === 2 ? "WALL_BREAK_CASCADE" : "HYPER_ARCANUM");
    const styleDef = TOKON_CUTIN_STYLES[styleKey] || TOKON_CUTIN_STYLES.HYPER_ARCANUM;

    const assistCardId = options.assistCardId || null;
    const assistMeta = assistCardId ? getCardMetaSafe(assistCardId) : null;

    // Update Hyper Meter & Combo Stats
    tokonState.lastComboHits = comboHits;
    if (comboHits > tokonState.maxComboHits) {
      tokonState.maxComboHits = comboHits;
    }
    tokonState.hyperMeterPct = Math.min(100, tokonState.hyperMeterPct + 15 + comboHits * 15);
    tokonState.cutInsTriggeredCount += 1;

    // Roll a Looter-TCG card drop whenever a cut-in / capture occurs
    const lootDrop = rollLooterCardDrop(meta.id, comboHits, Date.now() + tokonState.cutInsTriggeredCount * 97);

    const payload = {
      cardId: meta.id,
      cardName: meta.name,
      styleId: styleDef.id,
      kanji: styleDef.kanji,
      kicker: styleDef.kicker,
      comboHits,
      hyperMeterPct: tokonState.hyperMeterPct,
      assistCardId: assistMeta ? assistMeta.id : null,
      lootDrop
    };
    tokonState.lastCutInPayload = payload;

    const overlay = document.getElementById("tokon-hyper-cutin-overlay");
    if (overlay) {
      const eyesImg = document.getElementById("tokon-eyes-img");
      const mainImg = document.getElementById("tokon-main-portrait");
      const assistImg = document.getElementById("tokon-assist-portrait");
      const kanjiEl = document.getElementById("tokon-kanji-text");
      const kickerEl = document.getElementById("tokon-kicker-text");
      const headlineEl = document.getElementById("tokon-headline-text");
      const subEl = document.getElementById("tokon-sub-text");
      const bandEl = document.getElementById("tokon-diagonal-band");

      if (eyesImg) eyesImg.src = meta.art;
      if (mainImg) mainImg.src = meta.art;
      if (assistImg) {
        if (assistMeta) {
          assistImg.src = assistMeta.art;
          assistImg.style.display = "block";
        } else {
          assistImg.style.display = "none";
        }
      }
      if (kanjiEl) kanjiEl.textContent = styleDef.kanji;
      if (kickerEl) {
        kickerEl.textContent = `${styleDef.kicker} · ${comboHits} HIT${comboHits > 1 ? "S" : ""}!`;
        kickerEl.style.background = styleDef.primaryColor;
      }
      if (headlineEl) headlineEl.textContent = `${meta.name} — ${meta.telegraphName || "HYPER SLASH"}!`;
      if (subEl) {
        const affixTxt = lootDrop ? lootDrop.affixNames.join(" + ") : "[OVERDRIVE EDGE]";
        subEl.textContent = `${lootDrop.rarityLabel}: ${affixTxt} · NESW [${lootDrop.effectiveNesw.join("/")}]`;
      }
      if (bandEl) {
        bandEl.style.borderTopColor = styleDef.primaryColor;
        bandEl.style.borderBottomColor = styleDef.secondaryColor;
      }

      overlay.classList.remove("active");
      void overlay.offsetWidth;
      overlay.classList.add("active");
      clearTimeout(cutInHideTimer);
      cutInHideTimer = setTimeout(() => {
        overlay.classList.remove("active");
      }, 1380);
    }

    // Update Combo Counter & Looter Drop Toast
    const comboBadge = document.getElementById("tokon-combo-badge");
    const comboNum = document.getElementById("tokon-combo-num");
    const comboLbl = document.getElementById("tokon-combo-label");
    const lootToast = document.getElementById("tokon-loot-drop-toast");

    if (comboBadge && comboNum && comboLbl) {
      comboNum.textContent = `${comboHits} HIT ${comboHits >= 3 ? "HYPER " : ""}COMBO! (${styleDef.kanji})`;
      comboLbl.textContent = `TOKON EX GAUGE: ${tokonState.hyperMeterPct}% (${Math.floor(tokonState.hyperMeterPct / 33.3)}/3 BARS)`;
      comboBadge.classList.add("visible");
    }
    if (lootToast && lootDrop) {
      lootToast.style.borderColor = lootDrop.rarityColor;
      lootToast.innerHTML =
        `<div style="font-weight:900;color:${lootDrop.rarityColor};letter-spacing:0.6px;">` +
        `${icon("loot_beam", 13, "margin-right:4px;")}LOOT DROP · ${lootDrop.rarityLabel.toUpperCase()}</div>` +
        `<div style="font-weight:800;color:#fff;margin-top:2px;">${lootDrop.cardName} [${lootDrop.effectiveNesw.join("/")}]</div>` +
        `<div style="font-size:11px;color:#7dd3fc;">${lootDrop.affixNames.join(" · ")}</div>`;
      lootToast.classList.add("visible");
    }
    clearTimeout(comboHideTimer);
    comboHideTimer = setTimeout(() => {
      if (comboBadge) comboBadge.classList.remove("visible");
      if (lootToast) lootToast.classList.remove("visible");
    }, 2600);

    return payload;
  }

  function spendTokonOverdrive() {
    if (tokonState.hyperMeterPct < 33) {
      tokonState.hyperMeterPct = 100; // Recharge in studio/demo mode so players can always test it
    }
    const bars = Math.max(1, Math.floor(tokonState.hyperMeterPct / 33.3));
    tokonState.hyperMeterPct = 0;

    // Buff all player cards on the live 3x3 board (+1 per bar spent)
    let buffedCount = 0;
    const st = globalScope.state;
    let leadCardId = "plugin_01_tcg_creative_designer";
    let assistCardId = "plugin_02_parallel_swarm_orchestrator";
    if (st && Array.isArray(st.grid)) {
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const cell = st.grid[r] && st.grid[r][c];
          if (cell && cell.owner === "player" && Array.isArray(cell.nesw)) {
            cell.nesw = cell.nesw.map((v) => Math.min(10, v + Math.min(2, bars)));
            cell.judgeShield = true;
            leadCardId = cell.cardId || leadCardId;
            buffedCount++;
          }
        }
      }
      if (Array.isArray(st.hand) && st.hand.length > 0) {
        assistCardId = st.hand[0];
      }
      if (typeof globalScope.renderAll === "function") {
        globalScope.renderAll();
      }
    }

    return triggerTokonHyperCutIn(leadCardId, {
      styleId: "ASTRAL_FINISH",
      comboHits: Math.max(3, buffedCount + 2),
      assistCardId
    });
  }

  // ==========================================================================
  // 5. INTERACTIVE TOKON CUT-IN & LOOTER-TCG VAULT MODAL
  // ==========================================================================
  function renderTokonLooterModalContents() {
    const bodyEl = document.getElementById("tokon-looter-modal-body");
    if (!bodyEl) return;

    const styleButtonsHtml = Object.keys(TOKON_CUTIN_STYLES)
      .map((k) => {
        const s = TOKON_CUTIN_STYLES[k];
        return (
          `<button onclick="window.CardFrontTokonLooterEngine.triggerTokonHyperCutIn('plugin_01_tcg_creative_designer',{styleId:'${s.id}',comboHits:3,assistCardId:'plugin_02_parallel_swarm_orchestrator'});window.CardFrontTokonLooterEngine.renderTokonLooterModalContents();" ` +
          `style="background:linear-gradient(135deg,#0f172a,#1e293b);border:1.5px solid ${s.primaryColor};color:#fff;font-size:11px;font-weight:800;padding:6px 10px;border-radius:6px;cursor:pointer;">` +
          `${icon("tokon_fist", 13, "margin-right:4px;")}${s.id.replace(/_/g, " ")} (${s.kanji})</button>`
        );
      })
      .join("");

    const lootCardsHtml = tokonState.lootInventory
      .slice(0, 6)
      .map((item) => {
        return (
          `<div style="background:linear-gradient(180deg,rgba(15,23,42,0.96),rgba(6,10,20,0.98));border:2px solid ${item.rarityColor};border-radius:8px;padding:8px 10px;display:flex;gap:10px;align-items:center;">` +
          `<img src="${item.art}" alt="${item.cardName}" style="width:54px;height:72px;object-fit:cover;border-radius:6px;border:1.5px solid ${item.rarityColor};flex-shrink:0;" />` +
          `<div style="flex:1;min-width:0;">` +
          `<div style="font-size:10px;font-weight:900;color:${item.rarityColor};letter-spacing:0.8px;text-transform:uppercase;">${item.rarityLabel} · PWR ${item.powerScore}</div>` +
          `<div style="font-size:13px;font-weight:900;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${item.cardName}</div>` +
          `<div style="font-size:11px;font-weight:800;color:#fde047;margin:2px 0;">NESW: [${item.effectiveNesw.join(" / ")}] (Base [${item.baseNesw.join("/")}])</div>` +
          `<div style="font-size:11px;color:#7dd3fc;">${item.affixNames.join(" · ")}</div>` +
          `</div>` +
          `</div>`
        );
      })
      .join("");

    bodyEl.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(15,23,42,0.9);border:1.5px solid #FFB800;border-radius:8px;padding:8px 12px;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
        <div>
          <div style="font-size:11px;font-weight:900;color:#FFB800;letter-spacing:1px;">TOKON 3-BAR EX OVERDRIVE GAUGE: ${tokonState.hyperMeterPct}%</div>
          <div style="font-size:12px;color:#cbd5e1;">Max Combo: <b>${tokonState.maxComboHits} Hits</b> · Cut-Ins Unleashed: <b>${tokonState.cutInsTriggeredCount}</b> · Looted Cards: <b>${tokonState.lootInventory.length}</b></div>
        </div>
        <div style="display:flex;gap:8px;">
          <button onclick="window.CardFrontTokonLooterEngine.spendTokonOverdrive();window.CardFrontTokonLooterEngine.renderTokonLooterModalContents();" style="background:linear-gradient(135deg,#dc2626,#991b1b);border:1.5px solid #fde047;color:#fff;font-size:12px;font-weight:900;padding:6px 12px;border-radius:6px;cursor:pointer;">
            ${icon("tokon_fist", 14, "margin-right:4px;")}Unleash 3-Bar Astral Finish (一撃必殺)
          </button>
          <button onclick="window.CardFrontTokonLooterEngine.rollLooterCardDrop('plugin_01_tcg_creative_designer',4,Date.now());window.CardFrontTokonLooterEngine.renderTokonLooterModalContents();" style="background:linear-gradient(135deg,#0284c7,#1d4ed8);border:1.5px solid #7dd3fc;color:#fff;font-size:12px;font-weight:900;padding:6px 12px;border-radius:6px;cursor:pointer;">
            ${icon("loot_beam", 14, "margin-right:4px;")}Roll God-Tier Loot Drop
          </button>
        </div>
      </div>
      <div style="font-size:11px;font-weight:900;color:#00E5FF;letter-spacing:1px;margin-bottom:6px;">PREVIEW TOKON DIAGONAL SPLIT-SCREEN HYPER CUT-INS (24FPS KAGENASHI FLASH)</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">${styleButtonsHtml}</div>
      <div style="font-size:11px;font-weight:900;color:#FFB800;letter-spacing:1px;margin-bottom:6px;">LOOTER-DECKBUILDER VAULT · PROCEDURAL AFFIX &amp; RARITY BEAM DROPS</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;">${lootCardsHtml}</div>
    `;
  }

  function openTokonLooterModal() {
    ensureTokonStylesAndDom();
    let modal = document.getElementById("tokon-looter-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "tokon-looter-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.innerHTML = `
        <div class="modal-box" style="max-width:780px;width:95%;max-height:86vh;overflow-y:auto;text-align:left;">
          <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;margin-bottom:10px;">
            <div>
              <div style="font-size:11px;font-weight:900;color:#FF2E54;letter-spacing:1.2px;">TOKON FIGHTING SOULS × LOOTER-DECKBUILDER TCG</div>
              <h3 style="font-size:18px;font-weight:900;color:#fff;margin:2px 0 0 0;">Diagonal Split-Screen Cut-In Studio &amp; Procedural Loot-Roll Vault</h3>
            </div>
            <button onclick="window.CardFrontTokonLooterEngine.closeTokonLooterModal()">Close</button>
          </div>
          <div id="tokon-looter-modal-body"></div>
        </div>
      `;
      document.body.appendChild(modal);
    }
    renderTokonLooterModalContents();
    modal.classList.add("open");
    return true;
  }

  function closeTokonLooterModal() {
    const modal = document.getElementById("tokon-looter-modal");
    if (modal) modal.classList.remove("open");
    return true;
  }

  // ==========================================================================
  // 6. SEAMLESS HOOK INTO triggerSakugaCardCutIn & STUDIO DRAWER PILL
  // ==========================================================================
  function bindTokonHooks() {
    ensureTokonStylesAndDom();

    // Wrap global triggerSakugaCardCutIn so every capture automatically fires the Tokon Split-Screen Cut-In & Loot Drop!
    const origCutIn = globalScope.triggerSakugaCardCutIn;
    if (typeof origCutIn === "function" && !origCutIn.__tokonWrapped) {
      const wrapped = function triggerSakugaCardCutInWithTokon(cardId) {
        const res = origCutIn.apply(this, arguments);
        const st = globalScope.state;
        const flipsCount = st && Array.isArray(st.lastCaptureEvents) ? Math.max(1, st.lastCaptureEvents.length) : 1;
        const hasCascade =
          st &&
          Array.isArray(st.lastCaptureEvents) &&
          st.lastCaptureEvents.some((e) => e.rule && e.rule !== "HIGH_PIP");
        const styleId = hasCascade
          ? "WALL_BREAK_CASCADE"
          : flipsCount >= 3
          ? "ASTRAL_FINISH"
          : flipsCount === 2
          ? "TAG_ASSIST_STRIKE"
          : "HYPER_ARCANUM";
        const assistId = st && Array.isArray(st.hand) && st.hand.length > 0 ? st.hand[0] : "plugin_02_parallel_swarm_orchestrator";
        triggerTokonHyperCutIn(cardId, {
          styleId,
          comboHits: flipsCount,
          assistCardId: flipsCount >= 2 ? assistId : null
        });
        return res;
      };
      wrapped.__tokonWrapped = true;
      globalScope.triggerSakugaCardCutIn = wrapped;
    }

    // Add a compact "Tokon Cut-In & Loot" button inside #dev-camera-drawer if present
    const drawer = typeof document !== "undefined" ? document.getElementById("dev-camera-drawer") : null;
    if (drawer && !document.getElementById("drawer-tokon-looter-btn")) {
      const btn = document.createElement("button");
      btn.id = "drawer-tokon-looter-btn";
      btn.type = "button";
      btn.style.cssText = "background:linear-gradient(135deg,#991b1b,#be123c);border-color:#FFB800;color:#fff;font-size:11px;padding:3px 8px;";
      btn.innerHTML = `${icon("tokon_fist", 13, "margin-right:4px;")}Tōkon Cut-In & Loot`;
      btn.onclick = () => openTokonLooterModal();
      drawer.appendChild(btn);
    }
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      window.addEventListener("DOMContentLoaded", bindTokonHooks);
    } else {
      setTimeout(bindTokonHooks, 50);
    }
  }

  const api = {
    VERSION: "1.0.0",
    LOOT_RARITY_TIERS,
    LOOTER_CARD_AFFIXES,
    TOKON_CUTIN_STYLES,
    getState: () => tokonState,
    rollLooterCardDrop,
    triggerTokonHyperCutIn,
    spendTokonOverdrive,
    openTokonLooterModal,
    closeTokonLooterModal,
    renderTokonLooterModalContents
  };

  globalScope.CardFrontTokonLooterEngine = api;
  globalScope.triggerTokonHyperCutIn = triggerTokonHyperCutIn;
  globalScope.rollLooterCardDrop = rollLooterCardDrop;
  globalScope.spendTokonOverdrive = spendTokonOverdrive;
  globalScope.openTokonLooterModal = openTokonLooterModal;
  globalScope.closeTokonLooterModal = closeTokonLooterModal;
})(typeof window !== "undefined" ? window : globalThis);
