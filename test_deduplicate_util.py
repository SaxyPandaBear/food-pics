import unittest
from datetime import datetime, timedelta
from deduplicate_util import already_posted, fuzzy_match
from food_post import DATETIME_FMT
from fakeredis import FakeStrictRedis
import json


class DeduplicateUtilTest(unittest.TestCase):
    """
    Fuzzy matching for titles
    https://github.com/SaxyPandaBear/my-webhooks/issues/13
    """

    def test_fuzzy_match_hash(self):
        a = {"hash": 1}
        b = {"hash": 1}
        self.assertTrue(fuzzy_match(a, b))

    def test_fuzzy_match_title(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"hash": 1, "title": "Homemade beef tacos.", "date": ds}
        b = {"hash": 2, "title": "[homemade] Beef tacos.", "date": ds}
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

    # Mocked Redis tests
    # https://github.com/SaxyPandaBear/my-webhooks/issues/14
    def test_already_posted_matching_id(self):
        r = FakeStrictRedis(version=6)
        r.set("foo/bar", "{}")

        post = {"id": "bar"}
        self.assertTrue(already_posted(r, "foo", post))

    def test_already_posted_match_img_hash(self):
        r = FakeStrictRedis(version=6)
        stored = {"id": "bar", "hash": 1}
        r.set("foo/bar", json.dumps(stored))

        matching = {"id": "baz", "hash": 1}
        self.assertTrue(already_posted(r, "foo", matching))
