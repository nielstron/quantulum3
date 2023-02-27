#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from quantulum3.load import _CACHE_DICT, cached, clear_cache


@cached
def _test_function(*args, **kwargs):
    return args, kwargs


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
        from pathlib import Path

        self._test_cached(_test_function, Path("a"))


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
