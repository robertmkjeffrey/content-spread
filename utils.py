import re

def load_config(CONFIG_FILE = "config.yaml"):
    import yaml
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.load(f, yaml.SafeLoader)
    return config

def get_short_source(source):
    """Extract a shortname from a source. """
    # Twitter username
    tm = re.match(".*twitter.com\/(.*)\/status*.", source)
    if tm:
        return "@"+tm.group(1)

    return None
    
def get_image_links(sources, twitter_client=None):
    links = []
    for source in sources:
        if twitter_client is not None:
            # Twitter links
            idm = re.match(".*twitter.com\/.*\/status\/(\d*)", source)
            if idm:
                id = idm.group(1)
                links += get_tweet_media_urls(id, twitter_client)
    
    return links

# Imgur code - used to host files on imgur.

def create_imgur_client(config):
    from imgurpython import ImgurClient
    client = ImgurClient(config["imgur"]["client_id"], config["imgur"]["client_secret"])
    return client

def format_title_with_source(metadata):
    return metadata["title"] + " [" + metadata["short_source"] + "]"

def upload_album_to_imgur(files, client, metadata=None):
    # Can't create albums - library doesn't have the features to do it.
    posts = [client.upload_from_path(file) for file in files]

    # TODO: remove requests dependency
    # We have to do this manually as the library doesn't support deletehashes
    import requests

    album_url = "https://api.imgur.com/3/album"


    payload={f'deletehashes[]': [post["deletehash"] for post in posts],
    'cover': '{{imageHash}}'}
    if metadata is not None:
        payload['title'] = format_title_with_source(metadata)
        payload['description'] = "Sources: " + "\n".join(metadata["source_links"])
        
    files=[]
    headers = {
    'Authorization': f'Client-ID {client.client_id}'
    }

    response = requests.request("POST", album_url, headers=headers, data=payload, files=files)

    return response.json()["data"]["id"]

def get_album_link(album):
    return f"https://imgur.com/a/{album}"

def upload_post_to_imgur(file, client):
    return client.upload_from_path(file)

# reddit

def create_reddit_client(config):
    import praw
    client = praw.Reddit(
        client_id=config["reddit"]["client_id"],
        client_secret=config["reddit"]["client_secret"],
        username=config["reddit"]["username"],
        password=config["reddit"]["password"],
        user_agent=config["reddit"]["agent_name"],
)
    client.validate_on_submit=True
    return client

def upload_to_reddit(url, subreddit, metadata, client):
    submission = client.subreddit(subreddit).submit(
        title=format_title_with_source(metadata),
        url = url,
        resubmit = False,
        nsfw = metadata["nsfw"],
    )

    return submission

def post_sources(reddit_post, metadata):
    if len(metadata["source_links"]) == 1:
        reddit_post.reply(f"[Source]({metadata['source_links'][0]})")
    else:
        reply_text = "Sources:\n\n" + "\n\n".join(metadata['source_links'])
        reddit_post.reply(reply_text)

# Twitter

def create_twitter_client(config):
    import tweepy
    return tweepy.Client(
        bearer_token=config["twitter"]["bearer_token"], 
        consumer_key=config["twitter"]["api_key"], 
        consumer_secret=config["twitter"]["api_secret"], 
        access_token=config["twitter"]["access_token"], 
        access_token_secret=config["twitter"]["access_token_secret"]
    )

def get_tweet_media_urls(id, client):
    links = []
    tweet = client.get_tweet(id=id, expansions="attachments.media_keys", media_fields="url")
    for i, image in enumerate(tweet.includes["media"]):
        if image.type == "photo":
            links.append(image.url)
        elif image.type == "video":
            print("Warning: can't download video links.")
    return links

# def download_media_from_tweet(id, client):
#     import urllib
#     import os
#     tweet = client.get_tweet(id=id, expansions="attachments.media_keys", media_fields="url")
#     for i, image in enumerate(tweet.includes["media"]):
#         link = image.url
#         r = urllib.request.urlopen(link)
#         if image.type == "photo":
#             suffix = ".jpg"
#         elif image.type == "video":
#             suffix = "mp4"
#         else:
#             pass
#         with open(str(id) + "_" + str(i) + suffix, 'wb') as f:
#             f.write(r.read())