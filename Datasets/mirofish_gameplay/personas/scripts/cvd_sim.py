#!/usr/bin/env python3
"""Deuteranopia simulation + objective colour-pair distinguishability for the persona swarm.

1. Applies the Machado, Oliveira & Fernandes (2009) deuteranopia matrix (severity 1.0, linear RGB)
   to every screenshot of the colourblind persona (p08) -> *_deutan.jpg and a side-by-side *_compare.jpg.
2. Computes CIEDE2000 distances between the game's semantic colour pairs (taken from the CSS
   variables / inline colours of the game file) under normal vision and simulated deuteranopia.

Output: raw/cvd_color_pairs.json (+ images in screenshots/p08_*/).
"""
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M_DEUT = np.array([[0.367322, 0.860646, -0.227968],
                   [0.280085, 0.672501, 0.047413],
                   [-0.011820, 0.042940, 0.968881]])


def srgb_to_lin(x):
    x = x / 255.0
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055) * 255.0


def simulate(rgb):
    arr = np.asarray(rgb, dtype=np.float64)
    lin = srgb_to_lin(arr)
    out = lin @ M_DEUT.T
    return lin_to_srgb(out)


def rgb_to_lab(rgb):
    lin = srgb_to_lin(np.asarray(rgb, dtype=np.float64))
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def ciede2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dhp = h2p - h1p
    if C1p * C2p == 0:
        dhp = 0
    elif dhp > 180:
        dhp -= 360
    elif dhp < -180:
        dhp += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if (h1p + h2p) < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dtheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dtheta)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


# Semantic pairs that carry gameplay meaning (source: game CSS vars lines 12-17, flip/defend
# telegraph line colours in buildBoardTelegraphOverlaySVG, turn badge colours in renderAll).
PAIRS = {
    "player_frame_vs_ai_frame (--blue-ally vs --red-enemy)": ("#00E5FF", "#FF2E54"),
    "flip_preview_vs_defend_preview line (#FFB800 vs #FF2E54)": ("#FFB800", "#FF2E54"),
    "turn_badge YOUR TURN vs BOSS TURN (#FFB800 vs #FF2E54)": ("#FFB800", "#FF2E54"),
    "slide_target (--emerald) vs flip_target (--gold)": ("#00E676", "#FFB800"),
    "slide_target (--emerald) vs ai_frame (--red-enemy)": ("#00E676", "#FF2E54"),
    "victory_title vs defeat_title (#00E5FF vs #FF2E54)": ("#00E5FF", "#FF2E54"),
}


def main():
    res = {"method": "Machado2009 deuteranopia severity=1.0 (linear sRGB); CIEDE2000", "pairs": {}}
    for name, (a, b) in PAIRS.items():
        ra, rb = hexrgb(a), hexrgb(b)
        sa, sb = simulate(ra), simulate(rb)
        d_norm = ciede2000(rgb_to_lab(ra), rgb_to_lab(rb))
        d_deut = ciede2000(rgb_to_lab(sa), rgb_to_lab(sb))
        res["pairs"][name] = {
            "a": a, "b": b,
            "a_deutan": "#%02X%02X%02X" % tuple(int(round(v)) for v in sa),
            "b_deutan": "#%02X%02X%02X" % tuple(int(round(v)) for v in sb),
            "dE2000_normal": round(d_norm, 2), "dE2000_deutan": round(d_deut, 2),
            "retained_pct": round(100 * d_deut / d_norm, 1),
        }
    shots = sorted(glob.glob(os.path.join(ROOT, "screenshots", "p08_*", "*.jpg")))
    shots = [s for s in shots if not s.endswith(("_deutan.jpg", "_compare.jpg"))]
    made = []
    for s in shots:
        im = Image.open(s).convert("RGB")
        sim = Image.fromarray(simulate(np.asarray(im)).round().astype(np.uint8))
        out = s.replace(".jpg", "_deutan.jpg")
        sim.save(out, quality=72)
        cmp_ = Image.new("RGB", (im.width * 2, im.height))
        cmp_.paste(im, (0, 0))
        cmp_.paste(sim, (im.width, 0))
        cmp_ = cmp_.resize((im.width, im.height // 2))
        cmp_.save(s.replace(".jpg", "_compare.jpg"), quality=72)
        made.append(os.path.relpath(out, ROOT))
    res["deutan_screenshots"] = made
    with open(os.path.join(ROOT, "raw", "cvd_color_pairs.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res["pairs"], indent=2))
    print(f"{len(made)} deuteranopia screenshots written")


if __name__ == "__main__":
    sys.exit(main())
