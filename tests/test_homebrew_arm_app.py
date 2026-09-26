from pathlib import Path
import unittest

from scripts.adapters import ADAPTERS

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "arm-app.rb"


class ArmAppTests(unittest.TestCase):
    def build(self, source):
        return ADAPTERS["homebrew-arm-app"](
            source, {"token": "search", "download_hosts": ["github.com"]}
        )

    def test_search_preserves_platform_requirements(self):
        metadata = self.build(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(metadata["version"], "1.0.3")
        self.assertEqual(
            metadata["url"],
            "https://github.com/driceroland/Search/releases/download/v1.0.3/Search.dmg",
        )
        self.assertEqual(metadata["artifacts"], [{"app": ["Search.app"]}])
        self.assertEqual(
            metadata["depends_on"],
            {"arch": [{"type": "arm", "bits": 64}], "macos": {">=": ["14"]}},
        )

    def test_rejects_changed_or_missing_platform_requirements(self):
        source = FIXTURE.read_text(encoding="utf-8")
        for old, new in [
            ("arch: :arm64", "arch: :x86_64"),
            ("depends_on arch: :arm64", ""),
            ("macos: :sonoma", "macos: :unknown"),
            ("depends_on macos: :sonoma", ""),
        ]:
            with self.subTest(new=new), self.assertRaises(RuntimeError):
                self.build(source.replace(old, new))

    def test_rejects_unreviewed_download_url(self):
        source = FIXTURE.read_text(encoding="utf-8")
        for replacement in ["http://github.com/", "https://example.invalid/"]:
            with self.subTest(url=replacement), self.assertRaisesRegex(
                RuntimeError, "unexpected release URL"
            ):
                self.build(source.replace("https://github.com/", replacement))


if __name__ == "__main__":
    unittest.main()
