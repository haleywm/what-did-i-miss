import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, BigInteger, DateTime, select, delete, update, and_, UniqueConstraint, func
from operator import itemgetter
import datetime
import asyncio
from services.config import CONFIG
from typing import Optional

now = datetime.datetime.now

Base = sqlalchemy.orm.declarative_base()
Engine = None
Async_Session = None
Setup = asyncio.Event()

# A discord user class
# This contains the state of a user in a given server.
# Primary key is the server ID, and the user ID
# Stores the date that the user first joined the server
# Doesn't remove entries on user leaving server

class Membership(Base):
    __tablename__ = "membership"
    server_id = Column("server_id", BigInteger, primary_key=True)
    user_id = Column("user_id", BigInteger, primary_key=True)
    first_seen = Column("first_seen", DateTime, nullable=False)

class ServerRoles(Base):
    __tablename__ = "serverroles"
    __table_args__ = (
        UniqueConstraint("position")
    )
    server_id = Column("server_id", BigInteger, primary_key=True)
    role_id = Column("role_id", BigInteger, primary_key=True)
    position = Column("position", Integer, nullable=False)

async def setup_database():
    # Disable echo for production
    #engine = create_async_engine("sqlite+aiosqlite:///db.sqlite", future=True, echo=True)
    engine = create_async_engine("sqlite+aiosqlite:///db.sqlite", future=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Apologies for the global but it's the best encapsulation method
    global Async_Session
    Async_Session = sqlalchemy.orm.sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    global Engine
    Engine = engine
    Setup.set()

async def get_database():
    await Setup.wait()
    return Async_Session()

async def close_database():
    await Engine.dispose()

async def add_new_users(bot):
    # Running process on every guild
    async with await get_database() as session:
        for guild in bot.guilds:
            await process_server(guild, session)

async def process_user(guild, member, joined_at, cur):
    role = guild.get_role(CONFIG["newuserroles"]["role_id"])
    if role:
        if cur.tzinfo is None:
            cur = cur.replace(tzinfo=datetime.timezone.utc)
        if joined_at.tzinfo is None:
            joined_at = joined_at.replace(tzinfo=datetime.timezone.utc)
        time_joined = cur - joined_at
        if time_joined.days >= CONFIG["newuserroles"]["days"]:
            # User not new
            await member.remove_roles(role)
        else:
            # User new
            await member.add_roles(role)

async def slow_refresh(bot):
    # Waits an hour, and then checks if any users are old enough to no longer be new
    while True:
        await asyncio.sleep(60 * 60)
        # Check for users who would have aged in the last 2 hours, to ensure nothing slips by
        async with await get_database() as session:
            async with session.begin():
                now = datetime.datetime.utcnow()
                newest = now - datetime.timedelta(days=CONFIG["newuserroles"]["days"])
                oldest = now - datetime.timedelta(days=CONFIG["newuserroles"]["days"], hours=2)
                
                lookup = select(Membership).where(and_(
                    Membership.first_seen > newest,
                    Membership.first_seen < oldest
                ))
                results = await session.stream(lookup)

                async for user in results:
                    guild = bot.get_guild(user.server_id)
                    role = guild.get_role(CONFIG["newuserroles"]["role_id"])
                    if role:
                        member = guild.get_member(user.user_id)
                        await member.remove_role(role)

async def process_server(guild, session):
    # Process every user in the guild
    async with session.begin():
        for member in guild.members:
            lookup = select(Membership).where(and_(Membership.server_id == guild.id, Membership.user_id == member.id))
            result = (await session.execute(lookup)).first()
            if result:
                # Result already exists
                # Check the date, and remove users if enough time has passed
                await process_user(guild, member, result[0].first_seen, now(datetime.timezone.utc))
            else:
                # Haven't seen them before
                # Add them to the database, and give them the role if they're new
                new_user = Membership(server_id=guild.id, user_id=member.id, first_seen=member.joined_at)
                session.add(new_user)
                await process_user(guild, member, member.joined_at, now(datetime.timezone.utc))

async def remove_server(guild):
    # If the bot itself is removed from a server delete all records
    async with await get_database() as session:
        async with session.begin():
            to_del = delete(Membership).where(Membership.server_id == guild.id)
            await session.execute(to_del)

async def get_all_server_roles():
    # Return a map that maps server ID's to lists of sorted role id's for each server
    button_roles: dict[int, list[tuple[int, int]]] = dict()
    async with await get_database() as session:
        async with session.begin():
            lookup = select(ServerRoles)
            result = await session.stream(lookup)
            async for entry in result:
                server = entry.server_id
                role = entry.role_id
                pos = entry.position
                if server not in button_roles:
                    button_roles[server] = list()
                button_roles[server].append((role, pos))
    
    # Then sorting the data
    # Iterating through each list, and sorting its contents by the second value in each tuple
    for role_list in button_roles.values():
        role_list.sort(key=itemgetter(1))

    return button_roles

async def add_button(role_id: int, server_id: int, position: Optional[int] = None):
    async with await get_database() as session:
        async with session.begin():
            # If position isn't given, lookup the next highest position to use
            if position is None:
                # Lookup the highest position for this server and add 1
                lookup = select(func.max(ServerRoles.position).label("max_pos")).where(ServerRoles.server_id == server_id)
                result = (await session.execute(lookup)).first()
                # The max will be none/null if there aren't any roles for that server yet, so just use 0 in that case
                if result.max_pos is None:
                    position = 0
                else:
                    position = result.max_pos + 1
            new_role = ServerRoles(server_id = server_id, role_id = role_id, position = position)
            await session.add(new_role)

async def remove_button(role_id: int, server_id: int, position: Optional[int] = None):
    async with await get_database() as session:
        async with session.begin():
            # Lookup position if not known
            if position is None:
                lookup = select(ServerRoles.position).where(and_(ServerRoles.server_id == server_id, ServerRoles.role_id == role_id))
                result = (await session.execute(lookup)).first()
                if result is None:
                    # Button already gone
                    return
                position = result.position
            to_delete = delete(ServerRoles).where(and_(ServerRoles.server_id == server_id, ServerRoles.role_id == role_id))
            await session.execute(to_delete)
            to_update = update(ServerRoles).\
                where(and_(ServerRoles.server_id == server_id, ServerRoles.position > position)).\
                values(position=(ServerRoles.position - 1))
            await session.execute(to_update)

