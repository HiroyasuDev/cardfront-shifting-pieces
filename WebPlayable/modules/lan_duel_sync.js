/**
 * CARDFRONT 3D: Cradle of Echoes — Modular 2-MacBook Human-vs-Human LAN Duel Sync
 * Synchronizes Seat 1 (`host` / Blue) and Seat 2 (`challenger` / Red) over `/api/lan/room`
 * on 0.0.0.0:8096 with full 3x3 board authority, column dice sync, and turn handoff.
 */
(function (root) {
  "use strict";

  function serializeGridForLan(grid, actorRole = "host") {
    if (!Array.isArray(grid)) return new Array(9).fill(null);
    const flat = [];
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const cell = grid[r] && grid[r][c];
        if (!cell || !cell.cardId) {
          flat.push(null);
        } else {
          // Canonical owner encoding: "host" (Blue / Seat 1) vs "challenger" (Red / Seat 2)
          let canonicalOwner = cell.canonicalOwner;
          if (!canonicalOwner) {
            if (actorRole === "challenger") {
              canonicalOwner = cell.owner === "player" ? "challenger" : "host";
            } else {
              canonicalOwner = cell.owner === "player" ? "host" : "challenger";
            }
          }
          flat.push({
            id: cell.cardId,
            canonicalOwner,
            owner: cell.owner,
            nesw: Array.isArray(cell.nesw) ? cell.nesw.slice() : [6, 6, 6, 6],
            judgeShield: Boolean(cell.judgeShield)
          });
        }
      }
    }
    return flat;
  }

  function applyLanBoardToLocalGrid(room, stateObj) {
    if (!room || !Array.isArray(room.board) || room.board.length !== 9 || !stateObj || !Array.isArray(stateObj.grid)) {
      return { updatedCells: 0, flippedCells: 0 };
    }
    const myRole = (stateObj.lanMultiplayer && stateObj.lanMultiplayer.role) || "host";
    let updatedCells = 0;
    let flippedCells = 0;

    for (let idx = 0; idx < 9; idx++) {
      const r = Math.floor(idx / 3);
      const c = idx % 3;
      const remoteCell = room.board[idx];
      const localCell = stateObj.grid[r] && stateObj.grid[r][c];
      if (!localCell) continue;

      if (!remoteCell || !remoteCell.id) {
        if (localCell.cardId) {
          localCell.cardId = null;
          localCell.owner = null;
          localCell.canonicalOwner = null;
          localCell.nesw = [0, 0, 0, 0];
          updatedCells++;
        }
        continue;
      }

      const remoteCanon = remoteCell.canonicalOwner || (remoteCell.owner === "player" ? "host" : "challenger");
      // From each seat's perspective, their own cards are "player" (Blue) and opponent's are "ai" (Red)
      const localOwner = remoteCanon === myRole ? "player" : "ai";
      const wasOccupied = Boolean(localCell.cardId);
      const prevOwner = localCell.owner;

      if (localCell.cardId !== remoteCell.id || prevOwner !== localOwner) {
        localCell.cardId = remoteCell.id;
        localCell.owner = localOwner;
        localCell.canonicalOwner = remoteCanon;
        localCell.nesw = Array.isArray(remoteCell.nesw) ? remoteCell.nesw.slice() : [6, 6, 6, 6];
        localCell.judgeShield = Boolean(remoteCell.judgeShield);
        if (!wasOccupied) {
          localCell.justPlaced = true;
          updatedCells++;
        } else if (prevOwner && prevOwner !== localOwner) {
          localCell.justFlipped = true;
          flippedCells++;
        }
      } else if (Array.isArray(remoteCell.nesw)) {
        localCell.nesw = remoteCell.nesw.slice();
      }
    }

    if (Array.isArray(room.colDice) && room.colDice.length === 3) {
      stateObj.colDice = room.colDice.slice();
    }
    if (stateObj.lanMultiplayer && stateObj.lanMultiplayer.human1v1 && room.turnSeat) {
      stateObj.isPlayerTurn = room.turnSeat === myRole;
    }

    return { updatedCells, flippedCells };
  }

  const LanDuelSyncModule = {
    serializeGridForLan,
    applyLanBoardToLocalGrid
  };

  root.CardFrontModules = root.CardFrontModules || {};
  root.CardFrontModules.LanDuelSync = LanDuelSyncModule;
})(typeof window !== "undefined" ? window : globalThis);
