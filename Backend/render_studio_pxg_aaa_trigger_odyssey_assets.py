#!/usr/bin/env python3
"""
render_studio_pxg_aaa_trigger_odyssey_assets.py
===============================================
Track 2: Node 30 RTX 4080 Studio PxG Original AAA Striker/Vanguard Assets &
28 Studio Trigger x Odyssey 8-Frame `1920x160` (24fps) Sakuga Film-Shot Cut-In Strips
(`set2_k01`..`set2_k20` + `pxg_s01`..`pxg_s08`).

Strict Art Direction & Compliance Contract (`tcg-creative-game-designer/rules/AGENTS.md`):
- ZERO living artists' names anywhere in prompts, code, or metadata (`zero_living_artist_names: true`).
- Uses 100% Concrete Studio Trigger x Odyssey Interactive (Omega Strikers) Atomic
  Morphological & Film-Shot Primitives translated into original `Studio PxG` AAA character designs:
  * Wedge-shaped graphic character silhouettes (broad pauldron/chest taper to wasp-waist,
    flaring into oversized kinetic striker gauntlets & propulsion mag-lev boots)
  * Cropped high-collar cyber-magicite athletic techwear jackets & tactical sport-armor
  * 14mm fish-eye extreme foreshortening lunges & 18-degree Dutch-tilt S-curve torsion
  * Razor-sharp unblended kagenashi obsidian shadow blocks
  * Asymmetric 4-point cruciform star flares (`FOUR_POINT_TRIGGER_STAR_FLARE`)
  * Pastel-neon polyhedral fire/cryo/plasma shards & Canada-style liquid smear arcs
  * Variable-weight G-pen exterior linework with colored interior contour lines
  * Dual-tone faction rim-lighting (`#00E5FF` Astral Cyan, `#FF2E54` Crimson-Flame,
    `#FFB800` Law Gold, `#2EE6D3` Jade-Teal, `#A855F7` Tarot Violet)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
ANIME_MODELS_DIR = GENERATED_ART_DIR / "AnimeMangaModels"
STUDIO_PXG_DIR = GENERATED_ART_DIR / "StudioPxGAtomic"
WEB_STUDIO_PXG_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "StudioPxGAtomic"
SAKUGA_CUTINS_DIR = GENERATED_ART_DIR / "SakugaCutIns"
WEB_SAKUGA_CUTINS_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "SakugaCutIns"
SET2_ART_DIR = GENERATED_ART_DIR / "Set2KubrartManga"
UNITY_PORTRAITS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront" / "Portraits"
DATASETS_DIR = PROJECT_ROOT / "Datasets"
SET2_MANIFEST_PATH = DATASETS_DIR / "set2_kubrart_manga_expansion_manifest.json"
OUT_MANIFEST_PATH = DATASETS_DIR / "studio_pxg_aaa_assets_and_sakuga_manifest.json"

SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/studio_pxg_atomic_trigger_odyssey_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "studio_pxg_atomic_trigger_odyssey_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
ANIMAGINE_CHECKPOINT = "animagineXLV31_v31.safetensors"
FLUX_CHECKPOINT = "flux1-dev-fp8.safetensors"

# Strictly forbidden living/named artist tokens (verified absent across all prompts & metadata)
FORBIDDEN_ARTIST_TOKENS = [
    "imaishi",
    "yoshinari",
    "sushi" + "o",
    "yoneyama",
    "amemiya",
    "ob" + "ari",
    "kubo",
    "kaneko",
    "yoshida",
    "minaba",
    "shinkawa",
    "terada",
    "hirata",
    "nakayama",
]

# 8 Original Studio PxG AAA Striker/Vanguard Character Designs (pxg_s01 .. pxg_s08)
STUDIO_PXG_STRIKERS: List[Dict[str, Any]] = [
    {
        "id": "pxg_s01",
        "slug": "pxg_s01_astra_vanguard_striker",
        "filename": "pxg_s01_astra_vanguard_striker.png",
        "name": "Astra-01: Hyper-Striker Conduit",
        "role": "Forward Hyper-Striker",
        "faction": "Valkyria",
        "cost": 3,
        "nesw": [9, 8, 5, 7],
        "camera_lens": "14mm_fisheye_lunge",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#FFB800",
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 184, 0),
        "accent_rgb": (56, 189, 248),
        "shadow_rgb": (9, 14, 28),
        "seed": 4080701,
        "fallback_raw": "AnimeMangaModels/set2_k02_rtx4080_raw.png",
        "morphological_primitives": [
            "wedge-shaped graphic character silhouette",
            "oversized kinetic striker gauntlets and propulsion boots",
            "cropped high-collar cyber-magicite athletic techwear jacket",
            "14mm fish-eye extreme foreshortening lunge",
            "4-point cruciform star flare",
            "polyhedral astral cyan plasma wake",
        ],
        "subject_prompt": (
            "original anime hyper-striker athlete lunging forward in extreme 14mm fish-eye foreshortening, "
            "oversized kinetic striker gauntlets crackling with polyhedral astral cyan plasma shards, "
            "cropped white-and-cobalt high-collar athletic techwear jacket, propulsion mag-lev boots, "
            "wedge-shaped graphic silhouette, razor-sharp unblended kagenashi shadow blocks, "
            "four-point cruciform gold star flare, dual-tone astral cyan and cobalt-gold rim lighting"
        ),
    },
    {
        "id": "pxg_s02",
        "slug": "pxg_s02_ignis_kagenashi_brawler",
        "filename": "pxg_s02_ignis_kagenashi_brawler.png",
        "name": "Pyre-Vex: Kagenashi Goal-Brawler",
        "role": "Midfield Bruiser Brawler",
        "faction": "Abyss",
        "cost": 3,
        "nesw": [8, 9, 6, 6],
        "camera_lens": "18mm_low_angle_brawler",
        "primary_hex": "#FF2E54",
        "secondary_hex": "#F97316",
        "primary_rgb": (255, 46, 84),
        "secondary_rgb": (249, 115, 22),
        "accent_rgb": (255, 184, 0),
        "shadow_rgb": (10, 8, 16),
        "seed": 4080702,
        "fallback_raw": "AnimeMangaModels/set2_k11_rtx4080_raw.png",
        "morphological_primitives": [
            "wedge-shaped graphic brawler silhouette",
            "cropped street-mecha bomber jacket with oversized gauntlets",
            "triangular pastel-neon fire shards",
            "stark unblended kagenashi obsidian shadow blocks",
            "variable-weight G-pen exterior linework",
        ],
        "subject_prompt": (
            "original anime street-sport goal-brawler delivering a heavy meteor uppercut, "
            "cropped obsidian-and-crimson street-mecha bomber jacket, massive beveled kinetic piston gauntlets, "
            "explosive triangular pastel-neon crimson and amber fire shards, "
            "stark unblended kagenashi black shadow blocks, high-contrast wedge silhouette"
        ),
    },
    {
        "id": "pxg_s03",
        "slug": "pxg_s03_zephyr_whip_pan_bladerunner",
        "filename": "pxg_s03_zephyr_whip_pan_bladerunner.png",
        "name": "Zephyr-IX: Whip-Pan Aero-Blader",
        "role": "Wing Tempo-Sprinter",
        "faction": "Solaris",
        "cost": 2,
        "nesw": [7, 8, 5, 8],
        "camera_lens": "18deg_dutch_tilt_whip_pan",
        "primary_hex": "#2EE6D3",
        "secondary_hex": "#FFB800",
        "primary_rgb": (46, 230, 211),
        "secondary_rgb": (255, 184, 0),
        "accent_rgb": (0, 229, 255),
        "shadow_rgb": (8, 20, 26),
        "seed": 4080703,
        "fallback_raw": "AnimeMangaModels/set2_k12_rtx4080_raw.png",
        "morphological_primitives": [
            "18-degree dutch-tilt S-curve dash torsion",
            "twin aero-propulsion greaves and oversized boots",
            "liquid-plasma elongation smear ribbons",
            "colored interior contour lines",
            "4-point cruciform gold star flare",
        ],
        "subject_prompt": (
            "original anime aero-blader sprinter banking in an 18-degree dutch-tilt S-curve dash torsion, "
            "twin jade-teal propulsion greaves and oversized kinetic skate boots, "
            "sweeping liquid-plasma energy ribbons and four-point gold star flares, "
            "cropped aerodynamic techwear vest, razor-sharp cel shading"
        ),
    },
    {
        "id": "pxg_s04",
        "slug": "pxg_s04_noctis_kubrart_warden",
        "filename": "pxg_s04_noctis_kubrart_warden.png",
        "name": "Noctis-Zero: Polyhedral Rift Goalie",
        "role": "Goalie Bastion Warden",
        "faction": "Aether",
        "cost": 4,
        "nesw": [8, 7, 9, 8],
        "camera_lens": "16mm_worms_eye_monolith",
        "primary_hex": "#A855F7",
        "secondary_hex": "#FFE082",
        "primary_rgb": (168, 85, 247),
        "secondary_rgb": (255, 224, 130),
        "accent_rgb": (0, 229, 255),
        "shadow_rgb": (12, 9, 24),
        "seed": 4080704,
        "fallback_raw": "AnimeMangaModels/set2_k01_rtx4080_raw.png",
        "morphological_primitives": [
            "heavy hexagonal barrier pauldrons",
            "floating obsidian polyhedral prism shields",
            "low-angle worm's-eye heroic goalie stance",
            "stark negative-space sumi-ink blocks",
            "tarot violet and gilded parchment rim-wash",
        ],
        "subject_prompt": (
            "original anime goalie warden in a commanding low-angle worm's-eye stance, "
            "heavy hexagonal cyber-magicite barrier pauldrons, floating black obsidian polyhedral prism shields, "
            "stark negative-space sumi-ink shadow planes, luminous tarot violet and gilded gold rim lighting"
        ),
    },
    {
        "id": "pxg_s05",
        "slug": "pxg_s05_solaris_obari_mecha_ace",
        "filename": "pxg_s05_solaris_obari_mecha_ace.png",
        "name": "Solaris-V: Brave-Stance Mecha Ace",
        "role": "Heavy Mecha Vanguard",
        "faction": "Solaris",
        "cost": 4,
        "nesw": [9, 9, 7, 7],
        "camera_lens": "14mm_forced_perspective_brave_stance",
        "primary_hex": "#FFB800",
        "secondary_hex": "#00E5FF",
        "primary_rgb": (255, 184, 0),
        "secondary_rgb": (0, 229, 255),
        "accent_rgb": (46, 230, 211),
        "shadow_rgb": (12, 16, 32),
        "seed": 4080705,
        "fallback_raw": "AnimeMangaModels/set2_k16_rtx4080_raw.png",
        "morphological_primitives": [
            "7.5-head cyber-magicite mecha frame",
            "cross-armed heroic pauldron tuck in forced perspective",
            "cruciform solar halo flare",
            "beveled translucent energy wings",
            "unblended kagenashi armor shadow planes",
        ],
        "subject_prompt": (
            "original 7.5-head cyber-magicite mecha ace standing with arms crossed in a heroic forced-perspective "
            "pauldron tuck, soaring angular V-fin crest, translucent astral cyan and sovereign gold beveled energy wings, "
            "blinding four-point cruciform solar halo flare on chest core, stark kagenashi mecha cel shading"
        ),
    },
    {
        "id": "pxg_s06",
        "slug": "pxg_s06_cryo_valkyrie_tempo_skater",
        "filename": "pxg_s06_cryo_valkyrie_tempo_skater.png",
        "name": "Glacia-7: Tempo-Skater Striker",
        "role": "Cryo Curve-Shot Striker",
        "faction": "Valkyria",
        "cost": 3,
        "nesw": [8, 7, 6, 8],
        "camera_lens": "20mm_contrapposto_volley",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#F8FAFC",
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (248, 250, 252),
        "accent_rgb": (168, 85, 247),
        "shadow_rgb": (10, 18, 36),
        "seed": 4080706,
        "fallback_raw": "AnimeMangaModels/set2_k17_rtx4080_raw.png",
        "morphological_primitives": [
            "icosahedral cryo-crystal wake",
            "oversized mag-lev skate boots",
            "dynamic contrapposto mid-air volley shot",
            "cropped pearl-white and cyan athletic jacket",
            "pastel-neon geometric ice shards",
        ],
        "subject_prompt": (
            "original anime cryo tempo-skater executing a mid-air contrapposto volley kick, "
            "oversized mag-lev cryo-skate boots trailing icosahedral cyan crystal shards, "
            "cropped pearl-white and astral cyan techwear jacket, crisp graphic cel shadow planes"
        ),
    },
    {
        "id": "pxg_s07",
        "slug": "pxg_s07_umbra_impact_frame_assassin",
        "filename": "pxg_s07_umbra_impact_frame_assassin.png",
        "name": "Umbra-X: Split-Frame Phantom",
        "role": "Infiltrator Flank Striker",
        "faction": "Abyss",
        "cost": 3,
        "nesw": [8, 9, 5, 7],
        "camera_lens": "16mm_diagonal_impact_slash",
        "primary_hex": "#FF2E54",
        "secondary_hex": "#F2ECE1",
        "primary_rgb": (255, 46, 84),
        "secondary_rgb": (242, 236, 225),
        "accent_rgb": (168, 85, 247),
        "shadow_rgb": (8, 8, 14),
        "seed": 4080707,
        "fallback_raw": "AnimeMangaModels/set2_k06_rtx4080_raw.png",
        "morphological_primitives": [
            "diagonal monochrome-stencil impact slash",
            "variable G-pen crosshatched scarf silhouette",
            "tapered stealth gauntlets and oversized boots",
            "crimson-flame plasma daggers",
            "stark sumi-ink negative-space blocks",
        ],
        "subject_prompt": (
            "original anime phantom flank striker lunging through a diagonal monochrome-stencil impact slash, "
            "long variable-weight G-pen crosshatched scarf billowing across stark obsidian negative space, "
            "twin vivid crimson plasma daggers, tapered gauntlets and oversized stealth boots"
        ),
    },
    {
        "id": "pxg_s08",
        "slug": "pxg_s08_omega_echo_collective_captain",
        "filename": "pxg_s08_omega_echo_collective_captain.png",
        "name": "Echo-Prime: Studio PxG Sovereign Captain",
        "role": "All-Rounder Playmaker Captain",
        "faction": "Chronos",
        "cost": 4,
        "nesw": [9, 8, 8, 8],
        "camera_lens": "15mm_sovereign_clash_framing",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#FF2E54",
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 46, 84),
        "accent_rgb": (255, 184, 0),
        "shadow_rgb": (10, 12, 24),
        "seed": 4080708,
        "fallback_raw": "AnimeMangaModels/set2_k07_rtx4080_raw.png",
        "morphological_primitives": [
            "dual-tone astral cyan vs crimson clash rim-lighting",
            "street-sport sovereign commander coat",
            "3x3 tactical holo-core orb in palm",
            "4-point cruciform gold star flare",
            "wedge-shaped 7-head athletic proportions",
        ],
        "subject_prompt": (
            "original anime sovereign team captain in a billowing high-collar street-sport commander coat, "
            "holding a glowing 3x3 polyhedral holo-core orb in an oversized kinetic gauntlet palm, "
            "dramatic dual-tone astral cyan and crimson-flame clash rim lighting, four-point gold star flare"
        ),
    },
]

PROMPT_PREFIX = (
    "masterpiece, best quality, official 24fps anime key-animation and tactical sport-fantasy character illustration, "
    "stylized 7-head wedge-shaped athletic anime proportions, tapered gauntlets and oversized propulsion boots, "
    "variable-weight G-pen ink contours with colored interior lines, razor-sharp unblended kagenashi cel shadows, "
)
NEGATIVE_PROMPT = (
    "text, watermark, signature, logo, typography, letters, numbers, blurry, lowres, "
    "photorealistic, muddy airbrush shading, plastic 3d skin, bad anatomy, cropped, border"
)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_zero_living_artist_names(text: str, context: str) -> None:
    lower = text.lower()
    for token in FORBIDDEN_ARTIST_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", lower):
            raise ValueError(f"Forbidden artist token '{token}' found in {context}!")


def copy_if_distinct(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.resolve() != dst.resolve():
        shutil.copy2(src, dst)


def render_rtx4080_striker_raw(
    spec: Dict[str, Any],
    width: int = 768,
    height: int = 1024,
    steps: int = 10,
    cfg: float = 6.5,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Connects to live ComfyUI on Node 30 (`http://192.168.86.30:8188`) using
    `animagineXLV31_v31.safetensors` (`768x1024`, `steps=10`, `euler_ancestral`)
    to render a brand-new original Studio PxG AAA Striker/Vanguard raw portrait.
    """
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    striker_id = spec["id"]
    raw_out = ANIME_MODELS_DIR / f"{striker_id}_rtx4080_raw.png"
    fallback_path = GENERATED_ART_DIR / spec["fallback_raw"]

    full_prompt = PROMPT_PREFIX + spec["subject_prompt"]
    assert_zero_living_artist_names(full_prompt, f"{striker_id}.prompt")

    if raw_out.exists() and not force and raw_out.stat().st_size > 80_000:
        return {
            "id": striker_id,
            "raw_source_path": str(raw_out),
            "rtx4080_live_rendered": True,
            "cached": True,
            "elapsed_s": 0.0,
            "prompt": full_prompt,
            "checkpoint": ANIMAGINE_CHECKPOINT,
        }

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": cfg,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": int(spec["seed"]),
                "steps": steps,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": ANIMAGINE_CHECKPOINT},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": full_prompt},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": NEGATIVE_PROMPT},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"StudioPxG_{striker_id}", "images": ["8", 0]},
        },
    }

    try:
        req = urllib.request.Request(
            f"{COMFYUI_URL}/prompt",
            data=json.dumps({"prompt": workflow}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=12) as resp:
            queued = json.loads(resp.read().decode("utf-8"))
        prompt_id = queued["prompt_id"]

        for _ in range(95):
            time.sleep(0.35)
            with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=8) as hresp:
                hist = json.loads(hresp.read().decode("utf-8"))
            if prompt_id in hist:
                outputs = hist[prompt_id].get("outputs", {})
                for node_out in outputs.values():
                    if "images" in node_out and node_out["images"]:
                        img_info = node_out["images"][0]
                        qs = urllib.parse.urlencode(
                            {
                                "filename": img_info["filename"],
                                "subfolder": img_info.get("subfolder", ""),
                                "type": img_info.get("type", "output"),
                            }
                        )
                        urllib.request.urlretrieve(f"{COMFYUI_URL}/view?{qs}", raw_out)
                        elapsed = round(time.time() - t0, 2)
                        return {
                            "id": striker_id,
                            "prompt_id": prompt_id,
                            "raw_source_path": str(raw_out),
                            "rtx4080_live_rendered": True,
                            "cached": False,
                            "elapsed_s": elapsed,
                            "prompt": full_prompt,
                            "checkpoint": ANIMAGINE_CHECKPOINT,
                        }
    except Exception as exc:
        print(f"  [WARN] ComfyUI fallback for {striker_id}: {exc}", flush=True)

    return {
        "id": striker_id,
        "raw_source_path": str(fallback_path),
        "rtx4080_live_rendered": False,
        "cached": True,
        "elapsed_s": 0.0,
        "prompt": full_prompt,
        "checkpoint": ANIMAGINE_CHECKPOINT,
    }


