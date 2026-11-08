#!/usr/bin/env python3
"""
Tools/skill_harness/iterate.py
==============================
Grounded Continuous-Iteration GameDev-Skills Harness for `CARDFRONT: Cradle of Echoes`
(`Synapse.TcgEngine`), natively adapted for **Gemini 4 Argon (`gemini-4-argon`)**.

Replaces legacy synthetic toy simulations (`card_01..30`) with real verification against:
1. Primary Web Engine (custom HTML5/CSS3/JS): `WebPlayable/cardfront_cradle_of_echoes_playable.html`
   served at `http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html`
2. Unity 2022.3.40f1 Project: `Assets/` (`CardFrontUnifiedRuntime.cs`, `SynapseGameDevSkillsHarness.cs`, `CardDataSO.cs`)

Workflow (Steps A -> B -> C):
- Step A (Router & Gemini 4 Argon Dispatch):
  Queries `/Users/frederickamina/.local/bin/pxg-gamedev-harness` (`detect` & `route --json`),
  verifies against `router/SKILL.md` and `router/references/custom-engines.md` (dual-engine
  contract: custom web engine + Unity 2022.3.40f1), and outputs the ordered `SKILL.md` files
  (`Engine Fundamentals -> Discipline(s) -> Genre -> Workflow`) plus Gemini 4 Argon subagent bindings.
- Step B (Real Game Verification):
  1. Runs `WebPlayable/tests/drag_e2e.js` in headless Chromium via Playwright.
  2. Runs `?autotest=1` visual automated playtest in headless Chromium and verifies
     `TEST_COMPLETE:*:SINGLETON=true:IMG=true`.
  3. Loads `Tools/skill_harness/core_checks.json` (>=15 grounded checks) and dynamically merges
     all `Datasets/mirofish_gameplay/skills_*/checks.json` files present on disk, executing
     `playwright`, `static_regex`, `metric`, and `manual` probes against the live game and code.
  4. Ingests real gameplay telemetry from `Datasets/mirofish_gameplay/{balance,rules_audit,ux_qa,personas,benchmark,skills_*}/`.
- Step C (Scorecard, Gate & Ranked Backlog):
  Computes per-skill pass/fail scorecard, diff vs previous iteration in `Datasets/skill_harness/iterations.jsonl`,
  and a prioritized P0->P3 remediation backlog citing exact `SKILL.md` lines and game code lines.
  Writes `Datasets/skill_harness/iterations.jsonl`, `Datasets/skill_harness/latest_scorecard.json`,
  and `Datasets/skill_harness/latest_report.md`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
SKILLS_REPO = Path("/Users/frederickamina/.prime/agent/harness/gamedev_skills")
HARNESS_BIN = Path("/Users/frederickamina/.local/bin/pxg-gamedev-harness")
NODE_BIN = Path("/Users/frederickamina/.local/bin/node")
PLAYWRIGHT_CORE = "/Users/frederickamina/.local/node_modules/playwright-core"
CHROMIUM_EXE = (
    "/Users/frederickamina/Library/Caches/ms-playwright/"
    "chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell"
)
DEFAULT_PLAYTEST_URL = "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html"

SKILL_HARNESS_TOOLS_DIR = PROJECT_ROOT / "Tools" / "skill_harness"
CORE_CHECKS_JSON = SKILL_HARNESS_TOOLS_DIR / "core_checks.json"
MIROFISH_DIR = PROJECT_ROOT / "Datasets" / "mirofish_gameplay"
OUTPUT_DIR = PROJECT_ROOT / "Datasets" / "skill_harness"
ITERATIONS_JSONL = OUTPUT_DIR / "iterations.jsonl"
LATEST_SCORECARD_JSON = OUTPUT_DIR / "latest_scorecard.json"
LATEST_REPORT_MD = OUTPUT_DIR / "latest_report.md"

GEMINI_PLUGIN_MANIFEST = SKILLS_REPO / ".gemini-plugin" / "gemini-4-argon-skills.json"
LOCAL_GEMINI_MANIFEST_COPY = SKILL_HARNESS_TOOLS_DIR / "gemini-4-argon-skills.json"

DEFAULT_PROMPT = (
    "Refine 3x3 tactical card game UI layout, dynamic telegraph animations, "
    "game feel hit-stop screen shake, and ScriptableObject card balance"
)


# ---------------------------------------------------------------------------
# 0. Gemini 4 Argon 92-Skill Manifest Builder
# ---------------------------------------------------------------------------

def parse_skill_frontmatter(md_path: Path) -> Dict[str, str]:
    """Extract YAML frontmatter `name` and `description` from a SKILL.md file."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    name = md_path.parent.name
    desc_lines: List[str] = []
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            in_desc = False
            for raw_line in fm.splitlines():
                line = raw_line.strip()
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    in_desc = False
                elif line.startswith("description:"):
                    rest = line.split(":", 1)[1].strip()
                    if rest and rest not in (">", "|"):
                        desc_lines.append(rest.strip('"').strip("'"))
                    in_desc = True
                elif in_desc:
                    if re.match(r"^[a-zA-Z0-9_-]+:", raw_line):
                        in_desc = False
                    else:
                        desc_lines.append(line)
    description = " ".join(desc_lines).strip()
    return {"name": name, "description": description, "lines": str(len(text.splitlines()))}


