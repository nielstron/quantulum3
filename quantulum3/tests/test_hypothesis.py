#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` property based tests.
"""

from hypothesis import settings, given, strategies as st

from quantulum3.tests.test_setup import multilang
from .. import parser as p

import unittest


class TestNoErrors(unittest.TestCase):
    @given(st.text())
    @settings(deadline=None)
    def test_parse(self, s):
        # Just assert that this does not throw any exceptions
        p.parse(s)

    @given(st.text())
    @settings(deadline=None)
    def test_extract_spellout_values(self, s):
        # Just assert that this does not throw any exceptions
        p.extract_spellout_values(s)

    @given(st.text())
    @settings(deadline=None)
    def test_inline_parse_and_expand(self, s):
        # Just assert that this does not throw any exceptions
        p.inline_parse_and_expand(s)

    @given(st.text())
    @settings(deadline=None)
    def test_clean_text(self, s):
        # Just assert that this does not throw any exceptions
        p.clean_text(s)


if __name__ == "__main__":
    unittest.main()
