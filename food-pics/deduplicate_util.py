from typing import Dict
from food_post import FoodPost
from redis import Redis
import json

def already_posted(r: Redis, author: str, img_hash: int, post_id: str) -> bool: 
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
        return False  # the author key is not in the Redis cache at all
    # If the user exists, need to check the submission IDs, or the image hashes
    # to see if this image has already been posted. If not, we can store it.
    # each member is a JSON string, so need to unmarshal it
    posted = [json.loads(s) for s in r.smembers(author)]
    for p in posted:
        if p['id'] == post_id or p['hash'] == img_hash:
            return True
    return False  # it was not posted already.
