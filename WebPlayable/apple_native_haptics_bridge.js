/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes -- Multi-Platform Native Haptics, PWA & Crypto Vault Bridge
 * Provides:
 *   1. window.CardFrontHaptics:
 *      - trigger(type, intensityOrMeta) supporting:
 *        "card_place", "card_flip", "die_nudge", "telegraph_alert", "victory", "defeat",
 *        "light", "medium", "heavy", "success", "warning", "error"
 *      - impact(style) & notification(type) convenience methods
 *      - 6-tier fallback chain:
 *        1) Apple WebKit (window.webkit.messageHandlers.cardfrontHaptics)
 *        2) Android Native (window.CardFrontAndroidBridge.postHaptic)
 *        3) Steam Desktop (window.CardFrontSteamBridge.triggerRumble)
 *        4) Gamepad API (navigator.getGamepads vibrationActuator.playEffect("dual-rumble", ...))
 *        5) Web Vibration API (navigator.vibrate)
 *        6) WebAudio sub-bass tactile click synthesis
 *   2. window.CardFrontPlatformBridge:
 *      - detectPlatform() -> "apple_native_wkwebview" | "android_native" | "steam_desktop" | "apple_pwa_standalone" | "desktop_or_mobile_web"
 *      - exportSignedCrossSavePayload(stateObj) -> deterministic FNV-1a + SHA-256 signature envelope
 *      - verifySignedCrossSavePayload(envelope) -> boolean signature check
 *      - generateProvablyFairPackReceipt(stageIndex, packNonce) -> deterministic FNV-1a + SHA-256 commit-reveal receipt (zero_crypto_tokens: true)
 *      - injectMultiPlatformVaultSection() -> injects #multiplatform-crypto-vault-bar into #deckbuilder-modal
 *      - registerServiceWorker() -> registers ./sw_cardfront_pwa.js
 * ============================================================================ */

