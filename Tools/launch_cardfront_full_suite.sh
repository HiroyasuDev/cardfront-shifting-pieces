#!/usr/bin/env zsh
# ============================================================================
# launch_cardfront_full_suite.sh
# ============================================================================
# Single-command turnkey launcher for CARDFRONT: Cradle of Echoes across:
#   1. Owned 45-File Node.js TcgEngineAPI Daemon (TxLock + 12-Match 4-Faction ELO Tournament)
#   2. WebPlayable HTTP Server (port 8765)
#   3. Compiled Unity 6 (6000.6.8f1) Standalone macOS Mach-O Bundles:
#      - CARDFRONT_TcgEngine_Full3D.app
#      - CARDFRONT_CradleOfEchoes.app
#
# Usage:
#   ./Tools/launch_cardfront_full_suite.sh [--check-only] [--open-apps]
# ============================================================================
set -euo pipefail

SYNAPSE_ROOT="/Users/frederickamina/Documents/Projects/synapse/unity-tcg-engine"
UNPACKED_ROOT="/Users/frederickamina/Documents/Projects/synapse/tcg-engine-unpacked"
FULL3D_APP="$UNPACKED_ROOT/Builds/MacOS/CARDFRONT_TcgEngine_Full3D.app"
CRADLE_APP="$SYNAPSE_ROOT/Builds/MacOS/CARDFRONT_CradleOfEchoes.app"
WEB_HTML="$SYNAPSE_ROOT/WebPlayable/cardfront_cradle_of_echoes_playable.html"
TOURNAMENT_JS="$UNPACKED_ROOT/TcgEngineAPI/run_4faction_elo_tournament.js"
DUEL_JS="$UNPACKED_ROOT/TcgEngineAPI/run_fullstack_live_duel.js"

CHECK_ONLY=0
OPEN_APPS=0
for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    --open-apps)  OPEN_APPS=1 ;;
  esac
done

echo "[CARDFRONT Turnkey Suite] Verifying compiled Unity 6 Mach-O bundles & WebPlayable..."
test -d "$FULL3D_APP" || { echo "ERROR: Missing $FULL3D_APP"; exit 1; }
test -d "$CRADLE_APP" || { echo "ERROR: Missing $CRADLE_APP"; exit 1; }
test -f "$WEB_HTML"   || { echo "ERROR: Missing $WEB_HTML"; exit 1; }
test -f "$TOURNAMENT_JS" || { echo "ERROR: Missing $TOURNAMENT_JS"; exit 1; }

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo '{"status":"PASS_TURNKEY_SUITE_READY","full3d_app":"'"$FULL3D_APP"'","cradle_app":"'"$CRADLE_APP"'","web_playable":"http://127.0.0.1:8765/cardfront_cradle_of_echoes_playable.html"}'
  exit 0
fi

echo "[CARDFRONT Turnkey Suite] Running 4-Faction Double Round-Robin ELO Tournament on TcgEngineAPI..."
node "$TOURNAMENT_JS" > /dev/null

echo "[CARDFRONT Turnkey Suite] Running Full-Stack Live Duel & Echo-Ghost Verification..."
node "$DUEL_JS" > /dev/null

if ! lsof -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[CARDFRONT Turnkey Suite] Starting WebPlayable HTTP Server on http://127.0.0.1:8765 ..."
  (cd "$SYNAPSE_ROOT" && nohup python3 WebPlayable/serve_playtest.py >/dev/null 2>&1 &)
  sleep 1
fi

if [[ "$OPEN_APPS" -eq 1 ]]; then
  open "$FULL3D_APP" || true
  open "http://127.0.0.1:8765/cardfront_cradle_of_echoes_playable.html" || true
fi

echo '{"status":"PASS_TURNKEY_SUITE_LAUNCHED","full3d_app":"'"$FULL3D_APP"'","cradle_app":"'"$CRADLE_APP"'","web_playable_url":"http://127.0.0.1:8765/cardfront_cradle_of_echoes_playable.html"}'
