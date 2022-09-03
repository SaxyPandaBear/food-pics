Food Pics
=========

This is a one-off script that connects to Reddit, uses a configured 
delimited list of subreddit names, scrapes the subs for "hot" 
posts, and submits a random one to a configured Discord webhook.

The original idea for this came from 
https://github.com/SaxyPandaBear/discord-food-bot

### Configurations
Configurations for the script are expected to be in environment variables.
| Key                    | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `REDIS_URL`            | endpoint to connect to Redis                           |
| `WEBHOOK_URL`          | URL for Discord channel webhook                        |
| `REDDIT_CLIENT_ID`     | client ID for Reddit API access                        |
| `REDDIT_CLIENT_SECRET` | client secret for Reddit API access                    |
| `SUBREDDITS`           | subreddits to scrape split by `+`, e.g.: `foo+bar+Baz` |
| `LIMIT`                | (optional) batch size for scraping from Reddit         |

### Setup
This project is written in Python 3.9.13.
Install project requirements:
```bash
python -m pip install -r requirements.txt
# or
pip install -r requirements.txt
```

### Testing
Run Python unit tests as follows:
```bash
# From the root of the repository
pytest # this does test auto discovery
```
An example output of this:
```
$ pytest
===================== test session starts ======================
platform darwin -- Python 3.9.13, pytest-7.1.2, pluggy-1.0.0
rootdir: /path/to/repo/my-webhooks
collected 30 items                                             

food-pics/test_deduplicate_util.py .............         [ 43%]
food-pics/test_food_post.py ..............               [ 90%]
food-pics/test_image_util.py ...                         [100%]

====================== 30 passed in 3.06s ======================
```

### Linting and Formatting
Uses `black` and `pylint` for formatting and linting.
```bash
pipenv shell
(pipenv) cd ./food-pics/
(pipenv) black .
(pipenv) pylint --rcfile ../.pylintrc .
```

### Troubleshooting
#### Clear Redis data
1. Log in to the Heroku CLI
1. `heroku redis:cli -a the-app-name`
1. `flushall`
