#!/usr/bin/env python3
"""
Backend/synapse_card_identification_catalog.py
==============================================
Sovereign Bilingual Card Identification & Collector Taxonomy Engine (`[BP01]`–`[BP05]`)
for CARDFRONT: Cradle of Echoes & Shadowverse EVOLVE Collector Standard.

Models every card in the franchise on the exact collector identification specification:
    original title    機構翼の少女・ローザ(進化前)
    card game         Shadowverse EVOLVE
    version           [BP05] Eternal omens
    original version  ブースターパック第5弾 永劫なる絶傑
    card number       BP05-110 SR
    rarity            SR

Generates, validates, queries, and exports:
  1. `Assets/Resources/Cards/card_identification_catalog_v1.json` (+ `.meta`)
  2. `Assets/Resources/Cards/set1_60_cards_manifest.json` (+ `.meta`)
  3. `Logs/card_identification_catalog_report.json`

Every card record includes:
  - Full Bilingual Collector Identification metadata (`original_title`, `original_title_evolved`,
    `title`, `card_game`, `card_game_primary`, `card_game_interop`, `version`, `original_version`,
    `card_number`, `rarity`, `rarity_full_en`, `rarity_full_jp`, `evolution_state`,
    `evolved_counterpart`, `sha256_collector_id`).
  - Meaningful bilingual lore (`lore_en` and `lore_jp`) connecting the character/construct to
    the world of *CARDFRONT: Cradle of Echoes*.
  - `atelier_art_direction`: Detailed appreciation notes on brushwork, silhouette, chromatic
    faction harmony (`#00E5FF`, `#FFB800`, `#FF2E54`, `#A855F7`, `#2EE6D3`), and 2.5D depth/foil
    layering (strictly zero living artist names).
  - `collector_provenance`: `edition` (`"1st Edition · 初版"`), `serial_mint` (`"#0001 / 0500"`),
    `foil_treatment`, `full_bleed_resolution` (`"600x800 (3:4 Portrait)"`), and `sha256_collector_id`.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
CARDS_RES_DIR = PROJECT_ROOT / "Assets" / "Resources" / "Cards"
LOGS_DIR = PROJECT_ROOT / "Logs"

CATALOG_OUT_PATH = CARDS_RES_DIR / "card_identification_catalog_v1.json"
SET1_MANIFEST_OUT_PATH = CARDS_RES_DIR / "set1_60_cards_manifest.json"
REPORT_OUT_PATH = LOGS_DIR / "card_identification_catalog_report.json"


# =============================================================================
# 1. BOOSTER PACK TAXONOMY ([BP01] .. [BP05]) & RARITY TIERS
# =============================================================================
BOOSTER_SETS: Dict[str, Dict[str, Any]] = {
    "BP01": {
        "set_code": "BP01",
        "pack_index": 1,
        "version": "[BP01] Cradle of Echoes",
        "original_version": "ブースターパック第1弾 響きの揺り籠",
        "release_era": "Era I: Awakening of the Sky-Citadel Monoliths",
        "total_numbered_slots": 120,
        "theme_focus": "Foundational 3x3 Directional Capture & First Echo Conduits",
    },
    "BP02": {
        "set_code": "BP02",
        "pack_index": 2,
        "version": "[BP02] Reign of Law",
        "original_version": "ブースターパック第2弾 律法の覇権",
        "original_version_alt": "ブースターパック第2弾 律法の覇권",
        "release_era": "Era I: High Tribunal of Ivalice Law & Iron Vanguard",
        "total_numbered_slots": 120,
        "theme_focus": "Sacred Law Decrees, Judge Seals & Siege Dreadnoughts",
    },
    "BP03": {
        "set_code": "BP03",
        "pack_index": 3,
        "version": "[BP03] Astral Resonance",
        "original_version": "ブースターパック第3弾 星界の共鳴",
        "release_era": "Era I: Celestial Astrolabe & Lunar Tide Convergence",
        "total_numbered_slots": 120,
        "theme_focus": "Starlight Divination, Solar Paladins & Harmonic Choirs",
    },
    "BP04": {
        "set_code": "BP04",
        "pack_index": 4,
        "version": "[BP04] Chrono Sanctum",
        "original_version": "ブースターパック第4弾 時空の聖域",
        "release_era": "Era II: Pendulum Cathedral & Cyber-Umbra Infiltration",
        "total_numbered_slots": 120,
        "theme_focus": "Temporal Gear Locks, 90-Degree Stealth Cones & Hourglass Rifts",
    },
    "BP05": {
        "set_code": "BP05",
        "pack_index": 5,
        "version": "[BP05] Eternal omens",
        "original_version": "ブースターパック第5弾 永劫なる絶傑",
        "release_era": "Era II: Mechanized Wing Maidens & Omen of the Ten Sovereigns",
        "total_numbered_slots": 120,
        "theme_focus": "Evolve (進化前 / 進化後) Pinion Overdrive & Apex Singularity",
    },
}

RARITY_TIERS: Dict[str, Dict[str, str]] = {
    "UR": {
        "code": "UR",
        "rarity_full_en": "Ultimate Rare",
        "rarity_full_jp": "アルティメットレア",
        "foil_treatment": "Astral Prismatic Cold-Foil + Textured Gold Leaf Emboss + Full-Bleed Borderless Etch",
        "pull_rate_tier": "1 per Case (Masterpiece Chase)",
    },
    "SL": {
        "code": "SL",
        "rarity_full_en": "Super Legend",
        "rarity_full_jp": "スーパーレジェンド",
        "foil_treatment": "Sovereign Dual-Layer Holographic Filigree + Raised Silver-Gold Stamp",
        "pull_rate_tier": "2 per Case (Signed Frame Edition)",
    },
    "LG": {
        "code": "LG",
        "rarity_full_en": "Legend",
        "rarity_full_jp": "レジェンド",
        "foil_treatment": "Ivalice Law Gold-Leaf Frame + Radiant Halo Spot-UV",
        "pull_rate_tier": "2 per Booster Box",
    },
    "SR": {
        "code": "SR",
        "rarity_full_en": "Super Rare",
        "rarity_full_jp": "スーパーレア",
        "foil_treatment": "Gunmetal-Silver Filigree Cold-Foil + Prismatic Pinion Shimmer",
        "pull_rate_tier": "4 per Booster Box",
    },
    "GR": {
        "code": "GR",
        "rarity_full_en": "Gold Rare",
        "rarity_full_jp": "ゴールドレア",
        "foil_treatment": "Warm Parchment-Gold Metallic Rim + Micro-Etched Astrolabe Pattern",
        "pull_rate_tier": "8 per Booster Box",
    },
    "BR": {
        "code": "BR",
        "rarity_full_en": "Bronze Rare",
        "rarity_full_jp": "ブロンズレア",
        "foil_treatment": "Matte Atelier Silk-Varnish + Crisp Sumi-e Spot Gloss",
        "pull_rate_tier": " Core Collector Standard",
    },
}

LEGACY_RARITY_TO_COLLECTOR_CODE: Dict[str, str] = {
    "Mythic": "UR",
    "Legendary": "LG",
    "Epic": "SR",
    "Rare": "GR",
    "Common": "BR",
    "UR": "UR",
    "SL": "SL",
    "LG": "LG",
    "SR": "SR",
    "GR": "GR",
    "BR": "BR",
}

FACTION_ATELIER_NOTES: Dict[str, Dict[str, str]] = {
    "Tech": {
        "faction_name": "Aether-Tech / Valkyria Mechanica",
        "palette_hex": "#00E5FF (Astral Cyan) & #FFB800 (Brass-Gold Filigree)",
        "morphology": (
            "Stylized 7.0-to-7.5-head anime proportions with articulated brass-gold and gunmetal mechanical "
            "pinions, sleek beveled cyber-magicite armor plates, tapered gauntlets, and translucent emerald/cyan "
            "energy feathers over warm sunlit cel-wash."
        ),
        "foil_depth": (
            "3-plane 2.5D parallax depth map: Foreground clockwork feathers (+12px Z-relief), Midground heroine/knight "
            "silhouette (0px focal anchor), Background sky-citadel cloudsea (-14px atmospheric depth)."
        ),
    },
    "Magic": {
        "faction_name": "Chrono-Arcana / Aether Sanctum",
        "palette_hex": "#A855F7 (Tarot Violet) & #FFE082 (Gilded Parchment)",
        "morphology": (
            "Stylized 7-head arcane proportions framed by interlocking astrolabe rings, dense G-pen sumi-e ink "
            "crosshatching over warm parchment-gold filigree, levitating grimoire pages, and vibrant watercolor cel-wash."
        ),
        "foil_depth": (
            "3-plane 2.5D parallax depth map: Foreground tarot sigils and mana threads (+14px cold-foil mask), "
            "Midground spellcaster figure (0px crisp cel plane), Background observatory vault (-16px)."
        ),
    },
    "Divine": {
        "faction_name": "Solaris-Divine / Celestial Order",
        "palette_hex": "#FFB800 (Ivalice Law Gold) & #2EE6D3 (Jade-Teal Magicite)",
        "morphology": (
            "Heroic 7-head tactical paladin and seraph proportions, ornate baroque plate filigree, stained-glass "
            "sacred geometry halos, sculptural ivory capes, and radiant sunbeam cel-shading."
        ),
        "foil_depth": (
            "3-plane 2.5D parallax depth map: Foreground sacred law scales and feather tips (+13px gold-leaf emboss), "
            "Midground sovereign figure (0px), Background cathedral sunbeams (-15px)."
        ),
    },
    "Stealth": {
        "faction_name": "Umbra-Stealth / Shadow Syndicate",
        "palette_hex": "#FF2E54 (Crimson-Flame) & #C026D3 (Void Amethyst over Obsidian)",
        "morphology": (
            "Sleek 7-head stealth operative proportions, razor-sharp G-pen ink crosshatching, CMYK Ben-Day halftone "
            "screentone shadows, stark chiaroscuro negative space, and glowing crimson-amethyst optic trails."
        ),
        "foil_depth": (
            "3-plane 2.5D parallax depth map: Foreground kunai tracers and radar reticle (+11px spot-UV gloss), "
            "Midground infiltrator silhouette (0px), Background rain-slicked Neo-Arcadia spire (-14px)."
        ),
    },
    "Artisan": {
        "faction_name": "CardCraft-Studio / Sovereign Atelier",
        "palette_hex": "#A855F7 (Atelier Violet), #FFB800 (Sovereign Gold) & #00E5FF (Prism Cyan)",
        "morphology": (
            "Expressive 6.5-to-7-head creative director and key-animator proportions, living sumi-e brush coils, "
            "24fps impact-star flares, and multi-layered gouache over warm archival vellum texture."
        ),
        "foil_depth": (
            "3-plane 2.5D parallax depth map: Foreground living ink ribbons and prism nibs (+15px holographic foil), "
            "Midground artisan creator (0px), Background studio drafting sanctum (-15px)."
        ),
    },
}


# =============================================================================
# 2. 16 PLAYABLE HERO & BOSS CARDS (EXACT BILINGUAL COLLECTOR SPECIFICATIONS)
# =============================================================================
HERO_BOSS_16_SPECS: List[Dict[str, Any]] = [
    {
        "card_id": "kaelen",
        "web_alias_id": "h_kai",
        "title": "Kaelen, Sky-Pinion Vanguard (Unevolved)",
        "title_evolved": "Kaelen, Sky-Pinion Vanguard (Evolved)",
        "original_title": "蒼穹の機巧翼・カエレン(進化前)",
        "original_title_evolved": "蒼穹の機巧翼・カエレン(進化後)",
        "set_code": "BP01",
        "slot_number": 1,
        "rarity": "LG",
        "theme": "Tech",
        "faction": "Aether-Tech",
        "cost": 3,
        "up": 7, "right": 8, "down": 6, "left": 7,
        "art_path": "GeneratedArt/HeroCards/hero_01_kaelen_v2.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_kai.png",
        "lore_en": (
            "Born atop the wind-swept docks of Skystone Sanctuary, Kaelen calibrated his twin brass-and-cyan "
            "pinions to ride the violent mana updrafts of the 3x3 Citadel Monoliths. Even before full Awakening, "
            "his aerial target lock turns every flanking gust into a decisive vanguard strike."
        ),
        "lore_jp": (
            "浮遊城塞スカイストーンの風鳴る造船所で育ったカエレンは、真鍮と蒼光の機巧翼を自ら調律し、"
            "３×３モノリスの乱気流を翔ける。その双眸が捉えた戦線の隙は、一陣の蒼風となって敵陣を貫く。"
        ),
    },
    {
        "card_id": "seraph",
        "web_alias_id": "h_seraph",
        "title": "Seraph, Astral Choir Sovereign (Unevolved)",
        "title_evolved": "Seraph, Astral Choir Sovereign (Evolved)",
        "original_title": "星界の熾天使・セラフ(進化前)",
        "original_title_evolved": "星界の熾天使・セラフ(進化後)",
        "set_code": "BP01",
        "slot_number": 2,
        "rarity": "UR",
        "theme": "Divine",
        "faction": "Solaris-Divine",
        "cost": 4,
        "up": 8, "right": 6, "down": 7, "left": 8,
        "art_path": "GeneratedArt/MasteredCards/h_seraph.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_seraph.png",
        "lore_en": (
            "Descending from the highest choir of the Cradle of Echoes, Seraph unfolds six crystalline wings "
            "that resonate with the harmonic chimes of the First Law. Each beat of her pinions inscribes a four-point "
            "cross-star flare across the North and West sanctum lanes."
        ),
        "lore_jp": (
            "響きの揺り籠の最上聖歌隊より舞い降りし熾天使セラフ。六枚の結晶翼が第一律法の鐘音と共鳴するとき、"
            "北と西の戦線に煌めく十字星のアストラル・フレアが刻まれる。"
        ),
    },
    {
        "card_id": "vex",
        "web_alias_id": "e_reaper",
        "title": "Vex, Crimson Tactician (Unevolved)",
        "title_evolved": "Vex, Crimson Tactician (Evolved)",
        "original_title": "紅蓮の戦術士・ヴェックス(進化前)",
        "original_title_evolved": "紅蓮の戦術士・ヴェックス(進化後)",
        "set_code": "BP02",
        "slot_number": 14,
        "rarity": "SR",
        "theme": "Stealth",
        "faction": "Umbra-Stealth",
        "cost": 3,
        "up": 6, "right": 7, "down": 7, "left": 5,
        "art_path": "GeneratedArt/MasteredCards/e_reaper.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_reaper.png",
        "lore_en": (
            "A renegade strategist of the Crimson Foundry who treats the 3x3 grid as a living chessboard of "
            "feints and counter-captures. Vex's 180-degree blood-rune cleave lures overconfident paladins into "
            "an inescapable East-South pincer."
        ),
        "lore_jp": (
            "３×３の石盤を生ける盤上とみなす紅蓮工房の異端戦術士。ヴェックスが振るう紅の刻印鎌は、"
            "東と南の二面を同時に薙ぎ払い、突出した聖騎士たちを鮮やかに反転捕獲する。"
        ),
    },
    {
        "card_id": "solaris",
        "web_alias_id": "h_archangel",
        "title": "Solaris, Sunlit Law Paladin (Unevolved)",
        "title_evolved": "Solaris, Sunlit Law Paladin (Evolved)",
        "original_title": "陽炎の聖騎士・ソラリス(進化前)",
        "original_title_evolved": "陽炎の聖騎士・ソラリス(進化後)",
        "set_code": "BP03",
        "slot_number": 28,
        "rarity": "LG",
        "theme": "Divine",
        "faction": "Solaris-Divine",
        "cost": 4,
        "up": 8, "right": 7, "down": 6, "left": 7,
        "art_path": "GeneratedArt/MasteredCards/h_archangel.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_archangel.png",
        "lore_en": (
            "Anointed beneath the golden astrolabe of the Solar Spire, Solaris bears a cruciform lance forged "
            "from condensed dawnlight. Wherever his banner stands on the center monolith, adjacent allied conduits "
            "are shielded by the unbroken decree of Ivalice Law."
        ),
        "lore_jp": (
            "太陽の尖塔の黄金天球儀の下で叙任された聖騎士ソラリス。暁光を凝縮した十字槍を掲げ、"
            "中央モノリスに立つだけで隣接する味方コンジットに不壊の律法障壁を授ける。"
        ),
    },
    {
        "card_id": "nyx",
        "web_alias_id": "e_eclipse",
        "title": "Nyx, Abyssal Clockwork Maiden (Unevolved)",
        "title_evolved": "Nyx, Abyssal Clockwork Maiden (Evolved)",
        "original_title": "深淵の機巧少女・ニュクス(進化前)",
        "original_title_evolved": "深淵の機巧少女・ニュクス(進化後)",
        "set_code": "BP05",
        "slot_number": 42,
        "alt_card_number": "BP05-110 SR",
        "rarity": "SR",
        "theme": "Stealth",
        "faction": "Umbra-Stealth",
        "cost": 3,
        "up": 6, "right": 6, "down": 5, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/e_eclipse.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_eclipse.png",
        "lore_en": (
            "Woven from midnight Mainspring gears and umbral starlight in the fifth Eternal Omen, Nyx dances "
            "along the edge of the Eclipse singularity. Her twin clockwork blades fold space-time to reverse "
            "opposing directional ranks in a single heartbeat."
        ),
        "lore_jp": (
            "第五の絶傑『永劫なる絶傑』の深淵で、宵闇のぜんまい歯車と星影から紡がれた機巧少女ニュクス。"
            "双対の時計刃が虚空を裂くとき、敵対ユニットの四方ランクは一瞬にして反転する。"
        ),
    },
    {
        "card_id": "bastion",
        "web_alias_id": "h_arbiter",
        "title": "Bastion, Ironclad Fortress Titan (Unevolved)",
        "title_evolved": "Bastion, Ironclad Fortress Titan (Evolved)",
        "original_title": "鉄壁の重装機神・バスティオン(進化前)",
        "original_title_evolved": "鉄壁の重装機神・バスティオン(進化後)",
        "set_code": "BP01",
        "slot_number": 15,
        "rarity": "GR",
        "theme": "Tech",
        "faction": "Aether-Tech",
        "cost": 4,
        "up": 7, "right": 7, "down": 8, "left": 8,
        "art_path": "GeneratedArt/MasteredCards/h_arbiter.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_arbiter.png",
        "lore_en": (
            "Engineered to anchor the southern civilian power grid against Leviathan tremors, Bastion locks its "
            "hydraulic stabilizers directly into the stone slab. No push vector or seismic bump can dislodge "
            "its towering hexagonal aegis."
        ),
        "lore_jp": (
            "民間電力グリッドを巨獣の震動から護るため建造された重装機神バスティオン。油圧アンカーを石盤へ直結し、"
            "いかなる衝撃波や強制移動テレグラフも寄せ付けない絶対防壁を築く。"
        ),
    },
    {
        "card_id": "chronos",
        "web_alias_id": "h_chronos",
        "title": "Chronos, Sovereign of the Pendulum (Unevolved)",
        "title_evolved": "Chronos, Sovereign of the Pendulum (Evolved)",
        "original_title": "時空の歯車導師・クロノス(進化前)",
        "original_title_evolved": "時空の歯車導師・クロノス(進化後)",
        "set_code": "BP04",
        "slot_number": 7,
        "rarity": "UR",
        "theme": "Magic",
        "faction": "Chrono-Arcana",
        "cost": 4,
        "up": 6, "right": 8, "down": 7, "left": 7,
        "art_path": "GeneratedArt/MasteredCards/h_chronos.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_chronos.png",
        "lore_en": (
            "Keeper of the 1440-Frame Chrono Sanctum, Chronos conducts the planetary escapement gears that govern "
            "every turn clock. With one sweep of his pendulum staff, East, South, and West lanes lock into "
            "golden temporal stasis."
        ),
        "lore_jp": (
            "１４４０フレームの時空聖域を統べる歯車導師クロノス。惑星脱進機の律動を自在に操り、"
            "振り子の杖を一振りするだけで東・南・西の三戦線を黄金の時間停止へと封じる。"
        ),
    },
    {
        "card_id": "orb",
        "web_alias_id": "e_cryo",
        "title": "Orb, Celestial Astrolabe Core (Unevolved)",
        "title_evolved": "Orb, Celestial Astrolabe Core (Evolved)",
        "original_title": "天球の魔導核・オーブ(進化前)",
        "original_title_evolved": "天球の魔導核・オーブ(進化後)",
        "set_code": "BP03",
        "slot_number": 19,
        "rarity": "SR",
        "theme": "Magic",
        "faction": "Chrono-Arcana",
        "cost": 2,
        "up": 5, "right": 7, "down": 6, "left": 7,
        "art_path": "GeneratedArt/MasteredCards/e_cryo.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_cryo.png",
        "lore_en": (
            "A sentient gyroscope of cryo-sapphire and brass rings suspended in the heart of the Astral Observatory. "
            "Orb refracts sub-zero mana lattices across horizontal lanes, crystallizing enemy telegraph vectors before "
            "they can ignite."
        ),
        "lore_jp": (
            "星界天文台の心臓部に浮かぶ氷蒼玉と真鍮リングの自律魔導核オーブ。絶対零度の魔力格子を東西のレーンへ展開し、"
            "敵の攻撃テレグラフを発動前に氷結させる。"
        ),
    },
    {
        "card_id": "dreadnought",
        "web_alias_id": "e_titan",
        "title": "Dreadnought, Thunderclad Siege Ark (Unevolved)",
        "title_evolved": "Dreadnought, Thunderclad Siege Ark (Evolved)",
        "original_title": "轟雷の超弩級艦・ドレッドノート(進化前)",
        "original_title_evolved": "轟雷の超弩級艦・ドレッドノート(進化後)",
        "set_code": "BP02",
        "slot_number": 33,
        "rarity": "LG",
        "theme": "Tech",
        "faction": "Aether-Tech",
        "cost": 4,
        "up": 7, "right": 5, "down": 7, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/e_titan.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_titan.png",
        "lore_en": (
            "Flagship of the Iron Vanguard Directorate's orbital armada, Dreadnought descends on twin seismic "
            "thrusters. Its broadside rail-batteries send concentric shockwaves surging North and South across "
            "the stone tabletop."
        ),
        "lore_jp": (
            "鉄血先遣局の軌道艦隊を率いる超弩級戦艦ドレッドノート。重装スラスターの轟音と共に降下し、"
            "主砲レールキャノンの斉射で南北のタイルへ強烈な地震波を叩き込む。"
        ),
    },
    {
        "card_id": "archon",
        "web_alias_id": "e_archon",
        "title": "Archon, Prism Law Judicator (Unevolved)",
        "title_evolved": "Archon, Prism Law Judicator (Evolved)",
        "original_title": "プリズムの裁定者・アルコン(進化前)",
        "original_title_evolved": "プリズムの裁定者・アルコン(進化後)",
        "set_code": "BP02",
        "slot_number": 8,
        "rarity": "SL",
        "theme": "Divine",
        "faction": "Solaris-Divine",
        "cost": 4,
        "up": 7, "right": 6, "down": 6, "left": 5,
        "art_path": "GeneratedArt/MasteredCards/e_archon.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_archon.png",
        "lore_en": (
            "Manifested from an eight-faceted sacred octahedron above Ivalice Citadel, Archon weighs every card "
            "placement against the High Tribunal's prism code. Its tri-laser verdict purges any formation that "
            "breaks harmonic parity."
        ),
        "lore_jp": (
            "イヴァリース城塞の上空に顕現した八面体プリズムの最高裁定者アルコン。あらゆるカード配置を天秤にかけ、"
            "調和の律法を乱す陣形へ三条の閃光レーザーによる審判を下す。"
        ),
    },
    {
        "card_id": "shinobi",
        "web_alias_id": "e_shinobi",
        "title": "Shinobi, Cyber-Umbra Phantom (Unevolved)",
        "title_evolved": "Shinobi, Cyber-Umbra Phantom (Evolved)",
        "original_title": "電脳の影刃・シノビ(進化前)",
        "original_title_evolved": "電脳の影刃・シノビ(進化後)",
        "set_code": "BP04",
        "slot_number": 21,
        "rarity": "SR",
        "theme": "Stealth",
        "faction": "Umbra-Stealth",
        "cost": 2,
        "up": 7, "right": 6, "down": 6, "left": 5,
        "art_path": "GeneratedArt/MasteredCards/e_shinobi.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_shinobi.png",
        "lore_en": (
            "Cloaked in hexagonal optical camouflage along the rain-drenched highways of Neo-Arcadia, Shinobi "
            "strikes from outside the enemy's 90-degree radar cone. By the time the telemetry alert chimes, "
            "the capture is already sealed."
        ),
        "lore_jp": (
            "ネオ・アルカディアの雨煙る高速道路を光学迷彩で疾走する電脳の影刃シノビ。"
            "敵の９０度索敵コーンの死角から音もなく忍び寄り、警報が鳴り響く前に捕獲を完遂する。"
        ),
    },
    {
        "card_id": "oracle",
        "web_alias_id": "h_oracle",
        "title": "Oracle, Lunar Tide Diviner (Unevolved)",
        "title_evolved": "Oracle, Lunar Tide Diviner (Evolved)",
        "original_title": "月光の星詠み・オラクル(進化前)",
        "original_title_evolved": "月光の星詠み・オラクル(進化後)",
        "set_code": "BP03",
        "slot_number": 11,
        "rarity": "UR",
        "theme": "Magic",
        "faction": "Chrono-Arcana",
        "cost": 3,
        "up": 7, "right": 7, "down": 8, "left": 7,
        "art_path": "GeneratedArt/MasteredCards/h_oracle.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_oracle.png",
        "lore_en": (
            "High priestess of the Silver Observatory who reads the reflections of future turns upon a mirror "
            "of lunar water. Her orbiting crescent ward bathes the southern sanctum in restorative astral tides."
        ),
        "lore_jp": (
            "白銀天文台の水鏡に未来のターンを映し出す月光の星詠みオラクル。"
            "周囲を巡る三日月の結界が満ちるとき、南方の聖域は癒やしと守護の星潮に包まれる。"
        ),
    },
    {
        "card_id": "valkyrie",
        "web_alias_id": "h_valkyrie",
        "title": "Valkyrie, Azure Sky Striker (Unevolved)",
        "title_evolved": "Valkyrie, Azure Sky Striker (Evolved)",
        "original_title": "天翔ける蒼翼・ヴァルキリー(進化前)",
        "original_title_evolved": "天翔ける蒼翼・ヴァルキリー(進化後)",
        "set_code": "BP01",
        "slot_number": 9,
        "rarity": "LG",
        "theme": "Tech",
        "faction": "Aether-Tech",
        "cost": 3,
        "up": 8, "right": 8, "down": 5, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/h_valkyrie.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_valkyrie.png",
        "lore_en": (
            "Spearhead of the Cloudsea Valkyria Wing, she dives from stratospheric carriers with twin afterburners "
            "blazing astral cyan. Her supersonic chevron volley commands both North and East skies simultaneously."
        ),
        "lore_jp": (
            "雲海ヴァルキリア航空団の先陣を切る蒼翼のストライカー。成層圏母艦からアフターバーナーを煌めかせて急降下し、"
            "北と東の空域を同時に制圧する超音速シェブロン斉射を放つ。"
        ),
    },
    {
        "card_id": "behemoth",
        "web_alias_id": "e_inferno",
        "title": "Behemoth, Caldera World-Crusher (Unevolved)",
        "title_evolved": "Behemoth, Caldera World-Crusher (Evolved)",
        "original_title": "熔岩の巨獣王・ベヒーモス(進化前)",
        "original_title_evolved": "熔岩の巨獣王・ベヒーモス(進化後)",
        "set_code": "BP05",
        "slot_number": 55,
        "rarity": "GR",
        "theme": "Divine",
        "faction": "Solaris-Divine",
        "cost": 4,
        "up": 7, "right": 7, "down": 5, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/e_inferno.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_inferno.png",
        "lore_en": (
            "Awakened beneath the Hellfire Foundry during the fifth Eternal Omen, Behemoth carries a molten reactor "
            "within its obsidian carapace. Every footfall paints pulsing artillery danger zones across the northern front."
        ),
        "lore_jp": (
            "第五の絶傑の胎動と共に獄炎熔鉱炉の深部から目覚めた巨獣王ベヒーモス。"
            "黒曜の甲殻に宿す熔岩炉が脈動するたび、北東の戦線に灼熱の砲撃危険域が刻まれる。"
        ),
    },
    {
        "card_id": "siren",
        "web_alias_id": "h_phoenix",
        "title": "Siren, Starlight Chorus Weaver (Unevolved)",
        "title_evolved": "Siren, Starlight Chorus Weaver (Evolved)",
        "original_title": "星海の歌姫・セイレーン(進化前)",
        "original_title_evolved": "星海の歌姫・セイレーン(進化後)",
        "set_code": "BP03",
        "slot_number": 44,
        "rarity": "SR",
        "theme": "Artisan",
        "faction": "CardCraft-Studio",
        "cost": 3,
        "up": 9, "right": 8, "down": 5, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/h_phoenix.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/h_phoenix.png",
        "lore_en": (
            "Her aria echoes across the Astral Sea, weaving golden phoenix feathers and vibrant watercolor cadences "
            "into living protective wards. Allies who hear her chorus surge with renewed directional resonance."
        ),
        "lore_jp": (
            "星海に響き渡るアリアで黄金の鳳凰羽と水彩の旋律を紡ぎ合わせる歌姫セイレーン。"
            "その歌声に包まれた味方ユニットは、北東へと伸びる不死鳥の翼撃で敵陣を魅了する。"
        ),
    },
    {
        "card_id": "leviathan",
        "web_alias_id": "e_colossus",
        "title": "Leviathan, Rift-Tide Mecha Wyrm (Unevolved)",
        "title_evolved": "Leviathan, Rift-Tide Mecha Wyrm (Evolved)",
        "original_title": "次元裂きの海竜機・リヴァイアサン(進化前)",
        "original_title_evolved": "次元裂きの海竜機・リヴァイアサン(進化後)",
        "set_code": "BP05",
        "slot_number": 88,
        "rarity": "SL",
        "theme": "Tech",
        "faction": "Aether-Tech",
        "cost": 4,
        "up": 6, "right": 8, "down": 5, "left": 6,
        "art_path": "GeneratedArt/MasteredCards/e_colossus.png",
        "portrait_fallback": "GeneratedArt/MasteredCards/e_colossus.png",
        "lore_en": (
            "Coiling through the dimensional breach between Orbital Mecha Bay and the Abyssal Trench, Leviathan "
            "charges its emerald spine-coils to unleash a piercing Eastward rail-plasma torrent."
        ),
        "lore_jp": (
            "軌道メカベイと深淵海溝を繋ぐ次元の裂け目を泳ぐ海竜機リヴァイアサン。"
            "背びれの翠緑リアクターを臨界まで充填し、東方の戦線を一閃で貫くプラズマ奔流を放つ。"
        ),
    },
]


# =============================================================================
# 3. 60 SET 1 CARDS JAPANESE TITLES & BOOSTER PACK ASSIGNMENTS ([BP01]..[BP05])
# =============================================================================
SET1_60_BILINGUAL_TABLE: List[Tuple[str, str, str, str, str, int, str, str, Tuple[int, int, int, int], int]] = [
    # ── 14 Canonical Core Roster Cards (10 PROJECT CF + 4 CardCraft Studio) ──
    ("cf_01_mystic_mage", "Mystic Mage", "秘術の星導師・ミスティックメイジ", "BP01", "LG", 3, "Magic", "Chrono-Arcana", (5, 6, 7, 3), 3),
    ("cf_02_mech_knight", "Mech Knight", "鋼鉄の機甲騎士・メックナイト", "BP01", "SR", 4, "Tech", "Aether-Tech", (8, 5, 4, 6), 3),
    ("cf_03_celestial_guardian", "Celestial Guardian", "天界の守護神・セレスティアルガーディアン", "BP01", "UR", 5, "Divine", "Solaris-Divine", (6, 7, 9, 4), 4),
    ("cf_04_shadow_assassin", "Shadow Assassin", "宵闇の暗殺者・シャドウアサシン", "BP01", "SR", 6, "Stealth", "Umbra-Stealth", (7, 4, 5, 8), 2),
    ("cf_05_elemental_sprite", "Elemental Sprite", "精霊の風妖精・エレメンタルスプライト", "BP01", "GR", 7, "Magic", "Chrono-Arcana", (3, 9, 4, 6), 2),
    ("cf_06_galactic_explorer", "Galactic Explorer", "星海の開拓者・ギャラクティックエクスプローラー", "BP01", "SR", 8, "Tech", "Aether-Tech", (7, 8, 6, 5), 3),
    ("cf_07_clockwork_sorcerer", "Clockwork Sorcerer", "機械仕掛けの魔導師・クロックワークソーサラー", "BP01", "LG", 10, "Magic", "Chrono-Arcana", (4, 5, 8, 7), 4),
    ("cf_08_phoenix_guardian", "Phoenix Guardian", "不死鳥の聖衛・フェニックスガーディアン", "BP01", "UR", 11, "Divine", "Solaris-Divine", (9, 4, 7, 6), 4),
    ("cf_09_cyber_ninja", "Cyber Ninja", "電脳の忍・サイバーニンジャ", "BP01", "SR", 12, "Stealth", "Umbra-Stealth", (6, 7, 5, 8), 2),
    ("cf_10_lunar_oracle", "Lunar Oracle", "月輪の神託者・ルナオラクル", "BP01", "LG", 13, "Divine", "Solaris-Divine", (7, 9, 6, 4), 3),
    ("cc_01_sketching", "Sketching", "創世の鉛筆画・スケッチング", "BP01", "BR", 14, "Artisan", "CardCraft-Studio", (4, 5, 5, 6), 1),
    ("cc_02_concept_art", "Concept Art", "幻想の設計図・コンセプトアート", "BP01", "GR", 16, "Artisan", "CardCraft-Studio", (6, 7, 7, 8), 2),
    ("cc_03_storyboard", "Storyboard", "物語の絵コンテ・ストーリーボード", "BP01", "BR", 17, "Artisan", "CardCraft-Studio", (5, 6, 6, 5), 1),
    ("cc_04_animatic", "Animatic", "躍動の律動画・アニマティック", "BP01", "GR", 18, "Artisan", "CardCraft-Studio", (7, 8, 8, 7), 3),

    # ── 46 Set 1 Expansion Cards (Distributed Across BP01 .. BP05) ──
    ("s1_15_aether_vanguard", "Aether Vanguard", "蒼天の先遣騎兵・エーテルヴァンガード", "BP01", "SR", 19, "Tech", "Aether-Tech", (7, 6, 5, 6), 2),
    ("s1_16_chrono_sentinel", "Chrono Sentinel", "時守の真鍮衛士・クロノセンチネル", "BP01", "GR", 20, "Tech", "Aether-Tech", (5, 6, 8, 5), 2),
    ("s1_17_solaris_paladin", "Solaris Paladin", "暁光の聖堂騎士・ソラリスパラディン", "BP01", "SR", 21, "Divine", "Solaris-Divine", (8, 6, 7, 5), 3),
    ("s1_18_void_stalker", "Void Stalker", "虚空の追跡者・ヴォイドストーカー", "BP01", "GR", 22, "Stealth", "Umbra-Stealth", (6, 5, 4, 9), 2),
    ("s1_19_verdant_colossus", "Verdant Colossus", "深緑の巨神兵・ヴァーダントコロッサス", "BP02", "SR", 1, "Divine", "Solaris-Divine", (7, 4, 9, 5), 3),
    ("s1_20_nebula_corsair", "Nebula Corsair", "星雲の空賊船長・ネビュラコルセア", "BP02", "GR", 2, "Stealth", "Umbra-Stealth", (6, 8, 6, 7), 3),
    ("s1_21_brass_automaton", "Brass Automaton", "真鍮の自動人形・ブラスオートマトン", "BP02", "BR", 3, "Tech", "Aether-Tech", (8, 4, 6, 7), 2),
    ("s1_22_aegis_colossus", "Aegis Colossus", "天盾の巨神機・イージスコロッサス", "BP02", "LG", 4, "Tech", "Aether-Tech", (9, 5, 7, 8), 4),
    ("s1_23_cinder_valkyrie", "Cinder Valkyrie", "燼火の戦乙女・シンダーヴァルキリー", "BP02", "SR", 5, "Divine", "Solaris-Divine", (8, 7, 5, 6), 3),
    ("s1_24_ghost_operative", "Ghost Operative", "亡霊の特務工作員・ゴーストオペレーティブ", "BP02", "SR", 6, "Stealth", "Umbra-Stealth", (5, 7, 6, 8), 3),
    ("s1_25_crescent_archon", "Crescent Archon", "弦月の高位司祭・クレセントアルコン", "BP02", "LG", 7, "Divine", "Solaris-Divine", (6, 8, 8, 5), 3),
    ("s1_26_keyframe_sculptor", "Keyframe Sculptor", "原画の閃光彫師・キーフレームスカルプター", "BP02", "GR", 9, "Artisan", "CardCraft-Studio", (6, 7, 6, 8), 3),
    ("s1_27_runic_alchemist", "Runic Alchemist", "刻印の錬金術師・ルーニックアルケミスト", "BP02", "GR", 10, "Magic", "Chrono-Arcana", (4, 6, 7, 7), 2),
    ("s1_28_railgun_dragoons", "Railgun Dragoons", "電磁砲の竜騎兵・レールガンドラグーン", "BP02", "SR", 11, "Tech", "Aether-Tech", (9, 7, 4, 5), 3),
    ("s1_29_seraphim_arbiter", "Seraphim Arbiter", "熾天の律法裁定官・セラフィムアービター", "BP02", "UR", 12, "Divine", "Solaris-Divine", (7, 7, 8, 6), 4),
    ("s1_30_nightshade_kunoichi", "Nightshade Kunoichi", "夜影の紅くノ一・ナイトシェイドクノイチ", "BP02", "GR", 13, "Stealth", "Umbra-Stealth", (7, 6, 4, 8), 2),
    ("s1_31_briar_thornweaver", "Briar Thornweaver", "荊冠の呪術織師・ブライアソーンウィーバー", "BP03", "GR", 1, "Magic", "Chrono-Arcana", (5, 7, 7, 6), 2),
    ("s1_32_pulsar_navigator", "Pulsar Navigator", "脈動星の航海士・パルサーナビゲーター", "BP03", "SR", 2, "Magic", "Chrono-Arcana", (6, 8, 7, 5), 3),
    ("s1_33_cogwheel_artificer", "Cogwheel Artificer", "歯車工房の匠師・コグホイールアーティフィサー", "BP03", "GR", 3, "Artisan", "CardCraft-Studio", (5, 6, 6, 8), 2),
    ("s1_34_magma_behemoth", "Magma Behemoth", "火口の熔岩巨獣・マグマベヒーモス", "BP03", "SR", 4, "Divine", "Solaris-Divine", (9, 5, 8, 4), 3),
    ("s1_35_neural_netrunner", "Neural Netrunner", "神経網の潜入者・ニューラルネットランナー", "BP03", "SR", 5, "Stealth", "Umbra-Stealth", (6, 6, 5, 9), 3),
    ("s1_36_eclipse_sovereign", "Eclipse Sovereign", "皆既日食の覇王・エクリプスソヴリン", "BP03", "LG", 6, "Divine", "Solaris-Divine", (8, 8, 7, 5), 4),
    ("s1_37_voxel_architect", "Voxel Architect", "立体格子の建築家・ボクセルアーキテクト", "BP03", "SR", 7, "Artisan", "CardCraft-Studio", (7, 6, 7, 7), 3),
    ("s1_38_astral_spellblade", "Astral Spellblade", "星辰の魔剣士・アストラルスペルブレイド", "BP03", "GR", 8, "Magic", "Chrono-Arcana", (7, 7, 6, 6), 3),
    ("s1_39_bastion_dreadnought", "Bastion Dreadnought", "要塞装甲の超重機・バスティオンドレッドノート", "BP03", "SR", 9, "Tech", "Aether-Tech", (8, 4, 9, 5), 3),
    ("s1_40_luminary_hierophant", "Luminary Hierophant", "聖光の教皇導師・ルミナリーハイエロファント", "BP03", "GR", 10, "Divine", "Solaris-Divine", (5, 8, 8, 6), 3),
    ("s1_41_abyssal_reaver", "Abyssal Reaver", "奈落の魂狩り・アビサルリーヴァー", "BP04", "GR", 1, "Stealth", "Umbra-Stealth", (8, 5, 5, 7), 2),
    ("s1_42_spore_myconid", "Spore Myconid", "胞子森の菌糸王・スポアマイコニド", "BP04", "BR", 2, "Magic", "Chrono-Arcana", (4, 6, 8, 7), 2),
    ("s1_43_hyperion_starcruiser", "Hyperion Starcruiser", "銀河旗艦・ハイペリオンスタークルーザー", "BP04", "LG", 3, "Tech", "Aether-Tech", (8, 8, 6, 6), 4),
    ("s1_44_aether_chronomancer", "Aether Chronomancer", "砂時計の霊気導師・エーテルクロノマンサー", "BP04", "SR", 4, "Magic", "Chrono-Arcana", (6, 5, 8, 8), 3),
    ("s1_45_hellfire_drake", "Hellfire Drake", "業火の飛竜・ヘルファイアドレイク", "BP04", "GR", 5, "Divine", "Solaris-Divine", (8, 7, 6, 5), 3),
    ("s1_46_mirage_infiltrator", "Mirage Infiltrator", "陽炎の潜入工作員・ミラージュインフィルトレイター", "BP04", "GR", 6, "Stealth", "Umbra-Stealth", (5, 6, 7, 8), 2),
    ("s1_47_selene_valkyrie", "Selene Valkyrie", "銀月の弓戦乙女・セレーネヴァルキリー", "BP04", "SR", 8, "Divine", "Solaris-Divine", (7, 9, 6, 6), 3),
    ("s1_48_cel_shader_virtuoso", "Cel Shader Virtuoso", "色彩階調の巨匠・セルシェーダーヴィルトゥオーゾ", "BP04", "SR", 9, "Artisan", "CardCraft-Studio", (6, 7, 8, 7), 3),
    ("s1_49_kai_nakamura_striker", "Kai Nakamura", "紅きマフラーの疾風・カイ", "BP04", "SL", 10, "Tech", "Aether-Tech", (8, 7, 6, 7), 4),
    ("s1_50_mnemosyne_ninetails", "Mnemosyne Fox", "記憶を紡ぐ九尾・ムネモシュネ", "BP04", "LG", 11, "Magic", "Chrono-Arcana", (7, 8, 8, 6), 4),
    ("s1_51_luna_tarot_weaver", "Luna Tarot Weaver", "星辰タロットの紡ぎ手・ルナ", "BP05", "LG", 1, "Magic", "Chrono-Arcana", (6, 8, 7, 8), 4),
    ("s1_52_dr_rina_asakura", "Dr. Rina Asakura", "機巧研究所の主席博士・アサクラリナ", "BP05", "LG", 2, "Tech", "Aether-Tech", (5, 7, 9, 7), 4),
    ("s1_53_judge_cid_lawkeeper", "Judge Cid Lawkeeper", "最高法廷の審判長・ジャッジシド", "BP05", "SL", 3, "Divine", "Solaris-Divine", (8, 6, 8, 6), 4),
    ("s1_54_staccs_crown_emperor", "STACCS Crown Emperor", "天頂階層の戴冠帝・スタックスエンペラー", "BP05", "LG", 4, "Tech", "Aether-Tech", (9, 6, 7, 7), 4),
    ("s1_55_breach_leviathan_mech", "Breach Leviathan Mech", "次元防衛の巨神機・ブリーチリヴァイアサン", "BP05", "SR", 5, "Tech", "Aether-Tech", (8, 5, 8, 7), 3),
    ("s1_56_dicevaders_chronobudge", "Chrono Budge Commander", "時間連鎖の司令官・クロノバッジコマンダー", "BP05", "SR", 6, "Magic", "Chrono-Arcana", (7, 8, 6, 8), 3),
    ("s1_57_solid_eye_snake_hound", "Solid Eye Operative", "隻眼の戦術工作員・ソリッドアイオペレーティブ", "BP05", "LG", 7, "Stealth", "Umbra-Stealth", (7, 6, 7, 9), 4),
    ("s1_58_mana_sanctuary_dryad", "Mana Sanctuary Dryad", "世界樹の聖域精霊・マナドライアド", "BP05", "LG", 8, "Divine", "Solaris-Divine", (6, 8, 9, 6), 4),
    ("s1_59_neo_arcadia_zero_saber", "Neo Arcadia Cyber-Elf", "蒼き光剣の電脳妖精・ゼロセイバー", "BP05", "SL", 9, "Tech", "Aether-Tech", (9, 7, 5, 8), 4),
    ("s1_60_omega_chronos_prime", "Omega Chronos Prime", "終焉と創世の時空神・オメガクロノスプライム", "BP05", "UR", 10, "Artisan", "CardCraft-Studio", (10, 9, 9, 10), 5),
]

# Additional campaign expansion IDs from `synapse_set1_campaign_expansion.py` so every ID resolves
CAMPAIGN_EXPANSION_ALIASES: Dict[str, Tuple[str, str]] = {
    "s1_16_railgun_dragoon": ("s1_28_railgun_dragoons", "電磁砲の竜騎兵・レールガンドラグーン"),
    "s1_17_servo_bastion_mk2": ("s1_39_bastion_dreadnought", "重装防壁機・サーボバスティオン弐式"),
    "s1_18_orbital_relay_drone": ("s1_20_nebula_corsair", "軌道中継機・オービタルリレードローン"),
    "s1_19_plasma_halberdier": ("s1_15_aether_vanguard", "蒼閃の斧槍兵・プラズマハルバーディア"),
    "s1_20_chronos_hover_tank": ("s1_16_chrono_sentinel", "時空浮遊戦車・クロノスホバータンク"),
    "s1_21_nanoforge_engineer": ("s1_21_brass_automaton", "ナノ炉の機工技師・ナノフォージエンジニア"),
    "s1_22_tesla_siege_walker": ("s1_22_aegis_colossus", "電磁攻城機・テスラシージウォーカー"),
    "s1_23_valkyrie_interceptor": ("s1_23_cinder_valkyrie", "蒼空の迎撃機・ヴァルキリーインターセプター"),
    "s1_24_rex_metal_colossus": ("s1_55_breach_leviathan_mech", "超重核砲機・レックスメタルコロッサス"),
    "s1_25_astral_scholar": ("s1_25_crescent_archon", "星律の学徒・アストラルスカラー"),
    "s1_26_void_weaver": ("s1_26_keyframe_sculptor", "虚空の重力織師・ヴォイドウィーバー"),
    "s1_27_pendulum_alchemist": ("s1_27_runic_alchemist", "振り子の錬金術師・ペンデュラムアルケミスト"),
    "s1_28_rift_archon": ("s1_28_railgun_dragoons", "次元裂きの高位導師・リフトアルコン"),
    "s1_29_spellblade_duelist": ("s1_38_astral_spellblade", "魔剣の決闘士・スペルブレイドデュエリスト"),
    "s1_30_starlight_diviner": ("s1_32_pulsar_navigator", "星明かりの占星術師・スターライトディヴァイナー"),
    "s1_31_aeon_hourglass_mage": ("s1_44_aether_chronomancer", "永劫砂時計の魔導師・アイオーンメイジ"),
    "s1_32_grimoire_sentinel": ("s1_31_briar_thornweaver", "魔導書の守護兵・グリモワールセンチネル"),
    "s1_33_chronos_grand_magus": ("s1_60_omega_chronos_prime", "時空大魔導師・クロノスグランドメイガス"),
    "s1_34_dawn_templar": ("s1_17_solaris_paladin", "暁の聖堂騎士・ドーンテンプラー"),
    "s1_35_seraphic_lancer": ("s1_29_seraphim_arbiter", "熾天の飛槍騎・セラフィックランサー"),
    "s1_36_aegis_hierophant": ("s1_40_luminary_hierophant", "聖盾の教皇・イージスハイエロファント"),
    "s1_37_radiant_valkyrie": ("s1_47_selene_valkyrie", "光輪の戦乙女・ラディアントヴァルキリー"),
    "s1_38_solaris_inquisitor": ("s1_53_judge_cid_lawkeeper", "陽炎の異端審問官・ソラリスインクイジター"),
    "s1_39_eclipse_paladin": ("s1_36_eclipse_sovereign", "日食の聖騎士・エクリプスパラディン"),
    "s1_40_choir_chronicle_bard": ("s1_58_mana_sanctuary_dryad", "聖歌年代記の吟遊詩人・クワイアバード"),
    "s1_41_archangel_judicator": ("s1_29_seraphim_arbiter", "大天使の審判者・アークエンジェルジュディケイター"),
    "s1_42_sunforge_colossus": ("s1_34_magma_behemoth", "太陽炉の巨神像・サンフォージコロッサス"),
    "s1_43_whisper_infiltrator": ("s1_18_void_stalker", "静寂の潜入者・ウィスパーインフィルトレイター"),
    "s1_44_kunoichi_mirage": ("s1_30_nightshade_kunoichi", "幻影のくノ一・クノイチミラージュ"),
    "s1_45_optic_camo_sniper": ("s1_24_ghost_operative", "光学迷彩の狙撃手・オプティックカモスナイパー"),
    "s1_46_smoke_veil_saboteur": ("s1_46_mirage_infiltrator", "煙幕の工作兵・スモークヴェールサボタージュ"),
    "s1_47_phantom_cqc_operative": ("s1_57_solid_eye_snake_hound", "幻影格闘の特務兵・ファントムオペレーティブ"),
    "s1_48_nightshade_stalker": ("s1_41_abyssal_reaver", "夜影の追跡兵・ナイトシェイドストーカー"),
    "s1_49_zero_pulse_hacker": ("s1_35_neural_netrunner", "零脈の電脳黒客・ゼロパルスハッカー"),
    "s1_50_obsidian_ronin": ("s1_59_neo_arcadia_zero_saber", "黒曜の浪人剣士・オブシディアンロウニン"),
    "s1_51_eclipse_wire_agent": ("s1_20_nebula_corsair", "宵闇の索条工作員・エクリプスワイヤーエージェント"),
    "s1_52_viper_solid_eye_prime": ("s1_57_solid_eye_snake_hound", "隻眼の蛇王・ヴァイパーソリッドアイプライム"),
    "s1_53_ink_brush_calligrapher": ("s1_48_cel_shader_virtuoso", "墨筆の書道師・インクブラシカリグラファー"),
    "s1_54_halftone_pop_stylist": ("s1_33_cogwheel_artificer", "網点色彩の造形師・ハーフトーンポップスタイリスト"),
    "s1_55_sakuga_key_animator": ("s1_26_keyframe_sculptor", "神作画の原画師・サクガキーアニメーター"),
    "s1_56_parchment_cartographer": ("s1_42_spore_myconid", "羊皮紙の地図師・パーチメントカルトグラファー"),
    "s1_57_voxel_sculptor_hi3d": ("s1_37_voxel_architect", "立体格子の彫刻師・ボクセルスカルプター"),
    "s1_58_palette_harmonizer": ("s1_51_luna_tarot_weaver", "色彩調和の調律師・パレットハーモナイザー"),
    "s1_59_atelier_master_director": ("s1_52_dr_rina_asakura", "工房の総監督・アトリエマスターディレクター"),
}


def compute_collector_sha256(
    card_id: str,
    original_title: str,
    card_game: str,
    version: str,
    original_version: str,
    card_number: str,
    rarity: str,
    evolution_state: str,
) -> str:
    """Computes a deterministic 64-character SHA-256 hex digest over canonical collector fields."""
    canonical = "|".join(
        [
            card_id.strip(),
            original_title.strip(),
            card_game.strip(),
            version.strip(),
            original_version.strip(),
            card_number.strip(),
            rarity.strip(),
            evolution_state.strip(),
        ]
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_unity_meta_guid(rel_posix_path: str) -> str:
    normalized = rel_posix_path.strip().replace("\\", "/").lstrip("/")
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def write_unity_text_asset_meta(target_file: Path) -> Path:
    rel_posix = target_file.relative_to(PROJECT_ROOT).as_posix()
    guid = compute_unity_meta_guid(rel_posix)
    meta_path = Path(str(target_file) + ".meta")
    meta_content = (
        f"fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        f"TextScriptImporter:\n"
        f"  externalObjects: {{}}\n"
        f"  userData: \n"
        f"  assetBundleName: \n"
        f"  assetBundleVariant: \n"
    )
    meta_path.write_text(meta_content, encoding="utf-8")
    return meta_path


class SynapseCardIdentificationCatalog:
    """
    Sovereign Bilingual Card Identification & Collector Taxonomy Engine (`[BP01]`–`[BP05]`).
    Generates, validates, queries, and exports the full bilingual collector identification
    database for Shadowverse EVOLVE / CARDFRONT: Cradle of Echoes.
    """

    REFERENCE_ARCHETYPE_ID = "bp05_110_rosa_unevolved"
    REFERENCE_ARCHETYPE_EVOLVED_ID = "bp05_110_rosa_evolved"
    BOOSTER_SETS = BOOSTER_SETS
    RARITY_TIERS = RARITY_TIERS

    def __init__(self) -> None:
        self._cards_list: List[Dict[str, Any]] = []
        self._cards_by_id: Dict[str, Dict[str, Any]] = {}
        self._lookup_index: Dict[str, Dict[str, Any]] = {}
        self._set1_60_cards: List[Dict[str, Any]] = []
        self._hero_boss_16_cards: List[Dict[str, Any]] = []
        self._core_14_cards: List[Dict[str, Any]] = []
        self._build_all_entries()

    # -------------------------------------------------------------------------
    # Core Entry Construction
    # -------------------------------------------------------------------------
    def _build_collector_entry(
        self,
        *,
        card_id: str,
        title: str,
        original_title: str,
        card_game: str,
        card_game_primary: str,
        card_game_interop: str,
        set_code: str,
        card_number: str,
        rarity: str,
        evolution_state: str,
        evolution_state_en: str,
        up: int,
        right: int,
        down: int,
        left: int,
        theme: str,
        faction: str,
        cost: int,
        art_path: str,
        lore_en: str,
        lore_jp: str,
        serial_index: int,
        category: str,
        original_title_evolved: Optional[str] = None,
        evolved_counterpart: Optional[Dict[str, Any]] = None,
        unevolved_base_card_id: Optional[str] = None,
        extra_aliases: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        set_meta = BOOSTER_SETS[set_code]
        rarity_meta = RARITY_TIERS[rarity]
        atelier_meta = FACTION_ATELIER_NOTES.get(theme, FACTION_ATELIER_NOTES["Tech"])

        version = set_meta["version"]
        original_version = set_meta["original_version"]

        sha256_id = compute_collector_sha256(
            card_id=card_id,
            original_title=original_title,
            card_game=card_game,
            version=version,
            original_version=original_version,
            card_number=card_number,
            rarity=rarity,
            evolution_state=evolution_state,
        )

        serial_mint = f"#{serial_index:04d} / 0500"
        atelier_direction_obj = {
            "faction_chromatic_harmony": atelier_meta["palette_hex"],
            "morphological_brushwork_and_silhouette": atelier_meta["morphology"],
            "parallax_25d_and_foil_layering": atelier_meta["foil_depth"],
            "card_frame_craft": (
                f"Luxury {rarity_meta['code']} ({rarity_meta['rarity_full_en']} · {rarity_meta['rarity_full_jp']}) "
                f"collector frame with top-left octagonal cost gem ({cost}), directional compass crest "
                f"(N:{up} E:{right} S:{down} W:{left}), smoked-glass bilingual nameplate, and embossed {card_number} stamp."
            ),
            "zero_living_artist_names": True,
        }
        collector_provenance_obj = {
            "edition": "1st Edition · 初版",
            "serial_mint": serial_mint,
            "foil_treatment": rarity_meta["foil_treatment"],
            "full_bleed_resolution": "600x800 (3:4 Portrait)",
            "content_bounds": [0, 0, 600, 800],
            "sha256_collector_id": sha256_id,
        }

        identification_block = {
            "original_title": original_title,
            "original_title_evolved": original_title_evolved or original_title.replace("(進化前)", "(進化後)"),
            "title": title,
            "card_game": card_game,
            "card_game_primary": card_game_primary,
            "card_game_interop": card_game_interop,
            "version": version,
            "original_version": original_version,
            "card_number": card_number,
            "rarity": rarity,
            "rarity_full_en": rarity_meta["rarity_full_en"],
            "rarity_full_jp": rarity_meta["rarity_full_jp"],
            "evolution_state": evolution_state,
            "evolution_state_en": evolution_state_en,
            "set_code": set_code,
            "sha256_collector_id": sha256_id,
            "lore_en": lore_en,
            "lore_jp": lore_jp,
            "atelier_art_direction": atelier_direction_obj,
            "collector_provenance": collector_provenance_obj,
        }
        if evolved_counterpart is not None:
            identification_block["evolved_counterpart"] = evolved_counterpart
        if unevolved_base_card_id is not None:
            identification_block["unevolved_base_card_id"] = unevolved_base_card_id

        entry: Dict[str, Any] = {
            "card_id": card_id,
            "id": card_id,
            "category": category,
            "original_title": original_title,
            "original_title_evolved": original_title_evolved or original_title.replace("(進化前)", "(進化後)"),
            "title": title,
            "name": title,
            "card_game": card_game,
            "card_game_primary": card_game_primary,
            "card_game_interop": card_game_interop,
            "version": version,
            "original_version": original_version,
            "set_code": set_code,
            "card_number": card_number,
            "rarity": rarity,
            "rarity_full_en": rarity_meta["rarity_full_en"],
            "rarity_full_jp": rarity_meta["rarity_full_jp"],
            "evolution_state": evolution_state,
            "evolution_state_en": evolution_state_en,
            "up": int(up),
            "right": int(right),
            "down": int(down),
            "left": int(left),
            "stats": {
                "up": int(up),
                "right": int(right),
                "down": int(down),
                "left": int(left),
            },
            "nesw": [int(up), int(right), int(down), int(left)],
            "theme": theme,
            "themes": [theme, faction],
            "faction": faction,
            "cost": int(cost),
            "art_path": art_path,
            "lore_en": lore_en,
            "lore_jp": lore_jp,
            "atelier_art_direction": atelier_direction_obj,
            "collector_provenance": collector_provenance_obj,
            "sha256_collector_id": sha256_id,
            "identification": identification_block,
            "aliases": list(extra_aliases or []),
        }
        if evolved_counterpart is not None:
            entry["evolved_counterpart"] = evolved_counterpart
        if unevolved_base_card_id is not None:
            entry["unevolved_base_card_id"] = unevolved_base_card_id
        return entry

    def _register_entry(self, entry: Dict[str, Any]) -> None:
        cid = entry["card_id"]
        if cid not in self._cards_by_id:
            self._cards_list.append(entry)
        self._cards_by_id[cid] = entry
        self._lookup_index[cid.lower()] = entry
        self._lookup_index[entry["card_number"].lower()] = entry
        self._lookup_index[entry["card_number"].split()[0].lower()] = entry
        self._lookup_index[entry["original_title"]] = entry
        self._lookup_index[entry["title"].lower()] = entry
        for alias in entry.get("aliases", []):
            if alias:
                self._lookup_index[alias.lower()] = entry
                if alias not in self._cards_by_id:
                    self._cards_by_id[alias] = entry

    def _build_all_entries(self) -> None:
        serial_counter = 1

        # =====================================================================
        # A. EXACT REFERENCE ARCHETYPE ENTRY (`BP05-110 SR` & `BP05-110EV SR`)
        # =====================================================================
        rosa_evo_lore_en = (
            "When the fifth Eternal Omen tolls across the Cloudsea Sanctuary, Rosa's six mechanized brass-and-emerald "
            "pinions unfurl in full Astral Overdrive. Every clockwork songbird in the sky harmonizes with her heart, "
            "turning her flight path into an unbreakable 3x3 sanctuary ward."
        )
        rosa_evo_lore_jp = (
            "第五の絶傑の鐘音が雲海聖域に響き渡るとき、ローザの六枚の機構翼は翠緑と黄金のオーバードライブへと展開する。"
            "空を舞うすべての機械小鳥がその鼓動と共鳴し、３×３の戦盤に不落の天翔ける聖域を築き上げる。"
        )
        rosa_evolved = self._build_collector_entry(
            card_id=self.REFERENCE_ARCHETYPE_EVOLVED_ID,
            title="Rosa, Mechanized Wing Maiden (Evolved)",
            original_title="機構翼の少女・ローザ(進化後)",
            original_title_evolved="機構翼の少女・ローザ(進化後)",
            card_game="Shadowverse EVOLVE / CARDFRONT Collector Standard",
            card_game_primary="Shadowverse EVOLVE",
            card_game_interop="CARDFRONT: Cradle of Echoes",
            set_code="BP05",
            card_number="BP05-110EV SR",
            rarity="SR",
            evolution_state="進化後",
            evolution_state_en="Evolved",
            up=9,
            right=9,
            down=8,
            left=8,
            theme="Tech",
            faction="Aether-Tech",
            cost=3,
            art_path="GeneratedArt/HeroCards/hero_01_kaelen_v2.png",
            lore_en=rosa_evo_lore_en,
            lore_jp=rosa_evo_lore_jp,
            serial_index=serial_counter + 1,
            category="reference_archetype_evolved",
            unevolved_base_card_id=self.REFERENCE_ARCHETYPE_ID,
            extra_aliases=["rosa_evolved", "bp05-110ev", "bp05-110ev sr", "機構翼の少女・ローザ(進化後)"],
        )

        rosa_base_lore_en = (
            "\"They say these brass pinions are too small for the heavens... yet just feeling the sunset breeze "
            "makes my heart soar!\" — Rosa, calibrating her clockwork feather wings atop the Sky-Citadel terrace "
            "as a golden mechanical songbird alights upon her fingertips."
        )
        rosa_base_lore_jp = (
            "「この小さな真鍮の翼じゃ、まだ蒼穹には届かないって言うけれど……夕暮れの風を感じるだけで、"
            "こんなにも胸が高鳴るの！」――浮遊城塞のテラスで金色の機械小鳥を指先に留め、機構翼の少女・ローザは微笑む。"
        )
        rosa_unevolved = self._build_collector_entry(
            card_id=self.REFERENCE_ARCHETYPE_ID,
            title="Rosa, Mechanized Wing Maiden (Unevolved)",
            original_title="機構翼の少女・ローザ(進化前)",
            original_title_evolved="機構翼の少女・ローザ(進化後)",
            card_game="Shadowverse EVOLVE / CARDFRONT Collector Standard",
            card_game_primary="Shadowverse EVOLVE",
            card_game_interop="CARDFRONT: Cradle of Echoes",
            set_code="BP05",
            card_number="BP05-110 SR",
            rarity="SR",
            evolution_state="進化前",
            evolution_state_en="Unevolved",
            up=7,
            right=8,
            down=6,
            left=7,
            theme="Tech",
            faction="Aether-Tech",
            cost=3,
            art_path="GeneratedArt/HeroCards/hero_01_kaelen_v2.png",
            lore_en=rosa_base_lore_en,
            lore_jp=rosa_base_lore_jp,
            serial_index=serial_counter,
            category="reference_archetype_unevolved",
            evolved_counterpart=rosa_evolved,
            extra_aliases=["rosa", "rosa_unevolved", "bp05-110", "bp05-110 sr", "機構翼の少女・ローザ(進化前)"],
        )
        self._register_entry(rosa_unevolved)
        self._register_entry(rosa_evolved)
        serial_counter += 2

        # =====================================================================
        # B. ALL 16 PLAYABLE HERO & BOSS CARDS (`kaelen`..`leviathan` + `h_*`/`e_*`)
        # =====================================================================
        for hb in HERO_BOSS_16_SPECS:
            cid = hb["card_id"]
            web_id = hb["web_alias_id"]
            set_code = hb["set_code"]
            slot_num = hb["slot_number"]
            rarity = hb["rarity"]
            base_num = f"{set_code}-{slot_num:03d} {rarity}"
            evo_num = f"{set_code}-{slot_num:03d}EV {rarity}"

            u, r, d, l = hb["up"], hb["right"], hb["down"], hb["left"]
            eu = min(10, u + 1)
            er = min(10, r + 1)
            ed = min(10, d + 1)
            el = min(10, l + 1)

            evo_card_id = f"{cid}_evolved"
            evo_entry = self._build_collector_entry(
                card_id=evo_card_id,
                title=hb["title_evolved"],
                original_title=hb["original_title_evolved"],
                original_title_evolved=hb["original_title_evolved"],
                card_game="CARDFRONT: Cradle of Echoes (Shadowverse EVOLVE Standard)",
                card_game_primary="Shadowverse EVOLVE",
                card_game_interop="CARDFRONT: Cradle of Echoes",
                set_code=set_code,
                card_number=evo_num,
                rarity=rarity,
                evolution_state="進化後",
                evolution_state_en="Evolved",
                up=eu,
                right=er,
                down=ed,
                left=el,
                theme=hb["theme"],
                faction=hb["faction"],
                cost=hb["cost"],
                art_path=hb["art_path"],
                lore_en=hb["lore_en"] + " [Evolved Awakening: +1 All-Directional Resonance across the 3x3 Sanctum.]",
                lore_jp=hb["lore_jp"] + "【進化後覚醒：３×３聖域の四方ランクがすべて＋１共鳴上昇】",
                serial_index=serial_counter + 1,
                category="hero_boss_16_evolved",
                unevolved_base_card_id=cid,
                extra_aliases=[f"{web_id}_evolved"],
            )

            aliases = [web_id]
            if "alt_card_number" in hb:
                aliases.append(hb["alt_card_number"])

            base_entry = self._build_collector_entry(
                card_id=cid,
                title=hb["title"],
                original_title=hb["original_title"],
                original_title_evolved=hb["original_title_evolved"],
                card_game="CARDFRONT: Cradle of Echoes (Shadowverse EVOLVE Standard)",
                card_game_primary="Shadowverse EVOLVE",
                card_game_interop="CARDFRONT: Cradle of Echoes",
                set_code=set_code,
                card_number=base_num,
                rarity=rarity,
                evolution_state="進化前",
                evolution_state_en="Unevolved",
                up=u,
                right=r,
                down=d,
                left=l,
                theme=hb["theme"],
                faction=hb["faction"],
                cost=hb["cost"],
                art_path=hb["art_path"],
                lore_en=hb["lore_en"],
                lore_jp=hb["lore_jp"],
                serial_index=serial_counter,
                category="hero_boss_16",
                evolved_counterpart=evo_entry,
                extra_aliases=aliases,
            )
            base_entry["web_card_id"] = web_id
            self._register_entry(base_entry)
            self._register_entry(evo_entry)
            self._hero_boss_16_cards.append(base_entry)
            serial_counter += 2

        # =====================================================================
        # C. ALL 60 SET 1 CARDS (14 CANONICAL CORE ROSTER + 46 SET 1 EXPANSION)
        # =====================================================================
        web_base_16_ids = [
            "h_archangel", "h_phoenix", "h_oracle", "h_chronos",
            "h_seraph", "h_kai", "h_valkyrie", "h_arbiter",
            "e_eclipse", "e_archon", "e_inferno", "e_reaper",
            "e_titan", "e_colossus", "e_cryo", "e_shinobi",
        ]

        for idx, (cid, en_title, jp_stem, set_code, rarity, slot_num, theme, faction, (u, r, d, l), cost) in enumerate(SET1_60_BILINGUAL_TABLE):
            orig_title_pre = f"{jp_stem}(進化前)"
            orig_title_post = f"{jp_stem}(進化後)"
            base_num = f"{set_code}-{slot_num:03d} {rarity}"
            evo_num = f"{set_code}-{slot_num:03d}EV {rarity}"

            eu = min(10, u + 1)
            er = min(10, r + 1)
            ed = min(10, d + 1)
            el = min(10, l + 1)

            template_web_id = web_base_16_ids[idx % len(web_base_16_ids)]
            web_set1_id = template_web_id if idx < 16 else f"set1_c{idx + 1:02d}_{template_web_id}"
            art_path = (
                f"Assets/Resources/CardArt/{cid}.png"
                if idx < 14
                else f"GeneratedArt/MasteredCards/{web_set1_id}.png"
            )

            lore_en = (
                f"Inscribed in {BOOSTER_SETS[set_code]['version']} as collector slot {base_num}, {en_title} "
                f"channels {faction} directional mastery (N:{u} E:{r} S:{d} W:{l}) across the 3x3 stone monoliths "
                f"of CARDFRONT: Cradle of Echoes."
            )
            lore_jp = (
                f"『{BOOSTER_SETS[set_code]['original_version']}』収録のコレクターズカード（{base_num}）。"
                f"{jp_stem}は{faction}の戦術共鳴を宿し、３×３の石盤上で四方（北{u}・東{r}・南{d}・西{l}）の"
                f"テレグラフ支配を展開する。"
            )

            evo_cid = f"{cid}_evolved"
            evo_entry = self._build_collector_entry(
                card_id=evo_cid,
                title=f"{en_title} (Evolved)",
                original_title=orig_title_post,
                original_title_evolved=orig_title_post,
                card_game="CARDFRONT: Cradle of Echoes (Shadowverse EVOLVE Standard)",
                card_game_primary="Shadowverse EVOLVE",
                card_game_interop="CARDFRONT: Cradle of Echoes",
                set_code=set_code,
                card_number=evo_num,
                rarity=rarity,
                evolution_state="進化後",
                evolution_state_en="Evolved",
                up=eu,
                right=er,
                down=ed,
                left=el,
                theme=theme,
                faction=faction,
                cost=cost,
                art_path=art_path,
                lore_en=lore_en + " [Evolved Form: +1 to all directional ranks and prismatic foil aura.]",
                lore_jp=lore_jp + "【進化後：全方向ステータス＋１強化＆プリズムフォイル覚醒】",
                serial_index=serial_counter + 1,
                category="core_14_evolved" if idx < 14 else "set1_60_evolved",
                unevolved_base_card_id=cid,
                extra_aliases=[f"{web_set1_id}_evolved"],
            )

            base_entry = self._build_collector_entry(
                card_id=cid,
                title=f"{en_title} (Unevolved)",
                original_title=orig_title_pre,
                original_title_evolved=orig_title_post,
                card_game="CARDFRONT: Cradle of Echoes (Shadowverse EVOLVE Standard)",
                card_game_primary="Shadowverse EVOLVE",
                card_game_interop="CARDFRONT: Cradle of Echoes",
                set_code=set_code,
                card_number=base_num,
                rarity=rarity,
                evolution_state="進化前",
                evolution_state_en="Unevolved",
                up=u,
                right=r,
                down=d,
                left=l,
                theme=theme,
                faction=faction,
                cost=cost,
                art_path=art_path,
                lore_en=lore_en,
                lore_jp=lore_jp,
                serial_index=serial_counter,
                category="core_14" if idx < 14 else "set1_60",
                evolved_counterpart=evo_entry,
                extra_aliases=[web_set1_id, en_title],
            )
            base_entry["set1_index"] = idx + 1
            base_entry["web_set1_card_id"] = web_set1_id
            self._register_entry(base_entry)
            self._register_entry(evo_entry)
            self._set1_60_cards.append(base_entry)
            if idx < 14:
                self._core_14_cards.append(base_entry)
            serial_counter += 2

        # Register campaign expansion alias IDs so any lookup by `SET1_FULL_60_ROSTER` ID succeeds
        for camp_id, (target_cid, jp_stem) in CAMPAIGN_EXPANSION_ALIASES.items():
            if camp_id not in self._cards_by_id and target_cid in self._cards_by_id:
                template_entry = json.loads(json.dumps(self._cards_by_id[target_cid]))
                template_entry["card_id"] = camp_id
                template_entry["id"] = camp_id
                template_entry["original_title"] = f"{jp_stem}(進化前)"
                template_entry["original_title_evolved"] = f"{jp_stem}(進化後)"
                template_entry["identification"]["original_title"] = f"{jp_stem}(進化前)"
                template_entry["identification"]["original_title_evolved"] = f"{jp_stem}(進化後)"
                template_entry["evolved_counterpart"]["original_title"] = f"{jp_stem}(進化後)"
                self._cards_by_id[camp_id] = template_entry
                self._lookup_index[camp_id.lower()] = template_entry

    # -------------------------------------------------------------------------
    # Public Query & Formatting API
    # -------------------------------------------------------------------------
    def get_reference_archetype(self, evolved: bool = False) -> Dict[str, Any]:
        target_id = self.REFERENCE_ARCHETYPE_EVOLVED_ID if evolved else self.REFERENCE_ARCHETYPE_ID
        return self._cards_by_id[target_id]

    def get_card(self, query_key: str) -> Optional[Dict[str, Any]]:
        if not query_key:
            return None
        q = query_key.strip()
        if q in self._cards_by_id:
            return self._cards_by_id[q]
        if q in self._lookup_index:
            return self._lookup_index[q]
        q_low = q.lower()
        return self._lookup_index.get(q_low)

    def query_cards(
        self,
        *,
        set_code: Optional[str] = None,
        version: Optional[str] = None,
        rarity: Optional[str] = None,
        evolution_state: Optional[str] = None,
        theme: Optional[str] = None,
        search_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for card in self._cards_list:
            if set_code and card["set_code"].upper() != set_code.upper():
                continue
            if version and version.lower() not in card["version"].lower():
                continue
            if rarity and card["rarity"].upper() != rarity.upper():
                continue
            if evolution_state and evolution_state not in (card["evolution_state"], card["evolution_state_en"]):
                continue
            if theme and card["theme"].lower() != theme.lower():
                continue
            if search_text:
                needle = search_text.lower()
                haystack = " ".join(
                    [
                        card["card_id"],
                        card["title"],
                        card["original_title"],
                        card["card_number"],
                        card["version"],
                        card["original_version"],
                        card["lore_en"],
                        card["lore_jp"],
                    ]
                ).lower()
                if needle not in haystack:
                    continue
            results.append(card)
        return results

    def format_identification_block(self, card_or_id: Any, use_primary_game_label: bool = True) -> str:
        """
        Formats a card record into the exact 6-line collector identification block:
            original title    機構翼の少女・ローザ(進化前)
            card game         Shadowverse EVOLVE
            version           [BP05] Eternal omens
            original version  ブースターパック第5弾 永劫なる絶傑
            card number       BP05-110 SR
            rarity            SR
        """
        entry = self.get_card(card_or_id) if isinstance(card_or_id, str) else card_or_id
        if not entry:
            raise KeyError(f"Unknown card identifier: {card_or_id}")
        game_label = entry.get("card_game_primary", "Shadowverse EVOLVE") if use_primary_game_label else entry["card_game"]
        lines = [
            f"original title    {entry['original_title']}",
            f"card game         {game_label}",
            f"version           {entry['version']}",
            f"original version  {entry['original_version']}",
            f"card number       {entry['card_number']}",
            f"rarity            {entry['rarity']}",
        ]
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Catalog & Manifest Builders
    # -------------------------------------------------------------------------
    def build_catalog(self) -> Dict[str, Any]:
        ref_base = self.get_reference_archetype(evolved=False)
        ref_evo = self.get_reference_archetype(evolved=True)

        unevolved_cards = [c for c in self._cards_list if c["evolution_state"] == "進化前"]
        evolved_cards = [c for c in self._cards_list if c["evolution_state"] == "進化後"]

        return {
            "schema": "SYNAPSE_BILINGUAL_CARD_IDENTIFICATION_CATALOG_V1",
            "schema_version": "1.0.0",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "card_game_standard": "Shadowverse EVOLVE / CARDFRONT: Cradle of Echoes Collector Standard",
            "reference_archetype_specification": {
                "formatted_block": self.format_identification_block(ref_base, use_primary_game_label=True),
                "unevolved": ref_base,
                "evolved": ref_evo,
            },
            "booster_sets": BOOSTER_SETS,
            "rarity_tiers": RARITY_TIERS,
            "counts": {
                "total_catalog_records": len(self._cards_list),
                "unevolved_base_cards_count": len(unevolved_cards),
                "evolved_counterpart_cards_count": len(evolved_cards),
                "set1_60_cards_count": len(self._set1_60_cards),
                "playable_hero_boss_16_count": len(self._hero_boss_16_cards),
                "core_roster_14_count": len(self._core_14_cards),
                "booster_sets_count": len(BOOSTER_SETS),
                "rarity_tiers_count": len(RARITY_TIERS),
            },
            "reference_archetype_cards": [ref_base, ref_evo],
            "playable_hero_boss_16_cards": self._hero_boss_16_cards,
            "core_roster_14_cards": self._core_14_cards,
            "set1_60_cards": self._set1_60_cards,
            "cards": self._cards_list,
            "cards_by_id": self._cards_by_id,
        }

    def build_set1_60_manifest(self) -> Dict[str, Any]:
        """
        Builds `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Resources/Cards/set1_60_cards_manifest.json`
        with all 60 Set 1 cards enriched with full bilingual collector `identification`, `lore_en`, `lore_jp`,
        `atelier_art_direction`, and `collector_provenance`.
        """
        cards_by_id_map: Dict[str, Dict[str, Any]] = {}
        for card in self._set1_60_cards:
            cards_by_id_map[card["card_id"]] = card
            if "web_set1_card_id" in card:
                cards_by_id_map[card["web_set1_card_id"]] = card
        for camp_id, (target_cid, _) in CAMPAIGN_EXPANSION_ALIASES.items():
            if camp_id in self._cards_by_id:
                cards_by_id_map[camp_id] = self._cards_by_id[camp_id]
        for hb in self._hero_boss_16_cards:
            cards_by_id_map[hb["card_id"]] = hb
            if "web_card_id" in hb:
                cards_by_id_map[hb["web_card_id"]] = hb
        cards_by_id_map[self.REFERENCE_ARCHETYPE_ID] = self.get_reference_archetype(evolved=False)
        cards_by_id_map[self.REFERENCE_ARCHETYPE_EVOLVED_ID] = self.get_reference_archetype(evolved=True)

        return {
            "schema": "CARDFRONT_SET1_60_BILINGUAL_COLLECTOR_MANIFEST_V1",
            "schema_version": "1.0.0",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_cards": len(self._set1_60_cards),
            "set1_count": len(self._set1_60_cards),
            "core_14_count": len(self._core_14_cards),
            "expansion_46_count": len(self._set1_60_cards) - len(self._core_14_cards),
            "playable_hero_boss_16_count": len(self._hero_boss_16_cards),
            "reference_archetype": self.get_reference_archetype(evolved=False),
            "cards": self._set1_60_cards,
            "set1_full_60_roster": self._set1_60_cards,
            "playable_hero_boss_16": self._hero_boss_16_cards,
            "cards_by_id": cards_by_id_map,
        }

    # -------------------------------------------------------------------------
    # Deterministic Validation Gate
    # -------------------------------------------------------------------------
    def validate_catalog(self) -> Dict[str, Any]:
        errors: List[str] = []

        # 1. Verify exact reference archetype (`bp05_110_rosa_unevolved` & `bp05_110_rosa_evolved`)
        rosa_pre = self.get_card("bp05_110_rosa_unevolved")
        rosa_post = self.get_card("bp05_110_rosa_evolved")
        if not rosa_pre:
            errors.append("Missing reference archetype bp05_110_rosa_unevolved")
        else:
            if rosa_pre["original_title"] != "機構翼の少女・ローザ(進化前)":
                errors.append(f"Invalid rosa_pre original_title: {rosa_pre['original_title']}")
            if rosa_pre["title"] != "Rosa, Mechanized Wing Maiden (Unevolved)":
                errors.append(f"Invalid rosa_pre title: {rosa_pre['title']}")
            if "Shadowverse EVOLVE" not in rosa_pre["card_game"]:
                errors.append(f"Invalid rosa_pre card_game: {rosa_pre['card_game']}")
            if rosa_pre["version"] != "[BP05] Eternal omens":
                errors.append(f"Invalid rosa_pre version: {rosa_pre['version']}")
            if rosa_pre["original_version"] != "ブースターパック第5弾 永劫なる絶傑":
                errors.append(f"Invalid rosa_pre original_version: {rosa_pre['original_version']}")
            if rosa_pre["card_number"] != "BP05-110 SR":
                errors.append(f"Invalid rosa_pre card_number: {rosa_pre['card_number']}")
            if rosa_pre["rarity"] != "SR":
                errors.append(f"Invalid rosa_pre rarity: {rosa_pre['rarity']}")
            if rosa_pre["evolution_state"] != "進化前":
                errors.append(f"Invalid rosa_pre evolution_state: {rosa_pre['evolution_state']}")
            if (rosa_pre["up"], rosa_pre["right"], rosa_pre["down"], rosa_pre["left"]) != (7, 8, 6, 7):
                errors.append("Invalid rosa_pre directional stats")

        if not rosa_post:
            errors.append("Missing reference archetype bp05_110_rosa_evolved")
        else:
            if rosa_post["original_title"] != "機構翼の少女・ローザ(進化後)":
                errors.append(f"Invalid rosa_post original_title: {rosa_post['original_title']}")
            if rosa_post["card_number"] != "BP05-110EV SR":
                errors.append(f"Invalid rosa_post card_number: {rosa_post['card_number']}")
            if rosa_post["evolution_state"] != "進化後":
                errors.append(f"Invalid rosa_post evolution_state: {rosa_post['evolution_state']}")
            if (rosa_post["up"], rosa_post["right"], rosa_post["down"], rosa_post["left"]) != (9, 9, 8, 8):
                errors.append("Invalid rosa_post directional stats")

        # 2. Verify all 16 playable Hero/Boss cards
        expected_16 = [
            "kaelen", "seraph", "vex", "solaris", "nyx", "bastion", "chronos", "orb",
            "dreadnought", "archon", "shinobi", "oracle", "valkyrie", "behemoth", "siren", "leviathan",
        ]
        for hid in expected_16:
            c = self.get_card(hid)
            if not c:
                errors.append(f"Missing playable hero/boss card: {hid}")
                continue
            if not c["original_title"].endswith("(進化前)"):
                errors.append(f"Hero/Boss {hid} original_title does not end with (進化前): {c['original_title']}")
            evo = c.get("evolved_counterpart")
            if not evo or not evo["original_title"].endswith("(進化後)"):
                errors.append(f"Hero/Boss {hid} missing valid evolved_counterpart with (進化後)")

        # 3. Verify all 60 Set 1 cards and 14 Core Roster cards
        if len(self._set1_60_cards) != 60:
            errors.append(f"Expected 60 Set 1 cards, found {len(self._set1_60_cards)}")
        if len(self._core_14_cards) != 14:
            errors.append(f"Expected 14 Core Roster cards, found {len(self._core_14_cards)}")

        seen_sha256 = set()
        for c in self._cards_list:
            sha = c.get("sha256_collector_id", "")
            if len(sha) != 64:
                errors.append(f"Card {c['card_id']} has invalid sha256_collector_id: {sha}")
            seen_sha256.add(sha)
            if not c.get("lore_en") or not c.get("lore_jp"):
                errors.append(f"Card {c['card_id']} missing bilingual lore_en / lore_jp")
            if not c.get("atelier_art_direction") or not c.get("collector_provenance"):
                errors.append(f"Card {c['card_id']} missing atelier_art_direction or collector_provenance")

        return {
            "passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "total_catalog_records": len(self._cards_list),
            "unique_sha256_collector_ids": len(seen_sha256),
            "set1_60_cards_verified": len(self._set1_60_cards),
            "playable_hero_boss_16_verified": len(self._hero_boss_16_cards),
            "core_14_cards_verified": len(self._core_14_cards),
            "booster_sets_covered": list(BOOSTER_SETS.keys()),
            "rarities_covered": list(RARITY_TIERS.keys()),
        }

    def export_all(self) -> Dict[str, Any]:
        CARDS_RES_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        catalog_payload = self.build_catalog()
        set1_manifest_payload = self.build_set1_60_manifest()
        validation_report = self.validate_catalog()

        CATALOG_OUT_PATH.write_text(
            json.dumps(catalog_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_unity_text_asset_meta(CATALOG_OUT_PATH)

        SET1_MANIFEST_OUT_PATH.write_text(
            json.dumps(set1_manifest_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_unity_text_asset_meta(SET1_MANIFEST_OUT_PATH)

        report_payload = {
            "schema": "SYNAPSE_CARD_IDENTIFICATION_CATALOG_REPORT_V1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "catalog_path": str(CATALOG_OUT_PATH),
            "set1_manifest_path": str(SET1_MANIFEST_OUT_PATH),
            "report_path": str(REPORT_OUT_PATH),
            "reference_archetype_block": self.format_identification_block(self.REFERENCE_ARCHETYPE_ID),
            "validation": validation_report,
            "counts": catalog_payload["counts"],
            "sample_hero_boss_identifications": [
                {
                    "card_id": c["card_id"],
                    "original_title": c["original_title"],
                    "original_title_evolved": c["original_title_evolved"],
                    "version": c["version"],
                    "original_version": c["original_version"],
                    "card_number": c["card_number"],
                    "rarity": c["rarity"],
                }
                for c in self._hero_boss_16_cards[:6]
            ],
        }
        REPORT_OUT_PATH.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return report_payload


def main() -> None:
    engine = SynapseCardIdentificationCatalog()
    report = engine.export_all()
    print("=== Synapse Bilingual Card Identification & Collector Taxonomy Engine ===")
    print(engine.format_identification_block("bp05_110_rosa_unevolved"))
    print("-------------------------------------------------------------------------")
    print(f"Validation Passed       : {report['validation']['passed']}")
    print(f"Total Catalog Records   : {report['counts']['total_catalog_records']}")
    print(f"Unevolved Base Cards    : {report['counts']['unevolved_base_cards_count']}")
    print(f"Evolved Counterparts    : {report['counts']['evolved_counterpart_cards_count']}")
    print(f"Set 1 Cards (Manifest)  : {report['counts']['set1_60_cards_count']}")
    print(f"Playable Hero/Boss (16) : {report['counts']['playable_hero_boss_16_count']}")
    print(f"Core Roster Cards (14)  : {report['counts']['core_roster_14_count']}")
    print(f"Catalog JSON            : {report['catalog_path']}")
    print(f"Set 1 Manifest JSON     : {report['set1_manifest_path']}")
    print(f"Verification Report JSON: {report['report_path']}")
    if not report["validation"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
