import base64
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from jsonschema import Draft202012Validator, FormatChecker
from validate import (
    canonical_business_key,
    check_public_key_matches_p,
    jcs_canonicalize,
    load_json_strict,
    sign_record,
    signing_input,
    verify_record_signature,
    decode_ed25519_public_key,
    normalise_registration_number,
    parse_business_key,
    dns_tags,
    is_abiz_assertion,
    resolve_sources,
    select_representation,
    validate_record,
    validate_well_known,
    well_known_tags,
)

SCHEMA = json.loads((ROOT / "schemas" / "abiz-business-record-v1.1.schema.json").read_text())
REG = json.loads((ROOT / "examples" / "registered-us.json").read_text())
UNIT = json.loads((ROOT / "examples" / "unit-us.json").read_text())
WK_REG = json.loads((ROOT / "examples" / "well-known-registered-us.json").read_text())
WK_UNREG = json.loads((ROOT / "examples" / "well-known-unregistered-us.json").read_text())
WK_SCHEMA = json.loads((ROOT / "schemas" / "abiz-well-known-v1.1.schema.json").read_text())
UNREG = json.loads((ROOT / "examples" / "unregistered-us.json").read_text())
# Throwaway public key from examples/dns-ed25519-p.txt. The private key was not committed.
P_MESSAGE = b"abiz1.1 p-key test"
P_SIGNATURE = (
    "IaZr5HsbImiYvB92BzVDbwsCmCnq59qwga3YPWghNoHNJ+Z9fhMwFGV3VD+c5kVOsdcv"
    "gFZIa+iillIxV21kBA=="
)
# Shape of $defs/retired_key. Not a record property; the signature is a placeholder.
RETIRED_KEY_ENTRY = {
    "public_key": "CtW5mtOK/a36noCey4n3kQDYbl498nnTnArU5MPs+gs=",
    "valid_from": "2025-01-01T00:00:00Z",
    "retired_at": "2026-10-01T00:00:00Z",
    "reason": "rotated",
    "binding_signature": P_SIGNATURE,
}


