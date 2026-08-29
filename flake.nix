{
  description = "Maintainer environment for brew-api-extra";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "aarch64-darwin"
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      packagesFor = system: import nixpkgs { inherit system; };
      commandsFor =
        pkgs:
        let
          python = pkgs.python314;
        in
        rec {
          maintainerCheck = pkgs.writeShellApplication {
            name = "brew-api-extra-maintainer-check";
            runtimeInputs = [
              pkgs.gitMinimal
              python
              pkgs.yq-go
            ];
            text = ''
              export PYTHONDONTWRITEBYTECODE=1
              export PYTHONNOUSERSITE=1

              if [[ ! -f cask.json || ! -d registry || ! -d tests ]]; then
                echo "run maintainer-check from the brew-api-extra repository root" >&2
                exit 2
              fi

              ${python}/bin/python3 -m unittest discover -s tests
              ${python}/bin/python3 -m scripts.check_catalog
              ${pkgs.yq-go}/bin/yq eval '.' .github/workflows/*.yml >/dev/null
              ${pkgs.gitMinimal}/bin/git diff --check
            '';
          };

          updateCasks = pkgs.writeShellApplication {
            name = "brew-api-extra-update-casks";
            runtimeInputs = [ python ];
            text = ''
              export PYTHONDONTWRITEBYTECODE=1
              export PYTHONNOUSERSITE=1

              if [[ ! -f cask.json || ! -d registry ]]; then
                echo "run update-casks from the brew-api-extra repository root" >&2
                exit 2
              fi

              exec ${python}/bin/python3 -m scripts.update "$@"
            '';
          };
        };
    in
    {
      apps = forAllSystems (
        system:
        let
          commands = commandsFor (packagesFor system);
        in
        {
          maintainer-check = {
            type = "app";
            program = "${commands.maintainerCheck}/bin/brew-api-extra-maintainer-check";
          };
          update-casks = {
            type = "app";
            program = "${commands.updateCasks}/bin/brew-api-extra-update-casks";
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = packagesFor system;
          python = pkgs.python314;
        in
        {
          maintainer-check =
            pkgs.runCommand "brew-api-extra-maintainer-check"
              {
                nativeBuildInputs = [
                  python
                  pkgs.yq-go
                ];
                PYTHONDONTWRITEBYTECODE = "1";
                PYTHONNOUSERSITE = "1";
                src = self;
              }
              ''
                cp -R "$src" source
                chmod -R u+w source
                cd source
                ${python}/bin/python3 -m unittest discover -s tests
                ${python}/bin/python3 -m scripts.check_catalog
                ${pkgs.yq-go}/bin/yq eval '.' .github/workflows/*.yml >/dev/null
                touch "$out"
              '';
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = packagesFor system;
          maintainerShell = pkgs.mkShellNoCC {
            packages = [
              pkgs.gitMinimal
              pkgs.python314
              pkgs.yq-go
            ];
            shellHook = ''
              export PYTHONDONTWRITEBYTECODE=1
              export PYTHONNOUSERSITE=1
            '';
          };
        in
        {
          maintainer = maintainerShell;
          default = maintainerShell;
        }
      );

      formatter = forAllSystems (system: (packagesFor system).nixfmt-tree);
    };
}
