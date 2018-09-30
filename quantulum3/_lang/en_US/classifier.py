# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classifier functions.
"""

# Standard library
import re
import string

try:
    from stemming.porter2 import stem
except ImportError:
    stem = None


################################################################################
def clean_text(text):
    """
    Clean text for TFIDF
    """
    if not stem:
        raise ImportError("Module stemming is not installed.")

    my_regex = re.compile(r'[%s]' % re.escape(string.punctuation))
    new_text = my_regex.sub(' ', text)

    new_text = [
        stem(i) for i in new_text.lower().split()
        if not re.findall(r'[0-9]', i)
    ]

    new_text = ' '.join(new_text)

    return new_text
