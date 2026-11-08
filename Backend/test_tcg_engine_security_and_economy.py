#!/usr/bin/env python3
"""
Automated Security & Economy Regression Suite for TcgEngineAPI & GameServer.cs (V1-V6)
Executes syntax checks (`node -c`) and an in-memory Node.js mock harness against the real
controllers to prove that all 6 critical vulnerabilities are remediated and the 15% market sink
is enforced.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

NODE_BIN = "/Users/frederickamina/.local/bin/node"
API_DIR = "/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/TcgEngineAPI"
GAMESERVER_CS = "/Users/frederickamina/Documents/Projects/SYNAPSE/tcg-engine-unpacked/Assets/TcgEngine/Scripts/GameServer/GameServer.cs"
REPORT_PATH = "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine/Datasets/security_audit_v1_to_v6_remediation_report.json"

JS_FILES = [
    "config.js",
    "server.js",
    "tools/tx_lock.tool.js",
    "users/users.controller.js",
    "users/users.cards.controller.js",
    "market/market.controller.js",
    "matches/matches.controller.js",
    "matches/matches.tool.js",
]

NODE_HARNESS_SCRIPT = r"""
const Module = require('module');
const path = require('path');
const assert = require('assert');

const apiDir = process.argv[1];
const config = require(path.join(apiDir, 'config.js'));
const TxLock = require(path.join(apiDir, 'tools/tx_lock.tool.js'));

// In-memory state for mock models
const state = {
    usersById: new Map(),
    usersByUsername: new Map(),
    usersByEmail: new Map(),
    rewards: new Map(),
    packs: new Map(),
    cards: new Map(),
    variants: new Map(),
    offers: new Map(),
    matches: new Map(),
    activities: [],
};

