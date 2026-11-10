/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes -- CardCraftCollectables (C³) Dual-Sided
 * Character Bromide, Lore Chronicle & Variations Metadata Engine (v2.0.0)
 * Module: WebPlayable/modules/cardcraft_collectables_c3_engine.js
 *
 * Implements the Dual-Sided Collector Bromide & Variations Dossier for all
 * 141+ playable cards across CARDFRONT:
 *   - LEFT SIDE (Obverse): Full-Body Character Composition on Ivory-Mint
 *     Collector Filigree, Vertical Character Name on Left Spine, Vertical
 *     Affiliation on Right Spine, and "Studio PxG" Signature Crest at Bottom.
 *   - RIGHT SIDE (Reverse): Blueprint-Indigo C³ Unit Profile & Lore Dossier
 *     with Cyanotype Blueprint Silhouette, C³ Series No.XXX Pennant, 6 Profile
 *     Data Callout Boxes, Narrative Lore Chronicle, and Official Standard +
 *     Premium Foil Variations Metadata Table:
 *       - original title: 機構翼の少女・ローザ(進化前)
 *       - card game: Shadowverse EVOLVE
 *       - version: [BP05] Eternal omens
 *       - original version: ブースターパック第5弾 永劫なる絶傑
 *       - card number: BP05-110 SR / BP05-P50 Premium SR
 *       - rarity: SR / Premium SR
 *       - spec: Foil (Variations metadata)
 * ============================================================================ */

