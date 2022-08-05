# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "irissec"
  spec.version       = "0.1.0"
  spec.authors       = ["IrisSec"]
  spec.email         = ["irissec@pm.me"]

  spec.summary       = "IrisSec website."
  spec.homepage      = "http://irissec.xyz/"
  spec.license       = "MIT"

  spec.files         = `git ls-files -z`.split("\x0").select { |f| f.match(%r!^(assets|_layouts|_includes|_sass|LICENSE|README|_config\.yml)!i) }

  spec.add_runtime_dependency "jekyll", "~> 4.1"
end
