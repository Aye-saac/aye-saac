#!/bin/sh

# Abort on any error
set -x

# Download COCO Resnet model
mkdir -p data/coco_resnet && \
	cd data/coco_resnet && \
	curl -L -o saved_model.pb https://www.dropbox.com/s/icr8tftv7i4zdpd/ssd_resnet50_v1_2018_07_03.pb?dl=1
