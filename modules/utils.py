import discord, re
from . import config

class UserError(Exception):
    def __init__(self, message="Invalid Input"):
        self.message = message

def parse_time_to_seconds(raw_time):
    units = ("d", "h", "m", "s")
    try:
        minutes = int(raw_time[:-1])
    except ValueError:
        raise UserError("Invalid time duration.")
    unit = raw_time[-1].lower()
    if not unit in units:
        raise UserError("Invalid time unit")
    if unit == "d":
        minutes *= 86400
    elif unit == "h":
        minutes *= 3600
    elif unit == "m":
        minutes *= 60
    return minutes

def parse_bool(in_bool):
    falseValues = ("false", "0", "no")
    return in_bool.lower() not in falseValues

async def collect_messages(ctx, one_channel, timestamp, stopwords):
    # Getting the channel's that should be grabbed from
    if one_channel or ctx.guild is None: # If the message isn't in a server just grab current channel
        histories = [ctx.history]
    else:
        histories = [i.history for i in list(filter(
            lambda i:type(i) is discord.TextChannel and i.permissions_for(ctx.me).read_messages,
            ctx.guild.channels))]
    words = dict()
    for hist in histories:
        async for msg in hist(limit=None, after=timestamp):
            if msg.author is not ctx.me:
                # clean_content parses @'s and #'s to be readable names, while content doesn't.
                add_frequency(words, msg.clean_content, stopwords)
    return words

def add_frequency(freq_dict, text, stopwords):
    MAXLEN = 30
    # A dictionary of words, each word having an integer value of it's frequency
    # Adds the frequency to an existing set, pass an empty dict() to start with.
    if not text.startswith("."):
        for word in text.split():
            word = word.lower().strip(config.get_config()["commands"]["whatdidimiss"]["strip"])
            if word not in stopwords and len(word) <= MAXLEN:
                if word in freq_dict:
                    freq_dict[word] += 1
                else:
                    freq_dict[word] = 1

def check_perms(ctx, perms):
    # Checks that all permissions are present in context's channel, if the channel is part of a guild (server)
    return type(ctx.me) is not discord.Member or ctx.channel.permissions_for(ctx.me).is_superset(perms)

def merge_dicts(dict_one, dict_two):
    # Merges dict_two into dict_one, merging dicts and only overwriting values with the same name:
    for key, val in dict_two.items():
        if type(val) is dict and key in dict_one and type(dict_one[key]) is dict:
            merge_dicts(dict_one[key], val)
        else:
            dict_one[key] = val
            
            