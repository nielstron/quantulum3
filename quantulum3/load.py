#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""quantulum3 unit and entity loading functions."""

from builtins import open

# Standard library
import os
import json
from collections import defaultdict

# Dependencies
import inflect

# Quantulum
from . import classes as c

TOPDIR = os.path.dirname(__file__) or "."

PLURALS = inflect.engine()


###############################################################################
def get_key_from_dimensions(dimensions):
    """
    Get a key for DERIVED_UNI or DERIVED_ENT.

    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT
    dictionaries.
    """
    return tuple(tuple(i.items()) for i in dimensions)


###############################################################################
def get_dimension_permutations(entities, dimensions):
    """Get all possible dimensional definitions for an entity."""
    new_dimensions = defaultdict(int)
    for item in dimensions:
        new = entities[item['base']].dimensions
        if new:
            for new_item in new:
                new_dimensions[new_item['base']] += new_item['power'] * \
                                                 item['power']
        else:
            new_dimensions[item['base']] += item['power']

    final = [[{'base': i[0], 'power': i[1]} for i in new_dimensions.items()]]
    final.append(dimensions)
    final = [sorted(i, key=lambda x: x['base']) for i in final]

    candidates = []
    for item in final:
        if item not in candidates:
            candidates.append(item)

    return candidates


###############################################################################
def load_entities():
    """Load entities from JSON file."""
    path = os.path.join(TOPDIR, 'entities.json')
    entities = json.load(open(path, encoding='UTF-8'))
    names = [i['name'] for i in entities]

    try:
        assert len(set(names)) == len(entities)
    except AssertionError:
        raise Exception('Entities with same name: %s' % [i for i in names if
                                                         names.count(i) > 1])

    entities = dict((k['name'], c.Entity(name=k['name'],
                                         dimensions=k['dimensions'],
                                         uri=k['URI'])) for k in entities)

    dimensions_ent = defaultdict(list)
    for ent in entities:
        if not entities[ent].dimensions:
            continue
        perms = get_dimension_permutations(entities, entities[ent].dimensions)
        for perm in perms:
            key = get_key_from_dimensions(perm)
            dimensions_ent[key].append(entities[ent])

    return entities, dimensions_ent

ENTITIES, DERIVED_ENT = load_entities()


###############################################################################
def get_dimensions_units(names):
    """Create dictionary of unit dimensions."""
    dimensions_uni = {}

    for name in names:

        key = get_key_from_dimensions(names[name].dimensions)
        dimensions_uni[key] = names[name]
        plain_dimensions = [{'base': name, 'power': 1}]
        key = get_key_from_dimensions(plain_dimensions)
        dimensions_uni[key] = names[name]

        if not names[name].dimensions:
            names[name].dimensions = plain_dimensions

        names[name].dimensions = [{'base': names[i['base']].name,
                                   'power': i['power']} for i in
                                  names[name].dimensions]

    return dimensions_uni


###############################################################################
def load_units():
    """Load units from JSON file."""
    names = {}
    lowers = defaultdict(list)
    symbols = defaultdict(list)
    surfaces = defaultdict(list)
    for unit in json.load(open(os.path.join(TOPDIR, 'units.json'), encoding='UTF-8')):

        try:
            assert unit['name'] not in names
        except AssertionError:
            msg = 'Two units with same name in units.json: %s' % unit['name']
            raise Exception(msg)

        obj = c.Unit(name=unit['name'], surfaces=unit['surfaces'],
                     entity=ENTITIES[unit['entity']], uri=unit['URI'],
                     symbols=unit['symbols'], dimensions=unit['dimensions'])

        names[unit['name']] = obj

        for symbol in unit['symbols']:
            surfaces[symbol].append(obj)
            lowers[symbol.lower()].append(obj)
            if unit['entity'] == 'currency':
                symbols[symbol].append(obj)

        for surface in unit['surfaces']:
            surfaces[surface].append(obj)
            lowers[surface.lower()].append(obj)
            split = surface.split()
            index = None
            if ' per ' in surface:
                index = split.index('per') - 1
            elif 'degree ' in surface:
                index = split.index('degree')
            if index is not None:
                plural = ' '.join([i if num != index else
                                   PLURALS.plural(split[index]) for num, i in
                                   enumerate(split)])
            else:
                plural = PLURALS.plural(surface)
            if plural != surface:
                surfaces[plural].append(obj)
                lowers[plural.lower()].append(obj)

    dimensions_uni = get_dimensions_units(names)

    return names, surfaces, lowers, symbols, dimensions_uni

NAMES, UNITS, LOWER_UNITS, SYMBOLS, DERIVED_UNI = load_units()
