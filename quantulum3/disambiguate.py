# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions.
"""

import logging

from . import classifier as clf
from . import load
from . import no_classifier as no_clf

_LOGGER = logging.getLogger(__name__)

###############################################################################


def disambiguate_unit(unit_surface, text, lang="en_US"):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    :returns (str) unit name of the resolved unit
    """
    units = attempt_disambiguate_unit(unit_surface, text, lang)
    if units and len(units) == 1:
        return next(iter(units)).name

    # Change the capitalization of the last letter to find a better match.
    # Capitalization is sometimes cause of confusion, but the
    # capitalization of the prefix is too important to alter.

    # If the unit is longer than two prefixes, we set everything to lower
    # except the first letter.
    if len(unit_surface) > 2:
        unit_changed = unit_surface[0] + unit_surface[1:].lower()
        if unit_changed == unit_surface:
            return resolve_ambiguity(units, unit_surface, text)
        text_changed = text.replace(unit_surface, unit_changed)
        new_units = attempt_disambiguate_unit(unit_changed, text_changed, lang)
        units = get_a_better_one(units, new_units)
        return resolve_ambiguity(units, unit_surface, text)

    if not unit_surface or unit_surface[0] not in load.METRIC_PREFIXES.keys():
        # Only apply next work around if the first letter is a SI-prefix
        return resolve_ambiguity(units, unit_surface, text)

    unit_changed = unit_surface[:-1] + unit_surface[-1].swapcase()
    text_changed = text.replace(unit_surface, unit_changed)
    new_units = attempt_disambiguate_unit(unit_changed, text_changed, lang)
    units = get_a_better_one(units, new_units)
    return resolve_ambiguity(units, unit_surface, text)


def attempt_disambiguate_unit(unit_surface, text, lang):
    """Returns list of possibilities"""
    try:
        if clf.USE_CLF:
            return clf.attempt_disambiguate_unit(unit_surface, text, lang)
        else:
            return no_clf.attempt_disambiguate_no_classifier(unit_surface, text, lang)
    except KeyError:
        return None


def get_a_better_one(old, new):
    """Decide if we pick new over old, considering them being None, and
    preferring the smaller one."""
    if not new:
        return old
    if not old:
        return new
    if len(new) < len(old):
        return new
    return old


def resolve_ambiguity(units, unit, text):
    if not units:
        if unit and clf.USE_CLF:
            raise KeyError('Could not find unit "%s" from "%s"' % (unit, text))
        else:
            return "unk"
    if len(units) == 1:
        return next(iter(units)).name
    _LOGGER.warning(
        "Could not resolve ambiguous units: '{}'. For unit '{}' in text '{}'. ".format(
            ", ".join(str(u) for u in units), unit, text
        )
    )
    # Deterministically getting something out of units.
    return next(iter(sorted(u.name for u in units)))


###############################################################################


def disambiguate_entity(key, text, lang="en_US"):
    """
    Resolve ambiguity between entities with same dimensionality.
    """
    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text, lang)
        else:
            derived = load.entities().derived[key]
            if len(derived) > 1:
                ent = no_clf.disambiguate_no_classifier(derived, text, lang)
                ent = load.entities().names[ent]
            elif len(derived) == 1:
                ent = next(iter(derived))
            else:
                ent = None
    except (KeyError, StopIteration):
        ent = None

    return ent
