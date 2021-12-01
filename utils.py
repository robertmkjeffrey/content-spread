import regex as re

def get_short_source(source):
    """Extract a shortname from a source. """
    # Twitter username
    tm = re.match(".*twitter.com\/(.*)\/status*.", source)
    if tm:
        return "@"+tm.group(1)

    return None

def get_twitter_image(tweet_link):
    # TODO: complete
    idm = re.match(".*twitter.com\/.*\/status\/(\d*)", tweet_link)
    if not idm:
        return
    id = idm.group(1)

# Imgur code - used to host files on imgur.

def create_imgur_client(config):
    from imgurpython import ImgurClient
    client = ImgurClient(config["imgur"]["client_id"], config["imgur"]["client_secret"])
    return client

def format_title_with_source(metadata):
    return metadata["title"] + " [" + metadata["short_source"] + "]"

def upload_album_to_imgur(files, metadata, client):
    # Can't create albums - library doesn't have the features to do it.
    raise NotImplementedError
    posts = [client.upload_from_path(file) for file in files]

    album = client.create_album({
        "title": format_title_with_source(metadata),
        "description": "Sources: " + "\n".join(metadata["source_links"]),
        "ids" : [post["deletehash"] for post in posts]
    })

    return album

def get_album_link(album):
    raise NotImplementedError

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

def upload_to_reddit(url, metadata, client):
    submission = client.subreddit(metadata["subreddit"]).submit(
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