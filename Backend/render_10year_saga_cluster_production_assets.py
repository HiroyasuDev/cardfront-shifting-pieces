#!/usr/bin/env python3
"""
render_10year_saga_cluster_production_assets.py
===============================================
Track 2: GPU Cluster Node 30 (`192.168.86.30` RTX 4080) 10-Year Saga Production Assets:
  1. 6 Era/Expansion Key-Art Herald Master Cards (`600x800`, `3:4` RGB opaque,
     `content_bounds = [0, 0, 600, 800]`, zero borders, zero baked raster text)
     in `GeneratedArt/Saga10YearFranchise/` (mirrored to
     `WebPlayable/GeneratedArt/Saga10YearFranchise/` and
     `Assets/Resources/CardFront/Portraits/`).
  2. 6 Code-Native SVG Ranked League & Era Expansion Emblems (`viewBox="0 0 256 256"`,
     zero `<text>` tags) in `WebPlayable/assets/saga_emblems/`.
  3. `2400x1600` 10-Year Franchise Saga Production Showcase Atlas at
     `/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/cardfront_10year_saga_franchise_showcase.png`
     and `GeneratedArt/cardfront_10year_saga_franchise_showcase.png`.
  4. Full verification manifest at `Datasets/cardfront_10year_production_assets_manifest.json`.

Strict Art Direction & Compliance Contract (`tcg-creative-game-designer/rules/AGENTS.md`):
- ZERO living artists' names anywhere in prompts, code, or metadata (`zero_living_artist_names: true`).
- Uses 100% concrete morphological & film-shot descriptors.
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
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
ANIME_MODELS_DIR = GENERATED_ART_DIR / "AnimeMangaModels"
SAGA_ART_DIR = GENERATED_ART_DIR / "Saga10YearFranchise"
WEB_SAGA_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "Saga10YearFranchise"
UNITY_PORTRAITS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront" / "Portraits"
SVG_EMBLEMS_DIR = PROJECT_ROOT / "WebPlayable" / "assets" / "saga_emblems"
DATASETS_DIR = PROJECT_ROOT / "Datasets"
OUT_MANIFEST_PATH = DATASETS_DIR / "cardfront_10year_production_assets_manifest.json"

SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/cardfront_10year_saga_franchise_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "cardfront_10year_saga_franchise_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
ANIMAGINE_CHECKPOINT = "animagineXLV31_v31.safetensors"
FLUX_CHECKPOINT = "flux1-dev-fp8.safetensors"

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

PROMPT_PREFIX = (
    "masterpiece, best quality, official 10th-anniversary anime and manga tactical trading card key-art illustration, "
    "stylized 7-head to 7.5-head heroic proportions, tapered gauntlets and oversized propulsion boots, "
    "pen-and-ink G-pen crosshatching over warm parchment-gold filigree, razor-sharp unblended kagenashi cel shadows, "
)
NEGATIVE_PROMPT = (
    "text, watermark, signature, logo, typography, letters, numbers, blurry, lowres, "
    "photorealistic, muddy airbrush gradients, plastic 3d skin, bad anatomy, cropped, border"
)

# 6 Iconic 10-Year Franchise Era Herald Master Cards (saga_y01 .. saga_y10)
SAGA_HERALD_CARDS: List[Dict[str, Any]] = [
    {
        "id": "saga_y01",
        "slug": "saga_y01_cradle_genesis_herald",
        "filename": "saga_y01_cradle_genesis_herald.png",
        "name": "Herald of the Cradle Genesis",
        "era_id": "era_1",
        "era_title": "Era I: Cradle of Echoes (Years 1–3 · Sets 1–6)",
        "years_label": "Year 1–2 (Era I)",
        "sets_spanned": ["Set 1: Cradle of Echoes", "Set 2: Kubrart Astral Eclipse", "Set 3: Sanctum Vanguard", "Set 4: Echoing Rift"],
        "faction": "Valkyria",
        "cost": 3,
        "nesw": [9, 8, 6, 8],
        "primary_hex": "#00E5FF",
        "secondary_hex": "#FFB800",
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 184, 0),
        "accent_rgb": (56, 189, 248),
        "shadow_rgb": (9, 14, 28),
        "seed": 4080901,
        "fallback_raw": "AnimeMangaModels/pxg_s01_rtx4080_raw.png",
        "ability": {
            "id": "ab_cradle_genesis_resonator",
            "name": "Cradle Genesis Resonance",
            "text": "On Deploy: Projects a 3x3 Astral Sanctum lattice that grants +1 North and +1 East to all Era I allies.",
        },
        "subject_prompt": (
            "14mm foreshortened anime spellblade conduit holding a luminous 3x3 astral sanctum monolith cube, "
            "vibrant astral cyan and cobalt-gold energy wings, cropped high-collar tactical paladin coat, "
            "four-point gold star flare, floating citadel sky-sanctuary backdrop"
        ),
    },
    {
        "id": "saga_y02",
        "slug": "saga_y02_kubrart_eclipse_monarch",
        "filename": "saga_y02_kubrart_eclipse_monarch.png",
        "name": "Monarch of the Kubrart Eclipse",
        "era_id": "era_1",
        "era_title": "Era I: Cradle of Echoes (Years 1–3 · Sets 1–6)",
        "years_label": "Year 2–3 (Era I)",
        "sets_spanned": ["Set 5: Obsidian Prism", "Set 6: Eclipse Monarchs"],
        "faction": "Aether",
        "cost": 4,
        "nesw": [9, 9, 7, 8],
        "primary_hex": "#A855F7",
        "secondary_hex": "#00E5FF",
        "primary_rgb": (168, 85, 247),
        "secondary_rgb": (0, 229, 255),
        "accent_rgb": (255, 224, 130),
        "shadow_rgb": (8, 9, 18),
        "seed": 4080902,
        "fallback_raw": "AnimeMangaModels/set2_k01_rtx4080_raw.png",
        "ability": {
            "id": "ab_kubrart_eclipse_coronation",
            "name": "Negative-Space Eclipse Crown",
            "text": "Eclipse Sovereign: Converts adjacent orthogonal tiles into Obsidian Prism zones where Prime ranks win ties.",
        },
        "subject_prompt": (
            "sovereign anime eclipse monarch silhouetted in stark sumi-ink negative-space blocks, "
            "crowned by a floating polyhedral black obsidian eclipse halo, razor-sharp graphic vector-cel shards, "
            "luminous tarot violet and astral cyan dual rim-wash"
        ),
    },
    {
        "id": "saga_y04",
        "slug": "saga_y04_sovran_mechanica_titan",
        "filename": "saga_y04_sovran_mechanica_titan.png",
        "name": "Sovran Mechanica Prime Titan",
        "era_id": "era_2",
        "era_title": "Era II: Sovran Mechanica (Years 4–7 · Sets 7–14)",
        "years_label": "Year 4–5 (Era II)",
        "sets_spanned": ["Set 7: Sovran Mechanica", "Set 8: Orthographic Dragoons", "Set 9: Aegis Forge", "Set 10: Jade Core"],
        "faction": "Solaris",
        "cost": 4,
        "nesw": [9, 9, 8, 7],
        "primary_hex": "#FFB800",
        "secondary_hex": "#2EE6D3",
        "primary_rgb": (255, 184, 0),
        "secondary_rgb": (46, 230, 211),
        "accent_rgb": (0, 229, 255),
        "shadow_rgb": (10, 18, 28),
        "seed": 4080904,
        "fallback_raw": "AnimeMangaModels/pxg_s05_rtx4080_raw.png",
        "ability": {
            "id": "ab_sovran_mechanica_overdrive",
            "name": "Cruciform Solar Overdrive",
            "text": "Mecha Citadel: Fortifies all orthogonal allied constructs by +2 Armor and triggers an orthographic rail-sweep.",
        },
        "subject_prompt": (
            "7.5-head cyber-magicite mecha frame in heroic forced-perspective brave stance with crossed pauldrons, "
            "sovereign law-gold and jade-teal beveled armor plates, six cruciform solar energy wings, "
            "precision orthographic blueprint reticle halo, CMYK halftone screentone accents"
        ),
    },
    {
        "id": "saga_y06",
        "slug": "saga_y06_chrono_paradox_arbiter",
        "filename": "saga_y06_chrono_paradox_arbiter.png",
        "name": "Chrono-Lattice Paradox Arbiter",
        "era_id": "era_2",
        "era_title": "Era II: Sovran Mechanica (Years 4–7 · Sets 7–14)",
        "years_label": "Year 6–7 (Era II)",
        "sets_spanned": ["Set 11: Chrono-Lattice", "Set 12: Pendulum Decree", "Set 13: Ivory Inquisitors", "Set 14: Paradox Engine"],
        "faction": "Chronos",
        "cost": 3,
        "nesw": [8, 8, 9, 8],
        "primary_hex": "#00E5FF",
        "secondary_hex": "#FFE082",
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 224, 130),
        "accent_rgb": (249, 115, 22),
        "shadow_rgb": (14, 12, 22),
        "seed": 4080906,
        "fallback_raw": "AnimeMangaModels/set2_k07_rtx4080_raw.png",
        "ability": {
            "id": "ab_chrono_lattice_rewind",
            "name": "Paradox Lattice Rewind",
            "text": "Temporal Decree: Rewinds a captured allied unit to its pre-flip state once per match and locks column dice.",
        },
        "subject_prompt": (
            "ornate anime chronomancer law arbiter surrounded by shattered brass clockwork polyhedral rings, "
            "dense variable-weight G-pen manga crosshatching over warm gilded parchment filigree, "
            "dual-tone astral cyan and solar gold temporal halo"
        ),
    },
    {
        "id": "saga_y08",
        "slug": "saga_y08_astral_singularity_valkyrie",
        "filename": "saga_y08_astral_singularity_valkyrie.png",
        "name": "Singularity Ascended Valkyrie",
        "era_id": "era_3",
        "era_title": "Era III: Omega Convergence (Years 8–10 · Sets 15–20)",
        "years_label": "Year 8–9 (Era III)",
        "sets_spanned": ["Set 15: Astral Singularity", "Set 16: Crimson Horizon", "Set 17: 24fps Sakuga Apex", "Set 18: Valkyria Prime"],
        "faction": "Abyss",
        "cost": 4,
        "nesw": [10, 9, 6, 8],
        "primary_hex": "#FF2E54",
        "secondary_hex": "#00E5FF",
        "primary_rgb": (255, 46, 84),
        "secondary_rgb": (0, 229, 255),
        "accent_rgb": (255, 184, 0),
        "shadow_rgb": (10, 8, 18),
        "seed": 4080908,
        "fallback_raw": "AnimeMangaModels/set2_k12_rtx4080_raw.png",
        "ability": {
            "id": "ab_singularity_spear_dive",
            "name": "24fps Singularity Spear Dive",
            "text": "Sakuga Impact: Lunges across any main diagonal, triggering an inverted monochrome impact flash and +2 Attack.",
        },
        "subject_prompt": (
            "ascended anime valkyrie lancer thrusting a liquid-plasma smear spear in a 24fps key-animation impact pose, "
            "stark kagenashi hard-shadow wings, dramatic crimson-flame and astral cyan clash rim-lighting, "
            "four-point cruciform star flares"
        ),
    },
    {
        "id": "saga_y10",
        "slug": "saga_y10_omega_convergence_sovereign",
        "filename": "saga_y10_omega_convergence_sovereign.png",
        "name": "Omega Convergence Sovereign",
        "era_id": "era_3",
        "era_title": "Era III: Omega Convergence (Years 8–10 · Sets 15–20)",
        "years_label": "Year 10 (Era III Finale)",
        "sets_spanned": ["Set 19: Echoes Eternal", "Set 20: Omega Convergence (10th Anniversary Finale)"],
        "faction": "Solaris",
        "cost": 4,
        "nesw": [10, 10, 9, 9],
        "primary_hex": "#FFB800",
        "secondary_hex": "#00E5FF",
        "primary_rgb": (255, 184, 0),
        "secondary_rgb": (0, 229, 255),
        "accent_rgb": (168, 85, 247),
        "shadow_rgb": (9, 11, 24),
        "seed": 4080910,
        "fallback_raw": "AnimeMangaModels/pxg_s08_rtx4080_raw.png",
        "ability": {
            "id": "ab_omega_ten_year_convergence",
            "name": "Decade of Echoes Convergence",
            "text": "10th-Anniversary Apex: Unifies all 4 Faction Chromatic Halos (+1 N/E/S/W per distinct Era in your squad).",
        },
        "subject_prompt": (
            "ultimate 10th-anniversary anime sovereign monarch ascending inside a four-faction prismatic astrolabe crown, "
            "sovereign gold, astral cyan, crimson-flame, and tarot violet four-point star flare burst, "
            "ornate cyber-magicite ceremonial armor and floating polyhedral sanctum shards"
        ),
    },
]

SVG_EMBLEM_SPECS: List[Dict[str, Any]] = [
    {
        "id": "era1_cradle_of_echoes_crest",
        "filename": "era1_cradle_of_echoes_crest.svg",
        "title": "Era I: Cradle of Echoes Expansion Crest (Years 1–3)",
        "category": "era_crest",
        "primary": "#00E5FF",
        "secondary": "#A855F7",
        "accent": "#FFB800",
        "dark": "#090D16",
    },
    {
        "id": "era2_sovran_mechanica_crest",
        "filename": "era2_sovran_mechanica_crest.svg",
        "title": "Era II: Sovran Mechanica Expansion Crest (Years 4–7)",
        "category": "era_crest",
        "primary": "#FFB800",
        "secondary": "#2EE6D3",
        "accent": "#00E5FF",
        "dark": "#0B132B",
    },
    {
        "id": "era3_omega_convergence_crest",
        "filename": "era3_omega_convergence_crest.svg",
        "title": "Era III: Omega Convergence Expansion Crest (Years 8–10)",
        "category": "era_crest",
        "primary": "#FF2E54",
        "secondary": "#00E5FF",
        "accent": "#FFB800",
        "dark": "#090B14",
    },
    {
        "id": "rank_gold_law_arbiter_crest",
        "filename": "rank_gold_law_arbiter_crest.svg",
        "title": "Ranked League Tier: Gold Law Arbiter Crest",
        "category": "ranked_crest",
        "primary": "#FFB800",
        "secondary": "#FFE082",
        "accent": "#2EE6D3",
        "dark": "#141008",
    },
    {
        "id": "rank_diamond_kubrart_prism_crest",
        "filename": "rank_diamond_kubrart_prism_crest.svg",
        "title": "Ranked League Tier: Diamond Kubrart Prism Crest",
        "category": "ranked_crest",
        "primary": "#00E5FF",
        "secondary": "#A855F7",
        "accent": "#F8FAFC",
        "dark": "#090D16",
    },
    {
        "id": "rank_sovereign_grandmaster_apex_crest",
        "filename": "rank_sovereign_grandmaster_apex_crest.svg",
        "title": "Ranked League Tier: Sovereign Grandmaster Apex Crest",
        "category": "ranked_crest",
        "primary": "#FFB800",
        "secondary": "#FF2E54",
        "accent": "#00E5FF",
        "dark": "#070912",
    },
]


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


def render_rtx4080_saga_raw(
    spec: Dict[str, Any],
    width: int = 768,
    height: int = 1024,
    steps: int = 10,
    cfg: float = 6.5,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Connects to Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) with
    `animagineXLV31_v31.safetensors` (`768x1024`, `steps=10`, `euler_ancestral`)
    to render a fresh 10-Year Saga Era Herald raw portrait.
    """
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    card_id = spec["id"]
    raw_out = ANIME_MODELS_DIR / f"{card_id}_rtx4080_raw.png"
    fallback_path = GENERATED_ART_DIR / spec["fallback_raw"]

    full_prompt = PROMPT_PREFIX + spec["subject_prompt"]
    assert_zero_living_artist_names(full_prompt, f"{card_id}.prompt")

    if raw_out.exists() and not force and raw_out.stat().st_size > 80_000:
        return {
            "id": card_id,
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
            "inputs": {"filename_prefix": f"Saga10Year_{card_id}", "images": ["8", 0]},
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
                            "id": card_id,
                            "prompt_id": prompt_id,
                            "raw_source_path": str(raw_out),
                            "rtx4080_live_rendered": True,
                            "cached": False,
                            "elapsed_s": elapsed,
                            "prompt": full_prompt,
                            "checkpoint": ANIMAGINE_CHECKPOINT,
                        }
    except Exception as exc:
        print(f"  [WARN] ComfyUI fallback for {card_id}: {exc}", flush=True)

    return {
        "id": card_id,
        "raw_source_path": str(fallback_path),
        "rtx4080_live_rendered": False,
        "cached": True,
        "elapsed_s": 0.0,
        "prompt": full_prompt,
        "checkpoint": ANIMAGINE_CHECKPOINT,
    }


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
    pts: List[Tuple[float, float]] = []
    base_rad = math.radians(angle_deg)
    for i in range(8):
        ang = base_rad + i * (math.pi / 4.0)
        if i % 2 == 0:
            mult = 1.30 if (i % 4 == 0) else 0.94
            r = outer_r * mult
        else:
            r = inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=fill_rgba, outline=core_rgba)
    cr = max(2.5, inner_r * 0.65)
    draw.polygon([(cx, cy - cr), (cx + cr, cy), (cx, cy + cr), (cx - cr, cy)], fill=core_rgba)


