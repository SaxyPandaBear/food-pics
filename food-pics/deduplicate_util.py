from typing import Dict
from food_post import FoodPost
from image_util import compute_image_hash
from redis import Redis

def check_for_duplicates(r: Redis, author: str, fp: FoodPost) -> bool: 
    """
    
    """
    if r.exists(author) > 0:
        pass
    else:
        # No user exists with this user, so we can just
        # post it.
        # 1. Compute the hash
        # 2. 
        pass
    pass
