"""Adapter for a universal Homebrew cask containing one app artifact."""

from __future__ import annotations

from collections.abc import Mapping

from .common import (
    SHA256_PATTERN,
    base_metadata,
    complete_metadata,
    match,
    render_url,
    string_list,
)


def build(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    metadata = base_metadata(source, spec)
    url_template = match(r'^\s*url\s+"([^"]+)"', source, "URL")
    return complete_metadata(
        metadata,
        render_url(
            url_template,
            {"version": str(metadata["version"])},
            string_list(spec, "download_hosts"),
        ),
        match(
            rf'^\s*sha256\s+"({SHA256_PATTERN})"',
            source,
            "SHA-256",
        ),
    )
