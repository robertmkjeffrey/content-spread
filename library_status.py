import utils
import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
import os

from pprint import pprint

import matplotlib.pyplot as plt

SUBREDDIT_INDEX_FILE_NAME = "subreddit_index"

CONFIG_FILE = "config.yaml"
config = utils.load_config(CONFIG_FILE)
LIBRARY_DIRECTORY = config["library_directory"]
ARCHIVE_DIRECTORY = os.path.join(LIBRARY_DIRECTORY, "archive")

index_file = os.path.join(LIBRARY_DIRECTORY, SUBREDDIT_INDEX_FILE_NAME)

if os.path.exists(index_file):
    with open(index_file, "r") as f:
        subreddit_index = yaml.load(f, SafeLoader)
    plt.barh(*zip(*[(k, len(v)) for k,v in subreddit_index.items()]))
    
plt.show()