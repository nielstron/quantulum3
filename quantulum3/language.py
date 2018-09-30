#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

# Standard library
from importlib import import_module

# Quantulum
from . import load


def get(module, lang='en_US'):
    """
    Get module for given language
    :param module:
    :param lang:
    :return:
    """
    try:
        subdir = load.LANGUAGES[lang]
    except KeyError:
        raise AttributeError("Unsupported language: {}".format(lang))
    module = import_module('.lang.{}.{}'.format(subdir, module), package=__package__)
    return module

