# CARDFRONT: Cradle of Echoes — Grounded Skill Harness Report (Iteration #160)

- **Timestamp (UTC)**: `2026-11-09T10:42:12Z`
- **Target Orchestrator Model**: **`gemini-4-argon`** (`Gemini 4 Argon`)
- **Overall Gate Status**: **`PASS_ALL_GATES`**
- **Real Drag & Drop E2E (`WebPlayable/tests/drag_e2e.js`)**: `PASS`
- **Real In-Page Playtest (`?autotest=1`)**: `PASS` (`TEST_COMPLETE:5-4:SINGLETON=true:IMG=true`)
- **Grounded Skill Checks**: **134 / 134 PASS (100.0%)** — `0 P0`, `0 P1` failures
- **Check Suites Merged**: `Tools/skill_harness/core_checks.json, Datasets/mirofish_gameplay/skills_ai_save_ship/checks.json, Datasets/mirofish_gameplay/skills_art_direction/checks.json, Datasets/mirofish_gameplay/skills_cardgame_ui_input/checks.json, Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/checks.json`

## 1. Step A — Router & Dual-Engine Composition (`router/SKILL.md`)

- **Change Request Prompt**: `Refine 3x3 tactical card game UI layout, dynamic telegraph animations, game feel hit-stop screen shake, and ScriptableObject card balance`
- **Primary Target**: `Custom HTML5/CSS3/JS Tabletop Engine` (`WebPlayable/cardfront_cradle_of_echoes_playable.html`, bound via `router/references/custom-engines.md`)
- **Secondary Target**: `Unity 6000.6.8f1` (`Assets/ + ProjectSettings/ProjectVersion.txt`)
- **Composition Order**: `Engine Fundamentals -> Discipline(s) -> Genre -> Workflow`

### Loaded `SKILL.md` Stack
| Order | Slot | Skill | Path | Source |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `engine` | `unity/unity-scriptableobjects` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/unity/unity-scriptableobjects/SKILL.md` | `pxg-gamedev-harness` |
| 2 | `discipline` | `disciplines/game-feel` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md` | `pxg-gamedev-harness` |
| 3 | `discipline` | `disciplines/game-ui-ux` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md` | `pxg-gamedev-harness` |
| 4 | `genre` | `genres/card-game` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md` | `pxg-gamedev-harness` |

## 2. Step B — Per-Skill Scorecard

| Skill | Total Checks | Passed | Failed | Pass Rate | Failing Check IDs |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `art-direction/tactical-illustrator-library` | 1 | 1 | 0 | **100.0%** | — |
| `art-direction/tcg-creative-game-designer` | 3 | 3 | 0 | **100.0%** | — |
| `disciplines/ai-behavior-trees-utility-ai` | 5 | 5 | 0 | **100.0%** | — |
| `disciplines/art-direction` | 2 | 2 | 0 | **100.0%** | — |
| `disciplines/audio-design` | 6 | 6 | 0 | **100.0%** | — |
| `disciplines/camera-systems` | 4 | 4 | 0 | **100.0%** | — |
| `disciplines/create-game-assets` | 18 | 18 | 0 | **100.0%** | — |
| `disciplines/game-ai` | 4 | 4 | 0 | **100.0%** | — |
| `disciplines/game-feel` | 19 | 19 | 0 | **100.0%** | — |
| `disciplines/game-ui-ux` | 21 | 21 | 0 | **100.0%** | — |
| `disciplines/input-systems` | 6 | 6 | 0 | **100.0%** | — |
| `disciplines/performance-optimization` | 6 | 6 | 0 | **100.0%** | — |
| `disciplines/save-systems` | 6 | 6 | 0 | **100.0%** | — |
| `disciplines/ui-ux-design` | 1 | 1 | 0 | **100.0%** | — |
| `genres/card-game` | 16 | 16 | 0 | **100.0%** | — |
| `unity/unity-build-pipeline` | 1 | 1 | 0 | **100.0%** | — |
| `unity/unity-csharp-scripting` | 3 | 3 | 0 | **100.0%** | — |
| `unity/unity-netcode-multiplayer` | 1 | 1 | 0 | **100.0%** | — |
| `unity/unity-scriptableobjects` | 6 | 6 | 0 | **100.0%** | — |
| `workflows/itch-publish` | 2 | 2 | 0 | **100.0%** | — |
| `workflows/prototype-fast` | 2 | 2 | 0 | **100.0%** | — |
| `workflows/steam-publish` | 1 | 1 | 0 | **100.0%** | — |

