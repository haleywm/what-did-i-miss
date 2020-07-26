import discord.ext.commands as commands
from . import utils, config, wordcloud
from .utils import UserError
import concurrent.futures, asyncio, datetime
import discord
from io import BytesIO

class whatdidimiss(commands.Cog, name="Wordclouds"):
    r"""Class for defining a word cloud generator command for Discord.py
    Does not take input apart from what is defined by the spec for adding cogs.
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command(
        name = "wordcloud",
        aliases = ["wc"],
        description = "Generates a word cloud of messages in the given time period.",
        usage = r"""<Time> <This Channel Only> <Case Insensitive>
    Time: {num}{d, h, m, s} (Default: 6h)
    This Channel Only: {True/False} (Default: True)
    Case Insensitive: {True/False} (Default: True)

Examples:
    .wc
        (Generates a wordcloud for the last 6 hours, in this channel only, case insensitive)
    .wordcloud 45m False False
        (Generates a wordcloud for the last 45 minutes, in every channel on the server, case sensitive)
        """,
        enabled = config.get_config()["commands"]["whatdidimiss"]["enabled"]
    )
    async def wordcloud(self, ctx,
        in_time = config.get_config()["commands"]["whatdidimiss"]["defaulttime"],
        one_channel = "True",
        case_insensitive = "True"
        ):
        try:
            # Checking for appropriate permissions
            # Only check if the bot type is a member of a server
            if not utils.check_perms(ctx, discord.Permissions(
                read_message_history = True,
                attach_files = True,
                send_messages = True
            )):
                raise UserError("`read_message_history`, `attach_files`, and `send_messages` permissions required.")
            # Checking cooldown:
            cooldown_id = str(ctx.message.author.id) + ":" + str(ctx.message.channel.id)
            if cooldown_id in cooldown_list and cooldown_list[cooldown_id] > datetime.datetime.utcnow():
                raise UserError("Please wait for cooldown.")
            seconds = utils.parse_time_to_seconds(in_time)
            if  seconds > utils.parse_time_to_seconds(config.get_config()["commands"]["whatdidimiss"]["maxtime"]) or seconds < 1:
                raise UserError("Time outside of allowed range")

            one_channel = utils.parse_bool(one_channel)
            case_insensitive = utils.parse_bool(case_insensitive)
            # Getting the earliest time that should be used
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(seconds=seconds)

            # And now for the slow stuff
            with ctx.typing():
                # Next, recursively grabbing messages and appending them to a long ass string
                words = await utils.collect_messages(ctx, one_channel, timestamp,
                    config.get_config()["commands"]["whatdidimiss"]["stopwords"],
                    case_insensitive
                )
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    image = await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words)
                    await ctx.send(file=discord.File(fp=image, filename="wordcloud.png"))
            cooldown_list[cooldown_id] = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=utils.parse_time_to_seconds(config.get_config()["commands"]["whatdidimiss"]["cooldown"])
            )
        except UserError as e:
            await ctx.send(f"Invalid Input: {e.message}")

    @commands.command(
        name = "whatdidimiss",
        description = "Generates a wordcloud of messages posted in the channelsince the last message from the user"
    )
    async def whatdidimiss(self, ctx):
        try:
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(
                seconds = utils.parse_time_to_seconds(config.get_config()["commands"]["whatdidimiss"]["max-lookback-time"])
            )

            with ctx.typing():
                words = await utils.collect_messages(ctx, True, timestamp,
                    config.get_config()["commands"]["whatdidimiss"]["stopwords"],
                    True, True
                )
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    image = await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words)
                    await ctx.send("Here are the messages since your last post:")
                    await ctx.send(file=discord.File(fp=image, filename="wordcloud.png"))
        except UserError as e:
            await ctx.send(f"Invalid input: {e.message}")

def create_wordcloud(words):
    r"""Creates a wordcloud given a frequency dictionary, saves it to filename.
    Parameters
    ----------
    words : dict
        A dictionary of words to be used in the cloud.
        Every string should have an integer value representing it's frequency.
        Passes data, and config, to WordCloud.WordCloud().generate_from_frequencies()
        for generation.
    """
    wc = wordcloud.WordCloud(
        scale = config.get_config()["commands"]["whatdidimiss"]["scale"],
        width = config.get_config()["commands"]["whatdidimiss"]["width"],
        height = config.get_config()["commands"]["whatdidimiss"]["height"],
        background_color = config.get_config()["commands"]["whatdidimiss"]["background-colour"],
        mode = "RGBA",
        outline_thickness = config.get_config()["commands"]["whatdidimiss"]["outline-thickness"],
        outline_color = config.get_config()["commands"]["whatdidimiss"]["outline-colour"],
        font_path = config.get_config()["commands"]["whatdidimiss"]["fontpath"],
        tint_emoji = config.get_config()["commands"]["whatdidimiss"]["tint"],
        emoji_cache_path = config.get_config()["commands"]["whatdidimiss"]["cache"],
        rotate_emoji = config.get_config()["commands"]["whatdidimiss"]["rotate"],
        font_size_mod = config.get_config()["commands"]["whatdidimiss"]["limit"]
    )
    file = BytesIO()
    if words:
        wc.generate_from_frequencies(words, False).to_image().save(file, 'png')
        file.seek(0)
    else:
        raise UserError("No words for wordcloud")
    return file

cooldown_list = dict()