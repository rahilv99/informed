#!/bin/bash
set -e

# Build and Public Lambda Layer
pushd src/service_tier/layer
docker build -t build-layer .
popd
docker run --rm -v $(pwd)/output:/output build-layer cp /build/layer.zip /output



