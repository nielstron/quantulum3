#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod: Language specific regexes
"""

UNITS = [
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
    'sixteen', 'seventeen', 'eighteen', 'nineteen'
]

TENS = [
    '', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty',
    'ninety'
]

SCALES = ['hundred', 'thousand', 'million', 'billion', 'trillion']

DECIMALS = {
    'half': 0.5,
    'third': 1 / 3,
    'fourth': 0.25,
    'quarter': 0.25,
    'fifth': 0.2,
    'sixth': 1 / 6,
    'seventh': 1 / 7,
    'eighth': 1 / 8,
    'ninth': 1 / 9
}

MISCNUM = {'and': (1, 0), 'a': (1, 1), 'an': (1, 1)}

################################################################################

SUFFIXES = {'k': 1e3, 'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}

MULTIPLICATION_OPERATORS = {' times '}

DIVISION_OPERATORS = {
    u' per ',
    u' a ',
}

GROUPING_OPERATORS = {u',', u' '}
DECIMAL_OPERATORS = {u'.'}

# Pattern for extracting a digit-based number
NUM_PATTERN = r''' 
    (?{number}              # required number
        [+-]?                  #   optional sign
        \.?\d+                 #   required digits
        (?:[{grouping}]\d{{3}})*         #   allowed grouping
        (?{decimals}[{decimals}]\d+)?    #   optional decimals
    )
    (?{scale}               # optional exponent
        (?:{multipliers})?                #   multiplicative operators
        (?{base}(E|e|\d+)\^?)    #   required exponent prefix
        (?{exponent}[+-]?\d+|[{superscript])      #   required exponent, superscript or normal
    )?
    (?{fraction}             # optional fraction
        \ \d+/\d+|\ ?[{unicode_fract}]|/\d+
    )?

'''

RANGES = {'to', 'and'}
UNCERTAINTIES = {'plus minus'}
