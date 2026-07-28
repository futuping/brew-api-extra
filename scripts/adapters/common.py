"""Shared parsing and validation helpers for cask adapters."""

from __future__ import annotations

import re
from collections.abc import Mapping
from urllib.parse import urlparse

SHA256_PATTERN = r"[0-9a-f]{64}"


def match(pattern: str, source: str, label: str) -> str:
    result = re.search(pattern, source, re.MULTILINE)
    if result is None:
        raise RuntimeError(f"unable to parse {label} from upstream cask")
    return result.group(1)


def match_groups(
    pattern: str,
    source: str,
    label: str,
) -> tuple[str, ...]:
    result = re.search(pattern, source, re.MULTILINE)
    if result is None:
        raise RuntimeError(f"unable to parse {label} from upstream cask")
    return result.groups()


def base_metadata(source: str, spec: Mapping[str, object]) -> dict[str, object]:
    token = required_string(spec, "token")
    return {
        "token": token,
        "full_token": token,
        "name": [match(r'^\s*name\s+"([^"]+)"', source, "name")],
        "desc": match(r'^\s*desc\s+"([^"]+)"', source, "description"),
        "homepage": match(
            r'^\s*homepage\s+"([^"]+)"',
            source,
            "homepage",
        ),
        "version": match(r'^\s*version\s+"([^"]+)"', source, "version"),
        "artifacts": [
            {
                "app": [
                    match(
                        r'^\s*app\s+"([^"]+\.app)"',
                        source,
                        "application",
                    )
                ]
            }
        ],
        "auto_updates": True,
    }


def complete_metadata(
    metadata: Mapping[str, object],
    url: str,
    sha256: str,
    variations: Mapping[str, object] | None = None,
) -> dict[str, object]:
    result = {
        "token": metadata["token"],
        "full_token": metadata["full_token"],
        "name": metadata["name"],
        "desc": metadata["desc"],
        "homepage": metadata["homepage"],
        "url": url,
        "version": metadata["version"],
        "sha256": sha256,
        "artifacts": metadata["artifacts"],
        "auto_updates": metadata["auto_updates"],
    }
    if variations is not None:
        result["variations"] = dict(variations)
    return result


def render_url(
    template: str,
    variables: Mapping[str, str],
    allowed_hosts: list[str],
) -> str:
    url = template
    for name, value in variables.items():
        url = url.replace(f"#{{{name}}}", value)

    unresolved = re.findall(r"#\{([^}]+)\}", url)
    if unresolved:
        names = ", ".join(sorted(set(unresolved)))
        raise RuntimeError(f"unsupported URL interpolation variable(s): {names}")

    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise RuntimeError(f"unexpected release URL: {url}")
    return url


def required_string(spec: Mapping[str, object], key: str) -> str:
    value = spec.get(key)
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"registry field {key!r} must be a non-empty string")
    return value


def string_list(spec: Mapping[str, object], key: str) -> list[str]:
    value = spec.get(key)
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise RuntimeError(
            f"registry field {key!r} must be a non-empty string list"
        )
    return value
