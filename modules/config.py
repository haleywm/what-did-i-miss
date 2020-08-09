import sys
from .utils import merge_dicts
from yaml import load, YAMLError
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
# Loading config data, catching errors in a user friendly way
try:
    try:
        CONFIG = load(open("default_config.yml"), Loader=Loader)
    except (FileNotFoundError, YAMLError):
        print("The default_config.yml file has been moved or deleted. Please don't touch it.")
        sys.exit(1)
    merge_dicts(CONFIG, load(open("config.yml"), Loader=Loader))
except FileNotFoundError:
    print("Please create a config.yml file containing the discord bot private key.")
    sys.exit(1)
except YAMLError:
    print("Please create a valid config.yml as per the example file, or the README")
    sys.exit(1)

with open("stopwords.txt") as stoplist:
    CONFIG["commands"]["whatdidimiss"]["stopwords"] = [line[:-1] for line in stoplist.readlines()]

# This method is how other modules will interact with this and get the config dict
def get_config():
    r"""Returns the config dictionary.
    Dictionary is built by parsing default_config.yml
    And then overwriting with values defined in config.yml
    """
    return CONFIG