# A11y analysis of screenshots produced by t5_a11y.js (Pillow + numpy).
# - grayscale version of the mid-game board
# - player (blue) vs AI (red) border colour separation under normal / grayscale / CVD emulation
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(ROOT, "screens")
raw = json.load(open(os.path.join(ROOT, "raw", "t5_a11y.json")))
own = raw["colorOnlyOwnership"]["owners"]

def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def rel_lum(rgb):
    l = srgb_to_lin(np.array(rgb, dtype=float))
    return float(0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2])

def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def to_lab(rgb):
    l = srgb_to_lin(np.array(rgb, dtype=float))
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = M @ l / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

def owner_pixel_mask(img_normal, rect, origin, kind):
    """Coordinates of border-coloured pixels inside the card bbox in the NORMAL screenshot
    (cyan for player, red for AI), restricted to a 6px band along the bbox edges."""
    a = np.asarray(img_normal.convert("RGB")).astype(int)
    x, y, w, h = rect
    ox, oy = origin
    x0, y0 = max(0, int(x - ox)), max(0, int(y - oy))
    x1, y1 = min(a.shape[1], int(x - ox + w)), min(a.shape[0], int(y - oy + h))
    sub = a[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    band = (np.minimum.reduce([yy - y0, y1 - 1 - yy, xx - x0, x1 - 1 - xx]) < 6)
    R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
    if kind == "player":
        m = (R < 80) & (G > 170) & (B > 190)
    else:
        m = (R > 180) & (G < 110) & (B < 140)
    m = m & band
    return yy[m], xx[m]

def median_at(img, ys, xs):
    a = np.asarray(img.convert("RGB")).astype(float)
    return np.median(a[ys, xs], axis=0) if len(ys) else np.array([np.nan] * 3)

out = {"theoretical": {}, "measured": {}}
blue, red = (0x00, 0xE5, 0xFF), (0xFF, 0x2E, 0x54)
out["theoretical"] = {
    "blue_#00E5FF_luminance": round(rel_lum(blue), 3), "red_#FF2E54_luminance": round(rel_lum(red), 3),
    "blue_vs_red_contrast_ratio": round(contrast(blue, red), 2),
    "gray_value_blue_rec601": round(0.299 * blue[0] + 0.587 * blue[1] + 0.114 * blue[2], 1),
    "gray_value_red_rec601": round(0.299 * red[0] + 0.587 * red[1] + 0.114 * red[2], 1),
    "deltaE76_normal": round(float(np.linalg.norm(to_lab(blue) - to_lab(red))), 1),
}

g = Image.open(os.path.join(S, "t5_cvd_none.png")).convert("L")
g.save(os.path.join(S, "t5_grayscale_board.png"))

if own:
    origin = own["slabOrigin"]
    normal = Image.open(os.path.join(S, "t5_cvd_none.png"))
    py, px = owner_pixel_mask(normal, own["playerRect"], origin, "player")
    ay, ax = owner_pixel_mask(normal, own["aiRect"], origin, "ai")
    out["measured"]["sampled_pixels"] = {"player": int(len(py)), "ai": int(len(ay))}
    for t in ["none", "achromatopsia", "protanopia", "deuteranopia", "tritanopia"]:
        img = Image.open(os.path.join(S, f"t5_cvd_{t}.png"))
        pb = median_at(img, py, px)
        pa = median_at(img, ay, ax)
        out["measured"][t] = {
            "player_border_rgb": [int(v) for v in pb], "ai_border_rgb": [int(v) for v in pa],
            "contrast_ratio_between_borders": round(contrast(pb, pa), 2),
            "deltaE76": round(float(np.linalg.norm(to_lab(pb) - to_lab(pa))), 1),
        }
    gb = median_at(g.convert("RGB"), py, px)
    ga = median_at(g.convert("RGB"), ay, ax)
    out["measured"]["grayscale_L"] = {"player_gray": int(gb[0]), "ai_gray": int(ga[0]), "contrast_ratio": round(contrast(gb, ga), 2)}

json.dump(out, open(os.path.join(ROOT, "raw", "t5_color_analysis.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
