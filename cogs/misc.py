import discord

from discord.ext import commands
from services.config import CONFIG

class Hug(commands.Cog):
    @commands.command(
        enabled = CONFIG["commands"]["hug"]["enabled"],
        aliases = ["stab", "simp"]
    )
    async def hug(self, ctx, target: discord.Member):
        await ctx.send(f"Psst {target.name}! {ctx.message.author.name} sent you a virtual hug! :heart:")