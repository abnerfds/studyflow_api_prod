import time

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

# --- WORKAROUND PARA O WSL2 (RACE CONDITION DA DOCKER API) ---
original_get_exposed_port = DockerContainer.get_exposed_port


def robust_get_exposed_port(self, port):
    for _ in range(10):
        try:
            return original_get_exposed_port(self, port)
        except ConnectionError:
            time.sleep(0.2)
    return original_get_exposed_port(self, port)


DockerContainer.get_exposed_port = robust_get_exposed_port
# -------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Sobe o Postgres no Testcontainers e cria as tabelas uma única vez na sessão."""
    with PostgresContainer("postgres:16", driver="asyncpg") as postgres:
        url = postgres.get_connection_url()
        engine = create_async_engine(url, echo=False)

        import database

        # 👇 ADICIONE ISTO: Força a importação dos modelos antes de criar as tabelas
        # Ajuste o import abaixo se os seus modelos estiverem em outro arquivo/pasta
        # ex: import models.candidates, models.disciplines
        # Se todos estiverem na "main" ou no "database", garanta que eles estão mapeados.
        from main import create_app

        create_app()  # Iniciar o app geralmente engatilha os imports dos modelos pelas rotas

        async with engine.begin() as conn:
            # Drop_all preventivo caso haja algum cache persistente
            await conn.run_sync(database.Base.metadata.drop_all)
            # Agora sim ele cria!
            await conn.run_sync(database.Base.metadata.create_all)

        yield engine
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def app(db_engine):
    """Configura o app com o banco de teste."""
    import database
    from main import create_app

    test_app = create_app()
    TestSessionLocal = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    test_app.dependency_overrides[database.get_db] = override_get_db
    yield test_app
    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def client(app):
    """Cria o cliente HTTP de teste."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def clean_database(db_engine):
    """Roda automaticamente antes de CADA teste para limpar as tabelas, garantindo isolamento."""
    import database

    async with db_engine.begin() as conn:
        for table in reversed(database.Base.metadata.sorted_tables):
            await conn.execute(
                text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE')
            )
