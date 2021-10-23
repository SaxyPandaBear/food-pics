Food Pics
=========

Post random trending food pictures sourced from Reddit.
A Redis cache is used to mitigate reposting the same content,
by deduplicating on post IDs. Note that this does not counteract
cross-posting, since technically the post IDs would be different.

The original idea for this came from 
https://github.com/SaxyPandaBear/discord-food-bot

TODO: implement a way to deduplicate x-posts
