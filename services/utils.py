import discord, re, datetime
from math import floor
from services.config import CONFIG

class UserError(Exception):
    def __init__(self, message="Invalid Input", no_cooldown=False):
        self.message = message
        # No cooldown, this usually doesn't matter but can be used to say that an error can be used to stop cooldown. Must be implemented when relevant.
        self.no_cooldown = no_cooldown

# The regex used to recognize if a word is an external emoji
parseEmojis = re.compile(r"(<:[\w]+:\d+>)")


def parse_time_to_seconds(raw_time):
    r"""Parses a time string to seconds. Takes a form such as "6h".
    Returns an integer representing the total time in seconds.
    Parameters
    ----------
    raw_time : string
    Should be in form: \d+[smhd], an integer followed by a unit, either s, m, h, or d.
    """
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

def parse_seconds_to_time(raw_seconds, show_seconds=False):
    r"""Parses a integer into a huaman readable string of days, hours, minutes, and optionally seconds.
    If the time given is less than a minute then seconds shown anyway.
    Returns a string.
    Parameters
    ----------
    raw_seconds : integer
        The seconds to parse
    show_seconds : bool, default=False
        If seconds should be displayed
    """
    output = ""
    time_added = False
    if raw_seconds < 0:
        output += "-"
        raw_seconds *= -1
    elif raw_seconds < 1:
        return "No time"
    
    if raw_seconds > 86400:
        time_added = True
        unit = floor(raw_seconds / 86400)
        output += str(unit) + " day"
        if unit > 1:
            output += "s, "
        else:
            output += ", "
        raw_seconds %= 86400
    if raw_seconds > 3600:
        time_added = True
        unit = floor(raw_seconds / 3600)
        output += str(unit) + " hour"
        if unit > 1:
            output += "s, "
        else:
            output += ", "
        raw_seconds %= 3600
    if raw_seconds > 60:
        time_added = True
        unit = floor(raw_seconds / 60)
        output += str(unit) + " minute"
        if unit > 1:
            output += "s, "
        else:
            output += ", "
        raw_seconds %= 60
    if show_seconds or not time_added:
        unit = round(raw_seconds)
        output += str(unit) + " second"
        if unit > 1:
            output += "s, "
        else:
            output += ", "
    return output[:-2]

def parse_bool(in_bool):
    r"""Parses a string to decide if it is true or false.
    Defaults to true unless input matches "false", "0", "no".
    Case insensitive.
    Parameters
    ----------
    in_bool : string
        The string to be parsed to see if it is true or false.
    """
    falseValues = ("false", "0", "no")
    return in_bool.lower() not in falseValues

async def collect_messages(
    ctx, one_channel, timestamp, stopwords, case_insensitive = True, until_last_user_msg = False
):
    """Collects messages from a discord server from within a time period.
    Returns a frequency dictionary with its findings.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context that the command is being run from.
        Is used to get the current channel, and server if necessary.
    one_channel : bool
        Determines if only a single channels history should be grabbed,
        or every channel in the server that the bot can access.
    timestamp : datetime.datetime
        The datetime that the bot should look forward from
    stopwords : list[string] or set[string]
        A list of words that should be left out of the word count if matched.
    case_insensitive : bool, default=True
        If the messages should be case sensitive or not.
    until_last_user_msg : bool, default=False
        If the message collection should end when the next message from the user is found
    """
    # Getting the channel's that should be grabbed from
    if one_channel or ctx.guild is None: # If the message isn't in a server just grab current channel
        histories = [ctx.history]
    else:
        histories = [i.history for i in list(filter(
            lambda i:type(i) is discord.TextChannel and i.permissions_for(ctx.me).read_messages,
            ctx.guild.channels))]
    words = dict()
    time_now = datetime.datetime.utcnow()
    # Default time_back of 0
    # This will be set to a larger value only if until_last_user_msg is True
    time_back = datetime.timedelta()
    for hist in histories:
        async for msg in hist(limit=None, after=timestamp, oldest_first=False):
            if msg.author is not ctx.me:
                # Since I can't tell when the last message will be this is calculator for every
                # message. Efficient.
                # If only looking until the users last message, stop looking if they're the author
                if(
                    until_last_user_msg and
                    msg.author == ctx.message.author and
                    msg.created_at < time_now - datetime.timedelta(
                        seconds = parse_time_to_seconds(CONFIG["commands"]["whatdidimiss"]["ignore-msg-time"])
                    )
                ):
                    time_back = time_now - msg.created_at
                    break
                else:
                    # clean_content parses @'s and #'s to be readable names, while content doesn't.
                    add_frequency(words, msg.clean_content, stopwords, case_insensitive)
    if until_last_user_msg:
        return (words, time_back)
    else:
        return words

def add_frequency(freq_dict, text, stopwords, case_insensitive):
    r"""Adds the frequency of words inside the given string to a dict.
    Strips characters at the start and end as defined by
        config.STRIP
    Ignores words longer than 20 characters unless they're of the emoji format.
    Parameters
    ----------
    freq_dict : dict
        The dictionary that these values should be added to.
    test : string
        The string that should be parsed
    stopwords : list[string] or set[string]
        A list of words that should be left out of the word count if matched.
    case_insensitive : bool
        If the frequency should be case sensitive or not
    """
    MAXLEN = 20
    # A dictionary of words, each word having an integer value of it's frequency
    # Adds the frequency to an existing set, pass an empty dict() to start with.
    if not text.startswith("."):
        for word in text.split():
            if case_insensitive:
                word = word.lower()
            word = word.strip(CONFIG["commands"]["whatdidimiss"]["strip"])
            # Testing if the word is emojis
            emojis = parseEmojis.findall(word)
            if len(emojis) > 0:
                for emoji in emojis:
                    add_dict(freq_dict, emoji)
            elif word not in stopwords and len(word) <= MAXLEN:
                add_dict(freq_dict, word)

def add_dict(freq_dict, word):
    """Adds to a frequency dictionary
    Used by add_frequency, but add_frequency has all the logic to only add good words
    """
    if word in freq_dict:
        freq_dict[word] += 1
    else:
        freq_dict[word] = 1

def check_perms(ctx, perms):
    """Checks if the discord bot has all the required permissions in the given channel.
    Returns true if the bot has all permissions required,
    or if the context takes place within DM's where permissions don't apply.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context that the command is being run in.
        Used to get the channel, and check if the command is being run in a server.
    perms : discord.Permissions
        The set of permissions that the bot requires.
        Only values explicitly defined are checked.
    """
    # Checks that all permissions are present in context's channel, if the channel is part of a guild (server)
    return type(ctx.me) is not discord.Member or ctx.channel.permissions_for(ctx.me).is_superset(perms)
