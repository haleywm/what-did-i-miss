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
        usage = "Time: {num}{d, h, m, s} (Default: 6h), This Channel Only: {True/False} (Default: True)",
        enabled = config.get_config()["commands"]["whatdidimiss"]["enabled"]
    )
    async def whatdidimiss(self, ctx, in_time = config.get_config()["commands"]["whatdidimiss"]["defaulttime"], in_one_channel = "True"):
        r"""Discord Command for generating word clouds from message history in a server.
        Parameters
        ----------
        ctx : discord.ext.commands.Context
            Provided by Discord.py, is the context within which the command was given.
        
        in_time : string, default=config.get_config()["commands"]["whatdidimiss"]["defaulttime"]
            The amount of time to be evaluated by the bot. Takes a form such as "6h".
            Should be in form: \d+[smhd], an integer followed by a unit, either s, m, h, or d.
            Has a maximum value: config.get_config()["commands"]["whatdidimiss"]["maxtime"]
            Has a per user, per channel cooldown defined by:
                config.get_config()["commands"]["whatdidimiss"]["cooldown"]
        """
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
            one_channel = utils.parse_bool(in_one_channel)
            # Getting the earliest time that should be used
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(seconds=seconds)

            # And now for the slow stuff
            with ctx.typing():
                # Next, recursively grabbing messages and appending them to a long ass string
                words = await utils.collect_messages(ctx, one_channel, timestamp, config.get_config()["commands"]["whatdidimiss"]["stopwords"])
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