### Diff vs. Previous Iteration
- **Previous Iteration**: `159`
- **Pass Count Delta**: `+0` (Total checks delta: `+0`)
- **Newly Passing Checks**: `None`
- **Newly Failing Checks**: `None`

### Ingested MiroFish Gameplay Telemetry
- **Active Workstreams**: `balance, rules_audit, ux_qa, personas, benchmark, skills_art_direction`
- **Balance / Engine Parity**: `166 matches`, `975 actions`, `100% agreement`
- **Rules Audit**: `0 / 11` edge-case repro probes reproduced (`R01..R11`)
- **UX / Perf QA**: Drag p95 frame time `16.7 ms`, long tasks `0`, `renderAll` avg `0.47 ms`, keyboard-only game completed `True`
- **Persona Playtesters**: `120 matches` across `p01, p02, p03, p04, p05, p06, p07, p08, p09, p10` (`113 wins`)
- **Art Direction Raster QA**: `ok=True`, `16 card portraits verified (600x800)`

## 3. Step C — Prioritized P0 → P3 Remediation Backlog

| Rank | Priority | Check ID | Skill (`SKILL.md` Source) | Code Reference | Observed vs Expected | Concrete Remediation |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |

## 4. All Grounded Check Verdicts

| ID | Verdict | Priority | Skill | Method | Source | Code Ref |
| :--- | :---: | :---: | :--- | :---: | :--- | :--- |
| `core.card_game.01` | PASS | `P0` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:107` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1565-1584` |
| `core.card_game.02` | PASS | `P1` | `genres/card-game` | `static_regex` | `skills/genres/card-game/SKILL.md:118` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1499-1506` |
| `core.card_game.03` | PASS | `P1` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:33` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:963-1148` |
| `core.card_game.04` | PASS | `P0` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:95` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1546,1754` |
| `core.card_game.05` | PASS | `P0` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:123` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1546,2356-2378` |
| `core.card_game.06` | PASS | `P1` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:38` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1512-1520,1614-1623` |
| `core.card_game.07` | PASS | `P1` | `genres/card-game` | `static_regex` | `skills/genres/card-game/SKILL.md:115` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1499-1506,1608` |
| `core.game_feel.01` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `skills/disciplines/game-feel/SKILL.md:66` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1394-1400` |
| `core.game_feel.02` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `skills/disciplines/game-feel/SKILL.md:109` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs:81-91` |
| `core.game_feel.03` | PASS | `P2` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:40` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1739-1744` |
| `core.game_feel.04` | PASS | `P2` | `disciplines/game-feel` | `static_regex` | `skills/disciplines/game-feel/SKILL.md:156` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1372-1408` |
| `core.game_ui_ux.01` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:35` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:25-30,140-152` |
| `core.game_ui_ux.02` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:41` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1359,1410-1446` |
| `core.game_ui_ux.03` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:45` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:948-953,1546,1825-1846` |
| `core.game_ui_ux.04` | PASS | `P2` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:139` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:75,171,275,323` |
| `core.create_game_assets.01` | PASS | `P1` | `disciplines/create-game-assets` | `playwright` | `skills/disciplines/create-game-assets/SKILL.md:108` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:527-533,2532-2540` |
| `core.create_game_assets.02` | PASS | `P2` | `disciplines/create-game-assets` | `playwright` | `skills/disciplines/create-game-assets/SKILL.md:52` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1151-1255` |
| `core.unity_so.01` | PASS | `P1` | `unity/unity-scriptableobjects` | `static_regex` | `skills/unity/unity-scriptableobjects/SKILL.md:30` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs:17-30` |
| `core.unity_so.02` | PASS | `P2` | `unity/unity-scriptableobjects` | `static_regex` | `skills/unity/unity-scriptableobjects/SKILL.md:115` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs:18-42` |
| `core.input_systems.01` | PASS | `P1` | `disciplines/input-systems` | `playwright` | `skills/disciplines/input-systems/SKILL.md:35` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1410-1446` |
| `core.audio_design.01` | PASS | `P2` | `disciplines/audio-design` | `playwright` | `skills/disciplines/audio-design/SKILL.md:33` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1323-1344` |
| `core.save_systems.01` | PASS | `P2` | `disciplines/save-systems` | `static_regex` | `skills/disciplines/save-systems/SKILL.md:37` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1546-1590,1820-1846` |
| `core.game_ai.01` | PASS | `P2` | `disciplines/game-ai` | `playwright` | `skills/disciplines/game-ai/SKILL.md:36` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1757-1785` |
| `core.performance.01` | PASS | `P1` | `disciplines/performance-optimization` | `metric` | `skills/disciplines/performance-optimization/SKILL.md:65` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1985-2105` |
| `core.tabletop_real_estate.01` | PASS | `P0` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:45` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:22-30,560-595` |
| `core.tabletop_real_estate.02` | PASS | `P0` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:52` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:25-30,275-355` |
| `core.tabletop_real_estate.03` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:64` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:203-226` |
| `core.tabletop_real_estate.04` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:78` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:640-712,3334-3365` |
| `core.tabletop_real_estate.05` | PASS | `P0` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:48` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:426-540,1486-1545` |
| `core.tabletop_real_estate.06` | PASS | `P1` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:62` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:320-421,3580-3612` |
| `core.tabletop_real_estate.07` | PASS | `P1` | `disciplines/art-direction` | `playwright` | `skills/disciplines/art-direction/SKILL.md:54` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1136-1195` |
| `core.tabletop_real_estate.08` | PASS | `P1` | `disciplines/art-direction` | `playwright` | `skills/disciplines/art-direction/SKILL.md:71` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:714-775,3548-3560` |
| `core.tabletop_real_estate.09` | PASS | `P2` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:88` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:596-639,1523-1528` |
| `core.tabletop_real_estate.10` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:49` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:780-798,3541-3545` |
| `core.tabletop_real_estate.11` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:63` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:746-753,2861-2876` |
| `core.tabletop_real_estate.12` | PASS | `P0` | `disciplines/game-ui-ux` | `metric` | `skills/disciplines/game-ui-ux/SKILL.md:95` | `Tools/skill_harness/assess_tabletop_real_estate.js:1-140` |
| `core.tcg_creative_designer.01` | PASS | `P0` | `art-direction/tcg-creative-game-designer` | `metric` | `skills/art-direction/tcg-creative-game-designer/SKILL.md:30` | `Backend/render_tcg_agent_deck_graphics.py:87-610,992-1016` |
| `core.tcg_creative_designer.02` | PASS | `P1` | `art-direction/tcg-creative-game-designer` | `metric` | `skills/art-direction/tcg-creative-game-designer/SKILL.md:58` | `Backend/generate_agent_deck_3d_glb.py:45-248` |
| `core.tcg_creative_designer.03` | PASS | `P1` | `art-direction/tcg-creative-game-designer` | `playwright` | `skills/art-direction/tcg-creative-game-designer/SKILL.md:82` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1810-1870,2261-2285` |
| `core.next_gen_tabletop.01` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:54` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1470-1495,4450-4535` |
| `core.next_gen_tabletop.02` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:62` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1496-1522,4520-4535` |
| `core.next_gen_tabletop.03` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:88` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1525-1562,4542-4555` |
| `core.next_gen_tabletop.04` | PASS | `P2` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:112` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1205-1222` |
| `core.next_gen_tabletop.05` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `skills/disciplines/game-ui-ux/SKILL.md:45` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1880-1895,4125-4175` |
| `core.next_gen_tabletop.06` | PASS | `P2` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:72` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1572-1598,4108-4124` |
| `core.next_gen_tabletop.07` | PASS | `P1` | `genres/card-game` | `playwright` | `skills/genres/card-game/SKILL.md:64` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1600-1638,4176-4226` |
| `core.next_gen_tabletop.08` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:63` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1564-1571,3464-3495` |
| `core.next_gen_tabletop.09` | PASS | `P2` | `disciplines/audio-design` | `playwright` | `skills/disciplines/audio-design/SKILL.md:52` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:2482-2525` |
| `core.next_gen_tabletop.10` | PASS | `P1` | `unity/unity-csharp-scripting` | `static_regex` | `skills/unity/unity-csharp-scripting/SKILL.md:40` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs:914-1009` |
| `core.next_gen_tabletop.11` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:78` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1845-1860,4140-4160` |
| `core.next_gen_tabletop.12` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `skills/disciplines/create-game-assets/SKILL.md:92` | `Backend/pxg_v100_anime_telegraph_trainer.py:1-190` |
| `core.sakuga_v100.01` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `skills/disciplines/create-game-assets/SKILL.md:94` | `Backend/pxg_v100_anime_telegraph_trainer.py:302-432` |
| `core.sakuga_v100.02` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `skills/disciplines/create-game-assets/SKILL.md:98` | `Backend/train_v100_sakuga_lora.py:130-240` |
| `core.sakuga_v100.03` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `skills/disciplines/game-feel/SKILL.md:82` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:1880-1892,4165-4255` |
| `core.sakuga_v100.04` | PASS | `P1` | `disciplines/ui-ux-design` | `playwright` | `skills/disciplines/ui-ux-design/SKILL.md:72` | `WebPlayable/cardfront_cradle_of_echoes_playable.html:4409-4435` |
| `core.sakuga_v100.05` | PASS | `P1` | `unity/unity-csharp-scripting` | `static_regex` | `skills/unity/unity-csharp-scripting/SKILL.md:44` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs:1010-1038` |
| `core.unity6_tcg_rea_baseline.01` | PASS | `P0` | `unity/unity-build-pipeline` | `metric` | `skills/unity/unity-build-pipeline/SKILL.md:38` | `Assets/Scripts/Editor/UnityHeadlessAgentCLI.cs:35-210` |
| `core.unity6_tcg_rea_baseline.02` | PASS | `P0` | `unity/unity-scriptableobjects` | `metric` | `skills/unity/unity-scriptableobjects/SKILL.md:42` | `Backend/synapse_unity6_tcg_engine_rea_pipeline.py:40-298` |
| `core.unity6_tcg_rea_baseline.03` | PASS | `P1` | `unity/unity-csharp-scripting` | `static_regex` | `skills/unity/unity-csharp-scripting/SKILL.md:58` | `Assets/Scripts/Core/CardData.cs:5-530` |
| `core.unity6_tcg_rea_baseline.04` | PASS | `P0` | `unity/unity-netcode-multiplayer` | `metric` | `skills/unity/unity-netcode-multiplayer/SKILL.md:40` | `Backend/sync_unity_tcg_engine_port.py:180-235` |
| `ai_save_ship.1` | PASS | `P0` | `disciplines/game-ai` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md:57-67` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.2` | PASS | `P1` | `disciplines/ai-behavior-trees-utility-ai` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md:45-57` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.3` | PASS | `P1` | `disciplines/ai-behavior-trees-utility-ai` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md:126-139` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.4` | PASS | `P0` | `disciplines/ai-behavior-trees-utility-ai` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md:126-135` | `Datasets/mirofish_gameplay/skills_ai_save_ship/boss_ai_utility.js` |
| `ai_save_ship.5` | PASS | `P0` | `disciplines/ai-behavior-trees-utility-ai` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md:75-83` | `Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json` |
| `ai_save_ship.6` | PASS | `P0` | `disciplines/ai-behavior-trees-utility-ai` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/ai-behavior-trees-utility-ai/SKILL.md:75-83` | `Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json` |
| `ai_save_ship.7` | PASS | `P1` | `disciplines/game-ai` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md:57-67` | `Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json` |
| `ai_save_ship.8` | PASS | `P1` | `disciplines/game-ai` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ai/SKILL.md:57-67` | `Datasets/mirofish_gameplay/skills_ai_save_ship/raw/ai_benchmark.json` |
| `ai_save_ship.9` | PASS | `P1` | `disciplines/save-systems` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md:27-35` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.10` | PASS | `P1` | `disciplines/save-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md:45-64` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `ai_save_ship.11` | PASS | `P1` | `disciplines/save-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md:173-177` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `ai_save_ship.12` | PASS | `P1` | `disciplines/save-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md:175` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `ai_save_ship.13` | PASS | `P1` | `disciplines/save-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/save-systems/SKILL.md:97-130` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `ai_save_ship.14` | PASS | `P1` | `workflows/prototype-fast` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/prototype-fast/SKILL.md:62-66` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.15` | PASS | `P2` | `workflows/prototype-fast` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/prototype-fast/SKILL.md:88-92` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.16` | PASS | `P0` | `workflows/itch-publish` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md:129` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.17` | PASS | `P0` | `workflows/itch-publish` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/itch-publish/SKILL.md:132` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `ai_save_ship.18` | PASS | `P2` | `workflows/steam-publish` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/workflows/steam-publish/SKILL.md:110-163` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `art_direction.1` | PASS | `P0` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:16-18` | `Datasets/mirofish_gameplay/skills_art_direction/raw/asset_report_cards.json` |
| `art_direction.2` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:16-18` | `Datasets/mirofish_gameplay/skills_art_direction/raw/asset_report_bgs.json` |
| `art_direction.3` | PASS | `P0` | `disciplines/create-game-assets` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:38-40` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `art_direction.4` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:104-105` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.5` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/art-direction.md:60` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.6` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/art-direction.md:58-67` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.7` | PASS | `P0` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/art-direction.md:14` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.8` | PASS | `P0` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/art-direction.md:14` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.9` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:106-109` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.10` | PASS | `P1` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/raster-pipeline.md:33` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.11` | PASS | `P2` | `disciplines/create-game-assets` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:104-105` | `Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json` |
| `art_direction.12` | PASS | `P1` | `disciplines/create-game-assets` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md:20-21` | `Assets/Scripts/Visuals/SynapseIllustratorStyleLibrary.cs` |
| `art_direction.13` | PASS | `P2` | `disciplines/create-game-assets` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/references/raster-pipeline.md:39-41` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `art_direction.14` | PASS | `P1` | `art-direction/tactical-illustrator-library` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/art-direction/tactical-illustrator-library/SKILL.md:10-21` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `cardgame_ui_input.1` | PASS | `P0` | `genres/card-game` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:34` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.2` | PASS | `P1` | `genres/card-game` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:118-120` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.3` | PASS | `P1` | `genres/card-game` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:115-117` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.4` | PASS | `P1` | `genres/card-game` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:33` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.5` | PASS | `P0` | `genres/card-game` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:81-88` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.6` | PASS | `P1` | `genres/card-game` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/genres/card-game/SKILL.md:38` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `cardgame_ui_input.7` | PASS | `P0` | `disciplines/game-ui-ux` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:35-40` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.8` | PASS | `P0` | `disciplines/game-ui-ux` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:35-37` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.9` | PASS | `P1` | `disciplines/game-ui-ux` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:132-133` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.10` | PASS | `P2` | `disciplines/game-ui-ux` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:41-42` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.11` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:139-141` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.12` | PASS | `P1` | `disciplines/game-ui-ux` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:43-44` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.13` | PASS | `P2` | `disciplines/game-ui-ux` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:43-44` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.14` | PASS | `P2` | `disciplines/game-ui-ux` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-ui-ux/SKILL.md:45-46, 106` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.15` | PASS | `P1` | `disciplines/input-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md:36-37, 176-177` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.16` | PASS | `P1` | `disciplines/input-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md:166-169, 186-188` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.17` | PASS | `P2` | `disciplines/input-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md:38-39, 134` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.18` | PASS | `P2` | `disciplines/input-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md:38-39` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.19` | PASS | `P1` | `disciplines/input-systems` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/input-systems/SKILL.md:42-45` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `cardgame_ui_input.20` | PASS | `P1` | `unity/unity-scriptableobjects` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/unity/unity-scriptableobjects/SKILL.md:72-81, 110-113` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs` |
| `cardgame_ui_input.21` | PASS | `P1` | `unity/unity-scriptableobjects` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/unity/unity-scriptableobjects/SKILL.md:81-95, 115-120` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs` |
| `cardgame_ui_input.22` | PASS | `P2` | `unity/unity-scriptableobjects` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/unity/unity-scriptableobjects/SKILL.md:29-35` | `Assets/Scripts/Core/CardFrontUnifiedRuntime.cs` |
| `feel_audio_camera_perf.1` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:66, 81` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.2` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:83-86, 144` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.3` | PASS | `P1` | `disciplines/game-feel` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:92-114` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.4` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:109-113, 146-148` | `Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs` |
| `feel_audio_camera_perf.5` | PASS | `P1` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:97-105, 150-151` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.6` | PASS | `P2` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:56-57, 131-138` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.7` | PASS | `P2` | `disciplines/game-feel` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/game-feel/SKILL.md:157-158` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.8` | PASS | `P1` | `disciplines/audio-design` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/audio-design/SKILL.md:33-39, 162-167` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.9` | PASS | `P2` | `disciplines/audio-design` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/audio-design/SKILL.md:80-81, 164-165` | `Assets/Scripts/Audio/SynapseProceduralAudioDirector.cs` |
| `feel_audio_camera_perf.10` | PASS | `P2` | `disciplines/audio-design` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/audio-design/SKILL.md:48-49, 114-130` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.11` | PASS | `P2` | `disciplines/audio-design` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/audio-design/SKILL.md:45-47` | `Assets/Scripts/Audio/SynapseProceduralAudioDirector.cs` |
| `feel_audio_camera_perf.12` | PASS | `P2` | `disciplines/camera-systems` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/camera-systems/SKILL.md:46-47` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.13` | PASS | `P1` | `disciplines/camera-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/camera-systems/SKILL.md:38-40, 73-80, 131-132` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.14` | PASS | `P2` | `disciplines/camera-systems` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/camera-systems/SKILL.md:52` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.15` | PASS | `P2` | `disciplines/camera-systems` | `playwright` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/camera-systems/SKILL.md:117-127, 145-146` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
| `feel_audio_camera_perf.16` | PASS | `P1` | `disciplines/performance-optimization` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md:62-70` | `Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/raw/playwright_feel_perf_audit.json` |
| `feel_audio_camera_perf.17` | PASS | `P1` | `disciplines/performance-optimization` | `metric` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md:88-102, 146-149` | `Datasets/mirofish_gameplay/skills_feel_audio_camera_perf/raw/playwright_feel_perf_audit.json` |
| `feel_audio_camera_perf.18` | PASS | `P1` | `disciplines/performance-optimization` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md:88-102` | `Assets/Scripts/Tools/SynapseMemoryPool.cs` |
| `feel_audio_camera_perf.19` | PASS | `P2` | `disciplines/performance-optimization` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md:125-128, 148` | `Assets/Scripts/AI/SynapseMiroStrandsSimulationEngine.cs` |
| `feel_audio_camera_perf.20` | PASS | `P2` | `disciplines/performance-optimization` | `static_regex` | `/Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/performance-optimization/SKILL.md:48-50` | `WebPlayable/cardfront_cradle_of_echoes_playable.html` |
