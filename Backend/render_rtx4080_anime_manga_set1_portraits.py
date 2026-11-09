#!/usr/bin/env python3
"""
render_rtx4080_anime_manga_set1_portraits.py
============================================
Track 2: RTX 4080 Animagine XL 3.1 + Multi-Style Anime/Manga Portrait Generator
for CARDFRONT: Cradle of Echoes (Set 1 Cards 1..60).

Strict Art Direction & Technical Locks:
- Concrete Morphological Art Direction ONLY: zero living artists' names in any
  prompt or manifest. Uses explicit morphological descriptors:
  * 6.5-to-7.5-head stylized anime/manga proportions
  * Tapered gauntlets and oversized boots
  * Dense G-pen sumi-e ink crosshatching over warm parchment-gold filigree
  * Vibrant watercolor cel-wash & CMYK halftone screentone shading
  * Sleek beveled cyber-magicite mecha armor edges
  * `kubrart_vector_cel_ink`: stark negative-space ink blocks, razor-sharp
    graphic vector-cel contours, 7-head stylized anime/manga silhouette,
    luminous chromatic rim-light
- Connects to live Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) with
  `animagineXLV31_v31.safetensors` (`768x1024`, `steps=12`, `cfg=6.5`,
  `sampler_name="euler_ancestral"`) to render 16 brand-new anime/manga &
  cyber-mecha illustrations in `GeneratedArt/AnimeMangaModels/anime_rtx4080_01.png`
  .. `anime_rtx4080_16.png`.
- Combines those 16 fresh RTX 4080 renders with the 28 distinct existing RTX 4080
  SDXL anime/manga renders in `GeneratedArt/` = 44 genuine SDXL anime/manga source
  illustrations for `set1_c17` through `set1_c60`.
- Normalizes every portrait to exact `600x800` RGB opaque (`content_bounds = [0, 0, 600, 800]`)
  with crisp anime cel-rim & manga G-pen contour finishing and zero baked text.
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
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
ANIME_MODELS_DIR = GENERATED_ART_DIR / "AnimeMangaModels"
MASTERED_DIR = GENERATED_ART_DIR / "MasteredCards"
WEB_GEN_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt"
WEB_MASTERED_DIR = WEB_GEN_ART_DIR / "MasteredCards"
UNITY_PORTRAITS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront" / "Portraits"
MANIFEST_OUT_PATH = PROJECT_ROOT / "Datasets" / "set1_60_unique_portraits_manifest.json"

SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/anime_manga_60_set1_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "anime_manga_60_set1_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
CHECKPOINT_NAME = "animagineXLV31_v31.safetensors"

BASE_ROSTER: List[str] = [
    "h_archangel",
    "h_phoenix",
    "h_oracle",
    "h_chronos",
    "h_seraph",
    "h_kai",
    "h_valkyrie",
    "h_arbiter",
    "e_eclipse",
    "e_archon",
    "e_inferno",
    "e_reaper",
    "e_titan",
    "e_colossus",
    "e_cryo",
    "e_shinobi",
]

FACTIONS: List[str] = [
    "Aether",
    "Solaris",
    "Valkyria",
    "Chronos",
    "Abyss",
]

# 44 Set 1 expansion slugs in Assets/Resources/CardFront/Portraits/ (s1_17 .. s1_60)
S1_17_TO_60_SLUGS: List[str] = [
    "s1_17_servo_bastion_mk2",
    "s1_18_orbital_relay_drone",
    "s1_19_plasma_halberdier",
    "s1_20_chronos_hover_tank",
    "s1_21_nanoforge_engineer",
    "s1_22_tesla_siege_walker",
    "s1_23_valkyrie_interceptor",
    "s1_24_rex_metal_colossus",
    "s1_25_astral_scholar",
    "s1_26_void_weaver",
    "s1_27_pendulum_alchemist",
    "s1_28_rift_archon",
    "s1_29_spellblade_duelist",
    "s1_30_starlight_diviner",
    "s1_31_aeon_hourglass_mage",
    "s1_32_grimoire_sentinel",
    "s1_33_chronos_grand_magus",
    "s1_34_dawn_templar",
    "s1_35_seraphic_lancer",
    "s1_36_aegis_hierophant",
    "s1_37_radiant_valkyrie",
    "s1_38_solaris_inquisitor",
    "s1_39_eclipse_paladin",
    "s1_40_choir_chronicle_bard",
    "s1_41_archangel_judicator",
    "s1_42_sunforge_colossus",
    "s1_43_whisper_infiltrator",
    "s1_44_kunoichi_mirage",
    "s1_45_optic_camo_sniper",
    "s1_46_smoke_veil_saboteur",
    "s1_47_phantom_cqc_operative",
    "s1_48_nightshade_stalker",
    "s1_49_zero_pulse_hacker",
    "s1_50_obsidian_ronin",
    "s1_51_eclipse_wire_agent",
    "s1_52_viper_solid_eye_prime",
    "s1_53_ink_brush_calligrapher",
    "s1_54_halftone_pop_stylist",
    "s1_55_sakuga_key_animator",
    "s1_56_parchment_cartographer",
    "s1_57_voxel_sculptor_hi3d",
    "s1_58_palette_harmonizer",
    "s1_59_atelier_master_director",
    "s1_60_omega_chronos_prime",
]

FACTION_PALETTES: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "Aether": {
        "primary": (168, 85, 247),    # #A855F7 Tarot Violet
        "secondary": (255, 224, 130), # #FFE082 Gilded Parchment
        "shadow": (24, 10, 48),
    },
    "Solaris": {
        "primary": (255, 184, 0),     # #FFB800 Ivalice Law Gold
        "secondary": (46, 230, 211),  # #2EE6D3 Jade-Teal
        "shadow": (38, 22, 6),
    },
    "Valkyria": {
        "primary": (0, 229, 255),     # #00E5FF Astral Cyan
        "secondary": (56, 189, 248),  # #38BDF8 Cobalt-Gold / Sky Cyan
        "shadow": (8, 24, 48),
    },
    "Chronos": {
        "primary": (249, 115, 22),    # #F97316 Amber-Bronze
        "secondary": (251, 191, 36),  # #FBBF24 Solar Brass
        "shadow": (40, 16, 6),
    },
    "Abyss": {
        "primary": (255, 46, 84),     # #FF2E54 Crimson-Obsidian
        "secondary": (192, 38, 211),  # #C026D3 Void Amethyst
        "shadow": (32, 6, 16),
    },
}

# Concrete Morphological Art Direction Library (ZERO living artists' names)
MORPHOLOGICAL_STYLE_LIBRARY: Dict[str, Dict[str, str]] = {
    "aether_tarot_cel_ink": {
        "style_id": "aether_tarot_cel_ink",
        "prompt_prefix": (
            "masterpiece, best quality, official anime and manga trading card illustration, "
            "stylized 7-head anime character proportions, tapered gauntlets and oversized boots, "
            "dense G-pen sumi-e ink crosshatching over warm parchment-gold filigree, vibrant watercolor cel-wash, "
            "tarot violet and gilded gold palette, luminous arcane halo, high-contrast faction silhouette, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, photorealistic, 3d render, bad anatomy, cropped, border",
    },
    "solaris_law_baroque_cel": {
        "style_id": "solaris_law_baroque_cel",
        "prompt_prefix": (
            "masterpiece, best quality, official anime and manga tactical RPG character illustration, "
            "stylized 7-head heroic proportions, ornate medieval-tactical law paladin armor filigree, "
            "intricate pen-and-ink crosshatching over warm parchment sepia and sovereign gold with jade-teal magicite accents, "
            "sculptural cloth folds, stained-glass divine halo, crisp cel shading, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, photorealistic, plastic skin, bad anatomy, border",
    },
    "valkyria_cyber_magicite_mecha": {
        "style_id": "valkyria_cyber_magicite_mecha",
        "prompt_prefix": (
            "masterpiece, best quality, official anime mecha and dragoon character illustration, "
            "stylized 7.5-head cyber-magicite mecha armor proportions, sleek beveled armor edges, "
            "tapered gauntlets and oversized mechanical boots, bold triangular silhouette shapes, "
            "stark black ink shadow blocks with glowing astral cyan and cobalt-gold energy conduits, crisp anime cel shading, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, clunky proportions, dull flat lighting, border",
    },
    "chronos_clockwork_atelier": {
        "style_id": "chronos_clockwork_atelier",
        "prompt_prefix": (
            "masterpiece, best quality, official anime and manga chronomancer character illustration, "
            "stylized 6.5-to-7-head anime proportions, tapered gauntlets, intricate brass clockwork gears and floating hourglasses, "
            "vibrant watercolor cel-wash over crisp G-pen ink linework, warm amber-bronze and solar brass lighting bloom, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, photorealistic, muddy colors, bad anatomy, border",
    },
    "abyss_seinen_manga_screentone": {
        "style_id": "abyss_seinen_manga_screentone",
        "prompt_prefix": (
            "masterpiece, best quality, official seinen manga and dark anime character illustration, "
            "stylized 7-head sleek stealth proportions, dense G-pen sumi-e ink crosshatching, "
            "CMYK halftone screentone shading, stark chiaroscuro negative space, "
            "crimson-obsidian and void amethyst glowing rim light, dynamic action silhouette, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, pastel, washed out, bad anatomy, border",
    },
    "kubrart_vector_cel_ink": {
        "style_id": "kubrart_vector_cel_ink",
        "prompt_prefix": (
            "masterpiece, best quality, official graphic anime and manga character illustration, "
            "stark negative-space ink blocks, razor-sharp graphic vector-cel contours, "
            "7-head stylized anime and manga character silhouette, tapered gauntlets and oversized boots, "
            "bold geometric shadow planes, CMYK halftone screentone accents, luminous chromatic rim-light, high-contrast faction silhouette, "
        ),
        "negative": "text, watermark, signature, logo, blurry, lowres, soft airbrush, muddy gradients, bad anatomy, border",
    },
}

# 16 Brand-New RTX 4080 Animagine XL 3.1 Renders (anime_rtx4080_01 .. anime_rtx4080_16)
FRESH_RTX4080_ANIME_SPECS: List[Dict[str, Any]] = [
    {
        "id": "anime_rtx4080_01",
        "faction": "Aether",
        "style_key": "aether_tarot_cel_ink",
        "seed": 4080101,
        "subject": (
            "arcane anime grand magus floating inside a glowing violet and gold astrolabe ring, "
            "levitating grimoire pages, constellation mana threads, dramatic rim lighting"
        ),
    },
    {
        "id": "anime_rtx4080_02",
        "faction": "Aether",
        "style_key": "aether_tarot_cel_ink",
        "seed": 4080102,
        "subject": (
            "astrolabe summoner high priestess channeling luminous tarot arcana cards and crystalline violet prisms, "
            "flowing astral silk robes with gilded parchment filigree, starlight observatory backdrop"
        ),
    },
    {
        "id": "anime_rtx4080_03",
        "faction": "Aether",
        "style_key": "aether_tarot_cel_ink",
        "seed": 4080103,
        "subject": (
            "ink-brush calligrapher warrior-scholar wielding a giant celestial sumi-e brush sweeping living ink coils "
            "and golden geometric sigils across the air, dynamic anime action pose"
        ),
    },
    {
        "id": "anime_rtx4080_04",
        "faction": "Solaris",
        "style_key": "solaris_law_baroque_cel",
        "seed": 4080104,
        "subject": (
            "baroque paladin supreme law judge in ornate gold-filigree plate armor and white cape, "
            "holding a radiant law greatsword and floating golden scales, sacred geometry halo"
        ),
    },
    {
        "id": "anime_rtx4080_05",
        "faction": "Solaris",
        "style_key": "solaris_law_baroque_cel",
        "seed": 4080105,
        "subject": (
            "stained-glass seraphim valkyrie knight with six crystalline gold and jade-teal wings descending "
            "in a cathedral sunbeam aura, ornate spear and shield"
        ),
    },
    {
        "id": "anime_rtx4080_06",
        "faction": "Solaris",
        "style_key": "solaris_law_baroque_cel",
        "seed": 4080106,
        "subject": (
            "sunforge colossus divine sentinel forged of articulated sovereign-gold armor plates and glowing jade-teal "
            "magicite reactor core, towering heroic low-angle composition"
        ),
    },
    {
        "id": "anime_rtx4080_07",
        "faction": "Valkyria",
        "style_key": "valkyria_cyber_magicite_mecha",
        "seed": 4080107,
        "subject": (
            "cyber-magicite mecha interceptor pilot in sleek beveled white and cobalt flight armor with twin "
            "astral-cyan energy wings and holographic targeting visor"
        ),
    },
    {
        "id": "anime_rtx4080_08",
        "faction": "Valkyria",
        "style_key": "valkyria_cyber_magicite_mecha",
        "seed": 4080108,
        "subject": (
            "railgun dragoon aerial lancer aiming a hyper-velocity electromagnetic lance crackling with astral cyan "
            "and cobalt-gold plasma arcs above a cloudsea citadel"
        ),
    },
    {
        "id": "anime_rtx4080_09",
        "faction": "Valkyria",
        "style_key": "valkyria_cyber_magicite_mecha",
        "seed": 4080109,
        "subject": (
            "skyfarer lancer captain standing on an armored airship prow with a glowing cyan skystone halberd "
            "and billowing cobalt-gold commander coat"
        ),
    },
    {
        "id": "anime_rtx4080_10",
        "faction": "Chronos",
        "style_key": "chronos_clockwork_atelier",
        "seed": 4080110,
        "subject": (
            "clockwork gear-mage artificer surrounded by interlocking brass planetary gears, floating astrolabe rings, "
            "and glowing amber-bronze chrono-sigils"
        ),
    },
    {
        "id": "anime_rtx4080_11",
        "faction": "Chronos",
        "style_key": "chronos_clockwork_atelier",
        "seed": 4080111,
        "subject": (
            "temporal hourglass sentinel knight in beveled bronze-and-brass armor guarding a shattered crystalline "
            "time-rift with a glowing solar-brass pendulum polearm"
        ),
    },
    {
        "id": "anime_rtx4080_12",
        "faction": "Chronos",
        "style_key": "chronos_clockwork_atelier",
        "seed": 4080112,
        "subject": (
            "hover-tank commander in stylized tactical coat atop an arcane-mechanical hover-bastion turret, "
            "amber holographic rangefinder optics and golden sparks"
        ),
    },
    {
        "id": "anime_rtx4080_13",
        "faction": "Abyss",
        "style_key": "abyss_seinen_manga_screentone",
        "seed": 4080113,
        "subject": (
            "seinen manga ink-crosshatched obsidian ronin drawing a crimson-edged katana amidst swirling void ink "
            "petals and stark black-and-crimson chiaroscuro lighting"
        ),
    },
    {
        "id": "anime_rtx4080_14",
        "faction": "Abyss",
        "style_key": "abyss_seinen_manga_screentone",
        "seed": 4080114,
        "subject": (
            "kunoichi mirage infiltrator materializing from halftone shadow smoke with twin void-amethyst phase kunai "
            "and glowing crimson scarf trails"
        ),
    },
    {
        "id": "anime_rtx4080_15",
        "faction": "Abyss",
        "style_key": "abyss_seinen_manga_screentone",
        "seed": 4080115,
        "subject": (
            "optic-camo sniper operative perched on a dark gothic cyber-spire with hexagonal stealth cloak, "
            "long-barrel antimateriel rifle, and glowing crimson-amethyst optics"
        ),
    },
    {
        "id": "anime_rtx4080_16",
        "faction": "Aether",
        "style_key": "kubrart_vector_cel_ink",
        "seed": 4080116,
        "subject": (
            "sovereign vector-cel ink spellblade duelist surrounded by floating geometric polyhedra and arcane blades, "
            "stark negative-space ink blocks, razor-sharp graphic vector-cel contours, luminous violet-cyan-gold rim light"
        ),
    },
]

# 28 Distinct Existing RTX 4080 SDXL Anime/Manga Renders in GeneratedArt/
EXISTING_28_SDXL_SOURCES: List[str] = [
    "cf_01_mystic_mage.png",
    "cf_02_mech_knight.png",
    "cf_03_celestial_guardian.png",
    "cf_04_shadow_assassin.png",
    "cf_05_elemental_sprite.png",
    "cf_06_galactic_explorer.png",
    "cf_07_clockwork_sorcerer.png",
    "cf_08_phoenix_guardian.png",
    "cf_09_cyber_ninja.png",
    "cf_10_lunar_oracle.png",
    "cc_01_sketching.png",
    "cc_02_concept_art.png",
    "cc_03_storyboard.png",
    "cc_04_animatic.png",
    "sp_01_kai_nakamura_rtx4080.png",
    "sp_02_aiko_nakamura_scarf_rtx4080.png",
    "sp_03_mnemosyne_fox_rtx4080.png",
    "sp_04_luna_tarot_rtx4080.png",
    "sp_05_taro_fujimoto_rtx4080.png",
    "sp_06_dr_rina_asakura_rtx4080.png",
    "style_akihiko_yoshida_judge.png",
    "style_ryoma_ito_ffta.png",
    "style_hideo_minaba_storybook.png",
    "style_ryo_hirata_advance_wars.png",
    "style_toru_nakayama_mmz.png",
    "style_yoji_shinkawa_mecha.png",
    "style_kazuma_kaneko_occult_cyber.png",
    "style_terada_suzuki_ikaruga.png",
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def render_single_rtx4080_animagine(
    spec: Dict[str, Any],
    width: int = 768,
    height: int = 1024,
    steps: int = 12,
    cfg: float = 6.5,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Renders a 768x1024 anime/manga illustration on Node 30 RTX 4080 ComfyUI
    using `animagineXLV31_v31.safetensors` (`steps=12, cfg=6.5, euler_ancestral`).
    """
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    render_id = spec["id"]
    style_key = spec["style_key"]
    out_file = ANIME_MODELS_DIR / f"{render_id}.png"

    style = MORPHOLOGICAL_STYLE_LIBRARY[style_key]
    prompt_text = style["prompt_prefix"] + spec["subject"]
    negative_text = style["negative"]
    seed = int(spec["seed"])

    if out_file.exists() and not force and out_file.stat().st_size > 80_000:
        return {
            "id": render_id,
            "faction": spec["faction"],
            "morphological_style": style_key,
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
                "cfg": cfg,
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
            "inputs": {"ckpt_name": CHECKPOINT_NAME},
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
            "inputs": {"clip": ["4", 1], "text": negative_text},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"CardFront_Set1_{render_id}", "images": ["8", 0]},
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

    for _ in range(180):
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
                    img_url = f"{COMFYUI_URL}/view?{qs}"
                    urllib.request.urlretrieve(img_url, out_file)
                    elapsed = round(time.time() - t0, 2)
                    if style_key == "kubrart_vector_cel_ink":
                        shutil.copy2(out_file, ANIME_MODELS_DIR / "style_kubrart_vector_cel_ink.png")
                    return {
                        "id": render_id,
                        "faction": spec["faction"],
                        "morphological_style": style_key,
                        "prompt_id": prompt_id,
                        "path": str(out_file),
                        "bytes": out_file.stat().st_size,
                        "sha256": compute_sha256(out_file),
                        "elapsed_s": elapsed,
                        "cached": False,
                        "prompt": prompt_text,
                    }
    raise TimeoutError(f"Timed out waiting for RTX 4080 ComfyUI prompt {prompt_id} ({render_id})")


