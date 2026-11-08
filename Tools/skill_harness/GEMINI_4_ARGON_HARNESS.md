# Gemini 4 Argon Native Adaptation of `awesome-gamedev-agent-skills` (Video `t13A2XFGoOc`)

## 1. Deep Analysis of Video `t13A2XFGoOc` (`Nick Automates`)

- **Video**: [Turn Claude into an Expert Game Dev with these Free 77 AI Skills](https://youtu.be/t13A2XFGoOc?si=V1HkMBTl7KO5qwac) (35s YouTube Short by `@nickautomates`)
- **Featured Upstream Repository**: `gamedev-skills/awesome-gamedev-agent-skills` (77 skills + 1 Master Router = 78 `SKILL.md` files)
- **Local SYNAPSE Expansion**: +14 custom decompilation & art-direction skills = **91 routable skills + 1 Master Router (92 `SKILL.md` files total)** at `/Users/frederickamina/.prime/agent/harness/gamedev_skills/`

### What the Video Demonstrates vs. How Gemini 4 Argon Upgrades It

| Dimension | Upstream Video (`t13A2XFGoOc` / Claude Code) | SYNAPSE Gemini 4 Argon (`gemini-4-argon`) Native Adaptation |
| :--- | :--- | :--- |
| **Plugin Manifest** | `.claude-plugin/marketplace.json` | `.gemini-plugin/gemini-4-argon-skills.json` + `Tools/skill_harness/gemini-4-argon-skills.json` |
| **Engine Detection** | Single catalog engine (`Unity` or `Godot` or `Phaser`) | **Dual-Engine Contract**: Custom HTML5/CSS3/JS Web Engine (`WebPlayable/` via `router/references/custom-engines.md`) + Unity `2022.3.40f1` (`Assets/`) |
| **Progressive Disclosure** | Single-agent markdown read | `pxg-gamedev-harness route --json` + `router/SKILL.md` verification -> targeted `read_file` on exact 4-slot stack (`Engine -> Discipline(s) -> Genre -> Workflow`) |
| **Execution Topology** | Single-threaded coding assistant | **Parallel Subagent Swarms** via `invoke_subagent` (`Model: "inherit"`) dispatching `code-implementer`, `prime-vision-worker`, `mlx-local-worker`, `truth-verifier`, and `jev-judge` concurrently |
| **Verification Gate** | Manual inspection or ad-hoc unit tests | **Grounded Continuous Harness (`Tools/skill_harness/iterate.py`)**: Real Playwright Chromium `drag_e2e.js` + `?autotest=1` + merged `checks.json` probes + Apple Silicon `jevmlx` / `jev_gate` |

---

## 2. Gemini 4 Argon Subagent & MCP Tool Bindings

Every skill in `.gemini-plugin/gemini-4-argon-skills.json` is bound to Gemini 4 Argon's native toolset:

1. **`router` (`router/SKILL.md`)**:
   - **Primary Agent**: `parallel-architect` (`gemini-4-argon`)
   - **Tools**: `/Users/frederickamina/.local/bin/pxg-gamedev-harness`, `sequentialthinking`, `mem`, `mlx_jev_choose`
2. **Engine Skills (`skills/unity/*`, `skills/godot/*`, `skills/unreal/*`, `skills/web-engines/*`, `skills/other-engines/*`, `skills/ebitengine/*`)**:
   - **Primary Agent**: `code-implementer` (`Model: "inherit"`, isolated `Workspace: "share"` or `"branch"`)
   - **Verification**: `truth-verifier`, `jev-judge`
3. **Discipline & Genre Skills (`skills/disciplines/*`, `skills/genres/*`)**:
   - **Primary Agent**: `code-implementer`
   - **Grounded Probes**: Executed live in headless Chromium via `Tools/skill_harness/iterate.py` (`playwright`, `static_regex`, `metric`)
4. **Art Direction & Asset Pipeline (`skills/disciplines/create-game-assets`, `skills/art-direction/tactical-illustrator-library`)**:
   - **Primary Agent**: `prime-vision-worker` / `mlx-local-worker`
   - **Tools**: `scripts/asset_report.py`, `scripts/build_preview_sheet.py`, `mlx_jev_rate`
5. **Pre-Completion Verification Gate (`skills/workflows/*`)**:
   - **Primary Agent**: `truth-verifier` + `jev-judge` (`jev_gate` / `mlx_jev_judge`)
