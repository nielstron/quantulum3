quantulum3
==========
 [![Travis master build state](https://travis-ci.com/nielstron/quantulum3.svg?branch=master "Travis master build state")](https://travis-ci.com/nielstron/quantulum3)
 [![Coverage Status](https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=master)](https://coveralls.io/github/nielstron/quantulum3?branch=master)
 [![PyPI version](https://badge.fury.io/py/quantulum3.svg)](https://pypi.org/project/quantulum3/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quantulum3.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/quantulum3.svg)](https://pypi.org/project/quantulum3/)
 
Python library for information extraction of quantities, measurements
and their units from unstructured text. It is able to disambiguate between similar
looking units based on their *k-nearest neighbours* in their [GloVe](https://nlp.stanford.edu/projects/glove/) vector representation
and their [Wikipedia](https://en.wikipedia.org/) page.

It is Python 3 compatible fork of [recastrodiaz\'
fork](https://github.com/recastrodiaz/quantulum) of [grhawks\'
fork](https://github.com/grhawk/quantulum) of [the original by Marco
Lagi](https://github.com/marcolagi/quantulum).
The compatability with the newest version of sklearn is based on
the fork of [sohrabtowfighi](https://github.com/sohrabtowfighi/quantulum).

Installation
------------

First, install [`numpy`](https://pypi.org/project/numpy/), [`scipy`](https://www.scipy.org/install.html) and [`sklearn`](http://scikit-learn.org/stable/install.html).
Quantulum would still work without it, but it wouldn\'t be able to
disambiguate between units with the same name (e.g. *pound* as currency
or as unit of mass).

Then,

```bash
$ pip install quantulum3
```

Usage
-----

```pycon
>>> from quantulum3 import parser
>>> quants = parser.parse('I want 2 liters of wine')
>>> quants
[Quantity(2, 'litre')]
```

The *Quantity* class stores the surface of the original text it was
extracted from, as well as the (start, end) positions of the match:

```pycon
>>> quants[0].surface
u'2 liters'
>>> quants[0].span
(7, 15)
```

An inline parser that embeds the parsed quantities in the text is also
available (especially useful for debugging):

```pycon
>>> print parser.inline_parse('I want 2 liters of wine')
I want 2 liters {Quantity(2, "litre")} of wine
```

As the parser is also able to parse dimensionless numbers,
this library can also be used for simple number extraction.

```pycon
>>> print parser.parse('I want two')
[Quantity(2, 'dimensionless')]
```

Units and entities
------------------

All units (e.g. *litre*) and the entities they are associated to (e.g.
*volume*) are reconciled against WikiPedia:

```pycon
>>> quants[0].unit
Unit(name="litre", entity=Entity("volume"), uri=https://en.wikipedia.org/wiki/Litre)

>>> quants[0].unit.entity
Entity(name="volume", uri=https://en.wikipedia.org/wiki/Volume)
```

This library includes more than 290 units and 75 entities. It also
parses spelled-out numbers, ranges and uncertainties:

```pycon
>>> parser.parse('I want a gallon of beer')
[Quantity(1, 'gallon')]

>>> parser.parse('The LHC smashes proton beams at 12.8–13.0 TeV')
[Quantity(12.8, "teraelectronvolt"), Quantity(13, "teraelectronvolt")]

>>> quant = parser.parse('The LHC smashes proton beams at 12.9±0.1 TeV')
>>> quant[0].uncertainty
0.1
```

Non-standard units usually don\'t have a WikiPedia page. The parser will
still try to guess their underlying entity based on their
dimensionality:

```pycon
>>> parser.parse('Sound travels at 0.34 km/s')[0].unit
Unit(name="kilometre per second", entity=Entity("speed"), uri=None)
```

Disambiguation
--------------

If the parser detects an ambiguity, a classifier based on the WikiPedia
pages of the ambiguous units or entities tries to guess the right one:

```pycon
>>> parser.parse('I spent 20 pounds on this!')
[Quantity(20, "pound sterling")]

>>> parser.parse('It weighs no more than 20 pounds')
[Quantity(20, "pound-mass")]
```

or:

```pycon
>>> text = 'The average density of the Earth is about 5.5x10-3 kg/cm³'
>>> parser.parse(text)[0].unit.entity
Entity(name="density", uri=https://en.wikipedia.org/wiki/Density)

>>> text = 'The amount of O₂ is 2.98e-4 kg per liter of atmosphere'
>>> parser.parse(text)[0].unit.entity
Entity(name="concentration", uri=https://en.wikipedia.org/wiki/Concentration)
```

In addition to that, the classifier is trained on the most similar words to
all of the units surfaces, according to their distance in [GloVe](https://nlp.stanford.edu/projects/glove/)
vector representation.

Training the classifier
-----------------------

If you want to train the classifier yourself, in addition to the packages above, you'll also need
the packages `stemming` and `wikipedia`. 

You could also [download requirements_classifier.txt](https://raw.githubusercontent.com/nielstron/quantulum3/dev/requirements_classifier.txt)
and run 
```bash
$ pip install -r requirements_classifier.txt
```
Use the script `scripts/train.py` or the method `train_classifier` in `quantulum3.classifier` to train the classifier.

If you want to create a new or different `similars.json`, install `pymagnitude`.

For the extraction of nearest neighbours from a vector word representation file, 
use `scripts/extract_vere.py`. It automatically extracts the `k` nearest neighbours
in vector space of the vector representation for each of the possible surfaces
of the ambiguous units. The resulting neighbours are stored in `quantulum3/similars.json`
and automatically included for training.

The file provided should be in `.magnitude` format as other formats are first
converted to a `.magnitude` file on-the-run. Check out
[pre-formatted Magnitude formatted word-embeddings](https://github.com/plasticityai/magnitude#pre-converted-magnitude-formats-of-popular-embeddings-models)
and [Magnitude](https://github.com/plasticityai/magnitude) for more information.


Manipulation
------------

While quantities cannot be manipulated within this library, there are
many great options out there:

-   [pint](https://pint.readthedocs.org/en/latest/)
-   [natu](http://kdavies4.github.io/natu/)
-   [quantities](http://python-quantities.readthedocs.org/en/latest/)

Spoken version
--------------

Quantulum classes include methods to convert them to a speakable unit.

```pycon
>>> parser.parse("Gimme 10e9 GW now!")[0].to_spoken()
ten billion gigawatts
>>> parser.inline_parse_and_expand("Gimme $1e10 now and also 1 TW and 0.5 J!")
Gimme ten billion dollars now and also one terawatt and zero point five joules!
```

Extension
---------

See *units.json* for the complete list of units and *entities.json* for
the complete list of entities. The criteria for adding units have been:

-   the unit has (or is redirected to) a WikiPedia page
-   the unit is in common use (e.g. not the [premetric Swedish units of
    measurement](https://en.wikipedia.org/wiki/Swedish_units_of_measurement#Length)).

It\'s easy to extend these two files to the units/entities of interest.
Here is an example of an entry in *entities.json*:

```json
{
    "name": "speed",
    "dimensions": [{"base": "length", "power": 1}, {"base": "time", "power": -1}],
    "URI": "https://en.wikipedia.org/wiki/Speed"
}
```

-   *name* is self explanatory.
-   *URI* is the name of the wikipedia page of the entity. (i.e. `https://en.wikipedia.org/wiki/Speed` => `Speed`)
-   *dimensions* is the dimensionality, a list of dictionaries each
    having a *base* (the name of another entity) and a *power* (an
    integer, can be negative).

Here is an example of an entry in *units.json*:

```json
{
    "name": "metre per second",
    "surfaces": ["metre per second", "meter per second"],
    "entity": "speed",
    "URI": "Metre_per_second",
    "dimensions": [{"base": "metre", "power": 1}, {"base": "second", "power": -1}],
    "symbols": ["mps"]
},
{
    "name": "year",
    "surfaces": [ "year", "annum" ],
    "entity": "time",
    "URI": "Year",
    "dimensions": [],
    "symbols": [ "a", "y", "yr" ],
    "prefixes": [ "k", "M", "G", "T", "P", "E" ]
}
```

-   *name* is self explanatory.
-   *URI* follows the same scheme as in the *entities.json*
-   *surfaces* is a list of strings that refer to that unit. The library
    takes care of plurals, no need to specify them.
-   *entity* is the name of an entity in *entities.json*
-   *dimensions* follows the same schema as in *entities.json*, but the
    *base* is the name of another unit, not of another entity.
-   *symbols* is a list of possible symbols and abbreviations for that
    unit.
-   *prefixes* is an optional list. It can contain [Metric](https://en.wikipedia.org/wiki/Metric_prefix) and [Binary prefixes](https://en.wikipedia.org/wiki/Binary_prefix) and
    automatically generates according units. If you want to
    add specifics (like different surfaces) you need to create an entry for that
    prefixes version on its own.

All fields are case sensitive.

Contributing
------------
`dev` build: 

[![Travis dev build state](https://travis-ci.com/nielstron/quantulum3.svg?branch=dev "Travis dev build state")](https://travis-ci.com/nielstron/quantulum3)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=dev)](https://coveralls.io/github/nielstron/quantulum3?branch=dev)

If you'd like to contribute follow these steps:
1. Clone a fork of this project into your workspace
2. Run `pip install -e .` at the root of your development folder.
3. `pip install pipenv` and `pipenv shell`
4. Inside the project folder run `pipenv install --dev`
5. Make your changes
6. Run `scripts/format.sh` and `scripts/build.py` from the package root directory.
7. Test your changes with `coverage run --source=quantulum3 setup.py test` 
(Optional, will be done automatically after pushing)
8. Create a Pull Request when having commited and pushed your changes

Language support
----------------
[![Travis dev build state](https://travis-ci.com/nielstron/quantulum3.svg?branch=language_support "Travis dev build state")](https://travis-ci.com/nielstron/quantulum3)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=language_support)](https://coveralls.io/github/nielstron/quantulum3?branch=dev)

There is a branch for language support, namely `language_support`.
From inspecting the `README` file in the `_lang` subdirectory and
the functions and values given in the new `_lang.en_US` submodule,
one should be able to create own language submodules.
The new language modules should automatically be invoked and be available,
both through the `lang=` keyword argument in the parser functions as well
as in the automatic unittests.

No changes outside the own language submodule folder (i.e. `_lang.de_DE`) should
be necessary. If there are problems implementing a new language, don't hesitate to open an issue.

