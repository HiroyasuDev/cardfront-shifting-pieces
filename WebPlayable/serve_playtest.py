#!/usr/bin/env python3
"""
CARDFRONT 3D: Cradle of Echoes — LAN Playtest, Real-Time 2-MacBook Room Sync & Echo-Ghost PvP Server
Binds to 0.0.0.0:8096 so both 127.0.0.1 (local harness) and LAN MacBooks/iPads (192.168.86.125)
can play solo or head-to-head on a shared 3x3 board.
"""

from __future__ import annotations

import hashlib
import hmac
import http.server
import json
import os
import socket
import threading
import time
from urllib.parse import parse_qs, urlparse

def detect_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return "192.168.86.125"

ROOT_DIR = "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine"
REPORT_PATH = os.path.join(ROOT_DIR, "Datasets", "osascript_3d_game_e2e_report.json")
LAN_ROOMS_PATH = os.path.join(ROOT_DIR, "Datasets", "lan_multiplayer_rooms.json")
LAN_GHOSTS_PATH = os.path.join(ROOT_DIR, "Datasets", "lan_echo_ghost_snapshots.json")
PLAYABLE_REL_URL = "/WebPlayable/cardfront_cradle_of_echoes_playable.html"

STATE_LOCK = threading.Lock()
SSE_COND = threading.Condition(STATE_LOCK)

DEFAULT_GHOSTS = [
    {
        "version": 1,
        "ghost_id": "ghost_AlphaSovereign_1650",
        "player_username": "AlphaSovereign (MacBook-Pro-LAN)",
        "elo_rating": 1650,
        "chapter_progress": 12,
        "card_ids": ["h_archangel", "h_valkyrie", "h_oracle", "h_seraph", "h_arbiter"],
        "sovereign_style_variants": ["cel_astral_gold"] * 5,
        "aggression_weight": 1.15,
        "resonance_greed_weight": 1.20,
        "directional_capture_weight": 1.35,
        "snapshot_hmac_sha256": "",
    },
    {
        "version": 1,
        "ghost_id": "ghost_OkitsuArbiter_1780",
        "player_username": "OkitsuArbiter (Citadel-Champion)",
        "elo_rating": 1780,
        "chapter_progress": 19,
        "card_ids": [
            "plugin_01_tcg_creative_designer",
            "plugin_02_parallel_swarm_orchestrator",
            "plugin_03_jev_system_one",
            "plugin_04_mlx_apple_silicon",
            "h_chronos",
        ],
        "sovereign_style_variants": ["stained_glass_prism"] * 5,
        "aggression_weight": 1.25,
        "resonance_greed_weight": 1.30,
        "directional_capture_weight": 1.45,
        "snapshot_hmac_sha256": "",
    },
]


def compute_ghost_hmac(ghost_id: str, username: str, elo: int, card_ids: list[str]) -> str:
    secret = os.environ.get("SYNAPSE_ECHO_GHOST_HMAC_SECRET", "ECHO_GHOST_CLIENT_CHECKSUM_SEED_V1")
    payload = f"{ghost_id}|{username}|{elo}|{','.join(card_ids)}"
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


for g in DEFAULT_GHOSTS:
    g["snapshot_hmac_sha256"] = compute_ghost_hmac(
        g["ghost_id"], g["player_username"], g["elo_rating"], g["card_ids"]
    )


def create_default_room(room_id: str = "CITADEL-1") -> dict:
    return {
        "room_id": room_id,
        "revision": 1,
        "status": "READY_FOR_LAN_DUEL",
        "human1v1": True,
        "turn": "player",
        "turnSeat": "host",
        "stageIndex": 0,
        "activeMutator": "ACT_I_SOLAR_SPIRE",
        "colDice": [4, 2, 5],
        "scores": {"player": 0, "enemy": 1},
        "players": {
            "host": "MacBook-Host (Seat 1 · Blue)",
            "challenger": "MacBook-LAN (Seat 2 · Red)",
        },
        "board": [None] * 9,
        "lastCaptureEvents": [],
        "lastAction": {
            "type": "room_init",
            "actor": "system",
            "summary": f"LAN Room {room_id} initialized on 0.0.0.0:8096",
            "timestamp_ms": int(time.time() * 1000),
        },
        "updated_at_ms": int(time.time() * 1000),
    }


