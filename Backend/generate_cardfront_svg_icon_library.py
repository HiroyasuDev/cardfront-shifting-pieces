#!/usr/bin/env python3
"""
Backend/generate_cardfront_svg_icon_library.py
==============================================
Generates the Original CARDFRONT: Cradle of Echoes Custom SVG Icon, Emblem &
Card-Back Art Style Library (`Arcane Atelier x Cyber-Ivalice` house style).

All icons are 100% original code-native vector art (`viewBox="0 0 256 256"`,
with `cf_cardback_astrolabe.svg` at `viewBox="0 0 300 400"`), crafted with:
  - Multi-stop metallic gradients (Ivalice Law Gold `#FFB800`, Astral Cyan `#00E5FF`,
    Jade Verdict `#2EE6D3`, Crimson-Flame `#FF2E54`, Tarot Violet `#A855F7`,
    Obsidian Slate `#0B1021`).
  - Beveled cyber-magicite facets, concentric astrolabe rings, and pen-and-ink
    filigree linework.
  - Zero generic system emojis, zero living-artist references, and zero baked raster text.

Outputs:
  1. `WebPlayable/GeneratedArt/Icons/*.svg` (22 bespoke SVG assets)
  2. `Assets/Resources/UI/Icons/*.svg` (Unity 2022.3.40f1 mirror)
  3. `WebPlayable/GeneratedArt/Icons/icon_library_manifest.json`
  4. `WebPlayable/GeneratedArt/Icons/icon_library_gallery.html`
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_ICONS_DIR = ROOT_DIR / "WebPlayable" / "GeneratedArt" / "Icons"
UNITY_ICONS_DIR = ROOT_DIR / "Assets" / "Resources" / "UI" / "Icons"


SHARED_DEFS = """
  <defs>
    <linearGradient id="cf-gold-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF3B0"/>
      <stop offset="35%" stop-color="#FFB800"/>
      <stop offset="75%" stop-color="#C87D0A"/>
      <stop offset="100%" stop-color="#6E3F04"/>
    </linearGradient>
    <linearGradient id="cf-cyan-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E0FFFF"/>
      <stop offset="40%" stop-color="#00E5FF"/>
      <stop offset="80%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="cf-crimson-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFD1DC"/>
      <stop offset="38%" stop-color="#FF2E54"/>
      <stop offset="78%" stop-color="#9F1239"/>
      <stop offset="100%" stop-color="#3B0714"/>
    </linearGradient>
    <linearGradient id="cf-violet-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F3E8FF"/>
      <stop offset="40%" stop-color="#A855F7"/>
      <stop offset="82%" stop-color="#581C87"/>
      <stop offset="100%" stop-color="#1E1B4B"/>
    </linearGradient>
    <linearGradient id="cf-jade-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#CCFBF1"/>
      <stop offset="42%" stop-color="#2EE6D3"/>
      <stop offset="85%" stop-color="#0F766E"/>
      <stop offset="100%" stop-color="#042F2E"/>
    </linearGradient>
    <linearGradient id="cf-obsidian-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="50%" stop-color="#0F172A"/>
      <stop offset="100%" stop-color="#050811"/>
    </linearGradient>
    <radialGradient id="cf-core-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.95"/>
      <stop offset="55%" stop-color="#00E5FF" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#00E5FF" stop-opacity="0"/>
    </radialGradient>
  </defs>
