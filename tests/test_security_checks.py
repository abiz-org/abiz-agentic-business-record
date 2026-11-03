"""Security review items for published ABIZ 1.1: record host form, URL hosts and I-JSON."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402
from validate import check_url, dns_tags, identity_parts, load_json_strict  # noqa: E402

SCHEMA = json.loads((ROOT / "schemas" / "abiz-business-record-v1.1.schema.json").read_text())
KEY = "11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo="


class RecordHostTests(unittest.TestCase):
    def test_port_in_h_is_rejected_in_1_1(self):
        for h in ("a.example:443", "a.example:8443", "a.example:abc", "a.example:", "a.example:443/unit"):
            with self.subTest(h=h):
                self.assertIsNone(identity_parts(h))
                with self.assertRaises(ValueError):
                    dns_tags(f"v=abiz1;h={h};p={KEY}")

    def test_bad_port_does_not_crash_1_0(self):
        self.assertIsNone(identity_parts("a.example:abc", "1.0"))
        self.assertIsNotNone(identity_parts("a.example:443", "1.0"))

    def test_bare_host_and_unit_path_are_accepted(self):
        self.assertEqual(identity_parts("WWW.A.example"), "www.a.example")
        self.assertEqual(identity_parts("www.a.example/events"), "www.a.example/events")

    def test_special_use_hosts_are_rejected(self):
        for host in ("shop.local", "localhost", "a.internal", "nas.home.arpa", "x.onion", "a.invalid", "a.alt"):
            with self.subTest(host=host):
                self.assertIsNone(identity_parts(host))
                self.assertFalse(check_url(f"https://{host}/"))

    def test_documentation_names_stay_accepted(self):
        for url in ("https://www.a.example/", "https://shop.test/", "https://example.com/x?y=1"):
            with self.subTest(url=url):
                self.assertTrue(check_url(url))


class URLPolicyTests(unittest.TestCase):
    def test_section_4_7_1_rejections(self):
        for url in ("http://a.example/", "https://u:p@a.example/", "https://a.example/#frag",
                    "https://a.example:8443/", "https://127.0.0.1/", "https://[::1]/",
                    "https://a.example/" + "x" * 2048):
            with self.subTest(url=url[:60]):
                self.assertFalse(check_url(url))

    def test_record_with_special_use_website_is_rejected(self):
        record = json.loads((ROOT / "examples" / "locations-and-listings" / "multi-location-gb.json").read_text())
        record = copy.deepcopy(record)
        record["locations"][1]["website"] = "https://shop.local/"
        self.assertTrue(any("safe HTTPS URL" in e for e in validate.check_amended_members(record)))


class IJSONTests(unittest.TestCase):
    def test_malformed_numbers_and_strings_are_rejected_as_malformed(self):
        for text in ('{"a": 1e400}', '{"a": -1e400}', '{"a": 9007199254740993}',
                     '{"a": "\\ud800"}', '{"\\udc00": 1}', '{"a": NaN}', '{"a": 1, "a": 2}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                load_json_strict(text)

    def test_ordinary_numbers_still_parse(self):
        self.assertEqual(load_json_strict('{"a": 9007199254740992, "b": 1.5e3, "c": "\\ud83d\\ude00"}'),
                         {"a": 9007199254740992, "b": 1500.0, "c": "\U0001F600"})

    def test_cli_reports_out_of_range_number_as_malformed(self):
        import subprocess
        import tempfile
        record = json.loads((ROOT / "examples" / "registered-us.json").read_text())
        text = json.dumps(record).replace('"record_version"', '"x_big": 1e400, "record_version"', 1)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write(text)
        try:
            run = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py"), handle.name],
                                 capture_output=True, text=True)
        finally:
            Path(handle.name).unlink()
        output = run.stdout + run.stderr
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("I-JSON", output)
        self.assertNotIn("did not verify", output)


if __name__ == "__main__":
    unittest.main()
