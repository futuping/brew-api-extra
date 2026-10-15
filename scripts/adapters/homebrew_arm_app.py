"""Adapter for a single Apple Silicon app with an explicit macOS minimum."""

from __future__ import annotations

from collections.abc import Mapping

from .common import macos_requirement, match
from .homebrew_app import build as build_app


def build(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    architecture = match(
        r"^\s*depends_on arch: :(\w+)\s*$", source, "architecture requirement"
    )
    if architecture != "arm64":
        raise RuntimeError("expected an arm64-only cask")
    macos = macos_requirement(source)

    metadata = build_app(source, spec)
    metadata["depends_on"] = {
        "arch": [{"type": "arm", "bits": 64}],
        "macos": macos,
    }
    return metadata
