#!/usr/bin/env python3
"""
Synapse Ivalice Overworld Chronicle, CF-RPL1 Replay Ladder, Daily Lethal Puzzles & 10-Lang i18n Verifier
========================================================================================================
Generates and verifies:
  1. 15-Stage Ivalice Overworld Chronicle Node Graph across 3 Acts:
       - Act I: Sky-Stone Border (Stages 1-5)
       - Act II: Clockwork Sanctum (Stages 6-10)
       - Act III: Cradle of Echoes (Stages 11-15)
     with coordinates (x, y), branching DAG edges, Boss Commander IDs, Judge Laws, and reward relics.
  2. Deterministic `CF-RPL1:` Replay Serializer & Deserializer with FNV-1a 64-bit checksums.
  3. 10 Grandmaster Ghost Decks Ladder (`ghost_ladder_count: 10`) with verified 12-star cap & replays.
  4. 7 Daily Seeded Tactical Puzzles (`daily_puzzles_count: 7`) with verified solve-in-1-turn lethal captures.
  5. PUCT AlphaZero MCTS Evaluator (`SynapseAlphaZeroMCTSEvaluator`) for 3x3 board + hand + column dice.
  6. 10-Language AAA Localization String Table & 4 Colorblind Palettes verification.
  7. Writes `Logs/ivalice_chronicle_and_replay_manifest.json` (`status: "VERIFIED"`).
"""

from __future__ import annotations

import base64
import copy
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
I18N_JSON_PATH = PROJECT_ROOT / "Assets" / "Resources" / "Localization" / "i18n_strings_10lang.json"
LOGS_DIR = PROJECT_ROOT / "Logs"
MANIFEST_PATH = LOGS_DIR / "ivalice_chronicle_and_replay_manifest.json"


# ============================================================================
# 0. FNV-1a 64-BIT DETERMINISTIC HASHING & BASE64URL ENVELOPE CODEC
# ============================================================================

def compute_fnv1a_64_hex(payload_bytes: bytes) -> str:
    """Compute deterministic 64-bit FNV-1a checksum formatted as 0x + 16 hex chars."""
    h = 0xCBF29CE484222325
    prime = 0x100000001B3
    mask64 = 0xFFFFFFFFFFFFFFFF
    for b in payload_bytes:
        h ^= b
        h = (h * prime) & mask64
    return f"0x{h:016x}"


def compute_dict_fnv1a_64(data: Dict[str, Any], exclude_keys: Tuple[str, ...] = ("fnv1a_64_checksum",)) -> str:
    """Compute FNV-1a 64-bit checksum over canonical sorted-key JSON serialization."""
    filtered = {k: v for k, v in data.items() if k not in exclude_keys}
    canonical = json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return compute_fnv1a_64_hex(canonical.encode("utf-8"))


# ============================================================================
# 1. CARD CATALOG & 3x3 DIRECTIONAL GRID + SAME/PLUS/COMBO TACTICAL SIMULATOR
# ============================================================================

CARD_CATALOG: Dict[str, Dict[str, Any]] = {
    "h_archangel": {"id": "h_archangel", "name": "Solar Archangel", "faction": "Solaris", "nesw": [8, 7, 6, 7], "star_cost": 2},
    "h_phoenix": {"id": "h_phoenix", "name": "Phoenix Valkyrie", "faction": "Valkyria", "nesw": [9, 8, 5, 6], "star_cost": 2},
    "h_oracle": {"id": "h_oracle", "name": "Lunar Oracle", "faction": "Aether", "nesw": [7, 7, 8, 7], "star_cost": 2},
    "h_chronos": {"id": "h_chronos", "name": "Chronos Weaver", "faction": "Chronos", "nesw": [6, 8, 7, 7], "star_cost": 2},
    "h_seraph": {"id": "h_seraph", "name": "Astral Seraph", "faction": "Abyss", "nesw": [8, 6, 7, 8], "star_cost": 2},
    "h_kai": {"id": "h_kai", "name": "Kai Crimson Visor", "faction": "Aether", "nesw": [7, 8, 6, 7], "star_cost": 2},
    "h_valkyrie": {"id": "h_valkyrie", "name": "Sky-Wing Striker", "faction": "Valkyria", "nesw": [8, 8, 5, 6], "star_cost": 2},
    "h_arbiter": {"id": "h_arbiter", "name": "Sun Arbiter", "faction": "Solaris", "nesw": [7, 7, 8, 8], "star_cost": 3},
    "plugin_01_tcg_creative_designer": {"id": "plugin_01_tcg_creative_designer", "name": "Grand Arcanist of CardCraft", "faction": "Aether", "nesw": [8, 7, 6, 7], "star_cost": 2},
    "plugin_02_parallel_swarm_orchestrator": {"id": "plugin_02_parallel_swarm_orchestrator", "name": "Chronos Swarm Commander", "faction": "Chronos", "nesw": [7, 8, 6, 7], "star_cost": 2},
    "plugin_03_jev_system_one": {"id": "plugin_03_jev_system_one", "name": "Hallowed Arbiter of System One", "faction": "Solaris", "nesw": [8, 6, 8, 6], "star_cost": 2},
    "plugin_04_mlx_apple_silicon": {"id": "plugin_04_mlx_apple_silicon", "name": "A18 Pro Metal Forge Sovereign", "faction": "Valkyria", "nesw": [7, 7, 7, 7], "star_cost": 2},
    "e_eclipse": {"id": "e_eclipse", "name": "Eclipse Void Blade", "faction": "Abyss", "nesw": [6, 6, 5, 6], "star_cost": 1},
    "e_archon": {"id": "e_archon", "name": "Prism Core Archon", "faction": "Solaris", "nesw": [7, 6, 6, 5], "star_cost": 1},
    "e_inferno": {"id": "e_inferno", "name": "Inferno Seraph", "faction": "Valkyria", "nesw": [7, 7, 5, 6], "star_cost": 1},
    "e_reaper": {"id": "e_reaper", "name": "Sigil Wraith", "faction": "Abyss", "nesw": [6, 7, 7, 5], "star_cost": 1},
    "e_titan": {"id": "e_titan", "name": "Bastion Dreadnought", "faction": "Chronos", "nesw": [7, 5, 7, 6], "star_cost": 1},
    "e_colossus": {"id": "e_colossus", "name": "Emerald Colossus", "faction": "Aether", "nesw": [6, 8, 5, 6], "star_cost": 1},
    "e_cryo": {"id": "e_cryo", "name": "Cryo Interceptor", "faction": "Aether", "nesw": [5, 7, 6, 7], "star_cost": 1},
    "e_shinobi": {"id": "e_shinobi", "name": "Cyber Shinobi", "faction": "Chronos", "nesw": [7, 6, 6, 5], "star_cost": 1},
}

ORTHO_DIRS = (
    {"dr": -1, "dc": 0, "my_edge": 0, "their_edge": 2, "dir_name": "N"},
    {"dr": 0, "dc": 1, "my_edge": 1, "their_edge": 3, "dir_name": "E"},
    {"dr": 1, "dc": 0, "my_edge": 2, "their_edge": 0, "dir_name": "S"},
    {"dr": 0, "dc": -1, "my_edge": 3, "their_edge": 1, "dir_name": "W"},
)


