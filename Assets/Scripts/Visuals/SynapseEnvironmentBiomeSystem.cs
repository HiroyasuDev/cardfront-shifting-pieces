using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Synapse.TcgEngine.Visuals
{
    /// <summary>
    /// 6 Playable 3x3 Isometric Diorama Arena Biomes in Synapse.TcgEngine.
    /// </summary>
    public enum ArenaBiomeType
    {
        IvaliceStorybookJagd   = 0, // Hideo Minaba, Koji Tsukamoto & Isamu Kamikokuryo (FFTA / FFIX / FFXII / Granblue Fantasy)
        OrbonneDioramaBastion  = 1, // Hiroshi Minagawa & Akihiko Yoshida (Final Fantasy Tactics / Tactics Ogre / Vagrant Story)
        MacroLandCommandGrid   = 2, // Ryo Hirata, Daisuke Izuka & Sachiko Wada (Advance Wars 1/2/Dual Strike/Days of Ruin & Fire Emblem GBA)
        NeoArcadiaCyberSanctum = 3, // Toru Nakayama & Inti Creates Environment Team: Masaya Suzuki / Makoto Yabe (Mega Man Zero 1-4 / ZX / Dragon Marked for Death)
        ClockworkAetherFoundry = 4, // Synthesis: Minaba Steampunk Architecture + Kamikokuryo Sky-Machina + Minagawa Elevation Gearworks
        EclipseLunarShrine     = 5  // Synthesis: Yoshida Sacred Ruin Masonry + Nakayama Cyber-Astral Monoliths + Minaba Moonlight Bloom
    }

    /// <summary>
    /// Per-cell tactical terrain modifiers for the 3x3 Arena Grid (cells 0..8).
    /// </summary>
    public enum CellTerrainModifier
    {
        StandardGround = 0, // Neutral tactical tile (+0 all sides)
        HighGround     = 1, // Minagawa/Yoshida isometric stone bastion elevation (+1 Top/Bottom axial defense)
        LeylineCrystal = 2, // Minaba/Kamikokuryo Jagd mana crystal enclave (+1 Magic/Divine/Lunar resonance)
        CommandHQ      = 3, // Hirata/Izuka/Wada Advance Wars & Fire Emblem throne/HQ capture point (+1 all sides while controlled)
        CyberConduit   = 4, // Nakayama/Inti Creates Neo Arcadia beveled neon energy conduit (+1 Left/Right lateral surge)
        ShadowVeil     = 5  // Vagrant Story / Resistance Base stealth cover tile (grants optical refraction & ambush bonus)
    }

    /// <summary>
    /// Master Environmental & Map Architecture Lineage identifier.
    /// </summary>
    public enum EnvironmentMasterLineage
    {
        Minagawa_Yoshida_IsometricDiorama     = 0,
        Minaba_Tsukamoto_Kamikokuryo_Storybook = 1,
        Hirata_Izuka_Wada_TacticalCommandGrid = 2,
        Nakayama_IntiCreates_NeoArcadiaCyber  = 3
    }

    [Serializable]
    public class EnvironmentLineageMetadata
    {
        public EnvironmentMasterLineage lineageId;
        public string leadMasters;
        public string japaneseNames;
        public string foundationalTitles;
        public string architecturalSignature;
        public string spatialDesignRules;
    }

    [Serializable]
    public struct CellTerrainDefinition
    {
        public int cellIndex; // 0..8 (row = cellIndex / 3, col = cellIndex % 3)
        public int row;
        public int col;
        public CellTerrainModifier modifier;
        public float elevationOffset;
        public Vector4 statBonusNESW; // x=Top(N), y=Right(E), z=Bottom(S), w=Left(W)
        public string tacticalDescription;
    }

    [Serializable]
    public class ArenaBiomeProfile
    {
        public ArenaBiomeType biomeType;
        public string biomeTitle;
        public string subtitle;
        public EnvironmentMasterLineage primaryLineage;
        public string resourceBackdropPath; // Path under Resources/ (e.g., "CardArt/Environments/env_minaba_ivalice_storybook")
        public string comfyUiEnvironmentPrompt;

        // Ambient Lighting & Fog Shader Vectors
        public Color ambientSkyColor;
        public Color ambientEquatorColor;
        public Color directionalSunColor;
        public Vector4 fogDensityAndHeightVector; // x=density, y=heightFalloff, z=startDistance, w=bloomScatter
        public Vector4 dioramaShaderGrading;      // x=masonryRelief, y=storybookBloom, z=gridReadabilityContrast, w=neonConduitGlow

        // 3x3 Per-Cell Terrain Layout (Length = 9)
        public CellTerrainDefinition[] gridCells = new CellTerrainDefinition[9];
    }

    /// <summary>
    /// Clean-room Proprietary 3x3 Isometric Diorama Board & Terrain Biome System for Synapse.TcgEngine.
    /// Encodes the Master Environmental & Map Architecture Lineage:
    /// 1. Hiroshi Minagawa (皆川 裕史) & Akihiko Yoshida: Final Fantasy Tactics, Tactics Ogre, Vagrant Story
    ///    (3D isometric diorama stone bastions, elevation chiaroscuro, weathered masonry).
    /// 2. Hideo Minaba (皆葉 英夫), Koji Tsukamoto & Isamu Kamikokuryo: Final Fantasy Tactics Advance, FFIX, FFXII, Granblue Fantasy
    ///    (Vibrant storybook map artifacts, crystal Jagds, sky-citadels).
    /// 3. Ryo Hirata (平田 亮), Daisuke Izuka & Sachiko Wada: Advance Wars 1/2/Dual Strike/Days of Ruin & Fire Emblem (Thracia 776 / Binding Blade / Sacred Stones)
    ///    (High-readability tactical terrain tiles, HQ capture points, dynamic battle cut-in backgrounds).
    /// 4. Toru Nakayama (中山 徹) & Inti Creates Environment Team (Masaya Suzuki / Makoto Yabe): Mega Man Zero 1-4 (Rockman Zero), Mega Man ZX, Dragon Marked for Death
    ///    (Neo Arcadia cyber-cathedrals, beveled neon energy conduits, Resistance Base ruins).
    /// </summary>
    public class SynapseEnvironmentBiomeSystem : MonoBehaviour
    {
        private static readonly int PropAmbientSky      = Shader.PropertyToID("_SynapseAmbientSky");
        private static readonly int PropAmbientEquator  = Shader.PropertyToID("_SynapseAmbientEquator");
        private static readonly int PropSunColor        = Shader.PropertyToID("_SynapseSunColor");
        private static readonly int PropFogVector       = Shader.PropertyToID("_SynapseFogVector");
        private static readonly int PropDioramaGrading  = Shader.PropertyToID("_SynapseDioramaGrading");
        private static readonly int PropBackdropTex     = Shader.PropertyToID("_MainTex");

        [Header("Active Arena Biome Configuration")]
        public ArenaBiomeType activeBiome = ArenaBiomeType.IvaliceStorybookJagd;
        public Renderer boardBackdropRenderer;
        public RawImage boardBackdropUIImage;
        public Light directionalKeyLight;
        public Transform[] cellTileTransforms = new Transform[9];

        private MaterialPropertyBlock _boardMpb;
        private Texture2D _loadedBackdropTexture;

        public static readonly Dictionary<EnvironmentMasterLineage, EnvironmentLineageMetadata> MasterLineages =
            new Dictionary<EnvironmentMasterLineage, EnvironmentLineageMetadata>
            {
                {
                    EnvironmentMasterLineage.Minagawa_Yoshida_IsometricDiorama,
                    new EnvironmentLineageMetadata
                    {
                        lineageId = EnvironmentMasterLineage.Minagawa_Yoshida_IsometricDiorama,
                        leadMasters = "Hiroshi Minagawa & Akihiko Yoshida",
                        japaneseNames = "皆川 裕史 & 吉田 明彦",
                        foundationalTitles = "Final Fantasy Tactics, Tactics Ogre: Let Us Cling Together, Vagrant Story, Final Fantasy XII",
                        architecturalSignature = "3D isometric diorama stone bastions, rotating voxel-like terraced masonry, dramatic elevation chiaroscuro, weathered medieval church & fortress ruins, warm sepia-ochre vertex lighting.",
                        spatialDesignRules = "Strict 45-degree isometric diamond grid with stepped vertical cliffs; clear edge-bevel stone trims separating each 3x3 cell; deep shadow wells beneath elevated bastions."
                    }
                },
                {
                    EnvironmentMasterLineage.Minaba_Tsukamoto_Kamikokuryo_Storybook,
                    new EnvironmentLineageMetadata
                    {
                        lineageId = EnvironmentMasterLineage.Minaba_Tsukamoto_Kamikokuryo_Storybook,
                        leadMasters = "Hideo Minaba, Koji Tsukamoto & Isamu Kamikokuryo",
                        japaneseNames = "皆葉 英夫, 塚本 哲 & 上国料 勇",
                        foundationalTitles = "Final Fantasy Tactics Advance, Final Fantasy IX, Final Fantasy XII, Granblue Fantasy",
                        architecturalSignature = "Vibrant storybook map artifacts, luminous lawless crystal Jagds, floating sky-citadels, warm painterly cloudscapes, jewel-like map placement icons.",
                        spatialDesignRules = "Sun-drenched storybook palette with high-saturation emerald foliage, golden cobblestone plazas, and glowing aetherial Leyline crystals framing the 3x3 tactical arena."
                    }
                },
                {
                    EnvironmentMasterLineage.Hirata_Izuka_Wada_TacticalCommandGrid,
                    new EnvironmentLineageMetadata
                    {
                        lineageId = EnvironmentMasterLineage.Hirata_Izuka_Wada_TacticalCommandGrid,
                        leadMasters = "Ryo Hirata, Daisuke Izuka & Sachiko Wada",
                        japaneseNames = "平田 亮, 井塚 大介 & 和田 幸子",
                        foundationalTitles = "Advance Wars 1/2/Dual Strike/Days of Ruin, Fire Emblem: Thracia 776 / The Binding Blade / The Sacred Stones",
                        architecturalSignature = "High-readability tactical terrain tiles, unmistakable HQ capture buildings, road/river/mountain grid clarity, dynamic Commanding Officer battle cut-in backgrounds.",
                        spatialDesignRules = "Instantaneous silhouette recognition per tile: crisp border outlines, high-contrast color separation between neutral plains, defensive forts, and central Command HQs."
                    }
                },
                {
                    EnvironmentMasterLineage.Nakayama_IntiCreates_NeoArcadiaCyber,
                    new EnvironmentLineageMetadata
                    {
                        lineageId = EnvironmentMasterLineage.Nakayama_IntiCreates_NeoArcadiaCyber,
                        leadMasters = "Toru Nakayama & Inti Creates Environment Team (Masaya Suzuki / Makoto Yabe)",
                        japaneseNames = "中山 徹 & インティ・クリエイツ背景美術班 (鈴木 雅哉 / 矢部 誠)",
                        foundationalTitles = "Mega Man Zero 1-4 (Rockman Zero), Mega Man ZX, Dragon Marked for Death",
                        architecturalSignature = "Neo Arcadia cyber-cathedrals, beveled titanium-and-obsidian plating, glowing emerald/cyan Cyber-Elf energy conduits, stark black ink shadow recesses, Resistance Base industrial ruins.",
                        spatialDesignRules = "Angular 45-degree beveled metal floor plates linked by pulsing neon data buses; high-contrast cyber-gothic spires framing the perimeter with zero visual clutter on the 3x3 combat deck."
                    }
                }
            };

        public static readonly Dictionary<ArenaBiomeType, ArenaBiomeProfile> BiomeProfiles =
            new Dictionary<ArenaBiomeType, ArenaBiomeProfile>
            {
                {
                    ArenaBiomeType.IvaliceStorybookJagd,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.IvaliceStorybookJagd,
                        biomeTitle = "Ambervale Storybook Jagd",
                        subtitle = "Minaba × Tsukamoto × Kamikokuryo Crystal Enclave",
                        primaryLineage = EnvironmentMasterLineage.Minaba_Tsukamoto_Kamikokuryo_Storybook,
                        resourceBackdropPath = "CardArt/Environments/env_minaba_ivalice_storybook",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 isometric tactical RPG battle board environment in the art style of Hideo Minaba, Koji Tsukamoto, and Isamu Kamikokuryo (Final Fantasy Tactics Advance and Granblue Fantasy), vibrant storybook fantasy diorama, glowing turquoise Leyline crystals, ornate sun-drenched cobblestone 3x3 grid plaza, floating sky-citadel clouds, lush painterly textures",
                        ambientSkyColor = new Color(0.98f, 0.92f, 0.78f),
                        ambientEquatorColor = new Color(0.68f, 0.85f, 0.92f),
                        directionalSunColor = new Color(1.00f, 0.95f, 0.82f),
                        fogDensityAndHeightVector = new Vector4(0.012f, 0.35f, 8.0f, 0.78f),
                        dioramaShaderGrading = new Vector4(0.45f, 0.85f, 0.75f, 0.35f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.LeylineCrystal, CellTerrainModifier.StandardGround, CellTerrainModifier.HighGround,
                            CellTerrainModifier.StandardGround, CellTerrainModifier.CommandHQ,      CellTerrainModifier.StandardGround,
                            CellTerrainModifier.HighGround,     CellTerrainModifier.StandardGround, CellTerrainModifier.LeylineCrystal
                        )
                    }
                },
                {
                    ArenaBiomeType.OrbonneDioramaBastion,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.OrbonneDioramaBastion,
                        biomeTitle = "Orbonne Isometric Bastion",
                        subtitle = "Minagawa × Yoshida Weathered Stone Diorama",
                        primaryLineage = EnvironmentMasterLineage.Minagawa_Yoshida_IsometricDiorama,
                        resourceBackdropPath = "CardArt/Environments/env_minagawa_yoshida_diorama",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 isometric tactical RPG diorama battlefield in the art style of Hiroshi Minagawa and Akihiko Yoshida (Final Fantasy Tactics, Tactics Ogre, Vagrant Story), weathered medieval stone bastion courtyard, carved 3x3 tactical tile masonry, dramatic chiaroscuro torchlight and warm parchment ochre shadows, stepped stone elevation",
                        ambientSkyColor = new Color(0.82f, 0.74f, 0.60f),
                        ambientEquatorColor = new Color(0.48f, 0.42f, 0.35f),
                        directionalSunColor = new Color(0.96f, 0.84f, 0.64f),
                        fogDensityAndHeightVector = new Vector4(0.024f, 0.55f, 6.0f, 0.30f),
                        dioramaShaderGrading = new Vector4(0.95f, 0.25f, 0.82f, 0.15f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.HighGround,     CellTerrainModifier.StandardGround, CellTerrainModifier.HighGround,
                            CellTerrainModifier.ShadowVeil,     CellTerrainModifier.HighGround,     CellTerrainModifier.ShadowVeil,
                            CellTerrainModifier.StandardGround, CellTerrainModifier.CommandHQ,      CellTerrainModifier.StandardGround
                        )
                    }
                },
                {
                    ArenaBiomeType.MacroLandCommandGrid,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.MacroLandCommandGrid,
                        biomeTitle = "Macro Land Command HQ Grid",
                        subtitle = "Hirata × Izuka × Wada Tactical Frontline",
                        primaryLineage = EnvironmentMasterLineage.Hirata_Izuka_Wada_TacticalCommandGrid,
                        resourceBackdropPath = "CardArt/Environments/env_hirata_advance_wars_hq",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 tactical strategy battle board in the signature style of Ryo Hirata, Daisuke Izuka, and Sachiko Wada (Advance Wars Dual Strike and Fire Emblem GBA), high-readability 3x3 tactical terrain grid, central Command HQ capture spire, crisp graphic linework, punchy saturated terrain tiles, fortified bunkers and supply roads",
                        ambientSkyColor = new Color(0.88f, 0.96f, 1.00f),
                        ambientEquatorColor = new Color(0.62f, 0.78f, 0.90f),
                        directionalSunColor = new Color(1.00f, 0.99f, 0.94f),
                        fogDensityAndHeightVector = new Vector4(0.005f, 0.20f, 14.0f, 0.25f),
                        dioramaShaderGrading = new Vector4(0.55f, 0.30f, 1.00f, 0.40f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.CommandHQ,      CellTerrainModifier.StandardGround, CellTerrainModifier.HighGround,
                            CellTerrainModifier.StandardGround, CellTerrainModifier.CommandHQ,      CellTerrainModifier.StandardGround,
                            CellTerrainModifier.HighGround,     CellTerrainModifier.StandardGround, CellTerrainModifier.CommandHQ
                        )
                    }
                },
                {
                    ArenaBiomeType.NeoArcadiaCyberSanctum,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.NeoArcadiaCyberSanctum,
                        biomeTitle = "Neo Arcadia Cyber Sanctum",
                        subtitle = "Nakayama × Inti Creates Beveled Reploid Cathedral",
                        primaryLineage = EnvironmentMasterLineage.Nakayama_IntiCreates_NeoArcadiaCyber,
                        resourceBackdropPath = "CardArt/Environments/env_nakayama_neo_arcadia_mmz",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 isometric cyber-tactical arena in the signature art style of Toru Nakayama and Inti Creates (Mega Man Zero / Rockman Zero and Mega Man ZX), Neo Arcadia cyber-cathedral sanctum, sharp beveled metallic 3x3 floor tiles, glowing cyan and emerald Cyber-Elf energy conduits, stark black shadow blocks, high-tech holographic command pillars",
                        ambientSkyColor = new Color(0.12f, 0.24f, 0.36f),
                        ambientEquatorColor = new Color(0.06f, 0.14f, 0.22f),
                        directionalSunColor = new Color(0.45f, 0.95f, 1.00f),
                        fogDensityAndHeightVector = new Vector4(0.018f, 0.42f, 7.5f, 0.88f),
                        dioramaShaderGrading = new Vector4(0.75f, 0.55f, 0.92f, 1.00f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.CyberConduit,   CellTerrainModifier.ShadowVeil,     CellTerrainModifier.CyberConduit,
                            CellTerrainModifier.StandardGround, CellTerrainModifier.CommandHQ,      CellTerrainModifier.StandardGround,
                            CellTerrainModifier.CyberConduit,   CellTerrainModifier.ShadowVeil,     CellTerrainModifier.CyberConduit
                        )
                    }
                },
                {
                    ArenaBiomeType.ClockworkAetherFoundry,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.ClockworkAetherFoundry,
                        biomeTitle = "Clockwork Aether Foundry",
                        subtitle = "Minaba × Kamikokuryo × Minagawa Chronos Gearworks",
                        primaryLineage = EnvironmentMasterLineage.Minaba_Tsukamoto_Kamikokuryo_Storybook,
                        resourceBackdropPath = "CardArt/Environments/env_minaba_ivalice_storybook",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 isometric steampunk chronomancer arena synthesizing Hideo Minaba, Isamu Kamikokuryo, and Hiroshi Minagawa, brass interlocking gearwork 3x3 tactical platform, amber aether conduits, warm gaslight bloom",
                        ambientSkyColor = new Color(0.92f, 0.72f, 0.45f),
                        ambientEquatorColor = new Color(0.48f, 0.32f, 0.20f),
                        directionalSunColor = new Color(1.00f, 0.78f, 0.42f),
                        fogDensityAndHeightVector = new Vector4(0.020f, 0.48f, 7.0f, 0.68f),
                        dioramaShaderGrading = new Vector4(0.85f, 0.70f, 0.80f, 0.65f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.CyberConduit,   CellTerrainModifier.HighGround,     CellTerrainModifier.LeylineCrystal,
                            CellTerrainModifier.HighGround,     CellTerrainModifier.CommandHQ,      CellTerrainModifier.HighGround,
                            CellTerrainModifier.LeylineCrystal, CellTerrainModifier.HighGround,     CellTerrainModifier.CyberConduit
                        )
                    }
                },
                {
                    ArenaBiomeType.EclipseLunarShrine,
                    new ArenaBiomeProfile
                    {
                        biomeType = ArenaBiomeType.EclipseLunarShrine,
                        biomeTitle = "Eclipse Lunar Shrine",
                        subtitle = "Yoshida × Nakayama × Minaba Astral Sanctum",
                        primaryLineage = EnvironmentMasterLineage.Minagawa_Yoshida_IsometricDiorama,
                        resourceBackdropPath = "CardArt/Environments/env_minagawa_yoshida_diorama",
                        comfyUiEnvironmentPrompt = "masterpiece 3x3 isometric moonlit sacred ruin arena synthesizing Akihiko Yoshida, Toru Nakayama, and Hideo Minaba, obsidian and silver astrolabe 3x3 grid tiles, bioluminescent lunar leylines, deep indigo shadow veils",
                        ambientSkyColor = new Color(0.18f, 0.22f, 0.44f),
                        ambientEquatorColor = new Color(0.10f, 0.12f, 0.28f),
                        directionalSunColor = new Color(0.78f, 0.86f, 1.00f),
                        fogDensityAndHeightVector = new Vector4(0.022f, 0.50f, 6.5f, 0.82f),
                        dioramaShaderGrading = new Vector4(0.80f, 0.75f, 0.85f, 0.72f),
                        gridCells = BuildGridLayout(
                            CellTerrainModifier.ShadowVeil,     CellTerrainModifier.LeylineCrystal, CellTerrainModifier.ShadowVeil,
                            CellTerrainModifier.LeylineCrystal, CellTerrainModifier.CommandHQ,      CellTerrainModifier.LeylineCrystal,
                            CellTerrainModifier.ShadowVeil,     CellTerrainModifier.LeylineCrystal, CellTerrainModifier.ShadowVeil
                        )
                    }
                }
            };

        private static CellTerrainDefinition[] BuildGridLayout(params CellTerrainModifier[] modifiers)
        {
            var cells = new CellTerrainDefinition[9];
            for (int i = 0; i < 9; i++)
            {
                var mod = (modifiers != null && i < modifiers.Length) ? modifiers[i] : CellTerrainModifier.StandardGround;
                cells[i] = CreateCellDefinition(i, mod);
            }
            return cells;
        }

        public static CellTerrainDefinition CreateCellDefinition(int cellIndex, CellTerrainModifier modifier)
        {
            int r = cellIndex / 3;
            int c = cellIndex % 3;
            switch (modifier)
            {
                case CellTerrainModifier.HighGround:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = modifier,
                        elevationOffset = 0.28f,
                        statBonusNESW = new Vector4(1f, 0f, 1f, 0f),
                        tacticalDescription = "High Ground (Minagawa/Yoshida Bastion): +1 Top & +1 Bottom axial elevation defense."
                    };
                case CellTerrainModifier.LeylineCrystal:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = modifier,
                        elevationOffset = 0.08f,
                        statBonusNESW = new Vector4(1f, 1f, 0f, 0f),
                        tacticalDescription = "Leyline Crystal (Minaba/Kamikokuryo Jagd): +1 Top & +1 Right arcane crystal resonance."
                    };
                case CellTerrainModifier.CommandHQ:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = modifier,
                        elevationOffset = 0.18f,
                        statBonusNESW = new Vector4(1f, 1f, 1f, 1f),
                        tacticalDescription = "Command HQ (Hirata/Izuka/Wada Capture Point): +1 All Sides tactical command aura."
                    };
                case CellTerrainModifier.CyberConduit:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = modifier,
                        elevationOffset = 0.05f,
                        statBonusNESW = new Vector4(0f, 1f, 0f, 1f),
                        tacticalDescription = "Cyber Conduit (Nakayama/Inti Creates Neo Arcadia Bus): +1 Left & +1 Right lateral surge."
                    };
                case CellTerrainModifier.ShadowVeil:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = modifier,
                        elevationOffset = -0.04f,
                        statBonusNESW = new Vector4(0f, 0f, 1f, 1f),
                        tacticalDescription = "Shadow Veil (Vagrant Story / Resistance Ruin): +1 Bottom & +1 Left ambush refraction."
                    };
                default:
                    return new CellTerrainDefinition
                    {
                        cellIndex = cellIndex,
                        row = r,
                        col = c,
                        modifier = CellTerrainModifier.StandardGround,
                        elevationOffset = 0f,
                        statBonusNESW = Vector4.zero,
                        tacticalDescription = "Standard Ground: Neutral tactical tile."
                    };
            }
        }

        private void Awake()
        {
            _boardMpb = new MaterialPropertyBlock();
            ApplyBiome(activeBiome);
        }

        public static ArenaBiomeProfile GetBiomeProfile(ArenaBiomeType biome) =>
            BiomeProfiles.TryGetValue(biome, out var profile)
                ? profile
                : BiomeProfiles[ArenaBiomeType.IvaliceStorybookJagd];

        public CellTerrainDefinition GetCellTerrain(int row, int col)
        {
            int idx = Mathf.Clamp(row * 3 + col, 0, 8);
            var profile = GetBiomeProfile(activeBiome);
            return profile.gridCells[idx];
        }

        /// <summary>
        /// Dynamically loads the 1024x768 3x3 Arena Backdrop from Unity Resources, updates ambient/directional
        /// lighting & fog shader vectors, and adjusts the 3x3 diorama cell elevation offsets.
        /// </summary>
        public void ApplyBiome(ArenaBiomeType biome)
        {
            activeBiome = biome;
            var profile = GetBiomeProfile(biome);

            // 1. Update Global Environment & Shader Grading Vectors
            Shader.SetGlobalColor(PropAmbientSky, profile.ambientSkyColor);
            Shader.SetGlobalColor(PropAmbientEquator, profile.ambientEquatorColor);
            Shader.SetGlobalColor(PropSunColor, profile.directionalSunColor);
            Shader.SetGlobalVector(PropFogVector, profile.fogDensityAndHeightVector);
            Shader.SetGlobalVector(PropDioramaGrading, profile.dioramaShaderGrading);

            RenderSettings.ambientSkyColor = profile.ambientSkyColor;
            RenderSettings.ambientEquatorColor = profile.ambientEquatorColor;

            if (directionalKeyLight != null)
            {
                directionalKeyLight.color = profile.directionalSunColor;
            }

            // 2. Dynamically Load 3x3 Arena Backdrop Texture from Resources
            if (!string.IsNullOrEmpty(profile.resourceBackdropPath))
            {
                _loadedBackdropTexture = Resources.Load<Texture2D>(profile.resourceBackdropPath);
                if (_loadedBackdropTexture != null)
                {
                    if (boardBackdropRenderer != null)
                    {
                        _boardMpb ??= new MaterialPropertyBlock();
                        boardBackdropRenderer.GetPropertyBlock(_boardMpb);
                        _boardMpb.SetTexture(PropBackdropTex, _loadedBackdropTexture);
                        boardBackdropRenderer.SetPropertyBlock(_boardMpb);
                    }

                    if (boardBackdropUIImage != null)
                    {
                        boardBackdropUIImage.texture = _loadedBackdropTexture;
                    }
                }
            }

            // 3. Apply Diorama Elevation Offsets to the 3x3 Cell Transforms
            if (cellTileTransforms != null)
            {
                for (int i = 0; i < Mathf.Min(cellTileTransforms.Length, profile.gridCells.Length); i++)
                {
                    if (cellTileTransforms[i] != null)
                    {
                        Vector3 pos = cellTileTransforms[i].localPosition;
                        pos.y = profile.gridCells[i].elevationOffset;
                        cellTileTransforms[i].localPosition = pos;
                    }
                }
            }
        }
    }
}
