# brew-api-extra

Additional Homebrew Cask metadata for
[brew-nix](https://github.com/BatteredBunny/brew-nix).

The upstream `brew-api` project mirrors the official Homebrew Cask API. This
repository supplies the same JSON shape for applications that are distributed
through third-party taps.

## Included casks

- `motrix-next` from
  [`AnInsomniacy/motrix-next`](https://github.com/AnInsomniacy/homebrew-motrix-next)

## Updates

The update workflow reads the upstream cask without evaluating its Ruby code,
validates its version, URLs, application name, and SHA-256 values, and rewrites
`cask.json` only when the metadata changes.

Consumers should pin this repository as a non-flake input and update that input
through their normal `nix flake update` workflow.
