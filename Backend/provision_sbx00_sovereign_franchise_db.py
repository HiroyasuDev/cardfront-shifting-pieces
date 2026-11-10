#!/usr/bin/env python3
"""
Backend/provision_sbx00_sovereign_franchise_db.py
=================================================
CARDFRONT 3D: Cradle of Echoes — Track 3: `SBX00` (`192.168.86.32`) Sovereign Franchise
Database & Production Asset Vault Provisioning (`/DATA/SovereignVault/CARDFRONT_SAGA_VAULT`).

Why `SBX00` (`/DATA/SovereignVault/CARDFRONT_SAGA_VAULT`) is the Canonical Franchise Database Host:
  - `SBX00` (`192.168.86.32:2222`, `ssh sbx00-direct`) mounts the 7.2 TB `/DATA/SovereignVault`
    RAID/vault array (`~5.9 TB` available across `sda`/`sdb`/`sdc`/`sdd`) alongside GitLab CE (`:8929`),
    MinIO S3 (`:9000`), MariaDB (`:3306`), Redis (`:6379`), OpenBao, and Perforce (`:1666`).
  - CRITICAL HARDWARE GUARD: `SBX00`'s root partition `/` (`/dev/mmcblk0p2`) is a `29 GB` SD card at
    `99%` capacity (`~191 MB` free). This script explicitly verifies that `/DATA/SovereignVault` has
    `> 5,000 GB` free and strictly prohibits writing to `/home/pxadmin` or `/`, provisioning all
    database, LoRA `.safetensors`, and manifest artifacts exclusively inside
    `/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/`.

Materializes Locally & Remotely:
  1. `Datasets/cardfront_sovereign_franchise_sbx00.sqlite3` (8 relational tables, WAL mode, FK enabled)
  2. Remote sync to `sbx00-direct:/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/{db,models_lora,manifests}`
  3. `Logs/sbx00_sovereign_database_sync_report.json`
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "Datasets"
LOGS_DIR = PROJECT_ROOT / "Logs"
LORA_DIR = PROJECT_ROOT / "Models" / "LoRA"
SAKUGA_DIR = PROJECT_ROOT / "GeneratedArt" / "SakugaCutIns"

LOCAL_SQLITE_PATH = DATASETS_DIR / "cardfront_sovereign_franchise_sbx00.sqlite3"
SYNC_REPORT_PATH = LOGS_DIR / "sbx00_sovereign_database_sync_report.json"

SBX00_SSH_ALIAS = "sbx00-direct"
SBX00_HOST_IP = "192.168.86.32"
SBX00_SSH_PORT = 2222
SBX00_VAULT_MOUNT = "/DATA/SovereignVault"
SBX00_VAULT_ROOT = "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT"
SBX00_MIN_FREE_GB = 5000


# =============================================================================
# 1. 3 GRAND FRANCHISE ERAS (Years 1-10)
# =============================================================================
FRANCHISE_ERAS: List[Dict[str, Any]] = [
    {
        "era_id": "ERA_I_CRADLE_KUBRART_ECLIPSE",
        "era_number": 1,
        "title": "Era I: Cradle of Echoes & Kubrart Eclipse",
        "years_span": "Years 1-3 (Sets 01-06)",
        "start_year": 1,
        "end_year": 3,
        "narrative_arc": (
            "Awakening of the 3x3 Sky-Citadel Monoliths, the Kubrart Negative-Space Eclipse, "
            "and the First Convergence of the Five Factions."
        ),
        "signature_mechanics": "Directional NESW Capture, SAME/PLUS/COMBO_CASCADE, 1x Tactical Slide, Column Dice Parity",
        "visual_lineage": "Ivalice Watercolor Cel-Wash, Kubrart Vector-Cel Negative Space, Seinen G-Pen Sumi-e Crosshatch",
        "headliner_herald_ids": "herald_01_echo_sovereign,herald_02_kubrart_eclipse_archon",
    },
    {
        "era_id": "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR",
        "era_number": 2,
        "title": "Era II: Sovran Mechanica & Chrono-Lattice War",
        "years_span": "Years 4-7 (Sets 07-14)",
        "start_year": 4,
        "end_year": 7,
        "narrative_arc": (
            "Orbital Cyber-Magicite Mecha Armadas descend upon Neo-Arcadia as the 1440-Frame "
            "Chrono-Lattice fractures across parallel timeline branches."
        ),
        "signature_mechanics": "Genie 4 Promptable World Events, Elevation Z-Axis Siege, Chrono-Rewind Echo Ghosts, Synchro-Link",
        "visual_lineage": "7.5-Head Cyber-Magicite Orthographic Cel, CMYK Screentone Halftone, 24fps Sakuga Kagenashi Flare",
        "headliner_herald_ids": "herald_03_sovran_mechanica_prime,herald_04_chrono_lattice_arbiter",
    },
    {
        "era_id": "ERA_III_ASTRAL_SINGULARITY_OMEGA",
        "era_number": 3,
        "title": "Era III: Astral Singularity & Omega Convergence",
        "years_span": "Years 8-10 (Sets 15-20)",
        "start_year": 8,
        "end_year": 10,
        "narrative_arc": (
            "The Sovereign Agent Conduits and Totema Primordials unite across all 93 Realms to "
            "reforge the Astral Singularity and crown the Eternal Tactician."
        ),
        "signature_mechanics": "Multi-Realm Portal Shift, Sovereign Law-Gate Tribunal, Omni-Directional Prism Resonance",
        "visual_lineage": "12-Lineage TIES-Merged Master Soup, Chiaroscuro Obsidian-Ivory Tarot Foil, Luminous Gouache Citadel",
        "headliner_herald_ids": "herald_05_astral_singularity_seraph,herald_06_omega_convergence_monolith",
    },
]


# =============================================================================
# 2. 20 MAJOR EXPANSION SETS (SET_01..SET_20, 120 Cards/Set = 2,400 Planned)
# =============================================================================
EXPANSION_SETS_10YR: List[Dict[str, Any]] = [
    ("SET_01", 1, "Q1", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Cradle of Echoes", "Standard Year 1-2", 120, "NESW Capture, Column Dice, 1x Slide", 1.00),
    ("SET_02", 1, "Q3", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Kubrart Astral Eclipse & Manga Vanguard", "Standard Year 1-2", 120, "SAME, PLUS, COMBO_CASCADE, Prime Edge Flip", 1.02),
    ("SET_03", 2, "Q1", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Sovereign Agent Grimoire", "Standard Year 1-2", 120, "Law-Gate Verification, Subagent Swarm, MCP Conduit", 1.03),
    ("SET_04", 2, "Q3", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Studio PxG: Trigger Odyssey", "Standard Year 1-2", 120, "24fps Kagenashi Impact, Fisheye Lunge, Star-Flare", 1.04),
    ("SET_05", 3, "Q1", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Obsidian Tarot & Gilded Monolith", "Standard Year 2-3", 120, "Arcana Reversal, Chiaroscuro Seal, Blood Eclipse", 1.05),
    ("SET_06", 3, "Q3", "ERA_I_CRADLE_KUBRART_ECLIPSE", "Sky-Citadel Astrolabe", "Standard Year 2-3", 120, "Elevation High-Ground, Windward Slide, Gouache Aegis", 1.06),
    ("SET_07", 4, "Q1", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Sovran Mechanica: Orbital Drop", "Standard Year 3-4", 120, "Cyber-Magicite Armor, Beveled Wing Intercept, Railgun Piercing", 1.07),
    ("SET_08", 4, "Q3", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Solid-Eye Espionage & Halftone Matrix", "Standard Year 3-4", 120, "90-Degree Vision Cone, Stealth Ambush, CMYK Decoy", 1.08),
    ("SET_09", 5, "Q1", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Chrono-Lattice 1440", "Standard Year 4-5", 120, "KV-Memory Recall, Temporal Dilation, Echo-Ghost Dual Play", 1.09),
    ("SET_10", 5, "Q3", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "DiceVaders Dreadnought Command", "Standard Year 4-5", 120, "Orbital Die Overcharge, Parity Lock, Column Laser Sweep", 1.10),
    ("SET_11", 6, "Q1", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Seinen Sumi-e: Crimson Ronin", "Standard Year 5-6", 120, "Iaijutsu Counter-Slash, Bleed Crosshatch, Lone-Wolf Stance", 1.11),
    ("SET_12", 6, "Q3", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Neo-Arcadia Cyber Rain", "Standard Year 5-6", 120, "Hologram Grid Beacon, Corner Resonance, Overclock Cost-1", 1.12),
    ("SET_13", 7, "Q1", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Hi3D Voxel & Normal-Bridge Relics", "Standard Year 6-7", 120, "2.5D Relief Shield, Watertight Manifold Lock, Relic Equip", 1.13),
    ("SET_14", 7, "Q3", "ERA_II_SOVRAN_MECHANICA_CHRONO_WAR", "Totema Cataclysm", "Standard Year 6-7", 120, "Totema World-Summon, 3-Slot Colossal Unit, Law Tribunal", 1.14),
    ("SET_15", 8, "Q1", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Astral Singularity: Dawn of System One", "Standard Year 7-8", 120, "Calibrated Probability Flip, Noul Nullification, Zero-Entropy", 1.15),
    ("SET_16", 8, "Q3", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Twelve-Master Atelier Odyssey", "Standard Year 7-8", 120, "TIES-Merged Aura, Dual-Lineage Fusion, Masterwork Foil", 1.16),
    ("SET_17", 9, "Q1", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Genie 4 Causality & World Shaper", "Standard Year 8-9", 120, "Causal-DiT Flow Shift, VQ-Action 16 Combo, Arena Mutator", 1.17),
    ("SET_18", 9, "Q3", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Valkyria & Abyssal Apocalypse", "Standard Year 8-9", 120, "Solar Flare Corona, Abyssal Drain, Dual-Faction Pact", 1.18),
    ("SET_19", 10, "Q1", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Chronicle of the Eternal Ladder", "Standard Year 9-10", 120, "AlphaZero PUCT Foresight, Grandmaster Crest, Legacy Echo", 1.19),
    ("SET_20", 10, "Q3", "ERA_III_ASTRAL_SINGULARITY_OMEGA", "Omega Convergence: Cradle Reborn", "Eternal + Standard Year 9-10", 120, "Omega Triad Synthesis, All-Edge Harmonic, Sovereign Finale", 1.20),
]


# =============================================================================
# 3. 37 SOVEREIGN AGENT DECK + 6 10-YEAR SAGA ERA HERALDS
# =============================================================================
SOVEREIGN_AGENT_DECK_37: List[Tuple[str, str, str, int, List[int], str]] = [
    ("plugin_01_tcg_creative_designer", "Grand Arcanist of CardCraft", "Artisan", 5, [8, 7, 6, 7], "ab_plugin_tcg_designer"),
    ("plugin_02_parallel_swarm_orchestrator", "Chronos Swarm Commander", "Tech", 5, [7, 8, 6, 7], "ab_plugin_swarm_orchestrator"),
    ("plugin_03_jev_system_one", "Hallowed Arbiter of System One", "Divine", 4, [8, 6, 8, 6], "ab_plugin_jev_system_one"),
    ("plugin_04_mlx_apple_silicon", "A18 Pro Metal Forge Sovereign", "Tech", 4, [7, 7, 7, 7], "ab_plugin_mlx_silicon"),
    ("skill_01_master_router", "Compass of the 93 Realms", "Magic", 3, [7, 6, 6, 6], "ab_skill_master_router"),
    ("skill_02_tactical_illustrator_library", "Twelve-Master Atelier Grimoire", "Artisan", 4, [7, 7, 5, 7], "ab_skill_atelier_grimoire"),
    ("skill_03_create_game_assets", "Aegis of Deterministic Raster QA", "Artisan", 4, [6, 7, 7, 6], "ab_skill_raster_qa"),
    ("skill_04_card_game_genre", "Chronicle of the Single Zone", "Divine", 4, [8, 6, 6, 6], "ab_skill_single_zone"),
    ("skill_05_game_feel_juice", "Valkyrie of Kinetic Impact", "Divine", 3, [7, 7, 5, 5], "ab_skill_kinetic_juice"),
    ("skill_06_game_ui_ux", "Oracle of Responsive Anchors", "Magic", 3, [6, 6, 7, 6], "ab_skill_ui_anchors"),
    ("skill_07_ai_utility_behavior", "Archon of Utility & Negamax", "Tech", 4, [7, 8, 5, 6], "ab_skill_ai_negamax"),
    ("skill_08_shader_camera_audio", "Seraph of Halftone & Harmony", "Artisan", 3, [6, 7, 6, 6], "ab_skill_halftone_harmony"),
    ("skill_09_save_procgen_dialogue", "Keeper of Mnemosyne Vaults", "Magic", 3, [6, 5, 7, 7], "ab_skill_mnemosyne_vault"),
    ("skill_10_multi_engine_codex", "Titan of the Twelve Engines", "Tech", 4, [7, 6, 7, 6], "ab_skill_twelve_engines"),
    ("skill_11_decompilation_hi3d_rea", "Sovereign of Hi3D & Decompilation", "Stealth", 5, [8, 7, 6, 6], "ab_skill_hi3d_rea"),
    ("skill_12_workflows_and_agent_core", "Herald of the Golden Master", "Divine", 3, [6, 6, 6, 7], "ab_skill_golden_master"),
    ("tool_01_invoke_subagent", "Summon Parallel Phantom", "Tech", 3, [7, 7, 5, 6], "ab_tool_invoke_subagent"),
    ("tool_02_define_subagent", "Forge Specialist Construct", "Artisan", 3, [6, 7, 6, 5], "ab_tool_define_subagent"),
    ("tool_03_manage_subagents", "Tactical Swarm Overwatch", "Tech", 2, [6, 5, 6, 6], "ab_tool_manage_subagents"),
    ("tool_04_send_message", "Astral Telepathic Relay", "Magic", 1, [5, 6, 5, 6], "ab_tool_send_message"),
    ("tool_05_call_mcp_tool", "Channel Arcane MCP Conduit", "Magic", 3, [7, 6, 7, 5], "ab_tool_call_mcp"),
    ("tool_06_mcp_resources", "Scry Nexus Resource Archive", "Stealth", 2, [5, 6, 6, 6], "ab_tool_mcp_resources"),
    ("tool_07_run_command", "Incantation of the Zsh Shell", "Tech", 3, [8, 6, 5, 6], "ab_tool_run_command"),
    ("tool_08_manage_task", "Chrono Daemon Tether", "Magic", 2, [5, 6, 6, 5], "ab_tool_manage_task"),
    ("tool_09_read_file", "True-Sight Omniscient Lens", "Stealth", 2, [6, 6, 6, 6], "ab_tool_read_file"),
    ("tool_10_write_file", "Inscribe Sovereign Grimoire", "Artisan", 3, [7, 6, 6, 6], "ab_tool_write_file"),
    ("tool_11_edit_file", "Precision Rune Scalpel", "Stealth", 3, [7, 7, 5, 5], "ab_tool_edit_file"),
    ("tool_12_search_schedule_ask", "Astral Horizon & Oracle Call", "Divine", 2, [6, 5, 6, 6], "ab_tool_search_schedule"),
    ("mcp_01_jev_system_one", "Jev System One Tribunal", "Divine", 4, [8, 6, 7, 6], "ab_mcp_jev_tribunal"),
    ("mcp_02_jev_py_verifier", "Jev-Py Deterministic Verifier", "Divine", 4, [7, 7, 7, 6], "ab_mcp_jev_py"),
    ("mcp_03_mlx_apple_silicon", "MLX Metal GPU Matrix", "Tech", 4, [7, 8, 6, 6], "ab_mcp_mlx_matrix"),
    ("mcp_04_prime_rlm_swarm", "Prime Vision & RLM Swarm Core", "Tech", 4, [7, 7, 6, 7], "ab_mcp_prime_swarm"),
    ("mcp_05_sequential_thinking", "Astrolabe of Sequential Thought", "Magic", 3, [6, 6, 7, 6], "ab_mcp_seq_thinking"),
    ("mcp_06_knowledge_graph_mem", "Nexus of the Memory Graph", "Magic", 3, [6, 7, 6, 6], "ab_mcp_memory_graph"),
    ("mcp_07_git_time_chronicle", "Chrono-Branch Git Arbiter", "Stealth", 3, [6, 6, 6, 7], "ab_mcp_git_chronicle"),
    ("mcp_08_filesystem_and_fetch", "Citadel of Vault & Astral Fetch", "Stealth", 3, [6, 6, 6, 6], "ab_mcp_fs_fetch"),
    ("mcp_09_tcg_creative_studio", "Atelier of CardCraft MCP", "Artisan", 4, [8, 7, 6, 7], "ab_mcp_tcg_studio"),
]

SAGA_ERA_HERALDS_6: List[Tuple[str, str, str, str, int, List[int], str, str]] = [
    (
        "herald_01_echo_sovereign",
        "Aethelgard: Sovereign of the First Echo",
        "SET_01",
        "Divine",
        6,
        [9, 8, 8, 7],
        "ab_herald_first_echo",
        "synapse_aether_cel_v1_lora",
    ),
    (
        "herald_02_kubrart_eclipse_archon",
        "Nyx-00: Kubrart Eclipse Archon",
        "SET_02",
        "Magic",
        6,
        [8, 9, 7, 8],
        "ab_herald_kubrart_eclipse",
        "kubrart_vector_cel_ink_v1_lora",
    ),
    (
        "herald_03_sovran_mechanica_prime",
        "Hyperion-X: Sovran Mechanica Prime",
        "SET_07",
        "Tech",
        6,
        [9, 9, 6, 8],
        "ab_herald_sovran_mechanica",
        "cyber_mecha_orthographic_cel_v1_lora",
    ),
    (
        "herald_04_chrono_lattice_arbiter",
        "Chronos-1440: Lattice Time Arbiter",
        "SET_09",
        "Magic",
        6,
        [8, 8, 9, 8],
        "ab_herald_chrono_lattice",
        "genie4_world_model_causal_dit_v1",
    ),
    (
        "herald_05_astral_singularity_seraph",
        "Seraphim-One: Astral Singularity Gate",
        "SET_15",
        "Divine",
        6,
        [9, 8, 9, 8],
        "ab_herald_astral_singularity",
        "anime_sakuga_kagenashi_keyframe_v2_lora",
    ),
    (
        "herald_06_omega_convergence_monolith",
        "Omega-Triad: Convergence Monolith",
        "SET_20",
        "Artisan",
        6,
        [9, 9, 9, 9],
        "ab_herald_omega_convergence",
        "ties_merged_master_soup_v1",
    ),
]

# 5 Mech-Wing Maiden Evolve Pairs (10 Cards: ev_01_base/evo .. ev_05_base/evo)
EVOLVE_MECH_WING_PAIRS_5: List[Dict[str, Any]] = [
    {
        "pair_id": "PAIR_EV_01",
        "base_card_id": "ev_01_base",
        "evolved_card_id": "ev_01_evo",
        "base_name": "Seraphina: Mech-Wing Maiden [進化前]",
        "evolved_name": "Seraphina: Astral Overdrive Seraph [進化後]",
        "set_code": "SET_07",
        "faction": "Divine",
        "cost": 4,
        "evolve_cost_ep": 1,
        "trait": "Angel · Mech / 天使・機械",
        "frame_style": "SHADOWVERSE_EVOLVE_GUNMETAL_SR_UR",
        "base_nesw": [7, 7, 5, 6],
        "evolved_nesw": [9, 9, 7, 8],
        "base_ability_id": "ab_ev01_aegis_thruster_base",
        "evolved_ability_id": "ab_ev01_astral_overdrive_evo",
        "lora_adapter_id": "cyber_mecha_orthographic_cel_v1_lora",
        "on_evolve_effect": (
            "【進化時】 Spend 1 EP: Gain +2/+2/+2/+2 NESW, ignite 6-wing cyber-magicite solar feathers, "
            "and flip up to 2 adjacent orthogonal enemy units with S or W <= 7."
        ),
    },
    {
        "pair_id": "PAIR_EV_02",
        "base_card_id": "ev_02_base",
        "evolved_card_id": "ev_02_evo",
        "base_name": "Celestia-02: Railgun Valkyrie Maiden [進化前]",
        "evolved_name": "Celestia-02: Hyper-Velocity Archangel [進化後]",
        "set_code": "SET_07",
        "faction": "Tech",
        "cost": 4,
        "evolve_cost_ep": 1,
        "trait": "Angel · Mech / 天使・機械",
        "frame_style": "SHADOWVERSE_EVOLVE_GUNMETAL_SR_UR",
        "base_nesw": [8, 6, 5, 7],
        "evolved_nesw": [10, 8, 7, 9],
        "base_ability_id": "ab_ev02_railgun_valkyrie_base",
        "evolved_ability_id": "ab_ev02_hyper_archangel_evo",
        "lora_adapter_id": "cyber_mecha_orthographic_cel_v1_lora",
        "on_evolve_effect": (
            "【進化時】 Spend 1 EP: Gain +2/+2/+2/+2 NESW, fire column-piercing positron lance, "
            "and set this column's die to 6."
        ),
    },
    {
        "pair_id": "PAIR_EV_03",
        "base_card_id": "ev_03_base",
        "evolved_card_id": "ev_03_evo",
        "base_name": "Lyra-Zero: Chrono-Pinion Maiden [進化前]",
        "evolved_name": "Lyra-Zero: Singularity Wing Sovereign [進化後]",
        "set_code": "SET_09",
        "faction": "Magic",
        "cost": 3,
        "evolve_cost_ep": 1,
        "trait": "Angel · Mech / 天使・機械",
        "frame_style": "SHADOWVERSE_EVOLVE_GUNMETAL_SR_UR",
        "base_nesw": [6, 7, 6, 7],
        "evolved_nesw": [8, 9, 8, 9],
        "base_ability_id": "ab_ev03_chrono_pinion_base",
        "evolved_ability_id": "ab_ev03_singularity_wing_evo",
        "lora_adapter_id": "anime_sakuga_kagenashi_keyframe_v2_lora",
        "on_evolve_effect": (
            "【進化時】 Spend 1 EP: Gain +2/+2/+2/+2 NESW, restore player 1x Tactical Slide charge, "
            "and trigger SAME/PLUS resonance check."
        ),
    },
    {
        "pair_id": "PAIR_EV_04",
        "base_card_id": "ev_04_base",
        "evolved_card_id": "ev_04_evo",
        "base_name": "Noctis-VII: Obsidian Feather Maiden [進化前]",
        "evolved_name": "Noctis-VII: Abyssal Eclipse Seraph [進化後]",
        "set_code": "SET_08",
        "faction": "Stealth",
        "cost": 4,
        "evolve_cost_ep": 1,
        "trait": "Angel · Mech / 天使・機械",
        "frame_style": "SHADOWVERSE_EVOLVE_GUNMETAL_SR_UR",
        "base_nesw": [7, 8, 6, 5],
        "evolved_nesw": [9, 10, 8, 7],
        "base_ability_id": "ab_ev04_obsidian_feather_base",
        "evolved_ability_id": "ab_ev04_abyssal_seraph_evo",
        "lora_adapter_id": "kubrart_vector_cel_ink_v1_lora",
        "on_evolve_effect": (
            "【進化時】 Spend 1 EP: Gain +2/+2/+2/+2 NESW, drain -1 from all opposing adjacent edges, "
            "and cloak against enemy slides."
        ),
    },
    {
        "pair_id": "PAIR_EV_05",
        "base_card_id": "ev_05_base",
        "evolved_card_id": "ev_05_evo",
        "base_name": "Aurelia-Omega: Gunmetal Halo Maiden [進化前]",
        "evolved_name": "Aurelia-Omega: Sovereign Evolve Archon [進化後]",
        "set_code": "SET_15",
        "faction": "Artisan",
        "cost": 5,
        "evolve_cost_ep": 1,
        "trait": "Angel · Mech / 天使・機械",
        "frame_style": "SHADOWVERSE_EVOLVE_GUNMETAL_SR_UR",
        "base_nesw": [8, 7, 7, 7],
        "evolved_nesw": [10, 9, 9, 9],
        "base_ability_id": "ab_ev05_gunmetal_halo_base",
        "evolved_ability_id": "ab_ev05_sovereign_archon_evo",
        "lora_adapter_id": "ties_merged_master_soup_v1",
        "on_evolve_effect": (
            "【進化時】 Spend 1 EP: Gain +2/+2/+2/+2 NESW, deploy gunmetal SR/UR holofoil barrier, "
            "and grant +1 all edges to allied Angel · Mech units."
        ),
    },
]


# =============================================================================
# 4. 4 GPU & STORAGE CLUSTER NODES
# =============================================================================
GPU_CLUSTER_NODES: List[Dict[str, Any]] = [
    {
        "node_id": "SBX00",
        "hostname": "sbx00-direct",
        "ip_address": "192.168.86.32",
        "ssh_port": 2222,
        "hardware_spec": "Sovereign Vault Server + 7.2TB RAID Array (/DATA/SovereignVault, 5.9TB Free) + 29GB Root SD Guarded",
        "accelerator": "Multi-Drive 7.2TB Vault Storage Array (sda/sdb/sdc/sdd)",
        "vram_or_storage_gb": 7331.0,
        "services": "Canonical SQLite/MariaDB (:3306), GitLab CE (:8929), MinIO S3 (:9000), Redis (:6379), Perforce (:1666), OpenBao",
        "role": "Canonical 10-Year Franchise Database & LoRA/Sakuga Production Asset Vault",
        "vault_mount_path": "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT",
    },
    {
        "node_id": "v100",
        "hostname": "v100",
        "ip_address": "192.168.86.116",
        "ssh_port": 22,
        "hardware_spec": "NVIDIA Tesla V100-PCIE-32GB HBM2 Deep Learning Compute Node",
        "accelerator": "NVIDIA Tesla V100-PCIE-32GB HBM2",
        "vram_or_storage_gb": 32.0,
        "services": "PyTorch QLoRA / DoRA Rank-16 Training, 24fps Sakuga Cut-In Strip Synthesizer, AlphaZero Self-Play",
        "role": "Heavy LoRA/DoRA Fine-Tuning & 24fps Sakuga Strip Batch Compute",
        "vault_mount_path": "/home/Ubuntu/synapse_v100_work",
    },
    {
        "node_id": "node30",
        "hostname": "node30-rtx4080",
        "ip_address": "192.168.86.30",
        "ssh_port": 22,
        "hardware_spec": "NVIDIA GeForce RTX 4080 16GB GDDR6X Studio Render & Vision Critic Node",
        "accelerator": "NVIDIA GeForce RTX 4080 16GB",
        "vram_or_storage_gb": 16.0,
        "services": "ComfyUI (:8188, animagineXLV31 + flux1-dev-fp8), Ollama (:11434, pxg-lumenforge:12b-tutor, qwen2.5vl:3b)",
        "role": "Real-Time 600x800 Card Portrait Generation & Multimodal Vision QA",
        "vault_mount_path": "http://192.168.86.30:8188",
    },
    {
        "node_id": "macbook-neo",
        "hostname": "macbook-neo.local",
        "ip_address": "192.168.86.125",
        "ssh_port": 22,
        "hardware_spec": "Apple Silicon Metal GPU Unified Memory Workstation",
        "accelerator": "Apple Silicon Metal GPU (Device(gpu, 0))",
        "vram_or_storage_gb": 8.0,
        "services": "Unity 6000.5.0a1 Headless Editor, Jev System One Gate, jevmlx Local Inference, WebPlayable Duel Server (:8765)",
        "role": "Primary Game Engine Authoring, Unity 6 Build Host & Jev Verification Gate",
        "vault_mount_path": str(PROJECT_ROOT),
    },
]


# =============================================================================
# 5. 10-YEAR ETHICAL NON-P2W MONETIZATION & LTV PROJECTIONS (Years 1-10)
# =============================================================================
ECONOMY_10YR_PROJECTIONS: List[Dict[str, Any]] = [
    {
        "year_num": yr,
        "active_Sets": f"SET_{(yr - 1) * 2 + 1:02d}..SET_{yr * 2:02d}",
        "mau_players": int(45000 * (1.28 ** (yr - 1))),
        "d1_retention_pct": round(min(74.0, 62.5 + yr * 1.1), 2),
        "d30_retention_pct": round(min(46.0, 31.0 + yr * 1.35), 2),
        "d365_retention_pct": round(min(28.5, 14.5 + yr * 1.25), 2),
        "cosmetic_pass_arppu_usd": round(14.50 + yr * 1.25, 2),
        "p2w_power_sales_usd": 0.0,
        "tournament_prize_pool_usd": int(50000 + (yr - 1) * 75000),
        "gross_revenue_usd": round(45000 * (1.28 ** (yr - 1)) * 0.18 * (14.50 + yr * 1.25) * 4.0, 2),
        "net_studio_margin_pct": round(min(48.5, 34.0 + yr * 1.4), 2),
        "monetization_model": "100% Ethical Non-P2W (2.5D Parallax Foil Shaders, 24fps Sakuga Cut-In Skins, Arena Boards, Chronicle Passes)",
    }
    for yr in range(1, 11)
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_sbx00_storage_guard() -> Dict[str, Any]:
    """
    Verifies via `ssh sbx00-direct` that `/DATA/SovereignVault` has > 5,000 GB free
    and documents the `/` (/dev/mmcblk0p2) 29GB SD card capacity guard.
    """
    cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=10",
        SBX00_SSH_ALIAS,
        f"df -BG {SBX00_VAULT_MOUNT} /",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [ln.strip() for ln in res.stdout.strip().splitlines() if ln.strip()]

    vault_free_gb = 0
    vault_total_gb = 0
    root_free_gb = 0
    root_total_gb = 0

    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) >= 6:
            mount_pt = parts[-1]
            total_g = int(parts[1].rstrip("G"))
            avail_g = int(parts[3].rstrip("G"))
            if mount_pt == SBX00_VAULT_MOUNT:
                vault_total_gb = total_g
                vault_free_gb = avail_g
            elif mount_pt == "/":
                root_total_gb = total_g
                root_free_gb = avail_g

    if vault_free_gb < SBX00_MIN_FREE_GB:
        raise RuntimeError(
            f"SBX00 storage guard failed: {SBX00_VAULT_MOUNT} has {vault_free_gb}GB free (< {SBX00_MIN_FREE_GB}GB required)"
        )

    return {
        "sbx00_host": SBX00_HOST_IP,
        "ssh_alias": SBX00_SSH_ALIAS,
        "vault_mount": SBX00_VAULT_MOUNT,
        "vault_total_gb": vault_total_gb,
        "vault_free_gb": vault_free_gb,
        "root_sd_card_total_gb": root_total_gb,
        "root_sd_card_free_gb": root_free_gb,
        "guard_passed": vault_free_gb >= SBX00_MIN_FREE_GB,
        "strict_write_prefix": SBX00_VAULT_ROOT,
        "raw_df_output": res.stdout.strip(),
    }


def collect_131_canonical_cards() -> List[Dict[str, Any]]:
    """
    Collects all 131 canonical playable cards materialized in the engine:
      - 60 Set 1 cards (`Datasets/set1_full_60_cards_and_15_campaign_stages.json`)
      - 20 Set 2 Kubrart/Manga cards (`Datasets/set2_kubrart_manga_expansion_manifest.json`)
      - 37 Sovereign Agent Deck cards (`SOVEREIGN_AGENT_DECK_37`)
      - 8 Studio PxG AAA Strikers (`Datasets/studio_pxg_aaa_assets_and_sakuga_manifest.json`)
      - 6 10-Year Saga Era Heralds (`SAGA_ERA_HERALDS_6`)
    Total = 131 canonical playable cards.
    """
    cards: List[Dict[str, Any]] = []

    # 1. 60 Set 1 Cards
    set1_path = DATASETS_DIR / "set1_full_60_cards_and_15_campaign_stages.json"
    set1_data = json.loads(set1_path.read_text(encoding="utf-8"))
    set1_roster = set1_data.get("set1_full_60_roster", [])
    for idx, c in enumerate(set1_roster[:60]):
        cid = c.get("card_id") or c.get("id") or f"cf_{idx + 1:02d}"
        stats = c.get("stats") or {}
        n = int(stats.get("up", c.get("n", 6)))
        e = int(stats.get("right", c.get("e", 6)))
        s = int(stats.get("down", c.get("s", 6)))
        w = int(stats.get("left", c.get("w", 6)))
        cost = int(c.get("cost", c.get("mga_cost", 4)))
        tier = int(c.get("tier", max(1, min(5, cost))))
        ability = c.get("ability") or {}
        ability_id = ability.get("id", f"ab_set1_{cid}") if isinstance(ability, dict) else f"ab_set1_{cid}"
        cards.append(
            {
                "card_id": cid,
                "name": c.get("name") or c.get("title") or cid,
                "set_code": "SET_01",
                "faction": c.get("faction_short") or c.get("faction") or "Aether",
                "cost": cost,
                "tier": tier,
                "rank_n": n,
                "rank_e": e,
                "rank_s": s,
                "rank_w": w,
                "ability_id": ability_id,
                "portrait_path": c.get("portrait_path") or f"Assets/Resources/CardFront/Portraits/{cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{cid}_strip.png",
                "lora_adapter_id": "synapse_aether_cel_v1_lora",
            }
        )

    # 2. 20 Set 2 Kubrart/Manga Cards
    set2_path = DATASETS_DIR / "set2_kubrart_manga_expansion_manifest.json"
    set2_data = json.loads(set2_path.read_text(encoding="utf-8"))
    for c in set2_data.get("cards", [])[:20]:
        cid = c.get("slug") or c.get("id")
        nesw = c.get("nesw") or [7, 7, 6, 7]
        ab = c.get("ability") or {}
        cards.append(
            {
                "card_id": cid,
                "name": c.get("name", cid),
                "set_code": "SET_02",
                "faction": c.get("faction", "Aether"),
                "cost": int(c.get("cost", 4)),
                "tier": int(c.get("tier", 4)),
                "rank_n": int(nesw[0]),
                "rank_e": int(nesw[1]),
                "rank_s": int(nesw[2]),
                "rank_w": int(nesw[3]),
                "ability_id": ab.get("id", f"ab_{cid}"),
                "portrait_path": f"Assets/Resources/CardFront/Portraits/{cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{cid}_strip.png",
                "lora_adapter_id": str(c.get("lora_file", "kubrart_vector_cel_ink_v1_lora.safetensors")).replace(
                    ".safetensors", ""
                ),
            }
        )

    # 3. 37 Sovereign Agent Deck Cards
    for cid, title, faction, cost, nesw, ab_id in SOVEREIGN_AGENT_DECK_37:
        cards.append(
            {
                "card_id": cid,
                "name": title,
                "set_code": "SET_03",
                "faction": faction,
                "cost": cost,
                "tier": max(1, min(5, cost)),
                "rank_n": nesw[0],
                "rank_e": nesw[1],
                "rank_s": nesw[2],
                "rank_w": nesw[3],
                "ability_id": ab_id,
                "portrait_path": f"GeneratedArt/AgentDeck/Cards/{cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{cid}_strip.png",
                "lora_adapter_id": "ties_merged_master_soup_v1",
            }
        )

    # 4. 8 Studio PxG AAA Strikers
    pxg_path = DATASETS_DIR / "studio_pxg_aaa_assets_and_sakuga_manifest.json"
    pxg_data = json.loads(pxg_path.read_text(encoding="utf-8"))
    for c in pxg_data.get("studio_pxg_strikers", [])[:8]:
        cid = c.get("slug") or c.get("id")
        nesw = c.get("nesw") or [8, 8, 6, 7]
        cards.append(
            {
                "card_id": cid,
                "name": c.get("name", cid),
                "set_code": "SET_04",
                "faction": c.get("faction", "Valkyria"),
                "cost": int(c.get("cost", 4)),
                "tier": 4,
                "rank_n": int(nesw[0]),
                "rank_e": int(nesw[1]),
                "rank_s": int(nesw[2]),
                "rank_w": int(nesw[3]),
                "ability_id": f"ab_{c.get('id', cid)}_trigger_odyssey",
                "portrait_path": f"GeneratedArt/StudioPxGStrikers/{cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{cid}_strip.png",
                "lora_adapter_id": "anime_sakuga_kagenashi_keyframe_v2_lora",
            }
        )

    # 5. 6 10-Year Saga Era Heralds
    for cid, name, set_code, faction, cost, nesw, ab_id, lora_id in SAGA_ERA_HERALDS_6:
        cards.append(
            {
                "card_id": cid,
                "name": name,
                "set_code": set_code,
                "faction": faction,
                "cost": cost,
                "tier": 5,
                "rank_n": nesw[0],
                "rank_e": nesw[1],
                "rank_s": nesw[2],
                "rank_w": nesw[3],
                "ability_id": ab_id,
                "portrait_path": f"Assets/Resources/CardFront/Portraits/{cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{cid}_strip.png",
                "lora_adapter_id": lora_id,
            }
        )

    # 6. 10 Evolve Mech-Wing Maiden Cards (5 Pairs: ev_01_base/evo .. ev_05_base/evo)
    for pair in EVOLVE_MECH_WING_PAIRS_5:
        b_cid = pair["base_card_id"]
        b_nesw = pair["base_nesw"]
        cards.append(
            {
                "card_id": b_cid,
                "name": pair["base_name"],
                "set_code": pair["set_code"],
                "faction": pair["faction"],
                "cost": int(pair["cost"]),
                "tier": 4,
                "rank_n": int(b_nesw[0]),
                "rank_e": int(b_nesw[1]),
                "rank_s": int(b_nesw[2]),
                "rank_w": int(b_nesw[3]),
                "ability_id": pair["base_ability_id"],
                "portrait_path": f"Assets/Resources/CardFront/Portraits/{b_cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{b_cid}_strip.png",
                "lora_adapter_id": pair["lora_adapter_id"],
            }
        )
        e_cid = pair["evolved_card_id"]
        e_nesw = pair["evolved_nesw"]
        cards.append(
            {
                "card_id": e_cid,
                "name": pair["evolved_name"],
                "set_code": pair["set_code"],
                "faction": pair["faction"],
                "cost": int(pair["cost"]),
                "tier": 5,
                "rank_n": int(e_nesw[0]),
                "rank_e": int(e_nesw[1]),
                "rank_s": int(e_nesw[2]),
                "rank_w": int(e_nesw[3]),
                "ability_id": pair["evolved_ability_id"],
                "portrait_path": f"Assets/Resources/CardFront/Portraits/{e_cid}.png",
                "sakuga_strip_path": f"GeneratedArt/SakugaCutIns/{e_cid}_strip.png",
                "lora_adapter_id": pair["lora_adapter_id"],
            }
        )

    return cards


def collect_lora_models() -> List[Dict[str, Any]]:
    """Scans all `.safetensors` checkpoints in `Models/LoRA/`."""
    models: List[Dict[str, Any]] = []
    for sf_path in sorted(LORA_DIR.glob("*.safetensors")):
        raw = sf_path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        header_len = int.from_bytes(raw[:8], "little")
        meta: Dict[str, Any] = {}
        try:
            header_obj = json.loads(raw[8 : 8 + header_len].decode("utf-8"))
            meta = header_obj.get("__metadata__", {})
        except Exception:
            pass

        model_id = meta.get("model_id") or meta.get("adapter_id") or sf_path.stem
        rank = int(meta.get("lora_rank", 16))
        alpha = int(meta.get("lora_alpha", 32))
        base_ckpt = meta.get("base_model") or meta.get("architecture") or "animagineXLV31_v31.safetensors"

        models.append(
            {
                "model_id": model_id,
                "filename": sf_path.name,
                "rank": rank,
                "alpha": alpha,
                "base_checkpoint": base_ckpt,
                "sha256": sha,
                "byte_size": len(raw),
            }
        )
    return models


def collect_sakuga_strips() -> List[Dict[str, Any]]:
    """Scans all `1920x160` 8-frame 24fps Sakuga strips in `GeneratedArt/SakugaCutIns/`."""
    strips: List[Dict[str, Any]] = []
    for st_path in sorted(SAKUGA_DIR.glob("*_strip.png")):
        sha = compute_sha256(st_path)
        strips.append(
            {
                "strip_id": st_path.stem,
                "filename": st_path.name,
                "dimensions": "1920x160",
                "frame_count": 8,
                "fps": 24,
                "xsheet_timing": "24fps 8-Frame Kagenashi Impact X-Sheet (Frames 1-2 Anticipation, 3-4 Smear/Star-Flare, 5-6 Impact Hold, 7-8 Follow-Through)",
                "sha256": sha,
                "byte_size": st_path.stat().st_size,
            }
        )
    return strips


def build_local_sqlite_database(
    cards: List[Dict[str, Any]],
    lora_models: List[Dict[str, Any]],
    sakuga_strips: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Creates `Datasets/cardfront_sovereign_franchise_sbx00.sqlite3` with 8 production tables,
    WAL mode, foreign keys enabled, and deterministic indexes.
    """
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    if LOCAL_SQLITE_PATH.exists():
        LOCAL_SQLITE_PATH.unlink()

    conn = sqlite3.connect(str(LOCAL_SQLITE_PATH))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA foreign_keys=ON;")

        # 1. franchise_eras
        cur.execute(
            """
            CREATE TABLE franchise_eras (
                era_id TEXT PRIMARY KEY,
                era_number INTEGER NOT NULL UNIQUE,
                title TEXT NOT NULL,
                years_span TEXT NOT NULL,
                start_year INTEGER NOT NULL,
                end_year INTEGER NOT NULL,
                narrative_arc TEXT NOT NULL,
                signature_mechanics TEXT NOT NULL,
                visual_lineage TEXT NOT NULL,
                headliner_herald_ids TEXT NOT NULL
            );
            """
        )

        # 2. expansion_sets_10yr
        cur.execute(
            """
            CREATE TABLE expansion_sets_10yr (
                set_code TEXT PRIMARY KEY,
                release_year INTEGER NOT NULL,
                release_quarter TEXT NOT NULL,
                era_id TEXT NOT NULL,
                set_title TEXT NOT NULL,
                rotation_window TEXT NOT NULL,
                planned_card_count INTEGER NOT NULL,
                mechanic_keywords TEXT NOT NULL,
                power_creep_budget REAL NOT NULL,
                FOREIGN KEY (era_id) REFERENCES franchise_eras(era_id)
            );
            """
        )

        # 3. canonical_cards_catalog
        cur.execute(
            """
            CREATE TABLE canonical_cards_catalog (
                card_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                set_code TEXT NOT NULL,
                faction TEXT NOT NULL,
                cost INTEGER NOT NULL,
                tier INTEGER NOT NULL,
                rank_n INTEGER NOT NULL,
                rank_e INTEGER NOT NULL,
                rank_s INTEGER NOT NULL,
                rank_w INTEGER NOT NULL,
                ability_id TEXT NOT NULL,
                portrait_path TEXT NOT NULL,
                sakuga_strip_path TEXT NOT NULL,
                lora_adapter_id TEXT NOT NULL,
                FOREIGN KEY (set_code) REFERENCES expansion_sets_10yr(set_code)
            );
            """
        )

        # 4. lora_model_zoo
        cur.execute(
            """
            CREATE TABLE lora_model_zoo (
                model_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                rank INTEGER NOT NULL,
                alpha INTEGER NOT NULL,
                base_checkpoint TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                byte_size INTEGER NOT NULL
            );
            """
        )

        # 5. sakuga_cutin_registry
        cur.execute(
            """
            CREATE TABLE sakuga_cutin_registry (
                strip_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                dimensions TEXT NOT NULL,
                frame_count INTEGER NOT NULL,
                fps INTEGER NOT NULL,
                xsheet_timing TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                byte_size INTEGER NOT NULL
            );
            """
        )

        # 6. gpu_cluster_nodes
        cur.execute(
            """
            CREATE TABLE gpu_cluster_nodes (
                node_id TEXT PRIMARY KEY,
                hostname TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                ssh_port INTEGER NOT NULL,
                hardware_spec TEXT NOT NULL,
                accelerator TEXT NOT NULL,
                vram_or_storage_gb REAL NOT NULL,
                services TEXT NOT NULL,
                role TEXT NOT NULL,
                vault_mount_path TEXT NOT NULL
            );
            """
        )

        # 7. franchise_economy_and_ltv_projections
        cur.execute(
            """
            CREATE TABLE franchise_economy_and_ltv_projections (
                year_num INTEGER PRIMARY KEY,
                active_sets TEXT NOT NULL,
                mau_players INTEGER NOT NULL,
                d1_retention_pct REAL NOT NULL,
                d30_retention_pct REAL NOT NULL,
                d365_retention_pct REAL NOT NULL,
                cosmetic_pass_arppu_usd REAL NOT NULL,
                p2w_power_sales_usd REAL NOT NULL,
                tournament_prize_pool_usd INTEGER NOT NULL,
                gross_revenue_usd REAL NOT NULL,
                net_studio_margin_pct REAL NOT NULL,
                monetization_model TEXT NOT NULL
            );
            """
        )

        # 8. sbx00_vault_sync_audit
        cur.execute(
            """
            CREATE TABLE sbx00_vault_sync_audit (
                artifact_key TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                local_rel_path TEXT NOT NULL,
                remote_vault_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                byte_size INTEGER NOT NULL,
                synced_utc TEXT NOT NULL
            );
            """
        )

        # 9. evolve_mech_wing_pairs (and evolve_cards_pair_registry alias table)
        for tbl_name in ("evolve_mech_wing_pairs", "evolve_cards_pair_registry"):
            cur.execute(
                f"""
                CREATE TABLE {tbl_name} (
                    pair_id TEXT PRIMARY KEY,
                    base_card_id TEXT NOT NULL UNIQUE,
                    evolved_card_id TEXT NOT NULL UNIQUE,
                    base_name TEXT NOT NULL,
                    evolved_name TEXT NOT NULL,
                    evolve_cost_ep INTEGER NOT NULL,
                    trait TEXT NOT NULL,
                    frame_style TEXT NOT NULL,
                    base_nesw TEXT NOT NULL,
                    evolved_nesw TEXT NOT NULL,
                    on_evolve_effect TEXT NOT NULL,
                    FOREIGN KEY (base_card_id) REFERENCES canonical_cards_catalog(card_id),
                    FOREIGN KEY (evolved_card_id) REFERENCES canonical_cards_catalog(card_id)
                );
                """
            )

        # 10. player_collection_ledger (Seeded with >= 45 starter & unlocked cards)
        cur.execute(
            """
            CREATE TABLE player_collection_ledger (
                player_id TEXT NOT NULL,
                card_id TEXT NOT NULL,
                title TEXT NOT NULL,
                rarity TEXT NOT NULL,
                foil_finish TEXT NOT NULL,
                copies_owned INTEGER NOT NULL DEFAULT 1,
                is_evolved_unlocked INTEGER NOT NULL DEFAULT 0,
                chibi_unit_id TEXT NOT NULL,
                first_acquired_utc TEXT NOT NULL,
                PRIMARY KEY (player_id, card_id),
                FOREIGN KEY (card_id) REFERENCES canonical_cards_catalog(card_id)
            );
            """
        )

        # 11. gacha_pack_pulls_history (Seeded with >= 5 historical pack pulls)
        cur.execute(
            """
            CREATE TABLE gacha_pack_pulls_history (
                pull_id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                set_code TEXT NOT NULL,
                pack_type TEXT NOT NULL,
                pity_counter_after INTEGER NOT NULL,
                guaranteed_sr_hit INTEGER NOT NULL,
                ur_or_evolve_hit INTEGER NOT NULL,
                pulled_cards_json TEXT NOT NULL,
                pulled_at_utc TEXT NOT NULL
            );
            """
        )

        # 12. ranked_elo_match_history (Seeded with >= 10 ranked match records)
        cur.execute(
            """
            CREATE TABLE ranked_elo_match_history (
                match_id TEXT PRIMARY KEY,
                season_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                opponent_id TEXT NOT NULL,
                player_elo_before INTEGER NOT NULL,
                player_elo_after INTEGER NOT NULL,
                elo_delta INTEGER NOT NULL,
                winner TEXT NOT NULL,
                turns_played INTEGER NOT NULL,
                evolve_triggered INTEGER NOT NULL,
                board_hash_hex TEXT NOT NULL,
                played_at_utc TEXT NOT NULL
            );
            """
        )

        # Deterministic Indexes
        cur.execute("CREATE INDEX idx_cards_set_faction ON canonical_cards_catalog(set_code, faction);")
        cur.execute("CREATE INDEX idx_sets_era_year ON expansion_sets_10yr(era_id, release_year);")
        cur.execute("CREATE INDEX idx_sakuga_sha256 ON sakuga_cutin_registry(sha256);")
        cur.execute("CREATE INDEX idx_collection_player ON player_collection_ledger(player_id);")
        cur.execute("CREATE INDEX idx_gacha_player_utc ON gacha_pack_pulls_history(player_id, pulled_at_utc);")
        cur.execute("CREATE INDEX idx_elo_player_utc ON ranked_elo_match_history(player_id, played_at_utc);")

        # Populate Table 1: franchise_eras
        for era in FRANCHISE_ERAS:
            cur.execute(
                """
                INSERT INTO franchise_eras (
                    era_id, era_number, title, years_span, start_year, end_year,
                    narrative_arc, signature_mechanics, visual_lineage, headliner_herald_ids
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    era["era_id"],
                    era["era_number"],
                    era["title"],
                    era["years_span"],
                    era["start_year"],
                    era["end_year"],
                    era["narrative_arc"],
                    era["signature_mechanics"],
                    era["visual_lineage"],
                    era["headliner_herald_ids"],
                ),
            )

        # Populate Table 2: expansion_sets_10yr
        for row in EXPANSION_SETS_10YR:
            cur.execute(
                """
                INSERT INTO expansion_sets_10yr (
                    set_code, release_year, release_quarter, era_id, set_title,
                    rotation_window, planned_card_count, mechanic_keywords, power_creep_budget
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                row,
            )

        # Populate Table 3: canonical_cards_catalog (131 cards)
        for c in cards:
            cur.execute(
                """
                INSERT INTO canonical_cards_catalog (
                    card_id, name, set_code, faction, cost, tier,
                    rank_n, rank_e, rank_s, rank_w, ability_id,
                    portrait_path, sakuga_strip_path, lora_adapter_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    c["card_id"],
                    c["name"],
                    c["set_code"],
                    c["faction"],
                    c["cost"],
                    c["tier"],
                    c["rank_n"],
                    c["rank_e"],
                    c["rank_s"],
                    c["rank_w"],
                    c["ability_id"],
                    c["portrait_path"],
                    c["sakuga_strip_path"],
                    c["lora_adapter_id"],
                ),
            )

        # Populate Table 4: lora_model_zoo
        for m in lora_models:
            cur.execute(
                """
                INSERT INTO lora_model_zoo (
                    model_id, filename, rank, alpha, base_checkpoint, sha256, byte_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    m["model_id"],
                    m["filename"],
                    m["rank"],
                    m["alpha"],
                    m["base_checkpoint"],
                    m["sha256"],
                    m["byte_size"],
                ),
            )

        # Populate Table 5: sakuga_cutin_registry
        for s in sakuga_strips:
            cur.execute(
                """
                INSERT INTO sakuga_cutin_registry (
                    strip_id, filename, dimensions, frame_count, fps, xsheet_timing, sha256, byte_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    s["strip_id"],
                    s["filename"],
                    s["dimensions"],
                    s["frame_count"],
                    s["fps"],
                    s["xsheet_timing"],
                    s["sha256"],
                    s["byte_size"],
                ),
            )

        # Populate Table 6: gpu_cluster_nodes
        for node in GPU_CLUSTER_NODES:
            cur.execute(
                """
                INSERT INTO gpu_cluster_nodes (
                    node_id, hostname, ip_address, ssh_port, hardware_spec,
                    accelerator, vram_or_storage_gb, services, role, vault_mount_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    node["node_id"],
                    node["hostname"],
                    node["ip_address"],
                    node["ssh_port"],
                    node["hardware_spec"],
                    node["accelerator"],
                    node["vram_or_storage_gb"],
                    node["services"],
                    node["role"],
                    node["vault_mount_path"],
                ),
            )

        # Populate Table 7: franchise_economy_and_ltv_projections
        for econ in ECONOMY_10YR_PROJECTIONS:
            cur.execute(
                """
                INSERT INTO franchise_economy_and_ltv_projections (
                    year_num, active_sets, mau_players, d1_retention_pct, d30_retention_pct,
                    d365_retention_pct, cosmetic_pass_arppu_usd, p2w_power_sales_usd,
                    tournament_prize_pool_usd, gross_revenue_usd, net_studio_margin_pct,
                    monetization_model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    econ["year_num"],
                    econ["active_Sets"],
                    econ["mau_players"],
                    econ["d1_retention_pct"],
                    econ["d30_retention_pct"],
                    econ["d365_retention_pct"],
                    econ["cosmetic_pass_arppu_usd"],
                    econ["p2w_power_sales_usd"],
                    econ["tournament_prize_pool_usd"],
                    econ["gross_revenue_usd"],
                    econ["net_studio_margin_pct"],
                    econ["monetization_model"],
                ),
            )

        # Populate Table 8: sbx00_vault_sync_audit
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for m in lora_models:
            cur.execute(
                """
                INSERT INTO sbx00_vault_sync_audit (
                    artifact_key, category, local_rel_path, remote_vault_path, sha256, byte_size, synced_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    f"lora:{m['filename']}",
                    "LORA_SAFETENSORS",
                    f"Models/LoRA/{m['filename']}",
                    f"{SBX00_VAULT_ROOT}/models_lora/{m['filename']}",
                    m["sha256"],
                    m["byte_size"],
                    now_utc,
                ),
            )

        manifest_files = [
            "set1_full_60_cards_and_15_campaign_stages.json",
            "set2_kubrart_manga_expansion_manifest.json",
            "studio_pxg_aaa_assets_and_sakuga_manifest.json",
            "genie4_world_model_inference_report.json",
            "anime_manga_illustration_models_manifest.json",
        ]
        for mf in manifest_files:
            mf_path = DATASETS_DIR / mf
            if mf_path.is_file():
                cur.execute(
                    """
                    INSERT INTO sbx00_vault_sync_audit (
                        artifact_key, category, local_rel_path, remote_vault_path, sha256, byte_size, synced_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        f"manifest:{mf}",
                        "JSON_MANIFEST",
                        f"Datasets/{mf}",
                        f"{SBX00_VAULT_ROOT}/manifests/{mf}",
                        compute_sha256(mf_path),
                        mf_path.stat().st_size,
                        now_utc,
                    ),
                )

        # Populate Table 9: evolve_mech_wing_pairs (and evolve_cards_pair_registry)
        for tbl_name in ("evolve_mech_wing_pairs", "evolve_cards_pair_registry"):
            for pair in EVOLVE_MECH_WING_PAIRS_5:
                cur.execute(
                    f"""
                    INSERT INTO {tbl_name} (
                        pair_id, base_card_id, evolved_card_id, base_name, evolved_name,
                        evolve_cost_ep, trait, frame_style, base_nesw, evolved_nesw, on_evolve_effect
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        pair["pair_id"],
                        pair["base_card_id"],
                        pair["evolved_card_id"],
                        pair["base_name"],
                        pair["evolved_name"],
                        int(pair["evolve_cost_ep"]),
                        pair["trait"],
                        pair["frame_style"],
                        json.dumps(pair["base_nesw"]),
                        json.dumps(pair["evolved_nesw"]),
                        pair["on_evolve_effect"],
                    ),
                )

        # Populate Table 10: player_collection_ledger (55 starter & unlocked cards >= 45 rows)
        starter_selection = (
            cards[:25]
            + cards[60:70]
            + cards[80:90]
            + cards[131:141]
        )
        for idx_c, sc in enumerate(starter_selection):
            cid = sc["card_id"]
            is_ev = 1 if cid.startswith("ev_") else 0
            if cid.startswith("ev_") or cid.startswith("herald_") or sc["tier"] >= 5:
                rarity_str = "UR_EVOLVE" if cid.startswith("ev_") else "UR"
                foil_str = "25D_PARALLAX_GOLD_UR"
            elif sc["tier"] == 4 or cid.startswith("set2_"):
                rarity_str = "SR"
                foil_str = "GUNMETAL_SR_PRISM"
            elif sc["tier"] == 3:
                rarity_str = "RARE"
                foil_str = "ASTRAL_CYAN_FOIL"
            else:
                rarity_str = "COMMON"
                foil_str = "STANDARD_MATTE"

            cur.execute(
                """
                INSERT OR REPLACE INTO player_collection_ledger (
                    player_id, card_id, title, rarity, foil_finish,
                    copies_owned, is_evolved_unlocked, chibi_unit_id, first_acquired_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    "SovereignArchitect",
                    cid,
                    sc["name"],
                    rarity_str,
                    foil_str,
                    1 + (idx_c % 3),
                    is_ev,
                    f"chibi_{cid}",
                    now_utc,
                ),
            )

        # Populate Table 11: gacha_pack_pulls_history (6 historical pack pulls >= 5 rows)
        seed_pulls = [
            ("pull_seed_01", "SET_01", "CRADLE_STANDARD_PACK", 1, 1, 0, cards[0:8]),
            ("pull_seed_02", "SET_02", "KUBRART_ECLIPSE_PACK", 2, 1, 0, cards[60:68]),
            ("pull_seed_03", "SET_03", "SOVEREIGN_AGENT_PACK", 0, 1, 1, cards[80:88]),
            ("pull_seed_04", "SET_04", "STUDIO_PXG_ODYSSEY_PACK", 0, 1, 1, cards[117:125]),
            ("pull_seed_05", "SET_07", "EVOLVE_SR_COLLECTOR_PACK", 0, 1, 1, cards[125:133]),
            ("pull_seed_06", "SET_15", "EVOLVE_SR_COLLECTOR_PACK", 0, 1, 1, cards[133:141]),
        ]
        for pull_id, s_code, p_type, pity_after, sr_hit, ur_hit, pack_slice in seed_pulls:
            pack_payload = [
                {
                    "slot": i + 1,
                    "card_id": pc["card_id"],
                    "name": pc["name"],
                    "set_code": pc["set_code"],
                    "faction": pc["faction"],
                    "cost": pc["cost"],
                    "nesw": [pc["rank_n"], pc["rank_e"], pc["rank_s"], pc["rank_w"]],
                }
                for i, pc in enumerate(pack_slice)
            ]
            cur.execute(
                """
                INSERT INTO gacha_pack_pulls_history (
                    pull_id, player_id, set_code, pack_type, pity_counter_after,
                    guaranteed_sr_hit, ur_or_evolve_hit, pulled_cards_json, pulled_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    pull_id,
                    "SovereignArchitect",
                    s_code,
                    p_type,
                    pity_after,
                    sr_hit,
                    ur_hit,
                    json.dumps(pack_payload),
                    now_utc,
                ),
            )

        # Populate Table 12: ranked_elo_match_history (12 ranked match records >= 10 rows)
        seed_matches = [
            ("match_seed_01", "GrandDirectorAI", 1500, 1518, 18, "player", 5, 1),
            ("match_seed_02", "KubrartEclipseArchon", 1518, 1536, 18, "player", 6, 1),
            ("match_seed_03", "AlphaZeroPUCT_Boss", 1536, 1522, -14, "opponent", 7, 0),
            ("match_seed_04", "ValkyriaStrikerAI", 1522, 1541, 19, "player", 5, 1),
            ("match_seed_05", "ChronosLatticeArbiter", 1541, 1560, 19, "player", 5, 1),
            ("match_seed_06", "SeinenSumiRoninAI", 1560, 1578, 18, "player", 6, 1),
            ("match_seed_07", "SovranMechanicaPrime", 1578, 1597, 19, "player", 5, 1),
            ("match_seed_08", "AlphaZeroPUCT_Boss", 1597, 1618, 21, "player", 6, 1),
            ("match_seed_09", "AbyssalBloodMonolith", 1618, 1605, -13, "opponent", 7, 1),
            ("match_seed_10", "StudioPxGOdysseyBoss", 1605, 1626, 21, "player", 5, 1),
            ("match_seed_11", "OmegaTriadConvergence", 1626, 1648, 22, "player", 5, 1),
            ("match_seed_12", "GrandDirectorAI", 1648, 1668, 20, "player", 5, 1),
        ]
        for m_id, opp_id, e_before, e_after, e_delta, win_who, turns_p, ev_trig in seed_matches:
            b_hash = hashlib.sha256(f"{m_id}:{opp_id}:{e_after}".encode("utf-8")).hexdigest()[:16]
            cur.execute(
                """
                INSERT INTO ranked_elo_match_history (
                    match_id, season_id, player_id, opponent_id,
                    player_elo_before, player_elo_after, elo_delta,
                    winner, turns_played, evolve_triggered, board_hash_hex, played_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    m_id,
                    "SEASON_01_CRADLE_ECLIPSE",
                    "SovereignArchitect",
                    opp_id,
                    e_before,
                    e_after,
                    e_delta,
                    win_who,
                    turns_p,
                    ev_trig,
                    b_hash,
                    now_utc,
                ),
            )

        conn.commit()
        # Checkpoint WAL into main sqlite3 file so single-file SHA-256 is self-contained & deterministic
        cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        cur.execute("PRAGMA journal_mode=DELETE;")
        conn.commit()
        cur.close()
    finally:
        conn.close()

    local_sha256 = compute_sha256(LOCAL_SQLITE_PATH)
    local_bytes = LOCAL_SQLITE_PATH.stat().st_size

    return {
        "local_sqlite_path": str(LOCAL_SQLITE_PATH),
        "local_sha256": local_sha256,
        "local_byte_size": local_bytes,
    }


def sync_and_verify_on_sbx00(local_db_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provisions `/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/{db,models_lora,manifests}` on `SBX00`,
    syncs the SQLite database, `.safetensors` models, and manifests over SSH, and runs remote
    cryptographic + SQLite row-count verification on `SBX00`.
    """
    # 1. Create directories strictly inside /DATA/SovereignVault/CARDFRONT_SAGA_VAULT
    mkdir_cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=10",
        SBX00_SSH_ALIAS,
        (
            f"sudo -n mkdir -p {SBX00_VAULT_ROOT}/db {SBX00_VAULT_ROOT}/models_lora {SBX00_VAULT_ROOT}/manifests && "
            f"sudo -n chown -R pxadmin:pxadmin {SBX00_VAULT_ROOT}"
        ),
    ]
    subprocess.run(mkdir_cmd, check=True, capture_output=True, text=True)

    # 2. Sync SQLite database to SBX00:/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/db/
    remote_db_path = f"{SBX00_VAULT_ROOT}/db/{LOCAL_SQLITE_PATH.name}"
    subprocess.run(
        ["scp", "-q", str(LOCAL_SQLITE_PATH), f"{SBX00_SSH_ALIAS}:{remote_db_path}"],
        check=True,
    )

    # 3. Sync Models/LoRA/*.safetensors and safetensors_manifest.json
    lora_files = [str(p) for p in sorted(LORA_DIR.glob("*.safetensors"))]
    if (LORA_DIR / "safetensors_manifest.json").is_file():
        lora_files.append(str(LORA_DIR / "safetensors_manifest.json"))
    subprocess.run(
        ["scp", "-q", *lora_files, f"{SBX00_SSH_ALIAS}:{SBX00_VAULT_ROOT}/models_lora/"],
        check=True,
    )

    # 4. Sync key JSON manifests
    manifest_names = [
        "set1_full_60_cards_and_15_campaign_stages.json",
        "set2_kubrart_manga_expansion_manifest.json",
        "studio_pxg_aaa_assets_and_sakuga_manifest.json",
        "genie4_world_model_inference_report.json",
        "anime_manga_illustration_models_manifest.json",
    ]
    manifest_paths = [str(DATASETS_DIR / m) for m in manifest_names if (DATASETS_DIR / m).is_file()]
    if manifest_paths:
        subprocess.run(
            ["scp", "-q", *manifest_paths, f"{SBX00_SSH_ALIAS}:{SBX00_VAULT_ROOT}/manifests/"],
            check=True,
        )

    # 5. Execute remote verification on SBX00 (`ls -lh`, `sha256sum`, and `python3 -c "import sqlite3; ..."`)
    remote_py = (
        "import json, sqlite3; "
        f"conn = sqlite3.connect('{remote_db_path}'); "
        "cur = conn.cursor(); "
        "tables = ['franchise_eras','expansion_sets_10yr','canonical_cards_catalog',"
        "'lora_model_zoo','sakuga_cutin_registry','gpu_cluster_nodes',"
        "'franchise_economy_and_ltv_projections','sbx00_vault_sync_audit',"
        "'evolve_mech_wing_pairs','player_collection_ledger',"
        "'gacha_pack_pulls_history','ranked_elo_match_history']; "
        "counts = {t: cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in tables}; "
        "planned_cards = cur.execute('SELECT SUM(planned_card_count) FROM expansion_sets_10yr').fetchone()[0]; "
        "print(json.dumps({'table_counts': counts, 'total_planned_10yr_cards': planned_cards}))"
    )
    verify_cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=10",
        SBX00_SSH_ALIAS,
        (
            f"ls -lh {remote_db_path} && "
            f"sha256sum {remote_db_path} && "
            f"python3 -c \"{remote_py}\""
        ),
    ]
    verify_res = subprocess.run(verify_cmd, check=True, capture_output=True, text=True)
    out_lines = [ln.strip() for ln in verify_res.stdout.strip().splitlines() if ln.strip()]

    ls_line = out_lines[0] if len(out_lines) >= 1 else ""
    sha_line = out_lines[1] if len(out_lines) >= 2 else ""
    json_line = out_lines[-1] if len(out_lines) >= 3 else "{}"

    remote_sha256 = sha_line.split()[0] if sha_line else ""
    remote_query_data = json.loads(json_line)
    table_counts = remote_query_data.get("table_counts", {})

    sha_match = remote_sha256 == local_db_info["local_sha256"]
    if not sha_match:
        raise RuntimeError(
            f"SHA-256 mismatch between local ({local_db_info['local_sha256']}) and SBX00 ({remote_sha256})!"
        )

    assert table_counts.get("franchise_eras") == 3, "Expected franchise_eras == 3"
    assert table_counts.get("expansion_sets_10yr") == 20, "Expected expansion_sets_10yr == 20"
    assert table_counts.get("canonical_cards_catalog") == 141, "Expected canonical_cards_catalog == 141"
    assert table_counts.get("evolve_mech_wing_pairs") == 5, "Expected evolve_mech_wing_pairs == 5"
    assert table_counts.get("player_collection_ledger", 0) >= 45, "Expected player_collection_ledger >= 45"
    assert table_counts.get("gacha_pack_pulls_history", 0) >= 5, "Expected gacha_pack_pulls_history >= 5"
    assert table_counts.get("ranked_elo_match_history", 0) >= 10, "Expected ranked_elo_match_history >= 10"
    assert table_counts.get("gpu_cluster_nodes") == 4, "Expected gpu_cluster_nodes == 4"

    return {
        "remote_db_path": remote_db_path,
        "remote_ls_lh": ls_line,
        "remote_sha256": remote_sha256,
        "local_remote_sha256_match": sha_match,
        "remote_table_counts": table_counts,
        "verified_table_count": len(table_counts),
        "total_planned_10yr_cards": remote_query_data.get("total_planned_10yr_cards", 2400),
        "synced_lora_files_count": len(lora_files),
        "synced_manifest_files_count": len(manifest_paths),
    }


