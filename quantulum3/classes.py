#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classes.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from . import speak


class JSONMIxin(ABC):
    @abstractmethod
    def to_dict(self):
        pass  # pragma: no cover

    def to_json(self, *args, **kwargs) -> str:
        """
        Create a JSON representation of this object.

        :param args: Arguments to pass to the to_dict method
        :param kwargs: Keyword arguments to pass to the to_dict method

        :return: JSON representation of this object
        """
        return json.dumps(self.to_dict(*args, **kwargs))

    @classmethod
    @abstractmethod
    def from_dict(cls, ddict: Dict):
        pass  # pragma: no cover

    @classmethod
    def from_json(cls, json_str: str):
        """
        Create an object from a JSON string.

        :param json_str: JSON string to convert to an object

        :return: Object created from the JSON string
        """
        return cls.from_dict(json.loads(json_str))


###############################################################################
class Entity(JSONMIxin, object):
    """
    Class for an entity (e.g. "volume").
    """

    def __init__(
        self,
        name: str,
        dimensions: List[Dict[str, Any]] = [],
        uri: Optional[str] = None,
    ):
        self.name = name
        self.dimensions = dimensions
        self.uri = uri

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

    def to_dict(self) -> Dict:
        """
        Create a dictionary representation of this entity.

        :return: Dictionary representation of this entity
        """
        return {
            "name": self.name,
            "dimensions": self.dimensions,
            "uri": self.uri,
        }

    @classmethod
    def from_dict(cls, ddict: Dict) -> "Entity":
        """
        Create an entity from a dictionary representation.

        :param ddict: Dictionary representation of an entity (as produced by to_dict)

        :return: Entity created from the dictionary representation
        """
        return cls(
            name=ddict["name"],
            dimensions=ddict["dimensions"],
            uri=ddict["uri"],
        )


###############################################################################
class Unit(JSONMIxin, object):
    """
    Class for a unit (e.g. "gallon").
    """

    def __init__(
        self,
        name: str,
        entity: Entity,
        surfaces: List[str] = [],
        uri: Optional[str] = None,
        symbols: List[str] = [],
        dimensions: List[Dict[str, Any]] = [],
        currency_code: Optional[str] = None,
        original_dimensions: Optional[List[Dict[str, Any]]] = None,
        lang="en_US",
    ):
        """Initialization method."""
        self.name = name
        self.surfaces = surfaces
        self.entity = entity
        self.uri = uri
        self.symbols = symbols
        self.dimensions = dimensions
        # Stores the untampered dimensions that were parsed from the text
        self.original_dimensions = original_dimensions
        self.currency_code = currency_code
        self.lang = lang

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

    def to_dict(self, include_entity_dict: bool = False) -> Dict:
        """
        Create a dictionary representation of this unit.

        :param include_entity: When False, just the name of the entity is included, when True the full entity is included. Default is False.

        :return: Dictionary representation of this unit
        """
        ddict = {
            "name": self.name,
            "surfaces": self.surfaces,
            "entity": self.entity.name,
            "uri": self.uri,
            "symbols": self.symbols,
            "dimensions": self.dimensions,
            "original_dimensions": self.original_dimensions,
            "currency_code": self.currency_code,
            "lang": self.lang,
        }

        if include_entity_dict:
            ddict["entity"] = self.entity.to_dict()

        return ddict

    @classmethod
    def from_dict(cls, ddict: Dict) -> "Unit":
        """
        Create a unit from a dictionary representation.

        :param ddict: Dictionary representation of a unit (as produced by to_dict)

        :return: Unit created from the dictionary representation
        """
        return cls(
            name=ddict["name"],
            surfaces=ddict["surfaces"],
            entity=Entity.from_dict(ddict["entity"]),
            uri=ddict["uri"],
            symbols=ddict["symbols"],
            dimensions=ddict["dimensions"],
            original_dimensions=ddict["original_dimensions"],
            currency_code=ddict["currency_code"],
            lang=ddict["lang"],
        )


###############################################################################


class Quantity(JSONMIxin, object):
    """
    Class for a quantity (e.g. "4.2 gallons").
    """

    def __init__(
        self,
        value: float,
        unit: Unit,
        surface: Optional[str] = None,
        span: Optional[Tuple[int, int]] = None,
        uncertainty: Optional[float] = None,
        lang="en_US",
    ):
        self.value = value
        self.unit = unit
        self.surface = surface
        self.span = span
        self.uncertainty = uncertainty
        self.lang = lang

    def with_vals(
        self,
        value=None,
        unit=None,
        surface=None,
        span=None,
        uncertainty=None,
        lang=None,
    ):
        return Quantity(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            surface if surface is not None else self.surface,
            span if span is not None else self.span,
            uncertainty if uncertainty is not None else self.uncertainty,
            lang if lang is not None else self.lang,
        )

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

    def to_dict(
        self, include_unit_dict: bool = False, include_entity_dict: bool = False
    ) -> Dict:
        """
        Create a dictionary representation of this quantity

        :param include_unit: When False, just the name of the unit is included, when True, the full unit is included. Defaults to False
        :param include_entity: When False, just the name of the entity is included, when True, the full entity is included. Defaults to False. Only used when include_unit is True.

        :return: Dictionary representation of this quantity
        """
        ddict = {
            "value": self.value,
            "unit": self.unit.name,
            "entity": self.unit.entity.name,
            "surface": self.surface,
            "span": self.span,
            "uncertainty": self.uncertainty,
            "lang": self.lang,
        }

        if include_unit_dict:
            ddict["unit"] = self.unit.to_dict(include_entity_dict)

        return ddict

    @classmethod
    def from_dict(cls, ddict: Dict) -> "Quantity":
        """
        Create a quantity from a dictionary representation.

        :param ddict: Dictionary representation of a quantity (as produced by to_dict)

        :return: Quantity created from the dictionary representation
        """
        return cls(
            value=ddict["value"],
            unit=Unit.from_dict(ddict["unit"]),
            surface=ddict["surface"],
            span=tuple(ddict["span"]),
            uncertainty=ddict["uncertainty"],
            lang=ddict["lang"],
        )