function resetState() {
    state.usersById.clear();
    state.usersByUsername.clear();
    state.usersByEmail.clear();
    state.rewards.clear();
    state.packs.clear();
    state.cards.clear();
    state.variants.clear();
    state.offers.clear();
    state.matches.clear();
    state.activities = [];
    state.variants.set("standard", { tid: "standard", cost_factor: 1, is_default: true });
    state.variants.set("foil", { tid: "foil", cost_factor: 2, is_default: false });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function cloneUser(u) {
    if (!u) return null;
    const copy = JSON.parse(JSON.stringify(u));
    copy.deleteSecrets = function() {
        const c = JSON.parse(JSON.stringify(this));
        delete c.password;
        delete c.refresh_key;
        return c;
    };
    copy.deleteAdminOnly = copy.deleteSecrets;
    copy.save = async function() {
        await sleep(5);
        const stored = state.usersById.get(this.id || this._id);
        if (stored) {
            Object.assign(stored, JSON.parse(JSON.stringify(this)));
        }
        return this;
    };
    return copy;
}

const mocks = {
    'jsonwebtoken': {
        sign: (payload, secret) => "jwt_" + Buffer.from(JSON.stringify(payload)).toString('base64'),
        verify: (token, secret) => JSON.parse(Buffer.from(token.replace(/^jwt_/, ""), 'base64').toString('utf8'))
    },
    './users.model': {
        count: async () => state.usersById.size,
        getByUsername: async (u) => {
            await sleep(5);
            return cloneUser(state.usersByUsername.get(u));
        },
        getByEmail: async (e) => {
            await sleep(5);
            return cloneUser(state.usersByEmail.get(e));
        },
        getById: async (id) => {
            await sleep(5);
            return cloneUser(state.usersById.get(id));
        },
        getAll: async () => {
            await sleep(5);
            return Array.from(state.usersById.values()).map(cloneUser);
        },
        create: async (u) => {
            await sleep(5);
            const id = u._id || ("uid_" + (state.usersById.size + 1));
            const record = Object.assign({
                _id: id,
                id: id,
                rewards: [],
                cards: [],
                packs: [],
                decks: [],
                avatars: [],
                cardbacks: [],
                coins: config.start_coins,
                elo: config.start_elo,
                xp: 0,
                matches: 0,
                victories: 0,
                defeats: 0,
            }, JSON.parse(JSON.stringify(u)));
            state.usersById.set(id, record);
            state.usersByUsername.set(record.username, record);
            state.usersByEmail.set(record.email, record);
            return cloneUser(record);
        },
        save: async (user, fields) => {
            await sleep(8);
            const stored = state.usersById.get(user.id || user._id);
            if (!stored) return null;
            for (const f of fields) {
                stored[f] = JSON.parse(JSON.stringify(user[f]));
            }
            return cloneUser(stored);
        },
        update: async (user, data) => {
            await sleep(8);
            const stored = state.usersById.get(user.id || user._id);
            if (!stored) return null;
            Object.assign(stored, JSON.parse(JSON.stringify(data)));
            return cloneUser(stored);
        },
        remove: async (id) => {
            state.usersById.delete(id);
        }
    },
    '../rewards/rewards.model': {
        get: async (id) => state.rewards.get(id) || null
    },
    '../packs/packs.model': {
        get: async (id) => state.packs.get(id) || null
    },
    '../cards/cards.model': {
        get: async (id) => state.cards.get(id) || null
    },
    '../cards/cards.tool': {
        getPackCards: async (pack) => {
            await sleep(5);
            return [
                { tid: "c_iron_vanguard", variant: "standard", quantity: 1 },
                { tid: "c_ash_crawler", variant: "standard", quantity: 1 },
                { tid: "c_bio_drone", variant: "standard", quantity: 1 },
                { tid: "c_neural_spike", variant: "standard", quantity: 1 },
                { tid: "c_void_harbinger", variant: "standard", quantity: 1 }
            ];
        }
    },
    '../variants/variants.model': {
        get: async (id) => state.variants.get(id) || null,
        getDefault: async () => state.variants.get("standard")
    },
    '../variants/variants.model.js': {
        get: async (id) => state.variants.get(id) || null,
        getDefault: async () => state.variants.get("standard")
    },
    '../decks/decks.model': {
        getList: async () => []
    },
    '../activity/activity.model': {
        LogActivity: async (type, username, data) => {
            const entry = { type, username, data };
            state.activities.push(entry);
            return entry;
        }
    },
    '../tools/email.tool': {
        SendEmail: (e, s, t, cb) => { if (cb) cb(true); }
    },
    './market.model': {
        add: async (username, card, variant, offer) => {
            await sleep(5);
            const key = `${username}:${card}:${variant}`;
            const rec = Object.assign({}, offer, {
                toObj: function() { return { seller: this.seller, card: this.card, variant: this.variant, quantity: this.quantity, price: this.price }; }
            });
            state.offers.set(key, rec);
            return rec;
        },
        getOffer: async (username, card, variant) => {
            await sleep(5);
            const key = `${username}:${card}:${variant}`;
            const rec = state.offers.get(key);
            if (!rec || rec.quantity <= 0) return null;
            return Object.assign({}, rec);
        },
        reduce: async (username, card, variant, qty) => {
            await sleep(5);
            const key = `${username}:${card}:${variant}`;
            const rec = state.offers.get(key);
            if (!rec || rec.quantity < qty) return null;
            rec.quantity -= qty;
            if (rec.quantity <= 0) state.offers.delete(key);
            return rec;
        },
        remove: async (username, card, variant) => {
            await sleep(5);
            const key = `${username}:${card}:${variant}`;
            return state.offers.delete(key);
        }
    },
    './matches.model': {
        get: async (tid) => {
            await sleep(5);
            return state.matches.get(tid) || null;
        },
        create: async (m) => {
            await sleep(5);
            const rec = Object.assign({}, m, {
                markModified: () => {},
                save: async function() {
                    await sleep(5);
                    state.matches.set(this.tid, this);
                    return this;
                }
            });
            state.matches.set(m.tid, rec);
            return rec;
        }
    }
};

// Also alias '../users/users.model' to './users.model'
mocks['../users/users.model'] = mocks['./users.model'];

const origLoad = Module._load;
Module._load = function(request, parent, isMain) {
    if (mocks[request]) {
        return mocks[request];
    }
    return origLoad.apply(this, arguments);
};

const UsersController = require(path.join(apiDir, 'users/users.controller.js'));
const UsersCardsController = require(path.join(apiDir, 'users/users.cards.controller.js'));
const MarketController = require(path.join(apiDir, 'market/market.controller.js'));
const MatchesController = require(path.join(apiDir, 'matches/matches.controller.js'));

function makeRes() {
    return {
        statusCode: 200,
        body: null,
        status(c) { this.statusCode = c; return this; },
        send(b) { this.body = b; return this; }
    };
}

async function runTests() {
    const results = {};

    // =========================================================================
    // V1: Default JWT Secret Rejection & Sovereign 256-bit Secret Enforcement
    // =========================================================================
    let v1ThrewOnDefault = false;
    try {
        TxLock.assertSecureConfig({ jwt_secret: "JWT_123456789", server_hmac_secret: config.server_hmac_secret });
    } catch (e) {
        v1ThrewOnDefault = true;
    }
    const v1CurrentValid = TxLock.assertSecureConfig(config);
    results.V1_hardcoded_jwt_remediation = {
        passed: v1ThrewOnDefault && v1CurrentValid && config.jwt_secret !== "JWT_123456789" && config.jwt_secret.length >= 64,
        default_jwt_rejected: v1ThrewOnDefault,
        active_secret_length: config.jwt_secret.length,
        hmac_secret_length: config.server_hmac_secret.length,
    };

    // =========================================================================
    // V5: First-User Auto-Admin Privilege Escalation Blocked Without Bootstrap
    // =========================================================================
    resetState();
    const reqFirstNoToken = {
        headers: {},
        body: { username: "attacker1", email: "attacker1@test.com", password: "Password123!" }
    };
    const resFirstNoToken = makeRes();
    await UsersController.RegisterUser(reqFirstNoToken, resFirstNoToken);
    const attackerUser = state.usersByUsername.get("attacker1");

    resetState();
    const reqFirstWithToken = {
        headers: { "x-admin-bootstrap": config.admin_bootstrap_token },
        body: { username: "sovereignadmin", email: "admin@cardfront.io", password: "Password123!" }
    };
    const resFirstWithToken = makeRes();
    await UsersController.RegisterUser(reqFirstWithToken, resFirstWithToken);
    const adminUser = state.usersByUsername.get("sovereignadmin");

    results.V5_bootstrap_admin_hardening = {
        passed: attackerUser.permission_level === 1 && adminUser.permission_level === 10,
        unauthenticated_first_user_permission: attackerUser.permission_level,
        bootstrapped_first_user_permission: adminUser.permission_level,
    };

    // =========================================================================
    // V3: Client-Triggered GainReward Blocked Without Server Receipt / Server Role
    // =========================================================================
    resetState();
    await mocks['./users.model'].create({ _id: "u_player1", username: "player1", email: "p1@test.com", coins: 1000, rewards: [] });
    state.rewards.set("tut_reward_500", { tid: "tut_reward_500", coins: 500, xp: 100, repeat: false });

    // 1. Client tries to claim reward without server_receipt -> 403
    const resForgedReward = makeRes();
    await UsersController.GainReward({
        params: { userId: "u_player1" },
        jwt: { userId: "u_player1", username: "player1", permission_level: 1 },
        body: { reward: "tut_reward_500" }
    }, resForgedReward);

    // 2. Client tries to claim reward with invalid signature -> 403
    const resBadSigReward = makeRes();
    await UsersController.GainReward({
        params: { userId: "u_player1" },
        jwt: { userId: "u_player1", username: "player1", permission_level: 1 },
        body: { reward: "tut_reward_500", server_receipt: "deadbeef0000" }
    }, resBadSigReward);

    // 3. Client claims with valid HMAC receipt -> 200
    const validReceipt = TxLock.createServerReceipt("u_player1:tut_reward_500");
    const resValidReward = makeRes();
    await UsersController.GainReward({
        params: { userId: "u_player1" },
        jwt: { userId: "u_player1", username: "player1", permission_level: 1 },
        body: { reward: "tut_reward_500", server_receipt: validReceipt }
    }, resValidReward);

    const p1AfterReward = state.usersById.get("u_player1");
    results.V3_gain_reward_hmac_gate = {
        passed: resForgedReward.statusCode === 403 && resBadSigReward.statusCode === 403 && resValidReward.statusCode === 200 && p1AfterReward.coins === 1500,
        forged_client_status: resForgedReward.statusCode,
        bad_hmac_status: resBadSigReward.statusCode,
        valid_hmac_status: resValidReward.statusCode,
        coins_after_valid_claim: p1AfterReward.coins,
    };

    // =========================================================================
    // V4: 20-Way Parallel Promise.all Race Conditions (OpenPack, SellCard, Trade)
    // =========================================================================
    resetState();
    state.packs.set("core_pack", { tid: "core_pack", cost: 100, cards: 5 });
    state.cards.set("c_legend_mech", { tid: "c_legend_mech", cost: 500 });
    await mocks['./users.model'].create({
        _id: "u_racer",
        username: "racer",
        email: "racer@test.com",
        coins: 0,
        packs: [{ tid: "core_pack", quantity: 1 }],
        cards: [{ tid: "c_legend_mech", variant: "standard", quantity: 1 }]
    });

    // 4a. 20 concurrent OpenPack requests on 1 pack
    const openPackResponses = await Promise.all(
        Array.from({ length: 20 }, () => {
            const res = makeRes();
            return UsersCardsController.OpenPack({
                jwt: { userId: "u_racer", username: "racer", permission_level: 1 },
                body: { pack: "core_pack" }
            }, res).then(() => res);
        })
    );
    const openSuccesses = openPackResponses.filter(r => r.statusCode === 200).length;
    const openFailures = openPackResponses.filter(r => r.statusCode === 400).length;

    // 4b. 20 concurrent SellCard requests on 1 copy of c_legend_mech
    const sellCardResponses = await Promise.all(
        Array.from({ length: 20 }, () => {
            const res = makeRes();
            return UsersCardsController.SellCard({
                jwt: { userId: "u_racer", username: "racer", permission_level: 1 },
                body: { card: "c_legend_mech", variant: "standard", quantity: 1 }
            }, res).then(() => res);
        })
    );
    const sellSuccesses = sellCardResponses.filter(r => r.statusCode === 200).length;
    const sellFailures = sellCardResponses.filter(r => r.statusCode === 400).length;
    const racerAfterSell = state.usersById.get("u_racer");

    // 4c. 20 concurrent Market trade requests + 15% Collector Market Sink check
    await mocks['./users.model'].create({
        _id: "u_seller",
        username: "seller_bob",
        email: "bob@test.com",
        coins: 0,
        cards: [{ tid: "c_legend_mech", variant: "foil", quantity: 1 }]
    });
    await mocks['./users.model'].create({
        _id: "u_buyer",
        username: "buyer_alice",
        email: "alice@test.com",
        coins: 20000,
        cards: []
    });

    const addOfferRes = makeRes();
    await MarketController.addOffer({
        jwt: { userId: "u_seller", username: "seller_bob", permission_level: 1 },
        body: { card: "c_legend_mech", variant: "foil", quantity: 1, price: 1000 }
    }, addOfferRes);

    const tradeResponses = await Promise.all(
        Array.from({ length: 20 }, () => {
            const res = makeRes();
            return MarketController.trade({
                jwt: { userId: "u_buyer", username: "buyer_alice", permission_level: 1 },
                body: { seller: "seller_bob", card: "c_legend_mech", variant: "foil", quantity: 1 }
            }, res).then(() => res);
        })
    );
    const tradeSuccesses = tradeResponses.filter(r => r.statusCode === 200).length;
    const tradeFailures = tradeResponses.filter(r => r.statusCode >= 400).length;
    const sellerAfter = state.usersByUsername.get("seller_bob");
    const buyerAfter = state.usersByUsername.get("buyer_alice");

    results.V4_mutex_serialization_and_market_sink = {
        passed: (
            openSuccesses === 1 && openFailures === 19 &&
            sellSuccesses === 1 && sellFailures === 19 &&
            racerAfterSell.coins === 400 &&
            tradeSuccesses === 1 && tradeFailures === 19 &&
            sellerAfter.coins === 850 && buyerAfter.coins === 19000
        ),
        open_pack_20_way: { successes: openSuccesses, clean_rejections: openFailures },
        sell_card_20_way: { successes: sellSuccesses, clean_rejections: sellFailures, final_coins: racerAfterSell.coins },
        market_trade_20_way: {
            successes: tradeSuccesses,
            clean_rejections: tradeFailures,
            offer_price: 1000,
            fee_15_pct: 150,
            seller_payout: sellerAfter.coins,
            buyer_remaining_coins: buyerAfter.coins
        }
    };

    // =========================================================================
    // V2: Match Completion Integrity, ELO Persistence & Tie Safety
    // =========================================================================
    resetState();
    await mocks['./users.model'].create({ _id: "u_p1", username: "duelist_1", email: "d1@test.com", elo: 1000, coins: 1000, xp: 0, matches: 0, victories: 0, defeats: 0 });
    await mocks['./users.model'].create({ _id: "u_p2", username: "duelist_2", email: "d2@test.com", elo: 1000, coins: 1000, xp: 0, matches: 0, victories: 0, defeats: 0 });
    await mocks['./users.model'].create({ _id: "u_bystander", username: "bystander", email: "b@test.com", elo: 1500, coins: 1000 });

    // Add match with SERVER permission
    const addMatchRes = makeRes();
    await MatchesController.addMatch({
        jwt: { permission_level: config.permissions.SERVER },
        body: { tid: "match_001", players: ["duelist_1", "duelist_2"], ranked: true, mode: "ranked" }
    }, addMatchRes);

    // Attempt spoofing with non-participant winner -> 403
    const spoofWinnerRes = makeRes();
    await MatchesController.completeMatch({
        jwt: { permission_level: config.permissions.SERVER },
        body: { tid: "match_001", winner: "bystander" }
    }, spoofWinnerRes);

    // Attempt completion with user permission -> 403
    const userCompleteRes = makeRes();
    await MatchesController.completeMatch({
        jwt: { permission_level: config.permissions.USER },
        body: { tid: "match_001", winner: "duelist_1" }
    }, userCompleteRes);

    // Valid completion with HMAC
    const matchHmac = TxLock.createServerReceipt("match_001:duelist_1");
    const validCompleteRes = makeRes();
    await MatchesController.completeMatch({
        jwt: { permission_level: config.permissions.SERVER },
        body: { tid: "match_001", winner: "duelist_1", match_hmac: matchHmac }
    }, validCompleteRes);

    const d1After = state.usersByUsername.get("duelist_1");
    const d2After = state.usersByUsername.get("duelist_2");

    results.V2_match_integrity_and_elo_save = {
        passed: (
            addMatchRes.statusCode === 200 &&
            spoofWinnerRes.statusCode === 403 &&
            userCompleteRes.statusCode === 403 &&
            validCompleteRes.statusCode === 200 &&
            d1After.elo > 1000 && d2After.elo < 1000 &&
            d1After.victories === 1 && d2After.defeats === 1
        ),
        non_participant_winner_status: spoofWinnerRes.statusCode,
        client_spoof_status: userCompleteRes.statusCode,
        valid_server_complete_status: validCompleteRes.statusCode,
        winner_persisted_elo: d1After.elo,
        loser_persisted_elo: d2After.elo
    };

    // =========================================================================
    // V6: FixVariants ReferenceError Remediation & Admin Gate
    // =========================================================================
    resetState();
    await mocks['./users.model'].create({
        _id: "u_legacy",
        username: "legacy_collector",
        email: "leg@test.com",
        cards: [{ tid: "c_iron_vanguard", variant: "old_foil", quantity: 2 }]
    });

    const nonAdminFixRes = makeRes();
    await UsersCardsController.FixVariants({
        jwt: { username: "player", permission_level: config.permissions.USER },
        body: { from: "old_foil", to: "foil" }
    }, nonAdminFixRes);

    const adminFixRes = makeRes();
    await UsersCardsController.FixVariants({
        jwt: { username: "admin", permission_level: config.permissions.ADMIN },
        body: { from: "old_foil", to: "foil" }
    }, adminFixRes);

    const legacyAfter = state.usersById.get("u_legacy");
    results.V6_fix_variants_and_cors_hardening = {
        passed: (
            nonAdminFixRes.statusCode === 403 &&
            adminFixRes.statusCode === 200 &&
            adminFixRes.body.updated === 1 &&
            legacyAfter.cards[0].variant === "foil"
        ),
        non_admin_status: nonAdminFixRes.statusCode,
        admin_status: adminFixRes.statusCode,
        updated_users_count: adminFixRes.body.updated,
        migrated_variant: legacyAfter.cards[0].variant
    };

    console.log(JSON.stringify(results));
}

runTests().catch(err => {
    console.error(err);
    process.exit(1);
});
"""


def main():
    syntax_checks = []
    all_syntax_ok = True
    for rel_path in JS_FILES:
        full_path = os.path.join(API_DIR, rel_path)
        proc = subprocess.run([NODE_BIN, "-c", full_path], capture_output=True, text=True)
        passed = proc.returncode == 0
        if not passed:
            all_syntax_ok = False
        syntax_checks.append({
            "file": rel_path,
            "passed": passed,
            "stderr": proc.stderr.strip(),
        })

    # Verify GameServer.cs tie-game null-check remediation
    with open(GAMESERVER_CS, "r", encoding="utf-8") as f:
        cs_source = f.read()
    cs_tie_safe = (
        "int winner_pid = winner != null ? winner.player_id : -1;" in cs_source
        and "if (winner_pid >= 0)" in cs_source
    )

    # Verify server.js CORS hardening
    with open(os.path.join(API_DIR, "server.js"), "r", encoding="utf-8") as f:
        server_js_source = f.read()
    cors_hardened = (
        "config.allowed_origins.includes(origin)" in server_js_source
        and "X-Content-Type-Options" in server_js_source
        and "X-Frame-Options" in server_js_source
        and "TxLock.assertSecureConfig()" in server_js_source
    )

    # Run Node in-memory exploit & concurrency test harness
    harness_proc = subprocess.run(
        [NODE_BIN, "-e", NODE_HARNESS_SCRIPT, API_DIR],
        capture_output=True,
        text=True,
    )
    if harness_proc.returncode != 0:
        print("Node harness failed:", harness_proc.stderr, file=sys.stderr)
        sys.exit(1)

    harness_results = json.loads(harness_proc.stdout.strip().splitlines()[-1])
    harness_results["V2_match_integrity_and_elo_save"]["gameserver_cs_tie_null_safe"] = cs_tie_safe
    harness_results["V2_match_integrity_and_elo_save"]["passed"] = (
        harness_results["V2_match_integrity_and_elo_save"]["passed"] and cs_tie_safe
    )
    harness_results["V6_fix_variants_and_cors_hardening"]["cors_and_headers_hardened"] = cors_hardened
    harness_results["V6_fix_variants_and_cors_hardening"]["passed"] = (
        harness_results["V6_fix_variants_and_cors_hardening"]["passed"] and cors_hardened
    )

    all_passed = all_syntax_ok and all(v["passed"] for v in harness_results.values())

    report = {
        "suite": "TcgEngineAPI & GameServer.cs Security & Economy Remediation Suite (V1-V6)",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "node_binary": NODE_BIN,
        "all_passed": all_passed,
        "syntax_checks": syntax_checks,
        "vulnerability_remediations": harness_results,
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
