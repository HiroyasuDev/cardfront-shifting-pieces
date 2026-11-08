# MiroFish TCG Gameplay Test — Shared Brief (read before starting)

## Target under test (READ-ONLY — do not edit)
- Game: `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html`
- Served at: `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`
  (server `WebPlayable/serve_playtest.py`, already running — **do NOT kill or restart port 8096**.
  If it is down, start your own: `python3 -m http.server 8097 -d /Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine` and use 8097.)
- Single inline `<script>`; key symbols: `PLAYER_HEROES` (8 cards), `ENEMY_MECHS` (8), `ALL_CARDS`, `STAGES` (4 bosses, `aiBonus` 0/0/1/1),
  `state`, `startStage`, `handleSlotClick`, `executeBossTurn`, `findCaptures`, `findClashes`, `getCardEffectiveStats`, `isColBoosted`,
  `nudgeColDie`, `rerollAllDice`, `recalcBoardStats`, `getScores`, `checkGameOver`, `closeModal`, drag engine (`beginPointerDrag`, `drag`).
- Rules summary (verify against code, code wins): 3×3 grid, boss pre-places 1 card at (0,1); player hand 5 unique heroes; boss pool 5 enemies (pops from end);
  player places → captures adjacent enemy if own edge > their facing edge (NESW = top,right,bottom,left); boss turn after 650 ms (greedy max-flip, random tie start);
  column die ≥4 gives player cards +1 all sides (clamped 9); 2 nudges (+1 refilled per boss turn, cap 3), 2 rerolls; 1 Tactical Slide/turn to adjacent empty tile (can capture);
  game ends when board full or hand empty; win iff blue > red.

## Tooling
- Real browser automation: Playwright core at `/Users/frederickamina/.local/node_modules/playwright-core`
  with Chromium `executablePath: /Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell`
  (`chromium.launch({headless:true, executablePath})`). Reference real-mouse test: `WebPlayable/tests/drag_e2e.js`.
- Node: `/Users/frederickamina/.local/bin/node`. Python w/ numpy/Pillow: `/Users/frederickamina/.local/share/mlx-env/bin/python3`.
- Local LLMs: Ollama `http://127.0.0.1:11434` (check `/api/tags`), MLX tools. Machine has **8 GB unified memory** — run at most one local model at a time, prefer ≤3B 4-bit.
- Safari `do JavaScript` is disabled and screen capture is not permitted — use headless Chromium for screenshots.

## Output isolation (no collisions)
Each workstream writes ONLY inside its own folder:
`/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/<workstream>/`
(scripts, raw JSON/CSV, screenshots, and a `REPORT.md`). Do not edit any other file, do not git commit/push.

## Integrity rules
- Every number in your REPORT.md must come from a script you ran (cite the output file). Label LLM-generated persona text as **synthetic**.
- Report bugs with: severity (P0–P3), repro steps, code line refs, observed vs expected.
- Finish with a short summary message to the coordinator: headline findings, key metrics, file paths.
