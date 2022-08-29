from typing import Dict
from thefuzz import fuzz
from google.cloud import firestore
from datetime import datetime, timedelta
from food_post import DATETIME_FMT


FUZZ_THRESHOLD = 65  # lower threshold isn't bad. we want low tolerance for dupes.
TIME_THRESHOLD = timedelta(hours=24)


def already_posted(db: firestore.CollectionReference, post: Dict) -> bool:
    """
    https://github.com/SaxyPandaBear/my-webhooks/issues/15
    Check if the post is already found in the database.
    @param db   Google Cloud Firebase client
    @param post The submission from Reddit, in dictionary form
    @returns    True if the post is found exactly or matches close enough
                to another existing post by the same author
    """
    doc_ref = db.document(post["id"])
    doc = doc_ref.get()
    if doc.exists():
        return True  # if the post with the exact ID exists, return early

    docs = db.where("author", "==", post["author"]).stream()
    for d in docs:
        if fuzzy_match(post, d.to_dict()):
            return True
    return False


def fuzzy_match(a, b) -> bool:
    if "img" not in a or "img" not in b:
        return False
    if a["img"] == b["img"]:
        return True

    if "title" not in a or "title" not in b:
        return False
    title_a = a["title"].lower()
    title_b = b["title"].lower()
    ratio = fuzz.token_set_ratio(title_a, title_b)
    if ratio < FUZZ_THRESHOLD:
        return False

    if "found" not in a or "found" not in b:
        return False

    date1 = datetime.strptime(a["found"], DATETIME_FMT)
    date2 = datetime.strptime(b["found"], DATETIME_FMT)
    return abs(date1 - date2) < TIME_THRESHOLD
