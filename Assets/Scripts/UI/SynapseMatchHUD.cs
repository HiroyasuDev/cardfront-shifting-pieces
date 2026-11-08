using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;
using Synapse.TcgEngine.Client;
using Synapse.TcgEngine.Visuals;

namespace Synapse.TcgEngine.UI
{
    /// <summary>
    /// Immutable snapshot of the match HUD state for UI binding and automated testing.
    /// </summary>
    [Serializable]
    public struct MatchHudViewModel
    {
        public int turnNumber;
        public int activePlayerId;
        public string activePlayerBanner;
        public bool isNighttime;
        public string environmentCycleLabel;
        public MasterIllustratorStyle activeIllustratorStyle;
        public string activeIllustratorBanner;
        public string activeIllustratorSignatureWorks;
        public int player0ControlledCells;
        public int player1ControlledCells;
        public int player0ConfidencePoints;
        public int player1ConfidencePoints;
        public bool isBonusMoveActive;
        public bool showAbilityPrompt;
        public string abilityPromptTitle;
        public string abilityPromptHint;
        public bool isGameOver;
        public int winnerId;
        public string victoryHeadline;
        public int xpAwarded;
        public int cpAwarded;
        public List<string> unlockedBadges;
    }

    /// <summary>
    /// Clean-room Match HUD Controller for Synapse.TcgEngine (PROJECT CF & CardCraft).
    /// Displays:
    /// - Turn Number & Active Player indicator (including Mech Knight's `Charge` bonus move banner)
    /// - Day/Night Cycle indicator & toggle (for Lunar Oracle's `Moonlight Blessing`)
    /// - 5-Master Illustrator Style Switcher (`Ryōma Itō`, `Akihiko Yoshida`, `Hideo Minaba`, `Ryo Hirata`, `Toru Nakayama`, + `5-Master Synthesis`)
    /// - Controlled Cell Score (`P0 vs P1` on the 3x3 grid)
    /// - CardCraft Confidence Points (`CP`) counter
    /// - Special Ability activation prompt (`Teleport`, `WarpDrive`, `Vanish`, `TemporalRift`)
    /// - End-Game Victory / Rewards / Card Evolution modal.
    /// </summary>
    public class SynapseMatchHUD : MonoBehaviour
    {
        [Header("Board Controller Reference")]
        public SynapseGameBoardController boardController;

        [Header("Active Illustrator Aesthetic Profile")]
        public MasterIllustratorStyle selectedIllustratorStyle = MasterIllustratorStyle.TacticalSynthesis_Default;

        public MatchHudViewModel CurrentState { get; private set; }

        // Selected board cell for ability prompt inspection
        private int _inspectedX = -1;
        private int _inspectedY = -1;

        public event Action<MatchHudViewModel> OnHudViewModelUpdated;
        public event Action<IllustratorStyleProfile> OnIllustratorStyleChanged;
        public event Action<string> OnToastNotification;

        private void OnEnable()
        {
            if (boardController != null)
            {
                boardController.OnBoardStateUpdated += SyncFromGameLogic;
                boardController.OnSpecialAbilityTriggered += HandleSpecialAbilityTriggered;
                boardController.OnMatchEnded += HandleMatchEnded;
            }
        }

        private void OnDisable()
        {
            if (boardController != null)
            {
                boardController.OnBoardStateUpdated -= SyncFromGameLogic;
                boardController.OnSpecialAbilityTriggered -= HandleSpecialAbilityTriggered;
                boardController.OnMatchEnded -= HandleMatchEnded;
            }
        }

        /// <summary>
        /// Switches the active Illustrator Style profile (`Ryōma Itō`, `Akihiko Yoshida`,
        /// `Hideo Minaba`, `Ryo Hirata`, `Toru Nakayama`, or `Frontier Legends 5-Master Synthesis`)
        /// and broadcasts the updated shader grading profile.
        /// </summary>
        public IllustratorStyleProfile SetIllustratorStyle(MasterIllustratorStyle style)
        {
            selectedIllustratorStyle = style;
            var profile = SynapseIllustratorStyleLibrary.GetProfile(style);
            OnIllustratorStyleChanged?.Invoke(profile);
            OnToastNotification?.Invoke($"Illustrator Style: {profile.artistName} ({profile.japaneseName})");

            if (boardController != null && boardController.Game != null)
            {
                SyncFromGameLogic(boardController.Game);
            }
            return profile;
        }

        /// <summary>
        /// Cycles sequentially through all 6 `MasterIllustratorStyle` presets.
        /// </summary>
        public IllustratorStyleProfile CycleNextIllustratorStyle()
        {
            int next = ((int)selectedIllustratorStyle + 1) % 6;
            return SetIllustratorStyle((MasterIllustratorStyle)next);
        }

