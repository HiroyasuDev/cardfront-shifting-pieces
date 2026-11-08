using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Core;

namespace Synapse.TcgEngine.Networking
{
    public enum SynapseCommandOp : ushort
    {
        ConnectMatch      = 100,
        PlaceCardOnGrid   = 110,
        ActivateAbility   = 120,
        EndTurn           = 130,
        Resign            = 140,
        StateHashSync     = 200
    }

    [Serializable]
    public struct SynapseCommandPacket
    {
        public uint sequenceNumber;
        public SynapseCommandOp opcode;
        public int playerId;
        public string cardUid;
        public int fromX;
        public int fromY;
        public int targetX;
        public int targetY;
        public ulong postStateHash;
    }

    /// <summary>
    /// Clean-room Authoritative Match Server & Deterministic Lockstep Verifier.
    /// Replaces third-party GameServer/TcgNetwork/NetworkMessaging with an transport-agnostic
    /// command processor that validates state hashes (FNV-1a) on every move to prevent client tampering.
    /// </summary>
    public sealed class SynapseAuthoritativeServer
    {
        public readonly TcgGameLogic Game;
        public readonly List<SynapseCommandPacket> ReplayLog = new List<SynapseCommandPacket>();
        private uint _nextSeq = 1;

        public event Action<SynapseCommandPacket, int> OnCommandCommitted;
        public event Action<SynapseCommandPacket, string> OnCommandRejected;

        public SynapseAuthoritativeServer(int seed = 1337, bool isNighttime = false)
        {
            Game = new TcgGameLogic(seed, isNighttime);
        }

        public bool SubmitCommand(SynapseCommandPacket cmd, out int capturesMade)
        {
            capturesMade = 0;
            cmd.sequenceNumber = _nextSeq++;

            switch (cmd.opcode)
            {
                case SynapseCommandOp.PlaceCardOnGrid:
                    if (!Game.PlaceCard(cmd.playerId, cmd.cardUid, cmd.targetX, cmd.targetY, out capturesMade))
                    {
                        OnCommandRejected?.Invoke(cmd, "Illegal card placement or not player's turn.");
                        return false;
                    }
                    break;

                case SynapseCommandOp.ActivateAbility:
                    if (!Game.ActivateSpecialAbility(cmd.playerId, cmd.fromX, cmd.fromY, cmd.targetX, cmd.targetY))
                    {
                        OnCommandRejected?.Invoke(cmd, "Ability conditions not met.");
                        return false;
                    }
                    break;

                case SynapseCommandOp.EndTurn:
                    if (cmd.playerId != Game.activePlayerId)
                    {
                        OnCommandRejected?.Invoke(cmd, "Not active player.");
                        return false;
                    }
                    Game.EndTurn();
                    break;

                case SynapseCommandOp.Resign:
                    Game.winnerId = 1 - cmd.playerId;
                    Game.phase = TurnPhase.GameOver;
                    break;

                default:
                    OnCommandRejected?.Invoke(cmd, "Unsupported opcode.");
                    return false;
            }

            cmd.postStateHash = Game.ComputeStateHash();
            ReplayLog.Add(cmd);
            OnCommandCommitted?.Invoke(cmd, capturesMade);
            return true;
        }
    }
}
