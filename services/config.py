import sys
from yaml import load, YAMLError


def __merge_dicts(dict_one, dict_two):
    """Merges two dicts
    Recursively merges sub-dicts, rather than overwriting them at the top level as update() does.
    Parameters
    ----------
    dict_one : dict
        The dictionary for values to be merged into. This dictionary is written to.
    dict_two : dict
        The dictionary for values to be read from.
    """
    # Merges dict_two into dict_one, merging dicts and only overwriting values with the same name:
    for key, val in dict_two.items():
        if type(val) is dict and key in dict_one and type(dict_one[key]) is dict:
            __merge_dicts(dict_one[key], val)
        else:
            dict_one[key] = val


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
    __merge_dicts(CONFIG, load(open("config.yml"), Loader=Loader))
except FileNotFoundError:
    print("Please create a config.yml file containing the discord bot private key.")
    pass
except YAMLError:
    print("Please create a valid config.yml as per the example file, or the README")
    sys.exit(1)

with open("stopwords.txt") as stoplist:
    CONFIG["commands"]["whatdidimiss"]["stopwords"] = [line.strip() for line in stoplist.readlines()]

with open("colormaps.txt") as colormaps:
    CONFIG["commands"]["whatdidimiss"]["colormaps"] = [line.strip() for line in colormaps.readlines()]

# This method is how other modules will interact with this and get the config dict
def get_config():
    r"""Returns the config dictionary.
    Dictionary is built by parsing default_config.yml
    And then overwriting with values defined in config.yml
    """
    return CONFIG
