import discord
import wordcloud

class UserError(Exception):
    def __init__(self, message="Invalid Input"):
        self.message = message

def parse_time_to_minutes(raw_time):
    units = ("m", "h", "d")
    try:
        minutes = int(raw_time[:-1])
    except ValueError:
        raise UserError("Invalid time duration.")
    unit = raw_time[-1].lower()
    if not unit in units:
        raise UserError("Invalid time unit")
    if unit == "d":
        minutes *= 1440
    elif unit == "h":
        minutes *= 60
    return minutes

def parse_bool(in_bool):
    falseValues = ("false", "0", "no")
    return in_bool.lower() not in falseValues

async def collect_messages(ctx, one_channel, timestamp):
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
                add_frequency(words, msg.content)
    return words

def create_wordcloud(words, filename):
    wc = wordcloud.WordCloud(
        collocations = False
    )
    if words:
        wc.generate_from_frequencies(words).to_file(filename)
    else:
        raise UserError("No words for wordcloud")

def add_frequency(freq_dict, text):
    MAXLEN = 30
    # A dictionary of words, each word having an integer value of it's frequency
    # Adds the frequency to an existing set, pass an empty dict() to start with.
    for word in text.split():
        word = word.lower().strip('.,!?\'"`')
        if word not in wordcloud.STOPWORDS and len(word) <= MAXLEN:
            if word in freq_dict:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1

def check_perms(ctx, perms):
    # Checks that all permissions are present in context's channel, if the channel is part of a guild (server)
    return type(ctx.me) is not discord.Member or ctx.channel.permissions_for(ctx.me).is_superset(perms)