# admin tools for server configuration
from main import bot
import discord.ext.commands as commands
import discord
from typing import Union
from services.checks import server_admin_check, check_handler_shoveoff
from services.database.database import set_setting, get_setting, delete_setting


class Admin(commands.Cog, name="Administration"):
    r"Defines several useful administration tools"
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = "setbotchannel",
        description = "Sets a bot channel where other commands can be set to be per-bot only.",
        usage = """<channelname>
    Replace channel name with 'none' to disable the bot channel. Please don't make a channel named #none.
        """
    )
    @commands.guild_only()
    @commands.check(server_admin_check)
    async def setbotchannel(self, ctx, channel: Union[commands.TextChannelConverter, str]):
        try:
            if isinstance(channel, discord.TextChannel):
                await ctx.send(f"Setting bot channel to #{channel.name}")
                set_setting(ctx.guild.id, dict(bot_channel = channel.name))
            else:
                if channel.lower() == "none":
                    await ctx.send("Clearing bot channel")
                    delete_setting(ctx.guild.id, "bot_channel")
                else:
                    await ctx.send("Invalid channel")
        except Exception as e:
            await ctx.send("An error occured, that's not good :(")
            raise e

    @commands.command(
        name = "listcommands",
        description = "Lists the proper name of all commands, alongside their enabled status, and the current bot channel."
    )
    @commands.check(server_admin_check)
    async def listcommands(self, ctx):
        ret = ""
        channel = get_setting(ctx.guild.id, "bot_channel")
        if channel:
            ret += f"Bot channel: #{channel}\n"
        ret += "All commands: (Bot channel only)```\n"
        for command in self.bot.commands:
            allowed = True if get_setting(ctx.guild.id, f"bc_only_{command}") == '0' else False
            ret += f"{command}: {allowed}\n"
        ret += "```"
        await ctx.send(ret)
    
    @commands.command(
        name = "setcommand",
        description = "Set a command to be used in the bot channel only"
    )
    @commands.check(server_admin_check)
    @commands.guild_only()
    async def setcommand(self, ctx, command, enable: bool):
        command = command.lower()
        if command in map(str, self.bot.commands):
            set_setting(ctx.guild.id, {("bc_only_" + command): enable})
            await ctx.send(f"{'Enabled' if enable else 'Disabled'} command '.{command}' in non-bot channels.")
        else:
            await ctx.send("That isn't a recognized command, please run .listcommands for a list of bot commands")
    
    cog_command_error = check_handler_shoveoff