def example_dns() -> str:
    for line in (ROOT / "examples" / "dns-ed25519-p.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("v=abiz1;"):
            return line.strip()
    raise AssertionError("examples/dns-ed25519-p.txt has no assertion")


# ABIZ 1.1: p is REQUIRED (SPEC 3.2), so every valid assertion below carries the example key.
P = example_dns().split("p=", 1)[1]
# Key of the unregistered example (examples/well-known-unregistered-us.json).
MP = WK_UNREG["p"]

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    # TEST-ONLY key with a fixed, public seed, used to re-sign records that a test changes.
    # Never use it for a real record: anyone can sign with it.
    TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    TEST_P = sign_record({}, TEST_KEY)["public_key"]
except ImportError:  # pragma: no cover - cryptography is in requirements-dev.txt
    TEST_KEY = TEST_P = None


def resign(record: dict) -> dict:
    """Re-sign a changed record with the test-only key, so a test checks only what it changed."""
    return sign_record(record, TEST_KEY)


class ABIZConformanceTests(unittest.TestCase):
    def test_registered_business_passes(self):
        self.assertEqual(validate_record(REG, SCHEMA), [])
        self.assertEqual(validate_record(REG, SCHEMA,
                         "harbourbikes.example",
                         f"v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p={P}"), [])

    def test_unregistered_business_passes_without_k_or_mcp(self):
        self.assertEqual(validate_record(UNREG, SCHEMA,
                         "marketstand.example",
                         f"v=abiz1;h=market-stand-repairs-portland.biz.to.co;p={MP}"), [])

    def test_invalid_business_record_fails_schema(self):
        bad = json.loads((ROOT / "examples" / "invalid-business-record.json").read_text())
        self.assertTrue(validate_record(bad, SCHEMA))

    def test_cross_record_mismatch_fails(self):
        self.assertTrue(validate_record(REG, SCHEMA, "elsewhere.example",
                        f"v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p={P}"))
        self.assertTrue(validate_record(REG, SCHEMA, "harbourbikes.example",
                        f"v=abiz1;k=us-or-123456;h=wrong.example;p={P}"))

    def test_bad_registry_key_and_insecure_url_fail(self):
        bad = copy.deepcopy(REG)
        bad["business_key"] = "gb-123456"
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
        bad["made_up_field"] = "value"
        self.assertTrue(validate_record(bad, SCHEMA))

    def test_schema_descriptions_identify_each_published_revision(self):
        published = json.loads((ROOT / "schemas" / "abiz-business-record-v1.schema.json").read_text())
        description = published["description"]
        self.assertIn("published ABIZ 1.0", description)
        self.assertNotIn("1.1 public-review", description)
        self.assertEqual(published["$id"], "https://abizrecord.org/schema/abiz-business-record-v1.schema.json")
        self.assertIn("published ABIZ 1.1", SCHEMA["description"])
        self.assertNotIn("not a formal publication", SCHEMA["description"])
        self.assertNotIn("proposed", SCHEMA["title"].lower())
        self.assertEqual(SCHEMA["$id"], "https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json")

    def test_p_key_valid_example(self):
        dns = example_dns()
        self.assertIn(dns.split("p=", 1)[1], (ROOT / "SPEC.md").read_text(encoding="utf-8"))
        tags = dns_tags(dns)
        self.assertEqual(len(tags["p"]), 44)
        self.assertTrue(tags["p"].endswith("="))
        key = decode_ed25519_public_key(tags["p"])
        self.assertEqual(len(key), 32)
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", dns), [])

    def test_no_p_fails(self):
        # ABIZ 1.1: p is REQUIRED (SPEC 3.2, 3.3.1). These were valid under ABIZ 1.0.
        for dns in ("v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co",
                    "v=abiz1; h=harbour-bike-repair.or.us.to.co;",
                    "v=abiz1;h=harbour-bike-repair.or.us.to.co;x=1"):
            with self.subTest(dns=dns):
                with self.assertRaisesRegex(ValueError, "Missing p="):
                    dns_tags(dns)
                self.assertTrue(validate_record(REG, SCHEMA, "harbourbikes.example", dns))

    def test_p_key_accepts_plus_and_slash(self):
        raw = bytes([255, 239]) + bytes(range(30))
        value = base64.b64encode(raw).decode("ascii")
        self.assertIn("+", value)
        self.assertIn("/", value)
        self.assertEqual(len(value), 44)
        self.assertEqual(decode_ed25519_public_key(value), raw)
        self.assertEqual(dns_tags(f"v=abiz1;h=a.example;p={value}")["p"], value)

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
        self.assertTrue(validate_record(REG, SCHEMA, "harbourbikes.example", dns))

    def test_dns_duplicate_p_tag_fails(self):
        key = example_dns().split("p=", 1)[1]
        with self.assertRaises(ValueError):
            dns_tags(f"v=abiz1;h=harbour-bike-repair.or.us.to.co;p={key};p={key}")

    def _dns_with_p(self, value):
        return f"v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p={value}"

    def test_hex_token_p_fails(self):
        # 32 hex characters, the ABIZ 1.0 one-time handshake shape. Invalid from 1.1.
        token = "ede69a675ead36c690cc8689e1d3e21d"
        dns = self._dns_with_p(token)
        with self.assertRaises(ValueError):
            dns_tags(dns)
        errors = validate_record(REG, SCHEMA, "harbourbikes.example", dns)
        self.assertTrue(any(e.startswith("p (Ed25519 public key) must be") for e in errors), errors)
        # Spaced 1.0-style records with a hex token also fail, on p rather than whitespace.
        with self.assertRaises(ValueError):
            dns_tags(f"v=abiz1; h=harbour-bike-repair.or.us.to.co; p={token}")

    def test_base64url_p_fails(self):
        raw = bytes([255, 239]) + bytes(range(30))
        standard = base64.b64encode(raw).decode("ascii")
        padded_url = base64.urlsafe_b64encode(raw).decode("ascii")
        unpadded_url = padded_url.rstrip("=")
        self.assertNotEqual(standard, padded_url)
        self.assertEqual(len(unpadded_url), 43)
        for bad in (padded_url, unpadded_url, "ed25519:" + unpadded_url):
            with self.subTest(value=bad):
                self.assertTrue(validate_record(
                    REG, SCHEMA, "harbourbikes.example", self._dns_with_p(bad)))

    def test_missing_padding_p_fails(self):
        key = example_dns().split("p=", 1)[1]
        self.assertTrue(key.endswith("="))
        self.assertTrue(validate_record(
            REG, SCHEMA, "harbourbikes.example", self._dns_with_p(key[:-1])))

    def test_p_key_signature_round_trip(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("optional cryptography package is not installed")
        dns = example_dns()
        self.assertEqual(validate_record(
            REG, SCHEMA, "harbourbikes.example", dns,
            p_message=P_MESSAGE, p_signature=P_SIGNATURE), [])
        errors = validate_record(
            REG, SCHEMA, "harbourbikes.example", dns,
            p_message=b"different message", p_signature=P_SIGNATURE)
        self.assertTrue(any("did not verify" in e for e in errors))

    def test_cli_p_key_checked_by_default(self):
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

        retired_flag = subprocess.run(base + ["--check-p-key"], capture_output=True, text=True, check=False)
        self.assertEqual(retired_flag.returncode, 2)  # the opt-in flag no longer exists

        signed = subprocess.run(
            base + ["--p-message", P_MESSAGE.decode(), "--p-signature", P_SIGNATURE],
            capture_output=True, text=True, check=False)
        if "requires the optional cryptography package" in signed.stderr:
            self.assertNotEqual(signed.returncode, 0)
        else:
            self.assertEqual(signed.returncode, 0, signed.stderr)
            self.assertIn("signature matches p", signed.stdout)

        hex_token = dns.rsplit("p=", 1)[0] + "p=" + ("ab" * 16)
        rejected = subprocess.run(
            base[:-1] + [hex_token], capture_output=True, text=True, check=False)
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("Ed25519 public key", rejected.stderr)

    def test_top_level_retired_keys_fails(self):
        bad = copy.deepcopy(REG)
        bad["retired_keys"] = [RETIRED_KEY_ENTRY]
        errors = validate_record(bad, SCHEMA)
        self.assertTrue(any("retired_keys" in e for e in errors), errors)
        self.assertNotIn("retired_keys", SCHEMA["properties"])

    def test_nested_retired_key_definition_validates(self):
        nested = {"$ref": "#/$defs/retired_key", "$defs": SCHEMA["$defs"]}
        validator = Draft202012Validator(nested, format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors(RETIRED_KEY_ENTRY)), [])
        for change in (
            {"public_key": "not-a-key"},
            {"public_key": base64.b64encode(b"\x11" * 31).decode("ascii")},
            {"reason": "lost"},
            {"extra": "x"},
        ):
            with self.subTest(change=change):
                self.assertTrue(list(validator.iter_errors({**RETIRED_KEY_ENTRY, **change})))
        missing = dict(RETIRED_KEY_ENTRY)
        del missing["binding_signature"]
        self.assertTrue(list(validator.iter_errors(missing)))


class ABIZTagListWhitespaceTests(unittest.TestCase):
    """Published ABIZ 1.1 tag-list grammar, SPEC.md section 3.1.1."""

    HOST = "harbour-bike-repair.or.us.to.co"
    CANONICAL = {"v": "abiz1", "k": "us-or-123456", "h": HOST, "p": P}

    def assert_parses(self, value):
        self.assertEqual(dns_tags(value), self.CANONICAL, value)
        self.assertTrue(is_abiz_assertion(value), value)

    def test_canonical_1_0_form_still_parses(self):
        self.assert_parses(f"v=abiz1;k=us-or-123456;h={self.HOST};p={P}")

    def test_space_after_semicolon(self):
        self.assert_parses(f"v=abiz1; k=us-or-123456; h={self.HOST}; p={P}")

    def test_spaces_around_semicolon_and_equals(self):
        self.assert_parses(f"v = abiz1 ; k = us-or-123456 ; h = {self.HOST} ; p = {P}")

    def test_tabs(self):
        self.assert_parses(f"v=abiz1;\tk=us-or-123456\t;\th\t=\t{self.HOST}\t;\tp\t=\t{P}")

    def test_leading_and_trailing_whitespace(self):
        self.assert_parses(f"  v=abiz1;k=us-or-123456;h={self.HOST};p={P}  ")

    def test_single_trailing_semicolon(self):
        self.assert_parses(f"v=abiz1;k=us-or-123456;h={self.HOST};p={P};")
        self.assert_parses(f"v=abiz1; k=us-or-123456; h={self.HOST} ; p={P} ; ")

    def test_spaced_record_validates_end_to_end(self):
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example",
                         f"v=abiz1; k=us-or-123456; h={self.HOST}; p={P};"), [])

    def test_p_padding_survives_spaces_around_equals(self):
        key = "6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk="
        tags = dns_tags(f"v=abiz1; h={self.HOST}; p = {key} ;")
        self.assertEqual(tags["p"], key)
        self.assertEqual(len(decode_ed25519_public_key(tags["p"])), 32)

    def test_unknown_tags_ignored_even_if_repeated(self):
        tags = dns_tags(f"v=abiz1; h={self.HOST}; x=1; x=2; Future-Tag=ok; p={P}")
        self.assertEqual(tags["h"], self.HOST)

    def test_still_invalid(self):
        bad = [
            f"v=abiz1; h=harbour bike.example",           # space inside a value
            f"v=abiz1; h=a.example; k=us-or-123 456",      # space inside a value
            f"v=abiz1; h={self.HOST}; h=other.example",   # duplicate recognised tag
            f"v=abiz1; k=us-or-1; k=us-or-2; h={self.HOST}",  # duplicate k
            f"V=ABIZ1; h={self.HOST}",                    # tag names and values are case-sensitive
            f"V=abiz1; h={self.HOST}",
            f"v=ABIZ1; h={self.HOST}",
            f"h={self.HOST}; v=abiz1",                    # v must be first
            f"k=us-or-123456; h={self.HOST}",              # v missing
            f"v=abiz2; h={self.HOST}",                    # other version
            f"v=abiz1; h={self.HOST};;",                  # only one trailing ";"
            f"v=abiz1;; h={self.HOST}",                   # empty tag
            f"v=abiz1; h={self.HOST}; flag",              # tag without "="
            f"v=abiz1; h=; k=us-or-123456",                # empty value
            f"v=abiz1;\nh={self.HOST}",                   # only SP and HTAB are allowed
            f"v=abiz1;\r\nh={self.HOST}",
            f"v=abiz1;\u00a0h={self.HOST}",               # no-break space is not WSP
            f"v=abiz1; H={self.HOST}",                    # H is an unknown tag, so h is missing
        ]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                dns_tags(value)

    def test_assertion_selection(self):
        self.assertTrue(is_abiz_assertion("v=abiz1;h=a.example"))
        self.assertTrue(is_abiz_assertion(" v = abiz1 ; h=a.example"))
        self.assertTrue(is_abiz_assertion("v=abiz1"))
        for other in ("v=spf1 -all", "V=abiz1;h=a.example", "v=abiz10;h=a.example",
                      "v=abiz1x;h=a.example", "h=a.example;v=abiz1", "x v=abiz1"):
            with self.subTest(value=other):
                self.assertFalse(is_abiz_assertion(other))


