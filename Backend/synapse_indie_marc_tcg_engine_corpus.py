#!/usr/bin/env python3
"""
synapse_indie_marc_tcg_engine_corpus.py — Indie Marc `TCG Engine - Online Card Game`
Longitudinal Corpus Builder & Structural Cataloger (661 -> 721 Records)
====================================================================================
1. Inspects `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/Assets/TcgEngine/Scripts/`
   and `/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/TcgEngineAPI/` to catalog the
   exact subsystems of Indie Marc's `TCG Engine - Online Card Game`:
   - `Data/CardData.cs`, `Data/AbilityData.cs`, `Data/EffectData.cs`, `Data/ConditionData.cs`,
     `Data/FilterData.cs`, `Data/PackData.cs`
   - `GameLogic/Game.cs`, `GameLogic/GameLogic.cs`, `GameLogic/Card.cs`, `GameLogic/Player.cs`, `GameLogic/Slot.cs`
   - `Tools/ResolveQueue.cs`
   - `AI/AIPlayerMM.cs`, `AI/AIHeuristic.cs`
   - `Network/TcgNetwork.cs`, `GameServer/GameServer.cs`, `Api/ApiClient.cs`
   - `TcgEngineAPI/` Node.js + Express + MongoDB routes (`server.js`, `users`, `cards`, `packs`,
     `decks`, `variants`, `matches`, `rewards`, `market`, `activity`).
2. Appends 60 structured `indie_marc_tcg_engine_architecture_spec` records (12 Foundational Masters x
   5 Indie Marc `TCG Engine` Core Pillars) to:
   - `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_9_masters_full_corpus.jsonl`
   - `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl`
   expanding the longitudinal training corpus to 721 total records.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

BACKEND_DIR = Path(__file__).resolve().parent
UNPACKED_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked")
SCRIPTS_ROOT = UNPACKED_ROOT / "Assets" / "TcgEngine" / "Scripts"
API_ROOT = UNPACKED_ROOT / "TcgEngineAPI"

DATASET_FULL_PATH = BACKEND_DIR.parent / "Datasets" / "longitudinal_9_masters_full_corpus.jsonl"
DATASET_12_PATH = BACKEND_DIR.parent / "Datasets" / "longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl"
REPORT_PATH = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/hi3d_rea_workspace/indie_marc_tcg_engine_corpus_report.json")

TARGET_CSHARP_MODULES: List[str] = [
    "Data/CardData.cs",
    "Data/AbilityData.cs",
    "Data/EffectData.cs",
    "Data/ConditionData.cs",
    "Data/FilterData.cs",
    "Data/PackData.cs",
    "GameLogic/Game.cs",
    "GameLogic/GameLogic.cs",
    "GameLogic/Card.cs",
    "GameLogic/Player.cs",
    "GameLogic/Slot.cs",
    "Tools/ResolveQueue.cs",
    "AI/AIPlayerMM.cs",
    "AI/AIHeuristic.cs",
    "Network/TcgNetwork.cs",
    "GameServer/GameServer.cs",
    "Api/ApiClient.cs",
]

INDIE_MARC_TCG_ENGINE_PILLARS: List[Dict[str, Any]] = [
    {
        "pillar_id": "tcg_scriptableobject_card_ability_pipeline",
        "pillar_index": 1,
        "pillar_title": "ScriptableObject CardData & AbilityData Pipeline (Trigger -> ConditionData -> FilterData -> EffectData -> ChainAbilities)",
        "source_scripts": [
            "Data/CardData.cs",
            "Data/AbilityData.cs",
            "Data/EffectData.cs",
            "Data/ConditionData.cs",
            "Data/FilterData.cs",
        ],
        "architecture_formula": (
            "Indie Marc's data-driven ScriptableObject authoring separates static asset definitions (`CardData`, `AbilityData`, "
            "`TraitData`, `StatusData`) from mutable runtime state (`Card`, `Player`, `Game`). Every `AbilityData` executes a "
            "5-stage deterministic pipeline: (1) `AbilityTrigger` event dispatch (`OnPlay`, `StartOfTurn`, `OnBeforeAttack`, `OnAfterAttack`, "
            "`OnDeath`, `Ongoing`), (2) `ConditionData[] conditions_trigger` & `conditions_target` (`IsTriggerConditionMet` / `IsTargetConditionMet` "
            "with `CompareInt` and `CompareBool`), (3) `FilterData[] filters_target` (`FilterTargets` narrowing candidate `ListSwap<Card/Player/Slot>`), "
            "(4) `EffectData[] effects` + `StatusData[] status` (`DoEffect` / `DoOngoingEffect` mutating server-authoritative `Game`), and "
            "(5) `AbilityData[] chain_abilities` enqueued onto `ResolveQueue` for multi-stage tactical cascades. In SYNAPSE / Project CF, this "
            "pipeline is fused with 12-Master illustration & shader vectors and Dicevaders 4-die pip-column triggers (`Budge` ±1 & `Chrono` reroll)."
        ),
        "synapse_integration_spec": {
            "card_types": ["Hero", "Character", "Spell", "Artifact", "Secret", "Equipment"],
            "ability_pipeline_stages": [
                "AbilityTrigger",
                "ConditionData (conditions_trigger + conditions_target)",
                "FilterData (filters_target)",
                "EffectData (DoEffect / DoOngoingEffect) + StatusData",
                "AbilityData[] chain_abilities",
            ],
            "dicevaders_column_fusion": "Slot(x=1..3, y=1..3, p=0..1) 3x3 grid + 4-die pip row triggering column/row ChainAbilities on Pair/Triple/Quadruple resonance",
        },
    },
    {
        "pillar_id": "tcg_netcode_authoritative_server_resolvequeue",
        "pillar_index": 2,
        "pillar_title": "Unity Netcode Authoritative GameServer & ResolveQueue Deterministic Pooling (Instant AI Mode vs. Spring-Physics Client VFX)",
        "source_scripts": [
            "Network/TcgNetwork.cs",
            "GameServer/GameServer.cs",
            "GameLogic/Game.cs",
            "GameLogic/GameLogic.cs",
            "Tools/ResolveQueue.cs",
        ],
        "architecture_formula": (
            "All online and solo matches run through `GameServer` (`registered_commands` mapping `GameAction` codes such as `PlayCard`, "
            "`Attack`, `AttackPlayer`, `Move`, `CastAbility`, `SelectCard`, `SelectSlot`, `EndTurn`) backed by `TcgNetwork` (`NetworkManager` + "
            "`TcgTransport` + `NetworkMessaging` + `ConnectionApprovalCallback`). `ResolveQueue` uses zero-allocation object pools "
            "(`Pool<AbilityQueueElement>`, `Pool<SecretQueueElement>`, `Pool<AttackQueueElement>`, `Pool<CallbackQueueElement>`) with a dual-mode "
            "`skip_delay` flag: when `skip_delay = true` (used by `GameLogic(is_ai: true)` inside Minimax lookahead), all queues drain "
            "synchronously in microseconds with zero GC churn; when `skip_delay = false` (live server/client presentation), `resolve_delay` "
            "paces each step to synchronize with client-side damped spring physics (zeta = 0.42, omega_n = 30.0 rad/s), 55ms tile cascade stagger, "
            "and 48ms hit-stop freezes."
        ),
        "synapse_integration_spec": {
            "network_layer": "Unity.Netcode.NetworkManager + TcgTransport + NetworkMessaging (1MB msg_size buffer)",
            "authoritative_commands": [
                "GameAction.PlayCard",
                "GameAction.Attack",
                "GameAction.AttackPlayer",
                "GameAction.Move",
                "GameAction.CastAbility",
                "GameAction.SelectCard",
                "GameAction.SelectPlayer",
                "GameAction.SelectSlot",
                "GameAction.SelectChoice",
                "GameAction.EndTurn",
            ],
            "resolve_queue_pools": [
                "Pool<AbilityQueueElement>",
                "Pool<SecretQueueElement>",
                "Pool<AttackQueueElement>",
                "Pool<CallbackQueueElement>",
            ],
            "dual_timing_mode": "skip_delay=true for Minimax AI zero-latency tree expansion; skip_delay=false for 55ms cascade & 48ms hit-stop VFX",
        },
    },
    {
        "pillar_id": "tcg_minimax_ai_alpha_beta_dicevaders",
        "pillar_index": 3,
        "pillar_title": "Minimax Alpha-Beta Pruning AI (`AIPlayerMM` & `AIHeuristic`) with State Cloning & Dicevaders Budge/Chrono Lookahead",
        "source_scripts": [
            "AI/AIPlayerMM.cs",
            "AI/AIHeuristic.cs",
            "GameLogic/Card.cs",
            "GameLogic/Player.cs",
            "GameLogic/Slot.cs",
        ],
        "architecture_formula": (
            "Indie Marc's `AIPlayerMM` and `AIHeuristic` evaluate board states in `[-100000, +100000]` using weighted linear evaluation: "
            "`board_card_value = 20`, `secret_card_value = 10`, `hand_card_value = 5`, `kill_value = 5`, `player_hp_value = 4`, "
            "`card_attack_value = 3`, `card_hp_value = 2`, and `card_status_value = 15 * StatusData.hvalue`, plus `±100000 - node.tdepth * 1000` "
            "to reward fastest lethal or longest survival. In SYNAPSE, `AIHeuristic` is extended with a deterministic action-sort order and "
            "branching generator over Dicevaders `Budge` (±1 pip shift) and `Chrono` (targeted die reroll) tokens so the Alpha-Beta search "
            "discovers multi-card directional captures (`N/E/S/W` triad flips) and `Pair`/`Triple`/`Quadruple` dice-row multipliers."
        ),
        "synapse_integration_spec": {
            "heuristic_weights": {
                "board_card_value": 20,
                "secret_card_value": 10,
                "hand_card_value": 5,
                "kill_value": 5,
                "player_hp_value": 4,
                "card_attack_value": 3,
                "card_hp_value": 2,
                "card_status_value": 15,
                "lethal_bonus_base": 100000,
                "depth_penalty_per_ply": 1000,
            },
            "dicevaders_lookahead_extensions": {
                "budge_branching": "Evaluates ±1 pip shifts on active dice before committing PlayCard or CastAbility",
                "chrono_expected_value": "Computes exact 1/6 uniform pip expectation for targeted die rerolls",
                "directional_capture_bonus": "+35 heuristic points per flipped opponent card on the 3x3 Slot grid",
            },
        },
    },
    {
        "pillar_id": "tcg_nodejs_mongodb_web_api_economy",
        "pillar_index": 4,
        "pillar_title": "TcgEngineAPI Node.js + Express + MongoDB Backend (`ApiClient`, `PackData`, JWT Auth, Elo Matches, Market & MiroFish Economy)",
        "source_scripts": [
            "Api/ApiClient.cs",
            "Data/PackData.cs",
            "TcgEngineAPI/server.js",
        ],
        "architecture_formula": (
            "`TcgEngineAPI` provides a complete Node.js + Express + Mongoose persistent metagame backend (`server.js` mounting "
            "`AuthorizationRouter`, `UsersRouter`, `CardsRouter`, `PacksRouter`, `DecksRouter`, `VariantRouter`, `MatchesRouter`, "
            "`RewardsRouter`, `MarketRouter`, and `ActivityRouter`) paired with Unity's `ApiClient` (`PlayerPrefs` JWT `tcg_access_token` / "
            "`tcg_refresh_token` auto-renewal and 5-minute online heartbeat). `PackData` defines `PackType` (`Random` vs `Fixed`), "
            "`PackRarity[] rarities_1st` & `rarities`, and `PackVariant[] variants` probabilities. In SYNAPSE, this persistent economy is "
            "coupled with our MiroFish 4-persona (`Aggro/Control/Combo/Collector`) secondary-market simulation to continuously audit pack EV, "
            "foil variant inflation, and deck-legality balance."
        ),
        "synapse_integration_spec": {
            "nodejs_express_routers": [
                "authorization/auth.routes",
                "users/users.routes",
                "cards/cards.routes",
                "packs/packs.routes",
                "decks/decks.routes",
                "variants/variants.routes",
                "matches/matches.routes",
                "rewards/rewards.routes",
                "market/market.routes",
                "activity/activity.routes",
            ],
            "unity_api_client_features": [
                "JWT access_token + refresh_token auto-refresh",
                "5-minute online presence heartbeat",
                "Server-authoritative deck validation & match reward distribution",
                "PackData probability-weighted rarity & foil variant opening",
            ],
            "mirofish_market_audit": "Continuous 1,000-match simulation regulating card cost, pack EV, and foil liquidity",
        },
    },
    {
        "pillar_id": "tcg_cross_platform_controls_and_hi3d_vfx",
        "pillar_index": 5,
        "pillar_title": "Cross-Platform Desktop/Mobile Controls (`HandCard`, `BoardSlot`, `Budge/Chrono` UI) & Hi3D.ai / TRELLIS 2.0 Watertight 3D Frames",
        "source_scripts": [
            "Data/CardData.cs",
            "GameLogic/Slot.cs",
            "GameLogic/Card.cs",
        ],
        "architecture_formula": (
            "Indie Marc's client presentation layer decouples pure serializable data (`Card`, `Slot`, `Player`, `Game`) from interactive "
            "MonoBehaviours (`HandCard` drag-and-drop/hover zoom, `BoardSlot` raycast targeting, `SelectTargetUI` modal prompts, and "
            "`CardData` `spawn_fx`/`attack_fx`/`damage_fx`/`death_fx` + audio clips). In SYNAPSE, we unify Desktop mouse-hover and Mobile "
            "touch drag-and-drop across the 3x3 `BoardSlot` grid and tactile `Budge`/`Chrono` dice trays, rendering every card inside a "
            "watertight `.glb` / `.q3gs` 3D relief frame synthesized by `Hi3D.ai` + `TRELLIS 2.0` and audited by `morluto/rea` (`rea@6.8.0`)."
        ),
        "synapse_integration_spec": {
            "input_modalities": [
                "Desktop mouse hover preview + bezier targeting arrow",
                "Mobile single-finger drag-and-drop + tap-to-inspect modal",
                "Tactile Budge (±1 pip) and Chrono (reroll) die-tray buttons with spring recoil",
            ],
            "card_fx_hooks": [
                "spawn_fx / spawn_audio",
                "attack_fx / attack_audio",
                "damage_fx / damage_audio",
                "death_fx / death_audio",
                "idle_fx + ability board_fx / caster_fx / target_fx",
            ],
            "hi3d_3d_relief_binding": "CardData.art_full + CardData.art_board bound to watertight .glb/.q3gs 3D card frames with 12-Master custom toon/ink shaders",
        },
    },
]


def inspect_indie_marc_tcg_engine_files() -> Dict[str, Any]:
    """Catalog exact file metadata, classes, methods, and routes from `/tcg-engine-unpacked/`."""
    csharp_catalog: List[Dict[str, Any]] = []
    for rel_path in TARGET_CSHARP_MODULES:
        full_path = SCRIPTS_ROOT / rel_path
        if not full_path.exists():
            continue
        raw = full_path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        classes = re.findall(r"\b(?:class|struct|enum)\s+([A-Za-z0-9_]+)", text)
        methods = re.findall(
            r"\b(?:public|protected|private)\s+(?:virtual\s+|override\s+|static\s+|async\s+)*[A-Za-z0-9_<>\[\],\s]+\s+([A-Za-z0-9_]+)\s*\(",
            text,
        )
        csharp_catalog.append({
            "relative_path": f"Assets/TcgEngine/Scripts/{rel_path}",
            "bytes": len(raw),
            "lines": len(lines),
            "sha256": hashlib.sha256(raw).hexdigest()[:16],
            "types_defined": list(dict.fromkeys(classes))[:12],
            "methods_sampled": list(dict.fromkeys(methods))[:15],
        })

    # Inspect TcgEngineAPI Node.js / MongoDB files
    api_catalog: List[Dict[str, Any]] = []
    if API_ROOT.exists():
        for js_path in sorted(API_ROOT.rglob("*.js")):
            raw = js_path.read_bytes()
            text = raw.decode("utf-8", errors="replace")
            rel = str(js_path.relative_to(UNPACKED_ROOT))
            routes = re.findall(r"app\.(?:get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]", text)
            api_catalog.append({
                "relative_path": rel,
                "bytes": len(raw),
                "lines": len(text.splitlines()),
                "sha256": hashlib.sha256(raw).hexdigest()[:16],
                "express_routes": routes,
            })

    return {
        "unpacked_root": str(UNPACKED_ROOT),
        "csharp_subsystems_count": len(csharp_catalog),
        "csharp_subsystems": csharp_catalog,
        "nodejs_api_files_count": len(api_catalog),
        "nodejs_api_files": api_catalog,
    }


def append_60_indie_marc_tcg_records(catalog: Dict[str, Any]) -> Dict[str, Any]:
    """Append 60 structured `indie_marc_tcg_engine_architecture_spec` records (12 Masters x 5 Pillars) -> 721 records."""
    from build_longitudinal_artist_dataset import LONGITUDINAL_MASTERS_SPEC

    source_path = DATASET_FULL_PATH if DATASET_FULL_PATH.exists() else DATASET_12_PATH
    existing_records: List[Dict[str, Any]] = []
    if source_path.exists():
        for line in source_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_records.append(json.loads(line))

    # Deduplicate any prior `indie_marc_tcg_engine_architecture_spec` entries so repeated runs stay at 721
    base_records = [
        r for r in existing_records
        if r.get("record_type") != "indie_marc_tcg_engine_architecture_spec"
    ]

    cs_by_rel = {
        item["relative_path"].replace("Assets/TcgEngine/Scripts/", ""): item
        for item in catalog.get("csharp_subsystems", [])
    }
    api_routes_flat: List[str] = []
    for api_item in catalog.get("nodejs_api_files", []):
        for rt in api_item.get("express_routes", []):
            if rt not in api_routes_flat:
                api_routes_flat.append(rt)

    new_records: List[Dict[str, Any]] = []
    for master in LONGITUDINAL_MASTERS_SPEC:
        latest_era = master["eras"][-1]
        for pillar in INDIE_MARC_TCG_ENGINE_PILLARS:
            verified_modules = [
                cs_by_rel[s] for s in pillar["source_scripts"] if s in cs_by_rel
            ]
            new_records.append({
                "record_type": "indie_marc_tcg_engine_architecture_spec",
                "reference_engine": "Indie Marc TCG Engine - Online Card Game (Unity Netcode + ScriptableObjects + Minimax AI + Node.js/MongoDB API)",
                "master_id": master["master_id"],
                "artist_name": master["artist_name"],
                "kanji": master["kanji"],
                "pillar_id": pillar["pillar_id"],
                "pillar_index": pillar["pillar_index"],
                "pillar_title": pillar["pillar_title"],
                "shader_vector": latest_era["shader_vector"],
                "verified_source_modules": verified_modules,
                "verified_nodejs_routes_sample": api_routes_flat[:16],
                "instruction": (
                    f"Architect and implement `{pillar['pillar_title']}` from Indie Marc's **TCG Engine - Online Card Game** "
                    f"for `SYNAPSE / Project CF`, uniting Unity Netcode server authority, `ResolveQueue` pooling, `AIPlayerMM` "
                    f"Minimax lookahead, and *Dicevaders* (`3917700`) `Budge`/`Chrono` dice tactics with the signature visual "
                    f"direction and shader parameters of {master['artist_name']} ({master['kanji']})."
                ),
                "response": json.dumps({
                    "artist_style": master["artist_name"],
                    "era_reference": latest_era["era"],
                    "tcg_engine_pillar": pillar["pillar_title"],
                    "architecture_formula": pillar["architecture_formula"],
                    "synapse_integration_spec": pillar["synapse_integration_spec"],
                    "verified_csharp_modules": [
                        {
                            "path": m["relative_path"],
                            "lines": m["lines"],
                            "sha256": m["sha256"],
                            "types": m["types_defined"],
                        }
                        for m in verified_modules
                    ],
                    "shader_vector": latest_era["shader_vector"],
                }, ensure_ascii=False),
            })

    all_records = base_records + new_records
    for target_path in (DATASET_FULL_PATH, DATASET_12_PATH):
        with target_path.open("w", encoding="utf-8") as f:
            for r in all_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return {
        "previous_corpus_records": len(base_records),
        "new_indie_marc_tcg_records_appended": len(new_records),
        "total_corpus_records": len(all_records),
        "dataset_paths": [str(DATASET_FULL_PATH), str(DATASET_12_PATH)],
    }


def main() -> Dict[str, Any]:
    t0 = time.perf_counter()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    catalog = inspect_indie_marc_tcg_engine_files()
    corpus_info = append_60_indie_marc_tcg_records(catalog)
    report = {
        "status": "ok",
        "engine_reference": "Indie Marc TCG Engine - Online Card Game",
        "catalog_summary": {
            "csharp_subsystems_count": catalog["csharp_subsystems_count"],
            "nodejs_api_files_count": catalog["nodejs_api_files_count"],
        },
        "corpus_expansion": corpus_info,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = main()
    print(json.dumps(rep, indent=2, ensure_ascii=False))
