#!/usr/bin/env python3
"""
Unit & Integration Test Suite for Synapse-Sakuga-AnimEngine v1.0
================================================================
Verifies:
  1. Critically-damped (zeta == 1.0) spring convergence at 120Hz
  2. Under-damped (zeta < 1.0) spring overshoot & convergence at 120Hz
  3. Over-damped (zeta > 1.0) spring regime & monotonic convergence at 120Hz
  4. Analytical vs. RK4 and Semi-Implicit Euler integration agreement at dt = 1/120s
  5. 24fps & 12fps Sakuga stepped quantization, -0.18 anticipation dip, and 2-frame snap-lunge
  6. Sakuga freeze-frame HitStop hold (3..5 frames) invariance
  7. 2D FABRIK bone IK solver target convergence (tolerance <= 1e-3, max_iters <= 12)
  8. 2D FABRIK bone segment distance preservation (reachable & unreachable targets)
  9. 4-layer 2.5D depth parallax projection bounds (-0.35, -0.12, 0.18, 0.45)
  10. All 8 canonical .cfanim files in Assets/Resources/Animations/ with valid FNV-1a 64 checksums
  11. All 8 canonical .cfanim files in WebPlayable/GeneratedArt/Animations/ synced & verified
  12. Checksum tamper resistance on .cfanim payloads
  13. puppet_rigs_manifest.json has all 16 Hero & Boss 2.5D skeletal rigs in both directories
  14. Deterministic timeline scrubbing (scrub_to(t) history independence)
  15. Build verification manifest in Logs/sakuga_animation_engine_manifest.json (status: VERIFIED)
"""

from __future__ import annotations

import copy
import json
import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
BACKEND_DIR = PROJECT_ROOT / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from synapse_sakuga_animation_engine import (  # noqa: E402
    CANONICAL_CLIP_IDS,
    HERO_AND_BOSS_CARD_IDS,
    MANIFEST_REPORT_PATH,
    PARALLAX_LAYER_DEPTHS,
    UNITY_ANIM_DIR,
    WEB_ANIM_DIR,
    CfAnimClipCompiler,
    SynapseFabrikBoneChain2D,
    SynapseSakugaSteppedCurve,
    SynapseSpringHarmonicSolver,
    verify_clip_checksum,
)