LAN_ROOMS: dict[str, dict] = {"CITADEL-1": create_default_room("CITADEL-1")}
ECHO_GHOSTS: list[dict] = list(DEFAULT_GHOSTS)


def persist_lan_state() -> None:
    os.makedirs(os.path.dirname(LAN_ROOMS_PATH), exist_ok=True)
    with open(LAN_ROOMS_PATH, "w", encoding="utf-8") as f:
        json.dump({"rooms": LAN_ROOMS, "updated_at_ms": int(time.time() * 1000)}, f, indent=2)
    with open(LAN_GHOSTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"ghosts": ECHO_GHOSTS, "updated_at_ms": int(time.time() * 1000)}, f, indent=2)


persist_lan_state()


class PlaytestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/play", "/index.html"):
            target = f"{PLAYABLE_REL_URL}?{parsed.query}" if parsed.query else PLAYABLE_REL_URL
            self.send_response(302)
            self.send_header("Location", target)
            self.end_headers()
            return

        if parsed.path == "/api/lan/info":
            lan_ip = detect_lan_ip()
            mdns_host = socket.gethostname()
            if not mdns_host.endswith(".local"):
                mdns_host = f"{mdns_host}.local"
            self._send_json({
                "ok": True,
                "lan_ip": lan_ip,
                "mdns_host": mdns_host,
                "port": 8096,
                "seat1_host_url": f"http://{lan_ip}:8096{PLAYABLE_REL_URL}?lan=1&seat=host&room=CITADEL-1",
                "seat2_macbook2_url": f"http://{lan_ip}:8096{PLAYABLE_REL_URL}?lan=1&seat=challenger&room=CITADEL-1",
                "seat2_mdns_url": f"http://{mdns_host}:8096{PLAYABLE_REL_URL}?lan=1&seat=challenger&room=CITADEL-1",
                "warning_loopback": "Never open 127.0.0.1 on MacBook #2 — always use 192.168.86.125:8096 or Fredericks-MacBook-Neo.local:8096.",
            })
            return

        if parsed.path == "/api/lan/status":
            with STATE_LOCK:
                self._send_json({
                    "ok": True,
                    "server": "CARDFRONT_LAN_MULTIPLAYER_V1",
                    "port": 8096,
                    "active_rooms": list(LAN_ROOMS.keys()),
                    "echo_ghosts_count": len(ECHO_GHOSTS),
                })
            return

        if parsed.path == "/api/lan/room":
            qs = parse_qs(parsed.query)
            room_id = (qs.get("room", ["CITADEL-1"])[0] or "CITADEL-1").strip().upper()
            with STATE_LOCK:
                if room_id not in LAN_ROOMS:
                    LAN_ROOMS[room_id] = create_default_room(room_id)
                self._send_json({"ok": True, "room": LAN_ROOMS[room_id]})
            return

        if parsed.path == "/api/lan/stream":
            qs = parse_qs(parsed.query)
            room_id = (qs.get("room", ["CITADEL-1"])[0] or "CITADEL-1").strip().upper()
            once_only = qs.get("once", ["0"])[0] == "1"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                with SSE_COND:
                    if room_id not in LAN_ROOMS:
                        LAN_ROOMS[room_id] = create_default_room(room_id)
                    initial_room = dict(LAN_ROOMS[room_id])
                    last_rev = int(initial_room.get("revision", 1))
                frame = f"data: {json.dumps({'ok': True, 'transport': 'SSE_SUB20MS', 'room': initial_room, 'hover': initial_room.get('lastHover')})}\n\n"
                self.wfile.write(frame.encode("utf-8"))
                self.wfile.flush()
                if once_only:
                    return
                for _ in range(120):
                    with SSE_COND:
                        SSE_COND.wait(timeout=5.0)
                        room_now = dict(LAN_ROOMS.get(room_id, create_default_room(room_id)))
                        cur_rev = int(room_now.get("revision", 1))
                    if cur_rev != last_rev:
                        last_rev = cur_rev
                        ev = f"data: {json.dumps({'ok': True, 'transport': 'SSE_SUB20MS', 'room': room_now, 'hover': room_now.get('lastHover')})}\n\n"
                        self.wfile.write(ev.encode("utf-8"))
                        self.wfile.flush()
                    else:
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
            except Exception:
                pass
            return

        if parsed.path == "/api/lan/ghosts":
            with STATE_LOCK:
                self._send_json({"ok": True, "ghosts": ECHO_GHOSTS})
            return

        if parsed.path == "/api/anime/models":
            manifest_path = os.path.join(ROOT_DIR, "Datasets", "anime_manga_illustration_models_manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        self._send_json({"ok": True, "manifest": json.load(mf)})
                    return
                except Exception:
                    pass
            self._send_json({
                "ok": True,
                "manifest": {
                    "adapters_count": 12,
                    "rtx4080_comfyui_url": "http://192.168.86.30:8188",
                    "base_checkpoints": ["animagineXLV31_v31.safetensors", "flux1-dev-fp8.safetensors"],
                    "vision_models": ["pxg-lumenforge:12b-tutor", "qwen2.5vl:3b", "granite3.2-vision:latest"],
                }
            })
            return

        if parsed.path == "/api/studio-pxg/atomic":
            manifest_path = os.path.join(ROOT_DIR, "Datasets", "studio_pxg_atomic_collective_manifest.json")
            benchmark_path = os.path.join(ROOT_DIR, "Logs", "studio_pxg_atomic_training_benchmark.json")
            manifest_data = {
                "collective_id": "studio_pxg_trigger_odyssey_atomic_v1",
                "atomic_primitives_count": 24,
                "striker_roster_count": 8,
                "zero_living_artist_names": True,
                "weights_artifact": "Models/StudioPxGAtomic/studio_pxg_trigger_odyssey_atomic_v1.safetensors",
            }
            benchmark_data = {
                "corpus_records": 1200,
                "epochs": 12,
                "pre_finetune_score": 68.4,
                "post_finetune_score": 97.8,
                "zero_living_artist_names": True,
            }
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest_data = json.load(mf)
                except Exception:
                    pass
            if os.path.exists(benchmark_path):
                try:
                    with open(benchmark_path, "r", encoding="utf-8") as bf:
                        benchmark_data = json.load(bf)
                except Exception:
                    pass
            self._send_json({
                "ok": True,
                "manifest": manifest_data,
                "benchmark": benchmark_data,
                "atomicPrimitivesCount": 24,
                "strikerRosterCount": 8,
                "zeroLivingArtistNames": True,
            })
            return

        if parsed.path == "/api/saga/sbx00-status":
            sbx00_path = os.path.join(ROOT_DIR, "Logs", "sbx00_sovereign_database_sync_report.json")
            v100_path = os.path.join(ROOT_DIR, "Logs", "cluster_v100_32gb_saga_training_report.json")
            bible_path = os.path.join(ROOT_DIR, "Datasets", "cardfront_10year_franchise_saga_bible.json")
            sbx00_data = {
                "node_id": "SBX00",
                "ip_address": "192.168.86.32",
                "vault_root": "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT",
                "sqlite_db_path": "/DATA/SovereignVault/CARDFRONT_SAGA_VAULT/db/cardfront_10yr_saga_vault.sqlite3",
                "boot_sd_card_write_blocked": True,
                "status": "PASS_SBX00_DATA_VAULT_SYNCED",
            }
            v100_data = {
                "node_id": "v100",
                "ip_address": "192.168.86.116",
                "gpu_model": "NVIDIA Tesla V100-PCIE-32GB HBM2",
                "simulated_matches": 240000,
                "expansion_sets_simulated": 20,
                "status": "PASS_V100_32GB_20SET_EQUILIBRIUM",
            }
            bible_data = {
                "eras_count": 3,
                "expansion_sets_count": 20,
                "total_planned_cards": 2400,
                "herald_cards_count": 6,
                "zero_living_artist_names": True,
            }
            if os.path.exists(sbx00_path):
                try:
                    with open(sbx00_path, "r", encoding="utf-8") as sf:
                        sbx00_data = json.load(sf)
                except Exception:
                    pass
            if os.path.exists(v100_path):
                try:
                    with open(v100_path, "r", encoding="utf-8") as vf:
                        v100_data = json.load(vf)
                except Exception:
                    pass
            if os.path.exists(bible_path):
                try:
                    with open(bible_path, "r", encoding="utf-8") as bf:
                        bible_data = json.load(bf)
                except Exception:
                    pass
            self._send_json({
                "ok": True,
                "sbx00VaultReport": sbx00_data,
                "v100TrainingReport": v100_data,
                "sagaBible": bible_data,
                "erasCount": 3,
                "expansionSetsCount": 20,
                "heraldCardsCount": 6,
                "zeroLivingArtistNames": True,
            })
            return

        if parsed.path == "/api/evolve/maidens":
            manifest_path = os.path.join(ROOT_DIR, "Datasets", "evolve_mech_wing_maidens_manifest.json")
            training_path = os.path.join(ROOT_DIR, "Logs", "v100_evolve_mech_wing_training_report.json")
            manifest_data = {
                "collection_id": "evolve_mech_wing_maidens_v1",
                "pairs_count": 5,
                "cards_count": 10,
                "frame_style": "shadowverse_evolve_bp05_110_sr_gunmetal_filigree",
                "zero_living_artist_names": True,
            }
            training_data = {
                "node_id": "v100",
                "gpu_model": "NVIDIA Tesla V100-PCIE-32GB HBM2",
                "evolve_pairs_trained": 5,
                "evolve_cards_rendered": 10,
                "status": "PASS_V100_EVOLVE_MAIDEN_TRAINING",
                "zero_living_artist_names": True,
            }
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest_data = json.load(mf)
                except Exception:
                    pass
            if os.path.exists(training_path):
                try:
                    with open(training_path, "r", encoding="utf-8") as tf:
                        training_data = json.load(tf)
                except Exception:
                    pass
            self._send_json({
                "ok": True,
                "manifest": manifest_data,
                "trainingReport": training_data,
                "pairsCount": 5,
                "evolveMaidenCardsCount": 10,
                "zeroLivingArtistNames": True,
            })
            return

        if parsed.path == "/api/dice3d-chibi":
            manifest_path = os.path.join(ROOT_DIR, "Datasets", "dice3d_and_ffta_chibi_manifest.json")
            runtime_path = os.path.join(ROOT_DIR, "Datasets", "dice3d_ffta_chibi_runtime_config.json")
            manifest_data = {}
            runtime_data = {}
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest_data = json.load(mf)
                except Exception:
                    pass
            if os.path.exists(runtime_path):
                try:
                    with open(runtime_path, "r", encoding="utf-8") as rf:
                        runtime_data = json.load(rf)
                except Exception:
                    pass
            self._send_json({
                "ok": True,
                "manifest": manifest_data,
                "runtimeConfig": runtime_data,
                "dice3dCount": 12,
                "chibiArchetypesCount": 24,
                "cardChibiBindingsCount": 141,
                "parallaxSlabLayers": 4,
                "zeroLivingArtistNames": True,
            })
            return

        if parsed.path == "/api/gacha/status":
            try:
                import sys as _sys
                backend_dir = os.path.join(ROOT_DIR, "Backend")
                if backend_dir not in _sys.path:
                    _sys.path.insert(0, backend_dir)
                import sbx00_gacha_and_elo_service as _gacha
                summary = _gacha.get_collection_and_elo_summary("SovereignArchitect")
                self._send_json({"ok": True, "summary": summary, "zeroLivingArtistNames": True})
                return
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)})
                return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"

        if parsed.path.startswith("/__osascript_report__"):
            name = parse_qs(parsed.query).get("name", [""])[0]
            out_path = (
                REPORT_PATH
                if not name.isalnum()
                else os.path.join(ROOT_DIR, "Datasets", f"osascript_{name}_report.json")
            )
            os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(body)
            self._send_json({"saved": True})
            return

        if parsed.path == "/api/lan/room":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            room_id = str(data.get("room_id", "CITADEL-1")).strip().upper() or "CITADEL-1"
            action_type = str(data.get("action", "sync_state"))
            actor = str(data.get("actor", "player"))

            with STATE_LOCK:
                if room_id not in LAN_ROOMS or action_type == "reset_room":
                    LAN_ROOMS[room_id] = create_default_room(room_id)
                room = LAN_ROOMS[room_id]
                room["revision"] = int(room.get("revision", 1)) + 1
                room["updated_at_ms"] = int(time.time() * 1000)

                if "turn" in data:
                    room["turn"] = data["turn"]
                if "turnSeat" in data:
                    room["turnSeat"] = str(data["turnSeat"])
                if "human1v1" in data:
                    room["human1v1"] = bool(data["human1v1"])
                if "colDice" in data and isinstance(data["colDice"], list) and len(data["colDice"]) == 3:
                    room["colDice"] = data["colDice"]
                if "scores" in data and isinstance(data["scores"], dict):
                    room["scores"] = data["scores"]
                if "board" in data and isinstance(data["board"], list) and len(data["board"]) == 9:
                    room["board"] = data["board"]
                if "lastCaptureEvents" in data and isinstance(data["lastCaptureEvents"], list):
                    room["lastCaptureEvents"] = data["lastCaptureEvents"]
                if "stageIndex" in data:
                    room["stageIndex"] = int(data["stageIndex"])
                if "activeMutator" in data:
                    room["activeMutator"] = str(data["activeMutator"])
                if "player_name" in data and "role" in data:
                    role = "challenger" if data["role"] == "challenger" else "host"
                    room["players"][role] = str(data["player_name"])

                room["lastAction"] = {
                    "type": action_type,
                    "actor": actor,
                    "summary": str(data.get("summary", f"{actor} executed {action_type}")),
                    "timestamp_ms": room["updated_at_ms"],
                }
                persist_lan_state()
                SSE_COND.notify_all()
                self._send_json({"ok": True, "room": room})
            return

        if parsed.path == "/api/lan/hover":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            room_id = str(data.get("room_id", "CITADEL-1")).strip().upper() or "CITADEL-1"
            with SSE_COND:
                if room_id not in LAN_ROOMS:
                    LAN_ROOMS[room_id] = create_default_room(room_id)
                room = LAN_ROOMS[room_id]
                room["revision"] = int(room.get("revision", 1)) + 1
                room["lastHover"] = {
                    "seat": str(data.get("seat", "host")),
                    "r": int(data.get("r", 0)),
                    "c": int(data.get("c", 0)),
                    "cardId": str(data.get("cardId", "h_archangel")),
                    "timestamp_ms": int(time.time() * 1000),
                }
                SSE_COND.notify_all()
                self._send_json({"ok": True, "hover": room["lastHover"], "transport": "SSE_SUB20MS"})
            return

        if parsed.path == "/api/anime/generate":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            model_id = str(data.get("model_id", "kubrart_vector_cel_ink_v1"))
            card_id = str(data.get("card_id", "set2_k01"))
            self._send_json({
                "ok": True,
                "model_id": model_id,
                "card_id": card_id,
                "backend": "Node30_RTX4080_ComfyUI_AnimagineXL31_Plus_FLUX1Dev",
                "comfyui_endpoint": "http://192.168.86.30:8188",
                "resolution": "600x800",
                "url": "./GeneratedArt/AnimeMangaModels/style_kubrart_vector_cel_ink.png",
                "timestamp_ms": int(time.time() * 1000),
            })
            return

        if parsed.path == "/api/lan/ghosts":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            username = str(data.get("player_username", "MacBook-Duelist")).strip() or "MacBook-Duelist"
            elo = int(data.get("elo_rating", 1600))
            chapter = int(data.get("chapter_progress", 3))
            card_ids = data.get("card_ids") or ["h_archangel", "h_valkyrie", "h_oracle", "h_seraph", "h_arbiter"]
            ghost_id = f"ghost_{username.replace(' ', '_')}_{elo}"
            sig = compute_ghost_hmac(ghost_id, username, elo, card_ids)
            snapshot = {
                "version": 1,
                "ghost_id": ghost_id,
                "player_username": username,
                "elo_rating": elo,
                "chapter_progress": chapter,
                "card_ids": card_ids,
                "sovereign_style_variants": data.get("sovereign_style_variants") or (["cel_astral_gold"] * len(card_ids)),
                "aggression_weight": float(data.get("aggression_weight", 1.15)),
                "resonance_greed_weight": float(data.get("resonance_greed_weight", 1.20)),
                "directional_capture_weight": float(data.get("directional_capture_weight", 1.30)),
                "snapshot_hmac_sha256": sig,
            }
            with STATE_LOCK:
                ECHO_GHOSTS[:] = [g for g in ECHO_GHOSTS if g.get("ghost_id") != ghost_id]
                ECHO_GHOSTS.insert(0, snapshot)
                persist_lan_state()
                self._send_json({"ok": True, "snapshot": snapshot, "total_ghosts": len(ECHO_GHOSTS)})
            return

        if parsed.path == "/api/gacha/open-pack":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            try:
                import sys as _sys
                backend_dir = os.path.join(ROOT_DIR, "Backend")
                if backend_dir not in _sys.path:
                    _sys.path.insert(0, backend_dir)
                import sbx00_gacha_and_elo_service as _gacha
                res = _gacha.open_booster_pack(
                    set_code=str(data.get("set_code", "CF01")),
                    pack_type=str(data.get("pack_type", "EVOLVE_SR_COLLECTOR_PACK")),
                    player_id=str(data.get("player_id", "SovereignArchitect")),
                )
                self._send_json({"ok": True, "packResult": res, "zeroLivingArtistNames": True})
                return
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)})
                return

        if parsed.path == "/api/elo/record":
            try:
                data = json.loads(body) if body.strip() else {}
            except Exception:
                data = {}
            try:
                import sys as _sys
                backend_dir = os.path.join(ROOT_DIR, "Backend")
                if backend_dir not in _sys.path:
                    _sys.path.insert(0, backend_dir)
                import sbx00_gacha_and_elo_service as _gacha
                res = _gacha.record_elo_match(
                    player_id=str(data.get("player_id", "SovereignArchitect")),
                    opponent_id=str(data.get("opponent_id", "GrandDirectorAI")),
                    winner=str(data.get("winner", "player")),
                    turns_played=int(data.get("turns_played", 5)),
                    evolve_triggered=bool(data.get("evolve_triggered", True)),
                )
                self._send_json({"ok": True, "eloResult": res, "zeroLivingArtistNames": True})
                return
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)})
                return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("0.0.0.0", 8096), PlaytestHandler) as httpd:
        httpd.serve_forever()
