#!/usr/bin/env python3
"""
Synapse Sovereign TCG Engine — Node 30 RTX 4080 ComfyUI Automated Card Art Generator
with Full Master Tactical Illustrator Style Library:
- `ryoma_ito`: Ryōma Itō (Final Fantasy Tactics Advance Main Character Designer)
- `akihiko_yoshida`: Akihiko Yoshida (Final Fantasy Tactics & FFTA Artistic Supervisor / Judge Illustrations)
- `hideo_minaba`: Hideo Minaba (Final Fantasy Tactics Advance Art Director, FFIX, Granblue Fantasy)
- `ryo_hirata`: Ryo Hirata (Advance Wars 1/2/Dual Strike/Days of Ruin & Fire Emblem Thracia 776/Binding Blade/Sacred Stones)
- `tactical_synthesis`: Master Synthesis combining Itō × Yoshida × Minaba × Hirata
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
OUTPUT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Resources/CardArt")
SHOWCASE_DIR = OUTPUT_DIR / "StyleShowcase"

ILLUSTRATOR_STYLE_LIBRARY: Dict[str, Dict[str, str]] = {
    "ryoma_ito": {
        "artist": "Ryōma Itō (伊藤 龍馬)",
        "works": "Final Fantasy Tactics Advance, FFTA2, FFXII: Revenant Wings",
        "prompt_prefix": (
            "masterpiece, best quality, official character illustration in the signature art style of Ryoma Ito "
            "(Final Fantasy Tactics Advance), lighter stylized character proportions, expressive dynamic silhouette, "
            "tapered gauntlets and boots, vibrant watercolor cel-wash over crisp ink linework, Ivalice fantasy aesthetic, "
        ),
        "negative": "photorealistic, 3d render, muddy colors, stiff pose, lowres, text, watermark",
    },
    "akihiko_yoshida": {
        "artist": "Akihiko Yoshida (吉田 明彦)",
        "works": "Final Fantasy Tactics, FFTA Artistic Supervisor (Judge Illustrations), Tactics Ogre, Vagrant Story",
        "prompt_prefix": (
            "masterpiece, best quality, official illustration in the signature art style of Akihiko Yoshida "
            "(Final Fantasy Tactics and FFTA Judge illustrations), intricate pen-and-ink crosshatching, warm parchment "
            "sepia and ochre undertones, ornate medieval-tactical Judge armor filigree, sculptural cloth folds, solemn heroic gravitas, "
        ),
        "negative": "neon, flat vector, plastic skin, oversaturated, lowres, text, watermark",
    },
    "hideo_minaba": {
        "artist": "Hideo Minaba (皆葉 英夫)",
        "works": "Final Fantasy Tactics Advance (Art Director), Final Fantasy IX, Granblue Fantasy",
        "prompt_prefix": (
            "masterpiece, best quality, art direction by Hideo Minaba (Final Fantasy Tactics Advance and Granblue Fantasy), "
            "vibrant storybook fantasy illustration, richly textured painterly sky-citadel backdrop, warm atmospheric light bloom, "
            "intricate decorative card border framing, "
        ),
        "negative": "sterile background, plain void, harsh digital edges, lowres, text, watermark",
    },
    "ryo_hirata": {
        "artist": "Ryo Hirata (平田 亮)",
        "works": "Super Famicom Wars, Advance Wars, Advance Wars 2: Black Hole Rising, Advance Wars: Dual Strike, Days of Ruin, Fire Emblem: Thracia 776 / The Binding Blade / The Sacred Stones",
        "prompt_prefix": (
            "masterpiece, best quality, official character and battle unit illustration in the signature art style of Ryo Hirata "
            "(Intelligent Systems Advance Wars Dual Strike and Fire Emblem Sacred Stones), bold crisp graphic linework, "
            "high-contrast cel shading, punchy tactical faction color-coding, dynamic Commanding Officer battle cut-in composition, "
        ),
        "negative": "blurry, washed out, indistinct silhouette, low contrast, lowres, text, watermark",
    },
    "toru_nakayama": {
        "artist": "Toru Nakayama (中山 徹)",
        "works": "Mega Man Zero 1-4 (Rockman Zero), Mega Man ZX, Speed Power Gunbike, Dragon Marked for Death, MMZ/ZX Legacy Collection",
        "prompt_prefix": (
            "masterpiece, best quality, official character and promotional illustration in the signature art style of Toru Nakayama "
            "(Rockman Zero / Mega Man Zero and Mega Man ZX, Inti Creates), sleek stylized cyber-armor with sharp beveled edges, "
            "bold triangular silhouette shapes, noticeably larger expressive eyes, stark black shadow blocks with glowing neon cyber-elf highlights, "
        ),
        "negative": "bulky clunky proportions, dull flat lighting, photorealistic, blurry, lowres, text, watermark",
    },
    "hiroshi_minagawa": {
        "artist": "Hiroshi Minagawa & Ivalice Isometric Diorama Team (皆川 裕史)",
        "works": "Tactics Ogre, Final Fantasy Tactics, Vagrant Story, Final Fantasy Tactics Advance / FFXII",
        "prompt_prefix": (
            "masterpiece, best quality, isometric tactical RPG battlefield diorama in the signature art style of Hiroshi Minagawa "
            "and the Final Fantasy Tactics / Tactics Ogre environment team, terraced stone masonry, medieval timber roofs, "
            "warm directional sunlight, crisp elevation cliffs, hand-painted miniature diorama aesthetic, "
        ),
        "negative": "flat 2d plane, blurry perspective, modern asphalt, lowres, text, watermark",
    },
    "isamu_kamikokuryo": {
        "artist": "Isamu Kamikokuryo (上国料 勇)",
        "works": "Final Fantasy XII (Ivalice Environmental & Airship Art Director), Final Fantasy X, Final Fantasy XIII",
        "prompt_prefix": (
            "masterpiece, best quality, environmental concept art and battle arena in the signature style of Isamu Kamikokuryo "
            "(Final Fantasy XII Ivalice architecture), monumental sun-bleached limestone arches, ornate brass airship filigree, "
            "glowing cyan magicite skystone crystals, sweeping atmospheric depth, "
        ),
        "negative": "cramped interior, muddy lighting, flat colors, lowres, text, watermark",
    },
    "hiroo_isono": {
        "artist": "Hiroo Isono & Kouichi Ishii (磯野 宏夫 × 石井 浩一 — Mana World Team)",
        "works": "Secret of Mana, Trials of Mana, Legend of Mana, Heroes of Mana",
        "prompt_prefix": (
            "masterpiece, best quality, environmental illustration in the signature style of Hiroo Isono and Secret of Mana / "
            "Heroes of Mana world art, colossal ancient Mana Tree roots, lush multi-layered emerald botanical canopy, "
            "dappled golden sunbeams, bioluminescent forest shrine, "
        ),
        "negative": "barren desert, industrial grey, flat lighting, lowres, text, watermark",
    },
    "inti_creates_env": {
        "artist": "Makoto Yabe & Inti Creates Environment Team (矢部 誠 / インティ・クリエイツ背景班)",
        "works": "Mega Man Zero 1-4 (Neo Arcadia & Resistance Base Environments), Mega Man ZX, Azure Striker Gunvolt",
        "prompt_prefix": (
            "masterpiece, best quality, cyber-fantasy tactical battlefield environment in the style of Mega Man Zero (Neo Arcadia) "
            "and Mega Man ZX by Inti Creates, sleek beveled metallic spires, glowing cyan cyber-elf energy conduits, "
            "stark black shadow contrast, dramatic sci-fi cathedral lighting, "
        ),
        "negative": "rustic medieval wood, muddy brown, blurry edges, lowres, text, watermark",
    },
    "yoji_shinkawa": {
        "artist": "Yoji Shinkawa (新川 洋司 — Kojima Productions)",
        "works": "Metal Gear Solid 1-5, Zone of the Enders (Jehuty / Anubis), Death Stranding",
        "prompt_prefix": (
            "masterpiece, best quality, official tactical mecha and character illustration in the signature art style of Yoji Shinkawa "
            "(Metal Gear Solid and Zone of the Enders), expressive calligraphic sumi-e brush-pen ink strokes, dynamic dry-brush splatter, "
            "stark negative space, olive drab and glowing cyan accent wash, "
        ),
        "negative": "smooth airbrush, plastic 3d render, cluttered background, lowres, text, watermark",
    },
    "kazuma_kaneko": {
        "artist": "Kazuma Kaneko (金子 一馬 — Atlus / Megaten)",
        "works": "Shin Megami Tensei I-III: Nocturne, Persona 1-2, Devil Summoner, Zone of the Enders: The 2nd Runner",
        "prompt_prefix": (
            "masterpiece, best quality, official cyber-occult character and entity illustration in the signature art style of Kazuma Kaneko "
            "(Shin Megami Tensei III Nocturne and Devil Summoner), porcelain-smooth cyber-occult anatomy, stark black ink shadow blocks, "
            "luminous geometric esoteric sigils, clinical high-contrast cel shading, "
        ),
        "negative": "soft pastel, cute chibi, messy sketch lines, lowres, text, watermark",
    },
    "terada_suzuki": {
        "artist": "Katsuya Terada & Yasushi Suzuki (寺田 克也 × 鈴木 康士 — Ikaruga / Sin & Punishment)",
        "works": "Ikaruga, Sin & Punishment, Blood: The Last Vampire, Busin 0: Wizardry Alternative",
        "prompt_prefix": (
            "masterpiece, best quality, official illustration in the signature style of Yasushi Suzuki (Ikaruga and Sin and Punishment) "
            "and Katsuya Terada, dense organic-biomechanical ink crosshatching, dramatic black and white polarity energy chiaroscuro, "
            "visceral kinetic brush strokes, "
        ),
        "negative": "flat cartoon, washed out, static pose, lowres, text, watermark",
    },
    "tactical_synthesis": {
        "artist": "Frontier Legends 9-Master Synthesis (Itō × Yoshida × Minaba × Hirata × Nakayama × Minagawa × Kamikokuryo × Isono × Inti Creates)",
        "works": "PROJECT CF: Card Front Tactics — Frontier Legends & CardCraft",
        "prompt_prefix": (
            "masterpiece, best quality, tactical RPG trading card illustration synthesizing Ryoma Ito (FFTA stylized silhouette), "
            "Akihiko Yoshida (FFT Judge armor filigree and crosshatching), Hideo Minaba (vibrant storybook art direction), "
            "Ryo Hirata (Advance Wars & Fire Emblem crisp tactical unit readability), and Toru Nakayama (Mega Man Zero beveled cyber-armor), "
        ),
        "negative": "lowres, bad anatomy, text, watermark, blurry, deformed, cropped, worst quality",
    },
}

PROJECT_CF_ART_PROMPTS: Dict[str, str] = {
    "cf_01_mystic_mage": (
        "Mystic Mage Arcane Enigma, ethereal spellcaster in glowing astral robes floating above a tactical holographic grid, "
        "arcane runes, violet and cyan mana crystals, dramatic rim lighting"
    ),
    "cf_02_mech_knight": (
        "Mech Knight Iron Vanguard, heavy bipedal tactical mecha-armor knight wielding a plasma lance and energy shield, "
        "sparks, industrial hangar, glowing cyan optics, dramatic cinematic lighting"
    ),
    "cf_03_celestial_guardian": (
        "Celestial Guardian Divine Sentinel, valkyrie Judge-paladin in radiant gold and white winged armor, halo of solar light, "
        "healing aura particles, sacred geometry, epic low-angle composition"
    ),
    "cf_04_shadow_assassin": (
        "Shadow Assassin Midnight Eclipse, cloaked phantom rogue materializing from void smoke with dual obsidian phase-daggers, "
        "crimson and purple accents, moonlit rooftop, dynamic action pose"
    ),
    "cf_05_elemental_sprite": (
        "Elemental Sprite Nature's Grace, luminous forest spirit woven from emerald bioluminescent vines, swirling wind and water orbs, "
        "ancient overgrown ruin, vibrant magical realism"
    ),
    "cf_06_galactic_explorer": (
        "Galactic Explorer Cosmic Odyssey, frontier starship Commanding Officer in sleek exo-suit with holographic star-map visor, "
        "warp drive nebula vortex in background"
    ),
    "cf_07_clockwork_sorcerer": (
        "Clockwork Sorcerer Temporal Enigma, steampunk chronomancer surrounded by floating brass gears, shattered hourglasses, and golden time-rifts, "
        "ornate arcane-mechanical staff, warm amber and teal lighting"
    ),
    "cf_08_phoenix_guardian": (
        "Phoenix Guardian Eternal Flame, majestic armored fire-bird guardian erupting in solar flares and molten feathers, "
        "rebirth embers, volcanic sky, high contrast fiery glow"
    ),
    "cf_09_cyber_ninja": (
        "Cyber Ninja Digital Shadow, sleek shinobi in optical-camouflage armor with high-frequency katana, "
        "digital holographic glitch hexagons, neon teal matrix rain"
    ),
    "cf_10_lunar_oracle": (
        "Lunar Oracle Celestial Insight, serene high priestess beneath a giant crescent moon, silver astrolabe, "
        "starlight constellation threads, deep indigo and pearl palette"
    ),
    "cc_01_sketching": (
        "futuristic concept artist holographic drafting table, glowing cyan wireframe mecha blueprints floating in mid-air, stylus pen, creative studio lighting"
    ),
    "cc_02_concept_art": (
        "radiant holographic masterwork painting materializing into a living guardian mech, vibrant prism energy, golden ratio grid lines, arcane studio"
    ),
    "cc_03_storyboard": (
        "floating cinematic holographic storyboard panels depicting an epic mecha battle sequence, dynamic camera vectors, neon blue and amber UI"
    ),
    "cc_04_animatic": (
        "high-tech timeline projection engine rendering a 3D holographic battlefield in real-time, laser projectors, cybernetic director console"
    ),
}

ENVIRONMENTAL_BATTLEFIELD_PROMPTS: Dict[str, str] = {
    "env_01_ivalice_jagd_citadel": (
        "3x3 isometric tactical RPG battlefield diorama of an ancient Ivalice Jagd stone citadel, terraced elevation steps, "
        "weathered medieval arches, glowing law crystal pillar, warm golden sunset bounce lighting"
    ),
    "env_02_advance_wars_dual_front": (
        "isometric tactical command map with Orange Star vs Black Hole HQ bases, crisp terrain tiles, bridges, mountain choke points, "
        "vibrant strategic battlefield readability"
    ),
    "env_03_neo_arcadia_cyber_sanctum": (
        "Neo Arcadia cyber-cathedral battle arena, sleek beveled metallic monoliths, glowing cyan Cyber-Elf energy conduits, "
        "high-contrast crimson and teal rim lighting, futuristic Reploid ruins"
    ),
    "env_04_mana_world_tree_shrine": (
        "sacred World Tree botanical tactical sanctuary, colossal mossy roots forming elevated battle platforms, "
        "lush emerald canopy with golden sunbeams and bioluminescent water pools"
    ),
    "env_05_skystone_airship_dock": (
        "floating sky-citadel airship dock in Bhujerba / Ivalice, sun-bleached limestone colonnades, ornate brass hull ribs, "
        "glowing blue magicite skystone levitation crystals, vast cloudsea horizon"
    ),
    "env_06_3x3_tactical_diorama_grid": (
        "playable 3x3 tactical card battle arena suspended in an arcane observatory, crystalline tile borders, "
        "elevated commander pedestals, painterly atmospheric depth"
    ),
}


def generate_card_art_on_rtx4080(
    card_id: str,
    style_key: str = "tactical_synthesis",
    out_path: Path | None = None,
    width: int = 768,
    height: int = 1024,
    steps: int = 15,
    force: bool = False,
) -> Dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    local_file = out_path or (OUTPUT_DIR / f"{card_id}.png")
    local_file.parent.mkdir(parents=True, exist_ok=True)

    if local_file.exists() and not force and local_file.stat().st_size > 50_000:
        return {
            "card_id": card_id,
            "style_key": style_key,
            "local_file": str(local_file),
            "bytes": local_file.stat().st_size,
            "elapsed_s": 0.0,
            "cached": True,
        }

    style = ILLUSTRATOR_STYLE_LIBRARY.get(style_key, ILLUSTRATOR_STYLE_LIBRARY["tactical_synthesis"])
    subject = (
        PROJECT_CF_ART_PROMPTS.get(card_id)
        or ENVIRONMENTAL_BATTLEFIELD_PROMPTS.get(card_id)
        or PROJECT_CF_ART_PROMPTS["cf_01_mystic_mage"]
    )
    prompt_text = style["prompt_prefix"] + subject
    seed = (abs(hash(f"{card_id}_{style_key}")) % (2**31 - 1)) + 202

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
            "inputs": {"clip": ["4", 1], "text": prompt_text},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": style["negative"]},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"ProjectCF_{card_id}_{style_key}", "images": ["8", 0]},
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

    for _ in range(120):
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
                        "card_id": card_id,
                        "style_key": style_key,
                        "artist": style["artist"],
                        "prompt_id": prompt_id,
                        "local_file": str(local_file),
                        "bytes": local_file.stat().st_size,
                        "elapsed_s": round(time.time() - t0, 2),
                        "cached": False,
                    }
    raise TimeoutError(f"Timed out waiting for ComfyUI prompt {prompt_id}")


def render_all_roster(style_key: str = "tactical_synthesis") -> List[Dict]:
    results = []
    for cid in PROJECT_CF_ART_PROMPTS:
        res = generate_card_art_on_rtx4080(cid, style_key=style_key, width=768, height=1024, steps=15)
        print(f"[RTX 4080 ComfyUI | {style_key}] {cid}: {res['bytes']} bytes in {res['elapsed_s']}s (cached={res['cached']})", flush=True)
        results.append(res)
    return results


def render_4_master_illustrator_showcase() -> List[Dict]:
    showcase_pairs = [
        ("cf_01_mystic_mage", "ryoma_ito", SHOWCASE_DIR / "style_ryoma_ito_ffta.png"),
        ("cf_03_celestial_guardian", "akihiko_yoshida", SHOWCASE_DIR / "style_akihiko_yoshida_judge.png"),
        ("cf_07_clockwork_sorcerer", "hideo_minaba", SHOWCASE_DIR / "style_hideo_minaba_storybook.png"),
        ("cf_02_mech_knight", "ryo_hirata", SHOWCASE_DIR / "style_ryo_hirata_advance_wars.png"),
    ]
    results = []
    for cid, skey, out_p in showcase_pairs:
        res = generate_card_art_on_rtx4080(cid, style_key=skey, out_path=out_p, width=768, height=1024, steps=16)
        print(f"[RTX 4080 Illustrator Showcase | {skey}] -> {out_p.name}: {res['bytes']} bytes in {res['elapsed_s']}s", flush=True)
        results.append(res)
    return results


if __name__ == "__main__":
    render_all_roster()
    showcase = render_4_master_illustrator_showcase()
    print("SHOWCASE COMPLETE:", len(showcase), "master artist variants rendered in", str(SHOWCASE_DIR))
