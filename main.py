# Initializing config may print error messages to the user if the config is invalid
# import modules.config as config
import sys, os
import discord
from services.config import CONFIG
from discord.ext import commands
# This line only imports the modules defined in modules/__init__.py, which should only be cogs
from cogs import whatdidimiss, stop, misc


bot = commands.Bot(
    command_prefix=".",
    case_insensitive=True
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))

if __name__ == "__main__":
    # Add lines here to register additional "cogs", which are modular code sections that add commands
    bot.add_cog(whatdidimiss.Whatdidimiss(bot))
    bot.add_cog(stop.Stop(bot))
    bot.add_cog(misc.Wholesome())

    try:
        bot.run(CONFIG["key"])
    except discord.LoginFailure:
        print("Login error, please set a valid key")
        sys.exit(1)
