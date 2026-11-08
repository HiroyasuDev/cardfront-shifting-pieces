#!/usr/bin/env python3
"""
Synapse Sovereign TCG Engine — Track A: Unity Engine Production Serializer.
Generates bootable Unity 2022.3 LTS ProjectSettings, Packages/manifest.json,
60 ScriptableObject card assets (.asset), 4 tactical 3D/HUD prefabs (.prefab),
2 playable scenes (.unity), deterministic .meta files across all of Assets/,
and the production serialization manifest in Logs/unity_production_serialization_manifest.json.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "Assets"
PROJECT_SETTINGS_DIR = PROJECT_ROOT / "ProjectSettings"
PACKAGES_DIR = PROJECT_ROOT / "Packages"
CARDS_DIR = ASSETS_DIR / "Resources" / "Cards"
CARD_ART_DIR = ASSETS_DIR / "Resources" / "CardArt"
PREFABS_DIR = ASSETS_DIR / "Prefabs"
SCENES_DIR = ASSETS_DIR / "Scenes"
LOGS_DIR = PROJECT_ROOT / "Logs"

# CardTheme bitmask constants matching Assets/Scripts/Data/CardDataSO.cs
THEME_NONE = 0
THEME_MAGIC = 1 << 0       # 1
THEME_TECH = 1 << 1        # 2
THEME_DIVINE = 1 << 2      # 4
THEME_SHADOW = 1 << 3      # 8
THEME_NATURE = 1 << 4      # 16
THEME_COSMIC = 1 << 5      # 32
THEME_STEAMPUNK = 1 << 6   # 64
THEME_FIRE = 1 << 7        # 128
THEME_STEALTH = 1 << 8     # 256
THEME_LUNAR = 1 << 9       # 512
THEME_CREATIVE = 1 << 10   # 1024

# SpecialAbilityType enum constants matching Assets/Scripts/Data/CardDataSO.cs
ABILITY_NONE = 0
ABILITY_TELEPORT = 1
ABILITY_CHARGE = 2
ABILITY_HEALING_AURA = 3
ABILITY_VANISH = 4
ABILITY_ELEMENTAL_BURST = 5
ABILITY_WARP_DRIVE = 6
ABILITY_TEMPORAL_RIFT = 7
ABILITY_REBIRTH = 8
ABILITY_TECHNO_STEALTH = 9
ABILITY_MOONLIGHT_BLESSING = 10

ABILITY_DESCRIPTIONS: Dict[int, str] = {
    ABILITY_NONE: "Creative Portfolio Card: Evolves after repeated match mastery.",
    ABILITY_TELEPORT: "Once per game, move unit to any unoccupied space on the 3x3 grid and resolve captures.",
    ABILITY_CHARGE: "When this unit captures an opponent card, immediately make a bonus placement this turn.",
    ABILITY_HEALING_AURA: "At the end of your turn, restore +1 permanent strength to all sides of adjacent friendly cards.",
    ABILITY_VANISH: "Once per game, this unit becomes immune to capture for 1 full turn.",
    ABILITY_ELEMENTAL_BURST: "Once per game after capturing an adjacent card, swap base stats with the captured card.",
    ABILITY_WARP_DRIVE: "Once per turn, relocate to any unoccupied space on the 3x3 grid.",
    ABILITY_TEMPORAL_RIFT: "Once per game, reverse the directional strength values (Up<->Down, Left<->Right) of adjacent cards for 1 turn.",
    ABILITY_REBIRTH: "Once per game, if captured, this card returns to its original owner's hand.",
    ABILITY_TECHNO_STEALTH: "Immune to capture while orthogonally adjacent to any Tech card.",
    ABILITY_MOONLIGHT_BLESSING: "Gains +1 to all sides during nighttime or while adjacent to a Lunar card.",
}


@dataclass(frozen=True)
class SerializedCardSpec:
    id: str
    title: str
    code_name: str
    up: int
    down: int
    left: int
    right: int
    themes: int
    special_ability: int
    synergy_required_theme: int
    synergy_bonus: int
    synergy_name: str
    evolves_to: str = ""
    faction: str = "Frontier"
    rarity: str = "Rare"
    art_sprite_rel_path: str = "Assets/Resources/CardArt/cf_01_mystic_mage.png"


def compute_deterministic_guid(rel_posix_path: str) -> str:
    """
    Computes a deterministic 32-character lowercase hex GUID from a relative POSIX path
    (e.g. 'Assets/Scripts/Data/CardDataSO.cs').
    """
    normalized = rel_posix_path.strip().replace("\\", "/").lstrip("/")
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def build_60_card_roster() -> List[SerializedCardSpec]:
    """
    Returns the complete 60-card ScriptableObject catalog:
    - 14 canonical PROJECT CF & CardCraft cards (cf_01 .. cf_10, cc_01 .. cc_04)
    - 46 Set 1 Faction Expansion cards (s1_15_aether_vanguard .. s1_60_omega_chronos_prime)
    """
    canonical_14: List[SerializedCardSpec] = [
        SerializedCardSpec(
            "cf_01_mystic_mage", "Mystic Mage", "Arcane Enigma", 5, 7, 3, 6,
            THEME_MAGIC, ABILITY_TELEPORT, THEME_MAGIC, 2, "Arcane Power",
            faction="ArcaneEnclave", rarity="Legendary",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_01_mystic_mage.png",
        ),
        SerializedCardSpec(
            "cf_02_mech_knight", "Mech Knight", "Iron Vanguard", 8, 4, 6, 5,
            THEME_TECH, ABILITY_CHARGE, THEME_TECH, 1, "Technological Alliance",
            faction="IronVanguardDirectorate", rarity="Epic",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_02_mech_knight.png",
        ),
        SerializedCardSpec(
            "cf_03_celestial_guardian", "Celestial Guardian", "Divine Sentinel", 6, 9, 4, 7,
            THEME_DIVINE | THEME_COSMIC, ABILITY_HEALING_AURA, THEME_DIVINE, 3, "Holy Harmony",
            faction="CelestialOrder", rarity="Legendary",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_03_celestial_guardian.png",
        ),
        SerializedCardSpec(
            "cf_04_shadow_assassin", "Shadow Assassin", "Midnight Eclipse", 7, 5, 8, 4,
            THEME_SHADOW | THEME_STEALTH, ABILITY_VANISH, THEME_SHADOW | THEME_STEALTH, 2, "Dark Ambush",
            faction="ShadowSyndicate", rarity="Epic",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_04_shadow_assassin.png",
        ),
        SerializedCardSpec(
            "cf_05_elemental_sprite", "Elemental Sprite", "Nature's Grace", 3, 4, 6, 9,
            THEME_NATURE, ABILITY_ELEMENTAL_BURST, THEME_NATURE, 2, "Nature's Harmony",
            faction="WildwoodCovenant", rarity="Rare",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_05_elemental_sprite.png",
        ),
        SerializedCardSpec(
            "cf_06_galactic_explorer", "Galactic Explorer", "Cosmic Odyssey", 7, 6, 5, 8,
            THEME_COSMIC | THEME_TECH, ABILITY_WARP_DRIVE, THEME_COSMIC | THEME_DIVINE, 1, "Cosmic Synergy",
            faction="CelestialOrder", rarity="Epic",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_06_galactic_explorer.png",
        ),
        SerializedCardSpec(
            "cf_07_clockwork_sorcerer", "Clockwork Sorcerer", "Temporal Enigma", 4, 8, 7, 5,
            THEME_STEAMPUNK | THEME_MAGIC, ABILITY_TEMPORAL_RIFT, THEME_STEAMPUNK, 3, "Steampunk Mastery",
            faction="ArcaneEnclave", rarity="Legendary",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_07_clockwork_sorcerer.png",
        ),
        SerializedCardSpec(
            "cf_08_phoenix_guardian", "Phoenix Guardian", "Eternal Flame", 9, 7, 6, 4,
            THEME_FIRE | THEME_NATURE, ABILITY_REBIRTH, THEME_FIRE, 2, "Inferno Bond",
            faction="WildwoodCovenant", rarity="Legendary",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_08_phoenix_guardian.png",
        ),
        SerializedCardSpec(
            "cf_09_cyber_ninja", "Cyber Ninja", "Digital Shadow", 6, 5, 8, 7,
            THEME_TECH | THEME_STEALTH, ABILITY_TECHNO_STEALTH, THEME_STEALTH | THEME_SHADOW, 2, "Silent Circuit",
            faction="IronVanguardDirectorate", rarity="Epic",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_09_cyber_ninja.png",
        ),
        SerializedCardSpec(
            "cf_10_lunar_oracle", "Lunar Oracle", "Celestial Insight", 7, 6, 4, 9,
            THEME_LUNAR | THEME_COSMIC | THEME_DIVINE, ABILITY_MOONLIGHT_BLESSING, THEME_COSMIC | THEME_LUNAR, 3, "Celestial Guidance",
            faction="CelestialOrder", rarity="Legendary",
            art_sprite_rel_path="Assets/Resources/CardArt/cf_10_lunar_oracle.png",
        ),
        SerializedCardSpec(
            "cc_01_sketching", "Sketching", "Ideation Tier 1", 4, 5, 6, 5,
            THEME_CREATIVE, ABILITY_NONE, THEME_CREATIVE, 1, "Design + Feedback Loop",
            evolves_to="cc_02_concept_art", faction="CreativeStudio", rarity="Common",
            art_sprite_rel_path="Assets/Resources/CardArt/cc_01_sketching.png",
        ),
        SerializedCardSpec(
            "cc_02_concept_art", "Concept Art", "Ideation Tier 2", 6, 7, 8, 7,
            THEME_CREATIVE | THEME_MAGIC, ABILITY_NONE, THEME_CREATIVE, 2, "Portfolio Mastery",
            faction="CreativeStudio", rarity="Rare",
            art_sprite_rel_path="Assets/Resources/CardArt/cc_02_concept_art.png",
        ),
        SerializedCardSpec(
            "cc_03_storyboard", "Storyboard", "Execution Tier 1", 5, 6, 5, 6,
            THEME_CREATIVE, ABILITY_NONE, THEME_CREATIVE, 1, "Narrative Flow",
            evolves_to="cc_04_animatic", faction="CreativeStudio", rarity="Common",
            art_sprite_rel_path="Assets/Resources/CardArt/cc_03_storyboard.png",
        ),
        SerializedCardSpec(
            "cc_04_animatic", "Animatic", "Execution Tier 2", 7, 8, 7, 8,
            THEME_CREATIVE | THEME_TECH, ABILITY_WARP_DRIVE, THEME_CREATIVE, 2, "Render Pipeline",
            faction="CreativeStudio", rarity="Rare",
            art_sprite_rel_path="Assets/Resources/CardArt/cc_04_animatic.png",
        ),
    ]

    # 46 Set 1 Faction Expansion cards (s1_15 .. s1_60)
    expansion_defs: List[Tuple[str, str, str, Tuple[int, int, int, int], int, int, int, int, str, str, str, str]] = [
        ("s1_15_aether_vanguard", "Aether Vanguard", "Skyline Lancer", (7, 5, 6, 6), THEME_MAGIC | THEME_TECH, ABILITY_CHARGE, THEME_MAGIC, 2, "Aether Lance", "", "ArcaneEnclave", "Epic"),
        ("s1_16_chrono_sentinel", "Chrono Sentinel", "brass Pendulum", (5, 8, 6, 5), THEME_STEAMPUNK | THEME_TECH, ABILITY_TEMPORAL_RIFT, THEME_STEAMPUNK, 2, "Gearwork Lock", "", "ArcaneEnclave", "Rare"),
        ("s1_17_solaris_paladin", "Solaris Paladin", "Dawnbreaker Aegis", (8, 7, 5, 6), THEME_DIVINE | THEME_FIRE, ABILITY_HEALING_AURA, THEME_DIVINE, 2, "Radiant Bulwark", "", "CelestialOrder", "Epic"),
        ("s1_18_void_stalker", "Void Stalker", "Umbral Phantom", (6, 4, 9, 5), THEME_SHADOW | THEME_COSMIC, ABILITY_VANISH, THEME_SHADOW, 2, "Void Shroud", "", "ShadowSyndicate", "Rare"),
        ("s1_19_verdant_colossus", "Verdant Colossus", "Ancient Rootguard", (7, 9, 5, 4), THEME_NATURE, ABILITY_ELEMENTAL_BURST, THEME_NATURE, 3, "Rooted Bastion", "", "WildwoodCovenant", "Epic"),
        ("s1_20_nebula_corsair", "Nebula Corsair", "Starwind Raider", (6, 6, 7, 8), THEME_COSMIC | THEME_STEALTH, ABILITY_WARP_DRIVE, THEME_COSMIC, 2, "Astral Slipstream", "", "CelestialOrder", "Rare"),
        ("s1_21_brass_automaton", "Brass Automaton", "Clockwork Juggernaut", (8, 6, 7, 4), THEME_STEAMPUNK | THEME_TECH, ABILITY_CHARGE, THEME_STEAMPUNK, 2, "Steam Piston", "s1_22_aegis_colossus", "IronVanguardDirectorate", "Common"),
        ("s1_22_aegis_colossus", "Aegis Colossus", "Overclocked Titan", (9, 7, 8, 5), THEME_STEAMPUNK | THEME_TECH, ABILITY_CHARGE, THEME_TECH, 3, "Titanium Overdrive", "", "IronVanguardDirectorate", "Legendary"),
        ("s1_23_cinder_valkyrie", "Cinder Valkyrie", "Ashen Wing", (8, 5, 6, 7), THEME_FIRE | THEME_DIVINE, ABILITY_REBIRTH, THEME_FIRE, 2, "Ember Ascent", "", "WildwoodCovenant", "Epic"),
        ("s1_24_ghost_operative", "Ghost Operative", "Solid Eye Infiltrator", (5, 6, 8, 7), THEME_TECH | THEME_STEALTH, ABILITY_TECHNO_STEALTH, THEME_STEALTH, 2, "Optic Camo Link", "", "IronVanguardDirectorate", "Epic"),
        ("s1_25_crescent_archon", "Crescent Archon", "Tidecaller Priestess", (6, 8, 5, 8), THEME_LUNAR | THEME_DIVINE, ABILITY_MOONLIGHT_BLESSING, THEME_LUNAR, 3, "Lunar Tide", "", "CelestialOrder", "Legendary"),
        ("s1_26_keyframe_sculptor", "Keyframe Sculptor", "Sakuga Lead", (6, 6, 8, 7), THEME_CREATIVE | THEME_FIRE, ABILITY_TELEPORT, THEME_CREATIVE, 2, "Smear Frame Snap", "", "CreativeStudio", "Rare"),
        ("s1_27_runic_alchemist", "Runic Alchemist", "Philosopher Conduit", (4, 7, 7, 6), THEME_MAGIC | THEME_STEAMPUNK, ABILITY_ELEMENTAL_BURST, THEME_MAGIC, 2, "Transmutation", "", "ArcaneEnclave", "Rare"),
        ("s1_28_railgun_dragoons", "Railgun Dragoons", "Orbital Striker", (9, 4, 5, 7), THEME_TECH | THEME_COSMIC, ABILITY_CHARGE, THEME_TECH, 2, "Magnetic Salvo", "", "IronVanguardDirectorate", "Epic"),
        ("s1_29_seraphim_arbiter", "Seraphim Arbiter", "High Judge of Ivalice", (7, 8, 6, 7), THEME_DIVINE | THEME_MAGIC, ABILITY_HEALING_AURA, THEME_DIVINE, 3, "Sacred Decree", "", "CelestialOrder", "Legendary"),
        ("s1_30_nightshade_kunoichi", "Nightshade Kunoichi", "Lotus Blade", (7, 4, 8, 6), THEME_SHADOW | THEME_STEALTH, ABILITY_VANISH, THEME_STEALTH, 2, "Silent Petal", "", "ShadowSyndicate", "Rare"),
        ("s1_31_briar_thornweaver", "Briar Thornweaver", "Sylvan Hexer", (5, 7, 6, 7), THEME_NATURE | THEME_MAGIC, ABILITY_ELEMENTAL_BURST, THEME_NATURE, 2, "Thorn Snare", "", "WildwoodCovenant", "Rare"),
        ("s1_32_pulsar_navigator", "Pulsar Navigator", "Deep Space Astromancer", (6, 7, 5, 8), THEME_COSMIC | THEME_LUNAR, ABILITY_WARP_DRIVE, THEME_COSMIC, 2, "Quasar Beacon", "", "CelestialOrder", "Epic"),
        ("s1_33_cogwheel_artificer", "Cogwheel Artificer", "Mainspring Savant", (5, 6, 8, 6), THEME_STEAMPUNK | THEME_CREATIVE, ABILITY_TEMPORAL_RIFT, THEME_STEAMPUNK, 2, "Escapement Pulse", "", "ArcaneEnclave", "Rare"),
        ("s1_34_magma_behemoth", "Magma Behemoth", "Caldera Crusher", (9, 8, 4, 5), THEME_FIRE | THEME_NATURE, ABILITY_REBIRTH, THEME_FIRE, 3, "Tectonic Eruption", "", "WildwoodCovenant", "Epic"),
        ("s1_35_neural_netrunner", "Neural Netrunner", "Zero-Day Phantom", (6, 5, 9, 6), THEME_TECH | THEME_SHADOW, ABILITY_TECHNO_STEALTH, THEME_TECH, 2, "Packet Injection", "", "ShadowSyndicate", "Epic"),
        ("s1_36_eclipse_sovereign", "Eclipse Sovereign", "Corona Monarch", (8, 7, 5, 8), THEME_LUNAR | THEME_SHADOW, ABILITY_MOONLIGHT_BLESSING, THEME_LUNAR, 3, "Umbral Corona", "", "CelestialOrder", "Legendary"),
        ("s1_37_voxel_architect", "Voxel Architect", "O-Voxel Retopologist", (7, 7, 7, 6), THEME_CREATIVE | THEME_TECH, ABILITY_WARP_DRIVE, THEME_CREATIVE, 2, "Manifold Mesh", "", "CreativeStudio", "Epic"),
        ("s1_38_astral_spellblade", "Astral Spellblade", "Rift Duelist", (7, 6, 6, 7), THEME_MAGIC | THEME_COSMIC, ABILITY_TELEPORT, THEME_MAGIC, 2, "Phase Riposte", "", "ArcaneEnclave", "Rare"),
        ("s1_39_bastion_dreadnought", "Bastion Dreadnought", "Fortress Mobile Suit", (8, 9, 5, 4), THEME_TECH, ABILITY_CHARGE, THEME_TECH, 2, "Reactive Plating", "", "IronVanguardDirectorate", "Epic"),
        ("s1_40_luminary_hierophant", "Luminary Hierophant", "Choir Conductor", (5, 8, 6, 8), THEME_DIVINE, ABILITY_HEALING_AURA, THEME_DIVINE, 3, "Sanctuary Hymn", "", "CelestialOrder", "Rare"),
        ("s1_41_abyssal_reaver", "Abyssal Reaver", "Dusk Harvester", (8, 5, 7, 5), THEME_SHADOW, ABILITY_VANISH, THEME_SHADOW, 2, "Soul Siphon", "", "ShadowSyndicate", "Rare"),
        ("s1_42_spore_myconid", "Spore Myconid", "Fungal Sovereign", (4, 8, 7, 6), THEME_NATURE | THEME_SHADOW, ABILITY_ELEMENTAL_BURST, THEME_NATURE, 2, "Mycelial Network", "", "WildwoodCovenant", "Common"),
        ("s1_43_hyperion_starcruiser", "Hyperion Starcruiser", "Fleet Flagship", (8, 6, 6, 8), THEME_COSMIC | THEME_TECH, ABILITY_WARP_DRIVE, THEME_COSMIC, 3, "Broadside Telemetry", "", "IronVanguardDirectorate", "Legendary"),
        ("s1_44_aether_chronomancer", "Aether Chronomancer", "Hourglass Sage", (6, 8, 8, 5), THEME_STEAMPUNK | THEME_MAGIC, ABILITY_TEMPORAL_RIFT, THEME_STEAMPUNK, 3, "Retrograde Loop", "", "ArcaneEnclave", "Epic"),
        ("s1_45_hellfire_drake", "Hellfire Drake", "Cinder Wyrm", (8, 6, 5, 7), THEME_FIRE, ABILITY_REBIRTH, THEME_FIRE, 2, "Dragonfire Breath", "", "WildwoodCovenant", "Rare"),
        ("s1_46_mirage_infiltrator", "mirage Infiltrator", "Chaff Decoy Specialist", (5, 7, 8, 6), THEME_STEALTH | THEME_TECH, ABILITY_TECHNO_STEALTH, THEME_STEALTH, 2, "Hologram Dup", "", "ShadowSyndicate", "Rare"),
        ("s1_47_selene_valkyrie", "Selene Valkyrie", "Silver Bow", (7, 6, 6, 9), THEME_LUNAR | THEME_DIVINE, ABILITY_MOONLIGHT_BLESSING, THEME_LUNAR, 2, "Moonbeam Volley", "", "CelestialOrder", "Epic"),
        ("s1_48_cel_shader_virtuoso", "Cel Shader Virtuoso", "Halftone Ink Master", (6, 8, 7, 7), THEME_CREATIVE | THEME_MAGIC, ABILITY_TELEPORT, THEME_CREATIVE, 3, "Ben-Day Pop", "", "CreativeStudio", "Epic"),
        ("s1_49_kai_nakamura_striker", "Kai Nakamura", "Red Scarf Protagonist", (8, 6, 7, 7), THEME_TECH | THEME_CREATIVE, ABILITY_CHARGE, THEME_TECH, 3, "Shifting Resonance", "", "ArcaneEnclave", "Legendary"),
        ("s1_50_mnemosyne_ninetails", "Mnemosyne Fox", "Nine-Tailed Memory Guide", (7, 8, 6, 8), THEME_MAGIC | THEME_LUNAR, ABILITY_TELEPORT, THEME_MAGIC, 3, "Echoing Memories", "", "ArcaneEnclave", "Legendary"),
        ("s1_51_luna_tarot_weaver", "Luna Tarot Weaver", "Arcana Diviner", (6, 7, 8, 8), THEME_LUNAR | THEME_COSMIC, ABILITY_MOONLIGHT_BLESSING, THEME_LUNAR, 3, "Fate Reversal", "", "CelestialOrder", "Legendary"),
        ("s1_52_dr_rina_asakura", "Dr. Rina Asakura", "LumenForge Chief Scientist", (5, 9, 7, 7), THEME_TECH | THEME_CREATIVE, ABILITY_TEMPORAL_RIFT, THEME_TECH, 3, "Neural Calibration", "", "IronVanguardDirectorate", "Legendary"),
        ("s1_53_judge_cid_lawkeeper", "Judge Cid Lawkeeper", "Gavel of Ivalice", (8, 8, 6, 6), THEME_DIVINE | THEME_STEAMPUNK, ABILITY_HEALING_AURA, THEME_DIVINE, 3, "Red Card Verdict", "", "CelestialOrder", "Legendary"),
        ("s1_54_staccs_crown_emperor", "STACCS Crown Emperor", "Z-Level 5 Sovereign", (9, 7, 7, 6), THEME_TECH | THEME_COSMIC, ABILITY_CHARGE, THEME_COSMIC, 3, "Cantilever Slam", "", "IronVanguardDirectorate", "Legendary"),
        ("s1_55_breach_leviathan_mech", "Breach Leviathan Mech", "Kinetic Push Titan", (8, 8, 7, 5), THEME_TECH | THEME_FIRE, ABILITY_CHARGE, THEME_TECH, 3, "Grid Defense Bump", "", "IronVanguardDirectorate", "Epic"),
        ("s1_56_dicevaders_chronobudge", "Chrono Budge Commander", "Cascade Combo Pilot", (7, 6, 8, 8), THEME_COSMIC | THEME_STEAMPUNK, ABILITY_WARP_DRIVE, THEME_COSMIC, 3, "Timeline Cascade", "", "ArcaneEnclave", "Epic"),
        ("s1_57_solid_eye_snake_hound", "Solid Eye Operative", "Nojiri COST Tactician", (7, 7, 9, 6), THEME_STEALTH | THEME_TECH, ABILITY_TECHNO_STEALTH, THEME_STEALTH, 3, "Link Chain Fire", "", "ShadowSyndicate", "Legendary"),
        ("s1_58_mana_sanctuary_dryad", "Mana Sanctuary Dryad", "Isono World Tree Spirit", (6, 9, 6, 8), THEME_NATURE | THEME_DIVINE, ABILITY_HEALING_AURA, THEME_NATURE, 3, "World Tree Bloom", "", "WildwoodCovenant", "Legendary"),
        ("s1_59_neo_arcadia_zero_saber", "Neo Arcadia Cyber-Elf", "Nakayama Z-Saber Ace", (9, 5, 8, 7), THEME_TECH | THEME_FIRE, ABILITY_TELEPORT, THEME_TECH, 3, "Overdrive Slash", "", "IronVanguardDirectorate", "Legendary"),
        ("s1_60_omega_chronos_prime", "Omega Chronos Prime", "Apex Sovereign of Time", (9, 9, 8, 8), THEME_COSMIC | THEME_DIVINE | THEME_STEAMPUNK, ABILITY_TEMPORAL_RIFT, THEME_COSMIC, 3, "Singularity Convergence", "", "CelestialOrder", "Legendary"),
    ]

    canonical_art_cycle = [c.art_sprite_rel_path for c in canonical_14]
    expansion_46: List[SerializedCardSpec] = []
    for idx, (cid, title, code, (u, d, l, r), themes, abil, syn_theme, syn_bonus, syn_name, evolves_to, faction, rarity) in enumerate(expansion_defs):
        art_rel = canonical_art_cycle[idx % len(canonical_art_cycle)]
        expansion_46.append(
            SerializedCardSpec(
                id=cid,
                title=title,
                code_name=code,
                up=u,
                down=d,
                left=l,
                right=r,
                themes=themes,
                special_ability=abil,
                synergy_required_theme=syn_theme,
                synergy_bonus=syn_bonus,
                synergy_name=syn_name,
                evolves_to=evolves_to,
                faction=faction,
                rarity=rarity,
                art_sprite_rel_path=art_rel,
            )
        )

    roster = canonical_14 + expansion_46
    assert len(roster) == 60, f"Expected 60 cards, got {len(roster)}"
    return roster


def serialize_card_asset_yaml(card: SerializedCardSpec, card_data_so_guid: str) -> str:
    """
    Serializes a single CardDataSO instance as a valid Unity 2022.3 YAML (%YAML 1.1) .asset file.
    """
    sprite_guid = compute_deterministic_guid(card.art_sprite_rel_path)
    desc = ABILITY_DESCRIPTIONS.get(card.special_ability, "Tactical unit ability.")
    return (
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!114 &11400000\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        "  m_GameObject: {fileID: 0}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {card_data_so_guid}, type: 3}}\n"
        f"  m_Name: {card.id}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Data.CardDataSO\n"
        f"  id: {card.id}\n"
        f"  title: \"{card.title}\"\n"
        f"  codeName: \"{card.code_name}\"\n"
        "  baseStats:\n"
        f"    up: {card.up}\n"
        f"    down: {card.down}\n"
        f"    left: {card.left}\n"
        f"    right: {card.right}\n"
        f"  themes: {card.themes}\n"
        f"  specialAbility: {card.special_ability}\n"
        f"  specialAbilityDescription: \"{desc}\"\n"
        f"  synergyRequiredTheme: {card.synergy_required_theme}\n"
        f"  synergyAllSidesBonus: {card.synergy_bonus}\n"
        f"  synergyName: \"{card.synergy_name}\"\n"
        f"  evolvesToCardId: \"{card.evolves_to}\"\n"
        f"  cardArt: {{fileID: 21300000, guid: {sprite_guid}, type: 3}}\n"
    )


def write_project_settings_and_packages() -> List[str]:
    """
    Writes ProjectSettings/{ProjectVersion.txt, EditorBuildSettings.asset, TagManager.asset,
    QualitySettings.asset, GraphicsSettings.asset} and Packages/manifest.json.
    """
    PROJECT_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    written: List[str] = []

    # 1. ProjectVersion.txt
    pv_path = PROJECT_SETTINGS_DIR / "ProjectVersion.txt"
    pv_path.write_text(
        "m_EditorVersion: 2022.3.40f1\n"
        "m_EditorVersionWithRevision: 2022.3.40f1 (cbdda657d2f0)\n",
        encoding="utf-8",
    )
    written.append(str(pv_path))

    # 2. EditorBuildSettings.asset
    main_menu_guid = compute_deterministic_guid("Assets/Scenes/SynapseMainMenu.unity")
    battle_arena_guid = compute_deterministic_guid("Assets/Scenes/SynapseTacticalBattleArena.unity")
    ebs_path = PROJECT_SETTINGS_DIR / "EditorBuildSettings.asset"
    ebs_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!1045 &1\n"
        "EditorBuildSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_Scenes:\n"
        "  - enabled: 1\n"
        "    path: Assets/Scenes/SynapseMainMenu.unity\n"
        f"    guid: {main_menu_guid}\n"
        "  - enabled: 1\n"
        "    path: Assets/Scenes/SynapseTacticalBattleArena.unity\n"
        f"    guid: {battle_arena_guid}\n"
        "  m_configObjects: {}\n",
        encoding="utf-8",
    )
    written.append(str(ebs_path))

    # 3. TagManager.asset
    tm_path = PROJECT_SETTINGS_DIR / "TagManager.asset"
    tm_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!78 &1\n"
        "TagManager:\n"
        "  serializedVersion: 2\n"
        "  tags:\n"
        "  - StaccsCardCube\n"
        "  - TacticalBoardSlot\n"
        "  - TelegraphOverlay\n"
        "  - SolidEyeHud\n"
        "  - JudgeLawBanner\n"
        "  layers:\n"
        "  - Default\n"
        "  - TransparentFX\n"
        "  - Ignore Raycast\n"
        "  - \n"
        "  - Water\n"
        "  - UI\n"
        "  - TacticalBoard3x3\n"
        "  - StaccsIsoCube\n"
        "  - TelegraphLayer\n"
        "  - SolidEyePopCel\n"
        "  m_SortingLayers:\n"
        "  - name: Default\n"
        "    uniqueID: 0\n"
        "    locked: 0\n"
        "  - name: GroundTelegraph\n"
        "    uniqueID: 101\n"
        "    locked: 0\n"
        "  - name: StaccsTower\n"
        "    uniqueID: 102\n"
        "    locked: 0\n"
        "  - name: SolidEyeCutIn\n"
        "    uniqueID: 103\n"
        "    locked: 0\n",
        encoding="utf-8",
    )
    written.append(str(tm_path))

    # 4. QualitySettings.asset
    qs_path = PROJECT_SETTINGS_DIR / "QualitySettings.asset"
    qs_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!47 &1\n"
        "QualitySettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 5\n"
        "  m_CurrentQuality: 0\n"
        "  m_QualitySettings:\n"
        "  - serializedVersion: 3\n"
        "    name: Ultra_SynapseAetherCel_60FPS\n"
        "    pixelLightCount: 4\n"
        "    shadows: 2\n"
        "    shadowResolution: 3\n"
        "    shadowProjection: 1\n"
        "    shadowCascades: 4\n"
        "    shadowDistance: 60\n"
        "    antiAliasing: 4\n"
        "    vSyncCount: 1\n"
        "    lodBias: 2\n"
        "    maximumLODLevel: 0\n",
        encoding="utf-8",
    )
    written.append(str(qs_path))

    # 5. GraphicsSettings.asset
    holo_shader_guid = compute_deterministic_guid("Assets/Shaders/SynapseHoloCard.shader")
    gs_path = PROJECT_SETTINGS_DIR / "GraphicsSettings.asset"
    gs_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!30 &1\n"
        "GraphicsSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 13\n"
        "  m_AlwaysIncludedShaders:\n"
        "  - {fileID: 10753, guid: 0000000000000000f000000000000000, type: 0}\n"
        f"  - {{fileID: 4800000, guid: {holo_shader_guid}, type: 3}}\n"
        "  m_CustomRenderPipeline: {fileID: 0}\n"
        "  m_TransparencySortMode: 0\n"
        "  m_TransparencySortAxis: {x: 0, y: 1, z: -0.4}\n",
        encoding="utf-8",
    )
    written.append(str(gs_path))

    # 6. Packages/manifest.json
    pkg_manifest = {
        "dependencies": {
            "com.unity.collab-proxy": "2.3.1",
            "com.unity.feature.development": "1.0.1",
            "com.unity.ide.rider": "3.0.28",
            "com.unity.ide.visualstudio": "2.0.22",
            "com.unity.ide.vscode": "1.2.5",
            "com.unity.test-framework": "1.1.33",
            "com.unity.textmeshpro": "3.0.6",
            "com.unity.timeline": "1.7.6",
            "com.unity.ugui": "1.0.0",
            "com.unity.modules.ai": "1.0.0",
            "com.unity.modules.animation": "1.0.0",
            "com.unity.modules.assetbundle": "1.0.0",
            "com.unity.modules.audio": "1.0.0",
            "com.unity.modules.imageconversion": "1.0.0",
            "com.unity.modules.imgui": "1.0.0",
            "com.unity.modules.jsonserialize": "1.0.0",
            "com.unity.modules.particlesystem": "1.0.0",
            "com.unity.modules.physics": "1.0.0",
            "com.unity.modules.screencapture": "1.0.0",
            "com.unity.modules.ui": "1.0.0",
            "com.unity.modules.uielements": "1.0.0",
            "com.unity.modules.unitywebrequest": "1.0.0",
            "com.unity.modules.unitywebrequestaudio": "1.0.0",
            "com.unity.modules.unitywebrequesttexture": "1.0.0",
        }
    }
    manifest_path = PACKAGES_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(pkg_manifest, indent=2) + "\n", encoding="utf-8")
    written.append(str(manifest_path))

    return written


def write_prefabs() -> List[str]:
    """
    Serializes the 4 core Unity Prefabs in Assets/Prefabs/:
    1. StaccsCardCube.prefab
    2. TelegraphTileOverlay.prefab
    3. SolidEyeHud.prefab
    4. SynapseTacticalBoard3x3.prefab
    """
    PREFABS_DIR.mkdir(parents=True, exist_ok=True)
    written: List[str] = []

    staccs_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseStaccsCubeAnimator.cs")
    aesthetics_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseCardAesthetics.cs")
    telegraph_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseMultitudeTelegraphAnimator.cs")
    board_ctrl_guid = compute_deterministic_guid("Assets/Scripts/Client/SynapseGameBoardController.cs")
    biome_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseEnvironmentBiomeSystem.cs")
    unified_runtime_guid = compute_deterministic_guid("Assets/Scripts/Core/CardFrontUnifiedRuntime.cs")
    juice_guid = compute_deterministic_guid("Assets/Scripts/FX/SynapseDicevadersJuiceAndAudioController.cs")

    # 1. StaccsCardCube.prefab
    staccs_prefab = PREFABS_DIR / "StaccsCardCube.prefab"
    staccs_prefab.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!1 &100000\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400000}\n"
        "  - component: {fileID: 8200000}\n"
        "  - component: {fileID: 11400001}\n"
        "  - component: {fileID: 11400002}\n"
        "  m_Layer: 7\n"
        "  m_Name: StaccsCardCube\n"
        "  m_TagString: StaccsCardCube\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400000\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100000}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_ConstrainProportionsScale: 0\n"
        "  m_Children:\n"
        "  - {fileID: 400001}\n"
        "  - {fileID: 400002}\n"
        "  - {fileID: 400003}\n"
        "  - {fileID: 400004}\n"
        "  - {fileID: 400005}\n"
        "  m_Father: {fileID: 0}\n"
        "  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}\n"
        "--- !u!1 &100001\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400001}\n"
        "  - component: {fileID: 2300001}\n"
        "  m_Layer: 7\n"
        "  m_Name: TopDiamondFace\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400001\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100001}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0.14, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400000}\n"
        "--- !u!23 &2300001\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100001}\n"
        "  m_Enabled: 1\n"
        "  m_CastShadows: 1\n"
        "  m_ReceiveShadows: 1\n"
        "--- !u!1 &100002\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400002}\n"
        "  - component: {fileID: 2300002}\n"
        "  m_Layer: 7\n"
        "  m_Name: LeftIsoFace\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400002\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100002}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: -0.5, y: 0, z: -0.5}\n"
        "  m_LocalScale: {x: 1, y: 0.28, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400000}\n"
        "--- !u!23 &2300002\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100002}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &100003\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400003}\n"
        "  - component: {fileID: 2300003}\n"
        "  m_Layer: 7\n"
        "  m_Name: RightIsoFace\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400003\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100003}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0.5, y: 0, z: -0.5}\n"
        "  m_LocalScale: {x: 1, y: 0.28, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400000}\n"
        "--- !u!23 &2300003\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100003}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &100004\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400004}\n"
        "  m_Layer: 7\n"
        "  m_Name: CantileverBridgeMesh\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 0\n"
        "--- !u!4 &400004\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100004}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0.5, y: 0.28, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 0.12, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400000}\n"
        "--- !u!1 &100005\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400005}\n"
        "  m_Layer: 8\n"
        "  m_Name: HazardWarningChevronRoot\n"
        "  m_TagString: TelegraphOverlay\n"
        "  m_IsActive: 0\n"
        "--- !u!4 &400005\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100005}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0.45, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400000}\n"
        "--- !u!82 &8200000\n"
        "AudioSource:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100000}\n"
        "  m_Enabled: 1\n"
        "  OutputAudioMixerGroup: {fileID: 0}\n"
        "  m_PlayOnAwake: 0\n"
        "  m_Volume: 0.9\n"
        "  m_Pitch: 1\n"
        "--- !u!114 &11400001\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {staccs_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseStaccsCubeAnimator\n"
        "  cubeRoot: {fileID: 400000}\n"
        "  topDiamondFaceRenderer: {fileID: 2300001}\n"
        "  leftIsoFaceRenderer: {fileID: 2300002}\n"
        "  rightIsoFaceRenderer: {fileID: 2300003}\n"
        "  cantileverBridgeMesh: {fileID: 400004}\n"
        "  hazardWarningChevronRoot: {fileID: 400005}\n"
        "  cubeLayerThicknessY: 0.28\n"
        "  dropSpawnHeightOffset: 2.4\n"
        "  baseDropDuration: 0.36\n"
        "  maxStackHeight: 5\n"
        "  stackDropAudioSource: {fileID: 8200000}\n"
        "  basePitchSemitoneZero: 1\n"
        "  semitoneStepPerZLayer: 2\n"
        "  bumpDisplacementDistance: 0.42\n"
        "  bumpDuration: 0.24\n"
        "--- !u!114 &11400002\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 100000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {aesthetics_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseCardAesthetics\n",
        encoding="utf-8",
    )
    written.append(str(staccs_prefab))

    # 2. TelegraphTileOverlay.prefab (Enforces <= 3 simultaneous layers per tile)
    telegraph_prefab = PREFABS_DIR / "TelegraphTileOverlay.prefab"
    telegraph_prefab.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!1 &200000\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400100}\n"
        "  - component: {fileID: 11400101}\n"
        "  m_Layer: 8\n"
        "  m_Name: TelegraphTileOverlay\n"
        "  m_TagString: TelegraphOverlay\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400100\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200000}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0.02, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children:\n"
        "  - {fileID: 400101}\n"
        "  - {fileID: 400102}\n"
        "  - {fileID: 400103}\n"
        "  m_Father: {fileID: 0}\n"
        "--- !u!1 &200001\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400101}\n"
        "  - component: {fileID: 2300101}\n"
        "  m_Layer: 8\n"
        "  m_Name: Layer1_GroundDiamondAndHazardStripe\n"
        "  m_TagString: TelegraphOverlay\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400101\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200001}\n"
        "  serializedVersion: 2\n"
        "  m_LocalPosition: {x: 0, y: 0.01, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400100}\n"
        "--- !u!23 &2300101\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200001}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &200002\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400102}\n"
        "  - component: {fileID: 2300102}\n"
        "  m_Layer: 8\n"
        "  m_Name: Layer2_FftaFacingRingAndItbPushVector\n"
        "  m_TagString: TelegraphOverlay\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400102\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200002}\n"
        "  serializedVersion: 2\n"
        "  m_LocalPosition: {x: 0, y: 0.15, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400100}\n"
        "--- !u!23 &2300102\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200002}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &200003\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400103}\n"
        "  - component: {fileID: 2300103}\n"
        "  m_Layer: 8\n"
        "  m_Name: Layer3_AwCrosshairForecastPillAndJudgeLaw\n"
        "  m_TagString: TelegraphOverlay\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400103\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200003}\n"
        "  serializedVersion: 2\n"
        "  m_LocalPosition: {x: 0, y: 0.65, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 400100}\n"
        "--- !u!23 &2300103\n"
        "MeshRenderer:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200003}\n"
        "  m_Enabled: 1\n"
        "--- !u!114 &11400101\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 200000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {telegraph_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseMultitudeTelegraphAnimator\n",
        encoding="utf-8",
    )
    written.append(str(telegraph_prefab))

    # 3. SolidEyeHud.prefab (Metal Gear Acid COST timeline + AW Split-Screen Cut-In + Judge Law HUD)
    solid_eye_prefab = PREFABS_DIR / "SolidEyeHud.prefab"
    solid_eye_prefab.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!1 &300000\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 22400000}\n"
        "  - component: {fileID: 22300000}\n"
        "  - component: {fileID: 11400201}\n"
        "  - component: {fileID: 11400202}\n"
        "  m_Layer: 5\n"
        "  m_Name: SolidEyeHud\n"
        "  m_TagString: SolidEyeHud\n"
        "  m_IsActive: 1\n"
        "--- !u!224 &22400000\n"
        "RectTransform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300000}\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children:\n"
        "  - {fileID: 22400001}\n"
        "  - {fileID: 22400002}\n"
        "  - {fileID: 22400003}\n"
        "  m_Father: {fileID: 0}\n"
        "  m_AnchorMin: {x: 0, y: 0}\n"
        "  m_AnchorMax: {x: 1, y: 1}\n"
        "  m_AnchoredPosition: {x: 0, y: 0}\n"
        "  m_SizeDelta: {x: 0, y: 0}\n"
        "  m_Pivot: {x: 0.5, y: 0.5}\n"
        "--- !u!223 &22300000\n"
        "Canvas:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300000}\n"
        "  m_Enabled: 1\n"
        "  serializedVersion: 3\n"
        "  m_RenderMode: 0\n"
        "  m_Camera: {fileID: 0}\n"
        "  m_PlaneDistance: 100\n"
        "  m_PixelPerfect: 1\n"
        "  m_SortingOrder: 10\n"
        "--- !u!1 &300001\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 22400001}\n"
        "  m_Layer: 5\n"
        "  m_Name: NojiriCostTimelineBar\n"
        "  m_TagString: SolidEyeHud\n"
        "  m_IsActive: 1\n"
        "--- !u!224 &22400001\n"
        "RectTransform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300001}\n"
        "  m_Father: {fileID: 22400000}\n"
        "  m_AnchoredPosition: {x: 0, y: -32}\n"
        "  m_SizeDelta: {x: 840, y: 48}\n"
        "--- !u!1 &300002\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 22400002}\n"
        "  m_Layer: 5\n"
        "  m_Name: AwSplitScreenCombatCutInPanel\n"
        "  m_TagString: SolidEyeHud\n"
        "  m_IsActive: 1\n"
        "--- !u!224 &22400002\n"
        "RectTransform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300002}\n"
        "  m_Father: {fileID: 22400000}\n"
        "  m_AnchoredPosition: {x: 0, y: 120}\n"
        "  m_SizeDelta: {x: 960, y: 260}\n"
        "--- !u!1 &300003\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 22400003}\n"
        "  m_Layer: 5\n"
        "  m_Name: JudgeDecreeAndLinkEquipmentDock\n"
        "  m_TagString: JudgeLawBanner\n"
        "  m_IsActive: 1\n"
        "--- !u!224 &22400003\n"
        "RectTransform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300003}\n"
        "  m_Father: {fileID: 22400000}\n"
        "  m_AnchoredPosition: {x: -420, y: 0}\n"
        "  m_SizeDelta: {x: 280, y: 420}\n"
        "--- !u!114 &11400201\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {unified_runtime_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Core.CardFrontUnifiedRuntime\n"
        "--- !u!114 &11400202\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 300000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {juice_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.FX.SynapseDicevadersJuiceAndAudioController\n",
        encoding="utf-8",
    )
    written.append(str(solid_eye_prefab))

    # 4. SynapseTacticalBoard3x3.prefab (3x3 tactical directional capture grid with all 9 slots)
    slot_children_refs = "\n".join(f"  - {{fileID: {400301 + idx}}}" for idx in range(9))
    slot_blocks: List[str] = []
    for idx in range(9):
        sx, sy = idx % 3, idx // 3
        go_id = 400001 + idx
        tr_id = 400301 + idx
        mr_id = 2300301 + idx
        bc_id = 6500301 + idx
        wx = (sx - 1) * 2.2
        wz = (sy - 1) * 2.2
        slot_blocks.append(
            f"--- !u!1 &{go_id}\n"
            "GameObject:\n"
            "  m_ObjectHideFlags: 0\n"
            "  serializedVersion: 6\n"
            "  m_Component:\n"
            f"  - component: {{fileID: {tr_id}}}\n"
            f"  - component: {{fileID: {mr_id}}}\n"
            f"  - component: {{fileID: {bc_id}}}\n"
            "  m_Layer: 6\n"
            f"  m_Name: BoardSlot_{sx}_{sy}\n"
            "  m_TagString: TacticalBoardSlot\n"
            "  m_IsActive: 1\n"
            f"--- !u!4 &{tr_id}\n"
            "Transform:\n"
            "  m_ObjectHideFlags: 0\n"
            f"  m_GameObject: {{fileID: {go_id}}}\n"
            "  serializedVersion: 2\n"
            "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
            f"  m_LocalPosition: {{x: {wx:.2f}, y: 0, z: {wz:.2f}}}\n"
            "  m_LocalScale: {x: 2, y: 0.15, z: 2}\n"
            "  m_Children: []\n"
            "  m_Father: {fileID: 400300}\n"
            f"--- !u!23 &{mr_id}\n"
            "MeshRenderer:\n"
            "  m_ObjectHideFlags: 0\n"
            f"  m_GameObject: {{fileID: {go_id}}}\n"
            "  m_Enabled: 1\n"
            f"--- !u!65 &{bc_id}\n"
            "BoxCollider:\n"
            "  m_ObjectHideFlags: 0\n"
            f"  m_GameObject: {{fileID: {go_id}}}\n"
            "  m_IsTrigger: 0\n"
            "  m_Size: {x: 1, y: 1, z: 1}\n"
        )

    board_prefab = PREFABS_DIR / "SynapseTacticalBoard3x3.prefab"
    board_prefab.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!1 &400000\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 400300}\n"
        "  - component: {fileID: 11400301}\n"
        "  - component: {fileID: 11400302}\n"
        "  m_Layer: 6\n"
        "  m_Name: SynapseTacticalBoard3x3\n"
        "  m_TagString: TacticalBoardSlot\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &400300\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 400000}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children:\n"
        f"{slot_children_refs}\n"
        "  m_Father: {fileID: 0}\n"
        + "".join(slot_blocks)
        + "--- !u!114 &11400301\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 400000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {board_ctrl_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Client.SynapseGameBoardController\n"
        "  localPlayerId: 0\n"
        "  aiPlayerId: 1\n"
        "  playAgainstAI: 1\n"
        "  aiLookaheadDepth: 3\n"
        "  aiBeamWidth: 7\n"
        "  startAtNighttime: 0\n"
        "  matchSeed: 1337\n"
        "  cardPlaceResolveDelay: 0.32\n"
        "  captureFlipResolveDelay: 0.38\n"
        "  aiThinkDelay: 0.45\n"
        "--- !u!114 &11400302\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 400000}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {biome_guid}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseEnvironmentBiomeSystem\n",
        encoding="utf-8",
    )
    written.append(str(board_prefab))

    return written


def write_scenes() -> List[str]:
    """
    Serializes the 2 playable Unity scenes in Assets/Scenes/:
    1. SynapseMainMenu.unity
    2. SynapseTacticalBattleArena.unity
    """
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    written: List[str] = []

    unified_runtime_guid = compute_deterministic_guid("Assets/Scripts/Core/CardFrontUnifiedRuntime.cs")
    audio_dir_guid = compute_deterministic_guid("Assets/Scripts/Audio/SynapseProceduralAudioDirector.cs")
    api_client_guid = compute_deterministic_guid("Assets/Scripts/Api/SynapseApiClient.cs")
    lumenforge_client_guid = compute_deterministic_guid("Assets/Scripts/Api/LumenForgeIoStudioClient.cs")
    story_campaign_guid = compute_deterministic_guid("Assets/Scripts/Campaign/SynapseStoryCampaign.cs")
    board_ctrl_guid = compute_deterministic_guid("Assets/Scripts/Client/SynapseGameBoardController.cs")
    staccs_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseStaccsCubeAnimator.cs")
    telegraph_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseMultitudeTelegraphAnimator.cs")
    biome_guid = compute_deterministic_guid("Assets/Scripts/Visuals/SynapseEnvironmentBiomeSystem.cs")
    juice_guid = compute_deterministic_guid("Assets/Scripts/FX/SynapseDicevadersJuiceAndAudioController.cs")

    board_prefab_guid = compute_deterministic_guid("Assets/Prefabs/SynapseTacticalBoard3x3.prefab")
    hud_prefab_guid = compute_deterministic_guid("Assets/Prefabs/SolidEyeHud.prefab")
    cube_prefab_guid = compute_deterministic_guid("Assets/Prefabs/StaccsCardCube.prefab")
    telegraph_prefab_guid = compute_deterministic_guid("Assets/Prefabs/TelegraphTileOverlay.prefab")

    # 1. SynapseMainMenu.unity
    main_menu_path = SCENES_DIR / "SynapseMainMenu.unity"
    main_menu_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!29 &1\n"
        "OcclusionCullingSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_OcclusionBakeSettings:\n"
        "    smallestOccluder: 5\n"
        "    smallestHole: 0.25\n"
        "    backfaceThreshold: 100\n"
        "  m_SceneGUID: 00000000000000000000000000000001\n"
        "  m_OcclusionCullingData: {fileID: 0}\n"
        "--- !u!104 &2\n"
        "RenderSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 9\n"
        "  m_Fog: 0\n"
        "  m_AmbientSkyColor: {r: 0.212, g: 0.227, b: 0.259, a: 1}\n"
        "  m_SkyboxMaterial: {fileID: 10304, guid: 0000000000000000f000000000000000, type: 0}\n"
        "--- !u!157 &3\n"
        "LightmapSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 12\n"
        "  m_GIWorkflowMode: 1\n"
        "--- !u!196 &4\n"
        "NavMeshSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_BuildSettings:\n"
        "    serializedVersion: 3\n"
        "    agentRadius: 0.5\n"
        "--- !u!1 &500001\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 500002}\n"
        "  - component: {fileID: 500003}\n"
        "  - component: {fileID: 500004}\n"
        "  m_Layer: 0\n"
        "  m_Name: Main Camera\n"
        "  m_TagString: MainCamera\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &500002\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500001}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 1, z: -10}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "--- !u!20 &500003\n"
        "Camera:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500001}\n"
        "  m_Enabled: 1\n"
        "  serializedVersion: 2\n"
        "  m_ClearFlags: 2\n"
        "  m_BackGroundColor: {r: 0.05, g: 0.07, b: 0.12, a: 1}\n"
        "  field of view: 60\n"
        "  orthographic: 0\n"
        "--- !u!81 &500004\n"
        "AudioListener:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500001}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &500010\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 500011}\n"
        "  - component: {fileID: 500012}\n"
        "  - component: {fileID: 500013}\n"
        "  - component: {fileID: 500014}\n"
        "  - component: {fileID: 500015}\n"
        "  - component: {fileID: 500016}\n"
        "  m_Layer: 5\n"
        "  m_Name: SynapseMainMenuHubDirector\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &500011\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "--- !u!114 &500012\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {unified_runtime_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Core.CardFrontUnifiedRuntime\n"
        "--- !u!114 &500013\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {audio_dir_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Audio.SynapseProceduralAudioDirector\n"
        "--- !u!114 &500014\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {api_client_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Api.SynapseApiClient\n"
        "--- !u!114 &500015\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {lumenforge_client_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Api.LumenForgeIoStudioClient\n"
        "--- !u!114 &500016\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 500010}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {story_campaign_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Campaign.SynapseStoryCampaign\n"
        "--- !u!1660057539 &9223372036854775807\n"
        "SceneRoots:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_Roots:\n"
        "  - {fileID: 500002}\n"
        "  - {fileID: 500011}\n",
        encoding="utf-8",
    )
    written.append(str(main_menu_path))

    # 2. SynapseTacticalBattleArena.unity
    battle_arena_path = SCENES_DIR / "SynapseTacticalBattleArena.unity"
    battle_arena_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!29 &1\n"
        "OcclusionCullingSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_SceneGUID: 00000000000000000000000000000002\n"
        "  m_OcclusionCullingData: {fileID: 0}\n"
        "--- !u!104 &2\n"
        "RenderSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 9\n"
        "  m_Fog: 1\n"
        "  m_FogColor: {r: 0.08, g: 0.11, b: 0.18, a: 1}\n"
        "  m_AmbientSkyColor: {r: 0.28, g: 0.32, b: 0.42, a: 1}\n"
        "--- !u!157 &3\n"
        "LightmapSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 12\n"
        "  m_GIWorkflowMode: 1\n"
        "--- !u!196 &4\n"
        "NavMeshSettings:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "--- !u!1 &600001\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 600002}\n"
        "  - component: {fileID: 600003}\n"
        "  - component: {fileID: 600004}\n"
        "  m_Layer: 0\n"
        "  m_Name: IsometricTacticalCamera_45Yaw_35Pitch\n"
        "  m_TagString: MainCamera\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &600002\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600001}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0.2798481, y: 0.3647052, z: -0.1159169, w: 0.8804762}\n"
        "  m_LocalPosition: {x: -8, y: 9.5, z: -8}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "  m_LocalEulerAnglesHint: {x: 35.264, y: 45, z: 0}\n"
        "--- !u!20 &600003\n"
        "Camera:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600001}\n"
        "  m_Enabled: 1\n"
        "  serializedVersion: 2\n"
        "  m_ClearFlags: 2\n"
        "  m_BackGroundColor: {r: 0.06, g: 0.08, b: 0.14, a: 1}\n"
        "  orthographic: 1\n"
        "  orthographic size: 4.8\n"
        "--- !u!81 &600004\n"
        "AudioListener:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600001}\n"
        "  m_Enabled: 1\n"
        "--- !u!1 &600010\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 600011}\n"
        "  - component: {fileID: 600012}\n"
        "  m_Layer: 0\n"
        "  m_Name: IvaliceDirectionalSunLight\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &600011\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600010}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0.4082179, y: -0.2345697, z: 0.1093816, w: 0.8754261}\n"
        "  m_LocalPosition: {x: 0, y: 12, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "--- !u!108 &600012\n"
        "Light:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600010}\n"
        "  m_Enabled: 1\n"
        "  serializedVersion: 10\n"
        "  m_Type: 1\n"
        "  m_Color: {r: 1, g: 0.96, b: 0.88, a: 1}\n"
        "  m_Intensity: 1.25\n"
        "--- !u!1 &600020\n"
        "GameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: 600021}\n"
        "  - component: {fileID: 600022}\n"
        "  - component: {fileID: 600023}\n"
        "  - component: {fileID: 600024}\n"
        "  - component: {fileID: 600025}\n"
        "  - component: {fileID: 600026}\n"
        "  - component: {fileID: 600027}\n"
        "  m_Layer: 0\n"
        "  m_Name: SynapseBattleArenaMasterDirector\n"
        "  m_TagString: Untagged\n"
        "  m_IsActive: 1\n"
        "--- !u!4 &600021\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  serializedVersion: 2\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "--- !u!114 &600022\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {board_ctrl_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Client.SynapseGameBoardController\n"
        "--- !u!114 &600023\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {staccs_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseStaccsCubeAnimator\n"
        "--- !u!114 &600024\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {telegraph_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseMultitudeTelegraphAnimator\n"
        "--- !u!114 &600025\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {biome_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Visuals.SynapseEnvironmentBiomeSystem\n"
        "--- !u!114 &600026\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {audio_dir_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.Audio.SynapseProceduralAudioDirector\n"
        "--- !u!114 &600027\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_GameObject: {fileID: 600020}\n"
        "  m_Enabled: 1\n"
        f"  m_Script: {{fileID: 11500000, guid: {juice_guid}, type: 3}}\n"
        "  m_EditorClassIdentifier: Synapse.TcgEngine.FX.SynapseDicevadersJuiceAndAudioController\n"
        "--- !u!1001 &700001\n"
        "PrefabInstance:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_Modification:\n"
        "    serializedVersion: 3\n"
        "    m_TransformParent: {fileID: 0}\n"
        "    m_Modifications: []\n"
        "    m_RemovedComponents: []\n"
        f"  m_SourcePrefab: {{fileID: 100100000, guid: {board_prefab_guid}, type: 3}}\n"
        "--- !u!1001 &700002\n"
        "PrefabInstance:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_Modification:\n"
        "    serializedVersion: 3\n"
        "    m_TransformParent: {fileID: 0}\n"
        "    m_Modifications: []\n"
        "    m_RemovedComponents: []\n"
        f"  m_SourcePrefab: {{fileID: 100100000, guid: {hud_prefab_guid}, type: 3}}\n"
        "--- !u!1001 &700003\n"
        "PrefabInstance:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_Modification:\n"
        "    serializedVersion: 3\n"
        "    m_TransformParent: {fileID: 0}\n"
        "    m_Modifications: []\n"
        "    m_RemovedComponents: []\n"
        f"  m_SourcePrefab: {{fileID: 100100000, guid: {cube_prefab_guid}, type: 3}}\n"
        "--- !u!1001 &700004\n"
        "PrefabInstance:\n"
        "  m_ObjectHideFlags: 0\n"
        "  serializedVersion: 2\n"
        "  m_Modification:\n"
        "    serializedVersion: 3\n"
        "    m_TransformParent: {fileID: 0}\n"
        "    m_Modifications: []\n"
        "    m_RemovedComponents: []\n"
        f"  m_SourcePrefab: {{fileID: 100100000, guid: {telegraph_prefab_guid}, type: 3}}\n"
        "--- !u!1660057539 &9223372036854775807\n"
        "SceneRoots:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_Roots:\n"
        "  - {fileID: 600002}\n"
        "  - {fileID: 600011}\n"
        "  - {fileID: 600021}\n"
        "  - {fileID: 700001}\n"
        "  - {fileID: 700002}\n"
        "  - {fileID: 700003}\n"
        "  - {fileID: 700004}\n",
        encoding="utf-8",
    )
    written.append(str(battle_arena_path))

    return written


def build_meta_content_for_target(target_path: Path, guid: str) -> str:
    """
    Produces a deterministic Unity .meta file (fileFormatVersion: 2) tailored to the asset type.
    """
    if target_path.is_dir():
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "folderAsset: yes\n"
            "DefaultImporter:\n"
            "  externalObjects: {}\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )

    suffix = target_path.suffix.lower()
    if suffix == ".cs":
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "MonoImporter:\n"
            "  externalObjects: {}\n"
            "  serializedVersion: 2\n"
            "  defaultReferences: []\n"
            "  executionOrder: 0\n"
            "  icon: {instanceID: 0}\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
    if suffix == ".png":
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "TextureImporter:\n"
            "  internalIDToNameTable: []\n"
            "  externalObjects: {}\n"
            "  serializedVersion: 12\n"
            "  mipmaps:\n"
            "    mipMapMode: 0\n"
            "    enableMipMap: 0\n"
            "  textureType: 8\n"
            "  textureShape: 1\n"
            "  spriteMode: 1\n"
            "  spritePixelsToUnits: 100\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
    if suffix == ".shader":
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "ShaderImporter:\n"
            "  externalObjects: {}\n"
            "  defaultTextures: []\n"
            "  nonModifiableTextures: []\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
    if suffix == ".prefab":
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "PrefabImporter:\n"
            "  externalObjects: {}\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
    if suffix in (".asset", ".unity"):
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "NativeFormatImporter:\n"
            "  externalObjects: {}\n"
            "  mainObjectFileID: 11400000\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
    return (
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "DefaultImporter:\n"
        "  externalObjects: {}\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    )


def ensure_all_meta_files_under_assets() -> Dict[str, str]:
    """
    Walks every folder and file under Assets/ (excluding hidden files and .meta files)
    and writes a deterministic .meta file with `fileFormatVersion: 2` and `guid: <md5(rel_path)>`.
    Returns a mapping of `rel_posix_path -> guid`.
    """
    guid_registry: Dict[str, str] = {}
    all_targets = sorted(ASSETS_DIR.rglob("*"), key=lambda p: p.relative_to(PROJECT_ROOT).as_posix())

    for target in all_targets:
        if target.name.startswith(".") or target.suffix == ".meta":
            continue
        # Skip if any parent directory is hidden
        if any(part.startswith(".") for part in target.relative_to(ASSETS_DIR).parts):
            continue

        rel_posix = target.relative_to(PROJECT_ROOT).as_posix()
        guid = compute_deterministic_guid(rel_posix)
        meta_path = Path(str(target) + ".meta")
        meta_content = build_meta_content_for_target(target, guid)
        meta_path.write_text(meta_content, encoding="utf-8")
        guid_registry[rel_posix] = guid

    return guid_registry


def run_unity_production_serialization() -> Dict:
    """
    Executes the complete Track A Unity Engine Serialization pipeline and writes
    Logs/unity_production_serialization_manifest.json.
    """
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    PREFABS_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write ProjectSettings/* and Packages/manifest.json
    settings_files = write_project_settings_and_packages()

    # 2. Write 60 CardDataSO .asset files
    card_data_so_guid = compute_deterministic_guid("Assets/Scripts/Data/CardDataSO.cs")
    roster = build_60_card_roster()
    card_asset_paths: List[str] = []
    for card in roster:
        asset_path = CARDS_DIR / f"{card.id}.asset"
        yaml_text = serialize_card_asset_yaml(card, card_data_so_guid)
        asset_path.write_text(yaml_text, encoding="utf-8")
        card_asset_paths.append(asset_path.relative_to(PROJECT_ROOT).as_posix())

    # 3. Write 4 Prefabs
    prefab_paths = write_prefabs()

    # 4. Write 2 Scenes
    scene_paths = write_scenes()

    # 5. Generate deterministic .meta files for every file and folder under Assets/
    guid_registry = ensure_all_meta_files_under_assets()
    unique_guids = set(guid_registry.values())

    manifest = {
        "engine": "Synapse Sovereign TCG Engine",
        "unity_editor_version": "2022.3.40f1",
        "serialized_at_unix": round(time.time(), 3),
        "counts": {
            "unity_scenes": len(scene_paths),
            "prefabs": len(prefab_paths),
            "card_scriptable_objects": len(card_asset_paths),
            "canonical_project_cf_and_cardcraft_cards": 14,
            "set1_faction_expansion_cards": 46,
            "meta_files_generated": len(guid_registry),
            "unique_meta_guids": len(unique_guids),
            "guid_collision_count": len(guid_registry) - len(unique_guids),
            "project_settings_and_packages_files": len(settings_files),
        },
        "scenes": [Path(p).relative_to(PROJECT_ROOT).as_posix() for p in scene_paths],
        "prefabs": [Path(p).relative_to(PROJECT_ROOT).as_posix() for p in prefab_paths],
        "project_settings_and_packages": [Path(p).relative_to(PROJECT_ROOT).as_posix() for p in settings_files],
        "canonical_card_ids": [c.id for c in roster[:14]],
        "set1_expansion_card_ids": [c.id for c in roster[14:]],
        "key_script_guids": {
            "CardDataSO.cs": card_data_so_guid,
            "SynapseGameBoardController.cs": compute_deterministic_guid("Assets/Scripts/Client/SynapseGameBoardController.cs"),
            "SynapseStaccsCubeAnimator.cs": compute_deterministic_guid("Assets/Scripts/Visuals/SynapseStaccsCubeAnimator.cs"),
            "SynapseMultitudeTelegraphAnimator.cs": compute_deterministic_guid("Assets/Scripts/Visuals/SynapseMultitudeTelegraphAnimator.cs"),
            "CardFrontUnifiedRuntime.cs": compute_deterministic_guid("Assets/Scripts/Core/CardFrontUnifiedRuntime.cs"),
        },
        "guid_registry": guid_registry,
    }

    manifest_out = LOGS_DIR / "unity_production_serialization_manifest.json"
    manifest_out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = run_unity_production_serialization()
    print(json.dumps({
        "status": "OK",
        "unity_editor_version": result["unity_editor_version"],
        "counts": result["counts"],
        "scenes": result["scenes"],
        "prefabs": result["prefabs"],
    }, indent=2))
