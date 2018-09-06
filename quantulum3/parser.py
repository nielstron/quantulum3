#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
:mod:`Quantulum` parser.
'''

# Standard library
import re
import logging
from fractions import Fraction
from collections import defaultdict
from math import pow

from . import load as l
from . import regex as r
from . import classes as c
from . import classifier as clf


################################################################################
def clean_surface(surface, span):
    '''
    Remove spurious characters from a quantity's surface.
    '''

    surface = surface.replace('-', ' ')
    no_start = ['and', ' ']
    no_end = [' and', ' ']

    found = True
    while found:
        found = False
        for word in no_start:
            if surface.lower().startswith(word):
                surface = surface[len(word):]
                span = (span[0] + len(word), span[1])
                found = True
        for word in no_end:
            if surface.lower().endswith(word):
                surface = surface[:-len(word)]
                span = (span[0], span[1] - len(word))
                found = True

    if not surface:
        return None, None

    split = surface.lower().split()
    if split[0] in ['one', 'a', 'an'] and len(split) > 1 and split[1] in \
            r.UNITS + r.TENS:
        span = (span[0] + len(surface.split()[0]) + 1, span[1])
        surface = ' '.join(surface.split()[1:])

    return surface, span


################################################################################
def extract_spellout_values(text):
    '''
    Convert spelled out numbers in a given text to digits.
    '''

    values = []
    for item in r.REG_TXT.finditer(text):
        surface, span = clean_surface(item.group(0), item.span())
        if not surface or surface.lower() in r.SCALES:
            continue
        curr = result = 0.0
        for word in surface.split():
            scale = None
            try:
                scale, increment = 1, float(word.lower())
            except ValueError:
                scale, increment = r.NUMWORDS[word.lower()]
            curr = curr * scale + increment
            if scale > 100:
                result += curr
                curr = 0.0
        values.append({
            'old_surface': surface,
            'old_span': span,
            'new_surface': str(result + curr)
        })

    for item in re.finditer(r'\d+(,\d{3})+', text):
        values.append({
            'old_surface': item.group(0),
            'old_span': item.span(),
            'new_surface': str(item.group(0).replace(',', ''))
        })

    return sorted(values, key=lambda x: x['old_span'][0])


################################################################################
def substitute_values(text, values):
    '''
    Convert spelled out numbers in a given text to digits.
    '''

    shift, final_text, shifts = 0, text, defaultdict(int)
    for value in values:
        first = value['old_span'][0] + shift
        second = value['old_span'][1] + shift
        final_text = final_text[0:first] + value['new_surface'] + \
            final_text[second:]
        shift += len(value['new_surface']) - len(value['old_surface'])
        for char in range(first + 1, len(final_text)):
            shifts[char] = shift

    logging.debug('Text after numeric conversion: "%s"', final_text)

    return final_text, shifts


################################################################################
def get_values(item):
    '''
    Extract value from regex hit.
    '''

    def callback(pattern):
        return ' %s' % (r.UNI_FRAC[pattern.group(0)])

    fracs = r'|'.join(r.UNI_FRAC)

    value = item.group('value')
    # Replace unusual exponents by e (including e)
    value = re.sub(r'(?<=\d)(%s)(e|E|10)\^?' % r.MULTIPLIERS, 'e', value)
    # calculate other exponents
    value, factors = resolve_exponents(value)
    logging.debug("After exponent resolution: {}".format(value))

    value = re.sub(fracs, callback, value, re.IGNORECASE)

    range_separator = re.findall(r'\d+ ?(-|and|(?:- ?)?to) ?\d', value)
    uncer_separator = re.findall(r'\d+ ?(\+/-|±) ?\d', value)
    fract_separator = re.findall(r'\d+/\d+', value)

    value = re.sub(' +', ' ', value)
    uncertainty = None
    if range_separator:
        # A range just describes an uncertain quantity
        values = value.split(range_separator[0])
        values = [
            float(re.sub(r'-$', '', v)) * factors[i]
            for i, v in enumerate(values)
        ]
        mean = sum(values) / len(values)
        uncertainty = mean - min(values)
        values = [mean]
    elif uncer_separator:
        values = [float(i) for i in value.split(uncer_separator[0])]
        uncertainty = values[1] * factors[1]
        values = [values[0] * factors[0]]
    elif fract_separator:
        try:
            values = value.split()
            if len(values) > 1:
                values = [
                    float(values[0]) * factors[0] + float(Fraction(values[1]))
                ]
            else:
                values = [float(Fraction(values[0]))]
        except ZeroDivisionError as e:
            raise ValueError('{} is not a number'.format(values[0]), e)
    else:
        values = [float(re.sub(r'-$', '', value)) * factors[0]]

    logging.debug('\tUncertainty: %s', uncertainty)
    logging.debug('\tValues: %s', values)

    return uncertainty, values


###############################################################################
def resolve_exponents(value):
    """Resolve unusual exponents (like 2^4) and return substituted string and factor

    Params:
        value: str, string with only one value
    Returns:
        str, string with basis and exponent removed
        array of float, factors for multiplication

    """
    factors = []
    matches = re.finditer(r.NUM_PATTERN_GROUPS, value,
                          re.IGNORECASE | re.VERBOSE)
    for item in matches:
        try:
            base = item.group('base')
            if base in ['e', 'E']:
                # already handled by float
                factors.append(1)
                continue
                # exp = '10'
            exp = item.group('exponent')
            for superscript, substitute in r.UNI_SUPER.items():
                exp.replace(superscript, substitute)
            exp = float(exp)
            base = float(base.replace('^', ''))
            factor = pow(base, exp)
            stripped = str(value).replace(item.group('scale'), '')
            value = stripped
            factors.append(factor)
            logging.debug("Replaced {} by factor {}".format(
                item.group('scale'), factor))
        except (IndexError, AttributeError):
            factors.append(1)
            continue
    return value, factors


###############################################################################
def build_unit_name(dimensions):
    '''
    Build the name of the unit from its dimensions.
    '''
    name = c.Unit.name_from_dimensions(dimensions)

    logging.debug('\tUnit inferred name: %s', name)

    return name


################################################################################
def get_unit_from_dimensions(dimensions, text):
    '''
    Reconcile a unit based on its dimensionality.
    '''

    key = l.get_key_from_dimensions(dimensions)

    try:
        unit = l.DERIVED_UNI[key]
        # carry on surfaces
        unit.dimensions = dimensions
    except KeyError:
        logging.debug(u'\tCould not find unit for: %s', key)
        unit = c.Unit(
            name=build_unit_name(dimensions),
            dimensions=dimensions,
            entity=get_entity_from_dimensions(dimensions, text))

    return unit


################################################################################
def get_entity_from_dimensions(dimensions, text):
    '''
    Infer the underlying entity of a unit (e.g. "volume" for "m^3") based on its
    dimensionality.
    '''

    new_dimensions = [{
        'base': l.NAMES[i['base']].entity.name,
        'power': i['power']
    } for i in dimensions]

    new_derived = [{
        'base': l.NAMES[i['base']].entity.name,
        'power': i['power']
    } for i in dimensions]

    final_derived = sorted(new_derived, key=lambda x: x['base'])
    key = l.get_key_from_dimensions(final_derived)

    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text)
        else:
            ent = l.DERIVED_ENT[key][0]
    except IndexError:
        logging.debug('\tCould not find entity for: %s', key)
        ent = c.Entity(name='unknown', dimensions=new_derived)

    return ent


################################################################################
def parse_unit(item, unit, slash):
    '''
    Parse surface and power from unit text.
    '''

    surface = unit.replace('.', '')
    power = re.findall(r'\-?[0-9%s]+' % r.SUPERSCRIPTS, surface)

    if power:
        power = [r.UNI_SUPER[i] if i in r.UNI_SUPER else i for i in power]
        power = ''.join(power)
        new_power = (-1 * int(power) if slash else int(power))
        surface = re.sub(r'\^?\-?[0-9%s]+' % r.SUPERSCRIPTS, '', surface)

    elif re.findall(r'\bcubed\b', surface):
        new_power = (-3 if slash else 3)
        surface = re.sub(r'\bcubed\b', '', surface).strip()

    elif re.findall(r'\bsquared\b', surface):
        new_power = (-2 if slash else 2)
        surface = re.sub(r'\bsquared\b', '', surface).strip()

    else:
        new_power = (-1 if slash else 1)

    return surface, new_power


################################################################################
def get_unit(item, text):
    '''
    Extract unit from regex hit.
    '''

    group_units = ['prefix', 'unit1', 'unit2', 'unit3', 'unit4']
    group_operators = ['operator1', 'operator2', 'operator3', 'operator4']
    # How much of the end is removed because of an "incorrect" regex match
    unit_shortening = 0

    item_units = [item.group(i) for i in group_units if item.group(i)]

    if len(item_units) == 0:
        unit = l.NAMES['dimensionless']
    else:
        derived, slash = [], False
        multiplication_operator, division_operator = False, False
        for index in range(0, 5):
            unit = item.group(group_units[index])
            operator_index = None if index < 1 else group_operators[index - 1]
            operator = None if index < 1 else item.group(operator_index)

            # disallow spaces as operators in units expressed in their symbols
            # Enforce consistency among multiplication and division operators
            # Single exceptions are colloquial number abbreviations (5k miles)
            _cut_inconsistent_operator = False
            if operator in r.MULTIPLICATION_OPERATORS or (
                    operator is None and unit
                    and not (index == 1 and unit in r.SUFFIXES)):
                if multiplication_operator != operator and not (
                        index == 1 and str(operator).isspace()):
                    if multiplication_operator is False:
                        multiplication_operator = operator
                    else:
                        _cut_inconsistent_operator = True
            elif operator in r.DIVISION_OPERATORS:
                if division_operator != operator and division_operator is not False:
                    _cut_inconsistent_operator = True
                else:
                    division_operator = operator
            if _cut_inconsistent_operator:
                # Cut if inconsistent multiplication operator
                # treat the None operator differently - remove the whole word of it
                if operator is None:
                    # For this, use the last consistent operator (before the current) with a space
                    # which should always be the preceding operator
                    derived.pop()
                    operator_index = group_operators[index - 2]
                # Remove (original length - new end) characters
                unit_shortening = item.end() - item.start(operator_index)
                logging.debug(
                    "Because operator inconsistency, cut from operator: '{}', new surface: {}".
                    format(operator,
                           text[item.start():item.end() - unit_shortening]))
                break

            # Determine whether a negative power has to be applied to following units
            if operator and not slash:
                slash = any(i in operator for i in ['/', ' per '])
            # Determine which unit follows
            if unit:
                unit_surface, power = parse_unit(item, unit, slash)
                if clf.USE_CLF:
                    base = clf.disambiguate_unit(unit_surface, text).name
                else:
                    if len(l.UNIT_SYMBOLS[unit_surface]) > 0:
                        base = l.UNIT_SYMBOLS[unit_surface][0].name
                    elif len(l.UNITS[unit_surface]) > 0:
                        base = l.UNITS[unit_surface][0].name
                    elif len(l.UNIT_SYMBOLS_LOWER[unit_surface.lower()]) > 0:
                        base = l.UNIT_SYMBOLS_LOWER[unit_surface.lower()][
                            0].name
                    elif len(l.LOWER_UNITS[unit_surface.lower()]) > 0:
                        base = l.LOWER_UNITS[unit_surface.lower()][0].name
                    else:
                        base = 'unk'
                derived += [{
                    'base': base,
                    'power': power,
                    'surface': unit_surface
                }]

        unit = get_unit_from_dimensions(derived, text)

    logging.debug('\tUnit: %s', unit)
    logging.debug('\tEntity: %s', unit.entity)

    return unit, unit_shortening


################################################################################
def get_surface(shifts, orig_text, item, text, unit_shortening=0):
    '''
    Extract surface from regex hit.
    '''

    # handle cut end
    span = (item.start(), item.end() - unit_shortening)

    logging.debug('\tInitial span: %s ("%s")', span, text[span[0]:span[1]])

    real_span = (span[0] - shifts[span[0]], span[1] - shifts[span[1] - 1])
    surface = orig_text[real_span[0]:real_span[1]]
    logging.debug('\tShifted span: %s ("%s")', real_span, surface)

    while any(surface.endswith(i) for i in [' ', '-']):
        surface = surface[:-1]
        real_span = (real_span[0], real_span[1] - 1)

    while surface.startswith(' '):
        surface = surface[1:]
        real_span = (real_span[0] + 1, real_span[1])

    logging.debug('\tFinal span: %s ("%s")', real_span, surface)
    return surface, real_span


################################################################################
def is_quote_artifact(orig_text, span):
    '''
    Distinguish between quotes and units.
    '''

    res = False
    cursor = re.finditer(r'("|\')[^ .,:;?!()*+-].*?("|\')', orig_text)

    for item in cursor:
        if item.span()[1] <= span[1] and item.span()[1] >= span[0]:
            res = item
            break

    return res


################################################################################
def build_quantity(orig_text, text, item, values, unit, surface, span, uncert):
    '''
    Build a Quantity object out of extracted information.
    '''
    # Re parse unit if a change occurred
    dimension_change = False

    # Discard irrelevant txt2float extractions, cardinal numbers, codes etc.
    if surface.lower() in ['a', 'an', 'one'] or \
            re.search(r'1st|2nd|3rd|[04-9]th', surface) or \
            re.search(r'\d+[A-Z]+\d+', surface) or \
            re.search(r'\ba second\b', surface, re.IGNORECASE):
        logging.debug('\tMeaningless quantity ("%s"), discard', surface)
        return

    # Usually "$3T" does not stand for "dollar tesla"
    # this holds as well for "3k miles"
    # TODO use classifier to decide if 3K is 3 thousand or 3 Kelvin
    if unit.entity.dimensions:
        if (len(unit.entity.dimensions) > 1
                and unit.entity.dimensions[0]['base'] == 'currency'
                and unit.dimensions[1]['surface'] in r.SUFFIXES.keys()):
            suffix = unit.dimensions[1]['surface']
            # Only apply if at least last value is suffixed by k, M, etc
            if re.search(r'\d{}\b'.format(suffix), text):
                values = [value * r.SUFFIXES[suffix] for value in values]
                unit.dimensions = [unit.dimensions[0]] + unit.dimensions[2:]
                dimension_change = True

        elif unit.dimensions[0]['surface'] in r.SUFFIXES.keys():
            # k/M etc is only applied if non-symbolic surfaces of other units (because colloquial)
            # or currency units
            symbolic = all(
                any(dim['surface'] in unit.symbols
                    for unit in l.UNITS[dim['base']])
                for dim in unit.dimensions[1:])
            if not symbolic:
                suffix = unit.dimensions[0]['surface']
                values = [value * r.SUFFIXES[suffix] for value in values]
                unit.dimensions = unit.dimensions[1:]
                dimension_change = True

    # Usually "1990s" stands for the decade, not the amount of seconds
    elif re.match(r'[1-2]\d\d0s', surface):
        unit.dimensions = []
        dimension_change = True
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        logging.debug('\tCorrect for "1990s" pattern')

    # check if a unit, combined only from symbols
    # and without operators, actually is a common 4-letter-word
    if unit.dimensions:
        candidates = [(u.get('surface') in l.ALL_UNIT_SYMBOLS
                       and u['power'] == 1) for u in unit.dimensions]
        for start in range(0, len(unit.dimensions)):
            for end in reversed(range(start + 1, len(unit.dimensions) + 1)):
                # Try to match a combination of consecutive surfaces with a common 4 letter word
                if not all(candidates[start:end]):
                    continue
                combination = ''.join(
                    u['surface'] for u in unit.dimensions[start:end])
                # Combination has to be inside the surface
                if combination not in surface:
                    continue
                # Combination has to be a common word of at least two letters
                if len(combination
                       ) <= 1 or combination not in l.FOUR_LETTER_WORDS[len(
                           combination)]:
                    continue
                # Cut the combination from the surface and everything that follows
                # as it is a word, it will be preceded by a space
                match = re.search(r'[-\s]%s\b' % combination, surface)
                if not match:
                    continue
                span = (span[0], span[0] + match.start())
                surface = surface[:match.start()]
                unit.dimensions = unit.dimensions[:start]
                dimension_change = True

    # Usually "in" stands for the preposition, not inches
    if unit.dimensions and (unit.dimensions[-1]['base'] == 'inch'
                            and re.search(r' in$', surface)
                            and '/' not in surface):
        unit.dimensions = unit.dimensions[:-1]
        dimension_change = True
        surface = surface[:-3]
        span = (span[0], span[1] - 3)
        logging.debug('\tCorrect for "in" pattern')

    match = is_quote_artifact(text, item.span())
    if match:
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        if unit.dimensions and (unit.dimensions[-1]['base'] == 'inch'):
            unit.dimensions = unit.dimensions[:-1]
            dimension_change = True
        logging.debug('\tCorrect for quotes')

    if re.search(r' time$', surface) and len(unit.dimensions) > 1 and \
            unit.dimensions[-1]['base'] == 'count':
        unit.dimensions = unit.dimensions[:-1]
        dimension_change = True
        surface = surface[:-5]
        span = (span[0], span[1] - 5)
        logging.debug('\tCorrect for "time"')

    if dimension_change:
        if len(unit.dimensions) >= 1:
            unit = get_unit_from_dimensions(unit.dimensions, orig_text)
        else:
            unit = l.NAMES['dimensionless']

    objs = []
    for value in values:
        obj = c.Quantity(
            value=value,
            unit=unit,
            surface=surface,
            span=span,
            uncertainty=uncert)
        objs.append(obj)

    return objs


################################################################################
def clean_text(text):
    '''
    Clean text before parsing.
    '''

    # Replace a few nasty unicode characters with their ASCII equivalent
    maps = {'×': 'x', '–': '-', '−': '-'}
    for element in maps:
        text = text.replace(element, maps[element])

    # Replace genitives
    text = re.sub(r'(?<=\w)\'s\b|(?<=\w)s\'(?!\w)', '  ', text)

    logging.debug('Clean text: "%s"', text)

    return text


################################################################################
def parse(text, verbose=False):
    '''
    Extract all quantities from unstructured text.
    '''

    log_format = ('%(asctime)s --- %(message)s')
    logging.basicConfig(format=log_format)
    root = logging.getLogger()

    if verbose:
        level = root.level
        root.setLevel(logging.DEBUG)
        logging.debug('Verbose mode')

    # if isinstance(text, str):
    #    text = str(text, encoding='utf-8')
    #    logging.debug('Converted string to unicode (assume utf-8 encoding)')

    orig_text = text
    logging.debug('Original text: "%s"', orig_text)

    text = clean_text(text)
    values = extract_spellout_values(text)
    text, shifts = substitute_values(text, values)

    quantities = []
    for item in r.REG_DIM.finditer(text):

        groups = dict(
            [i for i in item.groupdict().items() if i[1] and i[1].strip()])
        logging.debug(u'Quantity found: %s', groups)

        try:
            uncert, values = get_values(item)

            unit, unit_shortening = get_unit(item, text)
            surface, span = get_surface(shifts, orig_text, item, text,
                                        unit_shortening)
            objs = build_quantity(orig_text, text, item, values, unit, surface,
                                  span, uncert)
            if objs is not None:
                quantities += objs
        except ValueError as err:
            logging.debug('Could not parse quantity: %s', err)

    if verbose:
        root.level = level

    return quantities


################################################################################
def inline_parse(text, verbose=False):
    '''
    Extract all quantities from unstructured text.
    '''

    if isinstance(text, str):
        text = text.decode('utf-8')

    parsed = parse(text, verbose=verbose)

    shift = 0
    for quantity in parsed:
        index = quantity.span[1] + shift
        to_add = u' {' + str(quantity) + u'}'
        text = text[0:index] + to_add + text[index:]
        shift += len(to_add)

    return text


################################################################################
def inline_parse_and_replace(text, verbose=False):
    '''
    Parse text and replace with the standardised quantities as string
    '''

    parsed = parse(text, verbose=verbose)

    shift = 0
    for quantity in parsed:
        index_start = quantity.span[0] + shift
        index_end = quantity.span[1] + shift
        to_add = quantity.as_string()
        text = text[0:index_start] + to_add + text[index_end:]
        shift += len(to_add) - (quantity.span[1] - quantity.span[0])

    return text
