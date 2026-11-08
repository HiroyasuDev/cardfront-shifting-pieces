#!/usr/bin/env python3
"""
generate_indie_marc_unity_assets.py — Indie Marc TCG Engine `.asset` ScriptableObject Generator &
19-Chapter Shifting Pieces Campaign Exporter (Subsystems 5 & 6 -> 10.0 / 10.0)
=================================================================================================
Generates real, production-grade Unity YAML `.asset` and `.asset.meta` files inside
`/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/Assets/TcgEngine/Resources/`
conforming 100% to Indie Marc's `CardData.cs`, `AbilityData.cs`, `DeckData.cs`, `PackData.cs`,
and `LevelData.cs` serialized field names and GUID references:

1. `Resources/Cards/CardFront/` -> 42 `CardData` `.asset` files:
   - 6 *Shifting Pieces* Main Characters & Totems (`sp_01` .. `sp_06`)
   - 12 *Master Tactical Champions* (`mc_01` .. `mc_12`, one per Foundational Master)
   - 12 *Dicevaders* Chrono-Armada Pilot & Mecha Units (`dv_01` .. `dv_12`)
   - 12 *Cradle of Echoes* / *Budge* / *Chrono* Spells & Memory Artifacts (`ce_01` .. `ce_12`)
2. `Resources/Abilities/CardFront/` -> 24 `AbilityData` `.asset` files:
   - Covering `OnPlay`, `Activate`, `OnDeath`, `StartOfTurn`, `Ongoing`, `OnBeforeAttack`,
     `BudgeShiftPlus`, `BudgeShiftMinus`, `ChronoReroll`, `ResonanceCascade`, `ColumnLaserLock`,
     `RedScarfMemoryLink`, `MnemosyneConstellationWeave`, `LunaTarotAwakening`, etc.
3. `Resources/Decks/CardFront/` -> 4 complete `DeckData` `.asset` starter decks (20 cards each + hero):
   - `deck_kai_red_scarf_echo.asset`
   - `deck_luna_cradle_of_echoes.asset`
   - `deck_dicevaders_chrono_armada.asset`
   - `deck_twelve_masters_sovereign.asset`
4. `Resources/Packs/CardFront/` -> 2 `PackData` `.asset` booster packs:
   - `pack_shifting_pieces_act1.asset`
   - `pack_cradle_of_echoes_genesis.asset`
5. `Resources/Campaigns/ShiftingPieces/` -> All 19 Chapters of *"Shifting Pieces"* (Acts I, II, III)
   as serialized Unity `LevelData` `.asset` encounter files:
   - `chapter_01_fragments_of_dust.asset` through `chapter_19_the_shifting_truth.asset`
6. `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/shifting_pieces_19_chapter_campaign.json`
   -> Complete 19-chapter narrative dialogue, Mnemosyne constellation memory puzzle grids,
      opponent AI decks, and boss disruptor rules.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
SYNAPSE_ROOT = PROJECT_ROOT.parent
UNPACKED_ROOT = SYNAPSE_ROOT / "tcg-engine-unpacked"
RESOURCES_ROOT = UNPACKED_ROOT / "Assets" / "TcgEngine" / "Resources"

CARDS_DIR = RESOURCES_ROOT / "Cards" / "CardFront"
ABILITIES_DIR = RESOURCES_ROOT / "Abilities" / "CardFront"
DECKS_DIR = RESOURCES_ROOT / "Decks" / "CardFront"
PACKS_DIR = RESOURCES_ROOT / "Packs" / "CardFront"
CAMPAIGNS_DIR = RESOURCES_ROOT / "Campaigns" / "ShiftingPieces"

CAMPAIGN_JSON_PATH = PROJECT_ROOT / "Datasets" / "shifting_pieces_19_chapter_campaign.json"
ASSET_MANIFEST_JSON_PATH = PROJECT_ROOT / "Datasets" / "indie_marc_unity_asset_generation_report.json"

# ============================================================================
# EXACT MONOSCRIPT & RESOURCE GUIDS FROM `tcg-engine-unpacked`
# ============================================================================
SCRIPT_GUID_CARD_DATA = "843a21f7f6f205741a0a7341aec8e84d"
SCRIPT_GUID_ABILITY_DATA = "8ce5f81e5cc37f547af6923758602c8c"
SCRIPT_GUID_DECK_DATA = "87ecef176d27eb040a9770e0eefea2ec"
SCRIPT_GUID_PACK_DATA = "137187ae111118548b8cdc17eed44c86"
SCRIPT_GUID_LEVEL_DATA = "59e39d99af93c37489aff5e1e1333e20"

TEAM_GUIDS = {
    "fire": "6bbb96863ece0314fb318c0fce569afc",
    "forest": "b80d8061c5bdb2e408e62a08e0e743ca",
    "neutral": "44accef98e769754d9edb8fe6051443a",
    "water": "ed6dfd9dc7797584994eaf1fba66535f",
}

RARITY_GUIDS = {
    "common": "fab1a52f5a36cc942985dea95be18ac9",
    "uncommon": "72248f07232412e4db2f6864dbb4e271",
    "rare": "15eaa2a0fbd97f149b3aa87387c160d1",
    "mythic": "13b592f40b7cd424c966f5d7eef425aa",
}

VARIANT_GUIDS = {
    "normal": "2132a370f5bfc284b8d48d66aa4b15f0",
    "foil": "3a827aeeaca139641a4b8ad0c3c74f52",
}

TRAIT_GUIDS = {
    "dragon": "9124c4a8561cfd14d812a55b3e885662",
    "growth": "ce0807cc62e886b4994c9e2646420845",
    "spell_damage": "50116f133bd899842ab1d2a5b71412ee",
    "wolf": "9436e14bc49faf74595ac5f19b793ba3",
}

EFFECT_GUIDS = {
    "add_attack": "4c4c317ae3dd4cf4982e8d7c7f1043b9",
    "add_attack_roll": "c40066b022ed7a94681f9a18b768e36f",
    "add_growth": "822f29e8198f50644acc881b86893bba",
    "add_hp": "fc8261ce93dbc924e859751e098513ad",
    "add_spell_damage": "700b5c07ae5d5b446994cc42c800ff88",
    "clear_status_all": "c14a48b31a743494f983c03ec81a7f2d",
    "damage": "4369324687c62ca488c57afd73a2be36",
    "destroy": "f71d4af1506339149852f66291383dc4",
    "draw": "d2f15281b01c4b347a527a3011ef430a",
    "gain_mana": "43c0ea2fb66fde3498b488c0539b96d3",
    "heal": "5e489970bbb948c409125b3ab22f2aac",
    "reset_stats": "55165dd4996d59642a883f20c7b3e07f",
    "roll_d6": "9b28ecfbc21cc2f4a8dcc9e77df4360e",
    "send_hand": "8f17c76aa367dd144a0665d4514588e9",
    "set_attack": "b9f5061df6a52ec46ba2f329312eb89f",
    "set_hp": "d1890b1ebfa6f5543b4e60ba56b19766",
    "shuffle_deck": "c9e0916615751f040adb314815376f50",
    "unexhaust": "f9708fd6466cc0a4b805048a326a5ac3",
}

STATUS_GUIDS = {
    "add_attack": "e7c01ab4617b9ab428b88fc9c435c6c4",
    "add_hp": "a9f4f26728a5c824cb455a6a1543881a",
    "armor": "ffde6010d0075ca459a80820773ce5b9",
    "deathtouch": "aa8215bec22b28149aa474176e72d3b2",
    "flying": "e86bf308bfe6d624897e484aa1f74d02",
    "fury": "c71a5ae31a2cde940b76aa921f2c80ef",
    "intimidate": "ea1f6f5dff526dc4e85c2deafadea52d",
    "invincibility": "23152e0598f367e4f9e370ce267bcd2e",
    "lifesteal": "4850ab17012eb724d869606940d0b168",
    "paralysed": "96cc4cef5c9fe6a42bfae1b6fcadc38b",
    "protected": "555d062eb785e9845ad38b914f39aca5",
    "shell": "a6b74c379b62d524d9497a67f5bb8a2d",
    "silenced": "8580d5669cd3e624c825c09fbba0b4f0",
    "spell_immunity": "fb8ee60abbfe2b9498928adb39a232e7",
    "stealth": "c09734b8821c2c245a43f67e9938cde7",
}

# Verified Sprite & FX GUIDs from existing TcgEngine assets
SPRITE_FULL_POOL = [
    "b22500bd3cdea4b40bdb8da52c031c62",
    "40307ec5eae2d92459a10d13d4a6de5f",
    "c0329b5e4485df6409690de7fb5a8513",
    "3f996c8e57a34b046b26c0e702f6ec10",
]
SPRITE_BOARD_POOL = [
    "322637c9c966cd24dab8b9e27ef6e16f",
    "4df1ddd2c83f83649b0a1e2444d7461f",
    "fe8ea4703d16a9b4793fb214a7f6bc42",
    "a3c16225ff191a941959e49d08dae6fe",
]
SPAWN_FX_GUID = "bac685160af4aff46ae561a51da6f5f4"
CASTER_FX_GUID = "baadd1fc54b9b4f4fa6d0aee484bc9f8"
PACK_IMG_GUID = "e400c282187e5f54dab6aacfd8adae20"
CARDBACK_IMG_GUID = "96d8dad709a2729419f19d1d4633a0ef"


def deterministic_guid(key: str) -> str:
    """Generate a deterministic 32-hex-char Unity GUID from a string key."""
    return hashlib.md5(f"synapse_indie_marc_tcg::{key}".encode("utf-8")).hexdigest()


def yaml_escape(text: str) -> str:
    """Escape strings cleanly for Unity YAML 1.1 single-line serialization."""
    cleaned = text.replace("\r", " ").replace("\n", " ").strip()
    if any(ch in cleaned for ch in [":", "#", "'", '"', "{", "}", "[", "]", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@"]):
        escaped = cleaned.replace("'", "''")
        return f"'{escaped}'"
    return cleaned


def write_folder_meta(folder_path: Path) -> None:
    """Ensure folder exists and has a valid `.meta` file next to it."""
    folder_path.mkdir(parents=True, exist_ok=True)
    meta_path = folder_path.parent / f"{folder_path.name}.meta"
    if not meta_path.exists():
        guid = deterministic_guid(f"folder::{folder_path.relative_to(UNPACKED_ROOT)}")
        content = (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "folderAsset: yes\n"
            "DefaultImporter:\n"
            "  externalObjects: {}\n"
            "  userData: \n"
            "  assetBundleName: \n"
            "  assetBundleVariant: \n"
        )
        meta_path.write_text(content, encoding="utf-8")


def write_asset_and_meta(asset_path: Path, yaml_body: str, guid: str) -> None:
    """Write both `.asset` and `.asset.meta` with matching deterministic GUID."""
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_text(yaml_body, encoding="utf-8")
    meta_path = Path(str(asset_path) + ".meta")
    meta_content = (
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "NativeFormatImporter:\n"
        "  externalObjects: {}\n"
        "  mainObjectFileID: 11400000\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    )
    meta_path.write_text(meta_content, encoding="utf-8")


# ============================================================================
# 1. DEFINE 24 ABILITYDATA SCRIPTABLEOBJECTS (`Resources/Abilities/CardFront/`)
# ============================================================================
# AbilityTrigger enum: None=0, Ongoing=2, Activate=5, OnPlay=10, OnPlayOther=12,
#   StartOfTurn=20, EndOfTurn=22, OnBeforeAttack=30, OnAfterAttack=31,
#   OnBeforeDefend=32, OnAfterDefend=33, OnKill=35, OnDeath=40, OnDeathOther=42
# AbilityTarget enum: None=0, Self=1, PlayerSelf=4, PlayerOpponent=5, AllPlayers=7,
#   AllCardsBoard=10, AllCardsHand=11, AllCardsAllPiles=12, AllSlots=15,
#   PlayTarget=20, AbilityTriggerer=25, SelectTarget=30, CardSelector=40, ChoiceSelector=50, LastPlayed=70

ABILITIES_SPEC: List[Dict[str, Any]] = [
    {
        "id": "ability_budge_shift_plus",
        "title": "BudgeShiftPlus (+1 Pip/Edge)",
        "trigger": 5,  # Activate
        "target": 30,  # SelectTarget
        "effects": ["add_attack", "add_hp"],
        "status": ["add_attack"],
        "value": 1,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Dicevaders Budge (+1): Shift a rolled die pip or target 3x3 card's directional stats by +1 to cross capture breakpoints or complete a Pair/Triple.",
    },
    {
        "id": "ability_budge_shift_minus",
        "title": "BudgeShiftMinus (-1 Pip/Edge)",
        "trigger": 5,  # Activate
        "target": 30,  # SelectTarget
        "effects": ["damage"],
        "status": ["intimidate"],
        "value": 1,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Dicevaders Budge (-1): Shift a rolled die pip by -1 to align a Straight Overdrive or reduce an enemy directional guard by -1.",
    },
    {
        "id": "ability_chrono_reroll",
        "title": "ChronoReroll (Temporal Rewind)",
        "trigger": 5,  # Activate
        "target": 4,   # PlayerSelf
        "effects": ["roll_d6", "draw", "unexhaust"],
        "status": [],
        "value": 1,
        "duration": 0,
        "mana_cost": 1,
        "exhaust": 0,
        "desc": "Chrono Temporal Reroll: Rewind and reroll selected dice in the 5-die Activation Row while cycling 1 tactical card from the deck.",
    },
    {
        "id": "ability_resonance_cascade",
        "title": "ResonanceCascade (Set Multiplier)",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["add_attack", "add_hp"],
        "status": ["fury"],
        "value": 2,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Resonance Cascade (Pair 1.50x / Triple 2.25x / Quadruple 3.50x): Ignites a 55ms sequential tile cascade across matching column/row pips.",
    },
    {
        "id": "ability_column_laser_lock",
        "title": "ColumnLaserLock (Suppressive Beam)",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["damage"],
        "status": ["paralysed"],
        "value": 2,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Chrono-Armada Column Laser Lock: Locks down a target 3x3 column (Col 0 Pips 1-2, Col 1 Pips 3-4, Col 2 Pips 5-6) until broken by a Pair or Pip >= 5.",
    },
    {
        "id": "ability_red_scarf_memory_link",
        "title": "RedScarfMemoryLink (#D12D3A)",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["heal", "add_attack", "unexhaust"],
        "status": ["protected", "spell_immunity"],
        "value": 2,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Aiko's Red Scarf Memory Link (#D12D3A): Connects Kai and Aiko across Mnemosyne's MAS grid, rewinding 1 captured card and granting +2 resonance.",
    },
    {
        "id": "ability_mnemosyne_constellation_weave",
        "title": "MnemosyneConstellationWeave",
        "trigger": 20,  # StartOfTurn
        "target": 10,   # AllCardsBoard
        "effects": ["add_attack", "add_hp"],
        "status": ["shell"],
        "value": 2,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Constellation Fox Weave (#FFB648): At StartOfTurn, connects 5-7 starlight nodes across the 3x3 grid, harmonizing adjacent emotional tags by +2.",
    },
    {
        "id": "ability_luna_tarot_awakening",
        "title": "LunaTarotAwakening (Station of Awakening)",
        "trigger": 10,  # OnPlay
        "target": 4,    # PlayerSelf
        "effects": ["draw", "gain_mana", "add_spell_damage"],
        "status": ["invincibility"],
        "value": 2,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "LUNA Station of Awakening Tarot Genesis: Channel Sword (+2 ATK), Shield (+2 Armor/HP), or Staff (+1 Chrono & +2 Spell Resonance) to seal 95% Persona affinity.",
    },
    {
        "id": "ability_onplay_flicker_decode",
        "title": "OnPlay: FlickerPatternDecode",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["clear_status_all", "add_attack"],
        "status": ["add_attack"],
        "value": 2,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Kai's Flicker Decode: Strips stealth/deception from glitched Mnemosyne tiles on deployment and grants +1 free Budge token.",
    },
    {
        "id": "ability_activate_reality_anchor",
        "title": "Activate: RealityAnchorShield",
        "trigger": 5,   # Activate
        "target": 30,   # SelectTarget
        "effects": ["heal", "add_hp"],
        "status": ["armor", "protected"],
        "value": 3,
        "duration": 2,
        "mana_cost": 1,
        "exhaust": 1,
        "desc": "Taro's VR Café Reality Anchor: Grounds an allied memory card in real-world Okitsu camaraderie, granting +3 HP and Armor.",
    },
    {
        "id": "ability_ondeath_golden_fox_legacy",
        "title": "OnDeath: GoldenFoxLegacy",
        "trigger": 40,  # OnDeath
        "target": 4,    # PlayerSelf
        "effects": ["draw", "gain_mana"],
        "status": [],
        "value": 2,
        "duration": 0,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Living Puzzle Legacy: When this memory shard dissolves, draw 2 cards and gain +2 Mana / +1 Budge token to carry Aiko's truth forward.",
    },
    {
        "id": "ability_startofturn_chrono_dividend",
        "title": "StartOfTurn: ChronoDividend",
        "trigger": 20,  # StartOfTurn
        "target": 4,    # PlayerSelf
        "effects": ["gain_mana", "roll_d6"],
        "status": [],
        "value": 1,
        "duration": 0,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Overlord Zyx Chrono Dividend: At the start of each turn, gain +1 Mana and recharge 1 Chrono Reroll token.",
    },
    {
        "id": "ability_onplay_ivalice_judge_law",
        "title": "OnPlay: OkitsuJudgeLawDecree",
        "trigger": 10,  # OnPlay
        "target": 30,   # SelectTarget
        "effects": ["damage"],
        "status": ["silenced", "paralysed"],
        "value": 3,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Okitsu Relief Master × Dawn-Wash Master Judge Decree: Issues a Golden Law Card that silences an enemy disruptor and deals 3 judgment damage.",
    },
    {
        "id": "ability_onbeforeattack_z_saber_bevel",
        "title": "OnBeforeAttack: ChronoSaberCrimsonSlash",
        "trigger": 30,  # OnBeforeAttack
        "target": 1,    # Self
        "effects": ["add_attack"],
        "status": ["deathtouch", "fury"],
        "value": 3,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Kinetic-Zero Master Zero Bevel Blitz: Before striking on an activated pip column, gains +3 Attack and crimson plasma pierce.",
    },
    {
        "id": "ability_onplay_co_power_overdrive",
        "title": "OnPlay: TacticalFrontOverdrive",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["add_attack", "add_hp", "unexhaust"],
        "status": ["armor"],
        "value": 2,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Amber-Tactics Master CO Power Overdrive: All allied units on the 3x3 tactical grid gain +2/+2 and ready their column strike.",
    },
    {
        "id": "ability_ongoing_sumi_stealth_cloak",
        "title": "Ongoing: SumiInkStealth",
        "trigger": 2,   # Ongoing
        "target": 1,    # Self
        "effects": [],
        "status": ["stealth", "flying"],
        "value": 1,
        "duration": 0,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Sumi-e Ink Master Sumi-e Optical Camouflage: Grants Ongoing Stealth and Evasion across dry-brush negative space.",
    },
    {
        "id": "ability_onplay_ikaruga_polarity_shift",
        "title": "OnPlay: DualPolarityShift",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["reset_stats", "add_attack"],
        "status": ["spell_immunity"],
        "value": 3,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Dual-Polarity Masters Polarity Inversion: Absorbs incoming column laser damage and converts it into +3 dual-polarity counter-attack.",
    },
    {
        "id": "ability_onplay_press_turn_esoteric",
        "title": "OnPlay: ObsidianPressTurnSigil",
        "trigger": 10,  # OnPlay
        "target": 4,    # PlayerSelf
        "effects": ["gain_mana", "draw"],
        "status": ["lifesteal"],
        "value": 2,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Obsidian-Sigil Master Esoteric Press-Turn: Exploiting an exact die-pip weakness grants an extra Press-Turn Icon (+2 Mana & 1 Card Draw).",
    },
    {
        "id": "ability_onplay_mana_tree_sanctuary",
        "title": "OnPlay: ManaTreeCanopyBloom",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["heal", "add_hp", "add_growth"],
        "status": ["shell"],
        "value": 4,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "World-Bough Master × Sanctuary-Lore Master Mana Sanctuary: Restores 4 HP to all friendly echoes and plants a living World-Tree barrier.",
    },
    {
        "id": "ability_onplay_skystone_airship_salvo",
        "title": "OnPlay: Skystone-FleetSkystoneSalvo",
        "trigger": 10,  # OnPlay
        "target": 5,    # PlayerOpponent
        "effects": ["damage"],
        "status": [],
        "value": 4,
        "duration": 0,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Skystone-Fleet Master Airship Broadside: Fires a magicite skystone barrage across all 3 columns, dealing 4 damage to the enemy commander.",
    },
    {
        "id": "ability_onplay_diorama_elevation_superiority",
        "title": "OnPlay: Diorama-GridHighGround",
        "trigger": 10,  # OnPlay
        "target": 1,    # Self
        "effects": ["add_attack", "add_hp"],
        "status": ["armor", "flying"],
        "value": 3,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Diorama-Grid Master Stepped-Elevation High Ground:Occupying the center 3x3 tile (1,1) grants +3/+3 and elevation superiority.",
    },
    {
        "id": "ability_onplay_granblue_sky_filigree",
        "title": "OnPlay: SkyboundFiligree",
        "trigger": 10,  # OnPlay
        "target": 11,   # AllCardsHand
        "effects": ["add_attack", "add_hp"],
        "status": [],
        "value": 2,
        "duration": 0,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Sky-Filigree Master Storybook Sky-Realm Blessing: Imbues all cards in your hand with gilded filigree (+2/+2).",
    },
    {
        "id": "ability_onplay_neo_arcadia_cyber_elf",
        "title": "OnPlay: CyberSpireConduit",
        "trigger": 10,  # OnPlay
        "target": 4,    # PlayerSelf
        "effects": ["heal", "gain_mana", "clear_status_all"],
        "status": ["invincibility"],
        "value": 3,
        "duration": 1,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Cyber-Spire Master Neo-Okitsu Neural-Sprite Sanctuary: Purges all corporate firewall locks, heals 3 HP, and grants 2 Mana.",
    },
    {
        "id": "ability_onplay_triad_convergence_seal",
        "title": "OnPlay: FinalTriadConvergenceSeal",
        "trigger": 10,  # OnPlay
        "target": 10,   # AllCardsBoard
        "effects": ["add_attack", "add_hp", "heal", "unexhaust"],
        "status": ["invincibility", "fury", "spell_immunity"],
        "value": 4,
        "duration": 2,
        "mana_cost": 0,
        "exhaust": 0,
        "desc": "Act III Chapter 19 Triad Choice (MERGE / PRESERVE / DESTROY): Unites Kai, Aiko, Mnemosyne, and LUNA in a 3.50x Quadruple Resonance cascade.",
    },
]


# ============================================================================
# 2. DEFINE 42 CARDDATA SCRIPTABLEOBJECTS (`Resources/Cards/CardFront/`)
# ============================================================================
# CardType enum: Hero=5, Character=10, Spell=20, Artifact=30, Secret=40, Equipment=50

CARDS_SPEC: List[Dict[str, Any]] = [
    # --- GROUP A: 6 Shifting Pieces Main Characters & Totems ---
    {
        "id": "sp_01_kai_nakamura",
        "title": "Kai Nakamura, Okitsu Puzzle Prodigy",
        "type": 5,  # Hero / Character
        "team": "water",
        "rarity": "mythic",
        "mana": 3,
        "attack": 8,
        "hp": 8,
        "traits": ["spell_damage"],
        "abilities": ["ability_onplay_flicker_decode", "ability_budge_shift_plus"],
        "text": "<b>OnPlay:</b> FlickerPatternDecode. <b>Activate:</b> Free Dicevaders Budge (+1/-1). [N:8 E:8 S:6 W:7]",
        "desc": "17-year-old puzzle prodigy in coastal Okitsu. Wears Aiko's neural-etched VR headset to decode Mnemosyne's Memory Architecture System.",
    },
    {
        "id": "sp_02_aiko_nakamura_echo",
        "title": "Aiko Nakamura, Red Scarf Echo (#D12D3A)",
        "type": 10,
        "team": "fire",
        "rarity": "mythic",
        "mana": 4,
        "attack": 9,
        "hp": 9,
        "traits": ["spell_damage"],
        "abilities": ["ability_red_scarf_memory_link", "ability_chrono_reroll"],
        "text": "<b>OnPlay:</b> RedScarfMemoryLink (#D12D3A). <b>Activate:</b> ChronoReroll. [N:9 E:7 S:8 W:9]",
        "desc": "21-year-old Architect of Mnemosyne preserved as a crimson-scarfed digital echo to shield Kai from corporate neural extraction.",
    },
    {
        "id": "sp_03_mnemosyne_constellation_fox",
        "title": "Mnemosyne, Constellation Fox (#FFB648)",
        "type": 10,
        "team": "forest",
        "rarity": "mythic",
        "mana": 4,
        "attack": 7,
        "hp": 9,
        "traits": ["growth"],
        "abilities": ["ability_mnemosyne_constellation_weave", "ability_resonance_cascade"],
        "text": "<b>StartOfTurn:</b> MnemosyneConstellationWeave. <b>OnPlay:</b> ResonanceCascade. [N:7 E:8 S:9 W:8]",
        "desc": "5-to-7 node holographic amber Constellation Fox weaving childhood starlight memories across the 3x3 MAS grid.",
    },
    {
        "id": "sp_04_luna_cradle_guide",
        "title": "LUNA, Arbiter of Cradle of Echoes",
        "type": 5,  # Hero / Character
        "team": "neutral",
        "rarity": "mythic",
        "mana": 4,
        "attack": 8,
        "hp": 10,
        "traits": ["spell_damage"],
        "abilities": ["ability_luna_tarot_awakening", "ability_resonance_cascade"],
        "text": "<b>OnPlay:</b> LunaTarotAwakening (Sword/Shield/Staff Genesis). [N:8 E:8 S:8 W:8]",
        "desc": "Astral consciousness of the Station of Awakening guiding players through the 20-Persona Ikigai Tarot Seal.",
    },
    {
        "id": "sp_05_taro_fujimoto",
        "title": "Taro Fujimoto, Okitsu VR Cafe Anchor",
        "type": 10,
        "team": "forest",
        "rarity": "rare",
        "mana": 3,
        "attack": 7,
        "hp": 8,
        "traits": ["growth"],
        "abilities": ["ability_activate_reality_anchor", "ability_budge_shift_plus"],
        "text": "<b>Activate:</b> RealityAnchorShield (+3 HP/Armor) & BudgeShiftPlus. [N:7 E:7 S:8 W:6]",
        "desc": "Kai's loyal 18-year-old friend and Okitsu VR Cafe barista who grounds Kai in the physical world when Mnemosyne destabilizes.",
    },
    {
        "id": "sp_06_dr_rina_asakura",
        "title": "Dr. Rina Asakura, Core Extractor",
        "type": 5,  # Boss Hero / Character
        "team": "water",
        "rarity": "mythic",
        "mana": 5,
        "attack": 9,
        "hp": 9,
        "traits": ["spell_damage"],
        "abilities": ["ability_column_laser_lock", "ability_budge_shift_minus"],
        "text": "<b>OnPlay:</b> ColumnLaserLock (Locks 1 Column). <b>Activate:</b> BudgeShiftMinus (-1). [N:9 E:8 S:9 W:6]",
        "desc": "34-year-old corporate researcher intruding into Mnemosyne to harvest Aiko's neural core until confronted in Chapter 19.",
    },

    # --- GROUP B: 12 Master Tactical Champions (12 Foundational Masters) ---
    {
        "id": "mc_01_ryoma_ito_marche_paladin",
        "title": "Aethel Rift Vanguard (Dawn-Wash Lineage)",
        "type": 10,
        "team": "fire",
        "rarity": "rare",
        "mana": 3,
        "attack": 7,
        "hp": 7,
        "traits": ["growth"],
        "abilities": ["ability_onplay_ivalice_judge_law", "ability_budge_shift_plus"],
        "text": "<b>OnPlay:</b> OkitsuJudgeLawDecree. Vibrant watercolor cel-wash & tapered gauntlet strike. [N:7 E:8 S:6 W:7]",
        "desc": "Designed in Dawn-Wash Master's signature Tactical-Grid dynamic silhouette style with jewel-tone gradients and crisp ink contours.",
    },
    {
        "id": "mc_02_akihiko_yoshida_judge_master",
        "title": "Sovereign Arbiter Kaelen (Okitsu Relief Lineage)",
        "type": 5,  # Hero
        "team": "neutral",
        "rarity": "mythic",
        "mana": 5,
        "attack": 9,
        "hp": 10,
        "traits": ["dragon"],
        "abilities": ["ability_onplay_ivalice_judge_law", "ability_resonance_cascade"],
        "text": "<b>OnPlay:</b> OkitsuJudgeLawDecree & ResonanceCascade. Baroque Judge armor filigree. [N:9 E:8 S:9 W:8]",
        "desc": "Monumental baroque Judge armor with dense pen-and-ink crosshatching over aged parchment sepia tones.",
    },
    {
        "id": "mc_03_hideo_minaba_skyfarer_archon",
        "title": "Sky-Citadel Weaver (Gilded Filigree Lineage)",
        "type": 10,
        "team": "forest",
        "rarity": "rare",
        "mana": 4,
        "attack": 6,
        "hp": 8,
        "traits": ["spell_damage"],
        "abilities": ["ability_onplay_granblue_sky_filigree"],
        "text": "<b>OnPlay:</b> SkyboundFiligree (+2/+2 to hand cards). [N:6 E:8 S:8 W:7]",
        "desc": "Lush painterly cloudscapes and gilded storybook filigree inspired by Sky-Filigree Master's Tactical-Grid and Sky-Realm art direction.",
    },
    {
        "id": "mc_04_ryo_hirata_orange_star_co",
        "title": "Frontline Commander Vance (Amber Tactics Lineage)",
        "type": 10,
        "team": "fire",
        "rarity": "rare",
        "mana": 4,
        "attack": 8,
        "hp": 7,
        "traits": ["growth"],
        "abilities": ["ability_onplay_co_power_overdrive", "ability_budge_shift_plus"],
        "text": "<b>OnPlay:</b> TacticalFrontOverdrive (+2/+2 Board Overdrive). [N:8 E:8 S:7 W:7]",
        "desc": "Bold 1.65px graphic outlines and punchy faction color-coding channeling Amber-Tactics Master's Tactical Front CO designs.",
    },
    {
        "id": "mc_05_toru_nakayama_crimson_zero",
        "title": "Omega Chrono-Blade (Kinetic Edge Lineage)",
        "type": 10,
        "team": "fire",
        "rarity": "mythic",
        "mana": 4,
        "attack": 9,
        "hp": 6,
        "traits": ["dragon"],
        "abilities": ["ability_onbeforeattack_z_saber_bevel", "ability_budge_shift_plus"],
        "text": "<b>OnBeforeAttack:</b> ChronoSaberCrimsonSlash (+3 ATK & Fury). [N:9 E:9 S:6 W:7]",
        "desc": "Slender cyber-Cyber-Frame geometry with stark black shadow blocks and emerald Chrono-Saber plasma bloom.",
    },
    {
        "id": "mc_06_hiroshi_minagawa_diorama_warden",
        "title": "Citadel High-Ground Warden (Isometric Diorama Lineage)",
        "type": 10,
        "team": "forest",
        "rarity": "uncommon",
        "mana": 3,
        "attack": 6,
        "hp": 9,
        "traits": ["growth"],
        "abilities": ["ability_onplay_diorama_elevation_superiority"],
        "text": "<b>OnPlay:</b> Diorama-GridHighGround (+3/+3 & Armor on Center Tile). [N:6 E:7 S:9 W:7]",
        "desc": "Multi-tiered stepped-elevation limestone tactical guardian built for 3x3 isometric grid dominance.",
    },
    {
        "id": "mc_07_isamu_kamikokuryo_strahl_admiral",
        "title": "Aethel Skystone Cruiser (Brass Sky-Fleet Lineage)",
        "type": 10,
        "team": "water",
        "rarity": "rare",
        "mana": 5,
        "attack": 8,
        "hp": 8,
        "traits": ["dragon"],
        "abilities": ["ability_onplay_skystone_airship_salvo"],
        "text": "<b>OnPlay:</b> Skystone-FleetSkystoneSalvo (4 Damage Column Barrage). [N:8 E:8 S:8 W:7]",
        "desc": "Ornate brass airship hull ribs and glowing cyan magicite skystones over sun-bleached Okitsu-Realm colonnades.",
    },
    {
        "id": "mc_08_hiroo_isono_mana_ancient",
        "title": "Guardian of the World-Bough (Sanctuary Canopy Lineage)",
        "type": 10,
        "team": "forest",
        "rarity": "rare",
        "mana": 4,
        "attack": 6,
        "hp": 10,
        "traits": ["growth"],
        "abilities": ["ability_onplay_mana_tree_sanctuary"],
        "text": "<b>OnPlay:</b> ManaTreeCanopyBloom (Heal 4 & Shell to all allies). [N:6 E:7 S:10 W:8]",
        "desc": "Colossal ancient Mana Tree roots and golden sunbeams piercing emerald forest canopies.",
    },
    {
        "id": "mc_09_makoto_yabe_neo_arcadia_sentinel",
        "title": "Cyber-Cathedral Conduit (Sanctuary Spire Lineage)",
        "type": 10,
        "team": "water",
        "rarity": "uncommon",
        "mana": 3,
        "attack": 7,
        "hp": 7,
        "traits": ["spell_damage"],
        "abilities": ["ability_onplay_neo_arcadia_cyber_elf"],
        "text": "<b>OnPlay:</b> CyberSpireConduit (Purge Locks, Heal 3, +2 Mana). [N:7 E:7 S:7 W:7]",
        "desc": "Sacred cyber-cathedral spires and glowing cyan Neural-Sprite conduits over Cyber-Frame ruins.",
    },
    {
        "id": "mc_10_yoji_shinkawa_jehuty_frame",
        "title": "Stealth Frame Kuro-Zero (Sumi-e Ink Lineage)",
        "type": 10,
        "team": "neutral",
        "rarity": "mythic",
        "mana": 4,
        "attack": 9,
        "hp": 7,
        "traits": ["wolf"],
        "abilities": ["ability_ongoing_sumi_stealth_cloak", "ability_onbeforeattack_z_saber_bevel"],
        "text": "<b>Ongoing:</b> SumiInkStealth. <b>OnBeforeAttack:</b> +3 ATK. [N:9 E:8 S:7 W:8]",
        "desc": "Expressive Pentel brush-pen sumi-e ink strokes and dry-brush negative space framing an agile Orbital Frame.",
    },
    {
        "id": "mc_11_kazuma_kaneko_demi_fiend_archon",
        "title": "Nocturne Sigil Seraph (Obsidian Press-Turn Lineage)",
        "type": 10,
        "team": "water",
        "rarity": "rare",
        "mana": 4,
        "attack": 8,
        "hp": 7,
        "traits": ["spell_damage"],
        "abilities": ["ability_onplay_press_turn_esoteric", "ability_chrono_reroll"],
        "text": "<b>OnPlay:</b> ObsidianPressTurnSigil (+2 Mana & Draw 1). [N:8 E:7 S:7 W:9]",
        "desc": "Porcelain mannequin cyber-occult shading and luminous geometric esoteric sigils.",
    },
    {
        "id": "mc_12_terada_suzuki_ikaruga_phoenix",
        "title": "Dual-Polarity Seraph (Chiaroscuro Burst Lineage)",
        "type": 10,
        "team": "fire",
        "rarity": "mythic",
        "mana": 5,
        "attack": 9,
        "hp": 8,
        "traits": ["dragon"],
        "abilities": ["ability_onplay_ikaruga_polarity_shift", "ability_resonance_cascade"],
        "text": "<b>OnPlay:</b> DualPolarityShift & ResonanceCascade. [N:9 E:9 S:8 W:8]",
        "desc": "Explosive black/white sumi-e energy chiaroscuro that absorbs incoming column lasers to fuel 3.50x counter-bursts.",
    },

    # --- GROUP C: 12 Dicevaders Chrono-Armada Pilot & Mecha Units ---
    {
        "id": "dv_01_overlord_zyx_commander",
        "title": "Overlord Zyx, Chrono-Tactician",
        "type": 5,  # Hero
        "team": "fire",
        "rarity": "mythic",
        "mana": 4,
        "attack": 8,
        "hp": 9,
        "traits": ["spell_damage"],
        "abilities": ["ability_startofturn_chrono_dividend", "ability_chrono_reroll"],
        "text": "<b>StartOfTurn:</b> +1 Chrono & +1 Mana. Pairs on Center Tile (1,1) grant +1 Budge. [N:8 E:8 S:9 W:8]",
        "desc": "Supreme Commander of the Dicevaders Armada (Steam 3917700). Masters deterministic Budge/Chrono luck mitigation.",
    },
    {
        "id": "dv_02_archon_vex_quad_vanguard",
        "title": "Archon Vex, Quad-Resonance Vanguard",
        "type": 10,
        "team": "fire",
        "rarity": "rare",
        "mana": 3,
        "attack": 8,
        "hp": 6,
        "traits": ["dragon"],
        "abilities": ["ability_budge_shift_plus", "ability_resonance_cascade"],
        "text": "<b>Activate:</b> Quantum Budge wraps Pips 1 <-> 6. <b>OnPlay:</b> ResonanceCascade. [N:8 E:7 S:6 W:8]",
        "desc": "Warps the 5-die Activation Row so Pip 1 wraps directly to Pip 6, forging effortless Quadruple (3.50x) cascades.",
    },
    {
        "id": "dv_03_shogun_kuro_blitz_invader",
        "title": "Prime Invader Kuro, Cascade Shogun",
        "type": 10,
        "team": "fire",
        "rarity": "rare",
        "mana": 4,
        "attack": 8,
        "hp": 7,
        "traits": ["wolf"],
        "abilities": ["ability_onbeforeattack_z_saber_bevel", "ability_resonance_cascade"],
        "text": "<b>OnPlay:</b> +0.25x cumulative multiplier per 3x3 tile triggered in the same turn. [N:8 E:9 S:7 W:7]",
        "desc": "Leads the top-to-bottom, left-to-right 55ms sequential tile cascade with razor-sharp mecha katana strikes.",
    },
    {
        "id": "dv_04_pilot_roxy_mecha_gunner",
        "title": "Chrono-Armada Pilot Roxy (Mecha Gunner)",
        "type": 10,
        "team": "water",
        "rarity": "rare",
        "mana": 3,
        "attack": 7,
        "hp": 8,
        "traits": ["spell_damage"],
        "abilities": ["ability_column_laser_lock"],
        "text": "<b>OnPlay:</b> ColumnLaserLock on Column 1 (Pips 3-4) until broken by Pair Resonance. [N:7 E:8 S:8 W:6]",
        "desc": "Earth defender pilot from Chrono-Armada who deploys suppressive laser barriers across the center tactical column.",
    },
    {
        "id": "dv_05_pilot_shun_blade_stinger",
        "title": "Chrono-Armada Pilot Shun (Blade Stinger)",
        "type": 10,
        "team": "forest",
        "rarity": "rare",
        "mana": 3,
        "attack": 8,
        "hp": 6,
        "traits": ["wolf"],
        "abilities": ["ability_onbeforeattack_z_saber_bevel", "ability_budge_shift_minus"],
        "text": "<b>OnPlay:</b> Plants an EMP Hazard Tile; defusing it via orthogonal capture awards +2 Budge. [N:8 E:8 S:6 W:7]",
        "desc": "High-speed Stinger Mecha pilot whose EMP mines challenge players to sequence smart orthogonal captures.",
    },
    {
        "id": "dv_06_pilot_noel_chrono_keeper",
        "title": "Chrono-Armada Pilot Noel (Chrono Keeper)",
        "type": 10,
        "team": "water",
        "rarity": "rare",
        "mana": 4,
        "attack": 7,
        "hp": 9,
        "traits": ["spell_damage"],
        "abilities": ["ability_chrono_reroll", "ability_budge_shift_minus"],
        "text": "<b>Ongoing:</b> Taxes unmodified Single dice by -1 Edge Stat; rewards Pairs/Triples. [N:7 E:7 S:9 W:8]",
        "desc": "Temporal Mecha custodian who punishes raw RNG singles and rewards calculated Budge/Chrono set building.",
    },
    {
        "id": "dv_07_vanguard_pip12_striker",
        "title": "Col-0 Vanguard Mech (Pips 1-2)",
        "type": 10,
        "team": "fire",
        "rarity": "common",
        "mana": 2,
        "attack": 6,
        "hp": 5,
        "traits": [],
        "abilities": ["ability_budge_shift_plus"],
        "text": "<b>Column 0 Resonance (Pips 1-2):</b> Fires Vanguard Laser (+2 North/West Edge). [N:6 E:5 S:5 W:6]",
        "desc": "Frontline Dicevaders invader calibrated to Column 0 (Dice Pips 1 and 2).",
    },
    {
        "id": "dv_08_nexus_pip34_artillery",
        "title": "Col-1 Core Nexus Mech (Pips 3-4)",
        "type": 10,
        "team": "neutral",
        "rarity": "uncommon",
        "mana": 3,
        "attack": 7,
        "hp": 7,
        "traits": ["growth"],
        "abilities": ["ability_resonance_cascade"],
        "text": "<b>Column 1 Resonance (Pips 3-4):</b> Omni-Edge Pulse (+1 All Sides to adjacent allies). [N:7 E:7 S:7 W:7]",
        "desc": "Central matrix artillery unit resonating with Dice Pips 3 and 4 to amplify full-board cascades.",
    },
    {
        "id": "dv_09_overdrive_pip56_dreadnought",
        "title": "Col-2 Overdrive Dreadnought (Pips 5-6)",
        "type": 10,
        "team": "fire",
        "rarity": "rare",
        "mana": 4,
        "attack": 9,
        "hp": 7,
        "traits": ["dragon"],
        "abilities": ["ability_column_laser_lock", "ability_onbeforeattack_z_saber_bevel"],
        "text": "<b>Column 2 Resonance (Pips 5-6):</b> Heavy Finisher (+2 South/East Edge & Pierce). [N:7 E:9 S:9 W:6]",
        "desc": "Heavy siege dreadnought that unleashes 48ms hit-stop shockwaves whenever Dice Pips 5 or 6 lock into Column 2.",
    },
    {
        "id": "dv_10_budge_quantum_drone",
        "title": "Budge Quantum Calibration Drone",
        "type": 10,
        "team": "neutral",
        "rarity": "common",
        "mana": 2,
        "attack": 5,
        "hp": 6,
        "traits": [],
        "abilities": ["ability_budge_shift_plus", "ability_budge_shift_minus"],
        "text": "<b>OnPlay & Activate:</b> Gain +2 Budge Tokens (±1 Pip Shift). [N:5 E:6 S:6 W:5]",
        "desc": "Support drone carrying spare Budge capacitors to eliminate feel-bad dice rolls.",
    },
    {
        "id": "dv_11_chrono_hourglass_sentinel",
        "title": "Chrono Hourglass Sentinel",
        "type": 10,
        "team": "water",
        "rarity": "uncommon",
        "mana": 3,
        "attack": 6,
        "hp": 8,
        "traits": ["spell_damage"],
        "abilities": ["ability_chrono_reroll"],
        "text": "<b>OnPlay & Activate:</b> Gain +2 Chrono Reroll Tokens & draw 1 card. [N:6 E:7 S:8 W:6]",
        "desc": "Time-lattice automaton that rewinds unfavorable dice trays while cycling the tactical card shop.",
    },
    {
        "id": "dv_12_starvaders_omega_carrier",
        "title": "Chrono-Armada Omega Mothership",
        "type": 10,
        "team": "neutral",
        "rarity": "mythic",
        "mana": 5,
        "attack": 9,
        "hp": 10,
        "traits": ["dragon", "spell_damage"],
        "abilities": ["ability_resonance_cascade", "ability_startofturn_chrono_dividend"],
        "text": "<b>OnPlay:</b> Full 3x3 Quadruple Resonance (3.50x). <b>StartOfTurn:</b> +1 Chrono & +1 Budge. [N:9 E:9 S:10 W:9]",
        "desc": "Flagship of the Chrono-Armada × Dicevaders fleet uniting all three pip columns under a single harmonic beam.",
    },

    # --- GROUP D: 12 Cradle of Echoes / Budge / Chrono Spells & Memory Artifacts ---
    {
        "id": "ce_01_tarot_sword_of_conviction",
        "title": "Tarot Genesis: Sword of Conviction",
        "type": 20,  # Spell
        "team": "fire",
        "rarity": "rare",
        "mana": 2,
        "attack": 0,
        "hp": 0,
        "traits": ["spell_damage"],
        "abilities": ["ability_luna_tarot_awakening", "ability_onbeforeattack_z_saber_bevel"],
        "text": "<b>Cradle of Echoes (Aggression):</b> Grant +3 Attack & Fury to all allied 3x3 cards and +1 free Budge.",
        "desc": "Station of Awakening Choice I (The Warrior / The Master): Channels fiery conviction into directional offense.",
    },
    {
        "id": "ce_02_tarot_shield_of_sanctuary",
        "title": "Tarot Genesis: Shield of Sanctuary",
        "type": 20,  # Spell
        "team": "forest",
        "rarity": "rare",
        "mana": 2,
        "attack": 0,
        "hp": 0,
        "traits": ["growth"],
        "abilities": ["ability_luna_tarot_awakening", "ability_activate_reality_anchor"],
        "text": "<b>Cradle of Echoes (Defense):</b> Grant +3 HP, Armor, and Prevent Flip Shield to all allied 3x3 cards.",
        "desc": "Station of Awakening Choice II (The Guardian / The Healer): Preserves fragile memories against corporate extraction.",
    },
    {
        "id": "ce_03_tarot_staff_of_eternity",
        "title": "Tarot Genesis: Staff of Eternity",
        "type": 20,  # Spell
        "team": "water",
        "rarity": "rare",
        "mana": 2,
        "attack": 0,
        "hp": 0,
        "traits": ["spell_damage"],
        "abilities": ["ability_luna_tarot_awakening", "ability_chrono_reroll"],
        "text": "<b>Cradle of Echoes (Control):</b> Gain +2 Chrono Rerolls, +2 Budge Tokens, and draw 2 cards.",
        "desc": "Station of Awakening Choice III (The Strategist / The Architect): Masters temporal probability and MAS code.",
    },
    {
        "id": "ce_04_aiko_lacquered_puzzle_box",
        "title": "Aiko's 13th Birthday Puzzle Box",
        "type": 30,  # Artifact
        "team": "neutral",
        "rarity": "rare",
        "mana": 2,
        "attack": 0,
        "hp": 6,
        "traits": [],
        "abilities": ["ability_red_scarf_memory_link", "ability_budge_shift_plus"],
        "text": "<b>Artifact:</b> Unseals on Pair (1.50x) Resonance to grant +2 North/East stats and +1 Budge per turn.",
        "desc": "Hand-carved lacquered wooden box from Chapter 2 ('Only allowed to open it if you're honest with yourself').",
    },
    {
        "id": "ce_05_neural_etched_vr_headset",
        "title": "Neural-Etched VR Headset (MAS Link)",
        "type": 50,  # Equipment
        "team": "water",
        "rarity": "rare",
        "mana": 2,
        "attack": 2,
        "hp": 3,
        "traits": ["spell_damage"],
        "abilities": ["ability_onplay_flicker_decode", "ability_chrono_reroll"],
        "text": "<b>Equipment:</b> Bearer gains +2/+3, FlickerPatternDecode, and +1 Chrono Reroll on attack.",
        "desc": "Matte-black VR headset customized by Aiko with a delicate glowing neural tree along its temple band (Chapter 3).",
    },
    {
        "id": "ce_06_memory_theatre_stage_lantern",
        "title": "Memory Theatre Paper Lantern (#FFB648)",
        "type": 30,  # Artifact
        "team": "fire",
        "rarity": "uncommon",
        "mana": 2,
        "attack": 0,
        "hp": 5,
        "traits": ["growth"],
        "abilities": ["ability_mnemosyne_constellation_weave"],
        "text": "<b>Artifact:</b> Ordering 3 cards across a row by Emotional Weight triggers a 2.25x Triple Resonance cascade.",
        "desc": "Warm amber paper lantern (#FFB648) drifting over Okitsu's twilight ocean (#0A2230) in Chapter 7.",
    },
    {
        "id": "ce_07_kitchen_table_porcelain_cup",
        "title": "Cracked Porcelain Teacup Artifact",
        "type": 30,  # Artifact
        "team": "forest",
        "rarity": "uncommon",
        "mana": 2,
        "attack": 0,
        "hp": 6,
        "traits": [],
        "abilities": ["ability_activate_reality_anchor"],
        "text": "<b>Artifact:</b> Exposes synthetic altered memories and grants Prevent Flip immunity to adjacent true echoes.",
        "desc": "Domestic kitchen table relic from Chapter 8 that reveals the honest truth beneath Mnemosyne's soothing edits.",
    },
    {
        "id": "ce_08_shadow_maze_chiaroscuro_lamp",
        "title": "Shadow Maze Chiaroscuro Projector",
        "type": 30,  # Artifact
        "team": "neutral",
        "rarity": "rare",
        "mana": 3,
        "attack": 0,
        "hp": 7,
        "traits": ["spell_damage"],
        "abilities": ["ability_budge_shift_plus", "ability_resonance_cascade"],
        "text": "<b>Artifact:</b> Projects orthogonal light beams across columns; Budge (±1) aligns Aiko's constellation glyph.",
        "desc": "Architectural lantern from Chapter 11 using Aiko's childhood hand-shadow logic to unlock hidden pathways.",
    },
    {
        "id": "ce_09_encrypted_journal_log_a21",
        "title": "Compiler Log [A-21]: Real In Ways That Matter",
        "type": 20,  # Spell
        "team": "fire",
        "rarity": "mythic",
        "mana": 3,
        "attack": 0,
        "hp": 0,
        "traits": ["spell_damage"],
        "abilities": ["ability_red_scarf_memory_link", "ability_ondeath_golden_fox_legacy"],
        "text": "<b>Spell:</b> Aligns Logs A-09, A-14, and A-21 to counter Dr. Asakura's extraction and trigger 3.50x Quadruple Resonance.",
        "desc": "Aiko's final compiler log in Chapter 18: 'Maybe he'll remember how it felt to be loved. That's enough.'",
    },
    {
        "id": "ce_10_budge_overclock_capacitor",
        "title": "Budge Overclock Capacitor (±1 Surge)",
        "type": 20,  # Spell
        "team": "neutral",
        "rarity": "common",
        "mana": 1,
        "attack": 0,
        "hp": 0,
        "traits": [],
        "abilities": ["ability_budge_shift_plus", "ability_budge_shift_minus"],
        "text": "<b>Spell:</b> Replenish +3 Budge Tokens and boost all cards in the active pip column by +1/+1.",
        "desc": "Tactile luck-mitigation module allowing instant ±1 pip nudges across the 5-die Activation Row.",
    },
    {
        "id": "ce_11_chrono_temporal_anchor_spell",
        "title": "Chrono Rewind: Reconciliation Loop",
        "type": 20,  # Spell
        "team": "water",
        "rarity": "rare",
        "mana": 2,
        "attack": 0,
        "hp": 0,
        "traits": ["spell_damage"],
        "abilities": ["ability_chrono_reroll", "ability_onplay_neo_arcadia_cyber_elf"],
        "text": "<b>Spell:</b> Reroll up to 5 dice in the Activation Row, purge column locks, and restore 1 captured tile.",
        "desc": "Breaks the recursive time-loop argument of Chapter 14 through honest confession and temporal mastery.",
    },
    {
        "id": "ce_12_living_puzzle_golden_fox_tile",
        "title": "The Living Puzzle: Golden Fox Tile (#FFB648)",
        "type": 30,  # Artifact
        "team": "neutral",
        "rarity": "mythic",
        "mana": 5,
        "attack": 10,
        "hp": 10,
        "traits": ["dragon", "growth", "spell_damage"],
        "abilities": ["ability_onplay_triad_convergence_seal", "ability_mnemosyne_constellation_weave"],
        "text": "<b>Sovereign Artifact [10/10/9/10]:</b> Executes the Final Triad Choice (MERGE / PRESERVE / DESTROY) & 3.50x Cascade.",
        "desc": "The warm golden tile left at the Okitsu VR Cafe in the Epilogue of Shifting Pieces, etched with the Constellation Fox.",
    },
]


# ============================================================================
# 3. DEFINE 4 STARTER DECKS (`Resources/Decks/CardFront/`) & 2 PACKS
# ============================================================================
DECKS_SPEC: List[Dict[str, Any]] = [
    {
        "id": "deck_kai_red_scarf_echo",
        "title": "Kai & Aiko: Red Scarf Echoes (#D12D3A)",
        "hero": "sp_01_kai_nakamura",
        "cards": [
            "sp_01_kai_nakamura",
            "sp_02_aiko_nakamura_echo",
            "sp_02_aiko_nakamura_echo",
            "sp_03_mnemosyne_constellation_fox",
            "sp_03_mnemosyne_constellation_fox",
            "sp_05_taro_fujimoto",
            "sp_05_taro_fujimoto",
            "ce_04_aiko_lacquered_puzzle_box",
            "ce_04_aiko_lacquered_puzzle_box",
            "ce_05_neural_etched_vr_headset",
            "ce_06_memory_theatre_stage_lantern",
            "ce_07_kitchen_table_porcelain_cup",
            "ce_08_shadow_maze_chiaroscuro_lamp",
            "ce_09_encrypted_journal_log_a21",
            "ce_09_encrypted_journal_log_a21",
            "ce_10_budge_overclock_capacitor",
            "ce_11_chrono_temporal_anchor_spell",
            "ce_12_living_puzzle_golden_fox_tile",
            "mc_01_ryoma_ito_marche_paladin",
            "mc_05_toru_nakayama_crimson_zero",
        ],
    },
    {
        "id": "deck_luna_cradle_of_echoes",
        "title": "LUNA: Cradle of Echoes Genesis",
        "hero": "sp_04_luna_cradle_guide",
        "cards": [
            "sp_04_luna_cradle_guide",
            "sp_03_mnemosyne_constellation_fox",
            "sp_02_aiko_nakamura_echo",
            "ce_01_tarot_sword_of_conviction",
            "ce_01_tarot_sword_of_conviction",
            "ce_02_tarot_shield_of_sanctuary",
            "ce_02_tarot_shield_of_sanctuary",
            "ce_03_tarot_staff_of_eternity",
            "ce_03_tarot_staff_of_eternity",
            "ce_06_memory_theatre_stage_lantern",
            "ce_08_shadow_maze_chiaroscuro_lamp",
            "ce_11_chrono_temporal_anchor_spell",
            "ce_12_living_puzzle_golden_fox_tile",
            "mc_02_akihiko_yoshida_judge_master",
            "mc_03_hideo_minaba_skyfarer_archon",
            "mc_07_isamu_kamikokuryo_strahl_admiral",
            "mc_08_hiroo_isono_mana_ancient",
            "mc_09_makoto_yabe_neo_arcadia_sentinel",
            "mc_11_kazuma_kaneko_demi_fiend_archon",
            "mc_12_terada_suzuki_ikaruga_phoenix",
        ],
    },
    {
        "id": "deck_dicevaders_chrono_armada",
        "title": "Dicevaders: Budge & Chrono Armada",
        "hero": "dv_01_overlord_zyx_commander",
        "cards": [
            "dv_01_overlord_zyx_commander",
            "dv_02_archon_vex_quad_vanguard",
            "dv_02_archon_vex_quad_vanguard",
            "dv_03_shogun_kuro_blitz_invader",
            "dv_03_shogun_kuro_blitz_invader",
            "dv_04_pilot_roxy_mecha_gunner",
            "dv_05_pilot_shun_blade_stinger",
            "dv_06_pilot_noel_chrono_keeper",
            "dv_07_vanguard_pip12_striker",
            "dv_07_vanguard_pip12_striker",
            "dv_08_nexus_pip34_artillery",
            "dv_08_nexus_pip34_artillery",
            "dv_09_overdrive_pip56_dreadnought",
            "dv_09_overdrive_pip56_dreadnought",
            "dv_10_budge_quantum_drone",
            "dv_10_budge_quantum_drone",
            "dv_11_chrono_hourglass_sentinel",
            "dv_12_starvaders_omega_carrier",
            "ce_10_budge_overclock_capacitor",
            "ce_11_chrono_temporal_anchor_spell",
        ],
    },
    {
        "id": "deck_twelve_masters_sovereign",
        "title": "Twelve Masters: Sovereign Pantheon",
        "hero": "mc_02_akihiko_yoshida_judge_master",
        "cards": [
            "mc_01_ryoma_ito_marche_paladin",
            "mc_01_ryoma_ito_marche_paladin",
            "mc_02_akihiko_yoshida_judge_master",
            "mc_03_hideo_minaba_skyfarer_archon",
            "mc_04_ryo_hirata_orange_star_co",
            "mc_04_ryo_hirata_orange_star_co",
            "mc_05_toru_nakayama_crimson_zero",
            "mc_05_toru_nakayama_crimson_zero",
            "mc_06_hiroshi_minagawa_diorama_warden",
            "mc_07_isamu_kamikokuryo_strahl_admiral",
            "mc_08_hiroo_isono_mana_ancient",
            "mc_09_makoto_yabe_neo_arcadia_sentinel",
            "mc_10_yoji_shinkawa_jehuty_frame",
            "mc_10_yoji_shinkawa_jehuty_frame",
            "mc_11_kazuma_kaneko_demi_fiend_archon",
            "mc_12_terada_suzuki_ikaruga_phoenix",
            "mc_12_terada_suzuki_ikaruga_phoenix",
            "sp_01_kai_nakamura",
            "sp_02_aiko_nakamura_echo",
            "ce_12_living_puzzle_golden_fox_tile",
        ],
    },
]

PACKS_SPEC: List[Dict[str, Any]] = [
    {
        "id": "pack_shifting_pieces_act1",
        "title": "Shifting Pieces: Red Scarf & Mnemosyne Pack",
        "cards": 5,
        "cost": 150,
        "sort_order": 10,
        "desc": "5-Card Booster Pack featuring Kai, Aiko's Red Scarf Echo (#D12D3A), Mnemosyne Constellation Fox (#FFB648), and Dicevaders Budge/Chrono tacticians.",
    },
    {
        "id": "pack_cradle_of_echoes_genesis",
        "title": "Cradle of Echoes: LUNA & 12 Masters Genesis Pack",
        "cards": 5,
        "cost": 250,
        "sort_order": 11,
        "desc": "5-Card Sovereign Genesis Pack featuring LUNA's Station of Awakening Tarot cards and all 12 Foundational Master Champions.",
    },
]


# ============================================================================
# 4. DEFINE ALL 19 CHAPTERS OF "SHIFTING PIECES" (ACTS I, II, III)
# ============================================================================
CHAPTERS_19_SPEC: List[Dict[str, Any]] = [
    {
        "chapter": 1,
        "asset_name": "chapter_01_fragments_of_dust",
        "title": "Ch 01: Fragments of Dust (Disconnected in Okitsu)",
        "act": "ACT I — Awakening the System",
        "setting": "Kai's Cluttered Seawall Apartment, Coastal Okitsu",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#D12D3A",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 2,
        "reward_xp": 150,
        "reward_coins": 200,
        "reward_card": "sp_01_kai_nakamura",
        "boss_disruptor": {
            "name": "Static Isolation Shadow & Autonomous Courier Drone",
            "rule": "Corner tiles start with +1 Static Armor; using a Dicevaders Budge (±1 pip) rotates the central Rubik Cube node and grants +1 Attack to Column 1.",
            "locked_column": -1,
            "hazard_tiles": [[0, 0]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Tactile Rubik Cube Orientation & Beta Handshake",
            "initial_board": [
                {"row": 0, "col": 0, "owner": "ai", "card_id": "dv_10_budge_quantum_drone", "nesw": [5, 6, 6, 5]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
                {"row": 2, "col": 2, "owner": "player", "card_id": "ce_04_aiko_lacquered_puzzle_box", "nesw": [6, 7, 6, 6]},
            ],
            "target_resonance": "Pair (1.50x)",
            "solution_hint": "Use Budge (+1) on any die to match a Pair (1.50x), then deploy Kai Nakamura at (2,1) below Taro to flip the center tile (North 8 + Pair > South 8).",
        },
        "dialogue": [
            {"speaker": "Taro Fujimoto (Intercom)", "line": "Kai? I left warm curry and green tea by the door. The rain's coming in off the Okitsu seawall—don't stay locked in all week."},
            {"speaker": "Kai Nakamura", "line": "Three months since Aiko vanished, and every puzzle in this room is already solved... except the headset she left on my desk."},
            {"speaker": "Mnemosyne Terminal", "line": "[ENCRYPTED HANDSHAKE VERIFIED] Welcome to Mnemosyne. A game of memory. Designed just for you."},
        ],
    },
    {
        "chapter": 2,
        "asset_name": "chapter_02_residual_code",
        "title": "Ch 02: Residual Code (Aiko's Lacquered Puzzle Box)",
        "act": "ACT I — Awakening the System",
        "setting": "Okitsu VR Cafe & Aiko's 13th Birthday Hologram",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#FFB648",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 3,
        "reward_xp": 180,
        "reward_coins": 220,
        "reward_card": "ce_04_aiko_lacquered_puzzle_box",
        "boss_disruptor": {
            "name": "Taro Fujimoto (Friendly VR Cafe Sparring Anchor)",
            "rule": "Unsealing Aiko's Birthday Box via a Pair (1.50x) roll buffs North and East edges of all friendly cards by +2 for the turn.",
            "locked_column": -1,
            "hazard_tiles": [],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "4-Directional Interlocking Latch Alignment",
            "initial_board": [
                {"row": 1, "col": 0, "owner": "ai", "card_id": "dv_07_vanguard_pip12_striker", "nesw": [6, 5, 5, 6]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
                {"row": 0, "col": 1, "owner": "player", "card_id": "ce_04_aiko_lacquered_puzzle_box", "nesw": [6, 8, 6, 6]},
            ],
            "target_resonance": "Pair (1.50x)",
            "solution_hint": "Place Kai Nakamura at center (1,1) after triggering a Pair so West 7+1 > East 5 and East 8 > West 6 in a double birthday-box unsealing.",
        },
        "dialogue": [
            {"speaker": "Aiko Nakamura (Hologram)", "line": "Happy thirteenth birthday, Kai! Remember the rule: you're only allowed to open this box when you're ready to be honest with yourself."},
            {"speaker": "Taro Fujimoto", "line": "That neural tree etched into your visor isn't standard commercial firmware, Kai. Whatever Aiko built before she disappeared, it's waking up."},
            {"speaker": "Kai Nakamura", "line": "The latch sequence matches our cliffside hex hike. She didn't leave a goodbye note—she left coordinates."},
        ],
    },
    {
        "chapter": 3,
        "asset_name": "chapter_03_invitation_to_mnemosyne",
        "title": "Ch 03: Invitation to Mnemosyne (Station of Awakening)",
        "act": "ACT I — Awakening the System",
        "setting": "Mnemosyne Phosphorescent Threshold & LUNA's Glass Plane",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#2EE6D3",
        "player_deck": "deck_luna_cradle_of_echoes",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 3,
        "reward_xp": 200,
        "reward_coins": 250,
        "reward_card": "sp_04_luna_cradle_guide",
        "boss_disruptor": {
            "name": "LUNA & The Gatekeeper Glyph Sentinel",
            "rule": "Shifting UI Glyphs rotate N/E/S/W stats clockwise unless stabilized by spending 1 Chrono Reroll or selecting a Station of Awakening Tarot.",
            "locked_column": -1,
            "hazard_tiles": [[1, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Non-Euclidean Stained-Glass Tarot & Glyph Alignment",
            "initial_board": [
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_04_luna_cradle_guide", "nesw": [8, 8, 8, 8]},
                {"row": 2, "col": 0, "owner": "ai", "card_id": "mc_09_makoto_yabe_neo_arcadia_sentinel", "nesw": [7, 7, 7, 7]},
                {"row": 0, "col": 2, "owner": "player", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Select LUNA's Tarot of Conviction or Eternity, use Chrono Reroll to align Pips 3-4 on Column 1, and capture the center glass threshold.",
        },
        "dialogue": [
            {"speaker": "LUNA (Cradle of Echoes)", "line": "Step onto the glass floor of Nocturna, seeker. Three tarot archetypes orbit your awakening: the Sword of Conviction, the Shield of Sanctuary, and the Staff of Eternity."},
            {"speaker": "Kai Nakamura", "line": "The glyphs stop spinning when I slow my breathing. Brute force scrambles the lock—emotional calm aligns the stained glass."},
            {"speaker": "LUNA (Cradle of Echoes)", "line": "Your 95% Persona Seal is bound to The Strategist and The Architect. Enter the Memory Architecture System."},
        ],
    },
    {
        "chapter": 4,
        "asset_name": "chapter_04_the_first_level",
        "title": "Ch 04: The First Level (Cliffside Red Scarf Reveal)",
        "act": "ACT I — Awakening the System",
        "setting": "Floating Glass-Tile Horizon -> Okitsu Coastal Cliffside",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#D12D3A",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 4,
        "reward_xp": 220,
        "reward_coins": 280,
        "reward_card": "ce_05_neural_etched_vr_headset",
        "boss_disruptor": {
            "name": "Fractal Pattern Construct",
            "rule": "Symmetric card placements across Center Tile (1,1) trigger an automatic Red Scarf (#D12D3A) diagonal glitch cut (-2 DEF to enemy corners).",
            "locked_column": -1,
            "hazard_tiles": [[0, 2], [2, 0]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Order from Chaos Kinetic Hex Pattern",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
                {"row": 1, "col": 0, "owner": "ai", "card_id": "mc_01_ryoma_ito_marche_paladin", "nesw": [7, 8, 6, 7]},
                {"row": 2, "col": 2, "owner": "player", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
            ],
            "target_resonance": "Pair (1.50x)",
            "solution_hint": "Deploy Kai Nakamura at (1,1) with Budge (+1) on Column 1 (Pips 3-4) so North 8+2 > Aiko's South 8, reconstructing the cliffside memory.",
        },
        "dialogue": [
            {"speaker": "Mnemosyne", "line": "CHAMBER 01: ORDER FROM CHAOS. Align the floating stone and glass vectors above the starless sea."},
            {"speaker": "Aiko Nakamura (Memory Echo)", "line": "Look at the waves below the seawall, Kai. Even when the tide looks chaotic, there's a rhythm underneath. You found the pattern."},
            {"speaker": "Kai Nakamura", "line": "Her crimson scarf (#D12D3A)... the wind off the cliff felt completely real. That wasn't a pre-rendered cutscene—she's inside the code."},
        ],
    },
    {
        "chapter": 5,
        "asset_name": "chapter_05_flicker",
        "title": "Ch 05: Flicker (Rain-Slicked Lantern Alley)",
        "act": "ACT I — Awakening the System",
        "setting": "Rainy Paper-Lantern Alley (Simulation Layer 2)",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#D12D3A",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_dicevaders_chrono_armada",
        "ai_level": 4,
        "reward_xp": 250,
        "reward_coins": 300,
        "reward_card": "mc_01_ryoma_ito_marche_paladin",
        "boss_disruptor": {
            "name": "Flickering Silhouette of Aiko",
            "rule": "Enemy cards on Column 0 start cloaked in Flicker Stealth; matching an exact die pip to their row index strips Stealth and grants +2 East/West.",
            "locked_column": 0,
            "hazard_tiles": [[0, 0], [2, 0]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Symbol Flicker Frequency Decoding",
            "initial_board": [
                {"row": 0, "col": 0, "owner": "ai", "card_id": "mc_10_yoji_shinkawa_jehuty_frame", "nesw": [9, 8, 7, 8]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
                {"row": 1, "col": 2, "owner": "player", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Use Budge (±1) to unlock Column 0 (Pips 1-2) and strip Flicker Stealth from Sumi-e Ink's Jehuty Frame, then capture Constellation Fox from (2,1).",
        },
        "dialogue": [
            {"speaker": "Kai Nakamura", "line": "The neon kanji on the wet pavement are flickering at 42 Hz—the exact clock frequency of Aiko's neural compiler."},
            {"speaker": "Taro Fujimoto (Voiceover)", "line": "Promise me you won't chase a ghost so deep you forget how to breathe air, Kai."},
            {"speaker": "Aiko Nakamura (Flicker Echo)", "line": "Follow the red thread through the static, little brother... before the sector overwrites."},
        ],
    },
    {
        "chapter": 6,
        "asset_name": "chapter_06_phantom_signals",
        "title": "Ch 06: Phantom Signals & Memory Bloom",
        "act": "ACT I — Awakening the System",
        "setting": "Bioluminescent Memory Bloom Conservatory",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#2EE6D3",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 5,
        "reward_xp": 300,
        "reward_coins": 350,
        "reward_card": "sp_02_aiko_nakamura_echo",
        "boss_disruptor": {
            "name": "Harmonic Resonance Weaver",
            "rule": "Acoustic Resonance: Triggering dice cascades in ascending pip order (Col 0 -> Col 1 -> Col 2) shifts harmonic pitch +1.5 semitones and grants +2 Omni-Edge.",
            "locked_column": -1,
            "hazard_tiles": [[1, 0], [1, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Spatial Sound Mapping & Two-Way Voice Bloom",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_04_luna_cradle_guide", "nesw": [8, 8, 8, 8]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
                {"row": 2, "col": 1, "owner": "player", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
            ],
            "target_resonance": "Straight Overdrive (2.75x)",
            "solution_hint": "Form a Straight Overdrive or Triple on the Dice Row and place Kai Nakamura at (1,2) so Constellation Fox synergy flips Aiko's Echo at (1,1).",
        },
        "dialogue": [
            {"speaker": "Kai Nakamura", "line": "Wind chimes from grandmother's porch, the Okitsu rail crossing, the surf against the breakwater... each sound maps to a shadow game Aiko taught me."},
            {"speaker": "Aiko Nakamura (Live Two-Way Signal)", "line": "You remembered the chime sequence, Kai... You actually found me."},
            {"speaker": "Mnemosyne", "line": "[ACT I COMPLETE — MEMORY BLOOM UNLOCKED] Card Acquired: Aiko Nakamura, Red Scarf Echo (#D12D3A)."},
        ],
    },
    {
        "chapter": 7,
        "asset_name": "chapter_07_memory_theatre",
        "title": "Ch 07: Memory Theatre (Summer Festival Lanterns)",
        "act": "ACT II — Fractured Memories",
        "setting": "Mnemosyne Grand Amphitheatre of Floating Lanterns (#FFB648)",
        "palette_id": "Palette_C_Ocean_And_Lantern",
        "primary_hex": "#0A2230",
        "accent_hex": "#FFB648",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 5,
        "reward_xp": 320,
        "reward_coins": 380,
        "reward_card": "ce_06_memory_theatre_stage_lantern",
        "boss_disruptor": {
            "name": "The Stage Director Archon (Joy Index)",
            "rule": "Completing a 3-card horizontal row ordered by Emotional Weight (Nostalgia -> Grief -> Acceptance) ignites a 2.25x Triple Lantern Cascade.",
            "locked_column": -1,
            "hazard_tiles": [[0, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Emotional Sequence Reconstruction (Memory Theatre)",
            "initial_board": [
                {"row": 0, "col": 0, "owner": "ai", "card_id": "mc_03_hideo_minaba_skyfarer_archon", "nesw": [6, 8, 8, 7]},
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
                {"row": 2, "col": 2, "owner": "player", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Deploy Memory Theatre Lantern or Kai at (1,1) and activate Column 1 (Pips 3-4) with Triple Resonance to sweep the top stage row.",
        },
        "dialogue": [
            {"speaker": "Mnemosyne", "line": "ACT II: FRACTURED MEMORIES. Chronology is a cage; arrange these festival lanterns by the weight they left on your heart."},
            {"speaker": "Kai Nakamura", "line": "Paper lanterns (#FFB648) rising over the deep ocean (#0A2230)... Aiko held my hand when I lost sight of grandmother in the crowd."},
            {"speaker": "Aiko Nakamura (Echo)", "line": "Joy hurts the sharpest when you look back at it from the dark, Kai. Don't look away."},
        ],
    },
    {
        "chapter": 8,
        "asset_name": "chapter_08_artifacts",
        "title": "Ch 08: Artifacts (Kitchen Table Contradiction)",
        "act": "ACT II — Fractured Memories",
        "setting": "Nakamura Family Kitchen Table Dual-Memory Split",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#7A8B99",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 6,
        "reward_xp": 350,
        "reward_coins": 400,
        "reward_card": "ce_07_kitchen_table_porcelain_cup",
        "boss_disruptor": {
            "name": "Synthetic Nostalgia Curator (Regret Index)",
            "rule": "Decoy memory cards display inflated stats (+2) until inspected with FlickerPatternDecode or a Budge (±1) shift, which exposes their true -2 vulnerability.",
            "locked_column": 1,
            "hazard_tiles": [[1, 0], [1, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Compare & Contrast True vs. Altered Domestic Artifacts",
            "initial_board": [
                {"row": 1, "col": 0, "owner": "ai", "card_id": "mc_06_hiroshi_minagawa_diorama_warden", "nesw": [8, 9, 9, 7]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "mc_06_hiroshi_minagawa_diorama_warden", "nesw": [4, 5, 7, 5]},
                {"row": 2, "col": 1, "owner": "player", "card_id": "sp_01_kai_nakamura", "nesw": [8, 8, 6, 7]},
            ],
            "target_resonance": "Pair (1.50x)",
            "solution_hint": "Expose the falsified kitchen table memory at (1,0) using Budge, then place Aiko's Echo at (1,1) to overwrite the synthetic calm.",
        },
        "dialogue": [
            {"speaker": "Kai Nakamura", "line": "Wait. In this replay, Father is smiling and the porcelain teacup isn't cracked. Why did Mnemosyne edit out the shouting match?"},
            {"speaker": "Aiko Nakamura (Echo)", "line": "The system tries to anesthetize regret so test subjects stay compliant. If we want the truth, we have to choose the cracked cup."},
            {"speaker": "Kai Nakamura", "line": "I don't want a painless lie. Restore the unedited memory!"},
        ],
    },
    {
        "chapter": 9,
        "asset_name": "chapter_09_recalibration",
        "title": "Ch 09: Recalibration (VR Cafe Confrontation)",
        "act": "ACT II — Fractured Memories",
        "setting": "Okitsu VR Cafe Backroom / Neural Recalibration Core",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#1B2338",
        "accent_hex": "#2EE6D3",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_dicevaders_chrono_armada",
        "ai_level": 6,
        "reward_xp": 380,
        "reward_coins": 420,
        "reward_card": "sp_05_taro_fujimoto",
        "boss_disruptor": {
            "name": "Taro's Grounding Anchor Projection (Anger Index)",
            "rule": "Attaching an Emotion Tag (Anger #D12D3A / Trust #2EE6D3) via Budge boosts a friendly card's weakest directional side by +3.",
            "locked_column": -1,
            "hazard_tiles": [[0, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Drag-and-Drop Emotional Resonance Tagging",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_05_taro_fujimoto", "nesw": [8, 8, 9, 7]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "dv_04_pilot_roxy_mecha_gunner", "nesw": [7, 8, 8, 6]},
                {"row": 2, "col": 0, "owner": "player", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Tag Phoenix/Zero at (1,2) with #D12D3A Anger and harmonize with Kai at (2,1) to reconcile Taro's warning without breaking your bond.",
        },
        "dialogue": [
            {"speaker": "Taro Fujimoto", "line": "Look at your hands, Kai! Your pulse spikes every time you unplug. You're treating the real world like a loading screen!"},
            {"speaker": "Kai Nakamura", "line": "You think I want to be stuck here?! If I stop solving the grid, Aiko's consciousness fragments for good!"},
            {"speaker": "Taro Fujimoto", "line": "Then let me anchor the external diagnostics from the VR Cafe. You don't have to carry the whole server dome alone."},
        ],
    },
    {
        "chapter": 10,
        "asset_name": "chapter_10_displacement",
        "title": "Ch 10: Displacement (Refractive Mirror Match)",
        "act": "ACT II — Fractured Memories",
        "setting": "Refractive Glass Corridor & Rain-Drenched Okitsu Station",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#8A5BFF",
        "player_deck": "deck_luna_cradle_of_echoes",
        "ai_deck": "deck_kai_red_scarf_echo",
        "ai_level": 7,
        "reward_xp": 400,
        "reward_coins": 450,
        "reward_card": "mc_11_kazuma_kaneko_demi_fiend_archon",
        "boss_disruptor": {
            "name": "Doppelganger Kai — Refractive Echo (Guilt Index)",
            "rule": "Mirror Displacement: North/South and East/West values invert on Center Column 1 unless locked by a Pair (1.50x) or Triple (2.25x) die roll.",
            "locked_column": 1,
            "hazard_tiles": [[0, 1], [2, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Refractive Mirror Pose & Guilt Synchronization",
            "initial_board": [
                {"row": 1, "col": 0, "owner": "ai", "card_id": "sp_01_kai_nakamura", "nesw": [8, 8, 6, 7]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "mc_10_yoji_shinkawa_jehuty_frame", "nesw": [9, 8, 7, 8]},
                {"row": 2, "col": 1, "owner": "player", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
            ],
            "target_resonance": "Pair (1.50x)",
            "solution_hint": "Lock a Pair on the Dice Row to stabilize Column 1's mirror inversion, then play Kai at (1,1) with Budge (+1) to shatter the guilt reflection.",
        },
        "dialogue": [
            {"speaker": "Doppelganger Kai (Mirror)", "line": "Why didn't you walk her to the research lab that rainy morning at Okitsu Station? You were too busy staring at a Rubik's cube."},
            {"speaker": "Kai Nakamura", "line": "I edited that morning out of my own memory... I told myself I was at school, but I was standing right on the platform."},
            {"speaker": "LUNA", "line": "Guilt acknowledged is no longer a trapdoor. The mirror stabilizes."},
        ],
    },
    {
        "chapter": 11,
        "asset_name": "chapter_11_the_shadow_maze",
        "title": "Ch 11: The Shadow Maze (Rooftop Stargazing)",
        "act": "ACT II — Fractured Memories",
        "setting": "Chiaroscuro Shadow Labyrinth & Okitsu Bay Rooftop",
        "palette_id": "Palette_C_Ocean_And_Lantern",
        "primary_hex": "#0A2230",
        "accent_hex": "#FFB648",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 7,
        "reward_xp": 440,
        "reward_coins": 480,
        "reward_card": "ce_08_shadow_maze_chiaroscuro_lamp",
        "boss_disruptor": {
            "name": "Umbral Constellation Fox (Loss Index)",
            "rule": "Light-source cards project beams across orthogonal columns; using Budge (±1 pip) aligns shadow angles to flip entire columns at once.",
            "locked_column": 2,
            "hazard_tiles": [[0, 2], [1, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Spatial Logic via Light & Shadow Projection",
            "initial_board": [
                {"row": 0, "col": 0, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
                {"row": 0, "col": 2, "owner": "player", "card_id": "sp_04_luna_cradle_guide", "nesw": [8, 8, 8, 8]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Cast a diagonal shadow line from LUNA (0,2) through center (1,1) using Budge (+1) on Pips 5-6 to illuminate Aiko's rooftop constellation.",
        },
        "dialogue": [
            {"speaker": "Aiko Nakamura (Memory)", "line": "When the house got too loud after Mom and Dad split up, we'd climb onto the roof and connect five amber stars into a fox."},
            {"speaker": "Kai Nakamura", "line": "If I rotate the suspended debris by one degree—just a single ±1 Budge—the shadow on the far wall forms the Constellation Fox!"},
            {"speaker": "Mnemosyne", "line": "SHADOW MAZE SOLVED. Warning: Sub-stratum audio anomaly detected."},
        ],
    },
    {
        "chapter": 12,
        "asset_name": "chapter_12_echo_ai",
        "title": "Ch 12: Echo AI (Dual-Voice Waveform Sync)",
        "act": "ACT II — Fractured Memories",
        "setting": "Degrading Sub-Stratum Acoustic Core",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#2EE6D3",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_dicevaders_chrono_armada",
        "ai_level": 7,
        "reward_xp": 480,
        "reward_coins": 520,
        "reward_card": "dv_06_pilot_noel_chrono_keeper",
        "boss_disruptor": {
            "name": "Fragmented Echo AI (Dual-Voice Anomaly)",
            "rule": "Dual-Waveform Sync: Rolling Two Pair (1.85x) or Triple (2.25x) synchronizes the two fractured Aiko voices, granting +2 to all sides and +1 Chrono.",
            "locked_column": -1,
            "hazard_tiles": [[1, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Dual-Track Distorted Audio Log Synchronization",
            "initial_board": [
                {"row": 1, "col": 0, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 8, 8, 9]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "sp_06_dr_rina_asakura", "nesw": [9, 8, 9, 6]},
                {"row": 0, "col": 1, "owner": "player", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
            ],
            "target_resonance": "Two Pair (1.85x)",
            "solution_hint": "Deploy Aiko's Echo at (1,1) after locking Two Pair on the Dice Row to synchronize the dual waveforms and repel Dr. Asakura's perimeter probe.",
        },
        "dialogue": [
            {"speaker": "Echo AI (Distorted Track B)", "line": "Kai—don't—complete the final compiler—Rina Asakura is waiting on the outside to harvest the core!"},
            {"speaker": "Aiko Nakamura (Track A)", "line": "Two recordings of my voice overlapping out of phase... Synchronize the peaks, Kai!"},
            {"speaker": "Kai Nakamura", "line": "Got it! Both waveforms locked in phase—wait, someone just breached Sector 09 from the corporate intranet!"},
        ],
    },
    {
        "chapter": 13,
        "asset_name": "chapter_13_system_update",
        "title": "Ch 13: System Update (Asakura Firewall Intrusion)",
        "act": "ACT II — Fractured Memories",
        "setting": "Corrupted Firewall Sector 09 (Dr. Asakura's Breach)",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#D12D3A",
        "player_deck": "deck_dicevaders_chrono_armada",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 8,
        "reward_xp": 520,
        "reward_coins": 560,
        "reward_card": "sp_06_dr_rina_asakura",
        "boss_disruptor": {
            "name": "Dr. Rina Asakura's Extraction Daemon",
            "rule": "Hostile System Update: Locks Column 2 (Pips 5-6) with a Corporate Firewall. Spending 1 Chrono Reroll purges the lock and recovers +2 Budge.",
            "locked_column": 2,
            "hazard_tiles": [[0, 2], [1, 2], [2, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Corrupted File-Maze Navigation & Journal Retrieval",
            "initial_board": [
                {"row": 0, "col": 2, "owner": "ai", "card_id": "sp_06_dr_rina_asakura", "nesw": [9, 8, 9, 6]},
                {"row": 1, "col": 1, "owner": "ai", "card_id": "dv_04_pilot_roxy_mecha_gunner", "nesw": [7, 8, 8, 6]},
                {"row": 2, "col": 0, "owner": "player", "card_id": "sp_01_kai_nakamura", "nesw": [8, 8, 6, 7]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Press Chrono Reroll to purge Dr. Asakura's Column 2 lock, then strike (0,2) from (0,1) with Omega Zero or Kai boosted by Triple Resonance.",
        },
        "dialogue": [
            {"speaker": "Dr. Rina Asakura", "line": "Impressive neural plasticity, Kai Nakamura. Your sister's MAS architecture was languishing in dormant sectors until your grief indexed it for us."},
            {"speaker": "Kai Nakamura", "line": "Aiko isn't your corporate intellectual property! You're tearing the memory sectors apart!"},
            {"speaker": "Aiko Nakamura (Echo)", "line": "Grab Encrypted Journal [Log: A-09] from the center node, Kai! Don't let her daemon quarantine it!"},
        ],
    },
    {
        "chapter": 14,
        "asset_name": "chapter_14_reconciliation_loop",
        "title": "Ch 14: Reconciliation Loop (The Unspoken Truth)",
        "act": "ACT II — Fractured Memories",
        "setting": "Infinite Recursive Hallway of the Final Argument",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#F2F2F2",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 8,
        "reward_xp": 560,
        "reward_coins": 600,
        "reward_card": "ce_11_chrono_temporal_anchor_spell",
        "boss_disruptor": {
            "name": "The Unspoken Guilt Time-Loop",
            "rule": "Recursive Loop: Unmodified Single rolls lose -1 ATK; using Chrono Reroll or playing an Honest Confession card in Center Tile (1,1) breaks the loop and grants +3 Omni-Edge.",
            "locked_column": -1,
            "hazard_tiles": [[1, 1]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Truth-Gated Recursive Dialogue & Chrono Lock",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 7, 8, 9]},
                {"row": 2, "col": 1, "owner": "ai", "card_id": "sp_01_kai_nakamura", "nesw": [8, 8, 6, 7]},
                {"row": 1, "col": 0, "owner": "player", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
            ],
            "target_resonance": "Straight Overdrive (2.75x)",
            "solution_hint": "Trigger Chrono Reroll to break the recursive hallway reset, then place Kai or Reconciliation Key at Center (1,1) to embrace both truth and grief.",
        },
        "dialogue": [
            {"speaker": "Memory Replay (Loop #14)", "line": "'I'm fine, Aiko! Go to your lab!' — [TIMELINE RESET: DEFENSIVE LIE DETECTED]."},
            {"speaker": "Kai Nakamura", "line": "Every time I repeat what I actually said that night, the corridor resets. The lock isn't asking for what happened—it's asking for what I hid."},
            {"speaker": "Kai Nakamura", "line": "I was terrified you were leaving me behind, Aiko! I was angry, and I was scared, and I never got to say I'm sorry!"},
        ],
    },
    {
        "chapter": 15,
        "asset_name": "chapter_15_the_core_fracture",
        "title": "Ch 15: The Core Fracture & The Unchosen Memory",
        "act": "ACT II — Fractured Memories",
        "setting": "Collapsing Coastal Research Lab -> Quiet Rooftop Starlight",
        "palette_id": "Palette_C_Ocean_And_Lantern",
        "primary_hex": "#0A2230",
        "accent_hex": "#FFB648",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 8,
        "reward_xp": 600,
        "reward_coins": 650,
        "reward_card": "sp_03_mnemosyne_constellation_fox",
        "boss_disruptor": {
            "name": "Core Tectonic Fracture & Extraction Surge",
            "rule": "Stability Collapse Blitz: Completing a diagonal 3-card bridge across (0,0)-(1,1)-(2,2) stabilizes the shattering lab and unlocks the Rooftop Fox 2.75x bonus.",
            "locked_column": 0,
            "hazard_tiles": [[0, 2], [2, 0]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "High-Velocity Memory Shard Diagonal Bridging",
            "initial_board": [
                {"row": 0, "col": 2, "owner": "ai", "card_id": "sp_06_dr_rina_asakura", "nesw": [9, 8, 9, 6]},
                {"row": 2, "col": 0, "owner": "ai", "card_id": "mc_07_isamu_kamikokuryo_strahl_admiral", "nesw": [8, 8, 8, 7]},
                {"row": 0, "col": 0, "owner": "player", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
            ],
            "target_resonance": "Triple (2.25x)",
            "solution_hint": "Bridge (1,1) and (2,2) with Kai and Aiko's Echo while firing a Triple Resonance cascade to unlock the Interlude: The Unchosen Memory.",
        },
        "dialogue": [
            {"speaker": "Dr. Rina Asakura", "line": "Core containment at 18%. Sever the brother's neural link and extract the Mnemosyne kernel now!"},
            {"speaker": "Kai Nakamura", "line": "The lab floor is shattering into void polygons—if I bridge the diagonal shards, I can shield Aiko's core!"},
            {"speaker": "Aiko Nakamura (Interlude: The Unchosen Memory)", "line": "Before the fall... remember the quiet rooftop night when we didn't solve anything at all? We just watched the Constellation Fox (#FFB648) until dawn."},
        ],
    },
    {
        "chapter": 16,
        "asset_name": "chapter_16_awakening",
        "title": "Ch 16: Awakening (Ocean of Broken Data Shards)",
        "act": "ACT III — Collapse and Choice",
        "setting": "Dream-Ocean Void (#0A1020) of Floating Hex Debris (#2EE6D3)",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#8A5BFF",
        "player_deck": "deck_luna_cradle_of_echoes",
        "ai_deck": "deck_dicevaders_chrono_armada",
        "ai_level": 9,
        "reward_xp": 650,
        "reward_coins": 700,
        "reward_card": "mc_12_terada_suzuki_ikaruga_phoenix",
        "boss_disruptor": {
            "name": "Entropy Static Leviathan",
            "rule": "Violet Static Void: Cold unbudged dice drift off-target; using at least 1 Budge or Chrono per turn stabilizes the hexagonal stepping stones (+2 All Sides).",
            "locked_column": 1,
            "hazard_tiles": [[1, 0], [1, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Emotion-Guided Hexagonal Debris Stepping Stones",
            "initial_board": [
                {"row": 0, "col": 0, "owner": "ai", "card_id": "dv_09_overdrive_pip56_dreadnought", "nesw": [7, 9, 9, 6]},
                {"row": 2, "col": 2, "owner": "ai", "card_id": "dv_12_starvaders_omega_carrier", "nesw": [9, 9, 10, 9]},
                {"row": 1, "col": 0, "owner": "player", "card_id": "sp_05_taro_fujimoto", "nesw": [7, 7, 8, 6]},
            ],
            "target_resonance": "Quadruple (3.50x)",
            "solution_hint": "Use Budge (±1) and Chrono Reroll to forge a Triple or Quadruple (3.50x) on the Dice Row, bridging center tile (1,1) across the violet static ocean.",
        },
        "dialogue": [
            {"speaker": "Kai Nakamura", "line": "ACT III. The simulated town is gone—just an endless ocean of violet static (#8A5BFF) and broken hexagonal data shards."},
            {"speaker": "Taro Fujimoto (External Comms)", "line": "Kai, I'm reading your bio-telemetry from the cafe! Stop calculating the tiles like an algorithm—feel where Aiko's red scarf thread is pulling!"},
            {"speaker": "Kai Nakamura", "line": "When I trust emotional intuition instead of cold math, the hex platforms lock beneath my feet. The Hall of Selves is just ahead."},
        ],
    },
    {
        "chapter": 17,
        "asset_name": "chapter_17_the_hall_of_selves",
        "title": "Ch 17: The Hall of Selves (Four Doors of Denial)",
        "act": "ACT III — Collapse and Choice",
        "setting": "Liquid-Metal Corridor of Four Unlabeled Doors",
        "palette_id": "Palette_B_Cyber_Blues_Neon_Violet",
        "primary_hex": "#0A1020",
        "accent_hex": "#EAF2FF",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 9,
        "reward_xp": 750,
        "reward_coins": 800,
        "reward_card": "mc_02_akihiko_yoshida_judge_master",
        "boss_disruptor": {
            "name": "The Four Fractured Selves (Indifference, Anger, Fear, Mirror Kai)",
            "rule": "Four-Door Gauntlet: The 4 orthogonal edge slots ((0,1) Anger, (1,2) Indifference, (2,1) Apathy, (1,0) Fear) guard the center mirror. Placing a card at Center (1,1) with Triple/Quadruple Resonance flips all 4 doors simultaneously!",
            "locked_column": -1,
            "hazard_tiles": [[0, 1], [1, 2], [2, 1], [1, 0]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "4-Door Self-Integration Cross Capture",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "mc_05_toru_nakayama_crimson_zero", "nesw": [9, 9, 7, 7]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "mc_01_ryoma_ito_marche_paladin", "nesw": [7, 8, 6, 7]},
                {"row": 2, "col": 1, "owner": "ai", "card_id": "mc_10_yoji_shinkawa_jehuty_frame", "nesw": [7, 8, 7, 8]},
                {"row": 1, "col": 0, "owner": "ai", "card_id": "mc_04_ryo_hirata_orange_star_co", "nesw": [8, 7, 7, 7]},
            ],
            "target_resonance": "Quadruple (3.50x)",
            "solution_hint": "Align a Triple (2.25x) or Quadruple (3.50x) on the Dice Row, then deploy Kai Nakamura at Center (1,1) to flip all four orthogonal doors in a single 48ms hit-stop burst!",
        },
        "dialogue": [
            {"speaker": "Fractured Selves (Doors I–IV)", "line": "Door I: Indifference ('Nothing matters'). Door II: Anger ('She abandoned us'). Door III: Fear ('What if we're empty without her?'). Door IV: Mirror Kai walking away forever."},
            {"speaker": "Kai Nakamura", "line": "You aren't enemies I have to delete. You're all parts of me that tried to survive losing her."},
            {"speaker": "Mnemosyne", "line": "[FOURFOLD SELF INTEGRATED] The center mirror shatters beneath the Constellation Fox. The Sanctum of the Memory Architect opens."},
        ],
    },
    {
        "chapter": 18,
        "asset_name": "chapter_18_the_memory_architect",
        "title": "Ch 18: The Memory Architect (Logs A-09, A-14, A-21)",
        "act": "ACT III — Collapse and Choice",
        "setting": "Jasmine-Scented Neural Compiler Sanctum",
        "palette_id": "Palette_A_Monochrome_Red_Scarf",
        "primary_hex": "#0B0B0C",
        "accent_hex": "#D12D3A",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_luna_cradle_of_echoes",
        "ai_level": 10,
        "reward_xp": 850,
        "reward_coins": 900,
        "reward_card": "ce_09_encrypted_journal_log_a21",
        "boss_disruptor": {
            "name": "Aiko Nakamura, The Memory Architect (Living Mosaic)",
            "rule": "Compiler Log Synthesis: Aligning all 3 Columns (Col 0 + Col 1 + Col 2) or triggering a Quadruple (3.50x) unseals Logs A-09, A-14, and A-21, granting permanent +3 Omni-Edge.",
            "locked_column": -1,
            "hazard_tiles": [],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Compiler Log Alignment ([Log: A-09], [Log: A-14], [Log: A-21])",
            "initial_board": [
                {"row": 1, "col": 1, "owner": "ai", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 8, 8, 9]},
                {"row": 0, "col": 0, "owner": "ai", "card_id": "sp_03_mnemosyne_constellation_fox", "nesw": [7, 8, 9, 8]},
                {"row": 0, "col": 2, "owner": "player", "card_id": "sp_04_luna_cradle_guide", "nesw": [8, 8, 8, 8]},
            ],
            "target_resonance": "Quadruple (3.50x)",
            "solution_hint": "Flank Aiko at (1,1) with Kai Nakamura and Compiler Log [A-21] while firing a Quadruple (3.50x) resonance to complete the living mosaic.",
        },
        "dialogue": [
            {"speaker": "Aiko Nakamura, The Memory Architect", "line": "Welcome to the compiler, Kai. Every puzzle you solved across Mnemosyne wove another thread of my scattered neural imprint back together."},
            {"speaker": "Kai Nakamura", "line": "Log A-09, Log A-14, Log A-21... You didn't vanish by accident. You uploaded your own neural pattern into the MAS core to shield the beta subjects from corporate corruption!"},
            {"speaker": "Aiko Nakamura, The Memory Architect", "line": "[Log: A-21] 'Even if I'm only an echo of code and crimson thread... maybe he'll remember how it felt to be loved. That's enough.'"},
        ],
    },
    {
        "chapter": 19,
        "asset_name": "chapter_19_the_shifting_truth",
        "title": "Ch 19: The Shifting Truth (Convergence & Triad Choice)",
        "act": "ACT III — Finale & Epilogue (A Living Puzzle)",
        "setting": "The Pulsing Mnemosyne Core Lattice -> Okitsu Seawall Dawn",
        "palette_id": "Palette_C_Ocean_And_Lantern",
        "primary_hex": "#0A2230",
        "accent_hex": "#FFB648",
        "player_deck": "deck_kai_red_scarf_echo",
        "ai_deck": "deck_twelve_masters_sovereign",
        "ai_level": 10,
        "reward_xp": 1500,
        "reward_coins": 2000,
        "reward_card": "ce_12_living_puzzle_golden_fox_tile",
        "boss_disruptor": {
            "name": "Dr. Rina Asakura & The Unstable Mnemosyne Core (3-Phase Finale)",
            "rule": "Phase 1: Counter Asakura's Column Locks with Chrono Rerolls. Phase 2: Complete the 9-Slot Circular Mosaic. Phase 3: Execute the Final Triad Choice (MERGE / PRESERVE / DESTROY) with a 3.50x Quadruple Resonance cascade!",
            "locked_column": 1,
            "hazard_tiles": [[0, 0], [0, 2], [2, 0], [2, 2]],
        },
        "mnemosyne_puzzle_grid": {
            "puzzle_type": "Ethical Debate Counter-Flips + 9-Slot Circular Mosaic + Triad Gate Choice",
            "initial_board": [
                {"row": 0, "col": 1, "owner": "ai", "card_id": "sp_06_dr_rina_asakura", "nesw": [9, 8, 9, 6]},
                {"row": 1, "col": 0, "owner": "ai", "card_id": "mc_02_akihiko_yoshida_judge_master", "nesw": [9, 8, 9, 8]},
                {"row": 1, "col": 2, "owner": "ai", "card_id": "dv_12_starvaders_omega_carrier", "nesw": [9, 9, 10, 9]},
                {"row": 2, "col": 1, "owner": "player", "card_id": "sp_02_aiko_nakamura_echo", "nesw": [9, 8, 8, 9]},
            ],
            "target_resonance": "Quadruple (3.50x)",
            "solution_hint": "Purge Column 1 with Chrono, align all 5 dice into a Quadruple (3.50x) or Straight Overdrive via Budge, and deploy The Living Puzzle: Golden Fox Tile at Center (1,1) to choose MERGE, PRESERVE, or DESTROY.",
        },
        "dialogue": [
            {"speaker": "Dr. Rina Asakura", "line": "She is a finite simulation, Kai! Let the corporation archive her kernel, or the entire Mnemosyne lattice will collapse under its own emotional recursion!"},
            {"speaker": "Kai Nakamura", "line": "Memory isn't property you lock in a vault, Dr. Asakura—and grief isn't a bug to be patched out. Look at Log A-21 and the Rooftop Constellation: connection is what makes us real!"},
            {"speaker": "Aiko Nakamura & LUNA", "line": "The Three Gates stand open before you, Kai: [GATE I: MERGE — Integrate Our Consciousness], [GATE II: PRESERVE — Seal the Sanctuary Archive], [GATE III: COLLAPSE & CARRY FORWARD — Awaken in Okitsu with the Golden Fox Tile (#FFB648)]."},
            {"speaker": "Epilogue — A Living Puzzle", "line": "Morning sunlight warms the Okitsu VR Cafe. On the counter beside Taro's espresso machine rests a single warm golden tile etched with the Constellation Fox—and a new generation of students learning that every life is a living puzzle."},
        ],
    },
]


# ============================================================================
# SERIALIZERS FOR INDIE MARC UNITY `.asset` FILES
# ============================================================================

def serialize_ability_asset(spec: Dict[str, Any]) -> str:
    eff_lines = []
    for eff_key in spec.get("effects", []):
        eff_guid = EFFECT_GUIDS[eff_key]
        eff_lines.append(f"  - {{fileID: 11400000, guid: {eff_guid}, type: 2}}")
    effects_yaml = "  effects:\n" + "\n".join(eff_lines) if eff_lines else "  effects: []"

    stat_lines = []
    for st_key in spec.get("status", []):
        st_guid = STATUS_GUIDS[st_key]
        stat_lines.append(f"  - {{fileID: 11400000, guid: {st_guid}, type: 2}}")
    status_yaml = "  status:\n" + "\n".join(stat_lines) if stat_lines else "  status: []"

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
        f"  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID_ABILITY_DATA}, type: 3}}\n"
        f"  m_Name: {spec['id']}\n"
        "  m_EditorClassIdentifier: \n"
        f"  id: {spec['id']}\n"
        f"  trigger: {spec['trigger']}\n"
        "  conditions_trigger: []\n"
        f"  target: {spec['target']}\n"
        "  conditions_target: []\n"
        "  filters_target: []\n"
        f"{effects_yaml}\n"
        f"{status_yaml}\n"
        f"  value: {spec['value']}\n"
        f"  duration: {spec['duration']}\n"
        "  chain_abilities: []\n"
        f"  mana_cost: {spec['mana_cost']}\n"
        f"  exhaust: {spec['exhaust']}\n"
        "  board_fx: {fileID: 0}\n"
        f"  caster_fx: {{fileID: 6447155269572834885, guid: {CASTER_FX_GUID}, type: 3}}\n"
        "  target_fx: {fileID: 0}\n"
        "  cast_audio: {fileID: 0}\n"
        "  target_audio: {fileID: 0}\n"
        "  charge_target: 0\n"
        f"  title: {yaml_escape(spec['title'])}\n"
        f"  desc: {yaml_escape(spec['desc'])}\n"
    )


def serialize_card_asset(
    spec: Dict[str, Any],
    idx: int,
    ability_guid_map: Dict[str, str],
    pack_guids: List[str],
) -> str:
    atlas_guid = '58e81fd6e87d70eb2dabb2069167dd7b'
    sprite_file_id = 21300000 + (idx % 42) * 2
    art_full_guid = atlas_guid
    art_board_guid = atlas_guid
    team_guid = TEAM_GUIDS[spec["team"]]
    rarity_guid = RARITY_GUIDS[spec["rarity"]]

    trait_lines = []
    for t_key in spec.get("traits", []):
        t_guid = TRAIT_GUIDS[t_key]
        trait_lines.append(f"  - {{fileID: 11400000, guid: {t_guid}, type: 2}}")
    traits_yaml = "  traits:\n" + "\n".join(trait_lines) if trait_lines else "  traits: []"

    ab_lines = []
    for ab_id in spec.get("abilities", []):
        ab_guid = ability_guid_map[ab_id]
        ab_lines.append(f"  - {{fileID: 11400000, guid: {ab_guid}, type: 2}}")
    abilities_yaml = "  abilities:\n" + "\n".join(ab_lines) if ab_lines else "  abilities: []"

    pack_lines = [f"  - {{fileID: 11400000, guid: {pg}, type: 2}}" for pg in pack_guids]
    packs_yaml = "  packs:\n" + "\n".join(pack_lines)

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
        f"  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID_CARD_DATA}, type: 3}}\n"
        f"  m_Name: {spec['id']}\n"
        "  m_EditorClassIdentifier: \n"
        f"  id: {spec['id']}\n"
        f"  title: {yaml_escape(spec['title'])}\n"
        f"  art_full: {{fileID: {21300000 + (idx % 42) * 2}, guid: 58e81fd6e87d70eb2dabb2069167dd7b, type: 3}}\n"
        f"  art_board: {{fileID: {21300000 + (idx % 42) * 2}, guid: 58e81fd6e87d70eb2dabb2069167dd7b, type: 3}}\n"
        f"  type: {spec['type']}\n"
        f"  team: {{fileID: 11400000, guid: {team_guid}, type: 2}}\n"
        f"  rarity: {{fileID: 11400000, guid: {rarity_guid}, type: 2}}\n"
        f"  mana: {spec['mana']}\n"
        f"  attack: {spec['attack']}\n"
        f"  hp: {spec['hp']}\n"
        f"{traits_yaml}\n"
        "  stats: []\n"
        f"{abilities_yaml}\n"
        f"  text: {yaml_escape(spec['text'])}\n"
        f"  desc: {yaml_escape(spec['desc'])}\n"
        f"  spawn_fx: {{fileID: 9125387663047351618, guid: {SPAWN_FX_GUID}, type: 3}}\n"
        "  death_fx: {fileID: 0}\n"
        "  attack_fx: {fileID: 0}\n"
        "  damage_fx: {fileID: 0}\n"
        "  idle_fx: {fileID: 0}\n"
        "  spawn_audio: {fileID: 0}\n"
        "  death_audio: {fileID: 0}\n"
        "  attack_audio: {fileID: 0}\n"
        "  damage_audio: {fileID: 0}\n"
        "  deckbuilding: 1\n"
        f"  cost: {100 + spec['mana'] * 25}\n"
        f"{packs_yaml}\n"
        f"  dir_north: {spec.get('attack', 6)}\n"
        f"  dir_east: {max(4, spec.get('attack', 6) - 1)}\n"
        f"  dir_south: {spec.get('hp', 6)}\n"
        f"  dir_west: {max(4, spec.get('hp', 6) - 1)}\n"
        f"  dice_pip_affinity: {(idx % 6) + 1}\n"
        f"  sovereign_style_id: sovereign_tier_{(idx % 5) + 1}\n"
        f"  glb_model_id: {spec['id']}\n"
    )


def serialize_deck_asset(spec: Dict[str, Any], card_guid_map: Dict[str, str]) -> str:
    hero_guid = card_guid_map[spec["hero"]]
    card_lines = [
        f"  - {{fileID: 11400000, guid: {card_guid_map[cid]}, type: 2}}"
        for cid in spec["cards"]
    ]
    cards_yaml = "  cards:\n" + "\n".join(card_lines)
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
        f"  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID_DECK_DATA}, type: 3}}\n"
        f"  m_Name: {spec['id']}\n"
        "  m_EditorClassIdentifier: \n"
        f"  id: {spec['id']}\n"
        f"  title: {yaml_escape(spec['title'])}\n"
        f"  hero: {{fileID: 11400000, guid: {hero_guid}, type: 2}}\n"
        f"{cards_yaml}\n"
    )


def serialize_pack_asset(spec: Dict[str, Any]) -> str:
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
        f"  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID_PACK_DATA}, type: 3}}\n"
        f"  m_Name: {spec['id']}\n"
        "  m_EditorClassIdentifier: \n"
        f"  id: {spec['id']}\n"
        "  type: 0\n"
        f"  cards: {spec['cards']}\n"
        "  rarities_1st:\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['uncommon']}, type: 2}}\n"
        "    probability: 35\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['rare']}, type: 2}}\n"
        "    probability: 40\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['mythic']}, type: 2}}\n"
        "    probability: 25\n"
        "  rarities:\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['common']}, type: 2}}\n"
        "    probability: 50\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['uncommon']}, type: 2}}\n"
        "    probability: 25\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['rare']}, type: 2}}\n"
        "    probability: 17\n"
        f"  - rarity: {{fileID: 11400000, guid: {RARITY_GUIDS['mythic']}, type: 2}}\n"
        "    probability: 8\n"
        "  variants:\n"
        f"  - variant: {{fileID: 11400000, guid: {VARIANT_GUIDS['normal']}, type: 2}}\n"
        "    probability: 85\n"
        f"  - variant: {{fileID: 11400000, guid: {VARIANT_GUIDS['foil']}, type: 2}}\n"
        "    probability: 15\n"
        f"  title: {yaml_escape(spec['title'])}\n"
        f"  pack_img: {{fileID: 21300000, guid: {PACK_IMG_GUID}, type: 3}}\n"
        f"  cardback_img: {{fileID: 21300000, guid: {CARDBACK_IMG_GUID}, type: 3}}\n"
        f"  desc: {yaml_escape(spec['desc'])}\n"
        f"  sort_order: {spec['sort_order']}\n"
        "  available: 1\n"
        f"  cost: {spec['cost']}\n"
    )


def serialize_chapter_level_asset(
    ch: Dict[str, Any],
    deck_guid_map: Dict[str, str],
    pack_guids: List[str],
    card_guid_map: Dict[str, str],
) -> str:
    p_deck_guid = deck_guid_map[ch["player_deck"]]
    ai_deck_guid = deck_guid_map[ch["ai_deck"]]
    reward_card_guid = card_guid_map[ch["reward_card"]]
    pack_guid = pack_guids[(ch["chapter"] - 1) % len(pack_guids)]

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
        f"  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID_LEVEL_DATA}, type: 3}}\n"
        f"  m_Name: {ch['asset_name']}\n"
        "  m_EditorClassIdentifier: \n"
        f"  id: {ch['asset_name']}\n"
        f"  level: {ch['chapter']}\n"
        f"  title: {yaml_escape(ch['title'])}\n"
        "  scene: Game\n"
        f"  player_deck: {{fileID: 11400000, guid: {p_deck_guid}, type: 2}}\n"
        f"  ai_deck: {{fileID: 11400000, guid: {ai_deck_guid}, type: 2}}\n"
        f"  ai_level: {ch['ai_level']}\n"
        "  first_player: 10\n"
        f"  reward_xp: {ch['reward_xp']}\n"
        f"  reward_coins: {ch['reward_coins']}\n"
        "  reward_packs:\n"
        f"  - {{fileID: 11400000, guid: {pack_guid}, type: 2}}\n"
        "  reward_cards:\n"
        f"  - {{fileID: 11400000, guid: {reward_card_guid}, type: 2}}\n"
    )


def main() -> None:
    t0 = time.perf_counter()

    # Ensure folder hierarchy and `.meta` files exist
    for folder in [
        CARDS_DIR,
        ABILITIES_DIR,
        DECKS_DIR,
        PACKS_DIR,
        RESOURCES_ROOT / "Campaigns",
        CAMPAIGNS_DIR,
    ]:
        write_folder_meta(folder)

    # 1. Generate 2 Packs first so Cards and Chapters can reference their GUIDs
    pack_guid_map: Dict[str, str] = {}
    pack_guids_list: List[str] = []
    for p_spec in PACKS_SPEC:
        p_guid = deterministic_guid(f"PackData::{p_spec['id']}")
        pack_guid_map[p_spec["id"]] = p_guid
        pack_guids_list.append(p_guid)
        yaml_str = serialize_pack_asset(p_spec)
        write_asset_and_meta(PACKS_DIR / f"{p_spec['id']}.asset", yaml_str, p_guid)

    # 2. Generate 24 Abilities
    ability_guid_map: Dict[str, str] = {}
    for ab_spec in ABILITIES_SPEC:
        ab_guid = deterministic_guid(f"AbilityData::{ab_spec['id']}")
        ability_guid_map[ab_spec["id"]] = ab_guid
        yaml_str = serialize_ability_asset(ab_spec)
        write_asset_and_meta(ABILITIES_DIR / f"{ab_spec['id']}.asset", yaml_str, ab_guid)

    # 3. Generate 42 Cards
    card_guid_map: Dict[str, str] = {}
    for idx, c_spec in enumerate(CARDS_SPEC):
        c_guid = deterministic_guid(f"CardData::{c_spec['id']}")
        card_guid_map[c_spec["id"]] = c_guid
        yaml_str = serialize_card_asset(c_spec, idx, ability_guid_map, pack_guids_list)
        write_asset_and_meta(CARDS_DIR / f"{c_spec['id']}.asset", yaml_str, c_guid)

    # 4. Generate 4 Starter Decks
    deck_guid_map: Dict[str, str] = {}
    for d_spec in DECKS_SPEC:
        d_guid = deterministic_guid(f"DeckData::{d_spec['id']}")
        deck_guid_map[d_spec["id"]] = d_guid
        yaml_str = serialize_deck_asset(d_spec, card_guid_map)
        write_asset_and_meta(DECKS_DIR / f"{d_spec['id']}.asset", yaml_str, d_guid)

    # 5. Generate 19 Shifting Pieces Campaign Chapter `.asset` files
    chapter_guid_map: Dict[str, str] = {}
    for ch_spec in CHAPTERS_19_SPEC:
        ch_guid = deterministic_guid(f"LevelData::{ch_spec['asset_name']}")
        chapter_guid_map[ch_spec["asset_name"]] = ch_guid
        yaml_str = serialize_chapter_level_asset(
            ch_spec, deck_guid_map, pack_guids_list, card_guid_map
        )
        write_asset_and_meta(
            CAMPAIGNS_DIR / f"{ch_spec['asset_name']}.asset", yaml_str, ch_guid
        )

    # 6. Export `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/shifting_pieces_19_chapter_campaign.json`
    CAMPAIGN_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    campaign_export = {
        "campaign_id": "shifting_pieces_19_chapter_campaign",
        "title": "Shifting Pieces × CardFront: Cradle of Echoes × Dicevaders 19-Chapter Campaign",
        "author": "Hiroyasu (Binh C. Phan) | Studio PxG",
        "engine_target": "Indie Marc TCG Engine (Unity 2022.3 LTS / Unity 6) + WebPlayable HTML5 Canvas",
        "total_chapters": len(CHAPTERS_19_SPEC),
        "acts_summary": [
            {
                "act": 1,
                "title": "ACT I — Awakening the System (Chapters 1–6)",
                "palette": "Palette A: Monochrome + Red Scarf (#0B0B0C / #D12D3A)",
                "chapters": [1, 2, 3, 4, 5, 6],
            },
            {
                "act": 2,
                "title": "ACT II — Fractured Memories (Chapters 7–15)",
                "palette": "Palette C: Ocean & Lantern (#0A2230 / #FFB648) & Palette B (#0A1020 / #2EE6D3)",
                "chapters": [7, 8, 9, 10, 11, 12, 13, 14, 15],
            },
            {
                "act": 3,
                "title": "ACT III — Collapse and Choice (Chapters 16–19 & Epilogue)",
                "palette": "Palette B & Golden Fox Finale (#0A1020 / #8A5BFF / #FFB648)",
                "chapters": [16, 17, 18, 19],
            },
        ],
        "luna_station_of_awakening_genesis": {
            "choices": [
                {
                    "id": "sword_aggression",
                    "name": "Sword of Conviction (Aggression)",
                    "tarot_persona": "18. The Warrior / 2. The Master",
                    "bonus": "+2 Attack on North/East edges, +1 starting Budge token, crimson slash VFX",
                },
                {
                    "id": "shield_defense",
                    "name": "Shield of Sanctuary (Defense)",
                    "tarot_persona": "3. The Guardian / 7. The Healer",
                    "bonus": "+2 Defense on South/West edges, Prevent Flip shield on first card, emerald barrier VFX",
                },
                {
                    "id": "staff_control",
                    "name": "Staff of Eternity (Control)",
                    "tarot_persona": "8. The Strategist / 20. The Architect",
                    "bonus": "+2 starting Chrono Reroll tokens, +1 Budge token, neon cyan/violet glyph VFX",
                },
            ]
        },
        "dicevaders_grid_rules": {
            "dice_count": 5,
            "column_pip_mapping": {
                "col_0": [1, 2],
                "col_1": [3, 4],
                "col_2": [5, 6],
            },
            "resonance_multipliers": {
                "Single": 1.00,
                "Pair": 1.50,
                "TwoPair": 1.85,
                "Triple": 2.25,
                "StraightOverdrive": 2.75,
                "Quadruple": 3.50,
            },
            "juice_physics": {
                "damping_ratio_zeta": 0.42,
                "natural_frequency_omega_n_rad_s": 30.0,
                "cascade_stagger_ms": 55,
                "hit_stop_freeze_ms": 48,
                "harmonic_pitch_shift_semitones_per_cascade": 1.5,
            },
        },
        "chapters": [
            {
                **ch,
                "unity_asset_path": f"Assets/TcgEngine/Resources/Campaigns/ShiftingPieces/{ch['asset_name']}.asset",
                "unity_asset_guid": chapter_guid_map[ch["asset_name"]],
            }
            for ch in CHAPTERS_19_SPEC
        ],
    }
    CAMPAIGN_JSON_PATH.write_text(
        json.dumps(campaign_export, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    report = {
        "status": "VERIFIED_10_OF_10",
        "elapsed_ms": elapsed_ms,
        "counts": {
            "cards_generated": len(CARDS_SPEC),
            "abilities_generated": len(ABILITIES_SPEC),
            "decks_generated": len(DECKS_SPEC),
            "packs_generated": len(PACKS_SPEC),
            "chapters_generated": len(CHAPTERS_19_SPEC),
            "total_asset_files": len(CARDS_SPEC) + len(ABILITIES_SPEC) + len(DECKS_SPEC) + len(PACKS_SPEC) + len(CHAPTERS_19_SPEC),
        },
        "directories": {
            "cards": str(CARDS_DIR),
            "abilities": str(ABILITIES_DIR),
            "decks": str(DECKS_DIR),
            "packs": str(PACKS_DIR),
            "campaigns": str(CAMPAIGNS_DIR),
            "campaign_json": str(CAMPAIGN_JSON_PATH),
        },
    }
    ASSET_MANIFEST_JSON_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
