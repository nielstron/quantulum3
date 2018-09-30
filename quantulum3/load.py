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
from pathlib import Path

# Quantulum
from . import classes as c
from . import language

TOPDIR = os.path.dirname(__file__) or "."

################################################################################
_CACHE_DICT = {}


def cached(funct):
    """
    Decorator for caching language specific data
    :param funct: the method, dynamically responding to language
    :return: the method, dynamically responding to language but also caching results
    """
    assert callable(funct)

    def cached_function(lang='en_US', *args, **kwargs):
        try:
            return _CACHE_DICT[id(funct)][lang]
        except KeyError:
            result = function(*args, lang=lang, **kwargs)
            _CACHE_DICT[id(funct)] = {lang: result}
            return result

    return cached_function


################################################################################
@cached
def _get_load(lang='en_US'):
    return language.get('load', lang)


################################################################################
def pluralize(singular, count=None, lang='en_US'):
    return _get_load(lang).pluralize(singular, count)


def number_to_words(count, lang='en_US'):
    return _get_load(lang).pluralize(count)


################################################################################
def get_string_json(raw_json_text):
    text = raw_json_text
    text = bytes(text, 'utf-8').decode('ascii', 'ignore')
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text


################################################################################
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

    derived_ent = defaultdict(set)
    for ent in entities:
        if not entities[ent].dimensions:
            continue
        perms = get_dimension_permutations(entities, entities[ent].dimensions)
        for perm in perms:
            key = get_key_from_dimensions(perm)
            derived_ent[key].add(entities[ent])

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
class Units(object):
    def __init__(self, lang='en_US'):
        """
        Load units from JSON file.
        """
        self.lang = lang

        # names of all units
        self.names = {}
        self.symbols, self.symbols_lower = defaultdict(set), defaultdict(set)
        self.surfaces, self.surfaces_lower = defaultdict(set), defaultdict(set)
        self.prefix_symbols = defaultdict(set)

        # Load general units
        path = os.path.join(TOPDIR, 'units.json')
        with open(path, encoding='utf-8') as file:
            general_units = json.load(file)
        # load language specifics
        path = os.path.join(language.get('load', lang).TOPDIR, 'units.json')
        with open(path, encoding='utf-8') as file:
            lang_units = json.load(file)

        units = {}
        for unit in general_units:
            units[unit['name']] = unit
        for unit in lang_units:
            # TODO currently overrides unit, does not extend
            units[unit['name']] = units.get(unit['name'], unit).update(unit)

        for unit in general_units:
            self.load_unit(unit)

        self.derived = get_derived_units(self.names)

        # symbols of all units
        self.symbols_all = self.symbols.copy()
        self.symbols_all.update(self.symbols_lower)

        # surfaces of all units
        self.surfaces_all = self.surfaces.copy()
        self.surfaces_all.update(self.surfaces_lower)

    def load_unit(self, unit):
        try:
            assert unit['name'] not in self.names
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

        self.names[unit['name']] = obj

        for symbol in unit['symbols']:
            self.symbols[symbol].add(obj)
            self.symbols_lower[symbol.lower()].add(obj)
            if unit['entity'] == 'currency':
                self.symbols[symbol].add(obj)

        for surface in unit['surfaces']:
            self.surfaces[surface].add(obj)
            self.surfaces_lower[surface.lower()].add(obj)
            plural = pluralize(surface, lang=self.lang)
            self.surfaces[plural].add(obj)
            self.surfaces_lower[plural.lower()].add(obj)

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
                        "Prefixing not supported for multiple dimensions in {}"
                        .format(unit['name']))

                uri = METRIC_PREFIXES[prefix].capitalize() + unit['URI'].lower(
                )

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
                self.load_unit(prefixed_unit)


@cached
def units(lang='en_US'):
    """
    Cached unit object
    """
    return Units(lang)


################################################################################
def languages():
    subdirs = [
        x for x in Path(os.path.join(TOPDIR, '_lang')).iterdir()
        if x.is_dir() and not x.name.startswith('__')
    ]
    langs = dict((x.name, x.name) for x in subdirs)
    langs.update((x.name[:2], x.name) for x in subdirs)
    return langs


LANGUAGES = languages()
