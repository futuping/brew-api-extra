"""Safe, purpose-built adapters for supported Homebrew Cask layouts."""

from .homebrew_app import build as build_homebrew_app
from .homebrew_arch_app import build as build_homebrew_arch_app
from .homebrew_input_method_app import build as build_homebrew_input_method_app

ADAPTERS = {
    "homebrew-app": build_homebrew_app,
    "homebrew-arch-app": build_homebrew_arch_app,
    "homebrew-input-method-app": build_homebrew_input_method_app,
}

__all__ = ["ADAPTERS"]
