using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;
using Synapse.TcgEngine.Tools;
using Synapse.TcgEngine.Visuals;
using Synapse.TcgEngine.AI;
using Synapse.TcgEngine.Networking;

namespace Synapse.TcgEngine.Client
{
    /// <summary>
    /// Clean-room representation of a single cell on the 3x3 tactical directional capture grid.
    /// </summary>
    [Serializable]
    public class BoardSlotView
    {
        public int x;
        public int y;
        public Transform slotTransform;
        public Renderer highlightRenderer;
        public SynapseCardAesthetics occupantVisual;
        public bool isValidPlacementTarget;
        public bool isSynergyLinked;
        public int previewCaptureMask; // Bitmask: 1=Up, 2=Down, 4=Left, 8=Right
    }

    /// <summary>
    /// Orthogonal capture preview arrow data for hovered placements on the 3x3 grid.
    /// </summary>
    [Serializable]
    public struct CapturePreviewArrow
    {
        public int fromX;
        public int fromY;
        public int toX;
        public int toY;
        public int attackerValue;
        public int defenderValue;
        public bool willCapture;
        public bool isTargetImmune;
    }

    /// <summary>
    /// Clean-room Proprietary 3x3 Tactical Board Controller for Synapse.TcgEngine.
    /// Replaces third-party GameClient/Board/BoardSlot/HandCard with:
    /// - 3x3 BoardSlotView matrix (`BoardSlotView[3,3]`)
    /// - Card drag-and-drop & click-to-place input state machine
    /// - Live valid-cell highlighting & orthogonal capture preview arrows
    /// - Seamless integration with `TcgGameLogic`, `SynapseResolveQueue`, `SynapseCardAesthetics`, and `TcgMinimaxAI`.
    /// </summary>
    public class SynapseGameBoardController : MonoBehaviour
    {
        [Header("Match Configuration")]
        public int localPlayerId = 0;
        public int aiPlayerId = 1;
        public bool playAgainstAI = true;
        public int aiLookaheadDepth = 3;
        public int aiBeamWidth = 7;
        public bool startAtNighttime = false;
        public int matchSeed = 1337;

        [Header("Presentation Timing")]
        public float cardPlaceResolveDelay = 0.32f;
        public float captureFlipResolveDelay = 0.38f;
        public float aiThinkDelay = 0.45f;

        public BoardSlotView[,] Slots { get; private set; } = new BoardSlotView[TcgGameLogic.GridWidth, TcgGameLogic.GridHeight];
        public TcgGameLogic Game => _server?.Game;
        public SynapseResolveQueue ResolveQueue { get; private set; }

        private SynapseAuthoritativeServer _server;
        private List<CardDataSO> _catalog;

        // Interactive Selection & Drag-and-Drop State
        private string _selectedHandCardUid;
        private bool _isDraggingCard;
        private Vector2 _hoveredCell = new Vector2(-1, -1);
        private Vector2Int? _pendingAbilitySourceCell;
        private readonly List<CapturePreviewArrow> _capturePreviews = new List<CapturePreviewArrow>(4);

        // Events for HUD & Audio subscribers
        public event Action<TcgGameLogic> OnBoardStateUpdated;
        public event Action<int, int, int> OnCardPlacedOnBoard; // (playerId, x, y)
        public event Action<int, int, int> OnCardCaptured;      // (newOwnerId, x, y)
        public event Action<int, SpecialAbilityType, int, int> OnSpecialAbilityTriggered;
        public event Action<List<CapturePreviewArrow>> OnCapturePreviewChanged;
        public event Action<int?> OnMatchEnded;

        private void Awake()
        {
            ResolveQueue = new SynapseResolveQueue(instantMode: false);
            InitializeSlotMatrix();
        }

