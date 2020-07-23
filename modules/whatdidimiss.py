import discord.ext.commands as commands
from . import utils, config, wordcloud
from .utils import UserError
import concurrent.futures, asyncio, datetime
import discord

class whatdidimiss(commands.Cog, name="Wordclouds"):
    r"""Class for defining a word cloud generator command for Discord.py
    Does not take input apart from what is defined by the spec for adding cogs.
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command(
        name = "whatdidimiss",
        aliases = ("wordcloud", "wc"),
        description = "Generates a word cloud of messages in the given time period.",
        usage = r"""<Time> <This Channel Only> <Case Insensitive>
    Time: {num}{d, h, m, s} (Default: 6h)
    This Channel Only: {True/False} (Default: True)
    Case Insensitive: {True/False} (Default: True)

Examples:
    .wc
        (Generates a wordcloud for the last 6 hours, in this channel only, case insensitive)
    .whatdidimiss 45m False False
        (Generates a wordcloud for the last 45 minutes, in every channel on the server, case sensitive)
        """,
        enabled = config.get_config()["commands"]["whatdidimiss"]["enabled"]
    )
    async def whatdidimiss(self, ctx,
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
                    await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words, "wordcloud.png")
                await ctx.send(file=discord.File(open("wordcloud.png", "rb")))
            cooldown_list[cooldown_id] = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=utils.parse_time_to_seconds(config.get_config()["commands"]["whatdidimiss"]["cooldown"])
            )
        except UserError as e:
            await ctx.send(f"Invalid Input: {e.message}")

def create_wordcloud(words, filename):
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
        font_path = config.get_config()["commands"]["whatdidimiss"]["fontpath"],
        tint_emoji = config.get_config()["commands"]["whatdidimiss"]["tint"],
        emoji_cache_path = config.get_config()["commands"]["whatdidimiss"]["cache"],
        rotate_emoji = config.get_config()["commands"]["whatdidimiss"]["rotate"],
        font_size_mod = config.get_config()["commands"]["whatdidimiss"]["limit"]
    )
    if words:
        wc.generate_from_frequencies(words, False).to_file(filename)
    else:
        raise UserError("No words for wordcloud")

cooldown_list = dict()