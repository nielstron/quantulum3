#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classes.
"""

from typing import Any, Dict, List, Tuple

from . import speak

###############################################################################


class Quantity(object):
    """
    Class for a quantity (e.g. "4.2 gallons").
    """

    def __init__(
        self,
        value=None,
        unit=None,
        surface=None,
        span=None,
        uncertainty=None,
        lang="en_US",
    ):

        self.value: float = value
        self.unit: Unit = unit
        self.surface: str = surface
        self.span: Tuple[int, int] = span
        self.uncertainty: float = uncertainty
        self.lang: str = lang

    def __repr__(self):

        msg = 'Quantity(%g, "%s")'
        msg = msg % (self.value, repr(self.unit))
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (
                self.value == other.value
                and self.unit == other.unit
                and self.surface == other.surface
                and self.span == other.span
                and self.uncertainty == other.uncertainty
            )
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):
        return self.to_spoken(self.lang)

    def to_spoken(self, lang=None):
        """
        Express quantity as a speakable string
        :return: Speakable version of this quantity
        """
        return speak.quantity_to_spoken(self, lang or self.lang)


###############################################################################
class Unit(object):
    """
    Class for a unit (e.g. "gallon").
    """

    def __init__(
        self,
        name=None,
        surfaces=None,
        entity=None,
        uri=None,
        symbols=None,
        dimensions=None,
        currency_code=None,
        original_dimensions=None,
        lang="en_US",
    ):
        """Initialization method."""
        self.name: str = name
        self.surfaces: str = surfaces
        self.entity: Entity = entity
        self.uri: str = uri
        self.symbols: List[str] = symbols
        self.dimensions: List[Dict[str, Any]] = dimensions
        # Stores the untampered dimensions that were parsed from the text
        self.original_dimensions: List[Dict[str, Any]] = original_dimensions
        self.currency_code: str = currency_code
        self.lang: str = lang

    def to_spoken(self, count=1, lang=None) -> str:
        """
        Convert a given unit to the unit in words, correctly inflected.
        :param count: The value of the quantity (i.e. 1 for one watt, 2 for
                      two seconds)
        :param lang: Language of result
        :return: A string with the correctly inflected spoken version of the
                 unit
        """
        return speak.unit_to_spoken(self, count, lang or self.lang)

    def __repr__(self):

        msg = 'Unit(name="%s", entity=Entity("%s"), uri=%s)'
        msg = msg % (self.name, self.entity.name, self.uri)
        return msg

    def __str__(self):
        return self.to_spoken()

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (
                self.name == other.name
                and self.entity == other.entity
                and all(
                    dim1["base"] == dim2["base"] and dim1["power"] == dim2["power"]
                    for dim1, dim2 in zip(self.dimensions, other.dimensions)
                )
            )
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))


###############################################################################
class Entity(object):
    """
    Class for an entity (e.g. "volume").
    """

    def __init__(self, name=None, dimensions=None, uri=None):

        self.name: str = name
        self.dimensions: List[Dict[str, any]] = dimensions
        self.uri: str = uri

    def __repr__(self):

        msg = 'Entity(name="%s", uri=%s)'
        msg = msg % (self.name, self.uri)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.name == other.name and self.dimensions == other.dimensions
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))
