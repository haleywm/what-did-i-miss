import discord
import re
from services.utils import check_perms
from fuzzywuzzy import fuzz
from services.config import CONFIG


# TODO Implement logging if/when a log handler is added
async def remove_invocation(cog, ctx):
    if CONFIG["commands"]["hug"]["delete-message"] and check_perms(ctx, discord.Permissions(
        manage_messages = True
    )):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("Invalid permissions: Bot needs manage_messages to delete user messages.")
        except discord.NotFound:
            print("Message not found. Something went wrong during command invocation.")
        except discord.HTTPException as e:
            print(f"HTTP Exception: {e}")


async def find_user(guild, user):
    is_mention = re.search(r'<@!\d+>', user)

    if is_mention:
        user_id = await convert_mention_to_id(user)
        member = guild.get_member(user_id)
    else:
        if CONFIG["commands"]["hug"]["fuzzy-matching"]:
            member = await fuzzymatch_name(guild, user)
        else:
            member = None

    return member


async def convert_mention_to_id(user):
    match = re.search(r'\d+', user)

    if not match:
        raise InvalidUserException

    return int(match[0])


async def fuzzymatch_name(guild, user):
    """
        If the supplied user string is at least 60% similar to an existing guild user, consider that a match
    """
    best_match = (None, -1)  # Member object and fuzzy ratio
    for member in guild.members:
        if member.nick is not None:
            ratio = fuzz.partial_ratio(user.lower(), member.nick.lower())
        else:
            ratio = fuzz.partial_ratio(user.lower(), member.name.lower())

        if ratio > best_match[1]:
            best_match = (member, ratio)

    return best_match[0]


class InvalidUserException(Exception):
    pass
