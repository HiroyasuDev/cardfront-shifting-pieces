#!/usr/bin/env python3
"""
render_3d_dice_and_ffta_pixel_chibi_assets.py
=============================================
Track A: High-Detail 3D/2.5D Polyhedral Game Dice Renders (`D6` / `D8` / `D12` / `D20`
Beveled Magicite & Gold Filigree Dice) + 24 Unique Final Fantasy Tactics Advance
(`FFTA` / Ivalice GBA/HD-2D Isometric Pixel-Art Chibi) Character Unit Sprites &
2-Frame Animated Sprite Sheets.

Strict Art Direction & Technical Locks:
- ZERO living artists' names in any prompt, script, or manifest (`zero_living_artist_names: true`).
- Connects to Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`, `animagineXLV31_v31.safetensors`)
  to render the master crystal caustic & gold filigree dice reference sheet
  (`dice3d_rtx4080_master_crystal_sheet.png`).
- Part 1 (`GeneratedArt/Dice3D/`, mirrored to `WebPlayable/GeneratedArt/Dice3D/` and
  `Assets/Resources/CardFront/Dice3D/`):
  * 6 3D Isometric Beveled D6 Column Dice (`dice3d_d6_face_1.png` .. `dice3d_d6_face_6.png`, 256x256 RGBA)
    showing all 3 visible 3D cube faces (`Top`, `Left`, `Right`) with recessed glowing pips,
    3D beveled metallic gold/gunmetal edges, engraved corner filigree, subsurface crystal
    refraction, specular highlights, and contact drop shadows.
  * 4 Faction 3D Special Polyhedral Dice (`dice3d_aether_sapphire_d8.png`,
    `dice3d_crimson_obsidian_d8.png`, `dice3d_sovereign_gold_d12.png`,
    `dice3d_kubrart_violet_d20.png`, 256x256 RGBA).
  * 2 Animated 8-Frame `2048x256` (`8` frames of `256x256`) 3D Tumbling Roll Sprite Strips
    (`dice3d_tumble_strip_blue.png` & `dice3d_tumble_strip_red.png`).
- Part 2 (`GeneratedArt/FFAChibiUnits/`, mirrored to `WebPlayable/GeneratedArt/FFAChibiUnits/` and
  `Assets/Resources/CardFront/FFAChibiUnits/`):
  * 24 unique, cryptographically distinct `128x128` (`32x32` native pixel grid upscaled `4x`
    via `NEAREST`) isometric pixel-art chibi sprites + 24 `256x128` 2-frame `[Idle | Strike]`
    animated sprite sheets (`_sheet.png`).
- Part 3:
  * Builds the `2400x1600` 3D Dice, 2.5D Card Slab & FFTA Pixel-Chibi Showcase Sheet
    (`dice3d_and_ffta_pixel_chibi_showcase.png`) and writes `Datasets/dice3d_and_ffta_chibi_manifest.json`.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
DICE3D_DIR = GENERATED_ART_DIR / "Dice3D"
CHIBI_DIR = GENERATED_ART_DIR / "FFAChibiUnits"
MASTERED_CARDS_DIR = GENERATED_ART_DIR / "MasteredCards"

WEB_GEN_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt"
WEB_DICE3D_DIR = WEB_GEN_ART_DIR / "Dice3D"
WEB_CHIBI_DIR = WEB_GEN_ART_DIR / "FFAChibiUnits"

UNITY_CARDFRONT_RES_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront"
UNITY_DICE3D_DIR = UNITY_CARDFRONT_RES_DIR / "Dice3D"
UNITY_CHIBI_DIR = UNITY_CARDFRONT_RES_DIR / "FFAChibiUnits"

MANIFEST_OUT_PATH = PROJECT_ROOT / "Datasets" / "dice3d_and_ffta_chibi_manifest.json"
SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/dice3d_and_ffta_pixel_chibi_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "dice3d_and_ffta_pixel_chibi_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
CHECKPOINT_NAME = "animagineXLV31_v31.safetensors"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def deterministic_guid(seed_text: str) -> str:
    return hashlib.md5(seed_text.encode("utf-8")).hexdigest()


def ensure_unity_folder_meta(folder: Path) -> None:
    meta_path = Path(str(folder) + ".meta")
    if not meta_path.exists():
        rel = str(folder.relative_to(PROJECT_ROOT)).replace("\\", "/")
        g = deterministic_guid(rel)
        meta_path.write_text(
            f"fileFormatVersion: 2\nguid: {g}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
            encoding="utf-8",
        )


def ensure_unity_png_meta(png_path: Path) -> None:
    meta_path = Path(str(png_path) + ".meta")
    if not meta_path.exists():
        rel = str(png_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        g = deterministic_guid(rel)
        meta_path.write_text(f"fileFormatVersion: 2\nguid: {g}\n", encoding="utf-8")


# =============================================================================
# PART 1A: RTX 4080 ComfyUI Master Crystal Dice Sheet
# =============================================================================
def render_rtx4080_master_crystal_dice_sheet() -> Dict[str, Any]:
    """
    Renders a 768x768 master crystal dice reference texture on Node 30 RTX 4080 ComfyUI
    using concrete morphological descriptions (zero living artists' names).
    """
    DICE3D_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DICE3D_DIR / "dice3d_rtx4080_master_crystal_sheet.png"
    prompt_text = (
        "masterpiece, best quality, official game asset illustration of ornate polyhedral magicite game dice "
        "D6 D8 D12 D20, beveled sovereign gold filigree edges, translucent astral sapphire crystal and crimson "
        "obsidian facets, subsurface internal caustic refraction, glowing cyan and gold engraved pips and runes, "
        "crisp anime cel-shaded specular highlights, dark velvet studio backdrop, no text, no watermark"
    )
    negative_text = (
        "blurry, lowres, flat 2d, plastic, muddy colors, text, watermark, signature, bad geometry, deformed"
    )

    if out_file.exists() and out_file.stat().st_size > 60_000:
        return {
            "filename": out_file.name,
            "path": str(out_file),
            "bytes": out_file.stat().st_size,
            "sha256": compute_sha256(out_file),
            "elapsed_s": 0.0,
            "cached": True,
            "prompt": prompt_text,
        }

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 6.5,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": 4080991,
                "steps": 12,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT_NAME},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 768, "width": 768},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": prompt_text},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative_text},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "CardFront_Dice3D_MasterCrystal", "images": ["8", 0]},
        },
    }

    t0 = time.time()
    try:
        req = urllib.request.Request(
            f"{COMFYUI_URL}/prompt",
            data=json.dumps({"prompt": workflow}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            queued = json.loads(resp.read().decode("utf-8"))
        prompt_id = queued["prompt_id"]

        for _ in range(150):
            time.sleep(0.4)
            with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10) as hresp:
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
                        urllib.request.urlretrieve(f"{COMFYUI_URL}/view?{qs}", out_file)
                        return {
                            "filename": out_file.name,
                            "path": str(out_file),
                            "prompt_id": prompt_id,
                            "bytes": out_file.stat().st_size,
                            "sha256": compute_sha256(out_file),
                            "elapsed_s": round(time.time() - t0, 2),
                            "cached": False,
                            "prompt": prompt_text,
                        }
    except Exception as exc:
        print(f"[WARN] ComfyUI crystal sheet fallback triggered: {exc}", flush=True)

    # Procedural high-detail crystal caustic fallback if offline
    arr = np.zeros((768, 768, 3), dtype=np.uint8)
    yy, xx = np.mgrid[0:768, 0:768].astype(np.float32) / 768.0
    wave = 0.5 + 0.5 * np.sin(xx * 18.0 + np.cos(yy * 14.0) * 3.0)
    arr[:, :, 0] = np.clip((20 + 180 * (wave ** 3)), 0, 255).astype(np.uint8)
    arr[:, :, 1] = np.clip((90 + 160 * wave), 0, 255).astype(np.uint8)
    arr[:, :, 2] = np.clip((160 + 95 * np.sqrt(wave)), 0, 255).astype(np.uint8)
    Image.fromarray(arr, mode="RGB").save(out_file, format="PNG")
    return {
        "filename": out_file.name,
        "path": str(out_file),
        "bytes": out_file.stat().st_size,
        "sha256": compute_sha256(out_file),
        "elapsed_s": round(time.time() - t0, 2),
        "cached": False,
        "prompt": prompt_text,
    }


# =============================================================================
# PART 1B: 3D Raytraced / PBR-Shaded Polyhedral Game Dice Renderer
# =============================================================================
PIP_LAYOUTS_UV: Dict[int, List[Tuple[float, float]]] = {
    1: [(0.0, 0.0)],
    2: [(-0.42, -0.42), (0.42, 0.42)],
    3: [(-0.44, -0.44), (0.0, 0.0), (0.44, 0.44)],
    4: [(-0.42, -0.42), (0.42, -0.42), (-0.42, 0.42), (0.42, 0.42)],
    5: [(-0.44, -0.44), (0.44, -0.44), (0.0, 0.0), (-0.44, 0.44), (0.44, 0.44)],
    6: [
        (-0.42, -0.46),
        (0.42, -0.46),
        (-0.42, 0.0),
        (0.42, 0.0),
        (-0.42, 0.46),
        (0.42, 0.46),
    ],
}

# Standard opposite-faces-sum-to-7 adjacency for (Top, Front-Left, Front-Right)
D6_VISIBLE_FACE_TRIPLETS: Dict[int, Tuple[int, int, int]] = {
    1: (1, 2, 3),
    2: (2, 4, 1),
    3: (3, 1, 5),
    4: (4, 6, 2),
    5: (5, 3, 6),
    6: (6, 5, 4),
}


def _rot_matrix(rx: float, ry: float, rz: float) -> np.ndarray:
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float32)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float32)
    return Rz @ Rx @ Ry


def _render_3d_cube_face_quad(
    canvas: Image.Image,
    p00: Tuple[float, float],
    p10: Tuple[float, float],
    p11: Tuple[float, float],
    p01: Tuple[float, float],
    face_normal: np.ndarray,
    pip_count: int,
    crystal_rgb: Tuple[int, int, int],
    deep_rgb: Tuple[int, int, int],
    gold_rgb: Tuple[int, int, int],
    pip_glow_rgb: Tuple[int, int, int],
    caustic_arr: np.ndarray,
    face_seed: int,
) -> None:
    """
    Renders a single visible 3D cube face with:
    - Bilinear inverse-mapped (u, v) coordinates in [-1, 1]^2
    - 3D chamfered metallic gold/gunmetal bevel edges & engraved corner filigree
    - Subsurface magicite crystal caustic refraction + Phong specular highlight
    - Recessed 3D hemispherical countersunk glowing enamel pips
    """
    w, h = canvas.size
    xs = [p00[0], p10[0], p11[0], p01[0]]
    ys = [p00[1], p10[1], p11[1], p01[1]]
    x_min = max(0, int(math.floor(min(xs))) - 1)
    x_max = min(w - 1, int(math.ceil(max(xs))) + 1)
    y_min = max(0, int(math.floor(min(ys))) - 1)
    y_max = min(h - 1, int(math.ceil(max(ys))) + 1)
    if x_max <= x_min or y_max <= y_min:
        return

    # Solve projective homography / affine mapping from quad corners to (u, v) in [-1, 1]^2
    # Since orthographic/weak-perspective cube faces are parallelograms:
    # P(s, t) = p00 + s*(p10 - p00) + t*(p01 - p00), where s, t in [0, 1]
    vx = np.array([p10[0] - p00[0], p01[0] - p00[0]], dtype=np.float32)
    vy = np.array([p10[1] - p00[1], p01[1] - p00[1]], dtype=np.float32)
    M = np.array([[vx[0], vx[1]], [vy[0], vy[1]]], dtype=np.float32)
    det = float(np.linalg.det(M))
    if abs(det) < 1e-4:
        return
    M_inv = np.linalg.inv(M)

    yy, xx = np.mgrid[y_min : y_max + 1, x_min : x_max + 1].astype(np.float32)
    dx = xx - p00[0]
    dy = yy - p00[1]
    s = M_inv[0, 0] * dx + M_inv[0, 1] * dy
    t = M_inv[1, 0] * dx + M_inv[1, 1] * dy

    # Rounded cube chamfer mask in (u, v) = (2s - 1, 2t - 1)
    u = 2.0 * s - 1.0
    v = 2.0 * t - 1.0
    # Superellipse chamfer boundary so cube corners are subtly rounded in 3D
    lp_dist = (np.abs(u) ** 8 + np.abs(v) ** 8) ** 0.125
    inside_mask = (s >= -0.01) & (s <= 1.01) & (t >= -0.01) & (t <= 1.01) & (lp_dist <= 1.015)
    if not np.any(inside_mask):
        return

    # Lighting vectors
    light_dir = np.array([-0.48, -0.62, 0.62], dtype=np.float32)
    light_dir /= np.linalg.norm(light_dir)
    view_dir = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    half_vec = light_dir + view_dir
    half_vec /= np.linalg.norm(half_vec)

    # Construct per-pixel normal perturbation for 3D bevels, filigree, and recessed pips
    nx = np.full_like(u, face_normal[0])
    ny = np.full_like(u, face_normal[1])
    nz = np.full_like(u, face_normal[2])

    max_uv = np.maximum(np.abs(u), np.abs(v))
    bevel_zone = max_uv > 0.81
    inner_trim_zone = (max_uv > 0.75) & (max_uv <= 0.81)

    # Corner filigree scrollwork in corners of inner crystal plate
    corner_dist = np.minimum(
        np.hypot(np.abs(u) - 0.62, np.abs(v) - 0.62),
        np.hypot(np.abs(u) - 0.68, np.abs(v) - 0.52),
    )
    filigree_scroll = (
        (np.abs(u) > 0.44)
        & (np.abs(v) > 0.44)
        & (max_uv < 0.74)
        & (np.abs(corner_dist - 0.09) < 0.024)
    )

    # Tilt normal outward on bevel zone
    nx = np.where(bevel_zone, nx + 0.45 * u, nx)
    ny = np.where(bevel_zone, ny + 0.45 * v, ny)
    norm_len = np.maximum(1e-5, np.sqrt(nx * nx + ny * ny + nz * nz))
    nx /= norm_len
    ny /= norm_len
    nz /= norm_len

    # Diffuse + Specular lighting
    ndotl = np.clip(nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2], 0.08, 1.0)
    ndoth = np.clip(nx * half_vec[0] + ny * half_vec[1] + nz * half_vec[2], 0.0, 1.0)
    spec_crystal = (ndoth ** 28) * 0.55
    spec_gold = (ndoth ** 14) * 0.75

    # Sample RTX 4080 caustic texture
    ch, cw, _ = caustic_arr.shape
    cu = np.clip(((s * 0.75 + 0.12 + (face_seed % 3) * 0.05) * (cw - 1)).astype(np.int32), 0, cw - 1)
    cv = np.clip(((t * 0.75 + 0.12 + (face_seed % 2) * 0.07) * (ch - 1)).astype(np.int32), 0, ch - 1)
    caustic_sample = caustic_arr[cv, cu].astype(np.float32) / 255.0

    c_prim = np.array(crystal_rgb, dtype=np.float32) / 255.0
    c_deep = np.array(deep_rgb, dtype=np.float32) / 255.0
    c_gold = np.array(gold_rgb, dtype=np.float32) / 255.0
    c_pip = np.array(pip_glow_rgb, dtype=np.float32) / 255.0

    # Radial subsurface depth inside crystal face
    r_center = np.hypot(u, v)
    subsurface = np.clip(1.0 - r_center * 0.65, 0.0, 1.0)
    crystal_col = (
        c_deep[np.newaxis, np.newaxis, :] * (1.0 - subsurface[:, :, np.newaxis] * 0.65)
        + c_prim[np.newaxis, np.newaxis, :] * (subsurface[:, :, np.newaxis] * 0.75)
        + caustic_sample * 0.22
    )
    crystal_col = crystal_col * (0.42 + 0.68 * ndotl[:, :, np.newaxis]) + spec_crystal[:, :, np.newaxis]

    # Gold metallic bevel & filigree shading
    gold_grad = 0.55 + 0.45 * np.sin((u + v) * 4.0)
    gold_col = (
        c_gold[np.newaxis, np.newaxis, :] * (0.45 + 0.62 * ndotl[:, :, np.newaxis]) * (0.82 + 0.18 * gold_grad[:, :, np.newaxis])
        + spec_gold[:, :, np.newaxis] * np.array([1.0, 0.96, 0.82], dtype=np.float32)[np.newaxis, np.newaxis, :]
    )
    gunmetal_groove = c_gold[np.newaxis, np.newaxis, :] * 0.32

    face_rgb = crystal_col
    face_rgb = np.where(filigree_scroll[:, :, np.newaxis], gold_col * 0.92, face_rgb)
    face_rgb = np.where(inner_trim_zone[:, :, np.newaxis], gunmetal_groove, face_rgb)
    face_rgb = np.where(bevel_zone[:, :, np.newaxis], gold_col, face_rgb)

    # Recessed 3D hemispherical pips
    pips = PIP_LAYOUTS_UV.get(pip_count, PIP_LAYOUTS_UV[1])
    pip_radius = 0.19 if pip_count == 1 else 0.145
    for px_uv, py_uv in pips:
        d_pip = np.hypot(u - px_uv, v - py_uv)
        rim_ring = (d_pip >= pip_radius * 0.92) & (d_pip <= pip_radius * 1.24)
        well_zone = d_pip < pip_radius * 0.92
        core_glow = np.clip(1.0 - (d_pip / (pip_radius * 0.92)), 0.0, 1.0) ** 1.4
        # Upper-left recessed shadow inside the countersunk well
        recess_shade = 0.45 + 0.55 * np.clip(((u - px_uv) * 0.6 + (v - py_uv) * 0.6) / pip_radius + 0.5, 0.0, 1.0)
        pip_well_col = (
            c_pip[np.newaxis, np.newaxis, :] * (0.55 + 0.65 * core_glow[:, :, np.newaxis]) * recess_shade[:, :, np.newaxis]
            + np.array([1.0, 1.0, 1.0], dtype=np.float32)[np.newaxis, np.newaxis, :] * ((core_glow ** 3.2)[:, :, np.newaxis] * 0.72)
        )
        face_rgb = np.where(rim_ring[:, :, np.newaxis], gold_col * 0.95, face_rgb)
        face_rgb = np.where(well_zone[:, :, np.newaxis], pip_well_col, face_rgb)

    # Anti-aliased edge alpha along superellipse boundary
    alpha = np.clip((1.015 - lp_dist) / 0.035, 0.0, 1.0) * inside_mask.astype(np.float32)

    sub_box = canvas.crop((x_min, y_min, x_max + 1, y_max + 1))
    dst_arr = np.asarray(sub_box, dtype=np.float32) / 255.0
    src_rgb = np.clip(face_rgb, 0.0, 1.0)
    src_a = alpha[:, :, np.newaxis]

    out_a = src_a + dst_arr[:, :, 3:4] * (1.0 - src_a)
    out_rgb = np.where(
        out_a > 1e-5,
        (src_rgb * src_a + dst_arr[:, :, :3] * dst_arr[:, :, 3:4] * (1.0 - src_a)) / np.maximum(out_a, 1e-5),
        0.0,
    )
    merged = np.concatenate([out_rgb, out_a], axis=2)
    merged_u8 = np.clip(merged * 255.0, 0, 255).astype(np.uint8)
    canvas.paste(Image.fromarray(merged_u8, mode="RGBA"), (x_min, y_min))


def render_3d_d6_sprite(
    top_face: int,
    caustic_arr: np.ndarray,
    rx_deg: float = 35.264,
    ry_deg: float = -45.0,
    rz_deg: float = 0.0,
    y_offset_px: float = 0.0,
    scale_factor: float = 1.0,
    theme: str = "blue",
    impact_burst: float = 0.0,
) -> Image.Image:
    """
    Renders a 256x256 RGBA 3D isometric/perspective beveled D6 sprite (2x supersampled at 512x512).
    """
    ss = 512
    canvas = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")

    if theme == "blue":
        crystal_rgb = (0, 215, 255)    # Astral Sapphire
        deep_rgb = (16, 42, 118)       # Deep Cobalt
        gold_rgb = (255, 198, 54)      # Ivalice Law-Gold
        pip_glow_rgb = (110, 248, 255) # Luminous Cyan-White
        glow_aura = (0, 229, 255)
    else:
        crystal_rgb = (255, 46, 84)    # Crimson-Obsidian
        deep_rgb = (48, 8, 26)         # Abyss Obsidian
        gold_rgb = (249, 155, 42)      # Solar Brass-Gold
        pip_glow_rgb = (255, 185, 90)  # Molten Amber-Crimson
        glow_aura = (255, 46, 84)

    # 1. Soft elliptical contact drop shadow + ambient aura at base
    sh_layer = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sh_layer, "RGBA")
    shadow_scale = max(0.55, 1.0 - max(0.0, -y_offset_px) / 140.0)
    rx_sh = int(148 * shadow_scale)
    ry_sh = int(66 * shadow_scale)
    cx_sh, cy_sh = ss // 2, int(ss * 0.79)
    sdraw.ellipse(
        [cx_sh - rx_sh, cy_sh - ry_sh, cx_sh + rx_sh, cy_sh + ry_sh],
        fill=(6, 10, 22, int(175 * shadow_scale)),
    )
    if impact_burst > 0.0:
        br = int(185 * (0.8 + 0.4 * impact_burst))
        sdraw.ellipse(
            [cx_sh - br, cy_sh - int(br * 0.55), cx_sh + br, cy_sh + int(br * 0.55)],
            fill=(*glow_aura, int(135 * impact_burst)),
            outline=(*gold_rgb, int(220 * impact_burst)),
            width=6,
        )
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(radius=14))
    canvas = Image.alpha_composite(canvas, sh_layer)

    # 2. Define 3D cube vertices and 6 faces
    R = 132.0 * scale_factor
    rot = _rot_matrix(math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg))
    cx, cy = ss * 0.5, ss * 0.47 + y_offset_px

    f_top, f_left, f_right = D6_VISIBLE_FACE_TRIPLETS.get(top_face, (1, 2, 3))
    f_bot = 7 - f_top
    f_back_right = 7 - f_left
    f_back_left = 7 - f_right

    # Cube faces defined with outward CCW vertices in [-1, 1]^3
    cube_faces = [
        # +Y (Top in die space before rotation -> mapped to y=-1 in screen-up coordinates)
        (
            f_top,
            np.array([[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1]], dtype=np.float32),
            np.array([0, -1, 0], dtype=np.float32),
        ),
        # -Y (Bottom)
        (
            f_bot,
            np.array([[-1, 1, 1], [1, 1, 1], [1, 1, -1], [-1, 1, -1]], dtype=np.float32),
            np.array([0, 1, 0], dtype=np.float32),
        ),
        # +Z (Front-Left)
        (
            f_left,
            np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=np.float32),
            np.array([0, 0, 1], dtype=np.float32),
        ),
        # +X (Front-Right)
        (
            f_right,
            np.array([[1, -1, 1], [1, -1, -1], [1, 1, -1], [1, 1, 1]], dtype=np.float32),
            np.array([1, 0, 0], dtype=np.float32),
        ),
        # -Z (Back-Right)
        (
            f_back_right,
            np.array([[1, -1, -1], [-1, -1, -1], [-1, 1, -1], [1, 1, -1]], dtype=np.float32),
            np.array([0, 0, -1], dtype=np.float32),
        ),
        # -X (Back-Left)
        (
            f_back_left,
            np.array([[-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1]], dtype=np.float32),
            np.array([-1, 0, 0], dtype=np.float32),
        ),
    ]

    visible_faces = []
    for pip_val, verts, norm in cube_faces:
        r_verts = (verts * R) @ rot.T
        r_norm = norm @ rot.T
        if r_norm[2] > 0.04:  # Facing camera
            z_mean = float(np.mean(r_verts[:, 2]))
            # Perspective projection
            pts_2d = []
            for vx, vy, vz in r_verts:
                persp = 900.0 / max(300.0, 900.0 - vz)
                pts_2d.append((cx + vx * persp, cy + vy * persp))
            visible_faces.append((z_mean, pip_val, pts_2d, r_norm))

    # Sort back-to-front by Z depth
    visible_faces.sort(key=lambda item: item[0])

    for idx_f, (_, pip_val, pts_2d, r_norm) in enumerate(visible_faces):
        _render_3d_cube_face_quad(
            canvas=canvas,
            p00=pts_2d[0],
            p10=pts_2d[1],
            p11=pts_2d[2],
            p01=pts_2d[3],
            face_normal=r_norm,
            pip_count=pip_val,
            crystal_rgb=crystal_rgb,
            deep_rgb=deep_rgb,
            gold_rgb=gold_rgb,
            pip_glow_rgb=pip_glow_rgb,
            caustic_arr=caustic_arr,
            face_seed=top_face * 7 + idx_f,
        )

    # 3. Specular star-glint on the front central vertex
    center_v = np.array([1.0, -1.0, 1.0], dtype=np.float32) * R @ rot.T
    if center_v[2] > 0:
        persp = 900.0 / max(300.0, 900.0 - center_v[2])
        gx = int(cx + center_v[0] * persp)
        gy = int(cy + center_v[1] * persp)
        glint = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glint, "RGBA")
        gdraw.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], fill=(255, 250, 220, 130))
        gdraw.line([(gx - 28, gy), (gx + 28, gy)], fill=(255, 255, 255, 215), width=3)
        gdraw.line([(gx, gy - 28), (gx, gy + 28)], fill=(255, 255, 255, 215), width=3)
        glint = glint.filter(ImageFilter.GaussianBlur(radius=1.5))
        canvas = Image.alpha_composite(canvas, glint)

    return canvas.resize((256, 256), Image.Resampling.LANCZOS)


def _draw_engraved_numeral_on_facet(
    draw: ImageDraw.ImageDraw,
    center: Tuple[float, float],
    label: str,
    scale: float,
    gold_rgb: Tuple[int, int, int],
    glow_rgb: Tuple[int, int, int],
) -> None:
    """
    Draws a crisp vector-geometric engraved numeral ('8', '12', '20', etc.) centered on a 3D polyhedral facet.
    """
    cx, cy = center
    # Digit stroke definitions in [-1, 1] x [-1.4, 1.4]
    digit_strokes: Dict[str, List[List[Tuple[float, float]]]] = {
        "0": [[(-0.7, -1.2), (0.7, -1.2), (0.7, 1.2), (-0.7, 1.2), (-0.7, -1.2)]],
        "1": [[(-0.3, -0.8), (0.1, -1.2), (0.1, 1.2)], [(-0.4, 1.2), (0.5, 1.2)]],
        "2": [[(-0.7, -0.8), (-0.3, -1.2), (0.5, -1.2), (0.7, -0.6), (-0.7, 1.2), (0.7, 1.2)]],
        "3": [[(-0.7, -1.1), (0.6, -1.1), (0.0, -0.1), (0.7, 0.4), (0.5, 1.2), (-0.7, 1.1)]],
        "4": [[(0.3, 1.2), (0.3, -1.2), (-0.7, 0.4), (0.7, 0.4)]],
        "5": [[(0.6, -1.2), (-0.6, -1.2), (-0.6, -0.1), (0.6, 0.1), (0.6, 1.1), (-0.6, 1.2)]],
        "6": [[(0.5, -1.2), (-0.6, -0.4), (-0.6, 1.1), (0.6, 1.1), (0.6, 0.1), (-0.6, 0.1)]],
        "7": [[(-0.7, -1.2), (0.7, -1.2), (-0.2, 1.2)]],
        "8": [
            [(-0.6, -1.2), (0.6, -1.2), (0.6, 0.0), (-0.6, 0.0), (-0.6, -1.2)],
            [(-0.65, 0.0), (0.65, 0.0), (0.65, 1.2), (-0.65, 1.2), (-0.65, 0.0)],
        ],
        "9": [[(-0.5, 1.2), (0.6, 0.4), (0.6, -1.1), (-0.6, -1.1), (-0.6, -0.1), (0.6, -0.1)]],
    }
    n_chars = len(label)
    spacing = scale * 1.65
    start_x = cx - ((n_chars - 1) * spacing) * 0.5
    for idx, ch in enumerate(label):
        ox = start_x + idx * spacing
        strokes = digit_strokes.get(ch, [])
        for st in strokes:
            pts_shadow = [(ox + px * scale + 2, cy + py * scale + 2) for px, py in st]
            pts_main = [(ox + px * scale, cy + py * scale) for px, py in st]
            draw.line(pts_shadow, fill=(10, 8, 20, 210), width=max(3, int(scale * 0.52)))
            draw.line(pts_main, fill=(*gold_rgb, 245), width=max(2, int(scale * 0.38)))
            draw.line(pts_main, fill=(*glow_rgb, 255), width=max(1, int(scale * 0.18)))


def render_3d_polyhedral_die(
    poly_type: str,
    crystal_rgb: Tuple[int, int, int],
    deep_rgb: Tuple[int, int, int],
    edge_rgb: Tuple[int, int, int],
    glow_rgb: Tuple[int, int, int],
    primary_numeral: str,
    secondary_numerals: List[str],
    caustic_arr: np.ndarray,
    rx_deg: float,
    ry_deg: float,
    rz_deg: float,
) -> Image.Image:
    """
    Renders a high-detail 3D faceted D8 (octahedron), D12 (dodecahedron), or D20 (icosahedron)
    at 512x512 supersampled -> 256x256 RGBA.
    """
    ss = 512
    canvas = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))

    # Drop shadow
    sh = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sh, "RGBA")
    sdraw.ellipse([ss // 2 - 142, int(ss * 0.78) - 62, ss // 2 + 142, int(ss * 0.78) + 62], fill=(6, 8, 20, 175))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
    canvas = Image.alpha_composite(canvas, sh)

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    inv_phi = 1.0 / phi

    if poly_type == "D8":
        verts = np.array(
            [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]],
            dtype=np.float32,
        )
        faces = [
            [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
            [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5],
        ]
        radius_scale = 188.0
    elif poly_type == "D20":
        verts = np.array(
            [
                [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
                [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
                [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1],
            ],
            dtype=np.float32,
        )
        verts /= np.linalg.norm(verts[0])
        faces = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
        ]
        radius_scale = 182.0
    else:  # D12 (dual of icosahedron: face centroids of D20 form the 20 vertices of D12, and each D20 vertex defines a pentagon!)
        ico_v = np.array(
            [
                [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
                [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
                [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1],
            ],
            dtype=np.float32,
        )
        ico_f = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
        ]
        d12_verts = []
        for f in ico_f:
            c = np.mean(ico_v[f], axis=0)
            c /= np.linalg.norm(c)
            d12_verts.append(c)
        verts = np.array(d12_verts, dtype=np.float32)
        faces = []
        for v_idx in range(len(ico_v)):
            incident = [fi for fi, f in enumerate(ico_f) if v_idx in f]
            n_vec = ico_v[v_idx] / np.linalg.norm(ico_v[v_idx])
            # Sort incident centroids CCW around n_vec
            ref = d12_verts[incident[0]] - np.dot(d12_verts[incident[0]], n_vec) * n_vec
            ref /= np.linalg.norm(ref)
            tan2 = np.cross(n_vec, ref)
            incident.sort(
                key=lambda fi: math.atan2(
                    float(np.dot(d12_verts[fi], tan2)),
                    float(np.dot(d12_verts[fi], ref)),
                )
            )
            faces.append(incident)
        radius_scale = 184.0

    rot = _rot_matrix(math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg))
    r_verts = (verts * radius_scale) @ rot.T
    cx, cy = ss * 0.5, ss * 0.46

    light_dir = np.array([-0.45, -0.60, 0.66], dtype=np.float32)
    light_dir /= np.linalg.norm(light_dir)
    view_dir = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    half_vec = light_dir + view_dir
    half_vec /= np.linalg.norm(half_vec)

    visible_facets = []
    for f_idx, f in enumerate(faces):
        fv = r_verts[f]
        centroid = np.mean(fv, axis=0)
        norm = centroid / max(1e-5, np.linalg.norm(centroid))
        if norm[2] > 0.02:
            pts_2d = []
            for vx, vy, vz in fv:
                persp = 950.0 / max(300.0, 950.0 - vz)
                pts_2d.append((cx + vx * persp, cy + vy * persp))
            visible_facets.append((float(centroid[2]), f_idx, pts_2d, norm))

    # Sort back to front; last facet has largest Z (most front-facing)
    visible_facets.sort(key=lambda item: item[0])

    poly_layer = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(poly_layer, "RGBA")

    for rank, (_, f_idx, pts_2d, norm) in enumerate(visible_facets):
        ndotl = float(np.clip(np.dot(norm, light_dir), 0.12, 1.0))
        ndoth = float(np.clip(np.dot(norm, half_vec), 0.0, 1.0))
        spec = (ndoth ** 20) * 0.65

        # Blend deep crystal and primary crystal + specular
        r = int(np.clip(deep_rgb[0] * (1.0 - ndotl * 0.7) + crystal_rgb[0] * (ndotl * 0.85) + 255 * spec, 0, 255))
        g = int(np.clip(deep_rgb[1] * (1.0 - ndotl * 0.7) + crystal_rgb[1] * (ndotl * 0.85) + 255 * spec, 0, 255))
        b = int(np.clip(deep_rgb[2] * (1.0 - ndotl * 0.7) + crystal_rgb[2] * (ndotl * 0.85) + 255 * spec, 0, 255))

        pdraw.polygon(pts_2d, fill=(r, g, b, 255))

        # Inner facet inset for 3D beveled metallic ridge look
        fcx = sum(p[0] for p in pts_2d) / len(pts_2d)
        fcy = sum(p[1] for p in pts_2d) / len(pts_2d)
        inner_pts = [(fcx + (p[0] - fcx) * 0.84, fcy + (p[1] - fcy) * 0.84) for p in pts_2d]
        filigree_pts = [(fcx + (p[0] - fcx) * 0.76, fcy + (p[1] - fcy) * 0.76) for p in pts_2d]

        # Outer gold/metallic bevel edge + inner dark groove + filigree line
        closed_outer = pts_2d + [pts_2d[0]]
        closed_inner = inner_pts + [inner_pts[0]]
        closed_fil = filigree_pts + [filigree_pts[0]]
        pdraw.line(closed_outer, fill=(*edge_rgb, 255), width=9)
        pdraw.line(closed_inner, fill=(20, 16, 32, 220), width=3)
        pdraw.line(closed_fil, fill=(*edge_rgb, 155), width=2)

        # Vertex rivets
        for vx_2d, vy_2d in pts_2d:
            pdraw.ellipse([vx_2d - 5, vy_2d - 5, vx_2d + 5, vy_2d + 5], fill=(255, 245, 200, 235))

        # Draw numeral on primary front-most facet and secondary visible facets
        is_primary = rank == len(visible_facets) - 1
        if is_primary:
            _draw_engraved_numeral_on_facet(
                pdraw,
                (fcx, fcy),
                primary_numeral,
                scale=22.0 if poly_type == "D8" else (18.0 if poly_type == "D12" else 14.5),
                gold_rgb=edge_rgb,
                glow_rgb=glow_rgb,
            )
        elif rank >= max(0, len(visible_facets) - 1 - len(secondary_numerals)):
            sec_idx = (len(visible_facets) - 2 - rank) % len(secondary_numerals)
            _draw_engraved_numeral_on_facet(
                pdraw,
                (fcx, fcy),
                secondary_numerals[sec_idx],
                scale=13.0 if poly_type == "D8" else (11.0 if poly_type == "D12" else 9.0),
                gold_rgb=edge_rgb,
                glow_rgb=glow_rgb,
            )

    canvas = Image.alpha_composite(canvas, poly_layer)
    return canvas.resize((256, 256), Image.Resampling.LANCZOS)


def render_all_12_dice3d_assets() -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Renders:
    - 1 RTX 4080 master crystal sheet (`dice3d_rtx4080_master_crystal_sheet.png`)
    - 6 3D Isometric Beveled D6 Column Dice (`dice3d_d6_face_1.png` .. `dice3d_d6_face_6.png`)
    - 4 Faction 3D Special Polyhedral Dice (`D8`, `D8`, `D12`, `D20`)
    - 2 Animated 8-Frame `2048x256` 3D Tumbling Roll Sprite Strips (`blue` & `red`)
    """
    DICE3D_DIR.mkdir(parents=True, exist_ok=True)
    master_sheet_info = render_rtx4080_master_crystal_dice_sheet()
    with Image.open(master_sheet_info["path"]) as cim:
        caustic_arr = np.asarray(cim.convert("RGB"), dtype=np.uint8)

    dice_records: List[Dict[str, Any]] = []

    # 1. Six 3D Isometric Beveled D6 faces (1..6)
    for face_val in range(1, 7):
        out_p = DICE3D_DIR / f"dice3d_d6_face_{face_val}.png"
        # Subtle unique angle per face so reflections & silhouette micro-details are distinct
        im = render_3d_d6_sprite(
            top_face=face_val,
            caustic_arr=caustic_arr,
            rx_deg=-34.5 - (face_val % 3) * 0.8,
            ry_deg=-44.0 - (face_val % 2) * 1.5,
            rz_deg=0.0,
            theme="blue",
        )
        im.save(out_p, format="PNG", optimize=True)
        dice_records.append(
            {
                "id": f"dice3d_d6_face_{face_val}",
                "filename": out_p.name,
                "path": str(out_p),
                "die_type": "D6",
                "face_value": face_val,
                "visible_faces": list(D6_VISIBLE_FACE_TRIPLETS[face_val]),
                "width": im.width,
                "height": im.height,
                "mode": im.mode,
                "sha256": compute_sha256(out_p),
                "bytes": out_p.stat().st_size,
            }
        )

    # 2. Four Faction 3D Special Polyhedral Dice (D8, D8, D12, D20)
    special_specs = [
        (
            "dice3d_aether_sapphire_d8",
            "D8",
            (0, 229, 255),
            (12, 36, 108),
            (255, 204, 64),
            (180, 252, 255),
            "8",
            ["2", "4", "6"],
            28.0,
            -38.0,
            8.0,
        ),
        (
            "dice3d_crimson_obsidian_d8",
            "D8",
            (255, 46, 84),
            (36, 6, 20),
            (251, 176, 52),
            (255, 210, 120),
            "8",
            ["3", "5", "7"],
            31.0,
            42.0,
            -6.0,
        ),
        (
            "dice3d_sovereign_gold_d12",
            "D12",
            (255, 184, 0),
            (58, 32, 6),
            (46, 230, 211),
            (255, 248, 190),
            "12",
            ["4", "7", "9", "10", "11"],
            24.0,
            -32.0,
            12.0,
        ),
        (
            "dice3d_kubrart_violet_d20",
            "D20",
            (168, 85, 247),
            (18, 8, 36),
            (255, 224, 130),
            (238, 190, 255),
            "20",
            ["2", "8", "13", "14", "17", "19"],
            20.0,
            -26.0,
            5.0,
        ),
    ]
    for (
        did,
        ptype,
        c_rgb,
        d_rgb,
        e_rgb,
        g_rgb,
        p_num,
        s_nums,
        rx,
        ry,
        rz,
    ) in special_specs:
        out_p = DICE3D_DIR / f"{did}.png"
        im = render_3d_polyhedral_die(
            poly_type=ptype,
            crystal_rgb=c_rgb,
            deep_rgb=d_rgb,
            edge_rgb=e_rgb,
            glow_rgb=g_rgb,
            primary_numeral=p_num,
            secondary_numerals=s_nums,
            caustic_arr=caustic_arr,
            rx_deg=rx,
            ry_deg=ry,
            rz_deg=rz,
        )
        im.save(out_p, format="PNG", optimize=True)
        dice_records.append(
            {
                "id": did,
                "filename": out_p.name,
                "path": str(out_p),
                "die_type": ptype,
                "face_value": int(p_num),
                "width": im.width,
                "height": im.height,
                "mode": im.mode,
                "sha256": compute_sha256(out_p),
                "bytes": out_p.stat().st_size,
            }
        )

    # 3. Two Animated 8-Frame 2048x256 (8 frames of 256x256) 3D Tumbling Roll Sprite Strips
    for theme_name, final_face in [("blue", 6), ("red", 5)]:
        strip_id = f"dice3d_tumble_strip_{theme_name}"
        out_p = DICE3D_DIR / f"{strip_id}.png"
        strip_im = Image.new("RGBA", (2048, 256), (0, 0, 0, 0))
        for frame_idx in range(8):
            t = frame_idx / 7.0
            # Parabolic bounce + damped settle on frame 7
            bounce_y = -68.0 * math.sin(t * math.pi) * (1.0 - 0.35 * t)
            if frame_idx == 7:
                rx_f, ry_f, rz_f = -35.0, -45.0, 0.0
                f_val = final_face
                burst = 1.0
                sc = 1.02
            else:
                rx_f = -35.0 + frame_idx * 52.0
                ry_f = -45.0 + frame_idx * 67.0
                rz_f = frame_idx * 41.0
                f_val = ((frame_idx + (0 if theme_name == "blue" else 2)) % 6) + 1
                burst = 0.35 if frame_idx == 6 else 0.0
                sc = 0.92 + 0.08 * math.sin(t * math.pi)

            frame_im = render_3d_d6_sprite(
                top_face=f_val,
                caustic_arr=caustic_arr,
                rx_deg=rx_f,
                ry_deg=ry_f,
                rz_deg=rz_f,
                y_offset_px=bounce_y,
                scale_factor=sc,
                theme=theme_name,
                impact_burst=burst,
            )
            strip_im.paste(frame_im, (frame_idx * 256, 0))

        strip_im.save(out_p, format="PNG", optimize=True)
        dice_records.append(
            {
                "id": strip_id,
                "filename": out_p.name,
                "path": str(out_p),
                "die_type": "D6_TUMBLE_STRIP_8F",
                "frames": 8,
                "frame_dimensions": [256, 256],
                "width": strip_im.width,
                "height": strip_im.height,
                "mode": strip_im.mode,
                "sha256": compute_sha256(out_p),
                "bytes": out_p.stat().st_size,
            }
        )

    return master_sheet_info, dice_records


# =============================================================================
# PART 2: 24 Unique Cute FFTA Isometric Pixel-Art Chibi Units
# (RTX 4080 Animagine XL 3.1 512x512 -> 64x64 24-Color GBA Pixel Art -> 2x NEAREST 128x128)
# =============================================================================
FFTA_CHIBI_SPECS: List[Dict[str, Any]] = [
    {
        "id": "chibi_01_rosalia_mech_wing_maiden",
        "title": "Rosalia Mech-Wing Maiden",
        "faction": "Aether",
        "card_binding": "h_archangel",
        "seed": 4080601,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "rose pink twin tails hair, small emerald and gold mechanical angel wings, holding ornate "
            "clockwork staff, white and gold dress, large expressive sparkling teal anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (255, 130, 178),
        "hair_shade": (198, 72, 124),
        "eye_color": (46, 230, 211),
        "primary": (255, 210, 96),
        "secondary": (46, 230, 185),
        "trim": (255, 245, 200),
    },
    {
        "id": "chibi_02_celestia_clockwork_valkyrie",
        "title": "Celestia Clockwork Valkyrie",
        "faction": "Valkyria",
        "card_binding": "h_valkyrie",
        "seed": 4080602,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "silver braided hair, valkyrie winged headband, holding crystal spear lance, azure blue and "
            "gold valkyrie armor, large expressive sparkling cyan anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (226, 238, 255),
        "hair_shade": (148, 172, 214),
        "eye_color": (0, 229, 255),
        "primary": (56, 189, 248),
        "secondary": (255, 214, 102),
        "trim": (240, 249, 255),
    },
    {
        "id": "chibi_03_lyra_harmony_automata",
        "title": "Lyra Harmony Automata",
        "faction": "Aether",
        "card_binding": "h_oracle",
        "seed": 4080603,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "lavender wavy hair, holding small golden lyre harp, violet and gold bard dress, "
            "large expressive sparkling gold anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (196, 148, 255),
        "hair_shade": (128, 78, 196),
        "eye_color": (255, 204, 72),
        "primary": (168, 85, 247),
        "secondary": (255, 224, 130),
        "trim": (245, 230, 255),
    },
    {
        "id": "chibi_04_ignia_blaze_pinion",
        "title": "Ignia Blaze Pinion",
        "faction": "Solaris",
        "card_binding": "h_phoenix",
        "seed": 4080604,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "fiery coral red ponytail hair, gold tiara, holding solar flame staff, orange and gold "
            "battle dress, large expressive sparkling amber anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (255, 94, 77),
        "hair_shade": (184, 38, 38),
        "eye_color": (255, 208, 0),
        "primary": (249, 115, 22),
        "secondary": (255, 214, 64),
        "trim": (255, 238, 170),
    },
    {
        "id": "chibi_05_nocturna_eclipse_saint",
        "title": "Nocturna Eclipse Saint",
        "faction": "Abyss",
        "card_binding": "h_seraph",
        "seed": 4080605,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "silver violet hair, crescent tiara, holding spellbook tome, dark violet and gold cleric "
            "robe, large expressive sparkling violet anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (218, 208, 246),
        "hair_shade": (132, 112, 180),
        "eye_color": (192, 38, 211),
        "primary": (126, 34, 206),
        "secondary": (255, 210, 140),
        "trim": (232, 198, 255),
    },
    {
        "id": "chibi_06_archangel_paladin",
        "title": "Archangel Ivalice Paladin",
        "faction": "Solaris",
        "card_binding": "cf_03_celestial_guardian",
        "seed": 4080506,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, spiky golden blonde hair, royal paladin circlet, "
            "flowing cyan cape, holding oversized radiant broadsword, silver and gold plate armor, large expressive "
            "sparkling blue anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 216, 102),
        "hair_shade": (194, 138, 32),
        "eye_color": (0, 210, 255),
        "primary": (240, 246, 255),
        "secondary": (0, 195, 255),
        "trim": (255, 196, 36),
    },
    {
        "id": "chibi_07_eclipse_assassin",
        "title": "Eclipse Shadow Assassin",
        "faction": "Abyss",
        "card_binding": "e_shinobi",
        "seed": 4080507,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, dark indigo hair, shinobi face mask and trailing red "
            "scarf, dual glowing crimson daggers, sleek obsidian stealth ninja outfit, large expressive sparkling "
            "red anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (68, 58, 96),
        "hair_shade": (32, 24, 52),
        "eye_color": (255, 46, 84),
        "primary": (44, 34, 68),
        "secondary": (255, 46, 84),
        "trim": (192, 38, 211),
    },
    {
        "id": "chibi_08_kubrart_eclipse_sovereign",
        "title": "Kubrart Eclipse Sovereign",
        "faction": "Aether",
        "card_binding": "e_eclipse",
        "seed": 4080608,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "spiky white hair, violet crown, holding glowing purple broadsword, black and violet "
            "royal coat, large expressive sparkling violet anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (245, 240, 255),
        "hair_shade": (148, 120, 210),
        "eye_color": (168, 85, 247),
        "primary": (24, 16, 42),
        "secondary": (168, 85, 247),
        "trim": (0, 229, 255),
    },
    {
        "id": "chibi_09_sumi_ronin_blademaster",
        "title": "Sumi Ronin Blademaster",
        "faction": "Abyss",
        "card_binding": "s1_50_obsidian_ronin",
        "seed": 4080609,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "spiky black ponytail hair, red headband, crimson and black samurai kimono armor, "
            "holding katana sword, large expressive sparkling red anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (42, 38, 54),
        "hair_shade": (18, 16, 26),
        "eye_color": (255, 64, 96),
        "primary": (54, 24, 42),
        "secondary": (255, 46, 84),
        "trim": (240, 228, 214),
    },
    {
        "id": "chibi_10_astra_hyper_striker",
        "title": "Astra Hyper Striker",
        "faction": "Valkyria",
        "card_binding": "h_kai",
        "seed": 4080610,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "short spiky cyan hair, goggles on head, blue and gold jacket, mechanical gauntlets, "
            "large expressive sparkling gold anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (0, 229, 255),
        "hair_shade": (14, 132, 188),
        "eye_color": (255, 192, 42),
        "primary": (38, 92, 214),
        "secondary": (0, 229, 255),
        "trim": (255, 204, 64),
    },
    {
        "id": "chibi_11_solaris_obari_mecha",
        "title": "Solaris SD Mecha Vanguard",
        "faction": "Valkyria",
        "card_binding": "e_titan",
        "seed": 4080611,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "futuristic white and cobalt blue mecha knight armor helmet with golden V-fin crest, "
            "holding glowing cyan beam sword and shield, glowing green eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (242, 248, 255),
        "hair_shade": (142, 168, 204),
        "eye_color": (46, 230, 140),
        "primary": (236, 244, 255),
        "secondary": (32, 118, 238),
        "trim": (255, 196, 0),
    },
    {
        "id": "chibi_12_judge_law_arbiter",
        "title": "Ivalice Judge Law Arbiter",
        "faction": "Solaris",
        "card_binding": "h_arbiter",
        "seed": 4080512,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, ornate golden horned judge helmet and heavy gold "
            "filigree plate armor, high collar cape, holding colossal golden law greatsword, glowing jade teal "
            "eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 196, 46),
        "hair_shade": (176, 118, 16),
        "eye_color": (46, 230, 211),
        "primary": (255, 188, 28),
        "secondary": (58, 48, 42),
        "trim": (46, 230, 211),
    },
    {
        "id": "chibi_13_time_mage_chrono",
        "title": "Chronos Time Mage",
        "faction": "Chronos",
        "card_binding": "h_chronos",
        "seed": 4080513,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, blonde hair, oversized crooked crimson and gold pointed "
            "wizard hat, floating brass clockwork gears, holding ornate hourglass staff, large expressive sparkling "
            "amber anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 224, 152),
        "hair_shade": (196, 142, 64),
        "eye_color": (249, 115, 22),
        "primary": (188, 68, 28),
        "secondary": (251, 191, 36),
        "trim": (255, 238, 178),
    },
    {
        "id": "chibi_14_white_monk_brawler",
        "title": "Ivalice White Monk Brawler",
        "faction": "Chronos",
        "card_binding": "s1_47_phantom_cqc_operative",
        "seed": 4080514,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, spiky brown hair, red martial arts headband, white and "
            "orange sleeveless monk gi outfit, glowing golden chi aura fists, dynamic martial arts stance, large "
            "expressive sparkling anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (92, 54, 38),
        "hair_shade": (52, 28, 18),
        "eye_color": (249, 115, 22),
        "primary": (244, 238, 226),
        "secondary": (234, 88, 12),
        "trim": (251, 191, 36),
    },
    {
        "id": "chibi_15_dragoon_sky_lancer",
        "title": "Dragoon Sky Lancer",
        "faction": "Valkyria",
        "card_binding": "s1_16_railgun_dragoon",
        "seed": 4080615,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "silver hair, blue dragon horn helmet, cobalt blue dragoon armor, holding long spear lance, "
            "large expressive sparkling gold anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (112, 198, 255),
        "hair_shade": (48, 112, 184),
        "eye_color": (255, 210, 64),
        "primary": (28, 104, 216),
        "secondary": (0, 229, 255),
        "trim": (255, 208, 76),
    },
    {
        "id": "chibi_16_black_mage_pyro",
        "title": "Ivalice Black Mage Pyro",
        "faction": "Chronos",
        "card_binding": "e_inferno",
        "seed": 4080516,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, classic straw yellow pointed wizard hat casting shadow "
            "over face, glowing bright yellow eyes in shadow, blue and orange wizard robe, holding glowing fireball "
            "magic staff, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (251, 191, 36),
        "hair_shade": (184, 118, 18),
        "eye_color": (255, 232, 56),
        "primary": (38, 64, 156),
        "secondary": (249, 115, 22),
        "trim": (251, 191, 36),
    },
    {
        "id": "chibi_17_gunner_moogle_machinist",
        "title": "Aether Moogle Machinist",
        "faction": "Chronos",
        "card_binding": "s1_21_nanoforge_engineer",
        "seed": 4080517,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, fluffy white moogle ears and red pom-pom on head, "
            "steampunk goggles and amber leather machinist vest, holding oversized brass flintlock cannon, large "
            "expressive sparkling red anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 246, 234),
        "hair_shade": (214, 194, 174),
        "eye_color": (228, 42, 76),
        "primary": (196, 98, 34),
        "secondary": (251, 191, 36),
        "trim": (255, 64, 92),
    },
    {
        "id": "chibi_18_illusionist_star_seer",
        "title": "Illusionist Star Seer",
        "faction": "Aether",
        "card_binding": "cf_10_lunar_oracle",
        "seed": 4080518,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, pastel blue hair, ornate star crown mitre, floating "
            "golden tarot cards and astrolabe ring, royal purple and gold mystic robes, large expressive sparkling "
            "violet anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (164, 218, 255),
        "hair_shade": (88, 138, 204),
        "eye_color": (168, 85, 247),
        "primary": (108, 48, 188),
        "secondary": (255, 224, 130),
        "trim": (164, 238, 255),
    },
    {
        "id": "chibi_19_fencer_red_mage",
        "title": "Fencer Red Mage Duelist",
        "faction": "Abyss",
        "card_binding": "s1_29_spellblade_duelist",
        "seed": 4080619,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "silver hair, red feathered cavalier hat, crimson and white red mage coat, holding rapier sword, "
            "large expressive sparkling green anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (244, 236, 248),
        "hair_shade": (168, 152, 184),
        "eye_color": (46, 214, 188),
        "primary": (214, 34, 68),
        "secondary": (248, 244, 240),
        "trim": (255, 208, 84),
    },
    {
        "id": "chibi_20_summoner_horn_conduit",
        "title": "Summoner Horn Conduit",
        "faction": "Solaris",
        "card_binding": "cf_05_elemental_sprite",
        "seed": 4080620,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, chibi, super deformed, full body, standing, "
            "mint green hair, small white summoner horn on forehead, white and green robe, holding golden rod, "
            "large expressive sparkling gold anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (124, 234, 168),
        "hair_shade": (54, 158, 102),
        "eye_color": (255, 196, 48),
        "primary": (242, 250, 244),
        "secondary": (46, 230, 172),
        "trim": (255, 204, 64),
    },
    {
        "id": "chibi_21_void_golem_construct",
        "title": "Void Golem Construct",
        "faction": "Abyss",
        "card_binding": "e_colossus",
        "seed": 4080621,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "heavy dark obsidian and crimson rune plate armor knight with horned helmet, glowing red visor eyes, "
            "oversized armored gauntlets, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (255, 46, 84),
        "hair_shade": (148, 18, 48),
        "eye_color": (255, 64, 108),
        "primary": (52, 44, 68),
        "secondary": (255, 46, 84),
        "trim": (192, 38, 211),
    },
    {
        "id": "chibi_22_valkyrie_aegis_shield",
        "title": "Valkyrie Aegis Shieldmaiden",
        "faction": "Solaris",
        "card_binding": "s1_37_radiant_valkyrie",
        "seed": 4080522,
        "prompt": (
            "masterpiece, best quality, solo, 1girl, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, golden blonde hair, white winged diadem tiara, golden "
            "and teal paladin armor, holding oversized ornate golden tower shield and spear, large expressive "
            "sparkling teal anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 228, 128),
        "hair_shade": (198, 148, 42),
        "eye_color": (46, 230, 211),
        "primary": (255, 192, 38),
        "secondary": (46, 230, 211),
        "trim": (255, 248, 220),
    },
    {
        "id": "chibi_23_necromancer_lich_lord",
        "title": "Necromancer Lich Archon",
        "faction": "Abyss",
        "card_binding": "e_reaper",
        "seed": 4080623,
        "render_res": 768,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, chibi, super deformed, full body, standing, "
            "pale teal hair, bone crown, dark purple and teal necromancer robe, holding skull staff, "
            "large expressive sparkling cyan anime eyes, "
            "simple background, flat solid dark navy blue background"
        ),
        "hair_color": (184, 248, 236),
        "hair_shade": (88, 168, 158),
        "eye_color": (46, 230, 211),
        "primary": (48, 22, 68),
        "secondary": (46, 230, 211),
        "trim": (218, 188, 255),
    },
    {
        "id": "chibi_24_omega_sovereign_captain",
        "title": "Omega Sovereign Captain",
        "faction": "Aether",
        "card_binding": "s1_60_omega_chronos_prime",
        "seed": 4080524,
        "prompt": (
            "masterpiece, best quality, solo, 1boy, cute super deformed 2.5 head proportion chibi character, "
            "full body standing sprite, tactical RPG unit, radiant golden hair, prismatic crown crest, glowing "
            "cyan and violet wings, ornate purple and gold sovereign commander armor, holding floating holographic "
            "cube orb, large expressive sparkling cyan anime eyes, simple flat solid dark navy background, centered full body chibi"
        ),
        "hair_color": (255, 234, 156),
        "hair_shade": (196, 146, 52),
        "eye_color": (0, 229, 255),
        "primary": (148, 68, 242),
        "secondary": (0, 229, 255),
        "trim": (255, 204, 52),
    },
]


def _render_raw_rtx4080_chibi(spec: Dict[str, Any], raw_cache_dir: Path) -> Path:
    """
    Renders a full-body 2.5-head chibi sprite on Node 30 RTX 4080 ComfyUI
    (`animagineXLV31_v31.safetensors`, steps=8, cfg=6.0, euler_ancestral).
    """
    raw_cache_dir.mkdir(parents=True, exist_ok=True)
    cid = spec["id"]
    render_res = int(spec.get("render_res", 512))
    out_raw = raw_cache_dir / f"{cid}_rtx4080_{render_res}_{spec['seed']}.png"
    if out_raw.exists() and out_raw.stat().st_size > 25_000:
        return out_raw
    legacy_raw = raw_cache_dir / f"{cid}_rtx4080_512.png"
    if legacy_raw.exists() and legacy_raw.stat().st_size > 25_000:
        return legacy_raw

    negative_text = (
        "multiple views, sprite sheet, reference sheet, grid, multiple girls, multiple boys, "
        "2girls, 2boys, card, box, frame, border, square background, circular background, "
        "window, pillar, gate, magic circle, halo behind back, text, watermark, signature, "
        "logo, blurry, lowres, complex background, scenery, cropped, close up, portrait only, bad anatomy"
    )
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 6.0,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": int(spec["seed"]),
                "steps": 8,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT_NAME},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": render_res, "width": render_res},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": spec["prompt"]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative_text},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"FFTA_Chibi_{cid}", "images": ["8", 0]},
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

    for _ in range(480):
        time.sleep(0.25)
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10) as hresp:
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
                    urllib.request.urlretrieve(f"{COMFYUI_URL}/view?{qs}", out_raw)
                    print(
                        f"  [RTX 4080 Chibi 512x512] {cid}: {out_raw.stat().st_size}B in {round(time.time() - t0, 2)}s",
                        flush=True,
                    )
                    return out_raw
    raise TimeoutError(f"Timed out rendering RTX 4080 chibi {cid}")


