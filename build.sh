#!/usr/bin/env bash

# This script is meant to be run to publish the changes in dev branch to master branch

git checkout master
git merge dev

# Script to run before pushing merged dev branch
sed -i -e 's/https:\/\/travis-ci\.com\/nielstron\/quantulum3.svg?branch=dev/https:\/\/travis-ci\.com\/nielstron\/quantulum3.svg?branch=master/g' README.md
sed -i -e 's/https:\/\/landscape.io\/github\/nielstron\/quantulum3\/dev/https:\/\/landscape.io\/github\/nielstron\/quantulum3\/master/g' README.md
pandoc README.md -o README.rst

git add .
git commit --amend --no-edit
git checkout dev