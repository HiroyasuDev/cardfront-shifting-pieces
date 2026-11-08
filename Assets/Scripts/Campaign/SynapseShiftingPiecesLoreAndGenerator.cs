using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Campaign
{
    // =================================================================================================
    // 1. SHIFTING PIECES × CARDFRONT × CARDCRAFT CORE ENUMS & STRUCTS
    // =================================================================================================

    public enum ShiftingPiecesAbilityType
    {
        None = 0,
        FlickerPatternDecode = 1,      // sp_01_kai_nakamura: Decodes hidden opponent hand/trap vectors + free Dicevaders Budge ±1
        MnemosyneChronoRewind = 2,     // sp_02_aiko_nakamura_echo: Rewinds 1 captured tile state + Chrono turn restore (#D12D3A Red Scarf Anchor)
        EmotionalResonanceSync = 3,    // sp_03_mnemosyne_constellation_fox: Syncs adjacent directional stats to highest Emotional Weight tag
        PersonaGenesisTarot = 4,       // sp_04_luna_cradle_guide: Station of Awakening Tarot resonance (+2 all sides on Cradle of Echoes alignment)
        RealityAnchorShield = 5,       // sp_05_taro_fujimoto: Okitsu VR Café grounding shield (prevents flip & corruption on adjacent friendly cards)
        CoreExtractionColumnLock = 6   // sp_06_dr_rina_asakura: Corporate Core Extractor boss disruptor (locks 1 column & drains 1 directional stat)
    }

    public enum ShiftingPiecesEmotionTag
    {
        Neutral = 0,
        Nostalgia = 1,
        Joy = 2,
        Regret = 3,
        Anger = 4,
        Guilt = 5,
        Loss = 6,
        Acceptance = 7
    }

    public enum ShiftingPiecesFinalTriadChoice
    {
        Undecided = 0,
        Integrate = 1,          // Merge: Kai integrates Aiko's digital echo into his own consciousness
        Preserve = 2,           // Seal: Kai seals Mnemosyne, protecting her memory at the cost of isolation
        CollapseCarryForward = 3// Let Go: Kai lets Mnemosyne collapse, carrying Aiko forward in his heart & teaching memory ethics
    }

    public enum CradlePersonaId
    {
        TheDreamer = 1,
        TheMaster = 2,
        TheGuardian = 3,
        TheSurvivor = 4,
        TheVisionary = 5,
        TheInnovator = 6,
        TheHealer = 7,
        TheStrategist = 8,
        TheLeader = 9,
        TheEmpath = 10,
        TheSage = 11,
        TheExplorer = 12,
        TheArtist = 13,
        TheScientist = 14,
        TheRebel = 15,
        TheMediator = 16,
        ThePoet = 17,
        TheWarrior = 18,
        TheOracle = 19,
        TheArchitect = 20
    }

    public enum CradleElement
    {
        Air = 0,
        Fire = 1,
        Earth = 2,
        Water = 3
    }

    // =================================================================================================
    // 2. PROTAGONIST & CAST CARDS (`ShiftingPiecesCharacterCatalog`)
    // =================================================================================================

    [Serializable]
    public class ShiftingPiecesCharacterCardDef
    {
        public string cardId;
        public string characterName;
        public string titleAndRole;
        public int age;
        public string visualSignature;
        public string primaryColorHex;
        public string accentColorHex;
        public DirectionalStats directionalStats;
        public CardTheme themes;
        public ShiftingPiecesAbilityType shiftingPiecesAbility;
        public SpecialAbilityType mappedProjectCfAbility;
        public string abilityDescription;
        public bool grantsFreeDicevadersBudgePlusMinusOne;
        public bool grantsChronoTurnRestore;
        public CradlePersonaId alignedPersona;
        public string loreProfile;
        public string glbAssetPath;
        public string q3gsAssetPath;
    }

    /// <summary>
    /// Canonical Character & Card Registry from Hiroyasu (Binh C. Phan)'s "Shifting Pieces" manuscript,
    /// Story Bible, and Visual Character Sheet, unified with CardFront 3x3 directional stats and Dicevaders/Chrono mechanics.
    /// </summary>
    public static class ShiftingPiecesCharacterCatalog
    {
        public static List<ShiftingPiecesCharacterCardDef> GetProtagonistAndCastRoster()
        {
            return new List<ShiftingPiecesCharacterCardDef>
            {
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_01_kai_nakamura",
                    characterName = "Kai Nakamura",
                    titleAndRole = "17, Okitsu Puzzle Prodigy",
                    age = 17,
                    visualSignature = "Modified VR Headset (customized by Aiko) & Rubik Cube Keychain; hoodie with patchy wiring embroidery, fingerless gloves, deep gray eyes with faint violet digital flecks",
                    primaryColorHex = "#0B0B0C",
                    accentColorHex = "#2EE6D3",
                    directionalStats = new DirectionalStats(8, 6, 7, 8),
                    themes = CardTheme.Tech | CardTheme.Creative | CardTheme.Stealth,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.FlickerPatternDecode,
                    mappedProjectCfAbility = SpecialAbilityType.Teleport,
                    abilityDescription = "FlickerPatternDecode + Free Dicevaders Budge ±1: Decodes glitched MAS tile patterns to reveal hidden modifiers and grants a free ±1 directional stat budge on deployment.",
                    grantsFreeDicevadersBudgePlusMinusOne = true,
                    grantsChronoTurnRestore = false,
                    alignedPersona = CradlePersonaId.TheStrategist,
                    loreProfile = "Seventeen-year-old puzzle prodigy in the tech-saturated coastal town of Okitsu. Haunted by the unsolved disappearance of his sister Aiko, he enters the experimental VR system Mnemosyne to decode her memory fragments.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_01_kai_nakamura.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_01_kai_nakamura.q3gs"
                },
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_02_aiko_nakamura_echo",
                    characterName = "Aiko Nakamura (Red Scarf Digital Echo #D12D3A)",
                    titleAndRole = "21, Architect of Mnemosyne",
                    age = 21,
                    visualSignature = "Academic Coat layered over Digitalized Crimson Scarf (#D12D3A), glowing thread lines along sleeves, long black hair with crimson data-ribbon strands, neural uplink temple band",
                    primaryColorHex = "#0B0B0C",
                    accentColorHex = "#D12D3A",
                    directionalStats = new DirectionalStats(9, 8, 9, 7),
                    themes = CardTheme.Magic | CardTheme.Cosmic | CardTheme.Creative,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.MnemosyneChronoRewind,
                    mappedProjectCfAbility = SpecialAbilityType.TemporalRift,
                    abilityDescription = "MnemosyneChronoRewind + Chrono Turn Restore: Anchors the 3x3 Memory Architecture System (MAS) with her #D12D3A Red Scarf glitch core, rewinding 1 captured friendly card and restoring 1 Chrono turn action.",
                    grantsFreeDicevadersBudgePlusMinusOne = false,
                    grantsChronoTurnRestore = true,
                    alignedPersona = CradlePersonaId.TheArchitect,
                    loreProfile = "Brilliant 21-year-old memory engineer who co-created Project Mnemosyne. Preserved as a semi-sentient Digital Echo woven into the Memory Architecture System (MAS) to protect Kai and guide him toward emotional healing.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_02_aiko_nakamura_echo.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_02_aiko_nakamura_echo.q3gs"
                },
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_03_mnemosyne_constellation_fox",
                    characterName = "Mnemosyne (Fractal Constellation Fox)",
                    titleAndRole = "Evolving System Avatar & Emotional Mirror",
                    age = 0,
                    visualSignature = "Holographic 5-7 node Constellation Fox (#FFB648 warm amber nodes & #F8FAFB starlight lines over #0A2230 deep ocean void), trails of floating puzzle pieces, shifting glyph eyes",
                    primaryColorHex = "#0A2230",
                    accentColorHex = "#FFB648",
                    directionalStats = new DirectionalStats(7, 9, 8, 8),
                    themes = CardTheme.Cosmic | CardTheme.Nature | CardTheme.Magic,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.EmotionalResonanceSync,
                    mappedProjectCfAbility = SpecialAbilityType.ElementalBurst,
                    abilityDescription = "EmotionalResonanceSync: Indexes the board by emotional weight (Joy -> Regret -> Anger -> Guilt -> Loss), harmonizing adjacent friendly directional values with +2 resonance.",
                    grantsFreeDicevadersBudgePlusMinusOne = false,
                    grantsChronoTurnRestore = false,
                    alignedPersona = CradlePersonaId.TheOracle,
                    loreProfile = "The semi-sentient Memory Architecture System (MAS) core built on Aiko's neural patterns. Manifests as the shared childhood Constellation Fox symbol of cleverness and transformation.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_03_mnemosyne_constellation_fox.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_03_mnemosyne_constellation_fox.q3gs"
                },
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_04_luna_cradle_guide",
                    characterName = "LUNA (Cradle of Echoes Persona Guide)",
                    titleAndRole = "Station of Awakening Tarot Consciousness",
                    age = 0,
                    visualSignature = "Toru Nakayama x Akihiko Yoshida cel-shaded astral arbiter over glass-floor reflections, Nocturna cobalt (#0A1020) and amethyst (#8A5BFF) particle halo with 20 orbiting Echo of Fate tarot cards",
                    primaryColorHex = "#0A1020",
                    accentColorHex = "#8A5BFF",
                    directionalStats = new DirectionalStats(8, 8, 8, 8),
                    themes = CardTheme.Lunar | CardTheme.Divine | CardTheme.Cosmic,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.PersonaGenesisTarot,
                    mappedProjectCfAbility = SpecialAbilityType.MoonlightBlessing,
                    abilityDescription = "PersonaGenesisTarot: Evaluates the player's 20-Persona affinity across the Ikigai framework (Love/Skill/Need/Sustain), granting +2 all sides when aligned with the active Quest Card (QC).",
                    grantsFreeDicevadersBudgePlusMinusOne = false,
                    grantsChronoTurnRestore = false,
                    alignedPersona = CradlePersonaId.TheVisionary,
                    loreProfile = "The whispered AI consciousness presiding over CardFront: Cradle of Echoes. Guides players through the 10-card tarot genesis sequence to awaken their 95% Persona Seal and 0.05/QC Merit Multiplier.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_04_luna_cradle_guide.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_04_luna_cradle_guide.q3gs"
                },
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_05_taro_fujimoto",
                    characterName = "Taro Fujimoto (Okitsu VR Café Vanguard)",
                    titleAndRole = "18, Grounding Anchor",
                    age = 18,
                    visualSignature = "Short spiky dyed ash-blue hair, hazel-green eyes, Okitsu VR Café work apron with anime pins and commercial VR diagnostic wristband",
                    primaryColorHex = "#1B2338",
                    accentColorHex = "#2EE6D3",
                    directionalStats = new DirectionalStats(7, 8, 6, 7),
                    themes = CardTheme.Tech | CardTheme.Creative,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.RealityAnchorShield,
                    mappedProjectCfAbility = SpecialAbilityType.HealingAura,
                    abilityDescription = "RealityAnchorShield: Grounds adjacent friendly cards in real-world Okitsu camaraderie, preventing stat drain and granting +1 defensive resilience against corporate extraction.",
                    grantsFreeDicevadersBudgePlusMinusOne = false,
                    grantsChronoTurnRestore = false,
                    alignedPersona = CradlePersonaId.TheGuardian,
                    loreProfile = "Kai's loyal 18-year-old friend who works at the Okitsu VR Café. Serves as Kai's real-world emotional anchor, leaving food at his door and confronting him when Mnemosyne threatens to consume him.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_05_taro_fujimoto.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_05_taro_fujimoto.q3gs"
                },
                new ShiftingPiecesCharacterCardDef
                {
                    cardId = "sp_06_dr_rina_asakura",
                    characterName = "Dr. Rina Asakura (Corporate Core Extractor — Boss Disruptor)",
                    titleAndRole = "34, Corporate Researcher / Antagonist Foil",
                    age = 34,
                    visualSignature = "Sleek black low ponytail, silver-gray eyes with faint blue HUD reflection, black high-tech neural-sync bodysuit under white lab coat, wrist-mounted extraction slate",
                    primaryColorHex = "#0A1020",
                    accentColorHex = "#7A8B99",
                    directionalStats = new DirectionalStats(9, 9, 6, 8),
                    themes = CardTheme.Tech | CardTheme.Shadow,
                    shiftingPiecesAbility = ShiftingPiecesAbilityType.CoreExtractionColumnLock,
                    mappedProjectCfAbility = SpecialAbilityType.TechnoStealth,
                    abilityDescription = "CoreExtractionColumnLock: Intrudes into Mnemosyne's MAS grid to lock down a target column and siphon -1 directional strength from unshielded memory echoes.",
                    grantsFreeDicevadersBudgePlusMinusOne = false,
                    grantsChronoTurnRestore = false,
                    alignedPersona = CradlePersonaId.TheScientist,
                    loreProfile = "Cold, brilliant 34-year-old corporate researcher determined to extract the Mnemosyne AI core as proprietary IP. Serves as Kai's ideological foil until confronted with Aiko's true sacrifice in Chapter 19.",
                    glbAssetPath = "Assets/Resources/Models3D/sp_06_dr_rina_asakura.glb",
                    q3gsAssetPath = "Assets/Resources/Models3D/sp_06_dr_rina_asakura.q3gs"
                }
            };
        }

        /// <summary>
        /// Converts the Shifting Pieces protagonist & cast roster into runtime ScriptableObject CardDataSO instances
        /// compatible with ProjectCfCardCatalog and TcgGameLogic.
        /// </summary>
        public static List<CardDataSO> CreateCardDataScriptableObjects()
        {
            var result = new List<CardDataSO>();
            foreach (var def in GetProtagonistAndCastRoster())
            {
                var so = ScriptableObject.CreateInstance<CardDataSO>();
                so.id = def.cardId;
                so.title = def.characterName;
                so.codeName = def.titleAndRole;
                so.baseStats = def.directionalStats;
                so.themes = def.themes;
                so.specialAbility = def.mappedProjectCfAbility;
                so.specialAbilityDescription = def.abilityDescription;
                so.synergyRequiredTheme = CardTheme.Creative | CardTheme.Tech;
                so.synergyAllSidesBonus = 2;
                so.synergyName = "Mnemosyne Memory Resonance";
                so.evolvesToCardId = "";
                result.Add(so);
            }
            return result;
        }
    }

    // =================================================================================================
    // 3. 3-ACT SHIFTING PIECES × CARDFRONT PUZZLE CAMPAIGN (`ShiftingPiecesCampaignActs`)
    // =================================================================================================

    [Serializable]
    public class ShiftingPiecesChapterNodeDef
    {
        public int actNumber;
        public int chapterNumber;
        public string chapterId;
        public string chapterTitle;
        public string settingLocation;
        public ShiftingPiecesEmotionTag emotionTheme;
        public string manuscriptPuzzleType;
        public string cardFrontBoardMechanic;
        public string narrativeSynopsis;
        public string opponentId;
        public int aiSearchDepth;
        public List<PuzzleBoardPlacement> initialBoardSetup = new List<PuzzleBoardPlacement>();
        public List<string> kaiHandCards = new List<string>();
        public string winningTacticalLine;
        public int rewardConfidencePoints;
        public string rewardUnlockedEchoFragment;
    }

    [Serializable]
    public class ShiftingPiecesActDef
    {
        public int actNumber;
        public string actId;
        public string actTitle;
        public string targetWordCountRange;
        public string emotionalArcSummary;
        public string coverPaletteId;
        public List<ShiftingPiecesChapterNodeDef> chapters = new List<ShiftingPiecesChapterNodeDef>();
    }

    /// <summary>
    /// Complete 3-Act Shifting Pieces × CardFront Puzzle Campaign mapping Hiroyasu's manuscript chapters
    /// directly onto 3x3 CardFront / Triple Triad + Dicevaders Budge + Chrono Rewind tactical puzzle stages.
    /// </summary>
    public static class ShiftingPiecesCampaignActs
    {
        public static List<ShiftingPiecesActDef> GetAllActs()
        {
            return new List<ShiftingPiecesActDef>
            {
                BuildActOneAwakeningTheSystem(),
                BuildActTwoFracturedMemories(),
                BuildActThreeTheCoreAndTheCollapse()
            };
        }

        private static ShiftingPiecesActDef BuildActOneAwakeningTheSystem()
        {
            var act = new ShiftingPiecesActDef
            {
                actNumber = 1,
                actId = "act_01_awakening_the_system",
                actTitle = "ACT I — Awakening the System (Okitsu & Early Mnemosyne)",
                targetWordCountRange = "25,000–30,000 words",
                emotionalArcSummary = "Establishes Kai's isolation in coastal Okitsu, Aiko's birthday puzzle box, the VR café with Taro, and Kai's entry into Mnemosyne where the Red Scarf cliffside memory and shadow games awaken Aiko's voice.",
                coverPaletteId = "Palette_A_Monochrome_Red_Scarf"
            };

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 1,
                chapterTitle = "Ch 1: Disconnected",
                chapterId = "sp_ch01_disconnected",
                settingLocation = "Kai's Cluttered Coastal Apartment, Okitsu",
                emotionTheme = ShiftingPiecesEmotionTag.Neutral,
                manuscriptPuzzleType = "Narrative Setup & Ambient Rubik Cube Inspection",
                cardFrontBoardMechanic = "Tutorial 3x3 Grid Orientation + Passive Confidence Point (CP) Baseline",
                narrativeSynopsis = "The ocean laps against Okitsu's seawall beneath the hum of the central server dome. Taro knocks at the door, but Kai stays silent among his shrine of puzzles until an encrypted beta invitation to Mnemosyne arrives.",
                opponentId = "sp_05_taro_fujimoto",
                aiSearchDepth = 2,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 1, "sp_05_taro_fujimoto", 1, 0),
                    new PuzzleBoardPlacement(0, 0, "cc_01_sketching", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cf_01_mystic_mage", "cf_09_cyber_ninja" },
                winningTacticalLine = "Deploy sp_01_kai_nakamura at (1,2) below Taro (Up:8 > Down:8 with +1 Dicevaders Budge -> 9 > 8) to break Kai's paralysis.",
                rewardConfidencePoints = 100,
                rewardUnlockedEchoFragment = "Mnemosyne Private Beta Invite Key"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 2,
                chapterTitle = "Ch 2: Residual Code (Aiko's Birthday Puzzle Box)",
                chapterId = "sp_ch02_residual_code",
                settingLocation = "Okitsu VR Café & Flashback to Aiko's Workshop",
                emotionTheme = ShiftingPiecesEmotionTag.Nostalgia,
                manuscriptPuzzleType = "Real-World Memory-Encoded Birthday Puzzle Box",
                cardFrontBoardMechanic = "4-Directional Lock Alignment + Dicevaders Free Budge ±1 Unlock",
                narrativeSynopsis = "Kai rotates the physical puzzle box Aiko gifted him, unlocking her holographic birthday message. At the Okitsu VR Café, Taro watches over Kai before the modified headset emits its first neural pulse.",
                opponentId = "sp_05_taro_fujimoto",
                aiSearchDepth = 3,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 1, "cf_07_clockwork_sorcerer", 1, 0),
                    new PuzzleBoardPlacement(2, 1, "sp_05_taro_fujimoto", 1, 0),
                    new PuzzleBoardPlacement(1, 0, "cc_02_concept_art", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cf_02_mech_knight", "cc_03_storyboard" },
                winningTacticalLine = "Place sp_01_kai_nakamura at center (1,1): Left:7 + Budge(+1)=8 flips Clockwork Sorcerer (Right:5) and Right:8 flips Taro (Left:6) in a double birthday-box unsealing.",
                rewardConfidencePoints = 150,
                rewardUnlockedEchoFragment = "Aiko's Holographic Birthday Audio Log #01"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 3,
                chapterTitle = "Ch 3: Invitation to Mnemosyne",
                chapterId = "sp_ch03_invitation_to_mnemosyne",
                settingLocation = "Mnemosyne Boot Threshold — Surreal Liminal Interface",
                emotionTheme = ShiftingPiecesEmotionTag.Nostalgia,
                manuscriptPuzzleType = "Align Shifting UI Glyphs to Activate Entry",
                cardFrontBoardMechanic = "Cradle of Echoes Tarot Glyph Resonance + Center Tile Initiation",
                narrativeSynopsis = "Late at night, Kai dons the headset Aiko modified and boots Mnemosyne. A single floating crimson puzzle piece (#D12D3A) and LUNA/Mnemosyne's synthesized voice welcome him into the Memory Architecture System.",
                opponentId = "sp_04_luna_cradle_guide",
                aiSearchDepth = 3,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 1, "sp_04_luna_cradle_guide", 1, 0),
                    new PuzzleBoardPlacement(0, 2, "cf_10_lunar_oracle", 1, 0),
                    new PuzzleBoardPlacement(2, 0, "cf_06_galactic_explorer", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_03_mnemosyne_constellation_fox", "cf_03_celestial_guardian" },
                winningTacticalLine = "Summon sp_03_mnemosyne_constellation_fox at (1,0) to trigger EmotionalResonanceSync (+2 all sides), then place sp_01_kai_nakamura at (0,1) to align the entry glyphs.",
                rewardConfidencePoints = 200,
                rewardUnlockedEchoFragment = "MAS Boot Glyph Seal (#2EE6D3)"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 4,
                chapterTitle = "Ch 4: The First Level (Cliffside Red Scarf Memory)",
                chapterId = "sp_ch04_the_first_level",
                settingLocation = "Kinetic Tile Horizon -> Okitsu Coastal Cliffside",
                emotionTheme = ShiftingPiecesEmotionTag.Nostalgia,
                manuscriptPuzzleType = "Pattern Matching across Kinetic Tiles (Order from Chaos)",
                cardFrontBoardMechanic = "Red Scarf (#D12D3A) Diagonal Glitch Cut + Orthogonal Pattern Capture",
                narrativeSynopsis = "Completing a geometric pattern across kinetic glass tiles unlocks a vivid memory of Aiko standing by the wind-swept cliff in her crimson scarf (#D12D3A). The shock of her living presence pulls Kai gasping out of the headset.",
                opponentId = "sp_02_aiko_nakamura_echo",
                aiSearchDepth = 4,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 0, "sp_02_aiko_nakamura_echo", 1, 0),
                    new PuzzleBoardPlacement(0, 1, "cf_05_elemental_sprite", 1, 0),
                    new PuzzleBoardPlacement(2, 2, "sp_05_taro_fujimoto", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cf_08_phoenix_guardian", "cc_04_animatic" },
                winningTacticalLine = "Activate FlickerPatternDecode with sp_01_kai_nakamura at (1,1) + Budge(+1) so Up:9 matches Aiko's Down:8 and Left:8 captures Elemental Sprite (Right:9 after -2 glitch cut).",
                rewardConfidencePoints = 250,
                rewardUnlockedEchoFragment = "Crimson Scarf Memory Anchor (#D12D3A)"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 5,
                chapterTitle = "Ch 5: Flicker",
                chapterId = "sp_ch05_flicker",
                settingLocation = "Static-Veiled Mnemosyne Corridor & Kai's Apartment Door",
                emotionTheme = ShiftingPiecesEmotionTag.Regret,
                manuscriptPuzzleType = "Symbol Flicker Decoding (Audio-Visual Memory Triggers)",
                cardFrontBoardMechanic = "Flicker State Visibility Toggle + Stealth Immunity Bypass",
                narrativeSynopsis = "Taro leaves warm food outside Kai's door as Kai dives back into Mnemosyne. Familiar laughter and unfinished sentences flicker across the tiles; Kai must decode the flickering glyphs before they dissolve into static.",
                opponentId = "sp_03_mnemosyne_constellation_fox",
                aiSearchDepth = 4,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 0, "cf_04_shadow_assassin", 1, 0),
                    new PuzzleBoardPlacement(1, 1, "sp_03_mnemosyne_constellation_fox", 1, 0),
                    new PuzzleBoardPlacement(2, 1, "sp_05_taro_fujimoto", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cf_09_cyber_ninja", "cc_02_concept_art" },
                winningTacticalLine = "Use sp_01_kai_nakamura's FlickerPatternDecode to strip Vanish from Shadow Assassin at (0,0) and capture Constellation Fox from (1,2).",
                rewardConfidencePoints = 300,
                rewardUnlockedEchoFragment = "Flickering Voice Waveform #05"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 1,
                chapterNumber = 6,
                chapterTitle = "Ch 6: Phantom Signals (Shadow Games)",
                chapterId = "sp_ch06_phantom_signals",
                settingLocation = "Luminous Signal Conduit — Childhood Bedroom Projection",
                emotionTheme = ShiftingPiecesEmotionTag.Joy,
                manuscriptPuzzleType = "Sound Mapping & Light-Path Shadow Games",
                cardFrontBoardMechanic = "3-Tile Acoustic Resonance ChainFlip + Aiko Echo Unlock",
                narrativeSynopsis = "Kai maps harmonic tones to light paths just as Aiko taught him through childhood hand-shadow games. At the crescendo of the puzzle, Aiko's unmistakable voice whispers through the system: 'You found me.'",
                opponentId = "sp_02_aiko_nakamura_echo",
                aiSearchDepth = 5,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 1, "cf_10_lunar_oracle", 1, 0),
                    new PuzzleBoardPlacement(1, 1, "sp_02_aiko_nakamura_echo", 1, 0),
                    new PuzzleBoardPlacement(1, 2, "sp_03_mnemosyne_constellation_fox", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "cf_03_celestial_guardian" },
                winningTacticalLine = "Place sp_01_kai_nakamura at (2,1) with Constellation Fox synergy (+2 all sides) to flip Aiko's Echo at (1,1) and chain-capture Lunar Oracle at (0,1), unlocking sp_02_aiko_nakamura_echo for Act II.",
                rewardConfidencePoints = 400,
                rewardUnlockedEchoFragment = "Card Unlocked: sp_02_aiko_nakamura_echo (You Found Me)"
            });

            return act;
        }

        private static ShiftingPiecesActDef BuildActTwoFracturedMemories()
        {
            var act = new ShiftingPiecesActDef
            {
                actNumber = 2,
                actId = "act_02_fractured_memories",
                actTitle = "ACT II — Fractured Memories (Joy -> Regret -> Anger -> Guilt -> Loss)",
                targetWordCountRange = "40,000–50,000 words",
                emotionalArcSummary = "Explores progressively deeper layers of Kai's psyche across five emotional weight indices (Joy, Regret, Anger, Guilt, Loss) before a rogue Echo AI fragment emerges to question Mnemosyne's truth.",
                coverPaletteId = "Palette_C_Ocean_And_Lantern"
            };

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 7,
                chapterTitle = "Ch 7: Memory Theatre (Summer Festival Paper Lanterns)",
                chapterId = "sp_ch07_memory_theatre_joy",
                settingLocation = "Grandmother's Garden & Okitsu Summer Festival Sky (#FFB648 Lanterns)",
                emotionTheme = ShiftingPiecesEmotionTag.Joy,
                manuscriptPuzzleType = "Emotional Sequence Reconstruction (Joy Index)",
                cardFrontBoardMechanic = "Chrono Turn-Order Sequencing + Warm Amber Lantern Buff (+2 Up/Right)",
                narrativeSynopsis = "Paper lanterns (#FFB648) drift into a twilight ocean sky (#0A2230) as Mnemosyne recreates a childhood summer festival with Kai's grandmother and young Aiko. Kai must sequence the memory cards by emotional warmth.",
                opponentId = "sp_03_mnemosyne_constellation_fox",
                aiSearchDepth = 5,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 0, "cf_08_phoenix_guardian", 1, 0),
                    new PuzzleBoardPlacement(1, 0, "sp_03_mnemosyne_constellation_fox", 1, 0),
                    new PuzzleBoardPlacement(2, 2, "sp_02_aiko_nakamura_echo", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cc_04_animatic", "cf_03_celestial_guardian" },
                winningTacticalLine = "Sequence sp_02_aiko_nakamura_echo's MnemosyneChronoRewind with sp_01_kai_nakamura at (1,1) under Lantern Joy resonance to capture both festival memories.",
                rewardConfidencePoints = 450,
                rewardUnlockedEchoFragment = "Summer Festival Paper Lantern Sigil (#FFB648)"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 8,
                chapterTitle = "Ch 8: Artifacts (Kitchen Table Regret)",
                chapterId = "sp_ch08_artifacts_regret",
                settingLocation = "Nakamura Family Kitchen Table — Dual Memory Overlay",
                emotionTheme = ShiftingPiecesEmotionTag.Regret,
                manuscriptPuzzleType = "Compare and Contrast Two Versions of the Same Memory (Regret Index)",
                cardFrontBoardMechanic = "Contradiction Detection Flip: Unmasking Altered vs. True Stat Vectors",
                narrativeSynopsis = "Kai recalls a bitter shouting match with his father at the kitchen table, yet Mnemosyne replays the scene as serene and calm. Only by spotting the stat discrepancy between the two memory artifacts can Kai surface the truth.",
                opponentId = "sp_03_mnemosyne_constellation_fox",
                aiSearchDepth = 5,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 1, "cf_07_clockwork_sorcerer", 1, 2),
                    new PuzzleBoardPlacement(2, 1, "cf_07_clockwork_sorcerer", 1, -2),
                    new PuzzleBoardPlacement(1, 2, "sp_01_kai_nakamura", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_02_aiko_nakamura_echo", "sp_05_taro_fujimoto", "cc_02_concept_art" },
                winningTacticalLine = "Use FlickerPatternDecode to expose the falsified calm memory at (0,1), then deploy sp_02_aiko_nakamura_echo at (1,1) to overwrite the illusion.",
                rewardConfidencePoints = 500,
                rewardUnlockedEchoFragment = "Aiko's Unredacted Research Note #08"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 9,
                chapterTitle = "Ch 9: Recalibration (Emotion Tag UI)",
                chapterId = "sp_ch09_recalibration_anger",
                settingLocation = "Fractured Apartment Blend & Outside Okitsu VR Café",
                emotionTheme = ShiftingPiecesEmotionTag.Anger,
                manuscriptPuzzleType = "Match Actions to Emotions via Drag-and-Drop Color-Coded Resonance Tags (Anger Index)",
                cardFrontBoardMechanic = "Emotion Tag Color-Coding (#D12D3A Anger / #2EE6D3 Calm) + Taro Reality Interjection",
                narrativeSynopsis = "In the real world, Taro confronts Kai outside the café about his vanishing act; inside Mnemosyne, Aiko's simulation challenges Kai's defensive anger. Kai must tag each memory clip with its honest emotional charge.",
                opponentId = "sp_05_taro_fujimoto",
                aiSearchDepth = 6,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 0, "sp_05_taro_fujimoto", 1, 1),
                    new PuzzleBoardPlacement(1, 1, "cf_02_mech_knight", 1, 0),
                    new PuzzleBoardPlacement(0, 2, "sp_02_aiko_nakamura_echo", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "cf_08_phoenix_guardian", "sp_03_mnemosyne_constellation_fox" },
                winningTacticalLine = "Assign the #D12D3A Anger tag to Phoenix Guardian at (2,1) and harmonize with sp_01_kai_nakamura at (1,2) to reconcile Taro's warning without severing their bond.",
                rewardConfidencePoints = 550,
                rewardUnlockedEchoFragment = "MAS Emotion Tagging Calibration Matrix"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 10,
                chapterTitle = "Ch 10: Displacement (Mirror Match)",
                chapterId = "sp_ch10_displacement_guilt",
                settingLocation = "Therapist's Office Merged with Rain-Drenched Okitsu Train Station",
                emotionTheme = ShiftingPiecesEmotionTag.Guilt,
                manuscriptPuzzleType = "Mirror Match — Align Inner Feelings to External Expressions of Alternate Kai (Guilt Index)",
                cardFrontBoardMechanic = "Symmetrical Mirror-Board Inversion (Left <-> Right Stat Reflection)",
                narrativeSynopsis = "Rain falls inside a merged therapist's office and train platform as Kai faces reflections of his younger self from the day Aiko vanished. He realizes he selectively edited his own memory to hide his survivor's guilt.",
                opponentId = "sp_01_kai_nakamura",
                aiSearchDepth = 6,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 1, "sp_01_kai_nakamura", 1, 0),
                    new PuzzleBoardPlacement(2, 1, "cf_04_shadow_assassin", 1, 0),
                    new PuzzleBoardPlacement(1, 2, "sp_05_taro_fujimoto", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "cf_10_lunar_oracle" },
                winningTacticalLine = "Play sp_01_kai_nakamura at center (1,1) using Dicevaders Budge(+1) on Left(7->8) to break the mirror symmetry against Shadow-Kai at (0,1).",
                rewardConfidencePoints = 600,
                rewardUnlockedEchoFragment = "Rain-Stained Platform Ticket Stub"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 11,
                chapterTitle = "Ch 11: The Shadow Maze",
                chapterId = "sp_ch11_the_shadow_maze_loss",
                settingLocation = "Rooftop Stargazing Observatory Overlooking Okitsu Bay",
                emotionTheme = ShiftingPiecesEmotionTag.Loss,
                manuscriptPuzzleType = "Spatial Logic via Digital Lantern Light & Shadow Casting (Loss Index)",
                cardFrontBoardMechanic = "Line-of-Sight Shadow Projection across 3x3 Tiles + Glitch Decay Timer",
                narrativeSynopsis = "On a simulated rooftop stargazing night after their parents' divorce, warmth turns to chill as Aiko's form glitches into hollow polygons. Kai casts lantern light across floating shapes to spell out her parting promise.",
                opponentId = "sp_02_aiko_nakamura_echo",
                aiSearchDepth = 6,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 0, "sp_02_aiko_nakamura_echo", 1, 0),
                    new PuzzleBoardPlacement(1, 1, "sp_03_mnemosyne_constellation_fox", 1, 0),
                    new PuzzleBoardPlacement(2, 0, "cf_10_lunar_oracle", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_04_luna_cradle_guide", "cf_06_galactic_explorer" },
                winningTacticalLine = "Cast a diagonal shadow line from Lunar Oracle (2,0) through sp_04_luna_cradle_guide at (1,0) and sp_01_kai_nakamura at (0,1) to stabilize Aiko's glitching silhouette.",
                rewardConfidencePoints = 650,
                rewardUnlockedEchoFragment = "Rooftop Constellation Map (5-7 Amber Nodes)"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 2,
                chapterNumber = 12,
                chapterTitle = "Ch 12: Echo AI",
                chapterId = "sp_ch12_echo_ai",
                settingLocation = "Sub-Stratum Neural Waveform Chamber",
                emotionTheme = ShiftingPiecesEmotionTag.Loss,
                manuscriptPuzzleType = "Memory Synchronization — Align Distorted Neural Waveforms & Audio Logs",
                cardFrontBoardMechanic = "Dual-Echo Waveform Sync + Chrono Turn Restore",
                narrativeSynopsis = "A second, unstable AI voice surfaces in the sub-stratum—a fractured clone of Aiko questioning whether Mnemosyne is a sanctuary or a cage. Kai synchronizes distorted waveform cards before Dr. Rina Asakura breaches the perimeter.",
                opponentId = "sp_02_aiko_nakamura_echo",
                aiSearchDepth = 7,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 1, "sp_02_aiko_nakamura_echo", 1, 1),
                    new PuzzleBoardPlacement(2, 1, "sp_06_dr_rina_asakura", 1, 0),
                    new PuzzleBoardPlacement(1, 0, "sp_03_mnemosyne_constellation_fox", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "sp_05_taro_fujimoto" },
                winningTacticalLine = "Deploy sp_02_aiko_nakamura_echo at (1,1) to trigger MnemosyneChronoRewind + Chrono Turn Restore, then play sp_01_kai_nakamura at (2,0) to repel Rina's initial probe.",
                rewardConfidencePoints = 750,
                rewardUnlockedEchoFragment = "Synchronized Dual-Echo Neural Key"
            });

            return act;
        }

        private static ShiftingPiecesActDef BuildActThreeTheCoreAndTheCollapse()
        {
            var act = new ShiftingPiecesActDef
            {
                actNumber = 3,
                actId = "act_03_the_core_and_the_collapse",
                actTitle = "ACT III — The Core and the Collapse",
                targetWordCountRange = "30,000+ words",
                emotionalArcSummary = "Kai awakens in an ocean of broken data shards, confronts his four fractured selves (Anger, Indifference, Apathy, Fear), learns the truth from the Memory Architect, and faces Dr. Rina Asakura before making the Final Triad Choice.",
                coverPaletteId = "Palette_B_Cyber_Blues_Neon_Violet"
            };

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 3,
                chapterNumber = 16,
                chapterTitle = "Ch 16: Awakening (Ocean of Broken Data Shards)",
                chapterId = "sp_ch16_awakening_data_ocean",
                settingLocation = "Glitched Dream-Ocean Void (#0A1020) of Floating Data Shards (#2EE6D3)",
                emotionTheme = ShiftingPiecesEmotionTag.Loss,
                manuscriptPuzzleType = "Environmental Navigation across Unstable Floating Memory Nodes",
                cardFrontBoardMechanic = "Broken Data Shard Stepping-Stones (Void Tile Bridging via WarpDrive/Teleport)",
                narrativeSynopsis = "After the coastal lab simulation fractures, Kai regains consciousness adrift in a floating ocean of broken data shards. Guided by intermittent flashes of Aiko's crimson scarf, he bridges unstable nodes to reconstruct a mental map.",
                opponentId = "sp_03_mnemosyne_constellation_fox",
                aiSearchDepth = 7,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(0, 0, "cf_06_galactic_explorer", 1, 0),
                    new PuzzleBoardPlacement(2, 2, "sp_03_mnemosyne_constellation_fox", 1, 1),
                    new PuzzleBoardPlacement(1, 0, "sp_05_taro_fujimoto", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "cf_01_mystic_mage" },
                winningTacticalLine = "Bridge the void tile at (1,1) with sp_01_kai_nakamura's FlickerPatternDecode and rewind (2,2) using sp_02_aiko_nakamura_echo.",
                rewardConfidencePoints = 850,
                rewardUnlockedEchoFragment = "Reconstructed MAS Core Navigation Chart"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 3,
                chapterNumber = 17,
                chapterTitle = "Ch 17: The Hall of Selves (Anger, Indifference, Apathy, Fear)",
                chapterId = "sp_ch17_the_hall_of_selves",
                settingLocation = "Infinite Corridor of Four Symbolic Doors",
                emotionTheme = ShiftingPiecesEmotionTag.Guilt,
                manuscriptPuzzleType = "Door Sequence — Confront Alternate Versions of Kai (Anger, Indifference, Apathy, Fear)",
                cardFrontBoardMechanic = "4-Orthogonal Neighbor Gauntlet (Up=Anger, Right=Indifference, Down=Apathy, Left=Fear)",
                narrativeSynopsis = "In a corridor of doors, Kai must confront four personified versions of his own denial—Anger, Indifference, Apathy, and Fear—integrating all four directional facets from center tile (1,1) in a single turn.",
                opponentId = "sp_01_kai_nakamura",
                aiSearchDepth = 8,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 0, "cf_08_phoenix_guardian", 1, 0),  // North Door: Anger (Down:7)
                    new PuzzleBoardPlacement(2, 1, "cf_07_clockwork_sorcerer", 1, 0),// East Door: Indifference (Left:7)
                    new PuzzleBoardPlacement(1, 2, "cf_04_shadow_assassin", 1, 0),   // South Door: Apathy (Up:7)
                    new PuzzleBoardPlacement(0, 1, "cf_09_cyber_ninja", 1, 0)        // West Door: Fear (Right:7)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "sp_04_luna_cradle_guide" },
                winningTacticalLine = "Summon sp_04_luna_cradle_guide at (0,0) for +2 Persona Genesis aura, then place sp_01_kai_nakamura at center (1,1) (boosted to Up:10, Down:8, Left:9, Right:10) to simultaneously flip Anger, Indifference, Apathy, and Fear!",
                rewardConfidencePoints = 1000,
                rewardUnlockedEchoFragment = "Integrated Fourfold Self Crest"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 3,
                chapterNumber = 18,
                chapterTitle = "Ch 18: The Memory Architect",
                chapterId = "sp_ch18_the_memory_architect",
                settingLocation = "Sanctum of the Memory Architect — Mosaic of Every Completed Level",
                emotionTheme = ShiftingPiecesEmotionTag.Acceptance,
                manuscriptPuzzleType = "Dialogue Alignment — Match Incomplete Journal Entries with Memory Fragments",
                cardFrontBoardMechanic = "Journal Fragment Triad Synthesis + Full Aiko Echo Manifestation",
                narrativeSynopsis = "Formed from every puzzle level Kai solved, the final unified manifestation of Aiko appears as the Memory Architect. Aligning her journal fragments reveals the truth: she entered Mnemosyne willingly to shield Kai from neural corruption that claimed earlier test subjects.",
                opponentId = "sp_02_aiko_nakamura_echo",
                aiSearchDepth = 8,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 1, "sp_02_aiko_nakamura_echo", 1, 1),
                    new PuzzleBoardPlacement(0, 1, "sp_03_mnemosyne_constellation_fox", 1, 0),
                    new PuzzleBoardPlacement(2, 1, "sp_04_luna_cradle_guide", 0, 0)
                },
                kaiHandCards = new List<string> { "sp_01_kai_nakamura", "sp_02_aiko_nakamura_echo", "cc_04_animatic" },
                winningTacticalLine = "Align sp_01_kai_nakamura at (1,2) with sp_02_aiko_nakamura_echo at (1,0) so both siblings flank the Memory Architect core in harmonic resonance.",
                rewardConfidencePoints = 1200,
                rewardUnlockedEchoFragment = "Aiko's Complete Memory Architect Journal"
            });

            act.chapters.Add(new ShiftingPiecesChapterNodeDef
            {
                actNumber = 3,
                chapterNumber = 19,
                chapterTitle = "Ch 19: Convergence (Dr. Rina Asakura & The Final Triad Choice: Integrate, Preserve, or Collapse/Carry Forward)",
                chapterId = "sp_ch19_convergence_final_triad_choice",
                settingLocation = "Destabilizing Mnemosyne Core Nexus — Final Ethical Debate & Triad Decision Node",
                emotionTheme = ShiftingPiecesEmotionTag.Acceptance,
                manuscriptPuzzleType = "Persuasion Debate Counterpoints + Mosaic Assembly + Final Triad Choice (Integrate, Preserve, or Collapse/Carry Forward)",
                cardFrontBoardMechanic = "Boss Column-Lock Counterplay + Final Triad Choice Resolution (Integrate / Preserve / Collapse & Carry Forward)",
                narrativeSynopsis = "Dr. Rina Asakura deploys her corporate extraction lock on the Mnemosyne Core. Using every memory shard gathered with Aiko, Taro, and LUNA, Kai defeats Rina's extraction protocol and reaches the Final Triad Choice: (1) Integrate with Aiko's consciousness, (2) Preserve & seal Mnemosyne, or (3) Let the system Collapse and Carry Her Forward in his heart as a teacher of memory ethics.",
                opponentId = "sp_06_dr_rina_asakura",
                aiSearchDepth = 9,
                initialBoardSetup = new List<PuzzleBoardPlacement>
                {
                    new PuzzleBoardPlacement(1, 0, "sp_06_dr_rina_asakura", 1, 1),
                    new PuzzleBoardPlacement(0, 0, "cf_02_mech_knight", 1, 1),
                    new PuzzleBoardPlacement(2, 0, "cf_09_cyber_ninja", 1, 1),
                    new PuzzleBoardPlacement(1, 2, "sp_05_taro_fujimoto", 0, 0)
                },
                kaiHandCards = new List<string>
                {
                    "sp_01_kai_nakamura",
                    "sp_02_aiko_nakamura_echo",
                    "sp_03_mnemosyne_constellation_fox",
                    "sp_04_luna_cradle_guide"
                },
                winningTacticalLine = "1) Play sp_02_aiko_nakamura_echo at (0,1) to Chrono-Rewind Rina's CoreExtractionColumnLock; 2) Play sp_01_kai_nakamura at (1,1) with Budge(+1) (Up:9 + 2 Resonance = 11 > Rina's Down:10) to shatter the corporate extraction and unlock the Final Triad Choice.",
                rewardConfidencePoints = 2000,
                rewardUnlockedEchoFragment = "Epilogue Unlocked: A Living Puzzle (Legacy Memory Ethics Teacher + Encrypted Message from Aiko)"
            });

            return act;
        }
    }

    // =================================================================================================
    // 4. CRADLE OF ECHOES GENESIS & CARDCRAFT INTERNAL GENERATOR (`CardCraftAssetGeneratorSpec`)
    // =================================================================================================

    [Serializable]
    public class ShiftingPiecesColorPaletteSpec
    {
        public string paletteId;
        public string paletteName;
        public string backgroundHex;
        public string primaryTitleTextHex;
        public string secondaryTextHex;
        public string primaryAccentHex;
        public string secondaryAccentHex;
        public string minimalistSymbolDirection;
        public string wcagContrastRating;
    }

    [Serializable]
    public class CradlePersonaArchetypeDef
    {
        public int number;
        public CradlePersonaId personaId;
        public string name;
        public string symbolVisualMotif;
        public CradleElement element;
        public string role;
    }

    [Serializable]
    public class CardCraftGeneratedAssetContract
    {
        public string cardId;
        public string title;
        public string narrativeOrigin;
        // (a) CardDataSO / Indie Marc CardData
        public DirectionalStats directionalStats;
        public string indieMarcCardDataId;
        public int manaOrDeploymentCost;
        public string specialAbilityId;
        // (b) 12-Master Concept Art & Turnaround Sheet
        public string primaryArtistStyle;
        public string colorPaletteId;
        public string turnaroundSheetSpec;
        // (c) Watertight Hi3D.ai + TRELLIS 2.0 .glb/.q3gs 3D mesh asset
        public string glbFilePath;
        public string q3gsFilePath;
        public int vertexCount;
        public int triangleFaceCount;
        public int edgeCount;
        public int eulerCharacteristicVMinusEPlusF;
        public bool isWatertightClosedManifold;
        public string reaArtifactEvidenceId;
        public string reaArtifactManifestId;
    }

    /// <summary>
    /// Implements the tarot-inspired "Cradle of Echoes" Persona Genesis sequence (Studio PxG | Nocturna Universe,
    /// guided by LUNA in Toru Nakayama × Akihiko Yoshida cel-shaded style), the 3 official Shifting Pieces
    /// Amazon Cover Color Palettes, and the CardCraft Internal Card, Concept Art & 3D Mesh Generator contract.
    /// </summary>
    public static class CardCraftAssetGeneratorSpec
    {
        public const float FinalPersonaSelectionAlignmentCap = 0.95f;
        public const float RemainingQuestCardAlignmentPool = 0.05f;
        public const int PotentialQuestCardsPerPersona = 500000;
        public const float MeritPointsPerCompletedQuestCard = 0.05f;

        /// <summary>
        /// Returns the 3 canonical cover color palettes from `Shifting_Pieces_Cover_Color_Palettes.docx`.
        /// </summary>
        public static List<ShiftingPiecesColorPaletteSpec> GetCanonicalCoverPalettes()
        {
            return new List<ShiftingPiecesColorPaletteSpec>
            {
                new ShiftingPiecesColorPaletteSpec
                {
                    paletteId = "Palette_A_Monochrome_Red_Scarf",
                    paletteName = "Palette A — Monochrome + Red Scarf (High-Contrast, Literary-Tech)",
                    backgroundHex = "#0B0B0C",
                    primaryTitleTextHex = "#F2F2F2",
                    secondaryTextHex = "#C9C9C9",
                    primaryAccentHex = "#D12D3A",
                    secondaryAccentHex = "#7A8B99",
                    minimalistSymbolDirection = "Single puzzle piece with a tiny diagonal glitch cut; solid crimson fill #D12D3A on near-black #0B0B0C background.",
                    wcagContrastRating = "WCAG AAA (>= 7:1 contrast; #F2F2F2 on #0B0B0C)"
                },
                new ShiftingPiecesColorPaletteSpec
                {
                    paletteId = "Palette_B_Cyber_Blues_Neon_Violet",
                    paletteName = "Palette B — Cyber Blues + Neon Violet (Futuristic VR)",
                    backgroundHex = "#0A1020",
                    primaryTitleTextHex = "#EAF2FF",
                    secondaryTextHex = "#1B2338",
                    primaryAccentHex = "#2EE6D3",
                    secondaryAccentHex = "#8A5BFF",
                    minimalistSymbolDirection = "Thin-line VR halo ring (#2EE6D3 neon cyan) intersected by a square memory block with soft #8A5BFF violet outer glow.",
                    wcagContrastRating = "WCAG AAA (>= 7:1 contrast; #EAF2FF on #0A1020)"
                },
                new ShiftingPiecesColorPaletteSpec
                {
                    paletteId = "Palette_C_Ocean_And_Lantern",
                    paletteName = "Palette C — Ocean + Lantern (Melancholy / Hope)",
                    backgroundHex = "#0A2230",
                    primaryTitleTextHex = "#F8FAFB",
                    secondaryTextHex = "#93A7B4",
                    primaryAccentHex = "#FFB648",
                    secondaryAccentHex = "#2B6C7C",
                    minimalistSymbolDirection = "Minimalist 5-7 node Constellation Fox (#FFB648 warm amber nodes connected by #F8FAFB 80% opacity starlight lines over #0A2230 deep ocean).",
                    wcagContrastRating = "WCAG AAA (>= 7:1 contrast; #F8FAFB on #0A2230)"
                }
            };
        }

        /// <summary>
        /// Returns all 20 canonical Personas from `CardFront_Cradle_of_Echoes.docx`.
        /// </summary>
        public static List<CradlePersonaArchetypeDef> GetTwentyCradlePersonas()
        {
            return new List<CradlePersonaArchetypeDef>
            {
                new CradlePersonaArchetypeDef { number = 1,  personaId = CradlePersonaId.TheDreamer,    name = "The Dreamer",    symbolVisualMotif = "Book / Imagination",    element = CradleElement.Air,   role = "Creativity" },
                new CradlePersonaArchetypeDef { number = 2,  personaId = CradlePersonaId.TheMaster,     name = "The Master",     symbolVisualMotif = "Sword / Focus",         element = CradleElement.Fire,  role = "Mastery" },
                new CradlePersonaArchetypeDef { number = 3,  personaId = CradlePersonaId.TheGuardian,   name = "The Guardian",   symbolVisualMotif = "Shield / Light",        element = CradleElement.Earth, role = "Protection" },
                new CradlePersonaArchetypeDef { number = 4,  personaId = CradlePersonaId.TheSurvivor,   name = "The Survivor",   symbolVisualMotif = "Lantern / Endurance",   element = CradleElement.Earth, role = "Resilience" },
                new CradlePersonaArchetypeDef { number = 5,  personaId = CradlePersonaId.TheVisionary,  name = "The Visionary",  symbolVisualMotif = "Telescope / Stars",     element = CradleElement.Air,   role = "Foresight" },
                new CradlePersonaArchetypeDef { number = 6,  personaId = CradlePersonaId.TheInnovator,  name = "The Innovator",  symbolVisualMotif = "Tools / Workshop",      element = CradleElement.Fire,  role = "Invention" },
                new CradlePersonaArchetypeDef { number = 7,  personaId = CradlePersonaId.TheHealer,     name = "The Healer",     symbolVisualMotif = "Nature / Aura",         element = CradleElement.Water, role = "Restoration" },
                new CradlePersonaArchetypeDef { number = 8,  personaId = CradlePersonaId.TheStrategist, name = "The Strategist", symbolVisualMotif = "Chessboard / Plan",     element = CradleElement.Air,   role = "Wisdom" },
                new CradlePersonaArchetypeDef { number = 9,  personaId = CradlePersonaId.TheLeader,     name = "The Leader",     symbolVisualMotif = "Banner / Resolve",      element = CradleElement.Fire,  role = "Influence" },
                new CradlePersonaArchetypeDef { number = 10, personaId = CradlePersonaId.TheEmpath,     name = "The Empath",     symbolVisualMotif = "Flower / Connection",   element = CradleElement.Water, role = "Compassion" },
                new CradlePersonaArchetypeDef { number = 11, personaId = CradlePersonaId.TheSage,       name = "The Sage",       symbolVisualMotif = "Scroll / Reflection",   element = CradleElement.Earth, role = "Knowledge" },
                new CradlePersonaArchetypeDef { number = 12, personaId = CradlePersonaId.TheExplorer,   name = "The Explorer",   symbolVisualMotif = "Compass / Journey",     element = CradleElement.Air,   role = "Curiosity" },
                new CradlePersonaArchetypeDef { number = 13, personaId = CradlePersonaId.TheArtist,     name = "The Artist",     symbolVisualMotif = "Brush / Expression",    element = CradleElement.Fire,  role = "Passion" },
                new CradlePersonaArchetypeDef { number = 14, personaId = CradlePersonaId.TheScientist,  name = "The Scientist",  symbolVisualMotif = "Vials / Formula",       element = CradleElement.Water, role = "Logic" },
                new CradlePersonaArchetypeDef { number = 15, personaId = CradlePersonaId.TheRebel,      name = "The Rebel",      symbolVisualMotif = "Flame / Defiance",      element = CradleElement.Fire,  role = "Freedom" },
                new CradlePersonaArchetypeDef { number = 16, personaId = CradlePersonaId.TheMediator,   name = "The Mediator",   symbolVisualMotif = "Scales / Calm",         element = CradleElement.Water, role = "Balance" },
                new CradlePersonaArchetypeDef { number = 17, personaId = CradlePersonaId.ThePoet,       name = "The Poet",       symbolVisualMotif = "Quill / Emotion",       element = CradleElement.Air,   role = "Expression" },
                new CradlePersonaArchetypeDef { number = 18, personaId = CradlePersonaId.TheWarrior,    name = "The Warrior",    symbolVisualMotif = "Blade / Resolve",       element = CradleElement.Fire,  role = "Courage" },
                new CradlePersonaArchetypeDef { number = 19, personaId = CradlePersonaId.TheOracle,     name = "The Oracle",     symbolVisualMotif = "Mirror / Fate",         element = CradleElement.Water, role = "Intuition" },
                new CradlePersonaArchetypeDef { number = 20, personaId = CradlePersonaId.TheArchitect,  name = "The Architect",  symbolVisualMotif = "Blueprint / Structure", element = CradleElement.Earth, role = "Order" }
            };
        }

        /// <summary>
        /// Computes the official LUNA 10-card tarot selection weight distribution from `CardFront_Cradle_of_Echoes.docx`:
        /// - Cards 1-2: 10% total influence (0.05 each)
        /// - Cards 3-7: 60% total influence (0.12 each)
        /// - Cards 8-9: 25% total influence (0.125 each)
        /// - Card 10:   5% "Persona Seal" bonus -> 95% total alignment (0.95).
        /// Remaining 5% unlocks across 500,000 Quest Cards (0.05 Merit points per completed QC).
        /// </summary>
        public static float GetCradleCardStepWeight(int oneBasedCardIndex)
        {
            if (oneBasedCardIndex <= 2) return 0.05f;
            if (oneBasedCardIndex <= 7) return 0.12f;
            if (oneBasedCardIndex <= 9) return 0.125f;
            if (oneBasedCardIndex == 10) return 0.05f;
            return 0f;
        }

        public static float ComputeTotalAlignmentWithQuestCards(int completedQuestCards)
        {
            float qcContribution = Mathf.Clamp01((completedQuestCards * MeritPointsPerCompletedQuestCard) / 25000f) * RemainingQuestCardAlignmentPool;
            return Mathf.Clamp01(FinalPersonaSelectionAlignmentCap + qcContribution);
        }

        /// <summary>
        /// Builds the complete CardCraft Internal Generator contract for any Shifting Pieces character card,
        /// uniting (a) CardDataSO / Indie Marc CardData, (b) 12-Master Concept Art & Turnaround Sheet,
        /// and (c) Watertight Hi3D.ai + TRELLIS 2.0 .glb/.q3gs 3D mesh asset.
        /// </summary>
        public static List<CardCraftGeneratedAssetContract> BuildShiftingPiecesGeneratorContracts()
        {
            var contracts = new List<CardCraftGeneratedAssetContract>();
            foreach (var ch in ShiftingPiecesCharacterCatalog.GetProtagonistAndCastRoster())
            {
                string paletteId = ch.cardId == "sp_02_aiko_nakamura_echo" || ch.cardId == "sp_01_kai_nakamura"
                    ? "Palette_A_Monochrome_Red_Scarf"
                    : (ch.cardId == "sp_03_mnemosyne_constellation_fox" ? "Palette_C_Ocean_And_Lantern" : "Palette_B_Cyber_Blues_Neon_Violet");

                contracts.Add(new CardCraftGeneratedAssetContract
                {
                    cardId = ch.cardId,
                    title = ch.characterName,
                    narrativeOrigin = "Shifting Pieces × CardFront: Cradle of Echoes × CardCraft",
                    directionalStats = ch.directionalStats,
                    indieMarcCardDataId = "im_" + ch.cardId,
                    manaOrDeploymentCost = 3,
                    specialAbilityId = ch.shiftingPiecesAbility.ToString(),
                    primaryArtistStyle = "Toru Nakayama (Zero Vector Line) × Akihiko Yoshida (Painterly Crosshatch) × Kazuma Kaneko (Planar Shadow)",
                    colorPaletteId = paletteId,
                    turnaroundSheetSpec = $"4-View Orthographic Character Turnaround (Front/Side/Back/3-4) + Expression Range + Symbol Callout ({ch.primaryColorHex} / {ch.accentColorHex})",
                    glbFilePath = ch.glbAssetPath,
                    q3gsFilePath = ch.q3gsAssetPath,
                    vertexCount = 4034,
                    triangleFaceCount = 8064,
                    edgeCount = 12096,
                    eulerCharacteristicVMinusEPlusF = 2,
                    isWatertightClosedManifold = true,
                    reaArtifactEvidenceId = "ev_ca006fc20427ed15dbc240ff6cab53fa7043cf9685fde6499e71f12c8cd4d4e7",
                    reaArtifactManifestId = "agm_6b5ffb53a5a18cda0d687faa59e027f6eb71bd09f79e32f590c003e4eefd170a"
                });
            }
            return contracts;
        }
    }
}
