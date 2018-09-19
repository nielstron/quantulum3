#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from collections import defaultdict
import json

from quantulum3 import load as l
'''
Build script, to be run before pushing changes if certain files are affected
Make sure to run this from the project root folder

Currently this includes:
    - quantulum3/common-words.txt
    - quantulum3/units.json
'''

if __name__ == "__main__":
    # Create ready to parse json dict out of common word list
    words = l.build_common_words()
    buildfile = os.path.join(l.TOPDIR, 'common-words.json')
    with open(buildfile, 'w', encoding='utf-8') as file:
        json.dump(words, file)
