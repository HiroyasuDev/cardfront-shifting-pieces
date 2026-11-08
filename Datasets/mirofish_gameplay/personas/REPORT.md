# Cardfront: Cradle of Echoes — 10-Persona Grounded Playtest Swarm & Balance Report

- **Target Under Test:** `WebPlayable/cardfront_cradle_of_echoes_playable.html` (`http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`)
- **Swarm Scale:** **10 distinct player personas × 4 stages × 3 matches = 120 full matches (`480` player turns, `476` boss turns, `580` real mouse drag gestures)** executed in headless Chromium via Playwright (`scripts/play_swarm.js`).
- **Epistemic Hygiene (REAL vs. SYNTHETIC Separation):**
  - **100% REAL Browser Telemetry (`raw/matches.jsonl`, `raw/moves.jsonl`, `raw/persona_summaries.json`, `raw/repro_bugs.json`, `raw/cvd_color_pairs.json`):** Every card deployment, Tactical Slide, column-die nudge, and full-dice reroll was driven through real Playwright mouse/pointer events on the live game DOM. All outcomes (captures, scores, boss replies, misdrops, drag retries, tile landing mismatches, modal titles, and screenshots) were read back from the live browser state.
  - **Explicitly Marked SYNTHETIC Subjective Layer (`feedback/persona_feedback.json`, `feedback/feedback_consistency.json`):** Post-session 1–10 ratings, NPS scores, likes, frustrations, and quotes were generated locally by `mlx-community/Qwen2.5-3B-Instruct-4bit` (`scripts/gen_feedback.py`) conditioned **exclusively** on `GAME_FACTS` and each persona's objective telemetry summary (`scripts/facts.py`), then audited item-by-item (`70` items) via `jevmlx.judge` (`fast` / `Qwen2.5-3B-Instruct-4bit`) plus deterministic contradiction rules (`scripts/judge_feedback.py`).

---

## 1. Executive Summary & Headline MiroFish Metrics

| Metric Category | Metric | Value | Grounding / Source |
|---|---|---|---|
| **Volume** | Total Browser Matches / Turns / Real Drags | **`120` matches / `480` turns / `580` drags** | `raw/matches.jsonl`, `raw/moves.jsonl` (`480` deploy drags + `100` slide drags) |
| **Overall Win Rate** | Pooled Win Rate (`10` personas × `12` matches) | **`94.2%` (`113 / 120` wins)** | `8/10` personas went **12–0 (`100%`)**; only `p04 CasualMobileTapper` (`9–3`, `75%`) and `p06 TCGFirstTimeNewcomer` (`8–4`, `67%`) ever lost a match |
| **Score Margin** | Mean Final Margin (`Blue − Red`) | **`+4.667` cards** (avg `6.83` Blue vs `2.17` Red) | Margin distribution: `+7` (`44` matches), `+5` (`39`), `+3` (`18`), `+1` (`12`), `-1` (`6`), `-3` (`1`) |
| **Rules & Boss Fidelity** | Player Capture Prediction / Boss Reply Prediction | **`98.75%` (`474/480`) / `100.0%` (`476/476`)** | Rules engine (`scripts/sim.js`) matches live game `findCaptures()` and `executeBossTurn()` (`100%` boss determinism); the `6/480` player divergences are caused by physical drag release jitter landing on an adjacent tile (`deploy_mismatch = 6`) |
| **MiroFish Agency** | `MeanPlayerAgencyScore` / `MeanDecisionSpace` | **`0.9119` / `2.7054` cards** | `ZeroChoiceTurnRate = 1.87%` (`0%` on Turns 1–3; `7.5%` on Turn 4 when only 1–2 open tiles remain) |
| **MiroFish Frustration** | `MeanFrustrationIndex` / `WouldQuitPersonas` | **`0.0415` / `2` personas (`p04`, `p06`)** | Both casual/newcomer personas crossed their `1.5` frustration patience budget at **Match 7 (Stage 3 Match 1)** when `aiBonus = +1` begins |
| **Deuteranopia Impact** | `p08` Ownership Misreads & CIEDE2000 Drop | **`7` misreads / `14.9%–38.9%` $\Delta E_{00}$ retained** | `slide_target (#00E676)` vs `ai_frame (#FF2E54)` collapses from $\Delta E_{00} = 86.94 \to 12.92$ (`14.9%` retained); `flip_preview (#FFB800)` vs `defend_preview (#FF2E54)` drops to $\Delta E_{00} = 18.67$ (`38.9%` retained) |
| **SYNTHETIC Ratings** | Mean Ratings (`n=10`) / NPS / Hallucination Rate | **`Rules 8.8`, `Readability 8.5`, `Fun 8.3`, `Depth 6.9`, `Replay 6.1` / `NPS -10.0`** | `jevmlx.judge` + rule gate flagged **`34 / 70` (`48.6%`)** synthetic statements for over-claiming difficulty/progression or contradicting zero-loss/zero-dice telemetry |

