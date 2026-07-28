"""Adapter for an arm/intel Homebrew cask containing one app artifact."""

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
    metadata = base_metadata(source, spec)
    url_template = match(r'^\s*url\s+"([^"]+)"', source, "URL")
    arm_arch, intel_arch = match_groups(
        r'^\s*arch\s+arm:\s*"([^"]+)",\s*intel:\s*"([^"]+)"',
        source,
        "architecture names",
    )
    arm_sha256, intel_sha256 = match_groups(
        rf'^\s*sha256\s+arm:\s*"({SHA256_PATTERN})",'
        rf'\s*intel:\s*"({SHA256_PATTERN})"',
        source,
        "architecture SHA-256 values",
    )
    allowed_hosts = string_list(spec, "download_hosts")
    version = str(metadata["version"])

    return complete_metadata(
        metadata,
        render_url(
            url_template,
            {"version": version, "arch": arm_arch},
            allowed_hosts,
        ),
        arm_sha256,
        {
            variation: {
                "url": render_url(
                    url_template,
                    {"version": version, "arch": intel_arch},
                    allowed_hosts,
                ),
                "sha256": intel_sha256,
            }
            for variation in string_list(spec, "intel_variations")
        },
    )
