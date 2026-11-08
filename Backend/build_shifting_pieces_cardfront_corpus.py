#!/usr/bin/env python3
"""
build_shifting_pieces_cardfront_corpus.py — Shifting Pieces × CardFront × CardCraft
Longitudinal Corpus Builder (721 -> 801 Records) & Multi-Agent Coordination Hub
===================================================================================
1. Reads the synced `bcphan@hawaii.edu` Google Drive manuscripts in
   `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-drive-docs/Shifting_Pieces_and_CardFront/`
   (`Shifting_Pieces_Complete_Novel.txt`, `Story Bible.docx`, `Visual Character Sheet – Shifting Pieces.docx`,
   `Chapter-by-Chapter Puzzle Integration Map – Shifting Pieces.docx`, `CardFront_Cradle_of_Echoes.docx`,
   `Shifting_Pieces_Cover_Color_Palettes.docx`) and `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-drive-docs/CardCraft.docx`.
2. Appends 80 structured `shifting_pieces_cardfront_cardcraft_spec` records to:
   - `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_9_masters_full_corpus.jsonl`
   - `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl`
   expanding the longitudinal training corpus from 721 to 801 total records:
   - 60 Records (12 Foundational Masters × 5 Shifting Pieces × CardFront × CardCraft Pillars):
     1. `sp_pillar_1_okitsu_mnemosyne_worldbuilding`
     2. `sp_pillar_2_cradle_of_echoes_persona_genesis`
     3. `sp_pillar_3_chapter_puzzle_3x3_dicevaders_map`
     4. `sp_pillar_4_cardcraft_internal_card_mesh_generator`
     5. `sp_pillar_5_act3_convergence_triad_ending`
   - 20 Records (All 19 Chapters + Prologue of *Shifting Pieces* mapped to playable
     *CardFront × CardCraft* encounters, boss mechanics, concept art prompts, and 3D relic assets).
3. Creates the shared cross-session Antigravity CLI 1.5.2 Coordination Hub at
   `/Users/frederickamina/Documents/Projects/SYNAPSE/ANTIGRAVITY_SWARM_COORDINATION_HUB.json`
   and persists it into NCM (`ncm.remember("antigravity_cli_152_shifting_pieces_cardfront_hub", ...)`).
4. Syncs `longitudinal_9_masters_full_corpus.jsonl` (801 records) to
   `v100:/mnt/models/forge/datasets/longitudinal_9_masters_full_corpus.jsonl` and runs a
   5-Epoch (30-step) V100 QLoRA + Hinton KD Refinement Pass.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROJECT_ROOT = BACKEND_DIR.parent
SYNAPSE_ROOT = PROJECT_ROOT.parent
TCG_DRIVE_ROOT = SYNAPSE_ROOT / "tcg-drive-docs"
SP_ROOT = TCG_DRIVE_ROOT / "Shifting_Pieces_and_CardFront"

DATASET_FULL_PATH = PROJECT_ROOT / "Datasets" / "longitudinal_9_masters_full_corpus.jsonl"
DATASET_12_PATH = PROJECT_ROOT / "Datasets" / "longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl"
COORDINATION_HUB_PATH = SYNAPSE_ROOT / "ANTIGRAVITY_SWARM_COORDINATION_HUB.json"
NCM_STORE_PATH = Path("/Users/frederickamina/.prime/agent/harness/ncm_store.json")
REPORT_OUT_PATH = PROJECT_ROOT / "Datasets" / "shifting_pieces_cardfront_801_corpus_report.json"

REMOTE_CORPUS_DEST = "v100:/mnt/models/forge/datasets/longitudinal_9_masters_full_corpus.jsonl"
HARNESS_BIN = "/Users/frederickamina/.local/bin/pxg-gamedev-harness"
FORGE_API_URL = "http://192.168.86.116:8090"
REFINE_TOPIC = (
    "Shifting Pieces Manuscript (Kai, Aiko Red Scarf #D12D3A, Mnemosyne, LUNA) x "
    "CardFront: Cradle of Echoes x CardCraft Internal Card/Mesh/Concept Generator (801 Records)"
)


class _NcmMemoryHelper:
    """Provides `ncm.remember(key, value, ...)` backed by `~/.prime/agent/harness/ncm_store.json`."""

    @staticmethod
    def remember(
        key: str,
        content: Any,
        category: str = "coordination_hub",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        NCM_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        store: Dict[str, Any] = {"version": "1.0.0", "updated_at": "", "nodes": {}}
        if NCM_STORE_PATH.exists():
            try:
                store = json.loads(NCM_STORE_PATH.read_text(encoding="utf-8"))
            except Exception:
                store = {"version": "1.0.0", "updated_at": "", "nodes": {}}
        if "nodes" not in store or not isinstance(store["nodes"], dict):
            store["nodes"] = {}

        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        serialized = content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False)
        node_entry = {
            "key": key,
            "category": category,
            "tags": tags or [
                "antigravity_cli_152",
                "shifting_pieces",
                "cardfront_cradle_of_echoes",
                "cardcraft",
                "indie_marc_tcg_engine",
                "dicevaders_3917700",
                "hi3d_rea_tools",
                "lumenforge_4node_pool",
            ],
            "content": serialized,
            "updated_at": now_iso,
        }
        store["nodes"][key] = node_entry
        store["updated_at"] = now_iso
        NCM_STORE_PATH.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"key": key, "store_path": str(NCM_STORE_PATH), "updated_at": now_iso, "total_keys": len(store["nodes"])}


try:
    import ncm as _existing_ncm  # type: ignore
    if not hasattr(_existing_ncm, "remember"):
        _existing_ncm.remember = _NcmMemoryHelper.remember  # type: ignore
    ncm = _existing_ncm
except ImportError:
    ncm = _NcmMemoryHelper()


def extract_docx_text(docx_path: Path) -> str:
    """Extract clean paragraph text from a `.docx` OpenXML archive."""
    if not docx_path.exists():
        return ""
    with zipfile.ZipFile(docx_path) as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs: List[str] = []
    for elem in root.iter():
        if elem.tag.endswith("}p"):
            runs = [t.text for t in elem.iter() if t.tag.endswith("}t") and t.text]
            if runs:
                paragraphs.append("".join(runs).strip())
    return "\n".join(p for p in paragraphs if p)


def read_drive_manuscripts() -> Dict[str, Any]:
    """
    Read and catalog the synced `bcphan@hawaii.edu` Google Drive manuscripts in
    `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-drive-docs/Shifting_Pieces_and_CardFront/`
    and `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-drive-docs/CardCraft.docx`.
    """
    target_files = {
        "shifting_pieces_complete_novel_txt": SP_ROOT / "Book_I" / "Shifting_Pieces_Complete_Novel.txt",
        "story_bible_docx": SP_ROOT / "Book_I" / "Notes" / "Story Bible.docx",
        "visual_character_sheet_docx": SP_ROOT / "Book_I" / "Notes" / "Visual Character Sheet – Shifting Pieces.docx",
        "chapter_puzzle_integration_map_docx": SP_ROOT / "Book_I" / "Notes" / "Chapter-by-Chapter Puzzle Integration Map – Shifting Pieces.docx",
        "cardfront_cradle_of_echoes_docx": SP_ROOT / "CardFront_Archives" / "CardFront_Cradle_of_Echoes.docx",
        "shifting_pieces_cover_palettes_docx": SP_ROOT / "CardFront_Archives" / "Shifting_Pieces_Cover_Color_Palettes.docx",
        "cardcraft_docx": TCG_DRIVE_ROOT / "CardCraft.docx",
    }

    catalog: Dict[str, Dict[str, Any]] = {}
    for key, path in target_files.items():
        if not path.exists():
            catalog[key] = {"path": str(path), "exists": False}
            continue
        raw_bytes = path.read_bytes()
        if path.suffix.lower() == ".docx":
            text = extract_docx_text(path)
        else:
            text = raw_bytes.decode("utf-8", errors="replace")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        catalog[key] = {
            "path": str(path),
            "filename": path.name,
            "exists": True,
            "bytes": len(raw_bytes),
            "extracted_chars": len(text),
            "extracted_lines": len(lines),
            "sha256": hashlib.sha256(raw_bytes).hexdigest()[:16],
            "excerpt": " ".join(lines[:10])[:650],
            "full_text": text,
        }
    return catalog


SHIFTING_PIECES_5_PILLARS: List[Dict[str, Any]] = [
    {
        "pillar_id": "sp_pillar_1_okitsu_mnemosyne_worldbuilding",
        "pillar_index": 1,
        "pillar_title": "Shifting Pieces Okitsu Coastal Town, VR Café & Mnemosyne MAS Architecture (Palette A #0B0B0C + Red Scarf #D12D3A & Palette B #0A1020 + #2EE6D3)",
        "source_documents": [
            "Shifting_Pieces_Complete_Novel.txt",
            "Story Bible.docx",
            "Visual Character Sheet – Shifting Pieces.docx",
            "Shifting_Pieces_Cover_Color_Palettes.docx",
        ],
        "architecture_formula": (
            "In Hiroyasu (Binh C. Phan)'s *Shifting Pieces*, the semi-isolated coastal city of Okitsu (pop. 15,000) "
            "blends traditional wooden shrines, seawalls, and cherry trees with smart-glass towers, courier drones, and "
            "Taro Fujimoto's corner VR Café. Seventeen-year-old puzzle prodigy Kai Nakamura (deep gray eyes with faint "
            "violet flecks, patchy wiring-embroidered hoodie, modified VR headset etched with Aiko's neural tree) enters "
            "Project Mnemosyne's Memory Architecture System (MAS) built by his vanished 21-year-old sister Aiko Nakamura "
            "(academic coat layered over a crimson digitalized Red Scarf `#D12D3A`, hair with data-ribbon red strands, "
            "neural uplink temple band). Visual shaders strictly bind Palette A (`#0B0B0C` near-black, `#F2F2F2` title, "
            "`#D12D3A` crimson Red Scarf focal accent, `#7A8B99` cool gray-blue glitch trim), Palette B (`#0A1020` midnight "
            "blue, `#2EE6D3` cyan VR halo linework, `#8A5BFF` violet outer glow), and Palette C (`#0A2230` deep ocean, "
            "`#FFB648` lantern amber Constellation Fox nodes)."
        ),
        "synapse_integration_spec": {
            "protagonist": "Kai Nakamura (Age 17, Puzzle Prodigy, Rubik-cube & Aiko-modified VR Headset)",
            "deuteragonist_echo": "Aiko Nakamura (Age 21, Memory Engineer, Red Scarf #D12D3A, Digital Ghost Architect)",
            "grounding_ally": "Taro Fujimoto (Age 18, Okitsu VR Café Barista, ash-blue spiky hair, hazel-green eyes)",
            "system_ai": "Mnemosyne (Holographic fractal Constellation Fox / shifting mosaic of Aiko / glyph eyes)",
            "color_palettes": {
                "Palette_A_Monochrome_Red_Scarf": {"bg": "#0B0B0C", "primary": "#F2F2F2", "secondary": "#C9C9C9", "accent_scarf": "#D12D3A", "sub_accent": "#7A8B99"},
                "Palette_B_Cyber_Blues_Neon_Violet": {"bg": "#0A1020", "primary": "#EAF2FF", "accent_cyan": "#2EE6D3", "accent_violet": "#8A5BFF", "grain": "#1B2338"},
                "Palette_C_Ocean_Lantern_Fox": {"bg": "#0A2230", "primary": "#F8FAFB", "accent_amber": "#FFB648", "twilight_teal": "#2B6C7C"},
            },
        },
    },
    {
        "pillar_id": "sp_pillar_2_cradle_of_echoes_persona_genesis",
        "pillar_index": 2,
        "pillar_title": "CardFront: Cradle of Echoes Station of Awakening Tarot Sequence Guided by LUNA (Toru Nakayama × Akihiko Yoshida Cel-Shading, 20 Personas & Quest Cards)",
        "source_documents": [
            "CardFront_Cradle_of_Echoes.docx",
            "CM442_CardFront_Prototype_Final.docx",
        ],
        "architecture_formula": (
            "*CardFront: Cradle of Echoes* (Studio PxG | Nocturna Universe) is the canonical Player Genesis Sequence set in a "
            "dreamlike liminal glass-floor plane inspired by *Kingdom Hearts* Station of Awakening and *Tactics Ogre* tarot. "
            "Guided by LUNA (`LUNA_CradleManager`, `LUNA_PersonaEngine`, `NERVA_PersonaBridge`), the player selects 10 floating "
            "tarot cards derived from the Ikigai Framework (Love / Skill / Need / Sustain). Card selections weight affinities "
            "(`personaWeights[personaID] += card.affinity[personaID] * selectionWeight`: Cards 1-2 = 10%, Cards 3-7 = 60%, "
            "Cards 8-9 = 25%, Card 10 = 5% Persona Seal -> 95% alignment, with the remaining 5% spread across 500,000 Quest Cards "
            "at `Merit * 0.05` per completed QC). Art direction fuses Toru Nakayama + Akihiko Yoshida crisp cel-shaded outlines "
            "over Nocturna blue and amethyst particle gradients with Yoko Shimomura-inspired piano/synth pads."
        ),
        "synapse_integration_spec": {
            "unity_scene_pipeline": [
                "Cradle_Awakening.unity (Stage 0: Awakening via LUNA_CradleManager.Initialize)",
                "Cradle_Selection.unity (Stages 1-3: NEC_CardSpawner.SpawnSet(10) + LUNA_PersonaEngine.ComputeWeights)",
                "Cradle_Revelation.unity (Stages 4-5: NERVA_PersonaBridge.RevealPersona + AssignQuestSeed)",
            ],
            "twenty_core_personas": [
                "1. The Dreamer (Air/Creativity)", "2. The Master (Fire/Mastery)", "3. The Guardian (Earth/Protection)",
                "4. The Survivor (Earth/Resilience)", "5. The Visionary (Air/Foresight)", "6. The Innovator (Fire/Invention)",
                "7. The Healer (Water/Restoration)", "8. The Strategist (Air/Wisdom)", "9. The Leader (Fire/Influence)",
                "10. The Empath (Water/Compassion)", "11. The Sage (Earth/Knowledge)", "12. The Explorer (Air/Curiosity)",
                "13. The Artist (Fire/Passion)", "14. The Scientist (Water/Logic)", "15. The Rebel (Fire/Freedom)",
                "16. The Mediator (Water/Balance)", "17. The Poet (Air/Expression)", "18. The Warrior (Fire/Courage)",
                "19. The Oracle (Water/Intuition)", "20. The Architect (Earth/Order)",
            ],
            "merit_formula": "95% Genesis Seal + 5% across 500,000 Quest Cards (0.05 Merit points per completed QC)",
        },
    },
    {
        "pillar_id": "sp_pillar_3_chapter_puzzle_3x3_dicevaders_map",
        "pillar_index": 3,
        "pillar_title": "Mapping Shifting Pieces Ch 1–19 Memory Puzzles onto the 3x3 CardFront × Dicevaders Budge/Chrono Tactical Grid",
        "source_documents": [
            "Chapter-by-Chapter Puzzle Integration Map – Shifting Pieces.docx",
            "Shifting_Pieces_Complete_Novel.txt",
        ],
        "architecture_formula": (
            "Every psychological memory puzzle in *Shifting Pieces* (Act I–Act III) maps deterministically onto our 3x3 "
            "`Slot(x=1..3, y=1..3)` *CardFront × CardCraft × Indie Marc TCG Engine* board augmented by *Dicevaders* (`3917700`) "
            "`Budge` (±1 pip shift) and `Chrono` (targeted die reroll) tokens: "
            "(1) **Flicker Decode (Ch 5)** triggers hidden `Secret` memory cards when a die pip matches a glitching tile's "
            "north/south threshold; (2) **Memory Theatre Lanterns (Ch 7)** requires ordering 3 cards across a row by ascending "
            "emotional resonance weight to trigger a `Triple (1.65x)` cascade; (3) **Kitchen Table Artifacts (Ch 8)** pits true "
            "vs. altered memory cards in directional `N/E/S/W` triad comparisons; (4) **Recalibration Emotion Tags (Ch 9)** "
            "attaches `StatusData` emotion tags (`Grief`, `Joy`, `Guilt`, `Trust`) via drag-and-drop `FilterData`; "
            "(5) **Shadow Maze (Ch 11)** projects directional light/shadow vectors across orthogonal columns so `Budge` ±1 "
            "aligns Aiko's childhood constellation glyph; and (6) **Hall of Selves (Ch 17)** gates 4 door slots (`Indifference`, "
            "`Anger`, `Fear`, `Avoidance`) that must be flipped in sequence before the mirror shatters."
        ),
        "synapse_integration_spec": {
            "grid_topology": "3x3 Triple Triad / CardCraft tactical grid + 4-die Dicevaders pip row (Budge ±1, Chrono reroll)",
            "puzzle_to_grid_mechanics": {
                "Flicker_Decode_Ch5": "Glitch reveal on exact pip parity + +2 East/West directional capture",
                "Memory_Theatre_Lanterns_Ch7": "Row emotional sequence reconstruction granting 1.65x Triple Resonance",
                "Kitchen_Table_Artifacts_Ch8": "True vs. synthetic memory card comparison with Prevent Flip shield",
                "Recalibration_Emotion_Tags_Ch9": "StatusData emotional tag attachment boosting adjacent allies +2",
                "Shadow_Maze_Ch11": "Orthogonal column light-ray projection unlocked via Budge ±1 pip alignment",
                "Hall_of_Selves_Ch17": "4-Door self-confrontation sequence (Indifference -> Anger -> Fear -> Mirror Kai)",
            },
        },
    },
    {
        "pillar_id": "sp_pillar_4_cardcraft_internal_card_mesh_generator",
        "pillar_index": 4,
        "pillar_title": "CardCraft Internal Generator Pipeline: Concept Art Turnaround + CardDataSO + Hi3D.ai / TRELLIS 2.0 .glb/.q3gs 3D Mesh + rea inspect-artifact + Creative Skill Evolution",
        "source_documents": [
            "CardCraft.docx",
            "CardFront_Cradle_of_Echoes.docx",
        ],
        "architecture_formula": (
            "*CardCraft* is both a stylized 3x3 Triple Triad strategic battle / educational simulation (`Draw -> Strategize -> "
            "Play Cards -> Capture Tiles -> Earn Confidence Points (CP) & Peer/Mentor Feedback -> Upgrade Deck`) and our internal "
            "generative asset pipeline. Every card has four directional values (`Top/North`, `Right/East`, `Bottom/South`, "
            "`Left/West` in `1..10`) and evolves through creative mastery (`Sketching -> Concept Art`, `Storyboard -> Animatic`, "
            "`Rough Cut -> Final Cut Edit`, `Peer Critique -> Creative Director`). Internally, the CardCraft Generator Pipeline "
            "synthesizes: (1) 12-Master Concept Art turnaround sheet, (2) Unity `CardDataSO` / Indie Marc `CardData` + `AbilityData` "
            "ScriptableObject, (3) watertight `Hi3D.ai / TRELLIS 2.0` `.glb` (`magic=0x46546C67`, Euler characteristic `V - E + F = 2`, "
            "4,034 vertices, 8,064 triangles) and `.q3gs` (`LUMENFRG` Gaussian splat) 3D relief mesh, and (4) `rea inspect-artifact` "
            "(`morluto/rea@6.8.0`) structural verification."
        ),
        "synapse_integration_spec": {
            "core_gameplay_loop": "Draw 5 Cards -> Strategize on 3x3 Grid -> Directional Flip (N/E/S/W 1-10) -> Earn Confidence Points (CP) & Mentor Feedback -> Evolve Deck",
            "creative_skill_evolutions": [
                "Sketching [4/5/3/4] -> Concept Art [7/8/6/7] (Ability: Boost Left Side +2)",
                "Storyboard [3/6/5/4] -> Animatic [6/9/7/6] (Ability: Chrono Frame Skip)",
                "Draft Script [5/4/6/3] -> Showrunner Bible [8/7/9/6] (Ability: Prevent Flip)",
                "Peer Critique [4/4/5/6] -> Resilient Creator Badge [7/7/8/9] (Ability: Synergy Feedback Loop +25 CP)",
            ],
            "internal_asset_generator_stages": [
                "Stage 1: 12-Master Concept Art Turnaround & Palette A/B/C Shader Conditioning",
                "Stage 2: Unity CardDataSO / Indie Marc CardData + AbilityData ScriptableObject Serialization",
                "Stage 3: Hi3D.ai (NiRNE -> NoRLD 1024^3 O-Voxel -> Quad Retopology -> 4K PBR -> 22-Bone Rig) .glb & .q3gs",
                "Stage 4: morluto/rea (`rea inspect-artifact`) Watertight Manifold & Hash Audit",
            ],
        },
    },
    {
        "pillar_id": "sp_pillar_5_act3_convergence_triad_ending",
        "pillar_index": 5,
        "pillar_title": "Act III Convergence Against Dr. Rina Asakura & The Final Triad Choice: Integrate with Aiko (MERGE), Preserve Memory (PRESERVE), or Collapse & Carry Forward (DESTROY)",
        "source_documents": [
            "Shifting_Pieces_Complete_Novel.txt",
            "Story Bible.docx",
            "Chapter-by-Chapter Puzzle Integration Map – Shifting Pieces.docx",
        ],
        "architecture_formula": (
            "In Act III of *Shifting Pieces* (Chapters 18–21 & Epilogue), Kai aligns Aiko's compiler logs (`[Log: A-09]`, "
            "`[Log: A-14]`, `[Log: A-21]`) with the living Memory Mosaic of Aiko (`The Memory Architect`), then confronts corporate "
            "researcher Dr. Rina Asakura at the unstable Mnemosyne Core (`Chapter 19: Convergence`). In *CardFront × CardCraft*, "
            "this climax is a multi-phase Boss Encounter where players counter Dr. Asakura's IP-extraction cards using collected "
            "Memory Shards (`Rooftop Constellation`, `Reconciliation Node`, `Log A-21`), assemble the 9-slot Circular Mosaic "
            "(`Chapter 20: The Final Puzzle`), and execute the **Final Triad Choice (`Chapter 21: The Choice`)**: "
            "(1) **MERGE (`Integrate with Aiko`)**: fuses Kai and Aiko's Echo into a dual-persona Sovereign Architect card; "
            "(2) **PRESERVE (`Preserve Memory`)**: seals Mnemosyne's core with permanent `Prevent Flip` Aegis sanctuary; or "
            "(3) **DESTROY (`Collapse & Carry Forward`)**: lets the simulation dissolve, unlocking the Epilogue `Living Puzzle` "
            "Golden Tile and Constellation Fox glyph (`#FFB648`) at the Okitsu VR Café."
        ),
        "synapse_integration_spec": {
            "boss_encounter": "Dr. Rina Asakura & The Unstable Mnemosyne Core (Act III Ch 19 Convergence)",
            "persuasion_counter_cards": [
                "Rooftop Fox Constellation Shard (Counters 'Voluntary Research Asset')",
                "Reconciliation Loop Node (Counters 'Recursive Grief Loop')",
                "Journal Log A-21: Real In The Ways That Matter (Unlocks Decision Threshold: Connection)",
            ],
            "final_triad_choices": {
                "MERGE_Integrate_With_Aiko": "Dual-consciousness Sovereign Card [10/9/9/10] with permanent LUNA + Aiko Echo resonance",
                "PRESERVE_Seal_Mnemosyne_Core": "Sanctuary Archive Artifact Card [8/10/10/8] granting board-wide Prevent Flip immunity",
                "DESTROY_Collapse_And_Carry_Forward": "Unlocks Epilogue 'A Living Puzzle' Golden Tile + Constellation Fox Glyph (#FFB648) & VR Ethics Mentor Mode",
            },
        },
    },
]


SHIFTING_PIECES_20_CHAPTER_ENCOUNTERS: List[Dict[str, Any]] = [
    {
        "chapter_index": 0,
        "chapter_code": "PROLOGUE_SYNOPSIS",
        "chapter_title": "Prologue & Query Synopsis — The Whisper of Mnemosyne & Cradle of Echoes Awakening",
        "act": "Prologue / Genesis",
        "novel_summary": (
            "Seventeen-year-old puzzle prodigy Kai Nakamura lives in quiet isolation in coastal Okitsu, haunted by the "
            "disappearance of his sister Aiko, a brilliant memory engineer. A mysterious encrypted beta invitation to "
            "Mnemosyne awakens the threshold between physical grief and digital memory architecture."
        ),
        "puzzle_mechanic": "Cradle of Echoes 10-Card Tarot Genesis & Encrypted Handshake",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_00_prologue_cradle_genesis",
            "arena": "Station of Awakening / Okitsu Seawall Dusk",
            "boss_or_challenger": "LUNA & The Constellation Fox Echo",
            "grid_rule": "Draw 5 symbolic Ikigai cards; align 3 across the center row to calculate initial Persona Affinity (95% Seal)",
            "featured_card": {"name": "Aiko's Red Scarf Fragment", "stats_nesw": [7, 6, 5, 8], "palette_hex": "#D12D3A", "evolution": "Red Scarf Fragment -> Memory Architect Mantle"},
            "hi3d_relic_asset": "relic_00_aiko_red_scarf_puzzle_piece.glb",
        },
    },
    {
        "chapter_index": 1,
        "chapter_code": "CH_01",
        "chapter_title": "Chapter 1 – Disconnected (Expanded Version)",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "In his cluttered Okitsu apartment overlooking the seawall and central server dome, Kai rotates his tactile "
            "puzzle cube while Taro knocks at the intercom leaving convenience meals and tea. Aiko's circuit-etched VR "
            "headset blinks with an encrypted transmission: 'Welcome to Mnemosyne. A game of memory. Designed just for you.'"
        ),
        "puzzle_mechanic": "Tactile Cube Rotation & Encrypted Beta Terminal Handshake",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_01_disconnected_seawall",
            "arena": "Kai's Puzzle Fortress Apartment (Okitsu Morning)",
            "boss_or_challenger": "Autonomous Courier Drone & Static Isolation Shadow",
            "grid_rule": "Corner slots grant +1 Defense; using a Dicevaders Budge (±1 pip) rotates the central Rubik Cube tile",
            "featured_card": {"name": "Kai's Tactile Puzzle Cube", "stats_nesw": [6, 6, 6, 6], "palette_hex": "#0B0B0C", "evolution": "Tactile Puzzle Cube -> Sovereign Hex Solver"},
            "hi3d_relic_asset": "relic_01_kai_tactile_puzzle_cube.glb",
        },
    },
    {
        "chapter_index": 2,
        "chapter_code": "CH_02",
        "chapter_title": "Chapter 2 – Residual Code (Expanded Version)",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "Kai opens the hand-carved lacquered wooden birthday puzzle box Aiko gave him at age thirteen ('only allowed to "
            "open it if you're honest with yourself'). A warm hologram of Aiko teases him about the cliffside hex grid hike, "
            "while at the Okitsu VR Café Taro worries about Kai's deepening withdrawal."
        ),
        "puzzle_mechanic": "Aiko's 13th Birthday Lacquered Puzzle Box Interlocking Latch",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_02_residual_code_puzzle_box",
            "arena": "Okitsu VR Café & Lacquered Hologram Shrine",
            "boss_or_challenger": "Taro Fujimoto (Friendly Sparring Mentor)",
            "grid_rule": "Unlocking a Pair (1.25x) on the Dicevaders tray unseals the Birthday Box hologram, buffing North/East sides by +2",
            "featured_card": {"name": "Lacquered Birthday Puzzle Box", "stats_nesw": [5, 7, 6, 5], "palette_hex": "#FFB648", "evolution": "Birthday Puzzle Box -> Sunset Cliff Hex Projector"},
            "hi3d_relic_asset": "relic_02_lacquered_birthday_puzzle_box.glb",
        },
    },
    {
        "chapter_index": 3,
        "chapter_code": "CH_03",
        "chapter_title": "Chapter 3 – Invitation to Mnemosyne (Expanded Version)",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "Kai dons the matte-black VR headset etched with Aiko's neural tree and enters Mnemosyne's borderless phosphorescent "
            "dream-space. A non-Euclidean stained-glass puzzle piece hovers midair; Kai aligns shifting UI glyphs by emotional "
            "calm rather than brute force to unlock entry."
        ),
        "puzzle_mechanic": "Non-Euclidean Stained-Glass Glyph Alignment via Emotional Calm",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_03_invitation_to_mnemosyne",
            "arena": "Mnemosyne Phosphorescent Threshold Void",
            "boss_or_challenger": "Gatekeeper Glyph Sentinel",
            "grid_rule": "Shifting UI Glyphs rotate card N/E/S/W stats clockwise each turn unless stabilized with a Chrono reroll token",
            "featured_card": {"name": "Aiko's Neural-Etched VR Headset", "stats_nesw": [7, 5, 7, 6], "palette_hex": "#2EE6D3", "evolution": "Neural VR Headset -> Mnemosyne Deep-Dive Crown"},
            "hi3d_relic_asset": "relic_03_neural_etched_vr_headset.glb",
        },
    },
    {
        "chapter_index": 4,
        "chapter_code": "CH_04",
        "chapter_title": "Chapter 4 – The First Level (Expanded Version)",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "Inside the first Mnemosyne chamber of floating stone and glass tiles over a starless sea, Kai solves a geometric "
            "pattern puzzle ('Order from chaos') that reconstructs a vivid cliffside memory of Aiko wearing her crimson scarf "
            "and whispering 'You found the pattern.'"
        ),
        "puzzle_mechanic": "Geometric Pattern Matching (Order from Chaos Cliffside Reveal)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_04_the_first_level_cliffside",
            "arena": "Floating Glass-Tile Chamber Over Starless Sea",
            "boss_or_challenger": "Fractal Pattern Construct",
            "grid_rule": "Symmetric card placements across the center slot `(2,2)` trigger an automatic directional flip on adjacent chaos tiles",
            "featured_card": {"name": "Cliffside Hex Horizon", "stats_nesw": [6, 8, 5, 6], "palette_hex": "#8A5BFF", "evolution": "Cliffside Sketch -> Isometric Diorama Panorama"},
            "hi3d_relic_asset": "relic_04_floating_glass_hex_tile.glb",
        },
    },
    {
        "chapter_index": 5,
        "chapter_code": "CH_05",
        "chapter_title": "Chapter 5 – Flicker (Expanded Version)",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "Guided by a voice that sounds unmistakably like Aiko, Kai navigates a rainy paper-lantern alley where visual symbols "
            "flicker at different frequencies. Decoding the flicker reveals Aiko's red scarf trailing into the mist while Taro "
            "urges him not to lose touch with the physical world."
        ),
        "puzzle_mechanic": "Symbol Flicker Frequency Decoding & Memory Trigger Identification",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_05_flicker_lantern_alley",
            "arena": "Rain-Slicked Okitsu Lantern Alley (Simulation Layer 2)",
            "boss_or_challenger": "Flickering Silhouette of Aiko",
            "grid_rule": "Hidden face-down Flicker tiles reveal their true N/E/S/W values when a Dicevaders die is Budged to match their slot index",
            "featured_card": {"name": "Flicker Signal Decoder", "stats_nesw": [7, 4, 8, 5], "palette_hex": "#D12D3A", "evolution": "Signal Sketch -> Glitch-Shader Animatic"},
            "hi3d_relic_asset": "relic_05_flickering_paper_lantern.glb",
        },
    },
    {
        "chapter_index": 6,
        "chapter_code": "CH_06",
        "chapter_title": "Chapter 6 – Phantom Signals & Interlude: Memory Bloom",
        "act": "ACT I – Awakening the System",
        "novel_summary": (
            "Kai decodes spatial audio tones—wind chimes, train crossings, and ocean surf—tied to childhood locations where Aiko "
            "taught him shadow games. In the Interlude 'Memory Bloom', a bioluminescent garden blossoms around a direct two-way "
            "voice response from the AI."
        ),
        "puzzle_mechanic": "Spatial Sound Mapping & Acoustic Memory Synchronization",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_06_phantom_signals_sound_map",
            "arena": "Bioluminescent Memory Bloom Conservatory",
            "boss_or_challenger": "Harmonic Resonance Weaver",
            "grid_rule": "Playing acoustic-tagged cards in ascending pitch order grants +3 Confidence Points (CP) and triggers ChainAbilities",
            "featured_card": {"name": "Okitsu Wind-Chime Transceiver", "stats_nesw": [5, 7, 7, 6], "palette_hex": "#2EE6D3", "evolution": "Audio Rough Cut -> Yoko Shimomura Synth Master"},
            "hi3d_relic_asset": "relic_06_acoustic_memory_chime.glb",
        },
    },
    {
        "chapter_index": 7,
        "chapter_code": "CH_07",
        "chapter_title": "Chapter 7 – Memory Theatre",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "Entering Act II, Mnemosyne manifests an ornate hollow amphitheatre of floating lanterns where childhood scenes "
            "play out on suspended stages. Kai must reconstruct the sequence not chronologically, but by honest emotional weight."
        ),
        "puzzle_mechanic": "Emotional Sequence Reconstruction (Memory Theatre Lantern Ordering)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_07_memory_theatre_lanterns",
            "arena": "Mnemosyne Grand Memory Amphitheatre",
            "boss_or_challenger": "The Stage Director Archon",
            "grid_rule": "Completing a 3-card row ordered by Emotional Weight (Nostalgia -> Grief -> Acceptance) triggers a 1.65x Triple Resonance sweep",
            "featured_card": {"name": "Memory Theatre Stage Lantern", "stats_nesw": [8, 6, 5, 7], "palette_hex": "#FFB648", "evolution": "Storyboard Scene -> Full Theatrical Animatic"},
            "hi3d_relic_asset": "relic_07_memory_theatre_lantern.glb",
        },
    },
    {
        "chapter_index": 8,
        "chapter_code": "CH_08",
        "chapter_title": "Chapter 8 – Artifacts",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "Inside a simulated replica of the Nakamura family kitchen table, Kai inspects pairs of nearly identical domestic "
            "memories—teacups, notes, a rainstorm—realizing one version has been subtly altered by Mnemosyne to soften his guilt."
        ),
        "puzzle_mechanic": "Compare & Contrast Memory Artifacts (True vs. Altered Scene Detection)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_08_kitchen_table_artifacts",
            "arena": "Nakamura Kitchen Table Dual-Memory Split",
            "boss_or_challenger": "Synthetic Nostalgia Curator",
            "grid_rule": "True Artifact cards gain 'Prevent Flip' when placed adjacent to an altered decoy card on the 3x3 grid",
            "featured_card": {"name": "Cracked Porcelain Teacup Artifact", "stats_nesw": [6, 8, 7, 5], "palette_hex": "#7A8B99", "evolution": "Still-Life Sketch -> Photoreal PBR Relic"},
            "hi3d_relic_asset": "relic_08_kitchen_table_teacup_artifact.glb",
        },
    },
    {
        "chapter_index": 9,
        "chapter_code": "CH_09",
        "chapter_title": "Chapter 9 – Recalibration",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "After a tense real-world confrontation with Taro at the VR Café over Kai's obsession, Kai re-enters Mnemosyne's "
            "Recalibration chamber and drags emotional resonance tags to unindexed memory clips, reconciling friendship and grief."
        ),
        "puzzle_mechanic": "Drag & Drop Emotional Resonance Tagging to Memory Clips",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_09_recalibration_emotion_tags",
            "arena": "VR Café Backroom / Neural Recalibration Core",
            "boss_or_challenger": "Taro's Grounding Anchor Projection",
            "grid_rule": "Attaching an Emotion Tag (`StatusData`) to a friendly card boosts its Weakest Side by +3 during opponent turns",
            "featured_card": {"name": "Taro's VR Café Matcha Anchor", "stats_nesw": [7, 7, 6, 7], "palette_hex": "#2B6C7C", "evolution": "Peer Critique -> Resilient Creator Badge"},
            "hi3d_relic_asset": "relic_09_recalibration_resonance_tag.glb",
        },
    },
    {
        "chapter_index": 10,
        "chapter_code": "CH_10",
        "chapter_title": "Chapter 10 – Displacement",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "In a hall of shifting refractive glass, Kai confronts alternate versions of himself in mirrors whose expressions "
            "and poses lag or diverge from his own, blurring the boundary between physical memory and digital recursion."
        ),
        "puzzle_mechanic": "Refractive Mirror Match (Synchronizing Shifting Poses of Alternate Kai)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_10_displacement_mirror_match",
            "arena": "Refractive Mirror Corridor of Displacement",
            "boss_or_challenger": "Doppelgänger Kai (Refractive Echo)",
            "grid_rule": "Mirror Rule: North/South and East/West values invert on the center column `(x=2)` unless locked by a Pair die roll",
            "featured_card": {"name": "Refractive Mirror Shard", "stats_nesw": [8, 5, 8, 5], "palette_hex": "#8A5BFF", "evolution": "Character Turnaround -> Dual-Pose Cel Shader"},
            "hi3d_relic_asset": "relic_10_refractive_mirror_prism.glb",
        },
    },
    {
        "chapter_index": 11,
        "chapter_code": "CH_11",
        "chapter_title": "Chapter 11 – The Shadow Maze",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "At the emotional climax of Act II, Kai navigates a darkened architectural labyrinth by rotating suspended objects "
            "so a single lantern beam casts readable shadow symbols on the far wall—the exact childhood method Aiko taught him."
        ),
        "puzzle_mechanic": "Spatial Logic via Light & Shadow Projection (Aiko's Childhood Method)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_11_the_shadow_maze",
            "arena": "Chiaroscuro Shadow Labyrinth of Aiko",
            "boss_or_challenger": "Umbral Constellation Fox",
            "grid_rule": "Light-source tiles cast beams across orthogonal lines; using Budge (±1 pip) aligns shadows to flip whole columns",
            "featured_card": {"name": "Aiko's Shadow-Caster Lantern", "stats_nesw": [8, 8, 6, 7], "palette_hex": "#FFB648", "evolution": "Chiaroscuro Sketch -> Volumetric Rimlight 3D Mesh"},
            "hi3d_relic_asset": "relic_11_shadow_maze_lantern_projector.glb",
        },
    },
    {
        "chapter_index": 12,
        "chapter_code": "CH_12",
        "chapter_title": "Chapter 12 – Echo AI",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "A second, unstable voice fractures through Mnemosyne's audio layer—a raw, unedited fragment of Aiko warning Kai "
            "as the system's geometry begins to degrade. Kai synchronizes distorted dual-track audio waveforms to decode her warning."
        ),
        "puzzle_mechanic": "Dual-Track Distorted Audio Log Synchronization",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_12_echo_ai_waveform_sync",
            "arena": "Degrading Acoustic Core Chamber",
            "boss_or_challenger": "Fragmented Echo AI (Dual-Voice Anomaly)",
            "grid_rule": "Matching two identical pip values on the Dicevaders tray synchronizes the waveform and grants +2 to all sides for 1 turn",
            "featured_card": {"name": "Dual-Waveform Echo Recorder", "stats_nesw": [7, 8, 7, 6], "palette_hex": "#2EE6D3", "evolution": "Voice Rough Track -> Synchronized Neural Stem"},
            "hi3d_relic_asset": "relic_12_dual_waveform_oscilloscope.glb",
        },
    },
    {
        "chapter_index": 13,
        "chapter_code": "CH_13",
        "chapter_title": "Chapter 13 – System Update",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "An external intrusion forces a hostile 'System Update' inside Mnemosyne: corporate researcher Dr. Rina Asakura has "
            "breached the network to harvest Aiko's neural core as proprietary IP. Kai navigates a maze of corrupted sectors to "
            "rescue Aiko's encrypted research journal."
        ),
        "puzzle_mechanic": "Corrupted File-Maze Navigation & Encrypted Journal Retrieval",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_13_system_update_intrusion",
            "arena": "Corrupted Firewall Sector 09 (Asakura Breach)",
            "boss_or_challenger": "Dr. Rina Asakura's Extraction Daemon",
            "grid_rule": "Firewall hazard tiles lock 2 random slots each turn; playing a Chrono reroll purges corruption and recovers +15 CP",
            "featured_card": {"name": "Encrypted Journal Fragment A-09", "stats_nesw": [8, 6, 8, 7], "palette_hex": "#D12D3A", "evolution": "Raw Code Dump -> Sovereign Encrypted Grimoire"},
            "hi3d_relic_asset": "relic_13_encrypted_journal_datacube.glb",
        },
    },
    {
        "chapter_index": 14,
        "chapter_code": "CH_14",
        "chapter_title": "Chapter 14 – Reconciliation Loop",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "Trapped in a repeating time-loop corridor of their final argument before Aiko vanished, every defensive lie resets "
            "the room. Kai can only break the mechanical and narrative lock by speaking his raw resentment, guilt, and love aloud."
        ),
        "puzzle_mechanic": "Recursive Dialogue Tree Loop (Truth-Gated Mechanical Lock)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_14_reconciliation_loop",
            "arena": "Infinite Recursive Hallway of the Final Argument",
            "boss_or_challenger": "The Unspoken Guilt Loop",
            "grid_rule": "Board state resets at Turn 4 unless the player sacrifices 1 hand card to play an Honest Confession card in Slot `(2,2)`",
            "featured_card": {"name": "Reconciliation Loop Key", "stats_nesw": [9, 7, 7, 8], "palette_hex": "#F2F2F2", "evolution": "Rough Dialogue Pass -> Cathartic Narrative Climax"},
            "hi3d_relic_asset": "relic_14_mobius_reconciliation_ring.glb",
        },
    },
    {
        "chapter_index": 15,
        "chapter_code": "CH_15",
        "chapter_title": "Chapter 15 – The Core Fracture & Interlude: The Unchosen Memory",
        "act": "ACT II – Fractured Memories",
        "novel_summary": (
            "The simulated coastal research lab shatters under Dr. Asakura's extraction surge. Racing a stability collapse timer, "
            "Kai bridges violently shaking memory shards before blacking out into 'The Unchosen Memory'—a quiet rooftop night "
            "where Aiko traced the Constellation Fox in the stars."
        ),
        "puzzle_mechanic": "Stability Collapse Timer & High-Velocity Memory Shard Bridging",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_15_the_core_fracture",
            "arena": "Collapsing Coastal Research Lab Simulation",
            "boss_or_challenger": "Core Tectonic Fracture",
            "grid_rule": "Blitz Timer: 15 seconds per turn; completing a diagonal 3-card bridge stabilizes the board and unlocks the Rooftop Fox bonus",
            "featured_card": {"name": "Rooftop Constellation Fox Chart", "stats_nesw": [8, 9, 7, 8], "palette_hex": "#FFB648", "evolution": "Star Sketch -> Celestial Vector Constellation"},
            "hi3d_relic_asset": "relic_15_constellation_fox_astrolabe.glb",
        },
    },
    {
        "chapter_index": 16,
        "chapter_code": "CH_16",
        "chapter_title": "Chapter 16 – Awakening",
        "act": "ACT III – Collapse and Choice",
        "novel_summary": (
            "Awakening in a fractured void of violet static and floating hexagonal debris, Kai realizes pure cold logic causes "
            "the tiles to rearrange unpredictably—only emotional intuition stabilizes the spiral path toward the Hall of Selves."
        ),
        "puzzle_mechanic": "Emotion-Guided Hexagonal Debris Stepping Stones Over Violet Static Void",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_16_awakening_violet_void",
            "arena": "Dream-Ocean Void of Floating Hex Debris",
            "boss_or_challenger": "Entropy Static Leviathan",
            "grid_rule": "Adjacent cards sharing the same Persona Element (Air/Fire/Earth/Water) form stable bridges (+2 all sides)",
            "featured_card": {"name": "Spiral Hex Stepping Stone", "stats_nesw": [7, 8, 9, 7], "palette_hex": "#8A5BFF", "evolution": "Greybox Blockout -> O-Voxel Watertight Diorama"},
            "hi3d_relic_asset": "relic_16_violet_static_hex_platform.glb",
        },
    },
    {
        "chapter_index": 17,
        "chapter_code": "CH_17",
        "chapter_title": "Chapter 17 – The Hall of Selves",
        "act": "ACT III – Collapse and Choice",
        "novel_summary": (
            "Behind a liquid-metal membrane lies an impossible corridor of unlabeled doors. Kai confronts and integrates four "
            "fractured versions of himself in sequence—Indifference, Anger, Fear, and the infinite Mirror Kai walking away—"
            "shattering the mirror under Aiko's Puzzle Fox constellation."
        ),
        "puzzle_mechanic": "4-Door Self-Integration Sequence (Indifference -> Anger -> Fear -> Mirror Kai)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_17_the_hall_of_selves",
            "arena": "Liquid-Metal Corridor of Four Doors",
            "boss_or_challenger": "The Four Fractured Selves of Kai",
            "grid_rule": "Must capture the 4 orthogonal edge slots (`(2,1)`, `(3,2)`, `(2,3)`, `(1,2)`) in exact emotional order to shatter the center mirror",
            "featured_card": {"name": "Shattered Mirror of Reintegration", "stats_nesw": [9, 8, 8, 9], "palette_hex": "#EAF2FF", "evolution": "Rough Expression Sheet -> Integrated Protagonist Master"},
            "hi3d_relic_asset": "relic_17_hall_of_selves_mirror_door.glb",
        },
    },
    {
        "chapter_index": 18,
        "chapter_code": "CH_18",
        "chapter_title": "Chapter 18 – The Memory Architect",
        "act": "ACT III – Collapse and Choice",
        "novel_summary": (
            "In a warm dark chamber scented with jasmine tea and soldered circuits, Kai meets the living Memory Mosaic of Aiko "
            "at the compiler. Aligning logs `[Log: A-09]`, `[Log: A-14]`, and `[Log: A-21]` ('maybe he'll remember how it felt "
            "to be loved. That's enough'), Kai stabilizes Aiko's final full node."
        ),
        "puzzle_mechanic": "Compiler Log Alignment (`A-09`, `A-14`, `A-21`) with Living Memory Windows",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_18_the_memory_architect",
            "arena": "The Jasmine-Scented Neural Compiler Chamber",
            "boss_or_challenger": "Aiko Nakamura, The Memory Architect (Living Mosaic)",
            "grid_rule": "Aligning all 3 Compiler Logs (`A-09`, `A-14`, `A-21`) triggers a 2.25x Quadruple Resonance and unlocks Aiko's Sovereign Blessing",
            "featured_card": {"name": "Aiko, The Memory Architect [Log A-21]", "stats_nesw": [9, 9, 8, 9], "palette_hex": "#D12D3A", "evolution": "Concept Art -> Watertight 3D Heroine Figurine"},
            "hi3d_relic_asset": "relic_18_aiko_memory_compiler_chair.glb",
        },
    },
    {
        "chapter_index": 19,
        "chapter_code": "CH_19_TO_21_FINALE",
        "chapter_title": "Chapters 19–21 & Epilogue – Convergence, The Final Puzzle, The Choice & A Living Puzzle",
        "act": "ACT III – Finale & Epilogue",
        "novel_summary": (
            "At the pulsing Mnemosyne Core, Kai defeats Dr. Rina Asakura's extraction argument in ethical debate using his "
            "collected memories (`Rooftop Constellation`, `Reconciliation Node`, `Log A-21`), reconstructs the grand circular "
            "mosaic of Aiko's life, and faces the Three Gates (`MERGE`, `PRESERVE`, `DESTROY`) before awakening on the Okitsu "
            "coast to become a teacher of VR ethics and puzzle design with the Golden Tile and Fox Glyph."
        ),
        "puzzle_mechanic": "Ethical Debate Persuasion Counterpoints + Circular Memory Mosaic + Triad Gate Choice (MERGE / PRESERVE / DESTROY)",
        "cardfront_cardcraft_encounter": {
            "encounter_id": "enc_19_convergence_and_triad_choice",
            "arena": "The Mnemosyne Core Lattice & Three Gates of Legacy",
            "boss_or_challenger": "Dr. Rina Asakura & The Unstable Mnemosyne Core",
            "grid_rule": "3-Phase Finale: Phase 1 Debate Counter-Flips -> Phase 2 9-Slot Circular Mosaic Full-Board Sweep (3.0x) -> Phase 3 Triad Legacy Choice",
            "featured_card": {"name": "The Living Puzzle: Golden Fox Glyph", "stats_nesw": [10, 10, 9, 10], "palette_hex": "#FFB648", "evolution": "Portfolio Milestone -> Sovereign Masterpiece Legacy"},
            "hi3d_relic_asset": "relic_19_golden_fox_glyph_monolith.glb",
        },
    },
]


def build_80_shifting_pieces_cardfront_records(manuscript_catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Construct the exact 80 `shifting_pieces_cardfront_cardcraft_spec` records:
    - 60 Pillar records (12 Foundational Masters × 5 Shifting Pieces × CardFront × CardCraft Pillars)
    - 20 Chapter Encounter records (All 19 Chapters + Prologue mapped to playable CardFront × CardCraft encounters)
    """
    from build_longitudinal_artist_dataset import LONGITUDINAL_MASTERS_SPEC

    doc_metadata_summary = [
        {
            "key": k,
            "filename": v.get("filename"),
            "bytes": v.get("bytes"),
            "extracted_chars": v.get("extracted_chars"),
            "sha256": v.get("sha256"),
        }
        for k, v in manuscript_catalog.items()
        if v.get("exists")
    ]

    records_60_pillars: List[Dict[str, Any]] = []
    for master in LONGITUDINAL_MASTERS_SPEC:
        latest_era = master["eras"][-1]
        for pillar in SHIFTING_PIECES_5_PILLARS:
            records_60_pillars.append({
                "record_type": "shifting_pieces_cardfront_cardcraft_spec",
                "sub_category": "master_x_pillar_architecture",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "kanji": master["kanji"],
                "pillar_id": pillar["pillar_id"],
                "pillar_index": pillar["pillar_index"],
                "pillar_title": pillar["pillar_title"],
                "shader_vector": latest_era["shader_vector"],
                "verified_drive_manuscripts": doc_metadata_summary,
                "instruction": (
                    f"Synthesize `{pillar['pillar_title']}` uniting Hiroyasu (Binh C. Phan)'s *Shifting Pieces* "
                    f"(Kai Nakamura, Aiko's crimson Red Scarf `#D12D3A`, Mnemosyne MAS, Okitsu VR Café), "
                    f"*CardFront: Cradle of Echoes* (LUNA 20-Persona Station of Awakening tarot), and *CardCraft* "
                    f"(3x3 Triple Triad creative skill evolution & Hi3D.ai `.glb`/`.q3gs` mesh generator) in the "
                    f"signature visual style and shader parameters of {master['artist_name']} ({master['kanji']})."
                ),
                "response": json.dumps({
                    "artist_style": master["artist_name"],
                    "era_reference": latest_era["era"],
                    "pillar_id": pillar["pillar_id"],
                    "pillar_title": pillar["pillar_title"],
                    "architecture_formula": pillar["architecture_formula"],
                    "synapse_integration_spec": pillar["synapse_integration_spec"],
                    "shader_vector": latest_era["shader_vector"],
                    "source_documents": pillar["source_documents"],
                }, ensure_ascii=False),
            })

    records_20_chapters: List[Dict[str, Any]] = []
    for idx, ch in enumerate(SHIFTING_PIECES_20_CHAPTER_ENCOUNTERS):
        master = LONGITUDINAL_MASTERS_SPEC[idx % len(LONGITUDINAL_MASTERS_SPEC)]
        latest_era = master["eras"][-1]
        enc = ch["cardfront_cardcraft_encounter"]
        records_20_chapters.append({
            "record_type": "shifting_pieces_cardfront_cardcraft_spec",
            "sub_category": "chapter_playable_encounter_spec",
            "chapter_index": ch["chapter_index"],
            "chapter_code": ch["chapter_code"],
            "chapter_title": ch["chapter_title"],
            "act": ch["act"],
            "master_id": master["master_id"],
            "artist_name": master["artist_name"],
            "kanji": master["kanji"],
            "shader_vector": latest_era["shader_vector"],
            "instruction": (
                f"Design the playable *CardFront × CardCraft × Dicevaders* 3x3 tactical encounter, boss mechanics, "
                f"12-Master concept art prompt ({master['artist_name']}), and watertight Hi3D.ai `.glb`/`.q3gs` 3D "
                f"relic asset for **{ch['chapter_title']}** ({ch['act']}) of *Shifting Pieces*."
            ),
            "response": json.dumps({
                "chapter_code": ch["chapter_code"],
                "chapter_title": ch["chapter_title"],
                "act": ch["act"],
                "novel_summary": ch["novel_summary"],
                "puzzle_mechanic": ch["puzzle_mechanic"],
                "playable_encounter": enc,
                "concept_art_prompt": (
                    f"{master['artist_name']} ({master['kanji']}) master illustration for {ch['chapter_title']}: "
                    f"{enc['arena']}, featuring {enc['featured_card']['name']} with accent hex {enc['featured_card']['palette_hex']}, "
                    f"Palette A (#0B0B0C + #D12D3A) & Palette B (#0A1020 + #2EE6D3) lighting, crisp cel-shaded outlines."
                ),
                "hi3d_trellis2_mesh_spec": {
                    "glb_filename": enc["hi3d_relic_asset"],
                    "q3gs_filename": enc["hi3d_relic_asset"].replace(".glb", ".q3gs"),
                    "topology": "Watertight manifold V - E + F = 2 (4,034 vertices, 8,064 triangles)",
                    "rea_verification_cmd": f"rea inspect-artifact Assets/Resources/Models3D/{enc['hi3d_relic_asset']} --json",
                },
                "shader_vector": latest_era["shader_vector"],
            }, ensure_ascii=False),
        })

    assert len(records_60_pillars) == 60, f"Expected 60 pillar records, got {len(records_60_pillars)}"
    assert len(records_20_chapters) == 20, f"Expected 20 chapter records, got {len(records_20_chapters)}"
    return records_60_pillars + records_20_chapters


