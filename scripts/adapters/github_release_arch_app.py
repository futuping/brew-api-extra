"""Pinned GitHub release assets for a cask whose tap has not caught up."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from urllib.parse import quote

from .common import complete_metadata, render_url, required_string, string_list


def build(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    repository = required_string(spec, "repository")
    tag = required_string(spec, "tag")
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None:
        raise RuntimeError("invalid GitHub repository")
    if re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-beta\.[0-9]+)?", tag) is None:
        raise RuntimeError("unsupported release tag")
    expected_source = f"https://api.github.com/repos/{repository}/releases/tags/{tag}"
    if spec.get("source") != expected_source:
        raise RuntimeError("release source must match the pinned repository and tag")

    release = json.loads(source)
    if not isinstance(release, dict) or release.get("tag_name") != tag:
        raise RuntimeError("release does not match the pinned tag")
    if release.get("draft") is not False:
        raise RuntimeError("draft releases are not accepted")
    prerelease = release.get("prerelease")
    if not isinstance(prerelease, bool) or prerelease != ("-" in tag):
        raise RuntimeError("inconsistent prerelease metadata")
    if prerelease and spec.get("allow_prerelease") is not True:
        raise RuntimeError("prerelease requires explicit opt-in")

    app = required_string(spec, "app")
    if re.fullmatch(r"[A-Za-z0-9 _-]+\.app", app) is None:
        raise RuntimeError("invalid application bundle name")
    assets = release.get("assets")
    if not isinstance(assets, list) or any(not isinstance(a, dict) for a in assets):
        raise RuntimeError("invalid release assets")

    def asset(architecture: str) -> dict[str, str]:
        name = required_string(spec, f"{architecture}_asset")
        if re.fullmatch(r"[A-Za-z0-9_.-]+\.app\.tar\.gz", name) is None:
            raise RuntimeError("invalid application asset name")
        matches = [a for a in assets if a.get("name") == name]
        if len(matches) != 1:
            raise RuntimeError(f"expected exactly one asset: {name}")
        selected = matches[0]
        expected_url = f"https://github.com/{repository}/releases/download/{tag}/{quote(name)}"
        url = selected.get("browser_download_url")
        if url != expected_url:
            raise RuntimeError("asset URL does not match the pinned release")
        render_url(url, {}, string_list(spec, "download_hosts"))
        digest = selected.get("digest")
        if not isinstance(digest, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None:
            raise RuntimeError("asset requires a complete SHA-256 digest")
        size = selected.get("size")
        if type(size) is not int or not 0 < size <= 256 * 1024 * 1024:
            raise RuntimeError("invalid or oversized application asset")
        return {"url": url, "sha256": digest.removeprefix("sha256:")}

    arm = asset("arm")
    intel = asset("intel")
    metadata = {
        "token": required_string(spec, "token"),
        "full_token": required_string(spec, "token"),
        "name": [required_string(spec, "name")],
        "desc": required_string(spec, "desc"),
        "homepage": required_string(spec, "homepage"),
        "version": tag.removeprefix("v"),
        "artifacts": [{"app": [app]}],
        "auto_updates": True,
    }
    return complete_metadata(
        metadata,
        arm["url"],
        arm["sha256"],
        {variation: dict(intel) for variation in string_list(spec, "intel_variations")},
    )
