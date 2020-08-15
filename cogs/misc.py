from main import bot
from discord.ext import commands
from services.cat.api import get_cat_image
from services.hug.utils import remove_invocation, find_user, InvalidMentionException


# TODO Implement error handling for cat commands
class Wholesome(commands.Cog):
    """
        A collection of wholesome commands intended to spread happy feelings
    """

    @bot.group(invoke_without_command=True)
    async def cat(self, ctx):
        """
            Post a random image or gif of a cat from https://cataas.com
        """
        async with ctx.typing():
            cat = await get_cat_image()

        await ctx.send(file=cat)

    @cat.command()
    async def gif(self, ctx):
        """
            Post a random gif of a cat from https://cataas.com
        """
        async with ctx.typing():
            cat = await get_cat_image(gif=True)

        await ctx.send(file=cat)

    @commands.before_invoke(remove_invocation)
    @commands.command()
    async def hug(self, ctx, mention):
        """
            Send a secret virtual hug to someone
        """
        try:
            user = await find_user(ctx.guild, mention)
            await ctx.send(f"{user.mention} You've been sent a virtual hug! :heart:")
        except InvalidMentionException:
            await ctx.message.author.send('Invalid user mention. Check that the user is valid.'
                                          f'```{ctx.message.content}```')
        except Exception as e:
            print(e)
