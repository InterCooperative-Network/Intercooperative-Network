from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


# Base declarative class used by all ORM models
Base = declarative_base()


def get_database_url() -> str:
    """Return DATABASE_URL or a sensible default for local dev."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://icn:icn_dev@localhost:5432/icn_node",
    )


# Async SQLAlchemy engine and session factory
engine = create_async_engine(get_database_url(), echo=False, future=True)
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with AsyncSessionFactory() as session:
        yield session


