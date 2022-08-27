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

### Testing
Run Python unit tests as follows:
```bash
# From the root of the repository
cd food-pics/  # test discovery from the root directory doesn't work
python -m unittest  # will find all files prefixed 'test_' and execute them
```
An example output of this:
```
$ python3 -m unittest
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
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
