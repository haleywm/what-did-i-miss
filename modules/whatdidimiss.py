import discord.ext.commands as commands
from . import utils, config, wordcloud
from .utils import UserError
import concurrent.futures, asyncio, datetime
import discord

class whatdidimiss(commands.Cog, name="Wordclouds"):
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
    wc = wordcloud.WordCloud(
        scale = config.get_config()["commands"]["whatdidimiss"]["scale"],
        width = config.get_config()["commands"]["whatdidimiss"]["width"],
        height = config.get_config()["commands"]["whatdidimiss"]["height"],
        font_path = config.get_config()["commands"]["whatdidimiss"]["fontpath"]
    )
    wc.tint_emoji = config.get_config()["commands"]["whatdidimiss"]["tint"]
    wc.emoji_cache_path = config.get_config()["commands"]["whatdidimiss"]["cache"]
    wc.rotate_emoji = config.get_config()["commands"]["whatdidimiss"]["rotate"]
    if words:
        wc.generate_from_frequencies(words).to_file(filename)
    else:
        raise UserError("No words for wordcloud")

cooldown_list = dict()