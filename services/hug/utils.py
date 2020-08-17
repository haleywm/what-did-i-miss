import discord
import re
from services.utils import check_perms
from fuzzywuzzy import fuzz


# TODO Implement logging if/when a log handler is added
async def remove_invocation(cog, ctx):
    if check_perms(ctx, discord.Permissions(
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
        member = await fuzzymatch_name(guild, user)

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
    for member in guild.members:
        ratio_required = 60

        nick_match = member.nick is not None and fuzz.ratio(member.nick.lower(), user.lower()) > ratio_required
        name_match = fuzz.ratio(member.name.lower(), user.lower()) > ratio_required

        if nick_match or name_match:
            return member

    raise InvalidUserException


class InvalidUserException(Exception):
    pass
