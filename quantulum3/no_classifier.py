# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions when no classifier is available
"""
from __future__ import division

# Standard library
import json
import os
from io import open

# Quantulum
from . import load


def disambiguate_no_classifier(entities, text):
    """
    Disambiguate the entity or unit without a classifier
    :param entities:
    :param text:
    :return: a single entity or unit that has been chosen for
    """
    paths = [
        os.path.join(load.TOPDIR, filename)
        for filename in ['similars.json', 'wiki.json', 'train.json']
    ]
    word_sets = []
    for path in paths:
        with open(path, encoding='utf-8') as file:
            word_sets += json.load(file)
    max_entity, max_count, max_relative = None, 0, 0
    for entity in entities:
        count = 0
        total = 0
        for word_set in word_sets:
            if word_set['unit'] == entity.name:
                total += len(word_set['text'])
                for word in word_set['text'].split(' '):
                    count += 1 if word in text else 0
        try:
            relative = count / total
        except ZeroDivisionError:
            relative = 0
        if relative > max_relative or (relative == max_relative
                                       and count > max_count):
            max_entity, max_count, max_relative = entity, count, relative
    return max_entity