def evaluate_board_captures(
    grid: List[List[Dict[str, Any]]],
    r: int,
    c: int,
    nesw: List[int],
    owner: str,
    okitsu_tie_surge: bool = False,
) -> List[Dict[str, Any]]:
    """
    Evaluate HIGH_PIP, SAME, PLUS, and COMBO_CASCADE captures when `owner` places or slides
    a card with `nesw` into `(r, c)`.
    """
    captured: List[Dict[str, Any]] = []
    seen_coords = set()

    # 1. Standard High-Pip (or Okitsu Tie-Surge) directional captures
    occupied_neighbors = []
    for d in ORTHO_DIRS:
        nr, nc = r + d["dr"], c + d["dc"]
        if 0 <= nr < 3 and 0 <= nc < 3:
            nb = grid[nr][nc]
            if nb and nb.get("cardId") and isinstance(nb.get("nesw"), list):
                my_val = int(nesw[d["my_edge"]])
                their_val = int(nb["nesw"][d["their_edge"]])
                occupied_neighbors.append({
                    "nr": nr,
                    "nc": nc,
                    "owner": nb.get("owner"),
                    "cardId": nb.get("cardId"),
                    "nesw": list(nb["nesw"]),
                    "my_val": my_val,
                    "their_val": their_val,
                    "edge_sum": my_val + their_val,
                    "equal": my_val == their_val,
                    "dir_name": d["dir_name"],
                })
                beats = (my_val >= their_val) if okitsu_tie_surge else (my_val > their_val)
                if nb.get("owner") != owner and beats:
                    key = (nr, nc)
                    if key not in seen_coords:
                        seen_coords.add(key)
                        captured.append({
                            "nr": nr,
                            "nc": nc,
                            "myVal": my_val,
                            "theirVal": their_val,
                            "dirName": d["dir_name"],
                            "rule": "OKITSU_TIE" if (okitsu_tie_surge and my_val == their_val) else "HIGH_PIP",
                        })

    # 2. SAME rule (2+ orthogonal neighbors have my_val == their_val)
    special_queue: List[Dict[str, Any]] = []
    equal_nbs = [n for n in occupied_neighbors if n["equal"]]
    if len(equal_nbs) >= 2:
        for n in equal_nbs:
            if n["owner"] != owner:
                key = (n["nr"], n["nc"])
                evt = {
                    "nr": n["nr"],
                    "nc": n["nc"],
                    "myVal": n["my_val"],
                    "theirVal": n["their_val"],
                    "dirName": n["dir_name"],
                    "rule": "SAME",
                }
                special_queue.append(evt)
                if key not in seen_coords:
                    seen_coords.add(key)
                    captured.append(evt)

    # 3. PLUS rule (2+ orthogonal neighbors share identical edge_sum)
    sum_groups: Dict[int, List[Dict[str, Any]]] = {}
    for n in occupied_neighbors:
        sum_groups.setdefault(n["edge_sum"], []).append(n)
    for edge_sum, grp in sum_groups.items():
        if len(grp) >= 2:
            for n in grp:
                if n["owner"] != owner:
                    key = (n["nr"], n["nc"])
                    evt = {
                        "nr": n["nr"],
                        "nc": n["nc"],
                        "myVal": n["my_val"],
                        "theirVal": n["their_val"],
                        "edgeSum": edge_sum,
                        "dirName": n["dir_name"],
                        "rule": "PLUS",
                    }
                    special_queue.append(evt)
                    if key not in seen_coords:
                        seen_coords.add(key)
                        captured.append(evt)

    # 4. COMBO_CASCADE from SAME / PLUS flips
    while special_queue:
        src = special_queue.pop(0)
        src_cell = grid[src["nr"]][src["nc"]]
        if not src_cell or not src_cell.get("cardId"):
            continue
        for d in ORTHO_DIRS:
            ar, ac = src["nr"] + d["dr"], src["nc"] + d["dc"]
            if 0 <= ar < 3 and 0 <= ac < 3:
                adj = grid[ar][ac]
                key = (ar, ac)
                if adj and adj.get("cardId") and adj.get("owner") != owner and key not in seen_coords:
                    src_edge = int(src_cell["nesw"][d["my_edge"]])
                    adj_edge = int(adj["nesw"][d["their_edge"]])
                    if src_edge > adj_edge:
                        seen_coords.add(key)
                        cascade_evt = {
                            "nr": ar,
                            "nc": ac,
                            "fromR": src["nr"],
                            "fromC": src["nc"],
                            "myVal": src_edge,
                            "theirVal": adj_edge,
                            "dirName": d["dir_name"],
                            "rule": "COMBO_CASCADE",
                        }
                        captured.append(cascade_evt)
                        special_queue.append(cascade_evt)

    return captured


# ============================================================================
# 2. 15-STAGE IVALICE OVERWORLD CHRONICLE NODE GRAPH (3 ACTS)
# ============================================================================

ACTS_METADATA: List[Dict[str, Any]] = [
    {
        "act_id": "ACT_I",
        "act_number": 1,
        "title": "Act I: Sky-Stone Border",
        "i18n_key": "act_1_title",
        "stage_indices": [0, 1, 2, 3, 4],
        "biome_theme": "Floating Limestone Citadels & Windmill Ridges",
        "default_judge_law_id": "STANDARD_HIGH_PIP",
    },
    {
        "act_id": "ACT_II",
        "act_number": 2,
        "title": "Act II: Clockwork Sanctum",
        "i18n_key": "act_2_title",
        "stage_indices": [5, 6, 7, 8, 9],
        "biome_theme": "Brass Astrolabe Vaults & Mnemosyne Resonance Nodes",
        "default_judge_law_id": "MNEMOSYNE_NODE_RESONANCE",
    },
    {
        "act_id": "ACT_III",
        "act_number": 3,
        "title": "Act III: Cradle of Echoes",
        "i18n_key": "act_3_title",
        "stage_indices": [10, 11, 12, 13, 14],
        "biome_theme": "Astral Singularity Rifts & Okitsu Sovereign Sanctum",
        "default_judge_law_id": "OKITSU_TIE_SURGE",
    },
]


