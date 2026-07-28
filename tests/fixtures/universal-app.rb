cask "example-app" do
  version "2.4.1"
  sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

  url "https://downloads.example.com/Example-#{version}.zip"
  name "Example App"
  desc "Example universal application"
  homepage "https://example.com/"

  app "Example.app"
end
