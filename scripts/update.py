#!/usr/bin/env python3
"""Generate brew-nix-compatible metadata from the cask registry."""

from __future__ import annotations

import argparse
import json
import urllib.request
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from urllib.parse import urlparse

from .adapters import ADAPTERS

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry"
OUTPUT = ROOT / "cask.json"
USER_AGENT = "futuping/brew-api-extra"


def load_registry(directory: Path = REGISTRY) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    tokens: set[str] = set()

    for path in sorted(directory.glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise RuntimeError(f"{path}: registry entry must be a JSON object")

        token = spec.get("token")
        adapter = spec.get("adapter")
        source = spec.get("source")
        if not isinstance(token, str) or not token:
            raise RuntimeError(f"{path}: token must be a non-empty string")
        if path.stem != token:
            raise RuntimeError(f"{path}: filename must match token {token!r}")
        if token in tokens:
            raise RuntimeError(f"duplicate cask token: {token}")
        if adapter not in ADAPTERS:
            raise RuntimeError(f"{path}: unsupported adapter {adapter!r}")
        if not isinstance(source, str) or not source:
            raise RuntimeError(f"{path}: source must be a non-empty string")
        parsed = urlparse(source)
        if parsed.scheme != "https":
            raise RuntimeError(f"{path}: source must use HTTPS")

        tokens.add(token)
        specs.append(spec)

    if not specs:
        raise RuntimeError(f"no registry entries found in {directory}")
    return specs


def fetch_source(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_catalog(
    specs: Iterable[Mapping[str, object]],
    fetch: Callable[[str], str] = fetch_source,
) -> list[dict[str, object]]:
    catalog: list[dict[str, object]] = []
    for spec in specs:
        token = str(spec["token"])
        adapter_name = str(spec["adapter"])
        source = fetch(str(spec["source"]))
        metadata = ADAPTERS[adapter_name](source, spec)
        if metadata.get("token") != token:
            raise RuntimeError(f"adapter changed cask token {token!r}")
        catalog.append(metadata)
    return sorted(catalog, key=lambda item: str(item["token"]))


def render_catalog(catalog: list[dict[str, object]]) -> str:
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def update(check: bool = False) -> bool:
    catalog = build_catalog(load_registry())
    rendered = render_catalog(catalog)
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
    if current == rendered:
        versions = ", ".join(
            f"{item['token']} {item['version']}" for item in catalog
        )
        print(f"{OUTPUT.name} is already current ({versions})")
        return False
    if check:
        raise RuntimeError(f"{OUTPUT.name} is not current")
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"updated {OUTPUT.name} ({len(catalog)} cask(s))")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when cask.json is stale",
    )
    arguments = parser.parse_args()
    update(check=arguments.check)


if __name__ == "__main__":
    main()
