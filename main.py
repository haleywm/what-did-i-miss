# Initializing config may print error messages to the user if the config is invalid
import modules.config as config
import sys, discord, asyncio
from discord.ext.commands import Bot
# This line only imports the modules defined in modules/__init__.py, which should only be cogs
from modules import *

PREFIX = "."

bot = Bot(command_prefix=PREFIX)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))

# Add lines here to register additional "cogs", which are modular code sections that add commands
bot.add_cog(whatdidimiss.whatdidimiss(bot))
bot.add_cog(stop.stop(bot))

if config.get_config()["key"]:
    bot.run(config.get_config()["key"])
else:
    print("Please set a private token")
    sys.exit(0)
