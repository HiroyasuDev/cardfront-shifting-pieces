/**
 * CARDFRONT 3D: Cradle of Echoes — Mastered Multi-Layer .WAV Foley & BGM Audio Bank
 * Decodes real mastered .wav stems (`WebPlayable/Audio/*.wav`) via WebAudio `decodeAudioData`
 * with seamless fallback to the Sakimoto-Yamada procedural synthesizer.
 */
(function (root) {
  "use strict";

  const AUDIO_STEM_MANIFEST = {
    card_slam_stone: "./Audio/card_slam_stone.wav",
    dice_tumble_brass: "./Audio/dice_tumble_brass.wav",
    crystal_capture_shatter: "./Audio/crystal_capture_shatter.wav",
    sakuga_impact_subdrop: "./Audio/sakuga_impact_subdrop.wav",
    bgm_citadel_tactical_loop: "./Audio/bgm_citadel_tactical_loop.wav"
  };

  const FoleyAudioBank = {
    buffers: {},
    loading: false,
    loadedCount: 0,
    activeBgmSource: null,

    async preloadAllStems(audioCtx) {
      if (!audioCtx || this.loading) return this.loadedCount;
      this.loading = true;
      const entries = Object.entries(AUDIO_STEM_MANIFEST);
      await Promise.all(
        entries.map(async ([key, url]) => {
          if (this.buffers[key]) return;
          try {
            const res = await fetch(url, { cache: "force-cache" });
            if (!res.ok) return;
            const arr = await res.arrayBuffer();
            const decoded = await audioCtx.decodeAudioData(arr);
            if (decoded) {
              this.buffers[key] = decoded;
              this.loadedCount++;
            }
          } catch (_e) {}
        })
      );
      this.loading = false;
      return this.loadedCount;
    },

    playSample(stemKey, audioCtx, destinationNode, playbackRate = 1.0, gainVal = 0.85) {
      if (!audioCtx) return false;
      if (!this.buffers[stemKey] && !this.loading) {
        this.preloadAllStems(audioCtx);
        return false;
      }
      const buf = this.buffers[stemKey];
      if (!buf) return false;
      try {
        const src = audioCtx.createBufferSource();
        const gain = audioCtx.createGain();
        src.buffer = buf;
        src.playbackRate.value = playbackRate;
        gain.gain.value = gainVal;
        src.connect(gain);
        gain.connect(destinationNode || audioCtx.destination);
        src.start(0);
        return true;
      } catch (_e) {
        return false;
      }
    },

    startBgmLoop(audioCtx, destinationNode, gainVal = 0.55) {
      this.stopBgmLoop();
      if (!audioCtx) return false;
      const buf = this.buffers.bgm_citadel_tactical_loop;
      if (!buf) {
        this.preloadAllStems(audioCtx);
        return false;
      }
      try {
        const src = audioCtx.createBufferSource();
        const gain = audioCtx.createGain();
        src.buffer = buf;
        src.loop = true;
        gain.gain.value = gainVal;
        src.connect(gain);
        gain.connect(destinationNode || audioCtx.destination);
        src.start(0);
        this.activeBgmSource = src;
        return true;
      } catch (_e) {
        return false;
      }
    },

    stopBgmLoop() {
      if (this.activeBgmSource) {
        try {
          this.activeBgmSource.stop();
          this.activeBgmSource.disconnect();
        } catch (_e) {}
        this.activeBgmSource = null;
      }
    }
  };

  root.CardFrontModules = root.CardFrontModules || {};
  root.CardFrontModules.FoleyAudioBank = FoleyAudioBank;
})(typeof window !== "undefined" ? window : globalThis);
