import base64
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import (
    compromised_key_rejects_time,
    decode_ed25519_public_key,
    dns_tags,
    retired_key_message,
    validate_record,
)

SCHEMA = json.loads((ROOT / "schemas" / "abiz-business-record-v1.schema.json").read_text())
REG = json.loads((ROOT / "examples" / "registered-us.json").read_text())
UNREG = json.loads((ROOT / "examples" / "unregistered-us.json").read_text())
# Throwaway public key from examples/dns-ed25519-p.txt. The private key was not committed.
P_MESSAGE = b"abiz1.1 p-key test"
P_SIGNATURE = (
    "K8z1ImVMyYZF7tGBnyaL4fhI3WAnCTo1EKHS77J+uLCet14Sbg629QmXc1e6rIjn"
    "3KtZdXgKNtuakuTLmruKAg=="
)


def example_dns() -> str:
    for line in (ROOT / "examples" / "dns-ed25519-p.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("v=abiz1;"):
            return line.strip()
    raise AssertionError("examples/dns-ed25519-p.txt has no assertion")


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

    def test_schema_description_matches_published_1_0(self):
        description = SCHEMA["description"]
        self.assertIn("ABIZ 1.0", description)
        self.assertNotIn("1.1 public-review", description)

    def test_p_key_valid_example(self):
        dns = example_dns()
        self.assertIn(dns.split("p=", 1)[1], (ROOT / "SPEC.md").read_text(encoding="utf-8"))
        tags = dns_tags(dns)
        self.assertEqual(len(tags["p"]), 44)
        self.assertTrue(tags["p"].endswith("="))
        key = decode_ed25519_public_key(tags["p"])
        self.assertEqual(len(key), 32)
        self.assertEqual(validate_record(
            REG, SCHEMA, "harbourbikes.example", dns, check_p_key_mode=True), [])
        # Default mode is unchanged: the same key is also a legal opaque token.
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", dns), [])

    def test_p_key_accepts_plus_and_slash(self):
        raw = bytes([255, 239]) + bytes(range(30))
        value = base64.b64encode(raw).decode("ascii")
        self.assertIn("+", value)
        self.assertIn("/", value)
        self.assertEqual(len(value), 44)
        self.assertEqual(decode_ed25519_public_key(value), raw)

    def test_p_key_malformed_base64(self):
        key = example_dns().split("p=", 1)[1]
        for bad in (
            key[:-1] + "-",          # base64url character
            key[:-1],                 # unpadded, 43 characters
            key + "=",                # extra padding
            "!!!!" + key[4:],         # alphabet
            key[:-2] + "-=",          # non-alphabet before padding
        ):
            with self.assertRaises(ValueError):
                decode_ed25519_public_key(bad)

    def test_p_key_wrong_length(self):
        short = base64.b64encode(b"\x11" * 31).decode("ascii")
        longer = base64.b64encode(b"\x22" * 33).decode("ascii")
        self.assertEqual(len(short), 44)
        self.assertEqual(len(longer), 44)
        for bad in (short, longer, base64.b64encode(b"\x33" * 32).decode("ascii")[:-1]):
            with self.assertRaises(ValueError):
                decode_ed25519_public_key(bad)
        dns = example_dns().split("p=", 1)[0] + "p=" + short
        errors = validate_record(
            REG, SCHEMA, "harbourbikes.example", dns, check_p_key_mode=True)
        self.assertTrue(errors)

    def test_dns_duplicate_p_tag_fails(self):
        key = example_dns().split("p=", 1)[1]
        with self.assertRaises(ValueError):
            dns_tags(f"v=abiz1;h=harbour-bike-repair.or.us.to.co;p={key};p={key}")

    def test_opaque_p_passes_unless_key_check_is_requested(self):
        token = "ab" * 16  # 32 hex characters, as used by some 1.0 handshakes
        dns = f"v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co;p={token}"
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", dns), [])
        errors = validate_record(
            REG, SCHEMA, "harbourbikes.example", dns, check_p_key_mode=True)
        self.assertTrue(any(e.startswith("p must be") for e in errors))

    def test_p_key_signature_round_trip(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("optional cryptography package is not installed")
        dns = example_dns()
        self.assertEqual(validate_record(
            REG, SCHEMA, "harbourbikes.example", dns,
            check_p_key_mode=True, p_message=P_MESSAGE, p_signature=P_SIGNATURE), [])
        errors = validate_record(
            REG, SCHEMA, "harbourbikes.example", dns,
            check_p_key_mode=True, p_message=b"different message", p_signature=P_SIGNATURE)
        self.assertTrue(any("did not verify" in e for e in errors))

    def test_cli_check_p_key_mode(self):
        dns = example_dns()
        base = [
            sys.executable, str(ROOT / "scripts" / "validate.py"),
            str(ROOT / "examples" / "registered-us.json"),
            "--domain", "harbourbikes.example",
            "--dns-value", dns,
        ]
        plain = subprocess.run(base, capture_output=True, text=True, check=False)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("offline DNS/document consistency", plain.stdout)
        self.assertNotIn("Ed25519", plain.stdout)

        checked = subprocess.run(base + ["--check-p-key"], capture_output=True, text=True, check=False)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("32-byte Ed25519 public key", checked.stdout)

        signed = subprocess.run(
            base + ["--check-p-key", "--p-message", P_MESSAGE.decode(), "--p-signature", P_SIGNATURE],
            capture_output=True, text=True, check=False)
        if "requires the optional cryptography package" in signed.stderr:
            self.assertNotEqual(signed.returncode, 0)
        else:
            self.assertEqual(signed.returncode, 0, signed.stderr)
            self.assertIn("signature matches p", signed.stdout)

        opaque = dns.rsplit("p=", 1)[0] + "p=" + ("ab" * 16)
        rejected = subprocess.run(
            base[:-1] + [opaque, "--check-p-key"],
            capture_output=True, text=True, check=False)
        self.assertEqual(rejected.returncode, 1)
        still_ok = subprocess.run(
            base[:-1] + [opaque], capture_output=True, text=True, check=False)
        self.assertEqual(still_ok.returncode, 0, still_ok.stderr)

    def _retired_record(self):
        return json.loads((ROOT / "examples" / "registered-us-retired-key.json").read_text(encoding="utf-8"))

    def _retired_dns(self):
        for line in (ROOT / "examples" / "dns-retired-keys.txt").read_text(encoding="utf-8").splitlines():
            if line.startswith("v=abiz1;"):
                return line.strip()
        raise AssertionError("examples/dns-retired-keys.txt has no assertion")

    def test_retired_key_entry_verifies(self):
        record = self._retired_record()
        dns = self._retired_dns()
        self.assertEqual(validate_record(record, SCHEMA), [])
        self.assertEqual(validate_record(
            record, SCHEMA, "harbourbikes.example", dns, check_p_key_mode=True), [])
        entry = record["retired-keys"][0]
        message = retired_key_message(record["domains"], entry)
        self.assertTrue(message.endswith(b"\n"))
        self.assertIn(b"domains=harbourbikes.example\n", message)
        self.assertNotIn(b"binding-signature", message)

    def test_retired_key_bad_signature_fails_key_check_only(self):
        record = self._retired_record()
        dns = self._retired_dns()
        record["retired-keys"][0]["binding-signature"] = P_SIGNATURE
        self.assertEqual(validate_record(record, SCHEMA), [])
        errors = validate_record(
            record, SCHEMA, "harbourbikes.example", dns, check_p_key_mode=True)
        self.assertTrue(any("did not verify" in error for error in errors), errors)

    def test_retired_key_malformed_public_key_fails_schema(self):
        record = self._retired_record()
        record["retired-keys"][0]["public-key"] = "not-a-key"
        self.assertTrue(validate_record(record, SCHEMA))
        record = self._retired_record()
        record["retired-keys"][0]["public-key"] = base64.b64encode(b"\x11" * 31).decode("ascii")
        self.assertTrue(validate_record(record, SCHEMA))

    def test_compromised_retired_key_time_rule(self):
        entry = {"reason": "compromised", "retired-at": "2026-10-01T00:00:00Z"}
        self.assertFalse(compromised_key_rejects_time(entry, "2026-10-01T00:00:00Z"))
        self.assertFalse(compromised_key_rejects_time(entry, "2026-09-30T23:59:59Z"))
        self.assertTrue(compromised_key_rejects_time(entry, "2026-10-01T00:00:01Z"))
        rotated = {"reason": "rotated", "retired-at": "2026-10-01T00:00:00Z"}
        self.assertFalse(compromised_key_rejects_time(rotated, "2027-01-01T00:00:00Z"))


if __name__ == "__main__":
    unittest.main()