def _extract_foreground_and_convert_to_64x64_gba_pixel_art(
    raw_img_path: Path,
    spec: Dict[str, Any],
) -> Tuple[Image.Image, Image.Image]:
    """
    1. Extracts the foreground chibi character mask from the 512x512 RTX 4080 render
       via border-seeded BFS flood-fill over bilinearly-interpolated corner background color
       and Sobel edge-stopping.
    2. Crops & fits the full chibi character into a `64x64` pixel-art grid
       (`BILINEAR` downscale -> `.quantize(colors=24, method=FASTOCTREE)` GBA palette ->
       binary alpha mask `alpha > 96 -> 255` -> 1px dark indigo sel-out outline `(22, 16, 36, 255)`
       + soft isometric ground shadow).
    3. Builds Frame 1 (`_sheet.png` right frame) by shifting the `64x64` sprite `(dx=+1, dy=-2)`
       and drawing a crisp pixel-art weapon slash arc & 4-point star sparkles in `secondary` & `trim`.
    4. Upscales both `64x64` frames exact `2x` via `Image.Resampling.NEAREST` to `128x128` RGBA.
    """
    with Image.open(raw_img_path) as raw_im:
        rgb_im = raw_im.convert("RGB")
        cid = spec["id"]
        # Pre-crop or clean specific RTX 4080 renders before background flood-fill
        if cid == "chibi_01_rosalia_mech_wing_maiden" and rgb_im.size == (768, 768):
            arr_fix = np.asarray(rgb_im, dtype=np.float32).copy()
            # Repair horizontal blind bar across hair/forehead (y=350..404) inside character x=220..548
            for yy_f in range(350, 405):
                alpha_f = (yy_f - 350.0) / 55.0
                arr_fix[yy_f, 225:545] = (
                    (1.0 - alpha_f) * arr_fix[348, 225:545] + alpha_f * arr_fix[406, 225:545]
                )
            # Replace striped background outside character silhouette with uniform corner color
            yy_g, xx_g = np.mgrid[0:768, 0:768].astype(np.float32)
            head_body_mask = (
                (((xx_g - 384.0) / 160.0) ** 2 + ((yy_g - 430.0) / 145.0) ** 2 < 1.0)
                | (
                    (yy_g > 460)
                    & (yy_g < 595)
                    & (np.abs(xx_g - 384.0) < 210)
                    & (arr_fix[:, :, 1] > arr_fix[:, :, 2] * 0.85)
                )
            )
            bg_fill = np.array([205.0, 230.0, 250.0], dtype=np.float32)
            for c_i in range(3):
                arr_fix[:, :, c_i] = np.where(head_body_mask, arr_fix[:, :, c_i], bg_fill[c_i])
            rgb_im = Image.fromarray(np.clip(arr_fix, 0, 255).astype(np.uint8), mode="RGB").crop(
                (160, 240, 608, 630)
            )
        elif cid == "chibi_08_kubrart_eclipse_sovereign":
            arr_fix = np.asarray(rgb_im, dtype=np.float32).copy()
            H0, W0, _ = arr_fix.shape
            yy_g, xx_g = np.mgrid[0:H0, 0:W0].astype(np.float32)
            bg_tl = np.median(arr_fix[:24, :24], axis=(0, 1))
            # Clear the dark diagonal top-right corner bar and white hair-adjacent background
            is_bg_8 = (
                ((yy_g < 175) & (xx_g > 280) & (np.mean(arr_fix, axis=2) < 135))
                | ((np.mean(arr_fix, axis=2) > 212) & ((yy_g < 95) | (xx_g < 155) | (xx_g > 610) | (yy_g > 700)))
            )
            for c_i in range(3):
                arr_fix[:, :, c_i] = np.where(is_bg_8, bg_tl[c_i], arr_fix[:, :, c_i])
            rgb_im = Image.fromarray(np.clip(arr_fix, 0, 255).astype(np.uint8), mode="RGB")
        elif cid == "chibi_20_summoner_horn_conduit":
            arr_fix = np.asarray(rgb_im, dtype=np.float32).copy()
            H0, W0, _ = arr_fix.shape
            yy_g, xx_g = np.mgrid[0:H0, 0:W0].astype(np.float32)
            # Isolate central horned summoner chibi from side window panes
            keep_mask = (
                (((xx_g - 256.0) / 118.0) ** 2 + ((yy_g - 235.0) / 195.0) ** 2 < 1.0)
                | ((yy_g >= 245) & (yy_g <= 345) & (np.abs(xx_g - 256.0) < 165) & (arr_fix[:, :, 1] < 140))
            )
            bg_fill = np.array([24.0, 42.0, 56.0], dtype=np.float32)
            for c_i in range(3):
                arr_fix[:, :, c_i] = np.where(keep_mask, arr_fix[:, :, c_i], bg_fill[c_i])
            rgb_im = Image.fromarray(np.clip(arr_fix, 0, 255).astype(np.uint8), mode="RGB").crop(
                (80, 12, 432, 442)
            )
        elif cid == "chibi_21_void_golem_construct":
            # Crop right-hand solo Void Golem construct and strip outer frame
            rgb_im = rgb_im.crop((232, 46, 496, 488))
        elif cid == "chibi_23_necromancer_lich_lord":
            arr_fix = np.asarray(rgb_im, dtype=np.float32).copy()
            # Crop right-hand solo Necromancer Lich and clear background outside silhouette
            sub = arr_fix[48:436, 232:496].copy()
            sh, sw, _ = sub.shape
            yy_g, xx_g = np.mgrid[0:sh, 0:sw].astype(np.float32)
            lich_keep = (((xx_g - sw * 0.5) / (sw * 0.44)) ** 2 + ((yy_g - sh * 0.50) / (sh * 0.44)) ** 2) < 1.0
            bg_fill = np.array([22.0, 48.0, 58.0], dtype=np.float32)
            for c_i in range(3):
                sub[:, :, c_i] = np.where(lich_keep, sub[:, :, c_i], bg_fill[c_i])
            rgb_im = Image.fromarray(np.clip(sub, 0, 255).astype(np.uint8), mode="RGB")

        # Boost contrast and color saturation before pixel-art quantization
        rgb_im = ImageEnhance.Contrast(rgb_im).enhance(1.15)
        rgb_im = ImageEnhance.Color(rgb_im).enhance(1.20)
        arr = np.asarray(rgb_im, dtype=np.float32)

    H, W, _ = arr.shape
    # Sample 4 corner 20x20 patches to build a bilinear background color reference
    c_tl = np.median(arr[:20, :20], axis=(0, 1))
    c_tr = np.median(arr[:20, W - 20 :], axis=(0, 1))
    c_bl = np.median(arr[H - 20 :, :20], axis=(0, 1))
    c_br = np.median(arr[H - 20 :, W - 20 :], axis=(0, 1))

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / float(W - 1)
    v = yy / float(H - 1)
    bg_ref = (
        c_tl[np.newaxis, np.newaxis, :] * ((1 - u) * (1 - v))[:, :, np.newaxis]
        + c_tr[np.newaxis, np.newaxis, :] * (u * (1 - v))[:, :, np.newaxis]
        + c_bl[np.newaxis, np.newaxis, :] * ((1 - u) * v)[:, :, np.newaxis]
        + c_br[np.newaxis, np.newaxis, :] * (u * v)[:, :, np.newaxis]
    )

    color_dist = np.sqrt(np.sum((arr - bg_ref) ** 2, axis=2))
    # Also compute Sobel gradient magnitude to stop flood-fill at crisp character contours
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    gx[:, 1:-1] = np.abs(lum[:, 2:] - lum[:, :-2])
    gy[1:-1, :] = np.abs(lum[2:, :] - lum[:-2, :])
    grad_mag = np.hypot(gx, gy)

    # Downsample to 128x128 for fast, clean border BFS flood-fill
    dist_128 = np.asarray(
        Image.fromarray(np.clip(color_dist, 0, 255).astype(np.uint8)).resize((128, 128), Image.Resampling.BILINEAR),
        dtype=np.float32,
    )
    grad_128 = np.asarray(
        Image.fromarray(np.clip(grad_mag, 0, 255).astype(np.uint8)).resize((128, 128), Image.Resampling.BILINEAR),
        dtype=np.float32,
    )

    bg_candidate = ((dist_128 < 58.0) & (grad_128 < 46.0)) | ((dist_128 < 96.0) & (grad_128 < 24.0))
    # Protect central torso/head core from ever being flooded
    y128, x128 = np.mgrid[0:128, 0:128].astype(np.float32)
    core_ellipse = ((x128 - 64.0) / 18.0) ** 2 + ((y128 - 66.0) / 28.0) ** 2 < 1.0
    bg_candidate[core_ellipse] = False

    visited = np.zeros((128, 128), dtype=bool)
    queue: List[Tuple[int, int]] = []
    for x_b in range(128):
        for y_b in (0, 127):
            if bg_candidate[y_b, x_b] and not visited[y_b, x_b]:
                visited[y_b, x_b] = True
                queue.append((y_b, x_b))
    for y_b in range(128):
        for x_b in (0, 127):
            if bg_candidate[y_b, x_b] and not visited[y_b, x_b]:
                visited[y_b, x_b] = True
                queue.append((y_b, x_b))

    head = 0
    while head < len(queue):
        cy_q, cx_q = queue[head]
        head += 1
        for ny_q, nx_q in ((cy_q - 1, cx_q), (cy_q + 1, cx_q), (cy_q, cx_q - 1), (cy_q, cx_q + 1)):
            if 0 <= ny_q < 128 and 0 <= nx_q < 128 and not visited[ny_q, nx_q] and bg_candidate[ny_q, nx_q]:
                visited[ny_q, nx_q] = True
                queue.append((ny_q, nx_q))

    fg_128 = (~visited).astype(np.uint8) * 255
    # Upscale mask back to 512x512 and erode 1px to remove background fringe
    fg_512 = Image.fromarray(fg_128, mode="L").resize((W, H), Image.Resampling.BILINEAR)
    fg_512 = fg_512.filter(ImageFilter.MinFilter(3))

    bbox = fg_512.getbbox()
    if not bbox or (bbox[2] - bbox[0] < 64) or (bbox[3] - bbox[1] < 64):
        bbox = (48, 28, W - 48, H - 28)

    bx0, by0, bx1, by1 = bbox
    bw, bh = max(1, bx1 - bx0), max(1, by1 - by0)
    crop_rgb = rgb_im.crop((bx0, by0, bx1, by1))
    crop_mask = fg_512.crop((bx0, by0, bx1, by1))

    # Fit cropped chibi into a 54x54 box inside the 64x64 pixel-art grid
    max_dim = 54
    scale = min(max_dim / float(bw), max_dim / float(bh))
    tw = max(16, min(56, int(round(bw * scale))))
    th = max(16, min(56, int(round(bh * scale))))

    small_rgb = crop_rgb.resize((tw, th), Image.Resampling.BILINEAR)
    # Quantize to crisp 24-color GBA pixel-art palette
    quant_rgb = small_rgb.quantize(colors=24, method=Image.Quantize.FASTOCTREE).convert("RGB")
    small_mask = crop_mask.resize((tw, th), Image.Resampling.BILINEAR)

    def _compose_64x64_frame(dx_off: int, dy_off: int, add_strike_fx: bool) -> Image.Image:
        canvas_64 = np.zeros((64, 64, 4), dtype=np.uint8)

        # 1. Soft isometric diamond/ellipse ground shadow at y = 56..61
        for sy in range(56, 62):
            ry_norm = (sy - 58.5) / 3.0
            rx_span = int(round(15.0 * math.sqrt(max(0.0, 1.0 - ry_norm * ry_norm))))
            for sx in range(32 - rx_span, 32 + rx_span + 1):
                if 0 <= sx < 64:
                    canvas_64[sy, sx] = (14, 10, 26, 145)

        # 2. Place quantized chibi RGB + binary alpha > 96 -> 255
        ox = (64 - tw) // 2 + dx_off
        oy = 59 - th + dy_off
        q_arr = np.asarray(quant_rgb, dtype=np.uint8)
        m_arr = np.asarray(small_mask, dtype=np.uint8) > 96

        char_mask_64 = np.zeros((64, 64), dtype=bool)
        for yy_c in range(th):
            dst_y = oy + yy_c
            if 1 <= dst_y < 62:
                for xx_c in range(tw):
                    dst_x = ox + xx_c
                    if 1 <= dst_x < 63 and m_arr[yy_c, xx_c]:
                        canvas_64[dst_y, dst_x, :3] = q_arr[yy_c, xx_c]
                        canvas_64[dst_y, dst_x, 3] = 255
                        char_mask_64[dst_y, dst_x] = True

        # 3. 1px dark indigo sel-out pixel outline (22, 16, 36, 255) around the 64x64 silhouette
        outline_col = (22, 16, 36, 255)
        for yy_o in range(1, 63):
            for xx_o in range(1, 63):
                if not char_mask_64[yy_o, xx_o]:
                    if (
                        char_mask_64[yy_o - 1, xx_o]
                        or char_mask_64[yy_o + 1, xx_o]
                        or char_mask_64[yy_o, xx_o - 1]
                        or char_mask_64[yy_o, xx_o + 1]
                    ):
                        canvas_64[yy_o, xx_o] = outline_col

        # 4. Frame 1 Weapon Slash Arc & 4-Point Star Sparkles in character secondary & trim colors
        if add_strike_fx:
            sc_rgba = (*spec["secondary"], 255)
            tr_rgba = (*spec["trim"], 255)
            white_rgba = (255, 255, 255, 255)
            slash_mask = np.zeros((64, 64), dtype=bool)
            for s_ang in range(-18, 19):
                rad = s_ang * 0.055
                sx_arc = int(round(48 + 11.0 * math.cos(rad)))
                sy_arc = int(round(32 + 18.0 * math.sin(rad)))
                for thick in range(3):
                    px_a = sx_arc - thick
                    if 1 <= px_a < 63 and 1 <= sy_arc < 62:
                        canvas_64[sy_arc, px_a] = white_rgba if thick == 0 else (tr_rgba if thick == 1 else sc_rgba)
                        slash_mask[sy_arc, px_a] = True

            # 4-point star sparkles
            for sp_x, sp_y in [(10, 12), (54, 10), (57, 46)]:
                for d_sp in range(-3, 4):
                    if 1 <= sp_x + d_sp < 63 and 1 <= sp_y < 63:
                        canvas_64[sp_y, sp_x + d_sp] = tr_rgba
                        slash_mask[sp_y, sp_x + d_sp] = True
                    if 1 <= sp_x < 63 and 1 <= sp_y + d_sp < 63:
                        canvas_64[sp_y + d_sp, sp_x] = tr_rgba
                        slash_mask[sp_y + d_sp, sp_x] = True
                canvas_64[sp_y, sp_x] = white_rgba

            # Outline the slash & sparkles slightly where transparent
            for yy_s in range(1, 63):
                for xx_s in range(1, 63):
                    if canvas_64[yy_s, xx_s, 3] == 0:
                        if (
                            slash_mask[yy_s - 1, xx_s]
                            or slash_mask[yy_s + 1, xx_s]
                            or slash_mask[yy_s, xx_s - 1]
                            or slash_mask[yy_s, xx_s + 1]
                        ):
                            canvas_64[yy_s, xx_s] = outline_col

        return Image.fromarray(canvas_64, mode="RGBA")

    f0_64 = _compose_64x64_frame(dx_off=0, dy_off=0, add_strike_fx=False)
    f1_64 = _compose_64x64_frame(dx_off=1, dy_off=-2, add_strike_fx=True)

    # Upscale 64x64 exact 2x via NEAREST to 128x128 RGBA
    f0_128 = f0_64.resize((128, 128), Image.Resampling.NEAREST)
    f1_128 = f1_64.resize((128, 128), Image.Resampling.NEAREST)
    return f0_128, f1_128


