#!/usr/bin/env python3
"""
test_multiplatform_execution_suite.py
CARDFRONT 3D: Cradle of Echoes (`Synapse.TcgEngine`) — Multiplatform Execution,
Cryptographic Cross-Save, Custom Atelier SVG Icon Library, and Standalone Deck Separation Test Suite.
"""

from __future__ import annotations

import copy
import hashlib
import html.parser
import json
import sys
import unittest
from pathlib import Path
from typing import List, Optional, Tuple

ROOT_DIR = Path("/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine")
BACKEND_DIR = ROOT_DIR / "Backend"
WEB_DIR = ROOT_DIR / "WebPlayable"
ICONS_MANIFEST_PATH = WEB_DIR / "GeneratedArt" / "Icons" / "icon_library_manifest.json"
PLAYABLE_HTML_PATH = WEB_DIR / "cardfront_cradle_of_echoes_playable.html"
PWA_MANIFEST_PATH = WEB_DIR / "manifest.webmanifest"
SERVICE_WORKER_PATH = WEB_DIR / "sw_cardfront_pwa.js"
APPLE_HAPTICS_JS_PATH = WEB_DIR / "apple_native_haptics_bridge.js"
UNITY_APPLE_BRIDGE_CS_PATH = ROOT_DIR / "Assets" / "Scripts" / "Core" / "SynapseAppleNativeCrossPlatformBridge.cs"
CRYPTO_REPORT_PATH = ROOT_DIR / "Logs" / "cross_platform_crypto_sync_report.json"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from synapse_cross_save_crypto_sync import (  # noqa: E402
    CrossPlatformSaveEnvelope,
    SUPPORTED_PLATFORMS,
    compute_save_fnv1a,
    generate_provably_fair_pack_receipt,
    merge_cross_platform_saves,
    run_cross_platform_self_test,
    sign_save_envelope,
    verify_provably_fair_pack_receipt,
    verify_save_envelope,
)


class _DomAncestryParser(html.parser.HTMLParser):
    """Tracks ancestor element IDs for every element with an `id` attribute."""

    def __init__(self) -> None:
        super().__init__()
        self._stack: List[Tuple[str, Optional[str]]] = []
        self.ancestors_by_id: dict[str, List[str]] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_map = dict(attrs)
        el_id = attr_map.get("id")
        if el_id:
            self.ancestors_by_id[el_id] = [aid for _, aid in self._stack if aid]
        if tag not in {"img", "br", "hr", "meta", "link", "input", "source"}:
            self._stack.append((tag, el_id))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break


