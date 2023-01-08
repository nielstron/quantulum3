#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

import logging
import re
from collections import defaultdict
from fractions import Fraction
from typing import List

from . import classes as cls
from . import disambiguate as dis
from . import language, load
from . import regex as reg

_LOGGER = logging.getLogger(__name__)


def _get_parser(lang="en_US"):
    """
    Get parser module for given language
    :param lang:
    :return:
    """
    return language.get("parser", lang)


###############################################################################
def extract_spellout_values(text, lang="en_US"):
    """
    Convert spelled out numbers in a given text to digits.
    """
    return _get_parser(lang).extract_spellout_values(text)


###############################################################################
def substitute_values(text, values):
    """
    Convert spelled out numbers in a given text to digits.
    """

    shift, final_text, shifts = 0, text, defaultdict(int)
    for value in values:
        first = value["old_span"][0] + shift
        second = value["old_span"][1] + shift
        final_text = final_text[0:first] + value["new_surface"] + final_text[second:]
        shift += len(value["new_surface"]) - len(value["old_surface"])
        for char in range(first + 1, len(final_text)):
            shifts[char] = shift

    _LOGGER.debug('Text after numeric conversion: "%s"', final_text)

    return final_text, shifts


###############################################################################
def words_before_span(text, span, k):
    if span[0] == 0:
        return []
    return [w.strip().lower() for w in text[: span[0]].split()[-k:]]


###############################################################################
def is_coordinated(quantity1, quantity2, context, lang="en_US"):
    return _get_parser(lang).is_coordinated(quantity1, quantity2, context)


def is_ranged(quantity1, quantity2, context, lang="en_US"):
    return _get_parser(lang).is_ranged(quantity1, quantity2, context)


###############################################################################
def get_values(item, lang="en_US"):
    """
    Extract value from regex hit. context is the enclosing text on which the regex hit.
    """

    def callback(pattern):
        return " %s" % (reg.unicode_fractions()[pattern.group(0)])

    fracs = r"|".join(reg.unicode_fractions())

    value = item.group("value")
    # Remove grouping operators
    value = re.sub(
        r"(?<=\d)[%s](?=\d{3})" % reg.grouping_operators_regex(lang), "", value
    )
    # Replace unusual exponents by e (including e)
    value = re.sub(
        r"(?<=\d)(%s)(e|E|10)\^?" % reg.multiplication_operators_regex(lang), "e", value
    )
    # calculate other exponents
    value, factors = resolve_exponents(value)
    _LOGGER.debug("After exponent resolution: {}".format(value))

    value = re.sub(fracs, callback, value, re.IGNORECASE)

    range_separator = re.findall(
        r"\d+ ?((?:-\ )?(?:%s)) ?\d" % "|".join(reg.ranges(lang)), value
    )

    uncer_separator = re.findall(
        r"\d+ ?(%s) ?\d" % "|".join(reg.uncertainties(lang)), value
    )
    fract_separator = re.findall(r"\d+/\d+", value)

    value = re.sub(" +", " ", value)
    uncertainty = None
    if range_separator:
        # A range just describes an uncertain quantity
        values = value.split(range_separator[0])
        values = [
            float(re.sub(r"-$", "", v)) * factors[i] for i, v in enumerate(values)
        ]
        if values[1] < values[0]:
            raise ValueError(
                "Invalid range, with second item being smaller than the first item"
            )
        mean = sum(values) / len(values)
        uncertainty = mean - min(values)
        values = [mean]
    elif uncer_separator:
        values = [float(i) for i in value.split(uncer_separator[0])]
        uncertainty = values[1] * factors[1]
        values = [values[0] * factors[0]]
    elif fract_separator:
        values = value.split()
        try:
            if len(values) > 1:
                values = [float(values[0]) * factors[0] + float(Fraction(values[1]))]
            else:
                values = [float(Fraction(values[0]))]
        except ZeroDivisionError as e:
            raise ValueError("{} is not a number".format(values[0]), e)
    else:
        values = [float(re.sub(r"-$", "", value)) * factors[0]]

    _LOGGER.debug("\tUncertainty: %s", uncertainty)
    _LOGGER.debug("\tValues: %s", values)

    return uncertainty, values