def render_all_24_ffta_chibi_units() -> List[Dict[str, Any]]:
    """
    Generates all 24 unique 128x128 (64x64 native GBA 24-color pixel grid upscaled 2x via NEAREST)
    FFTA pixel-art chibi sprites + 24 256x128 2-frame animated sprite sheets (`_sheet.png`),
    backed by Node 30 RTX 4080 `animagineXLV31_v31.safetensors` full-body chibi renders.
    """
    CHIBI_DIR.mkdir(parents=True, exist_ok=True)
    raw_cache_dir = CHIBI_DIR / "_rtx4080_raw_512"
    raw_cache_dir.mkdir(parents=True, exist_ok=True)
    records: List[Dict[str, Any]] = []

    for idx, spec in enumerate(FFTA_CHIBI_SPECS):
        cid = spec["id"]
        static_path = CHIBI_DIR / f"{cid}.png"
        sheet_path = CHIBI_DIR / f"{cid}_sheet.png"

        raw_512_path = _render_raw_rtx4080_chibi(spec, raw_cache_dir)
        f0_128, f1_128 = _extract_foreground_and_convert_to_64x64_gba_pixel_art(raw_512_path, spec)

        f0_128.save(static_path, format="PNG", optimize=True)

        sheet_256x128 = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
        sheet_256x128.paste(f0_128, (0, 0))
        sheet_256x128.paste(f1_128, (128, 0))
        sheet_256x128.save(sheet_path, format="PNG", optimize=True)

        records.append(
            {
                "index": idx + 1,
                "id": cid,
                "title": spec["title"],
                "faction": spec["faction"],
                "card_binding": spec["card_binding"],
                "rtx4080_raw_512_path": str(raw_512_path),
                "native_pixel_grid": [64, 64],
                "palette_colors": 24,
                "upscale_factor": 2,
                "upscale_filter": "NEAREST",
                "static_sprite": {
                    "filename": static_path.name,
                    "path": str(static_path),
                    "width": 128,
                    "height": 128,
                    "mode": "RGBA",
                    "sha256": compute_sha256(static_path),
                    "bytes": static_path.stat().st_size,
                },
                "animated_sheet_2f": {
                    "filename": sheet_path.name,
                    "path": str(sheet_path),
                    "frames": 2,
                    "width": 256,
                    "height": 128,
                    "mode": "RGBA",
                    "sha256": compute_sha256(sheet_path),
                    "bytes": sheet_path.stat().st_size,
                },
            }
        )

    return records


