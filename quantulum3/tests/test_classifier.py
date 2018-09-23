#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

# Python 2 compatibility
from __future__ import unicode_literals

# Standard library
import os
import json
import pickle
import sys
if sys.version_info[0] < 3:
    import urllib2 as request
else:
    import urllib.request as request
import unittest

# Quantulum
from .. import load
from .. import parser as p
from .. import classifier as clf
from .test_setup import load_expand_tests, load_quantity_tests

COLOR1 = '\033[94m%s\033[0m'
COLOR2 = '\033[91m%s\033[0m'
TOPDIR = os.path.dirname(__file__) or "."


################################################################################
class ClassifierTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def test_parse_classifier(self):
        """ Test that parsing works with classifier usage """
        all_tests = load_quantity_tests(False) + load_quantity_tests(True)
        # forcedly activate classifier
        clf.USE_CLF = True
        for test in sorted(all_tests, key=lambda x: len(x['req'])):
            quants = p.parse(test['req'])
            self.assertEqual(
                quants, test['res'],
                "\nExcpected: {1} \nGot: {0}".format(
                    [quant.__dict__ for quant in quants],
                    [quant.__dict__ for quant in test['res']]))

    def test_training(self):
        """ Test that classifier training works """
        # Test that no errors are thrown during training
        obj = clf.train_classifier(download=False, store=False)
        # Test that the classifier works with the currently downloaded data
        clf.TFIDF_MODEL, clf.CLF, clf.TARGET_NAMES = obj['tfidf_model'], obj[
            'clf'], obj['target_names']
        # Don't run tests with ambiguities because result is non-detemernistic

    def test_expand(self):
        all_tests = load_expand_tests()
        for test in all_tests:
            result = p.inline_parse_and_expand(test['req'])
            self.assertEqual(result, test['res'])

    def test_classifier_up_to_date(self):
        """ Test that the classifier has been built with the latest version of scikit-learn """
        path = os.path.join(load.TOPDIR, 'clf.pickle')
        with open(path, 'rb') as clf_file:
            obj = pickle.load(clf_file)
        clf_version = obj['scikit-learn_version']
        try:
            response = request.urlopen(
                "https://pypi.org/pypi/scikit-learn/json")
            cur_version = json.loads(
                response.read().decode('utf-8'))['info']['version']
        finally:
            response.close()
        self.assertEqual(
            clf_version, cur_version,
            "Classifier has been built with scikit-learn version {}, while the newest version is {}. Please update scikit-learn."
            .format(clf_version, cur_version))


################################################################################
if __name__ == '__main__':  # pragma: no cover

    unittest.main()
