import discord

from discord.ext import commands
from discord.commands import SlashCommandGroup
from services.api.all import *
from services.config import CONFIG

async def imgur_send(ctx, album_hash):
    await ctx.defer()
    download = not CONFIG["commands"]["images"]["link"]
    async with ctx.typing():
        gator = await get_image_from_album(album_hash, download)
        await send(ctx, gator, download)

async def send(ctx, f, download):
    if(download):
        await ctx.respond(file=f)
    else:
        await ctx.respond(f)

class Dog(commands.Cog):
    dog = SlashCommandGroup("dog", "Dog pictures and gifs")
    
    @dog.command()
    async def picture(self, ctx, gif=False):
        await ctx.defer()
        download = not CONFIG["commands"]["images"]["link"]
        async with ctx.typing():
            dog = await get_dog_image(gif, download)
            await send(ctx, dog, download)

    @dog.command()
    async def gif(self, ctx):
        await self.picture(self, ctx, True)

class Cat(commands.Cog):
    cat = SlashCommandGroup("cat", "Cat pictures and gifs")

    @cat.command()
    async def picture(self, ctx, gif=False):
        await ctx.defer()
        async with ctx.typing():
            cat = await get_cat_image(gif)
            await send(ctx, cat, True)

    @cat.command()
    async def gif(self, ctx):
        await self.picture(self, ctx, True)

class Gator(commands.Cog):
    gator = SlashCommandGroup("gator", "Gator pictures and gifs")

    @gator.command()
    async def picture(self, ctx):
        "Post a gator pick, from an album provided by Gator#3220"
        await imgur_send(ctx, "cwnBW9Q")

    @gator.command()
    async def gif(self, ctx):
        await imgur_send(ctx, "lSQtPms")
