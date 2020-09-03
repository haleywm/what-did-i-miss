# Initializing config may print error messages to the user if the config is invalid
# import modules.config as config
import sys, os
import discord
from services.config import CONFIG
from services.checks import server_allowed_check, global_command_handler
from discord.ext import commands

bot = commands.Bot(
    command_prefix=".",
    case_insensitive=True
)
#import after to prevent circular imports
from cogs import whatdidimiss, stop, misc, images

bot.on_command_error = global_command_handler

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))

if __name__ == "__main__":
    # Add lines here to register additional "cogs", which are modular code sections that add commands
    bot.add_cog(whatdidimiss.Whatdidimiss(bot))
    bot.add_cog(stop.Stop(bot))
    bot.add_cog(images.Cat())
    bot.add_cog(images.Dog())
    bot.add_cog(images.Gator())
    bot.add_cog(misc.Hug())
    bot.add_check(server_allowed_check)

    try:
        bot.run(CONFIG["key"])
    except discord.LoginFailure:
        print("Login error, please set a valid key")
        sys.exit(1)

