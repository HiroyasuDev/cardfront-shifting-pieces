Shader "Synapse/TcgEngine/HoloTacticalCard"
{
    Properties
    {
        _MainTex ("Card Portrait Art", 2D) = "white" {}
        _FrameTex ("Tactical Bezel & Compass Overlay", 2D) = "black" {}
        _FoilMask ("Holographic Foil Mask", 2D) = "white" {}
        _FactionColor ("Faction Synergy Glow", Color) = (0.2, 0.7, 1.0, 1.0)
        _OwnerTint ("Owner Control Border (Azure/Crimson)", Color) = (0.16, 0.58, 1.0, 1.0)
        _TiltXY ("Parallax Tilt XY", Vector) = (0, 0, 0, 0)
        _FoilIntensity ("Foil Iridescence Intensity", Range(0, 2)) = 0.5
        _SynergyPulse ("Active Synergy Pulse", Range(0, 1)) = 0.0
        _StealthCloak ("Vanish / TechnoStealth Cloak", Range(0, 1)) = 0.0
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 200
        Blend SrcAlpha OneMinusSrcAlpha
        Cull Off

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;
            sampler2D _FrameTex;
            sampler2D _FoilMask;
            float4 _FactionColor;
            float4 _OwnerTint;
            float4 _TiltXY;
            float _FoilIntensity;
            float _SynergyPulse;
            float _StealthCloak;

            float3 SpectralIridescence(float t)
            {
                return 0.5 + 0.5 * cos(6.28318 * (t + float3(0.0, 0.33, 0.67)));
            }

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                // Parallax-shifted portrait UV
                float2 parallaxUv = i.uv + _TiltXY.xy * 0.025;
                fixed4 art = tex2D(_MainTex, saturate(parallaxUv));
                fixed4 frame = tex2D(_FrameTex, i.uv);
                float foilMask = tex2D(_FoilMask, i.uv).r;

                // Rainbow holographic foil grating driven by tilt + UV diagonal
                float phase = dot(i.uv, float2(1.7, 2.3)) + (_TiltXY.x - _TiltXY.y) * 2.5 + _Time.y * 0.4;
                float3 foilColor = SpectralIridescence(phase) * foilMask * _FoilIntensity * 0.45;

                // Border distance for Owner Control Rim & Synergy Pulse
                float2 edgeDist = min(i.uv, 1.0 - i.uv);
                float borderMask = smoothstep(0.06, 0.015, min(edgeDist.x, edgeDist.y));
                float pulse = 0.65 + 0.35 * sin(_Time.y * 5.0);
                float3 borderGlow = lerp(_OwnerTint.rgb, _FactionColor.rgb * 1.5, _SynergyPulse * pulse) * borderMask;

                float3 finalRgb = lerp(art.rgb + foilColor, frame.rgb, frame.a) + borderGlow;
                float alpha = lerp(1.0, 0.42, _StealthCloak); // Semi-transparent refractive cloak when Vanish/TechnoStealth active
                return fixed4(finalRgb, alpha);
            }
            ENDCG
        }
    }
}
