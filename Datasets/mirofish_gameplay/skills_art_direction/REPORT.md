# Art Direction & Asset Cohesion Audit — `CARDFRONT: Cradle of Echoes`
**Adapted for Gemini 4 Argon (`gemini-4-argon`) + Antigravity Subagent Harness**

- **Target Web Playable (Read-Only):** [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Target Unity C# Runtime (Read-Only):** [`Assets/Scripts/Core/CardFrontUnifiedRuntime.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Core/CardFrontUnifiedRuntime.cs) & [`Assets/Scripts/Visuals/SynapseIllustratorStyleLibrary.cs`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Assets/Scripts/Visuals/SynapseIllustratorStyleLibrary.cs)
- **Loaded Skills:**
  1. [`skills/disciplines/create-game-assets/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/disciplines/create-game-assets/SKILL.md) (+ `references/art-direction.md`, `references/raster-pipeline.md`, `references/provenance.md`)
  2. [`skills/art-direction/tactical-illustrator-library/SKILL.md`](file:///Users/frederickamina/.prime/agent/harness/gamedev_skills/skills/art-direction/tactical-illustrator-library/SKILL.md) (SYNAPSE custom extension)
- **Quantitative Evidence Artifacts Generated:**
  - [`scripts/style_metrics.py`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/scripts/style_metrics.py)
  - [`raw/style_metrics.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.json) & [`raw/style_metrics.csv`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/style_metrics.csv)
  - [`raw/asset_report_cards.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/asset_report_cards.json) & [`raw/asset_report_bgs.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/asset_report_bgs.json) (from `create-game-assets/scripts/asset_report.py`)
  - [`contact_sheet.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/contact_sheet.png), [`raw/skill_preview_sheet.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/skill_preview_sheet.png), [`raw/bg_quad.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/raw/bg_quad.png)
  - [`screens/native_1280x800_stage1.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/screens/native_1280x800_stage1.png) & [`screens/native_1280x800_hover_telegraph.png`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/screens/native_1280x800_hover_telegraph.png)

---

## 1. Gemini 4 Argon (`gemini-4-argon`) Native Skill Routing & Verification Architecture

Whereas the source video (`https://youtu.be/t13A2XFGoOc` — *"Turn Claude into an Expert Game Dev with these Free 77 AI Skills"*) packages `gamedev-skills` as a sequential Claude Code `.claude-plugin` slash-command loader, **Gemini 4 Argon (`gemini-4-argon`)** executes the 91-skill catalog natively through Antigravity's parallel multi-agent & MCP verification stack:

1. **Master Router Skill (`gamedev-router` at `~/.gemini/config/skills/gamedev-router/SKILL.md` + `/Users/frederickamina/.local/bin/pxg-gamedev-harness`):**
   - Fingerprints both the Unity 2022.3.40f1 workspace (`ProjectSettings/ProjectVersion.txt`) and the custom HTML5/CSS3D web engine (`WebPlayable/cardfront_cradle_of_echoes_playable.html` per `router/references/custom-engines.md:1-18`).
   - Selects the 4-slot progressive disclosure stack: `create-game-assets` (Discipline) + `tactical-illustrator-library` (Art Direction) + `card-game` (Genre) + `unity-scriptableobjects` (Engine Data).
2. **Parallel Subagent Decomposition:**
   - `code-implementer` runs deterministic raster QA (`create-game-assets/scripts/asset_report.py`, `build_preview_sheet.py`) and quantitative image processing (`scripts/style_metrics.py`) via `/Users/frederickamina/.local/share/mlx-env/bin/python3`.
   - `prime-vision-worker` / headless Chromium Playwright captures native-resolution (`1280x800`) gameplay context screenshots (`screens/native_1280x800_stage1.png`) to verify card silhouettes and stat-gem legibility at actual display scale (`118×156 px` board slots and `91×122 px` hand cards).
   - `mlx-local-worker` (`jevmlx` on Apple Silicon Metal GPU) and `truth-verifier` execute `Tools/skill_harness/iterate.py` against [`checks.json`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/mirofish_gameplay/skills_art_direction/checks.json) to gate every asset claim against measured pixel statistics.

---

## 2. Executive Summary & Headline Findings

1. **Deterministic Normalization & Dimensions PASS (16/16 cards, 4/4 backgrounds):**
   - `create-game-assets/scripts/asset_report.py` (`raw/asset_report_cards.json:1-325`, `raw/asset_report_bgs.json:1-85`) confirms all 16 mastered card portraits are exact `600×800` RGB PNGs (`aspect = 0.7500`, matching `--hand-w: calc(var(--hand-h) * 0.75)` at `cardfront_cradle_of_echoes_playable.html:29` and within 1.3% of `--slot-w: calc(var(--slot-h) * 0.76)` at line 26) with zero uncropped borders (`content_bounds = [0, 0, 600, 800]`), and all 4 stage backgrounds are exact `1024×768` RGB PNGs.
2. **Line Weight & Contrast Cohesion PASS Across the 16-Card Set (`CV < 0.09`):**
   - Across all 16 cards (`raw/style_metrics.json:2238-2255`), RMS luminance contrast has `mean = 0.3043 ± 0.0272` (`CV = 0.089`) and estimated dark-ink stroke width has `mean = 2.43 px ± 0.17 px` (`CV = 0.070`). Only 2 cards breach `|z| >= 2.0` on any intrinsic style metric: **`e_reaper`** (`mean_value = 0.362, z = -2.14`; `line_weight_px = 2.91, z = +2.87`; `noise_sigma = 0.00, z = -2.70` — rendered as a flat vector graphic rather than painterly cel-wash) and **`h_kai`** (`rms_contrast = 0.229, z = -2.79` — washed-out midtones), plus **`e_inferno`** (`mean_saturation = 0.822, z = +2.10`).
3. **CRITICAL Art-Direction Failure (P0): Faction Color-Coding Is Inverted (`31.25%` Classifier Accuracy, `Cohen's d = -0.484`):**
   - The UI locks `--blue-ally: #00E5FF` (`186°` cyan-blue) for Player Heroes and `--red-enemy: #FF2E54` (`349°` crimson-red) for Boss Enemies (`cardfront_cradle_of_echoes_playable.html:12-15, 408-415`).
   - However, quantitative HSV hue-share analysis (`raw/style_metrics.json:2281-2304`) proves the card illustrations have **inverted faction palettes**:
     - **5 of 8 Player Heroes (`62.5%`)** are warm/red-orange dominant (`hero_mean_warm_share = 0.634`, `hero_mean_blue_share = 0.323`): `h_arbiter` (`B=0.000, R=0.061, hue=32°`), `h_archangel` (`B=0.147, R=0.245, hue=32°`), `h_chronos` (`B=0.036, R=0.246, hue=46°`), `h_kai` (`B=0.324, R=0.638, hue=346°`), and `h_phoenix` (`B=0.048, R=0.567, hue=28°`).
     - **6 of 8 Enemy Mechs (`75.0%`)** are cyan/blue/violet dominant (`enemy_mean_blue_share = 0.522`, `enemy_mean_red_share = 0.219`): `e_cryo` (`B=0.998, R=0.000, hue=194°`), `e_reaper` (`B=0.841, R=0.042, hue=260°`), `e_shinobi` (`B=0.697, R=0.009, hue=204°`), `e_eclipse` (`B=0.525, R=0.013, hue=269°`), `e_archon` (`B=0.508, R=0.335, hue=256°`), and `e_colossus` (`B=0.383, R=0.073, hue=171°`).
   - When an enemy card is captured by the player (or vice versa), only a `2px` border changes color (`cardfront_cradle_of_echoes_playable.html:408-415`) while `95%+` of the card surface retains the opposing faction's palette, breaking 1-second board ownership readability.
4. **Stage Background Drift (`4/4` backgrounds exceed `1.5σ` style distance to cards & `0.20` playfield contrast):**
   - The 4 stage backgrounds come from 4 disparate visual systems (`edge_density CV = 0.671`, ranging from `0.0328` painterly blur on `env_isamu_kamikokuryo_skystone.png` to `0.3161` hard isometric linework on `env_breach_staccs_isometric_tower.png`) and have raw center-playfield RMS contrast `0.217–0.250` (`> 0.20`). The web build compensates at runtime with a heavy CSS radial vignette (`rgba(20,35,72,0.72)` to `rgba(4,7,15,0.97)` at line 39), which masks the clash but violates `create-game-assets/SKILL.md:40` (*"Iterate on the source asset, not only on runtime compensations"*).

---

## 3. Skill-by-Skill Rule Audit Table

| Rule ID | Skill & Source Line | Quoted Rule / Guideline | Verdict | Evidence (`WebPlayable` / `Assets` / `raw/`) | Priority & Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AD-1** | `create-game-assets/SKILL.md:16-18` | *"Lock the technical frame. Record engine, 2D/3D, camera/view, native display size, asset dimensions, world scale, transparency, palette..."* | **PASS** | All 16 cards are `600×800` (`aspect 0.75`), all 4 stage BGs are `1024×768` (`aspect 1.3333`); verified in `raw/asset_report_cards.json:1-325` and `raw/asset_report_bgs.json:1-85`. | P3 · S |
| **AD-2** | `create-game-assets/SKILL.md:20-21` & `references/art-direction.md:24-25` | *"Use concrete visual properties; do not substitute a living artist's name for an art direction."* | **FAIL** | `tactical-illustrator-library/SKILL.md:14-18` and `Assets/Scripts/Visuals/SynapseIllustratorStyleLibrary.cs:79,104,129,154,179` inject living artists' names (`"in the art style of Ryoma Ito"`, `"Akihiko Yoshida"`, `"Hideo Minaba"`, `"Ryo Hirata"`, `"Toru Nakayama"`) directly into ComfyUI prompts and background filenames (`env_isamu_kamikokuryo_skystone.png`). | P1 · S |
| **AD-3** | `create-game-assets/SKILL.md:24-25` & `references/provenance.md:1-30` | *"Make an asset manifest... list every required asset, state, variant, size, pivot, collision role, source, license, and approval status... Record provenance."* | **FAIL** | No `asset-manifest.json` exists in `GeneratedArt/` or `WebPlayable/`; card URLs are hardcoded inline in `cardfront_cradle_of_echoes_playable.html:968-1140` with cache-buster `?v=tele4` and zero provenance/seed/license metadata. | P1 · S |
| **AD-4** | `create-game-assets/SKILL.md:29-31` & `references/art-direction.md:14` | *"Keep palette, view, proportions, lighting, outline, and texture density invariant... What roles do accent, danger, reward, neutral, environment, and UI colors play?"* | **FAIL** | Faction color role (`--blue-ally #00E5FF` vs `--red-enemy #FF2E54`) is inverted across 11/16 cards (`blue_vs_red_classifier_accuracy = 0.3125`, `Cohen's d = -0.484`, `raw/style_metrics.json:2288-2304`). | P0 · M |
| **AD-5** | `create-game-assets/SKILL.md:32-34` | *"Normalize deterministically. Crop, size, anchor, slice, name, compress, and check alpha with ordinary image/DCC tools."* | **PASS** | `raw/asset_report_cards.json` confirms 100% of cards have `content_bounds: [0,0,600,800]`, `mode: "RGB"`, `problems: []`, and deterministic `h_<slug>.png` / `e_<slug>.png` naming. | P3 · S |
| **AD-6** | `create-game-assets/SKILL.md:38-40` & `references/art-direction.md:49-55` | *"Validate in context. Inspect a contact sheet and the actual game at native resolution... Iterate on the source asset, not only on runtime compensations."* | **PARTIAL** | Cards read well at native `1280×800` (`screens/native_1280x800_stage1.png`) except `e_reaper` (`subject_area = 0.188`, `com_x = 0.64`) and `h_kai` (`rms_contrast = 0.229`). However, backgrounds rely on a heavy runtime CSS radial-gradient overlay (`alpha 0.72..0.97`, line 39) to hide high center contrast (`0.217–0.250`). | P1 · M |
| **AD-7** | `create-game-assets/references/art-direction.md:58-67` | *"Common drift signals: outline color/width changes between adjacent assets... texture/noise density increases on later generations."* | **PARTIAL** | 14/16 cards stay within `|z| < 2.0` on stroke width (`2.43 ± 0.17 px`) and noise (`0.94 ± 0.35`), but `e_reaper` (`noise_sigma = 0.00`, `line_weight_px = 2.91`, `edge_density = 0.0687`) drifted into a flat-shaded vector style. | P1 · S |
| **AD-8** | `create-game-assets/references/raster-pipeline.md:31-35` | *"Backgrounds and parallax: Preserve a low-contrast playfield behind characters and projectiles. Keep focal detail away from HUD safe areas."* | **FAIL** | All 4 stage backgrounds have raw center-playfield RMS contrast `> 0.20` (`0.217, 0.250, 0.225, 0.240`, `raw/style_metrics.json:1938,2031,2124,2217`) and `edge_density` up to `0.316` (`z = +4.26` vs cards). | P1 · M |
| **AD-9** | `create-game-assets/references/raster-pipeline.md:39-42` | *"UI art and icons: Keep labels, numbers, dynamic copy, focus state, and accessibility text code-native. Prefer one established icon family. Simple geometric symbols should usually be SVG/vector."* | **PASS** | Stat gems (`.edge-num`, lines 633-669), card names (`.slot-name-ribbon`, lines 606-630), and all 16 dynamic telegraph overlays (`buildUniqueTelegraphSVG`, lines 1151-1304) are 100% code-native HTML/CSS/SVG with zero baked raster text. | P3 · S |
| **AD-10** | `CardFrontUnifiedRuntime.cs:686-733` (`DiegeticAtelierController`) | *"High-Contrast Competitive Silhouette Lock: force canonical base mesh silhouette for instant competitive board readability (< 3.0s)."* | **PARTIAL** | Implemented in Unity C# (`CardFrontUnifiedRuntime.cs:700-701`), but absent from `WebPlayable/cardfront_cradle_of_echoes_playable.html` (no toggle to disable SVG telegraph overlays or tint card art by owner). | P2 · S |

---

## 4. Quantitative Style Metrics & Per-Asset Verdicts (`scripts/style_metrics.py`)

All numbers below are produced by running `/Users/frederickamina/.local/share/mlx-env/bin/python3 Datasets/mirofish_gameplay/skills_art_direction/scripts/style_metrics.py` (`raw/style_metrics.json` & `raw/style_metrics.csv`).

### 4.1 16-Card Family Distribution (`600×800` PNGs)
- **Mean Saturation:** `0.541 ± 0.133` (`min = 0.341` `h_archangel`, `max = 0.822` `e_inferno`, `CV = 0.246`)
- **Mean Value (Brightness):** `0.593 ± 0.108` (`min = 0.362` `e_reaper`, `max = 0.747` `e_cryo`, `CV = 0.182`)
- **RMS Luminance Contrast:** `0.304 ± 0.027` (`min = 0.229` `h_kai`, `max = 0.349` `e_titan`, `CV = 0.089`)
- **Sobel Edge Density (`mag > 128`):** `0.146 ± 0.040` (`min = 0.069` `e_reaper`, `max = 0.216` `h_archangel`, `CV = 0.273`)
- **Estimated Ink Stroke Width:** `2.430 ± 0.169 px` (`min = 2.235 px` `e_cryo`, `max = 2.915 px` `e_reaper`, `CV = 0.070`)
- **Flat-Region Noise Sigma:** `0.942 ± 0.348` (`min = 0.000` `e_reaper`, `max = 1.510` `h_chronos`, `CV = 0.370`)
- **Subject Saliency Area:** `0.442 ± 0.136` (`min = 0.188` `e_reaper`, `max = 0.708` `h_valkyrie`)
- **Subject Center-of-Mass Y (`com_y`):** `0.480 ± 0.086` (`min = 0.333` `h_arbiter`, `max = 0.613` `h_seraph`)

### 4.2 Per-Card Quantitative Table & Verdicts (`4 keep`, `5 re-grade`, `7 regenerate`)

| Card ID | Faction | Sat (`z`) | Val (`z`) | Contrast (`z`) | Edge (`z`) | Line px (`z`) | Noise (`z`) | Subj Area | COM `(x,y)` | Blue Share | Red Share | Dom Hue | Verdict | Primary Technical Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `h_oracle` | Hero (Blue) | 0.368 (-1.3) | 0.722 (+1.2) | 0.304 (+0.0) | 0.159 (+0.3) | 2.53 (+0.6) | 0.86 (-0.2) | 0.627 | (0.51, 0.38) | **0.634** | 0.070 | 240° | **KEEP** | Cohesive cyan-blue palette, strong upper-torso framing. |
| `h_seraph` | Hero (Blue) | 0.457 (-0.6) | 0.679 (+0.8) | 0.307 (+0.1) | 0.134 (-0.3) | 2.37 (-0.3) | 1.24 (+0.9) | 0.423 | (0.52, 0.61) | **0.878** | 0.001 | 218° | **KEEP** | Strongest ally cyan-blue identity (`B=0.88`), clean linework. |
| `h_valkyrie` | Hero (Blue) | 0.405 (-1.0) | 0.658 (+0.6) | 0.316 (+0.4) | 0.150 (+0.1) | 2.45 (+0.1) | 0.86 (-0.2) | 0.708 | (0.49, 0.55) | **0.514** | 0.377 | 281° | **KEEP** | Balanced blue-dominant silhouette, high subject fill (`0.71`). |
| `e_titan` | Enemy (Red) | 0.457 (-0.6) | 0.539 (-0.5) | 0.349 (+1.6) | 0.184 (+0.9) | 2.50 (+0.4) | 0.76 (-0.5) | 0.420 | (0.49, 0.58) | 0.226 | **0.545** | 20° | **KEEP** | Reference enemy mech: warm crimson/amber dominance (`R=0.55`), crisp contrast. |
| `h_arbiter` | Hero (Blue) | 0.614 (+0.5) | 0.593 (+0.0) | 0.283 (-0.8) | 0.094 (-1.3) | 2.41 (-0.1) | 1.39 (+1.3) | 0.296 | (0.51, 0.33) | 0.000 | 0.061 | 32° | **RE-GRADE** | Gold/ochre monochrome (`B=0.00`); needs cyan magicite rim/cape shift. |
| `h_archangel`| Hero (Blue) | 0.341 (-1.5) | 0.717 (+1.2) | 0.328 (+0.9) | 0.216 (+1.7) | 2.34 (-0.5) | 0.41 (-1.5) | 0.488 | (0.55, 0.41) | 0.147 | 0.245 | 32° | **RE-GRADE** | Reads warm gold/red (`R=0.25 > B=0.15`); shift background sky/halo to `#00E5FF`. |
| `h_chronos` | Hero (Blue) | 0.508 (-0.2) | 0.562 (-0.3) | 0.293 (-0.4) | 0.188 (+1.0) | 2.24 (-1.1) | 1.51 (+1.6) | 0.402 | (0.51, 0.51) | 0.036 | 0.246 | 46° | **RE-GRADE** | Amber/sepia palette (`B=0.04 < R=0.25`); shift temporal aura to cyan-blue. |
| `e_archon` | Enemy (Red) | 0.478 (-0.5) | 0.710 (+1.1) | 0.326 (+0.8) | 0.133 (-0.3) | 2.29 (-0.8) | 0.97 (+0.1) | 0.436 | (0.50, 0.38) | 0.508 | 0.335 | 256° | **RE-GRADE** | Enemy boss reads blue-violet (`B=0.51 > R=0.33`); shift core glow to `#FF2E54`. |
| `e_inferno` | Enemy (Red) | **0.822 (+2.1)**| 0.478 (-1.1) | 0.295 (-0.4) | 0.146 (-0.0) | 2.25 (-1.1) | 1.17 (+0.7) | 0.356 | (0.50, 0.57) | 0.000 | **0.736** | 22° | **RE-GRADE** | Correct enemy hue (`R=0.74`), but saturation outlier (`0.822 > 0.80` ceiling, `z=+2.10`). |
| `h_kai` | Hero (Blue) | 0.607 (+0.5) | 0.492 (-0.9) | **0.229 (-2.8)**| 0.092 (-1.4) | 2.64 (+1.2) | 1.04 (+0.3) | 0.472 | (0.46, 0.54) | 0.324 | **0.638** | 346° | **REGENERATE** | Contrast outlier (`z=-2.79`) + heavily crimson-dominant (`R=0.64`) on a Blue Hero. |
| `h_phoenix` | Hero (Blue) | 0.657 (+0.9) | 0.637 (+0.4) | 0.315 (+0.4) | 0.117 (-0.7) | 2.33 (-0.6) | 1.10 (+0.5) | 0.604 | (0.54, 0.40) | 0.048 | **0.567** | 28° | **REGENERATE** | Reads as an Enemy fire card (`R=0.57, B=0.05`); regenerate with blue-white astral flames. |
| `e_colossus` | Enemy (Red) | 0.681 (+1.0) | 0.458 (-1.3) | 0.337 (+1.2) | 0.158 (+0.3) | 2.53 (+0.6) | 0.81 (-0.4) | 0.364 | (0.50, 0.58) | **0.383** | 0.073 | 171° | **REGENERATE** | Stage 3 Boss is teal-cyan (`B=0.38, R=0.07`), matching Player ally color instead of Boss red. |
| `e_cryo` | Enemy (Red) | 0.746 (+1.5) | 0.747 (+1.4) | 0.295 (-0.3) | 0.205 (+1.5) | 2.24 (-1.2) | 0.98 (+0.1) | 0.319 | (0.47, 0.50) | **0.998** | 0.000 | 194° | **REGENERATE** | `99.8%` cyan-blue (`hue=194°`, identical to `--blue-ally` `186°`); worst faction confusion on board. |
| `e_eclipse` | Enemy (Red) | 0.463 (-0.6) | 0.523 (-0.6) | 0.278 (-1.0) | 0.126 (-0.5) | 2.47 (+0.2) | 0.93 (-0.0) | 0.341 | (0.49, 0.47) | **0.525** | 0.013 | 269° | **REGENERATE** | Stage 1 Boss has `R=0.013, B=0.525`; needs crimson-magenta void core to read as Red Boss. |
| `e_reaper` | Enemy (Red) | 0.472 (-0.5) | **0.362 (-2.1)**| 0.296 (-0.3) | 0.069 (-1.9) | **2.91 (+2.9)**| **0.00 (-2.7)**| **0.188** | (0.64, 0.37) | **0.841** | 0.042 | 260° | **REGENERATE** | 3-axis style outlier (`val`, `line_px`, `noise=0.00`), tiny off-center silhouette (`area=0.19`), blue hue (`0.84`). |
| `e_shinobi` | Enemy (Red) | 0.586 (+0.3) | 0.609 (+0.1) | 0.318 (+0.5) | 0.168 (+0.5) | 2.37 (-0.3) | 1.05 (+0.3) | 0.624 | (0.51, 0.49) | **0.697** | 0.009 | 204° | **REGENERATE** | `69.7%` cyan-blue (`R=0.009`); visually indistinguishable from a Blue Hero card at board scale. |

### 4.3 Stage Backgrounds Quantitative Table (`1024×768` PNGs)

| Stage & File | Sat | Val | Contrast | Edge Density (`z_vs_cards`) | Line px | Noise | Style Dist to Cards | Center Playfield Contrast | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S1:** `env_isamu_kamikokuryo_skystone.png` | 0.318 | 0.511 | 0.199 | 0.0328 (-2.84z) | 2.01 | 2.02 | **2.64σ** | **0.217** (`>0.20`) | **REGENERATE** |
| **S2:** `env_hiroshi_minagawa_ivalice_diorama.png` | 0.738 | 0.622 | 0.267 | 0.0893 (-1.43z) | 2.14 | 1.90 | **1.67σ** | **0.250** (`>0.20`) | **REGENERATE** |
| **S3:** `env_nakayama_neo_arcadia_mmz.png` | 0.473 | 0.842 | 0.252 | 0.2678 (+3.05z) | 2.12 | 1.01 | **1.91σ** | **0.225** (`>0.20`) | **REGENERATE** |
| **S4:** `env_breach_staccs_isometric_tower.png` | 0.473 | 0.832 | 0.230 | 0.3161 (+4.26z) | 2.64 | 1.17 | **2.34σ** | **0.240** (`>0.20`) | **REGENERATE** |

---

## 5. Concrete Fixes & CARDFRONT Style Bible (Not Applied to Game Files)

### 5.1 Quantitative Style Bible & Acceptance Band (for `create-game-assets` Gate)
- **Dimensions & Aspect:** Cards `600×800` PNG (`aspect = 0.75`, RGB, opaque); Stage Backgrounds `1024×768` PNG (`aspect = 1.3333`, RGB, opaque).
- **Value & Contrast Band:** Cards `mean_value ∈ [0.45, 0.75]`, `rms_contrast ∈ [0.26, 0.35]`, `mean_saturation ∈ [0.35, 0.78]`.
- **Edge & Line Weight Band:** `edge_density ∈ [0.10, 0.22]`, dark-ink stroke width `line_weight_px ∈ [2.15, 2.75] px`, flat-region `noise_sigma ∈ [0.40, 1.60]`.
- **Framing & Safe Zones:** `subject_area ∈ [0.30, 0.72]`, `subject_com_x ∈ [0.42, 0.58]`, `subject_com_y ∈ [0.34, 0.60]` (keeps character head/torso above the bottom `20px` `.slot-name-ribbon` and away from the `20×20px` `.edge-num` stat gems).
- **Faction Chromatic Separation:**
  - **Player Heroes (`h_*`):** `blue_share (180°–260°) >= red_share (330°–25°) + 0.10` (cool cyan/cobalt/astral gold accents).
  - **Enemy Mechs (`e_*`):** `red_share (330°–25°) >= blue_share (180°–260°) + 0.10` (crimson/scarlet/amber-obsidian accents).
- **Playfield Background Rule:** Center `50%×60%` playfield region `centre_rms_contrast <= 0.18` prior to CSS overlay.

### 5.2 Runtime Faction Ownership Tint & Silhouette Lock Sketch (WebPlayable CSS)
To make captured cards immediately readable on the 3×3 board even before re-generating the 7 off-palette portraits, apply a subtle faction duotone/rim filter in [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](file:///Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/WebPlayable/cardfront_cradle_of_echoes_playable.html#L408-L415):

```css
/* Sketch for WebPlayable/cardfront_cradle_of_echoes_playable.html:408-415 */
.card-3d-unit.owner-player .card-art-frame::after,
.card-3d-unit.owner-ai .card-art-frame::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  mix-blend-mode: color;
  opacity: 0.28;
}
.card-3d-unit.owner-player .card-art-frame::after {
  background: linear-gradient(180deg, #00E5FF 0%, rgba(0, 229, 255, 0.2) 100%);
}
.card-3d-unit.owner-ai .card-art-frame::after {
  background: linear-gradient(180deg, #FF2E54 0%, rgba(255, 46, 84, 0.2) 100%);
}
```
