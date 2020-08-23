import discord.ext.commands as commands
from services.checks import bot_admin_check, check_handler_shoveoff

class Stop(commands.Cog, name="Stop"):
    r"""Class for stopping the bot defined by Discord.py
    Does not take input apart from what is defined by the spec for adding cogs.
    """

    @commands.command(
        name = "stop",
        description = "Shuts down the bot if the user ID has been configured as a bot admin.",
        hidden = True,
        enabled = True
    )
    @bot_admin_check()
    async def stop_program(self, ctx):
        print("Closing due to admin command...")
        await ctx.send("Ok bye!!")
        await ctx.bot.logout()
    
    cog_command_error = check_handler_shoveoff
    
