using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.FX
{
    // =================================================================================================
    // 1. DICEVADERS × SHIFTING PIECES × CARDFRONT ENUMS & STATE MODELS
    // =================================================================================================

    public enum LunaTarotGenesisArchetype
    {
        None = 0,
        SwordAggression = 1, // +2 Attack on North/East edges, +1 starting Budge, Crimson Slash VFX
        ShieldDefense = 2,   // +2 Defense on South/West edges, Prevent Flip shield, Emerald Aegis VFX
        StaffControl = 3     // +2 starting Chrono Rerolls, +1 Budge, Neon Cyan/Violet Glyph VFX
    }

    public enum DicevadersResonanceTier
    {
        Single = 0,            // 1.00x
        Pair = 1,              // 1.50x
        TwoPair = 2,           // 1.85x
        Triple = 3,            // 2.25x
        StraightOverdrive = 4, // 2.75x
        Quadruple = 5          // 3.50x (4 or 5 matching pips)
    }

    /// <summary>
    /// Second-order underdamped harmonic spring solver:
    ///   x'' + 2 * zeta * omega_n * x' + omega_n^2 * (x - target) = 0
    /// Default parameters tuned to Dicevaders (Steam AppID 3917700) tactile pop spec:
    ///   zeta = 0.42 (damping ratio), omega_n = 30.0 rad/s (natural frequency).
    /// </summary>
    [Serializable]
    public struct DampedSpringState
    {
        public float Value;
        public float Velocity;
        public float Target;
        public float Zeta;
        public float OmegaN;

        public DampedSpringState(float initialValue, float zeta = 0.42f, float omegaN = 30.0f)
        {
            Value = initialValue;
            Velocity = 0f;
            Target = initialValue;
            Zeta = zeta;
            OmegaN = omegaN;
        }

        public void Impulse(float deltaVelocity)
        {
            Velocity += deltaVelocity;
        }

        public float Step(float dt)
        {
            dt = Mathf.Clamp(dt, 0.0001f, 0.033f);
            float accel = -2.0f * Zeta * OmegaN * Velocity - (OmegaN * OmegaN) * (Value - Target);
            Velocity += accel * dt;
            Value += Velocity * dt;
            return Value;
        }
    }

    [Serializable]
    public class TacticalActivationDie
    {
        public int SlotIndex;
        public int PipValue; // 1..6
        public bool IsLocked;
        public int MappedColumn => (PipValue <= 2) ? 0 : (PipValue <= 4 ? 1 : 2);
        public DampedSpringState ScaleSpring = new DampedSpringState(1.0f, 0.42f, 30.0f);
        public DampedSpringState TiltSpring = new DampedSpringState(0.0f, 0.42f, 30.0f);
    }

    [Serializable]
    public class ResonanceEvaluationResult
    {
        public DicevadersResonanceTier Tier;
        public string Label;
        public float Multiplier;
        public int BonusEdgeSurge;
        public bool[] ActivatedColumns = new bool[3];
    }

    // =================================================================================================
    // 2. SYNAPSE DICEVADERS JUICE, PARTICLE, SHADER & PROCEDURAL AUDIO CONTROLLER (SUBSYSTEM 4 -> 10/10)
    // =================================================================================================

    /// <summary>
    /// Complete Unity Particle, Shader, Damped-Spring, Hit-Stop, Screen-Shake, and Procedural 44.1kHz
    /// Harmonic Audio Controller for SYNAPSE / Project CF × Dicevaders × Shifting Pieces: Cradle of Echoes.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(AudioSource))]
    public class SynapseDicevadersJuiceAndAudioController : MonoBehaviour
    {
        public const int SampleRate = 44100;
        public const float DefaultSpringZeta = 0.42f;
        public const float DefaultSpringOmegaN = 30.0f;
        public const float CascadeTileStaggerSeconds = 0.055f; // 55ms sequential tile pop stagger
        public const float HitStopFreezeSeconds = 0.048f;      // 48ms (3-frame @ 60fps) hit-stop freeze
        public const float SemitonePitchStepPerCascade = 1.5f; // +1.5 semitones per cascade step
        public const float ChromaticAberrationPulsePx = 1.8f;  // 1.8px radial chromatic micro-pulse

        public static SynapseDicevadersJuiceAndAudioController Instance { get; private set; }

        [Header("LUNA Station of Awakening Tarot Genesis")]
        public LunaTarotGenesisArchetype ActiveTarotGenesis = LunaTarotGenesisArchetype.None;

        [Header("5-Die Dicevaders Activation Row & Tokens")]
        public List<TacticalActivationDie> ActivationRow = new List<TacticalActivationDie>(5);
        public int BudgeTokens = 3;
        public int MaxBudgeTokens = 5;
        public int ChronoRerollTokens = 2;
        public int MaxChronoTokens = 5;
        public ResonanceEvaluationResult CurrentResonance = new ResonanceEvaluationResult();

        [Header("Damped-Spring Physics & Camera Trauma")]
        public Transform CameraRigTransform;
        public Material PostProcessChromaticMaterial;
        private DampedSpringState _boardScaleSpring = new DampedSpringState(1.0f, DefaultSpringZeta, DefaultSpringOmegaN);
        private DampedSpringState[,] _tileSprings = new DampedSpringState[3, 3];
        private float _screenShakeTrauma;
        private float _chromaticPulseIntensity;
        private bool _isHitStopped;
        private Vector3 _cameraBaseLocalPos;

        [Header("Procedural 44.1kHz Harmonic Audio")]
        [Range(0f, 1f)] public float MasterVolume = 0.88f;
        private AudioSource _sfxSource;
        private AudioSource _harmonicSource;

        // Shader Property IDs (Palette A #D12D3A Red Scarf, Palette B #2EE6D3 Cyan, Palette C #FFB648 Fox)
        private static readonly int PropChromaticOffsetPx = Shader.PropertyToID("_ChromaticAberrationPx");
        private static readonly int PropRedScarfGlitch = Shader.PropertyToID("_RedScarfGlitchIntensity");
        private static readonly int PropResonanceGlow = Shader.PropertyToID("_ResonanceGlowMultiplier");

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;

            _sfxSource = GetComponent<AudioSource>();
            _sfxSource.playOnAwake = false;

            _harmonicSource = gameObject.AddComponent<AudioSource>();
            _harmonicSource.playOnAwake = false;

            if (CameraRigTransform != null)
            {
                _cameraBaseLocalPos = CameraRigTransform.localPosition;
            }

            InitializeSpringsAndDiceRow();
        }

        public void InitializeSpringsAndDiceRow()
        {
            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    _tileSprings[r, c] = new DampedSpringState(1.0f, DefaultSpringZeta, DefaultSpringOmegaN);
                }
            }

            ActivationRow.Clear();
            int[] initialPips = { 2, 4, 4, 6, 1 };
            for (int i = 0; i < 5; i++)
            {
                ActivationRow.Add(new TacticalActivationDie
                {
                    SlotIndex = i,
                    PipValue = initialPips[i],
                    IsLocked = false,
                    ScaleSpring = new DampedSpringState(1.0f, DefaultSpringZeta, DefaultSpringOmegaN),
                    TiltSpring = new DampedSpringState(0.0f, DefaultSpringZeta, DefaultSpringOmegaN)
                });
            }

            EvaluateDiceRowResonance();
        }

        private void Update()
        {
            float dt = Time.unscaledDeltaTime;

            // Step board and 3x3 tile damped springs (zeta=0.42, omega_n=30 rad/s)
            _boardScaleSpring.Step(dt);
            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    _tileSprings[r, c].Step(dt);
                }
            }

            for (int i = 0; i < ActivationRow.Count; i++)
            {
                ActivationRow[i].ScaleSpring.Step(dt);
                ActivationRow[i].TiltSpring.Step(dt);
            }

            // Decay screen-shake trauma & chromatic aberration pulse
            if (_screenShakeTrauma > 0.001f)
            {
                _screenShakeTrauma = Mathf.Max(0f, _screenShakeTrauma - dt * 2.8f);
                float shake = _screenShakeTrauma * _screenShakeTrauma;
                if (CameraRigTransform != null)
                {
                    float ox = (Mathf.PerlinNoise(Time.unscaledTime * 42f, 1.3f) * 2f - 1f) * 0.22f * shake;
                    float oy = (Mathf.PerlinNoise(2.7f, Time.unscaledTime * 42f) * 2f - 1f) * 0.22f * shake;
                    CameraRigTransform.localPosition = _cameraBaseLocalPos + new Vector3(ox, oy, 0f);
                }
            }
            else if (CameraRigTransform != null)
            {
                CameraRigTransform.localPosition = _cameraBaseLocalPos;
            }

            if (_chromaticPulseIntensity > 0.001f)
            {
                _chromaticPulseIntensity = Mathf.Max(0f, _chromaticPulseIntensity - dt * 6.0f);
                if (PostProcessChromaticMaterial != null)
                {
                    PostProcessChromaticMaterial.SetFloat(PropChromaticOffsetPx, _chromaticPulseIntensity * ChromaticAberrationPulsePx);
                }
            }
        }

        // =============================================================================================
        // 3. LUNA STATION OF AWAKENING 3-TAROT GENESIS SELECTION
        // =============================================================================================

        public void SelectLunaTarotGenesis(LunaTarotGenesisArchetype archetype)
        {
            ActiveTarotGenesis = archetype;
            switch (archetype)
            {
                case LunaTarotGenesisArchetype.SwordAggression:
                    BudgeTokens = Mathf.Min(MaxBudgeTokens, BudgeTokens + 1);
                    break;
                case LunaTarotGenesisArchetype.ShieldDefense:
                    BudgeTokens = Mathf.Min(MaxBudgeTokens, BudgeTokens + 1);
                    break;
                case LunaTarotGenesisArchetype.StaffControl:
                    ChronoRerollTokens = Mathf.Min(MaxChronoTokens, ChronoRerollTokens + 2);
                    BudgeTokens = Mathf.Min(MaxBudgeTokens, BudgeTokens + 1);
                    break;
            }

            _boardScaleSpring.Impulse(6.5f);
            AddScreenShakeTrauma(0.45f);
            PlaySynthesizedTarotGenesisChord(archetype);
        }

        // =============================================================================================
        // 4. DETERMINISTIC BUDGE (+1/-1) & CHRONO REROLL + RESONANCE EVALUATOR
        // =============================================================================================

        /// <summary>
        /// Applies a Dicevaders Budge (+1 or -1) to the die at <paramref name="dieIndex"/>.
        /// Wraps 6 <-> 1 when Quantum Relic / Archon Vex rule is active.
        /// </summary>
        public bool TryApplyBudge(int dieIndex, int delta, bool wrapQuantum = true)
        {
            if (BudgeTokens <= 0 || dieIndex < 0 || dieIndex >= ActivationRow.Count)
                return false;

            BudgeTokens--;
            TacticalActivationDie die = ActivationRow[dieIndex];
            int nextPip = die.PipValue + (delta >= 0 ? 1 : -1);
            if (wrapQuantum)
            {
                if (nextPip > 6) nextPip = 1;
                if (nextPip < 1) nextPip = 6;
            }
            else
            {
                nextPip = Mathf.Clamp(nextPip, 1, 6);
            }

            die.PipValue = nextPip;
            die.ScaleSpring.Impulse(8.5f);
            die.TiltSpring.Impulse(delta >= 0 ? 18.0f : -18.0f);

            EvaluateDiceRowResonance();
            PlaySynthesizedBudgeSnap(delta >= 0, die.PipValue);
            return true;
        }

        /// <summary>
        /// Spends 1 Chrono token to temporally rewind and reroll all unlocked dice in the 5-die Activation Row.
        /// </summary>
        public bool TryTriggerChronoReroll()
        {
            if (ChronoRerollTokens <= 0)
                return false;

            ChronoRerollTokens--;
            for (int i = 0; i < ActivationRow.Count; i++)
            {
                if (!ActivationRow[i].IsLocked)
                {
                    ActivationRow[i].PipValue = UnityEngine.Random.Range(1, 7);
                    ActivationRow[i].ScaleSpring.Impulse(10.0f);
                    ActivationRow[i].TiltSpring.Impulse((i % 2 == 0 ? 1f : -1f) * 24.0f);
                }
            }

            EvaluateDiceRowResonance();
            AddScreenShakeTrauma(0.35f);
            PlaySynthesizedChronoRewindSweep();
            return true;
        }

        /// <summary>
        /// Evaluates the 5-die Activation Row for Poker/Set Resonance Combos:
        /// Pair (1.50x), Two Pair (1.85x), Triple (2.25x), Straight Overdrive (2.75x), Quadruple/Five-of-a-Kind (3.50x)
        /// and maps pips to Columns (Col 0 = Pips 1-2, Col 1 = Pips 3-4, Col 2 = Pips 5-6).
        /// </summary>
        public ResonanceEvaluationResult EvaluateDiceRowResonance()
        {
            int[] counts = new int[7];
            bool[] cols = new bool[3];

            for (int i = 0; i < ActivationRow.Count; i++)
            {
                int pip = Mathf.Clamp(ActivationRow[i].PipValue, 1, 6);
                counts[pip]++;
                cols[ActivationRow[i].MappedColumn] = true;
            }

            int maxSame = 0;
            int pairsCount = 0;
            for (int p = 1; p <= 6; p++)
            {
                if (counts[p] > maxSame) maxSame = counts[p];
                if (counts[p] >= 2) pairsCount++;
            }

            bool isStraight =
                (counts[1] >= 1 && counts[2] >= 1 && counts[3] >= 1 && counts[4] >= 1) ||
                (counts[2] >= 1 && counts[3] >= 1 && counts[4] >= 1 && counts[5] >= 1) ||
                (counts[3] >= 1 && counts[4] >= 1 && counts[5] >= 1 && counts[6] >= 1);

            ResonanceEvaluationResult res = new ResonanceEvaluationResult
            {
                ActivatedColumns = cols
            };

            if (maxSame >= 4)
            {
                res.Tier = DicevadersResonanceTier.Quadruple;
                res.Label = "QUADRUPLE RESONANCE (3.50x)";
                res.Multiplier = 3.50f;
                res.BonusEdgeSurge = 3;
            }
            else if (isStraight)
            {
                res.Tier = DicevadersResonanceTier.StraightOverdrive;
                res.Label = "STRAIGHT OVERDRIVE (2.75x)";
                res.Multiplier = 2.75f;
                res.BonusEdgeSurge = 2;
            }
            else if (maxSame == 3)
            {
                res.Tier = DicevadersResonanceTier.Triple;
                res.Label = "TRIPLE RESONANCE (2.25x)";
                res.Multiplier = 2.25f;
                res.BonusEdgeSurge = 2;
            }
            else if (pairsCount >= 2)
            {
                res.Tier = DicevadersResonanceTier.TwoPair;
                res.Label = "TWO PAIR RESONANCE (1.85x)";
                res.Multiplier = 1.85f;
                res.BonusEdgeSurge = 1;
            }
            else if (maxSame == 2)
            {
                res.Tier = DicevadersResonanceTier.Pair;
                res.Label = "PAIR RESONANCE (1.50x)";
                res.Multiplier = 1.50f;
                res.BonusEdgeSurge = 1;
            }
            else
            {
                res.Tier = DicevadersResonanceTier.Single;
                res.Label = "SINGLE ALIGNMENT (1.00x)";
                res.Multiplier = 1.00f;
                res.BonusEdgeSurge = 0;
            }

            CurrentResonance = res;
            if (PostProcessChromaticMaterial != null)
            {
                PostProcessChromaticMaterial.SetFloat(PropResonanceGlow, res.Multiplier);
            }
            return res;
        }

        // =============================================================================================
        // 5. 55MS SEQUENTIAL TILE CASCADE, 48MS HIT-STOP FREEZE & HARMONIC PITCH ARPEGGIO
        // =============================================================================================

        public void TriggerTileCascadeSequence(List<Vector2Int> orderedTiles)
        {
            if (orderedTiles == null || orderedTiles.Count == 0)
                return;
            StartCoroutine(ExecuteCascadeCoroutine(orderedTiles));
        }

        private IEnumerator ExecuteCascadeCoroutine(List<Vector2Int> orderedTiles)
        {
            // Trigger 48ms (3-frame @ 60fps) Hit-Stop frame freeze on high resonance or multi-flip
            if (orderedTiles.Count >= 2 || CurrentResonance.Multiplier >= 2.25f)
            {
                yield return StartCoroutine(ExecuteHitStopFreezeCoroutine(HitStopFreezeSeconds));
            }

            for (int step = 0; step < orderedTiles.Count; step++)
            {
                Vector2Int cell = orderedTiles[step];
                int r = Mathf.Clamp(cell.x, 0, 2);
                int c = Mathf.Clamp(cell.y, 0, 2);

                _tileSprings[r, c].Impulse(11.5f);
                AddScreenShakeTrauma(0.28f + 0.10f * step);
                _chromaticPulseIntensity = 1.0f;

                // Play harmonic arpeggio shifted by +1.5 semitones per cascade step
                PlayHarmonicCascadeChime(step);

                yield return new WaitForSecondsRealtime(CascadeTileStaggerSeconds);
            }
        }

        public IEnumerator ExecuteHitStopFreezeCoroutine(float durationSeconds = HitStopFreezeSeconds)
        {
            if (_isHitStopped)
                yield break;

            _isHitStopped = true;
            float prevTimeScale = Time.timeScale;
            Time.timeScale = 0.0f;
            _chromaticPulseIntensity = 1.0f;

            yield return new WaitForSecondsRealtime(durationSeconds);

            Time.timeScale = prevTimeScale;
            _isHitStopped = false;
        }

        public void AddScreenShakeTrauma(float amount)
        {
            _screenShakeTrauma = Mathf.Clamp01(_screenShakeTrauma + amount);
        }

        public float GetTileSpringScale(int row, int col)
        {
            return _tileSprings[Mathf.Clamp(row, 0, 2), Mathf.Clamp(col, 0, 2)].Value;
        }

        // =============================================================================================
        // 6. PROCEDURAL 44.1KHZ HARMONIC WAVEFORM SYNTHESIZER (+1.5 SEMITONES PER CASCADE)
        // =============================================================================================

        public void PlayHarmonicCascadeChime(int cascadeIndex)
        {
            if (_harmonicSource == null)
                return;

            float semitoneShift = cascadeIndex * SemitonePitchStepPerCascade;
            float pitchRatio = Mathf.Pow(2.0f, semitoneShift / 12.0f);
            float baseFreq = 523.25f * pitchRatio; // C5 shifted +1.5 semitones per step

            int sampleCount = Mathf.RoundToInt(SampleRate * 0.24f);
            float[] buffer = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / SampleRate;
                float env = Mathf.Exp(-14.0f * t) * Mathf.Clamp01(t * 240.0f);
                float fundamental = Mathf.Sin(2.0f * Mathf.PI * baseFreq * t);
                float fifth = 0.45f * Mathf.Sin(2.0f * Mathf.PI * (baseFreq * 1.4983f) * t);
                float octaveBell = 0.25f * Mathf.Sin(2.0f * Mathf.PI * (baseFreq * 2.0f) * t);
                buffer[i] = (fundamental + fifth + octaveBell) * env * 0.55f;
            }

            AudioClip clip = AudioClip.Create($"cascade_step_{cascadeIndex}", sampleCount, 1, SampleRate, false);
            clip.SetData(buffer, 0);
            _harmonicSource.PlayOneShot(clip, MasterVolume);
        }

        public void PlaySynthesizedBudgeSnap(bool isPlus, int newPip)
        {
            if (_sfxSource == null)
                return;

            float f0 = isPlus ? 440.0f + newPip * 35.0f : 380.0f - (6 - newPip) * 25.0f;
            float f1 = isPlus ? f0 * 1.26f : f0 * 0.84f;
            int sampleCount = Mathf.RoundToInt(SampleRate * 0.11f);
            float[] buffer = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / SampleRate;
                float lerp = i / (float)sampleCount;
                float freq = Mathf.Lerp(f0, f1, lerp);
                float env = Mathf.Exp(-28.0f * t);
                buffer[i] = Mathf.Sin(2.0f * Mathf.PI * freq * t) * env * 0.6f;
            }

            AudioClip clip = AudioClip.Create("budge_snap", sampleCount, 1, SampleRate, false);
            clip.SetData(buffer, 0);
            _sfxSource.PlayOneShot(clip, MasterVolume);
        }

        public void PlaySynthesizedChronoRewindSweep()
        {
            if (_sfxSource == null)
                return;

            int sampleCount = Mathf.RoundToInt(SampleRate * 0.32f);
            float[] buffer = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / SampleRate;
                float freq = 880.0f - 440.0f * Mathf.Sin(Mathf.PI * (t / 0.32f));
                float env = Mathf.Sin(Mathf.PI * (t / 0.32f));
                float wave = Mathf.Sin(2.0f * Mathf.PI * freq * t) + 0.35f * Mathf.Sin(2.0f * Mathf.PI * freq * 1.5f * t);
                buffer[i] = wave * env * 0.45f;
            }

            AudioClip clip = AudioClip.Create("chrono_rewind", sampleCount, 1, SampleRate, false);
            clip.SetData(buffer, 0);
            _sfxSource.PlayOneShot(clip, MasterVolume);
        }

        public void PlaySynthesizedTarotGenesisChord(LunaTarotGenesisArchetype archetype)
        {
            if (_harmonicSource == null)
                return;

            float root = archetype == LunaTarotGenesisArchetype.SwordAggression ? 329.63f
                       : archetype == LunaTarotGenesisArchetype.ShieldDefense ? 293.66f
                       : 392.00f;

            int sampleCount = Mathf.RoundToInt(SampleRate * 0.45f);
            float[] buffer = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / SampleRate;
                float env = Mathf.Exp(-6.5f * t) * Mathf.Clamp01(t * 80.0f);
                float n1 = Mathf.Sin(2.0f * Mathf.PI * root * t);
                float n2 = Mathf.Sin(2.0f * Mathf.PI * (root * 1.2599f) * t);
                float n3 = Mathf.Sin(2.0f * Mathf.PI * (root * 1.4983f) * t);
                float n4 = Mathf.Sin(2.0f * Mathf.PI * (root * 2.0f) * t);
                buffer[i] = (n1 + 0.7f * n2 + 0.8f * n3 + 0.5f * n4) * 0.25f * env;
            }

            AudioClip clip = AudioClip.Create("luna_tarot_genesis", sampleCount, 1, SampleRate, false);
            clip.SetData(buffer, 0);
            _harmonicSource.PlayOneShot(clip, MasterVolume);
        }
    }
}
