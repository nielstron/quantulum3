#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

from __future__ import division

# Standard library
import os
import json
import urllib.request
import unittest

# Quantulum
from .. import load
from .. import parser as p
from .. import classifier as clf
from .test_setup import load_expand_tests, load_quantity_tests

# sklearn
from sklearn.externals import joblib

COLOR1 = '\033[94m%s\033[0m'
COLOR2 = '\033[91m%s\033[0m'
TOPDIR = os.path.dirname(__file__) or "."


################################################################################
class ClassifierTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def test_parse_classifier(self):
        """ Test that parsing works with classifier usage """
        # forcedly activate classifier
        clf.USE_CLF = True

        all_tests = load_quantity_tests(False)
        for test in sorted(all_tests, key=lambda x: len(x['req'])):
            quants = p.parse(test['req'])
            self.assertEqual(
                quants, test['res'],
                "{} \n {}".format([quant.__dict__ for quant in quants],
                                  [quant.__dict__ for quant in test['res']]))

        classifier_tests = load_quantity_tests(True)
        correct = 0
        total = len(classifier_tests)
        error = []
        for test in sorted(classifier_tests, key=lambda x: len(x['req'])):
            quants = p.parse(test['req'])
            if quants == test['res']:
                correct += 1
            else:
                error.append((test, quants))
        success_rate = correct / total
        print('Classifier success rate at {:.2f}%'.format(success_rate * 100))
        self.assertGreaterEqual(
            success_rate, 0.8,
            'Classifier success rate was at {}%, below 80%.\nFailure at\n{}'.
            format(
                success_rate * 100,
                '\n'.join('{}: {}'.format(test[0]['req'], test[1])
                          for test in error)))

    def test_training(self):
        """ Test that classifier training works """
        # Test that no errors are thrown during training
        obj = clf.train_classifier(download=False, store=False)
        # Test that the classifier works with the currently downloaded data
        clf.TFIDF_MODEL, clf.CLF, clf.TARGET_NAMES = obj['tfidf_model'], obj[
            'clf'], obj['target_names']
        self.test_parse_classifier()

    def test_expand(self):
        all_tests = load_expand_tests()
        for test in all_tests:
            result = p.inline_parse_and_expand(test['req'])
            self.assertEqual(result, test['res'])

    def test_classifier_up_to_date(self):
        """ Test that the classifier has been built with the latest version of scikit-learn """
        path = os.path.join(load.TOPDIR, 'clf.joblib')
        with open(path, 'rb') as clf_file:
            obj = joblib.load(clf_file)
        clf_version = obj['scikit-learn_version']
        with urllib.request.urlopen(
                "https://pypi.org/pypi/scikit-learn/json") as response:
            cur_version = json.loads(
                response.read().decode('utf-8'))['info']['version']
        self.assertEqual(
            clf_version, cur_version,
            "Classifier has been built with scikit-learn version {}, while the newest version is {}. Please update scikit-learn."
            .format(clf_version, cur_version))


################################################################################
if __name__ == '__main__':  # pragma: no cover

    unittest.main()
