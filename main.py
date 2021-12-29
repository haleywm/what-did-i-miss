# Initializing config may print error messages to the user if the config is invalid
# import modules.config as config
import sys, os
import discord
from services.config import CONFIG
from services import database
import asyncio

# Registering intents
intents = discord.Intents.none()
intents.members = True
intents.guilds = True

bot = discord.Bot(intents=intents)

#import after to prevent circular imports
from cogs import images, misc, whatdidimiss

def main():
    # Add lines here to register additional "cogs", which are modular code sections that add commands
    bot.add_cog(whatdidimiss.Whatdidimiss())
    bot.add_cog(images.Dog())
    bot.add_cog(images.Cat())
    bot.add_cog(images.Gator())
    bot.add_cog(misc.Hug())

    try:
        bot.run(CONFIG["key"])
    except discord.LoginFailure:
        print("Login error, please set a valid key")
        sys.exit(1)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await database.setup_database()
    #await bot.change_presence(activity=discord.Activity(name=".help", type=discord.ActivityType.listening))
    await database.add_new_users(bot)

if __name__ == "__main__":
   main()
