import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, DateTime, select, delete, and_
import datetime
import asyncio
from services.config import CONFIG

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
    server_id = Column("server_id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, primary_key=True)
    first_seen = Column("first_seen", DateTime, nullable=False)

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
                results = await session.execute(lookup)

                for user in results:
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
            session.execute(to_del)
