/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes — Offline-Capable PWA Service Worker (v3)
 * Strategy: Network-First with deterministic Cache Fallback for 60fps Playable
 * ============================================================================ */

const CACHE_NAME = "cardfront-3d-v3";

const CORE_PRECACHE_ASSETS = [
  "./",
  "./index.html",
  "./cardfront_cradle_of_echoes_playable.html",
  "./manifest.webmanifest",
  "./apple_native_haptics_bridge.js",
  "./tests/inpage_autotest.js",
  "./GeneratedArt/Icons/cf_cardback_astrolabe.svg",
  "./GeneratedArt/Icons/cf_icon_aether_coin.svg",
  "./GeneratedArt/Icons/cf_icon_ally_crest.svg",
  "./GeneratedArt/Icons/cf_icon_astral_surge.svg",
  "./GeneratedArt/Icons/cf_icon_bgm_chime.svg",
  "./GeneratedArt/Icons/cf_icon_booster_reliquary.svg",
  "./GeneratedArt/Icons/cf_icon_boss_crest.svg",
  "./GeneratedArt/Icons/cf_icon_camera_aperture.svg",
  "./GeneratedArt/Icons/cf_icon_cardcraft_anvil.svg",
  "./GeneratedArt/Icons/cf_icon_citadel_gear.svg",
  "./GeneratedArt/Icons/cf_icon_defeat_shatter.svg",
  "./GeneratedArt/Icons/cf_icon_faction_link.svg",
  "./GeneratedArt/Icons/cf_icon_grimoire_deck.svg",
  "./GeneratedArt/Icons/cf_icon_hologram_prism.svg",
  "./GeneratedArt/Icons/cf_icon_judge_aegis.svg",
  "./GeneratedArt/Icons/cf_icon_lock_seal.svg",
  "./GeneratedArt/Icons/cf_icon_sfx_horn.svg",
  "./GeneratedArt/Icons/cf_icon_sfx_muted.svg",
  "./GeneratedArt/Icons/cf_icon_sovereign_crown.svg",
  "./GeneratedArt/Icons/cf_icon_staccs_die.svg",
  "./GeneratedArt/Icons/cf_icon_tactical_lantern.svg",
  "./GeneratedArt/Icons/cf_icon_telegraph_hazard.svg",
  "./GeneratedArt/Icons/cf_icon_victory_laurel.svg",
  "./GeneratedArt/Icons/cf_app_icon_master.svg",
  "./GeneratedArt/Icons/cf_platform_apple.svg",
  "./GeneratedArt/Icons/cf_platform_android.svg",
  "./GeneratedArt/Icons/cf_platform_steam.svg",
  "./GeneratedArt/Icons/cf_platform_pwa.svg",
  "./GeneratedArt/Icons/cf_crypto_shield.svg",
  "./GeneratedArt/Icons/cf_pack_seal.svg"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      await Promise.allSettled(
        CORE_PRECACHE_ASSETS.map(async (url) => {
          try {
            const response = await fetch(url, { cache: "no-cache" });
            if (response && response.ok) {
              await cache.put(url, response.clone());
            }
          } catch (_) {
            // Ignore transient offline error during individual asset precache
          }
        })
      );
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
          return Promise.resolve(false);
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.pathname.includes("__osascript_report__")) return;

  // Network-first fallback to cache
  event.respondWith(
    fetch(req)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && url.origin === self.location.origin) {
          const cloned = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, cloned).catch(() => {});
          });
        }
        return networkResponse;
      })
      .catch(async () => {
        const cached = await caches.match(req, { ignoreSearch: true });
        if (cached) return cached;
        if (req.mode === "navigate") {
          const fallbackDoc = await caches.match("./cardfront_cradle_of_echoes_playable.html", { ignoreSearch: true });
          if (fallbackDoc) return fallbackDoc;
        }
        return new Response("Offline — CARDFRONT 3D cached resource unavailable", {
          status: 503,
          headers: { "Content-Type": "text/plain; charset=utf-8" }
        });
      })
  );
});
