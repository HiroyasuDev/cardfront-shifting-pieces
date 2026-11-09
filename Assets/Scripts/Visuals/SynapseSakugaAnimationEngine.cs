using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Tools;

namespace Synapse.TcgEngine.Visuals
{
    /// <summary>
    /// 120Hz analytical / semi-implicit damped harmonic spring evaluator for card physics,
    /// camera recoil, and 3D pawn hover damping.
    /// </summary>
    [Serializable]
    public struct SpringSample1D
    {
        public float position;
        public float velocity;
        public float target;
        public float stiffness;
        public float damping;
        public float mass;
        public float zeta;
    }

    /// <summary>
    /// 3D vector state sample for 120Hz damped harmonic spring evaluation.
    /// </summary>
    [Serializable]
    public struct SpringSampleVector3
    {
        public Vector3 position;
        public Vector3 velocity;
        public Vector3 target;
        public float stiffness;
        public float damping;
        public float mass;
        public float zeta;
    }

    /// <summary>
    /// Clean-room 120Hz damped harmonic spring solver supporting under-damped (zeta &lt; 1),
    /// critically-damped (zeta == 1), and over-damped (zeta &gt; 1) regimes.
    /// </summary>
    public static class SynapseSpringHarmonicSolver
    {
        public const float DefaultPhysicsHz = 120.0f;
        public const float FixedDeltaTime120Hz = 1.0f / DefaultPhysicsHz;
        private const float EquilibriumPosEpsilon = 0.00001f;
        private const float EquilibriumVelEpsilon = 0.0001f;

        /// <summary>
        /// Computes the dimensionless damping ratio zeta = c / (2 * sqrt(k * m)).
        /// </summary>
        public static float CalculateDampingRatioZeta(float stiffness, float damping, float mass = 1.0f)
        {
            float safeStiffness = Mathf.Max(0.0001f, stiffness);
            float safeMass = Mathf.Max(0.0001f, mass);
            float safeDamping = Mathf.Max(0.0f, damping);
            return safeDamping / (2.0f * Mathf.Sqrt(safeStiffness * safeMass));
        }

        /// <summary>
        /// Evaluates a 1D damped harmonic oscillator at 120Hz sub-stepping.
        /// Updates <paramref name="velocity"/> in-place and returns the new position.
        /// </summary>
        public static float EvaluateSpring1D(
            float currentPos,
            ref float velocity,
            float targetPos,
            float stiffness,
            float damping,
            float mass = 1.0f,
            float deltaTime = FixedDeltaTime120Hz)
        {
            SpringSample1D sample = EvaluateSpring1D(
                currentPos,
                velocity,
                targetPos,
                stiffness,
                damping,
                mass,
                deltaTime);
            velocity = sample.velocity;
            return sample.position;
        }

        /// <summary>
        /// Pure functional overload of 1D damped spring evaluation returning position, velocity, and zeta.
        /// </summary>
        public static SpringSample1D EvaluateSpring1D(
            float currentPos,
            float currentVelocity,
            float targetPos,
            float stiffness,
            float damping,
            float mass = 1.0f,
            float deltaTime = FixedDeltaTime120Hz)
        {
            float k = Mathf.Max(0.0001f, stiffness);
            float m = Mathf.Max(0.0001f, mass);
            float c = Mathf.Max(0.0f, damping);
            float zeta = CalculateDampingRatioZeta(k, c, m);
            float dtTotal = Mathf.Max(0.0f, deltaTime);

            if (dtTotal <= 0.0f)
            {
                return new SpringSample1D
                {
                    position = currentPos,
                    velocity = currentVelocity,
                    target = targetPos,
                    stiffness = k,
                    damping = c,
                    mass = m,
                    zeta = zeta
                };
            }

            float pos = currentPos;
            float vel = currentVelocity;
            int subSteps = Mathf.Clamp(Mathf.CeilToInt(dtTotal / FixedDeltaTime120Hz), 1, 240);
            float stepDt = dtTotal / subSteps;

            for (int i = 0; i < subSteps; i++)
            {
                float displacement = pos - targetPos;
                float springForce = -k * displacement;
                float dampingForce = -c * vel;
                float acceleration = (springForce + dampingForce) / m;

                // Semi-implicit symplectic Euler integration at 120Hz+
                vel += acceleration * stepDt;
                pos += vel * stepDt;
            }

            if (Mathf.Abs(pos - targetPos) < EquilibriumPosEpsilon && Mathf.Abs(vel) < EquilibriumVelEpsilon)
            {
                pos = targetPos;
                vel = 0.0f;
            }

            return new SpringSample1D
            {
                position = pos,
                velocity = vel,
                target = targetPos,
                stiffness = k,
                damping = c,
                mass = m,
                zeta = zeta
            };
        }

        /// <summary>
        /// Evaluates a 3D Vector3 damped harmonic oscillator at 120Hz sub-stepping.
        /// Updates <paramref name="velocity"/> in-place and returns the new 3D position.
        /// </summary>
        public static Vector3 EvaluateSpringVector3(
            Vector3 currentPos,
            ref Vector3 velocity,
            Vector3 targetPos,
            float stiffness,
            float damping,
            float mass = 1.0f,
            float deltaTime = FixedDeltaTime120Hz)
        {
            SpringSampleVector3 sample = EvaluateSpringVector3(
                currentPos,
                velocity,
                targetPos,
                stiffness,
                damping,
                mass,
                deltaTime);
            velocity = sample.velocity;
            return sample.position;
        }

