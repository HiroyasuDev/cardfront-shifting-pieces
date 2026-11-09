Shader "Synapse/URP/SakugaImpactFrame"
{
    Properties
    {
        [MainTexture] _BaseMap ("Scene / Cut-In Source Texture", 2D) = "white" {}
        _ImpactCenterXY ("Impact Focal Origin UV (XY)", Vector) = (0.5, 0.44, 0, 0)
        _ImpactFramePhase ("2-Frame Sakuga Impact Phase (0=Off, 1=FrameA Black/White, 2=FrameB Inverted)", Range(0.0, 2.0)) = 1.0
        _LuminanceThreshold ("Binary Ink Luminance Threshold", Range(0.05, 0.95)) = 0.48
        _ThresholdFeather ("Ink Edge Anti-Alias Feather", Range(0.001, 0.15)) = 0.015
        _SpeedLineDensity ("Angular Speed-Line Spoke Count", Range(16.0, 180.0)) = 72.0
        _SpeedLineSharpness ("Speed-Line Spike Sharpness", Range(1.0, 32.0)) = 8.5
        _RadialDistortionStrength ("Polar UV Radial Zoom Distortion", Range(0.0, 0.35)) = 0.085
        _InnerSafeRadius ("Focal Core Safe Radius", Range(0.05, 0.65)) = 0.22
        _ChromAbOffset ("Impact Chromatic Aberration Split", Range(0.0, 0.04)) = 0.012
        _InkBlackColor ("Sakuga Sumi-Ink Black", Color) = (0.03, 0.03, 0.05, 1.0)
        _FlashWhiteColor ("Sakuga Impact Paper White", Color) = (0.98, 0.99, 1.0, 1.0)
        _AccentSlashColor ("Crimson/Cyan Energy Slash Accent", Color) = (1.0, 0.18, 0.33, 1.0)
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry+20"
        }
        LOD 250

        Pass
        {
            Name "SakugaImpactForward"
            Tags { "LightMode" = "UniversalForward" }

            Cull Off
            ZWrite Off
            ZTest Always

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.5

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _ImpactCenterXY;
                float _ImpactFramePhase;
                float _LuminanceThreshold;
                float _ThresholdFeather;
                float _SpeedLineDensity;
                float _SpeedLineSharpness;
                float _RadialDistortionStrength;
                float _InnerSafeRadius;
                float _ChromAbOffset;
                float4 _InkBlackColor;
                float4 _FlashWhiteColor;
                float4 _AccentSlashColor;
            CBUFFER_END

            // Deterministic hash for high-frequency anime speed-line spokes
            float Hash11(float p)
            {
                p = frac(p * 0.1031);
                p *= p + 33.33;
                p *= p + p;
                return frac(p);
            }

            Varyings vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);

                // Compute polar coordinates relative to the Sakuga impact focal origin
                float2 center = _ImpactCenterXY.xy;
                float2 delta = input.uv - center;
                float2 aspectDelta = float2(delta.x * 0.75, delta.y);
                float radius = length(aspectDelta);
                float angle = atan2(aspectDelta.y, aspectDelta.x); // [-PI, PI]

                // Angular speed-line spike pattern in polar space
                float normAngle = (angle + 3.14159265) / 6.2831853;
                float spokeIndex = floor(normAngle * _SpeedLineDensity);
                float spokeFract = frac(normAngle * _SpeedLineDensity);
                float spokeShape = 1.0 - abs(spokeFract * 2.0 - 1.0);
                float spokeNoise = Hash11(spokeIndex + floor(_Time.y * 24.0) * 0.17);
                float spikeReach = _InnerSafeRadius + spokeNoise * 0.38;
                float radialMask = smoothstep(spikeReach, spikeReach + 0.18, radius);
                float speedLineSpike = pow(saturate(spokeShape), _SpeedLineSharpness) * radialMask;

                // Polar UV radial zoom distortion along active speed lines
                float2 radialDir = (radius > 1e-5) ? (delta / radius) : float2(0.0, 0.0);
                float impactWeight = saturate(_ImpactFramePhase);
                float2 distortedUV = saturate(
                    input.uv - radialDir * (speedLineSpike * _RadialDistortionStrength * impactWeight)
                );

                // Sample RGB with radial chromatic aberration split
                float2 caShift = radialDir * (_ChromAbOffset * impactWeight);
                half rChan = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, saturate(distortedUV + caShift)).r;
                half gChan = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, distortedUV).g;
                half bChan = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, saturate(distortedUV - caShift)).b;
                half3 baseRGB = half3(rChan, gChan, bChan);

                // Luminance & binary Sakuga ink threshold
                half lum = dot(baseRGB, half3(0.299h, 0.587h, 0.114h));
                half combinedSignal = lum + (half)(speedLineSpike * 0.55) - (half)((1.0 - radialMask) * 0.15);
                half binaryMask = smoothstep(
                    (half)(_LuminanceThreshold - _ThresholdFeather),
                    (half)(_LuminanceThreshold + _ThresholdFeather),
                    combinedSignal
                );

                // 2-Frame Sakuga Polarity Inversion:
                // Frame 1 (_ImpactFramePhase ~ 1.0): Paper-white flash core with sumi-ink black speed lines
                // Frame 2 (_ImpactFramePhase ~ 2.0): Inverted sumi-ink silhouette with white energy spokes
                half invertFlag = saturate((half)(_ImpactFramePhase - 1.0));
                half effectiveMask = lerp(binaryMask, 1.0h - binaryMask, invertFlag);

                // Diagonal impact slash highlight through the focal origin
                float slashCoord = abs((delta.x * 0.82 + delta.y * 0.57)) - 0.018 * (1.0 - radius);
                half slashMask = (half)(1.0 - smoothstep(0.0, 0.012, slashCoord)) * (half)smoothstep(0.65, 0.05, radius);

                half3 sakugaRGB = lerp(_InkBlackColor.rgb, _FlashWhiteColor.rgb, effectiveMask);
                sakugaRGB = lerp(sakugaRGB, _AccentSlashColor.rgb, slashMask * 0.85h);

                half3 finalRGB = lerp(baseRGB, sakugaRGB, saturate((half)_ImpactFramePhase));
                return half4(finalRGB, 1.0h);
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
