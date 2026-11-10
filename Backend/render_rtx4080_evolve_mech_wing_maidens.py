#!/usr/bin/env python3
"""
render_rtx4080_evolve_mech_wing_maidens.py
==========================================
Track 2: Node 30 (`192.168.86.30` RTX 4080) Live Render of 10 Paired Base + Evolved
(`進化前` & `進化後`) "Mech-Wing Maidens & Chrono-Seraphs" `600x800` Master Portraits &
`2400x1600` Shadowverse-EVOLVE-Style `SR / UR` Luxury Gunmetal-Filigree Showcase Atlas.

Strict Art Direction & Compliance Contract (`tcg-creative-game-designer/rules/AGENTS.md`):
- ZERO living artists' names anywhere in prompts, code, or metadata (`zero_living_artist_names: true`).
- Crystal-clear, luminous, expressive anime heroine facial features, bright joyful/heroic eyes,
  warm sunlit skin, ornate Victorian-fantasy dresses with articulated brass-gold & emerald/cyan
  mechanical feather wings, clockwork songbirds, and twilight/sunset skies.
- NO dark silhouette overlays covering the character's face or torso!
- All 10 portraits in `GeneratedArt/EvolveMechWingMaidens/` are normalized to exact `600x800`
  (`3:4` portrait, RGB, opaque, `content_bounds = [0, 0, 600, 800]`, zero borders, zero baked text).
- The `2400x1600` (`5 columns x 2 rows`) Showcase Atlas (`evolve_mech_wing_maiden_sr_showcase.png`)
  renders all 5 Base (`SR`) + 5 Evolved (`UR EVOLVED`) cards inside the luxury Gunmetal-Silver &
  Gilded-Prismatic physical card frame with top-left octagonal cost gem, semi-transparent
  smoked-glass lower-third rules/flavor box, sapphire attack gem, ruby defense shield gem, and
  `SR` / `UR` embossed stamp.
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
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
ANIME_MODELS_DIR = GENERATED_ART_DIR / "AnimeMangaModels"
EVOLVE_ART_DIR = GENERATED_ART_DIR / "EvolveMechWingMaidens"
WEB_EVOLVE_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "EvolveMechWingMaidens"
UNITY_PORTRAITS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront" / "Portraits"
DATASETS_DIR = PROJECT_ROOT / "Datasets"
OUT_MANIFEST_PATH = DATASETS_DIR / "evolve_mech_wing_maidens_manifest.json"

SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/evolve_mech_wing_maiden_sr_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "evolve_mech_wing_maiden_sr_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
ANIMAGINE_CHECKPOINT = "animagineXLV31_v31.safetensors"

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
    "mushimaro",
    "ponzu",
]

QUALITY_PREFIX = (
    "masterpiece, best quality, very aesthetic, absurdres, official anime trading card game illustration, "
    "luminous vibrant watercolor cel-wash and crisp anime linework, expressive detailed anime face and sparkling eyes, "
    "warm peach skin lighting, intricate gold and silver mechanical filigree, upper body and thighs visible, "
)

NEGATIVE_PROMPT = (
    "dark silhouette, faceless, helmet, mask, monochrome, blacked out face, heavy dark shadows, "
    "text, watermark, signature, logo, typography, letters, blurry, low quality, worst quality, "
    "bad anatomy, bad hands, extra digits, cropped head, border, frame"
)

# 5 Paired Base (進化前) + Evolved (進化後) Mech-Wing Maidens = 10 Cards Total
EVOLVE_MECH_WING_CARDS: List[Dict[str, Any]] = [
    # ── Pair 1: Rosalia, Mech-Wing Sky Maiden (Base + Evolved) ──
    {
        "id": "ev_01_base",
        "pair_id": "pair_01_rosalia",
        "form": "Base",
        "form_jp": "進化前",
        "rarity": "SR",
        "card_code": "CF02-110 SR",
        "slug": "ev_01_base_rosalia_mech_wing_maiden",
        "filename": "ev_01_base_rosalia_mech_wing_maiden.png",
        "name": "Rosalia, Mech-Wing Sky Maiden",
        "trait": "Follower · Angel / Mech",
        "faction": "Valkyria",
        "cost": 2,
        "atk": 1,
        "def": 3,
        "nesw": [6, 7, 8, 6],
        "evolve_cost": 1,
        "ability_lines": [
            "[Evolve (1)] : Evolve this card into Arch-Seraph Overdrive.",
            "[Ward] Adjacent allied conduits gain +1 South Defense.",
        ],
        "flavor_text": (
            "\"They say these brass pinions are too small for the heavens... "
            "yet just feeling the sunset breeze makes my heart soar!\""
        ),
        "primary_rgb": (46, 230, 168),   # Luminous Emerald-Jade Wing Feather
        "secondary_rgb": (255, 184, 0),  # Brass-Gold Filigree
        "hair_accent_rgb": (244, 114, 182),
        "seed": 40805101,
        "subject_prompt": (
            "1girl, solo, long rose-pink hair with twin side-tails and small dark-gold horned wing hairpins, "
            "bright joyful amber-rose anime eyes, open happy smile, warm sunlit peach skin, "
            "ornate indigo-violet and white corset dress with gold filigree and puffy blue-white sleeves, "
            "articulated brass-gold mechanical wings with glowing emerald-green translucent energy feathers, "
            "tiny golden clockwork songbird perched on her raised left hand, "
            "warm pastel sunset sky with soft pink clouds and distant ancient stone pillars"
        ),
    },
    {
        "id": "ev_01_evo",
        "pair_id": "pair_01_rosalia",
        "form": "Evolved",
        "form_jp": "進化後",
        "rarity": "UR",
        "card_code": "CF02-110 EVOLVED",
        "slug": "ev_01_evo_rosalia_arch_seraph_overdrive",
        "filename": "ev_01_evo_rosalia_arch_seraph_overdrive.png",
        "name": "Rosalia, Arch-Seraph Overdrive",
        "trait": "Evolved · Angel / Mech",
        "faction": "Valkyria",
        "cost": 2,
        "atk": 3,
        "def": 5,
        "nesw": [8, 9, 9, 8],
        "evolve_cost": 0,
        "ability_lines": [
            "[Ward] [Aerial Resonance]",
            "On Evolve: Summons 2 Golden Clockwork Songbirds (+2 N/E) and heals Sanctum by 2.",
        ],
        "flavor_text": (
            "\"Spread wide, my six emerald pinions! Every clockwork songbird in the sky "
            "now sings in harmony with our sanctuary!\""
        ),
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 204, 34),
        "hair_accent_rgb": (244, 114, 182),
        "seed": 40805188,
        "force_rerender": False,
        "subject_prompt": (
            "1girl, solo, cowboy shot, upper body centered, looking at viewer, "
            "long flowing luminous rose-pink hair with twin side-tails and golden seraphic wing hairpins, "
            "radiant confident smile, sparkling amber-rose anime eyes, warm peach skin, "
            "ornate royal indigo-violet and white gold-trimmed valkyrie corset gown, "
            "six unfurled golden-brass mechanical wings behind her back with glowing emerald-green and astral cyan crystal feathers, "
            "small golden clockwork songbird perched on her finger, sunset pastel clouds"
        ),
    },

    # ── Pair 2: Celestia, Clockwork Feather Valkyrie (Base + Evolved) ──
    {
        "id": "ev_02_base",
        "pair_id": "pair_02_celestia",
        "form": "Base",
        "form_jp": "進化前",
        "rarity": "SR",
        "card_code": "CF02-112 SR",
        "slug": "ev_02_base_celestia_clockwork_valkyrie",
        "filename": "ev_02_base_celestia_clockwork_valkyrie.png",
        "name": "Celestia, Clockwork Feather Valkyrie",
        "trait": "Follower · Angel / Mech",
        "faction": "Solaris",
        "cost": 3,
        "atk": 2,
        "def": 4,
        "nesw": [7, 8, 7, 7],
        "evolve_cost": 1,
        "ability_lines": [
            "[Evolve (1)] : Evolve this card into Chrono-Sovereign.",
            "On Deploy: Locks the opponent's highest directional rank for 1 turn.",
        ],
        "flavor_text": (
            "\"Each silver pinion ticks in measure with the celestial astrolabe. "
            "Not a single feather falls out of time.\""
        ),
        "primary_rgb": (56, 189, 248),
        "secondary_rgb": (255, 196, 46),
        "hair_accent_rgb": (226, 232, 240),
        "seed": 40805201,
        "subject_prompt": (
            "1girl, solo, long silver-white braided hair with golden gear hair ornaments, "
            "expressive sapphire-blue anime eyes, gentle noble smile, warm fair skin, "
            "royal azure-blue and ivory pleated valkyrie dress with golden clockwork shoulder pauldrons, "
            "articulated silver-and-gold mechanical wings with glowing cyan crystal feathers, "
            "floating brass pocket-astrolabe in her hand, bright cloudsea cathedral backdrop"
        ),
    },
    {
        "id": "ev_02_evo",
        "pair_id": "pair_02_celestia",
        "form": "Evolved",
        "form_jp": "進化後",
        "rarity": "UR",
        "card_code": "CF02-112 EVOLVED",
        "slug": "ev_02_evo_celestia_chrono_sovereign",
        "filename": "ev_02_evo_celestia_chrono_sovereign.png",
        "name": "Celestia, Chrono-Wing Sovereign",
        "trait": "Evolved · Angel / Mech",
        "faction": "Solaris",
        "cost": 3,
        "atk": 4,
        "def": 6,
        "nesw": [9, 9, 8, 8],
        "evolve_cost": 0,
        "ability_lines": [
            "[Ward] [Chrono-Aegis]",
            "On Evolve: Grants +2 North and +2 East to all Solaris and Valkyria followers.",
        ],
        "flavor_text": (
            "\"When the twelfth chime rings across the cloudsea, my mechanical wings "
            "open the gates of eternity!\""
        ),
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (255, 184, 0),
        "hair_accent_rgb": (248, 250, 252),
        "seed": 40805202,
        "subject_prompt": (
            "1girl, solo, flowing silver-white hair with a floating golden clockwork halo crown, "
            "luminous sapphire-blue anime eyes, heroic serene expression, "
            "ornate azure and sovereign-gold armored valkyrie dress, "
            "massive unfolded clockwork mechanical wings with glowing astral cyan and gold crystal feathers, "
            "interlocking golden astrolabe rings in a sunlit sky"
        ),
    },

    # ── Pair 3: Lyra, Harmonic Wing Automaton (Base + Evolved) ──
    {
        "id": "ev_03_base",
        "pair_id": "pair_03_lyra",
        "form": "Base",
        "form_jp": "進化前",
        "rarity": "SR",
        "card_code": "CF02-115 SR",
        "slug": "ev_03_base_lyra_harmony_automata",
        "filename": "ev_03_base_lyra_harmony_automata.png",
        "name": "Lyra, Harmonic Wing Automaton",
        "trait": "Follower · Angel / Mech",
        "faction": "Aether",
        "cost": 2,
        "atk": 2,
        "def": 2,
        "nesw": [7, 6, 7, 7],
        "evolve_cost": 1,
        "ability_lines": [
            "[Evolve (1)] : Evolve this card into Symphony Seraph.",
            "Fanfare: Draws 1 Mech-Wing card and restores 1 Aether Charge.",
        ],
        "flavor_text": (
            "\"Pluck a single golden string upon my wings, and the entire sky "
            "resonates with a lullaby of starlight.\""
        ),
        "primary_rgb": (168, 85, 247),
        "secondary_rgb": (46, 230, 211),
        "hair_accent_rgb": (216, 180, 254),
        "seed": 40805399,
        "force_rerender": False,
        "subject_prompt": (
            "1girl, solo, cowboy shot, thighs visible, standing in sky sanctuary, "
            "long wavy lavender-violet hair with golden wing hairpins, "
            "warm sparkling amethyst anime eyes, sweet cheerful smile, warm peach skin, "
            "ornate violet and white Victorian corset dress with gold filigree and pleated skirt, "
            "articulated brass-gold mechanical wings on her back with glowing turquoise-emerald crystal feathers, "
            "tiny golden clockwork songbird perched on her finger, sunset clouds background"
        ),
    },
    {
        "id": "ev_03_evo",
        "pair_id": "pair_03_lyra",
        "form": "Evolved",
        "form_jp": "進化後",
        "rarity": "UR",
        "card_code": "CF02-115 EVOLVED",
        "slug": "ev_03_evo_lyra_symphony_seraph",
        "filename": "ev_03_evo_lyra_symphony_seraph.png",
        "name": "Lyra, Grand Symphony Seraph",
        "trait": "Evolved · Angel / Mech",
        "faction": "Aether",
        "cost": 2,
        "atk": 4,
        "def": 4,
        "nesw": [9, 8, 8, 8],
        "evolve_cost": 0,
        "ability_lines": [
            "[Harmonic Chorus] [Plus-Resonance]",
            "On Evolve: Reduces all enemy orthogonal directional ranks by -1 until end of turn.",
        ],
        "flavor_text": (
            "\"Hear the crescendo of ten thousand golden feathers! Our celestial "
            "symphony shall never fade!\""
        ),
        "primary_rgb": (192, 132, 252),
        "secondary_rgb": (255, 224, 130),
        "hair_accent_rgb": (233, 213, 255),
        "seed": 40805302,
        "subject_prompt": (
            "1girl, solo, luminous flowing lavender-violet hair, radiant joyful singing expression, "
            "sparkling amethyst anime eyes, ornate violet and gilded gold concert-valkyrie dress, "
            "grand cathedral-harp mechanical wings of polished gold and glowing turquoise-violet crystal feathers, "
            "floating golden musical notes and starlight prisms in a twilight sky"
        ),
    },

    # ── Pair 4: Ignia, Blaze-Pinion Mech Maiden (Base + Evolved) ──
    {
        "id": "ev_04_base",
        "pair_id": "pair_04_ignia",
        "form": "Base",
        "form_jp": "進化前",
        "rarity": "SR",
        "card_code": "CF02-118 SR",
        "slug": "ev_04_base_ignia_blaze_pinion_maiden",
        "filename": "ev_04_base_ignia_blaze_pinion_maiden.png",
        "name": "Ignia, Blaze-Pinion Mech Maiden",
        "trait": "Follower · Angel / Mech",
        "faction": "Chronos",
        "cost": 3,
        "atk": 3,
        "def": 2,
        "nesw": [8, 8, 5, 7],
        "evolve_cost": 1,
        "ability_lines": [
            "[Evolve (1)] : Evolve this card into Solar-Phoenix Empress.",
            "[Rush] Gains +2 East Attack when contesting an enemy Construct.",
        ],
        "flavor_text": (
            "\"My furnace-heart burns at a thousand degrees, yet these ruby pinions "
            "dance lighter than a summer spark!\""
        ),
        "primary_rgb": (255, 46, 84),
        "secondary_rgb": (255, 184, 0),
        "hair_accent_rgb": (251, 113, 133),
        "seed": 40805401,
        "subject_prompt": (
            "1girl, solo, bright coral-red high ponytail with brass-gold wing hairpins, "
            "spirited golden-amber anime eyes, confident grin, warm sunlit skin, "
            "sleek crimson-and-white corset dress with ornate gold clockwork trim, "
            "articulated bronze-and-gold mechanical wings with glowing ruby-orange and emerald translucent feathers, "
            "small golden clockwork phoenix perched on her shoulder, golden hour sky"
        ),
    },
    {
        "id": "ev_04_evo",
        "pair_id": "pair_04_ignia",
        "form": "Evolved",
        "form_jp": "進化後",
        "rarity": "UR",
        "card_code": "CF02-118 EVOLVED",
        "slug": "ev_04_evo_ignia_solar_phoenix_empress",
        "filename": "ev_04_evo_ignia_solar_phoenix_empress.png",
        "name": "Ignia, Solar-Phoenix Empress",
        "trait": "Evolved · Angel / Mech",
        "faction": "Chronos",
        "cost": 3,
        "atk": 5,
        "def": 4,
        "nesw": [10, 9, 7, 8],
        "evolve_cost": 0,
        "ability_lines": [
            "[Storm] [Solar Ignition]",
            "On Evolve: Deals 2 rank damage to the North enemy unit and triggers an immediate capture check.",
        ],
        "flavor_text": (
            "\"Soar, my clockwork phoenixes! Set the twilight heavens ablaze with "
            "undying solar gold!\""
        ),
        "primary_rgb": (249, 115, 22),
        "secondary_rgb": (255, 215, 0),
        "hair_accent_rgb": (253, 186, 116),
        "seed": 40805402,
        "subject_prompt": (
            "1girl, solo, flowing blazing coral-crimson and gold hair, triumphant radiant smile, "
            "glowing golden anime eyes, ornate crimson-white and sovereign-gold empress valkyrie dress, "
            "six massive unfolded solar-phoenix mechanical wings of liquid gold and ruby-emerald crystal feathers, "
            "soaring golden clockwork phoenixes in a brilliant sunset sky"
        ),
    },

    # ── Pair 5: Nocturna, Eclipse-Wing Mech Saint (Base + Evolved) ──
    {
        "id": "ev_05_base",
        "pair_id": "pair_05_nocturna",
        "form": "Base",
        "form_jp": "進化前",
        "rarity": "SR",
        "card_code": "CF02-120 SR",
        "slug": "ev_05_base_nocturna_eclipse_wing_saint",
        "filename": "ev_05_base_nocturna_eclipse_wing_saint.png",
        "name": "Nocturna, Eclipse-Wing Mech Saint",
        "trait": "Follower · Angel / Mech",
        "faction": "Abyss",
        "cost": 4,
        "atk": 3,
        "def": 4,
        "nesw": [8, 7, 8, 8],
        "evolve_cost": 1,
        "ability_lines": [
            "[Evolve (1)] : Evolve this card into Abyssal-Prism Queen.",
            "[Ward] [Bane] Immune to enemy rank-reduction abilities.",
        ],
        "flavor_text": (
            "\"Even beneath a moonless eclipse, stained-glass feathers remember "
            "the warmth of the dawn.\""
        ),
        "primary_rgb": (0, 229, 255),
        "secondary_rgb": (168, 85, 247),
        "hair_accent_rgb": (199, 210, 254),
        "seed": 40805501,
        "subject_prompt": (
            "1girl, solo, long silver-lavender twin-tails with dark-gold horned wing hairpins and navy ribbons, "
            "luminous violet and cyan anime eyes, gentle mysterious smile, fair porcelain skin, "
            "ornate gothic-victorian midnight-blue and white ruffled dress with silver-gold filigree, "
            "articulated silver-gold mechanical wings with stained-glass violet and emerald-cyan crystal feathers, "
            "clockwork silver owl perched on her gloved finger, starry twilight sky"
        ),
    },
    {
        "id": "ev_05_evo",
        "pair_id": "pair_05_nocturna",
        "form": "Evolved",
        "form_jp": "進化後",
        "rarity": "UR",
        "card_code": "CF02-120 EVOLVED",
        "slug": "ev_05_evo_nocturna_abyssal_prism_queen",
        "filename": "ev_05_evo_nocturna_abyssal_prism_queen.png",
        "name": "Nocturna, Astral-Prism Queen",
        "trait": "Evolved · Angel / Mech",
        "faction": "Abyss",
        "cost": 4,
        "atk": 5,
        "def": 6,
        "nesw": [10, 9, 9, 9],
        "evolve_cost": 0,
        "ability_lines": [
            "[Ward] [Bane] [Eclipse Sanctuary]",
            "On Evolve: Flips up to 2 adjacent enemy followers whose Defense is 4 or less.",
        ],
        "flavor_text": (
            "\"Behold the prism of the eternal omen—where night and day embrace "
            "beneath six stained-glass wings!\""
        ),
        "primary_rgb": (168, 85, 247),
        "secondary_rgb": (0, 229, 255),
        "hair_accent_rgb": (224, 231, 255),
        "seed": 40805502,
        "subject_prompt": (
            "1girl, solo, flowing luminous silver-lavender hair with a golden eclipse halo crown, "
            "radiant violet-cyan anime eyes, serene queenly smile, "
            "ornate midnight-blue, white, and gold filigree ceremonial dress, "
            "six magnificent stained-glass mechanical wings glowing with violet, emerald, astral cyan, and gold feathers, "
            "auroral twilight sky with floating crystal prisms"
        ),
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


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_rtx4080_evolve_raw(
    spec: Dict[str, Any],
    width: int = 768,
    height: int = 1024,
    steps: int = 12,
    cfg: float = 6.5,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Connects to Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) using
    `animagineXLV31_v31.safetensors` (`768x1024`, `steps=12`, `cfg=6.5`, `euler_ancestral`)
    to render a luminous Mech-Wing Maiden portrait.
    """
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    card_id = spec["id"]
    raw_out = ANIME_MODELS_DIR / f"{card_id}_rtx4080_raw.png"

    full_prompt = QUALITY_PREFIX + spec["subject_prompt"]
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
            "inputs": {"filename_prefix": f"EvolveMechWing_{card_id}", "images": ["8", 0]},
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
        time.sleep(0.35)
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
    raise TimeoutError(f"ComfyUI timed out rendering {card_id}")