---

## 2. Persona Swarm Architecture (`scripts/personas.js`)

Each persona is parameterized by an explicit decision policy, lookahead depth, error rate ($\epsilon$), thinking latency distribution (`thinkMs`), mechanic usage rules (`nudge`, `reroll`, `slide`), physical mouse motor noise (`dragJitter`, `misdropProb`, `dragSteps`), frustration budget (`patience`), and colour-vision misperception rate (`ownerMisread`):

| ID | Persona Handle | Archetype | Policy | $\epsilon$ | `thinkMs` | Nudge / Reroll / Slide | `dragJitter` / `misdropProb` / `steps` | Patience | `ownerMisread` |
|---|---|---|---|---|---|---|---|---|---|
| **`p01`** | `TripleTriadEdgeVeteran` | FF8/FF14 Triple Triad veteran | `minimax` (2-ply worst-case boss reply) | `0.03` | `1200–2600` | `when_gain` / `never` / `when_gain` | `0.08` / `0.00` / `18` | `3.0` | `0.00` |
| **`p02`** | `QueensBloodLaneBuilder` | FF7 Rebirth Queen's Blood fan | `lane` (+0.4 boosted col, +0.2 col control) | `0.06` | `1400–2800` | `when_gain` / `low_boost` / `when_gain` | `0.10` / `0.02` / `16` | `3.0` | `0.00` |
| **`p03`** | `SnapCompetitiveGrinder` | Marvel Snap ranked grinder | `expectimax` (2-ply $\mathbb{E}[\text{boss}]$) | `0.04` | `400–950` | `eval` / `low_boost` / `eval` | `0.14` / `0.03` / `8` | `2.0` | `0.00` |
| **`p04`** | `CasualMobileTapper` | Casual mobile bus player | `random_biased` (`flipBias = 0.60`) | `0.00` | `600–1500` | `never` / `drama` / `never` | `0.22` / `0.10` / `6` | `1.5` | `0.00` |
| **`p05`** | `IntoTheBreachTactician` | Perfect-info tactics purist | `minimax` (zero-noise, full nudge/slide search) | `0.00` | `2500–4500` | `eval` / `never` / `eval` | `0.06` / `0.00` / `22` | `3.5` | `0.00` |
| **`p06`** | `TCGFirstTimeNewcomer` | Complete TCG newcomer | `random_biased` (`flipBias = 0.35`) | `0.00` | `2500–6000` | `never` / `never` / `never` | `0.25` / `0.18` / `30` | `1.5` | `0.00` |
| **`p07`** | `StreamerSpectacleCaster` | Variety streamer / entertainer | `spectacle` (max immediate slide+place flips) | `0.08` | `900–2000` | `when_gain` / `drama` / `spectacle` | `0.12` / `0.03` / `14` | `2.0` | `0.00` |
| **`p08`** | `DeuteranopiaColorReader` | Colourblind (deuteranopia) player | `expectimax` + `8%` edge ownership confusion | `0.05` | `1600–3200` | `when_gain` / `never` / `when_gain` | `0.10` / `0.02` / `16` | `2.5` | **`0.08`** |
| **`p09`** | `CompletionistCollector` | 100% completionist / collector | `coverage` (+0.35 unplayed hero / unused mech) | `0.03` | `1400–2600` | `when_gain` / `low_boost` / `when_gain` | `0.09` / `0.01` / `16` | `3.5` | `0.00` |
| **`p10`** | `MinMaxOptimizer` | 3-ply game solver | `minmax3` (3-ply expectimax over top-12 plans) | `0.00` | `1800–3200` | `eval` / `never` / `eval` | `0.06` / `0.00` / `18` | `3.0` | `0.00` |

---

## 3. Objective Telemetry Across All 10 Personas (`raw/persona_summaries.json`)

Every number in the table below is **100% REAL browser telemetry** aggregated from `raw/matches.jsonl` (`120` matches) and `raw/moves.jsonl` (`480` turns):