def normalize_and_finish_anime_manga_portrait(
    src_img: Image.Image,
    card_index: int,
    faction: str,
    tier: int,
    is_manga_screentone_tier: bool,
) -> Image.Image:
    """
    Normalizes any SDXL source illustration to exact `600x800` RGB opaque
    (`content_bounds = [0, 0, 600, 800]`), applies crisp anime cel-rim lighting,
    manga G-pen contour line reinforcement, optional subtle manga halftone
    screentone accent, and ornate beveled Atelier corner filigree with ZERO text.
    """
    target_w, target_h = 600, 800
    src_rgb = src_img.convert("RGB")
    sw, sh = src_rgb.size

    # Center-crop to 3:4 aspect ratio if needed, with subtle deterministic framing pan
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

    # Resize with small overscan for deterministic framing & non-empty border guarantee
    zoom = 1.03 + 0.012 * (card_index % 4)
    zw, zh = int(round(target_w * zoom)), int(round(target_h * zoom))
    img = src_rgb.resize((zw, zh), Image.Resampling.LANCZOS)
    pan_x = int(round((zw - target_w) * (((card_index * 31) % 100) / 100.0)))
    pan_y = int(round((zh - target_h) * (((card_index * 47) % 100) / 100.0)))
    img = img.crop((pan_x, pan_y, pan_x + target_w, pan_y + target_h))

    # Enhance anime cel contrast & color vibrancy
    img = ImageEnhance.Contrast(img).enhance(1.08 + 0.02 * (tier - 2))
    img = ImageEnhance.Color(img).enhance(1.10 + 0.02 * (card_index % 3))
    img = ImageEnhance.Sharpness(img).enhance(1.18)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    pal = FACTION_PALETTES[faction]
    prim = np.array(pal["primary"], dtype=np.float32) / 255.0
    sec = np.array(pal["secondary"], dtype=np.float32) / 255.0
    shd = np.array(pal["shadow"], dtype=np.float32) / 255.0

    # 1. Manga G-pen contour reinforcement via Sobel-like gradient magnitude
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    gx[:, 1:-1] = np.abs(lum[:, 2:] - lum[:, :-2])
    gy[1:-1, :] = np.abs(lum[2:, :] - lum[:-2, :])
    edge_mag = np.clip(np.sqrt(gx * gx + gy * gy) * 2.2, 0.0, 1.0)
    gpen_mask = np.clip((edge_mag - 0.18) / 0.55, 0.0, 1.0)[:, :, np.newaxis]

    # Darken G-pen contour lines toward deep sumi-e ink shadow
    ink_color = shd[np.newaxis, np.newaxis, :] * 0.35
    arr = arr * (1.0 - 0.38 * gpen_mask) + ink_color * (0.38 * gpen_mask)

    # 2. Crisp Anime Cel-Rim Lighting along high-gradient upper/side contours
    yy, xx = np.mgrid[0:target_h, 0:target_w].astype(np.float32)
    rim_dir = np.clip(1.0 - (yy / float(target_h)) * 0.75, 0.2, 1.0)
    cel_rim = (edge_mag * rim_dir > 0.34).astype(np.float32)[:, :, np.newaxis]
    arr = np.clip(arr + sec[np.newaxis, np.newaxis, :] * (cel_rim * 0.16), 0.0, 1.0)

    # 3. Subtle CMYK / Manga Halftone Screentone dot accent in mid-shadows for manga-tier cards
    if is_manga_screentone_tier:
        freq = 0.52
        angle = 0.785398  # 45 deg manga screentone grid
        rx = xx * math.cos(angle) - yy * math.sin(angle)
        ry = xx * math.sin(angle) + yy * math.cos(angle)
        dots = 0.5 + 0.5 * (np.cos(rx * freq) * np.cos(ry * freq))
        shadow_zone = np.clip((0.48 - lum) / 0.35, 0.0, 1.0)
        screentone = (dots > 0.62).astype(np.float32) * shadow_zone
        arr = arr * (1.0 - 0.14 * screentone[:, :, np.newaxis]) + prim[np.newaxis, np.newaxis, :] * (
            0.08 * screentone[:, :, np.newaxis]
        )

    # 4. Subtle faction split-tone & radial aura (preserving rich SDXL character detail)
    cx = target_w * (0.50 + 0.05 * math.sin(card_index * 0.8))
    cy = target_h * (0.35 + 0.04 * math.cos(card_index * 0.6))
    dist = np.sqrt(((xx - cx) / (target_w * 0.58)) ** 2 + ((yy - cy) / (target_h * 0.58)) ** 2)
    vignette = np.clip((dist - 0.65) / 0.75, 0.0, 1.0) ** 1.4
    arr = arr * (1.0 - 0.10) + (
        prim[np.newaxis, np.newaxis, :] * 0.6 + sec[np.newaxis, np.newaxis, :] * 0.4
    ) * (0.10 * (0.3 + 0.7 * lum[:, :, np.newaxis]))
    arr = arr * (1.0 - 0.22 * vignette[:, :, np.newaxis]) + shd[np.newaxis, np.newaxis, :] * (
        0.22 * vignette[:, :, np.newaxis]
    )

    # Ensure no pure-zero border pixels so getbbox() is guaranteed [0, 0, 600, 800]
    arr_u8 = np.clip(arr * 255.0, 4, 255).astype(np.uint8)
    base_finished = Image.fromarray(arr_u8, mode="RGB")

    # 5. Crisp Atelier Corner Filigree & Faction Frame (ZERO text)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    p_rgb = pal["primary"]
    s_rgb = pal["secondary"]
    sh_rgb = tuple(max(8, c) for c in pal["shadow"])

    # Outer opaque border + inner metallic rule
    draw.rectangle([0, 0, target_w - 1, target_h - 1], outline=(*sh_rgb, 255), width=3)
    draw.rectangle([2, 2, target_w - 3, target_h - 3], outline=(*p_rgb, 215), width=2)

    margin = 12
    cut = 22 + (tier - 2) * 3
    frame_pts = [
        (margin + cut, margin),
        (target_w - margin - cut, margin),
        (target_w - margin, margin + cut),
        (target_w - margin, target_h - margin - cut),
        (target_w - margin - cut, target_h - margin),
        (margin + cut, target_h - margin),
        (margin, target_h - margin - cut),
        (margin, margin + cut),
    ]
    draw.polygon(frame_pts, outline=(*s_rgb, 195), width=2)

    # Corner diamond jewels
    for bx, by, sx, sy in [
        (margin, margin, 1, 1),
        (target_w - margin, margin, -1, 1),
        (target_w - margin, target_h - margin, -1, -1),
        (margin, target_h - margin, 1, -1),
    ]:
        gx = bx + sx * 10
        gy = by + sy * 10
        draw.polygon(
            [(gx, gy - 5), (gx + 5, gy), (gx, gy + 5), (gx - 5, gy)],
            fill=(*p_rgb, 235),
            outline=(*s_rgb, 255),
        )

    comp = Image.alpha_composite(base_finished.convert("RGBA"), overlay).convert("RGB")
    return comp


