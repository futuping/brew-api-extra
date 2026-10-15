import json
from pathlib import Path
import unittest

from scripts.adapters import ADAPTERS

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "search-arch-app.rb"


class SearchArchAppTests(unittest.TestCase):
    def setUp(self):
        self.source = FIXTURE.read_text(encoding="utf-8")
        self.spec = json.loads(
            (ROOT / "registry" / "search.json").read_text(encoding="utf-8")
        )

    def build(self, source=None):
        return ADAPTERS[self.spec["adapter"]](
            self.source if source is None else source, self.spec
        )

    def test_search_registry_builds_both_architectures(self):
        metadata = self.build()
        self.assertEqual(metadata["version"], "1.0.5")
        self.assertEqual(
            metadata["url"],
            "https://github.com/driceroland/Search/releases/download/v1.0.5/Search.dmg",
        )
        self.assertEqual(
            metadata["sha256"],
            "4c750f505cf108bf06fc3be256abaeab3c0dfa1a587bec7036f1bbe732466ea1",
        )
        self.assertEqual(metadata["artifacts"], [{"app": ["Search.app"]}])
        self.assertEqual(
            metadata["depends_on"], {"macos": {">=": ["14"]}}
        )
        self.assertEqual(
            set(metadata["variations"]), {"golden_gate", "tahoe", "sequoia", "sonoma"}
        )
        for variation in metadata["variations"].values():
            self.assertEqual(
                variation,
                {
                    "url": "https://github.com/driceroland/Search/releases/download/v1.0.5/Search-Intel.dmg",
                    "sha256": "9feab786e545b9f4a40b68bd985cd1f24956b772abd1bdf9e91198e3812b1b64",
                },
            )

    def test_preserves_other_known_macos_minimums(self):
        for name, version in (("sequoia", "15"), ("tahoe", "26")):
            with self.subTest(name=name):
                metadata = self.build(self.source.replace(":sonoma", ":" + name))
                self.assertEqual(metadata["depends_on"], {"macos": {">=": [version]}})

    def test_rejects_unknown_or_unsupported_macos_requirements(self):
        for value in (":unknown", '">= :sonoma"', "[:sonoma, :sequoia]"):
            with self.subTest(value=value), self.assertRaisesRegex(RuntimeError, "macOS"):
                self.build(self.source.replace(":sonoma", value))

    def test_rejects_missing_architecture_or_checksum(self):
        for old, new in (
            ('arch arm: "", intel: "-Intel"', ""),
            ('intel: "-Intel"', 'intel: nil'),
            ("sha256 arm:", "sha256:"),
            ("9feab786", "invalid!"),
        ):
            with self.subTest(old=old), self.assertRaises(RuntimeError):
                self.build(self.source.replace(old, new))

    def test_rejects_unreviewed_url_or_interpolation(self):
        for old, new in (
            ("https://github.com/", "http://github.com/"),
            ("https://github.com/", "https://example.invalid/"),
            ("#{arch}", "#{unreviewed}"),
        ):
            with self.subTest(new=new), self.assertRaises(RuntimeError):
                self.build(self.source.replace(old, new))


if __name__ == "__main__":
    unittest.main()
