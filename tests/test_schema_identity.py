"""Schema identity: published ABIZ 1.0 and proposed ABIZ 1.1 are selected separately."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import infer_revision, validate_record, validate_record_v1_0  # noqa: E402

PUBLISHED = "3bbaa7b"
V1_ID = "https://abizrecord.org/schema/abiz-business-record-v1.schema.json"
V11_ID = "https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json"


def run_validator(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py"), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class SchemaIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_10 = json.loads((ROOT / "schemas" / "abiz-business-record-v1.schema.json").read_text())
        cls.schema_11 = json.loads((ROOT / "schemas" / "abiz-business-record-v1.1.schema.json").read_text())
        cls.record_10 = json.loads((ROOT / "examples" / "abiz-1.0" / "registered-us.json").read_text())
        cls.record_11 = json.loads((ROOT / "examples" / "registered-us.json").read_text())
        cls.dns_10 = "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co"

    def test_published_1_0_constraints_match_the_publication(self):
        blob = subprocess.run(
            ["git", "show", f"{PUBLISHED}:schemas/abiz-business-record-v1.schema.json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        published = json.loads(blob)
        original_description = published["description"]
        current = json.loads(json.dumps(self.schema_10))
        for document in (published, current):
            document.pop("title", None)
            document.pop("description", None)
        self.assertEqual(current, published)
        self.assertEqual(self.schema_10["$id"], V1_ID)
        self.assertNotEqual(self.schema_10["description"], original_description)
        self.assertIn("1.1 public-review", original_description)

    def test_revisions_have_distinct_ids(self):
        self.assertEqual(self.schema_11["$id"], V11_ID)
        self.assertNotEqual(self.schema_10["$id"], self.schema_11["$id"])
        well_known = json.loads((ROOT / "schemas" / "abiz-well-known-v1.1.schema.json").read_text())
        self.assertEqual(well_known["$id"], "https://abizrecord.org/schema/abiz-well-known-v1.1.schema.json")
        self.assertFalse((ROOT / "schemas" / "abiz-well-known-v1.schema.json").exists())

    def test_revision_file_selects_the_contract(self):
        self.assertEqual(infer_revision(ROOT / "examples" / "abiz-1.0" / "registered-us.json"), "1.0")
        self.assertEqual(infer_revision(ROOT / "examples" / "registered-us.json"), "1.1")
        self.assertEqual((ROOT / "examples" / "REVISION").read_text(encoding="utf-8").strip(), "1.1")

    def test_1_0_example_passes_only_the_1_0_contract(self):
        self.assertEqual(
            validate_record_v1_0(self.record_10, self.schema_10, "harbourbikes.example", self.dns_10),
            [],
        )
        errors = validate_record(self.record_10, self.schema_11)
        self.assertTrue(errors)
        self.assertFalse(any("did not verify" in error or "invalid signature" in error for error in errors))
        joined = " ".join(errors)
        self.assertTrue("required" in joined or "Additional properties" in joined)

    def test_1_1_example_fails_the_1_0_contract_as_a_schema_mismatch(self):
        errors = validate_record_v1_0(self.record_11, self.schema_10)
        self.assertTrue(errors)
        self.assertFalse(any("did not verify" in error or "invalid signature" in error for error in errors))

    def test_cli_reports_revision_separately_from_signatures(self):
        published = run_validator(str(ROOT / "examples" / "abiz-1.0" / "registered-us.json"))
        self.assertEqual(published.returncode, 0, published.stderr)
        self.assertIn("ABIZ 1.0", published.stdout)
        self.assertIn("no record signature", published.stdout)
        self.assertNotIn("did not verify", published.stdout)

        mismatch = run_validator(
            str(ROOT / "examples" / "abiz-1.0" / "registered-us.json"),
            "--revision",
            "1.1",
        )
        self.assertEqual(mismatch.returncode, 1)
        self.assertNotIn("did not verify", mismatch.stderr)
        self.assertNotIn("unsupported schema revision", mismatch.stderr)

        unsupported = run_validator(
            str(ROOT / "examples" / "registered-us.json"),
            "--revision",
            "1.2",
        )
        self.assertEqual(unsupported.returncode, 2)
        self.assertIn("unsupported schema revision", unsupported.stderr)
        self.assertIn("not an invalid signature", unsupported.stderr)
        self.assertNotIn("did not verify", unsupported.stderr)

        well_known = run_validator(
            str(ROOT / "examples" / "well-known-registered-us.json"),
            "--revision",
            "1.0",
        )
        self.assertEqual(well_known.returncode, 1)
        self.assertIn("not an invalid signature", well_known.stderr)
        self.assertIn("1.1 proposal", well_known.stderr)

        tampered = json.loads((ROOT / "examples" / "registered-us.json").read_text())
        tampered["signature"] = "A" * 86 + "=="
        target = ROOT / "examples" / "abiz-1.0" / "not-a-fixture.json"
        # Keep the tampered record outside the 1.0 directory so revision inference stays 1.1.
        outside = ROOT / "examples" / "tampered-signature.json"
        outside.write_text(json.dumps(tampered), encoding="utf-8")
        try:
            signed = run_validator(str(outside))
        finally:
            outside.unlink()
        self.assertEqual(signed.returncode, 1, signed.stderr)
        self.assertIn("did not verify", signed.stderr)
        self.assertNotIn("unsupported schema revision", signed.stderr)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
