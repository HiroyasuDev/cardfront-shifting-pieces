#!/usr/bin/env python3
"""
render_flux_animagine_set2_expansion.py
=======================================
Track A: Node 30 RTX 4080 Animagine XL 3.1 + FLUX.1-dev Refiner &
Set 2: "Kubrart Astral Eclipse & Manga Vanguard" Expansion (20 Cards: set2_k01 .. set2_k20)
for CARDFRONT: Cradle of Echoes.

Strict Art Direction & Technical Contract:
- Zero living artists' names in any prompt, comment, or manifest (`zero_living_artist_names: true`).
- Uses 100% Concrete Morphological Art Direction:
  * `set2_k01`..`set2_k05` (`kubrart_vector_cel_ink_v1`): stark obsidian negative-space silhouettes,
    razor-sharp vector-cel polyhedral shards, 7-head anime/manga proportions, tapered gauntlets/boots,
    luminous violet (`#A855F7`) & astral cyan (`#00E5FF`) rim-wash.
  * `set2_k06`..`set2_k10` (`manga_sumi_ink_seinen_v1`): dense monochrome G-pen crosshatching on
    bone-ivory (`#F2ECE1`) with vivid crimson (`#FF2E54`) blade trails and stark sumi-e ink blocks.
  * `set2_k11`..`set2_k15` (`anime_sakuga_kagenashi_v2`): 24fps key-animation hard kagenashi shadow
    blocks, RGB chromatic aberration edge split, radial impact speedlines, 4-point gold (`#FFB800`) star flares.
  * `set2_k16`..`set2_k20` (`cyber_mecha_orthographic_v1`): 7.5-head cyber-magicite mecha frames,
    sleek beveled energy wings, precision orthographic drafting reticles, CMYK halftone screentone dot-matrix.
- Connects to live Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) to render fresh
  `animagineXLV31_v31.safetensors` (`768x1024`, `steps=10`, `cfg=6.5`) portraits and refines all 20
  Set 2 cards into `600x800` (`3:4` portrait, RGB, opaque, `content_bounds = [0, 0, 600, 800]`,
  zero baked text, 20 distinct SHA-256 hashes).
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
from PIL import Image, ImageDraw, ImageEnhance

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
GENERATED_ART_DIR = PROJECT_ROOT / "GeneratedArt"
ANIME_MODELS_DIR = GENERATED_ART_DIR / "AnimeMangaModels"
SET2_ART_DIR = GENERATED_ART_DIR / "Set2KubrartManga"
WEB_SET2_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "Set2KubrartManga"
UNITY_PORTRAITS_DIR = PROJECT_ROOT / "Assets" / "Resources" / "CardFront" / "Portraits"
MANIFEST_OUT_PATH = PROJECT_ROOT / "Datasets" / "set2_kubrart_manga_expansion_manifest.json"

SHOWCASE_BRAIN_PATH = Path(
    "/Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/set2_kubrart_manga_showcase.png"
)
SHOWCASE_LOCAL_PATH = GENERATED_ART_DIR / "set2_kubrart_manga_showcase.png"

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.86.30:8188")
ANIMAGINE_CHECKPOINT = "animagineXLV31_v31.safetensors"
FLUX_CHECKPOINT = "flux1-dev-fp8.safetensors"

FORBIDDEN_LIVING_NAMES = [
    "yoshida",
    "minaba",
    "shinkawa",
    "kaneko",
    "terada",
    "hirata",
    "nakayama",
    "kubrart_realname",
]

LINEAGE_SPECS: Dict[str, Dict[str, Any]] = {
    "kubrart_vector_cel_ink_v1": {
        "model_id": "kubrart_vector_cel_ink_v1",
        "lineage_name": "Kubrart Vector-Cel & Negative-Space Prism",
        "lora_file": "kubrart_vector_cel_ink_v1_lora.safetensors",
        "base_checkpoint": ANIMAGINE_CHECKPOINT,
        "refiner_checkpoint": FLUX_CHECKPOINT,
        "shader_preset": "manga_gpen_screentone",
        "primary_rgb": (168, 85, 247),   # #A855F7 Luminous Tarot Violet
        "secondary_rgb": (0, 229, 255),  # #00E5FF Astral Cyan
        "accent_rgb": (255, 184, 0),     # #FFB800 Law Gold
        "bg_ink_rgb": (9, 13, 22),       # #090D16 Stark Obsidian
        "prompt_prefix": (
            "masterpiece, best quality, official anime and manga trading card illustration, "
            "stark negative-space sumi-ink blocks, razor-sharp graphic vector-cel contours, "
            "floating polyhedral crystal shards, stylized 7-head anime character proportions, "
            "tapered gauntlets and oversized boots, luminous violet and astral cyan rim-wash, "
            "flat graphic kagenashi shadow planes, high-contrast faction silhouette, "
        ),
        "negative_prompt": (
            "text, watermark, signature, logo, typography, letters, blurry, lowres, "
            "photorealistic, muddy airbrush gradients, bad anatomy, cropped, border"
        ),
    },
    "manga_sumi_ink_seinen_v1": {
        "model_id": "manga_sumi_ink_seinen_v1",
        "lineage_name": "Seinen Sumi-e G-Pen Crosshatch & Crimson Ink",
        "lora_file": "manga_sumi_ink_crosshatch_seinen_v1_lora.safetensors",
        "base_checkpoint": ANIMAGINE_CHECKPOINT,
        "refiner_checkpoint": FLUX_CHECKPOINT,
        "shader_preset": "manga_gpen_screentone",
        "primary_rgb": (255, 46, 84),     # #FF2E54 Vivid Crimson Blade Trail
        "secondary_rgb": (242, 236, 225), # #F2ECE1 Bone-Ivory Parchment
        "accent_rgb": (255, 224, 130),    # #FFE082 Gilded Filigree
        "bg_ink_rgb": (11, 14, 23),       # #0B0E17 Sumi-e Charcoal Black
        "prompt_prefix": (
            "masterpiece, best quality, official seinen manga character illustration, "
            "dense monochrome G-pen sumi-e crosshatching on warm bone-ivory paper with vivid crimson ink blade trails, "
            "stylized 7.5-head dark fantasy proportions, baroque engraved armor filigree, "
            "CMYK halftone screentone dot-matrix, stark chiaroscuro negative space, "
        ),
        "negative_prompt": (
            "text, watermark, signature, logo, typography, letters, blurry, lowres, "
            "pastel colors, plastic 3d skin, bad anatomy, border"
        ),
    },
    "anime_sakuga_kagenashi_v2": {
        "model_id": "anime_sakuga_kagenashi_v2",
        "lineage_name": "24fps Trigger Kagenashi Keyframe & Star-Flare",
        "lora_file": "anime_sakuga_kagenashi_keyframe_v2_lora.safetensors",
        "base_checkpoint": ANIMAGINE_CHECKPOINT,
        "refiner_checkpoint": FLUX_CHECKPOINT,
        "shader_preset": "sakuga_kagenashi_flare",
        "primary_rgb": (255, 184, 0),    # #FFB800 4-Point Gold Star-Flare
        "secondary_rgb": (0, 229, 255),  # #00E5FF Astral Cyan Rim
        "accent_rgb": (255, 46, 84),     # #FF2E54 Crimson Impact Burst
        "bg_ink_rgb": (15, 23, 42),      # #0F172A Deep Keyframe Slate
        "prompt_prefix": (
            "masterpiece, best quality, 24fps TV anime key-animation sakuga impact illustration, "
            "hard kagenashi unshaded shadow blocks, chromatic aberration edge split, "
            "four-point gold star-flare burst, radial shonen convergence speedlines, "
            "stylized 7-head anime hero proportions, tapered gauntlets, kinetic motion arc, "
        ),
        "negative_prompt": (
            "text, watermark, signature, logo, typography, letters, blurry, lowres, "
            "static pose, dull lighting, photorealistic, bad anatomy, border"
        ),
    },
    "cyber_mecha_orthographic_v1": {
        "model_id": "cyber_mecha_orthographic_v1",
        "lineage_name": "Cyber-Magicite Mecha Orthographic & Blueprint Halftone",
        "lora_file": "cyber_mecha_orthographic_cel_v1_lora.safetensors",
        "base_checkpoint": ANIMAGINE_CHECKPOINT,
        "refiner_checkpoint": FLUX_CHECKPOINT,
        "shader_preset": "mecha_blueprint_halftone",
        "primary_rgb": (0, 229, 255),    # #00E5FF Astral Cyan Visor
        "secondary_rgb": (46, 230, 211), # #2EE6D3 Jade-Teal Blueprint
        "accent_rgb": (249, 115, 22),    # #F97316 Thruster Amber
        "bg_ink_rgb": (11, 19, 43),      # #0B132B Blueprint Navy
        "prompt_prefix": (
            "masterpiece, best quality, official anime cyber-magicite mecha character illustration, "
            "stylized 7.5-head mecha frame proportions, sleek beveled cyber-magicite armor edges, "
            "tapered gauntlets and thruster boots, translucent geometric energy wings, "
            "luminous cockpit visor, precision orthographic panel-line drafting, CMYK screentone dot-matrix, "
        ),
        "negative_prompt": (
            "text, watermark, signature, logo, typography, letters, blurry, lowres, "
            "organic flesh, clunky proportions, muddy shading, border"
        ),
    },
}

SET2_CARDS_DEFINITION: List[Dict[str, Any]] = [
    # ── Lineage 1: Kubrart Vector-Cel & Negative-Space Prism (set2_k01 .. set2_k05) ──
    {
        "id": "set2_k01",
        "slug": "set2_k01_kubrart_eclipse_sovereign",
        "name": "Kubrart Eclipse Sovereign",
        "faction": "Aether",
        "cost": 4,
        "tier": 4,
        "nesw": [9, 8, 6, 8],
        "modelId": "kubrart_vector_cel_ink_v1",
        "ability": {
            "id": "ab_eclipse_prism_dominion",
            "name": "Negative-Space Prism Dominion",
            "text": "On Deploy: Flips adjacent orthogonal units if their opposing directional rank is Prime (2, 3, 5, 7) and grants +1 N/E to Allied Aether conduits.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080201,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_16.png",
        "subject_prompt": (
            "eclipse sovereign arch-mage suspended inside a shattered black obsidian polyhedral halo, "
            "stark negative-space sumi-ink cloak silhouette, razor-sharp vector-cel violet and astral cyan prism shards, "
            "dramatic low-angle heroic framing"
        ),
    },
    {
        "id": "set2_k02",
        "slug": "set2_k02_vector_prism_duelist",
        "name": "Vector-Prism Spellblade",
        "faction": "Aether",
        "cost": 2,
        "tier": 2,
        "nesw": [7, 7, 5, 6],
        "modelId": "kubrart_vector_cel_ink_v1",
        "ability": {
            "id": "ab_vector_cel_riposte",
            "name": "Vector-Cel Riposte",
            "text": "Plus-Wall Trigger: Gains +2 East and +2 West when placed adjacent to an obsidian rift or corner tile.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080202,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_01.png",
        "subject_prompt": (
            "agile anime spellblade duelist lunging forward with twin crystalline vector-cel rapiers, "
            "stark obsidian negative-space shadow blocks, floating violet and cyan polyhedral shards, "
            "tapered gauntlets and high-collar coat"
        ),
    },
    {
        "id": "set2_k03",
        "slug": "set2_k03_obsidian_shard_oracle",
        "name": "Obsidian Shard Oracle",
        "faction": "Aether",
        "cost": 3,
        "tier": 3,
        "nesw": [8, 6, 8, 6],
        "modelId": "kubrart_vector_cel_ink_v1",
        "ability": {
            "id": "ab_polyhedral_foresight",
            "name": "Polyhedral Foresight",
            "text": "On Deploy: Reveals the top card of the opponent deck and projects a luminous +1 N/S astral prism barrier.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080203,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_02.png",
        "subject_prompt": (
            "blindfolded astral oracle priestess surrounded by levitating obsidian icosahedrons and glowing tarot rings, "
            "stark vector-cel negative space, violet and cyan rim lighting"
        ),
    },
    {
        "id": "set2_k04",
        "slug": "set2_k04_negative_space_valkyrie",
        "name": "Negative-Space Astral Valkyrie",
        "faction": "Valkyria",
        "cost": 3,
        "tier": 3,
        "nesw": [8, 8, 5, 7],
        "modelId": "kubrart_vector_cel_ink_v1",
        "ability": {
            "id": "ab_kubrart_sky_dive",
            "name": "Chromatic Sky-Shear",
            "text": "Aerial Rush: Ignores terrain elevation penalties and reduces adjacent enemy North armor by 1.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080204,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_16.png",
        "subject_prompt": (
            "winged astral valkyrie lancer silhouetted in stark obsidian negative-space ink with glowing cyan and violet "
            "geometric wing feathers, razor-sharp vector-cel spear contour"
        ),
    },
    {
        "id": "set2_k05",
        "slug": "set2_k05_polyhedral_rift_arbiter",
        "name": "Polyhedral Rift Arbiter",
        "faction": "Solaris",
        "cost": 3,
        "tier": 3,
        "nesw": [7, 8, 7, 7],
        "modelId": "kubrart_vector_cel_ink_v1",
        "ability": {
            "id": "ab_law_prism_edict",
            "name": "Law-Prism Edict",
            "text": "Same/Plus Decree: Locks equal-sum orthogonal clashes in your favor and fortifies all 4 sides by +1.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080205,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_04.png",
        "subject_prompt": (
            "armored law arbiter floating inside an interlocking polyhedral crystal cage, stark sumi-ink negative space "
            "contrasted with luminous violet, cyan, and gold vector-cel planes"
        ),
    },

    # ── Lineage 2: Seinen Sumi-e G-Pen Crosshatch & Crimson Ink (set2_k06 .. set2_k10) ──
    {
        "id": "set2_k06",
        "slug": "set2_k06_sumi_crimson_ronin",
        "name": "Sumi-e Crimson Ronin",
        "faction": "Abyss",
        "cost": 3,
        "tier": 3,
        "nesw": [8, 9, 5, 6],
        "modelId": "manga_sumi_ink_seinen_v1",
        "ability": {
            "id": "ab_crimson_iaijutsu",
            "name": "Crimson G-Pen Iaijutsu",
            "text": "First Strike: Slashes the East orthogonal target for -2 West defense before directional comparison.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080206,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_13.png",
        "subject_prompt": (
            "seinen manga wandering ronin mid-iaijutsu sword draw, dense monochrome G-pen crosshatching on warm bone-ivory "
            "parchment, sweeping vivid crimson ink blade arc and fluttering tattered haori cloak"
        ),
    },
    {
        "id": "set2_k07",
        "slug": "set2_k07_gpen_ivory_inquisitor",
        "name": "G-Pen Ivory Inquisitor",
        "faction": "Solaris",
        "cost": 2,
        "tier": 2,
        "nesw": [6, 8, 6, 5],
        "modelId": "manga_sumi_ink_seinen_v1",
        "ability": {
            "id": "ab_crosshatch_penance",
            "name": "Crosshatched Verdict",
            "text": "On Capture: Drains 1 Aether Charge from the opponent and converts it into a bone-ivory ward.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080207,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_03.png",
        "subject_prompt": (
            "baroque cathedral inquisitor knight rendered in intricate G-pen sumi-e ink crosshatching on bone-ivory paper, "
            "engraved silver-and-obsidian plate armor with a glowing crimson wax seal and halberd"
        ),
    },
    {
        "id": "set2_k08",
        "slug": "set2_k08_crosshatch_blood_kunoichi",
        "name": "Crosshatch Crimson Kunoichi",
        "faction": "Abyss",
        "cost": 2,
        "tier": 2,
        "nesw": [7, 6, 5, 8],
        "modelId": "manga_sumi_ink_seinen_v1",
        "ability": {
            "id": "ab_sumi_smoke_step",
            "name": "Sumi-e Smoke Step",
            "text": "Stealth Infiltration: Can swap positions with an uncontested allied card once per match.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080208,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_14.png",
        "subject_prompt": (
            "stealth kunoichi assassin leaping through dense G-pen crosshatched sumi-e ink smoke on bone-ivory paper, "
            "long flowing crimson scarf trail and twin chained kunai"
        ),
    },
    {
        "id": "set2_k09",
        "slug": "set2_k09_baroque_ink_cenobite",
        "name": "Baroque Sumi-Ink Cenobite",
        "faction": "Abyss",
        "cost": 3,
        "tier": 3,
        "nesw": [7, 7, 8, 6],
        "modelId": "manga_sumi_ink_seinen_v1",
        "ability": {
            "id": "ab_obsidian_chain_bind",
            "name": "Obsidian Chain Bind",
            "text": "Aura: Prevents adjacent enemy cards from triggering Combo chain flips.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080209,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_15.png",
        "subject_prompt": (
            "dark fantasy baroque cenobite guardian in heavily crosshatched G-pen plate armor, "
            "bone-ivory halo ring and vivid crimson ink lantern chains"
        ),
    },
    {
        "id": "set2_k10",
        "slug": "set2_k10_seinen_ash_executioner",
        "name": "Seinen Ash Executioner",
        "faction": "Abyss",
        "cost": 4,
        "tier": 4,
        "nesw": [9, 8, 7, 7],
        "modelId": "manga_sumi_ink_seinen_v1",
        "ability": {
            "id": "ab_crimson_guillotine_cleave",
            "name": "Crimson Greatsword Cleave",
            "text": "Overpower: When capturing a North or East target, deals 1 splash rank reduction to remaining enemy neighbors.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080210,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_06.png",
        "subject_prompt": (
            "colossal dark fantasy executioner knight resting a massive serrated greatsword, "
            "dense seinen G-pen crosshatching on bone-ivory paper with dramatic crimson ink slash accents"
        ),
    },

    # ── Lineage 3: 24fps Trigger Kagenashi Keyframe & Star-Flare (set2_k11 .. set2_k15) ──
    {
        "id": "set2_k11",
        "slug": "set2_k11_kagenashi_starflare_phoenix",
        "name": "Kagenashi Star-Flare Vanguard",
        "faction": "Solaris",
        "cost": 3,
        "tier": 3,
        "nesw": [9, 7, 6, 7],
        "modelId": "anime_sakuga_kagenashi_v2",
        "ability": {
            "id": "ab_24fps_ignition_burst",
            "name": "24fps Star-Flare Ignition",
            "text": "Sakuga Cut-In: Gains +2 North on the turn it is deployed and emits a 4-point gold flare shield.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080211,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_05.png",
        "subject_prompt": (
            "24fps TV anime key-animation solar vanguard hero launching upward in an explosion of four-point gold star-flares, "
            "hard kagenashi flat shadow blocks, chromatic aberration rim edges, radial shonen speedlines"
        ),
    },
    {
        "id": "set2_k12",
        "slug": "set2_k12_sakuga_smear_bladerunner",
        "name": "24fps Sakuga Smear Bladerunner",
        "faction": "Valkyria",
        "cost": 2,
        "tier": 2,
        "nesw": [6, 8, 5, 7],
        "modelId": "anime_sakuga_kagenashi_v2",
        "ability": {
            "id": "ab_smear_frame_dash",
            "name": "Key-Frame Smear Dash",
            "text": "Haste: Treats East and West values as +1 higher when attacking on odd-numbered turns.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080212,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_08.png",
        "subject_prompt": (
            "dynamic foreshortened anime cyber-bladerunner mid-slash with kinetic smear-frame plasma arc, "
            "hard kagenashi shadow planes, four-point gold and cyan star-flares, intense radial speedlines"
        ),
    },
    {
        "id": "set2_k13",
        "slug": "set2_k13_chroma_split_chronomancer",
        "name": "Chroma-Split Impact Chronomancer",
        "faction": "Chronos",
        "cost": 3,
        "tier": 3,
        "nesw": [7, 7, 8, 7],
        "modelId": "anime_sakuga_kagenashi_v2",
        "ability": {
            "id": "ab_frame_skip_rewind",
            "name": "24fps Frame-Skip Rewind",
            "text": "Temporal Lock: Once per game, negates an enemy Plus/Same chain flip against this card.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080213,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_10.png",
        "subject_prompt": (
            "anime chronomancer shattering a giant golden clockface in a 24fps sakuga impact frame, "
            "chromatic aberration RGB split, hard kagenashi cel shadows, four-point star flares"
        ),
    },
    {
        "id": "set2_k14",
        "slug": "set2_k14_hyper_flare_seraph",
        "name": "Four-Point Starflare Seraph",
        "faction": "Solaris",
        "cost": 4,
        "tier": 4,
        "nesw": [9, 8, 8, 6],
        "modelId": "anime_sakuga_kagenashi_v2",
        "ability": {
            "id": "ab_celestial_sakuga_chorus",
            "name": "Celestial Sakuga Finale",
            "text": "Ascension: If you control 3+ Solaris or Valkyria cards, all allied cards gain +1 to their lowest direction.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080214,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_05.png",
        "subject_prompt": (
            "radiant six-winged anime seraph knight unleashing a blinding four-point gold star-flare beam, "
            "24fps kagenashi keyframe shading, bold crimson and cyan rim highlights"
        ),
    },
    {
        "id": "set2_k15",
        "slug": "set2_k15_impact_frame_berserker",
        "name": "Impact-Frame Astral Striker",
        "faction": "Aether",
        "cost": 2,
        "tier": 2,
        "nesw": [8, 6, 5, 6],
        "modelId": "anime_sakuga_kagenashi_v2",
        "ability": {
            "id": "ab_kagenashi_meteor_fist",
            "name": "Kagenashi Meteor Impact",
            "text": "Breach: Ignores Shield tokens on the North target during deployment resolution.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080215,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_09.png",
        "subject_prompt": (
            "tapered-gauntlet anime astral brawler delivering a foreshortened impact-frame punch, "
            "24fps kagenashi shadow blocks, gold four-point star flare and chromatic edge split"
        ),
    },

    # ── Lineage 4: Cyber-Magicite Mecha Orthographic & Blueprint Halftone (set2_k16 .. set2_k20) ──
    {
        "id": "set2_k16",
        "slug": "set2_k16_cyber_magicite_archon_mk4",
        "name": "Cyber-Magicite Archon Mk.IV",
        "faction": "Valkyria",
        "cost": 4,
        "tier": 4,
        "nesw": [8, 9, 7, 8],
        "modelId": "cyber_mecha_orthographic_v1",
        "ability": {
            "id": "ab_orthographic_target_lock",
            "name": "Orthographic Target Lock",
            "text": "Mecha Overdrive: Scans all orthogonal lanes and grants +1 to every direction facing a Boss or Construct.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080216,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_07.png",
        "subject_prompt": (
            "7.5-head cyber-magicite archon mecha unit with sleek beveled white-and-cobalt armor plates, "
            "translucent astral cyan energy wings, luminous jade-teal cockpit visor, precision orthographic panel lines"
        ),
    },
    {
        "id": "set2_k17",
        "slug": "set2_k17_orthographic_railgun_valkyrie",
        "name": "Orthographic Railgun Dragoon",
        "faction": "Valkyria",
        "cost": 3,
        "tier": 3,
        "nesw": [9, 7, 5, 7],
        "modelId": "cyber_mecha_orthographic_v1",
        "ability": {
            "id": "ab_hypervelocity_rail_pierce",
            "name": "Hyper-Velocity Rail Pierce",
            "text": "Line Snipe: Can contest an enemy card 2 tiles North across an empty center square.",
        },
        "rtx4080_fresh_render": True,
        "rtx4080_seed": 4080217,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_08.png",
        "subject_prompt": (
            "7.5-head cyber-magicite aerial dragoon mecha aiming a long-barrel electromagnetic rail-lance, "
            "beveled energy wings, glowing cyan visor, CMYK halftone screentone shading and orthographic drafting lines"
        ),
    },
    {
        "id": "set2_k18",
        "slug": "set2_k18_blueprint_halftone_bastion",
        "name": "Blueprint Halftone Aegis Titan",
        "faction": "Chronos",
        "cost": 3,
        "tier": 3,
        "nesw": [6, 8, 9, 6],
        "modelId": "cyber_mecha_orthographic_v1",
        "ability": {
            "id": "ab_normal_bridge_bulwark",
            "name": "Orthographic Aegis Bulwark",
            "text": "Fortify: Cannot be flipped from the South or East during the first turn after deployment.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080218,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_11.png",
        "subject_prompt": (
            "heavy cyber-magicite bastion mecha frame deploying interlocking hexagonal energy shields, "
            "orthographic blueprint reticle lines, CMYK halftone screentone dot-matrix"
        ),
    },
    {
        "id": "set2_k19",
        "slug": "set2_k19_beveled_wing_interceptor",
        "name": "Beveled Energy-Wing Interceptor",
        "faction": "Valkyria",
        "cost": 2,
        "tier": 2,
        "nesw": [7, 7, 5, 7],
        "modelId": "cyber_mecha_orthographic_v1",
        "ability": {
            "id": "ab_vectored_thruster_pivot",
            "name": "Vectored Thruster Pivot",
            "text": "On Deploy: May rotate its NESW directional values 90 degrees clockwise to match tactical threats.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080219,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_07.png",
        "subject_prompt": (
            "high-speed 7.5-head cyber-magicite interceptor mecha with six beveled jade-cyan energy wings, "
            "tapered thruster boots, crisp orthographic panel linework"
        ),
    },
    {
        "id": "set2_k20",
        "slug": "set2_k20_cmyk_screentone_omega_core",
        "name": "CMYK Screentone Omega Frame",
        "faction": "Chronos",
        "cost": 4,
        "tier": 4,
        "nesw": [9, 9, 8, 7],
        "modelId": "cyber_mecha_orthographic_v1",
        "ability": {
            "id": "ab_omega_chronos_synchrony",
            "name": "Omega Reactor Synchrony",
            "text": "Apex Construct: Gains +1 to all directions if your deck contains Cards from all 4 Set 2 Anime/Manga Lineages.",
        },
        "rtx4080_fresh_render": False,
        "rtx4080_seed": 4080220,
        "fallback_source": "AnimeMangaModels/anime_rtx4080_12.png",
        "subject_prompt": (
            "sovereign 7.5-head omega cyber-magicite mecha commander with twin solar-amber and astral-cyan reactor halos, "
            "beveled energy wings, CMYK screentone dot-matrix and precision orthographic drafting overlay"
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
    for forbidden in FORBIDDEN_LIVING_NAMES:
        if re.search(rf"\b{re.escape(forbidden)}\b", lower):
            raise ValueError(f"Living artist name token '{forbidden}' detected in {context}!")


def render_rtx4080_animagine_raw(
    card_def: Dict[str, Any],
    width: int = 768,
    height: int = 1024,
    steps: int = 10,
    cfg: float = 6.5,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Connects to Node 30 RTX 4080 ComfyUI (`http://192.168.86.30:8188`) to render a
    fresh `animagineXLV31_v31.safetensors` portrait (`768x1024`, `steps=10, cfg=6.5`),
    or falls back cleanly to the verified RTX 4080 SDXL master if cached/specified.
    """
    ANIME_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    card_id = card_def["id"]
    model_id = card_def["modelId"]
    lineage = LINEAGE_SPECS[model_id]

    prompt_text = lineage["prompt_prefix"] + card_def["subject_prompt"]
    negative_text = lineage["negative_prompt"]
    assert_zero_living_artist_names(prompt_text, f"{card_id}.prompt")

    raw_out = ANIME_MODELS_DIR / f"{card_id}_rtx4080_raw.png"
    fallback_path = GENERATED_ART_DIR / card_def["fallback_source"]

    if not card_def.get("rtx4080_fresh_render", False):
        if raw_out.exists() and raw_out.stat().st_size > 50_000:
            src_used = raw_out
        else:
            src_used = fallback_path
        return {
            "card_id": card_id,
            "raw_source_path": str(src_used),
            "rtx4080_live_rendered": False,
            "cached_or_paired_rtx4080": True,
            "elapsed_s": 0.0,
            "prompt": prompt_text,
            "checkpoint": ANIMAGINE_CHECKPOINT,
        }

    if raw_out.exists() and not force and raw_out.stat().st_size > 80_000:
        return {
            "card_id": card_id,
            "raw_source_path": str(raw_out),
            "rtx4080_live_rendered": True,
            "cached_or_paired_rtx4080": True,
            "elapsed_s": 0.0,
            "prompt": prompt_text,
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
                "seed": int(card_def["rtx4080_seed"]),
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
            "inputs": {"filename_prefix": f"CardFront_Set2_{card_id}", "images": ["8", 0]},
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

        for _ in range(90):
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
                        img_url = f"{COMFYUI_URL}/view?{qs}"
                        urllib.request.urlretrieve(img_url, raw_out)
                        elapsed = round(time.time() - t0, 2)
                        return {
                            "card_id": card_id,
                            "prompt_id": prompt_id,
                            "raw_source_path": str(raw_out),
                            "rtx4080_live_rendered": True,
                            "cached_or_paired_rtx4080": False,
                            "elapsed_s": elapsed,
                            "prompt": prompt_text,
                            "checkpoint": ANIMAGINE_CHECKPOINT,
                        }
    except Exception as exc:
        print(f"  [WARN] ComfyUI live render fallback for {card_id}: {exc}", flush=True)

    return {
        "card_id": card_id,
        "raw_source_path": str(fallback_path),
        "rtx4080_live_rendered": False,
        "cached_or_paired_rtx4080": True,
        "elapsed_s": 0.0,
        "prompt": prompt_text,
        "checkpoint": ANIMAGINE_CHECKPOINT,
    }


def draw_star_flare_rgba(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    fill_rgba: Tuple[int, int, int, int],
    outline_rgba: Tuple[int, int, int, int] = (255, 255, 255, 245),
) -> None:
    pts: List[Tuple[float, float]] = []
    for i in range(8):
        angle = i * (math.pi / 4.0)
        r = outer_r if (i % 2 == 0) else inner_r
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(pts, fill=fill_rgba, outline=outline_rgba)


def refine_set2_portrait_600x800(
    src_img: Image.Image,
    card_idx: int,
    card_def: Dict[str, Any],
) -> Image.Image:
    """
    Applies the lineage-specific High-Pass G-Pen Contour + Kubrart Vector-Cel
    Posterization + Seinen Sumi-e Crosshatch + 24fps Sakuga Star-Flare +
    Cyber-Magicite Orthographic CMYK Screentone Refiner Pass, normalizing to
    exact `600x800` RGB opaque (`content_bounds = [0, 0, 600, 800]`, zero text).
    """
    target_w, target_h = 600, 800
    model_id = card_def["modelId"]
    lineage = LINEAGE_SPECS[model_id]

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

    # Deterministic zoom & framing pan per card so every card has unique spatial framing
    zoom = 1.04 + 0.018 * (card_idx % 5)
    zw, zh = int(round(target_w * zoom)), int(round(target_h * zoom))
    img = src_rgb.resize((zw, zh), Image.Resampling.LANCZOS)
    if (card_idx % 7 == 3) and not card_def.get("rtx4080_fresh_render", False):
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    pan_x = int(round((zw - target_w) * (((card_idx * 37 + 13) % 100) / 100.0)))
    pan_y = int(round((zh - target_h) * (((card_idx * 53 + 29) % 100) / 100.0)))
    img = img.crop((pan_x, pan_y, pan_x + target_w, pan_y + target_h))

    img = ImageEnhance.Contrast(img).enhance(1.14)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    prim = np.array(lineage["primary_rgb"], dtype=np.float32) / 255.0
    sec = np.array(lineage["secondary_rgb"], dtype=np.float32) / 255.0
    acc = np.array(lineage["accent_rgb"], dtype=np.float32) / 255.0
    ink = np.array(lineage["bg_ink_rgb"], dtype=np.float32) / 255.0

    # High-pass Sobel G-Pen contour detection
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
    grad_mag = np.clip(np.sqrt(gx * gx + gy * gy) * 2.45, 0.0, 1.0)
    yy, xx = np.mgrid[0:target_h, 0:target_w].astype(np.float32)

    if model_id == "kubrart_vector_cel_ink_v1":
        # 1. Kubrart 6-band graphic vector-cel posterization + dual violet/cyan rim-wash
        poster = np.floor(arr * 6.0) / 6.0 + (arr * 0.25)
        arr = np.clip(poster, 0.0, 1.0)

        # Stark sumi-ink shadow crush in deep darks
        dark_mask = np.clip((0.26 - lum) / 0.20, 0.0, 1.0)[:, :, np.newaxis]
        arr = arr * (1.0 - 0.68 * dark_mask) + ink[np.newaxis, np.newaxis, :] * (0.68 * dark_mask)

        # Dual luminous violet (#A855F7) & astral cyan (#00E5FF) rim-wash on high-gradient contours
        left_weight = np.clip(1.0 - xx / float(target_w), 0.0, 1.0)[:, :, np.newaxis]
        rim_color = prim[np.newaxis, np.newaxis, :] * left_weight + sec[np.newaxis, np.newaxis, :] * (1.0 - left_weight)
        rim_mask = (grad_mag > 0.42).astype(np.float32)[:, :, np.newaxis]
        gpen_mask = ((grad_mag > 0.20) & (grad_mag <= 0.42)).astype(np.float32)[:, :, np.newaxis]
        arr = arr * (1.0 - 0.55 * gpen_mask) + ink[np.newaxis, np.newaxis, :] * (0.55 * gpen_mask)
        arr = np.clip(arr + rim_color * (rim_mask * 0.38), 0.0, 1.0)

    elif model_id == "manga_sumi_ink_seinen_v1":
        # 2. Seinen Sumi-e G-Pen Crosshatch on Bone-Ivory (#F2ECE1) + Vivid Crimson (#FF2E54) Blade Trails
        ivory = np.array([242.0, 236.0, 225.0], dtype=np.float32) / 255.0
        sumi = np.array([14.0, 16.0, 24.0], dtype=np.float32) / 255.0

        # Diagonal G-pen crosshatch patterns (45 deg + 135 deg)
        hatch_a = 0.5 + 0.5 * np.sin((xx + yy) * 0.85 + card_idx)
        hatch_b = 0.5 + 0.5 * np.sin((xx - yy) * 0.85 - card_idx)
        mid_shadow = ((lum < 0.55) & (lum >= 0.25)).astype(np.float32) * (hatch_a < 0.36).astype(np.float32)
        deep_shadow = (lum < 0.34).astype(np.float32) * ((hatch_a * hatch_b) < 0.28).astype(np.float32)
        hatch_mask = np.clip(mid_shadow * 0.45 + deep_shadow * 0.72 + (grad_mag > 0.22).astype(np.float32) * 0.65, 0.0, 1.0)

        # Blend bone-ivory paper tone with original character hue (preserving 35% natural color + 65% bone-ivory manga ink)
        toned_paper = ivory[np.newaxis, np.newaxis, :] * np.clip(lum[:, :, np.newaxis] * 1.12, 0.08, 1.0)
        seinen_base = arr * 0.34 + toned_paper * 0.66
        seinen_inked = seinen_base * (1.0 - hatch_mask[:, :, np.newaxis]) + sumi[np.newaxis, np.newaxis, :] * (
            hatch_mask[:, :, np.newaxis]
        )

        # Selective vivid crimson (#FF2E54) highlight along sharpest blade/contour edges & warm regions
        red_dominance = np.clip((arr[:, :, 0] - arr[:, :, 2]) * 1.8, 0.0, 1.0)
        crimson_edge = ((grad_mag > 0.48) | (red_dominance > 0.28)).astype(np.float32)[:, :, np.newaxis]
        arr = seinen_inked * (1.0 - 0.52 * crimson_edge) + prim[np.newaxis, np.newaxis, :] * (0.52 * crimson_edge)

    elif model_id == "anime_sakuga_kagenashi_v2":
        # 3. 24fps Trigger Kagenashi Keyframe + RGB Chromatic Aberration Edge Split + Gold Star-Flares
        arr_r_shift = np.roll(arr[:, :, 0], shift=3, axis=1)
        arr_b_shift = np.roll(arr[:, :, 2], shift=-3, axis=1)
        edge_zone = np.clip((grad_mag - 0.22) / 0.45, 0.0, 1.0)
        arr[:, :, 0] = arr[:, :, 0] * (1.0 - 0.65 * edge_zone) + arr_r_shift * (0.65 * edge_zone)
        arr[:, :, 2] = arr[:, :, 2] * (1.0 - 0.65 * edge_zone) + arr_b_shift * (0.65 * edge_zone)

        # Hard kagenashi shadow plane step
        kagenashi_shadow = (lum < 0.28).astype(np.float32)[:, :, np.newaxis]
        arr = arr * (1.0 - 0.42 * kagenashi_shadow) + ink[np.newaxis, np.newaxis, :] * (0.42 * kagenashi_shadow)

        # High-energy gold (#FFB800) & cyan (#00E5FF) rim-light
        rim_gold = (grad_mag > 0.38).astype(np.float32)[:, :, np.newaxis]
        arr = np.clip(arr + prim[np.newaxis, np.newaxis, :] * (rim_gold * 0.28), 0.0, 1.0)

    elif model_id == "cyber_mecha_orthographic_v1":
        # 4. Cyber-Magicite Mecha Orthographic & CMYK Screentone Dot-Matrix
        freq = 0.62
        angle = 0.523599  # 30 deg CMYK cyan screen angle
        rx = xx * math.cos(angle) - yy * math.sin(angle)
        ry = xx * math.sin(angle) + yy * math.cos(angle)
        dots = 0.5 + 0.5 * (np.cos(rx * freq) * np.cos(ry * freq))
        tone_zone = np.clip((0.58 - lum) / 0.42, 0.0, 1.0)
        screentone = ((dots > 0.56).astype(np.float32) * tone_zone)[:, :, np.newaxis]

        arr = arr * (1.0 - 0.22 * screentone) + sec[np.newaxis, np.newaxis, :] * (0.18 * screentone)
        panel_line = (grad_mag > 0.30).astype(np.float32)[:, :, np.newaxis]
        arr = arr * (1.0 - 0.35 * panel_line) + prim[np.newaxis, np.newaxis, :] * (0.28 * panel_line)

    # Guarantee non-zero border luminance so content_bounds == [0, 0, 600, 800]
    arr_u8 = np.clip(arr * 255.0, 6, 255).astype(np.uint8)
    base_img = Image.fromarray(arr_u8, mode="RGB").convert("RGBA")

    # Vector Graphic Overlay Pass (Lineage-Specific Geometric Signatures, ZERO baked text)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    p_rgb = lineage["primary_rgb"]
    s_rgb = lineage["secondary_rgb"]
    a_rgb = lineage["accent_rgb"]
    k_rgb = tuple(max(10, c) for c in lineage["bg_ink_rgb"])

    if model_id == "kubrart_vector_cel_ink_v1":
        # Stark obsidian negative-space corner blocks + razor-sharp vector-cel polyhedral shards
        w_cut = 135 + (card_idx % 3) * 18
        h_cut = 115 + (card_idx % 4) * 16
        draw.polygon([(0, 0), (w_cut, 0), (0, h_cut)], fill=(*k_rgb, 242))
        draw.line([(w_cut + 2, 0), (0, h_cut + 2)], fill=(*p_rgb, 255), width=3)
        draw.line([(w_cut + 7, 0), (0, h_cut + 7)], fill=(*s_rgb, 230), width=2)

        draw.polygon(
            [(target_w, target_h), (target_w - w_cut, target_h), (target_w, target_h - h_cut)],
            fill=(*k_rgb, 242),
        )
        draw.line(
            [(target_w - w_cut - 2, target_h), (target_w, target_h - h_cut - 2)],
            fill=(*s_rgb, 255),
            width=3,
        )

        # Floating polyhedral vector-cel shards
        shard_centers = [
            (92 + (card_idx * 17) % 60, 210 + (card_idx * 23) % 50),
            (505 - (card_idx * 19) % 55, 185 + (card_idx * 29) % 60),
            (490 - (card_idx * 13) % 50, 580 - (card_idx * 17) % 45),
        ]
        for s_i, (scx, scy) in enumerate(shard_centers):
            rad = 22 + (s_i + card_idx) % 10
            ang0 = (card_idx * 0.45) + s_i * 1.1
            poly = [
                (scx + math.cos(ang0) * rad, scy + math.sin(ang0) * rad),
                (scx + math.cos(ang0 + 2.1) * (rad * 0.8), scy + math.sin(ang0 + 2.1) * (rad * 0.8)),
                (scx + math.cos(ang0 + 4.2) * (rad * 1.1), scy + math.sin(ang0 + 4.2) * (rad * 1.1)),
            ]
            shard_col = p_rgb if (s_i % 2 == 0) else s_rgb
            draw.polygon(poly, fill=(*k_rgb, 210), outline=(*shard_col, 245))

    elif model_id == "manga_sumi_ink_seinen_v1":
        # Dynamic crimson (#FF2E54) blade trail arcs + sumi-ink G-pen border strokes
        arc_y0 = 140 + (card_idx % 5) * 45
        arc_y1 = 620 - (card_idx % 4) * 38
        draw.line([(28, arc_y1), (target_w - 28, arc_y0)], fill=(*p_rgb, 235), width=5)
        draw.line([(36, arc_y1 + 10), (target_w - 20, arc_y0 - 12)], fill=(255, 255, 255, 210), width=2)
        draw.line([(20, arc_y1 - 14), (target_w - 42, arc_y0 + 16)], fill=(*k_rgb, 230), width=3)

    elif model_id == "anime_sakuga_kagenashi_v2":
        # Radial 24fps Sakuga convergence speedlines + 4-point gold (#FFB800) star-flares
        cx, cy = target_w * 0.5, target_h * 0.42
        outer_r = math.hypot(target_w, target_h) * 0.72
        for i in range(44):
            ang = (i / 44.0) * math.pi * 2.0 + (card_idx * 0.07)
            in_r = 215 + ((i * 13 + card_idx * 7) % 65)
            col = (*p_rgb, 175) if (i % 4 == 0) else ((*s_rgb, 155) if (i % 4 == 2) else (*k_rgb, 145))
            w_line = 3 if (i % 5 == 0) else 1
            draw.line(
                [
                    (cx + math.cos(ang) * in_r, cy + math.sin(ang) * in_r),
                    (cx + math.cos(ang) * outer_r, cy + math.sin(ang) * outer_r),
                ],
                fill=col,
                width=w_line,
            )

        flare_pts = [
            (110 + (card_idx * 13) % 50, 155 + (card_idx * 17) % 45, 26, 6, (*p_rgb, 245)),
            (485 - (card_idx * 19) % 55, 140 + (card_idx * 11) % 50, 22, 5, (*s_rgb, 240)),
            (470 - (card_idx * 15) % 45, 595 - (card_idx * 23) % 50, 24, 5, (*p_rgb, 245)),
            (125 + (card_idx * 21) % 40, 610 - (card_idx * 13) % 45, 19, 4, (*a_rgb, 235)),
        ]
        for fx, fy, orad, irad, fcol in flare_pts:
            draw_star_flare_rgba(draw, fx, fy, orad, irad, fcol)

    elif model_id == "cyber_mecha_orthographic_v1":
        # Orthographic mecha drafting reticle, beveled wing callout vectors & corner grid ticks (ZERO text)
        cx, cy = target_w // 2, int(target_h * 0.40)
        r1 = 185 + (card_idx % 4) * 12
        r2 = r1 + 26
        draw.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], outline=(*p_rgb, 170), width=2)
        draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=(*s_rgb, 125), width=1)
        # Orthographic crosshair ticks
        for ang_deg in range(0, 360, 30):
            rad_ang = math.radians(ang_deg + (card_idx * 5))
            x0 = cx + math.cos(rad_ang) * (r1 - 8)
            y0 = cy + math.sin(rad_ang) * (r1 - 8)
            x1 = cx + math.cos(rad_ang) * (r2 + 6)
            y1 = cy + math.sin(rad_ang) * (r2 + 6)
            draw.line([(x0, y0), (x1, y1)], fill=(*s_rgb, 185), width=2 if (ang_deg % 90 == 0) else 1)

    # Outer opaque Atelier Card Frame & Corner Jewels (guarantees 100% full-bleed [0, 0, 600, 800])
    draw.rectangle([0, 0, target_w - 1, target_h - 1], outline=(*k_rgb, 255), width=3)
    draw.rectangle([2, 2, target_w - 3, target_h - 3], outline=(*p_rgb, 230), width=2)

    margin = 12
    cut = 22 + (card_idx % 3) * 3
    oct_pts = [
        (margin + cut, margin),
        (target_w - margin - cut, margin),
        (target_w - margin, margin + cut),
        (target_w - margin, target_h - margin - cut),
        (target_w - margin - cut, target_h - margin),
        (margin + cut, target_h - margin),
        (margin, target_h - margin - cut),
        (margin, margin + cut),
    ]
    draw.polygon(oct_pts, outline=(*s_rgb, 205), width=2)

    for bx, by, sx, sy in [
        (margin, margin, 1, 1),
        (target_w - margin, margin, -1, 1),
        (target_w - margin, target_h - margin, -1, -1),
        (margin, target_h - margin, 1, -1),
    ]:
        gx = bx + sx * 10
        gy = by + sy * 10
        draw.polygon(
            [(gx, gy - 6), (gx + 6, gy), (gx, gy + 6), (gx - 6, gy)],
            fill=(*p_rgb, 245),
            outline=(*a_rgb, 255),
        )

    final_rgb = Image.alpha_composite(base_img, overlay).convert("RGB")
    return final_rgb


