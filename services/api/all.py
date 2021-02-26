import io
import aiohttp
import mimetypes
import discord
import re
from random import randrange
from json import JSONDecodeError
from services.utils import UserError

__all__ = ["get_dog_image", "get_cat_image", "get_image_from_album"]

async def get_image(name, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            f = await response.read()
            name += mimetypes.guess_extension(response.content_type, strict=True)
            return discord.File(filename=name, fp=io.BytesIO(f))

async def get_json(url, headers_={}):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers_) as response:
            try:
                return await response.json()
            except JSONDecodeError:
                raise UserError("Imgur gave a bad response :(")

async def get_dog_image(gif=False, download=True):
    url = "https://api.thedogapi.com/v1/images/search?mime_types="
    url += int(gif)*"gif" + int(not gif)*"jpg,png"
    try:
        url = (await get_json(url))[0]["url"]
        return (await get_image("dog", url)) if download else url
    except (KeyError, IndexError):
        raise UserError("Dog API gave a bad response :(")

async def get_cat_image(gif=False):
    url = "https://cataas.com/cat" + int(gif)*"/gif"
    return await get_image("cat", url)

CLIENT_ID = "141216319b9f06c"
async def get_image_from_album(album_hash, download=True, image_id=-1):
    """Gets an image from an imgur album. By default will get a random image in the album, but a value can be given.
    Returns a url pointing to the image.
    Arguments
    ---------
    album_hash : str
        The imgur album hash
    image_id : int (default=-1)
        The imgur image id. If negative, a random image will be taken.
    """
    url = f"https://api.imgur.com/3/album/{album_hash}"
    try:
        album = await get_json(url, {"Authorization": f"Client-ID {CLIENT_ID}"})
        image_id = image_id if image_id > -1 else randrange(album["data"]["images_count"])
        url = album["data"]["images"][image_id]["link"]
        return (await get_image("gator", url)) if download else url
    except (KeyError, IndexError):
        raise UserError("Got an Invalid Response")