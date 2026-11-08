# Cardfront: Cradle of Echoes — Browser UX, Input, Viewport, Performance & Accessibility QA Report

- **Target Under Test:** `WebPlayable/cardfront_cradle_of_echoes_playable.html` (`http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`)
- **Harness:** Playwright (`playwright-core` + `chrome-headless-shell-mac-arm64`) on Apple Silicon (A18 Pro, 8 GB Unified Memory)
- **Methodology:** 100% real pointer, mouse, touch (CDP `Input.dispatchTouchEvent`), and keyboard (`page.keyboard`) input; zero synthetic state mutations for gameplay verification; runtime-only instrumentation for frame intervals (`requestAnimationFrame`), Long Tasks (`PerformanceObserver`), CDP `Performance.getMetrics`, and ` Emulation.setEmulatedVisionDeficiency` + Pillow/NumPy pixel analysis.
- **Raw Data Artifacts (`ux_qa/raw/`):**
  - `t1_campaign.json` — 4-stage full drag-and-drop campaign + per-turn DOM/heap/listener series
  - `t2_edge_cases.json` & `t2b_edge_cases.json` — 18 input/state race & pointer edge cases
  - `t3_viewports.json` & `t3b_hit_and_shift.json` — 7-viewport responsiveness, `elementFromPoint` hit-testing, touch emulation, and hover layout shift measurements
  - `t4_perf.json` — 1× and 4× CPU-throttled frame timing (`idle`, `hoverSweep`, `drag`), `renderAll()` profiling, and asset checks
  - `t5_a11y.json` & `t5_color_analysis.json` — Keyboard-only full match, tab-stop audit, focus indicator pixel analysis, WCAG contrast ratios (30 elements), font-size census, CVD/grayscale border contrast, and `prefers-reduced-motion` compliance
- **Visual Evidence (`ux_qa/screens/`):** 69 PNG screenshots across all 5 test suites (`t1_*` through `t5_*`).

---

## Executive Summary

| Suite | Scope | Verdict | Headline Finding |
|---|---|---|---|
| **T1: 4-Stage Campaign** | Full 4-stage drag-and-drop playthrough (16 turns) | **PASS** | All 4 stages won cleanly in 36.99 s (`7–2`, `6–3`, `7–2`, `6–3`), 0 misdrops, 100% capture prediction accuracy, 0 console/page/network errors, stable DOM (`671 → 705` nodes) and listener count (`72 → 85`). |
| **T2 / T2b: Input Edge Cases** | 18 drag, click, multi-pointer, keyboard & timer races | **9 PASS / 9 FAIL** | **3 P0/P1 timer races** (`setTimeout` handles for 120 ms snap commit, 650 ms boss reply, and 460 ms result modal are never cancelled by `startStage()`), **1-step fast flicks fail 100% (0/20)** because `drag.target` is only updated inside `pointermove`, **Reset/Stage-Select mid-drag places a card from the new hand**, and **foreign `pointerup` events aren't filtered by `pointerId`**. |
| **T3 / T3b: 7-Viewport Matrix** | 5 desktop + 2 iPad touch viewports (`820×1180` to `1920×1080`) | **1 PASS / 6 FAIL** | Right-hand Boss & 3D Dice panel (`aside.side-box`) is **74.9%–100% clipped off-screen** at every viewport width $\le 1280\text{px}$ and still **14.3% clipped at `1440×900`** due to `body { overflow: hidden }` + fixed/unwrapped middle track width (`sw = 1333px`). Hovering cards in hand shifts the entire 3×3 board horizontally by **up to 59 px** because `#telegraph-hud-desc` uses `white-space: nowrap` without a width cap. Furthermore, `transform-style: preserve-3d` causes `DIV.grid-3x3` / `DIV.board-3d-slab` to intercept `elementFromPoint` on lower rows, breaking click-to-place on row 2 at `1440×900` (`5/8` tiles clickable) and iPad portrait (`tap: false`). |
| **T4: Performance** | 3 s continuous rAF sampling (`idle`, `hoverSweep`, `drag`) at 1× and 4× CPU throttle | **PASS** | Solid 60 Hz (`16.67 ms` avg, `16.8 ms` p99, `0` Long Tasks) during continuous drag at both 1× and 4× CPU throttle. `renderAll()` averages `0.47 ms` at 1× (`1.68 ms` at 4×) and is properly throttled to tile-boundary crossings during drag (21–23 calls over 158–174 pointer moves). |
| **T5: Accessibility (A11y)** | Keyboard play, focus, ARIA, WCAG contrast, font sizes, CVD, reduced motion | **PARTIAL FAIL** | Full stage is completable via keyboard (`1–5`, `Arrows/WASD`, `Enter`), **but**: (1) global `window` `keydown` listener hijacks `Enter`/`Space` on focused header/reroll buttons and places a card instead (`t5_a11y.json`); (2) column-die nudges (`focusableDiceRows: 0`) are unreachable by keyboard; (3) **no non-color ownership cue** (`hasNonColorOwnerCue: false`, deuteranopia border contrast drops to **1.78:1**, grayscale **1.89:1**); (4) **58.1% of text elements (61/105) are `< 11px`** (down to `8.5px`); and (5) **`prefers-reduced-motion: reduce` is completely ignored** (13–14 infinite animations + `2.34 px` screen shake). |

---

## 1. T1: 4-Stage Drag-and-Drop Campaign (`t1_campaign.json`)

All 4 campaign stages were completed back-to-back in a single browser session using real mouse drag-and-drop gestures (`mouse.move` $\to$ `mouse.down` $\to$ 18-step interpolated `mouse.move` $\to$ `mouse.up`), advancing between stages via the `#result-modal` **Next Stage ▶** button.

### 1.1 Stage-by-Stage Campaign Summary

