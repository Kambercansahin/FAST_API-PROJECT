from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(settings.database_url)

local_session =async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)


class Base(DeclarativeBase):
    pass

async def get_db():
    async with local_session() as db:
        yield db