using System;
using System.Collections.Generic;
using UnityEngine;

namespace Synapse.TcgEngine.Visuals
{
    /// <summary>
    /// Enumeration of the 12 Classic-Yet-Dynamic Telegraph & Battle Animation Archetypes.
    /// Synthesizes GBA tactical readability (Advance Wars, Final Fantasy Tactics Advance)
    /// with modern deterministic spatial telegraphs (Into the Breach, STACCS).
    /// </summary>
    public enum TelegraphArchetypeId
    {
        /// <summary>
        /// 1. Advance Wars chunky red/cyan segmented tile path arrow with bouncing arrowhead and MP/Fuel tick cost.
        /// </summary>
        AwSegmentedMovementArrow = 0,

        /// <summary>
        /// 2. Advance Wars snapping 4-corner bracket crosshair + instant crisp pill badge (85% DMG / KO! / ★3 DEF).
        /// </summary>
        AwCrosshairDamageForecast = 1,

        /// <summary>
        /// 3. Advance Wars dynamic diagonal/vertical split-screen micro-cut-in (Attacker terrain strip vs. Defender terrain strip, squad volley, HP counter ticking 10 -> 6).
        /// </summary>
        AwSplitScreenCombatCutIn = 2,

        /// <summary>
        /// 4. Advance Wars high-contrast horizontal CO eyes cut-in with scrolling pixel speedlines (★ SUPER CO POWER ★).
        /// </summary>
        AwCoPowerSpeedlineBanner = 3,

        /// <summary>
        /// 5. FFTA rotating 4-corner isometric diamond cursor + soft vertical light column (Cyan Move, Amber Act, Crimson Danger).
        /// </summary>
        FftaIsometricDiamondCursor = 4,

        /// <summary>
        /// 6. FFTA 4-quadrant isometric ring around the target stack showing FRONT (1.0x), SIDE FLANK (1.25x), and BACK REAR (1.50x + PUSH) with pulsing highlight on the active attack vector.
        /// </summary>
        FftaDirectionalFacingRing = 5,

        /// <summary>
        /// 7. FFTA glowing golden/cyan parabolic energy arcs linking adjacent allied stacks that will join a synchronized Mythril Combo (+25% x N + +1 JP).
        /// </summary>
        FftaMythrilComboLinkArcs = 6,

        /// <summary>
        /// 8. FFTA Judge whistle icon + sliding Yellow/Red Law Card badge warning before a move violates the active Judge Decree.
        /// </summary>
        FftaJudgeLawCardWarning = 7,

        /// <summary>
        /// 9. Into the Breach animated scrolling amber/crimson diagonal hazard stripes + pulsing lethal skull or ⚡ GRID -1 icon.
        /// </summary>
        ItbHazardDiagonalStripe = 8,

        /// <summary>
        /// 10. Into the Breach bouncing directional arrow from target tile to destination tile + dual concentric orange shockwave rings (BUMP +1 DMG) on collision tiles.
        /// </summary>
        ItbKineticPushBumpVector = 9,

        /// <summary>
        /// 11. STACCS translucent 3-rhombus isometric cube ghost hovering and gently bobbing at elevation Z + 1 above the target stack, displaying exact new flank stat deltas (+1 per lower story).
        /// </summary>
        Staccs3DCubeHoverGhost = 10,

        /// <summary>
        /// 12. STACCS split-cube arc showing how the top Crown cube of a tall tower will shear off or cantilever across two adjacent cells on push/capture.
        /// </summary>
        StaccsCantileverShearTrajectory = 11
    }

    /// <summary>
    /// Easing curve families inspired by classic GBA 60fps stepped frame tables and snappy tactical UI curves.
    /// </summary>
    public enum TelegraphEaseCurveType
    {
        GbaStepped2Frame = 0,
        GbaStepped4Frame = 1,
        OutBackSnap = 2,
        LinearScrollLoop = 3,
        SineBobSeamless = 4,
        HitStopChromaticImpulse = 5
    }

    /// <summary>
    /// Immutable visual specification for one of the 12 classic-yet-dynamic telegraph archetypes.
    /// Enforces the "Classic & Simple Readability + Dynamic Tactical Punch" rule (max 3 simultaneous layers per tile).
    /// </summary>
    [Serializable]
    public struct TelegraphVisualProfile
    {
        public TelegraphArchetypeId archetypeId;
        public string displayName;
        public string sourceInspiration;
        public float durationSeconds;
        public float loopFrequencyHz;
        public string primaryColorHex;
        public string secondaryColorHex;
        public TelegraphEaseCurveType easeCurveType;
        public string gbaHardwareInspiration;
        public string svgOverlayTemplate;
        public string classicSimplicityRule;
        public int layerPriority; // 1 = Ground/Tile, 2 = Mid-Elevation Ring/Vector, 3 = Top Pill/Cut-In HUD
    }

    /// <summary>
    /// Single active telegraph layer instance computed for a board frame.
    /// Capped at 3 active layers per hovered tile to guarantee zero visual clutter.
    /// </summary>
    [Serializable]
    public struct TelegraphLayerTransform
    {
        public TelegraphArchetypeId archetypeId;
        public int layerSlotIndex; // 0, 1, or 2 (strictly <= 3 layers per tile)
        public Vector3 worldOffset;
        public Vector3 localScale;
        public float rotationDegrees;
        public float opacity;
        public string primaryColorHex;
        public string secondaryColorHex;
        public string badgeLabelText;
        public string renderedSvgMarkup;
    }