###############################################################################
def resolve_exponents(value, lang="en_US"):
    """Resolve unusual exponents (like 2^4) and return substituted string and
       factor

    Params:
        value: str, string with only one value
    Returns:
        str, string with basis and exponent removed
        array of float, factors for multiplication

    """
    factors = []
    matches = re.finditer(
        reg.number_pattern_groups(lang), value, re.IGNORECASE | re.VERBOSE
    )
    for item in matches:
        if item.group("base") and item.group("exponent"):
            base = item.group("base")
            exp = item.group("exponent")
            if base in ["e", "E"]:
                # already handled by float
                factors.append(1)
                continue
                # exp = '10'
            # Expect that in a pure decimal base,
            # either ^ or superscript notation is used
            if re.match(r"\d+\^?", base):
                if not (
                    "^" in base
                    or re.match(r"[%s]" % reg.unicode_superscript_regex(), exp)
                ):
                    factors.append(1)
                    continue
            for superscript, substitute in reg.unicode_superscript().items():
                exp.replace(superscript, substitute)
            exp = float(exp)
            base = float(base.replace("^", ""))
            factor = base**exp
            stripped = str(value).replace(item.group("scale"), "")
            value = stripped
            factors.append(factor)
            _LOGGER.debug(
                "Replaced {} by factor {}".format(item.group("scale"), factor)
            )
        else:
            factors.append(1)
            continue
    return value, factors


###############################################################################
def build_unit_name(dimensions, lang="en_US"):
    """
    Build the name of the unit from its dimensions.
    """
    name = _get_parser(lang).name_from_dimensions(dimensions)

    _LOGGER.debug("\tUnit inferred name: %s", name)

    return name


###############################################################################
def get_unit_from_dimensions(dimensions, text, lang="en_US"):
    """
    Reconcile a unit based on its dimensionality.
    """

    key = load.get_key_from_dimensions(dimensions)

    try:
        unit = load.units(lang).derived[key]
    except KeyError:
        _LOGGER.debug("\tCould not find unit for: %s", key)
        unit = cls.Unit(
            name=build_unit_name(dimensions, lang),
            dimensions=dimensions,
            entity=get_entity_from_dimensions(dimensions, text, lang),
        )

    # Carry on original composition
    unit.original_dimensions = dimensions
    return unit


def name_from_dimensions(dimensions, lang="en_US"):
    """
    Build the name of a unit from its dimensions.
    Param:
        dimensions: List of dimensions
    """
    return _get_parser(lang).name_from_dimensions(dimensions)


def infer_name(unit):
    """
    Return unit name based on dimensions
    :return: new name of this unit
    """
    name = name_from_dimensions(unit.dimensions) if unit.dimensions else None
    return name


###############################################################################
def get_entity_from_dimensions(dimensions, text, lang="en_US"):
    """
    Infer the underlying entity of a unit (e.g. "volume" for "m^3") based on
    its dimensionality.
    """

    new_derived = [
        {"base": load.units(lang).names[i["base"]].entity.name, "power": i["power"]}
        for i in dimensions
    ]

    final_derived = sorted(new_derived, key=lambda x: x["base"])
    key = load.get_key_from_dimensions(final_derived)

    ent = dis.disambiguate_entity(key, text, lang)
    if ent is None:
        _LOGGER.debug("\tCould not find entity for: %s", key)
        ent = cls.Entity(name="unknown", dimensions=new_derived)

    return ent


###############################################################################
def parse_unit(item, unit, slash, lang="en_US"):
    """
    Parse surface and power from unit text.
    """
    return _get_parser(lang).parse_unit(item, unit, slash)

def compact_matches(item):
  res = {}
  starts = {}
  groups = item.groupdict()
  unit_index = 1
  op_index = 1
  if "prefix" in groups and groups["prefix"]:
    res["prefix"] = groups["prefix"]
  if "value" in groups and groups["value"]:
    res["value"] = groups["value"]
  op_acum = ""
  for i in [1,2,3,4]:
    op = groups.get(f"operator{i}", None)
    un = groups.get(f"unit{i}", None)
    if op and un: #op.strip():
      res[f"operator{op_index}"] = op_acum + op
      starts[f"operator{op_index}"] = item.start(f"operator{i}")
      op_index += 1
      op_acum = ""
    if op and not un:
      op_acum += op
    if un:
      res[f"unit{unit_index}"] = un
      starts[f"unit{unit_index}"] = item.start(f"unit{i}")
      unit_index += 1
      if op_index < unit_index: op_index = unit_index
  print("ORIG", groups)
  print("COMP", res)
  return FakeItem(res, item, starts)
  
class FakeItem:
  def __init__(self, d, item, starts):
    print("created with", d)
    self.d = d
    self.item = item
    self.starts = starts

  def group(self, g):
    return self.d.get(g, None)

  def end(self): return self.item.end()
  def start(self, g=None):
    if g is None: return self.item.start()
    return self.starts[g]
  

