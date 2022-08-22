import unittest
from datetime import datetime, timedelta
from deduplicate_util import fuzzy_match


class DeduplicateUtilTest(unittest.TestCase):
    """
    Fuzzy matching for titles
    https://github.com/SaxyPandaBear/my-webhooks/issues/13
    """

    def test_fuzzy_match(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Homemade beef tacos.", "date": d}
        b = {"title": "[homemade] Beef tacos.", "date": d}
        self.assertTrue(fuzzy_match(a, b))

    def test_fuzzy_match_below_threshold(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Foo bar baz", "date": d}
        b = {"title": "this is another title that looks different", "date": d}
        self.assertFalse(fuzzy_match(a, b))

    def test_fuzzy_match_date(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Homemade beef tacos.", "date": d}
        b = {"title": "[homemade] Beef tacos.", "date": d + timedelta(days=5)}
        self.assertFalse(fuzzy_match(a, b))

    def test_missing_title(self):
        d = datetime(2022, 8, 21, 1)
        a = {"date": d}
        b = {"title": "[homemade] Beef tacos.", "date": d}
        self.assertFalse(fuzzy_match(a, b))

    def test_missing_date(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Homemade beef tacos.", "date": d}
        b = {"title": "[homemade] Beef tacos."}
        self.assertFalse(fuzzy_match(a, b))
