using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    public enum SetOneFactionType
    {
        AetherTech = 0,
        ChronoArcana = 1,
        SolarisDivine = 2,
        UmbraStealth = 3,
        CardCraftStudio = 4
    }

    public enum SetOneRarityType
    {
        Common = 0,
        Rare = 1,
        Epic = 2,
        Legendary = 3
    }

    public enum MgaCardActionMode
    {
        Effect = 0,
        Move = 1,
        Equip = 2,
        Link = 3
    }

    [Serializable]
    public struct SetOneDirectionalStats
    {
        public int up;
        public int right;
        public int down;
        public int left;

        public SetOneDirectionalStats(int up, int right, int down, int left)
        {
            this.up = Mathf.Clamp(up, 1, 10);
            this.right = Mathf.Clamp(right, 1, 10);
            this.down = Mathf.Clamp(down, 1, 10);
            this.left = Mathf.Clamp(left, 1, 10);
        }

        public int Total => up + right + down + left;
    }

    [Serializable]
    public class SetOneCardDefinition
    {
        public string cardId;
        public string name;
        public string faction;
        public string factionShort;
        public SetOneFactionType factionType;
        public SetOneRarityType rarity;
        public SetOneDirectionalStats stats;
        public int mgaCost;
        public string[] mgaModes = new string[] { "Effect", "Move", "Equip", "Link" };
        public string abilityId;
        public string abilityDesc;
        public int staccsHeightBias;
        public string hi3dModelId;
        public string evolvesToCardId;

        public SetOneCardDefinition(
            string cardId,
            string name,
            string faction,
            string factionShort,
            SetOneFactionType factionType,
            SetOneRarityType rarity,
            int up,
            int right,
            int down,
            int left,
            int mgaCost,
            string abilityId,
            string abilityDesc,
            int staccsHeightBias,
            string hi3dModelId,
            string evolvesToCardId = "")
        {
            this.cardId = cardId;
            this.name = name;
            this.faction = faction;
            this.factionShort = factionShort;
            this.factionType = factionType;
            this.rarity = rarity;
            this.stats = new SetOneDirectionalStats(up, right, down, left);
            this.mgaCost = Mathf.Clamp(mgaCost, 4, 20);
            this.abilityId = abilityId;
            this.abilityDesc = abilityDesc;
            this.staccsHeightBias = Mathf.Clamp(staccsHeightBias, 1, 3);
            this.hi3dModelId = hi3dModelId;
            this.evolvesToCardId = evolvesToCardId ?? string.Empty;
        }
    }

    [Serializable]
    public class TacticalCampaignStageDefinition
    {
        public int stageNumber;
        public int actNumber;
        public int stageInAct;
        public string stageId;
        public string title;
        public string biome;
        public string factionFocus;
        public string enemyCommanderId;
        public string coPowerName;
        public string superCoPowerName;
        public string fftaJudgeLawId;
        public string fftaForbiddenAction;
        public string fftaRecommendedAction;
        public int initialPowerGridBars;
        public int defaultTerrainDefenseStars;
        public int maxMgaCostBudget;
        public Vector2Int extractionTile;
        public string[] enemyDeckIds;

        public TacticalCampaignStageDefinition(
            int stageNumber,
            int actNumber,
            int stageInAct,
            string stageId,
            string title,
            string biome,
            string factionFocus,
            string enemyCommanderId,
            string coPowerName,
            string superCoPowerName,
            string fftaJudgeLawId,
            string fftaForbiddenAction,
            string fftaRecommendedAction,
            int initialPowerGridBars,
            int defaultTerrainDefenseStars,
            int maxMgaCostBudget,
            Vector2Int extractionTile,
            string[] enemyDeckIds)
        {
            this.stageNumber = stageNumber;
            this.actNumber = actNumber;
            this.stageInAct = stageInAct;
            this.stageId = stageId;
            this.title = title;
            this.biome = biome;
            this.factionFocus = factionFocus;
            this.enemyCommanderId = enemyCommanderId;
            this.coPowerName = coPowerName;
            this.superCoPowerName = superCoPowerName;
            this.fftaJudgeLawId = fftaJudgeLawId;
            this.fftaForbiddenAction = fftaForbiddenAction;
            this.fftaRecommendedAction = fftaRecommendedAction;
            this.initialPowerGridBars = initialPowerGridBars;
            this.defaultTerrainDefenseStars = defaultTerrainDefenseStars;
            this.maxMgaCostBudget = maxMgaCostBudget;
            this.extractionTile = extractionTile;
            this.enemyDeckIds = enemyDeckIds;
        }
    }

    [Serializable]
    public class CampaignPilotProgressionState
    {
        public string pilotId = "pilot_sovereign_01";
        public string activeCommanderId = "co_max_vanguard";
        public int highestUnlockedStage = 1;
        public int totalSRanksEarned = 0;
        public int cumulativePowerGridSaved = 0;
        public int judgePointsBank = 3;
        public int confidencePointsBank = 50;
        public List<string> clearedStageIds = new List<string>();
        public List<string> unlockedCardIds = new List<string>();
        public ulong lastSaveFnv1a64Hash = 0UL;
    }

    /// <summary>
    /// Clean-room Unity Runtime for the 60-Card Set 1 Expansion across 5 Factions
    /// and the 15-Stage Tactical Campaign (Into the Breach + Advance Wars + FFTA + Metal Gear Acid).
    /// </summary>
    public class SynapseSetOneCampaignRuntime : MonoBehaviour
    {
        public const int TotalSetOneCards = 60;
        public const int CardsPerFaction = 12;
        public const int TotalCampaignActs = 5;
        public const int StagesPerAct = 3;
        public const int TotalCampaignStages = 15;

        [SerializeField] private CampaignPilotProgressionState progressionState = new CampaignPilotProgressionState();

        private readonly List<SetOneCardDefinition> _roster60 = new List<SetOneCardDefinition>(TotalSetOneCards);
        private readonly Dictionary<string, SetOneCardDefinition> _cardsById = new Dictionary<string, SetOneCardDefinition>();
        private readonly List<TacticalCampaignStageDefinition> _stages15 = new List<TacticalCampaignStageDefinition>(TotalCampaignStages);
        private readonly Dictionary<string, TacticalCampaignStageDefinition> _stagesById = new Dictionary<string, TacticalCampaignStageDefinition>();

        public IReadOnlyList<SetOneCardDefinition> Roster60 => _roster60;
        public IReadOnlyList<TacticalCampaignStageDefinition> Stages15 => _stages15;
        public CampaignPilotProgressionState Progression => progressionState;

        private void Awake()
        {
            InitializeSetOneRosterAndStages();
        }

        public void InitializeSetOneRosterAndStages()
        {
            if (_roster60.Count == TotalSetOneCards && _stages15.Count == TotalCampaignStages)
            {
                return;
            }

            _roster60.Clear();
            _cardsById.Clear();
            _stages15.Clear();
            _stagesById.Clear();

            BuildCanonicalAndSetOneRoster();
            BuildFifteenCampaignStages();
            progressionState.lastSaveFnv1a64Hash = ComputeCampaignSaveFnv1a64Hash();
        }

        private void RegisterCard(SetOneCardDefinition card)
        {
            _roster60.Add(card);
            _cardsById[card.cardId] = card;
        }

        private void BuildCanonicalAndSetOneRoster()
        {
            // Canonical 14 (10 PROJECT CF + 4 CardCraft Studio)
            RegisterCard(new SetOneCardDefinition("cf_01_mystic_mage", "Mystic Mage", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Legendary, 5, 6, 7, 3, 8, "Teleport", "Relocate to any empty grid tile and trigger captures.", 2, "hi3d_cf_01_mystic_mage"));
            RegisterCard(new SetOneCardDefinition("cf_02_mech_knight", "Mech Knight", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Epic, 8, 5, 4, 6, 10, "Charge", "Grant immediate bonus deployment on capture.", 3, "hi3d_cf_02_mech_knight"));
            RegisterCard(new SetOneCardDefinition("cf_03_celestial_guardian", "Celestial Guardian", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Legendary, 6, 7, 9, 4, 12, "HealingAura", "Fortify adjacent allied stacks by +1.", 3, "hi3d_cf_03_celestial_guardian"));
            RegisterCard(new SetOneCardDefinition("cf_04_shadow_assassin", "Shadow Assassin", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Epic, 7, 4, 5, 8, 6, "Vanish", "Optical camouflage immunity for 1 turn.", 1, "hi3d_cf_04_shadow_assassin"));
            RegisterCard(new SetOneCardDefinition("cf_05_elemental_sprite", "Elemental Sprite", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Rare, 3, 9, 4, 6, 5, "ElementalBurst", "Swap directional stats with an adjacent card.", 1, "hi3d_cf_05_elemental_sprite"));
            RegisterCard(new SetOneCardDefinition("cf_06_galactic_explorer", "Galactic Explorer", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Epic, 7, 8, 6, 5, 9, "WarpDrive", "Slide 1 orthogonal tile into an empty cell.", 2, "hi3d_cf_06_galactic_explorer"));
            RegisterCard(new SetOneCardDefinition("cf_07_clockwork_sorcerer", "Clockwork Sorcerer", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Legendary, 4, 5, 8, 7, 11, "TemporalRift", "Invert Up/Down and Left/Right on adjacent cards.", 2, "hi3d_cf_07_clockwork_sorcerer"));
            RegisterCard(new SetOneCardDefinition("cf_08_phoenix_guardian", "Phoenix Guardian", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Legendary, 9, 4, 7, 6, 14, "Rebirth", "Return to original owner hand with +1 stats on first capture.", 3, "hi3d_cf_08_phoenix_guardian"));
            RegisterCard(new SetOneCardDefinition("cf_09_cyber_ninja", "Digital Shadow", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Epic, 6, 7, 5, 8, 6, "TechnoStealth", "Capture immune while adjacent to Tech or Stealth ally.", 1, "hi3d_cf_09_cyber_ninja"));
            RegisterCard(new SetOneCardDefinition("cf_10_lunar_oracle", "Lunar Oracle", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Legendary, 7, 9, 6, 4, 10, "MoonlightBlessing", "+1 all sides at night or adjacent to Solaris-Divine.", 2, "hi3d_cf_10_lunar_oracle"));
            RegisterCard(new SetOneCardDefinition("cc_01_sketching", "Sketching", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Common, 4, 5, 5, 6, 4, "IdeationDraft", "Gain +10 CP on deployment; evolves into Concept Art.", 1, "hi3d_cc_01_sketching", "cc_02_concept_art"));
            RegisterCard(new SetOneCardDefinition("cc_02_concept_art", "Concept Art", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Rare, 6, 7, 7, 8, 6, "KeyartProjection", "Project 2.5px ink barrier boosting adjacent Artisan stacks.", 2, "hi3d_cc_02_concept_art"));
            RegisterCard(new SetOneCardDefinition("cc_03_storyboard", "Storyboard", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Common, 5, 6, 6, 5, 4, "SequencedPanels", "Reduce next MGA card COST by 2; evolves into Animatic.", 1, "hi3d_cc_03_storyboard", "cc_04_animatic"));
            RegisterCard(new SetOneCardDefinition("cc_04_animatic", "Animatic", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Rare, 7, 8, 8, 7, 7, "WarpDrive", "12fps On-Twos dash and Link trigger.", 2, "hi3d_cc_04_animatic"));

            // Aether-Tech (10 Expansion Cards: s1_15 .. s1_24)
            RegisterCard(new SetOneCardDefinition("s1_15_aether_vanguard", "Aether Vanguard", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Common, 6, 6, 5, 5, 6, "AetherShieldWall", "Absorb 1 telegraphed hazard hit without shedding support layers.", 2, "hi3d_s1_15_aether_vanguard"));
            RegisterCard(new SetOneCardDefinition("s1_16_railgun_dragoon", "Railgun Dragoon", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Rare, 8, 7, 4, 5, 9, "LinePiercingSlug", "Push target orthogonal enemy 1 tile backward.", 2, "hi3d_s1_16_railgun_dragoon"));
            RegisterCard(new SetOneCardDefinition("s1_17_servo_bastion_mk2", "Servo Bastion Mk.II", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Common, 5, 5, 8, 6, 7, "HydraulicBrace", "Immune to enemy push/pull displacement.", 3, "hi3d_s1_17_servo_bastion_mk2"));
            RegisterCard(new SetOneCardDefinition("s1_18_orbital_relay_drone", "Orbital Relay Drone", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Common, 4, 7, 4, 7, 5, "TelemetryUplink", "Triggers +4 Link salvo when equipped.", 1, "hi3d_s1_18_orbital_relay_drone"));
            RegisterCard(new SetOneCardDefinition("s1_19_plasma_halberdier", "Plasma Halberdier", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Rare, 7, 6, 6, 5, 8, "CleavingArc", "+2 capture bonus against lower STACCS elevation.", 2, "hi3d_s1_19_plasma_halberdier"));
            RegisterCard(new SetOneCardDefinition("s1_20_chronos_hover_tank", "Chronos Hover Tank", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Epic, 8, 8, 6, 6, 12, "OverdriveTreads", "Ignores terrain movement cost and knocks back targets.", 3, "hi3d_s1_20_chronos_hover_tank"));
            RegisterCard(new SetOneCardDefinition("s1_21_nanoforge_engineer", "Nanoforge Engineer", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Common, 5, 6, 6, 5, 5, "GridCapacitorRepair", "Restore +1 bar to the civilian Power Grid.", 1, "hi3d_s1_21_nanoforge_engineer"));
            RegisterCard(new SetOneCardDefinition("s1_22_tesla_siege_walker", "Tesla Siege Walker", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Epic, 9, 6, 7, 5, 13, "ChainArcDischarge", "Arcs capture pressure across connected enemy stacks.", 3, "hi3d_s1_22_tesla_siege_walker"));
            RegisterCard(new SetOneCardDefinition("s1_23_valkyrie_interceptor", "Valkyrie Interceptor", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Rare, 7, 8, 5, 6, 8, "VectorThruster", "Rotate enemy facing 90 degrees to expose blind spot.", 2, "hi3d_s1_23_valkyrie_interceptor"));
            RegisterCard(new SetOneCardDefinition("s1_24_rex_metal_colossus", "REX Metal Colossus", "Aether-Tech", "Tech", SetOneFactionType.AetherTech, SetOneRarityType.Legendary, 10, 8, 8, 7, 18, "RailCannonOmega", "Row/column rail strike and +2 CO Stars.", 3, "hi3d_s1_24_rex_metal_colossus"));

            // Chrono-Arcana (9 Expansion Cards: s1_25 .. s1_33)
            RegisterCard(new SetOneCardDefinition("s1_25_astral_scholar", "Astral Scholar", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Common, 5, 6, 6, 4, 5, "RuneInscription", "Gain +1 FFTA Judge Point on Law compliance.", 1, "hi3d_s1_25_astral_scholar"));
            RegisterCard(new SetOneCardDefinition("s1_26_void_weaver", "Void Weaver", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Rare, 6, 8, 5, 7, 8, "GravityWellPull", "Pull enemy stack 1 tile to deflect its telegraph.", 2, "hi3d_s1_26_void_weaver"));
            RegisterCard(new SetOneCardDefinition("s1_27_pendulum_alchemist", "Pendulum Alchemist", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Common, 6, 5, 7, 4, 6, "EquivalenceTransmute", "Equalize highest and lowest directional stats.", 1, "hi3d_s1_27_pendulum_alchemist"));
            RegisterCard(new SetOneCardDefinition("s1_28_rift_archon", "Rift Archon", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Epic, 8, 7, 8, 5, 11, "PhaseSwap", "Swap positions of any two allied stacks for 0 Move COST.", 2, "hi3d_s1_28_rift_archon"));
            RegisterCard(new SetOneCardDefinition("s1_29_spellblade_duelist", "Spellblade Duelist", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Rare, 7, 7, 5, 6, 7, "ArcaneRiposte", "+2 counter bonus against frontal 90-degree attacks.", 2, "hi3d_s1_29_spellblade_duelist"));
            RegisterCard(new SetOneCardDefinition("s1_30_starlight_diviner", "Starlight Diviner", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Common, 4, 6, 6, 6, 5, "ForesightLens", "Reveal enemy Equip slots and reduce Link COST to 0.", 1, "hi3d_s1_30_starlight_diviner"));
            RegisterCard(new SetOneCardDefinition("s1_31_aeon_hourglass_mage", "Aeon Hourglass Mage", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Epic, 7, 8, 9, 5, 12, "CostClockRewind", "Subtract 4 ticks from active unit MGA COST clock.", 2, "hi3d_s1_31_aeon_hourglass_mage"));
            RegisterCard(new SetOneCardDefinition("s1_32_grimoire_sentinel", "Grimoire Sentinel", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Rare, 6, 5, 8, 7, 8, "WardOfIvalice", "Nullify next enemy stat reversal or displacement.", 3, "hi3d_s1_32_grimoire_sentinel"));
            RegisterCard(new SetOneCardDefinition("s1_33_chronos_grand_magus", "Chronos Grand Magus", "Chrono-Arcana", "Magic", SetOneFactionType.ChronoArcana, SetOneRarityType.Legendary, 9, 9, 8, 7, 16, "MateusTimeStop", "Freeze enemy COST clocks and invert board stats.", 3, "hi3d_s1_33_chronos_grand_magus"));

            // Solaris-Divine (9 Expansion Cards: s1_34 .. s1_42)
            RegisterCard(new SetOneCardDefinition("s1_34_dawn_templar", "Dawn Templar", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Common, 6, 5, 7, 5, 6, "SunlitBulwark", "+1 support bonus when stacked under Solaris-Divine.", 2, "hi3d_s1_34_dawn_templar"));
            RegisterCard(new SetOneCardDefinition("s1_35_seraphic_lancer", "Seraphic Lancer", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Rare, 8, 6, 6, 5, 8, "SkywardDive", "+2 Up/Down stats at STACCS Z-height >= 2.", 3, "hi3d_s1_35_seraphic_lancer"));
            RegisterCard(new SetOneCardDefinition("s1_36_aegis_hierophant", "Aegis Hierophant", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Common, 5, 6, 7, 5, 6, "SanctuaryBell", "Shield adjacent Power Grid buildings from 1 hit.", 2, "hi3d_s1_36_aegis_hierophant"));
            RegisterCard(new SetOneCardDefinition("s1_37_radiant_valkyrie", "Radiant Valkyrie", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Epic, 8, 8, 7, 6, 11, "HaloAscension", "Elevate allied stack by +1 Z-height and restore 1 layer.", 3, "hi3d_s1_37_radiant_valkyrie"));
            RegisterCard(new SetOneCardDefinition("s1_38_solaris_inquisitor", "Solaris Inquisitor", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Rare, 7, 7, 6, 6, 8, "LawEnforcer", "+3 capture power against Judge Law violators.", 2, "hi3d_s1_38_solaris_inquisitor"));
            RegisterCard(new SetOneCardDefinition("s1_39_eclipse_paladin", "Eclipse Paladin", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Epic, 7, 6, 9, 7, 12, "TwinCorona", "Triggers both HealingAura and MoonlightBlessing.", 3, "hi3d_s1_39_eclipse_paladin"));
            RegisterCard(new SetOneCardDefinition("s1_40_choir_chronicle_bard", "Choir Chronicle Bard", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Common, 4, 6, 5, 6, 5, "HymnOfValiance", "Charge +1.0 Advance Wars CO Star on play.", 1, "hi3d_s1_40_choir_chronicle_bard"));
            RegisterCard(new SetOneCardDefinition("s1_41_archangel_judicator", "Archangel Judicator", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Legendary, 9, 8, 9, 7, 16, "UltimaVerdict", "Summon Totema Ultima across a 3x3 cross.", 3, "hi3d_s1_41_archangel_judicator"));
            RegisterCard(new SetOneCardDefinition("s1_42_sunforge_colossus", "Sunforge Colossus", "Solaris-Divine", "Divine", SetOneFactionType.SolarisDivine, SetOneRarityType.Rare, 8, 5, 8, 5, 9, "PillarOfDawn", "Height-3 spire blocking enemy vision cones.", 3, "hi3d_s1_42_sunforge_colossus"));

            // Umbra-Stealth (10 Expansion Cards: s1_43 .. s1_52)
            RegisterCard(new SetOneCardDefinition("s1_43_whisper_infiltrator", "Whisper Infiltrator", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Common, 6, 5, 4, 7, 4, "SilentFootstep", "Move adds only +3 COST and avoids vision alerts.", 1, "hi3d_s1_43_whisper_infiltrator"));
            RegisterCard(new SetOneCardDefinition("s1_44_kunoichi_mirage", "Kunoichi Mirage", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Rare, 7, 6, 5, 8, 6, "PaperDecoy", "Spawn holographic decoy to absorb 1 telegraph.", 1, "hi3d_s1_44_kunoichi_mirage"));
            RegisterCard(new SetOneCardDefinition("s1_45_optic_camo_sniper", "Optic Camo Sniper", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Rare, 8, 4, 4, 9, 7, "BlindspotHeadshot", "+3 attack and -2 COST from outside 90-degree cone.", 1, "hi3d_s1_45_optic_camo_sniper"));
            RegisterCard(new SetOneCardDefinition("s1_46_smoke_veil_saboteur", "Smoke Veil Saboteur", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Common, 5, 6, 5, 6, 5, "ChaffGrenade", "Disable enemy MGA Equip Link chains for 1 turn.", 1, "hi3d_s1_46_smoke_veil_saboteur"));
            RegisterCard(new SetOneCardDefinition("s1_47_phantom_cqc_operative", "Phantom CQC Operative", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Epic, 8, 7, 6, 8, 8, "NojiriCqcThrow", "Throw adjacent enemy 1 tile for double push damage.", 2, "hi3d_s1_47_phantom_cqc_operative"));
            RegisterCard(new SetOneCardDefinition("s1_48_nightshade_stalker", "Nightshade Stalker", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Common, 6, 6, 4, 6, 5, "CornerPeek", "+2 Left/Right stats next to wall or height-3 stack.", 1, "hi3d_s1_48_nightshade_stalker"));
            RegisterCard(new SetOneCardDefinition("s1_49_zero_pulse_hacker", "Zero Pulse Hacker", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Rare, 5, 8, 5, 7, 6, "LogicBombInject", "Add +4 COST delay ticks to adjacent enemy clock.", 1, "hi3d_s1_49_zero_pulse_hacker"));
            RegisterCard(new SetOneCardDefinition("s1_50_obsidian_ronin", "Obsidian Ronin", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Epic, 9, 6, 5, 8, 9, "IaijutsuBackstab", "1.50x rear FFTA multiplier + MGA stealth ambush.", 2, "hi3d_s1_50_obsidian_ronin"));
            RegisterCard(new SetOneCardDefinition("s1_51_eclipse_wire_agent", "Eclipse Wire Agent", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Common, 5, 7, 4, 6, 4, "ZipwireExtraction", "Instant extraction on MGA extraction tile.", 1, "hi3d_s1_51_eclipse_wire_agent"));
            RegisterCard(new SetOneCardDefinition("s1_52_viper_solid_eye_prime", "Viper Solid Eye Prime", "Umbra-Stealth", "Stealth", SetOneFactionType.UmbraStealth, SetOneRarityType.Legendary, 9, 8, 7, 10, 14, "SolidEyeTacticalOverride", "All Stealth allies gain 1.5x ambush power from flanks.", 2, "hi3d_s1_52_viper_solid_eye_prime"));

            // CardCraft-Studio (8 Expansion Cards: s1_53 .. s1_60)
            RegisterCard(new SetOneCardDefinition("s1_53_ink_brush_calligrapher", "Ink Brush Calligrapher", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Common, 5, 6, 5, 6, 5, "ShinkawaSumiStroke", "Draw 3.2px sumi-e contour granting +1 defense star.", 1, "hi3d_s1_53_ink_brush_calligrapher"));
            RegisterCard(new SetOneCardDefinition("s1_54_halftone_pop_stylist", "Halftone Pop Stylist", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Rare, 6, 8, 6, 7, 7, "BenDayBurst", "Boost allied MGA Link damage by +3 via halftone pop.", 2, "hi3d_s1_54_halftone_pop_stylist"));
            RegisterCard(new SetOneCardDefinition("s1_55_sakuga_key_animator", "Sakuga Key Animator", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Epic, 8, 8, 6, 7, 10, "OnOnesImpactFrame", "24fps On-Ones impact flash stunning enemy telegraph.", 2, "hi3d_s1_55_sakuga_key_animator"));
            RegisterCard(new SetOneCardDefinition("s1_56_parchment_cartographer", "Parchment Cartographer", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Common, 4, 5, 7, 6, 5, "IvaliceTopography", "Upgrade grid cell into 3-star Citadel terrain.", 2, "hi3d_s1_56_parchment_cartographer"));
            RegisterCard(new SetOneCardDefinition("s1_57_voxel_sculptor_hi3d", "Voxel Sculptor Hi3D", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Rare, 7, 6, 8, 6, 8, "ManifoldExtrusion", "Extrude watertight Euler X=2 support cube (+1 Z-height).", 3, "hi3d_s1_57_voxel_sculptor_hi3d"));
            RegisterCard(new SetOneCardDefinition("s1_58_palette_harmonizer", "Palette Harmonizer", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Common, 5, 7, 5, 6, 5, "ChromaticResonance", "Matches all 5 factions for synergy and Equip-Link.", 1, "hi3d_s1_58_palette_harmonizer"));
            RegisterCard(new SetOneCardDefinition("s1_59_atelier_master_director", "Atelier Master Director", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Epic, 8, 9, 7, 8, 13, "GreenlightProduction", "Evolve all Tier-1 CardCraft allies and grant +25 CP.", 2, "hi3d_s1_59_atelier_master_director"));
            RegisterCard(new SetOneCardDefinition("s1_60_omega_chronos_prime", "Omega Chronos Prime", "CardCraft-Studio", "Artisan", SetOneFactionType.CardCraftStudio, SetOneRarityType.Legendary, 10, 9, 9, 10, 20, "SovereignMasterpiece", "Unites all 5 Factions, triggers Super CO Power, and restores +2 Power Grid.", 3, "hi3d_s1_60_omega_chronos_prime"));
        }

        private void RegisterStage(TacticalCampaignStageDefinition stage)
        {
            _stages15.Add(stage);
            _stagesById[stage.stageId] = stage;
        }

        private void BuildFifteenCampaignStages()
        {
            RegisterStage(new TacticalCampaignStageDefinition(1, 1, 1, "stage_01_aether_rail_depot", "Act I-1: Aether Rail Depot Breach", "Industrial_Railyard", "Aether-Tech", "co_lash_mechanized", "Terrain Tactics", "Prime Tactics", "law_01_no_high_cost_over_16", "CostOver16", "Aether-Tech Equip", 8, 3, 85, new Vector2Int(7, 7), new[] { "cf_02_mech_knight", "s1_15_aether_vanguard", "s1_16_railgun_dragoon", "s1_17_servo_bastion_mk2", "s1_18_orbital_relay_drone" }));
            RegisterStage(new TacticalCampaignStageDefinition(2, 1, 2, "stage_02_capacitor_spire_defense", "Act I-2: Capacitor Spire Defense", "High_Voltage_Spire", "Aether-Tech", "co_hawke_black_wave", "Black Wave", "Black Storm", "law_02_preserve_power_grid", "CivilianGridDamage", "PushDisplacement", 8, 2, 90, new Vector2Int(7, 6), new[] { "cf_06_galactic_explorer", "s1_19_plasma_halberdier", "s1_20_chronos_hover_tank", "s1_21_nanoforge_engineer", "s1_22_tesla_siege_walker" }));
            RegisterStage(new TacticalCampaignStageDefinition(3, 1, 3, "stage_03_rex_foundry_showdown", "Act I-3: REX Foundry Showdown", "Molten_Mecha_Foundry", "Aether-Tech", "co_sturm_meteor", "Meteor Strike", "Super Meteor Strike", "law_03_mandatory_equip_link", "ZeroEquipPlay", "LinkChain", 9, 3, 95, new Vector2Int(7, 7), new[] { "cf_02_mech_knight", "s1_20_chronos_hover_tank", "s1_22_tesla_siege_walker", "s1_23_valkyrie_interceptor", "s1_24_rex_metal_colossus" }));

            RegisterStage(new TacticalCampaignStageDefinition(4, 2, 1, "stage_04_clockwork_astrolabe", "Act II-1: Clockwork Astrolabe", "Chrono_Observatory", "Chrono-Arcana", "co_sonja_chronos", "Enhanced Vision", "Counter Break", "law_04_no_frontal_assault", "Frontal90ConeAttack", "TemporalRiftOrFlank", 8, 3, 85, new Vector2Int(7, 5), new[] { "cf_01_mystic_mage", "cf_05_elemental_sprite", "s1_25_astral_scholar", "s1_26_void_weaver", "s1_27_pendulum_alchemist" }));
            RegisterStage(new TacticalCampaignStageDefinition(5, 2, 2, "stage_05_pendulum_rift_bridge", "Act II-2: Pendulum Rift Bridge", "Suspended_Aether_Bridge", "Chrono-Arcana", "co_olaf_blizzard", "Blizzard", "Winter Fury", "law_05_minimum_z_height_2", "SoloUnstackedTopCapture", "VerticalStacking", 8, 2, 90, new Vector2Int(7, 7), new[] { "cf_07_clockwork_sorcerer", "s1_28_rift_archon", "s1_29_spellblade_duelist", "s1_30_starlight_diviner", "s1_31_aeon_hourglass_mage" }));
            RegisterStage(new TacticalCampaignStageDefinition(6, 2, 3, "stage_06_mateus_sanctum_nexus", "Act II-3: Mateus Sanctum Nexus", "Temporal_Vortex_Sanctum", "Chrono-Arcana", "co_kanbei_samurai", "Morale Boost", "Samurai Spirit", "law_06_arcane_combo_mandate", "ZeroJPCombo", "MythrilCombo", 9, 3, 95, new Vector2Int(7, 7), new[] { "cf_01_mystic_mage", "cf_07_clockwork_sorcerer", "s1_31_aeon_hourglass_mage", "s1_32_grimoire_sentinel", "s1_33_chronos_grand_magus" }));

            RegisterStage(new TacticalCampaignStageDefinition(7, 3, 1, "stage_07_solaris_sky_bastion", "Act III-1: Solaris Sky Bastion", "Floating_Marble_Citadel", "Solaris-Divine", "co_rachel_covering_fire", "Lucky Lass", "Covering Fire", "law_07_protect_allied_stacks", "SacrificeSupportLayer", "HealingAura", 9, 3, 85, new Vector2Int(7, 6), new[] { "cf_03_celestial_guardian", "s1_34_dawn_templar", "s1_35_seraphic_lancer", "s1_36_aegis_hierophant", "s1_40_choir_chronicle_bard" }));
            RegisterStage(new TacticalCampaignStageDefinition(8, 3, 2, "stage_08_lunar_eclipse_cathedral", "Act III-2: Lunar Eclipse Cathedral", "Nocturnal_Cathedral", "Solaris-Divine", "co_drake_tsunami", "Tsunami", "Typhoon", "law_08_nocturnal_blessing", "DaytimeFlare", "MoonlightBlessing", 9, 2, 90, new Vector2Int(7, 7), new[] { "cf_10_lunar_oracle", "s1_37_radiant_valkyrie", "s1_38_solaris_inquisitor", "s1_39_eclipse_paladin", "s1_42_sunforge_colossus" }));
            RegisterStage(new TacticalCampaignStageDefinition(9, 3, 3, "stage_09_ultima_seraph_throne", "Act III-3: Ultima Seraph Throne", "Apex_Empyrean_Throne", "Solaris-Divine", "co_eagle_lightning", "Lightning Drive", "Lightning Strike", "law_09_totema_summon_honor", "UnlinkedSoloStrike", "TotemaSummon", 10, 3, 95, new Vector2Int(7, 7), new[] { "cf_03_celestial_guardian", "cf_08_phoenix_guardian", "cf_10_lunar_oracle", "s1_39_eclipse_paladin", "s1_41_archangel_judicator" }));

            RegisterStage(new TacticalCampaignStageDefinition(10, 4, 1, "stage_10_shadow_comms_infiltration", "Act IV-1: Shadow Comms Infiltration", "Subzero_Helipad_Base", "Umbra-Stealth", "co_grit_snipe", "Snipe Attack", "Super Snipe", "law_10_zero_vision_cone_alerts", "TriggerVisionAlert", "StealthAmbush90Cone", 8, 3, 75, new Vector2Int(7, 7), new[] { "cf_04_shadow_assassin", "s1_43_whisper_infiltrator", "s1_44_kunoichi_mirage", "s1_46_smoke_veil_saboteur", "s1_48_nightshade_stalker" }));
            RegisterStage(new TacticalCampaignStageDefinition(11, 4, 2, "stage_11_laser_corridor_cqc", "Act IV-2: Laser Corridor CQC", "Security_Laser_Vault", "Umbra-Stealth", "co_jess_resupply", "Turbo Charge", "Overdrive", "law_11_cqc_displacement_only", "StaticTrades", "NojiriCqcKnockback", 8, 2, 80, new Vector2Int(7, 5), new[] { "cf_09_cyber_ninja", "s1_45_optic_camo_sniper", "s1_47_phantom_cqc_operative", "s1_49_zero_pulse_hacker", "s1_51_eclipse_wire_agent" }));
            RegisterStage(new TacticalCampaignStageDefinition(12, 4, 3, "stage_12_solid_eye_hangar_extraction", "Act IV-3: Solid Eye Hangar Extraction", "Underground_Mecha_Hangar", "Umbra-Stealth", "co_adder_sideslip", "Sideslip", "Sidewinder", "law_12_low_cost_stealth_tempo", "CostAbove14", "Sub8CostAmbush", 9, 3, 85, new Vector2Int(7, 7), new[] { "cf_04_shadow_assassin", "cf_09_cyber_ninja", "s1_47_phantom_cqc_operative", "s1_50_obsidian_ronin", "s1_52_viper_solid_eye_prime" }));

            RegisterStage(new TacticalCampaignStageDefinition(13, 5, 1, "stage_13_sumi_parchment_atelier", "Act V-1: Sumi Parchment Atelier", "Ivalice_Ink_Atelier", "CardCraft-Studio", "co_sami_double_time", "Double Time", "Victory March", "law_13_creative_cp_evolution", "UnevolvedTier1", "EvolveCardCraft", 9, 3, 90, new Vector2Int(7, 7), new[] { "cc_01_sketching", "cc_02_concept_art", "s1_53_ink_brush_calligrapher", "s1_56_parchment_cartographer", "s1_58_palette_harmonizer" }));
            RegisterStage(new TacticalCampaignStageDefinition(14, 5, 2, "stage_14_sakuga_halftone_arena", "Act V-2: Sakuga Halftone Arena", "Trigger_PopCel_Colosseum", "CardCraft-Studio", "co_max_blast", "Max Force", "Max Blast", "law_14_on_ones_sakuga_link", "UnlinkedEffect", "HalftoneLinkChain", 9, 2, 95, new Vector2Int(7, 7), new[] { "cc_03_storyboard", "cc_04_animatic", "s1_54_halftone_pop_stylist", "s1_55_sakuga_key_animator", "s1_57_voxel_sculptor_hi3d" }));
            RegisterStage(new TacticalCampaignStageDefinition(15, 5, 3, "stage_15_omega_chronos_sovereign_nexus", "Act V-3: Omega Chronos Sovereign Finale", "Sovereign_LumenForge_Nexus", "CardCraft-Studio", "co_von_bolt_ex_machina", "Lightning Bolt", "Ex Machina", "law_15_five_faction_grand_harmony", "SingleFactionMonoculture", "FiveFactionGrandSynergy", 10, 3, 100, new Vector2Int(7, 7), new[] { "s1_24_rex_metal_colossus", "s1_33_chronos_grand_magus", "s1_41_archangel_judicator", "s1_52_viper_solid_eye_prime", "s1_60_omega_chronos_prime" }));
        }

        public bool ValidateFiveFactionDeck(IReadOnlyList<string> cardIds, int minDeckSize = 5, int maxDeckSize = 12)
        {
            InitializeSetOneRosterAndStages();
            if (cardIds == null || cardIds.Count < minDeckSize || cardIds.Count > maxDeckSize)
            {
                return false;
            }

            for (int i = 0; i < cardIds.Count; i++)
            {
                if (!_cardsById.ContainsKey(cardIds[i]))
                {
                    return false;
                }
            }
            return true;
        }

        public Dictionary<SetOneFactionType, int> GetFactionDistribution()
        {
            InitializeSetOneRosterAndStages();
            var counts = new Dictionary<SetOneFactionType, int>
            {
                { SetOneFactionType.AetherTech, 0 },
                { SetOneFactionType.ChronoArcana, 0 },
                { SetOneFactionType.SolarisDivine, 0 },
                { SetOneFactionType.UmbraStealth, 0 },
                { SetOneFactionType.CardCraftStudio, 0 }
            };

            for (int i = 0; i < _roster60.Count; i++)
            {
                counts[_roster60[i].factionType]++;
            }
            return counts;
        }

        public ulong ComputeCampaignSaveFnv1a64Hash()
        {
            ulong hash = 14695981039346656037UL;
            const ulong prime = 1099511628211UL;

            void MixString(string s)
            {
                if (string.IsNullOrEmpty(s)) return;
                byte[] bytes = Encoding.UTF8.GetBytes(s);
                for (int i = 0; i < bytes.Length; i++)
                {
                    hash ^= bytes[i];
                    hash *= prime;
                }
            }

            void MixInt(int v)
            {
                hash ^= (ulong)v;
                hash *= prime;
            }

            MixString(progressionState.pilotId);
            MixString(progressionState.activeCommanderId);
            MixInt(progressionState.highestUnlockedStage);
            MixInt(progressionState.totalSRanksEarned);
            MixInt(progressionState.cumulativePowerGridSaved);
            MixInt(progressionState.judgePointsBank);
            MixInt(progressionState.confidencePointsBank);

            for (int i = 0; i < progressionState.clearedStageIds.Count; i++)
            {
                MixString(progressionState.clearedStageIds[i]);
            }
            return hash;
        }

        public bool RecordCampaignStageClear(string stageId, int remainingPowerBars, bool achievedSRank)
        {
            InitializeSetOneRosterAndStages();
            if (!_stagesById.TryGetValue(stageId, out var stageDef))
            {
                return false;
            }

            if (!progressionState.clearedStageIds.Contains(stageId))
            {
                progressionState.clearedStageIds.Add(stageId);
            }

            if (stageDef.stageNumber >= progressionState.highestUnlockedStage &&
                progressionState.highestUnlockedStage < TotalCampaignStages)
            {
                progressionState.highestUnlockedStage = stageDef.stageNumber + 1;
            }

            if (achievedSRank)
            {
                progressionState.totalSRanksEarned++;
            }

            progressionState.cumulativePowerGridSaved += Mathf.Max(0, remainingPowerBars);
            progressionState.judgePointsBank = Mathf.Min(10, progressionState.judgePointsBank + 2);
            progressionState.confidencePointsBank += 15;
            progressionState.lastSaveFnv1a64Hash = ComputeCampaignSaveFnv1a64Hash();
            return true;
        }
    }
}