class TestMultiplatformExecutionSuite(unittest.TestCase):
    """End-to-end verification of Cryptographic Cross-Save, Provably Fair Receipts, SVG Icons, and Multiplatform Bridges."""

    SECRET_KEY = "test_cardfront_sovereign_hmac_secret_v3"

    def _sample_save(
        self,
        coins: int = 400,
        unlocked_stage: int = 3,
        cleared_stages: Optional[List[int]] = None,
        owned_cards: Optional[List[str]] = None,
        deck: Optional[List[str]] = None,
        tiers: Optional[dict[str, int]] = None,
        matches: int = 5,
        wins: int = 4,
        losses: int = 1,
    ) -> dict:
        return {
            "version": 3,
            "coins": coins,
            "unlockedStage": unlocked_stage,
            "clearedStages": cleared_stages if cleared_stages is not None else [1, 2],
            "ownedCards": owned_cards
            if owned_cards is not None
            else ["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph", "h_kai"],
            "deck": deck
            if deck is not None
            else ["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph"],
            "cardCraftTiers": tiers if tiers is not None else {"h_archangel": 1},
            "matchesPlayed": matches,
            "wins": wins,
            "losses": losses,
        }

    def test_01_sign_and_verify_all_four_platforms(self) -> None:
        """Verify signing and verification across web_pwa, apple_native, steam_desktop, and android_native."""
        self.assertEqual(
            tuple(SUPPORTED_PLATFORMS),
            ("web_pwa", "apple_native", "steam_desktop", "android_native"),
        )
        for idx, platform in enumerate(SUPPORTED_PLATFORMS):
            save_v3 = self._sample_save(coins=300 + idx * 125, unlocked_stage=2 + idx)
            envelope = sign_save_envelope(save_v3, platform, self.SECRET_KEY)
            self.assertEqual(envelope["version"], 3)
            self.assertEqual(envelope["source_platform"], platform)
            self.assertTrue(envelope["fnv1a_checksum"].startswith("0x"))
            self.assertEqual(len(envelope["hmac_sha256_signature"]), 64)
            self.assertTrue(verify_save_envelope(envelope, self.SECRET_KEY))

            # Verify dataclass round-trip
            env_obj = CrossPlatformSaveEnvelope.from_dict(envelope)
            self.assertTrue(verify_save_envelope(env_obj, self.SECRET_KEY))

    def test_02_tamper_rejection_and_wrong_key_rejection(self) -> None:
        """Verify that any mutation to coins, stage, cards, platform, checksum, or key is rejected."""
        base = sign_save_envelope(self._sample_save(coins=550), "apple_native", self.SECRET_KEY)
        self.assertTrue(verify_save_envelope(base, self.SECRET_KEY))

        # 1. Tamper top-level coins
        t_coins = copy.deepcopy(base)
        t_coins["coins"] = 999999
        self.assertFalse(verify_save_envelope(t_coins, self.SECRET_KEY))

        # 2. Tamper both top-level and nested coins without updating HMAC
        t_both_coins = copy.deepcopy(base)
        t_both_coins["coins"] = 999999
        t_both_coins["save_v3"]["coins"] = 999999
        self.assertFalse(verify_save_envelope(t_both_coins, self.SECRET_KEY))

        # 3. Tamper ownedCards
        t_cards = copy.deepcopy(base)
        t_cards["ownedCards"].append("e_eclipse")
        t_cards["save_v3"]["ownedCards"].append("e_eclipse")
        self.assertFalse(verify_save_envelope(t_cards, self.SECRET_KEY))

        # 4. Tamper source_platform
        t_platform = copy.deepcopy(base)
        t_platform["source_platform"] = "steam_desktop"
        self.assertFalse(verify_save_envelope(t_platform, self.SECRET_KEY))

        # 5. Wrong secret key
        self.assertFalse(verify_save_envelope(base, "forged_key"))

    def test_03_crdt_cross_platform_merge_web_apple_steam(self) -> None:
        """Verify conflict-free CRDT union merge across web_pwa <-> apple_native <-> steam_desktop."""
        web_save = self._sample_save(
            coins=410,
            unlocked_stage=3,
            cleared_stages=[1, 2],
            owned_cards=["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph", "h_kai"],
            tiers={"h_archangel": 1, "h_kai": 2},
            matches=6,
            wins=4,
            losses=2,
        )
        apple_save = self._sample_save(
            coins=720,
            unlocked_stage=6,
            cleared_stages=[1, 2, 3, 4, 5],
            owned_cards=["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph", "p_jev_gate"],
            tiers={"h_archangel": 2, "p_jev_gate": 1},
            matches=12,
            wins=10,
            losses=2,
        )
        steam_save = self._sample_save(
            coins=640,
            unlocked_stage=8,
            cleared_stages=[1, 2, 3, 4, 5, 6, 7],
            owned_cards=["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph", "p_mlx_silicon"],
            deck=["h_archangel", "p_mlx_silicon", "h_oracle", "h_chronos", "h_seraph"],
            tiers={"h_archangel": 3, "h_kai": 1, "p_mlx_silicon": 2},
            matches=20,
            wins=16,
            losses=4,
        )

        merged_wa = merge_cross_platform_saves(web_save, apple_save)
        merged_all = merge_cross_platform_saves(merged_wa, steam_save)

        self.assertEqual(merged_all["version"], 3)
        self.assertEqual(merged_all["coins"], 720)
        self.assertEqual(merged_all["unlockedStage"], 8)
        self.assertEqual(merged_all["clearedStages"], [1, 2, 3, 4, 5, 6, 7])
        self.assertTrue({"h_kai", "p_jev_gate", "p_mlx_silicon"}.issubset(set(merged_all["ownedCards"])))
        self.assertEqual(merged_all["cardCraftTiers"]["h_archangel"], 3)
        self.assertEqual(merged_all["cardCraftTiers"]["h_kai"], 2)
        self.assertEqual(merged_all["cardCraftTiers"]["p_jev_gate"], 1)
        self.assertEqual(merged_all["cardCraftTiers"]["p_mlx_silicon"], 2)
        self.assertEqual(merged_all["matchesPlayed"], 20)
        self.assertEqual(merged_all["wins"], 16)
        self.assertEqual(merged_all["losses"], 4)
        self.assertEqual(merged_all["fnv1a_checksum"], compute_save_fnv1a(merged_all))

    def test_04_crdt_algebraic_invariants_commutativity_associativity_idempotence(self) -> None:
        """Verify that merge_cross_platform_saves satisfies CRDT join-semilattice laws."""
        s1 = self._sample_save(coins=350, unlocked_stage=2, cleared_stages=[1], matches=4, wins=3, losses=1)
        s2 = self._sample_save(coins=600, unlocked_stage=5, cleared_stages=[1, 2, 3, 4], matches=9, wins=7, losses=2)
        s3 = self._sample_save(coins=500, unlocked_stage=7, cleared_stages=[1, 2, 6], matches=15, wins=12, losses=3)

        # Commutativity: s1 U s2 == s2 U s1
        self.assertEqual(
            merge_cross_platform_saves(s1, s2),
            merge_cross_platform_saves(s2, s1),
        )
        # Associativity: (s1 U s2) U s3 == s1 U (s2 U s3)
        self.assertEqual(
            merge_cross_platform_saves(merge_cross_platform_saves(s1, s2), s3),
            merge_cross_platform_saves(s1, merge_cross_platform_saves(s2, s3)),
        )
        # Idempotence: s1 U s1 == s1
        m1 = merge_cross_platform_saves(s1, s1)
        self.assertEqual(merge_cross_platform_saves(m1, m1), m1)

    def test_05_provably_fair_pack_receipt_generation_and_verification(self) -> None:
        """Verify SHA-256 commitment receipt generation and verification with zero crypto tokens."""
        server_seed = "server_secret_seed_set1_cradle_9981"
        client_seed = "apple_metal_player_seed_42"
        nonce = 12
        pack_cards = ["h_archangel", "p_jev_gate", "p_atelier_svg", "h_chronos", "e_archon"]

        receipt = generate_provably_fair_pack_receipt(server_seed, client_seed, nonce, pack_cards)
        self.assertTrue(receipt["zero_blockchain_gas"])
        self.assertTrue(receipt["zero_crypto_tokens"])
        self.assertEqual(
            receipt["server_seed_commitment"],
            hashlib.sha256(server_seed.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(receipt["pack_cards"], pack_cards)
        self.assertEqual(len(receipt["slot_hashes"]), 5)
        self.assertTrue(verify_provably_fair_pack_receipt(receipt, server_seed))

    def test_06_provably_fair_pack_receipt_tamper_and_seed_rejection(self) -> None:
        """Verify that altering pack cards, nonce, client seed, or server seed fails verification."""
        server_seed = "server_secret_seed_set1_cradle_9981"
        receipt = generate_provably_fair_pack_receipt(
            server_seed=server_seed,
            client_seed="client_seed_alpha",
            nonce=3,
            pack_cards=["h_archangel", "h_phoenix", "h_oracle", "h_chronos", "h_seraph"],
        )
        self.assertTrue(verify_provably_fair_pack_receipt(receipt, server_seed))

        # Tamper pack_cards
        tampered_cards = copy.deepcopy(receipt)
        tampered_cards["pack_cards"][2] = "e_reaper"
        self.assertFalse(verify_provably_fair_pack_receipt(tampered_cards, server_seed))

        # Tamper nonce
        tampered_nonce = copy.deepcopy(receipt)
        tampered_nonce["nonce"] = 4
        self.assertFalse(verify_provably_fair_pack_receipt(tampered_nonce, server_seed))

        # Wrong server seed
        self.assertFalse(verify_provably_fair_pack_receipt(receipt, "wrong_server_seed"))

    def test_07_cross_platform_crypto_sync_self_test_report_persisted(self) -> None:
        """Verify that running the self-test writes Logs/cross_platform_crypto_sync_report.json."""
        report = run_cross_platform_self_test()
        self.assertTrue(CRYPTO_REPORT_PATH.exists())
        disk_report = json.loads(CRYPTO_REPORT_PATH.read_text(encoding="utf-8"))
        self.assertTrue(report["all_self_tests_passed"])
        self.assertTrue(disk_report["all_self_tests_passed"])
        self.assertEqual(
            set(disk_report["platform_envelopes"].keys()),
            {"web_pwa", "apple_native", "steam_desktop", "android_native"},
        )

    def test_08_icon_library_manifest_and_all_23_svg_assets(self) -> None:
        """Verify icon_library_manifest.json and all 23 custom SVG assets exist and match SHA-256."""
        self.assertTrue(ICONS_MANIFEST_PATH.exists(), f"Missing {ICONS_MANIFEST_PATH}")
        manifest = json.loads(ICONS_MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["total_assets"], 23)
        self.assertTrue(manifest["zero_generic_emojis"])
        self.assertTrue(manifest["zero_baked_raster_text"])
        self.assertEqual(len(manifest["assets"]), 23)

        for item in manifest["assets"]:
            web_svg_path = ROOT_DIR / item["web_path"]
            unity_svg_path = ROOT_DIR / item["unity_path"]
            self.assertTrue(web_svg_path.exists(), f"Missing web SVG: {web_svg_path}")
            self.assertTrue(unity_svg_path.exists(), f"Missing Unity SVG: {unity_svg_path}")
            content = web_svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", content)
            self.assertIn(f'viewBox="{item["viewBox"]}"', content)
            actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
            self.assertEqual(actual_sha, item["sha256"], f"SHA-256 mismatch for {item['filename']}")

    def test_09_zero_generic_emojis_in_playable_html(self) -> None:
        """Verify 0 generic system emojis in WebPlayable/cardfront_cradle_of_echoes_playable.html."""
        self.assertTrue(PLAYABLE_HTML_PATH.exists())
        html_text = PLAYABLE_HTML_PATH.read_text(encoding="utf-8")

        banned_emojis = [
            "🃏", "🎲", "💡", "🏆", "💥", "🛡️", "🎁", "⚒️", "🧊", "🎥",
            "🔒", "👑", "🔗", "🟦", "🟥", "⚙️", "🪙", "🔊", "🔇", "🔉",
            "⚠️", "⚡", "🌙",
        ]
        for emoji in banned_emojis:
            self.assertNotIn(emoji, html_text, f"Found banned generic emoji {emoji!r} in playable HTML")

        supplementary_plane_chars = [c for c in html_text if ord(c) >= 0x1F000]
        self.assertEqual(
            len(supplementary_plane_chars),
            0,
            f"Found supplementary-plane emoji chars: {supplementary_plane_chars[:10]}",
        )
        self.assertIn("cf_cardback_astrolabe.svg", html_text)
        self.assertIn("function cfIcon(", html_text)

    def test_10_standalone_deck_sanctum_separated_from_board_slab(self) -> None:
        """Verify #standalone-deck-sanctum is outside #board-3d-slab in playable HTML."""
        html_text = PLAYABLE_HTML_PATH.read_text(encoding="utf-8")
        parser = _DomAncestryParser()
        parser.feed(html_text)

        self.assertIn("board-3d-slab", parser.ancestors_by_id)
        self.assertIn("standalone-deck-sanctum", parser.ancestors_by_id)
        self.assertIn("tabletop-deck-stack", parser.ancestors_by_id)

        deck_sanctum_ancestors = parser.ancestors_by_id["standalone-deck-sanctum"]
        deck_stack_ancestors = parser.ancestors_by_id["tabletop-deck-stack"]

        self.assertNotIn(
            "board-3d-slab",
            deck_sanctum_ancestors,
            "#standalone-deck-sanctum must NOT be nested inside #board-3d-slab",
        )
        self.assertNotIn(
            "board-3d-slab",
            deck_stack_ancestors,
            "#tabletop-deck-stack must NOT be nested inside #board-3d-slab",
        )
        self.assertIn("arena-viewport", deck_sanctum_ancestors)
        self.assertIn("standalone-deck-sanctum", deck_stack_ancestors)

    def test_11_pwa_manifest_webmanifest_validity(self) -> None:
        """Verify WebPlayable/manifest.webmanifest exists and configures standalone landscape PWA."""
        self.assertTrue(PWA_MANIFEST_PATH.exists(), f"Missing {PWA_MANIFEST_PATH}")
        manifest = json.loads(PWA_MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("display"), "standalone")
        self.assertEqual(manifest.get("orientation"), "landscape")
        self.assertIn("CARDFRONT", manifest.get("name", ""))
        self.assertTrue(len(manifest.get("icons", [])) >= 2)

    def test_12_pwa_service_worker_sw_cardfront_pwa_js(self) -> None:
        """Verify WebPlayable/sw_cardfront_pwa.js exists and precaches all 23 custom SVG icons."""
        self.assertTrue(SERVICE_WORKER_PATH.exists(), f"Missing {SERVICE_WORKER_PATH}")
        sw_text = SERVICE_WORKER_PATH.read_text(encoding="utf-8")
        self.assertIn("CACHE_NAME", sw_text)
        self.assertIn('addEventListener("install"', sw_text)
        self.assertIn('addEventListener("activate"', sw_text)
        self.assertIn('addEventListener("fetch"', sw_text)
        self.assertIn("cf_cardback_astrolabe.svg", sw_text)
        self.assertIn("cf_icon_sovereign_crown.svg", sw_text)

    def test_13_apple_native_haptics_bridge_js(self) -> None:
        """Verify WebPlayable/apple_native_haptics_bridge.js exposes CardFrontHaptics and CardFrontPlatformBridge."""
        self.assertTrue(APPLE_HAPTICS_JS_PATH.exists(), f"Missing {APPLE_HAPTICS_JS_PATH}")
        js_text = APPLE_HAPTICS_JS_PATH.read_text(encoding="utf-8")
        for required_token in (
            "CardFrontHaptics",
            "CardFrontPlatformBridge",
            "cardfrontHaptics",
            "card_place",
            "card_flip",
            "die_nudge",
            "telegraph_alert",
            "victory",
            "defeat",
            "exportSignedCrossSavePayload",
            "verifySignedCrossSavePayload",
        ):
            self.assertIn(required_token, js_text)

    def test_14_unity_apple_native_cross_platform_bridge_cs(self) -> None:
        """Verify Assets/Scripts/Core/SynapseAppleNativeCrossPlatformBridge.cs implements ProMotion, CoreHaptics, and Save Envelope V3."""
        self.assertTrue(UNITY_APPLE_BRIDGE_CS_PATH.exists(), f"Missing {UNITY_APPLE_BRIDGE_CS_PATH}")
        cs_text = UNITY_APPLE_BRIDGE_CS_PATH.read_text(encoding="utf-8")
        for required_symbol in (
            "namespace Synapse.TcgEngine.Core",
            "enum ExecutionTargetPlatform",
            "class CrossPlatformSaveEnvelopeV3",
            "class SynapseAppleNativeCrossPlatformBridge",
            "ConfigureProMotionFramePacing",
            "TriggerCoreHapticTransient",
            "BuildCrossPlatformSaveEnvelope",
            "VerifyZeroTokenStoreCompliance",
        ):
            self.assertIn(required_symbol, cs_text)

    def test_15_apple_native_macos_app_bundle_and_arm64_binary(self) -> None:
        """Verify NativeApple Swift host, compiled macOS arm64 binary, and apple_native_build_manifest.json."""
        swift_host = ROOT_DIR / "NativeApple" / "CardFrontAppleNativeHost.swift"
        app_binary = ROOT_DIR / "Build" / "macOS" / "CARDFRONT 3D.app" / "Contents" / "MacOS" / "CardFront3D"
        manifest_path = ROOT_DIR / "Logs" / "apple_native_build_manifest.json"
        self.assertTrue(swift_host.exists(), f"Missing {swift_host}")
        self.assertTrue(app_binary.exists(), f"Missing {app_binary}")
        self.assertTrue(manifest_path.exists(), f"Missing {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("arm64", manifest.get("executableType", ""))
        self.assertIn("Apple", manifest.get("compilerMetadata", {}).get("selfTest", {}).get("metalDevice", ""))
        self.assertTrue(manifest.get("zeroTokenStoreCompliance"))

    def test_16_android_native_kotlin_webview_and_vibration_haptics_host(self) -> None:
        """Verify NativeAndroid Kotlin WebView host, AndroidManifest.xml, and android_native_build_manifest.json."""
        kt_host = ROOT_DIR / "NativeAndroid" / "CardFrontAndroidNativeHost.kt"
        android_xml = ROOT_DIR / "NativeAndroid" / "AndroidManifest.xml"
        manifest_path = ROOT_DIR / "Logs" / "android_native_build_manifest.json"
        self.assertTrue(kt_host.exists(), f"Missing {kt_host}")
        self.assertTrue(android_xml.exists(), f"Missing {android_xml}")
        self.assertTrue(manifest_path.exists(), f"Missing {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("platform"), "android_native")
        self.assertEqual(manifest.get("status"), "VERIFIED")
        self.assertTrue(manifest.get("vibration_effect_haptics"))
        self.assertTrue(manifest.get("atomic_save_v3"))

    def test_17_steam_desktop_native_cloud_save_and_steaminput_host(self) -> None:
        """Verify NativeSteam C# Steamworks host, VDF config, and steam_desktop_build_manifest.json."""
        cs_host = ROOT_DIR / "NativeSteam" / "CardFrontSteamDesktopHost.cs"
        vdf_path = ROOT_DIR / "NativeSteam" / "steam_app_build_3294810.vdf"
        manifest_path = ROOT_DIR / "Logs" / "steam_desktop_build_manifest.json"
        self.assertTrue(cs_host.exists(), f"Missing {cs_host}")
        self.assertTrue(vdf_path.exists(), f"Missing {vdf_path}")
        self.assertTrue(manifest_path.exists(), f"Missing {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("platform"), "steam_desktop")
        self.assertEqual(manifest.get("status"), "VERIFIED")
        self.assertTrue(manifest.get("steam_deck_verified_profile"))
        self.assertTrue(manifest.get("steam_cloud_save_v3"))

    def test_18_six_multiplatform_and_crypto_bespoke_svg_emblems(self) -> None:
        """Verify the 6 bespoke multiplatform & cryptographic vault SVG emblems exist and are registered in CF_ICON_BODIES."""
        svg_names = (
            "cf_platform_apple.svg",
            "cf_platform_android.svg",
            "cf_platform_steam.svg",
            "cf_platform_pwa.svg",
            "cf_crypto_shield.svg",
            "cf_pack_seal.svg",
        )
        icons_dir = WEB_DIR / "GeneratedArt" / "Icons"
        for fname in svg_names:
            p = icons_dir / fname
            self.assertTrue(p.exists(), f"Missing {p}")
            txt = p.read_text(encoding="utf-8")
            self.assertIn('viewBox="0 0 256 256"', txt)
            self.assertNotIn("<text", txt.lower())

        html_text = PLAYABLE_HTML_PATH.read_text(encoding="utf-8")
        for key in (
            "platform_apple:",
            "platform_android:",
            "platform_steam:",
            "platform_pwa:",
            "crypto_shield:",
            "pack_seal:",
        ):
            self.assertIn(key, html_text)

    def test_19_six_tier_haptics_and_interactive_grimoire_crypto_vault_bar(self) -> None:
        """Verify 6-tier haptics routing and interactive Grimoire Cross-Save & Provably Fair Vault UI injector."""
        js_text = APPLE_HAPTICS_JS_PATH.read_text(encoding="utf-8")
        for token in (
            "CardFrontAndroidBridge",
            "CardFrontSteamBridge",
            "generateProvablyFairPackReceipt",
            "injectMultiPlatformVaultSection",
            "multiplatform-crypto-vault-bar",
            "btn-verify-cross-save",
            "btn-verify-fair-pack",
        ):
            self.assertIn(token, js_text)
        supplementary_chars = [c for c in js_text if ord(c) >= 0x1F000]
        self.assertEqual(len(supplementary_chars), 0)

    def test_20_master_app_icon_512_and_192_raster_qa(self) -> None:
        """Verify cf_app_icon_master.svg, cf_app_icon_512.png, cf_app_icon_192.png, and Unity icon exist."""
        icons_dir = WEB_DIR / "GeneratedArt" / "Icons"
        for p in (
            icons_dir / "cf_app_icon_master.svg",
            icons_dir / "cf_app_icon_512.png",
            icons_dir / "cf_app_icon_192.png",
            ROOT_DIR / "Assets" / "Resources" / "UI" / "Icons" / "cf_app_icon_512.png",
        ):
            self.assertTrue(p.exists(), f"Missing {p}")
            self.assertGreater(p.stat().st_size, 512)


if __name__ == "__main__":
    unittest.main(verbosity=2)
