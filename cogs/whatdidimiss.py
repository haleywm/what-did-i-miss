from services import utils, wordcloud, cooldown
from services.utils import UserError
import discord.ext.commands as commands
import concurrent.futures, asyncio, datetime
import discord
from io import BytesIO
import secrets

from services.config import CONFIG


class Whatdidimiss(commands.Cog, name="Wordclouds"):
    r"""Class for defining a word cloud generator command for Discord.py
    Does not take input apart from what is defined by the spec for adding cogs.
    """
    
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
        enabled = CONFIG["commands"]["whatdidimiss"]["enabled"]
    )
    @commands.guild_only()
    async def wordcloud(self, ctx,
        in_time = CONFIG["commands"]["whatdidimiss"]["defaulttime"],
        one_channel: bool = True,
        case_insensitive: bool = True
    ):
        await self.find_wordcloud(ctx, in_time, one_channel, case_insensitive)

    @commands.command(
        name = "whatdidimiss",
        aliases = ["wdim"],
        description = "Generates a wordcloud of messages posted in the channelsince the last message from the user"
    )
    @commands.guild_only()
    async def whatdidimiss(self, ctx):
        await self.find_wordcloud(
            ctx, CONFIG["commands"]["whatdidimiss"]["max-lookback-time"], stop_after_usermsg=True
        )

    async def find_wordcloud(self, ctx, in_time, one_channel=True, case_insensitive=True, stop_after_usermsg=False):
        try:
            await self.check_cooldown(ctx)
            
            if not utils.check_perms(ctx, discord.Permissions(
                read_message_history = True,
                attach_files = True,
                send_messages = True
            )):
                raise UserError("`read_message_history`, `attach_files`, and `send_messages` permissions required.", True)

            seconds = utils.parse_time_to_seconds(in_time)
            if  seconds > utils.parse_time_to_seconds(CONFIG["commands"]["whatdidimiss"]["maxtime"]) or seconds < 1:
                raise UserError(f'Thats too much time! {CONFIG["commands"]["whatdidimiss"]["maxtime"]} Maximum!', True)
            
            # Getting the earliest time that should be used
            timestamp = ctx.message.created_at - datetime.timedelta(seconds=seconds)

            # And now for the slow stuff
            with ctx.typing():
                # Next, recursively grabbing messages and appending them to a long ass string
                result = await utils.collect_messages(
                    ctx, one_channel, timestamp, CONFIG["commands"]["whatdidimiss"]["stopwords"], case_insensitive, stop_after_usermsg
                )
                # Depending on if stop_after_usermsg is set, it'll either just return the frequency dict, or a tuple with more information
                words = result[0]
                msg_count = result[1]
                if stop_after_usermsg:
                    if result[2].total_seconds() == 0:
                        time_diff = f'Hit max time of {CONFIG["commands"]["whatdidimiss"]["max-lookback-time"]}'
                    else:
                        time_diff = utils.parse_seconds_to_time(int(result[2].total_seconds()))
                
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    image = await asyncio.get_event_loop().run_in_executor(pool, create_wordcloud, words)
                    if stop_after_usermsg:
                        await ctx.send(f"Heres what happened since your last post {time_diff} ago ({msg_count} messages)", file=discord.File(fp=image, filename="wordcloud.png"))
                    else:
                        await ctx.send(f"Heres what happened in the past {utils.prettify_time(in_time)} ({msg_count} messages)", file=discord.File(fp=image, filename="wordcloud.png"))
        except UserError as e:
            await ctx.send(f":warning:  {e.message}")
            # Removing the cooldown as an act of mercy
            if e.no_cooldown:
                cooldown.remove_cooldown(ctx)

    async def check_cooldown(self, ctx):
        c, t = cooldown.cooldown_in_effect(ctx)
        if c:
            t = utils.parse_seconds_to_time(t)
            raise UserError(f"Relax. Your cooldown expires in {t}!")
        cooldown.add_cooldown(ctx, CONFIG["commands"]["whatdidimiss"]["cooldown"])


# I would put this inside the object but causes issues with how making pools works
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

    cfg = CONFIG["commands"]["whatdidimiss"]

    wc = wordcloud.WordCloud(
        scale = cfg["scale"],
        width = cfg["width"],
        height = cfg["height"],
        background_color = cfg["background-colour"],
        mode = "RGBA",
        outline_thickness = cfg["outline-thickness"],
        font_path = cfg["fontpath"],
        tint_emoji = cfg["tint"],
        emoji_cache_path = cfg["cache"],
        rotate_emoji = cfg["rotate"],
        font_size_mod = cfg["limit"],
        colormap = secrets.choice(cfg["colormaps"]),
        randomize_hue = cfg["randomize-hue"]
    )
    file = BytesIO()
    if words:
        wc.generate_from_frequencies(words, False).to_image().save(file, 'png')
        file.seek(0)
    else:
        raise UserError("I need words for a wordcloud!", True)
    return file