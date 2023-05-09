#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

from __future__ import division

import json
import os
import sys
import unittest
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import MagicMock, patch

import joblib
import wikipedia

from .. import classifier as clf
from .. import language, load
from .. import parser as p
from .test_setup import (
    add_type_equalities,
    get_classifier_path,
    get_entity_paths,
    get_unit_paths,
    load_error_tests,
    load_expand_tests,
    load_quantity_tests,
    multilang,
)

COLOR1 = "\033[94m%s\033[0m"
COLOR2 = "\033[91m%s\033[0m"
TOPDIR = os.path.dirname(__file__) or "."
TEST_DATA_DIR = Path(TOPDIR) / "data"


###############################################################################
class ClassifierBuild(unittest.TestCase):
    @multilang
    def test_training(self, lang="en_US"):
        """Test that classifier training works"""
        # Test that no errors are thrown during training
        # Also stores result, to be included in package
        self.assertIsNotNone(clf.train_classifier(store=True, lang=lang))


###############################################################################
# pylint: disable=no-self-use
class ClassifierTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def setUp(self):
        load.clear_caches()
        load.reset_quantities()
        add_type_equalities(self)

    def _test_parse_classifier(self, lang="en_US", classifier_path=None):
        clf.USE_CLF = True

        parse_kwargs = {"lang": lang, "classifier_path": classifier_path}

        all_tests = load_quantity_tests(False, lang=lang)
        for test in sorted(all_tests, key=lambda x: len(x["req"])):
            with self.subTest(input=test["req"]):
                quants = p.parse(test["req"], **parse_kwargs)

                self.assertEqual(
                    len(test["res"]),
                    len(quants),
                    msg="Differing amount of quantities parsed, expected {}, "
                    "got {}: {}, {}".format(
                        len(test["res"]), len(quants), test["res"], quants
                    ),
                )
                for index, quant in enumerate(quants):
                    self.assertEqual(quant, test["res"][index])

        classifier_tests = load_quantity_tests(True, lang)
        correct = 0
        total = len(classifier_tests)
        error = []
        for test in sorted(classifier_tests, key=lambda x: len(x["req"])):
            quants = p.parse(test["req"], **parse_kwargs)
            if quants == test["res"]:
                correct += 1
            else:
                error.append((test, quants))
        success_rate = correct / total
        print("Classifier success rate at {:.2f}%".format(success_rate * 100))
        self.assertGreaterEqual(
            success_rate,
            0.8,
            "Classifier success rate was at {}%, below 80%.\nFailure at\n{}".format(
                success_rate * 100,
                "\n".join("{}: {}".format(test[0]["req"], test[1]) for test in error),
            ),
        )

    @multilang
    def test_parse_classifier(self, lang="en_US"):
        """Test that parsing works with classifier usage"""
        self._test_parse_classifier(lang=lang)

    # @multilang
    # this was causing the test to fail, `en_US` got convereted to lowercase
    # and the path was not found
    def test_parse_classifier_custom_classifier(self):
        """Test parsing with a custom classifier model. Use the same model as
        the default one, but load it via the classifier_path argument, and ensure
        that the results are the same."""

        lang = "en_US"
        classifier_path = get_classifier_path(lang)
        self.assertTrue(
            classifier_path.exists(),
            f"Classifier path does not exist: {classifier_path}",
        )

        classifier = clf.classifier(
            lang=lang,
            classifier_path=classifier_path,
        )

        # call.args and call.kwargs have different behavior pre-3.8
        # not interested in working this out for 3.6/3.7 which are EOL or soon to be
        if sys.version_info >= (3, 8):  # pragma: no cover
            with patch(
                "quantulum3.classifier.classifier", return_value=classifier
            ) as mock_clf_classifier:
                self._test_parse_classifier(classifier_path=classifier_path)

                self.mock_assert_arg_in_all_calls(
                    mock_clf_classifier,
                    "classifier_path",
                    1,
                    classifier_path,
                )
        else:  # pragma: no cover
            self._test_parse_classifier(classifier_path=classifier_path)

    def test_parse_classifier_custom_units(self):
        """Test parsing with custom units. Use the same unit files as the default ones,
        but load them via the custom_units argument, and ensure that the results are the
        same."""

        lang = "en_US"
        load.load_custom_units(get_unit_paths(lang), use_additional_units=False)
        self.assertFalse(load.USE_GENERAL_UNITS)
        self.assertFalse(load.USE_LANGUAGE_UNITS)
        self.assertFalse(load.USE_ADDITIONAL_UNITS)
        self.assertTrue(load.USE_CUSTOM_UNITS)
        self._test_parse_classifier(lang=lang)

    def test_parse_classifier_custom_entities(self):
        """Test parsing with custom entities. Use the same entity files as the default ones,
        but load them via the custom_entities argument, and ensure that the results are the
        same."""

        lang = "en_US"
        load.load_custom_entities(get_entity_paths(lang), use_additional_entities=False)
        self.assertFalse(load.USE_GENERAL_ENTITIES)
        self.assertFalse(load.USE_LANGUAGE_ENTITIES)
        self.assertFalse(load.USE_ADDITIONAL_ENTITIES)
        self.assertTrue(load.USE_CUSTOM_ENTITIES)
        self._test_parse_classifier(lang=lang)

    @multilang
    def test_expand(self, lang="en_US"):
        """Test that parsing and expanding works correctly"""
        all_tests = load_expand_tests(lang=lang)
        for test in all_tests:
            with self.subTest(input=test["req"]):
                result = p.inline_parse_and_expand(test["req"], lang=lang)
                self.assertEqual(result, test["res"])

    @multilang
    def test_errors(self, lang="en_US"):
        """Test that no errors are thrown in edge cases"""
        all_tests = load_error_tests(lang=lang)
        for test in all_tests:
            with self.subTest(input=test):
                # pylint: disable=broad-except
                p.parse(test, lang=lang)

    @unittest.skip("Not necessary, as classifier is live built")
    @multilang
    def test_classifier_up_to_date(self, lang="en_US"):
        """
        Test that the classifier has been built with the latest version of
        scikit-learn
        """
        path = language.topdir(lang).joinpath("clf.joblib")
        with path.open("rb") as clf_file:
            obj = joblib.load(clf_file)
        clf_version = obj["scikit-learn_version"]
        with urllib.request.urlopen(
            "https://pypi.org/pypi/scikit-learn/json"
        ) as response:
            cur_version = json.loads(response.read().decode("utf-8"))["info"]["version"]
        self.assertEqual(
            clf_version,
            cur_version,
            "Classifier has been built with scikit-learn version {}, while the"
            " newest version is {}. Please update scikit-learn.".format(
                clf_version, cur_version
            ),
        )

    @multilang
    def test_training(self, lang="en_US"):
        """Test that classifier training works"""
        # Test that no errors are thrown during training
        obj = clf.train_classifier(store=False, lang=lang)
        # Test that the classifier works with the currently downloaded data
        load._CACHE_DICT[id(clf.classifier)] = {
            lang: clf.Classifier(classifier_object=obj, lang=lang)
        }
        self.test_parse_classifier(lang=lang)

    @patch("quantulum3.load.training_set")
    def test_training_custom_data(self, mock_load_training_set):
        """Test the classifier training works with custom data"""

        with (TEST_DATA_DIR / "train.json").open() as f:
            self.custom_training_data = json.load(f)

        clf.train_classifier(
            store=False,
            training_set=self.custom_training_data,
        )
        mock_load_training_set.assert_not_called()

    def test_training_custom_out_path(self):
        """Test the classifier training works with custom out path"""

        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "clf.joblib"
            clf.train_classifier(
                output_path=out_path,
            )

            self.assertTrue(out_path.exists())

    @multilang(["en_US"])
    def test_wikipedia_pages(self, lang):
        wikipedia.set_lang(lang[:2])
        err = []
        units = dict(sorted(load.units(lang).names.items()))
        for unit in units.values():
            try:
                wikipedia.page(unit.uri.replace("_", " "), auto_suggest=False)
                pass
            except (
                wikipedia.PageError,
                wikipedia.DisambiguationError,
            ) as e:  # pragma: no cover
                err.append((unit, e))
        if err:  # pragma: no cover
            self.fail("Problematic pages:\n{}".format("\n".join(str(e) for e in err)))

    def mock_assert_arg_in_all_calls(
        self, mock: MagicMock, arg_name: str, arg_position: int, arg_value: Any
    ):
        """
        Checks that the given arg_name/arg_value is in every call to the given mock,
        either as a kwarg or as a positional argument.
        """
        trues = []

        self.assertGreater(
            len(mock.call_args_list),
            0,
            msg=f"Expected {arg_name}={arg_value} in all calls to {mock}, but there were no calls.",
        )

        for call in mock.call_args_list:
            try:
                if arg_name in call.kwargs:
                    if call.kwargs[arg_name] == arg_value:  # pragma: no cover
                        trues.append(call)
                elif arg_value == call.args[arg_position]:
                    trues.append(call)
            except IndexError:  # pragma: no cover
                pass

        self.assertEqual(
            len(trues),
            len(mock.call_args_list),
            msg=f"Expected {arg_name}={arg_value} in all calls to {mock}, but it was not in {len(mock.call_args_list) - len(trues)} calls.",
        )


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