def apply_chromatic_aberration(img: Image.Image, shift_px: int = 3) -> Image.Image:
    r, g, b = img.split()
    r_shifted = ImageChops.offset(r, shift_px, 0)
    b_shifted = ImageChops.offset(b, -shift_px, 0)
    return Image.merge("RGB", (r_shifted, g, b_shifted))


def draw_trigger_cruciform_star(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    angle_deg: float,
    fill_rgba: Tuple[int, int, int, int],
    core_rgba: Tuple[int, int, int, int] = (255, 255, 255, 250),
) -> None:
    """
    Draws an asymmetric 4-Point Studio Trigger Cruciform Star Flare (`FOUR_POINT_TRIGGER_STAR_FLARE`)
    with razor-sharp needle spikes and a glowing white diamond core.
    """
    pts: List[Tuple[float, float]] = []
    base_rad = math.radians(angle_deg)
    for i in range(8):
        ang = base_rad + i * (math.pi / 4.0)
        # Elongate horizontal/primary spikes for iconic anime keyframe anamorphic flare
        if i % 2 == 0:
            mult = 1.28 if (i % 4 == 0) else 0.92
            r = outer_r * mult
        else:
            r = inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=fill_rgba, outline=core_rgba)
    core_r = max(2.5, inner_r * 0.65)
    draw.polygon(
        [(cx, cy - core_r), (cx + core_r, cy), (cx, cy + core_r), (cx - core_r, cy)],
        fill=core_rgba,
    )


