# CARDFRONT: Cradle of Echoes — Rules, State-Machine & Card Balance Audit

- **Target Deliverable**: [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](../../../WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Target SHA-256**: `6703e34c35fcff64540ba91eb6e210108cbf15d47bbce41a262fd586cf08dd55` ([`out/target_sha256.txt`](out/target_sha256.txt))
- **Harness & Repros**: [`repros/`](repros/) (`R01`–`R11`) with machine-readable outputs & screenshots in [`out/`](out/)
- **Static & Monte-Carlo Card Analysis**: [`analysis/A01_card_analysis.js`](analysis/A01_card_analysis.js) → [`analysis/cards.json`](analysis/cards.json), [`analysis/cards.md`](analysis/cards.md); [`analysis/S01_sim_real_page.js`](analysis/S01_sim_real_page.js) → [`analysis/sim.json`](analysis/sim.json)

---

## 1. Executive Summary

We audited the complete rules engine, asynchronous turn lifecycle, pointer drag-and-drop controller, keyboard accessibility handler, progression flow, and 16-card stat table of **CARDFRONT: Cradle of Echoes** (`WebPlayable/cardfront_cradle_of_echoes_playable.html`). Every finding below is backed by a deterministic headless Chromium Playwright reproduction script (`repros/R01_*.js` – `repros/R11_*.js`) and JSON/PNG evidence in `out/`.

### Summary Bug Table (`R01`–`R11`)

| ID | Severity | Category | Title / Failure Mode | HTML Lines | Repro & Evidence |
|---|---|---|---|---|---|
| **R01** | **P0** | Async Turn Lifecycle | Pending `setTimeout(executeBossTurn, 650)` survives `↻ Reset` and `#stage-select`, dropping extra boss cards onto the new board and granting the boss consecutive moves. | `L1546–1590`, `L1754`, `L1757–1806` | [`repros/R01_stale_boss_turn_after_reset.js`](repros/R01_stale_boss_turn_after_reset.js) · [`out/R01_stale_boss_turn_after_reset.json`](out/R01_stale_boss_turn_after_reset.json) · [`out/R01_after_double_boss_move.png`](out/R01_after_double_boss_move.png) |
| **R03** | **P0** | Drag + Keyboard Race | Keyboard deploy (`Enter`/`Space`) mid-hand-drag shrinks `state.hand` without cancelling `drag`; releasing the mouse restores a stale `handIdx`, writes `cardId: undefined, owner: "player"` into the grid, throws `TypeError`, and awards a phantom Blue point without ending the turn. | `L1429–1432`, `L1512–1513`, `L1719–1727`, `L2356–2379` | [`repros/R03_stale_hand_drag_undefined_card.js`](repros/R03_stale_hand_drag_undefined_card.js) · [`out/R03_stale_hand_drag_undefined_card.json`](out/R03_stale_hand_drag_undefined_card.json) · [`out/R03_phantom_cell.png`](out/R03_phantom_cell.png) |
| **R04** | **P0** | Drag + Ownership Validation | Starting a board slide-drag on a Blue unit, deploying via keyboard, and releasing after the boss captures that unit slides the **boss-owned** card and converts it back to `owner = "player"` (`handleSlotClick` never re-verifies `src.owner === "player"`). Also deploys the wrong hand card when `handIdx` shifts. | `L1687–1700`, `L2356–2379` | [`repros/R04_stale_board_drag_steals_card.js`](repros/R04_stale_board_drag_steals_card.js) · [`out/R04_stale_board_drag_steals_card.json`](out/R04_stale_board_drag_steals_card.json) · [`out/R04_stolen_card.png`](out/R04_stolen_card.png) |
| **R02** | **P1** | AI Rules / Determinism | Boss tie-breaking is 100% deterministic row-major (`(0,0)` first), never random: `bestSlot` is initialized randomly at `L1773`, but `bestCount = -1` (`L1774`) causes the first open slot (`f >= 0 > -1`) to unconditionally overwrite `bestSlot` at `L1779`. Confirmed across 480 boss turns (257 tie turns, 257/257 picked first row-major slot). | `L1773–1780` | [`repros/R02_boss_tiebreak_deterministic.js`](repros/R02_boss_tiebreak_deterministic.js) · [`out/R02_boss_tiebreak_deterministic.json`](out/R02_boss_tiebreak_deterministic.json) |
| **R05** | **P1** | Input State Machine | When a Blue board unit is selected for Tactical Slide (`state.selectedBoardSlot != null`, hand UI shows 0 cards selected), clicking any non-adjacent empty tile (or any empty tile after slide is already spent) falls through `handleSlotClick` and silently deploys `state.hand[state.selectedHandIdx]`, ending the turn. | `L1675–1730`, `L2073` | [`repros/R05_selected_unit_misclick_deploys.js`](repros/R05_selected_unit_misclick_deploys.js) · [`out/R05_selected_unit_misclick_deploys.json`](out/R05_selected_unit_misclick_deploys.json) |
| **R06** | **P1** | 3D DOM Hit-Test / Re-render | Real-mouse clicks on empty `⇄ SLIDE HERE` tiles fail in **10/30 (33.3%)** trials across camera presets (`5,0`, `0,0`, `14,0`), vs **0/30** for plain deploy clicks. Rebuilding `#grid-3x3` inside `onmouseenter`/`onmouseleave` (`L1971`, `L2007–2026`) in a `preserve-3d` scene causes hit-testing to land on `#grid-3x3` (7/30) or drops the click across DOM node replacement. | `L1970–2067` | [`repros/R06_empty_tile_click_swallowed.js`](repros/R06_empty_tile_click_swallowed.js) · [`out/R06_empty_tile_click_swallowed.json`](out/R06_empty_tile_click_swallowed.json) |
| **R07** | **P1** | Combat Stat Recalculation | `recalcBoardStats()` (`L1614–1623`) only updates cells where `cell.owner === "player"` and always passes `isAi = false`: (a) a boss card captured by the player in Stages 3–4 silently loses its `+1 aiBonus` the moment any column die is nudged/rerolled; (b) a player hero captured by the boss retains its stale column boost forever even after the column die drops below 4. | `L1512–1520`, `L1614–1623`, `L1703–1706`, `L1732–1735`, `L1789–1792` | [`repros/R07_recalc_asymmetry_captured_cards.js`](repros/R07_recalc_asymmetry_captured_cards.js) · [`out/R07_recalc_asymmetry_captured_cards.json`](out/R07_recalc_asymmetry_captured_cards.json) |
| **R08** | **P2** | Progression & Turn Economy | Four end-of-stage flaws: (a) `Next Stage ▶` is visible and active on the **DEFEAT** modal (`L1826–1846`), letting players advance by losing; (b) `Next Stage ▶` after Stage 4 wraps via `% STAGES.length` back to Stage 1 (`L1842`); (c) `executeBossTurn` sets `state.isPlayerTurn = true` (`L1801`) before `checkGameOver()`, leaving the badge reading `YOUR TURN` on a finished board; (d) 1 pre-placed boss card + 4 player deploys + 4 boss replies = 9 tiles, so the boss **always** gets the final move and 1 of the 5 dealt hero cards is **always** left unused in hand. | `L1577–1584`, `L1801–1805`, `L1820–1846` | [`repros/R08_next_stage_after_defeat_wraps.js`](repros/R08_next_stage_after_defeat_wraps.js) · [`out/R08_next_stage_after_defeat_wraps.json`](out/R08_next_stage_after_defeat_wraps.json) · [`out/R08_defeat_modal_next_stage.png`](out/R08_defeat_modal_next_stage.png) |
| **R09** | **P2** | Modal Timer Lifecycle | `checkGameOver()` schedules `result-modal` display via an untracked `setTimeout(..., 460)` (`L1826–1835`) and `startStage()` (`L1546`) neither clears that timer nor hides `#result-modal`. Clicking `↻ Reset` within 460 ms of game end pops the old Victory/Defeat modal on top of the fresh board (`gameOver === false`). | `L1546–1590`, `L1826–1835` | [`repros/R09_stale_result_modal_after_reset.js`](repros/R09_stale_result_modal_after_reset.js) · [`out/R09_stale_result_modal_after_reset.json`](out/R09_stale_result_modal_after_reset.json) · [`out/R09_stale_modal.png`](out/R09_stale_modal.png) |
| **R10** | **P2** | Keyboard / Focus Hijack | `handleHarnessKeyDown` (`L1410–1446`) listens on `window` without checking `document.activeElement` or modifier keys: pressing `Space` or `Enter` while a UI `<button>` (e.g., `🎲 Roll All 3D Dice`) has focus calls `e.preventDefault()` and deploys a hand card to `focusedSlotIndex` (`(1,1)` by default); pressing bare `r`/`R` anywhere silently spends a reroll. | `L1410–1446` | [`repros/R10_global_hotkeys_hijack_space.js`](repros/R10_global_hotkeys_hijack_space.js) · [`out/R10_global_hotkeys_hijack_space.json`](out/R10_global_hotkeys_hijack_space.json) |
| **R11** | **P3** | Production Hygiene / Telemetry | Debug automation hooks (`?autotest=1`, `?dragtest=1` at `L2402–2410`) ship in production, match via substring (`location.search.includes("autotest=1")`, so `?ref=xautotest=1` triggers auto-play), POST unsolicited JSON to `/__osascript_report__` (`L2407`, `L2484`, `L2656`), reference a non-existent `#cam-select` (`L2557`, actual ID is `#camera-select`), and report losses as `"COMPLETED"` rather than `"DEFEAT"` (`L2652`). | `L2400–2665` | [`repros/R11_debug_hooks_in_production.js`](repros/R11_debug_hooks_in_production.js) · [`out/R11_debug_hooks_in_production.json`](out/R11_debug_hooks_in_production.json) |

---

## 2. Detailed Bug Analysis & Suggested Code Fixes

### R01 (P0) — Pending Boss Turn Timer Survives `Reset` and Stage Select
- **Location**: `handleSlotClick` (`L1754`), `startStage` (`L1546–1590`), `executeBossTurn` (`L1757–1806`).
- **Root Cause**: `handleSlotClick` schedules `setTimeout(executeBossTurn, 650)` at `L1754` without storing the timer ID or binding it to a match generation token. When the player clicks `↻ Reset` or changes `#stage-select` during that 650 ms window, `startStage(idx)` resets `state` synchronously, then the stale timer fires `executeBossTurn()` against the **new** board.
- **Impact**:
  - **Case A (Reset during boss thinking)**: The fresh board starts with 2 Red cards instead of 1, `aiPool` shrinks from 5 to 4, and `nudgesLeft` is incremented to 3 before the player has taken a single turn.
  - **Case B (Stage switch + immediate player deploy)**: Two `executeBossTurn` timers are in flight simultaneously; both fire on the new board, giving the boss **two consecutive moves** (3 Red cards on the board after 1 player move; see [`out/R01_after_double_boss_move.png`](out/R01_after_double_boss_move.png)).
- **Suggested Fix**:
  ```js
  // Track timer IDs and a monotonically increasing gameId in state:
  let bossTurnTimer = null;
  let modalTimer = null;

  function clearPendingTimers() {
    if (bossTurnTimer !== null) { clearTimeout(bossTurnTimer); bossTurnTimer = null; }
    if (modalTimer !== null) { clearTimeout(modalTimer); modalTimer = null; }
  }
  ```
  Call `clearPendingTimers()` (and `teardownDrag()`) at the top of `startStage(idx)` (`L1546`), and assign `bossTurnTimer = setTimeout(executeBossTurn, 650)` at `L1754`.

---

### R02 (P1) — Boss Tie-Break Is 100% Deterministic Row-Major (Never Random)
- **Location**: `executeBossTurn` (`L1773–1780`).
- **Root Cause**:
  ```js
  let bestSlot = open[Math.floor(Math.random() * open.length)];
  let bestCount = -1;

  open.forEach(slot => {
    const stats = getCardEffectiveStats(aiCardId, slot.c, true);
    const f = findCaptures(slot.r, slot.c, stats, "ai").length;
    if (f > bestCount) { bestCount = f; bestSlot = slot; }
  });
  ```
  Because `findCaptures(...).length` is always `>= 0` and `bestCount` starts at `-1`, the very first element of `open` (`open[0]`) satisfies `f > -1` and overwrites the randomly chosen `bestSlot`. Subsequent slots only replace `bestSlot` on strict `>`. Thus the `Math.random()` call at `L1773` is dead code (aside from advancing the RNG state), and ties always resolve to the first open cell in row-major order `(0,0), (0,2), (1,0), ...`.
- **Evidence**: Across 120 games / 480 boss turns in `R02`, ties occurred on **257/480 (53.5%)** turns, and the boss picked `tied[0]` in **257/257 (100%)** tie turns (`(0,0)` was chosen on 84/120 first boss turns).
- **Suggested Fix**:
  ```js
  let bestCount = -1;
  let bestSlots = [];
  open.forEach(slot => {
    const stats = getCardEffectiveStats(aiCardId, slot.c, true);
    const f = findCaptures(slot.r, slot.c, stats, "ai").length;
    if (f > bestCount) { bestCount = f; bestSlots = [slot]; }
    else if (f === bestCount) { bestSlots.push(slot); }
  });
  const bestSlot = bestSlots[Math.floor(Math.random() * bestSlots.length)];
  ```

---

### R03 (P0) — Stale Hand-Drag Drop After Keyboard Deploy Corrupts Board (`cardId = undefined`)
- **Location**: `handleHarnessKeyDown` (`L1429–1432`), `onDragPointerUp` (`L2356–2379`), `handleSlotClick` (`L1719–1727`).
- **Root Cause**: Starting a pointer drag on the 5th hand card (`drag.handIdx = 4`) and pressing `Enter` or `Space` mid-drag deploys a card via `handleHarnessKeyDown`, shrinking `state.hand` to 4 cards while `drag.active` remains `true`. When the pointer is later released on an empty tile, `onDragPointerUp` sets `state.selectedHandIdx = drag.handIdx` (`4`) and calls `handleSlotClick(t.r, t.c)`. At `L1719–1727`:
  ```js
  const cardId = state.hand[state.selectedHandIdx]; // undefined!
  state.hand.splice(state.selectedHandIdx, 1);      // no-op when index >= length
  ...
  cell.cardId = cardId;                             // writes undefined
  cell.owner = "player";                            // marks cell as player-owned!
  cell.nesw = getCardEffectiveStats(cardId, c, false); // throws TypeError: Cannot read properties of undefined (reading 'nesw')
  ```
- **Impact**: The uncaught `TypeError` aborts `handleSlotClick` **after** `cell.owner = "player"` is written but **before** `state.isPlayerTurn = false` (`L1750`). The player gets a free phantom Blue point (`getScores()` only checks `cell.owner === "player"` at `L1812`) and keeps their turn (see [`out/R03_phantom_cell.png`](out/R03_phantom_cell.png)).
- **Suggested Fix**:
  1. Ignore keyboard actions while `drag.active || drag.dropping` in `handleHarnessKeyDown` (`L1411`), or cancel any active drag whenever a turn action executes.
  2. In `onDragPointerUp` (`L2366`), verify that `state.isPlayerTurn && !state.gameOver && state.hand[idx] === drag.cardId` before deploying.
  3. Guard `handleSlotClick` (`L1717`): `const cardId = state.hand[state.selectedHandIdx]; if (!cardId) return;`.

---

### R04 (P0) — Stale Board-Drag Moves & Converts a Boss-Captured Card (and Places Wrong Hand Card)
- **Location**: `handleSlotClick` (`L1687–1700`), `onDragPointerUp` (`L2356–2379`).
- **Root Cause**:
  - **Part A (Board Slide Steal)**: A player starts dragging a Blue board card at `(1,0)`, deploys a hand card with `Enter` (ending the turn), and waits while the boss captures `(1,0)` (so `state.grid[1][0].owner` becomes `"ai"`). When the player releases the mouse on adjacent empty `(0,0)`, `onDragPointerUp` sets `state.selectedBoardSlot = { r: 1, c: 0 }` and calls `handleSlotClick(0, 0)`. Because the Tactical Slide branch at `L1687–1700` checks `if (state.selectedBoardSlot && !cell.cardId)` **without verifying that `src.cardId && src.owner === "player"`**, it moves the boss's card to `(0,0)`, sets `cell.owner = "player"`, and even triggers player captures from `(0,0)`!
  - **Part B (Wrong Hand Card Placed)**: If a player drags `hand[0]` (`h_seraph`), presses `Enter` to deploy `hand[0]`, and then drops the ghost on the next turn, `drag.handIdx` (`0`) now points to the **shifted** `hand[0]` (`h_arbiter`), silently deploying a card the player never dragged.
- **Suggested Fix**:
  - In `handleSlotClick` (`L1688`):
    ```js
    const { r: sr, c: sc } = state.selectedBoardSlot;
    const src = state.grid[sr][sc];
    if (!src.cardId || src.owner !== "player") {
      state.selectedBoardSlot = null;
      renderAll();
      return;
    }
    ```
  - Cancel any active drag (`teardownDrag()`) whenever a turn ends (`L1750`) or `startStage` runs (`L1546`).

---

### R05 (P1) — Mis-Click While a Board Unit Is Selected Silently Deploys From Hand
- **Location**: `handleSlotClick` (`L1675–1730`), `renderAll` (`L2073`).
- **Root Cause**: When the player clicks a Blue board unit to select it for Tactical Slide (`state.selectedBoardSlot = { r, c }`), `renderAll()` hides the hand selection highlight (`const isSel = idx === state.selectedHandIdx && !state.selectedBoardSlot` at `L2073`). However, if the player then clicks an empty tile that is **not** a valid slide target (either `manhattanDistance !== 1` or `state.usedSlideThisTurn === true`), the `if (state.selectedBoardSlot && !cell.cardId)` block at `L1687–1715` does not return—execution falls straight through to `L1719` and deploys `state.hand[state.selectedHandIdx]`, consuming the player's turn!
- **Suggested Fix**:
  - Do not allow selecting a board unit when `state.usedSlideThisTurn` is already `true` (`L1675`).
  - When `state.selectedBoardSlot` is set and the player clicks an invalid empty tile (`L1687–1715`), clear `state.selectedBoardSlot = null; renderAll(); return;` (or play an error tone and return) instead of falling through to hand deployment.

---

### R06 (P1) — Real-Mouse Clicks on Slide-Target Tiles Swallowed by Hover Re-Render / 3D Hit-Test
- **Location**: `renderAll` (`L1970–2067`).
- **Root Cause**: Every `onmouseenter` and `onmouseleave` on an empty `.board-slot` mutates `state.hoveredSlot` and calls `renderAll()` (`L2018`, `L2025`), which executes `gridEl.innerHTML = ""` (`L1971`) and recreates all 9 `.board-slot` elements inside the 3D-tilted `#grid-3x3` (`transform-style: preserve-3d`). For a plain deploy hover (`L2048–2052`), the hovered slot is populated with a 3D `.card-3d-unit` preview card that projects forward in Z and reliably catches clicks (**0/30** lost). For a slide-target hover (`L2046–2047`), the slot only contains flat text (`⇄ SLIDE HERE`) while `buildBoardTelegraphOverlaySVG` (`L2062–2067`) appends an SVG overlay to `#grid-3x3`; across camera presets (`5,0`, `0,0`, `14,0`), **10/30 (33.3%)** real-mouse clicks on valid slide targets fail to execute (7/30 hit-test directly to `#grid-3x3`, which has no click handler).
- **Suggested Fix**:
  - Attach a single delegated `click` / `pointerup` listener on `#grid-3x3` (using `e.target.closest(".board-slot")` with fallback to bounding-box hit-testing via `findDropTarget(e.clientX, e.clientY)`), and avoid destroying/recreating `#grid-3x3` DOM nodes on hover by updating a dedicated preview overlay container instead of `gridEl.innerHTML = ""`.

---

### R07 (P1) — Captured Cards Re-Statted Inconsistently on Dice Nudge / Reroll
- **Location**: `getCardEffectiveStats` (`L1512–1520`), `recalcBoardStats` (`L1614–1623`), and capture loops (`L1703–1706`, `L1732–1735`, `L1789–1792`).
- **Root Cause**:
  ```js
  function recalcBoardStats() {
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const cell = state.grid[r][c];
        if (cell.cardId && cell.owner === "player") {
          cell.nesw = getCardEffectiveStats(cell.cardId, c, false);
        }
      }
    }
  }
  ```
  When a card is captured (`L1704`, `L1733`, `L1790`), only `cell.owner` changes; `cell.nesw` is left untouched at the moment of capture. Later, when `nudgeColDie` or `rerollAllDice` calls `recalcBoardStats()`:
  - **(a) Player-captured enemy mech (`e_*` with `owner === "player"`)**: `recalcBoardStats()` recomputes its stats with `isAi = false`. On Stages 3–4 (`aiBonus = 1`),nudging **any** column die causes an enemy mech captured in an unboosted column to silently lose `+1` on all four sides (e.g., `e_titan` in Col 2 drops from `[8,6,8,7]` to `[7,5,7,6]`).
  - **(b) Boss-captured player hero (`h_*` with `owner === "ai"`)**: `recalcBoardStats()` skips `owner === "ai"` completely. If the hero was in a boosted column when captured (`[8,8,9,8]`), and the player nudges that column die from `6 → 1` to remove the boost, the player's own cards in that column lose `+1`, while the boss-held hero in the **same column** keeps the stale `+1` boost forever!
- **Suggested Fix**: Decide and enforce a single consistent rule for card stats on the board:
  - **Option A ( Current-Owner Rule )**: Every card on the board derives its stats from its **current** owner (`owner === "player"` gets column boost; `owner === "ai"` gets `aiBonus`), and `recalcBoardStats()` updates **all** occupied cells both on dice changes and immediately after any capture flip.
  - **Option B ( Faction / Card-Origin Rule )**: `isAi` is determined by faction (`cardId.startsWith("e_")`) or column boost applies only to `owner === "player"`, and `recalcBoardStats()` updates all 9 cells whenever ownership or dice change.

---

### R08 (P2) — Progression Bypass on Defeat, Stage 4→1 Wrap, Stale Turn Badge & 5th-Card Economy
- **Location**: `startStage` (`L1577–1584`), `executeBossTurn` (`L1801–1805`), `checkGameOver` (`L1820–1837`), `closeModal` (`L1839–1846`).
- **Root Cause & 4 Sub-Issues**:
  1. **Defeat still advances stage (`L1826–1846`)**: `#result-modal` always renders the `Next Stage ▶` button (`onclick="closeModal(true)"`) regardless of whether `win` is `true` or `false`. Losing Stage 1 and clicking `Next Stage ▶` advances to Stage 2.
  2. **Stage 4 wraps to Stage 1 (`L1842`)**: `state.stageIndex = (state.stageIndex + 1) % STAGES.length;` silently loops Stage 4 back to Stage 1 with no campaign completion state.
  3. **Turn badge says `YOUR TURN` on game over (`L1801–1805`)**: `executeBossTurn` sets `state.isPlayerTurn = true; renderAll(); checkGameOver();`, so the HUD badge always reads `YOUR TURN` after the 9th card fills the board.
  4. **Boss always moves last & 1 hero card is always unused (`L1577–1584`)**: Because the boss pre-places 1 card at `(0,1)` before Turn 1 (`8` empty cells remain) and the player has `5` cards in hand while the boss has `5` in `aiPool`, every game consists of exactly **4 player deployments** and **4 boss replies** (`1 + 4 + 4 = 9`). The player never deploys their 5th hand card, and the boss always gets the final unanswerable move on Turn 4.
- **Suggested Fix**:
  - Hide or disable `Next Stage ▶` when `!win` (show only `↻ Retry Stage`).
  - On Stage 4 victory (`state.stageIndex === STAGES.length - 1 && win`), label the button `🏆 Campaign Complete (Play Again)`.
  - In `renderAll()` (`L1900`), set `turnBadge.textContent = state.gameOver ? "MATCH OVER" : (state.isPlayerTurn ? "YOUR TURN" : "BOSS TURN")`.

---

### R09 (P2) — Stale Result Modal Pops Over a Fresh Game After `Reset`
- **Location**: `checkGameOver` (`L1826–1835`), `startStage` (`L1546–1590`).
- **Root Cause**: When the 9th card is placed, `checkGameOver()` sets `state.gameOver = true` and schedules `setTimeout(() => { modal.style.display = "flex"; }, 460)`. If the player clicks `↻ Reset` during that 460 ms delay, `startStage()` starts a new game (`state.gameOver = false`), and then the old timeout fires and displays the previous game's `💥 DEFEAT` or `🏆 VICTORY` modal over the brand-new board (see [`out/R09_stale_modal.png`](out/R09_stale_modal.png)).
- **Suggested Fix**: Store `modalTimer = setTimeout(...)` in `checkGameOver()`, cancel `modalTimer` and set `document.getElementById("result-modal").style.display = "none"` inside `startStage()`, and guard the timeout callback with `if (!state.gameOver) return;`.

---

### R10 (P2) — Global `keydown` Handler Hijacks `Space`, `Enter`, and `r` Across Focused Controls
- **Location**: `handleHarnessKeyDown` (`L1410–1446`).
- **Root Cause**: `window.addEventListener("keydown", handleHarnessKeyDown)` intercepts `Enter`, ` ` (`Space`), `r`/`R`, `p`/`P`, `w/a/s/d`, and `1–5` globally without checking whether focus is inside an interactive control (`BUTTON`, `SELECT`, `INPUT`) or whether modifier keys (`Ctrl`/`Meta`/`Alt`) are held:
  - Clicking `🎲 Roll All 3D Dice` leaves focus on that `<button>`. Pressing `Space` (standard keyboard activation for a focused button) is intercepted by `e.preventDefault(); handleSlotClick(row, col);` (`L1430–1431`), which **deploys a card from hand to `(1,1)` and ends the player's turn** instead of pressing the button!
  - Pressing `r` (or `Cmd+R` to reload in browsers that pass `keydown` before reload) calls `rerollAllDice()` (`L1437`), spending a reroll.
- **Suggested Fix**:
  ```js
  function handleHarnessKeyDown(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = e.target && e.target.tagName;
    if (tag === "BUTTON" || tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;
    if (state.gameOver || !state.isPlayerTurn || drag.active || drag.dropping) return;
    ...
  ```

---

### R11 (P3) — Debug/Autotest Hooks Reachable via URL Substring in Production
- **Location**: `DOMContentLoaded` listener (`L2400–2411`), `runDragDropTest` (`L2414–2487`), `runVisualAutomatedPlaytest` (`L2489–2665`).
- **Root Cause**:
  1. `window.location.search.includes("autotest=1")` (`L2402`) and `.includes("dragtest=1")` (`L2405`) use substring matching instead of `URLSearchParams`, so `?ref=xautotest=1` hijacks the session and plays a full game automatically.
  2. Both routines `POST` telemetry to `/__osascript_report__` on the serving origin (`L2407`, `L2484`, `L2656`).
  3. `document.getElementById("cam-select")` at `L2557` is a dead lookup (the `<select>` id in the DOM is `#camera-select`).
  4. `report.outcome = finalScores.blue > finalScores.red ? "VICTORY" : "COMPLETED"` (`L2652`) masks defeats as `"COMPLETED"`.
- **Suggested Fix**: Gate test harnesses behind `new URLSearchParams(location.search).get("autotest") === "1"` (or strip from production builds), fix `#camera-select`, and report `"DEFEAT"` when `finalScores.blue <= finalScores.red`.

---

## 3. Refuted & Non-Reproducible Hypotheses

To keep the audit rigorous, we explicitly tested and **refuted** several initial hypotheses:

1. **Duplicate / Non-Singleton Card Dealing**: *Refuted.* `shuffle(PLAYER_HEROES)` (`L1565`) and `shuffle(ENEMY_MECHS)` (`L1566`) clone and shuffle 8 unique hero cards and 8 unique enemy mechs per stage. Across all 160 browser playthroughs in `S01` and 166 validation matches in `balance/validate.js`, zero duplicate cards ever appeared.
2. **Mismatch Between Hover Clash Preview (`findClashes`) and Actual Capture Resolution (`findCaptures`)**: *Refuted.* Both functions (`L1625–1669`) use identical direction vectors (`N: 0↔2`, `E: 1↔3`, `S: 2↔0`, `W: 3↔1`) and strict inequality (`nesw[d.myEdge] > nb.nesw[d.theirEdge]`). Cross-validation between the browser and headless engine (`balance/results/validation_summary.json`) confirmed **100% agreement across 166 matches and 975 actions**.
3. **3D Hit-Test Swallowing Plain Card Deploy Clicks**: *Refuted for deploys.* In `R06`, **30/30 (100%)** real-mouse clicks for normal card deployment succeeded across all 3 camera presets (`5,0`, `0,0`, `14,0`). Click swallowing (**10/30 failed**) only occurs on **Tactical Slide target tiles** (`⇄ SLIDE HERE`) where no 3D preview card is injected.
4. **Boss Signature Card Guaranteed in Every Match**: *Clarified (Design Quirk, Not a Crash).* `STAGES[idx].bossId` is used only for the header name, avatar, and telegraph label (`L1558–1562`). The 6 enemy cards used in a stage (1 pre-placed opener + 5 in `aiPool`, with only 4 of the 5 pool cards ever played) are drawn uniformly from all 8 `ENEMY_MECHS` (`L1566–1583`). Thus the stage boss's own card only appears on the board in `5/8 = 62.5%` of matches (and is in opener+pool in `6/8 = 75%` of matches; empirical `S01` rate: `73.8%`).

---

## 4. 16-Card Stat & Dominance Analysis (`analysis/cards.json`, `analysis/cards.md`)

All 16 cards were parsed directly from `WebPlayable/cardfront_cradle_of_echoes_playable.html` (`L967–1135`) by [`analysis/A01_card_analysis.js`](analysis/A01_card_analysis.js).

### 4.1 Complete 16-Card Stat Table

| Card | ID | Faction | HTML Line | N | E | S | W | Sum | Min | Max | SD | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Sun Arbiter** | `h_arbiter` | Hero | `L1044` | 7 | 7 | 8 | 8 | **30** | 7 | 8 | 0.50 | Strictly dominates `h_oracle`; #1 hero overall |
| **Lunar Oracle** | `h_oracle` | Hero | `L989` | 7 | 7 | 8 | 7 | **29** | 7 | 8 | 0.43 | No edge below 7; dominated by `h_arbiter` |
| **Astral Seraph** | `h_seraph` | Hero | `L1011` | 8 | 6 | 7 | 8 | **29** | 6 | 8 | 0.83 | Strong N/W corner anchor |
| **Solar Archangel** | `h_archangel` | Hero | `L967` | 8 | 7 | 6 | 7 | **28** | 6 | 8 | 0.71 | Balanced N-heavy hero |
| **Phoenix Valkyrie** | `h_phoenix` | Hero | `L978` | 9 | 8 | 5 | 6 | **28** | 5 | 9 | 1.58 | Strictly dominates `h_valkyrie`; `N=9` wastes column boost (`Math.min(9, 9+1)=9`) |
| **Chronos Weaver** | `h_chronos` | Hero | `L1000` | 6 | 8 | 7 | 7 | **28** | 6 | 8 | 0.71 | E-heavy hero |
| **Kai Crimson Visor** | `h_kai` | Hero | `L1022` | 7 | 8 | 6 | 7 | **28** | 6 | 8 | 0.71 | E-heavy hero |
| **Sky-Wing Striker** | `h_valkyrie` | Hero | `L1033` | 8 | 8 | 5 | 6 | **27** | 5 | 8 | 1.30 | Weakest hero; strictly dominated by `h_phoenix` |
| **Inferno Seraph** | `e_inferno` | Enemy | `L1080` | 7 | 7 | 5 | 6 | **25** | 5 | 7 | 0.83 | Stage 4 boss (`aiBonus +1`); strictly dominates `e_eclipse` |
| **Sigil Wraith** | `e_reaper` | Enemy | `L1091` | 6 | 7 | 7 | 5 | **25** | 5 | 7 | 0.83 | Strong S/E attacker |
| **Bastion Dreadnought** | `e_titan` | Enemy | `L1102` | 7 | 5 | 7 | 6 | **25** | 5 | 7 | 0.83 | Strong N/S vertical attacker |
| **Emerald Colossus** | `e_colossus` | Enemy | `L1113` | 6 | 8 | 5 | 6 | **25** | 5 | 8 | 1.09 | Stage 3 boss (`aiBonus +1`); `E=8` (`9` in S3–4, unbeatable!) |
| **Cryo Interceptor** | `e_cryo` | Enemy | `L1124` | 5 | 7 | 6 | 7 | **25** | 5 | 7 | 0.83 | Only enemy with base `W=7` |
| **Prism Core Archon** | `e_archon` | Enemy | `L1069` | 7 | 6 | 6 | 5 | **24** | 5 | 7 | 0.71 | Stage 2 boss (`aiBonus 0`); identical stats to `e_shinobi` |
| **Cyber Shinobi** | `e_shinobi` | Enemy | `L1135` | 7 | 6 | 6 | 5 | **24** | 5 | 7 | 0.71 | Duplicate stat line (`[7,6,6,5]`) with `e_archon` |
| **Eclipse Void Blade** | `e_eclipse` | Enemy | `L1058` | 6 | 6 | 5 | 6 | **23** | 5 | 6 | 0.43 | Stage 1 boss (`aiBonus 0`); weakest card in the game |

### 4.2 Structural Stat Findings
1. **Massive Base Stat Asymmetry (Stages 1–2)**:
   - Player heroes average **7.094 per edge** (**28.38 total**), whereas enemy mechs average **6.125 per edge** (**24.50 total**).
   - Even the weakest hero (`h_valkyrie`, total **27**) has a higher stat total than the strongest enemy mech (`25`).
   - Across all `8 × 8 × 4 = 256` `(hero, enemy, facing)` pairings:
     - **Stages 1–2 unboosted (`+0` vs `+0`)**: Heroes capture enemies on **65.2%** of facings; enemies capture heroes on only **14.5%**.
     - **Stages 1–2 boosted (`+1` vs `+0`)**: Heroes capture enemies on **85.5%** of facings; enemies capture heroes on only **3.9%**.
     - **Stages 3–4 unboosted (`+0` vs `+1`)**: `aiBonus = +1` brings enemy average edge to **7.125** vs hero **7.094** (gap `-0.031`), equalizing unboosted capture rates to **36.7%** (hero) vs **34.8%** (enemy).
     - **Stages 3–4 boosted (`+1` vs `+1`)**: Column boost restores the exact Stages 1–2 unboosted advantage (**65.2%** vs **14.5%**).
2. **Strict Dominance & Duplicate Stat Lines**:
   - **Intra-Hero Strict Dominance**: `h_arbiter [7,7,8,8] ≻ h_oracle [7,7,8,7]` and `h_phoenix [9,8,5,6] ≻ h_valkyrie [8,8,5,6]`.
   - **Intra-Enemy Strict Dominance**: `e_inferno [7,7,5,6] ≻ e_eclipse [6,6,5,6]` and `e_colossus [6,8,5,6] ≻ e_eclipse [6,6,5,6]`.
   - **Duplicate Enemy Cards**: `e_archon` and `e_shinobi` have identical `[7,6,6,5]` stats.
   - **Cross-Faction Strict Dominance**: **39 of 64** `(hero, enemy)` pairs exhibit strict dominance on all 4 edges (`hero ≻ enemy` in all 39 cases; `h_arbiter` strictly dominates all 8 enemies at base stats).
3. **Clamp-at-9 Waste & Unbeatable Edges**:
   - `h_phoenix.N = 9` is already at the hard cap (`Math.min(9, v + boost)` at `L1519`), so a column boost gives `h_phoenix` only `+3` total stats instead of `+4`.
   - On Stages 3–4 (`aiBonus = +1`), `e_colossus.E` becomes `9`. Because `findCaptures` requires strict `>` (`L1637`) and stats clamp at `9`, **no hero in the game—even with a column boost (`max W = 9`)—can ever capture `e_colossus` from its East side**.
4. **Directional Bias**:
   - Heroes are N/E biased (`mean N = 7.50, E = 7.38, S = 6.50, W = 7.00`), while enemies are weak on S/W (`mean N = 6.38, E = 6.50, S = 5.88, W = 5.75`). Because `N` attacks `S` (`7.50 vs 5.88`) and `E` attacks `W` (`7.38 vs 5.75`), heroes attacking from South-to-North or West-to-East enjoy a **+1.63 edge advantage** even before column boosts.
