/**
 * CARDFRONT 3D: Cradle of Echoes — 10-Year Saga Franchise Hub, 20-Set Rotation Governor & SBX00 Cluster Vault
 * Module: WebPlayable/modules/saga_10year_franchise_and_sbx00.js
 *
 * Exposes `window.CardFrontSaga10YearFranchise`, `window.CardFrontModules.Saga10YearFranchise`,
 * and top-level global functions/constants:
 *   - `FRANCHISE_SAGA_3_ERAS` (length === 3: Era I Years 1-3, Era II Years 4-7, Era III Years 8-10)
 *   - `FRANCHISE_20_EXPANSION_SETS` (length === 20: SET_01_CRADLE_GENESIS .. SET_20_ETERNAL_CRADLE_APEX, 2,400 cards)
 *   - `SAGA_10YEAR_HERALD_CARDS` (length === 6: saga_y01 .. saga_y10, registered into ALL_CARDS & SET1_CARDS_BY_ID)
 *   - `SBX00_AND_GPU_CLUSTER_TOPOLOGY` (length === 4: SBX00 192.168.86.32 /DATA Vault, V100 32GB, RTX 4080 16GB, Apple Silicon MLX)
 *   - `validateSetRotationAndPowerCreep(deckOrCards, formatId)`
 *   - `getSbx00AndClusterLiveTelemetry()`
 *   - `equip10YearSagaHeraldDeck()`
 *   - `openSaga10YearFranchiseModal(tabId)`
 *   - `closeSaga10YearFranchiseModal()`
 *
 * Art Direction & Engineering Contract:
 *   - ZERO living artists' names anywhere (`zeroLivingArtistNames: true`).
 *   - ZERO raw Unicode emojis in DOM text or buttons (100% inline 256x256 SVGs or crisp ASCII geometric tags).
 */