        /// <summary>
        /// Synchronizes the HUD view model directly from an authoritative `TcgGameLogic` instance.
        /// </summary>
        public void SyncFromGameLogic(TcgGameLogic game)
        {
            if (game == null) return;

            int p0Score = game.CountControlledCards(0);
            int p1Score = game.CountControlledCards(1);
            bool bonusMove = game.bonusMovePlayerId.HasValue;

            string banner = game.activePlayerId == 0
                ? (bonusMove ? "PLAYER 1 — CHARGE BONUS MOVE!" : "PLAYER 1 TURN (FRONTIER AZURE)")
                : (bonusMove ? "RIVAL AI — CHARGE BONUS MOVE!" : "RIVAL AI TURN (CRIMSON VANGUARD)");

            var styleProfile = SynapseIllustratorStyleLibrary.GetProfile(selectedIllustratorStyle);

            bool showAbil = false;
            string abilTitle = string.Empty;
            string abilHint = string.Empty;

            if (game.InBounds(_inspectedX, _inspectedY) && !game.grid[_inspectedX, _inspectedY].IsEmpty)
            {
                var occ = game.grid[_inspectedX, _inspectedY].occupant;
                if (occ.ownerId == game.activePlayerId && CanPromptSpecialAbility(occ, out abilTitle, out abilHint))
                {
                    showAbil = true;
                }
            }

            bool over = game.phase == TurnPhase.GameOver || game.winnerId.HasValue;
            int winId = game.winnerId ?? -99;
            string headline = string.Empty;
            int xpReward = 0;
            int cpReward = 0;
            var badges = new List<string>();

            if (over)
            {
                if (winId == 0)
                {
                    headline = $"VICTORY! ({p0Score} - {p1Score})";
                    xpReward = 100;
                    cpReward = 25;
                }
                else if (winId == 1)
                {
                    headline = $"DEFEAT ({p0Score} - {p1Score})";
                    xpReward = 25;
                    cpReward = 10;
                }
                else
                {
                    headline = $"TACTICAL DRAW ({p0Score} - {p1Score})";
                    xpReward = 50;
                    cpReward = 15;
                }

                foreach (var b in game.players[0].badges)
                {
                    badges.Add(b);
                }
            }

            CurrentState = new MatchHudViewModel
            {
                turnNumber = game.turnNumber,
                activePlayerId = game.activePlayerId,
                activePlayerBanner = banner,
                isNighttime = game.isNighttime,
                environmentCycleLabel = game.isNighttime
                    ? "NIGHT CYCLE (Lunar Oracle +1 All Sides Active)"
                    : "DAYLIGHT CYCLE (Standard Solar Illumination)",
                activeIllustratorStyle = selectedIllustratorStyle,
                activeIllustratorBanner = $"{styleProfile.artistName} ({styleProfile.japaneseName})",
                activeIllustratorSignatureWorks = styleProfile.signatureWorks,
                player0ControlledCells = p0Score,
                player1ControlledCells = p1Score,
                player0ConfidencePoints = game.players[0].confidencePoints,
                player1ConfidencePoints = game.players[1].confidencePoints,
                isBonusMoveActive = bonusMove,
                showAbilityPrompt = showAbil,
                abilityPromptTitle = abilTitle,
                abilityPromptHint = abilHint,
                isGameOver = over,
                winnerId = winId,
                victoryHeadline = headline,
                xpAwarded = xpReward,
                cpAwarded = cpReward,
                unlockedBadges = badges
            };

            OnHudViewModelUpdated?.Invoke(CurrentState);
        }

        /// <summary>
        /// Inspects a board cell to determine whether an activatable Special Ability prompt
        /// (`Teleport`, `WarpDrive`, `Vanish`, `TemporalRift`) should be shown on the HUD.
        /// </summary>
        public void InspectBoardSlotForAbilityPrompt(TcgGameLogic game, int x, int y)
        {
            _inspectedX = x;
            _inspectedY = y;
            SyncFromGameLogic(game);
        }

        public static bool CanPromptSpecialAbility(RuntimeCard card, out string title, out string hint)
        {
            title = string.Empty;
            hint = string.Empty;
            if (card == null) return false;

            switch (card.specialAbility)
            {
                case SpecialAbilityType.Teleport:
                    if (card.oncePerGameAbilityUsed) return false;
                    title = "TELEPORT (Mystic Mage)";
                    hint = "Once per game: Select any unoccupied 3x3 cell to relocate and trigger orthogonal captures.";
                    return true;

                case SpecialAbilityType.WarpDrive:
                    if (card.movedThisTurn) return false;
                    title = "WARP DRIVE (Galactic Explorer / Animatic)";
                    hint = "Once per turn: Relocate to any unoccupied 3x3 cell and resolve directional captures.";
                    return true;

                case SpecialAbilityType.Vanish:
                    if (card.oncePerGameAbilityUsed) return false;
                    title = "VANISH (Shadow Assassin)";
                    hint = "Once per game: Cloak this card, rendering it immune to orthogonal capture for 1 full turn.";
                    return true;

                case SpecialAbilityType.TemporalRift:
                    if (card.oncePerGameAbilityUsed) return false;
                    title = "TEMPORAL RIFT (Clockwork Sorcerer)";
                    hint = "Once per game: Invert Up<->Down and Left<->Right stats on all orthogonally adjacent cards for 1 turn.";
                    return true;

                default:
                    return false;
            }
        }

        public void ConfirmAbilityActivation(int targetX = -1, int targetY = -1)
        {
            if (boardController == null || _inspectedX < 0 || _inspectedY < 0) return;
            if (boardController.TryActivateBoardAbility(_inspectedX, _inspectedY, targetX, targetY))
            {
                _inspectedX = -1;
                _inspectedY = -1;
            }
        }

        private void HandleSpecialAbilityTriggered(int playerId, SpecialAbilityType ability, int x, int y)
        {
            OnToastNotification?.Invoke($"Player {playerId + 1} activated {ability} at ({x}, {y})!");
        }

        private void HandleMatchEnded(int? winnerId)
        {
            if (boardController != null && boardController.Game != null)
            {
                SyncFromGameLogic(boardController.Game);
            }
        }
    }
}
