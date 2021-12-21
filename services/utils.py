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
        raise UserError("Invalid time duration.", True)
    unit = raw_time[-1].lower()
    if not unit in units:
        raise UserError("Invalid time unit", True)
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
    units = [(86400, "day", True), (3600, "hour", True), (60, "minute", True), (1, "second", show_seconds)]
    output = ""
    time_added = False
    if raw_seconds < 0:
        output += "-"
        raw_seconds *= -1
    elif raw_seconds < 1:
        return "No time"
    
    for unit in units:
        # Units with a [2] value of false won't be shown unless no time has been added by other values yet
        if raw_seconds > unit[0] and (unit[2] or not time_added):
            # Setting 
            time_added = True
            amount = floor(raw_seconds / unit[0])
            output += str(amount) + " " + unit[1]
            if amount > 1:
                output += "s, "
            else:
                output += ", "
            raw_seconds %= unit[0]
    return output[:-2]

def prettify_time(raw_time):
    "Converts a time to a full string by first converting it to seconds, and then to human readable time"
    return parse_seconds_to_time(parse_time_to_seconds(raw_time))

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
    msg_amount = 0
    time_now = datetime.datetime.now(datetime.timezone.utc)
    # Default time_back of 0
    # This will be set to a larger value only if until_last_user_msg is True
    time_back = datetime.timedelta()
    for hist in histories:
        async for msg in hist(limit=None, after=timestamp, oldest_first=False):
            if msg.author is not ctx.me and not msg.content.startswith("."):
                # Since I can't tell when the last message will be this is calculator for every
                # message. Efficient.
                # If only looking until the users last message, stop looking if they're the author
                if(
                    until_last_user_msg and
                    msg.author == ctx.author and
                    msg.created_at < time_now - datetime.timedelta(
                        seconds = parse_time_to_seconds(CONFIG["commands"]["whatdidimiss"]["ignore-msg-time"])
                    )
                ):
                    time_back = time_now - msg.created_at
                    break
                else:
                    # clean_content parses @'s and #'s to be readable names, while content doesn't.
                    add_frequency(words, msg.clean_content, stopwords, case_insensitive)
                    msg_amount += 1
                    
    if until_last_user_msg:
        return (words, msg_amount, time_back)
    else:
        return (words, msg_amount)

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

def check_perms(ctx, perms, user = None):
    """Checks if a user has all the required permissions in the given channel.
    Returns true if the user has all permissions required,
    or if the context takes place within DM's where permissions don't apply.
    The default user is the bot.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context that the command is being run in.
        Used to get the channel, and check if the command is being run in a server.
    perms : discord.Permissions
        The set of permissions that the bot requires.
        Only values explicitly defined are checked.
    user : discord.Member, discord.ClientUser
        The user for which to evaluate permissions. If user is a client user, then this implies context is in DM's, and command will return true
    """
    if not user:
        user = ctx.me
    # Checks that all permissions are present in context's channel, if the given user
    return (not isinstance(user, discord.Member)) or ctx.channel.permissions_for(user).is_superset(perms)