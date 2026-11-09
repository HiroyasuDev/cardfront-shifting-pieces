Shader "Synapse/URP/AetherCelOutline"
{
    Properties
    {
        [MainTexture] _BaseMap ("Delighted Albedo Portrait / Model Texture", 2D) = "white" {}
        [MainColor] _BaseColor ("Base Albedo Tint", Color) = (1, 1, 1, 1)
        _CelRampTex ("2-Band Anime Cel Ramp Lookup", 2D) = "white" {}
        _DepthParallaxMap ("4-Layer 2.5D Depth Map (R=BG, G=Mid, B=Char, A=FG)", 2D) = "gray" {}
        [Normal] _BumpMap ("Tangent-Space Normal Map", 2D) = "bump" {}
        _ShadowThreshold ("Cel Terminator Threshold", Range(-0.5, 0.8)) = 0.08
        _ShadowSmoothness ("Cel Terminator Step Smoothness", Range(0.001, 0.25)) = 0.025
        _ShadowTint ("2-Band Anime Shadow Tint (Nocturna Indigo)", Color) = (0.14, 0.11, 0.28, 1.0)
        _RimColor ("Aether Astral Rim Highlight", Color) = (0.0, 0.898, 1.0, 1.0)
        _RimThreshold ("Cel Rim Light Threshold", Range(0.1, 0.95)) = 0.68
        _ParallaxLayerScales ("4-Layer 2.5D Parallax Scales (BG, Mid, Char, FG)", Vector) = (-0.012, 0.006, 0.022, 0.040)
        _ViewTiltXY ("2.5D Camera / Card Tilt XY", Vector) = (0, 0, 0, 0)
        _OutlineColor ("Inverted-Hull Sumi-Ink Outline Color", Color) = (0.04, 0.03, 0.07, 1.0)
        _OutlineWidth ("Inverted-Hull Ink Outline Width (Object Units)", Range(0.0, 0.05)) = 0.0065
        _OutlineZOffset ("Outline Depth Bias Z-Offset", Range(-0.05, 0.05)) = 0.001
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }
        LOD 300

        // =====================================================================
        // PASS 1: 2-Band Anime Cel Shading + 4-Layer 2.5D Depth Parallax
        // =====================================================================
        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }

            Cull Back
            ZWrite On
            ZTest LEqual

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.5
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
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
            TEXTURE2D(_CelRampTex);
            SAMPLER(sampler_CelRampTex);
            TEXTURE2D(_DepthParallaxMap);
            SAMPLER(sampler_DepthParallaxMap);
            TEXTURE2D(_BumpMap);
            SAMPLER(sampler_BumpMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseColor;
                float _ShadowThreshold;
                float _ShadowSmoothness;
                float4 _ShadowTint;
                float4 _RimColor;
                float _RimThreshold;
                float4 _ParallaxLayerScales;
                float4 _ViewTiltXY;
                float4 _OutlineColor;
                float _OutlineWidth;
                float _OutlineZOffset;
            CBUFFER_END

            // 4-Layer 2.5D Depth Parallax UV Displacement
            float2 Compute4LayerParallaxUV(float2 uv, float2 tiltXY)
            {
                half4 layerWeights = SAMPLE_TEXTURE2D(_DepthParallaxMap, sampler_DepthParallaxMap, uv);
                float totalShift =
                    layerWeights.r * _ParallaxLayerScales.x +
                    layerWeights.g * _ParallaxLayerScales.y +
                    layerWeights.b * _ParallaxLayerScales.z +
                    layerWeights.a * _ParallaxLayerScales.w;

                // Secondary iterative refinement for foreground crest/weapon layer
                float2 shiftedUV = uv + tiltXY * totalShift;
                half fgRefine = SAMPLE_TEXTURE2D(_DepthParallaxMap, sampler_DepthParallaxMap, saturate(shiftedUV)).a;
                shiftedUV += tiltXY * (fgRefine * _ParallaxLayerScales.w * 0.35);
                return saturate(shiftedUV);
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
                float2 tiltXY = _ViewTiltXY.xy + viewDirWS.xy * 0.35;

                // 4-layer 2.5D parallax-displaced UV
                float2 parallaxUV = Compute4LayerParallaxUV(input.uv, tiltXY);
                half4 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, parallaxUV) * _BaseColor;

                // Tangent-space normal map perturbation
                half3 normalTS = UnpackNormal(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, parallaxUV));
                float3x3 tbn = float3x3(
                    normalize(input.tangentWS),
                    normalize(input.bitangentWS),
                    normalize(input.normalWS)
                );
                float3 normalWS = normalize(mul(normalTS, tbn));

                // Main directional light & 2-band anime cel terminator
                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                Light mainLight = GetMainLight(shadowCoord);
                float ndotl = dot(normalWS, normalize(mainLight.direction));
                float halfLambert = ndotl * 0.5 + 0.5;

                float celBand = smoothstep(
                    _ShadowThreshold - _ShadowSmoothness,
                    _ShadowThreshold + _ShadowSmoothness,
                    ndotl
                ) * mainLight.shadowAttenuation;

                half3 rampSample = SAMPLE_TEXTURE2D(_CelRampTex, sampler_CelRampTex, float2(saturate(halfLambert), 0.5)).rgb;
                half3 litColor = albedo.rgb * mainLight.color;
                half3 shadowColor = albedo.rgb * _ShadowTint.rgb * mainLight.color;
                half3 celShaded = lerp(shadowColor, litColor, (half)celBand) * rampSample;

                // Crisp anime rim light on lit silhouette edges
                float ndotv = saturate(dot(normalWS, viewDirWS));
                float rimFactor = (1.0 - ndotv) * saturate(ndotl + 0.35);
                half rimStep = (half)smoothstep(_RimThreshold - 0.03, _RimThreshold + 0.03, rimFactor);
                celShaded += _RimColor.rgb * rimStep * _RimColor.a;

                return half4(celShaded, albedo.a);
            }
            ENDHLSL
        }

        // =====================================================================
        // PASS 2: Inverted-Hull Sumi-Ink Silhouette Outline
        // =====================================================================
        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "SRPDefaultUnlit" }

            Cull Front
            ZWrite On
            ZTest LEqual

            HLSLPROGRAM
            #pragma vertex vertOutline
            #pragma fragment fragOutline
            #pragma target 3.5
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float4 color      : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseColor;
                float _ShadowThreshold;
                float _ShadowSmoothness;
                float4 _ShadowTint;
                float4 _RimColor;
                float _RimThreshold;
                float4 _ParallaxLayerScales;
                float4 _ViewTiltXY;
                float4 _OutlineColor;
                float _OutlineWidth;
                float _OutlineZOffset;
            CBUFFER_END

            Varyings vertOutline(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                // Tapered brush-pressure outline width modulated by vertex color alpha
                float brushWeight = lerp(0.65, 1.25, input.color.a);
                float3 normOS = normalize(input.normalOS);
                float3 extrudedOS = input.positionOS.xyz + normOS * (_OutlineWidth * brushWeight);

                float4 posCS = TransformObjectToHClip(extrudedOS);
                posCS.z += _OutlineZOffset * posCS.w;
                output.positionCS = posCS;
                return output;
            }

            half4 fragOutline(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return _OutlineColor;
            }
            ENDHLSL
        }

        // =====================================================================
        // PASS 3: URP ShadowCaster Pass
        // =====================================================================
        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }

            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull Back

            HLSLPROGRAM
            #pragma vertex vertShadow
            #pragma fragment fragShadow
            #pragma target 3.5
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings vertShadow(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 fragShadow(Varyings input) : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