    /// <summary>
    /// Deterministic board telegraph state for a given frame and tactical cursor inspection.
    /// Drives both Unity Canvas/Mesh overlays and WebGL/HTML SVG showcase renderers.
    /// </summary>
    [Serializable]
    public struct BoardTelegraphFrameState
    {
        public int hoveredX;
        public int hoveredY;
        public int facingDir;
        public int stackHeightZ;
        public int awDamagePercent;
        public int terrainStars;
        public bool triggersPushBump;
        public int comboAllyCount;
        public bool violatesJudgeLaw;
        public float timeSeconds;
        public int activeTileLayerCount; // Enforced <= 3 on primary target tile
        public List<TelegraphLayerTransform> primaryTileLayers;
        public List<TelegraphLayerTransform> auxiliaryBoardLayers;
        public string compositeHtmlHudSummary;
    }

    /// <summary>
    /// Single deterministic keyframe slice for the 0.55s Advance Wars split-screen combat cut-in.
    /// </summary>
    [Serializable]
    public struct SplitScreenCutInKeyframe
    {
        public float timestampSeconds;
        public float normalizedTime;
        public string phaseName;
        public float leftPanelSlideRatio;
        public float rightPanelSlideRatio;
        public float diagonalSplitAngleDeg;
        public float hitStopChromaticShiftPx;
        public int displayedDefenderHp;
        public int activeVolleyProjectiles;
        public bool coPowerSpeedlinesVisible;
        public string frameSvgSummary;
    }

    /// <summary>
    /// Full deterministic timeline for the classic Advance Wars split-screen battle animation (0.00s..0.55s).
    /// </summary>
    [Serializable]
    public struct SplitScreenCutInTimeline
    {
        public string attackerName;
        public string defenderName;
        public int attackerTerrainStars;
        public int defenderTerrainStars;
        public int startHp;
        public int endHp;
        public bool coPowerActive;
        public float totalDurationSeconds;
        public List<SplitScreenCutInKeyframe> keyframes;
    }

    /// <summary>
    /// Static catalog of all 12 Classic-Yet-Dynamic Telegraph & Battle Animation Archetypes.
    /// Deconstructs Advance Wars (GBA), Final Fantasy Tactics Advance (GBA), Into the Breach, and STACCS.
    /// </summary>
    public static class SynapseMultitudeTelegraphCatalog
    {
        private static readonly TelegraphVisualProfile[] Profiles = new TelegraphVisualProfile[]
        {
            // 1. AwSegmentedMovementArrow
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.AwSegmentedMovementArrow,
                displayName = "AW Segmented Movement Path Arrow",
                sourceInspiration = "Advance Wars (GBA 2001 - Intelligent Systems)",
                durationSeconds = 0.40f,
                loopFrequencyHz = 2.5f,
                primaryColorHex = "#FF3B30",
                secondaryColorHex = "#00F2FE",
                easeCurveType = TelegraphEaseCurveType.GbaStepped2Frame,
                gbaHardwareInspiration = "OAM 16x16 Tile Sprite + 2-Frame VBlank Arrowhead Bounce",
                svgOverlayTemplate = "<g class='aw-move-arrow'><path d='M8,32 L44,32' stroke='#FF3B30' stroke-width='8' stroke-linecap='square'/><polygon points='44,20 60,32 44,44' fill='#00F2FE'/><rect x='20' y='8' width='24' height='14' rx='3' fill='#0B132B'/><text x='32' y='18' fill='#FFFFFF' font-size='9' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 1 Ground Only: Solid orthogonal ribbon segments with 2px white border; never overlaps unit face sprites.",
                layerPriority = 1
            },

            // 2. AwCrosshairDamageForecast
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.AwCrosshairDamageForecast,
                displayName = "AW Snapping 4-Corner Crosshair & DMG Pill",
                sourceInspiration = "Advance Wars / Advance Wars 2: Black Hole Rising",
                durationSeconds = 0.25f,
                loopFrequencyHz = 3.0f,
                primaryColorHex = "#FF2A54",
                secondaryColorHex = "#FFD60A",
                easeCurveType = TelegraphEaseCurveType.OutBackSnap,
                gbaHardwareInspiration = "OAM 4-Corner Flipped 8x8 Brackets + BG0 Instant Numeric Pill",
                svgOverlayTemplate = "<g class='aw-crosshair'><path d='M6,18 L6,6 L18,6 M46,6 L58,6 L58,18 M58,46 L58,58 L46,58 M18,58 L6,58 L6,46' stroke='#FF2A54' stroke-width='3' fill='none'/><rect x='8' y='2' width='48' height='16' rx='4' fill='#111827' stroke='#FFD60A' stroke-width='1.5'/><text x='32' y='13' fill='#FFD60A' font-size='10' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 3 Top Pill: One high-contrast numeric pill (e.g. '85% DMG ★3') snapped above tile corners; zero decimal noise.",
                layerPriority = 3
            },