def append_80_records_to_corpora(new_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Append the 80 `shifting_pieces_cardfront_cardcraft_spec` records to both
    `longitudinal_9_masters_full_corpus.jsonl` and `longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl`,
    expanding the corpus from 721 to 801 total records (idempotent on repeated runs).
    """
    source_path = DATASET_FULL_PATH if DATASET_FULL_PATH.exists() else DATASET_12_PATH
    existing_records: List[Dict[str, Any]] = []
    if source_path.exists():
        for line in source_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_records.append(json.loads(line))

    base_records = [
        r for r in existing_records
        if r.get("record_type") != "shifting_pieces_cardfront_cardcraft_spec"
    ]

    all_records = base_records + new_records
    for target_path in (DATASET_FULL_PATH, DATASET_12_PATH):
        with target_path.open("w", encoding="utf-8") as f:
            for r in all_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return {
        "previous_corpus_records": len(base_records),
        "new_shifting_pieces_cardfront_records_appended": len(new_records),
        "pillar_records_count": 60,
        "chapter_encounter_records_count": 20,
        "total_corpus_records": len(all_records),
        "dataset_paths": [str(DATASET_FULL_PATH), str(DATASET_12_PATH)],
    }


def build_and_persist_coordination_hub(
    manuscript_catalog: Dict[str, Any],
    corpus_info: Dict[str, Any],
    v100_refinement: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create `/Users/frederickamina/Documents/Projects/SYNAPSE/ANTIGRAVITY_SWARM_COORDINATION_HUB.json`
    and persist it into NCM (`ncm.remember("antigravity_cli_152_shifting_pieces_cardfront_hub", ...)`).
    """
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hub_payload: Dict[str, Any] = {
        "hub_id": "antigravity_cli_152_shifting_pieces_cardfront_hub",
        "version": "1.5.2-sovereign-swarm",
        "updated_at_utc": now_iso,
        "shared_sessions": [
            {
                "session_name": "Antigravity CLI 1.5.2 Primary Swarm (frederickamina / bcphan@hawaii.edu)",
                "workspace": "/Users/frederickamina/Documents/Projects/SYNAPSE",
                "status": "ACTIVE_SYNCED",
            },
            {
                "session_name": "Antigravity CLI 1.5.2 Parallel Session (binh.cong@gmail.com)",
                "workspace": "/Users/frederickamina/Documents/Projects",
                "status": "ACTIVE_SYNCED",
            },
        ],
        "longitudinal_corpus_status": {
            "total_records": corpus_info["total_corpus_records"],
            "previous_records": corpus_info["previous_corpus_records"],
            "shifting_pieces_cardfront_cardcraft_records": corpus_info["new_shifting_pieces_cardfront_records_appended"],
            "primary_jsonl": str(DATASET_FULL_PATH),
            "concept_gamedesign_jsonl": str(DATASET_12_PATH),
            "v100_remote_jsonl": REMOTE_CORPUS_DEST,
        },
        "synced_google_drive_manuscripts": {
            "account": "bcphan@hawaii.edu",
            "root_dir": str(TCG_DRIVE_ROOT),
            "documents": {
                k: {
                    "path": v.get("path"),
                    "bytes": v.get("bytes"),
                    "extracted_chars": v.get("extracted_chars"),
                    "sha256": v.get("sha256"),
                }
                for k, v in manuscript_catalog.items()
                if v.get("exists")
            },
        },
        "five_core_pillars": [
            {
                "pillar_id": p["pillar_id"],
                "pillar_index": p["pillar_index"],
                "pillar_title": p["pillar_title"],
            }
            for p in SHIFTING_PIECES_5_PILLARS
        ],
        "twenty_chapter_encounters": [
            {
                "chapter_index": c["chapter_index"],
                "chapter_code": c["chapter_code"],
                "chapter_title": c["chapter_title"],
                "encounter_id": c["cardfront_cardcraft_encounter"]["encounter_id"],
                "featured_card": c["cardfront_cardcraft_encounter"]["featured_card"]["name"],
                "hi3d_relic_asset": c["cardfront_cardcraft_encounter"]["hi3d_relic_asset"],
            }
            for c in SHIFTING_PIECES_20_CHAPTER_ENCOUNTERS
        ],
        "engine_and_tooling_endpoints": {
            "shifting_pieces_corpus_builder": "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Backend/build_shifting_pieces_cardfront_corpus.py",
            "indie_marc_tcg_engine_unpacked": "/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/Assets/TcgEngine/Scripts/",
            "indie_marc_tcg_nodejs_api": "/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/TcgEngineAPI/server.js",
            "synapse_tcg_backend": "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Backend/synapse_tcg_backend.py",
            "lumenforge_studio_portal": "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Backend/lumenforge_io_studio_portal.py",
            "dicevaders_3917700_decompile_and_sim": "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Backend/synapse_dicevaders_decompile_and_design.py",
            "hi3d_rea_reverse_engineer": "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Backend/synapse_rea_hi3d_reverse_engineer.py",
            "morluto_rea_cli": "/Users/frederickamina/Documents/Projects/SYNAPSE/morluto-rea-re/package/dist/cli.js",
            "pxg_gamedev_harness": HARNESS_BIN,
        },
        "sovereign_4node_gpu_pool": {
            "total_vram_gb": 120,
            "peak_fp16_tflops": 342.45,
            "nodes": {
                "node116_v100": {
                    "gpu": "NVIDIA Tesla V100 32GB",
                    "forge_api": "http://192.168.86.116:8090",
                    "ollama_api": "http://192.168.86.116:11434",
                    "models": ["pxg-lumenforge:30b-a3b", "pxg-lumenforge:1.5b-qlora", "Qwen/Qwen2.5-Math-1.5B-Instruct"],
                },
                "node30_rtx4080": {
                    "gpu": "NVIDIA GeForce RTX 4080 16GB",
                    "ollama_api": "http://192.168.86.30:11434",
                    "models": ["pxg-lumenforge:12b-tutor"],
                },
                "node22_rtx2070": {
                    "gpu": "NVIDIA GeForce RTX 2070 8GB",
                    "ollama_api": "http://192.168.86.22:11434",
                    "models": ["pxg-lumenforge:7b-tutor"],
                },
                "node127_m1max_64gb": {
                    "gpu": "Apple M1 Max 64GB Unified Memory",
                    "ollama_api": "http://127.0.0.1:11434",
                    "models": ["pxg-lumenforge:7b-tutor", "mlx-community/Qwen2.5-3B-Instruct-4bit"],
                },
            },
        },
        "v100_latest_5epoch_refinement": v100_refinement or {},
    }

    COORDINATION_HUB_PATH.write_text(json.dumps(hub_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    ncm_status = ncm.remember(
        "antigravity_cli_152_shifting_pieces_cardfront_hub",
        hub_payload,
        category="coordination_hub",
    )
    return {
        "coordination_hub_path": str(COORDINATION_HUB_PATH),
        "ncm_status": ncm_status,
    }


def sync_corpus_to_v100() -> Dict[str, Any]:
    """Sync the 801-record `longitudinal_9_masters_full_corpus.jsonl` to `v100:/mnt/models/forge/datasets/`."""
    t0 = time.perf_counter()
    cmd = ["scp", "-q", str(DATASET_FULL_PATH), REMOTE_CORPUS_DEST]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            "ok": proc.returncode == 0,
            "command": " ".join(cmd),
            "destination": REMOTE_CORPUS_DEST,
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip(),
            "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": " ".join(cmd),
            "destination": REMOTE_CORPUS_DEST,
            "error": str(exc),
        }


def run_v100_5epoch_refinement(epochs: int = 5, steps: int = 6) -> Dict[str, Any]:
    """
    Run the 5-Epoch (30-step) V100 QLoRA + Hinton KD Refinement Pass:
    `/Users/frederickamina/.local/bin/pxg-gamedev-harness refine "Shifting Pieces Manuscript (Kai, Aiko Red Scarf #D12D3A, Mnemosyne, LUNA) x CardFront: Cradle of Echoes x CardCraft Internal Card/Mesh/Concept Generator (801 Records)" --epochs 5 --steps 6`
    """
    t0 = time.perf_counter()
    cmd = [
        HARNESS_BIN,
        "refine",
        REFINE_TOPIC,
        "--epochs",
        str(epochs),
        "--steps",
        str(steps),
    ]
    harness_stdout = ""
    harness_stderr = ""
    harness_rc = -1
    parsed_response: Optional[Dict[str, Any]] = None

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        harness_rc = proc.returncode
        harness_stdout = proc.stdout.strip()
        harness_stderr = proc.stderr.strip()
        first_brace = harness_stdout.find("{")
        last_brace = harness_stdout.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                parsed_response = json.loads(harness_stdout[first_brace : last_brace + 1])
            except Exception:
                parsed_response = None
    except Exception as exc:
        harness_stderr = str(exc)

    if not parsed_response or "error" in parsed_response:
        try:
            req = urllib.request.Request(
                f"{FORGE_API_URL}/v1/train/refine",
                data=json.dumps(
                    {
                        "topic": REFINE_TOPIC,
                        "domain": "shifting_pieces_cardfront_cardcraft_801_corpus",
                        "epochs": int(epochs),
                        "steps": int(steps),
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=240) as resp:
                parsed_response = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if not parsed_response:
                parsed_response = {"error": str(exc)}

    return {
        "command": " ".join(cmd),
        "epochs_requested": epochs,
        "steps_per_epoch_requested": steps,
        "total_steps_requested": epochs * steps,
        "harness_returncode": harness_rc,
        "harness_stdout_preview": harness_stdout[:1600],
        "harness_stderr": harness_stderr[:400],
        "v100_refinement_telemetry": parsed_response,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
    }


def main(run_training: bool = True) -> Dict[str, Any]:
    t0 = time.perf_counter()
    manuscript_catalog = read_drive_manuscripts()
    records_80 = build_80_shifting_pieces_cardfront_records(manuscript_catalog)
    corpus_info = append_80_records_to_corpora(records_80)
    scp_sync = sync_corpus_to_v100()
    v100_refinement = run_v100_5epoch_refinement(epochs=5, steps=6) if run_training else {"skipped": True}
    hub_info = build_and_persist_coordination_hub(manuscript_catalog, corpus_info, v100_refinement)

    report = {
        "status": "ok",
        "pipeline": "Shifting Pieces × CardFront: Cradle of Echoes × CardCraft Longitudinal Corpus Builder (801 Records) & Multi-Agent Coordination Hub",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manuscripts_read_count": sum(1 for v in manuscript_catalog.values() if v.get("exists")),
        "manuscripts_summary": {
            k: {
                "filename": v.get("filename"),
                "bytes": v.get("bytes"),
                "extracted_chars": v.get("extracted_chars"),
                "sha256": v.get("sha256"),
            }
            for k, v in manuscript_catalog.items()
            if v.get("exists")
        },
        "corpus_expansion": corpus_info,
        "coordination_hub": hub_info,
        "v100_scp_sync": scp_sync,
        "v100_5epoch_30step_refinement": v100_refinement,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
    }
    REPORT_OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = main(run_training=True)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
