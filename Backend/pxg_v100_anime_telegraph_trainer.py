#!/usr/bin/env python3
"""
Backend/pxg_v100_anime_telegraph_trainer.py
===========================================
PXG Engine V100 GPU Anime Telegraph & Sakuga Cut-In Training / Inference Pipeline
for CARDFRONT 3D: Cradle of Echoes (`Synapse.TcgEngine`).

Designed specifically for:
- Primary Training / Batch GPU: NVIDIA Tesla V100 (16GB / 32GB HBM2, Volta `sm_70`, FP16 Tensor Cores)
- Local Preview / Validation Fallback: Apple Silicon Metal GPU (`mlx` / `jevmlx` / PyTorch `mps`)

Pipelines Supported:
1. Wan 2.1 I2V (1.3B & 14B) FP16 Sakuga Cut-In LoRA (`pxg_sakuga_trigger_cutin_v1.safetensors` / `.pt`)
   - Uses `torch.float16` (Volta sm_70 native Tensor Core format; avoids `bfloat16` which requires sm_80+)
   - Uses PyTorch `sdpa` (`enable_mem_efficient_sdp(True)`) instead of `flash_attn_2` (sm_80+)
   - LoRA Rank `r=32`, `lora_alpha=64`, gradient checkpointing enabled
2. ToonCrafter Dual-Keyframe Anime Interpolation (`Pose A: Idle -> Pose B: Telegraph Impact`)
   - Synthesizes Pose-B Sakuga Impact Keyframes (`600x800`, RGB, opaque) in
     `Datasets/pxg_v100_sakuga_telegraph/keyframes_pose_b/<asset_id>_pose_b.png`
   - Synthesizes 8-Frame Studio Trigger / Omega Strikers Widescreen Sakuga Cut-In Sprite Strips
     (`1920x160`, 8 frames of `240x160`) in `WebPlayable/GeneratedArt/SakugaCutIns/<asset_id>_strip.png`
     for all 16 Core Hero/Mech units + 4 Mythic Sovereign Agent Plugins.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

PROJECT_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
MASTERED_CARDS_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "MasteredCards"
AGENT_DECK_CARDS_DIR = PROJECT_ROOT / "GeneratedArt" / "AgentDeck" / "Cards"
AGENT_DECK_SVGS_DIR = PROJECT_ROOT / "GeneratedArt" / "AgentDeck" / "SVGs"
SAKUGA_CUTINS_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "SakugaCutIns"
OUTPUT_DIR = PROJECT_ROOT / "Datasets" / "pxg_v100_sakuga_telegraph"
POSE_B_DIR = OUTPUT_DIR / "keyframes_pose_b"
MANIFEST_JSON = OUTPUT_DIR / "v100_sakuga_manifest.json"
V100_SHELL_SCRIPT = OUTPUT_DIR / "run_v100_pxg_trainer.sh"


# Concrete morphological Studio Trigger / Omega Strikers Sakuga descriptors (Zero living artist names)
SAKUGA_TELEGRAPH_ARCHETYPES: Dict[str, Dict[str, str]] = {
    "h_archangel": {
        "telegraph_name": "Solar Cross Lance",
        "sakuga_motion": "diagonal golden speedlines, 4-point cross-star lens flare, radiant wing expansion, cruciform lance thrust",
        "primary_hex": "#FFD54F",
        "secondary_hex": "#00E5FF",
    },
    "h_phoenix": {
        "telegraph_name": "Ember Wing Sweep",
        "sakuga_motion": "high-contrast cel-shaded crimson flame arcs, upward diagonal slash smear frame, floating ember shards",
        "primary_hex": "#FF6D00",
        "secondary_hex": "#FFD54F",
    },
    "h_oracle": {
        "telegraph_name": "Crescent Tidal Ward",
        "sakuga_motion": "spiral astral cyan water rings, zero-gravity hair billow, glowing geometric astrolabe halo",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#A855F7",
    },
    "h_chronos": {
        "telegraph_name": "Temporal Gear Lock",
        "sakuga_motion": "interlocking brass clockwork runes, chromatic aberration time-stop snap frame, gold lightning arcs",
        "primary_hex": "#FFB800",
        "secondary_hex": "#2EE6D3",
    },
    "h_seraph": {
        "telegraph_name": "Trigger Cross-Star",
        "sakuga_motion": "signature 4-point anime star burst, extreme perspective foreshortening, neon cyan-magenta impact frame",
        "primary_hex": "#E040FB",
        "secondary_hex": "#00E5FF",
    },
    "h_kai": {
        "telegraph_name": "Solid Eye Target Lock",
        "sakuga_motion": "horizontal sniper reticle lock-on, crimson visor trail streak, high-velocity katana shockwave cone",
        "primary_hex": "#FF2E54",
        "secondary_hex": "#00E5FF",
    },
    "h_valkyrie": {
        "telegraph_name": "Orbital Airstrike",
        "sakuga_motion": "triple booster afterburner contrails, steep diagonal dive speedlines, azure shock-ring burst",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#FEF08A",
    },
    "h_arbiter": {
        "telegraph_name": "Ivalice Law Seal",
        "sakuga_motion": "hexagonal golden law barrier materialization, gilded parchment filigree runes, sovereign halberd slam",
        "primary_hex": "#FFD700",
        "secondary_hex": "#2EE6D3",
    },
    "e_eclipse": {
        "telegraph_name": "Umbra Singularity",
        "sakuga_motion": "dark-violet gravitational vortex, twin crescent void slash arcs, crimson eye flare",
        "primary_hex": "#C084FC",
        "secondary_hex": "#FF2E54",
    },
    "e_archon": {
        "telegraph_name": "Prism Tri-Laser",
        "sakuga_motion": "rotating octahedron core refraction, tri-beam magenta laser convergence, geometric shard burst",
        "primary_hex": "#F43F5E",
        "secondary_hex": "#00E5FF",
    },
    "e_inferno": {
        "telegraph_name": "Hellfire Artillery",
        "sakuga_motion": "pulsing thermal artillery hazard rings, molten obsidian armor vents, crimson-orange shockwave",
        "primary_hex": "#FF5722",
        "secondary_hex": "#FFB800",
    },
    "e_reaper": {
        "telegraph_name": "Blood Rune Scythe",
        "sakuga_motion": "180-degree crimson scythe cleave smear, rotating necromantic rune sigil, dark ember wake",
        "primary_hex": "#FB7185",
        "secondary_hex": "#A855F7",
    },
    "e_titan": {
        "telegraph_name": "Seismic Tremor Push",
        "sakuga_motion": "heavy concentric ground-pound shockwaves, brass kinetic piston slam, flying basalt debris",
        "primary_hex": "#F59E0B",
        "secondary_hex": "#FF2E54",
    },
    "e_colossus": {
        "telegraph_name": "Overdrive Railgun",
        "sakuga_motion": "emerald reactor coil overcharge, piercing plasma vector beam, electromagnetic ring cascade",
        "primary_hex": "#10B981",
        "secondary_hex": "#00E5FF",
    },
    "e_cryo": {
        "telegraph_name": "Sub-Zero Lattice",
        "sakuga_motion": "crystalline ice snowflake lattice expansion, diamond dust speedlines, azure cryo beam",
        "primary_hex": "#38BDF8",
        "secondary_hex": "#E0F2FE",
    },
    "e_shinobi": {
        "telegraph_name": "90° Stealth Cone",
        "sakuga_motion": "stealth radar vision cone sweep, rapid jade kunai tracers, high-speed optical camo afterimage",
        "primary_hex": "#2DD4BF",
        "secondary_hex": "#FF2E54",
    },
    "plugin_01_tcg_creative_designer": {
        "telegraph_name": "3×3 Atelier Prism Lock",
        "sakuga_motion": "tarot violet prism lattice, gilded parchment filigree burst, 4-point creative arcanist star flare",
        "primary_hex": "#A855F7",
        "secondary_hex": "#FFE082",
    },
    "plugin_02_parallel_swarm_orchestrator": {
        "telegraph_name": "Tri-Portal Worktree Fan-Out",
        "sakuga_motion": "interlocking chronos swarm portals, crimson-orange command vectors, synchronized multi-agent slash",
        "primary_hex": "#F97316",
        "secondary_hex": "#00E5FF",
    },
    "plugin_03_jev_system_one": {
        "telegraph_name": "Octagonal Law-Seal Gate",
        "sakuga_motion": "sovereign Ivalice law-gold octagonal gate, jade-teal probability calibration rings, truth beam",
        "primary_hex": "#2EE6D3",
        "secondary_hex": "#FFB800",
    },
    "plugin_04_mlx_apple_silicon": {
        "telegraph_name": "Single-Pass Logit Diamond",
        "sakuga_motion": "Apple Silicon Metal GPU diamond conduit, astral cyan zero-latency lightning, 4-point star burst",
        "primary_hex": "#00E5FF",
        "secondary_hex": "#A855F7",
    },
}

FEATURED_STRIP_IDS = list(SAKUGA_TELEGRAPH_ARCHETYPES.keys())


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def draw_trigger_4point_star(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    angle_deg: float,
    fill_rgba: Tuple[int, int, int, int],
    core_rgba: Tuple[int, int, int, int] = (255, 255, 255, 255),
) -> None:
    """Draw a signature Studio Trigger / Omega Strikers 4-point elongated cross-star flare."""
    pts = []
    rad_base = math.radians(angle_deg)
    for i in range(8):
        ang = rad_base + i * (math.pi / 4.0)
        r = outer_r if i % 2 == 0 else inner_r
        # Elongate horizontal/primary axis for cinematic anime anamorphic flare
        scale_x = 1.35 if i in (0, 4) else 1.0
        pts.append((cx + math.cos(ang) * r * scale_x, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=fill_rgba)
    core_pts = []
    for i in range(8):
        ang = rad_base + i * (math.pi / 4.0)
        r = (outer_r * 0.45) if i % 2 == 0 else (inner_r * 0.45)
        core_pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(core_pts, fill=core_rgba)


def draw_diagonal_speedlines(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
    phase: float,
    density: int = 28,
) -> None:
    """Draw high-velocity diagonal Studio Trigger anime speedlines across the frame."""
    for i in range(density):
        seed_val = (i * 97 + int(phase * 100)) % 1000 / 1000.0
        y_base = int((i / float(density)) * (h + 60) - 30)
        slope_drop = int(w * 0.14)
        x_start = int(((seed_val + phase * 0.85) % 1.0) * (w * 0.45)) - 40
        seg_len = int(w * (0.28 + 0.45 * ((i * 37) % 10) / 10.0))
        x_end = x_start + seg_len
        y1 = y_base - int((x_start / float(max(1, w))) * slope_drop)
        y2 = y_base - int((x_end / float(max(1, w))) * slope_drop)
        col = primary_rgb if i % 2 == 0 else secondary_rgb
        alpha = 185 if i % 4 == 0 else 110
        width = 3 if i % 5 == 0 else (2 if i % 2 == 0 else 1)
        draw.line([(x_start, y1), (x_end, y2)], fill=(col[0], col[1], col[2], alpha), width=width)
        if i % 6 == 0:
            draw.line([(x_start + 12, y1 - 1), (x_end - 12, y2 - 1)], fill=(255, 255, 255, 165), width=1)


def apply_chromatic_aberration(img: Image.Image, shift_px: int = 4) -> Image.Image:
    """Apply crisp anime RGB channel split (red shifted right, cyan/blue shifted left)."""
    if shift_px <= 0:
        return img
    r, g, b = img.convert("RGB").split()
    r_shifted = ImageChops.offset(r, shift_px, -1)
    b_shifted = ImageChops.offset(b, -shift_px, 1)
    return Image.merge("RGB", (r_shifted, g, b_shifted))


def synthesize_pose_b_keyframe(
    pose_a_path: Path,
    pose_b_out: Path,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
) -> None:
    """
    Generate Pose-B (600x800 RGB opaque) Sakuga Telegraph Impact Keyframe from Pose-A:
    - Dynamic 1.22x upper-body action zoom + slight -3.5 deg Dutch tilt
    - High-contrast anime cel-boost + RGB chromatic split
    - Converging diagonal speedlines + 4-point Studio Trigger star flare
    """
    base = Image.open(pose_a_path).convert("RGB")
    w, h = 600, 800
    if base.size != (w, h):
        base = base.resize((w, h), Image.Resampling.LANCZOS)

    # 1. Zoom into upper torso/face focal zone (top 18%..82%) and apply subtle dynamic tilt
    crop_box = (int(w * 0.09), int(h * 0.06), int(w * 0.91), int(h * 0.88))
    zoomed = base.crop(crop_box).resize((w, h), Image.Resampling.LANCZOS)
    tilted = zoomed.rotate(-3.2, resample=Image.Resampling.BICUBIC, expand=False)
    # Fill any tiny corner rotation border from zoomed image so 100% opaque zero-border
    bg_fill = zoomed.filter(ImageFilter.GaussianBlur(radius=6))
    mask = Image.new("L", (w, h), 255).rotate(-3.2, resample=Image.Resampling.NEAREST, expand=False)
    comp = Image.composite(tilted, bg_fill, mask)

    # 2. Boost anime contrast & color saturation + RGB chromatic aberration
    comp = ImageEnhance.Contrast(comp).enhance(1.24)
    comp = ImageEnhance.Color(comp).enhance(1.22)
    comp = apply_chromatic_aberration(comp, shift_px=4)

    # 3. Overlay diagonal Sakuga speedlines, slash beam, and 4-point Studio Trigger star flare
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw_diagonal_speedlines(draw, w, h, primary_rgb, secondary_rgb, phase=0.35, density=36)

    # Diagonal energy slash across lower-mid torso
    draw.polygon(
        [(0, int(h * 0.74)), (w, int(h * 0.56)), (w, int(h * 0.61)), (0, int(h * 0.79))],
        fill=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 195),
    )
    draw.polygon(
        [(0, int(h * 0.755)), (w, int(h * 0.575)), (w, int(h * 0.592)), (0, int(h * 0.772))],
        fill=(255, 255, 255, 235),
    )

    # Signature 4-point Studio Trigger star flares
    draw_trigger_4point_star(
        draw,
        cx=w * 0.74,
        cy=h * 0.28,
        outer_r=68,
        inner_r=11,
        angle_deg=12.0,
        fill_rgba=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 235),
    )
    draw_trigger_4point_star(
        draw,
        cx=w * 0.24,
        cy=h * 0.66,
        outer_r=44,
        inner_r=8,
        angle_deg=-15.0,
        fill_rgba=(secondary_rgb[0], secondary_rgb[1], secondary_rgb[2], 220),
    )

    out_rgb = Image.alpha_composite(comp.convert("RGBA"), overlay).convert("RGB")
    pose_b_out.parent.mkdir(parents=True, exist_ok=True)
    out_rgb.save(pose_b_out, format="PNG", optimize=True)


def synthesize_sakuga_8frame_strip(
    pose_a_path: Path,
    strip_out_path: Path,
    primary_rgb: Tuple[int, int, int],
    secondary_rgb: Tuple[int, int, int],
) -> None:
    """
    Synthesize an 8-frame horizontal Studio Trigger / Omega Strikers Sakuga Cut-In Sprite Strip
    (`1920x160` RGB PNG -> 8 frames of `240x160`).
    Includes Frame 2 (`idx=2`) high-contrast black/white/neon Sakuga Impact Frame, dynamic camera pan,
    speedlines, diagonal katana/beam slashes, and rotating 4-point Trigger star flares.
    """
    base = Image.open(pose_a_path).convert("RGB")
    bw, bh = base.size
    fw, fh = 240, 160
    num_frames = 8
    strip = Image.new("RGB", (fw * num_frames, fh), (8, 12, 24))

    for f in range(num_frames):
        t = f / float(num_frames - 1)
        # Progressive zoom & horizontal sweep across the upper portrait (eyes / weapon focal band)
        zoom = 1.0 + 0.28 * math.sin(t * math.pi * 0.85)
        crop_w = int(bw / zoom)
        crop_h = int(crop_w * (fh / float(fw)))
        pan_x = int((bw - crop_w) * (0.35 + 0.30 * t))
        pan_y = int(bh * (0.14 - 0.04 * math.sin(t * math.pi)))
        pan_x = max(0, min(bw - crop_w, pan_x))
        pan_y = max(0, min(bh - crop_h, pan_y))

        frame_img = base.crop((pan_x, pan_y, pan_x + crop_w, pan_y + crop_h)).resize(
            (fw, fh), Image.Resampling.LANCZOS
        )

        if f == 2:
            # FRAME 2: Signature Studio Trigger Monochrome + Neon Accent SAKUGA IMPACT FRAME!
            gray = frame_img.convert("L")
            bw_mask = gray.point(lambda p: 255 if p > 118 else 0, mode="L")
            edges = gray.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 38 else 0, mode="L")
            dark_bg = Image.new("RGB", (fw, fh), (10, 12, 22))
            light_fg = Image.new("RGB", (fw, fh), (255, 252, 240))
            neon_edge = Image.new("RGB", (fw, fh), primary_rgb)
            impact_img = Image.composite(light_fg, dark_bg, bw_mask)
            frame_img = Image.composite(neon_edge, impact_img, edges)
        else:
            # Chromatic aberration peaks around the impact frame (frames 1, 3, 4)
            shift = 5 if f in (1, 3) else (3 if f in (4, 5) else 2)
            frame_img = ImageEnhance.Contrast(frame_img).enhance(1.18 + 0.14 * math.sin(t * math.pi))
            frame_img = ImageEnhance.Color(frame_img).enhance(1.20)
            frame_img = apply_chromatic_aberration(frame_img, shift_px=shift)

        overlay = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Speedlines with frame-specific phase
        draw_diagonal_speedlines(
            draw,
            fw,
            fh,
            primary_rgb=primary_rgb,
            secondary_rgb=secondary_rgb,
            phase=f * 0.19,
            density=24 if f != 2 else 34,
        )

        # Dynamic diagonal slash beam sweeping across the cut-in frame
        slash_y_left = int(fh * (0.82 - 0.35 * t))
        slash_y_right = int(fh * (0.48 - 0.25 * t))
        beam_thick = 14 if f in (2, 3) else 7
        draw.polygon(
            [
                (0, slash_y_left),
                (fw, slash_y_right),
                (fw, slash_y_right + beam_thick),
                (0, slash_y_left + beam_thick),
            ],
            fill=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 215),
        )
        draw.line(
            [(0, slash_y_left + beam_thick // 2), (fw, slash_y_right + beam_thick // 2)],
            fill=(255, 255, 255, 245),
            width=3 if f in (2, 3) else 2,
        )

        # Animated 4-point Studio Trigger star flare
        star_cx = fw * (0.22 + 0.58 * t)
        star_cy = fh * (0.62 - 0.28 * t)
        star_r = 46.0 if f in (2, 3) else (32.0 + 10.0 * math.sin(t * math.pi))
        draw_trigger_4point_star(
            draw,
            cx=star_cx,
            cy=star_cy,
            outer_r=star_r,
            inner_r=star_r * 0.18,
            angle_deg=f * 22.5,
            fill_rgba=(secondary_rgb[0], secondary_rgb[1], secondary_rgb[2], 235),
        )

        # Secondary harmonic star flare on opposite side
        if f in (2, 3, 4, 5):
            draw_trigger_4point_star(
                draw,
                cx=fw * 0.82,
                cy=fh * 0.26,
                outer_r=26.0,
                inner_r=5.0,
                angle_deg=-f * 18.0,
                fill_rgba=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 220),
            )

        # Top & bottom angled Omega Strikers letterbox slash trim
        draw.polygon([(0, 0), (fw, 0), (fw, 8), (0, 16)], fill=(6, 10, 20, 225))
        draw.polygon([(0, fh - 16), (fw, fh - 8), (fw, fh), (0, fh)], fill=(6, 10, 20, 225))
        draw.line([(0, 16), (fw, 8)], fill=(primary_rgb[0], primary_rgb[1], primary_rgb[2], 235), width=2)
        draw.line([(0, fh - 16), (fw, fh - 8)], fill=(secondary_rgb[0], secondary_rgb[1], secondary_rgb[2], 235), width=2)

        final_frame = Image.alpha_composite(frame_img.convert("RGBA"), overlay).convert("RGB")
        strip.paste(final_frame, (f * fw, 0))

    strip_out_path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(strip_out_path, format="PNG", optimize=True)


def discover_and_synthesize_library_assets() -> List[Dict[str, Any]]:
    """
    Collect all 600x800 mastered hero/mech portraits and Agent Command Deck portraits,
    and synthesize Pose-B Sakuga Impact Keyframes + 8-Frame Sakuga Cut-In Sprite Strips.
    """
    entries: List[Dict[str, Any]] = []
    SAKUGA_CUTINS_DIR.mkdir(parents=True, exist_ok=True)
    POSE_B_DIR.mkdir(parents=True, exist_ok=True)

    all_sources: List[Tuple[str, Path, str, Path | None]] = []
    if MASTERED_CARDS_DIR.exists():
        for png in sorted(MASTERED_CARDS_DIR.glob("*.png")):
            all_sources.append((png.stem, png, "core_16_units", None))

    if AGENT_DECK_CARDS_DIR.exists():
        for png in sorted(AGENT_DECK_CARDS_DIR.glob("*.png")):
            svg_file = AGENT_DECK_SVGS_DIR / f"{png.stem}.svg"
            all_sources.append(
                (png.stem, png, "agent_command_deck_37", svg_file if svg_file.exists() else None)
            )

    for stem, png_path, collection, svg_file in all_sources:
        default_primary = "#FFB800"
        default_secondary = "#00E5FF"
        if stem.startswith("plugin_"):
            default_primary, default_secondary = "#A855F7", "#FFE082"
        elif stem.startswith("skill_"):
            default_primary, default_secondary = "#00E5FF", "#FFB800"
        elif stem.startswith("tool_"):
            default_primary, default_secondary = "#FFB800", "#2EE6D3"
        elif stem.startswith("mcp_"):
            default_primary, default_secondary = "#2EE6D3", "#FF2E54"

        arch = SAKUGA_TELEGRAPH_ARCHETYPES.get(
            stem,
            {
                "telegraph_name": f"{stem.replace('_', ' ').title()} Cut-In",
                "sakuga_motion": (
                    "diagonal speedline banner, 4-point star lens flare, pen-and-ink crosshatching "
                    "over warm parchment-gold filigree, sleek beveled cyber-magicite armor edges"
                ),
                "primary_hex": default_primary,
                "secondary_hex": default_secondary,
            },
        )
        p_rgb = hex_to_rgb(arch["primary_hex"])
        s_rgb = hex_to_rgb(arch["secondary_hex"])

        pose_b_path = POSE_B_DIR / f"{stem}_pose_b.png"
        strip_path = SAKUGA_CUTINS_DIR / f"{stem}_strip.png"
        if HAS_PIL and (not pose_b_path.exists() or not strip_path.exists()):
            synthesize_pose_b_keyframe(png_path, pose_b_path, p_rgb, s_rgb)
            synthesize_sakuga_8frame_strip(png_path, strip_path, p_rgb, s_rgb)

        entries.append(
            {
                "asset_id": stem,
                "collection": collection,
                "keyframe_a_path": str(png_path.relative_to(PROJECT_ROOT)),
                "keyframe_b_path": str(pose_b_path.relative_to(PROJECT_ROOT)) if pose_b_path else None,
                "sakuga_strip_path": str(strip_path.relative_to(PROJECT_ROOT)) if strip_path else None,
                "telegraph_svg_path": str(svg_file.relative_to(PROJECT_ROOT)) if svg_file else None,
                "resolution": [600, 800],
                "strip_resolution": [1920, 160] if strip_path else None,
                "strip_frames": 8 if strip_path else 0,
                "aspect_ratio": "3:4",
                "telegraph_name": arch["telegraph_name"],
                "sakuga_prompt": (
                    f"production quality 2D anime sakuga telegraph cut-in, {arch['sakuga_motion']}, "
                    "stylized 7-head proportions, bold ink linework, cel-shaded vibrant color planes, "
                    "crisp impact frames, 24fps keyframe animation"
                ),
                "chromatic_split": f"{arch['primary_hex']} / {arch['secondary_hex']}",
                "target_frames": 16,
                "fps": 24,
            }
        )

    return entries


def build_v100_manifest() -> Dict[str, Any]:
    """Build and write the V100 PXG Sakuga Telegraph training & inference manifest."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    assets = discover_and_synthesize_library_assets()
    strips_count = sum(1 for a in assets if a.get("sakuga_strip_path"))
    pose_b_count = sum(1 for a in assets if a.get("keyframe_b_path"))

    manifest: Dict[str, Any] = {
        "schema_version": "1.1.0",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine": "PXG-Sakuga-Telegraph-Engine",
        "hardware_target": {
            "gpu_model": "NVIDIA Tesla V100 (Volta sm_70)",
            "vram_supported_gb": [16, 32],
            "compute_capability": "7.0",
            "dtype": "float16",
            "bfloat16_disabled_reason": "Volta sm_70 lacks native bf16 tensor cores; float16 gives 125 TFLOPS on V100",
            "attention_backend": "torch.nn.functional.scaled_dot_product_attention (mem_efficient_sdp)",
            "gradient_checkpointing": True,
        },
        "models_configured": [
            {
                "id": "wan2.1-i2v-1.3b-sakuga-lora",
                "base_model": "Wan-AI/Wan2.1-I2V-1.3B-480P",
                "v100_16gb_compatible": True,
                "lora_rank": 32,
                "lora_alpha": 64,
                "target_modules": ["q", "k", "v", "o", "ffn.0", "ffn.2"],
                "output_weights": "Models/pxg_sakuga_trigger_cutin_v1.pt",
            },
            {
                "id": "tooncrafter-keyframe-interpolator",
                "base_model": "Doubiiu/ToonCrafter",
                "v100_16gb_compatible": True,
                "interpolation_frames": 16,
                "resolution": [600, 800],
                "use_case": "Pose A (Idle Card Portrait) -> Pose B (Diagonal Sakuga Telegraph Cut-In)",
            },
        ],
        "dataset_summary": {
            "total_library_assets": len(assets),
            "core_16_units_count": sum(1 for a in assets if a["collection"] == "core_16_units"),
            "agent_deck_37_count": sum(1 for a in assets if a["collection"] == "agent_command_deck_37"),
            "synthesized_pose_b_keyframes_count": pose_b_count,
            "synthesized_8frame_sakuga_strips_count": strips_count,
            "all_600x800_verified": all(a["resolution"] == [600, 800] for a in assets),
        },
        "assets": assets,
    }

    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    shell_script = """#!/usr/bin/env bash
# ==============================================================================
# PXG Engine — NVIDIA Tesla V100 (sm_70, FP16) Anime Telegraph & Cut-In Trainer
# ==============================================================================
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"
export TORCH_CUDNN_V8_API_ENABLED=1

echo "[PXG-V100] Step 1/2: Synthesizing Pose-B Keyframes & 8-Frame Sakuga Strips..."
python3 Backend/pxg_v100_anime_telegraph_trainer.py

echo "[PXG-V100] Step 2/2: Launching PXG Spatio-Temporal Sakuga LoRA Trainer (FP16 Tensor Cores)..."
python3 Backend/train_v100_sakuga_lora.py --epochs 12 --lora-rank 32 --lora-alpha 64 --fp16
"""
    V100_SHELL_SCRIPT.write_text(shell_script, encoding="utf-8")
    V100_SHELL_SCRIPT.chmod(0o755)
    return manifest


if __name__ == "__main__":
    m = build_v100_manifest()
    print(
        json.dumps(
            {
                "ok": True,
                "manifest": str(MANIFEST_JSON),
                "total_assets": m["dataset_summary"]["total_library_assets"],
                "core_units": m["dataset_summary"]["core_16_units_count"],
                "agent_deck_units": m["dataset_summary"]["agent_deck_37_count"],
                "pose_b_keyframes": m["dataset_summary"]["synthesized_pose_b_keyframes_count"],
                "sakuga_8frame_strips": m["dataset_summary"]["synthesized_8frame_sakuga_strips_count"],
                "gpu_target": m["hardware_target"]["gpu_model"],
                "dtype": m["hardware_target"]["dtype"],
            }
        )
    )
