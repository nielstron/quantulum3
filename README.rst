.. image:: https://img.shields.io/pypi/v/quantulum.svg
    :target: https://pypi.python.org/pypi/quantulum
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/quantulum.svg
    :target: https://pypi.python.org/pypi/quantulum
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/quantulum.svg
    :target: https://pypi.python.org/pypi/quantulum
    :alt: Python Versions

.. image:: https://travis-ci.org/marcolagi/quantulum.svg?branch=master
    :target: https://travis-ci.org/marcolagi/quantulum
    :alt: CI

.. image:: https://coveralls.io/repos/github/marcolagi/quantulum/badge.svg?branch=master
    :target: https://coveralls.io/github/marcolagi/quantulum?branch=master
    :alt: Coverage

quantulum
=========

Python library for information extraction of quantities, measurements and their units from unstructured text.

Installation
------------

.. code-block:: bash

    $ pip install quantulum

Usage
-----

.. code-block:: python

    >>> from quantulum import parser
    >>> quants = parser.parse('I want 2 liters of wine')
    >>> quants
    [Quantity(2, 'litre')]

The *Quantity* class stores the surface of the original text it was extracted from, as well as the (start, end) positions of the match:

.. code-block:: python

    >>> quants[0].surface
    u'2 liters'
    >>> quants[0].span
    (7, 15)

An inline parser that embeds the parsed quantities in the text is also available (especially useful for debugging):

.. code-block:: python

    >>> print parser.inline_parse('I want 2 liters of wine')
    I want 2 liters {Quantity(2, "litre")} of wine


Units and entities
------------------

All units (e.g. litre) and the entities they are associated to (e.g. volume) are reconciled against WikiPedia:

.. code-block:: python

    >>> quants[0].unit
    Unit(name="litre", entity=Entity("volume"), uri=https://en.wikipedia.org/wiki/Litre)

    >>> quants[0].unit.entity
    Entity(name="volume", uri="https://en.wikipedia.org/wiki/Volume")

This library includes more than 290 units and 75 entities. It also parses spelled-out numbers, ranges and uncertainties:

.. code-block:: python

    >>> parser.parse('I want a gallon of beer')
    [Quantity(1, 'gallon')]

    >>> parser.parse('The LHC smashes proton beams at 12.8–13.0 TeV')
    [Quantity(12.8, "teraelectronvolt"), Quantity(13, "teraelectronvolt")]

    >>> quant = parser.parse('The LHC smashes proton beams at 12.9±0.1 TeV')
    >>> quant[0].uncertainty
    0.1

Non standard units usually don't have a WikiPedia page. The parser will still try to guess their underlying entity based on their dimensionality:

.. code-block:: python

    >>> parser.parse('Sound travels at 0.34 km/s')[0].unit
    Unit(name="kilometre per second", entity=Entity("speed"), uri=None)


Disambiguation
--------------

If the parser detects an ambiguity, a classifier based on the WikiPedia pages of the ambiguous units or entities tries to guess the right one:

.. code-block:: python

    >>> parser.parse('I spent 20 pounds on this!')
    [Quantity(20, "pound sterling")]

    >>> parser.parse('It weighs no more than 20 pounds')
    [Quantity(20, "pound-mass")]

or:

.. code-block:: python

    >>> text = 'The average density of the Earth is about 5.5x10-3 kg/cm³'
    >>> parser.parse(text)[0].unit.entity
    Entity(name="density", uri=https://en.wikipedia.org/wiki/Density)

    >>> text = 'The amount of O₂ is 2.98e-4 kg per liter of atmosphere'
    >>> parser.parse(text)[0].unit.entity
    Entity(name="concentration", uri=https://en.wikipedia.org/wiki/Concentration)

Manipulation
------------

While quantities cannot be manipulated within this library, there are many great options out there:

- `Pint <https://pint.readthedocs.org/en/latest/>`_
- `Natu <http://kdavies4.github.io/natu/>`_
- `Quantities <http://python-quantities.readthedocs.org/en/latest/>`_

Extension
---------

See *units.json* for the complete list of units and *entities.json* for the complete list of entities. The criteria for adding units have been:

1. the unit has (or is redirected to) a WikiPedia page
1. the unit is in common use (e.g. not the `pre-metric Swedish units of
measurement <https://en.wikipedia.org/wiki/Swedish_units_of_measurement#Length>`_).

It's easy to extend these two files to the units/entities of interest. Here is an example of an entry in *entities.json*:

.. code-block:: python

    {
        "name": "speed",
        "derived": [{"base": "length", "power": 1}, {"base": "time", "power": -1}],
        "URI": "https://en.wikipedia.org/wiki/Speed"
    }

- *name* and *URI* are self explanatory.
- *derived* is the dimensionality, a list of dictionaries each having a *base* (the name of another entity) and a *power* (an integer, can be negative).

Here is an example of an entry in *units.json*:

.. code-block:: python

    {
        "name": "metre per second",
        "surfaces": ["metre per second", "meter per second"],
        "entity": "speed",
        "URI": "https://en.wikipedia.org/wiki/Metre_per_second",
        "derived": [{"base": "metre", "power": 1}, {"base": "second", "power": -1}],
        "symbols": ["mps"]
    }

- *name* and *URI* are self explanatory.
- *surfaces* is a list of strings that refer to that unit. The library takes care of plurals, no need to specify them.
- *entity* is the name of an entity in *entities.json*
- *derived* follows the same schema as in *entities.json*, but the *base* is the name of another unit, not of another entity.
- *symbols* is a list of possible symbols and abbreviations for that unit.

All fields are case sensitive.

