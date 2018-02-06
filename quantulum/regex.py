#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:mod:`Quantulum` regex functions.
'''

# Standard library
import re

# Quantulum
from . import load as l

UNITS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
         'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
         'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']

TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
        'eighty', 'ninety']

SCALES = ['hundred', 'thousand', 'million', 'billion', 'trillion']

################################################################################
def get_numwords():

    '''
    Convert number words to integers in a given text.
    '''

    numwords = {'and': (1, 0), 'a': (1, 1), 'an': (1, 1)}

    for idx, word in enumerate(UNITS):
        numwords[word] = (1, idx)
    for idx, word in enumerate(TENS):
        numwords[word] = (1, idx * 10)
    for idx, word in enumerate(SCALES):
        numwords[word] = (10 ** (idx * 3 or 2), 0)

    all_numbers = r'|'.join(r'\b%s\b' % i for i in list(numwords.keys()) if i)

    return all_numbers, numwords


################################################################################

SUFFIXES = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}

UNI_SUPER = {'¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5',
             '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁰': '0'}

UNI_FRAC = {'¼': '1/4', '½': '1/2', '¾': '3/4', '⅐': '1/7', '⅑': '1/9',
            '⅒': '1/10', '⅓': '1/3', '⅔': '2/3', '⅕': '1/5', '⅖': '2/5',
            '⅗': '3/5', '⅘': '4/5', '⅙': '1/6', '⅚': '5/6', '⅛': '1/8',
            '⅜': '3/8', '⅝': '5/8', '⅞': '7/8'}

OPERATORS = {'/': ' per ', ' per ': ' per ', ' a ': ' per ',
             '*': ' ', ' ': ' ', '·': ' ', 'x': ' '}

ALL_NUM, NUMWORDS = get_numwords()
FRACTIONS = re.escape(''.join(list(UNI_FRAC.keys())))
SUPERSCRIPTS = re.escape(''.join(list(UNI_SUPER.keys())))

MULTIPLIERS = r'|'.join(r'%s' % re.escape(i) for i in OPERATORS if \
              OPERATORS[i] == ' ')

NUM_PATTERN = r'''            # Pattern for extracting a digit-based number

    (?:                        # required number
        [+-]?                  #   optional sign
        \.?\d+                 #   required digits
        (?:\.\d+)?             #   optional decimals
    )
    (?:                        # optional exponent
        (?:%s)?                #   multiplicative operators
        (?:E|e|10\^?)          #   required exponent prefix
        (?:[+-]?\d+|[%s])      #   required exponent, superscript or normal
    )?
    (?:                        # optional fraction
        \ \d+/\d+|\ ?[%s]|/\d+
    )?

''' % (MULTIPLIERS, SUPERSCRIPTS, FRACTIONS)

RAN_PATTERN = r'''                        # Pattern for a range of numbers

    (?:                                    # First number
        (?<![a-zA-Z0-9+.-])                # lookbehind, avoid "Area51"
        %s
    )
    (?:                                    # Second number
        \ ?(?:(?:-\ )?to|-|and|\+/-|±)\ ?  # Group for ranges or uncertainties
    %s)?

''' % (NUM_PATTERN, NUM_PATTERN)

TXT_PATTERN = r'''            # Pattern for extracting mixed digit-spelled num
    (?:
        (?<![a-zA-Z0-9+.-])    # lookbehind, avoid "Area51"
        %s
    )?
    [ -]?(?:%s)
    [ -]?(?:%s)?[ -]?(?:%s)?[ -]?(?:%s)?
    [ -]?(?:%s)?[ -]?(?:%s)?[ -]?(?:%s)?
''' % tuple([NUM_PATTERN] + 7*[ALL_NUM])

REG_TXT = re.compile(TXT_PATTERN, re.VERBOSE | re.IGNORECASE)

################################################################################
def get_units_regex():

    '''
    Build a compiled regex object. Groups of the extracted items, with 4
    repetitions, are:

        0: whole surface
        1: prefixed symbol
        2: numerical value
        3: first operator
        4: first unit
        5: second operator
        6: second unit
        7: third operator
        8: third unit
        9: fourth operator
        10: fourth unit

    Example, 'I want $20/h'

        0: $20/h
        1: $
        2: 20
        3: /
        4: h
        5: None
        6: None
        7: None
        8: None
        9: None
        10: None

    '''

    op_keys = sorted(list(OPERATORS.keys()), key=len, reverse=True)
    unit_keys = sorted(list(l.UNITS.keys()), key=len, reverse=True)
    symbol_keys = sorted(list(l.SYMBOLS.keys()), key=len, reverse=True)

    exponent = r'(?:(?:\^?\-?[0-9%s]*)(?:\ cubed|\ squared)?)(?![a-zA-Z])' % \
               SUPERSCRIPTS

    all_ops = '|'.join([r'%s' % re.escape(i) for i in op_keys])
    all_units = '|'.join([r'%s' % re.escape(i) for i in unit_keys])
    all_symbols = '|'.join([r'%s' % re.escape(i) for i in symbol_keys])

    pattern = r'''

        (?P<prefix>(?:%s)(?![a-zA-Z]))?         # Currencies, mainly
        (?P<value>%s)-?                           # Number
        (?:(?P<operator1>%s)?(?P<unit1>(?:%s)%s)?)    # Operator + Unit (1)
        (?:(?P<operator2>%s)?(?P<unit2>(?:%s)%s)?)    # Operator + Unit (2)
        (?:(?P<operator3>%s)?(?P<unit3>(?:%s)%s)?)    # Operator + Unit (3)
        (?:(?P<operator4>%s)?(?P<unit4>(?:%s)%s)?)    # Operator + Unit (4)

    ''' % tuple([all_symbols, RAN_PATTERN] + 4*[all_ops, all_units, exponent])

    regex = re.compile(pattern, re.VERBOSE | re.IGNORECASE)

    return regex

REG_DIM = get_units_regex()

