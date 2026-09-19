# brew-api-extra

Additional Homebrew Cask metadata for
[brew-nix](https://github.com/BatteredBunny/brew-nix).

The upstream `brew-api` project mirrors the official Homebrew Cask API. This
repository supplies the same JSON shape for applications that are distributed
through third-party taps.

## Included casks

- `rayburst` 4.0.0-beta.2 from the pinned
  [official release](https://github.com/AnInsomniacy/rayburst/releases/tag/v4.0.0-beta.2).
  The upstream Homebrew tap currently describes beta.1, so the narrow
  `github-release-arch-app` adapter reads the explicitly selected beta.2
  release's architecture-specific updater archives and SHA-256 digests.
  Prereleases require explicit registry opt-in. This entry stays pinned until
  a reviewed registry change advances it or returns it to the upstream cask
  adapter; the daily job does not follow future betas automatically.
- `motrix-next` 3.9.8 remains available for existing consumers. Its cask source
  is pinned before the upstream rename because the old path was deleted.
  The existing generated metadata and package identity are unchanged.

Rayburst is the renamed Motrix Next application, with a new bundle identifier.
Upstream does not migrate settings, tasks, or history; keep downloaded files
and select only one of the two applications in the consumer configuration.

## Repository layout

- `registry/*.json` selects an upstream cask and a parser adapter.
- `scripts/adapters/` contains constrained parsers for supported cask layouts.
- `scripts/update.py` combines all registry entries into a stable `cask.json`.
- `flake.nix` pins the Python maintainer environment and command entry points.
- `tests/` verifies the adapters without using the network.

The adapters read the upstream cask without evaluating its Ruby code. They
validate the version, URLs, application name, and SHA-256 values before
emitting metadata. The pinned-release adapter also rejects drafts, mismatched
tags or repositories, duplicate/missing architecture assets, invalid digests,
and oversized assets. Metadata downloads are bounded and reject cross-host
or insecure redirects. Publication rejects downgrades and same-version
artifact mutations and replaces the generated catalog atomically.
Add a registry entry when an existing adapter matches the
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
