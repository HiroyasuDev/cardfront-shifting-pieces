#!/usr/bin/env python3
"""
export_agent_deck_printable_pdf.py
==================================
Generates a high-resolution multi-page printable PDF sheet for the 37-card
CARDFRONT: Cradle of Echoes — Agent Command Deck:
  - Page 1: Master Blueprint Cover & Deck Manifest
  - Pages 2..6: 3x3 nine-pocket card pages (600x800 portrait cards with crop marks)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
AGENT_DECK_DIR = ROOT / "GeneratedArt" / "AgentDeck"
CARDS_DIR = AGENT_DECK_DIR / "Cards"
OUT_PDF = AGENT_DECK_DIR / "CARDFRONT_37_Card_Agent_Command_Deck_Printable.pdf"


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def build_cover_page(width: int = 2480, height: int = 3508) -> Image.Image:
    page = Image.new("RGB", (width, height), (7, 11, 22))
    draw = ImageDraw.Draw(page)

    # Outer gold filigree border
    draw.rectangle([48, 48, width - 48, height - 48], outline=(212, 163, 73), width=6)
    draw.rectangle([68, 68, width - 68, height - 68], outline=(0, 229, 255), width=2)

    f_title = load_font(68, bold=True)
    f_sub = load_font(34, bold=False)
    f_meta = load_font(28, bold=True)

    draw.text((120, 120), "CARDFRONT: CRADLE OF ECHOES", fill=(255, 184, 0), font=f_title)
    draw.text((120, 210), "SOVEREIGN AGENT COMMAND DECK — 37 STUDIO-MASTERED 600×800 CARDS", fill=(224, 242, 254), font=f_sub)
    draw.text(
        (120, 268),
        "4 Sovereign Plugins  ·  12 Arcane Skills  ·  13 Native Tools  ·  8 MCP Server Relics  ·  6 Watertight 3D .glb Miniatures",
        fill=(46, 230, 211),
        font=f_meta,
    )

    blueprint_path = AGENT_DECK_DIR / "tcg_creative_designer_master_blueprint.png"
    if blueprint_path.exists():
        bp = Image.open(blueprint_path).convert("RGB")
        target_w = width - 240
        target_h = int(bp.height * (target_w / bp.width))
        bp_resized = bp.resize((target_w, target_h), Image.Resampling.LANCZOS)
        page.paste(bp_resized, (120, 350))
        y_offset = 350 + target_h + 48
    else:
        y_offset = 380

    preview_path = AGENT_DECK_DIR / "tcg_agent_deck_preview_sheet.png"
    if preview_path.exists() and y_offset < height - 400:
        pv = Image.open(preview_path).convert("RGB")
        avail_h = height - y_offset - 120
        avail_w = width - 240
        scale = min(avail_w / pv.width, avail_h / pv.height)
        nw, nh = int(pv.width * scale), int(pv.height * scale)
        pv_resized = pv.resize((nw, nh), Image.Resampling.LANCZOS)
        page.paste(pv_resized, ((width - nw) // 2, y_offset))

    return page


def build_card_sheet_pages(card_paths, width: int = 2480, height: int = 3508):
    pages = []
    cols, rows = 3, 3
    per_page = cols * rows
    card_w, card_h = 660, 880  # 3:4 aspect ratio at ~300 DPI print size
    grid_w = cols * card_w + (cols - 1) * 60
    grid_h = rows * card_h + (rows - 1) * 60
    start_x = (width - grid_w) // 2
    start_y = 280
    f_hdr = load_font(36, bold=True)
    f_lbl = load_font(22, bold=False)

    for page_idx in range(0, len(card_paths), per_page):
        chunk = card_paths[page_idx : page_idx + per_page]
        page = Image.new("RGB", (width, height), (10, 14, 26))
        draw = ImageDraw.Draw(page)
        draw.rectangle([40, 40, width - 40, height - 40], outline=(212, 163, 73), width=4)
        sheet_num = (page_idx // per_page) + 1
        total_sheets = (len(card_paths) + per_page - 1) // per_page
        draw.text(
            (start_x, 110),
            f"CARDFRONT 3D: AGENT COMMAND DECK — 9-POCKET PRINT SHEET {sheet_num} / {total_sheets}",
            fill=(255, 184, 0),
            font=f_hdr,
        )
        draw.text(
            (start_x, 165),
            "Normalized 600×800 (3:4 Portrait) · Trim along outer cyan crop marks",
            fill=(148, 163, 184),
            font=f_lbl,
        )

        for idx, cp in enumerate(chunk):
            r = idx // cols
            c = idx % cols
            x = start_x + c * (card_w + 60)
            y = start_y + r * (card_h + 60)

            # Crop marks
            cm = 18
            draw.line([(x - cm, y), (x + cm, y)], fill=(0, 229, 255), width=2)
            draw.line([(x, y - cm), (x, y + cm)], fill=(0, 229, 255), width=2)
            draw.line([(x + card_w - cm, y), (x + card_w + cm, y)], fill=(0, 229, 255), width=2)
            draw.line([(x + card_w, y - cm), (x + card_w, y + cm)], fill=(0, 229, 255), width=2)
            draw.line([(x - cm, y + card_h), (x + cm, y + card_h)], fill=(0, 229, 255), width=2)
            draw.line([(x, y + card_h - cm), (x, y + card_h + cm)], fill=(0, 229, 255), width=2)
            draw.line([(x + card_w - cm, y + card_h), (x + card_w + cm, y + card_h)], fill=(0, 229, 255), width=2)
            draw.line([(x + card_w, y + card_h - cm), (x + card_w, y + card_h + cm)], fill=(0, 229, 255), width=2)

            img = Image.open(cp).convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS)
            page.paste(img, (x, y))
            draw.rectangle([x, y, x + card_w, y + card_h], outline=(212, 163, 73), width=2)
            draw.text((x + 6, y + card_h + 10), cp.stem, fill=(203, 213, 225), font=f_lbl)

        pages.append(page)
    return pages


def main():
    card_paths = sorted(CARDS_DIR.glob("*.png"))
    if not card_paths:
        raise RuntimeError(f"No card PNGs found in {CARDS_DIR}")
    cover = build_cover_page()
    sheets = build_card_sheet_pages(card_paths)
    cover.save(OUT_PDF, "PDF", resolution=300.0, save_all=True, append_images=sheets)
    print(f"[export_agent_deck_printable_pdf] Saved {1 + len(sheets)}-page PDF ({len(card_paths)} cards) -> {OUT_PDF}")


if __name__ == "__main__":
    main()