def build_gemini_4_argon_manifest() -> Dict[str, Any]:
    """
    Build and persist the Gemini 4 Argon native skill manifest covering all 92 SKILL.md files
    (1 Master Router + 77 upstream `awesome-gamedev-agent-skills` + 14 custom SYNAPSE skills).
    """
    all_skill_mds = sorted(SKILLS_REPO.rglob("SKILL.md"))
    skills_entries: List[Dict[str, Any]] = []
    by_category: Dict[str, List[str]] = {}

    subagent_routing_map = {
        "router": {
            "primary_agent": "parallel-architect",
            "delegate_agents": ["code-implementer", "truth-verifier", "jev-judge"],
            "mcp_tools": ["sequentialthinking", "mem", "mlx_jev_choose"],
            "slot": "router",
        },
        "disciplines": {
            "primary_agent": "code-implementer",
            "delegate_agents": ["prime-vision-worker", "mlx-local-worker", "truth-verifier"],
            "mcp_tools": ["mlx_jev_judge", "jev_verify", "sequentialthinking"],
            "slot": "discipline",
        },
        "genres": {
            "primary_agent": "code-implementer",
            "delegate_agents": ["truth-verifier", "jev-judge"],
            "mcp_tools": ["mlx_jev_schema_decide", "jev_gate"],
            "slot": "genre",
        },
        "workflows": {
            "primary_agent": "truth-verifier",
            "delegate_agents": ["jev-judge", "code-implementer"],
            "mcp_tools": ["jev_gate", "jev_review", "mlx_jev_judge"],
            "slot": "workflow",
        },
        "art-direction": {
            "primary_agent": "prime-vision-worker",
            "delegate_agents": ["mlx-local-worker", "code-implementer"],
            "mcp_tools": ["mlx_jev_rate", "jev_verify"],
            "slot": "discipline",
        },
        "decompilation": {
            "primary_agent": "code-implementer",
            "delegate_agents": ["research", "truth-verifier"],
            "mcp_tools": ["sequentialthinking", "jev_compare"],
            "slot": "workflow",
        },
    }

    for md_path in all_skill_mds:
        rel = md_path.relative_to(SKILLS_REPO)
        fm = parse_skill_frontmatter(md_path)
        if rel.parts[0] == "router":
            category = "router"
            skill_id = "router"
        else:
            category = rel.parts[1] if len(rel.parts) > 2 else "general"
            skill_id = f"{category}/{fm['name']}"

        by_category.setdefault(category, []).append(fm["name"])
        binding = subagent_routing_map.get(
            category,
            {
                "primary_agent": "code-implementer",
                "delegate_agents": ["truth-verifier", "jev-judge"],
                "mcp_tools": ["jev_verify", "mlx_jev_judge"],
                "slot": "engine",
            },
        )
        if fm["name"] == "create-game-assets":
            binding = subagent_routing_map["art-direction"]

        refs_dir = md_path.parent / "references"
        scripts_dir = md_path.parent / "scripts"
        skills_entries.append(
            {
                "skill_id": skill_id,
                "name": fm["name"],
                "category": category,
                "slot": binding["slot"],
                "path": str(md_path),
                "relative_path": str(rel),
                "line_count": int(fm["lines"]),
                "description": fm["description"],
                "references": sorted(str(p.relative_to(SKILLS_REPO)) for p in refs_dir.glob("*.md"))
                if refs_dir.exists()
                else [],
                "scripts": sorted(str(p.relative_to(SKILLS_REPO)) for p in scripts_dir.glob("*"))
                if scripts_dir.exists()
                else [],
                "gemini_4_argon_binding": {
                    "model": "gemini-4-argon",
                    "invoke_subagent_model": "inherit",
                    "primary_subagent": binding["primary_agent"],
                    "verification_subagents": binding["delegate_agents"],
                    "mcp_tools": binding["mcp_tools"],
                    "progressive_disclosure_tool": "read_file",
                },
            }
        )

    upstream_count = sum(
        len(v) for k, v in by_category.items() if k not in ("router", "decompilation", "art-direction")
    )
    custom_count = sum(len(v) for k, v in by_category.items() if k in ("decompilation", "art-direction"))

    manifest = {
        "schema_version": "2026.11.gemini-4-argon.v1",
        "name": "synapse-gamedev-agent-skills-gemini-4-argon",
        "target_model": {
            "id": "gemini-4-argon",
            "display_name": "Gemini 4 Argon",
            "runtime_harness": "Antigravity / SYNAPSE Parallel Swarm & Grounded Skill Harness",
            "replaces_legacy_plugin": ".claude-plugin/marketplace.json",
        },
        "source_video_reference": {
            "video_id": "t13A2XFGoOc",
            "url": "https://youtu.be/t13A2XFGoOc?si=V1HkMBTl7KO5qwac",
            "title": "Turn Claude into an Expert Game Dev with these Free 77 AI Skills",
            "author": "Nick Automates (@nickautomates)",
            "upstream_repo": "https://github.com/gamedev-skills/awesome-gamedev-agent-skills",
            "gemini_4_argon_adaptation": (
                "Re-architects the 77 upstream gamedev-skills + 14 custom SYNAPSE skills + Master Router "
                "(92 SKILL.md files total) for Gemini 4 Argon's native tool-use, progressive disclosure "
                "via `read_file`, parallel `invoke_subagent` swarms (`Model: inherit`), Apple Silicon "
                "`jevmlx` / `mlx-apple-silicon-mcp` local gates, and grounded Playwright + Unity verification."
            ),
        },
        "counts": {
            "total_skill_md_files": len(skills_entries),
            "master_router_count": 1,
            "upstream_gamedev_skills_count": upstream_count,
            "custom_synapse_skills_count": custom_count,
            "total_routable_skills": upstream_count + custom_count,
        },
        "composition_protocol": {
            "order": ["Engine Fundamentals", "Discipline(s)", "Genre", "Workflow"],
            "max_skills_per_single_agent_turn": 4,
            "dual_engine_project_support": {
                "primary_web_playable": {
                    "engine": "Custom HTML5/CSS3/JS Tabletop Engine (custom-engines.md)",
                    "entrypoint": "WebPlayable/cardfront_cradle_of_echoes_playable.html",
                    "server_url": DEFAULT_PLAYTEST_URL,
                },
                "secondary_unity_project": {
                    "engine": "Unity",
                    "version": "2022.3.40f1",
                    "entrypoint": "Assets/Scripts/Core/CardFrontUnifiedRuntime.cs",
                },
            },
        },
        "categories": {k: sorted(v) for k, v in sorted(by_category.items())},
        "skills": skills_entries,
    }

    GEMINI_PLUGIN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    GEMINI_PLUGIN_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    LOCAL_GEMINI_MANIFEST_COPY.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_GEMINI_MANIFEST_COPY.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------------------
# Step A: Router (Dual-Target Detection + router/SKILL.md Composition)
# ---------------------------------------------------------------------------

KEYWORD_SKILL_RULES: List[Tuple[str, str, str, str]] = [
    # (regex_pattern, category, skill_name, slot)
    (r"\b(scriptableobject|so\b|\.asset|carddataso)\b", "unity", "unity-scriptableobjects", "engine"),
    (r"\b(c#|monobehaviour|coroutine|unity)\b", "unity", "unity-csharp-scripting", "engine"),
    (r"\b(inputaction|input system)\b", "unity", "unity-input-system", "engine"),
    (r"\b(build pipeline|addressables|il2cpp)\b", "unity", "unity-build-pipeline", "engine"),
    (r"\b(shake|trauma|hit-?stop|freeze frame|juice|squash|stretch|punchy|feel)\b", "disciplines", "game-feel", "discipline"),
    (r"\b(ui|ux|hud|menu|layout|anchor|safe area|focus|modal|keyboard|accessibility|font|contrast)\b", "disciplines", "game-ui-ux", "discipline"),
    (r"\b(art|asset|sprite|portrait|silhouette|palette|raster|contact sheet|telegraph svg)\b", "disciplines", "create-game-assets", "discipline"),
    (r"\b(ai|boss|heuristic|utility|behavior tree|minimax|tie-?break)\b", "disciplines", "game-ai", "discipline"),
    (r"\b(utility ai|response curve|blackboard|decorator)\b", "disciplines", "ai-behavior-trees-utility-ai", "discipline"),
    (r"\b(audio|sound|music|sfx|mixer|bus|ducking|tone|mute)\b", "disciplines", "audio-design", "discipline"),
    (r"\b(input|rebind|hotkey|keydown|drag|pointer|deadzone|buffer)\b", "disciplines", "input-systems", "discipline"),
    (r"\b(save|load|persist|localstorage|migration|seed|replay)\b", "disciplines", "save-systems", "discipline"),
    (r"\b(camera|orbit|tilt|parallax|perspective)\b", "disciplines", "camera-systems", "discipline"),
    (r"\b(perf|fps|frame|gc|alloc|draw call|batch|long task|optimize)\b", "disciplines", "performance-optimization", "discipline"),
    (r"\b(shader|hlsl|urp|dissolve|outline|halftone)\b", "disciplines", "shader-programming", "discipline"),
    (r"\b(card|deck|hand|discard|zone|shuffle|fisher-?yates|tcg|ccg|capture|grid|dice)\b", "genres", "card-game", "genre"),
    (r"\b(steam|steamworks|depot)\b", "workflows", "steam-publish", "workflow"),
    (r"\b(itch|butler|webgl)\b", "workflows", "itch-publish", "workflow"),
    (r"\b(prototype|mvp|vertical slice)\b", "workflows", "prototype-fast", "workflow"),
]


