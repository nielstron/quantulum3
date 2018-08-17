#!/usr/bin/env bash

# Script to run before pushing merged dev branch
sed -i -e 's/https:\/\/travis-ci\.com\/nielstron\/quantulum3.svg?branch=dev/https:\/\/travis-ci\.com\/nielstron\/quantulum3.svg?branch=master/g' README.md
sed -i -e 's/https:\/\/landscape.io\/github\/nielstron\/quantulum3\/dev/https:\/\/landscape.io\/github\/nielstron\/quantulum3\/master/g' README.md
pandoc README.md -o README.rst
