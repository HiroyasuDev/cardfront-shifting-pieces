/**
 * ============================================================================
 * CARDFRONT: CRADLE OF ECHOES -- TRACK B MODULE
 * Live In-Game 3D Polyhedral Dice Renderer (Replacing Flat 2D Dice),
 * 4-Layer 2.5D/3D Extruded Parallax Card Slabs, & Unique Attached
 * Final Fantasy Tactics Advance (FFTA) 24x24 Pixel-Chibi Unit Pop-Up Engine
 * ============================================================================
 * File: WebPlayable/modules/dice3d_and_ffta_chibi_units.js
 * Global API: window.CardFrontDice3DAndChibiUnits
 *
 * Strict Compliance:
 * - ZERO living artists' names (zeroLivingArtistNames: true)
 * - ZERO raw Unicode emojis in DOM text, labels, or buttons (zeroRawUnicodeEmojis: true)
 * - Self-mounting on DOMContentLoaded / load + hooks into renderAll() & build3DCardHTML()
 * ============================================================================
 */
(function (globalScope) {
  "use strict";

  // ==========================================================================
  // 1. 12 POLYHEDRAL 3D DICE MODELS & FACE ROTATION MATRICES (D6 & D8)
  // ==========================================================================
  const DICE_3D_FACE_ROTATIONS = {
    1: { rx: -16, ry: 16, rz: 0 },
    2: { rx: 16, ry: 196, rz: 0 },
    3: { rx: -16, ry: -74, rz: 0 },
    4: { rx: -16, ry: 74, rz: 0 },
    5: { rx: -76, ry: 14, rz: 0 },
    6: { rx: 76, ry: 14, rz: 0 }
  };

  // Standard opposite-face sum = 7 pip layout on a 3x3 face grid (indices 0..8)
  const D6_PIP_PATTERNS = {
    1: [4],
    2: [0, 8],
    3: [0, 4, 8],
    4: [0, 2, 6, 8],
    5: [0, 2, 4, 6, 8],
    6: [0, 2, 3, 5, 6, 8]
  };

  const DICE_3D_MODELS_12 = [
    {
      id: "dice3d_01_d6_astralsapphire_f1",
      name: "Astral Sapphire Magicite D6 (Pip 1)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 1,
      primaryHex: "#00E5FF",
      bevelHex: "#FFB800",
      coreHex: "#0B192C",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_1.png"
    },
    {
      id: "dice3d_02_d6_astralsapphire_f2",
      name: "Astral Sapphire Magicite D6 (Pip 2)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 2,
      primaryHex: "#00E5FF",
      bevelHex: "#FFB800",
      coreHex: "#0B192C",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_2.png"
    },
    {
      id: "dice3d_03_d6_astralsapphire_f3",
      name: "Astral Sapphire Magicite D6 (Pip 3)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 3,
      primaryHex: "#00E5FF",
      bevelHex: "#FFB800",
      coreHex: "#0B192C",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_3.png"
    },
    {
      id: "dice3d_04_d6_lawgold_surge_f4",
      name: "Law-Gold Surge Magicite D6 (Pip 4 | +1 Boost)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 4,
      primaryHex: "#FFB800",
      bevelHex: "#FEF08A",
      coreHex: "#3F2305",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_4.png"
    },
    {
      id: "dice3d_05_d6_lawgold_surge_f5",
      name: "Law-Gold Surge Magicite D6 (Pip 5 | +1 Boost)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 5,
      primaryHex: "#FFB800",
      bevelHex: "#FEF08A",
      coreHex: "#3F2305",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_5.png"
    },
    {
      id: "dice3d_06_d6_sovereign_apex_f6",
      name: "Sovereign Apex Magicite D6 (Pip 6 | Overdrive)",
      polyhedron: "D6_BEVELED_CUBE",
      faces: 6,
      defaultFaceValue: 6,
      primaryHex: "#FFB800",
      bevelHex: "#00E5FF",
      coreHex: "#422006",
      texturePath: "./GeneratedArt/Dice3D/dice3d_d6_face_6.png"
    },
    {
      id: "dice3d_07_d8_aether_sapphire",
      name: "Aether Sapphire Octahedron (D8 Prism)",
      polyhedron: "D8_OCTAHEDRON",
      faces: 8,
      defaultFaceValue: 8,
      primaryHex: "#00E5FF",
      bevelHex: "#FFE082",
      coreHex: "#0B192C",
      texturePath: "./GeneratedArt/Dice3D/dice3d_aether_sapphire_d8.png"
    },
    {
      id: "dice3d_08_d8_crimson_obsidian",
      name: "Crimson Obsidian Octahedron (D8 Prism)",
      polyhedron: "D8_OCTAHEDRON",
      faces: 8,
      defaultFaceValue: 8,
      primaryHex: "#FF2E54",
      bevelHex: "#FFB800",
      coreHex: "#280714",
      texturePath: "./GeneratedArt/Dice3D/dice3d_crimson_obsidian_d8.png"
    },
    {
      id: "dice3d_09_d12_sovereign_gold",
      name: "Sovereign Law-Gold Dodecahedron (D12 Relic)",
      polyhedron: "D12_DODECAHEDRON",
      faces: 12,
      defaultFaceValue: 12,
      primaryHex: "#FFB800",
      bevelHex: "#2EE6D3",
      coreHex: "#2E1A05",
      texturePath: "./GeneratedArt/Dice3D/dice3d_sovereign_gold_d12.png"
    },
    {
      id: "dice3d_10_d20_kubrart_violet",
      name: "Kubrart Tarot Violet Icosahedron (D20 Relic)",
      polyhedron: "D20_ICOSAHEDRON",
      faces: 20,
      defaultFaceValue: 20,
      primaryHex: "#A855F7",
      bevelHex: "#FFE082",
      coreHex: "#1E1035",
      texturePath: "./GeneratedArt/Dice3D/dice3d_kubrart_violet_d20.png"
    },
    {
      id: "dice3d_11_tumble_strip_blue",
      name: "Astral Blue Tumbling Polyhedral Strip",
      polyhedron: "D6_TUMBLE_STRIP",
      faces: 6,
      defaultFaceValue: 6,
      primaryHex: "#00E5FF",
      bevelHex: "#38BDF8",
      coreHex: "#071E34",
      texturePath: "./GeneratedArt/Dice3D/dice3d_tumble_strip_blue.png"
    },
    {
      id: "dice3d_12_tumble_strip_red",
      name: "Crimson Boss Tumbling Polyhedral Strip",
      polyhedron: "D6_TUMBLE_STRIP",
      faces: 6,
      defaultFaceValue: 6,
      primaryHex: "#FF2E54",
      bevelHex: "#F97316",
      coreHex: "#2C1206",
      texturePath: "./GeneratedArt/Dice3D/dice3d_tumble_strip_red.png"
    }
  ];

  // ==========================================================================
  // 2. 24 FFTA ISOMETRIC 2.5-HEAD PIXEL-CHIBI UNIT ARCHETYPES
  // ==========================================================================
  const FFTA_PIXEL_CHIBI_ROSTER_24 = [
    {
      archetypeId: "chibi_01_rosalia_mech_wing_maiden",
      jobTitle: "Rosalia Mech-Wing Maiden",
      faction: "Aether",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "astral_lance",
      headgearType: "wing_tiara",
      wingType: "feathered_wings",
      primaryHex: "#10B981",
      secondaryHex: "#FACC15",
      armorHex: "#FFFFFF",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_01_rosalia_mech_wing_maiden.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_01_rosalia_mech_wing_maiden_sheet.png"
    },
    {
      archetypeId: "chibi_02_celestia_clockwork_valkyrie",
      jobTitle: "Celestia Clockwork Valkyrie",
      faction: "Valkyria",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "chrono_rapier",
      headgearType: "wing_tiara",
      wingType: "mecha_wings",
      primaryHex: "#00E5FF",
      secondaryHex: "#FFB800",
      armorHex: "#E0F2FE",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_02_celestia_clockwork_valkyrie.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_02_celestia_clockwork_valkyrie_sheet.png"
    },
    {
      archetypeId: "chibi_03_lyra_harmony_automata",
      jobTitle: "Lyra Harmony Automata",
      faction: "Aether",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "grimoire_staff",
      headgearType: "halo_crown",
      wingType: "astral_halo",
      primaryHex: "#A855F7",
      secondaryHex: "#FFE082",
      armorHex: "#DDD6FE",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_03_lyra_harmony_automata.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_03_lyra_harmony_automata_sheet.png"
    },
    {
      archetypeId: "chibi_04_ignia_blaze_pinion",
      jobTitle: "Ignia Blaze-Pinion Seraph",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "broadsword",
      headgearType: "halo_crown",
      wingType: "feathered_wings",
      primaryHex: "#F97316",
      secondaryHex: "#FACC15",
      armorHex: "#FEF08A",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_04_ignia_blaze_pinion.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_04_ignia_blaze_pinion_sheet.png"
    },
    {
      archetypeId: "chibi_05_nocturna_eclipse_saint",
      jobTitle: "Nocturna Eclipse Saint",
      faction: "Abyss",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "scythe",
      headgearType: "horned_crest",
      wingType: "obsidian_wings",
      primaryHex: "#C026D3",
      secondaryHex: "#FF2E54",
      armorHex: "#F5D0FE",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_05_nocturna_eclipse_saint.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_05_nocturna_eclipse_saint_sheet.png"
    },
    {
      archetypeId: "chibi_06_archangel_paladin",
      jobTitle: "Archangel Aegis Paladin",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "broadsword",
      headgearType: "plumed_helm",
      wingType: "feathered_wings",
      primaryHex: "#FFB800",
      secondaryHex: "#00E5FF",
      armorHex: "#E2E8F0",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_06_archangel_paladin.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_06_archangel_paladin_sheet.png"
    },
    {
      archetypeId: "chibi_07_eclipse_assassin",
      jobTitle: "Eclipse Shadow Assassin",
      faction: "Abyss",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "twin_kunai",
      headgearType: "spiky_bandana",
      wingType: "scarf_ribbons",
      primaryHex: "#FF2E54",
      secondaryHex: "#A855F7",
      armorHex: "#31102F",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_07_eclipse_assassin.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_07_eclipse_assassin_sheet.png"
    },
    {
      archetypeId: "chibi_08_kubrart_eclipse_sovereign",
      jobTitle: "Kubrart Eclipse Sovereign",
      faction: "Aether",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "katana_slash",
      headgearType: "samurai_kabuto",
      wingType: "tactical_cape",
      primaryHex: "#A855F7",
      secondaryHex: "#FFB800",
      armorHex: "#F3E8FF",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_08_kubrart_eclipse_sovereign.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_08_kubrart_eclipse_sovereign_sheet.png"
    },
    {
      archetypeId: "chibi_09_sumi_ronin_blademaster",
      jobTitle: "Sumi-Ink Ronin Blademaster",
      faction: "Valkyria",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "katana_slash",
      headgearType: "spiky_bandana",
      wingType: "scarf_ribbons",
      primaryHex: "#00E5FF",
      secondaryHex: "#FF2E54",
      armorHex: "#CBD5E1",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_09_sumi_ronin_blademaster.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_09_sumi_ronin_blademaster_sheet.png"
    },
    {
      archetypeId: "chibi_10_astra_hyper_striker",
      jobTitle: "Astra Hyper-Striker",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "chakram",
      headgearType: "cyber_visor",
      wingType: "mecha_wings",
      primaryHex: "#FF2E54",
      secondaryHex: "#FFB800",
      armorHex: "#FEF08A",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_10_astra_hyper_striker.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_10_astra_hyper_striker_sheet.png"
    },
    {
      archetypeId: "chibi_11_solaris_obari_mecha",
      jobTitle: "Solaris Brave Halberd Mecha",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "gun_halberd",
      headgearType: "plumed_helm",
      wingType: "mecha_wings",
      primaryHex: "#FFB800",
      secondaryHex: "#00E5FF",
      armorHex: "#F8FAFC",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_11_solaris_obari_mecha.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_11_solaris_obari_mecha_sheet.png"
    },
    {
      archetypeId: "chibi_12_judge_law_arbiter",
      jobTitle: "Sovereign Okitsu Law-Arbiter",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "judge_gavel",
      headgearType: "judge_mitre",
      wingType: "tactical_cape",
      primaryHex: "#FFB800",
      secondaryHex: "#2EE6D3",
      armorHex: "#FEF9C3",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_12_judge_law_arbiter.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_12_judge_law_arbiter_sheet.png"
    },
    {
      archetypeId: "chibi_13_time_mage_chrono",
      jobTitle: "Chronos Gear Time-Mage",
      faction: "Chronos",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "chrono_rapier",
      headgearType: "wizard_hat",
      wingType: "astral_halo",
      primaryHex: "#F97316",
      secondaryHex: "#00E5FF",
      armorHex: "#FDE68A",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_13_time_mage_chrono.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_13_time_mage_chrono_sheet.png"
    },
    {
      archetypeId: "chibi_14_white_monk_brawler",
      jobTitle: "Sanctuary White-Monk Brawler",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "chakram",
      headgearType: "spiky_bandana",
      wingType: "scarf_ribbons",
      primaryHex: "#10B981",
      secondaryHex: "#FFB800",
      armorHex: "#ECFDF5",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_14_white_monk_brawler.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_14_white_monk_brawler_sheet.png"
    },
    {
      archetypeId: "chibi_15_dragoon_sky_lancer",
      jobTitle: "Valkyria Sky-Lance Dragoon",
      faction: "Valkyria",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "astral_lance",
      headgearType: "wing_tiara",
      wingType: "mecha_wings",
      primaryHex: "#00E5FF",
      secondaryHex: "#FFB800",
      armorHex: "#E0F2FE",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_15_dragoon_sky_lancer.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_15_dragoon_sky_lancer_sheet.png"
    },
    {
      archetypeId: "chibi_16_black_mage_pyro",
      jobTitle: "Pyro Spire Black-Mage",
      faction: "Chronos",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "grimoire_staff",
      headgearType: "wizard_hat",
      wingType: "astral_halo",
      primaryHex: "#F97316",
      secondaryHex: "#FACC15",
      armorHex: "#FFEDD5",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_16_black_mage_pyro.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_16_black_mage_pyro_sheet.png"
    },
    {
      archetypeId: "chibi_17_gunner_moogle_machinist",
      jobTitle: "Skystone Machinist Gunner",
      faction: "Chronos",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "gun_halberd",
      headgearType: "cyber_visor",
      wingType: "mecha_wings",
      primaryHex: "#F97316",
      secondaryHex: "#00E5FF",
      armorHex: "#CBD5E1",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_17_gunner_moogle_machinist.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_17_gunner_moogle_machinist_sheet.png"
    },
    {
      archetypeId: "chibi_18_illusionist_star_seer",
      jobTitle: "Astrolabe Star-Seer Illusionist",
      faction: "Aether",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "grimoire_staff",
      headgearType: "halo_crown",
      wingType: "astral_halo",
      primaryHex: "#A855F7",
      secondaryHex: "#2EE6D3",
      armorHex: "#EDE9FE",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_18_illusionist_star_seer.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_18_illusionist_star_seer_sheet.png"
    },
    {
      archetypeId: "chibi_19_fencer_red_mage",
      jobTitle: "Crimson Duelist Red-Fencer",
      faction: "Valkyria",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "chrono_rapier",
      headgearType: "plumed_helm",
      wingType: "tactical_cape",
      primaryHex: "#FF2E54",
      secondaryHex: "#00E5FF",
      armorHex: "#FFE4E6",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_19_fencer_red_mage.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_19_fencer_red_mage_sheet.png"
    },
    {
      archetypeId: "chibi_20_summoner_horn_conduit",
      jobTitle: "Summoner Horn-Crest Conduit",
      faction: "Aether",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "grimoire_staff",
      headgearType: "horned_crest",
      wingType: "feathered_wings",
      primaryHex: "#2EE6D3",
      secondaryHex: "#FFB800",
      armorHex: "#CCFBF1",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_20_summoner_horn_conduit.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_20_summoner_horn_conduit_sheet.png"
    },
    {
      archetypeId: "chibi_21_void_golem_construct",
      jobTitle: "Obsidian Colossus Construct",
      faction: "Abyss",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "shield_blade",
      headgearType: "cyber_visor",
      wingType: "obsidian_wings",
      primaryHex: "#A855F7",
      secondaryHex: "#FF2E54",
      armorHex: "#94A3B8",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_21_void_golem_construct.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_21_void_golem_construct_sheet.png"
    },
    {
      archetypeId: "chibi_22_valkyrie_aegis_shield",
      jobTitle: "Valkyrie Aegis Shield-Maiden",
      faction: "Valkyria",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "shield_blade",
      headgearType: "wing_tiara",
      wingType: "feathered_wings",
      primaryHex: "#00E5FF",
      secondaryHex: "#FFB800",
      armorHex: "#F8FAFC",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_22_valkyrie_aegis_shield.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_22_valkyrie_aegis_shield_sheet.png"
    },
    {
      archetypeId: "chibi_23_necromancer_lich_lord",
      jobTitle: "Necro-Lich Grimoire Lord",
      faction: "Abyss",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "scythe",
      headgearType: "hooded_cloak",
      wingType: "obsidian_wings",
      primaryHex: "#FF2E54",
      secondaryHex: "#2EE6D3",
      armorHex: "#475569",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_23_necromancer_lich_lord.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_23_necromancer_lich_lord_sheet.png"
    },
    {
      archetypeId: "chibi_24_omega_sovereign_captain",
      jobTitle: "Omega Sovereign Collective Captain",
      faction: "Solaris",
      headRatio: "2.5-Head Isometric Chibi",
      weaponType: "broadsword",
      headgearType: "halo_crown",
      wingType: "feathered_wings",
      primaryHex: "#FFB800",
      secondaryHex: "#00E5FF",
      armorHex: "#FEF9C3",
      spritePath: "./GeneratedArt/FFAChibiUnits/chibi_24_omega_sovereign_captain.png",
      sheetPath: "./GeneratedArt/FFAChibiUnits/chibi_24_omega_sovereign_captain_sheet.png"
    }
  ];

  // ==========================================================================
  // 3. COMPLETE 141 CANONICAL CARD IDS -> UNIQUE FFTA CHIBI BINDING TABLE
  //    (60 Set 1 + 20 Set 2 Kubrart + 37 Sovereign Agent + 8 Studio PxG
  //     + 6 10-Year Saga + 10 Evolve Mech-Wing Maidens = 141 Cards)
  // ==========================================================================
  const BASE_16_ROSTER_IDS = [
    "h_archangel",
    "h_phoenix",
    "h_oracle",
    "h_chronos",
    "h_seraph",
    "h_kai",
    "h_valkyrie",
    "h_arbiter",
    "e_eclipse",
    "e_archon",
    "e_inferno",
    "e_reaper",
    "e_titan",
    "e_colossus",
    "e_cryo",
    "e_shinobi"
  ];

  const SET1_FACTIONS_5 = ["Aether", "Solaris", "Valkyria", "Chronos", "Abyss"];

  const SET2_KUBRART_20_IDS = [
    "set2_k01", "set2_k02", "set2_k03", "set2_k04", "set2_k05",
    "set2_k06", "set2_k07", "set2_k08", "set2_k09", "set2_k10",
    "set2_k11", "set2_k12", "set2_k13", "set2_k14", "set2_k15",
    "set2_k16", "set2_k17", "set2_k18", "set2_k19", "set2_k20"
  ];

  const SOVEREIGN_AGENT_37_IDS = [
    "plugin_01_tcg_creative_designer",
    "plugin_02_parallel_swarm_orchestrator",
    "plugin_03_jev_system_one",
    "plugin_04_mlx_apple_silicon",
    "skill_01_master_router",
    "skill_02_tactical_illustrator_library",
    "skill_03_create_game_assets",
    "skill_04_card_game_genre",
    "skill_05_game_feel_juice",
    "skill_06_game_ui_ux",
    "skill_07_ai_utility_behavior",
    "skill_08_shader_camera_audio",
    "skill_09_save_procgen_dialogue",
    "skill_10_multi_engine_codex",
    "skill_11_decompilation_hi3d_rea",
    "skill_12_workflows_and_agent_core",
    "tool_01_invoke_subagent",
    "tool_02_define_subagent",
    "tool_03_manage_subagents",
    "tool_04_send_message",
    "tool_05_call_mcp_tool",
    "tool_06_mcp_resources",
    "tool_07_run_command",
    "tool_08_manage_task",
    "tool_09_read_file",
    "tool_10_write_file",
    "tool_11_edit_file",
    "tool_12_search_schedule_ask",
    "mcp_01_jev_system_one",
    "mcp_02_jev_py_verifier",
    "mcp_03_mlx_apple_silicon",
    "mcp_04_prime_rlm_swarm",
    "mcp_05_sequential_thinking",
    "mcp_06_knowledge_graph_mem",
    "mcp_07_git_time_chronicle",
    "mcp_08_filesystem_and_fetch",
    "mcp_09_tcg_creative_studio"
  ];

  const STUDIO_PXG_8_IDS = [
    "pxg_s01", "pxg_s02", "pxg_s03", "pxg_s04",
    "pxg_s05", "pxg_s06", "pxg_s07", "pxg_s08"
  ];

  const SAGA_10YEAR_6_IDS = [
    "saga_y01", "saga_y02", "saga_y04", "saga_y06", "saga_y08", "saga_y10"
  ];

  const EVOLVE_MAIDEN_10_IDS = [
    "ev_01_base", "ev_01_evo",
    "ev_02_base", "ev_02_evo",
    "ev_03_base", "ev_03_evo",
    "ev_04_base", "ev_04_evo",
    "ev_05_base", "ev_05_evo"
  ];

  const WEAPON_VARIATIONS_12 = [
    "broadsword",
    "astral_lance",
    "grimoire_staff",
    "chrono_rapier",
    "twin_kunai",
    "gun_halberd",
    "judge_gavel",
    "katana_slash",
    "scythe",
    "shield_blade",
    "chakram",
    "seraph_bow"
  ];

  const HEADGEAR_VARIATIONS_10 = [
    "plumed_helm",
    "wizard_hat",
    "wing_tiara",
    "halo_crown",
    "horned_crest",
    "cyber_visor",
    "hooded_cloak",
    "samurai_kabuto",
    "judge_mitre",
    "spiky_bandana"
  ];

  const WING_VARIATIONS_6 = [
    "feathered_wings",
    "mecha_wings",
    "tactical_cape",
    "astral_halo",
    "scarf_ribbons",
    "obsidian_wings"
  ];

  const PALETTE_VARIATIONS_8 = [
    { primary: "#00E5FF", secondary: "#FFB800", armor: "#E2E8F0", hair: "#38BDF8", outline: "#081426" },
    { primary: "#FFB800", secondary: "#2EE6D3", armor: "#FEF9C3", hair: "#F59E0B", outline: "#261604" },
    { primary: "#A855F7", secondary: "#FFE082", armor: "#EDE9FE", hair: "#C084FC", outline: "#1B0B2E" },
    { primary: "#F97316", secondary: "#00E5FF", armor: "#FFEDD5", hair: "#FB923C", outline: "#2A1006" },
    { primary: "#FF2E54", secondary: "#C026D3", armor: "#FCE7F3", hair: "#F43F5E", outline: "#280612" },
    { primary: "#10B981", secondary: "#FACC15", armor: "#ECFDF5", hair: "#34D399", outline: "#05241B" },
    { primary: "#2EE6D3", secondary: "#A855F7", armor: "#CCFBF1", hair: "#5EEAD4", outline: "#062224" },
    { primary: "#38BDF8", secondary: "#F43F5E", armor: "#E0F2FE", hair: "#7DD3FC", outline: "#0B1D33" }
  ];

  function hashString32(str) {
    const s = String(str || "h_archangel");
    let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function buildAll141CardBindings() {
    const allCardEntries = [];

    // 1..60: Set 1 (16 base Mk.1 + 44 Mk.2/Mk.3/Mk.4)
    for (let i = 0; i < 60; i++) {
      const baseId = BASE_16_ROSTER_IDS[i % 16];
      const canonicalId = i < 16 ? baseId : ("set1_c" + String(i + 1).padStart(2, "0") + "_" + baseId);
      const aliasId = "set1_c" + String(i + 1).padStart(2, "0") + "_" + baseId;
      allCardEntries.push({
        cardId: canonicalId,
        aliasId: aliasId,
        setGroup: "SET1_60_CATALOG",
        archetypeIndex: i < 16 ? i : ((i * 7 + 3) % 24),
        faction: SET1_FACTIONS_5[i % 5]
      });
    }

    // 61..80: Set 2 Kubrart Manga (20 cards)
    for (let k = 0; k < SET2_KUBRART_20_IDS.length; k++) {
      allCardEntries.push({
        cardId: SET2_KUBRART_20_IDS[k],
        aliasId: SET2_KUBRART_20_IDS[k],
        setGroup: "SET2_KUBRART_20",
        archetypeIndex: (16 + k) % 24,
        faction: SET1_FACTIONS_5[k % 5]
      });
    }

    // 81..117: Sovereign Agent Deck (37 cards)
    for (let a = 0; a < SOVEREIGN_AGENT_37_IDS.length; a++) {
      allCardEntries.push({
        cardId: SOVEREIGN_AGENT_37_IDS[a],
        aliasId: SOVEREIGN_AGENT_37_IDS[a],
        setGroup: "SOVEREIGN_AGENT_37",
        archetypeIndex: (18 + a) % 24,
        faction: SET1_FACTIONS_5[a % 5]
      });
    }

    // 118..125: Studio PxG Strikers (8 cards)
    for (let p = 0; p < STUDIO_PXG_8_IDS.length; p++) {
      allCardEntries.push({
        cardId: STUDIO_PXG_8_IDS[p],
        aliasId: STUDIO_PXG_8_IDS[p],
        setGroup: "STUDIO_PXG_8",
        archetypeIndex: (23 + p) % 24,
        faction: SET1_FACTIONS_5[p % 5]
      });
    }

    // 126..131: 10-Year Saga Heralds (6 cards)
    for (let s = 0; s < SAGA_10YEAR_6_IDS.length; s++) {
      allCardEntries.push({
        cardId: SAGA_10YEAR_6_IDS[s],
        aliasId: SAGA_10YEAR_6_IDS[s],
        setGroup: "SAGA_10YEAR_6",
        archetypeIndex: (22 + s) % 24,
        faction: SET1_FACTIONS_5[s % 5]
      });
    }

    // 132..141: Evolve Mech-Wing Maidens (10 cards)
    for (let e = 0; e < EVOLVE_MAIDEN_10_IDS.length; e++) {
      allCardEntries.push({
        cardId: EVOLVE_MAIDEN_10_IDS[e],
        aliasId: EVOLVE_MAIDEN_10_IDS[e],
        setGroup: "EVOLVE_MECH_WING_10",
        archetypeIndex: 21,
        faction: e % 2 === 1 ? "Solaris" : "Aether"
      });
    }

    const bindingsList = [];
    const bindingsById = {};

    for (let idx = 0; idx < allCardEntries.length; idx++) {
      const entry = allCardEntries[idx];
      const arch = FFTA_PIXEL_CHIBI_ROSTER_24[entry.archetypeIndex % FFTA_PIXEL_CHIBI_ROSTER_24.length];
      const pal = PALETTE_VARIATIONS_8[idx % PALETTE_VARIATIONS_8.length];
      const weapon = idx < 16 ? arch.weaponType : WEAPON_VARIATIONS_12[idx % WEAPON_VARIATIONS_12.length];
      const headgear = idx < 16 ? arch.headgearType : HEADGEAR_VARIATIONS_10[idx % HEADGEAR_VARIATIONS_10.length];
      const wing = idx < 16 ? arch.wingType : WING_VARIATIONS_6[idx % WING_VARIATIONS_6.length];

      const chibiObj = {
        chibiIndex: idx + 1,
        chibiUnitId: "chibi_unit_" + String(idx + 1).padStart(3, "0") + "_" + entry.cardId,
        cardId: entry.cardId,
        aliasId: entry.aliasId,
        setGroup: entry.setGroup,
        archetypeId: arch.archetypeId,
        jobTitle: arch.jobTitle + " #" + String(idx + 1).padStart(3, "0"),
        faction: entry.faction,
        headRatio: "2.5-Head Isometric Pixel-Chibi",
        pixelGridSize: "24x24",
        idleFps: 2.5,
        weaponType: weapon,
        headgearType: headgear,
        wingType: wing,
        primaryHex: pal.primary,
        secondaryHex: pal.secondary,
        armorHex: pal.armor,
        hairHex: pal.hair,
        outlineHex: pal.outline,
        spritePath: arch.spritePath,
        crestMarkSeed: (idx * 37 + 11) % 256
      };

      bindingsList.push(chibiObj);
      bindingsById[entry.cardId] = chibiObj;
      if (entry.aliasId && entry.aliasId !== entry.cardId) {
        bindingsById[entry.aliasId] = chibiObj;
      }
    }

    return {
      list: bindingsList,
      byId: bindingsById
    };
  }

  const BUILT_BINDINGS = buildAll141CardBindings();
  const CARD_TO_CHIBI_BINDINGS_141 = BUILT_BINDINGS.list;
  const CARD_TO_CHIBI_MAP = BUILT_BINDINGS.byId;

  // ==========================================================================
  // 4. DETERMINISTIC CODE-NATIVE 24x24 PIXEL-GRID CHIBI SYNTHESIZER (SVG + URI)
  // ==========================================================================
  const SVG_CHIBI_CACHE = {};

  function getUniqueChibiForCard(cardId) {
    const rawId = String(cardId || "h_archangel").trim();
    if (CARD_TO_CHIBI_MAP[rawId]) {
      return CARD_TO_CHIBI_MAP[rawId];
    }
    // Check prefix match (e.g. set2_k01_gpen_ronin_vanguard -> set2_k01, pxg_s01_... -> pxg_s01)
    const shortMatch = rawId.match(/^(set2_k\d{2}|pxg_s\d{2}|saga_y\d{2}|ev_\d{2}_(?:base|evo)|set1_c\d{2}_[a-z_]+)/);
    if (shortMatch && CARD_TO_CHIBI_MAP[shortMatch[1]]) {
      return CARD_TO_CHIBI_MAP[shortMatch[1]];
    }

    // Deterministic synthesis for any custom/forged card ID
    const h = hashString32(rawId);
    const arch = FFTA_PIXEL_CHIBI_ROSTER_24[h % FFTA_PIXEL_CHIBI_ROSTER_24.length];
    const pal = PALETTE_VARIATIONS_8[(h >>> 4) % PALETTE_VARIATIONS_8.length];
    const synthesized = {
      chibiIndex: 142 + (h % 850),
      chibiUnitId: "chibi_unit_custom_" + rawId.replace(/[^a-zA-Z0-9_]/g, "_"),
      cardId: rawId,
      aliasId: rawId,
      setGroup: "CUSTOM_FORGED_CARD",
      archetypeId: arch.archetypeId,
      jobTitle: arch.jobTitle,
      faction: arch.faction,
      headRatio: "2.5-Head Isometric Pixel-Chibi",
      pixelGridSize: "24x24",
      idleFps: 2.5,
      weaponType: WEAPON_VARIATIONS_12[(h >>> 8) % WEAPON_VARIATIONS_12.length],
      headgearType: HEADGEAR_VARIATIONS_10[(h >>> 12) % HEADGEAR_VARIATIONS_10.length],
      wingType: WING_VARIATIONS_6[(h >>> 16) % WING_VARIATIONS_6.length],
      primaryHex: pal.primary,
      secondaryHex: pal.secondary,
      armorHex: pal.armor,
      hairHex: pal.hair,
      outlineHex: pal.outline,
      spritePath: arch.spritePath,
      crestMarkSeed: h & 255
    };
    CARD_TO_CHIBI_MAP[rawId] = synthesized;
    return synthesized;
  }

  /**
   * Synthesizes a crisp 24x24 pixel-art FFTA 2.5-head isometric chibi SVG
   * with separate Frame 0 (Idle Stance) and Frame 1 (Bounce + Weapon Slash).
   */
  function renderChibi24x24Svg(cardId, frameIdx) {
    const f = frameIdx ? 1 : 0;
    const chibi = getUniqueChibiForCard(cardId);
    const cacheKey = chibi.chibiUnitId + "_f" + f;
    if (SVG_CHIBI_CACHE[cacheKey]) {
      return SVG_CHIBI_CACHE[cacheKey];
    }

    const out = chibi.outlineHex || "#081426";
    const pri = chibi.primaryHex || "#00E5FF";
    const sec = chibi.secondaryHex || "#FFB800";
    const arm = chibi.armorHex || "#F8FAFC";
    const hair = chibi.hairHex || "#38BDF8";
    const skin = "#FDE6C4";
    const eye = "#090D16";
    const dy = f === 1 ? -1 : 0;

    const rects = [];
    function px(x, y, w, h, fill) {
      rects.push('<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + fill + '"/>');
    }

    // Ground isometric tactical shadow ellipse on 24x24 grid
    px(5, 22, 14, 2, "rgba(0,0,0,0.48)");
    px(7, 21, 10, 1, "rgba(255,184,0,0.35)");

    // Back Wing / Cape silhouette (varies by wingType)
    if (chibi.wingType === "feathered_wings" || chibi.wingType === "mecha_wings") {
      const wingCol = chibi.wingType === "mecha_wings" ? pri : arm;
      px(2, 9 + dy, 4, 7, out);
      px(18, 9 + dy, 4, 7, out);
      px(3, 10 + dy, 3, 5, wingCol);
      px(18, 10 + dy, 3, 5, wingCol);
      px(2, 11 + dy, 2, 2, sec);
      px(20, 11 + dy, 2, 2, sec);
    } else if (chibi.wingType === "astral_halo") {
      px(5, 1 + dy, 14, 1, sec);
      px(4, 2 + dy, 1, 3, sec);
      px(19, 2 + dy, 1, 3, sec);
    } else if (chibi.wingType === "scarf_ribbons") {
      px(16, 11 + dy, 6, 2, sec);
      px(18, 13 + dy, 5, 2, pri);
    } else {
      // tactical_cape or obsidian_wings
      px(4, 12 + dy, 16, 7, out);
      px(5, 13 + dy, 14, 5, pri);
    }

    // 2.5-Head Chibi Head & Hair (rows 3..11)
    px(6, 3 + dy, 12, 9, out);
    px(7, 4 + dy, 10, 4, hair);
    px(7, 7 + dy, 10, 4, skin);

    // Chibi Eyes (isometric 3/4 gaze)
    px(8, 8 + dy, 2, 2, eye);
    px(13, 8 + dy, 2, 2, eye);
    px(8, 8 + dy, 1, 1, "#FFFFFF");
    px(13, 8 + dy, 1, 1, "#FFFFFF");

    // Headgear variation (hat/helm/horns/tiara/visor)
    if (chibi.headgearType === "wizard_hat") {
      px(4, 3 + dy, 16, 2, out);
      px(5, 3 + dy, 14, 1, pri);
      px(8, 1 + dy, 8, 2, pri);
      px(10, 0 + dy, 5, 1, sec);
    } else if (chibi.headgearType === "horned_crest" || chibi.headgearType === "samurai_kabuto") {
      px(5, 1 + dy, 2, 3, sec);
      px(17, 1 + dy, 2, 3, sec);
      px(9, 2 + dy, 6, 2, pri);
    } else if (chibi.headgearType === "cyber_visor") {
      px(7, 7 + dy, 10, 2, "#00E5FF");
      px(8, 7 + dy, 8, 1, "#FFFFFF");
    } else if (chibi.headgearType === "halo_crown" || chibi.headgearType === "wing_tiara") {
      px(7, 1 + dy, 10, 2, sec);
      px(11, 0 + dy, 2, 2, pri);
    } else {
      // plumed_helm / judge_mitre / spiky_bandana
      px(6, 2 + dy, 12, 2, pri);
      px(10, 0 + dy, 4, 2, sec);
    }

    // Chibi Torso, Surcoat & Pauldrons (rows 12..17)
    px(6, 12 + dy, 12, 6, out);
    px(7, 12 + dy, 10, 5, arm);
    px(9, 13 + dy, 6, 4, pri);
    px(10, 14 + dy, 4, 2, sec);
    // Unique per-card crest pixel pattern on chest
    if (chibi.crestMarkSeed & 1) {
      px(11, 13 + dy, 2, 2, "#FFFFFF");
    }

    // Tapered Boots & Isometric Stance (rows 18..21)
    px(7, 18, 4, 3, out);
    px(13, 18, 4, 3, out);
    px(8, 18, 2, 2, pri);
    px(14, 18, 2, 2, pri);

    // Right-Hand Tactical Weapon (with Frame 1 Attack Slash Arc!)
    if (chibi.weaponType === "grimoire_staff" || chibi.weaponType === "astral_lance") {
      const wy = f === 1 ? 2 : 4;
      px(20, wy, 2, 16, out);
      px(20, wy + 1, 1, 14, sec);
      px(19, wy, 4, 3, pri);
    } else if (chibi.weaponType === "scythe" || chibi.weaponType === "gun_halberd") {
      const wy = f === 1 ? 2 : 4;
      px(19, wy, 3, 15, out);
      px(20, wy + 1, 1, 13, sec);
      px(15, wy, 7, 2, pri);
    } else if (chibi.weaponType === "judge_gavel") {
      const wy = f === 1 ? 4 : 6;
      px(19, wy + 2, 2, 11, sec);
      px(17, wy, 6, 4, pri);
    } else {
      // broadsword / katana_slash / chrono_rapier / twin_kunai / shield_blade / chakram
      const wy = f === 1 ? 3 : 5;
      px(19, wy, 3, 12, out);
      px(20, wy + 1, 2, 9, "#FFFFFF");
      px(19, wy + 2, 1, 7, pri);
      px(18, wy + 10, 5, 2, sec);
    }

    // Frame 1 Dynamic Pixel-Art Slash Arc
    if (f === 1) {
      px(21, 2, 2, 5, "#FFFFFF");
      px(22, 5, 2, 6, sec);
      px(20, 10, 3, 3, pri);
    }

    const svgStr =
      '<svg class="cf-ffta-pixel-svg" viewBox="0 0 24 24" width="46" height="46" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      rects.join("") +
      "</svg>";

    SVG_CHIBI_CACHE[cacheKey] = svgStr;
    return svgStr;
  }

  function buildChibiUnitBadgeHTML(cardId, owner) {
    const chibi = getUniqueChibiForCard(cardId);
    const svgFrame0 = renderChibi24x24Svg(cardId, 0);
    const svgFrame1 = renderChibi24x24Svg(cardId, 1);
    const sideCls = owner === "ai" ? "cf-chibi-owner-ai" : "cf-chibi-owner-player";
    return (
      '<div class="cf-slab-layer-3-chibi ' + sideCls + '" data-chibi-id="' + chibi.chibiUnitId + '" data-chibi-job="' + chibi.jobTitle + '" title="FFTA Pixel-Chibi Unit: ' + chibi.jobTitle + ' (' + chibi.weaponType + ')">' +
        '<div class="cf-chibi-pedestal-shadow"></div>' +
        '<div class="cf-chibi-sprite-stage">' +
          '<img class="cf-chibi-png-sprite" src="' + chibi.spritePath + '" alt="" draggable="false" onerror="this.style.display=\'none\';" />' +
          '<div class="cf-chibi-frame cf-chibi-frame-0">' + svgFrame0 + '</div>' +
          '<div class="cf-chibi-frame cf-chibi-frame-1">' + svgFrame1 + '</div>' +
        '</div>' +
        '<div class="cf-chibi-slash-fx"></div>' +
      '</div>'
    );
  }

  // ==========================================================================
  // 5. TRUE 3D POLYHEDRAL COLUMN DICE RENDERER (D6 BEVELED CUBE + D8 PRISM)
  // ==========================================================================
  const DICE3D_RUNTIME_STATE = {
    depthMode: "3d_extruded_hd2d",
    polyhedronMode: "D6_AND_D8_HYBRID",
    chibiOverlayEnabled: true,
    rollCount: 0,
    chibiAttackCount: 0,
    lastRolledColumn: 0,
    lastRolledValues: [3, 4, 2],
    selectedModalChibiIndex: 0
  };

  function build3DFacePipsHTML(faceVal) {
    const activeIndices = D6_PIP_PATTERNS[faceVal] || D6_PIP_PATTERNS[1];
    let cells = "";
    for (let i = 0; i < 9; i++) {
      const hasPip = activeIndices.indexOf(i) !== -1;
      cells += '<span class="cf-d6-pip-cell' + (hasPip ? " active" : "") + '"></span>';
    }
    return '<div class="cf-d6-pip-grid">' + cells + '</div>';
  }

  function buildSingle3DPolyhedralDieHTML(pipValue, isBoosted, colIndex, isTumbling) {
    const val = Math.max(1, Math.min(6, Number(pipValue) || 1));
    const rot = DICE_3D_FACE_ROTATIONS[val] || DICE_3D_FACE_ROTATIONS[1];
    const tumbleCls = isTumbling ? " cf-die3d-tumbling die-tumbling-3d" : "";
    const boostCls = isBoosted ? " cf-die3d-boosted" : "";

    let facesHtml = "";
    for (let f = 1; f <= 6; f++) {
      const texUrl = "./GeneratedArt/Dice3D/dice3d_d6_face_" + f + ".png";
      facesHtml +=
        '<div class="cube-face cf-poly-face f-' + f + '" data-face="' + f + '">' +
          '<img class="cf-die3d-tex" src="' + texUrl + '" alt="" draggable="false" onerror="this.style.display=\'none\';" />' +
          build3DFacePipsHTML(f) +
          '<span class="cf-die3d-numeral">' + f + '</span>' +
          '<span class="cf-die3d-specular"></span>' +
        '</div>';
    }

    // Inner D8 Octahedron crystal core for true polyhedral magicite refraction
    const d8CoreHtml =
      '<div class="cf-d8-octahedron-core" aria-hidden="true">' +
        '<div class="cf-d8-facet d8-f1"></div>' +
        '<div class="cf-d8-facet d8-f2"></div>' +
        '<div class="cf-d8-facet d8-f3"></div>' +
        '<div class="cf-d8-facet d8-f4"></div>' +
      '</div>';

    return (
      '<div class="cube-scene col-header-die-badge cf-poly-die-scene' + boostCls + '" data-col-index="' + colIndex + '" data-pip-value="' + val + '">' +
        '<div class="cube-3d cf-poly-cube-3d' + tumbleCls + '" style="transform: rotateX(' + rot.rx + 'deg) rotateY(' + rot.ry + 'deg) rotateZ(' + rot.rz + 'deg);">' +
          d8CoreHtml +
          facesHtml +
        '</div>' +
      '</div>'
    );
  }

  function ensureStylesInjected() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    if (doc.getElementById("cf-dice3d-and-ffta-chibi-styles")) return;

    const style = doc.createElement("style");
    style.id = "cf-dice3d-and-ffta-chibi-styles";
    style.textContent = `
      /* ====================================================================
         1. TRUE 3D BEVELED POLYHEDRAL DICE (D6 MAGICITE CUBE + D8 CORE)
         ==================================================================== */
      .cf-poly-die-scene {
        width: 34px !important;
        height: 34px !important;
        perspective: 260px !important;
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
      .cf-poly-cube-3d {
        width: 30px !important;
        height: 30px !important;
        position: relative;
        transform-style: preserve-3d !important;
        transition: transform 0.68s cubic-bezier(0.22, 1.35, 0.36, 1) !important;
      }
      .cf-poly-cube-3d.cf-die3d-tumbling {
        animation: cfPolyDieTumble3D 0.68s cubic-bezier(0.18, 0.89, 0.32, 1.28);
      }
      @keyframes cfPolyDieTumble3D {
        0%   { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale3d(1, 1, 1); }
        35%  { transform: rotateX(420deg) rotateY(540deg) rotateZ(180deg) scale3d(1.22, 1.22, 1.22); }
        70%  { transform: rotateX(680deg) rotateY(960deg) rotateZ(310deg) scale3d(1.08, 1.08, 1.08); }
        100% { transform: rotateX(720deg) rotateY(1080deg) rotateZ(360deg) scale3d(1, 1, 1); }
      }
      .cf-poly-face {
        position: absolute !important;
        width: 30px !important;
        height: 30px !important;
        border-radius: 6px !important;
        background: radial-gradient(circle at 30% 28%, #1e3a8a 0%, #0b192c 72%, #050b14 100%) !important;
        border: 1.8px solid #38bdf8 !important;
        box-shadow:
          inset 0 0 9px rgba(0, 229, 255, 0.55),
          inset 0 1px 2px rgba(255, 255, 255, 0.45),
          0 2px 6px rgba(0, 0, 0, 0.65) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden;
        backface-visibility: hidden !important;
        -webkit-backface-visibility: hidden !important;
      }
      .cf-poly-die-scene.cf-die3d-boosted .cf-poly-face,
      .col-header-pill.boosted .cf-poly-face,
      .col-die-row.charged .cf-poly-face {
        background: radial-gradient(circle at 30% 28%, #b45309 0%, #451a03 74%, #1c0a00 100%) !important;
        border-color: #fde047 !important;
        box-shadow:
          inset 0 0 11px rgba(250, 204, 21, 0.72),
          0 0 12px rgba(255, 184, 0, 0.55) !important;
      }
      .cf-poly-face.f-1 { transform: rotateY(  0deg) translateZ(15px) !important; }
      .cf-poly-face.f-2 { transform: rotateY(180deg) translateZ(15px) !important; }
      .cf-poly-face.f-3 { transform: rotateY( 90deg) translateZ(15px) !important; }
      .cf-poly-face.f-4 { transform: rotateY(-90deg) translateZ(15px) !important; }
      .cf-poly-face.f-5 { transform: rotateX( 90deg) translateZ(15px) !important; }
      .cf-poly-face.f-6 { transform: rotateX(-90deg) translateZ(15px) !important; }

      .cf-die3d-tex {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.92;
        pointer-events: none;
      }
      .cf-d6-pip-grid {
        position: absolute;
        inset: 3px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(3, 1fr);
        gap: 1px;
        pointer-events: none;
        z-index: 2;
      }
      .cf-d6-pip-cell {
        width: 4px;
        height: 4px;
        margin: auto;
        border-radius: 50%;
        background: transparent;
      }
      .cf-d6-pip-cell.active {
        background: #00E5FF;
        box-shadow: 0 0 4px #00E5FF, inset 0 0 1px #FFFFFF;
      }
      .cf-poly-die-scene.cf-die3d-boosted .cf-d6-pip-cell.active,
      .col-header-pill.boosted .cf-d6-pip-cell.active,
      .col-die-row.charged .cf-d6-pip-cell.active {
        background: #FEF08A;
        box-shadow: 0 0 5px #FFB800, inset 0 0 1px #FFFFFF;
      }
      .cf-die3d-numeral {
        position: relative;
        z-index: 3;
        font-size: 12px;
        font-weight: 900;
        color: #FFFFFF;
        text-shadow: 0 1px 4px #000000, 0 0 6px rgba(0, 229, 255, 0.85);
        line-height: 1;
      }
      .cf-die3d-specular {
        position: absolute;
        top: -30%;
        left: -30%;
        width: 85%;
        height: 55%;
        background: linear-gradient(135deg, rgba(255,255,255,0.38) 0%, transparent 70%);
        transform: rotate(-18deg);
        pointer-events: none;
        z-index: 4;
      }
      .cf-d8-octahedron-core {
        position: absolute;
        inset: 6px;
        transform-style: preserve-3d;
        animation: cfD8CoreSpin 6s linear infinite;
        pointer-events: none;
      }
      .cf-d8-facet {
        position: absolute;
        inset: 0;
        background: rgba(0, 229, 255, 0.22);
        border: 1px solid rgba(255, 184, 0, 0.45);
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
      }
      .cf-d8-facet.d8-f1 { transform: rotateY(0deg) rotateX(35deg); }
      .cf-d8-facet.d8-f2 { transform: rotateY(90deg) rotateX(35deg); }
      .cf-d8-facet.d8-f3 { transform: rotateY(180deg) rotateX(35deg); }
      .cf-d8-facet.d8-f4 { transform: rotateY(270deg) rotateX(35deg); }
      @keyframes cfD8CoreSpin {
        0%   { transform: rotateY(0deg) rotateX(15deg); }
        100% { transform: rotateY(360deg) rotateX(15deg); }
      }

      /* ====================================================================
         2. 4-LAYER 2.5D & 3D EXTRUDED PARALLAX CARD SLABS
         ==================================================================== */
      .card-3d-unit.cf-25d-parallax-slab {
        transform-style: preserve-3d !important;
        perspective: 720px;
        transition: transform 0.18s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.18s ease !important;
        --slab-tilt-x: 0deg;
        --slab-tilt-y: 0deg;
        --slab-spec-x: 50%;
        --slab-spec-y: 35%;
      }
      .board-slot:hover .card-3d-unit.cf-25d-parallax-slab,
      .hand-card-wrap:hover .card-3d-unit.cf-25d-parallax-slab {
        transform: rotateX(var(--slab-tilt-x, -8deg)) rotateY(var(--slab-tilt-y, 6deg)) translateZ(8px) !important;
      }
      /* Layer 0: 3D Extruded Metallic Slab Rim & 6px Physical Thickness */
      .cf-slab-layer-0-rim {
        position: absolute;
        inset: -2px;
        border-radius: 10px;
        transform: translateZ(-6px);
        background: linear-gradient(145deg, #d4af37 0%, #475569 38%, #0f172a 72%, #b45309 100%);
        box-shadow:
          0 7px 0 #1e293b,
          0 10px 18px rgba(0, 0, 0, 0.85),
          inset 0 0 4px rgba(255, 224, 130, 0.65);
        pointer-events: none;
        z-index: 0;
      }
      .card-3d-unit.owner-ai .cf-slab-layer-0-rim {
        background: linear-gradient(145deg, #ff2e54 0%, #4c0519 45%, #0f172a 75%, #f97316 100%);
        box-shadow:
          0 7px 0 #310814,
          0 10px 18px rgba(0, 0, 0, 0.88),
          inset 0 0 4px rgba(255, 46, 84, 0.65);
      }
      /* Layer 1: Recessed Portrait Well + Holographic Foil Specular Sweep */
      .card-3d-unit.cf-25d-parallax-slab .card-art-frame {
        transform: translateZ(2px);
      }
      .cf-slab-holo-foil {
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: radial-gradient(
          circle at var(--slab-spec-x, 50%) var(--slab-spec-y, 35%),
          rgba(255, 255, 255, 0.24) 0%,
          rgba(0, 229, 255, 0.14) 28%,
          rgba(168, 85, 247, 0.12) 54%,
          transparent 78%
        );
        mix-blend-mode: screen;
        pointer-events: none;
        z-index: 3;
      }
      /* Layer 2: Floating 2.5D N/E/S/W Compass Gem Cluster & Frame Filigree */
      .card-3d-unit.cf-25d-parallax-slab .edge-num,
      .card-3d-unit.cf-25d-parallax-slab .owner-badge,
      .card-3d-unit.cf-25d-parallax-slab .slot-name-ribbon {
        transform: translateZ(14px);
      }
      .cf-slab-layer-2-filigree {
        position: absolute;
        inset: 3px;
        border-radius: 7px;
        border: 1px solid rgba(255, 224, 130, 0.42);
        box-shadow: inset 0 0 8px rgba(0, 229, 255, 0.22);
        transform: translateZ(12px);
        pointer-events: none;
        z-index: 4;
      }

      /* ====================================================================
         3. LAYER 3: POP-UP FFTA 24x24 PIXEL-CHIBI CHARACTER UNIT ON CARD SLAB
            (Active by default on every board and hand card!)
         ==================================================================== */
      .cf-slab-layer-3-chibi {
        position: absolute;
        right: 4px;
        bottom: 18px;
        width: 44px;
        height: 44px;
        transform: translateZ(28px) rotateX(-16deg);
        transform-style: preserve-3d;
        pointer-events: none;
        z-index: 9;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 1;
        filter: drop-shadow(0 5px 6px rgba(0, 0, 0, 0.88));
        transition: opacity 0.18s ease, transform 0.22s cubic-bezier(0.22, 1.35, 0.36, 1);
      }
      body[data-cf-chibi-overlay="on"] .cf-slab-layer-3-chibi,
      .cf-slab-layer-3-chibi.cf-chibi-attack-active {
        opacity: 1;
      }
      .hand-card-wrap .cf-slab-layer-3-chibi {
        width: 36px;
        height: 36px;
        right: 3px;
        bottom: 15px;
      }
      body[data-cf-chibi-overlay="off"] .cf-slab-layer-3-chibi {
        display: none !important;
      }
      .cf-chibi-pedestal-shadow {
        position: absolute;
        bottom: 1px;
        left: 16%;
        width: 68%;
        height: 7px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 229, 255, 0.55) 0%, rgba(0, 0, 0, 0.78) 75%);
        border: 1px solid rgba(255, 184, 0, 0.65);
      }
      .cf-chibi-owner-ai .cf-chibi-pedestal-shadow {
        background: radial-gradient(circle, rgba(255, 46, 84, 0.6) 0%, rgba(0, 0, 0, 0.82) 75%);
        border-color: rgba(255, 46, 84, 0.75);
      }
      .cf-chibi-sprite-stage {
        position: relative;
        width: 100%;
        height: 100%;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
        animation: cfChibiIdleBounce 0.8s steps(2, end) infinite;
      }
      .cf-chibi-png-sprite {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: contain;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
        z-index: 2;
      }
      .cf-chibi-frame {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .cf-chibi-frame-0 {
        animation: cfChibiFrame0Toggle 0.8s steps(1, end) infinite;
      }
      .cf-chibi-frame-1 {
        animation: cfChibiFrame1Toggle 0.8s steps(1, end) infinite;
      }
      .cf-ffta-pixel-svg {
        width: 100%;
        height: 100%;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
      }
      @keyframes cfChibiIdleBounce {
        0%, 100% { transform: translateY(0px); }
        50%      { transform: translateY(-3px); }
      }
      @keyframes cfChibiFrame0Toggle {
        0%, 49.9% { opacity: 1; }
        50%, 100% { opacity: 0; }
      }
      @keyframes cfChibiFrame1Toggle {
        0%, 49.9% { opacity: 0; }
        50%, 100% { opacity: 1; }
      }
      /* Attack Slash Leap Animation on Deploy / Capture */
      .board-slot.just-placed .cf-slab-layer-3-chibi,
      .board-slot.just-flipped .cf-slab-layer-3-chibi,
      .cf-slab-layer-3-chibi.cf-chibi-attack-active {
        animation: cfChibiAttackLeap 0.62s cubic-bezier(0.18, 0.89, 0.32, 1.28) !important;
      }
      @keyframes cfChibiAttackLeap {
        0%   { transform: translateZ(28px) translateY(0) scale(1); }
        35%  { transform: translateZ(54px) translateY(-16px) translateX(-6px) scale(1.38) rotate(-10deg); }
        65%  { transform: translateZ(46px) translateY(-6px) translateX(8px) scale(1.25) rotate(8deg); }
        100% { transform: translateZ(28px) translateY(0) scale(1); }
      }
      .cf-chibi-slash-fx {
        position: absolute;
        inset: -8px;
        opacity: 0;
        pointer-events: none;
        background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,184,0,0.65) 40%, transparent 72%);
        clip-path: polygon(10% 85%, 45% 15%, 92% 8%, 60% 60%, 88% 92%, 35% 75%);
      }
      .board-slot.just-placed .cf-chibi-slash-fx,
      .board-slot.just-flipped .cf-chibi-slash-fx,
      .cf-slab-layer-3-chibi.cf-chibi-attack-active .cf-chibi-slash-fx {
        animation: cfChibiSlashBurst 0.55s ease-out;
      }
      @keyframes cfChibiSlashBurst {
        0%   { opacity: 0; transform: scale(0.4) rotate(-25deg); }
        40%  { opacity: 1; transform: scale(1.35) rotate(12deg); }
        100% { opacity: 0; transform: scale(1.6) rotate(32deg); }
      }
    `;
    doc.head.appendChild(style);
  }

  // ==========================================================================
  // 6. UPGRADE ALL COLUMN & HUD DICE TO 3D POLYHEDRAL CUBES & OCTAHEDRONS
  // ==========================================================================
  function upgradeAllDiceTo3D() {
    if (typeof globalScope.document === "undefined") return { upgradedCount: 0 };
    ensureStylesInjected();
    const doc = globalScope.document;
    const st = globalScope.state || {};
    const colDice = Array.isArray(st.colDice) ? st.colDice : DICE3D_RUNTIME_STATE.lastRolledValues;
    let upgradedCount = 0;

    // 1. Upgrade #col-headers (.col-header-pill) and ensure IDs #col-die-0, #col-die-1, #col-die-2 exist
    const headerPills = doc.querySelectorAll("#col-headers .col-header-pill");
    headerPills.forEach(function (pill, idx) {
      if (!pill.id) {
        pill.id = "col-die-" + idx;
      }
      const pip = Number(colDice[idx] || 3);
      const boosted = pip >= 4 || pill.classList.contains("boosted");
      const pedestalRing = pill.querySelector(".die-pedestal-ring");
      const wasTumbling = Boolean(pedestalRing && pedestalRing.querySelector(".die-tumbling-3d"));
      const isTumbling = wasTumbling || Boolean(st.tumblingCols && st.tumblingCols[idx]);
      if (pedestalRing) {
        pedestalRing.innerHTML = buildSingle3DPolyhedralDieHTML(pip, boosted, idx, isTumbling);
        upgradedCount += 1;
      }
    });

    // Also check direct #col-die-0, #col-die-1, #col-die-2 if created outside #col-headers
    for (let c = 0; c < 3; c++) {
      const directEl = doc.getElementById("col-die-" + c);
      if (directEl && !directEl.querySelector(".cf-poly-cube-3d")) {
        const pip = Number(colDice[c] || 3);
        const boosted = pip >= 4 || directEl.classList.contains("boosted");
        const scene = directEl.querySelector(".cube-scene");
        if (scene) {
          scene.outerHTML = buildSingle3DPolyhedralDieHTML(pip, boosted, c, false);
          upgradedCount += 1;
        }
      }
    }

    // 2. Upgrade floating HUD #dice-column-list (.col-die-row)
    const hudRows = doc.querySelectorAll("#dice-column-list .col-die-row");
    hudRows.forEach(function (row, idx) {
      const pip = Number(colDice[idx] || 3);
      const boosted = pip >= 4 || row.classList.contains("charged");
      const existingScene = row.querySelector(".cube-scene");
      if (existingScene) {
        existingScene.outerHTML = buildSingle3DPolyhedralDieHTML(pip, boosted, idx, false);
        upgradedCount += 1;
      }
    });

    return {
      ok: true,
      upgradedCount: upgradedCount,
      colDice: colDice.slice(0, 3)
    };
  }

  function roll3DColumnDie(colIndex, newValue) {
    const idx = Math.max(0, Math.min(2, Number(colIndex) || 0));
    if (!globalScope.state || typeof globalScope.state !== "object") {
      globalScope.state = { colDice: [3, 4, 2], tumblingCols: [false, false, false] };
    }
    const st = globalScope.state;
    if (!Array.isArray(st.colDice)) {
      st.colDice = [3, 4, 2];
    }
    const val = typeof newValue === "number" && newValue >= 1 && newValue <= 6
      ? Math.floor(newValue)
      : ((st.colDice[idx] % 6) + 1);

    st.colDice[idx] = val;
    st.tumblingCols = st.tumblingCols || [false, false, false];
    st.tumblingCols[idx] = true;

    DICE3D_RUNTIME_STATE.rollCount += 1;
    DICE3D_RUNTIME_STATE.lastRolledColumn = idx;
    DICE3D_RUNTIME_STATE.lastRolledValues = st.colDice.slice(0, 3);

    if (typeof globalScope.renderAll === "function") {
      globalScope.renderAll();
    }
    upgradeAllDiceTo3D();

    if (typeof globalScope.document !== "undefined") {
      const cubes = globalScope.document.querySelectorAll(
        '.cf-poly-die-scene[data-col-index="' + idx + '"] .cf-poly-cube-3d'
      );
      cubes.forEach(function (cube) {
        cube.classList.remove("cf-die3d-tumbling", "die-tumbling-3d");
        void cube.offsetWidth;
        cube.classList.add("cf-die3d-tumbling", "die-tumbling-3d");
      });
    }

    setTimeout(function () {
      if (st.tumblingCols) st.tumblingCols[idx] = false;
    }, 680);

    return {
      ok: true,
      colIndex: idx,
      value: val,
      colDice: st.colDice.slice(0, 3),
      rollCount: DICE3D_RUNTIME_STATE.rollCount
    };
  }

  function rollAll3DColumnDice(customValues) {
    if (!globalScope.state || typeof globalScope.state !== "object") {
      globalScope.state = { colDice: [3, 4, 2], tumblingCols: [false, false, false] };
    }
    const st = globalScope.state;
    if (!Array.isArray(st.colDice)) {
      st.colDice = [3, 4, 2];
    }
    for (let c = 0; c < 3; c++) {
      const v = Array.isArray(customValues) && typeof customValues[c] === "number"
        ? Math.max(1, Math.min(6, Math.floor(customValues[c])))
        : (1 + ((DICE3D_RUNTIME_STATE.rollCount * 3 + c * 2 + st.colDice[c]) % 6));
      roll3DColumnDie(c, v);
    }
    return {
      ok: true,
      colDice: st.colDice.slice(0, 3),
      rollCount: DICE3D_RUNTIME_STATE.rollCount
    };
  }

  // ==========================================================================
  // 7. UPGRADE ALL BOARD & HAND CARDS TO 4-LAYER 2.5D/3D PARALLAX SLABS + CHIBI
  // ==========================================================================
  function resolveCardIdFromElement(cardEl) {
    if (!cardEl) return "h_archangel";
    if (cardEl.dataset && cardEl.dataset.cardId) return cardEl.dataset.cardId;

    const slotEl = cardEl.closest ? cardEl.closest(".board-slot") : null;
    const st = globalScope.state;
    if (slotEl && st && Array.isArray(st.grid)) {
      const r = Number(slotEl.dataset.r);
      const c = Number(slotEl.dataset.c);
      if (!isNaN(r) && !isNaN(c) && st.grid[r] && st.grid[r][c] && st.grid[r][c].cardId) {
        return st.grid[r][c].cardId;
      }
    }

    const handWrap = cardEl.closest ? cardEl.closest(".hand-card-wrap") : null;
    if (handWrap && handWrap.parentElement && st && Array.isArray(st.hand)) {
      const siblings = Array.prototype.slice.call(handWrap.parentElement.children);
      const hIdx = siblings.indexOf(handWrap);
      if (hIdx >= 0 && st.hand[hIdx]) {
        return st.hand[hIdx];
      }
    }

    const img = cardEl.querySelector ? cardEl.querySelector("img.slot-art") : null;
    if (img && img.getAttribute("src")) {
      const m = img.getAttribute("src").match(/\/([a-zA-Z0-9_]+)\.(?:png|jpg|webp)$/);
      if (m && m[1]) return m[1];
    }
    return "h_archangel";
  }

  function bindInteractiveSlabTilt(containerEl, cardUnitEl) {
    if (!containerEl || !cardUnitEl || containerEl.dataset.cfTiltBound === "1") return;
    containerEl.dataset.cfTiltBound = "1";
    containerEl.addEventListener("pointermove", function (ev) {
      const rect = containerEl.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const nx = (ev.clientX - rect.left) / rect.width;
      const ny = (ev.clientY - rect.top) / rect.height;
      const tiltY = ((nx - 0.5) * 18).toFixed(2) + "deg";
      const tiltX = ((0.5 - ny) * 16).toFixed(2) + "deg";
      cardUnitEl.style.setProperty("--slab-tilt-x", tiltX);
      cardUnitEl.style.setProperty("--slab-tilt-y", tiltY);
      cardUnitEl.style.setProperty("--slab-spec-x", (nx * 100).toFixed(1) + "%");
      cardUnitEl.style.setProperty("--slab-spec-y", (ny * 100).toFixed(1) + "%");
    });
    containerEl.addEventListener("pointerleave", function () {
      cardUnitEl.style.setProperty("--slab-tilt-x", "0deg");
      cardUnitEl.style.setProperty("--slab-tilt-y", "0deg");
      cardUnitEl.style.setProperty("--slab-spec-x", "50%");
      cardUnitEl.style.setProperty("--slab-spec-y", "35%");
    });
  }

  function upgradeSingleCardElementTo25DSlab(cardUnitEl, explicitCardId, explicitOwner) {
    if (!cardUnitEl) return null;
    const cardId = explicitCardId || resolveCardIdFromElement(cardUnitEl);
    const owner = explicitOwner || (cardUnitEl.classList.contains("owner-ai") ? "ai" : "player");
    const chibi = getUniqueChibiForCard(cardId);

    cardUnitEl.dataset.cardId = cardId;
    cardUnitEl.dataset.chibiUnitId = chibi.chibiUnitId;
    cardUnitEl.classList.add("cf-25d-parallax-slab", "card");

    const parentSlot = cardUnitEl.closest ? cardUnitEl.closest(".board-slot") : null;
    const parentHand = cardUnitEl.closest ? cardUnitEl.closest(".hand-card-wrap") : null;
    if (parentSlot) {
      parentSlot.classList.add("grid-slot");
      cardUnitEl.classList.add("board-card");
      bindInteractiveSlabTilt(parentSlot, cardUnitEl);
    }
    if (parentHand) {
      parentHand.classList.add("hand-card");
      cardUnitEl.classList.add("hand-card");
      bindInteractiveSlabTilt(parentHand, cardUnitEl);
    }

    // Layer 0: 3D Extruded Metallic Slab Rim
    if (!cardUnitEl.querySelector(".cf-slab-layer-0-rim")) {
      const rim = globalScope.document.createElement("div");
      rim.className = "cf-slab-layer-0-rim";
      cardUnitEl.insertBefore(rim, cardUnitEl.firstChild);
    }

    // Layer 1: Recessed Portrait Well + Holographic Foil Specular Sweep
    const artFrame = cardUnitEl.querySelector(".card-art-frame");
    if (artFrame) {
      artFrame.classList.add("cf-slab-layer-1-portrait");
      if (!artFrame.querySelector(".cf-slab-holo-foil")) {
        const foil = globalScope.document.createElement("div");
        foil.className = "cf-slab-holo-foil";
        artFrame.appendChild(foil);
      }
    }

    // Layer 2: Floating 2.5D Frame Filigree
    if (!cardUnitEl.querySelector(".cf-slab-layer-2-filigree")) {
      const fil = globalScope.document.createElement("div");
      fil.className = "cf-slab-layer-2-filigree";
      cardUnitEl.appendChild(fil);
    }

    // Layer 3: Pop-Up FFTA 24x24 Pixel-Chibi Character Unit
    const existingChibi = cardUnitEl.querySelector(".cf-slab-layer-3-chibi");
    if (!existingChibi || existingChibi.dataset.chibiId !== chibi.chibiUnitId) {
      if (existingChibi) existingChibi.remove();
      cardUnitEl.insertAdjacentHTML("beforeend", buildChibiUnitBadgeHTML(cardId, owner));
    }

    return chibi;
  }

  function upgradeCardsTo25DParallaxSlabs() {
    if (typeof globalScope.document === "undefined") return { upgradedCards: 0 };
    ensureStylesInjected();
    const doc = globalScope.document;

    // Ensure all 9 board slots carry .grid-slot class
    const boardSlots = doc.querySelectorAll("#grid-3x3 .board-slot");
    boardSlots.forEach(function (s) {
      s.classList.add("grid-slot");
    });

    const cardUnits = doc.querySelectorAll(".card-3d-unit");
    let count = 0;
    cardUnits.forEach(function (unitEl) {
      upgradeSingleCardElementTo25DSlab(unitEl);
      count += 1;
    });

    return {
      ok: true,
      upgradedCards: count,
      depthMode: DICE3D_RUNTIME_STATE.depthMode
    };
  }

  function triggerChibiAttackAnimation(cellIndex) {
    if (typeof globalScope.document === "undefined") return { ok: false };
    ensureStylesInjected();
    const idx = Math.max(0, Math.min(8, Number(cellIndex) || 0));
    const slots = globalScope.document.querySelectorAll("#grid-3x3 .board-slot");
    const targetSlot = slots[idx];
    let triggeredChibiId = null;

    if (targetSlot) {
      const chibiEl = targetSlot.querySelector(".cf-slab-layer-3-chibi");
      if (chibiEl) {
        triggeredChibiId = chibiEl.dataset.chibiId || "chibi_unit_001";
        chibiEl.classList.remove("cf-chibi-attack-active");
        void chibiEl.offsetWidth;
        chibiEl.classList.add("cf-chibi-attack-active");
        setTimeout(function () {
          chibiEl.classList.remove("cf-chibi-attack-active");
        }, 650);
      }
    }

    DICE3D_RUNTIME_STATE.chibiAttackCount += 1;
    if (typeof globalScope.playTone === "function") {
      globalScope.playTone(9, "triangle", 0.16, true);
    }

    return {
      ok: true,
      cellIndex: idx,
      chibiUnitId: triggeredChibiId,
      attackCount: DICE3D_RUNTIME_STATE.chibiAttackCount
    };
  }

  function setCard25DDepthMode(mode) {
    const validModes = ["3d_extruded_hd2d", "25d_parallax_relief", "flat_classic"];
    const nextMode = validModes.indexOf(mode) !== -1 ? mode : "3d_extruded_hd2d";
    DICE3D_RUNTIME_STATE.depthMode = nextMode;
    if (typeof globalScope.document !== "undefined" && globalScope.document.body) {
      globalScope.document.body.setAttribute("data-cf-slab-depth-mode", nextMode);
    }
    upgradeCardsTo25DParallaxSlabs();
    return {
      ok: true,
      depthMode: nextMode
    };
  }

  // ==========================================================================
  // 8. INTERACTIVE 3D DICE, 2.5D SLAB & FFTA PIXEL-CHIBI ATELIER MODAL
  //    (#dice3d-ffta-chibi-modal)
  // ==========================================================================
  function ensureModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("dice3d-ffta-chibi-modal");
    if (!modal && doc.body) {
      modal = doc.createElement("div");
      modal.id = "dice3d-ffta-chibi-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-label", "3D Polyhedral Dice, 2.5D Card Slab & FFTA Pixel-Chibi Unit Atelier");
      modal.style.cssText =
        "display:none;position:fixed;inset:0;z-index:9690;background:rgba(5,9,18,0.92);backdrop-filter:blur(10px);padding:18px;overflow-y:auto;color:#f8fafc;font-family:system-ui,-apple-system,sans-serif;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function selectModalChibiArchetype(index) {
    const clamped = Math.max(0, Math.min(FFTA_PIXEL_CHIBI_ROSTER_24.length - 1, Number(index) || 0));
    DICE3D_RUNTIME_STATE.selectedModalChibiIndex = clamped;
    renderModalContents();
    return FFTA_PIXEL_CHIBI_ROSTER_24[clamped];
  }

  function renderModalContents() {
    const modal = ensureModalDom();
    if (!modal) return;

    const st = globalScope.state || {};
    const colDice = Array.isArray(st.colDice) ? st.colDice : [3, 4, 2];
    const selectedArch = FFTA_PIXEL_CHIBI_ROSTER_24[DICE3D_RUNTIME_STATE.selectedModalChibiIndex] || FFTA_PIXEL_CHIBI_ROSTER_24[0];
    const sampleBinding = CARD_TO_CHIBI_BINDINGS_141[DICE3D_RUNTIME_STATE.selectedModalChibiIndex] || CARD_TO_CHIBI_BINDINGS_141[0];

    const diceShowcaseHtml = [0, 1, 2].map(function (c) {
      const pip = Number(colDice[c] || 3);
      const boosted = pip >= 4;
      return (
        '<div style="background:rgba(15,23,42,0.9);border:1px solid ' + (boosted ? "#FACC15" : "#38BDF8") + ';border-radius:10px;padding:12px;display:flex;align-items:center;justify-content:space-between;gap:12px;">' +
          '<div>' +
            '<div style="font-size:11px;font-weight:800;color:#94A3B8;">COLUMN ' + (c + 1) + ' POLYHEDRAL DIE</div>' +
            '<div style="font-size:14px;font-weight:900;color:' + (boosted ? "#FEF08A" : "#F8FAFC") + ';">Pip ' + pip + (boosted ? " (+1 Lane Surge)" : " (Standard)") + '</div>' +
            '<button onclick="window.CardFrontDice3DAndChibiUnits.roll3DColumnDie(' + c + ');window.CardFrontDice3DAndChibiUnits.renderModalContents();" style="margin-top:6px;padding:5px 10px;border-radius:6px;background:#1E293B;color:#38BDF8;border:1px solid #38BDF8;font-size:11px;font-weight:800;cursor:pointer;">[TUMBLE COL ' + (c + 1) + ' 3D DIE]</button>' +
          '</div>' +
          '<div style="transform:scale(1.35);padding:8px;">' +
            buildSingle3DPolyhedralDieHTML(pip, boosted, c, false) +
          '</div>' +
        '</div>'
      );
    }).join("");

    const chibiGridHtml = FFTA_PIXEL_CHIBI_ROSTER_24.map(function (arch, idx) {
      const bind = CARD_TO_CHIBI_BINDINGS_141[idx] || CARD_TO_CHIBI_BINDINGS_141[0];
      const active = idx === DICE3D_RUNTIME_STATE.selectedModalChibiIndex;
      return (
        '<div onclick="window.CardFrontDice3DAndChibiUnits.selectModalChibiArchetype(' + idx + ')" style="cursor:pointer;background:' +
        (active ? "linear-gradient(135deg,rgba(0,229,255,0.22),rgba(255,184,0,0.18))" : "rgba(15,23,42,0.85)") +
        ";border:1.5px solid " + (active ? "#FACC15" : "rgba(148,163,184,0.28)") +
        ';border-radius:9px;padding:8px;text-align:center;">' +
          '<div style="width:48px;height:48px;margin:0 auto;">' +
            renderChibi24x24Svg(bind.cardId, idx % 2) +
          '</div>' +
          '<div style="font-size:10.5px;font-weight:900;color:#F8FAFC;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + arch.jobTitle + '</div>' +
          '<div style="font-size:9.5px;color:#94A3B8;">' + arch.faction + ' | ' + arch.weaponType + '</div>' +
        '</div>'
      );
    }).join("");

    modal.innerHTML =
      '<div style="max-width:1160px;margin:0 auto;background:#090D16;border:1.5px solid #FFB800;border-radius:14px;padding:18px;box-shadow:0 24px 64px rgba(0,0,0,0.9);">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;border-bottom:1px solid rgba(255,184,0,0.3);padding-bottom:12px;margin-bottom:14px;">' +
          '<div>' +
            '<div style="font-size:11px;font-weight:800;color:#00E5FF;letter-spacing:0.08em;">[TRACK B | TRUE 3D POLYHEDRAL DICE | 4-LAYER 2.5D SLABS | 141 UNIQUE FFTA PIXEL-CHIBI UNITS]</div>' +
            '<div style="font-size:18px;font-weight:900;color:#F8FAFC;">3D Polyhedral Magicite Dice & FFTA 2.5-Head Pixel-Chibi Unit Atelier</div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
            '<button id="btn-roll-all-3d-dice" onclick="window.CardFrontDice3DAndChibiUnits.rollAll3DColumnDice();window.CardFrontDice3DAndChibiUnits.renderModalContents();" style="padding:8px 12px;border-radius:7px;background:linear-gradient(135deg,#00E5FF,#0284C7);color:#041019;font-weight:900;font-size:11.5px;border:none;cursor:pointer;">[ROLL ALL 3D POLYHEDRAL DICE]</button>' +
            '<button id="btn-trigger-chibi-slash" onclick="window.CardFrontDice3DAndChibiUnits.triggerChibiAttackAnimation(4);" style="padding:8px 12px;border-radius:7px;background:linear-gradient(135deg,#FFB800,#D97706);color:#1C0A00;font-weight:900;font-size:11.5px;border:none;cursor:pointer;">[TRIGGER CHIBI SLASH ON BOARD]</button>' +
            '<button onclick="window.CardFrontDice3DAndChibiUnits.closeDice3DAndChibiModal();" style="padding:8px 12px;border-radius:7px;background:rgba(239,68,68,0.2);color:#FCA5A5;border:1px solid #EF4444;font-weight:800;font-size:11.5px;cursor:pointer;">[CLOSE ESC]</button>' +
          '</div>' +
        '</div>' +

        // Row 1: Live 3D Polyhedral Column Dice Inspector
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:16px;">' +
          diceShowcaseHtml +
        '</div>' +

        // Row 2: Selected Chibi Unit Frame 0 / Frame 1 Inspector + 4-Layer 2.5D Slab Spec
        '<div style="background:rgba(15,23,42,0.92);border:1px solid rgba(0,229,255,0.35);border-radius:10px;padding:12px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">' +
          '<div style="display:flex;align-items:center;gap:14px;">' +
            '<div style="width:64px;height:64px;background:#050B14;border:1px solid #FFB800;border-radius:8px;padding:6px;">' +
              renderChibi24x24Svg(sampleBinding.cardId, 0) +
            '</div>' +
            '<div style="width:64px;height:64px;background:#050B14;border:1px solid #00E5FF;border-radius:8px;padding:6px;">' +
              renderChibi24x24Svg(sampleBinding.cardId, 1) +
            '</div>' +
            '<div>' +
              '<div style="font-size:13.5px;font-weight:900;color:#FEF08A;">' + selectedArch.jobTitle + ' (' + selectedArch.archetypeId + ')</div>' +
              '<div style="font-size:11.5px;color:#CBD5E1;">Proportion: <b>' + selectedArch.headRatio + '</b> | Weapon: <b>' + selectedArch.weaponType + '</b> | Headgear: <b>' + selectedArch.headgearType + '</b></div>' +
              '<div style="font-size:11px;color:#2EE6D3;">141/141 Unique Card-to-Chibi Bindings Active | Layer 0 (-6px Rim) / Layer 1 (+2px Well) / Layer 2 (+14px Compass) / Layer 3 (+28px Chibi)</div>' +
            '</div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
            '<button onclick="window.CardFrontDice3DAndChibiUnits.setCard25DDepthMode(\'3d_extruded_hd2d\');" style="padding:7px 11px;border-radius:6px;background:#1E293B;color:#FEF08A;border:1px solid #FACC15;font-size:11px;font-weight:800;cursor:pointer;">[DEPTH: 3D EXTRUDED HD-2D]</button>' +
            '<button onclick="window.CardFrontDice3DAndChibiUnits.setCard25DDepthMode(\'25d_parallax_relief\');" style="padding:7px 11px;border-radius:6px;background:#1E293B;color:#38BDF8;border:1px solid #38BDF8;font-size:11px;font-weight:800;cursor:pointer;">[DEPTH: 2.5D RELIEF]</button>' +
          '</div>' +
        '</div>' +

        // Row 3: 24 FFTA Pixel-Chibi Archetype Roster Grid
        '<div style="font-size:12px;font-weight:900;color:#94A3B8;margin-bottom:8px;">[24 FFTA ISOMETRIC 2.5-HEAD PIXEL-CHIBI ARCHETYPES | CLICK TO INSPECT]</div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;">' +
          chibiGridHtml +
        '</div>' +
      '</div>';
  }

  function openDice3DAndChibiModal(archetypeIdx) {
    ensureStylesInjected();
    if (typeof archetypeIdx === "number" && !isNaN(archetypeIdx)) {
      DICE3D_RUNTIME_STATE.selectedModalChibiIndex = Math.max(0, Math.min(FFTA_PIXEL_CHIBI_ROSTER_24.length - 1, archetypeIdx));
    }
    const modal = ensureModalDom();
    renderModalContents();
    if (modal) {
      modal.style.display = "block";
    }
    return {
      ok: true,
      diceModelsCount: DICE_3D_MODELS_12.length,
      chibiArchetypesCount: FFTA_PIXEL_CHIBI_ROSTER_24.length,
      uniqueCardBindingsCount: CARD_TO_CHIBI_BINDINGS_141.length
    };
  }

  function closeDice3DAndChibiModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("dice3d-ffta-chibi-modal");
    if (modal) {
      modal.style.display = "none";
    }
  }

  // ==========================================================================
  // 9. AUTO-MOUNTING HOOKS INTO build3DCardHTML, renderAll, nudgeColDie, rerollAllDice
  // ==========================================================================
  function installRuntimeHooks() {
    ensureStylesInjected();
    if (typeof globalScope.document !== "undefined" && globalScope.document.body) {
      globalScope.document.body.setAttribute("data-cf-chibi-overlay", "on");
      globalScope.document.body.setAttribute("data-cf-slab-depth-mode", DICE3D_RUNTIME_STATE.depthMode || "3d_extruded_hd2d");
    }

    // Hook build3DCardHTML so every newly rendered card automatically includes the 4-layer 2.5D slab & FFTA Chibi unit
    if (typeof globalScope.build3DCardHTML === "function" && !globalScope.build3DCardHTML._cfChibiWrapped) {
      const origBuildCard = globalScope.build3DCardHTML;
      const wrappedBuildCard = function (cardId, nesw, owner, isBoosted) {
        const rawHtml = origBuildCard.call(this, cardId, nesw, owner, isBoosted);
        const chibi = getUniqueChibiForCard(cardId);
        const rimHtml = '<div class="cf-slab-layer-0-rim"></div>';
        const foilHtml = '<div class="cf-slab-holo-foil"></div>';
        const filHtml = '<div class="cf-slab-layer-2-filigree"></div>';
        const chibiHtml = buildChibiUnitBadgeHTML(cardId, owner);

        return rawHtml
          .replace(
            /<div class="card-3d-unit ([^"]+)">/,
            '<div class="card-3d-unit $1 cf-25d-parallax-slab card" data-card-id="' + String(cardId || "h_archangel") + '" data-chibi-unit-id="' + chibi.chibiUnitId + '">' + rimHtml
          )
          .replace(
            /<div class="slot-vignette"><\/div>/,
            '<div class="slot-vignette"></div>' + foilHtml
          )
          .replace(
            /<\/div>\s*$/,
            filHtml + chibiHtml + "</div>"
          );
      };
      wrappedBuildCard._cfChibiWrapped = true;
      globalScope.build3DCardHTML = wrappedBuildCard;
    }

    // Hook renderAll so every board/hand/dice refresh upgrades all 3D dice and 2.5D card slabs
    if (typeof globalScope.renderAll === "function" && !globalScope.renderAll._cfDiceChibiWrapped) {
      const origRenderAll = globalScope.renderAll;
      const wrappedRenderAll = function () {
        const res = origRenderAll.apply(this, arguments);
        upgradeAllDiceTo3D();
        upgradeCardsTo25DParallaxSlabs();
        return res;
      };
      wrappedRenderAll._cfDiceChibiWrapped = true;
      globalScope.renderAll = wrappedRenderAll;
    }

    // Hook nudgeColDie to trigger physical 3D cube tumble on nudge
    if (typeof globalScope.nudgeColDie === "function" && !globalScope.nudgeColDie._cfDiceChibiWrapped) {
      const origNudge = globalScope.nudgeColDie;
      const wrappedNudge = function (colIdx) {
        const res = origNudge.apply(this, arguments);
        upgradeAllDiceTo3D();
        return res;
      };
      wrappedNudge._cfDiceChibiWrapped = true;
      globalScope.nudgeColDie = wrappedNudge;
    }

    upgradeAllDiceTo3D();
    upgradeCardsTo25DParallaxSlabs();
  }

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", installRuntimeHooks);
    } else {
      installRuntimeHooks();
    }
    globalScope.addEventListener("load", installRuntimeHooks);
  }

  // ==========================================================================
  // 10. EXPOSE GLOBAL MODULE API
  // ==========================================================================
  const CardFrontDice3DAndChibiUnits = {
    DICE_3D_MODELS_12: DICE_3D_MODELS_12,
    POLYHEDRAL_3D_DICE_12: DICE_3D_MODELS_12,
    FFTA_PIXEL_CHIBI_ROSTER_24: FFTA_PIXEL_CHIBI_ROSTER_24,
    CARD_TO_CHIBI_BINDINGS_141: CARD_TO_CHIBI_BINDINGS_141,
    state: DICE3D_RUNTIME_STATE,
    upgradeAllDiceTo3D: upgradeAllDiceTo3D,
    roll3DColumnDie: roll3DColumnDie,
    rollAll3DColumnDice: rollAll3DColumnDice,
    upgradeCardsTo25DParallaxSlabs: upgradeCardsTo25DParallaxSlabs,
    getUniqueChibiForCard: getUniqueChibiForCard,
    renderChibi24x24Svg: renderChibi24x24Svg,
    triggerChibiAttackAnimation: triggerChibiAttackAnimation,
    setCard25DDepthMode: setCard25DDepthMode,
    selectModalChibiArchetype: selectModalChibiArchetype,
    renderModalContents: renderModalContents,
    openDice3DAndChibiModal: openDice3DAndChibiModal,
    closeDice3DAndChibiModal: closeDice3DAndChibiModal,
    installRuntimeHooks: installRuntimeHooks,
    zeroLivingArtistNames: true,
    zeroRawUnicodeEmojis: true
  };

  globalScope.CardFrontDice3DAndChibiUnits = CardFrontDice3DAndChibiUnits;
  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.Dice3DAndChibiUnits = CardFrontDice3DAndChibiUnits;

  globalScope.FFTA_PIXEL_CHIBI_ROSTER_24 = FFTA_PIXEL_CHIBI_ROSTER_24;
  globalScope.DICE_3D_MODELS_12 = DICE_3D_MODELS_12;
  globalScope.CARD_TO_CHIBI_BINDINGS_141 = CARD_TO_CHIBI_BINDINGS_141;
  globalScope.upgradeAllDiceTo3D = upgradeAllDiceTo3D;
  globalScope.roll3DColumnDie = roll3DColumnDie;
  globalScope.rollAll3DColumnDice = rollAll3DColumnDice;
  globalScope.upgradeCardsTo25DParallaxSlabs = upgradeCardsTo25DParallaxSlabs;
  globalScope.getUniqueChibiForCard = getUniqueChibiForCard;
  globalScope.triggerChibiAttackAnimation = triggerChibiAttackAnimation;
  globalScope.setCard25DDepthMode = setCard25DDepthMode;
  globalScope.openDice3DAndChibiModal = openDice3DAndChibiModal;
  globalScope.closeDice3DAndChibiModal = closeDice3DAndChibiModal;
})(typeof window !== "undefined" ? window : globalThis);
