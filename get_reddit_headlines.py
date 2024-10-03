#!/usr/bin/env python3
import praw

# Add your credentials
# Check https://www.reddit.com/r/reddit.com/wiki/api/
reddit = praw.Reddit(
    client_id="???",
    client_secret="???",
    user_agent="???",
)

def get_reddit_headlines(
    subreddit="worldnews"
):
    """
    Get up to 20 headlines (titles) of 'hot' submissions (posts) from a certain
    subreddit
    API Doc: https://www.reddit.com/dev/api/#GET_hot

   :param str subreddit: the name of the subreddit to retrieve headlines from
   :return: a list of titles of hot submissions
   :rtype: list of str
   :raises ValueError: if no topics can be found
   """
    submissions = reddit.subreddit("worldnews").hot(limit=22)
    headlines = list()

    for sub in submissions:
        headlines.append(sub.title)
    # Slice away first two, because they tend to be (permanent) moderator
    # posts
    if len(headlines) > 2:
        return headlines[2:]
    raise ValueError("Did not manage to find ")
        
headlines = get_reddit_headlines()

print("yes")
