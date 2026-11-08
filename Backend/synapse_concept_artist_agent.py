#!/usr/bin/env python3
"""
synapse_concept_artist_agent.py — Dedicated Sovereign Concept Artist, Anatomical Sketch,
Background/Landscape Renderer & Game-Design Nuance Compiler Agent
========================================================================================
Integrates with:
  1. Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) for live Anatomical Turnaround Sketch Sheets,
     Orthographic Mecha Blueprints, Value Studies, and Multi-Plane Background Landscapes.
  2. 4-Node 120 GB GPU Pool (`v100` 32GB + `m1max` 64GB + `rtx4080` 16GB + `rtx2070` 8GB) for LLM-driven
     Anatomical Construction Specs, 5-Plane Parallax Environment Architecture, and Game-Design Nuance Binding.
  3. V100 TRELLIS 2.0 + Hi3DGen (`http://192.168.86.116:8090/v1/trellis/generate`) for 2D-Concept-to-3D
     Watertight `.glb` / `.q3gs` asset generation.
  4. Continuous Longitudinal Dataset Expansion (`451` total records) & Multi-Epoch V100 QLoRA + Hinton KD Training.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
FORGE_API_URL = "http://192.168.86.116:8090"
SHOWCASE_DIR = BACKEND_DIR.parent / "Assets" / "Resources" / "CardArt" / "StyleShowcase"
CONCEPT_DIR = BACKEND_DIR.parent / "Assets" / "Resources" / "CardArt" / "ConceptStudio"
DATASET_FULL_PATH = BACKEND_DIR.parent / "Datasets" / "longitudinal_9_masters_full_corpus.jsonl"
DATASET_12_PATH = BACKEND_DIR.parent / "Datasets" / "longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl"

ANATOMICAL_RIG_ARCHETYPES: List[Dict[str, Any]] = [
    {
        "rig_id": "rig_01_stylized_tactical_vanguard",
        "title": "6.5-Head Tactical Vanguard Constructive Mannequin (Itō × Hirata Ratio)",
        "head_ratio": 6.5,
        "anatomical_notes": (
            "Loomis cranial sphere with 1/3 facial canon; exaggerated forearm/gauntlet and lower-leg/boot taper (1.35x); "
            "22-degree contrapposto pelvic tilt against shoulder line; clear negative space between weapon shaft and torso silhouette."
        ),
        "animation_telegraph_frames": {"anticipation": 5, "active_strike": 3, "recovery": 9},
    },
    {
        "rig_id": "rig_02_baroque_judge_colossus",
        "title": "8.5-Head Baroque Judge & Heavy Paladin Armor Anatomy (Yoshida × Kamikokuryo Ratio)",
        "head_ratio": 8.5,
        "anatomical_notes": (
            "Bridgman wedged thoracic block encased in layered pauldrons and gorget; solemn vertical plumb line; "
            "sculptural drapery folds radiating from hip girdle; high-contrast crosshatched shadow core under helm visor."
        ),
        "animation_telegraph_frames": {"anticipation": 8, "active_strike": 4, "recovery": 12},
    },
    {
        "rig_id": "rig_03_cyber_reploid_shinobi",
        "title": "7.0-Head Agile Cyber-Reploid & Biometal Striker (Nakayama × Shinkawa Ratio)",
        "head_ratio": 7.0,
        "anatomical_notes": (
            "Triangular torso-to-waist taper; narrow cylindrical waist joint for 360-degree slash rotation; "
            "sharp beveled knee/shoulder armor fins; 45-degree forward dash line-of-action with trailing energy ribbon."
        ),
        "animation_telegraph_frames": {"anticipation": 3, "active_strike": 2, "recovery": 6},
    },
    {
        "rig_id": "rig_04_orbital_tactical_mecha",
        "title": "9.0-Head Bipedal Orbital Frame & Mecha-Knight Rig (Shinkawa × Terada-Suzuki Ratio)",
        "head_ratio": 9.0,
        "anatomical_notes": (
            "Digitigrade reverse-jointed hydraulic ankles; cantilevered cockpit sternum; exposed carbon-fiber tendon bundles; "
            "calligraphic sumi-e ink weight heaviest at load-bearing joints."
        ),
        "animation_telegraph_frames": {"anticipation": 6, "active_strike": 3, "recovery": 10},
    },
    {
        "rig_id": "rig_05_occult_astral_caster",
        "title": "7.5-Head Levitating Astral & Cyber-Occult Sovereign (Kaneko × Minaba Ratio)",
        "head_ratio": 7.5,
        "anatomical_notes": (
            "S-curve weightless spine suspension; porcelain mannequin clavicles and elongated fingers; "
            "concentric geometric sigil halo framing head and shoulders for instant 0.25x card-scale silhouette recognition."
        ),
        "animation_telegraph_frames": {"anticipation": 6, "active_strike": 4, "recovery": 8},
    },
]

BACKGROUND_LANDSCAPE_ARCHITECTURES: List[Dict[str, Any]] = [
    {
        "landscape_id": "bg_01_ivalice_terraced_citadel",
        "title": "Multi-Elevation Ivalice Jagd Citadel & Terraced Stone Diorama (Minagawa × Yoshida)",
        "parallax_planes": {
            "plane_1_foreground_frame": "Weathered stone archways and battle-standard banners in 20% value dark silhouette",
            "plane_2_playable_3x3_grid": "Sun-drenched limestone 3x3 / isometric stepped tiles with <16% internal albedo noise and 2.4x cliff bevel contrast",
            "plane_3_midground_architecture": "Buttressed guild cathedral, waterwheel aqueduct, and glowing Law-Crystal obelisk",
            "plane_4_far_vista": "Mist-shrouded terraced mountain range and floating airship anchorage",
            "plane_5_zenith_sky": "Painterly warm ochre-and-cerulean cumulus skybox with directional 38-degree key sunlight",
        },
        "gameplay_terrain_modifiers": {"high_ground_dmg_bonus_pct": 15, "stone_cover_ranged_mitigation_pct": 25, "law_crystal_mana_regen": 1},
    },
    {
        "landscape_id": "bg_02_neo_arcadia_cyber_cathedral",
        "title": "Neo-Arcadia Cyber-Sanctum & Reploid Resistance Ruins (Inti Creates × Nakayama)",
        "parallax_planes": {
            "plane_1_foreground_frame": "Severed high-tension cyber-conduits and beveled dark-steel girders",
            "plane_2_playable_3x3_grid": "Hex-etched obsidian tactical grid with glowing cyan Cyber-Elf circuit borders",
            "plane_3_midground_architecture": "Towering Neo-Arcadia monolithic sanctuary spire with crimson energy core",
            "plane_4_far_vista": "Multi-layered subterranean megastructure skyline",
            "plane_5_zenith_sky": "High-contrast indigo cyber-aurora and volumetric data-rain shafts",
        },
        "gameplay_terrain_modifiers": {"cyber_conduit_haste_bonus_pct": 20, "energy_shield_tile_armor": 2, "emp_hazard_zone_drain": -1},
    },
    {
        "landscape_id": "bg_03_mana_world_tree_canopy",
        "title": "Sacred Mana World-Tree Sanctuary & Bioluminescent Root Arena (Isono × Ishii × Minaba)",
        "parallax_planes": {
            "plane_1_foreground_frame": "framing emerald ferns, hanging moss, and floating golden spore motes",
            "plane_2_playable_3x3_grid": "Interlocking ancient World-Tree root plateaus and shallow crystalline water tiles",
            "plane_3_midground_architecture": "Colossal gnarled Mana Tree trunk with carved elemental spirit shrines",
            "plane_4_far_vista": "Cascading emerald waterfalls and sunlit cloud-forest canopy",
            "plane_5_zenith_sky": "Dappled cathedral sunbeams piercing multi-layered botanical foliage",
        },
        "gameplay_terrain_modifiers": {"mana_spring_heal_per_turn": 2, "root_canopy_stealth_evasion_pct": 20, "elemental_resonance_boost_pct": 15},
    },
    {
        "landscape_id": "bg_04_bhujerba_skystone_airship_dock",
        "title": "Floating Skystone Airship Dock & Cloudsea Observatory (Kamikokuryo × Minaba)",
        "parallax_planes": {
            "plane_1_foreground_frame": "Ornate brass astrolabe rings and mooring chains",
            "plane_2_playable_3x3_grid": "Polished travertine marble deck inlaid with glowing blue magicite skystone veins",
            "plane_3_midground_architecture": "Dreadnought airship hull ribs, twin mana-turbines, and Mediterranean limestone colonnades",
            "plane_4_far_vista": "Suspended sky-islands drifting above an infinite golden-hour cloudsea",
            "plane_5_zenith_sky": "High-altitude stratospheric azure gradient with radiant atmospheric bloom",
        },
        "gameplay_terrain_modifiers": {"skystone_levitation_move_bonus": 1, "tailwind_initiative_boost": 2, "arc_turbine_overcharge_dmg": 3},
    },
    {
        "landscape_id": "bg_05_dual_strike_command_front",
        "title": "Tactical Command Theater & Mechanized Choke-Point Arena (Hirata × Shinkawa)",
        "parallax_planes": {
            "plane_1_foreground_frame": "Holographic tactical HUD rangefinders and reinforced bunker embrasure",
            "plane_2_playable_3x3_grid": "High-readability modular steel bridge, urban capture nodes, and fortified bunker tiles",
            "plane_3_midground_architecture": "Orange Star vs Black Hole command radar array and orbital lift gantry",
            "plane_4_far_vista": "Contested coastal strait with naval carrier group silhouette",
            "plane_5_zenith_sky": "Crisp cel-shaded strategic sky with contrail vectors",
        },
        "gameplay_terrain_modifiers": {"bunker_defense_stars": 4, "capture_node_vp_per_turn": 1, "radar_sight_range_bonus": 2},
    },
]

GAME_DESIGN_NUANCE_RULES: List[Dict[str, Any]] = [
    {
        "nuance_id": "gd_01_silhouette_scale_invariance",
        "principle": "3-Scale Silhouette Readability Invariance (100% Full Art -> 40% Hand Card -> 15% 3x3 Board Token)",
        "specification": (
            "Every unit and card illustration must pass 3-scale binary threshold legibility: primary weapon/class icon "
            "must occupy >=18% of convex hull perimeter, with >=2.2:1 luminance contrast between character focal point and background plane."
        ),
    },
    {
        "nuance_id": "gd_02_isometric_tile_albedo_discipline",
        "principle": "Playable Floor Low-Frequency Albedo Discipline vs. High-Frequency Perimeter Framing",
        "specification": (
            "Walkable/playable 3x3 and isometric tiles must restrict local luminance variance to <=16% so unit sprites/cards "
            "never visually camouflage, while non-playable perimeter architecture (Planes 1, 3, 4) carries high-frequency painterly detail."
        ),
    },
    {
        "nuance_id": "gd_03_combat_frame_telegraph_harmony",
        "principle": "Anatomical Line-of-Action to Combat Frame-Data Coupling",
        "specification": (
            "Fast rushdown/assassin units (2-3f active strike) use 40-50 degree acute diagonal lines-of-action and high bevel sharpness (>=0.88); "
            "heavy Judge/Tank vanguards (8f anticipation) use vertical/pyramidal stability axes and heavy ink outline weights (>=1.40)."
        ),
    },
    {
        "nuance_id": "gd_04_faction_chromatic_identity",
        "principle": "Gamut-Masked Faction Chromatic Coding & Shader Grading",
        "specification": (
            "Each faction locks a primary 60% dominant hue, 30% structural neutral (sepia parchment or obsidian steel), "
            "and 10% high-bloom emissive accent (e.g., Cyber-Elf Cyan, Magicite Blue, Law-Judge Gold, Mana Emerald)."
        ),
    },
    {
        "nuance_id": "gd_05_3x3_positional_adjacency_synergy",
        "principle": "3x3 Tactical Grid Positional Adjacency & Elevation Synergy",
        "specification": (
            "Front-row tiles grant +20% melee vanguard threat and shield rear tiles; center high-ground tile grants +15% omni-directional range/aura; "
            "corner sanctuary tiles provide +25% spell/magicite channeling efficiency."
        ),
    },
]

CONCEPT_STUDIO_SHOWCASE_PROMPTS: List[Dict[str, Any]] = [
    {
        "concept_id": "concept_01_anatomical_gesture_sheet",
        "filename": "concept_01_anatomical_gesture_sheet.png",
        "width": 1024,
        "height": 768,
        "positive": (
            "masterpiece, best quality, official game studio character concept art turnaround and constructive anatomical sketch sheet "
            "in the style of Ryoma Ito (Final Fantasy Tactics Advance), Akihiko Yoshida (FFT), and George Bridgman, "
            "toned warm parchment sketchbook paper, front view, 3/4 dynamic action pose, and rear silhouette study, "
            "visible constructive anatomy guidelines, cranial proportions, contrapposto line of action, red and sepia ink callout annotations, "
            "white gouache highlights, tactical paladin-rogue costume layering"
        ),
        "negative": "photorealistic 3d render, neon clutter, blurry, deformed limbs, lowres, watermark",
    },
    {
        "concept_id": "concept_02_mecha_orthographic_blueprint",
        "filename": "concept_02_mecha_orthographic_blueprint.png",
        "width": 1024,
        "height": 768,
        "positive": (
            "masterpiece, best quality, official mecha and cyber-armor concept art sheet in the signature style of Toru Nakayama "
            "(Mega Man Zero / Rockman Zero) and Yoji Shinkawa (Zone of the Enders and Metal Gear Solid), "
            "orthographic front and side armor breakdown, sharp beveled triangular silhouette plates, expressive sumi-e ink brushwork, "
            "mechanical joint articulation callouts, glowing cyan Cyber-Elf core schematic, studio concept design sheet"
        ),
        "negative": "blurry, messy proportions, muddy colors, lowres, watermark",
    },
    {
        "concept_id": "concept_03_ivalice_sky_citadel_landscape",
        "filename": "concept_03_ivalice_sky_citadel_landscape.png",
        "width": 1024,
        "height": 768,
        "positive": (
            "masterpiece, best quality, sweeping environmental concept art landscape and isometric tactical battlefield vista "
            "in the signature style of Hideo Minaba (FFTA / Granblue Fantasy), Isamu Kamikokuryo (FFXII Ivalice), and Hiroshi Minagawa (FFT), "
            "multi-plane parallax composition, foreground stone archway silhouette, midground terraced isometric limestone citadel and playable 3x3 battle arena, "
            "brass airships moored to glowing blue magicite skystone spires, painterly golden-hour cumulus cloudsea horizon"
        ),
        "negative": "characters blocking view, flat 2d, cramped room, blurry, lowres, watermark",
    },
    {
        "concept_id": "concept_04_mana_neo_arcadia_biome_vista",
        "filename": "concept_04_mana_neo_arcadia_biome_vista.png",
        "width": 1024,
        "height": 768,
        "positive": (
            "masterpiece, best quality, environmental concept art landscape synthesizing Hiroo Isono (Secret of Mana World Tree sanctuary) "
            "and Inti Creates (Mega Man Zero Neo Arcadia cyber-ruins), colossal ancient bioluminescent Mana Tree roots intertwining with "
            "sleek beveled cyber-cathedral monoliths, dappled emerald and cyan sunbeams, clear elevated tactical battle plateaus, atmospheric depth"
        ),
        "negative": "cluttered, flat lighting, muddy brown, blurry, lowres, watermark",
    },
]


def render_concept_sheet_on_rtx4080(spec: Dict[str, Any], steps: int = 16, force: bool = False) -> Dict[str, Any]:
    CONCEPT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = CONCEPT_DIR / spec["filename"]
    if out_file.exists() and not force and out_file.stat().st_size > 50_000:
        return {
            "concept_id": spec["concept_id"],
            "local_file": str(out_file),
            "bytes": out_file.stat().st_size,
            "elapsed_s": 0.0,
            "cached": True,
        }

    seed = (abs(hash(spec["concept_id"])) % (2**31 - 1)) + 707
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 6.8,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": seed,
                "steps": steps,
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "animagineXLV31_v31.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": spec["height"], "width": spec["width"]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": spec["positive"]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": spec["negative"]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"ConceptStudio_{spec['concept_id']}", "images": ["8", 0]}},
    }

    t0 = time.time()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=json.dumps({"prompt": workflow}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]

    for _ in range(120):
        time.sleep(0.5)
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10) as hresp:
            hist = json.loads(hresp.read().decode("utf-8"))
        if prompt_id in hist:
            for node_out in hist[prompt_id].get("outputs", {}).values():
                if "images" in node_out and node_out["images"]:
                    img_info = node_out["images"][0]
                    qs = urllib.parse.urlencode({
                        "filename": img_info["filename"],
                        "subfolder": img_info.get("subfolder", ""),
                        "type": img_info.get("type", "output"),
                    })
                    urllib.request.urlretrieve(f"{COMFYUI_URL}/view?{qs}", out_file)
                    return {
                        "concept_id": spec["concept_id"],
                        "prompt_id": prompt_id,
                        "local_file": str(out_file),
                        "bytes": out_file.stat().st_size,
                        "elapsed_s": round(time.time() - t0, 2),
                        "cached": False,
                    }
    raise TimeoutError(f"Timed out rendering concept sheet {spec['concept_id']}")


def expand_full_library_with_concept_and_gamedesign(render_concept_sheets: bool = True) -> Dict[str, Any]:
    from build_longitudinal_artist_dataset import LONGITUDINAL_MASTERS_SPEC, build_longitudinal_dataset

    base_info = build_longitudinal_dataset(render_showcases=False)
    existing_records: List[Dict[str, Any]] = []
    for line in DATASET_FULL_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing_records.append(json.loads(line))

    new_records: List[Dict[str, Any]] = []

    # 1. 12 Masters x 5 Constructive Anatomical Sketch & Turnaround Archetypes = 60 Records
    for master in LONGITUDINAL_MASTERS_SPEC:
        latest_era = master["eras"][-1]
        for rig in ANATOMICAL_RIG_ARCHETYPES:
            new_records.append({
                "record_type": "concept_artist_anatomical_sketch_spec",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "rig_id": rig["rig_id"],
                "head_ratio": rig["head_ratio"],
                "animation_telegraph_frames": rig["animation_telegraph_frames"],
                "shader_vector": latest_era["shader_vector"],
                "instruction": (
                    f"As the Sovereign Concept Artist Agent, generate a constructive anatomical sketch & turnaround sheet specification "
                    f"for `{rig['title']}` in the style of {master['artist_name']} ({master['kanji']})."
                ),
                "response": json.dumps({
                    "artist_style": master["artist_name"],
                    "rig_archetype": rig["title"],
                    "head_canon_ratio": rig["head_ratio"],
                    "constructive_anatomy": rig["anatomical_notes"],
                    "lineage_morphology": latest_era["morphological_traits"],
                    "frame_data_telegraph": rig["animation_telegraph_frames"],
                    "shader_grading": latest_era["shader_vector"],
                }, ensure_ascii=False),
            })

    # 2. 12 Masters x 5 Multi-Plane Background & Landscape Architectures = 60 Records
    for master in LONGITUDINAL_MASTERS_SPEC:
        latest_era = master["eras"][-1]
        for bg in BACKGROUND_LANDSCAPE_ARCHITECTURES:
            new_records.append({
                "record_type": "concept_artist_background_landscape_spec",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "landscape_id": bg["landscape_id"],
                "parallax_planes": bg["parallax_planes"],
                "gameplay_terrain_modifiers": bg["gameplay_terrain_modifiers"],
                "shader_vector": latest_era["shader_vector"],
                "instruction": (
                    f"As the Sovereign Concept Artist & Environment Agent, design a 5-plane parallax background landscape and playable "
                    f"isometric battlefield for `{bg['title']}` in the style of {master['artist_name']}."
                ),
                "response": json.dumps({
                    "artist_style": master["artist_name"],
                    "landscape_title": bg["title"],
                    "five_plane_parallax_stack": bg["parallax_planes"],
                    "gameplay_terrain_modifiers": bg["gameplay_terrain_modifiers"],
                    "shader_grading": latest_era["shader_vector"],
                }, ensure_ascii=False),
            })

    # 3. 12 Masters x 5 Full Game-Design Nuance & Mechanical Cohesion Rules = 60 Records
    for master in LONGITUDINAL_MASTERS_SPEC:
        latest_era = master["eras"][-1]
        for gd in GAME_DESIGN_NUANCE_RULES:
            new_records.append({
                "record_type": "game_design_nuance_and_visual_binding",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "nuance_id": gd["nuance_id"],
                "principle": gd["principle"],
                "shader_vector": latest_era["shader_vector"],
                "instruction": (
                    f"Bind the game-design nuance `{gd['principle']}` to the visual illustration and shader pipeline of {master['artist_name']}."
                ),
                "response": json.dumps({
                    "artist_style": master["artist_name"],
                    "game_design_principle": gd["principle"],
                    "technical_specification": gd["specification"],
                    "shader_vector": latest_era["shader_vector"],
                }, ensure_ascii=False),
            })

    all_records = existing_records + new_records
    with DATASET_FULL_PATH.open("w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with DATASET_12_PATH.open("w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    rendered_concepts = {}
    if render_concept_sheets:
        for spec in CONCEPT_STUDIO_SHOWCASE_PROMPTS:
            try:
                rendered_concepts[spec["concept_id"]] = render_concept_sheet_on_rtx4080(spec, steps=16)
            except Exception as exc:
                rendered_concepts[spec["concept_id"]] = {"error": str(exc)}

    return {
        "status": "ok",
        "dataset_path": str(DATASET_12_PATH),
        "total_records": len(all_records),
        "breakdown": {
            "era_records": base_info["era_records"],
            "character_card_records": base_info["character_card_records"],
            "environmental_battlefield_records": base_info["environmental_battlefield_records"],
            "anatomical_sketch_records": 60,
            "background_landscape_records": 60,
            "game_design_nuance_records": 60,
        },
        "rendered_concept_studio_sheets": rendered_concepts,
    }


if __name__ == "__main__":
    res = expand_full_library_with_concept_and_gamedesign(render_concept_sheets=True)
    print(json.dumps(res, indent=2, ensure_ascii=False))
