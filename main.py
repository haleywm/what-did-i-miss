import PIL, wordcloud, sys, typing, discord, datetime
from discord.ext.commands import Bot

PREFIX = "."
try:
    with open("key.txt") as key_file:
        KEY = key_file.readline()
except FileNotFoundError:
    print("Please create a key.txt file containing the discord bot private key.")
    sys.exit(-1)

bot = Bot(command_prefix=PREFIX)

@bot.command(
    name = "whatdidimiss",
    description = "Generates a word cloud of messages in the given time period.",
    usage = "Time: {num}{d, m, or y} (Default: 6h), This Channel Only: {True/False} (Default: True)"
)

async def whatdidimiss(ctx, in_time: typing.Optional[str] = "6h", in_one_channel: typing.Optional[str] = "True"):
    minutes = 6
    unit = "h"
    units = ("m", "h", "d")
    falseValues = ("false", "0", "no")
    try:
        minutes = int(in_time[:-1])
        unit = in_time[-1].lower()
        if not unit in units:
            raise ValueError("Invalid unit")
    except ValueError:
        await ctx.send("That's not a valid time >:( assuming 6 hours")
    
    # Throwing away any more than the first 2 arguments, and moving on:
    if unit == "m":
        pass
    elif unit == "d":
        minutes *= 1440
    else:
        minutes *= 60
    # Default unit is hours

    one_channel = not in_one_channel.lower() in falseValues

    # Getting the earliest time that should be used
    timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)

    # And now for the slow stuff
    async with ctx.typing():
        # Getting the channel's that should be grabbed from
        if one_channel or ctx.guild is None: # If the message isn't in a server just grab current channel
            histories = [ctx.history]
        else:
            histories = [i.history for i in list(filter(lambda i: type(i) is discord.TextChannel, ctx.guild.channels))]
        
        # Next, recursively grabbing messages and appending them to a long ass string
        words = ""
        for hist in histories:
            words += (" ".join(await hist(limit=None, after=timestamp).map(lambda x: x.content).flatten())) + " "

        wc = wordcloud.WordCloud(
            collocations = False
        )
        wc.generate(words).to_file("wordcloud.png")

        await ctx.send(file=discord.File(open("wordcloud.png", "rb")))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(KEY)
