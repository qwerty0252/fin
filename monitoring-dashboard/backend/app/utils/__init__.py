"""Database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings
from app.models import Base

settings = get_settings()


async def init_db():
    """Initialize database"""
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def get_engine():
    """Get database engine"""
    return create_async_engine(settings.database_url, echo=False)


def get_session_factory():
    """Get async session factory"""
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    """Dependency for getting database session"""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.close()
