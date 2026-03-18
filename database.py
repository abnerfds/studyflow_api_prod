from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None
_database_url: str | None = None


# Classe mãe que nossos models vão herdar para serem reconhecidos como tabelas.
# DeclarativeBase é a API do SQLAlchemy 2.0 com suporte completo a type checking.
class Base(DeclarativeBase):
    pass


def setup_database(
    database_url: str,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    global engine, AsyncSessionLocal, _database_url

    if (
        engine is not None
        and AsyncSessionLocal is not None
        and _database_url == database_url
    ):
        return engine, AsyncSessionLocal

    engine = create_async_engine(database_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    _database_url = database_url
    return engine, AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        msg = "Database has not been initialized. Call setup_database() first."
        raise RuntimeError(msg)

    async with AsyncSessionLocal() as session:
        yield session
