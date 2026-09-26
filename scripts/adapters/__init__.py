"""Safe, purpose-built adapters for supported Homebrew Cask layouts."""

from .homebrew_app import build as build_homebrew_app
from .homebrew_arch_app import build as build_homebrew_arch_app
from .homebrew_arm_app import build as build_homebrew_arm_app
from .github_release_arch_app import build as build_github_release_arch_app

ADAPTERS = {
    "homebrew-app": build_homebrew_app,
    "homebrew-arch-app": build_homebrew_arch_app,
    "homebrew-arm-app": build_homebrew_arm_app,
    "github-release-arch-app": build_github_release_arch_app,
}

__all__ = ["ADAPTERS"]
