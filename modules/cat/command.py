import discord

from main import bot, PREFIX
from discord.ext import commands
from .api_service import get_cat_image


class Cat(commands.Cog):

    """
    MAIN COMMAND
    """
    @bot.group(invoke_without_command=True)
    async def cat(self, ctx):
        async with ctx.typing():
            cat = await get_cat_image()

            await ctx.send(file=cat)

    """ 
    SUB-COMMANDS
    """
    @cat.command()
    async def gif(self, ctx):
        async with ctx.typing():
            cat = await get_cat_image(gif=True)

            await ctx.send(file=cat)

    @cat.command()
    async def help(self, ctx):
        async with ctx.typing():
            usage_text = f"Usage: {PREFIX}cat [gif]"
            help_text = "Display a random cat image or gif"
            embed = discord.Embed(title=self.qualified_name, description=f"{usage_text}\n\n{help_text}")

            await ctx.send(embed=embed)
