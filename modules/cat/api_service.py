import io
import aiohttp
import mimetypes


async def get_cat_image(gif=False):
    base_url = "https://cataas.com/cat"
    url = base_url if not gif else base_url + "/gif"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file_response = await response.read()
            name = f"cat" + mimetypes.guess_extension(response.content_type, strict=True)

            return discord.File(filename=name, fp=io.BytesIO(file_response))