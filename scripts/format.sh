#!/usr/bin/env bash

# Bash script to run before pushing changes to dev branch
# Run from git directory root
# TODO make this a python file
autopep8 -i -r .
yapf -i -r .
