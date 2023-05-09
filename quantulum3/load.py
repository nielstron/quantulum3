#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, List, Tuple, Union

from . import classes as c
from . import language

TOPDIR = Path(__file__).parent or Path(".")

###############################################################################
_CACHE_DICT = defaultdict(dict)


def clear_caches():
    clear_units_cache()
    clear_entities_cache()
    clear_cache()


def reset_quantities():
    global USE_GENERAL_UNITS, USE_GENERAL_ENTITIES, USE_LANGUAGE_UNITS, USE_LANGUAGE_ENTITIES, USE_CUSTOM_UNITS, USE_CUSTOM_ENTITIES, USE_ADDITIONAL_UNITS, USE_ADDITIONAL_ENTITIES

    USE_GENERAL_UNITS = True
    USE_GENERAL_ENTITIES = True
    USE_LANGUAGE_UNITS = True
    USE_LANGUAGE_ENTITIES = True
    USE_CUSTOM_UNITS = False
    USE_CUSTOM_ENTITIES = False
    USE_ADDITIONAL_UNITS = True
    USE_ADDITIONAL_ENTITIES = True


def clear_cache():
    """
    Useful for testing.
    """
    _CACHE_DICT.clear()


class CustomQuantities:
    def __init__(
        self,
        custom_units: List[Union[str, Path]] = None,
        custom_entities: List[Union[str, Path]] = None,
        use_general_units: bool = False,
        use_language_units: bool = False,
        use_additional_units: bool = True,
        use_general_entities: bool = False,
        use_language_entities: bool = False,
        use_additional_entities: bool = True,
    ):
        """
        Load custom unites and entities into Quantulum via a context manager.

        :param custom_units: list of paths to custom units
        :param custom_entities: list of paths to custom entities
        :param use_general_units: Whether to also load the general units, by default False
        :param use_language_units: Whether to also load the language specific units, by default False
        :param use_additional_units: Whether to also load the additional units, by default True
        """
        self.custom_units = custom_units
        self.custom_entities = custom_entities
        self.use_general_units = use_general_units
        self.use_language_units = use_language_units
        self.use_additional_units = use_additional_units
        self.use_general_entities = use_general_entities
        self.use_language_entities = use_language_entities
        self.use_additional_entities = use_additional_entities

    def __enter__(self):
        self._record_current_state()

        if self.custom_units:
            load_custom_units(
                self.custom_units,
                use_general_units=self.use_general_units,
                use_language_units=self.use_language_units,
                use_additional_units=self.use_additional_units,
            )

        if self.custom_entities:
            load_custom_entities(
                self.custom_entities,
                use_general_entities=self.use_general_entities,
                use_language_entities=self.use_language_entities,
                use_additional_entities=self.use_additional_entities,
            )

    def __exit__(self, exc_type, exc_value, exc_tb):
        # reset flags
        self._reset_state()

    def _record_current_state(self):
        self.previous_general_units = USE_GENERAL_UNITS
        self.previous_general_entities = USE_GENERAL_ENTITIES
        self.previous_language_units = USE_LANGUAGE_UNITS
        self.previous_language_entities = USE_LANGUAGE_ENTITIES
        self.previous_custom_units = USE_CUSTOM_UNITS
        self.previous_custom_entities = USE_CUSTOM_ENTITIES
        self.previous_additional_units = USE_ADDITIONAL_UNITS
        self.previous_additional_entities = USE_ADDITIONAL_ENTITIES

    def _reset_state(self):
        global USE_GENERAL_UNITS, USE_GENERAL_ENTITIES, USE_LANGUAGE_UNITS, USE_LANGUAGE_ENTITIES, USE_CUSTOM_UNITS, USE_CUSTOM_ENTITIES, USE_ADDITIONAL_UNITS, USE_ADDITIONAL_ENTITIES

        USE_GENERAL_UNITS = self.previous_general_units
        USE_GENERAL_ENTITIES = self.previous_general_entities
        USE_LANGUAGE_UNITS = self.previous_language_units
        USE_LANGUAGE_ENTITIES = self.previous_language_entities
        USE_CUSTOM_UNITS = self.previous_custom_units
        USE_CUSTOM_ENTITIES = self.previous_custom_entities
        USE_ADDITIONAL_UNITS = self.previous_additional_units
        USE_ADDITIONAL_ENTITIES = self.previous_additional_entities


