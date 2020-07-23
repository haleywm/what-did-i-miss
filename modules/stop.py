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
        description = "Shuts down the bot",
        hidden = True,
        enabled = config.get_config()["commands"]["stop"]["enabled"]
    )
    async def stop_program(self, ctx):
        r"""Discord Command for admins stopping the bot.
        Will only function if the user ID of the user making the command
        is listed in config.get_config()["admins"]
        Parameters
        ----------
        ctx : discord.ext.commands.Context
            Provided by Discord.py, is the context within which the command was given.
        """
        if ctx.message.author.id in config.get_config()["admins"]:
            await ctx.bot.logout()
        else:
            await ctx.send("You can't tell me what to do")