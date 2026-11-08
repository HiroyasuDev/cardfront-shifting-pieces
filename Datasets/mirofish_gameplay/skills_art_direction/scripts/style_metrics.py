#!/usr/bin/env python3
"""Quantitative art-direction style metrics for CARDFRONT card art + stage backgrounds.

Read-only over game art. Writes raw/style_metrics.json, raw/style_metrics.csv,
contact_sheet.png (annotated) into the skills_art_direction folder.

Run: /Users/frederickamina/.local/share/mlx-env/bin/python3 scripts/style_metrics.py
"""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
GAME = ROOT / "WebPlayable/cardfront_cradle_of_echoes_playable.html"
OUT = ROOT / "Datasets/mirofish_gameplay/skills_art_direction"
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(1234)  # deterministic k-means init


# ----------------------------------------------------------------------------- inputs
def discover_assets():
    src = GAME.read_text(encoding="utf-8")
    cards = sorted(set(re.findall(r'art:\s*"\.\./GeneratedArt/MasteredCards/((?:h|e)_[a-z]+)\.png', src)))
    stage_block = src[src.index("const STAGES = ["): src.index("];", src.index("const STAGES = ["))]
    bgs = re.findall(r'bg:\s*"\.\./GeneratedArt/([^"?]+)"', stage_block)
    return cards, bgs