| Persona | Policy | Win Rate | Avg Margin (`Min`) | Avg Score (`Blue–Red`) | Flips `+` / Match (`Place + Slide`) | Flips `−` / Match (Boss) | Nudges / Rerolls / Slides | Dice Turns % | Slide Turns % | Decision `ms` (Mean / Med) | Misdrop / Retry / Mismatch | Agency (`Regret`) | Zero-Choice % | Frustration Index | Would Quit At |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`p01 TripleTriadEdgeVeteran`** | `minimax` | **12/12 (`100%`)** | `+5.333` (`+3`) | `7.17 – 1.83` | `3.583 + 0.500` | `0.917` | `0 / 0 / 8` | `0%` | `17%` | `1878 / 1760` | `0 / 0 / 0` | `0.989` (`0.025`) | `4.2%` | `0.000` | — |
| **`p02 QueensBloodLaneBuilder`** | `lane` | **12/12 (`100%`)** | `+4.667` (`+1`) | `6.83 – 2.17` | `3.417 + 0.417` | `1.000` | `0 / 0 / 10` | `0%` | `21%` | `2126 / 2032` | `0 / 0 / 0` | `0.962` (`0.122`) | `0.0%` | `0.000` | — |
| **`p03 SnapCompetitiveGrinder`** | `expectimax` | **12/12 (`100%`)** | `+6.333` (`+5`) | `7.67 – 1.33` | `3.667 + 0.750` | `0.750` | `16 / 0 / 11` | `17%` | `23%` | `842 / 794` | `1 / 0 / 1` | `1.000` (`0.000`) | `0.0%` | `0.008` | — |
| **`p04 CasualMobileTapper`** | `random_biased` | **9/12 (`75%`)** | `+1.667` (`-1`) | `5.33 – 3.67` | `3.083 + 0.000` | `1.750` | `0 / 0 / 0` | `0%` | `0%` | `1072 / 1114` | `6 / 0 / 1` | `0.615` (`1.066`) | `2.1%` | `0.140` | **Match 7** (`p04_s3_m1`) |
| **`p05 IntoTheBreachTactician`** | `minimax` | **12/12 (`100%`)** | `+6.333` (`+3`) | `7.67 – 1.33` | `3.750 + 0.667` | `0.750` | `20 / 0 / 9` | `21%` | `19%` | `3467 / 3575` | `0 / 0 / 0` | `1.000` (`0.000`) | `0.0%` | `0.000` | — |
| **`p06 TCGFirstTimeNewcomer`** | `random_biased` | **8/12 (`67%`)** | `+0.833` (`-3`) | `4.92 – 4.08` | `2.500 + 0.000` | `1.583` | `0 / 0 / 0` | `0%` | `0%` | `4277 / 4201` | `12 / 0 / 4` | `0.588` (`1.027`) | `2.1%` | `0.252` | **Match 7** (`p06_s3_m1`) |
| **`p07 StreamerSpectacleCaster`** | `spectacle` | **12/12 (`100%`)** | `+4.833` (`+1`) | `6.92 – 2.08` | `3.333 + 0.750` | `1.167` | `0 / 0 / 16` | `0%` | `33%` | `1490 / 1539` | `0 / 0 / 0` | `0.989` (`0.028`) | `2.1%` | `0.008` | — |
| **`p08 DeuteranopiaColorReader`** | `expectimax` | **12/12 (`100%`)** | `+5.000` (`+3`) | `7.00 – 2.00` | `3.333 + 1.083` | `1.417` | `1 / 0 / 15` | `2%` | `31%` | `2314 / 2228` | `0 / 0 / 0` | `0.974` (`0.092`) | `4.2%` | `0.004` | — |
| **`p09 CompletionistCollector`** | `coverage` | **12/12 (`100%`)** | `+5.333` (`+3`) | `7.17 – 1.83` | `3.250 + 0.583` | `0.667` | `15 / 0 / 17` | `31%` | `35%` | `2061 / 1986` | `0 / 0 / 0` | `1.000` (`0.000`) | `4.2%` | `0.000` | — |
| **`p10 MinMaxOptimizer`** | `minmax3` | **12/12 (`100%`)** | `+6.333` (`+5`) | `7.67 – 1.33` | `3.667 + 0.917` | `0.917` | `18 / 0 / 14` | `19%` | `29%` | `2452 / 2421` | `0 / 0 / 0` | `1.000` (`0.000`) | `0.0%` | `0.002` | — |

### 3.1 Per-Stage Difficulty Progression (`raw/aggregate.json`)

| Stage | Boss Name (`bossId`) | AI Stat Bonus (`aiBonus`) | Matches | Win Rate | Avg Margin (`Blue − Red`) | Avg Flips Gained (`Place + Slide`) | Avg Flips Lost to Boss | Mean Player Agency |
|---|---|---|---|---|---|---|---|---|
| **Stage 1: Skystone Sanctuary** | `Eclipse Void Blade` (`e_eclipse`) | `+0` | `30` | **`100.0%` (`30/30`)** | **`+5.667`** | `4.000` | `0.667` | `0.901` |
| **Stage 2: Ivalice Law Sanctuary** | `Prism Core Archon` (`e_archon`) | `+0` | `30` | **`96.7%` (`29/30`)** | **`+5.333`** | `3.933` | `0.767` | `0.910` |
| **Stage 3: Costa del Sol Mirage** | `Emerald Colossus` (`e_colossus`) | **`+1` all edges** | `30` | **`83.3%` (`25/30`)** | **`+3.667`** | `3.600` | `1.267` | `0.908` |
| **Stage 4: Gold Saucer Colosseum** | `Inferno Core Seraph` (`e_inferno`) | **`+1` all edges** | `30` | **`96.7%` (`29/30`)** | **`+4.000`** | `4.167` | `1.667` | `0.928` |

