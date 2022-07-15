# Go through a user's media posts. For each post, present it and let the user download if wanted.
# Remember what posts have been seen so far! Store this using time periods.

# Robert Jeffrey (me@rmkj.dev) (c) 2021

# %% Initalisation
import yaml
from utils import *
from reddit_generate_post import create_reddit_post_record, input_desired_subreddits

CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, 'r') as f:
    config = yaml.load(f, yaml.SafeLoader)

twitter_client = create_twitter_client(config)

# %% Choose user
print("What user do you want to go through?")
username = []
while len(username) == 0:
    username = input("Twitter Username: ").lower()


if username[0] == "@":
    # drop "@"
    username = username[1:]

include_retweets = input("Include retweets? (y/n): ").lower() in ["y", "yes"]

# %%
user = twitter_client.get_user(username=username)

# %% Go through tweets and get user input.
pagination_token = None
while True:
    # Todo: keep track of post times to do later analysis.
    tweet_page = twitter_client.get_users_tweets(
        user.data.id, 
        exclude="replies" + (",retweets" if not include_retweets else ""),
        expansions="attachments.media_keys",
        pagination_token=pagination_token
    )

    pagination_token = tweet_page.meta["next_token"]

    # Set of all media keys that are photos (instead of videos).
    photo_media = {media.media_key for media in tweet_page.includes["media"] if media.type == "photo"}

    for tweet in tweet_page.data:
        # Continue if tweet has no attachments
        if tweet.attachments is None or "media_keys" not in tweet.attachments:
            continue
        # Or has videos.
        if not photo_media.issuperset(set(tweet.attachments["media_keys"])):
            continue

        # We now have a tweet with an image.

        tweet_id = tweet.id

        tweet = twitter_client.get_tweet(id=tweet_id, expansions=["attachments.media_keys", "author_id", "referenced_tweets.id"], media_fields="url")

        # If there's a source tweet, this is a retweet. 
        # Get the original tweet instead.
        if "tweets" in tweet.includes:
            included_tweets = tweet.includes["tweets"]
            assert len(included_tweets) == 1
            included_tweets[0]

            tweet_id = included_tweets[0].id
            tweet = twitter_client.get_tweet(id=tweet_id, expansions=["attachments.media_keys", "author_id", "referenced_tweets.id"], media_fields="url")


        tweet_author = tweet.includes["users"][0].username
        image_urls = [x.url for x in tweet.includes["media"]]

        print(tweet_id)
        print("@" + tweet_author)
        print(tweet.data.text)
        for url in image_urls:
            print(url)
        print()

        if input("Download? ").lower() in ["y", "yes"]:
            new_post = {
                    "source_links" : [f"https://twitter.com/{tweet_author}/status/{tweet_id}"], 
                    "image_links" : image_urls, 
                    "short_source" : f"@{tweet_author}", 
                    "title" : input("Title: "), 
                    "subreddits" : input_desired_subreddits(), 
                }

            new_post['nsfw'] = input_boolean_loop("NSFW? (y/n): ")
            create_reddit_post_record(new_post)

            print()

    if input("Continue to next page? (y/n): ") not in ["y", "Y", "yes", "Yes"]:
        break

# %%
