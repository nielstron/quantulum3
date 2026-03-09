#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from io import open

from quantulum3 import classifier
from quantulum3._lang.en_US import load

"""
Build script, to be run before pushing changes if certain files are affected
Make sure to run this from the project root folder

Currently this includes:
    - quantulum3/_lang/en_US/common-words.txt
    - quantulum3/_lang/en_US/common-words.json
    - quantulum3/_lang/en_US/clf.joblib
"""

if __name__ == "__main__":
    # Create ready to parse json dict out of common word list
    words = load.build_common_words()
    build_file = os.path.join(load.TOPDIR, "common-words.json")
    with open(build_file, "w", encoding="utf-8") as file:
        json.dump(words, file, sort_keys=True, separators=(",", ":"))

    # Rebuild the packaged classifier artifact used for disambiguation.
    classifier.train_classifier(store=True, lang="en_US")
