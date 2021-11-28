from typing import Dict
from redis import Redis
from praw.models import Submission
from image_util import compute_image_hash

def check_for_duplicates(r: Redis, s: Submission) -> bool: 
    """
    
    """
    user = s.author.name
    if r.exists(user) > 0:
        pass
    else:
        # No user exists with this user, so we can just
        # post it.
        pass
    pass


def submission_to_json(s: Submission, img_hash: int) -> Dict:
    """
    Transform the submission and it's hash into a Python
    dictionary, so that it can be converted into a JSON string
    that gets persisted in the Redis cache as part of an array.

    Example:
    {
        "id": "foo-bar-baz",
        "url": "https://i.reddit.com/abc123",
        "hash": "1234567890"
    }
    @param s Submission object from PRAW for a given post that was verified
    @param img_hash the hash of the byte array of the Image from PIL
    """
    return {
        'id': s.id,
        'url': s.url,
        'hash': str(img_hash)
    }
