import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_docs_links import github_slug, run


def copy_docs(dest: Path) -> None:
    shutil.copytree(ROOT / "docs", dest / "docs")
    for name in ("README.md", "SPEC.md", "CHANGELOG.md"):
        shutil.copy(ROOT / name, dest / name)
    for name in ("schemas", "scripts", "examples"):
        shutil.copytree(ROOT / name, dest / name)


class DocsNavigationTests(unittest.TestCase):
    def test_repository_navigation_is_valid(self):
        self.assertEqual(run(ROOT), [])

    def test_unlinked_country_guide_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_docs(root)
            (root / "docs/countries/europe/zz-dummy.md").write_text("# Dummy\n", encoding="utf-8")
            errors = run(root)
            self.assertTrue(any("country guide not linked: zz-dummy.md" in e for e in errors), errors)

    def test_broken_link_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_docs(root)
            (root / "docs/countries/oceania/fiji.md").unlink()
            errors = run(root)
            self.assertTrue(any("missing file: fiji.md" in e for e in errors), errors)

    def test_github_slug(self):
        self.assertEqual(github_slug("The ABIZ 1.1 `p` key"), "the-abiz-11-p-key")
        self.assertEqual(github_slug("What will I learn?"), "what-will-i-learn")


if __name__ == "__main__":
    unittest.main()
