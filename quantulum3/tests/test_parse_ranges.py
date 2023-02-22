#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

import unittest

from quantulum3 import parser as p


class RangeParse(unittest.TestCase):
    """Test suite for the functions in the parser module."""

    def test_split_range(self):
        test_data = {
            "1-2": {"separator": "-", "expected": ["1", "2"]},
            "1 - 2": {"separator": "-", "expected": ["1", "2"]},
            "-1 - 2": {"separator": "-", "expected": ["-1", "2"]},
            "1 - -2": {"separator": "-", "expected": ["1", "-2"]},
            "-1--2": {"separator": "-", "expected": ["-1", "-2"]},
            "1-2-3": {"separator": "-", "expected": ["1", "2", "3"]},
            "-1--2--3": {"separator": "-", "expected": ["-1", "-2", "-3"]},
            "1—2": {"separator": "—", "expected": ["1", "2"]},
            "-1—2": {"separator": "—", "expected": ["-1", "2"]},
            "1—-2": {"separator": "—", "expected": ["1", "-2"]},
        }

        for test, values in test_data.items():
            separator = values["separator"]
            expected = values["expected"]
            values = p.split_range(test, separator)
            self.assertEqual(values, expected)
