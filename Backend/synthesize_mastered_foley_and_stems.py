#!/usr/bin/env python3
"""
Synthesize and master 5 warm, physical tabletop foley & chamber-RPG BGM WAV audio files
(44100 Hz, 16-bit PCM, Stereo) for CARDFRONT 3D: Cradle of Echoes, distribute them across
WebPlayable and Unity Resources directories, and emit a deterministic audio manifest JSON.
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
CHANNELS = 2  # Stereo for warm acoustic staging & concert hall spatial width


def one_pole_lowpass(signal: np.ndarray, cutoff_hz: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Apply a smooth 1-pole low-pass filter to a 1D numpy signal."""
    rc = 1.0 / (2.0 * math.pi * max(cutoff_hz, 1.0))
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    out = np.zeros_like(signal, dtype=np.float64)
    prev = 0.0
    for i in range(len(signal)):
        prev = prev + alpha * (float(signal[i]) - prev)
        out[i] = prev
    return out


def two_pole_lowpass(signal: np.ndarray, cutoff_hz: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Apply a 12 dB/oct 2-pole low-pass filter for warm acoustic roll-off."""
    return one_pole_lowpass(one_pole_lowpass(signal, cutoff_hz, sr), cutoff_hz, sr)


def one_pole_highpass(signal: np.ndarray, cutoff_hz: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Apply a 1-pole high-pass filter via subtraction."""
    return signal - one_pole_lowpass(signal, cutoff_hz, sr)


def bandpass_filter(
    signal: np.ndarray,
    low_hz: float,
    high_hz: float,
    sr: int = SAMPLE_RATE,
) -> np.ndarray:
    """Band-pass filter using cascaded high-pass and 2-pole low-pass."""
    return two_pole_lowpass(one_pole_highpass(signal, low_hz, sr), high_hz, sr)


def karplus_strong_pluck(
    freq_hz: float,
    duration_sec: float,
    damping: float = 0.994,
    brightness: float = 0.42,
    seed: int = 100,
    sr: int = SAMPLE_RATE,
) -> np.ndarray:
    """
    Physical Karplus-Strong plucked string model for warm nylon/gut concert harp & lute.
    Uses a low-pass filtered initial pluck excitation so there is zero metallic harshness.
    """
    n_samples = int(round(duration_sec * sr))
    period = max(2, int(round(sr / max(freq_hz, 20.0))))
    rng = np.random.default_rng(seed)

    # Warm initial pluck excitation: blend of smoothed noise + warm fundamental sine cycle
    phase = np.linspace(0.0, 2.0 * math.pi, period, endpoint=False)
    warm_cycle = 0.65 * np.sin(phase) + 0.25 * np.sin(2.0 * phase)
    noise_burst = one_pole_lowpass(rng.uniform(-1.0, 1.0, period), min(freq_hz * 3.5, 2200.0), sr)
    buf = ((1.0 - brightness) * warm_cycle + brightness * noise_burst).astype(np.float64)
    buf -= np.mean(buf)

    out = np.zeros(n_samples, dtype=np.float64)
    idx = 0
    prev_val = float(buf[-1])
    for i in range(n_samples):
        curr = float(buf[idx])
        out[i] = curr
        # Warm low-pass averaging filter inside the string feedback loop
        filtered = 0.54 * curr + 0.46 * prev_val
        buf[idx] = damping * filtered
        prev_val = curr
        idx = (idx + 1) % period

    # Soft 2.5ms attack envelope to mimic finger-pad release on harp string
    attack_len = min(n_samples, int(0.0025 * sr))
    if attack_len > 1:
        out[:attack_len] *= np.linspace(0.0, 1.0, attack_len)
    return out


def apply_stereo_hall_reverb(
    left: np.ndarray,
    right: np.ndarray,
    wet: float = 0.26,
    sr: int = SAMPLE_RATE,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Warm stereo multi-tap concert hall reverb with prime delays (37ms, 61ms, 97ms, 149ms)
    and warm low-pass damping at 1800 Hz.
    """
    n = len(left)
    rev_l = np.zeros(n, dtype=np.float64)
    rev_r = np.zeros(n, dtype=np.float64)

    taps = [
        (37.0, 0.42, 0.30),
        (61.0, 0.28, 0.38),
        (97.0, 0.22, 0.19),
        (149.0, 0.14, 0.16),
        (211.0, 0.09, 0.10),
    ]
    for idx, (delay_ms, gain_l, gain_r) in enumerate(taps):
        d = int(round(delay_ms * 0.001 * sr))
        if d < n:
            if idx % 2 == 0:
                rev_l[d:] += gain_l * left[:-d]
                rev_r[d:] += gain_r * right[:-d]
            else:
                # Cross-feed stereo reflections for spacious hall width
                rev_l[d:] += gain_l * right[:-d]
                rev_r[d:] += gain_r * left[:-d]

    rev_l = one_pole_lowpass(rev_l, 1800.0, sr)
    rev_r = one_pole_lowpass(rev_r, 1800.0, sr)
    return left + wet * rev_l, right + wet * rev_r


def soft_knee_limit_stereo(
    left: np.ndarray,
    right: np.ndarray,
    target_peak: float = 0.89,
    drive: float = 1.20,
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply gentle soft-knee saturation and normalize peak amplitude <= target_peak (<= 0.92)."""
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
    1. card_slam_stone.wav (~0.35s):
       Warm physical luxury card snapping onto a velvet-covered mahogany/slate tabletop:
       - Warm 90Hz -> 36Hz wooden table resonance
       - Band-passed velvet/cardstock air-snap (400Hz - 2200Hz filtered noise transient over 18ms)
       - Warm low-mid mahogany body (180Hz)
       - ZERO high-pitched sine-wave rings.
    """
    duration = 0.35
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(1041)

    # Layer 1: Warm 90Hz -> 36Hz mahogany tabletop resonance
    inst_freq = 36.0 + (90.0 - 36.0) * np.exp(-t / 0.050)
    phase = 2.0 * math.pi * np.cumsum(inst_freq) / SAMPLE_RATE
    table_sub = 0.82 * np.sin(phase) * np.exp(-t / 0.095) * (1.0 - np.exp(-t / 0.002))

    # Layer 2: Warm low-mid wooden cavity body at 180Hz & 250Hz
    wood_body = (
        0.48 * np.sin(2.0 * math.pi * 180.0 * t) * np.exp(-t / 0.038)
        + 0.24 * np.sin(2.0 * math.pi * 250.0 * t) * np.exp(-t / 0.024)
    ) * (1.0 - np.exp(-t / 0.0015))

    # Layer 3: Band-passed velvet/cardstock air-snap (400Hz - 2200Hz over 18ms)
    snap_onset = np.maximum(t - 0.002, 0.0)
    snap_env = np.exp(-snap_onset / 0.018) * (t >= 0.002)
    cardstock_noise_l = bandpass_filter(rng.standard_normal(n), 400.0, 2200.0) * snap_env * 0.95
    cardstock_noise_r = bandpass_filter(rng.standard_normal(n), 400.0, 2200.0) * snap_env * 0.92

    # Layer 4: Soft velvet cushion air puff (120Hz - 650Hz)
    velvet_puff = bandpass_filter(rng.standard_normal(n), 120.0, 650.0) * np.exp(-t / 0.042) * 0.65

    fade_samples = int(0.030 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    left = two_pole_lowpass((table_sub + wood_body + velvet_puff + cardstock_noise_l) * tail_window, 2200.0)
    right = two_pole_lowpass((table_sub + wood_body + velvet_puff * 0.97 + cardstock_noise_r) * tail_window, 2200.0)
    left, right = soft_knee_limit_stereo(left, right, target_peak=0.89, drive=1.20)

    meta = {
        "description": "Warm physical luxury card snapping onto a velvet-covered mahogany tabletop (90Hz->36Hz wooden table resonance + 400Hz-2200Hz cardstock air-snap + 180Hz low-mid body)",
        "layers": [
            "90Hz->36Hz wooden table resonance",
            "400Hz-2200Hz band-passed velvet/cardstock air-snap (18ms)",
            "180Hz warm low-mid mahogany body",
        ],
    }
    return left, right, meta


def synth_dice_tumble_brass() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    2. dice_tumble_brass.wav (~0.45s):
       Real physical polyhedral bone/acrylic dice rolling and clattering across a wooden dice tray:
       - 6 staggered micro-bounces (0ms, 65ms, 125ms, 180ms, 230ms, 275ms)
       - Short 4ms wooden/ivory click transients (350Hz - 1800Hz band-passed noise)
       - Rapidly decaying 240Hz, 380Hz, 520Hz warm wood-cavity resonators with 12ms decay
       - ZERO high-pitched bell sine waves.
    """
    duration = 0.45
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(2082)

    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    bounces = [
        (0.000, 1.00, -0.32, 1.00),
        (0.065, 0.82, +0.26, 1.04),
        (0.125, 0.68, -0.20, 0.96),
        (0.180, 0.54, +0.18, 1.06),
        (0.230, 0.42, -0.12, 0.98),
        (0.275, 0.31, +0.10, 1.03),
    ]
    cavity_freqs = [240.0, 380.0, 520.0]
    cavity_amps = [0.52, 0.38, 0.24]

    for onset_sec, gain, pan, pitch_shift in bounces:
        mask = t >= onset_sec
        tau = np.maximum(t - onset_sec, 0.0)
        bounce_sig = np.zeros(n, dtype=np.float64)

        # Warm wood-cavity resonators (240Hz, 380Hz, 520Hz) with rapid 12ms decay
        res_env = np.exp(-tau / 0.012) * (1.0 - np.exp(-tau / 0.0006)) * mask
        for freq, amp in zip(cavity_freqs, cavity_amps):
            bounce_sig += amp * np.sin(2.0 * math.pi * (freq * pitch_shift) * tau) * res_env

        # Short 4ms wooden/ivory click transient (350Hz - 1800Hz band-passed noise)
        click_env = np.exp(-tau / 0.004) * mask
        click_noise = bandpass_filter(rng.standard_normal(n), 350.0, 1800.0)
        bounce_sig += 0.85 * click_noise * click_env

        l_b, r_b = pan_mono_to_stereo(bounce_sig * gain, pan)
        left += l_b
        right += r_b

    # Subtle wooden dice-tray rolling texture across 0ms -> 310ms (250Hz - 1100Hz)
    roll_env = np.exp(-t / 0.16) * (1.0 + 0.35 * np.sin(2.0 * math.pi * 16.0 * t))
    roll_noise = bandpass_filter(rng.standard_normal(n), 250.0, 1100.0) * roll_env * 0.18
    left += roll_noise
    right += roll_noise * 0.95

    fade_samples = int(0.030 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
    left = two_pole_lowpass(left * tail_window, 1850.0)
    right = two_pole_lowpass(right * tail_window, 1850.0)
    left, right = soft_knee_limit_stereo(left, right, target_peak=0.88, drive=1.18)

    meta = {
        "description": "Physical polyhedral bone/acrylic dice rolling across a wooden dice tray (6 staggered micro-bounces at 0ms, 65ms, 125ms, 180ms, 230ms, 275ms with 4ms ivory click transients and 240Hz/380Hz/520Hz wood-cavity resonators)",
        "impacts_ms": [0, 65, 125, 180, 230, 275],
        "wood_cavity_resonators_hz": [240, 380, 520],
    }
    return left, right, meta


def synth_crystal_capture_shatter() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    3. crystal_capture_shatter.wav (~0.55s):
       Warm, magical Final Fantasy / Shadowverse harp & celesta chord glissando
       (D5 587.3Hz, F5 698.5Hz, A5 880.0Hz, D6 1174.7Hz, A6 1760.0Hz staggered by 35ms each)
       synthesized using Karplus-Strong plucked string synthesis + warm stereo hall reverb tail.
    """
    duration = 0.55
    n = int(round(duration * SAMPLE_RATE))
    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    gliss_notes = [
        (587.33, 0.000, -0.35, 301),   # D5
        (698.46, 0.035, +0.25, 302),   # F5
        (880.00, 0.070, -0.18, 303),   # A5
        (1174.66, 0.105, +0.30, 304),  # D6
        (1760.00, 0.140, 0.00, 305),   # A6
    ]

    for freq, onset_sec, pan, seed in gliss_notes:
        start_idx = int(round(onset_sec * SAMPLE_RATE))
        rem = n - start_idx
        if rem <= 0:
            continue
        rem_sec = rem / float(SAMPLE_RATE)
        tau = np.arange(rem, dtype=np.float64) / SAMPLE_RATE

        # Karplus-Strong plucked concert harp string + warm fundamental celesta bell
        pluck = karplus_strong_pluck(freq, rem_sec, damping=0.994, brightness=0.36, seed=seed)
        celesta_env = (1.0 - np.exp(-tau / 0.004)) * np.exp(-tau / 0.18)
        celesta = 0.32 * np.sin(2.0 * math.pi * freq * tau) * celesta_env

        note_sig = (0.75 * pluck + celesta) * np.exp(-tau / 0.26)
        l_n, r_n = pan_mono_to_stereo(note_sig, pan)
        left[start_idx:] += l_n
        right[start_idx:] += r_n

    # Warm stereo hall reverb tail
    left, right = apply_stereo_hall_reverb(left, right, wet=0.34)

    fade_samples = int(0.045 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
    left, right = soft_knee_limit_stereo(left * tail_window, right * tail_window, target_peak=0.89, drive=1.15)

    meta = {
        "description": "Warm magical harp & celesta chord glissando (D5 587.3Hz, F5 698.5Hz, A5 880.0Hz, D6 1174.7Hz, A6 1760.0Hz staggered by 35ms) via Karplus-Strong plucked string synthesis + stereo hall reverb",
        "glissando_hz": [587.3, 698.5, 880.0, 1174.7, 1760.0],
    }
    return left, right, meta


def synth_sakuga_impact_subdrop() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    4. sakuga_impact_subdrop.wav (~0.65s):
       Deep anime cinema taiko drum hit (72Hz -> 32Hz warm sub punch + warm low brass
       D2 73.4Hz + A2 110Hz + D3 146.8Hz low-pass filtered chord swell).
    """
    duration = 0.65
    n = int(round(duration * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(4094)

    # Layer 1: Deep Taiko Drum 72Hz -> 32Hz warm sub punch + 2nd harmonic body
    inst_freq = 32.0 + (72.0 - 32.0) * np.exp(-t / 0.095)
    sub_phase = 2.0 * math.pi * np.cumsum(inst_freq) / SAMPLE_RATE
    taiko_env = (1.0 - np.exp(-t / 0.003)) * np.exp(-t / 0.28)
    taiko_sub = (0.88 * np.sin(sub_phase) + 0.26 * np.sin(2.0 * sub_phase)) * taiko_env

    # Layer 2: Taiko leather drumhead strike transient (110Hz - 460Hz warm wood/skin thud)
    skin_env = (1.0 - np.exp(-t / 0.0015)) * np.exp(-t / 0.038)
    skin_thud = bandpass_filter(rng.standard_normal(n), 110.0, 460.0) * skin_env * 0.70

    # Layer 3: Warm low brass chord swell (D2 73.42Hz + A2 110.00Hz + D3 146.83Hz) low-passed at 480Hz
    brass_freqs = [73.42, 110.00, 146.83]
    brass_l = np.zeros(n, dtype=np.float64)
    brass_r = np.zeros(n, dtype=np.float64)
    swell_env = (1.0 - np.exp(-t / 0.045)) * np.exp(-t / 0.34)

    for idx, bf in enumerate(brass_freqs):
        voice_l = np.zeros(n, dtype=np.float64)
        voice_r = np.zeros(n, dtype=np.float64)
        for h, h_amp in [(1, 0.65), (2, 0.28), (3, 0.12), (4, 0.05)]:
            voice_l += h_amp * np.sin(2.0 * math.pi * (bf * 0.9985 * h) * t + 0.1 * idx)
            voice_r += h_amp * np.sin(2.0 * math.pi * (bf * 1.0015 * h) * t + 0.3 * idx)
        brass_l += voice_l * 0.32
        brass_r += voice_r * 0.32

    brass_l = two_pole_lowpass(brass_l * swell_env, 480.0)
    brass_r = two_pole_lowpass(brass_r * swell_env, 480.0)

    left, right = apply_stereo_hall_reverb(taiko_sub + skin_thud + brass_l, taiko_sub + skin_thud * 0.96 + brass_r, wet=0.22)

    fade_samples = int(0.045 * SAMPLE_RATE)
    tail_window = np.ones(n, dtype=np.float64)
    tail_window[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
    left, right = soft_knee_limit_stereo(left * tail_window, right * tail_window, target_peak=0.90, drive=1.25)

    meta = {
        "description": "Deep anime cinema taiko drum hit (72Hz->32Hz warm sub punch + warm low brass D2 73.4Hz + A2 110Hz + D3 146.8Hz low-pass filtered chord swell)",
        "brass_chord_hz": [73.4, 110.0, 146.8],
    }
    return left, right, meta


def midi_to_hz(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def synth_bgm_citadel_tactical_loop() -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """
    5. bgm_citadel_tactical_loop.wav (12.0s seamless loop at 120 BPM, 6 bars of 4/4 in D Dorian / F Major):
       Warm, lush chamber-RPG instrumental loop:
       - Instrument 1 (Karplus-Strong Acoustic Concert Harp / Lute Arpeggios): eighth-note arpeggios
         across Dm9 -> Bbmaj7 -> Gm9 -> Fmaj7 -> Gm6 -> Asus4/A7
       - Instrument 2 (Warm Bowed Cello & Viola Pad): 0.25s slow attack/release fundamental + 2nd/3rd
         harmonic warm ensemble pad low-pass filtered at 520 Hz with 0.8 Hz stereo chorus LFO
       - Instrument 3 (Warm Wooden Flute / Celesta Melody): gentle expressive melody notes
         (A4, F4, G4, E4, D4, F4, A4, C5, Bb4, A4, G4, F4, E4) with warm stereo multi-tap hall reverb.
    """
    bpm = 120.0
    beats = 24  # 6 bars of 4/4 at 120 BPM = 12.0000s
    beat_sec = 60.0 / bpm  # 0.50s per quarter-note beat
    eighth_sec = beat_sec / 2.0  # 0.25s per eighth note (48 eighth notes across 6 bars)
    duration = beats * beat_sec  # 12.0000s (529,200 samples)
    n = int(round(duration * SAMPLE_RATE))

    # Render 1.5s overhang at the end and wrap-add into the start for a 100% seamless loop
    overhang_sec = 1.50
    n_ext = n + int(round(overhang_sec * SAMPLE_RATE))
    left_ext = np.zeros(n_ext, dtype=np.float64)
    right_ext = np.zeros(n_ext, dtype=np.float64)

    # -------------------------------------------------------------------------
    # Instrument 1: Karplus-Strong Acoustic Concert Harp / Lute Eighth-Note Arpeggios
    # 6 bars x 8 eighth notes = 48 plucks across Dm9 -> Bbmaj7 -> Gm9 -> Fmaj7 -> Gm6 -> Asus4/A7
    # -------------------------------------------------------------------------
    harp_bars_midi = [
        # Bar 1: Dm9 (D3, A3, C4, E4, F4, E4, C4, A3)
        [50, 57, 60, 64, 65, 64, 60, 57],
        # Bar 2: Bbmaj7 (Bb2, F3, A3, C4, D4, C4, A3, F3)
        [46, 53, 57, 60, 62, 60, 57, 53],
        # Bar 3: Gm9 (G2, D3, F3, A3, Bb3, A3, F3, D3)
        [43, 50, 53, 57, 58, 57, 53, 50],
        # Bar 4: Fmaj7 (F2, C3, E3, G3, A3, G3, E3, C3)
        [41, 48, 52, 55, 57, 55, 52, 48],
        # Bar 5: Gm6 / Em7b5 (G2, D3, E3, G3, Bb3, G3, E3, D3)
        [43, 50, 52, 55, 58, 55, 52, 50],
        # Bar 6: Asus4 -> A7 turnaround (A2, E3, G3, D4, C#4, A3, G3, E3)
        [45, 52, 55, 62, 61, 57, 55, 52],
    ]

    for bar_idx, bar_notes in enumerate(harp_bars_midi):
        for step_idx, midi_note in enumerate(bar_notes):
            global_step = bar_idx * 8 + step_idx
            onset_sec = global_step * eighth_sec
            start_idx = int(round(onset_sec * SAMPLE_RATE))
            pluck_dur = 1.25  # Warm natural string ring-out across the bar
            end_idx = min(start_idx + int(round(pluck_dur * SAMPLE_RATE)), n_ext)
            actual_dur = (end_idx - start_idx) / float(SAMPLE_RATE)
            if actual_dur <= 0.01:
                continue

            freq = midi_to_hz(midi_note)
            pluck_sig = karplus_strong_pluck(
                freq,
                actual_dur,
                damping=0.995,
                brightness=0.35,
                seed=5000 + global_step,
            )
            accent = 0.28 if (step_idx == 0) else (0.23 if (step_idx == 4) else 0.19)
            pan = -0.30 + 0.085 * (step_idx % 8)
            l_p, r_p = pan_mono_to_stereo(pluck_sig * accent, pan)
            left_ext[start_idx:end_idx] += l_p
            right_ext[start_idx:end_idx] += r_p

    # -------------------------------------------------------------------------
    # Instrument 2: Warm Bowed Cello & Viola Ensemble Pad (520 Hz LPF + 0.8 Hz Chorus)
    # -------------------------------------------------------------------------
    # Each bar is 2.0s (4 beats); add 0.45s release overlap into next bar
    pad_bars = [
        # (bar_idx, [cello_root_midi, viola_fifth_midi, viola_tenth_midi])
        (0, [38, 45, 53]),  # Dm: D2, A2, F3
        (1, [34, 41, 50]),  # Bbmaj7: Bb1, F2, D3
        (2, [31, 38, 46]),  # Gm: G1, D2, Bb2
        (3, [29, 36, 45]),  # Fmaj7: F1, C2, A2
        (4, [31, 38, 46]),  # Gm6: G1, D2, Bb2
        (5, [33, 40, 49]),  # A7: A1, E2, C#3
    ]
    pad_l_raw = np.zeros(n_ext, dtype=np.float64)
    pad_r_raw = np.zeros(n_ext, dtype=np.float64)

    for bar_idx, chord_midis in pad_bars:
        onset_sec = bar_idx * 4.0 * beat_sec
        pad_dur = 4.0 * beat_sec + 0.45
        start_idx = int(round(onset_sec * SAMPLE_RATE))
        end_idx = min(start_idx + int(round(pad_dur * SAMPLE_RATE)), n_ext)
        tau = np.arange(end_idx - start_idx, dtype=np.float64) / SAMPLE_RATE

        # Smooth 0.25s bow attack & gentle release
        attack_env = 1.0 - np.exp(-tau / 0.25)
        release_start = 4.0 * beat_sec - 0.15
        release_env = np.exp(-np.maximum(tau - release_start, 0.0) / 0.25)
        env = attack_env * release_env

        # 0.8 Hz stereo chorus LFO
        chorus_l = 1.0 + 0.0022 * np.sin(2.0 * math.pi * 0.8 * tau)
        chorus_r = 1.0 - 0.0022 * np.sin(2.0 * math.pi * 0.8 * tau + 0.9)

        for v_idx, m_note in enumerate(chord_midis):
            f0 = midi_to_hz(m_note)
            phase_l = 2.0 * math.pi * f0 * np.cumsum(chorus_l) / SAMPLE_RATE
            phase_r = 2.0 * math.pi * f0 * np.cumsum(chorus_r) / SAMPLE_RATE
            v_gain = 0.26 if v_idx == 0 else 0.16
            # Fundamental + 2nd & 3rd warm bowed harmonics
            sig_l = (
                0.65 * np.sin(phase_l)
                + 0.24 * np.sin(2.0 * phase_l + 0.3)
                + 0.11 * np.sin(3.0 * phase_l + 0.7)
            ) * env * v_gain
            sig_r = (
                0.65 * np.sin(phase_r + 0.2)
                + 0.24 * np.sin(2.0 * phase_r + 0.8)
                + 0.11 * np.sin(3.0 * phase_r + 1.2)
            ) * env * v_gain
            pad_l_raw[start_idx:end_idx] += sig_l
            pad_r_raw[start_idx:end_idx] += sig_r

    # Low-pass filter the bowed cello & viola ensemble pad at 520 Hz
    left_ext += two_pole_lowpass(pad_l_raw, 520.0)
    right_ext += two_pole_lowpass(pad_r_raw, 520.0)

    # -------------------------------------------------------------------------
    # Instrument 3: Warm Wooden Flute / Celesta Expressive Melody
    # Notes: A4, F4, G4, E4, D4, F4, A4, C5, Bb4, A4, G4, F4, E4
    # -------------------------------------------------------------------------
    melody_events = [
        # (start_beat, duration_beats, midi_note, pan)
        (0.0, 2.0, 69, +0.15),   # A4 (Bar 1)
        (2.0, 2.0, 65, +0.10),   # F4
        (4.0, 2.5, 67, -0.12),   # G4 (Bar 2)
        (6.5, 1.5, 64, -0.08),   # E4
        (8.0, 2.0, 62, +0.14),   # D4 (Bar 3)
        (10.0, 1.0, 65, +0.18),  # F4
        (11.0, 1.0, 69, +0.20),  # A4
        (12.0, 2.5, 72, -0.15),  # C5 (Bar 4)
        (14.5, 1.5, 70, -0.10),  # Bb4
        (16.0, 1.5, 69, +0.12),  # A4 (Bar 5)
        (17.5, 1.5, 67, +0.06),  # G4
        (19.0, 1.0, 65, -0.06),  # F4
        (20.0, 4.0, 64, 0.00),   # E4 (Bar 6 sustained resolution into Dm)
    ]

    flute_l = np.zeros(n_ext, dtype=np.float64)
    flute_r = np.zeros(n_ext, dtype=np.float64)

    for start_beat, dur_beats, m_note, pan in melody_events:
        onset_sec = start_beat * beat_sec
        note_dur = dur_beats * beat_sec + 0.18
        start_idx = int(round(onset_sec * SAMPLE_RATE))
        end_idx = min(start_idx + int(round(note_dur * SAMPLE_RATE)), n_ext)
        tau = np.arange(end_idx - start_idx, dtype=np.float64) / SAMPLE_RATE

        freq = midi_to_hz(m_note)
        # Soft breath envelope + gentle delayed vibrato
        attack = 1.0 - np.exp(-tau / 0.065)
        release = np.exp(-np.maximum(tau - (dur_beats * beat_sec * 0.78), 0.0) / 0.18)
        env = attack * release

        vib_depth = 0.0028 * (1.0 - np.exp(-tau / 0.25))
        inst_f = freq * (1.0 + vib_depth * np.sin(2.0 * math.pi * 4.8 * tau))
        phase = 2.0 * math.pi * np.cumsum(inst_f) / SAMPLE_RATE

        # Warm wooden concert flute (fundamental + soft 2nd harmonic) + gentle celesta pluck onset
        flute_tone = (0.78 * np.sin(phase) + 0.16 * np.sin(2.0 * phase)) * env
        celesta_bell = 0.18 * np.sin(2.0 * math.pi * freq * tau) * np.exp(-tau / 0.22) * (1.0 - np.exp(-tau / 0.003))
        melody_sig = (flute_tone + celesta_bell) * 0.24

        l_m, r_m = pan_mono_to_stereo(melody_sig, pan)
        flute_l[start_idx:end_idx] += l_m
        flute_r[start_idx:end_idx] += r_r if (r_r := r_m) is not None else r_m

    left_ext += two_pole_lowpass(flute_l, 1900.0)
    right_ext += two_pole_lowpass(flute_r, 1900.0)

    # Apply warm stereo multi-tap hall reverb (37ms, 61ms, 97ms, 149ms)
    left_ext, right_ext = apply_stereo_hall_reverb(left_ext, right_ext, wet=0.30)

    # Wrap overhang tail into the start of the 12.0s loop so boundaries are phase-continuous
    overhang_samples = n_ext - n
    left = left_ext[:n].copy()
    right = right_ext[:n].copy()
    left[:overhang_samples] += left_ext[n:n_ext]
    right[:overhang_samples] += right_ext[n:n_ext]

    # Smooth 512-sample (~11.6ms) circular crossfade at loop boundary for zero click
    xfade = 512
    w = np.linspace(0.0, 1.0, xfade)
    left[-xfade:] = left[-xfade:] * (1.0 - w) + left[:xfade] * w
    right[-xfade:] = right[-xfade:] * (1.0 - w) + right[:xfade] * w

    left, right = soft_knee_limit_stereo(left, right, target_peak=0.88, drive=1.15)

    meta = {
        "description": "Warm chamber-RPG instrumental loop in D Dorian / F Major (Karplus-Strong acoustic concert harp arpeggios across Dm9->Bbmaj7->Gm9->Asus4->A7, 520Hz low-passed bowed cello/viola pad with 0.8Hz chorus, and wooden flute/celesta melody with multi-tap hall reverb)",
        "bpm": 120,
        "bars": 6,
        "beats": 24,
        "mode": "D Dorian / F Major",
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

    l_clamped = np.clip(left, -0.9999, 0.9999)
    r_clamped = np.clip(right, -0.9999, 0.9999)

    interleaved = np.empty(len(l_clamped) * 2, dtype=np.int16)
    interleaved[0::2] = np.round(l_clamped * 32767.0).astype(np.int16)
    interleaved[1::2] = np.round(r_clamped * 32767.0).astype(np.int16)

    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(interleaved.tobytes())

    raw_bytes = filepath.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    file_size_bytes = len(raw_bytes)

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