# =============================================================================
# PART 3: Mirror Assets to WebPlayable & Unity Resources + Build 2400x1600 Showcase
# =============================================================================
def mirror_assets_to_web_and_unity() -> Dict[str, Any]:
    ensure_unity_folder_meta(UNITY_CARDFRONT_RES_DIR)
    UNITY_DICE3D_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_CHIBI_DIR.mkdir(parents=True, exist_ok=True)
    ensure_unity_folder_meta(UNITY_DICE3D_DIR)
    ensure_unity_folder_meta(UNITY_CHIBI_DIR)

    # Mirror Dice3D
    if not os.path.islink(WEB_GEN_ART_DIR) and not os.path.islink(WEB_DICE3D_DIR):
        WEB_DICE3D_DIR.mkdir(parents=True, exist_ok=True)
        if not os.path.samefile(DICE3D_DIR, WEB_DICE3D_DIR):
            for f in sorted(DICE3D_DIR.glob("*.png")):
                shutil.copy2(f, WEB_DICE3D_DIR / f.name)

    dice_unity_count = 0
    for f in sorted(DICE3D_DIR.glob("*.png")):
        dst = UNITY_DICE3D_DIR / f.name
        shutil.copy2(f, dst)
        ensure_unity_png_meta(dst)
        dice_unity_count += 1

    # Mirror FFAChibiUnits
    if not os.path.islink(WEB_GEN_ART_DIR) and not os.path.islink(WEB_CHIBI_DIR):
        WEB_CHIBI_DIR.mkdir(parents=True, exist_ok=True)
        if not os.path.samefile(CHIBI_DIR, WEB_CHIBI_DIR):
            for f in sorted(CHIBI_DIR.glob("*.png")):
                shutil.copy2(f, WEB_CHIBI_DIR / f.name)

    chibi_unity_count = 0
    for f in sorted(CHIBI_DIR.glob("*.png")):
        dst = UNITY_CHIBI_DIR / f.name
        shutil.copy2(f, dst)
        ensure_unity_png_meta(dst)
        chibi_unity_count += 1

    return {
        "web_dice3d_accessible": len(list(WEB_DICE3D_DIR.glob("*.png"))),
        "web_chibi_accessible": len(list(WEB_CHIBI_DIR.glob("*.png"))),
        "unity_dice3d_mirrored": dice_unity_count,
        "unity_chibi_mirrored": chibi_unity_count,
    }