| Stage | Stage Index | Turns | Outcome | Final Score (Blue–Red) | Modal Title | Hand Left | Gesture-to-Commit (Turn 0 / Turns 1–3) | Stage Time | Next Stage Loaded |
|---|---|---|---|---|---|---|---|---|---|
| **Stage 1: Skystone Sanctuary** | `0` | 4 | **WIN** | `7 – 2` | `🏆 VICTORY (7 – 2)!` | 1 | `1189 ms` / `673–674 ms` | `8,508 ms` | Yes (`stageSelect="1"`) |
| **Stage 2: Ivalice Law Sanctuary** | `1` | 4 | **WIN** | `6 – 3` | `🏆 VICTORY (6 – 3)!` | 1 | `1109 ms` / `672–673 ms` | `8,472 ms` | Yes (`stageSelect="2"`) |
| **Stage 3: Costa del Sol Mirage** | `2` | 4 | **WIN** | `7 – 2` | `🏆 VICTORY (7 – 2)!` | 1 | `1108 ms` / `672–673 ms` | `8,403 ms` | Yes (`stageSelect="3"`) |
| **Stage 4: Gold Saucer Colosseum** | `3` | 4 | **WIN** | `6 – 3` | `🏆 VICTORY (6 – 3)!` | 1 | `1106 ms` / `671–686 ms` | `8,448 ms` | Yes (wraps to `"0"`) |
| **Total / Aggregate** | `0 → 3` | **16** | **4/4 WIN** | **Avg `6.5 – 2.5`** | **100% Consistent** | **1 / match** | **Misdrops: `0`** | **`36,991 ms`** | **100%** |

### 1.2 Turn-Level Telemetry & Capture Fidelity

Every single turn across all 4 stages (`16/16` deploys) landed on the intended tile on the first drag (`landed: true`, `committed: true`, `misdrops: []`), and observed captures matched the rules engine's predicted captures `16/16` times (`100%`):

- **Stage 1 (`t1_stage1_start.png` $\to$ `t1_stage1_result.png`):**
  - T0: `h_arbiter` $\to$ `(0,0)` (pred `1`, obs `1`, boss flips `1`, score `1–2`)
  - T1: `h_seraph` $\to$ `(1,2)` (pred `1`, obs `1`, boss flips `0`, score `3–2`)
  - T2: `h_kai` $\to$ `(1,1)` (pred `2`, obs `2`, boss flips `1`, score `5–2`)
  - T3: `h_chronos` $\to$ `(2,0)` (pred `1`, obs `1`, boss flips `0`, final `7–2`)
- **Stage 2 (`t1_stage2_start.png` $\to$ `t1_stage2_result.png`):**
  - T0: `h_oracle` $\to$ `(0,0)` (`+1/-1`, `1–2`); T1: `h_seraph` $\to$ `(0,2)` (`+1/-0`, `3–2`); T2: `h_archangel` $\to$ `(1,2)` (`+1/-0`, `5–2`); T3: `h_phoenix` $\to$ `(2,2)` (`+0/-0`, final `6–3`).
- **Stage 3 (`t1_stage3_start.png` $\to$ `t1_stage3_result.png`):**
  - T0: `h_seraph` $\to$ `(0,2)` (`+1/-1`, `1–2`); T1: `h_kai` $\to$ `(0,0)` (`+1/-0`, `3–2`); T2: `h_chronos` $\to$ `(1,2)` (`+1/-1`, `4–3`); T3: `h_archangel` $\to$ `(2,0)` (`+2/-0`, final `7–2`).
- **Stage 4 (`t1_stage4_start.png` $\to$ `t1_stage4_result.png`):**
  - T0: `h_seraph` $\to$ `(0,2)` (`+1/-0`, `2–1`); T1: `h_oracle` $\to$ `(1,0)` (`+1/-0`, `4–1`); T2: `h_phoenix` $\to$ `(2,1)` (`+1/-1`, `5–2`); T3: `h_chronos` $\to$ `(1,2)` (`+0/-0`, final `6–3`).

### 1.3 DOM, Event Listener & Memory Stability Across 4 Stages

Sampled at 21 checkpoints (`initial`, after each turn `s1t0..s4t3`, and after each stage reset `after_stage1..after_stage4`):

| Metric | Initial (`initial`) | Peak (`s3t3`) | After Stage 1 | After Stage 2 | After Stage 3 | After Stage 4 (`after_stage4`) | Leak Assessment |
|---|---|---|---|---|---|---|---|
| **Live DOM Nodes (`document.querySelectorAll('*')`)** | `235` | `277` | `249` | `256` | `251` | `246` | **No leak** (scales with occupied board slots; resets to `~246–256` between stages) |
| **CDP Total Nodes (`Performance.getMetrics`)** | `671` | `802` | `710` | `728` | `716` | `705` | **No leak** (`+34` total across 4 stages) |
| **JS Event Listeners (`JSEventListeners`)** | `72` | `85` | `85` | `85` | `85` | `85` | **No leak** (plateaus at exactly `85` after Stage 1) |
| **JS Heap Used (`JSHeapUsedSize`)** | `1.20 MB` (`1,258,422 B`) | `2.24 MB` | `2.14 MB` | `2.20 MB` | `2.25 MB` | `2.27 MB` (`2,375,196 B`) | **No leak** (stabilizes at `~2.2–2.3 MB` after JIT warm-up) |
| **Console / Page / Network / Image Errors** | `0` | `0` | `0` | `0` | `0` | `0` | **Clean** (`imgCheck: []`, `failedRequests: []`) |

---

## 2. T2 & T2b: Input Edge Cases & Race Condition Matrix (`t2_edge_cases.json`, `t2b_edge_cases.json`)

Eighteen input and state-transition edge cases were executed across `t2_edges.js` and `t2b_edges.js` (which refines timing to wait for the `120 ms` snap-to-slot commit before testing mid-boss-turn interactions).

### 2.1 Complete Edge Case Matrix

