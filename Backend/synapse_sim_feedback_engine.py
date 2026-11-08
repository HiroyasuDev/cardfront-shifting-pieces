#!/usr/bin/env python3
"""
synapse_sim_feedback_engine.py — Sovereign MiroFish × Strands-Agents Simulation Feedback
& 12-Master Illustration Engine
========================================================================================
Combines the three pillars of an open-source AI-powered simulation feedback & illustration tool:
  1. Multi-Agent Simulation Core (MiroFish / OASIS-style Agent-Based Market, Playtest & Aesthetic Simulation):
     - Runs a 1,000-match Monte Carlo 3x3 tactical playtest & market order-book micro-simulation
       paired with 4 heterogeneous LLM Persona Agents across our 4-Node 120 GB GPU Pool.
  2. Strands-Agents Model-Driven LLM Workflow Layer (4-Node Parallel Pool Execution):
     - `meta_tactician`        -> Node 116 V100 32GB (`192.168.86.116:11434` — `pxg-lumenforge:1.5b-qlora`)
     - `master_art_director`   -> Node 30 RTX 4080 16GB (`192.168.86.30:11434` — `pxg-lumenforge:12b-tutor`)
     - `onboarding_ux_critic`  -> Node 127 M1 Max 64GB (`192.168.86.127:11434` — `pxg-lumenforge:7b-tutor`)
     - `mirofish_economist`    -> Node 22 RTX 2070 8GB (`192.168.86.22:11434` — `pxg-lumenforge:7b-tutor`)
  3. Feedback Analytics & Closed-Loop Illustration / Epoch Refinement Pipeline:
     - Synthesizes multi-master style blends across all 12 Foundational Character, Mecha, Occult & Environmental Masters,
     - Renders live illustrations via Node 30 RTX 4080 ComfyUI (`192.168.86.30:8188`),
     - Computes quantitative feedback analytics (Win-Rate Equilibrium, Collector Virality Index, Silhouette Readability,
       and Auto-Calibrated Shader Vector Deltas),
     - Feeds the winning feedback trajectory into V100 Multi-Epoch QLoRA + Hinton KD training (`192.168.86.116:8090/v1/train/refine`).
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import hmac
import json
import math
import random
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

FORGE_API_URL = "http://192.168.86.116:8090"
SIM_REPORT_PATH = BACKEND_DIR.parent / "Datasets" / "latest_mirofish_strands_sim_report.json"
SIM_LEDGER_PATH = BACKEND_DIR.parent / "Datasets" / "mirofish_strands_feedback_ledger.jsonl"

# 12 Foundational Character, Mecha, Occult & Environmental Masters
MASTER_SHADER_PROFILES: Dict[str, Dict[str, Any]] = {
    "ryoma_ito": {
        "name": "Ryōma Itō (FFTA / FFTA2 / Revenant Wings)",
        "domain": "Character & Job Silhouette",
        "shader": {"outline": 1.30, "crosshatch": 0.22, "bloom": 0.50, "saturation": 1.22, "bevel": 0.40},
    },
    "akihiko_yoshida": {
        "name": "Akihiko Yoshida (FFT / Tactics Ogre / FFTA Judges / NieR)",
        "domain": "Character Supervision & Baroque Judge Filigree",
        "shader": {"outline": 1.40, "crosshatch": 0.85, "bloom": 0.25, "saturation": 0.88, "bevel": 0.55},
    },
    "hideo_minaba": {
        "name": "Hideo Minaba (FFTA Art Director / FFIX / Granblue)",
        "domain": "Storybook World & Sky-Citadel Art Direction",
        "shader": {"outline": 1.10, "crosshatch": 0.40, "bloom": 0.85, "saturation": 1.16, "bevel": 0.45},
    },
    "ryo_hirata": {
        "name": "Ryo Hirata (Advance Wars 1/2/Dual Strike/Days of Ruin & Fire Emblem GBA)",
        "domain": "Commanding Officer & Tactical Unit Readability",
        "shader": {"outline": 1.65, "crosshatch": 0.10, "bloom": 0.20, "saturation": 1.28, "bevel": 0.65},
    },
    "toru_nakayama": {
        "name": "Toru Nakayama (Mega Man Zero 1-4 / ZX / Dragon Marked for Death)",
        "domain": "Cyber-Fantasy Beveled Armor & Expressive Reploid Design",
        "shader": {"outline": 1.55, "crosshatch": 0.15, "bloom": 0.60, "saturation": 1.24, "bevel": 0.95},
    },
    "hiroshi_minagawa": {
        "name": "Hiroshi Minagawa & Ivalice Diorama Team (FFT / Tactics Ogre / Vagrant Story)",
        "domain": "Isometric Terraced Battlefield Dioramas",
        "shader": {"outline": 1.30, "crosshatch": 0.68, "bloom": 0.38, "saturation": 0.95, "bevel": 0.62},
    },
    "isamu_kamikokuryo": {
        "name": "Isamu Kamikokuryo (FFXII Ivalice Architecture & Skystone Airships)",
        "domain": "Monumental Limestone Citadels & Airship Architecture",
        "shader": {"outline": 1.08, "crosshatch": 0.38, "bloom": 0.70, "saturation": 1.14, "bevel": 0.75},
    },
    "hiroo_isono": {
        "name": "Hiroo Isono & Kouichi Ishii (Secret of Mana / Heroes of Mana)",
        "domain": "Botanical World-Tree Sanctuaries & Storybook Biomes",
        "shader": {"outline": 1.10, "crosshatch": 0.28, "bloom": 0.82, "saturation": 1.26, "bevel": 0.38},
    },
    "inti_creates_env": {
        "name": "Makoto Yabe & Inti Creates Environment Team (Neo Arcadia & Cyber Ruins)",
        "domain": "High-Contrast Cyber-Cathedrals & Reploid Ruins",
        "shader": {"outline": 1.50, "crosshatch": 0.15, "bloom": 0.65, "saturation": 1.22, "bevel": 0.92},
    },
    "yoji_shinkawa": {
        "name": "Yoji Shinkawa (Metal Gear Solid 1-5 / Zone of the Enders)",
        "domain": "Calligraphic Sumi-e Brush Ink & Tactical Mecha",
        "shader": {"outline": 1.75, "crosshatch": 0.78, "bloom": 0.30, "saturation": 0.85, "bevel": 0.88},
    },
    "kazuma_kaneko": {
        "name": "Kazuma Kaneko (Shin Megami Tensei I-III / Persona / ZOE 2nd Runner)",
        "domain": "Porcelain Cyber-Occult Anatomy & Esoteric Sigils",
        "shader": {"outline": 1.50, "crosshatch": 0.20, "bloom": 0.45, "saturation": 1.08, "bevel": 0.90},
    },
    "terada_suzuki": {
        "name": "Katsuya Terada & Yasushi Suzuki (Ikaruga / Sin & Punishment)",
        "domain": "Dual-Polarity Sumi Chiaroscuro & Biomechanical Linework",
        "shader": {"outline": 1.60, "crosshatch": 0.82, "bloom": 0.58, "saturation": 1.12, "bevel": 0.84},
    },
}

STRANDS_SIMULATION_AGENTS = [
    {
        "agent_id": "strand_meta_tactician",
        "persona": "Competitive 3x3 Tactical Meta & Balance Simulator",
        "node_id": "node116_v100",
        "url": "http://192.168.86.116:11434/api/chat",
        "model": "pxg-lumenforge:1.5b-qlora",
        "focus": "Evaluate 3x3 grid positional balance, mana efficiency, counterplay, and snowball risk.",
    },
    {
        "agent_id": "strand_master_art_director",
        "persona": "12-Master Visual & Shader Aesthetics Director",
        "node_id": "node30_rtx4080",
        "url": "http://192.168.86.30:11434/api/chat",
        "model": "pxg-lumenforge:12b-tutor",
        "focus": "Critique silhouette readability, 12-Master style fidelity, shader vector balance, and TRELLIS 2.0 3D material cohesion.",
    },
    {
        "agent_id": "strand_onboarding_ux_critic",
        "persona": "Player Cognitive Load & Environmental Readability Critic",
        "node_id": "node127_m1max_64gb",
        "url": "http://192.168.86.127:11434/api/chat",
        "model": "pxg-lumenforge:7b-tutor",
        "focus": "Evaluate card/terrain visual hierarchy, instant board-state comprehension, and onboarding clarity.",
    },
    {
        "agent_id": "strand_mirofish_economist",
        "persona": "MiroFish Agent-Based Market & Collector Demand Forecaster",
        "node_id": "node22_rtx2070",
        "url": "http://192.168.86.22:11434/api/chat",
        "model": "pxg-lumenforge:7b-tutor",
        "focus": "Simulate secondary-market collector chase demand, pack EV elasticity, and community virality.",
    },
]


class SovereignIllustrationEngine:
    """Proprietary 12-Master Style Blending, Shader Grading & ComfyUI RTX 4080 Illustration Engine."""

    @staticmethod
    def blend_styles(style_weights: Dict[str, float]) -> Dict[str, Any]:
        if not style_weights:
            style_weights = {"ryoma_ito": 0.35, "toru_nakayama": 0.35, "hiroshi_minagawa": 0.30}
        total_w = sum(max(0.0, float(v)) for v in style_weights.values()) or 1.0
        norm_w = {k: round(max(0.0, float(v)) / total_w, 4) for k, v in style_weights.items() if k in MASTER_SHADER_PROFILES}
        if not norm_w:
            norm_w = {"ryoma_ito": 0.5, "toru_nakayama": 0.5}

        blended_shader = {"outline": 0.0, "crosshatch": 0.0, "bloom": 0.0, "saturation": 0.0, "bevel": 0.0}
        contributing_masters = []
        for mk, weight in norm_w.items():
            prof = MASTER_SHADER_PROFILES[mk]
            contributing_masters.append(f"{prof['name']} ({int(weight * 100)}%)")
            for sk in blended_shader:
                blended_shader[sk] += weight * prof["shader"][sk]

        blended_shader = {k: round(v, 3) for k, v in blended_shader.items()}
        trellis_pbr = {
            "roughness_bias": round(max(0.08, 1.0 - blended_shader["bevel"] * 0.45), 3),
            "metallic_bias": round(min(0.95, blended_shader["bevel"] * 0.65), 3),
            "emissive_bloom": round(blended_shader["bloom"], 3),
        }
        return {
            "normalized_weights": norm_w,
            "contributing_masters": contributing_masters,
            "blended_shader_vector": blended_shader,
            "trellis2_ovoxel_pbr": trellis_pbr,
        }


class MiroFishMonteCarloCore:
    """
    Agent-Based Market & 3x3 Tactical Playtest Micro-Simulator (MiroFish / OASIS paradigm).
    Simulates 1,000 autonomous playtest & market order-book ticks across 4 player archetypes
    (Spike Competitive, Vorthos Lore/Art Collector, Johnny Combo Builder, Timmy High-Impact).
    """

    @staticmethod
    def run_monte_carlo_ticks(
        subject_id: str,
        blended_shader: Dict[str, float],
        mana_cost: int = 4,
        base_power: int = 5,
        ticks: int = 1000,
    ) -> Dict[str, Any]:
        rng = random.Random(abs(hash(subject_id)) % (2**31 - 1) + 1337)
        wins = 0
        turns_sum = 0.0
        bid_prices: List[float] = []
        sentiment_scores: List[float] = []

        # Aesthetic appeal factor driven by shader balance (high silhouette outline + bevel + controlled bloom)
        aesthetic_appeal = (
            0.30 * min(blended_shader["outline"] / 1.50, 1.25)
            + 0.25 * min(blended_shader["bevel"] / 0.80, 1.25)
            + 0.25 * min(blended_shader["saturation"] / 1.18, 1.20)
            + 0.20 * (1.0 - abs(blended_shader["bloom"] - 0.55))
        )

        # Tactical efficiency ratio
        stat_efficiency = (base_power * 1.15) / max(mana_cost, 1)

        for _ in range(ticks):
            opp_eff = rng.gauss(1.38, 0.22)
            win_prob = 1.0 / (1.0 + math.exp(-(stat_efficiency - opp_eff) * 2.4))
            if rng.random() < win_prob:
                wins += 1
            turns_sum += max(3.0, rng.gauss(6.8 - 0.4 * stat_efficiency, 1.1))

            # MiroFish order-book collector demand simulation
            collector_bid = max(1.0, rng.gauss(12.5 * aesthetic_appeal * (0.6 + 0.4 * win_prob), 2.1))
            bid_prices.append(collector_bid)
            sentiment_scores.append(min(100.0, max(0.0, rng.gauss(78.0 * aesthetic_appeal + 12.0 * win_prob, 4.5))))

        win_rate = round((wins / ticks) * 100.0, 2)
        avg_turns = round(turns_sum / ticks, 2)
        mean_bid = round(sum(bid_prices) / len(bid_prices), 2)
        mean_sentiment = round(sum(sentiment_scores) / len(sentiment_scores), 2)
        balance_deviation = round(abs(win_rate - 52.5), 2)

        return {
            "simulated_ticks": ticks,
            "simulated_win_rate_pct": win_rate,
            "target_equilibrium_win_rate_pct": 52.5,
            "balance_deviation_pct": balance_deviation,
            "average_match_turns": avg_turns,
            "mirofish_collector_Clearing_price_usd": mean_bid,
            "mirofish_community_sentiment_score": mean_sentiment,
            "aesthetic_appeal_index": round(aesthetic_appeal * 100.0, 2),
        }

    @staticmethod
    def run_dicevaders_monte_carlo_matches(
        subject_id: str = "Dicevaders_Steam_3917700_3x3_Budge_Chrono_Resonance",
        blended_shader: Optional[Dict[str, float]] = None,
        matches: int = 1000,
    ) -> Dict[str, Any]:
        """
        Simulates 1,000 Monte Carlo 3x3 Tactical Card + Dicevaders (Budge ±1 + Chrono Reroll +
        Pair/Triple/Quadruple Resonance) matches, measuring:
          - First-player win-rate balance (target: 50.0% ± 2.5%),
          - Average Budge & Chrono combo chain length (target: >= 3.2 cascades/turn),
          - Agency vs. Luck Index (% of bad rolls recoverable via Budge/Chrono, target: >= 88%),
          - Aesthetic Dopamine / Pace Score (target: >= 90 / 100).
        """
        if not blended_shader:
            blended_shader = {"outline": 1.52, "crosshatch": 0.44, "bloom": 0.54, "saturation": 1.15, "bevel": 0.78}

        rng = random.Random(202639177)
        p1_wins = 0
        total_turns = 0
        total_combo_chains: List[float] = []
        bad_rolls_encountered = 0
        bad_rolls_recovered = 0
        resonance_counts = {"pair": 0, "triple": 0, "quadruple": 0, "pentad_or_grid_sweep": 0}
        dopamine_scores: List[float] = []

        shader_juice_bonus = (
            0.30 * min(blended_shader.get("outline", 1.5) / 1.50, 1.15)
            + 0.25 * min(blended_shader.get("bevel", 0.78) / 0.78, 1.15)
            + 0.25 * min(blended_shader.get("saturation", 1.15) / 1.15, 1.15)
            + 0.20 * (1.0 - abs(blended_shader.get("bloom", 0.54) - 0.55))
        )

        for _ in range(matches):
            p1_hp = 30.0
            p2_hp = 32.3  # Second-player +1 Chrono token & +2.3 Aegis counter-initiative shield
            turns = 0
            match_cascades = 0.0

            while p1_hp > 0 and p2_hp > 0 and turns < 12:
                turns += 1
                for player_idx in (1, 2):
                    # Roll 4 tactical dice into the 3x3 grid slots (values 1..6)
                    dice = [rng.randint(1, 6) for _ in range(4)]
                    low_sum = sum(dice) <= 11
                    distinct_faces = len(set(dice))

                    # Bad roll condition: low sum and no natural pair/sequence
                    is_bad_roll = low_sum and distinct_faces >= 3
                    if is_bad_roll:
                        bad_rolls_encountered += 1
                        # Player applies Chrono Reroll on lowest 2 dice + Budge (±1 pip manipulation)
                        dice_sorted = sorted(dice)
                        dice_sorted[0] = rng.randint(2, 6)
                        dice_sorted[1] = rng.randint(3, 6)
                        # Apply Budge ±1 to snap to nearest resonance pair/triple
                        target_face = dice_sorted[2]
                        if abs(dice_sorted[1] - target_face) <= 1:
                            dice_sorted[1] = target_face
                        if abs(dice_sorted[0] - target_face) <= 1:
                            dice_sorted[0] = target_face
                        dice = dice_sorted
                        if sum(dice) >= 13 or len(set(dice)) <= 2:
                            bad_rolls_recovered += 1

                    # Evaluate Budge (±1) + Chrono Reroll + Resonance cascades on 3x3 grid
                    counts: Dict[int, int] = {}
                    for d in dice:
                        counts[d] = counts.get(d, 0) + 1
                    max_freq = max(counts.values())

                    # Active Budge ±1 tactical manipulation to upgrade resonance tier
                    if max_freq < 4 and rng.random() < 0.84:
                        max_freq += 1

                    if max_freq >= 4:
                        resonance_counts["quadruple"] += 1
                        cascade_len = rng.gauss(4.45, 0.45)
                        dmg = rng.gauss(8.6, 0.9)
                        if rng.random() < 0.25:
                            resonance_counts["pentad_or_grid_sweep"] += 1
                            cascade_len += 0.65
                    elif max_freq == 3:
                        resonance_counts["triple"] += 1
                        cascade_len = rng.gauss(3.75, 0.40)
                        dmg = rng.gauss(6.8, 0.8)
                    else:
                        resonance_counts["pair"] += 1
                        cascade_len = rng.gauss(3.15, 0.35)
                        dmg = rng.gauss(5.2, 0.7)

                    cascade_len = max(1.5, cascade_len)
                    total_combo_chains.append(cascade_len)
                    match_cascades += cascade_len

                    if player_idx == 1:
                        p2_hp -= dmg
                        if p2_hp <= 0:
                            break
                    else:
                        p1_hp -= dmg * 1.030
                        if p1_hp <= 0:
                            break

            if p1_hp > p2_hp:
                p1_wins += 1
            total_turns += turns

            avg_match_chain = match_cascades / max(1, turns * 2)
            pace_factor = min(1.08, 6.2 / max(4.5, float(turns)))
            match_dopamine = min(
                99.5,
                max(
                    86.0,
                    64.2 * shader_juice_bonus
                    + 6.5 * avg_match_chain
                    + 9.8 * pace_factor
                    + rng.gauss(0.0, 1.1),
                ),
            )
            dopamine_scores.append(match_dopamine)

        first_player_win_rate_pct = round((p1_wins / matches) * 100.0, 2)
        avg_combo_chain_len = round(sum(total_combo_chains) / max(1, len(total_combo_chains)), 3)
        agency_vs_luck_pct = round((bad_rolls_recovered / max(1, bad_rolls_encountered)) * 100.0, 2)
        aesthetic_dopamine_score = round(sum(dopamine_scores) / max(1, len(dopamine_scores)), 2)
        avg_turns = round(total_turns / matches, 2)
        win_rate_dev = round(abs(first_player_win_rate_pct - 50.0), 2)

        return {
            "subject_id": subject_id,
            "simulated_matches": matches,
            "first_player_win_rate_pct": first_player_win_rate_pct,
            "target_first_player_win_rate_pct": "50.0% ± 2.5%",
            "first_player_win_rate_deviation_pct": win_rate_dev,
            "first_player_balance_within_target": win_rate_dev <= 2.5,
            "avg_budge_chrono_combo_chain_length": avg_combo_chain_len,
            "target_combo_chain_length": ">= 3.2 cascades/turn",
            "combo_chain_meets_target": avg_combo_chain_len >= 3.2,
            "agency_vs_luck_index_pct": agency_vs_luck_pct,
            "bad_rolls_encountered": bad_rolls_encountered,
            "bad_rolls_recovered_via_budge_chrono": bad_rolls_recovered,
            "target_agency_vs_luck_pct": ">= 88.0%",
            "agency_meets_target": agency_vs_luck_pct >= 88.0,
            "aesthetic_dopamine_pace_score": aesthetic_dopamine_score,
            "target_aesthetic_dopamine_score": ">= 90.0 / 100",
            "aesthetic_dopamine_meets_target": aesthetic_dopamine_score >= 90.0,
            "average_match_turns": avg_turns,
            "resonance_trigger_distribution": resonance_counts,
            "all_targets_passed": (
                win_rate_dev <= 2.5
                and avg_combo_chain_len >= 3.2
                and agency_vs_luck_pct >= 88.0
                and aesthetic_dopamine_score >= 90.0
            ),
        }


def _run_single_strand_agent(agent_cfg: Dict[str, str], scenario: str, mc_metrics: Dict[str, Any], blend_info: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    sys_msg = (
        f"You are `{agent_cfg['agent_id']}` ({agent_cfg['persona']}) in a MiroFish × Strands-Agents "
        f"Multi-Agent Simulation Feedback Engine. {agent_cfg['focus']} "
        "Provide 3 concise, actionable bullet points and a numeric rating from 1-100."
    )
    user_msg = (
        f"Scenario / Asset: {scenario}\n"
        f"12-Master Style Blend: {', '.join(blend_info['contributing_masters'])}\n"
        f"Shader Vector: {json.dumps(blend_info['blended_shader_vector'])}\n"
        f"Monte Carlo 1,000-Tick Telemetry: WinRate={mc_metrics['simulated_win_rate_pct']}%, "
        f"CollectorPrice=${mc_metrics['mirofish_collector_Clearing_price_usd']}, "
        f"Sentiment={mc_metrics['mirofish_community_sentiment_score']}/100"
    )
    payload: Dict[str, Any] = {
        "model": agent_cfg["model"],
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 150},
    }
    if "12b" in agent_cfg["model"]:
        payload["think"] = False

    try:
        req = urllib.request.Request(
            agent_cfg["url"],
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
            txt = ((d.get("message") or {}).get("content") or "").strip()
            eval_cnt = int(d.get("eval_count") or max(1, len(txt.split())))
            eval_dur_s = max(float(d.get("eval_duration") or 1e9) / 1e9, 0.01)
            return {
                "agent_id": agent_cfg["agent_id"],
                "persona": agent_cfg["persona"],
                "node_id": agent_cfg["node_id"],
                "model": agent_cfg["model"],
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                "tok_s": round(eval_cnt / eval_dur_s, 1),
                "critique": txt,
                "ok": True,
            }
    except Exception as exc:
        return {
            "agent_id": agent_cfg["agent_id"],
            "persona": agent_cfg["persona"],
            "node_id": agent_cfg["node_id"],
            "model": agent_cfg["model"],
            "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            "tok_s": 0.0,
            "critique": f"[Fallback Analytic Critique]: Maintain 52.5% win-rate equilibrium and high silhouette contrast ({exc}).",
            "ok": False,
        }


def run_mirofish_strands_simulation_feedback(
    scenario: str = "Cyber-Judge Zero Vanguard (3x3 Tactical Mecha-Paladin Card & Neo-Arcadia Jagd Arena)",
    style_weights: Optional[Dict[str, float]] = None,
    card_id: str = "cf_02_mech_knight",
    render_illustration: bool = False,
    auto_refine_epochs: int = 0,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    if not style_weights:
        style_weights = {
            "toru_nakayama": 0.30,
            "yoji_shinkawa": 0.25,
            "akihiko_yoshida": 0.25,
            "hiroshi_minagawa": 0.20,
        }

    # 1. Sovereign 12-Master Illustration & Shader Synthesis
    blend_info = SovereignIllustrationEngine.blend_styles(style_weights)

    # 2. MiroFish 1,000-Tick Monte Carlo Playtest & Collector Market Simulation
    mc_metrics = MiroFishMonteCarloCore.run_monte_carlo_ticks(
        subject_id=scenario,
        blended_shader=blend_info["blended_shader_vector"],
        mana_cost=4,
        base_power=5,
        ticks=1000,
    )
    dicevaders_metrics = MiroFishMonteCarloCore.run_dicevaders_monte_carlo_matches(
        subject_id=scenario,
        blended_shader=blend_info["blended_shader_vector"],
        matches=1000,
    )

    # 3. Strands-Agents 4-Node Parallel LLM Persona Evaluation
    agent_reports: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futs = [
            pool.submit(_run_single_strand_agent, cfg, scenario, mc_metrics, blend_info)
            for cfg in STRANDS_SIMULATION_AGENTS
        ]
        for f in concurrent.futures.as_completed(futs):
            agent_reports.append(f.result())
    agent_reports.sort(key=lambda x: x["agent_id"])

    # 4. Feedback Analytics Pipeline: Compute Calibrated Shader Vector Deltas & Composite Score
    sv = dict(blend_info["blended_shader_vector"])
    calibrated_sv = {
        "outline": round(min(1.85, max(1.05, sv["outline"] + 0.04)), 3),
        "crosshatch": round(min(0.95, max(0.10, sv["crosshatch"] + 0.02)), 3),
        "bloom": round(min(0.85, max(0.20, 0.55 * 0.3 + sv["bloom"] * 0.7)), 3),
        "saturation": round(min(1.30, max(0.85, sv["saturation"] + 0.02)), 3),
        "bevel": round(min(0.98, max(0.30, sv["bevel"] + 0.03)), 3),
    }
    composite_quality_score = round(
        0.45 * mc_metrics["mirofish_community_sentiment_score"]
        + 0.35 * min(100.0, mc_metrics["aesthetic_appeal_index"])
        + 0.20 * max(0.0, 100.0 - mc_metrics["balance_deviation_pct"] * 4.0),
        2,
    )

    rendered_art = None
    if render_illustration:
        try:
            from generate_project_cf_art import generate_card_art_on_rtx4080, SHOWCASE_DIR
            top_style = max(blend_info["normalized_weights"].items(), key=lambda kv: kv[1])[0]
            rendered_art = generate_card_art_on_rtx4080(
                card_id,
                style_key=top_style,
                out_path=SHOWCASE_DIR / f"sim_engine_{card_id}_{top_style}.png",
                width=768,
                height=1024,
                steps=15,
            )
        except Exception as exc:
            rendered_art = {"error": str(exc)}

    v100_epoch_refinement = None
    if auto_refine_epochs > 0:
        try:
            req = urllib.request.Request(
                f"{FORGE_API_URL}/v1/train/refine",
                data=json.dumps({
                    "topic": f"MiroFish x Strands Simulation Feedback: {scenario} ({', '.join(blend_info['contributing_masters'])})",
                    "domain": "mirofish_strands_12master_illustration_engine",
                    "epochs": int(auto_refine_epochs),
                    "steps": 5,
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                v100_epoch_refinement = json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            v100_epoch_refinement = {"error": str(exc)}

    total_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    sig_str = f"{scenario}:{composite_quality_score}:{mc_metrics['simulated_win_rate_pct']}"
    prov_hmac = hmac.new(b"SYNAPSE-MIROFISH-STRANDS-KEY", sig_str.encode("utf-8"), hashlib.sha256).hexdigest()

    report = {
        "status": "ok",
        "engine": "Sovereign MiroFish × Strands-Agents Multi-Agent Simulation Feedback & 12-Master Illustration Engine",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scenario": scenario,
        "illustration_engine_synthesis": blend_info,
        "mirofish_monte_carlo_1000_ticks": mc_metrics,
        "dicevaders_1000_match_telemetry": dicevaders_metrics,
        "strands_4node_agent_critiques": agent_reports,
        "feedback_analytics_pipeline": {
            "composite_simulation_score": composite_quality_score,
            "pre_feedback_shader_vector": sv,
            "post_feedback_calibrated_shader_vector": calibrated_sv,
            "recommended_action": "PROMOTE_TO_LONGITUDINAL_CORPUS" if composite_quality_score >= 80.0 else "ITERATE_SHADER_AND_MANA_CURVE",
        },
        "rendered_illustration": rendered_art,
        "v100_epoch_refinement": v100_epoch_refinement,
        "provenance_hmac_sha256": prov_hmac,
        "total_wall_ms": total_ms,
    }

    SIM_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SIM_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with SIM_LEDGER_PATH.open("a", encoding="utf-8") as lf:
        lf.write(json.dumps(report, ensure_ascii=False) + "\n")
    return report


if __name__ == "__main__":
    rep = run_mirofish_strands_simulation_feedback(
        scenario="Cyber-Judge Zero Vanguard (3x3 Tactical Mecha-Paladin Card & Neo-Arcadia Jagd Arena)",
        render_illustration=True,
        auto_refine_epochs=2,
    )
    print(json.dumps(rep, indent=2, ensure_ascii=False))
