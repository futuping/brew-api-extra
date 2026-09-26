"""Adapter for a single Apple Silicon app with an explicit macOS minimum."""

from __future__ import annotations

from collections.abc import Mapping

from .common import match
from .homebrew_app import build as build_app

MACOS_VERSIONS = {"sonoma": "14", "sequoia": "15", "tahoe": "26"}


def build(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    architecture = match(
        r"^\s*depends_on arch: :(\w+)\s*$", source, "architecture requirement"
    )
    if architecture != "arm64":
        raise RuntimeError("expected an arm64-only cask")
    minimum = match(
        r"^\s*depends_on macos: :(\w+)\s*$", source, "macOS requirement"
    )
    if minimum not in MACOS_VERSIONS:
        raise RuntimeError(f"unsupported macOS minimum: {minimum}")

    metadata = build_app(source, spec)
    metadata["depends_on"] = {
        "arch": [{"type": "arm", "bits": 64}],
        "macos": {">=": [MACOS_VERSIONS[minimum]]},
    }
    return metadata
