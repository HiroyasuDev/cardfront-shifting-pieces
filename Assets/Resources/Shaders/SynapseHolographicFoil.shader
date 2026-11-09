Shader "Synapse/URP/HolographicFoil"
{
    Properties
    {
        [MainTexture] _BaseMap ("Card Portrait Albedo (RGB) Alpha (A)", 2D) = "white" {}
        [MainColor] _BaseColor ("Base Color Tint", Color) = (1, 1, 1, 1)
        _FrameTex ("Tactical Bezel & Compass Overlay", 2D) = "black" {}
        _FoilMask ("Holographic Foil Mask (R=Foil, G=Filigree, B=Rim)", 2D) = "white" {}
        [Normal] _FoilNormalMap ("Micro-Groove Foil Normal Map", 2D) = "bump" {}
        _FactionColor ("Faction Chroma Rim (Mythic/Legendary)", Color) = (0.0, 0.898, 1.0, 1.0)
        _OwnerTint ("Owner Control Border (Azure/Crimson)", Color) = (0.16, 0.58, 1.0, 1.0)
        _TiltXY ("Interactive Parallax Tilt XY", Vector) = (0, 0, 0, 0)
        _AnisotropyDirection ("Anisotropic Tangent Direction", Vector) = (0.7071, 0.7071, 0, 0)
        _GratingFrequency ("Diffraction Grating Spatial Frequency", Range(1.0, 32.0)) = 12.0
        _FoilIntensity ("Holographic Diffraction Intensity", Range(0.0, 3.0)) = 1.15
        _GlintSharpness ("Specular Foil Glint Exponent", Range(4.0, 128.0)) = 42.0
        _RimPower ("Faction Chroma Rim Fresnel Power", Range(0.5, 8.0)) = 2.6
        _SynergyPulse ("Active Synergy Resonance Pulse", Range(0.0, 1.0)) = 0.0
        _StealthCloak ("Optical Camo Cloak Alpha", Range(0.0, 1.0)) = 0.0
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
            "IgnoreProjector" = "True"
        }
        LOD 300

        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }

            Blend SrcAlpha OneMinusSrcAlpha
            Cull Off
            ZWrite On

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.5
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float4 tangentOS  : TANGENT;
                float2 uv         : TEXCOORD0;
                float4 color      : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS  : SV_POSITION;
                float2 uv          : TEXCOORD0;
                float3 positionWS  : TEXCOORD1;
                float3 normalWS    : TEXCOORD2;
                float3 tangentWS   : TEXCOORD3;
                float3 bitangentWS : TEXCOORD4;
                float4 color       : TEXCOORD5;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);
            TEXTURE2D(_FrameTex);
            SAMPLER(sampler_FrameTex);
            TEXTURE2D(_FoilMask);
            SAMPLER(sampler_FoilMask);
            TEXTURE2D(_FoilNormalMap);
            SAMPLER(sampler_FoilNormalMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseColor;
                float4 _FactionColor;
                float4 _OwnerTint;
                float4 _TiltXY;
                float4 _AnisotropyDirection;
                float _GratingFrequency;
                float _FoilIntensity;
                float _GlintSharpness;
                float _RimPower;
                float _SynergyPulse;
                float _StealthCloak;
            CBUFFER_END

            // 6-band spectral cosine diffraction (first-order rainbow dispersion)
            half3 SpectralRainbowDiffraction(half phase)
            {
                half3 shift = half3(0.0h, 0.3333h, 0.6667h);
                return 0.5h + 0.5h * cos(6.2831853h * (phase + shift));
            }

            Varyings vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                VertexPositionInputs posInputs = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normInputs = GetVertexNormalInputs(input.normalOS, input.tangentOS);

                output.positionCS = posInputs.positionCS;
                output.positionWS = posInputs.positionWS;
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.normalWS = normInputs.normalWS;
                output.tangentWS = normInputs.tangentWS;
                output.bitangentWS = normInputs.bitangentWS;
                output.color = input.color;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);

                float3 viewDirWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
                Light mainLight = GetMainLight();
                float3 lightDirWS = normalize(mainLight.direction + float3(_TiltXY.xy * 0.65, 0.25));
                float3 halfDirWS = normalize(lightDirWS + viewDirWS);

                // Parallax-shifted portrait UV
                float2 parallaxUV = saturate(input.uv + _TiltXY.xy * 0.028);
                half4 baseSample = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, parallaxUV) * _BaseColor;
                half4 frameSample = SAMPLE_TEXTURE2D(_FrameTex, sampler_FrameTex, input.uv);
                half3 foilMasks = SAMPLE_TEXTURE2D(_FoilMask, sampler_FoilMask, input.uv).rgb;

                // Unpack tangent-space foil micro-groove normal
                half3 normalTS = UnpackNormal(SAMPLE_TEXTURE2D(_FoilNormalMap, sampler_FoilNormalMap, input.uv * 2.0));
                float3x3 tbn = float3x3(
                    normalize(input.tangentWS),
                    normalize(input.bitangentWS),
                    normalize(input.normalWS)
                );
                float3 perturbedNormalWS = normalize(mul(normalTS, tbn));

                // Kajiya-Kay anisotropic tangent ribbon along card filigree
                float2 anisoDir2D = normalize(_AnisotropyDirection.xy + 1e-4);
                float3 anisoTangentWS = normalize(
                    input.tangentWS * anisoDir2D.x +
                    input.bitangentWS * anisoDir2D.y +
                    perturbedNormalWS * 0.25
                );
                float tDotH = dot(anisoTangentWS, halfDirWS);
                float sinTH = sqrt(max(0.001, 1.0 - tDotH * tDotH));
                float anisoGlint = pow(sinTH, _GlintSharpness) * (0.35 + 0.65 * foilMasks.g);

                // Anisotropic rainbow diffraction grating phase
                float gratingCoord = dot(input.uv, anisoDir2D * _GratingFrequency);
                float viewAngleShift = dot(viewDirWS, perturbedNormalWS) * 1.85 + (_TiltXY.x - _TiltXY.y) * 2.75;
                half diffractionPhase = (half)(gratingCoord + viewAngleShift + _Time.y * 0.38);
                half3 rainbowFoil = SpectralRainbowDiffraction(diffractionPhase);

                half foilWeight = saturate(foilMasks.r + foilMasks.g * 0.5);
                half3 foilContribution = rainbowFoil * foilWeight * _FoilIntensity * (0.45h + (half)anisoGlint);

                // Faction Chroma Rim (Fresnel + Mythic/Legendary border resonance)
                float ndotv = saturate(dot(perturbedNormalWS, viewDirWS));
                float fresnelRim = pow(1.0 - ndotv, _RimPower);
                float2 edgeDist = min(input.uv, 1.0 - input.uv);
                float borderMask = smoothstep(0.065, 0.014, min(edgeDist.x, edgeDist.y));
                float synergyOsc = 0.65 + 0.35 * sin(_Time.y * 5.2);
                half3 rimChroma = lerp(_OwnerTint.rgb, _FactionColor.rgb * 1.45h, saturate(_SynergyPulse * (half)synergyOsc + (half)fresnelRim * 0.7h));
                half3 rimEmission = rimChroma * (half)max(borderMask, fresnelRim * foilMasks.b * 0.85);

                half3 compositedRGB = lerp(baseSample.rgb + foilContribution, frameSample.rgb, frameSample.a) + rimEmission;
                half finalAlpha = baseSample.a * lerp(1.0h, 0.42h, (half)_StealthCloak);
                return half4(compositedRGB, finalAlpha);
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
