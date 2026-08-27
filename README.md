# brew-api-extra

Additional Homebrew Cask metadata for
[brew-nix](https://github.com/BatteredBunny/brew-nix).

The upstream `brew-api` project mirrors the official Homebrew Cask API. This
repository supplies the same JSON shape for applications that are distributed
through third-party taps.

## Included casks

- `motrix-next` from
  [`AnInsomniacy/motrix-next`](https://github.com/AnInsomniacy/homebrew-motrix-next)
- `tinycast` from
  [`abue-ammar/tinycast`](https://github.com/abue-ammar/homebrew-tinycast)

## Repository layout

- `registry/*.json` selects an upstream cask and a parser adapter.
- `scripts/adapters/` contains constrained parsers for supported cask layouts.
- `scripts/update.py` combines all registry entries into a stable `cask.json`.
- `tests/` verifies the adapters without using the network.

The adapters read the upstream cask without evaluating its Ruby code. They
validate the version, URLs, application name, and SHA-256 values before
emitting metadata. Add a registry entry when an existing adapter matches the
upstream cask; add a purpose-built adapter when its layout differs.

Generate and test the catalog with:

```sh
python3 -m unittest discover -s tests
python3 -m scripts.update
```

## Updates

The scheduled workflow regenerates the complete catalog and commits
`cask.json` only when upstream metadata changes.

Consumers should pin this repository as a non-flake input and update that input
through their normal `nix flake update` workflow.
