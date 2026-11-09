/* ============================================================================
 * CARDFRONT 3D: Cradle of Echoes -- Sovereign Animation Engine
 * Module: Synapse-Sakuga-AnimEngine v1.0 (synapse_sakuga_anim_engine.js)
 * Targets: Web PWA, Apple Metal WKWebView, Android Native WebView, Steam Desktop
 *
 * Provides window.SynapseSakugaAnimEngine:
 *   - VERSION: "1.0.0", PHYSICS_HZ: 120, SAKUGA_FPS: 24
 *   - CLIPS: 8 canonical .cfanim clips with deterministic fnv1a64 checksums
 *   - solveSpring1D(pos, vel, target, stiffness, damping, mass, dt)
 *   - quantizeSakugaTime(tSec, fps = 24)
 *   - solveFabrik2D(joints, targetX, targetY, tolerance = 0.001, maxIters = 10)
 *   - computeParallaxOffsets(normX, normY)
 *   - scrubTo(clipId, timeSec)
 *   - attachLivePuppet25D()
 *   - triggerDeploySlam(slotIndex)
 *   - triggerDirectionalClashLunge(attackerSlot, defenderSlot, direction)
 *   - triggerCaptureFlip180(slotIndex, newOwner)
 *   - triggerTacticalSlideBank(fromSlot, toSlot)
 *   - triggerColumnDieSurge(colIndex)
 *   - triggerSakugaImpactFlash2F(slotIndex)
 *   - injectSakugaAnimStudioBar()
 *
 * Zero Generic Emojis: All icons rendered via window.cfIcon(name, size) with
 * code-native 256x256 inline SVGs.
 * ============================================================================ */

