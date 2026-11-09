#!/usr/bin/env python3
"""
Synthesize and master 5 multi-layered WAV audio files (44100 Hz, 16-bit PCM, Stereo)
for CARDFRONT 3D: Cradle of Echoes, distribute them across WebPlayable and Unity
Resources directories, and emit a deterministic audio manifest JSON.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import sys
import wave
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import numpy as np
except ModuleNotFoundError:
    mlx_py = Path.home() / ".local" / "share" / "mlx-env" / "bin" / "python3"
    if mlx_py.exists() and Path(sys.executable).resolve() != mlx_py.resolve():
        os.execv(str(mlx_py), [str(mlx_py), *sys.argv])
    raise

SAMPLE_RATE = 44100
CHANNELS = 2  # Stereo for rich spatial width & Ivalice orchestral staging


def one_pole_lowpass(signal: np.ndarray, cutoff_hz: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Apply a fast 1-pole low-pass filter to a 1D numpy signal."""
    rc = 1.0 / (2.0 * math.pi * max(cutoff_hz, 1.0))
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    out = np.zeros_like(signal, dtype=np.float64)
    prev = 0.0
    for i in range(len(signal)):
        prev = prev + alpha * (float(signal[i]) - prev)
        out[i] = prev
    return out


def one_pole_highpass(signal: np.ndarray, cutoff_hz: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Apply a fast 1-pole high-pass filter via subtraction."""
    return signal - one_pole_lowpass(signal, cutoff_hz, sr)


def soft_knee_limit_stereo(
    left: np.ndarray,
    right: np.ndarray,
    target_peak: float = 0.90,
    drive: float = 1.35,
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply soft-knee saturation and normalize peak amplitude <= target_peak (<= 0.92)."""
    l_sat = np.tanh(left * drive) / math.tanh(drive)
    r_sat = np.tanh(right * drive) / math.tanh(drive)
    current_peak = max(float(np.max(np.abs(l_sat))), float(np.max(np.abs(r_sat))), 1e-8)
    scale = target_peak / current_peak
    return l_sat * scale, r_sat * scale


def pan_mono_to_stereo(mono: np.ndarray, pan: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    """Constant-power stereo panner (-1.0 = full left, 0.0 = center, +1.0 = full right)."""
    angle = (pan + 1.0) * (math.pi / 4.0)
    return mono * math.cos(angle), mono * math.sin(angle)


def synth_card_slam_stone() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    1. card_slam_stone.wav (~0.38s):
       Heavy lithic stone slab thud (low-passed noise burst + 65Hz->28Hz pitch-drop
       body resonance + crisp parchment snap transient + metallic filigree ring).
    """
    duration = 0.38
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(1041)

    # Layer 1: 65Hz -> 28Hz pitch-drop body resonance + 2nd harmonic punch
    inst_freq = 28.0 + (65.0 - 28.0) * np.exp(-t / 0.065)
    phase = 2.0 * math.pi * np.cumsum(inst_freq) / SAMPLE_RATE
    sub_body = (0.85 * np.sin(phase) + 0.30 * np.sin(2.0 * phase)) * np.exp(-t / 0.125)

    # Layer 2: Low-passed lithic stone slab thud noise burst
    raw_noise = rng.standard_normal(n)
    stone_thud = one_pole_lowpass(raw_noise, 240.0) * np.exp(-t / 0.055) * 1.4

    # Layer 3: Crisp parchment snap transient (band-limited 1.2kHz - 4.5kHz burst at 4ms)
    snap_env = np.exp(-np.maximum(t - 0.003, 0.0) / 0.012) * (t >= 0.003)
    parchment_snap = one_pole_highpass(one_pole_lowpass(rng.standard_normal(n), 4600.0), 1200.0)
    parchment_snap = parchment_snap * snap_env * 0.75

    # Layer 4: Metallic filigree ring (Ivalice bronze/gold border resonance)
    ring_env = np.exp(-t / 0.14) * (1.0 - np.exp(-t / 0.002))
    filigree_l = (
        0.16 * np.sin(2.0 * math.pi * 1480.0 * t)
        + 0.11 * np.sin(2.0 * math.pi * 2210.0 * t + 0.4)
        + 0.07 * np.sin(2.0 * math.pi * 3190.0 * t + 1.1)
    ) * ring_env
    filigree_r = (
        0.16 * np.sin(2.0 * math.pi * 1486.0 * t + 0.2)
        + 0.11 * np.sin(2.0 * math.pi * 2218.0 * t + 0.9)
        + 0.07 * np.sin(2.0 * math.pi * 3182.0 * t + 0.3)
    ) * ring_env

    # Tail fade-out to zero at end of clip
    tail_window = np.ones(n, dtype=np.float64)
    fade_samples = int(0.025 * SAMPLE_RATE)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    left = (sub_body + stone_thud + parchment_snap * 1.05 + filigree_l) * tail_window
    right = (sub_body + stone_thud * 0.96 + parchment_snap * 0.95 + filigree_r) * tail_window
    left, right = soft_knee_limit_stereo(left, right, target_peak=0.90, drive=1.45)

    meta = {
        "description": "Heavy lithic stone slab thud (low-passed noise burst + 65Hz->28Hz pitch-drop body resonance + crisp parchment snap transient + metallic filigree ring)",
        "layers": ["65Hz->28Hz pitch-drop sub body", "low-passed lithic noise burst", "parchment snap transient", "metallic filigree ring"],
    }
    return left, right, meta


def synth_dice_tumble_brass() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    2. dice_tumble_brass.wav (~0.45s):
       Multi-bounce brass & obsidian polyhedral dice clatter (4 staggered micro-impacts
       at 0ms, 85ms, 165ms, 230ms with inharmonic bell partials 880Hz, 1340Hz, 2120Hz
       + stone table scrape).
    """
    duration = 0.45
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(2082)

    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    impacts = [
        (0.000, 1.00, -0.35, 1.00),
        (0.085, 0.78, +0.25, 1.04),
        (0.165, 0.58, -0.15, 0.97),
        (0.230, 0.42, +0.18, 1.08),
    ]
    partials = [880.0, 1340.0, 2120.0, 3410.0]
    partial_amps = [0.48, 0.36, 0.24, 0.14]
    partial_decays = [0.055, 0.045, 0.036, 0.025]

    for onset_sec, gain, pan, pitch_detune in impacts:
        mask = t >= onset_sec
        tau = np.maximum(t - onset_sec, 0.0)
        impact_sig = np.zeros(n, dtype=np.float64)

        # Inharmonic brass & obsidian bell partials
        for freq, amp, decay in zip(partials, partial_amps, partial_decays):
            f_actual = freq * pitch_detune
            env = np.exp(-tau / decay) * (1.0 - np.exp(-tau / 0.0008)) * mask
            impact_sig += amp * np.sin(2.0 * math.pi * f_actual * tau) * env

        # Obsidian vertex click transient
        click_env = np.exp(-tau / 0.0045) * mask
        click_noise = one_pole_highpass(one_pole_lowpass(rng.standard_normal(n), 6200.0), 900.0)
        impact_sig += 0.55 * click_noise * click_env

        # Low table knock resonance (~185 Hz)
        knock_env = np.exp(-tau / 0.022) * mask
        impact_sig += 0.35 * np.sin(2.0 * math.pi * (185.0 * pitch_detune) * tau) * knock_env

        l_imp, r_imp = pan_mono_to_stereo(impact_sig * gain, pan)
        left += l_imp
        right += r_imp

    # Continuous subtle stone table scrape across the roll (0ms -> 290ms)
    scrape_env = np.exp(-t / 0.18) * (1.0 + 0.45 * np.sin(2.0 * math.pi * 14.0 * t))
    scrape_noise = one_pole_highpass(one_pole_lowpass(rng.standard_normal(n), 2800.0), 450.0)
    scrape = 0.22 * scrape_noise * scrape_env
    left += scrape * 0.95
    right += scrape * 1.05

    fade_samples = int(0.03 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
    left, right = soft_knee_limit_stereo(left * tail_window, right * tail_window, target_peak=0.89, drive=1.3)

    meta = {
        "description": "Multi-bounce brass & obsidian polyhedral dice clatter (4 staggered micro-impacts at 0ms, 85ms, 165ms, 230ms with inharmonic bell partials 880Hz, 1340Hz, 2120Hz + stone table scrape)",
        "impacts_ms": [0, 85, 165, 230],
        "partials_hz": [880, 1340, 2120],
    }
    return left, right, meta


def synth_crystal_capture_shatter() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    3. crystal_capture_shatter.wav (~0.52s):
       Crystalline aether shatter + upward Sakimoto D-Dorian chord arpeggio
       (D5-F5-A5-B5-D6 shimmer + high-frequency glass transient burst).
    """
    duration = 0.52
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(3093)

    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    # Upward Sakimoto D-Dorian chord arpeggio: D5, F5, A5, B5, D6
    arp_notes = [
        (587.33, 0.000, -0.40),  # D5
        (698.46, 0.042, +0.30),  # F5
        (880.00, 0.084, -0.20),  # A5
        (987.77, 0.126, +0.35),  # B5 (characteristic Dorian natural 6th)
        (1174.66, 0.168, 0.00),  # D6
    ]

    for freq, onset, pan in arp_notes:
        mask = t >= onset
        tau = np.maximum(t - onset, 0.0)
        env = (1.0 - np.exp(-tau / 0.003)) * np.exp(-tau / 0.19) * mask
        # FM crystalline bell + octave shimmer
        mod = 1.6 * np.sin(2.0 * math.pi * (freq * 2.0) * tau) * np.exp(-tau / 0.07)
        tone = (
            0.55 * np.sin(2.0 * math.pi * freq * tau + mod)
            + 0.28 * np.sin(2.0 * math.pi * (freq * 2.002) * tau)
            + 0.14 * np.sin(2.0 * math.pi * (freq * 3.0) * tau)
        ) * env
        l_ch, r_ch = pan_mono_to_stereo(tone, pan)
        left += l_ch
        right += r_ch

    # High-frequency glass transient burst + micro-shard sparkles
    shatter_env = np.exp(-t / 0.032)
    glass_burst = one_pole_highpass(rng.standard_normal(n), 3200.0) * shatter_env * 0.65
    left += glass_burst
    right += np.roll(glass_burst, 19) * 0.95

    shard_times = [0.012, 0.029, 0.051, 0.078, 0.110, 0.148]
    shard_freqs = [3520.0, 4186.0, 4698.6, 5274.0, 3951.1, 4978.0]
    for st, sf in zip(shard_times, shard_freqs):
        mask = t >= st
        tau = np.maximum(t - st, 0.0)
        s_env = np.exp(-tau / 0.028) * mask
        shard = 0.18 * np.sin(2.0 * math.pi * sf * tau) * s_env
        left += shard
        right += shard * 0.9

    fade_samples = int(0.035 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
    left, right = soft_knee_limit_stereo(left * tail_window, right * tail_window, target_peak=0.90, drive=1.25)

    meta = {
        "description": "Crystalline aether shatter + upward Sakimoto D-Dorian chord arpeggio (D5-F5-A5-B5-D6 shimmer + high-frequency glass transient burst)",
        "arpeggio_notes": ["D5", "F5", "A5", "B5", "D6"],
    }
    return left, right, meta


def synth_sakuga_impact_subdrop() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    4. sakuga_impact_subdrop.wav (~0.75s):
       Anime Sakuga hit-stop impact stinger (110Hz->32Hz sub-bass drop + distorted
       sawtooth brass power fifth D3+A3+D4 + white-noise katana slash sweep).
    """
    duration = 0.75
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(4094)

    # Layer 1: 110Hz -> 32Hz anime Sakuga sub-bass drop with brief 18ms hit-stop compression
    inst_freq = 32.0 + (110.0 - 32.0) * np.exp(-t / 0.14)
    sub_phase = 2.0 * math.pi * np.cumsum(inst_freq) / SAMPLE_RATE
    sub_env = (1.0 - np.exp(-t / 0.002)) * np.exp(-t / 0.42)
    sub_drop = np.tanh(1.6 * np.sin(sub_phase)) * sub_env * 0.95

    # Layer 2: Distorted sawtooth brass power fifth (D3=146.83Hz, A3=220.00Hz, D4=293.66Hz)
    power_freqs = [146.83, 220.00, 293.66]
    brass_l = np.zeros(n, dtype=np.float64)
    brass_r = np.zeros(n, dtype=np.float64)
    brass_env = (1.0 - np.exp(-t / 0.006)) * np.exp(-t / 0.36)

    for idx, bf in enumerate(power_freqs):
        # Band-limited sawtooth via first 8 harmonics with slight stereo detune
        saw_l = np.zeros(n, dtype=np.float64)
        saw_r = np.zeros(n, dtype=np.float64)
        for h in range(1, 9):
            saw_l += ((-1.0) ** (h + 1)) * (1.0 / h) * np.sin(2.0 * math.pi * (bf * 0.998 * h) * t)
            saw_r += ((-1.0) ** (h + 1)) * (1.0 / h) * np.sin(2.0 * math.pi * (bf * 1.002 * h) * t + 0.15 * idx)
        brass_l += saw_l * (0.32 if idx < 2 else 0.24)
        brass_r += saw_r * (0.32 if idx < 2 else 0.24)

    brass_l = one_pole_lowpass(np.tanh(brass_l * 2.2), 2400.0) * brass_env
    brass_r = one_pole_lowpass(np.tanh(brass_r * 2.2), 2400.0) * brass_env

    # Layer 3: White-noise katana slash sweep (fast downward resonant swoosh + metallic edge)
    slash_env = (1.0 - np.exp(-t / 0.0015)) * np.exp(-t / 0.095)
    raw_slash = rng.standard_normal(n)
    slash_hi = one_pole_highpass(one_pole_lowpass(raw_slash, 5800.0), 950.0) * slash_env * 0.72
    katana_ring = (
        0.22 * np.sin(2.0 * math.pi * 2640.0 * t)
        + 0.15 * np.sin(2.0 * math.pi * 3960.0 * t)
    ) * np.exp(-t / 0.11)

    fade_samples = int(0.045 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    left = (sub_drop + brass_l + slash_hi * 1.08 + katana_ring) * tail_window
    right = (sub_drop + brass_r + slash_hi * 0.92 + katana_ring * 0.95) * tail_window
    left, right = soft_knee_limit_stereo(left, right, target_peak=0.91, drive=1.50)

    meta = {
        "description": "Anime Sakuga hit-stop impact stinger (110Hz->32Hz sub-bass drop + distorted sawtooth brass power fifth D3+A3+D4 + white-noise katana slash sweep)",
        "power_chord": ["D3", "A3", "D4"],
    }
    return left, right, meta


def midi_to_hz(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def synth_bgm_citadel_tactical_loop() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    5. bgm_citadel_tactical_loop.wav (~7.50s seamless loop at 128 BPM, 16 beats):
       Sakimoto-Yamada style Ivalice tactical orchestral-synth ostinato in D Dorian
       (driving bassline, harp/marimba arpeggio, warm French horn fifths, and subtle
       martial snare/timpani pulse), normalized with soft-knee limiting (peak <= 0.92).
    """
    bpm = 128.0
    beats = 16
    beat_sec = 60.0 / bpm  # 0.46875s per beat
    step_sec = beat_sec / 4.0  # 0.1171875s per 16th note (64 steps total)
    duration = beats * beat_sec  # Exactly 7.500000s (330,750 samples)
    n = int(round(duration * SAMPLE_RATE))

    # Render an extra bar overhang at the end and wrap-add it to the beginning for a 100% seamless loop
    overhang_sec = 2.0 * beat_sec
    n_ext = n + int(round(overhang_sec * SAMPLE_RATE))
    left_ext = np.zeros(n_ext, dtype=np.float64)
    right_ext = np.zeros(n_ext, dtype=np.float64)
    rng = np.random.default_rng(5128)

    def add_note_ext(
        onset_sec: float,
        note_dur: float,
        freq: float,
        amp: float,
        pan: float,
        timbre: str,
    ) -> None:
        start_idx = int(round(onset_sec * SAMPLE_RATE))
        length = int(round(note_dur * SAMPLE_RATE))
        end_idx = min(start_idx + length, n_ext)
        if end_idx <= start_idx:
            return
        tau = np.arange(end_idx - start_idx, dtype=np.float64) / SAMPLE_RATE

        if timbre == "bass":
            env = (1.0 - np.exp(-tau / 0.004)) * np.exp(-tau / 0.18)
            sig = (
                0.65 * np.sin(2.0 * math.pi * freq * tau)
                + 0.35 * np.sin(2.0 * math.pi * (freq * 2.0) * tau)
                + 0.18 * np.sin(2.0 * math.pi * (freq * 3.0) * tau)
            ) * env
        elif timbre == "marimba_harp":
            env = (1.0 - np.exp(-tau / 0.002)) * np.exp(-tau / 0.15)
            # Marimba 1:4 harmonic + concert harp fundamental/octave
            sig = (
                0.68 * np.sin(2.0 * math.pi * freq * tau)
                + 0.22 * np.sin(2.0 * math.pi * (freq * 2.0) * tau)
                + 0.16 * np.sin(2.0 * math.pi * (freq * 4.0) * tau) * np.exp(-tau / 0.04)
            ) * env
        elif timbre == "horn":
            attack = 1.0 - np.exp(-tau / 0.045)
            release = np.exp(-np.maximum(tau - (note_dur * 0.72), 0.0) / 0.16)
            env = attack * release
            vib = 1.0 + 0.0025 * np.sin(2.0 * math.pi * 5.2 * tau)
            phase = 2.0 * math.pi * freq * np.cumsum(vib) / SAMPLE_RATE
            sig = (
                0.52 * np.sin(phase)
                + 0.34 * np.sin(2.0 * phase + 0.3)
                + 0.18 * np.sin(3.0 * phase + 0.7)
                + 0.09 * np.sin(4.0 * phase + 1.1)
            ) * env
        else:
            env = np.exp(-tau / 0.1)
            sig = np.sin(2.0 * math.pi * freq * tau) * env

        l_s, r_s = pan_mono_to_stereo(sig * amp, pan)
        left_ext[start_idx:end_idx] += l_s
        right_ext[start_idx:end_idx] += r_s

    # Harmonic progression across 4 bars (16 beats) in D Dorian (D - E - F - G - A - B - C):
    # Bar 1: Dm7 (D, F, A, C)
    # Bar 2: G/D (D, G, B, D) -> signature Sakimoto Dorian IV chord over tonic pedal
    # Bar 3: Bbmaj7/C -> C6 (C, E, G, A)
    # Bar 4: Asus4 -> A7(b9) turnaround leading seamlessly back to Dm
    arp_bars_midi = [
        # Bar 1 (Dm9 Dorian ostinato): 16 sixteenth steps
        [62, 65, 69, 72, 74, 72, 69, 65, 62, 65, 69, 74, 76, 74, 72, 69],
        # Bar 2 (G/D Dorian natural-6th B4=71 ostinato):
        [62, 67, 71, 74, 76, 74, 71, 67, 62, 67, 71, 74, 79, 76, 74, 71],
        # Bar 3 (Fmaj7 -> C6 tactical rise):
        [60, 64, 67, 69, 72, 69, 67, 64, 60, 64, 67, 72, 76, 74, 72, 69],
        # Bar 4 (Em7 -> A7sus4 -> A7 turnaround):
        [64, 67, 71, 74, 76, 74, 71, 67, 61, 64, 69, 73, 76, 74, 73, 69],
    ]

    bass_bars_midi = [
        # Bar 1 (D2/D3 driving 8th/16th ostinato)
        [38, 38, 50, 38, 38, 45, 50, 45, 38, 38, 50, 38, 41, 41, 45, 48],
        # Bar 2 (D2 pedal under G triad)
        [38, 38, 50, 38, 43, 43, 50, 47, 38, 38, 50, 38, 43, 45, 47, 50],
        # Bar 3 (C2/C3 stride)
        [36, 36, 48, 36, 36, 43, 48, 43, 36, 36, 48, 36, 40, 43, 45, 48],
        # Bar 4 (E2 -> A2 dominant cadence)
        [40, 40, 52, 40, 43, 43, 47, 50, 45, 45, 57, 45, 49, 45, 43, 40],
    ]

    # 1. Render Harp/Marimba 16th-note arpeggio & Driving Bassline (64 steps)
    for bar_idx in range(4):
        for step_in_bar in range(16):
            global_step = bar_idx * 16 + step_in_bar
            onset = global_step * step_sec
            accent = 1.15 if (step_in_bar % 4 == 0) else (0.95 if (step_in_bar % 2 == 0) else 0.82)

            arp_midi = arp_bars_midi[bar_idx][step_in_bar]
            pan_arp = -0.28 if (step_in_bar % 2 == 0) else +0.28
            add_note_ext(
                onset,
                step_sec * 2.4,
                midi_to_hz(arp_midi),
                0.24 * accent,
                pan_arp,
                "marimba_harp",
            )

            bass_midi = bass_bars_midi[bar_idx][step_in_bar]
            add_note_ext(
                onset,
                step_sec * 1.9,
                midi_to_hz(bass_midi),
                0.30 * accent,
                0.0,
                "bass",
            )

    # 2. Render Warm French Horn Fifths & Heroic Counter-Line
    horn_voicings = [
        # (start_beat, duration_beats, [midi_notes])
        (0.0, 3.5, [50, 57, 62]),      # Bar 1: D3 - A3 - D4 open fifth
        (3.5, 0.5, [53, 60, 65]),      # Pickup: F3 - C4 - F4
        (4.0, 4.0, [50, 59, 67]),      # Bar 2: D3 - B3 - G4 (Dorian warm 6th + 4th)
        (8.0, 3.5, [48, 55, 64]),      # Bar 3: C3 - G3 - E4
        (11.5, 0.5, [50, 57, 65]),     # Pickup: D3 - A3 - F4
        (12.0, 2.0, [52, 59, 67]),     # Bar 4a: E3 - B3 - G4
        (14.0, 2.0, [45, 55, 61]),     # Bar 4b: A2 - G3 - C#4 turnaround
    ]
    for start_beat, dur_beats, notes in horn_voicings:
        onset = start_beat * beat_sec
        dur = dur_beats * beat_sec + 0.12
        for idx, m_note in enumerate(notes):
            pan_h = (-0.22 + 0.22 * idx)
            add_note_ext(onset, dur, midi_to_hz(m_note), 0.19, pan_h, "horn")

    # 3. Render Martial Timpani & Crisp Military Snare Pulse
    for beat in range(16):
        beat_onset = beat * beat_sec
        start_idx = int(round(beat_onset * SAMPLE_RATE))

        # Timpani on downbeats and tactical syncopations (beats 0, 2, 3.5, 4, 6, 8, 10, 12, 14, 15)
        if beat in (0, 2, 4, 6, 8, 10, 12, 14, 15):
            timp_midi = 38 if beat not in (8, 10, 14, 15) else (36 if beat in (8, 10) else 45)
            timp_freq = midi_to_hz(timp_midi)
            t_len = int(0.32 * SAMPLE_RATE)
            end_idx = min(start_idx + t_len, n_ext)
            tau = np.arange(end_idx - start_idx, dtype=np.float64) / SAMPLE_RATE
            p_env = timp_freq * (1.0 + 0.22 * np.exp(-tau / 0.025))
            phase = 2.0 * math.pi * np.cumsum(p_env) / SAMPLE_RATE
            timp = 0.34 * np.sin(phase) * np.exp(-tau / 0.16)
            left_ext[start_idx:end_idx] += timp
            right_ext[start_idx:end_idx] += timp

        # Martial snare pattern: backbeats (1, 3, 5, 7...) + 16th military ruff on beat 3, 7, 11, 15
        snare_offsets = []
        if beat % 2 == 1:
            snare_offsets.append((0.0, 0.22))
        if beat in (3, 7, 11, 15):
            snare_offsets.append((2.0 * step_sec, 0.13))
            snare_offsets.append((3.0 * step_sec, 0.17))

        for offset_s, s_gain in snare_offsets:
            s_idx = int(round((beat_onset + offset_s) * SAMPLE_RATE))
            s_len = int(0.11 * SAMPLE_RATE)
            e_idx = min(s_idx + s_len, n_ext)
            tau = np.arange(e_idx - s_idx, dtype=np.float64) / SAMPLE_RATE
            noise = one_pole_highpass(one_pole_lowpass(rng.standard_normal(e_idx - s_idx), 5200.0), 600.0)
            body = np.sin(2.0 * math.pi * 210.0 * tau) * np.exp(-tau / 0.025)
            snare = s_gain * (0.75 * noise * np.exp(-tau / 0.042) + 0.35 * body)
            l_sn, r_sn = pan_mono_to_stereo(snare, +0.12)
            left_ext[s_idx:e_idx] += l_sn
            right_ext[s_idx:e_idx] += r_sn

    # Wrap overhang tail into the start of the loop so Sample[0] and Sample[N-1] are phase-continuous
    overhang_samples = n_ext - n
    left = left_ext[:n].copy()
    right = right_ext[:n].copy()
    left[:overhang_samples] += left_ext[n:n_ext]
    right[:overhang_samples] += right_ext[n:n_ext]

    # Tiny 64-sample circular crossfade at the boundary to guarantee zero click on repeat
    xfade = 64
    w = np.linspace(0.0, 1.0, xfade)
    left[-xfade:] = left[-xfade:] * (1.0 - w) + left[:xfade] * w
    right[-xfade:] = right[-xfade:] * (1.0 - w) + right[:xfade] * w

    # Soft-knee limiting with peak <= 0.92 (target 0.89)
    left, right = soft_knee_limit_stereo(left, right, target_peak=0.89, drive=1.25)

    meta = {
        "description": "Sakimoto-Yamada style Ivalice tactical orchestral-synth ostinato in D Dorian (driving bassline, harp/marimba arpeggio, warm French horn fifths, and subtle martial snare/timpani pulse)",
        "bpm": 128,
        "beats": 16,
        "mode": "D Dorian",
        "seamless_loop": True,
    }
    return left, right, meta


def write_stereo_wav_and_measure(
    filepath: Path,
    left: np.ndarray,
    right: np.ndarray,
    extra_meta: Dict[str, object],
) -> Dict[str, object]:
    """Write 16-bit PCM stereo WAV at 44100 Hz and compute exact acoustic & file metrics."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    assert len(left) == len(right), "Stereo channels must have identical sample count"

    # Clamp safely and quantize to 16-bit signed integer PCM
    l_clamped = np.clip(left, -0.9999, 0.9999)
    r_clamped = np.clip(right, -0.9999, 0.9999)

    interleaved = np.empty(len(l_clamped) * 2, dtype=np.int16)
    interleaved[0::2] = np.round(l_clamped * 32767.0).astype(np.int16)
    interleaved[1::2] = np.round(r_clamped * 32767.0).astype(np.int16)

    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit PCM = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(interleaved.tobytes())

    raw_bytes = filepath.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    file_size_bytes = len(raw_bytes)

    # Compute exact normalized float metrics from quantized PCM
    pcm_float = interleaved.astype(np.float64) / 32768.0
    peak_amplitude = float(np.max(np.abs(pcm_float)))
    rms_level = float(np.sqrt(np.mean(pcm_float ** 2)))
    peak_dbfs = round(20.0 * math.log10(max(peak_amplitude, 1e-9)), 3)
    rms_dbfs = round(20.0 * math.log10(max(rms_level, 1e-9)), 3)
    duration_seconds = round(len(l_clamped) / float(SAMPLE_RATE), 4)

    return {
        "filename": filepath.name,
        "sample_rate": SAMPLE_RATE,
        "bit_depth": 16,
        "channels": CHANNELS,
        "num_frames": int(len(l_clamped)),
        "duration_seconds": duration_seconds,
        "file_size_bytes": file_size_bytes,
        "peak_amplitude": round(peak_amplitude, 6),
        "peak_dbfs": peak_dbfs,
        "rms_level": round(rms_level, 6),
        "rms_dbfs": rms_dbfs,
        "sha256": sha256_hex,
        **extra_meta,
    }


def main() -> None:
    project_root = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
    web_audio_dir = project_root / "WebPlayable" / "Audio"
    unity_res_audio_dir = project_root / "Assets" / "Resources" / "Audio"
    unpacked_res_audio_dir = Path(
        "/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/Assets/TcgEngine/Resources/Audio"
    )
    manifest_path = project_root / "Datasets" / "mastered_audio_stems_manifest.json"

    for d in (web_audio_dir, unity_res_audio_dir, unpacked_res_audio_dir, manifest_path.parent):
        d.mkdir(parents=True, exist_ok=True)

    generators = [
        ("card_slam_stone.wav", synth_card_slam_stone),
        ("dice_tumble_brass.wav", synth_dice_tumble_brass),
        ("crystal_capture_shatter.wav", synth_crystal_capture_shatter),
        ("sakuga_impact_subdrop.wav", synth_sakuga_impact_subdrop),
        ("bgm_citadel_tactical_loop.wav", synth_bgm_citadel_tactical_loop),
    ]

    stems_manifest: List[Dict[str, object]] = []

    for filename, synth_fn in generators:
        left, right, extra_meta = synth_fn()
        primary_path = web_audio_dir / filename
        entry = write_stereo_wav_and_measure(primary_path, left, right, extra_meta)

        # Copy identical mastered WAV to both Unity Resources/Audio targets
        copy_targets = [
            unity_res_audio_dir / filename,
            unpacked_res_audio_dir / filename,
        ]
        for target in copy_targets:
            shutil.copy2(primary_path, target)

        entry["paths"] = [
            str(primary_path),
            str(unity_res_audio_dir / filename),
            str(unpacked_res_audio_dir / filename),
        ]
        stems_manifest.append(entry)
        print(
            f"[OK] {filename:30s} | dur={entry['duration_seconds']:.2f}s | "
            f"size={entry['file_size_bytes']:8d}B | peak={entry['peak_amplitude']:.4f} | "
            f"rms={entry['rms_level']:.4f} | sha256={entry['sha256'][:12]}..."
        )

    manifest_payload = {
        "project": "CARDFRONT 3D: Cradle of Echoes",
        "generator": "Backend/synthesize_mastered_foley_and_stems.py",
        "format": {
            "sample_rate": SAMPLE_RATE,
            "bit_depth": 16,
            "encoding": "PCM_S16LE",
            "channels": CHANNELS,
        },
        "total_stems": len(stems_manifest),
        "stems": {item["filename"]: item for item in stems_manifest},
        "stems_list": stems_manifest,
    }

    manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
    print(f"\n[MANIFEST] Wrote {manifest_path}")


if __name__ == "__main__":
    main()
