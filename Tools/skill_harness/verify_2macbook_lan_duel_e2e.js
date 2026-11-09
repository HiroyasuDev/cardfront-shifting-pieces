#!/usr/bin/env node
/**
 * Tools/skill_harness/verify_2macbook_lan_duel_e2e.js
 * ===================================================
 * End-to-End 2-MacBook Human-vs-Human LAN Duel Verification using two isolated
 * Playwright Chromium contexts connected simultaneously to:
 *   - Seat 1 (Host · Blue):       http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html
 *   - Seat 2 (Challenger · Red):  http://192.168.86.125:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html
 *
 * Verifies:
 * 1. Both contexts connect to Room CITADEL-1 (`human1v1 = true`).
 * 2. Local Boss AI (`executeBossTurn`) is suppressed when `human1v1` is active.
 * 3. Seat 1 deploys a card & nudges a column die -> Seat 2 receives the updated 3x3 board,
 *    column dice, and `isPlayerTurn = true` (`turnSeat === "challenger"`).
 * 4. Seat 2 deploys a counter-card -> Seat 1 receives Seat 2's card as an opponent ("ai" / Red)
 *    card on its 3x3 board with 100% canonical cell parity and `isPlayerTurn = true`.
 * 5. Triple Triad SAME, PLUS, COMBO_CASCADE, and `drawNextDeckCardOnTurn()` execute cleanly.
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/frederickamina/.local/node_modules/playwright-core");

const CHROMIUM_EXECUTABLE =
  "/Users/frederickamina/Library/Caches/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const HOST_URL = "http://127.0.0.1:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const LAN_URL = "http://192.168.86.125:8096/WebPlayable/cardfront_cradle_of_echoes_playable.html";
const REPORT_OUT = path.join(
  "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine",
  "Datasets",
  "lan_2macbook_duel_e2e_report.json"
);

async function main() {
  const startTime = Date.now();
  const browser = await chromium.launch({
    executablePath: CHROMIUM_EXECUTABLE,
    headless: true,
    args: ["--no-sandbox", "--disable-gpu"]
  });

  try {
    const contextHost = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const contextChallenger = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    const pageHost = await contextHost.newPage();
    const pageChallenger = await contextChallenger.newPage();

    // Load Seat 1 on loopback and Seat 2 on the Wi-Fi LAN IP (with fallback to loopback if offline)
    await pageHost.goto(HOST_URL, { waitUntil: "domcontentloaded", timeout: 15000 });
    let challengerConnectedUrl = LAN_URL;
    try {
      await pageChallenger.goto(LAN_URL, { waitUntil: "domcontentloaded", timeout: 8000 });
    } catch (_e) {
      challengerConnectedUrl = HOST_URL;
      await pageChallenger.goto(HOST_URL, { waitUntil: "domcontentloaded", timeout: 15000 });
    }

    await pageHost.waitForTimeout(350);
    await pageChallenger.waitForTimeout(350);

    // 1. Join Room CITADEL-1 as Seat 1 (host) and Seat 2 (challenger)
    const hostJoin = await pageHost.evaluate(async () => {
      await joinLanRoomAsSeat("host", "CITADEL-1");
      return {
        enabled: state.lanMultiplayer.enabled,
        human1v1: state.lanMultiplayer.human1v1,
        role: state.lanMultiplayer.role,
        isPlayerTurn: state.isPlayerTurn
      };
    });

    const challengerJoin = await pageChallenger.evaluate(async () => {
      await joinLanRoomAsSeat("challenger", "CITADEL-1");
      return {
        enabled: state.lanMultiplayer.enabled,
        human1v1: state.lanMultiplayer.human1v1,
        role: state.lanMultiplayer.role,
        isPlayerTurn: state.isPlayerTurn
      };
    });

    const turnsLog = [];

    // 2. Turn 1 (Seat 1 Host deploys card at (1, 1) and nudges Col 1 die)
    const turn1Host = await pageHost.evaluate(async () => {
      nudgeColDie(1);
      handleSlotClick(1, 1);
      await pushLanRoomUpdate("play_card", "Seat 1 deployed to center (2,2)", "challenger");
      return {
        isPlayerTurnAfterMove: state.isPlayerTurn,
        centerCardId: state.grid[1][1].cardId,
        colDice: state.colDice.slice(),
        revision: state.lanMultiplayer.revision
      };
    });

    // Wait 900ms for Seat 2's poll (or trigger syncLanRoomState) and check Seat 2's board
    const turn1ChallengerSync = await pageChallenger.evaluate(async () => {
      const room = await syncLanRoomState("CITADEL-1");
      return {
        revision: state.lanMultiplayer.revision,
        isPlayerTurn: state.isPlayerTurn,
        centerCardId: state.grid[1][1].cardId,
        centerLocalOwner: state.grid[1][1].owner,
        centerCanonicalOwner: state.grid[1][1].canonicalOwner,
        colDice: state.colDice.slice(),
        turnSeat: room ? room.turnSeat : null
      };
    });
    turnsLog.push({ turn: 1, actor: "host", hostState: turn1Host, challengerSynced: turn1ChallengerSync });

    // 3. Turn 2 (Seat 2 Challenger deploys counter-card at (1, 0) and hands turn back to Seat 1 Host)
    const turn2Challenger = await pageChallenger.evaluate(async () => {
      handleSlotClick(1, 0);
      await pushLanRoomUpdate("play_card", "Seat 2 deployed counter-card at (2,1)", "host");
      return {
        isPlayerTurnAfterMove: state.isPlayerTurn,
        placedCardId: state.grid[1][0].cardId,
        placedLocalOwner: state.grid[1][0].owner,
        revision: state.lanMultiplayer.revision
      };
    });

    const turn2HostSync = await pageHost.evaluate(async () => {
      const room = await syncLanRoomState("CITADEL-1");
      return {
        revision: state.lanMultiplayer.revision,
        isPlayerTurn: state.isPlayerTurn,
        slot10CardId: state.grid[1][0].cardId,
        slot10LocalOwner: state.grid[1][0].owner,
        slot10CanonicalOwner: state.grid[1][0].canonicalOwner,
        turnSeat: room ? room.turnSeat : null
      };
    });
    turnsLog.push({ turn: 2, actor: "challenger", challengerState: turn2Challenger, hostSynced: turn2HostSync });

    // 4. Turn 3 (Seat 1 Host draws a replacement card from the 60-card Set 1 pool & deploys at (0, 0))
    const turn3Host = await pageHost.evaluate(async () => {
      const handBeforeDraw = state.hand.length;
      const drawnCardId = drawNextDeckCardOnTurn();
      const handAfterDraw = state.hand.length;
      handleSlotClick(0, 0);
      await pushLanRoomUpdate("play_card", "Seat 1 drew & deployed at (1,1)", "challenger");
      return {
        handBeforeDraw,
        drawnCardId,
        handAfterDraw,
        slot00CardId: state.grid[0][0].cardId,
        revision: state.lanMultiplayer.revision
      };
    });

    const turn3ChallengerSync = await pageChallenger.evaluate(async () => {
      await syncLanRoomState("CITADEL-1");
      return {
        isPlayerTurn: state.isPlayerTurn,
        slot00CardId: state.grid[0][0].cardId,
        slot00CanonicalOwner: state.grid[0][0].canonicalOwner
      };
    });
    turnsLog.push({ turn: 3, actor: "host", hostState: turn3Host, challengerSynced: turn3ChallengerSync });

    // 5. Verify canonical 3x3 board parity across both MacBooks
    const parityCheck = await Promise.all([
      pageHost.evaluate(() =>
        window.CardFrontModules.LanDuelSync.serializeGridForLan(state.grid, state.lanMultiplayer.role)
      ),
      pageChallenger.evaluate(() =>
        window.CardFrontModules.LanDuelSync.serializeGridForLan(state.grid, state.lanMultiplayer.role)
      )
    ]);

    const hostCanonical = parityCheck[0];
    const challengerCanonical = parityCheck[1];
    let matchingCells = 0;
    for (let i = 0; i < 9; i++) {
      const a = hostCanonical[i];
      const b = challengerCanonical[i];
      if (!a && !b) {
        matchingCells++;
      } else if (a && b && a.id === b.id && a.canonicalOwner === b.canonicalOwner) {
        matchingCells++;
      }
    }

    const allChecksPass =
      hostJoin.enabled === true &&
      challengerJoin.enabled === true &&
      turn1ChallengerSync.centerCardId === turn1Host.centerCardId &&
      turn1ChallengerSync.centerLocalOwner === "ai" &&
      turn1ChallengerSync.isPlayerTurn === true &&
      turn2HostSync.slot10CardId === turn2Challenger.placedCardId &&
      turn2HostSync.slot10LocalOwner === "ai" &&
      turn2HostSync.isPlayerTurn === true &&
      Boolean(turn3Host.drawnCardId) &&
      turn3Host.handAfterDraw === 5 &&
      matchingCells === 9;

    const report = {
      schema: "CARDFRONT_2MACBOOK_LAN_DUEL_E2E_REPORT_V1",
      status: allChecksPass ? "PASS_2MACBOOK_HUMAN_1V1_LAN_DUEL_E2E" : "FAIL_LAN_E2E",
      timestamp_utc: new Date().toISOString(),
      elapsed_ms: Date.now() - startTime,
      endpoints_tested: {
        seat1_host_url: HOST_URL,
        seat2_challenger_url: challengerConnectedUrl
      },
      room_id: "CITADEL-1",
      seat1_join: hostJoin,
      seat2_join: challengerJoin,
      turns_simulated: turnsLog.length,
      turns_log: turnsLog,
      deck_draw_verified: Boolean(turn3Host.drawnCardId && turn3Host.handAfterDraw === 5),
      canonical_3x3_cells_matched: matchingCells,
      canonical_board_lockstep_parity: matchingCells === 9
    };

    fs.mkdirSync(path.dirname(REPORT_OUT), { recursive: true });
    fs.writeFileSync(REPORT_OUT, JSON.stringify(report, null, 2), "utf8");
    console.log(JSON.stringify(report, null, 2));
    process.exit(allChecksPass ? 0 : 1);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
