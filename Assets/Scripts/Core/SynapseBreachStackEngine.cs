using System;
using System.Collections.Generic;
using System.Linq;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Categories of 100% deterministic pre-turn telegraphed threats decompiled from
    /// Subset Games' Into the Breach (QueuedAttack, SpaceDamage, VekSpawn, Airstrike, SeismicCrack).
    /// </summary>
    public enum TelegraphedIntentKind
    {
        EnemyDirectionalStrike, // Unit-originating directional strike; shifts dynamically if source stack is pushed
        VekBurrowEruption,      // Subterranean emergence at target (x, y); blocked if a stack occupies the tile (deals 1 bump damage)
        OrbitalAirstrike,       // Fixed-coordinate heavy bombardment; destroys top layer or deducts 2 Power Grid bars
        SeismicTileCrack,       // Cracks target tile (or collapses an already-cracked tile into an open chasm)
        TidalPushWave           // Environmental directional wave that pushes target stack along pushDirection
    }

    /// <summary>
    /// Represents a 100% deterministic pre-turn telegraphed action on the tactical board.
    /// Models Into the Breach's QueuedAttack + SpaceDamage(loc, iDamage, iPush).
    /// </summary>
    [Serializable]
    public class TelegraphedTileIntent
    {
        public string intentId;
        public TelegraphedIntentKind kind;
        public int sourceX;
        public int sourceY;
        public int targetX;
        public int targetY;
        public int dx;
        public int dy;
        public int damage;
        public (int dx, int dy) pushDirection;
        public bool resolved;

        public int pushDx => pushDirection.dx;
        public int pushDy => pushDirection.dy;
        public bool HasSourceTile => sourceX >= 0 && sourceY >= 0;
        public bool HasPush => pushDirection.dx != 0 || pushDirection.dy != 0;

        public TelegraphedTileIntent() { }

        public TelegraphedTileIntent(
            TelegraphedIntentKind kind,
            int sourceX,
            int sourceY,
            int targetX,
            int targetY,
            int dx,
            int dy,
            int damage,
            (int dx, int dy) pushDirection,
            string intentId = null)
        {
            this.intentId = string.IsNullOrEmpty(intentId) ? Guid.NewGuid().ToString("N") : intentId;
            this.kind = kind;
            this.sourceX = sourceX;
            this.sourceY = sourceY;
            this.targetX = targetX;
            this.targetY = targetY;
            this.dx = dx;
            this.dy = dy;
            this.damage = damage;
            this.pushDirection = pushDirection;
            this.resolved = false;
        }

        public TelegraphedTileIntent Clone()
        {
            return new TelegraphedTileIntent(
                kind, sourceX, sourceY, targetX, targetY, dx, dy, damage, pushDirection, intentId)
            {
                resolved = this.resolved
            };
        }
    }

    /// <summary>
    /// STACCS 3-Rhombus Isometric Cube Projection & Cantilever Overhang animation pose
    /// (Top Crown Rhombus, Left Flank Rhombus, Right Flank Rhombus + Z-stack elevation).
    /// </summary>
    [Serializable]
    public struct IsometricCubeProjection
    {
        public float isoX;
        public float isoY;
        public float elevationZ;
        public float cantileverOffsetX;
        public float cantileverOffsetY;
        public int topCrownAttackUp;
        public int topCrownAttackDown;
        public int leftRhombusFlankDefense;
        public int rightRhombusFlankDefense;
    }

    /// <summary>
    /// Represents a 3D isometric hexagonal cube-card stack on board cell (x, y) combining
    /// STACCS vertical Z-stacking (layers Z = 0..N-1) with Into the Breach terrain & Power Grid state.
    /// </summary>
    [Serializable]
    public class IsometricCardStack
    {
        public int x;
        public int y;
        public List<RuntimeCard> layers = new List<RuntimeCard>();
        public bool isPowerGridBuilding = false;
        public int buildingPowerBars = 0;
        public bool isCrackedTile = false;
        public bool isChasmTile = false;

        /// <summary>
        /// Topmost Crown card (Z = N - 1) governing active SpecialAbility, ownerId, and primary directional stats.
        /// </summary>
        public RuntimeCard TopCard => layers.Count > 0 ? layers[layers.Count - 1] : null;

        /// <summary>
        /// Total vertical Z-layers in this stack (N).
        /// </summary>
        public int StackHeight => layers.Count;

        /// <summary>
        /// Number of supporting lower layers (Z = 0..N-2) beneath the Crown card.
        /// Each lower layer contributes +1 to exposed Left and Right flank defense.
        /// </summary>
        public int SubLayerCount => layers.Count > 1 ? layers.Count - 1 : 0;

        /// <summary>
        /// Exposed Left-Rhombus flank defense bonus from underlying cube layers (+1 per lower layer).
        /// </summary>
        public int LeftFlankReinforcement => SubLayerCount;

        /// <summary>
        /// Exposed Right-Rhombus flank defense bonus from underlying cube layers (+1 per lower layer).
        /// </summary>
        public int RightFlankReinforcement => SubLayerCount;

        public bool IsEmpty => layers.Count == 0;

        public IsometricCardStack(int x, int y)
        {
            this.x = x;
            this.y = y;
        }

        /// <summary>
        /// Pushes a card onto the top of the 3D isometric stack (Z = layers.Count).
        /// Cannot stack onto an open chasm tile.
        /// </summary>
        public bool PushLayer(RuntimeCard card)
        {
            if (card == null || isChasmTile) return false;
            card.currentZone = ZoneType.Board;
            layers.Add(card);
            return true;
        }

        /// <summary>
        /// Shears and removes the topmost Crown card (Z = N - 1) from the stack,
        /// exposing the underlying layer (Z = N - 2) as the new TopCard.
        /// </summary>
        public RuntimeCard PopTopLayer()
        {
            if (layers.Count == 0) return null;
            int topIdx = layers.Count - 1;
            var top = layers[topIdx];
            layers.RemoveAt(topIdx);
            return top;
        }

        /// <summary>
        /// Computes the STACCS 3-rhombus isometric cube projection and cantilever overhang pose
        /// for a given layer index Z during idle or battle overhang animation toward (targetDx, targetDy).
        /// </summary>
        public IsometricCubeProjection ComputeIsometricProjection(
            int layerZ,
            DirectionalStats effectiveCrownStats,
            int targetDx = 0,
            int targetDy = 0,
            float cantileverProgress01 = 0f,
            float tileWidth = 2.0f,
            float tileHeight = 1.0f,
            float layerThickness = 0.35f)
        {
            int clampedZ = Math.Max(0, Math.Min(layerZ, Math.Max(0, layers.Count - 1)));
            float isoX = (x - y) * (tileWidth * 0.5f);
            float isoY = (x + y) * (tileHeight * 0.5f) + (clampedZ * layerThickness);

            // STACCS cantilever overhang: top layer slides 45% toward target cell before dropping
            bool isTopLayer = (clampedZ == layers.Count - 1);
            float overhangFactor = isTopLayer ? Math.Max(0f, Math.Min(1f, cantileverProgress01)) * 0.45f : 0f;
            float cantX = (targetDx - targetDy) * (tileWidth * 0.5f) * overhangFactor;
            float cantY = (targetDx + targetDy) * (tileHeight * 0.5f) * overhangFactor;

            return new IsometricCubeProjection
            {
                isoX = isoX,
                isoY = isoY,
                elevationZ = clampedZ * layerThickness + (overhangFactor > 0f ? layerThickness * 0.5f : 0f),
                cantileverOffsetX = cantX,
                cantileverOffsetY = cantY,
                topCrownAttackUp = effectiveCrownStats.up,
                topCrownAttackDown = effectiveCrownStats.down,
                leftRhombusFlankDefense = effectiveCrownStats.left,
                rightRhombusFlankDefense = effectiveCrownStats.right
            };
        }

        public IsometricCardStack Clone()
        {
            var copy = new IsometricCardStack(x, y)
            {
                isPowerGridBuilding = isPowerGridBuilding,
                buildingPowerBars = buildingPowerBars,
                isCrackedTile = isCrackedTile,
                isChasmTile = isChasmTile
            };
            foreach (var c in layers)
            {
                copy.layers.Add(c.Clone());
            }
            return copy;
        }
    }

    /// <summary>
    /// Snapshot of a single surviving Pilot card evacuated across an Into the Breach Time-Breach pod.
    /// </summary>
    [Serializable]
    public struct TimeBreachSurvivorRecord
    {
        public int playerId;
        public string pilotCardUid;
        public string evolvedCardId;
        public int preservedPilotXp;
        public int preservedPermanentStatBonus;
        public int preservedMatchesPlayedCount;
        public int timelineBreachGeneration;
        public int newTimelineSeed;
    }

    /// <summary>
    /// Clean-Room Into the Breach + STACCS 3D Isometric Card-Stacking Engine for Synapse.TcgEngine.Core.
    /// Extends TcgGameLogic with:
    /// 1. 3D Isometric Z-Stacking (IsometricCardStack per cell, +1 Left/Right flank defense per lower layer,
    ///    TopCard governing active SpecialAbility and primary stats, and cantilever overhang projection).
    /// 2. 100% Deterministic Pre-Turn Telegraphs (QueueTelegraphedIntent & ResolveAllTelegraphedIntents).
    /// 3. Into the Breach Push & Bump-Collision Physics (PushStack with tall-stack top-layer shearing,
    ///    mutual bump collision damage, Power Grid building defense, cracked/chasm tile collapse, and
    ///    dynamic origin/target shifting of queued telegraphed intents).
    /// 4. Time-Breach Single-Survivor Pilot Carryover (TriggerTimeBreach preserving XP, permanentStatBonus,
    ///    matchesPlayedCount, and evolved cardId across timeline resets).
    /// </summary>
    public class SynapseBreachStackEngine : TcgGameLogic
    {
        public const int DefaultMaxPowerGrid = 7;
        public const int BumpCollisionStatPenalty = 1;
        public const int MinSurvivableStatSum = 4;

        public IsometricCardStack[,] stacks = new IsometricCardStack[GridWidth, GridHeight];
        public List<TelegraphedTileIntent> telegraphedIntents = new List<TelegraphedTileIntent>();

        public int powerGridPool = DefaultMaxPowerGrid;
        public int maxPowerGridPool = DefaultMaxPowerGrid;
        public int currentTimelineSeed = 1337;
        public int timelineBreachCount = 0;
        public TimeBreachSurvivorRecord? lastBreachSurvivor = null;

        private static readonly (int dx, int dy)[] BreachOrthogonalDirs = new[]
        {
            (0, 1),  // Up
            (0, -1), // Down
            (-1, 0), // Left
            (1, 0)   // Right
        };

        public SynapseBreachStackEngine(int seed = 1337, bool isNighttime = false)
            : base(seed, isNighttime)
        {
            currentTimelineSeed = seed;
            InitializeStacks();
        }

        private void InitializeStacks()
        {
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    stacks[x, y] = new IsometricCardStack(x, y);
                    if (grid[x, y]?.occupant != null)
                    {
                        stacks[x, y].PushLayer(grid[x, y].occupant);
                    }
                }
            }
        }

        /// <summary>
        /// Synchronizes the base TcgGameLogic.grid[x, y].occupant pointer with each stack's TopCard
        /// so all inherited TcgGameLogic and SynapseJudgeLawEngine methods seamlessly see the Crown card.
        /// </summary>
        public void SyncGridOccupantsFromStacks()
        {
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    if (stacks[x, y].isChasmTile)
                    {
                        stacks[x, y].layers.Clear();
                        stacks[x, y].isPowerGridBuilding = false;
                        stacks[x, y].buildingPowerBars = 0;
                    }
                    grid[x, y].occupant = stacks[x, y].TopCard;
                }
            }
        }

        /// <summary>
        /// Configures a board cell as an Into the Breach Civilian Power Grid Building.
        /// </summary>
        public bool ConfigurePowerGridBuilding(int x, int y, int powerBars = 2)
        {
            if (!InBounds(x, y) || stacks[x, y].isChasmTile || powerBars <= 0) return false;
            stacks[x, y].isPowerGridBuilding = true;
            stacks[x, y].buildingPowerBars = powerBars;
            return true;
        }

        /// <summary>
        /// Computes the effective directional stats for the 3D Isometric Card Stack at (x, y).
        /// - The topmost Crown card (TopCard) governs primary directional stats, themes, and SpecialAbility.
        /// - Each lower cube layer (Z = 0..N-2) contributes +1 to exposed Left and Right flank defense.
        /// </summary>
        public DirectionalStats GetStackEffectiveStats(int x, int y)
        {
            if (!InBounds(x, y)) return default;
            SyncGridOccupantsFromStacks();
            var stack = stacks[x, y];
            if (stack.IsEmpty) return default;

            var crownStats = base.GetEffectiveStats(x, y);
            int flankBonus = stack.SubLayerCount;
            if (flankBonus > 0)
            {
                crownStats = new DirectionalStats(
                    crownStats.up,
                    crownStats.down,
                    crownStats.left + flankBonus,
                    crownStats.right + flankBonus);
            }
            return crownStats;
        }

        /// <summary>
        /// Stacks or deploys a card from a player's hand onto isometric board cell (x, y) at layer Z = N.
        /// Supports placing onto an empty tile or vertically stacking onto an existing friendly stack.
        /// Resolves orthogonal captures using the new Crown card (TopCard) and reinforced Left/Right flanks.
        /// </summary>
        public bool StackCardFromHand(int playerId, string cardUid, int x, int y, out int capturedCount)
        {
            capturedCount = 0;
            if (winnerId.HasValue || playerId != activePlayerId || phase != TurnPhase.Main) return false;
            if (!InBounds(x, y)) return false;

            var stack = stacks[x, y];
            if (stack.isChasmTile || stack.isPowerGridBuilding) return false;

            // Can deploy onto an empty tile or vertically stack atop a friendly stack
            if (!stack.IsEmpty && stack.TopCard.ownerId != playerId) return false;

            var p = players[playerId];
            var card = p.hand.Find(c => c.uid == cardUid);
            if (card == null) return false;

            p.hand.Remove(card);
            card.currentZone = ZoneType.Board;
            card.ownerId = playerId;
            card.matchesPlayedCount++;

            stack.PushLayer(card);
            grid[x, y].occupant = stack.TopCard;

            capturedCount = ResolveStackCapturesFrom(x, y, playerId);

            if (card.specialAbility == SpecialAbilityType.Charge && capturedCount > 0 && HasEmptyCell() && p.hand.Count > 0)
            {
                bonusMovePlayerId = playerId;
            }
            else
            {
                bonusMovePlayerId = null;
                EndTurn();
            }

            return true;
        }

        /// <summary>
        /// Resolves directional captures around (x, y) using STACCS 3D stack flank reinforcement.
        /// </summary>
        public int ResolveStackCapturesFrom(int x, int y, int attackerPlayerId)
        {
            SyncGridOccupantsFromStacks();
            var attackerStack = stacks[x, y];
            var attackerCard = attackerStack.TopCard;
            if (attackerCard == null) return 0;

            var attackerStats = GetStackEffectiveStats(x, y);
            int captures = 0;

            foreach (var (dx, dy) in BreachOrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!InBounds(nx, ny)) continue;

                var defenderStack = stacks[nx, ny];
                if (defenderStack.IsEmpty) continue;

                var defenderCard = defenderStack.TopCard;
                if (defenderCard.ownerId == attackerPlayerId) continue;
                if (IsCardCaptureImmune(nx, ny)) continue;

                var defenderStats = GetStackEffectiveStats(nx, ny);
                int atkVal = 0, defVal = 0;

                if (dx == 0 && dy == 1)       { atkVal = attackerStats.up;    defVal = defenderStats.down; }
                else if (dx == 0 && dy == -1) { atkVal = attackerStats.down;  defVal = defenderStats.up; }
                else if (dx == -1 && dy == 0) { atkVal = attackerStats.left;  defVal = defenderStats.right; }
                else if (dx == 1 && dy == 0)  { atkVal = attackerStats.right; defVal = defenderStats.left; }

                if (atkVal > defVal)
                {
                    captures++;
                    if (defenderCard.specialAbility == SpecialAbilityType.Rebirth && !defenderCard.oncePerGameAbilityUsed)
                    {
                        defenderCard.oncePerGameAbilityUsed = true;
                        defenderStack.PopTopLayer();
                        grid[nx, ny].occupant = defenderStack.TopCard;
                        defenderCard.ownerId = defenderCard.originalOwnerId;
                        defenderCard.currentZone = ZoneType.Hand;
                        players[defenderCard.originalOwnerId].hand.Add(defenderCard);
                    }
                    else
                    {
                        defenderCard.ownerId = attackerPlayerId;
                        if (attackerCard.specialAbility == SpecialAbilityType.ElementalBurst && !attackerCard.oncePerGameAbilityUsed)
                        {
                            attackerCard.oncePerGameAbilityUsed = true;
                            (attackerCard.baseStats, defenderCard.baseStats) = (defenderCard.baseStats, attackerCard.baseStats);
                        }
                    }
                }
            }

            players[attackerPlayerId].confidencePoints += captures * 10;
            SyncGridOccupantsFromStacks();
            return captures;
        }

        // =========================================================================================
        // 1. DETERMINISTIC PRE-TURN TELEGRAPHS (Into the Breach QueuedAttack & Hazard Intents)
        // =========================================================================================

        /// <summary>
        /// Queues a 100% deterministic pre-turn telegraphed intent onto the board.
        /// Players can inspect all queued intents before acting and counterplay via PushStack.
        /// </summary>
        public TelegraphedTileIntent QueueTelegraphedIntent(
            TelegraphedIntentKind kind,
            int sourceX,
            int sourceY,
            int targetX,
            int targetY,
            int damage = 1,
            int pushDx = 0,
            int pushDy = 0,
            string intentId = null)
        {
            int dirX = Math.Sign(targetX - sourceX);
            int dirY = Math.Sign(targetY - sourceY);
            var intent = new TelegraphedTileIntent(
                kind,
                sourceX,
                sourceY,
                targetX,
                targetY,
                dirX,
                dirY,
                damage,
                (pushDx, pushDy),
                intentId);

            telegraphedIntents.Add(intent);
            return intent;
        }

        /// <summary>
        /// Overload accepting a pre-constructed TelegraphedTileIntent.
        /// </summary>
        public TelegraphedTileIntent QueueTelegraphedIntent(TelegraphedTileIntent intent)
        {
            if (intent == null) return null;
            telegraphedIntents.Add(intent);
            return intent;
        }

        /// <summary>
        /// Resolves all queued, unresolved telegraphed intents in strict FIFO deterministic order.
        /// Returns the number of intents that successfully executed on the board.
        /// </summary>
        public int ResolveAllTelegraphedIntents()
        {
            SyncGridOccupantsFromStacks();
            int resolvedCount = 0;

            for (int i = 0; i < telegraphedIntents.Count; i++)
            {
                var intent = telegraphedIntents[i];
                if (intent == null || intent.resolved) continue;

                intent.resolved = true;
                resolvedCount++;

                // For EnemyDirectionalStrike, verify the source tile is still in-bounds and has an active unit
                if (intent.kind == TelegraphedIntentKind.EnemyDirectionalStrike)
                {
                    if (!InBounds(intent.sourceX, intent.sourceY) || stacks[intent.sourceX, intent.sourceY].IsEmpty)
                    {
                        // Source attacker was destroyed or pushed into a chasm — attack canceled!
                        continue;
                    }
                }

                if (!InBounds(intent.targetX, intent.targetY))
                {
                    // Attack was redirected off the board via PushStack — harmlessly misses!
                    continue;
                }

                var targetStack = stacks[intent.targetX, intent.targetY];

                switch (intent.kind)
                {
                    case TelegraphedIntentKind.EnemyDirectionalStrike:
                    case TelegraphedIntentKind.OrbitalAirstrike:
                        if (intent.damage > 0)
                        {
                            ApplyDamageToCell(intent.targetX, intent.targetY, intent.damage);
                        }
                        if (intent.HasPush && !targetStack.IsEmpty)
                        {
                            PushStack(intent.targetX, intent.targetY, intent.pushDx, intent.pushDy, out _);
                        }
                        break;

                    case TelegraphedIntentKind.VekBurrowEruption:
                        if (!targetStack.IsEmpty || targetStack.isPowerGridBuilding)
                        {
                            // Blocking a Vek spawn prevents emergence at the cost of 1 bump damage to the blocker
                            ApplyDamageToCell(intent.targetX, intent.targetY, Math.Max(1, intent.damage));
                        }
                        else if (!targetStack.isChasmTile)
                        {
                            // Unblocked burrow spawns a hostile Vek Bio-Construct layer owned by player 1
                            var spawnedVek = new RuntimeCard
                            {
                                uid = "vek_" + intent.intentId,
                                cardId = "itb_vek_scarab",
                                title = "Burrowing Vek Scarab",
                                codeName = "Hive Eruption",
                                ownerId = 1,
                                originalOwnerId = 1,
                                baseStats = new DirectionalStats(5, 5, 5, 5),
                                themes = CardTheme.Nature | CardTheme.Shadow,
                                specialAbility = SpecialAbilityType.None,
                                currentZone = ZoneType.Board
                            };
                            targetStack.PushLayer(spawnedVek);
                        }
                        break;

                    case TelegraphedIntentKind.SeismicTileCrack:
                        if (intent.damage > 0)
                        {
                            ApplyDamageToCell(intent.targetX, intent.targetY, intent.damage);
                        }
                        CrackOrCollapseTile(intent.targetX, intent.targetY);
                        break;

                    case TelegraphedIntentKind.TidalPushWave:
                        if (intent.damage > 0)
                        {
                            ApplyDamageToCell(intent.targetX, intent.targetY, intent.damage);
                        }
                        if (intent.HasPush)
                        {
                            PushStack(intent.targetX, intent.targetY, intent.pushDx, intent.pushDy, out _);
                        }
                        break;
                }
            }

            SyncGridOccupantsFromStacks();
            return resolvedCount;
        }

        // =========================================================================================
        // 2. INTO THE BREACH PUSH & BUMP-COLLISION PHYSICS + STACCS STACK SHEARING
        // =========================================================================================

        /// <summary>
        /// Displaces a card stack (or shears the topmost Crown layer of a tall stack with height > 1)
        /// from (fromX, fromY) along (dx, dy) into (fromX + dx, fromY + dy).
        /// - If the destination is out-of-bounds or occupied (by another stack or Power Grid building),
        ///   sets collisionOccurred = true and applies Bump/Collision Damage to both cells!
        /// - If the destination is unobstructed, moves the sheared/displaced card(s) into (destX, destY)
        ///   and dynamically shifts any unresolved TelegraphedTileIntent originating from (fromX, fromY)
        ///   to its new coordinates!
        /// </summary>
        public bool PushStack(int fromX, int fromY, int dx, int dy, out bool collisionOccurred)
        {
            collisionOccurred = false;
            SyncGridOccupantsFromStacks();

            if (!InBounds(fromX, fromY) || (dx == 0 && dy == 0)) return false;

            var srcStack = stacks[fromX, fromY];
            if (srcStack.IsEmpty) return false;

            int destX = fromX + dx;
            int destY = fromY + dy;

            // Case 1: Pushed out-of-bounds against the board perimeter wall -> Bump Collision!
            if (!InBounds(destX, destY))
            {
                collisionOccurred = true;
                ApplyDamageToCell(fromX, fromY, BumpCollisionStatPenalty);
                SyncGridOccupantsFromStacks();
                return true;
            }

            var dstStack = stacks[destX, destY];

            // Case 2: Destination is occupied by another card stack or a civilian Power Grid building -> Bump Collision!
            if (!dstStack.IsEmpty || dstStack.isPowerGridBuilding)
            {
                collisionOccurred = true;
                ApplyDamageToCell(fromX, fromY, BumpCollisionStatPenalty);
                ApplyDamageToCell(destX, destY, BumpCollisionStatPenalty);
                SyncGridOccupantsFromStacks();
                return true;
            }

            // Case 3: Unobstructed displacement (or into an open chasm tile)
            // If stack has multiple layers (Z > 1), shear the top Crown layer into dest; otherwise slide the stack.
            var displacedCard = srcStack.PopTopLayer();
            displacedCard.movedThisTurn = true;

            // Shift any unresolved TelegraphedTileIntent originating from (fromX, fromY) to (destX, destY)
            ShiftTelegraphedIntentsFromOrigin(fromX, fromY, dx, dy);

            if (dstStack.isChasmTile)
            {
                // Non-flying unit pushed into an open chasm falls to its destruction
                if (displacedCard.ownerId >= 0 && displacedCard.ownerId < players.Length)
                {
                    displacedCard.currentZone = ZoneType.Discard;
                    players[displacedCard.ownerId].discard.Add(displacedCard);
                }
            }
            else
            {
                dstStack.PushLayer(displacedCard);
            }

            SyncGridOccupantsFromStacks();
            return true;
        }

        /// <summary>
        /// Dynamically shifts the origin and target coordinates of any unresolved TelegraphedTileIntent
        /// originating at (fromX, fromY) by (dx, dy) when its source stack is pushed.
        /// </summary>
        public int ShiftTelegraphedIntentsFromOrigin(int fromX, int fromY, int dx, int dy)
        {
            int shifted = 0;
            for (int i = 0; i < telegraphedIntents.Count; i++)
            {
                var intent = telegraphedIntents[i];
                if (intent == null || intent.resolved) continue;

                if (intent.sourceX == fromX && intent.sourceY == fromY)
                {
                    intent.sourceX += dx;
                    intent.sourceY += dy;
                    intent.targetX += dx;
                    intent.targetY += dy;
                    shifted++;
                }
            }
            return shifted;
        }

        /// <summary>
        /// Applies Into the Breach SpaceDamage / Bump Damage to board cell (x, y):
        /// - If the cell is a Civilian Power Grid Building, deducts from buildingPowerBars and powerGridPool.
        /// - If the cell holds an IsometricCardStack, reduces TopCard.permanentStatBonus by damage;
        ///   if TopCard's total effective directional stats drop below MinSurvivableStatSum (or if damage >= 2
        ///   on a multi-layer stack), ablatively peels/destroys TopCard to expose the layer below.
        /// - If the tile is already cracked (isCrackedTile), impact shatters it into an open chasm (isChasmTile).
        /// </summary>
        public void ApplyDamageToCell(int x, int y, int damage)
        {
            if (!InBounds(x, y) || damage <= 0) return;
            var stack = stacks[x, y];

            // 1. Power Grid Building damage
            if (stack.isPowerGridBuilding && stack.buildingPowerBars > 0)
            {
                int gridLoss = Math.Min(stack.buildingPowerBars, damage);
                stack.buildingPowerBars -= gridLoss;
                powerGridPool = Math.Max(0, powerGridPool - gridLoss);
                if (stack.buildingPowerBars <= 0)
                {
                    stack.isPowerGridBuilding = false;
                }
                if (powerGridPool <= 0)
                {
                    phase = TurnPhase.GameOver;
                    winnerId = 1; // Timeline lost to Vek / Grid failure
                }
            }

            // 2. Isometric Card Stack damage (ablative Crown layer impact)
            if (!stack.IsEmpty)
            {
                var top = stack.TopCard;
                top.permanentStatBonus -= damage;

                var eff = top.baseStats.AddAll(top.permanentStatBonus);
                int statSum = eff.up + eff.down + eff.left + eff.right;

                // Peel/destroy top layer if lethal stat degradation or heavy multi-damage impact on tall stack
                if (statSum < MinSurvivableStatSum || (damage >= 2 && stack.StackHeight > 1))
                {
                    var destroyed = stack.PopTopLayer();
                    if (destroyed != null && destroyed.ownerId >= 0 && destroyed.ownerId < players.Length)
                    {
                        destroyed.currentZone = ZoneType.Discard;
                        players[destroyed.ownerId].discard.Add(destroyed);
                    }
                }
            }

            // 3. Cracked tile shatters into a chasm on subsequent damage/bump impact
            if (stack.isCrackedTile && !stack.isChasmTile)
            {
                CollapseTileToChasm(x, y);
            }

            SyncGridOccupantsFromStacks();
        }

        /// <summary>
        /// Cracks an intact tile, or collapses an already-cracked tile into an open chasm.
        /// </summary>
        public void CrackOrCollapseTile(int x, int y)
        {
            if (!InBounds(x, y)) return;
            var stack = stacks[x, y];
            if (stack.isChasmTile) return;

            if (!stack.isCrackedTile)
            {
                stack.isCrackedTile = true;
            }
            else
            {
                CollapseTileToChasm(x, y);
            }
        }

        private void CollapseTileToChasm(int x, int y)
        {
            var stack = stacks[x, y];
            stack.isCrackedTile = false;
            stack.isChasmTile = true;

            if (stack.isPowerGridBuilding && stack.buildingPowerBars > 0)
            {
                powerGridPool = Math.Max(0, powerGridPool - stack.buildingPowerBars);
                stack.buildingPowerBars = 0;
                stack.isPowerGridBuilding = false;
            }

            while (!stack.IsEmpty)
            {
                var fallen = stack.PopTopLayer();
                if (fallen != null && fallen.ownerId >= 0 && fallen.ownerId < players.Length)
                {
                    fallen.currentZone = ZoneType.Discard;
                    players[fallen.ownerId].discard.Add(fallen);
                }
            }

            grid[x, y].occupant = null;
        }

        // =========================================================================================
        // 3. TIME-BREACH SINGLE-SURVIVOR PILOT TIMELINE CARRYOVER
        // =========================================================================================

        /// <summary>
        /// Activates an Into the Breach emergency Time Pod ("TriggerTimeBreach"), resetting the board,
        /// telegraphed intents, and Power Grid for a new timeline seeded with newTimelineSeed while
        /// evacuating and preserving a single surviving Pilot card's XP, permanentStatBonus,
        /// matchesPlayedCount, and evolved cardId into the new timeline's opening hand.
        /// </summary>
        public bool TriggerTimeBreach(int playerId, string survivingPilotCardUid, int newTimelineSeed)
        {
            if (playerId < 0 || playerId >= players.Length || string.IsNullOrEmpty(survivingPilotCardUid))
                return false;

            SyncGridOccupantsFromStacks();

            // Locate the surviving Pilot card across the board stacks, hand, deck, or discard
            RuntimeCard pilotCard = FindPilotCardEverywhere(playerId, survivingPilotCardUid);
            if (pilotCard == null) return false;

            // Preserve Pilot veteran progression & apply evolution if available
            int preservedPlayerXp = Math.Max(players[playerId].xp, 50) + 25;
            int preservedStatBonus = Math.Max(1, pilotCard.permanentStatBonus + 1);
            int preservedMatches = Math.Max(1, pilotCard.matchesPlayedCount);
            string evolvedId = !string.IsNullOrEmpty(pilotCard.evolvesToCardId)
                ? pilotCard.evolvesToCardId
                : pilotCard.cardId;

            pilotCard.cardId = evolvedId;
            pilotCard.permanentStatBonus = preservedStatBonus;
            pilotCard.matchesPlayedCount = preservedMatches;
            pilotCard.oncePerGameAbilityUsed = false;
            pilotCard.movedThisTurn = false;
            pilotCard.vanishImmuneTurns = 0;
            pilotCard.temporalRiftReversedTurns = 0;
            pilotCard.ownerId = playerId;
            pilotCard.originalOwnerId = playerId;

            // Reset all board cells & 3D isometric stacks, returning non-pilot cards to their original owners' decks
            var allRecoveredCards = new List<RuntimeCard>[2]
            {
                new List<RuntimeCard>(),
                new List<RuntimeCard>()
            };

            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var st = stacks[x, y];
                    foreach (var layerCard in st.layers)
                    {
                        if (layerCard.uid == pilotCard.uid) continue;
                        ResetCardForNewTimeline(layerCard);
                        allRecoveredCards[layerCard.originalOwnerId].Add(layerCard);
                    }
                    stacks[x, y] = new IsometricCardStack(x, y);
                    grid[x, y].occupant = null;
                }
            }

            for (int p = 0; p < 2; p++)
            {
                foreach (var c in players[p].hand.Concat(players[p].deck).Concat(players[p].discard))
                {
                    if (c.uid == pilotCard.uid) continue;
                    ResetCardForNewTimeline(c);
                    if (!allRecoveredCards[c.originalOwnerId].Exists(existing => existing.uid == c.uid))
                    {
                        allRecoveredCards[c.originalOwnerId].Add(c);
                    }
                }

                players[p].hand.Clear();
                players[p].deck.Clear();
                players[p].discard.Clear();
                players[p].deck.AddRange(allRecoveredCards[p]);
            }

            // Re-seed deterministic timeline state
            currentTimelineSeed = newTimelineSeed;
            timelineBreachCount++;
            powerGridPool = maxPowerGridPool;
            telegraphedIntents.Clear();
            turnNumber = 1;
            activePlayerId = playerId;
            bonusMovePlayerId = null;
            winnerId = null;
            phase = TurnPhase.Main;

            // Deterministic shuffle of both players' decks using newTimelineSeed
            var breachRng = new System.Random(newTimelineSeed);
            for (int p = 0; p < 2; p++)
            {
                var deck = players[p].deck;
                for (int i = deck.Count - 1; i > 0; i--)
                {
                    int j = breachRng.Next(0, i + 1);
                    (deck[i], deck[j]) = (deck[j], deck[i]);
                }
            }

            // Place the surviving Time-Breach Pilot card directly into the player's opening hand!
            pilotCard.currentZone = ZoneType.Hand;
            players[playerId].hand.Add(pilotCard);
            players[playerId].xp = preservedPlayerXp;
            players[playerId].badges.Add("Time Breach Survivor");

            lastBreachSurvivor = new TimeBreachSurvivorRecord
            {
                playerId = playerId,
                pilotCardUid = pilotCard.uid,
                evolvedCardId = pilotCard.cardId,
                preservedPilotXp = preservedPlayerXp,
                preservedPermanentStatBonus = pilotCard.permanentStatBonus,
                preservedMatchesPlayedCount = pilotCard.matchesPlayedCount,
                timelineBreachGeneration = timelineBreachCount,
                newTimelineSeed = newTimelineSeed
            };

            SyncGridOccupantsFromStacks();
            return true;
        }

        private RuntimeCard FindPilotCardEverywhere(int playerId, string cardUid)
        {
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var foundOnBoard = stacks[x, y].layers.Find(c => c.uid == cardUid);
                    if (foundOnBoard != null) return foundOnBoard;
                }
            }

            var p = players[playerId];
            return p.hand.Find(c => c.uid == cardUid)
                ?? p.deck.Find(c => c.uid == cardUid)
                ?? p.discard.Find(c => c.uid == cardUid);
        }

        private static void ResetCardForNewTimeline(RuntimeCard card)
        {
            card.ownerId = card.originalOwnerId;
            card.currentZone = ZoneType.Deck;
            card.oncePerGameAbilityUsed = false;
            card.movedThisTurn = false;
            card.vanishImmuneTurns = 0;
            card.temporalRiftReversedTurns = 0;
            card.permanentStatBonus = 0;
        }
    }
}
