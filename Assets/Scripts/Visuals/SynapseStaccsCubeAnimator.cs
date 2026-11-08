using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Visuals
{
    /// <summary>
    /// Represents the 3 visible faces of a STACCS-inspired 3D Isometric Hexagonal Cube-Card.
    /// In an orthographic isometric projection (45° yaw, 35.264° pitch), a cube's silhouette
    /// forms a regular hexagon partitioned into three rhombic faces:
    /// - TopDiamondFace: Displays the card's Crown Emblem, Artwork, and Active Special Icon.
    /// - LeftIsoFace: Displays the Left/Up Flank Directional Stats & Faction Theme Badge.
    /// - RightIsoFace: Displays the Right/Down Flank Directional Stats & Owner Allegiance Color.
    /// </summary>
    [Serializable]
    public struct StaccsIsoCubeFaceData
    {
        public string cardId;
        public string displayName;
        public int ownerId;
        public int zStackIndex; // 1..5 vertical stack height
        public int statUp;
        public int statDown;
        public int statLeft;
        public int statRight;
        public CardTheme themes;
        public SpecialAbilityType specialAbility;
        public bool hasCantileverOverhang;
        public bool isTelegraphedHazardTarget;
    }

    /// <summary>
    /// Represents a deterministic Into the Breach telegraphed attack vector or environmental hazard
    /// rendered on the isometric board prior to end-of-turn resolution.
    /// </summary>
    [Serializable]
    public struct BreachTelegraphChevron
    {
        public Vector2Int sourceCoord;
        public Vector2Int targetCoord;
        public Vector2Int pushDirection;
        public int projectedDamage;
        public bool threatensPowerGrid;
        public string hazardLabel;
    }

    /// <summary>
    /// Clean-room Unity 3D Isometric Hexagonal Cube-Card Renderer & Battle Stacking Animator
    /// inspired by STACCS (https://youtube.com/shorts/EmsNLDg2B-s) and Into the Breach:
    /// 1. Projects each card into a 3-face isometric hexagonal cube:
    ///    - TopDiamondFace (Crown / Artwork / Special Icon)
    ///    - LeftIsoFace (Left/Up Flank Stats & Theme Badge)
    ///    - RightIsoFace (Right/Down Flank Stats & Owner Color)
    /// 2. Animates vertical Z-stack drops (AnimateStackDrop(int zIndex)) with sequential
    ///    cubic-bezier bounce and acoustic pitch escalation per stack height (Z = 1..5).
    /// 3. Renders cantilever overhang bridges when upper Z-layers bridge across adjacent cells.
    /// 4. Animates Into the Breach directional push/bump knockback recoil and telegraphed
    ///    hazard warning chevrons.
    /// </summary>
    public class SynapseStaccsCubeAnimator : MonoBehaviour
    {
        private static readonly int PropOwnerColor     = Shader.PropertyToID("_OwnerColor");
        private static readonly int PropThemeAccent    = Shader.PropertyToID("_ThemeAccent");
        private static readonly int PropStackZRatio    = Shader.PropertyToID("_StackZRatio");
        private static readonly int PropHazardWarning  = Shader.PropertyToID("_HazardWarningPulse");
        private static readonly int PropCantileverGlow = Shader.PropertyToID("_CantileverGlow");

        [Header("3-Face Isometric Hexagonal Cube Renderers (STACCS Topology)")]
        public Transform cubeRoot;
        public MeshRenderer topDiamondFaceRenderer;
        public MeshRenderer leftIsoFaceRenderer;
        public MeshRenderer rightIsoFaceRenderer;
        public Transform cantileverBridgeMesh;
        public Transform hazardWarningChevronRoot;

        [Header("Vertical Z-Stacking Geometry & Drop Physics (Z = 1..5)")]
        public float cubeLayerThicknessY = 0.28f;
        public float dropSpawnHeightOffset = 2.40f;
        public float baseDropDuration = 0.36f;
        public int maxStackHeight = 5;

        [Header("Acoustic Pitch Escalation (STACCS Stack Combo)")]
        public AudioSource stackDropAudioSource;
        public float basePitchSemitoneZero = 1.0f;
        public float semitoneStepPerZLayer = 2.0f; // +2 semitones per vertical stack layer

        [Header("Into the Breach Knockback & Bump Recoil")]
        public float bumpDisplacementDistance = 0.42f;
        public float bumpDuration = 0.24f;

        private MaterialPropertyBlock _mpb;
        private StaccsIsoCubeFaceData _faceData;

        // Active procedural animation state
        private bool _isDropping;
        private float _dropElapsed;
        private float _activeDropDuration;
        private float _targetRestHeightY;
        private float _startDropHeightY;

        private bool _isBumping;
        private float _bumpElapsed;
        private Vector3 _bumpDirectionWorld;
        private Vector3 _baseLocalPosition;
        private bool _resultsInCollisionDamage;

        private void Awake()
        {
            _mpb = new MaterialPropertyBlock();
            if (cubeRoot == null) cubeRoot = transform;
            _baseLocalPosition = cubeRoot.localPosition;
        }

        /// <summary>
        /// Configures the 3 isometric cube faces (TopDiamondFace, LeftIsoFace, RightIsoFace)
        /// for a given card and vertical stack height Z (1..5).
        /// </summary>
        public void BindIsoCubeFaces(StaccsIsoCubeFaceData data)
        {
            _faceData = data;
            int clampedZ = Mathf.Clamp(data.zStackIndex, 1, maxStackHeight);
            _targetRestHeightY = (clampedZ - 1) * cubeLayerThicknessY;

            Color ownerColor = (data.ownerId == 0)
                ? new Color(0.16f, 0.58f, 1.00f)  // Frontier Azure (P0)
                : new Color(0.96f, 0.22f, 0.28f); // Rival Crimson (P1)

            Color themeColor = ResolveThemeColor(data.themes);
            float zRatio = clampedZ / (float)maxStackHeight;

            ApplyFacePropertyBlock(topDiamondFaceRenderer, ownerColor, themeColor, zRatio, data.isTelegraphedHazardTarget);
            ApplyFacePropertyBlock(leftIsoFaceRenderer, themeColor, ownerColor, zRatio, data.isTelegraphedHazardTarget);
            ApplyFacePropertyBlock(rightIsoFaceRenderer, ownerColor, themeColor, zRatio, data.isTelegraphedHazardTarget);

            if (cantileverBridgeMesh != null)
            {
                cantileverBridgeMesh.gameObject.SetActive(data.hasCantileverOverhang && clampedZ > 1);
            }

            if (hazardWarningChevronRoot != null)
            {
                hazardWarningChevronRoot.gameObject.SetActive(data.isTelegraphedHazardTarget);
            }
        }

        /// <summary>
        /// Triggers the STACCS vertical Z-stack drop animation with cubic-bezier bounce
        /// and acoustic pitch escalation per stack height (Z = 1..5).
        /// </summary>
        public float AnimateStackDrop(int zIndex)
        {
            int clampedZ = Mathf.Clamp(zIndex, 1, maxStackHeight);
            _faceData.zStackIndex = clampedZ;
            _targetRestHeightY = (clampedZ - 1) * cubeLayerThicknessY;
            _startDropHeightY = _targetRestHeightY + dropSpawnHeightOffset + (clampedZ * 0.18f);
            _activeDropDuration = baseDropDuration + (clampedZ - 1) * 0.035f;
            _dropElapsed = 0f;
            _isDropping = true;

            if (cubeRoot != null)
            {
                Vector3 pos = _baseLocalPosition;
                pos.y = _startDropHeightY;
                cubeRoot.localPosition = pos;
            }

            float acousticPitch = ComputeStackAcousticPitch(clampedZ);
            if (stackDropAudioSource != null)
            {
                stackDropAudioSource.pitch = acousticPitch;
                stackDropAudioSource.Play();
            }

            return acousticPitch;
        }

        /// <summary>
        /// Computes the acoustic pitch multiplier for a vertical Z-stack drop (Z = 1..5)
        /// using equal-temperament semitone escalation: 2^(semitones / 12).
        /// </summary>
        public float ComputeStackAcousticPitch(int zIndex)
        {
            int clampedZ = Mathf.Clamp(zIndex, 1, maxStackHeight);
            float semitones = (clampedZ - 1) * semitoneStepPerZLayer;
            return basePitchSemitoneZero * Mathf.Pow(2f, semitones / 12f);
        }

        /// <summary>
        /// Evaluates a 3-segment cubic-bezier bounce curve for vertical cube-card drop impact.
        /// Returns 0 at start of drop, 1 at rest height, with crisp impact rebound.
        /// </summary>
        public static float EvaluateCubicBezierStackBounce(float t)
        {
            t = Mathf.Clamp01(t);
            if (t < 0.65f)
            {
                // Phase 1: Accelerated gravity drop (cubic bezier P0=0, P1=0.05, P2=0.85, P3=1.0)
                float u = t / 0.65f;
                return EvaluateCubicBezier1D(u, 0f, 0.05f, 0.85f, 1.0f);
            }
            else if (t < 0.86f)
            {
                // Phase 2: Crisp tactile rebound bounce above rest surface
                float u = (t - 0.65f) / 0.21f;
                float arc = 4f * u * (1f - u);
                return 1f - arc * 0.18f;
            }
            else
            {
                // Phase 3: Secondary micro-settle onto Z-stack
                float u = (t - 0.86f) / 0.14f;
                float arc = 4f * u * (1f - u);
                return 1f - arc * 0.04f;
            }
        }

        private static float EvaluateCubicBezier1D(float t, float p0, float p1, float p2, float p3)
        {
            float inv = 1f - t;
            return (inv * inv * inv * p0)
                 + (3f * inv * inv * t * p1)
                 + (3f * inv * t * t * p2)
                 + (t * t * t * p3);
        }

        /// <summary>
        /// Triggers an Into the Breach directional push/bump recoil animation along the isometric grid axes.
        /// </summary>
        public void TriggerDirectionalBumpRecoil(Vector2Int pushDirGrid, bool collisionDamage)
        {
            // Project 2D grid vector (dx, dy) into isometric world space
            Vector3 isoX = new Vector3(1f, 0f, -1f).normalized;
            Vector3 isoY = new Vector3(1f, 0f, 1f).normalized;
            _bumpDirectionWorld = (isoX * pushDirGrid.x + isoY * pushDirGrid.y).normalized;
            _resultsInCollisionDamage = collisionDamage;
            _bumpElapsed = 0f;
            _isBumping = true;
        }

        /// <summary>
        /// Advances vertical Z-stack drop bounce, directional push recoil, and hazard warning pulse.
        /// </summary>
        public void TickProceduralAnimation(float deltaTime)
        {
            if (cubeRoot == null) return;

            Vector3 currentPos = _baseLocalPosition;
            currentPos.y = _targetRestHeightY;

            if (_isDropping)
            {
                _dropElapsed += deltaTime;
                float normalizedT = _dropElapsed / Mathf.Max(0.05f, _activeDropDuration);
                if (normalizedT >= 1f)
                {
                    normalizedT = 1f;
                    _isDropping = false;
                }

                float bounceFactor = EvaluateCubicBezierStackBounce(normalizedT);
                currentPos.y = Mathf.Lerp(_startDropHeightY, _targetRestHeightY, bounceFactor);

                // Subtle squash-and-stretch on impact (t around 0.65)
                float impactProximity = 1f - Mathf.Clamp01(Mathf.Abs(normalizedT - 0.65f) / 0.08f);
                float squashY = 1f - impactProximity * 0.14f;
                float stretchXZ = 1f + impactProximity * 0.08f;
                cubeRoot.localScale = new Vector3(stretchXZ, squashY, stretchXZ);
            }
            else
            {
                cubeRoot.localScale = Vector3.Lerp(cubeRoot.localScale, Vector3.one, deltaTime * 16f);
            }

            if (_isBumping)
            {
                _bumpElapsed += deltaTime;
                float u = _bumpElapsed / Mathf.Max(0.05f, bumpDuration);
                if (u >= 1f)
                {
                    u = 1f;
                    _isBumping = false;
                }

                // Sharp impulse out and spring recoil back
                float recoilCurve = Mathf.Sin(u * Mathf.PI) * (1f - u * 0.35f);
                float amp = _resultsInCollisionDamage ? bumpDisplacementDistance * 1.25f : bumpDisplacementDistance;
                currentPos += _bumpDirectionWorld * (recoilCurve * amp);
            }

            cubeRoot.localPosition = currentPos;
        }

        private void ApplyFacePropertyBlock(
            MeshRenderer renderer,
            Color primaryColor,
            Color accentColor,
            float stackZRatio,
            bool hazardActive)
        {
            if (renderer == null) return;
            _mpb ??= new MaterialPropertyBlock();
            renderer.GetPropertyBlock(_mpb);
            _mpb.SetColor(PropOwnerColor, primaryColor);
            _mpb.SetColor(PropThemeAccent, accentColor);
            _mpb.SetFloat(PropStackZRatio, stackZRatio);
            _mpb.SetFloat(PropHazardWarning, hazardActive ? 1.0f : 0.0f);
            _mpb.SetFloat(PropCantileverGlow, _faceData.hasCantileverOverhang ? 1.0f : 0.0f);
            renderer.SetPropertyBlock(_mpb);
        }

        private static Color ResolveThemeColor(CardTheme themes)
        {
            foreach (var kv in SynapseCardAesthetics.FactionPalettes)
            {
                if ((themes & kv.Key) != 0)
                {
                    return kv.Value.glow;
                }
            }
            return new Color(0.42f, 0.78f, 1.00f);
        }
    }
}
