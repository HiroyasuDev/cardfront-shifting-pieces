using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Campaign
{
    public enum FactionId
    {
        ArcaneEnclave = 0,
        IronVanguardDirectorate = 1,
        CelestialOrder = 2,
        MidnightSyndicate = 3,
        VerdantConfluence = 4,
        OdysseyFleet = 5
    }

    [Serializable]
    public class FactionLoreDef
    {
        public FactionId id;
        public string name;
        public string motto;
        public string homeworldSector;
        public CardTheme primaryThemes;
        public List<string> signatureCardIds = new List<string>();
        public string loreOverview;
        public string tacticalDoctrine;
    }

    [Serializable]
    public class CampaignEncounterDef
    {
        public string encounterId;
        public string title;
        public string opponentCommander;
        public FactionId opponentFaction;
        public int aiSearchDepth;
        public bool isNighttimeArena;
        public string preBattleDialogue;
        public string victoryDialogue;
        public List<string> opponentDeckCardIds = new List<string>();
        public int rewardXp;
        public int rewardConfidencePoints;
        public string rewardBadge;
        public string rewardUnlockedCardId;
    }

    [Serializable]
    public class CampaignActDef
    {
        public int actNumber;
        public string actId;
        public string title;
        public string subtitle;
        public string narrativeSynopsis;
        public List<CampaignEncounterDef> encounters = new List<CampaignEncounterDef>();
    }

    [Serializable]
    public struct PuzzleBoardPlacement
    {
        public int x;
        public int y;
        public string cardId;
        public int ownerId;
        public int permanentStatBonus;

        public PuzzleBoardPlacement(int x, int y, string cardId, int ownerId, int permanentStatBonus = 0)
        {
            this.x = x;
            this.y = y;
            this.cardId = cardId;
            this.ownerId = ownerId;
            this.permanentStatBonus = permanentStatBonus;
        }
    }

    [Serializable]
    public struct PuzzleSolutionStep
    {
        public bool isSpecialAbilityActivation;
        public string handCardId;
        public int fromX;
        public int fromY;
        public int targetX;
        public int targetY;
        public string explanation;
    }

    /// <summary>
    /// Defines a 1-Turn Lethal 3x3 Tactical Board Puzzle where the player starts behind on the board
    /// and must execute the exact combination of Special Ability activation and/or Directional Placement
    /// to flip the board from losing to winning in a single turn.
    /// </summary>
    [Serializable]
    public class PuzzleStageDef
    {
        public string puzzleId;
        public string title;
        public string difficultyLabel;
        public bool isNighttime;
        public string tacticalBriefing;
        public string hintText;
        public List<PuzzleBoardPlacement> initialBoard = new List<PuzzleBoardPlacement>();
        public List<string> playerHandCardIds = new List<string>();
        public List<PuzzleSolutionStep> optimalSolutionSteps = new List<PuzzleSolutionStep>();
        public int rewardConfidencePoints;
        public string rewardBadge;
    }

    /// <summary>
    /// Complete PROJECT CF ("Card Front Tactics: Frontier Legends") 3-Act Story Campaign,
    /// Six Faction Lore Codex, and 5 Lethal 3x3 Tactical Board Puzzles.
    /// </summary>
    public static class SynapseStoryCampaign
    {
        public static List<FactionLoreDef> GetFactions()
        {
            return new List<FactionLoreDef>
            {
                new FactionLoreDef
                {
                    id = FactionId.ArcaneEnclave,
                    name = "Arcane Enclave",
                    motto = "Where Aether Bends, Geometry Obeys.",
                    homeworldSector = "Aethelgard Spire-Ring",
                    primaryThemes = CardTheme.Magic | CardTheme.Steampunk,
                    signatureCardIds = new List<string> { "cf_01_mystic_mage", "cf_07_clockwork_sorcerer", "cc_02_concept_art" },
                    loreOverview =
                        "Scholars of the high-altitude Spire-Ring who fuse leyline cryptography with brass chronometry. " +
                        "When the Frontier Rift opened, the Enclave bound unstable spatial anomalies into Guardian Frames " +
                        "capable of folding the 3x3 tactical grid.",
                    tacticalDoctrine =
                        "Repositioning and stat inversion. Uses Mystic Mage's Teleport to strike unguarded flanks and " +
                        "Clockwork Sorcerer's Temporal Rift to invert heavily armored enemy walls into fragile targets."
                },
                new FactionLoreDef
                {
                    id = FactionId.IronVanguardDirectorate,
                    name = "Iron Vanguard Directorate",
                    motto = "Momentum Is Armor. Impact Is Law.",
                    homeworldSector = "Vulcan Foundry Belt",
                    primaryThemes = CardTheme.Tech,
                    signatureCardIds = new List<string> { "cf_02_mech_knight", "cf_09_cyber_ninja", "cc_04_animatic" },
                    loreOverview =
                        "Forged in the orbital shipyards of the Vulcan Belt, the Directorate fields heavy mechanized " +
                        "calvalry alongside neural-linked cybernetic operatives. They view the Frontier Grid as an " +
                        "industrial siege engine where tempo dictates survival.",
                    tacticalDoctrine =
                        "Tempo cascades and adjacency stealth. Mech Knight's Charge grants a second consecutive placement " +
                        "on capture, while Cyber Ninja locks down corners with Techno Stealth immunity next to Tech allies."
                },
                new FactionLoreDef
                {
                    id = FactionId.CelestialOrder,
                    name = "Celestial Order",
                    motto = "Light Endures Beyond the Eclipse.",
                    homeworldSector = "Solstice Cathedral Station",
                    primaryThemes = CardTheme.Divine | CardTheme.Cosmic | CardTheme.Lunar,
                    signatureCardIds = new List<string> { "cf_03_celestial_guardian", "cf_10_lunar_oracle" },
                    loreOverview =
                        "Custodians of the ancient astral beacons that guide Frontier vessels through deep-space storms. " +
                        "Their Radiant Frames channel solar harmony and lunar tides, amplifying every allied formation " +
                        "that stands in orthogonal alignment.",
                    tacticalDoctrine =
                        "High-scaling defensive formations. Celestial Guardian's Healing Aura permanently fortifies " +
                        "neighbors each turn, while Lunar Oracle's Moonlight Blessing + Celestial Guidance grants massive +4 all-side swings."
                },
                new FactionLoreDef
                {
                    id = FactionId.MidnightSyndicate,
                    name = "Midnight Syndicate",
                    motto = "Unseen in the Dark; Inevitable at Dawn.",
                    homeworldSector = "Umbra Relay Undercity",
                    primaryThemes = CardTheme.Shadow | CardTheme.Stealth,
                    signatureCardIds = new List<string> { "cf_04_shadow_assassin", "cf_09_cyber_ninja" },
                    loreOverview =
                        "An intelligence collective operating within the shadow cones of hollowed asteroids. The Syndicate " +
                        "trades in encrypted telemetry and surgical strikes, neutralizing superior numbers through " +
                        "phase-cloaking and psychological misdirection.",
                    tacticalDoctrine =
                        "Capture denial and surgical corner control. Shadow Assassin's Vanish and Dark Ambush synergy " +
                        "create untouchable anchor points that deny opponent counter-captures."
                },
                new FactionLoreDef
                {
                    id = FactionId.VerdantConfluence,
                    name = "Verdant Confluence",
                    motto = "From Ash, the Canopy Rises Anew.",
                    homeworldSector = "Biosphere Ark Sylva-9",
                    primaryThemes = CardTheme.Nature | CardTheme.Fire,
                    signatureCardIds = new List<string> { "cf_05_elemental_sprite", "cf_08_phoenix_guardian" },
                    loreOverview =
                        "Terraformers and elemental symbiotes who seed living ecosystems across barren frontier worlds. " +
                        "Their Guardian Frames embody the cycle of wildfire and regrowth—turning defeat into immediate " +
                        "resurgence and stealing the strength of invading titans.",
                    tacticalDoctrine =
                        "Stat siphoning and recursive hand advantage. Elemental Sprite's Elemental Burst swaps base stats " +
                        "with captured juggernauts, while Phoenix Guardian's Rebirth returns it to hand upon capture."
                },
                new FactionLoreDef
                {
                    id = FactionId.OdysseyFleet,
                    name = "Odyssey Fleet",
                    motto = "No Horizon Beyond Our Reach.",
                    homeworldSector = "Hyperion Deep-Space Armada",
                    primaryThemes = CardTheme.Cosmic | CardTheme.Tech | CardTheme.Creative,
                    signatureCardIds = new List<string> { "cf_06_galactic_explorer", "cf_10_lunar_oracle", "cc_01_sketching", "cc_03_storyboard" },
                    loreOverview =
                        "Pioneers, cartographers, and CardCraft Tactician-Artisans who chart the outer rim. Equipped with " +
                        "micro-warp drives and adaptive holo-Blueprints, Odyssey captains outmaneuver static defenses " +
                        "through continuous every-turn mobility.",
                    tacticalDoctrine =
                        "Every-turn Warp Drive mobility and CardCraft evolution chains (Sketching -> Concept Art, " +
                        "Storyboard -> Animatic) that scale confidence points into unstoppable late-game boards."
                }
            };
        }

        public static List<CampaignActDef> GetCampaignActs()
        {
            return new List<CampaignActDef>
            {
                // =========================================================================
                // ACT I: FRONTIER AWAKENING
                // =========================================================================
                new CampaignActDef
                {
                    actNumber = 1,
                    actId = "act_01_frontier_awakening",
                    title = "ACT I: Frontier Awakening",
                    subtitle = "Sparks Across the Outer Grid",
                    narrativeSynopsis =
                        "Strange resonance surges across the outer rim beacons. As a newly commissioned Frontier Tactician, " +
                        "you must unite the scattered outposts of the Arcane Enclave and Verdant Confluence before rogue " +
                        "Iron Vanguard patrols lock down the sector.",
                    encounters = new List<CampaignEncounterDef>
                    {
                        new CampaignEncounterDef
                        {
                            encounterId = "act1_enc1_arcane_trial",
                            title = "1-1: Trial of the Spire-Ring",
                            opponentCommander = "Archivist Lyra",
                            opponentFaction = FactionId.ArcaneEnclave,
                            aiSearchDepth = 2,
                            isNighttimeArena = false,
                            preBattleDialogue = "Show me you understand directional alignment, Tactician. Watch my Mystic Mage's flank—or she will vanish behind your lines.",
                            victoryDialogue = "Impressive spatial awareness! The Arcane Enclave opens its archives to your squad.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_01_mystic_mage", "cc_01_sketching", "cc_02_concept_art",
                                "cf_05_elemental_sprite", "cc_03_storyboard", "cf_01_mystic_mage"
                            },
                            rewardXp = 150,
                            rewardConfidencePoints = 40,
                            rewardBadge = "Spire Initiate",
                            rewardUnlockedCardId = "cf_01_mystic_mage"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act1_enc2_verdant_canopy",
                            title = "1-2: Wildfire in Biosphere Sylva-9",
                            opponentCommander = "Warden Kaelen",
                            opponentFaction = FactionId.VerdantConfluence,
                            aiSearchDepth = 2,
                            isNighttimeArena = false,
                            preBattleDialogue = "Strike my Phoenix Guardian down if you dare—the Eternal Flame only rises stronger from your hand!",
                            victoryDialogue = "You tempered the flame without breaking the canopy. Sylva-9 stands with you.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_05_elemental_sprite", "cf_08_phoenix_guardian", "cf_01_mystic_mage",
                                "cf_05_elemental_sprite", "cf_08_phoenix_guardian", "cc_02_concept_art"
                            },
                            rewardXp = 200,
                            rewardConfidencePoints = 60,
                            rewardBadge = "Wildfire Tamer",
                            rewardUnlockedCardId = "cf_08_phoenix_guardian"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act1_enc3_iron_blockade",
                            title = "1-3: Siege of Vulcan Crossing",
                            opponentCommander = "Centurion Vane",
                            opponentFaction = FactionId.IronVanguardDirectorate,
                            aiSearchDepth = 3,
                            isNighttimeArena = false,
                            preBattleDialogue = "Halt! My Mech Knights need only a single capture to trigger a Charge cascade across your entire grid.",
                            victoryDialogue = "Impossible... our vanguard armor was breached in a single counter-formation!",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_02_mech_knight", "cf_06_galactic_explorer", "cf_02_mech_knight",
                                "cf_09_cyber_ninja", "cc_04_animatic", "cf_03_celestial_guardian"
                            },
                            rewardXp = 300,
                            rewardConfidencePoints = 100,
                            rewardBadge = "Breaker of Chains",
                            rewardUnlockedCardId = "cf_02_mech_knight"
                        }
                    }
                },

                // =========================================================================
                // ACT II: THE CLOCKWORK & CYBER SCHISM
                // =========================================================================
                new CampaignActDef
                {
                    actNumber = 2,
                    actId = "act_02_clockwork_cyber_schism",
                    title = "ACT II: The Clockwork & Cyber Schism",
                    subtitle = "Chrono-Gears Against Digital Shadows",
                    narrativeSynopsis =
                        "A covert conflict erupts between the brass chronomancers of the Arcane Enclave and the neural-stealth " +
                        "operatives of the Midnight Syndicate. In the neon-lit corridors of Umbra Relay, every card's stats " +
                        "can be reversed in an instant, and Tech-linked assassins cannot be captured by conventional force.",
                    encounters = new List<CampaignEncounterDef>
                    {
                        new CampaignEncounterDef
                        {
                            encounterId = "act2_enc1_silent_circuit",
                            title = "2-1: Ambush in the Umbra Undercity",
                            opponentCommander = "Cipher-Zero",
                            opponentFaction = FactionId.MidnightSyndicate,
                            aiSearchDepth = 3,
                            isNighttimeArena = true,
                            preBattleDialogue = "My Cyber Ninja stands beside a Tech node—Techno Stealth renders it untouchable. Find another angle, if you can.",
                            victoryDialogue = "You targeted the Tech relay first to sever my stealth link... calculated like a true operative.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_04_shadow_assassin", "cf_09_cyber_ninja", "cf_02_mech_knight",
                                "cf_04_shadow_assassin", "cf_09_cyber_ninja", "cf_06_galactic_explorer"
                            },
                            rewardXp = 350,
                            rewardConfidencePoints = 120,
                            rewardBadge = "Shadow Piercer",
                            rewardUnlockedCardId = "cf_09_cyber_ninja"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act2_enc2_temporal_paradox",
                            title = "2-2: The Pendulum Vault",
                            opponentCommander = "Chronomancer Valerius",
                            opponentFaction = FactionId.ArcaneEnclave,
                            aiSearchDepth = 3,
                            isNighttimeArena = false,
                            preBattleDialogue = "Your strongest walls are your greatest weakness once my Clockwork Sorcerer opens a Temporal Rift!",
                            victoryDialogue = "The gears halt... You anticipated the polarity inversion before the pendulum struck.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_07_clockwork_sorcerer", "cf_01_mystic_mage", "cf_07_clockwork_sorcerer",
                                "cf_03_celestial_guardian", "cc_02_concept_art", "cc_04_animatic"
                            },
                            rewardXp = 400,
                            rewardConfidencePoints = 150,
                            rewardBadge = "Chrono Sovereign",
                            rewardUnlockedCardId = "cf_07_clockwork_sorcerer"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act2_enc3_hyperion_warp",
                            title = "2-3: Warp-Gate Interdiction",
                            opponentCommander = "Commodore Astraea",
                            opponentFaction = FactionId.OdysseyFleet,
                            aiSearchDepth = 4,
                            isNighttimeArena = true,
                            preBattleDialogue = "Static formations mean nothing to the Odyssey Fleet. Our Galactic Explorers warp to open coordinates every turn!",
                            victoryDialogue = "All warp vectors boxed in! You command the 3x3 grid like a grand fleet admiral.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_06_galactic_explorer", "cf_03_celestial_guardian", "cf_06_galactic_explorer",
                                "cf_02_mech_knight", "cf_10_lunar_oracle", "cc_04_animatic"
                            },
                            rewardXp = 500,
                            rewardConfidencePoints = 180,
                            rewardBadge = "Hyperion Navigator",
                            rewardUnlockedCardId = "cf_06_galactic_explorer"
                        }
                    }
                },

                // =========================================================================
                // ACT III: ECLIPSE OF THE LUNAR ORACLE
                // =========================================================================
                new CampaignActDef
                {
                    actNumber = 3,
                    actId = "act_03_eclipse_lunar_oracle",
                    title = "ACT III: Eclipse of the Lunar Oracle",
                    subtitle = "Convergence at Solstice Cathedral",
                    narrativeSynopsis =
                        "Under a perpetual celestial eclipse, High Seraph Selene and the Celestial Order seek to lock the " +
                        "Frontier Grid in eternal stasis. Only by combining all ten Guardian Frames and evolved CardCraft " +
                        "masterworks can you break the Moonlight convergence and restore balance to the Frontier.",
                    encounters = new List<CampaignEncounterDef>
                    {
                        new CampaignEncounterDef
                        {
                            encounterId = "act3_enc1_sanctuary_wall",
                            title = "3-1: Bastion of Holy Harmony",
                            opponentCommander = "Paladin Auron",
                            opponentFaction = FactionId.CelestialOrder,
                            aiSearchDepth = 4,
                            isNighttimeArena = true,
                            preBattleDialogue = "Every turn my Celestial Guardians stand together, Holy Harmony and Healing Aura raise our shields beyond reach!",
                            victoryDialogue = "Even our sanctified phalanx could not withstand your elemental and temporal combo.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_03_celestial_guardian", "cf_10_lunar_oracle", "cf_03_celestial_guardian",
                                "cf_06_galactic_explorer", "cf_08_phoenix_guardian", "cf_01_mystic_mage"
                            },
                            rewardXp = 600,
                            rewardConfidencePoints = 220,
                            rewardBadge = "Sanctuary Vanguard",
                            rewardUnlockedCardId = "cf_03_celestial_guardian"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act3_enc2_eclipse_nexus",
                            title = "3-2: Shadows Beneath the Silver Moon",
                            opponentCommander = "Grandmaster Noctis",
                            opponentFaction = FactionId.MidnightSyndicate,
                            aiSearchDepth = 4,
                            isNighttimeArena = true,
                            preBattleDialogue = "In the eclipse, Stealth and Lunar resonance merge. Try capturing a board that phases out of reality!",
                            victoryDialogue = "The eclipse clears... You have mastered every synergy on the Frontier.",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_04_shadow_assassin", "cf_09_cyber_ninja", "cf_10_lunar_oracle",
                                "cf_07_clockwork_sorcerer", "cf_02_mech_knight", "cf_05_elemental_sprite"
                            },
                            rewardXp = 750,
                            rewardConfidencePoints = 260,
                            rewardBadge = "Eclipse Conqueror",
                            rewardUnlockedCardId = "cf_04_shadow_assassin"
                        },
                        new CampaignEncounterDef
                        {
                            encounterId = "act3_enc3_lunar_oracle_finale",
                            title = "3-3: Grand Finale — The Lunar Oracle's Convergence",
                            opponentCommander = "High Oracle Selene",
                            opponentFaction = FactionId.CelestialOrder,
                            aiSearchDepth = 5,
                            isNighttimeArena = true,
                            preBattleDialogue = "Behold the Celestial Insight! Under the eternal night, my Lunar Oracles command +4 across all directions. Show me the pinnacle of Card Front Tactics!",
                            victoryDialogue = "Magnificent... The ten Guardian Frames resonate in unison. You are truly a Legend of the Frontier!",
                            opponentDeckCardIds = new List<string>
                            {
                                "cf_10_lunar_oracle", "cf_03_celestial_guardian", "cf_10_lunar_oracle",
                                "cf_06_galactic_explorer", "cf_07_clockwork_sorcerer", "cf_08_phoenix_guardian"
                            },
                            rewardXp = 1200,
                            rewardConfidencePoints = 500,
                            rewardBadge = "Frontier Legend (Grand Champion)",
                            rewardUnlockedCardId = "cf_10_lunar_oracle"
                        }
                    }
                }
            };
        }

        /// <summary>
        /// Returns 5 deterministic 1-Turn Lethal 3x3 Tactical Board Puzzles.
        /// Every puzzle starts with Player 0 losing on the board and requires an exact 1-turn sequence
        /// (Special Ability activation + Card Placement, or Charge double-placement) to flip the board to a win.
        /// </summary>
        public static List<PuzzleStageDef> GetTacticalPuzzles()
        {
            return new List<PuzzleStageDef>
            {
                // =========================================================================
                // PUZZLE 1: CLOCKWORK TEMPORAL INVERSION
                // =========================================================================
                new PuzzleStageDef
                {
                    puzzleId = "puzzle_01_temporal_inversion",
                    title = "Puzzle I: Pendulum of Reversal",
                    difficultyLabel = "Tactician ★☆☆",
                    isNighttime = false,
                    tacticalBriefing =
                        "You trail 1-4 on the 3x3 grid. Your Clockwork Sorcerer sits at center (1,1) surrounded by " +
                        "three heavily fortified enemy cards whose inward-facing sides are 8 and 9, but whose outward-facing " +
                        "sides are weak. Activate Temporal Rift first, then place Mystic Mage to flip the board!",
                    hintText = "Activate Clockwork Sorcerer (1,1) to reverse adjacent enemy stats (Up<->Down, Left<->Right), then place Mystic Mage at (0,2).",
                    initialBoard = new List<PuzzleBoardPlacement>
                    {
                        new PuzzleBoardPlacement(1, 1, "cf_07_clockwork_sorcerer", 0), // Player's Clockwork Sorcerer at center
                        new PuzzleBoardPlacement(0, 1, "cf_09_cyber_ninja", 1),        // Enemy at (0,1): base U:6, D:5 -> reversed U becomes 5
                        new PuzzleBoardPlacement(1, 2, "cf_08_phoenix_guardian", 1),   // Enemy at (1,2): base L:6, R:4 -> reversed L becomes 4
                        new PuzzleBoardPlacement(2, 1, "cf_04_shadow_assassin", 1),    // Enemy at (2,1)
                        new PuzzleBoardPlacement(1, 0, "cc_01_sketching", 1)           // Enemy at (1,0)
                    },
                    playerHandCardIds = new List<string> { "cf_01_mystic_mage" },
                    optimalSolutionSteps = new List<PuzzleSolutionStep>
                    {
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = true,
                            fromX = 1,
                            fromY = 1,
                            targetX = -1,
                            targetY = -1,
                            explanation = "Activate Clockwork Sorcerer's Temporal Rift at (1,1) to reverse the directional stats of (0,1), (1,2), (2,1), and (1,0)."
                        },
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cf_01_mystic_mage",
                            targetX = 0,
                            targetY = 2,
                            explanation = "Place Mystic Mage at (0,2): Down 7 beats reversed Cyber Ninja (U:5) at (0,1) and Right 6 beats reversed Phoenix Guardian (L:4) at (1,2), flipping 1-4 into a 4-2 win!"
                        }
                    },
                    rewardConfidencePoints = 100,
                    rewardBadge = "Temporal Tactician"
                },

                // =========================================================================
                // PUZZLE 2: MYSTIC TELEPORT + ARCANE SYNERGY DOUBLE CAPTURE
                // =========================================================================
                new PuzzleStageDef
                {
                    puzzleId = "puzzle_02_arcane_teleport",
                    title = "Puzzle II: Blink Across the Leyline",
                    difficultyLabel = "Commander ★★☆",
                    isNighttime = false,
                    tacticalBriefing =
                        "You trail 1-4. Your Mystic Mage is pinned in the bottom-left corner (0,0). " +
                        "Use Mystic Mage's once-per-game Teleport to jump into the top-right pocket (1,2) to capture two enemies, " +
                        "then deploy Concept Art from hand at (1,1) to trigger Arcane Power (+2 all sides) and capture two more!",
                    hintText = "Teleport Mystic Mage from (0,0) to (1,2) first, then play Concept Art from your hand into the center (1,1).",
                    initialBoard = new List<PuzzleBoardPlacement>
                    {
                        new PuzzleBoardPlacement(0, 0, "cf_01_mystic_mage", 0),      // Player Mystic Mage (U:5, D:7, L:3, R:6)
                        new PuzzleBoardPlacement(0, 2, "cf_05_elemental_sprite", 1), // Enemy at (0,2)
                        new PuzzleBoardPlacement(2, 2, "cc_03_storyboard", 1),       // Enemy at (2,2) (L:5 -> beaten by Mystic Mage R:6!)
                        new PuzzleBoardPlacement(0, 1, "cc_01_sketching", 1),        // Enemy at (0,1) (R:5, Creative -> beaten by Concept Art L:8+2=10!)
                        new PuzzleBoardPlacement(2, 1, "cf_04_shadow_assassin", 1)   // Enemy at (2,1) (L:8 -> beaten by Concept Art R:7+2=9!)
                    },
                    playerHandCardIds = new List<string> { "cc_02_concept_art" },
                    optimalSolutionSteps = new List<PuzzleSolutionStep>
                    {
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = true,
                            fromX = 0,
                            fromY = 0,
                            targetX = 1,
                            targetY = 2,
                            explanation = "Teleport Mystic Mage from (0,0) to (1,2), capturing enemy Sketching at (0,2) or setting up Magic synergy."
                        },
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cc_02_concept_art",
                            targetX = 1,
                            targetY = 1,
                            explanation = "Place Concept Art (Magic/Creative) at (1,1) adjacent to Mystic Mage, activating synergy to capture (0,1) and (2,1)!"
                        }
                    },
                    rewardConfidencePoints = 125,
                    rewardBadge = "Leyline Blink Master"
                },

                // =========================================================================
                // PUZZLE 3: MECH KNIGHT CHARGE BLITZ
                // =========================================================================
                new PuzzleStageDef
                {
                    puzzleId = "puzzle_03_mech_charge_blitz",
                    title = "Puzzle III: Iron Vanguard Blitzkrieg",
                    difficultyLabel = "Commander ★★☆",
                    isNighttime = false,
                    tacticalBriefing =
                        "You have 0 cards on the board against 4 enemy cards! Fortunately, you hold Mech Knight and Cyber Ninja. " +
                        "Deploy Mech Knight to capture an enemy and trigger Charge (an immediate bonus placement in the same turn), " +
                        "then deploy Cyber Ninja adjacent to Mech Knight for Technological Alliance!",
                    hintText = "Place Mech Knight at (1,0) to capture (1,1) and (0,0) and trigger Charge, then immediately play Cyber Ninja at (2,1).",
                    initialBoard = new List<PuzzleBoardPlacement>
                    {
                        new PuzzleBoardPlacement(0, 0, "cc_01_sketching", 1),        // Enemy at (0,0): R:5 (beaten by Mech Knight L:6)
                        new PuzzleBoardPlacement(1, 1, "cc_03_storyboard", 1),       // Enemy at (1,1): D:6 (beaten by Mech Knight U:8)
                        new PuzzleBoardPlacement(2, 0, "cf_05_elemental_sprite", 1), // Enemy at (2,0): U:3 (beaten by Cyber Ninja D:5)
                        new PuzzleBoardPlacement(2, 2, "cf_01_mystic_mage", 1)       // Enemy at (2,2): D:7
                    },
                    playerHandCardIds = new List<string> { "cf_02_mech_knight", "cf_09_cyber_ninja" },
                    optimalSolutionSteps = new List<PuzzleSolutionStep>
                    {
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cf_02_mech_knight",
                            targetX = 1,
                            targetY = 0,
                            explanation = "Place Mech Knight at (1,0): Up 8 beats Storyboard (D:6) at (1,1) and Left 6 beats Sketching (R:5) at (0,0), triggering Charge!"
                        },
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cf_09_cyber_ninja",
                            targetX = 2,
                            targetY = 1,
                            explanation = "Use Mech Knight's bonus Charge move to place Cyber Ninja at (2,1), capturing Elemental Sprite at (2,0) (D:5 > U:3) for a 5-1 victory!"
                        }
                    },
                    rewardConfidencePoints = 150,
                    rewardBadge = "Vanguard Blitz Tactician"
                },

                // =========================================================================
                // PUZZLE 4: GALACTIC WARP DRIVE + TECHNO STEALTH BREAKER
                // =========================================================================
                new PuzzleStageDef
                {
                    puzzleId = "puzzle_04_warp_stealth_breaker",
                    title = "Puzzle IV: Severing the Silent Circuit",
                    difficultyLabel = "Vanguard ★★★",
                    isNighttime = false,
                    tacticalBriefing =
                        "Enemy Cyber Ninja at (1,1) is immune to capture via Techno Stealth because enemy Mech Knight sits at (0,1). " +
                        "First use your Galactic Explorer's Warp Drive to jump to (0,2) and capture the Mech Knight at (0,1)—turning " +
                        "it friendly and breaking enemy threat lines—then place Celestial Guardian at (1,0) to capture the center!",
                    hintText = "Warp Galactic Explorer from (2,0) to (0,2) to capture Mech Knight at (0,1), then play Celestial Guardian at (1,2).",
                    initialBoard = new List<PuzzleBoardPlacement>
                    {
                        new PuzzleBoardPlacement(2, 0, "cf_06_galactic_explorer", 0), // Player Galactic Explorer (U:7, D:6, L:5, R:8)
                        new PuzzleBoardPlacement(0, 1, "cf_05_elemental_sprite", 1),  // Enemy at (0,1) (U:3, R:9)
                        new PuzzleBoardPlacement(1, 2, "cc_01_sketching", 1),         // Enemy at (1,2) (L:6, D:5)
                        new PuzzleBoardPlacement(2, 2, "cc_03_storyboard", 1),        // Enemy at (2,2) (L:5)
                        new PuzzleBoardPlacement(1, 0, "cf_04_shadow_assassin", 1)    // Enemy at (1,0) (U:7)
                    },
                    playerHandCardIds = new List<string> { "cf_03_celestial_guardian" },
                    optimalSolutionSteps = new List<PuzzleSolutionStep>
                    {
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = true,
                            fromX = 2,
                            fromY = 0,
                            targetX = 0,
                            targetY = 2,
                            explanation = "Activate Galactic Explorer's Warp Drive from (2,0) to (0,2): Down 6 beats (0,1) Up 3 and Right 8 beats (1,2) Left 6!"
                        },
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cf_03_celestial_guardian",
                            targetX = 1,
                            targetY = 1,
                            explanation = "Place Celestial Guardian at (1,1): Down 9 beats Shadow Assassin (1,0) Up 7, flipping the board to 5-1!"
                        }
                    },
                    rewardConfidencePoints = 175,
                    rewardBadge = "Warp-Vector Strategist"
                },

                // =========================================================================
                // PUZZLE 5: ECLIPSE CONVERGENCE (LUNAR ORACLE +4 OMNI-SWEEP)
                // =========================================================================
                new PuzzleStageDef
                {
                    puzzleId = "puzzle_05_lunar_eclipse_sweep",
                    title = "Puzzle V: Convergence of the Silver Moon",
                    difficultyLabel = "Grandmaster ★★★★",
                    isNighttime = true,
                    tacticalBriefing =
                        "Night falls over the Solstice Cathedral (isNighttime = true). You trail 1-4 against an elite formation. " +
                        "Your Mystic Mage waits at (0,0) and you hold Lunar Oracle in hand. Teleport Mystic Mage to (0,2) to " +
                        "capture (0,1), then deploy Lunar Oracle at (1,1) next to Cosmic ally Galactic Explorer to unleash " +
                        "Celestial Guidance (+3) + Moonlight Blessing (+1) = +4 to ALL sides (11/10/8/13) and sweep the board!",
                    hintText = "Teleport Mystic Mage from (0,0) to (0,2), then place Lunar Oracle at (1,1) for a +4 all-sides omni-capture.",
                    initialBoard = new List<PuzzleBoardPlacement>
                    {
                        new PuzzleBoardPlacement(0, 0, "cf_01_mystic_mage", 0),       // Player Mystic Mage (D:7)
                        new PuzzleBoardPlacement(1, 2, "cf_06_galactic_explorer", 1), // Enemy Cosmic card at (1,2) (D:6, L:5)
                        new PuzzleBoardPlacement(0, 1, "cc_01_sketching", 1),         // Enemy at (0,1) (U:4, R:5)
                        new PuzzleBoardPlacement(2, 1, "cf_03_celestial_guardian", 1),// Enemy at (2,1) (L:4 +3 syn = 7)
                        new PuzzleBoardPlacement(1, 0, "cf_02_mech_knight", 1)        // Enemy at (1,0) (U:8)
                    },
                    playerHandCardIds = new List<string> { "cf_10_lunar_oracle" },
                    optimalSolutionSteps = new List<PuzzleSolutionStep>
                    {
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = true,
                            fromX = 0,
                            fromY = 0,
                            targetX = 0,
                            targetY = 2,
                            explanation = "Teleport Mystic Mage from (0,0) to (0,2): Down 7 captures Sketching at (0,1) (U:4) and Right 6 captures Galactic Explorer at (1,2) (L:5)!"
                        },
                        new PuzzleSolutionStep
                        {
                            isSpecialAbilityActivation = false,
                            handCardId = "cf_10_lunar_oracle",
                            targetX = 1,
                            targetY = 1,
                            explanation = "Place Lunar Oracle at (1,1) adjacent to Cosmic Galactic Explorer (1,2) at night: stats surge to (11,10,8,13), capturing Mech Knight (1,0) and Celestial Guardian (2,1) for a 6-0 clean sweep!"
                        }
                    },
                    rewardConfidencePoints = 250,
                    rewardBadge = "Oracle of the Eclipse"
                }
            };
        }

        /// <summary>
        /// Builds a live <see cref="TcgGameLogic"/> instance from a <see cref="PuzzleStageDef"/>.
        /// </summary>
        public static TcgGameLogic InstantiatePuzzleBoard(PuzzleStageDef puzzle, Dictionary<string, CardDataSO> catalogById = null)
        {
            if (catalogById == null)
            {
                catalogById = new Dictionary<string, CardDataSO>();
                foreach (var c in ProjectCfCardCatalog.CreateDefaultRoster())
                {
                    catalogById[c.id] = c;
                }
            }

            var game = new TcgGameLogic(1337, puzzle.isNighttime)
            {
                activePlayerId = 0,
                turnNumber = 1,
                phase = TurnPhase.Main
            };

            int uidCounter = 1;
            foreach (var cell in puzzle.initialBoard)
            {
                if (!catalogById.TryGetValue(cell.cardId, out var so)) continue;
                var rc = RuntimeCard.FromCardData(so, cell.ownerId, $"puz_board_{uidCounter++}_{so.id}");
                rc.currentZone = ZoneType.Board;
                rc.permanentStatBonus = cell.permanentStatBonus;
                if (rc.specialAbility == SpecialAbilityType.Rebirth && cell.ownerId == 1)
                {
                    rc.oncePerGameAbilityUsed = true;
                }
                game.grid[cell.x, cell.y].occupant = rc;
            }

            foreach (var handCardId in puzzle.playerHandCardIds)
            {
                if (!catalogById.TryGetValue(handCardId, out var so)) continue;
                var rc = RuntimeCard.FromCardData(so, 0, $"puz_hand_{uidCounter++}_{so.id}");
                rc.currentZone = ZoneType.Hand;
                game.players[0].hand.Add(rc);
            }

            return game;
        }

        /// <summary>
        /// Executes the optimal solution steps of a <see cref="PuzzleStageDef"/> on a fresh
        /// <see cref="TcgGameLogic"/> board and verifies that Player 0 starts behind and finishes winning.
        /// </summary>
        public static bool ExecuteAndVerifyPuzzleSolution(
            PuzzleStageDef puzzle,
            out int initialPlayerCards,
            out int initialEnemyCards,
            out int finalPlayerCards,
            out int finalEnemyCards,
            out string logSummary)
        {
            var game = InstantiatePuzzleBoard(puzzle);
            initialPlayerCards = game.CountControlledCards(0);
            initialEnemyCards = game.CountControlledCards(1);

            bool startedBehind = initialPlayerCards < initialEnemyCards;
            foreach (var step in puzzle.optimalSolutionSteps)
            {
                if (step.isSpecialAbilityActivation)
                {
                    bool ok = game.ActivateSpecialAbility(0, step.fromX, step.fromY, step.targetX, step.targetY);
                    if (!ok)
                    {
                        finalPlayerCards = game.CountControlledCards(0);
                        finalEnemyCards = game.CountControlledCards(1);
                        logSummary = $"[{puzzle.puzzleId}] Special ability failed at ({step.fromX},{step.fromY}) -> ({step.targetX},{step.targetY}).";
                        return false;
                    }
                }
                else
                {
                    var cardInHand = game.players[0].hand.Find(c => c.cardId == step.handCardId);
                    if (cardInHand == null)
                    {
                        finalPlayerCards = game.CountControlledCards(0);
                        finalEnemyCards = game.CountControlledCards(1);
                        logSummary = $"[{puzzle.puzzleId}] Card '{step.handCardId}' not found in player hand.";
                        return false;
                    }
                    bool ok = game.PlaceCard(0, cardInHand.uid, step.targetX, step.targetY, out _);
                    if (!ok)
                    {
                        finalPlayerCards = game.CountControlledCards(0);
                        finalEnemyCards = game.CountControlledCards(1);
                        logSummary = $"[{puzzle.puzzleId}] PlaceCard failed for '{step.handCardId}' at ({step.targetX},{step.targetY}).";
                        return false;
                    }
                }
            }

            finalPlayerCards = game.CountControlledCards(0);
            finalEnemyCards = game.CountControlledCards(1);
            bool flippedToWin = startedBehind && (finalPlayerCards > finalEnemyCards);
            logSummary = $"[{puzzle.puzzleId}] {puzzle.title}: {initialPlayerCards}-{initialEnemyCards} -> {finalPlayerCards}-{finalEnemyCards} (Solved={flippedToWin})";
            return flippedToWin;
        }
    }
}