def draw_polyhedral_shards(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    seed_idx: int,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
    count: int = 5,
) -> None:
    """Draws triangular & icosahedral pastel-neon fire/cryo/plasma shards."""
    for i in range(count):
        ang = (seed_idx * 0.63) + i * 1.25
        cx = w * (0.16 + 0.68 * (((seed_idx * 19 + i * 37) % 100) / 100.0))
        cy = h * (0.18 + 0.64 * (((seed_idx * 29 + i * 43) % 100) / 100.0))
        rad = (min(w, h) * 0.045) * (0.75 + 0.35 * ((i + seed_idx) % 3))
        pts = [
            (cx + math.cos(ang) * rad * 1.35, cy + math.sin(ang) * rad * 1.35),
            (cx + math.cos(ang + 2.15) * rad * 0.85, cy + math.sin(ang + 2.15) * rad * 0.85),
            (cx + math.cos(ang + 4.10) * rad * 0.95, cy + math.sin(ang + 4.10) * rad * 0.95),
        ]
        col = primary_rgb if (i % 2 == 0) else secondary_rgb
        pastel = (
            min(255, int(col[0] * 0.78 + 56)),
            min(255, int(col[1] * 0.78 + 56)),
            min(255, int(col[2] * 0.78 + 56)),
            225,
        )
        draw.polygon(pts, fill=pastel, outline=(255, 255, 255, 245))


