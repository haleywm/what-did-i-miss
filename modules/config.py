import sys
from yaml import load, YAMLError
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Loading config data, catching errors in a user friendly way
try:
    try:
        CONFIG = load(open("default_config.yml"), Loader=Loader)
    except FileNotFoundError:
        print("The default_config.yml file has been moved or deleted.")
        sys.exit(-1)
    CONFIG.update(load(open("config.yml"), Loader=Loader))
except FileNotFoundError:
    ## TEMP SETTING MIGRATE CODE, remove in future:
    # If a key.txt file exists, attempt to migrate it into a config file
    try:
        with open("key.txt") as file:
            with open("config.yml", "w") as output:
                output.write("key: " + file.readline())
                print("Migrated key to config.yml")
        try:
            CONFIG.update(load(open("config.yml"), Loader=Loader))
        except YAMLError:
            print("Attempted to generate config.yml from key.txt, encountered invalid output")
            sys.exit(-1)
    except FileNotFoundError:
        print("Please create a config.yml file containing the discord bot private key.")
        sys.exit(-1)
except YAMLError:
    print("Please create a valid config.yml as per the example file, or the README")
    sys.exit(-1)

# This method is how other modules will interact with this and get the config dict
def get_config():
    return CONFIG