using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Clean-room Unity C# implementation of the 77-Skill / 91-Skill GameDev Harness patterns
    /// from `gamedev-skills/awesome-gamedev-agent-skills` (YouTube `t13A2XFGoOc` analysis),
    /// natively adapted for **Gemini 4 Argon (`gemini-4-argon`)** in `Synapse.TcgEngine`:
    /// 1. `unity-scriptableobjects`: Domain-Reload-safe `[NonSerialized]` runtime variable & event channel reset
    ///    (including `EditorApplication.playModeStateChanged` fast-Play-Mode reset per `unity-scriptableobjects/SKILL.md:83`).
    /// 2. `game-feel`: Decaying quadratic trauma (`shake = trauma * trauma`) smooth sine camera offset,
    ///    real-time `WaitForSecondsRealtime` hit-stop (`80ms`), and volume-conserving squash & stretch.
    /// 3. `game-ui-ux`: Anchor/safe-area normalization (`Screen.safeArea`) and keyboard/gamepad focus grid navigation.
    /// 4. `card-game`: Single-zone invariant validator (`Deck ∩ Hand ∩ Board ∩ Discard = ∅`) and seeded Fisher-Yates shuffle.
    /// </summary>
    [CreateAssetMenu(fileName = "SynapseRuntimeFloatVariable", menuName = "Synapse/77-Skill Harness (Gemini 4 Argon)/Runtime Float Variable")]
    public sealed class ScriptableObjectDomainReloadGuard : ScriptableObject
    {
        public const string TargetOrchestratorModel = "gemini-4-argon";

        [SerializeField] private float initialValue = 0f;
        [NonSerialized] public float RuntimeValue;

        public event Action<float> OnValueChanged;

        private void OnEnable()
        {
            RuntimeValue = initialValue;
#if UNITY_EDITOR
            UnityEditor.EditorApplication.playModeStateChanged -= HandlePlayModeStateChanged;
            UnityEditor.EditorApplication.playModeStateChanged += HandlePlayModeStateChanged;
#endif
        }

#if UNITY_EDITOR
        private void OnDisable()
        {
            UnityEditor.EditorApplication.playModeStateChanged -= HandlePlayModeStateChanged;
        }

        private void HandlePlayModeStateChanged(UnityEditor.PlayModeStateChange change)
        {
            if (change == UnityEditor.PlayModeStateChange.ExitingEditMode)
            {
                RuntimeValue = initialValue;
            }
        }
#endif

        public void SetValue(float newValue)
        {
            if (Mathf.Approximately(RuntimeValue, newValue)) return;
            RuntimeValue = newValue;
            OnValueChanged?.Invoke(RuntimeValue);
        }

        public void ResetToInitial()
        {
            RuntimeValue = initialValue;
            OnValueChanged?.Invoke(RuntimeValue);
        }
    }

    public sealed class GameFeelTraumaShakeAndHitStopController : MonoBehaviour
    {
        [Header("Game Feel Pattern 1: Quadratic Trauma Shake (shake = trauma^2)")]
        [SerializeField] private float traumaDecayPerSecond = 1.4f;
        [SerializeField] private Vector2 maxShakeOffset = new Vector2(12f, 8f);
        [SerializeField] private float maxShakeRollDegrees = 2.2f;

        private float _trauma;
        private float _noiseTime;
        private int _activeHitStopId;

        public float CurrentTrauma => _trauma;
        public float CurrentShake => _trauma * _trauma;

        public void AddTrauma(float amount)
        {
            _trauma = Mathf.Clamp01(_trauma + Mathf.Max(0f, amount));
        }

        public Vector3 EvaluateCameraShakeOffset(float deltaTime, out float rollAngleDegrees)
        {
            if (_trauma <= 0f)
            {
                rollAngleDegrees = 0f;
                return Vector3.zero;
            }

            _trauma = Mathf.Max(0f, _trauma - traumaDecayPerSecond * deltaTime);
            float shake = _trauma * _trauma; // Quadratic response: subtle on small hits, punchy on big captures
            _noiseTime += deltaTime * 30f;

            float offsetX = maxShakeOffset.x * shake * Mathf.Sin(_noiseTime * 1.7f);
            float offsetY = maxShakeOffset.y * shake * Mathf.Sin(_noiseTime * 2.3f);
            rollAngleDegrees = maxShakeRollDegrees * shake * Mathf.Sin(_noiseTime * 1.1f);
            return new Vector3(offsetX, offsetY, 0f);
        }

        public IEnumerator TriggerHitStopCoroutine(float durationRealtimeSeconds = 0.08f, float slowTimeScale = 0.05f)
        {
            _activeHitStopId++;
            int myId = _activeHitStopId;
            Time.timeScale = slowTimeScale;
            // WaitForSecondsRealtime ignores Time.timeScale so hit-stop always recovers cleanly
            yield return new WaitForSecondsRealtime(durationRealtimeSeconds);
            if (myId == _activeHitStopId)
            {
                Time.timeScale = 1.0f;
            }
        }

        public static Vector3 EvaluateVolumeConservingSquashStretch(float normalizedTime)
        {
            float t = Mathf.Clamp01(normalizedTime);
            if (t < 0.35f)
            {
                float p = t / 0.35f;
                return Vector3.Lerp(Vector3.one, new Vector3(1.14f, 0.88f, 1f), p);
            }
            if (t < 0.75f)
            {
                float p = (t - 0.35f) / 0.40f;
                return Vector3.Lerp(new Vector3(1.14f, 0.88f, 1f), new Vector3(0.95f, 1.05f, 1f), p);
            }
            float settle = (t - 0.75f) / 0.25f;
            return Vector3.Lerp(new Vector3(0.95f, 1.05f, 1f), Vector3.one, settle);
        }
    }

    public static class CardGameSingleZoneInvariantValidator
    {
        /// <summary>
        /// Verifies the `card-game/SKILL.md` Single-Zone Invariant: every card UID exists in
        /// at most one zone (`Deck`, `Hand`, `Board`, `Discard`) and total count is conserved.
        /// </summary>
        public static bool VerifySingleZoneInvariant(
            IReadOnlyCollection<string> deckUids,
            IReadOnlyCollection<string> handUids,
            IReadOnlyCollection<string> boardUids,
            IReadOnlyCollection<string> discardUids,
            int expectedTotalCount)
        {
            var seen = new HashSet<string>(StringComparer.Ordinal);
            IReadOnlyCollection<string>[] zones = { deckUids, handUids, boardUids, discardUids };

            int total = 0;
            for (int z = 0; z < zones.Length; z++)
            {
                if (zones[z] == null) continue;
                foreach (string uid in zones[z])
                {
                    if (string.IsNullOrEmpty(uid)) return false;
                    if (!seen.Add(uid)) return false; // Duplicate across or within zones
                    total++;
                }
            }
            return total == expectedTotalCount;
        }

        /// <summary>
        /// Seeded Fisher-Yates shuffle respecting exclusive upper bound on System.Random.Next(0, i + 1).
        /// </summary>
        public static void SeededFisherYatesShuffle<T>(IList<T> list, int seed)
        {
            if (list == null || list.Count <= 1) return;
            var rng = new System.Random(seed);
            for (int i = list.Count - 1; i > 0; i--)
            {
                int j = rng.Next(0, i + 1); // Exclusive upper bound -> includes i
                T temp = list[i];
                list[i] = list[j];
                list[j] = temp;
            }
        }
    }

    public sealed class GameUiUxFocusAndSafeAreaNavigator
    {
        public int FocusedHandIndex { get; private set; }
        public int FocusedBoardSlotIndex { get; private set; }

        public GameUiUxFocusAndSafeAreaNavigator()
        {
            FocusedHandIndex = 0;
            FocusedBoardSlotIndex = 4; // Center slot (1,1) of 3x3 board
        }

        public int MoveBoardFocus3x3(int deltaX, int deltaY)
        {
            int row = FocusedBoardSlotIndex / 3;
            int col = FocusedBoardSlotIndex % 3;
            col = Mathf.Clamp(col + deltaX, 0, 2);
            row = Mathf.Clamp(row + deltaY, 0, 2);
            FocusedBoardSlotIndex = row * 3 + col;
            return FocusedBoardSlotIndex;
        }

        public int SelectHandSlot(int index, int handCount)
        {
            if (handCount <= 0)
            {
                FocusedHandIndex = 0;
                return 0;
            }
            FocusedHandIndex = Mathf.Clamp(index, 0, handCount - 1);
            return FocusedHandIndex;
        }

        public static void ComputeNormalizedSafeAreaAnchors(
            Rect safeAreaPixels,
            int screenWidth,
            int screenHeight,
            out Vector2 anchorMin,
            out Vector2 anchorMax)
        {
            float w = Mathf.Max(1, screenWidth);
            float h = Mathf.Max(1, screenHeight);
            anchorMin = new Vector2(safeAreaPixels.xMin / w, safeAreaPixels.yMin / h);
            anchorMax = new Vector2(safeAreaPixels.xMax / w, safeAreaPixels.yMax / h);
        }
    }
}
