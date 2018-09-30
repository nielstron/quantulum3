# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions.
"""

# Quantulum
from . import classifier as clf
from . import no_classifier as no_clf
from . import load


################################################################################
def disambiguate_unit(unit_surface, text):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    :returns (str) unit name of the resolved unit
    """
    if clf.USE_CLF:
        base = clf.disambiguate_unit(unit_surface, text).name
    else:
        if len(load.UNIT_SYMBOLS[unit_surface]) > 0:
            base = load.UNIT_SYMBOLS[unit_surface]
        elif len(load.UNITS[unit_surface]) > 0:
            base = load.UNITS[unit_surface]
        elif len(load.UNIT_SYMBOLS_LOWER[unit_surface.lower()]) > 0:
            base = load.UNIT_SYMBOLS_LOWER[unit_surface.lower()]
        elif len(load.LOWER_UNITS[unit_surface.lower()]) > 0:
            base = load.LOWER_UNITS[unit_surface.lower()]
        else:
            base = []

        if len(base) > 1:
            base = no_clf.disambiguate_no_classifier(base, text)
        elif len(base) == 1:
            base = next(iter(base))

        if base:
            base = base.name
        else:
            base = 'unk'

    return base


################################################################################
def disambiguate_entity(key, text):
    """
    Resolve ambiguity between entities with same dimensionality.
    """
    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text)
        else:
            derived = load.DERIVED_ENT[key]
            if len(derived) > 1:
                ent = no_clf.disambiguate_no_classifier(derived, text)
                ent = load.ENTITIES[ent]
            elif len(derived) == 1:
                ent = next(iter(derived))
            else:
                ent = None
    except (KeyError, StopIteration):
        ent = None

    return ent
