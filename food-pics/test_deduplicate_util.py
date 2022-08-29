import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from deduplicate_util import already_posted, fuzzy_match, TIME_THRESHOLD
from food_post import DATETIME_FMT


@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_matching_id(db):
    db.return_value.document.return_value.get.return_value.exists.return_value = True
    post = {"id": "bar"}

    assert already_posted(db(), post)
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.assert_not_called()


@patch("google.cloud.firestore.DocumentSnapshot")
@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_match_img_hash(db, snap):
    db.return_value.document.return_value.get.return_value.exists.return_value = False
    stored = {"id": "bar", "author": "foo", "img": 1}
    snap.return_value.to_dict.return_value = stored
    db.return_value.where.return_value.stream.return_value = [snap()]

    matching = {"id": "baz", "author": "foo", "img": 1}
    assert already_posted(db(), matching)
    snap.return_value.to_dict.assert_called()
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.return_value.stream.assert_called()


@patch("google.cloud.firestore.DocumentSnapshot")
@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_match_fuzz_title(db, snap):
    title = "This is a title."
    now = datetime.now()
    time_diff = timedelta(hours=3)
    db.return_value.document.return_value.get.return_value.exists.return_value = False
    stored = {
        "id": "bar",
        "author": "foo",
        "img": 1,
        "title": title.upper(),
        "found": now.strftime(DATETIME_FMT),
    }
    snap.return_value.to_dict.return_value = stored
    db.return_value.where.return_value.stream.return_value = [snap()]

    matching = {
        "id": "baz",
        "author": "foo",
        "img": 2,
        "title": title.lower(),
        "found": (now + time_diff).strftime(DATETIME_FMT),
    }
    assert already_posted(db(), matching)
    snap.return_value.to_dict.assert_called()
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.return_value.stream.assert_called()


@patch("google.cloud.firestore.DocumentSnapshot")
@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_does_not_match_fuzz_title(db, snap):
    db.return_value.document.return_value.get.return_value.exists.return_value = False
    stored = {"id": "bar", "author": "foo", "img": 1, "title": "Some title foo"}
    snap.return_value.to_dict.return_value = stored
    db.return_value.where.return_value.stream.return_value = [snap()]

    matching = {
        "id": "baz",
        "author": "foo",
        "img": 2,
        "title": "Lorem ipsum bar baz 123",
    }
    assert not already_posted(db(), matching)
    snap.return_value.to_dict.assert_called()
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.return_value.stream.assert_called()


@patch("google.cloud.firestore.DocumentSnapshot")
@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_match_fuzz_title_too_old(db, snap):
    title = "This is a title."
    now = datetime.now()
    time_diff = timedelta(weeks=3)
    assert time_diff > TIME_THRESHOLD  # make sure this triggers the right condition
    db.return_value.document.return_value.get.return_value.exists.return_value = False
    stored = {
        "id": "bar",
        "author": "foo",
        "img": 1,
        "title": title.upper(),
        "found": now.strftime(DATETIME_FMT),
    }
    snap.return_value.to_dict.return_value = stored
    db.return_value.where.return_value.stream.return_value = [snap()]

    matching = {
        "id": "baz",
        "author": "foo",
        "img": 2,
        "title": title.lower(),
        "found": (now + time_diff).strftime(DATETIME_FMT),
    }
    assert not already_posted(db(), matching)
    snap.return_value.to_dict.assert_called()
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.return_value.stream.assert_called()


@patch("google.cloud.firestore.CollectionReference", autospec=True)
def test_already_posted_not_matched(db):
    db.return_value.document.return_value.get.return_value.exists.return_value = False
    db.return_value.where.return_value.stream.return_value = []

    matching = {"id": "baz", "author": "foo", "img": 2}
    assert not already_posted(db(), matching)
    db.return_value.document.return_value.get.return_value.exists.assert_called()
    db.return_value.where.return_value.stream.assert_called()


class FuzzyMatchTest(unittest.TestCase):
    """
    Fuzzy matching for titles
    https://github.com/SaxyPandaBear/my-webhooks/issues/13
    """

    def test_fuzz_match_missing_hash(self):
        a = {"foo": "bar"}
        b = {"img": 1}
        self.assertFalse(fuzzy_match(a, b))
        self.assertFalse(fuzzy_match(b, a))

    def test_fuzzy_match_hash(self):
        a = {"img": 1}
        b = {"img": 1}
        self.assertTrue(fuzzy_match(a, b))
        self.assertTrue(fuzzy_match(b, a))

    def test_fuzzy_match_title(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"img": 1, "title": "Homemade beef tacos.", "found": ds}
        b = {"img": 2, "title": "[homemade] Beef tacos.", "found": ds}
        self.assertTrue(fuzzy_match(a, b))
        self.assertTrue(fuzzy_match(b, a))

    def test_fuzzy_match_below_threshold(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"img": 1, "title": "Foo bar baz", "found": ds}
        b = {
            "img": 2,
            "title": "this is another title that looks different",
            "found": ds,
        }
        self.assertFalse(fuzzy_match(a, b))
        self.assertFalse(fuzzy_match(b, a))

    def test_fuzzy_match_date(self):
        d = datetime(2022, 8, 21, 1)
        time_diff = timedelta(days=5)
        a = {
            "img": 1,
            "title": "Homemade beef tacos.",
            "found": d.strftime(DATETIME_FMT),
        }
        b = {
            "img": 2,
            "title": "[homemade] Beef tacos.",
            "found": (d + time_diff).strftime(DATETIME_FMT),
        }
        self.assertGreater(time_diff, TIME_THRESHOLD)
        self.assertFalse(fuzzy_match(a, b))
        self.assertFalse(fuzzy_match(b, a))

    def test_missing_title(self):
        d = datetime(2022, 8, 21, 1)
        ds = d.strftime(DATETIME_FMT)
        a = {"img": 1, "found": ds}
        b = {"img": 2, "title": "[homemade] Beef tacos.", "found": ds}
        self.assertFalse(fuzzy_match(a, b))
        self.assertFalse(fuzzy_match(b, a))

    def test_missing_date(self):
        d = datetime(2022, 8, 21, 1)
        a = {
            "img": 1,
            "title": "Homemade beef tacos.",
            "found": d.strftime(DATETIME_FMT),
        }
        b = {"img": 2, "title": "[homemade] Beef tacos."}
        self.assertFalse(fuzzy_match(a, b))
        self.assertFalse(fuzzy_match(b, a))