def cached(funct):
    """
    Decorator for caching language specific data
    :param funct: the method, dynamically responding to language. Only
                  parameter is lang
    :return: the method, dynamically responding to language but also caching
             results
    """
    assert callable(funct)

    def cached_function(*args, **kwargs):
        # create a hash of args and kwargs

        args_hash = hash((args, frozenset(kwargs.items())))

        try:
            return _CACHE_DICT[id(funct)][args_hash]
        except KeyError:
            result = funct(*args, **kwargs)
            _CACHE_DICT[id(funct)].update({args_hash: result})
            return result

    return cached_function


def object_pairs_hook_defer_duplicate_keys(object_pairs: List[Tuple[str, Any]]):
    keys = [x[0] for x in object_pairs]
    try:
        assert len(set(keys)) == len(keys)
    except AssertionError:
        raise AssertionError(
            "Dictionary has entries with same name: {}".format(
                [object_pairs[i] for i, k in enumerate(keys) if keys.count(k) > 1]
            )
        )
    return dict(object_pairs)


###############################################################################
@cached
def _get_load(lang="en_US"):
    return language.get("load", lang)


GENERAL_UNITS_PATH = TOPDIR.joinpath("units.json")
USE_GENERAL_UNITS = True
GENERAL_ENTITIES_PATH = TOPDIR.joinpath("entities.json")
USE_GENERAL_ENTITIES = True


def LANGUAGE_ENTITIES_PATH(lang="en_US"):
    return TOPDIR.joinpath(language.topdir(lang), "entities.json")


def LANGUAGE_UNITS_PATH(lang="en_US"):
    return TOPDIR.joinpath(language.topdir(lang), "units.json")


USE_LANGUAGE_UNITS = True
USE_LANGUAGE_ENTITIES = True


def _load_json(path_or_string: Union[Path, str]):
    if isinstance(path_or_string, Path):
        with path_or_string.open("r", encoding="utf-8") as jsonfile:
            return jsonfile.read()
    elif isinstance(path_or_string, str) and path_or_string.endswith(".json"):
        with open(path_or_string, "r", encoding="utf-8") as jsonfile:
            return jsonfile.read()
    return path_or_string


def _load_json_dict(path_or_string: Union[Path, str, dict]):
    if isinstance(path_or_string, dict):
        return path_or_string
    return json.loads(
        _load_json(path_or_string),
        object_pairs_hook=object_pairs_hook_defer_duplicate_keys,
    )


CUSTOM_ENTITIES = defaultdict(dict)
USE_CUSTOM_ENTITIES = True

ADDITIONAL_ENTITIES = defaultdict(dict)
USE_ADDITIONAL_ENTITIES = True

CUSTOM_UNITS = defaultdict(dict)
USE_CUSTOM_UNITS = True

ADDITIONAL_UNITS = defaultdict(dict)
USE_ADDITIONAL_UNITS = True


###############################################################################
def to_int_iff_int(value):
    """
    Returns int type number if the value is an integer value
    :param value:
    :return:
    """
    try:
        if int(value) == value:
            return int(value)
    except (TypeError, ValueError):
        pass
    return value


def pluralize(singular, count=None, lang="en_US"):
    # Make spelling integers more natural
    count = to_int_iff_int(count)
    return _get_load(lang).pluralize(singular, count)


def number_to_words(count, lang="en_US"):
    # Make spelling integers more natural
    count = to_int_iff_int(count)
    return _get_load(lang).number_to_words(count)


###############################################################################
METRIC_PREFIXES = {
    "Y": "yotta",
    "Z": "zetta",
    "E": "exa",
    "P": "peta",
    "T": "tera",
    "G": "giga",
    "M": "mega",
    "k": "kilo",
    "h": "hecto",
    "da": "deca",
    "d": "deci",
    "c": "centi",
    "m": "milli",
    "µ": "micro",
    "n": "nano",
    "p": "pico",
    "f": "femto",
    "a": "atto",
    "z": "zepto",
    "y": "yocto",
    "Ki": "kibi",
    "Mi": "mebi",
    "Gi": "gibi",
    "Ti": "tebi",
    "Pi": "pebi",
    "Ei": "exbi",
    "Zi": "zebi",
    "Yi": "yobi",
}