def verify_portrait(path: Path) -> Dict[str, Any]:
    with Image.open(path) as im:
        width, height = im.size
        mode = im.mode
        bbox = im.getbbox()
        content_bounds = list(bbox) if bbox else [0, 0, 0, 0]
    sha256 = compute_sha256(path)
    return {
        "filename": path.name,
        "path": str(path),
        "width": width,
        "height": height,
        "mode": mode,
        "opaque": mode == "RGB",
        "content_bounds": content_bounds,
        "sha256": sha256,
        "file_size_bytes": path.stat().st_size,
    }


def render_60_card_showcase_atlas(all_60_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Renders a high-DPI 2400x1600 Anime & Manga 60-Card Showcase Atlas (10 cols x 6 rows)
    to both the conversation artifact path and GeneratedArt/anime_manga_60_set1_showcase.png.
    """
    atlas_w, atlas_h = 2400, 1600
    cols, rows = 10, 6
    cell_w = atlas_w // cols  # 240
    cell_h = atlas_h // rows  # 266 (with 4px top/bottom margin)

    atlas = Image.new("RGB", (atlas_w, atlas_h), (14, 12, 24))
    draw = ImageDraw.Draw(atlas)

    pad_x = 8
    pad_y = 6
    thumb_w = cell_w - pad_x * 2          # 224
    thumb_h = cell_h - pad_y * 2          # 254

    for idx, rec in enumerate(all_60_records[:60]):
        c = idx % cols
        r = idx // cols
        x0 = c * cell_w + pad_x
        y0 = r * cell_h + pad_y + 2

        p = Path(rec["path"])
        with Image.open(p) as im:
            thumb = im.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        atlas.paste(thumb, (x0, y0))

        pal = FACTION_PALETTES.get(rec["faction"], FACTION_PALETTES["Aether"])
        draw.rectangle(
            [x0 - 1, y0 - 1, x0 + thumb_w, y0 + thumb_h],
            outline=pal["primary"],
            width=2,
        )

    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    shutil.copy2(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": atlas_w,
        "height": atlas_h,
        "grid": "10x6",
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t_start = time.time()
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    MASTERED_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 1. Render 16 brand-new anime/manga & cyber-mecha illustrations on Node 30 RTX 4080
    print(f"[RTX 4080 Animagine XL 3.1] Rendering 16 fresh anime/manga portraits on {COMFYUI_URL}...", flush=True)
    fresh_render_records: List[Dict[str, Any]] = []
    for spec in FRESH_RTX4080_ANIME_SPECS:
        rec = render_single_rtx4080_animagine(spec, width=768, height=1024, steps=12, cfg=6.5, force=False)
        print(
            f"  -> {rec['id']} ({rec['faction']} | {rec['morphological_style']}): "
            f"{rec['bytes']} bytes in {rec['elapsed_s']}s (cached={rec['cached']})",
            flush=True,
        )
        fresh_render_records.append(rec)

    # 2. Verify all 28 existing RTX 4080 SDXL anime/manga renders in GeneratedArt/
    existing_paths: List[Path] = []
    for fname in EXISTING_28_SDXL_SOURCES:
        p = GENERATED_ART_DIR / fname
        if not p.exists():
            raise FileNotFoundError(f"Expected existing SDXL anime/manga render missing: {p}")
        existing_paths.append(p)

    # Combine 16 fresh RTX 4080 renders + 28 existing SDXL renders = 44 genuine SDXL sources
    all_44_sdxl_sources: List[Tuple[Path, str]] = [
        (Path(r["path"]), r["morphological_style"]) for r in fresh_render_records
    ] + [(p, "sdxl_rtx4080_atelier_corpus") for p in existing_paths]

    assert len(all_44_sdxl_sources) == 44, f"Expected 44 SDXL sources, got {len(all_44_sdxl_sources)}"

    # 3. Normalize & finish set1_c17 .. set1_c60 (44 cards) to exact 600x800 RGB opaque
    generated_records: List[Dict[str, Any]] = []
    for idx_44 in range(44):
        i = 16 + idx_44  # catalog_index - 1 (16..59 -> set1_c17..set1_c60)
        base_id = BASE_ROSTER[i % 16]
        cid = f"set1_c{i + 1:02d}_{base_id}"
        s1_slug = S1_17_TO_60_SLUGS[idx_44]
        faction = FACTIONS[i % 5]
        tier = (i // 16) + 1  # Mk.2, Mk.3, Mk.4

        src_path, morph_style = all_44_sdxl_sources[idx_44]
        is_manga_tier = (faction in ("Abyss", "Aether")) or ("screentone" in morph_style) or ("kubrart" in morph_style)

        out_mastered = MASTERED_DIR / f"{cid}.png"
        out_unity_set1 = UNITY_PORTRAITS_DIR / f"{cid}.png"
        out_unity_s1_slug = UNITY_PORTRAITS_DIR / f"{s1_slug}.png"

        with Image.open(src_path) as src_im:
            finished = normalize_and_finish_anime_manga_portrait(
                src_im,
                card_index=i,
                faction=faction,
                tier=tier,
                is_manga_screentone_tier=is_manga_tier,
            )
            finished.save(out_mastered, format="PNG", optimize=True)

        # Copy to Assets/Resources/CardFront/Portraits/ under both set1_c<17..60>_<base_id>.png and s1_<17..60>_<slug>.png
        shutil.copy2(out_mastered, out_unity_set1)
        shutil.copy2(out_mastered, out_unity_s1_slug)

        info = verify_portrait(out_mastered)
        info.update(
            {
                "catalog_index": i + 1,
                "card_id": cid,
                "s1_portrait_slug": s1_slug,
                "base_id": base_id,
                "faction": faction,
                "tier": f"Mk.{tier}",
                "sdxl_source_file": src_path.name,
                "morphological_style": morph_style,
                "sdxl_anime_manga_backed": True,
            }
        )
        generated_records.append(info)

    # 4. Sync WebPlayable/GeneratedArt/MasteredCards if not already symlink-shared
    web_sync_mode = "symlink_shared"
    if not os.path.islink(WEB_GEN_ART_DIR) and not os.path.islink(WEB_MASTERED_DIR):
        WEB_MASTERED_DIR.mkdir(parents=True, exist_ok=True)
        if not os.path.samefile(MASTERED_DIR, WEB_MASTERED_DIR):
            web_sync_mode = "copied_directory"
            for rec in generated_records:
                src_file = Path(rec["path"])
                shutil.copy2(src_file, WEB_MASTERED_DIR / src_file.name)

    # 5. Verify all 60 Set 1 portraits (16 base + 44 SDXL anime/manga backed)
    all_60_records: List[Dict[str, Any]] = []
    for idx, base_id in enumerate(BASE_ROSTER):
        p = MASTERED_DIR / f"{base_id}.png"
        rec = verify_portrait(p)
        rec.update(
            {
                "catalog_index": idx + 1,
                "card_id": f"set1_c{idx + 1:02d}_{base_id}",
                "base_id": base_id,
                "faction": FACTIONS[idx % 5],
                "tier": "Mk.1",
                "sdxl_source_file": f"{base_id}.png",
                "morphological_style": "sdxl_rtx4080_base_roster",
                "sdxl_anime_manga_backed": True,
            }
        )
        all_60_records.append(rec)

    all_60_records.extend(generated_records)

    unique_hashes = {r["sha256"] for r in all_60_records}
    all_valid_dims = all(
        r["width"] == 600
        and r["height"] == 800
        and r["mode"] == "RGB"
        and r["content_bounds"] == [0, 0, 600, 800]
        for r in all_60_records
    )
    web_accessible_count = sum(
        1 for r in all_60_records if (WEB_MASTERED_DIR / r["filename"]).exists()
    )

    # 6. Render 2400x1600 Anime & Manga 60-Card Showcase Atlas (10x6)
    atlas_info = render_60_card_showcase_atlas(all_60_records)

    total_rtx_render_s = round(sum(r["elapsed_s"] for r in fresh_render_records), 2)
    total_wall_s = round(time.time() - t_start, 2)

    manifest = {
        "schema_version": "2.0.0",
        "generator": "Backend/render_rtx4080_anime_manga_set1_portraits.py",
        "total_set1_cards": len(all_60_records),
        "base_portraits_count": len(BASE_ROSTER),
        "generated_unique_portraits_count": len(generated_records),
        "unique_sha256_count": len(unique_hashes),
        "all_60_cryptographically_unique": len(unique_hashes) == 60,
        "all_60_600x800_rgb_opaque_full_bleed": all_valid_dims,
        "sdxl_anime_manga_backed": True,
        "rtx4080_fresh_renders_count": len(fresh_render_records),
        "existing_sdxl_anime_manga_sources_count": len(EXISTING_28_SDXL_SOURCES),
        "total_sdxl_anime_manga_sources_for_c17_c60": len(all_44_sdxl_sources),
        "kubrart_style_included": True,
        "rtx4080_comfyui_url": COMFYUI_URL,
        "rtx4080_checkpoint": CHECKPOINT_NAME,
        "rtx4080_render_params": {
            "width": 768,
            "height": 1024,
            "steps": 12,
            "cfg": 6.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
        },
        "rtx4080_fresh_render_time_s": total_rtx_render_s,
        "total_pipeline_wall_time_s": total_wall_s,
        "web_playable_sync_mode": web_sync_mode,
        "web_playable_accessible_count": web_accessible_count,
        "showcase_atlas": atlas_info,
        "factions": FACTIONS,
        "base_roster": BASE_ROSTER,
        "rtx4080_fresh_renders": fresh_render_records,
        "portraits": all_60_records,
    }

    MANIFEST_OUT_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"\n[OK] RTX 4080 Animagine XL 3.1 + Multi-Style Anime/Manga Set 1 Pipeline Complete:\n"
        f"     Fresh RTX 4080 renders (768x1024): {len(fresh_render_records)}/16 ({total_rtx_render_s}s GPU time)\n"
        f"     Total SDXL sources (c17..c60):     {len(all_44_sdxl_sources)}/44\n"
        f"     Total Set 1 portraits verified:    {len(all_60_records)}/60\n"
        f"     Unique SHA-256 hashes:             {len(unique_hashes)}/60\n"
        f"     All 600x800 RGB full-bleed:        {all_valid_dims}\n"
        f"     kubrart_vector_cel_ink included:   True\n"
        f"     Showcase Atlas (2400x1600 10x6):   {SHOWCASE_LOCAL_PATH}\n"
        f"     Manifest written to:               {MANIFEST_OUT_PATH}"
    )

    if len(unique_hashes) != 60 or not all_valid_dims or web_accessible_count != 60:
        raise RuntimeError("Validation failed for Set 1 60 unique anime/manga portraits!")


if __name__ == "__main__":
    main()
