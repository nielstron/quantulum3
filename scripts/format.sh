#!/usr/bin/env bash

# Bash script to run before pushing changes to dev branch
# TODO make this a python file
yapf -i -r .
pandoc README.md -o README.rst
