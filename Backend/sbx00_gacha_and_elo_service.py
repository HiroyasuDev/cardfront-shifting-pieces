#!/usr/bin/env python3
"""
Backend/sbx00_gacha_and_elo_service.py
======================================
CARDFRONT 3D: Cradle of Echoes — Live SQLite Booster Pack Opening (Gacha),
Player Collection Ledger & K-32 Ranked ELO Ladder Service backed by
`Datasets/cardfront_sovereign_franchise_sbx00.sqlite3` (and synced with
`SBX00:/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/db/cardfront_sovereign_franchise_sbx00.sqlite3`).

Provides deterministic, fast functions callable by `WebPlayable/serve_playtest.py` and CLI:
  - `open_booster_pack(set_code="CF01", pack_type="EVOLVE_SR_COLLECTOR_PACK", player_id="SovereignArchitect")`
  - `record_elo_match(player_id="SovereignArchitect", opponent_id="GrandDirectorAI", winner="player", turns_played=5, evolve_triggered=True)`
  - `get_collection_and_elo_summary(player_id="SovereignArchitect")`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "Datasets"
SQLITE_DB_PATH = DATASETS_DIR / "cardfront_sovereign_franchise_sbx00.sqlite3"

K_FACTOR_ELO = 32
PITY_TIMER_MAX_PACKS = 10


def _connect_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target = db_path or SQLITE_DB_PATH
    conn = sqlite3.connect(str(target), timeout=15.0)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_transactional_tables_exist(conn: sqlite3.Connection) -> None:
    """Ensures the 3 transactional Gacha, Collection & ELO tables exist."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS player_collection_ledger (
            player_id TEXT NOT NULL,
            card_id TEXT NOT NULL,
            title TEXT NOT NULL,
            rarity TEXT NOT NULL,
            foil_finish TEXT NOT NULL,
            copies_owned INTEGER NOT NULL DEFAULT 1,
            is_evolved_unlocked INTEGER NOT NULL DEFAULT 0,
            chibi_unit_id TEXT NOT NULL,
            first_acquired_utc TEXT NOT NULL,
            PRIMARY KEY (player_id, card_id)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS gacha_pack_pulls_history (
            pull_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            set_code TEXT NOT NULL,
            pack_type TEXT NOT NULL,
            pity_counter_after INTEGER NOT NULL,
            guaranteed_sr_hit INTEGER NOT NULL,
            ur_or_evolve_hit INTEGER NOT NULL,
            pulled_cards_json TEXT NOT NULL,
            pulled_at_utc TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ranked_elo_match_history (
            match_id TEXT PRIMARY KEY,
            season_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            opponent_id TEXT NOT NULL,
            player_elo_before INTEGER NOT NULL,
            player_elo_after INTEGER NOT NULL,
            elo_delta INTEGER NOT NULL,
            winner TEXT NOT NULL,
            turns_played INTEGER NOT NULL,
            evolve_triggered INTEGER NOT NULL,
            board_hash_hex TEXT NOT NULL,
            played_at_utc TEXT NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()


def _classify_card_rarity_and_foil(card_row: Dict[str, Any], slot_role: str) -> Dict[str, str]:
    cid = str(card_row.get("card_id", ""))
    tier = int(card_row.get("tier", 3))
    if cid.startswith("ev_") or cid.startswith("herald_"):
        return {"rarity": "UR_EVOLVE", "foil_finish": "25D_PARALLAX_GOLD_UR"}
    if slot_role == "UR_GUARANTEED" or tier >= 5 or cid.startswith("pxg_") or cid.startswith("plugin_"):
        return {"rarity": "UR", "foil_finish": "25D_PARALLAX_GOLD_UR"}
    if slot_role == "SR_SLOT" or tier == 4 or cid.startswith("set2_"):
        return {"rarity": "SR", "foil_finish": "GUNMETAL_SR_PRISM"}
    if tier == 3:
        return {"rarity": "RARE", "foil_finish": "ASTRAL_CYAN_FOIL"}
    return {"rarity": "COMMON", "foil_finish": "STANDARD_MATTE"}


def _resolve_ladder_tier(elo_rating: int) -> str:
    if elo_rating >= 1800:
        return "SOVEREIGN_GRANDMASTER"
    if elo_rating >= 1650:
        return "DIAMOND_KUBRART"
    if elo_rating >= 1525:
        return "GOLD_IVALICE"
    if elo_rating >= 1400:
        return "SILVER_VANGUARD"
    return "BRONZE_INITIATE"


def open_booster_pack(
    set_code: str = "CF01",
    pack_type: str = "EVOLVE_SR_COLLECTOR_PACK",
    player_id: str = "SovereignArchitect",
    seed: Optional[int] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Draws an 8-card booster pack from the 141 canonical cards in `cardfront_sovereign_franchise_sbx00.sqlite3`:
      - Slots 1-5: 5 Common / Rare tactical units
      - Slots 6-7: 2 Foil / Super Rare (SR) units
      - Slot 8:    1 Guaranteed SR/UR or Paired Evolve Mech-Wing Maiden / 10-Yr Herald (with 10-pack UR Pity Timer)
    Persists the pull in `gacha_pack_pulls_history` and updates `player_collection_ledger`.
    """
    conn = _connect_db(db_path)
    try:
        ensure_transactional_tables_exist(conn)
        cur = conn.cursor()

        all_cards = [dict(r) for r in cur.execute("SELECT * FROM canonical_cards_catalog ORDER BY card_id").fetchall()]
        if not all_cards:
            raise RuntimeError("canonical_cards_catalog is empty; run provision_sbx00_sovereign_franchise_db.py first.")

        evolve_pairs_map: Dict[str, Dict[str, Any]] = {}
        try:
            for r in cur.execute("SELECT * FROM evolve_mech_wing_pairs").fetchall():
                d = dict(r)
                evolve_pairs_map[d["base_card_id"]] = d
                evolve_pairs_map[d["evolved_card_id"]] = d
        except sqlite3.OperationalError:
            pass

        last_pull_row = cur.execute(
            "SELECT pity_counter_after FROM gacha_pack_pulls_history WHERE player_id = ? ORDER BY pulled_at_utc DESC, rowid DESC LIMIT 1",
            (player_id,),
        ).fetchone()
        pity_before = int(last_pull_row["pity_counter_after"]) if last_pull_row else 4
        total_pulls_before = cur.execute(
            "SELECT COUNT(*) AS cnt FROM gacha_pack_pulls_history WHERE player_id = ?",
            (player_id,),
        ).fetchone()["cnt"]

        rng_seed = seed if seed is not None else int(time.time() * 1000) + int(total_pulls_before) * 137
        rng = random.Random(rng_seed)

        # Normalize set filter for biased rate-up while keeping full 141-card pool accessible
        norm_set = set_code.upper().strip()
        if norm_set in ("CF01", "SET1", "SET_01"):
            rate_up_set = "SET_01"
        elif norm_set in ("CF02", "SET2", "SET_02", "KUBRART"):
            rate_up_set = "SET_02"
        elif norm_set in ("EVOLVE", "SET_07", "MECH_WING"):
            rate_up_set = "SET_07"
        else:
            rate_up_set = norm_set

        common_rare_pool = [c for c in all_cards if int(c.get("tier", 3)) <= 3 and not str(c["card_id"]).startswith("ev_")]
        if len(common_rare_pool) < 10:
            common_rare_pool = all_cards[:]

        sr_pool = [
            c
            for c in all_cards
            if int(c.get("tier", 3)) == 4 or str(c["card_id"]).startswith("set2_") or str(c["card_id"]).startswith("skill_")
        ]
        if len(sr_pool) < 5:
            sr_pool = all_cards[:]

        ur_evolve_pool = [
            c
            for c in all_cards
            if str(c["card_id"]).startswith("ev_")
            or str(c["card_id"]).startswith("herald_")
            or str(c["card_id"]).startswith("pxg_")
            or str(c["card_id"]).startswith("plugin_")
            or int(c.get("tier", 3)) >= 5
        ]
        if not ur_evolve_pool:
            ur_evolve_pool = all_cards[:]

        # Bias rate-up set cards if available
        rate_up_cr = [c for c in common_rare_pool if c.get("set_code") == rate_up_set]
        if len(rate_up_cr) >= 5:
            common_rare_pool = rate_up_cr + common_rare_pool

        pulled_cards: List[Dict[str, Any]] = []
        used_ids = set()

        # Slots 1-5: Common / Rare
        for slot_idx in range(1, 6):
            candidates = [c for c in common_rare_pool if c["card_id"] not in used_ids] or common_rare_pool
            chosen = rng.choice(candidates)
            used_ids.add(chosen["card_id"])
            rf = _classify_card_rarity_and_foil(chosen, "COMMON_RARE")
            pulled_cards.append(
                {
                    "slot": slot_idx,
                    "card_id": chosen["card_id"],
                    "name": chosen["name"],
                    "set_code": chosen["set_code"],
                    "faction": chosen["faction"],
                    "cost": chosen["cost"],
                    "nesw": [chosen["rank_n"], chosen["rank_e"], chosen["rank_s"], chosen["rank_w"]],
                    "rarity": rf["rarity"],
                    "foil_finish": rf["foil_finish"],
                    "portrait_path": chosen["portrait_path"],
                    "sakuga_strip_path": chosen["sakuga_strip_path"],
                    "chibi_unit_id": f"chibi_{chosen['card_id']}",
                }
            )

        # Slots 6-7: 2 Foil / Super Rare (SR)
        for slot_idx in (6, 7):
            candidates = [c for c in sr_pool if c["card_id"] not in used_ids] or sr_pool
            chosen = rng.choice(candidates)
            used_ids.add(chosen["card_id"])
            rf = _classify_card_rarity_and_foil(chosen, "SR_SLOT")
            pulled_cards.append(
                {
                    "slot": slot_idx,
                    "card_id": chosen["card_id"],
                    "name": chosen["name"],
                    "set_code": chosen["set_code"],
                    "faction": chosen["faction"],
                    "cost": chosen["cost"],
                    "nesw": [chosen["rank_n"], chosen["rank_e"], chosen["rank_s"], chosen["rank_w"]],
                    "rarity": rf["rarity"],
                    "foil_finish": rf["foil_finish"],
                    "portrait_path": chosen["portrait_path"],
                    "sakuga_strip_path": chosen["sakuga_strip_path"],
                    "chibi_unit_id": f"chibi_{chosen['card_id']}",
                }
            )

        # Slot 8: Guaranteed SR/UR or Paired Evolve Mech-Wing Maiden (with 10-Pack UR Pity Timer)
        is_pity_triggered = (pity_before + 1) >= PITY_TIMER_MAX_PACKS
        is_collector_ur_hit = (
            is_pity_triggered
            or "EVOLVE" in pack_type.upper()
            or "UR" in pack_type.upper()
            or rng.random() < 0.45
        )

        if is_collector_ur_hit:
            evolve_only = [c for c in ur_evolve_pool if str(c["card_id"]).startswith("ev_")]
            slot8_pool = evolve_only if ("EVOLVE" in pack_type.upper() and evolve_only) else ur_evolve_pool
            candidates = [c for c in slot8_pool if c["card_id"] not in used_ids] or slot8_pool
            chosen8 = rng.choice(candidates)
            rf8 = _classify_card_rarity_and_foil(chosen8, "UR_GUARANTEED")
            ur_or_evolve_hit = 1
            pity_after = 0
        else:
            candidates = [c for c in sr_pool if c["card_id"] not in used_ids] or sr_pool
            chosen8 = rng.choice(candidates)
            rf8 = _classify_card_rarity_and_foil(chosen8, "SR_SLOT")
            ur_or_evolve_hit = 0
            pity_after = pity_before + 1

        slot8_entry: Dict[str, Any] = {
            "slot": 8,
            "card_id": chosen8["card_id"],
            "name": chosen8["name"],
            "set_code": chosen8["set_code"],
            "faction": chosen8["faction"],
            "cost": chosen8["cost"],
            "nesw": [chosen8["rank_n"], chosen8["rank_e"], chosen8["rank_s"], chosen8["rank_w"]],
            "rarity": rf8["rarity"],
            "foil_finish": rf8["foil_finish"],
            "portrait_path": chosen8["portrait_path"],
            "sakuga_strip_path": chosen8["sakuga_strip_path"],
            "chibi_unit_id": f"chibi_{chosen8['card_id']}",
        }
        if chosen8["card_id"] in evolve_pairs_map:
            pair_info = evolve_pairs_map[chosen8["card_id"]]
            slot8_entry["evolve_pair"] = {
                "pair_id": pair_info["pair_id"],
                "base_card_id": pair_info["base_card_id"],
                "evolved_card_id": pair_info["evolved_card_id"],
                "evolve_cost_ep": pair_info["evolve_cost_ep"],
                "trait": pair_info["trait"],
                "on_evolve_effect": pair_info["on_evolve_effect"],
            }
        pulled_cards.append(slot8_entry)

        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        pull_id = f"pull_{int(time.time() * 1000)}_{hashlib.sha256(f'{player_id}:{rng_seed}'.encode()).hexdigest()[:8]}"

        cur.execute(
            """
            INSERT INTO gacha_pack_pulls_history (
                pull_id, player_id, set_code, pack_type, pity_counter_after,
                guaranteed_sr_hit, ur_or_evolve_hit, pulled_cards_json, pulled_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                pull_id,
                player_id,
                set_code,
                pack_type,
                pity_after,
                1,
                ur_or_evolve_hit,
                json.dumps(pulled_cards),
                now_utc,
            ),
        )

        # Upsert each pulled card into player_collection_ledger
        for pc in pulled_cards:
            cid = pc["card_id"]
            is_ev = 1 if (cid.startswith("ev_") or "evolve_pair" in pc) else 0
            existing = cur.execute(
                "SELECT copies_owned, is_evolved_unlocked FROM player_collection_ledger WHERE player_id = ? AND card_id = ?",
                (player_id, cid),
            ).fetchone()
            if existing:
                cur.execute(
                    """
                    UPDATE player_collection_ledger
                    SET copies_owned = copies_owned + 1,
                        is_evolved_unlocked = MAX(is_evolved_unlocked, ?),
                        foil_finish = CASE WHEN ? = '25D_PARALLAX_GOLD_UR' THEN '25D_PARALLAX_GOLD_UR' ELSE foil_finish END
                    WHERE player_id = ? AND card_id = ?;
                    """,
                    (is_ev, pc["foil_finish"], player_id, cid),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO player_collection_ledger (
                        player_id, card_id, title, rarity, foil_finish,
                        copies_owned, is_evolved_unlocked, chibi_unit_id, first_acquired_utc
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?);
                    """,
                    (
                        player_id,
                        cid,
                        pc["name"],
                        pc["rarity"],
                        pc["foil_finish"],
                        is_ev,
                        pc["chibi_unit_id"],
                        now_utc,
                    ),
                )

        conn.commit()
        cur.close()
    finally:
        conn.close()

    summary = get_collection_and_elo_summary(player_id=player_id, db_path=db_path)
    return {
        "status": "PASS_BOOSTER_PACK_OPENED",
        "pull_id": pull_id,
        "player_id": player_id,
        "set_code": set_code,
        "pack_type": pack_type,
        "pack_size": len(pulled_cards),
        "guaranteed_sr_hit": True,
        "ur_or_evolve_hit": bool(ur_or_evolve_hit),
        "pity_counter_before": pity_before,
        "pity_counter_after": pity_after,
        "pity_timer_max": PITY_TIMER_MAX_PACKS,
        "pulled_cards": pulled_cards,
        "pulled_at_utc": now_utc,
        "collection_summary": {
            "unique_cards_owned": summary["unique_cards_owned"],
            "total_canonical_cards": summary["total_canonical_cards"],
            "total_copies_owned": summary["total_copies_owned"],
            "pack_pulls_count": summary["pack_pulls_count"],
        },
    }


def record_elo_match(
    player_id: str = "SovereignArchitect",
    opponent_id: str = "GrandDirectorAI",
    winner: str = "player",
    turns_played: int = 5,
    evolve_triggered: bool = True,
    opponent_elo: int = 1620,
    season_id: str = "SEASON_01_CRADLE_ECLIPSE",
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Computes a standard K-32 ELO rating update, inserts a row into `ranked_elo_match_history`,
    and returns the updated ELO rating and ladder tier.
    """
    conn = _connect_db(db_path)
    try:
        ensure_transactional_tables_exist(conn)
        cur = conn.cursor()

        last_match = cur.execute(
            "SELECT player_elo_after FROM ranked_elo_match_history WHERE player_id = ? ORDER BY played_at_utc DESC, rowid DESC LIMIT 1",
            (player_id,),
        ).fetchone()
        elo_before = int(last_match["player_elo_after"]) if last_match else 1500

        expected_score = 1.0 / (1.0 + math.pow(10.0, (float(opponent_elo) - float(elo_before)) / 400.0))
        w_norm = str(winner).strip().lower()
        if w_norm in ("player", player_id.lower(), "1", "true", "win", "victory"):
            actual_score = 1.0
            winner_label = "player"
        elif w_norm in ("draw", "tie", "0.5"):
            actual_score = 0.5
            winner_label = "draw"
        else:
            actual_score = 0.0
            winner_label = "opponent"

        elo_delta = int(round(K_FACTOR_ELO * (actual_score - expected_score)))
        if winner_label == "player" and elo_delta < 4:
            elo_delta = 4
        elo_after = max(800, elo_before + elo_delta)

        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        board_hash_hex = hashlib.sha256(
            f"{player_id}:{opponent_id}:{elo_before}:{elo_after}:{turns_played}:{now_utc}".encode("utf-8")
        ).hexdigest()[:16]
        match_id = f"match_{int(time.time() * 1000)}_{board_hash_hex[:8]}"

        cur.execute(
            """
            INSERT INTO ranked_elo_match_history (
                match_id, season_id, player_id, opponent_id,
                player_elo_before, player_elo_after, elo_delta,
                winner, turns_played, evolve_triggered, board_hash_hex, played_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                match_id,
                season_id,
                player_id,
                opponent_id,
                elo_before,
                elo_after,
                elo_delta,
                winner_label,
                int(turns_played),
                1 if evolve_triggered else 0,
                board_hash_hex,
                now_utc,
            ),
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    ladder_tier = _resolve_ladder_tier(elo_after)
    return {
        "status": "PASS_ELO_MATCH_RECORDED",
        "match_id": match_id,
        "season_id": season_id,
        "player_id": player_id,
        "opponent_id": opponent_id,
        "winner": winner_label,
        "player_elo_before": elo_before,
        "player_elo_after": elo_after,
        "elo_delta": elo_delta,
        "ladder_tier": ladder_tier,
        "turns_played": int(turns_played),
        "evolve_triggered": bool(evolve_triggered),
        "board_hash_hex": board_hash_hex,
        "played_at_utc": now_utc,
    }


def get_collection_and_elo_summary(
    player_id: str = "SovereignArchitect",
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Returns complete player collection, Gacha pity timer, and Ranked ELO ladder telemetry.
    """
    conn = _connect_db(db_path)
    try:
        ensure_transactional_tables_exist(conn)
        cur = conn.cursor()

        total_canonical = cur.execute("SELECT COUNT(*) AS cnt FROM canonical_cards_catalog").fetchone()["cnt"]
        col_row = cur.execute(
            """
            SELECT
                COUNT(*) AS unique_cards,
                COALESCE(SUM(copies_owned), 0) AS total_copies,
                COALESCE(SUM(CASE WHEN is_evolved_unlocked > 0 THEN 1 ELSE 0 END), 0) AS evolved_unlocked
            FROM player_collection_ledger
            WHERE player_id = ?;
            """,
            (player_id,),
        ).fetchone()

        unique_owned = int(col_row["unique_cards"] or 0)
        total_copies = int(col_row["total_copies"] or 0)
        evolved_unlocked = int(col_row["evolved_unlocked"] or 0)

        pulls_count = cur.execute(
            "SELECT COUNT(*) AS cnt FROM gacha_pack_pulls_history WHERE player_id = ?",
            (player_id,),
        ).fetchone()["cnt"]
        last_pull = cur.execute(
            "SELECT pity_counter_after, set_code, pack_type, pulled_at_utc FROM gacha_pack_pulls_history WHERE player_id = ? ORDER BY pulled_at_utc DESC, rowid DESC LIMIT 1",
            (player_id,),
        ).fetchone()
        current_pity = int(last_pull["pity_counter_after"]) if last_pull else 0

        match_stats = cur.execute(
            """
            SELECT
                COUNT(*) AS total_matches,
                COALESCE(SUM(CASE WHEN winner = 'player' THEN 1 ELSE 0 END), 0) AS wins,
                COALESCE(SUM(CASE WHEN winner != 'player' THEN 1 ELSE 0 END), 0) AS losses
            FROM ranked_elo_match_history
            WHERE player_id = ?;
            """,
            (player_id,),
        ).fetchone()
        total_matches = int(match_stats["total_matches"] or 0)
        wins = int(match_stats["wins"] or 0)
        losses = int(match_stats["losses"] or 0)
        win_rate_pct = round((wins / max(1, total_matches)) * 100.0, 2)

        last_elo_row = cur.execute(
            "SELECT player_elo_after FROM ranked_elo_match_history WHERE player_id = ? ORDER BY played_at_utc DESC, rowid DESC LIMIT 1",
            (player_id,),
        ).fetchone()
        current_elo = int(last_elo_row["player_elo_after"]) if last_elo_row else 1500

        cur.close()
    finally:
        conn.close()

    return {
        "status": "OK",
        "player_id": player_id,
        "unique_cards_owned": unique_owned,
        "total_canonical_cards": int(total_canonical),
        "collection_completion_pct": round((unique_owned / max(1, int(total_canonical))) * 100.0, 2),
        "total_copies_owned": total_copies,
        "evolved_maidens_unlocked": evolved_unlocked,
        "pack_pulls_count": int(pulls_count),
        "current_pity_counter": current_pity,
        "pity_timer_max": PITY_TIMER_MAX_PACKS,
        "current_elo_rating": current_elo,
        "ladder_tier": _resolve_ladder_tier(current_elo),
        "matches_played": total_matches,
        "wins": wins,
        "losses": losses,
        "win_rate_pct": win_rate_pct,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="SBX00 Gacha Booster Pack & Ranked ELO Service CLI")
    parser.add_argument("--action", choices=["summary", "open-pack", "record-match"], default="summary")
    parser.add_argument("--player-id", default="SovereignArchitect")
    parser.add_argument("--set-code", default="CF01")
    parser.add_argument("--pack-type", default="EVOLVE_SR_COLLECTOR_PACK")
    parser.add_argument("--opponent-id", default="GrandDirectorAI")
    parser.add_argument("--winner", default="player")
    parser.add_argument("--turns", type=int, default=5)
    args = parser.parse_args()

    if args.action == "open-pack":
        out = open_booster_pack(set_code=args.set_code, pack_type=args.pack_type, player_id=args.player_id)
    elif args.action == "record-match":
        out = record_elo_match(
            player_id=args.player_id,
            opponent_id=args.opponent_id,
            winner=args.winner,
            turns_played=args.turns,
            evolve_triggered=True,
        )
    else:
        out = get_collection_and_elo_summary(player_id=args.player_id)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