""".strip()


def wrap_svg_256(inner: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" fill="none">\n'
        f"  {SHARED_DEFS}\n"
        f"  {inner.strip()}\n"
        "</svg>\n"
    )


ICON_SPECS: List[Dict[str, str]] = [
    {
        "id": "aether_coin",
        "filename": "cf_icon_aether_coin.svg",
        "title": "Ivalice Skystone Sovereign Coin",
        "category": "currency",
        "replaces": "Generic coin glyph",
        "palette": "#FFB800 / #00E5FF / #0F172A",
        "body": """
    <polygon points="128,14 208,48 242,128 208,208 128,242 48,208 14,128 48,48" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="6"/>
    <polygon points="128,32 196,60 224,128 196,196 128,224 60,196 32,128 60,60" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="5"/>
    <circle cx="128" cy="128" r="74" stroke="url(#cf-gold-grad)" stroke-width="4" stroke-dasharray="12 8"/>
    <polygon points="128,52 150,106 204,128 150,150 128,204 106,150 52,128 106,106" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <polygon points="128,84 148,128 128,172 108,128" fill="url(#cf-cyan-grad)" stroke="#E0FFFF" stroke-width="3"/>
    <circle cx="128" cy="128" r="10" fill="#FFF3B0"/>
        """,
    },
    {
        "id": "citadel_gear",
        "filename": "cf_icon_citadel_gear.svg",
        "title": "Chronos Astrolabe Settings Gear",
        "category": "hud_control",
        "replaces": "Generic gear glyph",
        "palette": "#FFB800 / #00E5FF / #1E293B",
        "body": """
    <g stroke="url(#cf-gold-grad)" stroke-width="18" stroke-linecap="round">
      <line x1="128" y1="16" x2="128" y2="240"/>
      <line x1="16" y1="128" x2="240" y2="128"/>
      <line x1="49" y1="49" x2="207" y2="207"/>
      <line x1="207" y1="49" x2="49" y2="207"/>
    </g>
    <circle cx="128" cy="128" r="84" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="14"/>
    <circle cx="128" cy="128" r="60" fill="none" stroke="#FFF3B0" stroke-width="3" stroke-dasharray="10 6"/>
    <polygon points="128,68 146,110 188,128 146,146 128,188 110,146 68,128 110,110" fill="url(#cf-gold-grad)"/>
    <circle cx="128" cy="128" r="24" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="4"/>
        """,
    },
    {
        "id": "bgm_chime",
        "filename": "cf_icon_bgm_chime.svg",
        "title": "Sakimoto Harmonic Lyre & Chime Crest",
        "category": "audio",
        "replaces": "Generic music note / low speaker",
        "palette": "#FFB800 / #2EE6D3 / #00E5FF",
        "body": """
    <circle cx="128" cy="128" r="104" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="6"/>
    <path d="M76,188 C58,148 64,88 94,54 L112,72 C92,98 88,142 102,174 Z" fill="url(#cf-gold-grad)"/>
    <path d="M180,188 C198,148 192,88 162,54 L144,72 C164,98 168,142 154,174 Z" fill="url(#cf-gold-grad)"/>
    <rect x="72" y="182" width="112" height="20" rx="8" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <line x1="112" y1="68" x2="112" y2="182" stroke="url(#cf-cyan-grad)" stroke-width="6"/>
    <line x1="128" y1="54" x2="128" y2="182" stroke="#FFF3B0" stroke-width="6"/>
    <line x1="144" y1="68" x2="144" y2="182" stroke="url(#cf-cyan-grad)" stroke-width="6"/>
    <polygon points="128,30 140,52 128,66 116,52" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "sfx_horn",
        "filename": "cf_icon_sfx_horn.svg",
        "title": "Arcane Resonance Horn & Sonic Chevrons",
        "category": "audio",
        "replaces": "Generic speaker glyph",
        "palette": "#00E5FF / #FFB800",
        "body": """
    <circle cx="128" cy="128" r="104" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="6"/>
    <polygon points="46,104 86,104 138,60 138,196 86,152 46,152" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="4" stroke-linejoin="round"/>
    <path d="M160,92 C178,108 178,148 160,164" stroke="url(#cf-cyan-grad)" stroke-width="10" stroke-linecap="round"/>
    <path d="M184,68 C212,98 212,158 184,188" stroke="url(#cf-cyan-grad)" stroke-width="10" stroke-linecap="round"/>
        """,
    },
    {
        "id": "sfx_muted",
        "filename": "cf_icon_sfx_muted.svg",
        "title": "Ward-Sealed Silence Crest",
        "category": "audio",
        "replaces": "Generic muted speaker glyph",
        "palette": "#FF2E54 / #FFB800",
        "body": """
    <circle cx="128" cy="128" r="104" fill="url(#cf-obsidian-grad)" stroke="url(#cf-crimson-grad)" stroke-width="6"/>
    <polygon points="46,104 86,104 138,60 138,196 86,152 46,152" fill="url(#cf-gold-grad)" opacity="0.65" stroke="#FFF3B0" stroke-width="4" stroke-linejoin="round"/>
    <line x1="162" y1="96" x2="210" y2="160" stroke="url(#cf-crimson-grad)" stroke-width="14" stroke-linecap="round"/>
    <line x1="210" y1="96" x2="162" y2="160" stroke="url(#cf-crimson-grad)" stroke-width="14" stroke-linecap="round"/>
    <line x1="54" y1="54" x2="202" y2="202" stroke="url(#cf-crimson-grad)" stroke-width="10" stroke-linecap="round"/>
        """,
    },
    {
        "id": "telegraph_hazard",
        "filename": "cf_icon_telegraph_hazard.svg",
        "title": "Breach Crimson-Gold Targeting Sigil",
        "category": "telegraph",
        "replaces": "Generic warning triangle",
        "palette": "#FF2E54 / #FFB800",
        "body": """
    <polygon points="128,16 240,128 128,240 16,128" fill="url(#cf-crimson-grad)" stroke="url(#cf-gold-grad)" stroke-width="10"/>
    <polygon points="128,42 214,128 128,214 42,128" fill="url(#cf-obsidian-grad)" stroke="#FF2E54" stroke-width="4"/>
    <polygon points="128,66 142,84 134,148 122,148 114,84" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <polygon points="128,164 142,178 128,192 114,178" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <path d="M16,64 L48,32 M240,64 L208,32 M16,192 L48,224 M240,192 L208,224" stroke="url(#cf-gold-grad)" stroke-width="6" stroke-linecap="round"/>
        """,
    },
    {
        "id": "astral_surge",
        "filename": "cf_icon_astral_surge.svg",
        "title": "Astral Fulmination Lance & Boost Crest",
        "category": "telegraph",
        "replaces": "Generic lightning bolt",
        "palette": "#00E5FF / #FFB800",
        "body": """
    <polygon points="128,20 222,74 222,182 128,236 34,182 34,74" fill="url(#cf-obsidian-grad)" stroke="url(#cf-cyan-grad)" stroke-width="8"/>
    <polygon points="148,18 66,136 124,136 102,238 194,114 134,114" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="5" stroke-linejoin="round"/>
    <polygon points="142,46 88,128 128,128 114,202 172,120 132,120" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "grimoire_deck",
        "filename": "cf_icon_grimoire_deck.svg",
        "title": "Arcane Atelier Triple Tarot Deck Crest",
        "category": "deckbuilder",
        "replaces": "Generic joker card emoji",
        "palette": "#FFB800 / #A855F7 / #00E5FF",
        "body": """
    <g transform="rotate(-14 128 140)">
      <rect x="54" y="38" width="116" height="164" rx="12" fill="url(#cf-obsidian-grad)" stroke="url(#cf-violet-grad)" stroke-width="6"/>
    </g>
    <g transform="rotate(14 128 140)">
      <rect x="86" y="38" width="116" height="164" rx="12" fill="url(#cf-obsidian-grad)" stroke="url(#cf-cyan-grad)" stroke-width="6"/>
    </g>
    <rect x="68" y="32" width="120" height="172" rx="14" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="8"/>
    <rect x="80" y="44" width="96" height="148" rx="8" fill="none" stroke="#FFF3B0" stroke-width="2" stroke-dasharray="8 5"/>
    <circle cx="128" cy="118" r="34" fill="none" stroke="url(#cf-gold-grad)" stroke-width="5"/>
    <polygon points="128,74 140,106 172,118 140,130 128,162 116,130 84,118 116,106" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="3"/>
        """,
    },
    {
        "id": "staccs_die",
        "filename": "cf_icon_staccs_die.svg",
        "title": "Isometric 3D STACCS Runic Hexahedron Die",
        "category": "dice",
        "replaces": "Generic die emoji",
        "palette": "#FFB800 / #00E5FF / #A855F7",
        "body": """
    <polygon points="128,20 228,76 128,132 28,76" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="5" stroke-linejoin="round"/>
    <polygon points="28,76 128,132 128,236 28,180" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="228,76 128,132 128,236 228,180" fill="#131C31" stroke="url(#cf-cyan-grad)" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="128" cy="76" r="12" fill="#0F172A"/>
    <circle cx="64" cy="134" r="10" fill="url(#cf-gold-grad)"/>
    <circle cx="96" cy="176" r="10" fill="url(#cf-gold-grad)"/>
    <circle cx="160" cy="130" r="9" fill="url(#cf-cyan-grad)"/>
    <circle cx="178" cy="156" r="9" fill="url(#cf-cyan-grad)"/>
    <circle cx="196" cy="182" r="9" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "tactical_lantern",
        "filename": "cf_icon_tactical_lantern.svg",
        "title": "Skystone Wayfinder Guidance Crystal",
        "category": "guidance",
        "replaces": "Generic lightbulb emoji",
        "palette": "#00E5FF / #FFB800",
        "body": """
    <circle cx="128" cy="128" r="108" fill="url(#cf-core-glow)"/>
    <polygon points="128,20 186,96 160,188 96,188 70,96" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="128,20 156,96 128,188 100,96" fill="#E0FFFF" opacity="0.55"/>
    <rect x="88" y="196" width="80" height="18" rx="6" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <polygon points="104,218 152,218 138,240 118,240" fill="url(#cf-gold-grad)"/>
    <g stroke="url(#cf-gold-grad)" stroke-width="6" stroke-linecap="round">
      <line x1="28" y1="92" x2="52" y2="100"/>
      <line x1="228" y1="92" x2="204" y2="100"/>
      <line x1="46" y1="44" x2="66" y2="62"/>
      <line x1="210" y1="44" x2="190" y2="62"/>
    </g>
        """,
    },
    {
        "id": "victory_laurel",
        "filename": "cf_icon_victory_laurel.svg",
        "title": "Sovereign Ivalice Winged Victory Chalice",
        "category": "result",
        "replaces": "Generic trophy emoji",
        "palette": "#FFB800 / #00E5FF",
        "body": """
    <path d="M40,68 C18,118 42,178 96,204 C64,164 58,116 74,76 Z" fill="url(#cf-gold-grad)"/>
    <path d="M216,68 C238,118 214,178 160,204 C192,164 198,116 182,76 Z" fill="url(#cf-gold-grad)"/>
    <path d="M76,44 H180 L166,136 C162,162 94,162 90,136 Z" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="5" stroke-linejoin="round"/>
    <rect x="116" y="154" width="24" height="44" fill="url(#cf-gold-grad)"/>
    <polygon points="80,200 176,200 190,228 66,228" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="4"/>
    <polygon points="128,62 138,88 166,98 138,108 128,134 118,108 90,98 118,88" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "defeat_shatter",
        "filename": "cf_icon_defeat_shatter.svg",
        "title": "Crimson-Obsidian Fractured Aegis Sigil",
        "category": "result",
        "replaces": "Generic collision emoji",
        "palette": "#FF2E54 / #FFB800",
        "body": """
    <polygon points="128,14 156,74 222,42 184,104 242,142 174,158 202,226 138,184 102,242 94,172 24,194 68,132 18,82 88,84" fill="url(#cf-crimson-grad)" stroke="url(#cf-gold-grad)" stroke-width="5" stroke-linejoin="round"/>
    <polygon points="128,54 146,98 190,82 162,122 198,150 152,158 166,200 128,170 92,202 98,154 54,162 86,124 58,92 104,96" fill="url(#cf-obsidian-grad)" stroke="#FFD1DC" stroke-width="3"/>
        """,
    },
    {
        "id": "judge_aegis",
        "filename": "cf_icon_judge_aegis.svg",
        "title": "Ivalice Judge Law Barrier Aegis",
        "category": "defense",
        "replaces": "Generic shield emoji",
        "palette": "#00E5FF / #FFB800",
        "body": """
    <path d="M128,18 L220,56 V128 C220,184 178,222 128,242 C78,222 36,184 36,128 V56 Z" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="10" stroke-linejoin="round"/>
    <path d="M128,38 L200,68 V126 C200,170 166,202 128,220 C90,202 56,170 56,126 V68 Z" fill="url(#cf-cyan-grad)" opacity="0.28" stroke="#00E5FF" stroke-width="4"/>
    <polygon points="128,54 140,114 184,128 140,142 128,202 116,142 72,128 116,114" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <circle cx="128" cy="128" r="14" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "booster_reliquary",
        "filename": "cf_icon_booster_reliquary.svg",
        "title": "Set 1 Cradle of Echoes Reliquary Chest",
        "category": "deckbuilder",
        "replaces": "Generic gift box emoji",
        "palette": "#FFB800 / #A855F7 / #00E5FF",
        "body": """
    <polygon points="48,92 128,44 208,92 208,204 48,204" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="8" stroke-linejoin="round"/>
    <polygon points="40,96 128,48 216,96 196,124 60,124" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="4" stroke-linejoin="round"/>
    <rect x="64" y="124" width="128" height="76" rx="6" fill="url(#cf-violet-grad)" stroke="url(#cf-gold-grad)" stroke-width="6"/>
    <line x1="128" y1="48" x2="128" y2="200" stroke="url(#cf-gold-grad)" stroke-width="12"/>
    <polygon points="128,94 148,124 128,154 108,124" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="4"/>
        """,
    },
    {
        "id": "cardcraft_anvil",
        "filename": "cf_icon_cardcraft_anvil.svg",
        "title": "CardCraft Magicite Forge Hammer & Anvil",
        "category": "deckbuilder",
        "replaces": "Generic hammers emoji",
        "palette": "#A855F7 / #FFB800 / #00E5FF",
        "body": """
    <line x1="64" y1="164" x2="188" y2="40" stroke="url(#cf-gold-grad)" stroke-width="14" stroke-linecap="round"/>
    <polygon points="148,24 224,64 200,98 124,58" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="5" stroke-linejoin="round"/>
    <path d="M36,156 H220 L194,188 H164 L180,224 H76 L92,188 H62 Z" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="8" stroke-linejoin="round"/>
    <polygon points="96,112 108,132 128,140 108,148 96,168 84,148 64,140 84,132" fill="url(#cf-gold-grad)"/>
        """,
    },
    {
        "id": "hologram_prism",
        "filename": "cf_icon_hologram_prism.svg",
        "title": "Hi3D Watertight Octahedron Hologram Prism",
        "category": "3d_inspector",
        "replaces": "Generic ice cube emoji",
        "palette": "#00E5FF / #2EE6D3 / #FFB800",
        "body": """
    <ellipse cx="128" cy="218" rx="76" ry="18" fill="none" stroke="url(#cf-gold-grad)" stroke-width="5" stroke-dasharray="10 6"/>
    <polygon points="128,20 218,122 128,206 38,122" fill="url(#cf-cyan-grad)" opacity="0.32" stroke="url(#cf-cyan-grad)" stroke-width="7" stroke-linejoin="round"/>
    <line x1="128" y1="20" x2="128" y2="206" stroke="#E0FFFF" stroke-width="5"/>
    <line x1="38" y1="122" x2="218" y2="122" stroke="#E0FFFF" stroke-width="5"/>
    <circle cx="128" cy="122" r="14" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="3"/>
        """,
    },
    {
        "id": "camera_aperture",
        "filename": "cf_icon_camera_aperture.svg",
        "title": "Isometric Brass Viewfinder Lens",
        "category": "camera",
        "replaces": "Generic movie camera emoji",
        "palette": "#FFB800 / #00E5FF",
        "body": """
    <rect x="28" y="56" width="200" height="148" rx="22" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="8"/>
    <polygon points="84,56 102,32 154,32 172,56" fill="url(#cf-gold-grad)"/>
    <circle cx="128" cy="130" r="52" fill="url(#cf-obsidian-grad)" stroke="url(#cf-cyan-grad)" stroke-width="8"/>
    <circle cx="128" cy="130" r="24" fill="url(#cf-cyan-grad)"/>
    <circle cx="188" cy="84" r="10" fill="url(#cf-gold-grad)"/>
        """,
    },
    {
        "id": "lock_seal",
        "filename": "cf_icon_lock_seal.svg",
        "title": "Ivalice Law Sealed Padlock",
        "category": "deckbuilder",
        "replaces": "Generic lock emoji",
        "palette": "#FFB800 / #FF2E54",
        "body": """
    <path d="M84,112 V78 C84,50 104,32 128,32 C152,32 172,50 172,78 V112" stroke="url(#cf-gold-grad)" stroke-width="16" stroke-linecap="round"/>
    <rect x="52" y="108" width="152" height="118" rx="18" fill="url(#cf-obsidian-grad)" stroke="url(#cf-gold-grad)" stroke-width="8"/>
    <circle cx="128" cy="154" r="16" fill="url(#cf-gold-grad)"/>
    <polygon points="120,162 136,162 142,198 114,198" fill="url(#cf-gold-grad)"/>
        """,
    },
    {
        "id": "sovereign_crown",
        "filename": "cf_icon_sovereign_crown.svg",
        "title": "Sovereign Agent Five-Spire Law Crown",
        "category": "plugins",
        "replaces": "Generic crown emoji",
        "palette": "#FFB800 / #A855F7 / #00E5FF",
        "body": """
    <polygon points="28,188 46,78 92,132 128,44 164,132 210,78 228,188" fill="url(#cf-gold-grad)" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>
    <rect x="36" y="188" width="184" height="26" rx="8" fill="url(#cf-violet-grad)" stroke="url(#cf-gold-grad)" stroke-width="5"/>
    <circle cx="128" cy="144" r="14" fill="url(#cf-cyan-grad)" stroke="#FFF3B0" stroke-width="3"/>
    <circle cx="76" cy="156" r="10" fill="url(#cf-violet-grad)" stroke="#FFF3B0" stroke-width="2"/>
    <circle cx="180" cy="156" r="10" fill="url(#cf-violet-grad)" stroke="#FFF3B0" stroke-width="2"/>
        """,
    },
    {
        "id": "faction_link",
        "filename": "cf_icon_faction_link.svg",
        "title": "Interlocking Astral Resonance Link Rings",
        "category": "synergy",
        "replaces": "Generic chain link / check emoji",
        "palette": "#00E5FF / #FFB800 / #2EE6D3",
        "body": """
    <circle cx="96" cy="128" r="56" fill="none" stroke="url(#cf-cyan-grad)" stroke-width="16"/>
    <circle cx="160" cy="128" r="56" fill="none" stroke="url(#cf-gold-grad)" stroke-width="16"/>
    <polygon points="128,88 140,118 170,128 140,138 128,168 116,138 86,128 116,118" fill="url(#cf-jade-grad)" stroke="#FFF3B0" stroke-width="3"/>
        """,
    },
    {
        "id": "ally_crest",
        "filename": "cf_icon_ally_crest.svg",
        "title": "Astral Cyan Player Conduit Crest",
        "category": "faction",
        "replaces": "Generic blue square emoji",
        "palette": "#00E5FF / #FFB800",
        "body": """
    <polygon points="128,16 232,128 128,240 24,128" fill="url(#cf-cyan-grad)" stroke="url(#cf-gold-grad)" stroke-width="10"/>
    <polygon points="128,56 192,128 128,200 64,128" fill="url(#cf-obsidian-grad)" stroke="#E0FFFF" stroke-width="5"/>
    <circle cx="128" cy="128" r="22" fill="url(#cf-cyan-grad)"/>
        """,
    },
    {
        "id": "boss_crest",
        "filename": "cf_icon_boss_crest.svg",
        "title": "Crimson-Obsidian Boss Dreadnought Crest",
        "category": "faction",
        "replaces": "Generic red square emoji",
        "palette": "#FF2E54 / #FFB800",
        "body": """
    <polygon points="128,14 236,82 198,232 58,232 20,82" fill="url(#cf-crimson-grad)" stroke="url(#cf-gold-grad)" stroke-width="10" stroke-linejoin="round"/>
    <polygon points="128,48 198,96 172,202 84,202 58,96" fill="url(#cf-obsidian-grad)" stroke="#FFD1DC" stroke-width="4"/>
    <polygon points="128,76 154,136 128,184 102,136" fill="url(#cf-crimson-grad)"/>
        """,
    },
]