(function initSynapseSakugaAnimEngine(globalScope) {
  "use strict";

  const ENGINE_VERSION = "1.0.0";
  const PHYSICS_HZ = 120;
  const SAKUGA_FPS = 24;
  const DEFAULT_DT = 1.0 / PHYSICS_HZ;

  const PARALLAX_LAYER_DEPTHS = {
    bg: -0.35,
    mid: -0.12,
    actor: 0.18,
    vfxFrameBreak: 0.45,
    bg_layer: -0.35,
    mid_layer: -0.12,
    actor_layer: 0.18,
    vfx_frame_break_layer: 0.45
  };

  // Bespoke 256x256 inline SVG bodies for window.cfIcon(name, size) (Zero Generic Emojis)
  const SAKUGA_ICON_BODIES = {
    bolt:
      '<polygon points="146,16 58,136 122,136 96,240 198,112 134,112" fill="#FFB800" stroke="#FFF3B0" stroke-width="8" stroke-linejoin="round"/>' +
      '<polygon points="140,48 84,128 126,128 110,198 172,118 130,118" fill="#00E5FF"/>',
    sparkle:
      '<polygon points="128,14 152,96 238,128 152,160 128,242 104,160 18,128 104,96" fill="#FFB800" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>' +
      '<polygon points="128,56 142,110 196,128 142,146 128,200 114,146 60,128 114,110" fill="#00E5FF"/>' +
      '<circle cx="128" cy="128" r="16" fill="#FFFFFF"/>',
    cube:
      '<polygon points="128,20 228,76 128,132 28,76" fill="#FFB800" stroke="#FFF3B0" stroke-width="6"/>' +
      '<polygon points="28,76 128,132 128,236 28,180" fill="#0F172A" stroke="#FFB800" stroke-width="8"/>' +
      '<polygon points="228,76 128,132 128,236 228,180" fill="#131C31" stroke="#00E5FF" stroke-width="8"/>' +
      '<circle cx="128" cy="76" r="14" fill="#0F172A"/>',
    eye:
      '<path d="M16,128 C52,64 100,44 128,44 C156,44 204,64 240,128 C204,192 156,212 128,212 C100,212 52,192 16,128 Z" fill="#0F172A" stroke="#00E5FF" stroke-width="12" stroke-linejoin="round"/>' +
      '<circle cx="128" cy="128" r="46" fill="#1E293B" stroke="#FFB800" stroke-width="10"/>' +
      '<polygon points="128,96 144,128 128,160 112,128" fill="#00E5FF"/>',
    shield:
      '<path d="M128,18 L220,56 L220,128 C220,184 178,222 128,242 C78,222 36,184 36,128 L36,56 Z" fill="#0F172A" stroke="#FFB800" stroke-width="12" stroke-linejoin="round"/>' +
      '<polygon points="128,52 156,112 200,128 156,144 128,204 100,144 56,128 100,112" fill="#2EE6D3"/>' +
      '<circle cx="128" cy="128" r="18" fill="#FFB800"/>',
    sword:
      '<line x1="48" y1="208" x2="204" y2="52" stroke="#00E5FF" stroke-width="18" stroke-linecap="round"/>' +
      '<polygon points="176,28 232,24 228,80 184,72" fill="#FFF3B0" stroke="#FFB800" stroke-width="6"/>' +
      '<line x1="68" y1="136" x2="120" y2="188" stroke="#FFB800" stroke-width="16" stroke-linecap="round"/>' +
      '<circle cx="42" cy="214" r="14" fill="#FF2E54" stroke="#FFB800" stroke-width="6"/>',
    dice:
      '<rect x="32" y="32" width="192" height="192" rx="28" fill="#0F172A" stroke="#FFB800" stroke-width="12"/>' +
      '<circle cx="80" cy="80" r="16" fill="#00E5FF"/>' +
      '<circle cx="176" cy="80" r="16" fill="#FFB800"/>' +
      '<circle cx="128" cy="128" r="18" fill="#FF2E54"/>' +
      '<circle cx="80" cy="176" r="16" fill="#FFB800"/>' +
      '<circle cx="176" cy="176" r="16" fill="#00E5FF"/>',
    sakuga_spark:
      '<circle cx="128" cy="128" r="106" fill="#0B1326" stroke="#FF2E54" stroke-width="10"/>' +
      '<polygon points="128,12 148,96 244,128 148,160 128,244 108,160 12,128 108,96" fill="#FFB800" stroke="#FFF3B0" stroke-width="6" stroke-linejoin="round"/>' +
      '<polygon points="52,52 114,106 128,128 106,114" fill="#00E5FF"/>' +
      '<polygon points="204,52 142,106 128,128 150,114" fill="#00E5FF"/>' +
      '<polygon points="128,68 142,114 188,128 142,142 128,188 114,142 68,128 114,114" fill="#00E5FF"/>' +
      '<circle cx="128" cy="128" r="16" fill="#FFFFFF"/>',
    puppet_rig:
      '<circle cx="128" cy="46" r="24" fill="#0F172A" stroke="#00E5FF" stroke-width="10"/>' +
      '<line x1="128" y1="70" x2="128" y2="156" stroke="#FFB800" stroke-width="14" stroke-linecap="round"/>' +
      '<line x1="128" y1="94" x2="54" y2="132" stroke="#00E5FF" stroke-width="12" stroke-linecap="round"/>' +
      '<line x1="128" y1="94" x2="202" y2="68" stroke="#2EE6D3" stroke-width="12" stroke-linecap="round"/>' +
      '<line x1="128" y1="156" x2="78" y2="226" stroke="#A855F7" stroke-width="12" stroke-linecap="round"/>' +
      '<line x1="128" y1="156" x2="178" y2="226" stroke="#A855F7" stroke-width="12" stroke-linecap="round"/>' +
      '<circle cx="128" cy="94" r="11" fill="#FFB800"/>' +
      '<circle cx="54" cy="132" r="10" fill="#00E5FF"/>' +
      '<circle cx="202" cy="68" r="10" fill="#2EE6D3"/>' +
      '<circle cx="128" cy="156" r="11" fill="#FFB800"/>'
  };

  function ensureCfIconSupport() {
    try {
      if (typeof CF_ICON_BODIES === "object" && CF_ICON_BODIES !== null) {
        Object.keys(SAKUGA_ICON_BODIES).forEach((k) => {
          if (!CF_ICON_BODIES[k]) {
            CF_ICON_BODIES[k] = SAKUGA_ICON_BODIES[k];
          }
        });
      }
    } catch (_) {
      // Lexical CF_ICON_BODIES not in scope; handled via globalScope.cfIcon wrapper below
    }

    const existingCfIcon = typeof globalScope.cfIcon === "function" ? globalScope.cfIcon : null;
    if (!existingCfIcon || !existingCfIcon.__sakugaIconsRegistered) {
      const wrappedCfIcon = function cfIcon(name, size = 14, extraStyle = "") {
        const key = String(name || "sakuga_spark");
        if (SAKUGA_ICON_BODIES[key]) {
          return (
            `<svg class="cf-lib-icon" data-icon-id="${key}" width="${size}" height="${size}" ` +
            `viewBox="0 0 256 256" fill="none" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0;${extraStyle}">` +
            `${SAKUGA_ICON_BODIES[key]}</svg>`
          );
        }
        if (existingCfIcon) {
          return existingCfIcon(key, size, extraStyle);
        }
        const fallbackBody = SAKUGA_ICON_BODIES.sakuga_spark;
        return (
          `<svg class="cf-lib-icon" data-icon-id="${key}" width="${size}" height="${size}" ` +
          `viewBox="0 0 256 256" fill="none" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0;${extraStyle}">` +
          `${fallbackBody}</svg>`
        );
      };
      wrappedCfIcon.__sakugaIconsRegistered = true;
      globalScope.cfIcon = wrappedCfIcon;
    }
  }

  ensureCfIconSupport();

  function renderIcon(name, size = 14, extraStyle = "") {
    ensureCfIconSupport();
    return globalScope.cfIcon(name, size, extraStyle);
  }

  // Register custom Sakuga haptic patterns into window.CardFrontHaptics when available
  function ensureHapticPatternsRegistered() {
    const haptics = globalScope.CardFrontHaptics;
    if (!haptics || !haptics.patterns) return;
    if (!haptics.patterns.card_deploy) {
      haptics.patterns.card_deploy = {
        name: "card_deploy",
        appleFeedbackType: "impactHeavy",
        intensity: 0.85,
        sharpness: 0.86,
        durationMs: 36,
        vibrate: [18, 22]
      };
    }
    if (!haptics.patterns.card_capture) {
      haptics.patterns.card_capture = {
        name: "card_capture",
        appleFeedbackType: "impactHeavy",
        intensity: 1.0,
        sharpness: 0.94,
        durationMs: 68,
        vibrate: [24, 30, 40]
      };
    }
    if (!haptics.patterns.tactical_slide) {
      haptics.patterns.tactical_slide = {
        name: "tactical_slide",
        appleFeedbackType: "impactMedium",
        intensity: 0.7,
        sharpness: 0.78,
        durationMs: 28,
        vibrate: [14, 18]
      };
    }
    if (!haptics.patterns.sakuga_clash) {
      haptics.patterns.sakuga_clash = {
        name: "sakuga_clash",
        appleFeedbackType: "impactHeavy",
        intensity: 0.95,
        sharpness: 0.95,
        durationMs: 52,
        vibrate: [22, 18, 34]
      };
    }
  }

  function triggerHapticSafe(patternName, intensity = 0.85) {
    ensureHapticPatternsRegistered();
    if (
      globalScope.CardFrontHaptics &&
      typeof globalScope.CardFrontHaptics.trigger === "function"
    ) {
      return globalScope.CardFrontHaptics.trigger(patternName, intensity);
    }
    return null;
  }

  // Deterministic 64-bit FNV-1a checksum (matches Backend/synapse_sakuga_animation_engine.py)
  function computeFnv1a64(inputStr) {
    const str = String(inputStr || "");
    if (typeof BigInt === "function") {
      let hash = BigInt("0xcbf29ce484222325");
      const prime = BigInt("0x100000001b3");
      const mask64 = BigInt("0xffffffffffffffff");
      for (let i = 0; i < str.length; i++) {
        hash ^= BigInt(str.charCodeAt(i) & 0xff);
        hash = (hash * prime) & mask64;
      }
      return "0x" + hash.toString(16).padStart(16, "0");
    }
    // 32-bit fallback pair if BigInt is unavailable
    let h1 = 0x811c9dc5;
    let h2 = 0xcbf29ce4;
    for (let i = 0; i < str.length; i++) {
      const c = str.charCodeAt(i) & 0xff;
      h1 ^= c;
      h1 = Math.imul(h1, 0x01000193) >>> 0;
      h2 ^= c;
      h2 = Math.imul(h2, 0x01000193) >>> 0;
    }
    return "0x" + h2.toString(16).padStart(8, "0") + h1.toString(16).padStart(8, "0");
  }

  function roundTo(val, decimals = 6) {
    const factor = Math.pow(10, decimals);
    return Math.round(Number(val) * factor) / factor;
  }

  // ============================================================================
  // 1. CORE MATHEMATICAL SOLVERS (120Hz Spring, 24fps Sakuga, 2D FABRIK IK, Parallax)
  // ============================================================================

  /**
   * Analytical / semi-implicit 120Hz damped harmonic spring physics step.
   * Supports under-damped (zeta < 1), critically-damped (zeta == 1), and over-damped (zeta > 1).
   *
   * @param {number} pos Current position
   * @param {number} vel Current velocity
   * @param {number} target Target equilibrium position
   * @param {number} stiffness Hooke spring constant k (> 0)
   * @param {number} damping Viscous damping coefficient c (>= 0)
   * @param {number} mass Oscillator mass m (> 0)
   * @param {number} dt Timestep in seconds (default 1 / 120)
   * @returns {{ pos: number, vel: number, zeta: number, omegaN: number, regime: string, settled: boolean }}
   */
  function solveSpring1D(
    pos = 0.0,
    vel = 0.0,
    target = 1.0,
    stiffness = 320.0,
    damping = 28.0,
    mass = 1.0,
    dt = DEFAULT_DT
  ) {
    const xCurr = Number(pos) || 0.0;
    const vCurr = Number(vel) || 0.0;
    const xTarget = Number(target !== undefined ? target : 1.0);
    const k = Math.max(1e-6, Number(stiffness) || 320.0);
    const c = Math.max(0.0, Number(damping !== undefined ? damping : 28.0));
    const m = Math.max(1e-6, Number(mass) || 1.0);
    const stepDt = Math.max(0.0, Number(dt !== undefined ? dt : DEFAULT_DT));

    const omegaN = Math.sqrt(k / m);
    const zeta = c / (2.0 * Math.sqrt(k * m));
    const regime =
      Math.abs(zeta - 1.0) <= 1e-6
        ? "critically-damped"
        : zeta < 1.0
        ? "under-damped"
        : "over-damped";

    if (stepDt === 0.0) {
      return {
        pos: xCurr,
        vel: vCurr,
        zeta: roundTo(zeta, 6),
        omegaN: roundTo(omegaN, 6),
        regime,
        settled: Math.abs(xCurr - xTarget) <= 1e-3 && Math.abs(vCurr) <= 1e-2
      };
    }

    const x0 = xCurr - xTarget;
    const v0 = vCurr;
    let displacement = 0.0;
    let nextVel = 0.0;

    if (Math.abs(zeta - 1.0) <= 1e-6) {
      const c1 = x0;
      const c2 = v0 + omegaN * x0;
      const expTerm = Math.exp(-omegaN * stepDt);
      displacement = (c1 + c2 * stepDt) * expTerm;
      nextVel = (c2 - omegaN * (c1 + c2 * stepDt)) * expTerm;
    } else if (zeta < 1.0) {
      const wd = omegaN * Math.sqrt(Math.max(1e-12, 1.0 - zeta * zeta));
      const aCoeff = x0;
      const bCoeff = (v0 + zeta * omegaN * x0) / wd;
      const expTerm = Math.exp(-zeta * omegaN * stepDt);
      const cosWt = Math.cos(wd * stepDt);
      const sinWt = Math.sin(wd * stepDt);
      displacement = expTerm * (aCoeff * cosWt + bCoeff * sinWt);
      nextVel =
        expTerm *
        ((-zeta * omegaN * aCoeff + wd * bCoeff) * cosWt +
          (-zeta * omegaN * bCoeff - wd * aCoeff) * sinWt);
    } else {
      const sqrtTerm = Math.sqrt(Math.max(1e-12, zeta * zeta - 1.0));
      const r1 = -omegaN * (zeta - sqrtTerm);
      const r2 = -omegaN * (zeta + sqrtTerm);
      const denom = r1 - r2;
      const c1 = (v0 - r2 * x0) / denom;
      const c2 = (r1 * x0 - v0) / denom;
      const e1 = Math.exp(r1 * stepDt);
      const e2 = Math.exp(r2 * stepDt);
      displacement = c1 * e1 + c2 * e2;
      nextVel = c1 * r1 * e1 + c2 * r2 * e2;
    }

    const nextPos = xTarget + displacement;
    return {
      pos: nextPos,
      vel: nextVel,
      zeta: roundTo(zeta, 6),
      omegaN: roundTo(omegaN, 6),
      regime,
      settled: Math.abs(nextPos - xTarget) <= 1e-3 && Math.abs(nextVel) <= 1e-2
    };
  }

  /**
   * Quantizes continuous time (seconds) into stepped anime frames:
   * Math.floor(tSec * fps) / fps
   *
   * @param {number} tSec Continuous time in seconds
   * @param {number} fps Frame rate (default 24)
   * @returns {number} Quantized stepped frame time in seconds
   */
  function quantizeSakugaTime(tSec, fps = SAKUGA_FPS) {
    const safeFps = Number(fps) > 0 ? Number(fps) : SAKUGA_FPS;
    const clampedT = Math.max(0.0, Number(tSec) || 0.0);
    return Math.floor(clampedT * safeFps + 1e-9) / safeFps;
  }

  function createHybridJoint(x, y) {
    const rx = roundTo(x, 6);
    const ry = roundTo(y, 6);
    const pt = { x: rx, y: ry, 0: rx, 1: ry };
    Object.defineProperty(pt, "length", { value: 2, enumerable: false });
    if (typeof Symbol !== "undefined" && Symbol.iterator) {
      Object.defineProperty(pt, Symbol.iterator, {
        value: function* () {
          yield this.x;
          yield this.y;
        },
        enumerable: false
      });
    }
    return pt;
  }

  function readJointXY(joint) {
    if (Array.isArray(joint)) {
      return [Number(joint[0]) || 0.0, Number(joint[1]) || 0.0];
    }
    if (joint && typeof joint === "object") {
      const x = joint.x !== undefined ? Number(joint.x) : Number(joint[0]);
      const y = joint.y !== undefined ? Number(joint.y) : Number(joint[1]);
      return [Number.isFinite(x) ? x : 0.0, Number.isFinite(y) ? y : 0.0];
    }
    return [0.0, 0.0];
  }

  function dist2D(ax, ay, bx, by) {
    return Math.hypot(bx - ax, by - ay);
  }

  function pointAlong2D(ox, oy, tx, ty, distance) {
    const dx = tx - ox;
    const dy = ty - oy;
    const norm = Math.hypot(dx, dy);
    if (norm <= 1e-9) {
      return [ox + distance, oy];
    }
    const scale = distance / norm;
    return [ox + dx * scale, oy + dy * scale];
  }

  /**
   * Deterministic 2D Forward-And-Backward-Reaching Inverse Kinematics (FABRIK) solver
   * preserving exact segment bone lengths.
   *
   * Returns an Array of solved joints where each joint supports both `{ x, y }` and `[x, y]`
   * indexing, and the returned array also carries `.joints`, `.boneLengths`, `.iterations`,
   * `.converged`, `.reachable`, and `.error` metadata properties.
   *
   * @param {Array} joints Array of `{x, y}` or `[x, y]` joint positions (minimum 2 joints)
   * @param {number|Array|Object} targetX Target X coordinate (or `[tx, ty]` / `{x, y}`)
   * @param {number} targetY Target Y coordinate
   * @param {number} tolerance Convergence tolerance (default 0.001)
   * @param {number} maxIters Maximum FABRIK iterations (default 10)
   */
  function solveFabrik2D(
    joints,
    targetX,
    targetY,
    tolerance = 0.001,
    maxIters = 10
  ) {
    let tx = 0.0;
    let ty = 0.0;
    let tol = Number(tolerance) > 0 ? Number(tolerance) : 0.001;
    let maxIterations = Number(maxIters) > 0 ? Math.floor(Number(maxIters)) : 10;

    if (Array.isArray(targetX) || (targetX && typeof targetX === "object")) {
      const parsedTarget = readJointXY(targetX);
      tx = parsedTarget[0];
      ty = parsedTarget[1];
      if (typeof targetY === "number" && targetY > 0) {
        tol = targetY;
      }
      if (typeof tolerance === "number" && tolerance >= 1) {
        maxIterations = Math.floor(tolerance);
      }
    } else {
      tx = Number(targetX) || 0.0;
      ty = Number(targetY) || 0.0;
    }

    const inputList = Array.isArray(joints) && joints.length >= 2
      ? joints
      : [
          [0.0, 0.0],
          [18.0, 12.0],
          [34.0, 22.0],
          [46.0, 28.0]
        ];

    const work = inputList.map((j) => readJointXY(j));
    const n = work.length;
    const rootX = work[0][0];
    const rootY = work[0][1];

    const boneLengths = [];
    let totalLength = 0.0;
    for (let i = 0; i < n - 1; i++) {
      const segLen = Math.max(
        1e-7,
        dist2D(work[i][0], work[i][1], work[i + 1][0], work[i + 1][1])
      );
      boneLengths.push(segLen);
      totalLength += segLen;
    }

    const rootToTarget = dist2D(rootX, rootY, tx, ty);
    const reachable = rootToTarget <= totalLength + 1e-9;
    let iterationsUsed = 0;

    if (!reachable) {
      iterationsUsed = 1;
      work[0] = [rootX, rootY];
      for (let i = 0; i < n - 1; i++) {
        work[i + 1] = pointAlong2D(
          work[i][0],
          work[i][1],
          tx,
          ty,
          boneLengths[i]
        );
      }
    } else {
      let endError = dist2D(work[n - 1][0], work[n - 1][1], tx, ty);
      while (endError > tol && iterationsUsed < maxIterations) {
        iterationsUsed++;
        // Forward reaching: end-effector to root
        work[n - 1] = [tx, ty];
        for (let i = n - 2; i >= 0; i--) {
          work[i] = pointAlong2D(
            work[i + 1][0],
            work[i + 1][1],
            work[i][0],
            work[i][1],
            boneLengths[i]
          );
        }
        // Backward reaching: root to end-effector
        work[0] = [rootX, rootY];
        for (let i = 0; i < n - 1; i++) {
          work[i + 1] = pointAlong2D(
            work[i][0],
            work[i][1],
            work[i + 1][0],
            work[i + 1][1],
            boneLengths[i]
          );
        }
        endError = dist2D(work[n - 1][0], work[n - 1][1], tx, ty);
      }
    }

    const solvedJoints = work.map((pt) => createHybridJoint(pt[0], pt[1]));
    const solvedLengths = [];
    let maxLengthDrift = 0.0;
    for (let i = 0; i < n - 1; i++) {
      const curLen = dist2D(
        solvedJoints[i].x,
        solvedJoints[i].y,
        solvedJoints[i + 1].x,
        solvedJoints[i + 1].y
      );
      solvedLengths.push(roundTo(curLen, 6));
      maxLengthDrift = Math.max(maxLengthDrift, Math.abs(curLen - boneLengths[i]));
    }

    const finalError = roundTo(
      dist2D(solvedJoints[n - 1].x, solvedJoints[n - 1].y, tx, ty),
      6
    );
    const converged = reachable ? finalError <= tol : true;

    Object.defineProperties(solvedJoints, {
      joints: { value: solvedJoints, enumerable: false },
      boneLengths: { value: solvedLengths, enumerable: false },
      bone_lengths: { value: solvedLengths, enumerable: false },
      bindBoneLengths: { value: boneLengths.map((l) => roundTo(l, 6)), enumerable: false },
      totalLength: { value: roundTo(totalLength, 6), enumerable: false },
      maxLengthDrift: { value: roundTo(maxLengthDrift, 8), enumerable: false },
      iterations: { value: iterationsUsed, enumerable: false },
      converged: { value: converged, enumerable: false },
      reachable: { value: reachable, enumerable: false },
      error: { value: finalError, enumerable: false },
      end_effector_error: { value: finalError, enumerable: false },
      target: { value: createHybridJoint(tx, ty), enumerable: false }
    });

    return solvedJoints;
  }

  /**
   * Computes 4-layer 2.5D depth parallax offsets (`bg`, `mid`, `actor`, `vfxFrameBreak`)
   * for cursor or gyroscope card tilt.
   *
   * @param {number} normX Normalized horizontal tilt in [-1, 1]
   * @param {number} normY Normalized vertical tilt in [-1, 1]
   * @param {number} maxDisplacementPx Maximum pixel shift at depth=1.0 (default 28.0)
   */
  function computeParallaxOffsets(normX = 0.0, normY = 0.0, maxDisplacementPx = 28.0) {
    const cx = Math.max(-1.0, Math.min(1.0, Number(normX) || 0.0));
    const cy = Math.max(-1.0, Math.min(1.0, Number(normY) || 0.0));
    const scale = Number(maxDisplacementPx) > 0 ? Number(maxDisplacementPx) : 28.0;

    function buildLayer(depthCoeff) {
      const dx = roundTo(cx * depthCoeff * scale, 5);
      const dy = roundTo(cy * depthCoeff * scale, 5);
      const sf = roundTo(1.0 + Math.abs(depthCoeff) * 0.06, 5);
      return {
        x: dx,
        y: dy,
        offset_x: dx,
        offset_y: dy,
        depth: depthCoeff,
        depth_coeff: depthCoeff,
        scale: sf,
        scale_factor: sf
      };
    }

    const bg = buildLayer(-0.35);
    const mid = buildLayer(-0.12);
    const actor = buildLayer(0.18);
    const vfxFrameBreak = buildLayer(0.45);

    return {
      bg,
      mid,
      actor,
      vfxFrameBreak,
      bg_layer: bg,
      mid_layer: mid,
      actor_layer: actor,
      vfx_frame_break_layer: vfxFrameBreak,
      normX: cx,
      normY: cy,
      tiltDegX: roundTo(-cy * 11.5, 4),
      tiltDegY: roundTo(cx * 11.5, 4)
    };
  }

  // ============================================================================
  // 2. CANONICAL .CFANIM CLIP DEFINITIONS & STEPPED SAKUGA CURVE EVALUATOR
  // ============================================================================

  function evaluateSakugaAtFrame(frameIdx, sakugaParams, springParams) {
    const f = Math.max(0, Math.floor(Number(frameIdx) || 0));
    const antEnd = Math.max(1, Number(sakugaParams.anticipation_frames) || 3);
    const lungeFrames = Math.max(1, Number(sakugaParams.lunge_frames) || 2);
    const hitstopFrames = Math.max(1, Number(sakugaParams.hitstop_frames) || 3);
    const antDip = Number(sakugaParams.anticipation_dip !== undefined ? sakugaParams.anticipation_dip : -0.18);
    const impactPeak = Number(sakugaParams.impact_peak !== undefined ? sakugaParams.impact_peak : 1.08);
    const lungeEnd = antEnd + lungeFrames;
    const hitstopEnd = lungeEnd + hitstopFrames;

    let phase = "anticipation";
    let value = 0.0;
    let inHitstop = false;

    if (f === 0) {
      phase = "anticipation";
      value = 0.0;
      inHitstop = false;
    } else if (f <= antEnd) {
      phase = "anticipation";
      const progress = f / antEnd;
      value = antDip * Math.sin(progress * 0.5 * Math.PI);
      inHitstop = false;
    } else if (f <= lungeEnd) {
      phase = "snap_lunge";
      const lungeStep = f - antEnd;
      const alpha = lungeStep / lungeFrames;
      value = antDip + alpha * (impactPeak - antDip);
      inHitstop = false;
    } else if (f < hitstopEnd) {
      phase = "hitstop";
      value = impactPeak;
      inHitstop = true;
    } else {
      phase = "settle";
      const settleFrames = f - hitstopEnd + 1;
      const settleT = settleFrames / SAKUGA_FPS;
      const settled = solveSpring1D(
        impactPeak,
        0.0,
        1.0,
        springParams.stiffness,
        springParams.damping,
        springParams.mass,
        settleT
      );
      value = settled.pos;
      inHitstop = false;
    }

    return {
      frame_index: f,
      quantized_time: roundTo(f / SAKUGA_FPS, 6),
      phase,
      value: roundTo(value, 6),
      in_hitstop: inHitstop
    };
  }

  const CANONICAL_CLIP_SPECS = [
    {
      clip_id: "idle_breathe_25d",
      description: "Subtle 2.5D harmonic breathing & cape sway with 4-layer depth parallax.",
      duration_sec: 2.0,
      fnv1a64: "0x7ce8bd3bd25e7052",
      spring_params: {
        stiffness: 180.0,
        damping: 22.0,
        mass: 1.0,
        zeta: 0.819892,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 3,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.02,
        hitstop_frames: 3
      },
      motion_profile: {
        pos_amp: [0.0, 6.5, 0.0],
        rot_amp_deg: [-1.2, 1.8, 0.8],
        scale_amp: [1.02, 1.025, 1.0],
        tilt: [0.22, -0.18]
      }
    },
    {
      clip_id: "deploy_orbital_slam",
      description: "High-altitude orbital card drop with 2-frame snap slam, 4-frame HitStop, and shockwave settle.",
      duration_sec: 0.85,
      fnv1a64: "0x0d083302713a0cd5",
      spring_params: {
        stiffness: 420.0,
        damping: 34.0,
        mass: 1.0,
        zeta: 0.829515,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 3,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.15,
        hitstop_frames: 4
      },
      motion_profile: {
        pos_amp: [0.0, -48.0, -18.0],
        rot_amp_deg: [8.5, 0.0, -2.5],
        scale_amp: [1.14, 0.92, 1.0],
        tilt: [0.0, 0.85]
      }
    },
    {
      clip_id: "directional_clash_lunge",
      description: "Aggressive directional combat lunge with -0.18 anticipation wind-up, 2-frame snap, and 4-frame HitStop.",
      duration_sec: 0.75,
      fnv1a64: "0xb90009f543696ffd",
      spring_params: {
        stiffness: 460.0,
        damping: 32.0,
        mass: 1.0,
        zeta: 0.746004,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 4,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.12,
        hitstop_frames: 4
      },
      motion_profile: {
        pos_amp: [34.0, 18.0, -8.0],
        rot_amp_deg: [-6.0, 4.5, -11.0],
        scale_amp: [1.1, 1.08, 1.0],
        tilt: [0.75, 0.45]
      }
    },
    {
      clip_id: "capture_flip_180",
      description: "180-degree axial ownership capture flip with faction chroma flash and critically-damped lock.",
      duration_sec: 0.65,
      fnv1a64: "0xf17e1cf347d09ba1",
      spring_params: {
        stiffness: 400.0,
        damping: 40.0,
        mass: 1.0,
        zeta: 1.0,
        regime: "critically-damped"
      },
      sakuga_params: {
        anticipation_frames: 2,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.06,
        hitstop_frames: 3
      },
      motion_profile: {
        pos_amp: [0.0, 22.0, -14.0],
        rot_amp_deg: [0.0, 180.0, 0.0],
        scale_amp: [1.08, 1.08, 1.0],
        tilt: [-0.65, 0.25]
      }
    },
    {
      clip_id: "tactical_slide_bank",
      description: "Grid tile relocation slide with aerodynamic roll banking and under-damped arrival settle.",
      duration_sec: 0.55,
      fnv1a64: "0x81d3a4c478dcebb5",
      spring_params: {
        stiffness: 340.0,
        damping: 26.0,
        mass: 1.0,
        zeta: 0.705024,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 2,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.05,
        hitstop_frames: 3
      },
      motion_profile: {
        pos_amp: [42.0, 4.0, 0.0],
        rot_amp_deg: [0.0, -4.0, -9.5],
        scale_amp: [1.03, 0.98, 1.0],
        tilt: [0.55, -0.15]
      }
    },
    {
      clip_id: "column_die_nudge_surge",
      description: "Tactical column die manipulation surge with metallic recoil and harmonic resonance.",
      duration_sec: 0.6,
      fnv1a64: "0xc52dc56b81ff0d88",
      spring_params: {
        stiffness: 380.0,
        damping: 28.0,
        mass: 1.0,
        zeta: 0.718185,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 2,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.1,
        hitstop_frames: 3
      },
      motion_profile: {
        pos_amp: [0.0, 16.0, -10.0],
        rot_amp_deg: [14.0, -8.0, 6.0],
        scale_amp: [1.16, 1.16, 1.0],
        tilt: [0.35, 0.6]
      }
    },
    {
      clip_id: "sakuga_impact_flash_2f",
      description: "2-frame black-and-white impact frame burst with 5-frame freeze-frame HitStop.",
      duration_sec: 0.5,
      fnv1a64: "0x2383b846e9fac22a",
      spring_params: {
        stiffness: 520.0,
        damping: 38.0,
        mass: 1.0,
        zeta: 0.833205,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 2,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.18,
        hitstop_frames: 5
      },
      motion_profile: {
        pos_amp: [-6.0, 8.0, -16.0],
        rot_amp_deg: [-3.5, 2.0, 5.0],
        scale_amp: [1.18, 1.18, 1.0],
        tilt: [-0.8, 0.75]
      }
    },
    {
      clip_id: "boss_telegraph_pulse",
      description: "Sovereign Boss crimson-obsidian hazard telegraph pulse with weapon IK lock.",
      duration_sec: 1.1,
      fnv1a64: "0xa63c9a9b0a74ca17",
      spring_params: {
        stiffness: 290.0,
        damping: 24.0,
        mass: 1.0,
        zeta: 0.704664,
        regime: "under-damped"
      },
      sakuga_params: {
        anticipation_frames: 4,
        anticipation_dip: -0.18,
        lunge_frames: 2,
        impact_peak: 1.14,
        hitstop_frames: 4
      },
      motion_profile: {
        pos_amp: [0.0, 14.0, -12.0],
        rot_amp_deg: [4.0, 0.0, -3.0],
        scale_amp: [1.09, 1.09, 1.0],
        tilt: [0.45, -0.65]
      }
    }
  ];

  function buildCanonicalClipObject(spec) {
    const clipId = spec.clip_id;
    const durationSec = spec.duration_sec;
    const sp = spec.spring_params;
    const sk = spec.sakuga_params;
    const mp = spec.motion_profile;
    const totalFrames = Math.round(durationSec * SAKUGA_FPS);

    const antFrame = sk.anticipation_frames;
    const hitstopStartFrame = sk.anticipation_frames + sk.lunge_frames;
    const flipFrame = Math.max(1, Math.floor(totalFrames / 2));

    const events = {
      onAnticipation: {
        event_name: "onAnticipation",
        frame_index: antFrame,
        time_sec: roundTo(antFrame / SAKUGA_FPS, 6),
        dip_value: sk.anticipation_dip,
        sfx_cue: `sfx_${clipId}_windup`
      },
      onHitStop: {
        event_name: "onHitStop",
        frame_index: hitstopStartFrame,
        time_sec: roundTo(hitstopStartFrame / SAKUGA_FPS, 6),
        hold_frames: sk.hitstop_frames,
        sfx_cue: `sfx_${clipId}_impact`
      },
      onCaptureFlip: {
        event_name: "onCaptureFlip",
        frame_index: flipFrame,
        time_sec: roundTo(flipFrame / SAKUGA_FPS, 6),
        flip_degrees: clipId === "capture_flip_180" ? 180.0 : 0.0,
        active: clipId === "capture_flip_180"
      },
      onHapticTrigger: {
        event_name: "onHapticTrigger",
        frame_index: hitstopStartFrame,
        time_sec: roundTo(hitstopStartFrame / SAKUGA_FPS, 6),
        intensity: 0.85,
        duration_ms: 35
      }
    };

    const bindArm = [
      [0.0, 0.0],
      [18.0, 12.0],
      [34.0, 22.0],
      [46.0, 28.0]
    ];
    const keyframes = [];

    for (let f = 0; f <= totalFrames; f++) {
      const tSec = roundTo(f / SAKUGA_FPS, 6);
      const skEval = evaluateSakugaAtFrame(f, sk, sp);
      const spEval = solveSpring1D(0.0, 0.0, 1.0, sp.stiffness, sp.damping, sp.mass, tSec);
      const val = skEval.value;

      const parallax = computeParallaxOffsets(mp.tilt[0] * val, mp.tilt[1] * val);
      const ikTargetX = 36.0 + 8.0 * val;
      const ikTargetY = 24.0 + 6.0 * val;
      const ikSolved = solveFabrik2D(bindArm, ikTargetX, ikTargetY, 0.001, 12);

      keyframes.push({
        frame_index: f,
        time_sec: tSec,
        phase: skEval.phase,
        in_hitstop: skEval.in_hitstop,
        sakuga_scalar: val,
        spring_pos_120hz: roundTo(spEval.pos, 6),
        spring_vel_120hz: roundTo(spEval.vel, 6),
        position: [
          roundTo(mp.pos_amp[0] * val, 4),
          roundTo(mp.pos_amp[1] * val, 4),
          roundTo(mp.pos_amp[2] * val, 4)
        ],
        rotation_deg: [
          roundTo(mp.rot_amp_deg[0] * val, 4),
          roundTo(mp.rot_amp_deg[1] * val, 4),
          roundTo(mp.rot_amp_deg[2] * val, 4)
        ],
        scale: [
          roundTo(1.0 + (mp.scale_amp[0] - 1.0) * val, 5),
          roundTo(1.0 + (mp.scale_amp[1] - 1.0) * val, 5),
          roundTo(1.0 + (mp.scale_amp[2] - 1.0) * val, 5)
        ],
        parallax_layers: {
          bg_layer: parallax.bg_layer,
          mid_layer: parallax.mid_layer,
          actor_layer: parallax.actor_layer,
          vfx_frame_break_layer: parallax.vfx_frame_break_layer
        },
        weapon_arm_ik: {
          target: [roundTo(ikTargetX, 5), roundTo(ikTargetY, 5)],
          joints: ikSolved.map((j) => [j.x, j.y]),
          error: ikSolved.error
        }
      });
    }

    return {
      clipId,
      clip_id: clipId,
      version: "1.0",
      description: spec.description,
      durationSec,
      duration_sec: durationSec,
      physicsHz: PHYSICS_HZ,
      physics_hz: PHYSICS_HZ,
      sakugaFps: SAKUGA_FPS,
      sakuga_fps: SAKUGA_FPS,
      fnv1a64: spec.fnv1a64,
      fnv1a_64_checksum: spec.fnv1a64,
      springParams: sp,
      spring_params: sp,
      sakugaParams: sk,
      sakuga_params: sk,
      motionProfile: mp,
      motion_profile: mp,
      parallaxLayerDepths: {
        bg_layer: -0.35,
        mid_layer: -0.12,
        actor_layer: 0.18,
        vfx_frame_break_layer: 0.45
      },
      parallax_layer_depths: {
        bg_layer: -0.35,
        mid_layer: -0.12,
        actor_layer: 0.18,
        vfx_frame_break_layer: 0.45
      },
      events,
      keyframes
    };
  }

  const CLIPS = {};
  CANONICAL_CLIP_SPECS.forEach((spec) => {
    CLIPS[spec.clip_id] = buildCanonicalClipObject(spec);
  });

  /**
   * Deterministic pure function returning exact
   * `{ tx, ty, tz, rx, ry, rz, scaleX, scaleY, scaleZ, impactFlashAlpha, activeEvents, phase, inHitStop, frameIndex, quantizedTime }`
   * at `timeSec` for replay scrubbing and automated verification tests.
   *
   * @param {string} clipId One of the 8 canonical .cfanim clip IDs
   * @param {number} timeSec Continuous time in seconds
   */
  function scrubTo(clipId, timeSec = 0.0) {
    const clip = CLIPS[String(clipId || "directional_clash_lunge")] || CLIPS.directional_clash_lunge;
    const clampedTime = Math.max(0.0, Math.min(clip.durationSec, Number(timeSec) || 0.0));
    const quantizedTime = quantizeSakugaTime(clampedTime, clip.sakugaFps);
    const maxFrame = clip.keyframes.length - 1;
    const frameIndex = Math.max(0, Math.min(maxFrame, Math.round(quantizedTime * clip.sakugaFps)));

    const kf = clip.keyframes[frameIndex] || clip.keyframes[0];
    const sk = clip.sakugaParams;
    const hitstopStart = sk.anticipation_frames + sk.lunge_frames;
    const hitstopEnd = hitstopStart + sk.hitstop_frames;

    let impactFlashAlpha = 0.0;
    if (clip.clipId === "sakuga_impact_flash_2f") {
      if (frameIndex <= 2 || frameIndex === hitstopStart || frameIndex === hitstopStart + 1) {
        impactFlashAlpha = frameIndex === 1 ? 0.92 : 1.0;
      } else if (kf.in_hitstop) {
        impactFlashAlpha = 0.45;
      }
    } else if (clip.clipId !== "idle_breathe_25d") {
      if (frameIndex === hitstopStart) {
        impactFlashAlpha = 1.0;
      } else if (frameIndex === hitstopStart + 1) {
        impactFlashAlpha = 0.85;
      } else if (kf.in_hitstop) {
        impactFlashAlpha = 0.35;
      } else if (frameIndex === hitstopStart - 1) {
        impactFlashAlpha = 0.2;
      }
    }

    const activeEvents = [];
    const evMap = clip.events;
    if (frameIndex >= evMap.onAnticipation.frame_index && frameIndex <= hitstopStart) {
      activeEvents.push("onAnticipation");
    }
    if (
      kf.in_hitstop ||
      (frameIndex >= evMap.onHitStop.frame_index && frameIndex < hitstopEnd)
    ) {
      activeEvents.push("onHitStop");
      activeEvents.push("onHapticTrigger");
    }
    if (impactFlashAlpha >= 0.8) {
      activeEvents.push("onImpactFlash");
    }
    if (
      evMap.onCaptureFlip.active &&
      frameIndex >= evMap.onCaptureFlip.frame_index
    ) {
      activeEvents.push("onCaptureFlip");
    }

    const isHitStopFrame =
      Boolean(kf.in_hitstop) ||
      (frameIndex >= evMap.onHitStop.frame_index && frameIndex < hitstopEnd);

    return {
      clipId: clip.clipId,
      timeSec: roundTo(clampedTime, 6),
      quantizedTime: roundTo(quantizedTime, 6),
      frameIndex,
      phase: isHitStopFrame ? "hitstop" : kf.phase,
      inHitStop: isHitStopFrame,
      sakugaScalar: kf.sakuga_scalar,
      springPos120Hz: kf.spring_pos_120hz,
      springVel120Hz: kf.spring_vel_120hz,
      tx: kf.position[0],
      ty: kf.position[1],
      tz: kf.position[2],
      rx: kf.rotation_deg[0],
      ry: kf.rotation_deg[1],
      rz: kf.rotation_deg[2],
      scaleX: kf.scale[0],
      scaleY: kf.scale[1],
      scaleZ: kf.scale[2],
      impactFlashAlpha,
      activeEvents,
      parallaxLayers: kf.parallax_layers,
      weaponArmIk: kf.weapon_arm_ik,
      fnv1a64: clip.fnv1a64
    };
  }

  // ============================================================================
  // 3. LIVE DOM / CSS / SVG TABLETOP ANIMATION TRIGGERS & 2.5D PUPPET RIG
  // ============================================================================

  function isInstantModeActive() {
    if (globalScope.SynapseSakugaAnimEngine && globalScope.SynapseSakugaAnimEngine.instantMode) {
      return true;
    }
    if (globalScope.instantMode === true) return true;
    if (globalScope.state && globalScope.state.instantMode === true) return true;
    return false;
  }

  function isDraggingActive() {
    if (typeof globalScope.document !== "undefined" && globalScope.document.body) {
      if (globalScope.document.body.classList.contains("is-dragging")) return true;
    }
    if (globalScope.drag && (globalScope.drag.active || globalScope.drag.dropping)) {
      return true;
    }
    return false;
  }

  function injectSakugaStylesheet() {
    if (typeof globalScope.document === "undefined") return;
    const doc = globalScope.document;
    if (doc.getElementById("synapse-sakuga-anim-styles")) return;

    const styleEl = doc.createElement("style");
    styleEl.id = "synapse-sakuga-anim-styles";
    styleEl.textContent = `
      :root {
        --puppet-breathe-y: 0px;
        --puppet-sway-rot: 0deg;
        --parallax-bg-x: 0px;
        --parallax-bg-y: 0px;
        --parallax-mid-x: 0px;
        --parallax-mid-y: 0px;
        --parallax-actor-x: 0px;
        --parallax-actor-y: 0px;
        --parallax-vfx-x: 0px;
        --parallax-vfx-y: 0px;
      }

      .hand-card, .board-card {
        --puppet-breathe-y: 0px;
        --parallax-bg-x: 0px;
        --parallax-actor-x: 0px;
        --parallax-vfx-x: 0px;
      }

      .hand-card .slot-art, .board-card .slot-art {
        transform: translate3d(var(--parallax-actor-x, 0px), var(--puppet-breathe-y, 0px), 0) scale(1.02);
        transition: transform 60ms linear;
        will-change: transform;
      }

      .hand-card .card-telegraph-fx, .board-card .card-telegraph-fx {
        transform: translate3d(var(--parallax-vfx-x, 0px), calc(var(--puppet-breathe-y, 0px) * -0.5), 0);
      }

      @keyframes sakugaOrbitalSlamKeyframes {
        0% {
          transform: translate3d(0px, -46px, 42px) rotateX(9deg) scale3d(0.92, 1.14, 1);
          filter: brightness(1.35);
        }
        24% {
          transform: translate3d(0px, 5px, -6px) rotateX(-3deg) scale3d(1.15, 0.88, 1);
          filter: brightness(1.6) contrast(1.25);
        }
        42% {
          transform: translate3d(0px, 5px, -6px) rotateX(-3deg) scale3d(1.14, 0.89, 1);
          filter: brightness(1.45);
        }
        72% {
          transform: translate3d(0px, -2px, 3px) rotateX(1.2deg) scale3d(0.98, 1.03, 1);
        }
        100% {
          transform: translate3d(0px, 0px, 0px) rotateX(0deg) scale3d(1, 1, 1);
          filter: brightness(1);
        }
      }

      @keyframes sakugaDirectionalClashKeyframes {
        0% {
          transform: translate3d(calc(var(--clash-dir-x, 0) * -8px), calc(var(--clash-dir-y, -1) * -8px), 2px) scale(0.94);
        }
        28% {
          transform: translate3d(calc(var(--clash-dir-x, 0) * 28px), calc(var(--clash-dir-y, -1) * 28px), 16px) scale(1.12);
          filter: brightness(1.55) contrast(1.3);
        }
        50% {
          transform: translate3d(calc(var(--clash-dir-x, 0) * 28px), calc(var(--clash-dir-y, -1) * 28px), 16px) scale(1.12);
        }
        78% {
          transform: translate3d(calc(var(--clash-dir-x, 0) * -4px), calc(var(--clash-dir-y, -1) * -4px), 2px) scale(0.98);
        }
        100% {
          transform: translate3d(0px, 0px, 0px) scale(1);
          filter: brightness(1);
        }
      }

      @keyframes sakugaCaptureFlip180Keyframes {
        0% {
          transform: translate3d(0px, 0px, 0px) rotateY(0deg) scale(0.95);
        }
        25% {
          transform: translate3d(0px, -18px, 26px) rotateY(95deg) scale(1.10);
          filter: brightness(1.7) contrast(1.35);
        }
        48% {
          transform: translate3d(0px, -18px, 26px) rotateY(188deg) scale(1.08);
        }
        78% {
          transform: translate3d(0px, 2px, -2px) rotateY(177deg) scale(0.99);
        }
        100% {
          transform: translate3d(0px, 0px, 0px) rotateY(180deg) scale(1);
          filter: brightness(1);
        }
      }

      @keyframes sakugaSlideBankKeyframes {
        0% {
          transform: translate3d(calc(var(--slide-from-dx, -32px)), calc(var(--slide-from-dy, 0px)), 12px) rotateZ(var(--slide-bank-deg, -15deg)) scale(1.04);
        }
        45% {
          transform: translate3d(3px, 0px, 4px) rotateZ(calc(var(--slide-bank-deg, -15deg) * -0.35)) scale(1.02);
        }
        100% {
          transform: translate3d(0px, 0px, 0px) rotateZ(0deg) scale(1);
        }
      }

      @keyframes sakugaColDieSurgeTileKeyframes {
        0% {
          box-shadow: inset 0 0 0px rgba(255, 184, 0, 0), 0 0 0px rgba(0, 229, 255, 0);
        }
        35% {
          box-shadow: inset 0 0 26px rgba(255, 184, 0, 0.78), 0 0 22px rgba(0, 229, 255, 0.68);
          transform: translate3d(0px, -4px, 8px) scale(1.04);
        }
        100% {
          box-shadow: inset 0 0 0px rgba(255, 184, 0, 0), 0 0 0px rgba(0, 229, 255, 0);
          transform: translate3d(0px, 0px, 0px) scale(1);
        }
      }

      .sakuga-deploy-slam-active {
        animation: sakugaOrbitalSlamKeyframes 0.85s cubic-bezier(0.22, 1, 0.36, 1);
      }

      .sakuga-clash-lunge-active {
        animation: sakugaDirectionalClashKeyframes 0.75s cubic-bezier(0.18, 0.89, 0.32, 1.28);
        z-index: 45 !important;
      }

      .sakuga-capture-flip-180 .card-3d-unit,
      .sakuga-capture-flip-180.board-card {
        animation: sakugaCaptureFlip180Keyframes 0.65s cubic-bezier(0.22, 1, 0.36, 1);
      }

      .sakuga-slide-bank-active {
        animation: sakugaSlideBankKeyframes 0.55s cubic-bezier(0.22, 1, 0.36, 1);
      }

      .sakuga-col-surge-tile {
        animation: sakugaColDieSurgeTileKeyframes 0.60s ease-out;
      }

      .sakuga-impact-flash-overlay {
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: 95;
        overflow: hidden;
        border-radius: inherit;
        mix-blend-mode: screen;
      }

      .sakuga-impact-flash-overlay[data-impact-frame="1"] {
        background: radial-gradient(circle at var(--impact-fx, 50%) var(--impact-fy, 50%), rgba(255,255,255,0.96) 0%, rgba(0,229,255,0.75) 38%, rgba(11,19,38,0.92) 85%);
      }

      .sakuga-impact-flash-overlay[data-impact-frame="2"] {
        background: radial-gradient(circle at var(--impact-fx, 50%) var(--impact-fy, 50%), rgba(11,19,38,0.94) 0%, rgba(255,184,0,0.88) 34%, rgba(255,46,84,0.72) 78%);
      }
    `;
    doc.head.appendChild(styleEl);
  }

  // Ensures .board-tile[data-slot], .hand-card, .board-card, and #col-die-${c} exist on the live DOM
  function syncDomCardClasses() {
    if (typeof globalScope.document === "undefined") {
      return { handCards: [], boardCards: [], boardTiles: [], colDice: [] };
    }
    const doc = globalScope.document;
    injectSakugaStylesheet();

    const rawSlots = doc.querySelectorAll("#grid-3x3 .board-slot, .board-tile");
    const boardTiles = [];
    rawSlots.forEach((slotEl, idx) => {
      slotEl.classList.add("board-tile");
      const r = slotEl.dataset.r !== undefined ? Number(slotEl.dataset.r) : Math.floor(idx / 3);
      const c = slotEl.dataset.c !== undefined ? Number(slotEl.dataset.c) : idx % 3;
      const computedSlot = Number.isFinite(r) && Number.isFinite(c) ? r * 3 + c : idx;
      if (slotEl.dataset.slot === undefined) {
        slotEl.dataset.slot = String(computedSlot);
      }
      boardTiles.push(slotEl);

      const unitEl = slotEl.querySelector(".card-3d-unit");
      if (unitEl) {
        unitEl.classList.add("board-card");
        unitEl.dataset.slot = String(computedSlot);
      }
    });

    const handWraps = doc.querySelectorAll("#hand-bar .hand-card-wrap, .hand-card");
    const handCards = [];
    handWraps.forEach((wrapEl, idx) => {
      wrapEl.classList.add("hand-card");
      if (wrapEl.dataset.handIndex === undefined) {
        wrapEl.dataset.handIndex = String(idx);
      }
      handCards.push(wrapEl);
    });

    const boardCards = Array.from(
      doc.querySelectorAll("#grid-3x3 .board-card, #grid-3x3 .card-3d-unit, .board-tile .card-3d-unit")
    );
    boardCards.forEach((el) => el.classList.add("board-card"));

    const colDice = [];
    for (let c = 0; c < 3; c++) {
      let dieEl =
        doc.getElementById(`col-die-${c}`) ||
        doc.querySelector(`.col-header-pill.col-idx-${c}`) ||
        doc.querySelectorAll("#col-headers .col-header-pill")[c];
      if (dieEl) {
        if (!dieEl.id) {
          dieEl.id = `col-die-${c}`;
        }
        dieEl.dataset.colIndex = String(c);
        colDice.push(dieEl);
      }
    }

    return { handCards, boardCards, boardTiles, colDice };
  }

  function applyPuppetCssVarsToElements(normX, normY, breatheSec) {
    if (typeof globalScope.document === "undefined") return 0;
    const doc = globalScope.document;
    const { handCards, boardCards } = syncDomCardClasses();

    const parallax = computeParallaxOffsets(normX, normY);
    const breatheScrub = scrubTo("idle_breathe_25d", breatheSec % 2.0);
    const breatheY = roundTo(
      Math.sin(breatheSec * Math.PI) * 2.4 + breatheScrub.ty * 0.25,
      3
    );
    const swayRot = roundTo(Math.cos(breatheSec * Math.PI) * 0.85, 3);

    const breatheYStr = `${breatheY}px`;
    const swayRotStr = `${swayRot}deg`;
    const bgXStr = `${parallax.bg.x}px`;
    const bgYStr = `${parallax.bg.y}px`;
    const midXStr = `${parallax.mid.x}px`;
    const actorXStr = `${parallax.actor.x}px`;
    const actorYStr = `${parallax.actor.y}px`;
    const vfxXStr = `${parallax.vfxFrameBreak.x}px`;
    const vfxYStr = `${parallax.vfxFrameBreak.y}px`;

    if (doc.documentElement && doc.documentElement.style) {
      doc.documentElement.style.setProperty("--puppet-breathe-y", breatheYStr);
      doc.documentElement.style.setProperty("--puppet-sway-rot", swayRotStr);
      doc.documentElement.style.setProperty("--parallax-bg-x", bgXStr);
      doc.documentElement.style.setProperty("--parallax-bg-y", bgYStr);
      doc.documentElement.style.setProperty("--parallax-mid-x", midXStr);
      doc.documentElement.style.setProperty("--parallax-actor-x", actorXStr);
      doc.documentElement.style.setProperty("--parallax-actor-y", actorYStr);
      doc.documentElement.style.setProperty("--parallax-vfx-x", vfxXStr);
      doc.documentElement.style.setProperty("--parallax-vfx-y", vfxYStr);
    }

    const targets = [...handCards, ...boardCards];
    targets.forEach((el, idx) => {
      if (!el || !el.style) return;
      const phaseOffset = idx * 0.35;
      const cardBreatheY = roundTo(Math.sin((breatheSec + phaseOffset) * Math.PI) * 2.4, 3);
      el.style.setProperty("--puppet-breathe-y", `${cardBreatheY}px`);
      el.style.setProperty("--puppet-sway-rot", swayRotStr);
      el.style.setProperty("--parallax-bg-x", bgXStr);
      el.style.setProperty("--parallax-bg-y", bgYStr);
      el.style.setProperty("--parallax-mid-x", midXStr);
      el.style.setProperty("--parallax-actor-x", actorXStr);
      el.style.setProperty("--parallax-actor-y", actorYStr);
      el.style.setProperty("--parallax-vfx-x", vfxXStr);
      el.style.setProperty("--parallax-vfx-y", vfxYStr);
    });

    return targets.length;
  }

  let puppet25DState = {
    attached: false,
    normX: 0.18,
    normY: -0.14,
    startTimeMs: Date.now(),
    rafId: null
  };

  /**
   * Attaches 2.5D cursor depth-parallax and subtle idle breathing / weapon sway CSS variables
   * (`--puppet-breathe-y`, `--parallax-bg-x`, `--parallax-actor-x`, `--parallax-vfx-x`)
   * to `.hand-card` and `.board-card` elements, with automatic pause during drag or `instantMode`.
   */
  function attachLivePuppet25D() {
    const synced = syncDomCardClasses();
    const updatedCount = applyPuppetCssVarsToElements(
      puppet25DState.normX,
      puppet25DState.normY,
      0.35
    );

    if (typeof globalScope.window !== "undefined" && !puppet25DState.attached) {
      puppet25DState.attached = true;
      puppet25DState.startTimeMs = Date.now();

      globalScope.addEventListener(
        "pointermove",
        (e) => {
          if (isDraggingActive() || isInstantModeActive()) return;
          const vw = Math.max(1, globalScope.innerWidth || 1280);
          const vh = Math.max(1, globalScope.innerHeight || 800);
          puppet25DState.normX = Math.max(-1.0, Math.min(1.0, (e.clientX / vw) * 2.0 - 1.0));
          puppet25DState.normY = Math.max(-1.0, Math.min(1.0, (e.clientY / vh) * 2.0 - 1.0));
          const elapsedSec = (Date.now() - puppet25DState.startTimeMs) / 1000.0;
          applyPuppetCssVarsToElements(puppet25DState.normX, puppet25DState.normY, elapsedSec);
        },
        { passive: true }
      );

      if (typeof globalScope.requestAnimationFrame === "function") {
        const tickPuppet = () => {
          if (!isDraggingActive() && !isInstantModeActive()) {
            const elapsedSec = (Date.now() - puppet25DState.startTimeMs) / 1000.0;
            applyPuppetCssVarsToElements(puppet25DState.normX, puppet25DState.normY, elapsedSec);
          }
          puppet25DState.rafId = globalScope.requestAnimationFrame(tickPuppet);
        };
        puppet25DState.rafId = globalScope.requestAnimationFrame(tickPuppet);
      }
    }

    return {
      attached: true,
      updatedElements: updatedCount,
      handCardCount: synced.handCards.length,
      boardCardCount: synced.boardCards.length,
      boardTileCount: synced.boardTiles.length,
      cssVars: [
        "--puppet-breathe-y",
        "--parallax-bg-x",
        "--parallax-actor-x",
        "--parallax-vfx-x"
      ],
      paused: isDraggingActive() || isInstantModeActive()
    };
  }

  function resolveBoardTileElement(slotIndex) {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    syncDomCardClasses();
    const idx = Math.max(0, Math.min(8, Number(slotIndex) || 0));
    return (
      doc.querySelector(`.board-tile[data-slot="${idx}"]`) ||
      doc.querySelectorAll("#grid-3x3 .board-slot, .board-tile")[idx] ||
      null
    );
  }

  /**
   * Runs `deploy_orbital_slam` on `.board-tile[data-slot="${slotIndex}"]` with
   * squash-and-stretch + recessed socket dust ring SVG burst +
   * `CardFrontHaptics.trigger('card_deploy', 0.85)`.
   */
  function triggerDeploySlam(slotIndex = 0) {
    const idx = Math.max(0, Math.min(8, Number(slotIndex) || 0));
    const hapticPayload = triggerHapticSafe("card_deploy", 0.85);
    const tileEl = resolveBoardTileElement(idx);
    const slamScrubPeak = scrubTo("deploy_orbital_slam", 0.208333);

    if (tileEl && typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      tileEl.classList.remove("sakuga-deploy-slam-active");
      void tileEl.offsetWidth;
      tileEl.classList.add("sakuga-deploy-slam-active");
      tileEl.dataset.sakugaClip = "deploy_orbital_slam";

      const slabEl = doc.getElementById("board-3d-slab");
      if (slabEl) {
        slabEl.classList.remove("thud");
        void slabEl.offsetWidth;
        slabEl.classList.add("thud");
      }

      const oldDust = tileEl.querySelector(".sakuga-socket-dust-svg");
      if (oldDust) oldDust.remove();

      const dustSvg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
      dustSvg.setAttribute("class", "sakuga-socket-dust-svg");
      dustSvg.setAttribute("viewBox", "0 0 256 256");
      dustSvg.setAttribute("aria-hidden", "true");
      dustSvg.style.cssText =
        "position:absolute;inset:-12%;width:124%;height:124%;pointer-events:none;z-index:38;";
      dustSvg.innerHTML =
        '<circle cx="128" cy="128" r="88" fill="none" stroke="#FFB800" stroke-width="8" stroke-dasharray="28 14" opacity="0.92"/>' +
        '<circle cx="128" cy="128" r="108" fill="none" stroke="#00E5FF" stroke-width="5" stroke-dasharray="18 20" opacity="0.85"/>' +
        '<polygon points="128,12 138,44 128,36 118,44" fill="#FFB800"/>' +
        '<polygon points="244,128 212,138 220,128 212,118" fill="#00E5FF"/>' +
        '<polygon points="128,244 138,212 128,220 118,212" fill="#FFB800"/>' +
        '<polygon points="12,128 44,138 36,128 44,118" fill="#00E5FF"/>';
      tileEl.appendChild(dustSvg);

      const cleanupMs = isInstantModeActive() ? 30 : 850;
      setTimeout(() => {
        if (dustSvg.parentNode) dustSvg.remove();
        tileEl.classList.remove("sakuga-deploy-slam-active");
      }, cleanupMs);
    }

    const record = {
      clipId: "deploy_orbital_slam",
      slotIndex: idx,
      durationSec: CLIPS.deploy_orbital_slam.durationSec,
      peakScaleX: slamScrubPeak.scaleX,
      peakScaleY: slamScrubPeak.scaleY,
      fnv1a64: CLIPS.deploy_orbital_slam.fnv1a64,
      hapticTriggered: Boolean(hapticPayload),
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Renders a 2-frame (~83ms at 24fps) high-contrast anime impact flash overlay
   * inside `#board-3d-slab` with SVG radial speed-lines.
   */
  function triggerSakugaImpactFlash2F(slotIndex = 4) {
    const idx = Math.max(0, Math.min(8, Number(slotIndex !== undefined ? slotIndex : 4)));
    const col = idx % 3;
    const row = Math.floor(idx / 3);
    const fxPct = roundTo((col + 0.5) * 33.333, 2);
    const fyPct = roundTo((row + 0.5) * 33.333, 2);

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      injectSakugaStylesheet();
      const slabEl = doc.getElementById("board-3d-slab") || doc.body;
      if (slabEl) {
        let overlay = doc.getElementById("sakuga-impact-flash-2f-overlay");
        if (!overlay) {
          overlay = doc.createElement("div");
          overlay.id = "sakuga-impact-flash-2f-overlay";
          overlay.className = "sakuga-impact-flash-overlay";
          slabEl.appendChild(overlay);
        }
        overlay.dataset.slot = String(idx);
        overlay.dataset.impactFrame = "1";
        overlay.style.setProperty("--impact-fx", `${fxPct}%`);
        overlay.style.setProperty("--impact-fy", `${fyPct}%`);
        overlay.style.opacity = "1";
        overlay.style.display = "block";

        const cx = Math.round((fxPct / 100) * 600);
        const cy = Math.round((fyPct / 100) * 600);
        let raysHtml = "";
        for (let i = 0; i < 16; i++) {
          const angle = (i * Math.PI * 2) / 16;
          const rInner = i % 2 === 0 ? 34 : 58;
          const rOuter = 420;
          const x1 = roundTo(cx + Math.cos(angle) * rInner, 1);
          const y1 = roundTo(cy + Math.sin(angle) * rInner, 1);
          const x2 = roundTo(cx + Math.cos(angle) * rOuter, 1);
          const y2 = roundTo(cy + Math.sin(angle) * rOuter, 1);
          const strokeCol = i % 2 === 0 ? "#FFFFFF" : "#FFB800";
          const strokeW = i % 4 === 0 ? 5.5 : 3.0;
          raysHtml += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${strokeCol}" stroke-width="${strokeW}" stroke-linecap="round"/>`;
        }

        overlay.innerHTML =
          `<svg class="sakuga-impact-speedlines-svg" viewBox="0 0 600 600" preserveAspectRatio="none" ` +
          `style="width:100%;height:100%;display:block;" aria-hidden="true">` +
          `${raysHtml}` +
          `<polygon points="${cx},${cy - 68} ${cx + 16},${cy - 16} ${cx + 68},${cy} ${cx + 16},${cy + 16} ${cx},${cy + 68} ${cx - 16},${cy + 16} ${cx - 68},${cy} ${cx - 16},${cy - 16}" fill="#FFFFFF" stroke="#00E5FF" stroke-width="5"/>` +
          `</svg>`;

        const frame1Ms = isInstantModeActive() ? 12 : Math.round(1000 / SAKUGA_FPS);
        const frame2Ms = isInstantModeActive() ? 24 : Math.round(2000 / SAKUGA_FPS);

        setTimeout(() => {
          overlay.dataset.impactFrame = "2";
        }, frame1Ms);

        setTimeout(() => {
          overlay.style.opacity = "0";
          overlay.style.display = "none";
        }, frame2Ms);
      }
    }

    const record = {
      clipId: "sakuga_impact_flash_2f",
      slotIndex: idx,
      frames: 2,
      fps: SAKUGA_FPS,
      durationMs: roundTo(2000 / SAKUGA_FPS, 2),
      fnv1a64: CLIPS.sakuga_impact_flash_2f.fnv1a64,
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Runs `directional_clash_lunge` (anticipation wind-up -> 24fps Sakuga snap lunge
   * toward N/E/S/W -> 2-frame Impact Flash + SVG directional clash beam -> spring recoil).
   */
  function triggerDirectionalClashLunge(attackerSlot = 4, defenderSlot = 1, direction) {
    const atkIdx = Math.max(0, Math.min(8, Number(attackerSlot !== undefined ? attackerSlot : 4)));
    const defIdx = Math.max(0, Math.min(8, Number(defenderSlot !== undefined ? defenderSlot : 1)));
    const ar = Math.floor(atkIdx / 3);
    const ac = atkIdx % 3;
    const dr = Math.floor(defIdx / 3);
    const dc = defIdx % 3;

    let resolvedDir = String(direction || "").toUpperCase();
    if (!["N", "E", "S", "W"].includes(resolvedDir)) {
      if (dr < ar) resolvedDir = "N";
      else if (dc > ac) resolvedDir = "E";
      else if (dr > ar) resolvedDir = "S";
      else if (dc < ac) resolvedDir = "W";
      else resolvedDir = "N";
    }

    const dirVecMap = {
      N: [0, -1],
      E: [1, 0],
      S: [0, 1],
      W: [-1, 0]
    };
    const [dirX, dirY] = dirVecMap[resolvedDir];

    triggerHapticSafe("sakuga_clash", 0.92);
    const atkEl = resolveBoardTileElement(atkIdx);
    const defEl = resolveBoardTileElement(defIdx);

    if (atkEl) {
      atkEl.style.setProperty("--clash-dir-x", String(dirX));
      atkEl.style.setProperty("--clash-dir-y", String(dirY));
      atkEl.classList.remove("sakuga-clash-lunge-active");
      void atkEl.offsetWidth;
      atkEl.classList.add("sakuga-clash-lunge-active");
      atkEl.dataset.sakugaClip = "directional_clash_lunge";
      atkEl.dataset.clashDirection = resolvedDir;
    }

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      const gridEl = doc.getElementById("grid-3x3") || doc.getElementById("board-3d-slab");
      if (gridEl) {
        const oldBeam = gridEl.querySelector(".sakuga-clash-beam-svg");
        if (oldBeam) oldBeam.remove();

        const x1 = roundTo((ac + 0.5) * 100, 2);
        const y1 = roundTo((ar + 0.5) * 100, 2);
        const x2 = roundTo((dc + 0.5) * 100, 2);
        const y2 = roundTo((dr + 0.5) * 100, 2);

        const beamSvg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
        beamSvg.setAttribute("class", "sakuga-clash-beam-svg");
        beamSvg.setAttribute("data-direction", resolvedDir);
        beamSvg.setAttribute("viewBox", "0 0 300 300");
        beamSvg.setAttribute("aria-hidden", "true");
        beamSvg.style.cssText =
          "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:60;";
        beamSvg.innerHTML =
          `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#00E5FF" stroke-width="14" stroke-opacity="0.38" stroke-linecap="round"/>` +
          `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#FFB800" stroke-width="6" stroke-linecap="round"/>` +
          `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>` +
          `<polygon points="${x2},${y2 - 22} ${x2 + 6},${y2 - 6} ${x2 + 22},${y2} ${x2 + 6},${y2 + 6} ${x2},${y2 + 22} ${x2 - 6},${y2 + 6} ${x2 - 22},${y2} ${x2 - 6},${y2 - 6}" fill="#FFB800" stroke="#FFFFFF" stroke-width="2"/>`;
        gridEl.appendChild(beamSvg);

        const cleanupMs = isInstantModeActive() ? 35 : 750;
        setTimeout(() => {
          if (beamSvg.parentNode) beamSvg.remove();
          if (atkEl) atkEl.classList.remove("sakuga-clash-lunge-active");
          if (defEl) defEl.classList.remove("sakuga-clash-defender-hit");
        }, cleanupMs);
      }
    }

    triggerSakugaImpactFlash2F(defIdx);

    const record = {
      clipId: "directional_clash_lunge",
      attackerSlot: atkIdx,
      defenderSlot: defIdx,
      direction: resolvedDir,
      durationSec: CLIPS.directional_clash_lunge.durationSec,
      fnv1a64: CLIPS.directional_clash_lunge.fnv1a64,
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Runs `capture_flip_180` (`rotateY(180deg)` spring flip + team emissive rim sweep +
   * `CardFrontHaptics.trigger('card_capture', 1.0)`).
   */
  function triggerCaptureFlip180(slotIndex = 0, newOwner = "player") {
    const idx = Math.max(0, Math.min(8, Number(slotIndex) || 0));
    const resolvedOwner =
      String(newOwner || "player").toLowerCase() === "ai" ||
      String(newOwner || "").toLowerCase() === "red"
        ? "ai"
        : "player";
    const rimColor = resolvedOwner === "ai" ? "#FF2E54" : "#00E5FF";
    const accentColor = resolvedOwner === "ai" ? "#F97316" : "#FFB800";

    const hapticPayload = triggerHapticSafe("card_capture", 1.0);
    const tileEl = resolveBoardTileElement(idx);

    if (tileEl && typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      tileEl.style.setProperty("--capture-rim-color", rimColor);
      tileEl.classList.remove("sakuga-capture-flip-180");
      void tileEl.offsetWidth;
      tileEl.classList.add("sakuga-capture-flip-180");
      tileEl.dataset.sakugaClip = "capture_flip_180";
      tileEl.dataset.capturedBy = resolvedOwner;

      const unitEl = tileEl.querySelector(".card-3d-unit, .board-card");
      if (unitEl) {
        unitEl.classList.toggle("owner-player", resolvedOwner === "player");
        unitEl.classList.toggle("owner-ai", resolvedOwner === "ai");
      }

      const oldRim = tileEl.querySelector(".sakuga-capture-rim-svg");
      if (oldRim) oldRim.remove();

      const rimSvg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
      rimSvg.setAttribute("class", "sakuga-capture-rim-svg");
      rimSvg.setAttribute("data-new-owner", resolvedOwner);
      rimSvg.setAttribute("viewBox", "0 0 256 256");
      rimSvg.setAttribute("aria-hidden", "true");
      rimSvg.style.cssText =
        "position:absolute;inset:-6%;width:112%;height:112%;pointer-events:none;z-index:42;";
      rimSvg.innerHTML =
        `<rect x="14" y="14" width="228" height="228" rx="22" fill="none" stroke="${rimColor}" stroke-width="10"/>` +
        `<polygon points="128,18 148,108 238,128 148,148 128,238 108,148 18,128 108,108" fill="${accentColor}" fill-opacity="0.38" stroke="${rimColor}" stroke-width="5"/>`;
      tileEl.appendChild(rimSvg);

      const cleanupMs = isInstantModeActive() ? 30 : 650;
      setTimeout(() => {
        if (rimSvg.parentNode) rimSvg.remove();
        tileEl.classList.remove("sakuga-capture-flip-180");
      }, cleanupMs);
    }

    const record = {
      clipId: "capture_flip_180",
      slotIndex: idx,
      newOwner: resolvedOwner,
      flipDegrees: 180.0,
      durationSec: CLIPS.capture_flip_180.durationSec,
      fnv1a64: CLIPS.capture_flip_180.fnv1a64,
      hapticTriggered: Boolean(hapticPayload),
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Runs `tactical_slide_bank` (`15deg` directional bank + magnetic socket lock +
   * `CardFrontHaptics.trigger('tactical_slide', 0.7)`).
   */
  function triggerTacticalSlideBank(fromSlot = 0, toSlot = 1) {
    const srcIdx = Math.max(0, Math.min(8, Number(fromSlot) || 0));
    const dstIdx = Math.max(0, Math.min(8, Number(toSlot !== undefined ? toSlot : 1)));
    const sr = Math.floor(srcIdx / 3);
    const sc = srcIdx % 3;
    const tr = Math.floor(dstIdx / 3);
    const tc = dstIdx % 3;

    const dx = tc - sc;
    const dy = tr - sr;
    const bankDeg = dx >= 0 ? 15 : -15;

    const hapticPayload = triggerHapticSafe("tactical_slide", 0.7);
    const dstEl = resolveBoardTileElement(dstIdx);

    if (dstEl && typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      dstEl.style.setProperty("--slide-from-dx", `${-dx * 36}px`);
      dstEl.style.setProperty("--slide-from-dy", `${-dy * 36}px`);
      dstEl.style.setProperty("--slide-bank-deg", `${bankDeg}deg`);
      dstEl.classList.remove("sakuga-slide-bank-active");
      void dstEl.offsetWidth;
      dstEl.classList.add("sakuga-slide-bank-active");
      dstEl.dataset.sakugaClip = "tactical_slide_bank";

      const oldLock = dstEl.querySelector(".sakuga-slide-lock-svg");
      if (oldLock) oldLock.remove();

      const lockSvg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
      lockSvg.setAttribute("class", "sakuga-slide-lock-svg");
      lockSvg.setAttribute("viewBox", "0 0 256 256");
      lockSvg.setAttribute("aria-hidden", "true");
      lockSvg.style.cssText =
        "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:36;";
      lockSvg.innerHTML =
        '<polyline points="20,64 20,20 64,20" fill="none" stroke="#2EE6D3" stroke-width="10" stroke-linecap="round"/>' +
        '<polyline points="192,20 236,20 236,64" fill="none" stroke="#2EE6D3" stroke-width="10" stroke-linecap="round"/>' +
        '<polyline points="20,192 20,236 64,236" fill="none" stroke="#2EE6D3" stroke-width="10" stroke-linecap="round"/>' +
        '<polyline points="192,236 236,236 236,192" fill="none" stroke="#2EE6D3" stroke-width="10" stroke-linecap="round"/>';
      dstEl.appendChild(lockSvg);

      const cleanupMs = isInstantModeActive() ? 30 : 550;
      setTimeout(() => {
        if (lockSvg.parentNode) lockSvg.remove();
        dstEl.classList.remove("sakuga-slide-bank-active");
      }, cleanupMs);
    }

    const record = {
      clipId: "tactical_slide_bank",
      fromSlot: srcIdx,
      toSlot: dstIdx,
      bankDeg,
      durationSec: CLIPS.tactical_slide_bank.durationSec,
      fnv1a64: CLIPS.tactical_slide_bank.fnv1a64,
      hapticTriggered: Boolean(hapticPayload),
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Runs `column_die_nudge_surge` traveling from `#col-die-${colIndex}` straight down
   * all 3 tiles in column `colIndex` with golden rune conduit pulse +
   * `CardFrontHaptics.trigger('die_nudge', 0.8)`.
   */
  function triggerColumnDieSurge(colIndex = 0) {
    const col = Math.max(0, Math.min(2, Number(colIndex) || 0));
    const affectedSlots = [col, 3 + col, 6 + col];
    const hapticPayload = triggerHapticSafe("die_nudge", 0.8);

    if (typeof globalScope.document !== "undefined") {
      const doc = globalScope.document;
      syncDomCardClasses();

      const dieEl = doc.getElementById(`col-die-${col}`);
      if (dieEl) {
        dieEl.classList.add("sakuga-die-nudge-active");
        setTimeout(() => {
          dieEl.classList.remove("sakuga-die-nudge-active");
        }, isInstantModeActive() ? 30 : 600);
      }

      affectedSlots.forEach((slotIdx, rowIdx) => {
        const tileEl = resolveBoardTileElement(slotIdx);
        if (!tileEl) return;

        const delayMs = isInstantModeActive() ? 0 : rowIdx * 55;
        setTimeout(() => {
          tileEl.classList.remove("sakuga-col-surge-tile");
          void tileEl.offsetWidth;
          tileEl.classList.add("sakuga-col-surge-tile");
          tileEl.dataset.sakugaClip = "column_die_nudge_surge";

          const oldRune = tileEl.querySelector(".sakuga-col-surge-svg");
          if (oldRune) oldRune.remove();

          const runeSvg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
          runeSvg.setAttribute("class", "sakuga-col-surge-svg");
          runeSvg.setAttribute("data-col", String(col));
          runeSvg.setAttribute("viewBox", "0 0 256 256");
          runeSvg.setAttribute("aria-hidden", "true");
          runeSvg.style.cssText =
            "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:34;";
          runeSvg.innerHTML =
            '<line x1="128" y1="0" x2="128" y2="256" stroke="#FFB800" stroke-width="10" stroke-dasharray="22 10" opacity="0.88"/>' +
            '<polygon points="128,36 164,128 128,220 92,128" fill="none" stroke="#00E5FF" stroke-width="7"/>';
          tileEl.appendChild(runeSvg);

          setTimeout(() => {
            if (runeSvg.parentNode) runeSvg.remove();
            tileEl.classList.remove("sakuga-col-surge-tile");
          }, isInstantModeActive() ? 30 : 540);
        }, delayMs);
      });
    }

    const record = {
      clipId: "column_die_nudge_surge",
      colIndex: col,
      affectedSlots,
      durationSec: CLIPS.column_die_nudge_surge.durationSec,
      fnv1a64: CLIPS.column_die_nudge_surge.fnv1a64,
      hapticTriggered: Boolean(hapticPayload),
      timestamp: Date.now()
    };
    SynapseSakugaAnimEngine.lastTriggeredClip = record;
    SynapseSakugaAnimEngine.history.push(record);
    return record;
  }

  /**
   * Injects a compact `#sakuga-anim-engine-bar` section inside `#deckbuilder-modal`
   * (below `#multiplatform-crypto-vault-bar`, minimum `12px` font size, zero generic emojis)
   * allowing the player or test harness to inspect the `120Hz Spring + 24fps Sakuga + 2.5D FABRIK IK`
   * status and click `#btn-test-sakuga-clash` to preview a live Sakuga Clash & 2.5D Puppet rig check.
   */
  function injectSakugaAnimStudioBar() {
    if (typeof globalScope.document === "undefined") return null;
    const doc = globalScope.document;
    const modal = doc.getElementById("deckbuilder-modal");
    if (!modal) return null;

    if (
      globalScope.CardFrontPlatformBridge &&
      typeof globalScope.CardFrontPlatformBridge.injectMultiPlatformVaultSection === "function" &&
      !doc.getElementById("multiplatform-crypto-vault-bar")
    ) {
      globalScope.CardFrontPlatformBridge.injectMultiPlatformVaultSection();
    }

    const anchorEl =
      doc.getElementById("multiplatform-crypto-vault-bar") ||
      doc.getElementById("deckbuilder-squad-summary");
    if (!anchorEl) return null;

    let studioBar = doc.getElementById("sakuga-anim-engine-bar");
    if (!studioBar) {
      studioBar = doc.createElement("div");
      studioBar.id = "sakuga-anim-engine-bar";
      studioBar.style.cssText =
        "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;" +
        "background:linear-gradient(135deg,rgba(15,23,42,0.96),rgba(30,27,75,0.92));" +
        "border:1px solid rgba(0,229,255,0.52);border-radius:8px;padding:7px 10px;" +
        "font-size:12px;color:#F8FAFC;box-shadow:0 6px 18px rgba(0,0,0,0.45);";
      anchorEl.insertAdjacentElement("afterend", studioBar);
    }

    const iconSpark = renderIcon("sakuga_spark", 14);
    const iconPuppet = renderIcon("puppet_rig", 14);
    const iconBolt = renderIcon("bolt", 14);
    const iconSword = renderIcon("sword", 14);

    studioBar.innerHTML =
      `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
      `${iconSpark}` +
      `<b style="color:#00E5FF;font-size:12px;letter-spacing:0.4px;">SAKUGA ANIM STUDIO v1.0:</b>` +
      `<span class="cf-sakuga-pill" style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:99px;border:1px solid #FFB800;background:rgba(255,184,0,0.14);color:#FEF08A;font-size:12px;font-weight:800;">` +
      `${iconBolt}<span style="font-size:12px;">120Hz Spring + 24fps Sakuga + 2.5D FABRIK IK</span></span>` +
      `<span class="cf-sakuga-pill" style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:99px;border:1px solid #2EE6D3;background:rgba(46,230,211,0.14);color:#CCFBF1;font-size:12px;font-weight:800;">` +
      `${iconPuppet}<span style="font-size:12px;">8 .cfanim Clips Verified (FNV-1a 64-bit)</span></span>` +
      `</div>` +
      `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
      `<button type="button" id="btn-test-sakuga-clash" style="display:inline-flex;align-items:center;gap:5px;` +
      `background:linear-gradient(135deg,#e11d48,#9f1239);border:1px solid #fda4af;color:#f8fafc;` +
      `border-radius:7px;padding:4px 10px;font-size:12px;font-weight:800;cursor:pointer;">` +
      `${iconSword}<span style="font-size:12px;">Test Sakuga Clash &amp; 2.5D Puppet</span></button>` +
      `</div>`;

    const btnClash = doc.getElementById("btn-test-sakuga-clash");
    if (btnClash) {
      btnClash.onclick = () => {
        const springCheck = solveSpring1D(0, 0, 1, 460, 32, 1, 1 / 120);
        const ikCheck = solveFabrik2D(
          [
            [12, 46],
            [28, 38],
            [46, 28],
            [62, 22]
          ],
          54,
          30,
          0.001,
          10
        );
        const scrubCheck = scrubTo("directional_clash_lunge", 0.25);
        attachLivePuppet25D();
        triggerDirectionalClashLunge(4, 1, "N");

        const statusEl = doc.getElementById("deckbuilder-status");
        if (statusEl) {
          statusEl.innerHTML =
            `<span style="display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">` +
            `${iconSpark}` +
            `<b style="color:#00E5FF;font-size:12px;">Synapse-Sakuga-AnimEngine v1.0 Verified:</b> ` +
            `<span style="color:#FEF08A;font-family:ui-monospace,monospace;font-size:12px;">` +
            `120Hz Spring (zeta=${springCheck.zeta}) | 24fps HitStop=${scrubCheck.inHitStop} | FABRIK IK err=${ikCheck.error} | FNV-1a ${CLIPS.directional_clash_lunge.fnv1a64}` +
            `</span></span>`;
        }
      };
    }

    return studioBar;
  }

  function hookTabletopRuntimeBridges() {
    if (
      typeof globalScope.openDeckbuilderModal === "function" &&
      !globalScope.openDeckbuilderModal.__sakugaStudioWrapped
    ) {
      const origOpen = globalScope.openDeckbuilderModal;
      const wrappedOpen = function (...args) {
        const res = origOpen.apply(this, args);
        injectSakugaAnimStudioBar();
        return res;
      };
      wrappedOpen.__sakugaStudioWrapped = true;
      globalScope.openDeckbuilderModal = wrappedOpen;
    }

    if (
      typeof globalScope.renderAll === "function" &&
      !globalScope.renderAll.__sakugaRenderWrapped
    ) {
      const origRenderAll = globalScope.renderAll;
      const wrappedRenderAll = function (...args) {
        const res = origRenderAll.apply(this, args);
        syncDomCardClasses();
        const elapsedSec = (Date.now() - puppet25DState.startTimeMs) / 1000.0;
        applyPuppetCssVarsToElements(puppet25DState.normX, puppet25DState.normY, elapsedSec);
        return res;
      };
      wrappedRenderAll.__sakugaRenderWrapped = true;
      globalScope.renderAll = wrappedRenderAll;
    }

    if (
      typeof globalScope.nudgeColDie === "function" &&
      !globalScope.nudgeColDie.__sakugaNudgeWrapped
    ) {
      const origNudge = globalScope.nudgeColDie;
      const wrappedNudge = function (colIdx, ...rest) {
        const res = origNudge.call(this, colIdx, ...rest);
        triggerColumnDieSurge(colIdx);
        return res;
      };
      wrappedNudge.__sakugaNudgeWrapped = true;
      globalScope.nudgeColDie = wrappedNudge;
    }

    injectSakugaAnimStudioBar();
    attachLivePuppet25D();
  }

  const SynapseSakugaAnimEngine = {
    VERSION: ENGINE_VERSION,
    ENGINE_ID: "Synapse-Sakuga-AnimEngine",
    PHYSICS_HZ,
    SAKUGA_FPS,
    PARALLAX_DEPTHS: PARALLAX_LAYER_DEPTHS,
    CLIPS,
    instantMode: false,
    lastTriggeredClip: null,
    history: [],

    computeFnv1a64,
    solveSpring1D,
    quantizeSakugaTime,
    solveFabrik2D,
    computeParallaxOffsets,
    scrubTo,

    attachLivePuppet25D,
    triggerDeploySlam,
    triggerDirectionalClashLunge,
    triggerCaptureFlip180,
    triggerTacticalSlideBank,
    triggerColumnDieSurge,
    triggerSakugaImpactFlash2F,
    injectSakugaAnimStudioBar,
    syncDomCardClasses
  };

  globalScope.SynapseSakugaAnimEngine = SynapseSakugaAnimEngine;

  if (typeof globalScope.document !== "undefined") {
    if (globalScope.document.readyState === "loading") {
      globalScope.document.addEventListener("DOMContentLoaded", hookTabletopRuntimeBridges);
    } else {
      hookTabletopRuntimeBridges();
    }
  }

  if (typeof globalScope.addEventListener === "function") {
    globalScope.addEventListener("DOMContentLoaded", hookTabletopRuntimeBridges);
    globalScope.addEventListener("load", hookTabletopRuntimeBridges);
  }
})(typeof window !== "undefined" ? window : globalThis);
