#!/usr/bin/env python3
"""
generate_set1_60_unique_portraits.py
====================================
Generates 44 distinct, faction-styled 600x800 RGB opaque card portraits for
Set 1 cards 17..60 (`set1_c17` through `set1_c60`) so that all 60 cards in
`SET1_60_CATALOG` have 100% unique visual and cryptographic artwork.

Technical & Atelier Art Direction Lock:
- Resolution: 600x800 (3:4 portrait, RGB, opaque, content_bounds = [0, 0, 600, 800])
- Zero baked raster text on any card portrait
- Faction Chromatic Discipline:
  * Aether:   Tarot Violet (#A855F7) & Gilded Parchment (#FFE082)
  * Solaris:  Ivalice Law Gold (#FFB800) & Jade-Teal (#2EE6D3)
  * Valkyria: Astral Cyan (#00E5FF) & Cobalt-Gold (#38BDF8)
  * Chronos:  Amber-Bronze (#F97316) & Solar Brass (#FBBF24)
  * Abyss:    Crimson-Obsidian (#FF2E54) & Void Amethyst (#C026D3)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
MASTERED_DIR = PROJECT_ROOT / "GeneratedArt" / "MasteredCards"
WEB_GEN_ART_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt"
WEB_MASTERED_DIR = WEB_GEN_ART_DIR / "MasteredCards"
MANIFEST_OUT_PATH = PROJECT_ROOT / "Datasets" / "set1_60_unique_portraits_manifest.json"

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

FACTION_PALETTES: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "Aether": {
        "primary": (168, 85, 247),    # #A855F7 Tarot Violet
        "secondary": (255, 224, 130), # #FFE082 Gilded Parchment
        "shadow": (28, 12, 54),
    },
    "Solaris": {
        "primary": (255, 184, 0),     # #FFB800 Ivalice Law Gold
        "secondary": (46, 230, 211),  # #2EE6D3 Jade-Teal
        "shadow": (42, 24, 6),
    },
    "Valkyria": {
        "primary": (0, 229, 255),     # #00E5FF Astral Cyan
        "secondary": (255, 200, 87),  # Cobalt-Gold highlight
        "shadow": (8, 28, 52),
    },
    "Chronos": {
        "primary": (249, 115, 22),    # #F97316 Amber-Bronze
        "secondary": (251, 191, 36),  # #FBBF24 Solar Brass
        "shadow": (44, 18, 8),
    },
    "Abyss": {
        "primary": (255, 46, 84),     # #FF2E54 Crimson-Obsidian
        "secondary": (192, 38, 211),  # Void Amethyst
        "shadow": (36, 6, 18),
    },
}


def apply_faction_grade_and_pose(
    base_img: Image.Image,
    card_index: int,
    faction: str,
    tier: int,
) -> Image.Image:
    """
    Applies deterministic Mk.2 / Mk.3 / Mk.4 composition framing, horizontal mirror
    on odd tiers (`tier == 3`), and faction color-grading with radial aura lighting.
    """
    w, h = 600, 800
    img = base_img.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)

    # Mirror horizontally on odd tiers (tier == 3) so silhouettes vary across tiers
    if tier == 3:
        img = ImageOps.mirror(img)

    # Subtle deterministic scale & focal pan per card_index and tier
    zoom = 1.02 + 0.022 * (tier - 1) + 0.004 * (card_index % 5)
    zw, zh = int(round(w * zoom)), int(round(h * zoom))
    img_zoomed = img.resize((zw, zh), Image.Resampling.LANCZOS)

    pan_x_ratio = ((card_index * 37) % 100) / 100.0
    pan_y_ratio = ((card_index * 53) % 100) / 100.0
    left = int(round((zw - w) * pan_x_ratio))
    top = int(round((zh - h) * pan_y_ratio))
    img = img_zoomed.crop((left, top, left + w, top + h))

    # Contrast and color adjustments tailored to tier (Mk.2, Mk.3, Mk.4)
    contrast_factor = 1.06 + 0.04 * (tier - 2) + 0.01 * (card_index % 3)
    sat_factor = 1.08 + 0.05 * (tier - 2)
    bright_factor = 1.01 + (0.02 if tier == 2 else (-0.01 if tier == 3 else 0.03))

    img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    img = ImageEnhance.Color(img).enhance(sat_factor)
    img = ImageEnhance.Brightness(img).enhance(bright_factor)

    # Numpy chromatic grading & split-tone radial aura
    arr = np.asarray(img, dtype=np.float32) / 255.0
    pal = FACTION_PALETTES[faction]
    prim = np.array(pal["primary"], dtype=np.float32) / 255.0
    sec = np.array(pal["secondary"], dtype=np.float32) / 255.0
    shd = np.array(pal["shadow"], dtype=np.float32) / 255.0

    # Compute luminance for split-toning (shadows -> faction shadow, highlights -> faction primary/secondary)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    lum_3d = lum[:, :, np.newaxis]

    # Coordinate grid for radial halo & diagonal gradient
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = w * (0.50 + 0.08 * math.sin(card_index * 0.9))
    cy = h * (0.36 + 0.06 * math.cos(card_index * 0.7))
    dist = np.sqrt(((xx - cx) / (w * 0.55)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2)
    radial_glow = np.clip(1.0 - dist, 0.0, 1.0) ** (1.6 + 0.2 * (tier - 2))
    vignette = np.clip((dist - 0.55) / 0.85, 0.0, 1.0) ** 1.5

    # Diagonal wave modulation unique to card_index
    angle = (card_index * 29) * math.pi / 180.0
    diag = (xx * math.cos(angle) + yy * math.sin(angle)) / float(w + h)
    shimmer = 0.5 + 0.5 * np.sin(diag * (6.0 + tier * 2.0) + card_index)

    tint_strength = 0.16 + 0.03 * (tier - 2)
    tone_color = (
        prim[np.newaxis, np.newaxis, :] * (0.65 + 0.35 * shimmer[:, :, np.newaxis])
        + sec[np.newaxis, np.newaxis, :] * (0.35 * (1.0 - shimmer[:, :, np.newaxis]))
    )

    # Blend split-tone highlights + radial aura + shadow vignette
    graded = arr * (1.0 - tint_strength) + tone_color * (tint_strength * (0.35 + 0.65 * lum_3d))
    graded += prim[np.newaxis, np.newaxis, :] * (radial_glow[:, :, np.newaxis] * (0.11 + 0.03 * (tier - 2)))
    graded = graded * (1.0 - 0.28 * vignette[:, :, np.newaxis]) + shd[np.newaxis, np.newaxis, :] * (
        0.28 * vignette[:, :, np.newaxis]
    )

    graded_u8 = np.clip(graded * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(graded_u8, mode="RGB")


def draw_atelier_filigree_overlay(
    graded_img: Image.Image,
    card_index: int,
    faction: str,
    tier: int,
) -> Image.Image:
    """
    Draws bespoke code-native geometric sacred-halo astrolabes, cyber-magicite energy
    arcs, constellation nodes, and beveled Atelier corner frames with ZERO baked text.
    """
    w, h = graded_img.size
    pal = FACTION_PALETTES[faction]
    prim = pal["primary"]
    sec = pal["secondary"]
    shd = pal["shadow"]

    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    crisp_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer, "RGBA")
    cdraw = ImageDraw.Draw(crisp_layer, "RGBA")

    # 1. Sacred Halo / Astrolabe behind/around upper focal center
    cx = int(w * (0.50 + 0.05 * math.sin(card_index * 1.3)))
    cy = int(h * (0.34 + 0.04 * math.cos(card_index * 1.1)))
    base_r = 128 + (card_index % 7) * 8 + (tier - 2) * 14

    # Outer & inner halo rings
    for ring_idx in range(tier):
        r = base_r + ring_idx * 22
        bbox = [cx - r, cy - r, cx + r, cy + r]
        alpha_glow = 78 - ring_idx * 14
        alpha_crisp = 145 - ring_idx * 20
        gdraw.ellipse(bbox, outline=(*prim, alpha_glow), width=6)
        cdraw.ellipse(bbox, outline=(*sec, alpha_crisp), width=2)

    # Star-polygon / astrolabe geometry inside the sacred halo
    num_points = 4 + (card_index % 5) + tier  # 6 to 12 vertices
    rot_offset = (card_index * 23.5) * math.pi / 180.0
    poly_pts: List[Tuple[float, float]] = []
    inner_pts: List[Tuple[float, float]] = []
    for k in range(num_points):
        theta = rot_offset + (2.0 * math.pi * k) / num_points
        px = cx + math.cos(theta) * base_r
        py = cy + math.sin(theta) * base_r
        poly_pts.append((px, py))

        theta_in = theta + math.pi / num_points
        ix = cx + math.cos(theta_in) * (base_r * 0.58)
        iy = cy + math.sin(theta_in) * (base_r * 0.58)
        inner_pts.append((ix, iy))

        # Radial tick spokes
        tx_out = cx + math.cos(theta) * (base_r + 18)
        ty_out = cy + math.sin(theta) * (base_r + 18)
        cdraw.line([(px, py), (tx_out, ty_out)], fill=(*sec, 140), width=2)
        # Constellation node jewel at vertex
        node_r = 4 + (k % 2) * 2
        gdraw.ellipse([px - node_r * 2, py - node_r * 2, px + node_r * 2, py + node_r * 2], fill=(*prim, 110))
        cdraw.ellipse([px - node_r, py - node_r, px + node_r, py + node_r], fill=(*sec, 210))

    # Connect star-polygon chords (step = 2 or 3)
    step = 2 if num_points <= 7 else 3
    for k in range(num_points):
        p1 = poly_pts[k]
        p2 = poly_pts[(k + step) % num_points]
        gdraw.line([p1, p2], fill=(*prim, 64), width=4)
        cdraw.line([p1, p2], fill=(*sec, 115), width=1)
        cdraw.line([p1, inner_pts[k]], fill=(*prim, 110), width=1)

    # 2. Cyber-Magicite Weapon / Aether Energy Arcs sweeping across the canvas
    num_arcs = 2 + tier
    for a_idx in range(num_arcs):
        phase = card_index * 0.85 + a_idx * 1.4
        arc_pts: List[Tuple[float, float]] = []
        for s in range(28):
            t = s / 27.0
            ax = w * (0.08 + 0.84 * t)
            ay = h * (
                0.22
                + 0.56 * t
                + 0.14 * math.sin(t * math.pi * (1.5 + 0.5 * (a_idx % 3)) + phase)
            )
            if tier == 3:
                ax = w - ax
            arc_pts.append((ax, ay))
        gdraw.line(arc_pts, fill=(*prim, 85), width=7 - (a_idx % 2) * 2)
        cdraw.line(arc_pts, fill=(*sec, 165), width=2)

        # Energy motes along the arc
        for m_idx in range(4, 25, 6):
            mx, my = arc_pts[m_idx]
            mr = 3 + ((card_index + m_idx) % 3)
            gdraw.ellipse([mx - mr * 2, my - mr * 2, mx + mr * 2, my + mr * 2], fill=(*prim, 130))
            cdraw.polygon(
                [(mx, my - mr - 2), (mx + mr + 2, my), (mx, my + mr + 2), (mx - mr - 2, my)],
                fill=(*sec, 220),
            )

    # 3. Ornate Beveled Atelier Frame & Corner Filigree (ensures full-bleed 600x800 bounds)
    # Outer opaque dark-gold/faction bevel border + inner filigree frame
    cdraw.rectangle([0, 0, w - 1, h - 1], outline=(*shd, 255), width=4)
    cdraw.rectangle([3, 3, w - 4, h - 4], outline=(*prim, 220), width=2)
    margin = 14
    corner_cut = 26 + (tier - 2) * 4
    frame_poly = [
        (margin + corner_cut, margin),
        (w - margin - corner_cut, margin),
        (w - margin, margin + corner_cut),
        (w - margin, h - margin - corner_cut),
        (w - margin - corner_cut, h - margin),
        (margin + corner_cut, h - margin),
        (margin, h - margin - corner_cut),
        (margin, margin + corner_cut),
    ]
    gdraw.polygon(frame_poly, outline=(*prim, 110), width=5)
    cdraw.polygon(frame_poly, outline=(*sec, 215), width=2)

    # Corner chevron ornaments
    corners = [
        (margin, margin, 1, 1),
        (w - margin, margin, -1, 1),
        (w - margin, h - margin, -1, -1),
        (margin, h - margin, 1, -1),
    ]
    for bx, by, sx, sy in corners:
        c_pts = [
            (bx, by + sy * (corner_cut + 10)),
            (bx, by),
            (bx + sx * (corner_cut + 10), by),
        ]
        cdraw.line(c_pts, fill=(*sec, 235), width=3)
        # Corner diamond gem
        gx = bx + sx * 12
        gy = by + sy * 12
        cdraw.polygon(
            [(gx, gy - 6), (gx + 6, gy), (gx, gy + 6), (gx - 6, gy)],
            fill=(*prim, 240),
            outline=(*sec, 255),
        )

    # Tier diamond pips along top & bottom filigree rail (2, 3, or 4 geometric diamonds, zero text)
    pip_spacing = 22
    start_x = w // 2 - ((tier - 1) * pip_spacing) // 2
    for p_idx in range(tier):
        px = start_x + p_idx * pip_spacing
        for py in (margin, h - margin):
            gdraw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(*prim, 160))
            cdraw.polygon(
                [(px, py - 7), (px + 7, py), (px, py + 7), (px - 7, py)],
                fill=(*sec, 245),
                outline=(*prim, 255),
            )

    # Blur glow layer and composite over graded portrait
    glow_blurred = glow_layer.filter(ImageFilter.GaussianBlur(radius=4.5))
    comp = graded_img.convert("RGBA")
    comp = Image.alpha_composite(comp, glow_blurred)
    comp = Image.alpha_composite(comp, crisp_layer)
    return comp.convert("RGB")


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


def main() -> None:
    MASTERED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Ensure all 16 base portraits exist
    missing_base = [
        bid for bid in BASE_ROSTER if not (MASTERED_DIR / f"{bid}.png").exists()
    ]
    if missing_base:
        raise FileNotFoundError(f"Missing base portraits in {MASTERED_DIR}: {missing_base}")

    generated_records: List[Dict[str, Any]] = []

    # Generate the 44 unique Set 1 portraits (i = 16..59 -> set1_c17..set1_c60)
    for i in range(16, 60):
        base_id = BASE_ROSTER[i % 16]
        cid = f"set1_c{i + 1:02d}_{base_id}"
        faction = FACTIONS[i % 5]
        tier = (i // 16) + 1  # Mk.2 (2), Mk.3 (3), Mk.4 (4)

        base_path = MASTERED_DIR / f"{base_id}.png"
        out_path = MASTERED_DIR / f"{cid}.png"

        with Image.open(base_path) as base_im:
            graded = apply_faction_grade_and_pose(base_im, card_index=i, faction=faction, tier=tier)
            final_img = draw_atelier_filigree_overlay(graded, card_index=i, faction=faction, tier=tier)
            final_img.save(out_path, format="PNG", optimize=True)

        info = verify_portrait(out_path)
        info.update({
            "catalog_index": i + 1,
            "card_id": cid,
            "base_id": base_id,
            "faction": faction,
            "tier": f"Mk.{tier}",
        })
        generated_records.append(info)

    # Check if WebPlayable/GeneratedArt or WebPlayable/GeneratedArt/MasteredCards is a symlink
    web_sync_mode = "symlink_shared"
    if not os.path.islink(WEB_GEN_ART_DIR) and not os.path.islink(WEB_MASTERED_DIR):
        WEB_MASTERED_DIR.mkdir(parents=True, exist_ok=True)
        if not os.path.samefile(MASTERED_DIR, WEB_MASTERED_DIR):
            web_sync_mode = "copied_directory"
            for rec in generated_records:
                src_file = Path(rec["path"])
                shutil.copy2(src_file, WEB_MASTERED_DIR / src_file.name)

    # Verify all 60 Set 1 portraits (16 base + 44 generated)
    all_60_records: List[Dict[str, Any]] = []
    for idx, base_id in enumerate(BASE_ROSTER):
        p = MASTERED_DIR / f"{base_id}.png"
        rec = verify_portrait(p)
        rec.update({
            "catalog_index": idx + 1,
            "card_id": f"set1_c{idx + 1:02d}_{base_id}",
            "base_id": base_id,
            "faction": FACTIONS[idx % 5],
            "tier": "Mk.1",
        })
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

    manifest = {
        "schema_version": "1.0.0",
        "generator": "Backend/generate_set1_60_unique_portraits.py",
        "total_set1_cards": len(all_60_records),
        "base_portraits_count": len(BASE_ROSTER),
        "generated_unique_portraits_count": len(generated_records),
        "unique_sha256_count": len(unique_hashes),
        "all_60_cryptographically_unique": len(unique_hashes) == 60,
        "all_60_600x800_rgb_opaque_full_bleed": all_valid_dims,
        "web_playable_sync_mode": web_sync_mode,
        "web_playable_accessible_count": web_accessible_count,
        "factions": FACTIONS,
        "base_roster": BASE_ROSTER,
        "portraits": all_60_records,
    }

    MANIFEST_OUT_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"[OK] Generated {len(generated_records)} unique Set 1 portraits (set1_c17..set1_c60).\n"
        f"     Total Set 1 portraits verified: {len(all_60_records)}/60\n"
        f"     Unique SHA-256 hashes:          {len(unique_hashes)}/60\n"
        f"     All 600x800 RGB full-bleed:     {all_valid_dims}\n"
        f"     WebPlayable accessible:         {web_accessible_count}/60 ({web_sync_mode})\n"
        f"     Manifest written to:            {MANIFEST_OUT_PATH}"
    )

    if len(unique_hashes) != 60 or not all_valid_dims or web_accessible_count != 60:
        raise RuntimeError("Validation failed for Set 1 60 unique portraits!")


if __name__ == "__main__":
    main()
