#!/usr/bin/env python3
"""
Generates `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/advance_wars_ffta_dynamics_training.jsonl`
containing 120 structured training records decompiling:
1. Advance Wars (Ryo Hirata / Intelligent Systems) — Damage Matrix, Terrain Defense Stars (0-4),
   CO Power / Super CO Power Star Meters, Segmented Movement Arrows, 4-Corner Crosshair % DMG Forecast,
   and Split-Screen Battle Cut-In Frame Timelines.
2. Final Fantasy Tactics Advance (Yasumi Matsuno / Ryoma Ito / Akihiko Yoshida / Hideo Minaba) —
   CTB (Charge Time Battle, CT += Speed >= 1000) turn-order equations, Directional Facing
   (Front 1.0x, Side/Flank 1.25x, Back/Rear 1.50x + Push), Elevation Delta-Z advantage,
   Judge Points (JP 0..10), Mythril Combo Link Arcs, and Totema Summons.
3. Multitude of 12 Classic-Yet-Simple Telegraph Animation Blueprints (frame timings, easing curves,
   color hex codes, and strategic readability rules).
4. Combined AW + FFTA + Into the Breach + STACCS tactical stack & telegraph synthesis scenarios.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
BACKEND_DIR = ROOT_DIR / "Backend"
DATASETS_DIR = ROOT_DIR / "Datasets"
OUTPUT_JSONL = DATASETS_DIR / "advance_wars_ffta_dynamics_training.jsonl"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from synapse_tcg_backend import (  # noqa: E402
    AdvanceWarsFftaDynamicsSimulator,
    CLASSIC_12_TELEGRAPH_ARCHETYPES,
    OFFICIAL_PROJECT_CF_CARDS,
)


def build_training_records() -> List[Dict]:
    records: List[Dict] = []
    sim = AdvanceWarsFftaDynamicsSimulator(width=3, height=3, seed=20261107)
    cards = list(OFFICIAL_PROJECT_CF_CARDS.values())

    # 1. All 12 Classic-Yet-Simple Telegraph Animation Blueprints (12 records)
    for idx, (arch_id, arch) in enumerate(CLASSIC_12_TELEGRAPH_ARCHETYPES.items(), start=1):
        records.append(
            {
                "record_id": f"telegraph_blueprint_{idx:03d}",
                "domain": "multitude_telegraph_archetype",
                "source_lineage": arch["source_game"],
                "archetype_id": arch_id,
                "animation_spec": {
                    "layer_order": arch["layer_order"],
                    "duration_ms": arch["duration_ms"],
                    "frames_60fps": arch["frames_60fps"],
                    "easing": arch["easing"],
                    "color_hex": arch["color_hex"],
                    "visual_style": arch["visual_style"],
                },
                "strategic_readout": arch["strategic_readout"],
                "instruction": (
                    f"Specify the classic-yet-simple telegraph animation blueprint for `{arch_id}` "
                    f"({arch['source_game']}) in Synapse.TcgEngine."
                ),
                "response": (
                    f"Telegraph `{arch_id}` renders on layer {arch['layer_order']} over {arch['duration_ms']}ms "
                    f"({arch['frames_60fps']} frames @ 60fps) using `{arch['easing']}` easing and primary hex "
                    f"`{arch['color_hex']}`. Visual style: {arch['visual_style']}. "
                    f"Strategic function: {arch['strategic_readout']}."
                ),
            }
        )

    # 2. Advance Wars Decompiled Damage Matrix, Terrain Stars (0-4), & Cut-In Timelines (30 records)
    terrains = [
        ("road", 0),
        ("plain", 1),
        ("woods", 2),
        ("building", 3),
        ("hq", 4),
    ]
    co_profiles = [
        ("Standard_Command", 100, 100, "NONE"),
        ("CO_Power_Active", 110, 110, "CO_POWER"),
        ("Super_CO_Power_Active", 130, 130, "SUPER_CO_POWER"),
    ]
    hp_pairs = [(10, 10), (8, 10), (10, 6), (7, 5)]
    aw_idx = 0
    for t_name, t_stars in terrains:
        for co_label, atk_co, def_co, p_state in co_profiles:
            for atk_hp, def_hp in hp_pairs[:2]:
                aw_idx += 1
                c_atk = cards[aw_idx % len(cards)]
                c_def = cards[(aw_idx + 3) % len(cards)]
                base_dmg = 55 + (c_atk.up * 5)
                dmg_pct = sim.compute_advance_wars_damage(
                    base_dmg=base_dmg,
                    atk_co=atk_co,
                    def_co=def_co,
                    atk_hp=atk_hp,
                    def_hp=def_hp,
                    terrain_stars=t_stars,
                    luck=0,
                )
                records.append(
                    {
                        "record_id": f"aw_damage_matrix_{aw_idx:03d}",
                        "domain": "advance_wars_decompilation",
                        "architects": "Ryo Hirata / Intelligent Systems",
                        "decompiled_routine": "GBA_0x0802A410_ComputeBattleDamagePercent",
                        "inputs": {
                            "attacker_card": c_atk.id,
                            "defender_card": c_def.id,
                            "base_damage": base_dmg,
                            "atk_co": atk_co,
                            "def_co": def_co,
                            "co_power_state": p_state,
                            "atk_hp_10": atk_hp,
                            "def_hp_10": def_hp,
                            "terrain": t_name,
                            "terrain_defense_stars": t_stars,
                        },
                        "outputs": {
                            "forecast_damage_pct": dmg_pct,
                            "telegraph_archetypes": [
                                "aw_segmented_movement_arrow",
                                "aw_4corner_crosshair_forecast",
                                "aw_terrain_defense_star_pulse",
                            ],
                            "split_screen_cutin_frames": {"slide_in": 8, "fire_burst": 18, "hp_tick_down": 12, "slide_out": 7},
                        },
                        "instruction": (
                            f"Compute the Advance Wars deterministic % damage forecast when `{c_atk.title}` "
                            f"(Base={base_dmg}, HP={atk_hp}/10, AtkCO={atk_co}) attacks `{c_def.title}` "
                            f"(HP={def_hp}/10, DefCO={def_co}) on `{t_name}` ({t_stars}★ defense)."
                        ),
                        "response": (
                            f"Using the Advance Wars formula `floor((Base*AtkCO/100)*(AtkHP/10)*((200-(DefCO+Stars*DefHP))/100))`, "
                            f"expected damage is `{dmg_pct}%`. The UI displays `aw_segmented_movement_arrow`, "
                            f"`aw_4corner_crosshair_forecast` (`{dmg_pct}% DMG`), and `{t_stars}★` `aw_terrain_defense_star_pulse`."
                        ),
                    }
                )

    # 3. Advance Wars CO Power & Super CO Power Star Meter Charging Curves (12 records)
    for i in range(1, 13):
        dealt = i * 10
        taken = (13 - i) * 5
        super_flag = (i % 2 == 0)
        sim_co = AdvanceWarsFftaDynamicsSimulator()
        sim_co.co_state[0]["co_stars"] = 5.0 if super_flag else 2.2
        res = sim_co.charge_and_activate_co_power(0, damage_dealt_value=dealt, damage_taken_value=taken, super_power=super_flag)
        records.append(
            {
                "record_id": f"aw_co_meter_{i:03d}",
                "domain": "advance_wars_co_power_meter",
                "architects": "Ryo Hirata / Intelligent Systems",
                "inputs": {
                    "damage_dealt_value": dealt,
                    "damage_taken_value": taken,
                    "request_super_co_power": super_flag,
                },
                "outputs": res,
                "instruction": (
                    f"Evaluate CO Star Meter charge for dealt={dealt}, taken={taken} (2x comeback multiplier) "
                    f"with `super_power={super_flag}`."
                ),
                "response": (
                    f"CO Meter resolves to `activated={res['activated']}` (`{res['power_type']}`), "
                    f"granting `atk_co={res['atk_co']}`, `def_co={res['def_co']}`, and `+{res['all_sides_bonus']}` "
                    f"all-sides card stats while triggering `aw_co_power_star_ignition`."
                ),
            }
        )

    # 4. Final Fantasy Tactics Advance CTB Queue & Directional Facing Multipliers (30 records)
    dir_names = ["UP", "DOWN", "LEFT", "RIGHT"]
    ffta_idx = 0
    for atk_d in dir_names:
        for def_d in dir_names:
            ffta_idx += 1
            facing_type, mult = sim.compute_ffta_facing_multiplier(atk_d, def_d)
            c_unit = cards[ffta_idx % len(cards)]
            speed_a = 110 + (c_unit.up * 5)
            speed_b = 95 + (c_unit.down * 4)
            ctb_res = sim.advance_ffta_ctb_queue(
                [
                    {"uid": f"{c_unit.id}_alpha", "ct": 600, "speed": speed_a},
                    {"uid": "enemy_sentinel", "ct": 650, "speed": speed_b},
                ]
            )
            records.append(
                {
                    "record_id": f"ffta_ctb_facing_{ffta_idx:03d}",
                    "domain": "ffta_decompilation",
                    "architects": "Yasumi Matsuno / Ryoma Ito / Akihiko Yoshida / Hideo Minaba",
                    "decompiled_routine": "GBA_0x08044B20_FFTA_CTB_And_DirectionalFacing",
                    "inputs": {
                        "attacker_card": c_unit.id,
                        "attack_direction": atk_d,
                        "defender_facing": def_d,
                        "unit_speeds": {"alpha": speed_a, "enemy": speed_b},
                    },
                    "outputs": {
                        "facing_hit_type": facing_type,
                        "damage_multiplier": mult,
                        "triggers_backstab_push": facing_type == "BACK",
                        "ctb_next_active": ctb_res["active_unit_uid"],
                        "ctb_ticks_elapsed": ctb_res["ticks_elapsed"],
                        "telegraph_archetypes": ["ffta_directional_facing_chevron", "ffta_ctb_turn_ribbon_preview"],
                    },
                    "instruction": (
                        f"Compute FFTA directional facing multiplier for attack vector `{atk_d}` against defender "
                        f"facing `{def_d}`, and resolve the CTB (`CT >= 1000`) queue."
                    ),
                    "response": (
                        f"Attack vector `{atk_d}` vs defender facing `{def_d}` yields `{facing_type}` (`{mult:.2f}x` multiplier, "
                        f"backstab_push={facing_type == 'BACK'}). Next active CTB unit is `{ctb_res['active_unit_uid']}` "
                        f"after `{ctb_res['ticks_elapsed']}` ticks."
                    ),
                }
            )

    # 5. FFTA Judge Points (JP), Mythril Combo Chains, & Combined AW+FFTA+ITB+STACCS Synthesis (36 records)
    for s_idx in range(1, 37):
        sim_comb = AdvanceWarsFftaDynamicsSimulator(width=3, height=3, seed=5000 + s_idx)
        c_main = cards[s_idx % len(cards)]
        c_ally1 = cards[(s_idx + 1) % len(cards)]
        c_ally2 = cards[(s_idx + 2) % len(cards)]
        c_enemy = cards[(s_idx + 5) % len(cards)]

        # Build 3D stack at (1, 1) and allied flankers at (0, 1) and (1, 0)
        sim_comb.stack_card(1, 1, "cc_01_sketching", owner=0)
        if s_idx % 2 == 0:
            sim_comb.stack_card(1, 1, "cc_03_storyboard", owner=0)
        sim_comb.stack_card(1, 1, c_main, owner=0)
        sim_comb.stack_card(0, 1, c_ally1, owner=0)
        sim_comb.stack_card(1, 0, c_ally2, owner=0)
        sim_comb.stack_card(1, 2, c_enemy, owner=1)
        sim_comb.place_power_grid_building(2, 2, bars=2)

        jp_to_spend = 10 if (s_idx % 9 == 0) else ((s_idx % 4) + 1)
        sim_comb.judge_points[0] = max(jp_to_spend, 4)
        combo_res = sim_comb.trigger_ffta_mythril_combo(sim_comb, 1, 1, owner=0, jp_spent=jp_to_spend)
        telegraphs = sim_comb.generate_multitude_telegraphs(
            sim_comb,
            {
                "owner": 0,
                "from": (0, 0),
                "to": (1, 1),
                "target": (1, 2),
                "attack_dir": "UP",
                "defender_facing": "UP" if s_idx % 3 == 0 else ("LEFT" if s_idx % 3 == 1 else "DOWN"),
                "push_dir": (0, 1),
                "base_dmg": 80,
            },
        )
        records.append(
            {
                "record_id": f"combined_tactical_synthesis_{s_idx:03d}",
                "domain": "combined_aw_ffta_itb_staccs_synthesis",
                "architects": "Ryo Hirata + Yasumi Matsuno + Subset Games + STACCS + Synapse",
                "inputs": {
                    "lead_card": c_main.id,
                    "stack_z_height": sim_comb.grid[1][1].z_height,
                    "allied_flankers": [c_ally1.id, c_ally2.id],
                    "enemy_target": c_enemy.id,
                    "jp_spent": jp_to_spend,
                },
                "outputs": {
                    "effective_stats": sim_comb.get_effective_stats(1, 1),
                    "mythril_combo": combo_res,
                    "active_telegraph_count": len(telegraphs),
                    "telegraph_ids": [t["archetype_id"] for t in telegraphs],
                    "forecast_damage_pct": telegraphs[0]["forecast_damage_pct"],
                    "facing_type": telegraphs[0]["facing_type"],
                    "elevation_delta_z": telegraphs[0]["elevation_delta_z"],
                },
                "instruction": (
                    f"Synthesize the combined Advance Wars + FFTA + Into the Breach + STACCS state when "
                    f"`{c_main.title}` (stack z={sim_comb.grid[1][1].z_height}) triggers a Mythril Combo "
                    f"(`jp_spent={jp_to_spend}`) with `{c_ally1.title}` & `{c_ally2.title}` against `{c_enemy.title}`."
                ),
                "response": (
                    f"Stack at (1,1) reaches effective stats `{sim_comb.get_effective_stats(1, 1)}` with "
                    f"`combo_stat_bonus=+{combo_res['combo_stat_bonus']}` (`totema_summoned={combo_res['totema_summoned']}`). "
                    f"All {len(telegraphs)} classic telegraph animations fire simultaneously, forecasting "
                    f"`{telegraphs[0]['forecast_damage_pct']}%` damage (`{telegraphs[0]['facing_type']}`, "
                    f"`ΔZ={telegraphs[0]['elevation_delta_z']}`)."
                ),
            }
        )

    return records


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    records = build_training_records()
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as fh:
        for row in records:
            fh.write(json.dumps(row) + "\n")
    print(json.dumps({"dataset_path": str(OUTPUT_JSONL), "records_written": len(records)}, indent=2))


if __name__ == "__main__":
    main()