class TestSynapseSakugaAnimationEngineSuite(unittest.TestCase):
    """Comprehensive verification suite for Synapse-Sakuga-AnimEngine v1.0."""

    @classmethod
    def setUpClass(cls) -> None:
        # Ensure all artifacts are freshly compiled before running file checks
        cls.compiler = CfAnimClipCompiler()
        cls.compile_report = cls.compiler.compile_and_export_all()

    def test_01_critically_damped_spring_convergence_120hz(self) -> None:
        """Critically-damped spring (zeta == 1.0) converges smoothly at 120Hz without overshoot."""
        # k = 400, m = 1 => 2 * sqrt(k*m) = 40.0 => c = 40.0 gives zeta = 1.0
        solver = SynapseSpringHarmonicSolver(
            stiffness=400.0,
            damping=40.0,
            mass=1.0,
            initial_pos=0.0,
            target_pos=1.0,
            initial_vel=0.0,
        )
        self.assertAlmostEqual(solver.zeta, 1.0, places=6)
        self.assertEqual(solver.regime, "critically-damped")

        dt = 1.0 / 120.0
        positions = []
        for _ in range(180):  # 1.5 seconds at 120Hz
            pos, _ = solver.step(dt=dt, method="rk4")
            positions.append(pos)

        # Critically damped from v0=0 should never overshoot target_pos=1.0
        self.assertTrue(all(p <= 1.000001 for p in positions))
        self.assertTrue(solver.is_settled(pos_tol=1e-4, vel_tol=1e-4))
        self.assertAlmostEqual(solver.pos, 1.0, places=5)

    def test_02_under_damped_spring_overshoot_and_settle_120hz(self) -> None:
        """Under-damped spring (zeta < 1.0) exhibits Sakuga overshoot then settles at 120Hz."""
        solver = SynapseSpringHarmonicSolver(
            stiffness=360.0,
            damping=12.0,
            mass=1.0,
            initial_pos=0.0,
            target_pos=1.0,
            initial_vel=0.0,
        )
        self.assertLess(solver.zeta, 1.0)
        self.assertEqual(solver.regime, "under-damped")

        dt = 1.0 / 120.0
        max_pos = 0.0
        for _ in range(360):  # 3.0 seconds at 120Hz
            pos, _ = solver.step(dt=dt, method="rk4")
            if pos > max_pos:
                max_pos = pos

        self.assertGreater(max_pos, 1.05, "Under-damped spring must overshoot target 1.0")
        self.assertTrue(solver.is_settled(pos_tol=1e-3, vel_tol=1e-2))

    def test_03_over_damped_spring_regime_120hz(self) -> None:
        """Over-damped spring (zeta > 1.0) approaches target monotonically without oscillation."""
        solver = SynapseSpringHarmonicSolver(
            stiffness=100.0,
            damping=30.0,  # zeta = 30 / 20 = 1.5 > 1.0
            mass=1.0,
            initial_pos=0.0,
            target_pos=1.0,
            initial_vel=0.0,
        )
        self.assertAlmostEqual(solver.zeta, 1.5, places=6)
        self.assertEqual(solver.regime, "over-damped")

        traj = solver.sample_trajectory(duration_sec=2.5, hz=120, method="analytical")
        for i in range(1, len(traj)):
            self.assertGreaterEqual(traj[i]["pos"], traj[i - 1]["pos"] - 1e-9)
        self.assertLessEqual(traj[-1]["pos"], 1.0)
        self.assertGreater(traj[-1]["pos"], 0.99)

    def test_04_analytical_vs_rk4_and_euler_consistency(self) -> None:
        """RK4 at 120Hz closely matches closed-form analytical solution across all regimes."""
        solver_rk4 = SynapseSpringHarmonicSolver(stiffness=320.0, damping=24.0, mass=1.0)
        solver_euler = SynapseSpringHarmonicSolver(stiffness=320.0, damping=24.0, mass=1.0)

        dt = 1.0 / 120.0
        for step_idx in range(1, 61):
            t = step_idx * dt
            p_rk4, v_rk4 = solver_rk4.step(dt=dt, method="rk4")
            p_euler, _ = solver_euler.step(dt=dt, method="euler")
            p_exact, v_exact = solver_rk4.evaluate_analytical(t)

            self.assertAlmostEqual(p_rk4, p_exact, places=4)
            self.assertAlmostEqual(v_rk4, v_exact, places=3)
            self.assertAlmostEqual(p_euler, p_exact, places=1)

    def test_05_sakuga_stepped_quantization_and_anticipation_lunge(self) -> None:
        """24fps & 12fps Sakuga curve enforces -0.18 anticipation dip and 2-frame snap-lunge."""
        curve_24 = SynapseSakugaSteppedCurve(
            fps=24,
            step_hold=2,  # "on-twos"
            anticipation_frames=4,
            anticipation_dip=-0.18,
            lunge_frames=2,
            impact_peak=1.12,
            hitstop_frames=4,
        )
        # Frames 2 and 3 should quantize to frame 2 when step_hold=2 ("on-twos")
        t_frame_2 = 2.1 / 24.0
        t_frame_3 = 3.8 / 24.0
        self.assertEqual(curve_24.quantize_frame_index(t_frame_2), 2)
        self.assertEqual(curve_24.quantize_frame_index(t_frame_3), 2)
        self.assertAlmostEqual(curve_24.evaluate(t_frame_2), curve_24.evaluate(t_frame_3), places=6)

        # At exact end of anticipation (frame 4), value must equal -0.18
        ant_state = curve_24.evaluate_at_frame(4)
        self.assertEqual(ant_state["phase"], "anticipation")
        self.assertAlmostEqual(ant_state["value"], -0.18, places=6)

        # 2-frame snap-lunge (frames 5 and 6) reaches impact_peak=1.12 at frame 6
        lunge_mid = curve_24.evaluate_at_frame(5)
        lunge_end = curve_24.evaluate_at_frame(6)
        self.assertEqual(lunge_mid["phase"], "snap_lunge")
        self.assertEqual(lunge_end["phase"], "snap_lunge")
        self.assertAlmostEqual(lunge_end["value"], 1.12, places=6)

        # Also verify 12fps mode works cleanly
        curve_12 = SynapseSakugaSteppedCurve(fps=12, hitstop_frames=3)
        self.assertAlmostEqual(curve_12.frame_duration, 1.0 / 12.0, places=6)

    def test_06_sakuga_hitstop_freeze_frame_hold(self) -> None:
        """HitStop window (3..5 frames) holds the exact impact pose with zero motion."""
        for hs_frames in (3, 4, 5):
            curve = SynapseSakugaSteppedCurve(
                fps=24,
                anticipation_frames=3,
                anticipation_dip=-0.18,
                lunge_frames=2,
                impact_peak=1.15,
                hitstop_frames=hs_frames,
            )
            hitstop_start = 3 + 2 + 1  # frame 6 (after 3 ant frames + 2 lunge frames)
            held_values = []
            for f in range(hitstop_start, hitstop_start + hs_frames):
                st = curve.evaluate_at_frame(f)
                self.assertEqual(st["phase"], "hitstop")
                self.assertTrue(st["in_hitstop"])
                held_values.append(st["value"])

            self.assertEqual(len(held_values), hs_frames)
            for v in held_values:
                self.assertAlmostEqual(v, 1.15, places=6)

            # Frame immediately after HitStop transitions to "settle"
            post_hs = curve.evaluate_at_frame(hitstop_start + hs_frames)
            self.assertEqual(post_hs["phase"], "settle")
            self.assertFalse(post_hs["in_hitstop"])

    def test_07_fabrik_2d_ik_target_convergence(self) -> None:
        """2D FABRIK solver converges within tolerance <= 1e-3 in <= 12 iterations for reachable targets."""
        chain = SynapseFabrikBoneChain2D(
            joint_positions=[(0.0, 0.0), (20.0, 0.0), (35.0, 0.0), (45.0, 0.0)],
            chain_name="WeaponArm",
        )
        reachable_targets = [
            (25.0, 20.0),
            (10.0, 30.0),
            (-15.0, 22.0),
            (30.0, -18.0),
        ]
        for target in reachable_targets:
            res = chain.solve_ik(target)
            self.assertTrue(res["reachable"])
            self.assertTrue(res["converged"])
            self.assertLessEqual(res["iterations"], 12)
            self.assertLessEqual(res["end_effector_error"], 1e-3)

    def test_08_fabrik_2d_bone_length_and_root_preservation(self) -> None:
        """2D FABRIK strictly preserves individual bone segment lengths and root anchor."""
        bind_pts = [(5.0, 10.0), (25.0, 18.0), (42.0, 30.0), (55.0, 42.0)]
        chain = SynapseFabrikBoneChain2D(joint_positions=bind_pts, chain_name="Cape/Wing")
        expected_lengths = list(chain.bone_lengths)

        # Test both a reachable target and an unreachable far target
        for target in [(28.0, 35.0), (200.0, 200.0)]:
            res = chain.solve_ik(target)
            # Root joint must stay anchored at bind_pts[0]
            self.assertAlmostEqual(res["joints"][0][0], bind_pts[0][0], places=5)
            self.assertAlmostEqual(res["joints"][0][1], bind_pts[0][1], places=5)

            # Segment lengths must be preserved
            actual_lengths = chain.current_segment_lengths()
            self.assertEqual(len(actual_lengths), len(expected_lengths))
            for actual, expected in zip(actual_lengths, expected_lengths):
                self.assertAlmostEqual(actual, expected, places=4)

    def test_09_four_layer_25d_depth_parallax_bounds(self) -> None:
        """4-layer 2.5D depth parallax uses exact weights (-0.35, -0.12, 0.18, 0.45) and clamps tilt."""
        self.assertEqual(
            PARALLAX_LAYER_DEPTHS,
            {
                "bg_layer": -0.35,
                "mid_layer": -0.12,
                "actor_layer": 0.18,
                "vfx_frame_break_layer": 0.45,
            },
        )
        # Excessive tilt values (e.g. 5.0, -5.0) must clamp to (+1.0, -1.0)
        offsets = SynapseFabrikBoneChain2D.compute_parallax_offsets(
            tilt_x=5.0, tilt_y=-5.0, max_displacement_px=20.0
        )
        self.assertAlmostEqual(offsets["bg_layer"]["offset_x"], -7.0, places=5)
        self.assertAlmostEqual(offsets["bg_layer"]["offset_y"], 7.0, places=5)
        self.assertAlmostEqual(offsets["mid_layer"]["offset_x"], -2.4, places=5)
        self.assertAlmostEqual(offsets["actor_layer"]["offset_x"], 3.6, places=5)
        self.assertAlmostEqual(offsets["vfx_frame_break_layer"]["offset_x"], 9.0, places=5)
        self.assertAlmostEqual(offsets["vfx_frame_break_layer"]["offset_y"], -9.0, places=5)

    def test_10_all_8_cfanim_files_in_unity_resources(self) -> None:
        """All 8 canonical .cfanim files exist in Assets/Resources/Animations/ with valid schema & checksum."""
        required_events = {"onAnticipation", "onHitStop", "onCaptureFlip", "onHapticTrigger"}
        for clip_id in CANONICAL_CLIP_IDS:
            clip_path = UNITY_ANIM_DIR / f"{clip_id}.cfanim"
            self.assertTrue(clip_path.is_file(), f"Missing Unity .cfanim: {clip_path}")
            data = json.loads(clip_path.read_text(encoding="utf-8"))

            self.assertEqual(data["clip_id"], clip_id)
            self.assertEqual(data["version"], "1.0")
            self.assertGreater(data["duration_sec"], 0.0)
            self.assertEqual(data["physics_hz"], 120)
            self.assertEqual(data["sakuga_fps"], 24)
            self.assertIn("spring_params", data)
            self.assertIn("keyframes", data)
            self.assertGreater(len(data["keyframes"]), 5)
            self.assertTrue(required_events.issubset(set(data["events"].keys())))
            self.assertTrue(verify_clip_checksum(data), f"Checksum failed for {clip_id}")

    def test_11_all_8_cfanim_files_in_webplayable_synced(self) -> None:
        """All 8 canonical .cfanim files exist in WebPlayable/GeneratedArt/Animations/ and match Unity."""
        for clip_id in CANONICAL_CLIP_IDS:
            unity_path = UNITY_ANIM_DIR / f"{clip_id}.cfanim"
            web_path = WEB_ANIM_DIR / f"{clip_id}.cfanim"
            self.assertTrue(web_path.is_file(), f"Missing WebPlayable .cfanim: {web_path}")

            unity_text = unity_path.read_text(encoding="utf-8")
            web_text = web_path.read_text(encoding="utf-8")
            self.assertEqual(unity_text, web_text)

            web_data = json.loads(web_text)
            self.assertTrue(verify_clip_checksum(web_data))

    def test_12_cfanim_checksum_tamper_detection(self) -> None:
        """Mutating any keyframe or parameter in a .cfanim payload invalidates its FNV-1a 64 checksum."""
        sample_path = UNITY_ANIM_DIR / "directional_clash_lunge.cfanim"
        data = json.loads(sample_path.read_text(encoding="utf-8"))
        self.assertTrue(verify_clip_checksum(data))

        tampered = copy.deepcopy(data)
        tampered["duration_sec"] = 9.99
        self.assertFalse(verify_clip_checksum(tampered))

    def test_13_puppet_rigs_manifest_all_16_heroes_and_bosses(self) -> None:
        """puppet_rigs_manifest.json exists in both directories with all 16 Hero & Boss 2.5D rigs."""
        for anim_dir in (UNITY_ANIM_DIR, WEB_ANIM_DIR):
            manifest_path = anim_dir / "puppet_rigs_manifest.json"
            self.assertTrue(manifest_path.is_file(), f"Missing {manifest_path}")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(manifest["rig_count"], 16)
            self.assertEqual(tuple(manifest["card_ids"]), HERO_AND_BOSS_CARD_IDS)
            self.assertTrue(verify_clip_checksum(manifest))

            rigs = manifest["rigs"]
            for card_id in HERO_AND_BOSS_CARD_IDS:
                self.assertIn(card_id, rigs)
                rig = rigs[card_id]
                self.assertEqual(rig["portrait_resolution"], [600, 800])
                for chain_name in ("Head", "Torso", "WeaponArm", "Cape/Wing"):
                    self.assertIn(chain_name, rig["bone_chains"])
                    self.assertGreaterEqual(len(rig["bone_chains"][chain_name]["bind_joints"]), 3)
                self.assertEqual(
                    rig["parallax_layers"]["depths"],
                    PARALLAX_LAYER_DEPTHS,
                )

    def test_14_deterministic_timeline_scrubbing_history_independence(self) -> None:
        """scrub_to(t) produces identical state regardless of step history on Spring and Sakuga evaluators."""
        spring_a = SynapseSpringHarmonicSolver(stiffness=350.0, damping=25.0, mass=1.0)
        spring_b = SynapseSpringHarmonicSolver(stiffness=350.0, damping=25.0, mass=1.0)

        # Mutate spring_a with arbitrary steps and scrubs before scrubbing to t = 0.375
        for _ in range(40):
            spring_a.step(dt=1.0 / 120.0, method="euler")
        spring_a.scrub_to(1.25)
        spring_a.step(dt=1.0 / 120.0, method="rk4")

        state_a = spring_a.scrub_to(0.375)
        state_b = spring_b.scrub_to(0.375)
        self.assertEqual(state_a, state_b)
        self.assertAlmostEqual(spring_a.pos, spring_b.pos, places=9)
        self.assertAlmostEqual(spring_a.vel, spring_b.vel, places=9)

        # Same check for SynapseSakugaSteppedCurve
        sakuga_a = SynapseSakugaSteppedCurve(fps=24, hitstop_frames=4)
        sakuga_b = SynapseSakugaSteppedCurve(fps=24, hitstop_frames=4)
        sakuga_a.scrub_to(0.95)
        sakuga_a.scrub_to(0.05)
        self.assertEqual(sakuga_a.scrub_to(0.28), sakuga_b.scrub_to(0.28))

    def test_15_build_verification_manifest_log(self) -> None:
        """Logs/sakuga_animation_engine_manifest.json exists with status == 'VERIFIED' and valid checksum."""
        self.assertTrue(MANIFEST_REPORT_PATH.is_file())
        report = json.loads(MANIFEST_REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(report["clip_count"], 8)
        self.assertEqual(report["puppet_rig_count"], 16)
        self.assertTrue(verify_clip_checksum(report))


if __name__ == "__main__":
    unittest.main(verbosity=2)
