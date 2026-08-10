import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://cansahin:cansahin1@localhost/testdb"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"


import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app

pytest_plugins =["anyio"]

#import app
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

#test engine
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine

## Setup Database
@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

## DB Session (Transactional Rollback)
@pytest.fixture
async def db_session( test_engine, setup_database,) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(bind=conn,class_=AsyncSession,
                                            expire_on_commit=False,
                                            join_transaction_mode="create_savepoint",)

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()



## Client Fixture
@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():#db dependency
        yield db_session

    app.dependency_overrides[get_db] = override_get_db #get_db --> override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear() #clear the overrides dependency

#Create a user
async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpass123",) -> dict:

    #create a user
    response = await client.post("/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    #check with assert if it is correct return ==201
    assert response.status_code == 201
    return response.json()

#Check the login
async def login_user(client: AsyncClient,email: str = "test@example.com",password: str = "testpass123",) -> str:
    #check user_token
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    # check with assert if it is correct return ==200
    assert response.status_code == 200
    return response.json()["access_token"]

#Create a token type
def auth_header(token: str) -> dict[str, str]:

    return {"Authorization": f"Bearer {token}"}


