from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.database.base import Base
from services.database.tables.server import Server

# Connecting to the database
engine = create_engine("sqlite:///:memory:")
# The server module registered itself with base when imported, creating missing db structures:
Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)


