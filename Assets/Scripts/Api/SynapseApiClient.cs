using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace Synapse.TcgEngine.Api
{
    [Serializable]
    public class SynapseUserProfile
    {
        public string userId;
        public string username;
        public int eloRating = 1200;
        public int coins = 1000;
        public int confidencePoints = 0;
        public int xp = 0;
        public List<string> ownedCards = new List<string>();
        public List<string> badges = new List<string>();
    }

    [Serializable]
    public class PackOpenResult
    {
        public string packId;
        public List<string> drawnCardIds = new List<string>();
        public int remainingCoins;
    }

    /// <summary>
    /// Clean-room Sovereign Metagame API Client for Synapse.TcgEngine.
    /// Replaces third-party ApiClient/ApiMsg/UserData with a lightweight REST client talking to
    /// our proprietary Python/SQLite backend (`Backend/synapse_tcg_backend.py`).
    /// </summary>
    public sealed class SynapseApiClient
    {
        public string BaseUrl { get; set; } = "http://127.0.0.1:8790";
        public string AccessToken { get; private set; }
        public SynapseUserProfile CurrentUser { get; private set; }

        public async Task<string> GetJsonAsync(string endpoint)
        {
            using var req = UnityWebRequest.Get(BaseUrl.TrimEnd('/') + endpoint);
            if (!string.IsNullOrEmpty(AccessToken))
                req.SetRequestHeader("Authorization", "Bearer " + AccessToken);
            var op = req.SendWebRequest();
            while (!op.isDone) await Task.Yield();
            return req.result == UnityWebRequest.Result.Success ? req.downloadHandler.text : null;
        }
    }
}
