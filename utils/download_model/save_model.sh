#!/bin/bash
set -e
save_location="saved_model"
docker build --build-arg MODEL_LOCATION=$save_location -t download_model_img .
docker run --rm -v $(pwd):/$save_location download_model_img cp -r $save_location /$save_location
cp -r $save_location ../../src/service_tier



