#!/usr/bin/env python3
"""
Deterministic Verification Suite for OGDEOP CDM v5.4
(Observational Game Development & Engine Outcomes Partnership Common Data Model)
"""

import json
import sqlite3
import unittest
from decimal import Decimal
from pathlib import Path

from Backend.ogdeop_cdm_engine import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_SFT_JSONL_PATH,
    DEFAULT_SQLITE_PATH,
    build_ogdeop_cdm_database,
    translate_source_code_to_standard_concept,
)


class TestOgdeopCdmV54(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = build_ogdeop_cdm_database()

    def test_01_all_21_omop_isomorphic_tables_populated(self) -> None:
        self.assertEqual(self.manifest["status"], "PASS_OGDEOP_CDM_V54_BUILT_AND_VERIFIED")
        self.assertEqual(self.manifest["total_tables"], 21)
        counts = self.manifest["table_row_counts"]
        for table_name, row_count in counts.items():
            self.assertGreater(row_count, 0, f"Table {table_name} must be non-empty")

    def test_02_cross_engine_source_to_standard_concept_harmonization(self) -> None:
        # Unity UGUI, Unreal UMG, and Godot Control overlap codes MUST all map to Standard Concept 3001
        u_map = translate_source_code_to_standard_concept("UNITY:ERR:RECT_OVERLAP_07")
        ue_map = translate_source_code_to_standard_concept("UE5:WARN:UMG_SLOT_CLIP")
        gd_map = translate_source_code_to_standard_concept("GODOT:WARN:CONTROL_RECT_COLLIDE")

        for m in (u_map, ue_map, gd_map):
            self.assertTrue(m["ok"])
            self.assertEqual(m["target_concept_id"], 3001)
            self.assertEqual(m["target_concept_code"], "ICD:UI_BBOX_COLLISION")
            self.assertEqual(m["standard_concept"], "S")

        # Perforce binary+l lock stall and Git LFS lock conflict MUST both map to Standard Concept 3003
        p4_map = translate_source_code_to_standard_concept("P4:LOCK:EXCLUSIVE_BINARY_WAIT")
        git_map = translate_source_code_to_standard_concept("GIT:LFS:LOCK_CONFLICT")
        self.assertEqual(p4_map["target_concept_id"], 3003)
        self.assertEqual(git_map["target_concept_id"], 3003)

    def test_03_cross_studio_network_studies_reproducibility(self) -> None:
        studies = self.manifest["standardized_network_studies"]
        s1 = studies["study_1_cross_engine_ui_collision_eradication"]
        self.assertEqual(len(s1), 3)  # CARDFRONT (Unity/Rust), Project Aegis (UE5), Echoes (Godot)
        for row in s1:
            self.assertGreater(row["pre_intervention_collisions"], 0.0)
            self.assertEqual(row["post_intervention_collisions"], 0.0)
            self.assertEqual(row["relative_risk_reduction_pct"], 100.0)

        s3 = studies["study_3_cardfront_70b_soup_distillation_and_balance"]
        self.assertGreaterEqual(len(s3), 8)
        self.assertTrue(all(r["pass_gate"] for r in s3))

    def test_04_penny_exact_decimal_finops_costs_and_sft_export(self) -> None:
        conn = sqlite3.connect(str(DEFAULT_SQLITE_PATH))
        cur = conn.cursor()
        cur.execute("SELECT total_cost_usd_decimal, cloud_offload_savings_usd_decimal FROM compute_and_studio_cost")
        for cost_str, savings_str in cur.fetchall():
            self.assertEqual(str(Decimal(cost_str)), cost_str)
            self.assertEqual(str(Decimal(savings_str)), savings_str)
        conn.close()

        self.assertTrue(DEFAULT_SFT_JSONL_PATH.exists())
        lines = DEFAULT_SFT_JSONL_PATH.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 14)


if __name__ == "__main__":
    unittest.main()
