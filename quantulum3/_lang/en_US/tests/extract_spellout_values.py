import unittest

from ..parser import extract_spellout_values

TEST_CASES = [
    ("one hundred and five", ["105.0"]),
    ("a million", ["1000000.0"]),
    ("a million and one", ["1000001.0"]),
    ("million", ["1000000.0"]),
    ("million and one", ["1000001.0"]),
    ("one hundred million", ["100000000.0"]),
    ("one hundred and five million", ["105000000.0"]),
    ("half", ["0.5"]),
    ("two and a half", ["2.5"]),
    ("two and a half million", ["2500000.0"]),
    ("twenty six million and seventy two hundred", ["26007200.0"]),
    ("twenty", ["20.0"]),
    ("zero", ["0.0"]),
    ("several hundred years", []),
    ("Zero is a small number.", ["0.0", "1.0"]),
    ("a million and a half", ["1000000.5"]),
    ("one and a half million", ["1500000.0"]),
    ("two hundred fifty thousand and twenty two", ["250022.0"]),
    ("ninety nine", ["99.0"]),
    ("two thousand six hundred forty five", ["2645.0"]),
    ("seven million five hundred twenty thousand", ["7520000.0"]),
    ## number splitting
    ("twenty thirty fifty hundred", ["20.0", "30.0", "5000.0"]),
    ("one, two, three", ["1.0", "2.0", "3.0"]),
    ("one, two and three", ["1.0", "2.0", "3.0"]),
    ("one and two and three", ["1.0", "2.0", "3.0"]),
    ("one two and three", ["1.0", "2.0", "3.0"]),
    ("twenty five and thirty six", ["25.0", "36.0"]),
    ("twenty five thirty six one hundred", ["25.0", "36.0", "100.0"]),
    ("hundred and five hundred and six", ["105.0", "106.0"]),  # this is ambiguous..
    ("hundred and five twenty two", ["105.0", "22.0"]),
    ("hundred and five twenty two million", ["105.0", "22000000.0"]),
    ## negatives
    ("minus ten", ["-10.0"]),
    ("minus a million and a half", ["-1000000.5"]),
    ("negative million and a half", ["-1000000.5"]),
    ## negative splitting
    ("minus twenty five and thirty six", ["-25.0", "36.0"]),
    ("twenty five and minus thirty six", ["25.0", "-36.0"]),
    ("negative twenty five and minus thirty six", ["-25.0", "-36.0"]),
]


class ExtractSpellout(unittest.TestCase):
    def test_spellout_values(self, lang="en_US"):
        """Test extraction and conversion of spellout numbers from text"""
        self.assertEqual(lang, "en_US")
        for input, expected in TEST_CASES:
            with self.subTest(input=input):
                output = [v["new_surface"] for v in extract_spellout_values(input)]
                self.assertEqual(output, expected)


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