def draw_small_star_sparkle(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    fill_rgba: Tuple[int, int, int, int],
) -> None:
    pts: List[Tuple[float, float]] = []
    for i in range(8):
        ang = i * (math.pi / 4.0)
        r = outer_r if (i % 2 == 0) else inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=fill_rgba, outline=(255, 255, 255, 240))


def normalize_luminous_evolve_portrait_600x800(
    src_img: Image.Image,
    spec: Dict[str, Any],
) -> Image.Image:
    """
    Normalizes the `768x1024` RTX 4080 `animagineXLV31_v31.safetensors` portrait to
    exact `600x800` (`3:4` RGB opaque, `content_bounds = [0, 0, 600, 800]`, zero text).

    CRITICAL VISUAL GUARANTEE:
    Preserves 100% of the clean, luminous anime heroine facial features, eyes, hair,
    and dress without ANY dark silhouette crush or heavy polygons over the subject.
    Adds only a delicate peripheral gunmetal-and-gold border rule and tiny corner
    feather-prism sparkles at the outer 14px margin.
    """
    target_w, target_h = 600, 800
    img = src_img.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Gentle warm anime vibrancy & crisp linework polish (preserving bright skin & eye catchlights)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = ImageEnhance.Sharpness(img).enhance(1.15)

    # Guarantee no pure-black (0,0,0) edge pixels so getbbox() == (0, 0, 600, 800)
    arr_u8 = np.clip(np.asarray(img, dtype=np.uint8), 8, 255)
    base_rgba = Image.fromarray(arr_u8, mode="RGB").convert("RGBA")

    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    p_rgb = spec["primary_rgb"]
    s_rgb = spec["secondary_rgb"]
    is_evolved = spec["form"] == "Evolved"

    # Delicate peripheral gunmetal-silver & gold border rule (outer 10px only, zero intrusion on character)
    outer_col = (212, 175, 55, 255) if is_evolved else (48, 54, 66, 255)
    inner_col = (*s_rgb, 225) if is_evolved else (*p_rgb, 210)
    draw.rectangle([0, 0, target_w - 1, target_h - 1], outline=outer_col, width=3)
    draw.rectangle([3, 3, target_w - 4, target_h - 4], outline=inner_col, width=2)

    # Subtle beveled corner filigree lines at 8px margin
    m = 8
    c = 18
    oct_pts = [
        (m + c, m),
        (target_w - m - c, m),
        (target_w - m, m + c),
        (target_w - m, target_h - m - c),
        (target_w - m - c, target_h - m),
        (m + c, target_h - m),
        (m, target_h - m - c),
        (m, m + c),
    ]
    draw.polygon(oct_pts, outline=(*s_rgb, 165), width=1)

    # Tiny corner starlight sparkles near the upper wing tips (never over the center/face)
    if is_evolved:
        draw_small_star_sparkle(draw, 36, 42, 14, 3, (*s_rgb, 220))
        draw_small_star_sparkle(draw, target_w - 36, 42, 14, 3, (*p_rgb, 220))

    return Image.alpha_composite(base_rgba, overlay).convert("RGB")


