from sqlalchemy import Column, Integer, Boolean
from services.database.base import Base

class Disabled_Commands(Base):
    __tablename__ = 'disabled_commands'

    # The server ID
    server_id = Column(Integer, primary_key=True, autoincrement=False)
    # The ID of the channel that is used for bot commands
    bot_channel = Column(Integer)
    # The list of commands that are 'bot channel only'. If true, that command is bot channel only
    whatdidimiss = Column(Boolean)
    stop = Column(Boolean)
    admin = Column(Boolean)

    command_list = ["whatdidimiss", "stop", "admin"]

    def __repr__(self):
        return f"<Server(id={self.server_id},bot_channel={self.bot_channel})>"
