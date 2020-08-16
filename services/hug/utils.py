import discord
import re
from services.utils import check_perms


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
    match = re.search(r'\d+', user)

    if not match:
        raise InvalidMentionException()

    member = guild.get_member((int(match[0])))

    return member


class InvalidMentionException(Exception):
    pass