        /// <summary>
        /// Pure functional overload of 3D Vector3 damped spring evaluation returning position, velocity, and zeta.
        /// </summary>
        public static SpringSampleVector3 EvaluateSpringVector3(
            Vector3 currentPos,
            Vector3 currentVelocity,
            Vector3 targetPos,
            float stiffness,
            float damping,
            float mass = 1.0f,
            float deltaTime = FixedDeltaTime120Hz)
        {
            SpringSample1D sx = EvaluateSpring1D(currentPos.x, currentVelocity.x, targetPos.x, stiffness, damping, mass, deltaTime);
            SpringSample1D sy = EvaluateSpring1D(currentPos.y, currentVelocity.y, targetPos.y, stiffness, damping, mass, deltaTime);
            SpringSample1D sz = EvaluateSpring1D(currentPos.z, currentVelocity.z, targetPos.z, stiffness, damping, mass, deltaTime);

            return new SpringSampleVector3
            {
                position = new Vector3(sx.position, sy.position, sz.position),
                velocity = new Vector3(sx.velocity, sy.velocity, sz.velocity),
                target = targetPos,
                stiffness = sx.stiffness,
                damping = sx.damping,
                mass = sx.mass,
                zeta = sx.zeta
            };
        }
    }

    /// <summary>
    /// 12fps (On-Twos) / 24fps (On-Ones) stepped anime cadence evaluator for CARDFRONT: Cradle of Echoes.
    /// Quantizes continuous engine time into discrete hand-drawn keyframe holds, Obake smear blitzes,
    /// and 2-frame B&amp;W impact flash pulses.
    /// </summary>
    public static class SynapseSakugaSteppedCurve
    {
        public const int DefaultOnTwosFps = 12;
        public const int DefaultOnOnesFps = 24;
        public const int DefaultImpactHitStopFps = 60;

        /// <summary>
        /// Quantizes continuous time in seconds to a stepped anime frame grid (e.g., 12fps On-Twos or 24fps On-Ones).
        /// </summary>
        public static float QuantizeSakugaTime(float timeSeconds, int sakugaFps = DefaultOnTwosFps)
        {
            int safeFps = Mathf.Clamp(sakugaFps, 1, 240);
            float safeTime = Mathf.Max(0.0f, timeSeconds);
            return Mathf.Floor(safeTime * safeFps) / safeFps;
        }

        /// <summary>
        /// Overload accepting floating-point cadence rate.
        /// </summary>
        public static float QuantizeSakugaTime(float timeSeconds, float sakugaFps)
        {
            float safeFps = Mathf.Clamp(sakugaFps, 1.0f, 240.0f);
            float safeTime = Mathf.Max(0.0f, timeSeconds);
            return Mathf.Floor(safeTime * safeFps) / safeFps;
        }

        /// <summary>
        /// Evaluates a stepped Sakuga directional clash lunge curve over normalized time [0, 1]:
        /// - Phase 1 [0.00 .. anticipationEnd): Gen-ga wind-up anticipation pullback (-0.28f hold).
        /// - Phase 2 [anticipationEnd .. impactPeak): Obake smear blitz forward to +1.12f impact apex.
        /// - Phase 3 [impactPeak .. 1.00]: Hit-stop lock at 1.0f followed by Kagenashi recoil back to 0.0f.
        /// </summary>
        public static float EvaluateClashLungeCurve(
            float normalizedTime,
            int sakugaFps = DefaultOnTwosFps,
            float anticipationEnd = 0.24f,
            float impactPeak = 0.50f)
        {
            float clampedT = Mathf.Clamp01(normalizedTime);
            float steppedT = QuantizeSakugaTime(clampedT, Mathf.Max(1, sakugaFps));
            float aEnd = Mathf.Clamp(anticipationEnd, 0.05f, 0.40f);
            float iPeak = Mathf.Clamp(impactPeak, aEnd + 0.05f, 0.85f);

            if (steppedT < aEnd)
            {
                float u = steppedT / aEnd;
                // Coiled pullback to -0.28
                return -0.28f * Mathf.Sin(u * Mathf.PI * 0.5f);
            }

            if (steppedT < iPeak)
            {
                float u = (steppedT - aEnd) / (iPeak - aEnd);
                // Explosive sawtooth Obake rush from -0.28 to +1.12 overshoot
                float fastSnap = 1.0f - Mathf.Pow(1.0f - u, 3.0f);
                return Mathf.Lerp(-0.28f, 1.12f, fastSnap);
            }

            float recoverySpan = 1.0f - iPeak;
            if (recoverySpan <= 0.0001f)
            {
                return 0.0f;
            }

            float r = (clampedT - iPeak) / recoverySpan;
            if (r < 0.18f)
            {
                // 2-frame hit-stop plateau at contact point
                return 1.0f;
            }

            float settleU = (r - 0.18f) / 0.82f;
            return Mathf.Lerp(1.0f, 0.0f, settleU * settleU * (3.0f - 2.0f * settleU));
        }

