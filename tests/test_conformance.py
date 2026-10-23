import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import validate_record, dns_tags

SCHEMA = json.loads((ROOT / "schemas" / "abiz-business-record-v1.schema.json").read_text())
REG = json.loads((ROOT / "examples" / "registered-us.json").read_text())
UNREG = json.loads((ROOT / "examples" / "unregistered-us.json").read_text())


class ABIZConformanceTests(unittest.TestCase):
    def test_registered_business_passes(self):
        self.assertEqual(validate_record(REG, SCHEMA), [])
        self.assertEqual(validate_record(REG, SCHEMA,
                         "harbourbikes.example",
                         "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co"), [])

    def test_unregistered_business_passes_without_k_or_mcp(self):
        self.assertEqual(validate_record(UNREG, SCHEMA,
                         "marketstand.example",
                         "v=abiz1;h=market-stand-repairs-portland.biz.to.co"), [])

    def test_invalid_business_record_fails_schema(self):
        bad = json.loads((ROOT / "examples" / "invalid-business-record.json").read_text())
        self.assertTrue(validate_record(bad, SCHEMA))

    def test_cross_record_mismatch_fails(self):
        self.assertTrue(validate_record(REG, SCHEMA, "elsewhere.example",
                        "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co"))
        self.assertTrue(validate_record(REG, SCHEMA, "harbourbikes.example",
                        "v=abiz1;k=us-OR123456;h=wrong.example"))

    def test_bad_registry_key_and_insecure_url_fail(self):
        bad = copy.deepcopy(REG)
        bad["business-key"] = "gb-OR123456"
        bad["website"] = "http://example.com"
        self.assertTrue(validate_record(bad, SCHEMA))

    def test_dns_duplicate_tag_fails(self):
        with self.assertRaises(ValueError):
            dns_tags("v=abiz1;h=good.example;h=bad.example")

    def test_dns_without_version_fails(self):
        with self.assertRaises(ValueError):
            dns_tags("h=good.example;v=abiz1")

    def test_unknown_top_level_property_fails(self):
        bad = copy.deepcopy(REG)
        bad["made-up-field"] = "value"
        self.assertTrue(validate_record(bad, SCHEMA))


if __name__ == "__main__":
    unittest.main()
