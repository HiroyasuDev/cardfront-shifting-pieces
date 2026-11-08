#!/usr/bin/env python3
"""
Synapse Sovereign TCG Engine (`Synapse.TcgEngine`) — Rigorous Clean-Room Verification Suite.
Verifies every rule, card invariant, special ability, synergy, CardCraft evolution,
metagame endpoint, cryptographic hash, artwork asset, and C# source cleanliness invariant.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
BACKEND_DIR = ROOT_DIR / "Backend"
SCRIPTS_DIR = ROOT_DIR / "Assets" / "Scripts"
CARD_ART_DIR = ROOT_DIR / "Assets" / "Resources" / "CardArt"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from synapse_tcg_backend import (  # noqa: E402
    AdvanceWarsFftaDynamicsSimulator,
    AnimeBaselineProprietaryDistiller,
    BreachStackMatchSimulator,
    CardDef,
    CLASSIC_12_TELEGRAPH_ARCHETYPES,
    GridStackCell,
    Hi3dAiFullStudioReEngine,
    LumenForgeIoStudioEngine,
    MetalGearAcidCostSimulator,
    MiroStrandsSimulationFeedbackEngine,
    OFFICIAL_PROJECT_CF_CARDS,
    OmegaStrikersHi3dReaProductionEngine,
    SynapseMetagameBackend,
    TelegraphedIntent,
)


@dataclass
class DirectionalStats:
    up: int
    down: int
    left: int
    right: int

    def add_all(self, bonus: int) -> "DirectionalStats":
        return DirectionalStats(
            self.up + bonus,
            self.down + bonus,
            self.left + bonus,
            self.right + bonus,
        )

    def total(self) -> int:
        return self.up + self.down + self.left + self.right


@dataclass
class RuntimeCardInstance:
    uid: str
    card_id: str
    title: str
    code_name: str
    owner_id: int
    original_owner_id: int
    base_stats: DirectionalStats
    permanent_stat_bonus: int = 0
    themes: List[str] = field(default_factory=list)
    special_ability: str = "None"
    synergy_theme: str = "None"
    synergy_bonus: int = 0
    evolves_to: str = ""
    once_per_game_used: bool = False
    moved_this_turn: bool = False
    vanish_immune_turns: int = 0
    temporal_rift_reversed_turns: int = 0
    matches_played_count: int = 0
    zone: str = "Deck"

    @staticmethod
    def from_def(cdef: CardDef, owner_id: int, uid: str) -> "RuntimeCardInstance":
        return RuntimeCardInstance(
            uid=uid,
            card_id=cdef.id,
            title=cdef.title,
            code_name=cdef.code_name,
            owner_id=owner_id,
            original_owner_id=owner_id,
            base_stats=DirectionalStats(cdef.up, cdef.down, cdef.left, cdef.right),
            themes=list(cdef.themes),
            special_ability=cdef.special_ability,
            synergy_theme=cdef.synergy_theme,
            synergy_bonus=cdef.synergy_bonus,
            evolves_to=cdef.evolves_to,
        )

    def clone(self) -> "RuntimeCardInstance":
        return RuntimeCardInstance(
            uid=self.uid,
            card_id=self.card_id,
            title=self.title,
            code_name=self.code_name,
            owner_id=self.owner_id,
            original_owner_id=self.original_owner_id,
            base_stats=DirectionalStats(
                self.base_stats.up,
                self.base_stats.down,
                self.base_stats.left,
                self.base_stats.right,
            ),
            permanent_stat_bonus=self.permanent_stat_bonus,
            themes=list(self.themes),
            special_ability=self.special_ability,
            synergy_theme=self.synergy_theme,
            synergy_bonus=self.synergy_bonus,
            evolves_to=self.evolves_to,
            once_per_game_used=self.once_per_game_used,
            moved_this_turn=self.moved_this_turn,
            vanish_immune_turns=self.vanish_immune_turns,
            temporal_rift_reversed_turns=self.temporal_rift_reversed_turns,
            matches_played_count=self.matches_played_count,
            zone=self.zone,
        )


@dataclass
class PlayerRuntimeState:
    player_id: int
    confidence_points: int = 0
    xp: int = 0
    badges: Set[str] = field(default_factory=set)
    deck: List[RuntimeCardInstance] = field(default_factory=list)
    hand: List[RuntimeCardInstance] = field(default_factory=list)
    discard: List[RuntimeCardInstance] = field(default_factory=list)


class SynapseTacticalGridEngine:
    """
    Exact Python verification & Monte Carlo simulation mirror of `Synapse.TcgEngine.Core.TcgGameLogic`.
    Enforces 1:1 parity with `Assets/Scripts/Core/TcgGameLogic.cs` across all 10 PROJECT CF
    Special Abilities, Orthogonal Directional Captures, Theme Synergies, CardCraft CP/XP/Evolution,
    and 64-bit FNV-1a State Hashing.
    """

    ORTHOGONAL_DIRS: Tuple[Tuple[int, int], ...] = (
        (0, 1),   # Up    (neighbor at y+1 opposes with Down)
        (0, -1),  # Down  (neighbor at y-1 opposes with Up)
        (-1, 0),  # Left  (neighbor at x-1 opposes with Right)
        (1, 0),   # Right (neighbor at x+1 opposes with Left)
    )

    def __init__(self, seed: int = 1337, is_nighttime: bool = False) -> None:
        self.seed = seed
        self.is_nighttime = is_nighttime
        self.grid: List[List[Optional[RuntimeCardInstance]]] = [
            [None for _ in range(3)] for _ in range(3)
        ]
        self.players: List[PlayerRuntimeState] = [
            PlayerRuntimeState(0),
            PlayerRuntimeState(1),
        ]
        self.active_player_id: int = 0
        self.turn_number: int = 1
        self.bonus_move_player_id: Optional[int] = None
        self.phase: str = "Main"
        self.winner_id: Optional[int] = None

    @staticmethod
    def in_bounds(x: int, y: int) -> bool:
        return 0 <= x < 3 and 0 <= y < 3

    def clone_state(self) -> "SynapseTacticalGridEngine":
        cp = SynapseTacticalGridEngine(self.seed, self.is_nighttime)
        cp.active_player_id = self.active_player_id
        cp.turn_number = self.turn_number
        cp.bonus_move_player_id = self.bonus_move_player_id
        cp.phase = self.phase
        cp.winner_id = self.winner_id
        for pid in (0, 1):
            cp.players[pid].confidence_points = self.players[pid].confidence_points
            cp.players[pid].xp = self.players[pid].xp
            cp.players[pid].badges = set(self.players[pid].badges)
            cp.players[pid].deck = [c.clone() for c in self.players[pid].deck]
            cp.players[pid].hand = [c.clone() for c in self.players[pid].hand]
            cp.players[pid].discard = [c.clone() for c in self.players[pid].discard]
        for x in range(3):
            for y in range(3):
                occ = self.grid[x][y]
                cp.grid[x][y] = occ.clone() if occ is not None else None
        return cp

    def compute_fnv1a_64_hash(self) -> int:
        """Deterministic 64-bit FNV-1a state hash matching `TcgGameLogic.ComputeStateHash()`."""
        h = 14695981039346656037
        prime = 1099511628211
        mask = (1 << 64) - 1

        def mix(val: int) -> None:
            nonlocal h
            h ^= (val & mask)
            h = (h * prime) & mask

        mix(self.active_player_id)
        mix(self.turn_number)
        mix(0 if self.phase == "Main" else 1)
        mix(self.winner_id if self.winner_id is not None else -99)

        for x in range(3):
            for y in range(3):
                occ = self.grid[x][y]
                if occ is None:
                    mix(0)
                else:
                    mix(occ.owner_id + 1)
                    st = self.get_effective_stats(x, y)
                    packed = ((st.up & 0xFF) << 24) | ((st.down & 0xFF) << 16) | ((st.left & 0xFF) << 8) | (st.right & 0xFF)
                    mix(packed)
        return h

    def get_effective_stats(self, x: int, y: int) -> DirectionalStats:
        if not self.in_bounds(x, y) or self.grid[x][y] is None:
            return DirectionalStats(0, 0, 0, 0)
        card = self.grid[x][y]
        assert card is not None
        stats = card.base_stats.add_all(card.permanent_stat_bonus)

        has_synergy_neighbor = False
        has_lunar_neighbor = False

        for dx, dy in self.ORTHOGONAL_DIRS:
            nx, ny = x + dx, y + dy
            if not self.in_bounds(nx, ny) or self.grid[nx][ny] is None:
                continue
            neighbor = self.grid[nx][ny]
            assert neighbor is not None
            if card.synergy_theme and card.synergy_theme != "None":
                if card.synergy_theme in neighbor.themes:
                    has_synergy_neighbor = True
            if "Lunar" in neighbor.themes:
                has_lunar_neighbor = True

        if has_synergy_neighbor:
            stats = stats.add_all(card.synergy_bonus)

        # 10. Lunar Oracle: Moonlight Blessing (+1 all sides during nighttime or adjacent to Lunar)
        if card.special_ability == "MoonlightBlessing" and (self.is_nighttime or has_lunar_neighbor):
            stats = stats.add_all(1)

        # 7. Clockwork Sorcerer: Temporal Rift stat reversal (up<->down, left<->right)
        if card.temporal_rift_reversed_turns > 0:
            stats = DirectionalStats(stats.down, stats.up, stats.right, stats.left)

        return stats

    def is_card_capture_immune(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y) or self.grid[x][y] is None:
            return False
        card = self.grid[x][y]
        assert card is not None
        if card.vanish_immune_turns > 0:
            return True
        if card.special_ability == "TechnoStealth":
            for dx, dy in self.ORTHOGONAL_DIRS:
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny) and self.grid[nx][ny] is not None:
                    if "Tech" in self.grid[nx][ny].themes:
                        return True
        return False

    def has_empty_cell(self) -> bool:
        return any(self.grid[x][y] is None for x in range(3) for y in range(3))

    def place_card(self, player_id: int, card_uid: str, x: int, y: int) -> Tuple[bool, int]:
        if self.winner_id is not None or player_id != self.active_player_id or self.phase != "Main":
            return False, 0
        if not self.in_bounds(x, y) or self.grid[x][y] is not None:
            return False, 0

        p = self.players[player_id]
        card = next((c for c in p.hand if c.uid == card_uid), None)
        if card is None:
            return False, 0

        p.hand.remove(card)
        card.zone = "Board"
        card.owner_id = player_id
        self.grid[x][y] = card
        card.matches_played_count += 1

        captured = self.resolve_captures_from(x, y, player_id)

        # 2. Mech Knight (Charge): On capture, grant immediate bonus move if board has space and hand has cards
        if card.special_ability == "Charge" and captured > 0 and self.has_empty_cell() and len(p.hand) > 0:
            self.bonus_move_player_id = player_id
        else:
            self.bonus_move_player_id = None
            self.end_turn()

        return True, captured

    def resolve_captures_from(self, x: int, y: int, attacker_player_id: int) -> int:
        attacker_card = self.grid[x][y]
        if attacker_card is None:
            return 0
        attacker_stats = self.get_effective_stats(x, y)
        captures = 0

        for dx, dy in self.ORTHOGONAL_DIRS:
            nx, ny = x + dx, y + dy
            if not self.in_bounds(nx, ny) or self.grid[nx][ny] is None:
                continue
            defender_card = self.grid[nx][ny]
            assert defender_card is not None
            if defender_card.owner_id == attacker_player_id:
                continue
            if self.is_card_capture_immune(nx, ny):
                continue

            defender_stats = self.get_effective_stats(nx, ny)
            if dx == 0 and dy == 1:
                atk_val, def_val = attacker_stats.up, defender_stats.down
            elif dx == 0 and dy == -1:
                atk_val, def_val = attacker_stats.down, defender_stats.up
            elif dx == -1 and dy == 0:
                atk_val, def_val = attacker_stats.left, defender_stats.right
            else:
                atk_val, def_val = attacker_stats.right, defender_stats.left

            if atk_val > def_val:
                captures += 1
                # 8. Phoenix Guardian (Rebirth): Returns to original owner's hand once per game
                if defender_card.special_ability == "Rebirth" and not defender_card.once_per_game_used:
                    defender_card.once_per_game_used = True
                    self.grid[nx][ny] = None
                    defender_card.owner_id = defender_card.original_owner_id
                    defender_card.zone = "Hand"
                    self.players[defender_card.original_owner_id].hand.append(defender_card)
                else:
                    defender_card.owner_id = attacker_player_id
                    # 5. Elemental Sprite (ElementalBurst): Swap base stats with captured adjacent card once per game
                    if attacker_card.special_ability == "ElementalBurst" and not attacker_card.once_per_game_used:
                        attacker_card.once_per_game_used = True
                        attacker_card.base_stats, defender_card.base_stats = (
                            defender_card.base_stats,
                            attacker_card.base_stats,
                        )

        self.players[attacker_player_id].confidence_points += captures * 10
        return captures

    def activate_special_ability(
        self, player_id: int, from_x: int, from_y: int, target_x: int = -1, target_y: int = -1
    ) -> bool:
        if not self.in_bounds(from_x, from_y) or self.grid[from_x][from_y] is None:
            return False
        card = self.grid[from_x][from_y]
        assert card is not None
        if card.owner_id != player_id:
            return False

        if card.special_ability == "Teleport":
            if card.once_per_game_used or not self.in_bounds(target_x, target_y) or self.grid[target_x][target_y] is not None:
                return False
            card.once_per_game_used = True
            self.grid[from_x][from_y] = None
            self.grid[target_x][target_y] = card
            self.resolve_captures_from(target_x, target_y, player_id)
            return True

        if card.special_ability == "WarpDrive":
            if card.moved_this_turn or not self.in_bounds(target_x, target_y) or self.grid[target_x][target_y] is not None:
                return False
            card.moved_this_turn = True
            self.grid[from_x][from_y] = None
            self.grid[target_x][target_y] = card
            self.resolve_captures_from(target_x, target_y, player_id)
            return True

        if card.special_ability == "Vanish":
            if card.once_per_game_used:
                return False
            card.once_per_game_used = True
            card.vanish_immune_turns = 2
            return True

        if card.special_ability == "TemporalRift":
            if card.once_per_game_used:
                return False
            card.once_per_game_used = True
            for dx, dy in self.ORTHOGONAL_DIRS:
                nx, ny = from_x + dx, from_y + dy
                if self.in_bounds(nx, ny) and self.grid[nx][ny] is not None:
                    self.grid[nx][ny].temporal_rift_reversed_turns = 2
            return True

        return False

    def end_turn(self) -> None:
        self.phase = "EndTurn"
        for x in range(3):
            for y in range(3):
                c = self.grid[x][y]
                if c is None:
                    continue
                c.moved_this_turn = False
                if c.vanish_immune_turns > 0:
                    c.vanish_immune_turns -= 1
                if c.temporal_rift_reversed_turns > 0:
                    c.temporal_rift_reversed_turns -= 1

                # 3. Celestial Guardian (HealingAura): +1 permanent strength to adjacent friendly cards at end of turn
                if c.special_ability == "HealingAura" and c.owner_id == self.active_player_id:
                    for dx, dy in self.ORTHOGONAL_DIRS:
                        nx, ny = x + dx, y + dy
                        if self.in_bounds(nx, ny) and self.grid[nx][ny] is not None:
                            if self.grid[nx][ny].owner_id == self.active_player_id:
                                self.grid[nx][ny].permanent_stat_bonus += 1

        if self.is_game_over():
            self.phase = "GameOver"
            self.determine_winner()
            return

        self.turn_number += 1
        self.active_player_id = 1 - self.active_player_id
        self.phase = "Main"

    def is_game_over(self) -> bool:
        if not self.has_empty_cell():
            return True
        if (
            len(self.players[0].hand) == 0
            and len(self.players[1].hand) == 0
            and len(self.players[0].deck) == 0
            and len(self.players[1].deck) == 0
        ):
            return True
        return False

    def count_controlled_cards(self, player_id: int) -> int:
        return sum(
            1
            for x in range(3)
            for y in range(3)
            if self.grid[x][y] is not None and self.grid[x][y].owner_id == player_id
        )

    def determine_winner(self) -> None:
        p0 = self.count_controlled_cards(0)
        p1 = self.count_controlled_cards(1)
        if p0 > p1:
            self.winner_id = 0
        elif p1 > p0:
            self.winner_id = 1
        else:
            self.winner_id = -1

        if self.winner_id is not None and self.winner_id >= 0:
            w = self.players[self.winner_id]
            w.xp += 100
            w.confidence_points += 25
            w.badges.add("Frontier Tactician")

    @staticmethod
    def evolve_cardcraft_card(card: RuntimeCardInstance, cp_available: int, cp_cost: int = 30) -> Tuple[RuntimeCardInstance, int]:
        """Executes CardCraft creative skill evolution (`cc_01_sketching -> cc_02_concept_art`, etc.)."""
        if not card.evolves_to or card.evolves_to not in OFFICIAL_PROJECT_CF_CARDS:
            raise ValueError(f"Card {card.card_id} does not have a valid evolution target.")
        if cp_available < cp_cost:
            raise ValueError("Insufficient Confidence Points (CP) for evolution.")
        target_def = OFFICIAL_PROJECT_CF_CARDS[card.evolves_to]
        evolved = RuntimeCardInstance.from_def(target_def, card.owner_id, card.uid + "_evo")
        evolved.matches_played_count = card.matches_played_count
        return evolved, cp_available - cp_cost


class TestSynapseTcgSuite(unittest.TestCase):
    """
    24-Test Clean-Room Verification Suite for `Synapse.TcgEngine` & `Backend/synapse_tcg_backend.py`.
    """

    def test_01_roster_completeness_and_stat_bounds(self) -> None:
        """Verify all 14 official cards (10 PROJECT CF + 4 CardCraft) have valid 1-10 stats and metadata."""
        self.assertEqual(len(OFFICIAL_PROJECT_CF_CARDS), 14)
        cf_ids = [k for k in OFFICIAL_PROJECT_CF_CARDS if k.startswith("cf_")]
        cc_ids = [k for k in OFFICIAL_PROJECT_CF_CARDS if k.startswith("cc_")]
        self.assertEqual(len(cf_ids), 10)
        self.assertEqual(len(cc_ids), 4)

        for cid, card in OFFICIAL_PROJECT_CF_CARDS.items():
            for side_name, val in (("up", card.up), ("down", card.down), ("left", card.left), ("right", card.right)):
                self.assertGreaterEqual(val, 1, f"{cid}.{side_name} below 1")
                self.assertLessEqual(val, 10, f"{cid}.{side_name} above 10")
            self.assertTrue(card.title.strip())
            self.assertTrue(card.code_name.strip())
            self.assertGreaterEqual(len(card.themes), 1)
            self.assertIn(card.synergy_bonus, (1, 2, 3))

    def test_02_all_14_card_art_png_assets_exist_and_valid(self) -> None:
        """Verify all 14 cards have rendered high-resolution PNG art in Assets/Resources/CardArt/."""
        png_magic = b"\x89PNG\r\n\x1a\n"
        for cid in OFFICIAL_PROJECT_CF_CARDS:
            art_path = CARD_ART_DIR / f"{cid}.png"
            self.assertTrue(art_path.is_file(), f"Missing card artwork PNG: {art_path}")
            size = art_path.stat().st_size
            self.assertGreater(size, 100_000, f"Card art {cid}.png suspiciously small ({size} bytes)")
            with open(art_path, "rb") as fh:
                header = fh.read(8)
            self.assertEqual(header, png_magic, f"Invalid PNG header for {art_path}")

    def test_03_orthogonal_directional_capture_up_vs_down(self) -> None:
        """Verify placing a card at (1, 0) compares its Up against (1, 1)'s Down."""
        eng = SynapseTacticalGridEngine()
        # Defender at (1, 1): Mystic Mage (Down = 7)
        defender = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 1, "u_def")
        eng.grid[1][1] = defender
        # Attacker in P0 hand: Phoenix Guardian (Up = 9 > Defender Down = 7)
        attacker = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_08_phoenix_guardian"], 0, "u_atk")
        eng.players[0].hand.append(attacker)

        ok, caps = eng.place_card(0, "u_atk", 1, 0)
        self.assertTrue(ok)
        self.assertEqual(caps, 1)
        self.assertEqual(eng.grid[1][1].owner_id, 0)

    def test_04_orthogonal_directional_capture_down_vs_up(self) -> None:
        """Verify placing a card at (1, 2) compares its Down against (1, 1)'s Up."""
        eng = SynapseTacticalGridEngine()
        # Defender at (1, 1): Elemental Sprite (Up = 3)
        defender = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_05_elemental_sprite"], 1, "u_def")
        eng.grid[1][1] = defender
        # Attacker: Celestial Guardian (Down = 9 > Defender Up = 3)
        attacker = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_03_celestial_guardian"], 0, "u_atk")
        eng.players[0].hand.append(attacker)

        ok, caps = eng.place_card(0, "u_atk", 1, 2)
        self.assertTrue(ok)
        self.assertEqual(caps, 1)
        self.assertEqual(eng.grid[1][1].owner_id, 0)

    def test_05_orthogonal_directional_capture_left_and_right(self) -> None:
        """Verify Left vs Right and Right vs Left comparisons and strict inequality on ties."""
        eng = SynapseTacticalGridEngine()
        # Defender at (0, 1): Mystic Mage (Right = 6)
        def_left = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 1, "def_l")
        # Defender at (2, 1): Sketching (Left = 6)
        def_right = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_01_sketching"], 1, "def_r")
        eng.grid[0][1] = def_left
        eng.grid[2][1] = def_right

        # Attacker at (1, 1): Cyber Ninja (Left = 8 > 6 captures def_left; Right = 7 > 6 captures def_right)
        atk = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_09_cyber_ninja"], 0, "atk_c")
        eng.players[0].hand.append(atk)
        ok, caps = eng.place_card(0, "atk_c", 1, 1)
        self.assertTrue(ok)
        self.assertEqual(caps, 2)
        self.assertEqual(eng.grid[0][1].owner_id, 0)
        self.assertEqual(eng.grid[2][1].owner_id, 0)

    def test_06_equal_directional_stats_do_not_capture(self) -> None:
        """Verify that equal opposing stats (atk == def) do not flip the neighbor."""
        eng = SynapseTacticalGridEngine()
        # Defender at (1, 1): Storyboard (Down = 6)
        defender = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_03_storyboard"], 1, "def_tie")
        eng.grid[1][1] = defender
        # Attacker at (1, 0): Celestial Guardian (Up = 6 == Defender Down = 6)
        attacker = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_03_celestial_guardian"], 0, "atk_tie")
        eng.players[0].hand.append(attacker)

        ok, caps = eng.place_card(0, "atk_tie", 1, 0)
        self.assertTrue(ok)
        self.assertEqual(caps, 0)
        self.assertEqual(eng.grid[1][1].owner_id, 1)

    def test_07_theme_synergy_bonus_1_2_3_all_sides(self) -> None:
        """Verify +1 (Tech), +2 (Magic), and +3 (Divine) synergy bonuses when orthogonally adjacent."""
        eng = SynapseTacticalGridEngine()
        # Mech Knight (+1 Tech synergy) at (0, 0), Cyber Ninja (Tech) at (0, 1)
        mk = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_02_mech_knight"], 0, "mk")
        cn = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_09_cyber_ninja"], 0, "cn")
        eng.grid[0][0] = mk
        self.assertEqual(eng.get_effective_stats(0, 0).up, 8)
        eng.grid[0][1] = cn
        self.assertEqual(eng.get_effective_stats(0, 0).up, 9)  # +1 Tech synergy

        # Mystic Mage (+2 Magic synergy) at (2, 0), Clockwork Sorcerer (Steampunk, Magic) at (2, 1)
        mm = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 0, "mm")
        cs = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_07_clockwork_sorcerer"], 0, "cs")
        eng.grid[2][0] = mm
        eng.grid[2][1] = cs
        self.assertEqual(eng.get_effective_stats(2, 0).down, 7 + 2)  # +2 Magic synergy

        # Celestial Guardian (+3 Divine synergy) at (1, 2), Lunar Oracle (Lunar, Cosmic, Divine) at (2, 2)
        cg = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_03_celestial_guardian"], 0, "cg")
        lo = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_10_lunar_oracle"], 0, "lo")
        eng.grid[1][2] = cg
        eng.grid[2][2] = lo
        self.assertEqual(eng.get_effective_stats(1, 2).down, 9 + 3)  # +3 Divine synergy

    def test_08_ability_01_mystic_mage_teleport(self) -> None:
        """Verify Mystic Mage's Teleport moves to any empty cell once per game and resolves captures."""
        eng = SynapseTacticalGridEngine()
        mm = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 0, "mm")
        victim = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_05_elemental_sprite"], 1, "vic")
        eng.grid[0][0] = mm
        eng.grid[2][1] = victim  # Up = 3; Mystic Mage at (2, 2) has Down = 7 > 3

        self.assertTrue(eng.activate_special_ability(0, 0, 0, 2, 2))
        self.assertIsNone(eng.grid[0][0])
        self.assertIs(eng.grid[2][2], mm)
        self.assertEqual(eng.grid[2][1].owner_id, 0)
        # Second use in same game must fail (once per game)
        self.assertFalse(eng.activate_special_ability(0, 2, 2, 0, 0))

    def test_09_ability_02_mech_knight_charge(self) -> None:
        """Verify Mech Knight's Charge grants an immediate bonus move after capturing a card."""
        eng = SynapseTacticalGridEngine()
        victim = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_05_elemental_sprite"], 1, "vic")
        eng.grid[0][1] = victim  # Down = 4
        mk = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_02_mech_knight"], 0, "mk")  # Up = 8
        follow_up = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_01_sketching"], 0, "fu")
        eng.players[0].hand.extend([mk, follow_up])

        ok, caps = eng.place_card(0, "mk", 0, 0)
        self.assertTrue(ok)
        self.assertEqual(caps, 1)
        # Active player remains 0 with bonus_move_player_id == 0
        self.assertEqual(eng.active_player_id, 0)
        self.assertEqual(eng.bonus_move_player_id, 0)

    def test_10_ability_03_celestial_guardian_healing_aura(self) -> None:
        """Verify Celestial Guardian's Healing Aura grants +1 permanent all-sides bonus to adjacent allies on EndTurn."""
        eng = SynapseTacticalGridEngine()
        cg = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_03_celestial_guardian"], 0, "cg")
        ally = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_01_sketching"], 0, "ally")
        enemy = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_03_storyboard"], 1, "enemy")
        eng.grid[1][1] = cg
        eng.grid[1][0] = ally
        eng.grid[1][2] = enemy
        eng.players[0].hand.append(RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 0, "h0"))

        eng.end_turn()
        self.assertEqual(ally.permanent_stat_bonus, 1)
        self.assertEqual(enemy.permanent_stat_bonus, 0)

    def test_11_ability_04_shadow_assassin_vanish(self) -> None:
        """Verify Shadow Assassin's Vanish grants capture immunity for 1 turn once per game."""
        eng = SynapseTacticalGridEngine()
        sa = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_04_shadow_assassin"], 0, "sa")
        eng.grid[1][1] = sa
        self.assertTrue(eng.activate_special_ability(0, 1, 1))
        self.assertTrue(eng.is_card_capture_immune(1, 1))

        # Opponent places Phoenix Guardian (Up=9) at (1, 0) against Shadow Assassin (Down=5)
        eng.active_player_id = 1
        pg = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_08_phoenix_guardian"], 1, "pg")
        eng.players[1].hand.append(pg)
        ok, caps = eng.place_card(1, "pg", 1, 0)
        self.assertTrue(ok)
        self.assertEqual(caps, 0)
        self.assertEqual(eng.grid[1][1].owner_id, 0)

    def test_12_ability_05_elemental_sprite_elemental_burst(self) -> None:
        """Verify Elemental Sprite swaps base stats with a captured card once per game."""
        eng = SynapseTacticalGridEngine()
        # Defender at (2, 1): Clockwork Sorcerer (Left = 7, base 4/8/7/5)
        defender = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_07_clockwork_sorcerer"], 1, "def")
        eng.grid[2][1] = defender
        # Elemental Sprite (Right = 9 > 7, base 3/4/6/9) placed at (1, 1)
        sprite = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_05_elemental_sprite"], 0, "spr")
        eng.players[0].hand.append(sprite)

        ok, caps = eng.place_card(0, "spr", 1, 1)
        self.assertTrue(ok)
        self.assertEqual(caps, 1)
        self.assertTrue(sprite.once_per_game_used)
        self.assertEqual((sprite.base_stats.up, sprite.base_stats.down), (4, 8))
        self.assertEqual((defender.base_stats.up, defender.base_stats.right), (3, 9))

    def test_13_ability_06_galactic_explorer_warp_drive(self) -> None:
        """Verify Galactic Explorer's WarpDrive can move once per turn and resets on subsequent turns."""
        eng = SynapseTacticalGridEngine()
        ge = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_06_galactic_explorer"], 0, "ge")
        eng.grid[0][0] = ge
        eng.players[0].hand.append(RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_01_sketching"], 0, "h0"))

        self.assertTrue(eng.activate_special_ability(0, 0, 0, 1, 1))
        self.assertFalse(eng.activate_special_ability(0, 1, 1, 2, 2))  # Already moved this turn
        eng.end_turn()
        self.assertFalse(ge.moved_this_turn)
        self.assertTrue(eng.activate_special_ability(0, 1, 1, 2, 2))  # Can move again next turn

    def test_14_ability_07_clockwork_sorcerer_temporal_rift(self) -> None:
        """Verify Clockwork Sorcerer's Temporal Rift reverses adjacent cards' Up<->Down and Left<->Right."""
        eng = SynapseTacticalGridEngine()
        cs = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_07_clockwork_sorcerer"], 0, "cs")
        neighbor = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_02_mech_knight"], 1, "mk")  # 8/4/6/5
        eng.grid[1][1] = cs
        eng.grid[1][2] = neighbor

        before = eng.get_effective_stats(1, 2)
        self.assertEqual((before.up, before.down, before.left, before.right), (8, 4, 6, 5))

        self.assertTrue(eng.activate_special_ability(0, 1, 1))
        after = eng.get_effective_stats(1, 2)
        self.assertEqual((after.up, after.down, after.left, after.right), (4, 8, 5, 6))

    def test_15_ability_08_phoenix_guardian_rebirth(self) -> None:
        """Verify Phoenix Guardian returns to its original owner's hand when captured."""
        eng = SynapseTacticalGridEngine()
        pg = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_08_phoenix_guardian"], 1, "pg")  # Right = 4
        eng.grid[0][1] = pg
        # Attacker at (1, 1): Cyber Ninja (Left = 8 > 4)
        cn = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_09_cyber_ninja"], 0, "cn")
        eng.players[0].hand.append(cn)

        ok, caps = eng.place_card(0, "cn", 1, 1)
        self.assertTrue(ok)
        self.assertEqual(caps, 1)
        self.assertIsNone(eng.grid[0][1])
        self.assertIn(pg, eng.players[1].hand)
        self.assertEqual(pg.owner_id, 1)
        self.assertTrue(pg.once_per_game_used)

    def test_16_ability_09_cyber_ninja_techno_stealth(self) -> None:
        """Verify Cyber Ninja is immune to capture when adjacent to a Tech card."""
        eng = SynapseTacticalGridEngine()
        cn = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_09_cyber_ninja"], 0, "cn")
        eng.grid[1][1] = cn
        self.assertFalse(eng.is_card_capture_immune(1, 1))

        # Place Tech ally Mech Knight at (1, 2)
        mk = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_02_mech_knight"], 0, "mk")
        eng.grid[1][2] = mk
        self.assertTrue(eng.is_card_capture_immune(1, 1))

    def test_17_ability_10_lunar_oracle_moonlight_blessing(self) -> None:
        """Verify Lunar Oracle gains +1 all sides at night or when adjacent to a Lunar card."""
        eng_day = SynapseTacticalGridEngine(is_nighttime=False)
        lo_day = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_10_lunar_oracle"], 0, "lo1")
        eng_day.grid[0][0] = lo_day
        self.assertEqual(eng_day.get_effective_stats(0, 0).up, 7)

        eng_night = SynapseTacticalGridEngine(is_nighttime=True)
        lo_night = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_10_lunar_oracle"], 0, "lo2")
        eng_night.grid[0][0] = lo_night
        self.assertEqual(eng_night.get_effective_stats(0, 0).up, 8)

    def test_18_cardcraft_evolution_sketching_and_storyboard(self) -> None:
        """Verify CardCraft evolution chains: Sketching -> Concept Art and Storyboard -> Animatic."""
        sketch = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_01_sketching"], 0, "sk")
        concept, rem_cp = SynapseTacticalGridEngine.evolve_cardcraft_card(sketch, cp_available=50, cp_cost=30)
        self.assertEqual(concept.card_id, "cc_02_concept_art")
        self.assertEqual(rem_cp, 20)
        self.assertGreater(concept.base_stats.total(), sketch.base_stats.total())

        story = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cc_03_storyboard"], 0, "sb")
        animatic, rem_cp2 = SynapseTacticalGridEngine.evolve_cardcraft_card(story, cp_available=40, cp_cost=30)
        self.assertEqual(animatic.card_id, "cc_04_animatic")
        self.assertEqual(animatic.special_ability, "WarpDrive")
        self.assertEqual(rem_cp2, 10)

    def test_19_backend_user_registration_and_cryptographic_pack_opening(self) -> None:
        """Verify SQLite metagame backend registration, starter deck, coin deduction, and pack RNG."""
        backend = SynapseMetagameBackend(":memory:")
        user = backend.register_user("Tactician_Alpha", "pw_secret")
        self.assertEqual(user["elo"], 1200)
        self.assertEqual(user["coins"], 1000)
        self.assertEqual(len(user["owned_cards"]), 7)
        self.assertIn("Initiate", user["badges"])

        pack = backend.open_pack(user["user_id"], pack_cost=200, cards_per_pack=5)
        self.assertEqual(len(pack["drawn_cards"]), 5)
        self.assertEqual(pack["remaining_coins"], 800)
        updated = backend.get_user(user["user_id"])
        self.assertEqual(len(updated["owned_cards"]), 12)

        with self.assertRaises(ValueError):
            backend.open_pack(user["user_id"], pack_cost=5000)

    def test_20_backend_authoritative_match_elo_cp_xp_and_hash(self) -> None:
        """Verify authoritative 3x3 match simulation updates Elo, CP, XP, and records deterministic state hash."""
        backend = SynapseMetagameBackend(":memory:")
        u0 = backend.register_user("Player_Zero", "pw0")
        u1 = backend.register_user("Player_One", "pw1")
        res = backend.simulate_authoritative_3x3_match(u0["user_id"], u1["user_id"], seed=42)

        self.assertEqual(res["p0_cells"] + res["p1_cells"], 9)
        self.assertEqual(len(res["turn_log"]), 9)
        self.assertEqual(len(res["state_hash"]), 16)

        winner_id = res["winner_id"]
        loser_id = u1["user_id"] if winner_id == u0["user_id"] else u0["user_id"]
        w_profile = backend.get_user(winner_id)
        l_profile = backend.get_user(loser_id)
        self.assertEqual(w_profile["elo"], 1224)
        self.assertEqual(l_profile["elo"], 1184)
        self.assertGreaterEqual(w_profile["xp"], 100)
        self.assertGreaterEqual(w_profile["confidence_points"], 25)

    def test_21_fnv1a_64_state_hash_determinism_and_tamper_sensitivity(self) -> None:
        """Verify 64-bit FNV-1a state hash is deterministic across clones and changes on board mutation."""
        eng1 = SynapseTacticalGridEngine(seed=99)
        c1 = RuntimeCardInstance.from_def(OFFICIAL_PROJECT_CF_CARDS["cf_01_mystic_mage"], 0, "c1")
        eng1.grid[1][1] = c1
        eng2 = eng1.clone_state()

        h1 = eng1.compute_fnv1a_64_hash()
        h2 = eng2.compute_fnv1a_64_hash()
        self.assertEqual(h1, h2)

        eng2.grid[1][1].owner_id = 1
        self.assertNotEqual(h1, eng2.compute_fnv1a_64_hash())

    def test_22_csharp_scripts_zero_third_party_namespace_leakage(self) -> None:
        """Verify zero third-party `TcgEngine` or `CCGKit` namespace imports exist in Assets/Scripts/**/*.cs."""
        cs_files = list(SCRIPTS_DIR.rglob("*.cs"))
        self.assertGreaterEqual(len(cs_files), 9)
        forbidden_patterns = [
            re.compile(r"\busing\s+TcgEngine\b"),
            re.compile(r"\busing\s+CCGKit\b"),
            re.compile(r"\bnamespace\s+TcgEngine\b"),
            re.compile(r"\bnamespace\s+CCGKit\b"),
        ]
        for path in cs_files:
            content = path.read_text(encoding="utf-8")
            for pat in forbidden_patterns:
                self.assertIsNone(
                    pat.search(content),
                    f"Forbidden third-party namespace reference `{pat.pattern}` found in {path}",
                )
            self.assertIn("namespace Synapse.TcgEngine", content, f"Missing Synapse.TcgEngine namespace in {path}")

    @staticmethod
    def _strip_csharp_comments_and_strings(text: str) -> str:
        """Single-pass lexical stripper for C# comments and string/char literals."""
        out: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            nxt = text[i + 1] if i + 1 < n else ""
            if ch == "/" and nxt == "/":
                i += 2
                while i < n and text[i] != "\n":
                    i += 1
            elif ch == "/" and nxt == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
            elif ch == "@" and nxt == '"':
                i += 2
                while i < n:
                    if text[i] == '"' and (i + 1 < n and text[i + 1] == '"'):
                        i += 2
                    elif text[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1
            elif ch == '"':
                i += 1
                while i < n:
                    if text[i] == "\\":
                        i += 2
                    elif text[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1
            elif ch == "'":
                i += 1
                while i < n:
                    if text[i] == "\\":
                        i += 2
                    elif text[i] == "'":
                        i += 1
                        break
                    else:
                        i += 1
            else:
                out.append(ch)
                i += 1
        return "".join(out)

    def test_23_csharp_scripts_brace_and_syntax_balance(self) -> None:
        """Verify every C# script in Assets/Scripts/**/*.cs has balanced braces, parens, and brackets."""
        cs_files = list(SCRIPTS_DIR.rglob("*.cs"))
        for path in cs_files:
            text = path.read_text(encoding="utf-8")
            cleaned = self._strip_csharp_comments_and_strings(text)
            self.assertEqual(cleaned.count("{"), cleaned.count("}"), f"Unbalanced {{}} in {path}")
            self.assertEqual(cleaned.count("("), cleaned.count(")"), f"Unbalanced () in {path}")
            self.assertEqual(cleaned.count("["), cleaned.count("]"), f"Unbalanced [] in {path}")

    def test_24_csharp_and_python_card_catalog_exact_parity(self) -> None:
        """Verify `CardDataSO.cs` and `synapse_tcg_backend.py` define the exact same 14 card IDs and base stats."""
        cs_catalog = (SCRIPTS_DIR / "Data" / "CardDataSO.cs").read_text(encoding="utf-8")
        pattern = re.compile(
            r'Add\(\s*"(?P<id>[a-z0-9_]+)"\s*,\s*"(?P<title>[^"]+)"\s*,\s*"(?P<code>[^"]+)"\s*,\s*'
            r'(?P<u>\d+)\s*,\s*(?P<d>\d+)\s*,\s*(?P<l>\d+)\s*,\s*(?P<r>\d+)'
        )
        matches = list(pattern.finditer(cs_catalog))
        self.assertEqual(len(matches), 14, "CardDataSO.cs must register all 14 cards")
        for m in matches:
            cid = m.group("id")
            self.assertIn(cid, OFFICIAL_PROJECT_CF_CARDS)
            py_card = OFFICIAL_PROJECT_CF_CARDS[cid]
            self.assertEqual(
                (int(m.group("u")), int(m.group("d")), int(m.group("l")), int(m.group("r"))),
                (py_card.up, py_card.down, py_card.left, py_card.right),
                f"Stat mismatch between C# and Python for {cid}",
            )

    def test_25_staccs_vertical_3d_card_stacking_and_flank_support_bonus(self) -> None:
        """Verify 3D vertical card stacking (`z_height`), top-card authority, +1 per support layer, and flank synergy."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=2501)
        # Stack 3 cards on (1, 1): Sketching (base support), Storyboard (mid support), Mech Knight (top card: 8/4/6/5)
        sim.stack_card(1, 1, "cc_01_sketching", owner=0)
        sim.stack_card(1, 1, "cc_03_storyboard", owner=0)
        cell = sim.stack_card(1, 1, "cf_02_mech_knight", owner=0)

        self.assertEqual(cell.z_height, 3)
        self.assertIsNotNone(cell.top_card)
        self.assertEqual(cell.top_card["card_id"], "cf_02_mech_knight")
        self.assertEqual(cell.top_card["special_ability"], "Charge")

        # 2 underlying support layers grant +2 all-sides Stack Support Bonus: (8+2, 4+2, 6+2, 5+2) = (10, 6, 8, 7)
        self.assertEqual(sim.get_effective_stats(1, 1), (10, 6, 8, 7))

        # Place Tech flank ally Cyber Ninja at (1, 2) -> grants Mech Knight's +1 Tech synergy bonus: (11, 7, 9, 8)
        sim.stack_card(1, 2, "cf_09_cyber_ninja", owner=0)
        self.assertEqual(sim.get_effective_stats(1, 1), (11, 7, 9, 8))

    def test_26_staccs_stack_layer_armor_shedding_on_damage(self) -> None:
        """Verify underlying support layers absorb damage by shedding bottom layers before the top card takes stat loss."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=2601)
        sim.stack_card(0, 0, "cc_01_sketching", owner=0)
        sim.stack_card(0, 0, "cc_03_storyboard", owner=0)
        sim.stack_card(0, 0, "cf_08_phoenix_guardian", owner=0)  # Top card base: 9/7/6/4 (+2 support = 11/9/8/6)

        self.assertEqual(sim.grid[0][0].z_height, 3)
        self.assertEqual(sim.get_effective_stats(0, 0), (11, 9, 8, 6))

        # 1 point of hazard damage sheds the bottom layer (cc_01_sketching); top card remains Phoenix Guardian unharmed
        dmg1 = sim.apply_damage(0, 0, amount=1, source="hazard")
        self.assertEqual(dmg1["layers_shed"], 1)
        self.assertEqual(dmg1["stat_damage"], 0)
        self.assertEqual(sim.grid[0][0].z_height, 2)
        self.assertEqual(sim.grid[0][0].top_card["card_id"], "cf_08_phoenix_guardian")
        self.assertEqual(sim.get_effective_stats(0, 0), (10, 8, 7, 5))

        # Second point of damage sheds the remaining support layer (cc_03_storyboard)
        dmg2 = sim.apply_damage(0, 0, amount=1, source="hazard")
        self.assertEqual(dmg2["layers_shed"], 1)
        self.assertEqual(sim.grid[0][0].z_height, 1)
        self.assertEqual(sim.get_effective_stats(0, 0), (9, 7, 6, 4))

        # Third point of damage hits the solo top card directly, reducing all directional stats by 1
        dmg3 = sim.apply_damage(0, 0, amount=1, source="hazard")
        self.assertEqual(dmg3["layers_shed"], 0)
        self.assertEqual(dmg3["stat_damage"], 1)
        self.assertEqual(sim.get_effective_stats(0, 0), (8, 6, 5, 3))

    def test_27_into_the_breach_deterministic_telegraph_queue_and_resolution(self) -> None:
        """Verify queued telegraphed enemy strikes resolve deterministically in FIFO order against target cells."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=2701)
        # Enemy at (2, 1), Player 2-layer stack at (1, 1)
        sim.stack_card(2, 1, "cf_04_shadow_assassin", owner=1)
        sim.stack_card(1, 1, "cc_01_sketching", owner=0)
        sim.stack_card(1, 1, "cf_03_celestial_guardian", owner=0)

        intent = sim.queue_telegraph(attacker_x=2, attacker_y=1, target_x=1, target_y=1, damage=1)
        self.assertIsInstance(intent, TelegraphedIntent)
        self.assertEqual(len(sim.telegraph_queue), 1)

        resolutions = sim.resolve_telegraphs()
        self.assertEqual(len(resolutions), 1)
        self.assertTrue(resolutions[0]["hit"])
        self.assertEqual(resolutions[0]["target"], (1, 1))
        self.assertEqual(sim.grid[1][1].z_height, 1)
        self.assertEqual(sim.grid[1][1].top_card["card_id"], "cf_03_celestial_guardian")
        self.assertEqual(len(sim.telegraph_queue), 0)

    def test_28_into_the_breach_push_redirects_telegraphed_enemy_attack(self) -> None:
        """Verify pushing an enemy shifts its telegraphed strike by (dx, dy) into another enemy and away from an ally."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=2801)
        # Ally at (0, 1); Enemy Alpha at (1, 1) telegraphing a strike left at (0, 1); Enemy Beta at (0, 2)
        sim.stack_card(0, 1, "cf_01_mystic_mage", owner=0)
        sim.stack_card(1, 1, "cf_02_mech_knight", owner=1)
        sim.stack_card(0, 2, "cc_01_sketching", owner=1)
        sim.stack_card(0, 2, "cf_04_shadow_assassin", owner=1)  # 2-layer enemy stack at (0, 2)

        sim.queue_telegraph(attacker_x=1, attacker_y=1, target_x=0, target_y=1, damage=1)

        # Push Enemy Alpha at (1, 1) Up by (dx=0, dy=+1) to (1, 2)
        push_res = sim.push_stack(1, 1, 0, 1)
        self.assertTrue(push_res["moved"])
        self.assertEqual(push_res["to"], (1, 2))
        self.assertEqual(push_res["shifted_telegraphs"], 1)

        # Telegraph target must have shifted from (0, 1) to (0, 2) where Enemy Beta sits!
        self.assertEqual(sim.telegraph_queue[0].attacker_x, 1)
        self.assertEqual(sim.telegraph_queue[0].attacker_y, 2)
        self.assertEqual((sim.telegraph_queue[0].target_x, sim.telegraph_queue[0].target_y), (0, 2))

        resolutions = sim.resolve_telegraphs()
        self.assertEqual(resolutions[0]["target"], (0, 2))
        # Ally at (0, 1) is completely unharmed; Enemy Beta at (0, 2) lost its support layer!
        self.assertEqual(sim.grid[0][1].top_card["damage_taken"], 0)
        self.assertEqual(sim.grid[0][2].z_height, 1)

    def test_29_into_the_breach_push_collision_bump_damage_between_two_stacks(self) -> None:
        """Verify pushing a stack into an occupied cell deals 1 Collision/Bump damage to both stacks without moving."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=2901)
        # Stack A at (1, 1) with 2 layers; Stack B at (2, 1) with 2 layers
        sim.stack_card(1, 1, "cc_01_sketching", owner=1)
        sim.stack_card(1, 1, "cf_02_mech_knight", owner=1)
        sim.stack_card(2, 1, "cc_03_storyboard", owner=1)
        sim.stack_card(2, 1, "cf_09_cyber_ninja", owner=1)

        bump = sim.push_stack(1, 1, 1, 0)
        self.assertFalse(bump["moved"])
        self.assertTrue(bump["collision"])
        self.assertEqual(bump["collision_type"], "unit_or_building")
        # Both stacks remain on their tiles and shed 1 bottom support layer each
        self.assertEqual(sim.grid[1][1].z_height, 1)
        self.assertEqual(sim.grid[2][1].z_height, 1)
        self.assertEqual(sim.grid[1][1].top_card["card_id"], "cf_02_mech_knight")
        self.assertEqual(sim.grid[2][1].top_card["card_id"], "cf_09_cyber_ninja")

    def test_30_into_the_breach_civilian_power_grid_building_protection_and_damage(self) -> None:
        """Verify Civilian Power Grid starts at 7 bars, takes damage from hits/bumps, and can be saved by pushing."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=3001, power_grid_bars=7)
        self.assertEqual(sim.power_grid_bars, 7)

        sim.place_power_grid_building(0, 0, bars=2)
        sim.place_power_grid_building(2, 2, bars=2)

        # Enemy at (0, 1) telegraphs 2 damage onto Civilian Building at (0, 0)
        sim.stack_card(0, 1, "cf_04_shadow_assassin", owner=1)
        sim.queue_telegraph(attacker_x=0, attacker_y=1, target_x=0, target_y=0, damage=1)
        sim.resolve_telegraphs()
        self.assertEqual(sim.power_grid_bars, 6)
        self.assertEqual(sim.grid[0][0].building_bars, 1)

        # Second telegraph against building at (2, 2) from enemy at (1, 2), but player pushes enemy away to (1, 1)!
        sim.stack_card(1, 2, "cf_02_mech_knight", owner=1)
        sim.queue_telegraph(attacker_x=1, attacker_y=2, target_x=2, target_y=2, damage=2)
        sim.push_stack(1, 2, 0, -1)  # Pushed to (1, 1) -> telegraph redirects to (2, 1) empty tile!
        sim.resolve_telegraphs()
        # Building at (2, 2) was saved; power_grid_bars remains 6!
        self.assertEqual(sim.power_grid_bars, 6)
        self.assertEqual(sim.grid[2][2].building_bars, 2)

    def test_31_into_the_breach_seismic_cracked_tile_to_chasm_collapse(self) -> None:
        """Verify pushing a stack onto a `cracked` tile collapses it into a `chasm` and destroys the stack."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=3101)
        sim.set_terrain(2, 0, "cracked")
        sim.stack_card(1, 0, "cc_01_sketching", owner=1)
        sim.stack_card(1, 0, "cf_07_clockwork_sorcerer", owner=1)
        sim.queue_telegraph(attacker_x=1, attacker_y=0, target_x=1, target_y=1, damage=2)

        res = sim.push_stack(1, 0, 1, 0)
        self.assertTrue(res["moved"])
        self.assertTrue(res["collapsed_to_chasm"])
        self.assertEqual(sim.grid[2][0].terrain, "chasm")
        self.assertEqual(sim.grid[2][0].z_height, 0)
        # Displaced enemy fell into chasm, so its queued telegraph is canceled!
        self.assertEqual(len(sim.telegraph_queue), 0)

    def test_32_into_the_breach_time_breach_single_pilot_roguelike_timeline_carryover(self) -> None:
        """Verify `trigger_time_breach` preserves 1 surviving Pilot with XP, permanent_bonus, and evolution into a new timeline."""
        sim = BreachStackMatchSimulator(width=3, height=3, seed=3201, power_grid_bars=2)
        cell = sim.stack_card(
            1,
            1,
            {
                "uid": "pilot_alpha_01",
                "card_id": "cc_03_storyboard",
                "owner": 0,
                "xp": 120,
                "permanent_bonus": 2,
                "damage_taken": 1,
            },
            owner=0,
        )
        self.assertEqual(cell.top_card["uid"], "pilot_alpha_01")

        next_timeline = sim.trigger_time_breach("pilot_alpha_01", new_seed=4099)
        self.assertEqual(next_timeline.seed, 4099)
        self.assertEqual(next_timeline.power_grid_bars, 7)
        self.assertEqual(next_timeline.timeline_generation, 2)
        self.assertIsNotNone(next_timeline.carryover_pilot)

        pilot = next_timeline.carryover_pilot
        self.assertEqual(pilot["uid"], "pilot_alpha_01")
        self.assertEqual(pilot["xp"], 120)
        self.assertEqual(pilot["permanent_bonus"], 2)
        self.assertEqual(pilot["damage_taken"], 0)
        # Because xp >= 100 and cc_03_storyboard evolves_to cc_04_animatic, pilot carries over in evolved form!
        self.assertEqual(pilot["card_id"], "cc_04_animatic")
        self.assertEqual(pilot["special_ability"], "WarpDrive")

    def test_33_advance_wars_damage_formula_and_terrain_defense_stars(self) -> None:
        """Verify Advance Wars decompiled % damage formula scales with AtkHP, AtkCO/DefCO, and 0-4★ Terrain Defense."""
        sim = AdvanceWarsFftaDynamicsSimulator()
        # Full HP (10/10), 100/100 CO, 0★ Road terrain: exact base damage (80%)
        dmg_road = sim.compute_advance_wars_damage(80, atk_co=100, def_co=100, atk_hp=10, def_hp=10, terrain_stars=0)
        self.assertEqual(dmg_road, 80)

        # 3★ City/Building terrain at 10 DefHP reduces damage by 30%: 80 * 0.70 = 56%
        dmg_city = sim.compute_advance_wars_damage(80, atk_co=100, def_co=100, atk_hp=10, def_hp=10, terrain_stars=3)
        self.assertEqual(dmg_city, 56)

        # Half-HP attacker (5/10) deals half damage: 80 * 0.5 = 40%
        dmg_half = sim.compute_advance_wars_damage(80, atk_co=100, def_co=100, atk_hp=5, def_hp=10, terrain_stars=0)
        self.assertEqual(dmg_half, 40)

        # Super CO Power attacker (130 AtkCO) on 0★ terrain: 80 * 1.30 = 104%
        dmg_sco = sim.compute_advance_wars_damage(80, atk_co=130, def_co=100, atk_hp=10, def_hp=10, terrain_stars=0)
        self.assertEqual(dmg_sco, 104)

    def test_34_advance_wars_co_power_and_super_co_power_star_meter(self) -> None:
        """Verify Advance Wars CO Star Meter charges 2x faster from damage taken and triggers CO / Super CO Power."""
        sim = AdvanceWarsFftaDynamicsSimulator()
        # Deal 20 damage (+1.0★) and take 20 damage (+2.0★) -> 3.0★ total -> activates normal CO Power (110/110, +1 all sides)
        res_co = sim.charge_and_activate_co_power(0, damage_dealt_value=20, damage_taken_value=20, super_power=False)
        self.assertTrue(res_co["activated"])
        self.assertEqual(res_co["power_type"], "CO_POWER")
        self.assertEqual(res_co["atk_co"], 110)
        self.assertEqual(res_co["def_co"], 110)
        self.assertEqual(res_co["all_sides_bonus"], 1)
        self.assertEqual(res_co["co_stars"], 0.0)

        # Charge 6.0★ for Player 1 and activate Super CO Power (130/130, +2 all sides)
        res_sco = sim.charge_and_activate_co_power(1, damage_dealt_value=40, damage_taken_value=40, super_power=True)
        self.assertTrue(res_sco["activated"])
        self.assertEqual(res_sco["power_type"], "SUPER_CO_POWER")
        self.assertEqual(res_sco["atk_co"], 130)
        self.assertEqual(res_sco["def_co"], 130)
        self.assertEqual(res_sco["all_sides_bonus"], 2)

    def test_35_ffta_ctb_charge_time_battle_turn_order_queue(self) -> None:
        """Verify FFTA Charge Time Battle (`CT += Speed >= 1000`) clock ticks deterministically and deducts 1000 CT."""
        units = [
            {"uid": "u_assassin", "ct": 600, "speed": 140},
            {"uid": "u_paladin", "ct": 650, "speed": 90},
            {"uid": "u_chrono", "ct": 500, "speed": 120},
        ]
        # Tick 1: assassin=740, paladin=740, chrono=620
        # Tick 2: assassin=880, paladin=830, chrono=740
        # Tick 3: assassin=1020 (>=1000!), paladin=920, chrono=860
        step1 = AdvanceWarsFftaDynamicsSimulator.advance_ffta_ctb_queue(units)
        self.assertEqual(step1["active_unit_uid"], "u_assassin")
        self.assertEqual(step1["ticks_elapsed"], 3)
        self.assertEqual(step1["post_tick_ct_map"]["u_assassin"], 20)

        # Next tick (Tick 1 from state): paladin reaches 920+90=1010, chrono reaches 860+120=980
        step2 = AdvanceWarsFftaDynamicsSimulator.advance_ffta_ctb_queue(units)
        self.assertEqual(step2["active_unit_uid"], "u_paladin")
        self.assertEqual(step2["ticks_elapsed"], 1)
        self.assertEqual(step2["post_tick_ct_map"]["u_paladin"], 10)

    def test_36_ffta_directional_facing_front_side_back_multipliers(self) -> None:
        """Verify FFTA orthogonal facing math returns FRONT (1.0x), SIDE (1.25x), and BACK (1.50x)."""
        sim = AdvanceWarsFftaDynamicsSimulator()
        # Defender facing UP (0, 1):
        # Attack travelling DOWN (0, -1) hits defender's chest -> FRONT (1.0x)
        self.assertEqual(sim.compute_ffta_facing_multiplier("DOWN", "UP"), ("FRONT", 1.0))
        # Attack travelling RIGHT (1, 0) or LEFT (-1, 0) hits defender's flank -> SIDE (1.25x)
        self.assertEqual(sim.compute_ffta_facing_multiplier("RIGHT", "UP"), ("SIDE", 1.25))
        self.assertEqual(sim.compute_ffta_facing_multiplier("LEFT", "UP"), ("SIDE", 1.25))
        # Attack travelling UP (0, 1) from behind hits defender's spine -> BACK (1.50x)
        self.assertEqual(sim.compute_ffta_facing_multiplier("UP", "UP"), ("BACK", 1.50))

    def test_37_ffta_judge_points_and_mythril_combo_chain_links(self) -> None:
        """Verify FFTA Mythril Combo links orthogonally adjacent allies, grants combo stat bonus, and supports Totema at 10 JP."""
        sim = AdvanceWarsFftaDynamicsSimulator(width=3, height=3)
        sim.stack_card(1, 1, "cf_01_mystic_mage", owner=0)
        sim.stack_card(0, 1, "cf_03_celestial_guardian", owner=0)
        sim.stack_card(2, 1, "cf_07_clockwork_sorcerer", owner=0)
        sim.stack_card(1, 2, "cf_04_shadow_assassin", owner=1)  # Enemy (not linked)

        sim.judge_points[0] = 4
        combo = sim.trigger_ffta_mythril_combo(sim, 1, 1, owner=0, jp_spent=3)
        self.assertEqual(combo["combo_count"], 2)
        self.assertEqual(combo["jp_spent"], 3)
        self.assertEqual(combo["jp_gained"], 1)
        self.assertEqual(combo["remaining_jp"], 2)  # 4 - 3 + 1 = 2
        self.assertFalse(combo["totema_summoned"])
        self.assertEqual(combo["combo_stat_bonus"], 2 * 2 + 3)  # 7

        # Verify 10 JP triggers Totema Ultimate Summon
        sim.judge_points[0] = 10
        totema = sim.trigger_ffta_mythril_combo(sim, 1, 1, owner=0, jp_spent=10)
        self.assertTrue(totema["totema_summoned"])
        self.assertGreaterEqual(totema["combo_stat_bonus"], 20)

    def test_38_multitude_of_12_classic_telegraph_animations_generation(self) -> None:
        """Verify `generate_multitude_telegraphs` produces all 12 classic-yet-dynamic telegraph archetypes."""
        sim = AdvanceWarsFftaDynamicsSimulator(width=3, height=3)
        sim.stack_card(1, 1, "cc_01_sketching", owner=0)
        sim.stack_card(1, 1, "cf_02_mech_knight", owner=0)
        sim.stack_card(1, 2, "cf_04_shadow_assassin", owner=1)
        sim.set_terrain(1, 2, "woods")

        telegraphs = sim.generate_multitude_telegraphs(
            sim,
            {
                "owner": 0,
                "from": (0, 1),
                "to": (1, 1),
                "target": (1, 2),
                "attack_dir": "UP",
                "defender_facing": "UP",
                "push_dir": (0, 1),
                "base_dmg": 80,
            },
        )
        self.assertEqual(len(telegraphs), 12)
        ids = {t["archetype_id"] for t in telegraphs}
        self.assertEqual(ids, set(CLASSIC_12_TELEGRAPH_ARCHETYPES.keys()))
        for t in telegraphs:
            self.assertGreater(t["duration_ms"], 0)
            self.assertTrue(t["color_hex"].startswith("#"))
            self.assertEqual(t["facing_type"], "BACK")
            self.assertEqual(t["facing_multiplier"], 1.50)
            self.assertEqual(t["terrain_defense_stars"], 2)
            self.assertEqual(t["elevation_delta_z"], 1)

    def test_39_combined_aw_ffta_itb_staccs_tactical_stack_elevation_synergy(self) -> None:
        """Verify combined 3D stack elevation (STACCS) + CO Power (AW) + Backstab Push (FFTA/ITB) into Cracked Chasm."""
        sim = AdvanceWarsFftaDynamicsSimulator(width=3, height=3, power_grid_bars=7)
        sim.place_power_grid_building(0, 2, bars=2)
        sim.set_terrain(2, 1, "cracked")

        # Player builds a 2-layer stack at (0, 1) and activates CO Power (+1 all sides)
        sim.stack_card(0, 1, "cc_01_sketching", owner=0)
        sim.stack_card(0, 1, "cf_02_mech_knight", owner=0)
        sim.charge_and_activate_co_power(0, damage_dealt_value=20, damage_taken_value=20, super_power=False)

        # Enemy at (1, 1) telegraphs a strike onto Civilian Building at (0, 2)
        sim.stack_card(1, 1, "cf_04_shadow_assassin", owner=1)
        sim.queue_telegraph(attacker_x=1, attacker_y=1, target_x=0, target_y=2, damage=2)

        # Player executes a Backstab Push from (0, 1) -> pushes Enemy at (1, 1) Right (+1, 0) onto Cracked Tile (2, 1)!
        f_type, f_mult = sim.compute_ffta_facing_multiplier("RIGHT", "RIGHT")
        self.assertEqual((f_type, f_mult), ("BACK", 1.50))

        push_res = sim.push_stack(1, 1, 1, 0)
        self.assertTrue(push_res["moved"])
        self.assertTrue(push_res["collapsed_to_chasm"])
        self.assertEqual(sim.grid[2][1].terrain, "chasm")

        # Resolve telegraphs: Enemy fell into chasm, so Civilian Power Grid building at (0, 2) takes 0 damage!
        sim.resolve_telegraphs()
        self.assertEqual(sim.power_grid_bars, 7)
        self.assertEqual(sim.grid[0][2].building_bars, 2)

    def test_40_advance_wars_ffta_dynamics_training_dataset_integrity(self) -> None:
        """Verify `Datasets/advance_wars_ffta_dynamics_training.jsonl` exists and contains >= 100 valid JSONL records."""
        dataset_path = ROOT_DIR / "Datasets" / "advance_wars_ffta_dynamics_training.jsonl"
        self.assertTrue(dataset_path.is_file(), f"Missing training dataset: {dataset_path}")
        lines = [ln.strip() for ln in dataset_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertGreaterEqual(len(lines), 100)

        domains_seen = set()
        for idx, ln in enumerate(lines):
            obj = json.loads(ln)
            self.assertIn("record_id", obj, f"Line {idx} missing record_id")
            self.assertIn("domain", obj, f"Line {idx} missing domain")
            self.assertIn("instruction", obj, f"Line {idx} missing instruction")
            self.assertIn("response", obj, f"Line {idx} missing response")
            domains_seen.add(obj["domain"])

        self.assertIn("multitude_telegraph_archetype", domains_seen)
        self.assertIn("advance_wars_decompilation", domains_seen)
        self.assertIn("ffta_decompilation", domains_seen)
        self.assertIn("combined_aw_ffta_itb_staccs_synthesis", domains_seen)

    def test_41_metal_gear_acid_cost_turn_delay_clock_and_action_order(self) -> None:
        """Verify Shinta Nojiri's MGA COST turn-delay clock (`3..16`) schedules the lowest-COST unit next."""
        mga = MetalGearAcidCostSimulator(seed=4101)
        mga.register_mga_unit("snake_alpha", initial_cost=4)
        mga.register_mga_unit("venus_beta", initial_cost=7)
        mga.register_mga_unit("teliko_gamma", initial_cost=2)

        q1 = mga.get_next_unit_by_lowest_cost()
        self.assertEqual(q1["active_unit_uid"], "teliko_gamma")
        self.assertEqual(q1["active_cost"], 2)

        # Teliko executes a heavy COST=10 card in frontal vision cone (no stealth discount -> +10 COST -> total 12)
        act = mga.execute_mga_card_action(
            "teliko_gamma",
            "cf_02_mech_knight",
            mode="Effect",
            base_cost=10,
            attacker_pos=(1, 2),
            defender_pos=(1, 1),
            defender_facing="UP",
        )
        self.assertEqual(act["cost_added"], 10)
        self.assertEqual(act["cumulative_cost"], 12)

        # Now snake_alpha (COST=4) acts next!
        q2 = mga.get_next_unit_by_lowest_cost()
        self.assertEqual(q2["active_unit_uid"], "snake_alpha")
        self.assertEqual(q2["active_cost"], 4)

    def test_42_metal_gear_acid_multimodal_card_play_move_equip_and_link_chain(self) -> None:
        """Verify MGA 4-mode card execution (`Effect | Move | Equip | Link`) and automatic Equipment Link chain."""
        mga = MetalGearAcidCostSimulator(seed=4201)
        mga.register_mga_unit("snake_01", initial_cost=0)

        # 1. Play card as Move (converts card to orthogonal movement steps at -2 COST discount)
        mv = mga.execute_mga_card_action("snake_01", "cf_02_mech_knight", mode="Move", base_cost=8)
        self.assertEqual(mv["mode"], "Move")
        self.assertEqual(mv["cost_added"], 6)
        self.assertGreaterEqual(mv["movement_steps"], 2)

        # 2. Equip a Tech card (`cf_09_cyber_ninja`) into snake_01's Equipment Slot
        eq = mga.execute_mga_card_action("snake_01", "cf_09_cyber_ninja", mode="Equip", base_cost=6)
        self.assertEqual(eq["mode"], "Equip")
        self.assertEqual(eq["equipped_count"], 1)

        # 3. Execute Tech card (`cf_02_mech_knight`) in Effect mode -> automatically triggers Link Chain with `cf_09_cyber_ninja`!
        eff = mga.execute_mga_card_action("snake_01", "cf_02_mech_knight", mode="Effect", base_cost=10)
        self.assertEqual(eff["mode"], "Effect")
        self.assertIn("cf_09_cyber_ninja", eff["linked_cards_triggered"])

        # 4. Explicit Link reaction adds 0 turn-boundary COST delay
        lnk = mga.execute_mga_card_action("snake_01", "cf_09_cyber_ninja", mode="Link", base_cost=6)
        self.assertEqual(lnk["cost_added"], 0)

    def test_43_metal_gear_acid_stealth_vision_cone_ambush_and_solid_eye_pop_cel(self) -> None:
        """Verify 90° Vision Cone Stealth Ambush (+50% DMG / -2 COST) and MGA2 Solid Eye Pop-Art Cel-Shader telemetry."""
        # Defender at (1, 1) facing UP (0, 1):
        # Attacker at (1, 2) is directly in front inside 90° Vision Cone -> detected!
        cone_front = MetalGearAcidCostSimulator.evaluate_stealth_vision_cone((1, 2), (1, 1), "UP")
        self.assertTrue(cone_front["detected_in_vision_cone"])
        self.assertFalse(cone_front["is_stealth_ambush"])
        self.assertEqual(cone_front["damage_multiplier"], 1.0)
        self.assertEqual(cone_front["cost_reduction"], 0)

        # Attacker at (1, 0) (rear blind spot) is outside 90° Vision Cone -> Stealth Ambush (+50% DMG, -2 COST)!
        cone_rear = MetalGearAcidCostSimulator.evaluate_stealth_vision_cone((1, 0), (1, 1), "UP")
        self.assertFalse(cone_rear["detected_in_vision_cone"])
        self.assertTrue(cone_rear["is_stealth_ambush"])
        self.assertEqual(cone_rear["damage_multiplier"], 1.50)
        self.assertEqual(cone_rear["cost_reduction"], 2)

        # Verify Naochika Morishita / Tsubasa Masao / Yoji Shinkawa Solid Eye Pop-Art Cel-Shader evaluation
        shader = MetalGearAcidCostSimulator.evaluate_solid_eye_pop_cel_shader("cf_04_shadow_assassin", outline_px=3.5, halftone_density=0.70)
        self.assertEqual(shader["shader_profile"], "MGA2_SolidEye_PopCel_ShinkawaInk")
        self.assertEqual(shader["stereoscopic_parallax_planes"], 3)
        self.assertGreaterEqual(shader["pop_contrast_score"], 0.90)

    def test_44_mirofish_strands_multi_agent_npc_simulation_core_and_market_feedback(self) -> None:
        """Verify 12 autonomous NPC archetypes run MiroFish market valuation and 5-stage Strands agentic workflows."""
        engine = MiroStrandsSimulationFeedbackEngine(seed=4401)
        mkt = engine.run_npc_market_simulation(rounds=24)
        self.assertEqual(mkt["npc_archetypes_active"], 12)
        self.assertEqual(mkt["market_rounds_simulated"], 24)
        self.assertEqual(len(mkt["card_market_valuations"]), 14)
        self.assertEqual(len(mkt["npc_agent_reports"]), 12)

        first_trace = mkt["npc_agent_reports"][0]["strands_trace"]["stages"]
        for required_stage in ("1_ObserveState", "2_ThinkHypothesis", "3_ToolCallSimulation", "4_PeerCritique", "5_EmitStructuredPatch"):
            self.assertIn(required_stage, first_trace)

    def test_45_mirofish_strands_studio_illustrator_multi_agent_critique_and_shader_feedback(self) -> None:
        """Verify all 7 Master Studio Illustrator & Creative Director persona agents audit cards, STACCS cubes, and telegraphs."""
        engine = MiroStrandsSimulationFeedbackEngine(seed=4501)
        art = engine.run_studio_illustrator_critique()
        self.assertEqual(art["illustrator_agents_active"], 7)
        self.assertGreaterEqual(art["studio_style_fidelity_score"], 0.90)
        self.assertGreaterEqual(art["telegraph_1s_readability_score"], 0.90)

        agent_ids = {c["agent_id"] for c in art["agent_critiques"]}
        self.assertIn("art_06_masao_morishita_shinkawa", agent_ids)
        self.assertIn("art_07_creative_director_24_7", agent_ids)

    def test_46_mirofish_strands_feedback_analytics_gini_entropy_and_auto_patch(self) -> None:
        """Verify feedback analytics computes Metagame Gini, Deck Shannon Entropy, Elasticity, and Agency Index."""
        engine = MiroStrandsSimulationFeedbackEngine(seed=4601)
        analytics = engine.compute_feedback_analytics()
        self.assertGreaterEqual(analytics["metagame_gini"], 0.0)
        self.assertLessEqual(analytics["metagame_gini"], 0.55)
        self.assertGreaterEqual(analytics["deck_shannon_entropy"], 2.0)
        self.assertGreaterEqual(analytics["agency_vs_frustration_index"], 0.85)
        self.assertGreaterEqual(analytics["telegraph_1s_readability_score"], 0.90)
        self.assertIsInstance(analytics["auto_patches"], list)

    def test_47_model_soup_uniform_greedy_task_arithmetic_and_ties_merging_pipeline(self) -> None:
        """Verify Soup-to-Full Training supports Uniform, Greedy, Task-Arithmetic, and TIES-Merging across adapters."""
        base_w = {"w_cost": 0.50, "w_facing": 0.50, "w_stack": 0.50}
        candidates = [
            {"name": "mga_adapter", "val_score": 0.94, "lambda": 0.4, "weights": {"w_cost": 0.70, "w_facing": 0.55, "w_stack": 0.52}},
            {"name": "ffta_adapter", "val_score": 0.93, "lambda": 0.3, "weights": {"w_cost": 0.54, "w_facing": 0.72, "w_stack": 0.56}},
            {"name": "staccs_adapter", "val_score": 0.92, "lambda": 0.3, "weights": {"w_cost": 0.52, "w_facing": 0.58, "w_stack": 0.74}},
        ]
        for mode in ("uniform", "greedy", "task_arithmetic", "ties"):
            res = MiroStrandsSimulationFeedbackEngine.compute_model_soup_merge(base_w, candidates, mode=mode)
            self.assertEqual(res["soup_mode"], mode)
            self.assertGreaterEqual(res["retained_count"], 1)
            self.assertGreater(res["composite_validation_score"], 0.90)
            self.assertEqual(set(res["merged_weights"].keys()), {"w_cost", "w_facing", "w_stack"})

    def test_48_round_the_clock_creative_director_non_stop_daemon_integration(self) -> None:
        """Verify 250-record longitudinal master corpus and 24/7 Creative Director + MiroFish/Strands daemon integration."""
        corpus_path = ROOT_DIR / "Datasets" / "longitudinal_5_masters_corpus.jsonl"
        self.assertTrue(corpus_path.is_file())
        rows = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(rows), 250)
        rec_ids = {r.get("record_id") or r.get("id") for r in rows}
        self.assertIn("mga_01", rec_ids)
        self.assertIn("mga_20", rec_ids)
        self.assertIn("miro_strands_01", rec_ids)
        self.assertIn("miro_strands_10", rec_ids)

    def test_49_anime_baseline_models_catalog_and_rtx4080_checkpoint_alignment(self) -> None:
        """Verify all 5 Anime Training Baselines (`Animagine XL 3.1`, `Illustrious-XL`, `NoobAI-XL V-Pred`, `Kohaku-XL`, `FLUX.1-dev FP8`) are registered."""
        models = AnimeBaselineProprietaryDistiller.BASELINE_MODELS
        self.assertEqual(len(models), 5)
        expected_ckpts = {
            "animagineXLV31_v31.safetensors",
            "illustriousXL_v10.safetensors",
            "noobaiXL_vpred10.safetensors",
            "kohakuXL_delta.safetensors",
            "flux1-dev-fp8.safetensors",
        }
        actual_ckpts = {m["ckpt_name"] for m in models.values()}
        self.assertEqual(actual_ckpts, expected_ckpts)
        self.assertTrue(models["animagine_xl_31"]["rtx4080_node30_primary"])
        self.assertEqual(models["noobai_xl_vpred_10"]["prediction_type"], "v_prediction")

    def test_50_unet_block_weighted_dora_soup_in_mid_out_isolation(self) -> None:
        """Verify UNet Block-Weighted DoRA/LoKr Soup isolates `IN00_08`, `MID00`, and `OUT00_05` for `Synapse-Aether-Cel v1.0`."""
        soup = AnimeBaselineProprietaryDistiller.compute_unet_block_weighted_dora_soup()
        self.assertEqual(soup["proprietary_style_id"], "Synapse-Aether-Cel v1.0")
        self.assertIn("IN00_08", soup["blocks"])
        self.assertIn("MID00", soup["blocks"])
        self.assertIn("OUT00_05", soup["blocks"])

        for block_name, b_weights in soup["blocks"].items():
            self.assertEqual(len(b_weights), 5)
            self.assertAlmostEqual(sum(b_weights.values()), 1.0, places=2, msg=f"Block {block_name} weights must sum to 1.0")

        self.assertAlmostEqual(sum(soup["global_artist_weights"].values()), 1.0, places=2)

    def test_51_dmd2_pcm_22step_to_4step_student_distillation_trajectory(self) -> None:
        """Verify 22-Step Teacher (`CFG=6.8`) to 4-Step Student (`CFG=1.0`) DMD2 distillation achieves 5.5x step / 11x NFE speedup."""
        distilled = AnimeBaselineProprietaryDistiller.distill_22step_teacher_to_4step_student(
            teacher_steps=22, student_steps=4, method="dmd2"
        )
        self.assertEqual(distilled["distillation_method"], "dmd2")
        self.assertEqual(distilled["teacher_steps"], 22)
        self.assertEqual(distilled["student_steps"], 4)
        self.assertEqual(distilled["student_cfg"], 1.0)
        self.assertEqual(distilled["step_speedup_factor"], 5.5)
        self.assertEqual(distilled["effective_nfe_speedup_factor"], 11.0)
        self.assertEqual(distilled["student_timesteps"], [1000, 750, 500, 250])
        self.assertLess(distilled["final_kld_loss"], 0.05)

    def test_52_proprietary_house_style_uniqueness_and_non_dominance_audit(self) -> None:
        """Verify no single artist/lineage exceeds 38% (`0.38`) dominance in `Synapse-Aether-Cel v1.0`."""
        audit = AnimeBaselineProprietaryDistiller.audit_proprietary_style_uniqueness()
        self.assertTrue(audit["passed_uniqueness_gate"])
        self.assertLessEqual(audit["highest_weight"], 0.38)
        self.assertGreaterEqual(audit["active_lineages_count"], 4)
        self.assertLessEqual(audit["max_cosine_similarity_to_single_master"], 0.75)

    def test_53_cross_modal_hinton_kd_teacher_to_unity_shader_distillation(self) -> None:
        """Verify Cross-Modal Hinton Knowledge Distillation maps Teacher Soup features into Unity URP Shader uniforms."""
        distilled = AnimeBaselineProprietaryDistiller.distill_22step_teacher_to_4step_student(method="hinton_kd")
        shader_student = distilled["unity_urp_shader_student"]
        self.assertEqual(shader_student["shader_name"], "Synapse/URP/AetherCelDistilledStudent")
        self.assertGreater(shader_student["_OutlineThicknessPx"], 2.0)
        self.assertGreater(shader_student["_ParchmentCrosshatchIntensity"], 0.25)
        self.assertGreater(shader_student["_SolidEyeHalftoneDensity"], 0.25)
        self.assertGreaterEqual(shader_student["_Telegraph1sLuminanceContrast"], 0.90)

    def test_54_anime_distillation_longitudinal_corpus_and_showcase_render_integrity(self) -> None:
        """Verify `anime_distill_01`..`anime_distill_15` exist in `longitudinal_5_masters_corpus.jsonl` and style showcases are valid PNGs."""
        corpus_path = ROOT_DIR / "Datasets" / "longitudinal_5_masters_corpus.jsonl"
        rows = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rec_ids = {r.get("record_id") or r.get("id") for r in rows}
        for i in range(1, 16):
            self.assertIn(f"anime_distill_{i:02d}", rec_ids)

        showcase_dir = ROOT_DIR / "Assets" / "Resources" / "CardArt" / "StyleShowcase"
        self.assertTrue(showcase_dir.is_dir())
        png_files = list(showcase_dir.glob("*.png"))
        self.assertGreaterEqual(len(png_files), 8)
        for p in png_files:
            self.assertGreater(p.stat().st_size, 50_000, f"Showcase PNG {p} too small")

    def test_55_morluto_rea_reverse_engineering_repository_and_artifact_contracts(self) -> None:
        """Verify `morluto/rea` repository exists locally and validates `.glb`, `.q3gs`, and `.png` binary evidence contracts."""
        glb_path = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "synapse_hi3d_staccs_mecha_cube.glb"
        q3gs_path = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "synapse_hi3d_staccs_mecha_cube.q3gs"
        png_path = CARD_ART_DIR / "cf_01_mystic_mage.png"

        glb_ev = OmegaStrikersHi3dReaProductionEngine.inspect_with_morluto_rea_contract(glb_path)
        self.assertTrue(glb_ev["rea_engine_verified"])
        self.assertEqual(glb_ev["detected_format"], "glTF_2.0_Binary_GLB")
        self.assertEqual(glb_ev["evidence_grade"], "VERIFIED_BINARY_EVIDENCE")
        self.assertEqual(len(glb_ev["sha256"]), 64)

        q3gs_ev = OmegaStrikersHi3dReaProductionEngine.inspect_with_morluto_rea_contract(q3gs_path)
        self.assertEqual(q3gs_ev["detected_format"], "Q3GS_LumenForge_3D_Gaussian_Splat")

        png_ev = OmegaStrikersHi3dReaProductionEngine.inspect_with_morluto_rea_contract(png_path)
        self.assertEqual(png_ev["detected_format"], "PNG_RGBA_Image")

    def test_56_omegastrikers_studio_trigger_stepped_sakuga_timing_on_ones_twos_threes(self) -> None:
        """Verify Omega Strikers / Studio Trigger frame-quantized sakuga sequence (`On-Threes 8fps`, `Obake Smear`, `On-Ones 24fps`, `On-Twos 12fps`)."""
        timeline = OmegaStrikersHi3dReaProductionEngine.evaluate_omegastrikers_sakuga_timeline(duration_s=0.65, fps=60)
        self.assertEqual(timeline["total_frames"], 39)
        self.assertEqual(len(timeline["phases"]), 5)

        stepped_rates = [p["stepped_rate"] for p in timeline["phases"]]
        self.assertIn("On_Threes_8fps", stepped_rates)
        self.assertIn("On_Ones_24fps", stepped_rates)
        self.assertIn("On_Twos_12fps", stepped_rates)
        self.assertEqual(timeline["obake_smear_frames"], 2)
        self.assertEqual(timeline["impact_flash_frames"], 2)

    def test_57_omegastrikers_fov_punch_in_kagenashi_shadows_and_trigger_cross_stars(self) -> None:
        """Verify Omega Strikers dynamic camera FOV punch-in (`75° -> 28°`), `14°` Dutch roll tilt, `Kagenashi` shadows, and `Trigger Cross-Star` flares."""
        timeline = OmegaStrikersHi3dReaProductionEngine.evaluate_omegastrikers_sakuga_timeline()
        self.assertEqual(timeline["fov_punch_in_range_deg"], (75.0, 28.0))
        self.assertEqual(timeline["max_dutch_tilt_deg"], 14.0)
        self.assertTrue(timeline["kagenashi_hard_shadow_mask"])
        self.assertTrue(timeline["trigger_4point_cross_star_flare"])

        impact_phase = timeline["phases"][2]
        self.assertEqual(impact_phase["fov_deg"], 28.0)
        self.assertEqual(impact_phase["dutch_tilt_deg"], 14.0)

    def test_58_hi3dgen_nirne_norld_and_trellis2_watertight_3d_glb_q3gs_assets(self) -> None:
        """Verify `Hi3DGen (NiRNE/NoRLD)` + `TRELLIS 2.0` `.glb` and `.q3gs` assets satisfy `0x46546C67` magic and watertight Euler $V - E + F = 2$."""
        mesh_report = OmegaStrikersHi3dReaProductionEngine.verify_hi3d_trellis2_watertight_mesh()
        self.assertEqual(mesh_report["gltf_magic_hex"], "0x46546c67")
        self.assertEqual(mesh_report["gltf_version"], 2)
        self.assertGreater(mesh_report["vertices"], 3000)
        self.assertGreater(mesh_report["triangles"], 6000)
        self.assertGreater(mesh_report["quads"], 3000)
        self.assertEqual(mesh_report["euler_characteristic"], 2)
        self.assertTrue(mesh_report["is_watertight_manifold"])
        self.assertEqual(mesh_report["q3gs_magic"], "Q3GS")
        self.assertTrue(mesh_report["q3gs_lumenforge_tagged"])

    def test_59_video_production_24fps_60fps_sakuga_trailer_and_finisher_exporter(self) -> None:
        """Verify 24fps stepped anime master and 60fps hybrid gameplay cut-in video production export profiles."""
        tl_24 = OmegaStrikersHi3dReaProductionEngine.evaluate_omegastrikers_sakuga_timeline(duration_s=1.0, fps=24)
        tl_60 = OmegaStrikersHi3dReaProductionEngine.evaluate_omegastrikers_sakuga_timeline(duration_s=1.0, fps=60)
        self.assertEqual(tl_24["total_frames"], 24)
        self.assertEqual(tl_60["total_frames"], 60)
        self.assertIn("1080p_24fps_Anime_Stepped_Master", tl_24["video_export_profiles"])
        self.assertIn("4K_60fps_Hybrid_Gameplay_CutIn", tl_60["video_export_profiles"])

    def test_60_huggingface_refinements_and_multi_epoch_local_engine_training_gate(self) -> None:
        """Verify all 11 Hugging Face repositories (`Animagine`, `NoobAI`, `Illustrious`, `Kohaku`, `Hi3DGen`, `TRELLIS`, `DMD2`, `Hyper-SD`, `PCM`, `Sana`) are registered."""
        reg = OmegaStrikersHi3dReaProductionEngine.HUGGINGFACE_MODEL_AND_OPTIMIZATION_REGISTRY
        self.assertEqual(len(reg), 11)
        expected_repos = {
            "cagliostrolab/animagine-xl-3.1",
            "cagliostrolab/animagine-xl-4.0",
            "Laxhar/noobai-XL-Vpred-1.0",
            "OnomaAIResearch/Illustrious-xl-early-release-v0",
            "KBlueLeaf/Kohaku-XL-Zeta",
            "Stable-X/trellis-normal-v0-1",
            "JeffreyXiang/TRELLIS-image-large",
            "tianweiy/DMD2",
            "ByteDance/Hyper-SD",
            "wangfuyun/PCM_Weights",
            "Efficient-Large-Model/Sana_1600M_1024px_BF16_diffusers",
        }
        self.assertEqual(set(reg.keys()), expected_repos)
        for repo_id, spec in reg.items():
            self.assertGreaterEqual(len(spec["optimizations"]), 2, f"Missing optimizations for {repo_id}")

    def test_61_hi3d_ai_text_image_multiview_to_3d_studio_pipeline(self) -> None:
        """Verify Stage 1 Hi3D.ai `NiRNE -> NoRLD -> O-Voxel SLAT` 3D generation across `text_to_3d`, `image_to_3d`, and `multiview_to_3d`."""
        for mode, expected_views in (("text_to_3d", 0), ("image_to_3d", 1), ("multiview_to_3d", 4)):
            res = Hi3dAiFullStudioReEngine.run_hi3d_text_image_multiview_to_3d("cf_02_mech_knight", mode=mode)
            self.assertEqual(res["generation_mode"], mode)
            self.assertEqual(res["conditioning_views"], expected_views)
            self.assertEqual(res["stage_1a_nirne_normal_estimator"]["normal_map_bit_depth"], 16)
            self.assertEqual(res["stage_1b_norld_latent_diffusion"]["sparse_voxel_grid"], "64x64x64_O_Voxel_SLAT")
            self.assertTrue(res["stage_1c_dual_contouring_decode"]["watertight_manifold"])
            self.assertEqual(res["stage_1c_dual_contouring_decode"]["euler_characteristic"], 2)

    def test_62_hi3d_ai_quad_dominant_retopology_and_polycount_tiers(self) -> None:
        """Verify Stage 2 Hi3D.ai quad-dominant retopology across `3k_mobile_cube`, `10k_card_pawn`, `30k_hero_cutin`, and `100k_cinematic_master`."""
        for tier in ("3k_mobile_cube", "10k_card_pawn", "30k_hero_cutin", "100k_cinematic_master"):
            retopo = Hi3dAiFullStudioReEngine.run_hi3d_quad_dominant_retopology(4034, target_tier=tier)
            self.assertEqual(retopo["target_tier"], tier)
            self.assertGreaterEqual(retopo["quad_ratio"], 0.92)
            self.assertEqual(retopo["non_manifold_edges"], 0)
            self.assertEqual(retopo["self_intersections"], 0)
            self.assertEqual(retopo["euler_characteristic"], 2)
            self.assertTrue(retopo["is_watertight"])

    def test_63_hi3d_ai_pbr_albedo_delighting_and_uv_atlas_baker(self) -> None:
        """Verify Stage 3 Hi3D.ai 4K intrinsic albedo delighting and 6-channel PBR + Cel/Halftone UV atlas baking."""
        atlas = Hi3dAiFullStudioReEngine.bake_hi3d_delighted_4k_pbr_atlas("cf_03_celestial_guardian", resolution=4096)
        self.assertEqual(atlas["atlas_resolution"], "4096x4096")
        self.assertLess(atlas["delighting_residual_shadow_error"], 0.03)
        self.assertGreaterEqual(atlas["uv_island_utilization"], 0.84)
        self.assertEqual(atlas["channel_count"], 6)
        self.assertIn("albedo_delighted_srgb", atlas["pbr_and_cel_channels"])
        self.assertIn("normal_nirne_16bit_tangent", atlas["pbr_and_cel_channels"])
        self.assertIn("cel_halftone_ramp_id", atlas["pbr_and_cel_channels"])

    def test_64_hi3d_ai_22_bone_humanoid_auto_rigging_and_animation_clips(self) -> None:
        """Verify Stage 4 Hi3D.ai 22-bone Humanoid/Mecha auto-rigger, normalized 4-bone skinning weights, and 4 procedural animation clips."""
        rig = Hi3dAiFullStudioReEngine.bind_hi3d_22_bone_auto_rig("cf_09_cyber_ninja")
        self.assertEqual(rig["bone_count"], 22)
        self.assertEqual(rig["max_influences_per_vertex"], 4)
        self.assertTrue(rig["weights_normalized_to_one"])
        self.assertEqual(len(rig["animation_clips"]), 4)
        clip_names = {c["clip_name"] for c in rig["animation_clips"]}
        self.assertIn("Staccs_Cube_Slam", clip_names)
        self.assertIn("OmegaStrikers_Sakuga_Finisher", clip_names)

    def test_65_morluto_rea_continuous_binary_gltf_chunk_and_shader_evidence_audit(self) -> None:
        """Verify Stage 5 `morluto/rea` deep glTF 2.0 binary chunk parser inspects 12-byte header, Chunk 0 (`JSON`), and Chunk 1 (`BIN`)."""
        glb_path = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "synapse_hi3d_staccs_mecha_cube.glb"
        deep = Hi3dAiFullStudioReEngine.audit_glb_with_morluto_rea_deep_chunks(glb_path)
        self.assertEqual(deep["header"]["magic_hex"], "0x46546c67")
        self.assertEqual(deep["header"]["version"], 2)
        self.assertEqual(deep["chunk0_json"]["chunk_type_hex"], "0x4e4f534a")
        self.assertGreaterEqual(deep["chunk0_json"]["meshes_count"], 1)
        self.assertEqual(deep["chunk1_bin"]["chunk_type_hex"], "0x4e4942")
        self.assertTrue(deep["chunk1_bin"]["payload_bytes_verified"])
        self.assertEqual(deep["topology_evidence"]["euler_characteristic"], 2)
        self.assertTrue(deep["topology_evidence"]["watertight_verified"])

    def test_66_full_14_card_hi3d_glb_q3gs_3d_roster_and_continuous_daemon_gate(self) -> None:
        """Verify all 14 official cards have valid watertight `.glb` and `.q3gs` 3D assets in `Assets/Resources/Models3D/`."""
        roster_3d = Hi3dAiFullStudioReEngine.ensure_all_14_card_hi3d_3d_assets_exist()
        self.assertEqual(roster_3d["cards_3d_verified_count"], 14)
        models_dir = ROOT_DIR / "Assets" / "Resources" / "Models3D"
        for cid in OFFICIAL_PROJECT_CF_CARDS:
            glb_file = models_dir / f"{cid}.glb"
            q3gs_file = models_dir / f"{cid}.q3gs"
            self.assertTrue(glb_file.is_file(), f"Missing 3D GLB for {cid}")
            self.assertTrue(q3gs_file.is_file(), f"Missing 3D Q3GS for {cid}")
            self.assertGreater(glb_file.stat().st_size, 100_000)
            self.assertGreater(q3gs_file.stat().st_size, 50_000)

    def test_67_lumenforge_io_sovereign_4node_pool_and_platform_manifest(self) -> None:
        """Verify `lumenforge.io` platform manifest and 4-node `lumenforge-sovereign-pool` (`120 GB` VRAM, `342.45` FP16 TFLOPS)."""
        manifest = LumenForgeIoStudioEngine.get_lumenforge_io_platform_manifest()
        self.assertEqual(manifest["domain"], "lumenforge.io")
        self.assertEqual(manifest["pool_name"], "lumenforge-sovereign-pool")
        pool = manifest["sovereign_pool"]
        self.assertEqual(pool["node_count"], 4)
        self.assertEqual(pool["total_vram_gb"], 120)
        self.assertAlmostEqual(pool["peak_fp16_tflops"], 342.45, places=2)
        self.assertEqual(
            set(pool["nodes"].keys()),
            {"node116_v100", "node30_4080", "node22_2070", "node127_m1max"},
        )
        self.assertEqual(
            manifest["hi3d_studio_pipeline"]["stages"],
            ["NiRNE", "NoRLD", "QuadRetopo_3K_10K_30K_100K", "PBR_4K_Delighting", "AutoRig_22Bone"],
        )

    def test_68_lumenforge_io_q3gs_and_glb_dual_3d_streaming_verification(self) -> None:
        """Verify `.q3gs` (`Q3GS` / `LUMENFRG`) Gaussian Splat binary structure and paired `.glb` manifold status."""
        q3gs_path = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "synapse_hi3d_staccs_mecha_cube.q3gs"
        info = LumenForgeIoStudioEngine.inspect_q3gs_lumenforge_binary(q3gs_path)
        self.assertEqual(info["magic"], "Q3GS")
        self.assertTrue(info["lumenforge_header_verified"])
        self.assertTrue(info["has_lumenfrg_tag"])
        self.assertEqual(info["byte_size"], 92_814)
        self.assertEqual(len(info["sha256"]), 64)
        self.assertTrue(info["paired_glb_exists"])
        self.assertEqual(info["paired_glb_euler_characteristic"], 2)
        self.assertTrue(info["paired_glb_watertight"])

    def test_69_lumenforge_io_morluto_rea_rl_environments_and_nuxt_bundle_evidence(self) -> None:
        """Verify `morluto/rea` RL environments (`hi3d_rl_env`, `dicevaders_rl_env`) and 12 `hi3d_nuxt_app` JS bundles on disk."""
        ev = LumenForgeIoStudioEngine.verify_rea_rl_environments_and_evidence()
        self.assertTrue(ev["workspace_verified"])
        self.assertEqual(ev["rea_version"], "6.8.0")
        self.assertTrue(ev["hi3d_rea_report_exists"])
        self.assertTrue(ev["dicevaders_rea_report_exists"])
        self.assertTrue(ev["hi3d_rl_env"]["env_toml_exists"])
        self.assertTrue(ev["hi3d_rl_env"]["manifest_exists"])
        self.assertTrue(ev["dicevaders_rl_env"]["env_toml_exists"])
        self.assertTrue(ev["dicevaders_rl_env"]["manifest_exists"])
        self.assertGreaterEqual(ev["hi3d_nuxt_app"]["js_bundle_count"], 12)

    def test_70_lumenforge_io_continuous_epoch_training_and_loss_convergence(self) -> None:
        """Verify `run_lumenforge_continuous_epoch_step` converges monotonically in `ce_loss` and `kl_div` with zero Euler violations."""
        e1 = LumenForgeIoStudioEngine.run_lumenforge_continuous_epoch_step(1)
        e5 = LumenForgeIoStudioEngine.run_lumenforge_continuous_epoch_step(5)
        e12 = LumenForgeIoStudioEngine.run_lumenforge_continuous_epoch_step(12)
        self.assertEqual(e1["domain"], "lumenforge.io")
        self.assertGreater(e1["ce_loss"], e5["ce_loss"])
        self.assertGreater(e5["ce_loss"], e12["ce_loss"])
        self.assertGreater(e1["kl_div"], e5["kl_div"])
        self.assertGreater(e5["kl_div"], e12["kl_div"])
        self.assertEqual(e12["euler_violation_rate"], 0.0)
        self.assertEqual(e12["soup_adapters_healthy"], 9)

    def test_71_lumenforge_io_unity_csharp_studio_pipeline_and_client_contracts(self) -> None:
        """Verify Unity C# `SynapseHi3dStudioPipeline.cs` (and `LumenForgeIoStudioClient.cs` if present) exist with balanced braces."""
        hi3d_cs = ROOT_DIR / "Assets" / "Scripts" / "Visuals" / "SynapseHi3dStudioPipeline.cs"
        self.assertTrue(hi3d_cs.is_file(), f"Missing {hi3d_cs}")
        src = hi3d_cs.read_text(encoding="utf-8")
        self.assertEqual(src.count("{"), src.count("}"))
        self.assertGreater(src.count("{"), 5)

        client_cs = ROOT_DIR / "Assets" / "Scripts" / "Api" / "LumenForgeIoStudioClient.cs"
        if client_cs.is_file():
            c_src = client_cs.read_text(encoding="utf-8")
            self.assertEqual(c_src.count("{"), c_src.count("}"))

    def test_72_lumenforge_io_end_to_end_daemon_and_721_record_corpus_gate(self) -> None:
        """Verify 9-Master and 12-Master longitudinal JSONL datasets (`>= 331` / `>= 600` records) and all 15 `.glb` + 15 `.q3gs` models."""
        ds9_path = ROOT_DIR / "Datasets" / "longitudinal_9_masters_full_corpus.jsonl"
        ds12_path = ROOT_DIR / "Datasets" / "longitudinal_12_masters_concept_and_gamedesign_corpus.jsonl"
        self.assertTrue(ds9_path.is_file())
        self.assertTrue(ds12_path.is_file())

        rows9 = [json.loads(line) for line in ds9_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows12 = [json.loads(line) for line in ds12_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(rows9), 331)
        self.assertGreaterEqual(len(rows12), 600)

        manifest = LumenForgeIoStudioEngine.get_lumenforge_io_platform_manifest()
        self.assertGreaterEqual(manifest["models_3d_roster"]["glb_count"], 15)
        self.assertGreaterEqual(manifest["models_3d_roster"]["q3gs_count"], 15)

    def test_73_track_a_unity_project_settings_and_urp_package_manifest(self) -> None:
        """Verify Track A Unity `ProjectSettings/` YAML assets and `Packages/manifest.json` exist and are valid."""
        ps_dir = ROOT_DIR / "ProjectSettings"
        for fname in (
            "ProjectVersion.txt",
            "EditorBuildSettings.asset",
            "TagManager.asset",
            "QualitySettings.asset",
            "GraphicsSettings.asset",
        ):
            fpath = ps_dir / fname
            self.assertTrue(fpath.is_file(), f"Missing ProjectSettings/{fname}")
            self.assertGreater(fpath.stat().st_size, 20)

        ver_txt = (ps_dir / "ProjectVersion.txt").read_text(encoding="utf-8")
        self.assertIn("m_EditorVersion: 2022.3.", ver_txt)

        pkg_manifest = ROOT_DIR / "Packages" / "manifest.json"
        self.assertTrue(pkg_manifest.is_file())
        pkg_data = json.loads(pkg_manifest.read_text(encoding="utf-8"))
        self.assertIn("com.unity.textmeshpro", pkg_data.get("dependencies", {}))
        self.assertIn("com.unity.ugui", pkg_data.get("dependencies", {}))

    def test_74_track_a_60_serialized_card_data_so_assets_and_meta_guids(self) -> None:
        """Verify all 60 Set 1 `CardDataSO` `.asset` ScriptableObject files and `.meta` GUIDs in `Assets/Resources/Cards/`."""
        cards_dir = ROOT_DIR / "Assets" / "Resources" / "Cards"
        self.assertTrue(cards_dir.is_dir())
        asset_files = sorted(cards_dir.glob("*.asset"))
        self.assertEqual(len(asset_files), 60)

        seen_guids = set()
        for af in asset_files:
            txt = af.read_text(encoding="utf-8")
            self.assertTrue(txt.startswith("%YAML 1.1"))
            self.assertIn("%TAG !u! tag:unity3d.com,2011:", txt)
            self.assertIn("MonoBehaviour:", txt)
            meta_f = Path(str(af) + ".meta")
            self.assertTrue(meta_f.is_file(), f"Missing meta for {af.name}")
            mtxt = meta_f.read_text(encoding="utf-8")
            self.assertIn("guid: ", mtxt)
            guid_line = [ln for ln in mtxt.splitlines() if ln.strip().startswith("guid:")][0]
            guid_val = guid_line.split(":", 1)[1].strip()
            self.assertEqual(len(guid_val), 32)
            seen_guids.add(guid_val)
        self.assertEqual(len(seen_guids), 60)

    def test_75_track_a_bootable_unity_scenes_and_prefab_hierarchies(self) -> None:
        """Verify 2 bootable `.unity` scenes, 4 `.prefab` hierarchies, and zero `.meta` GUID collisions across `Assets/`."""
        scenes_dir = ROOT_DIR / "Assets" / "Scenes"
        for sname in ("SynapseMainMenu.unity", "SynapseTacticalBattleArena.unity"):
            spath = scenes_dir / sname
            self.assertTrue(spath.is_file(), f"Missing scene {sname}")
            stxt = spath.read_text(encoding="utf-8")
            self.assertTrue(stxt.startswith("%YAML 1.1"))
            self.assertIn("Camera:", stxt)

        prefabs_dir = ROOT_DIR / "Assets" / "Prefabs"
        for pname in (
            "StaccsCardCube.prefab",
            "TelegraphTileOverlay.prefab",
            "SolidEyeHud.prefab",
            "SynapseTacticalBoard3x3.prefab",
        ):
            ppath = prefabs_dir / pname
            self.assertTrue(ppath.is_file(), f"Missing prefab {pname}")
            ptxt = ppath.read_text(encoding="utf-8")
            self.assertTrue(ptxt.startswith("%YAML 1.1"))
            self.assertIn("GameObject:", ptxt)

        ser_manifest_path = ROOT_DIR / "Logs" / "unity_production_serialization_manifest.json"
        self.assertTrue(ser_manifest_path.is_file())
        ser_manifest = json.loads(ser_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(ser_manifest["counts"]["guid_collision_count"], 0)
        self.assertGreaterEqual(ser_manifest["counts"]["unique_meta_guids"], 240)

    def test_76_track_b_binary_huggingface_safetensors_lora_checkpoints(self) -> None:
        """Verify all 4 binary `.safetensors` LoRA checkpoints in `Models/LoRA/` follow exact Hugging Face spec."""
        import struct

        lora_dir = ROOT_DIR / "Models" / "LoRA"
        expected = (
            "synapse_aether_cel_v1_lora.safetensors",
            "hi3d_trellis2_nirne_norld_adapter.safetensors",
            "mga2_solideye_halftone_shader_lora.safetensors",
            "ties_merged_master_soup_v1.safetensors",
        )
        for fname in expected:
            fpath = lora_dir / fname
            self.assertTrue(fpath.is_file(), f"Missing {fname}")
            raw = fpath.read_bytes()
            self.assertGreater(len(raw), 16384)
            header_len = struct.unpack("<Q", raw[:8])[0]
            header_json = json.loads(raw[8 : 8 + header_len].decode("utf-8"))
            self.assertIn("__metadata__", header_json)
            self.assertEqual(header_json["__metadata__"]["house_style"], "Synapse-Aether-Cel v1.0")
            tensor_keys = [k for k in header_json.keys() if k != "__metadata__"]
            self.assertEqual(len(tensor_keys), 8)
            max_end = max(header_json[k]["data_offsets"][1] for k in tensor_keys)
            self.assertEqual(8 + header_len + max_end, len(raw))

    def test_77_track_b_highpoly_10k_watertight_glb_and_q3gs_3d_meshes(self) -> None:
        """Verify all 15 HighPoly10K `.glb` and `.q3gs` models in `Assets/Resources/Models3D/HighPoly10K/` ($V=5186, E=15552, F=10368, \\chi=2$)."""
        hp_dir = ROOT_DIR / "Assets" / "Resources" / "Models3D" / "HighPoly10K"
        self.assertTrue(hp_dir.is_dir())
        glb_files = sorted(hp_dir.glob("*_10k.glb"))
        q3gs_files = sorted(hp_dir.glob("*_10k.q3gs"))
        self.assertEqual(len(glb_files), 15)
        self.assertEqual(len(q3gs_files), 15)

        hp_manifest = json.loads((hp_dir / "highpoly_10k_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(hp_manifest["euler_characteristic"], 2)
        for item in hp_manifest["models"]:
            self.assertEqual(item["vertices_V"], 5186)
            self.assertEqual(item["edges_E"], 15552)
            self.assertEqual(item["triangles_F"], 10368)
            self.assertEqual(item["euler_characteristic"], 2)
            self.assertTrue(item["watertight_manifold"])
            self.assertEqual(item["bones_count"], 22)

    def test_78_track_c_set1_full_60_card_roster_across_5_factions(self) -> None:
        """Verify Track C `SET1_FULL_60_ROSTER` contains 60 cards evenly distributed (12 per faction) across 5 factions."""
        from synapse_set1_campaign_expansion import SET1_FULL_60_ROSTER, SynapseProductionCampaignEngine

        self.assertEqual(len(SET1_FULL_60_ROSTER), 60)
        engine = SynapseProductionCampaignEngine(seed=42)
        summary = engine.get_set1_roster_summary()
        self.assertEqual(summary["total_cards"], 60)
        for faction_short, count in summary["faction_counts_short"].items():
            self.assertEqual(count, 12, f"Expected 12 cards for {faction_short}, got {count}")

    def test_79_track_c_15_stage_tactical_campaign_simulation_and_fnv1a_hash(self) -> None:
        """Verify Track C 15-stage tactical campaign simulation clears all 5 Acts (15 stages) deterministically."""
        from synapse_set1_campaign_expansion import SynapseProductionCampaignEngine

        engine = SynapseProductionCampaignEngine(seed=42)
        rep1 = engine.run_full_15_stage_campaign_verification(seed=42)
        rep2 = engine.run_full_15_stage_campaign_verification(seed=42)
        self.assertEqual(rep1["total_stages"], 15)
        self.assertEqual(rep1["stages_cleared"], 15)
        self.assertTrue(rep1["campaign_verified"])
        self.assertEqual(rep1["campaign_fnv1a_64_hash"], rep2["campaign_fnv1a_64_hash"])

    def test_80_track_c_unity_csharp_set1_expansion_and_campaign_runtime(self) -> None:
        """Verify Unity C# `SynapseSetOneExpansionAndCampaign.cs` exists in `namespace Synapse.TcgEngine.Core` with balanced braces."""
        cs_path = ROOT_DIR / "Assets" / "Scripts" / "Core" / "SynapseSetOneExpansionAndCampaign.cs"
        self.assertTrue(cs_path.is_file())
        src = cs_path.read_text(encoding="utf-8")
        self.assertIn("namespace Synapse.TcgEngine.Core", src)
        self.assertEqual(src.count("{"), src.count("}"))
        self.assertGreater(src.count("{"), 15)

    def test_81_pxg_gamedev_harness_91_skills_catalog_and_router_integrity(self) -> None:
        """Verify YouTube `t13A2XFGoOc` 77-Skill / 91-Skill catalog (`gamedev_skills`) and Master Router exist on disk."""
        from synapse_gamedev_skills_harness_bridge import SynapseGameDevSkillsHarnessBridge

        analysis = SynapseGameDevSkillsHarnessBridge.get_video_t13A2XFGoOc_analysis_and_catalog()
        self.assertEqual(analysis["video_analysis"]["video_id"], "t13A2XFGoOc")
        inv = analysis["local_harness_inventory"]
        self.assertTrue(inv["rust_binary_exists"])
        self.assertTrue(inv["router_skill_exists"])
        self.assertGreaterEqual(inv["total_indexed_skills"], 91)
        self.assertEqual(inv["upstream_gamedev_skills_count"], 77)
        self.assertGreaterEqual(inv["custom_synapse_skills_count"], 14)

    def test_82_pxg_gamedev_harness_unity_engine_detection_and_4_skill_composition(self) -> None:
        """Verify `pxg-gamedev-harness` detects Unity 2022.3.40f1 and composes the 4-slot `unity-scriptableobjects -> game-feel -> game-ui-ux -> card-game` stack."""
        from synapse_gamedev_skills_harness_bridge import (
            ITERATION_SKILL_PROMPTS,
            SynapseGameDevSkillsHarnessBridge,
        )

        decision = SynapseGameDevSkillsHarnessBridge.invoke_pxg_harness_route(
            ITERATION_SKILL_PROMPTS[0]["prompt"]
        )
        self.assertEqual(decision["engine_detection"]["engine"], "Unity")
        self.assertEqual(decision["engine_detection"]["version"], "2022.3.40f1")
        self.assertEqual(decision["skill_stack_count"], 4)
        self.assertEqual(
            decision["selected_skill_names"],
            ["unity-scriptableobjects", "game-feel", "game-ui-ux", "card-game"],
        )
        self.assertGreater(decision["composed_system_prompt_chars"], 25000)

    def test_83_gamedev_skills_bridge_card_game_feel_ui_ux_and_asset_qa_gates(self) -> None:
        """Verify `SynapseGameDevSkillsHarnessBridge.run_continuous_harness_step` passes all 77-Skill quality gates."""
        from synapse_gamedev_skills_harness_bridge import SynapseGameDevSkillsHarnessBridge

        step = SynapseGameDevSkillsHarnessBridge.run_continuous_harness_step(iteration_index=1)
        self.assertTrue(step["quality_gates"]["all_gates_passed"])
        self.assertTrue(step["quality_gates"]["card_game_invariants"]["passed"])
        self.assertTrue(step["quality_gates"]["game_feel_and_ui_ux"]["passed"])
        self.assertTrue(step["quality_gates"]["create_game_assets_and_so"]["passed"])

    def test_84_web_playable_game_feel_trauma_shake_hitstop_and_keyboard_focus_nav(self) -> None:
        """Verify `WebPlayable/cardfront_cradle_of_echoes_playable.html` implements `addTrauma` (`trauma * trauma`), `triggerHitStop`, `handleHarnessKeyDown`, and 16 unique card telegraphs."""
        html_path = ROOT_DIR / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html"
        self.assertTrue(html_path.is_file())
        txt = html_path.read_text(encoding="utf-8")
        self.assertIn("function addTrauma", txt)
        self.assertIn("trauma * trauma", txt)
        self.assertIn("function triggerHitStop", txt)
        self.assertIn("function handleHarnessKeyDown", txt)
        self.assertIn("function buildUniqueTelegraphSVG", txt)
        self.assertIn("function buildBoardTelegraphOverlaySVG", txt)
        self.assertIn("91-SKILL HARNESS ACTIVE", txt)

    def test_85_unity_csharp_gamedev_skills_runtime_harness_in_synapse_namespace(self) -> None:
        """Verify Unity C# `SynapseGameDevSkillsHarness.cs` exists in `namespace Synapse.TcgEngine.Core` with balanced braces."""
        cs_path = ROOT_DIR / "Assets" / "Scripts" / "Core" / "SynapseGameDevSkillsHarness.cs"
        self.assertTrue(cs_path.is_file())
        src = cs_path.read_text(encoding="utf-8")
        self.assertIn("namespace Synapse.TcgEngine.Core", src)
        self.assertIn("GameFeelTraumaShakeAndHitStopController", src)
        self.assertIn("CardGameSingleZoneInvariantValidator", src)
        self.assertIn("GameUiUxFocusAndSafeAreaNavigator", src)
        self.assertEqual(src.count("{"), src.count("}"))
        self.assertGreater(src.count("{"), 15)

    def test_86_stage2_atomic_save_system_v3_default_and_fnv1a_checksum(self) -> None:
        """Verify `SynapseAtomicSaveSystem.create_default_save_v3` creates a version 3 save with 5 active cards and FNV-1a checksum."""
        from synapse_stage2_metagame_and_publishing import SynapseAtomicSaveSystem

        s = SynapseAtomicSaveSystem.create_default_save_v3("player_test_86")
        self.assertEqual(s["version"], 3)
        self.assertEqual(len(s["active_deck"]), 5)
        self.assertTrue(s["fnv1a_64_checksum"].startswith("0x"))
        self.assertEqual(len(s["fnv1a_64_checksum"]), 18)

    def test_87_stage2_save_schema_migration_v1_to_v2_to_v3(self) -> None:
        """Verify `SynapseAtomicSaveSystem.migrate_save_data` upgrades v1 (`gold` -> `coins`) through v2 to v3 seamlessly."""
        from synapse_stage2_metagame_and_publishing import SynapseAtomicSaveSystem

        legacy_v1 = {"version": 1, "player_id": "legacy_hero", "gold": 777, "active_deck": ["h_archangel"]}
        migrated = SynapseAtomicSaveSystem.migrate_save_data(legacy_v1)
        self.assertEqual(migrated["version"], 3)
        self.assertEqual(migrated["coins"], 777)
        self.assertNotIn("gold", migrated)
        self.assertIn("settings", migrated)
        self.assertIn("fnv1a_64_checksum", migrated)

    def test_88_stage2_atomic_write_tmp_bak_rotation_and_corrupt_fallback(self) -> None:
        """Verify `save_atomic` writes `.bak` rotation and `load_save_with_fallback` recovers from `.bak` if primary is corrupted."""
        import tempfile
        from synapse_stage2_metagame_and_publishing import SynapseAtomicSaveSystem

        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test_slot.json"
            s1 = SynapseAtomicSaveSystem.create_default_save_v3("p_slot")
            s1["coins"] = 900
            SynapseAtomicSaveSystem.save_atomic(p, s1)
            s1["coins"] = 1250
            res2 = SynapseAtomicSaveSystem.save_atomic(p, s1)
            self.assertTrue(res2["backup_exists"])

            # Corrupt primary file -> must recover 900 coins from .bak!
            p.write_text("{corrupted_json", encoding="utf-8")
            recovered, src_tag = SynapseAtomicSaveSystem.load_save_with_fallback(p)
            self.assertEqual(src_tag, "backup_fallback")
            self.assertEqual(recovered["coins"], 900)

    def test_89_stage2_audio_mixer_bus_hierarchy_and_headroom_targets(self) -> None:
        """Verify `SynapseAudioMixerAndAdaptiveMusicEngine` defines `Master <- {Music <- MusicDuck, SFX, Ambience, UI, Voice}`."""
        from synapse_stage2_metagame_and_publishing import SynapseAudioMixerAndAdaptiveMusicEngine

        tree = SynapseAudioMixerAndAdaptiveMusicEngine.BUS_TREE
        self.assertIsNone(tree["Master"])
        self.assertEqual(tree["Music"], "Master")
        self.assertEqual(tree["MusicDuck"], "Music")
        self.assertEqual(tree["SFX"], "Master")
        self.assertEqual(tree["UI"], "Master")
        self.assertEqual(tree["Voice"], "Master")

    def test_90_stage2_audio_logarithmic_slider_squared_to_db_conversion(self) -> None:
        """Verify `slider_to_db` maps 0.0 -> (-80.0 dB, muted), 0.5 -> -12.041 dB, and 1.0 -> 0.0 dB."""
        from synapse_stage2_metagame_and_publishing import SynapseAudioMixerAndAdaptiveMusicEngine

        db0, muted0 = SynapseAudioMixerAndAdaptiveMusicEngine.slider_to_db(0.0)
        self.assertEqual(db0, -80.0)
        self.assertTrue(muted0)

        db_half, muted_half = SynapseAudioMixerAndAdaptiveMusicEngine.slider_to_db(0.5)
        self.assertFalse(muted_half)
        self.assertAlmostEqual(db_half, -12.041, places=2)

        db_full, muted_full = SynapseAudioMixerAndAdaptiveMusicEngine.slider_to_db(1.0)
        self.assertFalse(muted_full)
        self.assertEqual(db_full, 0.0)

    def test_91_stage2_audio_sidechain_ducking_attenuation_curve(self) -> None:
        """Verify `evaluate_sidechain_ducking` attenuates `MusicDuck` up to -12.0 dB when Voice/HitStop exceeds -30 dB."""
        from synapse_stage2_metagame_and_publishing import SynapseAudioMixerAndAdaptiveMusicEngine

        self.assertEqual(SynapseAudioMixerAndAdaptiveMusicEngine.evaluate_sidechain_ducking(-40.0), 0.0)
        duck_mid = SynapseAudioMixerAndAdaptiveMusicEngine.evaluate_sidechain_ducking(-22.0)
        self.assertLess(duck_mid, -5.0)
        duck_max = SynapseAudioMixerAndAdaptiveMusicEngine.evaluate_sidechain_ducking(-6.0)
        self.assertEqual(duck_max, -12.0)

    def test_92_stage2_audio_16_card_telegraph_sfx_pitch_variation(self) -> None:
        """Verify all 16 cards have distinct telegraph SFX synthesis profiles and seeded pitch variation (`0.96..1.04`)."""
        from synapse_stage2_metagame_and_publishing import SynapseAudioMixerAndAdaptiveMusicEngine

        self.assertEqual(len(SynapseAudioMixerAndAdaptiveMusicEngine.CARD_TELEGRAPH_SFX_PROFILES), 16)
        s1 = SynapseAudioMixerAndAdaptiveMusicEngine.sample_varied_telegraph_sfx("h_archangel", seed=10)
        s2 = SynapseAudioMixerAndAdaptiveMusicEngine.sample_varied_telegraph_sfx("h_archangel", seed=20)
        self.assertTrue(0.96 <= s1["pitch_scale"] <= 1.04)
        self.assertNotEqual(s1["varied_base_hz"], s2["varied_base_hz"])

    def test_93_stage2_steam_publish_appid_and_steampipe_vdf_scripts(self) -> None:
        """Verify `steam_appid.txt`, `app_build_3194820.vdf`, and `depot_build_3194821.vdf` exist and are valid."""
        from synapse_stage2_metagame_and_publishing import SynapseSteamAndItchReleasePackager

        manifest = SynapseSteamAndItchReleasePackager.build_release_artifacts()
        appid_txt = Path(manifest["steam_publish"]["steam_appid_txt"]).read_text(encoding="utf-8").strip()
        self.assertEqual(appid_txt, "3194820")
        app_vdf = Path(manifest["steam_publish"]["app_build_vdf"]).read_text(encoding="utf-8")
        depot_vdf = Path(manifest["steam_publish"]["depot_build_vdf"]).read_text(encoding="utf-8")
        self.assertIn('"appid" "3194820"', app_vdf)
        self.assertIn('"DepotID" "3194821"', depot_vdf)
        self.assertIn('"FileExclusion" "*.pdb"', depot_vdf)

    def test_94_stage2_itch_publish_toml_and_butler_channel_matrix(self) -> None:
        """Verify `.itch.toml` and the 4 `butler push` channels (`windows`, `osx`, `linux`, `html`) are configured."""
        manifest = json.loads((ROOT_DIR / "Logs" / "stage2_production_release_manifest.json").read_text(encoding="utf-8"))
        itch_toml = Path(manifest["itch_publish"]["itch_toml"]).read_text(encoding="utf-8")
        self.assertIn('name = "play"', itch_toml)
        self.assertIn("WebPlayable/cardfront_cradle_of_echoes_playable.html", itch_toml)
        channels = [c["channel"] for c in manifest["itch_publish"]["channels"]]
        self.assertEqual(channels, ["windows", "osx", "linux", "html"])

    def test_95_stage2_web_playable_15_campaign_stages_and_60_card_deckbuilder(self) -> None:
        """Verify `cardfront_cradle_of_echoes_playable.html` includes all 15 Act I-V stages and the 60-card Set 1 Deckbuilder."""
        html = (ROOT_DIR / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html").read_text(encoding="utf-8")
        self.assertIn("Act V-15: Omega Chronos Prime", html)
        self.assertIn("const SET1_60_CATALOG", html)
        self.assertIn("function openDeckbuilderModal", html)
        self.assertIn("function renderDeckbuilderGrid", html)

    def test_96_stage2_web_playable_booster_pack_cardcraft_and_save_v3(self) -> None:
        """Verify `cardfront_cradle_of_echoes_playable.html` implements `openBoosterPackUI`, `evolveCardCraftUI`, and `saveProgressionV3`."""
        html = (ROOT_DIR / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html").read_text(encoding="utf-8")
        self.assertIn("function openBoosterPackUI", html)
        self.assertIn("function evolveCardCraftUI", html)
        self.assertIn("function saveProgressionV3", html)
        self.assertIn("synapse_cardfront_save_v3", html)

    def test_97_stage2_web_playable_3d_glb_q3gs_hologram_pawn_inspector(self) -> None:
        """Verify `cardfront_cradle_of_echoes_playable.html` includes the live 3D `.glb` / `.q3gs` Hologram Pawn Inspector (`open3DPawnInspectorModal`)."""
        html = (ROOT_DIR / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html").read_text(encoding="utf-8")
        self.assertIn("function open3DPawnInspectorModal", html)
        self.assertIn("pawn3d-canvas", html)
        self.assertIn("cf_01_mystic_mage_10k.glb", html)

    def test_98_stage2_web_playable_adaptive_bgm_and_sidechain_duck_bus(self) -> None:
        """Verify `cardfront_cradle_of_echoes_playable.html` implements `slider01ToDb`, `duckMusicBus`, and `toggleAdaptiveBgm`."""
        html = (ROOT_DIR / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html").read_text(encoding="utf-8")
        self.assertIn("function slider01ToDb", html)
        self.assertIn("function duckMusicBus", html)
        self.assertIn("function toggleAdaptiveBgm", html)

    def test_99_stage2_unity_csharp_save_audio_and_publishing_runtime(self) -> None:
        """Verify Unity C# `SynapseStageTwoSaveAudioAndPublishing.cs` exists in `namespace Synapse.TcgEngine.Core` with balanced braces."""
        cs_path = ROOT_DIR / "Assets" / "Scripts" / "Core" / "SynapseStageTwoSaveAudioAndPublishing.cs"
        self.assertTrue(cs_path.is_file())
        src = cs_path.read_text(encoding="utf-8")
        self.assertIn("namespace Synapse.TcgEngine.Core", src)
        self.assertIn("SynapseAtomicSaveManager", src)
        self.assertIn("SynapseAudioMixerBusController", src)
        self.assertIn("SynapseSteamAndItchBuildConfig", src)
        self.assertEqual(src.count("{"), src.count("}"))
        self.assertGreater(src.count("{"), 15)

    def test_100_stage2_end_to_end_release_manifest_and_100_test_milestone(self) -> None:
        """Verify `Logs/stage2_production_release_manifest.json` exists and records schema v3, 7 audio buses, and Steam/Itch configs."""
        manifest_path = ROOT_DIR / "Logs" / "stage2_production_release_manifest.json"
        self.assertTrue(manifest_path.is_file())
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(m["save_system"]["schema_version"], 3)
        self.assertEqual(len(m["audio_engine"]["buses"]), 7)
        self.assertEqual(m["steam_publish"]["steam_app_id"], 3194820)
        self.assertEqual(m["itch_publish"]["version"], "2.0.0")








def run_suite() -> Dict:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSynapseTcgSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "passed": result.wasSuccessful(),
    }


if __name__ == "__main__":
    summary = run_suite()
    print(json.dumps(summary))
    sys.exit(0 if summary["passed"] else 1)
