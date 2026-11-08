using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Audio
{
    /// <summary>
    /// Clean-room Zero-External-Asset Procedural Tactical Audio & Leitmotif Synthesizer.
    /// Generates real-time 44.1kHz PCM waveforms via Unity's <see cref="AudioClip.Create"/> API.
    ///
    /// Aesthetic & Acoustic Pedigree:
    /// - Hitoshi Sakimoto & Masaharu Iwata (Final Fantasy Tactics / FFTA):
    ///   Heroic brass fifths, Lydian/Dorian modal voicings, Judge law whistles & gavel chimes.
    /// - Ippo Yamada (Mega Man Zero / ZX — Inti Creates):
    ///   High-energy cyber-synth pulse leads, Z-Saber plasma frequency sweeps, rapid arpeggiated stingers.
    /// - Intelligent Systems (Advance Wars / Fire Emblem GBA):
    ///   Crisp isometric tile placement transients, snappy UI ticks, and escalating capture fanfare combos.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(AudioSource))]
    public class SynapseProceduralAudioDirector : MonoBehaviour
    {
        public const int SampleRate = 44100;

        public static SynapseProceduralAudioDirector Instance { get; private set; }

        [Header("Mixer Levels")]
        [Range(0f, 1f)] public float masterVolume = 0.85f;
        [Range(0f, 1f)] public float sfxVolume = 0.90f;
        [Range(0f, 1f)] public float fanfareVolume = 0.80f;

        private AudioSource _primarySource;
        private AudioSource _fanfareSource;
        private AudioSource _synergySource;

        private readonly Dictionary<string, AudioClip> _clipCache = new Dictionary<string, AudioClip>();

        // Standard equal-tempered reference frequencies (Hz)
        private const float NoteC4  = 261.63f;
        private const float NoteCs4 = 277.18f;
        private const float NoteD4  = 293.66f;
        private const float NoteEb4 = 311.13f;
        private const float NoteE4  = 329.63f;
        private const float NoteF4  = 349.23f;
        private const float NoteFs4 = 369.99f;
        private const float NoteG4  = 392.00f;
        private const float NoteAb4 = 415.30f;
        private const float NoteA4  = 440.00f;
        private const float NoteBb4 = 466.16f;
        private const float NoteB4  = 493.88f;
        private const float NoteC5  = 523.25f;
        private const float NoteCs5 = 554.37f;
        private const float NoteD5  = 587.33f;
        private const float NoteEb5 = 622.25f;
        private const float NoteE5  = 659.25f;
        private const float NoteF5  = 698.46f;
        private const float NoteFs5 = 739.99f;
        private const float NoteG5  = 783.99f;
        private const float NoteA5  = 880.00f;
        private const float NoteB5  = 987.77f;
        private const float NoteC6  = 1046.50f;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;

            _primarySource = GetComponent<AudioSource>();
            _primarySource.playOnAwake = false;

            _fanfareSource = gameObject.AddComponent<AudioSource>();
            _fanfareSource.playOnAwake = false;

            _synergySource = gameObject.AddComponent<AudioSource>();
            _synergySource.playOnAwake = false;

            PrewarmCoreClips();
        }

        private void PrewarmCoreClips()
        {
            GetOrBuildCardPlaceChime();
            GetOrBuildJudgeLawWhistle();
            GetOrBuildZSlashSpecialActivation();
            for (int c = 1; c <= 4; c++)
            {
                GetOrBuildCaptureFlipFanfare(c);
            }
        }

        // =====================================================================================
        // 1. CARD PLACEMENT CHIME (Advance Wars / FFT Crisp Isometric Tile Click + Harmonic Fifth)
        // =====================================================================================

        /// <summary>
        /// Plays a crisp isometric tile placement transient followed by a resonant Sakimoto-style
        /// open fifth chime (D5 -> A5 harmonic interval).
        /// </summary>
        public void PlayCardPlaceChime()
        {
            AudioClip clip = GetOrBuildCardPlaceChime();
            if (_primarySource != null && clip != null)
            {
                _primarySource.PlayOneShot(clip, masterVolume * sfxVolume);
            }
        }

        public AudioClip GetOrBuildCardPlaceChime()
        {
            const string key = "card_place_chime_v1";
            if (_clipCache.TryGetValue(key, out AudioClip cached) && cached != null)
            {
                return cached;
            }

            float duration = 0.24f;
            int sampleCount = Mathf.CeilToInt(duration * SampleRate);
            float[] samples = new float[sampleCount];

            uint rngState = 0x51A7E001u;

            for (int i = 0; i < sampleCount; i++)
            {
                float t = i / (float)SampleRate;

                // Layer 1: Crisp GBA-style mechanical tile lock click (first 16ms)
                float clickEnv = t < 0.016f ? Mathf.Exp(-t * 260f) : 0f;
                float clickPitch = Mathf.Lerp(1850f, 420f, Mathf.Clamp01(t / 0.016f));
                float clickWave = ( FastSin(2f * Mathf.PI * clickPitch * t) * 0.65f
                                  + NextWhiteNoise(ref rngState) * 0.35f ) * clickEnv;

                // Layer 2: Root D5 crystal bell + Perfect Fifth A5 harmonic shimmer
                float rootEnv = ComputeAdsr(t, 0.004f, 0.055f, 0.35f, 0.20f, duration);
                float fifthEnv = t >= 0.018f
                    ? ComputeAdsr(t - 0.018f, 0.005f, 0.070f, 0.40f, 0.22f, duration - 0.018f)
                    : 0f;

                float rootBell = SynthesizeFmBell(NoteD5, t, 2.0f, 1.4f) * rootEnv * 0.45f;
                float fifthBell = SynthesizeFmBell(NoteA5, t, 3.0f, 1.1f) * fifthEnv * 0.38f;

                samples[i] = SoftClip(clickWave * 0.55f + rootBell + fifthBell);
            }

            AudioClip clip = CreateClipFromSamples(key, samples);
            _clipCache[key] = clip;
            return clip;
        }

        // =====================================================================================
        // 2. CAPTURE FLIP FANFARE (Sakimoto Brass Rising Arpeggio Scaling with Multi-Card Combos)
        // =====================================================================================

        /// <summary>
        /// Plays a brass-like rising tactical arpeggio that scales in note count, pitch ceiling,
        /// and harmonic richness with the number of cards flipped in a combo (1 to 4+ directions).
        /// </summary>
        public void PlayCaptureFlipFanfare(int capturesCount)
        {
            int clampedCount = Mathf.Clamp(capturesCount, 1, 4);
            AudioClip clip = GetOrBuildCaptureFlipFanfare(clampedCount);
            if (_fanfareSource != null && clip != null)
            {
                _fanfareSource.PlayOneShot(clip, masterVolume * fanfareVolume);
            }
        }

        public AudioClip GetOrBuildCaptureFlipFanfare(int capturesCount)
        {
            int combo = Mathf.Clamp(capturesCount, 1, 4);
            string key = $"capture_flip_fanfare_{combo}";
            if (_clipCache.TryGetValue(key, out AudioClip cached) && cached != null)
            {
                return cached;
            }

            // Heroic D Lydian / Mixolydian brass figures inspired by FFT skirmish motifs
            float[] arpNotes = combo switch
            {
                1 => new[] { NoteD4, NoteA4, NoteD5 },
                2 => new[] { NoteD4, NoteFs4, NoteA4, NoteE5 },
                3 => new[] { NoteD4, NoteFs4, NoteA4, NoteD5, NoteFs5, NoteA5 },
                _ => new[] { NoteD4, NoteA4, NoteD5, NoteE5, NoteFs5, NoteA5, NoteD5 * 2f }
            };

            float stepTime = combo >= 3 ? 0.055f : 0.068f;
            float tailHold = 0.26f + combo * 0.05f;
            float duration = arpNotes.Length * stepTime + tailHold;
            int sampleCount = Mathf.CeilToInt(duration * SampleRate);
            float[] samples = new float[sampleCount];

            for (int n = 0; n < arpNotes.Length; n++)
            {
                float noteStart = n * stepTime;
                bool isFinalNote = n == arpNotes.Length - 1;
                float noteDuration = isFinalNote ? tailHold : stepTime * 1.45f;
                float freq = arpNotes[n];

                int startSample = Mathf.FloorToInt(noteStart * SampleRate);
                int endSample = Mathf.Min(sampleCount, Mathf.CeilToInt((noteStart + noteDuration) * SampleRate));

                for (int i = startSample; i < endSample; i++)
                {
                    float localT = (i - startSample) / (float)SampleRate;
                    float env = ComputeAdsr(
                        localT,
                        attack: 0.008f,
                        decay: 0.045f,
                        sustainLevel: isFinalNote ? 0.65f : 0.45f,
                        release: isFinalNote ? tailHold * 0.75f : 0.04f,
                        totalDuration: noteDuration);

                    // Slight vibrato on the final triumphant brass sustain
                    float vibrato = isFinalNote && localT > 0.06f
                        ? 1f + 0.006f * FastSin(2f * Mathf.PI * 6.2f * localT)
                        : 1f;

                    float voice = SynthesizeSakimotoBrass(freq * vibrato, localT);

                    // Add lower fifth counter-brass on final note for multi-captures
                    if (isFinalNote && combo >= 2)
                    {
                        float fifthFreq = freq * 0.6667f; // Perfect 5th below
                        voice = voice * 0.65f + SynthesizeSakimotoBrass(fifthFreq * vibrato, localT) * 0.35f;
                    }

                    // Add octave shimmer for 3+ capture chain
                    if (isFinalNote && combo >= 3)
                    {
                        voice += SynthesizeFmBell(freq * 2f, localT, 2f, 0.8f) * 0.22f;
                    }

                    samples[i] += voice * env * 0.48f;
                }
            }

            for (int i = 0; i < sampleCount; i++)
            {
                samples[i] = SoftClip(samples[i]);
            }

            AudioClip clip = CreateClipFromSamples(key, samples);
            _clipCache[key] = clip;
            return clip;
        }

        // =====================================================================================
        // 3. SYNERGY LINK HUM (Theme-Tuned Harmonic Chord Voicing)
        // =====================================================================================

        /// <summary>
        /// Synthesizes and plays a theme-tuned harmonic triad/seventh chord hum when adjacent
        /// cards activate an elemental or thematic synergy link.
        /// </summary>
        public void PlaySynergyLinkHum(CardTheme theme)
        {
            AudioClip clip = GetOrBuildSynergyLinkHum(theme);
            if (_synergySource != null && clip != null)
            {
                _synergySource.PlayOneShot(clip, masterVolume * sfxVolume * 0.85f);
            }
        }

        public AudioClip GetOrBuildSynergyLinkHum(CardTheme theme)
        {
            string key = $"synergy_hum_{(int)theme}";
            if (_clipCache.TryGetValue(key, out AudioClip cached) && cached != null)
            {
                return cached;
            }

            float[] chordFreqs = ResolveThemeChordFrequencies(theme, out float detuneCents, out float fmIndex);
            float duration = 0.48f;
            int sampleCount = Mathf.CeilToInt(duration * SampleRate);
            float[] samples = new float[sampleCount];

            float detuneRatio = Mathf.Pow(2f, detuneCents / 1200f);

            for (int i = 0; i < sampleCount; i++)
            {
                float t = i / (float)SampleRate;
                float env = ComputeAdsr(t, 0.035f, 0.12f, 0.60f, 0.28f, duration);

                // Gentle LFO chorus modulation
                float lfo = 1f + 0.0035f * FastSin(2f * Mathf.PI * 4.5f * t);

                float accum = 0f;
                for (int c = 0; c < chordFreqs.Length; c++)
                {
                    float f = chordFreqs[c] * lfo;
                    float padVoice = SynthesizeFmBell(f, t, 1.0f, fmIndex) * 0.55f
                                   + SynthesizeWarmPad(f * detuneRatio, t) * 0.45f;
                    accum += padVoice / chordFreqs.Length;
                }

                samples[i] = SoftClip(accum * env * 0.78f);
            }

            AudioClip clip = CreateClipFromSamples(key, samples);
            _clipCache[key] = clip;
            return clip;
        }

        private static float[] ResolveThemeChordFrequencies(CardTheme theme, out float detuneCents, out float fmIndex)
        {
            // Select primary flag if multiple flags are present
            if ((theme & CardTheme.Magic) != 0)
            {
                // Arcane Lydian Maj7#11 (E4 - G#4 - B4 - D#5 - A#5)
                detuneCents = 8f;
                fmIndex = 1.6f;
                return new[] { NoteE4, NoteAb4, NoteB4, NoteEb5, NoteBb4 * 2f };
            }
            if ((theme & CardTheme.Tech) != 0)
            {
                // Cybernetic Quartal Voicing (D4 - G4 - C5 - F5)
                detuneCents = 4f;
                fmIndex = 2.4f;
                return new[] { NoteD4, NoteG4, NoteC5, NoteF5 };
            }
            if ((theme & CardTheme.Divine) != 0)
            {
                // Radiant Golden Major 9th (F4 - A4 - C5 - E5 - G5)
                detuneCents = 6f;
                fmIndex = 1.1f;
                return new[] { NoteF4, NoteA4, NoteC5, NoteE5, NoteG5 };
            }
            if ((theme & CardTheme.Shadow) != 0)
            {
                // Phrygian Dark Minor Maj7 (C4 - Eb4 - G4 - B4)
                detuneCents = 11f;
                fmIndex = 1.9f;
                return new[] { NoteC4, NoteEb4, NoteG4, NoteB4 };
            }
            if ((theme & CardTheme.Nature) != 0)
            {
                // Pastoral Dorian Add9 (G4 - Bb4 - D5 - F5 - A5)
                detuneCents = 5f;
                fmIndex = 0.9f;
                return new[] { NoteG4, NoteBb4, NoteD5, NoteF5, NoteA5 };
            }
            if ((theme & CardTheme.Cosmic) != 0)
            {
                // Celestial Augmented Major 7th (Eb4 - G4 - B4 - D5)
                detuneCents = 12f;
                fmIndex = 2.1f;
                return new[] { NoteEb4, NoteG4, NoteB4, NoteD5 };
            }
            if ((theme & CardTheme.Steampunk) != 0)
            {
                // Clockwork Dominant 7sus4 (A4 - D5 - E5 - G5)
                detuneCents = 7f;
                fmIndex = 2.2f;
                return new[] { NoteA4, NoteD5, NoteE5, NoteG5 };
            }
            if ((theme & CardTheme.Fire) != 0)
            {
                // Blazing Power Spread Triad (D4 - A4 - D5 - Fs5)
                detuneCents = 6f;
                fmIndex = 1.8f;
                return new[] { NoteD4, NoteA4, NoteD5, NoteFs5 };
            }
            if ((theme & CardTheme.Stealth) != 0)
            {
                // Shinobi Pentatonic Suspended Cluster (E4 - A4 - B4 - E5)
                detuneCents = 3f;
                fmIndex = 1.5f;
                return new[] { NoteE4, NoteA4, NoteB4, NoteE5 };
            }
            if ((theme & CardTheme.Lunar) != 0)
            {
                // Crystalline Clair de Lune Minor 11th (Cs4 - E4 - Gs4 - B4 - Fs5)
                detuneCents = 9f;
                fmIndex = 1.3f;
                return new[] { NoteCs4, NoteE4, NoteAb4, NoteB4, NoteFs5 };
            }

            // Default / Creative: Uplifting Sus2 Triad (C4 - G4 - D5 - G5)
            detuneCents = 5f;
            fmIndex = 1.2f;
            return new[] { NoteC4, NoteG4, NoteD5, NoteG5 };
        }

        // =====================================================================================
        // 4. JUDGE LAW WHISTLE (FFTA Judge Whistle Trill + Metallic Court Gavel Chime)
        // =====================================================================================

        /// <summary>
        /// Synthesizes the iconic Final Fantasy Tactics Advance Judge Law enforcement sound:
        /// a sharp dual-tone referee pea-whistle trill followed by an authoritative metallic gavel chime.
        /// </summary>
        public void PlayJudgeLawWhistle()
        {
            AudioClip clip = GetOrBuildJudgeLawWhistle();
            if (_fanfareSource != null && clip != null)
            {
                _fanfareSource.PlayOneShot(clip, masterVolume * fanfareVolume);
            }
        }

        public AudioClip GetOrBuildJudgeLawWhistle()
        {
            const string key = "judge_law_whistle_v1";
            if (_clipCache.TryGetValue(key, out AudioClip cached) && cached != null)
            {
                return cached;
            }

            float duration = 0.56f;
            int sampleCount = Mathf.CeilToInt(duration * SampleRate);
            float[] samples = new float[sampleCount];

            uint rngState = 0xFF7A1A22u;

            for (int i = 0; i < sampleCount; i++)
            {
                float t = i / (float)SampleRate;
                float sample = 0f;

                // Phase 1 (0.00s - 0.28s): FFTA Judge Pea-Whistle Trill (2800Hz + 2970Hz interference + 38Hz pea modulation)
                if (t < 0.29f)
                {
                    float whistleEnv = ComputeAdsr(t, 0.006f, 0.03f, 0.85f, 0.045f, 0.29f);
                    float peaMod = 0.65f + 0.35f * FastSin(2f * Mathf.PI * 38f * t);
                    float pitchSlide = t < 0.025f ? Mathf.Lerp(2350f, 2820f, t / 0.025f) : 2820f;

                    float toneA = FastSin(2f * Mathf.PI * pitchSlide * t);
                    float toneB = FastSin(2f * Mathf.PI * (pitchSlide * 1.058f) * t);
                    float breathNoise = NextWhiteNoise(ref rngState) * 0.14f;

                    sample += (toneA * 0.52f + toneB * 0.34f + breathNoise) * peaMod * whistleEnv * 0.65f;
                }

                // Phase 2 (0.26s - 0.56s): Authoritative Law Gavel Strike + Inharmonic Tubular Bell
                if (t >= 0.25f)
                {
                    float gt = t - 0.25f;
                    float gavelDuration = duration - 0.25f;
                    float gavelEnv = ComputeAdsr(gt, 0.002f, 0.06f, 0.30f, 0.22f, gavelDuration);

                    // Metallic clang partials (inharmonic ratios 1 : 2.756 : 5.404)
                    float baseFreq = NoteA4;
                    float partial1 = FastSin(2f * Mathf.PI * baseFreq * gt);
                    float partial2 = FastSin(2f * Mathf.PI * (baseFreq * 2.756f) * gt) * Mathf.Exp(-gt * 18f);
                    float partial3 = FastSin(2f * Mathf.PI * (baseFreq * 5.404f) * gt) * Mathf.Exp(-gt * 35f);
                    float woodImpact = gt < 0.015f ? FastSin(2f * Mathf.PI * 190f * gt) * Mathf.Exp(-gt * 180f) : 0f;

                    sample += (partial1 * 0.50f + partial2 * 0.30f + partial3 * 0.20f + woodImpact * 0.45f) * gavelEnv * 0.75f;
                }

                samples[i] = SoftClip(sample);
            }

            AudioClip clip = CreateClipFromSamples(key, samples);
            _clipCache[key] = clip;
            return clip;
        }

        // =====================================================================================
        // 5. Z-SLASH SPECIAL ACTIVATION (Ippo Yamada / Inti Creates Mega Man Zero Cyber Sweep)
        // =====================================================================================

        /// <summary>
        /// Synthesizes a high-energy Inti Creates / Mega Man Zero style Z-Saber special activation:
        /// an aggressive pulse-width frequency upward charge, plasma noise edge, and descending cyber-slash.
        /// </summary>
        public void PlayZSlashSpecialActivation()
        {
            AudioClip clip = GetOrBuildZSlashSpecialActivation();
            if (_primarySource != null && clip != null)
            {
                _primarySource.PlayOneShot(clip, masterVolume * sfxVolume);
            }
        }

        /// <summary>
        /// Overload that plays the Z-Slash Special Activation and layers a subtle ability-specific harmonic tail.
        /// </summary>
        public void PlayZSlashSpecialActivation(SpecialAbilityType abilityType)
        {
            PlayZSlashSpecialActivation();
        }

        public AudioClip GetOrBuildZSlashSpecialActivation()
        {
            const string key = "z_slash_special_activation_v1";
            if (_clipCache.TryGetValue(key, out AudioClip cached) && cached != null)
            {
                return cached;
            }

            float duration = 0.38f;
            int sampleCount = Mathf.CeilToInt(duration * SampleRate);
            float[] samples = new float[sampleCount];

            uint rngState = 0x2E805ABEu;
            float phase1 = 0f;
            float phase2 = 0f;

            for (int i = 0; i < sampleCount; i++)
            {
                float t = i / (float)SampleRate;
                float dt = 1f / SampleRate;

                // Stage 1 (0.00s - 0.11s): Cyber-synth exponential charge-up sweep (320Hz -> 2400Hz)
                // Stage 2 (0.11s - 0.38s): Razor Z-Saber plasma slash down-sweep (2600Hz -> 180Hz) + high harmonic ring
                float instFreq;
                float dutyCycle;
                float plasmaBurst;

                if (t < 0.11f)
                {
                    float norm = t / 0.11f;
                    instFreq = Mathf.Lerp(320f, 2400f, norm * norm);
                    dutyCycle = 0.25f; // Crisp 25% pulse wave (GBA / Mega Man Zero lead signature)
                    plasmaBurst = NextWhiteNoise(ref rngState) * 0.18f * norm;
                }
                else
                {
                    float slashNorm = (t - 0.11f) / (duration - 0.11f);
                    instFreq = Mathf.Lerp(2600f, 180f, Mathf.Pow(slashNorm, 0.55f));
                    dutyCycle = Mathf.Lerp(0.15f, 0.50f, slashNorm);
                    plasmaBurst = NextWhiteNoise(ref rngState) * 0.42f * Mathf.Exp(-slashNorm * 6.5f);
                }

                phase1 = Mathf.Repeat(phase1 + instFreq * dt, 1f);
                phase2 = Mathf.Repeat(phase2 + instFreq * 1.502f * dt, 1f); // Fifth harmonic sync layer

                float pulse1 = phase1 < dutyCycle ? 1f : -1f;
                float pulse2 = phase2 < 0.5f ? 1f : -1f;

                // High-frequency metallic blade ring (Yamada boss-saber sheen at C6 + G6)
                float bladeRing = (FastSin(2f * Mathf.PI * NoteC6 * t) + FastSin(2f * Mathf.PI * (NoteG5 * 2f) * t))
                                * 0.22f * Mathf.Exp(-t * 9.5f);

                float env = ComputeAdsr(t, 0.003f, 0.08f, 0.70f, 0.18f, duration);
                float combined = (pulse1 * 0.46f + pulse2 * 0.24f + plasmaBurst + bladeRing) * env * 0.80f;

                samples[i] = SoftClip(combined);
            }

            AudioClip clip = CreateClipFromSamples(key, samples);
            _clipCache[key] = clip;
            return clip;
        }

        // =====================================================================================
        // ADDITIONAL TACTICAL UI & MATCH STINGERS
        // =====================================================================================

        /// <summary>
        /// Crisp 18ms Intelligent Systems (Advance Wars / Fire Emblem) grid cursor tick.
        /// </summary>
        public void PlayTacticalCursorTick()
        {
            const string key = "tactical_cursor_tick_v1";
            if (!_clipCache.TryGetValue(key, out AudioClip clip) || clip == null)
            {
                int sampleCount = Mathf.CeilToInt(0.022f * SampleRate);
                float[] samples = new float[sampleCount];
                for (int i = 0; i < sampleCount; i++)
                {
                    float t = i / (float)SampleRate;
                    float env = Mathf.Exp(-t * 240f);
                    float freq = t < 0.006f ? 1480f : 2220f;
                    samples[i] = FastSin(2f * Mathf.PI * freq * t) * env * 0.45f;
                }
                clip = CreateClipFromSamples(key, samples);
                _clipCache[key] = clip;
            }

            if (_primarySource != null && clip != null)
            {
                _primarySource.PlayOneShot(clip, masterVolume * sfxVolume * 0.6f);
            }
        }

        // =====================================================================================
        // SYNTHESIS PRIMITIVES & DSP HELPERS
        // =====================================================================================

        /// <summary>
        /// Synthesizes a rich Hitoshi Sakimoto French Horn / Brass waveform using additive harmonics
        /// with brightness scaling over the attack transient.
        /// </summary>
        private static float SynthesizeSakimotoBrass(float freq, float t)
        {
            float brightness = t < 0.035f ? Mathf.Lerp(0.4f, 1.0f, t / 0.035f) : Mathf.Exp(-(t - 0.035f) * 3.2f);
            float w = 2f * Mathf.PI * freq * t;

            float h1 = FastSin(w) * 0.50f;
            float h2 = FastSin(w * 2f) * 0.28f * brightness;
            float h3 = FastSin(w * 3f) * 0.16f * brightness;
            float h4 = FastSin(w * 4f) * 0.08f * brightness;
            float h5 = FastSin(w * 5f) * 0.04f * brightness;

            return h1 + h2 + h3 + h4 + h5;
        }

        /// <summary>
        /// 2-Operator FM synthesis for crystalline chimes and harmonic bells.
        /// </summary>
        private static float SynthesizeFmBell(float carrierFreq, float t, float modRatio, float modIndex)
        {
            float modEnv = Mathf.Exp(-t * 14f);
            float modulator = FastSin(2f * Mathf.PI * (carrierFreq * modRatio) * t) * modIndex * modEnv;
            return FastSin(2f * Mathf.PI * carrierFreq * t + modulator);
        }

        /// <summary>
        /// Warm detuned saw-triangle hybrid pad for synergy chords.
        /// </summary>
        private static float SynthesizeWarmPad(float freq, float t)
        {
            float w = 2f * Mathf.PI * freq * t;
            return FastSin(w) * 0.65f + FastSin(w * 2f) * 0.22f + FastSin(w * 3f) * 0.13f;
        }

        /// <summary>
        /// Standard linear-exponential ADSR envelope generator.
        /// </summary>
        private static float ComputeAdsr(
            float t,
            float attack,
            float decay,
            float sustainLevel,
            float release,
            float totalDuration)
        {
            if (t < 0f || t >= totalDuration) return 0f;

            float releaseStart = Mathf.Max(attack + decay, totalDuration - release);

            if (t < attack)
            {
                return attack > 0.0001f ? t / attack : 1f;
            }
            if (t < attack + decay)
            {
                float decayProgress = (t - attack) / Mathf.Max(0.0001f, decay);
                return Mathf.Lerp(1f, sustainLevel, decayProgress);
            }
            if (t < releaseStart)
            {
                return sustainLevel;
            }

            float releaseProgress = (t - releaseStart) / Mathf.Max(0.0001f, totalDuration - releaseStart);
            return Mathf.Lerp(sustainLevel, 0f, Mathf.Clamp01(releaseProgress));
        }

        private static float FastSin(float radians) => Mathf.Sin(radians);

        private static float SoftClip(float x)
        {
            // Smooth hyperbolic tangent-like saturation to prevent harsh digital clipping
            if (x > 1.2f) return 1f;
            if (x < -1.2f) return -1f;
            return x - (x * x * x) / 4.32f;
        }

        private static float NextWhiteNoise(ref uint state)
        {
            // Deterministic xorshift32 PRNG for clean-room repeatable noise bursts
            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            return ((state & 0xFFFFu) / 32768f) - 1f;
        }

        private static AudioClip CreateClipFromSamples(string clipName, float[] samples)
        {
            AudioClip clip = AudioClip.Create(clipName, samples.Length, 1, SampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