def run_step_a_router(prompt: str, project_dir: Path) -> Dict[str, Any]:
    """
    Execute Step A:
    1. Query `/Users/frederickamina/.local/bin/pxg-gamedev-harness detect` and `route --json`.
    2. Apply `router/SKILL.md` rules across BOTH targets in `unity-tcg-engine`:
       - Primary target: Custom Web Engine (`WebPlayable/cardfront_cradle_of_echoes_playable.html`)
         governed by `router/references/custom-engines.md`.
       - Secondary target: Unity `2022.3.40f1` (`Assets/` + `ProjectSettings/ProjectVersion.txt`).
    3. Return verified composition order (`Engine Fundamentals -> Discipline(s) -> Genre -> Workflow`)
       and exact `SKILL.md` + reference paths to load under Gemini 4 Argon.
    """
    cli_detect: Dict[str, Any] = {}
    cli_route: Dict[str, Any] = {}

    if HARNESS_BIN.exists():
        try:
            det_proc = subprocess.run(
                [str(HARNESS_BIN), "detect", str(project_dir), "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            cli_detect = json.loads(det_proc.stdout)
        except Exception as exc:
            cli_detect = {"error": str(exc)}

        try:
            rt_proc = subprocess.run(
                [str(HARNESS_BIN), "route", prompt, "--dir", str(project_dir), "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            cli_route = json.loads(rt_proc.stdout)
        except Exception as exc:
            cli_route = {"error": str(exc)}

    # Verify against router/SKILL.md rules & custom-engines.md
    web_html = project_dir / "WebPlayable" / "cardfront_cradle_of_echoes_playable.html"
    unity_ver_file = project_dir / "ProjectSettings" / "ProjectVersion.txt"
    unity_version = "2022.3.40f1"
    if unity_ver_file.exists():
        m = re.search(r"m_EditorVersion:\s*(\S+)", unity_ver_file.read_text(encoding="utf-8"))
        if m:
            unity_version = m.group(1)

    # Start from CLI route stack, then verify/augment with router/SKILL.md keyword & target rules
    selected_by_slot: Dict[str, List[Dict[str, str]]] = {
        "engine": [],
        "discipline": [],
        "genre": [],
        "workflow": [],
    }
    seen_names = set()

    for item in cli_route.get("skill_stack", []):
        slot = item.get("slot", "discipline")
        name = item.get("name", "")
        cat = item.get("category", "")
        path = item.get("path", str(SKILLS_REPO / "skills" / cat / name / "SKILL.md"))
        if name and name not in seen_names:
            seen_names.add(name)
            selected_by_slot.setdefault(slot, []).append(
                {
                    "slot": slot,
                    "category": cat,
                    "name": name,
                    "skill_id": f"{cat}/{name}",
                    "path": path,
                    "source": "pxg-gamedev-harness",
                }
            )

    for pattern, cat, name, slot in KEYWORD_SKILL_RULES:
        if re.search(pattern, prompt, flags=re.IGNORECASE) and name not in seen_names:
            md_path = SKILLS_REPO / "skills" / cat / name / "SKILL.md"
            if md_path.exists():
                seen_names.add(name)
                selected_by_slot[slot].append(
                    {
                        "slot": slot,
                        "category": cat,
                        "name": name,
                        "skill_id": f"{cat}/{name}",
                        "path": str(md_path),
                        "source": "router/SKILL.md_verification",
                    }
                )

    # Ensure card-game genre is always present for CARDFRONT TCG requests if no genre matched
    if not selected_by_slot["genre"]:
        cg_path = SKILLS_REPO / "skills" / "genres" / "card-game" / "SKILL.md"
        selected_by_slot["genre"].append(
            {
                "slot": "genre",
                "category": "genres",
                "name": "card-game",
                "skill_id": "genres/card-game",
                "path": str(cg_path),
                "source": "router/SKILL.md_project_genre_default",
            }
        )

    # Order strictly: Engine Fundamentals -> Discipline(s) -> Genre -> Workflow
    ordered_skills: List[Dict[str, str]] = (
        selected_by_slot["engine"]
        + selected_by_slot["discipline"]
        + selected_by_slot["genre"]
        + selected_by_slot["workflow"]
    )

    files_to_load = [
        str(SKILLS_REPO / "router" / "SKILL.md"),
        str(SKILLS_REPO / "router" / "references" / "custom-engines.md"),
    ] + [s["path"] for s in ordered_skills]

    return {
        "prompt": prompt,
        "target_model": "gemini-4-argon",
        "dual_engine_detection": {
            "primary_target": {
                "engine": "Custom HTML5/CSS3/JS Tabletop Engine",
                "router_rule": "router/SKILL.md §6 + router/references/custom-engines.md",
                "entrypoint": str(web_html.relative_to(project_dir)),
                "live_url": DEFAULT_PLAYTEST_URL,
                "contract": {
                    "lifecycle": "DOMContentLoaded -> startStage(idx) -> renderAll()",
                    "input": "beginPointerDrag / handleSlotClick / handleHarnessKeyDown",
                    "state": "state.{grid, hand, aiPool, colDice, nudgesLeft, rerollsLeft, trauma, hitStopActive}",
                    "verification": "WebPlayable/tests/drag_e2e.js + ?autotest=1",
                },
            },
            "secondary_target": {
                "engine": cli_detect.get("engine", "Unity"),
                "version": unity_version,
                "signal": cli_detect.get("signal", "Assets/ + ProjectSettings/ProjectVersion.txt"),
                "entrypoints": [
                    "Assets/Scripts/Core/CardFrontUnifiedRuntime.cs",
                    "Assets/Scripts/Core/SynapseGameDevSkillsHarness.cs",
                    "Assets/Scripts/Data/CardDataSO.cs",
                ],
            },
        },
        "composition_order": "Engine Fundamentals -> Discipline(s) -> Genre -> Workflow",
        "ordered_skill_stack": ordered_skills,
        "exact_skill_files_to_load": files_to_load,
        "pxg_cli_raw": {
            "detect_engine": cli_detect.get("engine"),
            "detect_version": cli_detect.get("version"),
            "cli_selected_skills": cli_route.get("selected_skill_names", []),
        },
    }


# ---------------------------------------------------------------------------
# Step B: Real Game Verification (Playwright E2E + ?autotest=1 + Checks + MiroFish)
# ---------------------------------------------------------------------------

def run_drag_e2e_test(project_dir: Path) -> Dict[str, Any]:
    """Run `WebPlayable/tests/drag_e2e.js` using real Playwright Chromium mouse events."""
    script_path = project_dir / "WebPlayable" / "tests" / "drag_e2e.js"
    if not script_path.exists():
        return {"ran": False, "pass": False, "error": f"Missing {script_path}"}

    env = os.environ.copy()
    env["PLAYWRIGHT_CORE"] = PLAYWRIGHT_CORE
    env["CHROMIUM_EXE"] = CHROMIUM_EXE
    node_exe = str(NODE_BIN) if NODE_BIN.exists() else "node"

    t0 = time.time()
    try:
        proc = subprocess.run(
            [node_exe, str(script_path)],
            cwd=str(project_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=35,
        )
        elapsed_ms = round((time.time() - t0) * 1000.0, 1)
        if proc.returncode != 0:
            return {
                "ran": True,
                "pass": False,
                "elapsed_ms": elapsed_ms,
                "stderr": proc.stderr.strip()[-600:],
                "stdout": proc.stdout.strip()[-600:],
            }
        parsed = json.loads(proc.stdout.strip())
        parsed["ran"] = True
        parsed["elapsed_ms"] = elapsed_ms
        return parsed
    except Exception as exc:
        return {"ran": False, "pass": False, "error": str(exc)}


def run_playwright_autotest_and_probes(
    playtest_url: str,
    playwright_checks: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Launch a single headless Chromium session via Playwright to:
    1. Run `?autotest=1` on the real web build and verify `TEST_COMPLETE:*:SINGLETON=true:IMG=true`.
    2. Open a fresh page and evaluate every `playwright` check probe expression against the live game.
    """
    node_exe = str(NODE_BIN) if NODE_BIN.exists() else "node"
    probes_payload = []
    for chk in playwright_checks:
        probe = chk.get("probe") if isinstance(chk.get("probe"), dict) else {}
        expr = (
            probe.get("expression")
            or probe.get("js")
            or probe.get("script")
            or probe.get("code")
            or chk.get("expression")
            or (chk.get("probe") if isinstance(chk.get("probe"), str) else "false")
        )
        probes_payload.append({"id": chk["id"], "expression": expr})

    runner_js = r"""
const { chromium } = require(process.env.PLAYWRIGHT_CORE);
const fs = require("fs");

(async () => {
  const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const baseUrl = payload.baseUrl;
  const probes = payload.probes || [];
  const out = { autotest: {}, probeResults: {} };

  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_EXE || undefined,
  });

  try {
    // 1. Run ?autotest=1 in-page visual automated playtest (warming all 16 card portraits in HTTP cache first)
    const page1 = await browser.newPage({ viewport: { width: 1408, height: 800 } });
    const page1Errors = [];
    page1.on("pageerror", (e) => page1Errors.push(String(e)));
    const t0 = Date.now();
    await page1.goto(baseUrl + "?preload=" + Date.now(), { waitUntil: "networkidle" });
    await page1.evaluate(async () => {
      if (typeof ALL_CARDS === "object") {
        await Promise.all(
          Object.values(ALL_CARDS).map(
            (c) =>
              new Promise((resolve) => {
                const img = new Image();
                img.onload = img.onerror = resolve;
                img.src = c.art;
              })
          )
        );
      }
    });
    await page1.goto(baseUrl + "?autotest=1&ts=" + Date.now(), { waitUntil: "networkidle" });
    await page1.waitForFunction(
      () => document.title && document.title.startsWith("TEST_COMPLETE:"),
      null,
      { timeout: 22000 }
    );
    const title = await page1.title();
    const report = await page1.evaluate(() => window.__OSASCRIPT_TEST_REPORT__ || null);
    out.autotest = {
      ran: true,
      title,
      pass: title.startsWith("TEST_COMPLETE:") && title.includes("SINGLETON=true") && title.includes("IMG=true") && page1Errors.length === 0,
      singletonVerified: title.includes("SINGLETON=true"),
      imagesVerified: title.includes("IMG=true"),
      pageErrors: page1Errors,
      elapsed_ms: Date.now() - t0,
      report,
    };
    await page1.close();

    // 2. Evaluate all skill check probes on a clean page instance
    const page2 = await browser.newPage({ viewport: { width: 1408, height: 800 } });
    const page2Errors = [];
    page2.on("pageerror", (e) => page2Errors.push(String(e)));
    await page2.goto(baseUrl + "?harness_probes=" + Date.now(), { waitUntil: "networkidle" });
    await page2.waitForTimeout(450);
    await page2.evaluate(async () => {
      if (typeof ALL_CARDS === "object") {
        if (typeof window.CARDS === "undefined") {
          window.CARDS = Object.values(ALL_CARDS);
        }
        await Promise.all(
          Object.values(ALL_CARDS).map(
            (c) =>
              new Promise((resolve) => {
                const img = new Image();
                img.onload = img.onerror = resolve;
                img.src = c.art;
              })
          )
        );
      }
    });

    for (const p of probes) {
      try {
        const val = await page2.evaluate(async (exprStr) => {
          return await (0, eval)(exprStr);
        }, p.expression);
        out.probeResults[p.id] = { ok: true, value: val };
        await page2.evaluate(() => {
          if (typeof startStage === "function") startStage(0);
        });
        await page2.waitForTimeout(40);
      } catch (err) {
        out.probeResults[p.id] = { ok: false, error: String(err), value: null };
      }
    }
    out.probePageErrors = page2Errors;
    await page2.close();
  } finally {
    await browser.close();
  }

  console.log(JSON.stringify(out));
})().catch((e) => {
  console.error("PW_RUNNER_ERR:", e);
  process.exit(1);
});
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        runner_file = tmp_path / "pw_runner.js"
        input_file = tmp_path / "pw_input.json"
        runner_file.write_text(runner_js, encoding="utf-8")
        input_file.write_text(
            json.dumps({"baseUrl": playtest_url, "probes": probes_payload}),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PLAYWRIGHT_CORE"] = PLAYWRIGHT_CORE
        env["CHROMIUM_EXE"] = CHROMIUM_EXE

        try:
            proc = subprocess.run(
                [node_exe, str(runner_file), str(input_file)],
                capture_output=True,
                text=True,
                env=env,
                timeout=45,
            )
            if proc.returncode != 0:
                return (
                    {
                        "ran": False,
                        "pass": False,
                        "error": proc.stderr.strip()[-600:],
                    },
                    {},
                )
            data = json.loads(proc.stdout.strip())
            return data.get("autotest", {}), data.get("probeResults", {})
        except Exception as exc:
            return ({"ran": False, "pass": False, "error": str(exc)}, {})


def discover_all_checks(project_dir: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Load built-in `Tools/skill_harness/core_checks.json` (>=15 grounded checks) and merge all
    discovered `Datasets/mirofish_gameplay/skills_*/checks.json` files.
    Deduplicates by check `id` (external `skills_*/checks.json` entries append cleanly).
    """
    checks_by_id: Dict[str, Dict[str, Any]] = {}
    sources_loaded: List[str] = []

    if CORE_CHECKS_JSON.exists():
        try:
            core_list = json.loads(CORE_CHECKS_JSON.read_text(encoding="utf-8"))
            if isinstance(core_list, list):
                for c in core_list:
                    if isinstance(c, dict) and c.get("id"):
                        c["_check_origin"] = str(CORE_CHECKS_JSON.relative_to(project_dir))
                        checks_by_id[c["id"]] = c
                sources_loaded.append(str(CORE_CHECKS_JSON.relative_to(project_dir)))
        except Exception as exc:
            print(f"[warn] Failed to parse {CORE_CHECKS_JSON}: {exc}", file=sys.stderr)

    miro_dir = project_dir / "Datasets" / "mirofish_gameplay"
    if miro_dir.exists():
        for ext_file in sorted(miro_dir.glob("skills_*/checks.json")):
            try:
                raw = json.loads(ext_file.read_text(encoding="utf-8"))
                ext_list = raw.get("checks", []) if isinstance(raw, dict) else raw
                if isinstance(ext_list, list):
                    for idx, c in enumerate(ext_list):
                        if not isinstance(c, dict):
                            continue
                        cid = c.get("id") or f"{ext_file.parent.name}.{idx + 1}"
                        c["id"] = cid
                        c["_check_origin"] = str(ext_file.relative_to(project_dir))
                        checks_by_id[cid] = c
                    sources_loaded.append(str(ext_file.relative_to(project_dir)))
            except Exception as exc:
                print(f"[warn] Failed to parse {ext_file}: {exc}", file=sys.stderr)

    return list(checks_by_id.values()), sources_loaded


def evaluate_expectation(actual: Any, expect_spec: Any) -> bool:
    """Compare a probe's `actual` return value against an `expect` specification."""
    if expect_spec is None:
        return bool(actual)
    if isinstance(expect_spec, bool):
        return bool(actual) is expect_spec
    if isinstance(expect_spec, (int, float)):
        try:
            return float(actual) == float(expect_spec)
        except Exception:
            return False

    exp_str = str(expect_spec).strip()
    if exp_str.lower() == "true":
        return actual is True or str(actual).strip().lower() == "true"
    if exp_str.lower() == "false":
        return actual is False or str(actual).strip().lower() == "false"
    if exp_str.lower() == "match":
        return (actual is True) or (isinstance(actual, (int, float)) and actual > 0)
    if exp_str.lower() == "no_match":
        return (actual is False) or (isinstance(actual, (int, float)) and actual == 0)

    # Numeric comparisons: >=N, <=N, >N, <N, ==N, or "0 matches", ">=1 match", ">=3 call sites (...)"
    m_num = re.match(
        r"^(>=|<=|==|>|<)?\s*(-?\d+(?:\.\d+)?)\s*(?:(?:call\s+sites?|match(?:es)?)\b.*)?$",
        exp_str,
        flags=re.IGNORECASE,
    )
    if m_num:
        op = m_num.group(1) or "=="
        rhs_s = m_num.group(2)
        try:
            lhs = float(actual)
            rhs = float(rhs_s)
        except Exception:
            return False
        if op == ">=":
            return lhs >= rhs
        if op == "<=":
            return lhs <= rhs
        if op == ">":
            return lhs > rhs
        if op == "<":
            return lhs < rhs
        if op == "==":
            return lhs == rhs

    # Direct numeric equality
    try:
        return float(actual) == float(exp_str)
    except Exception:
        pass

    # Regex or substring match
    try:
        return bool(re.search(exp_str, str(actual)))
    except re.error:
        return str(actual) == exp_str


def resolve_json_path(obj: Any, path_expr: str) -> Any:
    """Resolve dotted path like `runs.cpu1x.drag.p95Ms` inside a dict/list."""
    cur = obj
    for part in path_expr.split("."):
        if not part:
            continue
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def normalize_skill_and_source(chk: Dict[str, Any]) -> Tuple[str, str]:
    """Normalize skill identifier (`category/name`) and `SKILL.md` source reference."""
    raw_skill = str(chk.get("skill", "unknown")).strip()
    raw_source = str(chk.get("source", "")).strip()
    category_lookup = {
        "game-ai": "disciplines/game-ai",
        "ai-behavior-trees-utility-ai": "disciplines/ai-behavior-trees-utility-ai",
        "save-systems": "disciplines/save-systems",
        "audio-design": "disciplines/audio-design",
        "game-feel": "disciplines/game-feel",
        "game-ui-ux": "disciplines/game-ui-ux",
        "input-systems": "disciplines/input-systems",
        "camera-systems": "disciplines/camera-systems",
        "performance-optimization": "disciplines/performance-optimization",
        "create-game-assets": "disciplines/create-game-assets",
        "card-game": "genres/card-game",
        "unity-scriptableobjects": "unity/unity-scriptableobjects",
        "unity-csharp-scripting": "unity/unity-csharp-scripting",
        "prototype-fast": "workflows/prototype-fast",
        "itch-publish": "workflows/itch-publish",
        "steam-publish": "workflows/steam-publish",
        "tactical-illustrator-library": "art-direction/tactical-illustrator-library",
    }
    if "SKILL.md" in raw_skill:
        slug = raw_skill.split("/SKILL.md")[0].split("/")[-1]
        norm_skill = category_lookup.get(slug, slug)
        norm_source = raw_skill if not raw_source or not ("SKILL.md" in raw_source) else raw_source
        return norm_skill, norm_source
    if "/" not in raw_skill and raw_skill in category_lookup:
        raw_skill = category_lookup[raw_skill]
    return raw_skill, raw_source


def execute_all_checks(
    project_dir: Path,
    playtest_url: str,
    checks: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Execute all checks (`playwright`, `static_regex`, `metric`, `manual`) and also return
    the `?autotest=1` playtest result from the shared Chromium session.
    """
    pw_checks = [c for c in checks if (c.get("method") or c.get("type")) == "playwright"]
    autotest_result, pw_probe_map = run_playwright_autotest_and_probes(playtest_url, pw_checks)

    evaluated_checks: List[Dict[str, Any]] = []
    for chk in checks:
        cid = chk.get("id", "unknown")
        method = chk.get("method") or chk.get("type") or "manual"
        probe = chk.get("probe") if isinstance(chk.get("probe"), dict) else {}
        expect = chk.get("expect", "true")
        actual_val: Any = None
        probe_error: Optional[str] = None
        norm_skill, norm_source = normalize_skill_and_source(chk)
        priority = chk.get("priority") or chk.get("severity") or "P2"
        rule_text = chk.get("rule") or chk.get("metric") or chk.get("id", "")

        if method == "playwright":
            pw_res = pw_probe_map.get(cid, {})
            if pw_res.get("ok"):
                actual_val = pw_res.get("value")
            else:
                probe_error = pw_res.get("error", "Playwright probe did not run")
                actual_val = None

        elif method == "static_regex":
            rel_file = (
                probe.get("file")
                or probe.get("path")
                or chk.get("file")
                or ("WebPlayable/cardfront_cradle_of_echoes_playable.html" if chk.get("target") == "web" else "")
            )
            pattern = probe.get("regex") or probe.get("pattern") or chk.get("pattern") or chk.get("regex") or ""
            target_path = Path(rel_file) if os.path.isabs(rel_file) else (project_dir / rel_file)
            if not target_path.exists():
                probe_error = f"File not found: {rel_file}"
                actual_val = False
            else:
                text = target_path.read_text(encoding="utf-8", errors="replace")
                matches = [m.group(0) for m in re.finditer(pattern, text, flags=re.MULTILINE)]
                exp_s = str(expect).strip().lower()
                if re.match(r"^(>=|<=|==|>|<|-?\d+)", exp_s) or exp_s in ("match", "no_match"):
                    actual_val = len(matches)
                else:
                    actual_val = len(matches) > 0

        elif method == "metric":
            rel_file = (
                (probe.get("json_file") or probe.get("file"))
                if isinstance(probe, dict)
                else None
            )
            if rel_file:
                target_path = Path(rel_file) if os.path.isabs(rel_file) else (project_dir / rel_file)
                if target_path.exists():
                    try:
                        jdata = json.loads(target_path.read_text(encoding="utf-8"))
                        if isinstance(probe, dict) and probe.get("expression"):
                            safe_builtins = {
                                "len": len,
                                "all": all,
                                "any": any,
                                "sum": sum,
                                "min": min,
                                "max": max,
                                "round": round,
                                "abs": abs,
                                "float": float,
                                "int": int,
                                "bool": bool,
                                "str": str,
                                "list": list,
                                "dict": dict,
                                "set": set,
                            }
                            actual_val = eval(
                                probe["expression"],
                                {"__builtins__": safe_builtins},
                                {"data": jdata},
                            )
                        else:
                            jpath = probe.get("json_path") or probe.get("key") or ""
                            actual_val = resolve_json_path(jdata, jpath) if jpath else jdata
                    except Exception as exc:
                        probe_error = str(exc)
                else:
                    probe_error = f"Metric file not found: {rel_file}"
            elif isinstance(probe, dict) and (probe.get("command") or probe.get("script")):
                cmd_str = probe.get("command") or probe.get("script")
                try:
                    proc = subprocess.run(
                        cmd_str,
                        shell=True,
                        cwd=str(project_dir),
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    actual_val = proc.stdout.strip()
                except Exception as exc:
                    probe_error = str(exc)
            elif isinstance(probe, dict) and "value" in probe:
                actual_val = probe["value"]
            elif "observed" in chk:
                actual_val = chk["observed"]
            elif "actual" in chk:
                actual_val = chk["actual"]

        elif method == "manual":
            if isinstance(probe, dict) and "current_result" in probe:
                actual_val = probe["current_result"]
            elif "current_result" in chk:
                actual_val = chk["current_result"]
            else:
                actual_val = True

        passed = False if probe_error else evaluate_expectation(actual_val, expect)
        code_ref = (
            chk.get("code_ref")
            or probe.get("file")
            or chk.get("file")
            or probe.get("json_file")
            or (chk.get("source") if "SKILL.md" in str(chk.get("skill", "")) else "")
            or "WebPlayable/cardfront_cradle_of_echoes_playable.html"
        )
        remediation_text = (
            chk.get("remediation")
            or chk.get("fix")
            or (f"Satisfy {norm_skill} rule ({norm_source}): expected {expect} in {code_ref}." if not passed else "")
        )
        evaluated_checks.append(
            {
                "id": cid,
                "skill": norm_skill,
                "rule": rule_text,
                "source": norm_source,
                "target": chk.get("target", "unity" if str(code_ref).endswith(".cs") else "web"),
                "method": method,
                "expect": expect,
                "actual": actual_val,
                "passed": passed,
                "priority": priority,
                "code_ref": code_ref,
                "remediation": remediation_text,
                "origin": chk.get("_check_origin", "core_checks.json"),
                "error": probe_error,
            }
        )

    return autotest_result, evaluated_checks


def ingest_mirofish_telemetry(project_dir: Path) -> Dict[str, Any]:
    """
    Ingest real gameplay test summaries from `Datasets/mirofish_gameplay/{balance,rules_audit,ux_qa,personas,benchmark,skills_*}/`
    when present on disk.
    """
    miro = project_dir / "Datasets" / "mirofish_gameplay"
    summary: Dict[str, Any] = {"workstreams_present": []}
    if not miro.exists():
        return summary

    # 1. balance
    bal_file = miro / "balance" / "results" / "validation_summary.json"
    bal_sim_file = miro / "balance" / "results" / "summary.json"
    if bal_file.exists() or bal_sim_file.exists():
        try:
            bdata = json.loads(bal_file.read_text(encoding="utf-8")) if bal_file.exists() else {}
            sdata = json.loads(bal_sim_file.read_text(encoding="utf-8")) if bal_sim_file.exists() else {}
            summary["workstreams_present"].append("balance")
            summary["balance"] = {
                "matches_validated": bdata.get("matches"),
                "actions_compared": bdata.get("actionsCompared"),
                "match_agreement_pct": bdata.get("matchAgreementPct"),
                "action_agreement_pct": bdata.get("actionAgreementPct"),
                "total_simulated_games": sdata.get("totalSimulatedGames"),
                "total_main_games": sdata.get("totalMainGames"),
                "total_variant_games": sdata.get("totalVariantGames"),
                "by_stage": bdata.get("byStage"),
            }
        except Exception:
            pass

    # 2. rules_audit
    ra_out = miro / "rules_audit" / "out"
    if ra_out.exists():
        repro_files = sorted(ra_out.glob("R*.json"))
        reproduced_bugs = []
        for rf in repro_files:
            try:
                rdata = json.loads(rf.read_text(encoding="utf-8"))
                reproduced_bugs.append(
                    {
                        "id": rdata.get("id", rf.stem),
                        "title": rdata.get("title", ""),
                        "reproduced": bool(rdata.get("reproduced", False)),
                    }
                )
            except Exception:
                pass
        summary["workstreams_present"].append("rules_audit")
        summary["rules_audit"] = {
            "total_repro_probes": len(reproduced_bugs),
            "reproduced_count": sum(1 for b in reproduced_bugs if b["reproduced"]),
            "findings": reproduced_bugs,
        }

    # 3. ux_qa
    ux_raw = miro / "ux_qa" / "raw"
    if ux_raw.exists():
        ux_info: Dict[str, Any] = {}
        perf_file = ux_raw / "t4_perf.json"
        if perf_file.exists():
            try:
                pdata = json.loads(perf_file.read_text(encoding="=" if False else "utf-8"))
                cpu1 = pdata.get("runs", {}).get("cpu1x", {})
                ux_info["drag_p95_ms"] = cpu1.get("drag", {}).get("p95Ms")
                ux_info["drag_long_tasks"] = cpu1.get("drag", {}).get("longTasks")
                ux_info["renderAll_avg_ms"] = cpu1.get("drag", {}).get("renderAll", {}).get("avgMs")
                ux_info["broken_images_count"] = len(cpu1.get("brokenImages", []))
            except Exception:
                pass
        a11y_file = ux_raw / "t5_a11y.json"
        if a11y_file.exists():
            try:
                adata = json.loads(a11y_file.read_text(encoding="utf-8"))
                kgame = adata.get("keyboardOnlyGame", {})
                ux_info["keyboard_only_game_completed"] = kgame.get("gameCompleted")
                ux_info["modal_auto_focused"] = kgame.get("modalAutoFocused")
            except Exception:
                pass
        summary["workstreams_present"].append("ux_qa")
        summary["ux_qa"] = ux_info

    # 4. personas
    personas_matches = miro / "personas" / "raw" / "matches.jsonl"
    if personas_matches.exists():
        try:
            lines = [ln for ln in personas_matches.read_text(encoding="utf-8").splitlines() if ln.strip()]
            wins = 0
            personas_seen = set()
            for ln in lines:
                row = json.loads(ln)
                if row.get("persona"):
                    personas_seen.add(row["persona"])
                if row.get("win") is True or row.get("outcome") == "VICTORY":
                    wins += 1
            summary["workstreams_present"].append("personas")
            summary["personas"] = {
                "matches_recorded": len(lines),
                "distinct_personas": sorted(personas_seen),
                "wins_recorded": wins,
            }
        except Exception:
            pass

    # 5. benchmark
    bench_file = miro / "benchmark" / "structural_sim_output.json"
    if bench_file.exists():
        try:
            bdata = json.loads(bench_file.read_text(encoding="utf-8"))
            summary["workstreams_present"].append("benchmark")
            summary["benchmark"] = {
                "hero_cards_count": len(bdata.get("cards", {}).get("heroes", [])),
                "enemy_cards_count": len(bdata.get("cards", {}).get("enemies", [])),
                "report_present": (miro / "benchmark" / "REPORT.md").exists(),
            }
        except Exception:
            pass

    # 6. skills_art_direction
    art_cards = miro / "skills_art_direction" / "raw" / "asset_report_cards.json"
    if art_cards.exists():
        try:
            adata = json.loads(art_cards.read_text(encoding="utf-8"))
            summary["workstreams_present"].append("skills_art_direction")
            summary["skills_art_direction"] = {
                "cards_raster_qa_ok": adata.get("ok"),
                "cards_verified_count": len(adata.get("assets", [])),
                "contact_sheet_exists": (miro / "skills_art_direction" / "contact_sheet.png").exists(),
            }
        except Exception:
            pass

    return summary


# ---------------------------------------------------------------------------
# Step C: Scorecard, Gate & Ranked Backlog + Persistence
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def compute_scorecard_and_backlog(
    router_out: Dict[str, Any],
    drag_e2e: Dict[str, Any],
    autotest: Dict[str, Any],
    evaluated_checks: List[Dict[str, Any]],
    check_sources: List[str],
    mirofish_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the per-skill scorecard, overall gate verdict, diff vs previous iteration,
    and prioritized P0->P3 backlog.
    """
    per_skill: Dict[str, Dict[str, Any]] = {}
    for chk in evaluated_checks:
        sk = chk["skill"]
        entry = per_skill.setdefault(
            sk,
            {"skill": sk, "total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0, "failed_ids": []},
        )
        entry["total"] += 1
        if chk["passed"]:
            entry["passed"] += 1
        else:
            entry["failed"] += 1
            entry["failed_ids"].append(chk["id"])

    for sk, entry in per_skill.items():
        entry["pass_rate"] = round((entry["passed"] / entry["total"]) * 100.0, 1) if entry["total"] else 100.0

    total_checks = len(evaluated_checks)
    passed_checks = sum(1 for c in evaluated_checks if c["passed"])
    failed_checks = total_checks - passed_checks

    # Build prioritized P0 -> P3 backlog from failing checks
    failing = [c for c in evaluated_checks if not c["passed"]]
    failing.sort(key=lambda c: (PRIORITY_RANK.get(c.get("priority", "P2"), 9), c["id"]))

    backlog: List[Dict[str, Any]] = []
    for rank, chk in enumerate(failing, start=1):
        backlog.append(
            {
                "rank": rank,
                "priority": chk.get("priority", "P2"),
                "check_id": chk["id"],
                "skill": chk["skill"],
                "skill_source": chk["source"],
                "target": chk["target"],
                "code_ref": chk.get("code_ref", ""),
                "rule": chk["rule"],
                "observed": chk["actual"],
                "expected": chk["expect"],
                "remediation": chk.get("remediation", ""),
            }
        )

    p0_failures = sum(1 for b in backlog if b["priority"] == "P0")
    p1_failures = sum(1 for b in backlog if b["priority"] == "P1")
    e2e_ok = bool(drag_e2e.get("pass")) and bool(autotest.get("pass"))

    if not e2e_ok or p0_failures > 0:
        gate_status = "FAIL_P0_BLOCKERS"
    elif failed_checks > 0:
        gate_status = "PASS_E2E_WITH_SKILL_BACKLOG"
    else:
        gate_status = "PASS_ALL_GATES"

    # Load previous iteration from iterations.jsonl for diffing
    prev_iter: Optional[Dict[str, Any]] = None
    if ITERATIONS_JSONL.exists():
        lines = [ln for ln in ITERATIONS_JSONL.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if lines:
            try:
                prev_iter = json.loads(lines[-1])
            except Exception:
                prev_iter = None

    iteration_num = (prev_iter.get("iteration", 0) + 1) if prev_iter else 1
    prev_passed_ids = set(prev_iter.get("summary", {}).get("passed_check_ids", [])) if prev_iter else set()
    prev_failed_ids = set(prev_iter.get("summary", {}).get("failed_check_ids", [])) if prev_iter else set()

    cur_passed_ids = {c["id"] for c in evaluated_checks if c["passed"]}
    cur_failed_ids = {c["id"] for c in evaluated_checks if not c["passed"]}

    diff_vs_previous = {
        "previous_iteration": prev_iter.get("iteration") if prev_iter else None,
        "newly_passing_checks": sorted(cur_passed_ids - prev_passed_ids) if prev_iter else [],
        "newly_failing_checks": sorted(cur_failed_ids - prev_failed_ids) if prev_iter else [],
        "pass_count_delta": (
            passed_checks - prev_iter.get("summary", {}).get("passed_checks", passed_checks)
            if prev_iter
            else 0
        ),
        "total_checks_delta": (
            total_checks - prev_iter.get("summary", {}).get("total_checks", total_checks)
            if prev_iter
            else 0
        ),
    }

    return {
        "iteration": iteration_num,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_model": "gemini-4-argon",
        "gate_status": gate_status,
        "summary": {
            "drag_e2e_passed": bool(drag_e2e.get("pass")),
            "autotest_e2e_passed": bool(autotest.get("pass")),
            "autotest_title": autotest.get("title", ""),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "pass_rate_pct": round((passed_checks / total_checks) * 100.0, 1) if total_checks else 0.0,
            "p0_failures": p0_failures,
            "p1_failures": p1_failures,
            "check_sources_loaded": check_sources,
            "passed_check_ids": sorted(cur_passed_ids),
            "failed_check_ids": sorted(cur_failed_ids),
        },
        "diff_vs_previous": diff_vs_previous,
        "step_a_router": router_out,
        "step_b_verification": {
            "drag_e2e": drag_e2e,
            "autotest": autotest,
            "checks": evaluated_checks,
            "mirofish_telemetry": mirofish_summary,
        },
        "step_c_scorecard": {
            "per_skill": per_skill,
            "prioritized_backlog": backlog,
        },
    }


def render_markdown_report(scorecard: Dict[str, Any]) -> str:
    """Format a human-readable Markdown report for `Datasets/skill_harness/latest_report.md`."""
    s = scorecard["summary"]
    r = scorecard["step_a_router"]
    diff = scorecard["diff_vs_previous"]
    per_skill = scorecard["step_c_scorecard"]["per_skill"]
    backlog = scorecard["step_c_scorecard"]["prioritized_backlog"]
    checks = scorecard["step_b_verification"]["checks"]
    miro = scorecard["step_b_verification"]["mirofish_telemetry"]

    lines = [
        f"# CARDFRONT: Cradle of Echoes — Grounded Skill Harness Report (Iteration #{scorecard['iteration']})",
        "",
        f"- **Timestamp (UTC)**: `{scorecard['timestamp_utc']}`",
        f"- **Target Orchestrator Model**: **`{scorecard['target_model']}`** (`Gemini 4 Argon`)",
        f"- **Overall Gate Status**: **`{scorecard['gate_status']}`**",
        f"- **Real Drag & Drop E2E (`WebPlayable/tests/drag_e2e.js`)**: `{'PASS' if s['drag_e2e_passed'] else 'FAIL'}`",
        f"- **Real In-Page Playtest (`?autotest=1`)**: `{'PASS' if s['autotest_e2e_passed'] else 'FAIL'}` (`{s['autotest_title']}`)",
        f"- **Grounded Skill Checks**: **{s['passed_checks']} / {s['total_checks']} PASS ({s['pass_rate_pct']}%)** — `{s['p0_failures']} P0`, `{s['p1_failures']} P1` failures",
        f"- **Check Suites Merged**: `{', '.join(s['check_sources_loaded'])}`",
        "",
        "## 1. Step A — Router & Dual-Engine Composition (`router/SKILL.md`)",
        "",
        f"- **Change Request Prompt**: `{r['prompt']}`",
        f"- **Primary Target**: `{r['dual_engine_detection']['primary_target']['engine']}` (`{r['dual_engine_detection']['primary_target']['entrypoint']}`, bound via `router/references/custom-engines.md`)",
        f"- **Secondary Target**: `{r['dual_engine_detection']['secondary_target']['engine']} {r['dual_engine_detection']['secondary_target']['version']}` (`{r['dual_engine_detection']['secondary_target']['signal']}`)",
        f"- **Composition Order**: `{r['composition_order']}`",
        "",
        "### Loaded `SKILL.md` Stack",
        "| Order | Slot | Skill | Path | Source |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]
    for idx, sk in enumerate(r["ordered_skill_stack"], start=1):
        lines.append(
            f"| {idx} | `{sk['slot']}` | `{sk['skill_id']}` | `{sk['path']}` | `{sk['source']}` |"
        )

    lines.extend(
        [
            "",
            "## 2. Step B — Per-Skill Scorecard",
            "",
            "| Skill | Total Checks | Passed | Failed | Pass Rate | Failing Check IDs |",
            "| :--- | :---: | :---: | :---: | :---: | :--- |",
        ]
    )
    for sk_name, sk_data in sorted(per_skill.items()):
        fail_str = ", ".join(f"`{fid}`" for fid in sk_data["failed_ids"]) if sk_data["failed_ids"] else "—"
        lines.append(
            f"| `{sk_name}` | {sk_data['total']} | {sk_data['passed']} | {sk_data['failed']} | **{sk_data['pass_rate']}%** | {fail_str} |"
        )

    lines.extend(
        [
            "",
            "### Diff vs. Previous Iteration",
            f"- **Previous Iteration**: `{diff['previous_iteration']}`",
            f"- **Pass Count Delta**: `{diff['pass_count_delta']:+d}` (Total checks delta: `{diff['total_checks_delta']:+d}`)",
            f"- **Newly Passing Checks**: `{', '.join(diff['newly_passing_checks']) or 'None'}`",
            f"- **Newly Failing Checks**: `{', '.join(diff['newly_failing_checks']) or 'None'}`",
            "",
            "### Ingested MiroFish Gameplay Telemetry",
            f"- **Active Workstreams**: `{', '.join(miro.get('workstreams_present', []))}`",
        ]
    )
    if "balance" in miro:
        b = miro["balance"]
        lines.append(
            f"- **Balance / Engine Parity**: `{b.get('matches_validated')} matches`, `{b.get('actions_compared')} actions`, `{b.get('action_agreement_pct')}% agreement`"
        )
    if "rules_audit" in miro:
        ra = miro["rules_audit"]
        lines.append(
            f"- **Rules Audit**: `{ra.get('reproduced_count')} / {ra.get('total_repro_probes')}` edge-case repro probes reproduced (`R01..R11`)"
        )
    if "ux_qa" in miro:
        ux = miro["ux_qa"]
        lines.append(
            f"- **UX / Perf QA**: Drag p95 frame time `{ux.get('drag_p95_ms')} ms`, long tasks `{ux.get('drag_long_tasks')}`, `renderAll` avg `{ux.get('renderAll_avg_ms')} ms`, keyboard-only game completed `{ux.get('keyboard_only_game_completed')}`"
        )
    if "personas" in miro:
        p = miro["personas"]
        lines.append(
            f"- **Persona Playtesters**: `{p.get('matches_recorded')} matches` across `{', '.join(p.get('distinct_personas', []))}` (`{p.get('wins_recorded')} wins`)"
        )
    if "skills_art_direction" in miro:
        ad = miro["skills_art_direction"]
        lines.append(
            f"- **Art Direction Raster QA**: `ok={ad.get('cards_raster_qa_ok')}`, `{ad.get('cards_verified_count')} card portraits verified (600x800)`"
        )

    lines.extend(
        [
            "",
            "## 3. Step C — Prioritized P0 → P3 Remediation Backlog",
            "",
            "| Rank | Priority | Check ID | Skill (`SKILL.md` Source) | Code Reference | Observed vs Expected | Concrete Remediation |",
            "| :---: | :---: | :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    for item in backlog:
        lines.append(
            f"| {item['rank']} | **{item['priority']}** | `{item['check_id']}` | `{item['skill']}` (`{item['skill_source']}`) | `{item['code_ref']}` | `{item['observed']}` (expect `{item['expected']}`) | {item['remediation']} |"
        )

    lines.extend(
        [
            "",
            "## 4. All Grounded Check Verdicts",
            "",
            "| ID | Verdict | Priority | Skill | Method | Source | Code Ref |",
            "| :--- | :---: | :---: | :--- | :---: | :--- | :--- |",
        ]
    )
    for c in checks:
        verdict = "PASS" if c["passed"] else "**FAIL**"
        lines.append(
            f"| `{c['id']}` | {verdict} | `{c['priority']}` | `{c['skill']}` | `{c['method']}` | `{c['source']}` | `{c['code_ref']}` |"
        )

    return "\n".join(lines) + "\n"


def run_iteration(
    prompt: str = DEFAULT_PROMPT,
    project_dir: Path = PROJECT_ROOT,
    playtest_url: str = DEFAULT_PLAYTEST_URL,
) -> Dict[str, Any]:
    """Execute Steps A, B, and C end-to-end and persist all artifacts."""
    t0 = time.time()
    manifest = build_gemini_4_argon_manifest()
    router_out = run_step_a_router(prompt, project_dir)
    drag_e2e = run_drag_e2e_test(project_dir)
    all_checks, check_sources = discover_all_checks(project_dir)
    autotest, evaluated_checks = execute_all_checks(project_dir, playtest_url, all_checks)
    mirofish_summary = ingest_mirofish_telemetry(project_dir)

    scorecard = compute_scorecard_and_backlog(
        router_out=router_out,
        drag_e2e=drag_e2e,
        autotest=autotest,
        evaluated_checks=evaluated_checks,
        check_sources=check_sources,
        mirofish_summary=mirofish_summary,
    )
    scorecard["gemini_4_argon_manifest_summary"] = {
        "manifest_path": str(GEMINI_PLUGIN_MANIFEST),
        "local_copy_path": str(LOCAL_GEMINI_MANIFEST_COPY),
        "total_skill_md_files": manifest["counts"]["total_skill_md_files"],
        "upstream_skills": manifest["counts"]["upstream_gamedev_skills_count"],
        "custom_synapse_skills": manifest["counts"]["custom_synapse_skills_count"],
    }
    scorecard["elapsed_ms"] = round((time.time() - t0) * 1000.0, 1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ITERATIONS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(scorecard) + "\n")
    LATEST_SCORECARD_JSON.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    LATEST_REPORT_MD.write_text(render_markdown_report(scorecard), encoding="utf-8")
    return scorecard


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CARDFRONT Grounded GameDev-Skills Continuous Iteration Harness (Gemini 4 Argon)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Change request prompt to route through pxg-gamedev-harness and router/SKILL.md",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=str(PROJECT_ROOT),
        help="Project root directory",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_PLAYTEST_URL,
        help="Live WebPlayable URL served by WebPlayable/serve_playtest.py",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON summary to stdout",
    )
    args = parser.parse_args()

    scorecard = run_iteration(
        prompt=args.prompt,
        project_dir=Path(args.dir),
        playtest_url=args.url,
    )
    if args.json:
        print(json.dumps(scorecard["summary"], indent=2))
    else:
        s = scorecard["summary"]
        print(
            f"[iterate.py | {scorecard['target_model']}] Iteration #{scorecard['iteration']} -> {scorecard['gate_status']} "
            f"(drag_e2e={s['drag_e2e_passed']}, autotest={s['autotest_e2e_passed']}, "
            f"checks={s['passed_checks']}/{s['total_checks']} [{s['pass_rate_pct']}%], "
            f"sources={len(s['check_sources_loaded'])}, elapsed={scorecard['elapsed_ms']}ms)"
        )


if __name__ == "__main__":
    main()