        public void InitializeSlotMatrix()
        {
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    Slots[x, y] ??= new BoardSlotView { x = x, y = y };
                }
            }
        }

        /// <summary>
        /// Starts a new 3x3 tactical match using the default PROJECT CF & CardCraft roster or custom decks.
        /// </summary>
        public void StartNewMatch(List<CardDataSO> p0Deck = null, List<CardDataSO> p1Deck = null, int? seedOverride = null, bool? nightOverride = null)
        {
            int seed = seedOverride ?? matchSeed;
            bool night = nightOverride ?? startAtNighttime;

            _catalog = ProjectCfCardCatalog.CreateDefaultRoster();
            _server = new SynapseAuthoritativeServer(seed, night);
            ResolveQueue.Clear();

            var deck0 = (p0Deck != null && p0Deck.Count > 0) ? p0Deck : _catalog;
            var deck1 = (p1Deck != null && p1Deck.Count > 0) ? p1Deck : _catalog;

            PopulatePlayerDeck(0, deck0);
            PopulatePlayerDeck(1, deck1);

            Game.ShuffleDeck(Game.players[0]);
            Game.ShuffleDeck(Game.players[1]);

            Game.DrawCards(Game.players[0], TcgGameLogic.StartingHandSize);
            Game.DrawCards(Game.players[1], TcgGameLogic.StartingHandSize);

            Game.activePlayerId = 0;
            Game.turnNumber = 1;
            Game.phase = TurnPhase.Main;

            ClearSelection();
            RefreshAllSlotVisuals();
            OnBoardStateUpdated?.Invoke(Game);
        }

        private void PopulatePlayerDeck(int playerId, List<CardDataSO> sourceCards)
        {
            var p = Game.players[playerId];
            p.deck.Clear();
            p.hand.Clear();
            p.discard.Clear();

            for (int i = 0; i < sourceCards.Count; i++)
            {
                var so = sourceCards[i];
                string uid = $"p{playerId}_{so.id}_{i}";
                var rc = RuntimeCard.FromCardData(so, playerId, uid);
                rc.currentZone = ZoneType.Deck;
                p.deck.Add(rc);
            }
        }

        private void Update()
        {
            if (Game == null) return;

            ResolveQueue.Tick(Time.deltaTime);

            // Drive AI turn automatically once resolve queue is idle
            if (!ResolveQueue.IsBusy &&
                playAgainstAI &&
                Game.phase == TurnPhase.Main &&
                !Game.winnerId.HasValue &&
                Game.activePlayerId == aiPlayerId)
            {
                QueueAIMove();
            }
        }

        // =====================================================================
        // INPUT HANDLING: CLICK-TO-PLACE, DRAG-AND-DROP & CAPTURE PREVIEW
        // =====================================================================

        public void SelectHandCard(string cardUid)
        {
            if (Game == null || Game.activePlayerId != localPlayerId || ResolveQueue.IsBusy) return;
            _pendingAbilitySourceCell = null;
            _selectedHandCardUid = cardUid;
            UpdateValidPlacementHighlights();
        }

        public void BeginDragHandCard(string cardUid)
        {
            SelectHandCard(cardUid);
            _isDraggingCard = !string.IsNullOrEmpty(_selectedHandCardUid);
        }

        public void OnHoverBoardSlot(int x, int y)
        {
            if (Game == null || !Game.InBounds(x, y)) return;
            _hoveredCell = new Vector2(x, y);

            if (!string.IsNullOrEmpty(_selectedHandCardUid) && Game.grid[x, y].IsEmpty)
            {
                var card = Game.players[localPlayerId].hand.Find(c => c.uid == _selectedHandCardUid);
                ComputeCapturePreview(card, localPlayerId, x, y);
            }
            else
            {
                _capturePreviews.Clear();
                OnCapturePreviewChanged?.Invoke(_capturePreviews);
            }
        }

        public void EndDragOnBoardSlot(int x, int y)
        {
            if (!_isDraggingCard) return;
            _isDraggingCard = false;
            OnClickBoardSlot(x, y);
        }

        public void OnClickBoardSlot(int x, int y)
        {
            if (Game == null || ResolveQueue.IsBusy || !Game.InBounds(x, y)) return;
            if (Game.activePlayerId != localPlayerId) return;

            // 1. Check if we are targeting an empty cell for Teleport / WarpDrive ability
            if (_pendingAbilitySourceCell.HasValue)
            {
                var src = _pendingAbilitySourceCell.Value;
                _pendingAbilitySourceCell = null;
                if (TryActivateBoardAbility(src.x, src.y, x, y))
                {
                    ClearSelection();
                    return;
                }
            }

            // 2. If clicking an occupied friendly cell, check if it has an activatable Special Ability
            if (!Game.grid[x, y].IsEmpty)
            {
                var occ = Game.grid[x, y].occupant;
                if (occ.ownerId == localPlayerId)
                {
                    if (occ.specialAbility == SpecialAbilityType.Teleport ||
                        occ.specialAbility == SpecialAbilityType.WarpDrive)
                    {
                        _pendingAbilitySourceCell = new Vector2Int(x, y);
                        HighlightEmptyCellsForAbility();
                        return;
                    }
                    if (occ.specialAbility == SpecialAbilityType.Vanish ||
                        occ.specialAbility == SpecialAbilityType.TemporalRift)
                    {
                        TryActivateBoardAbility(x, y, -1, -1);
                        return;
                    }
                }
                return;
            }

            // 3. Place selected hand card onto empty (x, y) slot
            if (!string.IsNullOrEmpty(_selectedHandCardUid))
            {
                TryPlaceCard(localPlayerId, _selectedHandCardUid, x, y);
            }
        }

        /// <summary>
        /// Computes orthogonal directional comparisons (`Up/Down/Left/Right`) for a candidate placement
        /// at `(x, y)` so the UI can draw live capture preview arrows before the player commits.
        /// </summary>
        public List<CapturePreviewArrow> ComputeCapturePreview(RuntimeCard candidateCard, int playerId, int x, int y)
        {
            _capturePreviews.Clear();
            if (candidateCard == null || Game == null || !Game.InBounds(x, y) || !Game.grid[x, y].IsEmpty)
            {
                OnCapturePreviewChanged?.Invoke(_capturePreviews);
                return _capturePreviews;
            }

            // Temporarily stage occupant to evaluate live synergy & Moonlight Blessing stats
            Game.grid[x, y].occupant = candidateCard;
            DirectionalStats atkStats = Game.GetEffectiveStats(x, y);
            Game.grid[x, y].occupant = null;

            (int dx, int dy, int atkVal, Func<DirectionalStats, int> defSelector, int bit)[] dirs =
            {
                (0,  1, atkStats.up,    d => d.down,  1),
                (0, -1, atkStats.down,  d => d.up,    2),
                (-1, 0, atkStats.left,  d => d.right, 4),
                (1,  0, atkStats.right, d => d.left,  8)
            };

            int mask = 0;
            foreach (var (dx, dy, atkVal, defSel, bit) in dirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!Game.InBounds(nx, ny) || Game.grid[nx, ny].IsEmpty) continue;

                var neighbor = Game.grid[nx, ny].occupant;
                if (neighbor.ownerId == playerId) continue;

                bool immune = Game.IsCardCaptureImmune(nx, ny);
                DirectionalStats defStats = Game.GetEffectiveStats(nx, ny);
                int defVal = defSel(defStats);
                bool captures = !immune && (atkVal > defVal);
                if (captures) mask |= bit;

                _capturePreviews.Add(new CapturePreviewArrow
                {
                    fromX = x,
                    fromY = y,
                    toX = nx,
                    toY = ny,
                    attackerValue = atkVal,
                    defenderValue = defVal,
                    willCapture = captures,
                    isTargetImmune = immune
                });
            }

            Slots[x, y].previewCaptureMask = mask;
            OnCapturePreviewChanged?.Invoke(_capturePreviews);
            return _capturePreviews;
        }

        // =====================================================================
        // AUTHORITATIVE COMMAND SUBMISSION & RESOLVE QUEUE INTEGRATION
        // =====================================================================

        public bool TryPlaceCard(int playerId, string cardUid, int x, int y)
        {
            if (Game == null || !Game.InBounds(x, y) || !Game.grid[x, y].IsEmpty) return false;

            // Snapshot pre-move owners to detect which orthogonal neighbors flipped
            int[,] preOwners = SnapshotBoardOwners();

            var cmd = new SynapseCommandPacket
            {
                opcode = SynapseCommandOp.PlaceCardOnGrid,
                playerId = playerId,
                cardUid = cardUid,
                targetX = x,
                targetY = y
            };

            if (!_server.SubmitCommand(cmd, out int captures))
                return false;

            ClearSelection();

            ResolveQueue.EnqueueStep("PlaceCard", () =>
            {
                OnCardPlacedOnBoard?.Invoke(playerId, x, y);
                RefreshAllSlotVisuals();
            }, cardUid, null, x, y);
            ResolveQueue.SetDelay(cardPlaceResolveDelay);

            if (captures > 0)
            {
                for (int cx = 0; cx < TcgGameLogic.GridWidth; cx++)
                {
                    for (int cy = 0; cy < TcgGameLogic.GridHeight; cy++)
                    {
                        if (cx == x && cy == y) continue;
                        int prevOwner = preOwners[cx, cy];
                        int curOwner = Game.grid[cx, cy].IsEmpty ? -1 : Game.grid[cx, cy].occupant.ownerId;
                        if (prevOwner != -1 && curOwner != -1 && prevOwner != curOwner)
                        {
                            int capturedX = cx, capturedY = cy, newOwner = curOwner;
                            ResolveQueue.EnqueueStep("CaptureFlip", () =>
                            {
                                Slots[capturedX, capturedY].occupantVisual?.TriggerCaptureFlip(newOwner);
                                OnCardCaptured?.Invoke(newOwner, capturedX, capturedY);
                                RefreshAllSlotVisuals();
                            }, cardUid, null, capturedX, capturedY);
                        }
                    }
                }
                ResolveQueue.SetDelay(captureFlipResolveDelay);
            }

            ResolveQueue.EnqueueStep("PostMoveSync", () =>
            {
                RefreshAllSlotVisuals();
                OnBoardStateUpdated?.Invoke(Game);
                if (Game.phase == TurnPhase.GameOver || Game.winnerId.HasValue)
                {
                    OnMatchEnded?.Invoke(Game.winnerId);
                }
            });

            return true;
        }

        public bool TryActivateBoardAbility(int fromX, int fromY, int targetX = -1, int targetY = -1)
        {
            if (Game == null || !Game.InBounds(fromX, fromY) || Game.grid[fromX, fromY].IsEmpty) return false;
            var card = Game.grid[fromX, fromY].occupant;
            var abil = card.specialAbility;

            var cmd = new SynapseCommandPacket
            {
                opcode = SynapseCommandOp.ActivateAbility,
                playerId = Game.activePlayerId,
                cardUid = card.uid,
                fromX = fromX,
                fromY = fromY,
                targetX = targetX,
                targetY = targetY
            };

            if (!_server.SubmitCommand(cmd, out _))
                return false;

            ResolveQueue.EnqueueStep("ActivateAbility", () =>
            {
                OnSpecialAbilityTriggered?.Invoke(Game.activePlayerId, abil, fromX, fromY);
                RefreshAllSlotVisuals();
                OnBoardStateUpdated?.Invoke(Game);
            }, card.uid, null, targetX, targetY);

            return true;
        }

        public void ToggleDayNightCycle()
        {
            if (Game == null) return;
            Game.isNighttime = !Game.isNighttime;
            RefreshAllSlotVisuals();
            OnBoardStateUpdated?.Invoke(Game);
        }

        private void QueueAIMove()
        {
            ResolveQueue.SetDelay(aiThinkDelay);
            ResolveQueue.EnqueueStep("AIMinimaxDecision", () =>
            {
                if (Game == null || Game.winnerId.HasValue || Game.activePlayerId != aiPlayerId) return;
                MoveAction best = TcgMinimaxAI.ChooseBestPlacement(Game, aiPlayerId, aiLookaheadDepth, aiBeamWidth);
                if (best.kind == AIActionKind.PlaceCard && !string.IsNullOrEmpty(best.cardUid))
                {
                    TryPlaceCard(aiPlayerId, best.cardUid, best.x, best.y);
                }
                else
                {
                    Game.EndTurn();
                    OnBoardStateUpdated?.Invoke(Game);
                }
            });
        }

        private int[,] SnapshotBoardOwners()
        {
            int[,] snap = new int[TcgGameLogic.GridWidth, TcgGameLogic.GridHeight];
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    snap[x, y] = Game.grid[x, y].IsEmpty ? -1 : Game.grid[x, y].occupant.ownerId;
                }
            }
            return snap;
        }

        private void UpdateValidPlacementHighlights()
        {
            bool hasSelection = !string.IsNullOrEmpty(_selectedHandCardUid);
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    Slots[x, y].isValidPlacementTarget = hasSelection && Game.grid[x, y].IsEmpty;
                }
            }
        }

        private void HighlightEmptyCellsForAbility()
        {
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    Slots[x, y].isValidPlacementTarget = Game.grid[x, y].IsEmpty;
                }
            }
        }

        public void ClearSelection()
        {
            _selectedHandCardUid = null;
            _isDraggingCard = false;
            _pendingAbilitySourceCell = null;
            _capturePreviews.Clear();
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    Slots[x, y].isValidPlacementTarget = false;
                    Slots[x, y].previewCaptureMask = 0;
                }
            }
            OnCapturePreviewChanged?.Invoke(_capturePreviews);
        }

        public void RefreshAllSlotVisuals()
        {
            if (Game == null) return;
            for (int x = 0; x < TcgGameLogic.GridWidth; x++)
            {
                for (int y = 0; y < TcgGameLogic.GridHeight; y++)
                {
                    var cell = Game.grid[x, y];
                    var slot = Slots[x, y];
                    if (cell.IsEmpty)
                    {
                        slot.isSynergyLinked = false;
                        continue;
                    }

                    var occ = cell.occupant;
                    bool hasSynergy = Game.HasOrthogonalNeighborWithTheme(x, y, occ.synergyRequiredTheme) ||
                                      (occ.specialAbility == SpecialAbilityType.MoonlightBlessing &&
                                       (Game.isNighttime || Game.HasOrthogonalNeighborWithTheme(x, y, CardTheme.Lunar)));
                    bool isImmune = Game.IsCardCaptureImmune(x, y);
                    slot.isSynergyLinked = hasSynergy;

                    if (slot.occupantVisual != null)
                    {
                        slot.occupantVisual.ApplyVisualState(occ.themes, occ.ownerId, hasSynergy, isImmune);
                    }
                }
            }
        }
    }
}