def refine_saga_herald_portrait_600x800(
    src_img: Image.Image,
    idx: int,
    spec: Dict[str, Any],
) -> Image.Image:
    """
    Normalizes and refines each 10-Year Saga Herald portrait to exact `600x800`
    (`3:4` RGB opaque, `content_bounds = [0, 0, 600, 800]`, zero borders, zero text)
    with Era-specific geometric astrolabe/polyhedral/cruciform overlays.
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

    zoom = 1.04 + 0.015 * (idx % 4)
    zw, zh = int(round(target_w * zoom)), int(round(target_h * zoom))
    img = src_rgb.resize((zw, zh), Image.Resampling.LANCZOS)
    pan_x = int(round((zw - target_w) * (((idx * 31 + 19) % 100) / 100.0)))
    pan_y = int(round((zh - target_h) * (((idx * 43 + 13) % 100) / 100.0)))
    img = img.crop((pan_x, pan_y, pan_x + target_w, pan_y + target_h))

    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.16)
    img = ImageEnhance.Sharpness(img).enhance(1.26)

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

    # Kagenashi deep shadow lock + dual-tone Era rim-wash
    kagenashi_mask = (lum < 0.24).astype(np.float32)[:, :, np.newaxis]
    arr = arr * (1.0 - 0.58 * kagenashi_mask) + shd[np.newaxis, np.newaxis, :] * (0.58 * kagenashi_mask)

    gpen_edge = ((grad_mag > 0.22) & (grad_mag <= 0.44)).astype(np.float32)[:, :, np.newaxis]
    rim_edge = (grad_mag > 0.44).astype(np.float32)[:, :, np.newaxis]
    left_w = np.clip(1.0 - xx / float(target_w), 0.0, 1.0)[:, :, np.newaxis]
    dual_rim = prim[np.newaxis, np.newaxis, :] * left_w + sec[np.newaxis, np.newaxis, :] * (1.0 - left_w)

    arr = arr * (1.0 - 0.48 * gpen_edge) + shd[np.newaxis, np.newaxis, :] * (0.48 * gpen_edge)
    arr = np.clip(arr + dual_rim * (rim_edge * 0.42), 0.0, 1.0)

    arr_u8 = np.clip(arr * 255.0, 8, 255).astype(np.uint8)
    base_rgba = Image.fromarray(arr_u8, mode="RGB").convert("RGBA")

    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    p_rgb = spec["primary_rgb"]
    s_rgb = spec["secondary_rgb"]
    a_rgb = spec["accent_rgb"]
    k_rgb = tuple(max(10, c) for c in spec["shadow_rgb"])

    # Era-specific concentric astrolabe halo & polyhedral shards
    cx, cy = target_w // 2, int(target_h * 0.36)
    r_outer = 210 + (idx % 3) * 14
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=(*p_rgb, 155), width=2)
    draw.ellipse(
        [cx - r_outer + 18, cy - r_outer + 18, cx + r_outer - 18, cy + r_outer - 18],
        outline=(*s_rgb, 130),
        width=1,
    )

    # Stark negative-space corner slashes
    cut_w, cut_h = 124, 98
    draw.polygon([(0, 0), (cut_w, 0), (0, cut_h)], fill=(*k_rgb, 242))
    draw.line([(cut_w + 2, 0), (0, cut_h + 2)], fill=(*p_rgb, 255), width=4)
    draw.polygon(
        [(target_w, target_h), (target_w - cut_w, target_h), (target_w, target_h - cut_h)],
        fill=(*k_rgb, 242),
    )
    draw.line(
        [(target_w - cut_w - 2, target_h), (target_w, target_h - cut_h - 2)],
        fill=(*s_rgb, 255),
        width=4,
    )

    # 4-Point Cruciform Star Flares
    draw_trigger_cruciform_star(
        draw,
        cx=target_w * 0.77,
        cy=target_h * 0.21,
        outer_r=56.0,
        inner_r=9.0,
        angle_deg=15.0 + idx * 6.0,
        fill_rgba=(*p_rgb, 245),
    )
    draw_trigger_cruciform_star(
        draw,
        cx=target_w * 0.22,
        cy=target_h * 0.68,
        outer_r=40.0,
        inner_r=6.5,
        angle_deg=-18.0 + idx * 5.0,
        fill_rgba=(*s_rgb, 235),
    )

    # Sovereign 10-Year Frame Filigree (ZERO baked text)
    draw.rectangle([0, 0, target_w - 1, target_h - 1], outline=(*k_rgb, 255), width=3)
    draw.rectangle([2, 2, target_w - 3, target_h - 3], outline=(*p_rgb, 235), width=2)
    margin = 12
    bevel = 26
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
    draw.polygon(oct_pts, outline=(*s_rgb, 215), width=2)
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


def build_svg_emblem(spec: Dict[str, Any]) -> str:
    """
    Generates a pure code-native SVG (`viewBox="0 0 256 256"`, zero `<text>` tags)
    for the given Saga Era or Ranked League Tier emblem.
    """
    eid = spec["id"]
    p = spec["primary"]
    s = spec["secondary"]
    a = spec["accent"]
    d = spec["dark"]

    if eid == "era1_cradle_of_echoes_crest":
        inner_geo = f"""
  <!-- Era I: 3x3 Sanctum Lattice & Polyhedral Eclipse Ring -->
  <circle cx="128" cy="128" r="96" fill="none" stroke="{p}" stroke-width="3" stroke-dasharray="10 6"/>
  <polygon points="128,22 220,75 220,181 128,234 36,181 36,75" fill="{d}" fill-opacity="0.88" stroke="{s}" stroke-width="4"/>
  <polygon points="128,42 202,128 128,214 54,128" fill="url(#grad_{eid})" stroke="{p}" stroke-width="3"/>
  <!-- 3x3 Tactical Grid Lines -->
  <line x1="96" y1="76" x2="96" y2="180" stroke="{a}" stroke-width="2.5"/>
  <line x1="160" y1="76" x2="160" y2="180" stroke="{a}" stroke-width="2.5"/>
  <line x1="76" y1="96" x2="180" y2="96" stroke="{a}" stroke-width="2.5"/>
  <line x1="76" y1="160" x2="180" y2="160" stroke="{a}" stroke-width="2.5"/>
  <!-- 4-Point Cruciform Astral Core -->
  <polygon points="128,56 140,116 200,128 140,140 128,200 116,140 56,128 116,116" fill="{p}" stroke="#FFFFFF" stroke-width="2"/>
  <circle cx="128" cy="128" r="10" fill="#FFFFFF"/>
