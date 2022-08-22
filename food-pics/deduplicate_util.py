from typing import Dict
from redis import Redis
from thefuzz import fuzz
from datetime import timedelta
import json
from csv import DictReader


FUZZ_THRESHOLD = 80
ONE_DAY = timedelta(hours=24)


def already_posted(r: Redis, author: str, post: Dict) -> bool:
    """
    https://github.com/SaxyPandaBear/my-webhooks/issues/2
    Check the Redis cache to see if the given FoodPost has already been posted.
    The key for the cache is the author/user who submitted the post. This maps
    to a set of JSON objects, which contain the post ID and its image hash.
    Note that this does not modify/add to the Redis cache, only reads from it.
    @param r The Redis cache client
    @param author The username of the Reddit user that posted the submission
    @param img_hash The hash of the downloaded image file
    @param post_id The Reddit submission ID to check for
    @return True if the post is already in the cache, False otherwise
    """
    if r.exists(author) == 0:
        print(f"Reddit user {author} does not exist in the cache yet.")
        return False  # the author key is not in the Redis cache at all
    # If the user exists, need to check the submission IDs, or the image hashes
    # to see if this image has already been posted. If not, we can store it.
    # each member is a JSON string, so need to unmarshal it
    post_id = post["id"]
    img_hash = post["hash"]
    posted = [json.loads(s) for s in r.smembers(author)]
    for p in posted:
        if p["id"] == post_id or p["hash"] == img_hash or fuzzy_match(p, post):
            print(f"Post {post_id} by {author} has already recently.")
            return True
    print(f"Post {post_id} has not been posted yet.")
    return False  # it was not posted already.


def fuzzy_match(a, b) -> bool:
    title_a = a["title"].lower()
    title_b = b["title"].lower()
    ratio = fuzz.token_set_ratio(title_a, title_b)
    if ratio < FUZZ_THRESHOLD:
        return False
    return abs(a["date"] - b["date"]) < ONE_DAY
