using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    public enum SynapseMctsActionType
    {
        Deploy = 0,
        Slide = 1,
        NudgeDie = 2
    }

    [Serializable]
    public sealed class SynapseMctsMoveRecommendation
    {
        public int rank;
        public SynapseMctsActionType actionType;
        public string actionLabel;
        public int handIndex;
        public int slotIndex;
        public int fromSlot;
        public int toSlot;
        public int columnIndex;
        public int visitCount;
        public float visitShare;
        public float qValue;
        public float priorProbability;
        public float winProbability;
        public string tacticalExplanation;
    }

    [Serializable]
    public sealed class SynapseAlphaZeroEvaluationResult
    {
        public float stateValue;
        public float winProbability;
        public int simulationsRun;
        public float cPuct;
        public float[] policyLogits;
        public List<SynapseMctsMoveRecommendation> topRecommendations = new List<SynapseMctsMoveRecommendation>();
    }

    [Serializable]
    public struct SynapseCardSnapshot
    {
        public string cardId;
        public string cardName;
        public int north;
        public int east;
        public int south;
        public int west;
        public int mgaCost;

        public SynapseCardSnapshot(string id, string name, int n, int e, int s, int w, int cost)
        {
            cardId = id ?? "cf_unit";
            cardName = name ?? "Unit";
            north = n;
            east = e;
            south = s;
            west = w;
            mgaCost = cost;
        }
    }

    [Serializable]
    public struct SynapseBoardSlotSnapshot
    {
        public bool isOccupied;
        public int ownerId; // 0 = Player, 1 = Enemy/Boss
        public SynapseCardSnapshot card;
    }

    /// <summary>
    /// Clean-room Unity 6 C# AlphaZero / MuZero Policy-Value Network and PUCT Monte Carlo Tree Search
    /// (`SynapseAlphaZeroPolicyNet`) for CARDFRONT 3D: Cradle of Echoes.
    /// Evaluates the 3x3 directional capture grid, 3 column dice, 1x tactical slide, and Shinta Nojiri MGA COST economy.
    /// </summary>
    public sealed class SynapseAlphaZeroPolicyNet
    {
        public const int StateDim = 96;
        public const int HiddenDim = 48;
        public const int ActionDim = 72;
        public const float DefaultCPuct = 1.414f;
        public const int DefaultSimulations = 64;

        private readonly float[,] _encoderW = new float[StateDim, HiddenDim];
        private readonly float[,] _policyHeadW = new float[HiddenDim, ActionDim];
        private readonly float[] _valueHeadW = new float[HiddenDim];

        private static readonly int[][] OrthogonalNeighbors = new int[][]
        {
            new int[] { 1, 3 },
            new int[] { 0, 2, 4 },
            new int[] { 1, 5 },
            new int[] { 0, 4, 6 },
            new int[] { 1, 3, 5, 7 },
            new int[] { 2, 4, 8 },
            new int[] { 3, 7 },
            new int[] { 4, 6, 8 },
            new int[] { 5, 7 }
        };

        private static readonly (int fromSlot, int toSlot)[] SlidePairs = BuildSlidePairs();

        private static (int fromSlot, int toSlot)[] BuildSlidePairs()
        {
            var list = new List<(int, int)>(24);
            for (int src = 0; src < 9; src++)
            {
                int[] neighbors = OrthogonalNeighbors[src];
                for (int i = 0; i < neighbors.Length; i++)
                {
                    list.Add((src, neighbors[i]));
                }
            }
            return list.ToArray();
        }

        public SynapseAlphaZeroPolicyNet(int seed = 20261109)
        {
            InitializeDeterministicWeights(seed);
        }

        public void InitializeDeterministicWeights(int seed)
        {
            uint state = (uint)seed;
            float encScale = 1.0f / Mathf.Sqrt(StateDim);
            float headScale = 1.0f / Mathf.Sqrt(HiddenDim);

            for (int i = 0; i < StateDim; i++)
            {
                for (int j = 0; j < HiddenDim; j++)
                {
                    _encoderW[i, j] = NextSignedFloat(ref state) * encScale;
                }
            }

            for (int j = 0; j < HiddenDim; j++)
            {
                for (int a = 0; a < ActionDim; a++)
                {
                    _policyHeadW[j, a] = NextSignedFloat(ref state) * headScale;
                }
                _valueHeadW[j] = NextSignedFloat(ref state) * headScale;
            }

            // Tactical residual inductive anchors matching Backend/synapse_alphazero_policy_value_net.py
            for (int j = 0; j < 8; j++)
            {
                _encoderW[90, j] += 0.45f; // Parity-adjusted capture differential
                _encoderW[88, j] += 0.25f; // MGA COST tempo advantage
                _encoderW[92, j] += 0.30f; // Center anchor control
                _valueHeadW[j] += 0.35f;
            }
        }

        private static float NextSignedFloat(ref uint state)
        {
            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            return ((state & 0xFFFF) / 32767.5f) - 1.0f;
        }

        /// <summary>
        /// Loads float32 tensors (`encoder_w`, `policy_head_w`, `value_head_w`) from a Safetensors checkpoint file.
        /// </summary>
        public bool LoadSafetensorsWeights(string safetensorsPath)
        {
            if (string.IsNullOrEmpty(safetensorsPath) || !File.Exists(safetensorsPath))
            {
                return false;
            }

            byte[] bytes = File.ReadAllBytes(safetensorsPath);
            if (bytes.Length < 16)
            {
                return false;
            }

            ulong headerLen = BitConverter.ToUInt64(bytes, 0);
            int payloadStart = 8 + (int)headerLen;
            if (payloadStart >= bytes.Length)
            {
                return false;
            }

            int expectedEncFloats = StateDim * HiddenDim;
            int expectedPolFloats = HiddenDim * ActionDim;
            int expectedValFloats = HiddenDim;
            int totalBytesNeeded = (expectedEncFloats + expectedPolFloats + expectedValFloats) * 4;

            if (bytes.Length - payloadStart < totalBytesNeeded)
            {
                return false;
            }

            int offset = payloadStart;
            for (int i = 0; i < StateDim; i++)
            {
                for (int j = 0; j < HiddenDim; j++)
                {
                    _encoderW[i, j] = BitConverter.ToSingle(bytes, offset);
                    offset += 4;
                }
            }

            for (int j = 0; j < HiddenDim; j++)
            {
                for (int a = 0; a < ActionDim; a++)
                {
                    _policyHeadW[j, a] = BitConverter.ToSingle(bytes, offset);
                    offset += 4;
                }
            }

            for (int j = 0; j < HiddenDim; j++)
            {
                _valueHeadW[j] = BitConverter.ToSingle(bytes, offset);
                offset += 4;
            }

            return true;
        }

        /// <summary>
        /// Encodes the 9 board slots, 3 column dice, 5 player hand cards, and MGA COST / slide availability into a 96-float feature vector.
        /// </summary>
        public float[] EncodeBoardState(
            SynapseBoardSlotSnapshot[] board,
            SynapseCardSnapshot[] hand,
            int[] columnDice,
            bool slideAvailable,
            int playerCost,
            int enemyCost,
            int turnNumber = 1,
            int perspectiveOwnerId = 0)
        {
            float[] features = new float[StateDim];
            int idx = 0;
            int friendlyCount = 0;
            int enemyCount = 0;
            int emptyCount = 0;

            for (int s = 0; s < 9; s++)
            {
                if (board != null && s < board.Length && board[s].isOccupied)
                {
                    bool isFriendly = board[s].ownerId == perspectiveOwnerId;
                    if (isFriendly) friendlyCount++;
                    else enemyCount++;

                    var c = board[s].card;
                    features[idx++] = isFriendly ? 1.0f : -1.0f;
                    features[idx++] = c.north / 10.0f;
                    features[idx++] = c.east / 10.0f;
                    features[idx++] = c.south / 10.0f;
                    features[idx++] = c.west / 10.0f;
                    features[idx++] = c.mgaCost / 12.0f;
                }
                else
                {
                    emptyCount++;
                    idx += 6;
                }
            }

            float diceSum = 0f;
            for (int col = 0; col < 3; col++)
            {
                int dVal = (columnDice != null && col < columnDice.Length) ? Mathf.Clamp(columnDice[col], 1, 6) : 3;
                diceSum += dVal;
                features[idx++] = dVal / 6.0f;
                features[idx++] = dVal >= 5 ? 1.0f : 0.0f;
            }

            for (int h = 0; h < 5; h++)
            {
                if (hand != null && h < hand.Length)
                {
                    var c = hand[h];
                    features[idx++] = c.north / 10.0f;
                    features[idx++] = c.east / 10.0f;
                    features[idx++] = c.south / 10.0f;
                    features[idx++] = c.west / 10.0f;
                    features[idx++] = c.mgaCost / 12.0f;
                }
                else
                {
                    idx += 5;
                }
            }

            float centerVal = 0f;
            if (board != null && board.Length > 4 && board[4].isOccupied)
            {
                centerVal = board[4].ownerId == perspectiveOwnerId ? 1.0f : -1.0f;
            }

            int[] corners = { 0, 2, 6, 8 };
            float cornerSum = 0f;
            for (int cIdx = 0; cIdx < corners.Length; cIdx++)
            {
                int slot = corners[cIdx];
                if (board != null && slot < board.Length && board[slot].isOccupied)
                {
                    cornerSum += board[slot].ownerId == perspectiveOwnerId ? 1.0f : -1.0f;
                }
            }

            float costAdv = Mathf.Clamp((enemyCost - playerCost) / 15.0f, -1.0f, 1.0f);
            float parityOffset = ((friendlyCount + enemyCount) % 2 == 1) ? -1.0f : 0.0f;

            features[idx++] = slideAvailable ? 1.0f : 0.0f;
            features[idx++] = 1.0f;
            features[idx++] = Mathf.Min(1.0f, playerCost / 30.0f);
            features[idx++] = Mathf.Min(1.0f, enemyCost / 30.0f);
            features[idx++] = costAdv;
            features[idx++] = Mathf.Min(1.0f, turnNumber / 10.0f);
            features[idx++] = ((friendlyCount - enemyCount) - parityOffset) / 9.0f;
            features[idx++] = emptyCount / 9.0f;
            features[idx++] = centerVal;
            features[idx++] = cornerSum / 4.0f;
            features[idx++] = diceSum / 18.0f;

            return features;
        }

        /// <summary>
        /// Evaluates a live `TcgGameLogic` instance using PUCT Monte Carlo Tree Search.
        /// </summary>
        public SynapseAlphaZeroEvaluationResult EvaluateBoardState(
            TcgGameLogic gameLogic,
            int[] columnDice = null,
            bool slideAvailable = true,
            int playerCost = 0,
            int enemyCost = 0,
            int numSimulations = DefaultSimulations,
            float cPuct = DefaultCPuct)
        {
            SynapseBoardSlotSnapshot[] board = new SynapseBoardSlotSnapshot[9];
            var handList = new List<SynapseCardSnapshot>();

            if (gameLogic != null)
            {
                for (int y = 0; y < 3; y++)
                {
                    for (int x = 0; x < 3; x++)
                    {
                        int slot = y * 3 + x;
                        var cell = gameLogic.grid[x, y];
                        if (cell != null && cell.occupant != null)
                        {
                            var occ = cell.occupant;
                            board[slot] = new SynapseBoardSlotSnapshot
                            {
                                isOccupied = true,
                                ownerId = occ.ownerId,
                                card = new SynapseCardSnapshot(
                                    occ.cardId,
                                    occ.title,
                                    occ.baseStats.up,
                                    occ.baseStats.right,
                                    occ.baseStats.down,
                                    occ.baseStats.left,
                                    5)
                            };
                        }
                    }
                }

                int activeId = gameLogic.activePlayerId;
                if (activeId >= 0 && activeId < gameLogic.players.Length)
                {
                    var pHand = gameLogic.players[activeId].hand;
                    for (int i = 0; i < Mathf.Min(5, pHand.Count); i++)
                    {
                        var c = pHand[i];
                        handList.Add(new SynapseCardSnapshot(
                            c.cardId,
                            c.title,
                            c.baseStats.up,
                            c.baseStats.right,
                            c.baseStats.down,
                            c.baseStats.left,
                            5));
                    }
                }
            }

            return EvaluateBoardState(
                board,
                handList.ToArray(),
                columnDice ?? new int[] { 3, 4, 2 },
                slideAvailable,
                playerCost,
                enemyCost,
                numSimulations,
                cPuct);
        }

        /// <summary>
        /// Runs dual-head Policy-Value network inference + PUCT MCTS (`c_puct = 1.414`, `num_simulations = 64`)
        /// and returns top-3 tactical move recommendations with visit counts, Q-values, and explanations.
        /// </summary>
        public SynapseAlphaZeroEvaluationResult EvaluateBoardState(
            SynapseBoardSlotSnapshot[] board,
            SynapseCardSnapshot[] hand,
            int[] columnDice,
            bool slideAvailable = true,
            int playerCost = 0,
            int enemyCost = 0,
            int numSimulations = DefaultSimulations,
            float cPuct = DefaultCPuct)
        {
            SynapseBoardSlotSnapshot[] safeBoard = new SynapseBoardSlotSnapshot[9];
            if (board != null)
            {
                Array.Copy(board, safeBoard, Mathf.Min(9, board.Length));
            }

            SynapseCardSnapshot[] safeHand = hand ?? Array.Empty<SynapseCardSnapshot>();
            int[] safeDice = (columnDice != null && columnDice.Length >= 3) ? columnDice : new int[] { 3, 4, 2 };

            float[] stateVec = EncodeBoardState(safeBoard, safeHand, safeDice, slideAvailable, playerCost, enemyCost);
            float[] hidden = new float[HiddenDim];
            for (int i = 0; i < StateDim; i++)
            {
                float x = stateVec[i];
                if (Mathf.Abs(x) < 1e-6f) continue;
                for (int j = 0; j < HiddenDim; j++)
                {
                    hidden[j] += x * _encoderW[i, j];
                }
            }
            for (int j = 0; j < HiddenDim; j++)
            {
                hidden[j] = (float)Math.Tanh(hidden[j]);
            }

            float[] logits = new float[ActionDim];
            float rawV = 0f;
            for (int j = 0; j < HiddenDim; j++)
            {
                float h = hidden[j];
                rawV += h * _valueHeadW[j];
                for (int a = 0; a < ActionDim; a++)
                {
                    logits[a] += 0.25f * h * _policyHeadW[j, a];
                }
            }

            float rootValue = (float)Math.Tanh(rawV + 0.85f * stateVec[90] + 0.25f * stateVec[92] + 0.20f * stateVec[93] + 0.18f * stateVec[88]);

            // Enumerate legal actions and compute tactical priors + PUCT rollouts
            var candidates = new List<MctsActionCandidate>();
            int maxHand = Mathf.Min(5, safeHand.Length);
            for (int h = 0; h < maxHand; h++)
            {
                for (int s = 0; s < 9; s++)
                {
                    if (!safeBoard[s].isOccupied)
                    {
                        int actionId = h * 9 + s;
                        int caps = CountDeployCaptures(safeBoard, safeHand[h], s, safeDice, 0);
                        float posBonus = s == 4 ? 0.55f : ((s == 0 || s == 2 || s == 6 || s == 8) ? 0.45f : 0.15f);
                        float costEff = Mathf.Max(0f, (7.0f - safeHand[h].mgaCost) * 0.12f);
                        float priorScore = logits[actionId] + 1.60f + caps * 2.85f + posBonus + costEff;
                        candidates.Add(new MctsActionCandidate
                        {
                            actionId = actionId,
                            actionType = SynapseMctsActionType.Deploy,
                            handIndex = h,
                            slotIndex = s,
                            captures = caps,
                            logit = priorScore,
                            cardName = safeHand[h].cardName,
                            cost = safeHand[h].mgaCost,
                            label = $"deploy({h}, {s})"
                        });
                    }
                }
            }

            if (slideAvailable)
            {
                for (int idx = 0; idx < SlidePairs.Length; idx++)
                {
                    var pair = SlidePairs[idx];
                    if (safeBoard[pair.fromSlot].isOccupied && safeBoard[pair.fromSlot].ownerId == 0 && !safeBoard[pair.toSlot].isOccupied)
                    {
                        int actionId = 45 + idx;
                        int caps = CountDeployCaptures(safeBoard, safeBoard[pair.fromSlot].card, pair.toSlot, safeDice, 0);
                        float priorScore = logits[actionId] + (caps >= 2 ? (1.20f + caps * 2.65f) : (caps == 1 ? 0.65f : -2.10f));
                        candidates.Add(new MctsActionCandidate
                        {
                            actionId = actionId,
                            actionType = SynapseMctsActionType.Slide,
                            fromSlot = pair.fromSlot,
                            toSlot = pair.toSlot,
                            captures = caps,
                            logit = priorScore,
                            cost = 2,
                            label = $"slide({pair.fromSlot}, {pair.toSlot})"
                        });
                    }
                }
            }

            for (int col = 0; col < 3; col++)
            {
                if (safeDice[col] < 6)
                {
                    int actionId = 69 + col;
                    int friendlyInCol = 0;
                    for (int r = 0; r < 3; r++)
                    {
                        int s = r * 3 + col;
                        if (safeBoard[s].isOccupied && safeBoard[s].ownerId == 0) friendlyInCol++;
                    }
                    float priorScore = logits[actionId] + (friendlyInCol >= 2 && safeDice[col] == 4 ? 0.95f : -1.75f);
                    candidates.Add(new MctsActionCandidate
                    {
                        actionId = actionId,
                        actionType = SynapseMctsActionType.NudgeDie,
                        columnIndex = col,
                        logit = priorScore,
                        cost = 1,
                        label = $"nudgeDie({col})"
                    });
                }
            }

            var result = new SynapseAlphaZeroEvaluationResult
            {
                stateValue = rootValue,
                winProbability = 0.5f * (rootValue + 1.0f),
                simulationsRun = Mathf.Max(1, numSimulations),
                cPuct = cPuct,
                policyLogits = logits
            };

            if (candidates.Count == 0)
            {
                return result;
            }

            // Softmax over candidates and top-12 progressive widening
            candidates.Sort((a, b) => b.logit.CompareTo(a.logit));
            int activeCount = Mathf.Min(12, candidates.Count);
            float maxLogit = candidates[0].logit;
            float sumExp = 0f;
            for (int i = 0; i < activeCount; i++)
            {
                float e = Mathf.Exp(Mathf.Clamp((candidates[i].logit - maxLogit) / 0.85f, -20f, 20f));
                candidates[i].prior = e;
                sumExp += e;
            }
            for (int i = 0; i < activeCount; i++)
            {
                candidates[i].prior /= Mathf.Max(1e-6f, sumExp);
            }

            // Run PUCT simulations
            int sims = Mathf.Max(1, numSimulations);
            for (int sim = 0; sim < sims; sim++)
            {
                float sqrtTotal = Mathf.Sqrt(sim + 1);
                int bestIdx = 0;
                float bestPuct = -1e9f;

                for (int i = 0; i < activeCount; i++)
                {
                    var cand = candidates[i];
                    float qEff = cand.visits > 0 ? (cand.valueSum / cand.visits) : 0.10f;
                    float puct = qEff + cPuct * cand.prior * (sqrtTotal / (1.0f + cand.visits));
                    if (puct > bestPuct)
                    {
                        bestPuct = puct;
                        bestIdx = i;
                    }
                }

                var chosen = candidates[bestIdx];
                float leafVal = Mathf.Clamp(
                    rootValue + chosen.captures * 0.28f + (chosen.slotIndex == 4 ? 0.12f : 0.04f) - chosen.visits * 0.004f,
                    -0.98f,
                    0.98f);
                chosen.visits += 1;
                chosen.valueSum += leafVal;
            }

            candidates.Sort((a, b) =>
            {
                int vCmp = b.visits.CompareTo(a.visits);
                if (vCmp != 0) return vCmp;
                return b.QValue.CompareTo(a.QValue);
            });

            int topK = Mathf.Min(3, activeCount);
            for (int r = 0; r < topK; r++)
            {
                var c = candidates[r];
                float qVal = c.QValue;
                float winP = Mathf.Clamp(0.5f * (qVal + 1.0f), 0.01f, 0.99f);
                result.topRecommendations.Add(new SynapseMctsMoveRecommendation
                {
                    rank = r + 1,
                    actionType = c.actionType,
                    actionLabel = c.label,
                    handIndex = c.handIndex,
                    slotIndex = c.slotIndex,
                    fromSlot = c.fromSlot,
                    toSlot = c.toSlot,
                    columnIndex = c.columnIndex,
                    visitCount = c.visits,
                    visitShare = c.visits / (float)sims,
                    qValue = qVal,
                    priorProbability = c.prior,
                    winProbability = winP,
                    tacticalExplanation = BuildExplanation(c, safeDice, winP)
                });
            }

            if (result.topRecommendations.Count > 0)
            {
                result.stateValue = Mathf.Clamp(0.65f * result.topRecommendations[0].qValue + 0.35f * rootValue, -1.0f, 1.0f);
                result.winProbability = 0.5f * (result.stateValue + 1.0f);
            }

            return result;
        }

        private static int CountDeployCaptures(
            SynapseBoardSlotSnapshot[] board,
            SynapseCardSnapshot card,
            int slotIndex,
            int[] columnDice,
            int actorOwnerId)
        {
            int flips = 0;
            int col = slotIndex % 3;
            float myDieBonus = columnDice[col] >= 5 ? 1.0f : (columnDice[col] == 4 ? 0.5f : 0.0f);
            int r = slotIndex / 3;

            // North (r - 1)
            if (r > 0 && IsEnemyOccupied(board, slotIndex - 3, actorOwnerId))
            {
                if (card.north + myDieBonus > board[slotIndex - 3].card.south + GetDieBonus(columnDice, (slotIndex - 3) % 3))
                    flips++;
            }
            // South (r + 1)
            if (r < 2 && IsEnemyOccupied(board, slotIndex + 3, actorOwnerId))
            {
                if (card.south + myDieBonus > board[slotIndex + 3].card.north + GetDieBonus(columnDice, (slotIndex + 3) % 3))
                    flips++;
            }
            // West (col - 1)
            if (col > 0 && IsEnemyOccupied(board, slotIndex - 1, actorOwnerId))
            {
                if (card.west + myDieBonus > board[slotIndex - 1].card.east + GetDieBonus(columnDice, (slotIndex - 1) % 3))
                    flips++;
            }
            // East (col + 1)
            if (col < 2 && IsEnemyOccupied(board, slotIndex + 1, actorOwnerId))
            {
                if (card.east + myDieBonus > board[slotIndex + 1].card.west + GetDieBonus(columnDice, (slotIndex + 1) % 3))
                    flips++;
            }
            return flips;
        }

        private static bool IsEnemyOccupied(SynapseBoardSlotSnapshot[] board, int slot, int actorOwnerId)
        {
            return board[slot].isOccupied && board[slot].ownerId != actorOwnerId;
        }

        private static float GetDieBonus(int[] columnDice, int col)
        {
            return columnDice[col] >= 5 ? 1.0f : (columnDice[col] == 4 ? 0.5f : 0.0f);
        }

        private static string BuildExplanation(MctsActionCandidate c, int[] dice, float winProb)
        {
            float winPct = Mathf.Round(winProb * 1000f) / 10f;
            if (c.actionType == SynapseMctsActionType.Deploy)
            {
                int col = c.slotIndex % 3;
                string role = c.slotIndex == 4 ? "Center Anchor" : ((c.slotIndex == 0 || c.slotIndex == 2 || c.slotIndex == 6 || c.slotIndex == 8) ? "Corner Bastion" : $"Flank Slot {c.slotIndex}");
                string capStr = c.captures > 0 ? $"triggers {c.captures} directional capture(s)" : "fortifies directional perimeter";
                return $"Deploy {c.cardName} to {role} (Slot {c.slotIndex}, Col Die={dice[col]}, COST +{c.cost}): {capStr} [{c.visits} visits, Q={c.QValue:+0.00;-0.00}, Win={winPct}%].";
            }
            if (c.actionType == SynapseMctsActionType.Slide)
            {
                return $"1x Tactical Slide Slot {c.fromSlot} -> Slot {c.toSlot}: repositions unit & flips {c.captures} enemy unit(s) [{c.visits} visits, Q={c.QValue:+0.00;-0.00}, Win={winPct}%].";
            }
            return $"Nudge Column {c.columnIndex + 1} Die (COST +1): amplifies column directional power [{c.visits} visits, Q={c.QValue:+0.00;-0.00}, Win={winPct}%].";
        }

        private sealed class MctsActionCandidate
        {
            public int actionId;
            public SynapseMctsActionType actionType;
            public int handIndex;
            public int slotIndex;
            public int fromSlot;
            public int toSlot;
            public int columnIndex;
            public int captures;
            public int cost;
            public string cardName;
            public string label;
            public float logit;
            public float prior;
            public int visits;
            public float valueSum;

            public float QValue => visits > 0 ? (valueSum / visits) : 0f;
        }
    }
}
