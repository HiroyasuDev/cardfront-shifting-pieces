using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Abilities
{
    public enum AbilityTrigger
    {
        None = 0,
        Ongoing = 2,
        Activate = 5,
        OnPlay = 10,
        OnCapture = 15,
        OnCaptured = 16,
        StartOfTurn = 20,
        EndOfTurn = 25,
        OnMoved = 30,
        OnDeath = 40
    }

    public enum AbilityTargetMode
    {
        None = 0,
        Self = 1,
        OrthogonalNeighbors = 2,
        OrthogonalFriendlyNeighbors = 3,
        OrthogonalEnemyNeighbors = 4,
        AllBoardCards = 5,
        AllFriendlyBoardCards = 6,
        AllEnemyBoardCards = 7,
        SelectedEmptySlot = 8,
        CapturedTarget = 9
    }

    public enum ConditionKind
    {
        None = 0,
        OncePerGame = 1,
        OncePerTurn = 2,
        AdjacentThemeMatch = 3,
        IsNighttime = 4,
        MinCapturesThisTurn = 5,
        TargetSlotEmpty = 6
    }

    public enum FilterKind
    {
        None = 0,
        HighestTotalStats = 1,
        LowestTotalStats = 2,
        FirstMatch = 3
    }

    public enum EffectOperation
    {
        None = 0,
        AddPermanentAllSidesBonus = 1,
        ReverseDirectionalStatsTemp = 2,
        SwapBaseStatsWithTarget = 3,
        MoveToTargetEmptySlot = 4,
        GrantCaptureImmunityTurns = 5,
        ReturnCapturedToOwnerHand = 6,
        GrantBonusTurnMove = 7,
        DrawCards = 8,
        AwardConfidencePoints = 9,
        EvolveCard = 10
    }

    [Serializable]
    public struct ConditionSpec
    {
        public ConditionKind kind;
        public CardTheme requiredTheme;
        public int intValue;
    }

    [Serializable]
    public struct FilterSpec
    {
        public FilterKind kind;
        public int maxTargets;
    }

    [Serializable]
    public struct EffectSpec
    {
        public EffectOperation operation;
        public int value;
        public int durationTurns;
    }

    /// <summary>
    /// Clean-room proprietary Composable Ability Definition (Trigger -> Condition -> Filter -> Effect).
    /// Replaces third-party AbilityData/ConditionData/FilterData/EffectData hierarchies with a
    /// cache-friendly, deterministic evaluator compatible with 3x3 directional grids and lane TCGs.
    /// </summary>
    [Serializable]
    public class SynapseAbilityDef
    {
        public string id;
        public string title;
        public string description;
        public AbilityTrigger trigger;
        public AbilityTargetMode targetMode;
        public List<ConditionSpec> conditions = new List<ConditionSpec>();
        public List<FilterSpec> filters = new List<FilterSpec>();
        public List<EffectSpec> effects = new List<EffectSpec>();
        public List<string> chainedAbilityIds = new List<string>();
    }

    public static class SynapseAbilityPipeline
    {
        public static bool AreConditionsMet(
            TcgGameLogic game,
            RuntimeCard caster,
            int casterX,
            int casterY,
            List<ConditionSpec> conditions,
            int targetX = -1,
            int targetY = -1,
            int capturesJustMade = 0)
        {
            if (conditions == null || conditions.Count == 0) return true;

            foreach (var cond in conditions)
            {
                switch (cond.kind)
                {
                    case ConditionKind.OncePerGame:
                        if (caster.oncePerGameAbilityUsed) return false;
                        break;
                    case ConditionKind.OncePerTurn:
                        if (caster.movedThisTurn) return false;
                        break;
                    case ConditionKind.IsNighttime:
                        if (!game.isNighttime) return false;
                        break;
                    case ConditionKind.MinCapturesThisTurn:
                        if (capturesJustMade < cond.intValue) return false;
                        break;
                    case ConditionKind.TargetSlotEmpty:
                        if (!game.InBounds(targetX, targetY) || !game.grid[targetX, targetY].IsEmpty)
                            return false;
                        break;
                    case ConditionKind.AdjacentThemeMatch:
                        if (!game.HasOrthogonalNeighborWithTheme(casterX, casterY, cond.requiredTheme))
                            return false;
                        break;
                }
            }
            return true;
        }
    }
}
