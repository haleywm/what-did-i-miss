from sqlalchemy import Column, Integer, String
from services.database.base import Base

class Server_Options(Base):
    __tablename__ = 'server_options'

    id = Column(Integer, primary_key=True)
    # The server ID
    server_id = Column(Integer, index=True)
    # The ID of the channel that is used for bot commands
    setting_key = Column(String)
    # The list of commands that are 'bot channel only'. If true, that command is bot channel only
    setting_value = Column(String)

    def __repr__(self):
        return f"<Server({self.server_id=}, {self.setting_key=}, {self.setting_value=})>"
