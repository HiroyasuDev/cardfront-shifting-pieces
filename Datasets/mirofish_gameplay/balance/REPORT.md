# CARDFRONT: Cradle of Echoes — Quantitative Balance, Skill-Gap & What-If Tuning Report

- **Target Deliverable**: [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](../../../WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Simulation & Search Engine**: [`engine.js`](engine.js), [`policies.js`](policies.js), [`search.js`](search.js), [`suites.js`](suites.js), [`run.js`](run.js), [`aggregate.js`](aggregate.js)
- **Browser Cross-Validation**: [`validate.js`](validate.js) → [`results/validation_summary.json`](results/validation_summary.json) (**166 matches, 975 actions, 100.0% agreement**)
- **Aggregated Dataset**: [`results/summary.json`](results/summary.json) (**322,000 simulated games**: 112,000 baseline main games across 12 policies × 4 stages + 210,000 what-if variant games across 8 rule variants)

---

## 1. Executive Summary & Headline Findings

We ported the exact rules of **CARDFRONT: Cradle of Echoes** into a zero-allocation headless engine ([`engine.js`](engine.js)) and compact bitboard expectimax solver ([`search.js`](search.js)), cross-validated it against the live Chromium DOM implementation via Playwright ([`results/validation_summary.json`](results/validation_summary.json)), and simulated **322,000 games** across **12 player policies** and **8 what-if tuning variants** ([`results/summary.json`](results/summary.json)).

1. **100% Browser-to-Engine Fidelity**: Across **166 live browser matches** (160 synchronous + 6 real-time timer matches) and **975 individual actions** spanning all 4 stages and 9 distinct policies (`chaos`, `random`, `greedy`, `greedy_dice`, `greedy_slide`, `greedy_all`, `lookahead`, `expert`, `expert_noslide`), action-level state snapshots (`grid`, `nesw`, `owner`, `hand`, `aiPool`, `colDice`, `nudgesLeft`, `rerollsLeft`, `usedSlideThisTurn`) and final scores agreed **100.0%** with zero page errors ([`results/validation_summary.json`](results/validation_summary.json)).
2. **Every Seed in the Shipped Game Is Mathematically Winnable (`100.0%` Expectimax / Lookahead Win Rate)**:
   - Because player heroes out-stat enemy mechs by **+3.88 total points per card** (`28.38` vs `24.50`), and the stage starts with two pre-charged column dice (`colDice = [4, 2, 5]`, so Columns 1 & 3 already grant `+1 All Sides`) plus `2` nudges (`+1` refill per turn), **Depth-2 Lookahead (`lookahead`)**, **Expectimax (`expert`)**, **Expectimax-NoTools (`expert_notools`)**, and **Perfect-Information Oracle (`oracle`)** all achieve a **100.00% win rate (10,000 / 10,000 wins)** across all four stages (`root_value = 1.000` on 100% of seeds).
3. **Massive Skill Gap (`Expert − Random = +45.48 pp` Overall, `+63.80 pp` on Stages 3–4)**:
   - **Stages 1–2 (`aiBonus = 0`)**: Even a purely **Random** policy wins **72.84%** of games (`meanBlue = 5.038`), while **Myopic Greedy** (deploy only) wins **98.26%** (`meanBlue = 6.325`), leaving only a **+27.16 pp** Expert-vs-Random gap and **+1.74 pp** Expert-vs-Greedy gap. Stages 1 and 2 are effectively tutorial difficulty.
   - **Stages 3–4 (`aiBonus = +1`)**: **Random** collapses to **36.20%** (`meanBlue = 4.108`), **Greedy** drops to **84.46%** (`meanBlue = 5.438`), **Greedy+Dice** reaches **88.84%**, **Greedy+Slide** jumps to **94.56%**, **Greedy+Dice+Slide** reaches **96.14%**, and **Lookahead / Expert** hit **100.00%** (`meanBlue = 6.586` for `expert`, `7.428` for `lookahead`, `7.565` for `expert_margin`). Here the skill gap widens to **+63.80 pp** (`Expert − Random`) and **+15.54 pp** (`Expert − Greedy`).
4. **Zero Draws Possible (`0.00%` Draw Rate)**: Because a 3×3 board has 9 cells and every game deploys `1 (boss opener) + 4 (player) + 4 (boss) = 9` cards, `blue + red = 9` (odd) at termination in 100% of games. Ties cannot occur.
5. **Tactical Slide Is ~4× More Valuable Than Dice Nudges/Rerolls**:
   - On the Greedy ladder (overall across S1–S4), adding **Dice tools alone** (`greedy_dice`) raises win rate by **+2.33 pp** (`91.36% → 93.69%`, `+0.138 Blue`), whereas adding **Tactical Slide alone** (`greedy_slide`) raises win rate by **+5.85 pp** (`91.36% → 97.21%`, `+0.712 Blue`). On Stages 3–4, Slide alone adds **+10.10 pp** (`84.46% → 94.56%`) vs **+4.38 pp** for Dice (`84.46% → 88.84%`).
   - Why is Dice utility muted in the baseline? Because stages start with `colDice = [4, 2, 5]` (two of three columns **already boosted** for free on Turn 1, and only 1 nudge needed to boost Column 2 from `2 → 4` takes 2 nudges, which the player already holds at Turn 1!). Consequently, `nudgeRefill = 0` (`noRefill` variant) has **0.00 pp** impact on any policy, and optimal policies spend **0.000 rerolls/game** (rerolling two already-boosted dice has negative expected value).
6. **Hidden Information (Boss Pool Order) Has Zero Win-Rate Value (`Oracle − Expert = 0.00 pp`)**:
   - Knowing the exact sequence of upcoming enemy cards (`oracle`) yields the exact same win rate (**100.00%**) and virtually identical `meanBlue` (**7.043** vs **7.043**) as imperfect-information `expert`, because `expert` already finds guaranteed winning lines against all `C(7,4)` boss pool permutations.

---

## 2. Cross-Validation Against the Live Browser Game (`results/validation_summary.json`)

Before running large-scale Monte-Carlo suites, [`validate.js`](validate.js) injected a seeded `mulberry32` PRNG into `WebPlayable/cardfront_cradle_of_echoes_playable.html` and replayed 166 full games across 9 policies (`chaos`, `random`, `greedy`, `greedy_dice`, `greedy_slide`, `greedy_all`, `lookahead`, `expert`, `expert_noslide`), comparing full state snapshots after every single nudge, reroll, tactical slide, player deploy, and boss reply:

| Validation Metric | Value | Source |
|---|---|---|
| **Total Browser Matches** | **166** (160 fast-clock + 6 real-time 650 ms clock) | [`results/validation_summary.json`](results/validation_summary.json) |
| **Total Actions Compared** | **975** | [`results/validation_summary.json`](results/validation_summary.json) |
| **Action-by-Action State Agreement** | **100.0% (975 / 975)** | [`results/validation_summary.json`](results/validation_summary.json) |
| **Final Score & Winner Agreement** | **100.0% (166 / 166)** | [`results/validation_summary.json`](results/validation_summary.json) |
| **Browser Console / Page Errors** | **0** | [`results/validation_summary.json`](results/validation_summary.json) |

---

## 3. Win/Draw/Loss Rates & Score Margins by Policy and Stage

*(Source: `byPolicyStage` and `skillGap` in [`results/summary.json`](results/summary.json); `N = 2,500` games/stage per policy, `N = 500`/stage for depth-limited `expert_margin`.)*

### 3.1 Win Rate (%) and Mean Blue Score (out of 9) Across Stages

| Policy | Description | Stage 1 (`+0`) | Stage 2 (`+0`) | Stage 3 (`+1`) | Stage 4 (`+1`) | S1–S2 Mean | S3–S4 Mean | Overall Win % (±95% CI) | Overall Mean Blue (±SD) |
|---|---|---|---|---|---|---|---|---|---|
| **`random`** | Uniform random card & cell (no tools) | 72.80% (5.05) | 72.88% (5.03) | 36.20% (4.11) | 36.20% (4.11) | 72.84% (5.04) | 36.20% (4.11) | **54.52%** (±0.98%) | **4.573** (±1.116) |
| **`greedy`** | Max immediate deploy flips (no tools) | 98.40% (6.31) | 98.12% (6.34) | 84.60% (5.43) | 84.32% (5.45) | 98.26% (6.33) | 84.46% (5.44) | **91.36%** (±0.55%) | **5.882** (±1.043) |
| **`greedy_dice`** | Greedy + nudge/reroll when EV > current | 98.80% (6.43) | 98.28% (6.43) | 88.96% (5.60) | 88.72% (5.62) | 98.54% (6.43) | 88.84% (5.61) | **93.69%** (±0.48%) | **6.020** (±1.023) |
| **`greedy_slide`** | Greedy + 1-turn slide+deploy flip max | 99.80% (7.08) | 99.92% (7.09) | 94.56% (6.09) | 94.56% (6.12) | 99.86% (7.09) | 94.56% (6.10) | **97.21%** (±0.32%) | **6.594** (±1.016) |
| **`greedy_all`** | Greedy + Dice + Tactical Slide | 99.88% (7.18) | 99.92% (7.19) | 96.08% (6.23) | 96.20% (6.27) | 99.90% (7.19) | 96.14% (6.25) | **98.02%** (±0.27%) | **6.720** (±0.990) |
| **`lookahead`** | Depth-2 minimax (worst-case boss reply) | 100.0% (7.87) | 100.0% (7.87) | 100.0% (7.43) | 100.0% (7.43) | 100.0% (7.87) | 100.0% (7.43) | **100.00%** (±0.00%) | **7.648** (±0.567) |
| **`expert_notools`** | Full-game expectimax, no dice/slide | 100.0% (6.50) | 100.0% (6.49) | 100.0% (5.78) | 100.0% (5.74) | 100.0% (6.50) | 100.0% (5.76) | **100.00%** (±0.00%) | **6.128** (±0.845) |
| **`expert_noslide`** | Full-game expectimax, dice only | 100.0% (6.59) | 100.0% (6.58) | 100.0% (6.02) | 100.0% (6.00) | 100.0% (6.59) | 100.0% (6.01) | **100.00%** (±0.00%) | **6.297** (±0.824) |
| **`expert_nodice`** | Full-game expectimax, slide only | 100.0% (7.26) | 100.0% (7.27) | 100.0% (6.14) | 100.0% (6.10) | 100.0% (7.27) | 100.0% (6.12) | **100.00%** (±0.00%) | **6.693** (±0.965) |
| **`expert`** | Full-game expectimax on `P(win)` | 100.0% (7.50) | 100.0% (7.50) | 100.0% (6.60) | 100.0% (6.57) | 100.0% (7.50) | 100.0% (6.59) | **100.00%** (±0.00%) | **7.043** (±0.847) |
| **`expert_margin`** | Expectimax on `E[Blue]` (2-turn horizon) | 100.0% (7.98) | 100.0% (7.98) | 100.0% (7.57) | 100.0% (7.56) | 100.0% (7.98) | 100.0% (7.57) | **100.00%** (±0.00%) | **7.773** (±0.510) |
| **`oracle`** | Expectimax with perfect boss pool knowledge | 100.0% (7.50) | 100.0% (7.50) | 100.0% (6.60) | 100.0% (6.57) | 100.0% (7.50) | 100.0% (6.59) | **100.00%** (±0.00%) | **7.043** (±0.848) |

### 3.2 Two-Regime Difficulty Structure (Stages 1–2 vs Stages 3–4)
- **Stages 1 & 2 are statistically identical** (`aiBonus = 0` for both; `STAGES[idx].bossId` only changes the UI banner, not the enemy deck). Similarly, **Stages 3 & 4 are statistically identical** (`aiBonus = 1` for both).
- Why does `expert_margin` (`meanBlue = 7.773`) achieve a higher average Blue card count than `expert` (`meanBlue = 7.043`) while both win `100.0%`? Because `expert` optimizes binary `P(win)` (`blue >= 5`) with `Star1` alpha-beta pruning that stops searching as soon as it proves a move has `P(win) = 1.0`, whereas `expert_margin` optimizes expected card count `E[Blue / 9]`, crushing the boss **7.98–1.02** on Stages 1–2 (`8–1` in 98% of games!) and **7.57–1.43** on Stages 3–4.

---

## 4. Dice & Tactical Slide Value Ablation (`diceAndSlideValue`)

| Stage Group | Baseline (`greedy` / `expert_notools`) | +Dice Only (`greedy_dice` / `expert_noslide`) | +Slide Only (`greedy_slide` / `expert_nodice`) | +Both (`greedy_all` / `expert`) |
|---|---|---|---|---|
| **Greedy: S1–S2** | 98.26% (6.325 Blue) | 98.54% (**+0.28 pp**, +0.102 Blue) | 99.86% (**+1.60 pp**, +0.761 Blue) | 99.90% (**+1.64 pp**, +0.864 Blue) |
| **Greedy: S3–S4** | 84.46% (5.438 Blue) | 88.84% (**+4.38 pp**, +0.174 Blue) | 94.56% (**+10.10 pp**, +0.664 Blue) | 96.14% (**+11.68 pp**, +0.812 Blue) |
| **Greedy: Overall** | 91.36% (5.882 Blue) | 93.69% (**+2.33 pp**, +0.138 Blue) | 97.21% (**+5.85 pp**, +0.712 Blue) | 98.02% (**+6.66 pp**, +0.838 Blue) |
| **Expert: S1–S2** | 100.0% (6.495 Blue) | 100.0% (+0.00 pp, **+0.090 Blue**) | 100.0% (+0.00 pp, **+0.770 Blue**) | 100.0% (+0.00 pp, **+1.004 Blue**) |
| **Expert: S3–S4** | 100.0% (5.761 Blue) | 100.0% (+0.00 pp, **+0.248 Blue**) | 100.0% (+0.00 pp, **+0.360 Blue**) | 100.0% (+0.00 pp, **+0.825 Blue**) |
| **Expert: Overall** | 100.0% (6.128 Blue) | 100.0% (+0.00 pp, **+0.169 Blue**) | 100.0% (+0.00 pp, **+0.565 Blue**) | 100.0% (+0.00 pp, **+0.915 Blue**) |

### Key Mechanics Insights
- **Tactical Slide Is a Free Second Attack Every Turn**: In `greedy_all`, players execute **1.063 slides/game** (in **70.29%** of games), generating **0.906 additional flips/game** on top of **4.101 deploy flips/game** (**5.007 total flips/game**). In `expert_margin`, slides are used **1.915 times/game** on Stages 3–4 (**92.9%** of games), generating **1.583 slide flips/game**.
- **Super-Additive Synergy on Stages 3–4**: Under `expert` on Stages 3–4, Dice alone adds `+0.248 Blue` and Slide alone adds `+0.360 Blue` (`sum = +0.608`), but having **both** adds **`+0.825 Blue`** because sliding a unit into a newly boosted column dynamically upgrades its stats (`getCardEffectiveStats(cell.cardId, c, false)` at `L1694`) and triggers immediate captures at `+1` power.
- **Starting Dice `[4, 2, 5]` Make Nudge Refills Redundant**: Because Columns 1 and 3 start at `4` and `5` (already boosted) and Column 2 starts at `2` (requiring exactly the `2` starting nudges to reach `4`), all 3 columns can be permanently boosted on Turn 1 step 1. The `+1` nudge refill per boss turn (`L1803`) and the 2 `Roll All 3D Dice` charges (`L1552`) are completely unused by optimal play.

---

## 5. Per-Card Win, Capture & Unused Rates (`perCard`)

*(Source: `perCard` in [`results/summary.json`](results/summary.json); `N = 10,000` games per policy, each hero dealt in ~6,250 games (`5/8`), each enemy pre-placed as opener in ~1,250 games (`1/8`).)*

### 5.1 Player Heroes (`PLAYER_HEROES`)

| Hero Card (`id`) | NESW (Sum) | `random` Win% (Δ) | `greedy` Win% (Δ) | `greedy_all` Win% (Δ) | `greedy` S3–4 Win% | `greedy` Unused % | `greedy` Deploy Flips/Play | `expert` Mean Blue When Dealt |
|---|---|---|---|---|---|---|---|---|
| **Sun Arbiter** (`h_arbiter`) | `[7,7,8,8]` (**30**) | **56.36%** (+1.84) | **92.84%** (+1.48) | **98.75%** (+0.73) | **87.21%** | 21.86% | **1.069** | 7.080 |
| **Lunar Oracle** (`h_oracle`) | `[7,7,8,7]` (**29**) | 55.40% (+0.88) | **92.35%** (+0.99) | 98.41% (+0.39) | **86.38%** | 26.86% | 0.992 | 7.078 |
| **Astral Seraph** (`h_seraph`) | `[8,6,7,8]` (**29**) | **55.93%** (+1.41) | 91.95% (+0.59) | 98.38% (+0.36) | 85.15% | **13.03%** | 1.050 | **7.108** |
| **Chronos Weaver** (`h_chronos`) | `[6,8,7,7]` (**28**) | 54.05% (-0.47) | 91.45% (+0.09) | 98.27% (+0.25) | 84.52% | **30.27%** | 0.962 | 7.058 |
| **Solar Archangel** (`h_archangel`) | `[8,7,6,7]` (**28**) | 54.87% (+0.35) | 91.33% (-0.03) | 98.06% (+0.04) | 84.19% | 17.59% | 1.003 | 7.088 |
| **Kai Crimson Visor** (`h_kai`) | `[7,8,6,7]` (**28**) | 54.35% (-0.17) | 90.80% (-0.56) | 97.92% (-0.10) | 83.22% | 21.85% | 0.992 | 7.041 |
| **Phoenix Valkyrie** (`h_phoenix`) | `[9,8,5,6]` (**28**) | 52.86% (-1.66) | 90.54% (-0.82) | 97.28% (-0.74) | 83.33% | 19.42% | 1.007 | 6.856 |
| **Sky-Wing Striker** (`h_valkyrie`) | `[8,8,5,6]` (**27**) | **52.34%** (-2.18) | **90.25%** (-1.11) | **97.09%** (-0.93) | **82.78%** | 19.89% | 1.004 | **7.029** |

- **Top vs Bottom Hero Spread**: Dealing `h_arbiter` (`[7,7,8,8]`) vs `h_valkyrie` (`[8,8,5,6]`) shifts win rate by **+4.02 pp** under `random` (`56.36%` vs `52.34%`), **+4.43 pp** under `greedy` on Stages 3–4 (`87.21%` vs `82.78%`), and **+1.66 pp** under `greedy_all` (`98.75%` vs `97.09%`).
- **Why Glass-Cannon Heroes (`h_phoenix`, `h_valkyrie`) Underperform**: Although `h_phoenix` (`[9,8,5,6]`) has `N=9, E=8`, its exposed `S=5, W=6` edges are easily counter-captured by the boss on the following turn (`expert` `meanBlueWhenDealt = 6.856` for `h_phoenix` vs `7.108` for `h_seraph`).

### 5.2 Enemy Mechs (`ENEMY_MECHS`) — Opener Threat & Boss Flip Rate

| Enemy Card (`id`) | NESW (Sum) | `greedy` Player Win% When Opener | `greedy` S3–4 Win% When Opener | `greedy_all` S3–4 Win% When Opener | `greedy` Boss Flips/Deploy (S3–4) | `expert` Mean Blue When Opener |
|---|---|---|---|---|---|---|
| **Emerald Colossus** (`e_colossus`) | `[6,8,5,6]` (**25**) | **86.73%** (Hardest) | **77.38%** | **93.81%** | 0.536 (0.629) | **6.933** (Hardest) |
| **Bastion Dreadnought** (`e_titan`) | `[7,5,7,6]` (**25**) | **88.14%** | **77.71%** | 95.33% | 0.574 (0.659) | 7.109 |
| **Eclipse Void Blade** (`e_eclipse`) | `[6,6,5,6]` (**23**) | 91.38% | 85.54% | 96.45% | **0.367 (0.462)** | 6.993 |
| **Cyber Shinobi** (`e_shinobi`) | `[7,6,6,5]` (**24**) | 91.66% | 84.75% | 96.26% | 0.559 (0.634) | 7.038 |
| **Cryo Interceptor** (`e_cryo`) | `[5,7,6,7]` (**25**) | 92.00% | 84.97% | 96.32% | 0.558 (0.634) | 7.031 |
| **Inferno Seraph** (`e_inferno`) | `[7,7,5,6]` (**25**) | 92.21% | 85.40% | 96.22% | **0.697 (0.779)** | 7.087 |
| **Prism Core Archon** (`e_archon`) | `[7,6,6,5]` (**24**) | 92.46% | 86.70% | 96.60% | 0.557 (0.621) | 7.009 |
| **Sigil Wraith** (`e_reaper`) | `[6,7,7,5]` (**25**) | **96.64%** (Easiest) | **93.68%** | **98.27%** | 0.460 (0.548) | **7.140** (Easiest) |

- **Opener Position `(0,1)` Creates a 16.3 pp Difficulty Swing on Stages 3–4**: Because the boss opener is always placed at top-center `(0,1)`, its exposed **West, South, and East** edges determine Turn 1:
  - When **`e_colossus`** (`[6,8,5,6]`, boosted to `[7,9,6,7]` on S3–4) opens at `(0,1)`, its East edge is `9` (impossible to beat from `(0,2)`) and its West edge is `7` (requiring an `8+` East edge from `(0,0)`). `greedy` win rate on S3–4 drops to **77.38%**.
  - When **`e_reaper`** (`[6,7,7,5]`, boosted to `[7,8,8,6]` on S3–4) opens at `(0,1)`, its West edge is only `6` (`5` on S1–2), which **every hero in the game** beats from boosted Column 1 `(0,0)`. `greedy` win rate on S3–4 jumps to **93.68%** (+16.30 pp!).
- **Strongest Mid-Game Boss Attacker**: When deployed from `aiPool`, **`e_inferno`** (`[7,7,5,6]`) averages the highest boss captures per deploy (**0.697 flips/deploy overall, 0.779 on S3–4**) because the boss tie-breaker favors top/left slots where `N=7, E=7` attack downward and rightward.

---

## 6. First-Move Spatial Heatmap (`firstMoveHeatmap`)

*(Source: `firstMoveHeatmap` in [`results/summary.json`](results/summary.json); cell `(0,1)` is pre-occupied by the boss opener.)*

### 6.1 Player First-Deploy Heatmap (Share % / Win % / Mean Blue)

| Board Cell `(r, c)` | `random` Share / Win% (Blue) | `greedy` Share / Win% (Blue) | `greedy_all` Share / Win% (Blue) | `lookahead` Share / Win% (Blue) | `expert` Share / Win% (Blue) |
|---|---|---|---|---|---|
| **`(0,0)` Top-Left** *(Col 1 Boosted, W of Opener)* | 12.41% / 61.56% (4.77) | **42.36%** / 91.55% (5.89) | **42.36%** / 97.92% (6.69) | **49.64%** / 100% (7.58) | **95.99%** / 100% (7.06) |
| **`(0,1)` Top-Mid** *(Boss Opener)* | 0.00% (Occupied) | 0.00% (Occupied) | 0.00% (Occupied) | 0.00% (Occupied) | 0.00% (Occupied) |
| **`(0,2)` Top-Right** *(Col 3 Boosted, E of Opener)* | 12.42% / 48.95% (4.45) | **27.11%** / 89.71% (5.78) | **27.11%** / 97.60% (6.65) | 0.66% / 100% (7.21) | 0.00% / — |
| **`(1,0)` Mid-Left** *(Col 1 Boosted, Non-adj)* | 13.03% / **40.37%** (4.17) | 0.00% / — | 0.00% / — | 0.00% / — | 0.00% / — |
| **`(1,1)` Center** *(Col 2 Unboosted → Boosted, S of Opener)* | 12.32% / 55.52% (4.61) | **30.53%** / **92.56%** (5.96) | **30.53%** / **98.53%** (6.82) | **49.70%** / 100% (7.72) | **4.01%** / 100% (6.62) |
| **`(1,2)` Mid-Right** *(Col 3 Boosted, Non-adj)* | 12.52% / 50.08% (4.45) | 0.00% / — | 0.00% / — | 0.00% / — | 0.00% / — |
| **`(2,0)` Bot-Left** *(Col 1 Boosted, Corner)* | 13.01% / **65.10%** (4.87) | 0.00% / — | 0.00% / — | 0.00% / — | 0.00% / — |
| **`(2,1)` Bot-Mid** *(Col 2 Unboosted)* | 12.04% / 54.65% (4.55) | 0.00% / — | 0.00% / — | 0.00% / — | 0.00% / — |
| **`(2,2)` Bot-Right** *(Col 3 Boosted, Corner)* | 12.25% / 60.24% (4.73) | 0.00% / — | 0.00% / — | 0.00% / — | 0.00% / — |

### 6.2 Boss First-Reply Heatmap (`bossFirstReply`)

| Board Cell `(r, c)` | `random` Boss Reply Share (Mean Flips) | `greedy` Boss Reply Share (Mean Flips) | `lookahead` Boss Reply Share (Mean Flips) | `expert` Boss Reply Share (Mean Flips) |
|---|---|---|---|---|
| **`(0,0)` Top-Left** | **63.90%** (0.162 flips) | **41.02%** (0.809 flips) | **50.36%** (0.398 flips) | 1.95% (0.277 flips) |
| **`(0,2)` Top-Right** | 6.50% (0.285 flips) | 18.89% (0.278 flips) | 38.85% (0.280 flips) | **39.27%** (0.332 flips) |
| **`(1,0)` Mid-Left** | 4.81% (1.000 flips) | 13.19% (1.000 flips) | 4.83% (1.000 flips) | **30.46%** (1.000 flips) |
| **`(1,1)` Center** | 8.15% (1.000 flips) | 19.15% (1.000 flips) | 5.96% (1.000 flips) | **26.26%** (1.000 flips) |
| **All Row 2 Cells `(2,*)`** | 13.88% (1.000 flips) | 6.31% (1.000 flips) | 0.00% | 2.06% (1.000 flips) |

- **Why `(0,0)` and `(1,1)` Dominate Opening Theory**:
  - Every `greedy`, `lookahead`, and `expert` opening immediately captures the boss opener at `(0,1)` (`meanImmediateFlips = 1.000` in 100% of games) by playing into one of its three neighbours: `(0,0)`, `(1,1)`, or `(0,2)`.
  - Under `random`, playing into `(1,0)` has the worst win rate on the board (**40.37% overall, 22.12% on S3–4**) because it does not capture `(0,1)` AND exposes the player card's North edge to an immediate deterministic boss capture at `(0,0)`!
  - Because of the boss row-major tie-break bug (`R02`), whenever the boss has `0` captures available on Turn 1, it **always** places at `(0,0)` if open (**63.90%** of `random` games, **50.36%** of `lookahead` games), or `(0,2)` if `(0,0)` is taken (**39.27%** of `expert` games).

---

## 7. Hand Deal Variance Across All $\binom{8}{5} = 56$ Hero Hands (`handDealVariance`)

*(Source: `handDealVariance` in [`results/summary.json`](results/summary.json).)*

Because 5 distinct heroes are dealt from 8 (`C(8,5) = 56` possible hands), the total base stat sum of the 5-card hand ranges from **139** (`{h_archangel, h_phoenix, h_chronos, h_kai, h_valkyrie}`) to **144** (6 hands containing `h_arbiter + h_oracle + h_seraph` plus two `28`-sum heroes):

| Hand Stat Sum (`edgeSum`) | Distinct Hands | Games (`N/10k`) | `random` Overall Win% | `random` S3–4 Win% | `greedy` S3–4 Win% | `greedy_all` S3–4 Win% | `expert` Overall Win% (Mean Blue) |
|---|---|---|---|---|---|---|---|
| **139** (Min) | 1 | 183 | 45.90% | **18.92%** | 82.43% | 91.89% | **100.0%** (6.913) |
| **140** | 8 | 1,409 | 47.91% | 28.67% | 77.56% | 93.35% | **100.0%** (6.867) |
| **141** | 12 | 2,197 | 52.34% | 34.18% | 79.42% | 94.83% | **100.0%** (6.998) |
| **142** | 17 | 3,022 | 54.77% | 36.06% | 86.29% | 96.47% | **100.0%** (7.045) |
| **143** | 12 | 2,138 | 57.86% | 39.51% | 88.58% | 97.66% | **100.0%** (7.135) |
| **144** (Max) | 6 | 1,051 | **61.94%** | **46.79%** | **91.13%** | **98.87%** | **100.0%** (7.201) |
| **56-Hand Spread (`Min → Max`)** | **56** | **10,000** | **42.08% → 67.03%** (`SD 6.06%`) | **18.92% → 55.68%** (`SD 7.51%`) | **71.58% → 95.60%** (`SD 5.98%`) | **90.20% → 100.0%** (`SD 2.66%`) | **100.0% → 100.0%** (`Blue 6.32 → 7.72`) |

- For heuristic players (`greedy` on Stages 3–4), hand deal luck causes a **24.02 pp win-rate swing** (`71.58%` with `{h_oracle, h_chronos, h_seraph, h_kai, h_valkyrie}` vs `95.60%` with `{h_archangel, h_oracle, h_seraph, h_kai, h_arbiter}`).
- Adding Tactical Slide + Dice (`greedy_all`) compresses that 56-hand SD on Stages 3–4 from **5.98 pp down to 2.66 pp** (`90.20% → 100.0%`), and `expert` eliminates win-rate variance completely (**100.0%** on all 56 hands).

---

## 8. What-If Rule & Balance Variants (`variants`)

We re-simulated 8 rule modifications (`N = 2,500` games per policy-stage cell, **210,000 variant games** total) using the **exact same seed streams** as the baseline (`seedBase = 1,000,000 * (stage + 1)`):

| Variant Key | Rule Change vs Shipped Baseline | Stage | `random` Win% (Δ) | `greedy` Win% (Δ) | `greedy_slide` Win% (Δ) | `greedy_all` Win% (Δ) | `lookahead` Win% (Δ) | `expert` Win% (Mean Blue, Δ) | Skill Gap (`Expert − Greedy`) |
|---|---|---|---|---|---|---|---|---|---|
| **`base`** *(Shipped)* | `startDice=[4,2,5]`, `aiBonus=0/1`, `slideCanCapture=true` | **S1** | 72.80% | 98.40% | 99.80% | 99.88% | 100.0% | 100.0% (7.498) | +1.60 pp |
| **`base`** *(Shipped)* | Same (`aiBonus=1` on Stage 3) | **S3** | 36.20% | 84.60% | 94.56% | 96.08% | 100.0% | 100.0% (6.598) | +15.40 pp |
| **`bossTieRandom`** | Fix `R02`: boss breaks capture ties uniformly at random | **S1** | 79.00% (+6.20) | 97.76% (-0.64) | 99.68% (-0.12) | 99.84% (-0.04) | 100.0% (0.00) | 100.0% (7.367, -0.131) | +2.24 pp |
| **`bossTieRandom`** | Fix `R02` on Stage 3 | **S3** | 41.12% (+4.92) | 84.04% (-0.56) | 94.84% (+0.28) | 96.28% (+0.20) | 100.0% (0.00) | 100.0% (6.614, +0.016) | +15.96 pp |
| **`noRefill`** | `nudgeRefill = 0` (nudges do not regenerate after boss turns) | **S1** | 72.80% (0.00) | 98.40% (0.00) | 99.80% (0.00) | 99.88% (0.00) | 100.0% (0.00) | 100.0% (7.498, 0.000) | +1.60 pp |
| **`noRefill`** | `nudgeRefill = 0` on Stage 3 | **S3** | 36.20% (0.00) | 84.60% (0.00) | 94.56% (0.00) | 96.08% (0.00) | 100.0% (0.00) | 100.0% (6.598, 0.000) | +15.40 pp |
| **`coldDice`** | `startDice = [1,2,3]` (no free boosted columns at Turn 1; 2 nudges can only boost Col 3 `3→4`) | **S1** | 50.64% (**-22.16**) | 92.80% (-5.60) | 98.56% (-1.24) | 99.32% (-0.56) | 100.0% (0.00) | 100.0% (7.357, -0.141) | +7.20 pp |
| **`coldDice`** | `startDice = [1,2,3]` on Stage 3 | **S3** | 10.36% (**-25.84**) | 55.80% (**-28.80**) | 76.48% (-18.08) | 88.88% (-7.20) | 100.0% (0.00) | 100.0% (6.372, -0.226) | **+44.20 pp** |
| **`slideNoCapture`** | `slideCanCapture = false` (Tactical Slide repositions only; no flips on slide) | **S1** | 72.80% (0.00) | 98.40% (0.00) | 99.28% (-0.52) | 99.36% (-0.52) | 100.0% (0.00) | 100.0% (6.624, -0.874) | +1.60 pp |
| **`slideNoCapture`** | `slideCanCapture = false` on Stage 3 | **S3** | 36.20% (0.00) | 84.60% (0.00) | 91.08% (-3.48) | 93.20% (-2.88) | **99.96%** (-0.04) | 100.0% (6.148, -0.450) | +15.40 pp |
| **`noSlide`** | `slideEnabled = false` (remove Tactical Slide completely) | **S1** | 72.80% (0.00) | 98.40% (0.00) | 98.40% (-1.40) | 98.80% (-1.08) | 100.0% (0.00) | 100.0% (6.594, -0.904) | +1.60 pp |
| **`noSlide`** | `slideEnabled = false` on Stage 3 | **S3** | 36.20% (0.00) | 84.60% (0.00) | 84.60% (-9.96) | 88.96% (-7.12) | **99.72%** (-0.28) | 100.0% (6.017, -0.581) | +15.40 pp |
| **`aiBonus2`** | Boss gets `aiBonus = +2` (clamped at 9) | **S1** | **5.60%** (-67.20) | **37.48%** (-60.92) | 56.72% (-43.08) | 65.16% (-34.72) | **98.56%** (-1.44) | 100.0% (5.570, -1.928) | **+62.52 pp** |
| **`aiBonus3`** | Boss gets `aiBonus = +3` (clamped at 9) | **S1** | **0.52%** (-72.28) | **11.28%** (-87.12) | 30.40% (-69.40) | 39.48% (-60.40) | **80.12%** (-19.88) | **99.68%** (5.152, -2.346) | **+88.40 pp** |
| **`tuned`** *(Proposed)* | `startDice = [1,2,3]` + `slideCanCapture = false` | **S1** | 50.64% (-22.16) | 92.80% (-5.60) | 96.16% (-3.64) | 97.72% (-2.16) | 100.0% (0.00) | 100.0% (6.513, -0.985) | +7.20 pp |
| **`tuned`** *(Proposed)* | `startDice = [1,2,3]` + `slideCanCapture = false` on Stage 3 | **S3** | **10.36%** (-25.84) | **55.80%** (-28.80) | **69.84%** (-24.72) | **85.04%** (-11.04) | **99.88%** (-0.12) | **100.0%** (5.963, -0.635) | **+44.20 pp** |

---

## 9. Actionable Balance Recommendations

1. **Adopt the `tuned` Package (`startDice = [1, 2, 3]` + `slideCanCapture = false`) with a Graduated 4-Stage `aiBonus` Ramp (`[0, 1, 1, 2]`)**:
   - **Why `startDice = [1, 2, 3]` (`coldDice`) works**: Starting with unboosted dice (`[1, 2, 3]`) immediately makes **both** Dice Nudges and Rerolls meaningful. On Stage 3 (`aiBonus = 1`), `greedy` (no dice) wins only **55.80%**, `greedy_slide` (repositioning slide only) wins **69.84%**, `greedy_all` (using dice nudges/rerolls + repositioning slide) climbs to **85.04%** (**+15.20 pp marginal value from Dice!**), while `lookahead` (**99.88%**) and `expert` (**100.0%**) still reward multi-turn planning without creating unwinnable seeds.
   - **Why `slideCanCapture = false` works**: Allowing Tactical Slide to reposition a unit to safety or open a key socket—without granting a free second capture phase every turn—eliminates the `+1.28 flips/game` snowball while preserving a **+14.04 pp** tactical benefit for sliding on Stage 3 (`55.80% → 69.84%`).
2. **Differentiate All 4 Stages (`aiBonus: [0, 0, 1, 1] → [0, 1, 1, 2]` + Guaranteed Boss Opener)**:
   - Currently Stage 1 = Stage 2 (`aiBonus = 0`) and Stage 3 = Stage 4 (`aiBonus = 1`), and `STAGES[idx].bossId` is not even guaranteed to appear in the match.
   - Pre-placing `STAGES[idx].bossId` at `(0,1)` as the mandatory stage opener gives each stage a distinct opening puzzle, and setting Stage 4 to `aiBonus = 2` creates a true boss climax where myopic `greedy_all` wins **65.16%**, `lookahead` wins **98.56%**, and `expert` wins **100.0%**.
3. **Eliminate Strict Dominance & Duplicate Enemy Stat Lines**:
   - Buff `h_valkyrie` (`[8,8,5,6] → [8,8,6,6]`) so it is no longer strictly dominated by `h_phoenix` (`[9,8,5,6]`).
   - Differentiate `h_oracle` (`[7,7,8,7] → [7,8,8,6]`) from `h_arbiter` (`[7,7,8,8]`), and differentiate `e_shinobi` (`[7,6,6,5] → [7,5,6,6]`) from `e_archon` (`[7,6,6,5]`).
   - Reallocate `h_phoenix.N = 9` (`[9,8,5,6] → [8,8,6,6]` or `[8,8,5,7]`) so column boosts (`Math.min(9, v+1)`) are not wasted on its North edge, and cap `e_colossus.E` at `7` base (`8` boosted) so it does not become an uncapturable `9` on `aiBonus >= 1` stages.
