"""Adapter exposing one Homebrew input method as an app for brew-nix."""

from __future__ import annotations

from collections.abc import Mapping

from .common import (
    SHA256_PATTERN,
    base_metadata,
    complete_metadata,
    match,
    match_groups,
    render_url,
    string_list,
)


def build(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    metadata = base_metadata(
        source,
        spec,
        artifact_pattern=r'^\s*input_method\s+"([^"]+\.app)"',
        artifact_label="input method",
    )
    version, build_number = match_groups(
        r'^\s*version\s+"(\d+(?:\.\d+)+),(\d+)"',
        source,
        "CSV version",
    )
    if metadata["version"] != f"{version},{build_number}":
        raise RuntimeError("CSV version does not match cask version")

    url_template = match(r'^\s*url\s+"([^"]+)"', source, "URL")
    return complete_metadata(
        metadata,
        render_url(
            url_template,
            {
                "version.csv.first": version,
                "version.csv.second": build_number,
            },
            string_list(spec, "download_hosts"),
        ),
        match(
            rf'^\s*sha256\s+"({SHA256_PATTERN})"',
            source,
            "SHA-256",
        ),
    )
