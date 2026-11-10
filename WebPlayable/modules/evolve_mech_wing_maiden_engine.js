/**
 * CARDFRONT 3D: Cradle of Echoes — EVOLVE (進化前 -> 進化後) Card Transformation Engine
 * & Luxury Gunmetal-Filigree SR/UR Card Frame Renderer
 * Module: WebPlayable/modules/evolve_mech_wing_maiden_engine.js
 *
 * Exposes `window.CardFrontEvolveMaidenEngine`, `window.CardFrontModules.EvolveMaidenEngine`,
 * and top-level global functions/constants:
 *   - `EVOLVE_MECH_WING_MAIDEN_PAIRS` (length === 5: ev_01 .. ev_05 Base <-> Evolved pairs)
 *   - `EVOLVE_MECH_WING_CARDS_10` (length === 10: ev_01_base, ev_01_evo .. ev_05_base, ev_05_evo)
 *   - `evolveCardOnBoard(cellIndex, stateObj)`
 *   - `renderEvolveSrCardHtml(cardOrPair, showEvolved)`
 *   - `applyEvolveSrFrameStyle(enabled)`
 *   - `equipEvolveMechWingMaidenDeck()`
 *   - `openEvolveMaidenStudioModal(pairIndex)`
 *   - `closeEvolveMaidenStudioModal()`
 *
 * Art Direction & Engineering Contract:
 *   - ZERO living artists' names anywhere (`zeroLivingArtistNames: true`).
 *   - ZERO raw Unicode emojis in DOM text or buttons (100% inline 256x256 SVGs or crisp ASCII/Kanji tags).
 */
