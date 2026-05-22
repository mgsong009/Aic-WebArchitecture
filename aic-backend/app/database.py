from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# NOTE:
# Some local Windows/MySQL client combos raise a TypeError in aiomysql ping()
# when SQLAlchemy's pre-ping is enabled. Disabling pre-ping avoids that path.
engine = create_async_engine(settings.DB_URL, pool_pre_ping=False, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
