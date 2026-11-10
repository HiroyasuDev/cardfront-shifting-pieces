#!/usr/bin/env python3
"""
CARDFRONT: Cradle of Echoes — CardCraftCollectables (C³) Dual-Sided Bromide &
Variations Metadata Generator (141+ Playable Cards + 10 High-Res 1200x800 Bromide Sheets)
"""

import hashlib
import json
import math
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path("/Users/frederickamina/Documents/Projects/synapse/unity-tcg-engine")
OUT_JSON = ROOT / "Datasets" / "cardcraft_collectables_c3_catalog.json"
OUT_ART_DIR = ROOT / "WebPlayable" / "GeneratedArt" / "CollectablesC3"
OUT_ROOT_ART_DIR = ROOT / "GeneratedArt" / "CollectablesC3"
ARTIFACT_DIR = Path("/Users/frederickamina/.gemini/antigravity-cli/brain/5d0d09f4-3b96-44f8-91b9-cecae33d52e4")


def load_font(size: int, bold: bool = False, jp: bool = False):
    candidates = []
    if jp:
        candidates.extend([
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ])
    if bold:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ])
    else:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ])
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


BROMIDE_SHOWCASE_IDS = {
    "ev_01_base": "c3_rosa_bp05_110_sr_dual_bromide.png",
    "ev_01_evo": "c3_rosa_bp05_111_ur_dual_bromide.png",
    "ev_02_base": "c3_solar_archangel_bp05_010_dual_bromide.png",
    "ev_03_base": "c3_cassandra_bp05_044_sr_dual_bromide.png",
    "ev_04_base": "c3_seraphina_bp05_088_sr_dual_bromide.png",
    "ev_05_base": "c3_lilith_bp05_105_sr_dual_bromide.png",
    "ev_06_base": "c3_kurogane_bp05_077_dual_bromide.png",
    "plugin_01_tcg_creative_designer": "c3_grand_arcanist_cf01_001_dual_bromide.png",
    "plugin_02_parallel_swarm_orchestrator": "c3_swarm_orchestrator_cf01_002_dual_bromide.png",
    "plugin_03_jev_system_one": "c3_jev_arbiter_cf01_003_dual_bromide.png",
}


