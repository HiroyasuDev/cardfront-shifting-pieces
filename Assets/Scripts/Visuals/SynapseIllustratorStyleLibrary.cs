using System;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.Visuals
{
    public enum MasterIllustratorStyle
    {
        TacticalSynthesis_Default          = 0, // Unified blend of all 9 Character & Environmental Tactical Masters
        RyomaIto_FFTA                      = 1, // Ryoma Ito (Final Fantasy Tactics Advance): Dynamic stylized proportions, vibrant watercolor cel-wash
        AkihikoYoshida_FFT_Judge           = 2, // Akihiko Yoshida (FFT / FFTA Judges / Tactics Ogre): Crosshatched sepia/ochre ink, ornate Judge armor filigree
        HideoMinaba_Storybook              = 3, // Hideo Minaba (FFTA Art Director / FFIX / Granblue): Storybook fantasy worldbuilding, lush painterly sky-citadels
        RyoHirata_AdvanceWars_FE           = 4, // Ryo Hirata (Advance Wars 1/2/Dual Strike/Days of Ruin, Fire Emblem GBA): Crisp CO/unit linework, bold faction color-coding
        ToruNakayama_MegaManZero_ZX        = 5, // Toru Nakayama (Mega Man Zero / ZX / Dragon Marked for Death / Inti Creates): Bold shapes, beveled cyber-edges, expressive large eyes
        HiroshiMinagawa_IvaliceIsometric   = 6, // Hiroshi Minagawa & Quest/Square Ivalice Team (FFT / Tactics Ogre / Vagrant Story): Terraced isometric stone/timber battlefields
        IsamuKamikokuryo_SkystoneCitadel   = 7, // Isamu Kamikokuryo (FFXII / Ivalice Architecture): Sun-bleached limestone arches, brass airship docks, magicite conduits
        HirooIsono_ManaBotanicalSanctuary  = 8,  // Hiroo Isono & Kouichi Ishii (Secret of Mana / Heroes of Mana): Lush multi-layered emerald canopy & world-tree biomes
        IntiCreates_NeoArcadiaCyberRuins   = 9,  // Makoto Yabe & Inti Creates Environment Team (Mega Man Zero / ZX): High-contrast cyber-cathedrals & neon Reploid ruins
        YojiShinkawa_TacticalMechaInk      = 10, // Yoji Shinkawa (Metal Gear Solid / Zone of the Enders / Kojima Productions): Calligraphic sumi-e ink brushwork & tactical mecha
        KazumaKaneko_OccultCyber           = 11, // Kazuma Kaneko (Shin Megami Tensei / Persona / ZOE 2nd Runner): High-contrast porcelain occult-cyber anatomy & geometric sigils
        TeradaSuzuki_KineticSumi           = 12  // Katsuya Terada & Yasushi Suzuki (Ikaruga / Sin & Punishment / Blood): Dense biomechanical linework & dramatic sumi-wash chiaroscuro
    }

    [Serializable]
    public class LongitudinalEraEntry
    {
        public string eraYears;
        public string projectTitle;
        public string studioOrPublisher;
        public string role;
        public string morphologicalSignature;
    }

    [Serializable]
    public class IllustratorStyleProfile
    {
        public MasterIllustratorStyle styleId;
        public string artistName;
        public string japaneseName;
        public string signatureWorks;
        public string visualCharacteristics;
        public string comfyUiPromptTags;
        public string comfyUiNegativeTags;
        public List<LongitudinalEraEntry> longitudinalTimeline = new List<LongitudinalEraEntry>();

        // Shader & Post-Processing Grading Parameters
        public Color paperWarmthTint;
        public float inkOutlineThickness;
        public float crosshatchIntensity;
        public float storybookBloom;
        public float colorSaturation;
        public float bevelHighlightSharpness;
    }

    /// <summary>
    /// Clean-room Proprietary 5-Master Longitudinal Tactical Illustrator Style Library for Synapse.TcgEngine.
    /// Encodes the longitudinal career evolution, visual DNA, shader grading parameters, and ComfyUI RTX 4080
    /// conditioning prompts for the five foundational masters of tactical RPG, strategy & cyber-action art:
    /// 1. Ryoma Ito (Final Fantasy Tactics Advance Character Designer)
    /// 2. Akihiko Yoshida (Final Fantasy Tactics / FFTA Artistic Supervisor & Judge Illustrator)
    /// 3. Hideo Minaba (Final Fantasy Tactics Advance Art Director)
    /// 4. Ryo Hirata (Advance Wars 1/2/Dual Strike/Days of Ruin & Fire Emblem GBA Main Artist)
    /// 5. Toru Nakayama (Mega Man Zero / Rockman Zero, Mega Man ZX, Speed Power Gunbike, Dragon Marked for Death)
    /// </summary>
    public static class SynapseIllustratorStyleLibrary
    {
        public static readonly Dictionary<MasterIllustratorStyle, IllustratorStyleProfile> Profiles =
            new Dictionary<MasterIllustratorStyle, IllustratorStyleProfile>
            {
                {
                    MasterIllustratorStyle.RyomaIto_FFTA,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.RyomaIto_FFTA,
                        artistName = "Ryōma Itō",
                        japaneseName = "伊藤 龍馬",
                        signatureWorks = "Final Fantasy Tactics Advance, FFTA2: Grimoire of the Rift, FFXII: Revenant Wings",
                        visualCharacteristics = "Lighter stylized proportions, tapered gauntlets and boots, dynamic expressive silhouettes, vibrant watercolor cel-shading over crisp ink lines.",
                        comfyUiPromptTags = "Final Fantasy Tactics Advance official character illustration, Ryoma Ito morphological lineage, stylized dynamic proportions, vibrant watercolor cel-wash, expressive silhouette, clean tapered armor and cloth folds, Ivalice tactical fantasy",
                        comfyUiNegativeTags = "photorealistic, 3d render, muddy colors, stiff pose",
                        paperWarmthTint = new Color(1.00f, 0.97f, 0.92f),
                        inkOutlineThickness = 1.25f,
                        crosshatchIntensity = 0.20f,
                        storybookBloom = 0.45f,
                        colorSaturation = 1.18f,
                        bevelHighlightSharpness = 0.35f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1997-2000", projectTitle = "Final Fantasy Tactics / Vagrant Story", studioOrPublisher = "Square", role = "Character & Event Artist", morphologicalSignature = "Early Ivalice apprentice linework under Yoshida" },
                            new LongitudinalEraEntry { eraYears = "2003", projectTitle = "Final Fantasy Tactics Advance", studioOrPublisher = "Square Enix", role = "Main Character Designer", morphologicalSignature = "Lighter stylized proportions, vibrant storybook cel-watercolor wash, dynamic job silhouettes" },
                            new LongitudinalEraEntry { eraYears = "2007-2008", projectTitle = "FFXII: Revenant Wings & FFTA2: Grimoire of the Rift", studioOrPublisher = "Square Enix", role = "Main Character Designer", morphologicalSignature = "High-density ornamental costume layering, expressive facial framing, rich jewel-tone gradients" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.AkihikoYoshida_FFT_Judge,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.AkihikoYoshida_FFT_Judge,
                        artistName = "Akihiko Yoshida",
                        japaneseName = "吉田 明彦",
                        signatureWorks = "Final Fantasy Tactics, FFTA Artistic Supervisor (Judge Illustrations), Tactics Ogre, Vagrant Story",
                        visualCharacteristics = "Masterful pen-and-ink crosshatching, warm parchment sepia and ochre undertones, intricate Judge armor filigree, sculptural drapery, noble solemn gravitas.",
                        comfyUiPromptTags = "Final Fantasy Tactics and FFTA Judge official illustration, Akihiko Yoshida morphological lineage, intricate pen and ink crosshatching, warm parchment sepia and gold palette, ornate medieval-tactical Judge armor filigree, museum-grade fantasy illustration",
                        comfyUiNegativeTags = "neon, flat vector, plastic skin, oversaturated",
                        paperWarmthTint = new Color(0.96f, 0.90f, 0.78f),
                        inkOutlineThickness = 1.40f,
                        crosshatchIntensity = 0.85f,
                        storybookBloom = 0.25f,
                        colorSaturation = 0.88f,
                        bevelHighlightSharpness = 0.50f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1995-1997", projectTitle = "Tactics Ogre & Final Fantasy Tactics", studioOrPublisher = "Quest / Square", role = "Main Character Designer & Art Director", morphologicalSignature = "Nose-less stylized medieval portraiture, dense ink crosshatching, warm parchment ochre palette" },
                            new LongitudinalEraEntry { eraYears = "2000-2003", projectTitle = "Vagrant Story & Final Fantasy Tactics Advance", studioOrPublisher = "Square Enix", role = "Artistic Supervisor & Judge Illustrator", morphologicalSignature = "Monumental baroque Judge armor filigree, sculptural anatomical shading, dramatic chiaroscuro" },
                            new LongitudinalEraEntry { eraYears = "2006-2017", projectTitle = "Final Fantasy XII, Bravely Default, NieR: Automata", studioOrPublisher = "Square Enix / CyDesignation", role = "Lead Character Designer", morphologicalSignature = "Painterly soft pencil-and-wash texture, ethereal gothic-machina silhouettes" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.HideoMinaba_Storybook,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.HideoMinaba_Storybook,
                        artistName = "Hideo Minaba",
                        japaneseName = "皆葉 英夫",
                        signatureWorks = "Final Fantasy Tactics Advance (Art Director), Final Fantasy IX, Granblue Fantasy",
                        visualCharacteristics = "Vibrant storybook-like direction, richly textured architectural environments, painterly sky-citadels, warm atmospheric light and ornamental framing.",
                        comfyUiPromptTags = "art direction by Hideo Minaba, Final Fantasy Tactics Advance and Granblue Fantasy storybook illustration, lush painterly fantasy architecture, vibrant atmospheric light, ornate decorative framing, rich environmental storytelling",
                        comfyUiNegativeTags = "sterile background, plain void, harsh digital edges",
                        paperWarmthTint = new Color(0.99f, 0.95f, 0.88f),
                        inkOutlineThickness = 1.00f,
                        crosshatchIntensity = 0.45f,
                        storybookBloom = 0.75f,
                        colorSaturation = 1.12f,
                        bevelHighlightSharpness = 0.30f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1994-2000", projectTitle = "Final Fantasy VI & Final Fantasy IX", studioOrPublisher = "Square", role = "Art Director", morphologicalSignature = "Steampunk-storybook synthesis, warm nostalgic architectural silhouettes" },
                            new LongitudinalEraEntry { eraYears = "2003", projectTitle = "Final Fantasy Tactics Advance", studioOrPublisher = "Square Enix", role = "Art Director", morphologicalSignature = "Vibrant isometric storybook world transformation, jewel-like terrain & crystal enclaves" },
                            new LongitudinalEraEntry { eraYears = "2014-2026", projectTitle = "Granblue Fantasy", studioOrPublisher = "Cygames / Designation", role = "Lead Art Director", morphologicalSignature = "Lush sky-farer painterly clouds, gilded ornamental card framing, atmospheric bloom" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.RyoHirata_AdvanceWars_FE,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.RyoHirata_AdvanceWars_FE,
                        artistName = "Ryo Hirata",
                        japaneseName = "平田 亮",
                        signatureWorks = "Super Famicom Wars, Advance Wars, Advance Wars 2: Black Hole Rising, Advance Wars: Dual Strike, Advance Wars: Days of Ruin, Fire Emblem: Thracia 776 / The Binding Blade / The Sacred Stones",
                        visualCharacteristics = "Iconic Intelligent Systems Commanding Officer (CO) & tactical battle unit design, bold graphic linework, high-contrast cel shading, unmistakable faction silhouette readability.",
                        comfyUiPromptTags = "Intelligent Systems Advance Wars Dual Strike and Fire Emblem Sacred Stones official character and battle unit art, Ryo Hirata morphological lineage, bold crisp graphic linework, high-contrast cel shading, punchy tactical faction colors, dynamic battle cut-in composition",
                        comfyUiNegativeTags = "blurry, washed out, indistinct silhouette, low contrast",
                        paperWarmthTint = new Color(1.00f, 1.00f, 1.00f),
                        inkOutlineThickness = 1.65f,
                        crosshatchIntensity = 0.10f,
                        storybookBloom = 0.20f,
                        colorSaturation = 1.28f,
                        bevelHighlightSharpness = 0.65f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1998-2004", projectTitle = "Super Famicom Wars & Fire Emblem (Thracia 776, The Binding Blade, The Sacred Stones)", studioOrPublisher = "Intelligent Systems", role = "Character, Map & Battle Animation Designer", morphologicalSignature = "Crisp GBA tactical sprite-to-portrait readability, noble fantasy armor trim" },
                            new LongitudinalEraEntry { eraYears = "2001-2005", projectTitle = "Advance Wars, Advance Wars 2: Black Hole Rising, Advance Wars: Dual Strike", studioOrPublisher = "Intelligent Systems", role = "Main Artist & Character/Unit Designer", morphologicalSignature = "Iconic CO expressive silhouettes, bold graphic linework, punchy saturated faction color-coding" },
                            new LongitudinalEraEntry { eraYears = "2008", projectTitle = "Advance Wars: Days of Ruin", studioOrPublisher = "Intelligent Systems", role = "Battle Unit Designer", morphologicalSignature = "Gritty post-apocalyptic mechanized unit geometry, sharp industrial bevels" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.ToruNakayama_MegaManZero_ZX,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.ToruNakayama_MegaManZero_ZX,
                        artistName = "Toru Nakayama",
                        japaneseName = "中山 徹",
                        signatureWorks = "Mega Man Zero 1-4 (Rockman Zero), Mega Man ZX, Mega Man Zero/ZX Legacy Collection, Speed Power Gunbike, Dragon Marked for Death (Inti Creates)",
                        visualCharacteristics = "Distinct stylized cyber-fantasy aesthetic featuring bold triangular shapes, sharp beveled armor edges, dramatic black shadow blocks, luminous energy blades, and characters with noticeably larger expressive eyes.",
                        comfyUiPromptTags = "Rockman Zero / Mega Man Zero and Mega Man ZX official illustration, Inti Creates Toru Nakayama morphological lineage, sleek stylized cyber-armor with sharp beveled edges, bold triangular silhouette shapes, noticeably larger expressive eyes, stark black shadow blocks with glowing neon cyber-elf highlights",
                        comfyUiNegativeTags = "bulky clunky proportions, dull flat lighting, photorealistic, blurry",
                        paperWarmthTint = new Color(0.95f, 0.98f, 1.00f),
                        inkOutlineThickness = 1.55f,
                        crosshatchIntensity = 0.15f,
                        storybookBloom = 0.60f,
                        colorSaturation = 1.24f,
                        bevelHighlightSharpness = 0.95f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1998", projectTitle = "Speed Power Gunbike", studioOrPublisher = "Inti Creates", role = "Character & Mecha Designer", morphologicalSignature = "Early high-speed angular mecha-suit beveling and bold graphic visor shapes" },
                            new LongitudinalEraEntry { eraYears = "2002-2005", projectTitle = "Mega Man Zero 1-4 (Rockman Zero)", studioOrPublisher = "Inti Creates / Capcom", role = "Main Character Designer, Promotional & Package Illustrator", morphologicalSignature = "Sleek Reploid anatomy, bold triangular silhouettes, beveled armor edges, large expressive eyes, stark black ink shadows with luminous Z-Saber highlights" },
                            new LongitudinalEraEntry { eraYears = "2006-2020", projectTitle = "Mega Man ZX, Dragon Marked for Death, Mega Man Zero/ZX Legacy Collection", studioOrPublisher = "Inti Creates / Capcom", role = "Lead Illustrator & Character Designer", morphologicalSignature = "Hybrid dark-fantasy & cybernetic Biometal aesthetics, painterly rim-lit promotional compositions" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.HiroshiMinagawa_IvaliceIsometric,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.HiroshiMinagawa_IvaliceIsometric,
                        artistName = "Hiroshi Minagawa & Ivalice Diorama Team",
                        japaneseName = "皆川 裕史 (Quest / Ivalice Alliance)",
                        signatureWorks = "Tactics Ogre, Final Fantasy Tactics, Vagrant Story, Final Fantasy Tactics Advance / FFXII",
                        visualCharacteristics = "Multi-elevation terraced isometric stone and timber battlefields, rotating miniature diorama lighting, crisp tactical grid readability blended with weathered medieval masonry.",
                        comfyUiPromptTags = "isometric tactical RPG battlefield diorama, Hiroshi Minagawa and Final Fantasy Tactics / Tactics Ogre environment lineage, terraced stone masonry, medieval timber roofs, warm directional sunlight, crisp elevation cliffs, hand-painted miniature diorama aesthetic",
                        comfyUiNegativeTags = "flat 2d plane, blurry perspective, modern asphalt, lowres, text, watermark",
                        paperWarmthTint = new Color(0.97f, 0.92f, 0.82f),
                        inkOutlineThickness = 1.30f,
                        crosshatchIntensity = 0.65f,
                        storybookBloom = 0.40f,
                        colorSaturation = 0.98f,
                        bevelHighlightSharpness = 0.60f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1993-1995", projectTitle = "Ogre Battle & Tactics Ogre: Let Us Cling Together", studioOrPublisher = "Quest", role = "Art Director & Isometric Map Designer", morphologicalSignature = "Stepped isometric elevation tiles, hand-crafted pixel masonry & water shaders" },
                            new LongitudinalEraEntry { eraYears = "1997-2000", projectTitle = "Final Fantasy Tactics & Vagrant Story", studioOrPublisher = "Square", role = "Art Director & Real-Time 3D Diorama Lead", morphologicalSignature = "Rotatable 3D isometric tactical dioramas, warm vertex-lit stone cathedrals & weathered fortresses" },
                            new LongitudinalEraEntry { eraYears = "2006-2022", projectTitle = "Final Fantasy XII & Tactics Ogre: Reborn", studioOrPublisher = "Square Enix", role = "Director / Visual Supervisor", morphologicalSignature = "High-definition tactical readability with museum-grade Ivalice architectural texture" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.IsamuKamikokuryo_SkystoneCitadel,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.IsamuKamikokuryo_SkystoneCitadel,
                        artistName = "Isamu Kamikokuryo",
                        japaneseName = "上国料 勇",
                        signatureWorks = "Final Fantasy XII (Ivalice Environmental & Airship Art Director), Final Fantasy X, Final Fantasy XIII",
                        visualCharacteristics = "Monumental sun-bleached Mediterranean-Ivalice limestone arches, brass airship hangars, glowing blue skystone/magicite conduits, sweeping atmospheric perspective.",
                        comfyUiPromptTags = "environmental concept art and battle arena, Isamu Kamikokuryo Final Fantasy XII Ivalice architectural lineage, monumental sun-bleached limestone arches, ornate brass airship filigree, glowing cyan magicite skystone crystals, sweeping atmospheric depth",
                        comfyUiNegativeTags = "cramped interior, muddy lighting, flat colors, lowres, text, watermark",
                        paperWarmthTint = new Color(0.99f, 0.96f, 0.90f),
                        inkOutlineThickness = 1.05f,
                        crosshatchIntensity = 0.35f,
                        storybookBloom = 0.70f,
                        colorSaturation = 1.14f,
                        bevelHighlightSharpness = 0.72f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1999-2001", projectTitle = "Final Fantasy X", studioOrPublisher = "Square", role = "Environmental Concept Artist", morphologicalSignature = "Luminous aquatic-fantasy ruins and organic temple geometry" },
                            new LongitudinalEraEntry { eraYears = "2003-2006", projectTitle = "Final Fantasy XII", studioOrPublisher = "Square Enix", role = "Art Director (Ivalice Environments & Airships)", morphologicalSignature = "Rabanastre/Bhujerba sun-drenched limestone citadels, brass airship hulls & magicite energy cores" },
                            new LongitudinalEraEntry { eraYears = "2009-2016", projectTitle = "Final Fantasy XIII & XV", studioOrPublisher = "Square Enix", role = "Art Director", morphologicalSignature = "Crystalline sci-fi cathedrals and painterly oil-on-canvas atmospheric vistas" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.HirooIsono_ManaBotanicalSanctuary,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.HirooIsono_ManaBotanicalSanctuary,
                        artistName = "Hiroo Isono & Kouichi Ishii (Mana World Team)",
                        japaneseName = "磯野 宏夫 × 石井 浩一",
                        signatureWorks = "Secret of Mana, Trials of Mana, Legend of Mana, Heroes of Mana (Environmental & World Art)",
                        visualCharacteristics = "Dense multi-layered botanical canopies, sacred World Tree roots, bioluminescent emerald/amber forest light shafts, serene storybook nature sanctuaries.",
                        comfyUiPromptTags = "masterpiece environmental illustration, Hiroo Isono and Secret of Mana / Heroes of Mana botanical world art lineage, colossal ancient Mana Tree roots, lush multi-layered emerald botanical canopy, dappled golden sunbeams, bioluminescent forest shrine",
                        comfyUiNegativeTags = "barren desert, industrial grey, flat lighting, lowres, text, watermark",
                        paperWarmthTint = new Color(0.95f, 1.00f, 0.93f),
                        inkOutlineThickness = 1.10f,
                        crosshatchIntensity = 0.30f,
                        storybookBloom = 0.80f,
                        colorSaturation = 1.25f,
                        bevelHighlightSharpness = 0.40f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1993-1995", projectTitle = "Secret of Mana & Trials of Mana (Seiken Densetsu 2 & 3)", studioOrPublisher = "Square", role = "Principal Environmental Illustrator & World Creator", morphologicalSignature = "Towering botanical forest cathedrals, rich emerald/teal/amber storybook foliage" },
                            new LongitudinalEraEntry { eraYears = "1999-2007", projectTitle = "Legend of Mana & Heroes of Mana", studioOrPublisher = "Square Enix", role = "World & Tactical Map Art Direction", morphologicalSignature = "Watercolor storybook tactical biomes and organic root-carved sanctuaries" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.IntiCreates_NeoArcadiaCyberRuins,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.IntiCreates_NeoArcadiaCyberRuins,
                        artistName = "Makoto Yabe & Inti Creates Environment Team",
                        japaneseName = "矢部 誠 / インティ・クリエイツ背景班",
                        signatureWorks = "Mega Man Zero 1-4 (Neo Arcadia & Resistance Base Environments), Mega Man ZX, Azure Striker Gunvolt",
                        visualCharacteristics = "Sleek Neo-Arcadia cyber-utopian spires contrasted with battle-scarred Reploid resistance ruins, glowing neon cyan/crimson energy conduits, sharp geometric parallax architecture.",
                        comfyUiPromptTags = "cyber-fantasy tactical battlefield environment, Mega Man Zero (Neo Arcadia) and Mega Man ZX Inti Creates architectural lineage, sleek beveled metallic spires, glowing cyan cyber-elf energy conduits, stark black shadow contrast, dramatic sci-fi cathedral lighting",
                        comfyUiNegativeTags = "rustic medieval wood, muddy brown, blurry edges, lowres, text, watermark",
                        paperWarmthTint = new Color(0.92f, 0.97f, 1.00f),
                        inkOutlineThickness = 1.50f,
                        crosshatchIntensity = 0.15f,
                        storybookBloom = 0.65f,
                        colorSaturation = 1.22f,
                        bevelHighlightSharpness = 0.92f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "2002-2005", projectTitle = "Mega Man Zero 1-4 (Rockman Zero)", studioOrPublisher = "Inti Creates / Capcom", role = "Background & Stage Environment Design Team", morphologicalSignature = "Neo Arcadia sacred cyber-spires, glowing holographic circuit glyphs, high-contrast crimson/teal lighting" },
                            new LongitudinalEraEntry { eraYears = "2006-2020", projectTitle = "Mega Man ZX & Dragon Marked for Death", studioOrPublisher = "Inti Creates", role = "Environmental Art Team", morphologicalSignature = "Multi-plane parallax cyber-ruins and biomechanical temple interiors" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.YojiShinkawa_TacticalMechaInk,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.YojiShinkawa_TacticalMechaInk,
                        artistName = "Yoji Shinkawa",
                        japaneseName = "新川 洋司 (Kojima Productions)",
                        signatureWorks = "Metal Gear Solid 1-5, Zone of the Enders (Orbital Frame Jehuty/Anubis), Death Stranding",
                        visualCharacteristics = "Expressive Pentel brush-pen sumi-e ink strokes, stark negative space, dry-brush splatter, razor-sharp tactical stealth and Orbital Frame mecha silhouettes.",
                        comfyUiPromptTags = "masterpiece official illustration, Yoji Shinkawa Metal Gear Solid and Zone of the Enders morphological lineage, expressive calligraphic sumi-e ink brushwork, dynamic dry-brush strokes, stark negative space, olive drab and cyan accent wash, tactical mecha silhouette",
                        comfyUiNegativeTags = "smooth airbrush, plastic 3d render, cluttered background, lowres, text, watermark",
                        paperWarmthTint = new Color(0.96f, 0.95f, 0.90f),
                        inkOutlineThickness = 1.75f,
                        crosshatchIntensity = 0.78f,
                        storybookBloom = 0.30f,
                        colorSaturation = 0.85f,
                        bevelHighlightSharpness = 0.88f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1998-2004", projectTitle = "Metal Gear Solid 1-3 & Zone of the Enders", studioOrPublisher = "Konami / KCEJ", role = "Lead Character & Mechanical Designer", morphologicalSignature = "Iconic Pentel brush-pen sumi-e strokes, high-contrast negative space, sleek Orbital Frame geometry" },
                            new LongitudinalEraEntry { eraYears = "2008-2026", projectTitle = "Metal Gear Solid 4/V & Death Stranding", studioOrPublisher = "Kojima Productions", role = "Art Director", morphologicalSignature = "Painterly acrylic-and-ink hybrid tactical hardware and biomechanical silhouette design" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.KazumaKaneko_OccultCyber,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.KazumaKaneko_OccultCyber,
                        artistName = "Kazuma Kaneko",
                        japaneseName = "金子 一馬 (Atlus / Megaten)",
                        signatureWorks = "Shin Megami Tensei I-III: Nocturne, Persona 1-2, Devil Summoner, Zone of the Enders: The 2nd Runner",
                        visualCharacteristics = "Porcelain-smooth mannequin-like cyber-occult anatomy, stark black upper-lip and eye shading, geometric esoteric sigils, eerie clinical cel-gradient lighting.",
                        comfyUiPromptTags = "masterpiece official illustration, Kazuma Kaneko Shin Megami Tensei III Nocturne and Devil Summoner morphological lineage, porcelain-smooth cyber-occult character and demon design, stark black ink shadow blocks, geometric esoteric sigils, clinical high-contrast cel shading",
                        comfyUiNegativeTags = "soft pastel, cute chibi, messy sketch lines, lowres, text, watermark",
                        paperWarmthTint = new Color(0.94f, 0.95f, 0.98f),
                        inkOutlineThickness = 1.50f,
                        crosshatchIntensity = 0.20f,
                        storybookBloom = 0.45f,
                        colorSaturation = 1.08f,
                        bevelHighlightSharpness = 0.90f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "1992-1999", projectTitle = "Shin Megami Tensei I/II, Devil Summoner, Persona 1/2", studioOrPublisher = "Atlus", role = "Primary Demon & Character Designer", morphologicalSignature = "Cyberpunk-meets-mythology iconography, crisp ink contours, high-fashion occult silhouettes" },
                            new LongitudinalEraEntry { eraYears = "2001-2008", projectTitle = "SMT III: Nocturne, Digital Devil Saga, ZOE: The 2nd Runner", studioOrPublisher = "Atlus / Konami", role = "Creative Director & World Designer", morphologicalSignature = "Luminous geometric tattoos, clinical porcelain shading, surreal biomechanical forms" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.TeradaSuzuki_KineticSumi,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.TeradaSuzuki_KineticSumi,
                        artistName = "Katsuya Terada & Yasushi Suzuki",
                        japaneseName = "寺田 克也 × 鈴木 康士 (Treasure / Ikaruga Lineage)",
                        signatureWorks = "Ikaruga, Sin & Punishment, Blood: The Last Vampire, Busin 0: Wizardry Alternative",
                        visualCharacteristics = "Dense organic-biomechanical linework, dramatic polarity black/white sumi-wash chiaroscuro, visceral kinetic energy arcs.",
                        comfyUiPromptTags = "masterpiece official illustration, Yasushi Suzuki (Ikaruga and Sin and Punishment) and Katsuya Terada morphological lineage, dense biomechanical linework, dramatic black and white polarity energy chiaroscuro, visceral kinetic brush strokes",
                        comfyUiNegativeTags = "flat cartoon, washed out, static pose, lowres, text, watermark",
                        paperWarmthTint = new Color(0.97f, 0.94f, 0.89f),
                        inkOutlineThickness = 1.60f,
                        crosshatchIntensity = 0.82f,
                        storybookBloom = 0.58f,
                        colorSaturation = 1.12f,
                        bevelHighlightSharpness = 0.84f,
                        longitudinalTimeline = new List<LongitudinalEraEntry>
                        {
                            new LongitudinalEraEntry { eraYears = "2000-2004", projectTitle = "Sin & Punishment, Ikaruga, Blood: The Last Vampire", studioOrPublisher = "Treasure / Production I.G", role = "Lead Illustrator & Concept Designer", morphologicalSignature = "Dual-polarity black/white energy contrast, hyper-detailed organic-mechanical ink hatching" },
                            new LongitudinalEraEntry { eraYears = "2005-2026", projectTitle = "Sin & Punishment: Star Successor & Modern Dark-Sci-Fi Key Art", studioOrPublisher = "Treasure / Independent", role = "Principal Illustrator", morphologicalSignature = "Explosive painterly composition with razor-sharp ink calligraphy" }
                        }
                    }
                },
                {
                    MasterIllustratorStyle.TacticalSynthesis_Default,
                    new IllustratorStyleProfile
                    {
                        styleId = MasterIllustratorStyle.TacticalSynthesis_Default,
                        artistName = "Frontier Legends 5-Master Synthesis (Itō × Yoshida × Minaba × Hirata × Nakayama)",
                        japaneseName = "伊藤龍馬 × 吉田明彦 × 皆葉英夫 × 平田亮 × 中山徹",
                        signatureWorks = "PROJECT CF: Card Front Tactics — Frontier Legends & CardCraft",
                        visualCharacteristics = "Synthesizes Ryōma Itō's stylized FFTA silhouettes, Akihiko Yoshida's Judge filigree & crosshatching, Hideo Minaba's storybook lighting, Ryo Hirata's Advance Wars / Fire Emblem unit clarity, and Toru Nakayama's Mega Man Zero beveled cyber-armor & expressive eyes.",
                        comfyUiPromptTags = "masterpiece tactical RPG card illustration synthesizing Ryoma Ito (FFTA character design), Akihiko Yoshida (FFT Judge armor filigree), Hideo Minaba (storybook art direction), Ryo Hirata (Advance Wars & Fire Emblem unit silhouette), and Toru Nakayama (Mega Man Zero sleek beveled cyber-armor and expressive eyes)",
                        comfyUiNegativeTags = "lowres, bad anatomy, text, watermark, blurry, deformed",
                        paperWarmthTint = new Color(0.98f, 0.96f, 0.92f),
                        inkOutlineThickness = 1.40f,
                        crosshatchIntensity = 0.45f,
                        storybookBloom = 0.55f,
                        colorSaturation = 1.18f,
                        bevelHighlightSharpness = 0.70f
                    }
                }
            };

        public static IllustratorStyleProfile GetProfile(MasterIllustratorStyle style) =>
            Profiles.TryGetValue(style, out var p) ? p : Profiles[MasterIllustratorStyle.TacticalSynthesis_Default];
    }
}
