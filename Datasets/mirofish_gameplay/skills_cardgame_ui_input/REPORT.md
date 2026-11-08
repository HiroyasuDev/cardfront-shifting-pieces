# Card-Game, UI/UX, Input Systems & ScriptableObjects Audit — `CARDFRONT: Cradle of Echoes`
**Adapted for Gemini 4 Argon (`gemini-4-argon`) + Antigravity Subagent Harness**

- **Target Web Playable (Read-Only):** [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Target Unity C# Runtime (Read-Only):** [`Assets/Scripts/Core/CardFrontUnifiedRuntime.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs) & [`Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs)
- **Loaded Skills:**
  1. [`skills/genres/card-game/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md) (+ `references/effect-resolution.md`)
  2. [`skills/disciplines/game-ui-ux/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md) (+ `references/layout-and-flow.md`)
  3. [`skills/disciplines/input-systems/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md) (+ `references/buffering-and-accessibility.md`)
  4. [`skills/unity/unity-scriptableobjects/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/unity/unity-scriptableobjects/SKILL.md) (+ `references/event-channels.md`)
- **Automated Audit Scripts & Telemetry:**
  - [`scripts/run_playwright_audits.js`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/scripts/run_playwright_audits.js)
  - [`raw/playwright_ui_input_audit.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/raw/playwright_ui_input_audit.json)
  - Multi-viewport screenshots: [`screens/viewport_1280x800_laptop.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/screens/viewport_1280x800_laptop.png), [`screens/viewport_1920x1080_desktop.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/screens/viewport_1920x1080_desktop.png), [`screens/viewport_2560x1080_ultrawide.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/screens/viewport_2560x1080_ultrawide.png), [`screens/viewport_375x667_mobile.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/screens/viewport_375x667_mobile.png)

---

## 1. Gemini 4 Argon (`gemini-4-argon`) Native Skill Routing & Verification Architecture

To adapt the `gamedev-skills/awesome-gamedev-agent-skills` workflow (`https://youtu.be/t13A2XFGoOc`) for **Gemini 4 Argon (`gemini-4-argon`)**:

1. **Master Router (`gamedev-router` + `pxg-gamedev-harness`):**
   - When prompted with *"Audit 3x3 tactical card game UI layout, input mapping, single-zone invariants, and ScriptableObject architecture"*, `gamedev-router` (`~/.gemini/config/skills/gamedev-router/SKILL.md:56-75`) routes across the 4-slot cap: `unity-scriptableobjects` (Engine) → `game-ui-ux` + `input-systems` (Disciplines) → `card-game` (Genre).
2. **Live Multi-Viewport & DOM Verification (`Tools/skill_harness/iterate.py`):**
   - Unlike static LLM code review or synthetic toy-array tests (`Backend/synapse_gamedev_skills_harness_bridge.py:218`), Gemini 4 Argon dispatches `code-implementer` and `truth-verifier` subagents to execute 22 live Playwright (`page.evaluate`) and `static_regex` probes in [`checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_cardgame_ui_input/checks.json) directly against `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html` and `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs`.

---

## 2. Executive Summary & Headline Findings

1. **CRITICAL P0 Layout Bug Caught at `1280×800`: Right Panel Clipped by `130 px` (`right = 1410 px > 1280 px`):**
   - Despite the CSS banner claiming `PROPORTIONAL VIEWPORT-SAFE SIZING (FITS 1280x800 SAFARI WITH ZERO CLIPPING)` (`cardfront_cradle_of_echoes_playable.html:23`) and `3-COLUMN STAGE (264px | 1fr | 264px — GUARANTEED ZERO RIGHT-EDGE CLIPPING)` (line 138), our Playwright measurement (`raw/playwright_ui_input_audit.json:60-69`) proves that as soon as a card is hovered on the board (`updateTelegraphHud`, line 1522), `#telegraph-hud-desc` populates with a long `white-space: nowrap` string inside `.center-zone`.
   - Because `.center-zone` (lines 241-252) sets `min-height: 0` but **omits `min-width: 0`**, CSS Grid's `1fr` column expands to its `min-content` width (`844 px` instead of `700 px`), pushing the right `aside.side-box` to `left: 1146 px, right: 1410 px` and **clipping `130 px` of the Boss Commander & 3D Column Dice panel off the right edge of the `1280×800` viewport** (`screens/viewport_1280x800_laptop.png`).
2. **CRITICAL P1 Mobile/Narrow Viewport Failure (`375×667`):**
   - At `375×667` (`raw/playwright_ui_input_audit.json:378-442`), `main` uses a fixed `grid-template-columns: 264px 1fr 264px` with zero `@media` breakpoints and `body { overflow: hidden }` (line 37). Both the 3×3 board (`left: 492 px, right: 915 px`) and the right panel (`left: 1129 px, right: 1393 px`) are 100% off-screen and unreachable.
3. **CRITICAL P1 Typography Floor Violation (`99%` of Leaf Text Nodes Below `18 px`):**
   - `game-ui-ux/SKILL.md:139-141` cites Xbox Accessibility Guideline 101: minimum `18 px` at 1080p on PC (`26 px` on console/TV). Playwright's font census (`raw/playwright_ui_input_audit.json:71-126`) found **107 of 108 leaf text nodes (`99.1%`) are `< 18 px`**, and **85 of 108 (`78.7%`) are `< 12 px`**, bottoming out at **`8.5 px`** on `.hand-card-wrap .slot-name-ribbon` (line 629) and `.tactical-slide-card` (lines 2098, 2101) and **`9.5 px`** on `.hand-card-wrap .edge-num` (line 653).
4. **Card-Game Single-Zone Invariant PASSES (`11/11` Unique Cards Conserved), But Unseeded `Math.random()` Fails Replay Determinism:**
   - Playwright verified that `state.hand` (5), `state.grid` (1 initial, up to 9), and `state.aiPool` (5) are strictly disjoint (`singleZoneDisjoint: true`, `totalInPlay: 11`, `uniqueInPlay: 11`, `raw/playwright_ui_input_audit.json:503-510`), and Fisher-Yates `shuffle()` (lines 1499-1506) uses the correct inclusive index `Math.floor(Math.random() * (i + 1))`.
   - However, `shuffle()`, `rerollAllDice()` (line 1608), and `executeBossTurn()` tie-breaking (line 1773) call unseeded `Math.random()`, violating `card-game/SKILL.md:68, 115-117` (*"Use a seeded RNG instance... and save its state with the run"*).
5. **Unity C# Combat Asymmetry Bug (`CardFrontUnifiedRuntime.cs:370-380`) & Domain-Reload Pitfall (`SynapseGameDevSkillsHarness.cs:25-28`):**
   - In `CardFrontUnifiedRuntime.cs:370-380`, `OnCardPlayedEvaluate3x3AndResonance` compares the attacker's **boosted** `result.effective_north` against the neighbor's **unboosted** base `neighbor.CardData.dir_south` instead of the neighbor's effective column-boosted stat (whereas the web playable at `cardfront_cradle_of_echoes_playable.html:1637` compares against `nb.nesw[d.theirEdge]`).
   - In `SynapseGameDevSkillsHarness.cs:18-28`, `ScriptableObjectDomainReloadGuard` resets `RuntimeValue = initialValue` inside `OnEnable()`, but omits the `EditorApplication.playModeStateChanged` hook required when Enter Play Mode Options disables Domain Reload (`unity-scriptableobjects/SKILL.md:81-95, 115-120`).

---

## 3. Skill-by-Skill Audit Table

### 3.1 `skills/genres/card-game/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CG-1** | `card-game/SKILL.md:34, 59-70, 107-108` | **Single-Zone Invariant:** Cards live in exactly one zone (`deck`, `hand`, `board`, `discard`); move = remove-then-add. | **PASS** | `startStage` (lines 1577-1583) pops `firstEnemy` before slicing `aiPool`, and `handleSlotClick` (line 1720) calls `state.hand.splice(state.selectedHandIdx, 1)` before assigning `cell.cardId`. Playwright confirmed `11/11` unique cards across zones (`raw/playwright_ui_input_audit.json:503-509`). | P0 · S |
| **CG-2** | `card-game/SKILL.md:118-120` | **Fair Fisher-Yates Shuffle:** Random index `j` must include `i` (`0 <= j <= i`), no off-by-one bias. | **PASS** | `shuffle(arr)` at `cardfront_cradle_of_echoes_playable.html:1502` uses `Math.floor(Math.random() * (i + 1))`; `SynapseGameDevSkillsHarness.cs:151` uses `rng.Next(0, i + 1)`. | P1 · S |
| **CG-3** | `card-game/SKILL.md:68, 115-117` | **Seeded RNG for Replays/Undo:** Use a seeded RNG instance, not global `Math.random()`. | **FAIL** | Web playable uses unseeded `Math.random()` at lines 1502, 1608, and 1773. Runs cannot be replayed or shared by seed. | P1 · S |
| **CG-4** | `card-game/SKILL.md:33, 75-88, 111-112` | **Card as Data + Effect Resolution:** Effects are data interpreted by one resolver; telegraph patterns should not be purely cosmetic when descriptions promise board effects. | **PARTIAL** | `PLAYER_HEROES` / `ENEMY_MECHS` (lines 963-1143) store `telegraphDesc` claiming distinct spatial effects (*"Projects a 4-way golden cruciform beam across its entire Row & Column"*), but `findCaptures` (lines 1625-1643) ignores `telegraphPattern` and applies identical 4-neighbor orthogonal NESW comparison for all 16 cards. | P2 · M |
| **CG-5** | `card-game/SKILL.md:38, 113-114` | **Unambiguous Effect Resolution Order:** Combat math must match between Web prototype and Unity C# runtime. | **FAIL** | Web `findCaptures` (line 1637) compares `nesw[d.myEdge] > nb.nesw[d.theirEdge]` (both column-boosted). Unity `CardFrontUnifiedRuntime.cs:370-380` compares `result.effective_north > neighbor.CardData.dir_south` (ignoring neighbor's column boost/traits). | P1 · S |

### 3.2 `skills/disciplines/game-ui-ux/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UI-1** | `game-ui-ux/SKILL.md:35-40, 130-133` | **Responsive Layout Across Aspect Ratios:** Survive `1280×800`, `1920×1080`, ultrawide `21:9`, and mobile without clipping. | **FAIL** | At `1280×800`, `.center-zone` lacks `min-width: 0`, expanding to `844 px` when `#telegraph-hud-desc` updates and clipping `rightPanel` (`right = 1410 px > 1280 px`). At `375×667`, fixed `264px 1fr 264px` grid clips board and right panel completely (`raw/playwright_ui_input_audit.json:60-69, 408-442`). | P0 · S |
| **UI-2** | `game-ui-ux/SKILL.md:41-42, 83-98, 134` | **Respect Safe Area:** Inset critical UI from screen edges/notches (`env(safe-area-inset-*)` on Web, `Screen.safeArea` in Unity). | **PARTIAL** | Unity `SynapseGameDevSkillsHarness.cs:191-202` implements `ComputeNormalizedSafeAreaAnchors`, but `WebPlayable/cardfront_cradle_of_echoes_playable.html` has zero `env(safe-area-inset-*)` CSS rules and lacks `viewport-fit=cover` in `<meta name="viewport">` (line 5). | P2 · S |
| **UI-3** | `game-ui-ux/SKILL.md:43-44, 100-114, 135-136` | **Keyboard/Gamepad Focus Navigation:** Initial focused control, focus neighbors, visible focus highlight, and full action coverage. | **PARTIAL** | `handleHarnessKeyDown` (lines 1410-1446) supports keys `1–5`, `WASD`/Arrows, `Enter`/`Space`, `P`, and `R`. However: (a) `.board-slot` has no visual focus ring class for `state.focusedSlotIndex` when not hovered, (b) Column Dice (`nudgeColDie`) cannot be focused/nudged via keyboard, (c) `#result-modal` (line 946) does not grab focus or respond to `Enter`/`Escape`, and (d) zero `navigator.getGamepads()` support exists. | P1 · M |
| **UI-4** | `game-ui-ux/SKILL.md:45-46, 142-143` | **Screen Stack vs Boolean Flag Soup:** Model overlays/modals as a push/pop stack with focus handoff. | **FAIL** | Modal visibility is toggled via raw inline style `modal.style.display = "flex"` / `"none"` (lines 1834, 1840) and boolean flags (`state.gameOver`, `state.isPlayerTurn`), without a screen stack or Escape/focus trapping. | P2 · S |
| **UI-5** | `game-ui-ux/SKILL.md:47-49, 116-126, 137-138` | **Event-Driven HUD (Not Per-Frame Polling):** Update UI only when state changes, and update incrementally rather than rebuilding the whole DOM. | **PARTIAL** | HUD is event-driven (no per-frame polling loop), but `renderAll()` (lines 1891-2106) wipes `innerHTML = ""` on 4 containers every hover/click, causing `504` node additions + `504` removals across 20 renders (`raw/playwright_ui_input_audit.json:512-518`). | P2 · M |
| **UI-6** | `game-ui-ux/SKILL.md:139-141` | **Accessible Font Size Floor:** Minimum `18 px` at 1080p on PC (`26 px` on console), scalable without clipping. | **FAIL** | `107/108` leaf text nodes are `< 18 px` (`85/108 < 12 px`), with card names at `8.5 px` (line 629) and stat numbers at `9.5 px` (line 653) (`raw/playwright_ui_input_audit.json:71-126`). | P1 · M |

### 3.3 `skills/disciplines/input-systems/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`WebPlayable` / `Assets`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IN-1** | `input-systems/SKILL.md:14-18, 36-37, 176-177` | **Named Actions Over Raw Keys:** Map physical keys/buttons to named actions; never hardcode raw `e.key` checks in gameplay logic. | **FAIL** | `handleHarnessKeyDown` (`cardfront_cradle_of_echoes_playable.html:1410-1445`) hardcodes raw `e.key === "ArrowUp" \|\| e.key === "w"` checks directly in gameplay logic with no action map data table. | P1 · S |
| **IN-2** | `input-systems/SKILL.md:166-169, 186-188` | **Physical Keycodes (`e.code`) vs Layout Letters (`e.key`):** Bind WASD by physical key position (`KeyW`, `KeyA`, `KeyS`, `KeyD`) so AZERTY/Dvorak layouts work, and ignore key auto-repeat (`!e.repeat`). | **FAIL** | Uses `e.key === "w"` instead of `e.code === "KeyW"`, breaking WASD spatial layout on AZERTY keyboards, and does not guard against `e.repeat` on discrete actions (`Enter`/`Space`/`R`/`P`). | P1 · S |
| **IN-3** | `input-systems/SKILL.md:48-50, 121-164, 184-185` | **Rebinding with Conflict Detection & Persistence:** Allow players to rebind controls and persist bindings. | **FAIL** | Zero rebinding UI, conflict detection, or saved keybindings in `WebPlayable/cardfront_cradle_of_echoes_playable.html`. | P2 · M |
| **IN-4** | `input-systems/SKILL.md:38-39, 99-117, 193-195` | **Multi-Device Pointer/Touch & Drag Threshold:** Support mouse + touch seamlessly with forgiving target acquisition. | **PASS** | Custom pointer drag engine (`beginPointerDrag`, lines 2116-2398) uses `PointerEvent` (`pointerdown`/`pointermove`/`pointerup`/`pointercancel`), `touch-action: none` (line 442), a `6 px` `DRAG_THRESHOLD_PX` so clicks and drags coexist, and a `0.72 × max(w,h)` magnet radius (`findDropTarget`, line 2213). | P2 · S |

### 3.4 `skills/unity/unity-scriptableobjects/SKILL.md`
| Rule ID | Source Line | Rule Summary | Verdict | Evidence (`Assets/Scripts/Core/`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SO-1** | `unity-scriptableobjects/SKILL.md:29-35, 48-58` | **Data Assets vs Hardcoded C# Arrays:** Author card/style definitions as `[CreateAssetMenu] ScriptableObject` assets, not hardcoded static arrays in logic classes. | **PARTIAL** | `SynapseGameDevSkillsHarness.cs:17-18` defines `[CreateAssetMenu] ScriptableObjectDomainReloadGuard`, but `CardFrontUnifiedRuntime.cs:609-666` hardcodes `s_sovereignStyles` as a `private static readonly SovereignStyleVariantDescriptor[]` array instead of `ScriptableObject` assets. | P2 · S |
| **SO-2** | `unity-scriptableobjects/SKILL.md:78-96, 110-120` | **Domain-Reload-Safe Runtime Reset:** Reset `[NonSerialized]` runtime state both in `OnEnable` AND via `EditorApplication.playModeStateChanged` (or `[RuntimeInitializeOnLoadMethod(SubsystemRegistration)]`). | **PARTIAL** | `SynapseGameDevSkillsHarness.cs:20-28` marks `[NonSerialized] public float RuntimeValue` and resets it in `OnEnable()`, but omits the `#if UNITY_EDITOR EditorApplication.playModeStateChanged` hook required when Enter Play Mode Options disables Domain Reload. | P1 · S |

---

## 4. Concrete Code Fixes (Sketches Only — Not Applied to Target Files)

### 4.1 Fix P0 `1280×800` Right-Panel Horizontal Clipping & Narrow Viewport Reflow (`WebPlayable/cardfront_cradle_of_echoes_playable.html:140-152, 241-252`)
```css
/* 1. Prevent #telegraph-hud-desc from expanding the 1fr grid track past 700px at 1280x800 */
.center-zone {
  min-width: 0;   /* ADD THIS at line 251 alongside min-height: 0 */
  min-height: 0;
}
.telegraph-hud-pill {
  max-width: 100%;
  width: min(100%, 660px);
}

/* 2. Responsive breakpoint for tablets/mobile (< 1100px) */
@media (max-width: 1100px) {
  body { overflow-y: auto; height: auto; min-height: 100vh; }
  main {
    grid-template-columns: 1fr;
    max-height: none;
    overflow: visible;
  }
}
```

### 4.2 Fix P1 Action Mapping, `e.code` Physical Keys & Repeat Guard (`WebPlayable/cardfront_cradle_of_echoes_playable.html:1410-1446`)
```javascript
const DEFAULT_ACTION_BINDINGS = {
  move_up:    ["ArrowUp", "KeyW"],
  move_down:  ["ArrowDown", "KeyS"],
  move_left:  ["ArrowLeft", "KeyA"],
  move_right: ["ArrowRight", "KeyD"],
  confirm:    ["Enter", "Space"],
  pulse:      ["KeyP"],
  reroll:     ["KeyR"],
  nudge_col1: ["Digit6"],
  nudge_col2: ["Digit7"],
  nudge_col3: ["Digit8"]
};

function isActionPressed(e, actionName, bindings = DEFAULT_ACTION_BINDINGS) {
  if (e.repeat) return false; // input-systems/SKILL.md:134 — ignore key auto-repeat on discrete edges
  const codes = bindings[actionName] || [];
  return codes.includes(e.code) || codes.includes(e.key);
}
```

### 4.3 Fix P1 Unity Domain-Reload-Off Reset (`Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs:25-28`)
```csharp
private void OnEnable()
{
    RuntimeValue = initialValue;
#if UNITY_EDITOR
    UnityEditor.EditorApplication.playModeStateChanged -= HandlePlayModeStateChanged;
    UnityEditor.EditorApplication.playModeStateChanged += HandlePlayModeStateChanged;
#endif
}

#if UNITY_EDITOR
private void OnDisable() => UnityEditor.EditorApplication.playModeStateChanged -= HandlePlayModeStateChanged;
private void HandlePlayModeStateChanged(UnityEditor.PlayModeStateChange state)
{
    if (state == UnityEditor.PlayModeStateChange.ExitingEditMode)
        RuntimeValue = initialValue;
}
#endif
```
