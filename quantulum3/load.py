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
import re

# Dependencies
import inflect

# Quantulum
from . import classes as c

TOPDIR = os.path.dirname(__file__) or "."

PLURALS = inflect.engine()

METRIC_PREFIXES = {
    'Y': 'yotta',
    'Z': 'zetta',
    'E': 'exa',
    'P': 'peta',
    'T': 'tera',
    'G': 'giga',
    'M': 'mega',
    'k': 'kilo',
    'h': 'hecto',
    'da': 'deca',
    'd': 'deci',
    'c': 'centi',
    'm': 'milli',
    'µ': 'micro',
    'n': 'nano',
    'p': 'pico',
    'f': 'femto',
    'a': 'atto',
    'z': 'zepto',
    'y': 'yocto',
    'Ki': 'kibi',
    'Mi': 'mebi',
    'Gi': 'gibi',
    'Ti': 'tebi',
    'Pi': 'pebi',
    'Ei': 'exbi',
    'Zi': 'zebi',
    'Yi': 'yobi'
}


def get_string_json(raw_json_text):
    text = raw_json_text
    text = bytes(text, 'utf-8').decode('ascii', 'ignore')
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text


################################################################################
def get_key_from_dimensions(derived):
    """
    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT dicts.
    """

    return tuple((i['base'], i['power']) for i in derived)


################################################################################
def get_dimension_permutations(entities, derived):
    """
    Get all possible dimensional definitions for an entity.
    """

    new_derived = defaultdict(int)
    for item in derived:
        new = entities[item['base']].dimensions
        if new:
            for new_item in new:
                new_derived[new_item['base']] += (
                    new_item['power'] * item['power'])
        else:
            new_derived[item['base']] += item['power']

    final = [[{
        'base': i[0],
        'power': i[1]
    } for i in list(new_derived.items())], derived]
    final = [sorted(i, key=lambda x: x['base']) for i in final]

    candidates = []
    for item in final:
        if item not in candidates:
            candidates.append(item)

    return candidates


################################################################################
def load_entities():
    """
    Load entities from JSON file.
    """

    path = os.path.join(TOPDIR, 'entities.json')
    string_json = ''.join(open(path, encoding='utf-8').readlines())
    string_json = get_string_json(string_json)
    entities = json.loads(string_json)
    names = [i['name'] for i in entities]

    try:
        assert len(set(names)) == len(entities)
    except AssertionError:  # pragma: no cover
        raise Exception('Entities with same name: %s' %
                        [i for i in names if names.count(i) > 1])

    entities = dict(
        (k['name'],
         c.Entity(name=k['name'], dimensions=k['dimensions'], uri=k['URI']))
        for k in entities)

    derived_ent = defaultdict(list)
    for ent in entities:
        if not entities[ent].dimensions:
            continue
        perms = get_dimension_permutations(entities, entities[ent].dimensions)
        for perm in perms:
            key = get_key_from_dimensions(perm)
            derived_ent[key].append(entities[ent])

    return entities, derived_ent


ENTITIES, DERIVED_ENT = load_entities()


################################################################################
def get_derived_units(names):
    """
    Create dictionary of unit dimensions.
    """

    derived_uni = {}

    for name in names:
        key = get_key_from_dimensions(names[name].dimensions)
        derived_uni[key] = names[name]
        plain_derived = [{'base': name, 'power': 1}]
        key = get_key_from_dimensions(plain_derived)
        derived_uni[key] = names[name]
        if not names[name].dimensions:
            names[name].dimensions = plain_derived
        names[name].dimensions = [{
            'base': names[i['base']].name,
            'power': i['power']
        } for i in names[name].dimensions]

    return derived_uni


################################################################################
def load_units():
    """
    Load units from JSON file.
    """

    names = {}
    unit_symbols, unit_symbols_lower, = defaultdict(list), defaultdict(list)
    surfaces, lowers, symbols = defaultdict(list), defaultdict(
        list), defaultdict(list)

    path = os.path.join(TOPDIR, 'units.json')
    string_json = ''.join(open(path, encoding='utf-8').readlines())
    for unit in json.loads(string_json):
        load_unit(unit, names, unit_symbols, unit_symbols_lower, surfaces,
                  lowers, symbols)

    derived_uni = get_derived_units(names)

    return names, unit_symbols, unit_symbols_lower, surfaces, lowers, symbols, derived_uni


def load_unit(unit, names, unit_symbols, unit_symbols_lower, surfaces, lowers,
              symbols):
    try:
        assert unit['name'] not in names
    except AssertionError:  # pragma: no cover
        msg = 'Two units with same name in units.json: %s' % unit['name']
        raise Exception(msg)

    obj = c.Unit(
        name=unit['name'],
        surfaces=unit['surfaces'],
        entity=ENTITIES[unit['entity']],
        uri=unit['URI'],
        symbols=unit['symbols'],
        dimensions=unit['dimensions'],
        currency_code=unit.get('currency_code'))

    names[unit['name']] = obj

    for symbol in unit['symbols']:
        unit_symbols[symbol].append(obj)
        unit_symbols_lower[symbol.lower()].append(obj)
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
            plural = ' '.join([
                i if num != index else PLURALS.plural(split[index])
                for num, i in enumerate(split)
            ])
        else:
            plural = PLURALS.plural(surface)
        if plural != surface:
            surfaces[plural].append(obj)
            lowers[plural.lower()].append(obj)

    # If SI-prefixes are given, add them
    if unit.get('prefixes'):
        for prefix in unit['prefixes']:
            try:
                assert prefix in METRIC_PREFIXES
            except AssertionError:  # pragma: no cover
                raise Exception(
                    "Given prefix '{}' for unit '{}' not supported".format(
                        prefix, unit['name']))
            try:
                assert len(unit['dimensions']) <= 1
            except AssertionError:  # pragma: no cover
                raise Exception(
                    "Prefixing not supported for multiple dimensions in {}".
                    format(unit['name']))

            uri = unit['URI']
            slash_position = uri.rfind('/') + 1
            uri = uri[:slash_position] + METRIC_PREFIXES[prefix].capitalize(
            ) + uri[slash_position:].lower()

            prefixed_unit = {
                'name':
                METRIC_PREFIXES[prefix] + unit['name'],
                'surfaces':
                [METRIC_PREFIXES[prefix] + i for i in unit['surfaces']],
                'entity':
                unit['entity'],
                'URI':
                uri,
                'dimensions': [],
                'symbols': [prefix + i for i in unit['symbols']]
            }
            load_unit(prefixed_unit, names, unit_symbols, unit_symbols_lower,
                      surfaces, lowers, symbols)


NAMES, UNIT_SYMBOLS, UNIT_SYMBOLS_LOWER, UNITS, LOWER_UNITS, PREFIX_SYMBOLS, \
    DERIVED_UNI = load_units()
ALL_UNIT_SYMBOLS = {}
ALL_UNIT_SYMBOLS.update(UNIT_SYMBOLS)
ALL_UNIT_SYMBOLS.update(UNIT_SYMBOLS_LOWER)
ALL_UNITS = {}
ALL_UNITS.update(UNITS)
ALL_UNITS.update(LOWER_UNITS)

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
            if line not in ALL_UNITS and line not in UNIT_SYMBOLS:
                words[len(line)].append(line)
                words[len(line)].append(PLURALS.plural(line))
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