def build_ivalice_15_stage_chronicle_graph() -> List[Dict[str, Any]]:
    """
    Build the 15-Stage Ivalice Overworld Chronicle Node Graph across 3 Acts:
      - Act I: Sky-Stone Border (stages 0..4)
      - Act II: Clockwork Sanctum (stages 5..9)
      - Act III: Cradle of Echoes (stages 10..14)
    Includes branching paths, (x, y) coordinates, Boss Commander IDs, Judge Laws, and Reward Relics.
    """
    raw_stages = [
        # ---------------- ACT I: SKY-STONE BORDER (0..4) ----------------
        {
            "stage_index": 0,
            "stage_id": "stage_01",
            "act_id": "ACT_I",
            "act_title": "Act I: Sky-Stone Border",
            "name": "Act I-1: Skystone Sanctuary",
            "biome": "Sky-Stone Border",
            "bg_art": "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
            "x": 70,
            "y": 260,
            "edges": [1, 2],
            "boss_commander_id": "e_eclipse",
            "boss_name": "Eclipse Void Blade",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_eclipse.png?v=tele4",
            "ai_bonus": 0,
            "reward_coins": 80,
            "judge_law": {
                "law_id": "STANDARD_HIGH_PIP",
                "name": "High-Pip & Faction Link Decree",
                "banner_key": "judge_law_standard",
                "banner": "JUDGE LAW: High-Pip & Faction Link Decree",
                "rule_modifier": "Adjacent same-faction allies gain +1 on shared edges; Pip 4-6 Column Dice grant +1 All Sides.",
            },
            "reward_relic": {
                "relic_id": "relic_01_skystone_compass",
                "name": "Skystone Astrolabe Compass",
                "effect": "+1 Starting Column Die Nudge on Turn 1",
                "bonus_coins": 80,
            },
        },
        {
            "stage_index": 1,
            "stage_id": "stage_02",
            "act_id": "ACT_I",
            "act_title": "Act I: Sky-Stone Border",
            "name": "Act I-2: Ivalice Citadel",
            "biome": "Sky-Stone Border",
            "bg_art": "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
            "x": 155,
            "y": 155,
            "edges": [3],
            "boss_commander_id": "e_archon",
            "boss_name": "Prism Core Archon",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_archon.png?v=tele4",
            "ai_bonus": 0,
            "reward_coins": 90,
            "judge_law": {
                "law_id": "SAME_PLUS_CASCADE",
                "name": "Ivalice Same / Plus & Combo Cascade",
                "banner_key": "judge_law_same_plus",
                "banner": "JUDGE LAW: Ivalice Same / Plus & Combo Cascade Active",
                "rule_modifier": "Matching 2+ equal opposing edges (SAME) or 2+ identical edge sums (PLUS) triggers chain captures.",
            },
            "reward_relic": {
                "relic_id": "relic_02_citadel_signet",
                "name": "Citadel Judge Signet",
                "effect": "Grants +25 Bonus Aether Coins on SAME/PLUS captures",
                "bonus_coins": 90,
            },
        },
        {
            "stage_index": 2,
            "stage_id": "stage_03",
            "act_id": "ACT_I",
            "act_title": "Act I: Sky-Stone Border",
            "name": "Act I-3: Solar Spire",
            "biome": "Sky-Stone Border",
            "bg_art": "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
            "x": 155,
            "y": 365,
            "edges": [3, 4],
            "boss_commander_id": "e_cryo",
            "boss_name": "Cryo Interceptor",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_cryo.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 100,
            "judge_law": {
                "law_id": "STANDARD_HIGH_PIP",
                "name": "Solaris High-Pip Decree",
                "banner_key": "judge_law_standard",
                "banner": "JUDGE LAW: High-Pip & Faction Link Decree",
                "rule_modifier": "Solaris and Aether cards gain +1 N/S resonance when deployed in boosted columns.",
            },
            "reward_relic": {
                "relic_id": "relic_03_solar_sunstone",
                "name": "Sunstone Prism Lens",
                "effect": "Column 1 Die starts at minimum Pip 4 (+1 Boost ready)",
                "bonus_coins": 100,
            },
        },
        {
            "stage_index": 3,
            "stage_id": "stage_04",
            "act_id": "ACT_I",
            "act_title": "Act I: Sky-Stone Border",
            "name": "Act I-4: Windmill Bastion",
            "biome": "Sky-Stone Border",
            "bg_art": "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
            "x": 245,
            "y": 200,
            "edges": [4, 5],
            "boss_commander_id": "e_shinobi",
            "boss_name": "Cyber Shinobi",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_shinobi.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 110,
            "judge_law": {
                "law_id": "SAME_PLUS_CASCADE",
                "name": "Windmill Tactical Slide Law",
                "banner_key": "judge_law_same_plus",
                "banner": "JUDGE LAW: Ivalice Same / Plus & Combo Cascade Active",
                "rule_modifier": "Tactical Slide bank maneuvers trigger full SAME/PLUS directional evaluations.",
            },
            "reward_relic": {
                "relic_id": "relic_04_zephyr_pinion",
                "name": "Zephyr Windmill Pinion",
                "effect": "Tactical Slide grants +1 East/West edge guard for 1 turn",
                "bonus_coins": 110,
            },
        },
        {
            "stage_index": 4,
            "stage_id": "stage_05",
            "act_id": "ACT_I",
            "act_title": "Act I: Sky-Stone Border",
            "name": "Act I-5: Aetherial Sky-Bridge",
            "biome": "Sky-Stone Border",
            "bg_art": "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
            "x": 325,
            "y": 310,
            "edges": [5, 6],
            "boss_commander_id": "e_colossus",
            "boss_name": "Emerald Colossus",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 120,
            "judge_law": {
                "law_id": "STANDARD_HIGH_PIP",
                "name": "Sky-Bridge Border Warden Law",
                "banner_key": "judge_law_standard",
                "banner": "JUDGE LAW: High-Pip & Faction Link Decree",
                "rule_modifier": "Act I Finale: Disrupted Boss telegraphs suffer -1 on South & West defending edges.",
            },
            "reward_relic": {
                "relic_id": "relic_05_aether_keystone",
                "name": "Aetherial Bridge Keystone",
                "effect": "Unlocks Act II Clockwork Sanctum & +1 Reroll charge",
                "bonus_coins": 120,
            },
        },
        # ---------------- ACT II: CLOCKWORK SANCTUM (5..9) ----------------
        {
            "stage_index": 5,
            "stage_id": "stage_06",
            "act_id": "ACT_II",
            "act_title": "Act II: Clockwork Sanctum",
            "name": "Act II-6: Clockwork Sanctum Gate",
            "biome": "Clockwork Sanctum",
            "bg_art": "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
            "x": 415,
            "y": 165,
            "edges": [6, 7],
            "boss_commander_id": "e_titan",
            "boss_name": "Bastion Dreadnought",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_titan.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 130,
            "judge_law": {
                "law_id": "MNEMOSYNE_NODE_RESONANCE",
                "name": "Mnemosyne Center Sanctum (+1 All Stats & +50G)",
                "banner_key": "judge_law_mnemosyne",
                "banner": "JUDGE LAW: Mnemosyne Center Sanctum (+1 All Stats & +50G)",
                "rule_modifier": "Deploying or sliding into Center Socket (2,2) grants +1 All Sides and +50 Aether Coins.",
            },
            "reward_relic": {
                "relic_id": "relic_06_chronos_escapement",
                "name": "Brass Escapement Gear",
                "effect": "Center Socket (2,2) resonance also fortifies adjacent allies",
                "bonus_coins": 130,
            },
        },
        {
            "stage_index": 6,
            "stage_id": "stage_07",
            "act_id": "ACT_II",
            "act_title": "Act II: Clockwork Sanctum",
            "name": "Act II-7: Orbital Mecha Bay",
            "biome": "Clockwork Sanctum",
            "bg_art": "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
            "x": 495,
            "y": 350,
            "edges": [7, 8],
            "boss_commander_id": "e_colossus",
            "boss_name": "Emerald Colossus",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 140,
            "judge_law": {
                "law_id": "MNEMOSYNE_NODE_RESONANCE",
                "name": "Orbital Resonance Law",
                "banner_key": "judge_law_mnemosyne",
                "banner": "JUDGE LAW: Mnemosyne Center Sanctum (+1 All Stats & +50G)",
                "rule_modifier": "Center Socket (2,2) amplifies orbital airstrike & railgun telegraphs by +1 All Stats.",
            },
            "reward_relic": {
                "relic_id": "relic_07_orbital_gyro",
                "name": "Orbital Gyroscope Core",
                "effect": "+1 North/East stat on Valkyria & Chronos constructs",
                "bonus_coins": 140,
            },
        },
        {
            "stage_index": 7,
            "stage_id": "stage_08",
            "act_id": "ACT_II",
            "act_title": "Act II: Clockwork Sanctum",
            "name": "Act II-8: Solid Eye Bunker",
            "biome": "Clockwork Sanctum",
            "bg_art": "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
            "x": 565,
            "y": 220,
            "edges": [8, 9],
            "boss_commander_id": "e_shinobi",
            "boss_name": "Cyber Shinobi",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_shinobi.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 150,
            "judge_law": {
                "law_id": "SAME_PLUS_CASCADE",
                "name": "Solid Eye Halftone Decree",
                "banner_key": "judge_law_same_plus",
                "banner": "JUDGE LAW: Ivalice Same / Plus & Combo Cascade Active",
                "rule_modifier": "Horizontal sniper lock and PLUS/SAME combo cascades pierce enemy armor.",
            },
            "reward_relic": {
                "relic_id": "relic_08_solideye_visor",
                "name": "MGA2 Tactical Visor Lens",
                "effect": "Reveals top 2 MCTS Oracle lines with zero cost",
                "bonus_coins": 150,
            },
        },
        {
            "stage_index": 8,
            "stage_id": "stage_09",
            "act_id": "ACT_II",
            "act_title": "Act II: Clockwork Sanctum",
            "name": "Act II-9: STACCS Chrono Spire",
            "biome": "Clockwork Sanctum",
            "bg_art": "./GeneratedArt/env_breach_staccs_isometric_tower.png",
            "x": 640,
            "y": 140,
            "edges": [9, 10],
            "boss_commander_id": "e_reaper",
            "boss_name": "Sigil Wraith",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_reaper.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 165,
            "judge_law": {
                "law_id": "MNEMOSYNE_NODE_RESONANCE",
                "name": "STACCS Column Conduit Law",
                "banner_key": "judge_law_mnemosyne",
                "banner": "JUDGE LAW: Mnemosyne Center Sanctum (+1 All Stats & +50G)",
                "rule_modifier": "Center Socket (2,2) grants +1 All Stats & charges Column 2 Die.",
            },
            "reward_relic": {
                "relic_id": "relic_09_staccs_die_matrix",
                "name": "STACCS Brass Die Matrix",
                "effect": "Nudging a Column Die to Pip 6 triggers a 24fps Sakuga Surge",
                "bonus_coins": 165,
            },
        },
        {
            "stage_index": 9,
            "stage_id": "stage_10",
            "act_id": "ACT_II",
            "act_title": "Act II: Clockwork Sanctum",
            "name": "Act II-10: Mnemosyne Gear Vault",
            "biome": "Clockwork Sanctum",
            "bg_art": "./GeneratedArt/env_nakayama_neo_arcadia_mmz.png",
            "x": 650,
            "y": 355,
            "edges": [10, 11],
            "boss_commander_id": "e_inferno",
            "boss_name": "Inferno Seraph",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 180,
            "judge_law": {
                "law_id": "MNEMOSYNE_NODE_RESONANCE",
                "name": "Mnemosyne Sovereign Vault Law",
                "banner_key": "judge_law_mnemosyne",
                "banner": "JUDGE LAW: Mnemosyne Center Sanctum (+1 All Stats & +50G)",
                "rule_modifier": "Act II Finale: Center Socket (2,2) grants +1 All Stats & +50 Aether Coins.",
            },
            "reward_relic": {
                "relic_id": "relic_10_mnemosyne_pendulum",
                "name": "Mnemosyne Golden Pendulum",
                "effect": "Unlocks Act III Cradle of Echoes & Sovereign Plugin Synergy",
                "bonus_coins": 180,
            },
        },
        # ---------------- ACT III: CRADLE OF ECHOES (10..14) ----------------
        {
            "stage_index": 10,
            "stage_id": "stage_11",
            "act_id": "ACT_III",
            "act_title": "Act III: Cradle of Echoes",
            "name": "Act III-11: Breach Rift Alpha",
            "biome": "Cradle of Echoes",
            "bg_art": "./GeneratedArt/env_breach_staccs_isometric_tower.png",
            "x": 740,
            "y": 215,
            "edges": [11, 12],
            "boss_commander_id": "e_inferno",
            "boss_name": "Inferno Seraph",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 195,
            "judge_law": {
                "law_id": "OKITSU_TIE_SURGE",
                "name": "Okitsu Tie-Surge Decree",
                "banner_key": "judge_law_okitsu",
                "banner": "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)",
                "rule_modifier": "Equal opposing edge values (>=) trigger full directional captures in addition to SAME/PLUS.",
            },
            "reward_relic": {
                "relic_id": "relic_11_breach_capacitor",
                "name": "Breach Rift Capacitor",
                "effect": "Okitsu Tie-Surge captures grant +1 trauma screen impact & +20 Coins",
                "bonus_coins": 195,
            },
        },
        {
            "stage_index": 11,
            "stage_id": "stage_12",
            "act_id": "ACT_III",
            "act_title": "Act III: Cradle of Echoes",
            "name": "Act III-12: Umbra Singularity",
            "biome": "Cradle of Echoes",
            "bg_art": "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
            "x": 795,
            "y": 360,
            "edges": [12, 13],
            "boss_commander_id": "e_eclipse",
            "boss_name": "Eclipse Void Blade",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_eclipse.png?v=tele4",
            "ai_bonus": 1,
            "reward_coins": 210,
            "judge_law": {
                "law_id": "OKITSU_TIE_SURGE",
                "name": "Umbra Tie-Surge & Void Law",
                "banner_key": "judge_law_okitsu",
                "banner": "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)",
                "rule_modifier": "Equal edge pips capture enemies; Center Socket (2,2) grants +1 All Stats.",
            },
            "reward_relic": {
                "relic_id": "relic_12_umbra_sigil",
                "name": "Umbra Singularity Sigil",
                "effect": "Abyss & Aether cards gain +1 West edge in corner sockets",
                "bonus_coins": 210,
            },
        },
        {
            "stage_index": 12,
            "stage_id": "stage_13",
            "act_id": "ACT_III",
            "act_title": "Act III: Cradle of Echoes",
            "name": "Act III-13: Prism Octahedron",
            "biome": "Cradle of Echoes",
            "bg_art": "./GeneratedArt/env_isamu_kamikokuryo_skystone.png",
            "x": 850,
            "y": 145,
            "edges": [13, 14],
            "boss_commander_id": "e_archon",
            "boss_name": "Prism Core Archon",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_archon.png?v=tele4",
            "ai_bonus": 2,
            "reward_coins": 230,
            "judge_law": {
                "law_id": "OKITSU_TIE_SURGE",
                "name": "Prism Octahedron Law",
                "banner_key": "judge_law_okitsu",
                "banner": "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)",
                "rule_modifier": "Elite Boss (+2 AI Stat Bonus); Okitsu Tie-Surge & SAME/PLUS cascades active.",
            },
            "reward_relic": {
                "relic_id": "relic_13_prism_octahedron",
                "name": "Refractive Octahedron Core",
                "effect": "All 4 Sovereign Agent Plugins gain +1 Faction Link resonance",
                "bonus_coins": 230,
            },
        },
        {
            "stage_index": 13,
            "stage_id": "stage_14",
            "act_id": "ACT_III",
            "act_title": "Act III: Cradle of Echoes",
            "name": "Act III-14: Trigger Cross-Star",
            "biome": "Cradle of Echoes",
            "bg_art": "./GeneratedArt/env_breach_staccs_isometric_tower.png",
            "x": 885,
            "y": 310,
            "edges": [14],
            "boss_commander_id": "e_colossus",
            "boss_name": "Emerald Colossus",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_colossus.png?v=tele4",
            "ai_bonus": 2,
            "reward_coins": 255,
            "judge_law": {
                "law_id": "OKITSU_TIE_SURGE",
                "name": "Trigger 24fps Sakuga Law",
                "banner_key": "judge_law_okitsu",
                "banner": "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)",
                "rule_modifier": "Corner sockets trigger 4-point Cross-Star surge; Equal Edge Pips Capture.",
            },
            "reward_relic": {
                "relic_id": "relic_14_trigger_star_core",
                "name": "Studio Trigger Cross-Star Crest",
                "effect": "Corner deployments trigger 2-frame Impact Flash & +1 N/W",
                "bonus_coins": 255,
            },
        },
        {
            "stage_index": 14,
            "stage_id": "stage_15",
            "act_id": "ACT_III",
            "act_title": "Act III: Cradle of Echoes",
            "name": "Act III-15: Omega Chronos Prime",
            "biome": "Cradle of Echoes",
            "bg_art": "./GeneratedArt/env_hiroshi_minagawa_ivalice_diorama.png",
            "x": 945,
            "y": 235,
            "edges": [],
            "boss_commander_id": "e_inferno",
            "boss_name": "Inferno Seraph (Omega Chronos Prime)",
            "boss_avatar": "./GeneratedArt/MasteredCards/e_inferno.png?v=tele4",
            "ai_bonus": 2,
            "reward_coins": 300,
            "judge_law": {
                "law_id": "OKITSU_TIE_SURGE",
                "name": "Omega Sovereign Finale Law",
                "banner_key": "judge_law_okitsu",
                "banner": "JUDGE LAW: Okitsu Tie-Surge (Equal Edge Pips Capture!)",
                "rule_modifier": "Grand Finale: Center Mnemosyne (+1 All Stats) + Okitsu Tie-Surge + Full SAME/PLUS/COMBO.",
            },
            "reward_relic": {
                "relic_id": "relic_15_crown_of_echoes",
                "name": "Sovereign Crown of Echoes",
                "effect": "Completes the 15-Stage Ivalice Chronicle & unlocks Grandmaster Ghost Tier",
                "bonus_coins": 300,
            },
        },
    ]

    for st in raw_stages:
        st["coordinates"] = {"x": st["x"], "y": st["y"]}
        st["next_stage_ids"] = [f"stage_{idx + 1:02d}" for idx in st["edges"]]
        st["fnv1a_64_checksum"] = compute_dict_fnv1a_64(st)
    return raw_stages