###############################################################################
def get_key_from_dimensions(derived):
    """
    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT dicts.
    """

    return tuple((i["base"], i["power"]) for i in derived)


###############################################################################
class Entities(object):
    def __init__(self, entity_dicts: List[Union[Path, str, dict]]):
        """
        Load entities from JSON file.
        """

        # Merge entity dictionarys
        all_entities = defaultdict(dict)
        for ed in entity_dicts:
            for new_name, new_ent in _load_json_dict(ed).items():
                all_entities[new_name].update(new_ent)

        self.names = dict(
            (
                name,
                c.Entity(
                    name=name,
                    dimensions=props.get("dimensions", []),
                    uri=props.get("URI"),
                ),
            )
            for name, props in all_entities.items()
        )

        # Generate derived units
        derived_ent = defaultdict(set)
        for entity in self.names.values():
            if not entity.dimensions:
                continue
            perms = self.get_dimension_permutations(entity.dimensions)
            for perm in perms:
                key = get_key_from_dimensions(perm)
                derived_ent[key].add(entity)

        self.derived = derived_ent

    def __getitem__(self, item):
        return self.names[item]

    def get_dimension_permutations(self, derived):
        """
        Get all possible dimensional definitions for an entity.
        """

        new_derived = defaultdict(int)
        for item in derived:
            new = self.names[item["base"]].dimensions
            if new:
                for new_item in new:
                    new_derived[new_item["base"]] += new_item["power"] * item["power"]
            else:
                new_derived[item["base"]] += item["power"]

        final = [
            [{"base": i[0], "power": i[1]} for i in list(new_derived.items())],
            derived,
        ]
        final = [sorted(i, key=lambda x: x["base"]) for i in final]

        candidates = []
        for item in final:
            if item not in candidates:
                candidates.append(item)

        return candidates


_CACHED_ENTITIES = {}


def clear_entities_cache():
    _CACHED_ENTITIES.clear()


def entities(
    lang: str = "en_US",
) -> Entities:
    """
    Cached entity object

    Parameters
    ----------
    lang : str
        Language code, loads the default and language specific entities.

    Returns
    -------
    Entities
        Entities object
    """

    args_hash = hash(
        (
            lang,
            USE_GENERAL_ENTITIES,
            USE_LANGUAGE_ENTITIES,
            USE_ADDITIONAL_ENTITIES,
            USE_CUSTOM_ENTITIES,
        )
    )
    if args_hash not in _CACHED_ENTITIES:
        entities_list = []
        if USE_GENERAL_ENTITIES:
            entities_list.append(GENERAL_ENTITIES_PATH)
        if USE_LANGUAGE_ENTITIES:
            entities_list.append(LANGUAGE_ENTITIES_PATH(lang))
        if USE_ADDITIONAL_ENTITIES:
            entities_list.append(ADDITIONAL_ENTITIES)
        if USE_CUSTOM_ENTITIES:
            entities_list.extend(CUSTOM_ENTITIES)

        _CACHED_ENTITIES[args_hash] = Entities(entities_list)

    return _CACHED_ENTITIES[args_hash]


###############################################################################
def get_derived_units(names):
    """
    Create dictionary of unit dimensions.
    """

    derived_uni = {}

    for name in names:
        key = get_key_from_dimensions(names[name].dimensions)
        derived_uni[key] = names[name]
        plain_derived = [{"base": name, "power": 1}]
        key = get_key_from_dimensions(plain_derived)
        derived_uni[key] = names[name]
        if not names[name].dimensions:
            names[name].dimensions = plain_derived
        names[name].dimensions = [
            {"base": names[i["base"]].name, "power": i["power"]}
            for i in names[name].dimensions
        ]

    return derived_uni


