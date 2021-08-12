#!/bin/sh

# Make the directory for storing images
mkdir -p Images
mkdir -p SelectedImages
cd Images

# Download the train and val images
echo "Downloading images"
curl -o train.zip https://ivc.ischool.utexas.edu/VizWiz_final/images/train.zip
curl -o val.zip https://ivc.ischool.utexas.edu/VizWiz_final/images/val.zip

# Unzip
echo "Unzipping images"
unzip train.zip
unzip val.zip

# Move the images so they're all in the same directory
echo "Moving images"
mv val/* .
mv train/* .
rm -rf val
rm -rf train
cd ../

# Download the annotations
echo "Downloading annotation data"
curl -o Annotations.zip https://ivc.ischool.utexas.edu/VizWiz_final/vqa_data/Annotations.zip

# Unzip
echo "Unzipping annotation data"
unzip Annotations.zip

cd ../
echo "Done"