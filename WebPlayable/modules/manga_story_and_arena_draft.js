/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes — 19-Chapter Dynamic 3-Panel Manga Cutscene
 * Engine & 5-Round Roguelite Arena Draft Mode (117-Card Pool)
 * Module: WebPlayable/modules/manga_story_and_arena_draft.js
 *
 * Exposes `window.CardFrontMangaCutsceneAndDraft`,
 * `window.CardFrontModules.MangaCutsceneAndDraft`, and top-level globals:
 *   - `MANGA_CHAPTER_CUTSCENES` (19 chapters x 3 panels = 57 panels)
 *   - `openMangaChapterCutscene(chapterIdx = 0)`
 *   - `advanceMangaCutscenePanel()`
 *   - `closeMangaCutsceneModal()`
 *   - `ARENA_DRAFT_STATE` ({ active, round, maxRounds: 5, draftedCards, currentPack, gauntletWins, gauntletLosses, eloRating: 1600 })
 *   - `openRogueliteArenaDraftModal()`
 *   - `pickArenaDraftCard(cardId)`
 *   - `launchArenaDraftGauntletMatch()`
 *   - `closeArenaDraftModal()`
 *
 * Zero Generic Unicode Emojis — all badges and icons use crisp ASCII tags
 * (`[ACT I]`, `[KUBRART DRAFT]`, etc.) and inline 256x256 vector SVGs.
 * ============================================================================ */