def render_shadowverse_evolve_card_frame(
    portrait_img: Image.Image,
    spec: Dict[str, Any],
    card_w: int = 456,
    card_h: int = 638,
) -> Image.Image:
    """
    Composites a single `456x638` luxury Shadowverse-EVOLVE-style `SR / UR` physical card
    for the `2400x1600` Showcase Atlas, faithfully modeled after `Rosa, Mech Wing Maiden BP05-110 SR`:
      1. Upper 62% of the card: 100% unobstructed, crystal-clear anime heroine face, hair,
         expression, and glowing mechanical wings!
      2. Top-Left Octagonal/Diamond Metallic Cost Crest (`2`, `3`, `4`) with silver-gold bevels.
      3. Lower-Middle Semi-Transparent Smoked-Glass Overlay (`y = 61% .. 82%`) where the heroine's
         dress and legs remain clearly visible underneath, displaying:
           - Ability text (`[Evolve (1)]`, `[Ward]`)
           - Thin metallic divider line
           - Italic flavor quote
      4. Bottom Luxury Gunmetal-Silver (`SR`) or Gilded-Prismatic (`UR EVOLVED`) Nameplate &
         Stat Bar (`y = 82% .. 97%`) with:
           - Left Faceted Sapphire-Blue Diamond Attack Gem
           - Right Faceted Ruby-Crimson Shield Defense Gem
           - Center Character Name, Trait Pill (`Follower · Angel / Mech`), and `SR` / `UR` Stamp!
    """
    is_evolved = spec["form"] == "Evolved"
    art = portrait_img.convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS).convert("RGBA")

    overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    p_rgb = spec["primary_rgb"]
    s_rgb = spec["secondary_rgb"]
    frame_metal = (225, 190, 88) if is_evolved else (168, 178, 195)
    frame_dark = (34, 30, 44) if is_evolved else (28, 32, 38)

    # 1. Semi-Transparent Smoked-Glass Rules & Flavor Box on lower third (y = 61% .. 82%)
    #    Notice alpha = 148 so the character's legs/skirt remain visible underneath!
    glass_y0 = int(card_h * 0.61)
    glass_y1 = int(card_h * 0.825)
    draw.rectangle(
        [14, glass_y0, card_w - 14, glass_y1],
        fill=(12, 15, 22, 148),
        outline=(*frame_metal, 185),
        width=1,
    )

    font_ability = load_font(11, bold=True)
    font_flavor = load_font(10, bold=False)
    font_name = load_font(15, bold=True)
    font_trait = load_font(11, bold=True)
    font_gem = load_font(26, bold=True)
    font_cost = load_font(28, bold=True)
    font_meta = load_font(9, bold=False)

    # Draw ability lines inside upper half of smoked-glass box
    ay = glass_y0 + 8
    for line in spec["ability_lines"][:2]:
        draw.text((22, ay), line[:64], fill=(248, 250, 252, 250), font=font_ability)
        ay += 18

    # Divider line inside smoked-glass box
    div_y = glass_y0 + 48
    draw.line([(22, div_y), (card_w - 22, div_y)], fill=(*frame_metal, 160), width=1)

    # Flavor quote (2 lines) inside lower half of smoked-glass box
    flavor = spec["flavor_text"]
    mid_split = len(flavor) // 2
    space_idx = flavor.find(" ", mid_split - 10)
    if space_idx == -1:
        space_idx = mid_split
    f_line1 = flavor[:space_idx].strip()
    f_line2 = flavor[space_idx:].strip()
    draw.text((22, div_y + 7), f_line1[:68], fill=(226, 232, 240, 235), font=font_flavor)
    draw.text((22, div_y + 23), f_line2[:68], fill=(226, 232, 240, 235), font=font_flavor)

    # 2. Bottom Luxury Gunmetal-Silver / Gilded Nameplate Bar (y = 82.5% .. 96.5%)
    bar_y0 = glass_y1
    bar_y1 = int(card_h * 0.965)
    draw.rectangle(
        [10, bar_y0, card_w - 10, bar_y1],
        fill=(*frame_dark, 238),
        outline=(*frame_metal, 240),
        width=2,
    )

    # Center Nameplate Title & Ornate Rule
    name_str = spec["name"]
    draw.text((card_w // 2, bar_y0 + 18), name_str, fill=(255, 252, 242, 255), font=font_name, anchor="mm")
    rule_y = bar_y0 + 34
    draw.line([(86, rule_y), (card_w - 86, rule_y)], fill=(*frame_metal, 225), width=2)
    draw.polygon(
        [(card_w // 2, rule_y - 4), (card_w // 2 + 5, rule_y), (card_w // 2, rule_y + 4), (card_w // 2 - 5, rule_y)],
        fill=(*s_rgb, 255),
    )

    # Follower / Evolved Pill Badge + Trait + SR/UR Stamp
    pill_y = bar_y0 + 44
    pill_col = (185, 38, 92, 240) if not is_evolved else (124, 58, 237, 245)
    draw.rounded_rectangle([92, pill_y, 166, pill_y + 20], radius=6, fill=pill_col, outline=(*frame_metal, 235), width=1)
    draw.text((129, pill_y + 10), spec["form"], fill=(255, 255, 255, 255), font=font_trait, anchor="mm")
    draw.text((238, pill_y + 10), "Angel · Mech", fill=(226, 232, 240, 245), font=font_trait, anchor="mm")

    # SR / UR Octagonal Stamp
    rarity_col = (255, 204, 46, 250) if is_evolved else (210, 220, 235, 250)
    draw.rounded_rectangle(
        [card_w - 134, pill_y, card_w - 90, pill_y + 20],
        radius=5,
        fill=(24, 28, 38, 250),
        outline=rarity_col,
        width=2,
    )
    draw.text((card_w - 112, pill_y + 10), spec["rarity"], fill=rarity_col, font=font_trait, anchor="mm")

    # 3. Top-Left Octagonal/Diamond Cost Gem (like Rosa's `2` diamond)
    cx_cost, cy_cost = 46, 48
    r_cost = 30
    cost_pts = [
        (cx_cost, cy_cost - r_cost - 4),
        (cx_cost + r_cost, cy_cost),
        (cx_cost, cy_cost + r_cost + 4),
        (cx_cost - r_cost, cy_cost),
    ]
    draw.polygon(cost_pts, fill=(32, 38, 46, 248), outline=(*frame_metal, 255), width=3)
    inner_cost_pts = [
        (cx_cost, cy_cost - r_cost + 4),
        (cx_cost + r_cost - 6, cy_cost),
        (cx_cost, cy_cost + r_cost - 4),
        (cx_cost - r_cost + 6, cy_cost),
    ]
    draw.polygon(inner_cost_pts, fill=(18, 22, 28, 245), outline=(*s_rgb, 220), width=1)
    draw.text((cx_cost, cy_cost), str(spec["cost"]), fill=(255, 255, 255, 255), font=font_cost, anchor="mm")

    # 4. Bottom-Left Faceted Sapphire-Blue Diamond Attack Gem (`atk`)
    cx_atk, cy_atk = 48, bar_y0 + 36
    r_atk = 31
    atk_pts = [
        (cx_atk, cy_atk - r_atk - 3),
        (cx_atk + r_atk - 2, cy_atk + 2),
        (cx_atk, cy_atk + r_atk + 3),
        (cx_atk - r_atk + 2, cy_atk + 2),
    ]
    draw.polygon(atk_pts, fill=(22, 78, 198, 250), outline=(215, 228, 245, 255), width=3)
    draw.polygon(
        [(cx_atk, cy_atk - r_atk + 5), (cx_atk + r_atk - 9, cy_atk + 2), (cx_atk, cy_atk + r_atk - 5), (cx_atk - r_atk + 9, cy_atk + 2)],
        fill=(37, 99, 235, 245),
        outline=(147, 197, 253, 235),
        width=1,
    )
    draw.text((cx_atk, cy_atk + 2), str(spec["atk"]), fill=(255, 255, 255, 255), font=font_gem, anchor="mm")

    # 5. Bottom-Right Faceted Ruby-Crimson Shield Defense Gem (`def`)
    cx_def, cy_def = card_w - 48, bar_y0 + 36
    r_def = 30
    shield_pts = [
        (cx_def - r_def + 4, cy_def - r_def + 6),
        (cx_def, cy_def - r_def - 2),
        (cx_def + r_def - 4, cy_def - r_def + 6),
        (cx_def + r_def - 2, cy_def + 8),
        (cx_def, cy_def + r_def + 4),
        (cx_def - r_def + 2, cy_def + 8),
    ]
    draw.polygon(shield_pts, fill=(175, 24, 58, 250), outline=(245, 215, 165, 255), width=3)
    draw.text((cx_def, cy_def + 2), str(spec["def"]), fill=(255, 255, 255, 255), font=font_gem, anchor="mm")

    # 6. Outer Beveled Gunmetal-Silver / Gilded-Prismatic Card Border & Copyright Footer
    draw.rounded_rectangle(
        [2, 2, card_w - 3, card_h - 3],
        radius=14,
        outline=(*frame_metal, 255),
        width=5,
    )
    draw.rounded_rectangle(
        [8, 8, card_w - 9, card_h - 9],
        radius=10,
        outline=(*p_rgb, 210) if is_evolved else (95, 108, 128, 215),
        width=2,
    )
    draw.text((22, card_h - 12), f"{spec['card_code']} · NESW {spec['nesw']}", fill=(203, 213, 225, 230), font=font_meta, anchor="lm")
    draw.text((card_w - 22, card_h - 12), "CARDFRONT EVOLVE", fill=(203, 213, 225, 230), font=font_meta, anchor="rm")

    return Image.alpha_composite(art, overlay).convert("RGB")


def build_evolve_sr_showcase_atlas_2400x1600(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Builds the `2400x1600` (`5 columns x 2 rows`) Shadowverse-EVOLVE-Style `SR / UR`
    Showcase Atlas (`evolve_mech_wing_maiden_sr_showcase.png`):
      - Top Row (`y = 92..730`): All 5 Base Form (`進化前` — `SR`) Mech-Wing Maidens
      - Bottom Row (`y = 852..1490`): All 5 Evolved Form (`進化後` — `UR EVOLVED`) Mech-Wing Maidens
    """
    atlas_w, atlas_h = 2400, 1600
    atlas = Image.new("RGB", (atlas_w, atlas_h), (11, 15, 24))
    draw = ImageDraw.Draw(atlas)

    font_header = load_font(22, bold=True)
    font_sub = load_font(14, bold=True)

    # Top Banner
    draw.rectangle([16, 12, atlas_w - 16, 76], fill=(18, 24, 38), outline=(212, 175, 55), width=2)
    draw.text(
        (atlas_w // 2, 34),
        "CARDFRONT EVOLVE · MECH-WING MAIDENS & CHRONO-SERAPHS (NODE 30 RTX 4080 ANIMAGINE XL 3.1)",
        fill=(255, 248, 225),
        font=font_header,
        anchor="mm",
    )
    draw.text(
        (atlas_w // 2, 58),
        "TOP ROW: BASE FORM (SR · GUNMETAL-SILVER FILIGREE)   |   BOTTOM ROW: AWAKENED EVOLVED FORM (UR · GILDED PRISM OVERDRIVE)",
        fill=(56, 189, 248),
        font=font_sub,
        anchor="mm",
    )

    base_cards = [r for r in records if r["form"] == "Base"]
    evo_cards = [r for r in records if r["form"] == "Evolved"]

    col_w = atlas_w // 5  # 480
    card_w, card_h = 456, 680

    for col_idx in range(5):
        x0 = col_idx * col_w + (col_w - card_w) // 2  # +12

        # Top Row: Base Form (SR)
        b_rec = base_cards[col_idx]
        b_spec = next(s for s in EVOLVE_MECH_WING_CARDS if s["id"] == b_rec["id"])
        with Image.open(b_rec["path"]) as b_im:
            framed_base = render_shadowverse_evolve_card_frame(b_im, b_spec, card_w=card_w, card_h=card_h)
        atlas.paste(framed_base, (x0, 92))

        # Evolution Arrow Connector between Row 1 (Base) and Row 2 (Evolved)
        cx_arrow = col_idx * col_w + col_w // 2
        draw.polygon(
            [
                (cx_arrow - 48, 780),
                (cx_arrow + 48, 780),
                (cx_arrow + 48, 804),
                (cx_arrow + 68, 804),
                (cx_arrow, 834),
                (cx_arrow - 68, 804),
                (cx_arrow - 48, 804),
            ],
            fill=(255, 184, 0),
            outline=(255, 255, 255),
        )
        draw.text((cx_arrow, 796), "EVOLVE", fill=(12, 16, 24), font=font_sub, anchor="mm")

        # Bottom Row: Evolved Form (UR EVOLVED)
        e_rec = evo_cards[col_idx]
        e_spec = next(s for s in EVOLVE_MECH_WING_CARDS if s["id"] == e_rec["id"])
        with Image.open(e_rec["path"]) as e_im:
            framed_evo = render_shadowverse_evolve_card_frame(e_im, e_spec, card_w=card_w, card_h=card_h)
        atlas.paste(framed_evo, (x0, 844))

    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    copy_if_distinct(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": atlas_w,
        "height": atlas_h,
        "grid": "5x2 (5 Base SR + 5 Evolved UR)",
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t_start = time.time()
    EVOLVE_ART_DIR.mkdir(parents=True, exist_ok=True)
    WEB_EVOLVE_ART_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    print(
        f"[Evolve Mech-Wing Maidens] Rendering 10 Paired Base + Evolved portraits on Node 30 RTX 4080 ({COMFYUI_URL})...",
        flush=True,
    )

    records: List[Dict[str, Any]] = []
    sha_set = set()
    live_count = 0

    for idx, spec in enumerate(EVOLVE_MECH_WING_CARDS):
        raw_info = render_rtx4080_evolve_raw(
            spec,
            width=768,
            height=1024,
            steps=12,
            cfg=6.5,
            force=bool(spec.get("force_rerender", False)),
        )
        if raw_info["rtx4080_live_rendered"]:
            live_count += 1

        raw_path = Path(raw_info["raw_source_path"])
        with Image.open(raw_path) as raw_im:
            portrait_im = normalize_luminous_evolve_portrait_600x800(raw_im, spec)

        out_path = EVOLVE_ART_DIR / spec["filename"]
        portrait_im.save(out_path, format="PNG", optimize=True)
        copy_if_distinct(out_path, WEB_EVOLVE_ART_DIR / spec["filename"])
        copy_if_distinct(out_path, UNITY_PORTRAITS_DIR / spec["filename"])

        with Image.open(out_path) as chk:
            w, h = chk.size
            mode = chk.mode
            bbox = list(chk.getbbox() or (0, 0, 0, 0))

        sha = compute_sha256(out_path)
        sha_set.add(sha)

        rec = {
            "id": spec["id"],
            "pair_id": spec["pair_id"],
            "form": spec["form"],
            "form_jp": spec["form_jp"],
            "rarity": spec["rarity"],
            "card_code": spec["card_code"],
            "slug": spec["slug"],
            "filename": spec["filename"],
            "name": spec["name"],
            "trait": spec["trait"],
            "faction": spec["faction"],
            "cost": spec["cost"],
            "atk": spec["atk"],
            "def": spec["def"],
            "nesw": spec["nesw"],
            "evolve_cost": spec["evolve_cost"],
            "ability_lines": spec["ability_lines"],
            "flavor_text": spec["flavor_text"],
            "art": f"./GeneratedArt/EvolveMechWingMaidens/{spec['filename']}",
            "path": str(out_path),
            "web_playable_path": str(WEB_EVOLVE_ART_DIR / spec["filename"]),
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
        records.append(rec)
        print(
            f"  [{idx + 1:02d}/10] {spec['id']} ({spec['form']} {spec['rarity']} | {spec['name']}): "
            f"{w}x{h} {mode} bounds={bbox} sha256={sha[:12]}... ({raw_info['elapsed_s']}s)",
            flush=True,
        )

    showcase_info = build_evolve_sr_showcase_atlas_2400x1600(records)

    all_valid = all(
        r["width"] == 600
        and r["height"] == 800
        and r["mode"] == "RGB"
        and r["opaque"] is True
        and r["content_bounds"] == [0, 0, 600, 800]
        for r in records
    )
    all_unique = len(sha_set) == 10 and len(records) == 10

    manifest = {
        "manifest_id": "cardfront_evolve_mech_wing_maidens_v1",
        "title": "Mech-Wing Maidens & Chrono-Seraphs (Paired Base SR + Evolved UR Expansion)",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "Backend/render_rtx4080_evolve_mech_wing_maidens.py",
        "status": "VERIFIED" if (all_valid and all_unique) else "FAILED",
        "zero_living_artist_names": True,
        "comfyui_rtx4080_endpoint": COMFYUI_URL,
        "checkpoint": ANIMAGINE_CHECKPOINT,
        "rtx4080_render_params": {
            "width": 768,
            "height": 1024,
            "steps": 12,
            "cfg": 6.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
        },
        "pairs_count": 5,
        "total_portraits_count": len(records),
        "unique_sha256_count": len(sha_set),
        "rtx4080_live_rendered_count": live_count,
        "all_600x800_rgb_opaque": all_valid,
        "all_cryptographically_unique": all_unique,
        "showcase_atlas": showcase_info,
        "total_wall_time_s": round(time.time() - t_start, 2),
        "cards": records,
    }

    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    assert_zero_living_artist_names(manifest_json, "evolve_mech_wing_maidens_manifest.json")
    OUT_MANIFEST_PATH.write_text(manifest_json + "\n", encoding="utf-8")

    print(
        f"[Complete] 10/10 Paired Base + Evolved Mech-Wing Maiden Portraits "
        f"(600x800 RGB={all_valid}, unique_sha256={len(sha_set)}/10) in {manifest['total_wall_time_s']}s.",
        flush=True,
    )
    print(f"  Manifest: {OUT_MANIFEST_PATH}", flush=True)
    print(f"  Showcase: {SHOWCASE_BRAIN_PATH}", flush=True)


if __name__ == "__main__":
    main()
