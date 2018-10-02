#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

# Standard library
from importlib import import_module
from pathlib import Path

TOPDIR = Path(__file__).parent or Path('.')


################################################################################
def languages():
    subdirs = [
        x for x in TOPDIR.joinpath('_lang').iterdir()
        if x.is_dir() and not x.name.startswith('__')
    ]
    langs = dict((x.name, x.name) for x in subdirs)
    langs.update((x.name[:2], x.name) for x in subdirs)
    return langs


LANGUAGES = languages()


################################################################################
def get(module, lang='en_US'):
    """
    Get module for given language
    :param module:
    :param lang:
    :return:
    """
    try:
        subdir = LANGUAGES[lang]
    except KeyError:
        raise NotImplementedError("Unsupported language: {}".format(lang))
    module = import_module(
        '._lang.{}.{}'.format(subdir, module), package=__package__)
    return module


################################################################################
def topdir(lang='en_US'):
    return TOPDIR.joinpath('_lang', LANGUAGES[lang])
