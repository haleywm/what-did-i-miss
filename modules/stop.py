import discord.ext.commands as commands
from . import config

class stop(commands.Cog, name="Stop"):
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
        if ctx.message.author.id in config.get_config()["admins"]:
            await ctx.bot.logout()
        else:
            await ctx.send("You can't tell me what to do")