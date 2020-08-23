# admin tools for server configuration
import discord.ext.commands as commands
import discord
from typing import Union
from services.checks import server_admin_check, check_handler_shoveoff
from services.database.database import set_server, get_server


class Admin(commands.Cog, name="Administration"):
    r"Defines several useful administration tools"
    
    @commands.command(
        name = "setbotchannel",
        description = "Sets a bot channel where other commands can be set to be per-bot only."
    )
    @commands.guild_only()
    @server_admin_check()
    async def setbotchannel(self, ctx, channel: Union[commands.TextChannelConverter, str]):
        try:
            if isinstance(channel, discord.TextChannel):
                await ctx.send(f"Setting bot channel to #{channel}")
                set_server(ctx.guild.id, dict(bot_channel = channel))
            else:
                if channel.lower() == "none":
                    await ctx.send("Clearing bot channel")
                    set_server(ctx.guild.id, dict(bot_channel = None))
                else:
                    await ctx.send("Invalid channel")
        except Exception as e:
            await ctx.send("An error occured, that's not good :(")
            raise e

    
    cog_command_error = check_handler_shoveoff
    