(function initCardCraftCollectablesC3Engine(globalScope) {
  "use strict";

  function buildRecordShape(raw) {
    const std = raw.standardEdition || raw.standard_edition || {
      originalTitle: raw.originalTitle || raw.original_title || "",
      cardGame: "Shadowverse EVOLVE",
      version: "[BP05] Eternal omens",
      originalVersion: "ブースターパック第5弾 永劫なる絶傑",
      cardNumber: "BP05-110 SR",
      rarity: "SR",
      spec: "Standard"
    };
    const prm = raw.premiumVariation || raw.premium_variation || {
      originalTitle: raw.originalTitle || raw.original_title || "",
      cardGame: "Shadowverse EVOLVE",
      version: "[BP05] Eternal omens",
      originalVersion: "ブースターパック第5弾 永劫なる絶傑",
      cardNumber: "BP05-P50 Premium SR",
      rarity: "Premium SR",
      spec: "Foil"
    };

    const stdNormalized = {
      originalTitle: std.originalTitle || std.original_title || raw.originalTitle || raw.original_title || "",
      original_title: std.original_title || std.originalTitle || raw.originalTitle || raw.original_title || "",
      cardGame: std.cardGame || std.card_game || "Shadowverse EVOLVE",
      card_game: std.card_game || std.cardGame || "Shadowverse EVOLVE",
      version: std.version || "[BP05] Eternal omens",
      originalVersion: std.originalVersion || std.original_version || "ブースターパック第5弾 永劫なる絶傑",
      original_version: std.original_version || std.originalVersion || "ブースターパック第5弾 永劫なる絶傑",
      cardNumber: std.cardNumber || std.card_number || "BP05-110 SR",
      card_number: std.card_number || std.cardNumber || "BP05-110 SR",
      rarity: std.rarity || "SR",
      spec: std.spec || "Standard"
    };

    const prmNormalized = {
      originalTitle: prm.originalTitle || prm.original_title || raw.originalTitle || raw.original_title || "",
      original_title: prm.original_title || prm.originalTitle || raw.originalTitle || raw.original_title || "",
      cardGame: prm.cardGame || prm.card_game || "Shadowverse EVOLVE",
      card_game: prm.card_game || prm.cardGame || "Shadowverse EVOLVE",
      version: prm.version || "[BP05] Eternal omens",
      originalVersion: prm.originalVersion || prm.original_version || "ブースターパック第5弾 永劫なる絶傑",
      original_version: prm.original_version || prm.originalVersion || "ブースターパック第5弾 永劫なる絶傑",
      cardNumber: prm.cardNumber || prm.card_number || "BP05-P50 Premium SR",
      card_number: prm.card_number || prm.cardNumber || "BP05-P50 Premium SR",
      rarity: prm.rarity || "Premium SR",
      spec: prm.spec || "Foil"
    };

    const cid = raw.cardId || raw.card_id || "ev_01_base";
    const nameEn = raw.nameEn || raw.character_name || raw.name_en || cid.toUpperCase();
    const originalTitle = raw.originalTitle || raw.original_title || stdNormalized.originalTitle;
    const sheetRel = (raw.dual_bromide_sheet || raw.bromideSheetUrl || "GeneratedArt/CollectablesC3/c3_rosa_bp05_110_sr_dual_bromide.png").replace(/^\.\//, "");
    const sheetUrl = sheetRel.startsWith("./") ? sheetRel : `./${sheetRel}`;
    const artClean = (raw.artUrl || raw.web_art_url || raw.art_path || "./GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png").replace(/^WebPlayable\//, "./");
    const artUrl = artClean.startsWith("./") || artClean.startsWith("http") ? artClean : `./${artClean}`;

    return {
      cardId: cid,
      card_id: cid,
      c3Number: raw.c3Number || raw.c3_number || "No.110",
      c3_number: raw.c3_number || raw.c3Number || "No.110",
      nameEn,
      name_en: nameEn,
      character_name: raw.character_name || nameEn,
      originalTitle,
      original_title: originalTitle,
      cvCredit: raw.cvCredit || raw.cv_credit || "CV. 佐倉綾音 · Studio PxG",
      cv_credit: raw.cv_credit || raw.cvCredit || "CV. 佐倉綾音 · Studio PxG",
      studioSignature: "Studio PxG",
      studio_signature: "Studio PxG",
      seriesHeader: "CardCraftCollectables C³",
      series_header: "CardCraftCollectables C³",
      affiliation: raw.affiliation || "CardFront: Cradle of Echoes · Chrono-Seraph",
      gradeStage: raw.gradeStage || raw.grade_stage || "1st Year · Vanguard",
      grade_stage: raw.grade_stage || raw.gradeStage || "1st Year · Vanguard",
      activationDate: raw.activationDate || raw.activation_date || "10月5日 (Eternal Omens)",
      activation_date: raw.activation_date || raw.activationDate || "10月5日 (Eternal Omens)",
      heightSpec: raw.heightSpec || raw.height_spec || "160cm · Aether Frame",
      height_spec: raw.height_spec || raw.heightSpec || "160cm · Aether Frame",
      threeMetrics: raw.threeMetrics || raw.three_metrics || "N:8 / E:8 / S:7 / W:8",
      three_metrics: raw.three_metrics || raw.threeMetrics || "N:8 / E:8 / S:7 / W:8",
      bloodCoreType: raw.bloodCoreType || raw.blood_core_type || "Type-AB · Astral Quartz",
      blood_core_type: raw.blood_core_type || raw.bloodCoreType || "Type-AB · Astral Quartz",
      constellationArchetype: raw.constellationArchetype || raw.constellation_archetype || "てんびん座 (Libra)",
      constellation_archetype: raw.constellation_archetype || raw.constellationArchetype || "てんびん座 (Libra)",
      artUrl,
      web_art_url: artUrl,
      dual_bromide_sheet: sheetRel,
      bromideSheetUrl: sheetUrl,
      loreStory: raw.loreStory || raw.lore_story || "",
      lore_story: raw.lore_story || raw.loreStory || "",
      standardEdition: stdNormalized,
      standard_edition: stdNormalized,
      premiumVariation: prmNormalized,
      premium_variation: prmNormalized,
      variations: [stdNormalized, prmNormalized]
    };
  }

  // 10 Curated Built-In Dual-Side Bromide Cards (5 original + 5 newly curated in v2.0.0)
  const FEATURED_CARDS = [
    buildRecordShape({
      cardId: "ev_01_base",
      c3Number: "No.110",
      nameEn: "ROSA, MECH-WING MAIDEN",
      character_name: "Rosa, Mech-Wing Maiden",
      originalTitle: "機構翼の少女・ローザ(進化前)",
      cvCredit: "CV. 佐倉綾音 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Chrono-Seraph",
      gradeStage: "1st Year · Aether Cadet",
      activationDate: "10月5日 (Eternal Omens)",
      heightSpec: "160cm · Wing-Span 240cm",
      threeMetrics: "B79 W56 H78 · ATK 8 / DEF 7",
      bloodCoreType: "Type-AB · Astral Quartz",
      constellationArchetype: "てんびん座 (Libra · Pinion)",
      artUrl: "./GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_rosa_bp05_110_sr_dual_bromide.png",
      loreStory:
        "Born beneath the clockwork vaults of the Skystone Sanctuary, Rosa calibrated the first pair of Chrono-Seraph mechanical pinions before her sixteenth autumn. Each feather-blade channels Studio PxG's 24fps Aether-Vector resonance across the 3x3 Skystone Arena.",
      standardEdition: {
        originalTitle: "機構翼の少女・ローザ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-110 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "機構翼の少女・ローザ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P50 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "ev_01_evo",
      c3Number: "No.111",
      nameEn: "ROSA, AWAKENED SERAPH",
      character_name: "Rosa, Awakened Seraph",
      originalTitle: "機構翼の少女・ローザ(進化後)",
      cvCredit: "CV. 佐倉綾音 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Chrono-Seraph",
      gradeStage: "Awakened Seraphic Form",
      activationDate: "10月5日 (Eternal Omens)",
      heightSpec: "162cm · 6-Wing Overdrive",
      threeMetrics: "B79 W56 H78 · ATK 9 / DEF 9",
      bloodCoreType: "Type-AB · Sovereign Gold",
      constellationArchetype: "てんびん座 (Libra · Arbiter)",
      artUrl: "./GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_arch_seraph_overdrive.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_rosa_bp05_111_ur_dual_bromide.png",
      loreStory:
        "When the Third Seal of Eternal Omens fractures, Rosa's twin mechanical wings unfold into six golden seraphic rail-blades. In her Awakened state, her telemetry links directly to the Citadel's astral astrolabe, turning every adjacent allied unit into an unbreakable bastion.",
      standardEdition: {
        originalTitle: "機構翼の少女・ローザ(進化後)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-111 UR",
        rarity: "UR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "機構翼の少女・ローザ(進化後)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P51 Premium UR",
        rarity: "Premium UR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "plugin_01_tcg_creative_designer",
      c3Number: "No.001",
      nameEn: "GRAND ARCANIST DESIGNER",
      character_name: "Grand Arcanist Designer",
      originalTitle: "創世の魔導設計者・アルカニスト",
      cvCredit: "CV. 早見沙織 · Studio PxG",
      affiliation: "CardFront: Sovereign Agent Command",
      gradeStage: "Mythic Sovereign Plugin",
      activationDate: "11月9日 (Sovereign Genesis)",
      heightSpec: "168cm · Atelier Astrolabe",
      threeMetrics: "N:9 / E:8 / S:8 / W:9",
      bloodCoreType: "Ivalice Gold · Type-S",
      constellationArchetype: "おとめ座 (Virgo · Architect)",
      artUrl: "./GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_grand_arcanist_cf01_001_dual_bromide.png",
      loreStory:
        "Wielding the gilded quill of the Sovereign Atelier, the Grand Arcanist inscribes living card geometry directly onto the 3x3 Sanctum slab. Every stroke of her brush binds ink, law, and chromatic light into tournament-grade tactical constructs.",
      standardEdition: {
        originalTitle: "創世の魔導設計者・アルカニスト",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "CF01-001 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "創世の魔導設計者・アルカニスト",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "CF01-P01 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "h_archangel",
      c3Number: "No.010",
      nameEn: "SOLAR ARCHANGEL SERAPHINA",
      character_name: "Solar Archangel Seraphina",
      originalTitle: "太陽の熾天使・セラフィナ(進化前)",
      cvCredit: "CV. 川澄綾子 · Studio PxG",
      affiliation: "CardFront: Solaris Sanctuary Club",
      gradeStage: "1st Order · High Seraph",
      activationDate: "3月21日 (Equinox Dawn)",
      heightSpec: "165cm · Halo Aegis Mk.IV",
      threeMetrics: "N:8 / E:7 / S:6 / W:7",
      bloodCoreType: "Type-A · Solar Flare",
      constellationArchetype: "おひつじ座 (Aries · Spear)",
      artUrl: "./GeneratedArt/MasteredCards/h_archangel.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_solar_archangel_bp05_010_dual_bromide.png",
      loreStory:
        "Commander of the Skystone Choir and bearer of the Cruciform Dawn Lance. When Seraphina descends onto the central sanctum tile, her solar blessing radiates across the entire row and column, fortifying every allied vanguard against the Void.",
      standardEdition: {
        originalTitle: "太陽の熾天使・セラフィナ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-010 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "太陽の熾天使・セラフィナ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P10 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "pxg_s01",
      c3Number: "No.077",
      nameEn: "ASTRA VANGUARD STRIKER",
      character_name: "Astra Vanguard Striker",
      originalTitle: "極限作画の閃光・アストラ(24fps)",
      cvCredit: "CV. 中村悠一 · Studio PxG",
      affiliation: "CardFront: Studio PxG Atomic Strikers",
      gradeStage: "Lead Striker · 24fps Master",
      activationDate: "7月7日 (Trigger Star)",
      heightSpec: "176cm · Kagenashi Odachi",
      threeMetrics: "N:9 / E:9 / S:7 / W:8",
      bloodCoreType: "Type-O · Crimson Ink",
      constellationArchetype: "しし座 (Leo · Impact Frame)",
      artUrl: "./GeneratedArt/StudioPxGAtomic/pxg_s01_astra_vanguard_striker.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_kurogane_bp05_077_dual_bromide.png",
      loreStory:
        "Forged in the monochrome stencil furnaces of Neo-Arcadia, Astra moves between 24fps keyframe intervals. His diagonal Kagenashi slash cleaves through enemy guard shields before the human eye can register the impact flash.",
      standardEdition: {
        originalTitle: "極限作画の閃光・アストラ(24fps)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-077 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "極限作画の閃光・アストラ(24fps)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P77 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "ev_03_base",
      c3Number: "No.044",
      nameEn: "CELESTE, CHRONO-FEATHER VALKYRIE",
      character_name: "Celeste, Chrono-Feather Valkyrie",
      originalTitle: "時翼の戦乙女・セレステ(進化前)",
      cvCredit: "CV. 悠木碧 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Solaris",
      gradeStage: "太陽聖堂騎士団 · Vanguard",
      activationDate: "12月16日 ([BP05] Eternal omens)",
      heightSpec: "158cm · Harmonic Pinion",
      threeMetrics: "N:8 / E:7 / S:8 / W:8",
      bloodCoreType: "Type-AB · Chrono Core",
      constellationArchetype: "おとめ座 (Virgo · 星詠みの乙女座)",
      artUrl: "./GeneratedArt/EvolveMechWingMaidens/ev_03_base_lyra_harmony_automata.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_cassandra_bp05_044_sr_dual_bromide.png",
      loreStory:
        "Archived in the CardCraftCollectables C³ Sanctuary Vault under BP05-114 SR. Celeste, Chrono-Feather Valkyrie serves the Solaris Order across the 3x3 Skystone Arena, channeling Studio PxG's directional Aether resonance to turn the tide of the Eternal Omens campaign.",
      standardEdition: {
        originalTitle: "時翼の戦乙女・セレステ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-114 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "時翼の戦乙女・セレステ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P54 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "ev_04_base",
      c3Number: "No.088",
      nameEn: "NOCTIS-LUMINA, GUNMETAL ANGEL",
      character_name: "Noctis-Lumina, Gunmetal Angel",
      originalTitle: "銃鉄の黒翼天使・ルミナ(進化前)",
      cvCredit: "CV. 花澤香菜 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Void",
      gradeStage: "深淵虚無レギオン · Vanguard",
      activationDate: "12月12日 ([BP05] Eternal omens)",
      heightSpec: "175cm · Gunmetal Aegis",
      threeMetrics: "N:8 / E:8 / S:6 / W:8",
      bloodCoreType: "Type-AB · Chrono Core",
      constellationArchetype: "いて座 (Sagittarius · 光矢の射手座)",
      artUrl: "./GeneratedArt/EvolveMechWingMaidens/ev_04_base_ignia_blaze_pinion_maiden.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_seraphina_bp05_088_sr_dual_bromide.png",
      loreStory:
        "Archived in the CardCraftCollectables C³ Sanctuary Vault under BP05-116 SR. Noctis-Lumina, Gunmetal Angel serves the Void Order across the 3x3 Skystone Arena, channeling Studio PxG's directional Aether resonance to turn the tide of the Eternal Omens campaign.",
      standardEdition: {
        originalTitle: "銃鉄の黒翼天使・ルミナ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-116 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "銃鉄の黒翼天使・ルミナ(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P56 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "ev_05_base",
      c3Number: "No.105",
      nameEn: "AURELIA, GRAND ACADEMY STRIKER",
      character_name: "Aurelia, Grand Academy Striker",
      originalTitle: "聖冠の学園機翼・アウレリア(進化前)",
      cvCredit: "CV. 沢城みゆき · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Solaris",
      gradeStage: "太陽聖堂騎士団 · Vanguard",
      activationDate: "1月21日 ([BP05] Eternal omens)",
      heightSpec: "178cm · Eclipse Frame",
      threeMetrics: "N:8 / E:8 / S:8 / W:7",
      bloodCoreType: "Type-A · Astral Core",
      constellationArchetype: "みずがめ座 (Aquarius · 蒼穹の水瓶座)",
      artUrl: "./GeneratedArt/EvolveMechWingMaidens/ev_05_base_nocturna_eclipse_wing_saint.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_lilith_bp05_105_sr_dual_bromide.png",
      loreStory:
        "Archived in the CardCraftCollectables C³ Sanctuary Vault under BP05-118 SR. Aurelia, Grand Academy Striker serves the Solaris Order across the 3x3 Skystone Arena, channeling Studio PxG's directional Aether resonance to turn the tide of the Eternal Omens campaign.",
      standardEdition: {
        originalTitle: "聖冠の学園機翼・アウレリア(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-118 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "聖冠の学園機翼・アウレリア(進化前)",
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: "BP05-P58 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "plugin_02_parallel_swarm_orchestrator",
      c3Number: "No.092",
      nameEn: "PARALLEL SWARM ORCHESTRATOR",
      character_name: "Parallel Swarm Orchestrator",
      originalTitle: "至高権能・エージェント第02章(神話級)",
      cvCredit: "CV. 佐倉綾音 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Sovereign Law",
      gradeStage: "至高律法評議会 · Sovereign Plugin",
      activationDate: "5月17日 ([CF-S01] Sovereign Genesis)",
      heightSpec: "166cm · Swarm Nexus Array",
      threeMetrics: "N:9 / E:8 / S:8 / W:9",
      bloodCoreType: "Type-A · Astral Core",
      constellationArchetype: "てんびん座 (Libra · 均衡の天秤座)",
      artUrl: "./GeneratedArt/AgentDeck/Cards/plugin_02_parallel_swarm_orchestrator.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_swarm_orchestrator_cf01_002_dual_bromide.png",
      loreStory:
        "Archived in the CardCraftCollectables C³ Sanctuary Vault under CF01-002 SR. Parallel Swarm Orchestrator commands concurrent tactical subagents across the 3x3 Skystone Arena, synchronizing multi-lane pincer formations in real time.",
      standardEdition: {
        originalTitle: "至高権能・エージェント第02章(神話級)",
        cardGame: "Shadowverse EVOLVE",
        version: "[CF-S01] Sovereign Genesis",
        originalVersion: "創世神話ブースター 第1弾 王権の刻印",
        cardNumber: "CF01-002 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "至高権能・エージェント第02章(神話級)",
        cardGame: "Shadowverse EVOLVE",
        version: "[CF-S01] Sovereign Genesis",
        originalVersion: "創世神話ブースター 第1弾 王権の刻印",
        cardNumber: "CF01-P02 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    }),
    buildRecordShape({
      cardId: "plugin_03_jev_system_one",
      c3Number: "No.093",
      nameEn: "JEV SYSTEM ONE ARBITER",
      character_name: "Jev System One Arbiter",
      originalTitle: "至高権能・エージェント第03章(神話級)",
      cvCredit: "CV. 悠木碧 · Studio PxG",
      affiliation: "CardFront: Cradle of Echoes · Sovereign Law",
      gradeStage: "至高律法評議会 · Sovereign Plugin",
      activationDate: "8月20日 ([CF-S01] Sovereign Genesis)",
      heightSpec: "169cm · Calibrated Scales",
      threeMetrics: "N:9 / E:8 / S:8 / W:9",
      bloodCoreType: "Type-AB · Chrono Core",
      constellationArchetype: "おとめ座 (Virgo · 星詠みの乙女座)",
      artUrl: "./GeneratedArt/AgentDeck/Cards/plugin_03_jev_system_one.png",
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_jev_arbiter_cf01_003_dual_bromide.png",
      loreStory:
        "Archived in the CardCraftCollectables C³ Sanctuary Vault under CF01-003 SR. Jev System One Arbiter weighs every tactical proposition with calibrated probability gates, sealing enemy misplays beneath Ivalice Law Gold decrees.",
      standardEdition: {
        originalTitle: "至高権能・エージェント第03章(神話級)",
        cardGame: "Shadowverse EVOLVE",
        version: "[CF-S01] Sovereign Genesis",
        originalVersion: "創世神話ブースター 第1弾 王権の刻印",
        cardNumber: "CF01-003 SR",
        rarity: "SR",
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: "至高権能・エージェント第03章(神話級)",
        cardGame: "Shadowverse EVOLVE",
        version: "[CF-S01] Sovereign Genesis",
        originalVersion: "創世神話ブースター 第1弾 王権の刻印",
        cardNumber: "CF01-P03 Premium SR",
        rarity: "Premium SR",
        spec: "Foil"
      }
    })
  ];

  const C3_FEATURED_OVERRIDES = {};
  FEATURED_CARDS.forEach((item) => {
    C3_FEATURED_OVERRIDES[item.cardId] = item;
  });

  const CV_POOL = [
    "CV. 佐倉綾音 · Studio PxG",
    "CV. 早見沙織 · Studio PxG",
    "CV. 川澄綾子 · Studio PxG",
    "CV. 悠木碧 · Studio PxG",
    "CV. 沢城みゆき · Studio PxG",
    "CV. 中村悠一 · Studio PxG",
    "CV. 諏訪部順一 · Studio PxG",
    "CV. 花澤香菜 · Studio PxG"
  ];

  const ZODIAC_POOL = [
    "てんびん座 (Libra)",
    "おひつじ座 (Aries)",
    "しし座 (Leo)",
    "おとめ座 (Virgo)",
    "みずがめ座 (Aquarius)",
    "さそり座 (Scorpio)",
    "ふたご座 (Gemini)",
    "いて座 (Sagittarius)"
  ];

  function hashCardId(str) {
    const s = String(str || "ev_01_base");
    let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function icon(name, size = 14, style = "") {
    if (typeof globalScope.cfIcon === "function") {
      return globalScope.cfIcon(name, size, style);
    }
    return `<svg class="cf-lib-icon" width="${size}" height="${size}" viewBox="0 0 256 256" fill="none" style="vertical-align:-2px;${style}"><polygon points="128,16 224,72 224,184 128,240 32,184 32,72" fill="#0F172A" stroke="#FFB800" stroke-width="14"/><circle cx="128" cy="128" r="44" fill="#00E5FF"/></svg>`;
  }

  // Deterministic 141-card C³ Registry & reactive state
  const c3RegistryByCardId = {};

  const state = {
    selectedCardId: "ev_01_base",
    activeVariation: "PREMIUM_FOIL", // "STANDARD" or "PREMIUM_FOIL"
    variationIdx: 1, // 0 = Standard, 1 = Premium Foil
    viewMode: "LIVE_DUAL_DOM", // "LIVE_DUAL_DOM" or "RENDERED_1200x800_PLATE"
    catalogLoaded: false,
    catalog: []
  };

  function syncStateCatalogArray() {
    state.catalog = Object.keys(c3RegistryByCardId).map((k) => c3RegistryByCardId[k]);
    return state.catalog;
  }

  function getCardC3Record(cardId) {
    const cid = String(cardId || "ev_01_base");
    if (C3_FEATURED_OVERRIDES[cid]) {
      c3RegistryByCardId[cid] = C3_FEATURED_OVERRIDES[cid];
      return C3_FEATURED_OVERRIDES[cid];
    }
    if (c3RegistryByCardId[cid]) {
      return c3RegistryByCardId[cid];
    }

    const h = hashCardId(cid);
    const meta =
      typeof globalScope.getCardMeta === "function"
        ? globalScope.getCardMeta(cid)
        : null;
    const nameEn = (meta && meta.name ? meta.name : cid.replace(/_/g, " ")).toUpperCase();
    const faction = (meta && meta.faction) || "Chrono-Seraph";
    const nesw = meta && Array.isArray(meta.nesw) ? meta.nesw : [8, 8, 7, 8];
    const artUrl =
      (meta && meta.art) ||
      "./GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png";

    const numIdx = (h % 140) + 1;
    const isEvo = cid.includes("evo") || cid.includes("plugin_") || cid.includes("saga_");
    const rarityBase = isEvo ? "UR" : "SR";
    const cardNumStd = `BP05-${String(numIdx).padStart(3, "0")} ${rarityBase}`;
    const cardNumPrm = `BP05-P${String(numIdx).padStart(2, "0")} Premium ${rarityBase}`;
    const jpSuffix = isEvo ? "(進化後)" : "(進化前)";
    const jpTitle = `機構翼の聖典・${nameEn.slice(0, 14)}${jpSuffix}`;

    const rec = buildRecordShape({
      cardId: cid,
      c3Number: `No.${String(numIdx).padStart(3, "0")}`,
      nameEn,
      character_name: meta && meta.name ? meta.name : nameEn,
      originalTitle: jpTitle,
      cvCredit: CV_POOL[h % CV_POOL.length],
      affiliation: `CardFront: Cradle of Echoes · ${faction}`,
      gradeStage: `${faction} · 1st Vanguard`,
      activationDate: `${(h % 12) + 1}月${(h % 28) + 1}日 (Eternal Omens)`,
      heightSpec: `${155 + (h % 24)}cm · Aether Frame`,
      threeMetrics: `N:${nesw[0]} / E:${nesw[1]} / S:${nesw[2]} / W:${nesw[3]}`,
      bloodCoreType: h % 2 === 0 ? "Type-AB · Astral Core" : "Type-A · Chrono Quartz",
      constellationArchetype: ZODIAC_POOL[h % ZODIAC_POOL.length],
      artUrl,
      dual_bromide_sheet: "GeneratedArt/CollectablesC3/c3_rosa_bp05_110_sr_dual_bromide.png",
      loreStory: `Archived in the CardCraftCollectables C³ Vault under ${cardNumStd}. ${nameEn} channels Studio PxG's directional Aether resonance across the 3x3 Skystone Sanctum, preserving the ancient laws of the ${faction} Order during the Eternal Omens campaign.`,
      standardEdition: {
        originalTitle: jpTitle,
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: cardNumStd,
        rarity: rarityBase,
        spec: "Standard"
      },
      premiumVariation: {
        originalTitle: jpTitle,
        cardGame: "Shadowverse EVOLVE",
        version: "[BP05] Eternal omens",
        originalVersion: "ブースターパック第5弾 永劫なる絶傑",
        cardNumber: cardNumPrm,
        rarity: `Premium ${rarityBase}`,
        spec: "Foil"
      }
    });

    c3RegistryByCardId[cid] = rec;
    return rec;
  }

  function populateAll141C3Records() {
    Object.keys(C3_FEATURED_OVERRIDES).forEach((k) => {
      c3RegistryByCardId[k] = C3_FEATURED_OVERRIDES[k];
    });
    if (
      globalScope.CardFrontDice3DAndChibiUnits &&
      globalScope.CardFrontDice3DAndChibiUnits.CARD_TO_CHIBI_BINDINGS_141
    ) {
      Object.keys(
        globalScope.CardFrontDice3DAndChibiUnits.CARD_TO_CHIBI_BINDINGS_141
      ).forEach((cid) => {
        getCardC3Record(cid);
      });
    }
    syncStateCatalogArray();
  }

  async function loadCatalog(url = "../Datasets/cardcraft_collectables_c3_catalog.json") {
    populateAll141C3Records();
    if (typeof fetch !== "function") {
      return state.catalog;
    }
    try {
      const resp = await fetch(url);
      if (!resp.ok) return state.catalog;
      const data = await resp.json();
      const cardsObj = (data && data.cards) || {};
      Object.keys(cardsObj).forEach((cid) => {
        const raw = cardsObj[cid];
        const curated = C3_FEATURED_OVERRIDES[cid];
        const merged = buildRecordShape(
          Object.assign({}, raw, curated ? {
            dual_bromide_sheet: curated.dual_bromide_sheet,
            bromideSheetUrl: curated.bromideSheetUrl,
            artUrl: curated.artUrl
          } : {})
        );
        c3RegistryByCardId[cid] = curated || merged;
      });
      state.catalogLoaded = true;
      syncStateCatalogArray();
    } catch (_err) {
      // Keep built-in deterministic catalog when offline or running under file://
    }
    return state.catalog;
  }

  function ensureC3StylesAndModal() {
    if (typeof document === "undefined" || !document.body) return;
    if (!document.getElementById("c3-collectables-styles")) {
      const st = document.createElement("style");
      st.id = "c3-collectables-styles";
      st.textContent = `
        /* CARDCRAFT COLLECTABLES C³ DUAL-SIDE BROMIDE & VARIATIONS DOSSIER */
        .c3-dual-bromide-stage {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 14px;
          background: #0b1120;
          padding: 12px;
          border-radius: 14px;
          border: 2px solid #334155;
          box-shadow: 0 20px 50px rgba(0,0,0,0.85);
        }
        @media (max-width: 900px) {
          .c3-dual-bromide-stage {
            grid-template-columns: 1fr;
          }
        }
        /* LEFT BROMIDE: OBVERSE FULL-BODY COMPOSITION + VERTICAL NAME + STUDIO PXG CREST */
        .c3-bromide-left {
          position: relative;
          min-height: 490px;
          background: radial-gradient(circle at 50% 42%, #ffffff 0%, #f1f7f5 68%, #e2f1ec 100%);
          border-radius: 14px;
          border: 3px solid #3a8a80;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: space-between;
          padding: 16px 38px 14px 38px;
          box-shadow: inset 0 0 0 4px rgba(58,138,128,0.16);
        }
        .c3-bromide-left.c3-foil-active::after {
          content: "";
          position: absolute;
          inset: 0;
          background: linear-gradient(
            125deg,
            rgba(255,255,255,0) 15%,
            rgba(0,229,255,0.22) 35%,
            rgba(255,184,0,0.28) 50%,
            rgba(168,85,247,0.22) 65%,
            rgba(255,255,255,0) 85%
          );
          background-size: 220% 220%;
          animation: c3FoilShimmer 3.2s linear infinite;
          pointer-events: none;
          mix-blend-mode: screen;
        }
        @keyframes c3FoilShimmer {
          0%   { background-position: 0% 0%; }
          50%  { background-position: 100% 100%; }
          100% { background-position: 0% 0%; }
        }
        .c3-vert-name-left {
          position: absolute;
          left: 8px;
          top: 18px;
          writing-mode: vertical-rl;
          transform: rotate(180deg);
          font-size: 18px;
          font-weight: 900;
          letter-spacing: 2px;
          color: #2d7a70;
          text-transform: uppercase;
          white-space: nowrap;
          z-index: 4;
        }
        .c3-vert-club-right {
          position: absolute;
          right: 8px;
          top: 18px;
          writing-mode: vertical-rl;
          font-size: 12px;
          font-weight: 800;
          letter-spacing: 1.2px;
          color: #2d7a70;
          white-space: nowrap;
          z-index: 4;
        }
        .c3-left-art-window {
          position: relative;
          width: 100%;
          height: 380px;
          border-radius: 16px;
          border: 2.5px solid #3a8a80;
          overflow: hidden;
          background: #0f172a;
          box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22);
          z-index: 2;
        }
        .c3-left-art-window img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          object-position: center 12%;
          display: block;
        }
        .c3-studio-pxg-plaque {
          position: relative;
          margin-top: -18px;
          z-index: 5;
          background: #f8faf9;
          border: 3px solid #2d7a70;
          outline: 2px solid #d4a349;
          border-radius: 14px;
          padding: 6px 26px;
          text-align: center;
          box-shadow: 0 8px 20px rgba(0,0,0,0.18);
        }
        .c3-studio-pxg-title {
          font-size: 24px;
          font-weight: 900;
          color: #2d7a70;
          letter-spacing: 0.6px;
          line-height: 1.05;
        }
        .c3-studio-pxg-sub {
          font-size: 12px;
          font-weight: 900;
          color: #b48228;
          letter-spacing: 1px;
        }

        /* RIGHT BROMIDE: REVERSE BLUEPRINT C³ UNIT PROFILE & VARIATIONS METADATA */
        .c3-bromide-right {
          position: relative;
          min-height: 490px;
          background: #f8fafc;
          border-radius: 14px;
          border: 3px solid #1e3a8a;
          padding: 12px;
          color: #1e3a8a;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          gap: 8px;
        }
        .c3-right-top-pills {
          display: flex;
          justify-content: space-between;
          gap: 8px;
        }
        .c3-blueprint-pill {
          border: 2px solid #1e3a8a;
          border-radius: 99px;
          padding: 2px 12px;
          font-size: 12px;
          font-weight: 900;
          background: #ffffff;
          color: #1e3a8a;
        }
        .c3-profile-mid-grid {
          display: grid;
          grid-template-columns: 1.05fr 1.15fr 1.05fr;
          gap: 8px;
          align-items: stretch;
        }
        .c3-blueprint-box {
          background: #ffffff;
          border: 2px solid #1e3a8a;
          border-radius: 8px;
          padding: 6px 8px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }
        .c3-blueprint-center-fig {
          position: relative;
          border: 2px solid #1e3a8a;
          border-radius: 12px;
          overflow: hidden;
          background: radial-gradient(circle, #eff6ff 0%, #dbeafe 100%);
          min-height: 210px;
        }
        .c3-blueprint-center-fig img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          object-position: center 12%;
          filter: grayscale(100%) sepia(85%) hue-rotate(185deg) saturate(210%) brightness(1.04) contrast(1.12);
          opacity: 0.9;
        }
        .c3-variations-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }
        .c3-var-card {
          border: 2px solid #1e3a8a;
          border-radius: 8px;
          background: #ffffff;
          overflow: hidden;
        }
        .c3-var-card.c3-var-premium {
          border-color: #b48228;
          background: #fefcf3;
        }
        .c3-var-hdr {
          background: #1e3a8a;
          color: #ffffff;
          font-size: 12px;
          font-weight: 900;
          padding: 3px 8px;
        }
        .c3-var-card.c3-var-premium .c3-var-hdr {
          background: linear-gradient(90deg, #b48228, #d97706);
        }
        .c3-var-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
        }
        .c3-var-table td {
          padding: 2px 6px;
          border-bottom: 1px dotted rgba(30, 58, 138, 0.2);
          line-height: 1.25;
        }
        .c3-var-table td.c3-k {
          color: #64748b;
          font-weight: 800;
          width: 42%;
          white-space: nowrap;
        }
        .c3-var-table td.c3-v {
          color: #1e3a8a;
          font-weight: 900;
        }
      `;
      document.head.appendChild(st);
    }

    if (!document.getElementById("c3-collectables-modal")) {
      const modal = document.createElement("div");
      modal.id = "c3-collectables-modal";
      modal.className = "modal-backdrop";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.innerHTML = `
        <div class="modal-box" style="max-width:980px;width:96%;max-height:90vh;overflow-y:auto;text-align:left;">
          <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b4478;padding-bottom:8px;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
            <div>
              <div style="font-size:12px;font-weight:900;color:#FFB800;letter-spacing:1px;">CARDCRAFT COLLECTABLES (C³) · STUDIO PXG OFFICIAL ARCHIVE</div>
              <h3 style="font-size:18px;font-weight:900;color:#fff;margin:2px 0 0 0;">Dual-Side Character Bromide, Lore Chronicle &amp; Variations Metadata (141 Playable Cards)</h3>
            </div>
            <button onclick="window.CardFrontCollectablesC3.closeC3CollectablesModal()">Close</button>
          </div>
          <div id="c3-collectables-modal-body"></div>
        </div>
      `;
      document.body.appendChild(modal);
    }
  }

  function renderDualBromideHtml(cardId, variationMode = "PREMIUM_FOIL") {
    const rec = getCardC3Record(cardId);
    const std = rec.standardEdition;
    const prm = rec.premiumVariation;
    const isFoil = variationMode === "PREMIUM_FOIL";

    return `
      <div class="c3-dual-bromide-stage" data-c3-card-id="${rec.cardId}" data-dual-bromide-sheet="${rec.dual_bromide_sheet}">
        <!-- LEFT SIDE: FULL-BODY COMPOSITION + VERTICAL NAME ON LEFT + STUDIO PXG AT BOTTOM -->
        <div class="c3-bromide-left ${isFoil ? "c3-foil-active" : ""}">
          <div class="c3-vert-name-left">${rec.nameEn}</div>
          <div class="c3-vert-club-right">${rec.affiliation}</div>
          <div class="c3-left-art-window">
            <img src="${rec.artUrl}" alt="${rec.nameEn}" />
          </div>
          <div class="c3-studio-pxg-plaque">
            <div class="c3-studio-pxg-title">Studio PxG</div>
            <div class="c3-studio-pxg-sub">CARDCRAFT COLLECTABLES C³ · ${isFoil ? prm.cardNumber : std.cardNumber}</div>
          </div>
        </div>

        <!-- RIGHT SIDE: BLUEPRINT C³ UNIT PROFILE, LORE & VARIATIONS METADATA -->
        <div class="c3-bromide-right">
          <div class="c3-right-top-pills">
            <span class="c3-blueprint-pill">${rec.affiliation}</span>
            <span class="c3-blueprint-pill">C³ UNIT PROFILE</span>
          </div>

          <div style="display:flex;justify-content:space-between;align-items:stretch;gap:8px;">
            <div class="c3-blueprint-box" style="flex:1;">
              <div style="font-size:12px;font-weight:900;color:#1e3a8a;">${rec.nameEn}</div>
              <div style="font-size:16px;font-weight:900;color:#1e3a8a;margin:2px 0;">${rec.originalTitle}</div>
              <div style="font-size:12px;font-weight:800;color:#3b82f6;">${rec.cvCredit}</div>
            </div>
            <div class="c3-blueprint-box" style="min-width:118px;text-align:center;background:#eff6ff;">
              <div style="font-size:12px;font-weight:900;color:#1e3a8a;">C³ SERIES</div>
              <div style="font-size:20px;font-weight:900;color:#1e3a8a;line-height:1.1;">${rec.c3Number}</div>
              <div style="font-size:12px;font-weight:900;color:#b48228;">Studio PxG</div>
            </div>
          </div>

          <div class="c3-profile-mid-grid">
            <div class="c3-blueprint-box">
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">階級 / GRADE</div>
                <div style="font-size:12px;font-weight:900;">${rec.gradeStage}</div>
              </div>
              <hr style="border:none;border-top:1px dashed #93c5fd;margin:4px 0;" />
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">初出 / ORIGIN</div>
                <div style="font-size:12px;font-weight:900;">${rec.activationDate}</div>
              </div>
              <hr style="border:none;border-top:1px dashed #93c5fd;margin:4px 0;" />
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">身長 / SPEC</div>
                <div style="font-size:12px;font-weight:900;">${rec.heightSpec}</div>
              </div>
            </div>

            <div class="c3-blueprint-center-fig">
              <img src="${rec.artUrl}" alt="${rec.nameEn} Blueprint" />
            </div>

            <div class="c3-blueprint-box">
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">戦力 / METRICS</div>
                <div style="font-size:12px;font-weight:900;">${rec.threeMetrics}</div>
              </div>
              <hr style="border:none;border-top:1px dashed #93c5fd;margin:4px 0;" />
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">核心 / CORE</div>
                <div style="font-size:12px;font-weight:900;">${rec.bloodCoreType}</div>
              </div>
              <hr style="border:none;border-top:1px dashed #93c5fd;margin:4px 0;" />
              <div>
                <div style="font-size:12px;color:#64748b;font-weight:800;">星座 / ZODIAC</div>
                <div style="font-size:12px;font-weight:900;">${rec.constellationArchetype}</div>
              </div>
            </div>
          </div>

          <div class="c3-blueprint-box" style="background:#eff6ff;">
            <div style="font-size:12px;font-weight:900;color:#b48228;">C³ LORE CHRONICLE // 聖典伝承録</div>
            <div style="font-size:12px;font-weight:700;color:#1e3a8a;line-height:1.35;margin-top:2px;">${rec.loreStory}</div>
          </div>

          <!-- OFFICIAL STANDARD & PREMIUM FOIL VARIATIONS METADATA TABLE -->
          <div class="c3-variations-grid">
            <div class="c3-var-card">
              <div class="c3-var-hdr">STANDARD EDITION METADATA</div>
              <table class="c3-var-table">
                <tr><td class="c3-k">original title</td><td class="c3-v">${std.originalTitle}</td></tr>
                <tr><td class="c3-k">card game</td><td class="c3-v">${std.cardGame}</td></tr>
                <tr><td class="c3-k">version</td><td class="c3-v">${std.version}</td></tr>
                <tr><td class="c3-k">original version</td><td class="c3-v">${std.originalVersion}</td></tr>
                <tr><td class="c3-k">card number</td><td class="c3-v">${std.cardNumber}</td></tr>
                <tr><td class="c3-k">rarity</td><td class="c3-v">${std.rarity}</td></tr>
              </table>
            </div>

            <div class="c3-var-card c3-var-premium">
              <div class="c3-var-hdr">VARIATIONS METADATA (PREMIUM FOIL)</div>
              <table class="c3-var-table">
                <tr><td class="c3-k">original title</td><td class="c3-v">${prm.originalTitle}</td></tr>
                <tr><td class="c3-k">card game</td><td class="c3-v">${prm.cardGame}</td></tr>
                <tr><td class="c3-k">version</td><td class="c3-v">${prm.version}</td></tr>
                <tr><td class="c3-k">original version</td><td class="c3-v">${prm.originalVersion}</td></tr>
                <tr><td class="c3-k">card number</td><td class="c3-v">${prm.cardNumber}</td></tr>
                <tr><td class="c3-k">rarity</td><td class="c3-v">${prm.rarity}</td></tr>
                <tr><td class="c3-k">spec</td><td class="c3-v">${prm.spec}</td></tr>
              </table>
            </div>
          </div>

          <div style="font-size:12px;font-weight:900;color:#1e3a8a;text-align:center;">
            C3-${std.cardNumber.replace(/\s+/g, "-")} · [CARDCRAFT COLLECTABLES C³] · © 2026 Studio PxG
          </div>
        </div>
      </div>
    `;
  }

  function renderC3ModalContents() {
    populateAll141C3Records();
    if (typeof document === "undefined") return;
    const bodyEl = document.getElementById("c3-collectables-modal-body");
    if (!bodyEl) return;

    const featuredList = [
      { id: "ev_01_base", label: "Rosa BP05-110 SR (進化前)" },
      { id: "ev_01_evo", label: "Rosa BP05-111 UR (進化後)" },
      { id: "plugin_01_tcg_creative_designer", label: "Grand Arcanist CF01-001 SR" },
      { id: "h_archangel", label: "Solar Archangel BP05-010 SR" },
      { id: "pxg_s01", label: "Astra Striker BP05-077 SR" },
      { id: "ev_03_base", label: "Celeste BP05-114 SR" },
      { id: "ev_04_base", label: "Lumina BP05-116 SR" },
      { id: "ev_05_base", label: "Aurelia BP05-118 SR" },
      { id: "plugin_02_parallel_swarm_orchestrator", label: "Swarm Orchestrator CF01-002 SR" },
      { id: "plugin_03_jev_system_one", label: "Jev Arbiter CF01-003 SR" }
    ];

    const quickBtnsHtml = featuredList
      .map((item) => {
        const active = state.selectedCardId === item.id;
        return (
          `<button onclick="window.CardFrontCollectablesC3.selectC3Card('${item.id}')" ` +
          `style="background:${active ? "linear-gradient(135deg,#0284c7,#1d4ed8)" : "#0f172a"};border:1.5px solid ${active ? "#FFB800" : "#334155"};color:#fff;font-size:12px;font-weight:800;padding:5px 10px;border-radius:6px;cursor:pointer;">` +
          `${item.label}</button>`
        );
      })
      .join("");

    const allIds = Object.keys(c3RegistryByCardId);
    const selectOptionsHtml = allIds
      .map((cid) => {
        const r = c3RegistryByCardId[cid];
        const sel = cid === state.selectedCardId ? " selected" : "";
        return `<option value="${cid}"${sel}>${r.c3Number} · ${r.nameEn} (${r.standardEdition.cardNumber} / ${r.premiumVariation.cardNumber})</option>`;
      })
      .join("");

    const isFoil = state.activeVariation === "PREMIUM_FOIL";

    bodyEl.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(15,23,42,0.92);border:1.5px solid #FFB800;border-radius:8px;padding:8px 12px;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span style="font-size:12px;font-weight:900;color:#FFB800;">SELECT PLAYABLE CARD (${allIds.length} C³ ARCHIVES):</span>
          <select onchange="window.CardFrontCollectablesC3.selectC3Card(this.value)" style="background:#090d16;color:#f8fafc;border:1px solid #38bdf8;border-radius:6px;padding:4px 8px;font-size:12px;font-weight:800;">
            ${selectOptionsHtml}
          </select>
        </div>
        <div style="display:flex;gap:6px;">
          <button onclick="window.CardFrontCollectablesC3.setVariationMode('STANDARD')" style="background:${!isFoil ? "#1e3a8a" : "#0f172a"};border:1.5px solid ${!isFoil ? "#38bdf8" : "#475569"};color:#fff;font-size:12px;font-weight:900;padding:5px 10px;border-radius:6px;cursor:pointer;">
            Standard Edition (SR/UR)
          </button>
          <button onclick="window.CardFrontCollectablesC3.setVariationMode('PREMIUM_FOIL')" style="background:${isFoil ? "linear-gradient(135deg,#b48228,#d97706)" : "#0f172a"};border:1.5px solid #FFB800;color:#fff;font-size:12px;font-weight:900;padding:5px 10px;border-radius:6px;cursor:pointer;">
            Premium Variation · Spec: Foil
          </button>
        </div>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;">${quickBtnsHtml}</div>
      ${renderDualBromideHtml(state.selectedCardId, state.activeVariation)}
    `;
  }

  function selectC3Card(cardId) {
    state.selectedCardId = cardId || "ev_01_base";
    renderC3ModalContents();
    return getCardC3Record(state.selectedCardId);
  }

  function setVariationMode(mode) {
    if (mode === 0 || mode === "STANDARD") {
      state.activeVariation = "STANDARD";
      state.variationIdx = 0;
    } else {
      state.activeVariation = "PREMIUM_FOIL";
      state.variationIdx = 1;
    }
    renderC3ModalContents();
    return state.activeVariation;
  }

  function openC3CollectablesModal(cardId = "ev_01_base", variationMode = "PREMIUM_FOIL") {
    ensureC3StylesAndModal();
    populateAll141C3Records();
    if (cardId) state.selectedCardId = cardId;
    if (variationMode === 0 || variationMode === "STANDARD") {
      state.activeVariation = "STANDARD";
      state.variationIdx = 0;
    } else if (variationMode === 1 || variationMode === "PREMIUM_FOIL") {
      state.activeVariation = "PREMIUM_FOIL";
      state.variationIdx = 1;
    }
    renderC3ModalContents();
    if (typeof document !== "undefined") {
      const modal = document.getElementById("c3-collectables-modal");
      if (modal) modal.classList.add("open");
    }
    return true;
  }

  function closeC3CollectablesModal() {
    if (typeof document !== "undefined") {
      const modal = document.getElementById("c3-collectables-modal");
      if (modal) modal.classList.remove("open");
    }
    return true;
  }

  function resolveCardIdOrName(cardIdOrName) {
    populateAll141C3Records();
    const qRaw = String(cardIdOrName || "").trim();
    if (!qRaw) return "ev_01_base";

    // Direct match by card_id
    if (c3RegistryByCardId[qRaw]) {
      return qRaw;
    }

    const qLower = qRaw.toLowerCase();
    const qNorm = qLower.replace(/[^a-z0-9\u3040-\u30ff\u4e00-\u9faf]+/g, " ").trim();

    // Exact case-insensitive match on card_id, character_name, nameEn, or original_title
    for (let i = 0; i < state.catalog.length; i++) {
      const entry = state.catalog[i];
      if (
        String(entry.card_id || "").toLowerCase() === qLower ||
        String(entry.character_name || "").toLowerCase() === qLower ||
        String(entry.nameEn || "").toLowerCase() === qLower ||
        String(entry.original_title || "").toLowerCase() === qLower
      ) {
        return entry.card_id;
      }
    }

    // Substring or token match against catalog
    for (let i = 0; i < state.catalog.length; i++) {
      const entry = state.catalog[i];
      const hay = [
        entry.card_id,
        entry.character_name,
        entry.nameEn,
        entry.original_title
      ]
        .join(" ")
        .toLowerCase();
      if (hay.includes(qLower) || (qNorm && hay.includes(qNorm))) {
        return entry.card_id;
      }
    }

    return c3RegistryByCardId[qRaw] ? qRaw : "ev_01_base";
  }

  function openCardById(cardIdOrName, variationIdx) {
    const resolvedId = resolveCardIdOrName(cardIdOrName);
    let varMode = state.activeVariation;
    if (variationIdx === 0 || variationIdx === "STANDARD") {
      varMode = "STANDARD";
    } else if (variationIdx === 1 || variationIdx === "PREMIUM_FOIL") {
      varMode = "PREMIUM_FOIL";
    }
    openC3CollectablesModal(resolvedId, varMode);
    return getCardC3Record(resolvedId);
  }

  function extractCardIdentifierFromElement(cardEl) {
    if (!cardEl) return null;
    const directId =
      cardEl.getAttribute("data-card-id") ||
      cardEl.getAttribute("data-c3-card-id") ||
      (cardEl.dataset && (cardEl.dataset.cardId || cardEl.dataset.c3CardId));
    if (directId) return directId;

    const childWithId = cardEl.querySelector("[data-card-id], [data-c3-card-id]");
    if (childWithId) {
      return (
        childWithId.getAttribute("data-card-id") ||
        childWithId.getAttribute("data-c3-card-id")
      );
    }

    const nameRibbon = cardEl.querySelector(
      ".slot-name-ribbon, .card-name, .hand-card-name, [data-card-name]"
    );
    if (nameRibbon && nameRibbon.textContent && nameRibbon.textContent.trim()) {
      return nameRibbon.textContent.trim();
    }

    const artImg = cardEl.querySelector("img.slot-art, img[alt]");
    if (artImg) {
      const altText = artImg.getAttribute("alt");
      if (altText && altText.trim()) return altText.trim();
    }

    return null;
  }

  let contextHooksBound = false;

  function bindCardInspectContextHandlers() {
    if (contextHooksBound || typeof document === "undefined") return;
    contextHooksBound = true;

    const selector = ".hand-card, .board-card, .hand-card-wrap, .board-slot, .card-3d-unit";

    document.addEventListener("contextmenu", (event) => {
      const targetEl =
        event.target && typeof event.target.closest === "function"
          ? event.target.closest(selector)
          : null;
      if (!targetEl) return;
      const cardIdOrName = extractCardIdentifierFromElement(targetEl);
      if (!cardIdOrName) return;
      event.preventDefault();
      openCardById(cardIdOrName, 1);
    });

    document.addEventListener("click", (event) => {
      if (!event.altKey) return;
      const targetEl =
        event.target && typeof event.target.closest === "function"
          ? event.target.closest(selector)
          : null;
      if (!targetEl) return;
      const cardIdOrName = extractCardIdentifierFromElement(targetEl);
      if (!cardIdOrName) return;
      event.preventDefault();
      event.stopPropagation();
      openCardById(cardIdOrName, 1);
    });
  }

  function mount() {
    ensureC3StylesAndModal();
    populateAll141C3Records();
    loadCatalog();
    bindCardInspectContextHandlers();

    const drawer =
      typeof document !== "undefined" ? document.getElementById("dev-camera-drawer") : null;
    if (drawer && !document.getElementById("drawer-c3-collectables-btn")) {
      const btn = document.createElement("button");
      btn.id = "drawer-c3-collectables-btn";
      btn.type = "button";
      btn.title =
        "Open CardCraftCollectables (C³) Dual-Side Character Bromide, Lore & Variations Vault";
      btn.style.cssText =
        "background:linear-gradient(135deg,#0f766e,#1e3a8a);border-color:#FFB800;color:#fff;font-size:12px;padding:3px 8px;";
      btn.innerHTML = `${icon("booster_reliquary", 13, "margin-right:4px;")}C³ Collectables`;
      btn.onclick = () => openC3CollectablesModal(state.selectedCardId, "PREMIUM_FOIL");
      drawer.appendChild(btn);
    }
    return true;
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      window.addEventListener("DOMContentLoaded", mount);
    } else {
      setTimeout(mount, 60);
    }
  }

  const api = {
    VERSION: "2.0.0",
    STUDIO_SIGNATURE: "Studio PxG",
    SERIES_NAME: "CardCraftCollectables C³",
    FEATURED_CARDS,
    C3_FEATURED_OVERRIDES,
    state,
    mount,
    loadCatalog,
    getRegistry: () => {
      populateAll141C3Records();
      return c3RegistryByCardId;
    },
    getCardC3Record,
    renderDualBromideHtml,
    selectC3Card,
    setVariationMode,
    openCardById,
    openModal: openC3CollectablesModal,
    closeModal: closeC3CollectablesModal,
    openC3CollectablesModal,
    closeC3CollectablesModal
  };

  globalScope.CardFrontCollectablesC3 = api;
  globalScope.openC3CollectablesModal = openC3CollectablesModal;
  globalScope.closeC3CollectablesModal = closeC3CollectablesModal;
})(typeof window !== "undefined" ? window : globalThis);
