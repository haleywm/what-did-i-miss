# cooldown.py
# Establishes a cooldown system that can be used by different commands

import datetime
import services.utils as utils

def get_cooldown_id(ctx):
    "Converts a context into the cooldown ID that would be used in that particular context."
    return str(ctx.author.id)


def cooldown_in_effect(ctx):
    "Returns the tuple: (User on Cooldown boolean, Seconds remaining)"
    cooldown_id = get_cooldown_id(ctx)
    on_cooldown = cooldown_id in cooldown_list and cooldown_list[cooldown_id] > datetime.datetime.utcnow()
    
    remaining = 0
    if on_cooldown:
        remaining = int((cooldown_list[cooldown_id] - datetime.datetime.utcnow()).total_seconds())
    
    return on_cooldown, remaining


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