- **All 7 losses across the entire 120-match dataset** occurred in `p04 CasualMobileTapper` (`p04_s2_m3` `4–5`, `p04_s3_m1` `4–5`, `p04_s3_m2` `4–5`) and `p06 TCGFirstTimeNewcomer` (`p06_s3_m1` `4–5`, `p06_s3_m2` `4–5`, `p06_s3_m3` `4–5`, `p06_s4_m2` `3–6`).
- **Stages 1 & 2 (`aiBonus = 0`) vs. Stages 3 & 4 (`aiBonus = 1`) are Identical in Rules:** Because enemy lineups are drawn uniformly from all 8 `ENEMY_MECHS` regardless of stage (`repro_bugs.json`), Stage 1 and Stage 2 are mathematically identical (`aiBonus = 0`), and Stage 3 and Stage 4 are mathematically identical (`aiBonus = 1`).

---

## 4. Deep-Dive Game Balance, Mechanics & Code-Grounded Bugs (`raw/repro_bugs.json`, `raw/aggregate.json`)

### 4.1 Why Competent Personas Win 100% of Matches (Card Stat Budget Asymmetry)

Deterministic inspection of `PLAYER_HEROES` vs. `ENEMY_MECHS` in `repro_bugs.json` reveals a massive base-stat advantage for the player:

- **Hero Edge Sum (`PLAYER_HEROES`, `n=8`):** Mean **`28.38`** (`h_arbiter: 30`, `h_oracle: 29`, `h_seraph: 29`, `h_archangel: 28`, `h_chronos: 28`, `h_kai: 28`, `h_phoenix: 28`, `h_valkyrie: 27`).
- **Enemy Mech Edge Sum (`ENEMY_MECHS`, `n=8`):** Mean **`24.50`** (`e_eclipse: 23`, `e_archon: 24`, `e_shinobi: 24`, `e_colossus: 25`, `e_cryo: 25`, `e_inferno: 25`, `e_reaper: 25`, `e_titan: 25`).
- **Pairwise Edge Dominance (`edge_win_prob`):**
  - On **Stages 1 & 2 (`aiBonus = 0`)**, a random unboosted hero edge strictly beats a random facing enemy edge **`65.2%` of the time** (before column dice boosts!).
  - On **Stages 3 & 4 (`aiBonus = +1`, enemy mean `28.50`)**, an unboosted hero edge beats a facing enemy edge **`36.7%` of the time**, **but** the player also gets **Column 3D Dice boosts (`+1` on pips `4–6`)** which apply **only to `owner === 'player'` cards** (`getCardEffectiveStats` ignores `colDice` when `isEnemy === true`), plus **Tactical Slide** (an extra free capture action per turn that the boss cannot perform), plus **last-move advantage on Turn 4** (since the boss opens at `(0,1)` and the player places the 9th card on Turn 4 with no boss counter-turn!).
- **Turn-by-Turn Boss Flip Decay (`boss_flips_by_turn`):**
  - Because the player places the 9th and final card on Turn 4, the boss only acts on Turns 1, 2, and 3 (except when a slide or mis-sequencing occurs): mean boss flips per turn drop from **`0.467` on Turn 1** (`56` cards lost) $\to$ **`0.239` on Turn 2** (`28` lost) $\to$ **`0.267` on Turn 3** (`32` lost) $\to$ **`0.126` on Turn 4** (`15` lost).
- **Tile Vulnerability (`lost_by_tile_kind`):**
  - Out of `131` total player cards flipped by the boss across 120 matches, **`97` (`74.0%`) were on edge tiles**, **`20` (`15.3%`) on the center tile**, and only **`14` (`10.7%`) on corner tiles**, confirming `p01 TripleTriadEdgeVeteran`'s corner-safety heuristic.

### 4.2 Column Dice & Tactical Slide Leverage (`raw/aggregate.json`)