        /// <summary>
        /// Evaluates the 2-frame monochromatic impact flash stencil alpha in [0, 1].
        /// Returns 1.0f during the active impact frame window and decays rapidly to 0.0f outside.
        /// </summary>
        public static float EvaluateImpactFlashAlpha(
            float timeSeconds,
            float impactStartSeconds = 0.20f,
            int flashFrameCount = 2,
            int hitStopFps = DefaultImpactHitStopFps)
        {
            int safeFps = Mathf.Max(1, hitStopFps);
            int safeFrames = Mathf.Max(1, flashFrameCount);
            float flashDuration = (float)safeFrames / safeFps;
            float elapsed = timeSeconds - impactStartSeconds;

            if (elapsed < 0.0f)
            {
                return 0.0f;
            }

            if (elapsed <= flashDuration)
            {
                // Crisp alternating strobe peak on frame 0 and frame 1
                int frameIdx = Mathf.FloorToInt(elapsed * safeFps);
                return (frameIdx % 2 == 0) ? 1.0f : 0.88f;
            }

            float fadeOutWindow = flashDuration * 1.5f;
            if (elapsed <= flashDuration + fadeOutWindow)
            {
                float u = (elapsed - flashDuration) / Mathf.Max(0.0001f, fadeOutWindow);
                return Mathf.Clamp01(1.0f - u);
            }

            return 0.0f;
        }
    }

    /// <summary>
    /// Enumeration of the 4 canonical 2.5D card puppet joints controlled by <see cref="SynapseFabrikBoneChain2D"/>.
    /// </summary>
    public enum SynapsePuppetJointId
    {
        Torso = 0,
        Head = 1,
        WeaponArm = 2,
        Cape = 3
    }

    /// <summary>
    /// Represents a single 2D joint in a card portrait's 2.5D skeletal puppet rig.
    /// </summary>
    [Serializable]
    public struct FabrikPuppetJoint2D
    {
        public SynapsePuppetJointId jointId;
        public string jointName;
        public Vector2 position;
        public float boneLength;
    }

    /// <summary>
    /// 2D Forward And Backward Reaching Inverse Kinematics (FABRIK) solver for 2.5D card puppet joints
    /// (<c>Head</c>, <c>Torso</c>, <c>WeaponArm</c>, <c>Cape</c>) plus 4-layer depth parallax offset evaluation.
    /// </summary>
    public static class SynapseFabrikBoneChain2D
    {
        public const int ParallaxLayerCount = 4;

        // Canonical 4-layer parallax depth weights:
        // Layer 0: Deep Stage Background (-0.35)
        // Layer 1: Midground Faction Sigil / Halo (-0.12)
        // Layer 2: Hero / Mecha Subject (+0.45)
        // Layer 3: Foreground Weapon Slash & Frame Filigree (+1.00)
        private static readonly float[] DefaultLayerDepthWeights = new float[ParallaxLayerCount]
        {
            -0.35f,
            -0.12f,
            0.45f,
            1.00f
        };

        /// <summary>
        /// Creates the canonical 4-joint 2.5D card puppet rig (<c>Torso</c>, <c>Head</c>, <c>WeaponArm</c>, <c>Cape</c>).
        /// </summary>
        public static FabrikPuppetJoint2D[] CreateCanonicalCardPuppetJoints(Vector2 torsoOrigin)
        {
            return new FabrikPuppetJoint2D[4]
            {
                new FabrikPuppetJoint2D
                {
                    jointId = SynapsePuppetJointId.Torso,
                    jointName = "Torso",
                    position = torsoOrigin,
                    boneLength = 42.0f
                },
                new FabrikPuppetJoint2D
                {
                    jointId = SynapsePuppetJointId.Head,
                    jointName = "Head",
                    position = torsoOrigin + new Vector2(0.0f, 42.0f),
                    boneLength = 48.0f
                },
                new FabrikPuppetJoint2D
                {
                    jointId = SynapsePuppetJointId.WeaponArm,
                    jointName = "WeaponArm",
                    position = torsoOrigin + new Vector2(48.0f, 42.0f),
                    boneLength = 54.0f
                },
                new FabrikPuppetJoint2D
                {
                    jointId = SynapsePuppetJointId.Cape,
                    jointName = "Cape",
                    position = torsoOrigin + new Vector2(48.0f, -12.0f),
                    boneLength = 0.0f
                }
            };
        }

