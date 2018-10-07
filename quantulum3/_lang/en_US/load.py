#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""

from builtins import open

# Standard library
import os
import json
from collections import defaultdict

# Dependencies
import inflect

# Quantulum
from ... import load
from . import lang

TOPDIR = os.path.dirname(__file__) or "."

PLURALS = inflect.engine()


################################################################################
def pluralize(singular, count=None):
    # TODO remove this, as soon as the correct plural branch is merges into inflect
    split = singular.split(' ')
    if 'per' in split:
        per = split.index('per')
        return ' '.join(
            [pluralize(' '.join(split[:per]), count)]
            + split[per:]
        )
    if len(split) >= 2 and split[-2] == 'degree':
        return ' '.join(
            split[:-2]
            + ['degrees']
            + split[-1:]
        )
    return PLURALS.plural(singular, count)


def number_to_words(number):
    return PLURALS.number_to_words(number)


################################################################################
def build_common_words():
    # Read raw 4 letter file
    path = os.path.join(TOPDIR, 'common-words.txt')
    words = defaultdict(list)  # Collect words based on length
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            line = line.rstrip()
            if line not in load.units(
                    lang).surfaces_all and line not in load.units(
                        lang).symbols:
                words[len(line)].append(line)
            plural = load.pluralize(line)
            if plural not in load.units(
                    lang).surfaces_all and plural not in load.units(
                        lang).symbols:
                words[len(plural)].append(plural)
    return words


################################################################################
def load_common_words():
    path = os.path.join(TOPDIR, 'common-words.json')
    dumped = {}
    try:
        with open(path, 'r', encoding='utf-8') as file:
            dumped = json.load(file)
    except OSError:  # pragma: no cover
        pass

    words = defaultdict(list)  # Collect words based on length
    for length, word_list in dumped.items():
        words[int(length)] = word_list
    return words


COMMON_WORDS = load_common_words()
