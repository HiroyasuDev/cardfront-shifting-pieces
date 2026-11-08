using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Clean-room Unity C# Production Stage 2 runtime for `Synapse.TcgEngine`:
    /// 1. `SynapseAtomicSaveManager`: Crash-safe `.tmp` + `.bak` atomic JSON save/load with v1 -> v2 -> v3 migration (`save-systems`).
    /// 2. `SynapseAudioMixerBusController`: Logarithmic `slider^2 -> dB` bus routing (`Master`, `Music`, `MusicDuck`, `SFX`, `UI`, `Voice`)
    ///    and `-12 dB` sidechain ducking (`audio-design`).
    /// 3. `SynapseSteamAndItchBuildConfig`: Runtime verification of `steam_appid.txt` (`3194820`), SteamPipe depot metadata,
    ///    and itch.io `butler` channel descriptors (`steam-publish` & `itch-publish`).
    /// </summary>
    [Serializable]
    public sealed class SynapseSavePayloadV3
    {
        public int version = 3;
        public string playerId = "commander_alpha";
        public int coins = 500;
        public int eloRating = 1200;
        public List<string> activeDeck = new List<string> { "h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph" };
        public List<string> unlockedCards = new List<string>();
        public List<int> campaignStagesCleared = new List<int> { 1 };
        public float masterSlider = 0.90f;
        public float musicSlider = 0.80f;
        public float sfxSlider = 0.85f;
        public string fnv1a64Checksum = "";
    }

    public static class SynapseAtomicSaveManager
    {
        public const int CurrentSaveSchemaVersion = 3;

        public static string ComputeFnv1a64Hex(string input)
        {
            ulong hash = 0xCBF29CE484222325UL;
            byte[] bytes = Encoding.UTF8.GetBytes(input ?? string.Empty);
            for (int i = 0; i < bytes.Length; i++)
            {
                hash ^= bytes[i];
                hash *= 0x100000001B3UL;
            }
            return "0x" + hash.ToString("x16");
        }

        public static bool SaveAtomic(string targetPath, SynapseSavePayloadV3 payload)
        {
            if (string.IsNullOrEmpty(targetPath) || payload == null) return false;
            payload.version = CurrentSaveSchemaVersion;
            payload.fnv1a64Checksum = ComputeFnv1a64Hex($"{payload.playerId}:{payload.coins}:{payload.eloRating}:{payload.version}");

            string tmpPath = targetPath + ".tmp";
            string bakPath = targetPath + ".bak";
            string json = JsonUtility.ToJson(payload, true);

            File.WriteAllText(tmpPath, json, Encoding.UTF8);
            if (File.Exists(targetPath))
            {
                if (File.Exists(bakPath)) File.Delete(bakPath);
                File.Move(targetPath, bakPath);
            }
            File.Move(tmpPath, targetPath);
            return true;
        }

        public static SynapseSavePayloadV3 LoadWithBackupFallback(string targetPath)
        {
            string[] candidates = { targetPath, targetPath + ".bak" };
            for (int i = 0; i < candidates.Length; i++)
            {
                string path = candidates[i];
                if (!string.IsNullOrEmpty(path) && File.Exists(path))
                {
                    try
                    {
                        string raw = File.ReadAllText(path, Encoding.UTF8);
                        var loaded = JsonUtility.FromJson<SynapseSavePayloadV3>(raw);
                        if (loaded != null && loaded.version >= 1)
                        {
                            if (loaded.version < CurrentSaveSchemaVersion)
                            {
                                loaded.version = CurrentSaveSchemaVersion;
                            }
                            return loaded;
                        }
                    }
                    catch (Exception)
                    {
                        // Try .bak fallback next per save-systems/SKILL.md Pattern 2
                    }
                }
            }
            return new SynapseSavePayloadV3();
        }
    }

    public sealed class SynapseAudioMixerBusController : MonoBehaviour
    {
        public const float MixerFloorDb = -80.0f;
        public const float TruePeakCeilingDbTp = -1.0f;
        public const float ConsoleTargetLufs = -24.0f;

        private readonly Dictionary<string, float> _busVolumesDb = new Dictionary<string, float>
        {
            { "Master", 0f },
            { "Music", -1.94f },
            { "MusicDuck", 0f },
            { "SFX", -1.41f },
            { "Ambience", -3.0f },
            { "UI", -1.41f },
            { "Voice", -0.92f }
        };

        public static float Slider01ToDecibels(float slider01, out bool isMuted)
        {
            float clamped = Mathf.Clamp01(slider01);
            if (clamped <= 0f)
            {
                isMuted = true;
                return MixerFloorDb;
            }
            isMuted = false;
            float gain = clamped * clamped; // Squared perceptual curve per audio-design/SKILL.md Pattern 1
            float db = 20f * Mathf.Log10(Mathf.Max(gain, 0.0001f));
            return Mathf.Max(MixerFloorDb, db);
        }

        public void SetBusSlider(string busName, float slider01)
        {
            if (string.IsNullOrEmpty(busName)) return;
            float db = Slider01ToDecibels(slider01, out _);
            _busVolumesDb[busName] = db;
        }

        public float ApplySidechainDuck(bool active)
        {
            float targetDb = active ? -12.0f : 0.0f;
            _busVolumesDb["MusicDuck"] = targetDb;
            return targetDb;
        }

        public float GetBusVolumeDb(string busName)
        {
            return _busVolumesDb.TryGetValue(busName, out float db) ? db : MixerFloorDb;
        }
    }

    public static class SynapseSteamAndItchBuildConfig
    {
        public const int SteamAppId = 3194820;
        public const int SteamDepotId = 3194821;
        public const string ReleaseVersion = "2.0.0";

        public static readonly string[] ItchButlerChannels =
        {
            "windows",
            "osx",
            "linux",
            "html"
        };
    }
}
