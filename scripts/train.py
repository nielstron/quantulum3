#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Train the disambiguator '''

import sys
import os

from quantulum3.classifier import train_classifier

train_classifier(download=False, store=True)