CARDBACK_ASTROLABE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400" fill="none">
  <defs>
    <linearGradient id="cb-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#171E36"/>
      <stop offset="50%" stop-color="#0B1021"/>
      <stop offset="100%" stop-color="#050811"/>
    </linearGradient>
    <linearGradient id="cb-gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF3B0"/>
      <stop offset="40%" stop-color="#FFB800"/>
      <stop offset="80%" stop-color="#B4690E"/>
      <stop offset="100%" stop-color="#5C3404"/>
    </linearGradient>
    <linearGradient id="cb-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E0FFFF"/>
      <stop offset="50%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
    <radialGradient id="cb-aura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.48"/>
      <stop offset="55%" stop-color="#A855F7" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#050811" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="6" y="6" width="288" height="388" rx="22" fill="url(#cb-bg)" stroke="url(#cb-gold)" stroke-width="8"/>
  <rect x="20" y="20" width="260" height="360" rx="14" fill="none" stroke="url(#cb-gold)" stroke-width="3"/>
  <rect x="30" y="30" width="240" height="340" rx="10" fill="url(#cb-aura)" stroke="#FFB800" stroke-opacity="0.45" stroke-width="1.5" stroke-dasharray="8 6"/>

  <!-- Corner Ivalice Filigree Brackets -->
  <path d="M24,68 L24,24 L68,24" stroke="url(#cb-gold)" stroke-width="6" stroke-linecap="round"/>
  <path d="M276,68 L276,24 L232,24" stroke="url(#cb-gold)" stroke-width="6" stroke-linecap="round"/>
  <path d="M24,332 L24,376 L68,376" stroke="url(#cb-gold)" stroke-width="6" stroke-linecap="round"/>
  <path d="M276,332 L276,376 L232,376" stroke="url(#cb-gold)" stroke-width="6" stroke-linecap="round"/>

  <!-- Top & Bottom Skystone Spires -->
  <polygon points="150,36 168,78 150,96 132,78" fill="url(#cb-gold)"/>
  <polygon points="150,364 168,322 150,304 132,322" fill="url(#cb-gold)"/>

  <!-- Double Concentric Astrolabe Rings -->
  <circle cx="150" cy="200" r="96" stroke="url(#cb-gold)" stroke-width="5"/>
  <circle cx="150" cy="200" r="82" stroke="url(#cb-cyan)" stroke-width="2.5" stroke-dasharray="10 6"/>
  <circle cx="150" cy="200" r="64" stroke="url(#cb-gold)" stroke-width="3"/>

  <!-- 8-Pointed Cradle of Echoes Celestial Star -->
  <polygon points="150,92 172,172 252,200 172,228 150,308 128,228 48,200 128,172" fill="url(#cb-gold)" stroke="#FFF3B0" stroke-width="2.5"/>
  <polygon points="150,126 166,184 224,200 166,216 150,274 134,216 76,200 134,184" fill="url(#cb-cyan)" opacity="0.88"/>
  <circle cx="150" cy="200" r="22" fill="#0B1021" stroke="url(#cb-gold)" stroke-width="4"/>
  <circle cx="150" cy="200" r="10" fill="url(#cb-cyan)"/>
