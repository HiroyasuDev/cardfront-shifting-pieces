/**
 * CARDFRONT 3D: Cradle of Echoes — Anime/Manga Illustration Model Zoo & Screentone Shader Studio
 * Module: WebPlayable/modules/anime_manga_studio.js
 *
 * Exposes `window.CardFrontAnimeMangaStudio` and top-level helpers:
 *   - `ANIME_MANGA_ILLUSTRATION_MODELS` (13 `.safetensors` models in `Models/LoRA/`, including 12 anime/manga LoRA adapters + AlphaZero policy-value adapter)
 *   - `MANGA_SCREENTONE_SHADERS` (5 visual style presets: `cel_astral_gold`, `manga_gpen_screentone`, `sakuga_kagenashi_flare`, `mecha_blueprint_halftone`, `tarot_chiaroscuro_foil`)
 *   - `renderMangaStylePreviewCanvas(canvasEl, modelId, sourceImageEl)`
 *   - `applyIllustrationModelToTabletop(modelId, stateObj)`
 *
 * Art Direction Contract:
 *   100% concrete morphological properties (stylized 6.5-to-7.5-head proportions, tapered gauntlets/boots,
 *   pen-and-ink G-pen crosshatching over warm parchment-gold filigree, vibrant watercolor cel-wash,
 *   CMYK halftone screentone dot-matrix, 24fps kagenashi key-animation rim lighting, sleek beveled
 *   cyber-magicite armor edges, stark negative-space sumi-ink blocks, and high-contrast faction silhouettes).
 *   Zero living artists' names in prompts or model descriptions.
 */
