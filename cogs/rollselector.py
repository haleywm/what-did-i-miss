import discord
from discord.ext import commands

class RoleSelector(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, pos: int):
        super().__init__(label=role.name, style=discord.enums.ButtonStyle.primary, custom_id=str(role.id))
        self.role_id = role.id
        self.position = pos
