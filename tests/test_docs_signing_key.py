"""Country guides must state that the ABIZ 1.1 DNS signing key p is required."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# A line that names ABIZ 1.0 may still describe the historical optional token.
HISTORICAL = re.compile(r"ABIZ 1\.0")

# Phrases that tell a reader p may be omitted, or that deleting p revokes an assertion.
FORBIDDEN = (
    re.compile(r"`?p`?\s+is\s+optional", re.I),
    re.compile(r"optional signing key", re.I),
    re.compile(r"remove\s+`?p`?\s+to\s+revoke", re.I),
    re.compile(r"h\s+is\s+required;\s*`?k`?\s+and\s+`?p`?\s+are\s+optional", re.I),
    re.compile(r"`k`\s+and\s+`p`\s+are\s+optional", re.I),
    re.compile(r"`p`\s+est\s+facultati", re.I),
    re.compile(r"`p`\s+es\s+opcional", re.I),
    re.compile(r"`p`\s+é\s+opcional", re.I),
    re.compile(r"`p`\s+ist\s+optional", re.I),
    re.compile(r"`p`\s+è\s+facoltativ", re.I),
    re.compile(r"`p`\s+is\s+optioneel", re.I),
    re.compile(r"`p`\s+är\s+frivillig", re.I),
    re.compile(r"`p`\s+er\s+valgfri\b", re.I),
    re.compile(r"`p`\s+jest\s+opcjonal", re.I),
    re.compile(r"`p`\s+este\s+opțional", re.I),
    re.compile(r"`p`\s+необязател"),
    re.compile(r"`p`\s+необов"),
    re.compile(r"необязательный ключ подписи"),
    re.compile(r"тегов `k` и `p`"),
    re.compile(r"`k`\s+i\s+`p`\s+są\s+opcjonal"),
    re.compile(r"`k`\s+og\s+`p`\s+er\s+valgfri"),
    re.compile(r"`k`\s+och\s+`p`\s+är\s+frivill"),
    re.compile(r"`k`\s+și\s+`p`\s+sunt\s+opțional"),
    re.compile(r"`k`\s+і\s+`p`\s+необов"),
    re.compile(r"удалите `p`"),
    re.compile(r"usuwa się `p`"),
    re.compile(r"eliminați `p`"),
    re.compile(r"fjerner dere `p`"),
    re.compile(r"tar ni bort `p`"),
    re.compile(r"видаліть `p`"),
    re.compile(r"utelat `p`"),
    re.compile(r"utelämna `p`"),
    re.compile(r"pominąć `p`"),
    re.compile(r"omiteți `p`"),
    re.compile(r"не вказуйте `p`"),
    re.compile(r"omettez `p`", re.I),
    re.compile(r"omita `p`", re.I),
    re.compile(r"leave `p` out", re.I),
    re.compile(r"to revoke,\s*remove `p`", re.I),
)

# Each country guide must say, in its language, that p is required.
REQUIRED_MARK = re.compile(
    r"`p`.{0,40}("
    r"required|obligatoire|obligatori|obrigat|Pflicht|obbligat|إلزامي|必填|必須|"
    r"필수|נדרש|υποχρεωτικ|wajib|ข้อบังคับ|bắt buộc|zorunlu|обязател|verplicht|"
    r"povinn|obligatorisk|pakoll|обов.язков|wymagane"
    r")",
    re.I,
)


def scanned_files():
    yield ROOT / "README.md"
    yield ROOT / "SPEC.md"
    yield from sorted(DOCS.rglob("*.md"))


def country_guides():
    for path in sorted((DOCS / "countries").rglob("*.md")):
        if path.name in {"index.md", "README.md"}:
            continue
        yield path


class SigningKeyDocumentationTests(unittest.TestCase):
    def test_guides_do_not_say_p_is_optional(self):
        hits = []
        for path in scanned_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if HISTORICAL.search(line):
                    continue
                for pattern in FORBIDDEN:
                    if pattern.search(line):
                        hits.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
                        break
        self.assertEqual(hits, [], "\n".join(hits))

    def test_every_country_guide_requires_p(self):
        missing = []
        for path in country_guides():
            text = path.read_text(encoding="utf-8")
            if REQUIRED_MARK.search(text) is None:
                missing.append(str(path.relative_to(ROOT)))
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