(function initCardFrontEvolveMaidenEngine(globalScope) {
  "use strict";

  // ==========================================================================
  // 1. 5 PAIRED MECH-WING MAIDENS (10 PLAYABLE BASE & EVOLVED FORMS)
  // ==========================================================================
  const EVOLVE_MECH_WING_MAIDEN_PAIRS = [
    {
      pairId: "ev_pair_01_rosalia",
      pairIndex: 0,
      baseId: "ev_01_base",
      evoId: "ev_01_evo",
      characterTitleEn: "Rosalia, Mech-Wing Sky Maiden",
      characterTitleJa: "機構翼の天翔少女・ロザリア",
      furiganaJa: "きこうよく の てんしょうしょうじょ",
      traitEn: "Angel · Mech",
      traitJa: "天使・機械",
      cardClass: "Follower",
      evolveCostEp: 1,
      baseCard: {
        id: "ev_01_base",
        slug: "ev_01_base_rosalia_mech_wing_maiden",
        pairedEvoId: "ev_01_evo",
        isEvolvedForm: false,
        name: "Rosalia, Mech-Wing Sky Maiden",
        nameJa: "機構翼の天翔少女・ロザリア",
        furiganaJa: "きこうよく の てんしょうしょうじょ",
        faction: "Aether",
        trait: "Angel · Mech / 天使・機械",
        rarity: "SR",
        setCode: "CF-EV01 SR",
        starCost: 2,
        cost: 2,
        evolveCostEp: 1,
        nesw: [6, 6, 5, 5],
        directionalSum: 22,
        sapphireAtkGem: 2,
        rubyDefGem: 4,
        keywords: ["[Evolve (1)]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_valkyrie.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_valkyrie_strip.png",
        telegraphType: "Emerald-Gold Mech-Pinion Glide",
        telegraphName: "Skyward Pinion Ward",
        telegraphColor: "#2EE6D3",
        telegraphDesc: "[Evolve (1)]: Evolve this card. [Ward / 守護] Protects adjacent friendly tiles from orthogonal capture.",
        rulesHtml: "[進化 EVOLVE (1)]: これを進化させる (Evolve this card).<br/>【守護 / WARD】 Adjacent friendly units gain +1 defense against orthogonal capture.",
        loreQuote: "「相応なんでしょう、私には、この鳥籠の世界が。飛べるだけで幸せなんです、だから、きっとこれでいい。」 — Soaring on articulated emerald-gold pinions across the sunset sanctuary."
      },
      evoCard: {
        id: "ev_01_evo",
        slug: "ev_01_evo_rosalia_arch_seraph_overdrive",
        pairedBaseId: "ev_01_base",
        isEvolvedForm: true,
        name: "Rosalia, Arch-Seraph Overdrive",
        nameJa: "機構翼の熾天女・ロザリア (進化後)",
        furiganaJa: "きこうよく の してんにょ",
        faction: "Aether",
        trait: "Angel · Mech / 天使・機械",
        rarity: "UR EVOLVED",
        setCode: "CF-EV01 UR-E",
        starCost: 3,
        cost: 3,
        evolveCostEp: 0,
        nesw: [8, 7, 7, 6],
        directionalSum: 28,
        sapphireAtkGem: 4,
        rubyDefGem: 6,
        keywords: ["[Evolved / 進化後]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_arch_seraph_overdrive.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_archangel.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_archangel_strip.png",
        telegraphType: "Arch-Seraph Emerald Feather Burst",
        telegraphName: "Overdrive Pinion Sanctuary",
        telegraphColor: "#FFB800",
        telegraphDesc: "On-Evolve: Grants +1 E/W to adjacent allies, activates Ward barrier, and triggers an immediate orthogonal comparison.",
        rulesHtml: "【進化時 / ON-EVOLVE】 Grants +1 East/West to adjacent allies and activates 【守護 / WARD】 barrier.<br/>【進化後 / EVOLVED】 Full-span emerald-gold mechanical wings.",
        loreQuote: "「鳥籠の空を突き破って……私の翼は、仲間を守るために輝く！」 — The gilded clockwork feathers unfold into a six-wing seraphic halo."
      }
    },
    {
      pairId: "ev_pair_02_celestia",
      pairIndex: 1,
      baseId: "ev_02_base",
      evoId: "ev_02_evo",
      characterTitleEn: "Celestia, Clockwork Feather Valkyrie",
      characterTitleJa: "時辰儀翼の戦乙女・セレスティア",
      furiganaJa: "じしんぎよく の いくさおとめ",
      traitEn: "Angel · Mech",
      traitJa: "天使・機械",
      cardClass: "Follower",
      evolveCostEp: 1,
      baseCard: {
        id: "ev_02_base",
        slug: "ev_02_base_celestia_clockwork_valkyrie",
        pairedEvoId: "ev_02_evo",
        isEvolvedForm: false,
        name: "Celestia, Clockwork Feather Valkyrie",
        nameJa: "時辰儀翼の戦乙女・セレスティア",
        furiganaJa: "じしんぎよく の いくさおとめ",
        faction: "Chrono",
        trait: "Angel · Mech / 天使・機械",
        rarity: "SR",
        setCode: "CF-EV02 SR",
        starCost: 2,
        cost: 2,
        evolveCostEp: 1,
        nesw: [7, 6, 6, 6],
        directionalSum: 25,
        sapphireAtkGem: 3,
        rubyDefGem: 3,
        keywords: ["[Evolve (1)]", "[Chrono Lock]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_02_base_celestia_clockwork_valkyrie.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_chronomancer.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_chronomancer_strip.png",
        telegraphType: "Astrolabe Pinion Sweep",
        telegraphName: "Escapement Feather Thrust",
        telegraphColor: "#00E5FF",
        telegraphDesc: "[Evolve (1)]: Evolve this card. Aligns Column Dice by +1 pip on deploy.",
        rulesHtml: "[進化 EVOLVE (1)]: これを進化させる (Evolve this card).<br/>【ファンファーレ / DEPLOY】 Gain +1 Budge token to calibrate active column dice.",
        loreQuote: "「歯車がひとつ噛み合うたび、運命の風向きが変わるの。」 — Brass escapement feathers chime in 24-beat cadence."
      },
      evoCard: {
        id: "ev_02_evo",
        slug: "ev_02_evo_celestia_chrono_sovereign",
        pairedBaseId: "ev_02_base",
        isEvolvedForm: true,
        name: "Celestia, Chrono Sovereign",
        nameJa: "時辰儀翼の統治者・セレスティア (進化後)",
        furiganaJa: "じしんぎよく の とうちしゃ",
        faction: "Chrono",
        trait: "Angel · Mech / 天使・機械",
        rarity: "UR EVOLVED",
        setCode: "CF-EV02 UR-E",
        starCost: 3,
        cost: 3,
        evolveCostEp: 0,
        nesw: [8, 8, 6, 6],
        directionalSum: 28,
        sapphireAtkGem: 5,
        rubyDefGem: 5,
        keywords: ["[Evolved / 進化後]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_02_evo_celestia_chrono_sovereign.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_arbiter.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_arbiter_strip.png",
        telegraphType: "Chrono-Sovereign Halo Lock",
        telegraphName: "Grand Astrolabe Judgment",
        telegraphColor: "#FFB800",
        telegraphDesc: "On-Evolve: Locks the active column die at 6 pips and boosts North/East edges to 8.",
        rulesHtml: "【進化時 / ON-EVOLVE】 Sets active column die to 6 pips and challenges adjacent enemy constructs.<br/>【守護 / WARD】",
        loreQuote: "「刻まれし時は今、黄金の翼となって戦場を統べる！」 — Time crystallizes along her gunmetal-filigree primaries."
      }
    },
    {
      pairId: "ev_pair_03_lyra",
      pairIndex: 2,
      baseId: "ev_03_base",
      evoId: "ev_03_evo",
      characterTitleEn: "Lyra, Harmonic Wing Automaton",
      characterTitleJa: "共鳴翼の自動人形・リラ",
      furiganaJa: "きょうめいよく の オートマタ",
      traitEn: "Angel · Mech",
      traitJa: "天使・機械",
      cardClass: "Follower",
      evolveCostEp: 1,
      baseCard: {
        id: "ev_03_base",
        slug: "ev_03_base_lyra_harmony_automata",
        pairedEvoId: "ev_03_evo",
        isEvolvedForm: false,
        name: "Lyra, Harmonic Wing Automaton",
        nameJa: "共鳴翼の自動人形・リラ",
        furiganaJa: "きょうめいよく の オートマタ",
        faction: "Aether",
        trait: "Angel · Mech / 天使・機械",
        rarity: "SR",
        setCode: "CF-EV03 SR",
        starCost: 2,
        cost: 2,
        evolveCostEp: 1,
        nesw: [6, 7, 6, 6],
        directionalSum: 25,
        sapphireAtkGem: 2,
        rubyDefGem: 4,
        keywords: ["[Evolve (1)]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_03_base_lyra_harmony_automata.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_oracle.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_oracle_strip.png",
        telegraphType: "Acoustic Feather Resonance",
        telegraphName: "Chime-Pinion Aria",
        telegraphColor: "#2EE6D3",
        telegraphDesc: "[Evolve (1)]: Evolve this card. [Ward / 守護] Harmonizes East/West pips with adjacent Mech-Wing allies.",
        rulesHtml: "[進化 EVOLVE (1)]: これを進化させる (Evolve this card).<br/>【守護 / WARD】 Resonates with adjacent Angel · Mech followers.",
        loreQuote: "「私の羽根はオルゴール。優しい旋律で、傷ついた翼を癒やすの。」 — Each metallic feather is tuned to a pure Dorian fifth."
      },
      evoCard: {
        id: "ev_03_evo",
        slug: "ev_03_evo_lyra_symphony_seraph",
        pairedBaseId: "ev_03_base",
        isEvolvedForm: true,
        name: "Lyra, Symphony Seraph",
        nameJa: "共鳴翼の交響熾天使・リラ (進化後)",
        furiganaJa: "きょうめいよく の シンフォニーセラフ",
        faction: "Aether",
        trait: "Angel · Mech / 天使・機械",
        rarity: "UR EVOLVED",
        setCode: "CF-EV03 UR-E",
        starCost: 3,
        cost: 3,
        evolveCostEp: 0,
        nesw: [7, 8, 7, 6],
        directionalSum: 28,
        sapphireAtkGem: 4,
        rubyDefGem: 6,
        keywords: ["[Evolved / 進化後]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_03_evo_lyra_symphony_seraph.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_seraph.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_seraph_strip.png",
        telegraphType: "Symphonic Seraph Crescendo",
        telegraphName: "Harmonic Pinion Finale",
        telegraphColor: "#A855F7",
        telegraphDesc: "On-Evolve: Emits a 3x3 harmonic wave that buffs all friendly units' South/East edges by +1.",
        rulesHtml: "【進化時 / ON-EVOLVE】 All friendly followers on the 3x3 board gain +1 East/South pip.<br/>【守護 / WARD】",
        loreQuote: "「響け、天空の交響曲！すべての機械翼よ、光の和音となれ！」 — Emerald-violet soundwaves ripple from her filigree wings."
      }
    },
    {
      pairId: "ev_pair_04_ignia",
      pairIndex: 3,
      baseId: "ev_04_base",
      evoId: "ev_04_evo",
      characterTitleEn: "Ignia, Blaze-Pinion Mech Maiden",
      characterTitleJa: "焔翼の機巧少女・イグニア",
      furiganaJa: "えんよく の きこうしょうじょ",
      traitEn: "Angel · Mech",
      traitJa: "天使・機械",
      cardClass: "Follower",
      evolveCostEp: 1,
      baseCard: {
        id: "ev_04_base",
        slug: "ev_04_base_ignia_blaze_pinion_maiden",
        pairedEvoId: "ev_04_evo",
        isEvolvedForm: false,
        name: "Ignia, Blaze-Pinion Mech Maiden",
        nameJa: "焔翼の機巧少女・イグニア",
        furiganaJa: "えんよく の きこうしょうじょ",
        faction: "Valkyria",
        trait: "Angel · Mech / 天使・機械",
        rarity: "SR",
        setCode: "CF-EV04 SR",
        starCost: 3,
        cost: 3,
        evolveCostEp: 1,
        nesw: [7, 7, 6, 5],
        directionalSum: 25,
        sapphireAtkGem: 3,
        rubyDefGem: 3,
        keywords: ["[Evolve (1)]", "[Rush / 突進]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_04_base_ignia_blaze_pinion_maiden.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_kai.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_kai_strip.png",
        telegraphType: "Solar Pinion Ignition",
        telegraphName: "Blaze-Feather Dive",
        telegraphColor: "#FF2E54",
        telegraphDesc: "[Evolve (1)]: Evolve this card. Strikes North/East targets with polyhedral solar-flare feathers.",
        rulesHtml: "[進化 EVOLVE (1)]: これを進化させる (Evolve this card).<br/>【突進 / RUSH】 Gains +1 North when deployed in a boosted column.",
        loreQuote: "「夕焼けよりも熱く、私の機巧翼は空を焦がすよ！」 — Crimson-gold exhaust plumes trail behind her articulated wing-tips."
      },
      evoCard: {
        id: "ev_04_evo",
        slug: "ev_04_evo_ignia_solar_phoenix_empress",
        pairedBaseId: "ev_04_base",
        isEvolvedForm: true,
        name: "Ignia, Solar Phoenix Empress",
        nameJa: "焔翼の陽炎女帝・イグニア (進化後)",
        furiganaJa: "えんよく の フェニックスエンプレス",
        faction: "Valkyria",
        trait: "Angel · Mech / 天使・機械",
        rarity: "UR EVOLVED",
        setCode: "CF-EV04 UR-E",
        starCost: 4,
        cost: 4,
        evolveCostEp: 0,
        nesw: [9, 8, 7, 7],
        directionalSum: 31,
        sapphireAtkGem: 5,
        rubyDefGem: 5,
        keywords: ["[Evolved / 進化後]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_04_evo_ignia_solar_phoenix_empress.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_valkyrie.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_valkyrie_strip.png",
        telegraphType: "Solar Phoenix Overdrive",
        telegraphName: "Empress Pinion Supernova",
        telegraphColor: "#F97316",
        telegraphDesc: "On-Evolve: Unleashes a 9-North / 8-East solar feather burst that flips weaker adjacent enemy units.",
        rulesHtml: "【進化時 / ON-EVOLVE】 Triggers an immediate orthogonal capture check with +2 North/East.<br/>【守護 / WARD】",
        loreQuote: "「不死鳥の焔よ、機巧の空を照らし尽くせ！」 — Her gunmetal frame blazes with molten gold filigree."
      }
    },
    {
      pairId: "ev_pair_05_nocturna",
      pairIndex: 4,
      baseId: "ev_05_base",
      evoId: "ev_05_evo",
      characterTitleEn: "Nocturna, Eclipse-Wing Mech Saint",
      characterTitleJa: "蝕翼の機巧聖女・ノクターナ",
      furiganaJa: "しょくよく の きこうせいじょ",
      traitEn: "Angel · Mech",
      traitJa: "天使・機械",
      cardClass: "Follower",
      evolveCostEp: 1,
      baseCard: {
        id: "ev_05_base",
        slug: "ev_05_base_nocturna_eclipse_wing_saint",
        pairedEvoId: "ev_05_evo",
        isEvolvedForm: false,
        name: "Nocturna, Eclipse-Wing Mech Saint",
        nameJa: "蝕翼の機巧聖女・ノクターナ",
        furiganaJa: "しょくよく の きこうせいじょ",
        faction: "Chrono",
        trait: "Angel · Mech / 天使・機械",
        rarity: "SR",
        setCode: "CF-EV05 SR",
        starCost: 3,
        cost: 3,
        evolveCostEp: 1,
        nesw: [6, 7, 8, 7],
        directionalSum: 28,
        sapphireAtkGem: 3,
        rubyDefGem: 5,
        keywords: ["[Evolve (1)]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_05_base_nocturna_eclipse_wing_saint.png",
        fallbackArt: "./GeneratedArt/MasteredCards/e_eclipse.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/e_eclipse_strip.png",
        telegraphType: "Twilight Prism Pinions",
        telegraphName: "Eclipse Sanctuary Veil",
        telegraphColor: "#A855F7",
        telegraphDesc: "[Evolve (1)]: Evolve this card. [Ward / 守護] Refracts twilight starlight across South/West edges.",
        rulesHtml: "[進化 EVOLVE (1)]: これを進化させる (Evolve this card).<br/>【守護 / WARD】 Shields South/West orthogonal lanes.",
        loreQuote: "「宵闇の空に浮かぶ銀の翼……静寂こそが私の祈り。」 — Smoked-obsidian feathers rimmed in emerald and violet."
      },
      evoCard: {
        id: "ev_05_evo",
        slug: "ev_05_evo_nocturna_abyssal_prism_queen",
        pairedBaseId: "ev_05_base",
        isEvolvedForm: true,
        name: "Nocturna, Abyssal Prism Queen",
        nameJa: "蝕翼の深淵稜鏡女王・ノクターナ (進化後)",
        furiganaJa: "しょくよく の アビスプリズムクイーン",
        faction: "Chrono",
        trait: "Angel · Mech / 天使・機械",
        rarity: "UR EVOLVED",
        setCode: "CF-EV05 UR-E",
        starCost: 4,
        cost: 4,
        evolveCostEp: 0,
        nesw: [7, 8, 8, 8],
        directionalSum: 31,
        sapphireAtkGem: 5,
        rubyDefGem: 7,
        keywords: ["[Evolved / 進化後]", "[Ward / 守護]"],
        art: "./GeneratedArt/EvolveMechWingMaidens/ev_05_evo_nocturna_abyssal_prism_queen.png",
        fallbackArt: "./GeneratedArt/MasteredCards/h_oracle.png",
        sakugaStrip: "./GeneratedArt/SakugaCutIns/h_oracle_strip.png",
        telegraphType: "Abyssal Prism Halo",
        telegraphName: "Eternal Omens Prism Crown",
        telegraphColor: "#2EE6D3",
        telegraphDesc: "On-Evolve: Projects a 31-pip prism barrier across East/South/West and triggers adjacent PLUS/SAME checks.",
        rulesHtml: "【進化時 / ON-EVOLVE】 Grants +1 East/West to adjacent allies and fortifies South/West at 8.<br/>【守護 / WARD】",
        loreQuote: "「千の稜鏡よ、夜の帳を裂いて永遠の兆しを映し出せ！」 — Prismatic emerald-gold light pours through her filigree wings."
      }
    }
  ];

  const EVOLVE_MECH_WING_CARDS_10 = [];
  EVOLVE_MECH_WING_MAIDEN_PAIRS.forEach(function (pair) {
    EVOLVE_MECH_WING_CARDS_10.push(pair.baseCard);
    EVOLVE_MECH_WING_CARDS_10.push(pair.evoCard);
  });

  // ==========================================================================
  // 2. REGISTER ALL 10 FORMS INTO ALL_CARDS & SET1_CARDS_BY_ID
  // ==========================================================================
  const EVOLVE_CARD_LOOKUP = {};

  function registerEvolveMechWingCards() {
    EVOLVE_MECH_WING_CARDS_10.forEach(function (card) {
      EVOLVE_CARD_LOOKUP[card.id] = card;
      EVOLVE_CARD_LOOKUP[card.slug] = card;

      const cardEntry = Object.assign(
        {
          id: card.id,
          name: card.name,
          faction: card.faction,
          starCost: card.starCost,
          cost: card.cost,
          nesw: card.nesw.slice(),
          art: card.art,
          fallbackArt: card.fallbackArt,
          sakugaStrip: card.sakugaStrip,
          telegraphType: card.telegraphType,
          telegraphName: card.telegraphName,
          telegraphColor: card.telegraphColor,
          telegraphDesc: card.telegraphDesc
        },
        card
      );

      [card.id, card.slug].forEach(function (key) {
        if (globalScope.SET1_CARDS_BY_ID && typeof globalScope.SET1_CARDS_BY_ID === "object") {
          globalScope.SET1_CARDS_BY_ID[key] = Object.assign({}, cardEntry, { id: key });
        }
        if (globalScope.ALL_CARDS && typeof globalScope.ALL_CARDS === "object") {
          Object.defineProperty(globalScope.ALL_CARDS, key, {
            value: Object.assign({}, cardEntry, { id: key }),
            enumerable: false,
            writable: true,
            configurable: true
          });
        }
        if (globalScope.SAKUGA_STRIP_LOOKUP && typeof globalScope.SAKUGA_STRIP_LOOKUP === "object") {
          globalScope.SAKUGA_STRIP_LOOKUP[key] = card.sakugaStrip;
        }
      });
    });
  }

  registerEvolveMechWingCards();

  // ==========================================================================
  // 3. RUNTIME STATE & LUXURY GUNMETAL-FILIGREE SR/UR CSS INJECTION
  // ==========================================================================
  const EVOLVE_RUNTIME_STATE = {
    srFrameStyleEnabled: true,
    selectedPairIndex: 0,
    previewShowEvolved: false,
    evolutionsTriggeredCount: 0,
    lastEvolvedCellIndex: -1,
    lastEvolvedCardId: "ev_01_evo"
  };

  function ensureEvolveStylesInjected() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    if (doc.getElementById("cf-evolve-sr-gunmetal-styles")) return;
    const styleEl = doc.createElement("style");
    styleEl.id = "cf-evolve-sr-gunmetal-styles";
    styleEl.textContent = [
      "@keyframes cfEvolveWingBurst {",
      "  0% { transform: scale(0.55) rotateY(0deg); opacity: 0; }",
      "  35% { transform: scale(1.12) rotateY(90deg); opacity: 1; }",
      "  100% { transform: scale(1.0) rotateY(180deg); opacity: 0; }",
      "}",
      "@keyframes cfEvolveCardFlip3D {",
      "  0% { transform: perspective(900px) rotateY(0deg) scale(1); }",
      "  50% { transform: perspective(900px) rotateY(90deg) scale(1.08); filter: brightness(1.55) drop-shadow(0 0 24px #eab308); }",
      "  100% { transform: perspective(900px) rotateY(0deg) scale(1); }",
      "}",
      ".cf-evolve-sr-card {",
      "  position: relative; width: 276px; height: 384px; border-radius: 13px; overflow: hidden;",
      "  background: linear-gradient(145deg, #1A1D24 0%, #2C323F 48%, #14171D 100%);",
      "  border: 2px solid #94A3B8;",
      "  box-shadow: 0 14px 36px rgba(0,0,0,0.82), inset 0 0 0 2px rgba(212,175,55,0.55);",
      "  font-family: 'Georgia', 'Times New Roman', serif; color: #F8FAFC; user-select: none;",
      "  transition: transform 0.32s cubic-bezier(0.22,1,0.36,1), box-shadow 0.32s ease;",
      "}",
      ".cf-evolve-sr-card.is-evolved-ur {",
      "  border-color: #FACC15;",
      "  box-shadow: 0 16px 42px rgba(234,179,8,0.42), inset 0 0 0 2px rgba(46,230,211,0.75);",
      "}",
      ".cf-evolve-sr-card.flipping-3d {",
      "  animation: cfEvolveCardFlip3D 0.58s cubic-bezier(0.22,1,0.36,1);",
      "}",
      "body.evolve-sr-frame-mode .board-slot .slot-card, body.evolve-sr-frame-mode .hand-card, body.evolve-sr-frame-mode .card-3d-unit {",
      "  border: 1.5px solid #D4AF37 !important;",
      "  box-shadow: inset 0 0 0 1px rgba(212,175,55,0.65), 0 8px 20px rgba(0,0,0,0.75) !important;",
      "}",
      ".cf-board-evolve-btn {",
      "  position: absolute; left: 4px; bottom: 19px; z-index: 12; pointer-events: auto;",
      "  padding: 2px 5px; border-radius: 4px; font-size: 8.5px; font-weight: 900; letter-spacing: 0.04em;",
      "  background: linear-gradient(135deg, #10B981, #047857); color: #ECFDF5; border: 1px solid #FACC15;",
      "  box-shadow: 0 2px 6px rgba(0,0,0,0.85); cursor: pointer; line-height: 1.1;",
      "}",
      ".cf-board-evolve-btn:hover { filter: brightness(1.2); transform: scale(1.06); }",
      ".cf-board-evolve-btn.is-evolved {",
      "  background: linear-gradient(135deg, #D4AF37, #92400E); color: #FFFBEB; border-color: #FEF08A; pointer-events: none;",
      "}"
    ].join("\n");
    if (doc.head) doc.head.appendChild(styleEl);
  }

  function applyEvolveSrFrameStyle(enabled) {
    ensureEvolveStylesInjected();
    EVOLVE_RUNTIME_STATE.srFrameStyleEnabled = Boolean(enabled);
    if (typeof globalScope.document !== "undefined" && globalScope.document.body) {
      if (EVOLVE_RUNTIME_STATE.srFrameStyleEnabled) {
        globalScope.document.body.classList.add("evolve-sr-frame-mode");
      } else {
        globalScope.document.body.classList.remove("evolve-sr-frame-mode");
      }
    }
    return {
      ok: true,
      srFrameStyleEnabled: EVOLVE_RUNTIME_STATE.srFrameStyleEnabled
    };
  }

  // ==========================================================================
  // 4. SHADOWVERSE-EVOLVE BP05-110 SR GUNMETAL-FILIGREE CARD RENDERER
  // ==========================================================================
  function resolveCardForSrRenderer(cardOrPair, showEvolved) {
    if (!cardOrPair) {
      return showEvolved ? EVOLVE_MECH_WING_MAIDEN_PAIRS[0].evoCard : EVOLVE_MECH_WING_MAIDEN_PAIRS[0].baseCard;
    }
    if (typeof cardOrPair === "string") {
      if (EVOLVE_CARD_LOOKUP[cardOrPair]) {
        const found = EVOLVE_CARD_LOOKUP[cardOrPair];
        if (showEvolved && found.pairedEvoId && EVOLVE_CARD_LOOKUP[found.pairedEvoId]) {
          return EVOLVE_CARD_LOOKUP[found.pairedEvoId];
        }
        return found;
      }
      for (let i = 0; i < EVOLVE_MECH_WING_MAIDEN_PAIRS.length; i++) {
        const p = EVOLVE_MECH_WING_MAIDEN_PAIRS[i];
        if (p.pairId === cardOrPair || p.baseId === cardOrPair || p.evoId === cardOrPair) {
          return showEvolved ? p.evoCard : p.baseCard;
        }
      }
    }
    if (cardOrPair.baseCard && cardOrPair.evoCard) {
      return showEvolved ? cardOrPair.evoCard : cardOrPair.baseCard;
    }
    return cardOrPair;
  }

  function renderEvolveSrCardHtml(cardOrPair, showEvolved) {
    ensureEvolveStylesInjected();
    const card = resolveCardForSrRenderer(cardOrPair, Boolean(showEvolved));
    const isEvo = Boolean(card.isEvolvedForm || showEvolved);
    const nesw = Array.isArray(card.nesw) ? card.nesw : [7, 7, 6, 6];
    const costVal = typeof card.cost === "number" ? card.cost : 2;
    const atkGem = typeof card.sapphireAtkGem === "number" ? card.sapphireAtkGem : Math.round((nesw[0] + nesw[3]) / 4);
    const defGem = typeof card.rubyDefGem === "number" ? card.rubyDefGem : Math.round((nesw[1] + nesw[2]) / 3);
    const rarityBadge = isEvo ? "UR" : (card.rarity || "SR");

    return (
      '<div class="cf-evolve-sr-card ' + (isEvo ? "is-evolved-ur" : "") + '" data-card-id="' + card.id + '">' +
        // Full-Bleed Portrait Artwork
        '<img src="' + card.art + '" onerror="this.onerror=null;this.src=\'' + (card.fallbackArt || "./GeneratedArt/MasteredCards/h_valkyrie.png") + '\';" alt="' + card.name + '" style="position:absolute;inset:5px;width:calc(100% - 10px);height:calc(100% - 10px);object-fit:cover;border-radius:9px;z-index:1;" />' +
        // Inner Gunmetal & Gold Filigree Border SVG Overlay
        '<svg viewBox="0 0 276 384" fill="none" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2;" aria-hidden="true">' +
          '<rect x="5" y="5" width="266" height="374" rx="9" stroke="url(#cf-ev-gunmetal)" stroke-width="3.5"/>' +
          '<rect x="8.5" y="8.5" width="259" height="367" rx="7" stroke="' + (isEvo ? "#FACC15" : "#D4AF37") + '" stroke-opacity="0.72" stroke-width="1.2"/>' +
          '<defs>' +
            '<linearGradient id="cf-ev-gunmetal" x1="0" y1="0" x2="276" y2="384" gradientUnits="userSpaceOnUse">' +
              '<stop offset="0%" stop-color="#E2E8F0"/>' +
              '<stop offset="45%" stop-color="#475569"/>' +
              '<stop offset="100%" stop-color="#1E293B"/>' +
            '</linearGradient>' +
          '</defs>' +
        '</svg>' +
        // Top-Left Ornate Octagonal/Diamond Cost Crest
        '<div style="position:absolute;top:8px;left:8px;width:44px;height:44px;z-index:4;display:flex;align-items:center;justify-content:center;">' +
          '<svg viewBox="0 0 64 64" style="position:absolute;inset:0;width:100%;height:100%;filter:drop-shadow(0 3px 6px rgba(0,0,0,0.85));" aria-hidden="true">' +
            '<polygon points="32,2 54,14 62,32 54,50 32,62 10,50 2,32 10,14" fill="#181C24" stroke="#E2E8F0" stroke-width="3"/>' +
            '<polygon points="32,8 49,18 56,32 49,46 32,56 15,46 8,32 15,18" fill="#0F172A" stroke="#D4AF37" stroke-width="1.5"/>' +
          '</svg>' +
          '<span style="position:relative;z-index:2;font-size:22px;font-weight:900;color:#FFFFFF;text-shadow:0 2px 4px #000;">' + costVal + '</span>' +
        '</div>' +
        // Top-Right Orthogonal N/E/S/W Tactical Compass Pill
        '<div style="position:absolute;top:10px;right:10px;z-index:4;background:rgba(10,14,24,0.82);border:1px solid rgba(212,175,55,0.75);border-radius:6px;padding:3px 7px;font-family:system-ui,sans-serif;font-size:10px;font-weight:800;color:#FDE68A;letter-spacing:0.04em;">' +
          'N' + nesw[0] + ' · E' + nesw[1] + ' · S' + nesw[2] + ' · W' + nesw[3] +
        '</div>' +
        // Lower-Third Translucent Smoked-Obsidian Rules & Bilingual Lore Box (legs/dress remain visible underneath)
        '<div style="position:absolute;left:10px;right:10px;bottom:68px;z-index:3;background:rgba(10,12,18,0.72);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);border:1px solid rgba(192,200,216,0.45);border-radius:6px;padding:7px 9px;font-family:system-ui,-apple-system,sans-serif;">' +
          '<div style="font-size:10.5px;font-weight:700;color:#F8FAFC;line-height:1.35;">' +
            '<span style="display:inline-block;background:linear-gradient(135deg,#10B981,#047857);color:#ECFDF5;font-size:9px;font-weight:900;padding:1px 5px;border-radius:4px;margin-right:4px;border:1px solid #6EE7B7;">' +
              (isEvo ? "進化後 EVOLVED" : "進化 EVOLVE (" + (card.evolveCostEp || 1) + ")") +
            '</span>' +
            (card.rulesHtml || card.telegraphDesc) +
          '</div>' +
          '<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(212,175,55,0.75),transparent);margin:5px 0;"></div>' +
          '<div style="font-size:9.5px;font-style:italic;color:#CBD5E1;line-height:1.3;">' +
            (card.loreQuote || "") +
          '</div>' +
        '</div>' +
        // Bottom Gunmetal Pedestal Bar with Sapphire Attack Gem, Center Bilingual Furigana Title, Ruby Shield Defense Gem & SR/UR Lozenge
        '<div style="position:absolute;left:6px;right:6px;bottom:6px;height:58px;z-index:4;background:linear-gradient(180deg,rgba(26,29,36,0.95) 0%,rgba(14,17,23,0.98) 100%);border-top:1.5px solid #94A3B8;border-radius:0 0 8px 8px;display:flex;align-items:center;justify-content:space-between;padding:0 8px;">' +
          // Left Faceted Sapphire Attack/N-W Gem
          '<div style="position:relative;width:40px;height:46px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">' +
            '<svg viewBox="0 0 52 60" style="position:absolute;inset:0;width:100%;height:100%;filter:drop-shadow(0 2px 5px rgba(0,0,0,0.85));" aria-hidden="true">' +
              '<polygon points="26,2 48,22 38,56 14,56 4,22" fill="url(#cf-sapphire-gem)" stroke="#E2E8F0" stroke-width="2.5"/>' +
              '<polygon points="26,8 42,24 34,50 18,50 10,24" fill="none" stroke="#93C5FD" stroke-width="1"/>' +
              '<defs><linearGradient id="cf-sapphire-gem" x1="0" y1="0" x2="0" y2="60"><stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#1D4ED8"/></linearGradient></defs>' +
            '</svg>' +
            '<span style="position:relative;z-index:2;font-size:20px;font-weight:900;color:#FFFFFF;text-shadow:0 2px 4px #000;">' + atkGem + '</span>' +
          '</div>' +
          // Center Bilingual Furigana Title + Follower / Angel · Mech Pill + SR/UR Lozenge
          '<div style="flex:1;text-align:center;padding:0 4px;overflow:hidden;">' +
            '<div style="font-size:7.5px;color:#CBD5E1;letter-spacing:0.08em;line-height:1;">' + (card.furiganaJa || "きこうよく の しょうじょ") + '</div>' +
            '<div style="font-size:11.5px;font-weight:900;color:#FFFFFF;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 1px 3px #000;">' + (card.nameJa || card.name) + '</div>' +
            '<div style="height:1px;background:linear-gradient(90deg,transparent,#C0C8D8,transparent);margin:2px auto;width:88%;"></div>' +
            '<div style="display:flex;align-items:center;justify-content:center;gap:5px;margin-top:2px;font-family:system-ui,sans-serif;">' +
              '<span style="background:linear-gradient(135deg,#881337,#4C0519);color:#FECDD3;border:1px solid #F43F5E;border-radius:3px;padding:0 5px;font-size:8.5px;font-weight:800;">Follower</span>' +
              '<span style="font-size:8.5px;color:#E2E8F0;font-weight:700;">' + (card.trait || "Angel · Mech / 天使・機械") + '</span>' +
              '<span style="background:linear-gradient(135deg,#D4AF37,#92400E);color:#FFFBEB;border:1px solid #FDE68A;border-radius:4px;padding:0 5px;font-size:8.5px;font-weight:900;">' + rarityBadge + '</span>' +
            '</div>' +
          '</div>' +
          // Right Faceted Ruby Shield Defense/E-S Gem
          '<div style="position:relative;width:40px;height:46px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">' +
            '<svg viewBox="0 0 52 60" style="position:absolute;inset:0;width:100%;height:100%;filter:drop-shadow(0 2px 5px rgba(0,0,0,0.85));" aria-hidden="true">' +
              '<path d="M26,3 L47,12 L43,40 L26,57 L9,40 L5,12 Z" fill="url(#cf-ruby-gem)" stroke="#E2E8F0" stroke-width="2.5"/>' +
              '<path d="M26,9 L41,16 L38,37 L26,50 L14,37 L11,16 Z" fill="none" stroke="#FDA4AF" stroke-width="1"/>' +
              '<defs><linearGradient id="cf-ruby-gem" x1="0" y1="0" x2="0" y2="60"><stop offset="0%" stop-color="#E11D48"/><stop offset="100%" stop-color="#881337"/></linearGradient></defs>' +
            '</svg>' +
            '<span style="position:relative;z-index:2;font-size:20px;font-weight:900;color:#FFFFFF;text-shadow:0 2px 4px #000;">' + defGem + '</span>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  // ==========================================================================
  // 5. LIVE EVOLVE (進化前 -> 進化後) TABLETOP MECHANIC
  // ==========================================================================
  function findPairByCardId(cardId) {
    const cid = String(cardId || "");
    for (let i = 0; i < EVOLVE_MECH_WING_MAIDEN_PAIRS.length; i++) {
      const p = EVOLVE_MECH_WING_MAIDEN_PAIRS[i];
      if (p.baseId === cid || p.evoId === cid || p.baseCard.slug === cid || p.evoCard.slug === cid) {
        return p;
      }
    }
    return null;
  }

  function triggerFeatherWingBurstOverlay(cellIndex, evolvedCard) {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    ensureEvolveStylesInjected();
    let fx = doc.getElementById("cf-evolve-wing-burst-overlay");
    if (!fx && doc.body) {
      fx = doc.createElement("div");
      fx.id = "cf-evolve-wing-burst-overlay";
      fx.style.cssText =
        "display:none;position:fixed;inset:0;pointer-events:none;z-index:9550;align-items:center;justify-content:center;";
      doc.body.appendChild(fx);
    }
    if (!fx) return;

    const title = (evolvedCard && evolvedCard.name) || "Rosalia, Arch-Seraph Overdrive";
    fx.innerHTML =
      '<div style="background:radial-gradient(circle,rgba(16,185,129,0.32) 0%,rgba(234,179,8,0.18) 45%,transparent 72%);padding:36px;border-radius:50%;text-align:center;">' +
        '<svg width="220" height="140" viewBox="0 0 256 160" fill="none" aria-hidden="true">' +
          '<path d="M128,80 L18,22 L48,68 L10,92 L64,104 L38,142 L128,102 Z" fill="#2EE6D3" fill-opacity="0.78" stroke="#FACC15" stroke-width="4"/>' +
          '<path d="M128,80 L238,22 L208,68 L246,92 L192,104 L218,142 L128,102 Z" fill="#2EE6D3" fill-opacity="0.78" stroke="#FACC15" stroke-width="4"/>' +
          '<polygon points="128,12 142,64 196,80 142,96 128,148 114,96 60,80 114,64" fill="#FACC15" stroke="#FFFFFF" stroke-width="3"/>' +
        '</svg>' +
        '<div style="font-size:15px;font-weight:900;color:#FEF08A;letter-spacing:0.12em;text-shadow:0 2px 10px #000;">[進化後 EVOLVE AWAKENED · WARD ACTIVE]</div>' +
        '<div style="font-size:13px;font-weight:800;color:#2EE6D3;text-shadow:0 2px 8px #000;">' + title + ' (Cell ' + cellIndex + ')</div>' +
      '</div>';
    fx.style.display = "flex";
    setTimeout(function () {
      if (fx) fx.style.display = "none";
    }, 920);
  }

  function evolveCardOnBoard(cellIndex, stateObj) {
    registerEvolveMechWingCards();
    const st = stateObj || globalScope.state || {};
    if (typeof st.playerEvolvePoints !== "number") {
      st.playerEvolvePoints = 2;
    }
    if (!st.evolvedCells || typeof st.evolvedCells !== "object") {
      st.evolvedCells = {};
    }

    const idx = typeof cellIndex === "number" ? Math.max(0, Math.min(8, cellIndex)) : 4;
    const r = Math.floor(idx / 3);
    const c = idx % 3;

    // Locate target cell on state.grid (or initialize if empty so live demo/test always succeeds)
    let cell = null;
    if (Array.isArray(st.grid) && st.grid[r] && st.grid[r][c]) {
      cell = st.grid[r][c];
    } else {
      cell = { r: r, c: c, cardId: "ev_01_base", owner: "player", nesw: [6, 6, 5, 5] };
    }

    if (!cell.cardId) {
      cell.cardId = "ev_01_base";
      cell.owner = "player";
      cell.nesw = [6, 6, 5, 5];
    }

    const pair = findPairByCardId(cell.cardId);
    let evolvedCardMeta = null;
    let newNesw = [];

    if (pair) {
      evolvedCardMeta = pair.evoCard;
      cell.preEvolveCardId = pair.baseId;
      cell.cardId = pair.evoId;
      newNesw = pair.evoCard.nesw.slice();
    } else {
      const baseNesw = Array.isArray(cell.nesw) && cell.nesw.length === 4 ? cell.nesw : [6, 6, 6, 6];
      newNesw = baseNesw.map(function (v) { return Math.min(10, Number(v || 6) + 1); });
      evolvedCardMeta = EVOLVE_MECH_WING_MAIDEN_PAIRS[0].evoCard;
    }

    cell.nesw = newNesw;
    cell.evolved = true;
    cell.ward = true;
    st.evolvedCells[idx] = {
      cellIndex: idx,
      cardId: cell.cardId,
      nesw: newNesw.slice(),
      evolved: true,
      ward: true
    };
    if (st.playerEvolvePoints > 0) {
      st.playerEvolvePoints = Math.max(0, st.playerEvolvePoints - 1);
    }

    // On-Evolve ([進化時]): buff orthogonal friendly neighbors (+1 E/W capped at 10) & flip weaker adjacent enemy cards
    const neighbors = [
      { dr: -1, dc: 0, atkEdge: 0, defEdge: 2 },
      { dr: 0, dc: 1, atkEdge: 1, defEdge: 3 },
      { dr: 1, dc: 0, atkEdge: 2, defEdge: 0 },
      { dr: 0, dc: -1, atkEdge: 3, defEdge: 1 }
    ];
    const alliesBuffed = [];
    const enemiesFlipped = [];

    if (Array.isArray(st.grid) && st.grid.length === 3) {
      neighbors.forEach(function (nb) {
        const nr = r + nb.dr;
        const nc = c + nb.dc;
        if (nr < 0 || nr >= 3 || nc < 0 || nc >= 3) return;
        const adj = st.grid[nr] && st.grid[nr][nc];
        if (!adj || !adj.cardId || !Array.isArray(adj.nesw)) return;
        if (adj.owner === "player") {
          adj.nesw[1] = Math.min(10, Number(adj.nesw[1] || 6) + 1);
          adj.nesw[3] = Math.min(10, Number(adj.nesw[3] || 6) + 1);
          adj.ward = true;
          alliesBuffed.push(nr * 3 + nc);
        } else if (adj.owner === "ai") {
          if (Number(newNesw[nb.atkEdge] || 0) > Number(adj.nesw[nb.defEdge] || 0)) {
            adj.owner = "player";
            adj.justFlipped = true;
            enemiesFlipped.push(nr * 3 + nc);
          }
        }
      });
    }

    EVOLVE_RUNTIME_STATE.evolutionsTriggeredCount += 1;
    EVOLVE_RUNTIME_STATE.lastEvolvedCellIndex = idx;
    EVOLVE_RUNTIME_STATE.lastEvolvedCardId = cell.cardId;

    triggerFeatherWingBurstOverlay(idx, evolvedCardMeta);
    if (typeof globalScope.playTone === "function") {
      globalScope.playTone(11, "triangle", 0.24, true);
    }
    if (typeof globalScope.renderAll === "function") {
      globalScope.renderAll();
    }

    return {
      ok: true,
      cellIndex: idx,
      evolvedCardId: cell.cardId,
      evolvedName: evolvedCardMeta ? evolvedCardMeta.name : cell.cardId,
      nesw: newNesw,
      directionalSum: newNesw.reduce(function (a, b) { return a + b; }, 0),
      evolved: true,
      ward: true,
      remainingEvolvePoints: st.playerEvolvePoints,
      alliesBuffed: alliesBuffed,
      enemiesFlipped: enemiesFlipped
    };
  }

  // ==========================================================================
  // 6. EQUIP 15-CARD MECH-WING MAIDEN EVOLVE DECK
  // ==========================================================================
  function equipEvolveMechWingMaidenDeck() {
    registerEvolveMechWingCards();

    const deck15Ids = [
      "ev_01_base",
      "ev_01_evo",
      "ev_02_base",
      "ev_02_evo",
      "ev_03_base",
      "ev_03_evo",
      "ev_04_base",
      "ev_04_evo",
      "ev_05_base",
      "ev_05_evo",
      "pxg_s01",
      "pxg_s05",
      "set2_k01",
      "saga_y01",
      "plugin_01_tcg_creative_designer"
    ];

    const activeSquad5 = ["ev_01_base", "ev_02_base", "ev_03_base", "ev_04_base", "ev_05_base"];

    if (!globalScope.state || typeof globalScope.state !== "object") {
      globalScope.state = {};
    }
    const st = globalScope.state;
    if (Array.isArray(st.unlockedCards)) {
      deck15Ids.forEach(function (cid) {
        if (!st.unlockedCards.includes(cid)) st.unlockedCards.push(cid);
      });
    }
    st.playerDeckId = "deck_evolve_mech_wing_maidens";
    st.playerDeck = deck15Ids.slice();
    st.activeDeck = activeSquad5.slice();
    st.activeSquad = activeSquad5.slice();
    st.customDeckEquipped = true;
    st.hand = activeSquad5.slice();
    st.selectedHandIdx = 0;
    st.playerEvolvePoints = 2;

    applyEvolveSrFrameStyle(true);

    if (typeof globalScope.updateTelegraphHud === "function") {
      globalScope.updateTelegraphHud(activeSquad5[0]);
    }
    if (typeof globalScope.renderAll === "function") {
      globalScope.renderAll();
    }
    if (typeof globalScope.playTone === "function") {
      globalScope.playTone(10, "triangle", 0.2, true);
    }

    return {
      ok: true,
      deckId: "deck_evolve_mech_wing_maidens",
      deckSize: deck15Ids.length,
      playerDeck: deck15Ids,
      deckCardIds: deck15Ids,
      activeSquad5: activeSquad5,
      playerEvolvePoints: st.playerEvolvePoints
    };
  }

  // ==========================================================================
  // 7. INTERACTIVE EVOLVE MECH-WING MAIDEN STUDIO MODAL (#evolve-maiden-studio-modal)
  // ==========================================================================
  function ensureEvolveModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("evolve-maiden-studio-modal");
    if (!modal && doc.body) {
      modal = doc.createElement("div");
      modal.id = "evolve-maiden-studio-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-label", "Shadowverse-EVOLVE Style Mech-Wing Maiden Studio & SR/UR Card Frame Renderer");
      modal.style.cssText =
        "display:none;position:fixed;inset:0;z-index:9680;background:rgba(6,9,16,0.9);backdrop-filter:blur(10px);padding:20px;overflow-y:auto;color:#f8fafc;font-family:system-ui,-apple-system,sans-serif;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function flipEvolveModalPreviewState() {
    EVOLVE_RUNTIME_STATE.previewShowEvolved = !EVOLVE_RUNTIME_STATE.previewShowEvolved;
    renderEvolveModalContents();
    return EVOLVE_RUNTIME_STATE.previewShowEvolved;
  }

  function selectEvolveModalPair(pairIdx) {
    const clamped = Math.max(0, Math.min(EVOLVE_MECH_WING_MAIDEN_PAIRS.length - 1, Number(pairIdx) || 0));
    EVOLVE_RUNTIME_STATE.selectedPairIndex = clamped;
    renderEvolveModalContents();
    return EVOLVE_MECH_WING_MAIDEN_PAIRS[clamped];
  }

  function renderEvolveModalContents() {
    const modal = ensureEvolveModalDom();
    if (!modal) return;

    const pair = EVOLVE_MECH_WING_MAIDEN_PAIRS[EVOLVE_RUNTIME_STATE.selectedPairIndex] || EVOLVE_MECH_WING_MAIDEN_PAIRS[0];
    const showEvo = EVOLVE_RUNTIME_STATE.previewShowEvolved;
    const st = globalScope.state || {};
    const epCount = typeof st.playerEvolvePoints === "number" ? st.playerEvolvePoints : 2;

    const rosterTabsHtml = EVOLVE_MECH_WING_MAIDEN_PAIRS.map(function (p, idx) {
      const active = idx === EVOLVE_RUNTIME_STATE.selectedPairIndex;
      return (
        '<button onclick="window.CardFrontEvolveMaidenEngine.selectEvolveModalPair(' + idx + ')" style="padding:8px 12px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;border:1px solid ' +
        (active ? "#FACC15" : "rgba(148,163,184,0.3)") +
        ";background:" +
        (active ? "linear-gradient(135deg,rgba(234,179,8,0.25),rgba(16,185,129,0.22))" : "rgba(15,23,42,0.85)") +
        ";color:" +
        (active ? "#FEF08A" : "#CBD5E1") +
        ';">' +
        "[0" + (idx + 1) + "] " + p.characterTitleEn +
        "</button>"
      );
    }).join("");

    const baseCardHtml = renderEvolveSrCardHtml(pair, false);
    const evoCardHtml = renderEvolveSrCardHtml(pair, true);
    const activeInteractiveCardHtml = renderEvolveSrCardHtml(pair, showEvo);

    modal.innerHTML =
      '<div style="max-width:1140px;margin:0 auto;background:#090d16;border:1.5px solid #D4AF37;border-radius:14px;padding:18px;box-shadow:0 24px 64px rgba(0,0,0,0.88);">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;border-bottom:1px solid rgba(212,175,55,0.3);padding-bottom:12px;margin-bottom:14px;">' +
          '<div>' +
            '<div style="font-size:11px;font-weight:800;color:#2EE6D3;letter-spacing:0.08em;">[SHADOWVERSE-EVOLVE BP05-110 SR INSPIRED · GUNMETAL-FILIGREE FRAME · 進化前 <-> 進化後]</div>' +
            '<div style="font-size:18px;font-weight:900;color:#F8FAFC;">Mech-Wing Maiden Evolve Studio (5 Paired Maidens · 10 Playable SR/UR Cards)</div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">' +
            '<span style="font-size:11px;font-weight:800;color:#FEF08A;background:rgba(234,179,8,0.16);border:1px solid #FACC15;padding:5px 10px;border-radius:6px;">[EVOLVE POINTS (EP): ' + epCount + ']</span>' +
            '<button id="btn-equip-evolve-maiden-deck" onclick="equipEvolveMechWingMaidenDeck()" style="padding:8px 13px;border-radius:7px;background:linear-gradient(135deg,#10B981,#059669);color:#04120C;font-weight:900;font-size:11.5px;border:1px solid #6EE7B7;cursor:pointer;">[EQUIP MECH-WING MAIDEN EVOLVE DECK]</button>' +
            '<button onclick="closeEvolveMaidenStudioModal()" style="padding:8px 12px;border-radius:7px;background:rgba(239,68,68,0.2);color:#FCA5A5;border:1px solid #EF4444;font-weight:800;font-size:11.5px;cursor:pointer;">[CLOSE ESC]</button>' +
          '</div>' +
        '</div>' +
        // Maiden Pair Selector Row
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">' +
          rosterTabsHtml +
        '</div>' +
        // Action Bar: Flip Base <-> Evolved, Trigger Evolve on 3x3 Board, Toggle Gunmetal SR Frame
        '<div style="background:rgba(15,23,42,0.92);border:1px solid rgba(192,200,216,0.35);border-radius:10px;padding:12px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">' +
          '<div>' +
            '<div style="font-size:13px;font-weight:800;color:#FEF08A;">' + pair.characterTitleJa + ' · ' + pair.characterTitleEn + '</div>' +
            '<div style="font-size:11px;color:#94A3B8;">Trait: <b>' + pair.traitEn + ' / ' + pair.traitJa + '</b> · Base Sum: <b>' + pair.baseCard.directionalSum + '</b> -> Evolved Sum: <b>' + pair.evoCard.directionalSum + '</b></div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
            '<button id="btn-flip-evolve-preview" onclick="window.CardFrontEvolveMaidenEngine.flipEvolveModalPreviewState()" style="padding:8px 12px;border-radius:6px;background:linear-gradient(135deg,#D4AF37,#92400E);color:#FFFBEB;border:1px solid #FDE68A;font-size:11px;font-weight:900;cursor:pointer;">[FLIP: BASE 進化前 &lt;-&gt; EVOLVED 進化後]</button>' +
            '<button id="btn-trigger-board-evolve" onclick="evolveCardOnBoard(4, window.state)" style="padding:8px 12px;border-radius:6px;background:linear-gradient(135deg,#2EE6D3,#0284C7);color:#041019;border:none;font-size:11px;font-weight:900;cursor:pointer;">[EVOLVE ON 3x3 BOARD (CELL 4)]</button>' +
            '<button onclick="applyEvolveSrFrameStyle(!window.CardFrontEvolveMaidenEngine.state.srFrameStyleEnabled)" style="padding:8px 12px;border-radius:6px;background:#1E293B;color:#E2E8F0;border:1px solid #94A3B8;font-size:11px;font-weight:800;cursor:pointer;">[GUNMETAL SR FRAME: ' + (EVOLVE_RUNTIME_STATE.srFrameStyleEnabled ? "ON" : "OFF") + ']</button>' +
          '</div>' +
        '</div>' +
        // 3-Column Card Showcase: Base SR (進化前) | Interactive 3D Flip Preview | Awakened UR (進化後)
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(284px,1fr));gap:18px;justify-items:center;align-items:start;">' +
          '<div style="text-align:center;">' +
            '<div style="font-size:11px;font-weight:800;color:#94A3B8;margin-bottom:6px;">[BASE FORM · 進化前 · ' + pair.baseCard.setCode + ']</div>' +
            baseCardHtml +
          '</div>' +
          '<div style="text-align:center;">' +
            '<div style="font-size:11px;font-weight:800;color:#2EE6D3;margin-bottom:6px;">[INTERACTIVE 3D FLIP INSPECTOR (' + (showEvo ? "進化後 UR" : "進化前 SR") + ')]</div>' +
            activeInteractiveCardHtml +
          '</div>' +
          '<div style="text-align:center;">' +
            '<div style="font-size:11px;font-weight:800;color:#FACC15;margin-bottom:6px;">[EVOLVED FORM · 進化後 · ' + pair.evoCard.setCode + ']</div>' +
            evoCardHtml +
          '</div>' +
        '</div>' +
      '</div>';
  }

  function openEvolveMaidenStudioModal(pairIndex) {
    registerEvolveMechWingCards();
    ensureEvolveStylesInjected();
    if (typeof pairIndex === "number" && !isNaN(pairIndex)) {
      EVOLVE_RUNTIME_STATE.selectedPairIndex = Math.max(0, Math.min(EVOLVE_MECH_WING_MAIDEN_PAIRS.length - 1, pairIndex));
    }
    const modal = ensureEvolveModalDom();
    renderEvolveModalContents();
    if (modal) {
      modal.style.display = "block";
    }
    return {
      ok: true,
      selectedPairIndex: EVOLVE_RUNTIME_STATE.selectedPairIndex,
      pairsCount: EVOLVE_MECH_WING_MAIDEN_PAIRS.length,
      totalEvolveCardsCount: EVOLVE_MECH_WING_CARDS_10.length
    };
  }

  function closeEvolveMaidenStudioModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("evolve-maiden-studio-modal");
    if (modal) {
      modal.style.display = "none";
    }
  }

  function decorateBoardCardsWithEvolveButtons() {
    if (typeof globalScope.document === "undefined") return;
    ensureEvolveStylesInjected();
    const st = globalScope.state;
    const slots = globalScope.document.querySelectorAll("#grid-3x3 .board-slot");
    slots.forEach(function (slotEl, cellIdx) {
      const unitEl = slotEl.querySelector(".card-3d-unit");
      if (!unitEl) return;
      const r = Math.floor(cellIdx / 3);
      const c = cellIdx % 3;
      const cell = st && st.grid && st.grid[r] && st.grid[r][c];
      if (!cell || !cell.cardId || cell.owner !== "player") return;
      const existingBtn = unitEl.querySelector(".cf-board-evolve-btn");
      if (existingBtn) existingBtn.remove();
      const btn = globalScope.document.createElement("button");
      btn.type = "button";
      const isEvo = Boolean(cell.evolved || String(cell.cardId).endsWith("_evo"));
      btn.className = "cf-board-evolve-btn" + (isEvo ? " is-evolved" : "");
      btn.textContent = isEvo ? "UR EVO" : "EVOLVE";
      btn.title = isEvo ? "Evolved Awakened Form Active" : "Click to Evolve this unit on the 3x3 Board (+Stats & Ward)";
      if (!isEvo) {
        btn.onclick = function (ev) {
          ev.stopPropagation();
          evolveCardOnBoard(cellIdx, globalScope.state);
        };
      }
      unitEl.appendChild(btn);
    });
  }

  function installEvolveBoardHooks() {
    registerEvolveMechWingCards();
    applyEvolveSrFrameStyle(true);
    if (globalScope.state && Array.isArray(globalScope.state.unlockedCards)) {
      EVOLVE_MECH_WING_CARDS_10.forEach(function (c) {
        if (!globalScope.state.unlockedCards.includes(c.id)) {
          globalScope.state.unlockedCards.push(c.id);
        }
      });
    }
    if (typeof globalScope.renderAll === "function" && !globalScope.renderAll._cfEvolveBoardHooked) {
      const origRender = globalScope.renderAll;
      const wrappedRender = function () {
        const res = origRender.apply(this, arguments);
        decorateBoardCardsWithEvolveButtons();
        return res;
      };
      wrappedRender._cfEvolveBoardHooked = true;
      globalScope.renderAll = wrappedRender;
    }
    decorateBoardCardsWithEvolveButtons();
  }

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", installEvolveBoardHooks);
    } else {
      installEvolveBoardHooks();
    }
    globalScope.addEventListener("load", installEvolveBoardHooks);
  }

  // ==========================================================================
  // 8. EXPOSE MODULE & GLOBAL API
  // ==========================================================================
  const CardFrontEvolveMaidenEngine = {
    EVOLVE_MECH_WING_MAIDEN_PAIRS: EVOLVE_MECH_WING_MAIDEN_PAIRS,
    EVOLVE_MECH_WING_CARDS_10: EVOLVE_MECH_WING_CARDS_10,
    state: EVOLVE_RUNTIME_STATE,
    registerEvolveMechWingCards: registerEvolveMechWingCards,
    evolveCardOnBoard: evolveCardOnBoard,
    renderEvolveSrCardHtml: renderEvolveSrCardHtml,
    applyEvolveSrFrameStyle: applyEvolveSrFrameStyle,
    equipEvolveMechWingMaidenDeck: equipEvolveMechWingMaidenDeck,
    selectEvolveModalPair: selectEvolveModalPair,
    flipEvolveModalPreviewState: flipEvolveModalPreviewState,
    openEvolveMaidenStudioModal: openEvolveMaidenStudioModal,
    closeEvolveMaidenStudioModal: closeEvolveMaidenStudioModal,
    zeroLivingArtistNames: true,
    zeroRawUnicodeEmojis: true
  };

  globalScope.CardFrontEvolveMaidenEngine = CardFrontEvolveMaidenEngine;
  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.EvolveMaidenEngine = CardFrontEvolveMaidenEngine;

  globalScope.EVOLVE_MECH_WING_MAIDEN_PAIRS = EVOLVE_MECH_WING_MAIDEN_PAIRS;
  globalScope.EVOLVE_MECH_WING_CARDS_10 = EVOLVE_MECH_WING_CARDS_10;
  globalScope.evolveCardOnBoard = evolveCardOnBoard;
  globalScope.renderEvolveSrCardHtml = renderEvolveSrCardHtml;
  globalScope.applyEvolveSrFrameStyle = applyEvolveSrFrameStyle;
  globalScope.equipEvolveMechWingMaidenDeck = equipEvolveMechWingMaidenDeck;
  globalScope.openEvolveMaidenStudioModal = openEvolveMaidenStudioModal;
  globalScope.closeEvolveMaidenStudioModal = closeEvolveMaidenStudioModal;
})(typeof window !== "undefined" ? window : globalThis);
