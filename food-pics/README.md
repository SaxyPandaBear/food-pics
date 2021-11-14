Food Pics
=========

Post random trending food pictures sourced from Reddit.
A Redis cache is used to mitigate reposting the same content,
by deduplicating on post IDs. Note that this does not counteract
cross-posting, since technically the post IDs would be different.

The original idea for this came from 
https://github.com/SaxyPandaBear/discord-food-bot

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