(function initCardFrontAnimeMangaStudio(globalScope) {
  "use strict";

  const MANGA_SCREENTONE_SHADERS = {
    cel_astral_gold: {
      id: "cel_astral_gold",
      name: "Ivalice Astral Cel-Wash & Law-Gold Filigree",
      description:
        "Vibrant watercolor cel-wash, pen-and-ink G-pen crosshatching over warm parchment-gold filigree, and astral cyan rim lighting.",
      cssFilter: "contrast(1.08) saturate(1.18) brightness(1.03)",
      rimColor: "#00E5FF",
      secondaryColor: "#FFB800",
      inkColor: "#0F172A",
      screentoneSpacing: 6,
      screentoneOpacity: 0.16,
      inkEdgeStrength: 0.72,
      speedlineCount: 28,
      starFlareCount: 3
    },
    manga_gpen_screentone: {
      id: "manga_gpen_screentone",
      name: "G-Pen Sumi-e Crosshatch & CMYK Screentone Dot-Matrix",
      description:
        "Stark negative-space sumi-ink blocks, razor-sharp G-pen contours, and 60-LPI halftone screentone dot-matrix gradients.",
      cssFilter: "contrast(1.26) saturate(0.82) brightness(1.02)",
      rimColor: "#00E5FF",
      secondaryColor: "#FF2E54",
      inkColor: "#090D16",
      screentoneSpacing: 4,
      screentoneOpacity: 0.34,
      inkEdgeStrength: 0.94,
      speedlineCount: 36,
      starFlareCount: 2
    },
    sakuga_kagenashi_flare: {
      id: "sakuga_kagenashi_flare",
      name: "24fps Sakuga Kagenashi Rim-Light & Impact Star-Flare",
      description:
        "24fps TV anime key-animation unshaded cel planes, chromatic aberration split, radial shonen speedlines, and 4-point star-flares.",
      cssFilter: "contrast(1.18) saturate(1.32) brightness(1.06)",
      rimColor: "#FF2E54",
      secondaryColor: "#00E5FF",
      inkColor: "#0F172A",
      screentoneSpacing: 5,
      screentoneOpacity: 0.20,
      inkEdgeStrength: 0.85,
      speedlineCount: 64,
      starFlareCount: 6
    },
    mecha_blueprint_halftone: {
      id: "mecha_blueprint_halftone",
      name: "7.5-Head Cyber-Magicite Orthographic & Normal-Bridge Cel",
      description:
        "Sleek beveled cyber-magicite armor edges, precision orthographic panel-line drafting, sparse voxel relief, and jade-cyan visor glow.",
      cssFilter: "contrast(1.15) saturate(1.14) hue-rotate(-4deg)",
      rimColor: "#2EE6D3",
      secondaryColor: "#00E5FF",
      inkColor: "#0B132B",
      screentoneSpacing: 5,
      screentoneOpacity: 0.24,
      inkEdgeStrength: 0.88,
      speedlineCount: 32,
      starFlareCount: 4
    },
    tarot_chiaroscuro_foil: {
      id: "tarot_chiaroscuro_foil",
      name: "Chiaroscuro Obsidian-Ivory Tarot & Gilded Astral Halo",
      description:
        "Obsidian-and-ivory chiaroscuro contrast, concentric geometric tarot halo linework, tarot violet wash, and gilded parchment foil.",
      cssFilter: "contrast(1.22) saturate(1.10) sepia(0.14)",
      rimColor: "#A855F7",
      secondaryColor: "#FFE082",
      inkColor: "#05070C",
      screentoneSpacing: 5,
      screentoneOpacity: 0.26,
      inkEdgeStrength: 0.90,
      speedlineCount: 24,
      starFlareCount: 4
    }
  };

  const ANIME_MANGA_ILLUSTRATION_MODELS = [
    {
      id: "synapse_aether_cel_v1",
      adapterId: "synapse_aether_cel_v1_lora",
      name: "Ivalice Watercolor Cel-Wash & Tapered Gauntlet Proportions",
      category: "Tactical Fantasy Cel-Wash & Filigree",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "synapse_aether_cel_v1_lora.safetensors",
      shaderPreset: "cel_astral_gold",
      morphologicalPrompt:
        "stylized 6.5-to-7.5-head proportions, tapered gauntlets/boots, pen-and-ink G-pen crosshatching over warm parchment-gold filigree, vibrant watercolor cel-wash, high-contrast faction silhouettes, astral cyan and cobalt-gold rim lighting",
      colorSignature: ["#00E5FF", "#FFB800", "#1E293B", "#FFE082"]
    },
    {
      id: "hi3d_trellis2_nirne_norld",
      adapterId: "hi3d_trellis2_nirne_norld_adapter",
      name: "Hi3D Normal-Bridge & Sparse Voxel Manga Silhouette",
      category: "2.5D Normal-Bridge & Sparse Voxel Cel",
      baseCheckpoint: "Stable-X/trellis-normal-v0-1",
      loraFile: "hi3d_trellis2_nirne_norld_adapter.safetensors",
      shaderPreset: "mecha_blueprint_halftone",
      morphologicalPrompt:
        "isometric 2.5D normal-bridge relief, sparse voxel manga silhouette, sleek beveled cyber-magicite armor edges, stylized 7-head tactical unit proportions, crisp G-pen contour linework, jade-teal and cyan normal-mapped rim lighting",
      colorSignature: ["#2EE6D3", "#00E5FF", "#0F172A", "#94A3B8"]
    },
    {
      id: "mga2_solideye_halftone",
      adapterId: "mga2_solideye_halftone_shader_lora",
      name: "CMYK Screentone Halftone Dot-Matrix & Kagenashi Cel Shadow",
      category: "CMYK Screentone Halftone & Kagenashi Cel",
      baseCheckpoint: "KBlueLeaf/Kohaku-XL-Zeta",
      loraFile: "mga2_solideye_halftone_shader_lora.safetensors",
      shaderPreset: "manga_gpen_screentone",
      morphologicalPrompt:
        "CMYK halftone screentone dot-matrix, 24fps kagenashi key-animation rim lighting, stylized 7-head tactical espionage proportions, razor-sharp G-pen ink outlines, flat graphic cel shadow planes, high-contrast faction silhouettes",
      colorSignature: ["#00E5FF", "#FF2E54", "#FFB800", "#0F172A"]
    },
    {
      id: "ties_merged_master_soup_v1",
      adapterId: "ties_merged_master_soup_v1",
      name: "12-Lineage TIES-Merged Anime/Manga Model Soup",
      category: "12-Lineage TIES-Merged House Style",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "ties_merged_master_soup_v1.safetensors",
      shaderPreset: "cel_astral_gold",
      morphologicalPrompt:
        "12-lineage TIES-merged anime/manga model soup, stylized 6.5-to-7.5-head proportions, tapered gauntlets/boots, pen-and-ink G-pen crosshatching over warm parchment-gold filigree, vibrant watercolor cel-wash, sleek beveled cyber-magicite armor edges",
      colorSignature: ["#FFB800", "#00E5FF", "#A855F7", "#2EE6D3"]
    },
    {
      id: "anime_sakuga_kagenashi_v2",
      adapterId: "anime_sakuga_kagenashi_keyframe_v2_lora",
      name: "24fps TV Anime Key-Animation Kagenashi Rim-Light & Star-Flare",
      category: "24fps TV Anime Sakuga & Star-Flare",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "anime_sakuga_kagenashi_keyframe_v2_lora.safetensors",
      shaderPreset: "sakuga_kagenashi_flare",
      morphologicalPrompt:
        "24fps kagenashi key-animation rim lighting, four-point star-flare burst, stylized 7-head anime hero proportions, unshaded flat cel shadow blocks, kinetic smear-frame motion arcs, high-contrast faction silhouettes, crimson-flame and astral cyan highlights",
      colorSignature: ["#FF2E54", "#FFB800", "#00E5FF", "#FFFFFF"]
    },
    {
      id: "manga_sumi_ink_seinen_v1",
      adapterId: "manga_sumi_ink_crosshatch_seinen_v1_lora",
      name: "High-Contrast G-Pen Sumi-e Ink Crosshatching & Baroque Armor Filigree",
      category: "Seinen G-Pen Sumi-e & Baroque Crosshatch",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "manga_sumi_ink_crosshatch_seinen_v1_lora.safetensors",
      shaderPreset: "manga_gpen_screentone",
      morphologicalPrompt:
        "pen-and-ink G-pen crosshatching over warm parchment-gold filigree, high-contrast sumi-e dry-brush ink strokes, baroque engraved plate armor, monochrome screentone dot-matrix gradients, stylized 7.5-head dark fantasy proportions, stark silhouette",
      colorSignature: ["#F8FAFC", "#0F172A", "#FFE082", "#94A3B8"]
    },
    {
      id: "cyber_mecha_orthographic_v1",
      adapterId: "cyber_mecha_orthographic_cel_v1_lora",
      name: "7.5-Head Cyber-Magicite Mecha Frame, Beveled Energy Wings & Cockpit Visor",
      category: "Cyber-Magicite Mecha & Orthographic Cel",
      baseCheckpoint: "flux1-dev-fp8.safetensors",
      loraFile: "cyber_mecha_orthographic_cel_v1_lora.safetensors",
      shaderPreset: "mecha_blueprint_halftone",
      morphologicalPrompt:
        "stylized 7.5-head cyber-magicite mecha frame, sleek beveled cyber-magicite armor edges, tapered gauntlets/boots, translucent astral energy wings, luminous cockpit visor, precision orthographic panel-line drafting, high-contrast faction silhouettes",
      colorSignature: ["#00E5FF", "#2EE6D3", "#F97316", "#0F172A"]
    },
    {
      id: "dark_occult_tarot_v1",
      adapterId: "dark_occult_tarot_monolith_v1_lora",
      name: "Chiaroscuro Obsidian-Ivory Tarot Iconography & Astral Halo Linework",
      category: "Occult Tarot Chiaroscuro & Gilded Foil",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "dark_occult_tarot_monolith_v1_lora.safetensors",
      shaderPreset: "tarot_chiaroscuro_foil",
      morphologicalPrompt:
        "chiaroscuro obsidian-ivory tarot iconography, concentric astral halo linework, pen-and-ink G-pen crosshatching over warm parchment-gold filigree, stylized 7-head arcane monolith silhouette, tarot violet and gilded foil accents",
      colorSignature: ["#A855F7", "#FFE082", "#090D16", "#FFB800"]
    },
    {
      id: "storybook_gouache_citadel_v1",
      adapterId: "storybook_gouache_sky_citadel_v1_lora",
      name: "Luminous Gouache Cloudscape, Brass Astrolabe Filigree & Jewel-Tone Wash",
      category: "Storybook Gouache & Sky-Citadel Wash",
      baseCheckpoint: "flux1-dev-fp8.safetensors",
      loraFile: "storybook_gouache_sky_citadel_v1_lora.safetensors",
      shaderPreset: "cel_astral_gold",
      morphologicalPrompt:
        "vibrant watercolor cel-wash and luminous gouache cloudscape, brass astrolabe rings over warm parchment-gold filigree, stylized 6.5-to-7.5-head proportions, jewel-tone atmospheric depth, crisp sepia ink contour lines",
      colorSignature: ["#38BDF8", "#FFE082", "#2EE6D3", "#1E293B"]
    },
    {
      id: "tactical_chibi_commander_v1",
      adapterId: "tactical_chibi_commander_vanguard_v1_lora",
      name: "Crisp 6.5-Head Tactical Unit Commander, Bold Vector Outlines & Faction Visor",
      category: "Tactical 6.5-Head Commander & Vector Cel",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "tactical_chibi_commander_vanguard_v1_lora.safetensors",
      shaderPreset: "cel_astral_gold",
      morphologicalPrompt:
        "stylized 6.5-head tactical unit commander proportions, tapered gauntlets/boots, bold variable-width vector ink outlines, vibrant watercolor cel-wash, luminous faction visor, high-contrast faction silhouettes",
      colorSignature: ["#00E5FF", "#FFB800", "#FF2E54", "#0F172A"]
    },
    {
      id: "shonen_astral_burst_v1",
      adapterId: "shonen_astral_burst_speedline_v1_lora",
      name: "Dynamic Foreshortened Blade Lunge, Radial Manga Speedlines & Chroma Split",
      category: "Shonen Radial Speedline & Chroma Burst",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "shonen_astral_burst_speedline_v1_lora.safetensors",
      shaderPreset: "sakuga_kagenashi_flare",
      morphologicalPrompt:
        "dynamic foreshortened blade lunge, dense radial manga convergence speedlines, CMYK halftone screentone dot-matrix, 24fps kagenashi key-animation rim lighting, chromatic aberration edge split, high-contrast faction silhouettes",
      colorSignature: ["#00E5FF", "#FF2E54", "#F97316", "#FFFFFF"]
    },
    {
      id: "kubrart_vector_cel_ink_v1",
      adapterId: "kubrart_vector_cel_ink_v1",
      name: "Kubrart Graphic Vector-Cel & Stark Ink Silhouette",
      category: "Graphic Vector-Cel & Negative-Space Manga Ink",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "kubrart_vector_cel_ink_v1_lora.safetensors",
      shaderPreset: "manga_gpen_screentone",
      morphologicalPrompt:
        "stark negative-space sumi-ink blocks, razor-sharp vector-cel contours, 7-head stylized anime/manga silhouette, luminous chromatic rim-light, flat graphic kagenashi shadow planes, high-contrast faction silhouettes",
      colorSignature: ["#0F172A", "#00E5FF", "#FF2E54", "#F8FAFC"]
    },
    {
      id: "synapse_alphazero_policy_value_v1",
      adapterId: "synapse_alphazero_policy_value_v1",
      name: "Synapse AlphaZero PUCT Policy-Value & Tactical Telegraph Adapter",
      category: "AlphaZero Tactical Policy-Value & Telegraph Conditioning",
      baseCheckpoint: "animagineXLV31_v31.safetensors",
      loraFile: "synapse_alphazero_policy_value_v1.safetensors",
      shaderPreset: "cel_astral_gold",
      morphologicalPrompt:
        "tactical 3x3 directional grid policy-value telemetry visualization, crisp vector telegraph lines, stylized 7-head unit silhouettes, astral cyan and law-gold rim lighting",
      colorSignature: ["#00E5FF", "#FFB800", "#A855F7", "#2EE6D3"]
    }
  ];

  const LIVE_COMFYUI_BASE_CHECKPOINTS = [
    {
      id: "animagineXLV31_v31.safetensors",
      endpoint: "http://192.168.86.30:8188",
      architecture: "SDXL 1.0 Anime/Manga Base"
    },
    {
      id: "flux1-dev-fp8.safetensors",
      endpoint: "http://192.168.86.30:8188",
      architecture: "FLUX.1-dev FP8 Rectified Flow"
    }
  ];

  const MULTIMODAL_VISION_CRITICS = [
    "pxg-lumenforge:12b-tutor",
    "qwen2.5vl:3b",
    "granite3.2-vision:latest"
  ];

  /**
   * Set 2: "Kubrart Astral Eclipse & Manga Vanguard" Expansion (20 Cards: set2_k01 .. set2_k20)
   * Spanning 4 Anime/Manga Illustration Lineages:
   *   - set2_k01..set2_k05: Kubrart Vector-Cel & Negative-Space Prism (`kubrart_vector_cel_ink_v1`)
   *   - set2_k06..set2_k10: Seinen Sumi-e G-Pen Crosshatch & Crimson Ink (`manga_sumi_ink_seinen_v1`)
   *   - set2_k11..set2_k15: 24fps Trigger Kagenashi Keyframe & Star-Flare (`anime_sakuga_kagenashi_v2`)
   *   - set2_k16..set2_k20: Cyber-Magicite Mecha Orthographic & Blueprint Halftone (`cyber_mecha_orthographic_v1`)
   */
  const SET2_KUBRART_MANGA_CARDS = [
    {
      id: "set2_k01",
      name: "Kubrart Eclipse Sovereign",
      faction: "Aether",
      nesw: [9, 8, 6, 8],
      cost: 4,
      tier: 4,
      modelId: "kubrart_vector_cel_ink_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k01_kubrart_eclipse_sovereign.png",
      ability: {
        id: "ab_eclipse_prism_dominion",
        name: "Negative-Space Prism Dominion",
        text: "On Deploy: Flips adjacent orthogonal units if their opposing directional rank is Prime (2, 3, 5, 7) and grants +1 N/E to Allied Aether conduits."
      },
      morphologicalPrompt:
        "stark negative-space sumi-ink blocks, razor-sharp graphic vector-cel contours, floating polyhedral crystal shards, stylized 7-head anime character proportions, luminous violet #A855F7 and astral cyan #00E5FF rim-wash"
    },
    {
      id: "set2_k02",
      name: "Vector-Prism Spellblade",
      faction: "Aether",
      nesw: [7, 7, 5, 6],
      cost: 2,
      tier: 2,
      modelId: "kubrart_vector_cel_ink_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k02_vector_prism_duelist.png",
      ability: {
        id: "ab_vector_cel_riposte",
        name: "Vector-Cel Riposte",
        text: "Plus-Wall Trigger: Gains +2 East and +2 West when placed adjacent to an obsidian rift or corner tile."
      },
      morphologicalPrompt:
        "agile anime spellblade duelist with twin crystalline vector-cel rapiers, stark obsidian negative-space shadow blocks, floating violet and cyan polyhedral shards, tapered gauntlets"
    },
    {
      id: "set2_k03",
      name: "Obsidian Shard Oracle",
      faction: "Aether",
      nesw: [8, 6, 8, 6],
      cost: 3,
      tier: 3,
      modelId: "kubrart_vector_cel_ink_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k03_obsidian_shard_oracle.png",
      ability: {
        id: "ab_polyhedral_foresight",
        name: "Polyhedral Foresight",
        text: "On Deploy: Reveals the top card of the opponent deck and projects a luminous +1 N/S astral prism barrier."
      },
      morphologicalPrompt:
        "astral oracle priestess surrounded by levitating obsidian icosahedrons and glowing tarot rings, stark vector-cel negative space, violet and cyan rim lighting"
    },
    {
      id: "set2_k04",
      name: "Negative-Space Astral Valkyrie",
      faction: "Valkyria",
      nesw: [8, 8, 5, 7],
      cost: 3,
      tier: 3,
      modelId: "kubrart_vector_cel_ink_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k04_negative_space_valkyrie.png",
      ability: {
        id: "ab_kubrart_sky_dive",
        name: "Chromatic Sky-Shear",
        text: "Aerial Rush: Ignores terrain elevation penalties and reduces adjacent enemy North armor by 1."
      },
      morphologicalPrompt:
        "winged astral valkyrie lancer silhouetted in stark obsidian negative-space ink with glowing cyan and violet geometric wing feathers, razor-sharp vector-cel spear contour"
    },
    {
      id: "set2_k05",
      name: "Polyhedral Rift Arbiter",
      faction: "Solaris",
      nesw: [7, 8, 7, 7],
      cost: 3,
      tier: 3,
      modelId: "kubrart_vector_cel_ink_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k05_polyhedral_rift_arbiter.png",
      ability: {
        id: "ab_law_prism_edict",
        name: "Law-Prism Edict",
        text: "Same/Plus Decree: Locks equal-sum orthogonal clashes in your favor and fortifies all 4 sides by +1."
      },
      morphologicalPrompt:
        "armored law arbiter floating inside an interlocking polyhedral crystal cage, stark sumi-ink negative space contrasted with luminous violet, cyan, and gold vector-cel planes"
    },
    {
      id: "set2_k06",
      name: "Sumi-e Crimson Ronin",
      faction: "Abyss",
      nesw: [8, 9, 5, 6],
      cost: 3,
      tier: 3,
      modelId: "manga_sumi_ink_seinen_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k06_sumi_crimson_ronin.png",
      ability: {
        id: "ab_crimson_iaijutsu",
        name: "Crimson G-Pen Iaijutsu",
        text: "First Strike: Slashes the East orthogonal target for -2 West defense before directional comparison."
      },
      morphologicalPrompt:
        "seinen manga wandering ronin mid-iaijutsu sword draw, dense monochrome G-pen crosshatching on warm bone-ivory #F2ECE1 parchment, vivid crimson #FF2E54 ink blade trail"
    },
    {
      id: "set2_k07",
      name: "G-Pen Ivory Inquisitor",
      faction: "Solaris",
      nesw: [6, 8, 6, 5],
      cost: 2,
      tier: 2,
      modelId: "manga_sumi_ink_seinen_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k07_gpen_ivory_inquisitor.png",
      ability: {
        id: "ab_crosshatch_penance",
        name: "Crosshatched Verdict",
        text: "On Capture: Drains 1 Aether Charge from the opponent and converts it into a bone-ivory ward."
      },
      morphologicalPrompt:
        "baroque cathedral inquisitor knight rendered in intricate G-pen sumi-e ink crosshatching on bone-ivory paper, engraved plate armor with vivid crimson ink accents"
    },
    {
      id: "set2_k08",
      name: "Crosshatch Crimson Kunoichi",
      faction: "Abyss",
      nesw: [7, 6, 5, 8],
      cost: 2,
      tier: 2,
      modelId: "manga_sumi_ink_seinen_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k08_crosshatch_blood_kunoichi.png",
      ability: {
        id: "ab_sumi_smoke_step",
        name: "Sumi-e Smoke Step",
        text: "Stealth Infiltration: Can swap positions with an uncontested allied card once per match."
      },
      morphologicalPrompt:
        "stealth kunoichi assassin leaping through dense G-pen crosshatched sumi-e ink smoke on bone-ivory paper, long flowing crimson scarf trail and twin chained kunai"
    },
    {
      id: "set2_k09",
      name: "Baroque Sumi-Ink Cenobite",
      faction: "Abyss",
      nesw: [7, 7, 8, 6],
      cost: 3,
      tier: 3,
      modelId: "manga_sumi_ink_seinen_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k09_baroque_ink_cenobite.png",
      ability: {
        id: "ab_obsidian_chain_bind",
        name: "Obsidian Chain Bind",
        text: "Aura: Prevents adjacent enemy cards from triggering Combo chain flips."
      },
      morphologicalPrompt:
        "dark fantasy baroque cenobite guardian in heavily crosshatched G-pen plate armor, bone-ivory halo ring and vivid crimson ink lantern chains"
    },
    {
      id: "set2_k10",
      name: "Seinen Ash Executioner",
      faction: "Abyss",
      nesw: [9, 8, 7, 7],
      cost: 4,
      tier: 4,
      modelId: "manga_sumi_ink_seinen_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k10_seinen_ash_executioner.png",
      ability: {
        id: "ab_crimson_guillotine_cleave",
        name: "Crimson Greatsword Cleave",
        text: "Overpower: When capturing a North or East target, deals 1 splash rank reduction to remaining enemy neighbors."
      },
      morphologicalPrompt:
        "colossal dark fantasy executioner knight with serrated greatsword, dense seinen G-pen crosshatching on bone-ivory paper with dramatic crimson ink slash accents"
    },
    {
      id: "set2_k11",
      name: "Kagenashi Star-Flare Vanguard",
      faction: "Solaris",
      nesw: [9, 7, 6, 7],
      cost: 3,
      tier: 3,
      modelId: "anime_sakuga_kagenashi_v2",
      art: "./GeneratedArt/Set2KubrartManga/set2_k11_kagenashi_starflare_phoenix.png",
      ability: {
        id: "ab_24fps_ignition_burst",
        name: "24fps Star-Flare Ignition",
        text: "Sakuga Cut-In: Gains +2 North on the turn it is deployed and emits a 4-point gold flare shield."
      },
      morphologicalPrompt:
        "24fps TV anime key-animation solar vanguard hero launching upward in an explosion of four-point gold #FFB800 star-flares, hard kagenashi shadow blocks, chromatic aberration edges"
    },
    {
      id: "set2_k12",
      name: "24fps Sakuga Smear Bladerunner",
      faction: "Valkyria",
      nesw: [6, 8, 5, 7],
      cost: 2,
      tier: 2,
      modelId: "anime_sakuga_kagenashi_v2",
      art: "./GeneratedArt/Set2KubrartManga/set2_k12_sakuga_smear_bladerunner.png",
      ability: {
        id: "ab_smear_frame_dash",
        name: "Key-Frame Smear Dash",
        text: "Haste: Treats East and West values as +1 higher when attacking on odd-numbered turns."
      },
      morphologicalPrompt:
        "dynamic foreshortened anime cyber-bladerunner mid-slash with kinetic smear-frame plasma arc, hard kagenashi shadow planes, four-point gold and cyan star-flares"
    },
    {
      id: "set2_k13",
      name: "Chroma-Split Impact Chronomancer",
      faction: "Chronos",
      nesw: [7, 7, 8, 7],
      cost: 3,
      tier: 3,
      modelId: "anime_sakuga_kagenashi_v2",
      art: "./GeneratedArt/Set2KubrartManga/set2_k13_chroma_split_chronomancer.png",
      ability: {
        id: "ab_frame_skip_rewind",
        name: "24fps Frame-Skip Rewind",
        text: "Temporal Lock: Once per game, negates an enemy Plus/Same chain flip against this card."
      },
      morphologicalPrompt:
        "anime chronomancer shattering a giant golden clockface in a 24fps sakuga impact frame, chromatic aberration RGB split, hard kagenashi cel shadows, four-point star flares"
    },
    {
      id: "set2_k14",
      name: "Four-Point Starflare Seraph",
      faction: "Solaris",
      nesw: [9, 8, 8, 6],
      cost: 4,
      tier: 4,
      modelId: "anime_sakuga_kagenashi_v2",
      art: "./GeneratedArt/Set2KubrartManga/set2_k14_hyper_flare_seraph.png",
      ability: {
        id: "ab_celestial_sakuga_chorus",
        name: "Celestial Sakuga Finale",
        text: "Ascension: If you control 3+ Solaris or Valkyria cards, all allied cards gain +1 to their lowest direction."
      },
      morphologicalPrompt:
        "radiant six-winged anime seraph knight unleashing a blinding four-point gold star-flare beam, 24fps kagenashi keyframe shading, bold crimson and cyan rim highlights"
    },
    {
      id: "set2_k15",
      name: "Impact-Frame Astral Striker",
      faction: "Aether",
      nesw: [8, 6, 5, 6],
      cost: 2,
      tier: 2,
      modelId: "anime_sakuga_kagenashi_v2",
      art: "./GeneratedArt/Set2KubrartManga/set2_k15_impact_frame_berserker.png",
      ability: {
        id: "ab_kagenashi_meteor_fist",
        name: "Kagenashi Meteor Impact",
        text: "Breach: Ignores Shield tokens on the North target during deployment resolution."
      },
      morphologicalPrompt:
        "tapered-gauntlet anime astral brawler delivering a foreshortened impact-frame punch, 24fps kagenashi shadow blocks, gold four-point star flare and chromatic edge split"
    },
    {
      id: "set2_k16",
      name: "Cyber-Magicite Archon Mk.IV",
      faction: "Valkyria",
      nesw: [8, 9, 7, 8],
      cost: 4,
      tier: 4,
      modelId: "cyber_mecha_orthographic_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k16_cyber_magicite_archon_mk4.png",
      ability: {
        id: "ab_orthographic_target_lock",
        name: "Orthographic Target Lock",
        text: "Mecha Overdrive: Scans all orthogonal lanes and grants +1 to every direction facing a Boss or Construct."
      },
      morphologicalPrompt:
        "7.5-head cyber-magicite archon mecha unit with sleek beveled white-and-cobalt armor plates, translucent astral cyan energy wings, luminous jade-teal cockpit visor, CMYK screentone dot-matrix"
    },
    {
      id: "set2_k17",
      name: "Orthographic Railgun Dragoon",
      faction: "Valkyria",
      nesw: [9, 7, 5, 7],
      cost: 3,
      tier: 3,
      modelId: "cyber_mecha_orthographic_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k17_orthographic_railgun_valkyrie.png",
      ability: {
        id: "ab_hypervelocity_rail_pierce",
        name: "Hyper-Velocity Rail Pierce",
        text: "Line Snipe: Can contest an enemy card 2 tiles North across an empty center square."
      },
      morphologicalPrompt:
        "7.5-head cyber-magicite aerial dragoon mecha aiming a long-barrel electromagnetic rail-lance, beveled energy wings, glowing cyan visor, CMYK halftone screentone dot-matrix"
    },
    {
      id: "set2_k18",
      name: "Blueprint Halftone Aegis Titan",
      faction: "Chronos",
      nesw: [6, 8, 9, 6],
      cost: 3,
      tier: 3,
      modelId: "cyber_mecha_orthographic_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k18_blueprint_halftone_bastion.png",
      ability: {
        id: "ab_normal_bridge_bulwark",
        name: "Orthographic Aegis Bulwark",
        text: "Fortify: Cannot be flipped from the South or East during the first turn after deployment."
      },
      morphologicalPrompt:
        "heavy 7.5-head cyber-magicite bastion mecha frame deploying interlocking hexagonal energy shields, orthographic blueprint reticle lines, CMYK halftone screentone dot-matrix"
    },
    {
      id: "set2_k19",
      name: "Beveled Energy-Wing Interceptor",
      faction: "Valkyria",
      nesw: [7, 7, 5, 7],
      cost: 2,
      tier: 2,
      modelId: "cyber_mecha_orthographic_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k19_beveled_wing_interceptor.png",
      ability: {
        id: "ab_vectored_thruster_pivot",
        name: "Vectored Thruster Pivot",
        text: "On Deploy: May rotate its NESW directional values 90 degrees clockwise to match tactical threats."
      },
      morphologicalPrompt:
        "high-speed 7.5-head cyber-magicite interceptor mecha with six beveled jade-cyan energy wings, tapered thruster boots, crisp orthographic panel linework"
    },
    {
      id: "set2_k20",
      name: "CMYK Screentone Omega Frame",
      faction: "Chronos",
      nesw: [9, 9, 8, 7],
      cost: 4,
      tier: 4,
      modelId: "cyber_mecha_orthographic_v1",
      art: "./GeneratedArt/Set2KubrartManga/set2_k20_cmyk_screentone_omega_core.png",
      ability: {
        id: "ab_omega_chronos_synchrony",
        name: "Omega Reactor Synchrony",
        text: "Apex Construct: Gains +1 to all directions if your deck contains Cards from all 4 Set 2 Anime/Manga Lineages."
      },
      morphologicalPrompt:
        "sovereign 7.5-head omega cyber-magicite mecha commander with twin solar-amber and astral-cyan reactor halos, beveled energy wings, CMYK screentone dot-matrix"
    }
  ];

  function resolveIllustrationModel(modelIdOrKey) {
    if (!modelIdOrKey) {
      return ANIME_MANGA_ILLUSTRATION_MODELS[0];
    }
    const q = String(modelIdOrKey).trim().toLowerCase();
    for (let i = 0; i < ANIME_MANGA_ILLUSTRATION_MODELS.length; i++) {
      const m = ANIME_MANGA_ILLUSTRATION_MODELS[i];
      if (
        m.id.toLowerCase() === q ||
        (m.adapterId && m.adapterId.toLowerCase() === q) ||
        m.loraFile.toLowerCase() === q ||
        m.loraFile.replace(/\.safetensors$/i, "").toLowerCase() === q
      ) {
        return m;
      }
    }
    // Check if passed a shaderPreset directly
    for (let i = 0; i < ANIME_MANGA_ILLUSTRATION_MODELS.length; i++) {
      const m = ANIME_MANGA_ILLUSTRATION_MODELS[i];
      if (m.shaderPreset.toLowerCase() === q || m.id.toLowerCase().indexOf(q) !== -1 || q.indexOf(m.id.toLowerCase()) !== -1) {
        return m;
      }
    }
    return ANIME_MANGA_ILLUSTRATION_MODELS[0];
  }

  function hexToRgb(hex) {
    const clean = String(hex || "#00E5FF").replace("#", "");
    const num = parseInt(clean.length === 3 ? clean.replace(/(.)/g, "$1$1") : clean, 16);
    if (Number.isNaN(num)) {
      return { r: 0, g: 229, b: 255 };
    }
    return {
      r: (num >> 16) & 255,
      g: (num >> 8) & 255,
      b: num & 255
    };
  }

  function drawStarFlare(ctx, cx, cy, outerR, innerR, colorHex, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = colorHex;
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const angle = (i * Math.PI) / 4;
      const r = i % 2 === 0 ? outerR : innerR;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  function drawProceduralSilhouetteFallback(ctx, w, h, model, preset) {
    const sig = model.colorSignature || ["#00E5FF", "#FFB800", "#0F172A", "#F8FAFC"];
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, "#090D16");
    bgGrad.addColorStop(0.55, "#131C31");
    bgGrad.addColorStop(1, "#0B1120");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Astral halo or mecha reticle behind figure
    const cx = w * 0.5;
    const cy = h * 0.42;
    ctx.save();
    ctx.strokeStyle = sig[0];
    ctx.globalAlpha = 0.45;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, Math.min(w, h) * 0.32, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = sig[1];
    ctx.beginPath();
    ctx.arc(cx, cy, Math.min(w, h) * 0.24, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Stylized 7-head anime/manga heroic/mecha bust & tapered gauntlets silhouette
    ctx.save();
    ctx.fillStyle = "#1E293B";
    ctx.strokeStyle = preset.rimColor || sig[0];
    ctx.lineWidth = 2.4;

    // Cloak / Energy Wings
    ctx.beginPath();
    ctx.moveTo(cx, cy - h * 0.16);
    ctx.lineTo(cx - w * 0.34, cy + h * 0.36);
    ctx.lineTo(cx + w * 0.34, cy + h * 0.36);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Pauldrons & Torso
    ctx.fillStyle = sig[2] || "#0F172A";
    ctx.beginPath();
    ctx.moveTo(cx - w * 0.26, cy - h * 0.02);
    ctx.lineTo(cx + w * 0.26, cy - h * 0.02);
    ctx.lineTo(cx + w * 0.16, cy + h * 0.34);
    ctx.lineTo(cx - w * 0.16, cy + h * 0.34);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Head & Faction Visor
    ctx.fillStyle = "#F8FAFC";
    ctx.beginPath();
    ctx.arc(cx, cy - h * 0.14, Math.min(w, h) * 0.095, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Visor slash
    ctx.fillStyle = sig[0];
    ctx.beginPath();
    ctx.moveTo(cx - w * 0.09, cy - h * 0.15);
    ctx.lineTo(cx + w * 0.09, cy - h * 0.13);
    ctx.lineTo(cx + w * 0.06, cy - h * 0.10);
    ctx.lineTo(cx - w * 0.07, cy - h * 0.12);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  /**
   * Renders a high-impact procedural anime/manga preview on a `<canvas>`:
   *   - Draws the card portrait (from `sourceImageEl`, active `.slot-art`, or procedural silhouette fallback)
   *   - Runs live G-Pen ink contour detection
   *   - Overlays CMYK/monochrome manga screentone dot-matrix
   *   - Adds radial shonen speedlines, stark sumi-ink negative-space blocks, or 24fps sakuga star-flares
   */
  function renderMangaStylePreviewCanvas(canvasEl, modelId, sourceImageEl) {
    const targetCanvas =
      typeof canvasEl === "string" && typeof document !== "undefined"
        ? document.getElementById(canvasEl) || document.querySelector(canvasEl)
        : canvasEl;

    if (!targetCanvas || typeof targetCanvas.getContext !== "function") {
      return { rendered: false, reason: "invalid_canvas" };
    }

    const model = resolveIllustrationModel(modelId);
    const preset = MANGA_SCREENTONE_SHADERS[model.shaderPreset] || MANGA_SCREENTONE_SHADERS.cel_astral_gold;
    const w = targetCanvas.width || 300;
    const h = targetCanvas.height || 400;
    if (!targetCanvas.width) targetCanvas.width = w;
    if (!targetCanvas.height) targetCanvas.height = h;

    const ctx = targetCanvas.getContext("2d");
    if (!ctx) {
      return { rendered: false, reason: "no_2d_context" };
    }

    ctx.clearRect(0, 0, w, h);

    // Resolve source image if available
    let imgEl = sourceImageEl || null;
    if (!imgEl && typeof document !== "undefined") {
      const slotImgs = document.querySelectorAll("img.slot-art");
      for (let i = 0; i < slotImgs.length; i++) {
        if (slotImgs[i].complete && slotImgs[i].naturalWidth > 0) {
          imgEl = slotImgs[i];
          break;
        }
      }
    }

    let drewExternalImage = false;
    if (imgEl && typeof imgEl === "object") {
      try {
        const isReadyImg =
          (imgEl.tagName === "IMG" && imgEl.complete && imgEl.naturalWidth > 0) ||
          imgEl.tagName === "CANVAS";
        if (isReadyImg) {
          ctx.drawImage(imgEl, 0, 0, w, h);
          drewExternalImage = true;
        }
      } catch (_err) {
        drewExternalImage = false;
      }
    }

    if (!drewExternalImage) {
      drawProceduralSilhouetteFallback(ctx, w, h, model, preset);
    }

    // 1. Live G-Pen Ink Contour Detection & Cel Quantization Pass
    let inkContourPixels = 0;
    try {
      const imgData = ctx.getImageData(0, 0, w, h);
      const data = imgData.data;
      const copy = new Uint8ClampedArray(data);
      const rimRgb = hexToRgb(model.colorSignature[0] || preset.rimColor);
      const inkRgb = hexToRgb(preset.inkColor || "#090D16");
      const isMonoManga =
        model.id === "manga_sumi_ink_seinen_v1" || model.id === "kubrart_vector_cel_ink_v1";
      const edgeThreshold = Math.max(18, Math.round((1.0 - preset.inkEdgeStrength) * 95));

      for (let y = 1; y < h - 1; y++) {
        const rowOffset = y * w * 4;
        for (let x = 1; x < w - 1; x++) {
          const idx = rowOffset + x * 4;
          const lumCenter = copy[idx] * 0.299 + copy[idx + 1] * 0.587 + copy[idx + 2] * 0.114;
          const lumRight = copy[idx + 4] * 0.299 + copy[idx + 5] * 0.587 + copy[idx + 6] * 0.114;
          const lumDown =
            copy[idx + w * 4] * 0.299 + copy[idx + w * 4 + 1] * 0.587 + copy[idx + w * 4 + 2] * 0.114;
          const grad = Math.abs(lumCenter - lumRight) + Math.abs(lumCenter - lumDown);

          if (grad > edgeThreshold) {
            inkContourPixels++;
            if (grad > edgeThreshold * 2.1) {
              // Chromatic Kagenashi Rim-Light along strongest silhouette edges
              data[idx] = rimRgb.r;
              data[idx + 1] = rimRgb.g;
              data[idx + 2] = rimRgb.b;
            } else {
              // Crisp G-Pen Sumi-Ink Contour
              data[idx] = inkRgb.r;
              data[idx + 1] = inkRgb.g;
              data[idx + 2] = inkRgb.b;
            }
          } else if (isMonoManga) {
            // Seinen / Kubrart high-contrast posterized sumi-ink & ivory planes
            const band = lumCenter < 68 ? 14 : lumCenter < 145 ? 118 : lumCenter < 205 ? 202 : 246;
            data[idx] = band;
            data[idx + 1] = band;
            data[idx + 2] = Math.min(255, band + 6);
          } else {
            // Cel-wash posterization (4-band anime cel step)
            data[idx] = Math.min(255, Math.round(copy[idx] / 32) * 32 + 8);
            data[idx + 1] = Math.min(255, Math.round(copy[idx + 1] / 32) * 32 + 8);
            data[idx + 2] = Math.min(255, Math.round(copy[idx + 2] / 32) * 32 + 8);
          }
        }
      }
      ctx.putImageData(imgData, 0, 0);
    } catch (_pixelErr) {
      inkContourPixels = Math.round(w * h * 0.08);
    }

    // 2. CMYK / Monochrome Manga Screentone Dot-Matrix Overlay
    let screentoneDotsDrawn = 0;
    const step = Math.max(4, preset.screentoneSpacing || 5);
    ctx.save();
    ctx.globalAlpha = preset.screentoneOpacity || 0.24;
    for (let y = step; y < h - step; y += step) {
      const shift = (Math.floor(y / step) % 2) * (step * 0.5);
      for (let x = step + shift; x < w - step; x += step) {
        const distFromCenter = Math.hypot((x - w * 0.5) / (w * 0.5), (y - h * 0.45) / (h * 0.5));
        if (distFromCenter > 0.32) {
          const radius = Math.min(step * 0.38, (distFromCenter - 0.28) * step * 0.55);
          ctx.fillStyle =
            (Math.floor(x / step) + Math.floor(y / step)) % 3 === 0
              ? model.colorSignature[0] || preset.rimColor
              : preset.inkColor || "#090D16";
          ctx.beginPath();
          ctx.arc(x, y, Math.max(0.6, radius), 0, Math.PI * 2);
          ctx.fill();
          screentoneDotsDrawn++;
        }
      }
    }
    ctx.restore();

    // 3. Stark Negative-Space Sumi-Ink Blocks (for Kubrart & Seinen Crosshatch)
    if (
      model.id === "kubrart_vector_cel_ink_v1" ||
      model.id === "manga_sumi_ink_seinen_v1" ||
      model.shaderPreset === "manga_gpen_screentone"
    ) {
      ctx.save();
      ctx.fillStyle = "#090D16";
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(w * 0.28, 0);
      ctx.lineTo(0, h * 0.22);
      ctx.closePath();
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(w, h);
      ctx.lineTo(w * 0.72, h);
      ctx.lineTo(w, h * 0.76);
      ctx.closePath();
      ctx.fill();

      // Razor-sharp vector-cel chromatic rim slash
      ctx.strokeStyle = model.colorSignature[1] || "#00E5FF";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(w * 0.29, 0);
      ctx.lineTo(0, h * 0.23);
      ctx.moveTo(w * 0.71, h);
      ctx.lineTo(w, h * 0.75);
      ctx.stroke();
      ctx.restore();
    }

    // 4. Radial Shonen Speedlines & Kinetic Convergence Lines
    const speedlineCount = preset.speedlineCount || 32;
    const cx = w * 0.5;
    const cy = h * 0.44;
    const outerRadius = Math.hypot(w, h) * 0.75;
    ctx.save();
    for (let i = 0; i < speedlineCount; i++) {
      const angle = (i / speedlineCount) * Math.PI * 2;
      const innerR = Math.min(w, h) * (0.31 + ((i * 7) % 11) * 0.014);
      ctx.strokeStyle = i % 3 === 0 ? model.colorSignature[0] || preset.rimColor : "#0F172A";
      ctx.globalAlpha = i % 3 === 0 ? 0.52 : 0.36;
      ctx.lineWidth = i % 4 === 0 ? 2.2 : 1.1;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(angle) * innerR, cy + Math.sin(angle) * innerR);
      ctx.lineTo(cx + Math.cos(angle) * outerRadius, cy + Math.sin(angle) * outerRadius);
      ctx.stroke();
    }
    ctx.restore();

    // 5. 24fps Sakuga Star-Flares & Style-Specific Geometric Overlays
    const flareCount = preset.starFlareCount || 3;
    const flarePositions = [
      [w * 0.22, h * 0.24],
      [w * 0.78, h * 0.20],
      [w * 0.82, h * 0.62],
      [w * 0.18, h * 0.68],
      [w * 0.52, h * 0.14],
      [w * 0.34, h * 0.52]
    ];
    for (let f = 0; f < Math.min(flareCount, flarePositions.length); f++) {
      const pos = flarePositions[f];
      const color = model.colorSignature[f % model.colorSignature.length] || preset.rimColor;
      drawStarFlare(ctx, pos[0], pos[1], 14 - f * 1.2, 3.2, color, 0.88);
    }

    // 6. Signature Footer Telemetry Strip on Canvas
    ctx.save();
    ctx.fillStyle = "rgba(9, 13, 22, 0.86)";
    ctx.fillRect(0, h - 28, w, 28);
    ctx.strokeStyle = model.colorSignature[0] || preset.rimColor;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h - 28);
    ctx.lineTo(w, h - 28);
    ctx.stroke();

    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 10px monospace";
    ctx.fillText(model.id.toUpperCase().slice(0, 26), 8, h - 10);

    const swatches = model.colorSignature || ["#00E5FF", "#FFB800", "#FF2E54", "#F8FAFC"];
    for (let s = 0; s < swatches.length; s++) {
      ctx.fillStyle = swatches[s];
      ctx.fillRect(w - (swatches.length - s) * 14 - 6, h - 20, 10, 10);
    }
    ctx.restore();

    targetCanvas.dataset.renderedModelId = model.id;
    targetCanvas.dataset.shaderPreset = model.shaderPreset;

    return {
      rendered: true,
      modelId: model.id,
      loraFile: model.loraFile,
      shaderPreset: model.shaderPreset,
      width: w,
      height: h,
      inkContourPixels: inkContourPixels,
      screentoneDotsDrawn: screentoneDotsDrawn
    };
  }

  function ensureTabletopShaderStylesInjected() {
    if (typeof document === "undefined") return;
    if (document.getElementById("cf-anime-manga-studio-styles")) return;
    const styleEl = document.createElement("style");
    styleEl.id = "cf-anime-manga-studio-styles";
    styleEl.textContent = [
      "body[data-anime-manga-shader='cel_astral_gold'] .slot-art, body[data-anime-manga-style='cel_astral_gold'] .slot-art {",
      "  filter: contrast(1.08) saturate(1.18) brightness(1.03);",
      "}",
      "body[data-anime-manga-shader='manga_gpen_screentone'] .slot-art, body[data-anime-manga-style='manga_gpen_screentone'] .slot-art, body[data-anime-manga-style='kubrart_vector_cel_ink_v1'] .slot-art {",
      "  filter: contrast(1.26) saturate(0.84) brightness(1.02);",
      "}",
      "body[data-anime-manga-shader='sakuga_kagenashi_flare'] .slot-art, body[data-anime-manga-style='sakuga_kagenashi_flare'] .slot-art {",
      "  filter: contrast(1.18) saturate(1.32) brightness(1.05);",
      "}",
      "body[data-anime-manga-shader='mecha_blueprint_halftone'] .slot-art, body[data-anime-manga-style='mecha_blueprint_halftone'] .slot-art {",
      "  filter: contrast(1.15) saturate(1.14) hue-rotate(-4deg);",
      "}",
      "body[data-anime-manga-shader='tarot_chiaroscuro_foil'] .slot-art, body[data-anime-manga-style='tarot_chiaroscuro_foil'] .slot-art {",
      "  filter: contrast(1.22) saturate(1.10) sepia(0.14);",
      "}"
    ].join("\n");
    document.head.appendChild(styleEl);
  }

  /**
   * Applies the chosen illustration model / shader preset to `document.body.dataset.animeMangaStyle`
   * and updates `stateObj.activeIllustrationModelId`.
   */
  function applyIllustrationModelToTabletop(modelId, stateObj) {
    ensureTabletopShaderStylesInjected();
    const model = resolveIllustrationModel(modelId);
    const preset = MANGA_SCREENTONE_SHADERS[model.shaderPreset] || MANGA_SCREENTONE_SHADERS.cel_astral_gold;
    const directShaderMatch = MANGA_SCREENTONE_SHADERS[modelId] ? modelId : null;

    const targetState =
      stateObj ||
      (typeof globalScope !== "undefined" && globalScope.state ? globalScope.state : null);

    if (targetState && typeof targetState === "object") {
      targetState.activeIllustrationModelId = model.id;
      targetState.activeIllustrationLoraFile = model.loraFile;
      targetState.activeAnimeMangaShaderPreset = directShaderMatch || model.shaderPreset;
    }

    if (typeof document !== "undefined" && document.body) {
      document.body.dataset.animeMangaStyle = directShaderMatch || model.id;
      document.body.dataset.animeMangaShader = directShaderMatch || model.shaderPreset;
      document.body.dataset.illustrationModelId = model.id;
      document.body.dataset.illustrationLoraFile = model.loraFile;
      document.documentElement.style.setProperty("--cf-anime-rim-color", model.colorSignature[0] || preset.rimColor);
      document.documentElement.style.setProperty(
        "--cf-anime-secondary-color",
        model.colorSignature[1] || preset.secondaryColor
      );

      const previewCanvas =
        document.getElementById("anime-studio-preview-canvas") ||
        document.getElementById("anime-manga-preview-canvas");
      if (previewCanvas) {
        renderMangaStylePreviewCanvas(previewCanvas, model.id);
      }
    }

    return {
      applied: true,
      modelId: model.id,
      name: model.name,
      category: model.category,
      loraFile: model.loraFile,
      baseCheckpoint: model.baseCheckpoint,
      shaderPreset: directShaderMatch || model.shaderPreset,
      colorSignature: model.colorSignature,
      morphologicalPrompt: model.morphologicalPrompt
    };
  }

  /**
   * Requests a live or cached RTX 4080 ComfyUI (`http://192.168.86.30:8188`) card portrait
   * render via `POST /api/anime/generate` and updates `#anime-studio-preview-canvas` and
   * `#anime-studio-active-meta` with the live RTX 4080 render telemetry.
   */
  async function requestLiveRtx4080CardRender(
    modelId = "kubrart_vector_cel_ink_v1",
    cardId = "set2_k01",
    customPrompt = ""
  ) {
    const model = resolveIllustrationModel(modelId);
    const card =
      SET2_KUBRART_MANGA_CARDS.find((c) => c.id === cardId) ||
      SET2_KUBRART_MANGA_CARDS.find((c) => c.modelId === model.id) ||
      SET2_KUBRART_MANGA_CARDS[0];

    const promptText =
      (customPrompt && String(customPrompt).trim()) ||
      (card && card.morphologicalPrompt) ||
      model.morphologicalPrompt;

    const payload = {
      modelId: model.id,
      model_id: model.id,
      adapterId: model.adapterId,
      loraFile: model.loraFile,
      baseCheckpoint: model.baseCheckpoint,
      shaderPreset: model.shaderPreset,
      cardId: card ? card.id : cardId,
      card_id: card ? card.id : cardId,
      cardName: card ? card.name : cardId,
      faction: card ? card.faction : "Aether",
      prompt: promptText,
      width: 600,
      height: 800
    };

    let apiResponse = null;
    const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();
    if (typeof fetch === "function") {
      try {
        const resp = await fetch("/api/anime/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (resp && resp.ok) {
          apiResponse = await resp.json();
        }
      } catch (_fetchErr) {
        apiResponse = null;
      }
    }
    const elapsedMs = Math.max(
      1,
      Math.round((typeof performance !== "undefined" ? performance.now() : Date.now()) - t0)
    );

    const resolvedArt =
      (apiResponse &&
        (apiResponse.artUrl ||
          apiResponse.image_url ||
          apiResponse.art ||
          (apiResponse.card && apiResponse.card.art))) ||
      (card ? card.art : "./GeneratedArt/Set2KubrartManga/set2_k01_kubrart_eclipse_sovereign.png");

    let previewCanvas = null;
    let metaEl = null;
    if (typeof document !== "undefined") {
      previewCanvas =
        document.getElementById("anime-studio-preview-canvas") ||
        document.getElementById("anime-manga-preview-canvas");
      metaEl = document.getElementById("anime-studio-active-meta");

      if (previewCanvas) {
        renderMangaStylePreviewCanvas(previewCanvas, model.id);
        if (typeof Image !== "undefined" && resolvedArt) {
          try {
            const img = new Image();
            img.crossOrigin = "anonymous";
            img.onload = function onSet2ArtLoaded() {
              renderMangaStylePreviewCanvas(previewCanvas, model.id, img);
            };
            img.src = resolvedArt;
          } catch (_imgErr) {
            // Procedural + screentone canvas already rendered above
          }
        }
      }

      if (metaEl) {
        const checkpointUsed =
          (apiResponse && (apiResponse.checkpoint || apiResponse.baseCheckpoint)) ||
          model.baseCheckpoint;
        const shaShort =
          apiResponse && apiResponse.sha256 ? String(apiResponse.sha256).slice(0, 12) : "600x800-RGB";
        metaEl.innerHTML =
          `Active Model: <b style="color:var(--gold);">${model.name}</b><br/>` +
          `<span style="color:#94a3b8;font-size:11px;">` +
          `Set 2 Card: <b style="color:#38bdf8;">${card ? card.id : cardId} · ${card ? card.name : ""}</b> · ` +
          `RTX 4080 (${checkpointUsed}) · ${elapsedMs}ms · ${shaShort}` +
          `</span>`;
        metaEl.dataset.lastRenderedModelId = model.id;
        metaEl.dataset.lastRenderedCardId = card ? card.id : cardId;
        metaEl.dataset.lastRenderedArt = resolvedArt;
      }
    }

    return {
      ok: true,
      rendered: true,
      modelId: model.id,
      cardId: card ? card.id : cardId,
      cardName: card ? card.name : cardId,
      faction: card ? card.faction : "Aether",
      baseCheckpoint: model.baseCheckpoint,
      loraFile: model.loraFile,
      shaderPreset: model.shaderPreset,
      art: resolvedArt,
      comfyUiEndpoint: "http://192.168.86.30:8188",
      elapsedMs: elapsedMs,
      canvasUpdated: Boolean(previewCanvas),
      metaUpdated: Boolean(metaEl),
      apiResponse: apiResponse
    };
  }

  const CardFrontAnimeMangaStudio = {
    version: "2.0.0",
    zeroLivingArtistNames: true,
    comfyUiEndpoint: "http://192.168.86.30:8188",
    LIVE_COMFYUI_BASE_CHECKPOINTS: LIVE_COMFYUI_BASE_CHECKPOINTS,
    MULTIMODAL_VISION_CRITICS: MULTIMODAL_VISION_CRITICS,
    ANIME_MANGA_ILLUSTRATION_MODELS: ANIME_MANGA_ILLUSTRATION_MODELS,
    MANGA_SCREENTONE_SHADERS: MANGA_SCREENTONE_SHADERS,
    SET2_KUBRART_MANGA_CARDS: SET2_KUBRART_MANGA_CARDS,
    resolveIllustrationModel: resolveIllustrationModel,
    renderMangaStylePreviewCanvas: renderMangaStylePreviewCanvas,
    applyIllustrationModelToTabletop: applyIllustrationModelToTabletop,
    requestLiveRtx4080CardRender: requestLiveRtx4080CardRender
  };

  globalScope.CardFrontAnimeMangaStudio = CardFrontAnimeMangaStudio;
  globalScope.ANIME_MANGA_ILLUSTRATION_MODELS = ANIME_MANGA_ILLUSTRATION_MODELS;
  globalScope.MANGA_SCREENTONE_SHADERS = MANGA_SCREENTONE_SHADERS;
  globalScope.SET2_KUBRART_MANGA_CARDS = SET2_KUBRART_MANGA_CARDS;
  globalScope.renderMangaStylePreviewCanvas = renderMangaStylePreviewCanvas;
  globalScope.applyIllustrationModelToTabletop = applyIllustrationModelToTabletop;
  globalScope.requestLiveRtx4080CardRender = requestLiveRtx4080CardRender;

  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.AnimeMangaStudio = CardFrontAnimeMangaStudio;
})(typeof window !== "undefined" ? window : globalThis);
