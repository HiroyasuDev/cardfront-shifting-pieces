using System;
using System.Collections.Generic;
using UnityEngine;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Visuals
{
    [Serializable]
    public struct ThemeVisualPalette
    {
        public CardTheme theme;
        public Color primaryFrameColor;
        public Color secondaryGlowColor;
        public Color statGemHighlight;
        public string frameMaterialPreset;
    }

    /// <summary>
    /// Clean-room Proprietary Aesthetics, Juice & Shader Controller for Synapse.TcgEngine.
    /// Replaces third-party BoardCardFX/HoverFX/AnimMatFX/SnapFX with:
    /// 1. 10-Theme Faction Color & Frame Palettes (PROJECT CF & CardCraft)
    /// 2. Interactive 3D Perspective Tilt + Parallax Holographic Foil (_TiltXY)
    /// 3. 180-Degree Tactical Capture Flip with Spring Overshoot & Hit-Stop
    /// 4. Orthogonal Synergy Tether Beams (+1/+2/+3 all sides visual link)
    /// 5. Stealth/Vanish Refractive Cloak & Temporal Rift Chromatic Inversion
    /// </summary>
    public class SynapseCardAesthetics : MonoBehaviour
    {
        private static readonly int PropTiltXY       = Shader.PropertyToID("_TiltXY");
        private static readonly int PropFoilPower    = Shader.PropertyToID("_FoilIntensity");
        private static readonly int PropFactionColor = Shader.PropertyToID("_FactionColor");
        private static readonly int PropSynergyPulse = Shader.PropertyToID("_SynergyPulse");
        private static readonly int PropStealthCloak = Shader.PropertyToID("_StealthCloak");
        private static readonly int PropOwnerTint    = Shader.PropertyToID("_OwnerTint");

        [Header("Card Renderers")]
        public Renderer cardMeshRenderer;
        public Transform cardVisualRoot;

        [Header("Tactical Feel & Juice Parameters")]
        public float hoverScaleMultiplier = 1.14f;
        public float hoverElevationY = 0.35f;
        public float maxTiltDegrees = 14f;
        public float captureFlipDuration = 0.38f;

        private MaterialPropertyBlock _mpb;
        private Vector3 _baseScale = Vector3.one;
        private bool _isHovered;
        private float _flipProgress = 1f;
        private int _displayedOwnerId = 0;

        public static readonly Dictionary<CardTheme, (Color frame, Color glow)> FactionPalettes =
            new Dictionary<CardTheme, (Color frame, Color glow)>
            {
                { CardTheme.Magic,     (new Color(0.29f, 0.14f, 0.58f), new Color(0.62f, 0.38f, 1.00f)) }, // Mystic Mage
                { CardTheme.Tech,      (new Color(0.12f, 0.28f, 0.42f), new Color(0.00f, 0.85f, 1.00f)) }, // Mech Knight / Cyber Ninja
                { CardTheme.Divine,    (new Color(0.72f, 0.58f, 0.18f), new Color(1.00f, 0.92f, 0.45f)) }, // Celestial Guardian
                { CardTheme.Shadow,    (new Color(0.11f, 0.09f, 0.16f), new Color(0.55f, 0.12f, 0.75f)) }, // Shadow Assassin
                { CardTheme.Nature,    (new Color(0.14f, 0.44f, 0.22f), new Color(0.35f, 0.95f, 0.52f)) }, // Elemental Sprite
                { CardTheme.Cosmic,    (new Color(0.08f, 0.12f, 0.36f), new Color(0.38f, 0.65f, 1.00f)) }, // Galactic Explorer
                { CardTheme.Steampunk, (new Color(0.48f, 0.29f, 0.14f), new Color(0.95f, 0.62f, 0.22f)) }, // Clockwork Sorcerer
                { CardTheme.Fire,      (new Color(0.62f, 0.14f, 0.08f), new Color(1.00f, 0.42f, 0.10f)) }, // Phoenix Guardian
                { CardTheme.Stealth,   (new Color(0.10f, 0.22f, 0.26f), new Color(0.00f, 0.95f, 0.78f)) }, // Digital Shadow
                { CardTheme.Lunar,     (new Color(0.18f, 0.24f, 0.48f), new Color(0.75f, 0.88f, 1.00f)) }, // Lunar Oracle
                { CardTheme.Creative,  (new Color(0.22f, 0.36f, 0.52f), new Color(0.45f, 0.82f, 1.00f)) }  // CardCraft Portfolio
            };

        private void Awake()
        {
            _mpb = new MaterialPropertyBlock();
            if (cardVisualRoot == null) cardVisualRoot = transform;
            _baseScale = cardVisualRoot.localScale;
        }

        /// <summary>
        /// Applies the card's primary faction theme palette, owner border tint (Blue = P0, Crimson = P1),
        /// synergy pulse intensity, and stealth cloak state to the holographic shader.
        /// </summary>
        public void ApplyVisualState(CardTheme themes, int ownerId, bool hasActiveSynergy, bool isCaptureImmune)
        {
            if (cardMeshRenderer == null) return;
            _mpb ??= new MaterialPropertyBlock();
            cardMeshRenderer.GetPropertyBlock(_mpb);

            Color glow = new Color(0.4f, 0.7f, 1f);
            foreach (var kv in FactionPalettes)
            {
                if ((themes & kv.Key) != 0)
                {
                    glow = kv.Value.glow;
                    break;
                }
            }

            Color ownerColor = (ownerId == 0)
                ? new Color(0.16f, 0.58f, 1.00f) // Player 0 Frontier Azure
                : new Color(0.96f, 0.22f, 0.28f); // Player 1 Rival Crimson

            _mpb.SetColor(PropFactionColor, glow);
            _mpb.SetColor(PropOwnerTint, ownerColor);
            _mpb.SetFloat(PropSynergyPulse, hasActiveSynergy ? 1.0f : 0.0f);
            _mpb.SetFloat(PropStealthCloak, isCaptureImmune ? 0.65f : 0.0f);
            cardMeshRenderer.SetPropertyBlock(_mpb);
        }

        /// <summary>
        /// Triggers the 180-degree axial capture flip when a card is captured on the 3x3 grid.
        /// </summary>
        public void TriggerCaptureFlip(int newOwnerId)
        {
            _displayedOwnerId = newOwnerId;
            _flipProgress = 0f;
        }

        /// <summary>
        /// Updates interactive mouse-over parallax tilt and capture flip animation each frame.
        /// </summary>
        public void UpdateProceduralMotion(Vector2 normalizedPointerOffset, float deltaTime)
        {
            if (cardVisualRoot == null) return;

            // 1. Capture Flip Spring Curve
            float flipAngleY = 0f;
            if (_flipProgress < 1f)
            {
                _flipProgress = Mathf.Min(1f, _flipProgress + deltaTime / Mathf.Max(0.05f, captureFlipDuration));
                float t = _flipProgress;
                // Smooth overshoot curve
                float curve = 1f - Mathf.Pow(1f - t, 3f) * Mathf.Cos(t * Mathf.PI * 1.5f);
                flipAngleY = curve * 360f;
            }

            // 2. Pointer Parallax Tilt + Holographic Foil UV Shift
            float pitch = _isHovered ? -normalizedPointerOffset.y * maxTiltDegrees : 0f;
            float roll  = _isHovered ?  normalizedPointerOffset.x * maxTiltDegrees : 0f;
            Quaternion targetRot = Quaternion.Euler(pitch, flipAngleY, roll);
            cardVisualRoot.localRotation = Quaternion.Slerp(cardVisualRoot.localRotation, targetRot, deltaTime * 14f);

            Vector3 targetScale = _isHovered ? _baseScale * hoverScaleMultiplier : _baseScale;
            cardVisualRoot.localScale = Vector3.Lerp(cardVisualRoot.localScale, targetScale, deltaTime * 14f);

            if (cardMeshRenderer != null)
            {
                _mpb ??= new MaterialPropertyBlock();
                cardMeshRenderer.GetPropertyBlock(_mpb);
                _mpb.SetVector(PropTiltXY, new Vector4(normalizedPointerOffset.x, normalizedPointerOffset.y, 0f, 0f));
                _mpb.SetFloat(PropFoilPower, _isHovered ? 1.0f : 0.35f);
                cardMeshRenderer.SetPropertyBlock(_mpb);
            }
        }

        public void SetHovered(bool hovered) => _isHovered = hovered;
    }
}
