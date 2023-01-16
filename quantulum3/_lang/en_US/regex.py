#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod: Language specific regexes
"""

UNITS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]

TENS = [
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]

SCALES = ["hundred", "thousand", "million", "billion", "trillion"]

DECIMALS = {
    "half": 0.5,
    "third": 1 / 3,
    "fourth": 0.25,
    "quarter": 0.25,
    "fifth": 0.2,
    "sixth": 1 / 6,
    "seventh": 1 / 7,
    "eighth": 1 / 8,
    "ninth": 1 / 9,
}

MISCNUM = {"&": (1, 0), "and": (1, 0), "a": (1, 1), "an": (1, 1)}

###############################################################################

SUFFIXES = {"k": 1e3, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}

MULTIPLICATION_OPERATORS = {" times "}

DIVISION_OPERATORS = {" per ", " a "}

NEGATIVES = {"minus", "negative"}

GROUPING_OPERATORS = {",", " "}
DECIMAL_OPERATORS = {"."}

# Pattern for extracting word based numbers
TEXT_PATTERN = r"""            # Pattern for extracting mixed digit-spelled num
    (?:
        (?<![a-zA-Z0-9+.-])    # lookbehind, avoid "Area51"
        {number_pattern_no_groups}
    )?
    [, ]?(?:{numberwords_regex})
    (?:[, -]*(?:{numberwords_regex}))*
    (?!\s?{number_pattern_no_groups}) # Disallow being followed by only a
                                      # number
"""

RANGES = {"to"}  # "and" in "between X and" will be converted to "to".
UNCERTAINTIES = {"plus minus", "plus or minus"}

CONJUNCTIONS = {"and", "or", "but"}

POWERS = {"squared": 2, "cubed": 3}
EXPONENTS_REGEX = r"(?:(?:\^?\-?[0-9{{superscripts}}]+)?(?:\ (?:{powers}))?)".format(
    powers="|".join(POWERS.keys())
)