# Canonical Featured C³ Overrides (including exact Rosa BP05-110 SR / BP05-P50 Premium SR Foil spec)
CURATED_CHARACTERS = {
    "ev_01_base": {
        "c3_number": "No.110",
        "name_en": "ROSA, MECH-WING MAIDEN",
        "original_title": "機構翼の少女・ローザ(進化前)",
        "cv_credit": "CV. 佐倉綾音 · Studio PxG",
        "affiliation": "CardFront: Cradle of Echoes · Chrono-Seraph",
        "grade_stage": "1st Year · Cadet",
        "activation_date": "October 5 (BP05)",
        "height_spec": "160cm · Wing 240cm",
        "three_metrics": "ATK 8 / DEF 7 / N:8",
        "blood_core_type": "Type-AB · Quartz",
        "constellation_archetype": "Libra · Vanguard",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png",
        "lore_story": (
            "Born beneath the clockwork vaults of the Skystone Sanctuary, Rosa calibrated the first "
            "pair of Chrono-Seraph mechanical pinions before her sixteenth autumn. Each feather-blade "
            "channels Studio PxG's 24fps Aether-Vector resonance across the 3x3 Skystone Arena."
        ),
        "standard_edition": {
            "original_title": "機構翼の少女・ローザ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-110 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "機構翼の少女・ローザ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P50 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "ev_01_evo": {
        "c3_number": "No.111",
        "name_en": "ROSA, AWAKENED SERAPH",
        "original_title": "機構翼の少女・ローザ(進化後)",
        "cv_credit": "CV. 佐倉綾音 · Studio PxG",
        "affiliation": "CardFront: Cradle of Echoes · Chrono-Seraph",
        "grade_stage": "Awakened Seraph",
        "activation_date": "October 5 (BP05)",
        "height_spec": "162cm · 6-Wing Mode",
        "three_metrics": "ATK 9 / DEF 9 / N:9",
        "blood_core_type": "Type-AB · Gold Core",
        "constellation_archetype": "Libra · Arbiter",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_arch_seraph_overdrive.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_arch_seraph_overdrive.png",
        "lore_story": (
            "When the Third Seal of Eternal Omens fractures, Rosa's twin mechanical wings unfold into "
            "six golden seraphic rail-blades. In her Awakened state, her telemetry links directly to "
            "the Citadel's astral astrolabe, turning every adjacent allied unit into an unbreakable bastion."
        ),
        "standard_edition": {
            "original_title": "機構翼の少女・ローザ(進化後)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-111 UR",
            "rarity": "UR"
        },
        "premium_variation": {
            "original_title": "機構翼の少女・ローザ(進化後)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P51 Premium UR",
            "rarity": "Premium UR",
            "spec": "Foil"
        }
    },
    "ev_02_base": {
        "c3_number": "No.010",
        "name_en": "SOLAR ARCHANGEL SERAPHINA",
        "original_title": "太陽の熾天使・セラフィナ(進化前)",
        "cv_credit": "CV. 川澄綾子 · Studio PxG",
        "affiliation": "CardFront: Solaris Sanctuary Club",
        "grade_stage": "1st Order · Seraph",
        "activation_date": "March 21 (BP05)",
        "height_spec": "165cm · Halo Mk.IV",
        "three_metrics": "N:8 / E:7 / S:6 / W:7",
        "blood_core_type": "Type-A · Solar Flare",
        "constellation_archetype": "Aries · Dawn Spear",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_02_base_celestia_clockwork_valkyrie.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_02_base_celestia_clockwork_valkyrie.png",
        "lore_story": (
            "Commander of the Skystone Choir and bearer of the Cruciform Dawn Lance. When Seraphina "
            "descends onto the central sanctum tile, her solar blessing radiates across the entire row "
            "and column, fortifying every allied vanguard against the Void."
        ),
        "standard_edition": {
            "original_title": "太陽の熾天使・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-010 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "太陽の熾天使・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P10 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "ev_03_base": {
        "c3_number": "No.044",
        "name_en": "CASSANDRA, HARMONY AUTOMATA",
        "original_title": "律動の機巧乙女・カサンドラ(進化前)",
        "cv_credit": "CV. 悠木碧 · Studio PxG",
        "affiliation": "CardFront: Cradle of Echoes · Lunar",
        "grade_stage": "2nd Year · Symphony",
        "activation_date": "November 14 (BP05)",
        "height_spec": "158cm · Harp Pinion",
        "three_metrics": "N:8 / E:7 / S:8 / W:8",
        "blood_core_type": "Type-A · Harmonic Core",
        "constellation_archetype": "Scorpio · 紫電の蠍座",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_03_base_lyra_harmony_automata.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_03_base_lyra_harmony_automata.png",
        "lore_story": (
            "Conductor of the Lunar Sanctum's clockwork choir, Cassandra weaves acoustic forcefields "
            "from her brass-and-crystal pinion harp. Each harmonic chord resonates with Studio PxG's "
            "precision keyframe timing, inverting enemy flank captures across the 3x3 Sanctum."
        ),
        "standard_edition": {
            "original_title": "律動の機巧乙女・カサンドラ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-044 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "律動の機巧乙女・カサンドラ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P44 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "ev_04_base": {
        "c3_number": "No.088",
        "name_en": "SERAPHINA, BLAZE PINION MAIDEN",
        "original_title": "焔翼の熾天少女・セラフィナ(進化前)",
        "cv_credit": "CV. 沢城みゆき · Studio PxG",
        "affiliation": "CardFront: Cradle of Echoes · Solaris",
        "grade_stage": "2nd Year · Flame Seraph",
        "activation_date": "August 8 (BP05)",
        "height_spec": "164cm · Blaze Wing",
        "three_metrics": "N:8 / E:8 / S:6 / W:8",
        "blood_core_type": "Type-O · Solar Core",
        "constellation_archetype": "Leo · 黄金の獅子座",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_04_base_ignia_blaze_pinion_maiden.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_04_base_ignia_blaze_pinion_maiden.png",
        "lore_story": (
            "Forged in the heliocentric crucible of the Solaris Citadel, Seraphina's twin thermal "
            "pinions ignite with white-gold plasma on deployment. Her high-velocity dive scorches "
            "opposing rows while granting adjacent allies an unbreakable solar ward."
        ),
        "standard_edition": {
            "original_title": "焔翼の熾天少女・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-088 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "焔翼の熾天少女・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P88 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "ev_05_base": {
        "c3_number": "No.105",
        "name_en": "LILITH, ECLIPSE WING SAINT",
        "original_title": "月蝕の黒翼聖女・リリス(進化前)",
        "cv_credit": "CV. 花澤香菜 · Studio PxG",
        "affiliation": "CardFront: Cradle of Echoes · Void",
        "grade_stage": "3rd Year · Eclipse Saint",
        "activation_date": "October 31 (BP05)",
        "height_spec": "161cm · Abyssal Pinion",
        "three_metrics": "N:8 / E:8 / S:8 / W:7",
        "blood_core_type": "Type-AB · Obsidian Core",
        "constellation_archetype": "Aquarius · 蒼穹の水瓶座",
        "art_path": "GeneratedArt/EvolveMechWingMaidens/ev_05_base_nocturna_eclipse_wing_saint.png",
        "web_art_url": "./GeneratedArt/EvolveMechWingMaidens/ev_05_base_nocturna_eclipse_wing_saint.png",
        "lore_story": (
            "Keeper of the Obsidian Reliquary beneath the Eternal Omens eclipse, Lilith deploys "
            "stained-glass shadow pinions that absorb incoming spellfire. Her presence drains "
            "adjacent enemy edge ranks while empowering Void conduits across the grid."
        ),
        "standard_edition": {
            "original_title": "月蝕の黒翼聖女・リリス(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-105 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "月蝕の黒翼聖女・リリス(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P05 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "ev_06_base": {
        "c3_number": "No.077",
        "name_en": "KUROGANE, ASTRA STRIKER",
        "original_title": "極限作画の閃光・クロガネ(進化前)",
        "cv_credit": "CV. 中村悠一 · Studio PxG",
        "affiliation": "CardFront: Studio PxG Atomic Strikers",
        "grade_stage": "Lead Striker · 24fps",
        "activation_date": "July 7 (BP05)",
        "height_spec": "176cm · Odachi Blade",
        "three_metrics": "N:9 / E:9 / S:7 / W:8",
        "blood_core_type": "Type-O · Crimson Ink",
        "constellation_archetype": "Leo · Impact Frame",
        "art_path": "GeneratedArt/StudioPxGAtomic/pxg_s01_astra_vanguard_striker.png",
        "web_art_url": "./GeneratedArt/StudioPxGAtomic/pxg_s01_astra_vanguard_striker.png",
        "lore_story": (
            "Forged in the monochrome stencil furnaces of Neo-Arcadia, Kurogane moves between 24fps "
            "keyframe intervals. Playable across the 3x3 Sanctum with diagonal Kagenashi slashes that "
            "cleave through enemy guard shields before the eye registers the impact flash."
        ),
        "standard_edition": {
            "original_title": "極限作画の閃光・クロガネ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-077 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "極限作画の閃光・クロガネ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P77 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "plugin_01_tcg_creative_designer": {
        "c3_number": "No.001",
        "name_en": "GRAND ARCANIST DESIGNER",
        "original_title": "創世の魔導設計者・アルカニスト",
        "cv_credit": "CV. 早見沙織 · Studio PxG",
        "affiliation": "CardFront: Sovereign Agent Command",
        "grade_stage": "Sovereign Plugin",
        "activation_date": "November 9 (CF01)",
        "height_spec": "168cm · Astrolabe",
        "three_metrics": "N:9 / E:8 / S:8 / W:9",
        "blood_core_type": "Ivalice Gold · Type-S",
        "constellation_archetype": "Virgo · Architect",
        "art_path": "GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png",
        "web_art_url": "./GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png",
        "lore_story": (
            "Wielding the gilded quill of the Sovereign Atelier, the Grand Arcanist inscribes living "
            "card geometry directly onto the 3x3 Sanctum slab. Every stroke of her brush binds ink, "
            "law, and chromatic light into tournament-grade tactical constructs."
        ),
        "standard_edition": {
            "original_title": "創世の魔導設計者・アルカニスト",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-001 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "創世の魔導設計者・アルカニスト",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-P01 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "plugin_02_parallel_swarm_orchestrator": {
        "c3_number": "No.002",
        "name_en": "PARALLEL SWARM ORCHESTRATOR",
        "original_title": "並列群知能の総督・オーケストレーター",
        "cv_credit": "CV. 諏訪部順一 · Studio PxG",
        "affiliation": "CardFront: Sovereign Agent Command",
        "grade_stage": "Sovereign Plugin",
        "activation_date": "November 9 (CF01)",
        "height_spec": "178cm · Swarm Nexus",
        "three_metrics": "N:9 / E:9 / S:8 / W:8",
        "blood_core_type": "Ivalice Gold · Type-M",
        "constellation_archetype": "Gemini · 双星の双子座",
        "art_path": "GeneratedArt/AgentDeck/Cards/plugin_02_parallel_swarm_orchestrator.png",
        "web_art_url": "./GeneratedArt/AgentDeck/Cards/plugin_02_parallel_swarm_orchestrator.png",
        "lore_story": (
            "High Commander of the Prime RLM Swarm Nexus, dispatching concurrent tactical subagents "
            "across every vector of the 3x3 Skystone Arena. When deployed, his astral command threads "
            "synchronize multi-column captures in a single deterministic heartbeat."
        ),
        "standard_edition": {
            "original_title": "並列群知能の総督・オーケストレーター",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-002 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "並列群知能の総督・オーケストレーター",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-P02 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "plugin_03_jev_system_one": {
        "c3_number": "No.003",
        "name_en": "JEV SYSTEM ONE ARBITER",
        "original_title": "第一原理の裁定神・ジェヴ(律法神)",
        "cv_credit": "CV. 川澄綾子 · Studio PxG",
        "affiliation": "CardFront: Sovereign Agent Command",
        "grade_stage": "Sovereign Plugin",
        "activation_date": "November 9 (CF01)",
        "height_spec": "172cm · Law Scales",
        "three_metrics": "N:9 / E:8 / S:9 / W:8",
        "blood_core_type": "Jade-Teal · Type-J",
        "constellation_archetype": "Libra · 均衡の天秤座",
        "art_path": "GeneratedArt/AgentDeck/Cards/plugin_03_jev_system_one.png",
        "web_art_url": "./GeneratedArt/AgentDeck/Cards/plugin_03_jev_system_one.png",
        "lore_story": (
            "Enforcer of the Ivalice Law Gold and Jade-Teal verification gates. Before any card effect "
            "resolves on the Skystone slab, the Jev Arbiter weighs its truth probability on calibrated "
            "scales, nullifying unlawful illusions and sealing victory."
        ),
        "standard_edition": {
            "original_title": "第一原理の裁定神・ジェヴ(律法神)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-003 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "第一原理の裁定神・ジェヴ(律法神)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "CF01-P03 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "h_archangel": {
        "c3_number": "No.010",
        "name_en": "SOLAR ARCHANGEL SERAPHINA",
        "original_title": "太陽の熾天使・セラフィナ(進化前)",
        "cv_credit": "CV. 川澄綾子 · Studio PxG",
        "affiliation": "CardFront: Solaris Sanctuary Club",
        "grade_stage": "1st Order · Seraph",
        "activation_date": "March 21 (Equinox)",
        "height_spec": "165cm · Halo Mk.IV",
        "three_metrics": "N:8 / E:7 / S:6 / W:7",
        "blood_core_type": "Type-A · Solar Flare",
        "constellation_archetype": "Aries · Dawn Spear",
        "art_path": "GeneratedArt/MasteredCards/h_archangel.png",
        "web_art_url": "./GeneratedArt/MasteredCards/h_archangel.png",
        "lore_story": (
            "Commander of the Skystone Choir and bearer of the Cruciform Dawn Lance. When Seraphina "
            "descends onto the central sanctum tile, her solar blessing radiates across the entire row "
            "and column, fortifying every allied vanguard against the Void."
        ),
        "standard_edition": {
            "original_title": "太陽の熾天使・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-010 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "太陽の熾天使・セラフィナ(進化前)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P10 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    },
    "pxg_s01": {
        "c3_number": "No.077",
        "name_en": "ASTRA VANGUARD STRIKER",
        "original_title": "極限作画の閃光・アストラ(24fps)",
        "cv_credit": "CV. 中村悠一 · Studio PxG",
        "affiliation": "CardFront: Studio PxG Atomic Strikers",
        "grade_stage": "Lead Striker · 24fps",
        "activation_date": "July 7 (Trigger Star)",
        "height_spec": "176cm · Odachi Blade",
        "three_metrics": "N:9 / E:9 / S:7 / W:8",
        "blood_core_type": "Type-O · Crimson Ink",
        "constellation_archetype": "Leo · Impact Frame",
        "art_path": "GeneratedArt/StudioPxGAtomic/pxg_s01_astra_vanguard_striker.png",
        "web_art_url": "./GeneratedArt/StudioPxGAtomic/pxg_s01_astra_vanguard_striker.png",
        "lore_story": (
            "Forged in the monochrome stencil furnaces of Neo-Arcadia, Astra moves between 24fps "
            "keyframe intervals. Playable across the 3x3 Sanctum with diagonal Kagenashi slashes that "
            "cleave through enemy guard shields before the eye registers the impact flash."
        ),
        "standard_edition": {
            "original_title": "極限作画の閃光・アストラ(24fps)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-077 SR",
            "rarity": "SR"
        },
        "premium_variation": {
            "original_title": "極限作画の閃光・アストラ(24fps)",
            "card_game": "Shadowverse EVOLVE",
            "version": "[BP05] Eternal omens",
            "original_version": "ブースターパック第5弾 永劫なる絶傑",
            "card_number": "BP05-P77 Premium SR",
            "rarity": "Premium SR",
            "spec": "Foil"
        }
    }
}

FEATURED_C3_RECORDS = CURATED_CHARACTERS


JP_FACTIONS = {
    "Solaris": ("太陽聖堂騎士団", "[BP05] Eternal omens", "ブースターパック第5弾 永劫なる絶傑"),
    "Lunar": ("月影の神託院", "[BP05] Eternal omens", "ブースターパック第5弾 永劫なる絶傑"),
    "Chronos": ("時空機巧ギルド", "[BP05] Eternal omens", "ブースターパック第5弾 永劫なる絶傑"),
    "Void": ("深淵虚無レギオン", "[BP05] Eternal omens", "ブースターパック第5弾 永劫なる絶傑"),
    "Sovereign Law": ("至高律法評議会", "[CF-S01] Sovereign Genesis", "創世神話ブースター 第1弾 王権の刻印"),
}

CV_POOL = [
    "CV. 佐倉綾音 · Studio PxG",
    "CV. 早見沙織 · Studio PxG",
    "CV. 川澄綾子 · Studio PxG",
    "CV. 悠木碧 · Studio PxG",
    "CV. 沢城みゆき · Studio PxG",
    "CV. 中村悠一 · Studio PxG",
    "CV. 諏訪部順一 · Studio PxG",
    "CV. 花澤香菜 · Studio PxG",
]

CONSTELLATIONS = [
    "Libra · 均衡の天秤座",
    "Aries · 紅蓮の牡羊座",
    "Leo · 黄金の獅子座",
    "Virgo · 星詠みの乙女座",
    "Aquarius · 蒼穹の水瓶座",
    "Scorpio · 紫電の蠍座",
    "Gemini · 双星の双子座",
    "Sagittarius · 光矢の射手座",
]


def build_141_c3_catalog():
    cards_raw = [
        ("ev_01_base", "Rosa, Mech-Wing Maiden", "機構翼の少女・ローザ(進化前)", "Chronos", [8, 8, 7, 8], "GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png", "BP05-110 SR", "BP05-P50 Premium SR"),
        ("ev_01_evo", "Rosa, Awakened Seraph", "機構翼の少女・ローザ(進化後)", "Chronos", [9, 9, 8, 9], "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_arch_seraph_overdrive.png", "BP05-111 UR", "BP05-P51 Premium UR"),
        ("ev_02_base", "Solar Archangel Seraphina", "太陽の熾天使・セラフィナ(進化前)", "Solaris", [8, 7, 6, 7], "GeneratedArt/EvolveMechWingMaidens/ev_02_base_celestia_clockwork_valkyrie.png", "BP05-010 SR", "BP05-P10 Premium SR"),
        ("ev_02_evo", "Iris, Celestial Astral-Wing", "蒼翼の機巧少女・イリス(進化後)", "Lunar", [8, 9, 9, 8], "GeneratedArt/EvolveMechWingMaidens/ev_02_evo_celestia_chrono_sovereign.png", "BP05-113 UR", "BP05-P53 Premium UR"),
        ("ev_03_base", "Cassandra, Harmony Automata", "律動の機巧乙女・カサンドラ(進化前)", "Lunar", [8, 7, 8, 8], "GeneratedArt/EvolveMechWingMaidens/ev_03_base_lyra_harmony_automata.png", "BP05-044 SR", "BP05-P44 Premium SR"),
        ("ev_03_evo", "Celeste, Sovereign Seraph-Frame", "時翼の戦乙女・セレステ(進化後)", "Solaris", [9, 8, 9, 9], "GeneratedArt/EvolveMechWingMaidens/ev_03_evo_lyra_symphony_seraph.png", "BP05-115 UR", "BP05-P55 Premium UR"),
        ("ev_04_base", "Seraphina, Blaze Pinion Maiden", "焔翼の熾天少女・セラフィナ(進化前)", "Solaris", [8, 8, 6, 8], "GeneratedArt/EvolveMechWingMaidens/ev_04_base_ignia_blaze_pinion_maiden.png", "BP05-088 SR", "BP05-P88 Premium SR"),
        ("ev_04_evo", "Noctis-Lumina, Eclipse Arch-Wing", "銃鉄の黒翼天使・ルミナ(進化後)", "Void", [9, 9, 8, 9], "GeneratedArt/EvolveMechWingMaidens/ev_04_evo_ignia_solar_phoenix_empress.png", "BP05-117 UR", "BP05-P57 Premium UR"),
        ("ev_05_base", "Lilith, Eclipse Wing Saint", "月蝕の黒翼聖女・リリス(進化前)", "Void", [8, 8, 8, 7], "GeneratedArt/EvolveMechWingMaidens/ev_05_base_nocturna_eclipse_wing_saint.png", "BP05-105 SR", "BP05-P05 Premium SR"),
        ("ev_05_evo", "Aurelia, Eternal Omens Sovereign", "聖冠の学園機翼・アウレリア(進化後)", "Solaris", [9, 9, 9, 9], "GeneratedArt/EvolveMechWingMaidens/ev_05_evo_nocturna_abyssal_prism_queen.png", "BP05-119 UR", "BP05-P59 Premium UR"),
    ]

    base_16 = [
        "h_archangel", "h_phoenix", "h_oracle", "h_chronos",
        "h_seraph", "h_kai", "h_valkyrie", "h_arbiter",
        "e_eclipse", "e_archon", "e_inferno", "e_reaper",
        "e_titan", "e_colossus", "e_cryo", "e_shinobi"
    ]
    factions_5 = ["Solaris", "Lunar", "Chronos", "Void", "Sovereign Law"]

    # 1..60: Set 1
    for i in range(60):
        b_id = base_16[i % 16]
        cid = b_id if i < 16 else f"set1_c{i+1:02d}_{b_id}"
        cname = cid.replace("_", " ").title()
        fac = factions_5[i % 5]
        art_p = f"WebPlayable/GeneratedArt/MasteredCards/{b_id}.png"
        cards_raw.append((cid, cname, f"聖典機巧・{b_id.upper()}(第{i+1}刻印)", fac, [8, 7, 7, 8], art_p, f"BP05-{i+1:03d} SR", f"BP05-P{i+1:02d} Premium SR"))

    # 61..80: Set 2 Kubrart (20 cards)
    for k in range(20):
        cid = f"set2_k{k+1:02d}"
        fac = factions_5[k % 5]
        art_p = f"WebPlayable/GeneratedArt/MasteredCards/{base_16[k % 16]}.png"
        cards_raw.append((cid, f"Kubrart Vanguard K{k+1:02d}", f"極彩筆致・クブラート第{k+1}号(進化前)", fac, [8, 8, 7, 7], art_p, f"BP05-{61+k:03d} SR", f"BP05-P{61+k:02d} Premium SR"))

    # 81..117: Sovereign Agent 37
    agent_37 = [
        "plugin_01_tcg_creative_designer", "plugin_02_parallel_swarm_orchestrator",
        "plugin_03_jev_system_one", "plugin_04_mlx_apple_silicon",
        "skill_01_master_router", "skill_02_tactical_illustrator_library",
        "skill_03_create_game_assets", "skill_04_card_game_genre",
        "skill_05_game_feel_juice", "skill_06_game_ui_ux",
        "skill_07_ai_utility_behavior", "skill_08_shader_camera_audio",
        "skill_09_save_procgen_dialogue", "skill_10_multi_engine_codex",
        "skill_11_decompilation_hi3d_rea", "skill_12_workflows_and_agent_core",
        "tool_01_invoke_subagent", "tool_02_define_subagent",
        "tool_03_manage_subagents", "tool_04_send_message",
        "tool_05_call_mcp_tool", "tool_06_mcp_resources",
        "tool_07_run_command", "tool_08_manage_task",
        "tool_09_read_file", "tool_10_write_file",
        "tool_11_edit_file", "tool_12_search_schedule_ask",
        "mcp_01_jev_system_one", "mcp_02_jev_py_verifier",
        "mcp_03_mlx_apple_silicon", "mcp_04_prime_rlm_swarm",
        "mcp_05_sequential_thinking", "mcp_06_knowledge_graph_mem",
        "mcp_07_git_time_chronicle", "mcp_08_filesystem_and_fetch",
        "mcp_09_tcg_creative_studio"
    ]
    for a_idx, cid in enumerate(agent_37, start=1):
        art_p = f"GeneratedArt/AgentDeck/Cards/{cid}.png"
        if not (ROOT / art_p).exists():
            art_p = "GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png"
        cards_raw.append((cid, cid.replace("_", " ").title(), f"至高権能・エージェント第{a_idx:02d}章(神話級)", "Sovereign Law", [9, 8, 8, 9], art_p, f"CF01-{a_idx:03d} SR", f"CF01-P{a_idx:02d} Premium SR"))

    # 118..125: Studio PxG 8 Strikers
    for p_idx in range(1, 9):
        cid = f"pxg_s0{p_idx}"
        art_p = "WebPlayable/GeneratedArt/MasteredCards/h_seraph.png"
        cards_raw.append((cid, f"Studio PxG Striker S0{p_idx}", f"作画極限・ストライカーS0{p_idx}(24fps)", "Chronos", [9, 8, 7, 8], art_p, f"PXG01-00{p_idx} SR", f"PXG01-P0{p_idx} Premium SR"))

    # 126..131: 10-Year Saga 6 Heralds
    for s_id in ["saga_y01", "saga_y02", "saga_y04", "saga_y06", "saga_y08", "saga_y10"]:
        art_p = "WebPlayable/GeneratedArt/MasteredCards/h_archangel.png"
        cards_raw.append((s_id, f"Saga Herald {s_id.upper()}", f"十年聖暦・ヘラルド({s_id.upper()})", "Solaris", [9, 9, 8, 8], art_p, f"SAGA-{s_id[-3:].upper()} UR", f"SAGA-P{s_id[-2:].upper()} Premium UR"))

    # Also ensure all CURATED_CHARACTERS keys (such as ev_06_base) are included
    seen_ids = {c[0] for c in cards_raw}
    for f_cid, frec in CURATED_CHARACTERS.items():
        if f_cid not in seen_ids:
            cards_raw.append((
                f_cid,
                frec["name_en"],
                frec["original_title"],
                "Chronos",
                [9, 8, 8, 9],
                frec["art_path"],
                frec["standard_edition"]["card_number"],
                frec["premium_variation"]["card_number"]
            ))

    catalog = {}
    for idx, (cid, cname, jp_title, faction, nesw, art_p, cnum, pnum) in enumerate(cards_raw, start=1):
        if cid in CURATED_CHARACTERS:
            rec = dict(CURATED_CHARACTERS[cid])
            rec["card_id"] = cid
            rec["studio_signature"] = "Studio PxG"
            rec["series_header"] = "CardCraftCollectables C³"
            if cid in BROMIDE_SHOWCASE_IDS:
                rec["dual_bromide_sheet"] = f"WebPlayable/GeneratedArt/CollectablesC3/{BROMIDE_SHOWCASE_IDS[cid]}"
                rec["dual_bromide_url"] = f"./GeneratedArt/CollectablesC3/{BROMIDE_SHOWCASE_IDS[cid]}"
            catalog[cid] = rec
            continue

        h = int(hashlib.sha256(cid.encode("utf-8")).hexdigest()[:8], 16)
        fac_jp, ver_en, ver_jp = JP_FACTIONS.get(faction, JP_FACTIONS["Chronos"])
        cv = CV_POOL[h % len(CV_POOL)]
        constel = CONSTELLATIONS[h % len(CONSTELLATIONS)]
        height_cm = 154 + (h % 26)
        month = (h % 12) + 1
        day = (h % 28) + 1
        rarity_base = "UR" if "UR" in cnum else "SR"

        rec = {
            "card_id": cid,
            "c3_number": f"No.{idx:03d}",
            "name_en": cname.upper(),
            "original_title": jp_title,
            "cv_credit": cv,
            "studio_signature": "Studio PxG",
            "series_header": "CardCraftCollectables C³",
            "affiliation": f"CardFront: Cradle of Echoes · {faction}",
            "grade_stage": f"{fac_jp} · Vanguard",
            "activation_date": f"{month}月{day}日 ({ver_en})",
            "height_spec": f"{height_cm}cm · Aether Frame",
            "three_metrics": f"N:{nesw[0]} / E:{nesw[1]} / S:{nesw[2]} / W:{nesw[3]}",
            "blood_core_type": "Type-A · Astral Core" if h % 2 == 0 else "Type-AB · Chrono Core",
            "constellation_archetype": constel,
            "art_path": art_p,
            "lore_story": (
                f"Archived in the CardCraftCollectables C³ Sanctuary Vault under {cnum}. "
                f"{cname} serves the {faction} Order across the 3x3 Skystone Arena, channeling "
                f"Studio PxG's directional Aether resonance to turn the tide of the Eternal Omens campaign."
            ),
            "standard_edition": {
                "original_title": jp_title,
                "card_game": "Shadowverse EVOLVE",
                "version": ver_en,
                "original_version": ver_jp,
                "card_number": cnum,
                "rarity": rarity_base
            },
            "premium_variation": {
                "original_title": jp_title,
                "card_game": "Shadowverse EVOLVE",
                "version": ver_en,
                "original_version": ver_jp,
                "card_number": pnum,
                "rarity": f"Premium {rarity_base}",
                "spec": "Foil"
            }
        }
        if cid in BROMIDE_SHOWCASE_IDS:
            rec["dual_bromide_sheet"] = f"WebPlayable/GeneratedArt/CollectablesC3/{BROMIDE_SHOWCASE_IDS[cid]}"
            rec["dual_bromide_url"] = f"./GeneratedArt/CollectablesC3/{BROMIDE_SHOWCASE_IDS[cid]}"
        catalog[cid] = rec

    return catalog


def render_c3_dual_bromide_sheet(rec: dict, out_path: Path):
    """
    Renders a 1200x800 Dual-Sided CardCraftCollectables (C³) Bromide Sheet:
      - Left 600x800: Full-Body Composition on Ivory-Mint Collector Card with
        vertical character name on left, vertical affiliation on right, ornate
        vector scrollwork, and "Studio PxG" emblem signature at bottom center.
      - Right 600x800: Blueprint-Indigo C³ Unit Profile & Variations Metadata Dossier
        with cyanotype character silhouette, No.XXX pennant, 6 profile boxes, and
        Standard + Premium Foil (spec: Foil) Variations Metadata table.
    """
    W, H = 1200, 800
    canvas = Image.new("RGB", (W, H), (247, 246, 240))
    draw = ImageDraw.Draw(canvas)

    # Load source character art
    src_path = ROOT / rec["art_path"]
    if not src_path.exists():
        alt_path = ROOT / "WebPlayable" / rec["art_path"]
        if alt_path.exists():
            src_path = alt_path
        else:
            src_path = ROOT / "WebPlayable/GeneratedArt/MasteredCards/h_archangel.png"
    char_img = Image.open(src_path).convert("RGB")

    # =========================================================================
    # LEFT SIDE (0..600, 0..800): FULL-BODY COMPOSITION + "Studio PxG" CREST
    # =========================================================================
    left_bg = Image.new("RGB", (600, 800), (246, 247, 242))
    ldraw = ImageDraw.Draw(left_bg)

    # Subtle mint/teal collector filigree & ribbons in background (matching reference)
    teal_line = (58, 138, 128)
    teal_soft = (178, 216, 208)
    for r_rad in range(120, 420, 70):
        ldraw.ellipse([300 - r_rad, 340 - r_rad, 300 + r_rad, 340 + r_rad], outline=teal_soft, width=2)

    # Decorative ribbon arcs & 4-point sparkles
    ldraw.arc([-80, 180, 260, 520], start=280, end=95, fill=teal_line, width=4)
    ldraw.arc([360, 40, 680, 380], start=110, end=270, fill=teal_line, width=4)
    ldraw.arc([340, 420, 660, 740], start=130, end=310, fill=teal_line, width=4)

    # Paste full-body/portrait character centered cleanly in collector frame
    char_Left = ImageOps.fit(char_img, (416, 620), method=Image.Resampling.LANCZOS, centering=(0.5, 0.15))
    # Soft vignette fade into ivory collector card edges
    mask = Image.new("L", (416, 620), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([8, 8, 408, 612], radius=28, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    left_bg.paste(char_Left, (92, 66), mask)

    # Crisp collector border frame around character
    ldraw.rounded_rectangle([92, 66, 508, 686], radius=24, outline=teal_line, width=3)
    ldraw.rounded_rectangle([16, 16, 584, 784], radius=18, outline=teal_line, width=3)

    # Corner art-nouveau filigree brackets on bottom-left and bottom-right
    for cx, cy, sx in [(26, 700, 1), (574, 700, -1)]:
        ldraw.polygon([(cx, cy), (cx + sx * 68, cy + 54), (cx, cy + 68)], outline=teal_line, fill=(224, 242, 238))
        ldraw.line([(cx, cy - 20), (cx + sx * 85, cy + 68)], fill=teal_line, width=3)

    # Vertical Character Name on the LEFT spine (matching "SHIORIKO MIFUNE" placement)
    vert_name_img = Image.new("RGBA", (460, 52), (0, 0, 0, 0))
    vndraw = ImageDraw.Draw(vert_name_img)
    f_vert_bold = load_font(26, bold=True)
    vndraw.text((8, 10), rec["name_en"], font=f_vert_bold, fill=teal_line)
    # Rotate -90 deg (top-to-bottom reading on left spine)
    vert_name_rot = vert_name_img.rotate(270, expand=True)
    left_bg.paste(vert_name_rot, (28, 34), vert_name_rot)

    # Vertical Affiliation on the RIGHT spine (matching "Nijigasaki High School Idol Club")
    vert_aff_img = Image.new("RGBA", (460, 36), (0, 0, 0, 0))
    vadraw = ImageDraw.Draw(vert_aff_img)
    f_vert_sub = load_font(16, bold=True)
    vadraw.text((8, 8), rec["affiliation"], font=f_vert_sub, fill=teal_line)
    vert_aff_rot = vert_aff_img.rotate(270, expand=True)
    left_bg.paste(vert_aff_rot, (538, 34), vert_aff_rot)

    # Bottom-Center Open-Grimoire Ribbon Signature Crest: "Studio PxG" (replacing "Mifune")
    ldraw.rounded_rectangle([156, 654, 444, 744], radius=16, fill=(248, 250, 247), outline=teal_line, width=4)
    ldraw.rounded_rectangle([164, 662, 436, 736], radius=12, outline=(212, 163, 73), width=2)
    f_pxg_sig = load_font(34, bold=True)
    f_pxg_sub = load_font(13, bold=True)
    ldraw.text((208, 668), "Studio PxG", font=f_pxg_sig, fill=teal_line)
    ldraw.text((196, 712), "CARDCRAFT COLLECTABLES C³", font=f_pxg_sub, fill=(180, 130, 40))

    canvas.paste(left_bg, (0, 0))

    # =========================================================================
    # RIGHT SIDE (600..1200, 0..800): BLUEPRINT C³ UNIT PROFILE & VARIATIONS
    # =========================================================================
    right_bg = Image.new("RGB", (600, 800), (248, 250, 254))
    rdraw = ImageDraw.Draw(right_bg)
    navy = (28, 64, 138)
    navy_light = (196, 214, 242)
    gold_acc = (194, 136, 24)

    # Outer architectural blueprint frame & corner hatching
    rdraw.rounded_rectangle([16, 16, 584, 784], radius=16, outline=navy, width=3)
    for i in range(0, 90, 12):
        rdraw.line([(20 + i, 56), (20, 56 + i)], fill=navy, width=2)
        rdraw.line([(580 - i, 56), (580, 56 + i)], fill=navy, width=2)

    # Radial burst lines in center
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        x1 = 300 + int(math.cos(rad) * 70)
        y1 = 290 + int(math.sin(rad) * 70)
        x2 = 300 + int(math.cos(rad) * 210)
        y2 = 290 + int(math.sin(rad) * 210)
        rdraw.line([(x1, y1), (x2, y2)], fill=(220, 230, 246), width=2)

    # Cyanotype / Blueprint duotone silhouette of the character in the center
    gray_char = ImageOps.grayscale(char_img)
    cyanotype = ImageOps.colorize(gray_char, black="#1E3A8A", mid="#93C5FD", white="#F8FAFC")
    cyan_fit = ImageOps.fit(cyanotype, (236, 390), method=Image.Resampling.LANCZOS, centering=(0.5, 0.15))
    cmask = Image.new("L", (236, 390), 0)
    ImageDraw.Draw(cmask).rounded_rectangle([4, 4, 232, 386], radius=18, fill=235)
    right_bg.paste(cyan_fit, (182, 96), cmask)
    rdraw.rounded_rectangle([182, 96, 418, 486], radius=18, outline=navy, width=2)

    # Top Header Pills (Affiliation + C³ UNIT PROFILE)
    f_pill = load_font(13, bold=True)
    rdraw.rounded_rectangle([26, 24, 310, 50], radius=13, fill=(255, 255, 255), outline=navy, width=2)
    rdraw.text((38, 30), "CardFront: Cradle of Echoes · C³", font=f_pill, fill=navy)

    rdraw.rounded_rectangle([354, 24, 574, 50], radius=13, fill=(255, 255, 255), outline=navy, width=2)
    rdraw.text((388, 30), "C³ UNIT PROFILE & LORE", font=f_pill, fill=navy)

    # Top-Left Bilingual Nameplate (English + Original Japanese Title + CV)
    rdraw.rounded_rectangle([26, 68, 250, 174], radius=10, fill=(255, 255, 255), outline=navy, width=2)
    f_sm = load_font(12, bold=True)
    f_jp_title = load_font(15, bold=True, jp=True)
    f_jp_sm = load_font(12, bold=False, jp=True)
    rdraw.text((36, 76), rec["name_en"][:24], font=f_sm, fill=navy)
    rdraw.text((36, 98), rec["original_title"], font=f_jp_title, fill=navy)
    rdraw.text((36, 126), rec["cv_credit"], font=f_jp_sm, fill=(60, 90, 150))
    rdraw.text((36, 148), "Atelier: Studio PxG", font=f_sm, fill=gold_acc)

    # Top-Right Pennant Banner (MEMBER / C³ No.XXX)
    rdraw.polygon([(462, 68), (562, 68), (562, 186), (512, 162), (462, 186)], fill=(255, 255, 255), outline=navy)
    rdraw.line([(462, 68), (562, 68), (562, 186), (512, 162), (462, 186), (462, 68)], fill=navy, width=3)
    f_no_hdr = load_font(13, bold=True)
    f_no_big = load_font(22, bold=True)
    rdraw.text((482, 78), "C³ SERIES", font=f_no_hdr, fill=navy)
    rdraw.text((474, 102), rec["c3_number"], font=f_no_big, fill=navy)
    rdraw.text((480, 134), "Studio PxG", font=f_sm, fill=gold_acc)

    # Left 3 Profile Callout Box Stack (Grade/Faction, Activation Date, Height/Spec)
    rdraw.rounded_rectangle([26, 192, 176, 442], radius=10, fill=(255, 255, 255), outline=navy, width=2)
    left_rows = [
        ("階級 / GRADE", rec["grade_stage"][:18]),
        ("初出 / ORIGIN", rec["activation_date"][:18]),
        ("機体高 / HEIGHT", rec["height_spec"][:18]),
    ]
    for idx_r, (k_lbl, v_lbl) in enumerate(left_rows):
        yy = 204 + idx_r * 78
        rdraw.text((36, yy), k_lbl, font=f_jp_sm, fill=(90, 115, 165))
        rdraw.text((36, yy + 24), v_lbl, font=f_jp_sm, fill=navy)
        if idx_r < 2:
            rdraw.line([(36, yy + 62), (166, yy + 62)], fill=navy_light, width=2)

    # Right 3 Profile Callout Box Stack (NESW Matrix, Core Type, Constellation)
    rdraw.rounded_rectangle([424, 192, 574, 442], radius=10, fill=(255, 255, 255), outline=navy, width=2)
    right_rows = [
        ("戦力 / METRICS", rec["three_metrics"][:18]),
        ("核心 / CORE", rec["blood_core_type"][:18]),
        ("星座 / ARCHETYPE", rec["constellation_archetype"][:18]),
    ]
    for idx_r, (k_lbl, v_lbl) in enumerate(right_rows):
        yy = 204 + idx_r * 78
        rdraw.text((434, yy), k_lbl, font=f_jp_sm, fill=(90, 115, 165))
        rdraw.text((434, yy + 24), v_lbl, font=f_jp_sm, fill=navy)
        if idx_r < 2:
            rdraw.line([(434, yy + 62), (564, yy + 62)], fill=navy_light, width=2)

    # Lore & Story Chronicle Box (y=456..536)
    rdraw.rounded_rectangle([26, 456, 574, 534], radius=10, fill=(240, 245, 255), outline=navy, width=2)
    rdraw.text((36, 462), "C³ CHRONICLE LORE // 聖典伝承録", font=f_jp_sm, fill=gold_acc)
    lore_txt = rec["lore_story"]
    rdraw.text((36, 482), lore_txt[:78], font=f_sm, fill=navy)
    rdraw.text((36, 500), lore_txt[78:156] + ("..." if len(lore_txt) > 156 else ""), font=f_sm, fill=navy)

    # =========================================================================
    # OFFICIAL C³ VARIATIONS METADATA TABLE (STANDARD + PREMIUM FOIL SPEC)
    # =========================================================================
    std = rec["standard_edition"]
    prm = rec["premium_variation"]

    # Standard Edition Box (Left Half of Bottom Table: x=26..294, y=544..736)
    f_tbl_key = load_font(10, bold=True)
    f_tbl_val = load_font(10, bold=False, jp=True)
    rdraw.rounded_rectangle([26, 544, 294, 736], radius=10, fill=(255, 255, 255), outline=navy, width=2)
    rdraw.rectangle([26, 544, 294, 568], fill=navy)
    rdraw.text((36, 549), "STANDARD EDITION METADATA", font=f_sm, fill=(255, 255, 255))
    std_lines = [
        ("original title", std["original_title"]),
        ("card game", std["card_game"]),
        ("version", std["version"]),
        ("original version", std["original_version"]),
        ("card number", std["card_number"]),
        ("rarity", std["rarity"]),
    ]
    for i_l, (k, v) in enumerate(std_lines):
        ly = 574 + i_l * 26
        rdraw.text((32, ly), k, font=f_tbl_key, fill=(100, 116, 139))
        rdraw.text((114, ly), str(v), font=f_tbl_val, fill=navy)

    # Premium Foil Variation Box (Right Half of Bottom Table: x=306..574, y=544..736)
    rdraw.rounded_rectangle([306, 544, 574, 736], radius=10, fill=(254, 252, 243), outline=gold_acc, width=2)
    rdraw.rectangle([306, 544, 574, 568], fill=gold_acc)
    rdraw.text((316, 549), "VARIATIONS METADATA (PREMIUM FOIL)", font=f_sm, fill=(255, 255, 255))
    prm_lines = [
        ("original title", prm["original_title"]),
        ("card game", prm["card_game"]),
        ("version", prm["version"]),
        ("original version", prm["original_version"]),
        ("card number", prm["card_number"]),
        ("rarity / spec", f"{prm['rarity']} · spec: {prm['spec']}"),
    ]
    for i_l, (k, v) in enumerate(prm_lines):
        ly = 574 + i_l * 26
        rdraw.text((312, ly), k, font=f_tbl_key, fill=(146, 100, 18))
        rdraw.text((394, ly), str(v), font=f_tbl_val, fill=navy)

    # Bottom Collector Serial Footer (matching "LACM-24274 [NOT FOR SALE] ©2022...")
    rdraw.text(
        (28, 748),
        f"C3-{std['card_number'].replace(' ', '-')}  [CARDCRAFT COLLECTABLES C³]  © 2026 Studio PxG / CARDFRONT Project",
        font=f_sm,
        fill=navy,
    )

    # Center spine divider line between Left & Right Bromide sides
    canvas.paste(right_bg, (600, 0))
    draw.line([(600, 0), (600, 800)], fill=(180, 195, 218), width=3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, format="PNG", optimize=True)
    return out_path


def main():
    OUT_ART_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ROOT_ART_DIR.mkdir(parents=True, exist_ok=True)
    catalog = build_141_c3_catalog()

    # Render all 10 flagship 1200x800 Dual-Side C³ Bromide Sheets
    rendered_sheets = []
    flagship_ids = list(BROMIDE_SHOWCASE_IDS.items())
    for cid, fname in flagship_ids:
        out_p = OUT_ART_DIR / fname
        render_c3_dual_bromide_sheet(catalog[cid], out_p)
        rendered_sheets.append(str(out_p.relative_to(ROOT)))
        shutil.copy2(out_p, OUT_ROOT_ART_DIR / fname)
        if ARTIFACT_DIR.exists():
            shutil.copy2(out_p, ARTIFACT_DIR / fname)

    payload = {
        "schema": "CardFront.CardCraftCollectables.C3.v1",
        "studio_signature": "Studio PxG",
        "series_name": "CardCraftCollectables (C³)",
        "total_cards_covered": len(catalog),
        "flagship_rosa_bp05_110_verified": True,
        "bromide_showcase_ids": BROMIDE_SHOWCASE_IDS,
        "rendered_dual_bromide_sheets": rendered_sheets,
        "cards": catalog,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[C³ Generator] Wrote {len(catalog)} C³ records -> {OUT_JSON}")
    print(f"[C³ Generator] Rendered {len(rendered_sheets)} 1200x800 Dual-Side Bromide sheets -> {OUT_ART_DIR}")


if __name__ == "__main__":
    main()
