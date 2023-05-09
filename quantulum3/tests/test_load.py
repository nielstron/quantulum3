#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from quantulum3 import classifier as clf
from quantulum3 import load
from quantulum3.load import (
    _CACHE_DICT,
    _CACHED_ENTITIES,
    _CACHED_UNITS,
    CustomQuantities,
    Entities,
    Units,
    cached,
    clear_cache,
    clear_entities_cache,
    clear_units_cache,
    entities,
    load_custom_entities,
    load_custom_units,
    units,
)

from .test_setup import get_classifier_path, multilang

TOPDIR = os.path.dirname(__file__) or "."
TEST_DATA_DIR = Path(TOPDIR) / "data"


@cached
def _test_function(*args, **kwargs):
    return args, kwargs


# pylint: disable=no-self-use
class TestCached(unittest.TestCase):
    def setUp(self) -> None:
        clear_cache()

    def _test_cached(self, func, *args, **kwargs):
        """
        Test that a cached function is accessed with same args and kwargs.
        """
        result = func(*args, **kwargs)

        # we can't access the funcid directly (as we just get the id of `cached`)
        # so we'll just get the value of the first key in the cache dict
        # (which should be empty)
        func_id = list(_CACHE_DICT.keys())[0]

        self.assertEqual(len(_CACHE_DICT[func_id]), 1)
        cached_result = func(*args, **kwargs)
        self.assertEqual(len(_CACHE_DICT[func_id]), 1)
        self.assertEqual(result, cached_result)

    def test_clear_cache(self):
        """
        Test that the cache is cleared.
        """
        _test_function()
        self.assertGreaterEqual(len(_CACHE_DICT), 1)
        clear_cache()
        self.assertEqual(len(_CACHE_DICT), 0)

    def test_cached_language(self):
        """
        Test backwards compatable language based caching on old @cached decorator API.
        """

        @cached
        def _lang_test_function(lang):
            return lang

        self._test_cached(_lang_test_function, "en_US")

    def test_cached_same_args(self):
        """
        Test that a cached function is accessed with same args and kwargs.
        """

        self._test_cached(_test_function, 1, 2, 3, a=1, b=2, c=3)

    def test_cached_different_args(self):
        result = _test_function(1, 2, 3, a=1, b=2, c=3)
        func_id = list(_CACHE_DICT.keys())[0]
        self.assertEqual(len(_CACHE_DICT[func_id]), 1)
        cached_result = _test_function("a", "b", "c", a="a", b="b", c="c")
        self.assertEqual(len(_CACHE_DICT[func_id]), 2)
        self.assertNotEqual(result, cached_result)

    def test_cached_with_path(self):
        self._test_cached(_test_function, Path("a"))


# pylint: disable=no-self-use
class TestLoaders(unittest.TestCase):
    def setUp(self) -> None:
        load.USE_CUSTOM_UNITS = False
        load.USE_CUSTOM_ENTITIES = False
        load.USE_GENERAL_UNITS = True
        load.USE_LANGUAGE_UNITS = True
        load.USE_LANGUAGE_ENTITIES = True
        load.USE_ADDITIONAL_UNITS = True
        load.USE_ADDITIONAL_ENTITIES = True

        clear_cache()
        clear_units_cache()
        clear_entities_cache()

    @multilang
    def test_classifier_default_model(self, lang="en_US"):
        """
        Test that a classifier can be initialized with the default model
        """
        clf.Classifier(lang=lang)

    @patch("quantulum3.language")
    def test_classifier_custom_model(self, mock_language):
        """
        Test that a classifier can be initialized with a custom model
        """

        classifier_path = get_classifier_path("en_US")
        clf.Classifier(classifier_path=classifier_path)
        mock_language.topdir.assert_not_called()

    @multilang
    def test_load_units(self, lang="en_US"):
        """
        Test that the units can be loaded.
        """
        self.assertIsInstance(units(lang=lang), Units)

    @multilang
    def test_load_entities(self, lang="en_US"):
        """
        Test that the entities can be loaded.
        """
        self.assertIsInstance(entities(lang=lang), Entities)

    def test_load_custom_entities(self):
        """
        Test that the entities can be loaded with a custom path.
        """

        custom_entities = TEST_DATA_DIR / "entities.json"
        lang = "en_US"

        load_custom_entities(custom_entities)
        self.assertIsInstance(entities(lang=lang), Entities)
        self.assertFalse(load.USE_GENERAL_ENTITIES)
        self.assertFalse(load.USE_LANGUAGE_ENTITIES)
        self.assertTrue(load.USE_ADDITIONAL_ENTITIES)
        self.assertEqual(len(_CACHED_ENTITIES), 1)

        # check caching
        entities(lang=lang)
        self.assertEqual(len(_CACHED_ENTITIES), 1)

        # check cache updates with global variable change
        load.USE_GENERAL_ENTITIES = True
        entities(lang=lang)
        self.assertEqual(len(_CACHED_ENTITIES), 2)

    def test_load_custom_units(self):
        """
        Test that the units can be loaded with a custom path.
        """
        custom_unites = TEST_DATA_DIR / "units.json"
        lang = "en_US"

        load_custom_units(custom_unites)
        self.assertIsInstance(units(lang=lang), Units)
        self.assertEqual(len(_CACHED_UNITS), 1)

        # check caching
        units(lang=lang)
        self.assertEqual(len(_CACHED_UNITS), 1)

        # check cache updates with global variable change
        load.USE_GENERAL_UNITS = True
        units(lang=lang)
        self.assertEqual(len(_CACHED_UNITS), 2)

    def test_custom_quantities(self):
        """
        Test custom units and entities are loaded via the context manager.
        """
        custom_units_path = TEST_DATA_DIR / "units.json"
        custom_entities_path = TEST_DATA_DIR / "entities.json"

        # current state
        general_units = load.USE_GENERAL_UNITS
        general_entities = load.USE_GENERAL_ENTITIES
        language_units = load.USE_LANGUAGE_UNITS
        language_entities = load.USE_LANGUAGE_ENTITIES
        additional_units = load.USE_ADDITIONAL_UNITS
        additional_entities = load.USE_ADDITIONAL_ENTITIES
        custom_entities = load.USE_CUSTOM_ENTITIES
        custom_units = load.USE_CUSTOM_UNITS

        with CustomQuantities(custom_units_path, custom_entities_path):
            self.assertIsInstance(units(), Units)
            self.assertIsInstance(entities(), Entities)

            # check default behaviour
            assert load.USE_CUSTOM_UNITS == True
            assert load.USE_CUSTOM_ENTITIES == True
            assert load.USE_GENERAL_UNITS == False
            assert load.USE_GENERAL_ENTITIES == False
            assert load.USE_LANGUAGE_UNITS == False
            assert load.USE_LANGUAGE_ENTITIES == False
            assert load.USE_ADDITIONAL_UNITS == True
            assert load.USE_ADDITIONAL_ENTITIES == True

        # check that the state is restored
        assert load.USE_GENERAL_UNITS == general_units
        assert load.USE_GENERAL_ENTITIES == general_entities
        assert load.USE_LANGUAGE_UNITS == language_units
        assert load.USE_LANGUAGE_ENTITIES == language_entities
        assert load.USE_ADDITIONAL_UNITS == additional_units
        assert load.USE_ADDITIONAL_ENTITIES == additional_entities
        assert load.USE_CUSTOM_UNITS == custom_units
        assert load.USE_CUSTOM_ENTITIES == custom_entities

        self.assertIsInstance(units(), Units)
        self.assertIsInstance(entities(), Entities)


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