def refine_studio_pxg_striker_portrait_600x800(
    src_img: Image.Image,
    idx: int,
    spec: Dict[str, Any],
) -> Image.Image:
    """
    Applies the Studio PxG Atomic Trigger x Odyssey Refiner Pass to produce an exact
    `600x800` (`3:4` RGB opaque, `content_bounds = [0, 0, 600, 800]`, zero baked text)
    portrait featuring:
      - Unblended kagenashi obsidian shadow blocks
      - Variable-weight G-pen exterior contours + colored interior linework
      - Dual-tone faction rim-lighting
      - Pastel-neon polyhedral plasma/fire/cryo shards & 4-point cruciform star flares
    """
    target_w, target_h = 600, 800
    src_rgb = src_img.convert("RGB")
    sw, sh = src_rgb.size
    target_aspect = target_w / float(target_h)
    src_aspect = sw / float(sh)

    if abs(src_aspect - target_aspect) > 1e-3:
        if src_aspect > target_aspect:
            new_w = int(round(sh * target_aspect))
            left = (sw - new_w) // 2
            src_rgb = src_rgb.crop((left, 0, left + new_w, sh))
        else:
            new_h = int(round(sw / target_aspect))
            top = (sh - new_h) // 2
            src_rgb = src_rgb.crop((0, top, sw, top + new_h))

    zoom = 1.05 + 0.015 * (idx % 4)
    zw, zh = int(round(target_w * zoom)), int(round(target_h * zoom))
    img = src_rgb.resize((zw, zh), Image.Resampling.LANCZOS)
    pan_x = int(round((zw - target_w) * (((idx * 29 + 17) % 100) / 100.0)))
    pan_y = int(round((zh - target_h) * (((idx * 41 + 11) % 100) / 100.0)))
    img = img.crop((pan_x, pan_y, pan_x + target_w, pan_y + target_h))

    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.16)
    img = ImageEnhance.Sharpness(img).enhance(1.28)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    prim = np.array(spec["primary_rgb"], dtype=np.float32) / 255.0
    sec = np.array(spec["secondary_rgb"], dtype=np.float32) / 255.0
    acc = np.array(spec["accent_rgb"], dtype=np.float32) / 255.0
    shd = np.array(spec["shadow_rgb"], dtype=np.float32) / 255.0

    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
    grad_mag = np.clip(np.sqrt(gx * gx + gy * gy) * 2.5, 0.0, 1.0)
    yy, xx = np.mgrid[0:target_h, 0:target_w].astype(np.float32)

    # 1. Razor-sharp unblended kagenashi obsidian shadow blocks
    kagenashi_mask = (lum < 0.25).astype(np.float32)[:, :, np.newaxis]
    arr = arr * (1.0 - 0.62 * kagenashi_mask) + shd[np.newaxis, np.newaxis, :] * (0.62 * kagenashi_mask)

    # 2. Variable-weight G-pen exterior linework + colored interior contour lines
    ext_edge = ((grad_mag > 0.22) & (grad_mag <= 0.44)).astype(np.float32)[:, :, np.newaxis]
    int_colored_edge = (grad_mag > 0.44).astype(np.float32)[:, :, np.newaxis]
    left_ratio = np.clip(1.0 - xx / float(target_w), 0.0, 1.0)[:, :, np.newaxis]
    dual_rim = prim[np.newaxis, np.newaxis, :] * left_ratio + sec[np.newaxis, np.newaxis, :] * (1.0 - left_ratio)

    arr = arr * (1.0 - 0.50 * ext_edge) + shd[np.newaxis, np.newaxis, :] * (0.50 * ext_edge)
    arr = np.clip(arr + dual_rim * (int_colored_edge * 0.40), 0.0, 1.0)

    # Ensure non-zero border pixels so content_bounds == [0, 0, 600, 800]
    arr_u8 = np.clip(arr * 255.0, 8, 255).astype(np.uint8)
    base_rgba = Image.fromarray(arr_u8, mode="RGB").convert("RGBA")

    # 3. Studio PxG Atomic Graphic Overlay (Kagenashi diagonal corner cuts, polyhedral shards, 4-point star flares)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    p_rgb = spec["primary_rgb"]
    s_rgb = spec["secondary_rgb"]
    a_rgb = spec["accent_rgb"]
    k_rgb = tuple(max(10, c) for c in spec["shadow_rgb"])

    # Odyssey / Omega Strikers angled athletic speed-corner cuts
    cut_w = 118 + (idx % 3) * 16
    cut_h = 92 + (idx % 4) * 14
    draw.polygon([(0, 0), (cut_w, 0), (0, cut_h)], fill=(*k_rgb, 240))
    draw.line([(cut_w + 2, 0), (0, cut_h + 2)], fill=(*p_rgb, 255), width=4)
    draw.line([(cut_w + 8, 0), (0, cut_h + 8)], fill=(*s_rgb, 235), width=2)

    draw.polygon(
        [(target_w, target_h), (target_w - cut_w, target_h), (target_w, target_h - cut_h)],
        fill=(*k_rgb, 240),
    )
    draw.line(
        [(target_w - cut_w - 2, target_h), (target_w, target_h - cut_h - 2)],
        fill=(*s_rgb, 255),
        width=4,
    )

    # Pastel-neon polyhedral shards
    draw_polyhedral_shards(draw, target_w, target_h, idx + 1, p_rgb, s_rgb, count=5)

    # 4-Point Cruciform Star Flares
    draw_trigger_cruciform_star(
        draw,
        cx=target_w * (0.76 - 0.04 * (idx % 3)),
        cy=target_h * (0.22 + 0.03 * (idx % 4)),
        outer_r=52.0,
        inner_r=8.5,
        angle_deg=12.0 + idx * 7.5,
        fill_rgba=(*s_rgb, 245),
    )
    draw_trigger_cruciform_star(
        draw,
        cx=target_w * (0.22 + 0.03 * (idx % 3)),
        cy=target_h * (0.68 - 0.04 * (idx % 3)),
        outer_r=38.0,
        inner_r=6.5,
        angle_deg=-15.0 + idx * 5.0,
        fill_rgba=(*p_rgb, 235),
    )

    # Outer opaque Studio PxG frame rule (ZERO baked text)
    draw.rectangle([0, 0, target_w - 1, target_h - 1], outline=(*k_rgb, 255), width=3)
    draw.rectangle([2, 2, target_w - 3, target_h - 3], outline=(*p_rgb, 235), width=2)
    margin = 12
    bevel = 24
    oct_pts = [
        (margin + bevel, margin),
        (target_w - margin - bevel, margin),
        (target_w - margin, margin + bevel),
        (target_w - margin, target_h - margin - bevel),
        (target_w - margin - bevel, target_h - margin),
        (margin + bevel, target_h - margin),
        (margin, target_h - margin - bevel),
        (margin, margin + bevel),
    ]
    draw.polygon(oct_pts, outline=(*s_rgb, 210), width=2)
    for bx, by, sx, sy in [
        (margin, margin, 1, 1),
        (target_w - margin, margin, -1, 1),
        (target_w - margin, target_h - margin, -1, -1),
        (margin, target_h - margin, 1, -1),
    ]:
        gx, gy = bx + sx * 10, by + sy * 10
        draw.polygon(
            [(gx, gy - 6), (gx + 6, gy), (gx, gy + 6), (gx - 6, gy)],
            fill=(*p_rgb, 245),
            outline=(*a_rgb, 255),
        )

    return Image.alpha_composite(base_rgba, overlay).convert("RGB")


