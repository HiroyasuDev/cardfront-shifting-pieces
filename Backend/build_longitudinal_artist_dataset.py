#!/usr/bin/env python3
"""
Synapse Sovereign TCG & Game Engine — Longitudinal 9-Master Character, Creative Team & Environmental Dataset Builder.
Constructs a full longitudinal training dataset (`Datasets/longitudinal_9_masters_full_corpus.jsonl`
and `Datasets/longitudinal_5_masters_corpus.jsonl`) spanning the complete career evolutions (1991–2026) of:

Character & Creative Lead Masters:
1. Ryōma Itō (伊藤 龍馬) — Final Fantasy Tactics Advance, FFTA2, FFXII: Revenant Wings, Heroes of Mana
2. Akihiko Yoshida (吉田 明彦) — Tactics Ogre, Final Fantasy Tactics, Vagrant Story, FFTA Judges, FFXII, NieR
3. Hideo Minaba (皆葉 英夫) — Final Fantasy VI/IX, FFTA Art Director, Granblue Fantasy
4. Ryo Hirata (平田 亮) — Super Famicom Wars, Fire Emblem (Thracia 776/Binding Blade/Sacred Stones), Advance Wars 1/2/Dual Strike/Days of Ruin
5. Toru Nakayama (中山 徹) — Speed Power Gunbike, Mega Man Zero 1-4 (Rockman Zero), Mega Man ZX, Dragon Marked for Death, MMZ/ZX Legacy Collection

Environmental, Isometric Diorama & World Architecture Masters:
6. Hiroshi Minagawa & Quest/Ivalice Diorama Team (皆川 裕史) — Ogre Battle, Tactics Ogre, Final Fantasy Tactics, Vagrant Story, FFXII
7. Isamu Kamikokuryo (上国料 勇) — Final Fantasy X, Final Fantasy XII (Ivalice Environments & Airships), Final Fantasy XIII
8. Hiroo Isono & Kouichi Ishii Mana World Team (磯野 宏夫 × 石井 浩一) — Secret of Mana, Trials of Mana, Legend of Mana, Heroes of Mana
9. Makoto Yabe & Inti Creates Environment Team (矢部 誠 / インティ・クリエイツ背景班) — Mega Man Zero 1-4 (Neo Arcadia & Resistance Ruins), Mega Man ZX
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

DATASET_5_PATH = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_5_masters_corpus.jsonl")
DATASET_9_PATH = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_9_masters_full_corpus.jsonl")
SHOWCASE_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Resources/CardArt/StyleShowcase")

LONGITUDINAL_MASTERS_SPEC: List[Dict] = [
    {
        "master_id": "ryoma_ito",
        "artist_name": "Ryōma Itō",
        "kanji": "伊藤 龍馬",
        "domain_category": "character_and_job_class_design",
        "creative_team_lineage": "Square Enix Ivalice Alliance Character Design Team",
        "primary_roles": ["Main Character Designer (Final Fantasy Tactics Advance)", "Character Designer (FFTA2, FFXII: Revenant Wings, Heroes of Mana)"],
        "eras": [
            {
                "era": "1997-2000 (Early Ivalice & Square Era)",
                "works": ["Final Fantasy Tactics (Event/Sub-Character Art)", "Vagrant Story"],
                "morphological_traits": "Apprenticeship under Akihiko Yoshida; warm earth-toned palette transitioning toward cleaner, more kinetic silhouette lines.",
                "shader_vector": {"outline": 1.20, "crosshatch": 0.35, "bloom": 0.30, "saturation": 1.05, "bevel": 0.25},
            },
            {
                "era": "2003 (Final Fantasy Tactics Advance Breakthrough)",
                "works": ["Final Fantasy Tactics Advance"],
                "morphological_traits": "Lighter, more stylized proportions compared to PS1 FFT; tapered gauntlets and oversized boots; vibrant watercolor cel-wash; expressive youthful silhouettes.",
                "shader_vector": {"outline": 1.25, "crosshatch": 0.20, "bloom": 0.45, "saturation": 1.18, "bevel": 0.35},
            },
            {
                "era": "2007-2026 (Mature Ivalice & Modern Tactical Era)",
                "works": ["Final Fantasy XII: Revenant Wings", "Final Fantasy Tactics A2: Grimoire of the Rift", "Heroes of Mana"],
                "morphological_traits": "High-density multi-layered job costumes, dynamic mid-air spell/blade poses, jewel-tone gradients with crisp ink contours.",
                "shader_vector": {"outline": 1.30, "crosshatch": 0.22, "bloom": 0.50, "saturation": 1.22, "bevel": 0.40},
            },
        ],
    },
    {
        "master_id": "akihiko_yoshida",
        "artist_name": "Akihiko Yoshida",
        "kanji": "吉田 明彦",
        "domain_category": "character_supervision_and_baroque_armor_filigree",
        "creative_team_lineage": "Quest -> Square Enix Ivalice -> CyDesignation Creative Lineage",
        "primary_roles": ["Artistic Supervisor & Judge Illustrator (FFTA)", "Main Character Designer (Final Fantasy Tactics, Tactics Ogre, Vagrant Story)"],
        "eras": [
            {
                "era": "1995-1997 (Tactics Ogre & Original PS1 Final Fantasy Tactics)",
                "works": ["Tactics Ogre: Let Us Cling Together", "Final Fantasy Tactics"],
                "morphological_traits": "Iconic nose-less stylized medieval portraiture, dense pen-and-ink crosshatching over aged parchment sepia/ochre tones.",
                "shader_vector": {"outline": 1.45, "crosshatch": 0.90, "bloom": 0.15, "saturation": 0.82, "bevel": 0.40},
            },
            {
                "era": "2000-2003 (Vagrant Story & FFTA Judge Supervision)",
                "works": ["Vagrant Story", "Final Fantasy Tactics Advance (Judge Illustrations & Artistic Supervision)"],
                "morphological_traits": "Monumental baroque Judge armor filigree, winged helmets, heavy metallic chiaroscuro, solemn law-giving authority.",
                "shader_vector": {"outline": 1.40, "crosshatch": 0.85, "bloom": 0.25, "saturation": 0.88, "bevel": 0.55},
            },
            {
                "era": "2006-2026 (FFXII, Bravely Default, NieR & CyDesignation Era)",
                "works": ["Final Fantasy XII", "Bravely Default", "NieR: Automata"],
                "morphological_traits": "Soft graphite pencil grain blended with luminous digital wash, sculptural costume anatomy, timeless museum-grade finish.",
                "shader_vector": {"outline": 1.15, "crosshatch": 0.70, "bloom": 0.40, "saturation": 0.92, "bevel": 0.50},
            },
        ],
    },
    {
        "master_id": "hideo_minaba",
        "artist_name": "Hideo Minaba",
        "kanji": "皆葉 英夫",
        "domain_category": "environmental_and_world_art_direction",
        "creative_team_lineage": "Square Enix Art Direction -> Designation Inc. Studio",
        "primary_roles": ["Art Director (Final Fantasy Tactics Advance, Final Fantasy VI, Final Fantasy IX, Granblue Fantasy)"],
        "eras": [
            {
                "era": "1994-2000 (FFVI & FFIX World Architecture Era)",
                "works": ["Final Fantasy VI", "Final Fantasy IX"],
                "morphological_traits": "Steampunk-meets-fairy-tale architectural silhouettes, warm gaslight and brass textures, rich theatrical stage framing.",
                "shader_vector": {"outline": 1.05, "crosshatch": 0.50, "bloom": 0.65, "saturation": 1.05, "bevel": 0.30},
            },
            {
                "era": "2003 (FFTA Vibrant Storybook Transformation)",
                "works": ["Final Fantasy Tactics Advance"],
                "morphological_traits": "Shifted Ivalice into a vibrant, storybook-like direction; jewel-like isometric map tiles, crystal Jagds, and warm sun-drenched palettes.",
                "shader_vector": {"outline": 1.00, "crosshatch": 0.45, "bloom": 0.75, "saturation": 1.12, "bevel": 0.30},
            },
            {
                "era": "2014-2026 (Designation & Granblue Sky-Realm Era)",
                "works": ["Granblue Fantasy", "Lost Odyssey"],
                "morphological_traits": "Lush painterly cloudscapes, ornate gilded TCG/RPG frame filigree, radiant atmospheric bloom.",
                "shader_vector": {"outline": 1.10, "crosshatch": 0.40, "bloom": 0.85, "saturation": 1.16, "bevel": 0.45},
            },
        ],
    },
    {
        "master_id": "ryo_hirata",
        "artist_name": "Ryo Hirata",
        "kanji": "平田 亮",
        "domain_category": "tactical_unit_co_character_and_battle_map_design",
        "creative_team_lineage": "Intelligent Systems Wars & Fire Emblem Visual Design Team",
        "primary_roles": ["Main Artist & Character/Unit Designer (Advance Wars Series)", "Character/Map/Battle Animation Designer (Fire Emblem GBA & Super Famicom Wars)"],
        "eras": [
            {
                "era": "1998-2004 (Super Famicom Wars & Fire Emblem Thracia 776 / Binding Blade / Sacred Stones)",
                "works": ["Super Famicom Wars", "Fire Emblem: Thracia 776", "Fire Emblem: The Binding Blade", "Fire Emblem: The Sacred Stones"],
                "morphological_traits": "High-readability tactical map & battle animation framing; crisp medieval-fantasy silhouette clarity that translates cleanly from 16-bit/32-bit sprites to full portraits.",
                "shader_vector": {"outline": 1.55, "crosshatch": 0.15, "bloom": 0.25, "saturation": 1.20, "bevel": 0.50},
            },
            {
                "era": "2001-2005 (Advance Wars, Black Hole Rising & Dual Strike Golden Era)",
                "works": ["Advance Wars", "Advance Wars 2: Black Hole Rising", "Advance Wars: Dual Strike"],
                "morphological_traits": "Iconic Commanding Officer (CO) character design; bold graphic linework, punchy saturated faction color-coding (Orange Star, Blue Moon, Green Earth, Yellow Comet, Black Hole), compact stylized battle vehicles.",
                "shader_vector": {"outline": 1.65, "crosshatch": 0.10, "bloom": 0.20, "saturation": 1.28, "bevel": 0.65},
            },
            {
                "era": "2008 (Advance Wars: Days of Ruin Battle Unit Evolution)",
                "works": ["Advance Wars: Days of Ruin"],
                "morphological_traits": "Hardened tactical unit geometry, sharp industrial armor plates, high-contrast directional rim lighting.",
                "shader_vector": {"outline": 1.60, "crosshatch": 0.25, "bloom": 0.20, "saturation": 1.10, "bevel": 0.75},
            },
        ],
    },
    {
        "master_id": "toru_nakayama",
        "artist_name": "Toru Nakayama",
        "kanji": "中山 徹",
        "domain_category": "cyber_fantasy_character_and_promotional_illustration",
        "creative_team_lineage": "Inti Creates Rockman Zero / ZX & Dark Cyber-Fantasy Creative Team",
        "primary_roles": ["Main Artist, Character Designer & Promotional Illustrator (Mega Man Zero / Rockman Zero 1-4)", "Character Designer (Mega Man ZX, Speed Power Gunbike, Dragon Marked for Death)"],
        "eras": [
            {
                "era": "1998 (Speed Power Gunbike Early Mecha-Action Era)",
                "works": ["Speed Power Gunbike"],
                "morphological_traits": "Angular transforming mecha-bike geometry, sharp beveled armor facets, kinetic speed-line composition.",
                "shader_vector": {"outline": 1.50, "crosshatch": 0.15, "bloom": 0.45, "saturation": 1.18, "bevel": 0.85},
            },
            {
                "era": "2002-2005 (Mega Man Zero 1-4 / Rockman Zero GBA Defining Era)",
                "works": ["Mega Man Zero", "Mega Man Zero 2", "Mega Man Zero 3", "Mega Man Zero 4"],
                "morphological_traits": "Slender cyber-Reploid proportions, bold triangular silhouette shapes, sharp beveled metallic armor edges, noticeably larger expressive eyes beneath helm visors, stark black ink shadow blocks contrasted with luminous emerald Z-Saber and Cyber-Elf glow.",
                "shader_vector": {"outline": 1.55, "crosshatch": 0.15, "bloom": 0.60, "saturation": 1.24, "bevel": 0.95},
            },
            {
                "era": "2006-2026 (Mega Man ZX, Dragon Marked for Death & MMZ/ZX Legacy Collection)",
                "works": ["Mega Man ZX", "Dragon Marked for Death", "Mega Man Zero/ZX Legacy Collection"],
                "morphological_traits": "Fusion of dark cyber-fantasy and Biometal armor; rich painterly promotional key-art with razor-sharp specular bevel highlights and dramatic backlighting.",
                "shader_vector": {"outline": 1.45, "crosshatch": 0.20, "bloom": 0.68, "saturation": 1.26, "bevel": 0.98},
            },
        ],
    },
    {
        "master_id": "hiroshi_minagawa",
        "artist_name": "Hiroshi Minagawa & Ivalice Isometric Diorama Team",
        "kanji": "皆川 裕史",
        "domain_category": "isometric_battlefield_diorama_and_terrain_architecture",
        "creative_team_lineage": "Quest Ogre Battle Team -> Square Enix Creative Business Unit III / Ivalice Alliance",
        "primary_roles": ["Art Director & Isometric Battlefield Architect (Tactics Ogre, Final Fantasy Tactics, Vagrant Story)", "Co-Director / Visual Supervisor (FFXII, Tactics Ogre: Reborn)"],
        "eras": [
            {
                "era": "1993-1995 (Ogre Battle & Tactics Ogre Stepped-Elevation Pixel Diorama Era)",
                "works": ["Ogre Battle: The March of the Black Queen", "Tactics Ogre: Let Us Cling Together"],
                "morphological_traits": "Multi-tiered isometric stone and turf battlegrounds, hand-crafted water reflections, unmistakable tile height readability.",
                "shader_vector": {"outline": 1.35, "crosshatch": 0.60, "bloom": 0.30, "saturation": 0.96, "bevel": 0.55},
            },
            {
                "era": "1997-2000 (Final Fantasy Tactics & Vagrant Story 3D Diorama Revolution)",
                "works": ["Final Fantasy Tactics", "Vagrant Story"],
                "morphological_traits": "Rotatable 3D miniature diorama battlefields, warm vertex-lit limestone cathedrals, weathered timber roofs, deep shadow crevices.",
                "shader_vector": {"outline": 1.30, "crosshatch": 0.68, "bloom": 0.38, "saturation": 0.95, "bevel": 0.62},
            },
            {
                "era": "2006-2026 (FFXII, FFXIV Tactical Zones & Tactics Ogre: Reborn)",
                "works": ["Final Fantasy XII", "Tactics Ogre: Reborn"],
                "morphological_traits": "High-resolution painterly texel density preserving classic 3x3/isometric tactical grid clarity and atmospheric depth.",
                "shader_vector": {"outline": 1.22, "crosshatch": 0.58, "bloom": 0.45, "saturation": 1.02, "bevel": 0.60},
            },
        ],
    },
    {
        "master_id": "isamu_kamikokuryo",
        "artist_name": "Isamu Kamikokuryo",
        "kanji": "上国料 勇",
        "domain_category": "monumental_environmental_concept_and_airship_architecture",
        "creative_team_lineage": "Square Enix Ivalice & Sci-Fi Fantasy Environmental Art Direction Team",
        "primary_roles": ["Art Director (Final Fantasy XII, Final Fantasy XIII)", "Environmental Concept Artist (Final Fantasy X)"],
        "eras": [
            {
                "era": "1999-2001 (Final Fantasy X Spira Temple & Aquatic Ruin Era)",
                "works": ["Final Fantasy X"],
                "morphological_traits": "Luminous ocean-side temple ruins, curving organic arches, vibrant pyrefly bioluminescence.",
                "shader_vector": {"outline": 1.05, "crosshatch": 0.30, "bloom": 0.72, "saturation": 1.18, "bevel": 0.65},
            },
            {
                "era": "2003-2007 (Final Fantasy XII Ivalice Skystone & Airship Citadel Era)",
                "works": ["Final Fantasy XII", "Final Fantasy XII: Revenant Wings"],
                "morphological_traits": "Sun-bleached Mediterranean-Ivalice limestone colonnades, ornate brass airship hull ribs, glowing cyan magicite skystones.",
                "shader_vector": {"outline": 1.08, "crosshatch": 0.38, "bloom": 0.70, "saturation": 1.14, "bevel": 0.75},
            },
            {
                "era": "2009-2026 (FFXIII Crystalline Sci-Fi & Fine-Art Canvas Era)",
                "works": ["Final Fantasy XIII", "Final Fantasy XV"],
                "morphological_traits": "Monumental crystalline sci-fi cathedrals blended with impasto oil-painting light diffusion.",
                "shader_vector": {"outline": 1.02, "crosshatch": 0.32, "bloom": 0.78, "saturation": 1.16, "bevel": 0.80},
            },
        ],
    },
    {
        "master_id": "hiroo_isono",
        "artist_name": "Hiroo Isono & Kouichi Ishii (Mana World Environmental Team)",
        "kanji": "磯野 宏夫 × 石井 浩一",
        "domain_category": "botanical_world_tree_and_storybook_biome_illustration",
        "creative_team_lineage": "Seiken Densetsu / Grezzo Storybook Biome & Environmental Lineage",
        "primary_roles": ["Principal World & Forest Sanctuary Illustrator (Secret of Mana, Trials of Mana, Heroes of Mana)", "Series Creator & Art Director (Kouichi Ishii)"],
        "eras": [
            {
                "era": "1991-1995 (Secret of Mana & Trials of Mana Botanical Masterwork Era)",
                "works": ["Secret of Mana (Seiken Densetsu 2)", "Trials of Mana (Seiken Densetsu 3)"],
                "morphological_traits": "Colossal ancient Mana Tree roots, dense multi-layered emerald and teal foliage canopies, serene golden sunbeams piercing misty forest sanctuaries.",
                "shader_vector": {"outline": 1.10, "crosshatch": 0.28, "bloom": 0.82, "saturation": 1.26, "bevel": 0.38},
            },
            {
                "era": "1999-2007 (Legend of Mana & Heroes of Mana Tactical Biome Era)",
                "works": ["Legend of Mana", "Heroes of Mana"],
                "morphological_traits": "Storybook watercolor tactical maps where living flora, coral reefs, and ancient ruins form natural elevation battlefields.",
                "shader_vector": {"outline": 1.12, "crosshatch": 0.32, "bloom": 0.78, "saturation": 1.24, "bevel": 0.42},
            },
        ],
    },
    {
        "master_id": "inti_creates_env",
        "artist_name": "Makoto Yabe & Inti Creates Environment Team",
        "kanji": "矢部 誠 / インティ・クリエイツ背景班",
        "domain_category": "cyber_cathedral_and_post_apocalyptic_reploid_ruin_environments",
        "creative_team_lineage": "Inti Creates Mega Man Zero / ZX & Gunvolt Stage Art Team",
        "primary_roles": ["Background & Stage Environment Design Team (Mega Man Zero 1-4, Mega Man ZX, Azure Striker Gunvolt)"],
        "eras": [
            {
                "era": "2002-2005 (Mega Man Zero 1-4 Neo Arcadia & Resistance Ruin Era)",
                "works": ["Mega Man Zero", "Mega Man Zero 2", "Mega Man Zero 3", "Mega Man Zero 4"],
                "morphological_traits": "Sleek Neo-Arcadia sacred cyber-cathedrals juxtaposed against battle-scarred Reploid wastelands, glowing cyan Cyber-Elf conduits, stark black ink shadow geometry.",
                "shader_vector": {"outline": 1.50, "crosshatch": 0.15, "bloom": 0.65, "saturation": 1.22, "bevel": 0.92},
            },
            {
                "era": "2006-2026 (Mega Man ZX, Gunvolt & Dragon Marked for Death Stage Environments)",
                "works": ["Mega Man ZX", "Mega Man ZX Advent", "Azure Striker Gunvolt", "Dragon Marked for Death"],
                "morphological_traits": "Multi-plane high-contrast parallax industrial skylines, holographic circuit glyphs, razor-sharp metallic bevel lighting.",
                "shader_vector": {"outline": 1.48, "crosshatch": 0.18, "bloom": 0.70, "saturation": 1.25, "bevel": 0.95},
            },
        ],
    },
    {
        "master_id": "yoji_shinkawa",
        "artist_name": "Yoji Shinkawa",
        "kanji": "新川 洋司",
        "domain_category": "tactical_stealth_mecha_and_calligraphic_sumi_ink_illustration",
        "creative_team_lineage": "Konami KCEJ -> Kojima Productions Mechanical & Character Design Team",
        "primary_roles": ["Lead Character & Mecha Designer (Metal Gear Solid 1-5, Zone of the Enders)", "Art Director (Death Stranding)"],
        "eras": [
            {
                "era": "1998-2004 (Metal Gear Solid 1-3 & Zone of the Enders Jehuty/Anubis Era)",
                "works": ["Metal Gear Solid", "Metal Gear Solid 2: Sons of Liberty", "Zone of the Enders", "Metal Gear Solid 3: Snake Eater"],
                "morphological_traits": "Expressive Pentel brush-pen sumi-e ink strokes, stark negative space, dry-brush splatter, razor-sharp Orbital Frame and tactical stealth silhouettes.",
                "shader_vector": {"outline": 1.75, "crosshatch": 0.78, "bloom": 0.30, "saturation": 0.85, "bevel": 0.88},
            },
            {
                "era": "2008-2026 (MGS4/V & Death Stranding Biomechanical Tactical Era)",
                "works": ["Metal Gear Solid 4", "Metal Gear Solid V", "Death Stranding"],
                "morphological_traits": "Painterly acrylic-and-ink hybrid tactical hardware, carbon-fiber mecha articulation, olive-drab and cyan energy accents.",
                "shader_vector": {"outline": 1.68, "crosshatch": 0.72, "bloom": 0.38, "saturation": 0.90, "bevel": 0.90},
            },
        ],
    },
    {
        "master_id": "kazuma_kaneko",
        "artist_name": "Kazuma Kaneko",
        "kanji": "金子 一馬",
        "domain_category": "cyber_occult_mythology_and_high_contrast_mannequin_shading",
        "creative_team_lineage": "Atlus Megami Tensei R&D1 Creative & Demonology Design Team",
        "primary_roles": ["Primary Character & Demon Designer (Shin Megami Tensei I-III, Persona 1-2, Devil Summoner)", "Guest Mecha/Orbital Frame Designer (Zone of the Enders: The 2nd Runner)"],
        "eras": [
            {
                "era": "1992-1999 (SMT I/II, Devil Summoner & Persona 1/2 Cyber-Occult Era)",
                "works": ["Shin Megami Tensei", "Shin Megami Tensei II", "Shin Megami Tensei: Devil Summoner", "Persona 2: Innocent Sin / Eternal Punishment"],
                "morphological_traits": "Porcelain-smooth mannequin-like cyber-occult anatomy, stark black upper-lip and eye shading, high-fashion cyberpunk silhouettes.",
                "shader_vector": {"outline": 1.50, "crosshatch": 0.20, "bloom": 0.45, "saturation": 1.08, "bevel": 0.90},
            },
            {
                "era": "2001-2008 (SMT III: Nocturne, Digital Devil Saga & ZOE 2nd Runner Era)",
                "works": ["Shin Megami Tensei III: Nocturne", "Digital Devil Saga", "Zone of the Enders: The 2nd Runner"],
                "morphological_traits": "Luminous geometric esoteric sigils, clinical high-contrast cel-gradient lighting, surreal biomechanical angel/demon forms.",
                "shader_vector": {"outline": 1.48, "crosshatch": 0.18, "bloom": 0.55, "saturation": 1.12, "bevel": 0.92},
            },
        ],
    },
    {
        "master_id": "terada_suzuki",
        "artist_name": "Katsuya Terada & Yasushi Suzuki",
        "kanji": "寺田 克也 × 鈴木 康士",
        "domain_category": "kinetic_polarity_sumi_chiaroscuro_and_biomechanical_linework",
        "creative_team_lineage": "Treasure Co. (Ikaruga / Sin & Punishment) & Production I.G Illustrative Lineage",
        "primary_roles": ["Lead Concept & Promotional Illustrators (Ikaruga, Sin & Punishment, Blood: The Last Vampire, Busin 0: Wizardry Alternative)"],
        "eras": [
            {
                "era": "2000-2004 (Sin & Punishment, Ikaruga & Blood: The Last Vampire Era)",
                "works": ["Sin and Punishment", "Ikaruga", "Blood: The Last Vampire", "Busin 0: Wizardry Alternative"],
                "morphological_traits": "Dual-polarity black/white energy chiaroscuro, dense organic-biomechanical ink crosshatching, explosive kinetic brush strokes.",
                "shader_vector": {"outline": 1.60, "crosshatch": 0.82, "bloom": 0.58, "saturation": 1.12, "bevel": 0.84},
            },
            {
                "era": "2009-2026 (Sin & Punishment: Star Successor & Modern Dark Sci-Fi Key Art)",
                "works": ["Sin & Punishment: Star Successor"],
                "morphological_traits": "High-contrast digital sumi-wash fused with intricate mechanical feather and armor detailing.",
                "shader_vector": {"outline": 1.56, "crosshatch": 0.76, "bloom": 0.62, "saturation": 1.15, "bevel": 0.86},
            },
        ],
    },
]


def build_longitudinal_dataset(render_showcases: bool = True) -> Dict:
    from generate_project_cf_art import (
        ENVIRONMENTAL_BATTLEFIELD_PROMPTS,
        ILLUSTRATOR_STYLE_LIBRARY,
        PROJECT_CF_ART_PROMPTS,
        generate_card_art_on_rtx4080,
    )

    DATASET_9_PATH.parent.mkdir(parents=True, exist_ok=True)
    records: List[Dict] = []

    for master in LONGITUDINAL_MASTERS_SPEC:
        # 1. Career Era Evolution Records
        for era_obj in master["eras"]:
            records.append({
                "record_type": "longitudinal_era_specification",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "kanji": master["kanji"],
                "domain_category": master["domain_category"],
                "creative_team_lineage": master["creative_team_lineage"],
                "era": era_obj["era"],
                "works": era_obj["works"],
                "morphological_traits": era_obj["morphological_traits"],
                "shader_vector": era_obj["shader_vector"],
                "instruction": (
                    f"Configure the proprietary Synapse Engine illustrator, environment & shader pipeline for "
                    f"{master['artist_name']} ({master['creative_team_lineage']} — {era_obj['era']})."
                ),
                "response": (
                    f"Artist/Team: {master['artist_name']} ({master['kanji']}) | Lineage: {master['creative_team_lineage']} | "
                    f"Domain: {master['domain_category']} | Era: {era_obj['era']} | "
                    f"Works: {', '.join(era_obj['works'])} | Morphology: {era_obj['morphological_traits']} | "
                    f"Shader Grading: {json.dumps(era_obj['shader_vector'])}"
                ),
            })

        latest_era = master["eras"][-1]
        style_info = ILLUSTRATOR_STYLE_LIBRARY.get(master["master_id"], ILLUSTRATOR_STYLE_LIBRARY["tactical_synthesis"])

        # 2. Card Character & Concept Conditioning Records
        for card_id, card_desc in PROJECT_CF_ART_PROMPTS.items():
            records.append({
                "record_type": "card_illustrator_conditioning",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "domain_category": master["domain_category"],
                "card_id": card_id,
                "comfyui_positive_prompt": style_info["prompt_prefix"] + card_desc,
                "comfyui_negative_prompt": style_info["negative"],
                "shader_vector": latest_era["shader_vector"],
                "instruction": f"Generate the ComfyUI RTX 4080 conditioning prompt and proprietary engine shader vector for card `{card_id}` in the style of {master['artist_name']}.",
                "response": json.dumps({
                    "card_id": card_id,
                    "artist": master["artist_name"],
                    "creative_team": master["creative_team_lineage"],
                    "positive_prompt": style_info["prompt_prefix"] + card_desc,
                    "negative_prompt": style_info["negative"],
                    "shader_vector": latest_era["shader_vector"],
                }),
            })

        # 3. Environmental Battlefield & 3x3 Isometric Diorama Conditioning Records
        for env_id, env_desc in ENVIRONMENTAL_BATTLEFIELD_PROMPTS.items():
            records.append({
                "record_type": "environmental_battlefield_conditioning",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "domain_category": master["domain_category"],
                "environment_id": env_id,
                "comfyui_positive_prompt": style_info["prompt_prefix"] + env_desc,
                "comfyui_negative_prompt": style_info["negative"],
                "shader_vector": latest_era["shader_vector"],
                "trellis2_ovoxel_pbr": {
                    "roughness_bias": round(1.0 - latest_era["shader_vector"]["bevel"] * 0.45, 2),
                    "metallic_bias": round(latest_era["shader_vector"]["bevel"] * 0.65, 2),
                    "emissive_bloom": latest_era["shader_vector"]["bloom"],
                },
                "instruction": f"Synthesize the environmental battlefield art prompt, shader grading, and TRELLIS 2.0 3D O-Voxel PBR material profile for arena `{env_id}` in the style of {master['artist_name']}.",
                "response": json.dumps({
                    "environment_id": env_id,
                    "artist_or_team": master["artist_name"],
                    "positive_prompt": style_info["prompt_prefix"] + env_desc,
                    "negative_prompt": style_info["negative"],
                    "shader_vector": latest_era["shader_vector"],
                    "trellis2_ovoxel_pbr": {
                        "roughness_bias": round(1.0 - latest_era["shader_vector"]["bevel"] * 0.45, 2),
                        "metallic_bias": round(latest_era["shader_vector"]["bevel"] * 0.65, 2),
                        "emissive_bloom": latest_era["shader_vector"]["bloom"],
                    },
                }),
            })

    # 4. Into the Breach + STACCS 3D Isometric Cube-Card Stacking Records (15 records)
    for i in range(1, 16):
        records.append({
            "record_id": f"itb_staccs_{i:02d}",
            "record_type": "itb_staccs_isometric_stack_conditioning",
            "master_id": "subset_games_staccs",
            "artist_name": "Justin Ma & Matthew Davis (Subset Games) x STACCS 3D Studio",
            "domain_category": "deterministic_telegraph_and_3d_cube_stack",
            "instruction": f"Specify Into the Breach + STACCS 3D isometric cube-card stacking & deterministic telegraph rule #{i}.",
            "response": json.dumps({
                "record_id": f"itb_staccs_{i:02d}",
                "mechanic": "3-Rhombus Isometric Cube Stacking (Z=1..5) + Deterministic Push/Bump Telegraph + Power Grid & Time Breach",
            }),
        })

    # 5. Metal Gear Acid 1 & 2 (Shinta Nojiri, Tsubasa Masao, Naochika Morishita, Ikuya Nakamura, Yoji Shinkawa) Records (20 records)
    for i in range(1, 21):
        records.append({
            "record_id": f"mga_{i:02d}",
            "record_type": "metal_gear_acid_cost_and_solid_eye_conditioning",
            "master_id": "nojiri_masao_morishita_shinkawa_mga",
            "artist_name": "Shinta Nojiri, Tsubasa Masao, Naochika Morishita, Ikuya Nakamura & Yoji Shinkawa",
            "domain_category": "mga_cost_stealth_solid_eye_pop_cel",
            "instruction": f"Specify Metal Gear Acid 1 & 2 COST turn-delay clock, 4-mode Effect/Move/Equip/Link card economy, and Solid Eye Halftone Pop-Cel shader rule #{i}.",
            "response": json.dumps({
                "record_id": f"mga_{i:02d}",
                "creative_director": "Shinta Nojiri",
                "illustrators": ["Tsubasa Masao", "Naochika Morishita", "Ikuya Nakamura", "Yoji Shinkawa"],
                "shader_profile": "SolidEyeCelPopShaderProfile (2.5px comic ink, 42Hz Ben-Day halftone, -0.18m stereoscopic Z pop-out)",
            }),
        })

    # 6. MiroFish + AWS Strands Multi-Agent NPC & Studio Illustrator Simulation Feedback + Model Soup Records (10 records)
    for i in range(1, 11):
        records.append({
            "record_id": f"miro_strands_{i:02d}",
            "record_type": "mirofish_strands_multi_agent_simulation_soup",
            "master_id": "mirofish_strands_soup_director",
            "artist_name": "Synapse Studio Swarm (MiroFish + AWS Strands Agents + Model Soup)",
            "domain_category": "multi_agent_simulation_and_model_soup",
            "instruction": f"Specify MiroFish 12-NPC Metagame Market + 7-Master Studio Illustrator Strands Workflow + Uniform/Greedy/Task-Arithmetic/TIES Model Soup rule #{i}.",
            "response": json.dumps({
                "record_id": f"miro_strands_{i:02d}",
                "npc_archetypes": 12,
                "studio_illustrators": 7,
                "soup_modes": ["uniform", "greedy", "task_arithmetic", "ties"],
            }),
        })

    # 7. Anime Training Baselines & Proprietary House-Style Distillation (`Synapse-Aether-Cel v1.0`) Records (15 records)
    anime_distill_specs = [
        ("anime_distill_01", "Animagine XL 3.1 Baseline Backbone", "animagineXLV31_v31.safetensors", "SDXL Epsilon-Pred 1024x1024 primary anime/game concept backbone on Node 30 RTX 4080"),
        ("anime_distill_02", "Illustrious-XL High-Density Lineart Backbone", "illustriousXL_v10.safetensors", "Danbooru2023+ high-frequency pen crosshatching, mecha bevel, and drapery separation teacher"),
        ("anime_distill_03", "NoobAI-XL V-Prediction Dynamic Range Backbone", "noobaiXL_vpred10.safetensors", "Zero-Terminal-SNR v-prediction teacher for deep chiaroscuro ink shadows and radiant bloom"),
        ("anime_distill_04", "Kohaku-XL Delta Structural Teacher", "kohakuXL_delta.safetensors", "Crisp graphic cel-boundary and halftone dot fidelity teacher"),
        ("anime_distill_05", "FLUX.1-dev FP8 / Sana-1.6B Rectified-Flow Teacher", "flux1-dev-fp8.safetensors", "12B MMDiT / Linear DiT multi-subject spatial layout and isometric 3x3 diorama teacher"),
        ("anime_distill_06", "UNet IN00-IN08 Structural Composition Block Soup", "unet_in00_08_dora_lokr", "Block-weighted DoRA/LoKr merge routing Minagawa isometric masonry + Nojiri/Morishita MGA perspective"),
        ("anime_distill_07", "UNet MID00 Bottleneck Anatomy & Silhouette Block Soup", "unet_mid00_dora_lokr", "Bottleneck merge routing Ryoma Ito hero proportions + Toru Nakayama cyber-Reploid bevels + Shinkawa mecha posture"),
        ("anime_distill_08", "UNet OUT00-OUT05 Fine-Grain Brush & Shader Block Soup", "unet_out00_05_dora_lokr", "Output block merge routing Yoshida crosshatching + Hirata Advance Wars cel + Morishita Solid Eye Ben-Day halftone + Kaneko/Suzuki sumi"),
        ("anime_distill_09", "DMD2 Distribution Matching Distillation (22-Step -> 4-Step)", "dmd2_4step_student", "Minimizes KL divergence between 22-step CFG=6.8 Teacher Soup and 4-step CFG=1.0 Student (5.5x speedup on RTX 4080)"),
        ("anime_distill_10", "Phased Consistency Model (PCM)ODE Trajectory Distillation", "pcm_4step_trajectory", "Enforces phase-consistent latent trajectory across 4 sub-intervals [1000->750->500->250->0] withoutwashed-out cel edges"),
        ("anime_distill_11", "SDXL-Lightning Adversarial + Progressive Distillation", "sdxl_lightning_4step_lora", "Combines progressive timestep halving with a relational UNet discriminator for razor-sharp 1-second telegraph icons"),
        ("anime_distill_12", "Hinton Cross-Modal Knowledge Distillation to Unity Shaders", "hinton_kd_unity_shader_student", "Distills 22-step diffusion teacher feature statistics into 5 deterministic real-time Unity URP shader uniforms"),
        ("anime_distill_13", "Proprietary Style Non-Dominance & Uniqueness Gate", "proprietary_uniqueness_audit", "Enforces max single-artist weight <= 0.38 and cosine similarity <= 0.72 so Synapse-Aether-Cel v1.0 is 100% original"),
        ("anime_distill_14", "STACCS 3-Rhombus Isometric Cube Face Style Distillation", "staccs_cube_face_distill", "Projects distilled Synapse-Aether-Cel v1.0 textures across Top Diamond Crown, Left Armor Flank, and Right Support Flank"),
        ("anime_distill_15", "Closed-Loop 24/7 Creative Director Distillation Retraining", "creative_director_distill_loop", "Automatically updates block-weighted DoRA/LoKr soup weights from MiroFish + Strands 7-Illustrator Swarm telemetry"),
    ]
    for rec_id, title, target_ckpt, desc in anime_distill_specs:
        records.append({
            "record_id": rec_id,
            "record_type": "anime_baseline_proprietary_style_distillation",
            "master_id": "synapse_aether_cel_distiller",
            "artist_name": "Synapse-Aether-Cel v1.0 Proprietary Style Distillation Pipeline",
            "domain_category": "anime_baseline_and_4step_style_distillation",
            "target_checkpoint_or_module": target_ckpt,
            "title": title,
            "instruction": f"Configure `{rec_id}` ({title}) for the Synapse-Aether-Cel v1.0 proprietary anime-to-tactical distillation pipeline.",
            "response": json.dumps({
                "record_id": rec_id,
                "title": title,
                "module": target_ckpt,
                "specification": desc,
                "proprietary_style": "Synapse-Aether-Cel v1.0",
            }),
        })

    for idx, r in enumerate(records, start=1):
        if "record_id" not in r:
            r["record_id"] = f"rec_{idx:03d}"

    with DATASET_9_PATH.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Also keep DATASET_5_PATH synced with the full corpus so existing scripts read all 251 records seamlessly
    with DATASET_5_PATH.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    rendered_showcases = {}
    if render_showcases:
        showcase_jobs = [
            ("cf_09_cyber_ninja", "toru_nakayama", SHOWCASE_DIR / "style_toru_nakayama_mmz.png", 768, 1024),
            ("env_01_ivalice_jagd_citadel", "hiroshi_minagawa", SHOWCASE_DIR / "env_hiroshi_minagawa_ivalice_diorama.png", 1024, 768),
            ("env_03_neo_arcadia_cyber_sanctum", "inti_creates_env", SHOWCASE_DIR / "env_inti_creates_neo_arcadia.png", 1024, 768),
            ("env_04_mana_world_tree_shrine", "hiroo_isono", SHOWCASE_DIR / "env_hiroo_isono_mana_sanctuary.png", 1024, 768),
            ("env_05_skystone_airship_dock", "isamu_kamikokuryo", SHOWCASE_DIR / "env_isamu_kamikokuryo_skystone.png", 1024, 768),
            ("cf_02_mech_knight", "yoji_shinkawa", SHOWCASE_DIR / "style_yoji_shinkawa_mecha.png", 768, 1024),
            ("cf_04_shadow_assassin", "kazuma_kaneko", SHOWCASE_DIR / "style_kazuma_kaneko_occult_cyber.png", 768, 1024),
            ("cf_08_phoenix_guardian", "terada_suzuki", SHOWCASE_DIR / "style_terada_suzuki_ikaruga.png", 768, 1024),
        ]
        for cid, skey, out_p, w, h in showcase_jobs:
            try:
                rendered_showcases[skey] = generate_card_art_on_rtx4080(
                    cid, style_key=skey, out_path=out_p, width=w, height=h, steps=15
                )
            except Exception as exc:
                rendered_showcases[skey] = {"error": str(exc)}

    return {
        "dataset_9_path": str(DATASET_9_PATH),
        "dataset_5_path": str(DATASET_5_PATH),
        "total_longitudinal_records": len(records),
        "era_records": sum(1 for r in records if r["record_type"] == "longitudinal_era_specification"),
        "character_card_records": sum(1 for r in records if r["record_type"] == "card_illustrator_conditioning"),
        "environmental_battlefield_records": sum(1 for r in records if r["record_type"] == "environmental_battlefield_conditioning"),
        "masters_included": [m["artist_name"] for m in LONGITUDINAL_MASTERS_SPEC],
        "rendered_showcases": rendered_showcases,
    }


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    res = build_longitudinal_dataset(render_showcases=True)
    print(json.dumps(res, indent=2, ensure_ascii=False))
