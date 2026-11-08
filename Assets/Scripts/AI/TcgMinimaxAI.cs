using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.AI
{
    public enum AIActionKind
    {
        PlaceCard = 1,
        ActivateSpecial = 2,
        EndTurn = 3
    }

    public struct MoveAction
    {
        public AIActionKind kind;
        public string cardUid;
        public int fromX;
        public int fromY;
        public int x;
        public int y;
        public float score;
        public int nodesEvaluated;
        public int reachedDepth;
    }

    /// <summary>
    /// Clean-room Proprietary Alpha-Beta Pruning Minimax + Beam Search Lookahead AI
    /// for Synapse.TcgEngine (PROJECT CF: Card Front Tactics & CardCraft).
    /// Replaces third-party AILogic/AIPlayerMM/AIHeuristic with zero-GC state cloning,
    /// beam-width move ordering, and tactical 3x3 directional capture evaluation.
    /// </summary>
    public static class TcgMinimaxAI
    {
        public static int DefaultMaxDepth = 3;
        public static int DefaultBeamWidth = 7;

        public static float EvaluateBoardState(TcgGameLogic game, int aiPlayerId)
        {
            int oppId = 1 - aiPlayerId;
            if (game.winnerId == aiPlayerId) return 10000f;
            if (game.winnerId == oppId) return -10000f;

            float score = 0f;
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    if (game.grid[x, y].IsEmpty) continue;
                    var card = game.grid[x, y].occupant;
                    var stats = game.GetEffectiveStats(x, y);
                    float sign = (card.ownerId == aiPlayerId) ? 1f : -1f;

                    // Base card ownership value (100 pts per controlled cell)
                    float cellValue = 100f;

                    // Sum directional strength facing open cells (defensive resilience)
                    if (game.InBounds(x, y + 1) && game.grid[x, y + 1].IsEmpty) cellValue += stats.up * 2.5f;
                    if (game.InBounds(x, y - 1) && game.grid[x, y - 1].IsEmpty) cellValue += stats.down * 2.5f;
                    if (game.InBounds(x - 1, y) && game.grid[x - 1, y].IsEmpty) cellValue += stats.left * 2.5f;
                    if (game.InBounds(x + 1, y) && game.grid[x + 1, y].IsEmpty) cellValue += stats.right * 2.5f;

                    // Corner cells only have 2 exposed sides -> tactical bonus
                    bool isCorner = (x == 0 || x == 2) && (y == 0 || y == 2);
                    if (isCorner) cellValue += 12f;

                    // Immunity bonus
                    if (game.IsCardCaptureImmune(x, y)) cellValue += 25f;

                    score += sign * cellValue;
                }
            }

            score += (game.players[aiPlayerId].hand.Count - game.players[oppId].hand.Count) * 8f;
            score += (game.players[aiPlayerId].confidencePoints - game.players[oppId].confidencePoints) * 0.5f;
            return score;
        }

        /// <summary>
        /// Full Alpha-Beta Pruning Minimax lookahead up to `maxDepth` plies with `beamWidth` move ordering.
        /// </summary>
        public static MoveAction ChooseBestPlacement(TcgGameLogic game, int aiPlayerId, int maxDepth = 3, int beamWidth = 7)
        {
            int nodesEvaluated = 0;
            var rootCandidates = GenerateOrderedMoves(game, aiPlayerId, beamWidth);
            if (rootCandidates.Count == 0)
            {
                return new MoveAction { kind = AIActionKind.EndTurn, score = EvaluateBoardState(game, aiPlayerId) };
            }

            MoveAction bestMove = rootCandidates[0];
            float alpha = float.NegativeInfinity;
            float beta = float.PositiveInfinity;

            foreach (var candidate in rootCandidates)
            {
                var sim = game.CloneState();
                sim.PlaceCard(aiPlayerId, candidate.cardUid, candidate.x, candidate.y, out _);
                nodesEvaluated++;

                float val = AlphaBeta(sim, aiPlayerId, maxDepth - 1, alpha, beta, ref nodesEvaluated, beamWidth);
                if (val > alpha)
                {
                    alpha = val;
                    bestMove = candidate;
                    bestMove.score = val;
                }
            }

            bestMove.nodesEvaluated = nodesEvaluated;
            bestMove.reachedDepth = maxDepth;
            return bestMove;
        }

        private static float AlphaBeta(
            TcgGameLogic state,
            int rootAiPlayerId,
            int depth,
            float alpha,
            float beta,
            ref int nodesEvaluated,
            int beamWidth)
        {
            if (depth <= 0 || state.winnerId.HasValue || state.IsGameOver())
            {
                return EvaluateBoardState(state, rootAiPlayerId);
            }

            int currentPlayer = state.activePlayerId;
            var moves = GenerateOrderedMoves(state, currentPlayer, beamWidth);
            if (moves.Count == 0)
            {
                return EvaluateBoardState(state, rootAiPlayerId);
            }

            if (currentPlayer == rootAiPlayerId)
            {
                float maxEval = float.NegativeInfinity;
                foreach (var m in moves)
                {
                    var child = state.CloneState();
                    child.PlaceCard(currentPlayer, m.cardUid, m.x, m.y, out _);
                    nodesEvaluated++;
                    float eval = AlphaBeta(child, rootAiPlayerId, depth - 1, alpha, beta, ref nodesEvaluated, beamWidth);
                    if (eval > maxEval) maxEval = eval;
                    if (eval > alpha) alpha = eval;
                    if (beta <= alpha) break; // Beta cutoff
                }
                return maxEval;
            }
            else
            {
                float minEval = float.PositiveInfinity;
                foreach (var m in moves)
                {
                    var child = state.CloneState();
                    child.PlaceCard(currentPlayer, m.cardUid, m.x, m.y, out _);
                    nodesEvaluated++;
                    float eval = AlphaBeta(child, rootAiPlayerId, depth - 1, alpha, beta, ref nodesEvaluated, beamWidth);
                    if (eval < minEval) minEval = eval;
                    if (eval < beta) beta = eval;
                    if (beta <= alpha) break; // Alpha cutoff
                }
                return minEval;
            }
        }

        public static List<MoveAction> GenerateOrderedMoves(TcgGameLogic game, int playerId, int maxKeep = 7)
        {
            var hand = game.players[playerId].hand;
            var candidates = new List<MoveAction>(hand.Count * 9);

            foreach (var card in hand)
            {
                for (int x = 0; x < TcgGameLogic.GridWidth; x++)
                {
                    for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                    {
                        if (!game.grid[x, y].IsEmpty) continue;
                        float heuristicScore = SimulatePlacementScore(game, playerId, card, x, y);
                        candidates.Add(new MoveAction
                        {
                            kind = AIActionKind.PlaceCard,
                            cardUid = card.uid,
                            x = x,
                            y = y,
                            score = heuristicScore
                        });
                    }
                }
            }

            candidates.Sort((a, b) => b.score.CompareTo(a.score));
            if (candidates.Count > maxKeep)
            {
                candidates.RemoveRange(maxKeep, candidates.Count - maxKeep);
            }
            return candidates;
        }

        private static float SimulatePlacementScore(TcgGameLogic game, int aiPlayerId, RuntimeCard card, int x, int y)
        {
            game.grid[x, y].occupant = card;
            var stats = game.GetEffectiveStats(x, y);
            int simulatedCaptures = 0;

            (int dx, int dy, int atk, Func<DirectionalStats, int> defSelector)[] dirs =
            {
                (0, 1, stats.up, d => d.down),
                (0, -1, stats.down, d => d.up),
                (-1, 0, stats.left, d => d.right),
                (1, 0, stats.right, d => d.left)
            };

            foreach (var (dx, dy, atk, defSel) in dirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!game.InBounds(nx, ny) || game.grid[nx, ny].IsEmpty) continue;
                var neighbor = game.grid[nx, ny].occupant;
                if (neighbor.ownerId != aiPlayerId && !game.IsCardCaptureImmune(nx, ny))
                {
                    var defStats = game.GetEffectiveStats(nx, ny);
                    if (atk > defSel(defStats)) simulatedCaptures++;
                }
            }

            float score = simulatedCaptures * 200f + (stats.up + stats.down + stats.left + stats.right) * 3f;
            if ((x == 0 || x == 2) && (y == 0 || y == 2)) score += 10f;

            game.grid[x, y].occupant = null;
            return score;
        }
    }
}
