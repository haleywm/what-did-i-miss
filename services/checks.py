from services.config import CONFIG
import discord.ext.commands.errors as errors
import discord.ext.commands as commands
from discord import Permissions
from services.database.database import get_setting
from services.utils import check_perms

def bot_admin_check(ctx):
    "Checks if the command caller is a bot admin."
    return ctx.message.author.id in CONFIG["admins"]

def server_admin_check(ctx):
    "Checks if the command caller is a server admin."
    # Defining a discord server admin as someone with administrator permissions for that server
    return check_perms(ctx, Permissions(
        administrator = True
    ), ctx.author)

def server_allowed_check(ctx):
    """Checks if the message is on a server.
    If so, that the message is either in the bot channel, or is allowed in the server config.
    Doesn't return a predicate so that it can be run bot wide."""
    allowed = True
    if ctx.guild:
        allowed = get_setting(ctx.guild.id, f"bot-{ctx.command.name}") != '0'
    return allowed

async def global_command_handler(ctx, error):
    # Ignores errors that can fail silently, like failed checks, and invalid arguments
    # Raises them otherwise
    if not isinstance(error, (commands.BadArgument, commands.CheckFailure)):
        raise error

# Check handler
# Set for a specific cog with: cog_command_error = check_handler_shoveoff
async def check_handler_shoveoff(self, ctx, error):
    if isinstance(error, errors.CheckFailure):
        await ctx.send("You can't tell me what to do.")
    elif isinstance(error, errors.BadArgument):
        await ctx.send("Invalid command arguments")
    else:
        # Can't help if it's another type of error :)
        raise error