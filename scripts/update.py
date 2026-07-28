#!/usr/bin/env python3

import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

CASK_URL = (
    "https://raw.githubusercontent.com/"
    "AnInsomniacy/homebrew-motrix-next/main/Casks/motrix-next.rb"
)
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "cask.json"
INTEL_VARIATIONS = (
    "golden_gate",
    "tahoe",
    "sequoia",
    "sonoma",
    "ventura",
    "monterey",
    "big_sur",
    "catalina",
)


def match(pattern: str, source: str, label: str) -> str:
    result = re.search(pattern, source, re.MULTILINE)
    if result is None:
        raise RuntimeError(f"unable to parse {label} from upstream cask")
    return result.group(1)


request = urllib.request.Request(
    CASK_URL,
    headers={"User-Agent": "futuping/brew-api-extra"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    cask = response.read().decode("utf-8")

version = match(r'^\s*version\s+"([^"]+)"', cask, "version")
arm_sha256 = match(r'^\s*sha256\s+arm:\s+"([0-9a-f]{64})"', cask, "ARM SHA-256")
intel_sha256 = match(
    r'^\s*intel:\s+"([0-9a-f]{64})"',
    cask,
    "Intel SHA-256",
)
url_template = match(r'^\s*url\s+"([^"]+)"', cask, "URL")
name = match(r'^\s*name\s+"([^"]+)"', cask, "name")
description = match(r'^\s*desc\s+"([^"]+)"', cask, "description")
homepage = match(r'^\s*homepage\s+"([^"]+)"', cask, "homepage")
application = match(r'^\s*app\s+"([^"]+\.app)"', cask, "application")

if "#{version}" not in url_template or "#{arch}" not in url_template:
    raise RuntimeError("upstream URL no longer uses the expected version/arch template")


def release_url(architecture: str) -> str:
    url = url_template.replace("#{version}", version).replace(
        "#{arch}",
        architecture,
    )
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise RuntimeError(f"unexpected release URL: {url}")
    return url


intel = {
    "url": release_url("x64"),
    "sha256": intel_sha256,
}
metadata = [
    {
        "token": "motrix-next",
        "full_token": "motrix-next",
        "name": [name],
        "desc": description,
        "homepage": homepage,
        "url": release_url("aarch64"),
        "version": version,
        "sha256": arm_sha256,
        "artifacts": [{"app": [application]}],
        "auto_updates": True,
        "variations": {
            variation: intel.copy() for variation in INTEL_VARIATIONS
        },
    }
]

rendered = json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered:
    print(f"{OUTPUT.name} is already current ({version})")
else:
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"updated {OUTPUT.name} to {version}")
