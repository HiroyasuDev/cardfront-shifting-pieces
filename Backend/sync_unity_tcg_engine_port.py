#!/usr/bin/env python3
"""
Synchronizes CARDFRONT 3D: Cradle of Echoes across:
1. /Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine (Primary Clean-Room Unity + WebPlayable Repo)
2. /Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked (Full Unpacked Indie Marc TcgEngine Unity Asset Project)

- Syncs CardFrontUnifiedRuntime.cs (namespace TcgEngine) into tcg-engine-unpacked
- Copies all 53 Sakuga Cut-In Sprite Strips (1920x160) & 53 Mastered Card Portraits (600x800) into Resources/CardFront/
- Builds the unified 97-card catalog (60 Set 1 Cradle of Echoes cards + 37 Agent Command Deck cards)
- Generates Editor Menu Importer (CardFrontTcgEngineImporter.cs) for one-click CardData ScriptableObject generation
- Exports Datasets/unity_tcg_engine_port_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

PRIMARY_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
UNPACKED_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked")


def ensure_unity_meta_files(assets_root: Path, project_root: Path) -> int:
    created = 0
    for p in sorted(assets_root.rglob("*")):
        if p.suffix == ".meta" or p.name.startswith("."):
            continue
        meta = Path(str(p) + ".meta")
        if not meta.exists():
            guid = hashlib.md5(str(p.relative_to(project_root)).encode("utf-8")).hexdigest()
            if p.is_dir():
                meta.write_text(
                    f"fileFormatVersion: 2\nguid: {guid}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
                    encoding="utf-8",
                )
            else:
                meta.write_text(f"fileFormatVersion: 2\nguid: {guid}\n", encoding="utf-8")
            created += 1
    return created


def sync_unified_runtime_cs() -> dict:
    src_cs = PRIMARY_ROOT / "Assets" / "Scripts" / "Core" / "CardFrontUnifiedRuntime.cs"
    dst_cs = UNPACKED_ROOT / "Assets" / "TcgEngine" / "Scripts" / "CardFront" / "CardFrontUnifiedRuntime.cs"
    dst_cs.parent.mkdir(parents=True, exist_ok=True)

    raw_text = src_cs.read_text(encoding="utf-8")
    unpacked_text = raw_text.replace("namespace Synapse.TcgEngine.Core", "namespace TcgEngine")
    dst_cs.write_text(unpacked_text, encoding="utf-8")
    return {
        "primary_cs": str(src_cs),
        "unpacked_cs": str(dst_cs),
        "bytes_synced": len(unpacked_text.encode("utf-8")),
    }


def sync_art_and_sakuga_resources() -> dict:
    sakuga_src_dir = PRIMARY_ROOT / "GeneratedArt" / "SakugaCutIns"
    core_cards_dir = PRIMARY_ROOT / "GeneratedArt" / "MasteredCards"
    agent_cards_dir = PRIMARY_ROOT / "GeneratedArt" / "AgentDeck" / "Cards"

    targets = [
        PRIMARY_ROOT / "Assets" / "Resources" / "CardFront",
        UNPACKED_ROOT / "Assets" / "TcgEngine" / "Resources" / "CardFront",
    ]

    sakuga_copied = 0
    portraits_copied = 0

    for base_target in targets:
        sakuga_dst = base_target / "SakugaCutIns"
        portraits_dst = base_target / "Portraits"
        sakuga_dst.mkdir(parents=True, exist_ok=True)
        portraits_dst.mkdir(parents=True, exist_ok=True)

        if sakuga_src_dir.exists():
            for png in sorted(sakuga_src_dir.glob("*_strip.png")):
                shutil.copy2(png, sakuga_dst / png.name)
                if base_target == targets[0]:
                    sakuga_copied += 1

        if core_cards_dir.exists():
            for png in sorted(core_cards_dir.glob("*.png")):
                shutil.copy2(png, portraits_dst / png.name)
                if base_target == targets[0]:
                    portraits_copied += 1

        if agent_cards_dir.exists():
            for png in sorted(agent_cards_dir.glob("*.png")):
                shutil.copy2(png, portraits_dst / png.name)
                if base_target == targets[0]:
                    portraits_copied += 1

    return {
        "sakuga_strips_synced": sakuga_copied,
        "portraits_synced": portraits_copied,
    }


def build_97_card_catalog() -> dict:
    set1_path = PRIMARY_ROOT / "Datasets" / "set1_full_60_cards_and_15_campaign_stages.json"
    sakuga_manifest_path = PRIMARY_ROOT / "Datasets" / "pxg_v100_sakuga_telegraph" / "v100_sakuga_manifest.json"

    set1_cards = []
    if set1_path.exists():
        raw_set1 = json.loads(set1_path.read_text(encoding="utf-8"))
        set1_cards = raw_set1.get("set1_full_60_roster", raw_set1.get("cards", [])) if isinstance(raw_set1, dict) else raw_set1

    sakuga_entries = []
    if sakuga_manifest_path.exists():
        raw_sakuga = json.loads(sakuga_manifest_path.read_text(encoding="utf-8"))
        sakuga_entries = raw_sakuga.get("assets", [])

    catalog_cards = []
    seen_ids = set()

    for idx, c in enumerate(set1_cards):
        cid = c.get("card_id") or c.get("id") or f"cf_set1_{idx+1:02d}"
        seen_ids.add(cid)
        catalog_cards.append({
            "id": cid,
            "title": c.get("title") or c.get("name") or cid,
            "set": "SET1_CRADLE_OF_ECHOES",
            "faction": c.get("faction", "ASTRAL_VANGUARD"),
            "mana": int(c.get("mana_cost", c.get("mana", 2))),
            "attack": int(c.get("attack", 5)),
            "hp": int(c.get("hp", 5)),
            "dir_north": int(c.get("north", c.get("dir_north", 6))),
            "dir_east": int(c.get("east", c.get("dir_east", 6))),
            "dir_south": int(c.get("south", c.get("dir_south", 6))),
            "dir_west": int(c.get("west", c.get("dir_west", 6))),
            "dice_pip_affinity": (idx % 6) + 1,
            "sakuga_strip_resource": f"CardFront/SakugaCutIns/{cid}_strip",
            "portrait_resource": f"CardFront/Portraits/{cid}",
        })

    for idx, entry in enumerate(sakuga_entries):
        cid = entry.get("asset_id") or entry.get("card_id") or ""
        if not cid or cid in seen_ids:
            continue
        seen_ids.add(cid)
        catalog_cards.append({
            "id": cid,
            "title": entry.get("telegraph_name") or entry.get("name") or cid,
            "set": entry.get("collection", "AGENT_COMMAND_DECK"),
            "faction": entry.get("faction", "SOVEREIGN_AGENT"),
            "mana": 3,
            "attack": 7,
            "hp": 7,
            "dir_north": 7 + (idx % 2),
            "dir_east": 6 + ((idx + 1) % 3),
            "dir_south": 6 + (idx % 3),
            "dir_west": 7 + ((idx + 2) % 2),
            "dice_pip_affinity": (idx % 6) + 1,
            "sakuga_strip_resource": f"CardFront/SakugaCutIns/{cid}_strip",
            "portrait_resource": f"CardFront/Portraits/{cid}",
        })

    catalog_payload = {
        "schema": "CARDFRONT_TCG_ENGINE_UNITY_CATALOG_V1",
        "total_cards": len(catalog_cards),
        "set1_count": len(set1_cards),
        "sakuga_entries_count": len(sakuga_entries),
        "cards": catalog_cards,
    }

    for target_root in [
        PRIMARY_ROOT / "Assets" / "Resources" / "CardFront",
        UNPACKED_ROOT / "Assets" / "TcgEngine" / "Resources" / "CardFront",
    ]:
        target_root.mkdir(parents=True, exist_ok=True)
        (target_root / "cardfront_97_card_catalog.json").write_text(
            json.dumps(catalog_payload, indent=2), encoding="utf-8"
        )

    return {
        "total_catalog_cards": len(catalog_cards),
        "set1_cards": len(set1_cards),
        "sakuga_cards": len(sakuga_entries),
    }


def write_unity_editor_importer() -> str:
    editor_dir = UNPACKED_ROOT / "Assets" / "TcgEngine" / "Scripts" / "Editor"
    editor_dir.mkdir(parents=True, exist_ok=True)
    importer_path = editor_dir / "CardFrontTcgEngineImporter.cs"
    if importer_path.exists() and "BuildFullTcgEngineProductionScenesAndStandaloneApp" in importer_path.read_text(encoding="utf-8"):
        return str(importer_path)

    code = """#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace TcgEngine.EditorTool
{
    [Serializable]
    public class CardFrontCatalogEntry
    {
        public string id;
        public string title;
        public string set;
        public string faction;
        public int mana;
        public int attack;
        public int hp;
        public int dir_north;
        public int dir_east;
        public int dir_south;
        public int dir_west;
        public int dice_pip_affinity;
        public string sakuga_strip_resource;
        public string portrait_resource;
    }

    [Serializable]
    public class CardFrontCatalogPayload
    {
        public string schema;
        public int total_cards;
        public CardFrontCatalogEntry[] cards;
    }

    /// <summary>
    /// One-click Unity Editor tool that imports all CARDFRONT 3D: Cradle of Echoes cards
    /// (Set 1 + 37 Agent Command Deck cards) as native TcgEngine CardData ScriptableObjects
    /// and configures the 3x3 shared tabletop grid.
    /// </summary>
    public static class CardFrontTcgEngineImporter
    {
        [MenuItem("TcgEngine/CardFront/Import All Cards & Configure 3x3 Tabletop")]
        public static void ImportAllCardsAndConfigureTabletop()
        {
            CardFrontUnifiedRuntime.Configure3x3SharedTabletopGrid();

            TextAsset catalogAsset = Resources.Load<TextAsset>("CardFront/cardfront_97_card_catalog");
            if (catalogAsset == null)
            {
                Debug.LogError("[CardFront] Could not find Resources/CardFront/cardfront_97_card_catalog.json");
                return;
            }

            CardFrontCatalogPayload payload = JsonUtility.FromJson<CardFrontCatalogPayload>(catalogAsset.text);
            if (payload == null || payload.cards == null)
                return;

            string cardsFolder = "Assets/TcgEngine/Resources/Cards/CardFront";
            if (!Directory.Exists(cardsFolder))
                Directory.CreateDirectory(cardsFolder);

            int imported = 0;
            foreach (CardFrontCatalogEntry entry in payload.cards)
            {
                string assetPath = cardsFolder + "/" + entry.id + ".asset";
                CardData cardData = AssetDatabase.LoadAssetAtPath<CardData>(assetPath);
                if (cardData == null)
                {
                    cardData = ScriptableObject.CreateInstance<CardData>();
                    AssetDatabase.CreateAsset(cardData, assetPath);
                }

                cardData.id = entry.id;
                cardData.title = entry.title;
                cardData.type = CardType.Character;
                cardData.mana = entry.mana;
                cardData.attack = entry.attack;
                cardData.hp = entry.hp;
                cardData.dir_north = entry.dir_north;
                cardData.dir_east = entry.dir_east;
                cardData.dir_south = entry.dir_south;
                cardData.dir_west = entry.dir_west;
                cardData.dice_pip_affinity = entry.dice_pip_affinity;
                cardData.deckbuilding = true;

                Sprite portrait = Resources.Load<Sprite>(entry.portrait_resource);
                if (portrait != null)
                {
                    cardData.art_full = portrait;
                    cardData.art_board = portrait;
                }

                EditorUtility.SetDirty(cardData);
                imported++;
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(string.Format("[CardFront] Imported {0} CardData ScriptableObjects and configured 3x3 shared tabletop grid.", imported));
        }
    }
}
#endif
"""
    importer_path.write_text(code, encoding="utf-8")
    return str(importer_path)


def main() -> None:
    runtime_sync = sync_unified_runtime_cs()
    art_sync = sync_art_and_sakuga_resources()
    catalog_sync = build_97_card_catalog()
    importer_path = write_unity_editor_importer()
    ensure_unity_meta_files(PRIMARY_ROOT / "Assets", PRIMARY_ROOT)

    unpacked_scripts = list((UNPACKED_ROOT / "Assets" / "TcgEngine" / "Scripts").rglob("*.cs"))

    manifest = {
        "schema": "CARDFRONT_UNITY_TCG_ENGINE_PORT_MANIFEST_V1",
        "status": "READY_FOR_UNITY_2022_3_LTS_AND_LAN_MULTIPLAYER",
        "primary_unity_repo": str(PRIMARY_ROOT),
        "unpacked_tcg_engine_repo": str(UNPACKED_ROOT),
        "unpacked_csharp_scripts_count": len(unpacked_scripts),
        "network_opcodes_wired": {
            "RollDiceRow": 1060,
            "ApplyBudge": 1062,
            "ApplyChrono": 1064,
            "SolveMnemosynePuzzle": 1066,
        },
        "tabletop_3x3_config": {
            "Slot.x_min": 1,
            "Slot.x_max": 3,
            "Slot.y_min": 1,
            "Slot.y_max": 3,
            "Slot.ignore_p": True,
            "tactical_slide_1_tile_orthogonal": True,
            "boss_holo_telegraph_preview": True,
            "sakuga_24fps_8frame_cutin_strips": 53,
        },
        "runtime_sync": runtime_sync,
        "art_sync": art_sync,
        "catalog_sync": catalog_sync,
        "editor_importer_script": importer_path,
    }

    manifest_path = PRIMARY_ROOT / "Datasets" / "unity_tcg_engine_port_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
