#!/usr/bin/env bash

# Bash script to run before pushing changes to dev branch
# Run from git directory root
# TODO make this a python file
SOURCES="quantulum3 scripts setup.py"
yapf -i -r ${SOURCES}
autopep8 -i -r ${SOURCES}
