from config import ADMINS
import discord.ext.commands.errors as errors

# All check utils

def admin_check(ctx):
    return ctx.message.author.id in ADMINS

async def check_handler_shoveoff(self, ctx, error):
    if type(error) is errors.CheckFailure:
        await ctx.send("You can't tell me what to do.")
    else:
        print(error)