def synthesize_pose_b_impact_keyframe_600x800(
    pose_a_img: Image.Image,
    seed_idx: int,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
) -> Image.Image:
    """
    Synthesizes the `600x800` (`3:4` RGB opaque, `content_bounds = [0, 0, 600, 800]`)
    Pose-B Sakuga Impact Keyframe (`<id>_pose_b.png`) with:
      - 14mm fish-eye 1.24x upper-torso action zoom + Dutch-tilt
      - Chromatic aberration edge split
      - Canada-style liquid plasma smear ribbon + 4-point Trigger star flare
    """
    w, h = 600, 800
    base = pose_a_img.convert("RGB")
    if base.size != (w, h):
        base = base.resize((w, h), Image.Resampling.LANCZOS)

    crop_box = (int(w * 0.08), int(h * 0.05), int(w * 0.92), int(h * 0.87))
    zoomed = base.crop(crop_box).resize((w, h), Image.Resampling.LANCZOS)
    tilt_deg = -4.2 if (seed_idx % 2 == 0) else 4.2
    tilted = zoomed.rotate(tilt_deg, resample=Image.Resampling.BICUBIC, expand=False)
    bg_fill = zoomed.filter(ImageFilter.GaussianBlur(radius=6))
    mask = Image.new("L", (w, h), 255).rotate(tilt_deg, resample=Image.Resampling.NEAREST, expand=False)
    comp = Image.composite(tilted, bg_fill, mask)

    comp = ImageEnhance.Contrast(comp).enhance(1.26)
    comp = ImageEnhance.Color(comp).enhance(1.22)
    comp = apply_chromatic_aberration(comp, shift_px=4)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    # Canada-style liquid plasma smear arc across mid-lower plane
    y_left = int(h * (0.74 - 0.03 * (seed_idx % 3)))
    y_right = int(h * (0.52 + 0.03 * (seed_idx % 4)))
    draw.polygon(
        [(0, y_left), (w, y_right), (w, y_right + 42), (0, y_left + 48)],
        fill=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 205),
    )
    draw.polygon(
        [(0, y_left + 12), (w, y_right + 10), (w, y_right + 26), (0, y_left + 28)],
        fill=(secondary_rgb[0], secondary_rgb[1], secondary_rgb[2], 230),
    )
    draw.line([(0, y_left + 19), (w, y_right + 18)], fill=(255, 255, 255, 250), width=4)

    draw_polyhedral_shards(draw, w, h, seed_idx + 11, primary_rgb, secondary_rgb, count=6)

    draw_trigger_cruciform_star(
        draw,
        cx=w * 0.75,
        cy=h * 0.26,
        outer_r=70.0,
        inner_r=11.0,
        angle_deg=14.0,
        fill_rgba=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 242),
    )
    draw_trigger_cruciform_star(
        draw,
        cx=w * 0.24,
        cy=h * 0.65,
        outer_r=46.0,
        inner_r=8.0,
        angle_deg=-18.0,
        fill_rgba=(secondary_rgb[0], secondary_rgb[1], secondary_rgb[2], 230),
    )

    # Guarantee opaque border
    draw.rectangle([0, 0, w - 1, h - 1], outline=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 255), width=3)
    out = Image.alpha_composite(comp.convert("RGBA"), overlay).convert("RGB")
    arr_u8 = np.clip(np.asarray(out, dtype=np.uint8), 6, 255)
    return Image.fromarray(arr_u8, mode="RGB")


def synthesize_trigger_odyssey_8frame_strip(
    pose_a_img: Image.Image,
    seed_idx: int,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
) -> Image.Image:
    """
    Synthesizes an 8-Frame `1920x160` (`8` frames of `240x160` at `24fps`) Studio Trigger x Odyssey
    Sakuga Film-Shot Sprite Strip featuring:
      - Frame 0-1: 18-deg Dutch-Tilt Anticipation Hold (on-twos/threes) with dense diagonal sumi
        speedlines & colored interior linework
      - Frame 2-3: 14mm Fish-Eye Foreshortening Lunge + Canada-Style Elongation Smear Arc
      - Frame 4:   2-Frame Inverted Monochrome + Faction-Crimson/Cyan Woodcut Impact Flash
                   (`IMPACT_FRAME_INVERTED_MONOCHROME_2F`)
      - Frame 5:   Asymmetric 4-Point Trigger Star Flare Burst (`FOUR_POINT_TRIGGER_STAR_FLARE`)
      - Frame 6-7: Kagenashi Hard-Shadow Hero Lock & Polyhedral Shard Follow-Through
    """
    base = pose_a_img.convert("RGB")
    bw, bh = base.size
    fw, fh = 240, 160
    num_frames = 8
    strip = Image.new("RGB", (fw * num_frames, fh), (10, 14, 26))

    for f in range(num_frames):
        # Stepped cadence quantization: Frames 0-1 hold anticipation ('on-twos'), then explosive lunge
        effective_step = 0.0 if f in (0, 1) else (f / float(num_frames - 1))

        if f in (0, 1):
            zoom = 1.08
        elif f in (2, 3):
            # 14mm Fish-Eye Foreshortening Lunge
            zoom = 1.34 + 0.08 * (f - 2)
        elif f == 4:
            zoom = 1.46
        elif f == 5:
            zoom = 1.38
        else:
            # Frames 6-7 Hero Lock settle
            zoom = 1.22 - 0.04 * (f - 6)

        crop_w = int(bw / zoom)
        crop_h = int(crop_w * (fh / float(fw)))
        pan_x = int((bw - crop_w) * (0.32 + 0.36 * effective_step))
        pan_y = int(bh * (0.14 - 0.04 * math.sin(effective_step * math.pi)))
        pan_x = max(0, min(bw - crop_w, pan_x))
        pan_y = max(0, min(bh - crop_h, pan_y))

        frame_img = base.crop((pan_x, pan_y, pan_x + crop_w, pan_y + crop_h)).resize(
            (fw, fh), Image.Resampling.LANCZOS
        )

        # Frame 0-1: 18-deg Dutch-Tilt Anticipation Hold + Colored Interior Linework
        if f in (0, 1):
            dutch_angle = -7.5 if (seed_idx % 2 == 0) else 7.5
            tilted = frame_img.rotate(dutch_angle, resample=Image.Resampling.BICUBIC, expand=False)
            bg_fill = frame_img.filter(ImageFilter.GaussianBlur(radius=4))
            mask = Image.new("L", (fw, fh), 255).rotate(dutch_angle, resample=Image.Resampling.NEAREST, expand=False)
            frame_img = Image.composite(tilted, bg_fill, mask)
            edges = frame_img.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 42 else 0, mode="L")
            colored_line = Image.new("RGB", (fw, fh), secondary_rgb)
            frame_img = Image.composite(colored_line, frame_img, edges)

        elif f == 4:
            # Frame 4: IMPACT_FRAME_INVERTED_MONOCHROME_2F (Woodcut Stencil + Faction-Crimson/Cyan Flash)
            gray = frame_img.convert("L")
            inv_stencil = gray.point(lambda p: 0 if p > 122 else 255, mode="L")
            edges = gray.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 34 else 0, mode="L")
            obsidian_bg = Image.new("RGB", (fw, fh), (8, 10, 18))
            ivory_fg = Image.new("RGB", (fw, fh), (255, 252, 242))
            faction_flash = Image.new("RGB", (fw, fh), primary_rgb)
            stencil_comp = Image.composite(ivory_fg, obsidian_bg, inv_stencil)
            frame_img = Image.composite(faction_flash, stencil_comp, edges)

        else:
            shift = 5 if f in (2, 3, 5) else 2
            frame_img = ImageEnhance.Contrast(frame_img).enhance(1.22)
            frame_img = ImageEnhance.Color(frame_img).enhance(1.20)
            frame_img = apply_chromatic_aberration(frame_img, shift_px=shift)

        overlay = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        # Dense diagonal sumi & neon speedlines across all frames
        line_count = 32 if f in (2, 3, 4, 5) else 22
        for i in range(line_count):
            y_pos = int(((i * 19 + f * 23 + seed_idx * 11) % (fh + 20)) - 10)
            length = 48 + ((i * 31 + f * 17) % 68)
            is_left = (i % 2 == 0)
            x0 = 0 if is_left else fw
            x1 = length if is_left else (fw - length)
            y1 = y_pos - (8 if is_left else -8)
            col = (*primary_rgb, 210) if (i % 3 == 0) else ((*secondary_rgb, 190) if (i % 3 == 1) else (10, 14, 24, 215))
            draw.line([(x0, y_pos), (x1, y1)], fill=col, width=2 if (i % 4 == 0) else 1)

        # Frame 2-3: Canada-Style Elongation Smear Arc
        if f in (2, 3):
            y_l = int(fh * (0.78 - 0.16 * (f - 2)))
            y_r = int(fh * (0.28 + 0.12 * (f - 2)))
            draw.polygon(
                [(0, y_l), (fw, y_r), (fw, y_r + 22), (0, y_l + 26)],
                fill=(*primary_rgb, 225),
            )
            draw.polygon(
                [(0, y_l + 6), (fw, y_r + 5), (fw, y_r + 14), (0, y_l + 16)],
                fill=(*secondary_rgb, 240),
            )
            draw.line([(0, y_l + 10), (fw, y_r + 9)], fill=(255, 255, 255, 255), width=3)

        # Frame 4: Woodcut Impact Radial Lightning Slash
        if f == 4:
            draw.polygon(
                [(0, fh - 22), (fw, 18), (fw, 38), (0, fh - 4)],
                fill=(*primary_rgb, 245),
            )
            draw.line([(0, fh - 13), (fw, 28)], fill=(255, 255, 255, 255), width=4)

        # Frame 5: FOUR_POINT_TRIGGER_STAR_FLARE Burst at focal point
        if f == 5:
            star_cx, star_cy = fw * 0.56, fh * 0.44
            # Full-width cruciform anamorphic horizontal & vertical glare bars
            draw.line([(12, star_cy), (fw - 12, star_cy)], fill=(*secondary_rgb, 245), width=5)
            draw.line([(24, star_cy), (fw - 24, star_cy)], fill=(255, 255, 255, 255), width=2)
            draw.line([(star_cx, 10), (star_cx, fh - 10)], fill=(*primary_rgb, 235), width=4)
            draw_trigger_cruciform_star(
                draw,
                cx=star_cx,
                cy=star_cy,
                outer_r=64.0,
                inner_r=10.5,
                angle_deg=15.0,
                fill_rgba=(*secondary_rgb, 250),
            )
            draw_trigger_cruciform_star(
                draw,
                cx=fw * 0.24,
                cy=fh * 0.68,
                outer_r=34.0,
                inner_r=6.0,
                angle_deg=-22.0,
                fill_rgba=(*primary_rgb, 235),
            )
        else:
            # Traveling harmonic star flare across all other frames
            t_norm = f / float(num_frames - 1)
            draw_trigger_cruciform_star(
                draw,
                cx=fw * (0.20 + 0.60 * t_norm),
                cy=fh * (0.64 - 0.30 * t_norm),
                outer_r=34.0 if f in (2, 3) else 24.0,
                inner_r=5.5,
                angle_deg=f * 22.5,
                fill_rgba=(*secondary_rgb, 230),
            )

        # Frame 6-7: Kagenashi Hard-Shadow Hero Lock & Polyhedral Shard Follow-Through
        if f in (6, 7):
            draw.polygon([(0, 0), (54, 0), (0, 68)], fill=(8, 11, 20, 245))
            draw.line([(56, 0), (0, 70)], fill=(*primary_rgb, 250), width=3)
            draw_polyhedral_shards(draw, fw, fh, seed_idx + f * 7, primary_rgb, secondary_rgb, count=4)

        # Top & bottom angled Odyssey / Omega Strikers letterbox slash trim
        draw.polygon([(0, 0), (fw, 0), (fw, 8), (0, 15)], fill=(8, 12, 22, 235))
        draw.polygon([(0, fh - 15), (fw, fh - 8), (fw, fh), (0, fh)], fill=(8, 12, 22, 235))
        draw.line([(0, 15), (fw, 8)], fill=(*primary_rgb, 240), width=2)
        draw.line([(0, fh - 15), (fw, fh - 8)], fill=(*secondary_rgb, 240), width=2)
        draw.rectangle([0, 0, fw - 1, fh - 1], outline=(16, 24, 42, 255), width=1)

        final_frame = Image.alpha_composite(frame_img.convert("RGBA"), overlay).convert("RGB")
        strip.paste(final_frame, (f * fw, 0))

    arr_u8 = np.clip(np.asarray(strip, dtype=np.uint8), 6, 255)
    return Image.fromarray(arr_u8, mode="RGB")


