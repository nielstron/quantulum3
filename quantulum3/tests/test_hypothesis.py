#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` property based tests.
"""

import unittest

from hypothesis import example, given, settings
from hypothesis import strategies as st

from .. import parser as p
from ..language import LANGUAGES

multilang_strategy = st.one_of(*(st.just(l) for l in LANGUAGES))


class TestNoErrors(unittest.TestCase):
    # pylint: disable=no-self-use
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
    @example("0/B", "en_US")
    @settings(deadline=None)
    def test_inline_parse_and_expand(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.inline_parse_and_expand(s, lang=lang)

    @given(st.text(), multilang_strategy)
    @settings(deadline=None)
    def test_clean_text(self, s, lang):
        # Just assert that this does not throw any exceptions
        p.clean_text(s, lang=lang)


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
