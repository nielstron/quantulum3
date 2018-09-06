quantulum3 |Travis master build state| |Coverage Status|
========================================================

Python library for information extraction of quantities, measurements
and their units from unstructured text. It is Python 3 compatible fork
of `recastrodiaz' fork <https://github.com/recastrodiaz/quantulum>`__ of
`grhawks' fork <https://github.com/grhawk/quantulum>`__ of `the original
by Marco Lagi <https://github.com/marcolagi/quantulum>`__. The
compatability with the newest version of sklearn is based on the fork of
`sohrabtowfighi <https://github.com/sohrabtowfighi/quantulum>`__.

Installation
------------

First, install
`sklearn <http://scikit-learn.org/stable/install.html>`__. Quantulum
would still work without it, but it wouldn't be able to disambiguate
between units with the same name (e.g. *pound* as currency or as unit of
mass).

Then,

.. code:: bash

   $ pip install quantulum3

Contributing
------------

If you’d like to contribute follow these steps: 1. Clone a fork of this
project into your workspace 2. ``pip install pipenv yapf`` 3. Inside the
project folder run ``pipenv install`` 4. Make your changes 5. Run
``format.sh`` 6. Create a Pull Request when having commited your changes

``dev`` build:

|Travis dev build state| |Coverage Status|

Usage
-----

.. code:: python

   >>> from quantulum3 import parser
   >>> quants = parser.parse('I want 2 liters of wine')
   >>> quants
   [Quantity(2, 'litre')]

The *Quantity* class stores the surface of the original text it was
extracted from, as well as the (start, end) positions of the match:

.. code:: python

   >>> quants[0].surface
   u'2 liters'
   >>> quants[0].span
   (7, 15)

An inline parser that embeds the parsed quantities in the text is also
available (especially useful for debugging):

.. code:: python

   >>> print parser.inline_parse('I want 2 liters of wine')
   I want 2 liters {Quantity(2, "litre")} of wine

As the parser is also able to parse dimensionless numbers, this library
can also be used for simple number extraction.

.. code:: python

   >>> print parser.parse('I want two')
   [Quantity(2, 'dimensionless')]

Units and entities
------------------

All units (e.g. *litre*) and the entities they are associated to (e.g.
*volume*) are reconciled against WikiPedia:

.. code:: python

   >>> quants[0].unit
   Unit(name="litre", entity=Entity("volume"), uri=https://en.wikipedia.org/wiki/Litre)

   >>> quants[0].unit.entity
   Entity(name="volume", uri=https://en.wikipedia.org/wiki/Volume)

This library includes more than 290 units and 75 entities. It also
parses spelled-out numbers, ranges and uncertainties:

.. code:: python

   >>> parser.parse('I want a gallon of beer')
   [Quantity(1, 'gallon')]

   >>> parser.parse('The LHC smashes proton beams at 12.8–13.0 TeV')
   [Quantity(12.8, "teraelectronvolt"), Quantity(13, "teraelectronvolt")]

   >>> quant = parser.parse('The LHC smashes proton beams at 12.9±0.1 TeV')
   >>> quant[0].uncertainty
   0.1

Non-standard units usually don't have a WikiPedia page. The parser will
still try to guess their underlying entity based on their
dimensionality:

.. code:: python

   >>> parser.parse('Sound travels at 0.34 km/s')[0].unit
   Unit(name="kilometre per second", entity=Entity("speed"), uri=None)

Disambiguation
--------------

If the parser detects an ambiguity, a classifier based on the WikiPedia
pages of the ambiguous units or entities tries to guess the right one:

.. code:: python

   >>> parser.parse('I spent 20 pounds on this!')
   [Quantity(20, "pound sterling")]

   >>> parser.parse('It weighs no more than 20 pounds')
   [Quantity(20, "pound-mass")]

or:

.. code:: python

   >>> text = 'The average density of the Earth is about 5.5x10-3 kg/cm³'
   >>> parser.parse(text)[0].unit.entity
   Entity(name="density", uri=https://en.wikipedia.org/wiki/Density)

   >>> text = 'The amount of O₂ is 2.98e-4 kg per liter of atmosphere'
   >>> parser.parse(text)[0].unit.entity
   Entity(name="concentration", uri=https://en.wikipedia.org/wiki/Concentration)

Manipulation
------------

While quantities cannot be manipulated within this library, there are
many great options out there:

-  `pint <https://pint.readthedocs.org/en/latest/>`__
-  `natu <http://kdavies4.github.io/natu/>`__
-  `quantities <http://python-quantities.readthedocs.org/en/latest/>`__

Extension
---------

See *units.json* for the complete list of units and *entities.json* for
the complete list of entities. The criteria for adding units have been:

-  the unit has (or is redirected to) a WikiPedia page
-  the unit is in common use (e.g. not the `premetric Swedish units of
   measurement <https://en.wikipedia.org/wiki/Swedish_units_of_measurement#Length>`__).

It's easy to extend these two files to the units/entities of interest.
Here is an example of an entry in *entities.json*:

.. code:: python

   {
       "name": "speed",
       "dimensions": [{"base": "length", "power": 1}, {"base": "time", "power": -1}],
       "URI": "https://en.wikipedia.org/wiki/Speed"
   }

-  *name* and *URI* are self explanatory.
-  *dimensions* is the dimensionality, a list of dictionaries each
   having a *base* (the name of another entity) and a *power* (an
   integer, can be negative).

Here is an example of an entry in *units.json*:

.. code:: python

   {
       "name": "metre per second",
       "surfaces": ["metre per second", "meter per second"],
       "entity": "speed",
       "URI": "https://en.wikipedia.org/wiki/Metre_per_second",
       "dimensions": [{"base": "metre", "power": 1}, {"base": "second", "power": -1}],
       "symbols": ["mps"]
   }

-  *name* and *URI* are self explanatory.
-  *surfaces* is a list of strings that refer to that unit. The library
   takes care of plurals, no need to specify them.
-  *entity* is the name of an entity in *entities.json*
-  *dimensions* follows the same schema as in *entities.json*, but the
   *base* is the name of another unit, not of another entity.
-  *symbols* is a list of possible symbols and abbreviations for that
   unit.

All fields are case sensitive.

.. |Travis master build state| image:: https://travis-ci.com/nielstron/quantulum3.svg?branch=master
   :target: https://travis-ci.com/nielstron/quantulum3
.. |Coverage Status| image:: https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=master
   :target: https://coveralls.io/github/nielstron/quantulum3?branch=master
.. |Travis dev build state| image:: https://travis-ci.com/nielstron/quantulum3.svg?branch=dev
   :target: https://travis-ci.com/nielstron/quantulum3
.. |Coverage Status| image:: https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=dev
   :target: https://coveralls.io/github/nielstron/quantulum3?branch=dev
