#!/usr/bin/env python3
"""Consistency gate: is each SYNTHETIC feedback item supported by that persona's real telemetry?

Two independent checks per item (likes, frustrations, quote):
  1. jevmlx.judge (same engine behind the `mlx_jev_judge` MCP tool), model "fast"
     (mlx-community/Qwen2.5-3B-Instruct-4bit), context = GAME_FACTS + persona telemetry facts.
  2. Deterministic contradiction rules against the telemetry numbers (keyword-triggered).
An item is flagged HALLUCINATED/UNSUPPORTED if the Jev verdict is False (p<0.5) or a rule fires.
Ratings get rule-based plausibility notes (e.g. difficulty vs win rate).

Output: feedback/feedback_consistency.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facts import GAME_FACTS, facts  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("JEV_MODEL", "fast")


def rule_checks(text, s):
    t = text.lower()
    fired = []
    absent = {
        r"deck[- ]?build": "no deck building exists", r"multiplayer|pvp|online|ranked|ladder|matchmak": "no multiplayer/ranked",
        r"\btimer\b|time limit|countdown": "no timer exists", r"\bsame\b rule|\bplus\b rule|\bcombo(s)?\b rule|chain reaction": "no Same/Plus/Combo rules",
        r"collect(ion|ing)|unlock|progression|loot|pack(s)?\b": "no collection/progression/unlocks",
        r"tutorial": "no tutorial exists", r"sound|music|audio": "audio not measured in headless run",
    }
    for pat, why in absent.items():
        if re.search(pat, t) and not re.search(r"\b(no|lack|missing|without|wish|want|need|absence|would like)\b", t):
            fired.append(f"claims feature/experience not present: {why}")
    if s["losses"] == 0 and re.search(r"\b(lost|losing|defeat|beat me|crushed)\b", t) and not re.search(r"\b(never|no|didn't|without)\b", t):
        fired.append("mentions losing but persona had 0 losses")
    if s["wins"] == 0 and re.search(r"\b(won|winning|victory|victories)\b", t):
        fired.append("mentions winning but persona had 0 wins")
    if s["nudges_total"] + s["rerolls_total"] == 0 and re.search(r"\b(dice|die|nudg|reroll|roll)", t) and not re.search(r"\b(never|didn't|did not|ignored|unused|confus|unclear|no idea)\b", t):
        fired.append("describes using dice but persona never used dice")
    if s["slides_total"] == 0 and re.search(r"\bslid(e|ing)\b", t) and not re.search(r"\b(never|didn't|did not|ignored|unused|confus|unclear)\b", t):
        fired.append("describes sliding but persona never slid")
    if s["misdrops_total"] + s["drop_retries_total"] + s["drop_mismatch_total"] == 0 and re.search(r"(misdrop|drop(s|ped)? (fail|miss)|wrong tile|snap(ped)? back|spr(a|u)ng back)", t):
        fired.append("complains about failed drops but persona had none")
    return fired


def rating_notes(fb, s):
    n = []
    r = fb.get("ratings", {})
    if s["win_rate"] == 1.0 and s["avg_margin"] >= 4 and r.get("difficulty_fairness", 0) >= 9:
        n.append("difficulty_fairness>=9 despite 100% wins with avg margin >= 4 (game was very easy for this persona)")
    if s["drop_retries_total"] + s["drop_mismatch_total"] + s["misdrops_total"] >= 3 and r.get("drag_drop_feel", 0) >= 9:
        n.append("drag_drop_feel>=9 despite >=3 drag problems")
    if s["pct_turns_zero_decision_space"] is not None and s["pct_turns_zero_decision_space"] >= 0.3 and r.get("strategic_depth", 0) >= 9:
        n.append("strategic_depth>=9 though >=30% of turns had no meaningful choice")
    if fb.get("nps", 0) >= 9 and s["would_quit_at_match"]:
        n.append("NPS>=9 although the persona's patience model hit its quit threshold")
    return n


def main():
    from jevmlx import judge

    sums = json.load(open(os.path.join(ROOT, "raw", "persona_summaries.json")))
    fbs = json.load(open(os.path.join(ROOT, "feedback", "persona_feedback.json")))["feedback"]
    out = {"_note": "Consistency check of SYNTHETIC feedback vs REAL telemetry. judge model: jevmlx '" + MODEL + "'", "personas": {}}
    for pid, fb in fbs.items():
        s = sums[pid]
        if not fb.get("likes"):
            out["personas"][pid] = {"error": "no parsed feedback"}
            continue
        ctx = GAME_FACTS + "\n\n" + facts(s)
        items = [("like", x) for x in fb["likes"]] + [("frustration", x) for x in fb["frustrations"]] + [("quote", fb["quote"])]
        res = []
        for kind, text in items:
            prop = (f"The playtester's {kind} statement \"{text}\" is consistent with the game facts and this player's session "
                    "telemetry: it does not describe features, events or numbers that contradict them or that did not happen.")
            j = judge(ctx, prop, model=MODEL)
            rules = rule_checks(text, s)
            jv = bool(j.value)
            res.append({"kind": kind, "text": text, "jev_verdict": jv, "jev_probability": round(float(j.probability), 4),
                        "jev_margin": round(float(j.probability_margin), 4) if j.probability_margin is not None else None,
                        "rule_flags": rules, "flagged": (not jv) or bool(rules)})
            print(pid, kind, "FLAG" if res[-1]["flagged"] else "ok", round(float(j.probability), 3), rules, text[:90])
        out["personas"][pid] = {"name": s["name"], "items": res, "rating_notes": rating_notes(fb, s),
                                "n_items": len(res), "n_flagged": sum(r["flagged"] for r in res)}
    tot = sum(p.get("n_items", 0) for p in out["personas"].values())
    fl = sum(p.get("n_flagged", 0) for p in out["personas"].values())
    out["summary"] = {"items": tot, "flagged": fl, "flag_rate": round(fl / tot, 3) if tot else None}
    json.dump(out, open(os.path.join(ROOT, "feedback", "feedback_consistency.json"), "w"), indent=2, ensure_ascii=False)
    print(out["summary"])


if __name__ == "__main__":
    sys.exit(main())
