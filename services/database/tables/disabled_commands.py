from sqlalchemy import Column, Integer, String
from services.database.base import Base

class Disabled_Commands(Base):
    __tablename__ = 'disabled_commands'

    # The server ID
    server_id = Column(Integer, primary_key=True, autoincrement=False)
    # The ID of the channel that is used for bot commands
    bot_channel = Column(Integer)
    # The list of commands that are 'bot channel only'. If empty, all commands are allowed.
    bot_channel_commands = Column(String)

    def __repr__(self):
        return f"<Server(id={self.server_id},bot_channel={self.bot_channel},bot_channel_commands='{self.bot_channel_commands}')>"