(function initMangaStoryAndArenaDraft(globalScope) {
  "use strict";

  const MODULE_VERSION = "1.0.0";

  // ==========================================================================
  // 0. INLINE 256x256 SVG ICON HELPERS (ZERO UNICODE EMOJIS)
  // ==========================================================================
  const MANGA_DRAFT_SVG_ICONS = {
    manga_quill:
      '<polygon points="36,220 92,196 220,68 188,36 60,164" fill="#0F172A" stroke="#00E5FF" stroke-width="12" stroke-linejoin="round"/>' +
      '<line x1="36" y1="220" x2="116" y2="140" stroke="#FFB800" stroke-width="8"/>' +
      '<polygon points="188,36 220,68 236,52 204,20" fill="#FF2E54" stroke="#FFE082" stroke-width="6"/>' +
      '<circle cx="76" cy="180" r="8" fill="#00E5FF"/>',
    manga_panel_grid:
      '<polygon points="20,24 148,24 128,232 20,232" fill="#0F172A" stroke="#00E5FF" stroke-width="10" stroke-linejoin="round"/>' +
      '<polygon points="164,24 236,24 236,120 148,120" fill="#1E293B" stroke="#FFB800" stroke-width="10" stroke-linejoin="round"/>' +
      '<polygon points="144,136 236,136 236,232 132,232" fill="#0F172A" stroke="#FF2E54" stroke-width="10" stroke-linejoin="round"/>',
    arena_draft_crest:
      '<polygon points="128,16 228,68 204,196 128,240 52,196 28,68" fill="#0F172A" stroke="#FFB800" stroke-width="12" stroke-linejoin="round"/>' +
      '<rect x="64" y="68" width="52" height="72" rx="6" transform="rotate(-12 90 104)" fill="#1E293B" stroke="#00E5FF" stroke-width="8"/>' +
      '<rect x="140" y="68" width="52" height="72" rx="6" transform="rotate(12 166 104)" fill="#1E293B" stroke="#FF2E54" stroke-width="8"/>' +
      '<rect x="102" y="56" width="52" height="76" rx="6" fill="#0F172A" stroke="#FFB800" stroke-width="9"/>' +
      '<circle cx="128" cy="94" r="11" fill="#2EE6D3"/>',
    speed_burst:
      '<polygon points="128,16 154,90 232,68 176,128 232,188 154,166 128,240 102,166 24,188 80,128 24,68 102,90" fill="#FF2E54" stroke="#FFE082" stroke-width="8" stroke-linejoin="round"/>' +
      '<circle cx="128" cy="128" r="24" fill="#00E5FF"/>'
  };

  function renderSvgIcon(iconKey, sizePx, extraStyle) {
    const sz = Number(sizePx) || 14;
    const body = MANGA_DRAFT_SVG_ICONS[iconKey] || MANGA_DRAFT_SVG_ICONS.manga_panel_grid;
    const st = extraStyle ? String(extraStyle) : "";
    return (
      '<svg class="cf-manga-draft-icon" data-icon="' +
      String(iconKey || "manga_panel_grid") +
      '" width="' +
      sz +
      '" height="' +
      sz +
      '" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0;' +
      st +
      '">' +
      body +
      "</svg>"
    );
  }

  // ==========================================================================
  // 1. STYLE PRESETS FOR 3-PANEL MANGA ENGINE
  // ==========================================================================
  const MANGA_STYLE_PRESETS = {
    kubrart_vector_cel: {
      id: "kubrart_vector_cel",
      tag: "[KUBRART VECTOR-CEL]",
      name: "Kubrart Graphic Vector-Cel & Stark Ink Silhouette",
      borderHex: "#00E5FF",
      accentHex: "#FF2E54",
      inkBg: "linear-gradient(155deg, #070B14 0%, #0F172A 62%, #1E1B4B 100%)",
      portraitFilter: "contrast(1.24) saturate(1.18) brightness(1.03)",
      halftoneColor: "rgba(0, 229, 255, 0.24)",
      speedlineColor: "rgba(255, 46, 84, 0.34)",
      balloonBorder: "#00E5FF",
      sfxColor: "#FF2E54"
    },
    seinen_gpen_ink: {
      id: "seinen_gpen_ink",
      tag: "[SEINEN G-PEN INK]",
      name: "Seinen High-Contrast G-Pen Crosshatch & 60-LPI Screentone",
      borderHex: "#FFE082",
      accentHex: "#D12D3A",
      inkBg: "linear-gradient(155deg, #05070B 0%, #111827 65%, #1F2937 100%)",
      portraitFilter: "contrast(1.36) saturate(0.76) brightness(1.02)",
      halftoneColor: "rgba(248, 250, 252, 0.26)",
      speedlineColor: "rgba(255, 224, 130, 0.28)",
      balloonBorder: "#FFE082",
      sfxColor: "#FFB800"
    },
    sakuga_24fps_flare: {
      id: "sakuga_24fps_flare",
      tag: "[SAKUGA 24FPS FLARE]",
      name: "24fps Sakuga Kagenashi Rim-Light & Star-Flare Burst",
      borderHex: "#FF2E54",
      accentHex: "#00E5FF",
      inkBg: "linear-gradient(155deg, #090D1A 0%, #1E1028 58%, #0F172A 100%)",
      portraitFilter: "contrast(1.18) saturate(1.34) brightness(1.06)",
      halftoneColor: "rgba(255, 46, 84, 0.24)",
      speedlineColor: "rgba(0, 229, 255, 0.36)",
      balloonBorder: "#FF2E54",
      sfxColor: "#00E5FF"
    }
  };

  // ==========================================================================
  // 2. 19-CHAPTER DYNAMIC 3-PANEL MANGA STORY CUTSCENES (57 TOTAL PANELS)
  //    Matching Shifting Pieces / Cradle of Echoes:
  //    - Act I: Okitsu Discovery (Chapters 1..6)
  //    - Act II: Memory Theatre & Shadow Maze (Chapters 7..15)
  //    - Act III: Hall of Selves & Red Scarf Convergence (Chapters 16..19)
  // ==========================================================================
  const PORTRAIT_MAP = {
    kai: "./GeneratedArt/sp_01_kai_nakamura_rtx4080.png",
    aiko: "./GeneratedArt/sp_02_aiko_nakamura_scarf_rtx4080.png",
    fox: "./GeneratedArt/sp_03_mnemosyne_fox_rtx4080.png",
    luna: "./GeneratedArt/sp_04_luna_tarot_rtx4080.png",
    taro: "./GeneratedArt/sp_05_taro_fujimoto_rtx4080.png",
    asakura: "./GeneratedArt/sp_06_dr_rina_asakura_rtx4080.png",
    kubrart: "./GeneratedArt/AnimeMangaModels/style_kubrart_vector_cel_ink.png",
    archangel: "./GeneratedArt/MasteredCards/h_archangel.png",
    oracle: "./GeneratedArt/MasteredCards/h_oracle.png",
    eclipse: "./GeneratedArt/MasteredCards/e_eclipse.png"
  };

  const MANGA_CHAPTER_CUTSCENES = [
    {
      chapter: 1,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 01: Fragments of Dust (Disconnected in Okitsu)",
      stageIndex: 0,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Taro Fujimoto [Intercom]",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "Kai? I left warm curry and green tea by the door. The rain is coming in off the Okitsu seawall — do not stay locked inside all week.",
          sfxKatakanaRomanized: "ZAAA // SEAWALL RAIN",
          speedlineAngle: -18,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Three months since Aiko vanished, and every Rubik cube in this apartment is already solved... except the neural headset she left on my desk.",
          sfxKatakanaRomanized: "DOKUN // HEARTBEAT",
          speedlineAngle: 14,
          halftoneDensity: 0.28
        },
        {
          panelNumber: 3,
          speaker: "Mnemosyne Terminal",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "[ENCRYPTED HANDSHAKE VERIFIED] Welcome to Mnemosyne. A tactical game of memory — designed exclusively for you.",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -26,
          halftoneDensity: 0.38
        }
      ]
    },
    {
      chapter: 2,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 02: Residual Code (Aiko's Lacquered Puzzle Box)",
      stageIndex: 1,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Aiko Nakamura [Hologram]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Happy thirteenth birthday, Kai! Remember the rule: you are only allowed to unseal this puzzle box when you are ready to be honest with yourself.",
          sfxKatakanaRomanized: "KIRAN // HOLOGRAM",
          speedlineAngle: -12,
          halftoneDensity: 0.24
        },
        {
          panelNumber: 2,
          speaker: "Taro Fujimoto",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "That neural tree etched into your visor is not commercial firmware, Kai. Whatever Aiko built before she disappeared, it is waking up.",
          sfxKatakanaRomanized: "GOGOGO // HUM",
          speedlineAngle: 20,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "The 4-directional latch sequence matches our cliffside hex hike. She did not leave a goodbye note — she left coordinates.",
          sfxKatakanaRomanized: "KACHIN // UNSEAL",
          speedlineAngle: -22,
          halftoneDensity: 0.34
        }
      ]
    },
    {
      chapter: 3,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 03: Invitation to Mnemosyne (Station of Awakening)",
      stageIndex: 2,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "LUNA [Cradle of Echoes]",
          portraitUrl: PORTRAIT_MAP.luna,
          dialogue:
            "Step onto the stained-glass floor of Nocturna, seeker. Three tarot archetypes orbit your awakening: Conviction, Sanctuary, and Eternity.",
          sfxKatakanaRomanized: "SHUWA // ASTRAL BELL",
          speedlineAngle: -15,
          halftoneDensity: 0.26
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "The directional glyphs stop spinning when I slow my breathing. Brute force scrambles the lock — emotional calm aligns the stained glass.",
          sfxKatakanaRomanized: "SUUU // FOCUS",
          speedlineAngle: 10,
          halftoneDensity: 0.22
        },
        {
          panelNumber: 3,
          speaker: "LUNA [Cradle of Echoes]",
          portraitUrl: PORTRAIT_MAP.luna,
          dialogue:
            "Your 95% Persona Seal is bound to The Strategist and The Architect. Enter the Memory Architecture System.",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -28,
          halftoneDensity: 0.36
        }
      ]
    },
    {
      chapter: 4,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 04: The First Level (Cliffside Red Scarf Reveal)",
      stageIndex: 3,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Mnemosyne Core",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "CHAMBER 01: ORDER FROM CHAOS. Align the floating stone and glass vectors above the starless Okitsu sea.",
          sfxKatakanaRomanized: "GOGOGO // TECTONIC",
          speedlineAngle: -20,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 2,
          speaker: "Aiko Nakamura [Memory Echo]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Look at the waves below the seawall, Kai. Even when the tide looks chaotic, there is a rhythm underneath. You found the pattern.",
          sfxKatakanaRomanized: "HYUUU // SEA WIND",
          speedlineAngle: 16,
          halftoneDensity: 0.25
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Her crimson scarf (#D12D3A)... the wind off the cliff felt completely real. That was not a pre-rendered cutscene — she is inside the code.",
          sfxKatakanaRomanized: "BA-DUMP // SCARF SNAP",
          speedlineAngle: -24,
          halftoneDensity: 0.35
        }
      ]
    },
    {
      chapter: 5,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 05: Flicker (Rain-Slicked Lantern Alley)",
      stageIndex: 4,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "The neon kanji on the wet pavement are flickering at 42 Hz — the exact clock frequency of Aiko's neural compiler.",
          sfxKatakanaRomanized: "BZZT // 42HZ STATIC",
          speedlineAngle: -14,
          halftoneDensity: 0.34
        },
        {
          panelNumber: 2,
          speaker: "Taro Fujimoto [Voiceover]",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "Promise me you will not chase a ghost so deep into the grid that you forget how to breathe real air, Kai.",
          sfxKatakanaRomanized: "ZAAA // DOWNPOUR",
          speedlineAngle: 18,
          halftoneDensity: 0.31
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura [Flicker Echo]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Follow the crimson thread through the static, little brother... before Sector 05 overwrites.",
          sfxKatakanaRomanized: "SHING // RED THREAD",
          speedlineAngle: -25,
          halftoneDensity: 0.38
        }
      ]
    },
    {
      chapter: 6,
      actTitle: "[ACT I] OKITSU DISCOVERY — AWAKENING THE SYSTEM",
      chapterTitle: "Ch 06: Phantom Signals & Memory Bloom",
      stageIndex: 5,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Wind chimes from grandmother's porch, the Okitsu rail crossing, the surf against the breakwater... each sound maps to a shadow game Aiko taught me.",
          sfxKatakanaRomanized: "CHIRIN // WIND CHIME",
          speedlineAngle: -10,
          halftoneDensity: 0.22
        },
        {
          panelNumber: 2,
          speaker: "Aiko Nakamura [Live Signal]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "You remembered the chime sequence, Kai... You actually found me across the conservatory.",
          sfxKatakanaRomanized: "DOKUN // RESONANCE",
          speedlineAngle: 22,
          halftoneDensity: 0.28
        },
        {
          panelNumber: 3,
          speaker: "Mnemosyne Core",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "[ACT I COMPLETE — MEMORY BLOOM UNLOCKED] Card Acquired: Aiko Nakamura, Red Scarf Echo (#D12D3A).",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -30,
          halftoneDensity: 0.36
        }
      ]
    },
    {
      chapter: 7,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 07: Memory Theatre (Summer Festival Lanterns)",
      stageIndex: 6,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "Mnemosyne Stage Director",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "ACT II: FRACTURED MEMORIES. Chronology is a cage; arrange these festival lanterns by the emotional weight they left on your heart.",
          sfxKatakanaRomanized: "DON // TAIKO DRUM",
          speedlineAngle: -16,
          halftoneDensity: 0.26
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Paper lanterns (#FFB648) rising over the deep ocean (#0A2230)... Aiko held my hand when I lost sight of grandmother in the crowd.",
          sfxKatakanaRomanized: "FUWA // LANTERN GLOW",
          speedlineAngle: 14,
          halftoneDensity: 0.24
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura [Echo]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Joy hurts the sharpest when you look back at it from the dark, Kai. Do not look away.",
          sfxKatakanaRomanized: "SHING // FLARE",
          speedlineAngle: -22,
          halftoneDensity: 0.32
        }
      ]
    },
    {
      chapter: 8,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 08: Artifacts (Kitchen Table Contradiction)",
      stageIndex: 7,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Wait. In this replay, Father is smiling and the porcelain teacup is not cracked. Why did Mnemosyne edit out the shouting match?",
          sfxKatakanaRomanized: "PISHI // HAIRLINE CRACK",
          speedlineAngle: -19,
          halftoneDensity: 0.35
        },
        {
          panelNumber: 2,
          speaker: "Aiko Nakamura [Echo]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "The system tries to anesthetize regret so test subjects stay compliant. If we want the truth, we must choose the cracked cup.",
          sfxKatakanaRomanized: "GOGOGO // GLITCH",
          speedlineAngle: 17,
          halftoneDensity: 0.33
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "I do not want a painless lie. Restore the unedited memory!",
          sfxKatakanaRomanized: "GASHAAN // SHATTER",
          speedlineAngle: -28,
          halftoneDensity: 0.40
        }
      ]
    },
    {
      chapter: 9,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 09: Recalibration (VR Cafe Confrontation)",
      stageIndex: 8,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Taro Fujimoto",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "Look at your hands, Kai! Your pulse spikes every time you unplug. You are treating the real world like a loading screen!",
          sfxKatakanaRomanized: "BAM // DESK SLAM",
          speedlineAngle: -21,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "You think I want to be stuck here?! If I stop solving the 3x3 grid, Aiko's consciousness fragments for good!",
          sfxKatakanaRomanized: "ZASHU // SPARK",
          speedlineAngle: 24,
          halftoneDensity: 0.34
        },
        {
          panelNumber: 3,
          speaker: "Taro Fujimoto",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "Then let me anchor the external diagnostics from the VR Cafe. You do not have to carry the whole server dome alone.",
          sfxKatakanaRomanized: "KACHIN // ANCHOR LOCK",
          speedlineAngle: -14,
          halftoneDensity: 0.26
        }
      ]
    },
    {
      chapter: 10,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 10: Displacement (Refractive Mirror Match)",
      stageIndex: 9,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Doppelganger Kai [Mirror]",
          portraitUrl: PORTRAIT_MAP.eclipse,
          dialogue:
            "Why did you not walk her to the research lab that rainy morning at Okitsu Station? You were too busy staring at a Rubik cube.",
          sfxKatakanaRomanized: "GIN // MIRROR GLARE",
          speedlineAngle: -24,
          halftoneDensity: 0.38
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "I edited that morning out of my own memory... I told myself I was at school, but I was standing right on the platform.",
          sfxKatakanaRomanized: "DOKUN // CONFESSION",
          speedlineAngle: 15,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 3,
          speaker: "LUNA [Cradle of Echoes]",
          portraitUrl: PORTRAIT_MAP.luna,
          dialogue:
            "Guilt acknowledged is no longer a trapdoor. The refractive mirror stabilizes.",
          sfxKatakanaRomanized: "SHUWA // CLEAR",
          speedlineAngle: -18,
          halftoneDensity: 0.25
        }
      ]
    },
    {
      chapter: 11,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 11: The Shadow Maze (Rooftop Stargazing)",
      stageIndex: 10,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Aiko Nakamura [Memory]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "When the house got too loud after Mom and Dad split up, we would climb onto the roof and connect five amber stars into a fox.",
          sfxKatakanaRomanized: "KIRARI // STARLIGHT",
          speedlineAngle: -12,
          halftoneDensity: 0.24
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "If I rotate the suspended debris by one degree — a single +1 Budge — the shadow on the far wall forms the Constellation Fox!",
          sfxKatakanaRomanized: "GACHI // ALIGNMENT",
          speedlineAngle: 20,
          halftoneDensity: 0.29
        },
        {
          panelNumber: 3,
          speaker: "Mnemosyne Core",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "SHADOW MAZE SOLVED. Warning: Sub-stratum dual-waveform audio anomaly detected.",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -26,
          halftoneDensity: 0.35
        }
      ]
    },
    {
      chapter: 12,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 12: Echo AI (Dual-Voice Waveform Sync)",
      stageIndex: 11,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "Echo AI [Distorted Track B]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Kai — do not complete the final compiler — Dr. Rina Asakura is waiting on the outside to harvest the core!",
          sfxKatakanaRomanized: "BZZT // PHASE SHIFT",
          speedlineAngle: -22,
          halftoneDensity: 0.34
        },
        {
          panelNumber: 2,
          speaker: "Aiko Nakamura [Track A]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Two recordings of my voice overlapping out of phase... Synchronize the waveform peaks, Kai!",
          sfxKatakanaRomanized: "SHING // HARMONIC",
          speedlineAngle: 18,
          halftoneDensity: 0.28
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Got it! Both waveforms locked in phase — wait, someone just breached Sector 09 from the corporate intranet!",
          sfxKatakanaRomanized: "GYUUN // BREACH ALARM",
          speedlineAngle: -28,
          halftoneDensity: 0.37
        }
      ]
    },
    {
      chapter: 13,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 13: System Update (Asakura Firewall Intrusion)",
      stageIndex: 12,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Dr. Rina Asakura",
          portraitUrl: PORTRAIT_MAP.asakura,
          dialogue:
            "Impressive neural plasticity, Kai Nakamura. Your sister's MAS architecture was dormant until your grief indexed it for us.",
          sfxKatakanaRomanized: "GOGOGO // FIREWALL",
          speedlineAngle: -24,
          halftoneDensity: 0.36
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Aiko is not your corporate intellectual property! You are tearing the memory sectors apart!",
          sfxKatakanaRomanized: "ZASHU // OVERDRIVE",
          speedlineAngle: 22,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura [Echo]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Grab Encrypted Journal [Log: A-09] from the center node, Kai! Do not let her extraction daemon quarantine it!",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -30,
          halftoneDensity: 0.39
        }
      ]
    },
    {
      chapter: 14,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 14: Reconciliation Loop (The Unspoken Truth)",
      stageIndex: 13,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Memory Replay [Loop #14]",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "'I am fine, Aiko! Go to your lab!' — [TIMELINE RESET: DEFENSIVE LIE DETECTED].",
          sfxKatakanaRomanized: "KACHIN // REWIND",
          speedlineAngle: -18,
          halftoneDensity: 0.36
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Every time I repeat what I actually said that night, the corridor resets. The lock is asking for what I hid.",
          sfxKatakanaRomanized: "DOKUN // PULSE",
          speedlineAngle: 14,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "I was terrified you were leaving me behind, Aiko! I was angry, and I was scared, and I never got to say I am sorry!",
          sfxKatakanaRomanized: "PARIN // LOOP SHATTER",
          speedlineAngle: -28,
          halftoneDensity: 0.40
        }
      ]
    },
    {
      chapter: 15,
      actTitle: "[ACT II] MEMORY THEATRE & SHADOW MAZE — FRACTURED MEMORIES",
      chapterTitle: "Ch 15: The Core Fracture & The Unchosen Memory",
      stageIndex: 14,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "Dr. Rina Asakura",
          portraitUrl: PORTRAIT_MAP.asakura,
          dialogue:
            "Core containment at 18%. Sever the brother's neural link and extract the Mnemosyne kernel now!",
          sfxKatakanaRomanized: "GA-GA-GA // TECTONIC",
          speedlineAngle: -25,
          halftoneDensity: 0.35
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "The lab floor is shattering into void polygons — if I bridge the diagonal shards, I can shield Aiko's core!",
          sfxKatakanaRomanized: "SHING // BRIDGE",
          speedlineAngle: 20,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura [Interlude]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Before the fall... remember the quiet rooftop night when we did not solve anything at all? We just watched the Constellation Fox (#FFB648) until dawn.",
          sfxKatakanaRomanized: "FUWA // DAWN STAR",
          speedlineAngle: -12,
          halftoneDensity: 0.22
        }
      ]
    },
    {
      chapter: 16,
      actTitle: "[ACT III] HALL OF SELVES & RED SCARF CONVERGENCE",
      chapterTitle: "Ch 16: Awakening (Ocean of Broken Data Shards)",
      stageIndex: 15,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "ACT III. The simulated town is gone — just an endless ocean of violet static (#8A5BFF) and broken hexagonal data shards.",
          sfxKatakanaRomanized: "ZAAA // VIOLET VOID",
          speedlineAngle: -20,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 2,
          speaker: "Taro Fujimoto [External Comms]",
          portraitUrl: PORTRAIT_MAP.taro,
          dialogue:
            "Kai, I am reading your bio-telemetry from the cafe! Stop calculating the tiles like an algorithm — feel where Aiko's crimson scarf thread is pulling!",
          sfxKatakanaRomanized: "PI-PI-PI // TELEMETRY",
          speedlineAngle: 18,
          halftoneDensity: 0.28
        },
        {
          panelNumber: 3,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "When I trust emotional intuition instead of cold math, the hex platforms lock beneath my feet. The Hall of Selves is straight ahead.",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -26,
          halftoneDensity: 0.36
        }
      ]
    },
    {
      chapter: 17,
      actTitle: "[ACT III] HALL OF SELVES & RED SCARF CONVERGENCE",
      chapterTitle: "Ch 17: The Hall of Selves (Four Doors of Denial)",
      stageIndex: 16,
      stylePreset: "seinen_gpen_ink",
      panels: [
        {
          panelNumber: 1,
          speaker: "Fractured Selves [Doors I-IV]",
          portraitUrl: PORTRAIT_MAP.eclipse,
          dialogue:
            "Door I: Indifference. Door II: Anger. Door III: Fear. Door IV: Mirror Kai walking away forever.",
          sfxKatakanaRomanized: "GOGOGO // FOUR DOORS",
          speedlineAngle: -24,
          halftoneDensity: 0.38
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "You are not enemies I have to delete. You are all parts of me that tried to survive losing her.",
          sfxKatakanaRomanized: "DOKUN // INTEGRATION",
          speedlineAngle: 16,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 3,
          speaker: "Mnemosyne Core",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "[FOURFOLD SELF INTEGRATED] The center mirror shatters beneath the Constellation Fox. The Sanctum of the Memory Architect opens.",
          sfxKatakanaRomanized: "GASHAAN // UNSEAL",
          speedlineAngle: -30,
          halftoneDensity: 0.39
        }
      ]
    },
    {
      chapter: 18,
      actTitle: "[ACT III] HALL OF SELVES & RED SCARF CONVERGENCE",
      chapterTitle: "Ch 18: The Memory Architect (Logs A-09, A-14, A-21)",
      stageIndex: 17,
      stylePreset: "sakuga_24fps_flare",
      panels: [
        {
          panelNumber: 1,
          speaker: "Aiko Nakamura [Memory Architect]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "Welcome to the compiler, Kai. Every puzzle you solved across Mnemosyne wove another thread of my scattered neural imprint back together.",
          sfxKatakanaRomanized: "SHUWA // JASMINE SANCTUM",
          speedlineAngle: -14,
          halftoneDensity: 0.25
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Log A-09, Log A-14, Log A-21... You did not vanish by accident. You uploaded your own neural pattern into the MAS core to shield the beta subjects!",
          sfxKatakanaRomanized: "ZASHU // REVELATION",
          speedlineAngle: 22,
          halftoneDensity: 0.32
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura [Log: A-21]",
          portraitUrl: PORTRAIT_MAP.aiko,
          dialogue:
            "[Log: A-21] 'Even if I am only an echo of code and crimson thread... maybe he will remember how it felt to be loved. That is enough.'",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -28,
          halftoneDensity: 0.36
        }
      ]
    },
    {
      chapter: 19,
      actTitle: "[ACT III] HALL OF SELVES & RED SCARF CONVERGENCE",
      chapterTitle: "Ch 19: The Shifting Truth (Convergence & Triad Choice)",
      stageIndex: 18,
      stylePreset: "kubrart_vector_cel",
      panels: [
        {
          panelNumber: 1,
          speaker: "Dr. Rina Asakura",
          portraitUrl: PORTRAIT_MAP.asakura,
          dialogue:
            "She is a finite simulation, Kai! Let the corporation archive her kernel, or the entire Mnemosyne lattice will collapse under its own recursion!",
          sfxKatakanaRomanized: "GOGOGO // CORE OVERLOAD",
          speedlineAngle: -26,
          halftoneDensity: 0.37
        },
        {
          panelNumber: 2,
          speaker: "Kai Nakamura",
          portraitUrl: PORTRAIT_MAP.kai,
          dialogue:
            "Memory is not corporate property, Dr. Asakura — and grief is not a bug to be patched out. Connection is what makes us real!",
          sfxKatakanaRomanized: "SHING // GOLDEN FOX",
          speedlineAngle: 20,
          halftoneDensity: 0.30
        },
        {
          panelNumber: 3,
          speaker: "Aiko Nakamura & LUNA",
          portraitUrl: PORTRAIT_MAP.fox,
          dialogue:
            "The Three Gates open before you, Kai: [GATE I: MERGE], [GATE II: PRESERVE], [GATE III: AWAKEN IN OKITSU WITH THE GOLDEN FOX TILE (#FFB648)].",
          sfxKatakanaRomanized: "DOOM // ZASHU",
          speedlineAngle: -32,
          halftoneDensity: 0.40
        }
      ]
    }
  ];

  // ==========================================================================
  // 3. MANGA CUTSCENE RUNTIME STATE, WEBAUDIO VOICE CADENCE & MODAL RENDERER
  // ==========================================================================
  const MANGA_CUTSCENE_STATE = {
    active: false,
    chapterIndex: 0, // 0..18
    activePanelIndex: 0, // 0..2
    overrideStylePreset: null
  };

  function playMangaVoiceCadenceBleep(panelIdx, stylePresetId) {
    try {
      const actx = globalScope.actx;
      if (globalScope.state && globalScope.state.muted) return;
      if (typeof globalScope.playTone === "function") {
        const baseSemi = panelIdx === 0 ? 2 : panelIdx === 1 ? 5 : 9;
        const wave = stylePresetId === "seinen_gpen_ink" ? "sawtooth" : "triangle";
        globalScope.playTone(baseSemi, wave, 0.11, false);
        setTimeout(function () {
          if (typeof globalScope.playTone === "function") {
            globalScope.playTone(baseSemi + 4, "sine", 0.09, false);
          }
        }, 65);
        return;
      }
      if (!actx || typeof actx.createOscillator !== "function") return;
      const now = actx.currentTime || 0;
      const osc = actx.createOscillator();
      const gain = actx.createGain();
      osc.type = stylePresetId === "kubrart_vector_cel" ? "square" : "triangle";
      const freq = 360 + (Number(panelIdx) || 0) * 90;
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(freq * 1.18, now + 0.09);
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.08, now + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.095);
      osc.connect(gain);
      gain.connect(actx.destination);
      osc.start(now);
      osc.stop(now + 0.1);
    } catch (_) {}
  }

  function buildSpeedlineSvg(angleDeg, strokeColor) {
    const lines = [];
    const totalRays = 28;
    for (let i = 0; i < totalRays; i++) {
      const theta = (i / totalRays) * Math.PI * 2 + (Number(angleDeg || 0) * Math.PI) / 180;
      const rInner = 64 + (i % 3) * 14;
      const rOuter = 240;
      const x1 = (200 + Math.cos(theta) * rInner).toFixed(1);
      const y1 = (150 + Math.sin(theta) * rInner).toFixed(1);
      const x2 = (200 + Math.cos(theta) * rOuter).toFixed(1);
      const y2 = (150 + Math.sin(theta) * rOuter).toFixed(1);
      const sw = (i % 4 === 0 ? 3.2 : 1.5).toFixed(1);
      lines.push(
        '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" stroke="' + strokeColor + '" stroke-width="' + sw + '" stroke-linecap="round"/>'
      );
    }
    return (
      '<svg class="manga-speedline-svg" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true" ' +
      'style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;">' +
      lines.join("") +
      "</svg>"
    );
  }

  function ensureMangaCutsceneModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("manga-cutscene-modal");
    if (!modal && doc.body) {
      modal = doc.createElement("div");
      modal.id = "manga-cutscene-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.setAttribute("aria-label", "19-Chapter Dynamic 3-Panel Manga Cutscene Engine");
      modal.style.cssText =
        "display:none;position:fixed;inset:0;z-index:9850;background:rgba(3,6,14,0.92);" +
        "backdrop-filter:blur(10px);align-items:center;justify-content:center;padding:14px;box-sizing:border-box;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function normalizeChapterIndex(chapterIdx) {
    const raw = Number(chapterIdx);
    if (!Number.isFinite(raw) || raw < 0) return 0;
    if (raw >= 0 && raw < MANGA_CHAPTER_CUTSCENES.length) return Math.floor(raw);
    if (raw === MANGA_CHAPTER_CUTSCENES.length) return MANGA_CHAPTER_CUTSCENES.length - 1;
    return Math.floor(raw) % MANGA_CHAPTER_CUTSCENES.length;
  }

  function renderMangaCutsceneModalContent() {
    const modal = ensureMangaCutsceneModalDom();
    if (!modal) return null;

    const chObj = MANGA_CHAPTER_CUTSCENES[MANGA_CUTSCENE_STATE.chapterIndex] || MANGA_CHAPTER_CUTSCENES[0];
    const presetKey = MANGA_CUTSCENE_STATE.overrideStylePreset || chObj.stylePreset || "kubrart_vector_cel";
    const stylePreset = MANGA_STYLE_PRESETS[presetKey] || MANGA_STYLE_PRESETS.kubrart_vector_cel;
    const activePanelIdx = MANGA_CUTSCENE_STATE.activePanelIndex;

    const clipPolygons = [
      "polygon(0% 0%, 100% 0%, 94% 100%, 0% 100%)",
      "polygon(4% 0%, 100% 0%, 96% 100%, 0% 100%)",
      "polygon(4% 0%, 100% 0%, 100% 100%, 0% 100%)"
    ];

    const chapterOptionsHtml = MANGA_CHAPTER_CUTSCENES.map(function (c, idx) {
      const sel = idx === MANGA_CUTSCENE_STATE.chapterIndex ? ' selected="selected"' : "";
      return '<option value="' + idx + '"' + sel + ">" + c.chapterTitle + "</option>";
    }).join("");

    const presetButtonsHtml = Object.keys(MANGA_STYLE_PRESETS)
      .map(function (k) {
        const p = MANGA_STYLE_PRESETS[k];
        const isCurrent = p.id === stylePreset.id;
        return (
          '<button type="button" class="manga-preset-btn" data-preset="' +
          p.id +
          '" onclick="window.selectMangaCutsceneStylePreset(\'' +
          p.id +
          '\')" style="padding:4px 9px;border-radius:6px;font-size:11px;font-weight:800;cursor:pointer;' +
          "border:1px solid " +
          (isCurrent ? p.borderHex : "rgba(148,163,184,0.35)") +
          ";background:" +
          (isCurrent ? "rgba(0,229,255,0.18)" : "rgba(15,23,42,0.75)") +
          ";color:" +
          (isCurrent ? "#FFFFFF" : "#CBD5E1") +
          ';">' +
          p.tag +
          "</button>"
        );
      })
      .join("");

    const panelsHtml = chObj.panels
      .map(function (p, idx) {
        const isActive = idx === activePanelIdx;
        const isCompleted = idx < activePanelIdx;
        const clipPoly = clipPolygons[idx] || clipPolygons[0];
        const dotSize = Math.max(3, Math.round(8 - (Number(p.halftoneDensity) || 0.28) * 10));
        const borderCol = isActive ? stylePreset.borderHex : isCompleted ? "rgba(46,230,211,0.55)" : "rgba(148,163,184,0.28)";
        const boxShadow = isActive
          ? "0 0 24px " + stylePreset.borderHex + "55, inset 0 0 18px " + stylePreset.accentHex + "33"
          : "none";
        const opacity = isActive ? "1" : isCompleted ? "0.86" : "0.58";

        return (
          '<div class="manga-slanted-panel' +
          (isActive ? " active-manga-panel" : "") +
          '" data-panel-number="' +
          p.panelNumber +
          '" onclick="window.CardFrontMangaCutsceneAndDraft.setActivePanel(' +
          idx +
          ')" style="position:relative;flex:1 1 0;min-width:220px;min-height:360px;background:' +
          stylePreset.inkBg +
          ";border:2px solid " +
          borderCol +
          ";border-radius:8px;overflow:hidden;clip-path:" +
          clipPoly +
          ";box-shadow:" +
          boxShadow +
          ";opacity:" +
          opacity +
          ';transition:all 0.22s ease;cursor:pointer;display:flex;flex-direction:column;justify-content:space-between;">' +
          // SVG Radial Speedlines
          buildSpeedlineSvg(p.speedlineAngle, stylePreset.speedlineColor) +
          // Halftone Dot-Matrix Overlay
          '<div class="manga-halftone-overlay" style="position:absolute;inset:0;pointer-events:none;z-index:2;' +
          "background-image:radial-gradient(" +
          stylePreset.halftoneColor +
          " 1.25px, transparent 1.25px);background-size:" +
          dotSize +
          "px " +
          dotSize +
          "px;opacity:" +
          (Number(p.halftoneDensity) || 0.28) +
          ';"></div>' +
          // Top Panel Header & SFX Katakana Romanized Stamp
          '<div style="position:relative;z-index:4;display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(3,7,18,0.78);border-bottom:1px solid rgba(148,163,184,0.22);">' +
          '<span style="font-size:11px;font-weight:900;letter-spacing:0.08em;color:' +
          stylePreset.borderHex +
          ';">[PANEL 0' +
          p.panelNumber +
          "]</span>" +
          '<span class="manga-sfx-stamp" style="font-size:11px;font-weight:900;letter-spacing:0.06em;padding:2px 7px;border-radius:4px;background:rgba(15,23,42,0.92);border:1px solid ' +
          stylePreset.sfxColor +
          ";color:" +
          stylePreset.sfxColor +
          ';transform:skewX(-10deg);">' +
          p.sfxKatakanaRomanized +
          "</span>" +
          "</div>" +
          // Character Portrait Cut-In Frame
          '<div style="position:relative;z-index:3;flex:1;display:flex;align-items:center;justify-content:center;padding:10px;overflow:hidden;">' +
          '<img src="' +
          p.portraitUrl +
          '" alt="' +
          p.speaker +
          '" style="width:100%;max-width:210px;height:200px;object-fit:cover;object-position:center 18%;border-radius:8px;border:2px solid ' +
          borderCol +
          ";filter:" +
          stylePreset.portraitFilter +
          ';" onerror="this.style.display=\'none\'"/>' +
          "</div>" +
          // Dramatic Manga Speech Balloon
          '<div class="manga-speech-balloon" style="position:relative;z-index:4;margin:8px 12px 12px 12px;padding:10px 12px;background:#F8FAFC;color:#090D16;border:2.5px solid ' +
          stylePreset.balloonBorder +
          ';border-radius:14px 14px 14px 4px;box-shadow:4px 4px 0px rgba(9,13,22,0.92);">' +
          '<div style="font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:0.06em;color:#0F172A;margin-bottom:4px;border-bottom:1px solid rgba(15,23,42,0.18);padding-bottom:2px;">' +
          p.speaker +
          "</div>" +
          '<div class="manga-dialogue-line" style="font-size:12px;line-height:1.42;font-weight:700;color:#0F172A;">' +
          p.dialogue +
          "</div>" +
          "</div>" +
          "</div>"
        );
      })
      .join("");

    const nextBtnLabel =
      activePanelIdx < 2
        ? "[ADVANCE TO PANEL 0" + (activePanelIdx + 2) + " ->]"
        : "[DEPLOY TO STAGE " + (chObj.stageIndex + 1) + " DUEL (3x3)]";

    modal.innerHTML =
      '<div class="manga-cutscene-sheet" style="width:100%;max-width:1060px;background:linear-gradient(180deg,#0B1120 0%,#060913 100%);border:2px solid ' +
      stylePreset.borderHex +
      ';border-radius:14px;padding:16px;box-shadow:0 20px 60px rgba(0,0,0,0.85);color:#F8FAFC;display:flex;flex-direction:column;gap:12px;">' +
      // Top Header Bar
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-bottom:1px solid rgba(148,163,184,0.24);padding-bottom:10px;">' +
      '<div style="display:flex;flex-direction:column;gap:2px;">' +
      '<div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:900;color:#FFB800;letter-spacing:0.08em;">' +
      renderSvgIcon("manga_quill", 14) +
      "<span>" +
      chObj.actTitle +
      "</span>" +
      "</div>" +
      '<h3 id="manga-cutscene-chapter-title" style="margin:0;font-size:17px;font-weight:900;color:#FFFFFF;">' +
      chObj.chapterTitle +
      "</h3>" +
      "</div>" +
      '<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">' +
      '<label for="manga-chapter-select" style="font-size:11px;font-weight:800;color:#94A3B8;">CHAPTER:</label>' +
      '<select id="manga-chapter-select" onchange="window.openMangaChapterCutscene(parseInt(this.value, 10))" ' +
      'style="background:#0F172A;color:#F8FAFC;border:1px solid #38BDF8;border-radius:6px;padding:4px 8px;font-size:11px;font-weight:800;">' +
      chapterOptionsHtml +
      "</select>" +
      '<button type="button" id="manga-cutscene-close-btn" onclick="window.closeMangaCutsceneModal()" ' +
      'style="padding:5px 10px;border-radius:6px;border:1px solid rgba(248,113,113,0.6);background:rgba(127,29,29,0.45);color:#FCA5A5;font-size:11px;font-weight:900;cursor:pointer;">[CLOSE X]</button>' +
      "</div>" +
      "</div>" +
      // Style Preset Strip
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:rgba(15,23,42,0.72);padding:6px 10px;border-radius:8px;border:1px solid rgba(148,163,184,0.18);">' +
      '<div style="font-size:11px;font-weight:800;color:#94A3B8;">SCREENTONE &amp; LINEWORK SHADER: <strong style="color:' +
      stylePreset.borderHex +
      ';">' +
      stylePreset.name +
      "</strong></div>" +
      '<div style="display:flex;gap:6px;flex-wrap:wrap;">' +
      presetButtonsHtml +
      "</div>" +
      "</div>" +
      // 3-Panel Diagonal Manga Spread
      '<div id="manga-three-panel-spread" style="display:flex;gap:10px;align-items:stretch;justify-content:space-between;flex-wrap:nowrap;overflow-x:auto;">' +
      panelsHtml +
      "</div>" +
      // Bottom Action Controls
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding-top:6px;border-top:1px solid rgba(148,163,184,0.22);">' +
      '<div style="font-size:11px;font-weight:800;color:#CBD5E1;">' +
      "ACTIVE PANEL: <strong id=\"manga-active-panel-indicator\" style=\"color:#00E5FF;\">" +
      (activePanelIdx + 1) +
      " / 3</strong> · CHAPTER <strong style=\"color:#FFB800;\">" +
      chObj.chapter +
      " / 19</strong>" +
      "</div>" +
      '<div style="display:flex;gap:8px;align-items:center;">' +
      '<button type="button" id="manga-prev-chapter-btn" onclick="window.openMangaChapterCutscene(' +
      Math.max(0, MANGA_CUTSCENE_STATE.chapterIndex - 1) +
      ')" style="padding:7px 12px;border-radius:7px;border:1px solid rgba(148,163,184,0.4);background:rgba(15,23,42,0.85);color:#E2E8F0;font-size:11px;font-weight:800;cursor:pointer;">[&lt;- PREV CH]</button>' +
      '<button type="button" id="manga-advance-panel-btn" onclick="window.advanceMangaCutscenePanel()" ' +
      'style="padding:8px 16px;border-radius:7px;border:1px solid ' +
      stylePreset.borderHex +
      ";background:linear-gradient(135deg,#0284C7,#0F172A);color:#FFFFFF;font-size:12px;font-weight:900;cursor:pointer;box-shadow:0 0 14px " +
      stylePreset.borderHex +
      '44;">' +
      nextBtnLabel +
      "</button>" +
      '<button type="button" id="manga-next-chapter-btn" onclick="window.openMangaChapterCutscene(' +
      Math.min(MANGA_CHAPTER_CUTSCENES.length - 1, MANGA_CUTSCENE_STATE.chapterIndex + 1) +
      ')" style="padding:7px 12px;border-radius:7px;border:1px solid rgba(148,163,184,0.4);background:rgba(15,23,42,0.85);color:#E2E8F0;font-size:11px;font-weight:800;cursor:pointer;">[NEXT CH -&gt;]</button>' +
      "</div>" +
      "</div>" +
      "</div>";

    return modal;
  }

  function openMangaChapterCutscene(chapterIdx) {
    const idx = normalizeChapterIndex(chapterIdx === undefined ? 0 : chapterIdx);
    MANGA_CUTSCENE_STATE.active = true;
    MANGA_CUTSCENE_STATE.chapterIndex = idx;
    MANGA_CUTSCENE_STATE.activePanelIndex = 0;
    const chObj = MANGA_CHAPTER_CUTSCENES[idx] || MANGA_CHAPTER_CUTSCENES[0];
    const modal = renderMangaCutsceneModalContent();
    if (modal) {
      modal.style.display = "flex";
    }
    playMangaVoiceCadenceBleep(0, MANGA_CUTSCENE_STATE.overrideStylePreset || chObj.stylePreset);
    return chObj;
  }

  function advanceMangaCutscenePanel() {
    const chObj = MANGA_CHAPTER_CUTSCENES[MANGA_CUTSCENE_STATE.chapterIndex] || MANGA_CHAPTER_CUTSCENES[0];
    if (MANGA_CUTSCENE_STATE.activePanelIndex < 2) {
      MANGA_CUTSCENE_STATE.activePanelIndex += 1;
      renderMangaCutsceneModalContent();
      playMangaVoiceCadenceBleep(
        MANGA_CUTSCENE_STATE.activePanelIndex,
        MANGA_CUTSCENE_STATE.overrideStylePreset || chObj.stylePreset
      );
      return {
        completedCutscene: false,
        chapter: chObj.chapter,
        activePanelNumber: MANGA_CUTSCENE_STATE.activePanelIndex + 1
      };
    }
    closeMangaCutsceneModal();
    if (typeof globalScope.startStage === "function") {
      globalScope.startStage(chObj.stageIndex);
    } else if (globalScope.state && typeof globalScope.state === "object") {
      globalScope.state.stageIndex = chObj.stageIndex;
    }
    return {
      completedCutscene: true,
      chapter: chObj.chapter,
      deployedStageIndex: chObj.stageIndex
    };
  }

  function closeMangaCutsceneModal() {
    MANGA_CUTSCENE_STATE.active = false;
    if (typeof globalScope.document !== "undefined") {
      const modal = globalScope.document.getElementById("manga-cutscene-modal");
      if (modal) {
        modal.style.display = "none";
      }
    }
    return false;
  }

  function selectMangaCutsceneStylePreset(presetId) {
    if (presetId && MANGA_STYLE_PRESETS[presetId]) {
      MANGA_CUTSCENE_STATE.overrideStylePreset = presetId;
      renderMangaCutsceneModalContent();
      playMangaVoiceCadenceBleep(MANGA_CUTSCENE_STATE.activePanelIndex, presetId);
    }
    return MANGA_STYLE_PRESETS[presetId] || MANGA_STYLE_PRESETS.kubrart_vector_cel;
  }

  function setActivePanel(panelIdx) {
    const p = Math.max(0, Math.min(2, Number(panelIdx) || 0));
    MANGA_CUTSCENE_STATE.activePanelIndex = p;
    renderMangaCutsceneModalContent();
    const chObj = MANGA_CHAPTER_CUTSCENES[MANGA_CUTSCENE_STATE.chapterIndex] || MANGA_CHAPTER_CUTSCENES[0];
    playMangaVoiceCadenceBleep(p, MANGA_CUTSCENE_STATE.overrideStylePreset || chObj.stylePreset);
    return p + 1;
  }

  // ==========================================================================
  // 4. 5-ROUND ROGUELITE ARENA DRAFT POOL (117 TOTAL DRAFTABLE CARDS)
  //    - Set 1: Cradle of Echoes Core (60 cards)
  //    - Set 2: Kubrart Astral Eclipse (20 cards)
  //    - Sovereign Agent Command Cards (37 cards)
  // ==========================================================================
  const BASE_16_ROSTER = [
    { id: "h_archangel", name: "Solar Archangel", faction: "Solaris", nesw: [8, 7, 6, 7], art: "./GeneratedArt/MasteredCards/h_archangel.png" },
    { id: "h_phoenix", name: "Phoenix Valkyrie", faction: "Valkyria", nesw: [9, 8, 5, 6], art: "./GeneratedArt/MasteredCards/h_phoenix.png" },
    { id: "h_oracle", name: "Lunar Oracle", faction: "Aether", nesw: [7, 7, 8, 7], art: "./GeneratedArt/MasteredCards/h_oracle.png" },
    { id: "h_chronos", name: "Chronos Weaver", faction: "Chronos", nesw: [6, 8, 7, 7], art: "./GeneratedArt/MasteredCards/h_chronos.png" },
    { id: "h_seraph", name: "Astral Seraph", faction: "Abyss", nesw: [8, 6, 7, 8], art: "./GeneratedArt/MasteredCards/h_seraph.png" },
    { id: "h_kai", name: "Kai Crimson Visor", faction: "Aether", nesw: [7, 8, 6, 7], art: "./GeneratedArt/MasteredCards/h_kai.png" },
    { id: "h_valkyrie", name: "Sky-Wing Striker", faction: "Valkyria", nesw: [8, 8, 5, 6], art: "./GeneratedArt/MasteredCards/h_valkyrie.png" },
    { id: "h_arbiter", name: "Sun Arbiter", faction: "Solaris", nesw: [7, 7, 8, 8], art: "./GeneratedArt/MasteredCards/h_arbiter.png" },
    { id: "e_eclipse", name: "Eclipse Void Blade", faction: "Abyss", nesw: [6, 6, 5, 6], art: "./GeneratedArt/MasteredCards/e_eclipse.png" },
    { id: "e_archon", name: "Prism Core Archon", faction: "Solaris", nesw: [7, 6, 6, 5], art: "./GeneratedArt/MasteredCards/e_archon.png" },
    { id: "e_inferno", name: "Inferno Seraph", faction: "Valkyria", nesw: [7, 7, 5, 6], art: "./GeneratedArt/MasteredCards/e_inferno.png" },
    { id: "e_reaper", name: "Sigil Wraith", faction: "Abyss", nesw: [6, 7, 7, 5], art: "./GeneratedArt/MasteredCards/e_reaper.png" },
    { id: "e_titan", name: "Bastion Dreadnought", faction: "Chronos", nesw: [7, 5, 7, 6], art: "./GeneratedArt/MasteredCards/e_titan.png" },
    { id: "e_colossus", name: "Emerald Colossus", faction: "Aether", nesw: [6, 8, 5, 6], art: "./GeneratedArt/MasteredCards/e_colossus.png" },
    { id: "e_cryo", name: "Cryo Interceptor", faction: "Aether", nesw: [5, 7, 6, 7], art: "./GeneratedArt/MasteredCards/e_cryo.png" },
    { id: "e_shinobi", name: "Cyber Shinobi", faction: "Chronos", nesw: [7, 6, 6, 5], art: "./GeneratedArt/MasteredCards/e_shinobi.png" }
  ];

  function buildSet1Pool60() {
    if (Array.isArray(globalScope.SET1_60_CATALOG) && globalScope.SET1_60_CATALOG.length === 60) {
      return globalScope.SET1_60_CATALOG.map(function (c) {
        return Object.assign({}, c, {
          poolSet: "SET1_CRADLE_OF_ECHOES",
          poolBadge: "[SET 1 CORE]"
        });
      });
    }
    const factions = ["Aether", "Solaris", "Valkyria", "Chronos", "Abyss"];
    const out = [];
    for (let i = 0; i < 60; i++) {
      const tpl = BASE_16_ROSTER[i % BASE_16_ROSTER.length];
      const tier = Math.floor(i / 16) + 1;
      const cid = i < BASE_16_ROSTER.length ? tpl.id : "set1_c" + String(i + 1).padStart(2, "0") + "_" + tpl.id;
      const nesw = tpl.nesw.map(function (v, idx) {
        return Math.min(9, v + ((i + idx) % 2 === 0 && i >= 16 ? 1 : 0));
      });
      const sum = nesw.reduce(function (s, v) { return s + v; }, 0);
      out.push({
        id: cid,
        name: i < BASE_16_ROSTER.length ? tpl.name : tpl.name + " Mk." + tier,
        faction: factions[i % factions.length],
        nesw: nesw,
        starCost: sum >= 30 ? 3 : sum >= 28 ? 2 : 1,
        art: i < BASE_16_ROSTER.length ? tpl.art : "./GeneratedArt/MasteredCards/" + cid + ".png",
        telegraphName: "Directional Capture Matrix",
        poolSet: "SET1_CRADLE_OF_ECHOES",
        poolBadge: "[SET 1 CORE]"
      });
    }
    return out;
  }

  const SET2_KUBRART_ASTRAL_ECLIPSE_20 = [
    {
      id: "kubrart_s2_01_astral_ronin",
      name: "Kubrart Astral Ronin Zero",
      faction: "Abyss",
      nesw: [9, 8, 6, 7],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/style_kubrart_vector_cel_ink.png",
      telegraphName: "Stark Sumi-Ink Diagonal Iai",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_02_eclipse_valkyrie",
      name: "Eclipse Kagenashi Valkyrie",
      faction: "Valkyria",
      nesw: [8, 9, 6, 7],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_01.png",
      telegraphName: "24fps Kagenashi Wing Sweep",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_03_sumi_judge_arbiter",
      name: "Sumi-e Law Arbiter VII",
      faction: "Solaris",
      nesw: [8, 7, 8, 7],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_02.png",
      telegraphName: "G-Pen Crosshatch Decree",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_04_vector_cel_seraph",
      name: "Vector-Cel Crimson Seraph",
      faction: "Valkyria",
      nesw: [9, 7, 7, 7],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_03.png",
      telegraphName: "Chromatic Rim-Light Pierce",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_05_halftone_phantom",
      name: "60-LPI Screentone Phantom",
      faction: "Abyss",
      nesw: [7, 8, 7, 8],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_04.png",
      telegraphName: "CMYK Dot-Matrix Cloak",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_06_nocturna_tarot_weaver",
      name: "Nocturna Chiaroscuro Weaver",
      faction: "Aether",
      nesw: [8, 6, 8, 8],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_05.png",
      telegraphName: "Obsidian-Ivory Tarot Ring",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_07_cyber_magicite_dragoon",
      name: "Cyber-Magicite Apex Dragoon",
      faction: "Chronos",
      nesw: [9, 8, 5, 7],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_06.png",
      telegraphName: "Beveled Gauntlet Sky-Drop",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_08_okitsu_red_scarf_vanguard",
      name: "Okitsu Red Scarf Vanguard",
      faction: "Aether",
      nesw: [8, 8, 7, 7],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_07.png",
      telegraphName: "Crimson Thread Counter-Flip",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_09_constellation_fox_archon",
      name: "Constellation Fox Sovereign",
      faction: "Solaris",
      nesw: [7, 9, 8, 6],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_08.png",
      telegraphName: "Five-Star Amber Refraction",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_10_mnemosyne_mirror_duelist",
      name: "Mnemosyne Mirror Duelist",
      faction: "Abyss",
      nesw: [8, 7, 7, 8],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_09.png",
      telegraphName: "Hall of Selves Symmetry",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_11_gpen_crosshatch_paladin",
      name: "G-Pen Filigree Paladin",
      faction: "Solaris",
      nesw: [8, 8, 6, 7],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_10.png",
      telegraphName: "Parchment-Gold Aegis",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_12_speedline_shonen_striker",
      name: "Radial Speedline Striker",
      faction: "Valkyria",
      nesw: [9, 7, 6, 7],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_11.png",
      telegraphName: "Foreshortened Blade Lunge",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_13_orthographic_mecha_sentinel",
      name: "Orthographic Mecha Sentinel",
      faction: "Chronos",
      nesw: [7, 8, 8, 6],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_12.png",
      telegraphName: "7.5-Head Panel-Line Lock",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_14_gouache_citadel_astrolabe",
      name: "Sky-Citadel Astrolabe Sage",
      faction: "Aether",
      nesw: [7, 7, 8, 7],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_13.png",
      telegraphName: "Luminous Gouache Orbit",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_15_sparse_voxel_interceptor",
      name: "Hi3D Normal-Bridge Interceptor",
      faction: "Chronos",
      nesw: [8, 7, 6, 8],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_14.png",
      telegraphName: "2.5D Normal-Mapped Relief",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_16_starflare_kagenashi_ace",
      name: "Star-Flare Kagenashi Ace",
      faction: "Valkyria",
      nesw: [8, 9, 5, 7],
      starCost: 2,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_15.png",
      telegraphName: "Four-Point Star-Flare Arc",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_17_negative_space_assassin",
      name: "Negative-Space Ink Assassin",
      faction: "Abyss",
      nesw: [9, 6, 7, 8],
      starCost: 3,
      art: "./GeneratedArt/AnimeMangaModels/anime_rtx4080_16.png",
      telegraphName: "Sumi-e Silhouette Ambush",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_18_ties_soup_grandmaster",
      name: "12-Lineage TIES Grandmaster",
      faction: "Solaris",
      nesw: [8, 8, 8, 6],
      starCost: 3,
      art: "./GeneratedArt/sp_01_kai_nakamura_rtx4080.png",
      telegraphName: "TIES-Merged Vector Convergence",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_19_crimson_thread_architect",
      name: "Aiko, Crimson Thread Architect",
      faction: "Aether",
      nesw: [9, 7, 8, 8],
      starCost: 3,
      art: "./GeneratedArt/sp_02_aiko_nakamura_scarf_rtx4080.png",
      telegraphName: "Compiler Log A-21 Overwrite",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    },
    {
      id: "kubrart_s2_20_eclipse_monolith",
      name: "Kubrart Astral Eclipse Monolith",
      faction: "Abyss",
      nesw: [8, 8, 8, 8],
      starCost: 3,
      art: "./GeneratedArt/sp_04_luna_tarot_rtx4080.png",
      telegraphName: "Omni-Directional Eclipse Seal",
      poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
      poolBadge: "[SET 2 KUBRART]"
    }
  ];

  const SOVEREIGN_AGENT_CARDS_37 = [
    // 4 Mythic Plugins
    { id: "plugin_01_tcg_creative_designer", name: "Grand Arcanist of CardCraft", faction: "Aether", nesw: [8, 7, 6, 7], starCost: 3, art: "./GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png", telegraphName: "3x3 Atelier Prism Lock", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "plugin_02_parallel_swarm_orchestrator", name: "Chronos Swarm Commander", faction: "Chronos", nesw: [7, 8, 6, 7], starCost: 3, art: "./GeneratedArt/AgentDeck/Cards/plugin_02_parallel_swarm_orchestrator.png", telegraphName: "Tri-Portal Worktree Fan-Out", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "plugin_03_jev_system_one", name: "Hallowed Arbiter of System One", faction: "Solaris", nesw: [8, 6, 8, 6], starCost: 3, art: "./GeneratedArt/AgentDeck/Cards/plugin_03_jev_system_one.png", telegraphName: "Octagonal Law-Seal Gate", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "plugin_04_mlx_apple_silicon", name: "A18 Pro Metal Forge Sovereign", faction: "Valkyria", nesw: [7, 7, 7, 7], starCost: 3, art: "./GeneratedArt/AgentDeck/Cards/plugin_04_mlx_apple_silicon.png", telegraphName: "Single-Pass Logit Diamond", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    // 12 Arcane Skills
    { id: "skill_01_master_router", name: "Compass of the 93 Realms", faction: "Solaris", nesw: [7, 6, 6, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_01_master_router.png", telegraphName: "4-Slot Disclosure Vector", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_02_tactical_illustrator_library", name: "Twelve-Master Atelier Grimoire", faction: "Aether", nesw: [7, 7, 5, 7], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_02_tactical_illustrator_library.png", telegraphName: "Crosshatch & Cel-Wash Aura", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_03_create_game_assets", name: "Aegis of Deterministic Raster QA", faction: "Aether", nesw: [6, 7, 7, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_03_create_game_assets.png", telegraphName: "600x800 Contrast Envelope", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_04_card_game_genre", name: "Chronicle of the Single Zone", faction: "Solaris", nesw: [8, 6, 6, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_04_card_game_genre.png", telegraphName: "3x3 Directional Capture Cross", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_05_game_feel_juice", name: "Valkyrie of Kinetic Impact", faction: "Valkyria", nesw: [7, 7, 5, 5], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/skill_05_game_feel_juice.png", telegraphName: "48ms Hit-Stop Wave", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_06_game_ui_ux", name: "Oracle of Responsive Anchors", faction: "Aether", nesw: [6, 6, 7, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/skill_06_game_ui_ux.png", telegraphName: "Safe-Area Focus Grid", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_07_ai_utility_behavior", name: "Archon of Utility & Negamax", faction: "Abyss", nesw: [7, 8, 5, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_07_ai_utility_behavior.png", telegraphName: "Alpha-Beta Pruning Scan", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_08_shader_camera_audio", name: "Seraph of Halftone & Harmony", faction: "Valkyria", nesw: [6, 7, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/skill_08_shader_camera_audio.png", telegraphName: "Cel-Outline & Audio Duck Ring", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_09_save_procgen_dialogue", name: "Keeper of Mnemosyne Vaults", faction: "Chronos", nesw: [6, 5, 7, 7], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/skill_09_save_procgen_dialogue.png", telegraphName: "Versioned Save Lattice", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_10_multi_engine_codex", name: "Titan of the Twelve Engines", faction: "Chronos", nesw: [7, 6, 7, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_10_multi_engine_codex.png", telegraphName: "Dual-Engine Contract", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_11_decompilation_hi3d_rea", name: "Sovereign of Hi3D & Decompilation", faction: "Abyss", nesw: [8, 7, 6, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/skill_11_decompilation_hi3d_rea.png", telegraphName: "Watertight Manifold Scan", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "skill_12_workflows_and_agent_core", name: "Herald of the Golden Master", faction: "Solaris", nesw: [6, 6, 6, 7], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/skill_12_workflows_and_agent_core.png", telegraphName: "Release Readiness Arc", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    // 12 Tactical Spells
    { id: "tool_01_invoke_subagent", name: "Summon Parallel Phantom", faction: "Chronos", nesw: [7, 7, 5, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_01_invoke_subagent.png", telegraphName: "Async Subagent Worktree", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_02_define_subagent", name: "Forge Specialist Construct", faction: "Aether", nesw: [6, 7, 6, 5], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_02_define_subagent.png", telegraphName: "Agent Blueprint Inscription", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_03_manage_subagents", name: "Tactical Swarm Overwatch", faction: "Chronos", nesw: [6, 5, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_03_manage_subagents.png", telegraphName: "Fleet Status Sweep", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_04_send_message", name: "Astral Telepathic Relay", faction: "Aether", nesw: [5, 6, 5, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_04_send_message.png", telegraphName: "Direct Peer Message Vector", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_05_call_mcp_tool", name: "Channel Arcane MCP Conduit", faction: "Solaris", nesw: [7, 6, 7, 5], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_05_call_mcp_tool.png", telegraphName: "Schema-Validated MCP Pulse", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_06_mcp_resources", name: "Scry Nexus Resource Archive", faction: "Aether", nesw: [5, 6, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_06_mcp_resources.png", telegraphName: "URI Resource Discovery Cone", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_07_run_command", name: "Incantation of the Zsh Shell", faction: "Valkyria", nesw: [8, 6, 5, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_07_run_command.png", telegraphName: "Daemon Execution Strike", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_08_manage_task", name: "Chrono Daemon Tether", faction: "Chronos", nesw: [5, 6, 6, 5], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_08_manage_task.png", telegraphName: "Task Stream Monitor", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_09_read_file", name: "True-Sight Omniscient Lens", faction: "Solaris", nesw: [6, 6, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_09_read_file.png", telegraphName: "Multimodal Asset Scan", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_10_write_file", name: "Inscribe Sovereign Grimoire", faction: "Aether", nesw: [7, 6, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_10_write_file.png", telegraphName: "Atomic File Creation Seal", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_11_edit_file", name: "Precision Rune Scalpel", faction: "Valkyria", nesw: [7, 7, 5, 5], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_11_edit_file.png", telegraphName: "Contiguous AST Splice", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "tool_12_search_schedule_ask", name: "Astral Horizon & Oracle's Call", faction: "Solaris", nesw: [6, 5, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/tool_12_search_schedule_ask.png", telegraphName: "Web Citation & Timer Wakeup", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    // 9 MCP Conduits
    { id: "mcp_01_jev_system_one", name: "Jev System One Tribunal", faction: "Solaris", nesw: [8, 6, 7, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/mcp_01_jev_system_one.png", telegraphName: "12-Point Calibrated Ring", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_02_jev_py_verifier", name: "Jev-Py Deterministic Verifier", faction: "Solaris", nesw: [7, 7, 7, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/mcp_02_jev_py_verifier.png", telegraphName: "Dual-Runtime Diff Gate", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_03_mlx_apple_silicon", name: "MLX Metal GPU Matrix", faction: "Valkyria", nesw: [7, 8, 6, 6], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/mcp_03_mlx_apple_silicon.png", telegraphName: "Unified-Memory Tensor Bus", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_04_prime_rlm_swarm", name: "Prime Vision & RLM Swarm Core", faction: "Abyss", nesw: [7, 7, 6, 7], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/mcp_04_prime_rlm_swarm.png", telegraphName: "Parallel Local Vision Dispatch", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_05_sequential_thinking", name: "Astrolabe of Sequential Thought", faction: "Chronos", nesw: [6, 6, 7, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/mcp_05_sequential_thinking.png", telegraphName: "Task Decomposition Lattice", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_06_knowledge_graph_mem", name: "Nexus of the Memory Graph", faction: "Aether", nesw: [6, 7, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/mcp_06_knowledge_graph_mem.png", telegraphName: "Entity-Relation Constellation", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_07_git_time_chronicle", name: "Chrono-Branch Git Arbiter", faction: "Chronos", nesw: [6, 6, 6, 7], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/mcp_07_git_time_chronicle.png", telegraphName: "Worktree Branch Timeline", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_08_filesystem_and_fetch", name: "Citadel of Vault & Astral Fetch", faction: "Aether", nesw: [6, 6, 6, 6], starCost: 1, art: "./GeneratedArt/AgentDeck/Cards/mcp_08_filesystem_and_fetch.png", telegraphName: "Sandboxed IO Conduit", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" },
    { id: "mcp_09_tcg_creative_studio", name: "Atelier of CardCraft MCP", faction: "Aether", nesw: [8, 7, 6, 7], starCost: 2, art: "./GeneratedArt/AgentDeck/Cards/mcp_09_tcg_creative_studio.png", telegraphName: "Card Concept + SVG Synthesizer", poolSet: "SOVEREIGN_AGENT_37", poolBadge: "[SOVEREIGN AGENT]" }
  ];

  function buildFullArenaDraftPool117() {
    const set1 = buildSet1Pool60();
    const set2Source =
      Array.isArray(globalScope.SET2_KUBRART_CATALOG) && globalScope.SET2_KUBRART_CATALOG.length === 20
        ? globalScope.SET2_KUBRART_CATALOG
        : SET2_KUBRART_ASTRAL_ECLIPSE_20;
    const set2 = set2Source.map(function (c) {
      return Object.assign({}, c, {
        poolSet: "SET2_KUBRART_ASTRAL_ECLIPSE",
        poolBadge: "[SET 2 KUBRART]"
      });
    });
    const sov = SOVEREIGN_AGENT_CARDS_37.map(function (c) {
      return Object.assign({}, c, {
        poolSet: "SOVEREIGN_AGENT_37",
        poolBadge: "[SOVEREIGN AGENT]"
      });
    });
    const combined = set1.concat(set2, sov);

    // Register into global card lookup maps so getCardMeta(cardId) always resolves drafted cards
    try {
      combined.forEach(function (card) {
        if (globalScope.SET1_CARDS_BY_ID && typeof globalScope.SET1_CARDS_BY_ID === "object" && !globalScope.SET1_CARDS_BY_ID[card.id]) {
          globalScope.SET1_CARDS_BY_ID[card.id] = card;
        }
        if (globalScope.AGENT_PLUGIN_CARDS_BY_ID && typeof globalScope.AGENT_PLUGIN_CARDS_BY_ID === "object" && card.poolSet === "SOVEREIGN_AGENT_37") {
          globalScope.AGENT_PLUGIN_CARDS_BY_ID[card.id] = card;
        }
        if (globalScope.ALL_CARDS && typeof globalScope.ALL_CARDS === "object" && !globalScope.ALL_CARDS[card.id]) {
          Object.defineProperty(globalScope.ALL_CARDS, card.id, {
            value: card,
            enumerable: false,
            writable: true,
            configurable: true
          });
        }
      });
    } catch (_) {}

    return combined;
  }

  const ARENA_DRAFT_POOL_117 = buildFullArenaDraftPool117();
  const ARENA_DRAFT_BY_ID = {};
  ARENA_DRAFT_POOL_117.forEach(function (c) {
    ARENA_DRAFT_BY_ID[c.id] = c;
  });

  // ==========================================================================
  // 5. ROGUELITE ARENA DRAFT STATE & LOGIC
  // ==========================================================================
  const ARENA_DRAFT_STATE = {
    active: false,
    round: 1,
    maxRounds: 5,
    draftedCards: [],
    currentPack: [],
    gauntletWins: 0,
    gauntletLosses: 0,
    eloRating: 1600,
    rngSeed: 0xCF202611
  };

  function nextDraftRand() {
    if (typeof globalScope.seededRng === "function") {
      return globalScope.seededRng();
    }
    let t = (ARENA_DRAFT_STATE.rngSeed += 0x6D2B79F5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  function dealThreeCardArenaPack() {
    const pool = buildFullArenaDraftPool117();
    const draftedSet = new Set(ARENA_DRAFT_STATE.draftedCards);

    const set1Avail = pool.filter(function (c) { return c.poolSet === "SET1_CRADLE_OF_ECHOES" && !draftedSet.has(c.id); });
    const set2Avail = pool.filter(function (c) { return c.poolSet === "SET2_KUBRART_ASTRAL_ECLIPSE" && !draftedSet.has(c.id); });
    const sovAvail = pool.filter(function (c) { return c.poolSet === "SOVEREIGN_AGENT_37" && !draftedSet.has(c.id); });

    const pickOne = function (arr, fallbackArr) {
      const src = arr.length > 0 ? arr : fallbackArr;
      const idx = Math.floor(nextDraftRand() * src.length) % src.length;
      return src[Math.max(0, idx)];
    };

    const c1 = pickOne(set1Avail, pool);
    const c2 = pickOne(set2Avail, pool);
    const c3 = pickOne(sovAvail, pool);

    ARENA_DRAFT_STATE.currentPack = [c1, c2, c3];
    return ARENA_DRAFT_STATE.currentPack;
  }

  function ensureArenaDraftModalDom() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    let modal = doc.getElementById("arena-draft-modal");
    if (!modal && doc.body) {
      modal = doc.createElement("div");
      modal.id = "arena-draft-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.setAttribute("aria-label", "5-Round Roguelite Arena Draft Mode");
      modal.style.cssText =
        "display:none;position:fixed;inset:0;z-index:9860;background:rgba(4,8,18,0.93);" +
        "backdrop-filter:blur(10px);align-items:center;justify-content:center;padding:14px;box-sizing:border-box;";
      doc.body.appendChild(modal);
    }
    return modal;
  }

  function renderArenaDraftModalContent() {
    const modal = ensureArenaDraftModalDom();
    if (!modal) return null;

    const pack = Array.isArray(ARENA_DRAFT_STATE.currentPack) && ARENA_DRAFT_STATE.currentPack.length > 0
      ? ARENA_DRAFT_STATE.currentPack
      : dealThreeCardArenaPack();

    const packCardsHtml = pack
      .map(function (c, idx) {
        const badgeColor =
          c.poolSet === "SET2_KUBRART_ASTRAL_ECLIPSE"
            ? "#FF2E54"
            : c.poolSet === "SOVEREIGN_AGENT_37"
            ? "#A855F7"
            : "#00E5FF";
        const nesw = Array.isArray(c.nesw) ? c.nesw : [7, 7, 7, 7];
        const sumStats = nesw[0] + nesw[1] + nesw[2] + nesw[3];

        return (
          '<div class="arena-draft-pack-card" data-card-id="' +
          c.id +
          '" onclick="window.pickArenaDraftCard(\'' +
          c.id +
          '\')" style="flex:1 1 240px;max-width:310px;background:linear-gradient(165deg,#0F172A 0%,#090D16 100%);border:2px solid ' +
          badgeColor +
          ';border-radius:12px;padding:12px;cursor:pointer;display:flex;flex-direction:column;justify-content:space-between;gap:8px;box-shadow:0 8px 24px rgba(0,0,0,0.65);transition:transform 0.16s ease;">' +
          // Top Badge & Faction
          '<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">' +
          '<span style="font-size:10px;font-weight:900;padding:2px 7px;border-radius:4px;background:rgba(15,23,42,0.9);border:1px solid ' +
          badgeColor +
          ";color:" +
          badgeColor +
          ';">' +
          (c.poolBadge || "[DRAFT POOL]") +
          "</span>" +
          '<span style="font-size:10px;font-weight:800;color:#FFE082;">[' +
          String(c.faction || "Aether").toUpperCase() +
          " · TIER " +
          (c.starCost || 2) +
          "]</span>" +
          "</div>" +
          // Portrait & Directional NESW Pip Diamond
          '<div style="position:relative;height:185px;border-radius:8px;overflow:hidden;border:1px solid rgba(148,163,184,0.28);background:#050811;display:flex;align-items:center;justify-content:center;">' +
          '<img src="' +
          c.art +
          '" alt="' +
          c.name +
          '" style="width:100%;height:100%;object-fit:cover;object-position:center 18%;" onerror="this.style.display=\'none\'"/>' +
          // NESW Tactical Overlay
          '<div style="position:absolute;top:8px;left:8px;width:48px;height:48px;border-radius:8px;background:rgba(3,7,18,0.88);border:1.5px solid ' +
          badgeColor +
          ';display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-rows:1fr 1fr 1fr;font-size:11px;font-weight:900;color:#FFFFFF;text-align:center;align-items:center;">' +
          "<span></span><span style=\"color:#38BDF8;\">" +
          nesw[0] +
          "</span><span></span>" +
          "<span style=\"color:#F43F5E;\">" +
          nesw[3] +
          '</span><span style="color:#FFB800;font-size:9px;">+</span><span style="color:#2EE6D3;">' +
          nesw[1] +
          "</span>" +
          "<span></span><span style=\"color:#FFE082;\">" +
          nesw[2] +
          "</span><span></span>" +
          "</div>" +
          "</div>" +
          // Card Title & Telegraph
          '<div style="display:flex;flex-direction:column;gap:3px;">' +
          '<div style="font-size:14px;font-weight:900;color:#FFFFFF;">' +
          c.name +
          "</div>" +
          '<div style="font-size:11px;font-weight:700;color:#94A3B8;">Telegraph: <span style="color:#E2E8F0;">' +
          (c.telegraphName || "3x3 Directional Capture") +
          "</span> · Sum: <strong style=\"color:#FFB800;\">" +
          sumStats +
          "</strong></div>" +
          "</div>" +
          '<button type="button" class="arena-pick-card-btn" data-pick-idx="' +
          idx +
          '" style="width:100%;padding:8px 10px;border-radius:7px;border:1px solid ' +
          badgeColor +
          ";background:rgba(0,229,255,0.14);color:#FFFFFF;font-size:11px;font-weight:900;cursor:pointer;\">" +
          "[DRAFT CARD #" +
          (idx + 1) +
          " INTO SQUAD]" +
          "</button>" +
          "</div>"
        );
      })
      .join("");

    const slotsHtml = [0, 1, 2, 3, 4]
      .map(function (slotIdx) {
        const cid = ARENA_DRAFT_STATE.draftedCards[slotIdx];
        const cardObj = cid ? ARENA_DRAFT_BY_ID[cid] || { id: cid, name: cid } : null;
        if (cardObj) {
          return (
            '<div class="arena-drafted-slot filled" style="flex:1 1 140px;padding:7px 10px;border-radius:7px;background:rgba(16,185,129,0.15);border:1px solid #2EE6D3;color:#F8FAFC;font-size:11px;font-weight:800;">' +
            "[SLOT " +
            (slotIdx + 1) +
            "] " +
            cardObj.name +
            "</div>"
          );
        }
        return (
          '<div class="arena-drafted-slot empty" style="flex:1 1 140px;padding:7px 10px;border-radius:7px;background:rgba(15,23,42,0.65);border:1px dashed rgba(148,163,184,0.35);color:#64748B;font-size:11px;font-weight:800;">' +
          "[SLOT " +
          (slotIdx + 1) +
          " — AWAITING PICK]" +
          "</div>"
        );
      })
      .join("");

    modal.innerHTML =
      '<div class="arena-draft-sheet" style="width:100%;max-width:1020px;background:linear-gradient(180deg,#0B1120 0%,#050811 100%);border:2px solid #FFB800;border-radius:14px;padding:16px;box-shadow:0 20px 60px rgba(0,0,0,0.88);color:#F8FAFC;display:flex;flex-direction:column;gap:12px;">' +
      // Header
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-bottom:1px solid rgba(148,163,184,0.24);padding-bottom:10px;">' +
      '<div style="display:flex;flex-direction:column;gap:2px;">' +
      '<div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:900;color:#FFB800;letter-spacing:0.08em;">' +
      renderSvgIcon("arena_draft_crest", 15) +
      "<span>[ROGUELITE ARENA DRAFT · 117-CARD POOL: 60 SET 1 + 20 SET 2 KUBRART + 37 SOVEREIGN AGENT]</span>" +
      "</div>" +
      '<h3 id="arena-draft-title" style="margin:0;font-size:18px;font-weight:900;color:#FFFFFF;">Round ' +
      ARENA_DRAFT_STATE.round +
      " / " +
      ARENA_DRAFT_STATE.maxRounds +
      " — Choose 1 Card for Your 5-Card Gauntlet Squad</h3>" +
      "</div>" +
      '<div style="display:flex;align-items:center;gap:8px;">' +
      '<span style="font-size:11px;font-weight:900;padding:4px 9px;border-radius:6px;background:rgba(255,184,0,0.16);border:1px solid #FFB800;color:#FEF08A;">ELO: ' +
      ARENA_DRAFT_STATE.eloRating +
      " · RECORD: " +
      ARENA_DRAFT_STATE.gauntletWins +
      "W-" +
      ARENA_DRAFT_STATE.gauntletLosses +
      "L</span>" +
      '<button type="button" id="arena-draft-close-btn" onclick="window.closeArenaDraftModal()" ' +
      'style="padding:5px 10px;border-radius:6px;border:1px solid rgba(248,113,113,0.6);background:rgba(127,29,29,0.45);color:#FCA5A5;font-size:11px;font-weight:900;cursor:pointer;">[CLOSE X]</button>' +
      "</div>" +
      "</div>" +
      // 3-Card Pack Row
      '<div id="arena-draft-pack-row" style="display:flex;gap:12px;justify-content:center;align-items:stretch;flex-wrap:wrap;">' +
      packCardsHtml +
      "</div>" +
      // Drafted Squad Progress Bar
      '<div style="display:flex;flex-direction:column;gap:6px;background:rgba(15,23,42,0.78);padding:10px;border-radius:8px;border:1px solid rgba(148,163,184,0.22);">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;">' +
      '<span style="font-size:11px;font-weight:900;color:#2EE6D3;">DRAFTED GAUNTLET SQUAD (' +
      ARENA_DRAFT_STATE.draftedCards.length +
      " / " +
      ARENA_DRAFT_STATE.maxRounds +
      " CARDS):</span>" +
      '<span style="font-size:11px;font-weight:800;color:#94A3B8;">Auto-deploys to 3x3 Board upon 5th pick</span>' +
      "</div>" +
      '<div id="arena-draft-squad-slots" style="display:flex;gap:8px;flex-wrap:wrap;">' +
      slotsHtml +
      "</div>" +
      "</div>" +
      "</div>";

    return modal;
  }

  function openRogueliteArenaDraftModal() {
    ARENA_DRAFT_STATE.active = true;
    ARENA_DRAFT_STATE.round = 1;
    ARENA_DRAFT_STATE.maxRounds = 5;
    ARENA_DRAFT_STATE.draftedCards = [];
    dealThreeCardArenaPack();
    const modal = renderArenaDraftModalContent();
    if (modal) {
      modal.style.display = "flex";
    }
    playMangaVoiceCadenceBleep(1, "kubrart_vector_cel");
    return ARENA_DRAFT_STATE;
  }

  function launchArenaDraftGauntletMatch() {
    const squad = ARENA_DRAFT_STATE.draftedCards.slice(0, 5);
    while (squad.length < 5) {
      const fallbackCard = ARENA_DRAFT_POOL_117[squad.length % ARENA_DRAFT_POOL_117.length];
      squad.push(fallbackCard.id);
    }

    // Ensure state exists and equip the 5-card drafted squad
    if (!globalScope.state || typeof globalScope.state !== "object") {
      globalScope.state = {
        hand: squad.slice(),
        activeSquad: squad.slice(),
        activeDeck: squad.slice(),
        customDeckEquipped: true
      };
    } else {
      if (Array.isArray(globalScope.state.unlockedCards)) {
        squad.forEach(function (cid) {
          if (!globalScope.state.unlockedCards.includes(cid)) {
            globalScope.state.unlockedCards.push(cid);
          }
        });
      }
      globalScope.state.activeSquad = squad.slice();
      globalScope.state.activeDeck = squad.slice();
      globalScope.state.customDeckEquipped = true;
      globalScope.state.hand = squad.slice();
    }

    closeArenaDraftModal();

    const targetStageIdx =
      (ARENA_DRAFT_STATE.gauntletWins + ARENA_DRAFT_STATE.gauntletLosses) % 15;
    if (typeof globalScope.startStage === "function") {
      globalScope.startStage(targetStageIdx);
    }

    // Re-assert hand and activeSquad after startStage so any star-cap or default hand logic preserves the 5 drafted cards
    if (globalScope.state && typeof globalScope.state === "object") {
      globalScope.state.hand = squad.slice();
      globalScope.state.activeSquad = squad.slice();
      globalScope.state.activeDeck = squad.slice();
      globalScope.state.customDeckEquipped = true;
    }
    if (typeof globalScope.renderAll === "function") {
      globalScope.renderAll();
    }

    return {
      launched: true,
      hand: squad.slice(),
      activeSquad: squad.slice(),
      eloRating: ARENA_DRAFT_STATE.eloRating
    };
  }

  function pickArenaDraftCard(cardId) {
    if (!Array.isArray(ARENA_DRAFT_STATE.currentPack) || ARENA_DRAFT_STATE.currentPack.length === 0) {
      dealThreeCardArenaPack();
    }
    const chosenId =
      cardId && String(cardId).trim()
        ? String(cardId).trim()
        : ARENA_DRAFT_STATE.currentPack[0].id;

    ARENA_DRAFT_STATE.draftedCards.push(chosenId);
    playMangaVoiceCadenceBleep(ARENA_DRAFT_STATE.round % 3, "sakuga_24fps_flare");

    if (ARENA_DRAFT_STATE.draftedCards.length >= ARENA_DRAFT_STATE.maxRounds) {
      ARENA_DRAFT_STATE.round = ARENA_DRAFT_STATE.maxRounds;
      return launchArenaDraftGauntletMatch();
    }

    ARENA_DRAFT_STATE.round = ARENA_DRAFT_STATE.draftedCards.length + 1;
    dealThreeCardArenaPack();
    renderArenaDraftModalContent();
    return {
      launched: false,
      round: ARENA_DRAFT_STATE.round,
      draftedCards: ARENA_DRAFT_STATE.draftedCards.slice(),
      currentPack: ARENA_DRAFT_STATE.currentPack.slice()
    };
  }

  function closeArenaDraftModal() {
    ARENA_DRAFT_STATE.active = false;
    if (typeof globalScope.document !== "undefined") {
      const modal = globalScope.document.getElementById("arena-draft-modal");
      if (modal) {
        modal.style.display = "none";
      }
    }
    return false;
  }

  // ==========================================================================
  // 6. SAFE UI COMMAND PILL INJECTION INTO STUDIO / DRAWER BARS
  // ==========================================================================
  function injectMangaAndDraftCommandPills() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    const parentBar =
      doc.getElementById("aaa-studio-command-pills") ||
      doc.getElementById("sakuga-anim-studio-bar") ||
      doc.getElementById("dev-camera-drawer");
    if (!parentBar) return;

    if (!doc.getElementById("btn-pill-manga-cutscene")) {
      const mangaBtn = doc.createElement("button");
      mangaBtn.type = "button";
      mangaBtn.id = "btn-pill-manga-cutscene";
      mangaBtn.setAttribute("onclick", "window.openMangaChapterCutscene(window.state ? window.state.stageIndex : 0)");
      mangaBtn.style.cssText =
        "display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;" +
        "border:1px solid #FF2E54;background:rgba(255,46,84,0.18);color:#FFE4E6;font-size:12px;font-weight:800;cursor:pointer;";
      mangaBtn.innerHTML = renderSvgIcon("manga_panel_grid", 13) + "<span>Manga Story (19)</span>";
      parentBar.appendChild(mangaBtn);
    }

    if (!doc.getElementById("btn-pill-arena-draft")) {
      const draftBtn = doc.createElement("button");
      draftBtn.type = "button";
      draftBtn.id = "btn-pill-arena-draft";
      draftBtn.setAttribute("onclick", "window.openRogueliteArenaDraftModal()");
      draftBtn.style.cssText =
        "display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:7px;" +
        "border:1px solid #FFB800;background:rgba(255,184,0,0.18);color:#FEF08A;font-size:12px;font-weight:800;cursor:pointer;";
      draftBtn.innerHTML = renderSvgIcon("arena_draft_crest", 13) + "<span>Arena Draft (117)</span>";
      parentBar.appendChild(draftBtn);
    }
  }

  // ==========================================================================
  // 7. PUBLIC API EXPORT & REGISTRATION
  // ==========================================================================
  const CardFrontMangaCutsceneAndDraft = {
    VERSION: MODULE_VERSION,
    MANGA_STYLE_PRESETS: MANGA_STYLE_PRESETS,
    MANGA_CHAPTER_CUTSCENES: MANGA_CHAPTER_CUTSCENES,
    MANGA_CUTSCENE_STATE: MANGA_CUTSCENE_STATE,
    openMangaChapterCutscene: openMangaChapterCutscene,
    advanceMangaCutscenePanel: advanceMangaCutscenePanel,
    closeMangaCutsceneModal: closeMangaCutsceneModal,
    selectMangaCutsceneStylePreset: selectMangaCutsceneStylePreset,
    setActivePanel: setActivePanel,
    ARENA_DRAFT_STATE: ARENA_DRAFT_STATE,
    ARENA_DRAFT_POOL_117: ARENA_DRAFT_POOL_117,
    SET2_KUBRART_ASTRAL_ECLIPSE_20: SET2_KUBRART_ASTRAL_ECLIPSE_20,
    SOVEREIGN_AGENT_CARDS_37: SOVEREIGN_AGENT_CARDS_37,
    openRogueliteArenaDraftModal: openRogueliteArenaDraftModal,
    pickArenaDraftCard: pickArenaDraftCard,
    launchArenaDraftGauntletMatch: launchArenaDraftGauntletMatch,
    closeArenaDraftModal: closeArenaDraftModal,
    injectMangaAndDraftCommandPills: injectMangaAndDraftCommandPills
  };

  globalScope.CardFrontMangaCutsceneAndDraft = CardFrontMangaCutsceneAndDraft;
  globalScope.CardFrontModules = globalScope.CardFrontModules || {};
  globalScope.CardFrontModules.MangaCutsceneAndDraft = CardFrontMangaCutsceneAndDraft;

  // Expose top-level globals for direct calls from cardfront_cradle_of_echoes_playable.html
  globalScope.MANGA_CHAPTER_CUTSCENES = MANGA_CHAPTER_CUTSCENES;
  globalScope.openMangaChapterCutscene = openMangaChapterCutscene;
  globalScope.advanceMangaCutscenePanel = advanceMangaCutscenePanel;
  globalScope.closeMangaCutsceneModal = closeMangaCutsceneModal;
  globalScope.selectMangaCutsceneStylePreset = selectMangaCutsceneStylePreset;
  globalScope.ARENA_DRAFT_STATE = ARENA_DRAFT_STATE;
  globalScope.ARENA_DRAFT_POOL_117 = ARENA_DRAFT_POOL_117;
  globalScope.openRogueliteArenaDraftModal = openRogueliteArenaDraftModal;
  globalScope.pickArenaDraftCard = pickArenaDraftCard;
  globalScope.launchArenaDraftGauntletMatch = launchArenaDraftGauntletMatch;
  globalScope.closeArenaDraftModal = closeArenaDraftModal;

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", injectMangaAndDraftCommandPills);
    } else {
      injectMangaAndDraftCommandPills();
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