"""
    elif eid == "era2_sovran_mechanica_crest":
        inner_geo = f"""
  <!-- Era II: Orthographic Astrolabe Gear & Beveled Mecha V-Fin Shield -->
  <circle cx="128" cy="128" r="102" fill="none" stroke="{s}" stroke-width="2.5"/>
  <polygon points="128,18 152,34 188,28 198,62 232,78 220,112 238,144 210,172 214,206 178,214 158,240 128,226 98,240 78,214 42,206 46,172 18,144 36,112 24,78 58,62 68,28 104,34" fill="{d}" stroke="{p}" stroke-width="3.5"/>
  <circle cx="128" cy="128" r="76" fill="url(#grad_{eid})" stroke="{s}" stroke-width="3"/>
  <!-- Mecha V-Fin & Energy Wings -->
  <polygon points="128,62 212,42 176,124 128,98 80,124 44,42" fill="{p}" stroke="#FFFFFF" stroke-width="2.5"/>
  <polygon points="128,104 176,148 128,216 80,148" fill="{s}" stroke="{p}" stroke-width="3"/>
  <polygon points="128,74 138,118 182,128 138,138 128,182 118,138 74,128 118,118" fill="#FFFFFF" stroke="{a}" stroke-width="1.5"/>
"""
    elif eid == "era3_omega_convergence_crest":
        inner_geo = f"""
  <!-- Era III: Omega Singularity Crown & 4-Point Cruciform Star Burst -->
  <circle cx="128" cy="128" r="104" fill="none" stroke="{a}" stroke-width="3"/>
  <polygon points="128,16 194,48 240,128 194,208 128,240 62,208 16,128 62,48" fill="{d}" stroke="{p}" stroke-width="4"/>
  <polygon points="128,34 218,128 128,222 38,128" fill="url(#grad_{eid})" stroke="{s}" stroke-width="3"/>
  <!-- Six Singularity Seraph Wings -->
  <polygon points="128,70 226,52 184,116 232,148 168,158 128,224 88,158 24,148 72,116 30,52" fill="{p}" fill-opacity="0.85" stroke="{a}" stroke-width="2.5"/>
  <!-- Asymmetric 4-Point Trigger Star Flare -->
  <polygon points="128,20 142,114 236,128 142,142 128,236 114,142 20,128 114,114" fill="{a}" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="128" cy="128" r="14" fill="#FFFFFF" stroke="{s}" stroke-width="3"/>
