#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:mod:`Quantulum` unit and entity loading functions.
'''

# Standard library
import os
import json
from collections import defaultdict

# Dependences
import inflect

# Quantulum
from . import classes as c

TOPDIR = os.path.dirname(__file__) or "."

PLURALS = inflect.engine()

################################################################################
def get_key_from_dimensions(derived):

    '''
    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT dicts.
    '''

    return tuple(tuple(i.items()) for i in derived)


################################################################################
def get_dimension_permutations(entities, derived):

    '''
    Get all possible dimensional definitions for an entity.
    '''

    new_derived = defaultdict(int)
    for item in derived:
        new = entities[item['base']].derived
        if new:
            for new_item in new:
                new_derived[new_item['base']] += new_item['power'] * \
                                                 item['power']
        else:
            new_derived[item['base']] += item['power']

    final = [[{'base': i[0], 'power': i[1]} for i in new_derived.items()]]
    final.append(derived)
    final = [sorted(i, key=lambda x: x['base']) for i in final]

    candidates = []
    for item in final:
        if item not in candidates:
            candidates.append(item)

    return candidates


################################################################################
def load_entities():

    '''
    Load entities from JSON file.
    '''

    path = os.path.join(TOPDIR, 'entities.json')
    entities = json.load(open(path))
    names = [i['name'] for i in entities]

    try:
        assert len(set(names)) == len(entities)
    except AssertionError:
        raise Exception('Entities with same name: %s' % [i for i in names if \
                         names.count(i) > 1])

    entities = dict((k['name'], c.Entity(name=k['name'], derived=k['derived'],
                                         uri=k['URI'])) for k in entities)

    derived_ent = defaultdict(list)
    for ent in entities:
        if not entities[ent].derived:
            continue
        perms = get_dimension_permutations(entities, entities[ent].derived)
        for perm in perms:
            key = get_key_from_dimensions(perm)
            derived_ent[key].append(entities[ent])

    return entities, derived_ent

ENTITIES, DERIVED_ENT = load_entities()

################################################################################
def get_derived_units(names):

    '''
    Create dictionary of unit dimensions.
    '''

    derived_uni = {}

    for name in names:
        key = get_key_from_dimensions(names[name].derived)
        derived_uni[key] = names[name]
        plain_derived = [{'base': name, 'power': 1}]
        key = get_key_from_dimensions(plain_derived)
        derived_uni[key] = names[name]
        if not names[name].derived:
            names[name].derived = plain_derived
        names[name].derived = [{'base': names[i['base']].name,
                                'power': i['power']} for i in \
                                 names[name].derived]

    return derived_uni


################################################################################
def load_units():

    '''
    Load units from JSON file.
    '''

    names = {}
    surfaces, lowers, symbols = defaultdict(list), defaultdict(list), \
                                defaultdict(list)

    for unit in json.load(open(os.path.join(TOPDIR, 'units.json'))):

        try:
            assert unit['name'] not in names
        except AssertionError:
            msg = 'Two units with same name in units.json: %s' % unit['name']
            raise Exception(msg)

        obj = c.Unit(name=unit['name'], surfaces=unit['surfaces'],
                     entity=ENTITIES[unit['entity']], uri=unit['URI'],
                     symbols=unit['symbols'], derived=unit['derived'])

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
                plural = ' '.join([i if num != index else \
                         PLURALS.plural(split[index]) for num, i in \
                         enumerate(split)])
            else:
                plural = PLURALS.plural(surface)
            if plural != surface:
                surfaces[plural].append(obj)
                lowers[plural.lower()].append(obj)

    derived_uni = get_derived_units(names)

    return names, surfaces, lowers, symbols, derived_uni

NAMES, UNITS, LOWER_UNITS, SYMBOLS, DERIVED_UNI = load_units()
