# Initializing config may print error messages to the user if the config is invalid
# import modules.config as config
import sys
import discord
from discord.ext import commands
# This line only imports the modules defined in modules/__init__.py, which should only be cogs
from modules import whatdidimiss, stop
from config import TOKEN

PREFIX = "."

bot = commands.Bot(
    command_prefix=PREFIX,
    case_insensitive=True
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))

if __name__ == "__main__":
    # Add lines here to register additional "cogs", which are modular code sections that add commands
    bot.add_cog(whatdidimiss.whatdidimiss(bot))
    bot.add_cog(stop.stop(bot))

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Login error, please set a valid key")
        sys.exit(1)
