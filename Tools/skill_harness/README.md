# Grounded Continuous-Iteration GameDev-Skills Harness (`Tools/skill_harness/`)

Grounded verification and skill-routing harness for **`CARDFRONT: Cradle of Echoes`** (`Synapse.TcgEngine`), natively adapted for **Gemini 4 Argon (`gemini-4-argon`)** from the 77-skill `gamedev-skills/awesome-gamedev-agent-skills` ecosystem (featured in YouTube Short `https://youtu.be/t13A2XFGoOc` by Nick Automates) plus 14 custom SYNAPSE decompilation & art-direction skills (**92 `SKILL.md` files total**).

---

## 1. Why This Harness Exists

The earlier synthetic bridge (`Backend/synapse_gamedev_skills_harness_bridge.py` v1) tested toy Python arrays (`card_01..30`) and synthetic sine loops rather than the actual playable game.

`Tools/skill_harness/iterate.py` replaces all synthetic checks with **100% grounded verification** against the real dual-engine targets in `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine`:
1. **Primary Web Engine (Custom HTML5/CSS3/JS Tabletop Engine)**:
   - File: `WebPlayable/cardfront_cradle_of_echoes_playable.html`
   - Served at: `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html` (`WebPlayable/serve_playtest.py`)
   - Governed by `router/SKILL.md` §6 & `router/references/custom-engines.md`
2. **Secondary Unity Engine (`Unity 2022.3.40f1`)**:
   - Fingerprint: `Assets/` + `ProjectSettings/ProjectVersion.txt`
   - Key scripts: `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs`, `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs`, `Assets/Scripts/Data/CardDataSO.cs`

---

## 2. Three-Step Architecture (`iterate.py`)

### Step A — Router & Dual-Engine Skill Composition
- Invokes `/Users/frederickamina/.local/bin/pxg-gamedev-harness detect <dir> --json` and `route "<prompt>" --dir <dir> --json`.
- Verifies CLI output against `/Users/frederickamina/.prime/agent/harness/gamedev_skills/router/SKILL.md` and `router/references/custom-engines.md`.
- Outputs the ordered 4-slot progressive disclosure stack:
  `Engine Fundamentals -> Discipline(s) -> Genre -> Workflow`
- Generates `/Users/frederickamina/.prime/agent/harness/gamedev_skills/.gemini-plugin/gemini-4-argon-skills.json` (and local copy `Tools/skill_harness/gemini-4-argon-skills.json`) registering all 92 `SKILL.md` files with **Gemini 4 Argon (`gemini-4-argon`)** subagent and MCP tool bindings.

### Step B — Real Game Verification
1. **Real-Mouse Drag & Drop E2E (`WebPlayable/tests/drag_e2e.js`)**:
   - Launches headless Chromium via Playwright (`PLAYWRIGHT_CORE=/Users/frederickamina/.local/node_modules/playwright-core`) and verifies ghost creation, invalid drop spring-back, magnet snap near slot edge, valid drop placement, Tactical Slide by drag, and click-to-place fallback.
2. **In-Page Automated Playtest (`?autotest=1`)**:
   - Runs a full 4-turn match in headless Chromium testing 4 camera tilt presets, `nudgeColDie(0)`, `rerollAllDice()`, Tactical Slide, and greedy capture deployment, asserting `TEST_COMPLETE:*:SINGLETON=true:IMG=true`.
3. **Grounded Check Suite (`core_checks.json` + `Datasets/mirofish_gameplay/skills_*/checks.json`)**:
   - Executes `Tools/skill_harness/core_checks.json` (24 built-in grounded checks across 10 skills) and automatically merges any `Datasets/mirofish_gameplay/skills_*/checks.json` files produced by skill-audit workstreams.
   - Supports `playwright` (live `page.evaluate` JS probes), `static_regex` (regex probes against `.html` / `.cs`), `metric` (JSON/command telemetry probes), and `manual` check methods.
4. **MiroFish Telemetry Ingestion**:
   - Automatically ingests summary metrics from `Datasets/mirofish_gameplay/{balance,rules_audit,ux_qa,personas,benchmark,skills_*}/`.

### Step C — Scorecard, Gate & Ranked P0→P3 Backlog
- Computes per-skill pass rates, diff vs. the previous iteration in `Datasets/skill_harness/iterations.jsonl`, overall gate status (`PASS_ALL_GATES` / `PASS_E2E_WITH_SKILL_BACKLOG` / `FAIL_P0_BLOCKERS`), and a prioritized **P0 → P3 remediation backlog** with exact `SKILL.md` line citations and game code line references.
- Writes:
  - `Datasets/skill_harness/iterations.jsonl`
  - `Datasets/skill_harness/latest_scorecard.json`
  - `Datasets/skill_harness/latest_report.md`

---

## 3. Usage

```bash
# Run a grounded iteration with the default TCG UI/Feel/Balance prompt
python3 Tools/skill_harness/iterate.py

# Run with a custom change request prompt and output JSON summary
python3 Tools/skill_harness/iterate.py \
  --prompt "Fix stale boss turn timeout on Reset, guard drag state on stage change, and add versioned localStorage save system" \
  --json

# Run via the updated backend bridge (also updates Logs/gamedev_skills_video_t13A2XFGoOc_report.json)
python3 Backend/synapse_gamedev_skills_harness_bridge.py
```
