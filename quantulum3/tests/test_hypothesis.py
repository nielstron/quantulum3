#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` property based tests.
"""

from hypothesis import settings, given, strategies as st

from ..language import LANGUAGES
from .. import parser as p

import unittest

multilang_strategy = st.one_of(*(st.just(l) for l in LANGUAGES))


class TestNoErrors(unittest.TestCase):
    @given(st.text(), multilang_strategy)
    @settings(deadline=None)
    def test_parse(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.parse(s, lang=lang)

    @given(st.text(), multilang_strategy)
    @settings(deadline=None)
    def test_extract_spellout_values(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.extract_spellout_values(s, lang=lang)

    @given(st.text(), multilang_strategy)
    @settings(deadline=None)
    def test_inline_parse_and_expand(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.inline_parse_and_expand(s, lang=lang)

    @given(st.text(), multilang_strategy)
    @settings(deadline=None)
    def test_clean_text(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.clean_text(s, lang=lang)


if __name__ == "__main__":
    unittest.main()
