from sqlalchemy import Column, Integer, String
from services.database.base import Base

class Server(Base):
    __tablename__ = 'servers'

    # The server ID
    id = Column(Integer, primary_key=True)
    # The ID of the channel that is used for bot commands
    bot_channel = Column(Integer)
    # The list of commands that are 'bot channel only'. If empty, all commands are allowed.
    bot_channel_commands = Column(String)

    def __repr__(self):
        return f"<Server(id={self.id},bot_channel={self.bot_channel},bot_channel_commands='{self.bot_channel_commands}')>"