- **Column Dice Boost Effect (`dice_effect`):**
  - Across `480` card deployments, **`365` (`76.0%`)** were placed into a column whose die showed `4–6` (`+1` boost), yielding **`0.877` immediate placement flips/deploy** vs. **`0.722` flips/deploy** in unboosted columns (`+21.5%` more captures).
  - Personas that actively evaluated nudges (`p03`, `p05`, `p09`, `p10`; `40` matches with dice used) achieved a **`100.0%` win rate** and an average margin of **`+6.15`**, compared to **`91.2%` win rate** and **`+3.925` margin** across the `80` matches without dice usage.
  - Notably, **full-dice reroll (`rerolls_total = 0` across all 10 personas)** was never triggered even by `low_boost` / `drama` policies because initial column dice + 2 starting nudges (+1 per boss turn) almost always provided $\ge 2$ boosted columns without needing a random reroll.
- **Tactical Slide Leverage (`slide_usage_split`):**
  - Used **`100` times across `72` matches (`100%` execution success, `0` failed slides)**, generating **`0.722` extra flips per slide** and lifting average match margin from **`+3.458` (no slide)** to **`+5.472` (with slide)** (`+2.01` cards/match).

### 4.3 Three Confirmed Game-Logic Bugs in `repro_bugs.json`

1. **[Logic Bug 1] Boss Tie-Break RNG Is Dead Code (`repro_bugs.json → boss_tiebreak`):**
   - In `executeBossTurn()`, the code initializes `let bestSlot = openSlots[Math.floor(Math.random() * openSlots.length)]; let bestCount = -1;` and then iterates `openSlots` in row-major order (`(0,0)` to `(2,2)`) with `if (flips.length > bestCount) { bestCount = flips.length; bestSlot = slot; }`.
   - Because `flips.length >= 0` is **always** strictly greater than `-1` on the first iteration (`openSlots[0]`), `bestSlot` is **unconditionally overwritten by the first open slot in row-major order** whenever all slots tie! Across `200/200` trials on an all-tie board, the boss placed at `(0,0)` **200 times (`100%`)**, never using the random tie-breaker.
2. **[Logic Bug 2] Captured Enemy Cards Lose Their `aiBonus` (+1) When Any Column Die Changes (`repro_bugs.json → captured_card_stat_drift`):**
   - When a card is deployed, `state.grid[r][c].nesw` stores a snapshot of its effective stats at placement time (so an enemy `e_titan` on Stage 3 has `[8, 6, 8, 7]` from base `[7, 5, 7, 6] + aiBonus 1`).
   - When the player captures that enemy card, `owner` flips to `'player'` while `nesw` remains `[8, 6, 8, 7]`.
   - However, as soon as the player nudges **any** column die (even an unrelated column!) or rerolls, `recalcBoardStats()` recomputes every `owner === 'player'` slot using `getCardEffectiveStats(cell.cardId, c, false)` (`isEnemy = false`), which **strips the card's `aiBonus`**, dropping the captured `e_titan` in Column 2 (die=2) from `[8, 6, 8, 7]` down to `[7, 5, 7, 6]`!
3. **[Design Bug 3] Stage Boss Identity Is ~23% Absent from the Match (`repro_bugs.json → stage_boss_presence`):**
   - `startStage()` shuffles all 8 `ENEMY_MECHS` and takes the first 6 (`1` starter + `5` in `aiPool`) without guaranteeing that `stage.bossId` is included (and the boss only plays 4 cards total per match: 1 starter + 3 replies). Across 300 trials per stage, `stage.bossId` was in the 6-card pool only **`74.7%–79.7%` of the time** (and actually deployed on the board only ~62.5% of matches), even though the right-hand Boss Profile banner always displays `stage.bossId` (`Eclipse Void Blade`, `Prism Core Archon`, `Emerald Colossus`, `Inferno Core Seraph`).

---

## 5. Deuteranopia Simulation & Color-Pair Distinguishability (`p08`, `raw/cvd_color_pairs.json`)

Using the **Machado, Oliveira & Fernandes (2009)** deuteranopia projection matrix ($\text{severity} = 1.0$ in linear sRGB, `scripts/cvd_sim.py`), we transformed all 24 screenshots of `p08 DeuteranopiaColorReader` (`screenshots/p08_DeuteranopiaColorReader/*_deutan.jpg` and side-by-side `*_compare.jpg`) and computed **CIEDE2000 ($\Delta E_{00}$)** perceptual color distances across the 6 semantic color pairs used by the game:

| Semantic Gameplay Color Pair | Normal Hex (`A` vs `B`) | Deuteranopia Simulated Hex (`A` vs `B`) | $\Delta E_{00}$ (Normal) | $\Delta E_{00}$ (Deuteranopia) | Retained Perceptual Distance | Gameplay Impact on `p08` |
|---|---|---|---|---|---|---|
| **1. `slide_target (--emerald)` vs `ai_frame (--red-enemy)`** | `#00E676` vs `#FF2E54` | `#D1C27E` vs `#A4954E` | `86.94` | **`12.92`** | **`14.9%` (CRITICAL COLLAPSE)** | Both collapse into muddy olive-tan; green Tactical Slide target ring is nearly indistinguishable from adjacent red enemy card frames. |
| **2. `slide_target (--emerald)` vs `flip_target (--gold)`** | `#00E676` vs `#FFB800` | `#D1C27E` vs `#E5CC17` | `42.22` | **`12.32`** | **`29.2%` (SEVERE COLLAPSE)** | Emerald slide target and gold capture target both become warm yellow-ochre. |
| **3. `flip_preview (#FFB800)` vs `defend_preview (#FF2E54)` SVG lines** | `#FFB800` vs `#FF2E54` | `#E5CC17` vs `#A4954E` | `48.03` | **`18.67`** | **`38.9%` (POOR)** | Gold "will capture" telegraph lines and red "enemy threat" telegraph lines converge toward yellow-brown. |
| **4. `turn_badge` (`YOUR TURN` `#FFB800` vs `BOSS TURN` `#FF2E54`)** | `#FFB800` vs `#FF2E54` | `#E5CC17` vs `#A4954E` | `48.03` | **`18.67`** | **`38.9%` (POOR)** | Mitigated by text change (`YOUR TURN` vs `BOSS TURN`). |
| **5. `player_frame (--blue-ally)` vs `ai_frame (--red-enemy)`** | `#00E5FF` vs `#FF2E54` | `#B2C7FF` vs `#A4954E` | `84.55` | **`45.34`** | **`53.6%` (MODERATE)** | Hue separation drops by nearly half (light slate-blue vs olive-brown), and as shown in `ux_qa/raw/t5_color_analysis.json`, border-to-border luminance contrast under deuteranopia is only **`1.78:1`** with **zero non-color ownership icons**. |
| **6. `victory_title (#00E5FF)` vs `defeat_title (#FF2E54)`** | `#00E5FF` vs `#FF2E54` | `#B2C7FF` vs `#A4954E` | `84.55` | **`45.34`** | **`53.6%` (MODERATE)** | Mitigated by `🏆 VICTORY` vs `💀 DEFEAT` text. |

In browser play, `p08 DeuteranopiaColorReader` (`ownerMisread = 0.08`) suffered **`7` ownership misreads** while planning (`avg_flips_lost = 1.417/match`, the highest of any lookahead persona, vs `0.750` for `p03`), yet still won `12/12` matches (`avg_margin = +5.0`) because hero card base stats and Tactical Slide (`1.083` slide flips/match) compensated for single-edge misreads.

---

## 6. SYNTHETIC Persona Feedback & `jevmlx.judge` Consistency Audit (`feedback/`)

> [!IMPORTANT]
> **SYNTHETIC Labeling:** All ratings, NPS scores, likes, frustrations, and quotes in this section were generated by local `mlx-community/Qwen2.5-3B-Instruct-4bit` (`feedback/persona_feedback.json`) role-playing each persona from `GAME_FACTS` + that persona's objective telemetry (`scripts/facts.py`). Every statement (`70` total across 10 personas) was then audited by `jevmlx.judge` (`fast`) and deterministic contradiction rules (`feedback/feedback_consistency.json`).

### 6.1 SYNTHETIC Ratings Matrix & Hallucination Gate Results

