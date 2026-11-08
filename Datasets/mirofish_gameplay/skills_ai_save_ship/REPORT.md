# Track 4 Audit Report: AI Behavior Trees & Utility AI, Save Systems, Prototype-Fast, and Itch.io / Steam Publishing

**Target Build:** [WebPlayable/cardfront_cradle_of_echoes_playable.html](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html) (`17b5c65`) & [Assets/Scripts/Core/CardFrontUnifiedRuntime.cs](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs) + [Assets/Scripts/AI/SynapseMiroStrandsSimulationEngine.cs](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/AI/SynapseMiroStrandsSimulationEngine.cs)  
**Skills Audited (`gamedev-skills/awesome-gamedev-agent-skills`):**
1. [`skills/disciplines/game-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md)
2. [`skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md)
3. [`skills/disciplines/save-systems/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md)
4. [`skills/workflows/prototype-fast/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/prototype-fast/SKILL.md)
5. [`skills/workflows/itch-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md)
6. [`skills/workflows/steam-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/steam-publish/SKILL.md)

**Prototype & Telemetry Artifacts:**
- Clean-Room Utility AI Module & 16,000-Match Monte Carlo Benchmark: [`boss_ai_utility.js`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js)
- Benchmark Results JSON: [`raw/ai_benchmark.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json)
- Automatable Checks Manifest (`18` checks): [`checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/checks.json)

---

## 1. Gemini 4 Argon (`gemini-4-argon`) Native Skill Routing & Verification Architecture

In the reference video (`https://youtu.be/t13A2XFGoOc`, *"Turn Claude into an Expert Game Dev with these Free 77 AI Skills"*), Claude Code loads skills sequentially inside a single agent loop via `.claude-plugin/marketplace.json`. Under **Gemini 4 Argon (`gemini-4-argon`) + the Antigravity Subagent/MCP Harness**, AI prototyping, save-system verification, and store-release gating are executed as a deterministic multi-agent pipeline:

```mermaid
flowchart LR
    Req["AI, Persistence & Ship Audit Request"] --> Router["gamedev-router<br/>(~/.gemini/config/skills/gamedev-router/SKILL.md)"]
    Router -->|Discipline: AI| AI["game-ai +<br/>ai-behavior-trees-utility-ai"]
    Router -->|Discipline: Persistence| Save["save-systems"]
    Router -->|Workflows: Ship| Ship["prototype-fast +<br/>itch-publish + steam-publish"]
    AI --> Impl["code-implementer Subagent<br/>(Prototypes boss_ai_utility.js + 16k Monte Carlo)"]
    Save --> Impl
    Ship --> MLX["mlx-local-worker Subagent<br/>(Apple Silicon M-Series / A18 Pro Local Inference)"]
    Impl --> Iterate["Tools/skill_harness/iterate.py<br/>(Executes checks.json static_regex + playwright + metric)"]
    MLX --> Verifier["truth-verifier / jev-judge<br/>(Gates store VDFs, itch zip layout & win-rate uplift)"]
    Iterate --> Verifier
```

