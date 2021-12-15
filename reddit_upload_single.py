import utils
import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
import os

from pprint import pprint

SUBREDDIT_INDEX_FILE_NAME = "subreddit_index"

CONFIG_FILE = "config.yaml"
config = utils.load_config(CONFIG_FILE)
LIBRARY_DIRECTORY = config["library_directory"]
ARCHIVE_DIRECTORY = os.path.join(LIBRARY_DIRECTORY, "archive")
# Records if the config has been update to check if we should write it back.

def reddit_upload_single_post(post_id, archive=True, verbose=False):
    # Get post metadata 
    with open(os.path.join(LIBRARY_DIRECTORY, post_id, "data.yaml"), 'r') as f:
        post_data = yaml.load(f, SafeLoader)

    # Upload all images in the media folder.
    # Filepaths of images
    images = [os.path.join(LIBRARY_DIRECTORY, post_id, "media", x) for x in sorted(os.listdir(os.path.join(LIBRARY_DIRECTORY, post_id, "media")))]

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
        os.rename(os.path.join(LIBRARY_DIRECTORY, post_id), os.path.join(ARCHIVE_DIRECTORY, post_id))

        index_file = os.path.join(LIBRARY_DIRECTORY, SUBREDDIT_INDEX_FILE_NAME)
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                subreddit_index = yaml.load(f, SafeLoader)

            for subreddit in post_data["subreddits"]:
                subreddit_index[subreddit].remove(post_id)

            with open(index_file, "w") as f:
                yaml.dump(subreddit_index, f, SafeDumper)

    if verbose:
        print("Complete!")

if __name__ == "__main__":
    print("Welcome to the reddit uploader!")
    print("Which post would you like to upload? Give the folder name, type \"list\" or type \"random\".")

    while True:
        post = input("Post: ")
        if post.lower() == "list":
            index_file = os.path.join(LIBRARY_DIRECTORY, SUBREDDIT_INDEX_FILE_NAME)
            if os.path.exists(index_file):
                with open(index_file, "r") as f:
                    subreddit_index = yaml.load(f, SafeLoader)
                pprint(subreddit_index)
            else:
                print("No subreddit index found.")
        elif post.lower() == "random":
            # TODO: select a random post by 
            raise NotImplementedError()
        elif post[0:5] != "post_":
            print("Error: unrecognised post format. It should start with post_")
            exit()
        else:
            reddit_upload_single_post(post, archive=True, verbose=True)
            break


