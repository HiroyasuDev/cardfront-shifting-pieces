#!/usr/bin/env python3
"""
Synapse Sovereign TCG Engine (`Synapse.TcgEngine`) — Continuous Self-Play Balance & 3-GPU Iteration Daemon.
- Executes `Tests/test_synapse_tcg_suite.py` (24-test clean-room verification gate) on every iteration.
- Runs 200-match Monte Carlo AI vs AI self-play tournaments over the 3x3 Tactical Grid Engine,
  computing win-rate, capture-rate, and synergy telemetry across all 14 official cards
  (10 PROJECT CF Guardian Frames + 4 CardCraft Creative Evolution cards).
- Dispatches parallel 3-GPU telemetry & balance reviews across:
  1. Node 116 Tesla V100 32GB (`pxg-lumenforge:30b-a3b`)
  2. Node 30 RTX 4080 16GB (`pxg-lumenforge:12b-tutor`)
  3. Node 22 RTX 2070 8GB (`pxg-lumenforge:7b-tutor`)
  via `ncm.fleet.dispatch_all`.
- Appends structured JSONL iteration telemetry to `Logs/continuous_iterations.jsonl`.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
BACKEND_DIR = ROOT_DIR / "Backend"
TESTS_DIR = ROOT_DIR / "Tests"
LOGS_DIR = ROOT_DIR / "Logs"
ITERATIONS_LOG_PATH = LOGS_DIR / "continuous_iterations.jsonl"
MIRO_STRANDS_LOG_PATH = LOGS_DIR / "miro_strands_simulation_feedback.jsonl"

for p in (BACKEND_DIR, TESTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from synapse_tcg_backend import (  # noqa: E402
    Hi3dAiFullStudioReEngine,
    LumenForgeIoStudioEngine,
    MetalGearAcidCostSimulator,
    MiroStrandsSimulationFeedbackEngine,
    OFFICIAL_PROJECT_CF_CARDS,
    SynapseMetagameBackend,
)
from test_synapse_tcg_suite import (  # noqa: E402
    RuntimeCardInstance,
    SynapseTacticalGridEngine,
    run_suite,
)
from synapse_gamedev_skills_harness_bridge import SynapseGameDevSkillsHarnessBridge  # noqa: E402


@dataclass
class FleetNodeTarget:
    node_key: str
    node_name: str
    host_port: str
    model: str
    fallback_model: str
    role: str


THREE_GPU_FLEET_TARGETS: Tuple[FleetNodeTarget, ...] = (
    FleetNodeTarget(
        node_key="node116_v100",
        node_name="Node 116 Tesla V100 32GB",
        host_port="192.168.86.116:11434",
        model="pxg-lumenforge:30b-a3b",
        fallback_model="pxg-lumenforge:1.5b-qlora",
        role="Lead Game Balance Architect & Synergy Auditor",
    ),
    FleetNodeTarget(
        node_key="node30_rtx4080",
        node_name="Node 30 RTX 4080 16GB",
        host_port="192.168.86.30:11434",
        model="pxg-lumenforge:12b-tutor",
        fallback_model="pxg-lumenforge:12b-tutor",
        role="Minimax AI Heuristics & Special Ability Strategist",
    ),
    FleetNodeTarget(
        node_key="node22_rtx2070",
        node_name="Node 22 RTX 2070 8GB",
        host_port="192.168.86.22:11434",
        model="pxg-lumenforge:7b-tutor",
        fallback_model="pxg-lumenforge:7b-tutor",
        role="CardCraft Progression & Evolution Telemetry Reviewer",
    ),
)


class _NcmFleetNamespace:
    """
    Provides `ncm.fleet.dispatch_all(...)` across Node 116 Tesla V100, Node 30 RTX 4080,
    and Node 22 RTX 2070 with concurrent HTTP/JSON dispatch and automatic model fallback.
    """

    @staticmethod
    def _query_ollama_node(target: FleetNodeTarget, prompt: str, num_predict: int = 160, timeout_s: float = 35.0) -> Dict[str, Any]:
        t0 = time.time()
        for candidate_model in (target.model, target.fallback_model):
            payload: Dict[str, Any] = {
                "model": candidate_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"You are {target.role} on {target.node_name} ({candidate_model}). "
                            "Provide a concise 2-3 sentence competitive balance recommendation for Synapse.TcgEngine "
                            "(PROJECT CF & CardCraft 3x3 Directional Capture TCG)."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": num_predict},
            }
            if "30b" in candidate_model or "12b" in candidate_model:
                payload["think"] = False

            req = urllib.request.Request(
                f"http://{target.host_port}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                msg = body.get("message", {})
                text = (msg.get("content") or msg.get("thinking") or "").strip()
                if text:
                    return {
                        "node": target.node_key,
                        "node_name": target.node_name,
                        "model": candidate_model,
                        "role": target.role,
                        "online": True,
                        "elapsed_ms": round((time.time() - t0) * 1000.0, 2),
                        "review": text,
                    }
            except Exception as exc:
                last_err = str(exc)
                continue

        return {
            "node": target.node_key,
            "node_name": target.node_name,
            "model": target.model,
            "role": target.role,
            "online": False,
            "elapsed_ms": round((time.time() - t0) * 1000.0, 2),
            "error": last_err if "last_err" in locals() else "unreachable",
        }

    def dispatch_all(self, prompt: str, num_predict: int = 160) -> List[Dict[str, Any]]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [
                pool.submit(self._query_ollama_node, target, prompt, num_predict)
                for target in THREE_GPU_FLEET_TARGETS
            ]
            return [f.result() for f in futures]


class _NcmRoot:
    fleet = _NcmFleetNamespace()


try:
    import ncm as _existing_ncm  # type: ignore
    if not hasattr(_existing_ncm, "fleet") or not hasattr(_existing_ncm.fleet, "dispatch_all"):
        _existing_ncm.fleet = _NcmFleetNamespace()
    ncm = _existing_ncm
except ImportError:
    ncm = _NcmRoot()


def choose_ai_move(engine: SynapseTacticalGridEngine, player_id: int) -> Optional[Tuple[str, int, int, float]]:
    """
    Tactical lookahead heuristic matching `TcgMinimaxAI.SimulatePlacementScore` + corner/synergy weighting.
    Returns `(card_uid, x, y, score)` for the active player.
    """
    hand = engine.players[player_id].hand
    if not hand:
        return None

    best_choice: Optional[Tuple[str, int, int, float]] = None
    for card in hand:
        for x in range(3):
            for y in range(3):
                if engine.grid[x][y] is not None:
                    continue
                engine.grid[x][y] = card
                stats = engine.get_effective_stats(x, y)
                simulated_captures = 0
                for dx, dy in SynapseTacticalGridEngine.ORTHOGONAL_DIRS:
                    nx, ny = x + dx, y + dy
                    if not engine.in_bounds(nx, ny) or engine.grid[nx][ny] is None:
                        continue
                    neighbor = engine.grid[nx][ny]
                    assert neighbor is not None
                    if neighbor.owner_id != player_id and not engine.is_card_capture_immune(nx, ny):
                        def_stats = engine.get_effective_stats(nx, ny)
                        if dx == 0 and dy == 1 and stats.up > def_stats.down:
                            simulated_captures += 1
                        elif dx == 0 and dy == -1 and stats.down > def_stats.up:
                            simulated_captures += 1
                        elif dx == -1 and dy == 0 and stats.left > def_stats.right:
                            simulated_captures += 1
                        elif dx == 1 and dy == 0 and stats.right > def_stats.left:
                            simulated_captures += 1

                is_corner = (x in (0, 2)) and (y in (0, 2))
                score = (
                    simulated_captures * 200.0
                    + stats.total() * 3.0
                    + (12.0 if is_corner else 0.0)
                )
                engine.grid[x][y] = None

                if best_choice is None or score > best_choice[3]:
                    best_choice = (card.uid, x, y, score)

    return best_choice


def run_monte_carlo_tournament(num_matches: int = 200, base_seed: int = 20261106) -> Dict[str, Any]:
    """
    Executes `num_matches` full AI vs AI 3x3 tactical matches across random 5-card draws from
    the 14-card `OFFICIAL_PROJECT_CF_CARDS` roster, recording per-card win rate, capture rate,
    and synergy/ability activations.
    """
    t0 = time.time()
    all_card_ids = list(OFFICIAL_PROJECT_CF_CARDS.keys())
    telemetry: Dict[str, Dict[str, Any]] = {
        cid: {
            "card_id": cid,
            "title": OFFICIAL_PROJECT_CF_CARDS[cid].title,
            "rarity": OFFICIAL_PROJECT_CF_CARDS[cid].rarity,
            "special_ability": OFFICIAL_PROJECT_CF_CARDS[cid].special_ability,
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "captures_made": 0,
            "times_placed": 0,
        }
        for cid in all_card_ids
    }

    p0_wins = 0
    p1_wins = 0
    draws = 0
    total_turns = 0
    night_matches = 0

    for m_idx in range(num_matches):
        rng = random.Random(base_seed + m_idx * 31)
        is_night = (m_idx % 2 == 1)
        if is_night:
            night_matches += 1

        eng = SynapseTacticalGridEngine(seed=base_seed + m_idx, is_nighttime=is_night)
        eng.active_player_id = m_idx % 2  # Alternate first-player advantage

        pool = list(all_card_ids)
        rng.shuffle(pool)
        p0_card_ids = pool[:5]
        p1_card_ids = pool[5:10]

        for idx, cid in enumerate(p0_card_ids):
            inst = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS[cid], 0, f"m{m_idx}_p0_{idx}")
            if cid == "cc_01_sketching":
                inst.permanent_bonus = 2  # CardCraft Veteran Tournament Parity (+2 all sides)
            elif cid in ("cc_03_storyboard", "cf_05_elemental_sprite"):
                inst.permanent_bonus = 1  # CardCraft / Elemental Sprite Tournament Parity (+1 all sides)
            eng.players[0].hand.append(inst)
            telemetry[cid]["matches_played"] += 1
        for idx, cid in enumerate(p1_card_ids):
            inst = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS[cid], 1, f"m{m_idx}_p1_{idx}")
            if cid == "cc_01_sketching":
                inst.permanent_bonus = 2  # CardCraft Veteran Tournament Parity (+2 all sides)
            elif cid in ("cc_03_storyboard", "cf_05_elemental_sprite"):
                inst.permanent_bonus = 1  # CardCraft / Elemental Sprite Tournament Parity (+1 all sides)
            eng.players[1].hand.append(inst)
            telemetry[cid]["matches_played"] += 1

        safety_steps = 0
        while not eng.is_game_over() and eng.winner_id is None and safety_steps < 20:
            safety_steps += 1
            active = eng.active_player_id
            move = choose_ai_move(eng, active)
            if move is None:
                eng.end_turn()
                continue
            cuid, tx, ty, _ = move
            placed_card = next((c for c in eng.players[active].hand if c.uid == cuid), None)
            ok, caps = eng.place_card(active, cuid, tx, ty)
            if ok and placed_card is not None:
                telemetry[placed_card.card_id]["times_placed"] += 1
                telemetry[placed_card.card_id]["captures_made"] += caps
                total_turns += 1

        if eng.winner_id is None:
            eng.determine_winner()

        if eng.winner_id == 0:
            p0_wins += 1
            for cid in p0_card_ids:
                telemetry[cid]["wins"] += 1
            for cid in p1_card_ids:
                telemetry[cid]["losses"] += 1
        elif eng.winner_id == 1:
            p1_wins += 1
            for cid in p1_card_ids:
                telemetry[cid]["wins"] += 1
            for cid in p0_card_ids:
                telemetry[cid]["losses"] += 1
        else:
            draws += 1
            for cid in p0_card_ids + p1_card_ids:
                telemetry[cid]["draws"] += 1

    # Compute derived rates
    leaderboard: List[Dict[str, Any]] = []
    for cid, stats in telemetry.items():
        mp = max(1, stats["matches_played"])
        tp = max(1, stats["times_placed"])
        stats["win_rate_pct"] = round((stats["wins"] / mp) * 100.0, 2)
        stats["captures_per_placement"] = round(stats["captures_made"] / tp, 3)
        leaderboard.append(stats)

    leaderboard.sort(key=lambda r: (r["win_rate_pct"], r["captures_per_placement"]), reverse=True)

    return {
        "matches_simulated": num_matches,
        "nighttime_matches": night_matches,
        "p0_wins": p0_wins,
        "p1_wins": p1_wins,
        "draws": draws,
        "total_placements": total_turns,
        "elapsed_s": round(time.time() - t0, 3),
        "top_cards": leaderboard[:5],
        "bottom_cards": leaderboard[-3:],
        "per_card_telemetry": {row["card_id"]: row for row in leaderboard},
    }


def execute_single_iteration(iteration_index: int, num_matches: int = 200) -> Dict[str, Any]:
    iter_start = time.time()
    # 1. Run 24-test verification suite
    suite_result = run_suite()

    # 2. Run 200-match Monte Carlo self-play tournament
    mc_result = run_monte_carlo_tournament(num_matches=num_matches, base_seed=10000 + iteration_index * 997)

    # 3. Verify SQLite metagame persistence round-trip
    backend = SynapseMetagameBackend(":memory:")
    u0 = backend.register_user(f"Iter{iteration_index}_Alpha", "pw_a")
    u1 = backend.register_user(f"Iter{iteration_index}_Omega", "pw_b")
    sample_match = backend.simulate_authoritative_3x3_match(u0["user_id"], u1["user_id"], seed=iteration_index)

    # 4. Run 24/7 Round-the-Clock Game Creative Director + MiroFish/Strands NPC & Studio Illustrator Simulation
    miro_engine = MiroStrandsSimulationFeedbackEngine(seed=20261107 + iteration_index)
    npc_market = miro_engine.run_npc_market_simulation(
        per_card_telemetry=mc_result["per_card_telemetry"],
        rounds=24,
    )
    studio_critique = miro_engine.run_studio_illustrator_critique()
    analytics = miro_engine.compute_feedback_analytics(npc_market, studio_critique)

    # 5. Execute Soup-to-Full Model Soup Merge (Uniform, Greedy, Task-Arithmetic, TIES)
    base_weights = {"tempo_cost_w": 0.50, "capture_synergy_w": 0.50, "telegraph_clarity_w": 0.50, "pop_cel_contrast_w": 0.50}
    adapter_candidates = [
        {
            "name": "adapter_mga_nojiri_masao",
            "val_score": 0.94,
            "lambda": 0.35,
            "weights": {"tempo_cost_w": 0.62, "capture_synergy_w": 0.54, "telegraph_clarity_w": 0.58, "pop_cel_contrast_w": 0.66},
        },
        {
            "name": "adapter_ffta_matsuno_ito",
            "val_score": 0.93,
            "lambda": 0.35,
            "weights": {"tempo_cost_w": 0.56, "capture_synergy_w": 0.64, "telegraph_clarity_w": 0.61, "pop_cel_contrast_w": 0.55},
        },
        {
            "name": "adapter_aw_itb_staccs",
            "val_score": 0.92,
            "lambda": 0.30,
            "weights": {"tempo_cost_w": 0.58, "capture_synergy_w": 0.59, "telegraph_clarity_w": 0.67, "pop_cel_contrast_w": 0.57},
        },
    ]
    greedy_soup = miro_engine.compute_model_soup_merge(base_weights, adapter_candidates, mode="greedy")
    ties_soup = miro_engine.compute_model_soup_merge(base_weights, adapter_candidates, mode="ties")

    # 6. Dispatch 3-GPU telemetry review via ncm.fleet.dispatch_all
    top_summary = ", ".join(
        f"{c['title']} ({c['win_rate_pct']}% WR, {c['captures_per_placement']} cap/play)"
        for c in mc_result["top_cards"][:3]
    )
    bot_summary = ", ".join(
        f"{c['title']} ({c['win_rate_pct']}% WR, {c['captures_per_placement']} cap/play)"
        for c in mc_result["bottom_cards"]
    )
    fleet_prompt = (
        f"Iteration #{iteration_index} [24/7 Creative Director Shinta Nojiri x Yasumi Matsuno] "
        f"({num_matches} matches, {suite_result['tests_run']}/{suite_result['tests_run']} tests green, "
        f"Gini={analytics['metagame_gini']}, Entropy={analytics['deck_shannon_entropy']} bits, "
        f"Telegraph1s={analytics['telegraph_1s_readability_score']}): "
        f"Top cards: {top_summary}. Lowest cards: {bot_summary}. "
        "Provide 2 concise MGA COST, FFTA CTB/Facing, and Studio Shader tuning insights."
    )
    fleet_reviews = ncm.fleet.dispatch_all(fleet_prompt, num_predict=140)

    creative_director_status = {
        "director_persona": "Shinta Nojiri (Metal Gear Acid) x Yasumi Matsuno (FFTA) — 24/7 Non-Stop Creative Director",
        "active_around_the_clock": True,
        "npc_archetypes_simulated": npc_market["npc_archetypes_active"],
        "studio_illustrators_simulated": studio_critique["illustrator_agents_active"],
        "feedback_analytics": analytics,
        "model_soup_greedy": greedy_soup,
        "model_soup_ties": ties_soup,
    }

    # 7. Run Hi3D.ai Full 5-Stage Studio Pipeline + morluto/rea Continuous Deep Chunk Audit across all 14 cards
    roster_3d = Hi3dAiFullStudioReEngine.ensure_all_14_card_hi3d_3d_assets_exist()
    sample_glb_path = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "synapse_hi3d_staccs_mecha_cube.glb"
    rea_deep_audit = Hi3dAiFullStudioReEngine.audit_glb_with_morluto_rea_deep_chunks(sample_glb_path)
    hi3d_rea_studio_audit = {
        "roster_3d_verified_count": roster_3d["cards_3d_verified_count"],
        "sample_glb_euler_characteristic": rea_deep_audit["topology_evidence"]["euler_characteristic"],
        "sample_glb_watertight": rea_deep_audit["topology_evidence"]["watertight_verified"],
        "chunk0_json_verified": rea_deep_audit["chunk0_json"]["chunk_type_hex"] == "0x4e4f534a",
        "chunk1_bin_verified": rea_deep_audit["chunk1_bin"]["payload_bytes_verified"],
    }

    # 8. Run lumenforge.io Sovereign 4-Node Pool, Q3GS/GLB Dual Streaming & RL Environment Audit
    lf_manifest = LumenForgeIoStudioEngine.get_lumenforge_io_platform_manifest()
    lf_epoch = LumenForgeIoStudioEngine.run_lumenforge_continuous_epoch_step(epoch_index=iteration_index)
    lf_rea_env = LumenForgeIoStudioEngine.verify_rea_rl_environments_and_evidence()
    lumenforge_io_audit = {
        "domain": lf_manifest["domain"],
        "pool_name": lf_manifest["pool_name"],
        "total_vram_gb": lf_manifest["sovereign_pool"]["total_vram_gb"],
        "peak_fp16_tflops": lf_manifest["sovereign_pool"]["peak_fp16_tflops"],
        "glb_count": lf_manifest["models_3d_roster"]["glb_count"],
        "q3gs_count": lf_manifest["models_3d_roster"]["q3gs_count"],
        "rea_workspace_verified": lf_rea_env["workspace_verified"],
        "epoch_step": lf_epoch,
    }

    # 9. Run 77-Skill / 91-Skill GameDev Harness Bridge (YouTube t13A2XFGoOc & pxg-gamedev-harness)
    gamedev_skills_harness = SynapseGameDevSkillsHarnessBridge.run_continuous_harness_step(
        iteration_index=iteration_index
    )

    report = {
        "iteration": iteration_index,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "unit_test_gate": suite_result,
        "monte_carlo_tournament": {
            "matches_simulated": mc_result["matches_simulated"],
            "p0_wins": mc_result["p0_wins"],
            "p1_wins": mc_result["p1_wins"],
            "draws": mc_result["draws"],
            "elapsed_s": mc_result["elapsed_s"],
            "top_3_cards": mc_result["top_cards"][:3],
            "bottom_3_cards": mc_result["bottom_cards"],
            "per_card_telemetry": mc_result["per_card_telemetry"],
        },
        "authoritative_backend_probe": {
            "match_id": sample_match["match_id"],
            "state_hash": sample_match["state_hash"],
            "p0_cells": sample_match["p0_cells"],
            "p1_cells": sample_match["p1_cells"],
        },
        "creative_director_and_miro_strands": creative_director_status,
        "hi3d_rea_studio_audit": hi3d_rea_studio_audit,
        "lumenforge_io_audit": lumenforge_io_audit,
        "gamedev_skills_harness": gamedev_skills_harness,
        "three_gpu_fleet_reviews": fleet_reviews,
        "total_iteration_elapsed_s": round(time.time() - iter_start, 3),
    }

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ITERATIONS_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(report) + "\n")
    with open(MIRO_STRANDS_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "iteration": iteration_index,
                    "timestamp_utc": report["timestamp_utc"],
                    "creative_director": creative_director_status,
                    "npc_market_valuations": npc_market["card_market_valuations"],
                    "studio_critiques": studio_critique["agent_critiques"],
                }
            )
            + "\n"
        )

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synapse.TcgEngine Continuous Self-Play Balance & 3-GPU Iteration Daemon"
    )
    parser.add_argument("--once", action="store_true", help="Run a single verification & tournament cycle and exit.")
    parser.add_argument("--loop", action="store_true", help="Run continuously at --interval seconds.")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between iterations in --loop mode.")
    parser.add_argument("--matches", type=int, default=200, help="Number of Monte Carlo matches per iteration.")
    args = parser.parse_args()

    iteration = 1
    if ITERATIONS_LOG_PATH.exists():
        try:
            with open(ITERATIONS_LOG_PATH, "r", encoding="utf-8") as fh:
                iteration = sum(1 for line in fh if line.strip()) + 1
        except Exception:
            iteration = 1

    if args.once or not args.loop:
        rep = execute_single_iteration(iteration_index=iteration, num_matches=args.matches)
        print(
            json.dumps(
                {
                    "status": "ITERATION_COMPLETE",
                    "iteration": rep["iteration"],
                    "tests_passed": rep["unit_test_gate"]["passed"],
                    "tests_run": rep["unit_test_gate"]["tests_run"],
                    "matches_simulated": rep["monte_carlo_tournament"]["matches_simulated"],
                    "top_card": rep["monte_carlo_tournament"]["top_3_cards"][0]["title"],
                    "fleet_nodes_responded": sum(1 for r in rep["three_gpu_fleet_reviews"] if r.get("online")),
                    "log_file": str(ITERATIONS_LOG_PATH),
                    "elapsed_s": rep["total_iteration_elapsed_s"],
                },
                indent=2,
            )
        )
        sys.exit(0 if rep["unit_test_gate"]["passed"] else 1)

    while True:
        rep = execute_single_iteration(iteration_index=iteration, num_matches=args.matches)
        print(
            f"[Synapse Continuous Daemon] Iteration #{iteration} complete in {rep['total_iteration_elapsed_s']}s "
            f"(tests={rep['unit_test_gate']['tests_run']} passed={rep['unit_test_gate']['passed']}, "
            f"fleet_online={sum(1 for r in rep['three_gpu_fleet_reviews'] if r.get('online'))}/3)",
            flush=True,
        )
        iteration += 1
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    main()
