using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.GameLogic
{
    /// <summary>
    /// Enumeration of poker/Yahtzee-inspired Dicevaders (Steam AppID: 3917700) tactical resonance tiers
    /// evaluated across the active dice row to drive cascading 3x3 board activations and damage/capture multipliers.
    /// </summary>
    public enum DicevadersResonanceTier
    {
        SingleHighCard = 0, // 1.00x base activation
        Pair           = 1, // 1.50x resonance multiplier
        TwoPair        = 2, // 1.85x resonance multiplier
        Triple         = 3, // 2.25x resonance multiplier
        Straight       = 4, // 2.50x resonance multiplier (4+ sequential pips, e.g., 1-2-3-4, 2-3-4-5, 3-4-5-6)
        FullHouse      = 5, // 2.75x resonance multiplier (Triple + Pair)
        Quadruple      = 6  // 3.50x resonance multiplier (4 or more of a kind)
    }

    /// <summary>
    /// Directional stat slot boosted when a player spends a Budge charge to shift a die by ±1 pip.
    /// Maps directly to the 4 directional combat edges of a 3x3 card (Top/Right/Bottom/Left).
    /// </summary>
    public enum BudgeDirectionalEdge
    {
        Top    = 0,
        Right  = 1,
        Bottom = 2,
        Left   = 3
    }

    /// <summary>
    /// Dynamic enemy boss disruption archetypes inspired by StarVaders &amp; Dicevaders Pilot Bosses.
    /// </summary>
    public enum PilotDisruptionKind
    {
        None               = 0,
        JamColumn          = 1, // Locks a target column (0..2) from dice resonance activation until cleared by a Pair+ or Budge
        InvertPipPolarity  = 2, // Flips pip-to-column mapping (7 - pip: 1<->6, 2<->5, 3<->4) and reverses high/low comparisons
        DeployShieldBeacon = 3  // Places an armored Shield Beacon on (x, y) that absorbs the first activation cascade in its row/column
    }

    /// <summary>
    /// Represents a single 6-sided tactical die (1..6 pips) in the Dicevaders command tray,
    /// bound to the 3x3 tactical grid columns (Col 0 = Pips 1-2, Col 1 = Pips 3-4, Col 2 = Pips 5-6)
    /// and directional card stat resonance.
    /// </summary>
    [Serializable]
    public class DicevadersDie
    {
        public int dieIndex;
        [Range(1, 6)] public int pipValue;
        public bool isLockedForChronoReroll;
        public bool wasBudgedThisTurn;
        public int budgeDeltaApplied;
        public bool isCorruptedByPilotBoss;

        /// <summary>
        /// Maps pip 1..6 to 3x3 tactical grid column 0..2:
        /// Col 0 = Pips 1-2, Col 1 = Pips 3-4, Col 2 = Pips 5-6.
        /// When <paramref name="invertPolarity"/> is active, pip polarity is inverted (7 - pipValue) before mapping.
        /// </summary>
        public int GetMappedColumn(bool invertPolarity = false)
        {
            int effectivePip = Mathf.Clamp(pipValue, 1, 6);
            if (invertPolarity)
            {
                effectivePip = 7 - effectivePip;
            }
            return Mathf.Clamp((effectivePip - 1) / 2, 0, 2);
        }

        /// <summary>
        /// Maps pip 1..6 to 3x3 tactical grid row 0..2 via parity/triad cycling
        /// so each die naturally addresses a specific (col, row) coordinate or full column sweep.
        /// </summary>
        public int GetMappedRow(bool invertPolarity = false)
        {
            int effectivePip = Mathf.Clamp(pipValue, 1, 6);
            if (invertPolarity)
            {
                effectivePip = 7 - effectivePip;
            }
            return (effectivePip - 1) % 3;
        }

        /// <summary>
        /// Determines which directional card edge (Top/Right/Bottom/Left) receives the +1 Budge resonance boost.
        /// </summary>
        public BudgeDirectionalEdge GetResonantDirectionalEdge()
        {
            int idx = Mathf.Abs(dieIndex + pipValue) % 4;
            return (BudgeDirectionalEdge)idx;
        }

        public DicevadersDie Clone()
        {
            return new DicevadersDie
            {
                dieIndex = this.dieIndex,
                pipValue = this.pipValue,
                isLockedForChronoReroll = this.isLockedForChronoReroll,
                wasBudgedThisTurn = this.wasBudgedThisTurn,
                budgeDeltaApplied = this.budgeDeltaApplied,
                isCorruptedByPilotBoss = this.isCorruptedByPilotBoss
            };
        }
    }

    /// <summary>
    /// Represents the full active Dicevaders command tray state for a turn, including
    /// the 5 tactical dice, Budge charges, Chrono-Reroll tokens, accumulated combo charge,
    /// and per-column directional stat buffs applied to the 3x3 board.
    /// </summary>
    [Serializable]
    public class DiceRowState
    {
        public const int DefaultDiceCount = 5;
        public const int MinPip = 1;
        public const int MaxPip = 6;

        public List<DicevadersDie> dice = new List<DicevadersDie>();
        public int remainingBudgeCharges = 2;
        public int maxBudgeChargesPerTurn = 2;
        public int remainingChronoRerolls = 1;
        public int preservedComboCharge = 0;
        public int chronoShopRefreshCount = 0;
        public bool wrapBudgePips = true;

        /// <summary>
        /// Accumulated directional stat bonuses per column (index 0..2) granted by ApplyBudge this turn.
        /// </summary>
        public DirectionalStats[] columnBudgeStatBonuses = new DirectionalStats[TcgGameLogic.GridWidth];

        /// <summary>
        /// Current tactical draft shop / hand offer card IDs refreshed on Chrono-Reroll.
        /// </summary>
        public List<string> tacticalDraftShopCardIds = new List<string>();

        public IReadOnlyList<int> GetPipValues()
        {
            var pips = new List<int>(dice.Count);
            for (int i = 0; i < dice.Count; i++)
            {
                pips.Add(dice[i].pipValue);
            }
            return pips;
        }
    }

    /// <summary>
    /// Result of a deterministic ApplyBudge(dieIndex, delta) action.
    /// </summary>
    [Serializable]
    public struct BudgeActionResult
    {
        public bool success;
        public int dieIndex;
        public int previousPip;
        public int newPip;
        public int activatedColumn;
        public BudgeDirectionalEdge boostedEdge;
        public DirectionalStats updatedColumnBonus;
        public int cardsBoostedInColumn;
        public int remainingBudgeCharges;
    }

    /// <summary>
    /// Result of a deterministic ApplyChronoReroll(lockedIndices) temporal rewind action.
    /// </summary>
    [Serializable]
    public struct ChronoRerollResult
    {
        public bool success;
        public int[] previousPips;
        public int[] newPips;
        public int[] lockedIndices;
        public int preservedComboCharge;
        public int remainingChronoRerolls;
        public List<string> refreshedShopCardIds;
    }

    /// <summary>
    /// Represents a single cascading cell/column activation step generated by EvaluateComboResonance.
    /// </summary>
    [Serializable]
    public struct TacticalCascadeStep
    {
        public int stepOrder;
        public int dieIndex;
        public int pipValue;
        public int targetColumn;
        public int targetRow;
        public float scheduledTimeMs;
        public float effectiveMultiplier;
        public bool blockedByPilotDisruptor;
    }

    /// <summary>
    /// Full evaluation result returned by EvaluateComboResonance(IReadOnlyList&lt;int&gt; pips).
    /// </summary>
    [Serializable]
    public class ComboResonanceEvaluation
    {
        public DicevadersResonanceTier tier;
        public float multiplier;
        public string comboBannerTitle;
        public int primaryResonantPip;
        public int bonusConfidencePoints;
        public List<int> activatedColumnsOrder = new List<int>();
        public List<int> activatedRowsOrder = new List<int>();
        public List<TacticalCascadeStep> cascadeSteps = new List<TacticalCascadeStep>();
    }

    /// <summary>
    /// Damped harmonic spring animation &amp; tactile game-feel solver inspired by Dicevaders (3917700) and StarVaders.
    /// Governs card pop scale, Budge nudge impulse, hit-stop freeze frames, and sequential cascade timing.
    /// </summary>
    [Serializable]
    public class DicevadersJuiceSpringProfile
    {
        public float zeta = 0.42f;             // Underdamped spring ratio for snappy overshoot & settle
        public float omegaN = 30.0f;           // Natural angular frequency (rad/s)
        public float cascadeDelayMs = 55f;     // Inter-card / inter-column cascade step delay (ms)
        public float hitStopMs = 48f;          // Tactile impact freeze duration on capture / Triple+ combo (ms)
        public float scorePopScale = 1.45f;    // Peak scale multiplier when a combo multiplier badge pops

        /// <summary>
        /// Analytical underdamped second-order spring solver:
        /// x(t) = target + (x0 - target) * exp(-zeta * omegaN * t) * (cos(omegaD * t) + (zeta / sqrt(1 - zeta^2)) * sin(omegaD * t))
        /// Evaluates current value and velocity at time <paramref name="timeSeconds"/>.
        /// </summary>
        public float EvaluateAnalyticalSpring(float startValue, float targetValue, float timeSeconds)
        {
            if (timeSeconds <= 0f)
            {
                return startValue;
            }

            float clampedZeta = Mathf.Clamp(zeta, 0.01f, 0.99f);
            float omegaD = omegaN * Mathf.Sqrt(1.0f - clampedZeta * clampedZeta);
            float decay = Mathf.Exp(-clampedZeta * omegaN * timeSeconds);
            float sinTerm = (clampedZeta / Mathf.Sqrt(1.0f - clampedZeta * clampedZeta)) * Mathf.Sin(omegaD * timeSeconds);
            float cosTerm = Mathf.Cos(omegaD * timeSeconds);

            float displacement = (startValue - targetValue) * decay * (cosTerm + sinTerm);
            return targetValue + displacement;
        }

        /// <summary>
        /// Evaluates the instantaneous scale multiplier for a card or score badge pop at <paramref name="elapsedMs"/>
        /// after a hit-stop window of <see cref="hitStopMs"/>.
        /// </summary>
        public float EvaluateCardPopScaleAtMs(float elapsedMs, float comboMultiplier = 1.0f)
        {
            if (elapsedMs <= 0f)
            {
                return 1.0f;
            }

            // During the tactile hit-stop window, hold at peak compressed/popped anticipation scale
            float peakScale = scorePopScale + Mathf.Max(0f, comboMultiplier - 1.0f) * 0.12f;
            if (elapsedMs <= hitStopMs)
            {
                return peakScale;
            }

            float springTimeSeconds = (elapsedMs - hitStopMs) * 0.001f;
            return EvaluateAnalyticalSpring(peakScale, 1.0f, springTimeSeconds);
        }

        /// <summary>
        /// Computes the exact timeline trigger timestamp in milliseconds for cascade index <paramref name="stepIndex"/>.
        /// </summary>
        public float GetCascadeTimestampMs(int stepIndex, DicevadersResonanceTier tier)
        {
            int clampedIndex = Math.Max(0, stepIndex);
            float tierHitStopFactor = tier >= DicevadersResonanceTier.Triple ? hitStopMs : (hitStopMs * 0.5f);
            return clampedIndex * cascadeDelayMs + (clampedIndex > 0 ? tierHitStopFactor : 0f);
        }
    }

    /// <summary>
    /// Dynamic enemy boss disruptor inspired by StarVaders &amp; Dicevaders Enemy Pilots.
    /// Can jam a 3x3 column, invert pip polarity across the dice tray, or deploy a Shield Beacon on a board cell.
    /// </summary>
    [Serializable]
    public class PilotBossDisruptor
    {
        public string pilotId = "pilot_chrono_valkyrie";
        public string pilotTitle = "Commander Vex // Chrono-Invader";
        public PilotDisruptionKind activeDisruption = PilotDisruptionKind.None;
        public int jammedColumnIndex = -1;
        public bool isPipPolarityInverted = false;
        public Vector2Int shieldBeaconCell = new Vector2Int(-1, -1);
        public int shieldBeaconCharges = 0;
        public int turnsRemaining = 0;

        /// <summary>
        /// Triggers a deterministic boss disruption hazard on the 3x3 tactical board and dice tray.
        /// </summary>
        public void ActivateDisruption(PilotDisruptionKind kind, int targetColumnOrX, int targetRowOrY = 1, int durationTurns = 2)
        {
            activeDisruption = kind;
            turnsRemaining = Math.Max(1, durationTurns);

            switch (kind)
            {
                case PilotDisruptionKind.JamColumn:
                    jammedColumnIndex = Mathf.Clamp(targetColumnOrX, 0, TcgGameLogic.GridWidth - 1);
                    isPipPolarityInverted = false;
                    shieldBeaconCell = new Vector2Int(-1, -1);
                    shieldBeaconCharges = 0;
                    break;

                case PilotDisruptionKind.InvertPipPolarity:
                    jammedColumnIndex = -1;
                    isPipPolarityInverted = true;
                    shieldBeaconCell = new Vector2Int(-1, -1);
                    shieldBeaconCharges = 0;
                    break;

                case PilotDisruptionKind.DeployShieldBeacon:
                    jammedColumnIndex = -1;
                    isPipPolarityInverted = false;
                    shieldBeaconCell = new Vector2Int(
                        Mathf.Clamp(targetColumnOrX, 0, TcgGameLogic.GridWidth - 1),
                        Mathf.Clamp(targetRowOrY, 0, TcgGameLogic.GridHeight - 1));
                    shieldBeaconCharges = 1;
                    break;

                default:
                    ClearDisruption();
                    break;
            }
        }

        /// <summary>
        /// Evaluates whether a cascade step targeting (col, row) is intercepted by the Pilot Boss disruptor,
        /// consuming Shield Beacon charges or clearing a column jam if a Pair+ resonance overpowers it.
        /// </summary>
        public bool TryInterceptCascadeStep(int col, int row, DicevadersResonanceTier resonanceTier)
        {
            if (activeDisruption == PilotDisruptionKind.None || turnsRemaining <= 0)
            {
                return false;
            }

            if (activeDisruption == PilotDisruptionKind.JamColumn && col == jammedColumnIndex)
            {
                // A Quadruple or FullHouse resonance shatters the column jam immediately
                if (resonanceTier >= DicevadersResonanceTier.FullHouse)
                {
                    jammedColumnIndex = -1;
                    activeDisruption = PilotDisruptionKind.None;
                    turnsRemaining = 0;
                    return false;
                }
                return true;
            }

            if (activeDisruption == PilotDisruptionKind.DeployShieldBeacon &&
                shieldBeaconCharges > 0 &&
                shieldBeaconCell.x == col &&
                shieldBeaconCell.y == row)
            {
                shieldBeaconCharges--;
                if (shieldBeaconCharges <= 0)
                {
                    shieldBeaconCell = new Vector2Int(-1, -1);
                    activeDisruption = PilotDisruptionKind.None;
                }
                return true;
            }

            return false;
        }

        public void ClearDisruption()
        {
            activeDisruption = PilotDisruptionKind.None;
            jammedColumnIndex = -1;
            isPipPolarityInverted = false;
            shieldBeaconCell = new Vector2Int(-1, -1);
            shieldBeaconCharges = 0;
            turnsRemaining = 0;
        }
    }

    /// <summary>
    /// Core deterministic engine integrating Dicevaders (Steam AppID: 3917700) tactical dice-row manipulation,
    /// Budge RNG mitigation (+1 directional column buffs), Chrono-Reroll temporal rewinds, Poker/Yahtzee
    /// resonance multipliers, damped spring juice profiles, and Pilot Boss disruptors with our 3x3 TCG grid.
    /// </summary>
    public class SynapseDicevadersComboEngine
    {
        public const float MultiplierSingleHigh = 1.00f;
        public const float MultiplierPair       = 1.50f;
        public const float MultiplierTwoPair    = 1.85f;
        public const float MultiplierTriple     = 2.25f;
        public const float MultiplierStraight   = 2.50f;
        public const float MultiplierFullHouse  = 2.75f;
        public const float MultiplierQuadruple  = 3.50f;

        private static readonly string[] DefaultTacticalShopPool = new[]
        {
            "cf_01_mystic_mage",
            "cf_02_mech_knight",
            "cf_03_celestial_guardian",
            "cf_04_shadow_assassin",
            "cf_05_elemental_sprite",
            "cf_06_galactic_explorer",
            "cf_07_clockwork_sorcerer",
            "cf_08_phoenix_guardian",
            "cf_09_cyber_ninja",
            "cf_10_lunar_oracle"
        };

        public readonly DiceRowState rowState = new DiceRowState();
        public readonly DicevadersJuiceSpringProfile juiceProfile = new DicevadersJuiceSpringProfile();
        public readonly PilotBossDisruptor pilotDisruptor = new PilotBossDisruptor();

        private readonly TcgGameLogic _boardLogic;
        private readonly System.Random _rng;
        private int _deterministicSeed;

        public SynapseDicevadersComboEngine(TcgGameLogic boardLogic = null, int seed = 3917700)
        {
            _boardLogic = boardLogic;
            _deterministicSeed = seed;
            _rng = new System.Random(seed);
            InitializeDiceRow(DiceRowState.DefaultDiceCount);
        }

        /// <summary>
        /// Initializes or resets the dice row for a new turn and rolls deterministic initial pips (1..6).
        /// </summary>
        public void InitializeDiceRow(int diceCount = DiceRowState.DefaultDiceCount, IReadOnlyList<int> explicitPips = null)
        {
            int count = Mathf.Clamp(diceCount, 1, 8);
            rowState.dice.Clear();
            rowState.remainingBudgeCharges = rowState.maxBudgeChargesPerTurn;
            rowState.remainingChronoRerolls = 1;

            for (int c = 0; c < TcgGameLogic.GridWidth; c++)
            {
                rowState.columnBudgeStatBonuses[c] = new DirectionalStats(0, 0, 0, 0);
            }

            for (int i = 0; i < count; i++)
            {
                int pip = (explicitPips != null && i < explicitPips.Count)
                    ? Mathf.Clamp(explicitPips[i], DiceRowState.MinPip, DiceRowState.MaxPip)
                    : _rng.Next(DiceRowState.MinPip, DiceRowState.MaxPip + 1);

                rowState.dice.Add(new DicevadersDie
                {
                    dieIndex = i,
                    pipValue = pip,
                    isLockedForChronoReroll = false,
                    wasBudgedThisTurn = false,
                    budgeDeltaApplied = 0,
                    isCorruptedByPilotBoss = false
                });
            }

            RefreshTacticalDraftShop(3);
        }

        /// <summary>
        /// Deterministic RNG mitigation ("Budge"): shifts die <paramref name="dieIndex"/> by ±1 pip
        /// (wrapping 6 &lt;-&gt; 1 when <c>rowState.wrapBudgePips</c> is enabled, or clamping to 1..6)
        /// and grants a +1 directional stat boost (Top/Right/Bottom/Left) to cards in the activated 3x3 column.
        /// Also increments combo charge so Budge plays build toward Chrono-Reroll synergies.
        /// </summary>
        public BudgeActionResult ApplyBudge(int dieIndex, int delta)
        {
            if (dieIndex < 0 || dieIndex >= rowState.dice.Count || rowState.remainingBudgeCharges <= 0 || delta == 0)
            {
                return new BudgeActionResult
                {
                    success = false,
                    dieIndex = dieIndex,
                    remainingBudgeCharges = rowState.remainingBudgeCharges
                };
            }

            int normalizedDelta = delta > 0 ? 1 : -1;
            var die = rowState.dice[dieIndex];
            int previousPip = die.pipValue;
            int nextPip = previousPip + normalizedDelta;

            if (rowState.wrapBudgePips)
            {
                if (nextPip > DiceRowState.MaxPip) nextPip = DiceRowState.MinPip;
                else if (nextPip < DiceRowState.MinPip) nextPip = DiceRowState.MaxPip;
            }
            else
            {
                nextPip = Mathf.Clamp(nextPip, DiceRowState.MinPip, DiceRowState.MaxPip);
            }

            die.pipValue = nextPip;
            die.wasBudgedThisTurn = true;
            die.budgeDeltaApplied += normalizedDelta;
            rowState.remainingBudgeCharges--;
            rowState.preservedComboCharge += 15;

            int activatedColumn = die.GetMappedColumn(pilotDisruptor.isPipPolarityInverted);
            BudgeDirectionalEdge edge = die.GetResonantDirectionalEdge();

            // Apply +1 to the corresponding directional edge in the activated column
            DirectionalStats colBonus = rowState.columnBudgeStatBonuses[activatedColumn];
            switch (edge)
            {
                case BudgeDirectionalEdge.Top:
                    colBonus.up += 1;
                    break;
                case BudgeDirectionalEdge.Right:
                    colBonus.right += 1;
                    break;
                case BudgeDirectionalEdge.Bottom:
                    colBonus.down += 1;
                    break;
                case BudgeDirectionalEdge.Left:
                    colBonus.left += 1;
                    break;
            }
            rowState.columnBudgeStatBonuses[activatedColumn] = colBonus;

            // If bound to a live 3x3 TcgGameLogic board, apply directional stat boost to friendly cards in that column
            int boostedCardsCount = 0;
            if (_boardLogic != null)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    var cell = _boardLogic.grid[activatedColumn, y];
                    if (cell != null && cell.occupant != null)
                    {
                        var stats = cell.occupant.baseStats;
                        switch (edge)
                        {
                            case BudgeDirectionalEdge.Top:    stats.up += 1; break;
                            case BudgeDirectionalEdge.Right:  stats.right += 1; break;
                            case BudgeDirectionalEdge.Bottom: stats.down += 1; break;
                            case BudgeDirectionalEdge.Left:   stats.left += 1; break;
                        }
                        cell.occupant.baseStats = stats;
                        boostedCardsCount++;
                    }
                }
            }

            // Budging a die inside a Pilot Boss jammed column weakens the jam by 1 turn
            if (pilotDisruptor.activeDisruption == PilotDisruptionKind.JamColumn &&
                pilotDisruptor.jammedColumnIndex == activatedColumn &&
                pilotDisruptor.turnsRemaining > 0)
            {
                pilotDisruptor.turnsRemaining--;
                if (pilotDisruptor.turnsRemaining <= 0)
                {
                    pilotDisruptor.ClearDisruption();
                }
            }

            return new BudgeActionResult
            {
                success = true,
                dieIndex = dieIndex,
                previousPip = previousPip,
                newPip = nextPip,
                activatedColumn = activatedColumn,
                boostedEdge = edge,
                updatedColumnBonus = colBonus,
                cardsBoostedInColumn = boostedCardsCount,
                remainingBudgeCharges = rowState.remainingBudgeCharges
            };
        }

        /// <summary>
        /// Temporal rewind ("Chrono-Reroll"): locks specified dice indices, rerolls all unlocked dice
        /// deterministically, and refreshes the tactical draft shop/hand while preserving accumulated combo charge.
        /// </summary>
        public ChronoRerollResult ApplyChronoReroll(int[] lockedIndices)
        {
            int count = rowState.dice.Count;
            var prevPips = new int[count];
            for (int i = 0; i < count; i++)
            {
                prevPips[i] = rowState.dice[i].pipValue;
            }

            if (rowState.remainingChronoRerolls <= 0)
            {
                return new ChronoRerollResult
                {
                    success = false,
                    previousPips = prevPips,
                    newPips = prevPips,
                    lockedIndices = lockedIndices ?? Array.Empty<int>(),
                    preservedComboCharge = rowState.preservedComboCharge,
                    remainingChronoRerolls = 0,
                    refreshedShopCardIds = new List<string>(rowState.tacticalDraftShopCardIds)
                };
            }

            var lockedSet = new HashSet<int>(lockedIndices ?? Array.Empty<int>());
            var newPips = new int[count];

            for (int i = 0; i < count; i++)
            {
                var die = rowState.dice[i];
                die.isLockedForChronoReroll = lockedSet.Contains(i);
                if (!die.isLockedForChronoReroll)
                {
                    die.pipValue = _rng.Next(DiceRowState.MinPip, DiceRowState.MaxPip + 1);
                }
                newPips[i] = die.pipValue;
            }

            rowState.remainingChronoRerolls--;
            rowState.chronoShopRefreshCount++;
            // Preserve and slightly amplify combo charge through the temporal rewind
            rowState.preservedComboCharge = Math.Max(25, rowState.preservedComboCharge);

            RefreshTacticalDraftShop(3);

            return new ChronoRerollResult
            {
                success = true,
                previousPips = prevPips,
                newPips = newPips,
                lockedIndices = lockedSet.OrderBy(idx => idx).ToArray(),
                preservedComboCharge = rowState.preservedComboCharge,
                remainingChronoRerolls = rowState.remainingChronoRerolls,
                refreshedShopCardIds = new List<string>(rowState.tacticalDraftShopCardIds)
            };
        }

        /// <summary>
        /// Evaluates Dicevaders resonance combos across <paramref name="pips"/>:
        /// - <see cref="DicevadersResonanceTier.Pair"/> (1.50x)
        /// - <see cref="DicevadersResonanceTier.TwoPair"/> (1.85x)
        /// - <see cref="DicevadersResonanceTier.Triple"/> (2.25x)
        /// - <see cref="DicevadersResonanceTier.Straight"/> (2.50x)
        /// - <see cref="DicevadersResonanceTier.FullHouse"/> (2.75x)
        /// - <see cref="DicevadersResonanceTier.Quadruple"/> (3.50x)
        /// Also computes the cascading column/row activation sequence and spring-timed cascade schedule.
        /// </summary>
        public ComboResonanceEvaluation EvaluateComboResonance(IReadOnlyList<int> pips)
        {
            var evaluation = new ComboResonanceEvaluation
            {
                tier = DicevadersResonanceTier.SingleHighCard,
                multiplier = MultiplierSingleHigh,
                comboBannerTitle = "SINGLE PULSE (1.00x)",
                primaryResonantPip = 1,
                bonusConfidencePoints = 0
            };

            if (pips == null || pips.Count == 0)
            {
                return evaluation;
            }

            int[] freq = new int[DiceRowState.MaxPip + 1];
            int maxPipSeen = 1;

            for (int i = 0; i < pips.Count; i++)
            {
                int clamped = Mathf.Clamp(pips[i], DiceRowState.MinPip, DiceRowState.MaxPip);
                if (pilotDisruptor.isPipPolarityInverted)
                {
                    clamped = 7 - clamped;
                }
                freq[clamped]++;
                if (clamped > maxPipSeen)
                {
                    maxPipSeen = clamped;
                }
            }

            int maxCount = 0;
            int primaryPip = maxPipSeen;
            int pairsCount = 0;
            bool hasTriple = false;
            bool hasPair = false;

            for (int p = DiceRowState.MaxPip; p >= DiceRowState.MinPip; p--)
            {
                int c = freq[p];
                if (c > maxCount)
                {
                    maxCount = c;
                    primaryPip = p;
                }
                if (c >= 3 && !hasTriple)
                {
                    hasTriple = true;
                }
                else if (c >= 2)
                {
                    hasPair = true;
                }

                if (c >= 2)
                {
                    pairsCount++;
                }
            }

            // Detect longest consecutive pip run for Straight (4+ sequential pips, e.g., 1-2-3-4, 2-3-4-5, 3-4-5-6)
            int longestRun = 0;
            int currentRun = 0;
            int highestStraightPip = maxPipSeen;
            for (int p = DiceRowState.MinPip; p <= DiceRowState.MaxPip; p++)
            {
                if (freq[p] > 0)
                {
                    currentRun++;
                    if (currentRun >= longestRun)
                    {
                        longestRun = currentRun;
                        highestStraightPip = p;
                    }
                }
                else
                {
                    currentRun = 0;
                }
            }

            bool isStraight = longestRun >= 4;

            if (maxCount >= 4)
            {
                evaluation.tier = DicevadersResonanceTier.Quadruple;
                evaluation.multiplier = MultiplierQuadruple;
                evaluation.comboBannerTitle = "QUADRUPLE OVERDRIVE (3.50x)";
                evaluation.primaryResonantPip = primaryPip;
                evaluation.bonusConfidencePoints = 40;
            }
            else if (hasTriple && hasPair)
            {
                evaluation.tier = DicevadersResonanceTier.FullHouse;
                evaluation.multiplier = MultiplierFullHouse;
                evaluation.comboBannerTitle = "FULL HOUSE SYNAPSE (2.75x)";
                evaluation.primaryResonantPip = primaryPip;
                evaluation.bonusConfidencePoints = 30;
            }
            else if (isStraight)
            {
                evaluation.tier = DicevadersResonanceTier.Straight;
                evaluation.multiplier = MultiplierStraight;
                evaluation.comboBannerTitle = "CHRONO STRAIGHT WAVE (2.50x)";
                evaluation.primaryResonantPip = highestStraightPip;
                evaluation.bonusConfidencePoints = 25;
            }
            else if (maxCount == 3)
            {
                evaluation.tier = DicevadersResonanceTier.Triple;
                evaluation.multiplier = MultiplierTriple;
                evaluation.comboBannerTitle = "TRIPLE RESONANCE (2.25x)";
                evaluation.primaryResonantPip = primaryPip;
                evaluation.bonusConfidencePoints = 20;
            }
            else if (pairsCount >= 2)
            {
                evaluation.tier = DicevadersResonanceTier.TwoPair;
                evaluation.multiplier = MultiplierTwoPair;
                evaluation.comboBannerTitle = "TWIN PAIR LINK (1.85x)";
                evaluation.primaryResonantPip = primaryPip;
                evaluation.bonusConfidencePoints = 15;
            }
            else if (maxCount == 2)
            {
                evaluation.tier = DicevadersResonanceTier.Pair;
                evaluation.multiplier = MultiplierPair;
                evaluation.comboBannerTitle = "RESONANT PAIR (1.50x)";
                evaluation.primaryResonantPip = primaryPip;
                evaluation.bonusConfidencePoints = 10;
            }
            else
            {
                evaluation.tier = DicevadersResonanceTier.SingleHighCard;
                evaluation.multiplier = MultiplierSingleHigh;
                evaluation.comboBannerTitle = "SINGLE PULSE (1.00x)";
                evaluation.primaryResonantPip = maxPipSeen;
                evaluation.bonusConfidencePoints = 5;
            }

            // Build cascading column/row activation order:
            // Resonant dice (higher frequency first, then pip value) fire sequentially with juiceProfile cascade spacing.
            var indexedDice = new List<(int dieIndex, int effectivePip, int frequency)>(pips.Count);
            for (int i = 0; i < pips.Count; i++)
            {
                int rawPip = Mathf.Clamp(pips[i], DiceRowState.MinPip, DiceRowState.MaxPip);
                int effectivePip = pilotDisruptor.isPipPolarityInverted ? (7 - rawPip) : rawPip;
                indexedDice.Add((i, effectivePip, freq[effectivePip]));
            }

            indexedDice.Sort((a, b) =>
            {
                int freqCmp = b.frequency.CompareTo(a.frequency);
                if (freqCmp != 0) return freqCmp;
                int pipCmp = b.effectivePip.CompareTo(a.effectivePip);
                if (pipCmp != 0) return pipCmp;
                return a.dieIndex.CompareTo(b.dieIndex);
            });

            for (int step = 0; step < indexedDice.Count; step++)
            {
                var entry = indexedDice[step];
                int col = Mathf.Clamp((entry.effectivePip - 1) / 2, 0, TcgGameLogic.GridWidth - 1);
                int row = (entry.effectivePip - 1) % TcgGameLogic.GridHeight;

                if (!evaluation.activatedColumnsOrder.Contains(col))
                {
                    evaluation.activatedColumnsOrder.Add(col);
                }
                if (!evaluation.activatedRowsOrder.Contains(row))
                {
                    evaluation.activatedRowsOrder.Add(row);
                }

                bool blocked = pilotDisruptor.TryInterceptCascadeStep(col, row, evaluation.tier);
                float scheduledMs = juiceProfile.GetCascadeTimestampMs(step, evaluation.tier);

                evaluation.cascadeSteps.Add(new TacticalCascadeStep
                {
                    stepOrder = step,
                    dieIndex = entry.dieIndex,
                    pipValue = entry.effectivePip,
                    targetColumn = col,
                    targetRow = row,
                    scheduledTimeMs = scheduledMs,
                    effectiveMultiplier = blocked ? 0.0f : evaluation.multiplier,
                    blockedByPilotDisruptor = blocked
                });
            }

            return evaluation;
        }

        private void RefreshTacticalDraftShop(int offerSize)
        {
            rowState.tacticalDraftShopCardIds.Clear();
            int count = Mathf.Clamp(offerSize, 1, DefaultTacticalShopPool.Length);
            int offset = (_deterministicSeed + rowState.chronoShopRefreshCount * 3) % DefaultTacticalShopPool.Length;
            if (offset < 0) offset += DefaultTacticalShopPool.Length;

            for (int i = 0; i < count; i++)
            {
                int poolIdx = (offset + i + _rng.Next(0, DefaultTacticalShopPool.Length)) % DefaultTacticalShopPool.Length;
                rowState.tacticalDraftShopCardIds.Add(DefaultTacticalShopPool[poolIdx]);
            }
        }

        /// <summary>
        /// Headless deterministic verification suite confirming all Dicevaders (3917700) mechanics:
        /// - Pip-to-Column mapping (Col 0 = 1-2, Col 1 = 3-4, Col 2 = 5-6)
        /// - ApplyBudge(dieIndex, delta) deterministic ±1 wrap/clamp shift &amp; +1 directional column stat bonus
        /// - ApplyChronoReroll(lockedIndices) temporal rewind preserving locked dice &amp; combo charge
        /// - EvaluateComboResonance exact multipliers for Pair (1.50x), TwoPair (1.85x), Triple (2.25x),
        ///   Straight (2.50x), FullHouse (2.75x), and Quadruple (3.50x)
        /// - DicevadersJuiceSpringProfile analytical spring solver &amp; PilotBossDisruptor interception
        /// </summary>
        public static bool RunHeadlessVerificationSuite(out string diagnosticReport)
        {
            var board = new TcgGameLogic(3917700);
            var engine = new SynapseDicevadersComboEngine(board, 3917700);
            engine.InitializeDiceRow(5, new[] { 2, 2, 4, 5, 6 });

            // 1. Verify Pip-to-Column mapping (1-2 -> Col 0, 3-4 -> Col 1, 5-6 -> Col 2)
            bool colMappingOk =
                engine.rowState.dice[0].GetMappedColumn() == 0 &&
                engine.rowState.dice[2].GetMappedColumn() == 1 &&
                engine.rowState.dice[4].GetMappedColumn() == 2;

            // 2. Verify ApplyBudge wraps 6 -> 1 and grants +1 directional stat bonus to Col 0
            BudgeActionResult budgeRes = engine.ApplyBudge(4, +1);
            bool budgeOk = budgeRes.success &&
                           budgeRes.previousPip == 6 &&
                           budgeRes.newPip == 1 &&
                           budgeRes.activatedColumn == 0 &&
                           engine.rowState.remainingBudgeCharges == 1;

            // 3. Verify ApplyChronoReroll preserves locked indices [0, 1] and refreshes tactical shop
            int lockedPip0 = engine.rowState.dice[0].pipValue;
            int lockedPip1 = engine.rowState.dice[1].pipValue;
            ChronoRerollResult rerollRes = engine.ApplyChronoReroll(new[] { 0, 1 });
            bool chronoOk = rerollRes.success &&
                            rerollRes.newPips[0] == lockedPip0 &&
                            rerollRes.newPips[1] == lockedPip1 &&
                            rerollRes.preservedComboCharge >= 25 &&
                            rerollRes.refreshedShopCardIds.Count == 3;

            // 4. Verify all 6 Combo Resonance Multipliers
            var evalPair      = engine.EvaluateComboResonance(new[] { 2, 2, 3, 5, 6 });
            var evalTwoPair   = engine.EvaluateComboResonance(new[] { 2, 2, 5, 5, 6 });
            var evalTriple    = engine.EvaluateComboResonance(new[] { 4, 4, 4, 1, 6 });
            var evalStraight  = engine.EvaluateComboResonance(new[] { 2, 3, 4, 5, 2 });
            var evalFullHouse = engine.EvaluateComboResonance(new[] { 3, 3, 3, 6, 6 });
            var evalQuadruple = engine.EvaluateComboResonance(new[] { 6, 6, 6, 6, 2 });

            bool combosOk =
                Mathf.Approximately(evalPair.multiplier, MultiplierPair) &&
                Mathf.Approximately(evalTwoPair.multiplier, MultiplierTwoPair) &&
                Mathf.Approximately(evalTriple.multiplier, MultiplierTriple) &&
                Mathf.Approximately(evalStraight.multiplier, MultiplierStraight) &&
                Mathf.Approximately(evalFullHouse.multiplier, MultiplierFullHouse) &&
                Mathf.Approximately(evalQuadruple.multiplier, MultiplierQuadruple);

            // 5. Verify DicevadersJuiceSpringProfile analytical damped spring & hit-stop scale
            float hitStopScale = engine.juiceProfile.EvaluateCardPopScaleAtMs(20f, MultiplierTriple);
            float settledScale = engine.juiceProfile.EvaluateCardPopScaleAtMs(650f, MultiplierTriple);
            bool springOk = hitStopScale >= engine.juiceProfile.scorePopScale &&
                            Mathf.Abs(settledScale - 1.0f) < 0.02f;

            // 6. Verify PilotBossDisruptor column jam and FullHouse breaker
            engine.pilotDisruptor.ActivateDisruption(PilotDisruptionKind.JamColumn, 1, 0, 2);
            var jammedEval = engine.EvaluateComboResonance(new[] { 3, 3, 1, 2, 5 });
            bool jamBlockedStep = jammedEval.cascadeSteps.Any(s => s.targetColumn == 1 && s.blockedByPilotDisruptor);
            var breakerEval = engine.EvaluateComboResonance(new[] { 3, 3, 3, 6, 6 });
            bool jamBrokenByFullHouse = engine.pilotDisruptor.activeDisruption == PilotDisruptionKind.None &&
                                        breakerEval.cascadeSteps.All(s => !s.blockedByPilotDisruptor);

            bool allPassed = colMappingOk && budgeOk && chronoOk && combosOk && springOk && jamBlockedStep && jamBrokenByFullHouse;
            diagnosticReport =
                $"[Dicevaders 3917700 Verification] AllPassed={allPassed} | ColMap={colMappingOk} | Budge={budgeOk} | " +
                $"ChronoReroll={chronoOk} | Combos={combosOk} (Pair={evalPair.multiplier:F2}x, TwoPair={evalTwoPair.multiplier:F2}x, " +
                $"Triple={evalTriple.multiplier:F2}x, Straight={evalStraight.multiplier:F2}x, FullHouse={evalFullHouse.multiplier:F2}x, " +
                $"Quad={evalQuadruple.multiplier:F2}x) | Spring(20ms={hitStopScale:F3}, 650ms={settledScale:F3}) | " +
                $"PilotDisruptor(Blocked={jamBlockedStep}, ShatteredByFullHouse={jamBrokenByFullHouse})";

            return allPassed;
        }
    }
}