| # | Test Case | Input Sequence | Expected Behavior | Observed Behavior (`t2` + `t2b`) | Verdict |
|---|---|---|---|---|---|
| **1** | `dragDuringBossTurn` | Commit card $\to$ immediately drag another hand card during the `650 ms` boss delay (`s1.isPlayerTurn === false`) | Reject drag; do not create ghost or place card; show disabled/not-allowed feedback | Drag rejected (`ghostCreated: false`, `handAfterBoss: 4`), **but** hand cards retain `cursor: grab` with no visual/cursor indication why dragging is blocked (`screens/t2_drag_during_boss_turn.png`). | **PASS** *(P3 UX polish)* |
| **2** | `rapidDoubleClick` | Click-select hand card $\to$ `dblclick` empty tile; then click two different empty tiles `30 ms` apart | Place only 1 card per turn; ignore second click while `isPlayerTurn === false` | `dblclickPlacedCount: 1`, `twoTileRapidPlacedCount: 1`. Guard `!state.isPlayerTurn` in `deployCardToBoard()` prevents double-deploy. | **PASS** |
| **3** | `dropOnOccupied` | Drag hand card dead-center onto occupied boss tile `(0,1)` | Reject drop, spring ghost back to hand, leave `(0,1)` unchanged | `placed: 0`, `ghostLeft: 0`, `occupiedUnchanged: true` (`screens/t2_drop_on_occupied_mid.png`). | **PASS** |
| **4** | `dropOnOccupiedNearEdge` | Drag hand card onto `(0,1)` at `fx=0.12, fy=0.5` (near empty `(0,0)`) | Magnet snaps within `92 px` radius to nearest valid empty slot `(0,0)` | `placedSomewhere: 1`, `whereChanged: [0, 1]`. Works as designed by `findNearestValidSlot()` (`92 px` magnet radius). | **PASS** *(By Design)* |
| **5** | `dropOutsideBoard` | Drag hand card and release over: (a) `rightPanel` `(1350,201)`, (b) `header` `(700,20)`, (c) `handPanelOtherCard` `(208,434)`, (d) `belowBoard30px` `(748,760)`, (e) `leftOfBoard60px` `(475,459)` | Releases far off-board (`rightPanel`, `header`, `handPanel`) cancel & spring back; releases within `92 px` of a tile center (`belowBoard30px`, `leftOfBoard60px`) snap if magnet is active | Far releases (`rightPanel`, `header`, `handPanelOtherCard`) cleanly cancel (`placed: 0`, `ghostAfter: 0`, `passStrict: true`). However, releasing `30 px` below the board `(748,760)` or `60 px` left of the board `(475,459)` still triggers the `92 px` magnet and places the card onto `[2,1]` / `[1,0]`! Additionally, in `t2`, dragging from card 0 to `handPanel` `(208,434)` after a prior move placed a card because `onSlotClick` / magnet state wasn't isolated. | **WARN / FAIL** *(Magnet extends 30–60 px outside board slab)* |
| **6** | `escMidDrag` | Hold drag over valid tile $\to$ press `Escape` $\to$ release mouse $\to$ drag again | Cancel active drag immediately, remove ghost, do not place on `mouseup`, allow subsequent drags | `ghostAfterEsc: 0`, `dragActiveAfterEsc: false`, `placedAfterRelease: 0`, `dragWorksAfterEsc: true`. | **PASS** |
| **7** | `windowBlurMidDrag` | Hold drag $\to$ dispatch `window` `blur` event (and test multi-tab switch) | `window` `blur` listener cancels drag and cleans up ghost | `dispatchedBlur`: `ghostAfterBlur: 0, placed: 0, ghostAfter: 0`. (Note: headless Chromium `bringToFront` does not fire `blur`, and there is no `visibilitychange` listener.) | **PASS** |
| **8** | `dragBoardCardSlideUsed` | Perform valid Tactical Slide $\to$ attempt a second board-card drag on the same turn | Block second slide (`state.usedSlideThisTurn === true`); no ghost; board unchanged | `firstSlideOk: true`, `secondDrag: { ghost: 0, boardChanged: false }`. However, `cursorOnUsedBoardCard` stays `"pointer"` (`screens/t2_slide_used_second_drag.png`). | **PASS** *(P3 cursor polish)* |
| **9** | `clickSelectThenDragOther` | Click-select hand card `0` $\to$ drag hand card `2` (`h_arbiter`) to board | Deploy the dragged card (`h_arbiter`), not the previously click-selected card | `expected: "h_arbiter"`, `placed: "p:h_arbiter"`. | **PASS** |
| **10** | `resetMidDrag` | Hold mouse drag on hand card `1` (`h_arbiter`) $\to$ tap header **Reset** via touch $\to$ release mouse | `startStage()` should cancel any active drag (`cancelDrag(true)`) so releasing the mouse does nothing | **FAIL:** `startStage()` does **not** reset `drag`. Releasing the mouse after Reset commits `drag.handIndex` (`1`) from the **newly dealt hand** (`placedAfterRelease: "p:h_chronos"`, `placedCardMatchesGhost: false`) (`screens/t2_reset_mid_drag.png`). | **FAIL (P1 Bug)** |
| **11** | `stageSelectMidDrag` | Hold mouse drag on hand card `1` (`h_valkyrie`) $\to$ change `#stage-select` to Stage 3 $\to$ release mouse | Changing stage should cancel active drag and remove `.drag-ghost` | **FAIL:** `.drag-ghost` remains on screen (`ghostStillShown: 1`) and releasing the mouse places `h_arbiter` (index 1 of Stage 3's new hand) onto the new stage's board (`placedCardMatchesGhost: false`). | **FAIL (P1 Bug)** |
| **12** | `resetDuringSnapAnimation` | Release drag over `(1,1)` $\to$ during the `120 ms` snap-to-slot animation, click **Reset** | Reset should cancel the pending `120 ms` `finishSnap()` timeout | **FAIL:** The orphaned `120 ms` timeout fires on the newly reset board, deploying the card (`cardsAfter.p = 1`) and then triggering a boss move (`cardsAfter.a = 2`, `nudges: 3`) (`screens/t2_reset_during_snap.png`). | **FAIL (P0 Bug)** |
| **13** | `resetButtonMidBossTurn` | Commit card $\to$ during the `650 ms` boss turn delay, click **Reset** | Reset should clear the pending `executeBossTurn` timeout; fresh board should have `0` player cards, `1` boss card, `2` nudges | **FAIL:** `setTimeout(executeBossTurn, 650)` is never cleared! Right after Reset the board has `{p:0, a:1, e:8}`, but `<650 ms` later the stale boss turn fires onto the fresh board, leaving **2 boss cards (`{p:0, a:2, e:7}`)** and `nudgesAfter: 3` (`screens/t2_resetButton_mid_boss_turn.png`). | **FAIL (P0 Bug)** |
| **14** | `stageSelectMidBossTurn` | Commit card $\to$ during the `650 ms` boss turn delay, switch `#stage-select` | Switching stage should cancel the pending `executeBossTurn` timeout | **FAIL:** Same uncanceled timer bug — the old stage's boss turn fires onto the newly selected stage (`cardsAfter1200ms: {p:0, a:2, e:7}`, `nudgesAfter: 3`) (`screens/t2_stageSelect_mid_boss_turn.png`). | **FAIL (P0 Bug)** |
| **15** | `resetDuringGameOverDelay` | Place final card $\to$ after `state.gameOver` is set, during the `460 ms` delay before `#result-modal` opens, click **Reset** | Reset should cancel the pending modal timeout; fresh board should not have a victory modal | **FAIL:** `setTimeout(() => showResultModal(...), 460)` fires on the freshly reset board (`modalVisibleOnFreshBoard: true`, `freshBoardCards: {p:0, a:1, e:8}`, `modalTitle: "🏆 VICTORY (6 – 3)!"`) (`screens/t2_reset_during_gameover_delay.png`). | **FAIL (P1 Bug)** |
| **16** | `nudgeRerollSpam` | Click a column die 10× rapidly; click **Roll All 3D Dice** 10× rapidly; click die during boss turn | Clamp at `0` remaining nudges/rerolls; ignore clicks during boss turn | State clamps properly (`nudgesAfter10Clicks: 0`, `rerollsAfter10Clicks: 0`, `nudgeDuringBossTurnChangedDice: false`). **However**, exhausted controls never look disabled: `#reroll-btn` keeps `disabled: false, opacity: "1", cursor: "pointer"`, and `.col-die-row` keeps `opacity: "1", cursor: "pointer"` (`screens/t2_nudge_reroll_spam.png`). | **PASS** *(P2 Visual State Bug)* |
| **17** | `fastFlick` & `oneStepFlick20x` | Drag from hand to tile in `steps=1, 2, 3, 5` with `0 ms` hold before `mouseup`; also 20× 1-step flicks (`t2b`) | Fast 1-step flicks that land on a valid tile should still place the card | **FAIL on 1-step flicks:** `steps=1` at tile center (`fx=0.5, fy=0.5`) placed **0/8** in `t2` and **0/20 (`0%`)** in `t2b` (`oneStepFlick20x`). Why? `onDragPointerDown` sets `drag.started = false`; a single `pointermove` to `(tx, ty)` crosses the `6 px` threshold and calls `activateDragGhost()`, which sets `drag.started = true` and `return`s early **without** computing `drag.target = findNearestValidSlot(...)`! If `pointerup` arrives next, `drag.target` is still `null`, so the card springs back to hand. (`steps >= 2` succeeds `21/21` at center). Also, off-edge releases (`fx=1.06` or `fy=-0.05`) get pulled into adjacent tiles `3/7` and `4/7` times by the `92 px` magnet. | **FAIL (P1 Bug)** |
| **18** | `enterKeyMidDrag` & `digitAndRerollKeysMidDrag` | While holding a mouse drag on a card, press `Enter`, `4`, or `R` | Keyboard shortcuts should be ignored while `drag.active` is true | **FAIL (`enterKeyMidDrag`):** Pressing `Enter` mid-drag deploys a card onto `state.focusedSlotIndex` *while the drag ghost is still held* (`placedDuringDrag: 1, ghostStillUp: 1`), and releasing the mouse fails/corrupts the turn (`t2_edge_cases.json`). Pressing `4` and `R` mid-drag also mutates `state.selectedHandIndex` (`selDuringDrag: 3`) and consumes a dice reroll (`rerollsDuringDrag: 1`) mid-drag! | **FAIL (P1 Bug)** |
| **19** | `secondPointerUpEndsDrag` | Hold mouse drag over `(2,2)` $\to$ tap `(700, 790)` with a second (touch) pointer | Foreign `pointerId` should be ignored during an active drag | **FAIL:** `onDragPointerUp` / `onDragPointerCancel` do not check `e.pointerId === drag.pointerId`. The foreign touch `pointerup` immediately commits the held mouse drag (`placedByForeignPointerUp: 1, ghostAfterTouch: 0`). | **FAIL (P2 Bug)** |

---

## 3. T3 & T3b: 7-Viewport Responsiveness, Hit-Testing & Layout Shift Matrix (`t3_viewports.json`, `t3b_hit_and_shift.json`)

Tested across 7 viewports: 5 desktop sizes (`1024×768`, `1280×720`, `1280×800`, `1440×900`, `1920×1080`) and 2 tablet touch viewports (`ipad_portrait_820x1180`, `ipad_landscape_1180x820` with `hasTouch: true, isMobile: true` and real CDP `Input.dispatchTouchEvent` gestures).

### 3.1 7-Viewport Visibility, Overflow & Interaction Matrix

| Viewport | `docScroll` (`sw × sh`) | Right Header Hidden % | Right Panel (`bossPanelAside`) Hidden % | `dicePanel` & `rerollBtn` Hidden % | `telegraphHud` Hidden % | Board / Tiles Hidden % | Center Hit-Test (All 9 Tiles) | Corner Hit-Test (All 9 Tiles) | Click-to-Place (`t3b`) | Drag / Touch Place | Hover Grid Shift (`gridLeftRangePx`) | Hover Aside Shift (`asideLeftRangePx`) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`1024×768`** | `1333 × 768` | **54.1%** | **100.0%** | **100.0%** | **18.9%** | `0%` | `9/9` OK | `3/9` OK (Rows 1–2 fail) | `8/8` | Mouse Drag: **OK** | **`44 px`** | **`89 px`** |
| **`1280×720`** | `1333 × 720` | **9.2%** | **76.4%** | **79.3%** | `0%` | `0%` | `6/9` OK (Row 2 fails) | `6/9` OK (Row 1 `tl` fails) | `8/8` | Mouse Drag: **OK** | **`59 px`** | **`119 px`** |
| **`1280×800`** | `1333 × 800` | **9.2%** | **74.9%** | **77.6%** | `0%` | `0%` | `9/9` OK | `6/9` OK (Row 1 fails) | `8/8` | Mouse Drag: **OK** | **`6 px`** | **`11 px`** |
| **`1440×900`** | `1440 × 900` | `0%` | **14.3%** | **10.4%** | `0%` | `0%` | `9/9` OK | `6/9` OK (Row 1 `tl` fails) | **`5/8` FAIL** (Row 2 `(2,0..2)` fail!) | Mouse Drag: **OK** | **`29 px`** | **`59 px`** |
| **`1920×1080`** | `1920 × 1080` | `0%` | `0%` | `0%` | `0%` | `0%` | `6/9` OK (Row 1 center fails) | `3/9` OK (Rows 1–2 `tl` fail) | `8/8` | Mouse Drag: **OK** | `0 px` | `0 px` |
| **`ipad_portrait` (`820×1180`)** | `1333 × 1919` | **89.9%** | **100.0%** | **100.0%** | **37.6%** | Board **31.2%**, Col 2 tiles **91.2–93.1% hidden** | `6/9` OK (Col 2 off-screen) | `0/9` OK | N/A | Touch Drag: **OK**, Touch Tap: **FAIL** | N/A | N/A |
| **`ipad_landscape` (`1180×820`)** | `1333 × 927` | **26.8%** | **100.0%** | **100.0%** | **1.2%** | `0%` | `9/9` OK | `6/9` OK (Row 1 `tl` fails) | **`7/8` FAIL** (`(0,0)` fails) | Touch Drag: **OK**, Touch Tap: **OK** | **`41 px`** | **`81 px`** |

### 3.2 Three Structural Layout & Hit-Testing Bugs Identified in T3 / T3b

1. **P0 — Right Panel (3D Dice, Reroll Button, Boss Profile, Turn Badge) Completely Unreachable at $\le 1280\text{px}$ and Clipped at `1440×900`:**
   - The main layout uses `grid-template-columns: 264px minmax(0, 1fr) 264px` on `main`, paired with `body { overflow: hidden; height: 100vh }`.
   - Because `#telegraph-hud` (`white-space: nowrap`, `875–917 px` wide) and `#header-right` (`570 px` wide) do not shrink below `1333 px` total document width (`docScroll.sw = 1333`), the middle `1fr` column expands to `~880–920 px` and pushes the right `264 px` `aside` (`bossPanelAside`) off the right edge of the viewport (`left = 1214–1221 px`), where `body { overflow: hidden }` clips it with **no scrollbar**.
   - At `1024×768` (`screens/t3_vp_1024x768.png`) and `1180×820` (`screens/t3_vp_ipad_landscape_1180x820.png`), **100% of the dice panel, reroll button, and boss profile are invisible and unclickable**. At `1280×720` (`screens/t3_vp_1280x720.png`) and `1280×800` (`screens/t3_vp_1280x800.png`), **75%–79% of the right panel is cut off**. Even at `1440×900` (`screens/t3_vp_1440x900.png`), **14.3% of the right panel (`10.4%` of dice rows and reroll button)** is clipped when a long telegraph description is shown!
   - On `ipad_portrait_820x1180` (`screens/t3_vp_ipad_portrait_820x1180.png`), mobile emulation scales the page inconsistently (`sw=1333, sh=1919`) and clips **31.2% of the board** and **91.2%–93.1% of Column 3 tiles `(0,2)`, `(1,2)`, `(2,2)`**.

2. **P1 — Horizontal Board & Panel Layout Shift (`41–59 px` Grid Shift, `81–119 px` Aside Shift) on Hand Card Hover (`t3b_hit_and_shift.json`):**
   - `#telegraph-hud-desc` has `white-space: nowrap` and changes text length whenever the player hovers or selects a different card in hand (from 96 chars / `798 px` up to 123 chars / `917 px`).
   - Because the middle grid column has no `overflow: hidden` or fixed width on `#telegraph-hud`, hovering across the 5 hand cards causes the centered 3×3 board (`#grid-3x3`) to **jump horizontally by `59 px` at `1280×720`**, **`44 px` at `1024×768`**, **`41 px` at `1180×820`**, and **`29 px` at `1440×900`**, while the right panel jumps by **`59–119 px`** (`screens/t3b_1280x720_hover_last_card.png`, `screens/t3b_1440x900_hover_last_card.png`).

3. **P1 — 3D Perspective Plane (`transform-style: preserve-3d`) Occludes Pointer Hit-Testing on Board Tiles (`t3b_hit_and_shift.json`):**
   - `#board-3d-slab` uses `transform: rotateX(5deg); transform-style: preserve-3d` and `.board-slot` uses `transform: translateZ(...)`. In Chromium's 3D hit-testing, the parent `DIV.grid-3x3` or `DIV.board-3d-slab` plane intersects the 3D-transformed `.board-slot` planes and steals `elementFromPoint(x, y)` hits:
     - At `1280×720`, `elementFromPoint` at the **dead center** of Row 2 tiles `(2,0)`, `(2,1)`, `(2,2)` hits `DIV.grid-3x3` instead of `.board-slot`!
     - At `1920×1080`, `elementFromPoint` at the **dead center** of Row 1 tiles `(1,0)`, `(1,1)`, `(1,2)` hits `DIV.grid-3x3`!
     - At `1440×900`, **real mouse click-to-place fails on all 3 bottom-row tiles `(2,0)`, `(2,1)`, `(2,2)` (`clickToPlaceOk: "5/8"`)** because the click lands on `DIV.grid-3x3` / `DIV.board-3d-slab` (which has no click listener; only `.board-slot` has `onclick`). Drag-and-drop only succeeds there because `onDragPointerMove` uses geometric bounding-box distance (`findNearestValidSlot`) rather than DOM hit-testing.

---

## 4. T4: Frame Timing, Drag Performance & Resource Profiling (`t4_perf.json`)

Executed via `ux_qa/t4_perf.js` at `1408×800` under both **1× native CPU** and **4× CDP CPU throttling** (`Emulation.setCPUThrottlingRate: 4`) across three 3-second scenarios:
1. **`idle`**: 3.0 s static board with ambient CSS animations running.
2. **`hoverSweep`**: 3.0 s continuous orbital mouse sweep across all 9 tiles (`~360` pointer moves).
3. **`drag`**: 3.0 s continuous card drag across all 9 tiles (`174` pointer moves at 1×, `158` at 4×) with `.drag-ghost` active and live SVG telegraph recalculations.

### 4.1 Frame Timing & `renderAll()` Execution Table

| CPU Rate | Scenario | Frames (3 s) | Avg Frame (`avgMs`) | p95 (`p95Ms`) | p99 (`p99Ms`) | Max Frame (`maxMs`) | Frames `>20ms` | Frames `>33.4ms` | Frames `>50ms` | Long Tasks (`>50ms`) | `renderAll()` Calls | `renderAll()` Avg / Max (`ms`) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CPU 1×** | `idle` | `180` | `16.67 ms` | `16.70 ms` | `16.80 ms` | `16.80 ms` | `0` | `0` | `0` | `0` | `0` | `0.00 / 0.00 ms` |
| **CPU 1×** | `hoverSweep` | `362` | `8.31 ms` | `16.70 ms` | `16.80 ms` | `16.80 ms` | `0` | `0` | `0` | `0` | `33` | **`0.42 / 0.80 ms`** |
| **CPU 1×** | `drag` (`174` moves) | `181` | `16.67 ms` | `16.70 ms` | `16.80 ms` | `16.80 ms` | `0` | `0` | `0` | `0` | `23` | **`0.47 / 0.70 ms`** |
| **CPU 4×** | `idle` | `181` | `16.67 ms` | `16.70 ms` | `16.80 ms` | `16.80 ms` | `0` | `0` | `0` | `0` | `0` | `0.00 / 0.00 ms` |
| **CPU 4×** | `hoverSweep` | `360` | `8.36 ms` | `16.70 ms` | `16.80 ms` | `33.30 ms` | `1` | `0` | `0` | `0` | `35` | **`1.41 / 2.50 ms`** |
| **CPU 4×** | `drag` (`158` moves) | `182` | `16.67 ms` | `16.70 ms` | `16.80 ms` | `16.80 ms` | `0` | `0` | `0` | `0` | `21` | **`1.68 / 2.50 ms`** |

### 4.2 Key Performance Findings

- **Smart Drag Rendering Optimization Works Well:** During `drag`, `onDragPointerMove` updates `.drag-ghost`'s `transform: translate3d(...)` directly on every pointer move (`174` moves in 3 s) and **only calls `renderAll()` when the nearest target slot changes** (`23` calls at 1×, `21` calls at 4×). Even under 4× CPU throttling, `renderAll()` takes just `1.68 ms` avg (`2.50 ms` max), producing **zero dropped frames (`0` frames `>20 ms`)** and **zero Long Tasks**.
- **Zero Redundant Image Fetches During Drag/Re-render:** `imageRequestsAtLoad: 9`, `imageRequestsDuringDrag: 0`, `brokenImages: []`, `resourceErrors: { failed: [], bad: [] }`. Even though `renderAll()` rebuilds `#grid-3x3` and `#hand-bar` via `innerHTML`, browser HTTP caching prevents network re-requests for the 9 card PNGs.

---

## 5. T5: Accessibility, Keyboard, Contrast & Color-Vision Analysis (`t5_a11y.json`, `t5_color_analysis.json`)

### 5.1 Keyboard-Only Play & Focus Hijacking (`t5_a11y.json`)

1. **Keyboard-Only Stage Completion (`keyboardOnlyGame`):**
   - A full stage was played and won (`🏆 VICTORY (7 – 2)!`) using **only** keyboard events (`1–5` to select hand card, `ArrowUp/Down/Left/Right` to move board focus, `Enter` to deploy, `Tab` $\times 7$ + `Enter` on `Next Stage ▶`).
2. **P1 Bug — Global `keydown` Listener Hijacks `Enter` and `Space` on Focused `<button>` Elements:**
   - `handleHarnessKeyDown` (registered on `window`) intercepts `Enter` and `Space` with `e.preventDefault()` and calls `activateFocusedSlot()` **without checking `document.activeElement`**!
   - **`enterOnFocusedResetButton` (`pass: false`):** When the user tabs to the header **↻ Reset** button and presses `Enter`, **Reset is never triggered** — instead, the game deploys a card from the player's hand onto `state.focusedSlotIndex` (`cardPlacedInstead: true`, hand shrinks from `5` to `4`)!
   - **`spaceOnFocusedRerollButton` (`pass: false`):** When the user tabs to **🎲 Roll All 3D Dice** and presses `Space`, **the dice do not reroll** (`rerollsBefore: 2, rerollsAfter: 2`) — instead, a card is deployed onto the board (`cardPlaced: true`)!
   - **`arrowOnFocusedStageSelect`:** Pressing `ArrowDown` while `#stage-select` is focused simultaneously moves the board focus (`boardFocusMoved: true`).
3. **P1 Bug — Column 3D Dice Nudge Rows Are Unreachable by Keyboard (`focusableDiceRows: 0`):**
   - Only 5 elements in the main UI are tab-focusable (`#camera-select`, `#stage-select`, `⚡ Pulse Telegraphs`, `↻ Reset`, `🎲 Roll All 3D Dice`).
   - `.col-die-row` elements are `<div onclick="nudgeColDie(idx)">` with no `tabindex`, no `role="button"`, and no keyboard shortcut (`1–5` are bound to hand cards), making the core **Nudge (+1)** mechanic **100% inaccessible to keyboard-only players**.
4. **P2 Bug — No Dedicated Board Focus Indicator on Occupied Tiles & No Modal Focus Trap:**
   - Keyboard board navigation (`Arrow`/`WASD`) reuses `state.hoveredSlot = state.focusedSlotIndex`, which applies `.hover-preview` **only on empty tiles** (`slotClassesAfterNav: ["board-slot hover-preview", ...]`, `hasDedicatedFocusClass: false`). When `focusedSlotIndex` is on an **occupied tile** (e.g. `(0,1)` in `screens/t5_focus_at_0_1_occupied.png`, which is required to initiate a keyboard Tactical Slide), there is no focus ring on the occupied tile itself.
   - When `#result-modal` opens (`screens/t5_keyboard_modal_focus.png`), focus is not moved into the modal (`modalAutoFocused: false`, `modalRoleDialog: false`), requiring **6–7 `Tab` presses** through background header/sidebar buttons to reach `Play Again` / `Next Stage ▶`.
   - Zero ARIA live regions (`ariaLiveRegions: 0`) and zero board roles (`rolesOnBoard: 0`).

### 5.2 Color-Only Ownership & CVD / Grayscale Distinguishability (`t5_color_analysis.json`)

- **Zero Non-Color Ownership Cues (`hasNonColorOwnerCue: false`):**
  - Comparing computed styles and DOM structure of `.card-3d-unit.owner-player` vs `.card-3d-unit.owner-ai` (`t5_a11y.json`) confirms that once a card is on the 3×3 board, **ownership is communicated exclusively by border/glow color** (`rgb(0, 229, 255)` cyan vs `rgb(255, 46, 84)` red). There is no "YOU"/"BOSS" badge, faction icon, corner glyph, or border pattern difference (`playerTextNoDigits: "Sun Arbiter"`, `aiTextNoDigits: "Bastion Dreadnought"`).
- **Measured Border Contrast Across Vision Profiles (`t5_color_analysis.json`, 614 player & 627 AI border pixels sampled):**

| Vision Profile | Screenshot | Player Border Median RGB | AI Border Median RGB | Border-vs-Border Contrast Ratio | CIE $\Delta E_{76}$ | Meets 3:1 Non-Text UI Contrast (WCAG 1.4.11)? |
|---|---|---|---|---|---|---|
| **Theoretical (`#00E5FF` vs `#FF2E54`)** | — | `[0, 229, 255]` (`L=0.633`) | `[255, 46, 84]` (`L=0.239`) | `2.37 : 1` | `129.4` |Luminance contrast < 3:1 (relies on hue) |
| **Normal Vision (`none`)** | `screens/t5_cvd_none.png` | `[0, 225, 250]` | `[251, 46, 83]` | `2.34 : 1` | `127.5` | Hue-distinct, luminance < 3:1 |
| **Deuteranopia (`deuteranopia`)** | `screens/t5_cvd_deuteranopia.png` | `[175, 196, 250]` | `[161, 147, 77]` | **`1.78 : 1`** | `70.6` | **FAIL (`1.78 : 1` luminance contrast)** |
| **Protanopia (`protanopia`)** | `screens/t5_cvd_protanopia.png` | `[203, 216, 252]` | `[111, 105, 83]` | `3.86 : 1` | `53.2` | Pass luminance (`3.86 : 1`), reduced chroma |
| **Tritanopia (`tritanopia`)** | `screens/t5_cvd_tritanopia.png` | `[0, 236, 232]` | `[255, 0, 64]` | `2.66 : 1` | `141.4` | Hue-distinct |
| **Achromatopsia (`achromatopsia`)** | `screens/t5_cvd_achromatopsia.png` | `[204, 204, 204]` | `[132, 132, 132]` | **`2.33 : 1`** | **`26.9`** | **FAIL (`< 3.0 : 1`, zero hue, no icon/label)** |
| **Rec.601 Grayscale (`grayscale_L`)** | `screens/t5_grayscale_board.png` | `Gray 161` | `Gray 113` | **`1.89 : 1`** | — | **FAIL (`1.89 : 1`)** |

### 5.3 WCAG 2.1 Text Contrast Audit & Micro-Typography Census (`t5_a11y.json`)

Out of **30 semantic UI text elements** audited for WCAG AA contrast (`4.5:1` normal text):
- **27 / 30 PASS** (with strong ratios between `5.17:1` and `19.00:1`).
- **3 / 30 FAIL WCAG AA (`< 4.5:1`):**
  1. **`OPEN tile label` (`#grid-3x3 .board-slot:not(.occupied) > div`)**: `rgba(148, 163, 184, 0.34)` on `rgb(8, 14, 30)` $\to$ **`1.87 : 1`** (`10.5px`, weight `800`) — **severe fail** on boosted column hint text (`⚡ +1 BOOST` / `OPEN`).
  2. **`brand badge` (`CARDFRONT 3D`)**: `rgb(248, 250, 252)` on `rgb(255, 46, 84)` $\to$ **`3.48 : 1`** (`10px`, weight `900`).
  3. **`VS` scoreboard divider (`.scoreboard > span`)**: `rgb(100, 116, 139)` on `rgb(10, 17, 34)` $\to$ **`3.95 : 1`** (`11px`, weight `800`).

- **Micro-Typography Census (`smallFonts`):**
  - Across **105 visible text elements** (excluding SVGs and hidden modal), **61 elements (`58.1%`) render below `11px`**:
    - **`8.5px` (7 elements):** Hand card name ribbons (`Chronos Weaver`, `Astral Seraph`, `Kai Crimson Visor`), Tactical Slide card type (`MGA COST Clockwork (E+S+W)`), and slide status (`⇄ Slide: 1× Ready`).
    - **`9.0px` (1 element):** Tactical Slide title (`⚡ Temporal Gear Lock`).
    - **`9.5px` (26 elements):** All 20 hand card edge numbers, board card name ribbons (`Sigil Wraith`), die row hints (`Click to Nudge +1`), and telegraph HUD badge.
    - **`10.0px` (13 elements):** Section titles (`Hero Hand`, `5 CARDS`, `NUDGES: 2`, `YOUR TURN`), column headers (`COL 2 (DIE: 2)`), boss telegraph label.
    - **`10.5px` (14 elements):** Open tile labels (`OPEN`, `⚡ +1 BOOST`), dice help text, last-move banner.

### 5.4 `prefers-reduced-motion: reduce` Compliance (`t5_a11y.json`)

- **Result: FAIL (`pass: false`, `cssHasReducedMotionMedia: false`).**
- Grepping the HTML confirms zero `@media (prefers-reduced-motion: reduce)` rules and zero `matchMedia('(prefers-reduced-motion: reduce)')` checks in JavaScript.
- When emulated with `reducedMotion: "reduce"` (`mq: true`):
  - **13 infinite CSS animations** run continuously at idle (`14` after placement), identical to `no-preference`.
  - **Screen shake on card capture** (`#arena-viewport` inline transform shake) still runs for **22 frames** with a peak offset of **`2.34 px`** (`2.82 px` under `no-preference`).

---

## 6. Prioritized UX & Engineering Issues (P0 – P3)

### P0 — Critical Blockers (Broken Core Mechanics / State Corruption)

1. **[P0-1] Right Sidebar (3D Dice, Reroll Button, Boss Profile, Turn Badge) Clipped 75%–100% Off-Screen on All Viewports $\le 1280\text{px}$ (and 14% at `1440×900`)**
   - **Evidence:** `t3_viewports.json`, `screens/t3_vp_1024x768.png`, `screens/t3_vp_1280x720.png`, `screens/t3_vp_1280x800.png`, `screens/t3_vp_ipad_landscape_1180x820.png`.
   - **Root Cause:** `body { overflow: hidden }` combined with un-shrinking header/HUD flex items (`#telegraph-hud-desc { white-space: nowrap }`, `#header-right`) forces the document scroll width to `1333 px` and pushes the right `264 px` column off-viewport with no scroll bar.
   - **Fix:** Allow `#telegraph-hud-desc` to truncate (`overflow: hidden; text-overflow: ellipsis; min-width: 0`) inside a `min-width: 0` center track, wrap `.header-bar` controls at $\le 1360\text{px}$, and scale sidebar widths via `clamp(200px, 18vw, 264px)`.

2. **[P0-2] Uncanceled `setTimeout` Timers in `startStage()` Cause Stale Snap Commits, Extra Boss Moves, and Ghost Victory Modals After Reset / Stage Switch**
   - **Evidence:** `t2b_edge_cases.json` (`resetDuringSnapAnimation`, `resetButtonMidBossTurn`, `stageSelectMidBossTurn`, `resetDuringGameOverDelay`), `screens/t2_reset_during_snap.png`, `screens/t2_resetButton_mid_boss_turn.png`, `screens/t2_reset_during_gameover_delay.png`.
   - **Root Cause:** The `120 ms` `finishSnap` timer, `650 ms` `executeBossTurn` timer, and `460 ms` `showResultModal` timer are anonymous `setTimeout` calls whose IDs are never stored or cleared when `startStage()` runs (nor is a generation counter checked).
   - **Fix:** Increment a `state.matchGen` counter in `startStage()` (and call `cancelDrag(true)`), and guard every async callback with `if (gen !== state.matchGen) return;`.

### P1 — High-Priority Bugs (Input Drops, Layout Shifts, A11y Blockers)

3. **[P1-1] 3D Perspective Plane (`DIV.grid-3x3` / `DIV.board-3d-slab`) Intercepts `elementFromPoint` and Breaks Click-to-Place on Row 2 (`1440×900`: `5/8` Clickable)**
   - **Evidence:** `t3b_hit_and_shift.json` (`1440x900` `failedClicks` on `[2,0]`, `[2,1]`, `[2,2]`; `1280x720` and `1920x1080` `badHits`).
   - **Root Cause:** `transform-style: preserve-3d` on `#board-3d-slab` with `rotateX(5deg)` causes the parent slab/grid plane to sit in front of lower-row `.board-slot` elements in Chromium's hit-test tree.
   - **Fix:** Add `pointer-events: none` to `#board-3d-slab` and `#grid-3x3` while setting `pointer-events: auto` on `.board-slot` and `.col-header-pill` (or attach a fallback click listener on `#grid-3x3` that resolves coordinates via `findNearestValidSlot`).

4. **[P1-2] Hovering Hand Cards Shifts the 3×3 Board Horizontally by up to `59 px` (`aside` by `119 px`)**
   - **Evidence:** `t3b_hit_and_shift.json` (`gridLeftRangePx: 59` at `1280×720`, `44` at `1024×768`, `29` at `1440×900`), `screens/t3b_1280x720_hover_last_card.png`.
   - **Root Cause:** `#telegraph-hud-desc` uses `white-space: nowrap` inside an intrinsically sized flex/grid container, changing width (`798 px` to `917 px`) as card descriptions change on hover.
   - **Fix:** Set `min-width: 0; width: 100%; max-width: 760px` on `#telegraph-hud` and `overflow: hidden; text-overflow: ellipsis` on `#telegraph-hud-desc`.

5. **[P1-3] Fast 1-Step Flick Drags Fail 100% (`0/20`) Because `drag.target` Is Not Computed on the Threshold-Crossing `pointermove`**
   - **Evidence:** `t2_edge_cases.json` (`steps1_fx0.5_fy0.5`: `0/8`), `t2b_edge_cases.json` (`oneStepFlick20x`: `0/20`).
   - **Root Cause:** When `Math.hypot(dx, dy) >= 6` first triggers `activateDragGhost(e.clientX, e.clientY)`, `onDragPointerMove` returns or skips updating `drag.target` on that event, and `onDragPointerUp` relies solely on `drag.target` instead of calling `findNearestValidSlot(e.clientX, e.clientY)` on release.
   - **Fix:** Compute `drag.target = findNearestValidSlot(e.clientX, e.clientY)` inside `activateDragGhost()` and as a fallback in `onDragPointerUp()`.

6. **[P1-4] Global `keydown` Handler Hijacks `Enter`/`Space` on Focused Header & Reroll Buttons (`t5_a11y.json`) and Mid-Drag (`t2_edge_cases.json`)**
   - **Evidence:** `t5_a11y.json` (`enterOnFocusedResetButton.cardPlacedInstead: true`, `spaceOnFocusedRerollButton.cardPlaced: true`), `t2_edge_cases.json` (`enterKeyMidDrag.placedDuringDrag: 1`).
   - **Fix:** In `handleHarnessKeyDown`, return early if `drag.active || drag.dropping` or if `document.activeElement` is a `<button>`, `<select>`, or `<input>`.

7. **[P1-5] Reset or Stage-Select Mid-Drag Leaves Drag State Active and Deploys a Card from the New Hand on Release**
   - **Evidence:** `t2_edge_cases.json` (`resetMidDrag`, `stageSelectMidDrag`), `screens/t2_reset_mid_drag.png`.
   - **Fix:** Call `cancelDrag(true)` at the top of `startStage()`.

8. **[P1-6] Ownership Is 100% Color-Only (`1.78:1` Deuteranopia Border Contrast, `1.89:1` Grayscale) & Column Dice Cannot Be Nudged by Keyboard**
   - **Evidence:** `t5_color_analysis.json`, `t5_a11y.json` (`hasNonColorOwnerCue: false`, `focusableDiceRows: 0`), `screens/t5_cvd_deuteranopia.png`, `screens/t5_grayscale_board.png`.
   - **Fix:** Add a distinct owner badge/glyph (`◆ YOU` vs `▲ BOSS` or double/dashed frame) on board cards, and add `tabindex="0" role="button"` + `Enter`/`Space` handlers (and keys `Q/W/E` or `6/7/8`) to `.col-die-row`.

### P2 — Medium-Priority UX & Accessibility Issues

9. **[P2-1] `prefers-reduced-motion: reduce` Ignored (13–14 Infinite Animations + `2.34 px` Screen Shake)** (`t5_a11y.json`) — Add `@media (prefers-reduced-motion: reduce)` to disable infinite pulse/float animations and skip capture screen-shake.
10. **[P2-2] Micro-Typography (`58.1%` of Text Elements `< 11px`, Down to `8.5px`) & Low-Contrast Open-Tile Boost Label (`1.87:1`)** (`t5_a11y.json`) — Raise `.board-slot:not(.occupied) > div` alpha from `0.34` to `>= 0.72` (`>= 4.5:1` contrast) and increase minimum card/UI font sizes to `10.5–12px`.
11. **[P2-3] Exhausted Dice Reroll Button (`0 left`) and Nudge Rows (`NUDGES: 0`) Retain Active `cursor: pointer` and `opacity: 1`** (`t2_edge_cases.json`, `screens/t2_nudge_reroll_spam.png`) — Set `disabled = true` on `#reroll-btn` and `.exhausted` styling (`opacity: 0.45; cursor: not-allowed`) when counts reach `0`.
12. **[P2-4] Foreign `pointerup` Ends Active Drag (`secondPointerUpEndsDrag`) & Magnet Extends `30–60 px` Outside Board** (`t2b_edge_cases.json`) — Filter `onDragPointerMove`/`Up`/`Cancel` by `e.pointerId === drag.pointerId`, and clamp `findNearestValidSlot()` so points outside `#board-3d-slab`'s bounding box (+12 px pad) return `null`.

### P3 — Polish & Minor Ergonomics

13. **[P3-1] Hand Cards Keep `cursor: grab` During Boss Turn and Board Cards Keep `cursor: pointer` After Tactical Slide Used** (`t2_edge_cases.json`) — Switch to `cursor: not-allowed` or `default` when `!state.isPlayerTurn` or `state.usedSlideThisTurn`.
14. **[P3-2] `#result-modal` Does Not Auto-Focus Primary Action or Trap `Tab` Focus** (`t5_a11y.json`, `screens/t5_keyboard_modal_focus.png`) — Add `role="dialog" aria-modal="true"` and auto-focus the `Next Stage ▶` / `Play Again` button when opened.
