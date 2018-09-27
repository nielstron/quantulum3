#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract the n nearest neighbours of the ambigous units from the word2vec file
"""
import sys
import os
import json
from io import open

from quantulum3 import classifier, classes, load

TOPDIR = os.path.dirname(__file__) or '.'
try:
    n = int(sys.argv[1])
except IndexError:
    n = 1000


def glove_via_magnitude(topn=500,
                        min_similarity=None,
                        filename='glove.6B.100d.magnitude'):

    from pymagnitude import Magnitude

    v = Magnitude(os.path.join(TOPDIR, filename))
    training_set = list()
    units = set()
    for unit_list in classifier.ambiguous_units():
        for unit in unit_list[1]:
            units.add(unit)
    for unit in units:
        print('Processing {}...'.format(unit.name))

        name = unit.name
        surfaces = set(unit.name)
        if isinstance(unit, classes.Unit):
            surfaces.update(unit.surfaces)
            surfaces.update(unit.symbols)
        for surface in surfaces:
            neighbours = v.most_similar(
                v.query(surface), topn=topn, min_similarity=min_similarity)
            training_set.append({
                'unit':
                name,
                'text':
                ' '.join(neighbour[0] for neighbour in neighbours)
            })
    print('Done')

    with open(
            os.path.join(load.TOPDIR, 'similars.json'), 'w',
            encoding='utf8') as file:
        json.dump(training_set, file, sort_keys=True, indent=4)


if __name__ == '__main__':
    glove_via_magnitude()
