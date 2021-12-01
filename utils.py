import regex as re

def get_short_source(source):
    """Extract a shortname from a source. """
    # Twitter username
    tm = re.match(".*twitter.com\/(.*)\/status*.", source)
    if tm:
        return "@"+tm.group(1)

    return None

def upload_to_imgur(files, config, testing=False):
    from imgurpython import ImgurClient
    client = ImgurClient(config["imgur"]["client_id"], config["imgur"]["client_secret"])

    posts = []

    for file in files:
        return NotImplementedError()
        posts.append(client.upload_from_path(file))

    return posts