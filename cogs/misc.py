import discord

from discord.ext import commands
from services.config import CONFIG
from services.hug.utils import remove_invocation, find_user, InvalidUserException

class Hug(commands.Cog):
    @commands.before_invoke(remove_invocation)
    @commands.command(
        enabled = CONFIG["commands"]["hug"]["enabled"],
        aliases = ["stab", "simp"]
    )
    async def hug(self, ctx, target):
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