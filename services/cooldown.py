# cooldown.py
# Establishes a cooldown system that can be used by different commands

import datetime
import services.utils as utils

def get_cooldown_id(ctx):
    "Converts a context into the cooldown ID that would be used in that particular context."
    return str(ctx.message.author.id)


def cooldown_in_effect(ctx):
    "Returns a boolean True or False to say if a cooldown is in effect for the current context"
    cooldown_id = get_cooldown_id(ctx)
    return cooldown_id in cooldown_list and cooldown_list[cooldown_id] > datetime.datetime.utcnow()


def add_cooldown(ctx, down_time):
    "Adds a cooldown for the given amount of time (in the bots text time format) for the current context."
    cooldown_id = get_cooldown_id(ctx)
    cooldown_list[cooldown_id] = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=utils.parse_time_to_seconds(down_time)
    )

def remove_cooldown(ctx):
    "Removes a cooldown for the current context if one exists. Will not return an error if none exists."
    cooldown_id = get_cooldown_id(ctx)
    if cooldown_id in cooldown_list:
        cooldown_list.pop(cooldown_id)


cooldown_list = dict()