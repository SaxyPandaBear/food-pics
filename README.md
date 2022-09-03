My Webhooks
===========

This repo contains code that will be executed and push content to webhooks. 

This can be run directly with one-off dynos on Heroku. Assuming that your
dyno is set up with the right environment (the `./food-pics` webhook code
uses Python), you should be able to invoke a one-off dyno to run the code.

Example:
```bash
heroku run -a my-dyno-12345 python food-pics/food.py
```

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
