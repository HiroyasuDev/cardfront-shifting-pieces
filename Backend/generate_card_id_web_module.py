#!/usr/bin/env python3
"""
Builds WebPlayable/modules/card_identification_catalog_ui.js from
Assets/Resources/Cards/card_identification_catalog_v1.json and
WebPlayable/GeneratedArt/Icons/collector_rarity_svg_manifest.json.
"""

import json
from pathlib import Path

ROOT = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
CATALOG_PATH = ROOT / "Assets/Resources/Cards/card_identification_catalog_v1.json"
SVG_MANIFEST_PATH = ROOT / "WebPlayable/GeneratedArt/Icons/collector_rarity_svg_manifest.json"
OUT_JS_PATH = ROOT / "WebPlayable/modules/card_identification_catalog_ui.js"


def compact_record(rec: dict) -> dict:
    ident = rec.get("identification") or {}
    evo = ident.get("evolved_counterpart")
    out = {
        "card_id": rec.get("card_id") or rec.get("id"),
        "id": rec.get("id") or rec.get("card_id"),
        "original_title": rec.get("original_title") or ident.get("original_title"),
        "original_title_evolved": rec.get("original_title_evolved") or ident.get("original_title_evolved"),
        "title": rec.get("title") or rec.get("name") or ident.get("title"),
        "name": rec.get("name") or rec.get("title") or ident.get("title"),
        "card_game": rec.get("card_game") or ident.get("card_game") or "Shadowverse EVOLVE / CARDFRONT Collector Standard",
        "card_game_primary": rec.get("card_game_primary") or ident.get("card_game_primary") or "Shadowverse EVOLVE",
        "version": rec.get("version") or ident.get("version") or "[BP05] Eternal omens",
        "original_version": rec.get("original_version") or ident.get("original_version") or "ブースターパック第5弾 永劫なる絶傑",
        "set_code": rec.get("set_code") or ident.get("set_code") or "BP05",
        "card_number": rec.get("card_number") or ident.get("card_number") or "BP05-110 SR",
        "rarity": rec.get("rarity") or ident.get("rarity") or "SR",
        "rarity_full_en": rec.get("rarity_full_en") or ident.get("rarity_full_en") or "Super Rare",
        "rarity_full_jp": rec.get("rarity_full_jp") or ident.get("rarity_full_jp") or "スーパーレア",
        "evolution_state": rec.get("evolution_state") or ident.get("evolution_state") or "進化前",
        "evolution_state_en": rec.get("evolution_state_en") or ident.get("evolution_state_en") or "Unevolved",
        "nesw": rec.get("nesw") or [rec.get("up", 7), rec.get("right", 8), rec.get("down", 6), rec.get("left", 7)],
        "faction": rec.get("faction") or rec.get("theme") or "Aether-Tech",
        "cost": rec.get("cost", 3),
        "art_path": rec.get("art_path") or "GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png",
        "evolved_art_path": rec.get("evolved_art_path") or "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png",
        "lore_en": rec.get("lore_en") or ident.get("lore_en") or "",
        "lore_jp": rec.get("lore_jp") or ident.get("lore_jp") or "",
        "atelier_art_direction": rec.get("atelier_art_direction") or ident.get("atelier_art_direction") or {},
        "collector_provenance": rec.get("collector_provenance") or ident.get("collector_provenance") or {},
        "sha256_collector_id": rec.get("sha256_collector_id") or ident.get("sha256_collector_id") or "",
    }
    if evo and isinstance(evo, dict):
        out["evolved_counterpart_id"] = evo.get("card_id") or evo.get("id")
    return out