###############################################################################
def get_unit(item, text, lang="en_US"):
    """
    Extract unit from regex hit.
    """

    group_units = ["prefix", "unit1", "unit2", "unit3", "unit4"]
    group_operators = ["operator1", "operator2", "operator3", "operator4"]
    # How much of the end is removed because of an "incorrect" regex match
    unit_shortening = 0
    print(item.groupdict())

    item_units = [item.group(i) for i in group_units if item.group(i)]
    print("unit:", item_units)

    item = compact_matches(item)
    if len(item_units) == 0:
        unit = load.units(lang).names["dimensionless"]
    else:
        derived, slash = [], False
        multiplication_operator = False
        for index in range(0, 5):
            unit = item.group(group_units[index])
            operator_index = None if index < 1 else group_operators[index - 1]
            operator = None if index < 1 else item.group(operator_index)
            print(index, "O", operator, "U", unit)

            # disallow spaces as operators in units expressed in their symbols
            # Enforce consistency among multiplication and division operators
            # Single exceptions are colloquial number abbreviations (5k miles)
            if operator in reg.multiplication_operators(lang) or (
                operator is None
                and unit
                and not (index == 1 and unit in reg.suffixes(lang))
            ):
                if multiplication_operator != operator and not (
                    index == 1 and str(operator).isspace()
                ):
                    if multiplication_operator is False:
                        multiplication_operator = operator
                    else:
                        # Cut if inconsistent multiplication operator
                        # treat the None operator differently - remove the
                        # whole word of it
                        if operator is None:
                            # For this, use the last consistent operator
                            # (before the current) with a space
                            # which should always be the preceding operator
                            derived.pop()
                            operator_index = group_operators[index - 2]
                        # Remove (original length - new end) characters
                        unit_shortening = item.end() - item.start(operator_index)
                        _LOGGER.debug(
                            "Because operator inconsistency, cut from "
                            "operator: '{}', new surface: {}".format(
                                operator,
                                text[item.start() : item.end() - unit_shortening],
                            )
                        )
                        break

            # Determine whether a negative power has to be applied to following
            # units
            if operator and not slash:
                slash = any(i in operator for i in reg.division_operators(lang))
            # Determine which unit follows
            if unit:
                unit_surface, power = parse_unit(item, unit, slash, lang)
                base = dis.disambiguate_unit(unit_surface, text, lang)
                derived += [{"base": base, "power": power, "surface": unit_surface}]

        unit = get_unit_from_dimensions(derived, text, lang)

    _LOGGER.debug("\tUnit: %s", unit)
    _LOGGER.debug("\tEntity: %s", unit.entity)

    return unit, unit_shortening


###############################################################################
def get_surface(shifts, orig_text, item, text, unit_shortening=0):
    """
    Extract surface from regex hit.
    """

    # handle cut end
    span = (item.start(), item.end() - unit_shortening)
    # extend with as many spaces as are possible (this is to handle cleaned text)
    i = span[1]
    while i < len(text) and text[i] == " ":
        i += 1
    span = (span[0], i)

    _LOGGER.debug('\tInitial span: %s ("%s")', span, text[span[0] : span[1]])

    real_span = (span[0] - shifts[span[0]], span[1] - shifts[span[1] - 1])
    surface = orig_text[real_span[0] : real_span[1]]
    _LOGGER.debug('\tShifted span: %s ("%s")', real_span, surface)

    while any(surface.endswith(i) for i in [" ", "-"]):
        surface = surface[:-1]
        real_span = (real_span[0], real_span[1] - 1)

    while surface.startswith(" "):
        surface = surface[1:]
        real_span = (real_span[0] + 1, real_span[1])

    _LOGGER.debug('\tFinal span: %s ("%s")', real_span, surface)
    return surface, real_span


###############################################################################
def is_quote_artifact(orig_text, span):
    """
    Distinguish between quotes and units.
    """

    res = False
    cursor = re.finditer(r'["\'][^ .,:;?!()*+-].*?["\']', orig_text)

    for item in cursor:
        if span[0] <= item.span()[1] <= span[1]:
            res = item
            break

    return res


###############################################################################
def build_quantity(
    orig_text, text, item, values, unit, surface, span, uncert, lang="en_US"
):
    """
    Build a Quantity object out of extracted information.
    Takes care of caveats and common errors
    """
    return _get_parser(lang).build_quantity(
        orig_text, text, item, values, unit, surface, span, uncert
    )


###############################################################################
def clean_text(text, lang="en_US"):
    """
    Clean text before parsing.
    """

    # Replace a few nasty unicode characters with their ASCII equivalent
    maps = {"×": "x", "–": "-", "−": "-"}
    for element in maps:
        text = text.replace(element, maps[element])

    # Language specific cleaning
    text = _get_parser(lang).clean_text(text)

    _LOGGER.debug('Clean text: "%s"', text)

    return text