        /// <summary>
        /// Solves 2D Forward And Backward Reaching Inverse Kinematics (FABRIK) in-place for an arbitrary
        /// chain of 2D joint positions and segment lengths toward <paramref name="targetPosition"/>.
        /// Returns the final distance between the end-effector and <paramref name="targetPosition"/>.
        /// </summary>
        public static float SolveFabrik2D(
            IList<Vector2> jointPositions,
            IList<float> boneLengths,
            Vector2 targetPosition,
            int maxIterations = 10,
            float tolerance = 0.001f)
        {
            if (jointPositions == null || jointPositions.Count == 0)
            {
                return 0.0f;
            }

            int n = jointPositions.Count;
            if (n == 1)
            {
                return Vector2.Distance(jointPositions[0], targetPosition);
            }

            float[] lengths = new float[n - 1];
            float totalReach = 0.0f;
            for (int i = 0; i < n - 1; i++)
            {
                float segLen = (boneLengths != null && i < boneLengths.Count && boneLengths[i] > 0.0001f)
                    ? boneLengths[i]
                    : Vector2.Distance(jointPositions[i], jointPositions[i + 1]);
                lengths[i] = Mathf.Max(0.0001f, segLen);
                totalReach += lengths[i];
            }

            Vector2 rootOrigin = jointPositions[0];
            float rootToTargetDist = Vector2.Distance(rootOrigin, targetPosition);

            // Unreachable target: stretch chain collinearly along root -> target ray
            if (rootToTargetDist >= totalReach)
            {
                Vector2 dir = (rootToTargetDist > 0.00001f)
                    ? (targetPosition - rootOrigin) / rootToTargetDist
                    : Vector2.right;
                jointPositions[0] = rootOrigin;
                for (int i = 0; i < n - 1; i++)
                {
                    jointPositions[i + 1] = jointPositions[i] + dir * lengths[i];
                }
                return Vector2.Distance(jointPositions[n - 1], targetPosition);
            }

            int safeIterations = Mathf.Clamp(maxIterations, 1, 64);
            float safeTolerance = Mathf.Max(0.00001f, tolerance);

            for (int iter = 0; iter < safeIterations; iter++)
            {
                float currentError = Vector2.Distance(jointPositions[n - 1], targetPosition);
                if (currentError <= safeTolerance)
                {
                    break;
                }

                // Stage 1: Forward reaching (from end-effector back to root)
                jointPositions[n - 1] = targetPosition;
                for (int i = n - 2; i >= 0; i--)
                {
                    Vector2 delta = jointPositions[i] - jointPositions[i + 1];
                    float dist = delta.magnitude;
                    Vector2 dir = (dist > 0.00001f) ? (delta / dist) : Vector2.up;
                    jointPositions[i] = jointPositions[i + 1] + dir * lengths[i];
                }

                // Stage 2: Backward reaching (from fixed root out to end-effector)
                jointPositions[0] = rootOrigin;
                for (int i = 0; i < n - 1; i++)
                {
                    Vector2 delta = jointPositions[i + 1] - jointPositions[i];
                    float dist = delta.magnitude;
                    Vector2 dir = (dist > 0.00001f) ? (delta / dist) : Vector2.right;
                    jointPositions[i + 1] = jointPositions[i] + dir * lengths[i];
                }
            }

            return Vector2.Distance(jointPositions[n - 1], targetPosition);
        }

        /// <summary>
        /// Overload solving 2D FABRIK directly on a <see cref="FabrikPuppetJoint2D"/> array (<c>Torso</c>, <c>Head</c>, <c>WeaponArm</c>, <c>Cape</c>).
        /// </summary>
        public static float SolveFabrik2D(
            FabrikPuppetJoint2D[] puppetJoints,
            Vector2 targetPosition,
            int maxIterations = 10,
            float tolerance = 0.001f)
        {
            if (puppetJoints == null || puppetJoints.Length == 0)
            {
                return 0.0f;
            }

            int count = puppetJoints.Length;
            var positions = new Vector2[count];
            var lengths = new float[Mathf.Max(1, count - 1)];

            for (int i = 0; i < count; i++)
            {
                positions[i] = puppetJoints[i].position;
                if (i < count - 1)
                {
                    lengths[i] = puppetJoints[i].boneLength > 0.0001f
                        ? puppetJoints[i].boneLength
                        : Vector2.Distance(puppetJoints[i].position, puppetJoints[i + 1].position);
                }
            }

            float err = SolveFabrik2D(positions, lengths, targetPosition, maxIterations, tolerance);
            for (int i = 0; i < count; i++)
            {
                puppetJoints[i].position = positions[i];
            }

            return err;
        }

        /// <summary>
        /// Evaluates the 2D parallax UV/pixel offset for one of the 4 depth layers (0..3) given normalized pointer/gyro tilt.
        /// </summary>
        public static Vector2 EvaluateParallaxLayerOffset(
            int layerIndex,
            Vector2 normalizedTilt,
            float maxDisplacementPixels = 18.0f)
        {
            int clampedLayer = Mathf.Clamp(layerIndex, 0, ParallaxLayerCount - 1);
            Vector2 clampedTilt = new Vector2(
                Mathf.Clamp(normalizedTilt.x, -1.0f, 1.0f),
                Mathf.Clamp(normalizedTilt.y, -1.0f, 1.0f));
            float depthWeight = DefaultLayerDepthWeights[clampedLayer];
            return clampedTilt * (maxDisplacementPixels * depthWeight);
        }

        /// <summary>
        /// Evaluates all 4 depth layers' parallax offsets simultaneously for a 600x800 2.5D card portrait.
        /// </summary>
        public static Vector2[] EvaluateAllParallaxLayerOffsets(Vector2 normalizedTilt, float maxDisplacementPixels = 18.0f)
        {
            var offsets = new Vector2[ParallaxLayerCount];
            for (int i = 0; i < ParallaxLayerCount; i++)
            {
                offsets[i] = EvaluateParallaxLayerOffset(i, normalizedTilt, maxDisplacementPixels);
            }
            return offsets;
        }
    }

    /// <summary>
    /// Serializable keyframe entry inside a <c>.cfanim</c> sovereign animation clip.
    /// </summary>
    [Serializable]
    public struct CfAnimKeyframe
    {
        public int frame_index;
        public float time_sec;
        public Vector3 position;
        public Vector3 rotation_euler;
        public Vector3 scale;
        public float alpha;
        public string interpolation;
    }

    /// <summary>
    /// Serializable frame-accurate event marker (VFX, SFX foley stem, camera hit-stop, damage tick) inside a <c>.cfanim</c> clip.
    /// </summary>
    [Serializable]
    public struct CfAnimEvent
    {
        public string event_id;
        public float time_sec;
        public int frame_index;
        public string payload;
    }

