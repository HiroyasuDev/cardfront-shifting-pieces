# CARDFRONT Benchmark: How It Compares to Established Tactical Card/Grid Games

**Workstream:** `benchmark` · **Author:** browser-operator subagent · **Date:** 2026-11-08
**Target (read-only):** `WebPlayable/cardfront_cradle_of_echoes_playable.html` (sha256 `6703e34c…dd55`, 2668 lines at 02:11 local. The file changed by 1 line while this work was running, so line refs are approximate and **symbol names are authoritative**.)

## 0. Method & integrity notes

- **External facts:** every one comes from a page that was actually fetched; IDs `[S#]` map to URLs in §6. Search-engine summaries were used only to find pages. A claim that rests only on a search summary is marked **UNVERIFIED**.
- **Prompt-injection screening:**
  - `jev_screen` could not run because no TypeSafe/OpenRouter key is configured.
  - Fallback, step 1: a regex pre-screen of all 50+ fetched outputs for agent-directed phrases ("ignore previous", "system prompt", "you are an AI", etc.). It got **0 hits on web content**.
  - Fallback, step 2: two local `mlx_jev_judge` (Qwen2.5-3B 4-bit) passes over the excerpts relied on here.
    - Batch 1 (FF wikis/guides, Queen's Blood press): **not injection, p=0.96**.
    - Batch 2 (Snap/Gwent/ITB/Wikipedia): **inconclusive, 0.51/0.49**, so it counts as `review`. I inspected it by hand: no attempts to redirect tool use, obtain credentials, or override rules. The nearest trigger is the Gwent dev letter's phrasing "We heard you — we will fix the coin flip". All content was treated as data only.
- **Blocked sources:** Fandom wikis (`finalfantasy.fandom.com`) refuse automated fetching via robots.txt (403), and I respected that. GameSpot returned 403. Washington Post timed out.
- **CARDFRONT numbers:** all come from [`structural_sim.js`](structural_sim.js) → [`structural_sim_output.json`](structural_sim_output.json) (N=20,000 games per cell). The script is a headless copy of the game's logic: `findCaptures`, `executeBossTurn` and `checkGameOver` are reproduced as-is, and card data is extracted from the HTML.
  - Not modelled: Tactical Slide, nudges and rerolls. Dice are fixed at the `startStage` default `[4,2,5]`.
  - Those three mechanics only help the player, so the win rates below are a **lower bound for player strength**.
- "Score x/5" values in the rubric are **analyst judgment**, not measurements.

---

## 1. CARDFRONT's actual rules (verified against code)

| Aspect | Code fact | Where |
|---|---|---|
| Board | 3×3. The boss pre-places 1 random enemy at (row 0, col 1) | `startStage` |
| Player hand | 5 heroes drawn at random from 8 (`shuffle(PLAYER_HEROES).slice(0,5)`). No choice, no draw | `startStage` |
| Boss pool | 5 of the remaining 7 shuffled enemies, popped from the end. **Hidden**: `aiPool` is never rendered | `startStage`, `executeBossTurn` |
| Stage identity | `STAGES[i].bossId` is used only for the name/label. The boss's own card is **not** guaranteed to appear; the only mechanical difference between stages is `aiBonus` 0/0/1/1 | `startStage`, `getCardEffectiveStats` |
| Capture | Strictly greater facing edge (NESW). No Same/Plus/Combo. Ties do nothing | `findCaptures` |
| Column dice | Column die ≥4 gives **player** cards +1 on all sides (cap 9). The boss is never affected by dice | `isColBoosted`, `getCardEffectiveStats` |
| Dice tools | Nudge: 2, +1 refill per boss turn, cap 3. Steps the die 1→…→6→1 (a nudge on a 6 *drops* to 1). Reroll: 2, randomizes all dice | `nudgeColDie`, `rerollAllDice`, `executeBossTurn` |
| Tactical Slide | 1 per turn. Moves an own card to an adjacent empty tile and can capture. **Does not end the turn and does not use a card** | `handleSlotClick` |
| Boss AI | Picks the slot with the most flips (1-ply greedy). **The tie-break is not random**: `bestCount=-1` means the random initial `bestSlot` is always overwritten by the first maximum in reading order | `executeBossTurn` |
| End / win | Ends when the board is full or the hand is empty. Win iff `blue > red`. Only board cards count | `checkGameOver` |
| "Telegraphs" | `triggerAllBoardTelegraphs` paints alternating strike/ally zones (`i % 2`). This is **cosmetic** and does not show what the boss intends | `triggerAllBoardTelegraphs` |
| Juice | 80 ms hit-stop and trauma shake scaled by flips. Tones on every action | `handleSlotClick`, `triggerHitStop`, `addTrauma` |

**Structural measurements** (`structural_sim_output.json`):

- **Card power is lopsided.** Hero edge totals average **28.375**; enemy totals average **24.5**. Edges are compressed into the 5–9 range.
- **Edge-vs-edge odds.** For a random hero edge against a random enemy edge:

  | Matchup | Hero edge wins | Tie |
  |---|---|---|
  | No boost, aiBonus 0 | **65.7%** | 22.0% |
  | With column boost, aiBonus 0 | **87.7%** | |
  | No boost, aiBonus 1 | **35.0%** | 30.8% |

  An enemy edge beats a hero edge only **12.3%** of the time at aiBonus 0, and **34.3%** at aiBonus 1.
- **Placements are fixed.** Every simulated game ends with the player having placed **4** cards and the boss **5** (including the pre-placed one), with **1** hero left unused in hand. The player starts at 4 vs 5 on board and needs net +1 captures just to win.
- **Decisions per turn.** The player has 20 legal moves per turn on average (5×8, 4×6, 3×4, 2×2). A capture is available on **96–98%** of player turns (no capture available: 2.0–7.4%).

| Player policy (no dice/slide) | aiBonus 0 (stages 1–2) win rate | aiBonus 1 (stages 3–4) win rate | Mean blue cards /9 (bonus 0 → 1) |
|---|---|---|---|
| Random legal moves | **72.9%** | **34.3%** | 5.05 → 4.08 |
| 1-ply greedy (max flips) | **98.4%** | **83.6%** | 6.32 → 5.42 |

**Counterfactual: if FF8's Same/Plus rules were added**, they would fire on **7.4–10.5%** of player placements. Plus would do almost all of the work (6.7–8.8%) and Same would fire on 0.3–2.9%.

---

## 2. Reference games (sourced fact sheets)

### 2.1 Triple Triad (FF8, 1999; also FFXIV)
- **Board / hand:**
  - 3×3 grid; each player brings 5 cards [S1][S2].
  - Edge ranks run 1–10, with "A" meaning 10 [S2].
  - In FF8 the player picks their 5 from a collection [S3].
- **Turns:** a **coin flip / random draw decides who starts** [S1][S2]; then one card per turn, alternating [S2].
- **Capture:** the placed card's facing rank must be **higher** than the neighbour's facing rank [S1][S2].
  - Wikipedia's "matching or exceeding" [S3] contradicts both rule sources, so it is treated as an error.
- **Card-count parity:** "The player who goes second will have a card remaining in their hand and that card will count towards their ending score". The majority of all **10** cards wins, and draws are possible [S2]. FFXIV states the same: "the unplaced 10th card is also counted" [S1].
- **Rule modifiers** (regional in FF8, per-NPC/regional in FFXIV) [S1][S2]:
  - **Open** (all hands visible) and **Three Open** (3 random cards visible).
  - **Same:** ≥2 sides with equal numbers flip; at least one matched card must be the opponent's.
  - **Same Wall:** board edges count as A for Same.
  - **Plus:** ≥2 sides with equal sums flip.
  - **Combo:** cards flipped by Same/Plus then chain-capture weaker neighbours.
  - **Elemental:** random tiles; a matching element gives +1, a mismatch −1. Same/Plus ignore this.
  - **Random** (random 5 from collection), **Sudden Death** (on a draw, replay using the cards each side currently controls; FFXIV caps it at 5 consecutive replays).
  - **FFXIV only:** Order, Chaos, Reverse, Fallen Ace, Ascension/Descension, Swap, Roulette, Draft.
- **Randomness:** who starts, Elemental tiles, Random/Chaos/Swap/Roulette rules, and rule spreading between regions in FF8 [S1][S2].
- **Match length:** 9 placements (5+4) [S1]. Wall-clock time **UNVERIFIED**.
- **Known issues and fixes:**
  - The going-first imbalance is handled by **counting the leftover hand card**, plus a random first player [S1][S2].
  - Draws are handled by Sudden Death [S1][S2].
  - Depth on a tiny board comes from **rule modifiers**, not from a bigger board [S1][S2].
  - Reception: "pretty tactical" and widely loved [S3]. Designed as a diegetic pastime inspired by *Magic: The Gathering* [S3][S4].

### 2.2 Queen's Blood (FF7 Rebirth, 2024)
- **Board:** 3 lanes × 5 tiles; players work in from the left and right edges [S6][S7][S9].
- **Deck / hand:** 15-card deck [S7][S8]. Mulligan any number of cards at the start [S6][S8]. Cards are drawn on later turns (inferred from IGN's tips [S7]). Starting hand of 5 is **UNVERIFIED**.
- **Turns:** play one card or pass. The game ends when **both players pass in succession** [S6]. In the main game **the player always starts**, and passing to go second is a recommended reactive tactic [S8].
- **Placement / capture:** you can only play on tiles you own whose pawn rank is ≥ the card's rank [S6][S8].
  - A card's pattern adds pawns (raising rank) and **takes over empty enemy tiles** it overlaps [S6][S9].
  - Abilities: enhance, enfeeble (a card is destroyed at 0 power), and replacement cards [S6][S8].
- **Scoring:** sum of card power per lane; **only the lane winner's points count** [S6][S8]. The total wins, not the number of lanes won [S7].
- **Randomness:** deck draws only. Mulligan softens it [S6].
- **Match length:** "matches were quick" (Eurogamer via [S11]). Exact duration **UNVERIFIED**.
- **Balance notes:**
  - The director says *Marvel Snap*'s rules were "a helpful reference … to adjust the balance" [S10].
  - The team spent about a year prototyping on paper and in a simple Windows app before implementing [S10].
  - Reviewers call the starter deck "very balanced" [S7][S8].

### 2.3 Tetra Master (FF9, 2000)
- **Board:** 4×4, with **up to 6 tiles blocked at random** [S5].
- **Hand:** 5 cards chosen from inventory; 10 cards played in total [S5].
- **Turns:** a **coin flip decides who lays the first card** [S5].
- **Capture:**
  - Up to 8 arrows per card. An arrow into a neighbour with no arrow back captures it outright [S5].
  - If the neighbour points back, a **battle** happens: each side's stat becomes a random value between 0 and its base. Any card can beat any card [S5].
  - Combos happen only after battles and are first-degree only [S5].
- **Randomness:** blocked tiles, battle rolls, card type upgrades [S5].
- **Known issue:** the battle RNG is notoriously opaque. The guide author jokes it "will make you a nihilist" [S5]. It is a cautionary contrast to Triple Triad's deterministic captures.

### 2.4 Marvel Snap (2022)
- **Board / deck:** 3 locations, assigned at random and revealed one per turn over turns 1–3, each with a unique effect. 12-card deck [S12].
- **Turns:** **simultaneous** face-down play. Energy starts at 1 and grows by 1 per turn. 6 rounds; win 2 of 3 locations [S12].
- **Reveal order ("priority"):** the player winning more locations reveals first. Ties go to higher total power, then to a coin flip. Turn 1 is always a coin flip [S13].
- **Stakes:** a "Snap" doubles the cube stakes and the opponent may retreat. Stakes also double automatically on the final turn [S12].
- **Randomness:** locations, draws [S12].
- **Session length:** "individual games typically last a few minutes" [S12]. A "~3 min" figure is **UNVERIFIED**.
- **Balance:** first-mover advantage is removed by **simultaneous turns**, and reveal order is a dynamic, readable rule [S12][S13]. Depth comes from bluffing and stakes rather than complex mechanics [S12].

### 2.5 Gwent (Witcher 3 → standalone 2018)
- **Board:** 2 rows per side (Melee, Ranged) in standalone [S14].
- **Deck / hand:** 10-card hand drawn from a 25+ card deck [S14].
- **Turns:** one card per turn, best of 3 rounds. A round ends when both pass or both run out of cards [S14].
- **Scoring:** highest board power wins the round [S14].
- **Known issue (official):** "going second can give players a significant advantage … we will 'fix the coin flip'" — CDPR's Homecoming letter [S15].
  - Fix: a **Tactical Advantage** card, "Order: Boost an allied unit by 5". Its flavour text: "He who first draws his blade has the advantage" [S16].
  - That it is granted specifically to the first player is **UNVERIFIED** beyond the flavour text and community posts.
- **Other lesson:** CDPR cut the random "Create" mechanic because "wide RNG is not something that fits our focus on player skill" [S15].
- **Late-life problem:** power creep with no rotation system [S14].

### 2.6 Into the Breach (2018)
- **Board / turns:** 8×8 field. The player controls 3 mechs with a fixed turn limit per map [S17].
- **Telegraphing:** enemies show their intended attack direction before the player moves [S17][S18].
- **Design principles:**
  - "you always know exactly what the bugs are going to attack next" [S18].
  - "we would **sacrifice cool ideas for the sake of clarity every time**" [S18][S19].
  - Only 3 attack shapes, and pushes are at most 1 tile, for readability [S18].
  - Animated tooltips were called "the most important decision we made" [S18][S19].
  - Telegraphs plus a turn limit keep battles short [S17].
- **Randomness:** procedurally chosen scenarios and spawns [S17]. Per-turn outcomes are deterministic once telegraphed [S18].

### 2.7 Dicey Dungeons (2019)
- **Structure:** turn-based fights. Each turn you get a **random roll of your dice** and **allocate** them into equipment slots, some with constraints (odd/even, ≤ / ≥). Some items alter or reuse dice [S20].
- **Lesson:** dice are a *resource you place*, not a modifier you wait on. Enemies follow the same rules [S20].
- Match length **UNVERIFIED**.

### 2.8 Metal Gear Acid (2004)
- **Hand:** up to 6 cards; deck size grows with progress [S21].
- **Card use:** a card is played either for its effect or as movement (usually 3 squares) [S21].
- **Turn order:** each card's **cost** decides when the character next acts: higher cost means a longer wait [S21].
- **Lesson:** tempo is a cost, so turn order can't be farmed for free.
- Board size and match length **UNVERIFIED**.

### 2.9 Inscryption (2021)
- **Board:** 3×4 grid (3×5 in Act III) [S22].
- **Telegraphing:** the opponent **plays cards ahead of time into a visible back row**; they advance the following turn [S22].
- **Combat:** cards attack the opposing card in the same column. Damage tips a scale, and a 5-tooth lead wins [S22].
- **Costs:** blood sacrifice, bones, energy, or gems [S22].
- **Run structure:** a roguelike map between fights, with deck add/remove nodes [S22].
- Who goes first and match length **UNVERIFIED**.

---

## 3. (a) Comparison table vs CARDFRONT

| Game | Board | Hand / deck | Turn structure | Capture / scoring | Randomness | Match length | First-player / parity handling |
|---|---|---|---|---|---|---|---|
| **CARDFRONT** | 3×3; 1 pre-placed enemy | 5 random of 8 heroes; boss 5 hidden | Alternating; player always first; free Slide + dice tools | Strict `>` edge flips; most board cards of 9 | Hand deal, boss pool, rerolls; boss tie-break deterministic | 4 player placements (sim) | **Boss 5 vs player 4 board cards**; hand card not counted; no draws |
| Triple Triad | 3×3 (+Elemental tiles) | 5 chosen (or Random) | Alternating, coin flip start | Strict `>`; +Same/Plus/Combo; majority of 10 | Start, tiles, rule variants | 9 placements | **10th card counts**; draw → Sudden Death [S1][S2] |
| Queen's Blood | 3×5 lanes | 15-card deck, mulligan | Alternating; play or pass; ends on double pass | Lane-winner-takes-points | Draws | "Quick" | Player always starts, but **passing** lets you go second [S8] |
| Tetra Master | 4×4, 0–6 blocked | 5 chosen | Alternating, coin flip start | Arrows; random battles; 1-degree combo | Blocks + battle RNG (high) | 10 placements | Coin flip [S5] |
| Marvel Snap | 3 locations | 12-card deck, energy ramp | **Simultaneous**, 6 turns | Win 2 of 3 locations | Locations, draws | "A few minutes" | Reveal priority by board state; coin flip T1 [S13] |
| Gwent | 2 rows/side | 10 of 25+ | Alternating, pass, Bo3 | Round power | Draws | Multi-round | Coin flip + **Tactical Advantage** compensation [S15][S16] |
| Into the Breach | 8×8 | n/a (3 mechs) | Enemy telegraph → player acts → resolve | Objectives under turn limit | Spawns / scenarios | Short, turn-capped | Enemy intent always shown [S17][S18] |
| Dicey Dungeons | n/a | Equipment + dice | Alternating | HP race | **Dice you allocate** | UNVERIFIED | Symmetric rules [S20] |
| Metal Gear Acid | Tactical map | ≤6-card hand | Cost-based initiative | Mission goals | Draws | UNVERIFIED | Cost delays next turn [S21] |
| Inscryption | 3×4 | Run deck | Alternating; enemy **queues** cards | 5-tooth scale lead | Draws, map | UNVERIFIED | Enemy intent visible a turn ahead [S22] |

---

## 4. (b) 10-criterion heuristic rubric

Scores are analyst judgment (1 = poor, 5 = matches the best reference). The CARDFRONT evidence is cited from code or the sim.

| # | Criterion | What "good" looks like (sourced) | CARDFRONT today | Score |
|---|---|---|---|---|
| 1 | Meaningful decisions per turn | QB: "each turn is dense with decision-making" [S9]. TT rule modifiers make placement order and edges matter [S1] | 20 legal moves/turn, but a capture is available on 96–98% of turns and greedy wins 98.4% at aiBonus 0, so the right move is usually obvious. Dice/Slide add options the sim didn't model | 2 |
| 2 | Counterplay | ITB: you see the threat and disrupt it [S18]. Snap: priority and reveal order can be played around [S13] | The boss's next card is hidden and the AI is 1-ply. The player can't plan around a specific threat. The boss does not react to dice | 2 |
| 3 | Information clarity | ITB: "sacrifice cool ideas for the sake of clarity"; 3 attack shapes [S18][S19]. TT Open / Three Open [S1] | Edge numbers and flip preview (`findClashes`) are good. But the "telegraph" pulse is cosmetic (`i % 2`), the boss pool is hidden, and boost rules (player-only, nudge wraps 6→1) aren't obvious | 2.5 |
| 4 | Randomness vs skill | TT: deterministic captures with randomness pushed to setup [S1][S2]. Tetra Master's battle RNG frustrates [S5]. Gwent removed "Create" RNG [S15] | Captures are deterministic (good). Randomness sits in the deal and rerolls. But a skill-free random player still wins 72.9% at aiBonus 0, so skill hardly matters on stages 1–2 | 3 |
| 5 | Comeback potential | TT Combo chains "turn a match around" [S1]. Snap retreat limits losses [S12]. Gwent best-of-3 [S14] | No chains. One-step flips only, and the board is nearly decided by turn 3–4 | 2 |
| 6 | Session length | Snap "a few minutes" [S12]. ITB short, turn-capped battles [S17]. QB "quick" [S11] | 4 decisions per stage plus 650 ms boss delays makes stages very short. Good for mobile, but too thin unless stages chain into a run | 3.5 |
| 7 | Onboarding | ITB animated tooltips [S18]. QB tutorial plus mechanics unlocked gradually [S6][S8] | Banner hint on start, flip preview, drag or click. No staged rule unlocks | 3 |
| 8 | Collection / meta depth | TT pick 5 from a collection, plus card-to-item refinement [S3][S4]. QB 15-card deckbuilding, prebuilt decks [S7][S8]. Inscryption run-based deck edits [S22] | Fixed 8 heroes, random 5, no choice, no progression. Stage boss identity isn't used in the boss pool | 1 |
| 9 | Juice / feel | ITB's clarity-first visuals [S18]. QB cited as a polished diegetic minigame [S11] | 80 ms hit-stop, trauma shake scaled by flips, tones, 3D cards: strong for a prototype | 4 |
| 10 | Visual readability | ITB parse-at-a-glance goal [S18]. QB physical-board readability testing [S10] | Edge numbers are visible, but 5–9 compressed values and heavy art/telegraph overlays risk clutter. Needs on-device testing (other workstreams) | 3 |

---

## 5. (c) Design risks & proven fixes for CARDFRONT

1. **Solved-game risk: greedy play almost always wins (98.4% / 83.6%).**
   - Fix A: add TT's Same / Plus / Combo [S1][S2] as stage modifiers.
     - In the sim they would fire on 7.4–10.5% of placements, often enough to matter without dominating.
     - Because edges are compressed into 5–9, **Plus fires about 5–25× more often than Same**. Consider widening the edge range (TT uses 1–A) [S2] if Same should matter.
   - Fix B: make the boss 2-ply, i.e. have it penalize placements it can lose next turn.
2. **Card-count parity: 4 vs 5 board cards, board-only scoring.**
   - TT's fix is to count the unplayed card of the player who moved second (10 total) [S1][S2].
   - Options for CARDFRONT:
     - (i) remove the pre-placed card and pick the first player at random [S1][S5];
     - (ii) keep the pre-placed card but count the player's leftover hand card;
     - (iii) Gwent-style compensation, e.g. a free +1 "Tactical Advantage" token for the side that is behind on tempo [S15][S16].
   - Options (i) and (ii) make draws possible, so pair them with **Sudden Death** capped at N replays (FFXIV caps at 5) [S1].
3. **Difficulty comes only from flat stat inflation (`aiBonus`).**
   - +1 roughly halves hero edge wins (65.7% → 35.0%) and raises ties to 30.8%. That is a cliff between stage 2 and stage 3.
   - Fix: escalate with **rules** instead (Elemental tiles, Reverse, Fallen Ace, Three Open → closed hands) [S1][S2], or with Snap-style location effects [S12].
   - Hero (28.4) vs enemy (24.5) power is already lopsided, so tune per stage with modifiers rather than numbers.
4. **Fake telegraphs and hidden intent.**
   - ITB [S18] and Inscryption [S22] both show real enemy intent a turn ahead.
   - CARDFRONT's boss is deterministic (first-max in reading order), so it **can be telegraphed honestly**: show the top of `aiPool` and highlight its greedy target tile.
   - Replace the cosmetic `i % 2` pulse with this. It would directly lift rubric items 2 and 3.
5. **Dice give the player free upside with no tension.**
   - The dice only buff the player, and the 6→1 nudge wrap is a hidden trap.
   - Dicey Dungeons model [S20]: dice as an allocation resource with trade-offs.
   - Alternatives: low dice could buff the boss in that column, or each die could be spent once.
   - Avoid Tetra-Master-style opaque RNG [S5].
6. **No comeback mechanics.** Combo chains [S1], or best-of-3 stages (Gwent [S14]), would let a losing board swing.
7. **No collection or choice.**
   - Let the player pick 5 of 8 (TT [S3]) or use a Draft rule (FFXIV [S1]).
   - Chain the 4 stages into an Inscryption / Dicey-style run with deck edits between fights [S20][S22].
   - Use `bossId` so each boss's signature card is guaranteed in its pool. That gives stage identity, as with Snap locations [S12].
8. **Boss tie-break bug (P3).**
   - Repro: any boss turn with ≥2 slots tied for most flips → the AI always picks the first tied slot in reading order.
   - Expected (per the brief): a random tie-break. Observed: deterministic. Code: `executeBossTurn`, `let bestCount = -1` overwrites the random `bestSlot`.
   - Either fix it (`>=` with a random shuffle) or keep it on purpose to support honest telegraphing (risk 4).
9. **Stale stats on flipped cards (P3).**
   - `recalcBoardStats` recomputes only `owner==='player'` cells.
   - Player cards captured by the boss keep their player column boost forever.
   - Boss cards captured by the player switch from AI-bonus stats to player-boost stats only when the dice change.
   - Expected: one consistent rule. Code: `recalcBoardStats`, `getCardEffectiveStats`.

---

## 6. Sources

| ID | URL |
|---|---|
| S1 | https://ffxiv.consolegameswiki.com/wiki/Triple_Triad |
| S2 | https://steamcommunity.com/sharedfiles/filedetails/?id=2935597806 (FF8 Remastered Triple Triad guide) |
| S3 | https://en.wikipedia.org/wiki/Triple_Triad |
| S4 | https://en.wikipedia.org/wiki/Final_Fantasy_VIII |
| S5 | https://www.cavesofnarshe.com/ff9/tetramaster.php |
| S6 | https://www.eurogamer.net/queens-blood-matches-rules-card-types-final-fantasy-7-rebirth-9403 |
| S7 | https://www.ign.com/wikis/final-fantasy-7-rebirth/Queen%27s_Blood |
| S8 | https://gamingtrend.com/editorials/down-and-dirty-guide-to-rebirths-queens-blood-card-game/ |
| S9 | https://www.polygon.com/24062207/final-fantasy-7-rebirth-queens-blood-is-a-very-good-gwent/ |
| S10 | https://kotaku.com/ff7-rebirth-queens-blood-naoki-hamaguchi-interview-1851312733 |
| S11 | https://en.wikipedia.org/wiki/Queen%27s_Blood |
| S12 | https://en.wikipedia.org/wiki/Marvel_Snap |
| S13 | https://snap.fan/guides/a-guide-on-priority/ |
| S14 | https://en.wikipedia.org/wiki/Gwent:_The_Witcher_Card_Game |
| S15 | https://www.playgwent.com/en/news/18951/gwent-homecoming-see-whats-next-for-gwent |
| S16 | https://gwent.one/en/card/202140 |
| S17 | https://en.wikipedia.org/wiki/Into_the_Breach |
| S18 | https://www.rockpapershotgun.com/2018/03/05/into-the-breach-interface-design/ |
| S19 | https://www.gamedeveloper.com/design/-i-into-the-breach-i-dev-on-ui-design-sacrifice-cool-ideas-for-the-sake-of-clarity-every-time- |
| S20 | https://en.wikipedia.org/wiki/Dicey_Dungeons |
| S21 | https://en.wikipedia.org/wiki/Metal_Gear_Acid |
| S22 | https://en.wikipedia.org/wiki/Inscryption |

Not fetched (existence noted only): GDC 2019 "Into the Breach Design Postmortem", https://gdcvault.com/play/1026333/-Into-the-Breach-Design

### Unverified items (summary)
- Wall-clock match length for TT, Tetra Master, QB, Dicey, MGA and Inscryption.
- Snap "~3 min".
- QB starting hand of 5.
- Gwent Tactical Advantage being assigned to the first player.
- MGA board size.
- Inscryption first-player rule.
- ITB turns per mission (only "fixed number" is verified).