### How Gemini 4 Argon Supersedes `.claude-plugin` on Track 4
1. **Multi-Axis Routing (`gamedev-router`):** Per [`gamedev-router/SKILL.md`](file:///Users/frederickamina/.gemini/config/skills/gamedev-router/SKILL.md#L64-L115), when a task spans opponent AI tuning, progression persistence, and store shipping, `gemini-4-argon` composes discipline skills (`game-ai`, `ai-behavior-trees-utility-ai`, `save-systems`) with workflow skills (`prototype-fast`, `itch-publish`, `steam-publish`) in a single subagent brief.
2. **Sandboxed Clean-Room AI Prototyping (`code-implementer`):** While 5 concurrent gameplay subagents test the live browser build at `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`, `code-implementer` builds and benchmarks [`boss_ai_utility.js`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js) out-of-tree (`16,000` simulated matches in `< 0.8s` on Node.js) without mutating the shared HTML file.
3. **Apple Silicon Local MLX Policy Distillation (`mlx-local-worker`):** On Apple Silicon (`~/.local/share/mlx-env`), `mlx-local-worker` and [`SynapseMiroStrandsSimulationEngine.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/AI/SynapseMiroStrandsSimulationEngine.cs#L19-L63) pair fast Utility AI response curves (`< 0.05 ms/move`) with local 4-bit quantized Qwen/JevMLX batch evaluation (`mlx_jev_choose`, `mlx_jev_rate`) for offline narrative telemetry and deck balance auditing.
4. **Executable Verification Loop (`Tools/skill_harness/iterate.py` & `truth-verifier`):** Every rule from the 6 skills—including itch.io zip root `index.html` validation, relative asset traversal checks, save schema versioning, and Utility AI win-rate uplift—is encoded as an executable assertion in [`checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/checks.json) and verified by [`Tools/skill_harness/iterate.py`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Tools/skill_harness/iterate.py).

---

## 2. Executive Summary & Skill Compliance Matrix

| Skill | Primary Target | Passed | Failed | Verdict | Key Finding |
|---|---|---:|---:|---|---|
| [`game-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md) | `executeBossTurn` ([HTML:1757-1806](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1757-L1806)) | 2 | 2 | **PARTIAL** | Cleanly separates turn scheduling (`setTimeout(executeBossTurn, 620)`) from board state, and telegraphs stage AI bonuses (`+1 ALL SIDES`), but lacks difficulty tiers and couples decision logic directly to DOM mutation inside `executeBossTurn`. |
| [`ai-behavior-trees-utility-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md) | `executeBossTurn` & [`boss_ai_utility.js`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js) | 1 | 3 | **FAIL (Live HTML) / PASS (Prototype)** | Live `executeBossTurn` pops a fixed card (`state.aiPool.pop()`), scores only 1 integer (`findCaptures().length`), and breaks ties uniformly at random (`6.65%` win rate vs greedy player). Our clean-room Utility AI (`grandmaster` tier) lifts Boss win rate to **`15.95%` overall (+140% relative uplift)** and **`30.4%` on Stage 4** (`85.6%` vs random player). |
| [`save-systems/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md) | Web Playable & `EchoGhostPvPManager` ([C#:459-582](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L459-L582)) | 1 | 4 | **FAIL** | Web build has **zero** `localStorage` persistence (`0` keys saved across reloads). Unity `EchoGhostSnapshot` ([C#:462-470](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L462-L470)) implements HMAC-SHA256 receipt signing (`GenerateActionLogHmacReceipt`) but omits a `version` integer field, omits atomic `.tmp` $\rightarrow$ `.bak` file writes, and hardcodes `DefaultReceiptSecret` in source ([C#:475](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L475)). |
| [`prototype-fast/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/prototype-fast/SKILL.md) | [cardfront_cradle_of_echoes_playable.html](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html) | 2 | 1 | **PARTIAL** | Strong data-driven `CARDS` / `STAGES` tables ([HTML:962-1298](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L962-L1298)), but embeds 250+ lines of test harnesses (`?autotest=1`, `?dragtest=1` at [HTML:2414-2665](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L2414-L2665)) directly in the shippable HTML file. |
| [`itch-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md) | `WebPlayable/` Packaging | 0 | 3 | **FAIL (Blocker)** | Entry HTML is named `cardfront_cradle_of_echoes_playable.html` instead of `index.html`, and uses `../GeneratedArt/...` parent-directory paths ([HTML:40, 931, 968-1140, 1307-1310](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L968-L1140)) that 404 inside itch.io's HTML5 iframe sandbox. |
| [`steam-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/steam-publish/SKILL.md) | Repository Release Readiness | 0 | 2 | **FAIL (Pre-Alpha)** | No `app_build_*.vdf` or `depot_build_*.vdf` SteamPipe manifests exist in the repository yet, and Generative AI disclosure metadata for `GeneratedArt/` must be prepared for the Steamworks Content Survey. |

---

## 3. Detailed Audit: `game-ai` & `ai-behavior-trees-utility-ai`

### 3.1 Audit of Live Boss AI (`executeBossTurn`)
In [WebPlayable/cardfront_cradle_of_echoes_playable.html:1757-1806](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1757-L1806), the Boss AI is implemented as a 50-line greedy loop:

```javascript
// WebPlayable/cardfront_cradle_of_echoes_playable.html:1762-1778
const cardId = state.aiPool.pop();
const cardObj = getCard(cardId);

// Boss AI: pick open slot that maximizes immediate captures, tie-break randomly
let bestSlot = open[Math.floor(Math.random() * open.length)];
let bestScore = -1;
for (const slot of open) {
  const nesw = getEffectiveStats(cardObj, slot.c, true);
  const flips = findCaptures(slot.r, slot.c, nesw, 'ai');
  if (flips.length > bestScore) {
    bestScore = flips.length;
    bestSlot = slot;
  }
}
```

Evaluating this against [`game-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md) and [`ai-behavior-trees-utility-ai/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md) reveals four structural flaws:

1. **No Pool Evaluation (`state.aiPool.pop()`):** Even though `state.aiPool` holds 5 Boss cards at the start of a stage ([HTML:1622](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1622)), `executeBossTurn` pops the last card blindly before looking at the board. If the popped card has high North/West stats (`[8, 3, 2, 7]`) and the only player card is to the South, the Boss wastes its high edges and fails to flip.
2. **Step-Function Single-Integer Scoring (`flips.length`):** Per [`ai-behavior-trees-utility-ai/SKILL.md:45-57`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md#L45-L57), Utility AI shines when multiple continuous factors trade off ("Target selection, ability choice, tactical positioning"). In `executeBossTurn`, whenever `flips.length === 0` for all open slots (which happens on **100% of Turn 1 Boss responses** whenever the popped card cannot immediately beat the player's opening card, and on ~45% of midgame turns), `bestScore` stays `0` on the first slot (`open[0]`, top-left `(0,0)` or first scan index)! Notice a subtle bug at [HTML:1766-1774](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1766-L1774): `bestSlot` is initialized to a random slot, `bestScore` is initialized to `-1`, and on the very first iteration `slot = open[0]`, `flips.length` (`>= 0`) is strictly `> -1`, so **`bestSlot` is immediately overwritten with `open[0]`**! Thus the "random tie-break" on line 1766 is **dead code**—when all slots score `0` flips, `executeBossTurn` deterministically dumps its card into the first open cell in row-major order (`(0,0)`, then `(0,1)`, etc.)!
3. **Zero Positional Awareness (Edge Exposure, Corners, Boosted Columns):** Placing a card with a weak `2` East edge at `(0,0)` when `(0,1)` is empty invites an automatic player counter-capture next turn. Similarly, leaving a player-boosted column (`state.colDice[c] >= 4`, which grants the player `+1` to all 4 edges at [HTML:1600-1601](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1600-L1601)) open gifts the player free stats.
4. **Coupled Decision & Execution ([`game-ai/SKILL.md:36-41`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md#L36-L41)):** `executeBossTurn` mutates `state.grid`, triggers `playCardPlaceSfx()`, spawns DOM `.battle-clash-badge` elements, and mutates `innerHTML` inside the same function, making it impossible to run headless lookahead or unit tests without mocking the DOM.

### 3.2 Clean-Room Prototype: `boss_ai_utility.js`
We prototyped [`Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js) following [`ai-behavior-trees-utility-ai/SKILL.md:126-158`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md#L126-L158):
- **Normalized `[0..1]` Response Curves ([`boss_ai_utility.js:26-60`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js#L26-L60)):** Implements `Curves.linear`, `Curves.quadratic`, `Curves.exponential`, `Curves.sigmoid`, `Curves.smoothstep`, and Dave Mark's IAUS makeup compensation `Curves.compensate(product, count)` so multiplying 5 considerations in `[0..1]` does not underflow valid multi-factor plays.
- **Five Tactical Considerations ([`boss_ai_utility.js:149-250`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js#L149-L250)):**
  1. `cFlips` (`Curves.quadratic`): Smoothly rewards capturing 1–3 adjacent player cards while preserving a `0.22` base floor so non-capture setup turns still compete on positioning.
  2. `cEdgeSafety` (`Curves.sigmoid`): Rewards placing high edges toward open neighbor sockets and tucking weak edges against board outer walls.
  3. `cTopology` (`Curves.smoothstep`): Values 2-neighbor corner fortresses (`(0,0)`, `(0,2)`, `(2,0)`, `(2,2)`) for fragile cards and reserves the 4-neighbor center (`(1,1)`) for high-stat Boss cards (`avgStat >= 0.72`).
  4. `cColumnDenial` (`Curves.linear`): Prioritizes occupying columns where `state.colDice[c] >= 4` (`+1` player column boost), denying the player boosted deployments.
  5. `cCounterResistance` (1-ply worst-case lookahead): Simulates the player's remaining hand cards across adjacent empty sockets and penalizes placements that can be immediately re-flipped on the player's next turn.
- **Three Difficulty Tiers ([`boss_ai_utility.js:65-105`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js#L65-L105)):**
  - `apprentice` (Stage 1 Intro): Softmax selection (`temperature = 0.28`) on top drawn card, giving new players a fair, varied opening opponent.
  - `tactician` (Stage 2–3 Midgame): Softmax selection (`temperature = 0.08`) across the Boss's available `aiPool` with balanced positional weights.
  - `grandmaster` (Stage 4 Apex Boss): Argmax selection (`temperature = 0.01`) across all `(cardId, slot)` pairs with strong 1-ply counter-flip resistance (`weight = 1.10`) and hysteresis (`+0.035`).

### 3.3 16,000-Match Monte Carlo Benchmark Results (`raw/ai_benchmark.json`)
We ran `2,000` deterministic matches per Boss policy (`500` matches × 4 stages) against both a **Greedy Player** (maximizing immediate flips + boosted columns + player Tactical Slide) and a **Random Player** (`16,000` total matches in [`raw/ai_benchmark.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json)):

| Boss AI Policy | Selection & Pool Mode | vs Greedy Player (All Stages) | Stage 1 (`+0`) | Stage 2 (`+0`) | Stage 3 (`+1`) | Stage 4 (`+1`) | Avg Boss Final Cards | Avg Boss Flips / Match | vs Random Player (All Stages) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`greedy_current` (Live HTML)** | Top card + row-major tie bug | **6.65%** | 1.00% | 0.40% | 11.60% | 13.60% | 2.98 | 1.94 | 44.75% |
| **`apprentice` (Tier 1)** | Softmax ($T=0.28$), top card | **3.50%** | 0.60% | 0.60% | 5.80% | 7.00% | 2.67 | 1.51 | 32.70% |
| **`tactician` (Tier 2)** | Softmax ($T=0.08$), full pool | **10.90%** | 2.20% | 1.60% | 19.60% | 20.20% | 3.11 | 1.86 | 46.05% |
| **`grandmaster` (Tier 3)** | Argmax + 5 curves + 1-ply lookahead | **15.95%** | **3.40%** | **2.40%** | **27.60%** | **30.40%** | **3.47** | **2.40** | **65.00%** (85.6% S4) |

> [!TIP]
> **Why `grandmaster` More Than Doubles Boss Win Rate (+140% Relative Uplift vs Greedy Player):**
> Because the player moves first (placing 5 of the 9 board cards) AND gets a free Tactical Slide + column dice boosts (`colDice[c] >= 4`), the second-player Boss faces a massive structural disadvantage (`greedy_current` wins only `6.65%` overall and `13.60%` even with Stage 4's `+1 ALL SIDES` aura). By evaluating all remaining cards in `state.aiPool`, tucking weak edges into corners (`cEdgeSafety` + `cTopology`), denying player-boosted columns (`cColumnDenial`), and avoiding immediate counter-flips (`cCounterResistance`), `grandmaster` boosts Stage 4 Boss win rate from **`13.60%` to `30.40%`** against a Greedy Player and from **`64.80%` to `85.60%`** against a Random Player.

---

## 4. Detailed Audit: `save-systems`

We audited both [WebPlayable/cardfront_cradle_of_echoes_playable.html](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html) and Unity's [`EchoGhostPvPManager`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L459-L582) against [`skills/disciplines/save-systems/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md):

1. **Zero Web Playable Persistence (`save-systems/SKILL.md:27-35, 134-152` — FAIL):**
   - **Evidence:** Static regex scan and Playwright runtime evaluation (`Object.keys(window.localStorage).length`) confirm `0` calls to `localStorage`, `sessionStorage`, or `IndexedDB` anywhere in [cardfront_cradle_of_echoes_playable.html](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html). If a player reaches Stage 4 (`Apex Neural Core`) and refreshes the browser tab, `state.stageIdx`, `state.Wins`, `state.Losses`, and deck unlocks reset to zero.
2. **Missing Schema `version` Integer & Sequential Migration (`save-systems/SKILL.md:45-93, 187` — FAIL):**
   - **Evidence:** [`save-systems/SKILL.md:46-47`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md#L46-L47) mandates: *"Put `"version": 1` (integer, not semver string) at the root of every save file from day one."* In [Assets/Scripts/Core/CardFrontUnifiedRuntime.cs:462-470](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L462-L470), `EchoGhostSnapshot` defines `snapshot_id`, `player_id`, `player_display_name`, `mmr_rating`, `deck_card_ids`, `opening_preference_tags`, and `action_log_hmac_receipt`, but has **no `version` integer field** and no `MIGRATIONS` step function (`v -> v + 1`).
3. **Missing Atomic Temp-File Write & `.bak` Rotation (`save-systems/SKILL.md:97-130, 188` — FAIL):**
   - **Evidence:** `EchoGhostPvPManager.CapturePlayerEchoSnapshot` ([C#:497-522](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L497-L522)) serializes directly in memory via `JsonUtility.ToJson(snap, true)` without an atomic disk-write helper (`File.WriteAllText(tmpPath)` $\rightarrow$ `File.Flush` $\rightarrow$ rotate `.bak` $\rightarrow$ `File.Replace`).
4. **Hardcoded HMAC Secret Key in Source (`save-systems/SKILL.md:173-177` — FAIL):**
   - **Evidence:** While `EchoGhostPvPManager.GenerateActionLogHmacReceipt` ([C#:562-575](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs#L562-L575)) implements HMAC-SHA256 integrity signing, line 475 hardcodes `private const string DefaultReceiptSecret = "CARDFRONT_ECHO_GHOST_SOVEREIGN_HMAC_KEY_2026";` directly inside the client assembly. Per [`save-systems/SKILL.md:175`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md#L175): *"Note: The key lives in the binary and WILL be extracted by determined users. This stops notepad edits, not dedicated tool authors."* For asynchronous PvP ghost validation (`VerifySnapshotIntegrity`), receipt verification must either use server-side secrets or label client-side HMAC strictly as a corruption/casual-tamper checksum.

### Concrete Remediation: Versioned Web Save + Migration + Atomic LocalStorage Backup
```javascript
const SAVE_KEY = "cardfront_cradle_save_v1";
const SAVE_BAK_KEY = "cardfront_cradle_save_v1.bak";
const CURRENT_SAVE_VERSION = 1;

const SAVE_MIGRATIONS = {
  // Future migrations: 1: (s) => ({ ...s, version: 2, unlockedRelics: [] })
};

function saveCampaignProgress(state) {
  const payload = {
    version: CURRENT_SAVE_VERSION,
    savedAtIso: new Date().toISOString(),
    stageIdx: state.stageIdx,
    wins: state.Wins,
    losses: state.Losses,
    deckIds: state.deck
  };
  const prev = localStorage.getItem(SAVE_KEY);
  if (prev) localStorage.setItem(SAVE_BAK_KEY, prev);
  localStorage.setItem(SAVE_KEY, JSON.stringify(payload));
}
```

---

## 5. Detailed Audit: `prototype-fast`, `itch-publish`, & `steam-publish`

### 5.1 `prototype-fast` ([`skills/workflows/prototype-fast/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/prototype-fast/SKILL.md))
- **PASS — Tunables Externalized in Top-Level Data Tables (`prototype-fast/SKILL.md:62-66`):** `CARDS` ([HTML:962-1280](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L962-L1280)) and `STAGES` ([HTML:1282-1298](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L1282-L1298)) cleanly externalize card stats, faction tags, stage dice bonuses, and background paths into declarative tables.
- **FAIL — Production HTML Embeds Automated Test Harnesses (`prototype-fast/SKILL.md:88-92`):** Lines [2414-2665](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L2414-L2665) embed `runDragDropTest()` (`?dragtest=1`) and `runVisualAutomatedPlaytest()` (`?autotest=1`) inside the player-facing HTML file. These should be extracted to an external Playwright/Node test runner so production bundles stay lean and cannot be triggered by end-user query strings.

### 5.2 `itch-publish` ([`skills/workflows/itch-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md))
Auditing `WebPlayable/` against the HTML5 / WebGL Requirements in [`itch-publish/SKILL.md:127-146`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md#L127-L146) uncovered **two P0 deployment blockers**:
1. **Blocker 1 — Missing `index.html` at Zip Root (`itch-publish/SKILL.md:129`):**
   - Rule: *"Entry file MUST be `index.html` at the root of the `.zip` (not inside a subfolder)."*
   - Observed: The file is named `WebPlayable/cardfront_cradle_of_echoes_playable.html`. Uploading `WebPlayable/` as a zip to itch.io fails with *"No index.html found"*.
2. **Blocker 2 — Parent-Directory Asset Traversal `../GeneratedArt/` (`itch-publish/SKILL.md:132`):**
   - Rule: *"Use relative asset paths (`./assets/foo.png`, NOT `/assets/foo.png`) — itch serves your game from a subfolder URL."*
   - Observed: [cardfront_cradle_of_echoes_playable.html](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html) references `../GeneratedArt/CardFronts/...` and `../GeneratedArt/Stages/...` **23 times** (lines `40, 931, 968-1140, 1307-1310`). Because `GeneratedArt/` sits outside `WebPlayable/`, zipping `WebPlayable/` omits all 20 PNGs, and `../GeneratedArt/` attempts to traverse above the itch.io CDN sandbox root (returning HTTP 403/404).
3. **Mandatory Generative AI Disclosure (`itch-publish/SKILL.md:51-53`):**
   - Rule: *"itch requires tagging if any assets/code/text were created with generative AI tools. Failing to disclose gets pages delisted; disclosing accurately is fine."* Because the 16 card fronts and 4 stage backgrounds in `GeneratedArt/` were generated via ComfyUI (`SD 1.5`), the itch.io project settings must check the Generative AI disclosure box.

#### Self-Contained `butler` Packaging Script for itch.io (`scripts/package_itch_html5.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail
DIST_DIR="Build/itch-web"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/GeneratedArt/CardFronts" "$DIST_DIR/GeneratedArt/Stages"

# Copy HTML to root index.html and rewrite ../GeneratedArt/ -> ./GeneratedArt/
sed 's|\.\./GeneratedArt/|./GeneratedArt/|g' \
  WebPlayable/cardfront_cradle_of_echoes_playable.html > "$DIST_DIR/index.html"

cp GeneratedArt/CardFronts/*.png "$DIST_DIR/GeneratedArt/CardFronts/"
cp GeneratedArt/Stages/*.png "$DIST_DIR/GeneratedArt/Stages/"

# Push via itch.io butler CLI (itch-publish/SKILL.md:75-100)
# butler push "$DIST_DIR" synapse-studio/cardfront-cradle-of-echoes:web --userversion 0.1.0-alpha
```

### 5.3 `steam-publish` ([`skills/workflows/steam-publish/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/steam-publish/SKILL.md))
1. **Missing SteamPipe VDF Manifests (`steam-publish/SKILL.md:110-163`):** The repository currently has `0` `.vdf` files (`app_build_*.vdf` / `depot_build_*.vdf`). Before running [`scripts/check_steam_build.py`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/steam-publish/scripts/check_steam_build.py), a `steam/` directory with `FileExclusion` rules for `*.pdb`, `*.burst.debug*`, and `*DoNotShip*` must be added.
2. **Steamworks Generative AI Content Survey (`steam-publish/SKILL.md:202`):** Pre-generated ComfyUI card/stage art in `GeneratedArt/` must be declared under the *"Pre-Generated AI Content"* section of the Steamworks Content Survey.

---

## 6. Verification Summary (`checks.json`)

All **18 automatable checks** in [`Datasets/mirofish_gameplay/skills_ai_save_ship/checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/checks.json) have been executed and validated against the live `8096` server, static source files, and the 16,000-match [`raw/ai_benchmark.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json) telemetry.