            // 3. AwSplitScreenCombatCutIn
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.AwSplitScreenCombatCutIn,
                displayName = "AW Dynamic Split-Screen Combat Micro-Cut-In",
                sourceInspiration = "Advance Wars GBA Battle Window (WIN0 / WIN1 Split)",
                durationSeconds = 0.55f,
                loopFrequencyHz = 1.0f,
                primaryColorHex = "#38BDF8",
                secondaryColorHex = "#F43F5E",
                easeCurveType = TelegraphEaseCurveType.HitStopChromaticImpulse,
                gbaHardwareInspiration = "GBA WIN0/WIN1 Diagonal Split + BG2 Parallax Terrain Strip + 3-Frame Hit-Stop",
                svgOverlayTemplate = "<g class='aw-split-cutin'><polygon points='0,0 38,0 28,64 0,64' fill='#0F172A' stroke='#38BDF8' stroke-width='2'/><polygon points='38,0 64,0 64,64 28,64' fill='#1E1B4B' stroke='#F43F5E' stroke-width='2'/><line x1='38' y1='0' x2='28' y2='64' stroke='#FFFFFF' stroke-width='3'/><text x='32' y='36' fill='#FFFFFF' font-size='10' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Committed Action Only: Fires for 0.55s on attack confirmation, ticking integer HP (10 -> 6) with crisp 3-frame hit-stop.",
                layerPriority = 3
            },

            // 4. AwCoPowerSpeedlineBanner
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.AwCoPowerSpeedlineBanner,
                displayName = "AW CO Power Eyes Cut-In & Pixel Speedlines",
                sourceInspiration = "Advance Wars Super CO Power Banner + Inti Creates Eye Flash",
                durationSeconds = 0.45f,
                loopFrequencyHz = 8.0f,
                primaryColorHex = "#FACC15",
                secondaryColorHex = "#38BDF8",
                easeCurveType = TelegraphEaseCurveType.LinearScrollLoop,
                gbaHardwareInspiration = "BG1 H-Blank Line Scroll Speedlines + OAM Double-Size Affine Star",
                svgOverlayTemplate = "<g class='aw-copower-banner'><rect x='0' y='18' width='64' height='24' fill='#090D16' stroke='#FACC15' stroke-width='2'/><line x1='4' y1='22' x2='60' y2='22' stroke='#38BDF8' stroke-width='1.5' stroke-dasharray='12,4'/><text x='32' y='34' fill='#FACC15' font-size='8' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Full-Width Letterbox Strip: Appears for 0.45s above board without obscuring tactical grid coordinates.",
                layerPriority = 3
            },

            // 5. FftaIsometricDiamondCursor
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.FftaIsometricDiamondCursor,
                displayName = "FFTA Isometric Diamond Cursor & Light Column",
                sourceInspiration = "Final Fantasy Tactics Advance (GBA 2003 - Square) Tile Selector",
                durationSeconds = 0.80f,
                loopFrequencyHz = 1.25f,
                primaryColorHex = "#00F5D4",
                secondaryColorHex = "#F59E0B",
                easeCurveType = TelegraphEaseCurveType.SineBobSeamless,
                gbaHardwareInspiration = "BG2 Isometric Rhombus Mask + BLDMOD Alpha Additive Light Pillar",
                svgOverlayTemplate = "<g class='ffta-iso-cursor'><polygon points='32,12 58,28 32,44 6,28' fill='none' stroke='#00F5D4' stroke-width='2.5'/><polygon points='18,6 46,6 46,28 18,28' fill='#00F5D4' fill-opacity='0.16'/></g>",
                classicSimplicityRule = "Layer 1 Isometric Footprint: Clean 2:1 isometric rhombus outline + subtle 16% alpha vertical beam.",
                layerPriority = 1
            },

            // 6. FftaDirectionalFacingRing
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.FftaDirectionalFacingRing,
                displayName = "FFTA 4-Quadrant Directional Facing & Backstab Ring",
                sourceInspiration = "Final Fantasy Tactics Advance Directional Hit/Crit Multipliers",
                durationSeconds = 0.60f,
                loopFrequencyHz = 2.0f,
                primaryColorHex = "#10B981",
                secondaryColorHex = "#EF4444",
                easeCurveType = TelegraphEaseCurveType.GbaStepped4Frame,
                gbaHardwareInspiration = "OAM 4-Quadrant Isometric Arcs with Palette-Swapped Active Sector",
                svgOverlayTemplate = "<g class='ffta-facing-ring'><ellipse cx='32' cy='32' rx='24' ry='12' fill='none' stroke='#10B981' stroke-width='2' stroke-dasharray='14,4'/><path d='M32,20 L40,12 L24,12 Z' fill='#EF4444'/><text x='32' y='54' fill='#FFFFFF' font-size='8' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 2 Mid-Ring: Highlights only the active attack quadrant (FRONT 1.0x / SIDE 1.25x / BACK 1.50x + PUSH).",
                layerPriority = 2
            },

            // 7. FftaMythrilComboLinkArcs
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.FftaMythrilComboLinkArcs,
                displayName = "FFTA Mythril Combo Parabolic Link Arcs",
                sourceInspiration = "Final Fantasy Tactics Advance Totema / Mythril Combo Chain",
                durationSeconds = 0.70f,
                loopFrequencyHz = 1.8f,
                primaryColorHex = "#FBBF24",
                secondaryColorHex = "#38BDF8",
                easeCurveType = TelegraphEaseCurveType.SineBobSeamless,
                gbaHardwareInspiration = "OAM Parabolic Bead Chain + Palette Cycle Pulse Between Allied Stacks",
                svgOverlayTemplate = "<g class='ffta-combo-arc'><path d='M8,40 Q32,4 56,40' fill='none' stroke='#FBBF24' stroke-width='2.5' stroke-dasharray='6,3'/><circle cx='32' cy='20' r='5' fill='#38BDF8'/><text x='32' y='14' fill='#FBBF24' font-size='8' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Auxiliary Neighbor Link: Parabolic arc bridges adjacent allied stacks without adding clutter to the central target tile.",
                layerPriority = 2
            },

            // 8. FftaJudgeLawCardWarning
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.FftaJudgeLawCardWarning,
                displayName = "FFTA Judge Whistle & Law Card Penalty Warning",
                sourceInspiration = "Final Fantasy Tactics Advance Judge Decree System (Yellow/Red Card)",
                durationSeconds = 0.50f,
                loopFrequencyHz = 2.5f,
                primaryColorHex = "#FACC15",
                secondaryColorHex = "#DC2626",
                easeCurveType = TelegraphEaseCurveType.OutBackSnap,
                gbaHardwareInspiration = "OAM Top-Right Priority Badge + 2-Tone Square Channel Whistle Chirp",
                svgOverlayTemplate = "<g class='ffta-judge-card'><rect x='42' y='4' width='14' height='20' rx='2' fill='#FACC15' stroke='#DC2626' stroke-width='1.5'/><text x='49' y='17' fill='#090D16' font-size='9' font-weight='bold' text-anchor='middle'>!</text><text x='32' y='58' fill='#FACC15' font-size='8' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Conditional Corner Badge: Only renders when the hovered card/action violates the active Judge Law.",
                layerPriority = 3
            },

            // 9. ItbHazardDiagonalStripe
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.ItbHazardDiagonalStripe,
                displayName = "ITB Scrolling Diagonal Hazard Stripes & Lethal Icon",
                sourceInspiration = "Into the Breach (Subset Games) Vek Attack & Grid Threat Telegraph",
                durationSeconds = 1.00f,
                loopFrequencyHz = 1.0f,
                primaryColorHex = "#F59E0B",
                secondaryColorHex = "#EF4444",
                easeCurveType = TelegraphEaseCurveType.LinearScrollLoop,
                gbaHardwareInspiration = "BG3 Scrolling 45-Degree Hatch Pattern + High-Contrast Threat Glyph",
                svgOverlayTemplate = "<g class='itb-hazard-stripe'><polygon points='32,12 58,28 32,44 6,28' fill='#EF4444' fill-opacity='0.22' stroke='#F59E0B' stroke-width='2' stroke-dasharray='5,3'/><text x='32' y='31' fill='#F59E0B' font-size='9' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 1 Floor Hatch: Unambiguous amber/crimson diagonal stripes locked inside tile bounds.",
                layerPriority = 1
            },

            // 10. ItbKineticPushBumpVector
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.ItbKineticPushBumpVector,
                displayName = "ITB Kinetic Push Arrow & Dual Bump Shockwave Rings",
                sourceInspiration = "Into the Breach Knockback Collision & Bump +1 DMG Preview",
                durationSeconds = 0.55f,
                loopFrequencyHz = 2.2f,
                primaryColorHex = "#FB923C",
                secondaryColorHex = "#FBBF24",
                easeCurveType = TelegraphEaseCurveType.OutBackSnap,
                gbaHardwareInspiration = "OAM Directional Bouncing Chevron + Concentric Collision Ring Sprites",
                svgOverlayTemplate = "<g class='itb-push-vector'><line x1='16' y1='32' x2='46' y2='32' stroke='#FB923C' stroke-width='4'/><polygon points='44,24 58,32 44,40' fill='#FBBF24'/><circle cx='52' cy='32' r='9' fill='none' stroke='#FB923C' stroke-width='2'/><text x='32' y='16' fill='#FB923C' font-size='8' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 2 Directional Vector: Bouncing orange arrow from target to destination tile + concentric collision rings.",
                layerPriority = 2
            },

            // 11. Staccs3DCubeHoverGhost
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.Staccs3DCubeHoverGhost,
                displayName = "STACCS 3-Rhombus Isometric Cube Ghost (Z+1 Preview)",
                sourceInspiration = "STACCS 3D Isometric Cube Stacking & Vertical Height Synergy",
                durationSeconds = 0.75f,
                loopFrequencyHz = 1.5f,
                primaryColorHex = "#38BDF8",
                secondaryColorHex = "#A855F7",
                easeCurveType = TelegraphEaseCurveType.SineBobSeamless,
                gbaHardwareInspiration = "EVA/EVB 50% Translucent 3-Rhombus Isometric Cube Sprite at Elevation Z+1",
                svgOverlayTemplate = "<g class='staccs-cube-ghost'><polygon points='32,8 52,18 32,28 12,18' fill='#38BDF8' fill-opacity='0.45' stroke='#FFFFFF' stroke-width='1.5'/><polygon points='12,18 32,28 32,46 12,36' fill='#0284C7' fill-opacity='0.45'/><polygon points='32,28 52,18 52,36 32,46' fill='#A855F7' fill-opacity='0.45'/><text x='32' y='22' fill='#FFFFFF' font-size='8' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Layer 2 Elevation Preview: Bobbing translucent 3-face cube at Z+1 showing exact +1 per story stat delta.",
                layerPriority = 2
            },

            // 12. StaccsCantileverShearTrajectory
            new TelegraphVisualProfile
            {
                archetypeId = TelegraphArchetypeId.StaccsCantileverShearTrajectory,
                displayName = "STACCS Crown Shear & Cantilever Bridge Trajectory",
                sourceInspiration = "STACCS Tall Tower Top-Cube Shear & Multi-Tile Cantilever Overhang",
                durationSeconds = 0.65f,
                loopFrequencyHz = 1.8f,
                primaryColorHex = "#C084FC",
                secondaryColorHex = "#22D3EE",
                easeCurveType = TelegraphEaseCurveType.GbaStepped4Frame,
                gbaHardwareInspiration = "OAM Affine Shear Matrix + Split-Rhombus Bridge Silhouette",
                svgOverlayTemplate = "<g class='staccs-cantilever-shear'><polygon points='24,14 48,14 56,26 32,26' fill='#C084FC' fill-opacity='0.55' stroke='#22D3EE' stroke-width='1.5'/><path d='M28,26 L52,38' stroke='#22D3EE' stroke-width='2' stroke-dasharray='4,2'/><text x='36' y='23' fill='#FFFFFF' font-size='8' font-weight='bold' text-anchor='middle'>{BADGE}</text></g>",
                classicSimplicityRule = "Auxiliary Shear Arc: Shows top Crown cube bridging across adjacent cell on Z>=2 stacks.",
                layerPriority = 2
            }
        };

        /// <summary>
        /// Returns an immutable copy of all 12 Classic-Yet-Dynamic Telegraph & Battle Animation profiles.
        /// </summary>
        public static TelegraphVisualProfile[] GetAll12Profiles()
        {
            var copy = new TelegraphVisualProfile[Profiles.Length];
            Array.Copy(Profiles, copy, Profiles.Length);
            return copy;
        }

        /// <summary>
        /// Retrieves the visual profile for a specific <see cref="TelegraphArchetypeId"/>.
        /// </summary>
        public static TelegraphVisualProfile GetProfile(TelegraphArchetypeId id)
        {
            int idx = (int)id;
            if (idx >= 0 && idx < Profiles.Length)
            {
                return Profiles[idx];
            }
            return Profiles[0];
        }
    }

    /// <summary>
    /// Deterministic Telegraph & Split-Screen Battle Cut-In Animator for <c>Synapse.TcgEngine</c>.
    /// Combines classic GBA step-curve readability (Advance Wars, Final Fantasy Tactics Advance)
    /// with spatial tactical knockback and 3D stack previews (Into the Breach, STACCS).
    /// Strictly enforces the Classic Simplicity Rule: maximum 3 simultaneous layers on any primary tile.
    /// </summary>
    public class SynapseMultitudeTelegraphAnimator : MonoBehaviour
    {
        public const int MaxSimultaneousLayersPerTile = 3;

        private static readonly string[] FacingLabels = new string[]
        {
            "FRONT 1.0x",
            "SIDE FLANK 1.25x",
            "BACK REAR 1.50x + PUSH",
            "SIDE FLANK 1.25x"
        };

        /// <summary>
        /// Evaluates a classic GBA stepped or tactical easing curve at normalized time <paramref name="t"/>.
        /// </summary>
        public static float EvaluateTelegraphCurve(TelegraphEaseCurveType curveType, float timeSeconds, float frequencyHz)
        {
            float cycle = Mathf.Repeat(timeSeconds * Mathf.Max(0.1f, frequencyHz), 1.0f);
            switch (curveType)
            {
                case TelegraphEaseCurveType.GbaStepped2Frame:
                    return cycle < 0.5f ? 0.0f : 1.0f;

                case TelegraphEaseCurveType.GbaStepped4Frame:
                    return Mathf.Floor(cycle * 4.0f) / 3.0f;

                case TelegraphEaseCurveType.OutBackSnap:
                {
                    float c1 = 1.70158f;
                    float c3 = c1 + 1.0f;
                    float p = cycle - 1.0f;
                    return Mathf.Clamp01(1.0f + c3 * p * p * p + c1 * p * p);
                }

                case TelegraphEaseCurveType.LinearScrollLoop:
                    return cycle;

                case TelegraphEaseCurveType.SineBobSeamless:
                    return 0.5f + 0.5f * Mathf.Sin(cycle * Mathf.PI * 2.0f);

                case TelegraphEaseCurveType.HitStopChromaticImpulse:
                    return cycle < 0.25f ? 1.0f : Mathf.Clamp01(1.0f - (cycle - 0.25f) / 0.75f);

                default:
                    return cycle;
            }
        }

        /// <summary>
        /// Builds a deterministic <see cref="BoardTelegraphFrameState"/> for the hovered tactical tile.
        /// Enforces the Classic Simplicity Rule: at most 3 layers on the primary tile (Ground, Mid-Ring/Cube, Top Pill),
        /// while placing multi-tile arcs (movement arrows, push vectors, Mythril combo links, cantilever bridges)
        /// into <see cref="BoardTelegraphFrameState.auxiliaryBoardLayers"/> so the board never clutters.
        /// </summary>
        public static BoardTelegraphFrameState BuildBoardTelegraphFrame(
            int hoveredX,
            int hoveredY,
            int facingDir,
            int stackHeightZ,
            int awDamagePercent,
            int terrainStars,
            bool triggersPushBump,
            int comboAllyCount,
            bool violatesJudgeLaw,
            float timeSeconds)
        {
            int clampedX = Mathf.Clamp(hoveredX, 0, 2);
            int clampedY = Mathf.Clamp(hoveredY, 0, 2);
            int clampedFacing = ((facingDir % 4) + 4) % 4;
            int clampedZ = Mathf.Clamp(stackHeightZ, 0, 5);
            int clampedDmg = Mathf.Clamp(awDamagePercent, 0, 199);
            int clampedStars = Mathf.Clamp(terrainStars, 0, 4);
            int clampedCombos = Mathf.Clamp(comboAllyCount, 0, 4);

            var primaryLayers = new List<TelegraphLayerTransform>(MaxSimultaneousLayersPerTile);
            var auxiliaryLayers = new List<TelegraphLayerTransform>(6);

            // --- PRIMARY SLOT 0 (Ground Footprint): FFTA Isometric Cursor or ITB Hazard Stripe if lethal/bump ---
            TelegraphArchetypeId groundArchetype = triggersPushBump
                ? TelegraphArchetypeId.ItbHazardDiagonalStripe
                : TelegraphArchetypeId.FftaIsometricDiamondCursor;
            TelegraphVisualProfile groundProfile = SynapseMultitudeTelegraphCatalog.GetProfile(groundArchetype);
            float groundPulse = EvaluateTelegraphCurve(groundProfile.easeCurveType, timeSeconds, groundProfile.loopFrequencyHz);
            string groundBadge = triggersPushBump ? "HAZARD" : string.Format("({0},{1})", clampedX, clampedY);

            primaryLayers.Add(new TelegraphLayerTransform
            {
                archetypeId = groundArchetype,
                layerSlotIndex = 0,
                worldOffset = new Vector3(clampedX * 1.0f, 0.02f, clampedY * 1.0f),
                localScale = Vector3.one * (0.96f + 0.04f * groundPulse),
                rotationDegrees = 0.0f,
                opacity = 0.85f + 0.15f * groundPulse,
                primaryColorHex = groundProfile.primaryColorHex,
                secondaryColorHex = groundProfile.secondaryColorHex,
                badgeLabelText = groundBadge,
                renderedSvgMarkup = groundProfile.svgOverlayTemplate.Replace("{BADGE}", groundBadge)
            });

            // --- PRIMARY SLOT 1 (Mid-Elevation Stack / Facing): STACCS 3D Cube Ghost (if stacking) or FFTA Facing Ring ---
            TelegraphArchetypeId midArchetype = clampedZ > 0
                ? TelegraphArchetypeId.Staccs3DCubeHoverGhost
                : TelegraphArchetypeId.FftaDirectionalFacingRing;
            TelegraphVisualProfile midProfile = SynapseMultitudeTelegraphCatalog.GetProfile(midArchetype);
            float midPulse = EvaluateTelegraphCurve(midProfile.easeCurveType, timeSeconds, midProfile.loopFrequencyHz);
            string midBadge = clampedZ > 0
                ? string.Format("Z{0} +{1} STAT", clampedZ + 1, clampedZ)
                : FacingLabels[clampedFacing];

            primaryLayers.Add(new TelegraphLayerTransform
            {
                archetypeId = midArchetype,
                layerSlotIndex = 1,
                worldOffset = new Vector3(clampedX * 1.0f, (clampedZ + 1) * 0.28f + 0.08f * midPulse, clampedY * 1.0f),
                localScale = Vector3.one,
                rotationDegrees = clampedFacing * 90.0f,
                opacity = 0.78f + 0.18f * midPulse,
                primaryColorHex = midProfile.primaryColorHex,
                secondaryColorHex = midProfile.secondaryColorHex,
                badgeLabelText = midBadge,
                renderedSvgMarkup = midProfile.svgOverlayTemplate.Replace("{BADGE}", midBadge)
            });

            // --- PRIMARY SLOT 2 (Top Crisp Pill Badge): Judge Law Warning (if violated) OR AW Crosshair Damage Forecast ---
            TelegraphArchetypeId topArchetype = violatesJudgeLaw
                ? TelegraphArchetypeId.FftaJudgeLawCardWarning
                : TelegraphArchetypeId.AwCrosshairDamageForecast;
            TelegraphVisualProfile topProfile = SynapseMultitudeTelegraphCatalog.GetProfile(topArchetype);
            float topPulse = EvaluateTelegraphCurve(topProfile.easeCurveType, timeSeconds, topProfile.loopFrequencyHz);
            string dmgLabel = clampedDmg >= 100 ? "KO! ★" + clampedStars : string.Format("{0}% DMG ★{1}", clampedDmg, clampedStars);
            string topBadge = violatesJudgeLaw ? "LAW VIOLATION!" : dmgLabel;

            primaryLayers.Add(new TelegraphLayerTransform
            {
                archetypeId = topArchetype,
                layerSlotIndex = 2,
                worldOffset = new Vector3(clampedX * 1.0f, (clampedZ + 1) * 0.28f + 0.45f, clampedY * 1.0f),
                localScale = Vector3.one * (0.95f + 0.08f * topPulse),
                rotationDegrees = 0.0f,
                opacity = 1.0f,
                primaryColorHex = topProfile.primaryColorHex,
                secondaryColorHex = topProfile.secondaryColorHex,
                badgeLabelText = topBadge,
                renderedSvgMarkup = topProfile.svgOverlayTemplate.Replace("{BADGE}", topBadge)
            });

            // --- AUXILIARY MULTI-TILE VECTORS (Rendered on adjacent/path tiles so primary tile never exceeds 3 layers) ---
            // 1. Advance Wars Segmented Movement Arrow
            TelegraphVisualProfile moveProfile = SynapseMultitudeTelegraphCatalog.GetProfile(TelegraphArchetypeId.AwSegmentedMovementArrow);
            float moveStep = EvaluateTelegraphCurve(moveProfile.easeCurveType, timeSeconds, moveProfile.loopFrequencyHz);
            string moveBadge = string.Format("MP -{0}", Mathf.Max(1, clampedX + clampedY));
            auxiliaryLayers.Add(new TelegraphLayerTransform
            {
                archetypeId = TelegraphArchetypeId.AwSegmentedMovementArrow,
                layerSlotIndex = 0,
                worldOffset = new Vector3(Mathf.Max(0, clampedX - 1) * 1.0f, 0.03f + 0.03f * moveStep, clampedY * 1.0f),
                localScale = Vector3.one,
                rotationDegrees = clampedFacing * 90.0f,
                opacity = 0.95f,
                primaryColorHex = moveProfile.primaryColorHex,
                secondaryColorHex = moveProfile.secondaryColorHex,
                badgeLabelText = moveBadge,
                renderedSvgMarkup = moveProfile.svgOverlayTemplate.Replace("{BADGE}", moveBadge)
            });

            // 2. Into the Breach Kinetic Push/Bump Vector (when triggersPushBump is true)
            if (triggersPushBump)
            {
                TelegraphVisualProfile pushProfile = SynapseMultitudeTelegraphCatalog.GetProfile(TelegraphArchetypeId.ItbKineticPushBumpVector);
                float pushBounce = EvaluateTelegraphCurve(pushProfile.easeCurveType, timeSeconds, pushProfile.loopFrequencyHz);
                string pushBadge = "BUMP +1 DMG";
                auxiliaryLayers.Add(new TelegraphLayerTransform
                {
                    archetypeId = TelegraphArchetypeId.ItbKineticPushBumpVector,
                    layerSlotIndex = 1,
                    worldOffset = new Vector3(clampedX * 1.0f, 0.14f, clampedY * 1.0f) + new Vector3(0.12f * pushBounce, 0f, 0f),
                    localScale = Vector3.one,
                    rotationDegrees = clampedFacing * 90.0f,
                    opacity = 0.95f,
                    primaryColorHex = pushProfile.primaryColorHex,
                    secondaryColorHex = pushProfile.secondaryColorHex,
                    badgeLabelText = pushBadge,
                    renderedSvgMarkup = pushProfile.svgOverlayTemplate.Replace("{BADGE}", pushBadge)
                });
            }

            // 3. FFTA Mythril Combo Link Arcs (when comboAllyCount > 0)
            if (clampedCombos > 0)
            {
                TelegraphVisualProfile comboProfile = SynapseMultitudeTelegraphCatalog.GetProfile(TelegraphArchetypeId.FftaMythrilComboLinkArcs);
                float comboPulse = EvaluateTelegraphCurve(comboProfile.easeCurveType, timeSeconds, comboProfile.loopFrequencyHz);
                string comboBadge = string.Format("COMBO +{0}% +{1}JP", clampedCombos * 25, clampedCombos);
                auxiliaryLayers.Add(new TelegraphLayerTransform
                {
                    archetypeId = TelegraphArchetypeId.FftaMythrilComboLinkArcs,
                    layerSlotIndex = 1,
                    worldOffset = new Vector3(clampedX * 1.0f, 0.35f + 0.06f * comboPulse, clampedY * 1.0f),
                    localScale = Vector3.one,
                    rotationDegrees = 0.0f,
                    opacity = 0.90f,
                    primaryColorHex = comboProfile.primaryColorHex,
                    secondaryColorHex = comboProfile.secondaryColorHex,
                    badgeLabelText = comboBadge,
                    renderedSvgMarkup = comboProfile.svgOverlayTemplate.Replace("{BADGE}", comboBadge)
                });
            }

            // 4. STACCS Cantilever Shear Trajectory (when stackHeightZ >= 2 and push/shear active)
            if (clampedZ >= 2)
            {
                TelegraphVisualProfile shearProfile = SynapseMultitudeTelegraphCatalog.GetProfile(TelegraphArchetypeId.StaccsCantileverShearTrajectory);
                float shearStep = EvaluateTelegraphCurve(shearProfile.easeCurveType, timeSeconds, shearProfile.loopFrequencyHz);
                string shearBadge = string.Format("CROWN Z{0} BRIDGE", clampedZ);
                auxiliaryLayers.Add(new TelegraphLayerTransform
                {
                    archetypeId = TelegraphArchetypeId.StaccsCantileverShearTrajectory,
                    layerSlotIndex = 2,
                    worldOffset = new Vector3(clampedX * 1.0f, clampedZ * 0.28f + 0.05f * shearStep, clampedY * 1.0f),
                    localScale = Vector3.one,
                    rotationDegrees = clampedFacing * 90.0f,
                    opacity = 0.88f,
                    primaryColorHex = shearProfile.primaryColorHex,
                    secondaryColorHex = shearProfile.secondaryColorHex,
                    badgeLabelText = shearBadge,
                    renderedSvgMarkup = shearProfile.svgOverlayTemplate.Replace("{BADGE}", shearBadge)
                });
            }

            string hudSummary = string.Format(
                "TILE ({0},{1}) | {2} | {3} | Z-STACK: {4} | LAYERS: {5}/{6}",
                clampedX,
                clampedY,
                topBadge,
                FacingLabels[clampedFacing],
                clampedZ,
                primaryLayers.Count,
                MaxSimultaneousLayersPerTile);

            return new BoardTelegraphFrameState
            {
                hoveredX = clampedX,
                hoveredY = clampedY,
                facingDir = clampedFacing,
                stackHeightZ = clampedZ,
                awDamagePercent = clampedDmg,
                terrainStars = clampedStars,
                triggersPushBump = triggersPushBump,
                comboAllyCount = clampedCombos,
                violatesJudgeLaw = violatesJudgeLaw,
                timeSeconds = timeSeconds,
                activeTileLayerCount = primaryLayers.Count,
                primaryTileLayers = primaryLayers,
                auxiliaryBoardLayers = auxiliaryLayers,
                compositeHtmlHudSummary = hudSummary
            };
        }

        /// <summary>
        /// Builds a deterministic keyframe timeline (0.00s..0.55s) for the classic Advance Wars
        /// dynamic split-screen combat micro-cut-in, including CO Power speedlines and integer HP countdown.
        /// </summary>
        public static SplitScreenCutInTimeline BuildSplitScreenCutInTimeline(
            string attackerName,
            string defenderName,
            int attackerTerrainStars,
            int defenderTerrainStars,
            int startHp,
            int endHp,
            bool coPowerActive)
        {
            string safeAttacker = string.IsNullOrEmpty(attackerName) ? "SYNAPSE STRIKER" : attackerName;
            string safeDefender = string.IsNullOrEmpty(defenderName) ? "NULL GUARDIAN" : defenderName;
            int clampedAttStars = Mathf.Clamp(attackerTerrainStars, 0, 4);
            int clampedDefStars = Mathf.Clamp(defenderTerrainStars, 0, 4);
            int clampedStartHp = Mathf.Clamp(startHp, 1, 10);
            int clampedEndHp = Mathf.Clamp(endHp, 0, clampedStartHp);

            const float totalDuration = 0.55f;
            float[] sampleTimes = new float[] { 0.00f, 0.10f, 0.22f, 0.34f, 0.45f, 0.55f };
            string[] phaseNames = new string[]
            {
                "WIN0/WIN1 Shutter Snap-In",
                "CO Power Speedline & Terrain Strip Lock",
                "Squad Volley Fire & Muzzle Flash",
                "Inti Creates 3-Frame Chromatic Hit-Stop",
                "Advance Wars Integer HP Tick Down",
                "Clean Split-Screen Wipe Out"
            };

            var keyframes = new List<SplitScreenCutInKeyframe>(sampleTimes.Length);
            for (int i = 0; i < sampleTimes.Length; i++)
            {
                float t = sampleTimes[i];
                float norm = t / totalDuration;

                float slide = i == 0 ? 0.35f : (i == sampleTimes.Length - 1 ? 0.0f : 1.0f);
                float splitAngle = 76.0f;
                float hitStopShift = (i == 3) ? 4.5f : 0.0f;
                int volleyCount = (i == 2 || i == 3) ? 4 : 0;

                float hpLerp = Mathf.Clamp01((t - 0.22f) / 0.23f);
                int currentHp = Mathf.RoundToInt(Mathf.Lerp(clampedStartHp, clampedEndHp, hpLerp));

                string frameSvg = string.Format(
                    "<svg viewBox='0 0 120 48' class='aw-cutin-slice'><rect x='0' y='0' width='58' height='48' fill='#0F172A'/><rect x='62' y='0' width='58' height='48' fill='#1E1B4B'/><line x1='62' y1='0' x2='54' y2='48' stroke='#FACC15' stroke-width='3'/><text x='8' y='16' fill='#38BDF8' font-size='7'>{0} ★{1}</text><text x='68' y='16' fill='#F43F5E' font-size='7'>{2} ★{3}</text><text x='88' y='36' fill='#FFFFFF' font-size='12' font-weight='bold'>HP {4}</text></svg>",
                    safeAttacker,
                    clampedAttStars,
                    safeDefender,
                    clampedDefStars,
                    currentHp);

                keyframes.Add(new SplitScreenCutInKeyframe
                {
                    timestampSeconds = t,
                    normalizedTime = norm,
                    phaseName = phaseNames[i],
                    leftPanelSlideRatio = slide,
                    rightPanelSlideRatio = slide,
                    diagonalSplitAngleDeg = splitAngle,
                    hitStopChromaticShiftPx = hitStopShift,
                    displayedDefenderHp = currentHp,
                    activeVolleyProjectiles = volleyCount,
                    coPowerSpeedlinesVisible = coPowerActive && (i >= 1 && i <= 4),
                    frameSvgSummary = frameSvg
                });
            }

            return new SplitScreenCutInTimeline
            {
                attackerName = safeAttacker,
                defenderName = safeDefender,
                attackerTerrainStars = clampedAttStars,
                defenderTerrainStars = clampedDefStars,
                startHp = clampedStartHp,
                endHp = clampedEndHp,
                coPowerActive = coPowerActive,
                totalDurationSeconds = totalDuration,
                keyframes = keyframes
            };
        }
    }
}
