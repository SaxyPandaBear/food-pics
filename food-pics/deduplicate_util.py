from typing import Dict
from redis import Redis
from thefuzz import fuzz
from datetime import datetime, timedelta
from food_post import DATETIME_FMT
import json


FUZZ_THRESHOLD = 65  # lower threshold isn't bad. we want low tolerance for dupes.
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
    post_id = post["id"]
    if r.exists(f"{author}/{post_id}") > 0:
        print(f"Post {post_id} by {author} has already been used recently.")
        return True

    # https://github.com/SaxyPandaBear/my-webhooks/issues/14
    # If the author/post combination key does not exist, there is still
    # a possibility that the author reposted the same image, so it needs
    # a deduplication check. Since all of the keys are expected to follow
    # the scheme "author/postId", we can scan the Redis cache by the author
    # name, iterate over the returned records and compare image hashes and
    # post titles to do a fuzzy match.
    r.scan()
    i = r.scan_iter(f"{author}/*")
    done = False
    while not done:
        try:
            key = next(i)
            val = r.get(key)  # realistically this should never be None...
            if val is not None:
                p = json.loads(val)
                if fuzzy_match(p, post):
                    print(
                        f"Something similar to {author}/{post_id} has already been posted recently."
                    )
                    return True
        except StopIteration:
            done = True
    print(f"Post {post_id} has not been posted yet.")
    return False  # it was not posted already.


def fuzzy_match(a, b) -> bool:
    if "hash" not in a or "hash" not in b:
        return False
    if a["hash"] == b["hash"]:
        return True

    if "title" not in a or "title" not in b:
        return False
    title_a = a["title"].lower()
    title_b = b["title"].lower()
    ratio = fuzz.token_set_ratio(title_a, title_b)
    if ratio < FUZZ_THRESHOLD:
        return False

    if "date" not in a or "date" not in b:
        return False

    date1 = datetime.strptime(a["date"], DATETIME_FMT)
    date2 = datetime.strptime(b["date"], DATETIME_FMT)
    return abs(date1 - date2) < ONE_DAY
