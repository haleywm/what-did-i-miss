import discord.ext.commands as commands
from . import utils, config
from .utils import UserError
import concurrent.futures, asyncio, datetime, wordcloud
import discord

# Adding a few words to the wordcloud stopwords (boring words)
wordcloud.STOPWORDS.add("whatdidimiss")
wordcloud.STOPWORDS.add("wordcloud")

class whatdidimiss(commands.Cog, name="Wordclouds", command_attrs=dict(
    name = "whatdidimiss",
    aliases = ("wordcloud", "wc"),
    description = "Generates a word cloud of messages in the given time period.",
    usage = "Time: {num}{d, m, or y} (Default: 6h), This Channel Only: {True/False} (Default: True)",
    enabled = config.get_config()["commands"]["whatdidimiss"]["enabled"]
)):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
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
            
            minutes = utils.parse_time_to_minutes(in_time)
            if  minutes > utils.parse_time_to_minutes(config.get_config()["commands"]["whatdidimiss"]["maxtime"]) or minutes < 1:
                raise UserError("Time outside of allowed range")
            one_channel = utils.parse_bool(in_one_channel)
            # Getting the earliest time that should be used
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)

            # And now for the slow stuff
            with ctx.typing():
                # Next, recursively grabbing messages and appending them to a long ass string
                words = await utils.collect_messages(ctx, one_channel, timestamp)
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    await asyncio.get_event_loop().run_in_executor(pool, utils.create_wordcloud, words, "wordcloud.png")
                await ctx.send(file=discord.File(open("wordcloud.png", "rb")))
        except UserError as e:
            await ctx.send(f"Invalid Input: {e.message}")