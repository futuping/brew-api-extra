#!/usr/bin/env python3
"""Run deterministic, network-free catalog validation."""

from __future__ import annotations

import json

from .update import OUTPUT, load_registry, render_catalog


def main() -> None:
    specs = load_registry()
    catalog_text = OUTPUT.read_text(encoding="utf-8")
    catalog = json.loads(catalog_text)
    if not isinstance(catalog, list):
        raise RuntimeError(f"{OUTPUT.name} must contain a JSON array")

    registry_tokens = sorted(str(spec["token"]) for spec in specs)
    catalog_tokens: list[str] = []
    for index, entry in enumerate(catalog):
        if not isinstance(entry, dict):
            raise RuntimeError(
                f"{OUTPUT.name} entry {index} must be a JSON object"
            )
        token = entry.get("token")
        if not isinstance(token, str) or not token:
            raise RuntimeError(
                f"{OUTPUT.name} entry {index} has an invalid token"
            )
        catalog_tokens.append(token)

    if catalog_tokens != sorted(catalog_tokens):
        raise RuntimeError(f"{OUTPUT.name} entries must be sorted by token")
    if len(catalog_tokens) != len(set(catalog_tokens)):
        raise RuntimeError(f"{OUTPUT.name} contains duplicate tokens")
    if catalog_tokens != registry_tokens:
        raise RuntimeError(
            "registry/catalog token mismatch: "
            f"registry={registry_tokens}, catalog={catalog_tokens}"
        )
    if catalog_text != render_catalog(catalog):
        raise RuntimeError(f"{OUTPUT.name} is not canonically formatted")

    print(
        f"validated {OUTPUT.name} offline "
        f"({len(catalog_tokens)} cask(s))"
    )


if __name__ == "__main__":
    main()
