import aiohttp, discord
from random import randrange
from json import JSONDecodeError
from services.utils import UserError

CLIENT_ID = "141216319b9f06c"

async def get_image_from_album(album_hash, image_id=-1):
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

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=dict(Authorization=f"Client-ID {CLIENT_ID}")) as response:
            try:
                album = await response.json()
                if image_id < 0:
                    image_id = randrange(album["data"]["images_count"])
                image = album["data"]["images"][image_id]
                return image["link"]
            except JSONDecodeError:
                print("JSON Error")
                raise UserError("Bad Response from Imgur")
            except (KeyError, IndexError):
                raise UserError("Invalid Response format from Imgur")
            