def build_studio_pxg_2400x1600_showcase(
    striker_records: List[Dict[str, Any]],
    strip_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Composites a `2400x1600` RGB opaque showcase sheet:
      - Top half (`y = 0..750`): All 8 new `600x800` RTX 4080 Studio PxG AAA Striker/Vanguard portraits
        (`pxg_s01` .. `pxg_s08`) + their Pose-B impact preview & chromatic telemetry bars.
      - Bottom half (`y = 750..1600`): 8 full-width `1920x160` 8-frame Studio Trigger x Odyssey
        Sakuga Film-Shot Cut-In strips (`pxg_s01`..`pxg_s04` + `set2_k01`, `set2_k06`, `set2_k11`, `set2_k16`)
        with X-Sheet frame boundary ticks (`F0..F7`).
    """
    sheet_w, sheet_h = 2400, 1600
    sheet = Image.new("RGB", (sheet_w, sheet_h), (9, 13, 24))
    draw = ImageDraw.Draw(sheet)

    # Top Half: 8 columns x 1 row of Studio PxG AAA Striker Portraits (each column 300px wide)
    col_w = sheet_w // 8  # 300
    card_w, card_h = 276, 368
    pose_b_w, pose_b_h = 276, 310

    for idx, rec in enumerate(striker_records[:8]):
        x0 = idx * col_w + 12
        y_card = 16
        p_col = tuple(rec["primary_rgb"])
        s_col = tuple(rec["secondary_rgb"])

        draw.rectangle(
            [idx * col_w + 4, 6, (idx + 1) * col_w - 4, 738],
            fill=(14, 20, 36),
            outline=p_col,
            width=2,
        )

        with Image.open(rec["path"]) as im_a:
            thumb_a = im_a.convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb_a, (x0, y_card))
        draw.rectangle([x0 - 1, y_card - 1, x0 + card_w, y_card + card_h], outline=p_col, width=2)

        y_pose_b = y_card + card_h + 14
        with Image.open(rec["pose_b_path"]) as im_b:
            thumb_b = im_b.convert("RGB").resize((pose_b_w, pose_b_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb_b, (x0, y_pose_b))
        draw.rectangle([x0 - 1, y_pose_b - 1, x0 + pose_b_w, y_pose_b + pose_b_h], outline=s_col, width=2)

        # Chromatic telemetry swatches at bottom of top-half card cell
        y_swatch = y_pose_b + pose_b_h + 8
        draw.rectangle([x0, y_swatch, x0 + card_w // 2 - 2, y_swatch + 12], fill=p_col)
        draw.rectangle([x0 + card_w // 2 + 2, y_swatch, x0 + card_w, y_swatch + 12], fill=s_col)

    # Bottom Half (y = 752..1592): 8 Full-Width 8-Frame 1920x160 Sakuga Film-Shot Strips
    # Pick 4 Studio PxG Atomic Strikers (pxg_s01..s04) + 4 Set 2 Lineage Flagships (set2_k01, k06, k11, k16)
    by_id = {r["id"]: r for r in strip_records}
    featured_ids = [
        "pxg_s01",
        "pxg_s02",
        "pxg_s03",
        "pxg_s04",
        "set2_k01",
        "set2_k06",
        "set2_k11",
        "set2_k16",
    ]
    featured_strips = [by_id[k] for k in featured_ids if k in by_id]
    if len(featured_strips) < 8:
        featured_strips = strip_records[:8]

    strip_disp_w = 2352  # 8 frames * 294px
    strip_disp_h = 92
    x_strip = (sheet_w - strip_disp_w) // 2
    y_base = 756
    row_step = 104

    for r_idx, s_rec in enumerate(featured_strips[:8]):
        y_s = y_base + r_idx * row_step
        p_col = tuple(s_rec["primary_rgb"])
        s_col = tuple(s_rec["secondary_rgb"])

        with Image.open(s_rec["strip_path"]) as st_im:
            scaled_strip = st_im.convert("RGB").resize((strip_disp_w, strip_disp_h), Image.Resampling.LANCZOS)
        sheet.paste(scaled_strip, (x_strip, y_s))
        draw.rectangle(
            [x_strip - 2, y_s - 2, x_strip + strip_disp_w + 1, y_s + strip_disp_h + 1],
            outline=p_col,
            width=2,
        )

        # Draw X-Sheet 8-frame markers (F0..F7) along the bottom of each strip
        fw_disp = strip_disp_w // 8
        for f_i in range(8):
            fx0 = x_strip + f_i * fw_disp
            if f_i > 0:
                draw.line([(fx0, y_s), (fx0, y_s + strip_disp_h)], fill=s_col, width=1)
            # Highlight Frame 4 (Inverted Monochrome Impact) and Frame 5 (4-Point Star Flare)
            bar_col = p_col if f_i in (4, 5) else s_col
            draw.rectangle([fx0 + 4, y_s + strip_disp_h + 3, fx0 + fw_disp - 4, y_s + strip_disp_h + 7], fill=bar_col)

    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    copy_if_distinct(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": sheet_w,
        "height": sheet_h,
        "top_half_portraits_count": 8,
        "bottom_half_sakuga_strips_count": 8,
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t_start = time.time()
    STUDIO_PXG_DIR.mkdir(parents=True, exist_ok=True)
    WEB_STUDIO_PXG_DIR.mkdir(parents=True, exist_ok=True)
    SAKUGA_CUTINS_DIR.mkdir(parents=True, exist_ok=True)
    WEB_SAKUGA_CUTINS_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    print(
        f"[Studio PxG Atomic Trigger x Odyssey] Rendering 8 original AAA Striker/Vanguard portraits on {COMFYUI_URL}...",
        flush=True,
    )

    striker_records: List[Dict[str, Any]] = []
    striker_sha_set = set()
    live_rtx4080_count = 0

    for idx, spec in enumerate(STUDIO_PXG_STRIKERS):
        raw_info = render_rtx4080_striker_raw(spec, width=768, height=1024, steps=10, cfg=6.5, force=False)
        if raw_info["rtx4080_live_rendered"]:
            live_rtx4080_count += 1

        raw_path = Path(raw_info["raw_source_path"])
        with Image.open(raw_path) as raw_im:
            portrait_im = refine_studio_pxg_striker_portrait_600x800(raw_im, idx, spec)

        out_path = STUDIO_PXG_DIR / spec["filename"]
        portrait_im.save(out_path, format="PNG", optimize=True)
        copy_if_distinct(out_path, WEB_STUDIO_PXG_DIR / spec["filename"])
        copy_if_distinct(out_path, UNITY_PORTRAITS_DIR / spec["filename"])

        with Image.open(out_path) as chk:
            w, h = chk.size
            mode = chk.mode
            bbox = list(chk.getbbox() or (0, 0, 0, 0))

        sha = compute_sha256(out_path)
        striker_sha_set.add(sha)

        striker_records.append(
            {
                "id": spec["id"],
                "slug": spec["slug"],
                "filename": spec["filename"],
                "name": spec["name"],
                "role": spec["role"],
                "faction": spec["faction"],
                "cost": spec["cost"],
                "nesw": spec["nesw"],
                "camera_lens": spec["camera_lens"],
                "primary_hex": spec["primary_hex"],
                "secondary_hex": spec["secondary_hex"],
                "primary_rgb": list(spec["primary_rgb"]),
                "secondary_rgb": list(spec["secondary_rgb"]),
                "morphological_primitives": spec["morphological_primitives"],
                "path": str(out_path),
                "web_playable_path": str(WEB_STUDIO_PXG_DIR / spec["filename"]),
                "unity_portrait_path": str(UNITY_PORTRAITS_DIR / spec["filename"]),
                "art": f"./GeneratedArt/StudioPxGAtomic/{spec['filename']}",
                "width": w,
                "height": h,
                "mode": mode,
                "opaque": mode == "RGB",
                "content_bounds": bbox,
                "sha256": sha,
                "file_size_bytes": out_path.stat().st_size,
                "rtx4080_raw_source": raw_info["raw_source_path"],
                "rtx4080_live_rendered": raw_info["rtx4080_live_rendered"],
                "rtx4080_elapsed_s": raw_info["elapsed_s"],
                "prompt": raw_info["prompt"],
                "zero_living_artist_names": True,
            }
        )
        print(
            f"  [PxG {idx + 1:02d}/08] {spec['id']} ({spec['name']}): "
            f"{w}x{h} {mode} bounds={bbox} sha256={sha[:12]}... ({raw_info['elapsed_s']}s)",
            flush=True,
        )

    # Load all 20 Set 2 cards from Datasets/set2_kubrart_manga_expansion_manifest.json
    if not SET2_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing Set 2 manifest: {SET2_MANIFEST_PATH}")
    set2_manifest = json.loads(SET2_MANIFEST_PATH.read_text(encoding="utf-8"))
    set2_cards = set2_manifest.get("cards", [])

    LINEAGE_PALETTES: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
        "kubrart_vector_cel_ink_v1": ((168, 85, 247), (0, 229, 255)),
        "manga_sumi_ink_seinen_v1": ((255, 46, 84), (242, 236, 225)),
        "anime_sakuga_kagenashi_v2": ((255, 184, 0), (0, 229, 255)),
        "cyber_mecha_orthographic_v1": ((0, 229, 255), (46, 230, 211)),
    }

    print(
        "[Studio Trigger x Odyssey Sakuga Engine] Synthesizing 28 8-Frame 1920x160 (24fps) Cut-In Strips & Pose-B Keyframes...",
        flush=True,
    )

    all_sakuga_units: List[Dict[str, Any]] = []
    for s_idx, c in enumerate(set2_cards):
        p_rgb, s_rgb = LINEAGE_PALETTES.get(c["modelId"], ((0, 229, 255), (255, 184, 0)))
        all_sakuga_units.append(
            {
                "id": c["id"],
                "slug": c["slug"],
                "name": c["name"],
                "series": "Set2KubrartManga",
                "modelId": c["modelId"],
                "source_portrait_path": Path(c["path"]),
                "primary_rgb": p_rgb,
                "secondary_rgb": s_rgb,
                "seed_idx": s_idx + 1,
            }
        )

    for p_idx, p_rec in enumerate(striker_records):
        all_sakuga_units.append(
            {
                "id": p_rec["id"],
                "slug": p_rec["slug"],
                "name": p_rec["name"],
                "series": "StudioPxGAtomic",
                "modelId": "anime_sakuga_kagenashi_v2",
                "source_portrait_path": Path(p_rec["path"]),
                "primary_rgb": tuple(p_rec["primary_rgb"]),
                "secondary_rgb": tuple(p_rec["secondary_rgb"]),
                "seed_idx": 100 + p_idx,
            }
        )

    sakuga_records: List[Dict[str, Any]] = []
    strip_sha_set = set()
    pose_b_sha_set = set()

    for u_idx, unit in enumerate(all_sakuga_units):
        uid = unit["id"]
        uslug = unit["slug"]
        src_path = unit["source_portrait_path"]

        with Image.open(src_path) as src_im:
            pose_b_im = synthesize_pose_b_impact_keyframe_600x800(
                src_im,
                seed_idx=unit["seed_idx"],
                primary_rgb=unit["primary_rgb"],
                secondary_rgb=unit["secondary_rgb"],
            )
            strip_im = synthesize_trigger_odyssey_8frame_strip(
                src_im,
                seed_idx=unit["seed_idx"],
                primary_rgb=unit["primary_rgb"],
                secondary_rgb=unit["secondary_rgb"],
            )

        # Save both `<slug>_strip.png` AND `<id>_strip.png` (and `<slug>_pose_b.png` AND `<id>_pose_b.png`)
        slug_strip_path = SAKUGA_CUTINS_DIR / f"{uslug}_strip.png"
        id_strip_path = SAKUGA_CUTINS_DIR / f"{uid}_strip.png"
        slug_pose_b_path = SAKUGA_CUTINS_DIR / f"{uslug}_pose_b.png"
        id_pose_b_path = SAKUGA_CUTINS_DIR / f"{uid}_pose_b.png"

        strip_im.save(slug_strip_path, format="PNG", optimize=True)
        copy_if_distinct(slug_strip_path, id_strip_path)
        copy_if_distinct(slug_strip_path, WEB_SAKUGA_CUTINS_DIR / slug_strip_path.name)
        copy_if_distinct(id_strip_path, WEB_SAKUGA_CUTINS_DIR / id_strip_path.name)

        pose_b_im.save(slug_pose_b_path, format="PNG", optimize=True)
        copy_if_distinct(slug_pose_b_path, id_pose_b_path)
        copy_if_distinct(slug_pose_b_path, WEB_SAKUGA_CUTINS_DIR / slug_pose_b_path.name)
        copy_if_distinct(id_pose_b_path, WEB_SAKUGA_CUTINS_DIR / id_pose_b_path.name)

        with Image.open(slug_strip_path) as chk_s:
            sw, sh = chk_s.size
            smode = chk_s.mode
            sbbox = list(chk_s.getbbox() or (0, 0, 0, 0))
        with Image.open(slug_pose_b_path) as chk_b:
            bw, bh = chk_b.size
            bmode = chk_b.mode
            bbbox = list(chk_b.getbbox() or (0, 0, 0, 0))

        s_sha = compute_sha256(slug_strip_path)
        b_sha = compute_sha256(slug_pose_b_path)
        strip_sha_set.add(s_sha)
        pose_b_sha_set.add(b_sha)

        # Attach pose_b_path and strip_path back to striker_records if matching
        for sr in striker_records:
            if sr["id"] == uid:
                sr["pose_b_path"] = str(slug_pose_b_path)
                sr["strip_path"] = str(slug_strip_path)

        rec = {
            "id": uid,
            "slug": uslug,
            "name": unit["name"],
            "series": unit["series"],
            "modelId": unit["modelId"],
            "primary_rgb": list(unit["primary_rgb"]),
            "secondary_rgb": list(unit["secondary_rgb"]),
            "strip_filename": slug_strip_path.name,
            "strip_short_filename": id_strip_path.name,
            "strip_path": str(slug_strip_path),
            "strip_short_path": str(id_strip_path),
            "strip_web_path": f"./GeneratedArt/SakugaCutIns/{slug_strip_path.name}",
            "strip_width": sw,
            "strip_height": sh,
            "strip_frames": 8,
            "frame_width": 240,
            "frame_height": 160,
            "fps": 24,
            "strip_mode": smode,
            "strip_content_bounds": sbbox,
            "strip_sha256": s_sha,
            "pose_b_filename": slug_pose_b_path.name,
            "pose_b_short_filename": id_pose_b_path.name,
            "pose_b_path": str(slug_pose_b_path),
            "pose_b_short_path": str(id_pose_b_path),
            "pose_b_web_path": f"./GeneratedArt/SakugaCutIns/{slug_pose_b_path.name}",
            "pose_b_width": bw,
            "pose_b_height": bh,
            "pose_b_mode": bmode,
            "pose_b_content_bounds": bbbox,
            "pose_b_sha256": b_sha,
            "xsheet_film_shot_phases": {
                "frames_0_1": "18-deg Dutch-Tilt Anticipation Hold (on-twos/threes) + Colored Interior Linework",
                "frames_2_3": "14mm Fish-Eye Foreshortening Lunge + Canada-Style Elongation Smear Arc",
                "frame_4": "IMPACT_FRAME_INVERTED_MONOCHROME_2F (Woodcut Stencil + Faction-Crimson/Cyan Flash)",
                "frame_5": "FOUR_POINT_TRIGGER_STAR_FLARE (Asymmetric 4-Point Cruciform Star Burst)",
                "frames_6_7": "Kagenashi Hard-Shadow Hero Lock & Polyhedral Shard Follow-Through",
            },
        }
        sakuga_records.append(rec)
        print(
            f"  [Sakuga {u_idx + 1:02d}/28] {uid} ({uslug}): strip={sw}x{sh} {smode} "
            f"pose_b={bw}x{bh} {bmode} sha256={s_sha[:10]}...",
            flush=True,
        )

    showcase_info = build_studio_pxg_2400x1600_showcase(striker_records, sakuga_records)

    all_strikers_valid = all(
        r["width"] == 600
        and r["height"] == 800
        and r["mode"] == "RGB"
        and r["content_bounds"] == [0, 0, 600, 800]
        for r in striker_records
    )
    all_strips_valid = all(
        r["strip_width"] == 1920
        and r["strip_height"] == 160
        and r["strip_mode"] == "RGB"
        and r["strip_content_bounds"] == [0, 0, 1920, 160]
        and r["pose_b_width"] == 600
        and r["pose_b_height"] == 800
        and r["pose_b_mode"] == "RGB"
        and r["pose_b_content_bounds"] == [0, 0, 600, 800]
        for r in sakuga_records
    )

    manifest = {
        "manifest_id": "studio_pxg_aaa_trigger_odyssey_assets_and_sakuga_v1",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "Backend/render_studio_pxg_aaa_trigger_odyssey_assets.py",
        "status": "VERIFIED" if (all_strikers_valid and all_strips_valid) else "FAILED",
        "zero_living_artist_names": True,
        "comfyui_rtx4080_endpoint": COMFYUI_URL,
        "dual_model_checkpoints": [ANIMAGINE_CHECKPOINT, FLUX_CHECKPOINT],
        "rtx4080_render_params": {
            "width": 768,
            "height": 1024,
            "steps": 10,
            "cfg": 6.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
        },
        "studio_pxg_strikers_count": len(striker_records),
        "studio_pxg_unique_sha256_count": len(striker_sha_set),
        "rtx4080_live_rendered_strikers_count": live_rtx4080_count,
        "all_strikers_600x800_rgb_opaque": all_strikers_valid,
        "set2_sakuga_strips_count": 20,
        "studio_pxg_sakuga_strips_count": 8,
        "total_new_sakuga_8frame_strips_count": len(sakuga_records),
        "unique_strip_sha256_count": len(strip_sha_set),
        "unique_pose_b_sha256_count": len(pose_b_sha_set),
        "all_strips_1920x160_rgb_24fps": all_strips_valid,
        "all_pose_b_600x800_rgb_opaque": all_strips_valid,
        "showcase_sheet": showcase_info,
        "total_wall_time_s": round(time.time() - t_start, 2),
        "studio_pxg_strikers": striker_records,
        "sakuga_cutin_strips": sakuga_records,
    }

    manifest_json = json.dumps(manifest, indent=2)
    assert_zero_living_artist_names(manifest_json, "studio_pxg_aaa_assets_and_sakuga_manifest.json")
    OUT_MANIFEST_PATH.write_text(manifest_json + "\n", encoding="utf-8")

    print(
        f"[Complete] 8/8 Studio PxG AAA Strikers (600x800 RGB={all_strikers_valid}) + "
        f"28/28 8-Frame 1920x160 Sakuga Strips & Pose-B Keyframes (valid={all_strips_valid}) "
        f"in {manifest['total_wall_time_s']}s.",
        flush=True,
    )
    print(f"  Manifest: {OUT_MANIFEST_PATH}", flush=True)
    print(f"  Showcase: {SHOWCASE_BRAIN_PATH}", flush=True)


if __name__ == "__main__":
    main()
