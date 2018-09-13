#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Train the disambiguator '''

import sys
import os

if not os.path.isdir('./quantulum3') or not os.path.exists('./README.md'):
    print(
        "Script is not run from project root. Please try again after changing working directory."
    )
    exit(-1)

sys.path.append(os.path.abspath('.'))

from quantulum3.classifier import train_classifier, download_wiki

download_wiki(store=True)
train_classifier(download=False, store=True)