    /// <summary>
    /// Serializable representation of CARDFRONT <c>.cfanim</c> animation clip assets with
    /// deterministic FNV-1a 64-bit integrity checksum verification.
    /// </summary>
    [Serializable]
    public class CfAnimClipAsset
    {
        public const ulong Fnv1a64OffsetBasis = 14695981039346656037UL;
        public const ulong Fnv1a64Prime = 1099511628211UL;

        public string clip_id = string.Empty;
        public float duration_sec = 0.50f;
        public int physics_hz = 120;
        public int sakuga_fps = 12;
        public string fnv1a_64_checksum = string.Empty;
        public List<CfAnimKeyframe> keyframes = new List<CfAnimKeyframe>();
        public List<CfAnimEvent> events = new List<CfAnimEvent>();

        /// <summary>
        /// Computes a 64-bit FNV-1a digest formatted as a 16-character lowercase hexadecimal string.
        /// </summary>
        public static string ComputeFnv1a64Hex(string canonicalText)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(canonicalText ?? string.Empty);
            ulong hash = Fnv1a64OffsetBasis;
            for (int i = 0; i < bytes.Length; i++)
            {
                hash ^= bytes[i];
                hash *= Fnv1a64Prime;
            }
            return hash.ToString("x16", CultureInfo.InvariantCulture);
        }