class ABIZBusinessKeyTests(unittest.TestCase):
    """Published ABIZ 1.1 business key, SPEC.md section 4.2."""

    HOST = "harbour-bike-repair.or.us.to.co"

    def record(self, key, number, country="us"):
        r = copy.deepcopy(REG)
        r["country"], r["business_key"], r["registration_number"] = country, key, number
        r["locations"][0]["address"] = {"country": {"code": country.upper()}}
        r["locations"][0].pop("opening_hours")
        return resign(r)

    def test_valid_keys_per_country(self):
        for key in ("us-or-123456", "us-dc-A1", "ca-on-1001216372", "ca-bc-BC0578072",
                    "ca-12345678", "ae-du-1234567", "ae-az-ADGM000123", "gb-01234567",
                    "gb-SC123456", "jp-1234567890123", "de-K1101RHRB12345", "au-123456789",
                    "in-U72200MH2009PLC123456", "br-12345678000195", "ch-CHE123456789",
                    "cn-91110000123456789X", "mx-ABC010101AB1", "pr-123456"):
            with self.subTest(key=key):
                parse_business_key(key)
                self.assertEqual(dns_tags(f"v=abiz1;k={key};h={self.HOST};p={P}")["k"], key)

    def test_invalid_country(self):
        for key in ("uk-01234567", "xk-123", "eu-123", "zz-123", "u1-123", "usa-or-1"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_business_key(key)
        bad = copy.deepcopy(REG)
        bad["country"] = "UK"
        bad["business_key"], bad["registration_number"] = "uk-123456", "123456"
        self.assertTrue(validate_record(bad, SCHEMA))
        bad = copy.deepcopy(UNREG)
        bad["locations"][0]["address"]["country"]["code"] = "ZZ"
        self.assertTrue(validate_record(resign(bad), SCHEMA))
        bad["locations"][0]["address"]["country"]["code"] = "us"
        self.assertTrue(validate_record(resign(bad), SCHEMA))

    def test_invalid_subdivision_for_country(self):
        for key in ("us-zz-123456", "us-on-123456", "ca-or-123", "ae-du1-1", "us-pr-123456", "us-um-1"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_business_key(key)

    def test_missing_subdivision_where_required(self):
        for key in ("us-123456", "us-OR123456", "ae-1234567"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_business_key(key)
        with self.assertRaises(ValueError):
            dns_tags(f"v=abiz1;k=us-OR123456;h={self.HOST}")  # the ABIZ 1.0 example key
        self.assertTrue(validate_record(self.record("us-123456", "123456"), SCHEMA))

    def test_canada_federal_key_has_no_subdivision(self):
        self.assertEqual(parse_business_key("ca-12345678"), ("ca", None, "12345678"))

    def test_subdivision_present_where_not_required(self):
        for key in ("gb-eng-01234567", "de-by-HRB12345", "jp-13-1234567890123", "au-nsw-123456789"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_business_key(key)

    def test_case_insensitive_match(self):
        self.assertEqual(canonical_business_key("US-OR-123456"), "us-or-123456")
        self.assertEqual(canonical_business_key("ca-bc-bc0578072"), "ca-bc-BC0578072")
        record = self.record("US-Or-abc123", "ABC123", country="Us")
        self.assertEqual(validate_record(record, SCHEMA), [])
        self.assertEqual(validate_record(record, SCHEMA, "harbourbikes.example",
                         f"v=abiz1;k=us-or-ABC123;h={self.HOST};p={TEST_P}"), [])
        self.assertTrue(validate_record(record, SCHEMA, "harbourbikes.example",
                        f"v=abiz1;k=us-or-ABC124;h={self.HOST};p={TEST_P}"))
        # Uppercase record country, as in the unregistered example, is still valid.
        self.assertEqual(UNREG["country"], "US")
        self.assertEqual(validate_record(UNREG, SCHEMA), [])

    def test_special_characters_rejected(self):
        for number in ("HRB 12345", "123-456", "123.456", "123/456", "12_34", "AB&C", "１２３", "ÄB1"):
            with self.subTest(number=number):
                self.assertTrue(validate_record(self.record(f"us-or-{number}", number), SCHEMA))
        for key in ("us-or-123_456", "us-or-123.456", "us-or-123-456", "us-or-"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_business_key(key)

    def test_key_must_match_registration_number_and_country(self):
        self.assertTrue(validate_record(self.record("us-or-123456", "123457"), SCHEMA))
        self.assertTrue(validate_record(self.record("ca-on-123456", "123456"), SCHEMA))

    def test_normalisation(self):
        self.assertEqual(normalise_registration_number("１２３４５６７８９０１２３"), "1234567890123")
        self.assertEqual(normalise_registration_number("ＨＲＢ　１２３４５"), "HRB12345")
        self.assertEqual(normalise_registration_number("HRB 12345"), "HRB12345")
        self.assertEqual(normalise_registration_number("CHE-123.456.789"), "CHE123456789")
        self.assertEqual(normalise_registration_number("12.345.678/0001-95"), "12345678000195")
        self.assertEqual(normalise_registration_number("1234567-8"), "12345678")
        self.assertEqual(normalise_registration_number("aab\u20101234"), "AAB1234")
        self.assertEqual(normalise_registration_number("01234567"), "01234567")
        self.assertEqual(normalise_registration_number("sc123456"), "SC123456")
        for raw in ("第123号", "AB&C", "Ñ01", "", " - "):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                normalise_registration_number(raw)

    def test_k_is_optional(self):
        # Registration fields in the record do not require k in DNS.
        self.assertIn("business_key", REG)
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", f"v=abiz1;h={self.HOST};p={P}"), [])
        self.assertEqual(validate_record(UNREG, SCHEMA, "marketstand.example",
                         f"v=abiz1;h=market-stand-repairs-portland.biz.to.co;p={MP}"), [])
        # But k without business_key in the record is a mismatch.
        errors = validate_record(UNREG, SCHEMA, "marketstand.example",
                                 f"v=abiz1;k=us-or-123456;h=market-stand-repairs-portland.biz.to.co;p={MP}")
        self.assertEqual(errors, ["DNS k is present for record without a business_key"])

    def test_bundled_iso_data(self):
        data = json.loads((ROOT / "data" / "iso3166.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["countries"]), 249)
        self.assertEqual(len(data["subdivisions"]["us"]), 51)
        self.assertEqual(len(data["subdivisions"]["ca"]), 13)
        self.assertEqual(len(data["subdivisions"]["ae"]), 7)
        self.assertIn("pycountry 26.2.16", data["source"])



class ABIZWellKnownTests(unittest.TestCase):
    """ABIZ 1.1 well-known file, SPEC.md section 3.4."""

    HOST = "harbour-bike-repair.or.us.to.co"

    def test_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(WK_SCHEMA)
        self.assertEqual(WK_SCHEMA["$id"], "https://abizrecord.org/schema/abiz-well-known-v1.1.schema.json")

    def test_examples_validate(self):
        for doc in (WK_REG, WK_UNREG):
            with self.subTest(doc=doc["h"]):
                self.assertEqual(validate_well_known(doc, WK_SCHEMA), [])

    def test_example_matches_dns_example(self):
        self.assertEqual(well_known_tags(WK_REG), dns_tags(example_dns()))

    def test_well_known_alone_validates_record(self):
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", well_known=WK_REG), [])
        self.assertEqual(validate_record(UNREG, SCHEMA, "marketstand.example", well_known=WK_UNREG), [])

    def test_missing_p_or_h_or_bad_v_fails(self):
        for member in ("p", "h", "v"):
            doc = {k: v for k, v in WK_REG.items() if k != member}
            with self.subTest(missing=member):
                self.assertTrue(validate_well_known(doc, WK_SCHEMA))
                with self.assertRaises(ValueError):
                    well_known_tags(doc)
        for v in ("ABIZ1", "abiz2", 1):
            with self.subTest(v=v):
                with self.assertRaises(ValueError):
                    well_known_tags({**WK_REG, "v": v})

    def test_non_key_p_and_bad_values_fail(self):
        for bad in ({"p": "ab" * 16}, {"p": P.rstrip("=")}, {"h": "https://" + self.HOST},
                    {"h": self.HOST + ";x=1"}, {"k": "us-123456"}, {"k": 5}, {"p": " " + P}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    well_known_tags({**WK_REG, **bad})

    def test_unknown_members_ignored(self):
        self.assertEqual(well_known_tags({**WK_REG, "future": "ok"}), well_known_tags(WK_REG))

    def test_not_an_object_fails(self):
        for doc in ([], "v=abiz1", None, 1):
            with self.subTest(doc=doc):
                with self.assertRaises(ValueError):
                    well_known_tags(doc)


class ABIZSourcePrecedenceTests(unittest.TestCase):
    """DNS takes precedence over the well-known file, SPEC.md section 3.4.4."""

    DNS = example_dns()

    def test_dns_only(self):
        self.assertEqual(resolve_sources([self.DNS], None), (dns_tags(self.DNS), "dns"))

    def test_well_known_only(self):
        self.assertEqual(resolve_sources(["v=spf1 -all"], WK_REG), (well_known_tags(WK_REG), "well-known"))

    def test_both_agree(self):
        warnings = []
        self.assertEqual(resolve_sources([self.DNS], WK_REG, warnings)[1], "dns")
        self.assertEqual(warnings, [])

    def test_dns_wins_when_they_disagree(self):
        warnings = []
        tags, source = resolve_sources([self.DNS], WK_UNREG, warnings)
        self.assertEqual((tags, source), (dns_tags(self.DNS), "dns"))
        self.assertEqual(len(warnings), 1)
        self.assertIn("disagrees", warnings[0])
        # The record still validates against the DNS assertion, not the file.
        self.assertEqual(validate_record(REG, SCHEMA, "harbourbikes.example", self.DNS, well_known=WK_UNREG), [])

    def test_invalid_file_ignored_when_dns_valid(self):
        warnings = []
        self.assertEqual(resolve_sources([self.DNS], {"v": "abiz1"}, warnings)[1], "dns")
        self.assertIn("ignored", warnings[0])

    def test_no_fallback_when_dns_is_invalid_or_ambiguous_or_unavailable(self):
        for txt in ([self.DNS, self.DNS], ["v=abiz1;h=" + WK_REG["h"]], ["v=abiz1;h=x.example;p=" + "ab" * 16], None):
            with self.subTest(txt=txt):
                with self.assertRaises(ValueError):
                    resolve_sources(txt, WK_REG)

    def test_nothing_published(self):
        with self.assertRaisesRegex(ValueError, "No ABIZ assertion"):
            resolve_sources([], None)

    def test_cli_well_known(self):
        script = str(ROOT / "scripts" / "validate.py")
        for args in (
            [str(ROOT / "examples" / "registered-us.json"), "--domain", "harbourbikes.example",
             "--well-known", str(ROOT / "examples" / "well-known-registered-us.json")],
            [str(ROOT / "examples" / "well-known-registered-us.json")],
        ):
            with self.subTest(args=args):
                run = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, check=False)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn("PASS", run.stdout)


class ABIZFormatParameterTests(unittest.TestCase):
    """The record host's format parameter and content negotiation, SPEC.md section 4.5."""

    def test_format_parameter(self):
        self.assertEqual(select_representation(None), "html")
        self.assertEqual(select_representation("html", "application/json"), "html")
        self.assertEqual(select_representation("json", "text/html"), "json")
        self.assertEqual(select_representation("markdown"), "markdown")
        self.assertEqual(select_representation("md"), "markdown")  # optional alias

    def test_accept_negotiation_when_format_absent_or_unknown(self):
        self.assertEqual(select_representation(None, "application/json"), "json")
        self.assertEqual(select_representation(None, "text/markdown, text/html;q=0.5"), "markdown")
        self.assertEqual(select_representation(None, "text/html;q=0.9, application/json"), "json")
        self.assertEqual(select_representation("JSON", "text/markdown"), "markdown")  # case-sensitive value
        self.assertEqual(select_representation("xml", None), "html")
        self.assertEqual(select_representation(None, "application/json;q=0"), "html")


class ABIZUnitAndCountryTests(unittest.TestCase):
    """Business units (SPEC.md section 8) and unsupported countries (section 4.2.7)."""

    def test_unit_record_with_path_host(self):
        dns = "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co/events;p=" + P
        self.assertEqual(validate_record(UNIT, SCHEMA), [])
        self.assertEqual(validate_record(UNIT, SCHEMA, "events.harbourbikes.example", dns), [])
        # The unit's path is part of h: the bare parent host does not match it.
        self.assertTrue(validate_record(UNIT, SCHEMA, "events.harbourbikes.example",
                                        "v=abiz1;h=harbour-bike-repair.or.us.to.co;p=" + P))

    def test_north_korea_is_not_supported(self):
        record = resign({"record_version": "abiz1", "business_name": "Example", "country": "kp",
                         "identity_host": "example.biz.to.co", "domains": ["example.example"]})
        self.assertTrue(any("not supported" in e for e in validate_record(record, SCHEMA)))
        self.assertTrue(validate_record(resign({**record, "country": "KP"}), SCHEMA))
        with self.assertRaisesRegex(ValueError, "not supported"):
            parse_business_key("kp-123456")
        located = copy.deepcopy(REG)
        located["locations"][0]["address"] = {"country": {"code": "KP"}}
        located["locations"][0].pop("opening_hours")
        self.assertTrue(any("not supported" in e for e in validate_record(resign(located), SCHEMA)))
        # South Korea is unaffected.
        parse_business_key("kr-1234567890")


class ABIZDocumentExampleTests(unittest.TestCase):
    """Every DNS and well-known example in SPEC.md and README.md passes the validator."""

    def test_dns_examples_in_docs_parse(self):
        import re
        found = 0
        for name in ("SPEC.md", "README.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for value in re.findall(r'IN TXT "([^"]+)"', text):
                found += 1
                with self.subTest(doc=name, value=value):
                    tags = dns_tags(value)
                    self.assertIn("p", tags)
        self.assertGreaterEqual(found, 5)

    def test_well_known_examples_in_docs_validate(self):
        import re
        text = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        blocks = [json.loads(b) for b in re.findall(r"```json\n(.*?)```", text, re.S)]
        docs = [b for b in blocks if isinstance(b, dict) and "v" in b]
        self.assertTrue(docs)
        for doc in docs:
            with self.subTest(doc=doc):
                self.assertEqual(validate_well_known(doc, WK_SCHEMA), [])


    def test_record_examples_in_docs_validate(self):
        import re
        found = 0
        for name in ("SPEC.md", "README.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for block in re.findall(r"```json\n(.*?)```", text, re.S):
                doc = load_json_strict(block)
                if isinstance(doc, dict) and "record_version" in doc:
                    found += 1
                    with self.subTest(doc=name, record=doc["business_name"]):
                        self.assertEqual(validate_record(doc, SCHEMA), [])
        self.assertGreaterEqual(found, 1)

    def test_no_hyphenated_member_names_in_docs(self):
        import re
        for name in ("SPEC.md", "README.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for block in re.findall(r"```json\n(.*?)```", text, re.S):
                self.assertFalse(re.search(r'"[a-z]+-[a-z-]+"\s*:', block), block[:120])

class ABIZRecordSigningTests(unittest.TestCase):
    """public_key and signature in the business record, SPEC.md section 4.6."""

    def test_examples_are_signed_and_verify(self):
        for name, record, p in (("registered", REG, P), ("unit", UNIT, P), ("unregistered", UNREG, MP)):
            with self.subTest(example=name):
                self.assertEqual(verify_record_signature(record), base64.b64decode(record["public_key"]))
                check_public_key_matches_p(record, p)
                self.assertEqual(list(record)[-1], "signature")

    def test_signing_input_test_vector(self):
        vector = (ROOT / "examples" / "registered-us.signing-input.txt").read_bytes()
        self.assertEqual(signing_input(REG), vector)
        self.assertNotIn(b'"signature"', vector)
        self.assertIn(b'"public_key"', vector)
        # Member order and whitespace in the served JSON do not matter.
        shuffled = dict(reversed(list(REG.items())))
        self.assertEqual(signing_input(shuffled), vector)
        self.assertEqual(validate_record(shuffled, SCHEMA), [])

    def test_missing_public_key_or_signature_fails(self):
        for member in ("public_key", "signature"):
            with self.subTest(missing=member):
                record = {k: v for k, v in REG.items() if k != member}
                errors = validate_record(record, SCHEMA)
                self.assertTrue(any(member in e for e in errors), errors)

    def test_tampered_record_fails(self):
        for change in ({"business_name": "Harbour Bike Repair Ltd"}, {"last_updated": "2026-11-04T09:00:00Z"},
                       {"extensions": {"example.test": {"note": "added"}}}, {"public_key": TEST_P}):
            with self.subTest(change=change):
                errors = validate_record({**REG, **change}, SCHEMA)
                self.assertTrue(any("did not verify" in e for e in errors), errors)

    def test_bad_signature_encoding_fails(self):
        sig = REG["signature"]
        for bad in (sig[:-2], sig[:10] + "-" + sig[11:], sig[:20] + "_" + sig[21:], "A" * 88,
                    sig[:-3] + ("B==" if sig.endswith("A==") else "A==")):
            with self.subTest(bad=bad):
                self.assertTrue(validate_record({**REG, "signature": bad}, SCHEMA))

    def test_public_key_must_match_p(self):
        # Validly signed with another key, but DNS p names the example key: identity claim rejected.
        other = resign(REG)
        self.assertEqual(validate_record(other, SCHEMA), [])
        errors = validate_record(other, SCHEMA, "harbourbikes.example", example_dns())
        self.assertEqual(errors, ["record public_key does not match p: the identity claim is rejected"])
        errors = validate_record(other, SCHEMA, "harbourbikes.example", well_known=WK_REG)
        self.assertEqual(errors, ["record public_key does not match p: the identity claim is rejected"])
        self.assertTrue(validate_record(REG, SCHEMA, p_value=TEST_P))
        self.assertEqual(validate_record(REG, SCHEMA, p_value=P), [])

    def test_sign_record_round_trip(self):
        record = resign({k: v for k, v in UNREG.items() if k not in ("public_key", "signature")})
        self.assertEqual(record["public_key"], TEST_P)
        self.assertEqual(validate_record(record, SCHEMA, p_value=TEST_P), [])

    def test_jcs_rfc8785_vectors(self):
        # RFC 8785 section 3.2.2 and appendix B examples.
        self.assertEqual(jcs_canonicalize({"b": 1, "a": [True, None, "x"]}), '{"a":[true,null,"x"],"b":1}')
        self.assertEqual(jcs_canonicalize("\u20ac$\u000f\nA'B\"\\\\\"/"), '"€$\\u000f\\nA\'B\\"\\\\\\\\\\"/"')
        numbers = [0.0, -0.0, 1e21, 1e-7, 333333333.3333333, 1e+30, 4.5, 2e-3, 0.000001, 1e23, 9007199254740992]
        self.assertEqual([jcs_canonicalize(n) for n in numbers],
                         ["0", "0", "1e+21", "1e-7", "333333333.3333333", "1e+30", "4.5", "0.002", "0.000001",
                          "1e+23", "9007199254740992"])
        # Sorting is by UTF-16 code units, not code points (RFC 8785 section 3.2.3).
        self.assertEqual(jcs_canonicalize({"\U0001F600": 1, "\uFB33": 2}), '{"\U0001F600":1,"\uFB33":2}')
        for bad in (float("nan"), float("inf"), "\ud800", 2**60):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                jcs_canonicalize(bad)

    def test_duplicate_members_rejected(self):
        text = (ROOT / "examples" / "registered-us.json").read_text(encoding="utf-8")
        self.assertEqual(load_json_strict(text), REG)
        with self.assertRaises(ValueError):
            load_json_strict('{"business_name": "A", "business_name": "B"}')

    def test_cli_signature_checks(self):
        script = str(ROOT / "scripts" / "validate.py")
        reg = str(ROOT / "examples" / "registered-us.json")
        alone = subprocess.run([sys.executable, script, reg], capture_output=True, text=True, check=False)
        self.assertEqual(alone.returncode, 0, alone.stderr)
        self.assertIn("record signature", alone.stdout)
        self.assertIn("identity claim is unconfirmed", alone.stdout)
        ok = subprocess.run([sys.executable, script, reg, "--p", P], capture_output=True, text=True, check=False)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = subprocess.run([sys.executable, script, reg, "--p", MP], capture_output=True, text=True, check=False)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("public_key does not match p", bad.stderr)


if __name__ == "__main__":
    unittest.main()
