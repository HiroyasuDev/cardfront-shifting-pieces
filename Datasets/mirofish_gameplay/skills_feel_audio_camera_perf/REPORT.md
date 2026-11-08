# Game Feel, Audio Design, Camera Systems & Performance Optimization Audit — `CARDFRONT: Cradle of Echoes`
**Adapted for Gemini 4 Argon (`gemini-4-argon`) + Antigravity Subagent Harness**

- **Target Web Playable (Read-Only):** [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Target Unity C# Runtime (Read-Only):**
  - [`Assets/Scripts/Core/CardFrontUnifiedRuntime.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs)
  - [`Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs)
  - [`Assets/Scripts/FX/SynapseDicevadersJuiceAndAudioController.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/FX/SynapseDicevadersJuiceAndAudioController.cs)
  - [`Assets/Scripts/Audio/SynapseProceduralAudioDirector.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Audio/SynapseProceduralAudioDirector.cs)
  - [`Assets/Scripts/Tools/SynapseMemoryPool.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Tools/SynapseMemoryPool.cs)
- **Loaded Skills:**
  1. [`skills/disciplines/game-feel/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md) (+ `references/feedback-recipes.md`)
  2. [`skills/disciplines/audio-design/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/audio-design/SKILL.md) (+ `references/adaptive-music.md`)
  3. [`skills/disciplines/camera-systems/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/camera-systems/SKILL.md) (+ `references/follow-and-framing.md`)
  4. [`skills/disciplines/performance-optimization/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md) (+ `references/profiling-and-budgets.md`)
- **Automated Audit Telemetry:**
  - [`raw/playwright_feel_perf_audit.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/raw/playwright_feel_perf_audit.json)

---

## 1. Gemini 4 Argon (`gemini-4-argon`) Native Skill Routing & Verification Architecture

To adapt the `t13A2XFGoOc` (`gamedev-skills`) workflow for **Gemini 4 Argon (`gemini-4-argon`)**:

1. **Master Router (`gamedev-router` + `pxg-gamedev-harness`):**
   - Routes feel/audio/camera/perf prompts into the 4-slot progressive disclosure stack (`game-feel` + `audio-design` + `camera-systems` + `performance-optimization`) and pairs them with Unity 2022.3.40f1 (`unity-animation`, `unity-csharp-scripting`) and the custom HTML5/CSS3D web engine (`router/references/custom-engines.md`).
2. **Profiler-First Verification via Parallel Subagents (`Tools/skill_harness/iterate.py`):**
   - Obeying `performance-optimization/SKILL.md:35-39` (*"The golden rule: measure first, never guess"*), Gemini 4 Argon's `code-implementer` and `truth-verifier` subagents run real `requestAnimationFrame` frame-budget timing (`60` frames under active trauma shake + SVG animations) and `MutationObserver` DOM-churn profiling on the live Chromium page before scoring the 20 automated checks in [`checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/checks.json).

---

## 2. Executive Summary & Headline Findings

1. **Game-Feel Quadratic Trauma Shake (`shake = trauma * trauma`) & 80ms Hit-Stop PASS on Player Captures, But Overlapping Hit-Stops & Boss Captures Have Bugs:**
   - Both Web (`cardfront_cradle_of_echoes_playable.html:1372-1408`) and Unity (`SynapseGameDevSkillsHarness.cs:44-92`) implement decaying trauma (`1.4/s` decay, `shake = trauma * trauma`, multi-frequency sine offsets `sin(t*1.7)`, `sin(t*2.3)`).
   - **Bug GF-1 (P1 — Overlapping Hit-Stop Race Condition):** Unity (`SynapseGameDevSkillsHarness.cs:81-91`) increments `_activeHitStopId` and guards `if (myId == _activeHitStopId) Time.timeScale = 1.0f;` per `game-feel/SKILL.md:97-105, 150-151`. However, Web `triggerHitStop(durationMs = 80)` (`cardfront_cradle_of_echoes_playable.html:1376-1386`) uses an unguarded `setTimeout(() => { state.hitStopActive = false; vp.style.filter = ""; }, durationMs)`, so two rapid triggers let the first timer prematurely cancel the second hit-stop.
   - **Bug GF-2 (P2 — Asymmetry on Tactical Slide & Boss Captures):** `handleSlotClick` triggers `triggerHitStop(80)` and `addTrauma(...)` when deploying a card from hand (lines 1739-1744), but **omits both hit-stop and trauma** when capturing enemy cards via Tactical Slide (lines 1702-1707) and when the Boss captures player cards in `executeBossTurn` (lines 1788-1796).
   - **Bug GF-3 (P2 — Missing Accessibility Toggle):** Neither Web nor Unity exposes a `"Reduce Screen Shake / Reduce Flashing"` option required by `game-feel/SKILL.md:157-158`.
2. **Audio Design Fails Bus Routing, Master Limiter, and SFX Pitch Variation on Web (`playTone` at lines 1322-1344):**
   - In `cardfront_cradle_of_echoes_playable.html:1323-1344`, every sound creates a raw `OscillatorNode` + `GainNode` connected directly to `actx.destination` (`g.connect(actx.destination)`, line 1341) with hardcoded linear gain `0.16` and zero master bus, zero `DynamicsCompressorNode` limiter (`audio-design/SKILL.md:33-43, 162-167`), zero volume/mute UI controls, and zero pitch/volume randomization (`audio-design/SKILL.md:48-49, 116-130`).
   - In Unity (`SynapseProceduralAudioDirector.cs:29-36, 73-80` & `SynapseDicevadersJuiceAndAudioController.cs:134-156`), `AudioSource` components are created via `gameObject.AddComponent<AudioSource>()` with `outputAudioMixerGroup == null` (bypassing Unity's `AudioMixer`, `audio-design/SKILL.md:80-81, 164-165`) and linear slider multiplication (`masterVolume * sfxVolume`, line 109) instead of logarithmic dB mapping `20f * Mathf.Log10(Mathf.Max(gain * gain, 0.0001f))` (`audio-design/SKILL.md:67-80, 158-161`).
3. **Camera Systems: Frame-Rate-Independent Drag Spring (`dragTick`) vs Mouse-Parallax Instant Snap:**
   - Web's `setBoardCamera` (lines 1471-1479) and `arena-viewport` `mousemove` parallax (lines 1484-1496) set `slab.style.transform` directly on every `mousemove` event without frame-rate-independent exponential smoothing `1 - Math.exp(-rate * dt)` (`camera-systems/SKILL.md:38-40, 73-80, 131-132`), and `dragTick()` (lines 2267-2299) uses fixed per-frame lerp constants (`* 0.22`, `* 0.42`, `* 0.2`) without scaling by `dt`.
   - Furthermore, the `autotest=1` harness (`runVisualAutomatedPlaytest`, line 2557) queries `document.getElementById("cam-select")`, which returns `null` because the header `<select>` id is actually `"camera-select"` (line 863)!
4. **Performance Optimization: 60 FPS (`16.67 ms`) Achieved, But `renderAll()` Causes `504` DOM Node Allocations per 20 Hover Events:**
   - Playwright's 60-frame `requestAnimationFrame` profiler (`raw/playwright_feel_perf_audit.json:512-523`) measured `meanFrameMs = 16.67 ms` (`60.0 FPS`) and `p95FrameMs = 16.80 ms` under active trauma shake + 6 continuous SVG animations.
   - However, `renderAll()` (lines 1891-2106) destroys and rebuilds `#col-headers`, `#dice-column-list`, `#grid-3x3`, and `#hand-bar` via `innerHTML = ""` on every hover/click, generating **`584` DOM mutations (`504` added + `504` removed top-level nodes) across 20 renders** (`0.185 ms/call`), and `startGameFeelTraumaLoop` (lines 1388-1408) runs an unconditional `requestAnimationFrame(step)` loop 60 times/sec forever even when `state.trauma === 0`.

---

## 3. Skill-by-Skill Audit Table

### 3.1 `skills/disciplines/game-feel/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GF-1** | `game-feel/SKILL.md:63-90, 142-145` | **Decaying Quadratic Trauma Shake (`shake = trauma^2`) on Visual Offset:** Drive smooth sine/noise camera offset from decaying trauma (`0..1`), never random per-frame static. | **PASS** | Web (`cardfront_cradle_of_echoes_playable.html:1393-1403`) decays `state.trauma` by `1.4 * dt`, computes `const shake = trauma * trauma`, and applies smooth sine offsets `sin(noiseTime * 1.7)` / `sin(noiseTime * 2.3)` to `#arena-viewport`. Unity (`SynapseGameDevSkillsHarness.cs:63-79`) matches identically. | P1 · S |
| **GF-2** | `game-feel/SKILL.md:92-114, 146-148` | **Real-Time Hit-Stop Timer:** Restore time/freeze state using a real-time timer (`WaitForSecondsRealtime` in Unity) so timeScale `0.05` never deadlocks. | **PASS** | Unity (`SynapseGameDevSkillsHarness.cs:81-92`) uses `yield return new WaitForSecondsRealtime(durationRealtimeSeconds)`. Web (`lines 1376-1386`) uses wall-clock `setTimeout` + brightness/contrast flash (`brightness(1.22) contrast(1.12)`). | P1 · S |
| **GF-3** | `game-feel/SKILL.md:97-105, 150-151` | **Overlapping Hit-Stop Guard (`_hit_stop_id`):** Two hits close together must let only the newest hit-stop restore normal state. | **PARTIAL** | Unity (`SynapseGameDevSkillsHarness.cs:83-91`) guards restore with `if (myId == _activeHitStopId)`. Web (`cardfront_cradle_of_echoes_playable.html:1376-1386`) has no ID/timer cancellation guard. | P1 · S |
| **GF-4** | `game-feel/SKILL.md:41, 56-57, 131-138` | **Consistent Importance Tiers Across Events:** Scale feedback bundles consistently across all capture events (deploy capture, slide capture, boss capture). | **FAIL** | Web `handleSlotClick` (lines 1739-1744) fires `triggerHitStop(80)` + `addTrauma(...)` on hand deploy, but Tactical Slide captures (lines 1702-1713) and Boss captures (`executeBossTurn`, lines 1788-1800) trigger **zero** trauma shake and **zero** hit-stop. | P2 · S |
| **GF-5** | `game-feel/SKILL.md:116-127, 152-153` | **Eased Motion & Volume-Conserving Squash/Stretch:** Use overshoot (`cubic-bezier` / `TRANS_BACK`) and volume-conserving squash/stretch on impacts. | **PASS** | Web `.board-slot.just-placed .card-3d-unit` (lines 507-514) uses `cubic-bezier(0.22, 1.4, 0.36, 1)` squash-land (`scale(1.06) -> scale(0.97) -> scale(1.0)`), `.board-3d-slab.thud` (lines 515-520) adds a 3px table thud, and Unity (`SynapseGameDevSkillsHarness.cs:94-109`, `SynapseDicevadersJuiceAndAudioController.cs:35-66`) implements volume-conserving squash/stretch and underdamped springs (`zeta=0.42, omega_n=30`). | P2 · S |
| **GF-6** | `game-feel/SKILL.md:157-158` | **Accessibility Option ("Reduce Screen Shake / Flashing"):** Provide a user toggle to disable/reduce screen shake and hit-stop brightness flashes. | **FAIL** | Neither `WebPlayable/cardfront_cradle_of_echoes_playable.html` nor `SynapseGameDevSkillsHarness.cs` exposes a `reduceScreenShake` / `prefers-reduced-motion` guard. | P2 · S |

### 3.2 `skills/disciplines/audio-design/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AU-1** | `audio-design/SKILL.md:33-36, 61-81, 162-165` | **Bus Routing & Mixer Architecture:** Route all sounds through named buses (`Master <- {Music, SFX, UI}`) rather than directly to destination or unrouted `AudioSource`s. | **FAIL** | Web `playTone` (line 1341) connects each one-shot `GainNode` straight to `actx.destination` with no master/SFX gain bus or mute toggle. Unity `SynapseProceduralAudioDirector.cs:73-80` creates `AudioSource`s without assigning `outputAudioMixerGroup`. | P1 · S |
| **AU-2** | `audio-design/SKILL.md:37-43, 67-76, 158-167` | **Logarithmic (dB / Squared Slider) Volume & Master Peak Limiter:** Convert `0..1` sliders via `gain * gain` -> dB and place a limiter/compressor on Master to prevent clipping (`<= -1 dBTP`). | **FAIL** | Unity `SynapseProceduralAudioDirector.cs:109, 168` multiplies raw linear floats (`masterVolume * sfxVolume`). Web `playTone` has no `DynamicsCompressorNode` on `actx.destination`. | P2 · S |
| **AU-3** | `audio-design/SKILL.md:44-47, 83-112, 169-173` | **Adaptive Music & Sidechain Ducking:** Layer/re-sequence music by combat state and duck music under fanfare/important SFX. | **FAIL** | Web playable has zero background music or ambient stems and zero ducking. Unity `SynapseProceduralAudioDirector.cs` synthesizes SFX/fanfares (`PlayCaptureFlipFanfare`), but has no adaptive BGM loop or sidechain ducking. | P2 · M |
| **AU-4** | `audio-design/SKILL.md:48-49, 114-130` | **SFX Variation (Pitch & Volume Randomization):** Vary repeated SFX by `±1` semitone / `±2 dB` to prevent robotic "machine-gun" repetition. | **FAIL** | Web `playTone(semi, type, dur)` (line 1331) computes exact deterministic `f = 440 * Math.pow(2, semi / 12)` with zero pitch or gain jitter on repeated card hovers/clicks. | P2 · S |

### 3.3 `skills/disciplines/camera-systems/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CM-1** | `camera-systems/SKILL.md:38-40, 73-80, 131-132` | **Frame-Rate-Independent Smoothing (`1 - exp(-rate * dt)`):** Never use fixed per-frame `lerp(a, b, 0.1)` that changes speed with FPS. | **FAIL** | Web `dragTick()` (`cardfront_cradle_of_echoes_playable.html:2271, 2284-2287, 2293-2295`) uses fixed per-frame factors (`* 0.22`, `* 0.42`, `* 0.2`) without `dt` exponential decay `1 - Math.exp(-rate * dt)`. (Unity `DampedSpringState.Step(dt)` in `SynapseDicevadersJuiceAndAudioController.cs:59-66` properly integrates with `dt`.) | P1 · S |
| **CM-2** | `camera-systems/SKILL.md:41-42, 84-94, 137-139` | **Deadzone & Pitch/Angle Clamping:** Ignore micro-movements inside a deadzone and clamp pitch/tilt angles. | **PARTIAL** | Web board parallax (`lines 1484-1492`) clamps tilt implicitly to `baseTiltX ± 2.2°` and `rotateY ± 2.6°`, and freezes during drag (`if (drag.active) return;`), but has no center deadzone so tiny mouse tremors continuously rotate the 3D board. Also, line 2557 has a bug: `document.getElementById("cam-select")` queries the wrong ID (`#camera-select` is at line 863). | P2 · S |
| **CM-3** | `camera-systems/SKILL.md:117-127, 145-146` | **Additive Shake Composition:** Compose smooth camera framing first and apply `game-feel` shake offset on top of a separate visual parent so follow and shake never fight. | **PASS** | Web applies camera tilt/parallax to `#board-3d-slab` (line 1491) and applies trauma shake `translate3d(ox, oy, 0)` to its parent `#arena-viewport` (line 1400), keeping them cleanly separated. | P2 · S |

### 3.4 `skills/disciplines/performance-optimization/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets` / `raw/`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PF-1** | `performance-optimization/SKILL.md:43-44, 62-70` | **60 FPS Frame-Time Budget (`<= 16.67 ms`):** Total frame time must stay within `16.67 ms` at 60 Hz. | **PASS** | Playwright 60-frame rAF benchmark (`raw/playwright_feel_perf_audit.json:520-522`) measured `meanFrameMs = 16.67 ms` and `p95FrameMs = 16.80 ms` during active trauma shake and 6 continuous SVG animations. | P1 · S |
| **PF-2** | `performance-optimization/SKILL.md:88-102, 123-134, 146-149` | **Object Pooling & Zero Per-Event DOM/Heap Thrash:** Reuse nodes/buffers (`SynapsePool<T>`) instead of destroying and recreating trees on every interaction. | **PARTIAL** | Unity (`Assets/Scripts/Tools/SynapseMemoryPool.cs:9-61`) implements zero-allocation `SynapsePool<T>` and `SwapBuffer<T>`. However, Web `renderAll()` (lines 1905, 1916, 1971, 2071) calls `innerHTML = ""` on 4 containers every hover/click, causing `504` node allocations + `504` removals per 20 renders (`raw/playwright_feel_perf_audit.json:514-518`), and `SynapseMiroStrandsSimulationEngine.cs:3` imports `System.Linq` in AI evaluation. | P1 · M |
| **PF-3** | `performance-optimization/SKILL.md:48-51, 106-119, 155` | **Limit Continuous Idle Work & Overdraw:** Stop rAF loops and infinite off-focus CSS animations when idle, and avoid stacked `backdrop-filter: blur()` + `mix-blend-mode: screen` overdraw. | **FAIL** | `startGameFeelTraumaLoop` (lines 1388-1408) runs `requestAnimationFrame(step)` 60 times/sec forever even when `state.trauma === 0`; all 6–14 visible `.card-telegraph-fx` SVGs run infinite CSS keyframe animations (`spinSlow`, `pulseRing`, `sweepSlash`, lines 567-603) with `mix-blend-mode: screen` over `backdrop-filter: blur(12px)` panels (line 166). | P2 · S |

---

## 4. Concrete Code Fixes (Sketches Only — Not Applied to Target Files)

### 4.1 Fix Hit-Stop Overlap Race, Reduced-Motion Guard & On-Demand Trauma Loop (`WebPlayable/cardfront_cradle_of_echoes_playable.html:1372-1408`)
```javascript
let hitStopSeq = 0;
let traumaRafId = 0;
const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function addTrauma(amount = 0.45) {
  if (prefersReducedMotion || state.reduceShake) return;
  state.trauma = Math.min(1.0, Math.max(0.0, state.trauma + amount));
  if (!traumaRafId) {
    lastTraumaTs = performance.now();
    traumaRafId = requestAnimationFrame(stepTrauma);
  }
}

function triggerHitStop(durationMs = 80) {
  if (prefersReducedMotion || state.reduceShake) return;
  const mySeq = ++hitStopSeq;
  state.hitStopActive = true;
  const vp = document.getElementById("arena-viewport");
  if (vp) vp.style.filter = "brightness(1.22) contrast(1.12)";
  setTimeout(() => {
    if (mySeq !== hitStopSeq) return; // Newer hit-stop owns the restore (game-feel/SKILL.md:104)
    state.hitStopActive = false;
    if (vp) vp.style.filter = "";
  }, durationMs);
}
```

### 4.2 Fix Web Audio Bus Routing, Master Compressor Limiter & Pitch Variation (`WebPlayable/cardfront_cradle_of_echoes_playable.html:1322-1344`)
```javascript
let actx = null, masterBus = null, sfxBus = null;
function ensureAudioGraph() {
  if (!actx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    actx = new AC();
    const limiter = actx.createDynamicsCompressor();
    limiter.threshold.value = -3.0; // Headroom below -1 dBTP (audio-design/SKILL.md:38)
    limiter.ratio.value = 12.0;
    masterBus = actx.createGain();
    sfxBus = actx.createGain();
    sfxBus.connect(masterBus);
    masterBus.connect(limiter);
    limiter.connect(actx.destination);
  }
  if (actx.state === "suspended") actx.resume();
  return true;
}

function playTone(semi = 0, type = "triangle", dur = 0.2, jitterSemitones = 0.35) {
  if (!ensureAudioGraph()) return;
  const now = actx.currentTime;
  const randSemi = semi + (Math.random() * 2 - 1) * jitterSemitones; // SFX variation (audio-design/SKILL.md:123)
  const f = 440 * Math.pow(2, randSemi / 12);
  const o = actx.createOscillator();
  const g = actx.createGain();
  o.type = type;
  o.frequency.setValueAtTime(f, now);
  o.frequency.exponentialRampToValueAtTime(f * 1.15, now + dur);
  g.gain.setValueAtTime(0.001, now);
  g.gain.linearRampToValueAtTime(0.16, now + 0.015);
  g.gain.exponentialRampToValueAtTime(0.001, now + dur);
  o.connect(g);
  g.connect(sfxBus);
  o.start(now);
  o.stop(now + dur + 0.02);
}
```

### 4.3 Fix Frame-Rate-Independent Exponential Smoothing in `dragTick` (`WebPlayable/cardfront_cradle_of_echoes_playable.html:2267-2299`)
```javascript
let lastDragTs = performance.now();
function dragTick(now = performance.now()) {
  if (!drag.active || drag.dropping) return;
  const dt = Math.min(0.05, Math.max(0.001, (now - lastDragTs) / 1000.0));
  lastDragTs = now;
  const alphaPos = 1.0 - Math.exp(-32.0 * dt);   // Frame-rate independent (camera-systems/SKILL.md:75)
  const alphaScale = 1.0 - Math.exp(-15.0 * dt);
  // ... apply alphaPos and alphaScale instead of fixed 0.42 and 0.22 ...
}
```