def verify_chronicle_graph_dag(stages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify 15 stages across 3 acts form a connected, acyclic DAG from stage 0 to stage 14."""
    assert len(stages) == 15, f"Expected 15 stages, got {len(stages)}"
    acts_seen = {s["act_id"] for s in stages}
    assert acts_seen == {"ACT_I", "ACT_II", "ACT_III"}, f"Unexpected acts: {acts_seen}"

    # Reachability from 0
    visited = set()
    queue = [0]
    while queue:
        cur = queue.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        for nxt in stages[cur]["edges"]:
            assert nxt > cur, f"DAG cycle/backward edge detected: {cur} -> {nxt}"
            assert 0 <= nxt < 15, f"Out-of-range edge: {nxt}"
            queue.append(nxt)

    assert len(visited) == 15, f"Not all 15 stages reachable from stage 0: {visited}"
    branching_nodes = [s["stage_index"] for s in stages if len(s["edges"]) >= 2]
    total_edges = sum(len(s["edges"]) for s in stages)

    return {
        "valid_dag": True,
        "stages_count": len(stages),
        "acts_count": len(acts_seen),
        "reachable_from_root": len(visited),
        "branching_nodes_count": len(branching_nodes),
        "total_edges_count": total_edges,
    }


# ============================================================================
# 3. DETERMINISTIC `CF-RPL1` REPLAY SERIALIZER & DESERIALIZER
# ============================================================================

REPLAY_PREFIX = "CF-RPL1:"


def serialize_replay_cf_rpl1(replay_obj: Dict[str, Any]) -> str:
    """
    Serialize a deterministic CARDFRONT replay dictionary into a compact
    `CF-RPL1:<base64url_payload>.<fnv1a_64_hex>` string.
    """
    payload = copy.deepcopy(replay_obj)
    payload.setdefault("format", "CF-RPL1")
    payload.setdefault("version", 1)
    checksum = compute_dict_fnv1a_64(payload, exclude_keys=("fnv1a_64_checksum", "envelope"))
    payload["fnv1a_64_checksum"] = checksum
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    b64 = base64.urlsafe_b64encode(canonical_bytes).decode("ascii").rstrip("=")
    return f"{REPLAY_PREFIX}{b64}.{checksum}"


def deserialize_replay_cf_rpl1(envelope_str: str) -> Dict[str, Any]:
    """
    Deserialize and cryptographically verify a `CF-RPL1:<base64url>.<fnv1a_64_hex>` replay string.
    Raises ValueError if tampered or malformed.
    """
    if not isinstance(envelope_str, str) or not envelope_str.startswith(REPLAY_PREFIX):
        raise ValueError("Replay string must start with 'CF-RPL1:'")
    body = envelope_str[len(REPLAY_PREFIX):].strip()
    if "." not in body:
        raise ValueError("Replay string missing '.<fnv1a_64_hex>' checksum suffix")
    b64_part, claimed_hash = body.rsplit(".", 1)
    padding = "=" * ((4 - len(b64_part) % 4) % 4)
    decoded_bytes = base64.urlsafe_b64decode((b64_part + padding).encode("ascii"))
    data = json.loads(decoded_bytes.decode("utf-8"))
    expected_hash = compute_dict_fnv1a_64(data, exclude_keys=("fnv1a_64_checksum", "envelope"))
    if claimed_hash.lower() != expected_hash.lower() or data.get("fnv1a_64_checksum", "").lower() != expected_hash.lower():
        raise ValueError(f"CF-RPL1 checksum mismatch: claimed={claimed_hash}, expected={expected_hash}")
    return data


# ============================================================================
# 4. 10 GRANDMASTER GHOST DECKS LADDER
# ============================================================================

def build_grandmaster_ghost_ladder() -> List[Dict[str, Any]]:
    """Build 10 Grandmaster Ghost Decks with verified 12-star squad cap and `CF-RPL1` replays."""
    raw_ghosts = [
        {
            "ghost_id": "ghost_gm_01_alpha_sovereign",
            "rank": 10,
            "title": "Initiate of the Sky-Stone",
            "player_username": "AlphaSovereign",
            "elo_rating": 1650,
            "stage_index": 0,
            "faction_focus": "Solaris",
            "judge_law_id": "STANDARD_HIGH_PIP",
            "deck_card_ids": ["h_archangel", "h_valkyrie", "h_oracle", "h_kai", "e_eclipse"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_archangel", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_eclipse", "slotIndex": 2, "r": 0, "c": 2, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "h_valkyrie", "slotIndex": 5, "r": 1, "c": 2, "flips": 1},
            ],
        },
        {
            "ghost_id": "ghost_gm_02_valkyria_wing",
            "rank": 9,
            "title": "Windmill Lance Tactician",
            "player_username": "ValkyriaSkylance",
            "elo_rating": 1720,
            "stage_index": 2,
            "faction_focus": "Valkyria",
            "judge_law_id": "SAME_PLUS_CASCADE",
            "deck_card_ids": ["h_phoenix", "h_valkyrie", "h_kai", "h_chronos", "e_cryo"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "NUDGE_DIE", "colIndex": 0, "newPip": 5},
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_phoenix", "slotIndex": 3, "r": 1, "c": 0, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_cryo", "slotIndex": 0, "r": 0, "c": 0, "flips": 0},
            ],
        },
        {
            "ghost_id": "ghost_gm_03_okitsu_arbiter",
            "rank": 8,
            "title": "Citadel Lawkeeper",
            "player_username": "OkitsuArbiter",
            "elo_rating": 1790,
            "stage_index": 4,
            "faction_focus": "Solaris",
            "judge_law_id": "SAME_PLUS_CASCADE",
            "deck_card_ids": ["h_arbiter", "h_archangel", "h_oracle", "h_seraph", "e_archon"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_arbiter", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_archon", "slotIndex": 8, "r": 2, "c": 2, "flips": 0},
                {"turn": 3, "actor": "player", "action": "SLIDE", "cardId": "h_arbiter", "fromSlot": 4, "toSlot": 5, "flips": 1},
            ],
        },
        {
            "ghost_id": "ghost_gm_04_chronos_weaver",
            "rank": 7,
            "title": "Clockwork Sanctum Warden",
            "player_username": "ChronosEscapement",
            "elo_rating": 1860,
            "stage_index": 5,
            "faction_focus": "Chronos",
            "judge_law_id": "MNEMOSYNE_NODE_RESONANCE",
            "deck_card_ids": ["h_chronos", "plugin_02_parallel_swarm_orchestrator", "h_kai", "h_oracle", "e_shinobi"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_chronos", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_titan", "slotIndex": 3, "r": 1, "c": 0, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "plugin_02_parallel_swarm_orchestrator", "slotIndex": 6, "r": 2, "c": 0, "flips": 1},
            ],
        },
        {
            "ghost_id": "ghost_gm_05_solideye_phantom",
            "rank": 6,
            "title": "Solid Eye Halftone Operative",
            "player_username": "KaiHalftoneZero",
            "elo_rating": 1940,
            "stage_index": 7,
            "faction_focus": "Aether",
            "judge_law_id": "SAME_PLUS_CASCADE",
            "deck_card_ids": ["h_kai", "h_oracle", "plugin_01_tcg_creative_designer", "h_valkyrie", "e_colossus"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_kai", "slotIndex": 0, "r": 0, "c": 0, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_shinobi", "slotIndex": 2, "r": 0, "c": 2, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "plugin_01_tcg_creative_designer", "slotIndex": 4, "r": 1, "c": 1, "flips": 2},
            ],
        },
        {
            "ghost_id": "ghost_gm_06_mnemosyne_sage",
            "rank": 5,
            "title": "Archon of the Gear Vault",
            "player_username": "MnemosyneOracle",
            "elo_rating": 2030,
            "stage_index": 9,
            "faction_focus": "Aether",
            "judge_law_id": "MNEMOSYNE_NODE_RESONANCE",
            "deck_card_ids": ["h_oracle", "plugin_01_tcg_creative_designer", "plugin_03_jev_system_one", "h_archangel", "e_cryo"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "plugin_03_jev_system_one", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_inferno", "slotIndex": 7, "r": 2, "c": 1, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "h_oracle", "slotIndex": 8, "r": 2, "c": 2, "flips": 2},
            ],
        },
        {
            "ghost_id": "ghost_gm_07_jev_gatekeeper",
            "rank": 4,
            "title": "System One Calibrated Judge",
            "player_username": "JevSystemOneGM",
            "elo_rating": 2120,
            "stage_index": 11,
            "faction_focus": "Solaris",
            "judge_law_id": "OKITSU_TIE_SURGE",
            "deck_card_ids": ["plugin_03_jev_system_one", "h_arbiter", "h_archangel", "plugin_04_mlx_apple_silicon", "e_archon"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "plugin_03_jev_system_one", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_eclipse", "slotIndex": 3, "r": 1, "c": 0, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "h_arbiter", "slotIndex": 6, "r": 2, "c": 0, "flips": 2},
            ],
        },
        {
            "ghost_id": "ghost_gm_08_mlx_metal_titan",
            "rank": 3,
            "title": "A18 Pro Metal Sovereign",
            "player_username": "MlxAppleSiliconGM",
            "elo_rating": 2210,
            "stage_index": 12,
            "faction_focus": "Valkyria",
            "judge_law_id": "OKITSU_TIE_SURGE",
            "deck_card_ids": ["plugin_04_mlx_apple_silicon", "h_phoenix", "h_valkyrie", "plugin_02_parallel_swarm_orchestrator", "e_inferno"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "NUDGE_DIE", "colIndex": 1, "newPip": 4},
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "plugin_04_mlx_apple_silicon", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_archon", "slotIndex": 5, "r": 1, "c": 2, "flips": 0},
            ],
        },
        {
            "ghost_id": "ghost_gm_09_trigger_cross_star",
            "rank": 2,
            "title": "Studio Trigger 24fps Maestro",
            "player_username": "SakugaCrossStarGM",
            "elo_rating": 2310,
            "stage_index": 13,
            "faction_focus": "Abyss",
            "judge_law_id": "OKITSU_TIE_SURGE",
            "deck_card_ids": ["h_seraph", "plugin_01_tcg_creative_designer", "plugin_02_parallel_swarm_orchestrator", "h_chronos", "e_reaper"],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "h_seraph", "slotIndex": 8, "r": 2, "c": 2, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_colossus", "slotIndex": 5, "r": 1, "c": 2, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "plugin_01_tcg_creative_designer", "slotIndex": 4, "r": 1, "c": 1, "flips": 2},
            ],
        },
        {
            "ghost_id": "ghost_gm_10_omega_chronos_prime",
            "rank": 1,
            "title": "Supreme Sovereign of Cradle of Echoes",
            "player_username": "OmegaChronosPrime",
            "elo_rating": 2420,
            "stage_index": 14,
            "faction_focus": "Aether",
            "judge_law_id": "OKITSU_TIE_SURGE",
            "deck_card_ids": [
                "plugin_01_tcg_creative_designer",
                "plugin_02_parallel_swarm_orchestrator",
                "plugin_03_jev_system_one",
                "plugin_04_mlx_apple_silicon",
                "h_archangel",
            ],
            "opening_book_moves": [
                {"turn": 1, "actor": "player", "action": "DEPLOY", "cardId": "plugin_01_tcg_creative_designer", "slotIndex": 4, "r": 1, "c": 1, "flips": 1},
                {"turn": 2, "actor": "ai", "action": "DEPLOY", "cardId": "e_inferno", "slotIndex": 2, "r": 0, "c": 2, "flips": 0},
                {"turn": 3, "actor": "player", "action": "DEPLOY", "cardId": "plugin_03_jev_system_one", "slotIndex": 5, "r": 1, "c": 2, "flips": 2},
            ],
        },
    ]

    for g in raw_ghosts:
        total_stars = sum(CARD_CATALOG[cid]["star_cost"] for cid in g["deck_card_ids"])
        assert len(g["deck_card_ids"]) == 5, f"Ghost {g['ghost_id']} must have 5 cards"
        assert total_stars <= 12, f"Ghost {g['ghost_id']} exceeds 12-star cap: {total_stars}"
        g["squad_stars"] = total_stars
        replay_payload = {
            "replay_id": f"rpl_{g['ghost_id']}",
            "seed": 20261109 + g["rank"],
            "stage_index": g["stage_index"],
            "player_username": g["player_username"],
            "elo_rating": g["elo_rating"],
            "judge_law_id": g["judge_law_id"],
            "deck_card_ids": g["deck_card_ids"],
            "turns": g["opening_book_moves"],
        }
        g["sample_replay_cf_rpl1"] = serialize_replay_cf_rpl1(replay_payload)
        # Verify roundtrip immediately
        rt = deserialize_replay_cf_rpl1(g["sample_replay_cf_rpl1"])
        assert rt["replay_id"] == replay_payload["replay_id"]
        g["fnv1a_64_checksum"] = compute_dict_fnv1a_64(g)

    return raw_ghosts


# ============================================================================
# 5. DAILY SEEDED TACTICAL PUZZLE GENERATOR (7 SOLVE-IN-1-TURN LETHAL PUZZLES)
# ============================================================================

def build_and_verify_daily_lethal_puzzles() -> List[Dict[str, Any]]:
    """
    Build and mathematically verify 7 deterministic Daily Seeded Tactical Puzzles
    (`solve-in-1-turn` lethal capture puzzles covering HIGH_PIP, SAME, PLUS, COMBO_CASCADE,
    COLUMN_DIE_NUDGE, and OKITSU_TIE_SURGE).
    """
    puzzles_spec = [
        {
            "puzzle_id": "daily_puzzle_01",
            "day_index": 1,
            "seed": 20261101,
            "title": "Day 1: Solar Cruciform Double Capture",
            "subtitle": "Deploy Solar Archangel into Center Socket (2,2) to flip North & West foes in 1 turn.",
            "stage_index": 0,
            "judge_law_id": "STANDARD_HIGH_PIP",
            "okitsu_tie_surge": False,
            "col_dice": [4, 5, 2],
            "nudges_left": 1,
            "used_slide_this_turn": False,
            "hand": ["h_archangel", "h_kai"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_eclipse", "owner": "ai", "nesw": [6, 6, 5, 6]},
                {"r": 1, "c": 0, "cardId": "e_shinobi", "owner": "ai", "nesw": [7, 6, 6, 5]},
                {"r": 2, "c": 2, "cardId": "e_cryo", "owner": "ai", "nesw": [5, 7, 6, 7]},
                {"r": 2, "c": 0, "cardId": "h_oracle", "owner": "player", "nesw": [7, 7, 8, 7]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "h_archangel",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": None,
            },
        },
        {
            "puzzle_id": "daily_puzzle_02",
            "day_index": 2,
            "seed": 20261102,
            "title": "Day 2: Triple Triad SAME Rule Reversal",
            "subtitle": "Match exact opposing edges (N=7 vs S=7 and E=7 vs W=7) to trigger a SAME double flip.",
            "stage_index": 1,
            "judge_law_id": "SAME_PLUS_CASCADE",
            "okitsu_tie_surge": False,
            "col_dice": [2, 2, 2],
            "nudges_left": 0,
            "used_slide_this_turn": True,
            "hand": ["h_oracle", "h_chronos"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_reaper", "owner": "ai", "nesw": [6, 7, 7, 5]},
                {"r": 1, "c": 2, "cardId": "e_cryo", "owner": "ai", "nesw": [5, 7, 6, 7]},
                {"r": 2, "c": 0, "cardId": "e_eclipse", "owner": "ai", "nesw": [6, 6, 5, 6]},
                {"r": 0, "c": 0, "cardId": "h_valkyrie", "owner": "player", "nesw": [8, 8, 5, 6]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "h_oracle",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": None,
            },
        },
        {
            "puzzle_id": "daily_puzzle_03",
            "day_index": 3,
            "seed": 20261103,
            "title": "Day 3: Ivalice PLUS Rule & Combo Cascade",
            "subtitle": "Match identical edge sums (8+5=13 North & 6+7=13 West) to trigger PLUS + Combo Cascade!",
            "stage_index": 3,
            "judge_law_id": "SAME_PLUS_CASCADE",
            "okitsu_tie_surge": False,
            "col_dice": [2, 2, 2],
            "nudges_left": 0,
            "used_slide_this_turn": True,
            "hand": ["h_valkyrie", "h_kai"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_eclipse", "owner": "ai", "nesw": [6, 6, 5, 6]},
                {"r": 1, "c": 0, "cardId": "e_reaper", "owner": "ai", "nesw": [8, 7, 7, 5]},
                {"r": 0, "c": 0, "cardId": "e_archon", "owner": "ai", "nesw": [7, 5, 5, 5]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "h_valkyrie",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": None,
            },
        },
        {
            "puzzle_id": "daily_puzzle_04",
            "day_index": 4,
            "seed": 20261104,
            "title": "Day 4: Column Die Nudge Surge +1 Lethal",
            "subtitle": "Nudge Column 2 Die from Pip 3 -> Pip 4 (+1 All Sides), then deploy Phoenix Valkyrie!",
            "stage_index": 5,
            "judge_law_id": "MNEMOSYNE_NODE_RESONANCE",
            "okitsu_tie_surge": False,
            "col_dice": [2, 3, 2],
            "nudges_left": 1,
            "used_slide_this_turn": True,
            "hand": ["h_phoenix"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_titan", "owner": "ai", "nesw": [7, 5, 8, 6]},
                {"r": 1, "c": 2, "cardId": "e_colossus", "owner": "ai", "nesw": [6, 8, 5, 8]},
                {"r": 2, "c": 0, "cardId": "h_kai", "owner": "player", "nesw": [7, 8, 6, 7]},
            ],
            "winning_move": {
                "action_type": "NUDGE_AND_DEPLOY",
                "hand_index": 0,
                "card_id": "h_phoenix",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": 1,
            },
        },
        {
            "puzzle_id": "daily_puzzle_05",
            "day_index": 5,
            "seed": 20261105,
            "title": "Day 5: Sovereign Plugin Quad-Edge Sweep",
            "subtitle": "Deploy Hallowed Arbiter of System One into (1,1) to capture North, South, and West foes.",
            "stage_index": 8,
            "judge_law_id": "MNEMOSYNE_NODE_RESONANCE",
            "okitsu_tie_surge": False,
            "col_dice": [2, 5, 2],
            "nudges_left": 0,
            "used_slide_this_turn": True,
            "hand": ["plugin_03_jev_system_one", "h_chronos"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_inferno", "owner": "ai", "nesw": [7, 7, 6, 6]},
                {"r": 2, "c": 1, "cardId": "e_archon", "owner": "ai", "nesw": [7, 6, 6, 5]},
                {"r": 1, "c": 0, "cardId": "e_eclipse", "owner": "ai", "nesw": [6, 6, 5, 6]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "plugin_03_jev_system_one",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": None,
            },
        },
        {
            "puzzle_id": "daily_puzzle_06",
            "day_index": 6,
            "seed": 20261106,
            "title": "Day 6: Okitsu Tie-Surge Equal-Pip Breakthrough",
            "subtitle": "Under Act III Okitsu Law, equal opposing pips (>=) capture! Deploy A18 Pro Metal Sovereign.",
            "stage_index": 11,
            "judge_law_id": "OKITSU_TIE_SURGE",
            "okitsu_tie_surge": True,
            "col_dice": [2, 2, 2],
            "nudges_left": 0,
            "used_slide_this_turn": True,
            "hand": ["plugin_04_mlx_apple_silicon"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_reaper", "owner": "ai", "nesw": [6, 7, 7, 5]},
                {"r": 1, "c": 2, "cardId": "e_cryo", "owner": "ai", "nesw": [5, 7, 6, 7]},
                {"r": 2, "c": 1, "cardId": "e_titan", "owner": "ai", "nesw": [7, 5, 7, 6]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "plugin_04_mlx_apple_silicon",
                "slot_index": 4,
                "r": 1,
                "c": 1,
                "pre_nudge_col": None,
            },
        },
        {
            "puzzle_id": "daily_puzzle_07",
            "day_index": 7,
            "seed": 20261107,
            "title": "Day 7: Omega Chronos Finale — Sun Arbiter Law Seal",
            "subtitle": "Deploy Sun Arbiter into (0,2) with Column 3 Boost to capture South & West constructs.",
            "stage_index": 14,
            "judge_law_id": "OKITSU_TIE_SURGE",
            "okitsu_tie_surge": True,
            "col_dice": [2, 2, 6],
            "nudges_left": 1,
            "used_slide_this_turn": False,
            "hand": ["h_arbiter", "h_seraph"],
            "board_setup": [
                {"r": 0, "c": 1, "cardId": "e_colossus", "owner": "ai", "nesw": [6, 8, 5, 6]},
                {"r": 1, "c": 2, "cardId": "e_inferno", "owner": "ai", "nesw": [8, 7, 5, 6]},
                {"r": 2, "c": 2, "cardId": "e_eclipse", "owner": "ai", "nesw": [6, 6, 5, 6]},
                {"r": 2, "c": 0, "cardId": "h_archangel", "owner": "player", "nesw": [8, 7, 6, 7]},
            ],
            "winning_move": {
                "action_type": "DEPLOY",
                "hand_index": 0,
                "card_id": "h_arbiter",
                "slot_index": 2,
                "r": 0,
                "c": 2,
                "pre_nudge_col": None,
            },
        },
    ]

    verified_puzzles: List[Dict[str, Any]] = []
    for p in puzzles_spec:
        # Build 3x3 board
        grid: List[List[Dict[str, Any]]] = [
            [{"r": r, "c": c, "cardId": None, "owner": None, "nesw": [0, 0, 0, 0]} for c in range(3)]
            for r in range(3)
        ]
        for cell in p["board_setup"]:
            grid[cell["r"]][cell["c"]] = {
                "r": cell["r"],
                "c": cell["c"],
                "cardId": cell["cardId"],
                "owner": cell["owner"],
                "nesw": list(cell["nesw"]),
            }

        col_dice = list(p["col_dice"])
        wm = p["winning_move"]
        if wm.get("pre_nudge_col") is not None:
            ncol = int(wm["pre_nudge_col"])
            col_dice[ncol] = (col_dice[ncol] % 6) + 1

        cid = wm["card_id"]
        tr, tc = int(wm["r"]), int(wm["c"])
        base_nesw = list(CARD_CATALOG[cid]["nesw"])
        col_boost = 1 if col_dice[tc] >= 4 else 0
        mnemosyne_boost = 1 if (p["judge_law_id"] == "MNEMOSYNE_NODE_RESONANCE" and tr == 1 and tc == 1) else 0
        eff_nesw = [min(9, v + col_boost + mnemosyne_boost) for v in base_nesw]

        grid[tr][tc] = {"r": tr, "c": tc, "cardId": cid, "owner": "player", "nesw": eff_nesw}
        flips = evaluate_board_captures(grid, tr, tc, eff_nesw, "player", okitsu_tie_surge=bool(p["okitsu_tie_surge"]))
        for f in flips:
            grid[f["nr"]][f["nc"]]["owner"] = "player"

        blue_score = sum(1 for row in grid for cell in row if cell["owner"] == "player")
        red_score = sum(1 for row in grid for cell in row if cell["owner"] == "ai")
        assert len(flips) >= 2, f"Puzzle {p['puzzle_id']} expected >=2 flips, got {len(flips)}"
        assert blue_score > red_score, f"Puzzle {p['puzzle_id']} did not achieve lethal win: {blue_score} vs {red_score}"

        wm["flips_count"] = len(flips)
        wm["rules_triggered"] = sorted({f["rule"] for f in flips})
        wm["final_score_blue"] = blue_score
        wm["final_score_red"] = red_score
        p["verified_lethal_1_turn"] = True
        p["fnv1a_64_checksum"] = compute_dict_fnv1a_64(p)
        verified_puzzles.append(p)

    return verified_puzzles


# ============================================================================
# 6. PUCT ALPHAZERO MCTS EVALUATOR (PYTHON REFERENCE + VERIFICATION)
# ============================================================================

class SynapseAlphaZeroMCTSEvaluator:
    """
    Deterministic PUCT MCTS + Policy-Value Tactical Oracle for CARDFRONT 3x3 board states.
    Evaluates all legal candidate moves (Deploy, Nudge+Deploy, Tactical Slide) using:
      PUCT(s, a) = Q(s, a) + c_puct * P(s, a) * sqrt(N(s)) / (1 + N(s, a))
    """

    def __init__(self, c_puct: float = 1.414, simulations: int = 64) -> None:
        self.c_puct = float(c_puct)
        self.simulations = int(simulations)

    def evaluate_state(
        self,
        grid: List[List[Dict[str, Any]]],
        hand: List[str],
        col_dice: List[int],
        nudges_left: int = 1,
        okitsu_tie_surge: bool = False,
    ) -> Dict[str, Any]:
        candidates: List[Dict[str, Any]] = []
        for h_idx, cid in enumerate(hand):
            card_meta = CARD_CATALOG.get(cid, {"id": cid, "name": cid, "nesw": [7, 7, 7, 7]})
            for r in range(3):
                for c in range(3):
                    if grid[r][c].get("cardId") is not None:
                        continue
                    slot_idx = r * 3 + c
                    boost = 1 if col_dice[c] >= 4 else 0
                    eff_nesw = [min(9, v + boost) for v in card_meta["nesw"]]
                    flips = evaluate_board_captures(grid, r, c, eff_nesw, "player", okitsu_tie_surge=okitsu_tie_surge)
                    center_bonus = 0.18 if (r == 1 and c == 1) else (0.10 if (r != 1 and c != 1) else 0.04)
                    edge_avg = sum(eff_nesw) / 36.0
                    raw_gain = len(flips) * 1.35 + center_bonus + edge_avg * 0.45
                    candidates.append({
                        "actionType": "DEPLOY",
                        "label": f"Deploy {card_meta['name']} -> ({r + 1},{c + 1})",
                        "slotIndex": slot_idx,
                        "r": r,
                        "c": c,
                        "cardId": cid,
                        "cardName": card_meta["name"],
                        "handIndex": h_idx,
                        "flipsCount": len(flips),
                        "rulesTriggered": sorted({f["rule"] for f in flips}),
                        "rawGain": round(raw_gain, 4),
                    })

        if not candidates:
            return {"winProbPct": 50.0, "valueScore": 0.0, "topMoves": []}

        # Softmax prior probabilities P(s, a)
        max_g = max(m["rawGain"] for m in candidates)
        exp_scores = [math.exp(m["rawGain"] - max_g) for m in candidates]
        sum_exp = sum(exp_scores) or 1.0
        for m, es in zip(candidates, exp_scores):
            m["priorProb"] = round(es / sum_exp, 4)
            m["visits"] = 0
            m["valueSum"] = 0.0
            m["qValue"] = 0.0
            m["expectedGain"] = round(m["rawGain"], 3)

        # Run PUCT MCTS rollouts
        for sim in range(1, self.simulations + 1):
            best_m = None
            best_puct = -1e9
            sqrt_n = math.sqrt(sim)
            for m in candidates:
                u = self.c_puct * m["priorProb"] * (sqrt_n / (1.0 + m["visits"]))
                q = m["qValue"]
                score = q + u
                if score > best_puct:
                    best_puct = score
                    best_m = m
            assert best_m is not None
            leaf_v = math.tanh(best_m["rawGain"] * 0.55)
            best_m["visits"] += 1
            best_m["valueSum"] += leaf_v
            best_m["qValue"] = round(best_m["valueSum"] / best_m["visits"], 4)
            best_m["expectedGain"] = round(best_m["rawGain"], 3)

        candidates.sort(key=lambda x: (x["visits"], x["qValue"], x["expectedGain"]), reverse=True)
        top_moves = candidates[:5]
        best_val = top_moves[0]["qValue"]
        win_prob = round(50.0 + 48.0 * best_val, 1)
        return {
            "winProbPct": max(1.0, min(99.5, win_prob)),
            "valueScore": round(best_val, 4),
            "simulationsRun": self.simulations,
            "cPuct": self.c_puct,
            "topMoves": [
                {
                    "actionType": m["actionType"],
                    "label": m["label"],
                    "slotIndex": m["slotIndex"],
                    "r": m["r"],
                    "c": m["c"],
                    "cardId": m["cardId"],
                    "cardName": m["cardName"],
                    "expectedGain": m["expectedGain"],
                    "visits": m["visits"],
                    "qValue": m["qValue"],
                    "flipsCount": m["flipsCount"],
                    "rulesTriggered": m["rulesTriggered"],
                }
                for m in top_moves
            ],
        }


# ============================================================================
# 7. VERIFY 10-LANGUAGE LOCALIZATION TABLE & WRITE MANIFEST
# ============================================================================

REQUIRED_LANGS = ("EN", "JA", "KO", "ZH-Hans", "ZH-Hant", "FR", "DE", "ES", "PT-BR", "IT")
REQUIRED_STRING_KEYS = (
    "your_turn",
    "boss_turn",
    "hero_hand",
    "deck_label",
    "victory",
    "defeat",
    "draw_match",
    "tactical_slide",
    "column_dice",
    "overworld_chronicle",
    "mcts_oracle",
    "replay_theater",
    "colorblind_mode",
)
REQUIRED_PALETTES = ("standard", "deuteranopia", "protanopia", "tritanopia")


def verify_i18n_10lang_table() -> Dict[str, Any]:
    """Verify `Assets/Resources/Localization/i18n_strings_10lang.json` completeness."""
    assert I18N_JSON_PATH.exists(), f"Missing i18n JSON at {I18N_JSON_PATH}"
    data = json.loads(I18N_JSON_PATH.read_text(encoding="utf-8"))
    langs = data.get("supported_languages", [])
    assert tuple(langs) == REQUIRED_LANGS, f"Expected {REQUIRED_LANGS}, got {langs}"

    strings = data.get("strings", {})
    for key in REQUIRED_STRING_KEYS:
        assert key in strings, f"Missing required i18n key: {key}"
        for lang in REQUIRED_LANGS:
            val = strings[key].get(lang, "")
            assert isinstance(val, str) and len(val.strip()) > 0, f"Empty translation for {key}.{lang}"

    palettes = data.get("colorblind_palettes", {})
    for pal_id in REQUIRED_PALETTES:
        assert pal_id in palettes, f"Missing colorblind palette: {pal_id}"

    return {
        "verified": True,
        "path": str(I18N_JSON_PATH),
        "languages_count": len(langs),
        "core_keys_verified": len(REQUIRED_STRING_KEYS),
        "total_string_keys": len(strings),
        "colorblind_palettes_count": len(palettes),
        "fnv1a_64_checksum": compute_dict_fnv1a_64(data),
    }


def generate_and_verify_all() -> Dict[str, Any]:
    """Run all generators and verifiers and write `Logs/ivalice_chronicle_and_replay_manifest.json`."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    stages = build_ivalice_15_stage_chronicle_graph()
    dag_report = verify_chronicle_graph_dag(stages)
    ghost_ladder = build_grandmaster_ghost_ladder()
    daily_puzzles = build_and_verify_daily_lethal_puzzles()
    i18n_report = verify_i18n_10lang_table()

    # Sample MCTS evaluation on Daily Puzzle #1 initial board
    p0 = daily_puzzles[0]
    sample_grid = [
        [{"r": r, "c": c, "cardId": None, "owner": None, "nesw": [0, 0, 0, 0]} for c in range(3)]
        for r in range(3)
    ]
    for cell in p0["board_setup"]:
        sample_grid[cell["r"]][cell["c"]] = dict(cell)
    mcts = SynapseAlphaZeroMCTSEvaluator(c_puct=1.414, simulations=64)
    mcts_eval = mcts.evaluate_state(
        sample_grid,
        p0["hand"],
        p0["col_dice"],
        nudges_left=p0["nudges_left"],
        okitsu_tie_surge=p0["okitsu_tie_surge"],
    )

    manifest: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "module_id": "Synapse-Ivalice-Chronicle-Replay-MCTS-i18n",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "VERIFIED",
        "stages_count": len(stages),
        "acts_count": len(ACTS_METADATA),
        "ghost_ladder_count": len(ghost_ladder),
        "daily_puzzles_count": len(daily_puzzles),
        "languages_count": i18n_report["languages_count"],
        "colorblind_palettes_count": i18n_report["colorblind_palettes_count"],
        "dag_verification": dag_report,
        "i18n_verification": i18n_report,
        "mcts_oracle_sample": mcts_eval,
        "acts": ACTS_METADATA,
        "stages": stages,
        "ghost_ladder": ghost_ladder,
        "daily_puzzles": daily_puzzles,
    }
    manifest["fnv1a_64_checksum"] = compute_dict_fnv1a_64(manifest)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    report = generate_and_verify_all()
    print(
        json.dumps(
            {
                "status": report["status"],
                "stages_count": report["stages_count"],
                "acts_count": report["acts_count"],
                "ghost_ladder_count": report["ghost_ladder_count"],
                "daily_puzzles_count": report["daily_puzzles_count"],
                "languages_count": report["languages_count"],
                "colorblind_palettes_count": report["colorblind_palettes_count"],
                "mcts_top_move": report["mcts_oracle_sample"]["topMoves"][0]["label"],
                "fnv1a_64_checksum": report["fnv1a_64_checksum"],
            },
            indent=2,
        )
    )
