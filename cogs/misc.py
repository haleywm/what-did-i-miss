import discord

from main import bot
from discord.ext import commands
from services.cat.api import get_cat_image
from services.config import CONFIG
from services.hug.utils import remove_invocation, find_user, InvalidUserException
from services.imgur.imgur import get_image_from_album


# TODO Implement error handling for cat commands
class Wholesome(commands.Cog):
    """
        A collection of wholesome commands intended to spread happy feelings
    """

    @bot.group(
        invoke_without_command=True,
        enabled = CONFIG["commands"]["cat"]["enabled"]
    )
    async def cat(self, ctx):
        """
            Post a random image or gif of a cat from https://cataas.com
        """
        async with ctx.typing():
            cat = await get_cat_image()

        await ctx.send(file=cat)

    @cat.command(
        enabled = CONFIG["commands"]["cat"]["enabled"]
    )
    async def gif(self, ctx):
        """
            Post a random gif of a cat from https://cataas.com
        """
        async with ctx.typing():
            cat = await get_cat_image(gif=True)

        await ctx.send(file=cat)

    @commands.before_invoke(remove_invocation)
    @commands.command(
        enabled = CONFIG["commands"]["hug"]["enabled"],
        aliases = ["stab"]
    )
    async def hug(self, ctx, target):
        """
            Send a virtual hug to someone
        """
        try:
            user = await find_user(ctx.guild, target)
            if user:
                await ctx.send(f"Psst {user.name}! {ctx.message.author.name} sent you a virtual hug! :heart:")
            else:
                await ctx.author.send("Sorry, I couldn't find anyone with that name to hug :(")
        except InvalidUserException:
            await ctx.send(f'User not found. Check that the user is valid.```{ctx.message.content}```')
        except Exception as e:
            raise e
    
    @commands.command(
        enabled = CONFIG["commands"]["gator"]["enabled"],
        aliases = ["alligator"]
    )
    async def gator(self, ctx):
        "Post a gator pick, from an album provided by Gator#3220"
        url = await get_image_from_album("cwnBW9Q")
        await ctx.send(url)