###############################################################################
class Units(object):
    def __init__(self, unit_dict_json: List[Union[str, Path, dict]], lang="en_US"):
        """
        Load units from JSON file.

        Parameters
        ----------
        unit_paths : List[Union[str, Path, dict]]
            Paths to unit JSON files.
        lang : str
            Language code, loads the default and language specific units.
        custom_entities : List[Union[Path, str, dict]]
            Paths to custom entity JSON files. If a list is provided, no default language
            or general entities will be loaded.
        """

        # names of all units
        self.names = {}
        self.symbols, self.symbols_lower = defaultdict(set), defaultdict(set)
        self.surfaces, self.surfaces_lower = defaultdict(set), defaultdict(set)
        self.prefix_symbols = defaultdict(set)
        self.lang = lang

        unit_dict = defaultdict(dict)
        for ud in unit_dict_json:
            for name, unit in _load_json_dict(ud).items():
                for nname, nunit in self.prefixed_units(name, unit):
                    unit_dict[nname].update(nunit)

        for name, unit in unit_dict.items():
            self.load_unit(name, unit)

        self.derived = get_derived_units(self.names)

        # symbols of all units
        self.symbols_all = self.symbols.copy()
        self.symbols_all.update(self.symbols_lower)

        # surfaces of all units
        self.surfaces_all = self.surfaces.copy()
        self.surfaces_all.update(self.surfaces_lower)

    def __getitem__(self, name):
        return self.names[name]

    def load_unit(self, name, unit):
        try:
            assert name not in self.names
        except AssertionError:  # pragma: no cover
            msg = "Two units with same name in units.json: %s" % name
            raise Exception(msg)

        obj = c.Unit(
            name=name,
            surfaces=unit.get("surfaces", []),
            entity=entities(self.lang).names[unit["entity"]],
            uri=unit.get("URI"),
            symbols=unit.get("symbols", []),
            dimensions=unit.get("dimensions", []),
            currency_code=unit.get("currency_code"),
            lang=self.lang,
        )

        self.names[name] = obj

        for symbol in unit.get("symbols", []):
            self.symbols[symbol].add(obj)
            self.symbols_lower[symbol.lower()].add(obj)
            if unit["entity"] == "currency":
                self.prefix_symbols[symbol].add(obj)

        for surface in unit.get("surfaces", []):
            self.surfaces[surface].add(obj)
            self.surfaces_lower[surface.lower()].add(obj)
            plural = pluralize(surface, lang=self.lang)
            self.surfaces[plural].add(obj)
            self.surfaces_lower[plural.lower()].add(obj)

    @staticmethod
    def prefixed_units(name, unit):
        yield name, unit
        # If SI-prefixes are given, add them
        for prefix in unit.get("prefixes", []):
            assert (
                prefix in METRIC_PREFIXES
            ), "Given prefix '{}' for unit '{}' not supported".format(prefix, name)
            assert (
                len(unit["dimensions"]) <= 1
            ), "Prefixing not supported for multiple dimensions in {}".format(name)

            uri = METRIC_PREFIXES[prefix].capitalize() + unit["URI"].lower()
            # we usually do not want the "_(unit)" postfix for prefixed units
            uri = uri.replace("_(unit)", "")

            yield METRIC_PREFIXES[prefix] + name, {
                "surfaces": [METRIC_PREFIXES[prefix] + i for i in unit["surfaces"]],
                "entity": unit["entity"],
                "URI": uri,
                "dimensions": [],
                "symbols": [prefix + i for i in unit["symbols"]],
            }


_CACHED_UNITS = {}


def clear_units_cache():
    _CACHED_UNITS.clear()


def units(
    lang: str = "en_US",
) -> Units:
    """
    Cached unit object

    Parameters
    ----------
    lang : str
        Language code, loads the default and language specific units.

    Returns
    -------
    Units
        Units object
    """

    args_hash = hash(
        (
            lang,
            USE_GENERAL_UNITS,
            USE_LANGUAGE_UNITS,
            USE_ADDITIONAL_UNITS,
            USE_CUSTOM_UNITS,
        )
    )

    if args_hash not in _CACHED_UNITS:
        units_list = []
        if USE_GENERAL_UNITS:
            units_list.append(GENERAL_UNITS_PATH)
        if USE_LANGUAGE_UNITS:
            units_list.append(LANGUAGE_UNITS_PATH(lang))
        if USE_ADDITIONAL_UNITS:
            units_list.append(ADDITIONAL_UNITS)
        if USE_CUSTOM_UNITS:
            units_list.extend(CUSTOM_UNITS)

        _CACHED_UNITS[args_hash] = Units(units_list, lang)

    return _CACHED_UNITS[args_hash]


