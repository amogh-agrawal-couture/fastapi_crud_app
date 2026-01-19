from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not all([
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
]):
    raise RuntimeError("Missing required PostgreSQL environment variables")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
