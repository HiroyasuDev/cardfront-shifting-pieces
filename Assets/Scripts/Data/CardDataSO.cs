using System;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.Data
{
    [Flags]
    public enum CardTheme
    {
        None      = 0,
        Magic     = 1 << 0,
        Tech      = 1 << 1,
        Divine    = 1 << 2,
        Shadow    = 1 << 3,
        Nature    = 1 << 4,
        Cosmic    = 1 << 5,
        Steampunk = 1 << 6,
        Fire      = 1 << 7,
        Stealth   = 1 << 8,
        Lunar     = 1 << 9,
        Creative  = 1 << 10
    }

    public enum SpecialAbilityType
    {
        None,
        Teleport,        // 1. Mystic Mage (Arcane Enigma): Once per game, move to any unoccupied space.
        Charge,          // 2. Mech Knight (Iron Vanguard): On capture, make an immediate second move to an empty space.
        HealingAura,     // 3. Celestial Guardian (Divine Sentinel): End of turn, restore +1 strength to adjacent friendly cards.
        Vanish,          // 4. Shadow Assassin (Midnight Eclipse): Once per game, immune to capture for 1 turn.
        ElementalBurst,  // 5. Elemental Sprite (Nature's Grace): Once per game, swap stats with adjacent opponent card after capture.
        WarpDrive,       // 6. Galactic Explorer (Cosmic Odyssey): Move to any unoccupied space once per turn.
        TemporalRift,    // 7. Clockwork Sorcerer (Temporal Enigma): Once per game, reverse strength values of adjacent cards for 1 turn.
        Rebirth,         // 8. Phoenix Guardian (Eternal Flame): If captured, returns to owner's hand to be played again.
        TechnoStealth,   // 9. Cyber Ninja (Digital Shadow): Immune to capture when adjacent to a Tech/Cybernetic card.
        MoonlightBlessing// 10. Lunar Oracle (Celestial Insight): +1 all sides during nighttime or adjacent to Lunar/Moon card.
    }

    [Serializable]
    public struct DirectionalStats
    {
        public int up;
        public int down;
        public int left;
        public int right;

        public DirectionalStats(int up, int down, int left, int right)
        {
            this.up = up;
            this.down = down;
            this.left = left;
            this.right = right;
        }

        public DirectionalStats AddAll(int bonus) =>
            new DirectionalStats(up + bonus, down + bonus, left + bonus, right + bonus);
    }

    [CreateAssetMenu(fileName = "NewCard", menuName = "Synapse TCG/CardData (Project CF & CardCraft)")]
    public class CardDataSO : ScriptableObject
    {
        public string id;
        public string title;
        public string codeName;
        public DirectionalStats baseStats;
        public CardTheme themes;
        public SpecialAbilityType specialAbility;
        public string specialAbilityDescription;
        public CardTheme synergyRequiredTheme;
        public int synergyAllSidesBonus;
        public string synergyName;
        public string evolvesToCardId;
        public Sprite cardArt;

        [Header("Collector Identification (Shadowverse EVOLVE / BP Standard)")]
        public string originalTitleJp = "機構翼の少女・ローザ(進化前)";
        public string cardGameTitle = "Shadowverse EVOLVE";
        public string boosterVersionEn = "[BP05] Eternal omens";
        public string originalVersionJp = "ブースターパック第5弾 永劫なる絶傑";
        public string collectorCardNumber = "BP05-110 SR";
        public string collectorRarity = "SR";
        public string evolutionStateJp = "進化前";
    }

    /// <summary>
    /// Built-in Registry of all 10 PROJECT CF (Card Front Tactics: Frontier Legends) Guardian Frames
    /// and CardCraft Creative Skill cards extracted from Google Drive (bcphan@hawaii.edu).
    /// </summary>
    public static class ProjectCfCardCatalog
    {
        public static List<CardDataSO> CreateDefaultRoster()
        {
            var list = new List<CardDataSO>();

            void Add(string id, string title, string code, int u, int d, int l, int r,
                     CardTheme themes, SpecialAbilityType abil, CardTheme synTheme, int synBonus, string synName, string evolvesTo = "")
            {
                var so = ScriptableObject.CreateInstance<CardDataSO>();
                so.id = id;
                so.title = title;
                so.codeName = code;
                so.baseStats = new DirectionalStats(u, d, l, r);
                so.themes = themes;
                so.specialAbility = abil;
                so.synergyRequiredTheme = synTheme;
                so.synergyAllSidesBonus = synBonus;
                so.synergyName = synName;
                so.evolvesToCardId = evolvesTo;
                list.Add(so);
            }

            // 10 Official PROJECT CF (Card Front Tactics: Frontier Legends) Guardian Frame Cards
            Add("cf_01_mystic_mage", "Mystic Mage", "Arcane Enigma", 5, 7, 3, 6,
                CardTheme.Magic, SpecialAbilityType.Teleport, CardTheme.Magic, 2, "Arcane Power");
            Add("cf_02_mech_knight", "Mech Knight", "Iron Vanguard", 8, 4, 6, 5,
                CardTheme.Tech, SpecialAbilityType.Charge, CardTheme.Tech, 1, "Technological Alliance");
            Add("cf_03_celestial_guardian", "Celestial Guardian", "Divine Sentinel", 6, 9, 4, 7,
                CardTheme.Divine | CardTheme.Cosmic, SpecialAbilityType.HealingAura, CardTheme.Divine, 3, "Holy Harmony");
            Add("cf_04_shadow_assassin", "Shadow Assassin", "Midnight Eclipse", 7, 5, 8, 4,
                CardTheme.Shadow | CardTheme.Stealth, SpecialAbilityType.Vanish, CardTheme.Shadow | CardTheme.Stealth, 2, "Dark Ambush");
            Add("cf_05_elemental_sprite", "Elemental Sprite", "Nature's Grace", 3, 4, 6, 9,
                CardTheme.Nature, SpecialAbilityType.ElementalBurst, CardTheme.Nature, 2, "Nature's Harmony");
            Add("cf_06_galactic_explorer", "Galactic Explorer", "Cosmic Odyssey", 7, 6, 5, 8,
                CardTheme.Cosmic | CardTheme.Tech, SpecialAbilityType.WarpDrive, CardTheme.Cosmic | CardTheme.Divine, 1, "Cosmic Synergy");
            Add("cf_07_clockwork_sorcerer", "Clockwork Sorcerer", "Temporal Enigma", 4, 8, 7, 5,
                CardTheme.Steampunk | CardTheme.Magic, SpecialAbilityType.TemporalRift, CardTheme.Steampunk, 3, "Steampunk Mastery");
            Add("cf_08_phoenix_guardian", "Phoenix Guardian", "Eternal Flame", 9, 7, 6, 4,
                CardTheme.Fire | CardTheme.Nature, SpecialAbilityType.Rebirth, CardTheme.Fire, 2, "Inferno Bond");
            Add("cf_09_cyber_ninja", "Cyber Ninja", "Digital Shadow", 6, 5, 8, 7,
                CardTheme.Tech | CardTheme.Stealth, SpecialAbilityType.TechnoStealth, CardTheme.Stealth | CardTheme.Shadow, 2, "Silent Circuit");
            Add("cf_10_lunar_oracle", "Lunar Oracle", "Celestial Insight", 7, 6, 4, 9,
                CardTheme.Lunar | CardTheme.Cosmic | CardTheme.Divine, SpecialAbilityType.MoonlightBlessing, CardTheme.Cosmic | CardTheme.Lunar, 3, "Celestial Guidance");

            // CardCraft Creative Portfolio Evolution Cards
            Add("cc_01_sketching", "Sketching", "Ideation Tier 1", 4, 5, 6, 5,
                CardTheme.Creative, SpecialAbilityType.None, CardTheme.Creative, 1, "Design + Feedback Loop", "cc_02_concept_art");
            Add("cc_02_concept_art", "Concept Art", "Ideation Tier 2", 6, 7, 8, 7,
                CardTheme.Creative | CardTheme.Magic, SpecialAbilityType.None, CardTheme.Creative, 2, "Portfolio Mastery");
            Add("cc_03_storyboard", "Storyboard", "Execution Tier 1", 5, 6, 5, 6,
                CardTheme.Creative, SpecialAbilityType.None, CardTheme.Creative, 1, "Narrative Flow", "cc_04_animatic");
            Add("cc_04_animatic", "Animatic", "Execution Tier 2", 7, 8, 7, 8,
                CardTheme.Creative | CardTheme.Tech, SpecialAbilityType.WarpDrive, CardTheme.Creative, 2, "Render Pipeline");

            return list;
        }
    }
}
