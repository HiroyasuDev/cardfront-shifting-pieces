"""Shared helpers: turn a persona's objective telemetry summary into plain-text facts.

These facts are the ONLY grounding given to the feedback LLM and the context used by the Jev judge.
"""

GAME_FACTS = (
    "GAME FACTS (from the game's source code): Cardfront: Cradle of Echoes is a single-player browser card duel on a 3x3 board "
    "versus a boss AI. You hold 5 hero cards; each card has 4 edge numbers (top/right/bottom/left). Placing a card next to an "
    "enemy card flips it to your side if your touching edge number is higher. The boss starts with one card on the top-middle "
    "tile and replies after each of your moves by placing the card that flips the most of yours. Each of 3 columns has a die; "
    "a die showing 4-6 gives your cards in that column +1 on all edges. You can nudge a die +1 (2 nudges, +1 per boss turn, "
    "max 3) or reroll all dice (2 per match). Once per turn you can drag one of your board cards to an adjacent empty tile "
    "(Tactical Slide), which can also flip cards. Cards are deployed by dragging from the hand onto a tile (or click card then tile). "
    "A match ends when the board is full (you place 4 cards, so 1 hand card always goes unused); you win with more blue (yours) "
    "than red (boss) cards. There are 4 stages; stages 3 and 4 give boss cards +1 on all edges. Ownership is shown by a cyan "
    "(yours) vs red (boss) card frame. There is no deck building, no collection/progression, no multiplayer, no timer, and no "
    "Same/Plus/Combo rules."
)


def facts(s):
    ps = s["per_stage"]
    stage_txt = "; ".join(f"stage {k}: {v['wins']}/{v['matches']} wins, avg final margin {v['avg_margin']}" for k, v in ps.items())
    lost_kind = s["cards_lost_by_tile_kind"] or {}
    lines = [
        f"SESSION TELEMETRY for {s['name']} ({s['archetype']}), measured in a real browser session:",
        f"- Played {s['matches']} full matches across 4 stages: {s['wins']} wins, {s['losses']} losses (win rate {round(100*s['win_rate'])}%).",
        f"- Per stage: {stage_txt}.",
        f"- Average final board: {s['avg_final_blue']} blue vs {s['avg_final_red']} red; closest match margin {s['min_margin']}."
        + (f" Losses: {', '.join(l['match'] + ' (' + l['score'] + ')' for l in s['loss_list'])}." if s['loss_list'] else " No losses."),
        f"- Flipped on average {s['avg_flips_gained_per_match']} boss cards per match by placement and {s['avg_slide_flips_per_match']} by Tactical Slide; "
        f"the boss flipped back {s['avg_flips_lost_per_match']} of the player's cards per match.",
        f"- Cards lost by tile type: corner {lost_kind.get('corner', 0)}, edge {lost_kind.get('edge', 0)}, center {lost_kind.get('center', 0)}; "
        f"by turn: {s['cards_lost_by_turn'] or 'none'}.",
        f"- Dice: {s['nudges_total']} nudges and {s['rerolls_total']} rerolls in total; dice used on {round(100*s['pct_turns_using_dice'])}% of turns. "
        f"Tactical Slide used on {round(100*s['pct_turns_using_slide'])}% of turns ({s['slides_total']} slides).",
        f"- Average decision time {round(s['decision_latency_ms_mean'])} ms per turn; average drag gesture {round(s['drag_ms_mean'])} ms.",
        f"- Drag & drop: {s['misdrops_total']} cards released off the board (sprang back), {s['drop_retries_total']} failed drops needing a retry, "
        f"{s['drop_mismatch_total']} drops that landed on a different tile than intended.",
        f"- Agency: on average the chosen move achieved {s['agency_mean']} of the best-vs-worst outcome range (1.0 = always best); "
        f"average outcome spread between best and worst move {s['decision_space_mean']} cards; {round(100*s['pct_turns_zero_decision_space'])}% of turns had no meaningful choice.",
        f"- Played {s['distinct_heroes_played']} of 8 distinct hero cards; {s['unused_hand_cards_per_match']} hand card(s) left unused every match.",
        f"- Mean frustration index {s['frustration_index_mean']} (0-1 scale); "
        + (f"patience ran out at match {s['would_quit_at_match']} (would have quit)." if s['would_quit_at_match'] else "never reached the quit threshold."),
    ]
    if s["ownership_misreads_total"]:
        lines.append(f"- Misjudged card ownership (colour confusion model) {s['ownership_misreads_total']} times while planning.")
    if s["random_moves_total"]:
        lines.append(f"- Made {s['random_moves_total']} careless/random moves.")
    return "\n".join(lines)
