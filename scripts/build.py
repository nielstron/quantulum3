#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import defaultdict
import json
import sys

if not os.path.isdir('./quantulum3') or not os.path.exists('./README.md'):
    print(
        "Script is not run from project root. Please try again after changing working directory."
    )
    exit(-1)

sys.path.append(os.path.abspath('.'))
from quantulum3 import load as l
'''
Build script, to be run before pushing changes if certain files are affected
Make sure to run this from the project root folder

Currently this includes:
    - quantulum3/common-words.txt
    - quantulum3/units.json
'''


def build_four_letter_words():
    # Read raw 4 letter file
    path = os.path.join(l.TOPDIR, 'common-words.txt')
    words = defaultdict(list)  # Collect words based on length
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            line = line.rstrip()
            # TODO don't do this comparison at every start up, use a build script
            if line not in l.ALL_UNITS and line not in l.UNIT_SYMBOLS:
                words[len(line)].append(line)
    # Create ready to parse json dict out of it
    buildfile = os.path.join(l.TOPDIR, 'common-words.json')
    with open(buildfile, 'w', encoding='utf-8') as file:
        json.dump(words, file)


if __name__ == "__main__":
    build_four_letter_words()
