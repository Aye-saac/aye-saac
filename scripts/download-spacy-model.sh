#!/bin/sh

# Abort on any error
set -x

python -m spacy download en_core_web_md && \
python -m spacy link en_core_web_md en
