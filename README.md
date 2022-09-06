Food Pics
=========

This is a script that connects to Reddit, uses a configured 
delimited list of subreddit names, scrapes the subs for "hot" 
posts, and submits a random one to a configured Discord webhook.

The original idea for this came from 
https://github.com/SaxyPandaBear/discord-food-bot

### Configurations
Configurations for the script are expected to be in environment variables. Redis variables
are injected by Railway ([docs](https://docs.railway.app/databases/redis#connect))
| Key                    | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `REDISHOST`            | hostname to connect to Railway Redis instance          |
| `REDISUSER`            | Redis user                                             |
| `REDISPORT`            | Port to connect to on Redis instance                   |
| `REDISPASSWORD         | Redis password                                         |
| `WEBHOOK_URL`          | URL for Discord channel webhook                        |
| `REDDIT_CLIENT_ID`     | client ID for Reddit API access                        |
| `REDDIT_CLIENT_SECRET` | client secret for Reddit API access                    |
| `SUBREDDITS`           | subreddits to scrape split by `+`, e.g.: `foo+bar+Baz` |
| `LIMIT`                | (optional) batch size for scraping from Reddit         |


### Dependency management
This project uses pipenv, which has it's challenges.

Railway requires a `requirements.txt` file to detect a Python app, so
run:
```bash
pipenv requirements > requirements.txt
```
after updating dependencies in order to propagate them on deployments.

### How does it know what webhook to push to?
Currently it's only pushing to one webhook, defined in the `WEBHOOK_URL` 
environment variable (in Heroku), but can split this out into separate
variables as necessary in the future.

### How does this prevent duplicate posts?
There are a couple methods to try to deduplicate Reddit submissions. 
1. Perform exact match on submission IDs
1. Compute image hash and compare with other image hashes from the same author
1. Fuzzy match submission title with same author, from the past week

### Testing
Run Python unit tests as follows:
```bash
# From the root of the repository
pipenv run python -m unittest  # will find all files prefixed 'test_' and execute them
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
(pipenv) black .
(pipenv) pylint --rcfile ../.pylintrc .
```

### Troubleshooting
#### Clear Redis data
TODO: update this since not using Heroku anymore
1. Log in to the Heroku CLI
1. `heroku redis:cli -a the-app-name`
1. `flushall`
