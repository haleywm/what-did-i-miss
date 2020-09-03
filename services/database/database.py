from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.database.base import Base
from services.database.tables.serveroptions import Server_Options

# Connecting to the database
engine = create_engine("sqlite:///server_variables.db")
# The server module registered itself with base when imported, creating missing db structures:
# TODO: Support for migration using sqlalchemy alembic. Not neccessary until I want to modify table structure in an update
Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

def get_setting(server_id, setting_key):
    "Lookup a server with the given ID and return it. Returns None if server or setting doesn't exist."
    session = Session()
    value = None
    result = session.query(Server_Options).filter(Server_Options.server_id == server_id).\
        filter(Server_Options.setting_key == setting_key).first()
    if result:
        value = result.setting_value
    session.close()
    return value

def set_setting(server_id, setting_values):
    """set_server
    Updates the given server with the new values listed, and creates a new database entry if needed.
    Returns the new server value so that it can be used if needed.
    PARAMETERS
    ----------
    server_id (int)
        The id of the server being set.
    setting_values (dict)
        The new values that should be set, in key: value format.
    """
    # Create a new session, and then for each value check if it already exists, and set it if it doesn't
    session = Session()
    server = session.query(Server_Options).filter(Server_Options.server_id == server_id)

    for key, value in setting_values.items():
        current_value = server.filter(Server_Options.setting_key == key).first()
        if current_value:
            current_value.setting_value = value
        else:
            session.add(
                Server_Options(server_id=server_id, setting_key=key, setting_value=value)
            )
    
    # Commiting the session saves the changes. As has already been added to session, it has been keeping track of changes for us.
    session.commit()