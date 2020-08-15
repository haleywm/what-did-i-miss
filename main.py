# Initializing config may print error messages to the user if the config is invalid
# import modules.config as config
import sys, os
import discord
from discord.ext import commands
# This line only imports the modules defined in modules/__init__.py, which should only be cogs
from cogs import whatdidimiss, stop, cat

try:
    from config import TOKEN, ADMINS
except ImportError as e:
    print("""Import error.
Please make sure that you've created a config.py file in the same folder as main.py, using config_sample.py as an example.
Note that for other config values, you'll need to edit modules/config.py
""")
    # Raise the error anyway since this is a breaking error
    raise e

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
    # Testing if the old config format exists, and letting the user know to migrate if so
    if os.path.exists("config.yml"):
        print("""Note: you have a config.yml file, however this is no longer supported.
Please migrate your settings by editing modules/config.py
        """)
    # Add lines here to register additional "cogs", which are modular code sections that add commands
    bot.add_cog(whatdidimiss.whatdidimiss(bot))
    bot.add_cog(stop.stop(bot))
    bot.add_cog(command.Cat())

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Login error, please set a valid key")
        sys.exit(1)
