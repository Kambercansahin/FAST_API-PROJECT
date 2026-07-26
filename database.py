from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker

SQLAlchemy_DATABASE_URL ="sqlite:///./fast_api.db"

engine = create_engine(
    url=SQLAlchemy_DATABASE_URL,connect_args={"check_same_thread":False}
)

local_session =sessionmaker(autocommit=False,autoflush=False,bind=engine)


class Base(DeclarativeBase):
    pass

def get_db():
    with local_session() as db:
        yield db