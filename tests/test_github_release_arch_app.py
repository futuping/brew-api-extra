import copy
import json
from pathlib import Path
import unittest

from scripts.adapters import ADAPTERS
from scripts.update import SourceRedirectHandler, validate_release_updates
from urllib.request import Request

ROOT = Path(__file__).resolve().parent.parent


class GitHubReleaseTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / "registry/rayburst.json").read_text())
        self.release = json.loads((ROOT / "tests/fixtures/rayburst-release.json").read_text())

    def build(self):
        return ADAPTERS["github-release-arch-app"](json.dumps(self.release), self.spec)

    def test_both_architectures_and_bundle(self):
        result = self.build()
        self.assertEqual(result["version"], "4.0.0-beta.2")
        self.assertEqual(result["artifacts"], [{"app": ["Rayburst.app"]}])
        self.assertTrue(result["url"].endswith("/Rayburst_aarch64.app.tar.gz"))
        self.assertEqual(result["sha256"], self.release["assets"][0]["digest"][7:])
        for item in result["variations"].values():
            self.assertTrue(item["url"].endswith("/Rayburst_x64.app.tar.gz"))
            self.assertEqual(item["sha256"], self.release["assets"][1]["digest"][7:])

    def test_rejects_unapproved_prerelease(self):
        self.spec["allow_prerelease"] = False
        with self.assertRaisesRegex(RuntimeError, "explicit opt-in"):
            self.build()

    def test_rejects_wrong_release_and_draft(self):
        for field, value in (("tag_name", "v3.9.9"), ("draft", True), ("prerelease", False)):
            with self.subTest(field=field):
                old = self.release[field]
                self.release[field] = value
                with self.assertRaises(RuntimeError):
                    self.build()
                self.release[field] = old

    def test_requires_exactly_one_asset_per_architecture(self):
        for assets in (self.release["assets"][:1], self.release["assets"] * 2):
            with self.subTest(assets=assets):
                original = self.release["assets"]
                self.release["assets"] = assets
                with self.assertRaisesRegex(RuntimeError, "exactly one asset"):
                    self.build()
                self.release["assets"] = original

    def test_rejects_invalid_asset_identity(self):
        for field, value in (
            ("digest", None), ("digest", "sha256:123"),
            ("size", 0), ("size", True), ("size", 300 * 1024 * 1024),
            ("browser_download_url", "https://example.com/Rayburst_aarch64.app.tar.gz"),
            ("browser_download_url", "https://github.com/other/project/releases/download/v4.0.0-beta.2/Rayburst_aarch64.app.tar.gz"),
        ):
            with self.subTest(field=field, value=value):
                old = self.release["assets"][0][field]
                self.release["assets"][0][field] = value
                with self.assertRaises(RuntimeError):
                    self.build()
                self.release["assets"][0][field] = old

    def test_rejects_wrong_metadata_source_and_download_host(self):
        self.spec["source"] = "https://api.github.com/repos/other/project/releases/latest"
        with self.assertRaisesRegex(RuntimeError, "source must match"):
            self.build()
        self.setUp()
        self.spec["download_hosts"] = ["example.com"]
        with self.assertRaisesRegex(RuntimeError, "unexpected release URL"):
            self.build()

    def test_rejects_mutated_hash_and_downgrade(self):
        original = self.build()
        for version, digest in (("4.0.0-beta.2", "0" * 64), ("4.0.0-beta.1", original["sha256"])):
            candidate = copy.deepcopy(original)
            candidate.update(version=version, sha256=digest)
            with self.subTest(version=version), self.assertRaises(RuntimeError):
                validate_release_updates([original], [candidate], [self.spec])

    def test_allows_no_change_and_promotion_to_stable(self):
        original = self.build()
        validate_release_updates([original], [original], [self.spec])
        stable = dict(original, version="4.0.0")
        validate_release_updates([original], [stable], [self.spec])
        with self.assertRaisesRegex(RuntimeError, "downgrade"):
            validate_release_updates([stable], [original], [self.spec])

    def test_rejects_metadata_redirect_to_another_host(self):
        handler = SourceRedirectHandler()
        request = Request(self.spec["source"])
        for target in ("https://example.com/release", "http://api.github.com/release"):
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, "redirect"):
                handler.redirect_request(request, None, 302, "Found", {}, target)


if __name__ == "__main__":
    unittest.main()
