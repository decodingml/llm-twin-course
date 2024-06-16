group "default" {
  targets = ["bytewax", "cdc"]
}

target "bytewax" {
  context = "."
  dockerfile = ".docker/Dockerfile.bytewax"
}

target "cdc" {
  context = "."
  dockerfile = ".docker/Dockerfile.cdc"
}