# ----------------------------------------------------------------------------- helpers
def rgb_to_hsv(arr: np.ndarray):
    a = arr.astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1)
    mn = a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rm = m & (mx == r)
    gm = m & (mx == g) & ~rm
    bm = m & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = ((b - r)[gm] / d[gm]) + 2
    h[bm] = ((r - g)[bm] / d[bm]) + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def luminance(arr):
    a = arr.astype(np.float32)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def kmeans(pixels: np.ndarray, k=6, iters=25):
    idx = RNG.choice(len(pixels), size=k, replace=False)
    cent = pixels[idx].astype(np.float32)
    for _ in range(iters):
        d = ((pixels[:, None, :] - cent[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        new = np.array([pixels[lab == i].mean(0) if np.any(lab == i) else cent[i] for i in range(k)])
        if np.allclose(new, cent, atol=0.5):
            break
        cent = new
    share = np.bincount(lab, minlength=k) / len(lab)
    order = np.argsort(-share)
    return [("#%02x%02x%02x" % tuple(int(round(v)) for v in cent[i]), float(share[i])) for i in order]


def sobel_mag(L: np.ndarray):
    p = np.pad(L, 1, mode="edge")
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    return np.hypot(gx, gy)


def otsu(x: np.ndarray):
    hist, edges = np.histogram(x, bins=256)
    w = np.cumsum(hist)
    mu = np.cumsum(hist * edges[:-1])
    wt, mt = w[-1], mu[-1]
    between = (mt * w - mu * wt) ** 2 / np.maximum(w * (wt - w), 1)
    return edges[int(np.argmax(between))]


HUE_BLUE = (180.0, 260.0)  # cyan..blue (game token --blue-ally #00E5FF = 186deg)
HUE_RED_WRAP = (330.0, 25.0)  # magenta-red..red-orange (--red-enemy #FF2E54 = 349deg)


def metrics_for(path: Path, kind: str):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    arr = np.asarray(im)
    small = np.asarray(im.resize((W // 4, H // 4), Image.BILINEAR))
    h, s, v = rgb_to_hsv(arr)
    L = luminance(arr)
    Ln = L / 255.0

    # palette
    pal = kmeans(small.reshape(-1, 3).astype(np.float32), k=6)

    # contrast
    rms_contrast = float(Ln.std())
    p5, p95 = np.percentile(Ln, [5, 95])

    # edges / line weight
    mag = sobel_mag(L)
    edge_density = float((mag > 128).mean())  # strong edges (Sobel units on 0..255 luminance)
    gimg = Image.fromarray(L.astype(np.uint8))
    local = np.asarray(gimg.filter(ImageFilter.BoxBlur(4)), dtype=np.float32)
    line_mask = (L < local - 25) & (L < 110)  # dark ink-like strokes darker than surroundings
    area = line_mask.sum()
    inner = line_mask[1:-1, 1:-1] & line_mask[:-2, 1:-1] & line_mask[2:, 1:-1] & line_mask[1:-1, :-2] & line_mask[1:-1, 2:]
    perim = area - inner.sum()
    line_weight_px = float(2.0 * area / perim) if perim > 0 else 0.0  # mean stroke width estimate
    ink_coverage = float(area / line_mask.size)

    # noise: residual against 3x3 median, measured in low-gradient (flat) regions only
    med = np.asarray(gimg.filter(ImageFilter.MedianFilter(3)), dtype=np.float32)
    resid = np.abs(L - med)
    flat = mag < np.percentile(mag, 40)
    noise = float(np.median(resid[flat]) * 1.4826) if flat.any() else 0.0
    noise_mean = float(resid[flat].mean()) if flat.any() else 0.0

    # framing: subject = pixels that differ from the border colour (5% strip) AND have saliency
    bw = max(4, int(0.05 * min(W, H)))
    border = np.concatenate([arr[:bw].reshape(-1, 3), arr[-bw:].reshape(-1, 3), arr[:, :bw].reshape(-1, 3), arr[:, -bw:].reshape(-1, 3)])
    bmed = np.median(border, 0)
    dist = np.sqrt(((arr.astype(np.float32) - bmed) ** 2).sum(-1))
    sal = 0.6 * dist / (dist.max() + 1e-6) + 0.4 * np.asarray(Image.fromarray(np.clip(mag / 4, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), dtype=np.float32) / 255.0
    sal = np.asarray(Image.fromarray((sal / sal.max() * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)), dtype=np.float32)
    thr = otsu(sal)
    mask = sal > thr
    ys, xs = np.nonzero(mask)
    if len(xs):
        bbox = [float(np.percentile(xs, 5) / W), float(np.percentile(ys, 5) / H), float(np.percentile(xs, 95) / W), float(np.percentile(ys, 95) / H)]
        wts = sal[ys, xs]
        com = [float((xs * wts).sum() / wts.sum() / W), float((ys * wts).sum() / wts.sum() / H)]
    else:
        bbox, com = [0, 0, 1, 1], [0.5, 0.5]
    subject_area = float(mask.mean())
    # key-light proxy: luminance-weighted centroid offset from centre
    yy, xx = np.mgrid[0:H, 0:W]
    lw = Ln ** 2
    light = [float((xx * lw).sum() / lw.sum() / W - 0.5), float((yy * lw).sum() / lw.sum() / H - 0.5)]

    # faction hue
    colourful = (s > 0.35) & (v > 0.25)
    hh = h[colourful]
    blue_share = float(((hh >= HUE_BLUE[0]) & (hh <= HUE_BLUE[1])).sum() / max(1, colourful.sum()))
    red_share = float(((hh >= HUE_RED_WRAP[0]) | (hh <= HUE_RED_WRAP[1])).sum() / max(1, colourful.sum()))
    warm_share = float((((hh >= 0) & (hh < 70)) | (hh >= 330)).sum() / max(1, colourful.sum()))
    wts = (s * v)[colourful]
    ang = np.deg2rad(hh)
    dom_hue = float((np.rad2deg(math.atan2((np.sin(ang) * wts).sum(), (np.cos(ang) * wts).sum())) + 360) % 360) if len(hh) else 0.0
    hue_hist = np.histogram(hh, bins=12, range=(0, 360), weights=wts)[0]
    hue_hist = (hue_hist / max(hue_hist.sum(), 1e-6)).round(4).tolist()

    # in-game zones (card only): art under edge gems & under bottom vignette/ribbon, as rendered with
    # object-fit:cover; object-position:center 12% (slot aspect 0.76 ~= art 0.75 so crop is ~1%)
    zones = {}
    if kind == "card":
        def zone_l(x0, y0, x1, y1):
            z = Ln[int(y0 * H): int(y1 * H), int(x0 * W): int(x1 * W)]
            return float(z.mean()), float(z.std())
        zones = {
            "top_gem": zone_l(0.40, 0.0, 0.60, 0.15),
            "left_gem": zone_l(0.0, 0.38, 0.17, 0.52),
            "right_gem": zone_l(0.83, 0.38, 1.0, 0.52),
            "face_band_top35": zone_l(0.2, 0.0, 0.8, 0.35),
        }

    return {
        "file": str(path.relative_to(ROOT)),
        "kind": kind,
        "width": W,
        "height": H,
        "aspect": round(W / H, 4),
        "palette_top6": pal,
        "mean_saturation": float(s.mean()),
        "mean_value": float(v.mean()),
        "mean_luminance": float(Ln.mean()),
        "rms_contrast": rms_contrast,
        "lum_p5": float(p5),
        "lum_p95": float(p95),
        "edge_density": edge_density,
        "line_weight_px": line_weight_px,
        "ink_coverage": ink_coverage,
        "noise_sigma": noise,
        "noise_mean_abs": noise_mean,
        "subject_bbox": bbox,
        "subject_com": com,
        "subject_area": subject_area,
        "key_light_offset": light,
        "blue_share": blue_share,
        "red_share": red_share,
        "warm_share": warm_share,
        "dominant_hue_deg": dom_hue,
        "hue_hist12": hue_hist,
        "zones": zones,
    }


Z_KEYS = ["mean_saturation", "mean_value", "rms_contrast", "edge_density", "line_weight_px", "noise_sigma",
          "subject_area", "com_y", "blue_minus_red"]


def zscores(rows):
    for r in rows:
        r["com_y"] = r["subject_com"][1]
        r["blue_minus_red"] = r["blue_share"] - r["red_share"]
    out = {}
    for k in Z_KEYS:
        vals = np.array([r[k] for r in rows], dtype=float)
        mu, sd = vals.mean(), vals.std(ddof=0)
        out[k] = {"mean": float(mu), "std": float(sd), "min": float(vals.min()), "max": float(vals.max())}
        for r in rows:
            r.setdefault("z", {})[k] = float((r[k] - mu) / sd) if sd > 1e-9 else 0.0
    for r in rows:
        r["outlier_flags"] = [k for k, z in r["z"].items() if abs(z) >= 2.0 and k != "blue_minus_red"]
        r["watch_flags"] = [k for k, z in r["z"].items() if 1.5 <= abs(z) < 2.0 and k != "blue_minus_red"]
    return out


def faction_analysis(cards):
    heroes = [c for c in cards if Path(c["file"]).name.startswith("h_")]
    enemies = [c for c in cards if Path(c["file"]).name.startswith("e_")]
    hb = np.array([c["blue_share"] for c in heroes]); hr = np.array([c["red_share"] for c in heroes])
    eb = np.array([c["blue_share"] for c in enemies]); er = np.array([c["red_share"] for c in enemies])
    # naive classifier: predict hero iff blue_share > red_share
    correct = sum(c["blue_share"] > c["red_share"] for c in heroes) + sum(c["red_share"] >= c["blue_share"] for c in enemies)
    # separation statistic on (blue-red): Cohen's d between groups
    dh = hb - hr; de = eb - er
    pooled = math.sqrt((dh.var(ddof=1) + de.var(ddof=1)) / 2)
    d = float((dh.mean() - de.mean()) / pooled) if pooled > 0 else 0.0
    return {
        "hero_mean_blue_share": float(hb.mean()), "hero_mean_red_share": float(hr.mean()),
        "enemy_mean_blue_share": float(eb.mean()), "enemy_mean_red_share": float(er.mean()),
        "hero_mean_warm_share": float(np.mean([c["warm_share"] for c in heroes])),
        "enemy_mean_warm_share": float(np.mean([c["warm_share"] for c in enemies])),
        "blue_vs_red_classifier_accuracy": correct / len(cards),
        "cohens_d_blue_minus_red_hero_vs_enemy": d,
        "heroes_not_blue_dominant": [Path(c["file"]).stem for c in heroes if c["blue_share"] <= c["red_share"]],
        "enemies_blue_dominant": [Path(c["file"]).stem for c in enemies if c["blue_share"] > c["red_share"]],
    }


# ----------------------------------------------------------------------------- verdicts
def verdict(r, faction):
    name = Path(r["file"]).stem
    reasons = []
    hero = name.startswith("h_")
    if r["outlier_flags"]:
        reasons.append("style outlier (|z|>=2): " + ", ".join(r["outlier_flags"]))
    if hero and r["blue_share"] <= r["red_share"]:
        reasons.append(f"hero reads warm/red (blue {r['blue_share']:.2f} <= red {r['red_share']:.2f}) - clashes with --red-enemy border")
    if (not hero) and r["blue_share"] > r["red_share"]:
        reasons.append(f"enemy reads blue/cyan (blue {r['blue_share']:.2f} > red {r['red_share']:.2f}) - clashes with --blue-ally border")
    if r["mean_saturation"] > 0.80:
        reasons.append(f"saturation {r['mean_saturation']:.2f} above 0.80 band ceiling")
    if r["noise_sigma"] > 6.0:
        reasons.append(f"noise sigma {r['noise_sigma']:.1f} > 6.0")
    if r["subject_com"][1] > 0.62:
        reasons.append(f"subject centre-of-mass y={r['subject_com'][1]:.2f} sits in the bottom vignette/ribbon zone")
    structural = [x for x in r["outlier_flags"] if x in ("subject_area", "com_y", "edge_density", "line_weight_px")]
    faction_wrong = (hero and r["blue_share"] <= r["red_share"]) or ((not hero) and r["blue_share"] > r["red_share"])
    strongly_wrong = faction_wrong and abs(r["blue_share"] - r["red_share"]) > 0.25
    if structural or strongly_wrong:
        v = "regenerate"
    elif reasons:
        v = "re-grade"
    else:
        v = "keep"
    return v, reasons


# ----------------------------------------------------------------------------- contact sheet
def font(sz):
    for p in ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNSMono.ttf", "/Library/Fonts/Arial.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def contact_sheet(cards, bgs, path: Path):
    CW, CH = 240, 320
    PADX, TXT = 14, 150
    cols = 8
    rows_cards = math.ceil(len(cards) / cols)
    bgW, bgH = 400, 300
    sheetW = cols * (CW + PADX) + PADX
    sheetH = 60 + rows_cards * (CH + TXT + 20) + bgH + TXT + 60
    sheet = Image.new("RGB", (sheetW, sheetH), (14, 17, 26))
    d = ImageDraw.Draw(sheet)
    f_t, f_s, f_xs = font(22), font(13), font(11)
    d.text((PADX, 16), "CARDFRONT art-direction audit - 16 mastered cards + 4 STAGES backgrounds (metrics: scripts/style_metrics.py)", fill=(230, 235, 245), font=f_t)
    vcol = {"keep": (34, 197, 94), "re-grade": (250, 204, 21), "regenerate": (239, 68, 68)}
    for i, r in enumerate(cards):
        x = PADX + (i % cols) * (CW + PADX)
        y = 60 + (i // cols) * (CH + TXT + 20)
        im = Image.open(ROOT / r["file"]).convert("RGB").resize((CW, CH), Image.LANCZOS)
        sheet.paste(im, (x, y))
        fac = (0, 229, 255) if Path(r["file"]).name.startswith("h_") else (255, 46, 84)
        d.rectangle([x - 2, y - 2, x + CW + 1, y + CH + 1], outline=fac, width=3)
        # subject bbox + com
        b = r["subject_bbox"]
        d.rectangle([x + b[0] * CW, y + b[1] * CH, x + b[2] * CW, y + b[3] * CH], outline=(255, 255, 255), width=1)
        cx, cy = x + r["subject_com"][0] * CW, y + r["subject_com"][1] * CH
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(255, 184, 0), width=2)
        # palette strip
        px = x
        for hexc, share in r["palette_top6"]:
            w = max(1, int(round(share * CW)))
            d.rectangle([px, y + CH + 2, px + w, y + CH + 14], fill=hexc)
            px += w
        ty = y + CH + 18
        name = Path(r["file"]).stem
        d.text((x, ty), name, fill=fac, font=f_s)
        vc = vcol[r["verdict"]]
        d.text((x + 120, ty), r["verdict"].upper(), fill=vc, font=f_s)
        lines = [
            f"sat {r['mean_saturation']:.2f} ({r['z']['mean_saturation']:+.1f}z) val {r['mean_value']:.2f}",
            f"contrast {r['rms_contrast']:.3f} ({r['z']['rms_contrast']:+.1f}z)",
            f"edge {r['edge_density']:.3f} ({r['z']['edge_density']:+.1f}z) line {r['line_weight_px']:.2f}px",
            f"noise {r['noise_sigma']:.2f} ({r['z']['noise_sigma']:+.1f}z)",
            f"subj area {r['subject_area']:.2f} com y {r['subject_com'][1]:.2f}",
            f"blue {r['blue_share']:.2f} red {r['red_share']:.2f} hue {r['dominant_hue_deg']:.0f}",
        ]
        for j, ln in enumerate(lines):
            d.text((x, ty + 18 + j * 15), ln, fill=(200, 208, 220), font=f_xs)
        if r["outlier_flags"]:
            d.text((x, ty + 18 + 6 * 15), "OUTLIER: " + ",".join(r["outlier_flags"])[:34], fill=(239, 68, 68), font=f_xs)
    # backgrounds row
    y0 = 60 + rows_cards * (CH + TXT + 20) + 10
    d.text((PADX, y0), "STAGES backgrounds (bg:) - shown raw; in-game they sit under a 0.72-0.97 alpha radial gradient", fill=(230, 235, 245), font=f_s)
    for i, r in enumerate(bgs):
        x = PADX + i * (bgW + 30)
        y = y0 + 22
        im = Image.open(ROOT / r["file"]).convert("RGB").resize((bgW, bgH), Image.LANCZOS)
        sheet.paste(im, (x, y))
        px = x
        for hexc, share in r["palette_top6"]:
            w = max(1, int(round(share * bgW)))
            d.rectangle([px, y + bgH + 2, px + w, y + bgH + 14], fill=hexc)
            px += w
        ty = y + bgH + 18
        d.text((x, ty), f"S{i+1} {Path(r['file']).stem[:40]}", fill=(230, 235, 245), font=f_xs)
        d.text((x, ty + 15), f"sat {r['mean_saturation']:.2f} val {r['mean_value']:.2f} contrast {r['rms_contrast']:.3f}", fill=(200, 208, 220), font=f_xs)
        d.text((x, ty + 30), f"edge {r['edge_density']:.3f} line {r['line_weight_px']:.2f}px noise {r['noise_sigma']:.2f}", fill=(200, 208, 220), font=f_xs)
        d.text((x, ty + 45), f"centre-playfield contrast {r['centre_rms_contrast']:.3f}  verdict {r['verdict'].upper()}", fill=vcol[r['verdict']], font=f_xs)
    sheet.save(path)


def main():
    cards, bgs = discover_assets()
    card_rows = [metrics_for(ROOT / "GeneratedArt/MasteredCards" / f"{c}.png", "card") for c in cards]
    bg_rows = [metrics_for(ROOT / "GeneratedArt" / b, "background") for b in bgs]
    stats = zscores(card_rows)
    fac = faction_analysis(card_rows)
    for r in card_rows:
        r["verdict"], r["reasons"] = verdict(r, fac)

    # background: style distance to the card family centroid (z-normalised over card stats)
    feat = ["mean_saturation", "mean_value", "rms_contrast", "edge_density", "line_weight_px", "noise_sigma"]
    for r in bg_rows:
        zs = {k: (r[k] - stats[k]["mean"]) / stats[k]["std"] for k in feat}
        r["z_vs_cards"] = zs
        r["style_distance_to_cards"] = float(math.sqrt(sum(v * v for v in zs.values()) / len(zs)))
        im = np.asarray(Image.open(ROOT / r["file"]).convert("RGB"))
        Hh, Ww = im.shape[:2]
        c = luminance(im[int(Hh * .2):int(Hh * .8), int(Ww * .25):int(Ww * .75)]) / 255.0
        r["centre_rms_contrast"] = float(c.std())
    # pairwise distance among backgrounds (are they one family?)
    bfeat = np.array([[r[k] for k in feat] for r in bg_rows])
    bnorm = (bfeat - bfeat.mean(0)) / (bfeat.std(0) + 1e-9)
    card_feat = np.array([[r[k] for k in feat] for r in card_rows])
    card_cv = (card_feat.std(0) / card_feat.mean(0)).tolist()
    bg_cv = (bfeat.std(0) / bfeat.mean(0)).tolist()
    for r in bg_rows:
        reasons = []
        if r["style_distance_to_cards"] > 1.5:
            reasons.append(f"style distance to card family {r['style_distance_to_cards']:.2f} (>1.5 card-sigma RMS)")
        if r["centre_rms_contrast"] > 0.20:
            reasons.append(f"centre playfield RMS contrast {r['centre_rms_contrast']:.3f} > 0.20 (raster-pipeline: keep low-contrast playfield)")
        r["verdict"] = "regenerate" if len(reasons) >= 2 else ("re-grade" if reasons else "keep")
        r["reasons"] = reasons

    out = {
        "generated_by": "scripts/style_metrics.py",
        "cards": card_rows,
        "backgrounds": bg_rows,
        "card_family_stats": stats,
        "faction": fac,
        "coefficient_of_variation": {"features": feat, "cards": card_cv, "backgrounds": bg_cv},
        "verdict_counts": {v: sum(r["verdict"] == v for r in card_rows) for v in ("keep", "re-grade", "regenerate")},
    }
    (RAW / "style_metrics.json").write_text(json.dumps(out, indent=2))
    with open(RAW / "style_metrics.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        hdr = ["name", "kind", "w", "h", "sat", "val", "contrast", "edge", "line_px", "noise", "subj_area", "com_x", "com_y", "blue", "red", "dom_hue", "verdict", "flags"]
        w.writerow(hdr)
        for r in card_rows + bg_rows:
            w.writerow([Path(r["file"]).stem, r["kind"], r["width"], r["height"], f"{r['mean_saturation']:.3f}", f"{r['mean_value']:.3f}",
                        f"{r['rms_contrast']:.3f}", f"{r['edge_density']:.4f}", f"{r['line_weight_px']:.2f}", f"{r['noise_sigma']:.2f}",
                        f"{r['subject_area']:.3f}", f"{r['subject_com'][0]:.2f}", f"{r['subject_com'][1]:.2f}", f"{r['blue_share']:.3f}",
                        f"{r['red_share']:.3f}", f"{r['dominant_hue_deg']:.0f}", r["verdict"], ";".join(r.get("outlier_flags", []))])
    contact_sheet(card_rows, bg_rows, OUT / "contact_sheet.png")
    # console summary
    for r in card_rows:
        print(f"{Path(r['file']).stem:12s} sat={r['mean_saturation']:.2f} val={r['mean_value']:.2f} con={r['rms_contrast']:.3f} edge={r['edge_density']:.3f} "
              f"line={r['line_weight_px']:.2f} noise={r['noise_sigma']:.2f} area={r['subject_area']:.2f} com=({r['subject_com'][0]:.2f},{r['subject_com'][1]:.2f}) "
              f"B={r['blue_share']:.2f} R={r['red_share']:.2f} hue={r['dominant_hue_deg']:.0f} -> {r['verdict']} {r['outlier_flags']}")
    for r in bg_rows:
        print(f"BG {Path(r['file']).stem[:34]:34s} sat={r['mean_saturation']:.2f} val={r['mean_value']:.2f} con={r['rms_contrast']:.3f} edge={r['edge_density']:.3f} "
              f"line={r['line_weight_px']:.2f} noise={r['noise_sigma']:.2f} dist={r['style_distance_to_cards']:.2f} centre_con={r['centre_rms_contrast']:.3f} -> {r['verdict']}")
    print(json.dumps(fac, indent=1))
    print("CV cards", [round(x, 3) for x in card_cv], "CV bgs", [round(x, 3) for x in bg_cv])
    print(out["verdict_counts"])


if __name__ == "__main__":
    main()
