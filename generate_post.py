import os
import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
from pprint import pprint

POST_NAME_LENGTH = 10

CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, 'r') as f:
    config = yaml.load(f, SafeLoader)
# Records if the config has been update to check if we should write it back.
update_config = False
if config is None:
    config = {}

from utils import get_short_source
LIBRARY_DIRECTORY = "post_library"
ARCHIVE_DIRECTORY = os.path.join(LIBRARY_DIRECTORY, "archive")

print("Welcome to the post generator! I am 9653-cs, at your service.")

new_post = {}

print("First, enter links to the images you'd like to save. Enter a blank line to finish.")
new_post["image_links"] = []
while True:
    link = input(f"Image #{len(new_post['image_links']) + 1}: ")
    if len(link) > 0:
        new_post["image_links"].append(link)
    elif not new_post["image_links"]:
        print("Error: must provide at least one link. Try again.")
    else:
        break

print()
print("Great! What's main source for that? Again, blank line to finish.")
new_post['source_links']= []
while True:
    source = input(f"Source #{len(new_post['source_links'])+1}: ")
    if len(source) > 0:
        new_post['source_links'].append(source)
    elif not new_post["source_links"]:
        print("Error: must provide at least one source. Try again.")
    else:
        break

# TAutomatically get this from the source if possible
new_post['short_source'] = get_short_source(new_post['source_links'][0])
if new_post['short_source'] is None:
    print("Next, give a short name for the attribution.")
    new_post['short_source'] = input("Short name: ")
else:
    print("Detected source " + new_post["short_source"])

print()
print("Give a title for the post. I'll add the attribution for you.")
new_post['title'] = input("Title: ")

print("Great! Which subreddit(s) should I designate it for?")
new_post['subreddit'] = None
printed_one = False

try:
    if config['saved_subreddits'] is None:
        config['saved_subreddits'] = []
    choices = {0: None}
    for i, subreddit in enumerate(config['saved_subreddits']):
        printed_one = True
        choices[i+1] = subreddit
        print(f"{i+1}: /r/{subreddit.lower()}")
except KeyError:
    config["saved_subreddits"] = []

if printed_one:
    print("For a different subreddit, enter 0.")
    choice = int(input())
    new_post['subreddit'] = choices[choice]

if new_post['subreddit'] is None:
    print("Enter the subreddit I should post it in. Don't include the \"r/\"!")
    new_post['subreddit'] = input("Subreddit: ").lower()
    print("Should I save that?")
    if input().lower() in ["y", "yes", "good drone"]:
        config['saved_subreddits'].append(new_post['subreddit'])
        update_config = True

print()
print("Finally, is the post NSFW? (y/n)")
while True:
    nsfw_input = input("NSFW: ").lower()
    if nsfw_input in ["y", "yes"]:
        new_post["nsfw"] = True
        break
    elif nsfw_input in ["n", "no"]:
        new_post["nsfw"] = False
        break
    else:
        print("I didn't understand that...")

print("Okay, we're done! Saving this post:")
pprint(new_post)

import random
import string
post_directory = os.path.join(LIBRARY_DIRECTORY, "post_"+''.join(random.choices(string.ascii_lowercase + string.digits, k=POST_NAME_LENGTH)))
print(f"Directory name: {post_directory}")
os.mkdir(post_directory)


import urllib.request

for i, link in enumerate(new_post["image_links"]):
    r = urllib.request.urlopen(link)
    with open(os.path.join(post_directory, "image"+str(i)+".jpg"), 'wb') as f:
        f.write(r.read())

with open(os.path.join(post_directory, "data.yaml"), 'w') as f:
    yaml.dump(new_post, f, SafeDumper)

if update_config:
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, SafeDumper)
