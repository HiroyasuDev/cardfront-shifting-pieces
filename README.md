# CARDFRONT: Cradle of Echoes — 2.5D/3D Tabletop & Tactical Card Battler (`unity-tcg-engine`)

**CARDFRONT: Cradle of Echoes** (*Shifting Pieces × CardCraft × Dicevaders*) is a 2.5D/3D tactical grid card and dice battler combining **3×3 directional card capture** (*Triple Triad / Queen's Blood / Metal Gear Acid*), **Tactical Slide & 16 unique unit telegraphs** (*Into the Breach*), and **real 6-sided 3D column dice power-ups** (*Dicey Dungeons*).

---

## 🎮 Playable 2.5D/3D Web Build (`WebPlayable/`)

- **Playable HTML5 / WebGL-Style 3D Tabletop Client**: [`WebPlayable/cardfront_cradle_of_echoes_playable.html`](WebPlayable/cardfront_cradle_of_echoes_playable.html)
- **Local Playtest & Telemetry Server**: [`WebPlayable/serve_playtest.py`](WebPlayable/serve_playtest.py)
  ```bash
  python3 WebPlayable/serve_playtest.py
  # Open http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html
  ```
- **Automated macOS `osascript` E2E Playtest**:
  - Append `?autotest=1` (`http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html?autotest=1`) to trigger [`runVisualAutomatedPlaytest()`](WebPlayable/cardfront_cradle_of_echoes_playable.html), which verifies 100% singleton cards, `600×800` (`3:4` portrait) mastered illustrations, 3D camera presets, 3D tumbling dice nudges/rerolls, Tactical Slide (`1× Free / Turn`), 16 unique animated SVG telegraphs, and full 4-turn match completion.
  - Latest E2E telemetry report: [`Datasets/osascript_3d_game_e2e_report.json`](Datasets/osascript_3d_game_e2e_report.json)

---

## 🎨 Studio-Mastered `600×800` (`3:4` Portrait) Card Illustrations (`GeneratedArt/MasteredCards/`)

All 16 singleton cards (8 Player Heroes + 8 Boss Constructs) feature dedicated `600×800` (`3:4` portrait) mastered illustrations and unique animated SVG tactical telegraphs:

- **Player Heroes (Blue)**:
  - `h_archangel.png` — **Aethelgard Seraph** (*4-Wing Solar Cross*)
  - `h_phoenix.png` — **Ignis Blademaster** (*Twin Flame Arc*)
  - `h_oracle.png` — **Lunar Tide Oracle** (*Crescent Tidal Ward*)
  - `h_chronos.png` — **Chronos Sovereign** (*12-Hour Astrolabe*)
  - `h_seraph.png` — **radiant Valkyrie** (*4-Pillar Spear Drop*)
  - `h_kai.png` — **Kai — Neon Breacher** (*Solid Eye Target Lock*)
  - `h_valkyrie.png` — **Aegis Striker** (*Orbital Airstrike*)
  - `h_arbiter.png` — **Hallowed Arbiter** (*Ivalice Law Seal*)
- **Enemy Boss Constructs (Red)**:
  - `e_eclipse.png` — **Eclipse Void Blade** (*Void Gravity Well*)
  - `e_archon.png` — **Prism Core Archon** (*Refraction Tri-Beam*)
  - `e_inferno.png` — **Inferno Core Seraph** (*Hellfire Hazard Ring*)
  - `e_reaper.png` — **Sigil Wraith** (*180° Grim Cleave*)
  - `e_titan.png` — **Bastion Dreadnought** (*Seismic Shockwave*)
  - `e_colossus.png` — **Emerald Colossus** (*Piercing Railgun*)
  - `e_cryo.png` — **Cryo Interceptor** (*Zero-K Frost Lattice*)
  - `e_shinobi.png` — **Cyber Shinobi** (*MGA Stealth Cone*)

---

## 🏗️ Unity C# Runtime, Hardened Backend & MiroFish Verification

- **Unified C# Runtime Bridge**: [`Assets/TcgEngine/Scripts/GameLogic/CardFrontUnifiedRuntime.cs`](Assets/TcgEngine/Scripts/GameLogic/CardFrontUnifiedRuntime.cs) (`42/42` automated assertions passed)
- **Hardened Node.js Backend (`TcgEngineAPI`)**: [`Backend/Server.js`](Backend/Server.js), [`Backend/controllers/users.controller.js`](Backend/controllers/users.controller.js), [`Backend/SecurityVerification.test.js`](Backend/SecurityVerification.test.js) (`19/19` security checks passed)
- **MiroFish Financial & Unit Economics Audit**: [`Datasets/mirofish_post_remediation_viability.json`](Datasets/mirofish_post_remediation_viability.json)