def _render_25d_tilted_card_slab_with_chibi(
    card_portrait_path: Path,
    chibi_sprite_path: Path,
    die_sprite_path: Path,
    accent_rgb: Tuple[int, int, int],
) -> Image.Image:
    """
    Renders a 360x420 RGBA 2.5D Isometric Tilted Card Slab with:
    - 3D extruded metallic gold/obsidian slab thickness & drop shadow
    - Perspective-foreshortened card portrait on the slab top surface
    - Cute FFTA Pixel-Art Chibi Unit standing upright in 2.5D pop-up relief on top of the card!
    - Floating 3D polyhedral die badge in the corner
    """
    cw, ch = 360, 420
    panel = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel, "RGBA")

    # 1. Isometric tilted slab geometry
    top_quad = [(72, 168), (308, 138), (336, 356), (36, 388)]
    slab_depth = 16

    # Shadow under slab
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sh, "RGBA")
    sdraw.polygon(
        [(x + 8, y + slab_depth + 14) for x, y in top_quad],
        fill=(4, 6, 16, 185),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(radius=12))
    panel = Image.alpha_composite(panel, sh)
    draw = ImageDraw.Draw(panel, "RGBA")

    # Extruded 3D side walls of the card slab
    bottom_edge = [
        top_quad[3],
        top_quad[2],
        (top_quad[2][0], top_quad[2][1] + slab_depth),
        (top_quad[3][0], top_quad[3][1] + slab_depth),
    ]
    left_edge = [
        top_quad[0],
        top_quad[3],
        (top_quad[3][0], top_quad[3][1] + slab_depth),
        (top_quad[0][0], top_quad[0][1] + slab_depth),
    ]
    draw.polygon(bottom_edge, fill=(42, 32, 18, 255), outline=(*accent_rgb, 220))
    draw.polygon(left_edge, fill=(68, 52, 24, 255), outline=(255, 204, 72, 220))

    # Warp/project the 600x800 card portrait onto the tilted top_quad
    if card_portrait_path.exists():
        with Image.open(card_portrait_path) as pim:
            src_card = pim.convert("RGBA").resize((240, 320), Image.Resampling.LANCZOS)
    else:
        src_card = Image.new("RGBA", (240, 320), (*accent_rgb, 255))

    # Bilinear Inverse Sampling onto top_quad
    warped_slab = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    src_arr = np.asarray(src_card, dtype=np.uint8)
    dst_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
    p00, p10, p11, p01 = [np.array(p, dtype=np.float32) for p in top_quad]
    for sv in range(320):
        tv = sv / 319.0
        left_pt = p00 * (1.0 - tv) + p01 * tv
        right_pt = p10 * (1.0 - tv) + p11 * tv
        for su in range(240):
            tu = su / 239.0
            pt = left_pt * (1.0 - tu) + right_pt * tu
            ix, iy = int(round(pt[0])), int(round(pt[1]))
            if 0 <= ix < cw and 0 <= iy < ch:
                dst_arr[iy, ix] = src_arr[sv, su]
                if ix + 1 < cw:
                    dst_arr[iy, ix + 1] = src_arr[sv, su]
                if iy + 1 < ch:
                    dst_arr[iy + 1, ix] = src_arr[sv, su]

    warped_slab = Image.fromarray(dst_arr, mode="RGBA")
    panel = Image.alpha_composite(panel, warped_slab)
    draw = ImageDraw.Draw(panel, "RGBA")

    # Beveled gold & faction border around the tilted slab top
    closed_top = top_quad + [top_quad[0]]
    draw.line(closed_top, fill=(255, 210, 82, 255), width=5)
    draw.line(closed_top, fill=(*accent_rgb, 235), width=2)

    # Holographic summoning circle on the card slab center
    cx_slab, cy_slab = 186, 256
    for r_w, r_h, alpha in [(74, 34, 150), (56, 25, 215)]:
        draw.ellipse(
            [cx_slab - r_w, cy_slab - r_h, cx_slab + r_w, cy_slab + r_h],
            outline=(*accent_rgb, alpha),
            width=3,
        )

    # 2. Pop-up 2.5D FFTA Pixel-Art Chibi Unit standing upright on the card slab!
    with Image.open(chibi_sprite_path) as cim:
        chibi_up = cim.convert("RGBA").resize((192, 192), Image.Resampling.NEAREST)
    panel.alpha_composite(chibi_up, (cx_slab - 96, cy_slab - 158))

    # 3. Floating 3D Beveled Polyhedral Die next to the slab
    if die_sprite_path.exists():
        with Image.open(die_sprite_path) as dim:
            die_thumb = dim.convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
        panel.alpha_composite(die_thumb, (16, 48))

    return panel