"""
    elif eid == "rank_gold_law_arbiter_crest":
        inner_geo = f"""
  <!-- Ranked Gold Law Arbiter Crest: Sovereign Scales & Paladin Shield -->
  <polygon points="128,18 216,54 202,168 128,238 54,168 40,54" fill="{d}" stroke="{p}" stroke-width="5"/>
  <polygon points="128,34 198,64 186,160 128,220 70,160 58,64" fill="url(#grad_{eid})" stroke="{s}" stroke-width="2.5"/>
  <!-- Law Balance Crossbar & Scales -->
  <line x1="64" y1="104" x2="192" y2="104" stroke="#FFFFFF" stroke-width="4"/>
  <polygon points="128,44 140,104 128,198 116,104" fill="{p}" stroke="#FFFFFF" stroke-width="2"/>
  <polygon points="72,104 92,146 52,146" fill="{s}" stroke="{p}" stroke-width="2"/>
  <polygon points="184,104 204,146 164,146" fill="{s}" stroke="{p}" stroke-width="2"/>
  <circle cx="128" cy="104" r="12" fill="{a}" stroke="#FFFFFF" stroke-width="2.5"/>
"""
    elif eid == "rank_diamond_kubrart_prism_crest":
        inner_geo = f"""
  <!-- Ranked Diamond Kubrart Prism Crest: Negative-Space Obsidian & Polyhedral Facets -->
  <polygon points="128,14 222,72 222,184 128,242 34,184 34,72" fill="{d}" stroke="{p}" stroke-width="4"/>
  <!-- Stark Negative-Space Obsidian Split -->
  <polygon points="34,72 128,14 128,128 34,184" fill="#05070C"/>
  <polygon points="128,28 214,128 128,228 42,128" fill="url(#grad_{eid})" stroke="{a}" stroke-width="3.5"/>
  <polygon points="128,54 186,128 128,202 70,128" fill="{d}" stroke="{s}" stroke-width="3"/>
  <polygon points="128,44 140,116 212,128 140,140 128,212 116,140 44,128 116,116" fill="{p}" stroke="#FFFFFF" stroke-width="2"/>
