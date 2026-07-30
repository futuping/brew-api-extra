from pathlib import Path
import unittest

from scripts.adapters import ADAPTERS

FIXTURES = Path(__file__).resolve().parent / "fixtures"
INTEL_VARIATIONS = ["sequoia", "sonoma"]


class AdapterTests(unittest.TestCase):
    def test_homebrew_app(self) -> None:
        source = (FIXTURES / "universal-app.rb").read_text(encoding="utf-8")
        metadata = ADAPTERS["homebrew-app"](
            source,
            {
                "token": "example-app",
                "download_hosts": ["downloads.example.com"],
            },
        )

        self.assertEqual(metadata["version"], "2.4.1")
        self.assertEqual(
            metadata["url"],
            "https://downloads.example.com/Example-2.4.1.zip",
        )
        self.assertEqual(metadata["artifacts"], [{"app": ["Example.app"]}])

    def test_homebrew_arch_app(self) -> None:
        source = (FIXTURES / "arch-app.rb").read_text(encoding="utf-8")
        metadata = ADAPTERS["homebrew-arch-app"](
            source,
            {
                "token": "example-arch-app",
                "download_hosts": ["github.com"],
                "intel_variations": INTEL_VARIATIONS,
            },
        )

        self.assertIn("Example-arm64.zip", metadata["url"])
        self.assertEqual(
            sorted(metadata["variations"]),
            sorted(INTEL_VARIATIONS),
        )
        self.assertTrue(
            all(
                "Example-x86_64.zip" in variation["url"]
                for variation in metadata["variations"].values()
            )
        )

    def test_rejects_unexpected_download_host(self) -> None:
        source = (FIXTURES / "universal-app.rb").read_text(encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "unexpected release URL"):
            ADAPTERS["homebrew-app"](
                source,
                {
                    "token": "example-app",
                    "download_hosts": ["example.invalid"],
                },
            )


if __name__ == "__main__":
    unittest.main()
