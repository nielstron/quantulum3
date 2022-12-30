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
    # ("a million and a half", ["1500000.0"]), # this is a hard one
    # ("twenty thirty fifty hundred", ["20.0", "30.0", "5000.0"]),
    # ("one, two, three", ["1.0", "2.0", "3.0"]),
]


class ExtractSpellout(unittest.TestCase):
    def test_training(self, lang="en_US"):
        """Test that classifier training works"""
        for input, expected in TEST_CASES:
            print("---------input", input)
            output = [v["new_surface"] for v in extract_spellout_values(input)]
            self.assertEquals(output, expected)


###############################################################################
if __name__ == "__main__":  # pragma: no cover

    unittest.main()
