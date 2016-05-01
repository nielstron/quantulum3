#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:mod:`Quantulum` classes.
'''

################################################################################
class Quantity(object):

    '''
    Class for a quantity (e.g. "4.2 gallons").
    '''

    def __init__(self, value=None, unit=None, surface=None, span=None,
                 uncertainty=None):

        self.value = value
        self.unit = unit
        self.surface = surface
        self.span = span
        self.uncertainty = uncertainty

    def __repr__(self):

        msg = u'Quantity(%g, "%s")'
        msg = msg % (self.value, self.unit.name)
        return msg.encode('utf-8')

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)


################################################################################
class Unit(object):

    '''
    Class for a unit (e.g. "gallon").
    '''

    def __init__(self, name=None, surfaces=None, entity=None, uri=None,
                 symbols=None, derived=None):

        self.name = name
        self.surfaces = surfaces
        self.entity = entity
        self.uri = uri
        self.symbols = symbols
        self.derived = derived

    def __repr__(self):

        msg = u'Unit(name="%s", entity=Entity("%s"), uri=%s)'
        msg = msg % (self.name, self.entity.name, self.uri)
        return msg.encode('utf-8')

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)


################################################################################
class Entity(object):

    '''
    Class for an entity (e.g. "volume").
    '''

    def __init__(self, name=None, derived=None, uri=None):

        self.name = name
        self.derived = derived
        self.uri = uri

    def __repr__(self):

        msg = u'Entity(name="%s", uri=%s)'
        msg = msg % (self.name, self.uri)
        return msg.encode('utf-8')

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