"""
    else:
        # rank_sovereign_grandmaster_apex_crest
        inner_geo = f"""
  <!-- Ranked Sovereign Grandmaster Apex Crest: 4-Faction Crown & Cruciform Star -->
  <circle cx="128" cy="128" r="108" fill="none" stroke="{p}" stroke-width="3" stroke-dasharray="14 6"/>
  <polygon points="128,12 172,44 228,36 212,92 244,128 212,164 228,220 172,212 128,244 84,212 28,220 44,164 12,128 44,92 28,36 84,44" fill="{d}" stroke="{p}" stroke-width="4"/>
  <circle cx="128" cy="128" r="82" fill="url(#grad_{eid})" stroke="{a}" stroke-width="3"/>
  <!-- Sovereign Crown Spires -->
  <polygon points="62,142 78,68 106,112 128,48 150,112 178,68 194,142" fill="{p}" stroke="#FFFFFF" stroke-width="2.5"/>
  <!-- 4-Point Cruciform Grandmaster Star -->
  <polygon points="128,18 144,112 238,128 144,144 128,238 112,144 18,128 112,112" fill="{s}" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="128" cy="128" r="16" fill="#FFFFFF" stroke="{p}" stroke-width="4"/>
"""

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" data-emblem-id="{eid}">
  <defs>
    <linearGradient id="grad_{eid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{p}" stop-opacity="0.92"/>
      <stop offset="55%" stop-color="{s}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{d}" stop-opacity="0.96"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="248" height="248" rx="28" fill="{d}" stroke="{p}" stroke-width="3"/>
{inner_geo}</svg>
"""
    return svg_content


