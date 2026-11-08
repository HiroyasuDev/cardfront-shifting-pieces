#!/usr/bin/env python3
"""Aggregate objective telemetry (REAL) with SYNTHETIC feedback into MiroFish analytics.

Inputs : raw/moves.jsonl, raw/matches.jsonl, raw/persona_summaries.json,
         feedback/persona_feedback.json, feedback/feedback_consistency.json, raw/cvd_color_pairs.json
Outputs: raw/aggregate.json, raw/report_tables.md
"""
import json
import os
import re
import statistics as st
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
FB = os.path.join(ROOT, "feedback")
RK = ["fun", "rules_clarity", "board_readability", "difficulty_fairness", "strategic_depth", "drag_drop_feel", "art", "replay_intent"]


def jl(p):
    return [json.loads(l) for l in open(p)]


def jload(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


def rank(xs):
    s = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and xs[s[j + 1]] == xs[s[i]]:
            j += 1
        for k in range(i, j + 1):
            r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3 or len(set(a)) < 2 or len(set(b)) < 2:
        return None
    ra, rb = rank(a), rank(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return round(num / den, 3) if den else None


THEMES = {
    "too easy / low challenge": r"easy|too simple|no challenge|not challenging|predictab|always win|won every|steamroll|trivial",
    "dice / column boost": r"dice|die\b|nudg|reroll|column boost|\+1",
    "tactical slide": r"slid",
    "drag & drop feel": r"drag|drop|snap|magnet",
    "art / visuals": r"\bart\b|artwork|visual|graphic|illustrat|look(s)? (great|good|amazing)|beautiful|style",
    "readability / clarity": r"readab|clear|clarity|confus|understand|numbers|hard to (see|read|tell)|colou?r",
    "strategic depth": r"strateg|depth|deep|tactic|decision|choice|think",
    "boss AI behaviour": r"\bboss\b|\bai\b|opponent|enemy",
    "pace / speed": r"fast|quick|slow|pace|short|speed",
    "unused 5th card / hand size": r"unused|fifth|5th|leftover|left over",
}


def main():
    moves, matches = jl(os.path.join(RAW, "moves.jsonl")), jl(os.path.join(RAW, "matches.jsonl"))
    sums = jload(os.path.join(RAW, "persona_summaries.json"), {})
    fbj = jload(os.path.join(FB, "persona_feedback.json"), {"feedback": {}})["feedback"]
    cons = jload(os.path.join(FB, "feedback_consistency.json"), {"personas": {}})
    cvd = jload(os.path.join(RAW, "cvd_color_pairs.json"), {})
    agg = {}

    # ---- pooled objective ----
    n = len(matches)
    agg["pooled"] = {
        "matches": n, "turns": len(moves), "personas": len(sums),
        "win_rate": round(sum(m["outcome"] == "win" for m in matches) / n, 3),
        "avg_margin": round(st.mean(m["margin"] for m in matches), 3),
        "place_pred_match_rate": round(sum(x["flips_pred"] == x["flips_gained"] for x in moves) / len(moves), 4),
        "boss_pred_match_rate": round(sum(x["boss"]["pred_match"] for x in moves if "boss" in x) / sum(1 for x in moves if "boss" in x), 4),
        "boss_turns": sum(1 for x in moves if "boss" in x),
        "modal_consistent_rate": round(sum(m["modal_consistent"] for m in matches) / n, 4),
        "unused_hand_cards_per_match": round(st.mean(len(m["unused_hand"]) for m in matches), 3),
        "turns_per_match": round(st.mean(m["turns"] for m in matches), 3),
        "margin_distribution": dict(sorted(Counter(m["margin"] for m in matches).items())),
    }
    stage = {}
    for s in (1, 2, 3, 4):
        sm = [m for m in matches if m["stage"] == s]
        smv = [x for x in moves if x["stage"] == s]
        stage[s] = {"matches": len(sm), "win_rate": round(sum(m["outcome"] == "win" for m in sm) / len(sm), 3),
                    "avg_margin": round(st.mean(m["margin"] for m in sm), 3),
                    "avg_flips_lost": round(st.mean(m["totals"]["flips_lost"] for m in sm), 3),
                    "avg_flips_gained": round(st.mean(m["totals"]["flips_gained"] + m["totals"]["slide_flips"] for m in sm), 3),
                    "ai_bonus": sm[0]["ai_bonus"], "boss_name": sm[0]["stage_name"],
                    "agency_mean": round(st.mean(x["agency"] for x in smv if x["agency"] is not None), 3)}
    agg["per_stage"] = stage
    agg["lost_by_tile_kind"] = dict(Counter(l["kind"] for m in matches for l in m["lost_at"]))
    agg["lost_by_turn"] = dict(sorted(Counter(l["turn"] for m in matches for l in m["lost_at"]).items()))
    agg["boss_flips_by_turn"] = {t: round(st.mean(x["boss"]["flips"] for x in moves if x["turn"] == t and "boss" in x), 3) for t in (1, 2, 3, 4)}
    # tile availability in final-turn: decision space by turn
    agg["decision_space_by_turn"] = {t: round(st.mean(x["decision_space"] for x in moves if x["turn"] == t), 3) for t in (1, 2, 3, 4)}
    agg["zero_choice_turn_rate_by_turn"] = {t: round(sum(x["decision_space"] == 0 for x in moves if x["turn"] == t) / max(1, sum(1 for x in moves if x["turn"] == t)), 3) for t in (1, 2, 3, 4)}

    # dice effect on placement flips (dice state at the moment of deploy, reconstructed from logged actions)
    b_f, nb_f = [], []
    for x in moves:
        d = list(x["reroll"]["after"]) if "reroll" in x else list(x["dice_start"])
        for nd in x.get("nudges", []):
            d[nd["col"] - 1] = nd["after"]
        col = x["landed_tile"][1] - 1
        (b_f if d[col] >= 4 else nb_f).append(x["flips_gained"])
    agg["dice_effect"] = {"deploys_in_boosted_col": len(b_f), "avg_flips_boosted": round(st.mean(b_f), 3) if b_f else None,
                          "deploys_unboosted_col": len(nb_f), "avg_flips_unboosted": round(st.mean(nb_f), 3) if nb_f else None}
    # win rate vs dice usage (persona-level confounded; reported as descriptive only)
    used = [m for m in matches if m["totals"]["nudges"] + m["totals"]["rerolls"] > 0]
    unused = [m for m in matches if m["totals"]["nudges"] + m["totals"]["rerolls"] == 0]
    agg["dice_usage_split"] = {
        "matches_with_dice": len(used), "win_rate_with_dice": round(sum(m["outcome"] == "win" for m in used) / len(used), 3) if used else None,
        "avg_margin_with_dice": round(st.mean(m["margin"] for m in used), 3) if used else None,
        "matches_without_dice": len(unused), "win_rate_without_dice": round(sum(m["outcome"] == "win" for m in unused) / len(unused), 3) if unused else None,
        "avg_margin_without_dice": round(st.mean(m["margin"] for m in unused), 3) if unused else None}
    sl = [m for m in matches if m["totals"]["slides"] > 0]
    nsl = [m for m in matches if m["totals"]["slides"] == 0]
    agg["slide_usage_split"] = {
        "matches_with_slide": len(sl), "avg_margin_with_slide": round(st.mean(m["margin"] for m in sl), 3) if sl else None,
        "avg_slide_flips_when_used": round(st.mean(m["totals"]["slide_flips"] / m["totals"]["slides"] for m in sl), 3) if sl else None,
        "matches_without_slide": len(nsl), "avg_margin_without_slide": round(st.mean(m["margin"] for m in nsl), 3) if nsl else None}
    drags = len(moves) + sum(1 for x in moves if "slide" in x)
    agg["drag"] = {"deploy_drags": len(moves), "slide_drags": sum(1 for x in moves if "slide" in x),
                   "deploy_mismatch": sum(x["drop_mismatch"] for x in moves), "deploy_retries": sum(x["drop_retries"] for x in moves),
                   "misdrops_springback": sum(x["misdrops"] for x in moves),
                   "slide_failed": sum(1 for x in moves if "slide" in x and not x["slide"]["ok"]),
                   "slide_landed_elsewhere": sum(1 for x in moves if "slide" in x and x["slide"]["ok"] and x["slide"]["landed"] != x["slide"]["to"]),
                   "max_abs_release_offset_tile_frac_success": round(max(max(abs(v) for v in x["release_offset"]) for x in moves if not x["drop_mismatch"] and x["drop_retries"] == 0), 3)}
    agg["drag"]["total_drags"] = drags

    # ---- MiroFish analytics ----
    agency = [x["agency"] for x in moves if x["agency"] is not None]
    agg["mirofish"] = {
        "MeanFrustrationIndex": round(st.mean(m["frustration_index"] for m in matches), 4),
        "MeanPlayerAgencyScore": round(st.mean(agency), 4),
        "MeanDecisionSpace_cards": round(st.mean(x["decision_space"] for x in moves), 4),
        "ZeroChoiceTurnRate": round(sum(x["decision_space"] == 0 for x in moves) / len(moves), 4),
        "WouldQuitPersonas": [sums[p]["name"] for p in sums if sums[p]["would_quit_at_match"]],
    }
    # ---- subjective (SYNTHETIC) ----
    ok = {p: f for p, f in fbj.items() if f.get("ratings")}
    disp = {}
    for k in RK:
        vals = [f["ratings"][k] for f in ok.values()]
        disp[k] = {"mean": round(st.mean(vals), 2), "sd": round(st.pstdev(vals), 2), "min": min(vals), "max": max(vals)} if vals else None
    npsv = [f["nps"] for f in ok.values()]
    agg["synthetic_ratings"] = {
        "personas_with_feedback": len(ok), "dispersion": disp,
        "RatingDispersion_mean_sd": round(st.mean(d["sd"] for d in disp.values() if d), 3) if ok else None,
        "nps_values": npsv,
        "NPS_score": round(100 * (sum(v >= 9 for v in npsv) - sum(v <= 6 for v in npsv)) / len(npsv), 1) if npsv else None,
    }
    # objective vs subjective
    pids = [p for p in ok if p in sums]
    pairs = {
        "win_rate~difficulty_fairness": ([sums[p]["win_rate"] for p in pids], [ok[p]["ratings"]["difficulty_fairness"] for p in pids]),
        "avg_margin~fun": ([sums[p]["avg_margin"] for p in pids], [ok[p]["ratings"]["fun"] for p in pids]),
        "agency_mean~strategic_depth": ([sums[p]["agency_mean"] for p in pids], [ok[p]["ratings"]["strategic_depth"] for p in pids]),
        "drag_problems~drag_drop_feel": ([sums[p]["misdrops_total"] + sums[p]["drop_retries_total"] + sums[p]["drop_mismatch_total"] for p in pids], [ok[p]["ratings"]["drag_drop_feel"] for p in pids]),
        "frustration_index~nps": ([sums[p]["frustration_index_mean"] for p in pids], [ok[p]["nps"] for p in pids]),
        "pct_turns_using_dice~strategic_depth": ([sums[p]["pct_turns_using_dice"] for p in pids], [ok[p]["ratings"]["strategic_depth"] for p in pids]),
    }
    agg["obj_vs_subj_spearman_n10"] = {k: spearman(a, b) for k, (a, b) in pairs.items()}
    # themes across personas (unflagged items only count as "grounded")
    th = defaultdict(lambda: {"like_personas": set(), "frustration_personas": set(), "grounded_like": set(), "grounded_frustration": set()})
    for p, c in cons.get("personas", {}).items():
        for it in c.get("items", []):
            if it["kind"] == "quote":
                continue
            for name, pat in THEMES.items():
                if re.search(pat, it["text"].lower()):
                    th[name][it["kind"] + "_personas"].add(p)
                    if not it["flagged"]:
                        th[name]["grounded_" + it["kind"]].add(p)
    agg["themes"] = {k: {kk: len(vv) for kk, vv in v.items()} for k, v in sorted(th.items(), key=lambda kv: -len(kv[1]["like_personas"] | kv[1]["frustration_personas"]))}
    agg["consistency"] = cons.get("summary")
    agg["cvd"] = cvd.get("pairs")
    json.dump(agg, open(os.path.join(RAW, "aggregate.json"), "w"), indent=2, default=list)

    # ---- markdown tables ----
    L = []
    L.append("| Persona | Policy | Win rate | Avg margin | Flips +/match (place+slide) | Flips −/match | Dice turns % | Slide turns % | Decision ms (mean) | Misdrop/retry/mismatch | Agency | Zero-choice turns % | Frustration idx | Would quit at |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p, s in sums.items():
        L.append(f"| {s['name']} | {s['params']['policy']} | {s['wins']}/{s['matches']} ({round(100*s['win_rate'])}%) | {s['avg_margin']} | "
                 f"{s['avg_flips_gained_per_match']}+{s['avg_slide_flips_per_match']} | {s['avg_flips_lost_per_match']} | {round(100*s['pct_turns_using_dice'])} | "
                 f"{round(100*s['pct_turns_using_slide'])} | {round(s['decision_latency_ms_mean'])} | {s['misdrops_total']}/{s['drop_retries_total']}/{s['drop_mismatch_total']} | "
                 f"{s['agency_mean']} | {round(100*s['pct_turns_zero_decision_space'])} | {s['frustration_index_mean']} | {s['would_quit_at_match'] or '—'} |")
    L.append("")
    L.append("| Persona (SYNTHETIC ratings) | " + " | ".join(RK) + " | NPS | flagged items |")
    L.append("|---|" + "---|" * (len(RK) + 2))
    for p, f in ok.items():
        c = cons.get("personas", {}).get(p, {})
        L.append(f"| {sums[p]['name']} | " + " | ".join(str(f["ratings"][k]) for k in RK) + f" | {f['nps']} | {c.get('n_flagged','?')}/{c.get('n_items','?')} |")
    if ok:
        L.append("| **mean (sd)** | " + " | ".join(f"{disp[k]['mean']} ({disp[k]['sd']})" for k in RK) + f" | {round(st.mean(npsv),1)} | |")
    open(os.path.join(RAW, "report_tables.md"), "w").write("\n".join(L) + "\n")
    print(json.dumps({k: agg[k] for k in ("pooled", "per_stage", "mirofish", "dice_effect", "dice_usage_split", "slide_usage_split", "drag")}, indent=1, default=list))


if __name__ == "__main__":
    main()
