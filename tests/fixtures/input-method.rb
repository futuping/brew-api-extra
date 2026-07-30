cask "example-input-method" do
  version "2.2.2,643"
  sha256 "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"

  url "https://downloads.example.com/#{version.csv.first}/Example_#{version.csv.first}_#{version.csv.second}.zip"
  name "Example Input Method"
  desc "Example input method"
  homepage "https://example.com/"

  input_method "Example.app"
end
