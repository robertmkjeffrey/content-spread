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

print("Welcome to the reddit uploader!")
print("Which post would you like to upload? Give the folder name or type \"random\".")

post = input("Post: ")
if post.lower() == "random":
    # TODO: select a random post by 
    raise NotImplementedError()
elif post[0:5] != "post_":
    print("Error: unrecognised post format. It should start with post_")
    exit()

# Get post metadata 
with open(os.path.join(LIBRARY_DIRECTORY, post, "data.yaml"), 'r') as f:
    post_data = yaml.load(f, SafeLoader)

# Upload all images in the media folder.
# Filepaths of images
images = [os.path.join(LIBRARY_DIRECTORY, post, "media", x) for x in os.listdir(os.path.join(LIBRARY_DIRECTORY, post, "media"))]

imgur_client = utils.create_imgur_client(config)
print("Uploading to imgur...")
if len(images) != 1:
    url = utils.get_album_link(utils.upload_album_to_imgur(images, imgur_client))
else:
    url = utils.upload_post_to_imgur(images[0], imgur_client)["link"]

print(url)

## Upload to reddit
reddit_client = utils.create_reddit_client(config)
reddit_post = utils.upload_to_reddit(url, post_data, reddit_client)
utils.post_sources(reddit_post, post_data)

# Move files to archive
print("Archiving...")
os.rename(os.path.join(LIBRARY_DIRECTORY, post), os.path.join(ARCHIVE_DIRECTORY, post))

print("Complete! Here's the link:")
print(reddit_post.shortlink)




