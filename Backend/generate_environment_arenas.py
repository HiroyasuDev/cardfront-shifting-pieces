#!/usr/bin/env python3
"""
Synapse Sovereign TCG Engine — 3x3 Isometric Diorama Board & Terrain Biome Generator.

1. Appends 60 longitudinal environmental & map-design training records (covering Hiroshi Minagawa,
   Hideo Minaba, Isamu Kamikokuryo, Ryo Hirata, and Toru Nakayama / Inti Creates environmental design rules)
   into `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_5_masters_corpus.jsonl`
   (bringing the dataset from 85 to 145 longitudinal records, idempotent across re-runs).
2. Connects to ComfyUI on Node 30 RTX 4080 (`http://192.168.86.30:8188`) and renders 4 high-resolution
   (`1024x768`) 3x3 Tactical Arena Environment Backdrops into
   `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Resources/CardArt/Environments/`:
   - `env_minaba_ivalice_storybook.png`
   - `env_minagawa_yoshida_diorama.png`
   - `env_hirata_advance_wars_hq.png`
   - `env_nakayama_neo_arcadia_mmz.png`
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
DATASET_PATH = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_5_masters_corpus.jsonl")
ENV_OUTPUT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Resources/CardArt/Environments")

ENVIRONMENT_MASTERS_SPEC: List[Dict] = [
    {
        "lineage_id": "hiroshi_minagawa_yoshida_diorama",
        "lead_artists": "Hiroshi Minagawa & Akihiko Yoshida",
        "kanji": "皆川 裕史 & 吉田 明彦",
        "works": ["Tactics Ogre: Let Us Cling Together", "Final Fantasy Tactics", "Vagrant Story", "Final Fantasy XII"],
        "architectural_dna": (
            "3D isometric diorama stone bastions, terraced medieval masonry, deep elevation chiaroscuro, "
            "weathered church and castle ruins, warm parchment sepia-ochre vertex lighting, crisp 45-degree diamond bevels."
        ),
        "shader_grading": {"masonry_relief": 0.95, "storybook_bloom": 0.25, "grid_contrast": 0.82, "neon_conduit": 0.15},
        "eras": [
            ("1995-1997 (Tactics Ogre & PS1 Final Fantasy Tactics Diorama Era)", "Rotatable 3D isometric stone bastions, stepped cliffside elevation, hand-painted masonry textures with warm vertex chiaroscuro."),
            ("2000 (Vagrant Story Leá Monde Architecture Era)", "Carved Romanesque-Gothic cathedrals, subterranean wine cellars, dramatic torchlight shadow wells, acoustic spatial mood."),
            ("2006-2026 (FFXII Ivalice Monumental Stone & Tactics Ogre Reborn Era)", "High-relief limestone citadels, weathered archways, tactical elevation grid readability with museum-grade patina."),
        ],
    },
    {
        "lineage_id": "hideo_minaba_storybook_jagd",
        "lead_artists": "Hideo Minaba & Koji Tsukamoto",
        "kanji": "皆葉 英夫 & 塚本 哲",
        "works": ["Final Fantasy Tactics Advance", "Final Fantasy IX", "Granblue Fantasy"],
        "architectural_dna": (
            "Vibrant storybook map artifacts, jewel-like isometric placement icons, lawless crystal Jagds, "
            "sun-drenched cobblestone plazas, painterly cloudscapes, warm golden-hour bloom."
        ),
        "shader_grading": {"masonry_relief": 0.45, "storybook_bloom": 0.85, "grid_contrast": 0.75, "neon_conduit": 0.35},
        "eras": [
            ("1994-2000 (FFVI & FFIX Theatrical Storybook Architecture)", "Steampunk-meets-fairy-tale cobblestone towns, warm gaslight plazas, illustrated storybook background layers."),
            ("2003 (Final Fantasy Tactics Advance Map Artifact & Jagd System)", "Interactive world-map artifact icons placed onto a grid; vibrant storybook isometric battlefields and lawless crystal Jagds."),
            ("2014-2026 (Granblue Fantasy Sky-Citadel & Designation Era)", "Floating island sanctuaries, gilded ornamental bridges, radiant atmospheric cloud bloom."),
        ],
    },
    {
        "lineage_id": "isamu_kamikokuryo_sky_machina",
        "lead_artists": "Isamu Kamikokuryo",
        "kanji": "上国料 勇",
        "works": ["Final Fantasy Tactics Advance (Backgrounds)", "Final Fantasy XII (Art Director)", "Final Fantasy XIII"],
        "architectural_dna": (
            "Grand Mediterranean-fantasy sky-citadels, iridescent aetherial Leyline crystals, turquoise-and-gold "
            "marble colonnades, sweeping atmospheric perspective and luminous horizon scattering."
        ),
        "shader_grading": {"masonry_relief": 0.70, "storybook_bloom": 0.88, "grid_contrast": 0.80, "neon_conduit": 0.55},
        "eras": [
            ("2003 (FFTA Environmental & Crystal Enclave Concept Era)", "Painterly botanical and crystal formations seamlessly integrated into isometric tactical grids."),
            ("2006 (Final Fantasy XII Rabanastre & Bhujerba Sky-Architecture Era)", "Monumental alabaster stone fused with bronze airship dockyards and glowing magicite conduits."),
            ("2009-2026 (High-Luminance Aetherial Sanctuary Era)", "Crystalline sanctums with refractive prism lighting and expansive celestial skyboxes."),
        ],
    },
    {
        "lineage_id": "ryo_hirata_izuka_wada_command_grid",
        "lead_artists": "Ryo Hirata, Daisuke Izuka & Sachiko Wada",
        "kanji": "平田 亮, 井塚 大介 & 和田 幸子",
        "works": [
            "Advance Wars", "Advance Wars 2: Black Hole Rising", "Advance Wars: Dual Strike",
            "Advance Wars: Days of Ruin", "Fire Emblem: Thracia 776", "Fire Emblem: The Binding Blade", "Fire Emblem: The Sacred Stones"
        ],
        "architectural_dna": (
            "High-readability tactical terrain tiles, unmistakable HQ capture points, fortified bunkers, "
            "throne/gate defensive tiles, dynamic Commanding Officer battle cut-in backgrounds, crisp graphic outlines."
        ),
        "shader_grading": {"masonry_relief": 0.55, "storybook_bloom": 0.30, "grid_contrast": 1.00, "neon_conduit": 0.40},
        "eras": [
            ("1999-2004 (Fire Emblem Thracia 776 / Binding Blade / Sacred Stones Castle & Throne Maps)", "Clean orthogonal castle masonry, throne capture tiles, forest/fort defense icons with zero ambiguity."),
            ("2001-2005 (Advance Wars 1/2/Dual Strike Macro Land Command Grid)", "Punchy faction-colored HQs, cities, bases, and road networks paired with kinetic split-screen battle cut-in backdrops."),
            ("2008 (Advance Wars: Days of Ruin Fortified Ruin Grid)", "Weathered industrial command bunkers, tactical radar craters, high-contrast directional rim lighting."),
        ],
    },
    {
        "lineage_id": "toru_nakayama_inti_creates_neo_arcadia",
        "lead_artists": "Toru Nakayama & Inti Creates Environment Team (Masaya Suzuki / Makoto Yabe)",
        "kanji": "中山 徹 & インティ・クリエイツ背景美術班 (鈴木 雅哉 / 矢部 誠)",
        "works": ["Mega Man Zero 1-4 (Rockman Zero)", "Mega Man ZX", "Dragon Marked for Death"],
        "architectural_dna": (
            "Neo Arcadia cyber-cathedrals, sharp 45-degree beveled titanium floor plating, glowing emerald/cyan "
            "Cyber-Elf energy conduits, stark black ink shadow recesses, Resistance Base industrial ruins."
        ),
        "shader_grading": {"masonry_relief": 0.75, "storybook_bloom": 0.55, "grid_contrast": 0.92, "neon_conduit": 1.00},
        "eras": [
            ("2002-2003 (Mega Man Zero 1-2 Neo Arcadia Sanctum & Resistance Base)", "Sleek cyber-gothic Reploid cathedrals contrasted with scarred subterranean Resistance Base command rooms."),
            ("2004-2005 (Mega Man Zero 3-4 Ragnarok & Area Zero Cyber-Biome)", "High-contrast beveled metallic platforms, pulsing neon data conduits, dramatic crimson/cyan atmospheric backlighting."),
            ("2006-2026 (Mega Man ZX & Dragon Marked for Death Hybrid Bio-Mechanical Ruins)", "Ancient techno-organic ruins with sharp specular bevel highlights and deep shadow wells."),
        ],
    },
]

SIX_BIOMES_SPEC: List[Dict] = [
    {
        "biome_id": "IvaliceStorybookJagd",
        "title": "Ambervale Storybook Jagd",
        "terrain_modifiers": ["LeylineCrystal", "StandardGround", "HighGround", "StandardGround", "CommandHQ", "StandardGround", "HighGround", "StandardGround", "LeylineCrystal"],
        "ambient_lighting": {"sky": [0.98, 0.92, 0.78], "equator": [0.68, 0.85, 0.92], "sun": [1.0, 0.95, 0.82], "fog": [0.012, 0.35, 8.0, 0.78]},
    },
    {
        "biome_id": "OrbonneDioramaBastion",
        "title": "Orbonne Isometric Bastion",
        "terrain_modifiers": ["HighGround", "StandardGround", "HighGround", "ShadowVeil", "HighGround", "ShadowVeil", "StandardGround", "CommandHQ", "StandardGround"],
        "ambient_lighting": {"sky": [0.82, 0.74, 0.60], "equator": [0.48, 0.42, 0.35], "sun": [0.96, 0.84, 0.64], "fog": [0.024, 0.55, 6.0, 0.30]},
    },
    {
        "biome_id": "MacroLandCommandGrid",
        "title": "Macro Land Command HQ Grid",
        "terrain_modifiers": ["CommandHQ", "StandardGround", "HighGround", "StandardGround", "CommandHQ", "StandardGround", "HighGround", "StandardGround", "CommandHQ"],
        "ambient_lighting": {"sky": [0.88, 0.96, 1.00], "equator": [0.62, 0.78, 0.90], "sun": [1.0, 0.99, 0.94], "fog": [0.005, 0.20, 14.0, 0.25]},
    },
    {
        "biome_id": "NeoArcadiaCyberSanctum",
        "title": "Neo Arcadia Cyber Sanctum",
        "terrain_modifiers": ["CyberConduit", "ShadowVeil", "CyberConduit", "StandardGround", "CommandHQ", "StandardGround", "CyberConduit", "ShadowVeil", "CyberConduit"],
        "ambient_lighting": {"sky": [0.12, 0.24, 0.36], "equator": [0.06, 0.14, 0.22], "sun": [0.45, 0.95, 1.0], "fog": [0.018, 0.42, 7.5, 0.88]},
    },
    {
        "biome_id": "ClockworkAetherFoundry",
        "title": "Clockwork Aether Foundry",
        "terrain_modifiers": ["CyberConduit", "HighGround", "LeylineCrystal", "HighGround", "CommandHQ", "HighGround", "LeylineCrystal", "HighGround", "CyberConduit"],
        "ambient_lighting": {"sky": [0.92, 0.72, 0.45], "equator": [0.48, 0.32, 0.20], "sun": [1.0, 0.78, 0.42], "fog": [0.020, 0.48, 7.0, 0.68]},
    },
    {
        "biome_id": "EclipseLunarShrine",
        "title": "Eclipse Lunar Shrine",
        "terrain_modifiers": ["ShadowVeil", "LeylineCrystal", "ShadowVeil", "LeylineCrystal", "CommandHQ", "LeylineCrystal", "ShadowVeil", "LeylineCrystal", "ShadowVeil"],
        "ambient_lighting": {"sky": [0.18, 0.22, 0.44], "equator": [0.10, 0.12, 0.28], "sun": [0.78, 0.86, 1.0], "fog": [0.022, 0.50, 6.5, 0.82]},
    },
]

TERRAIN_MODIFIER_RULES: List[Dict] = [
    {"modifier": "HighGround", "bonus_nesw": [1, 0, 1, 0], "elevation": 0.28, "rule": "Minagawa/Yoshida isometric stone bastion elevation (+1 Top & +1 Bottom axial defense)."},
    {"modifier": "LeylineCrystal", "bonus_nesw": [1, 1, 0, 0], "elevation": 0.08, "rule": "Minaba/Kamikokuryo Jagd mana crystal enclave (+1 Top & +1 Right arcane crystal resonance)."},
    {"modifier": "CommandHQ", "bonus_nesw": [1, 1, 1, 1], "elevation": 0.18, "rule": "Hirata/Izuka/Wada Advance Wars & Fire Emblem HQ capture point (+1 All Sides command aura)."},
    {"modifier": "CyberConduit", "bonus_nesw": [0, 1, 0, 1], "elevation": 0.05, "rule": "Nakayama/Inti Creates Neo Arcadia beveled neon energy bus (+1 Left & +1 Right lateral surge)."},
    {"modifier": "ShadowVeil", "bonus_nesw": [0, 0, 1, 1], "elevation": -0.04, "rule": "Vagrant Story / Resistance Base stealth cover tile (+1 Bottom & +1 Left ambush refraction)."},
]

ENVIRONMENT_ARENA_RENDERS: List[Dict[str, str]] = [
    {
        "filename": "env_minaba_ivalice_storybook.png",
        "biome": "IvaliceStorybookJagd",
        "artist": "Hideo Minaba, Koji Tsukamoto & Isamu Kamikokuryo",
        "positive": (
            "masterpiece, best quality, official tactical RPG isometric 3x3 battle board environment art direction by "
            "Hideo Minaba, Koji Tsukamoto, and Isamu Kamikokuryo (Final Fantasy Tactics Advance and Granblue Fantasy), "
            "vibrant storybook fantasy diorama plaza with clearly delineated 3x3 ornate cobblestone and marble tactical grid tiles, "
            "glowing turquoise Leyline mana crystals on corner tiles, floating sky-citadel clouds, warm golden sunlight bloom, "
            "no characters, environment background only, wide isometric view"
        ),
        "negative": "characters, people, portrait, close-up face, blurry, lowres, text, watermark, messy grid, dark muddy colors",
    },
    {
        "filename": "env_minagawa_yoshida_diorama.png",
        "biome": "OrbonneDioramaBastion",
        "artist": "Hiroshi Minagawa & Akihiko Yoshida",
        "positive": (
            "masterpiece, best quality, official 3D isometric tactical RPG diorama battlefield in the signature style of "
            "Hiroshi Minagawa and Akihiko Yoshida (Final Fantasy Tactics, Tactics Ogre, Vagrant Story), "
            "weathered medieval Orbonne stone bastion courtyard, stepped 3x3 isometric stone tile grid with elevated high-ground corner bastions, "
            "intricate pen-and-ink masonry crosshatching, warm parchment sepia and ochre torchlight chiaroscuro, "
            "no characters, environment diorama only"
        ),
        "negative": "characters, people, neon, flat vector, oversaturated, blurry, lowres, text, watermark",
    },
    {
        "filename": "env_hirata_advance_wars_hq.png",
        "biome": "MacroLandCommandGrid",
        "artist": "Ryo Hirata, Daisuke Izuka & Sachiko Wada",
        "positive": (
            "masterpiece, best quality, official tactical strategy battle board environment in the signature art style of "
            "Ryo Hirata, Daisuke Izuka, and Sachiko Wada (Intelligent Systems Advance Wars Dual Strike and Fire Emblem GBA), "
            "high-readability isometric 3x3 tactical command grid, central futuristic-military Command HQ capture building, "
            "fortified corner defense bunkers, crisp graphic linework, punchy saturated terrain tiles, clean supply roads, "
            "no characters, tactical map environment only"
        ),
        "negative": "characters, people, blurry, washed out, indistinct tiles, low contrast, lowres, text, watermark",
    },
    {
        "filename": "env_nakayama_neo_arcadia_mmz.png",
        "biome": "NeoArcadiaCyberSanctum",
        "artist": "Toru Nakayama & Inti Creates Environment Team (Masaya Suzuki / Makoto Yabe)",
        "positive": (
            "masterpiece, best quality, official cyber-tactical arena environment in the signature art style of "
            "Toru Nakayama and Inti Creates (Mega Man Zero / Rockman Zero and Mega Man ZX), "
            "Neo Arcadia cyber-cathedral sanctum with an isometric 3x3 grid of sharp beveled metallic titanium floor tiles, "
            "glowing emerald and cyan Cyber-Elf energy conduits running between tiles, stark black shadow recesses, "
            "holographic command pillars, no characters, environment arena only"
        ),
        "negative": "characters, people, organic mud, dull flat lighting, photorealistic, blurry, lowres, text, watermark",
    },
]


def build_60_environment_records() -> List[Dict]:
    records: List[Dict] = []

    # 1. 15 Longitudinal Environmental Era Specification Records (5 lineages x 3 eras = 15)
    for master in ENVIRONMENT_MASTERS_SPEC:
        for era_title, era_desc in master["eras"]:
            records.append({
                "record_type": "environment_longitudinal_era",
                "lineage_id": master["lineage_id"],
                "lead_artists": master["lead_artists"],
                "kanji": master["kanji"],
                "era": era_title,
                "works": master["works"],
                "architectural_dna": era_desc,
                "shader_grading": master["shader_grading"],
                "instruction": f"Configure the SynapseEnvironmentBiomeSystem architectural & shader pipeline for {master['lead_artists']} during {era_title}.",
                "response": (
                    f"Environmental Masters: {master['lead_artists']} ({master['kanji']}) | Era: {era_title} | "
                    f"Titles: {', '.join(master['works'])} | Architecture: {era_desc} | "
                    f"Diorama Shader Grading: {json.dumps(master['shader_grading'])}"
                ),
            })

    # 2. 30 Biome x Master Lineage Synthesis Records (6 playable 3x3 biomes x 5 environmental lineages = 30)
    for biome in SIX_BIOMES_SPEC:
        for master in ENVIRONMENT_MASTERS_SPEC:
            records.append({
                "record_type": "biome_master_architecture_conditioning",
                "biome_id": biome["biome_id"],
                "biome_title": biome["title"],
                "lineage_id": master["lineage_id"],
                "lead_artists": master["lead_artists"],
                "terrain_layout_3x3": biome["terrain_modifiers"],
                "ambient_lighting": biome["ambient_lighting"],
                "shader_grading": master["shader_grading"],
                "instruction": (
                    f"Synthesize the 3x3 isometric board layout and ambient shader vectors for biome `{biome['biome_id']}` "
                    f"({biome['title']}) using the environmental design rules of {master['lead_artists']}."
                ),
                "response": json.dumps({
                    "biome_id": biome["biome_id"],
                    "lead_artists": master["lead_artists"],
                    "architectural_dna": master["architectural_dna"],
                    "grid_3x3_modifiers": biome["terrain_modifiers"],
                    "ambient_lighting": biome["ambient_lighting"],
                    "shader_grading": master["shader_grading"],
                }),
            })

    # 3. 15 Tactical Terrain Modifier x Master Lineage Spatial Rule Records (5 terrain modifiers x 3 core rules = 15)
    for mod in TERRAIN_MODIFIER_RULES:
        for idx, master in enumerate(ENVIRONMENT_MASTERS_SPEC[:3]):
            records.append({
                "record_type": "terrain_modifier_spatial_rule",
                "modifier": mod["modifier"],
                "lineage_id": master["lineage_id"],
                "lead_artists": master["lead_artists"],
                "bonus_nesw": mod["bonus_nesw"],
                "elevation_offset": mod["elevation"],
                "spatial_rule": mod["rule"],
                "instruction": (
                    f"Define the 3x3 cell elevation, NESW stat modifier, and visual tile readability rule for "
                    f"`{mod['modifier']}` under {master['lead_artists']} environmental direction."
                ),
                "response": json.dumps({
                    "modifier": mod["modifier"],
                    "bonus_nesw": mod["bonus_nesw"],
                    "elevation_offset": mod["elevation"],
                    "rule": mod["rule"],
                    "reference_lineage": master["lead_artists"],
                }),
            })

    assert len(records) == 60, f"Expected exactly 60 environmental records, got {len(records)}"
    return records


def append_environment_records_to_corpus() -> Dict:
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing_records: List[Dict] = []
    preserved_tail_records: List[Dict] = []
    if DATASET_PATH.exists():
        with DATASET_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                rtype = obj.get("record_type")
                if rtype in ("longitudinal_era_specification", "card_illustrator_conditioning"):
                    existing_records.append(obj)
                elif rtype in (
                    "itb_staccs_isometric_stack_conditioning",
                    "metal_gear_acid_cost_and_solid_eye_conditioning",
                    "mirofish_strands_multi_agent_simulation_soup",
                    "anime_baseline_proprietary_style_distillation",
                ) or str(obj.get("record_id", "")).startswith(("itb_staccs_", "mga_", "miro_strands_", "anime_distill_")):
                    preserved_tail_records.append(obj)

    env_records = build_60_environment_records()
    combined = existing_records + env_records + preserved_tail_records
    for idx, rec in enumerate(combined, start=1):
        if "record_id" not in rec or not rec["record_id"]:
            rec["record_id"] = f"rec_{idx:03d}"

    with DATASET_PATH.open("w", encoding="utf-8") as f:
        for rec in combined:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return {
        "dataset_path": str(DATASET_PATH),
        "base_character_records": len(existing_records),
        "appended_environment_records": len(env_records),
        "total_longitudinal_records": len(combined),
    }


def render_environment_on_rtx4080(
    spec: Dict[str, str],
    width: int = 1024,
    height: int = 768,
    steps: int = 16,
    force: bool = False,
) -> Dict:
    ENV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    local_file = ENV_OUTPUT_DIR / spec["filename"]

    if local_file.exists() and not force and local_file.stat().st_size > 50_000:
        return {
            "filename": spec["filename"],
            "biome": spec["biome"],
            "artist": spec["artist"],
            "local_file": str(local_file),
            "bytes": local_file.stat().st_size,
            "resolution": f"{width}x{height}",
            "elapsed_s": 0.0,
            "cached": True,
        }

    seed = (abs(hash(spec["filename"])) % (2**31 - 1)) + 4080
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
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "animagineXLV31_v31.safetensors"},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": spec["positive"]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": spec["negative"]},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"SynapseEnv_{spec['biome']}", "images": ["8", 0]},
        },
    }

    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=json.dumps({"prompt": workflow}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=15) as resp:
        queued = json.loads(resp.read().decode("utf-8"))
    prompt_id = queued["prompt_id"]

    for _ in range(150):
        time.sleep(0.5)
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10) as hresp:
            hist = json.loads(hresp.read().decode("utf-8"))
        if prompt_id in hist:
            outputs = hist[prompt_id].get("outputs", {})
            for node_out in outputs.values():
                if "images" in node_out and node_out["images"]:
                    img_info = node_out["images"][0]
                    qs = urllib.parse.urlencode({
                        "filename": img_info["filename"],
                        "subfolder": img_info.get("subfolder", ""),
                        "type": img_info.get("type", "output"),
                    })
                    img_url = f"{COMFYUI_URL}/view?{qs}"
                    urllib.request.urlretrieve(img_url, local_file)
                    return {
                        "filename": spec["filename"],
                        "biome": spec["biome"],
                        "artist": spec["artist"],
                        "prompt_id": prompt_id,
                        "local_file": str(local_file),
                        "bytes": local_file.stat().st_size,
                        "resolution": f"{width}x{height}",
                        "elapsed_s": round(time.time() - t0, 2),
                        "cached": False,
                    }
    raise TimeoutError(f"Timed out waiting for ComfyUI environment prompt {prompt_id}")


def main() -> None:
    corpus_summary = append_environment_records_to_corpus()
    print(
        f"[Longitudinal Corpus] {corpus_summary['total_longitudinal_records']} total records "
        f"({corpus_summary['base_character_records']} base + {corpus_summary['appended_environment_records']} environmental) "
        f"-> {corpus_summary['dataset_path']}",
        flush=True,
    )

    rendered_arenas = []
    for spec in ENVIRONMENT_ARENA_RENDERS:
        res = render_environment_on_rtx4080(spec, width=1024, height=768, steps=16)
        print(
            f"[RTX 4080 ComfyUI 1024x768 Arena] {res['filename']} ({res['biome']}): "
            f"{res['bytes']} bytes in {res['elapsed_s']}s (cached={res['cached']})",
            flush=True,
        )
        rendered_arenas.append(res)

    print(
        json.dumps(
            {
                "corpus": corpus_summary,
                "environments_rendered": rendered_arenas,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
