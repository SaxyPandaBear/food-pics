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

### Why does the Procfile not do anything?
There is a dummy `Procfile` in this that SHOULD NOT be modified, as it is just a
placeholder in order to enforce free dyno usage for using the Heroku Scheduler 
addon. When no Procfile is defined, and no processes running on the environment,
the Heroku Scheduler addon does not give the free dyno option - just the paid 
tiers.

### Configuring the scheduler
Using the [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler), you
can schedule one-off dyno execution for a process. This makes it easy to perform
simple serverless workflows. Create a new job for your application, and just use
the UI to set the schedule and execution script to run. The execution script should
be like what you would run if you were going to run a one-off dyno from the CLI.

For something like
```bash
heroku run -a my-dyno-12345 python food-pics/food.py
```
you would want to configure with just the `python food-pics/food.py` part.

### How does it know what webhook to push to?
Currently it's only pushing to one webhook, defined in the `WEBHOOK_URL` 
environment variable (in Heroku), but can split this out into separate
variables as necessary in the future.
