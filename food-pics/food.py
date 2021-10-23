import os

# Read the Redis URL from the environment. This value gets injected
# by Heroku
redis_url = os.environ['REDIS_URL']
