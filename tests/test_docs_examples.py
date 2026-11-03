"""Every DNS assertion shown in the documentation is a valid published ABIZ 1.1 assertion.

Covers README.md, SPEC.md and every page under docs/ (all regions and languages):
TXT records in DNS examples and the --dns-value of validator commands. A record
host with a path is a business unit (SPEC section 8); a business's main record uses
a bare host, so a path host is accepted only when the same page also shows the
parent's bare-host assertion.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import dns_tags  # noqa: E402

TXT = re.compile(r'IN\s+TXT\s+"([^"]+)"')
DNS_VALUE = re.compile(r"--dns-value\s+(?:'(v=abiz1[^']+)'|\"(v=abiz1[^\"]+)\")")


def pages():
    yield ROOT / "README.md"
    yield ROOT / "SPEC.md"
    yield from sorted((ROOT / "docs").rglob("*.md"))


def assertions(text):
    for match in TXT.finditer(text):
        yield match.group(1)
    for match in DNS_VALUE.finditer(text):
        yield match.group(1) or match.group(2)


class DocumentedAssertionTests(unittest.TestCase):
    def test_every_documented_assertion_is_valid_abiz_1_1(self):
        count = 0
        for path in pages():
            for value in assertions(path.read_text(encoding="utf-8")):
                count += 1
                with self.subTest(page=str(path.relative_to(ROOT)), value=value):
                    tags = dns_tags(value)  # raises for a missing or malformed p, bad h or k
                    self.assertRegex(tags["p"], r"^[A-Za-z0-9+/]{43}=$")
        self.assertGreater(count, 590)

    def test_main_records_use_a_bare_host(self):
        for path in pages():
            text = path.read_text(encoding="utf-8")
            hosts = set()
            parsed = []
            for value in assertions(text):
                h = dns_tags(value)["h"]
                parsed.append(h)
                hosts.add(h.lower())
            for h in parsed:
                if "/" not in h:
                    continue
                parent = h.split("/", 1)[0].lower()
                with self.subTest(page=str(path.relative_to(ROOT)), h=h):
                    self.assertIn(parent, hosts, "a path record host must be a unit shown beside its parent's bare host")
                    self.assertFalse(h.endswith(".json"), "a record host is not a JSON file path")


class StatusWordingTests(unittest.TestCase):
    """ABIZ 1.1 is the published, stable version; nothing may describe it as a proposal."""

    PROPOSED = re.compile(r"proposed\s+(?:ABIZ\s+)?1\.1|1\.1\s+(?:is\s+)?(?:a\s+)?proposal|ABIZ 1\.1 (?:public-review )?draft", re.I)

    def test_no_proposed_1_1_wording(self):
        files = [ROOT / "README.md", ROOT / "SPEC.md", ROOT / "scripts" / "validate.py"]
        # The published 1.0 schema is immutable and is not edited here, even in its annotations.
        files += sorted((ROOT / "docs").rglob("*.md")) + sorted(
            path for path in (ROOT / "schemas").glob("*.json") if path.name != "abiz-business-record-v1.schema.json")
        files += sorted((ROOT / "examples").rglob("*.md"))
        hits = []
        for path in files:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if self.PROPOSED.search(line):
                    hits.append(f"{path.relative_to(ROOT)}:{number}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
