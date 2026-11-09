using System;
using UnityEngine;
using Synapse.TcgEngine.Core;

namespace Synapse.TcgEngine.UI
{
    /// <summary>
    /// Clean-room Unity 2022.3.40f1 MonoBehaviour controller mirroring <c>TcgEngine.UI.CardFrontTabletopUIController</c>.
    /// Bridges the 1:1 Tactile Tabletop HUD, 3D Column Dice Pedestals, Boss Holo-Telegraph Incoming Lip,
    /// 180-degree Y-axis 3D capture flips, and 24fps 8-frame Studio Trigger / Omega Strikers Sakuga Cut-In strips.
    /// </summary>
    public class CardFrontTabletopUIController : MonoBehaviour
    {
        public TactileTabletopTopologyState topologyState;
        public string activeBossTelegraphCardId;
        public Slot activeBossTelegraphSlot;
        public int activeSakugaFrameIndex;

        private static readonly int[] s_sakugaTimingLut = new int[] { 0, 1, 2, 2, 3, 4, 5, 6, 7 };

        protected virtual void Awake()
        {
            CardFrontUnifiedRuntime.Configure3x3SharedTabletopGrid();
            topologyState = TactileTabletopHudAndCinematicsBridge.CreateDefaultTabletopTopology();
        }

        public Vector4 StepSakugaCutInTick(int tickIndex, out bool isImpactFrame)
        {
            int safeTick = ((tickIndex % s_sakugaTimingLut.Length) + s_sakugaTimingLut.Length) % s_sakugaTimingLut.Length;
            activeSakugaFrameIndex = s_sakugaTimingLut[safeTick];
            isImpactFrame = PxgV100SakugaTelegraphBridge.IsSakugaImpactFrame(activeSakugaFrameIndex);
            return PxgV100SakugaTelegraphBridge.EvaluateSakugaStripFrameUv(activeSakugaFrameIndex);
        }
    }
}