</svg>
"""


def main() -> None:
    WEB_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_ICONS_DIR.mkdir(parents=True, exist_ok=True)

    manifest_items = []
    for spec in ICON_SPECS:
        svg_text = wrap_svg_256(spec["body"])
        web_path = WEB_ICONS_DIR / spec["filename"]
        unity_path = UNITY_ICONS_DIR / spec["filename"]
        web_path.write_text(svg_text, encoding="utf-8")
        unity_path.write_text(svg_text, encoding="utf-8")
        sha256_hex = hashlib.sha256(svg_text.encode("utf-8")).hexdigest()
        manifest_items.append(
            {
                "id": spec["id"],
                "filename": spec["filename"],
                "title": spec["title"],
                "category": spec["category"],
                "replaces": spec["replaces"],
                "palette": spec["palette"],
                "viewBox": "0 0 256 256",
                "web_path": str(web_path.relative_to(ROOT_DIR)),
                "unity_path": str(unity_path.relative_to(ROOT_DIR)),
                "bytes": len(svg_text.encode("utf-8")),
                "sha256": sha256_hex,
            }
        )

    # Write bespoke 3:4 Card-Back Astrolabe SVG
    cb_name = "cf_cardback_astrolabe.svg"
    for target_dir in (WEB_ICONS_DIR, UNITY_ICONS_DIR):
        (target_dir / cb_name).write_text(CARDBACK_ASTROLABE_SVG, encoding="utf-8")
    manifest_items.append(
        {
            "id": "cardback_astrolabe",
            "filename": cb_name,
            "title": "Cradle of Echoes Ornate Astrolabe Card Back (3:4)",
            "category": "deck_visual",
            "replaces": "Generic crescent moon deck card back",
            "palette": "#FFB800 / #00E5FF / #0B1021",
            "viewBox": "0 0 300 400",
            "web_path": f"WebPlayable/GeneratedArt/Icons/{cb_name}",
            "unity_path": f"Assets/Resources/UI/Icons/{cb_name}",
            "bytes": len(CARDBACK_ASTROLABE_SVG.encode("utf-8")),
            "sha256": hashlib.sha256(CARDBACK_ASTROLABE_SVG.encode("utf-8")).hexdigest(),
        }
    )

    manifest = {
        "library_name": "CARDFRONT: Cradle of Echoes — Original Atelier SVG Icon & Emblem Library",
        "house_style": "Synapse-Aether-Cel v1.0 (Arcane Atelier x Cyber-Ivalice)",
        "total_assets": len(manifest_items),
        "zero_generic_emojis": True,
        "zero_baked_raster_text": True,
        "assets": manifest_items,
    }
    manifest_path = WEB_ICONS_DIR / "icon_library_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (UNITY_ICONS_DIR / "icon_library_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Build visual gallery HTML for inspecting all original icons & card back
    cards_html = "\n".join(
        f"""
        <div class="icon-card">
          <img src="./{item['filename']}" alt="{item['title']}" />
          <div class="icon-title">{item['title']}</div>
          <div class="icon-meta"><code>{item['id']}</code> · {item['category']}</div>
        </div>
        """
        for item in manifest_items
    )
    gallery_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>CARDFRONT Atelier — Original SVG Icon & Emblem Library</title>
<style>
  body {{ background: #070b16; color: #f8fafc; font-family: system-ui, sans-serif; padding: 28px; }}
  h1 {{ color: #ffb800; font-size: 22px; margin-bottom: 6px; }}
  p {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(175px, 1fr)); gap: 14px; }}
  .icon-card {{ background: #0f172a; border: 1.5px solid #334155; border-radius: 12px; padding: 14px; text-align: center; }}
  .icon-card img {{ width: 72px; height: 72px; object-fit: contain; margin-bottom: 8px; }}
  .icon-title {{ font-size: 12px; font-weight: 800; color: #e2e8f0; margin-bottom: 4px; }}
  .icon-meta {{ font-size: 11px; color: #38bdf8; }}
</style>
</head>
<body>
  <h1>CARDFRONT: Cradle of Echoes — Original Atelier SVG Icon &amp; Emblem Library ({len(manifest_items)} Assets)</h1>
  <p>House Style: Arcane Atelier × Cyber-Ivalice · Zero Generic System Emojis · Code-Native Vector Art</p>
  <div class="grid">{cards_html}</div>
</body>
</html>
"""
    (WEB_ICONS_DIR / "icon_library_gallery.html").write_text(gallery_html, encoding="utf-8")
    print(json.dumps({"generated_assets": len(manifest_items), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