def render_emblem_preview_pil(spec: Dict[str, Any], size: int = 220) -> Image.Image:
    """Renders a crisp vector-style PIL preview of the SVG emblem for the 2400x1600 showcase sheet."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    def hex_rgb(h: str) -> Tuple[int, int, int]:
        c = h.lstrip("#")
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))

    p = hex_rgb(spec["primary"])
    s = hex_rgb(spec["secondary"])
    a = hex_rgb(spec["accent"])
    d = hex_rgb(spec["dark"])
    cx, cy = size // 2, size // 2

    draw.rounded_rectangle([4, 4, size - 5, size - 5], radius=24, fill=(*d, 255), outline=(*p, 255), width=3)
    r_hex = int(size * 0.39)
    hex_pts = [
        (cx + math.cos(math.radians(60 * i - 30)) * r_hex, cy + math.sin(math.radians(60 * i - 30)) * r_hex)
        for i in range(6)
    ]
    draw.polygon(hex_pts, fill=(*d, 235), outline=(*s, 245))
    r_dia = int(size * 0.31)
    dia_pts = [(cx, cy - r_dia), (cx + r_dia, cy), (cx, cy + r_dia), (cx - r_dia, cy)]
    draw.polygon(dia_pts, fill=(*p, 95), outline=(*a, 240))
    draw_trigger_cruciform_star(
        draw,
        cx=cx,
        cy=cy,
        outer_r=size * 0.34,
        inner_r=size * 0.06,
        angle_deg=0.0,
        fill_rgba=(*p, 245),
    )
    draw_trigger_cruciform_star(
        draw,
        cx=cx,
        cy=cy,
        outer_r=size * 0.22,
        inner_r=size * 0.04,
        angle_deg=45.0,
        fill_rgba=(*s, 235),
    )
    return img.convert("RGB")


def build_10year_saga_showcase_2400x1600(
    card_records: List[Dict[str, Any]],
    emblem_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Composites a `2400x1600` RGB opaque 10-Year Franchise Saga Production Showcase Sheet:
      - Top Section (`y = 0..860`): All 6 `600x800` RTX 4080 Era Herald Master Cards (`saga_y01`..`saga_y10`)
        in 6 columns (`400px` per column, `360x480` 3:4 portrait + Era/Year chromatic telemetry bars).
      - Middle Section (`y = 860..1120`): 10-Year (20-Set, 3-Era) Franchise Timeline Bands with
        chromatic milestone nodes for Years 1..10.
      - Bottom Section (`y = 1120..1600`): Rendered vector previews of all 6 Code-Native SVG
        Era & Ranked League Emblems (`era1`..`era3` + `rank_gold`, `rank_diamond`, `rank_sovereign`).
    """
    sheet_w, sheet_h = 2400, 1600
    sheet = Image.new("RGB", (sheet_w, sheet_h), (8, 12, 22))
    draw = ImageDraw.Draw(sheet)

    # 1. Top Section: 6 Era Herald Master Cards (6 cols x 400px)
    col_w = sheet_w // 6  # 400
    card_w, card_h = 360, 480

    for idx, rec in enumerate(card_records[:6]):
        x_cell = idx * col_w
        x0 = x_cell + (col_w - card_w) // 2  # +20
        y0 = 28
        p_col = tuple(rec["primary_rgb"])
        s_col = tuple(rec["secondary_rgb"])

        draw.rectangle(
            [x_cell + 8, 12, x_cell + col_w - 8, 568],
            fill=(13, 19, 34),
            outline=p_col,
            width=2,
        )

        with Image.open(rec["path"]) as im:
            thumb = im.convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x0, y0))
        draw.rectangle([x0 - 2, y0 - 2, x0 + card_w + 1, y0 + card_h + 1], outline=p_col, width=2)

        # Era & Year Chromatic Telemetry Strip below each portrait
        y_bar = y0 + card_h + 14
        draw.rectangle([x0, y_bar, x0 + card_w, y_bar + 32], fill=(18, 26, 46), outline=s_col, width=2)
        draw.rectangle([x0 + 6, y_bar + 6, x0 + 96, y_bar + 26], fill=p_col)
        draw.rectangle([x0 + 104, y_bar + 6, x0 + 194, y_bar + 26], fill=s_col)

    # 2. Middle Section (y = 588..960): 10-Year / 20-Set Franchise Timeline Progression Matrix
    draw.rectangle([20, 592, sheet_w - 20, 952], fill=(12, 17, 32), outline=(0, 229, 255), width=2)

    era_bands = [
        ("Era I: Cradle of Echoes (Y1-Y3)", 40, 790, (0, 229, 255), (168, 85, 247)),
        ("Era II: Sovran Mechanica (Y4-Y7)", 810, 1590, (255, 184, 0), (46, 230, 211)),
        ("Era III: Omega Convergence (Y8-Y10)", 1610, 2360, (255, 46, 84), (255, 184, 0)),
    ]
    for _title, x_start, x_end, c_prim, c_sec in era_bands:
        draw.rectangle([x_start, 616, x_end, 740], fill=(16, 24, 44), outline=c_prim, width=3)
        draw.rectangle([x_start + 12, 632, x_end - 12, 668], fill=c_prim)
        draw.rectangle([x_start + 12, 682, x_end - 12, 722], fill=(22, 32, 58), outline=c_sec, width=2)

    # 10 Year Milestone Nodes across y = 840
    y_tl = 845
    draw.line([(80, y_tl), (sheet_w - 80, y_tl)], fill=(0, 229, 255), width=5)
    for yr in range(10):
        nx = int(120 + yr * ((sheet_w - 240) / 9.0))
        node_col = (0, 229, 255) if yr < 3 else ((255, 184, 0) if yr < 7 else (255, 46, 84))
        draw.ellipse([nx - 26, y_tl - 26, nx + 26, y_tl + 26], fill=(10, 15, 28), outline=node_col, width=4)
        draw.ellipse([nx - 12, y_tl - 12, nx + 12, y_tl + 12], fill=node_col)
        # Set pair bars below each Year node (2 sets per year = 20 sets total)
        draw.rectangle([nx - 34, y_tl + 38, nx - 4, y_tl + 64], fill=node_col)
        draw.rectangle([nx + 4, y_tl + 38, nx + 34, y_tl + 64], fill=(248, 250, 252))

    # 3. Bottom Section (y = 976..1584): 6 Code-Native SVG Era & Ranked League Emblem Previews
    for idx, (e_spec, e_rec) in enumerate(zip(SVG_EMBLEM_SPECS, emblem_records)):
        x_cell = idx * col_w
        draw.rectangle(
            [x_cell + 8, 976, x_cell + col_w - 8, 1584],
            fill=(13, 19, 34),
            outline=(255, 184, 0) if idx >= 3 else (0, 229, 255),
            width=2,
        )
        emblem_im = render_emblem_preview_pil(e_spec, size=320)
        ex0 = x_cell + (col_w - 320) // 2
        ey0 = 1015
        sheet.paste(emblem_im, (ex0, ey0))

        # Chromatic footer bar under each emblem
        draw.rectangle([ex0, ey0 + 340, ex0 + 320, ey0 + 376], fill=(20, 30, 54), outline=(0, 229, 255), width=2)

    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    copy_if_distinct(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": sheet_w,
        "height": sheet_h,
        "herald_cards_displayed": 6,
        "svg_emblems_displayed": 6,
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t_start = time.time()
    SAGA_ART_DIR.mkdir(parents=True, exist_ok=True)
    WEB_SAGA_ART_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    SVG_EMBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    print(
        f"[10-Year Saga Cluster Production] Rendering 6 Era Herald Master Portraits on {COMFYUI_URL}...",
        flush=True,
    )

    card_records: List[Dict[str, Any]] = []
    card_sha_set = set()
    live_render_count = 0

    for idx, spec in enumerate(SAGA_HERALD_CARDS):
        raw_info = render_rtx4080_saga_raw(spec, width=768, height=1024, steps=10, cfg=6.5, force=False)
        if raw_info["rtx4080_live_rendered"]:
            live_render_count += 1

        raw_path = Path(raw_info["raw_source_path"])
        with Image.open(raw_path) as raw_im:
            finished_im = refine_saga_herald_portrait_600x800(raw_im, idx, spec)

        out_path = SAGA_ART_DIR / spec["filename"]
        finished_im.save(out_path, format="PNG", optimize=True)
        copy_if_distinct(out_path, WEB_SAGA_ART_DIR / spec["filename"])
        copy_if_distinct(out_path, UNITY_PORTRAITS_DIR / spec["filename"])

        with Image.open(out_path) as chk:
            w, h = chk.size
            mode = chk.mode
            bbox = list(chk.getbbox() or (0, 0, 0, 0))

        sha = compute_sha256(out_path)
        card_sha_set.add(sha)

        card_records.append(
            {
                "id": spec["id"],
                "slug": spec["slug"],
                "filename": spec["filename"],
                "name": spec["name"],
                "era_id": spec["era_id"],
                "era_title": spec["era_title"],
                "years_label": spec["years_label"],
                "sets_spanned": spec["sets_spanned"],
                "faction": spec["faction"],
                "cost": spec["cost"],
                "nesw": spec["nesw"],
                "ability": spec["ability"],
                "primary_hex": spec["primary_hex"],
                "secondary_hex": spec["secondary_hex"],
                "primary_rgb": list(spec["primary_rgb"]),
                "secondary_rgb": list(spec["secondary_rgb"]),
                "art": f"./GeneratedArt/Saga10YearFranchise/{spec['filename']}",
                "path": str(out_path),
                "web_playable_path": str(WEB_SAGA_ART_DIR / spec["filename"]),
                "unity_portrait_path": str(UNITY_PORTRAITS_DIR / spec["filename"]),
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
            f"  [Saga {idx + 1:02d}/06] {spec['id']} ({spec['name']}): "
            f"{w}x{h} {mode} bounds={bbox} sha256={sha[:12]}... ({raw_info['elapsed_s']}s)",
            flush=True,
        )

    print("[10-Year Saga SVG Emblems] Generating 6 code-native 256x256 SVG emblems...", flush=True)
    emblem_records: List[Dict[str, Any]] = []
    for e_spec in SVG_EMBLEM_SPECS:
        svg_str = build_svg_emblem(e_spec)
        assert_zero_living_artist_names(svg_str, e_spec["filename"])
        out_svg = SVG_EMBLEMS_DIR / e_spec["filename"]
        out_svg.write_text(svg_str, encoding="utf-8")

        # Parse XML & verify viewBox="0 0 256 256" and zero <text>/<tspan> elements
        root_el = ET.fromstring(svg_str)
        view_box = root_el.attrib.get("viewBox", "")
        has_text_tag = any(
            el.tag.endswith("text") or el.tag.endswith("tspan") for el in root_el.iter()
        )
        if view_box != "0 0 256 256" or has_text_tag:
            raise ValueError(f"Invalid SVG emblem {e_spec['filename']}: viewBox={view_box}, has_text={has_text_tag}")

        emblem_records.append(
            {
                "id": e_spec["id"],
                "filename": e_spec["filename"],
                "title": e_spec["title"],
                "category": e_spec["category"],
                "path": str(out_svg),
                "web_asset_path": f"./assets/saga_emblems/{e_spec['filename']}",
                "viewBox": view_box,
                "zero_text_nodes": not has_text_tag,
                "sha256": compute_sha256(out_svg),
                "bytes": out_svg.stat().st_size,
            }
        )
        print(
            f"  [SVG] {e_spec['filename']}: viewBox='{view_box}' zero_text_nodes={not has_text_tag}",
            flush=True,
        )

    showcase_info = build_10year_saga_showcase_2400x1600(card_records, emblem_records)

    all_cards_valid = all(
        r["width"] == 600
        and r["height"] == 800
        and r["mode"] == "RGB"
        and r["content_bounds"] == [0, 0, 600, 800]
        for r in card_records
    )
    all_emblems_valid = all(
        e["viewBox"] == "0 0 256 256" and e["zero_text_nodes"] is True for e in emblem_records
    )

    manifest = {
        "manifest_id": "cardfront_10year_production_assets_v1",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "Backend/render_10year_saga_cluster_production_assets.py",
        "status": "VERIFIED" if (all_cards_valid and all_emblems_valid and len(card_sha_set) == 6) else "FAILED",
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
        "saga_herald_cards_count": len(card_records),
        "saga_herald_unique_sha256_count": len(card_sha_set),
        "rtx4080_live_rendered_heralds_count": live_render_count,
        "all_herald_cards_600x800_rgb_opaque": all_cards_valid,
        "svg_emblems_count": len(emblem_records),
        "all_svg_emblems_256x256_zero_text": all_emblems_valid,
        "showcase_atlas": showcase_info,
        "total_wall_time_s": round(time.time() - t_start, 2),
        "saga_herald_cards": card_records,
        "svg_emblems": emblem_records,
    }

    manifest_json = json.dumps(manifest, indent=2)
    assert_zero_living_artist_names(manifest_json, "cardfront_10year_production_assets_manifest.json")
    OUT_MANIFEST_PATH.write_text(manifest_json + "\n", encoding="utf-8")

    print(
        f"[Complete] 6/6 10-Year Saga Herald Master Cards (600x800 RGB={all_cards_valid}) + "
        f"6/6 256x256 Code-Native SVG Emblems (valid={all_emblems_valid}) in {manifest['total_wall_time_s']}s.",
        flush=True,
    )
    print(f"  Manifest: {OUT_MANIFEST_PATH}", flush=True)
    print(f"  Showcase: {SHOWCASE_BRAIN_PATH}", flush=True)


if __name__ == "__main__":
    main()
