#!/usr/bin/env bash

# Bash script to run before pushing changes to dev branch
yapf -i -r .
pandoc README.md -o README.rst
