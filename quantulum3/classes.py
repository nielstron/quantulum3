#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classes.
"""

# Dependencies
import inflect
import num2words

INFLECT_ENGINE = inflect.engine()

################################################################################


class Quantity(object):
    """
    Class for a quantity (e.g. "4.2 gallons").
    """

    def __init__(self,
                 value=None,
                 unit=None,
                 surface=None,
                 span=None,
                 uncertainty=None):

        self.value = value
        self.unit = unit
        self.surface = surface
        self.span = span
        self.uncertainty = uncertainty

    def __repr__(self):

        msg = 'Quantity(%g, "%s")'
        msg = msg % (self.value, self.unit.name)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (self.value == other.value and self.unit == other.unit
                    and self.surface == other.surface
                    and self.span == other.span
                    and self.uncertainty == other.uncertainty)
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def as_string(self):  # pragma: no cover
        """
        Express the quantity as a normal string
        """

        return '{} {}'.format(self.value, self.unit.name)

    def to_spoken(self):
        """
        Express quantity as a speakable string
        :return: Speakable version of this quantity
        """
        count = self.value
        if self.unit.entity.name == "currency" and self.unit.currency_code:
            try:
                return num2words.num2words(
                    count,
                    lang='en',
                    to='currency',
                    currency=self.unit.currency_code)
            except NotImplementedError:
                pass
        if count.is_integer():
            count = int(count)
        unit_string = self.unit.to_spoken(count)
        return '{}{}{}'.format(
            INFLECT_ENGINE.number_to_words(count),
            " " if len(unit_string) else "", unit_string)


################################################################################
class Unit(object):
    """
    Class for a unit (e.g. "gallon").
    """

    def __init__(self,
                 name=None,
                 surfaces=None,
                 entity=None,
                 uri=None,
                 symbols=None,
                 dimensions=None,
                 currency_code=None):
        """Initialization method."""
        self.name = name
        self.surfaces = surfaces
        self.entity = entity
        self.uri = uri
        self.symbols = symbols
        self.dimensions = dimensions
        self.currency_code = currency_code

    @staticmethod
    def name_from_dimensions(dimensions):
        """
        Build the name of the unit from its dimensions.
        Param:
            dimensions: List of dimensions
        """

        name = ''

        for unit in dimensions:
            if unit['power'] < 0:
                name += 'per '
            power = abs(unit['power'])
            if power == 1:
                name += unit['base']
            elif power == 2:
                name += 'square ' + unit['base']
            elif power == 3:
                name += 'cubic ' + unit['base']
            elif power > 3:
                name += unit['base'] + ' to the %g' % power
            name += ' '

        name = name.strip()

        return name

    def infer_name(self):
        """
        Set own name based on dimensions
        :return: new name of this unit
        """
        self.name = self.name_from_dimensions(
            self.dimensions) if self.dimensions else None
        return self.name

    def to_spoken(self, count=1):
        """
        Convert a given unit to the unit in words, correctly inflected.
        :param count: The value of the quantity (i.e. 1 for one watt, 2 for two seconds)
        :return: A string with the correctly inflected spoken version of the unit
        """
        if self.name == "dimensionless":
            unit_string = ""
        elif self.surfaces:
            unit_string = self.surfaces[0]
            unit_string = INFLECT_ENGINE.plural(unit_string, count)
        else:
            # derived unit
            denominator_dimensions = [
                i for i in self.dimensions if i['power'] > 0
            ]
            denominator_string = self.name_from_dimensions(
                denominator_dimensions)
            plural_denominator_string = INFLECT_ENGINE.plural(
                denominator_string)
            unit_string = self.name.replace(denominator_string,
                                            plural_denominator_string)
        return unit_string

    def __repr__(self):

        msg = 'Unit(name="%s", entity=Entity("%s"), uri=%s)'
        msg = msg % (self.name, self.entity.name, self.uri)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (
                self.name == other.name and self.surfaces == other.surfaces
                and self.entity == other.entity and self.uri == other.uri
                and self.symbols == other.symbols and all(
                    dim1['base'] == dim2['base']
                    and dim1['power'] == dim2['power']
                    for dim1, dim2 in zip(self.dimensions, other.dimensions)))
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))


################################################################################
class Entity(object):
    """
    Class for an entity (e.g. "volume").
    """

    def __init__(self, name=None, dimensions=None, uri=None):

        self.name = name
        self.dimensions = dimensions
        self.uri = uri

    def __repr__(self):

        msg = 'Entity(name="%s", uri=%s)'
        msg = msg % (self.name, self.uri)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (self.name == other.name
                    and self.dimensions == other.dimensions
                    and self.uri == other.uri)
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))
