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

# Quantulum
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
            try:
                scale, increment = 1, float(word.lower())
            except ValueError:
                scale, increment = r.NUMWORDS[word.lower()]
            curr = curr * scale + increment
            if scale > 100:
                result += curr
                curr = 0.0
        values.append({'old_surface': surface,
                       'old_span': span,
                       'new_surface': unicode(result + curr)})

    for item in re.finditer(r'\d+(,\d{3})+', text):
        values.append({'old_surface': item.group(0),
                       'old_span': item.span(),
                       'new_surface': unicode(item.group(0).replace(',', ''))})

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

    logging.debug(u'Text after numeric conversion: "%s"', final_text)

    return final_text, shifts


################################################################################
def get_values(item):

    '''
    Extract value from regex hit.
    '''

    callback = lambda pattern: ' %s' % (r.UNI_FRAC[pattern.group(0)])
    fracs = r'|'.join(r.UNI_FRAC)

    value = item.group(2)
    value = re.sub(ur'(?<=\d)(%s)10' % r.MULTIPLIERS, 'e', value)
    value = re.sub(fracs, callback, value, re.IGNORECASE)
    value = re.sub(' +', ' ', value)

    range_separator = re.findall(ur'\d+ ?(-|and|(?:- ?)?to) ?\d', value)
    uncer_separator = re.findall(ur'\d+ ?(\+/-|±) ?\d', value)
    fract_separator = re.findall(ur'\d+/\d+', value)

    uncertainty = None
    if range_separator:
        values = value.split(range_separator[0])
        values = [float(re.sub(r'-$', '', i)) for i in values]
    elif uncer_separator:
        values = [float(i) for i in value.split(uncer_separator[0])]
        uncertainty = values[1]
        values = [values[0]]
    elif fract_separator:
        values = value.split()
        if len(values) > 1:
            values = [float(values[0]) + float(Fraction(values[1]))]
        else:
            values = [float(Fraction(values[0]))]
    else:
        values = [float(re.sub(r'-$', '', value))]

    logging.debug(u'\tUncertainty: %s', uncertainty)
    logging.debug(u'\tValues: %s', values)

    return uncertainty, values


################################################################################
def build_unit_name(derived):

    '''
    Build the name of the unit from its dimensions.
    '''

    name = ''

    for unit in derived:
        if unit['power'] < 0:
            name += 'per '
        power = abs(unit['power'])
        if power == 1:
            name += unit['base']
        elif power == 2:
            name += 'square ' + unit['base']
        elif power == 3:
            name += 'cubic ' + unit['base']
        elif power > 3:
            name += unit['base'] + ' to the %g' % power
        name += ' '

    name = name.strip()

    logging.debug(u'\tUnit inferred name: %s', name)

    return name


################################################################################
def get_unit_from_dimensions(derived, text):

    '''
    Reconcile a unit based on its dimensionality.
    '''

    key = l.get_key_from_dimensions(derived)

    try:
        unit = l.DERIVED_UNI[key]
    except KeyError:
        logging.debug(u'\tCould not find unit for: %s', key)
        unit = c.Unit(name=build_unit_name(derived),
                      derived=derived,
                      entity=get_entity_from_dimensions(derived, text))

    return unit


################################################################################
def get_entity_from_dimensions(derived, text):

    '''
    Infer the underlying entity of a unit (e.g. "volume" for "m^3") based on its
    dimensionality.
    '''

    new_derived = [{'base': l.NAMES[i['base']].entity.name,
                    'power': i['power']} for i in derived]

    final_derived = sorted(new_derived, key=lambda x: x['base'])
    key = l.get_key_from_dimensions(final_derived)

    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text)
        else:
            ent = l.DERIVED_ENT[key][0]
    except IndexError:
        logging.debug(u'\tCould not find entity for: %s', key)
        ent = c.Entity(name='unknown', derived=new_derived)

    return ent


################################################################################
def parse_unit(item, group, slash):

    '''
    Parse surface and power from unit text.
    '''

    surface = item.group(group).replace('.', '')
    power = re.findall(r'\-?[0-9%s]+' % r.SUPERSCRIPTS, surface)

    if power:
        power = [r.UNI_SUPER[i] if i in r.UNI_SUPER else i for i \
                 in power]
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

    group_units = [1, 4, 6, 8, 10]
    group_operators = [3, 5, 7, 9]

    item_units = [item.group(i) for i in group_units if item.group(i)]

    if len(item_units) == 0:
        unit = l.NAMES['dimensionless']
    else:
        derived, slash = [], False
        for group in sorted(group_units + group_operators):
            if not item.group(group):
                continue
            if group in group_units:
                surface, power = parse_unit(item, group, slash)
                if clf.USE_CLF:
                    base = clf.disambiguate_unit(surface, text).name
                else:
                    base = l.UNITS[surface][0].name
                derived += [{'base': base, 'power': power}]
            elif not slash:
                slash = any(i in item.group(group) for i in [u'/', u' per '])

        unit = get_unit_from_dimensions(derived, text)

    logging.debug(u'\tUnit: %s', unit)
    logging.debug(u'\tEntity: %s', unit.entity)

    return unit