def main() -> None:
    t0 = time.perf_counter()
    storage_guard = verify_sbx00_storage_guard()
    cards = collect_131_canonical_cards()
    lora_models = collect_lora_models()
    sakuga_strips = collect_sakuga_strips()

    local_db_info = build_local_sqlite_database(cards, lora_models, sakuga_strips)
    remote_sync_info = sync_and_verify_on_sbx00(local_db_info)
    elapsed_s = round(time.perf_counter() - t0, 3)

    report = {
        "status": "PASS_SBX00_SOVEREIGN_VAULT_SYNCED",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sbx00_host": SBX00_HOST_IP,
        "sbx00_ssh_alias": SBX00_SSH_ALIAS,
        "sbx00_ssh_port": SBX00_SSH_PORT,
        "sbx00_vault_path": SBX00_VAULT_ROOT,
        "local_sqlite_path": local_db_info["local_sqlite_path"],
        "remote_sqlite_path": remote_sync_info["remote_db_path"],
        "local_sha256": local_db_info["local_sha256"],
        "remote_sha256": remote_sync_info["remote_sha256"],
        "local_remote_sha256_match": remote_sync_info["local_remote_sha256_match"],
        "sqlite_byte_size": local_db_info["local_byte_size"],
        "sbx00_storage_guard": storage_guard,
        "table_row_counts": remote_sync_info["remote_table_counts"],
        "canonical_cards_catalog": remote_sync_info["remote_table_counts"].get("canonical_cards_catalog", 141),
        "evolve_mech_wing_pairs": remote_sync_info["remote_table_counts"].get("evolve_mech_wing_pairs", 5),
        "total_planned_10yr_cards": remote_sync_info["total_planned_10yr_cards"],
        "canonical_cards_breakdown": {
            "set1_cradle_of_echoes": 60,
            "set2_kubrart_manga_vanguard": 20,
            "set3_sovereign_agent_deck": 37,
            "set4_studio_pxg_aaa_strikers": 8,
            "saga_10yr_era_heralds": 6,
            "evolve_mech_wing_maidens": 10,
            "total_canonical_playable_cards": len(cards),
        },
        "remote_verification": remote_sync_info,
        "provisioning_wall_time_s": elapsed_s,
    }

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
