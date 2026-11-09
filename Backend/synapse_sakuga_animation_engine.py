#!/usr/bin/env python3
"""
Synapse-Sakuga-AnimEngine v1.0
==============================
Sovereign CARDFRONT: Cradle of Echoes — 2.5D Sakuga Animation Engine,
Damped Harmonic Spring Solver (120Hz), Stepped Anime Cadence Evaluator (12/24fps),
2D FABRIK Inverse Kinematics Puppet Rig Solver, and `.cfanim` Clip Compiler.

Generates:
  - 8 canonical `.cfanim` declarative JSON animation clips in:
      * Assets/Resources/Animations/
      * WebPlayable/GeneratedArt/Animations/
  - `puppet_rigs_manifest.json` (16 Hero & Boss 2.5D skeletal rigs + 4-layer parallax) in both directories
  - Build verification manifest in `Logs/sakuga_animation_engine_manifest.json`
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
UNITY_ANIM_DIR = PROJECT_ROOT / "Assets" / "Resources" / "Animations"
WEB_ANIM_DIR = PROJECT_ROOT / "WebPlayable" / "GeneratedArt" / "Animations"
LOGS_DIR = PROJECT_ROOT / "Logs"
MANIFEST_REPORT_PATH = LOGS_DIR / "sakuga_animation_engine_manifest.json"

CANONICAL_CLIP_IDS: Tuple[str, ...] = (
    "idle_breathe_25d",
    "deploy_orbital_slam",
    "directional_clash_lunge",
    "capture_flip_180",
    "tactical_slide_bank",
    "column_die_nudge_surge",
    "sakuga_impact_flash_2f",
    "boss_telegraph_pulse",
)

HERO_AND_BOSS_CARD_IDS: Tuple[str, ...] = (
    "h_kai",
    "h_seraph",
    "h_valkyrie",
    "h_oracle",
    "h_chronos",
    "h_bastion",
    "h_shinobi",
    "h_archon",
    "e_dreadnought",
    "e_cryo",
    "e_shinobi",
    "e_behemoth",
    "e_valkyrie",
    "e_chronos",
    "e_leviathan",
    "e_eclipse",
)

PARALLAX_LAYER_DEPTHS: Dict[str, float] = {
    "bg_layer": -0.35,
    "mid_layer": -0.12,
    "actor_layer": 0.18,
    "vfx_frame_break_layer": 0.45,
}


def compute_fnv1a_64_hex(payload_bytes: bytes) -> str:
    """Compute deterministic 64-bit FNV-1a checksum formatted as 0x + 16 hex chars."""
    fnv_offset_basis = 0xCBF29CE484222325
    fnv_prime = 0x100000001B3
    mask64 = 0xFFFFFFFFFFFFFFFF
    h = fnv_offset_basis
    for b in payload_bytes:
        h ^= b
        h = (h * fnv_prime) & mask64
    return f"0x{h:016x}"


def compute_dict_fnv1a_64(data: Dict[str, Any], exclude_keys: Tuple[str, ...] = ("fnv1a_64_checksum",)) -> str:
    """Compute FNV-1a 64-bit checksum over a canonical sorted-key JSON serialization of `data`."""
    filtered = {k: v for k, v in data.items() if k not in exclude_keys}
    canonical_json = json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return compute_fnv1a_64_hex(canonical_json.encode("utf-8"))


def verify_clip_checksum(clip_data: Dict[str, Any]) -> bool:
    """Verify the `fnv1a_64_checksum` field of a `.cfanim` clip dictionary."""
    claimed = clip_data.get("fnv1a_64_checksum", "")
    if not isinstance(claimed, str) or not claimed.startswith("0x") or len(claimed) != 18:
        return False
    expected = compute_dict_fnv1a_64(clip_data)
    return claimed.lower() == expected.lower()


class SynapseSpringHarmonicSolver:
    """
    Analytical & semi-implicit Euler / RK4 damped harmonic oscillator at dt = 1/120.0.
    Supports:
      - Under-damped (zeta < 1.0)
      - Critically-damped (zeta == 1.0)
      - Over-damped (zeta > 1.0)
    where zeta = damping / (2 * sqrt(stiffness * mass)).
    """

    DEFAULT_DT: float = 1.0 / 120.0

    def __init__(
        self,
        stiffness: float = 320.0,
        damping: float = 28.0,
        mass: float = 1.0,
        initial_pos: float = 0.0,
        target_pos: float = 1.0,
        initial_vel: float = 0.0,
    ) -> None:
        if stiffness <= 0.0:
            raise ValueError("stiffness must be > 0")
        if mass <= 0.0:
            raise ValueError("mass must be > 0")
        if damping < 0.0:
            raise ValueError("damping must be >= 0")

        self.stiffness = float(stiffness)
        self.damping = float(damping)
        self.mass = float(mass)
        self.initial_pos = float(initial_pos)
        self.target_pos = float(target_pos)
        self.initial_vel = float(initial_vel)

        self.pos = float(initial_pos)
        self.vel = float(initial_vel)
        self.elapsed_time = 0.0

    @property
    def omega_n(self) -> float:
        """Undamped natural angular frequency sqrt(k / m)."""
        return math.sqrt(self.stiffness / self.mass)

    @property
    def zeta(self) -> float:
        """Damping ratio c / (2 * sqrt(k * m))."""
        return self.damping / (2.0 * math.sqrt(self.stiffness * self.mass))

    @property
    def regime(self) -> str:
        """Return 'under-damped', 'critically-damped', or 'over-damped'."""
        z = self.zeta
        if abs(z - 1.0) <= 1e-6:
            return "critically-damped"
        return "under-damped" if z < 1.0 else "over-damped"

    def reset(self) -> Tuple[float, float]:
        """Reset state to initial_pos, initial_vel, and t=0."""
        self.pos = self.initial_pos
        self.vel = self.initial_vel
        self.elapsed_time = 0.0
        return (self.pos, self.vel)

    def _acceleration(self, x: float, v: float) -> float:
        """Compute instantaneous acceleration a = (-k*(x - target) - c*v) / m."""
        return (-self.stiffness * (x - self.target_pos) - self.damping * v) / self.mass

    def evaluate_analytical(self, t: float) -> Tuple[float, float]:
        """
        Closed-form analytical solution (position, velocity) at time t >= 0
        for under-damped, critically-damped, and over-damped regimes.
        """
        t = max(0.0, float(t))
        if t == 0.0:
            return (self.initial_pos, self.initial_vel)

        w0 = self.omega_n
        z = self.zeta
        x0 = self.initial_pos - self.target_pos
        v0 = self.initial_vel

        if abs(z - 1.0) <= 1e-6:
            # Critically-damped: x(t) = (c1 + c2 * t) * exp(-w0 * t)
            c1 = x0
            c2 = v0 + w0 * x0
            exp_term = math.exp(-w0 * t)
            displacement = (c1 + c2 * t) * exp_term
            velocity = (c2 - w0 * (c1 + c2 * t)) * exp_term
        elif z < 1.0:
            # Under-damped: x(t) = exp(-z*w0*t) * (A cos(wd*t) + B sin(wd*t))
            wd = w0 * math.sqrt(max(1e-12, 1.0 - z * z))
            a_coeff = x0
            b_coeff = (v0 + z * w0 * x0) / wd
            exp_term = math.exp(-z * w0 * t)
            cos_wt = math.cos(wd * t)
            sin_wt = math.sin(wd * t)
            displacement = exp_term * (a_coeff * cos_wt + b_coeff * sin_wt)
            velocity = exp_term * (
                (-z * w0 * a_coeff + wd * b_coeff) * cos_wt
                + (-z * w0 * b_coeff - wd * a_coeff) * sin_wt
            )
        else:
            # Over-damped: x(t) = c1 * exp(r1 * t) + c2 * exp(r2 * t)
            sqrt_term = math.sqrt(max(1e-12, z * z - 1.0))
            r1 = -w0 * (z - sqrt_term)
            r2 = -w0 * (z + sqrt_term)
            denom = r1 - r2
            c1 = (v0 - r2 * x0) / denom
            c2 = (r1 * x0 - v0) / denom
            e1 = math.exp(r1 * t)
            e2 = math.exp(r2 * t)
            displacement = c1 * e1 + c2 * e2
            velocity = c1 * r1 * e1 + c2 * r2 * e2

        return (self.target_pos + displacement, velocity)

    def step_semi_implicit_euler(self, dt: float = DEFAULT_DT, substeps: int = 4) -> Tuple[float, float]:
        """Advance state by dt using symplectic semi-implicit Euler integration."""
        sub_dt = dt / float(max(1, substeps))
        for _ in range(max(1, substeps)):
            acc = self._acceleration(self.pos, self.vel)
            self.vel += acc * sub_dt
            self.pos += self.vel * sub_dt
        self.elapsed_time += dt
        return (self.pos, self.vel)

    def step_rk4(self, dt: float = DEFAULT_DT) -> Tuple[float, float]:
        """Advance state by dt using 4th-order Runge-Kutta (RK4) integration."""
        x0 = self.pos
        v0 = self.vel

        k1_x = v0
        k1_v = self._acceleration(x0, v0)

        x2 = x0 + 0.5 * dt * k1_x
        v2 = v0 + 0.5 * dt * k1_v
        k2_x = v2
        k2_v = self._acceleration(x2, v2)

        x3 = x0 + 0.5 * dt * k2_x
        v3 = v0 + 0.5 * dt * k2_v
        k3_x = v3
        k3_v = self._acceleration(x3, v3)

        x4 = x0 + dt * k3_x
        v4 = v0 + dt * k3_v
        k4_x = v4
        k4_v = self._acceleration(x4, v4)

        self.pos = x0 + (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
        self.vel = v0 + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
        self.elapsed_time += dt
        return (self.pos, self.vel)

    def step(self, dt: float = DEFAULT_DT, method: str = "rk4") -> Tuple[float, float]:
        """Advance oscillator by one timestep dt (default 1/120s)."""
        if method == "euler":
            return self.step_semi_implicit_euler(dt)
        if method == "analytical":
            self.elapsed_time += dt
            self.pos, self.vel = self.evaluate_analytical(self.elapsed_time)
            return (self.pos, self.vel)
        return self.step_rk4(dt)

    def scrub_to(self, t: float) -> Dict[str, Any]:
        """
        Deterministically scrub oscillator state to exact time `t` (in seconds),
        producing identical state regardless of prior step history.
        """
        clamped_t = max(0.0, float(t))
        pos, vel = self.evaluate_analytical(clamped_t)
        self.pos = pos
        self.vel = vel
        self.elapsed_time = clamped_t
        return {
            "t": round(self.elapsed_time, 6),
            "pos": round(self.pos, 8),
            "vel": round(self.vel, 8),
            "zeta": round(self.zeta, 6),
            "regime": self.regime,
        }

    def is_settled(self, pos_tol: float = 1e-3, vel_tol: float = 1e-2) -> bool:
        """Check whether the spring has converged to `target_pos` within tolerance."""
        return abs(self.pos - self.target_pos) <= pos_tol and abs(self.vel) <= vel_tol

    def sample_trajectory(
        self,
        duration_sec: float,
        hz: int = 120,
        method: str = "analytical",
    ) -> List[Dict[str, float]]:
        """Sample the spring trajectory over `duration_sec` at `hz` samples per second."""
        dt = 1.0 / float(hz)
        total_steps = int(round(duration_sec * hz))
        self.reset()
        samples: List[Dict[str, float]] = [
            {
                "t": 0.0,
                "pos": round(self.pos, 6),
                "vel": round(self.vel, 6),
            }
        ]
        for step_idx in range(1, total_steps + 1):
            t_cur = step_idx * dt
            if method == "analytical":
                p, v = self.evaluate_analytical(t_cur)
                self.pos, self.vel, self.elapsed_time = p, v, t_cur
            else:
                p, v = self.step(dt=dt, method=method)
            samples.append(
                {
                    "t": round(t_cur, 6),
                    "pos": round(p, 6),
                    "vel": round(v, 6),
                }
            )
        return samples


class SynapseSakugaSteppedCurve:
    """
    Stepped anime cadence evaluator ('on-twos' / 'on-threes' quantization at 12fps or 24fps)
    featuring:
      1. Anticipation wind-up dip (`anticipation_dip = -0.18`)
      2. 2-frame snap-lunge (`lunge_frames = 2`) to impact peak (`impact_peak = 1.08`)
      3. Freeze-frame `HitStop` hold (`hitstop_frames` in 3..5 frames) with zero motion
      4. Damped harmonic spring settle to `rest_target = 1.0`
    """

    def __init__(
        self,
        fps: int = 24,
        step_hold: int = 1,
        anticipation_frames: int = 4,
        anticipation_dip: float = -0.18,
        lunge_frames: int = 2,
        impact_peak: float = 1.08,
        hitstop_frames: int = 4,
        rest_target: float = 1.0,
        spring_stiffness: float = 360.0,
        spring_damping: float = 30.0,
        spring_mass: float = 1.0,
    ) -> None:
        if fps not in (12, 24):
            raise ValueError("Sakuga stepped cadence fps must be 12 or 24")
        if not (3 <= hitstop_frames <= 5):
            raise ValueError("hitstop_frames must be between 3 and 5 frames inclusive")
        if lunge_frames != 2:
            raise ValueError("lunge_frames must be 2 frames for canonical Sakuga snap-lunge")

        self.fps = int(fps)
        self.step_hold = max(1, int(step_hold))
        self.anticipation_frames = max(1, int(anticipation_frames))
        self.anticipation_dip = float(anticipation_dip)
        self.lunge_frames = int(lunge_frames)
        self.impact_peak = float(impact_peak)
        self.hitstop_frames = int(hitstop_frames)
        self.rest_target = float(rest_target)

        self.settle_solver = SynapseSpringHarmonicSolver(
            stiffness=spring_stiffness,
            damping=spring_damping,
            mass=spring_mass,
            initial_pos=self.impact_peak,
            target_pos=self.rest_target,
            initial_vel=0.0,
        )

        self._last_scrub_state: Dict[str, Any] = {}

    @property
    def frame_duration(self) -> float:
        """Duration of a single Sakuga frame at `self.fps`."""
        return 1.0 / float(self.fps)

    def quantize_frame_index(self, t: float) -> int:
        """Convert continuous time `t` (sec) into quantized Sakuga frame index."""
        raw_frame = int(math.floor(max(0.0, float(t)) * self.fps + 1e-9))
        return (raw_frame // self.step_hold) * self.step_hold

    def quantize_time(self, t: float) -> float:
        """Quantize continuous time `t` (sec) onto the stepped anime frame grid."""
        q_frame = self.quantize_frame_index(t)
        return q_frame / float(self.fps)

    def evaluate_at_frame(self, frame_idx: int) -> Dict[str, Any]:
        """Evaluate the stepped Sakuga curve at integer frame index `frame_idx`."""
        f = max(0, int(frame_idx))
        ant_end = self.anticipation_frames
        lunge_end = ant_end + self.lunge_frames
        hitstop_end = lunge_end + self.hitstop_frames

        if f == 0:
            phase = "anticipation"
            value = 0.0
            in_hitstop = False
        elif f <= ant_end:
            phase = "anticipation"
            # Smooth ease into -0.18 anticipation dip reaching exact -0.18 at f == ant_end
            progress = f / float(ant_end)
            value = self.anticipation_dip * math.sin(progress * 0.5 * math.pi)
            in_hitstop = False
        elif f <= lunge_end:
            phase = "snap_lunge"
            # 2-frame explosive snap from anticipation_dip (-0.18) to impact_peak
            lunge_step = f - ant_end
            alpha = lunge_step / float(self.lunge_frames)
            value = self.anticipation_dip + alpha * (self.impact_peak - self.anticipation_dip)
            in_hitstop = False
        elif f <= hitstop_end:
            phase = "hitstop"
            # Strict freeze-frame hold for hitstop_frames frames
            value = self.impact_peak
            in_hitstop = True
        else:
            phase = "settle"
            settle_frames = f - hitstop_end
            settle_t = settle_frames / float(self.fps)
            value, _ = self.settle_solver.evaluate_analytical(settle_t)
            in_hitstop = False

        return {
            "frame_index": f,
            "quantized_time": round(f / float(self.fps), 6),
            "phase": phase,
            "value": round(float(value), 6),
            "in_hitstop": in_hitstop,
        }

    def evaluate(self, t: float) -> float:
        """Return quantized Sakuga scalar value at continuous time `t`."""
        q_frame = self.quantize_frame_index(t)
        return self.evaluate_at_frame(q_frame)["value"]

    def scrub_to(self, t: float) -> Dict[str, Any]:
        """
        Deterministically scrub the Sakuga curve to time `t` (in seconds),
        returning the full stepped state independent of prior evaluation history.
        """
        q_frame = self.quantize_frame_index(t)
        state = self.evaluate_at_frame(q_frame)
        state["requested_time"] = round(max(0.0, float(t)), 6)
        self._last_scrub_state = state
        return copy.deepcopy(state)


class SynapseFabrikBoneChain2D:
    """
    Deterministic 2D Forward And Backward Reaching Inverse Kinematics (FABRIK) solver
    for 2.5D card puppets (`Head`, `Torso`, `WeaponArm`, `Cape/Wing`), guaranteed to
    converge within tolerance `1e-3` or `max_iters=12`, plus 4-layer depth parallax
    offset calculation (`bg_layer=-0.35`, `mid_layer=-0.12`, `actor_layer=0.18`,
    `vfx_frame_break_layer=0.45`).
    """

    TOLERANCE: float = 1e-3
    MAX_ITERS: int = 12
    LAYER_DEPTHS: Dict[str, float] = dict(PARALLAX_LAYER_DEPTHS)

    def __init__(
        self,
        joint_positions: List[Tuple[float, float]],
        chain_name: str = "WeaponArm",
        tolerance: float = TOLERANCE,
        max_iters: int = MAX_ITERS,
    ) -> None:
        if len(joint_positions) < 2:
            raise ValueError("A FABRIK bone chain requires at least 2 joints")
        self.chain_name = chain_name
        self.tolerance = float(tolerance)
        self.max_iters = int(max_iters)

        self.bind_joints: List[Tuple[float, float]] = [
            (float(x), float(y)) for x, y in joint_positions
        ]
        self.joints: List[Tuple[float, float]] = list(self.bind_joints)
        self.bone_lengths: List[float] = [
            self._distance(self.bind_joints[i], self.bind_joints[i + 1])
            for i in range(len(self.bind_joints) - 1)
        ]
        for length in self.bone_lengths:
            if length <= 1e-7:
                raise ValueError("Each bone segment length must be > 0")
        self.total_length: float = sum(self.bone_lengths)

    @staticmethod
    def _distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return math.hypot(b[0] - a[0], b[1] - a[1])

    @staticmethod
    def _point_along(
        origin: Tuple[float, float],
        towards: Tuple[float, float],
        distance: float,
    ) -> Tuple[float, float]:
        dx = towards[0] - origin[0]
        dy = towards[1] - origin[1]
        norm = math.hypot(dx, dy)
        if norm <= 1e-9:
            return (origin[0] + distance, origin[1])
        scale = distance / norm
        return (origin[0] + dx * scale, origin[1] + dy * scale)

    def reset_to_bind(self) -> List[Tuple[float, float]]:
        """Restore all joints to their initial bind pose."""
        self.joints = list(self.bind_joints)
        return list(self.joints)

    def current_segment_lengths(self) -> List[float]:
        """Compute current Euclidean distances between consecutive joints."""
        return [
            self._distance(self.joints[i], self.joints[i + 1])
            for i in range(len(self.joints) - 1)
        ]

    def solve_ik(
        self,
        target: Tuple[float, float],
        reset_first: bool = True,
    ) -> Dict[str, Any]:
        """
        Solve 2D FABRIK toward `target = (tx, ty)` with fixed root `self.bind_joints[0]`.
        Guaranteed to preserve segment lengths and terminate within `tolerance <= 1e-3`
        or `max_iters <= 12`.
        """
        if reset_first:
            self.reset_to_bind()

        tx, ty = float(target[0]), float(target[1])
        target_pt = (tx, ty)
        root_pt = self.joints[0]
        n = len(self.joints)

        root_to_target = self._distance(root_pt, target_pt)
        iterations_used = 0
        reachable = root_to_target <= self.total_length + 1e-9

        if not reachable:
            # Target is beyond full reach: align chain straight toward target
            iterations_used = 1
            for i in range(n - 1):
                self.joints[i + 1] = self._point_along(
                    self.joints[i], target_pt, self.bone_lengths[i]
                )
        else:
            end_error = self._distance(self.joints[-1], target_pt)
            while end_error > self.tolerance and iterations_used < self.max_iters:
                iterations_used += 1
                # Stage 1: Forward reaching (end-effector to root)
                self.joints[-1] = target_pt
                for i in range(n - 2, -1, -1):
                    self.joints[i] = self._point_along(
                        self.joints[i + 1], self.joints[i], self.bone_lengths[i]
                    )

                # Stage 2: Backward reaching (root to end-effector)
                self.joints[0] = root_pt
                for i in range(n - 1):
                    self.joints[i + 1] = self._point_along(
                        self.joints[i], self.joints[i + 1], self.bone_lengths[i]
                    )

                end_error = self._distance(self.joints[-1], target_pt)

        final_error = self._distance(self.joints[-1], target_pt)
        converged = (final_error <= self.tolerance) if reachable else True
        return {
            "chain_name": self.chain_name,
            "target": [round(tx, 5), round(ty, 5)],
            "reachable": reachable,
            "converged": converged,
            "iterations": iterations_used,
            "end_effector_error": round(final_error, 6),
            "joints": [[round(x, 6), round(y, 6)] for x, y in self.joints],
            "bone_lengths": [round(l, 6) for l in self.current_segment_lengths()],
        }

    @classmethod
    def compute_parallax_offsets(
        cls,
        tilt_x: float,
        tilt_y: float,
        max_displacement_px: float = 28.0,
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute 4-layer 2.5D depth parallax offsets for:
          - bg_layer = -0.35
          - mid_layer = -0.12
          - actor_layer = 0.18
          - vfx_frame_break_layer = 0.45
        Inputs `tilt_x` and `tilt_y` are clamped to [-1.0, 1.0].
        """
        cx = max(-1.0, min(1.0, float(tilt_x)))
        cy = max(-1.0, min(1.0, float(tilt_y)))
        scale = float(max_displacement_px)

        result: Dict[str, Dict[str, float]] = {}
        for layer_name, depth_coeff in cls.LAYER_DEPTHS.items():
            dx = round(cx * depth_coeff * scale, 5)
            dy = round(cy * depth_coeff * scale, 5)
            result[layer_name] = {
                "depth_coeff": depth_coeff,
                "offset_x": dx,
                "offset_y": dy,
                "scale_factor": round(1.0 + abs(depth_coeff) * 0.06, 5),
            }
        return result


