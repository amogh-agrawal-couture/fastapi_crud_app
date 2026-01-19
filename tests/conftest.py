import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import fakeredis

from app.main import app
from app.db import get_db
from app.cache import get_redis
from app.models.base import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(TEST_DATABASE_URL, future=True)

AsyncSessionLocalTest = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def override_get_db():
    async with AsyncSessionLocalTest() as session:
        yield session

async def override_get_redis():
    return fakeredis.FakeAsyncRedis(decode_responses=True)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    asyncio.run(_prepare_db())
    yield
    asyncio.run(_drop_db())


async def _prepare_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _drop_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def clear_tables():
    async def _clear():
        async with engine_test.begin() as conn:
            await conn.execute(text("DELETE FROM items"))

    asyncio.run(_clear())
    yield


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
