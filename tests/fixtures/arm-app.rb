cask "search" do
  version "1.0.3"
  sha256 "a30bc15d4e619ff9d2038886d7bc30f80721dede806bd4a03d4653402deeb6ef"

  url "https://github.com/driceroland/Search/releases/download/v#{version}/Search.dmg"
  name "Search"
  desc "Browser with nothing in the way"
  homepage "https://officecommun.com/search"

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Search.app"
end
