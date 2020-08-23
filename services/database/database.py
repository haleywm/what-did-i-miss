from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.database.base import Base
from services.database.tables.disabled_commands import Disabled_Commands

# Connecting to the database
engine = create_engine("sqlite:///server_variables.db")
# The server module registered itself with base when imported, creating missing db structures:
# TODO: Support for migration using sqlalchemy alembic. Not neccessary until I want to modify table structure in an update
Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

def get_server(server_id):
    "Lookup a server with the given ID and return it. Returns None if server doesn't exist."
    session = Session()
    server = session.query(Disabled_Commands).filter(Disabled_Commands.server_id == server_id).first()
    session.close()
    return server

def set_server(server_id, newvals):
    """set_server
    Updates the given server with the new values listed, and creates a new database entry if needed.
    Returns the new server value so that it can be used if needed.
    PARAMETERS
    ----------
    server_id (int)
        The id of the server being set.
    newvals (dict)
        The new values that should be set, in key: value format.
        Values that aren't part of the Disabled_Commands class are discarded.
    """
    # Create a new session, check if an item already exists, and either update the server or create a new entry
    session = Session()
    server = session.query(Disabled_Commands).filter(Disabled_Commands.server_id == server_id).first()
    # server is None is doesn't exist
    if not server:
        server = Disabled_Commands(server_id = server_id)
        session.add(server)
    
    for key, value in newvals.items():
        setattr(server, key, value)
    
    # Commiting the session saves the changes. As has already been added to session, it has been keeping track of changes for us.
    session.commit()
    return server