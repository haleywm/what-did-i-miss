import discord.ext.commands as commands
from . import config

class stop(commands.Cog, name="Stop"):
    r"""Class for stopping the bot defined by Discord.py
    Does not take input apart from what is defined by the spec for adding cogs.
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(
        name = "stop",
        description = "Shuts down the bot if the user ID has been configured as a bot admin.",
        hidden = True,
        enabled = config.get_config()["commands"]["stop"]["enabled"]
    )
    async def stop_program(self, ctx):
        if ctx.message.author.id in config.get_config()["admins"]:
            await ctx.bot.logout()
        else:
            await ctx.send("You can't tell me what to do")