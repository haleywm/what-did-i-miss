import PIL, wordcloud, sys, discord, datetime, asyncio
import concurrent.futures
from discord.ext.commands import Bot

class UserError(Exception):
    def __init__(self, message="Invalid Input"):
        self.message = message

PREFIX = "."
try:
    with open("key.txt") as key_file:
        KEY = key_file.readline()
except FileNotFoundError:
    print("Please create a key.txt file containing the discord bot private key.")
    sys.exit(-1)

wordcloud.STOPWORDS.add("wordcloud")

bot = Bot(command_prefix=PREFIX)

@bot.command(
    name = "whatdidimiss",
    description = "Generates a word cloud of messages in the given time period.",
    usage = "Time: {num}{d, m, or y} (Default: 6h), This Channel Only: {True/False} (Default: True)"
)

async def whatdidimiss(ctx, in_time = "6h", in_one_channel = "True"):
    try:
        minutes = parse_time_to_minutes(in_time)
        one_channel = parse_bool(in_one_channel)
        # Getting the earliest time that should be used
        timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)

        # And now for the slow stuff
        with ctx.typing():
            # Next, recursively grabbing messages and appending them to a long ass string
            words = await collect_messages(ctx, one_channel, timestamp)
            with concurrent.futures.ProcessPoolExecutor() as pool:
                await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words, "wordcloud.png")
            await ctx.send(file=discord.File(open("wordcloud.png", "rb")))
    except UserError as e:
        await ctx.send(f"Invalid Input: {e.message}")

def parse_time_to_minutes(raw_time):
    units = ("m", "h", "d")
    try:
        minutes = int(raw_time[:-1])
    except ValueError:
        raise UserError("Invalid time duration.")
    if minutes > 100000 or minutes < 0:
        raise UserError("Number outside of allowed range")
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
        histories = [i.history for i in list(filter(lambda i: type(i) is discord.TextChannel, ctx.guild.channels))]
    words = dict()
    for hist in histories:
        async for msg in hist(limit=None, after=timestamp):
            add_frequency(words, msg.content)
    return words

def create_wordcloud(words, filename):
    wc = wordcloud.WordCloud(
        collocations = False
    )
    wc.generate_from_frequencies(words).to_file(filename)

def add_frequency(freq_dict, text):
    # A dictionary of words, each word having an integer value of it's frequency
    # Adds the frequency to an existing set, pass an empty dict() to start with.
    for word in text.split():
        word = word.lower().strip('.,!?\'"')
        if word not in wordcloud.STOPWORDS:
            if word in freq_dict:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(KEY)
