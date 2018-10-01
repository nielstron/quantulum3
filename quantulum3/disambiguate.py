# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions.
"""

# Quantulum
import json
import os
from pathlib import Path

from quantulum3 import language
from . import classifier as clf
from . import no_classifier as no_clf
from . import load
from .load import cached


################################################################################
@cached
def training_set(lang='en_US'):
    training_set_ = []

    path = Path(os.path.join(language.topdir(lang), 'train'))
    for file in path.iterdir():
        if file.suffix == '.json':
            with file.open('r', encoding='utf-8') as train_file:
                training_set_ += json.load(train_file)

    return training_set_


################################################################################
def disambiguate_unit(unit_surface, text, lang='en_US'):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    :returns (str) unit name of the resolved unit
    """
    if clf.USE_CLF:
        base = clf.disambiguate_unit(unit_surface, text, lang).name
    else:
        base = (load.units(lang).symbols[unit_surface]
                or load.units(lang).surfaces[unit_surface]
                or load.units(lang).surfaces_lower[unit_surface.lower()]
                or load.units(lang).symbols_lower[unit_surface.lower()])

        if len(base) > 1:
            base = no_clf.disambiguate_no_classifier(base, text, lang)
        elif len(base) == 1:
            base = next(iter(base))

        if base:
            base = base.name
        else:
            base = 'unk'

    return base


################################################################################
def disambiguate_entity(key, text, lang='en_US'):
    """
    Resolve ambiguity between entities with same dimensionality.
    """
    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text)
        else:
            derived = load.entities().derived[key]
            if len(derived) > 1:
                ent = no_clf.disambiguate_no_classifier(derived, text)
                ent = load.entities().names[ent]
            elif len(derived) == 1:
                ent = next(iter(derived))
            else:
                ent = None
    except (KeyError, StopIteration):
        ent = None

    return ent


