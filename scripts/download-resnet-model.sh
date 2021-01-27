#!/bin/sh

# Abort on any error
set -x

# Download Resnet model
mkdir -p data/resnet && \
	cd data/resnet && \
	curl -L -o resnet50_v1_model.pb https://www.dropbox.com/s/icr8tftv7i4zdpd/ssd_resnet50_v1_2018_07_03.pb?dl=1
