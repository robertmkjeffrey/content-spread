import utils
import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
import os


CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, 'r') as f:
    config = yaml.load(f, SafeLoader)
LIBRARY_DIRECTORY = config["library_directory"]
ARCHIVE_DIRECTORY = os.path.join(LIBRARY_DIRECTORY, "archive")
# Records if the config has been update to check if we should write it back.

def reddit_upload_single_post(post, archive, verbose=False):
    # Get post metadata 
    with open(os.path.join(LIBRARY_DIRECTORY, post, "data.yaml"), 'r') as f:
        post_data = yaml.load(f, SafeLoader)

    # Upload all images in the media folder.
    # Filepaths of images
    images = [os.path.join(LIBRARY_DIRECTORY, post, "media", x) for x in os.listdir(os.path.join(LIBRARY_DIRECTORY, post, "media"))]

    imgur_client = utils.create_imgur_client(config)
    if verbose:
        print("Uploading to imgur...")
    if len(images) != 1:
        url = utils.get_album_link(utils.upload_album_to_imgur(images, imgur_client))
    else:
        url = utils.upload_post_to_imgur(images[0], imgur_client)["link"]

    if verbose:
        print(url)

    ## Upload to reddit
    reddit_client = utils.create_reddit_client(config)
    for subreddit in post_data["subreddits"]:
        reddit_post = utils.upload_to_reddit(url, subreddit, post_data, reddit_client)
        utils.post_sources(reddit_post, post_data)
        if verbose:
            print(reddit_post.shortlink)


    # Move files to archive
    if archive:
        if verbose:
            print("Archiving...")
        os.rename(os.path.join(LIBRARY_DIRECTORY, post), os.path.join(ARCHIVE_DIRECTORY, post))

    if verbose:
        print("Complete!")

if __name__ == "__main__":
    print("Welcome to the reddit uploader!")
    print("Which post would you like to upload? Give the folder name or type \"random\".")

    post = input("Post: ")
    if post.lower() == "random":
        # TODO: select a random post by 
        raise NotImplementedError()
    elif post[0:5] != "post_":
        print("Error: unrecognised post format. It should start with post_")
        exit()

    reddit_upload_single_post(post, archive=True, verbose=True)