################################################################################
def get_surface(shifts, orig_text, item, text):

    '''
    Extract surface from regex hit.
    '''

    span = item.span()
    logging.debug(u'\tInitial span: %s ("%s")', span, text[span[0]:span[1]])

    real_span = (span[0] - shifts[span[0]], span[1] - shifts[span[1] - 1])
    surface = orig_text[real_span[0]:real_span[1]]
    logging.debug(u'\tShifted span: %s ("%s")', real_span, surface)

    while any(surface.endswith(i) for i in [' ', '-']):
        surface = surface[:-1]
        real_span = (real_span[0], real_span[1] - 1)

    while surface.startswith(' '):
        surface = surface[1:]
        real_span = (real_span[0] + 1, real_span[1])

    logging.debug(u'\tFinal span: %s ("%s")', real_span, surface)
    return surface, real_span


################################################################################
def is_quote_artifact(orig_text, span):

    '''
    Distinguish between quotes and units.
    '''

    res = False
    cursor = re.finditer(r'("|\')[^ .,:;?!()*+-].*?("|\')', orig_text)

    for item in cursor:
        if item.span()[1] == span[1]:
            res = True

    return res


################################################################################
def build_quantity(orig_text, text, item, values, unit, surface, span, uncert):

    '''
    Build a Quantity object out of extracted information.
    '''

    # Discard irrelevant txt2float extractions, cardinal numbers, codes etc.
    if surface.lower() in ['a', 'an', 'one'] or \
    re.search(r'1st|2nd|3rd|[04-9]th', surface) or \
    re.search(r'\d+[A-Z]+\d+', surface) or \
    re.search(r'\ba second\b', surface, re.IGNORECASE):
        logging.debug(u'\tMeaningless quantity ("%s"), discard', surface)
        return

    # Usually "$3T" does not stand for "dollar tesla"
    elif unit.entity.derived and unit.entity.derived[0]['base'] == 'currency':
        if len(unit.derived) > 1:
            try:
                suffix = re.findall(r'\d(K|M|B|T)\b(.*?)$', surface)[0]
                values = [i * r.SUFFIXES[suffix[0]] for i in values]
                unit = l.UNITS[unit.derived[0]['base']][0]
                if suffix[1]:
                    surface = surface[:surface.find(suffix[1])]
                    span = (span[0], span[1] - len(suffix[1]))
                logging.debug(u'\tCorrect for "$3T" pattern')
            except IndexError:
                pass
        else:
            try:
                suffix = re.findall(r'%s(K|M|B|T)\b' % re.escape(surface),
                                    orig_text)[0]
                surface += suffix
                span = (span[0], span[1] + 1)
                values = [i * r.SUFFIXES[suffix] for i in values]
                logging.debug(u'\tCorrect for "$3T" pattern')
            except IndexError:
                pass

    # Usually "1990s" stands for the decade, not the amount of seconds
    elif re.match(r'[1-2]\d\d0s', surface):
        unit = l.NAMES['dimensionless']
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        logging.debug(u'\tCorrect for "1990s" pattern')

    # Usually "in" stands for the preposition, not inches
    elif unit.derived[-1]['base'] == 'inch' and re.search(r' in$', surface) and\
    '/' not in surface:
        if len(unit.derived) > 1:
            unit = get_unit_from_dimensions(unit.derived[:-1], orig_text)
        else:
            unit = l.NAMES['dimensionless']
        surface = surface[:-3]
        span = (span[0], span[1] - 3)
        logging.debug(u'\tCorrect for "in" pattern')

    elif is_quote_artifact(text, item.span()):
        if len(unit.derived) > 1:
            unit = get_unit_from_dimensions(unit.derived[:-1], orig_text)
        else:
            unit = l.NAMES['dimensionless']
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        logging.debug(u'\tCorrect for quotes')

    elif re.search(r' time$', surface) and len(unit.derived) > 1 and \
    unit.derived[-1]['base'] == 'count':
        unit = get_unit_from_dimensions(unit.derived[:-1], orig_text)
        surface = surface[:-5]
        span = (span[0], span[1] - 5)
        logging.debug(u'\tCorrect for "time"')

    objs = []
    for value in values:
        obj = c.Quantity(value=value,
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
    maps = {u'×': u'x', u'–': u'-', u'−': '-'}
    for element in maps:
        text = text.replace(element, maps[element])

    # Replace genitives
    text = re.sub(r'(?<=\w)\'s\b|(?<=\w)s\'(?!\w)', '  ', text)

    logging.debug(u'Clean text: "%s"', text)

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
        logging.debug(u'Verbose mode')

    if isinstance(text, str):
        text = text.decode('utf-8')
        logging.debug(u'Converted string to unicode (assume utf-8 encoding)')

    orig_text = text
    logging.debug(u'Original text: "%s"', orig_text)

    text = clean_text(text)
    values = extract_spellout_values(text)
    text, shifts = substitute_values(text, values)

    quantities = []
    for item in r.REG_DIM.finditer(text):

        groups = dict([i for i in item.groupdict().items() if i[1] and \
                       i[1].strip()])
        logging.debug(u'Quantity found: %s', groups)

        try:
            uncert, values = get_values(item)
        except ValueError as err:
            logging.debug(u'Could not parse quantity: %s', err)

        unit = get_unit(item, text)
        surface, span = get_surface(shifts, orig_text, item, text)
        objs = build_quantity(orig_text, text, item, values, unit, surface,
                              span, uncert)
        if objs is not None:
            quantities += objs

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
        to_add = u' {' + unicode(quantity) + u'}'
        text = text[0:index] + to_add + text[index:]
        shift += len(to_add)

    return text