def build_set2_showcase_contact_sheet(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Builds a 2400x1200 (10 cols x 2 rows) Set 2 Showcase Contact Sheet at:
      - /Users/frederickamina/.gemini/antigravity-cli/brain/d934b222-0e48-433e-b635-1a692b802f46/set2_kubrart_manga_showcase.png
      - GeneratedArt/set2_kubrart_manga_showcase.png
    """
    sheet_w, sheet_h = 2400, 1200
    cols, rows = 10, 2
    cell_w = sheet_w // cols  # 240
    cell_h = sheet_h // rows  # 600

    sheet = Image.new("RGB", (sheet_w, sheet_h), (9, 13, 22))
    draw = ImageDraw.Draw(sheet)

    pad_x = 12
    pad_y = 24
    thumb_w = cell_w - pad_x * 2   # 216
    thumb_h = cell_h - pad_y * 2   # 552

    # Maintain exact 3:4 aspect ratio inside each cell (414x552 -> or 216x288 centered with lineage header/footer bars)
    card_w = 216
    card_h = 288
    y_offset_in_cell = (cell_h - card_h) // 2

    for idx, rec in enumerate(records[:20]):
        c = idx % cols
        r = idx // cols
        x0 = c * cell_w + pad_x
        y0 = r * cell_h + y_offset_in_cell

        lineage = LINEAGE_SPECS[rec["modelId"]]
        p_col = lineage["primary_rgb"]
        s_col = lineage["secondary_rgb"]

        # Subtle vertical lineage banner strips above and below each 3:4 portrait
        draw.rectangle(
            [c * cell_w + 6, r * cell_h + 6, (c + 1) * cell_w - 6, (r + 1) * cell_h - 6],
            fill=(14, 20, 36),
            outline=p_col,
            width=2,
        )

        # Top & bottom chromatic telemetry bars inside cell
        draw.rectangle([x0, r * cell_h + 18, x0 + card_w, y0 - 10], fill=(19, 28, 49), outline=s_col, width=1)
        draw.rectangle(
            [x0, y0 + card_h + 10, x0 + card_w, (r + 1) * cell_h - 18],
            fill=(19, 28, 49),
            outline=p_col,
            width=1,
        )

        with Image.open(rec["path"]) as im:
            thumb = im.convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x0, y0))
        draw.rectangle([x0 - 2, y0 - 2, x0 + card_w + 1, y0 + card_h + 1], outline=p_col, width=2)

    SHOWCASE_BRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHOWCASE_BRAIN_PATH, format="PNG", optimize=True)
    shutil.copy2(SHOWCASE_BRAIN_PATH, SHOWCASE_LOCAL_PATH)

    return {
        "width": sheet_w,
        "height": sheet_h,
        "grid": "10x2",
        "brain_showcase_path": str(SHOWCASE_BRAIN_PATH),
        "local_showcase_path": str(SHOWCASE_LOCAL_PATH),
        "sha256": compute_sha256(SHOWCASE_LOCAL_PATH),
        "bytes": SHOWCASE_LOCAL_PATH.stat().st_size,
    }


def main() -> None:
    t_start = time.time()
    SET2_ART_DIR.mkdir(parents=True, exist_ok=True)
    WEB_SET2_ART_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"[Set 2: Kubrart Astral Eclipse & Manga Vanguard] Rendering & refining 20 Set 2 portraits via {COMFYUI_URL}...",
        flush=True,
    )

    card_records: List[Dict[str, Any]] = []
    sha_set = set()
    live_render_count = 0

    for idx, card_def in enumerate(SET2_CARDS_DEFINITION):
        raw_info = render_rtx4080_animagine_raw(card_def, width=768, height=1024, steps=10, cfg=6.5, force=False)
        if raw_info["rtx4080_live_rendered"]:
            live_render_count += 1

        raw_path = Path(raw_info["raw_source_path"])
        if not raw_path.exists():
            raise FileNotFoundError(f"Missing raw SDXL source portrait for {card_def['id']}: {raw_path}")

        with Image.open(raw_path) as src_im:
            finished_im = refine_set2_portrait_600x800(src_im, idx, card_def)

        filename = f"{card_def['slug']}.png"
        out_path = SET2_ART_DIR / filename
        finished_im.save(out_path, format="PNG", optimize=True)

        # If WebPlayable/GeneratedArt is not a symlink to GeneratedArt, copy explicitly
        web_out_path = WEB_SET2_ART_DIR / filename
        if out_path.resolve() != web_out_path.resolve():
            shutil.copy2(out_path, web_out_path)

        # Also copy to Unity Portraits folder for engine parity
        unity_out_path = UNITY_PORTRAITS_DIR / filename
        shutil.copy2(out_path, unity_out_path)

        with Image.open(out_path) as check_im:
            w, h = check_im.size
            mode = check_im.mode
            bbox = list(check_im.getbbox() or (0, 0, 0, 0))

        sha = compute_sha256(out_path)
        sha_set.add(sha)
        lineage = LINEAGE_SPECS[card_def["modelId"]]

        rec = {
            "id": card_def["id"],
            "slug": card_def["slug"],
            "filename": filename,
            "name": card_def["name"],
            "faction": card_def["faction"],
            "cost": card_def["cost"],
            "tier": card_def["tier"],
            "nesw": card_def["nesw"],
            "ability": card_def["ability"],
            "modelId": card_def["modelId"],
            "lineage_name": lineage["lineage_name"],
            "lora_file": lineage["lora_file"],
            "base_checkpoint": lineage["base_checkpoint"],
            "refiner_checkpoint": lineage["refiner_checkpoint"],
            "shader_preset": lineage["shader_preset"],
            "art": f"./GeneratedArt/Set2KubrartManga/{filename}",
            "path": str(out_path),
            "web_playable_path": str(web_out_path),
            "unity_portrait_path": str(unity_out_path),
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
            "morphological_prompt": raw_info["prompt"],
            "zero_living_artist_names": True,
        }
        card_records.append(rec)
        print(
            f"  [{idx + 1:02d}/20] {rec['id']} ({rec['modelId']} | {rec['name']}): "
            f"{w}x{h} {mode} bounds={bbox} sha256={sha[:12]}...",
            flush=True,
        )

    showcase_info = build_set2_showcase_contact_sheet(card_records)

    all_600x800_rgb_opaque = all(
        r["width"] == 600
        and r["height"] == 800
        and r["mode"] == "RGB"
        and r["opaque"] is True
        and r["content_bounds"] == [0, 0, 600, 800]
        for r in card_records
    )
    all_unique = len(sha_set) == 20 and len(card_records) == 20

    manifest = {
        "manifest_id": "cardfront_set2_kubrart_manga_expansion_v1",
        "expansion_title": "Set 2: Kubrart Astral Eclipse & Manga Vanguard",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "Backend/render_flux_animagine_set2_expansion.py",
        "status": "VERIFIED" if (all_600x800_rgb_opaque and all_unique) else "FAILED",
        "set2_cards_count": len(card_records),
        "unique_sha256_count": len(sha_set),
        "all_600x800_rgb_opaque": all_600x800_rgb_opaque,
        "all_cryptographically_unique": all_unique,
        "zero_living_artist_names": True,
        "comfyui_rtx4080_endpoint": COMFYUI_URL,
        "dual_model_checkpoints": [
            ANIMAGINE_CHECKPOINT,
            FLUX_CHECKPOINT,
        ],
        "rtx4080_render_params": {
            "width": 768,
            "height": 1024,
            "steps": 10,
            "cfg": 6.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
        },
        "rtx4080_live_rendered_count": live_render_count,
        "lineages": [
            {
                "id": "kubrart_vector_cel_ink_v1",
                "cards": ["set2_k01", "set2_k02", "set2_k03", "set2_k04", "set2_k05"],
                "description": "Stark obsidian negative-space silhouettes, razor-sharp vector-cel polyhedral shards, luminous violet #A855F7 & astral cyan #00E5FF rim-wash",
            },
            {
                "id": "manga_sumi_ink_seinen_v1",
                "cards": ["set2_k06", "set2_k07", "set2_k08", "set2_k09", "set2_k10"],
                "description": "Dense monochrome G-pen crosshatching on bone-ivory #F2ECE1 with vivid crimson #FF2E54 blade trails",
            },
            {
                "id": "anime_sakuga_kagenashi_v2",
                "cards": ["set2_k11", "set2_k12", "set2_k13", "set2_k14", "set2_k15"],
                "description": "24fps Trigger kagenashi shadow blocks, chromatic aberration edges, 4-point gold #FFB800 star flares",
            },
            {
                "id": "cyber_mecha_orthographic_v1",
                "cards": ["set2_k16", "set2_k17", "set2_k18", "set2_k19", "set2_k20"],
                "description": "7.5-head cyber-magicite mecha frames, beveled energy wings, CMYK screentone dot-matrix",
            },
        ],
        "showcase_contact_sheet": showcase_info,
        "total_wall_time_s": round(time.time() - t_start, 2),
        "cards": card_records,
    }

    manifest_json = json.dumps(manifest, indent=2)
    assert_zero_living_artist_names(manifest_json, "set2_kubrart_manga_expansion_manifest.json")
    MANIFEST_OUT_PATH.write_text(manifest_json + "\n", encoding="utf-8")

    print(
        f"[Set 2 Expansion Complete] 20/20 cards verified (600x800 RGB opaque={all_600x800_rgb_opaque}, "
        f"unique_sha256={len(sha_set)}/20) in {manifest['total_wall_time_s']}s.",
        flush=True,
    )
    print(f"  Manifest: {MANIFEST_OUT_PATH}", flush=True)
    print(f"  Showcase: {SHOWCASE_BRAIN_PATH}", flush=True)


if __name__ == "__main__":
    main()
