# brew-api-extra

Additional Homebrew Cask metadata for
[brew-nix](https://github.com/BatteredBunny/brew-nix).

The upstream `brew-api` project mirrors the official Homebrew Cask API. This
repository supplies the same JSON shape for applications that are distributed
through third-party taps.

## Included casks

- `motrix-next` from
  [`AnInsomniacy/motrix-next`](https://github.com/AnInsomniacy/homebrew-motrix-next)

## Repository layout

- `registry/*.json` selects an upstream cask and a parser adapter.
- `scripts/adapters/` contains constrained parsers for supported cask layouts.
- `scripts/update.py` combines all registry entries into a stable `cask.json`.
- `flake.nix` pins the Python maintainer environment and command entry points.
- `tests/` verifies the adapters without using the network.

The adapters read the upstream cask without evaluating its Ruby code. They
validate the version, URLs, application name, and SHA-256 values before
emitting metadata. Add a registry entry when an existing adapter matches the
upstream cask; add a purpose-built adapter when its layout differs.

Run the deterministic offline checks with the locked Python 3.14 environment:

```sh
nix run --no-update-lock-file .#maintainer-check
```

Regenerate the catalog from upstream sources with:

```sh
nix run --no-update-lock-file .#update-casks
```

The update command requires network access and may write `cask.json`. Its
read-only freshness mode is:

```sh
nix run --no-update-lock-file .#update-casks -- --check
```

For an interactive shell using exactly the same locked tools:

```sh
nix develop --no-update-lock-file .#maintainer
```

The flake exports the explicit `maintainer` development shell (also used as the
default shell) and both command entry points for `aarch64-darwin` and
`x86_64-linux`. Python 3.9 is the minimum compatibility target and Python 3.14
is the current maintainer version. Pull requests and pushes test both versions
explicitly, while scheduled updates run only through the locked Nix entry
point. If future adapters require Node.js, Ruby, or another runtime, add it to
this repository's flake and entry point instead of relying on a maintainer's
global `PATH`.

## Updates

The daily 05:17 UTC scheduled workflow regenerates the complete catalog and
commits `cask.json` only when upstream metadata changes. Pull requests and
ordinary pushes are read-only and cannot publish catalog updates.

Consumers should pin this repository as a non-flake input and update that input
through their normal `nix flake update` workflow.
