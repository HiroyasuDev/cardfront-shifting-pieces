#!/usr/bin/env python3
"""
Backend/render_cf_app_icons.py
==============================
Renders `WebPlayable/GeneratedArt/Icons/cf_app_icon_master.svg` into crisp,
4x-supersampled opaque RGB PNG app icons for CARDFRONT 3D: Cradle of Echoes:
  1. `WebPlayable/GeneratedArt/Icons/cf_app_icon_512.png` (512x512, RGB)
  2. `WebPlayable/GeneratedArt/Icons/cf_app_icon_192.png` (192x192, RGB)
  3. `Assets/Resources/UI/Icons/cf_app_icon_512.png` (512x512, RGB)
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT_DIR = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT_DIR / "WebPlayable" / "GeneratedArt" / "Icons" / "cf_app_icon_master.svg"
OUT_512_WEB = ROOT_DIR / "WebPlayable" / "GeneratedArt" / "Icons" / "cf_app_icon_512.png"
OUT_192_WEB = ROOT_DIR / "WebPlayable" / "GeneratedArt" / "Icons" / "cf_app_icon_192.png"
OUT_512_UNITY = ROOT_DIR / "Assets" / "Resources" / "UI" / "Icons" / "cf_app_icon_512.png"


def render_master_crest_2048() -> Image.Image:
    """Renders the 512x512 master SVG geometry at 2048x2048 (4x SSAA) for crisp downsampling."""
    S = 4  # 4x supersampling factor (512 * 4 = 2048)
    W = 512 * S
    img = Image.new("RGBA", (W, W), (11, 16, 33, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    def sc(pts):
        return [(x * S, y * S) for (x, y) in pts]

    # 0. Full-bleed background gradient + corner geometric bevels
    for y in range(W):
        t = y / (W - 1)
        r = int(19 * (1 - t) + 5 * t)
        g = int(27 * (1 - t) + 8 * t)
        b = int(51 * (1 - t) + 17 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    draw.polygon(sc([(0, 0), (96, 0), (0, 96)]), fill=(30, 41, 59, 180))
    draw.polygon(sc([(512, 0), (416, 0), (512, 96)]), fill=(30, 41, 59, 180))
    draw.polygon(sc([(0, 512), (96, 512), (0, 416)]), fill=(30, 41, 59, 180))
    draw.polygon(sc([(512, 512), (416, 512), (512, 416)]), fill=(30, 41, 59, 180))
    draw.rounded_rectangle([4 * S, 4 * S, 508 * S, 508 * S], radius=110 * S, outline=(255, 184, 0, 145), width=4 * S)

    # 1. Obsidian-Cobalt Squircle Shield
    draw.rounded_rectangle(
        [18 * S, 18 * S, 494 * S, 494 * S],
        radius=102 * S,
        fill=(217, 138, 22, 255),
        outline=(255, 246, 194, 255),
        width=4 * S,
    )
    draw.rounded_rectangle(
        [30 * S, 30 * S, 482 * S, 482 * S],
        radius=92 * S,
        fill=(17, 25, 46, 255),
        outline=(92, 50, 3, 255),
        width=4 * S,
    )
    draw.rounded_rectangle(
        [42 * S, 42 * S, 470 * S, 470 * S],
        radius=82 * S,
        fill=(13, 21, 43, 255),
        outline=(255, 184, 0, 255),
        width=5 * S,
    )
    draw.rounded_rectangle(
        [56 * S, 56 * S, 456 * S, 456 * S],
        radius=70 * S,
        outline=(255, 184, 0, 105),
        width=2 * S,
    )

    # Corner Ivalice Filigree Brackets
    bracket_color = (255, 184, 0, 255)
    draw.line(sc([(64, 132), (64, 68), (132, 68)]), fill=bracket_color, width=8 * S)
    draw.line(sc([(448, 132), (448, 68), (380, 68)]), fill=bracket_color, width=8 * S)
    draw.line(sc([(64, 380), (64, 444), (132, 444)]), fill=bracket_color, width=8 * S)
    draw.line(sc([(448, 380), (448, 444), (380, 444)]), fill=bracket_color, width=8 * S)

    # 4 Corner Magicite Jewels
    draw.polygon(sc([(88, 68), (106, 88), (88, 108), (70, 88)]), fill=(0, 229, 255, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(424, 68), (442, 88), (424, 108), (406, 88)]), fill=(168, 85, 247, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(88, 404), (106, 424), (88, 444), (70, 424)]), fill=(46, 230, 211, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(424, 404), (442, 424), (424, 444), (406, 424)]), fill=(255, 46, 84, 255), outline=(255, 246, 194, 255), width=3 * S)

    # Radial Clash Aura
    for rad, col in [
        (196, (168, 85, 247, 36)),
        (164, (255, 46, 84, 52)),
        (132, (0, 229, 255, 72)),
        (96, (255, 246, 194, 90)),
    ]:
        draw.ellipse([(256 - rad) * S, (256 - rad) * S, (256 + rad) * S, (256 + rad) * S], fill=col)

    # 2. Gilded Ivalice Law Astrolabe Ring
    for r, col, w in [
        (192, (255, 184, 0, 255), 12),
        (182, (11, 16, 33, 255), 4),
        (172, (217, 138, 22, 230), 5),
        (158, (0, 229, 255, 180), 3),
        (146, (255, 184, 0, 255), 4),
    ]:
        draw.ellipse([(256 - r) * S, (256 - r) * S, (256 + r) * S, (256 + r) * S], outline=col, width=w * S)

    # Astrolabe Degree Ticks
    for deg in range(0, 360, 10):
        rad_a = math.radians(deg)
        r_in = 166 if deg % 30 == 0 else 169
        r_out = 177
        x1 = (256 + r_in * math.cos(rad_a)) * S
        y1 = (256 + r_in * math.sin(rad_a)) * S
        x2 = (256 + r_out * math.cos(rad_a)) * S
        y2 = (256 + r_out * math.sin(rad_a)) * S
        draw.line([(x1, y1), (x2, y2)], fill=(255, 243, 176, 220), width=2 * S)

    # Meridian Crosshairs
    for p1, p2 in [((110, 110), (402, 402)), ((402, 110), (110, 402)), ((64, 256), (448, 256)), ((256, 64), (256, 448))]:
        draw.line(sc([p1, p2]), fill=(255, 184, 0, 135), width=3 * S)

    # Cardinal & Ordinal Astrolabe Spires
    draw.polygon(sc([(256, 42), (274, 82), (256, 98), (238, 82)]), fill=(255, 184, 0, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(256, 470), (274, 430), (256, 414), (238, 430)]), fill=(255, 184, 0, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(42, 256), (82, 238), (98, 256), (82, 274)]), fill=(0, 229, 255, 255), outline=(255, 184, 0, 255), width=3 * S)
    draw.polygon(sc([(470, 256), (430, 238), (414, 256), (430, 274)]), fill=(255, 46, 84, 255), outline=(255, 184, 0, 255), width=3 * S)

    # 3. 3x3 Isometric Tactical Grid Facet (Center Diorama Battlefield)
    draw.polygon(sc([(104, 264), (256, 354), (256, 384), (104, 294)]), fill=(9, 19, 38, 255), outline=(0, 229, 255, 255), width=3 * S)
    draw.polygon(sc([(408, 264), (256, 354), (256, 384), (408, 294)]), fill=(31, 9, 24, 255), outline=(255, 46, 84, 255), width=3 * S)
    draw.polygon(sc([(256, 174), (408, 264), (256, 354), (104, 264)]), fill=(11, 16, 33, 255), outline=(255, 184, 0, 255), width=7 * S)

    cells = [
        ([(256, 186), (300, 212), (256, 238), (212, 212)], (168, 85, 247, 255), (255, 246, 194, 255)),
        ([(300, 212), (344, 238), (300, 264), (256, 238)], (190, 18, 60, 255), (255, 158, 177, 255)),
        ([(344, 238), (388, 264), (344, 290), (300, 264)], (255, 46, 84, 255), (255, 246, 194, 255)),
        ([(212, 212), (256, 238), (212, 264), (168, 238)], (2, 132, 199, 255), (165, 243, 252, 255)),
        ([(256, 238), (300, 264), (256, 290), (212, 264)], (255, 184, 0, 255), (255, 255, 255, 255)),
        ([(300, 264), (344, 290), (300, 316), (256, 290)], (190, 18, 60, 255), (255, 158, 177, 255)),
        ([(168, 238), (212, 264), (168, 290), (124, 264)], (0, 229, 255, 255), (255, 246, 194, 255)),
        ([(212, 264), (256, 290), (212, 316), (168, 290)], (2, 132, 199, 255), (165, 243, 252, 255)),
        ([(256, 290), (300, 316), (256, 342), (212, 316)], (46, 230, 211, 255), (255, 246, 194, 255)),
    ]
    for poly, fill_col, out_col in cells:
        draw.polygon(sc(poly), fill=fill_col, outline=out_col, width=3 * S)

    # 4. Dual Directional Crystalline Lances (Astral Cyan #00E5FF vs Breach Crimson #FF2E54)
    # Breach Crimson Lance
    draw.polygon(sc([(444, 68), (344, 122), (362, 150), (312, 182), (330, 200), (390, 168)]), fill=(159, 18, 57, 255), outline=(255, 184, 0, 255), width=4 * S)
    draw.polygon(sc([(444, 68), (242, 242), (218, 218)]), fill=(255, 46, 84, 255), outline=(255, 246, 194, 255), width=3 * S)
    draw.polygon(sc([(444, 68), (270, 270), (242, 242)]), fill=(159, 18, 57, 255), outline=(255, 184, 0, 255), width=3 * S)
    draw.polygon(sc([(454, 58), (412, 66), (426, 86), (446, 100)]), fill=(255, 184, 0, 255), outline=(255, 246, 194, 255), width=2 * S)

    # Astral Cyan Lance
    draw.polygon(sc([(68, 444), (168, 390), (150, 362), (200, 330), (182, 312), (122, 344)]), fill=(2, 132, 199, 255), outline=(255, 184, 0, 255), width=4 * S)
    draw.polygon(sc([(68, 444), (336, 146), (296, 176), (256, 256)]), fill=(0, 229, 255, 255), outline=(255, 255, 255, 255), width=4 * S)
    draw.polygon(sc([(68, 444), (336, 146), (306, 186), (242, 270)]), fill=(3, 105, 161, 255), outline=(255, 184, 0, 255), width=3 * S)
    draw.polygon(sc([(358, 124), (310, 152), (328, 170)]), fill=(230, 255, 255, 255), outline=(0, 229, 255, 255), width=3 * S)
    draw.polygon(sc([(58, 454), (100, 446), (86, 426), (66, 412)]), fill=(255, 184, 0, 255), outline=(255, 246, 194, 255), width=2 * S)

    # 5. Central Sovereign Clash Nexus & 8-Pointed Singularity Star
    draw.ellipse([(256 - 46) * S, (264 - 46) * S, (256 + 46) * S, (264 + 46) * S], fill=(11, 16, 33, 215), outline=(255, 184, 0, 255), width=5 * S)
    draw.polygon(sc([(256, 196), (272, 226), (256, 218), (240, 226)]), fill=(0, 229, 255, 255), outline=(255, 246, 194, 255), width=2 * S)
    draw.polygon(sc([(324, 264), (294, 280), (302, 264), (294, 248)]), fill=(255, 46, 84, 255), outline=(255, 246, 194, 255), width=2 * S)
    draw.polygon(sc([(256, 332), (272, 302), (256, 310), (240, 302)]), fill=(46, 230, 211, 255), outline=(255, 246, 194, 255), width=2 * S)
    draw.polygon(sc([(188, 264), (218, 280), (210, 264), (218, 248)]), fill=(0, 229, 255, 255), outline=(255, 246, 194, 255), width=2 * S)

    draw.polygon(
        sc([(256, 210), (268, 252), (310, 264), (268, 276), (256, 318), (244, 276), (202, 264), (244, 252)]),
        fill=(255, 184, 0, 255),
        outline=(255, 255, 255, 255),
        width=3 * S,
    )
    draw.polygon(
        sc([(256, 232), (266, 256), (290, 264), (266, 272), (256, 296), (246, 272), (222, 264), (246, 256)]),
        fill=(0, 229, 255, 255),
    )
    draw.ellipse([(256 - 10) * S, (264 - 10) * S, (256 + 10) * S, (264 + 10) * S], fill=(255, 246, 194, 255), outline=(255, 184, 0, 255), width=3 * S)

    return img.convert("RGB")


def verify_png(path: Path, expected_size: tuple[int, int]) -> dict:
    with Image.open(path) as im:
        w, h = im.size
        mode = im.mode
        stat = ImageStat.Stat(im.convert("L"))
        rms_contrast = round(stat.stddev[0] / 255.0, 4)
        bg = Image.new("RGB", im.size, im.convert("RGB").getpixel((0, 0)))
        diff = ImageChops.difference(im.convert("RGB"), bg)
        bbox = list(diff.getbbox() or (0, 0, w, h))
    return {
        "path": str(path),
        "size": [w, h],
        "expected_size": list(expected_size),
        "mode": mode,
        "rms_contrast": rms_contrast,
        "content_bounds": bbox,
        "valid": (w, h) == expected_size and mode in ("RGB", "RGBA") and rms_contrast >= 0.18,
    }


def main() -> None:
    OUT_512_WEB.parent.mkdir(parents=True, exist_ok=True)
    OUT_512_UNITY.parent.mkdir(parents=True, exist_ok=True)

    master_2048 = render_master_crest_2048()
    icon_512 = master_2048.resize((512, 512), Image.Resampling.LANCZOS)
    icon_192 = master_2048.resize((192, 192), Image.Resampling.LANCZOS)

    icon_512.save(OUT_512_WEB, format="PNG", optimize=True)
    icon_192.save(OUT_192_WEB, format="PNG", optimize=True)
    shutil.copy2(OUT_512_WEB, OUT_512_UNITY)

    report = {
        "svg_master": str(SVG_PATH),
        "svg_bytes": SVG_PATH.stat().st_size if SVG_PATH.exists() else 0,
        "icons": [
            verify_png(OUT_512_WEB, (512, 512)),
            verify_png(OUT_192_WEB, (192, 192)),
            verify_png(OUT_512_UNITY, (512, 512)),
        ],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
