import os
import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
from pprint import pprint
import random
import string
import urllib.request

from utils import create_twitter_client, get_short_source, get_image_links, load_config

POST_NAME_LENGTH = 10
SUBREDDIT_INDEX_FILE_NAME = "subreddit_index"

CONFIG_PATH = "config.yaml"
config = load_config(CONFIG_PATH)
    
# Records if the config has been update to check if we should write it back.
update_config = False
if config is None:
    config = {}

LIBRARY_DIRECTORY = config["library_directory"]
ARCHIVE_DIRECTORY = os.path.join(LIBRARY_DIRECTORY, "archive")

def input_desired_subreddits():
    subreddits = []
    printed_one = False

    # If saved_subreddits is none or non-existant, create it.
    try:
        if config['saved_subreddits'] is None:
                config['saved_subreddits'] = []
    except KeyError:
        config["saved_subreddits"] = []

    # Get the subreddits the post is designated for.
    while True:
        # Print the saved subreddits.
        if len(config['saved_subreddits']) > 0:
            choices = {0: None}
            for i, subreddit in enumerate(config['saved_subreddits']):
                printed_one = True
                choices[i+1] = subreddit
                print(f"{i+1}: /r/{subreddit.lower()}")
            
            print("For a different subreddit, enter 0.")


            choice = input("Subreddit: ")
            if len(choice) == 0:
                break

            try:
                choice = int(choice)
            except ValueError:
                print(f"Invalid choice {choice}. Input must be an integer.")
                print()
                continue

            if int(choice) == 0:
                # If they entered zero, continue to get explicit text input.
                pass
            else:
                # Otherwise, take the input and start again.
                subreddits.append(choices[int(choice)])
                print()
                continue

        # If we didn't select a saved subreddit, get it as text.
        print("Enter the subreddit I should post it in. Don't include the \"r/\"!")
        new_subreddit = input("Subreddit: ").lower()
        subreddits.append(new_subreddit)
        print("Should I save that?")
        if input("Save? ").lower() in ["y", "yes"]:
            config['saved_subreddits'].append(new_subreddit)
            update_config = True

    return subreddits

def create_reddit_post_record(new_post : dict):

    assert set(new_post.keys()) == {
        "source_links", 
        "image_links", 
        "short_source", 
        "title", 
        "subreddits", 
        "nsfw",
    }

    # Generate a random post title of letters and digits.
    post_id = "post_"+''.join(random.choices(string.ascii_lowercase + string.digits, k=POST_NAME_LENGTH))
    post_directory = os.path.join(LIBRARY_DIRECTORY, post_id)
    print(f"Directory name: {post_id}")
    os.mkdir(post_directory)

    new_post["post_id"] = post_id

    # Make a media directory in the post file and save all linked images to that folder.
    os.mkdir(os.path.join(post_directory, "media"))
    for i, link in enumerate(new_post["image_links"]):
        r = urllib.request.urlopen(link)
        with open(os.path.join(post_directory,"media","image"+str(i)+".jpg"), 'wb') as f:
            f.write(r.read())

    # Dump the data into a yaml file.
    with open(os.path.join(post_directory, "data.yaml"), 'w') as f:
        yaml.dump(new_post, f, SafeDumper)

    # Open the existing subreddit index
    index_file = os.path.join(LIBRARY_DIRECTORY, SUBREDDIT_INDEX_FILE_NAME)
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            subreddit_index = yaml.load(f, SafeLoader)
    else:
        subreddit_index = {}

    # Update the subreddit index.
    for subreddit in new_post["subreddits"]:
        if subreddit not in subreddit_index:
            subreddit_index[subreddit] = []
        subreddit_index[subreddit].append(post_id)

    # Write the subreddit index.
    with open(index_file, "w") as f:
        yaml.dump(subreddit_index, f, SafeDumper)


if __name__ == "__main__":

    # Try to create a twitter client.
    twitter_client = create_twitter_client(config)

    print("Welcome to the post generator! I am 9653-cs, at your service.")

    post_data = {}

    # Get a list of source links.
    print()
    print("First, provide the source links. Enter a blank line to finish.")
    post_data['source_links']= []
    while True:
        source = input(f"Source #{len(post_data['source_links'])+1}: ")
        if len(source) > 0:
            post_data['source_links'].append(source)
        elif not post_data["source_links"]:
            print("Error: must provide at least one source. Try again.")
        else:
            break

    # Try to get the images from the source links.
    post_data["image_links"] = get_image_links(post_data["source_links"], twitter_client=twitter_client)
    if not post_data["image_links"]:
        print("Great! Now enter links to the images you'd like to save. Again, blank line to finish.")
        print("Note: I'm currently unable to create albums on imgur. Just use one source for now!")
        post_data["image_links"] = []
        while True:
            link = input(f"Image #{len(post_data['image_links']) + 1}: ")
            if len(link) > 0:
                post_data["image_links"].append(link)
            elif not post_data["image_links"]:
                print("Error: must provide at least one link. Try again.")
            else:
                break

    # Automatically get this from the source if possible
    post_data['short_source'] = get_short_source(post_data['source_links'][0])
    if post_data['short_source'] is None:
        print("Next, give a short name for the attribution.")
        post_data['short_source'] = input("Short name: ")
    else:
        print("Detected source " + post_data["short_source"])

    print()
    print("Give a title for the post. I'll add the attribution for you.")
    post_data['title'] = input("Title: ")

    #%% Get subreddit(s)
    print("Great! Which subreddit(s) should I designate it for?")
    print("Enter a blank line to finish.")
    
    post_data["subreddits"] = input_desired_subreddits()

    #%%
    print()
    print("Finally, is the post NSFW? (y/n)")
    while True:
        nsfw_input = input("NSFW: ").lower()
        if nsfw_input in ["y", "yes"]:
            post_data["nsfw"] = True
            break
        elif nsfw_input in ["n", "no"]:
            post_data["nsfw"] = False
            break
        else:
            print("I didn't understand that...")

    print("Okay, we're done! Saving this post:")
    pprint(post_data)

    create_reddit_post_record(post_data)

    # If the config was updated, save it
    if update_config:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, SafeDumper)
