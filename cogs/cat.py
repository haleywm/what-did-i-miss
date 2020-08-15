import discord

from main import bot, PREFIX
from discord.ext import commands
from services.cat.api import get_cat_image


class Cat(commands.Cog):

    """
    MAIN COMMAND
    """
    @bot.group(invoke_without_command=True,
        description = f"""Usage: {PREFIX}cat [gif]
    Display a random cat image or gif"""
    )

    async def cat(self, ctx):
        
        async with ctx.typing():
            cat = await get_cat_image()

        await ctx.send(file=cat)

    """ 
    SUB-COMMANDS
    """
    @cat.command(
        description = f"""Usage: {PREFIX}cat [gif]
    Display a random cat gif"""
    )
    async def gif(self, ctx):
        async with ctx.typing():
            cat = await get_cat_image(gif=True)

        await ctx.send(file=cat)

    @cat.command(
        description = "Prints help but in a Fancier way."
    )
    async def help(self, ctx):
        async with ctx.typing():
            usage_text = f"Usage: {PREFIX}cat [gif]"
            help_text = "Display a random cat image or gif"
            embed = discord.Embed(title=self.qualified_name, description=f"{usage_text}\n\n{help_text}")

        await ctx.send(embed=embed)