def build_2400x1600_showcase_sheet() -> Dict[str, Any]:
    """
    Builds the 2400x1600 3D Dice, 2.5D Card Slab & FFTA Pixel-Chibi Showcase Sheet:
    - Top section (y = 0..410): All 12 3D Beveled Polyhedral Magicite Dice (D6 faces 1-6 + D8/D12/D20 + Tumble preview)
    - Middle section (y = 410..870): 6 2.5D Isometric Tilted Card Slabs with cute FFTA Pixel-Art Chibi Units standing in 2.5D pop-up relief on top of the cards
    - Bottom section (y = 870..1600): All 24 unique FFTA Isometric Pixel-Art Chibi Unit sprites (4x NEAREST crisp pixel art) in an Ivalice 8x3 tactical diorama grid
    """
    W, H = 2400, 1600
    atlas = Image.new("RGBA", (W, H), (14, 12, 26, 255))
    draw = ImageDraw.Draw(atlas, "RGBA")

    # Subtle tactical background grid lines
    for gx in range(0, W, 60):
        draw.line([(gx, 0), (gx, H)], fill=(32, 28, 56, 120), width=1)
    for gy in range(0, H, 60):
        draw.line([(0, gy), (W, gy)], fill=(32, 28, 56, 120), width=1)

    # Section dividers
    draw.rectangle([16, 14, W - 16, 396], outline=(0, 229, 255, 180), width=2)
    draw.rectangle([16, 410, W - 16, 862], outline=(255, 196, 46, 180), width=2)
    draw.rectangle([16, 876, W - 16, H - 16], outline=(168, 85, 247, 180), width=2)

    # TOP SECTION: 12 3D Polyhedral Game Dice (10 individual 256x256 dice + 2 animated tumble strips)
    top_dice_files = [
        "dice3d_d6_face_1.png",
        "dice3d_d6_face_2.png",
        "dice3d_d6_face_3.png",
        "dice3d_d6_face_4.png",
        "dice3d_d6_face_5.png",
        "dice3d_d6_face_6.png",
        "dice3d_aether_sapphire_d8.png",
        "dice3d_crimson_obsidian_d8.png",
        "dice3d_sovereign_gold_d12.png",
        "dice3d_kubrart_violet_d20.png",
    ]
    for idx, fname in enumerate(top_dice_files):
        p = DICE3D_DIR / fname
        x0 = 32 + idx * 234
        y0 = 28
        draw.rounded_rectangle([x0, y0, x0 + 220, y0 + 220], radius=16, fill=(22, 20, 40, 230), outline=(88, 128, 214, 190), width=2)
        with Image.open(p) as dim:
            d_img = dim.convert("RGBA").resize((208, 208), Image.Resampling.LANCZOS)
        atlas.alpha_composite(d_img, (x0 + 6, y0 + 6))

    # Paste both 8-frame 3D Tumble Strips right below the 10 dice in the Top Section (y = 258..388)
    for s_idx, strip_name in enumerate(["dice3d_tumble_strip_blue.png", "dice3d_tumble_strip_red.png"]):
        sp = DICE3D_DIR / strip_name
        sx0 = 36 + s_idx * 1176
        sy0 = 258
        draw.rounded_rectangle([sx0, sy0, sx0 + 1152, sy0 + 128], radius=12, fill=(20, 16, 36, 235), outline=(255, 196, 56, 180), width=2)
        with Image.open(sp) as sim:
            s_thumb = sim.convert("RGBA").resize((1024, 124), Image.Resampling.LANCZOS)
        atlas.alpha_composite(s_thumb, (sx0 + 64, sy0 + 2))

    # MIDDLE SECTION: 6 2.5D Isometric Tilted Card Slabs with Pop-Up FFTA Pixel-Art Chibi Units
    slab_Showcase_bindings = [
        ("h_archangel.png", "chibi_01_rosalia_mech_wing_maiden.png", "dice3d_d6_face_6.png", (168, 85, 247)),
        ("h_valkyrie.png", "chibi_02_celestia_clockwork_valkyrie.png", "dice3d_aether_sapphire_d8.png", (0, 229, 255)),
        ("h_phoenix.png", "chibi_04_ignia_blaze_pinion.png", "dice3d_sovereign_gold_d12.png", (255, 184, 0)),
        ("h_arbiter.png", "chibi_12_judge_law_arbiter.png", "dice3d_d6_face_5.png", (46, 230, 211)),
        ("e_eclipse.png", "chibi_08_kubrart_eclipse_sovereign.png", "dice3d_kubrart_violet_d20.png", (192, 38, 211)),
        ("e_titan.png", "chibi_11_solaris_obari_mecha.png", "dice3d_crimson_obsidian_d8.png", (255, 46, 84)),
    ]
    for idx, (c_file, ch_file, d_file, acc_rgb) in enumerate(slab_Showcase_bindings):
        slab_im = _render_25d_tilted_card_slab_with_chibi(
            MASTERED_CARDS_DIR / c_file,
            CHIBI_DIR / ch_file,
            DICE3D_DIR / d_file,
            acc_rgb,
        )
        atlas.alpha_composite(slab_im, (34 + idx * 392, 422))

    # BOTTOM SECTION: All 24 Unique FFTA Isometric Pixel-Art Chibi Units (8 cols x 3 rows)
    cols_b = 8
    cell_w = (W - 64) // cols_b  # 292
    cell_h = 228
    for idx, spec in enumerate(FFTA_CHIBI_SPECS):
        c = idx % cols_b
        r = idx // cols_b
        bx = 32 + c * cell_w
        by = 890 + r * cell_h

        # Isometric tactical tile pedestal
        tile_cx = bx + cell_w // 2
        tile_cy = by + 168
        iso_diamond = [
            (tile_cx, tile_cy - 34),
            (tile_cx + 86, tile_cy),
            (tile_cx, tile_cy + 34),
            (tile_cx - 86, tile_cy),
        ]
        iso_side_l = [
            (tile_cx - 86, tile_cy),
            (tile_cx, tile_cy + 34),
            (tile_cx, tile_cy + 50),
            (tile_cx - 86, tile_cy + 16),
        ]
        iso_side_r = [
            (tile_cx, tile_cy + 34),
            (tile_cx + 86, tile_cy),
            (tile_cx + 86, tile_cy + 16),
            (tile_cx, tile_cy + 50),
        ]
        draw.polygon(iso_side_l, fill=(44, 58, 42, 255), outline=(24, 32, 22, 255))
        draw.polygon(iso_side_r, fill=(32, 42, 30, 255), outline=(20, 26, 18, 255))
        draw.polygon(iso_diamond, fill=(68, 96, 62, 255), outline=(*(spec["primary"]), 220))

        # Paste crisp 4x NEAREST FFTA chibi sprite (128x128) + small Strike preview (96x96)
        sheet_p = CHIBI_DIR / f"{spec['id']}_sheet.png"
        with Image.open(sheet_p) as shim:
            idle_128 = shim.crop((0, 0, 128, 128))
            strike_128 = shim.crop((128, 0, 256, 128)).resize((96, 96), Image.Resampling.NEAREST)
        atlas.alpha_composite(idle_128, (tile_cx - 78, tile_cy - 116))
        atlas.alpha_composite(strike_128, (tile_cx + 12, tile_cy - 92))

    final_rgb = atlas.convert("RGB")
    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    final_rgb.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    shutil.copy2(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": W,
        "height": H,
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t0 = time.time()
    master_sheet_info, dice_records = render_all_12_dice3d_assets()
    chibi_records = render_all_24_ffta_chibi_units()
    mirror_info = mirror_assets_to_web_and_unity()
    showcase_info = build_2400x1600_showcase_sheet()

    dice_hashes = {r["sha256"] for r in dice_records}
    chibi_static_hashes = {r["static_sprite"]["sha256"] for r in chibi_records}
    chibi_sheet_hashes = {r["animated_sheet_2f"]["sha256"] for r in chibi_records}

    manifest = {
        "schema_version": "1.0.0",
        "generator": "Backend/render_3d_dice_and_ffta_pixel_chibi_assets.py",
        "zero_living_artist_names": True,
        "elapsed_s": round(time.time() - t0, 2),
        "rtx4080_master_crystal_dice_sheet": master_sheet_info,
        "dice3d_summary": {
            "total_dice3d_sprites": len(dice_records),
            "unique_sha256_count": len(dice_hashes),
            "d6_faces_count": 6,
            "special_polyhedral_dice_count": 4,
            "animated_tumble_strips_count": 2,
            "all_cryptographically_unique": len(dice_hashes) == len(dice_records),
        },
        "ffta_chibi_summary": {
            "total_chibi_units": len(chibi_records),
            "unique_static_sha256_count": len(chibi_static_hashes),
            "unique_sheet_sha256_count": len(chibi_sheet_hashes),
            "native_resolution": [64, 64],
            "upscale_factor": 2,
            "palette_colors": 24,
            "rtx4080_sdxl_chibi_backed": True,
            "upscaled_static_resolution": [128, 128],
            "upscaled_sheet_2f_resolution": [256, 128],
            "all_24_cryptographically_unique": len(chibi_static_hashes) == 24 and len(chibi_sheet_hashes) == 24,
        },
        "mirror_sync": mirror_info,
        "showcase_sheet": showcase_info,
        "dice3d_assets": dice_records,
        "ffta_chibi_units": chibi_records,
    }

    MANIFEST_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"[OK] Track A 3D Polyhedral Dice & FFTA Pixel-Chibi Pipeline Complete in {manifest['elapsed_s']}s:\n"
        f"     RTX 4080 Crystal Sheet:     {master_sheet_info['filename']} ({master_sheet_info['bytes']} bytes, {master_sheet_info['elapsed_s']}s)\n"
        f"     3D Polyhedral Dice Assets:  {len(dice_records)}/12 (unique SHA-256: {len(dice_hashes)}/12)\n"
        f"     FFTA Pixel-Chibi Units:     {len(chibi_records)}/24 static + 24 2-frame sheets (unique SHA-256: {len(chibi_static_hashes)}/24 & {len(chibi_sheet_hashes)}/24)\n"
        f"     Showcase (2400x1600):       {SHOWCASE_LOCAL_PATH}\n"
        f"     Manifest:                   {MANIFEST_OUT_PATH}"
    )

    if len(dice_hashes) != 12 or len(chibi_static_hashes) != 24 or len(chibi_sheet_hashes) != 24:
        raise RuntimeError("SHA-256 uniqueness check failed for Dice3D or FFTA Chibi units!")


if __name__ == "__main__":
    main()
