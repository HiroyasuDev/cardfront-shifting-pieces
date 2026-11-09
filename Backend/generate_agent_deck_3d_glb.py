#!/usr/bin/env python3
"""
generate_agent_deck_3d_glb.py
=============================
Generates 6 Watertight (V=4,034, E=12,096, F=8,064, V-E+F=2, 0 boundary edges),
4-Bone Skeletal-Rigged (Bone_0_Root, Bone_1_SpineCore, Bone_2_ChestAura, Bone_3_HeadCrest),
Keyframe-Animated (Idle_Breathing, Tactical_Strike), UV-Baked PBR glTF 2.0 `.glb`
and `.q3gs` Quantized 3D Gaussian Splat tabletop miniatures for the Antigravity
Agent Command Deck in `CARDFRONT: Cradle of Echoes`.

Outputs to:
- `/Users/frederickamina/Documents/Projects/synapse/unity-tcg-engine/Assets/Resources/Models3D/AgentDeck/`
- `/Users/frederickamina/Documents/Projects/synapse/unity-tcg-engine/GeneratedArt/AgentDeck/Models3D/`
- `/Users/frederickamina/Documents/Projects/synapse/unity-tcg-engine/GeneratedArt/AgentDeck/agent_deck_3d_glb_manifest.json`
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from upgrade_cardcraft_rigged_pbr_glb import (  # noqa: E402
    WORKSPACE_DIR,
    build_rigged_pbr_glb_and_q3gs,
    verify_glb_watertight_and_rigged,
)

PROJECT_ROOT = BACKEND_DIR.parent
UNITY_AGENT_MODELS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "Models3D" / "AgentDeck"
GENART_AGENT_MODELS_DIR = PROJECT_ROOT / "GeneratedArt" / "AgentDeck" / "Models3D"
MANIFEST_OUT_PATH = PROJECT_ROOT / "GeneratedArt" / "AgentDeck" / "agent_deck_3d_glb_manifest.json"

AGENT_DECK_3D_RELIC_SPECS: List[Dict[str, Any]] = [
    {
        "card_id": "agent_01_grand_arcanist_designer",
        "linked_card_id": "plugin_01_tcg_creative_designer",
        "category": "mythic_sovereign_plugin_relic",
        "character_name": "Grand Arcanist of CardCraft (Atelier Turnaround Relic)",
        "age": 0,
        "role": "Master TCG Creative Game Designer & 3x3 Grid Architect",
        "visual_signature": "Gilded parchment-gold trenchcoat, glowing cyan nib quill stylus, isometric 3x3 grid pedestal, floating tarot prism",
        "palette_id": "Palette_Atelier_Violet_Gold",
        "primary_hex": "#A855F7",
        "accent_hex": "#FFB800",
        "stats": {"up": 8, "right": 7, "down": 6, "left": 7},
        "ability_id": "AtelierPrismBriefCompile",
        "ability_effect": "DEPLOY: Compiles 8-block morphological briefs, 600x800 portraits, & SVG telegraphs.",
        "aligned_persona": "1. The Creator (Quill / Prism — Aether / Mastery)",
        "base_color_rgba": [0.66, 0.33, 0.97, 1.0],
        "emissive_rgb": [0.45, 0.22, 0.68],
        "metallic": 0.82,
        "roughness": 0.22,
        "scale_xyz": (1.02, 1.14, 1.02),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_turnaround_sheet.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_tcg_designer.png",
    },
    {
        "card_id": "agent_02_chronos_swarm_commander",
        "linked_card_id": "plugin_02_parallel_swarm_orchestrator",
        "category": "mythic_sovereign_plugin_relic",
        "character_name": "Chronos Swarm Commander (Tri-Worktree Mecha Tactician)",
        "age": 0,
        "role": "Master Parallel Subagent & Worktree Swarm Orchestrator",
        "visual_signature": "Beveled cyber-magicite armor, three glowing hexagonal worktree portals (Share / Branch / Inherit), golden astrolabe",
        "palette_id": "Palette_Swarm_Amber_Cyan",
        "primary_hex": "#F97316",
        "accent_hex": "#00E5FF",
        "stats": {"up": 7, "right": 8, "down": 6, "left": 7},
        "ability_id": "TriWorktreeSwarmFanOut",
        "ability_effect": "DEPLOY: Summons parallel subagents in isolated git worktrees with shared memory.",
        "aligned_persona": "8. The Strategist (Tri-Portal / Command — Fire / Velocity)",
        "base_color_rgba": [0.98, 0.45, 0.09, 1.0],
        "emissive_rgb": [0.55, 0.25, 0.05],
        "metallic": 0.86,
        "roughness": 0.20,
        "scale_xyz": (1.06, 1.12, 1.04),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_swarm_commander.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_swarm_commander.png",
    },
    {
        "card_id": "agent_03_hallowed_arbiter_jev",
        "linked_card_id": "plugin_03_jev_system_one",
        "category": "mythic_sovereign_plugin_relic",
        "character_name": "Hallowed Arbiter of System One (Jev Law-Seal Sentinel)",
        "age": 0,
        "role": "Calibrated Probability & Pre-Completion Verification Gate",
        "visual_signature": "Gilded Ivalice Law-Judge armor, balanced twin scales of calibrated probability, octagonal jade-teal verification halo",
        "palette_id": "Palette_Jev_Jade_LawGold",
        "primary_hex": "#2EE6D3",
        "accent_hex": "#FFB800",
        "stats": {"up": 8, "right": 6, "down": 8, "left": 6},
        "ability_id": "OctagonalLawSealGate",
        "ability_effect": "GUARD: Screens untrusted input (jev_screen) & gates diffs with calibrated probabilities.",
        "aligned_persona": "11. The Judge (Scales / Verdict — Law / Truth)",
        "base_color_rgba": [0.18, 0.90, 0.83, 1.0],
        "emissive_rgb": [0.10, 0.52, 0.48],
        "metallic": 0.88,
        "roughness": 0.18,
        "scale_xyz": (1.00, 1.16, 1.00),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_jev_arbiter.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_jev_arbiter.png",
    },
    {
        "card_id": "agent_04_a18_pro_metal_sovereign",
        "linked_card_id": "plugin_04_mlx_apple_silicon",
        "category": "mythic_sovereign_plugin_relic",
        "character_name": "A18 Pro Metal Forge Sovereign (Unified-Memory Dragon)",
        "age": 0,
        "role": "Local Apple Silicon Metal GPU & JevMLX Single-Pass Engine",
        "visual_signature": "Crystalline silicon-wafer dragon-construct forging a 4-bit quantized logit diamond over an 8GB unified-memory anvil",
        "palette_id": "Palette_MLX_Cyan_Indigo",
        "primary_hex": "#00E5FF",
        "accent_hex": "#6366F1",
        "stats": {"up": 7, "right": 7, "down": 7, "left": 7},
        "ability_id": "SinglePassLogitRefraction",
        "ability_effect": "OVERCHARGE: Executes zero-latency Choice, Score & Noul decisions on Metal GPU.",
        "aligned_persona": "14. The Forgemaster (Silicon Die / Tensor — Lightning / Precision)",
        "base_color_rgba": [0.0, 0.90, 1.0, 1.0],
        "emissive_rgb": [0.05, 0.48, 0.65],
        "metallic": 0.92,
        "roughness": 0.16,
        "scale_xyz": (1.04, 1.10, 1.04),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_mlx_forge.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_mlx_forge.png",
    },
    {
        "card_id": "agent_05_router_spellbook_compass",
        "linked_card_id": "skill_01_master_router",
        "category": "arcane_skill_totem_relic",
        "character_name": "Compass of the 93 Realms & Tool-Calling Grimoire",
        "age": 0,
        "role": "4-Slot Progressive-Disclosure Skill Router & Spellbook",
        "visual_signature": "Leather-bound arcane grimoire open on a brass lectern with a 4-ring celestial compass rose (Engine / Discipline / Genre / Workflow)",
        "palette_id": "Palette_Router_Gold_Cyan",
        "primary_hex": "#FFB800",
        "accent_hex": "#00E5FF",
        "stats": {"up": 7, "right": 6, "down": 6, "left": 6},
        "ability_id": "ProgressiveDisclosureRoute",
        "ability_effect": "ROUTE: Fingerprints Engine -> Discipline -> Genre -> Workflow with zero bulk-load bloat.",
        "aligned_persona": "5. The Navigator (Compass / Grimoire — Air / Foresight)",
        "base_color_rgba": [1.0, 0.72, 0.0, 1.0],
        "emissive_rgb": [0.55, 0.38, 0.05],
        "metallic": 0.84,
        "roughness": 0.24,
        "scale_xyz": (1.00, 1.05, 1.00),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_spellbook_compass.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_spellbook_compass.png",
    },
    {
        "card_id": "agent_06_celestial_mcp_astrolabe",
        "linked_card_id": "mcp_06_knowledge_graph_mem",
        "category": "mcp_conduit_totem_relic",
        "character_name": "Celestial MCP Nexus Astrolabe & Memory Constellation",
        "age": 0,
        "role": "9-Server MCP Conduit & Knowledge Graph Constellation Core",
        "visual_signature": "Nine-tailed constellation kitsune & brass armillary sphere linking 9 glowing icosahedral MCP server conduits",
        "palette_id": "Palette_MCP_Violet_Jade",
        "primary_hex": "#2EE6D3",
        "accent_hex": "#A855F7",
        "stats": {"up": 6, "right": 7, "down": 6, "left": 6},
        "ability_id": "NineConduitMemorySync",
        "ability_effect": "CONDUIT: Synchronizes 9 MCP servers (52+ tools) with the persistent Knowledge Graph.",
        "aligned_persona": "19. The Oracle (Astrolabe / Fox — Aether / Memory)",
        "base_color_rgba": [0.54, 0.36, 0.96, 1.0],
        "emissive_rgb": [0.28, 0.18, 0.58],
        "metallic": 0.85,
        "roughness": 0.20,
        "scale_xyz": (1.03, 1.08, 1.03),
        "turnaround_concept_art": "GeneratedArt/AgentDeck/KeyArt/hero_hi3d_relic_sculptor.png",
        "key_art_portrait": "GeneratedArt/AgentDeck/KeyArt/hero_memory_graph.png",
    },
]


def main() -> None:
    t0 = time.perf_counter()
    UNITY_AGENT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    GENART_AGENT_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    fallback_glb = WORKSPACE_DIR / "hi3d_sovereign_cyber_judge_zero.glb"
    if not fallback_glb.exists():
        fallback_glb = WORKSPACE_DIR / "sp_02_aiko_nakamura_echo.glb"
    template_glb_bytes = fallback_glb.read_bytes()

    fallback_q3gs = WORKSPACE_DIR / "hi3d_sovereign_cyber_judge_zero.q3gs"
    if not fallback_q3gs.exists():
        fallback_q3gs = WORKSPACE_DIR / "sp_02_aiko_nakamura_echo.q3gs"
    template_q3gs_bytes = fallback_q3gs.read_bytes()

    records: List[Dict[str, Any]] = []
    for spec in AGENT_DECK_3D_RELIC_SPECS:
        cid = spec["card_id"]
        rigged_glb, custom_q3gs, metrics = build_rigged_pbr_glb_and_q3gs(
            template_glb_bytes, template_q3gs_bytes, spec
        )
        # Double-verify with verify_glb_watertight_and_rigged
        verified = verify_glb_watertight_and_rigged(rigged_glb)
        assert verified["watertight_euler_2"] is True, f"{cid} failed Euler V-E+F=2 check!"
        assert verified["has_skeletal_rig"] is True, f"{cid} missing skeletal rig!"

        unity_glb = UNITY_AGENT_MODELS_DIR / f"{cid}.glb"
        unity_q3gs = UNITY_AGENT_MODELS_DIR / f"{cid}.q3gs"
        genart_glb = GENART_AGENT_MODELS_DIR / f"{cid}.glb"
        genart_q3gs = GENART_AGENT_MODELS_DIR / f"{cid}.q3gs"

        for p in (unity_glb, genart_glb):
            p.write_bytes(rigged_glb)
        for p in (unity_q3gs, genart_q3gs):
            p.write_bytes(custom_q3gs)

        records.append({
            "relic_id": cid,
            "linked_card_id": spec["linked_card_id"],
            "character_name": spec["character_name"],
            "role": spec["role"],
            "primary_hex": spec["primary_hex"],
            "accent_hex": spec["accent_hex"],
            "directional_stats": spec["stats"],
            "ability_id": spec["ability_id"],
            "ability_effect": spec["ability_effect"],
            "turnaround_concept_art": spec["turnaround_concept_art"],
            "key_art_portrait": spec["key_art_portrait"],
            "unity_glb_path": str(unity_glb.relative_to(PROJECT_ROOT)),
            "unity_q3gs_path": str(unity_q3gs.relative_to(PROJECT_ROOT)),
            "genart_glb_path": str(genart_glb.relative_to(PROJECT_ROOT)),
            "genart_q3gs_path": str(genart_q3gs.relative_to(PROJECT_ROOT)),
            "glb_bytes": len(rigged_glb),
            "q3gs_bytes": len(custom_q3gs),
            "glb_sha256": hashlib.sha256(rigged_glb).hexdigest(),
            "q3gs_sha256": hashlib.sha256(custom_q3gs).hexdigest(),
            "watertight_euler_2": verified["watertight_euler_2"],
            "has_skeletal_rig": verified["has_skeletal_rig"],
            "has_pbr_normal_roughness_maps": verified["has_pbr_normal_roughness_maps"],
            "animations_count": verified["animations_count"],
            "mesh_metrics": verified,
        })

    manifest = {
        "schema_version": "2026.11.agent-deck-3d-glb.v1",
        "status": "VERIFIED_WATERTIGHT_EULER_2",
        "total_relics": len(records),
        "watertight_euler_2": all(r["watertight_euler_2"] for r in records),
        "has_skeletal_rig": all(r["has_skeletal_rig"] for r in records),
        "has_pbr_normal_roughness_maps": all(r["has_pbr_normal_roughness_maps"] for r in records),
        "animations_count": 2,
        "topology": {
            "vertices": 4034,
            "edges": 12096,
            "faces": 8064,
            "euler_characteristic_v_minus_e_plus_f": 2,
            "boundary_edges": 0,
            "skeletal_joints": ["Bone_0_Root", "Bone_1_SpineCore", "Bone_2_ChestAura", "Bone_3_HeadCrest"],
            "animations": ["Idle_Breathing", "Tactical_Strike"],
        },
        "relics": records,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
    }
    MANIFEST_OUT_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "total_relics": manifest["total_relics"],
        "watertight_euler_2": manifest["watertight_euler_2"],
        "manifest_path": str(MANIFEST_OUT_PATH),
        "elapsed_ms": manifest["elapsed_ms"],
    }, indent=2))


if __name__ == "__main__":
    main()
