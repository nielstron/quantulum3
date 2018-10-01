#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

# Standard library
from importlib import import_module
import os

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
        raise NotImplementedError("Unsupported language: {}".format(lang))
    module = import_module(
        '._lang.{}.{}'.format(subdir, module), package=__package__)
    return module


def topdir(lang='en_US'):
    return os.path.join(load.TOPDIR, '_lang', load.LANGUAGES[lang])