def build_js() -> None:
    catalog_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    svg_manifest = json.loads(SVG_MANIFEST_PATH.read_text(encoding="utf-8"))
    icon_bodies = dict(svg_manifest.get("cf_icon_bodies", {}))

    records = {}
    ref = catalog_data["reference_archetype_specification"]
    rosa_u = compact_record(ref["unevolved"])
    rosa_e = compact_record(ref["evolved"])
    rosa_u["art_path"] = "GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png"
    rosa_u["evolved_art_path"] = "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png"
    rosa_u["evolved_counterpart_id"] = "bp05_110_rosa_evolved"
    rosa_e["art_path"] = "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png"

    records["bp05_110_rosa"] = rosa_u
    records["bp05_110_rosa_unevolved"] = rosa_u
    records["bp05_110_rosa_evolved"] = rosa_e

    for entry in catalog_data.get("cards", []):
        cid = entry.get("card_id") or entry.get("id")
        if cid:
            records[cid] = compact_record(entry)
        evo = entry.get("identification", {}).get("evolved_counterpart")
        if evo and evo.get("card_id"):
            records[evo["card_id"]] = compact_record(evo)

    for entry in catalog_data.get("evolved_cards", []):
        cid = entry.get("card_id") or entry.get("id")
        if cid and cid not in records:
            records[cid] = compact_record(entry)

    playable_aliases = {
        "h_archangel": ("hero_01_kaelen", "GeneratedArt/MasteredCards/h_archangel.png", "GeneratedArt/EvolveMechWingMaidens/ev_02_evo_seraphina_solar_archon.png"),
        "h_valkyrie": ("hero_02_valkyrie", "GeneratedArt/MasteredCards/h_valkyrie.png", "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png"),
        "h_lunar": ("hero_03_celeste", "GeneratedArt/MasteredCards/h_lunar.png", "GeneratedArt/EvolveMechWingMaidens/ev_03_evo_lyra_chrono_horizon_empress.png"),
        "h_bastion": ("hero_04_bastion", "GeneratedArt/MasteredCards/h_bastion.png", "GeneratedArt/EvolveMechWingMaidens/ev_04_evo_isolde_abyssal_rose_sovereign.png"),
        "h_chronos": ("hero_05_chronos", "GeneratedArt/MasteredCards/h_chronos.png", "GeneratedArt/EvolveMechWingMaidens/ev_03_evo_lyra_chrono_horizon_empress.png"),
        "h_orb": ("hero_06_seraphina", "GeneratedArt/MasteredCards/h_orb.png", "GeneratedArt/EvolveMechWingMaidens/ev_05_evo_noctis_genesis_star_breaker.png"),
        "h_dreadnought": ("hero_07_dreadnought", "GeneratedArt/MasteredCards/h_dreadnought.png", "GeneratedArt/EvolveMechWingMaidens/ev_04_evo_isolde_abyssal_rose_sovereign.png"),
        "h_seraph": ("hero_08_aurora", "GeneratedArt/MasteredCards/h_seraph.png", "GeneratedArt/EvolveMechWingMaidens/ev_02_evo_seraphina_solar_archon.png"),
        "h_kai": ("hero_09_kai", "GeneratedArt/MasteredCards/h_kai.png", "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png"),
        "h_golem": ("hero_10_golem", "GeneratedArt/MasteredCards/h_golem.png", "GeneratedArt/EvolveMechWingMaidens/ev_05_evo_noctis_genesis_star_breaker.png"),
        "h_sylph": ("hero_11_sylph", "GeneratedArt/MasteredCards/h_sylph.png", "GeneratedArt/EvolveMechWingMaidens/ev_01_evo_rosalia_celestial_aegis_wing.png"),
        "h_phoenix": ("hero_12_phoenix", "GeneratedArt/MasteredCards/h_phoenix.png", "GeneratedArt/EvolveMechWingMaidens/ev_02_evo_seraphina_solar_archon.png"),
        "b_behemoth": ("boss_01_behemoth", "GeneratedArt/MasteredCards/b_behemoth.png", "GeneratedArt/EvolveMechWingMaidens/ev_04_evo_isolde_abyssal_rose_sovereign.png"),
        "b_siren": ("boss_02_siren", "GeneratedArt/MasteredCards/b_siren.png", "GeneratedArt/EvolveMechWingMaidens/ev_05_evo_noctis_genesis_star_breaker.png"),
        "b_automaton": ("boss_03_automaton", "GeneratedArt/MasteredCards/b_automaton.png", "GeneratedArt/EvolveMechWingMaidens/ev_03_evo_lyra_chrono_horizon_empress.png"),
        "b_leviathan": ("boss_04_leviathan", "GeneratedArt/MasteredCards/b_leviathan.png", "GeneratedArt/EvolveMechWingMaidens/ev_05_evo_noctis_genesis_star_breaker.png"),
    }

    for alias_id, (src_id, base_art, evo_art) in playable_aliases.items():
        if src_id in records:
            cloned = json.loads(json.dumps(records[src_id]))
            cloned["card_id"] = alias_id
            cloned["id"] = alias_id
            cloned["art_path"] = base_art
            cloned["evolved_art_path"] = evo_art
            records[alias_id] = cloned

    js_source = f"""/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes — Bilingual Card Identification System,
 * 3D Holographic Collector Slab & Full-Bleed Artwork Appreciation Mode (鑑賞モード)
 * Module: WebPlayable/modules/card_identification_catalog_ui.js
 *
 * Canonical Reference Specification:
 *   original title    機構翼の少女・ローザ(進化前)
 *   card game         Shadowverse EVOLVE
 *   version           [BP05] Eternal omens
 *   original version  ブースターパック第5弾 永劫なる絶傑
 *   card number       BP05-110 SR
 *   rarity            SR
 *
 * Zero Generic Unicode Emojis: 100% bespoke viewBox="0 0 256 256" Atelier SVGs.
 * Zero Living Artists' Names: Concrete morphological & chromatic art direction.
 * ============================================================================ */
(function initSynapseCardIdentificationCatalogUI(globalScope) {{
  "use strict";

  const COLLECTOR_SVG_BODIES = {json.dumps(icon_bodies, ensure_ascii=False, indent=2)};

  function registerCollectorIcons() {{
    if (!globalScope.CF_ICON_BODIES) {{
      globalScope.CF_ICON_BODIES = {{}};
    }}
    Object.keys(COLLECTOR_SVG_BODIES).forEach(function (k) {{
      globalScope.CF_ICON_BODIES[k] = COLLECTOR_SVG_BODIES[k];
    }});
  }}

  registerCollectorIcons();

  function renderIcon(name, sizePx, extraStyle) {{
    registerCollectorIcons();
    if (typeof globalScope.cfIcon === "function") {{
      return globalScope.cfIcon(name, sizePx || 16, extraStyle || "");
    }}
    const body = COLLECTOR_SVG_BODIES[name] || COLLECTOR_SVG_BODIES.rarity_sr;
    const sz = sizePx || 16;
    return `<svg class="cf-atelier-svg-icon" viewBox="0 0 256 256" width="${{sz}}" height="${{sz}}" style="vertical-align:middle;${{extraStyle || ""}}">${{body}}</svg>`;
  }}

  function rarityIconKey(rarity) {{
    const r = String(rarity || "SR").toUpperCase();
    if (r === "UR") return "rarity_ur";
    if (r === "LG") return "rarity_lg";
    if (r === "SR") return "rarity_sr";
    if (r === "GR") return "rarity_gr";
    return "rarity_br";
  }}

  const RAW_RECORDS = {json.dumps(records, ensure_ascii=False)};

  const NUMBER_INDEX = {{}};
  const TITLE_INDEX = {{}};

  function indexRecord(key, rec) {{
    if (!rec) return;
    RAW_RECORDS[key] = rec;
    const num = String(rec.card_number || "").trim().toUpperCase();
    if (num) {{
      NUMBER_INDEX[num] = rec;
      const baseCode = num.split(/\\s+/)[0];
      if (baseCode && !NUMBER_INDEX[baseCode]) NUMBER_INDEX[baseCode] = rec;
    }}
    const origTitle = String(rec.original_title || "").trim();
    if (origTitle) {{
      TITLE_INDEX[origTitle] = rec;
      TITLE_INDEX[origTitle.toLowerCase()] = rec;
    }}
    const enTitle = String(rec.title || rec.name || "").trim();
    if (enTitle) {{
      TITLE_INDEX[enTitle.toLowerCase()] = rec;
    }}
  }}

  Object.keys(RAW_RECORDS).forEach(function (k) {{
    indexRecord(k, RAW_RECORDS[k]);
  }});

  let activeCardKey = "bp05_110_rosa";
  let showEvolvedState = false;
  let artAppreciationMode = false;

  function lookupCard(query) {{
    if (!query) return RAW_RECORDS["bp05_110_rosa"];
    if (typeof query === "object" && query.original_title) return query;
    const q = String(query).trim();
    if (RAW_RECORDS[q]) return RAW_RECORDS[q];
    if (RAW_RECORDS[q.toLowerCase()]) return RAW_RECORDS[q.toLowerCase()];
    const upper = q.toUpperCase();
    if (NUMBER_INDEX[upper]) return NUMBER_INDEX[upper];
    if (TITLE_INDEX[q]) return TITLE_INDEX[q];
    if (TITLE_INDEX[q.toLowerCase()]) return TITLE_INDEX[q.toLowerCase()];

    const keys = Object.keys(RAW_RECORDS);
    for (let i = 0; i < keys.length; i++) {{
      const rec = RAW_RECORDS[keys[i]];
      const hay = [
        rec.card_id,
        rec.original_title,
        rec.title,
        rec.name,
        rec.card_number,
        rec.version,
        rec.original_version
      ].join(" ").toLowerCase();
      if (hay.indexOf(q.toLowerCase()) !== -1) {{
        return rec;
      }}
    }}
    return RAW_RECORDS["bp05_110_rosa"];
  }}

  function resolveDisplayRecord(cardOrId, evolvedOverride) {{
    const baseRec = lookupCard(cardOrId);
    const useEvo = typeof evolvedOverride === "boolean" ? evolvedOverride : showEvolvedState;
    if (useEvo) {{
      const evoId = baseRec.evolved_counterpart_id || ((baseRec.card_id || "") + "_evolved");
      const evoCounter = RAW_RECORDS[evoId];
      if (evoCounter) {{
        const merged = Object.assign({{}}, baseRec, evoCounter);
        merged.art_path = baseRec.evolved_art_path || evoCounter.art_path || baseRec.art_path;
        return merged;
      }}
      const synth = Object.assign({{}}, baseRec);
      synth.original_title = String(baseRec.original_title || "").replace("進化前", "進化後");
      synth.evolution_state = "進化後";
      synth.evolution_state_en = "Evolved";
      const nesw = Array.isArray(baseRec.nesw) ? baseRec.nesw : [7, 8, 6, 7];
      synth.nesw = nesw.map(function (v) {{ return Math.min(10, Number(v) + 1); }});
      synth.art_path = baseRec.evolved_art_path || baseRec.art_path;
      return synth;
    }}
    return baseRec;
  }}

  function formatCollectorPlainText(cardOrId, evolvedOverride) {{
    const rec = resolveDisplayRecord(cardOrId, evolvedOverride);
    const gameLabel = rec.card_game_primary || "Shadowverse EVOLVE";
    return [
      "original title    " + (rec.original_title || "機構翼の少女・ローザ(進化前)"),
      "card game         " + gameLabel,
      "version           " + (rec.version || "[BP05] Eternal omens"),
      "original version  " + (rec.original_version || "ブースターパック第5弾 永劫なる絶傑"),
      "card number       " + (rec.card_number || "BP05-110 SR"),
      "rarity            " + (rec.rarity || "SR")
    ].join("\\n");
  }}

  function formatCollectorSpecTable(cardOrId, evolvedOverride) {{
    const rec = resolveDisplayRecord(cardOrId, evolvedOverride);
    const rarity = rec.rarity || "SR";
    const rIcon = renderIcon(rarityIconKey(rarity), 18, "margin-right:6px;");
    const eIcon = renderIcon("evolve_crest", 16, "margin-right:5px;");
    const gameLabel = (rec.card_game_primary || "Shadowverse EVOLVE") + " / CARDFRONT";
    return `
      <table class="cf-collector-spec-table" aria-label="Bilingual Card Identification Specification">
        <tbody>
          <tr>
            <th>original title</th>
            <td>
              <span class="cf-spec-jp-title">${{rec.original_title || "機構翼の少女・ローザ(進化前)"}}</span>
              <span class="cf-spec-evo-pill">${{eIcon}}${{rec.evolution_state || "進化前"}} · ${{rec.evolution_state_en || "Unevolved"}}</span>
            </td>
          </tr>
          <tr>
            <th>card game</th>
            <td>${{gameLabel}}</td>
          </tr>
          <tr>
            <th>version</th>
            <td><code class="cf-spec-code">${{rec.version || "[BP05] Eternal omens"}}</code></td>
          </tr>
          <tr>
            <th>original version</th>
            <td>${{rec.original_version || "ブースターパック第5弾 永劫なる絶傑"}}</td>
          </tr>
          <tr>
            <th>card number</th>
            <td><strong class="cf-spec-cardnum">${{rec.card_number || "BP05-110 SR"}}</strong></td>
          </tr>
          <tr>
            <th>rarity</th>
            <td><span class="cf-spec-rarity-badge cf-rarity-${{String(rarity).toLowerCase()}}">${{rIcon}}${{rarity}} · ${{rec.rarity_full_en || "Super Rare"}} (${{rec.rarity_full_jp || "スーパーレア"}})</span></td>
          </tr>
        </tbody>
      </table>
    `;
  }}

  function ensureStylesInjected() {{
    if (document.getElementById("cf-card-id-catalog-styles")) return;
    const style = document.createElement("style");
    style.id = "cf-card-id-catalog-styles";
    style.textContent = `
      #cf-card-id-modal {{
        position: fixed;
        inset: 0;
        z-index: 9850;
        background: radial-gradient(circle at 50% 24%, rgba(12, 20, 38, 0.94), rgba(4, 7, 15, 0.98));
        backdrop-filter: blur(14px);
        display: none;
        align-items: center;
        justify-content: center;
        padding: 16px;
        color: #f8fafc;
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
      }}
      #cf-card-id-modal.open {{
        display: flex;
      }}
      .cf-cid-dialog {{
        width: min(1140px, 96vw);
        max-height: 92vh;
        background: linear-gradient(155deg, rgba(13, 21, 38, 0.97), rgba(7, 11, 22, 0.99));
        border: 1.5px solid rgba(255, 184, 0, 0.55);
        border-radius: 16px;
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.85), 0 0 32px rgba(0, 229, 255, 0.18);
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }}
      .cf-cid-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 18px;
        background: linear-gradient(90deg, rgba(255, 184, 0, 0.14), rgba(0, 229, 255, 0.08));
        border-bottom: 1px solid rgba(255, 184, 0, 0.32);
        gap: 12px;
        flex-wrap: wrap;
      }}
      .cf-cid-title {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 900;
        letter-spacing: 0.6px;
        color: #ffe082;
        text-transform: uppercase;
      }}
      .cf-cid-body {{
        display: grid;
        grid-template-columns: 360px 1fr;
        gap: 18px;
        padding: 16px 18px;
        overflow-y: auto;
      }}
      @media (max-width: 860px) {{
        .cf-cid-body {{
          grid-template-columns: 1fr;
        }}
      }}
      /* 3:4 600x800 Interactive 3D Collector Slab & Holographic Foil Loupe */
      .cf-collector-slab-stage {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        perspective: 1100px;
      }}
      .cf-collector-slab-card {{
        position: relative;
        width: 315px;
        height: 420px;
        aspect-ratio: 3 / 4;
        border-radius: 14px;
        overflow: hidden;
        transform-style: preserve-3d;
        transition: transform 0.14s cubic-bezier(0.2, 0.85, 0.3, 1), box-shadow 0.25s ease;
        border: 2px solid #ffb800;
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.78), 0 0 24px rgba(0, 229, 255, 0.28);
        background: #070b14;
        cursor: grab;
      }}
      .cf-collector-slab-card.evolved-glow {{
        border-color: #00e5ff;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.85), 0 0 34px rgba(255, 184, 0, 0.58), 0 0 18px rgba(0, 229, 255, 0.65);
      }}
      .cf-collector-slab-art {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transform: scale(1.015);
        transition: transform 0.35s ease, filter 0.35s ease;
      }}
      .cf-collector-slab-card.evolved-glow .cf-collector-slab-art {{
        filter: saturate(1.14) contrast(1.06);
      }}
      .cf-collector-foil-sheen {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        background: linear-gradient(125deg,
          rgba(255,255,255,0) 20%,
          rgba(0, 229, 255, 0.22) 42%,
          rgba(255, 184, 0, 0.28) 50%,
          rgba(168, 85, 247, 0.22) 58%,
          rgba(255,255,255,0) 80%);
        mix-blend-mode: screen;
        opacity: 0.68;
        transition: background 0.1s linear, opacity 0.25s ease;
      }}
      .cf-collector-hud-overlay {{
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px;
        pointer-events: none;
        background: linear-gradient(180deg, rgba(6,10,22,0.55) 0%, rgba(6,10,22,0.0) 24%, rgba(6,10,22,0.0) 64%, rgba(6,10,22,0.88) 100%);
        transition: opacity 0.28s ease;
      }}
      /* Full-Bleed 600x800 Artwork Appreciation Mode (鑑賞モード) */
      .cf-collector-slab-card.art-appreciation-mode .cf-collector-hud-overlay {{
        opacity: 0 !important;
      }}
      .cf-collector-slab-TopRow {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
      }}
      .cf-slab-badge {{
        background: rgba(8, 13, 26, 0.86);
        border: 1px solid rgba(255, 184, 0, 0.65);
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 11px;
        font-weight: 800;
        color: #fef08a;
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }}
      .cf-slab-nesw-diamond {{
        display: grid;
        grid-template-columns: repeat(3, 20px);
        grid-template-rows: repeat(3, 20px);
        gap: 1px;
        background: rgba(8, 13, 26, 0.88);
        border: 1.5px solid #ffb800;
        border-radius: 8px;
        padding: 3px;
        font-size: 11px;
        font-weight: 900;
        color: #f8fafc;
        text-align: center;
      }}
      .cf-slab-bottom-plate {{
        background: rgba(8, 13, 26, 0.88);
        border: 1px solid rgba(255, 184, 0, 0.55);
        border-radius: 10px;
        padding: 8px 10px;
        display: flex;
        flex-direction: column;
        gap: 3px;
      }}
      .cf-slab-jp-name {{
        font-size: 13px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 0.3px;
      }}
      .cf-slab-en-name {{
        font-size: 11px;
        color: #93c5fd;
        font-weight: 700;
      }}
      .cf-slab-serial-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 10px;
        color: #cbd5e1;
        margin-top: 2px;
        padding-top: 3px;
        border-top: 1px solid rgba(148, 163, 184, 0.25);
      }}
      .cf-collector-spec-table {{
        width: 100%;
        border-collapse: collapse;
        background: rgba(9, 14, 28, 0.88);
        border: 1px solid rgba(255, 184, 0, 0.38);
        border-radius: 10px;
        overflow: hidden;
        font-size: 12px;
      }}
      .cf-collector-spec-table th {{
        width: 148px;
        text-align: left;
        padding: 7px 12px;
        background: rgba(255, 184, 0, 0.11);
        color: #fde68a;
        font-weight: 800;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        text-transform: lowercase;
      }}
      .cf-collector-spec-table td {{
        padding: 7px 12px;
        color: #f8fafc;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
      }}
      .cf-spec-jp-title {{
        font-weight: 900;
        color: #ffffff;
        margin-right: 8px;
      }}
      .cf-spec-evo-pill {{
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        background: rgba(0, 229, 255, 0.16);
        border: 1px solid rgba(0, 229, 255, 0.48);
        color: #67e8f9;
      }}
      .cf-spec-code {{
        background: rgba(30, 41, 59, 0.85);
        padding: 2px 6px;
        border-radius: 4px;
        color: #38bdf8;
        font-weight: 700;
      }}
      .cf-spec-cardnum {{
        color: #fbbf24;
        letter-spacing: 0.5px;
      }}
      .cf-spec-rarity-badge {{
        display: inline-flex;
        align-items: center;
        font-weight: 800;
        color: #fef08a;
      }}
      .cf-cid-preset-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
      }}
      .cf-cid-pill-btn {{
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.45);
        color: #e2e8f0;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
      }}
      .cf-cid-pill-btn:hover, .cf-cid-pill-btn.active {{
        border-color: #ffb800;
        background: rgba(255, 184, 0, 0.18);
        color: #ffffff;
      }}
      .cf-cid-lore-box {{
        background: rgba(12, 19, 36, 0.86);
        border: 1px solid rgba(168, 85, 247, 0.38);
        border-radius: 10px;
        padding: 10px 12px;
        margin-top: 10px;
        font-size: 12px;
        line-height: 1.48;
      }}
      .cf-cid-art-notes {{
        background: rgba(10, 17, 32, 0.86);
        border: 1px solid rgba(0, 229, 255, 0.32);
        border-radius: 10px;
        padding: 10px 12px;
        margin-top: 10px;
        font-size: 11.5px;
        line-height: 1.45;
        color: #cbd5e1;
      }}
      /* Micro collector stamp on hand and board cards */
      .cf-card-collector-microstamp {{
        position: absolute;
        bottom: 2px;
        left: 4px;
        z-index: 9;
        background: rgba(5, 9, 18, 0.84);
        border: 1px solid rgba(255, 184, 0, 0.48);
        border-radius: 4px;
        padding: 0px 4px;
        font-size: 8.5px;
        font-weight: 800;
        color: #fde68a;
        letter-spacing: 0.25px;
        pointer-events: none;
        line-height: 1.25;
      }}
    `;
    document.head.appendChild(style);
  }}

  function ensureModalBuilt() {{
    ensureStylesInjected();
    let modal = document.getElementById("cf-card-id-modal");
    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "cf-card-id-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-label", "Bilingual Card Identification & Artwork Appreciation Grimoire");
    modal.innerHTML = `
      <div class="cf-cid-dialog">
        <div class="cf-cid-header">
          <div class="cf-cid-title">
            ${{renderIcon("rarity_ur", 20)}}
            <span>CARDFRONT × EVOLVE — Bilingual Card Identification & Art Appreciation Grimoire (鑑賞モード)</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <input id="cf-cid-search-input" type="search" placeholder="Search BP05-110 SR, 機構翼の少女・ローザ, Set 1..." style="background:#090e1c;border:1px solid #38bdf8;color:#f8fafc;border-radius:8px;padding:5px 10px;font-size:12px;width:240px;" />
            <button id="cf-cid-close-btn" type="button" style="background:rgba(239,68,68,0.2);border:1px solid #f87171;color:#fecaca;border-radius:8px;padding:5px 12px;font-size:12px;font-weight:800;cursor:pointer;">Close</button>
          </div>
        </div>
        <div class="cf-cid-body">
          <div class="cf-collector-slab-stage">
            <div id="cf-collector-slab-card" class="cf-collector-slab-card">
              <img id="cf-collector-slab-art" class="cf-collector-slab-art" src="GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png" alt="Collector Card Full-Bleed 600x800 Portrait" />
              <div id="cf-collector-foil-sheen" class="cf-collector-foil-sheen"></div>
              <div id="cf-collector-hud-overlay" class="cf-collector-hud-overlay">
                <div class="cf-collector-slab-TopRow">
                  <span id="cf-slab-set-badge" class="cf-slab-badge">BP05-110 SR</span>
                  <div id="cf-slab-nesw-diamond" class="cf-slab-nesw-diamond">
                    <span></span><span id="cf-slab-n">7</span><span></span>
                    <span id="cf-slab-w">7</span><span>${{renderIcon("evolve_crest", 12)}}</span><span id="cf-slab-e">8</span>
                    <span></span><span id="cf-slab-s">6</span><span></span>
                  </div>
                </div>
                <div class="cf-slab-bottom-plate">
                  <div id="cf-slab-jp-name" class="cf-slab-jp-name">機構翼の少女・ローザ(進化前)</div>
                  <div id="cf-slab-en-name" class="cf-slab-en-name">Rosa, Mechanized Wing Maiden (Unevolved)</div>
                  <div class="cf-slab-serial-row">
                    <span id="cf-slab-edition">1st Edition · 初版</span>
                    <span id="cf-slab-serial">#0001 / 0500</span>
                  </div>
                </div>
              </div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;width:100%;">
              <button id="cf-cid-evolve-btn" type="button" class="cf-cid-pill-btn" style="border-color:#00e5ff;color:#67e8f9;">
                ${{renderIcon("evolve_crest", 14, "margin-right:4px;")}}Toggle 進化前 ⇄ 進化後 (Evolve)
              </button>
              <button id="cf-cid-appreciate-btn" type="button" class="cf-cid-pill-btn" style="border-color:#ffb800;color:#fde68a;">
                ${{renderIcon("rarity_ur", 14, "margin-right:4px;")}}Full-Bleed Art View (鑑賞モード)
              </button>
            </div>
            <div style="font-size:10.5px;color:#94a3b8;text-align:center;">
              Move cursor across slab for 3D Holographic Foil Loupe · Locked 600×800 (3:4) Full-Bleed Portrait
            </div>
          </div>
          <div style="display:flex;flex-direction:column;min-width:0;">
            <div class="cf-cid-preset-row" id="cf-cid-preset-row">
              <button type="button" class="cf-cid-pill-btn" data-cid="bp05_110_rosa">BP05-110 SR · 機構翼の少女・ローザ(進化前)</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="h_archangel">BP01-001 LG · Kaelen Sky-Knight</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="h_valkyrie">BP01-002 SR · Valkyrie Ignis</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="h_lunar">BP01-003 LG · Celeste Lunar Oracle</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="h_seraph">BP01-008 UR · Seraph Dawn-Warden</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="b_leviathan">BP02-004 UR · Abyssal Leviathan</button>
              <button type="button" class="cf-cid-pill-btn" data-cid="set1_001">Set 1 #001 · Sky-Citadel Vanguard</button>
            </div>
            <div id="cf-cid-spec-table-wrap"></div>
            <div id="cf-cid-lore-wrap" class="cf-cid-lore-box"></div>
            <div id="cf-cid-art-notes-wrap" class="cf-cid-art-notes"></div>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const slab = modal.querySelector("#cf-collector-slab-card");
    const sheen = modal.querySelector("#cf-collector-foil-sheen");
    if (slab && sheen) {{
      slab.addEventListener("pointermove", function (ev) {{
        const rect = slab.getBoundingClientRect();
        const nx = ((ev.clientX - rect.left) / Math.max(1, rect.width)) - 0.5;
        const ny = ((ev.clientY - rect.top) / Math.max(1, rect.height)) - 0.5;
        const rotY = (nx * 18).toFixed(2);
        const rotX = (-ny * 16).toFixed(2);
        slab.style.transform = `rotateX(${{rotX}}deg) rotateY(${{rotY}}deg) scale(1.02)`;
        const angle = Math.round(115 + nx * 55 + ny * 35);
        sheen.style.background = `linear-gradient(${{angle}}deg, rgba(255,255,255,0) 15%, rgba(0,229,255,0.28) 42%, rgba(255,184,0,0.34) 50%, rgba(168,85,247,0.26) 58%, rgba(255,255,255,0) 85%)`;
      }});
      slab.addEventListener("pointerleave", function () {{
        slab.style.transform = "rotateX(0deg) rotateY(0deg) scale(1)";
      }});
    }}

    modal.querySelector("#cf-cid-close-btn").addEventListener("click", closeCardIdModal);
    modal.querySelector("#cf-cid-evolve-btn").addEventListener("click", function () {{
      evolveCardState(activeCardKey);
    }});
    modal.querySelector("#cf-cid-appreciate-btn").addEventListener("click", function () {{
      toggleArtAppreciationMode();
    }});
    const searchInput = modal.querySelector("#cf-cid-search-input");
    searchInput.addEventListener("input", function () {{
      const val = searchInput.value.trim();
      if (val) {{
        const found = lookupCard(val);
        if (found) {{
          activeCardKey = found.card_id || found.id || "bp05_110_rosa";
          renderModalCardView();
        }}
      }}
    }});
    modal.querySelectorAll("#cf-cid-preset-row [data-cid]").forEach(function (btn) {{
      btn.addEventListener("click", function () {{
        activeCardKey = btn.getAttribute("data-cid") || "bp05_110_rosa";
        showEvolvedState = false;
        renderModalCardView();
      }});
    }});

    return modal;
  }}

  function renderModalCardView() {{
    const modal = ensureModalBuilt();
    const rec = resolveDisplayRecord(activeCardKey, showEvolvedState);
    const slab = modal.querySelector("#cf-collector-slab-card");
    const artEl = modal.querySelector("#cf-collector-slab-art");
    const badgeEl = modal.querySelector("#cf-slab-set-badge");
    const jpEl = modal.querySelector("#cf-slab-jp-name");
    const enEl = modal.querySelector("#cf-slab-en-name");
    const edEl = modal.querySelector("#cf-slab-edition");
    const serEl = modal.querySelector("#cf-slab-serial");
    const specWrap = modal.querySelector("#cf-cid-spec-table-wrap");
    const loreWrap = modal.querySelector("#cf-cid-lore-wrap");
    const notesWrap = modal.querySelector("#cf-cid-art-notes-wrap");

    if (slab) {{
      slab.classList.toggle("evolved-glow", !!showEvolvedState);
      slab.classList.toggle("art-appreciation-mode", !!artAppreciationMode);
    }}
    if (artEl) {{
      artEl.src = rec.art_path || "GeneratedArt/EvolveMechWingMaidens/ev_01_base_rosalia_mech_wing_maiden.png";
    }}
    if (badgeEl) {{
      badgeEl.innerHTML = `${{renderIcon(rarityIconKey(rec.rarity), 13)}} ${{rec.card_number || "BP05-110 SR"}}`;
    }}
    const nesw = Array.isArray(rec.nesw) ? rec.nesw : [7, 8, 6, 7];
    const nEl = modal.querySelector("#cf-slab-n");
    const eEl = modal.querySelector("#cf-slab-e");
    const sEl = modal.querySelector("#cf-slab-s");
    const wEl = modal.querySelector("#cf-slab-w");
    if (nEl) nEl.textContent = nesw[0];
    if (eEl) eEl.textContent = nesw[1];
    if (sEl) sEl.textContent = nesw[2];
    if (wEl) wEl.textContent = nesw[3];

    if (jpEl) jpEl.textContent = rec.original_title || "機構翼の少女・ローザ(進化前)";
    if (enEl) enEl.textContent = rec.title || rec.name || "Rosa, Mechanized Wing Maiden";
    const prov = rec.collector_provenance || {{}};
    if (edEl) edEl.textContent = prov.edition || "1st Edition · 初版";
    if (serEl) serEl.textContent = prov.serial_mint || "#0001 / 0500";

    if (specWrap) {{
      specWrap.innerHTML = formatCollectorSpecTable(rec, showEvolvedState);
    }}
    if (loreWrap) {{
      loreWrap.innerHTML = `
        <div style="font-weight:800;color:#e9d5ff;margin-bottom:4px;">${{renderIcon("evolve_crest", 14, "margin-right:4px;")}}Bilingual Collector Lore & Story Memory</div>
        <div style="color:#f8fafc;margin-bottom:4px;">${{rec.lore_jp || "「この小さな真鍮の翼じゃ、まだ蒼穹には届かないって言うけれど……夕暮れの風を感じるだけで、こんなにも胸が高鳴るの！」"}}</div>
        <div style="color:#cbd5e1;font-style:italic;">${{rec.lore_en || "\\"They say these brass pinions are too small for the heavens... yet just feeling the sunset breeze makes my heart soar!\\""}}</div>
      `;
    }}
    const ad = rec.atelier_art_direction || {{}};
    if (notesWrap) {{
      notesWrap.innerHTML = `
        <div style="font-weight:800;color:#67e8f9;margin-bottom:4px;">${{renderIcon("rarity_lg", 14, "margin-right:4px;")}}Atelier Art Direction, 2.5D Layering & Collector Provenance</div>
        <div><b>Chromatic Harmony:</b> ${{ad.faction_chromatic_harmony || "#00E5FF (Astral Cyan) & #FFB800 (Brass-Gold Filigree)"}}</div>
        <div><b>Morphological Craft:</b> ${{ad.morphological_brushwork_and_silhouette || "Stylized 7.0-head proportions, beveled cyber-magicite filigree, and full-bleed 600x800 portrait composition."}}</div>
        <div><b>2.5D Depth & Foil:</b> ${{prov.foil_treatment || "Gunmetal-Silver Filigree Cold-Foil + 3-Plane 2.5D Parallax"}} · <b>SHA-256 Seal:</b> <code>${{String(rec.sha256_collector_id || prov.sha256_collector_id || "").slice(0, 20)}}…</code></div>
      `;
    }}
  }}

  function openCardIdModal(initialQuery) {{
    ensureModalBuilt();
    if (initialQuery) {{
      const found = lookupCard(initialQuery);
      if (found) {{
        activeCardKey = found.card_id || found.id || "bp05_110_rosa";
      }}
    }}
    renderModalCardView();
    const modal = document.getElementById("cf-card-id-modal");
    if (modal) modal.classList.add("open");
    return resolveDisplayRecord(activeCardKey, showEvolvedState);
  }}

  function closeCardIdModal() {{
    const modal = document.getElementById("cf-card-id-modal");
    if (modal) modal.classList.remove("open");
  }}

  function toggleArtAppreciationMode(forceState) {{
    artAppreciationMode = typeof forceState === "boolean" ? forceState : !artAppreciationMode;
    renderModalCardView();
    return artAppreciationMode;
  }}

  function evolveCardState(cardId) {{
    if (cardId) {{
      const found = lookupCard(cardId);
      if (found) activeCardKey = found.card_id || found.id || activeCardKey;
    }}
    showEvolvedState = !showEvolvedState;
    renderModalCardView();
    if (globalScope.SynapseSakugaAnimEngine && typeof globalScope.SynapseSakugaAnimEngine.triggerCaptureFlip180 === "function") {{
      try {{ globalScope.SynapseSakugaAnimEngine.triggerCaptureFlip180(0, "player"); }} catch (_e) {{}}
    }}
    return resolveDisplayRecord(activeCardKey, showEvolvedState);
  }}

  function decorateRenderedCards() {{
    registerCollectorIcons();
    ensureStylesInjected();

    const topDrawer = document.querySelector(".top-utility-drawer") || document.querySelector(".header-actions");
    if (topDrawer && !document.getElementById("btn-card-id-catalog")) {{
      const btn = document.createElement("button");
      btn.id = "btn-card-id-catalog";
      btn.type = "button";
      btn.className = "utility-pill-btn";
      btn.style.cssText = "background:rgba(15,23,42,0.92);border:1px solid #ffb800;color:#fde68a;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;gap:4px;";
      btn.innerHTML = `${{renderIcon("rarity_sr", 13)}}Card ID · 鑑賞`;
      btn.addEventListener("click", function () {{
        openCardIdModal("bp05_110_rosa");
      }});
      topDrawer.appendChild(btn);
    }}

    document.querySelectorAll(".hand-card, .board-card").forEach(function (cardEl) {{
      if (cardEl.querySelector(".cf-card-collector-microstamp")) return;
      const cid = cardEl.getAttribute("data-card-id") || cardEl.getAttribute("data-id") || "h_archangel";
      const rec = lookupCard(cid);
      if (!rec) return;
      const stamp = document.createElement("div");
      stamp.className = "cf-card-collector-microstamp";
      stamp.textContent = rec.card_number || "BP01-001 LG";
      cardEl.appendChild(stamp);
    }});
  }}

  const api = {{
    VERSION: "1.0.0",
    CATALOG: RAW_RECORDS,
    COLLECTOR_SVG_BODIES: COLLECTOR_SVG_BODIES,
    lookupCard: lookupCard,
    resolveDisplayRecord: resolveDisplayRecord,
    formatCollectorPlainText: formatCollectorPlainText,
    formatCollectorSpecTable: formatCollectorSpecTable,
    openCardIdModal: openCardIdModal,
    closeCardIdModal: closeCardIdModal,
    toggleArtAppreciationMode: toggleArtAppreciationMode,
    evolveCardState: evolveCardState,
    decorateRenderedCards: decorateRenderedCards
  }};

  globalScope.SynapseCardIdCatalog = api;
  globalScope.openCardIdModal = openCardIdModal;
  globalScope.closeCardIdModal = closeCardIdModal;

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", function () {{
      decorateRenderedCards();
    }});
  }} else {{
    decorateRenderedCards();
  }}
}})(typeof window !== "undefined" ? window : globalThis);
"""
    OUT_JS_PATH.write_text(js_source, encoding="utf-8")
    print(f"Wrote {OUT_JS_PATH} ({OUT_JS_PATH.stat().st_size} bytes, {len(records)} records)")


if __name__ == "__main__":
    build_js()