###############################################################################
def extract_range_ands(text, lang="en_US"):
    return _get_parser(lang).extract_range_ands(text)


###############################################################################
def handle_consecutive_quantities(quantities, context):
    """
    [45] and/or [50 mg] --> add unit to first [45 mg] [50 mg]
    between [44 mg] and [50 mg] --> range [47+/-3 mg]
    [44 mg] to [50 mg] --> range [47+/-3 mg]
    """
    if len(quantities) < 1:
        return quantities

    results = []
    skip_next = False
    for q1, q2 in zip(quantities, quantities[1:]):
        if skip_next:
            skip_next = False
            continue
        range_span = is_ranged(q1, q2, context)
        if range_span:
            if q1.unit.name == q2.unit.name or q1.unit.name == "dimensionless":
                if (
                    q1.uncertainty == None
                    and q2.uncertainty == None
                    and q1.value != q2.value
                ):
                    a, b = (q1, q2) if q2.value > q1.value else (q2, q1)
                    value = (a.value + b.value) / 2.0
                    uncertainty = b.value - value
                    surface = context[range_span[0] : range_span[1]]
                    q1 = q1.with_vals(
                        uncertainty=uncertainty,
                        value=value,
                        unit=q2.unit,
                        span=range_span,
                        surface=surface,
                    )
                    skip_next = True
        elif is_coordinated(q1, q2, context):
            if q1.unit.name == "dimensionless":
                q1 = q1.with_vals(unit=q2.unit)
        results.append(q1)
    if not skip_next:
        results.append(quantities[-1])
    return results


###############################################################################
def parse(text, lang="en_US", verbose=False) -> List[cls.Quantity]:
    """
    Extract all quantities from unstructured text.
    """

    log_format = "%(asctime)s --- %(message)s"
    logging.basicConfig(format=log_format)

    if verbose:  # pragma: no cover
        prev_level = logging.root.getEffectiveLevel()
        logging.root.setLevel(logging.DEBUG)
        _LOGGER.debug("Verbose mode")

    orig_text = text
    _LOGGER.debug('Original text: "%s"', orig_text)

    text = clean_text(text, lang)
    values = extract_spellout_values(text, lang)
    text, shifts = substitute_values(text, values)

    quantities = []
    for item in reg.units_regex(lang).finditer(text):

        groups = dict([i for i in item.groupdict().items() if i[1] and i[1].strip()])
        _LOGGER.debug("Quantity found: %s", groups)
        print("XX",groups)

        try:
            uncert, values = get_values(item, lang)

            unit, unit_shortening = get_unit(item, text)
            surface, span = get_surface(shifts, orig_text, item, text, unit_shortening)
            objs = build_quantity(
                orig_text, text, item, values, unit, surface, span, uncert, lang
            )
            if objs is not None:
                quantities += objs
        except ValueError as err:
            _LOGGER.debug("Could not parse quantity: %s", err)

    if verbose:  # pragma: no cover
        logging.root.setLevel(prev_level)

    quantities = handle_consecutive_quantities(quantities, text)
    return quantities


###############################################################################
def inline_parse(text, verbose=False):  # pragma: no cover
    """
    Extract all quantities from unstructured text.
    """

    parsed = parse(text, verbose=verbose)

    shift = 0
    for quantity in parsed:
        index = quantity.span[1] + shift
        to_add = " {" + str(quantity) + "}"
        text = text[0:index] + to_add + text[index:]
        shift += len(to_add)

    return text


###############################################################################
def inline_parse_and_replace(text, lang="en_US", verbose=False):  # pragma: no cover
    """
    Parse text and replace with the standardised quantities as string
    """

    parsed = parse(text, lang=lang, verbose=verbose)

    shift = 0
    for quantity in parsed:
        index_start = quantity.span[0] + shift
        index_end = quantity.span[1] + shift
        to_add = str(quantity)
        text = text[0:index_start] + to_add + text[index_end:]
        shift += len(to_add) - (quantity.span[1] - quantity.span[0])

    return text


###############################################################################
def inline_parse_and_expand(text, lang="en_US", verbose=False):
    """
    Parse text and replace qunatities with speakable version
    """
    parsed = parse(text, lang=lang, verbose=verbose)

    shift = 0
    for quantity in parsed:
        index_start = quantity.span[0] + shift
        index_end = quantity.span[1] + shift
        to_add = quantity.to_spoken()
        text = text[0:index_start] + to_add + text[index_end:]
        shift += len(to_add) - (quantity.span[1] - quantity.span[0])

    return text