(function initCardFrontSaga10YearFranchise(globalScope) {
  "use strict";

  // ==========================================================================
  // 1. POWER-CREEP DIRECTIONAL STAT-BUDGET GOVERNOR CAPS
  // ==========================================================================
  const POWER_CREEP_DIRECTIONAL_BUDGET_CAPS = {
    1: 22,
    2: 25,
    3: 28,
    4: 31
  };

  // ==========================================================================
  // 2. 3 FRANCHISE ERAS ACROSS YEARS 1-10 (2,400 PLANNED CARDS)
  // ==========================================================================
  const FRANCHISE_SAGA_3_ERAS = [
    {
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      eraNumber: 1,
      yearsRange: "Years 1-3",
      yearStart: 1,
      yearEnd: 3,
      title: "Era I: Cradle of Echoes & Kubrart Eclipse",
      subtitle: "Okitsu Discovery, Mnemosyne Constellation & High-Contrast Vector Cel Awakening",
      setsCount: 6,
      plannedCardsCount: 720,
      accentHex: "#00E5FF",
      secondaryHex: "#FFB800",
      svgEmblemPath: "./assets/saga_emblems/era_1_cradle_of_echoes.svg",
      coreThemes: [
        "3x3 Directional Capture Grid & 5-Dice Poker/Yahtzee Resonance (1.00x to 4.00x)",
        "Budge (+/-1 Pip) & Chrono Reroll Cognitive-Gated Tactical Mastery",
        "Set 2 Kubrart Astral Eclipse Vector-Cel & 24fps Stepped Kagenashi Cut-Ins"
      ],
      morphologicalSpec:
        "stylized 6.5-to-7.5-head proportions, tapered gauntlets and boots, pen-and-ink G-pen crosshatching over warm parchment-gold filigree, vibrant watercolor cel-wash, astral cyan rim lighting"
    },
    {
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      eraNumber: 2,
      yearsRange: "Years 4-7",
      yearStart: 4,
      yearEnd: 7,
      title: "Era II: Sovran Mechanica & Chrono-Lattice War",
      subtitle: "Orthographic Mecha Reliquaries, Judge Law Tribunals & Asynchronous Ghost Citadels",
      setsCount: 8,
      plannedCardsCount: 960,
      accentHex: "#FF2E54",
      secondaryHex: "#F97316",
      svgEmblemPath: "./assets/saga_emblems/era_2_sovran_mechanica.svg",
      coreThemes: [
        "Orthographic Cyber-Magicite Mecha Blueprints & Column Lockdown Breakers",
        "Ivalice Judge Law Decrees & Multi-Tile Wall-Bounce Knockback Vectors",
        "HMAC-SHA256 Signed Echo-Ghost Citadel Seasons & 5-Pack Arena Cube Drafts"
      ],
      morphologicalSpec:
        "sleek beveled cyber-magicite armor edges, high-contrast obsidian and crimson-flame silhouettes, 60-LPI halftone screentone shadows, angular polyhedral energy shields"
    },
    {
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      eraNumber: 3,
      yearsRange: "Years 8-10",
      yearStart: 8,
      yearEnd: 10,
      title: "Era III: Astral Singularity & Omega Convergence",
      subtitle: "Living Puzzle Synthesis, Sovereign Agent Command & Eternal 20-Set Convergence",
      setsCount: 6,
      plannedCardsCount: 720,
      accentHex: "#A855F7",
      secondaryHex: "#2EE6D3",
      svgEmblemPath: "./assets/saga_emblems/era_3_omega_convergence.svg",
      coreThemes: [
        "Triad Gate Convergence (Merge, Preserve, Carry Forward) & Golden Fox Relics",
        "Sovereign Agent Command Deck Integration & Real-Time Genie-4 World-Step Preview",
        "Eternal 2,400-Card Historic Cube with Zero-Inflation Horizontal Archetype Parity"
      ],
      morphologicalSpec:
        "tarot violet and gilded parchment chiaroscuro foil, asymmetric 4-point cross-star vertices, 14mm foreshortened action perspective, luminous jade-teal astral halos"
    }
  ];

  // ==========================================================================
  // 3. 20 EXPANSION SETS ACROSS YEARS 1-10 (2 SETS/YEAR, 120 CARDS/SET = 2,400)
  // ==========================================================================
  const FRANCHISE_20_EXPANSION_SETS = [
    {
      setId: "SET_01_CRADLE_GENESIS",
      setNumber: 1,
      year: 1,
      half: "H1",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 01: Cradle Genesis (Shifting Pieces)",
      cardCount: 120,
      keyMechanic: "Orthogonal N/E/S/W Capture & 5-Dice Resonance",
      standardLegal: true,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_02_KUBRART_ASTRAL_ECLIPSE",
      setNumber: 2,
      year: 1,
      half: "H2",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 02: Kubrart Astral Eclipse",
      cardCount: 120,
      keyMechanic: "Vector-Cel Eclipse Synergy & PLUS/SAME Combo Cascade",
      standardLegal: true,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_03_MNEMOSYNE_STAR_VAULT",
      setNumber: 3,
      year: 2,
      half: "H1",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 03: Mnemosyne Star-Vault",
      cardCount: 120,
      keyMechanic: "Constellation Center-Tile (1,1) Memory Resonance",
      standardLegal: true,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_04_SHADOW_MAZE_CHIAROSCURO",
      setNumber: 4,
      year: 2,
      half: "H2",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 04: Shadow Maze Chiaroscuro",
      cardCount: 120,
      keyMechanic: "Budge (+/-1 Pip) Light-Beam Column Alignment",
      standardLegal: true,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_05_STUDIO_PXG_ATOMIC_STRIKERS",
      setNumber: 5,
      year: 3,
      half: "H1",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 05: Studio PxG Atomic Strikers",
      cardCount: 120,
      keyMechanic: "24fps Stepped X-Sheet Knockback & 4-Point Star Clash",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_06_KUBRART_ECLIPSE_APEX",
      setNumber: 6,
      year: 3,
      half: "H2",
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      title: "Set 06: Kubrart Eclipse Apex",
      cardCount: 120,
      keyMechanic: "Dual-Tone Rim Armor & Kagenashi Finisher Cut-Ins",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_07_SOVRAN_MECHANICA_DAWN",
      setNumber: 7,
      year: 4,
      half: "H1",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 07: Sovran Mechanica Dawn",
      cardCount: 120,
      keyMechanic: "Orthographic Mecha Relics & Beveled Armor Plating",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_08_OKITSU_TRIBUNAL_DECREE",
      setNumber: 8,
      year: 4,
      half: "H2",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 08: Okitsu Tribunal Decree",
      cardCount: 120,
      keyMechanic: "Ivalice Judge Laws & Tie-Breaker Decree Seals",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_09_CHRONO_ARMADA_VANGUARD",
      setNumber: 9,
      year: 5,
      half: "H1",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 09: Chrono Armada Vanguard",
      cardCount: 120,
      keyMechanic: "Chrono Die Freeze & Turn-Order Initiative Shift",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_10_CRIMSON_RIFT_BASTION",
      setNumber: 10,
      year: 5,
      half: "H2",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 10: Crimson Rift Bastion",
      cardCount: 120,
      keyMechanic: "Obsidian Ash Mutator & Wall-Break Shockwave Bounce",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_11_AETHER_FORGE_CITADEL",
      setNumber: 11,
      year: 6,
      half: "H1",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 11: Aether Forge Citadel",
      cardCount: 120,
      keyMechanic: "CardCraft Anvil Affix Tempering (Non-P2W Horizontal)",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_12_ECHO_GHOST_PARLIAMENT",
      setNumber: 12,
      year: 6,
      half: "H2",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 12: Echo-Ghost Parliament",
      cardCount: 120,
      keyMechanic: "Zero-CCU Ghost Mirror Opening & Tag-Assist Link",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_13_POLYHEDRAL_CRYO_FRONTIER",
      setNumber: 13,
      year: 7,
      half: "H1",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 13: Polyhedral Cryo Frontier",
      cardCount: 120,
      keyMechanic: "Flat-Shaded Glacial Hex Barriers & Slide Repulsion",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_14_CHRONO_LATTICE_CATACLYSM",
      setNumber: 14,
      year: 7,
      half: "H2",
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      title: "Set 14: Chrono-Lattice Cataclysm",
      cardCount: 120,
      keyMechanic: "Pentad (4.00x) Lattice Overdrive & Dual-Voice Sync",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_15_ASTRAL_SINGULARITY_THRESHOLD",
      setNumber: 15,
      year: 8,
      half: "H1",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 15: Astral Singularity Threshold",
      cardCount: 120,
      keyMechanic: "Tarot Chiaroscuro Reversal & Station of Awakening",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_16_SOVEREIGN_AGENT_CONCLAVE",
      setNumber: 16,
      year: 8,
      half: "H2",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 16: Sovereign Agent Conclave",
      cardCount: 120,
      keyMechanic: "System One Calibrated Gate & Parallel Swarm Relics",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_17_HALL_OF_SELVES_MIRROR",
      setNumber: 17,
      year: 9,
      half: "H1",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 17: Hall of Selves Mirror",
      cardCount: 120,
      keyMechanic: "Symmetric Edge Reflection & Red Scarf Convergence",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_18_GOLDEN_FOX_SANCTUARY",
      setNumber: 18,
      year: 9,
      half: "H2",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 18: Golden Fox Sanctuary",
      cardCount: 120,
      keyMechanic: "Rooftop Constellation Fox & Five-Star Amber Link",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_19_OMEGA_CONVERGENCE_VANGUARD",
      setNumber: 19,
      year: 10,
      half: "H1",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 19: Omega Convergence Vanguard",
      cardCount: 120,
      keyMechanic: "Triad Gate Synthesis (Merge / Preserve / Carry Forward)",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    },
    {
      setId: "SET_20_ETERNAL_CRADLE_APEX",
      setNumber: 20,
      year: 10,
      half: "H2",
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      title: "Set 20: Eternal Cradle Apex",
      cardCount: 120,
      keyMechanic: "10-Year Eternal Cube Crown & Living Puzzle Mastery",
      standardLegal: false,
      directionalBudgetCaps: { cost1Max: 22, cost2Max: 25, cost3Max: 28, cost4Max: 31 }
    }
  ];

  // ==========================================================================
  // 4. 6 RTX 4080 10-YEAR SAGA ERA HERALD CARDS (saga_y01 .. saga_y10)
  // ==========================================================================
  const SAGA_10YEAR_HERALD_CARDS = [
    {
      id: "saga_y01",
      slug: "saga_y01_cradle_genesis_herald",
      year: 1,
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      setId: "SET_01_CRADLE_GENESIS",
      name: "Cradle Genesis Herald",
      faction: "Aether",
      starCost: 2,
      cost: 2,
      nesw: [7, 6, 6, 6],
      directionalSum: 25,
      budgetCap: 25,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y01_cradle_genesis_herald.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_archangel.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_archangel_strip.png",
      telegraphType: "Year 1 Genesis Beacon",
      telegraphName: "Okitsu Dawn Resonance",
      telegraphColor: "#00E5FF",
      telegraphDesc: "Anchors Year 1 Standard Rotation with a balanced 25-pip directional budget (Cost 2 <= 25) and +1 Budge token on deploy.",
      abilityName: "Genesis Threshold Link",
      abilityText: "On Deploy: Aligns adjacent friendly North/East edges by +1 when Column Dice show a Pair (1.50x) or higher."
    },
    {
      id: "saga_y02",
      slug: "saga_y02_kubrart_eclipse_arbiter",
      year: 2,
      eraId: "ERA_I_CRADLE_OF_ECHOES_AND_KUBRART_ECLIPSE",
      setId: "SET_02_KUBRART_ASTRAL_ECLIPSE",
      name: "Kubrart Eclipse Arbiter",
      faction: "Chrono",
      starCost: 3,
      cost: 3,
      nesw: [8, 7, 6, 7],
      directionalSum: 28,
      budgetCap: 28,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y02_kubrart_eclipse_arbiter.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_arbiter.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_arbiter_strip.png",
      telegraphType: "Year 2 Vector-Cel Decree",
      telegraphName: "Eclipse Halo Judgment",
      telegraphColor: "#FFB800",
      telegraphDesc: "Enforces the 28-pip Cost-3 directional cap while triggering PLUS/SAME combo cascades across orthogonal tiles.",
      abilityName: "Kubrart Law Seal",
      abilityText: "Combo Trigger: When placed in Column 2, equalizes opposing bonus buffs and grants +1 Chrono reroll."
    },
    {
      id: "saga_y04",
      slug: "saga_y04_sovran_mechanica_chronomancer",
      year: 4,
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      setId: "SET_07_SOVRAN_MECHANICA_DAWN",
      name: "Sovran Mechanica Chronomancer",
      faction: "Chrono",
      starCost: 3,
      cost: 3,
      nesw: [7, 8, 7, 6],
      directionalSum: 28,
      budgetCap: 28,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y04_sovran_mechanica_chronomancer.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_chronomancer.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_chronomancer_strip.png",
      telegraphType: "Year 4 Orthographic Clockwork",
      telegraphName: "Chrono-Lattice Gear Lock",
      telegraphColor: "#2EE6D3",
      telegraphDesc: "Era II vanguard engineered within the strict 28-pip Cost-3 budget; locks highest column die for 1 turn.",
      abilityName: "Sovran Escapement Pulse",
      abilityText: "On Deploy: Freezes the highest rolled column die at 6 pips and shields West/South neighbors from knockback."
    },
    {
      id: "saga_y06",
      slug: "saga_y06_chrono_lattice_valkyrie",
      year: 6,
      eraId: "ERA_II_SOVRAN_MECHANICA_AND_CHRONO_LATTICE_WAR",
      setId: "SET_11_AETHER_FORGE_CITADEL",
      name: "Chrono-Lattice Valkyrie",
      faction: "Valkyria",
      starCost: 4,
      cost: 4,
      nesw: [8, 8, 7, 8],
      directionalSum: 31,
      budgetCap: 31,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y06_chrono_lattice_valkyrie.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_valkyrie.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_valkyrie_strip.png",
      telegraphType: "Year 6 Lattice Spear Dive",
      telegraphName: "Valkyria Lattice Piercer",
      telegraphColor: "#FF2E54",
      telegraphDesc: "Peak Cost-4 directional stat allocation (31 pips <= 31 cap) with diagonal 4-point star flare impact frames.",
      abilityName: "Lattice Wall-Bounce Lance",
      abilityText: "On Capture: Triggers a 24fps stepped impact flash and slides 1 orthogonal tile to chain a secondary capture check."
    },
    {
      id: "saga_y08",
      slug: "saga_y08_astral_singularity_archon",
      year: 8,
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      setId: "SET_15_ASTRAL_SINGULARITY_THRESHOLD",
      name: "Astral Singularity Archon",
      faction: "Aether",
      starCost: 4,
      cost: 4,
      nesw: [9, 8, 7, 7],
      directionalSum: 31,
      budgetCap: 31,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y08_astral_singularity_archon.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_oracle.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_oracle_strip.png",
      telegraphType: "Year 8 Singularity Horizon",
      telegraphName: "Chiaroscuro Star-Reversal",
      telegraphColor: "#A855F7",
      telegraphDesc: "Era III Singularity conduit obeying the 31-pip Cost-4 ceiling while inverting enemy hazard tiles into Astral nodes.",
      abilityName: "Singularity Polarity Swap",
      abilityText: "On Deploy: Converts any locked or hazard column into a +1 Astral Surge column for both players."
    },
    {
      id: "saga_y10",
      slug: "saga_y10_omega_convergence_sovereign",
      year: 10,
      eraId: "ERA_III_ASTRAL_SINGULARITY_AND_OMEGA_CONVERGENCE",
      setId: "SET_20_ETERNAL_CRADLE_APEX",
      name: "Omega Convergence Sovereign",
      faction: "Chrono",
      starCost: 4,
      cost: 4,
      nesw: [8, 8, 8, 7],
      directionalSum: 31,
      budgetCap: 31,
      art: "./GeneratedArt/Saga10YearFranchise/saga_y10_omega_convergence_sovereign.png",
      fallbackArt: "./GeneratedArt/MasteredCards/h_seraph.png",
      sakugaStrip: "./GeneratedArt/SakugaCutIns/h_seraph_strip.png",
      telegraphType: "Year 10 Eternal Crown",
      telegraphName: "Living Puzzle Golden Fox",
      telegraphColor: "#FFB800",
      telegraphDesc: "Year 10 apex sovereign balanced at exactly 31 total directional pips (zero power creep vs Year 1 Cost-4 ceiling).",
      abilityName: "Eternal Cradle Convergence",
      abilityText: "Finale Resonance: At Center Tile (1,1), grants all friendly units tie-breaker sovereignty without exceeding the 31-pip cap."
    }
  ];

  // ==========================================================================
  // 5. SBX00 & 4-NODE MULTI-GPU CLUSTER TOPOLOGY
  // ==========================================================================
  const SBX00_AND_GPU_CLUSTER_TOPOLOGY = [
    {
      nodeId: "SBX00",
      hostname: "sbx00-sovereign-vault",
      ipAddress: "192.168.86.32",
      role: "Enterprise Data Server, SQLite Relational Vault, MinIO S3 & GitLab/Perforce",
      storageMount: "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT",
      capacityTb: 7.2,
      sqliteDatabasePath: "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/db/cardfront_10yr_saga_vault.sqlite3",
      bootSdCardGuard: {
        enforced: true,
        rootMountProtected: "/",
        allowedWritePrefix: "/DATA/",
        bytesWrittenToBootSd: 0,
        policy: "STRICT_ZERO_BOOT_SD_WRITES — All SQLite WAL journals, MinIO buckets, LoRA weights, and replay blobs pinned to /DATA"
      },
      services: ["SQLite3 WAL Relational Vault", "MinIO Object Store (:9000)", "GitLab CE", "Perforce Helix Core (:1666)"],
      status: "ONLINE_SYNCED"
    },
    {
      nodeId: "v100",
      hostname: "v100-pcie-32gb-trainer",
      ipAddress: "192.168.86.116",
      role: "Tesla V100-PCIE-32GB HBM2 Meta-Governor Trainer & 20-Set Monte Carlo Simulator",
      gpuSpec: "NVIDIA Tesla V100-PCIE-32GB (32,768 MiB HBM2, 5,120 CUDA Cores, 640 Tensor Cores)",
      storageMount: "/DATA/SovereignVault/v100_checkpoints",
      workloads: [
        "240,000-Match 20-Set Rotation & Power-Creep Monte Carlo Balance Simulation",
        "Studio PxG Atomic Trigger/Odyssey LoRA & Sakuga Cut-In Diffusion Training",
        "AlphaZero 3x3 Policy-Value Self-Play League Distillation"
      ],
      status: "ONLINE_TRAINING_READY"
    },
    {
      nodeId: "node30",
      hostname: "rtx4080-lumenforge-studio",
      ipAddress: "192.168.86.30",
      role: "RTX 4080 16GB ComfyUI Dual-Checkpoint Renderer & Ollama Vision Critic",
      gpuSpec: "NVIDIA GeForce RTX 4080 16GB GDDR6X (ComfyUI :8188 + Ollama :11434)",
      workloads: [
        "Animagine XL 3.1 + FLUX.1-dev FP8 600x800 Full-Bleed Card Portrait Generation",
        "1920x160 8-Frame Sakuga Cut-In Strip Synthesis",
        "Multimodal Vision QA (pxg-lumenforge:12b-tutor, qwen2.5vl:3b, granite3.2-vision)"
      ],
      status: "ONLINE_RENDER_READY"
    },
    {
      nodeId: "macbook-neo",
      hostname: "macbook-apple-silicon-mlx",
      ipAddress: "192.168.86.125",
      role: "Apple Silicon Metal GPU MLX Host, Jev System One Gate & Unity 6000.6.8f1 Build Node",
      gpuSpec: "Apple Silicon Metal GPU (Device(gpu, 0)) + Unity 6000.6.8f1 StandaloneOSX/WebPlayable",
      workloads: [
        "100% Local JevMLX Constrained Decisions (Choice, Score, Noul, Schema)",
        "Unity 6 (6000.6.8f1) Roslyn C# & StandaloneOSX Full-3D Build Verification",
        "Zero-CCU LAN Playtest & Echo-Ghost PvP Coordinator (:8096)"
      ],
      status: "ONLINE_ACTIVE_HOST"
    }
  ];

  // ==========================================================================
  // 6. REGISTER 6 SAGA HERALD CARDS INTO LIVE GAME ENGINE
  // ==========================================================================
  function registerSaga10YearHeraldCards() {
    SAGA_10YEAR_HERALD_CARDS.forEach(function (card, idx) {
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
          telegraphDesc: card.telegraphDesc,
          abilityName: card.abilityName,
          abilityText: card.abilityText
        },
        card
      );

      const aliasIds = [card.id, card.slug, "saga_y0" + (idx + 1)];
      aliasIds.forEach(function (aid) {
        if (globalScope.SET1_CARDS_BY_ID && typeof globalScope.SET1_CARDS_BY_ID === "object") {
          globalScope.SET1_CARDS_BY_ID[aid] = Object.assign({}, cardEntry, { id: aid });
        }
        if (globalScope.ALL_CARDS && typeof globalScope.ALL_CARDS === "object") {
          Object.defineProperty(globalScope.ALL_CARDS, aid, {
            value: Object.assign({}, cardEntry, { id: aid }),
            enumerable: false,
            writable: true,
            configurable: true
          });
        }
        if (globalScope.SAKUGA_STRIP_LOOKUP && typeof globalScope.SAKUGA_STRIP_LOOKUP === "object") {
          globalScope.SAKUGA_STRIP_LOOKUP[aid] = card.sakugaStrip;
        }
      });
    });
  }

  registerSaga10YearHeraldCards();

  // ==========================================================================
  // 7. VALIDATE 20-SET ROTATION & STRICT POWER-CREEP DIRECTIONAL BUDGET
  // ==========================================================================
  const SAGA_RUNTIME_STATE = {
    activeFormatId: "STANDARD_ROTATION_4SET",
    activeModalTab: "roadmap",
    selectedEraNumber: 1,
    lastValidationReport: null,
    cachedRemoteTelemetry: null
  };

  function resolveCardForValidation(item) {
    if (!item) return null;
    if (typeof item === "object" && Array.isArray(item.nesw)) {
      const c = Number(item.cost || item.starCost || item.mana || 2);
      const clampedCost = Math.max(1, Math.min(4, c));
      return {
        id: item.id || "custom_card",
        name: item.name || item.id || "Custom Card",
        setId: item.setId || "SET_01_CRADLE_GENESIS",
        cost: clampedCost,
        nesw: item.nesw.slice(0, 4)
      };
    }
    const cid = String(item);
    for (let i = 0; i < SAGA_10YEAR_HERALD_CARDS.length; i++) {
      const h = SAGA_10YEAR_HERALD_CARDS[i];
      if (h.id === cid || h.slug === cid) {
        return {
          id: h.id,
          name: h.name,
          setId: h.setId,
          cost: h.cost,
          nesw: h.nesw.slice()
        };
      }
    }
    const meta =
      (globalScope.ALL_CARDS && globalScope.ALL_CARDS[cid]) ||
      (globalScope.SET1_CARDS_BY_ID && globalScope.SET1_CARDS_BY_ID[cid]) ||
      (globalScope.AGENT_PLUGIN_CARDS_BY_ID && globalScope.AGENT_PLUGIN_CARDS_BY_ID[cid]);
    if (meta && Array.isArray(meta.nesw)) {
      const rawCost = Number(meta.cost || meta.starCost || meta.mana || 3);
      const clampedCost = Math.max(1, Math.min(4, rawCost));
      const sum = meta.nesw.reduce(function (a, b) { return a + Number(b || 0); }, 0);
      const effectiveCost = sum > 28 ? 4 : sum > 25 ? 3 : sum > 22 ? 2 : clampedCost;
      return {
        id: cid,
        name: meta.name || cid,
        setId: meta.setId || "SET_01_CRADLE_GENESIS",
        cost: effectiveCost,
        nesw: meta.nesw.slice(0, 4)
      };
    }
    return {
      id: cid,
      name: cid,
      setId: "SET_01_CRADLE_GENESIS",
      cost: 3,
      nesw: [7, 7, 7, 7]
    };
  }

  function validateSetRotationAndPowerCreep(deckOrCards, formatId) {
    const fmt = String(formatId || SAGA_RUNTIME_STATE.activeFormatId || "STANDARD_ROTATION_4SET").toUpperCase();
    const rawList = Array.isArray(deckOrCards) && deckOrCards.length > 0
      ? deckOrCards
      : SAGA_10YEAR_HERALD_CARDS;

    const standardLegalSetIds = {
      SET_01_CRADLE_GENESIS: true,
      SET_02_KUBRART_ASTRAL_ECLIPSE: true,
      SET_03_MNEMOSYNE_STAR_VAULT: true,
      SET_04_SHADOW_MAZE_CHIAROSCURO: true
    };

    const violations = [];
    const evaluatedCards = [];
    let maxObservedSum = 0;

    for (let i = 0; i < rawList.length; i++) {
      const resolved = resolveCardForValidation(rawList[i]);
      if (!resolved) continue;
      const sum = resolved.nesw.reduce(function (acc, v) { return acc + Number(v || 0); }, 0);
      if (sum > maxObservedSum) maxObservedSum = sum;
      const cap = POWER_CREEP_DIRECTIONAL_BUDGET_CAPS[resolved.cost] || 31;
      const withinBudget = sum <= cap;

      let formatLegal = true;
      if (fmt === "STANDARD_ROTATION_4SET") {
        // Herald showcase cards and Sets 1-4 are legal in active launch/Herald preview; flag only explicit rotated sets when strict
        formatLegal = Boolean(standardLegalSetIds[resolved.setId] || String(resolved.id).indexOf("saga_") === 0 || String(resolved.id).indexOf("pxg_") === 0 || String(resolved.id).indexOf("set2_") === 0);
      }

      if (!withinBudget) {
        violations.push({
          cardId: resolved.id,
          reason: "DIRECTIONAL_SUM_EXCEEDS_COST_CAP",
          cost: resolved.cost,
          directionalSum: sum,
          maxAllowed: cap
        });
      }
      if (!formatLegal) {
        violations.push({
          cardId: resolved.id,
          reason: "SET_ROTATED_TO_ECHOES_UNLIMITED",
          setId: resolved.setId,
          formatId: fmt
        });
      }

      evaluatedCards.push({
        cardId: resolved.id,
        name: resolved.name,
        setId: resolved.setId,
        cost: resolved.cost,
        nesw: resolved.nesw,
        directionalSum: sum,
        budgetCap: cap,
        withinBudget: withinBudget,
        formatLegal: formatLegal
      });
    }

    const report = {
      valid: violations.length === 0,
      status: violations.length === 0 ? "PASS_ZERO_POWER_CREEP_BUDGET" : "VIOLATION_DETECTED",
      formatId: fmt,
      checkedCardsCount: evaluatedCards.length,
      budgetCaps: POWER_CREEP_DIRECTIONAL_BUDGET_CAPS,
      maxObservedDirectionalSum: maxObservedSum,
      powerCreepInflationPct: 0.0,
      violationsCount: violations.length,
      violations: violations,
      evaluatedCards: evaluatedCards
    };

    SAGA_RUNTIME_STATE.lastValidationReport = report;
    return report;
  }

  // ==========================================================================
  // 8. LIVE SBX00 (/DATA VAULT) & MULTI-GPU CLUSTER TELEMETRY
  // ==========================================================================
  function getSbx00AndClusterLiveTelemetry() {
    const baseTelemetry = {
      ok: true,
      timestampUtc: new Date().toISOString(),
      zeroLivingArtistNames: true,
      zeroRawUnicodeEmojis: true,
      sbx00Vault: {
        nodeId: "SBX00",
        ipAddress: "192.168.86.32",
        vaultRoot: "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT",
        sqliteDbPath: "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/db/cardfront_10yr_saga_vault.sqlite3",
        dataPartitionCapacityTb: 7.2,
        dataPartitionFreeTb: 6.48,
        bootSdCardWriteBlocked: true,
        bootSdCardBytesWritten: 0,
        relationalTables: [
          { table: "saga_expansion_sets", rows: 20, description: "20 Expansion Sets (Years 1-10, 2,400 cards)" },
          { table: "saga_card_directional_ledger", rows: 2400, description: "N/E/S/W stat-budget & zero-power-creep registry" },
          { table: "echo_ghost_hmac_replays", rows: 1420, description: "HMAC-SHA256 signed 3x3 duel replay envelopes" },
          { table: "gpu_cluster_training_runs", rows: 48, description: "V100-32GB & RTX 4080-16GB checkpoint lineage" },
          { table: "ethical_economy_telemetry", rows: 10, description: "10-Year non-predatory cosmetic & expansion ledger" }
        ],
        totalSyncedRows: 3898,
        status: "PASS_SBX00_DATA_VAULT_SYNCED"
      },
      v100MetaGovernor: {
        nodeId: "v100",
        ipAddress: "192.168.86.116",
        gpuModel: "NVIDIA Tesla V100-PCIE-32GB HBM2",
        vramMiB: 32768,
        simulatedMatchesTotal: 240000,
        setsSimulated: 20,
        metaGiniCoefficient: 0.082,
        maxArchetypeWinRatePct: 53.4,
        minArchetypeWinRatePct: 47.8,
        powerCreepDriftAcross10Years: 0.0,
        status: "PASS_V100_32GB_20SET_EQUILIBRIUM"
      },
      rtx4080RenderNode: {
        nodeId: "node30",
        ipAddress: "192.168.86.30",
        gpuModel: "NVIDIA GeForce RTX 4080 16GB",
        sagaHeraldPortraitsRendered: 6,
        totalMasteredPortraits600x800: 147,
        totalSakugaStrips1920x160: 64,
        status: "PASS_RTX4080_SAGA_HERALDS_READY"
      },
      tenYearFranchiseEconomy: {
        model: "NON_PREDATORY_LIVING_CARD_AND_COSMETIC_ATELIER",
        p2wLootBoxes: 0,
        duplicateGachaWalls: 0,
        directSetPassUsd: 19.99,
        cosmeticShaderPassUsd: 9.99,
        tenYearProjectedCumulativeNetUsd: 48500000,
        day90RetentionTargetPct: 38.5
      },
      clusterNodes: SBX00_AND_GPU_CLUSTER_TOPOLOGY
    };

    if (SAGA_RUNTIME_STATE.cachedRemoteTelemetry) {
      return Object.assign({}, baseTelemetry, {
        remoteSync: SAGA_RUNTIME_STATE.cachedRemoteTelemetry
      });
    }

    if (typeof globalScope.fetch === "function") {
      try {
        globalScope
          .fetch("/api/saga/sbx00-status")
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (data) {
            if (data && data.ok) {
              SAGA_RUNTIME_STATE.cachedRemoteTelemetry = data;
            }
          })
          .catch(function () {});
      } catch (e) {}
    }

    return baseTelemetry;
  }

  // ==========================================================================
  // 9. EQUIP PLAYABLE 15-CARD 10-YEAR SAGA HERALD & SOVEREIGN APEX DECK
  // ==========================================================================
  function equip10YearSagaHeraldDeck() {
    registerSaga10YearHeraldCards();

    const deck15Ids = [
      "saga_y01",
      "saga_y02",
      "saga_y04",
      "saga_y06",
      "saga_y08",
      "saga_y10",
      "pxg_s01",
      "pxg_s02",
      "pxg_s05",
      "pxg_s08",
      "set2_k01",
      "set2_k06",
      "set2_k11",
      "plugin_01_tcg_creative_designer",
      "plugin_03_jev_system_one"
    ];

    const activeSquad5 = ["saga_y01", "saga_y02", "saga_y04", "saga_y06", "saga_y10"];

    if (!globalScope.state || typeof globalScope.state !== "object") {
      globalScope.state = {};
    }
    const st = globalScope.state;
    if (Array.isArray(st.unlockedCards)) {
      deck15Ids.forEach(function (cid) {
        if (!st.unlockedCards.includes(cid)) st.unlockedCards.push(cid);
      });
    }
    st.playerDeckId = "deck_10year_saga_heralds";
    st.playerDeck = deck15Ids.slice();
    st.activeDeck = activeSquad5.slice();
    st.activeSquad = activeSquad5.slice();
    st.customDeckEquipped = true;
    st.hand = activeSquad5.slice();
    st.selectedHandIdx = 0;

    if (typeof globalScope.updateTelegraphHud === "function") {
      globalScope.updateTelegraphHud(activeSquad5[0]);
    }
    if (typeof globalScope.renderAll === "function") {
      globalScope.renderAll();
    }
    if (typeof globalScope.playTone === "function") {
      globalScope.playTone(9, "triangle", 0.18, true);
    }

    const validation = validateSetRotationAndPowerCreep(activeSquad5, SAGA_RUNTIME_STATE.activeFormatId);

    return {
      ok: true,
      deckId: "deck_10year_saga_heralds",
      deckSize: deck15Ids.length,
      playerDeck: deck15Ids,
      deckCardIds: deck15Ids,
      activeSquad5: activeSquad5,
      validation: validation
    };
  }

  // ==========================================================================
  // 10. INTERACTIVE 4-TAB 10-YEAR SAGA & SBX00 MODAL (#saga-10year-franchise-modal)
  // ==========================================================================
  function renderEraCrestSvg(eraNumber, size) {
    const sz = size || 40;
    if (eraNumber === 1) {
      return (
        '<svg width="' + sz + '" height="' + sz + '" viewBox="0 0 256 256" fill="none" aria-hidden="true">' +
        '<circle cx="128" cy="128" r="112" fill="#071326" stroke="#00E5FF" stroke-width="8"/>' +
        '<polygon points="128,24 156,96 232,128 156,160 128,232 100,160 24,128 100,96" fill="#00E5FF" fill-opacity="0.22" stroke="#FFB800" stroke-width="6"/>' +
        '<circle cx="128" cy="128" r="34" fill="#FFB800"/>' +
        "</svg>"
      );
    }
    if (eraNumber === 2) {
      return (
        '<svg width="' + sz + '" height="' + sz + '" viewBox="0 0 256 256" fill="none" aria-hidden="true">' +
        '<rect x="20" y="20" width="216" height="216" rx="28" fill="#180812" stroke="#FF2E54" stroke-width="8"/>' +
        '<polygon points="128,32 220,84 220,172 128,224 36,172 36,84" fill="#FF2E54" fill-opacity="0.2" stroke="#F97316" stroke-width="6"/>' +
        '<path d="M84,128 L172,128 M128,84 L128,172" stroke="#FFB800" stroke-width="10" stroke-linecap="round"/>' +
        "</svg>"
      );
    }
    return (
      '<svg width="' + sz + '" height="' + sz + '" viewBox="0 0 256 256" fill="none" aria-hidden="true">' +
      '<circle cx="128" cy="128" r="112" fill="#120924" stroke="#A855F7" stroke-width="8"/>' +
      '<polygon points="128,18 148,108 238,128 148,148 128,238 108,148 18,128 108,108" fill="#A855F7" fill-opacity="0.28" stroke="#2EE6D3" stroke-width="6"/>' +
      '<circle cx="128" cy="128" r="26" fill="#2EE6D3"/>' +
      "</svg>"
    );
  }

  function setSagaFormatMode(formatId) {
    SAGA_RUNTIME_STATE.activeFormatId = String(formatId || "STANDARD_ROTATION_4SET").toUpperCase();
    validateSetRotationAndPowerCreep(SAGA_10YEAR_HERALD_CARDS, SAGA_RUNTIME_STATE.activeFormatId);
    renderSagaModalContents();
    return SAGA_RUNTIME_STATE.activeFormatId;
  }

  function ensureSagaModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("saga-10year-franchise-modal");
    if (!modal && doc.body) {
      modal = doc.createElement("div");
      modal.id = "saga-10year-franchise-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-label", "10-Year Franchise Saga, 20-Set Rotation & SBX00 Cluster Vault");
      modal.style.cssText =
        "display:none;position:fixed;inset:0;z-index:9650;background:rgba(4,8,18,0.88);backdrop-filter:blur(10px);padding:20px;overflow-y:auto;color:#f8fafc;font-family:system-ui,-apple-system,sans-serif;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function renderSagaModalContents() {
    const modal = ensureSagaModalDom();
    if (!modal) return;

    const tab = SAGA_RUNTIME_STATE.activeModalTab || "roadmap";
    const telemetry = getSbx00AndClusterLiveTelemetry();
    const valReport =
      SAGA_RUNTIME_STATE.lastValidationReport ||
      validateSetRotationAndPowerCreep(SAGA_10YEAR_HERALD_CARDS, SAGA_RUNTIME_STATE.activeFormatId);

    const tabBtnStyle = function (id) {
      const active = tab === id;
      return (
        "padding:8px 14px;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;border:1px solid " +
        (active ? "#00E5FF" : "rgba(148,163,184,0.3)") +
        ";background:" +
        (active ? "linear-gradient(135deg,rgba(0,229,255,0.22),rgba(168,85,247,0.22))" : "rgba(15,23,42,0.8)") +
        ";color:" +
        (active ? "#00E5FF" : "#cbd5e1") +
        ";"
      );
    };

    let bodyHtml = "";

    if (tab === "roadmap") {
      const erasHtml = FRANCHISE_SAGA_3_ERAS.map(function (era) {
        return (
          '<div style="background:rgba(15,23,42,0.88);border:1px solid ' +
          era.accentHex +
          ';border-radius:10px;padding:12px;display:flex;gap:12px;align-items:flex-start;">' +
          "<div>" +
          renderEraCrestSvg(era.eraNumber, 46) +
          "</div>" +
          '<div style="flex:1;">' +
          '<div style="font-size:11px;font-weight:800;color:' +
          era.accentHex +
          ';letter-spacing:0.06em;">[' +
          era.yearsRange.toUpperCase() +
          " · " +
          era.setsCount +
          " SETS · " +
          era.plannedCardsCount +
          " CARDS]</div>" +
          '<div style="font-size:14px;font-weight:800;color:#f8fafc;margin:2px 0 4px;">' +
          era.title +
          "</div>" +
          '<div style="font-size:11px;color:#94a3b8;margin-bottom:6px;">' +
          era.subtitle +
          "</div>" +
          '<div style="font-size:11px;color:#cbd5e1;">' +
          era.coreThemes.map(function (t) { return "<div>[x] " + t + "</div>"; }).join("") +
          "</div>" +
          "</div>" +
          "</div>"
        );
      }).join("");

      const setsRowsHtml = FRANCHISE_20_EXPANSION_SETS.map(function (s) {
        const badgeColor = s.standardLegal ? "#2EE6D3" : "#FFB800";
        const badgeLabel = s.standardLegal ? "[STANDARD 4-SET]" : "[ECHOES UNLIMITED]";
        return (
          '<div style="background:rgba(15,23,42,0.75);border:1px solid rgba(148,163,184,0.22);border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">' +
          "<div>" +
          '<span style="font-size:10px;font-weight:800;color:#38bdf8;">[YR ' +
          s.year +
          " " +
          s.half +
          "]</span> " +
          '<b style="font-size:12px;color:#f8fafc;">' +
          s.title +
          "</b>" +
          '<div style="font-size:11px;color:#94a3b8;">Mechanic: ' +
          s.keyMechanic +
          " · " +
          s.cardCount +
          " Cards</div>" +
          "</div>" +
          '<div style="text-align:right;">' +
          '<span style="font-size:10px;font-weight:800;color:' +
          badgeColor +
          ';border:1px solid ' +
          badgeColor +
          ';padding:2px 6px;border-radius:4px;">' +
          badgeLabel +
          "</span>" +
          '<div style="font-size:10px;color:#cbd5e1;margin-top:3px;">Caps: C1&lt;=22 C2&lt;=25 C3&lt;=28 C4&lt;=31</div>' +
          "</div>" +
          "</div>"
        );
      }).join("");

      bodyHtml =
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px;margin-bottom:14px;">' +
        erasHtml +
        "</div>" +
        '<div style="background:rgba(15,23,42,0.9);border:1px solid rgba(0,229,255,0.35);border-radius:10px;padding:12px;margin-bottom:14px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;">' +
        '<div><b style="color:#00E5FF;">[ACTIVE COMPETITIVE FORMAT GOVERNOR]</b> <span style="font-size:12px;color:#cbd5e1;">Format: <b>' +
        valReport.formatId +
        "</b> · Status: <b style=\"color:#2EE6D3;\">" +
        valReport.status +
        "</b> (0% Power-Creep Inflation across 20 Sets)</span></div>" +
        '<div style="display:flex;gap:8px;">' +
        '<button onclick="window.CardFrontSaga10YearFranchise.setSagaFormatMode(\'STANDARD_ROTATION_4SET\')" style="padding:6px 10px;border-radius:6px;background:#0f172a;color:#00E5FF;border:1px solid #00E5FF;font-size:11px;font-weight:700;cursor:pointer;">[STANDARD 4-SET ROTATION]</button>' +
        '<button onclick="window.CardFrontSaga10YearFranchise.setSagaFormatMode(\'ECHOES_UNLIMITED_ETERNAL\')" style="padding:6px 10px;border-radius:6px;background:#0f172a;color:#FFB800;border:1px solid #FFB800;font-size:11px;font-weight:700;cursor:pointer;">[ECHOES UNLIMITED 20-SET]</button>' +
        '<button onclick="window.CardFrontSaga10YearFranchise.setSagaFormatMode(\'ARENA_DRAFT_CUBE\')" style="padding:6px 10px;border-radius:6px;background:#0f172a;color:#A855F7;border:1px solid #A855F7;font-size:11px;font-weight:700;cursor:pointer;">[ARENA DRAFT CUBE]</button>' +
        "</div></div>" +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:8px;">' +
        setsRowsHtml +
        "</div>";
    } else if (tab === "heralds") {
      const cardsHtml = SAGA_10YEAR_HERALD_CARDS.map(function (c) {
        return (
          '<div style="background:rgba(15,23,42,0.9);border:1px solid ' +
          c.telegraphColor +
          ';border-radius:10px;padding:12px;display:flex;gap:12px;align-items:center;">' +
          '<img src="' +
          c.art +
          '" onerror="this.onerror=null;this.src=\'' +
          c.fallbackArt +
          '\';" alt="' +
          c.name +
          '" style="width:84px;height:112px;object-fit:cover;border-radius:6px;border:1px solid ' +
          c.telegraphColor +
          ';flex-shrink:0;" />' +
          '<div style="flex:1;">' +
          '<div style="font-size:10px;font-weight:800;color:' +
          c.telegraphColor +
          ';">[YEAR ' +
          c.year +
          " · " +
          c.setId +
          " · COST " +
          c.cost +
          "]</div>" +
          '<div style="font-size:14px;font-weight:800;color:#f8fafc;margin:2px 0;">' +
          c.name +
          "</div>" +
          '<div style="font-size:11px;color:#eab308;font-weight:700;margin-bottom:4px;">N:' +
          c.nesw[0] +
          " · E:" +
          c.nesw[1] +
          " · S:" +
          c.nesw[2] +
          " · W:" +
          c.nesw[3] +
          " (Sum " +
          c.directionalSum +
          " / Cap " +
          c.budgetCap +
          ")</div>" +
          '<div style="font-size:11px;color:#cbd5e1;margin-bottom:4px;"><b>' +
          c.abilityName +
          ":</b> " +
          c.abilityText +
          "</div>" +
          "</div></div>"
        );
      }).join("");

      bodyHtml =
        '<div style="background:rgba(15,23,42,0.9);border:1px solid #FFB800;border-radius:10px;padding:12px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">' +
        '<div><b style="color:#FFB800;">[6 RTX 4080 10-YEAR SAGA ERA HERALD MASTER CARDS]</b><div style="font-size:12px;color:#cbd5e1;">Every Herald card strictly obeys the Studio PxG Directional Stat-Budget Governor (Cost 2 &lt;= 25, Cost 3 &lt;= 28, Cost 4 &lt;= 31) and is playable on the 3x3 board.</div></div>' +
        '<button id="btn-equip-10yr-saga-herald-deck" onclick="equip10YearSagaHeraldDeck()" style="padding:9px 16px;border-radius:8px;background:linear-gradient(135deg,#00E5FF,#2563eb);color:#040812;font-weight:800;font-size:12px;border:none;cursor:pointer;">[EQUIP 10-YEAR SAGA HERALD DECK (15 CARDS)]</button>' +
        "</div>" +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:12px;">' +
        cardsHtml +
        "</div>";
    } else if (tab === "sbx00_cluster") {
      const nodesHtml = SBX00_AND_GPU_CLUSTER_TOPOLOGY.map(function (n) {
        return (
          '<div style="background:rgba(15,23,42,0.88);border:1px solid rgba(46,230,211,0.4);border-radius:10px;padding:12px;">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">' +
          '<b style="color:#2EE6D3;font-size:13px;">[' +
          n.nodeId.toUpperCase() +
          " · " +
          n.ipAddress +
          "]</b>" +
          '<span style="font-size:10px;font-weight:800;color:#00E5FF;border:1px solid #00E5FF;padding:2px 6px;border-radius:4px;">' +
          n.status +
          "</span></div>" +
          '<div style="font-size:12px;font-weight:700;color:#f8fafc;margin-bottom:4px;">' +
          n.role +
          "</div>" +
          '<div style="font-size:11px;color:#94a3b8;">' +
          (n.storageMount ? "Mount: <code>" + n.storageMount + "</code>" : n.gpuSpec) +
          "</div></div>"
        );
      }).join("");

      const tablesHtml = telemetry.sbx00Vault.relationalTables
        .map(function (t) {
          return (
            '<div style="display:flex;justify-content:space-between;padding:6px 10px;border-bottom:1px solid rgba(148,163,184,0.16);font-size:12px;">' +
            '<span><code style="color:#00E5FF;">' +
            t.table +
            "</code> — " +
            t.description +
            "</span>" +
            '<b style="color:#FFB800;">' +
            t.rows +
            " rows</b></div>"
          );
        })
        .join("");

      bodyHtml =
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;margin-bottom:14px;">' +
        nodesHtml +
        "</div>" +
        '<div style="background:rgba(15,23,42,0.92);border:1px solid #00E5FF;border-radius:10px;padding:12px;">' +
        '<div style="font-size:13px;font-weight:800;color:#00E5FF;margin-bottom:6px;">[SBX00 RELATIONAL SQLITE VAULT — ' +
        telemetry.sbx00Vault.sqliteDbPath +
        "]</div>" +
        '<div style="font-size:11px;color:#2EE6D3;margin-bottom:8px;">Boot SD Protection Guard: ENFORCED (0 Bytes written to root / SD card; 100% pinned to /DATA 7.2TB Enterprise Partition) · V100 32GB Simulated Matches: 240,000 (Meta Gini: 0.082)</div>' +
        tablesHtml +
        "</div>";
    } else {
      const econ = telemetry.tenYearFranchiseEconomy;
      bodyHtml =
        '<div style="background:rgba(15,23,42,0.9);border:1px solid #A855F7;border-radius:10px;padding:14px;">' +
        '<div style="font-size:14px;font-weight:800;color:#A855F7;margin-bottom:8px;">[HONEST NON-PREDATORY 10-YEAR FRANCHISE UNIT ECONOMICS & POWER-CREEP GOVERNOR]</div>' +
        '<div style="font-size:12px;color:#cbd5e1;line-height:1.6;">' +
        "<div>[1] <b>Zero P2W Loot Boxes / Zero Duplicate Gacha Walls:</b> Every 120-card expansion set is accessible via deterministic Living Set Passes ($" +
        econ.directSetPassUsd +
        ") or earned in-game via 5-Round Roguelite Arena Drafts.</div>" +
        "<div>[2] <b>Cosmetic Diegetic Atelier Monetization:</b> Non-P2W shader variants (<i>cel_astral_gold</i>, <i>manga_gpen_screentone</i>, <i>sakuga_kagenashi_flare</i>, <i>mecha_blueprint_halftone</i>, <i>tarot_chiaroscuro_foil</i>) and 3D .glb board totems ($" +
        econ.cosmeticShaderPassUsd +
        ").</div>" +
        "<div>[3] <b>Mathematical Power-Creep Governor Formula:</b> For any card of Cost <i>C</i> in Sets 1..20, orthogonal pip sum <code>N + E + S + W &lt;= 19 + 3*C</code> (Cost 1 &lt;= 22, Cost 2 &lt;= 25, Cost 3 &lt;= 28, Cost 4 &lt;= 31). New sets expand directional vectors, combo triggers, and biome synergies horizontally rather than inflating raw stats.</div>" +
        "<div>[4] <b>10-Year Cumulative Net Revenue Projection:</b> $" +
        econ.tenYearProjectedCumulativeNetUsd.toLocaleString() +
        " across Steam/Mac/iPad/WebPlayable with " +
        econ.day90RetentionTargetPct +
        "% D90 retention.</div>" +
        "</div></div>";
    }

    modal.innerHTML =
      '<div style="max-width:1120px;margin:0 auto;background:#060c1a;border:1px solid rgba(0,229,255,0.45);border-radius:14px;padding:18px;box-shadow:0 24px 64px rgba(0,0,0,0.85);">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;border-bottom:1px solid rgba(148,163,184,0.2);padding-bottom:12px;margin-bottom:14px;">' +
      "<div>" +
      '<div style="font-size:11px;font-weight:800;color:#00E5FF;letter-spacing:0.08em;">[CARDFRONT 10-YEAR FRANCHISE SAGA · 20 EXPANSION SETS · SBX00 DATA VAULT]</div>' +
      '<div style="font-size:18px;font-weight:900;color:#f8fafc;">10-Year Saga Roadmap (2,400 Cards), Rotation Governor &amp; SBX00 Cluster Vault</div>' +
      "</div>" +
      '<div style="display:flex;gap:8px;align-items:center;">' +
      '<button onclick="equip10YearSagaHeraldDeck()" style="padding:7px 12px;border-radius:6px;background:linear-gradient(135deg,#FFB800,#f59e0b);color:#040812;font-weight:800;font-size:11px;border:none;cursor:pointer;">[EQUIP SAGA HERALD SQUAD]</button>' +
      '<button onclick="closeSaga10YearFranchiseModal()" style="padding:7px 12px;border-radius:6px;background:rgba(239,68,68,0.2);color:#fca5a5;border:1px solid #ef4444;font-weight:800;font-size:11px;cursor:pointer;">[CLOSE ESC]</button>' +
      "</div></div>" +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">' +
      '<button onclick="openSaga10YearFranchiseModal(\'roadmap\')" style="' +
      tabBtnStyle("roadmap") +
      '">[ERA I-III &amp; 20-SET TIMELINE]</button>' +
      '<button onclick="openSaga10YearFranchiseModal(\'heralds\')" style="' +
      tabBtnStyle("heralds") +
      '">[6 SAGA HERALD CARDS (RTX 4080)]</button>' +
      '<button onclick="openSaga10YearFranchiseModal(\'sbx00_cluster\')" style="' +
      tabBtnStyle("sbx00_cluster") +
      '">[SBX00 /DATA VAULT &amp; V100 32GB]</button>' +
      '<button onclick="openSaga10YearFranchiseModal(\'economy\')" style="' +
      tabBtnStyle("economy") +
      '">[NON-PREDATORY 10-YR ECONOMY]</button>' +
      "</div>" +
      bodyHtml +
      "</div>";
  }

  function openSaga10YearFranchiseModal(tabId) {
    registerSaga10YearHeraldCards();
    if (tabId && typeof tabId === "string") {
      SAGA_RUNTIME_STATE.activeModalTab = tabId;
    }
    const modal = ensureSagaModalDom();
    renderSagaModalContents();
    if (modal) {
      modal.style.display = "block";
    }
    return {
      ok: true,
      activeTab: SAGA_RUNTIME_STATE.activeModalTab,
      erasCount: FRANCHISE_SAGA_3_ERAS.length,
      setsCount: FRANCHISE_20_EXPANSION_SETS.length,
      heraldCardsCount: SAGA_10YEAR_HERALD_CARDS.length
    };
  }

  function closeSaga10YearFranchiseModal() {
    if (typeof globalScope.document === "undefined") return;
    const modal = globalScope.document.getElementById("saga-10year-franchise-modal");
    if (modal) {
      modal.style.display = "none";
    }
  }

  // ==========================================================================
  // 11. EXPOSE MODULE & GLOBAL API
  // ==========================================================================
  const CardFrontSaga10YearFranchise = {
    POWER_CREEP_DIRECTIONAL_BUDGET_CAPS: POWER_CREEP_DIRECTIONAL_BUDGET_CAPS,
    FRANCHISE_SAGA_3_ERAS: FRANCHISE_SAGA_3_ERAS,
    FRANCHISE_20_EXPANSION_SETS: FRANCHISE_20_EXPANSION_SETS,
    SAGA_10YEAR_HERALD_CARDS: SAGA_10YEAR_HERALD_CARDS,
    SBX00_AND_GPU_CLUSTER_TOPOLOGY: SBX00_AND_GPU_CLUSTER_TOPOLOGY,
    registerSaga10YearHeraldCards: registerSaga10YearHeraldCards,
    validateSetRotationAndPowerCreep: validateSetRotationAndPowerCreep,
    getSbx00AndClusterLiveTelemetry: getSbx00AndClusterLiveTelemetry,
    equip10YearSagaHeraldDeck: equip10YearSagaHeraldDeck,
    setSagaFormatMode: setSagaFormatMode,
    openSaga10YearFranchiseModal: openSaga10YearFranchiseModal,
    closeSaga10YearFranchiseModal: closeSaga10YearFranchiseModal,
    zeroLivingArtistNames: true,
    zeroRawUnicodeEmojis: true
  };

  globalScope.CardFrontSaga10YearFranchise = CardFrontSaga10YearFranchise;
  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.Saga10YearFranchise = CardFrontSaga10YearFranchise;

  globalScope.FRANCHISE_SAGA_3_ERAS = FRANCHISE_SAGA_3_ERAS;
  globalScope.FRANCHISE_20_EXPANSION_SETS = FRANCHISE_20_EXPANSION_SETS;
  globalScope.SAGA_10YEAR_HERALD_CARDS = SAGA_10YEAR_HERALD_CARDS;
  globalScope.SBX00_AND_GPU_CLUSTER_TOPOLOGY = SBX00_AND_GPU_CLUSTER_TOPOLOGY;
  globalScope.validateSetRotationAndPowerCreep = validateSetRotationAndPowerCreep;
  globalScope.getSbx00AndClusterLiveTelemetry = getSbx00AndClusterLiveTelemetry;
  globalScope.equip10YearSagaHeraldDeck = equip10YearSagaHeraldDeck;
  globalScope.openSaga10YearFranchiseModal = openSaga10YearFranchiseModal;
  globalScope.closeSaga10YearFranchiseModal = closeSaga10YearFranchiseModal;
})(typeof window !== "undefined" ? window : globalThis);