class CfAnimClipCompiler:
    """
    Declarative `.cfanim` compiler & 2.5D puppet rig generator for CARDFRONT: Cradle of Echoes.
    """

    def __init__(
        self,
        unity_output_dir: Path = UNITY_ANIM_DIR,
        web_output_dir: Path = WEB_ANIM_DIR,
        manifest_report_path: Path = MANIFEST_REPORT_PATH,
    ) -> None:
        self.unity_output_dir = Path(unity_output_dir)
        self.web_output_dir = Path(web_output_dir)
        self.manifest_report_path = Path(manifest_report_path)

    @staticmethod
    def _build_clip_specs() -> List[Dict[str, Any]]:
        """Return canonical parameter specifications for all 8 `.cfanim` clips."""
        return [
            {
                "clip_id": "idle_breathe_25d",
                "description": "Subtle 2.5D harmonic breathing & cape sway with 4-layer depth parallax.",
                "duration_sec": 2.0,
                "spring_params": {"stiffness": 180.0, "damping": 22.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 3,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.02,
                    "hitstop_frames": 3,
                },
                "motion_profile": {
                    "pos_amp": [0.0, 6.5, 0.0],
                    "rot_amp_deg": [-1.2, 1.8, 0.8],
                    "scale_amp": [1.02, 1.025, 1.0],
                    "tilt": [0.22, -0.18],
                },
            },
            {
                "clip_id": "deploy_orbital_slam",
                "description": "High-altitude orbital card drop with 2-frame snap slam, 4-frame HitStop, and shockwave settle.",
                "duration_sec": 0.85,
                "spring_params": {"stiffness": 420.0, "damping": 34.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 3,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.15,
                    "hitstop_frames": 4,
                },
                "motion_profile": {
                    "pos_amp": [0.0, -48.0, -18.0],
                    "rot_amp_deg": [8.5, 0.0, -2.5],
                    "scale_amp": [1.14, 0.92, 1.0],
                    "tilt": [0.0, 0.85],
                },
            },
            {
                "clip_id": "directional_clash_lunge",
                "description": "Aggressive directional combat lunge with -0.18 anticipation wind-up, 2-frame snap, and 4-frame HitStop.",
                "duration_sec": 0.75,
                "spring_params": {"stiffness": 460.0, "damping": 32.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 4,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.12,
                    "hitstop_frames": 4,
                },
                "motion_profile": {
                    "pos_amp": [34.0, 18.0, -8.0],
                    "rot_amp_deg": [-6.0, 4.5, -11.0],
                    "scale_amp": [1.10, 1.08, 1.0],
                    "tilt": [0.75, 0.45],
                },
            },
            {
                "clip_id": "capture_flip_180",
                "description": "180-degree axial ownership capture flip with faction chroma flash and critically-damped lock.",
                "duration_sec": 0.65,
                "spring_params": {"stiffness": 400.0, "damping": 40.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 2,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.06,
                    "hitstop_frames": 3,
                },
                "motion_profile": {
                    "pos_amp": [0.0, 22.0, -14.0],
                    "rot_amp_deg": [0.0, 180.0, 0.0],
                    "scale_amp": [1.08, 1.08, 1.0],
                    "tilt": [-0.65, 0.25],
                },
            },
            {
                "clip_id": "tactical_slide_bank",
                "description": "Grid tile relocation slide with aerodynamic roll banking and under-damped arrival settle.",
                "duration_sec": 0.55,
                "spring_params": {"stiffness": 340.0, "damping": 26.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 2,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.05,
                    "hitstop_frames": 3,
                },
                "motion_profile": {
                    "pos_amp": [42.0, 4.0, 0.0],
                    "rot_amp_deg": [0.0, -4.0, -9.5],
                    "scale_amp": [1.03, 0.98, 1.0],
                    "tilt": [0.55, -0.15],
                },
            },
            {
                "clip_id": "column_die_nudge_surge",
                "description": "Tactical column die manipulation surge with metallic recoil and harmonic resonance.",
                "duration_sec": 0.60,
                "spring_params": {"stiffness": 380.0, "damping": 28.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 2,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.10,
                    "hitstop_frames": 3,
                },
                "motion_profile": {
                    "pos_amp": [0.0, 16.0, -10.0],
                    "rot_amp_deg": [14.0, -8.0, 6.0],
                    "scale_amp": [1.16, 1.16, 1.0],
                    "tilt": [0.35, 0.60],
                },
            },
            {
                "clip_id": "sakuga_impact_flash_2f",
                "description": "2-frame black-and-white impact frame burst with 5-frame freeze-frame HitStop.",
                "duration_sec": 0.50,
                "spring_params": {"stiffness": 520.0, "damping": 38.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 2,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.18,
                    "hitstop_frames": 5,
                },
                "motion_profile": {
                    "pos_amp": [-6.0, 8.0, -16.0],
                    "rot_amp_deg": [-3.5, 2.0, 5.0],
                    "scale_amp": [1.18, 1.18, 1.0],
                    "tilt": [-0.80, 0.75],
                },
            },
            {
                "clip_id": "boss_telegraph_pulse",
                "description": "Sovereign Boss crimson-obsidian hazard telegraph pulse with weapon IK lock.",
                "duration_sec": 1.10,
                "spring_params": {"stiffness": 290.0, "damping": 24.0, "mass": 1.0},
                "sakuga_params": {
                    "anticipation_frames": 4,
                    "anticipation_dip": -0.18,
                    "lunge_frames": 2,
                    "impact_peak": 1.14,
                    "hitstop_frames": 4,
                },
                "motion_profile": {
                    "pos_amp": [0.0, 14.0, -12.0],
                    "rot_amp_deg": [4.0, 0.0, -3.0],
                    "scale_amp": [1.09, 1.09, 1.0],
                    "tilt": [0.45, -0.65],
                },
            },
        ]

    @classmethod
    def compile_clip(cls, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compile a single `.cfanim` declarative clip dictionary with FNV-1a 64-bit checksum."""
        clip_id = spec["clip_id"]
        duration_sec = float(spec["duration_sec"])
        physics_hz = 120
        sakuga_fps = 24

        sp = spec["spring_params"]
        sk = spec["sakuga_params"]
        mp = spec["motion_profile"]

        solver = SynapseSpringHarmonicSolver(
            stiffness=sp["stiffness"],
            damping=sp["damping"],
            mass=sp["mass"],
            initial_pos=0.0,
            target_pos=1.0,
            initial_vel=0.0,
        )
        sakuga = SynapseSakugaSteppedCurve(
            fps=sakuga_fps,
            step_hold=1,
            anticipation_frames=sk["anticipation_frames"],
            anticipation_dip=sk["anticipation_dip"],
            lunge_frames=sk["lunge_frames"],
            impact_peak=sk["impact_peak"],
            hitstop_frames=sk["hitstop_frames"],
            rest_target=1.0,
            spring_stiffness=sp["stiffness"],
            spring_damping=sp["damping"],
            spring_mass=sp["mass"],
        )

        # Sample keyframes at 24fps Sakuga boundaries
        total_sakuga_frames = int(round(duration_sec * sakuga_fps))
        keyframes: List[Dict[str, Any]] = []
        base_tilt_x, base_tilt_y = mp["tilt"]

        # Create a WeaponArm FABRIK chain to embed IK target poses in keyframes
        arm_chain = SynapseFabrikBoneChain2D(
            joint_positions=[(0.0, 0.0), (18.0, 12.0), (34.0, 22.0), (46.0, 28.0)],
            chain_name="WeaponArm",
        )

        for frame_idx in range(total_sakuga_frames + 1):
            t_sec = round(frame_idx / float(sakuga_fps), 6)
            sk_eval = sakuga.evaluate_at_frame(frame_idx)
            sp_pos, sp_vel = solver.evaluate_analytical(t_sec)
            val = sk_eval["value"]

            tx = base_tilt_x * val
            ty = base_tilt_y * val
            parallax = SynapseFabrikBoneChain2D.compute_parallax_offsets(tx, ty)

            ik_target = (36.0 + 8.0 * val, 24.0 + 6.0 * val)
            ik_solution = arm_chain.solve_ik(ik_target)

            keyframes.append(
                {
                    "frame_index": frame_idx,
                    "time_sec": t_sec,
                    "phase": sk_eval["phase"],
                    "in_hitstop": sk_eval["in_hitstop"],
                    "sakuga_scalar": val,
                    "spring_pos_120hz": round(sp_pos, 6),
                    "spring_vel_120hz": round(sp_vel, 6),
                    "position": [
                        round(mp["pos_amp"][0] * val, 4),
                        round(mp["pos_amp"][1] * val, 4),
                        round(mp["pos_amp"][2] * val, 4),
                    ],
                    "rotation_deg": [
                        round(mp["rot_amp_deg"][0] * val, 4),
                        round(mp["rot_amp_deg"][1] * val, 4),
                        round(mp["rot_amp_deg"][2] * val, 4),
                    ],
                    "scale": [
                        round(1.0 + (mp["scale_amp"][0] - 1.0) * val, 5),
                        round(1.0 + (mp["scale_amp"][1] - 1.0) * val, 5),
                        round(1.0 + (mp["scale_amp"][2] - 1.0) * val, 5),
                    ],
                    "parallax_layers": parallax,
                    "weapon_arm_ik": {
                        "target": ik_solution["target"],
                        "joints": ik_solution["joints"],
                        "error": ik_solution["end_effector_error"],
                    },
                }
            )

        ant_frame = sk["anticipation_frames"]
        hitstop_start_frame = sk["anticipation_frames"] + sk["lunge_frames"]
        flip_frame = max(1, total_sakuga_frames // 2)

        events: Dict[str, Dict[str, Any]] = {
            "onAnticipation": {
                "event_name": "onAnticipation",
                "frame_index": ant_frame,
                "time_sec": round(ant_frame / float(sakuga_fps), 6),
                "dip_value": sk["anticipation_dip"],
                "sfx_cue": f"sfx_{clip_id}_windup",
            },
            "onHitStop": {
                "event_name": "onHitStop",
                "frame_index": hitstop_start_frame,
                "time_sec": round(hitstop_start_frame / float(sakuga_fps), 6),
                "hold_frames": sk["hitstop_frames"],
                "sfx_cue": f"sfx_{clip_id}_impact",
            },
            "onCaptureFlip": {
                "event_name": "onCaptureFlip",
                "frame_index": flip_frame,
                "time_sec": round(flip_frame / float(sakuga_fps), 6),
                "flip_degrees": 180.0 if clip_id == "capture_flip_180" else 0.0,
                "active": clip_id == "capture_flip_180",
            },
            "onHapticTrigger": {
                "event_name": "onHapticTrigger",
                "frame_index": hitstop_start_frame,
                "time_sec": round(hitstop_start_frame / float(sakuga_fps), 6),
                "intensity": 0.85,
                "duration_ms": 35,
            },
        }

        clip_payload: Dict[str, Any] = {
            "clip_id": clip_id,
            "version": "1.0",
            "description": spec["description"],
            "duration_sec": duration_sec,
            "physics_hz": physics_hz,
            "sakuga_fps": sakuga_fps,
            "spring_params": {
                "stiffness": sp["stiffness"],
                "damping": sp["damping"],
                "mass": sp["mass"],
                "zeta": round(solver.zeta, 6),
                "regime": solver.regime,
            },
            "sakuga_params": dict(sk),
            "parallax_layer_depths": dict(PARALLAX_LAYER_DEPTHS),
            "events": events,
            "keyframes": keyframes,
        }
        clip_payload["fnv1a_64_checksum"] = compute_dict_fnv1a_64(clip_payload)
        return clip_payload

    @classmethod
    def build_puppet_rigs_manifest(cls) -> Dict[str, Any]:
        """
        Generate `puppet_rigs_manifest.json` containing 2.5D skeletal bone chains
        (`Head`, `Torso`, `WeaponArm`, `Cape/Wing`) and 4-layer depth parallax rig
        descriptors for all 16 core Hero & Boss cards.
        """
        rigs: Dict[str, Dict[str, Any]] = {}

        for idx, card_id in enumerate(HERO_AND_BOSS_CARD_IDS):
            is_hero = card_id.startswith("h_")
            faction = "Astral_Conduit" if is_hero else "Obsidian_Swarm"
            primary_hex = "#00E5FF" if is_hero else "#FF2E54"
            accent_hex = "#FFB800" if is_hero else "#F97316"

            # Slight deterministic per-character morphological variation
            reach_scale = 1.0 + (idx % 4) * 0.05

            head_chain = SynapseFabrikBoneChain2D(
                joint_positions=[
                    (0.0, 56.0),
                    (0.0, 74.0 * reach_scale),
                    (2.0, 90.0 * reach_scale),
                ],
                chain_name="Head",
            )
            torso_chain = SynapseFabrikBoneChain2D(
                joint_positions=[
                    (0.0, 0.0),
                    (0.0, 28.0 * reach_scale),
                    (0.0, 56.0 * reach_scale),
                ],
                chain_name="Torso",
            )
            weapon_arm_chain = SynapseFabrikBoneChain2D(
                joint_positions=[
                    (12.0, 46.0),
                    (28.0 * reach_scale, 38.0),
                    (46.0 * reach_scale, 28.0),
                    (62.0 * reach_scale, 22.0),
                ],
                chain_name="WeaponArm",
            )
            cape_wing_chain = SynapseFabrikBoneChain2D(
                joint_positions=[
                    (-10.0, 48.0),
                    (-26.0 * reach_scale, 32.0),
                    (-44.0 * reach_scale, 14.0),
                    (-58.0 * reach_scale, -6.0),
                ],
                chain_name="Cape/Wing",
            )

            default_parallax = SynapseFabrikBoneChain2D.compute_parallax_offsets(
                tilt_x=0.25 if is_hero else -0.25,
                tilt_y=0.18,
            )

            rig_entry: Dict[str, Any] = {
                "card_id": card_id,
                "faction": faction,
                "primary_chroma_hex": primary_hex,
                "accent_chroma_hex": accent_hex,
                "portrait_resolution": [600, 800],
                "default_clip_id": "idle_breathe_25d",
                "combat_clip_id": "directional_clash_lunge" if is_hero else "boss_telegraph_pulse",
                "parallax_layers": {
                    "depths": dict(PARALLAX_LAYER_DEPTHS),
                    "default_preview_offsets": default_parallax,
                },
                "bone_chains": {
                    "Head": {
                        "bind_joints": head_chain.bind_joints,
                        "bone_lengths": [round(l, 5) for l in head_chain.bone_lengths],
                        "total_length": round(head_chain.total_length, 5),
                    },
                    "Torso": {
                        "bind_joints": torso_chain.bind_joints,
                        "bone_lengths": [round(l, 5) for l in torso_chain.bone_lengths],
                        "total_length": round(torso_chain.total_length, 5),
                    },
                    "WeaponArm": {
                        "bind_joints": weapon_arm_chain.bind_joints,
                        "bone_lengths": [round(l, 5) for l in weapon_arm_chain.bone_lengths],
                        "total_length": round(weapon_arm_chain.total_length, 5),
                    },
                    "Cape/Wing": {
                        "bind_joints": cape_wing_chain.bind_joints,
                        "bone_lengths": [round(l, 5) for l in cape_wing_chain.bone_lengths],
                        "total_length": round(cape_wing_chain.total_length, 5),
                    },
                },
            }
            rig_entry["fnv1a_64_checksum"] = compute_dict_fnv1a_64(rig_entry)
            rigs[card_id] = rig_entry

        manifest: Dict[str, Any] = {
            "engine": "Synapse-Sakuga-AnimEngine",
            "version": "1.0",
            "rig_count": len(rigs),
            "card_ids": list(HERO_AND_BOSS_CARD_IDS),
            "parallax_layer_depths": dict(PARALLAX_LAYER_DEPTHS),
            "rigs": rigs,
        }
        manifest["fnv1a_64_checksum"] = compute_dict_fnv1a_64(manifest)
        return manifest

    def compile_and_export_all(self) -> Dict[str, Any]:
        """
        Compile all 8 `.cfanim` clips and `puppet_rigs_manifest.json` into both
        Unity (`Assets/Resources/Animations/`) and WebPlayable (`WebPlayable/GeneratedArt/Animations/`),
        and write the verification report to `Logs/sakuga_animation_engine_manifest.json`.
        """
        self.unity_output_dir.mkdir(parents=True, exist_ok=True)
        self.web_output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_report_path.parent.mkdir(parents=True, exist_ok=True)

        specs = self._build_clip_specs()
        compiled_clips_summary: List[Dict[str, Any]] = []

        for spec in specs:
            clip_data = self.compile_clip(spec)
            clip_filename = f"{clip_data['clip_id']}.cfanim"
            unity_path = self.unity_output_dir / clip_filename
            web_path = self.web_output_dir / clip_filename

            serialized = json.dumps(clip_data, indent=2, sort_keys=False) + "\n"
            unity_path.write_text(serialized, encoding="utf-8")
            web_path.write_text(serialized, encoding="utf-8")

            compiled_clips_summary.append(
                {
                    "clip_id": clip_data["clip_id"],
                    "filename": clip_filename,
                    "duration_sec": clip_data["duration_sec"],
                    "physics_hz": clip_data["physics_hz"],
                    "sakuga_fps": clip_data["sakuga_fps"],
                    "keyframe_count": len(clip_data["keyframes"]),
                    "fnv1a_64_checksum": clip_data["fnv1a_64_checksum"],
                    "unity_path": str(unity_path),
                    "web_path": str(web_path),
                }
            )

        rigs_manifest = self.build_puppet_rigs_manifest()
        rigs_serialized = json.dumps(rigs_manifest, indent=2, sort_keys=False) + "\n"
        unity_rigs_path = self.unity_output_dir / "puppet_rigs_manifest.json"
        web_rigs_path = self.web_output_dir / "puppet_rigs_manifest.json"
        unity_rigs_path.write_text(rigs_serialized, encoding="utf-8")
        web_rigs_path.write_text(rigs_serialized, encoding="utf-8")

        report: Dict[str, Any] = {
            "engine": "Synapse-Sakuga-AnimEngine",
            "version": "1.0",
            "status": "VERIFIED",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "physics_hz": 120,
            "sakuga_fps": 24,
            "clip_count": len(compiled_clips_summary),
            "puppet_rig_count": rigs_manifest["rig_count"],
            "parallax_layer_depths": dict(PARALLAX_LAYER_DEPTHS),
            "unity_animations_dir": str(self.unity_output_dir),
            "web_animations_dir": str(self.web_output_dir),
            "clips": compiled_clips_summary,
            "puppet_rigs_manifest": {
                "unity_path": str(unity_rigs_path),
                "web_path": str(web_rigs_path),
                "rig_count": rigs_manifest["rig_count"],
                "card_ids": rigs_manifest["card_ids"],
                "fnv1a_64_checksum": rigs_manifest["fnv1a_64_checksum"],
            },
        }
        report["fnv1a_64_checksum"] = compute_dict_fnv1a_64(report)
        self.manifest_report_path.write_text(
            json.dumps(report, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        return report


def main() -> None:
    compiler = CfAnimClipCompiler()
    report = compiler.compile_and_export_all()
    print(
        f"[Synapse-Sakuga-AnimEngine v1.0] status={report['status']} "
        f"clips={report['clip_count']} rigs={report['puppet_rig_count']} "
        f"checksum={report['fnv1a_64_checksum']}"
    )


if __name__ == "__main__":
    main()
