#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

# Standard library
import os
import unittest

# Quantulum
from .. import parser as p
from .. import classifier as clf
from .test_setup import load_quantity_tests

COLOR1 = '\033[94m%s\033[0m'
COLOR2 = '\033[91m%s\033[0m'
TOPDIR = os.path.dirname(__file__) or "."


################################################################################
class ParsingTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def test_parse_no_classifier(self):
        """ Test that parsing works without classifier usage """
        all_tests = load_quantity_tests(False)
        # Disable classifier usage
        clf.USE_CLF = False
        for test in sorted(all_tests, key=lambda x: len(x['req'])):
            quants = p.parse(test['req'])
            self.assertEqual(
                quants, test['res'], "\nExcpected: {1} \nGot: {0}".format(
                    [quant.__dict__ for quant in quants],
                    [quant.__dict__ for quant in test['res']]))


################################################################################
if __name__ == '__main__':  # pragma: no cover

    unittest.main()