###############################################################################
@cached
def training_set(lang="en_US"):
    training_set_ = []

    path = language.topdir(lang).joinpath("train")
    for file in path.iterdir():
        if file.suffix == ".json":
            with file.open("r", encoding="utf-8") as train_file:
                training_set_ += json.load(train_file)

    return training_set_


###############################################################################
def add_custom_unit(name: str, **kwargs):
    """
    Adds a custom unit to the set of default units
    Note: causes a reload of all units
    :param name: Name of the unit to add, should preferably be unique,
    otherwise will overwrite attributes in existing units
    :param kwargs: properties of the unit as found in units.json, i.e. surfaces=["centimetre"]
    """
    ADDITIONAL_UNITS[name].update(kwargs)
    clear_caches()


def remove_custom_unit(name: str):
    """
    Removes a unit from the set of custom units
    Note: causes a reload of all units
    :param name: Name of the unit to remove. This will not affect units that are loaded per default.
    """
    ADDITIONAL_UNITS.pop(name)
    clear_caches()


def add_custom_entity(name: str, **kwargs):
    """
    Adds a custom entity to the set of default entities
    Note: causes a reload of all entities
    :param name: Name of the entity to add, should preferably be unique,
    otherwise will overwrite attributes in existing entities
    :param kwargs: properties of the entity as found in entities.json, i.e. surfaces=["centimetre"]
    """
    ADDITIONAL_ENTITIES[name].update(kwargs)
    clear_caches()


def remove_custom_entity(name: str):
    """
    Removes a entity from the set of custom entities
    Note: causes a reload of all entities
    :param name: Name of the entity to remove. This will not affect entities that are loaded per default.
    """
    ADDITIONAL_ENTITIES.pop(name)
    clear_caches()


def load_custom_units(
    unit_dict_json: List[Union[str, Path]],
    use_general_units: bool = False,
    use_language_units: bool = False,
    use_additional_units: bool = True,
):
    """
    Load custom units from a dictionary or json file.

    Parameters
    ----------
    unit_dict_json : List[Dict]
        A list of dictionaries or paths to json files containing the units to load.
    use_general_units : bool, optional
        Whether to also load the general units, by default False
    use_language_units : bool, optional
        Whether to also load the language specific units, by default False
    use_additional_units : bool, optional
        Whether to also load the additional units (from the add_custom_unit functions), by default True
    """

    if not isinstance(unit_dict_json, list):
        unit_dict_json = [unit_dict_json]

    global USE_GENERAL_UNITS, USE_LANGUAGE_UNITS, USE_ADDITIONAL_UNITS, USE_CUSTOM_UNITS, CUSTOM_UNITS

    USE_GENERAL_UNITS = use_general_units
    USE_LANGUAGE_UNITS = use_language_units
    USE_ADDITIONAL_UNITS = use_additional_units
    USE_CUSTOM_UNITS = True

    CUSTOM_UNITS = unit_dict_json

    clear_units_cache()


def load_custom_entities(
    entity_dict_json: List[Union[str, Path]],
    use_general_entities: bool = False,
    use_language_entities: bool = False,
    use_additional_entities: bool = True,
):
    """
    Load custom entities from a dictionary or json file.

    Parameters
    ----------
    entity_dict_json : List[Dict]
        A list of dictionaries or paths to json files containing the entities to load.
    use_general_entities : bool, optional
        Whether to also load the general entities, by default False
    use_language_entities : bool, optional
        Whether to also load the language specific entities, by default False
    use_additional_entities : bool, optional
        Whether to also load the additional entities (from the add_custom_entity functions), by default True
    """

    if not isinstance(entity_dict_json, list):
        entity_dict_json = [entity_dict_json]

    global USE_GENERAL_ENTITIES, USE_LANGUAGE_ENTITIES, USE_ADDITIONAL_ENTITIES, USE_CUSTOM_ENTITIES, CUSTOM_ENTITIES

    USE_GENERAL_ENTITIES = use_general_entities
    USE_LANGUAGE_ENTITIES = use_language_entities
    USE_ADDITIONAL_ENTITIES = use_additional_entities
    USE_CUSTOM_ENTITIES = True

    CUSTOM_ENTITIES = entity_dict_json

    clear_entities_cache()
