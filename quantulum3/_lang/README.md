Checklist language support
--------------------------

Following is a list, describing all necessary files and functions to
add a new language to the quantulum project.

### load.py

#### `pluralize(singular, count)`

Turn a given word into its plural form based
on the given count (`None` -> plural)
        
#### `number_to_words(number)`

Turn the given float into a pronouncable string


### regex.py

`TEXT_PATTERN` is a regex pattern describing numbers that are spelled out
(at least partly). It can be freely assigned but has to contain the formatting
groups contained in the following example pattern. Also braces that are to be
contained in the resulting regular expression untampered should be escaped (see below on how this is done)

`number_pattern_no_groups` will be replaced by the below number pattern with
no regex groups inserted.

`numberwords_regex` is just a concatenation of all possible numberwords (defined in
regex.py) with `|`, resulting in an "either or" decision for the regex engine.

```pythonregexp
(?:
    (?<![a-zA-Z0-9+.-])    # lookbehind, avoid "Area51"
    {number_pattern_no_groups}
)?
[ -]?(?:{numberwords_regex})
[ -]?(?:{numberwords_regex})?[ -]?(?:{numberwords_regex})?[ -]?(?:{numberwords_regex})?
[ -]?(?:{numberwords_regex})?[ -]?(?:{numberwords_regex})?[ -]?(?:{numberwords_regex})?
```
`NUM_PATTERN` is an regex pattern, describing the general form of a number.
it is important that the below formatting groups are contained in
the regex string (marked by enclosing `{}`). It is defined on a package wide level
and should not have to be changed for localization.

`{{3}}` is a case of escaped braces and will be formatted to `{3}`.

```pythonregexp
(?{number}              # required number
    [+-]?                  #   optional sign
    \.?\d+                 #   required digits
    (?:[{grouping}]\d{{3}})*         #   allowed grouping
    (?{decimals}[{decimal_operators}]\d+)?    #   optional decimals
)
(?{scale}               # optional exponent
    (?:{multipliers})?                #   multiplicative operators
    (?{base}(E|e|\d+)\^?)    #   required exponent prefix
    (?{exponent}[+-]?\d+|[{superscript}])      #   required exponent, superscript or normal
)?
(?{fraction}             # optional fraction
    \ \d+/\d+|\ ?[{unicode_fract}]|/\d+
)?
```

The rest should be self-explanatory by inspecting `en_US/regex.py`.


### parser.py, classifier.py, speak.py

Refer to the corresponding python modules in `en_US`. They contain example code and documentation on the
necessary functions. Most currently included functions are necessary.


### train

This directory contains `json`-files with training data for the classifier for that language.
The serialized objects are lists, containing dicts with two keys

- `unit`: the unit which is associated with the following text
- `text`: a text associated with the unit. It will be tokenized and stemmed
          and then be used as training data for the unit

All `json`-files will be included for training. All other keys in the dictionary
will be ignored. They can be used for comments.

The classifier can later be trained via `scripts/train.py`.


### tests

This directory contains `json`-files with test data for the language.
The tests are subdivided in `expand`, `quantities` and `quantities.ambiguity`.

- `expand`: Test if parsing and replacing in the text, correctly pluralized, works
- `quantities`: Test if units are correctly parsed **without** a classifier
- `quantities.ambiguity`: Test if the classifier succeeds a telling which unit
                          was meant in the text, invoking the classifier.
                          
### units.json, entities.json

These files can be built exactly like the corresponding files on the package top-level.

The defined units and entities will be added if not defined in the gloabl files or
override values for the global entities. `surfaces` and `URI` are fields that should be
overridden by all languages.

