#!/usr/bin/env python3
"""Per-persona objective telemetry summaries from raw/moves.jsonl + raw/matches.jsonl.

Output: raw/persona_summaries.json  (consumed by gen_feedback.py, judge_feedback.py, aggregate.py)
Every number here is computed from the real-browser telemetry; nothing is synthetic.
"""
import json
import os
import statistics as st
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")


def load(name):
    p = os.path.join(RAW, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 3) if xs else None


def main():
    moves, matches = load("moves.jsonl"), load("matches.jsonl")
    import subprocess
    personas = json.loads(subprocess.check_output(
        ["/Users/frederickamina/.local/bin/node", "-e",
         "console.log(JSON.stringify(require('./personas.js')))"], cwd=os.path.join(ROOT, "scripts")))
    by_m = defaultdict(list)
    by_mv = defaultdict(list)
    for m in matches:
        by_m[m["persona"]].append(m)
    for mv in moves:
        by_mv[mv["persona"]].append(mv)
    out = {}
    for P in personas:
        pid = P["id"]
        ms, mvs = by_m[pid], by_mv[pid]
        if not ms:
            continue
        n = len(ms)
        wins = sum(m["outcome"] == "win" for m in ms)
        per_stage = {}
        for s in (1, 2, 3, 4):
            sm = [m for m in ms if m["stage"] == s]
            per_stage[s] = {"matches": len(sm), "wins": sum(m["outcome"] == "win" for m in sm),
                            "avg_margin": mean([m["margin"] for m in sm]),
                            "avg_blue": mean([m["blue"] for m in sm])}
        T = lambda k: sum(m["totals"][k] for m in ms)
        lost_kinds = Counter(l["kind"] for m in ms for l in m["lost_at"])
        lost_turns = Counter(l["turn"] for m in ms for l in m["lost_at"])
        turns = len(mvs)
        dice_turns = sum(1 for x in mvs if "nudges" in x or "reroll" in x)
        slide_turns = sum(1 for x in mvs if x.get("slide", {}).get("ok"))
        boss = [x["boss"] for x in mvs if "boss" in x]
        losses = [{"match": m["match_id"], "score": f'{m["blue"]}-{m["red"]}'} for m in ms if m["outcome"] == "loss"]
        heroes = Counter(c for m in ms for c in m["cards_played"])
        out[pid] = {
            "persona": pid, "name": P["name"], "archetype": P["archetype"],
            "params": {k: P[k] for k in ("policy", "epsilon", "thinkMs", "nudge", "reroll", "slide", "dragJitter",
                                         "misdropProb", "dragSteps", "patience", "ownerMisread")},
            "matches": n, "wins": wins, "losses": n - wins, "win_rate": round(wins / n, 3),
            "per_stage": per_stage,
            "avg_final_blue": mean([m["blue"] for m in ms]), "avg_final_red": mean([m["red"] for m in ms]),
            "avg_margin": mean([m["margin"] for m in ms]), "min_margin": min(m["margin"] for m in ms),
            "loss_list": losses,
            "turns": turns,
            "avg_flips_gained_per_match": round(T("flips_gained") / n, 3),
            "avg_slide_flips_per_match": round(T("slide_flips") / n, 3),
            "avg_flips_lost_per_match": round(T("flips_lost") / n, 3),
            "nudges_total": T("nudges"), "rerolls_total": T("rerolls"), "slides_total": T("slides"),
            "pct_turns_using_dice": round(dice_turns / turns, 3) if turns else 0,
            "pct_turns_using_slide": round(slide_turns / turns, 3) if turns else 0,
            "misdrops_total": T("misdrops"), "drop_retries_total": T("drop_retries"),
            "drop_mismatch_total": T("drop_mismatch"), "invalid_actions_total": T("invalid_actions"),
            "random_moves_total": T("random_moves"), "ownership_misreads_total": T("misreads"),
            "decision_latency_ms_mean": mean([x["decision_latency_ms"] for x in mvs]),
            "decision_latency_ms_median": round(st.median([x["decision_latency_ms"] for x in mvs]), 1) if mvs else None,
            "policy_compute_ms_mean": mean([x["policy_compute_ms"] for x in mvs]),
            "drag_ms_mean": mean([x["drag_ms"] for x in mvs]),
            "agency_mean": mean([x["agency"] for x in mvs]),
            "decision_space_mean": mean([x["decision_space"] for x in mvs]),
            "regret_mean": mean([x["regret"] for x in mvs]),
            "pct_turns_zero_decision_space": round(sum(1 for x in mvs if x["decision_space"] == 0) / turns, 3) if turns else None,
            "cards_lost_by_tile_kind": dict(lost_kinds),
            "cards_lost_by_turn": {str(k): v for k, v in sorted(lost_turns.items())},
            "boss_pred_match_rate": round(sum(b["pred_match"] for b in boss) / len(boss), 3) if boss else None,
            "place_pred_match_rate": round(sum(1 for x in mvs if x["flips_pred"] == x["flips_gained"]) / turns, 3) if turns else None,
            "distinct_heroes_played": len(heroes), "hero_play_counts": dict(heroes),
            "unused_hand_cards_per_match": mean([len(m["unused_hand"]) for m in ms]),
            "frustration_index_mean": mean([m["frustration_index"] for m in ms]),
            "cum_frustration_final": ms[-1]["cum_frustration"],
            "would_quit_at_match": ms[-1]["would_quit_at_match"],
            "modal_consistent_all": all(m["modal_consistent"] for m in ms),
            "avg_match_duration_s": round(mean([m["duration_ms"] for m in ms]) / 1000, 2),
            "screenshots": [s for m in ms for s in m["screenshots"]],
        }
    with open(os.path.join(RAW, "persona_summaries.json"), "w") as f:
        json.dump(out, f, indent=2)
    for pid, s in out.items():
        print(pid, s["name"], "win", s["win_rate"], "margin", s["avg_margin"], "lat", s["decision_latency_ms_mean"],
              "dice%", s["pct_turns_using_dice"], "slide%", s["pct_turns_using_slide"], "agency", s["agency_mean"])


if __name__ == "__main__":
    main()
