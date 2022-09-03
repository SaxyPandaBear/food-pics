from deduplicate_util import already_posted
from food_post import FoodPost
import os
import json
from typing import List, Optional
from datetime import timedelta
from praw import Reddit
from redis import Redis, from_url as init_redis_client
import requests
import random
import sys
import schedule
import time
import queue
import threading


# Keep records in Redis for at most one week. Reddit moves fast,
# so although this doesn't prevent karma farmer reposts from
# showing up, a week is still a long time.
TIME_TO_LIVE = timedelta(weeks=1)


def get_submission(
    redis_client: Redis, reddit_client: Reddit, subs: str, request_limit: int
) -> Optional[FoodPost]:
    """
    Retrieve a "hot" post from the list of subreddits defined in the
    'SUBREDDITS' environment variable, returning a FoodPost object
    @param redis_client  Redis client to interface with Heroku Redis
    @param reddit_client PRAW Reddit client
    @return a "hot" post from the list of subreddits, or None if there are no
            posts, or an error occurs
    """
    # fallback in case all of the posts are already used
    submissions: List[FoodPost] = []
    try:
        for submission in reddit_client.subreddit(subs).hot(limit=request_limit):
            fp = FoodPost.from_submission(submission)
            submissions.append(fp)
            fp_hash = fp.to_json()
            if not already_posted(redis_client, submission.author.name, fp_hash):
                redis_client.set(
                    f"{submission.author.name}/{fp.id}",
                    json.dumps(fp_hash),
                    ex=TIME_TO_LIVE,
                )
                return fp  # short-circuit early if we know this is new
    except Exception as e:
        print(f"An unexpected exception occurred: {repr(e)}")
        return None
    # if we did not return before this, then all of the hot posts
    # returned have already been posted. default to return a random one,
    # rather than try the search again to limit execution time
    if len(submissions) > 0:
        print("Picking random submission")
        return random.choice(submissions)
    else:
        print("No submissions found from Reddit for supplied subreddits")
        return None


def post():
    """
    Initialize the Reddit and Redis clients, get a random Reddit post
    from the configured subreddits, and post to the webhook URL
    """
    # Read the Redis URL from the environment. This value gets injected
    # by Heroku
    print("Finding Reddit submission")
    r = Redis(
        host=os.getenv("REDISHOST"),
        username=os.getenv("REDISUSER"),
        password=os.getenv("REDISPASSWORD"),
        port=os.getenv("REDISPORT"),
        decode_responses=True,
    )
    print("Instantiated Redis client")

    # TODO: modify this to allow for multiple webhook URLs
    webhook_url = os.getenv("WEBHOOK_URL")

    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    # expected to be a list of subreddits to search, separated by +
    # example: "foo+bar+baz" where foo, bar, and baz are all subreddits
    subs = os.getenv("SUBREDDITS")
    request_limit = int(os.getenv(key="LIMIT", default="24"))

    if webhook_url is None:
        raise Exception("No webhook URL specified in environment")
    if reddit_client_id is None or reddit_client_secret is None:
        raise Exception("Reddit API credentials not configured in environment")
    if subs is None:
        raise Exception("No subreddits list defined in environment")

    reddit = Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent="discord:food_waifu:v0.2",
    )
    print("Instantiated Reddit client")

    submission = get_submission(r, reddit, subs, request_limit)
    if submission is None:
        raise Exception("No Reddit submission found")
    embed = submission.to_embed()
    data = {
        "username": "Food from Reddit",
        "avatar_url": "https://i.imgur.com/gLP2Tl0.jpeg",
        "embeds": [embed],
    }
    print(f"Submitting {data} to Discord webhook")
    result = requests.post(url=webhook_url, json=data)
    result.raise_for_status()

    print("Payload delivered successfully, code {}.".format(result.status_code))


jobqueue = queue.Queue()
schedule.every().hour.at(":00").do(jobqueue.put, post)


def worker_main():
    print("Running job exec thread")
    while True:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()


if __name__ == "__main__":
    print("Starting cron scheduler")

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()
    while True:
        schedule.run_pending()
        time.sleep(1)
