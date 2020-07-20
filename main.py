import wordcloud, sys, discord, datetime, asyncio
import concurrent.futures
from discord.ext.commands import Bot
from yaml import load, YAMLError
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

class UserError(Exception):
    def __init__(self, message="Invalid Input"):
        self.message = message

PREFIX = "."

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

# Adding a few words to the wordcloud stopwords (boring words)
wordcloud.STOPWORDS.add("whatdidimiss")
wordcloud.STOPWORDS.add("wordcloud")

bot = Bot(command_prefix=PREFIX)

@bot.command(
    name = "whatdidimiss",
    aliases = ("wordcloud", "wc"),
    description = "Generates a word cloud of messages in the given time period.",
    usage = "Time: {num}{d, m, or y} (Default: 6h), This Channel Only: {True/False} (Default: True)",
    enabled = CONFIG["commands"]["whatdidimiss"]["enabled"]
)
async def whatdidimiss(ctx, in_time = CONFIG["commands"]["whatdidimiss"]["defaulttime"], in_one_channel = "True"):
    try:
        # Checking for appropriate permissions
        # Only check if the bot type is a member of a server
        if not check_perms(ctx, discord.Permissions(
            read_message_history = True,
            attach_files = True,
            send_messages = True
        )):
            raise UserError("`read_message_history`, `attach_files`, and `send_messages` permissions required.")
        
        minutes = parse_time_to_minutes(in_time)
        if  minutes > parse_time_to_minutes(CONFIG["commands"]["whatdidimiss"]["maxtime"]) or minutes < 1:
            raise UserError("Time outside of allowed range")
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

@bot.command(
    name = "stop",
    description = "Shuts down the bot",
    hidden = True,
    enabled = CONFIG["commands"]["stop"]["enabled"]
)
async def stop_program(ctx):
    if ctx.message.author.id in CONFIG["admins"]:
        await bot.logout()
    else:
        await ctx.send("You can't tell me what to do")

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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))

@bot.event
async def on_guild_join(guild):
    if guild.system_channel:
        await guild.system_channel.send("Hi! Use .help to see a list of commands")

if CONFIG["key"]:
    bot.run(CONFIG["key"])
else:
    print("Please set a private token")
    sys.exit(0)
