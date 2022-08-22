import unittest
from datetime import datetime, timedelta
from deduplicate_util import fuzzy_match
from food_post import DATETIME_FMT


class DeduplicateUtilTest(unittest.TestCase):
    """
    Fuzzy matching for titles
    https://github.com/SaxyPandaBear/my-webhooks/issues/13
    """

    def test_fuzzy_match(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"title": "Homemade beef tacos.", "date": ds}
        b = {"title": "[homemade] Beef tacos.", "date": ds}
        self.assertTrue(fuzzy_match(a, b))

    def test_fuzzy_match_below_threshold(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"title": "Foo bar baz", "date": ds}
        b = {"title": "this is another title that looks different", "date": ds}
        self.assertFalse(fuzzy_match(a, b))

    def test_fuzzy_match_date(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Homemade beef tacos.", "date": d.strftime(DATETIME_FMT)}
        b = {
            "title": "[homemade] Beef tacos.",
            "date": (d + timedelta(days=5)).strftime(DATETIME_FMT),
        }
        self.assertFalse(fuzzy_match(a, b))

    def test_missing_title(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"date": ds}
        b = {"title": "[homemade] Beef tacos.", "date": ds}
        self.assertFalse(fuzzy_match(a, b))

    def test_missing_date(self):
        d = datetime(2022, 8, 21, 1)
        a = {"title": "Homemade beef tacos.", "date": d.strftime(DATETIME_FMT)}
        b = {"title": "[homemade] Beef tacos."}
        self.assertFalse(fuzzy_match(a, b))
