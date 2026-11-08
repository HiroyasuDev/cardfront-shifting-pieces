using System;
using System.Collections.Generic;
using System.Linq;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Advance Wars 1 & 2 Terrain Defense Star rating (0★ to 4★).
    /// Each star grants (10% * VisualHP / 10) damage reduction in the decompiled Advance Wars formula.
    /// </summary>
    public enum TerrainDefenseType
    {
        Road_0Star       = 0, // 0★: Road, Bridge, Reef, Open Sky (0% terrain defense)
        Plain_1Star      = 1, // 1★: Open Plains (10% defense at 10 HP)
        Woods_2Star      = 2, // 2★: Woods / Forest Cover (20% defense at 10 HP)
        Citadel_3Star    = 3, // 3★: City, Factory Base, Airport, Port (30% defense at 10 HP + supply repair)
        HQMountain_4Star = 4  // 4★: Headquarters / Mountain Fortress (40% defense at 10 HP)
    }

    /// <summary>
    /// Final Fantasy Tactics Advance 4-way isometric unit facing compass direction.
    /// </summary>
    public enum UnitFacingDirection
    {
        North = 0, // (0, +1)
        East  = 1, // (+1, 0)
        South = 2, // (0, -1)
        West  = 3  // (-1, 0)
    }

    /// <summary>
    /// Final Fantasy Tactics Advance directional attack angle classification relative to defender's facing.
    /// </summary>
    public enum FacingAttackAngle
    {
        Front     = 0, // 1.00x Damage, +0% Hit, +0 Directional Stat Bonus
        SideFlank = 1, // 1.25x Damage, +15% Hit, +1 Directional Stat Bonus
        BackRear  = 2  // 1.50x Damage, +30% Hit, +2 Directional Stat Bonus + Guaranteed Push
    }

    /// <summary>
    /// All 12 Classic-Yet-Dynamic Telegraph & Battle Cut-In Archetypes synthesized from
    /// Advance Wars 1/2, Final Fantasy Tactics Advance, Into the Breach, and STACCS.
    /// </summary>
    public enum TelegraphArchetype
    {
        AdvanceWars_SegmentedPathArrow      = 0,  // 16x16 modular red movement path arrow + bouncing head
        AdvanceWars_CrosshairDamageForecast = 1,  // 4-corner reticle + instant deterministic % Damage & Counter HUD badge
        AdvanceWars_SplitScreenBattleCutIn  = 2,  // WIN0/WIN1 curtain wipe + terrain parallax + 5-unit squad volley
        AdvanceWars_CoPowerBannerFlash      = 3,  // Full-width eyes-flash speedline banner + golden groove wave
        Ffta_IsometricTileHighlightDiamond  = 4,  // Translucent cyan move / amber attack / crimson AoE isometric diamonds
        Ffta_DirectionalFacingRing          = 5,  // 4-compass chevron ring indicating Front (1.0x), Flank (1.25x), Back (1.50x)
        Ffta_MythrilComboLinkArcs           = 6,  // Pulsing golden bezier energy arcs linking JP Mythril Combo allies
        Ffta_JudgeLawCardBroadcast          = 7,  // Hovering Judge whistle + Law Commendation / Yellow / Red Card banner
        IntoTheBreach_TelegraphHazardStripes= 8,  // Animated diagonal amber/crimson hazard stripes + attack vector arrow
        IntoTheBreach_KineticPushBumpPreview= 9,  // Pulsing directional push arrow + red collision star (DAMAGE_BUMP)
        Staccs_IsometricCubeGhostStack      = 10, // Translucent 3-rhombus cube ghost hovering at target Z = N with +Flank badge
        Staccs_CantileverOverhangShearArc   = 11  // Parabolic lift -> 45% cantilever overhang shadow -> rigidbody clack drop
    }

    /// <summary>
    /// Commanding Officer (CO) Power & Super CO Power profile decompiled from Advance Wars 1 & 2.
    /// </summary>
    [Serializable]
    public class CoPowerProfile
    {
        public const int GoldValuePerStar = 9000;
        public const float CostScalingPerActivation = 1.20f;

        public string coId;
        public string coName;
        public string normalPowerName;
        public string superPowerName;
        public int normalStarCost = 3;
        public int superStarCost = 6;
        public int baseFirepowerPercent = 100;
        public int baseDefensePercent = 100;
        public int normalPowerFirepowerPercent = 110;
        public int normalPowerDefensePercent = 110;
        public int superPowerFirepowerPercent = 130;
        public int superPowerDefensePercent = 120;

        public int currentStarMeterGold = 0;
        public int activationsCount = 0;
        public bool isNormalPowerActive = false;
        public bool isSuperPowerActive = false;

        public int CurrentFirepowerPercent =>
            isSuperPowerActive ? superPowerFirepowerPercent :
            (isNormalPowerActive ? normalPowerFirepowerPercent : baseFirepowerPercent);

        public int CurrentDefensePercent =>
            isSuperPowerActive ? superPowerDefensePercent :
            (isNormalPowerActive ? normalPowerDefensePercent : baseDefensePercent);

        public int GetScaledStarCostGold(bool superPower)
        {
            int stars = superPower ? superStarCost : normalStarCost;
            int scaled = Math.Min(10, activationsCount);
            double multiplier = 1.0 + (0.20 * scaled);
            return (int)Math.Round(stars * GoldValuePerStar * multiplier);
        }

        public bool CanActivateNormalPower => currentStarMeterGold >= GetScaledStarCostGold(false);
        public bool CanActivateSuperPower => currentStarMeterGold >= GetScaledStarCostGold(true);

        public bool TryActivateCoPower(bool superPower)
        {
            int requiredGold = GetScaledStarCostGold(superPower);
            if (currentStarMeterGold < requiredGold) return false;

            currentStarMeterGold -= requiredGold;
            activationsCount++;
            if (superPower)
            {
                isSuperPowerActive = true;
                isNormalPowerActive = false;
            }
            else
            {
                isNormalPowerActive = true;
                isSuperPowerActive = false;
            }
            return true;
        }

        public void EndTurnClearActivePower()
        {
            isNormalPowerActive = false;
            isSuperPowerActive = false;
        }

        public CoPowerProfile Clone() => (CoPowerProfile)MemberwiseClone();
    }

    /// <summary>
    /// Final Fantasy Tactics Advance CTB (Charge Time Battle) 1000-tick turn-order queue entry.
    /// </summary>
    [Serializable]
    public class CtbTurnQueueEntry
    {
        public const int ReadyThresholdCt = 1000;
        public const int WaitRetainedCt = 500;
        public const int PartialActionRetainedCt = 200;

        public string cardUid;
        public int ownerId;
        public int x;
        public int y;
        public int speed;
        public int chargeTime;

        public bool IsReadyToAct => chargeTime >= ReadyThresholdCt;

        public void ConsumeTurnCt(bool moved, bool acted)
        {
            if (!moved && !acted)
            {
                // Wait: retains 500 CT (only deducts 500 CT)
                chargeTime = Math.Max(0, chargeTime - (ReadyThresholdCt - WaitRetainedCt));
            }
            else if (moved ^ acted)
            {
                // Moved only OR Acted only: retains 200 CT (deducts 800 CT)
                chargeTime = Math.Max(0, chargeTime - (ReadyThresholdCt - PartialActionRetainedCt));
            }
            else
            {
                // Full Move + Action: deducts full 1000 CT
                chargeTime = Math.Max(0, chargeTime - ReadyThresholdCt);
            }
        }

        public CtbTurnQueueEntry Clone() => (CtbTurnQueueEntry)MemberwiseClone();
    }

    /// <summary>
    /// Rich presentation & tactical payload for any of the 12 Classic-Yet-Dynamic Telegraph Archetypes.
    /// Drives both deterministic AI/UI previews and classic GBA/Isometric battle cut-ins.
    /// </summary>
    [Serializable]
    public class TelegraphDescriptor
    {
        public string telegraphId;
        public TelegraphArchetype archetype;
        public int sourceX;
        public int sourceY;
        public int targetX;
        public int targetY;
        public List<(int x, int y)> pathWaypoints = new List<(int x, int y)>();
        public int forecastedDamagePercent;
        public int forecastedCounterPercent;
        public int attackerSquadCount;
        public int defenderSquadCount;
        public TerrainDefenseType defenderTerrain;
        public UnitFacingDirection defenderFacing;
        public FacingAttackAngle attackAngle;
        public float facingDamageMultiplier = 1.0f;
        public int elevationDeltaZ;
        public int mythrilComboAllyCount;
        public (int dx, int dy) pushDirection;
        public bool predictsBumpCollision;
        public float cantileverOverhangRatio = 0.45f;
        public string headlineBannerText;
    }

    /// <summary>
    /// Synthesizes Intelligent Systems' Advance Wars 1/2 (exact damage%, terrain stars, CO Power meters,
    /// split-screen squad cut-ins) and Square Enix's Final Fantasy Tactics Advance (isometric directional
    /// facing multipliers, elevation advantage, 1000-tick CTB turn queue, Judge Points JP 0..10, Mythril
    /// Combos, and Totema summons) on top of SynapseBreachStackEngine.
    /// </summary>
    public class SynapseAdvanceWarsFftaDynamicsEngine
    {
        public const int MaxJudgePoints = 10;
        public const int TotemaRequiredJp = 5;

        public readonly SynapseBreachStackEngine BreachEngine;
        public readonly TerrainDefenseType[,] TerrainGrid = new TerrainDefenseType[TcgGameLogic.GridWidth, TcgGameLogic.GridHeight];
        public readonly UnitFacingDirection[,] FacingGrid = new UnitFacingDirection[TcgGameLogic.GridWidth, TcgGameLogic.GridHeight];
        public readonly int[,] VisualHpGrid = new int[TcgGameLogic.GridWidth, TcgGameLogic.GridHeight];
        public readonly CoPowerProfile[] PlayerCoProfiles = new CoPowerProfile[2];
        public readonly int[] PlayerJudgePoints = new int[2] { 0, 0 };
        public readonly List<CtbTurnQueueEntry> CtbTurnQueue = new List<CtbTurnQueueEntry>();
        public readonly List<TelegraphDescriptor> ActiveTelegraphFeed = new List<TelegraphDescriptor>();

        public SynapseAdvanceWarsFftaDynamicsEngine(SynapseBreachStackEngine breachEngine = null, int seed = 1337)
        {
            BreachEngine = breachEngine ?? new SynapseBreachStackEngine(seed);
            InitializeDefaultTerrainAndCoProfiles();
        }

        private void InitializeDefaultTerrainAndCoProfiles()
        {
            // Default classic symmetrical tactical layout on the 3x3 grid:
            // Center (1,1) is a 4★ HQ/Mountain citadel; corners are 2★ Woods; mid-flanks are 3★ Cities / 1★ Plains
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    VisualHpGrid[x, y] = 10;
                    FacingGrid[x, y] = (y == 0) ? UnitFacingDirection.North : UnitFacingDirection.South;

                    if (x == 1 && y == 1)
                        TerrainGrid[x, y] = TerrainDefenseType.HQMountain_4Star;
                    else if ((x == 0 || x == 2) && (y == 0 || y == 2))
                        TerrainGrid[x, y] = TerrainDefenseType.Woods_2Star;
                    else if (x == 1)
                        TerrainGrid[x, y] = TerrainDefenseType.Citadel_3Star;
                    else
                        TerrainGrid[x, y] = TerrainDefenseType.Plain_1Star;
                }
            }

            PlayerCoProfiles[0] = new CoPowerProfile
            {
                coId = "co_andy_vanguard",
                coName = "Commander Andy (Frontier Vanguard)",
                normalPowerName = "Hyper Repair (+2 HP & +10% All Stats)",
                superPowerName = "Hyper Upgrade (+2 All Directional Sides & +30% Firepower)",
                normalStarCost = 3,
                superStarCost = 6,
                baseFirepowerPercent = 100,
                baseDefensePercent = 100,
                normalPowerFirepowerPercent = 110,
                normalPowerDefensePercent = 110,
                superPowerFirepowerPercent = 130,
                superPowerDefensePercent = 120
            };

            PlayerCoProfiles[1] = new CoPowerProfile
            {
                coId = "co_kanbei_magister",
                coName = "High Magister Kanbei (Imperial Guard)",
                normalPowerName = "Morale Boost (+130% Firepower)",
                superPowerName = "Samurai Spirit (+150% Firepower & +150% Counter)",
                normalStarCost = 4,
                superStarCost = 7,
                baseFirepowerPercent = 110,
                baseDefensePercent = 110,
                normalPowerFirepowerPercent = 130,
                normalPowerDefensePercent = 120,
                superPowerFirepowerPercent = 150,
                superPowerDefensePercent = 140
            };
        }

        // =========================================================================================
        // 1. ADVANCE WARS EXACT DAMAGE FORMULA, TERRAIN STARS, & CO POWER METER
        // =========================================================================================

        /// <summary>
        /// Computes the exact decompiled Advance Wars 1 & 2 percentage damage formula:
        /// Damage% = ((BaseDamage * AttackerCO / 100) + Luck) * (AttackerHP / 10.0) * ((200 - (DefenderCO + TerrainStars * DefenderHP)) / 100.0)
        /// Enhanced with FFTA Directional Facing (1.0x Front, 1.25x SideFlank, 1.50x BackRear),
        /// Isometric Elevation ΔZ advantage, and Mythril Combo Link bonuses (+25% per linked ally).
        /// </summary>
        public int ComputeAdvanceWarsFftaDamagePercent(
            int attackerX,
            int attackerY,
            int defenderX,
            int defenderY,
            int baseWeaponDamage = 55,
            int luckRoll = 0,
            int mythrilComboAllies = 0)
        {
            if (!BreachEngine.InBounds(attackerX, attackerY) || !BreachEngine.InBounds(defenderX, defenderY))
                return 0;

            var atkStack = BreachEngine.stacks[attackerX, attackerY];
            var defStack = BreachEngine.stacks[defenderX, defenderY];
            int atkOwner = atkStack.TopCard?.ownerId ?? 0;
            int defOwner = defStack.TopCard?.ownerId ?? 1;

            int attackerCo = PlayerCoProfiles[atkOwner].CurrentFirepowerPercent;
            int defenderCo = PlayerCoProfiles[defOwner].CurrentDefensePercent;

            int attackerHp = Math.Max(1, Math.Min(10, VisualHpGrid[attackerX, attackerY]));
            int defenderHp = Math.Max(1, Math.Min(10, VisualHpGrid[defenderX, defenderY]));
            int terrainStars = (int)TerrainGrid[defenderX, defenderY];

            // Core Advance Wars formula
            int coScaledBase = (baseWeaponDamage * attackerCo) / 100 + luckRoll;
            double hpFactor = attackerHp / 10.0;
            int rawDefTerm = defenderCo + (terrainStars * defenderHp);
            double defenseMultiplier = Math.Max(0.05, (200 - rawDefTerm) / 100.0);

            double awDamage = coScaledBase * hpFactor * defenseMultiplier;

            // FFTA Directional Facing multiplier (Front = 1.0x, SideFlank = 1.25x, BackRear = 1.50x)
            var angle = ClassifyAttackAngle(attackerX, attackerY, defenderX, defenderY, FacingGrid[defenderX, defenderY]);
            double facingMultiplier = GetFacingDamageMultiplier(angle);

            // FFTA + STACCS Isometric Elevation ΔZ bonus (+10% per height layer above defender, up to +30%)
            int deltaZ = Math.Max(0, Math.Min(3, atkStack.StackHeight - defStack.StackHeight));
            double elevationMultiplier = 1.0 + (0.10 * deltaZ);

            // FFTA Mythril Combo Link bonus (+25% per linked ally)
            double comboMultiplier = 1.0 + (0.25 * Math.Max(0, mythrilComboAllies));

            int finalDamagePercent = (int)Math.Floor(awDamage * facingMultiplier * elevationMultiplier * comboMultiplier);
            return Math.Max(1, finalDamagePercent);
        }

        /// <summary>
        /// Charges both players' Advance Wars CO Power Star Meters based on combat damage exchanged
        /// and awards FFTA Judge Points (JP 0..10) for tactical engagement.
        /// </summary>
        public void RecordCombatEngagement(int attackerPlayerId, int defenderPlayerId, int damagePercentDealt)
        {
            int goldEquivalent = Math.Max(500, damagePercentDealt * 100);
            PlayerCoProfiles[attackerPlayerId].currentStarMeterGold += goldEquivalent / 2;
            PlayerCoProfiles[defenderPlayerId].currentStarMeterGold += goldEquivalent;

            PlayerJudgePoints[attackerPlayerId] = Math.Min(MaxJudgePoints, PlayerJudgePoints[attackerPlayerId] + 1);
            if (damagePercentDealt >= 50)
            {
                PlayerJudgePoints[attackerPlayerId] = Math.Min(MaxJudgePoints, PlayerJudgePoints[attackerPlayerId] + 1);
            }
        }

        // =========================================================================================
        // 2. FFTA DIRECTIONAL FACING, CTB 1000-TICK TURN QUEUE, JP COMBOS, & TOTEMA SUMMONS
        // =========================================================================================

        /// <summary>
        /// Classifies whether an attack from (attackerX, attackerY) strikes the Front, SideFlank, or BackRear
        /// of a unit at (defenderX, defenderY) facing defenderFacing.
        /// </summary>
        public static FacingAttackAngle ClassifyAttackAngle(
            int attackerX,
            int attackerY,
            int defenderX,
            int defenderY,
            UnitFacingDirection defenderFacing)
        {
            // Vector from defender toward attacker
            int toAttackerX = Math.Sign(attackerX - defenderX);
            int toAttackerY = Math.Sign(attackerY - defenderY);

            (int fx, int fy) = GetFacingVector(defenderFacing);
            int dot = (toAttackerX * fx) + (toAttackerY * fy);

            if (dot > 0) return FacingAttackAngle.Front;     // Attacker is in front of defender
            if (dot < 0) return FacingAttackAngle.BackRear;  // Attacker is directly behind defender's back
            return FacingAttackAngle.SideFlank;              // Attacker is on the exposed Left or Right flank
        }

        public static (int dx, int dy) GetFacingVector(UnitFacingDirection dir) => dir switch
        {
            UnitFacingDirection.North => (0, 1),
            UnitFacingDirection.East  => (1, 0),
            UnitFacingDirection.South => (0, -1),
            UnitFacingDirection.West  => (-1, 0),
            _                         => (0, 1)
        };

        public static float GetFacingDamageMultiplier(FacingAttackAngle angle) => angle switch
        {
            FacingAttackAngle.Front     => 1.00f,
            FacingAttackAngle.SideFlank => 1.25f,
            FacingAttackAngle.BackRear  => 1.50f,
            _                           => 1.00f
        };

        public static int GetFacingDirectionalStatBonus(FacingAttackAngle angle) => angle switch
        {
            FacingAttackAngle.Front     => 0,
            FacingAttackAngle.SideFlank => 1,
            FacingAttackAngle.BackRear  => 2,
            _                           => 0
        };

        /// <summary>
        /// Rebuilds or synchronizes the FFTA CTB (Charge Time Battle) turn queue from all active stacks on the board.
        /// </summary>
        public void SyncCtbTurnQueueFromBoard()
        {
            BreachEngine.SyncGridOccupantsFromStacks();
            var activeUids = new HashSet<string>();

            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    var top = BreachEngine.stacks[x, y].TopCard;
                    if (top == null) continue;

                    activeUids.Add(top.uid);
                    var existing = CtbTurnQueue.Find(e => e.cardUid == top.uid);
                    var st = BreachEngine.GetStackEffectiveStats(x, y);
                    int computedSpeed = 100 + (st.up + st.down + st.left + st.right) * 5;

                    if (existing == null)
                    {
                        CtbTurnQueue.Add(new CtbTurnQueueEntry
                        {
                            cardUid = top.uid,
                            ownerId = top.ownerId,
                            x = x,
                            y = y,
                            speed = computedSpeed,
                            chargeTime = 0
                        });
                    }
                    else
                    {
                        existing.ownerId = top.ownerId;
                        existing.x = x;
                        existing.y = y;
                        existing.speed = computedSpeed;
                    }
                }
            }

            CtbTurnQueue.RemoveAll(e => !activeUids.Contains(e.cardUid));
        }

        /// <summary>
        /// Advances the deterministic FFTA 1000-tick CTB clock until at least one unit reaches CT >= 1000,
        /// returning the ready CtbTurnQueueEntry with the highest ChargeTime.
        /// </summary>
        public CtbTurnQueueEntry AdvanceCtbTurnQueue()
        {
            SyncCtbTurnQueueFromBoard();
            if (CtbTurnQueue.Count == 0) return null;

            int safetyTicks = 0;
            while (!CtbTurnQueue.Any(e => e.IsReadyToAct) && safetyTicks < 100)
            {
                safetyTicks++;
                for (int i = 0; i < CtbTurnQueue.Count; i++)
                {
                    CtbTurnQueue[i].chargeTime += Math.Max(10, CtbTurnQueue[i].speed);
                }
            }

            CtbTurnQueue.Sort((a, b) =>
            {
                int cmp = b.chargeTime.CompareTo(a.chargeTime);
                return cmp != 0 ? cmp : string.CompareOrdinal(a.cardUid, b.cardUid);
            });

            return CtbTurnQueue[0];
        }

        /// <summary>
        /// Invokes a 5-JP Final Fantasy Tactics Advance Totema Ultimate Summon:
        /// Deals board-wide catastrophe damage to all opposing stacks and grants +2 permanentStatBonus to friendly stacks.
        /// </summary>
        public bool InvokeTotemaSummon(int playerId, string totemaName = "Mateus, the Corrupt")
        {
            if (playerId < 0 || playerId >= 2 || PlayerJudgePoints[playerId] < TotemaRequiredJp)
                return false;

            PlayerJudgePoints[playerId] -= TotemaRequiredJp;

            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    var st = BreachEngine.stacks[x, y];
                    if (st.IsEmpty) continue;

                    if (st.TopCard.ownerId == playerId)
                    {
                        st.TopCard.permanentStatBonus += 1;
                        VisualHpGrid[x, y] = Math.Min(10, VisualHpGrid[x, y] + 2);
                    }
                    else
                    {
                        VisualHpGrid[x, y] = Math.Max(1, VisualHpGrid[x, y] - 4);
                        BreachEngine.ApplyDamageToCell(x, y, 2);
                    }
                }
            }

            ActiveTelegraphFeed.Add(new TelegraphDescriptor
            {
                telegraphId = "totema_" + Guid.NewGuid().ToString("N"),
                archetype = TelegraphArchetype.Ffta_JudgeLawCardBroadcast,
                sourceX = 1,
                sourceY = 1,
                targetX = 1,
                targetY = 1,
                forecastedDamagePercent = 100,
                headlineBannerText = $"TOTEMA SUMMON: {totemaName.ToUpperInvariant()} (5 JP EXPENDED)"
            });

            return true;
        }

        // =========================================================================================
        // 3. MULTITUDE OF CLASSIC-YET-DYNAMIC TELEGRAPH SUITE (ALL 12 ARCHETYPES)
        // =========================================================================================

        /// <summary>
        /// Generates the full suite of 12 Classic-Yet-Dynamic Telegraph Descriptors for an impending tactical engagement
        /// from (sourceX, sourceY) to (targetX, targetY), combining Advance Wars, FFTA, Into the Breach, and STACCS.
        /// </summary>
        public List<TelegraphDescriptor> BuildComprehensiveTelegraphSuite(
            int sourceX,
            int sourceY,
            int targetX,
            int targetY,
            int pushDx = 0,
            int pushDy = 0)
        {
            var suite = new List<TelegraphDescriptor>(12);
            if (!BreachEngine.InBounds(sourceX, sourceY) || !BreachEngine.InBounds(targetX, targetY))
                return suite;

            var srcStack = BreachEngine.stacks[sourceX, sourceY];
            var dstStack = BreachEngine.stacks[targetX, targetY];
            int attackerOwner = srcStack.TopCard?.ownerId ?? 0;

            // Count adjacent friendly stacks for FFTA Mythril Combo Link Arcs
            int comboAllies = CountLinkedComboAllies(targetX, targetY, attackerOwner, sourceX, sourceY);
            int dmgPercent = ComputeAdvanceWarsFftaDamagePercent(sourceX, sourceY, targetX, targetY, 65, 0, comboAllies);
            int counterPercent = dstStack.IsEmpty ? 0 : ComputeAdvanceWarsFftaDamagePercent(targetX, targetY, sourceX, sourceY, 45, 0, 0) / 2;

            var angle = ClassifyAttackAngle(sourceX, sourceY, targetX, targetY, FacingGrid[targetX, targetY]);
            float facingMult = GetFacingDamageMultiplier(angle);
            int deltaZ = srcStack.StackHeight - dstStack.StackHeight;

            int atkHp = VisualHpGrid[sourceX, sourceY];
            int defHp = VisualHpGrid[targetX, targetY];
            int atkSquad = Math.Max(1, (atkHp + 1) / 2);
            int defSquad = Math.Max(1, (defHp + 1) / 2);

            int destPushX = targetX + pushDx;
            int destPushY = targetY + pushDy;
            bool predictsBump = (pushDx != 0 || pushDy != 0) &&
                (!BreachEngine.InBounds(destPushX, destPushY) ||
                 !BreachEngine.stacks[destPushX, destPushY].IsEmpty ||
                 BreachEngine.stacks[destPushX, destPushY].isPowerGridBuilding);

            var waypoints = BuildOrthogonalPathWaypoints(sourceX, sourceY, targetX, targetY);

            foreach (TelegraphArchetype arch in Enum.GetValues(typeof(TelegraphArchetype)))
            {
                suite.Add(new TelegraphDescriptor
                {
                    telegraphId = $"tel_{(int)arch}_{sourceX}{sourceY}_{targetX}{targetY}",
                    archetype = arch,
                    sourceX = sourceX,
                    sourceY = sourceY,
                    targetX = targetX,
                    targetY = targetY,
                    pathWaypoints = new List<(int x, int y)>(waypoints),
                    forecastedDamagePercent = dmgPercent,
                    forecastedCounterPercent = counterPercent,
                    attackerSquadCount = atkSquad,
                    defenderSquadCount = defSquad,
                    defenderTerrain = TerrainGrid[targetX, targetY],
                    defenderFacing = FacingGrid[targetX, targetY],
                    attackAngle = angle,
                    facingDamageMultiplier = facingMult,
                    elevationDeltaZ = deltaZ,
                    mythrilComboAllyCount = comboAllies,
                    pushDirection = (pushDx, pushDy),
                    predictsBumpCollision = predictsBump,
                    cantileverOverhangRatio = 0.45f,
                    headlineBannerText = FormatArchetypeHeadline(arch, dmgPercent, counterPercent, angle, comboAllies, predictsBump)
                });
            }

            ActiveTelegraphFeed.Clear();
            ActiveTelegraphFeed.AddRange(suite);
            return suite;
        }

        private int CountLinkedComboAllies(int targetX, int targetY, int attackerOwner, int excludeX, int excludeY)
        {
            int count = 0;
            (int dx, int dy)[] dirs = { (0, 1), (0, -1), (-1, 0), (1, 0) };
            foreach (var (dx, dy) in dirs)
            {
                int nx = targetX + dx, ny = targetY + dy;
                if (nx == excludeX && ny == excludeY) continue;
                if (!BreachEngine.InBounds(nx, ny)) continue;
                var st = BreachEngine.stacks[nx, ny];
                if (!st.IsEmpty && st.TopCard.ownerId == attackerOwner)
                {
                    count++;
                }
            }
            return count;
        }

        private static List<(int x, int y)> BuildOrthogonalPathWaypoints(int sx, int sy, int tx, int ty)
        {
            var path = new List<(int x, int y)> { (sx, sy) };
            int cx = sx, cy = sy;
            while (cx != tx)
            {
                cx += Math.Sign(tx - cx);
                path.Add((cx, cy));
            }
            while (cy != ty)
            {
                cy += Math.Sign(ty - cy);
                path.Add((cx, cy));
            }
            return path;
        }

        private static string FormatArchetypeHeadline(
            TelegraphArchetype arch,
            int dmgPercent,
            int counterPercent,
            FacingAttackAngle angle,
            int comboAllies,
            bool bumpCollision) => arch switch
        {
            TelegraphArchetype.AdvanceWars_SegmentedPathArrow =>
                "AW PATH ARROW: Modular 16x16 Red Vector Locked",
            TelegraphArchetype.AdvanceWars_CrosshairDamageForecast =>
                $"AW FORECAST: DAMAGE {dmgPercent}% | COUNTER {counterPercent}%",
            TelegraphArchetype.AdvanceWars_SplitScreenBattleCutIn =>
                $"AW CUT-IN: Split-Screen Squad Volley ({dmgPercent}% Impact)",
            TelegraphArchetype.AdvanceWars_CoPowerBannerFlash =>
                "AW CO POWER: Eyes-Flash Speedline Groove (+10% ATK / +10% DEF)",
            TelegraphArchetype.Ffta_IsometricTileHighlightDiamond =>
                "FFTA ISO DIAMOND: Hardware Alpha-Blended Target Zone",
            TelegraphArchetype.Ffta_DirectionalFacingRing =>
                $"FFTA FACING: {angle} Strike ({GetFacingDamageMultiplier(angle):0.00}x DMG)",
            TelegraphArchetype.Ffta_MythrilComboLinkArcs =>
                $"FFTA MYTHRIL COMBO: {comboAllies} Linked Allies (+{comboAllies * 25}% Boost)",
            TelegraphArchetype.Ffta_JudgeLawCardBroadcast =>
                "FFTA JUDGE: Magisterium Law & JP Verdict Active",
            TelegraphArchetype.IntoTheBreach_TelegraphHazardStripes =>
                "ITB HAZARD: Deterministic Pre-Turn Telegraph Vector",
            TelegraphArchetype.IntoTheBreach_KineticPushBumpPreview =>
                bumpCollision ? "ITB PUSH: Kinetic Collision Bump (+1 DMG Both)" : "ITB PUSH: Unobstructed Displacement",
            TelegraphArchetype.Staccs_IsometricCubeGhostStack =>
                "STACCS CUBE GHOST: 3-Rhombus Z-Stack & Flank Reinforcement Preview",
            TelegraphArchetype.Staccs_CantileverOverhangShearArc =>
                "STACCS CANTILEVER: 45% Overhang Shadow & Rigidbody Clack Drop",
            _ => "TACTICAL TELEGRAPH"
        };
    }
}