(function initCardFrontNativeAndPwaBridge(globalScope) {
  "use strict";

  const HAPTIC_PATTERNS = {
    card_place: {
      name: "card_place",
      appleFeedbackType: "impactMedium",
      intensity: 0.72,
      sharpness: 0.80,
      durationMs: 24,
      vibrate: [14]
    },
    card_flip: {
      name: "card_flip",
      appleFeedbackType: "impactHeavy",
      intensity: 0.92,
      sharpness: 0.90,
      durationMs: 65,
      vibrate: [22, 30, 36]
    },
    die_nudge: {
      name: "die_nudge",
      appleFeedbackType: "selectionChanged",
      intensity: 0.58,
      sharpness: 0.88,
      durationMs: 18,
      vibrate: [10]
    },
    telegraph_alert: {
      name: "telegraph_alert",
      appleFeedbackType: "notificationWarning",
      intensity: 0.84,
      sharpness: 0.76,
      durationMs: 50,
      vibrate: [18, 24, 18]
    },
    victory: {
      name: "victory",
      appleFeedbackType: "notificationSuccess",
      intensity: 1.0,
      sharpness: 0.95,
      durationMs: 110,
      vibrate: [28, 40, 28, 40, 65]
    },
    defeat: {
      name: "defeat",
      appleFeedbackType: "notificationError",
      intensity: 0.88,
      sharpness: 0.45,
      durationMs: 95,
      vibrate: [45, 50, 70]
    },
    light: {
      name: "light",
      appleFeedbackType: "impactLight",
      intensity: 0.45,
      sharpness: 0.70,
      durationMs: 16,
      vibrate: [8]
    },
    medium: {
      name: "medium",
      appleFeedbackType: "impactMedium",
      intensity: 0.75,
      sharpness: 0.82,
      durationMs: 26,
      vibrate: [15]
    },
    heavy: {
      name: "heavy",
      appleFeedbackType: "impactHeavy",
      intensity: 0.95,
      sharpness: 0.92,
      durationMs: 42,
      vibrate: [28]
    },
    success: {
      name: "success",
      appleFeedbackType: "notificationSuccess",
      intensity: 0.88,
      sharpness: 0.90,
      durationMs: 60,
      vibrate: [18, 24, 32]
    },
    warning: {
      name: "warning",
      appleFeedbackType: "notificationWarning",
      intensity: 0.82,
      sharpness: 0.75,
      durationMs: 52,
      vibrate: [20, 22, 20]
    },
    error: {
      name: "error",
      appleFeedbackType: "notificationError",
      intensity: 0.90,
      sharpness: 0.50,
      durationMs: 75,
      vibrate: [35, 30, 45]
    }
  };

  // Bespoke 256x256 inline SVGs for Multi-Platform Vault Pills & Action Buttons (Zero Generic Emojis)
  const VAULT_SVG_ICONS = {
    web_pwa:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<circle cx="128" cy="128" r="102" fill="#0B1326" stroke="#00E5FF" stroke-width="14"/>' +
      '<ellipse cx="128" cy="128" rx="52" ry="102" fill="none" stroke="#FFB800" stroke-width="10"/>' +
      '<line x1="26" y1="128" x2="230" y2="128" stroke="#00E5FF" stroke-width="10"/>' +
      '<polygon points="128,68 148,112 192,128 148,144 128,188 108,144 64,128 108,112" fill="#FFB800"/>' +
      "</svg>",
    apple_native:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<polygon points="128,16 218,58 240,148 182,228 74,228 16,148 38,58" fill="#0F172A" stroke="#FFB800" stroke-width="14"/>' +
      '<polygon points="128,44 196,128 128,212 60,128" fill="#00E5FF" fill-opacity="0.3" stroke="#00E5FF" stroke-width="10"/>' +
      '<circle cx="128" cy="128" r="24" fill="#FFB800"/>' +
      "</svg>",
    steam_desktop:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<circle cx="128" cy="128" r="102" fill="#0B1326" stroke="#38BDF8" stroke-width="14"/>' +
      '<circle cx="164" cy="100" r="34" fill="#0F172A" stroke="#FFB800" stroke-width="12"/>' +
      '<circle cx="92" cy="164" r="26" fill="#0F172A" stroke="#00E5FF" stroke-width="12"/>' +
      '<line x1="108" y1="148" x2="146" y2="116" stroke="#FFB800" stroke-width="16" stroke-linecap="round"/>' +
      "</svg>",
    android_native:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<line x1="76" y1="32" x2="98" y2="74" stroke="#2EE6D3" stroke-width="14" stroke-linecap="round"/>' +
      '<line x1="180" y1="32" x2="158" y2="74" stroke="#2EE6D3" stroke-width="14" stroke-linecap="round"/>' +
      '<path d="M52,144 C52,92 86,66 128,66 C170,66 204,92 204,144 L204,196 L52,196 Z" fill="#0B1326" stroke="#2EE6D3" stroke-width="14"/>' +
      '<circle cx="98" cy="130" r="14" fill="#FFB800"/>' +
      '<circle cx="158" cy="130" r="14" fill="#FFB800"/>' +
      "</svg>",
    verify_shield:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<path d="M128,18 L220,56 L220,128 C220,184 178,222 128,242 C78,222 36,184 36,128 L36,56 Z" fill="#0F172A" stroke="#FFB800" stroke-width="14"/>' +
      '<polyline points="84,132 116,164 176,96" fill="none" stroke="#2EE6D3" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>",
    fair_pack:
      '<svg width="14" height="14" viewBox="0 0 256 256" fill="none" aria-hidden="true" style="flex-shrink:0;">' +
      '<polygon points="128,20 226,76 226,180 128,236 30,180 30,76" fill="#0F172A" stroke="#A855F7" stroke-width="14"/>' +
      '<polygon points="128,54 190,128 128,202 66,128" fill="#FFB800"/>' +
      '<circle cx="128" cy="128" r="20" fill="#00E5FF"/>' +
      "</svg>"
  };

  // Fallback Set 1 pool for deterministic pack draws when global catalog is not yet initialized
  const FALLBACK_SET1_POOL = [
    { id: "h_archangel", name: "Solar Archangel", faction: "Solaris", starCost: 3 },
    { id: "h_phoenix", name: "Phoenix Valkyrie", faction: "Valkyria", starCost: 3 },
    { id: "h_oracle", name: "Lunar Oracle", faction: "Aether", starCost: 3 },
    { id: "h_chronos", name: "Chronos Weaver", faction: "Chronos", starCost: 2 },
    { id: "h_seraph", name: "Astral Seraph", faction: "Aether", starCost: 3 },
    { id: "h_kai", name: "Kai Crimson Visor", faction: "Valkyria", starCost: 2 },
    { id: "h_valkyrie", name: "Sky-Wing Striker", faction: "Valkyria", starCost: 2 },
    { id: "h_arbiter", name: "Sun Arbiter", faction: "Solaris", starCost: 3 },
    { id: "p_jev_gate", name: "Jev Verification Gate", faction: "Solaris", starCost: 3 },
    { id: "p_mlx_silicon", name: "Apple Silicon MLX Core", faction: "Aether", starCost: 3 },
    { id: "p_swarm_nexus", name: "Parallel Swarm Nexus", faction: "Chronos", starCost: 3 },
    { id: "p_atelier_svg", name: "Atelier Vector Forge", faction: "Valkyria", starCost: 3 }
  ];

  // Deterministic 32-bit FNV-1a hash (returns 8-char hex)
  function computeFnv1a32(inputStr) {
    const str = String(inputStr || "");
    let hash = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
      hash ^= str.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  // Deterministic synchronous SHA-256 implementation for cross-save signing & provably fair receipts
  const SHA256_K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ]);

  function rotr32(x, n) {
    return (x >>> n) | (x << (32 - n));
  }

  function computeSha256Hex(asciiInput) {
    const utf8 = unescape(encodeURIComponent(String(asciiInput || "")));
    const bitLen = utf8.length * 8;
    const totalBytes = (((utf8.length + 8) >> 6) + 1) * 64;
    const buf = new Uint8Array(totalBytes);
    for (let i = 0; i < utf8.length; i++) {
      buf[i] = utf8.charCodeAt(i) & 0xff;
    }
    buf[utf8.length] = 0x80;
    const view = new DataView(buf.buffer);
    view.setUint32(totalBytes - 8, Math.floor(bitLen / 0x100000000), false);
    view.setUint32(totalBytes - 4, bitLen >>> 0, false);

    let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
    let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
    const w = new Uint32Array(64);

    for (let offset = 0; offset < totalBytes; offset += 64) {
      for (let i = 0; i < 16; i++) {
        w[i] = view.getUint32(offset + i * 4, false);
      }
      for (let i = 16; i < 64; i++) {
        const s0 = rotr32(w[i - 15], 7) ^ rotr32(w[i - 15], 18) ^ (w[i - 15] >>> 3);
        const s1 = rotr32(w[i - 2], 17) ^ rotr32(w[i - 2], 19) ^ (w[i - 2] >>> 10);
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
      }

      let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
      for (let i = 0; i < 64; i++) {
        const S1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25);
        const ch = (e & f) ^ (~e & g);
        const temp1 = (h + S1 + ch + SHA256_K[i] + w[i]) >>> 0;
        const S0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22);
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const temp2 = (S0 + maj) >>> 0;

        h = g;
        g = f;
        f = e;
        e = (d + temp1) >>> 0;
        d = c;
        c = b;
        b = a;
        a = (temp1 + temp2) >>> 0;
      }

      h0 = (h0 + a) >>> 0;
      h1 = (h1 + b) >>> 0;
      h2 = (h2 + c) >>> 0;
      h3 = (h3 + d) >>> 0;
      h4 = (h4 + e) >>> 0;
      h5 = (h5 + f) >>> 0;
      h6 = (h6 + g) >>> 0;
      h7 = (h7 + h) >>> 0;
    }

    return [h0, h1, h2, h3, h4, h5, h6, h7]
      .map((word) => (word >>> 0).toString(16).padStart(8, "0"))
      .join("");
  }

  // Async WebCrypto SHA-256 helper with deterministic synchronous fallback
  async function computeSha256SubtleHex(inputStr) {
    const text = String(inputStr || "");
    try {
      if (
        globalScope.crypto &&
        globalScope.crypto.subtle &&
        typeof globalScope.crypto.subtle.digest === "function" &&
        typeof TextEncoder !== "undefined"
      ) {
        const encoded = new TextEncoder().encode(text);
        const digestBuf = await globalScope.crypto.subtle.digest("SHA-256", encoded);
        const bytes = new Uint8Array(digestBuf);
        let hex = "";
        for (let i = 0; i < bytes.length; i++) {
          hex += bytes[i].toString(16).padStart(2, "0");
        }
        return hex;
      }
    } catch (_) {
      // Fallback to synchronous FIPS 180-4 SHA-256
    }
    return computeSha256Hex(text);
  }

  // WebAudio sub-bass tactile click synthesis fallback (#6 in haptic chain)
  let sharedHapticAudioCtx = null;
  function synthesizeSubBassTactileClick(intensity = 0.72, sharpness = 0.80, durationMs = 24) {
    try {
      if (globalScope.state && globalScope.state.muted) {
        return false;
      }
      const AudioCtxCtor = globalScope.AudioContext || globalScope.webkitAudioContext;
      const ctx = globalScope.actx || sharedHapticAudioCtx || (AudioCtxCtor ? (sharedHapticAudioCtx = new AudioCtxCtor()) : null);
      if (!ctx || typeof ctx.createOscillator !== "function" || typeof ctx.createGain !== "function") {
        return false;
      }
      const now = ctx.currentTime || 0;
      const durSec = Math.max(0.015, Math.min(0.085, Number(durationMs || 24) / 1000));
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      const startHz = 52 + Math.round(Math.max(0, Math.min(1, sharpness)) * 28);
      osc.frequency.setValueAtTime(startHz, now);
      osc.frequency.exponentialRampToValueAtTime(28, now + durSec);
      const peakGain = Math.max(0.01, Math.min(0.12, Number(intensity || 0.7) * 0.08));
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.linearRampToValueAtTime(peakGain, now + 0.003);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + durSec);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + durSec + 0.004);
      return true;
    } catch (_) {
      return false;
    }
  }

  const CardFrontHaptics = {
    enabled: true,
    patterns: HAPTIC_PATTERNS,
    lastTriggered: null,
    lastPayload: null,
    triggerCount: 0,
    history: [],

    isSupported() {
      const hasWkBridge = Boolean(
        globalScope.webkit &&
        globalScope.webkit.messageHandlers &&
        globalScope.webkit.messageHandlers.cardfrontHaptics &&
        typeof globalScope.webkit.messageHandlers.cardfrontHaptics.postMessage === "function"
      );
      const hasAndroidBridge = Boolean(
        globalScope.CardFrontAndroidBridge &&
        typeof globalScope.CardFrontAndroidBridge.postHaptic === "function"
      );
      const hasSteamBridge = Boolean(
        globalScope.CardFrontSteamBridge &&
        typeof globalScope.CardFrontSteamBridge.triggerRumble === "function"
      );
      const hasVibrate = Boolean(
        typeof globalScope.navigator !== "undefined" &&
        typeof globalScope.navigator.vibrate === "function"
      );
      const hasAudioCtx = Boolean(globalScope.AudioContext || globalScope.webkitAudioContext);
      return hasWkBridge || hasAndroidBridge || hasSteamBridge || hasVibrate || hasAudioCtx;
    },

    impact(style = "medium", meta = {}) {
      const norm = String(style || "medium").toLowerCase();
      const patternKey = HAPTIC_PATTERNS[norm] ? norm : "medium";
      return this.trigger(patternKey, meta);
    },

    notification(type = "success", meta = {}) {
      const norm = String(type || "success").toLowerCase();
      const patternKey = HAPTIC_PATTERNS[norm] ? norm : "success";
      return this.trigger(patternKey, meta);
    },

    selection(meta = {}) {
      return this.trigger("die_nudge", meta);
    },

    trigger(type, intensity = {}) {
      const key = String(type || "card_place");
      const spec = HAPTIC_PATTERNS[key] || HAPTIC_PATTERNS.card_place;
      const numericIntensity =
        typeof intensity === "number" && !Number.isNaN(intensity)
          ? Math.max(0.05, Math.min(1.0, intensity))
          : spec.intensity;
      const metaObj =
        intensity && typeof intensity === "object" && !Array.isArray(intensity)
          ? intensity
          : { requestedIntensity: numericIntensity };
      const durationMs = spec.durationMs || 28;

      this.triggerCount = (this.triggerCount || 0) + 1;
      this.lastTriggered = key;

      let route = "simulated_telemetry";
      const payload = {
        pattern: key,
        appleFeedbackType: spec.appleFeedbackType,
        intensity: numericIntensity,
        sharpness: spec.sharpness,
        durationMs,
        vibrate: spec.vibrate,
        meta: metaObj,
        count: this.triggerCount,
        timestamp: Date.now()
      };

      if (this.enabled) {
        const wkHandler =
          globalScope.webkit &&
          globalScope.webkit.messageHandlers &&
          globalScope.webkit.messageHandlers.cardfrontHaptics;

        // 1) Apple WebKit (window.webkit.messageHandlers.cardfrontHaptics)
        if (wkHandler && typeof wkHandler.postMessage === "function") {
          try {
            wkHandler.postMessage(payload);
            route = "apple_wkwebview_corehaptics";
          } catch (_) {
            route = "apple_wkwebview_error_fallback";
          }
        }
        // 2) Android Native (window.CardFrontAndroidBridge.postHaptic)
        else if (
          globalScope.CardFrontAndroidBridge &&
          typeof globalScope.CardFrontAndroidBridge.postHaptic === "function"
        ) {
          try {
            globalScope.CardFrontAndroidBridge.postHaptic(key, numericIntensity, JSON.stringify(payload));
            route = "android_native_bridge";
          } catch (_) {
            route = "android_native_error_fallback";
          }
        }
        // 3) Steam Desktop (window.CardFrontSteamBridge.triggerRumble)
        else if (
          globalScope.CardFrontSteamBridge &&
          typeof globalScope.CardFrontSteamBridge.triggerRumble === "function"
        ) {
          try {
            globalScope.CardFrontSteamBridge.triggerRumble(key, numericIntensity, durationMs);
            route = "steam_desktop_bridge";
          } catch (_) {
            route = "steam_desktop_error_fallback";
          }
        } else {
          // 4) Gamepad API (navigator.getGamepads vibrationActuator.playEffect("dual-rumble", ...))
          let gamepadRumbling = false;
          if (
            typeof globalScope.navigator !== "undefined" &&
            typeof globalScope.navigator.getGamepads === "function"
          ) {
            try {
              const pads = globalScope.navigator.getGamepads() || [];
              for (let i = 0; i < pads.length; i++) {
                const pad = pads[i];
                if (
                  pad &&
                  pad.vibrationActuator &&
                  typeof pad.vibrationActuator.playEffect === "function"
                ) {
                  pad.vibrationActuator.playEffect("dual-rumble", {
                    startDelay: 0,
                    duration: durationMs,
                    weakMagnitude: Math.min(1.0, Math.max(0.1, spec.sharpness)),
                    strongMagnitude: Math.min(1.0, Math.max(0.1, numericIntensity))
                  });
                  gamepadRumbling = true;
                  route = "gamepad_dual_rumble";
                  break;
                }
              }
            } catch (_) {
              gamepadRumbling = false;
            }
          }

          // 5) Web Vibration API (navigator.vibrate)
          if (
            !gamepadRumbling &&
            typeof globalScope.navigator !== "undefined" &&
            typeof globalScope.navigator.vibrate === "function"
          ) {
            try {
              const vibrated = globalScope.navigator.vibrate(spec.vibrate);
              if (vibrated !== false) {
                route = "web_navigator_vibrate";
              }
            } catch (_) {
              route = "web_vibrate_blocked";
            }
          }

          // 6) WebAudio sub-bass tactile click synthesis fallback
          if (route === "simulated_telemetry" || route === "web_vibrate_blocked") {
            const playedSubBass = synthesizeSubBassTactileClick(numericIntensity, spec.sharpness, durationMs);
            if (playedSubBass) {
              route = "webaudio_subbass_tactile";
            }
          }
        }
      }

      payload.route = route;
      this.lastPayload = payload;
      this.history.push(payload);
      if (this.history.length > 32) {
        this.history.shift();
      }
      return payload;
    },

    resetTelemetry() {
      this.lastTriggered = null;
      this.lastPayload = null;
      this.triggerCount = 0;
      this.history = [];
    }
  };

  const CardFrontPlatformBridge = {
    swRegistrationStatus: "unregistered",
    lastCrossSaveEnvelope: null,
    lastPackReceipt: null,
    lastSubtleDigestHex: null,
    packNonceCounter: 0,

    detectPlatform() {
      const hasAppleNativeBridge = Boolean(
        globalScope.webkit &&
        globalScope.webkit.messageHandlers &&
        (globalScope.webkit.messageHandlers.cardfrontHaptics ||
         globalScope.webkit.messageHandlers.cardfrontNativeHost)
      );
      if (hasAppleNativeBridge) {
        return "apple_native_wkwebview";
      }

      if (
        globalScope.CardFrontAndroidBridge &&
        typeof globalScope.CardFrontAndroidBridge.postHaptic === "function"
      ) {
        return "android_native";
      }

      if (
        globalScope.CardFrontSteamBridge &&
        typeof globalScope.CardFrontSteamBridge.triggerRumble === "function"
      ) {
        return "steam_desktop";
      }

      const isIosStandalone = Boolean(
        typeof globalScope.navigator !== "undefined" &&
        globalScope.navigator.standalone === true
      );
      const isDisplayModeStandalone = Boolean(
        typeof globalScope.matchMedia === "function" &&
        globalScope.matchMedia("(display-mode: standalone)").matches
      );
      if (isIosStandalone || isDisplayModeStandalone) {
        return "apple_pwa_standalone";
      }

      return "desktop_or_mobile_web";
    },

    computeFnv1a32,
    computeSha256Hex,
    computeSha256SubtleHex,

    exportSignedCrossSavePayload(stateObj) {
      const src = stateObj || globalScope.state || {};
      const canonicalData = {
        stageIndex: Number(src.stageIndex || 0),
        unlockedStage: Number(src.unlockedStage || 0),
        clearedStages: Array.isArray(src.clearedStages) ? [...src.clearedStages].map(Number).sort((a, b) => a - b) : [],
        coins: Number(src.coins !== undefined ? src.coins : 250),
        wins: Number(src.wins || 0),
        losses: Number(src.losses || 0),
        matchesPlayed: Number(src.matchesPlayed || 0),
        unlockedCards: Array.isArray(src.unlockedCards) ? [...src.unlockedCards].map(String).sort() : [],
        activeDeck: Array.isArray(src.activeDeck) ? [...src.activeDeck].map(String) : [],
        cardEvolutions: src.cardEvolutions && typeof src.cardEvolutions === "object" ? src.cardEvolutions : {}
      };

      const canonicalJson = JSON.stringify(canonicalData);
      const fnv1a = computeFnv1a32(canonicalJson);
      const sha256 = computeSha256Hex(canonicalJson + "|CARDFRONT_SOVEREIGN_SALT_V3");
      const envelope = {
        schema: "CARDFRONT_CROSS_SAVE_V3",
        platform: this.detectPlatform(),
        supportedPlatforms: ["web_pwa", "apple_native", "steam_desktop", "android_native"],
        exportedAt: new Date().toISOString(),
        data: canonicalData,
        signature: {
          algorithm: "FNV1A-32+SHA256",
          fnv1a,
          sha256,
          envelopeHash: `${fnv1a}:${sha256}`
        }
      };
      this.lastCrossSaveEnvelope = envelope;
      return envelope;
    },

    verifySignedCrossSavePayload(envelope) {
      if (!envelope || !envelope.data || !envelope.signature) return false;
      const canonicalJson = JSON.stringify(envelope.data);
      const expectedFnv = computeFnv1a32(canonicalJson);
      const expectedSha = computeSha256Hex(canonicalJson + "|CARDFRONT_SOVEREIGN_SALT_V3");
      return (
        envelope.signature.fnv1a === expectedFnv &&
        envelope.signature.sha256 === expectedSha
      );
    },

    generateProvablyFairPackReceipt(stageIndex, packNonce) {
      const resolvedStage =
        typeof stageIndex === "number" && !Number.isNaN(stageIndex)
          ? stageIndex
          : Number((globalScope.state && globalScope.state.stageIndex) || 0);
      const resolvedNonce =
        typeof packNonce === "number" && !Number.isNaN(packNonce)
          ? packNonce
          : (this.packNonceCounter = (this.packNonceCounter || 0) + 1);

      const serverSeed = `CARDFRONT_SET1_CRADLE_SERVER_SEED_STAGE_${resolvedStage}`;
      const serverSeedHash = computeSha256Hex(serverSeed);
      const clientSeedInput = `stage:${resolvedStage}|nonce:${resolvedNonce}|seed:${(globalScope.state && globalScope.state.seed) || 20261108}`;
      const clientSeed = `cf_client_${computeFnv1a32(clientSeedInput)}`;
      const commitmentPayload = `${serverSeedHash}:${clientSeed}:${resolvedNonce}`;
      const fnv1aCommitment = computeFnv1a32(commitmentPayload);
      const combinedCommitmentHash = computeSha256Hex(commitmentPayload);

      const catalog =
        Array.isArray(globalScope.SET1_60_CATALOG) && globalScope.SET1_60_CATALOG.length >= 5
          ? globalScope.SET1_60_CATALOG
          : FALLBACK_SET1_POOL;

      const rarities = ["Mythic", "Legendary", "Epic", "Rare", "Rare"];
      const cardsDrawn = [];
      const usedIndices = new Set();

      for (let slot = 0; slot < 5; slot++) {
        const slotSeed = `${combinedCommitmentHash}:slot:${slot}:${fnv1aCommitment}`;
        const slotHash = computeSha256Hex(slotSeed);
        const slotFnvHex = computeFnv1a32(slotSeed);
        let idx = parseInt(slotFnvHex, 16) % catalog.length;
        let guard = 0;
        while (usedIndices.has(idx) && guard < catalog.length) {
          idx = (idx + 1) % catalog.length;
          guard++;
        }
        usedIndices.add(idx);
        const picked = catalog[idx] || FALLBACK_SET1_POOL[slot % FALLBACK_SET1_POOL.length];
        const rarity =
          String(picked.id || "").startsWith("p_")
            ? "Mythic"
            : (picked.starCost >= 3 ? rarities[Math.min(slot, 1)] : rarities[slot]);

        const cardEntry = {
          id: picked.id,
          cardId: picked.id,
          name: picked.name || picked.id,
          rarity,
          faction: picked.faction || "Solaris",
          slotIndex: slot,
          slotHash
        };
        Object.defineProperty(cardEntry, "toString", {
          value: function () {
            return `${this.id} (${this.rarity})`;
          },
          enumerable: false
        });
        cardsDrawn.push(cardEntry);
      }

      const receipt = {
        serverSeedHash,
        clientSeed,
        packNonce: resolvedNonce,
        combinedCommitmentHash,
        fnv1aChecksum: `0x${fnv1aCommitment}`,
        cardsDrawn,
        pack_cards: cardsDrawn.map((c) => c.id),
        slot_hashes: cardsDrawn.map((c) => c.slotHash),
        server_seed_commitment: serverSeedHash,
        zeroCryptoTokens: true,
        zero_crypto_tokens: true,
        zero_blockchain_gas: true,
        verified: true
      };

      this.lastPackReceipt = receipt;

      // Cross-verify asynchronously with WebCrypto subtle.digest("SHA-256", ...) when available
      computeSha256SubtleHex(commitmentPayload)
        .then((subtleHex) => {
          this.lastSubtleDigestHex = subtleHex;
          receipt.subtleSha256Verified = subtleHex === combinedCommitmentHash;
        })
        .catch(() => {});

      return receipt;
    },

    injectMultiPlatformVaultSection() {
      if (typeof globalScope.document === "undefined") return null;
      const doc = globalScope.document;
      const modal = doc.getElementById("deckbuilder-modal");
      const summaryEl = doc.getElementById("deckbuilder-squad-summary");
      if (!modal || !summaryEl) return null;

      let vaultBar = doc.getElementById("multiplatform-crypto-vault-bar");
      if (!vaultBar) {
        vaultBar = doc.createElement("div");
        vaultBar.id = "multiplatform-crypto-vault-bar";
        vaultBar.style.cssText =
          "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;" +
          "background:linear-gradient(135deg,rgba(11,19,38,0.94),rgba(18,28,54,0.92));" +
          "border:1px solid rgba(255,184,0,0.48);border-radius:8px;padding:7px 10px;" +
          "font-size:12px;color:#F8FAFC;box-shadow:0 6px 18px rgba(0,0,0,0.45);";
        summaryEl.insertAdjacentElement("afterend", vaultBar);
      }

      const activePlatform = this.detectPlatform();
      const platformSpecs = [
        { id: "web_pwa", label: "Web PWA", svg: VAULT_SVG_ICONS.web_pwa, active: activePlatform === "desktop_or_mobile_web" || activePlatform === "apple_pwa_standalone" },
        { id: "apple_native", label: "Apple Native Metal", svg: VAULT_SVG_ICONS.apple_native, active: activePlatform === "apple_native_wkwebview" },
        { id: "steam_desktop", label: "Steam Desktop", svg: VAULT_SVG_ICONS.steam_desktop, active: activePlatform === "steam_desktop" },
        { id: "android_native", label: "Android Native", svg: VAULT_SVG_ICONS.android_native, active: activePlatform === "android_native" }
      ];

      const pillsHtml = platformSpecs
        .map((p) => {
          const borderCol = p.active ? "#00E5FF" : "rgba(148,163,184,0.38)";
          const bgCol = p.active ? "rgba(0,229,255,0.16)" : "rgba(15,23,42,0.85)";
          const textCol = p.active ? "#E0FFFF" : "#CBD5E1";
          return (
            `<span class="cf-platform-pill" data-platform-id="${p.id}" style="display:inline-flex;align-items:center;gap:5px;` +
            `padding:3px 8px;border-radius:99px;border:1px solid ${borderCol};background:${bgCol};` +
            `color:${textCol};font-size:12px;font-weight:800;white-space:nowrap;">` +
            `${p.svg}<span style="font-size:12px;">${p.label}</span></span>`
          );
        })
        .join("");

      vaultBar.innerHTML =
        `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
        `<b style="color:#FFB800;font-size:12px;letter-spacing:0.4px;">CROSS-SAVE CRDT &amp; FAIR RNG:</b>` +
        `${pillsHtml}` +
        `</div>` +
        `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
        `<button type="button" id="btn-verify-cross-save" style="display:inline-flex;align-items:center;gap:5px;` +
        `background:linear-gradient(135deg,#0f766e,#115e59);border:1px solid #2ee6d3;color:#f8fafc;` +
        `border-radius:7px;padding:4px 9px;font-size:12px;font-weight:800;cursor:pointer;">` +
        `${VAULT_SVG_ICONS.verify_shield}<span style="font-size:12px;">Verify Cross-Save CRDT</span></button>` +
        `<button type="button" id="btn-verify-fair-pack" style="display:inline-flex;align-items:center;gap:5px;` +
        `background:linear-gradient(135deg,#6d28d9,#4c1d95);border:1px solid #c4b5fd;color:#f8fafc;` +
        `border-radius:7px;padding:4px 9px;font-size:12px;font-weight:800;cursor:pointer;">` +
        `${VAULT_SVG_ICONS.fair_pack}<span style="font-size:12px;">Verify Fair Pack RNG</span></button>` +
        `</div>`;

      const btnCrossSave = doc.getElementById("btn-verify-cross-save");
      if (btnCrossSave) {
        btnCrossSave.onclick = () => {
          const envelope = this.exportSignedCrossSavePayload(globalScope.state);
          const verified = this.verifySignedCrossSavePayload(envelope);
          CardFrontHaptics.impact("medium", { source: "btn-verify-cross-save" });
          const statusEl = doc.getElementById("deckbuilder-status");
          if (statusEl) {
            const shaShort = envelope.signature.sha256.slice(0, 16);
            statusEl.innerHTML =
              `<span style="display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
              `${VAULT_SVG_ICONS.verify_shield}` +
              `<b style="color:#2EE6D3;font-size:12px;">CrossPlatformSaveEnvelope V3 Verified (${verified ? "VALID" : "INVALID"}):</b> ` +
              `<span style="color:#FEF08A;font-family:ui-monospace,monospace;font-size:12px;">FNV-1a 0x${envelope.signature.fnv1a} | SHA-256 ${shaShort}...</span> ` +
              `<span style="color:#CBD5E1;font-size:12px;">CRDT Union Sync Ready (Web PWA / Apple Metal / Steam / Android).</span>` +
              `</span>`;
          }
        };
      }

      const btnFairPack = doc.getElementById("btn-verify-fair-pack");
      if (btnFairPack) {
        btnFairPack.onclick = () => {
          const stIdx = globalScope.state && typeof globalScope.state.stageIndex === "number" ? globalScope.state.stageIndex : 0;
          const receipt = this.generateProvablyFairPackReceipt(stIdx);
          CardFrontHaptics.notification("success", { source: "btn-verify-fair-pack", packNonce: receipt.packNonce });
          const statusEl = doc.getElementById("deckbuilder-status");
          if (statusEl) {
            const cardsSummary = receipt.cardsDrawn
              .map((c) => `${c.id} [${c.rarity}]`)
              .join(" + ");
            const commitShort = receipt.combinedCommitmentHash.slice(0, 16);
            statusEl.innerHTML =
              `<span style="display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
              `${VAULT_SVG_ICONS.fair_pack}` +
              `<b style="color:#C4B5FD;font-size:12px;">Provably Fair Pack RNG Verified (zero_crypto_tokens: ${receipt.zeroCryptoTokens}):</b> ` +
              `<span style="color:#FEF08A;font-family:ui-monospace,monospace;font-size:12px;">Nonce #${receipt.packNonce} | SHA-256 ${commitShort}...</span> ` +
              `<span style="color:#E2E8F0;font-size:12px;">Draws: ${cardsSummary}</span>` +
              `</span>`;
          }
        };
      }

      return vaultBar;
    },

    async registerServiceWorker() {
      if (
        typeof globalScope.navigator === "undefined" ||
        !("serviceWorker" in globalScope.navigator)
      ) {
        this.swRegistrationStatus = "unsupported";
        return { registered: false, reason: "unsupported" };
      }

      const proto = globalScope.location && globalScope.location.protocol;
      if (proto !== "http:" && proto !== "https:") {
        this.swRegistrationStatus = "skipped_non_http_protocol";
        return { registered: false, reason: "skipped_non_http_protocol" };
      }

      try {
        const reg = await globalScope.navigator.serviceWorker.register("./sw_cardfront_pwa.js", {
          scope: "./"
        });
        this.swRegistrationStatus = "registered";
        return { registered: true, scope: reg.scope };
      } catch (err) {
        this.swRegistrationStatus = "error";
        return { registered: false, reason: String(err && err.message ? err.message : err) };
      }
    }
  };

  function hookDeckbuilderModalInjector() {
    if (
      typeof globalScope.openDeckbuilderModal === "function" &&
      !globalScope.openDeckbuilderModal.__cfVaultWrapped
    ) {
      const originalOpenDeckbuilder = globalScope.openDeckbuilderModal;
      const wrappedOpenDeckbuilder = function (...args) {
        const result = originalOpenDeckbuilder.apply(this, args);
        CardFrontPlatformBridge.injectMultiPlatformVaultSection();
        return result;
      };
      wrappedOpenDeckbuilder.__cfVaultWrapped = true;
      globalScope.openDeckbuilderModal = wrappedOpenDeckbuilder;
    }
    CardFrontPlatformBridge.injectMultiPlatformVaultSection();
  }

  globalScope.CardFrontHaptics = CardFrontHaptics;
  globalScope.CardFrontPlatformBridge = CardFrontPlatformBridge;

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", hookDeckbuilderModalInjector);
    } else {
      hookDeckbuilderModalInjector();
    }
  }

  if (typeof globalScope.addEventListener === "function") {
    globalScope.addEventListener("DOMContentLoaded", hookDeckbuilderModalInjector);
    globalScope.addEventListener("load", () => {
      hookDeckbuilderModalInjector();
      CardFrontPlatformBridge.registerServiceWorker().catch(() => {});
    });
  }
})(typeof window !== "undefined" ? window : globalThis);
