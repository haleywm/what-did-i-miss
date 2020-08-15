from services import utils, wordcloud, cooldown
from services.utils import UserError
import discord.ext.commands as commands
import concurrent.futures, asyncio, datetime
import discord
from io import BytesIO

# Whatdidimiss-specific config
from services.config import ENABLED, DEFAULT_TIME, MAX_TIME, STOPWORDS, MAX_LOOKBACK_TIME, COOLDOWN

# Wordcloud-specific config
from services.config import SCALE, WIDTH, HEIGHT, BACKGROUND_COLOUR, OUTLINE_THICKNESS, \
    OUTLINE_COLOUR, FONT_PATH, TINT, CACHE, ROTATE, LIMIT

class Whatdidimiss(commands.Cog, name="Wordclouds"):
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
        enabled = ENABLED
    )
    async def wordcloud(self, ctx,
        in_time = DEFAULT_TIME,
        one_channel = "True",
        case_insensitive = "True"
        ):
        try:
            # Checking cooldown:
            if cooldown.cooldown_in_effect(ctx):
                raise UserError("Please wait for cooldown.")
            cooldown.add_cooldown(ctx, COOLDOWN)
            
            # Checking for appropriate permissions
            check_cmd_perms(ctx)

            seconds = utils.parse_time_to_seconds(in_time)
            if  seconds > utils.parse_time_to_seconds(MAX_TIME) or seconds < 1:
                raise UserError("Time outside of allowed range")

            one_channel = utils.parse_bool(one_channel)
            case_insensitive = utils.parse_bool(case_insensitive)
            # Getting the earliest time that should be used
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(seconds=seconds)

            # And now for the slow stuff
            with ctx.typing():
                # Next, recursively grabbing messages and appending them to a long ass string
                words = await utils.collect_messages(ctx, one_channel, timestamp, STOPWORDS, case_insensitive)
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    image = await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words)
                    await ctx.send(f"Messages over: {in_time}", file=discord.File(fp=image, filename="wordcloud.png"))
        except UserError as e:
            await ctx.send(f"Invalid Input: {e.message}")
            # Removing the cooldown as an act of mercy
            if e.no_cooldown:
                cooldown.remove_cooldown(ctx)

    @commands.command(
        name = "whatdidimiss",
        aliases = ["wdim"],
        description = "Generates a wordcloud of messages posted in the channelsince the last message from the user"
    )
    async def whatdidimiss(self, ctx):
        try:
            # Checking cooldown:
            if cooldown.cooldown_in_effect(ctx):
                raise UserError("Please wait for cooldown.")
            cooldown.add_cooldown(ctx, COOLDOWN)
            
            # Checking for appropriate permissions
            check_cmd_perms(ctx)

            timestamp = datetime.datetime.utcnow() - datetime.timedelta(
                seconds = utils.parse_time_to_seconds(MAX_LOOKBACK_TIME)
            )

            with ctx.typing():
                (words, msg_time) = await utils.collect_messages(ctx, True, timestamp, STOPWORDS, True, True)
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    image = await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words)
                if msg_time.total_seconds() == 0:
                    time_diff = f'Hit max time of {MAX_LOOKBACK_TIME}'
                else:
                    time_diff = utils.parse_seconds_to_time(int(msg_time.total_seconds()))
                await ctx.send(f"Here are the messages since your last post: ({time_diff})", file=discord.File(fp=image, filename="wordcloud.png"))
            cooldown.add_cooldown(ctx, COOLDOWN)
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
        scale = SCALE,
        width = WIDTH,
        height = HEIGHT,
        background_color = BACKGROUND_COLOUR,
        mode = "RGBA",
        outline_thickness = OUTLINE_THICKNESS,
        outline_color = OUTLINE_COLOUR,
        font_path = FONT_PATH,
        tint_emoji = TINT,
        emoji_cache_path = CACHE,
        rotate_emoji = ROTATE,
        font_size_mod = LIMIT
    )
    file = BytesIO()
    if words:
        wc.generate_from_frequencies(words, False).to_image().save(file, 'png')
        file.seek(0)
    else:
        raise UserError("No words for wordcloud", True)
    return file

def check_cmd_perms(ctx):
    # Checking for appropriate permissions
    # Only check if the bot type is a member of a server
    if not utils.check_perms(ctx, discord.Permissions(
        read_message_history = True,
        attach_files = True,
        send_messages = True
    )):
        raise UserError("`read_message_history`, `attach_files`, and `send_messages` permissions required.", True)