| Persona (`SYNTHETIC` Ratings) | Fun | Rules Clarity | Board Readability | Difficulty Fairness | Strategic Depth | Drag & Drop Feel | Art | Replay Intent | NPS (`0–10`) | `jevmlx` + Rule Flagged Items | Plausibility / Consistency Notes (`feedback_consistency.json`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **`p01 TripleTriadEdgeVeteran`** | `7` | `9` | `7` | `7` | `6` | `8` | `6` | `5` | `6` | **`0 / 7` (`0%`)** | Fully grounded; notes absence of progression/multiplayer and cost of $\epsilon$ random moves (`2` made). |
| **`p02 QueensBloodLaneBuilder`** | `9` | `9` | `8` | `9` | `8` | `8` | `7` | `7` | `8` | **`3 / 7` (`43%`)** | Rule-flagged for wording *"match progression"* (`no progression`), plus `rating_note`: `difficulty_fairness=9` despite 100% wins with `+4.67` avg margin. |
| **`p03 SnapCompetitiveGrinder`** | `8` | `9` | `9` | `8` | `7` | `6` | `7` | `7` | `8` | **`7 / 7` (`100%`)** | Complained about *"frequent nudging and rerolling"* even though `rerolls_total = 0` (`16` nudges); `jevmlx.judge` flagged generic praise against `100%` steamroll telemetry (`+6.33` margin). |
| **`p04 CasualMobileTapper`** | `7` | `7` | `8` | `7` | `5` | `6` | `6` | `5` | `6` | **`6 / 7` (`86%`)** | Quote grounded (`jev_verdict: true, p=0.611`), but `jevmlx.judge` flagged *"Engaging strategic depth"* and *"Clear and intuitive rules"* as inconsistent with a casual player who had `6` misdrops, `0` dice/slides, and hit `would_quit_at_match = 7`. |
| **`p05 IntoTheBreachTactician`** | `10` | `10` | `10` | `10` | `9` | `9` | `8` | `7` | `9` | **`1 / 7` (`14%`)** | `6/6` likes & frustrations grounded (`p = 0.68–0.83`); `rating_note`: `difficulty_fairness=10` despite `12–0` record and `+6.33` margin. |
| **`p06 TCGFirstTimeNewcomer`** | `6` | `7` | `7` | `7` | `5` | **`2`** | `6` | **`4`** | **`4`** | **`2 / 7` (`29%`)** | Accurately rated `drag_drop_feel = 2` and `nps = 4` after suffering **`12` misdrops and `4` tile mismatches** (`would_quit_at_match = 7`), but hallucinated *"No dice system"* (confusing `0` dice used with no dice existing in the game). |
| **`p07 StreamerSpectacleCaster`** | `9` | `10` | `9` | `8` | `7` | `9` | `8` | `6` | `7` | **`2 / 7` (`29%`)** | All 3 frustrations and quote grounded (`p = 0.51–0.82`: flat difficulty curve, lack of deck-building/progression); *"The game is very fair and balanced"* flagged against `12–0` win rate. |
| **`p08 DeuteranopiaColorReader`** | `10` | `10` | `10` | `10` | `7` | `10` | `9` | `5` | `7` | **`4 / 7` (`57%`)** | Frustrations & quote **strongly grounded (`p = 0.81–0.93`)** on the `7` colourblind ownership misreads; likes flagged for claiming *"rerolling dice"* (`rerolls_total = 0`) and inflated `board_readability = 10` / `difficulty_fairness = 10`. |
| **`p09 CompletionistCollector`** | `7` | `7` | `7` | `7` | `5` | `7` | `6` | `5` | `7` | **`2 / 7` (`29%`)** | `5/7` items grounded (`p = 0.64–0.78`), including *"Rarely have to make difficult strategic choices"*, *"Lack of progression makes it predictable"*, and *"Limited choices due to hand size"*. |
| **`p10 MinMaxOptimizer`** | `10` | `10` | `10` | `10` | `10` | `10` | `10` | `10` | `10` | **`7 / 7` (`100%`)** | Model produced ceiling `10/10` ratings across the board despite `100%` win rate (`+6.33` margin, `0` regret); `jevmlx.judge` and `rating_notes` flagged the uncritical praise. |
| **Mean (`SD`) Across 10 Personas** | **`8.30` (`1.42`)** | **`8.80` (`1.25`)** | **`8.50` (`1.20`)** | **`8.30` (`1.27`)** | **`6.90` (`1.64`)** | **`7.50` (`2.29`)** | **`7.30` (`1.35`)** | **`6.10` (`1.64`)** | **`7.20` (`NPS -10.0`)** | **`34 / 70` (`48.6%` flagged)** | Mean rating SD across dimensions = **`1.508`**. Lowest dimensions: **Replay Intent (`6.10`)** and **Strategic Depth (`6.90`)**. |

### 6.2 Objective Telemetry vs. SYNTHETIC Rating Correlations (Spearman $\rho$, $n=10$)

Computed in `scripts/aggregate.py` (`raw/aggregate.json → obj_vs_subj_spearman_n10`):

| Objective Telemetry Metric | SYNTHETIC Subjective Dimension | Spearman $\rho$ ($n=10$) | Interpretation |
|---|---|---|---|
| **Drag Problems (`misdrops + retries + mismatch`)** | **`drag_drop_feel` rating** | **`-0.815`** | **Strongest alignment:** Personas with physical drag errors (`p06` with `16` drag issues $\to 2/10$, `p04` with `7` $\to 6/10`, `p03` with `2` $\to 6/10`) rated `drag_drop_feel` sharply lower than zero-misdrop personas (`8–10/10`). |
| **Win Rate (`win_rate`)** | **`difficulty_fairness` rating** | **`+0.544`** | Personas that won `100%` of matches rated `difficulty_fairness` higher (`7–10`) than losing personas (`7`), revealing a classic LLM sycophancy bias: equating winning every match with "fair difficulty" (caught by `rating_notes`). |
| **Avg Score Margin (`avg_margin`)** | **`fun` rating** | **`+0.519`** | High-margin winners (`+5.0` to `+6.33`) rated `fun` higher (`7–10`) than low-margin strugglers (`p06`: `+0.83` $\to 6/10$, `p04`: `+1.67` $\to 7/10`). |
| **Mean Player Agency (`agency_mean`)** | **`strategic_depth` rating** | **`+0.463`** | Lookahead planners (`agency = 0.96–1.00`) rated `strategic_depth` higher than `random_biased` personas (`agency = 0.59–0.62` $\to 5/10$). |
| **Mean Frustration Index (`frustration_index_mean`)** | **`NPS` (`0–10`)** | **`-0.463`** | Higher telemetry frustration (`p06 = 0.252`, `p04 = 0.140`) directly depressed NPS (`4` and `6`, the two detractors that drove net `NPS = -10.0`). |
| **Dice Usage Rate (`pct_turns_using_dice`)** | **`strategic_depth` rating** | **`+0.298`** | Weak positive correlation; `p09` used dice on `31%` of turns but rated `strategic_depth = 5` due to how easily it solved every stage. |

### 6.3 Grounded Qualitative Themes (`raw/aggregate.json → themes`)

Filtering to **only unflagged, `jevmlx.judge`-verified statements**:
1. **Low Challenge / Predictability & Lack of Meta-Progression (`grounded_frustration = 3` personas: `p02`, `p07`, `p09`; plus `p01`, `p05`, `p06` on missing progression/deck-building):** Competent personas won `100%` of matches (`+4.67` to `+6.33` avg margin) and consistently cited the flat difficulty curve across stages and the lack of deck-building or collection hooks (`replay_intent = 6.10/10`, lowest of all 8 dimensions).
2. **Readability & Rules Clarity (`grounded_like = 3` personas: `p01`, `p05`, `p06`; `grounded_frustration = 1`: `p08`):** Basic cardinal comparison rules and telegraph previews were easy to grasp for sighted players, whereas `p08 DeuteranopiaColorReader` (`jev_probability = 0.929` and `0.886`) specifically highlighted colour-based ownership confusion (`7` misreads).
3. **Tactical Slide & Drag-and-Drop Core Loop (`grounded_like = 3` personas: `p01`, `p02`, `p07`):** Smooth drag-and-drop and once-per-turn Tactical Slide combos (`+2.01` margin lift when used) were the standout moment-to-moment mechanical highlights for mid-core/streamer personas, whereas high-jitter newcomers (`p06`, `12` misdrops + `4` magnet mismatches) struggled without an onboarding tutorial.

---

## 7. Actionable Balance & Persona-Driven Recommendations

1. **Close the Hero vs. Enemy Stat Gap (`28.38` vs `24.50` Edge Sum) & Let the Boss Use Column Dice Boosts:**
   - Raise `ENEMY_MECHS` base edge sums by `+2` to `+3` points (or allow enemy cards in boosted columns `4–6` to also receive `+1` on Stage 2+), and differentiate Stages 1–4 with distinct stage rules rather than only `aiBonus: 0, 0, 1, 1`.
2. **Fix the 3 Confirmed Rules/State Bugs (`repro_bugs.json`):**
   - Initialize `bestCount = -1` tie-breaking in `executeBossTurn()` to collect all tied max-flip slots and pick randomly among them (instead of always picking `(0,0)`).
   - Store `originalOwner` / `spawnAiBonus` on board cells so `recalcBoardStats()` does not strip `aiBonus` from captured boss cards when a column die is nudged.
   - Always include `stage.bossId` in the 4 cards the boss actually deploys during that stage (e.g., as the boss's Turn 3 finisher or opener).
3. **Add Onboarding Callouts for Dice Nudge & Tactical Slide (`p04`, `p06`):**
   - Both casual/newcomer personas (`p04`, `p06`) never discovered column nudges or Tactical Slide (`0%` usage), suffered `18` combined misdrops, lost `7` matches on Stages 2–4, and hit their quit threshold at **Match 7**. Highlighting a suggested nudge/slide on Stage 1 Turn 2 would bridge the skill cliff at Stage 3.
4. **Fix Deuteranopia Palette Collisions (`p08`, `cvd_color_pairs.json`):**
   - Replace `--emerald (#00E676)` vs `--gold (#FFB800)` vs `--red-enemy (#FF2E54)` colour-only telegraph distinctions (which collapse to $\Delta E_{00} = 12.3–18.7$ under deuteranopia) with distinct stroke patterns (dashed vs solid SVG lines), distinct badge shapes (`◆ ALLY` vs `▲ BOSS`), and higher luminance separation.
