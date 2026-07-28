cask "example-arch-app" do
  arch arm: "arm64",
       intel: "x86_64"

  version "3.1.4"
  sha256 arm:   "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
         intel: "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"

  url "https://github.com/example/project/releases/download/v#{version}/Example-#{arch}.zip"
  name "Example Arch App"
  desc "Example architecture-specific application"
  homepage "https://github.com/example/project"

  app "Example Arch.app"
end
