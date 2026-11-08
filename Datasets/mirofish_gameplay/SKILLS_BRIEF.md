# Gamedev-Skills Integration — Shared Brief (video t13A2XFGoOc)

Source video: "Turn Claude into an Expert Game Dev with these Free 77 AI Skills" (Nick Automates, 35 s Short).
It promotes `gamedev-skills/awesome-gamedev-agent-skills`: 77 skills + a master router that auto-selects skills by engine + task;
highlights: engine coverage (Unreal/Unity/Godot/web), auto-routing, player movement/genre skills, a dedicated **art-direction** skill
for asset consistency, and shipping to App Store/Steam.

## Local copies (already installed, read-only)
- Skills repo (upstream-current, 78 SKILL.md + 14 custom SYNAPSE skills): `/Users/frederickamina/.prime/agent/harness/gamedev_skills/`
  - router: `router/SKILL.md` (+ `router/references/routing-table.md`, `custom-engines.md`, `engine-detection.md`)
  - skills: `skills/<category>/<name>/SKILL.md` (+ `references/` on demand)
- Router CLI: `/Users/frederickamina/.local/bin/pxg-gamedev-harness` (`detect <dir> --json`, `route "<prompt>" --dir <dir> --json`, `catalog --json`).
  Verify its output against router/SKILL.md; don't trust it blindly.
- Existing bridge (untracked, created by an earlier agent): `Backend/synapse_gamedev_skills_harness_bridge.py` + `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs`.
  **Known flaw:** its checks run on synthetic toy data (card_01..30, random seeds), not on the real game.

## Targets (project root `/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine`)
1. Web build (primary, custom engine — plain HTML/CSS/JS, no framework): `WebPlayable/cardfront_cradle_of_echoes_playable.html` — **READ-ONLY right now**
   (5 gameplay-test agents are testing commit 17b5c65; see `Datasets/mirofish_gameplay/BRIEF.md` for rules summary, tooling, Playwright/Chromium paths, server on :8096 — do not kill it).
2. Unity project (Unity 2022.3.40f1): `Assets/` (e.g. `Assets/TcgEngine/Scripts/GameLogic/CardFrontUnifiedRuntime.cs`). Read-only.

## Skill audit output contract (auditors)
Write ONLY to `Datasets/mirofish_gameplay/skills_<your-slug>/`:
- `REPORT.md`: for every loaded skill: which SKILL.md sections apply, each rule/guideline quoted briefly (with file path + line) → verdict for CARDFRONT
  (PASS / PARTIAL / FAIL / N/A) with evidence (code line refs, measurements, screenshots) → concrete fix (code sketch, not applied) → priority P0–P3 and effort S/M/L.
- `checks.json`: machine-readable checks for the harness, array of
  `{ "id": "<slug>.<n>", "skill": "<category/name>", "rule": "<short quote>", "source": "<SKILL.md path:line>",
     "target": "web|unity", "method": "static_regex|playwright|metric|manual",
     "probe": { ... method-specific: regex+file, or a JS expression evaluated in the page that returns true/false/number, or script path ... },
     "expect": "<true | >=N | <=N | regex>", "priority": "P0-P3" }`
  Prefer automatable checks (static_regex / playwright `page.evaluate` expressions against the live page at
  `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`). Validate every probe you write by actually running it once and record its current result.
- Every claim must cite a SKILL.md line and a game code line or a measurement you ran. No invented skill names.
- Finish with a concise summary message to the coordinator.
