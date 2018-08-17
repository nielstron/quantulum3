#!/usr/bin/env bash

# This script is meant to be run to publish the changes in dev branch to master branch

git checkout master
git rebase dev