        /// <summary>
        /// Builds the deterministic canonical payload string from clip metadata, keyframes, and events.
        /// </summary>
        public string BuildCanonicalDigestPayload()
        {
            var sb = new StringBuilder(256);
            sb.Append(clip_id ?? string.Empty).Append('|');
            sb.AppendFormat(CultureInfo.InvariantCulture, "{0:F4}|", duration_sec);
            sb.Append(physics_hz).Append('|');
            sb.Append(sakuga_fps).Append('|');
            sb.Append(keyframes != null ? keyframes.Count : 0).Append('|');
            sb.Append(events != null ? events.Count : 0);

            if (keyframes != null)
            {
                for (int i = 0; i < keyframes.Count; i++)
                {
                    CfAnimKeyframe kf = keyframes[i];
                    sb.AppendFormat(
                        CultureInfo.InvariantCulture,
                        "|KF:{0}:{1:F4}:{2:F3},{3:F3},{4:F3}",
                        kf.frame_index,
                        kf.time_sec,
                        kf.position.x,
                        kf.position.y,
                        kf.position.z);
                }
            }

            if (events != null)
            {
                for (int i = 0; i < events.Count; i++)
                {
                    CfAnimEvent ev = events[i];
                    sb.AppendFormat(
                        CultureInfo.InvariantCulture,
                        "|EV:{0}:{1:F4}:{2}",
                        ev.event_id ?? string.Empty,
                        ev.time_sec,
                        ev.frame_index);
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Recomputes and stamps <see cref="fnv1a_64_checksum"/> from the clip's canonical payload.
        /// </summary>
        public string SealChecksum()
        {
            fnv1a_64_checksum = ComputeFnv1a64Hex(BuildCanonicalDigestPayload());
            return fnv1a_64_checksum;
        }

        /// <summary>
        /// Verifies the clip's <see cref="fnv1a_64_checksum"/> against its canonical FNV-1a 64-bit hash,
        /// or validates an explicit 16-hex-character FNV-1a 64-bit digest.
        /// </summary>
        public bool VerifyChecksum(string expectedPayloadOverride = null)
        {
            if (string.IsNullOrEmpty(fnv1a_64_checksum) || fnv1a_64_checksum.Length != 16)
            {
                return false;
            }

            for (int i = 0; i < 16; i++)
            {
                char c = fnv1a_64_checksum[i];
                bool isHex = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
                if (!isHex)
                {
                    return false;
                }
            }

            if (!string.IsNullOrEmpty(expectedPayloadOverride))
            {
                string overrideDigest = ComputeFnv1a64Hex(expectedPayloadOverride);
                return string.Equals(fnv1a_64_checksum, overrideDigest, StringComparison.OrdinalIgnoreCase);
            }

            string canonicalDigest = ComputeFnv1a64Hex(BuildCanonicalDigestPayload());
            return string.Equals(fnv1a_64_checksum, canonicalDigest, StringComparison.OrdinalIgnoreCase);
        }
    }

    /// <summary>
    /// Evaluated 3D transform pose and shader telemetry for a <c>.glb</c> / <c>.q3gs</c> tactical miniature pawn.
    /// </summary>
    [Serializable]
    public struct PawnKinematicPose3D
    {
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 eulerAngles;
        public Vector3 scale;
        public float shockwaveRingRadius;
        public float emissiveSurgeIntensity;
    }

    /// <summary>
    /// Procedural 3D miniature kinematics evaluator for watertight <c>.glb</c> and Quad-3DGS <c>.q3gs</c> pawns
    /// on the 3x3 CARDFRONT tactical grid.
    /// </summary>
    public static class SynapsePawnKinematics3D
    {
        /// <summary>
        /// 1. Evaluates an orbital deployment slam from <paramref name="orbitalDropHeight"/> onto <paramref name="boardTilePos"/>,
        /// with squash-and-stretch compression at impact and radial shockwave ring expansion.
        /// </summary>
        public static PawnKinematicPose3D EvaluateDeployOrbitalSlam(
            Vector3 boardTilePos,
            float normalizedTime,
            float orbitalDropHeight = 4.20f)
        {
            float t = Mathf.Clamp01(normalizedTime);
            const float impactTime = 0.52f;

            Vector3 pos = boardTilePos;
            Vector3 scale = Vector3.one;
            float pitchDeg = 0.0f;
            float shockwaveRadius = 0.0f;
            float emissive = 0.0f;

            if (t < impactTime)
            {
                float u = t / impactTime;
                // High-gravity cubic drop acceleration
                float dropProgress = u * u * u;
                pos.y = boardTilePos.y + Mathf.Max(0.1f, orbitalDropHeight) * (1.0f - dropProgress);
                // Vertical elongation during orbital descent
                scale = new Vector3(1.0f - 0.14f * u, 1.0f + 0.28f * u, 1.0f - 0.14f * u);
                pitchDeg = 12.0f * (1.0f - u);
                emissive = 0.35f * u;
            }
            else
            {
                float u = (t - impactTime) / (1.0f - impactTime);
                // Impact squash at u == 0 followed by damped harmonic settle to Vector3.one
                float dampedBounce = Mathf.Exp(-6.0f * u) * Mathf.Cos(u * Mathf.PI * 2.5f);
                scale = new Vector3(
                    1.0f + 0.22f * dampedBounce,
                    1.0f - 0.26f * dampedBounce,
                    1.0f + 0.22f * dampedBounce);
                shockwaveRadius = Mathf.Lerp(0.15f, 2.40f, 1.0f - Mathf.Pow(1.0f - u, 2.0f));
                emissive = Mathf.Clamp01(1.0f - u * 1.4f);
            }

            Vector3 euler = new Vector3(pitchDeg, 0.0f, 0.0f);
            return new PawnKinematicPose3D
            {
                position = pos,
                rotation = Quaternion.Euler(euler),
                eulerAngles = euler,
                scale = scale,
                shockwaveRingRadius = shockwaveRadius,
                emissiveSurgeIntensity = emissive
            };
        }

        /// <summary>
        /// 2. Evaluates a directional clash lunge along <paramref name="attackDirection"/> using stepped Sakuga timing,
        /// anticipatory wind-up tilt, and Obake smear stretch at contact.
        /// </summary>
        public static PawnKinematicPose3D EvaluateDirectionalClashLunge(
            Vector3 originPos,
            Vector3 attackDirection,
            float normalizedTime,
            float lungeDistance = 0.68f,
            int sakugaFps = 12)
        {
            Vector3 dir = attackDirection.sqrMagnitude > 0.0001f
                ? attackDirection.normalized
                : Vector3.forward;

            float curveVal = SynapseSakugaSteppedCurve.EvaluateClashLungeCurve(normalizedTime, sakugaFps);
            Vector3 displacedPos = originPos + dir * (curveVal * lungeDistance);

            // Pitch forward during lunge (+24 deg), pitch backward during anticipation (-16 deg)
            float pitchDeg = curveVal >= 0.0f ? (curveVal * 24.0f) : (curveVal * 55.0f);
            Vector3 euler = new Vector3(pitchDeg * dir.z, 0.0f, -pitchDeg * dir.x);

            float stretch = Mathf.Max(0.0f, curveVal) * 0.20f;
            Vector3 scale = new Vector3(
                1.0f + Mathf.Abs(dir.x) * stretch - Mathf.Abs(dir.z) * (stretch * 0.4f),
                1.0f - stretch * 0.35f,
                1.0f + Mathf.Abs(dir.z) * stretch - Mathf.Abs(dir.x) * (stretch * 0.4f));

            return new PawnKinematicPose3D
            {
                position = displacedPos,
                rotation = Quaternion.Euler(euler),
                eulerAngles = euler,
                scale = scale,
                shockwaveRingRadius = curveVal > 0.90f ? 1.15f : 0.0f,
                emissiveSurgeIntensity = Mathf.Clamp01(curveVal)
            };
        }

        /// <summary>
        /// 3. Evaluates a 180-degree card/pawn ownership capture flip with parabolic hop apex and settle bounce.
        /// </summary>
        public static PawnKinematicPose3D EvaluateCaptureFlip180(
            Vector3 boardTilePos,
            float normalizedTime,
            float hopApexHeight = 1.35f,
            float initialYawDeg = 0.0f)
        {
            float t = Mathf.Clamp01(normalizedTime);
            // Parabolic vertical arc 4 * h * t * (1 - t)
            float verticalLift = 4.0f * Mathf.Max(0.1f, hopApexHeight) * t * (1.0f - t);
            Vector3 pos = new Vector3(boardTilePos.x, boardTilePos.y + verticalLift, boardTilePos.z);

            // Smooth S-curve 180-degree flip around Z/roll and Y/yaw
            float smoothT = t * t * (3.0f - 2.0f * t);
            float flipAngleDeg = 180.0f * smoothT;
            Vector3 euler = new Vector3(0.0f, initialYawDeg + flipAngleDeg, flipAngleDeg);

            float apexScaleBoost = 1.0f + 0.14f * Mathf.Sin(t * Mathf.PI);
            return new PawnKinematicPose3D
            {
                position = pos,
                rotation = Quaternion.Euler(euler),
                eulerAngles = euler,
                scale = Vector3.one * apexScaleBoost,
                shockwaveRingRadius = (t > 0.85f) ? ((t - 0.85f) / 0.15f) * 1.25f : 0.0f,
                emissiveSurgeIntensity = Mathf.Sin(t * Mathf.PI)
            };
        }

        /// <summary>
        /// 4. Evaluates a tactical tile-to-tile slide with aerodynamic roll/bank angle proportional to velocity.
        /// </summary>
        public static PawnKinematicPose3D EvaluateTacticalSlideBank(
            Vector3 fromTilePos,
            Vector3 toTilePos,
            float normalizedTime,
            float maxBankAngleDeg = 18.0f)
        {
            float t = Mathf.Clamp01(normalizedTime);
            float smoothT = t * t * (3.0f - 2.0f * t);
            Vector3 pos = Vector3.Lerp(fromTilePos, toTilePos, smoothT);
            // Subtle hover glide lift during transit
            pos.y += 0.18f * Mathf.Sin(t * Mathf.PI);

            Vector3 travelDir = (toTilePos - fromTilePos);
            if (travelDir.sqrMagnitude > 0.0001f)
            {
                travelDir.Normalize();
            }

            // Derivative of smoothstep peaks at t = 0.5: 6 * t * (1 - t)
            float velocityProfile = 4.0f * t * (1.0f - t);
            float bankDeg = maxBankAngleDeg * velocityProfile;
            Vector3 euler = new Vector3(travelDir.z * bankDeg, 0.0f, -travelDir.x * bankDeg);

            return new PawnKinematicPose3D
            {
                position = pos,
                rotation = Quaternion.Euler(euler),
                eulerAngles = euler,
                scale = Vector3.one,
                shockwaveRingRadius = 0.0f,
                emissiveSurgeIntensity = 0.25f * velocityProfile
            };
        }

        /// <summary>
        /// 5. Evaluates a Column Die resonance surge (1..6 pip power) elevating and pulsing the pawn in that column.
        /// </summary>
        public static PawnKinematicPose3D EvaluateColumnDieSurge(
            Vector3 pawnBasePos,
            int dieFaceValue,
            float normalizedTime,
            float maxHoverElevation = 0.60f)
        {
            int clampedPips = Mathf.Clamp(dieFaceValue, 1, 6);
            float pipRatio = clampedPips / 6.0f;
            float t = Mathf.Clamp01(normalizedTime);

            float surgeEnvelope = Mathf.Sin(t * Mathf.PI);
            float hoverY = maxHoverElevation * pipRatio * surgeEnvelope;
            Vector3 pos = new Vector3(pawnBasePos.x, pawnBasePos.y + hoverY, pawnBasePos.z);

            float spinYawDeg = 360.0f * t * (clampedPips >= 5 ? 1.0f : 0.0f);
            Vector3 euler = new Vector3(0.0f, spinYawDeg, 0.0f);
            float uniformScale = 1.0f + (0.18f * pipRatio * surgeEnvelope);

            return new PawnKinematicPose3D
            {
                position = pos,
                rotation = Quaternion.Euler(euler),
                eulerAngles = euler,
                scale = Vector3.one * uniformScale,
                shockwaveRingRadius = 1.60f * pipRatio * surgeEnvelope,
                emissiveSurgeIntensity = pipRatio * surgeEnvelope
            };
        }
    }

    /// <summary>
    /// Active timeline track instance scheduled inside <see cref="SynapseSakugaAnimationEngine"/>.
    /// </summary>
    [Serializable]
    public sealed class ScheduledSakugaTrack
    {
        public string trackId;
        public CfAnimClipAsset clip;
        public float currentTimeSec;
        public float quantizedTimeSec;
        public bool isCompleted;
        public Action<float> onSampleTime;
        public Action<CfAnimEvent> onEventFired;
        public Action onCompleted;
        public readonly HashSet<int> firedEventIndices = new HashSet<int>();
    }

    /// <summary>
    /// Deterministic 120Hz timeline scheduler and <c>.cfanim</c> clip runtime for CARDFRONT: Cradle of Echoes.
    /// Integrates directly with <see cref="SynapseResolveQueue"/> so AI lookahead rollouts can call
    /// <see cref="InstantResolveAll"/> with zero frame latency while client presentation steps at 120Hz.
    /// </summary>
    public class SynapseSakugaAnimationEngine
    {
        public const float FixedStepHz = 120.0f;
        public const float FixedStepDeltaSec = 1.0f / FixedStepHz;

        private readonly List<ScheduledSakugaTrack> _activeTracks = new List<ScheduledSakugaTrack>();
        private float _accumulatorSec;
        private int _totalFixedStepsExecuted;
        private float _timelineCursorSec;

        public int ActiveTrackCount => _activeTracks.Count;
        public int TotalFixedStepsExecuted => _totalFixedStepsExecuted;
        public float TimelineCursorSec => _timelineCursorSec;

        /// <summary>
        /// Schedules a <see cref="CfAnimClipAsset"/> on the deterministic timeline and optionally registers
        /// its duration delay on a <see cref="SynapseResolveQueue"/>.
        /// </summary>
        public ScheduledSakugaTrack ScheduleClip(
            CfAnimClipAsset clip,
            SynapseResolveQueue resolveQueue = null,
            Action<float> onSampleTime = null,
            Action<CfAnimEvent> onEventFired = null,
            Action onCompleted = null)
        {
            if (clip == null)
            {
                return null;
            }

            var track = new ScheduledSakugaTrack
            {
                trackId = string.IsNullOrEmpty(clip.clip_id) ? "cfanim_default" : clip.clip_id,
                clip = clip,
                currentTimeSec = 0.0f,
                quantizedTimeSec = 0.0f,
                isCompleted = false,
                onSampleTime = onSampleTime,
                onEventFired = onEventFired,
                onCompleted = onCompleted
            };

            _activeTracks.Add(track);
            if (resolveQueue != null && clip.duration_sec > 0.0f)
            {
                resolveQueue.SetDelay(clip.duration_sec);
            }

            EvaluateTrackAtTime(track, 0.0f);
            return track;
        }

        /// <summary>
        /// Advances the animation timeline by fixed 120Hz sub-steps (<c>dt = 1/120s</c>).
        /// Returns the number of 120Hz steps executed during this call.
        /// </summary>
        public int StepFixed120Hz(float deltaTimeSec = FixedStepDeltaSec, SynapseResolveQueue resolveQueue = null)
        {
            float safeDt = Mathf.Max(0.0f, deltaTimeSec);
            _accumulatorSec += safeDt;
            int stepsRun = 0;

            while (_accumulatorSec + 0.000001f >= FixedStepDeltaSec)
            {
                _accumulatorSec -= FixedStepDeltaSec;
                if (_accumulatorSec < 0.0f)
                {
                    _accumulatorSec = 0.0f;
                }

                _timelineCursorSec += FixedStepDeltaSec;
                _totalFixedStepsExecuted++;
                stepsRun++;

                for (int i = 0; i < _activeTracks.Count; i++)
                {
                    ScheduledSakugaTrack track = _activeTracks[i];
                    if (track == null || track.isCompleted)
                    {
                        continue;
                    }

                    float nextTime = track.currentTimeSec + FixedStepDeltaSec;
                    EvaluateTrackAtTime(track, nextTime);
                }

                resolveQueue?.Tick(FixedStepDeltaSec);
            }

            PruneCompletedTracks();
            return stepsRun;
        }

        /// <summary>
        /// Deterministically scrubs all active tracks (and timeline cursor) to an exact timestamp in seconds.
        /// Supports forward and backward scrubbing for replay verification and frame inspection.
        /// </summary>
        public void ScrubToTime(float targetTimeSec)
        {
            float clampedTarget = Mathf.Max(0.0f, targetTimeSec);
            _timelineCursorSec = clampedTarget;
            _accumulatorSec = 0.0f;

            for (int i = 0; i < _activeTracks.Count; i++)
            {
                ScheduledSakugaTrack track = _activeTracks[i];
                if (track == null || track.clip == null)
                {
                    continue;
                }

                if (clampedTarget < track.currentTimeSec)
                {
                    track.firedEventIndices.Clear();
                    track.isCompleted = false;
                }

                EvaluateTrackAtTime(track, clampedTarget);
            }
        }

        /// <summary>
        /// Immediately resolves all active animation clips, fires all pending frame events in chronological order,
        /// invokes completion callbacks, and drains <paramref name="resolveQueue"/> synchronously.
        /// Used by <see cref="SynapseResolveQueue"/> AI lookahead search and headless simulation tests.
        /// </summary>
        public int InstantResolveAll(SynapseResolveQueue resolveQueue = null)
        {
            int resolvedCount = 0;

            for (int i = 0; i < _activeTracks.Count; i++)
            {
                ScheduledSakugaTrack track = _activeTracks[i];
                if (track == null || track.isCompleted)
                {
                    continue;
                }

                float duration = (track.clip != null && track.clip.duration_sec > 0.0f)
                    ? track.clip.duration_sec
                    : 0.0f;
                EvaluateTrackAtTime(track, duration);
                if (!track.isCompleted)
                {
                    track.isCompleted = true;
                    track.onCompleted?.Invoke();
                }
                resolvedCount++;
            }

            _activeTracks.Clear();
            _accumulatorSec = 0.0f;

            if (resolveQueue != null)
            {
                resolveQueue.Tick(9999.0f);
                resolveQueue.DrainAll();
            }

            return resolvedCount;
        }

        /// <summary>
        /// Evaluates a single track at <paramref name="timeSec"/>, quantizing to its Sakuga FPS cadence and firing events.
        /// </summary>
        private static void EvaluateTrackAtTime(ScheduledSakugaTrack track, float timeSec)
        {
            if (track == null || track.clip == null)
            {
                return;
            }

            float duration = Mathf.Max(0.0001f, track.clip.duration_sec);
            float clampedTime = Mathf.Clamp(timeSec, 0.0f, duration);
            int fps = track.clip.sakuga_fps > 0 ? track.clip.sakuga_fps : SynapseSakugaSteppedCurve.DefaultOnTwosFps;

            track.currentTimeSec = clampedTime;
            track.quantizedTimeSec = SynapseSakugaSteppedCurve.QuantizeSakugaTime(clampedTime, fps);
            track.onSampleTime?.Invoke(track.quantizedTimeSec);

            if (track.clip.events != null)
            {
                for (int i = 0; i < track.clip.events.Count; i++)
                {
                    CfAnimEvent ev = track.clip.events[i];
                    if (clampedTime + 0.00001f >= ev.time_sec && !track.firedEventIndices.Contains(i))
                    {
                        track.firedEventIndices.Add(i);
                        track.onEventFired?.Invoke(ev);
                    }
                }
            }

            if (clampedTime + 0.00001f >= duration && !track.isCompleted)
            {
                track.isCompleted = true;
                track.onCompleted?.Invoke();
            }
        }

        private void PruneCompletedTracks()
        {
            for (int i = _activeTracks.Count - 1; i >= 0; i--)
            {
                if (_activeTracks[i] == null || _activeTracks[i].isCompleted)
                {
                    _activeTracks.RemoveAt(i);
                }
            }
        }
    }
}
