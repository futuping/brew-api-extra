import os
import unittest
from unittest.mock import patch

from scripts.update import MAX_SOURCE_BYTES, USER_AGENT, fetch_source

API_URL = "https://api.github.com/repos/example/app/releases/latest"


class FetchSourceTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        opener = patch("scripts.update.urllib.request.build_opener")
        self.build_opener = opener.start()
        self.addCleanup(opener.stop)
        self.open = self.build_opener.return_value.open
        self.response = self.open.return_value.__enter__.return_value
        self.response.read.return_value = b'{"name": "example"}'

    def fetch_request(self, url=API_URL):
        self.assertEqual(fetch_source(url), '{"name": "example"}')
        request = self.open.call_args.args[0]
        self.assertEqual(self.open.call_args.kwargs, {"timeout": 30})
        self.response.read.assert_called_with(MAX_SOURCE_BYTES + 1)
        self.assertEqual(request.get_header("User-agent"), USER_AGENT)
        return request

    def test_authenticates_canonical_github_api(self):
        os.environ["GITHUB_TOKEN"] = "test-token"
        request = self.fetch_request()
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def test_api_still_works_without_token(self):
        for token in (None, ""):
            with self.subTest(token=token):
                if token is not None:
                    os.environ["GITHUB_TOKEN"] = token
                self.assertIsNone(self.fetch_request().get_header("Authorization"))

    def test_never_authenticates_other_authorities_or_insecure_urls(self):
        os.environ["GITHUB_TOKEN"] = "test-token"
        for url in (
            "https://raw.githubusercontent.com/example/tap/main/Casks/app.rb",
            "https://example.com/release",
            "https://api.github.com.example.com/release",
            "http://api.github.com/release",
            "https://api.github.com:8443/release",
            "https://api.github.com:443/release",
            "https://user@api.github.com/release",
            "https://api.github.com@example.com/release",
        ):
            with self.subTest(url=url):
                self.assertIsNone(self.fetch_request(url).get_header("Authorization"))

    def test_does_not_forward_token_on_same_host_redirects(self):
        os.environ["GITHUB_TOKEN"] = "test-token"
        request = self.fetch_request()
        handler = self.build_opener.call_args.args[0]
        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                redirected = handler.redirect_request(
                    request, None, code, "Redirect", {},
                    "https://api.github.com/repos/example/renamed/releases/latest",
                )
                self.assertIsNone(redirected.get_header("Authorization"))
                self.assertEqual(redirected.get_header("User-agent"), USER_AGENT)

    def test_accepts_metadata_at_size_limit(self):
        self.response.read.return_value = b"x" * MAX_SOURCE_BYTES
        self.assertEqual(fetch_source(API_URL), "x" * MAX_SOURCE_BYTES)

    def test_rejects_metadata_over_size_limit(self):
        self.response.read.return_value = b"x" * (MAX_SOURCE_BYTES + 1)
        with self.assertRaisesRegex(RuntimeError, "exceeds size limit"):
            fetch_source(API_URL)
        self.response.read.assert_called_once_with(MAX_SOURCE_BYTES + 1)


if __name__ == "__main__":
    unittest.main()
